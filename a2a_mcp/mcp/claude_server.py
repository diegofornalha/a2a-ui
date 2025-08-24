#!/usr/bin/env python3
"""
MCP Server usando Claude Code SDK ao invés de Google API.
Integra com Claude para embeddings e busca semântica de agentes.
"""

import json
import os
import sqlite3
import traceback
import uuid
import sys
import platform
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
import requests

# Importar Claude Code SDK
from claude_code_sdk import (
    ClaudeSDKClient,
    ClaudeCodeOptions,
    query,
    AssistantMessage,
    ResultMessage,
    TextBlock
)

# Importar AI SDK Provider para funcionalidades adicionais
try:
    from ai_sdk_provider_claude_code import (
        ClaudeCodeProvider,
        ClaudeCodeLanguageModel,
        ClaudeCodeSettings
    )
except ImportError:
    print("Aviso: ai_sdk_provider_claude_code não disponível")
    ClaudeCodeProvider = None

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger


logger = get_logger(__name__)
AGENT_CARDS_DIR = 'agent_cards'
SQLLITE_DB = 'travel_agency.db'
PLACES_API_URL = 'https://places.googleapis.com/v1/places:searchText'


class ClaudeEmbeddingService:
    """Serviço para gerar embeddings usando Claude Code SDK."""
    
    def __init__(self):
        """Inicializa o serviço de embeddings com Claude."""
        self.client = None
        self.embeddings_cache = {}
        
    async def initialize(self):
        """Inicializa o cliente Claude SDK."""
        try:
            self.client = ClaudeSDKClient(
                options=ClaudeCodeOptions(
                    claude_cli_path="claude",
                    log_level="info"
                )
            )
            logger.info("Claude SDK Client inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Claude SDK: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embeddings para o texto usando Claude.
        
        Como o Claude não fornece embeddings nativos, vamos usar uma estratégia alternativa:
        1. Pedir ao Claude para analisar e extrair características do texto
        2. Converter essas características em um vetor numérico
        """
        # Verificar cache
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        try:
            # Prompt para Claude analisar o texto e gerar características
            prompt = f"""
            Analise o seguinte texto e extraia 10 características numéricas principais (0-1):
            1. Complexidade técnica (0=simples, 1=complexo)
            2. Orientação a dados (0=não, 1=muito)
            3. Interatividade (0=passivo, 1=interativo)
            4. Automação (0=manual, 1=automático)
            5. Processamento de linguagem (0=não, 1=intensivo)
            6. Visualização (0=texto, 1=visual)
            7. Tempo real (0=batch, 1=real-time)
            8. Colaboração (0=individual, 1=colaborativo)
            9. Segurança (0=aberto, 1=seguro)
            10. Escalabilidade (0=pequeno, 1=grande escala)
            
            Texto: "{text[:500]}"
            
            Responda APENAS com 10 números decimais separados por vírgula.
            Exemplo: 0.8,0.5,0.3,0.9,0.2,0.7,0.4,0.6,0.1,0.5
            """
            
            # Consultar Claude
            result = await query(prompt)
            
            if isinstance(result, ResultMessage):
                response = result.content.strip()
            else:
                response = str(result).strip()
            
            # Extrair números da resposta
            try:
                numbers = [float(x.strip()) for x in response.split(',')[:10]]
                # Garantir que temos 10 dimensões
                while len(numbers) < 10:
                    numbers.append(0.5)  # Valor padrão neutro
                embedding = numbers[:10]
            except:
                # Fallback: embedding aleatório baseado no hash do texto
                import hashlib
                hash_obj = hashlib.md5(text.encode())
                hash_bytes = hash_obj.digest()
                # Converter bytes para floats entre 0 e 1
                embedding = [b / 255.0 for b in hash_bytes[:10]]
            
            # Cachear resultado
            self.embeddings_cache[text] = embedding
            return embedding
            
        except Exception as e:
            logger.error(f"Erro ao gerar embedding com Claude: {e}")
            # Fallback: embedding baseado em hash
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            return [b / 255.0 for b in hash_bytes[:10]]
    
    async def close(self):
        """Fecha o cliente Claude SDK."""
        if self.client:
            try:
                await self.client.disconnect()
            except:
                pass


# Instância global do serviço de embeddings
embedding_service = ClaudeEmbeddingService()


def load_agent_cards():
    """Carrega agent cards dos arquivos JSON."""
    card_uris = []
    agent_cards = []
    dir_path = Path(AGENT_CARDS_DIR)
    
    if not dir_path.is_dir():
        logger.error(f'Diretório de agent cards não encontrado: {AGENT_CARDS_DIR}')
        return card_uris, agent_cards
    
    logger.info(f'Carregando agent cards de: {AGENT_CARDS_DIR}')
    
    for filename in os.listdir(AGENT_CARDS_DIR):
        if filename.lower().endswith('.json'):
            file_path = dir_path / filename
            
            if file_path.is_file():
                logger.info(f'Lendo arquivo: {filename}')
                try:
                    with file_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        card_uris.append(f'resource://agent_cards/{Path(filename).stem}')
                        agent_cards.append(data)
                except Exception as e:
                    logger.error(f'Erro ao processar {filename}: {e}')
    
    logger.info(f'Carregados {len(agent_cards)} agent cards')
    return card_uris, agent_cards


async def build_agent_card_embeddings() -> Optional[pd.DataFrame]:
    """
    Carrega agent cards e gera embeddings usando Claude.
    """
    card_uris, agent_cards = load_agent_cards()
    
    if not agent_cards:
        logger.warning("Nenhum agent card encontrado")
        return None
    
    logger.info('Gerando embeddings para agent cards com Claude')
    
    try:
        # Inicializar serviço de embeddings
        await embedding_service.initialize()
        
        # Criar DataFrame
        df = pd.DataFrame({
            'card_uri': card_uris,
            'agent_card': agent_cards
        })
        
        # Gerar embeddings para cada card
        embeddings = []
        for card in agent_cards:
            card_text = json.dumps(card)
            embedding = await embedding_service.generate_embedding(card_text)
            embeddings.append(embedding)
        
        df['card_embeddings'] = embeddings
        
        logger.info('Embeddings gerados com sucesso')
        return df
        
    except Exception as e:
        logger.error(f'Erro ao gerar embeddings: {e}', exc_info=True)
        return None


def serve(host, port, transport):
    """
    Inicializa e executa o servidor MCP com Claude Code SDK.
    
    Args:
        host: Hostname ou IP para bind
        port: Porta para bind
        transport: Mecanismo de transporte ('stdio', 'sse', etc)
    """
    logger.info('Iniciando Agent Cards MCP Server com Claude SDK')
    
    # Verificar se Claude está disponível
    try:
        import subprocess
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        logger.info(f"Claude Code versão: {result.stdout.strip()}")
    except:
        logger.warning("Claude Code CLI não encontrado. Certifique-se de que está instalado.")
    
    mcp = FastMCP('agent-cards-claude', host=host, port=port)
    
    # DataFrame global para armazenar embeddings
    df = None
    
    @mcp.tool(
        name='find_agent',
        description='Encontra o agent card mais relevante usando Claude para análise semântica.'
    )
    async def find_agent(query: str) -> str:
        """Encontra o agent card mais relevante baseado em uma consulta."""
        nonlocal df
        
        # Carregar embeddings se ainda não carregados
        if df is None:
            df = await build_agent_card_embeddings()
            if df is None:
                return json.dumps({
                    "error": "Nenhum agent card disponível",
                    "suggestion": "Adicione agent cards no diretório 'agent_cards/'"
                })
        
        try:
            # Gerar embedding para a query
            query_embedding = await embedding_service.generate_embedding(query)
            
            # Calcular similaridade (produto escalar)
            similarities = []
            for card_embedding in df['card_embeddings']:
                similarity = np.dot(card_embedding, query_embedding)
                similarities.append(similarity)
            
            # Encontrar melhor match
            best_match_index = np.argmax(similarities)
            best_score = similarities[best_match_index]
            
            logger.debug(f'Melhor match para "{query}": índice {best_match_index}, score {best_score:.3f}')
            
            return json.dumps({
                "agent_card": df.iloc[best_match_index]['agent_card'],
                "confidence": float(best_score),
                "uri": df.iloc[best_match_index]['card_uri']
            })
            
        except Exception as e:
            logger.error(f"Erro ao buscar agente: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool(
        name='analyze_agent_with_claude',
        description='Analisa um agent card usando Claude para insights detalhados.'
    )
    async def analyze_agent_with_claude(agent_name: str) -> str:
        """Usa Claude para analisar profundamente um agent card."""
        nonlocal df
        
        if df is None:
            df = await build_agent_card_embeddings()
            if df is None:
                return json.dumps({"error": "Nenhum agent card disponível"})
        
        try:
            # Encontrar o agent card pelo nome
            agent_card = None
            for _, row in df.iterrows():
                if agent_name.lower() in json.dumps(row['agent_card']).lower():
                    agent_card = row['agent_card']
                    break
            
            if not agent_card:
                return json.dumps({"error": f"Agent '{agent_name}' não encontrado"})
            
            # Pedir análise ao Claude
            prompt = f"""
            Analise este agent card e forneça insights sobre suas capacidades:
            
            {json.dumps(agent_card, indent=2)}
            
            Responda com:
            1. Principais capacidades
            2. Casos de uso ideais
            3. Limitações conhecidas
            4. Sugestões de integração
            """
            
            result = await query(prompt)
            
            if isinstance(result, ResultMessage):
                analysis = result.content
            else:
                analysis = str(result)
            
            return json.dumps({
                "agent": agent_card.get("name", "Unknown"),
                "analysis": analysis
            })
            
        except Exception as e:
            logger.error(f"Erro ao analisar agente: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.resource(
        name='list_all_agents',
        description='Lista todos os agent cards disponíveis'
    )
    async def list_all_agents() -> str:
        """Retorna lista de todos os agents disponíveis."""
        _, agent_cards = load_agent_cards()
        
        agents_list = []
        for card in agent_cards:
            agents_list.append({
                "name": card.get("name", "Unknown"),
                "description": card.get("description", ""),
                "url": card.get("url", "")
            })
        
        return json.dumps({
            "total": len(agents_list),
            "agents": agents_list
        })
    
    # Inicializar servidor
    logger.info(f"Servidor MCP com Claude iniciado em {host}:{port}")
    logger.info("Usando Claude Code SDK para embeddings e análise")
    
    # Executar servidor
    if transport == 'stdio':
        mcp.run_stdio()
    else:
        mcp.run()


if __name__ == '__main__':
    # Configurações padrão
    host = os.getenv('MCP_HOST', 'localhost')
    port = int(os.getenv('MCP_PORT', '8175'))
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    
    # Executar servidor
    serve(host, port, transport)
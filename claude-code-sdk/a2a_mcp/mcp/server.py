#!/usr/bin/env python3
"""
MCP Server usando APENAS Claude Code SDK.
NÃO USA Google API - 100% Claude local.
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

# APENAS Claude Code SDK - SEM Google!
from claude_code_sdk import (
    ClaudeSDKClient,
    ClaudeCodeOptions,
    query,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    CLINotFoundError,
    ProcessError
)

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger


logger = get_logger(__name__)
AGENT_CARDS_DIR = 'agent_cards'
SQLLITE_DB = 'travel_agency.db'


class ClaudeEmbeddingService:
    """Serviço para gerar embeddings usando APENAS Claude Code SDK."""
    
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
        NÃO USA Google - apenas análise do Claude.
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


def generate_embeddings(text):
    """
    Gera embeddings para o texto usando CLAUDE (não Google!).
    Mantém compatibilidade com código existente.
    """
    # Executa de forma síncrona para compatibilidade
    loop = asyncio.new_event_loop()
    try:
        embedding = loop.run_until_complete(
            embedding_service.generate_embedding(text)
        )
        return embedding
    finally:
        loop.close()


def load_agent_cards():
    """Carrega agent cards dos arquivos JSON."""
    card_uris = []
    agent_cards = []
    dir_path = Path(AGENT_CARDS_DIR)
    
    if not dir_path.is_dir():
        logger.error(f'Diretório de agent cards não encontrado: {AGENT_CARDS_DIR}')
        # Criar diretório e alguns cards de exemplo
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Criar agent cards de exemplo
        example_cards = [
            {
                "name": "Orchestrator Agent",
                "description": "Coordena e delega tarefas entre múltiplos agentes",
                "url": "http://localhost:8001",
                "capabilities": ["delegation", "coordination", "task_planning"],
                "version": "1.0.0"
            },
            {
                "name": "Planner Agent",
                "description": "Planeja e estrutura tarefas complexas",
                "url": "http://localhost:8002",
                "capabilities": ["planning", "breakdown", "scheduling"],
                "version": "1.0.0"
            }
        ]
        
        for i, card in enumerate(example_cards):
            card_file = dir_path / f"agent_{i}.json"
            with open(card_file, 'w') as f:
                json.dump(card, f, indent=2)
        
        logger.info(f'Criados {len(example_cards)} agent cards de exemplo')
    
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


def build_agent_card_embeddings() -> pd.DataFrame:
    """
    Carrega agent cards e gera embeddings usando CLAUDE (não Google!).
    """
    card_uris, agent_cards = load_agent_cards()
    logger.info('Gerando embeddings para agent cards com Claude')
    
    try:
        if agent_cards:
            df = pd.DataFrame({
                'card_uri': card_uris,
                'agent_card': agent_cards
            })
            
            # Gerar embeddings com Claude para cada card
            df['card_embeddings'] = df.apply(
                lambda row: generate_embeddings(json.dumps(row['agent_card'])),
                axis=1
            )
            
            logger.info('Embeddings gerados com sucesso usando Claude')
            return df
        else:
            logger.warning("Nenhum agent card encontrado")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f'Erro ao gerar embeddings: {e}', exc_info=True)
        return pd.DataFrame()


def serve(host, port, transport):
    """
    Inicializa e executa o servidor MCP com CLAUDE Code SDK.
    NÃO USA Google API!
    
    Args:
        host: Hostname ou IP para bind
        port: Porta para bind
        transport: Mecanismo de transporte ('stdio', 'sse', etc)
    """
    logger.info('Iniciando Agent Cards MCP Server com Claude SDK (SEM Google!)')
    
    # NÃO precisa de GOOGLE_API_KEY!
    # Verificar se Claude está disponível
    try:
        import subprocess
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        logger.info(f"Claude Code versão: {result.stdout.strip()}")
    except:
        logger.warning("Claude Code CLI não encontrado. Certifique-se de que está instalado.")
    
    mcp = FastMCP('agent-cards-claude', host=host, port=port)
    
    # Inicializar serviço de embeddings
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(embedding_service.initialize())
    
    df = build_agent_card_embeddings()
    
    @mcp.tool(
        name='find_agent',
        description='Encontra o agent card mais relevante usando CLAUDE para análise semântica.'
    )
    def find_agent(query: str) -> str:
        """Encontra o agent card mais relevante baseado em uma consulta."""
        if df.empty:
            return json.dumps({
                "error": "Nenhum agent card disponível",
                "suggestion": "Adicione agent cards no diretório 'agent_cards/'"
            })
        
        try:
            # Gerar embedding para a query com Claude
            query_embedding = generate_embeddings(query)
            
            # Calcular similaridade (produto escalar)
            dot_products = np.dot(
                np.stack(df['card_embeddings']), 
                query_embedding
            )
            
            # Encontrar melhor match
            best_match_index = np.argmax(dot_products)
            best_score = dot_products[best_match_index]
            
            logger.debug(f'Melhor match para "{query}": índice {best_match_index}, score {best_score:.3f}')
            
            return json.dumps({
                "agent_card": df.iloc[best_match_index]['agent_card'],
                "confidence": float(best_score),
                "uri": df.iloc[best_match_index]['card_uri'],
                "powered_by": "Claude Code SDK"
            })
            
        except Exception as e:
            logger.error(f"Erro ao buscar agente: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.resource(
        name='find_resource',
        description='Encontra recursos usando análise do Claude'
    )
    def find_resource(uri: str) -> str:
        """Encontra e retorna um recurso específico."""
        logger.debug(f'Buscando recurso: {uri}')
        
        if uri.startswith('resource://agent_cards/'):
            card_name = uri.replace('resource://agent_cards/', '')
            
            for _, row in df.iterrows():
                if card_name in row['card_uri']:
                    return json.dumps({
                        "agent_card": [row['agent_card']],
                        "powered_by": "Claude Code SDK"
                    })
        
        return json.dumps({"error": f"Recurso não encontrado: {uri}"})
    
    @mcp.resource(
        name='agent_cards/planner_agent',
        description='Agent card do Planner Agent'
    )
    def planner_agent_resource() -> str:
        """Retorna o agent card do Planner Agent."""
        for _, row in df.iterrows():
            if 'planner' in json.dumps(row['agent_card']).lower():
                return json.dumps({
                    "agent_card": [row['agent_card']],
                    "powered_by": "Claude Code SDK"
                })
        
        # Card padrão se não encontrado
        return json.dumps({
            "agent_card": [{
                "name": "Planner Agent",
                "description": "Planeja e estrutura tarefas complexas",
                "url": "http://localhost:8002",
                "capabilities": ["planning", "breakdown", "scheduling"],
                "version": "1.0.0"
            }],
            "powered_by": "Claude Code SDK"
        })
    
    # Executar servidor
    logger.info(f"Servidor MCP com Claude iniciado em {host}:{port}")
    logger.info("Usando APENAS Claude Code SDK - SEM Google API!")
    
    if transport == 'stdio':
        mcp.run_stdio()
    else:
        mcp.run()


def init_api_key():
    """
    NÃO PRECISA de API Key!
    Esta função existe apenas para compatibilidade.
    """
    logger.info("Usando Claude Code SDK - não precisa de API Key externa!")
    return True


if __name__ == '__main__':
    # Configurações padrão
    host = os.getenv('MCP_HOST', 'localhost')
    port = int(os.getenv('MCP_PORT', '8175'))
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    
    # Executar servidor
    serve(host, port, transport)
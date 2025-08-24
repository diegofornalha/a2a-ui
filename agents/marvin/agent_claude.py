"""
Agente Marvin usando Claude Code SDK ao invés de OpenAI/Marvin.
100% Claude local, sem necessidade de API keys externas.
"""

import logging
import os
import sys
import json
import threading
from collections.abc import AsyncIterable
from typing import Annotated, Any, ClassVar, TypeVar, Generic
from dataclasses import dataclass

from a2a.types import TextPart
from pydantic import BaseModel, Field

# Adicionar caminho do Claude SDK
sys.path.insert(0, '/home/codable/terminal/claude-code-sdk-python/src')
sys.path.insert(0, '/home/codable/terminal/ai-sdk-provider-python/src')

# Importar Claude Code SDK
from claude_code_sdk import query as claude_query, ClaudeSDKClient, ClaudeCodeOptions

logger = logging.getLogger(__name__)


ClarifyingQuestion = Annotated[
    str, Field(description="A clarifying question to ask the user")
]


def _to_text_part(text: str) -> TextPart:
    return TextPart(type="text", text=text)


class ExtractionOutcome(BaseModel, Generic[TypeVar('T')]):
    """Represents the result of trying to extract information."""
    
    extracted_data: Any
    summary: str = Field(
        description="summary of the extracted information.",
    )


class ClaudeMemory:
    """Gerenciador de memória de sessão para Claude."""
    
    def __init__(self):
        self.sessions = {}
    
    def get_context(self, session_id: str) -> str:
        """Obtém contexto da sessão."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return "\n".join(self.sessions[session_id])
    
    def add_to_context(self, session_id: str, message: str):
        """Adiciona mensagem ao contexto da sessão."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(message)
        # Manter apenas últimas 10 mensagens
        if len(self.sessions[session_id]) > 10:
            self.sessions[session_id] = self.sessions[session_id][-10:]


# Instância global de memória
memory = ClaudeMemory()


class ClaudeExtractorAgent:
    """
    Agente de extração de informações usando Claude Code SDK.
    Substitui o Marvin framework por Claude local.
    """
    
    SUPPORTED_CONTENT_TYPES: ClassVar[list[str]] = [
        "text",
        "text/plain",
        "application/json",
    ]
    
    def __init__(self, instructions: str, result_type: type):
        """
        Inicializa o agente com instruções e tipo de resultado.
        
        Args:
            instructions: Personalidade/instruções do agente
            result_type: Tipo de dados a extrair
        """
        self.instructions = instructions
        self.result_type = result_type
        self.client = None
    
    async def _get_claude_response(self, prompt: str, session_id: str) -> str:
        """
        Obtém resposta do Claude usando o SDK.
        
        Args:
            prompt: Pergunta/comando para o Claude
            session_id: ID da sessão para manter contexto
            
        Returns:
            Resposta do Claude como string
        """
        try:
            # Obter contexto da sessão
            context = memory.get_context(session_id)
            
            # Criar prompt completo com contexto e instruções
            full_prompt = f"""
{self.instructions}

Contexto da conversa:
{context}

Tarefa atual: {prompt}

Se você precisar de mais informações, faça uma pergunta clarificadora.
Se você tiver informações suficientes, extraia os dados solicitados.

Responda em formato JSON com a estrutura:
{{
    "type": "extraction" ou "question",
    "data": (dados extraídos se type="extraction"),
    "summary": "resumo do que foi extraído",
    "question": "pergunta se type="question"
}}
"""
            
            # Consultar Claude
            response_text = ""
            async for message in claude_query(prompt=full_prompt):
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            response_text += block.text
            
            # Adicionar ao contexto
            memory.add_to_context(session_id, f"User: {prompt}")
            memory.add_to_context(session_id, f"Assistant: {response_text}")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Erro ao consultar Claude: {e}")
            raise
    
    async def invoke(self, query: str, sessionId: str) -> dict[str, Any]:
        """
        Processa uma query do usuário com Claude.
        
        Args:
            query: Input do usuário
            sessionId: Identificador da sessão
            
        Returns:
            Dicionário com o resultado do processamento
        """
        try:
            logger.debug(
                f"[Session: {sessionId}] PID: {os.getpid()} | "
                f"PyThread: {threading.get_ident()} | "
                f"Using Claude SDK for session: {sessionId}"
            )
            
            # Obter resposta do Claude
            response = await self._get_claude_response(query, sessionId)
            
            # Tentar parsear como JSON
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # Se não for JSON, tratar como pergunta clarificadora
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "text_parts": [_to_text_part(response)],
                    "data": None,
                }
            
            # Processar resposta baseada no tipo
            if result.get("type") == "extraction":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "text_parts": [_to_text_part(result.get("summary", "Dados extraídos com sucesso"))],
                    "data": result.get("data", {}),
                }
            else:
                # Pergunta clarificadora
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "text_parts": [_to_text_part(result.get("question", "Pode fornecer mais informações?"))],
                    "data": None,
                }
                
        except Exception as e:
            logger.exception(f"Erro durante invocação para sessão {sessionId}")
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "text_parts": [
                    _to_text_part(
                        f"Desculpe, encontrei um erro ao processar sua solicitação: {str(e)}"
                    )
                ],
                "data": None,
            }
    
    async def stream(self, query: str, sessionId: str) -> AsyncIterable[dict[str, Any]]:
        """
        Versão streaming do processamento (retorna resultado incrementalmente).
        
        Args:
            query: Input do usuário
            sessionId: Identificador da sessão
            
        Yields:
            Dicionários com partes da resposta
        """
        try:
            logger.debug(f"[Session: {sessionId}] Starting streaming response with Claude")
            
            # Obter contexto
            context = memory.get_context(sessionId)
            
            # Criar prompt
            full_prompt = f"""
{self.instructions}

Contexto: {context}

Solicitação: {query}

Responda de forma conversacional e depois forneça os dados estruturados se possível.
"""
            
            response_text = ""
            
            # Stream da resposta
            async for message in claude_query(prompt=full_prompt):
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            chunk = block.text
                            response_text += chunk
                            
                            # Enviar chunk
                            yield {
                                "is_task_complete": False,
                                "require_user_input": False,
                                "text_parts": [_to_text_part(chunk)],
                                "data": None,
                            }
            
            # Adicionar ao contexto
            memory.add_to_context(sessionId, f"User: {query}")
            memory.add_to_context(sessionId, f"Assistant: {response_text}")
            
            # Enviar resultado final
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "text_parts": [],
                "data": {"response": response_text},
            }
            
        except Exception as e:
            logger.exception(f"Erro durante streaming para sessão {sessionId}")
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "text_parts": [
                    _to_text_part(f"Erro no streaming: {str(e)}")
                ],
                "data": None,
            }


# Função de compatibilidade para substituir ExtractorAgent
def ExtractorAgent(instructions: str, result_type: type):
    """
    Função de compatibilidade que retorna ClaudeExtractorAgent.
    Permite substituir o agente Marvin sem modificar código existente.
    """
    return ClaudeExtractorAgent(instructions, result_type)
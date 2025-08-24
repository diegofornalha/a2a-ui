"""
Integração do Claude Code SDK com a UI A2A.

Este módulo conecta o Claude Code SDK Python oficial com o backend da UI,
permitindo que as respostas do Claude apareçam diretamente na interface.
"""

import asyncio
import json
import traceback
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

# Importar do Claude Code SDK oficial
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

# Importar do AI SDK Provider
from ai_sdk_provider_claude_code import (
    ClaudeCodeProvider,
    ClaudeCodeLanguageModel,
    ClaudeCodeSettings
)


@dataclass
class ClaudeSDKResponse:
    """Resposta do Claude SDK formatada para a UI."""
    message_id: str
    context_id: str
    role: str = "assistant"
    content: str = ""
    parts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    

class ClaudeSDKIntegration:
    """
    Integração do Claude Code SDK com a UI A2A.
    
    Esta classe gerencia a comunicação entre:
    1. UI (frontend Mesop)
    2. Backend FastAPI
    3. Claude Code SDK Python
    4. Claude Code (aplicação desktop)
    """
    
    def __init__(self, settings: Optional[ClaudeCodeSettings] = None):
        """
        Inicializa a integração do Claude SDK.
        
        Args:
            settings: Configurações do Claude Code SDK
        """
        self.settings = settings or ClaudeCodeSettings()
        self.provider = ClaudeCodeProvider(settings=self.settings)
        self.active_sessions: Dict[str, ClaudeSDKClient] = {}
        
    async def process_message(
        self,
        message_content: str,
        context_id: str,
        message_id: str,
        use_streaming: bool = False
    ) -> ClaudeSDKResponse:
        """
        Processa uma mensagem usando o Claude Code SDK.
        
        Args:
            message_content: Conteúdo da mensagem do usuário
            context_id: ID do contexto/conversa
            message_id: ID da mensagem
            use_streaming: Se deve usar modo streaming
            
        Returns:
            ClaudeSDKResponse com a resposta do Claude
        """
        try:
            # Verificar se já existe uma sessão ativa para este contexto
            if context_id not in self.active_sessions:
                # Criar nova sessão
                client = ClaudeSDKClient(
                    options=ClaudeCodeOptions(
                        claude_cli_path="claude",  # Comando claude no PATH
                        log_level="info"
                    )
                )
                self.active_sessions[context_id] = client
            else:
                client = self.active_sessions[context_id]
            
            if use_streaming:
                # Modo streaming - receber respostas em tempo real
                response_content = ""
                response_parts = []
                
                async with client:
                    # Enviar mensagem
                    await client.query(message_content)
                    
                    # Receber respostas em streaming
                    async for message in client.receive_messages():
                        if isinstance(message, AssistantMessage):
                            # Processar blocos de texto
                            for block in message.content:
                                if isinstance(block, TextBlock):
                                    response_content += block.text
                                    response_parts.append({
                                        "type": "text",
                                        "text": block.text
                                    })
                            
                            # Se a mensagem estiver completa, parar
                            if hasattr(message, 'stop_reason') and message.stop_reason:
                                break
            else:
                # Modo não-streaming - usar query simples
                result = await query(message_content)
                
                if isinstance(result, ResultMessage):
                    response_content = result.content
                    response_parts = [{"type": "text", "text": result.content}]
                else:
                    response_content = str(result)
                    response_parts = [{"type": "text", "text": str(result)}]
            
            # Criar resposta formatada
            return ClaudeSDKResponse(
                message_id=f"claude_response_{message_id}",
                context_id=context_id,
                content=response_content,
                parts=response_parts,
                metadata={
                    "sdk_version": "1.0.0",
                    "model": self.settings.model_id or "opus",
                    "streaming": use_streaming
                }
            )
            
        except CLINotFoundError as e:
            # Claude CLI não encontrado
            error_msg = (
                "⚠️ Claude Code não está instalado ou não foi encontrado no PATH.\n"
                "Por favor, instale o Claude Code Desktop e certifique-se de que "
                "o comando 'claude' está disponível no terminal."
            )
            return ClaudeSDKResponse(
                message_id=f"error_{message_id}",
                context_id=context_id,
                content=error_msg,
                parts=[{"type": "text", "text": error_msg}],
                metadata={"error": str(e), "error_type": "cli_not_found"}
            )
            
        except ProcessError as e:
            # Erro no processo do Claude
            error_msg = f"❌ Erro ao processar com Claude: {str(e)}"
            return ClaudeSDKResponse(
                message_id=f"error_{message_id}",
                context_id=context_id,
                content=error_msg,
                parts=[{"type": "text", "text": error_msg}],
                metadata={"error": str(e), "error_type": "process_error"}
            )
            
        except Exception as e:
            # Erro genérico
            error_msg = f"❌ Erro inesperado: {str(e)}\n{traceback.format_exc()}"
            return ClaudeSDKResponse(
                message_id=f"error_{message_id}",
                context_id=context_id,
                content=error_msg,
                parts=[{"type": "text", "text": error_msg}],
                metadata={"error": str(e), "error_type": "unknown"}
            )
    
    async def close_session(self, context_id: str):
        """
        Fecha uma sessão ativa do Claude SDK.
        
        Args:
            context_id: ID do contexto/conversa
        """
        if context_id in self.active_sessions:
            client = self.active_sessions[context_id]
            try:
                await client.disconnect()
            except:
                pass  # Ignorar erros ao desconectar
            del self.active_sessions[context_id]
    
    async def close_all_sessions(self):
        """Fecha todas as sessões ativas."""
        for context_id in list(self.active_sessions.keys()):
            await self.close_session(context_id)
    
    def get_active_sessions(self) -> List[str]:
        """Retorna lista de IDs de contextos com sessões ativas."""
        return list(self.active_sessions.keys())
    
    def format_for_ui(self, response: ClaudeSDKResponse) -> Dict[str, Any]:
        """
        Formata a resposta do Claude SDK para o formato esperado pela UI.
        
        Args:
            response: Resposta do Claude SDK
            
        Returns:
            Dicionário formatado para a UI
        """
        return {
            "message_id": response.message_id,
            "context_id": response.context_id,
            "role": response.role,
            "parts": response.parts,
            "metadata": response.metadata,
            "timestamp": response.timestamp
        }


# Instância global para ser usada pelo backend
claude_sdk_integration = None

def get_claude_sdk_integration() -> ClaudeSDKIntegration:
    """
    Retorna a instância global da integração do Claude SDK.
    Cria uma nova se não existir.
    """
    global claude_sdk_integration
    if claude_sdk_integration is None:
        claude_sdk_integration = ClaudeSDKIntegration()
    return claude_sdk_integration
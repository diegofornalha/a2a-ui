"""
Agente Claude usando o Claude Code SDK
Integração moderna com o sistema A2A
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from service.client.claude_sdk_client import ClaudeSDKClient, ClaudeSDKResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeSDKAgent:
    """
    Agente Claude usando o Claude Code SDK oficial
    Substitui completamente o uso do Gemini/Vertex AI
    """
    
    def __init__(self):
        """Inicializa o agente Claude SDK"""
        self.name = "Claude SDK Assistant"
        self.agent_id = "claude-sdk-agent"
        self.version = "2.0.0"
        self.capabilities = [
            "chat",
            "code_generation",
            "code_analysis",
            "question_answering",
            "task_execution",
            "tool_usage",
            "streaming"
        ]
        self.sdk_client = ClaudeSDKClient()
        self.conversation_history: List[Dict[str, Any]] = []
        self.is_ready = self.sdk_client.initialized
        
        if self.is_ready:
            logger.info(f"✅ {self.name} inicializado com sucesso")
        else:
            logger.error(f"❌ {self.name} falhou ao inicializar")
    
    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário usando Claude SDK
        
        Args:
            message: Mensagem do usuário
            context: Contexto adicional
            conversation_id: ID da conversa
            
        Returns:
            Dict com a resposta
        """
        if not self.is_ready:
            return {
                "success": False,
                "error": "Claude SDK Agent não está pronto",
                "agent_id": self.agent_id
            }
        
        try:
            # Adicionar à história
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "conversation_id": conversation_id
            })
            
            # Preparar contexto
            context_str = None
            if context:
                # Incluir histórico recente se disponível
                if len(self.conversation_history) > 1:
                    recent = self.conversation_history[-3:]  # Últimas 3 mensagens
                    context_str = "Histórico recente:\n"
                    for msg in recent[:-1]:  # Excluir a mensagem atual
                        context_str += f"{msg['role']}: {msg['content'][:100]}...\n"
                
                # Adicionar contexto fornecido
                if context:
                    context_str = (context_str or "") + f"\nContexto: {context}"
            
            # Processar com Claude SDK
            response = await self.sdk_client.query_simple(message, context_str)
            
            if response.success:
                # Adicionar resposta à história
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content,
                    "timestamp": datetime.now().isoformat(),
                    "conversation_id": conversation_id
                })
                
                return {
                    "success": True,
                    "content": response.content,
                    "agent_id": self.agent_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": response.metadata
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "agent_id": self.agent_id
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def generate_code(
        self,
        description: str,
        language: str = "python",
        framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera código usando Claude SDK
        
        Args:
            description: Descrição do código a gerar
            language: Linguagem de programação
            framework: Framework opcional
            
        Returns:
            Dict com o código gerado
        """
        if not self.is_ready:
            return {
                "success": False,
                "error": "Claude SDK Agent não está pronto",
                "agent_id": self.agent_id
            }
        
        try:
            response = await self.sdk_client.generate_code(
                description,
                language,
                framework
            )
            
            if response.success:
                return {
                    "success": True,
                    "code": response.content,
                    "language": language,
                    "framework": framework,
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": response.metadata
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "agent_id": self.agent_id
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar código: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        task: str = "analyze"
    ) -> Dict[str, Any]:
        """
        Analisa código usando Claude SDK
        
        Args:
            code: Código a analisar
            language: Linguagem do código
            task: Tipo de análise
            
        Returns:
            Dict com a análise
        """
        if not self.is_ready:
            return {
                "success": False,
                "error": "Claude SDK Agent não está pronto",
                "agent_id": self.agent_id
            }
        
        try:
            response = await self.sdk_client.analyze_code(
                code,
                language,
                task
            )
            
            if response.success:
                return {
                    "success": True,
                    "analysis": response.content,
                    "task": task,
                    "language": language,
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": response.metadata
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "agent_id": self.agent_id
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao analisar código: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def execute_task(
        self,
        task: str,
        agents: Optional[List[str]] = None,
        use_tools: bool = False
    ) -> Dict[str, Any]:
        """
        Executa tarefa com coordenação A2A
        
        Args:
            task: Descrição da tarefa
            agents: Lista de agentes para simular perspectivas
            use_tools: Se deve usar ferramentas (Read, Write, etc)
            
        Returns:
            Dict com o resultado
        """
        if not self.is_ready:
            return {
                "success": False,
                "error": "Claude SDK Agent não está pronto",
                "agent_id": self.agent_id
            }
        
        try:
            if use_tools:
                # Executar com ferramentas habilitadas
                response = await self.sdk_client.query_with_tools(
                    task,
                    allowed_tools=["Read", "Write"]
                )
            else:
                # Executar sem ferramentas
                response = await self.sdk_client.execute_with_a2a(task, agents)
            
            if response.success:
                return {
                    "success": True,
                    "result": response.content,
                    "task": task,
                    "agents": agents,
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": response.metadata,
                    "used_tools": use_tools
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "agent_id": self.agent_id
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar tarefa: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def stream_response(
        self,
        prompt: str
    ):
        """
        Stream de resposta do Claude SDK
        
        Args:
            prompt: Prompt para gerar resposta
            
        Yields:
            Chunks da resposta
        """
        if not self.is_ready:
            yield {
                "success": False,
                "error": "Claude SDK Agent não está pronto",
                "agent_id": self.agent_id
            }
            return
        
        try:
            async for chunk in self.sdk_client.stream_response(prompt):
                yield {
                    "success": True,
                    "chunk": chunk,
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"❌ Erro no streaming: {str(e)}")
            yield {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status do agente
        
        Returns:
            Dict com informações do status
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "is_ready": self.is_ready,
            "capabilities": self.capabilities,
            "conversation_count": len(self.conversation_history),
            "sdk_initialized": self.sdk_client.initialized,
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_history(self):
        """Limpa o histórico de conversação"""
        self.conversation_history = []
        logger.info(f"📝 Histórico de {self.name} limpo")
    
    def get_agent_card(self) -> Dict[str, Any]:
        """
        Retorna o card do agente para registro A2A
        
        Returns:
            Dict com informações do agente
        """
        return {
            "id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "description": "Claude SDK Assistant - Using official Claude Code SDK",
            "capabilities": self.capabilities,
            "endpoint": "/claude-sdk",
            "status": "ready" if self.is_ready else "error",
            "metadata": {
                "uses_sdk": True,
                "requires_api_key": False,
                "supports_streaming": True,
                "supports_tools": True,
                "sdk_version": "0.0.20"
            }
        }


# Singleton do agente
_claude_sdk_agent = None


def get_claude_sdk_agent() -> ClaudeSDKAgent:
    """
    Retorna a instância singleton do agente Claude SDK
    
    Returns:
        ClaudeSDKAgent: Instância do agente
    """
    global _claude_sdk_agent
    if _claude_sdk_agent is None:
        _claude_sdk_agent = ClaudeSDKAgent()
    return _claude_sdk_agent


# Teste do agente
if __name__ == "__main__":
    import anyio
    
    async def test_agent():
        print("🧪 Testando Claude SDK Agent para A2A")
        print("-" * 50)
        
        agent = get_claude_sdk_agent()
        
        # Status
        print("\n📊 Status do agente:")
        status = agent.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        if not agent.is_ready:
            print("\n❌ Agente não está pronto. Instale o SDK:")
            print("   pip install claude-code-sdk")
            return
        
        # Teste de mensagem
        print("\n💬 Teste de chat:")
        response = await agent.process_message("Olá! O que é Python?")
        if response["success"]:
            print(f"  ✅ Resposta: {response['content'][:200]}...")
        else:
            print(f"  ❌ Erro: {response['error']}")
        
        # Teste de geração de código
        print("\n🔧 Teste de geração de código:")
        response = await agent.generate_code(
            "função para calcular fatorial",
            language="python"
        )
        if response["success"]:
            print(f"  ✅ Código gerado:")
            print(response['code'][:300])
        else:
            print(f"  ❌ Erro: {response['error']}")
        
        # Teste de análise
        print("\n🔍 Teste de análise de código:")
        code = "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
        response = await agent.analyze_code(code, task="explain")
        if response["success"]:
            print(f"  ✅ Análise:")
            print(response['analysis'][:200] + "...")
        else:
            print(f"  ❌ Erro: {response['error']}")
        
        # Card do agente
        print("\n🎴 Card do agente:")
        card = agent.get_agent_card()
        for key, value in card.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Testes concluídos!")
    
    anyio.run(test_agent)
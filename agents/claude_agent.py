"""
Agente Claude integrado ao sistema A2A
Usa o Claude CLI local sem necessidade de API key
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from service.client.claude_cli_client import ClaudeCLIClient, ClaudeResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeAgent:
    """
    Agente Claude para o sistema A2A
    Wrapper para integrar Claude CLI com o framework A2A
    """
    
    def __init__(self):
        """Inicializa o agente Claude"""
        self.name = "Claude Assistant"
        self.agent_id = "claude-agent"
        self.version = "1.0.0"
        self.capabilities = [
            "chat",
            "code_generation",
            "code_analysis",
            "question_answering",
            "task_execution"
        ]
        self.cli_client = ClaudeCLIClient()
        self.conversation_history: List[Dict[str, Any]] = []
        self.is_ready = False
        self._initialize()
    
    def _initialize(self):
        """Inicializa e verifica o agente"""
        try:
            # Verificar se CLI está disponível
            self.cli_client._verify_cli()
            self.is_ready = True
            logger.info(f"✅ {self.name} inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar {self.name}: {str(e)}")
            self.is_ready = False
    
    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário
        
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
                "error": "Agente Claude não está pronto",
                "agent_id": self.agent_id
            }
        
        try:
            # Adicionar à história
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Preparar contexto
            context_str = None
            if context:
                context_str = f"Contexto: {context}"
            
            # Processar com Claude CLI
            response = await self.cli_client.query_simple(message, context_str)
            
            if response.success:
                # Adicionar resposta à história
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "content": response.content,
                    "agent_id": self.agent_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
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
        Gera código usando Claude
        
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
                "error": "Agente Claude não está pronto",
                "agent_id": self.agent_id
            }
        
        try:
            response = await self.cli_client.generate_code(
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
                    "timestamp": datetime.now().isoformat()
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
        Analisa código usando Claude
        
        Args:
            code: Código a analisar
            language: Linguagem do código
            task: Tipo de análise (analyze, review, optimize, explain)
            
        Returns:
            Dict com a análise
        """
        if not self.is_ready:
            return {
                "success": False,
                "error": "Agente Claude não está pronto",
                "agent_id": self.agent_id
            }
        
        try:
            response = await self.cli_client.analyze_code(
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
                    "timestamp": datetime.now().isoformat()
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
        agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executa tarefa com coordenação A2A simulada
        
        Args:
            task: Descrição da tarefa
            agents: Lista de agentes para simular perspectivas
            
        Returns:
            Dict com o resultado
        """
        if not self.is_ready:
            return {
                "success": False,
                "error": "Agente Claude não está pronto",
                "agent_id": self.agent_id
            }
        
        try:
            response = await self.cli_client.execute_with_a2a(task, agents)
            
            if response.success:
                return {
                    "success": True,
                    "result": response.content,
                    "task": task,
                    "agents": agents,
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
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
        Stream de resposta do Claude
        
        Args:
            prompt: Prompt para gerar resposta
            
        Yields:
            Chunks da resposta
        """
        if not self.is_ready:
            yield {
                "success": False,
                "error": "Agente Claude não está pronto",
                "agent_id": self.agent_id
            }
            return
        
        try:
            async for chunk in self.cli_client.stream_response(prompt):
                yield {
                    "success": True,
                    "chunk": chunk,
                    "agent_id": self.agent_id
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
            "description": "Claude Assistant - AI agent using Claude CLI without API key",
            "capabilities": self.capabilities,
            "endpoint": "/claude",
            "status": "ready" if self.is_ready else "error",
            "metadata": {
                "uses_cli": True,
                "requires_api_key": False,
                "supports_streaming": True
            }
        }


# Singleton do agente
_claude_agent = None


def get_claude_agent() -> ClaudeAgent:
    """
    Retorna a instância singleton do agente Claude
    
    Returns:
        ClaudeAgent: Instância do agente
    """
    global _claude_agent
    if _claude_agent is None:
        _claude_agent = ClaudeAgent()
    return _claude_agent


# Exemplo de uso
if __name__ == "__main__":
    async def test_agent():
        print("🧪 Testando Claude Agent para A2A")
        print("-" * 50)
        
        agent = get_claude_agent()
        
        # Status
        print("\n📊 Status do agente:")
        status = agent.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Teste de mensagem
        print("\n💬 Teste de chat:")
        response = await agent.process_message("Olá! Quem é você?")
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
        
        # Card do agente
        print("\n🎴 Card do agente:")
        card = agent.get_agent_card()
        for key, value in card.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Testes concluídos!")
    
    asyncio.run(test_agent())
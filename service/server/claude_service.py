"""
Serviço Claude para integração com o backend A2A
Gerencia o cliente Claude CLI e fornece endpoints
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from agents.claude_agent import get_claude_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Serviço para gerenciar interações com Claude no backend A2A
    """
    
    def __init__(self):
        """Inicializa o serviço Claude"""
        self.agent = get_claude_agent()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Inicializa o serviço"""
        try:
            if self.agent.is_ready:
                self.initialized = True
                logger.info("✅ Claude Service inicializado com sucesso")
            else:
                logger.error("❌ Claude Agent não está pronto")
                self.initialized = False
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Claude Service: {str(e)}")
            self.initialized = False
    
    async def handle_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa uma query para o Claude
        
        Args:
            query: Query do usuário
            session_id: ID da sessão (opcional)
            context: Contexto adicional
            
        Returns:
            Resposta do Claude
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Claude Service não está inicializado"
            }
        
        try:
            # Criar sessão se necessário
            if session_id and session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "created_at": datetime.now().isoformat(),
                    "messages": []
                }
            
            # Processar query
            response = await self.agent.process_message(
                query,
                context=context,
                conversation_id=session_id
            )
            
            # Salvar na sessão
            if session_id and response.get("success"):
                self.active_sessions[session_id]["messages"].append({
                    "query": query,
                    "response": response.get("content"),
                    "timestamp": datetime.now().isoformat()
                })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar query: {str(e)}")
            return {
                "success": False,
                "error": str(e)
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
            description: Descrição do código
            language: Linguagem de programação
            framework: Framework (opcional)
            
        Returns:
            Código gerado
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Claude Service não está inicializado"
            }
        
        try:
            return await self.agent.generate_code(
                description,
                language,
                framework
            )
        except Exception as e:
            logger.error(f"❌ Erro ao gerar código: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "analyze"
    ) -> Dict[str, Any]:
        """
        Analisa código usando Claude
        
        Args:
            code: Código a analisar
            language: Linguagem do código
            analysis_type: Tipo de análise
            
        Returns:
            Análise do código
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Claude Service não está inicializado"
            }
        
        try:
            return await self.agent.analyze_code(
                code,
                language,
                analysis_type
            )
        except Exception as e:
            logger.error(f"❌ Erro ao analisar código: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_a2a_task(
        self,
        task: str,
        agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executa tarefa com coordenação A2A
        
        Args:
            task: Descrição da tarefa
            agents: Lista de agentes
            
        Returns:
            Resultado da execução
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Claude Service não está inicializado"
            }
        
        try:
            return await self.agent.execute_task(task, agents)
        except Exception as e:
            logger.error(f"❌ Erro ao executar tarefa A2A: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stream_response(
        self,
        prompt: str,
        session_id: Optional[str] = None
    ):
        """
        Stream de resposta do Claude
        
        Args:
            prompt: Prompt para gerar resposta
            session_id: ID da sessão (opcional)
            
        Yields:
            Chunks da resposta
        """
        if not self.initialized:
            yield {
                "success": False,
                "error": "Claude Service não está inicializado"
            }
            return
        
        try:
            async for chunk in self.agent.stream_response(prompt):
                # Adicionar session_id ao chunk se fornecido
                if session_id:
                    chunk["session_id"] = session_id
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ Erro no streaming: {str(e)}")
            yield {
                "success": False,
                "error": str(e)
            }
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna dados de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dados da sessão ou None
        """
        return self.active_sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Lista todas as sessões ativas
        
        Returns:
            Lista de sessões
        """
        return [
            {
                "session_id": sid,
                "created_at": data["created_at"],
                "message_count": len(data["messages"])
            }
            for sid, data in self.active_sessions.items()
        ]
    
    def clear_session(self, session_id: str) -> bool:
        """
        Limpa uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            True se limpo, False se não encontrado
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"🗑️ Sessão {session_id} removida")
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna status do serviço
        
        Returns:
            Status do serviço
        """
        return {
            "service": "ClaudeService",
            "initialized": self.initialized,
            "agent_ready": self.agent.is_ready if self.agent else False,
            "active_sessions": len(self.active_sessions),
            "total_messages": sum(
                len(s["messages"]) 
                for s in self.active_sessions.values()
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Retorna informações do agente Claude
        
        Returns:
            Informações do agente
        """
        if self.agent:
            return self.agent.get_agent_card()
        return {
            "error": "Agente não disponível"
        }


# Singleton do serviço
_claude_service = None


def get_claude_service() -> ClaudeService:
    """
    Retorna instância singleton do Claude Service
    
    Returns:
        ClaudeService: Instância do serviço
    """
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service


# Exemplo de uso
if __name__ == "__main__":
    async def test_service():
        print("🧪 Testando Claude Service")
        print("-" * 50)
        
        service = get_claude_service()
        
        # Status
        print("\n📊 Status do serviço:")
        status = service.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Query simples
        print("\n💬 Teste de query:")
        response = await service.handle_query(
            "Explique o que é Python em uma frase",
            session_id="test-session"
        )
        if response.get("success"):
            print(f"  ✅ Resposta: {response['content'][:200]}...")
        else:
            print(f"  ❌ Erro: {response.get('error')}")
        
        # Geração de código
        print("\n🔧 Teste de geração de código:")
        response = await service.generate_code(
            "função para somar dois números"
        )
        if response.get("success"):
            print(f"  ✅ Código:")
            print(response.get("code", "")[:200])
        else:
            print(f"  ❌ Erro: {response.get('error')}")
        
        # Listar sessões
        print("\n📝 Sessões ativas:")
        sessions = service.list_sessions()
        for session in sessions:
            print(f"  - {session}")
        
        print("\n✅ Testes concluídos!")
    
    asyncio.run(test_service())
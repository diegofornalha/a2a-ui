"""
MCP Agent Manager - Integra agentes do A2A MCP com a UI
"""
import asyncio
import datetime
import json
import os
import uuid
from typing import Any

import httpx

from a2a.types import (
    AgentCard,
    Message,
    Task,
    Role,
)

from service.server.adk_host_manager import ADKHostManager
from service.types import Conversation, Event
from a2a_mcp.agents.orchestrator_agent import OrchestratorAgent
from a2a_mcp.agents.langgraph_planner_agent import LangraphPlannerAgent
from a2a_mcp.common import prompts


class MCPAgentManager(ADKHostManager):
    """Agent Manager que integra agentes do A2A MCP"""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_key: str = '',
        uses_vertex_ai: bool = False,
    ):
        super().__init__(http_client, api_key, uses_vertex_ai)
        self._mcp_agents = {}
        self._initialize_mcp_agents()

    def _initialize_mcp_agents(self):
        """Inicializa os agentes MCP disponíveis"""
        try:
            # Carregar agent cards do diretório
            agent_cards_dir = "agent_cards"
            if os.path.exists(agent_cards_dir):
                for filename in os.listdir(agent_cards_dir):
                    if filename.endswith('.json'):
                        with open(os.path.join(agent_cards_dir, filename), 'r') as f:
                            card_data = json.load(f)
                            agent_card = AgentCard(**card_data)
                            self._agents.append(agent_card)
                            
                            # Criar instância do agente baseado no nome
                            agent_instance = self._create_agent_instance(agent_card)
                            if agent_instance:
                                self._mcp_agents[agent_card.name] = agent_instance
        except Exception as e:
            print(f"Erro ao inicializar agentes MCP: {e}")

    def _create_agent_instance(self, agent_card: AgentCard):
        """Cria instância do agente baseado no agent card"""
        try:
            agent_name = agent_card.name
            
            if agent_name == 'Orchestrator Agent':
                return OrchestratorAgent()
            elif agent_name == 'Langraph Planner Agent':
                return LangraphPlannerAgent()
            return None
        except Exception as e:
            print(f"Erro ao criar instância do agente {agent_card.name}: {e}")
            return None

    async def process_message_with_mcp_agent(self, message: Message, agent_name: str):
        """Processa mensagem usando agente MCP específico"""
        if agent_name not in self._mcp_agents:
            raise ValueError(f"Agente {agent_name} não encontrado")
        
        agent = self._mcp_agents[agent_name]
        context_id = message.contextId or str(uuid.uuid4())
        task_id = message.taskId or str(uuid.uuid4())
        
        # Extrair query da mensagem
        query = ""
        for part in message.parts:
            if hasattr(part, 'text') and part.text:
                query += part.text
        
        try:
            # Usar stream do agente MCP
            async for response_chunk in agent.stream(query, context_id, task_id):
                # Criar evento para cada chunk de resposta
                response_message = Message(
                    messageId=str(uuid.uuid4()),
                    contextId=context_id,
                    taskId=task_id,
                    role=Role.assistant,
                    parts=[{
                        'kind': 'text',
                        'text': str(response_chunk.get('content', ''))
                    }]
                )
                
                self.add_event(
                    Event(
                        id=str(uuid.uuid4()),
                        actor=agent_name,
                        content=response_message,
                        timestamp=datetime.datetime.utcnow().timestamp(),
                    )
                )
                
                if response_chunk.get('is_task_complete', False):
                    break
                    
        except Exception as e:
            print(f"Erro ao processar mensagem com agente {agent_name}: {e}")
            # Criar mensagem de erro
            error_message = Message(
                messageId=str(uuid.uuid4()),
                contextId=context_id,
                taskId=task_id,
                role=Role.assistant,
                parts=[{
                    'kind': 'text', 
                    'text': f"Erro ao processar solicitação: {str(e)}"
                }]
            )
            
            self.add_event(
                Event(
                    id=str(uuid.uuid4()),
                    actor=agent_name,
                    content=error_message,
                    timestamp=datetime.datetime.utcnow().timestamp(),
                )
            )

    def get_available_mcp_agents(self) -> list[str]:
        """Retorna lista de agentes MCP disponíveis"""
        return list(self._mcp_agents.keys())

    def is_mcp_agent_query(self, message: Message) -> tuple[bool, str]:
        """Verifica se a mensagem é direcionada para um agente MCP específico"""
        query = ""
        for part in message.parts:
            if hasattr(part, 'text') and part.text:
                query += part.text.lower()
        
        # Palavras-chave para detectar tipo de agente necessário
        if any(word in query for word in ['trip', 'travel', 'plan', 'viagem']):
            return True, 'Orchestrator Agent'
        
        return False, ''

    async def process_message(self, message: Message):
        """Override do método process_message para incluir lógica MCP"""
        # Verificar se deve usar agente MCP
        is_mcp, agent_name = self.is_mcp_agent_query(message)
        
        if is_mcp and agent_name in self._mcp_agents:
            await self.process_message_with_mcp_agent(message, agent_name)
        else:
            # Usar processamento padrão
            await super().process_message(message) 
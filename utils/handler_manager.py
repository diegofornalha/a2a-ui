"""
Handler Manager para gerenciar handlers do Mesop e evitar handlers órfãos
quando agentes desconectam.
"""

import asyncio
import httpx
import logging
from typing import Dict, Set, Optional, Callable
from datetime import datetime, timedelta
import mesop as me

logger = logging.getLogger(__name__)


class HandlerManager:
    """Gerencia handlers do Mesop e detecta agentes desconectados."""
    
    def __init__(self, check_interval: int = 30):
        """
        Inicializa o gerenciador de handlers.
        
        Args:
            check_interval: Intervalo em segundos para verificar agentes (padrão: 30s)
        """
        self.agent_handlers: Dict[str, Set[str]] = {}  # agent_url -> set of handler_ids
        self.handler_agents: Dict[str, str] = {}  # handler_id -> agent_url
        self.agent_status: Dict[str, bool] = {}  # agent_url -> is_online
        self.check_interval = check_interval
        self._monitor_task: Optional[asyncio.Task] = None
        self._httpx_client: Optional[httpx.AsyncClient] = None
        
    async def start_monitoring(self):
        """Inicia o monitoramento de agentes."""
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._monitor_agents())
            logger.info("Handler monitoring started")
    
    async def stop_monitoring(self):
        """Para o monitoramento de agentes."""
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            logger.info("Handler monitoring stopped")
    
    def register_handler(self, handler_id: str, agent_url: str):
        """
        Registra um handler associado a um agente.
        
        Args:
            handler_id: ID do handler do Mesop
            agent_url: URL do agente (ex: http://localhost:12000)
        """
        if agent_url not in self.agent_handlers:
            self.agent_handlers[agent_url] = set()
        
        self.agent_handlers[agent_url].add(handler_id)
        self.handler_agents[handler_id] = agent_url
        self.agent_status[agent_url] = True  # Assume online inicialmente
        
        logger.debug(f"Handler {handler_id} registered for agent {agent_url}")
    
    def unregister_handler(self, handler_id: str):
        """
        Remove o registro de um handler.
        
        Args:
            handler_id: ID do handler do Mesop
        """
        if handler_id in self.handler_agents:
            agent_url = self.handler_agents[handler_id]
            if agent_url in self.agent_handlers:
                self.agent_handlers[agent_url].discard(handler_id)
                if not self.agent_handlers[agent_url]:
                    del self.agent_handlers[agent_url]
            del self.handler_agents[handler_id]
            logger.debug(f"Handler {handler_id} unregistered")
    
    async def check_agent_health(self, agent_url: str) -> bool:
        """
        Verifica se um agente está online.
        
        Args:
            agent_url: URL do agente
            
        Returns:
            True se o agente está online, False caso contrário
        """
        if not self._httpx_client:
            self._httpx_client = httpx.AsyncClient(timeout=5.0)
        
        health_endpoints = [
            "/.well-known/agent.json",
            "/health",
            "/info",
            "/"
        ]
        
        for endpoint in health_endpoints:
            try:
                response = await self._httpx_client.get(f"{agent_url}{endpoint}")
                if response.status_code == 200:
                    return True
            except (httpx.RequestError, httpx.TimeoutException):
                continue
        
        return False
    
    async def _monitor_agents(self):
        """Monitora continuamente o status dos agentes."""
        logger.info(f"Starting agent monitoring with {self.check_interval}s interval")
        
        while True:
            try:
                await self._check_all_agents()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in agent monitoring: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_all_agents(self):
        """Verifica o status de todos os agentes registrados."""
        for agent_url in list(self.agent_handlers.keys()):
            try:
                is_online = await self.check_agent_health(agent_url)
                
                if self.agent_status.get(agent_url, True) and not is_online:
                    # Agente ficou offline
                    logger.warning(f"Agent {agent_url} went offline")
                    await self._handle_agent_disconnection(agent_url)
                    
                elif not self.agent_status.get(agent_url, True) and is_online:
                    # Agente voltou online
                    logger.info(f"Agent {agent_url} is back online")
                    
                self.agent_status[agent_url] = is_online
                
            except Exception as e:
                logger.error(f"Error checking agent {agent_url}: {e}")
    
    async def _handle_agent_disconnection(self, agent_url: str):
        """
        Lida com a desconexão de um agente.
        
        Args:
            agent_url: URL do agente desconectado
        """
        # Obter todos os handlers do agente
        handler_ids = self.agent_handlers.get(agent_url, set()).copy()
        
        logger.info(f"Cleaning up {len(handler_ids)} handlers for disconnected agent {agent_url}")
        
        # Limpar handlers
        for handler_id in handler_ids:
            self.unregister_handler(handler_id)
        
        # Notificar a UI sobre a desconexão
        # Isso pode ser expandido para atualizar o estado da UI
        await self._notify_ui_agent_offline(agent_url)
    
    async def _notify_ui_agent_offline(self, agent_url: str):
        """
        Notifica a UI que um agente está offline.
        
        Args:
            agent_url: URL do agente offline
        """
        # Esta função pode ser expandida para atualizar o estado da UI
        # Por exemplo, marcando o agente como offline na lista de agentes
        logger.info(f"UI notified: Agent {agent_url} is offline")
    
    def is_handler_valid(self, handler_id: str) -> bool:
        """
        Verifica se um handler é válido (agente online).
        
        Args:
            handler_id: ID do handler
            
        Returns:
            True se o handler é válido, False caso contrário
        """
        if handler_id not in self.handler_agents:
            return True  # Handler não gerenciado, assume válido
        
        agent_url = self.handler_agents[handler_id]
        return self.agent_status.get(agent_url, True)
    
    def wrap_handler(self, handler_fn: Callable, agent_url: str) -> Callable:
        """
        Envolve um handler para adicionar verificação de agente online.
        
        Args:
            handler_fn: Função handler original
            agent_url: URL do agente
            
        Returns:
            Handler envolvido com verificação
        """
        def wrapped_handler(*args, **kwargs):
            if not self.agent_status.get(agent_url, True):
                logger.warning(f"Handler called for offline agent {agent_url}")
                # Pode retornar uma resposta de erro ou redirecionar
                return
            
            return handler_fn(*args, **kwargs)
        
        return wrapped_handler
    
    async def cleanup(self):
        """Limpa recursos do gerenciador."""
        await self.stop_monitoring()
        
        if self._httpx_client:
            await self._httpx_client.aclose()
            self._httpx_client = None


# Instância global do gerenciador
handler_manager = HandlerManager()


# Funções de conveniência
async def start_handler_monitoring():
    """Inicia o monitoramento de handlers."""
    await handler_manager.start_monitoring()


async def stop_handler_monitoring():
    """Para o monitoramento de handlers."""
    await handler_manager.stop_monitoring()


def register_agent_handler(handler_id: str, agent_url: str):
    """Registra um handler de agente."""
    handler_manager.register_handler(handler_id, agent_url)


def is_handler_valid(handler_id: str) -> bool:
    """Verifica se um handler é válido."""
    return handler_manager.is_handler_valid(handler_id)
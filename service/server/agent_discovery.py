"""
Agent Discovery Service - Auto-descoberta de agentes localhost

Este serviço automaticamente descobrir e registra agentes A2A rodando em localhost
nas portas padrão, mantendo-os sempre disponíveis na lista de Remote Agents.
"""

import asyncio
import json
import logging
from typing import List, Optional

import httpx
from a2a.types import AgentCard

logger = logging.getLogger(__name__)

# Portas comuns onde agentes A2A costumam rodar
DEFAULT_AGENT_PORTS = [
    9999,   # HelloWorld Agent (sempre ativo)
    10000,  # Porta padrão A2A
    10030,  # Marvin Agent
    10100,  # MCP Server
    11000,  # Agent genérico
    # Não incluir 12000 (UI) na descoberta para evitar auto-descoberta
]

# Endpoints possíveis para agent cards
AGENT_CARD_ENDPOINTS = [
    "/.well-known/agent.json",
    "/agent-card",
    "/info",
    "/health",
]


class AgentDiscovery:
    """Serviço de descoberta automática de agentes localhost"""
    
    def __init__(self, http_client: httpx.AsyncClient, timeout: float = 5.0):
        self.http_client = http_client
        self.timeout = timeout
        self.discovered_agents: List[AgentCard] = []
        
    async def discover_localhost_agents(self) -> List[AgentCard]:
        """Descobre todos os agentes rodando em localhost"""
        tasks = []
        
        for port in DEFAULT_AGENT_PORTS:
            for endpoint in AGENT_CARD_ENDPOINTS:
                url = f"http://localhost:{port}{endpoint}"
                task = asyncio.create_task(self._check_agent_endpoint(url, port))
                tasks.append(task)
        
        # Executar todas as verificações em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados válidos
        valid_agents = []
        for result in results:
            if isinstance(result, AgentCard):
                # Evitar duplicatas
                if not any(agent.url == result.url for agent in valid_agents):
                    valid_agents.append(result)
                    logger.info(f"Descoberto agente: {result.name} em {result.url}")
        
        self.discovered_agents = valid_agents
        return valid_agents
    
    async def _check_agent_endpoint(self, url: str, port: int) -> Optional[AgentCard]:
        """Verifica um endpoint específico para agent card"""
        try:
            response = await self.http_client.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verificar se é um agent card válido
                    if self._is_valid_agent_card(data):
                        agent_card = self._parse_agent_card(data, port)
                        return agent_card
                        
                except (json.JSONDecodeError, ValueError):
                    # Tentar parsing como health check
                    if "status" in response.text and "healthy" in response.text:
                        return self._create_basic_agent_card(port, "Health Check Agent")
                        
        except (httpx.RequestError, httpx.TimeoutException):
            # Agente não disponível nesta porta/endpoint
            pass
            
        return None
    
    def _is_valid_agent_card(self, data: dict) -> bool:
        """Verifica se os dados representam um agent card válido"""
        required_fields = ["name"]
        optional_fields = ["description", "url", "capabilities", "skills"]
        
        # Deve ter pelo menos o campo name
        if not isinstance(data, dict) or "name" not in data:
            return False
            
        # Verificar se tem estrutura de agent card
        has_agent_structure = any(field in data for field in optional_fields)
        
        return has_agent_structure or len(data) > 1
    
    def _parse_agent_card(self, data: dict, port: int) -> AgentCard:
        """Converte dados JSON em AgentCard"""
        base_url = f"http://localhost:{port}"
        
        # Usar URL fornecida ou construir baseada na porta
        agent_url = data.get("url", base_url)
        if not agent_url.startswith("http"):
            agent_url = f"{base_url}{agent_url if agent_url.startswith('/') else '/' + agent_url}"
        
        # Preparar provider
        provider_data = data.get("provider")
        if provider_data is None:
            provider_data = {
                "organization": "Auto-discovered",
                "url": agent_url
            }
        elif isinstance(provider_data, dict) and "url" not in provider_data:
            provider_data["url"] = agent_url
        
        agent_card = AgentCard(
            name=data.get("name", f"Agent Port {port}"),
            description=data.get("description", f"Agente descoberto automaticamente na porta {port}"),
            url=agent_url,
            provider=provider_data,
            version=data.get("version", "1.0.0"),
            documentationUrl=data.get("documentationUrl", ""),
            capabilities=data.get("capabilities", {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False
            }),
            authentication=data.get("authentication", {
                "credentials": None,
                "schemes": ["public"]
            }),
            defaultInputModes=data.get("defaultInputModes", ["text", "application/json"]),
            defaultOutputModes=data.get("defaultOutputModes", ["text", "application/json"]),
            skills=data.get("skills", [])
        )
        
        return agent_card
    
    def _create_basic_agent_card(self, port: int, name: str) -> AgentCard:
        """Cria um agent card básico para agentes que respondem mas não têm card completo"""
        base_url = f"http://localhost:{port}"
        return AgentCard(
            name=name,
            description=f"Agente básico descoberto na porta {port}",
            url=base_url,
            provider={
                "organization": "Auto-discovered",
                "url": base_url
            },
            version="1.0.0",
            documentationUrl="",
            capabilities={
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False
            },
            authentication={
                "credentials": None,
                "schemes": ["public"]
            },
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            skills=[]
        )
    
    async def get_agent_by_port(self, port: int) -> Optional[AgentCard]:
        """Busca um agente específico por porta"""
        for endpoint in AGENT_CARD_ENDPOINTS:
            url = f"http://localhost:{port}{endpoint}"
            agent = await self._check_agent_endpoint(url, port)
            if agent:
                return agent
        return None
    
    def get_discovered_agents(self) -> List[AgentCard]:
        """Retorna lista de agentes descobertos"""
        return self.discovered_agents.copy()
    
    async def is_agent_alive(self, agent_url: str) -> bool:
        """Verifica se um agente ainda está ativo"""
        try:
            # Tentar múltiplos endpoints para verificar se está vivo
            test_endpoints = ["/.well-known/agent.json", "/health", "/", "/agent-card"]
            
            for endpoint in test_endpoints:
                try:
                    test_url = agent_url.rstrip('/') + endpoint
                    response = await self.http_client.get(test_url, timeout=2.0)
                    if response.status_code in [200, 404]:  # 404 também indica que o servidor está respondendo
                        return True
                except:
                    continue
                    
        except Exception:
            pass
            
        return False


async def auto_discover_and_register(discovery: AgentDiscovery, manager) -> List[AgentCard]:
    """
    Função utilitária para descobrir e registrar agentes automaticamente
    
    Args:
        discovery: Instância do AgentDiscovery
        manager: ApplicationManager para registrar os agentes
        
    Returns:
        Lista de agentes descobertos e registrados
    """
    try:
        # Descobrir agentes
        agents = await discovery.discover_localhost_agents()
        
        # Registrar cada agente encontrado
        for agent in agents:
            try:
                manager.register_agent(agent.url)
                logger.info(f"Agente registrado automaticamente: {agent.name} ({agent.url})")
            except Exception as e:
                logger.warning(f"Falha ao registrar agente {agent.name}: {e}")
        
        return agents
        
    except Exception as e:
        logger.error(f"Erro na descoberta automática de agentes: {e}")
        return []


# Função de conveniência para usar fora do contexto de classe
async def discover_localhost_agents_simple(timeout: float = 5.0) -> List[dict]:
    """
    Função simples para descobrir agentes localhost sem dependências complexas
    
    Returns:
        Lista de dicionários com informações dos agentes descobertos
    """
    async with httpx.AsyncClient() as client:
        discovery = AgentDiscovery(client, timeout)
        agents = await discovery.discover_localhost_agents()
        
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "url": agent.url,
                "port": int(agent.url.split(":")[-1].split("/")[0]) if ":" in agent.url else None,
                "capabilities": agent.capabilities,
            }
            for agent in agents
        ]
"""
Página ultra-simplificada de agentes A2A - Zero estilos complexos
"""

import asyncio
import httpx
import json
import mesop as me
from typing import List, Any
from dataclasses import field


@me.stateclass
class SimpleAgentState:
    agents: List[dict[str, Any]] = field(default_factory=list)
    error_message: str = ""
    is_loading: bool = False


def ultra_simple_agents_page():
    """Página minimalista de agentes A2A"""
    state = me.state(SimpleAgentState)
    
    # Título simples
    me.text('🤖 Agentes A2A Descobertos', style=me.Style(font_size=24, font_weight='bold'))
    
    # Botões
    with me.box(style=me.Style(display='flex', gap=10)):
        me.button('🔄 Atualizar Agentes', on_click=refresh_agents)
        me.button('📋 Listar Agentes', on_click=list_server_agents)
    
    # Conteúdo
    if state.is_loading:
        me.text('🔍 Descobrindo agentes...')
    elif state.error_message:
        me.text(f'❌ {state.error_message}', style=me.Style(color='red'))
    elif state.agents:
        show_agents(state.agents)
    else:
        me.text('🔍 Nenhum agente encontrado. Clique em "Listar Agentes"')
    
    # Auto-listar na primeira carga
    if not state.agents and not state.is_loading and not state.error_message:
        list_server_agents(None)


def show_agents(agents: List[dict[str, Any]]):
    """Mostra lista de agentes de forma ultra-simples"""
    me.text(f'📡 {len(agents)} agente(s) encontrado(s)', style=me.Style(font_weight='bold'))
    
    for i, agent in enumerate(agents):
        show_agent_card(agent, i)


def show_agent_card(agent: dict[str, Any], index: int):
    """Card ultra-simples de agente"""
    name = agent.get('name', f'Agente {index + 1}')
    description = agent.get('description', 'Sem descrição')
    url = agent.get('url', '')
    port = agent.get('port', 'N/A')
    
    # Card minimalista
    me.text('─' * 50)  # Separador
    me.text(f'🤖 {name}', style=me.Style(font_size=18, font_weight='bold'))
    me.text(f'📝 {description}')
    me.text(f'🔗 {url}')
    me.text(f'🚪 Porta: {port}')
    me.text('🟢 Status: Online')
    
    # Botão de teste simples
    me.button(
        f'🔧 Testar {name}',
        key=f'test_{index}',
        on_click=lambda e, agent_url=url, agent_name=name: test_agent_simple(e, agent_url, agent_name)
    )


def list_server_agents(e):
    """Lista agentes registrados no servidor"""
    print("📋 LISTANDO AGENTES DO SERVIDOR...")
    state = me.state(SimpleAgentState)
    state.is_loading = True
    state.error_message = ""
    state.agents = []
    
    try:
        agents = asyncio.run(get_agents_from_server())
        print(f"📊 {len(agents)} agentes registrados no servidor")
        
        state.agents = agents
        state.is_loading = False
        
        for agent in agents:
            print(f"  - {agent.get('name')} ({agent.get('url')}) - Status: {agent.get('status', 'unknown')}")
            
    except Exception as ex:
        state.error_message = f"Erro: {str(ex)}"
        state.is_loading = False
        print(f"❌ Erro ao listar: {ex}")
        import traceback
        print(f"📜 Traceback: {traceback.format_exc()}")


def refresh_agents(e):
    """Atualiza descoberta de agentes via servidor"""
    print("🔄 ATUALIZANDO AGENTES...")
    state = me.state(SimpleAgentState)
    state.is_loading = True
    state.error_message = ""
    
    try:
        asyncio.run(refresh_agents_on_server())
        list_server_agents(e)  # Lista após atualizar
    except Exception as ex:
        state.error_message = f"Erro: {str(ex)}"
        state.is_loading = False
        print(f"❌ Erro ao atualizar: {ex}")


def discover_agents(e):
    """Descoberta ultra-simples de agentes"""
    print("🚀 INICIANDO DESCOBERTA DE AGENTES...")
    state = me.state(SimpleAgentState)
    state.is_loading = True
    state.error_message = ""
    state.agents = []
    
    try:
        print("🔍 Chamando ultra_simple_discovery()...")
        agents = asyncio.run(ultra_simple_discovery())
        print(f"📊 Resultado da descoberta: {len(agents)} agentes encontrados")
        
        state.agents = agents
        state.is_loading = False
        
        print(f"✅ Ultra-simple: Descobertos {len(agents)} agentes")
        for agent in agents:
            print(f"  - {agent.get('name')} ({agent.get('url')})")
            
    except Exception as ex:
        state.error_message = f"Erro: {str(ex)}"
        state.is_loading = False
        print(f"❌ Erro ultra-simple: {ex}")
        import traceback
        print(f"📜 Traceback completo: {traceback.format_exc()}")


async def ultra_simple_discovery() -> List[dict[str, Any]]:
    """Descoberta minimalista sem estilos complexos"""
    print("🔍 ULTRA_SIMPLE_DISCOVERY: Iniciando descoberta...")
    ports = [9999, 10000, 10030, 10100, 11000]
    agents = []
    
    print(f"🚪 Testando portas: {ports}")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for port in ports:
            try:
                # Tenta o endpoint principal
                url = f"http://localhost:{port}/.well-known/agent.json"
                print(f"📡 Testando URL: {url}")
                response = await client.get(url)
                print(f"📊 Porta {port} - Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"📋 Porta {port} - JSON recebido: {data.get('name', 'SEM_NOME')}")
                        if isinstance(data, dict) and 'name' in data:
                            agent_data = {
                                'name': data.get('name', f'Agent {port}'),
                                'description': data.get('description', f'Agente na porta {port}'),
                                'url': f"http://localhost:{port}",
                                'port': port,
                                'capabilities': data.get('capabilities', {}),
                                'version': data.get('version', '1.0.0')
                            }
                            agents.append(agent_data)
                            print(f"✅ Agente ADICIONADO na porta {port}: {data.get('name')}")
                        else:
                            print(f"⚠️ Porta {port}: JSON inválido ou sem 'name'")
                            
                    except json.JSONDecodeError as je:
                        print(f"⚠️ Porta {port}: Erro JSON - {je}")
                        
            except Exception as e:
                print(f"⚠️ Porta {port}: Erro de conexão - {e}")
                continue
    
    print(f"🎯 ULTRA_SIMPLE_DISCOVERY: Finalizando com {len(agents)} agentes")
    return agents


async def get_agents_from_server() -> List[dict[str, Any]]:
    """Obtém lista de agentes do servidor"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                "http://localhost:12000/agent/list",
                json={"jsonrpc": "2.0", "method": "list", "params": {}, "id": "1"}
            )
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', [])
                agents = []
                for item in result:
                    agent_card = item.get('agent_card', {})
                    agents.append({
                        'name': agent_card.get('name', 'Unknown'),
                        'description': agent_card.get('description', ''),
                        'url': agent_card.get('url', ''),
                        'status': item.get('status', 'unknown'),
                        'is_online': item.get('is_online', False),
                        'enabled': item.get('enabled', False),
                        'capabilities': agent_card.get('capabilities', {}),
                        'version': agent_card.get('version', '1.0.0')
                    })
                return agents
            return []
        except Exception as e:
            print(f"Erro ao listar agentes: {e}")
            raise


async def refresh_agents_on_server():
    """Solicita ao servidor para atualizar descoberta de agentes"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                "http://localhost:12000/agent/refresh",
                json={"jsonrpc": "2.0", "method": "refresh", "params": {}, "id": "1"}
            )
            if response.status_code == 200:
                print("✅ Atualização solicitada ao servidor")
            else:
                print(f"❌ Erro na atualização: {response.status_code}")
        except Exception as e:
            print(f"Erro ao atualizar: {e}")
            raise


async def test_agent_simple(e, agent_url: str, agent_name: str):
    """Teste ultra-simples de agente"""
    print(f"🔧 Testando: {agent_name} ({agent_url})")
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{agent_url}/.well-known/agent.json")
            
            if response.status_code == 200:
                print(f"✅ {agent_name}: Teste OK (Status: {response.status_code})")
                data = response.json()
                print(f"📋 Dados: {data.get('name')} v{data.get('version', 'N/A')}")
            else:
                print(f"⚠️ {agent_name}: Status {response.status_code}")
                
    except Exception as ex:
        print(f"❌ {agent_name}: Erro no teste - {ex}")


# Função para integração
def create_ultra_simple_agents_page():
    """Cria página ultra-simples"""
    return ultra_simple_agents_page
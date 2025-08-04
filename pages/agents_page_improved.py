"""
Página de agentes melhorada seguindo as melhores práticas do Mesop
"""

import asyncio
import httpx
import json
import mesop as me
from typing import List, Any
from datetime import datetime

from components.agent_card import agent_card, agent_list_header, action_buttons
from state.agent_state import AgentState, UIState, AgentInfoState


def agents_page_improved():
    """Página de agentes seguindo melhores práticas do Mesop"""
    agent_state = me.state(AgentState)
    ui_state = me.state(UIState)
    
    # Título da página
    me.text(
        '🤖 Agentes A2A Descobertos',
        style=me.Style(
            font_size=24,
            font_weight='bold',
            margin=me.Margin(bottom=20),
            color="#2c3e50"
        )
    )
    
    # Botões de ação usando componente reutilizável
    action_buttons(
        on_refresh=refresh_agents,
        on_list=list_server_agents
    )
    
    # Status e informações
    if agent_state.is_loading:
        with me.box(
            style=me.Style(
                display="flex",
                align_items="center",
                gap=12,
                margin=me.Margin(bottom=20)
            )
        ):
            me.progress_spinner()
            me.text('🔍 Descobrindo agentes...')
    
    elif agent_state.error_message:
        me.text(
            f'❌ {agent_state.error_message}',
            style=me.Style(color='red', margin=me.Margin(bottom=16))
        )
    
    elif agent_state.agents:
        # Usar componente reutilizável para cabeçalho
        agent_list_header(len(agent_state.agents))
        
        # Lista de agentes usando componente reutilizável
        for i, agent in enumerate(agent_state.agents):
            agent_card(
                agent=agent.__dict__,
                index=i,
                on_test=test_agent_improved
            )
        
        # Informações adicionais
        if agent_state.last_update:
            me.text(
                f'🕒 Última atualização: {agent_state.last_update}',
                style=me.Style(
                    font_size=12,
                    color="#95a5a6",
                    margin=me.Margin(top=16)
                )
            )
    
    else:
        me.text(
            '🔍 Nenhum agente encontrado. Clique em "Listar Agentes"',
            style=me.Style(
                color="#7f8c8d",
                font_size=16,
                margin=me.Margin(top=20)
            )
        )
    
    # Auto-listar na primeira carga
    if not agent_state.agents and not agent_state.is_loading and not agent_state.error_message:
        list_server_agents(None)


def list_server_agents(e):
    """Lista agentes registrados no servidor"""
    print("📋 LISTANDO AGENTES DO SERVIDOR...")
    agent_state = me.state(AgentState)
    agent_state.is_loading = True
    agent_state.error_message = ""
    
    try:
        agents = asyncio.run(get_agents_from_server())
        print(f"📊 {len(agents)} agentes registrados no servidor")
        
        # Converter para AgentInfoState
        agent_list = []
        for agent in agents:
            agent_info = AgentInfoState(
                name=agent.get('name', 'Unknown'),
                description=agent.get('description', ''),
                url=agent.get('url', ''),
                port=agent.get('port', 0),
                status=agent.get('status', 'unknown'),
                is_online=agent.get('is_online', False),
                enabled=agent.get('enabled', False),
                capabilities=agent.get('capabilities', {}),
                version=agent.get('version', '1.0.0')
            )
            agent_list.append(agent_info)
        
        agent_state.agents = agent_list
        agent_state.is_loading = False
        agent_state.last_update = datetime.now().strftime("%H:%M:%S")
        agent_state.total_discovered = len(agent_list)
        
    except Exception as ex:
        agent_state.error_message = f"Erro: {str(ex)}"
        agent_state.is_loading = False
        print(f"❌ Erro ao listar: {ex}")


def refresh_agents(e):
    """Atualiza descoberta de agentes via servidor"""
    print("🔄 ATUALIZANDO AGENTES...")
    agent_state = me.state(AgentState)
    agent_state.is_loading = True
    agent_state.error_message = ""
    agent_state.refresh_count += 1
    
    try:
        asyncio.run(refresh_agents_on_server())
        # Toast removido - não existe no Mesop
        print("✅ Agentes atualizados com sucesso!")
        list_server_agents(e)  # Lista após atualizar
    except Exception as ex:
        agent_state.error_message = f"Erro: {str(ex)}"
        agent_state.is_loading = False
        # Toast removido - não existe no Mesop
        print(f"❌ Erro ao atualizar: {ex}")


def test_agent_improved(e: me.ClickEvent, agent_url: str, agent_name: str):
    """Teste melhorado de agente com feedback"""
    print(f"🔧 Testando: {agent_name} ({agent_url})")
    
    # Toast removido - não existe no Mesop
    print(f"🔧 Testando {agent_name}...")
    
    asyncio.run(test_agent_async(agent_url, agent_name))


async def test_agent_async(agent_url: str, agent_name: str):
    """Teste assíncrono de agente"""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{agent_url}/.well-known/agent.json")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {agent_name} está respondendo!")
                print(f"📋 Versão: {data.get('version', 'N/A')}")
                # Toast removido - não existe no Mesop
            else:
                print(f"⚠️ {agent_name} retornou status: {response.status_code}")
                # Toast removido - não existe no Mesop
                
    except Exception as e:
        print(f"❌ Erro ao testar {agent_name}: {e}")
        # Toast removido - não existe no Mesop


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
                        'version': agent_card.get('version', '1.0.0'),
                        'port': int(agent_card.get('url', '').split(':')[-1].split('/')[0]) if ':' in agent_card.get('url', '') else 0
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
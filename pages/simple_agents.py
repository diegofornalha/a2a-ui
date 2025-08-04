"""
Página simplificada de agentes - SPARC Implementation
Specification: Interface limpa e funcional para visualizar agentes A2A
"""

import asyncio
import httpx
import mesop as me
from typing import List, Dict, Any
from dataclasses import field

from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from service.server.agent_discovery import AgentDiscovery, discover_localhost_agents_simple


@me.stateclass
class SimpleAgentPageState:
    agents: List[Dict[str, Any]] = field(default_factory=list)
    error_message: str = ""
    is_loading: bool = False


def simple_agents_page():
    """Página principal de agentes simplificada"""
    state = me.state(SimpleAgentPageState)
    
    with page_scaffold():
        with page_frame():
            with header('🤖 Agentes A2A', 'smart_toy'):
                me.button(
                    '🔄 Atualizar',
                    on_click=refresh_agents,
                    style=me.Style(
                        background='#2196F3',
                        color='white',
                        border_radius=20,
                        padding=me.Padding.all(8)
                    )
                )
            
            if state.is_loading:
                me.text('🔄 Carregando agentes...', style=me.Style(text_align='center', padding=me.Padding.all(20)))
            elif state.error_message:
                me.text(f'❌ {state.error_message}', style=me.Style(color='red', text_align='center'))
            else:
                render_agents_list(state.agents)
    
    # Auto-carregar agentes na primeira visita
    if not state.agents and not state.is_loading:
        refresh_agents(None)


def render_agents_list(agents: List[Dict[str, Any]]):
    """Renderiza lista de agentes de forma simples"""
    if not agents:
        with me.box(style=me.Style(text_align='center', padding=me.Padding.all(40))):
            me.text(
                '🔍 Nenhum agente encontrado',
                style=me.Style(font_size=20, color='#666')
            )
            me.text(
                'Certifique-se de que há agentes rodando nas portas padrão (9999, 10000, 10030, etc.)',
                style=me.Style(color='#888', margin=me.Margin(top=8))
            )
        return
    
    # Título da seção
    me.text(
        f'📡 {len(agents)} agente(s) encontrado(s)',
        style=me.Style(
            font_size=24,
            font_weight='bold',
            margin=me.Margin(bottom=20),
            color='#2196F3'
        )
    )
    
    # Grid de agentes
    for i, agent in enumerate(agents):
        render_simple_agent_card(agent, i)


def render_simple_agent_card(agent: Dict[str, Any], index: int):
    """Renderiza card simples de agente"""
    name = agent.get('name', f'Agent {index + 1}')
    description = agent.get('description', 'Sem descrição')
    url = agent.get('url', '')
    capabilities = agent.get('capabilities', {})
    
    # Determinar cor do status
    is_online = True  # Por enquanto, assume online se foi descoberto
    status_color = '#4CAF50' if is_online else '#F44336'
    status_text = '🟢 Online' if is_online else '🔴 Offline'
    
    with me.box(
        style=me.Style(
            background='white',
            border_radius=12,
            box_shadow='0 4px 8px rgba(0,0,0,0.1)',
            padding=me.Padding.all(20),
            margin=me.Margin(bottom=16),
            border=f'2px solid {status_color}'
        )
    ):
        # Cabeçalho do card
        with me.box(style=me.Style(display='flex', justify_content='space-between', align_items='flex-start')):
            # Informações principais
            with me.box(style=me.Style(flex_grow=1)):
                me.text(
                    name,
                    style=me.Style(font_size=20, font_weight='bold', color='#333')
                )
                me.text(
                    description,
                    style=me.Style(color='#666', margin=me.Margin(top=4, bottom=12))
                )
                me.text(
                    f'🔗 {url}',
                    style=me.Style(color='#888', font_size=14)
                )
            
            # Status
            with me.box():
                me.text(
                    status_text,
                    style=me.Style(
                        color=status_color,
                        font_weight='bold',
                        font_size=16
                    )
                )
        
        # Capacidades
        if capabilities:
            with me.box(style=me.Style(margin=me.Margin(top=16))):
                me.text('⚡ Capacidades:', style=me.Style(font_weight='bold', color='#333'))
                
                capabilities_text = []
                if capabilities.get('streaming'):
                    capabilities_text.append('📡 Streaming')
                if capabilities.get('pushNotifications'):
                    capabilities_text.append('🔔 Push Notifications')
                if capabilities.get('stateTransitionHistory'):
                    capabilities_text.append('📈 State History')
                
                if capabilities_text:
                    me.text(
                        ' • '.join(capabilities_text),
                        style=me.Style(color='#666', margin=me.Margin(top=4))
                    )
        
        # Botão de teste
        with me.box(style=me.Style(margin=me.Margin(top=16), text_align='center')):
            me.button(
                '🔧 Testar Conexão',
                key=f'test_{index}',
                on_click=lambda e, agent_url=url: test_agent_connection(e, agent_url),
                style=me.Style(
                    background='#FF9800',
                    color='white',
                    border_radius=8,
                    padding=me.Padding.symmetric(horizontal=16, vertical=8)
                )
            )


def refresh_agents(e):
    """Atualiza lista de agentes"""
    state = me.state(SimpleAgentPageState)
    state.is_loading = True
    state.error_message = ""
    
    try:
        # Usar função de descoberta simplificada
        agents = asyncio.run(discover_localhost_agents_simple())
        state.agents = agents
        state.is_loading = False
        
        if agents:
            print(f"✅ {len(agents)} agentes descobertos")
        else:
            print("ℹ️ Nenhum agente encontrado")
            
    except Exception as ex:
        state.error_message = f"Erro ao buscar agentes: {str(ex)}"
        state.is_loading = False
        print(f"❌ Erro na descoberta: {ex}")


async def test_agent_connection(e, agent_url: str):
    """Testa conectividade com um agente específico"""
    print(f"🔧 Testando conexão com: {agent_url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{agent_url}/.well-known/agent.json", timeout=3.0)
            if response.status_code == 200:
                print(f"✅ Agente {agent_url} respondeu com sucesso")
                data = response.json()
                print(f"📋 Nome: {data.get('name', 'Unknown')}")
            else:
                print(f"⚠️ Agente {agent_url} respondeu com status {response.status_code}")
    except Exception as ex:
        print(f"❌ Erro ao testar {agent_url}: {ex}")


# Função para uso na rota principal
def create_simple_agents_page():
    """Cria página de agentes simplificada"""
    return simple_agents_page
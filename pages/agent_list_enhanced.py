import asyncio

import mesop as me

from components.dialog import dialog, dialog_actions
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from state.agent_state import AgentState
from state.host_agent_service import AddRemoteAgent, ListRemoteAgents, ToggleRemoteAgent, RemoveRemoteAgent
from state.state import AppState
from utils.agent_card import get_agent_card


def agent_list_enhanced_page(app_state: AppState):
    """Enhanced Agents List Page with toggle functionality"""
    state = me.state(AgentState)
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Agentes Remotos', 'smart_toy'):
                pass
                
            agents = asyncio.run(ListRemoteAgents())
            enhanced_agents_list(agents, state)
            
            # Dialog para adicionar agente
            with dialog(state.agent_dialog_open):
                with me.box(
                    style=me.Style(
                        display='flex', flex_direction='column', gap=12
                    )
                ):
                    me.input(
                        label='Agent Address',
                        on_blur=set_agent_address,
                        placeholder='https://remote-server.com:10000',
                    )
                    
                    if state.error != '':
                        me.text(state.error, style=me.Style(color='red'))
                    if state.agent_name != '':
                        me.text(f'Agent Name: {state.agent_name}')
                    if state.agent_description:
                        me.text(f'Agent Description: {state.agent_description}')
                    if state.agent_framework_type:
                        me.text(
                            f'Agent Framework Type: {state.agent_framework_type}'
                        )
                    
                with dialog_actions():
                    if not state.agent_name:
                        me.button('Testar', on_click=load_agent_info)
                    elif not state.error:
                        me.button('Adicionar', on_click=save_agent)
                    me.button('Cancelar', on_click=cancel_agent_dialog)


def enhanced_agents_list(agents, state):
    """Lista aprimorada de agentes com controles de toggle"""
    if not agents:
        with me.box(style=me.Style(text_align='center', padding=me.Padding.all(32))):
            me.text(
                '🤖 Nenhum agente registrado por enquanto',
                style=me.Style(font_size=18, color='#666')
            )
            me.button(
                '+ Adicionar Agente Remoto',
                on_click=open_agent_dialog,
                style=me.Style(
                    margin=me.Margin(top=16),
                    background='#2196F3',
                    color='white',
                    border_radius=20,
                    padding=me.Padding.symmetric(horizontal=24, vertical=12)
                )
            )
        return
    
    # Separar agentes por tipo
    local_agents = [a for a in agents if getattr(a, 'is_local', True)]
    remote_agents = [a for a in agents if not getattr(a, 'is_local', True)]
    
    # Seção de agentes locais
    if local_agents:
        me.text(
            '🏠 Agentes Locais',
            style=me.Style(font_size=20, font_weight='bold', margin=me.Margin(bottom=16))
        )
        
        for agent_info in local_agents:
            agent_card = getattr(agent_info, 'agent_card', agent_info)
            render_local_agent_card(agent_info, agent_card)
    
    # Seção de agentes remotos
    me.text(
        '🌐 Agentes Remotos',
        style=me.Style(
            font_size=20, 
            font_weight='bold', 
            margin=me.Margin(top=32, bottom=16)
        )
    )
    
    if remote_agents:
        for agent_info in remote_agents:
            agent_card = getattr(agent_info, 'agent_card', agent_info)
            render_remote_agent_card(agent_info, agent_card)
    else:
        with me.box(style=me.Style(text_align='center', padding=me.Padding.all(16))):
            me.text('Nenhum agente remoto adicionado', style=me.Style(color='#888'))
    
    # Botão para adicionar agente remoto
    with me.box(style=me.Style(text_align='center', margin=me.Margin(top=16))):
        me.button(
            '+ Adicionar Agente Remoto',
            on_click=open_agent_dialog,
            style=me.Style(
                background='#2196F3',
                color='white',
                border_radius=20,
                padding=me.Padding.symmetric(horizontal=24, vertical=12)
            )
        )


def render_local_agent_card(agent_info, agent_card):
    """Renderiza card de agente local com toggle"""
    is_enabled = getattr(agent_info, 'enabled', True)
    is_online = getattr(agent_info, 'is_online', True)
    
    # Determinar cor do status
    status_color = '#4CAF50' if (is_enabled and is_online) else '#FF9800' if is_online else '#F44336'
    status_text = '🟢 Ativo' if (is_enabled and is_online) else '🟡 Desabilitado' if is_online else '🔴 Offline'
    
    with me.box(
        style=me.Style(
            background='white',
            border_radius=8,
            box_shadow='0 2px 4px rgba(0,0,0,0.1)',
            padding=me.Padding.all(16),
            margin=me.Margin(bottom=12),
            border=f'2px solid {status_color}'
        )
    ):
        with me.box(style=me.Style(display='flex', justify_content='space-between', align_items='center')):
            # Informações do agente
            with me.box(style=me.Style(flex_grow=1)):
                me.text(
                    agent_card.name if hasattr(agent_card, 'name') else 'Unknown Agent',
                    style=me.Style(font_size=18, font_weight='bold')
                )
                me.text(
                    agent_card.description if hasattr(agent_card, 'description') else '',
                    style=me.Style(color='#666', margin=me.Margin(bottom=8))
                )
                me.text(
                    agent_card.url if hasattr(agent_card, 'url') else '',
                    style=me.Style(color='#888', font_size=14)
                )
                me.text(status_text, style=me.Style(color=status_color, font_weight='bold'))
            
            # Controles
            with me.box(style=me.Style(display='flex', flex_direction='column', gap=8)):
                # Toggle switch
                toggle_text = 'Desabilitar' if is_enabled else 'Habilitar'
                toggle_color = '#FF9800' if is_enabled else '#4CAF50'
                
                me.button(
                    toggle_text,
                    key=f'toggle_{agent_card.url}',
                    on_click=lambda e, url=agent_card.url, enabled=not is_enabled: toggle_agent(e, url, enabled),
                    style=me.Style(
                        background=toggle_color,
                        color='white',
                        border_radius=4,
                        padding=me.Padding.all(8),
                        font_size=12
                    )
                )


def render_remote_agent_card(agent_info, agent_card):
    """Renderiza card de agente remoto com botão de remover"""
    is_online = getattr(agent_info, 'is_online', True)
    
    status_color = '#4CAF50' if is_online else '#F44336'
    status_text = '🟢 Online' if is_online else '🔴 Offline'
    
    with me.box(
        style=me.Style(
            background='white',
            border_radius=8,
            box_shadow='0 2px 4px rgba(0,0,0,0.1)',
            padding=me.Padding.all(16),
            margin=me.Margin(bottom=12),
            border=f'2px solid {status_color}'
        )
    ):
        with me.box(style=me.Style(display='flex', justify_content='space-between', align_items='center')):
            # Informações do agente
            with me.box(style=me.Style(flex_grow=1)):
                me.text(
                    agent_card.name if hasattr(agent_card, 'name') else 'Unknown Agent',
                    style=me.Style(font_size=18, font_weight='bold')
                )
                me.text(
                    agent_card.description if hasattr(agent_card, 'description') else '',
                    style=me.Style(color='#666', margin=me.Margin(bottom=8))
                )
                me.text(
                    agent_card.url if hasattr(agent_card, 'url') else '',
                    style=me.Style(color='#888', font_size=14)
                )
                me.text(status_text, style=me.Style(color=status_color, font_weight='bold'))
            
            # Botão remover
            with me.box():
                me.button(
                    '🗑️ Remover',
                    key=f'remove_{agent_card.url}',
                    on_click=lambda e, url=agent_card.url: remove_remote_agent(e, url),
                    style=me.Style(
                        background='#F44336',
                        color='white',
                        border_radius=4,
                        padding=me.Padding.all(8),
                        font_size=12
                    )
                )


# Event handlers
def open_agent_dialog(e: me.ClickEvent):
    state = me.state(AgentState)
    state.agent_dialog_open = True
    state.agent_address = ''
    state.agent_name = ''
    state.error = ''


def set_agent_address(e: me.InputBlurEvent):
    state = me.state(AgentState)
    state.agent_address = e.value


def load_agent_info(e: me.ClickEvent):
    state = me.state(AgentState)
    try:
        state.error = None
        agent_card_response = get_agent_card(state.agent_address)
        state.agent_name = agent_card_response.name
        state.agent_description = agent_card_response.description
        state.agent_framework_type = (
            agent_card_response.provider.organization
            if agent_card_response.provider
            else ''
        )
    except Exception as e:
        print(e)
        state.agent_name = None
        state.error = f'Cannot connect to agent at {state.agent_address}'


async def save_agent(e: me.ClickEvent):
    state = me.state(AgentState)
    await AddRemoteAgent(state.agent_address)
    state.agent_address = ''
    state.agent_name = ''
    state.agent_description = ''
    state.agent_dialog_open = False


def cancel_agent_dialog(e: me.ClickEvent):
    state = me.state(AgentState)
    state.agent_dialog_open = False


async def toggle_agent(e: me.ClickEvent, agent_url: str, enabled: bool):
    """Toggle agent enabled/disabled status"""
    try:
        result = await ToggleRemoteAgent(agent_url, enabled)
        if result.get('result', {}).get('success', False):
            print(f"✅ Agent {'enabled' if enabled else 'disabled'}: {agent_url}")
        else:
            print(f"❌ Failed to toggle agent: {result.get('result', {}).get('message', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error toggling agent: {e}")


async def remove_remote_agent(e: me.ClickEvent, agent_url: str):
    """Remove a remote agent"""
    try:
        await RemoveRemoteAgent(agent_url)
        print(f"🗑️ Remote agent removed: {agent_url}")
    except Exception as e:
        print(f"❌ Error removing agent: {e}")



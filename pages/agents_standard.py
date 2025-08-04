"""
Página de agentes seguindo o padrão correto do a2a-samples/demo/ui
"""

import asyncio
import mesop as me
import pandas as pd

from components.agent_list_table import agents_list_table
from components.dialog import dialog, dialog_actions
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from state.agent_state import AgentState
from state.host_agent_service import AddRemoteAgent, ListRemoteAgents
from state.state import AppState
from utils.agent_card import get_agent_card


def agent_list_page_standard(app_state: AppState):
    """Agents List Page - Padrão correto"""
    state = me.state(AgentState)
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Remote Agents', 'smart_toy'):
                # Botão para adicionar agente manualmente
                with me.box(style=me.Style(display='flex', justify_content='flex-end')):
                    me.button(
                        '➕ Adicionar Agente Manualmente',
                        on_click=open_add_agent_dialog,
                        style=me.Style(
                            background="#27ae60",
                            color="white",
                            border_radius=6,
                            padding=me.Padding.all(8)
                        )
                    )
            try:
                agents = asyncio.run(ListRemoteAgents())
                print(f"Debug - Agents returned: {agents}")
                print(f"Debug - Type of agents: {type(agents)}")
                if agents:
                    print(f"Debug - First agent type: {type(agents[0])}")
                # Se não houver agentes ou estiverem em formato incorreto, usar lista vazia
                if not agents or not isinstance(agents, list):
                    agents = []
                agents_list_table(agents)
            except Exception as e:
                print(f"Erro ao listar agentes: {e}")
                import traceback
                traceback.print_exc()
                # Em caso de erro, mostrar lista vazia
                agents_list_table([])
            with dialog(state.agent_dialog_open):
                # Título do dialog
                me.text(
                    '🤖 Adicionar Agente Manualmente',
                    style=me.Style(
                        font_size=20,
                        font_weight='bold',
                        margin=me.Margin(bottom=16)
                    )
                )
                
                with me.box(
                    style=me.Style(
                        display='flex', flex_direction='column', gap=12
                    )
                ):
                    me.text(
                        'Digite o endereço do agente (hostname:porta):',
                        style=me.Style(font_size=14, color='#666')
                    )
                    me.input(
                        label='Agent Address',
                        on_blur=set_agent_address,
                        placeholder='localhost:10000',
                    )
                    me.text(
                        'Exemplos: localhost:9999, localhost:10030, 192.168.1.100:8080',
                        style=me.Style(font_size=12, color='#888', font_style='italic')
                    )
                    input_modes_string = ', '.join(state.input_modes)
                    output_modes_string = ', '.join(state.output_modes)

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
                    if state.input_modes:
                        me.text(f'Input Modes: {input_modes_string}')
                    if state.output_modes:
                        me.text(f'Output Modes: {output_modes_string}')

                    if state.agent_name:
                        me.text(
                            f'Streaming Supported: {state.stream_supported}'
                        )
                        me.text(
                            f'Push Notifications Supported: {state.push_notifications_supported}'
                        )
                with dialog_actions():
                    if not state.agent_name:
                        me.button('Read', on_click=load_agent_info)
                    elif not state.error:
                        me.button('Save', on_click=save_agent)
                    me.button('Cancel', on_click=cancel_agent_dialog)


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
        state.input_modes = agent_card_response.defaultInputModes
        state.output_modes = agent_card_response.defaultOutputModes
        state.stream_supported = agent_card_response.capabilities.streaming
        state.push_notifications_supported = (
            agent_card_response.capabilities.pushNotifications
        )
    except Exception as e:
        print(e)
        state.agent_name = None
        state.error = f'Cannot connect to agent as {state.agent_address}'


def cancel_agent_dialog(e: me.ClickEvent):
    state = me.state(AgentState)
    state.agent_dialog_open = False
    # Limpar campos
    state.agent_address = ''
    state.agent_name = ''
    state.agent_description = ''
    state.error = ''


def open_add_agent_dialog(e: me.ClickEvent):
    """Abre o dialog para adicionar agente manualmente"""
    state = me.state(AgentState)
    state.agent_dialog_open = True
    # Limpar campos anteriores
    state.agent_address = ''
    state.agent_name = ''
    state.agent_description = ''
    state.error = ''


async def save_agent(e: me.ClickEvent):
    state = me.state(AgentState)
    await AddRemoteAgent(state.agent_address)
    state.agent_address = ''
    state.agent_name = ''
    state.agent_description = ''
    state.agent_dialog_open = False
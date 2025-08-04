import asyncio
import mesop as me
import pandas as pd

from a2a.types import AgentCard
from state.agent_state import AgentState
from state.host_agent_service import RemoveRemoteAgent


@me.component
def agents_list(
    agents: list[AgentCard],
):
    """Agents list component."""
    with me.box(
        style=me.Style(
            display='flex',
            justify_content='space-between',
            flex_direction='column',
        )
    ):
        # Lista de agentes com botões de remoção
        if not agents:
            with me.box(
                style=me.Style(
                    display='flex',
                    justify_content='center',
                    align_items='center',
                    flex_direction='column',
                    min_height='200px'
                )
            ):
                me.text(
                    "🎉 Nenhum agente registrado por enquanto.",
                    style=me.Style(
                        text_align='center',
                        font_size=16,
                        color='#666',
                        margin=me.Margin.all(32)
                    )
                )
        else:
            for agent in agents:
                with me.box(
                    style=me.Style(
                        border=me.Border.all(me.BorderSide(color="#e0e0e0", width=1, style="solid")),
                        border_radius=8,
                        margin=me.Margin(bottom=10),
                        padding=me.Padding.all(16),
                        display='flex',
                        justify_content='space-between',
                        align_items='center',
                    )
                ):
                    # Informações do agente
                    with me.box(style=me.Style(flex_grow=1)):
                        me.text(
                            agent.name,
                            style=me.Style(font_weight="bold", font_size=16, margin=me.Margin(bottom=4))
                        )
                        me.text(
                            agent.description,
                            style=me.Style(color="#666", margin=me.Margin(bottom=4))
                        )
                        me.text(
                            f"URL: {agent.url}",
                            style=me.Style(font_size=12, color="#888")
                        )
                        if agent.provider and agent.provider.organization:
                            me.text(
                                f"Organização: {agent.provider.organization}",
                                style=me.Style(font_size=12, color="#888")
                            )
                        me.text(
                            f"Skills: {len(agent.skills)} | Streaming: {'Sim' if agent.capabilities.streaming else 'Não'}",
                            style=me.Style(font_size=12, color="#888")
                        )
                    
                    # Botão de remoção
                    with me.content_button(
                        type='flat',
                        on_click=lambda e, url=agent.url: remove_agent(e, url),
                        key=f'remove_agent_{agent.url}',
                        style=me.Style(
                            color='red',
                            padding=me.Padding.all(8),
                        ),
                    ):
                        me.icon(icon='delete')
        
        # Botão 
        with me.content_button(
            type='raised',
            on_click=add_agent,
            key='new_agent',
            style=me.Style(
                display='flex',
                flex_direction='row',
                gap=5,
                align_items='center',
                margin=me.Margin(top=10),
            ),
        ):
            me.icon(icon='add')


def add_agent(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Import agent button handler."""
    state = me.state(AgentState)
    state.agent_dialog_open = True


def remove_agent(e: me.ClickEvent, agent_url: str):  # pylint: disable=unused-argument
    """Remove agent button handler."""
    try:
        asyncio.run(RemoveRemoteAgent(agent_url))
        # Força atualização da página recarregando
        # A UI será atualizada automaticamente na próxima busca
    except Exception as ex:
        print(f"Erro ao remover agente {agent_url}: {ex}")

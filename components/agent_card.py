"""
Componente reutilizável para cards de agentes A2A
Seguindo as melhores práticas do Mesop
"""

import mesop as me
from typing import Any, Callable


@me.component
def agent_card(
    agent: dict[str, Any],
    index: int,
    on_test: Callable[[me.ClickEvent, str, str], None]
):
    """Card reutilizável de agente seguindo padrões Mesop"""
    name = agent.get('name', f'Agente {index + 1}')
    description = agent.get('description', 'Sem descrição')
    url = agent.get('url', '')
    port = agent.get('port', 'N/A')
    
    # Card com estilo consistente
    with me.box(
        style=me.Style(
            border=me.Border.all(me.BorderSide(color="#e0e0e0", width=1)),
            border_radius=8,
            padding=me.Padding.all(16),
            margin=me.Margin(bottom=12),
            background="white",
            box_shadow="0 2px 4px rgba(0,0,0,0.1)"
        )
    ):
        # Cabeçalho do card
        with me.box(
            style=me.Style(
                display="flex",
                justify_content="space_between",
                align_items="center",
                margin=me.Margin(bottom=8)
            )
        ):
            me.text(
                f'🤖 {name}',
                style=me.Style(
                    font_size=18,
                    font_weight="bold",
                    color="#2c3e50"
                )
            )
            me.text(
                '🟢 Online',
                style=me.Style(
                    color="#27ae60",
                    font_size=12,
                    font_weight="500"
                )
            )
        
        # Informações do agente
        me.text(
            f'📝 {description}',
            style=me.Style(
                color="#7f8c8d",
                margin=me.Margin(bottom=8)
            )
        )
        
        with me.box(
            style=me.Style(
                display="flex",
                gap=16,
                margin=me.Margin(bottom=12)
            )
        ):
            me.text(
                f'🔗 {url}',
                style=me.Style(font_size=12, color="#3498db")
            )
            me.text(
                f'🚪 Porta: {port}',
                style=me.Style(font_size=12, color="#95a5a6")
            )
        
        # Botão de teste reutilizável
        me.button(
            f'🔧 Testar {name}',
            key=f'test_{index}',
            on_click=lambda e, url=url, name=name: on_test(e, url, name),
            style=me.Style(
                background="#3498db",
                color="white",
                padding=me.Padding.all(8),
                border_radius=4,
                font_weight="500"
            )
        )


@me.component
def agent_list_header(count: int):
    """Cabeçalho reutilizável para lista de agentes"""
    with me.box(
        style=me.Style(
            margin=me.Margin(bottom=16),
            padding=me.Padding(bottom=8),
            border=me.Border(bottom=me.BorderSide(color="#e0e0e0", width=1))
        )
    ):
        me.text(
            f'📡 {count} agente(s) encontrado(s)',
            style=me.Style(
                font_weight='bold',
                font_size=16,
                color="#34495e"
            )
        )


@me.component  
def action_buttons(on_refresh: Callable, on_list: Callable):
    """Botões de ação reutilizáveis"""
    with me.box(
        style=me.Style(
            display='flex',
            gap=12,
            margin=me.Margin(bottom=20),
            align_items="center"
        )
    ):
        me.button(
            '🔄 Atualizar Agentes',
            on_click=on_refresh,
            style=me.Style(
                background="#2ecc71",
                color="white",
                padding=me.Padding.all(10),
                border_radius=6,
                font_weight="500"
            )
        )
        me.button(
            '📋 Listar Agentes',
            on_click=on_list,
            style=me.Style(
                background="#3498db", 
                color="white",
                padding=me.Padding.all(10),
                border_radius=6,
                font_weight="500"
            )
        )
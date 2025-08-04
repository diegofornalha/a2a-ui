"""
Página de agentes ultra-simples seguindo as melhores práticas do Mesop
"""

import mesop as me
from dataclasses import field


@me.stateclass
class SimpleAgentState:
    """Estado ultra-simples para debugging"""
    message: str = "Página carregada com sucesso!"
    agents_count: int = 0
    is_loading: bool = False


@me.page(path="/agents")
def agents_page_simple():
    """Página de agentes ultra-simples"""
    state = me.state(SimpleAgentState)
    
    # Título
    me.text(
        '🤖 Agentes A2A - Versão Simples',
        style=me.Style(
            font_size=24,
            font_weight='bold',
            margin=me.Margin(bottom=20),
            color="#2c3e50"
        )
    )
    
    # Status
    me.text(
        f'✅ {state.message}',
        style=me.Style(
            color="#27ae60",
            font_size=16,
            margin=me.Margin(bottom=20)
        )
    )
    
    # Botões
    with me.box(
        style=me.Style(
            display="flex",
            gap=12,
            margin=me.Margin(bottom=20)
        )
    ):
        me.button(
            '🔄 Teste Simples',
            on_click=test_simple,
            style=me.Style(
                background="#3498db",
                color="white",
                border_radius=6,
                padding=me.Padding.all(8)
            )
        )
        
        me.button(
            '📊 Contar Agentes',
            on_click=count_agents,
            style=me.Style(
                background="#f39c12",
                color="white",
                border_radius=6,
                padding=me.Padding.all(8)
            )
        )
        
        me.button(
            '🐛 Debug Info',
            on_click=debug_info,
            style=me.Style(
                background="#e74c3c",
                color="white",
                border_radius=6,
                padding=me.Padding.all(8)
            )
        )
    
    # Informações
    if state.is_loading:
        me.text('⏳ Carregando...')
    else:
        me.text(f'📡 Agentes encontrados: {state.agents_count}')
    
    # Lista simples
    if state.agents_count > 0:
        me.text('─' * 50)
        me.text('🤖 HelloWorld Agent')
        me.text('🔗 http://localhost:9999')
        me.text('🟢 Status: Online')
        me.text('─' * 50)
        me.text('🤖 Marvin Agent')
        me.text('🔗 http://localhost:10030')
        me.text('🟢 Status: Online')


def test_simple(e):
    """Teste simples"""
    state = me.state(SimpleAgentState)
    state.message = "Teste executado com sucesso!"
    state.agents_count = 2
    print("✅ Teste simples funcionando!")


def count_agents(e):
    """Conta agentes"""
    state = me.state(SimpleAgentState)
    state.agents_count = 2
    state.message = f"Encontrados {state.agents_count} agentes"
    print(f"📊 {state.agents_count} agentes encontrados!")


def debug_info(e):
    """Informações de debug"""
    state = me.state(SimpleAgentState)
    state.message = "Debug: Página funcionando corretamente"
    state.is_loading = False
    print("🐛 Debug info atualizada!") 
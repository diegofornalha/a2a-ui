"""
Página de agentes com debugging seguindo as melhores práticas do Mesop
"""

import mesop as me
from typing import List, Any
from dataclasses import field


@me.stateclass
class DebugAgentState:
    """Estado simplificado para debugging"""
    agents: List[dict[str, Any]] = field(default_factory=list)
    error_message: str = ""
    is_loading: bool = False
    debug_info: str = ""


def agents_page_debug():
    """Página de agentes com debugging"""
    state = me.state(DebugAgentState)
    
    # Título da página
    me.text(
        '🤖 Agentes A2A - Debug Mode',
        style=me.Style(
            font_size=24,
            font_weight='bold',
            margin=me.Margin(bottom=20),
            color="#2c3e50"
        )
    )
    
    # Informações de debug
    if state.debug_info:
        me.text(
            f'🔍 Debug: {state.debug_info}',
            style=me.Style(
                color="#e74c3c",
                font_size=12,
                margin=me.Margin(bottom=10)
            )
        )
    
    # Botões de ação
    with me.box(
        style=me.Style(
            display="flex",
            gap=12,
            margin=me.Margin(bottom=20)
        )
    ):
        me.button(
            '🔄 Atualizar Agentes',
            on_click=refresh_agents_debug,
            style=me.Style(
                background="#27ae60",
                color="white",
                border_radius=6,
                padding=me.Padding.all(8)
            )
        )
        me.button(
            '📋 Listar Agentes',
            on_click=list_agents_debug,
            style=me.Style(
                background="#f39c12",
                color="white",
                border_radius=6,
                padding=me.Padding.all(8)
            )
        )
        me.button(
            '🐛 Teste Simples',
            on_click=test_simple_debug,
            style=me.Style(
                background="#3498db",
                color="white",
                border_radius=6,
                padding=me.Padding.all(8)
            )
        )
    
    # Status e informações
    if state.is_loading:
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
    
    elif state.error_message:
        me.text(
            f'❌ {state.error_message}',
            style=me.Style(color='red', margin=me.Margin(bottom=16))
        )
    
    elif state.agents:
        me.text(
            f'📡 {len(state.agents)} agente(s) encontrado(s)',
            style=me.Style(
                font_weight="bold",
                font_size=16,
                margin=me.Margin(bottom=16),
                color="#2c3e50"
            )
        )
        
        # Lista de agentes simplificada
        for i, agent in enumerate(state.agents):
            show_agent_simple(agent, i)
    
    else:
        me.text(
            '🔍 Nenhum agente encontrado. Clique em "Listar Agentes"',
            style=me.Style(
                color="#7f8c8d",
                font_size=16,
                margin=me.Margin(top=20)
            )
        )


def show_agent_simple(agent: dict[str, Any], index: int):
    """Mostra agente de forma simplificada"""
    name = agent.get('name', f'Agente {index + 1}')
    description = agent.get('description', 'Sem descrição')
    url = agent.get('url', '')
    
    me.text('─' * 50)  # Separador
    me.text(f'🤖 {name}', style=me.Style(font_size=18, font_weight='bold'))
    me.text(f'📝 {description}')
    me.text(f'🔗 {url}')
    me.text('🟢 Status: Online')
    
    me.button(
        f'🔧 Testar {name}',
        key=f'test_{index}',
        on_click=lambda e, url=url, name=name: test_agent_simple(e, url, name)
    )


def test_simple_debug(e):
    """Teste simples para verificar se a página está funcionando"""
    state = me.state(DebugAgentState)
    state.debug_info = "Teste simples executado com sucesso!"
    state.error_message = ""
    state.is_loading = False
    
    # Adicionar alguns agentes de teste
    state.agents = [
        {
            'name': 'HelloWorld Agent',
            'description': 'Agente de teste Hello World',
            'url': 'http://localhost:9999',
            'status': 'online'
        },
        {
            'name': 'Marvin Agent',
            'description': 'Agente de teste Marvin',
            'url': 'http://localhost:10030',
            'status': 'online'
        }
    ]
    
    print("✅ Teste simples executado!")


def list_agents_debug(e):
    """Lista agentes de forma simplificada"""
    state = me.state(DebugAgentState)
    state.is_loading = True
    state.error_message = ""
    state.debug_info = "Listando agentes..."
    
    try:
        # Simular busca de agentes
        state.agents = [
            {
                'name': 'HelloWorld Agent',
                'description': 'Agente Hello World na porta 9999',
                'url': 'http://localhost:9999',
                'status': 'online'
            },
            {
                'name': 'Marvin Agent',
                'description': 'Agente Marvin na porta 10030',
                'url': 'http://localhost:10030',
                'status': 'online'
            }
        ]
        
        state.is_loading = False
        state.debug_info = f"Encontrados {len(state.agents)} agentes"
        print(f"✅ {len(state.agents)} agentes encontrados!")
        
    except Exception as ex:
        state.error_message = f"Erro: {str(ex)}"
        state.is_loading = False
        state.debug_info = f"Erro: {str(ex)}"


def refresh_agents_debug(e):
    """Atualiza agentes de forma simplificada"""
    state = me.state(DebugAgentState)
    state.is_loading = True
    state.error_message = ""
    state.debug_info = "Atualizando agentes..."
    
    try:
        # Simular atualização
        state.agents = [
            {
                'name': 'HelloWorld Agent (Atualizado)',
                'description': 'Agente Hello World atualizado',
                'url': 'http://localhost:9999',
                'status': 'online'
            }
        ]
        
        state.is_loading = False
        state.debug_info = "Agentes atualizados com sucesso"
        print("✅ Agentes atualizados!")
        
    except Exception as ex:
        state.error_message = f"Erro: {str(ex)}"
        state.is_loading = False
        state.debug_info = f"Erro na atualização: {str(ex)}"


def test_agent_simple(e, agent_url: str, agent_name: str):
    """Teste simples de agente"""
    print(f"🔧 Testando {agent_name} em {agent_url}")
    print(f"🔧 Testando: {agent_name} ({agent_url})") 
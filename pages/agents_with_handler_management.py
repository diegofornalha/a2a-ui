"""
Página de agentes A2A com gerenciamento de handlers para evitar erros
quando agentes desconectam.
"""

import asyncio
import httpx
import json
import mesop as me
from typing import List, Any
from dataclasses import field
from datetime import datetime

# Importar o gerenciador de handlers
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.handler_manager import handler_manager, start_handler_monitoring
from utils.mesop_handler_patch import patch_mesop_handler, create_safe_handler

# Aplicar patch no Mesop na inicialização
patch_mesop_handler()

# Iniciar monitoramento de handlers
asyncio.create_task(start_handler_monitoring())


@me.stateclass
class AgentPageState:
    agents: List[dict[str, Any]] = field(default_factory=list)
    error_message: str = ""
    is_loading: bool = False
    last_refresh: str = ""
    agent_status: dict[str, bool] = field(default_factory=dict)  # agent_url -> is_online


def agents_page():
    """Página principal de agentes A2A com gerenciamento de handlers"""
    state = me.state(AgentPageState)
    
    # Atualizar status dos agentes baseado no handler_manager
    update_agent_status(state)
    
    # Cabeçalho
    with me.box(style=me.Style(padding=me.Padding.all(20), background='#f5f5f5')):
        with me.box(style=me.Style(display='flex', justify_content='space_between', align_items='center')):
            me.text(
                '🤖 Agentes A2A com Handler Management',
                style=me.Style(font_size=28, font_weight='bold', color='#2196F3')
            )
            with me.box(style=me.Style(display='flex', gap=10)):
                me.button(
                    '🔄 Descobrir Agentes',
                    on_click=discover_agents,
                    style=me.Style(
                        background='#2196F3',
                        color='white',
                        border_radius=25,
                        padding=me.Padding.symmetric(horizontal=20, vertical=10),
                        font_size=16
                    )
                )
                me.button(
                    '🔍 Verificar Status',
                    on_click=check_agent_status,
                    style=me.Style(
                        background='#4CAF50',
                        color='white',
                        border_radius=25,
                        padding=me.Padding.symmetric(horizontal=20, vertical=10),
                        font_size=16
                    )
                )
    
    # Status do monitoramento
    with me.box(style=me.Style(padding=me.Padding.all(10), background='#e3f2fd')):
        me.text(
            f'📡 Monitoramento de Handlers: {"Ativo ✅" if handler_manager._monitor_task else "Inativo ❌"}',
            style=me.Style(color='#1976D2')
        )
        if state.last_refresh:
            me.text(
                f'Última atualização: {state.last_refresh}',
                style=me.Style(color='#666', font_size=14)
            )
    
    # Conteúdo principal
    with me.box(style=me.Style(padding=me.Padding.all(20))):
        if state.is_loading:
            loading_section()
        elif state.error_message:
            error_section(state.error_message)
        elif state.agents:
            agents_section_with_status(state.agents, state.agent_status)
        else:
            empty_section()
    
    # Auto-descobrir na primeira carga
    if not state.agents and not state.is_loading and not state.error_message:
        discover_agents(None)


def update_agent_status(state: AgentPageState):
    """Atualiza o status dos agentes baseado no handler_manager"""
    for agent in state.agents:
        agent_url = agent.get('url', '')
        state.agent_status[agent_url] = handler_manager.agent_status.get(agent_url, True)


def loading_section():
    """Seção de carregamento"""
    with me.box(style=me.Style(text_align='center', padding=me.Padding.all(40))):
        me.text('🔍 Descobrindo agentes...', style=me.Style(font_size=20, color='#666'))
        me.text('Verificando portas: 9999, 10000, 10030, 10100, 11000, 12000', style=me.Style(color='#888'))


def error_section(error: str):
    """Seção de erro"""
    with me.box(style=me.Style(text_align='center', padding=me.Padding.all(40))):
        me.text(f'❌ {error}', style=me.Style(font_size=18, color='#F44336'))


def empty_section():
    """Seção quando não há agentes"""
    with me.box(style=me.Style(text_align='center', padding=me.Padding.all(40))):
        me.text(
            '🔍 Nenhum agente A2A encontrado',
            style=me.Style(font_size=24, color='#666', margin=me.Margin(bottom=16))
        )
        me.text(
            'Certifique-se de que há agentes rodando nas portas padrão',
            style=me.Style(color='#888', margin=me.Margin(bottom=20))
        )
        me.text('Portas verificadas: 9999, 10000, 10030, 10100, 11000, 12000', style=me.Style(color='#AAA'))


def agents_section_with_status(agents: List[dict[str, Any]], agent_status: dict[str, bool]):
    """Seção principal com lista de agentes e seus status"""
    # Estatísticas
    online_count = sum(1 for a in agents if agent_status.get(a.get('url', ''), True))
    with me.box(style=me.Style(margin=me.Margin(bottom=20))):
        me.text(
            f'📡 {len(agents)} agente(s) descoberto(s) | {online_count} online',
            style=me.Style(font_size=20, font_weight='bold', color='#4CAF50')
        )
    
    # Grid de agentes
    for i, agent in enumerate(agents):
        render_agent_card_with_status(agent, i, agent_status)


def render_agent_card_with_status(agent: dict[str, Any], index: int, agent_status: dict[str, bool]):
    """Renderiza card individual de agente com status de conexão"""
    name = agent.get('name', f'Agente {index + 1}')
    description = agent.get('description', 'Sem descrição disponível')
    url = agent.get('url', '')
    port = agent.get('port', 'N/A')
    capabilities = agent.get('capabilities', {})
    is_online = agent_status.get(url, True)
    
    # Determinar cor baseada no status e porta
    colors = {
        9999: '#4CAF50',   # Verde - HelloWorld
        10000: '#2196F3',  # Azul - A2A padrão
        10030: '#FF9800',  # Laranja - Marvin
        10100: '#9C27B0',  # Roxo - MCP
        11000: '#607D8B',  # Cinza - Genérico
        12000: '#00BCD4'   # Ciano - Porta adicional
    }
    card_color = colors.get(port, '#666666')
    
    # Ajustar cor se offline
    if not is_online:
        card_color = '#F44336'  # Vermelho para offline
    
    with me.box(
        style=me.Style(
            background='white',
            border_radius=12,
            box_shadow='0 4px 12px rgba(0,0,0,0.15)',
            padding=me.Padding.all(24),
            margin=me.Margin(bottom=20),
            border=f'3px solid {card_color}',
            opacity=1.0 if is_online else 0.6
        )
    ):
        # Cabeçalho do card com status
        with me.box(style=me.Style(display='flex', justify_content='space_between', align_items='center')):
            with me.box(style=me.Style(margin=me.Margin(bottom=16))):
                me.text(
                    name,
                    style=me.Style(
                        font_size=22,
                        font_weight='bold',
                        color='#333' if is_online else '#999',
                        margin=me.Margin(bottom=8)
                    )
                )
                me.text(
                    description,
                    style=me.Style(color='#666' if is_online else '#aaa', font_size=16, line_height='1.4')
                )
            
            # Badge de status
            me.text(
                '🟢 Online' if is_online else '🔴 Offline',
                style=me.Style(
                    background='#e8f5e9' if is_online else '#ffebee',
                    color='#4CAF50' if is_online else '#F44336',
                    padding=me.Padding.symmetric(horizontal=12, vertical=6),
                    border_radius=20,
                    font_weight='bold',
                    font_size=14
                )
            )
        
        # Informações técnicas
        with me.box(style=me.Style(background='#f8f9fa', border_radius=8, padding=me.Padding.all(16))):
            with me.box(style=me.Style(display='flex', flex_wrap='wrap', gap=16)):
                # URL
                with me.box():
                    me.text('🔗 Endpoint:', style=me.Style(font_weight='bold', color='#555'))
                    me.text(url, style=me.Style(color='#2196F3' if is_online else '#999', font_family='monospace'))
                
                # Porta
                with me.box():
                    me.text('🚪 Porta:', style=me.Style(font_weight='bold', color='#555'))
                    me.text(str(port), style=me.Style(color=card_color, font_weight='bold'))
                
                # Handlers registrados
                handler_count = len(handler_manager.agent_handlers.get(url, set()))
                if handler_count > 0:
                    with me.box():
                        me.text('🔧 Handlers:', style=me.Style(font_weight='bold', color='#555'))
                        me.text(f'{handler_count} registrados', style=me.Style(color='#666'))
        
        # Capacidades
        if capabilities and is_online:
            with me.box(style=me.Style(margin=me.Margin(top=16))):
                me.text('⚡ Capacidades:', style=me.Style(font_weight='bold', color='#333', margin=me.Margin(bottom=8)))
                
                caps_list = []
                if capabilities.get('streaming'):
                    caps_list.append('📡 Streaming')
                if capabilities.get('pushNotifications'):
                    caps_list.append('🔔 Notificações')
                if capabilities.get('stateTransitionHistory'):
                    caps_list.append('📈 Histórico')
                
                if caps_list:
                    me.text(
                        ' • '.join(caps_list),
                        style=me.Style(color='#666', font_size=14)
                    )
                else:
                    me.text('Capacidades básicas', style=me.Style(color='#666', font_size=14))
        
        # Botões de ação
        with me.box(style=me.Style(display='flex', gap=10, justify_content='center', margin=me.Margin(top=20))):
            if is_online:
                # Criar handler seguro para teste
                safe_test_handler = create_safe_handler(
                    lambda e: test_agent_safe(e, url, name),
                    url
                )
                
                me.button(
                    '🔧 Testar Conectividade',
                    key=f'test_agent_{index}',
                    on_click=safe_test_handler,
                    style=me.Style(
                        background=card_color,
                        color='white',
                        border_radius=25,
                        padding=me.Padding.symmetric(horizontal=20, vertical=10),
                        font_size=14,
                        font_weight='bold'
                    )
                )
            else:
                me.button(
                    '🔄 Tentar Reconectar',
                    key=f'reconnect_agent_{index}',
                    on_click=lambda e, agent_url=url: reconnect_agent(e, agent_url),
                    style=me.Style(
                        background='#FF9800',
                        color='white',
                        border_radius=25,
                        padding=me.Padding.symmetric(horizontal=20, vertical=10),
                        font_size=14,
                        font_weight='bold'
                    )
                )


def discover_agents(e):
    """Descobre agentes nas portas padrão"""
    state = me.state(AgentPageState)
    state.is_loading = True
    state.error_message = ""
    state.agents = []
    
    try:
        agents = asyncio.run(simple_agent_discovery())
        state.agents = agents
        state.is_loading = False
        state.last_refresh = datetime.now().strftime("%H:%M:%S")
        
        # Registrar agentes no handler_manager
        for agent in agents:
            agent_url = agent.get('url', '')
            handler_manager.agent_status[agent_url] = True
        
        print(f"✅ Descobertos {len(agents)} agentes")
        for agent in agents:
            print(f"  - {agent.get('name')} ({agent.get('url')})")
            
    except Exception as ex:
        state.error_message = f"Erro na descoberta: {str(ex)}"
        state.is_loading = False
        print(f"❌ Erro: {ex}")


def check_agent_status(e):
    """Verifica manualmente o status de todos os agentes"""
    state = me.state(AgentPageState)
    state.last_refresh = datetime.now().strftime("%H:%M:%S")
    
    # Forçar verificação de todos os agentes
    asyncio.run(handler_manager._check_all_agents())
    
    # Atualizar status na UI
    update_agent_status(state)


def test_agent_safe(e, agent_url: str, agent_name: str):
    """Testa conectividade com agente de forma segura"""
    print(f"🔧 Testando conectividade (seguro): {agent_name} ({agent_url})")
    
    try:
        # Verificar se agente está online antes de testar
        is_online = asyncio.run(handler_manager.check_agent_health(agent_url))
        
        if is_online:
            print(f"✅ Agente {agent_name} está online e respondendo")
        else:
            print(f"❌ Agente {agent_name} está offline")
            
    except Exception as ex:
        print(f"❌ Erro ao testar agente: {ex}")


def reconnect_agent(e, agent_url: str):
    """Tenta reconectar a um agente offline"""
    print(f"🔄 Tentando reconectar ao agente: {agent_url}")
    
    try:
        is_online = asyncio.run(handler_manager.check_agent_health(agent_url))
        
        if is_online:
            print(f"✅ Agente {agent_url} está de volta online!")
            handler_manager.agent_status[agent_url] = True
            
            # Atualizar UI
            state = me.state(AgentPageState)
            update_agent_status(state)
        else:
            print(f"❌ Agente {agent_url} ainda está offline")
            
    except Exception as ex:
        print(f"❌ Erro ao reconectar: {ex}")


async def simple_agent_discovery() -> List[dict[str, Any]]:
    """Descoberta simplificada de agentes incluindo porta 12000"""
    ports = [9999, 10000, 10030, 10100, 11000, 12000]  # Incluída porta 12000
    endpoints = ["/.well-known/agent.json", "/agent-card", "/info", "/health"]
    
    agents = []
    
    async with httpx.AsyncClient(timeout=3.0) as client:
        tasks = []
        
        for port in ports:
            for endpoint in endpoints:
                url = f"http://localhost:{port}{endpoint}"
                task = asyncio.create_task(check_agent_endpoint(client, url, port))
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados válidos e evitar duplicatas
        seen_urls = set()
        for result in results:
            if isinstance(result, dict) and result.get('url') not in seen_urls:
                agents.append(result)
                seen_urls.add(result.get('url'))
    
    return agents


async def check_agent_endpoint(client: httpx.AsyncClient, url: str, port: int) -> dict[str, Any]:
    """Verifica um endpoint específico"""
    try:
        response = await client.get(url)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Verificar se é um agent card válido
                if isinstance(data, dict) and 'name' in data:
                    return {
                        'name': data.get('name', f'Agent Port {port}'),
                        'description': data.get('description', f'Agente descoberto na porta {port}'),
                        'url': f"http://localhost:{port}",
                        'port': port,
                        'capabilities': data.get('capabilities', {}),
                        'version': data.get('version', '1.0.0')
                    }
                    
            except json.JSONDecodeError:
                # Se não é JSON válido, criar agent básico
                if "health" in response.text.lower() or "ok" in response.text.lower():
                    return {
                        'name': f'Agent Port {port}',
                        'description': f'Agente básico na porta {port}',
                        'url': f"http://localhost:{port}",
                        'port': port,
                        'capabilities': {},
                        'version': '1.0.0'
                    }
                    
    except Exception:
        pass
    
    return None
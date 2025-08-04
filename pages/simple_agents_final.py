"""
Página de agentes A2A - Versão final SPARC sem dependências complexas
SPARC: Specification, Pseudocode, Architecture, Refinement, Completion
"""

import asyncio
import httpx
import json
import mesop as me
from typing import List, Any
from dataclasses import field


@me.stateclass
class AgentPageState:
    agents: List[dict[str, Any]] = field(default_factory=list)
    error_message: str = ""
    is_loading: bool = False
    last_refresh: str = ""


def agents_page():
    """Página principal de agentes A2A - SPARC Implementation"""
    state = me.state(AgentPageState)
    
    # Cabeçalho
    with me.box(style=me.Style(padding=me.Padding.all(20), background='#f5f5f5')):
        with me.box(style=me.Style(display='flex', justify_content='space-between', align_items='center')):
            me.text(
                '🤖 Agentes A2A Descobertos',
                style=me.Style(font_size=28, font_weight='bold', color='#2196F3')
            )
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
    
    # Conteúdo principal
    with me.box(style=me.Style(padding=me.Padding.all(20))):
        if state.is_loading:
            loading_section()
        elif state.error_message:
            error_section(state.error_message)
        elif state.agents:
            agents_section(state.agents)
        else:
            empty_section()
    
    # Auto-descobrir na primeira carga
    if not state.agents and not state.is_loading and not state.error_message:
        discover_agents(None)


def loading_section():
    """Seção de carregamento"""
    with me.box(style=me.Style(text_align='center', padding=me.Padding.all(40))):
        me.text('🔍 Descobrindo agentes...', style=me.Style(font_size=20, color='#666'))
        me.text('Verificando portas: 9999, 10000, 10030, 10100, 11000', style=me.Style(color='#888'))


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
        me.text('Portas verificadas: 9999, 10000, 10030, 10100, 11000', style=me.Style(color='#AAA'))


def agents_section(agents: List[dict[str, Any]]):
    """Seção principal com lista de agentes"""
    # Estatísticas
    with me.box(style=me.Style(margin=me.Margin(bottom=20))):
        me.text(
            f'📡 {len(agents)} agente(s) descoberto(s)',
            style=me.Style(font_size=20, font_weight='bold', color='#4CAF50')
        )
    
    # Grid de agentes
    for i, agent in enumerate(agents):
        render_agent_card(agent, i)


def render_agent_card(agent: dict[str, Any], index: int):
    """Renderiza card individual de agente"""
    name = agent.get('name', f'Agente {index + 1}')
    description = agent.get('description', 'Sem descrição disponível')
    url = agent.get('url', '')
    port = agent.get('port', 'N/A')
    capabilities = agent.get('capabilities', {})
    
    # Determinar cor baseada na porta
    colors = {
        9999: '#4CAF50',   # Verde - HelloWorld
        10000: '#2196F3',  # Azul - A2A padrão
        10030: '#FF9800',  # Laranja - Marvin
        10100: '#9C27B0',  # Roxo - MCP
        11000: '#607D8B'   # Cinza - Genérico
    }
    card_color = colors.get(port, '#666666')
    
    with me.box(
        style=me.Style(
            background='white',
            border_radius=12,
            box_shadow='0 4px 12px rgba(0,0,0,0.15)',
            padding=me.Padding.all(24),
            margin=me.Margin(bottom=20),
            border=f'3px solid {card_color}'
        )
    ):
        # Cabeçalho do card
        with me.box(style=me.Style(margin=me.Margin(bottom=16))):
            me.text(
                name,
                style=me.Style(
                    font_size=22,
                    font_weight='bold',
                    color='#333',
                    margin=me.Margin(bottom=8)
                )
            )
            me.text(
                description,
                style=me.Style(color='#666', font_size=16, line_height='1.4')
            )
        
        # Informações técnicas
        with me.box(style=me.Style(background='#f8f9fa', border_radius=8, padding=me.Padding.all(16))):
            with me.box(style=me.Style(display='flex', flex_wrap='wrap', gap=16)):
                # URL
                with me.box():
                    me.text('🔗 Endpoint:', style=me.Style(font_weight='bold', color='#555'))
                    me.text(url, style=me.Style(color='#2196F3', font_family='monospace'))
                
                # Porta
                with me.box():
                    me.text('🚪 Porta:', style=me.Style(font_weight='bold', color='#555'))
                    me.text(str(port), style=me.Style(color=card_color, font_weight='bold'))
                
                # Status
                with me.box():
                    me.text('📡 Status:', style=me.Style(font_weight='bold', color='#555'))
                    me.text('🟢 Online', style=me.Style(color='#4CAF50', font_weight='bold'))
        
        # Capacidades
        if capabilities:
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
        
        # Botão de teste
        with me.box(style=me.Style(text_align='center', margin=me.Margin(top=20))):
            me.button(
                '🔧 Testar Conectividade',
                key=f'test_agent_{index}',
                on_click=lambda e, agent_url=url, agent_name=name: test_agent(e, agent_url, agent_name),
                style=me.Style(
                    background=card_color,
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
        
        print(f"✅ Descobertos {len(agents)} agentes")
        for agent in agents:
            print(f"  - {agent.get('name')} ({agent.get('url')})")
            
    except Exception as ex:
        state.error_message = f"Erro na descoberta: {str(ex)}"
        state.is_loading = False
        print(f"❌ Erro: {ex}")


async def simple_agent_discovery() -> List[dict[str, Any]]:
    """Descoberta simplificada de agentes sem dependências complexas"""
    ports = [9999, 10000, 10030, 10100, 11000]
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


async def test_agent(e, agent_url: str, agent_name: str):
    """Testa conectividade com agente específico"""
    print(f"🔧 Testando conectividade: {agent_name} ({agent_url})")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Testar múltiplos endpoints
            test_endpoints = ["/.well-known/agent.json", "/health", "/", "/info"]
            
            for endpoint in test_endpoints:
                try:
                    test_url = agent_url.rstrip('/') + endpoint
                    response = await client.get(test_url)
                    
                    if response.status_code == 200:
                        print(f"✅ {agent_name}: Respondeu em {endpoint} (Status: {response.status_code})")
                        
                        # Tentar parsear response
                        try:
                            data = response.json()
                            if 'name' in data:
                                print(f"📋 Nome confirmado: {data['name']}")
                            if 'version' in data:
                                print(f"🔖 Versão: {data['version']}")
                        except:
                            print(f"📄 Resposta texto: {response.text[:100]}...")
                        
                        return  # Sucesso, para o teste
                        
                except Exception as endpoint_err:
                    continue  # Tenta próximo endpoint
            
            print(f"⚠️ {agent_name}: Não respondeu em nenhum endpoint testado")
            
    except Exception as ex:
        print(f"❌ Erro ao testar {agent_name}: {ex}")


# Função para integração com main.py
def create_agents_page():
    """Cria a página de agentes"""
    return agents_page()
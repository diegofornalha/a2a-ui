"""
Página de chat com Claude integrada ao Mesop
Interface para interagir com o Claude CLI sem API key
"""

import mesop as me
import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from components.page_scaffold import page_scaffold
from state.state import AppState


from dataclasses import field

@me.stateclass
class ClaudePageState:
    """Estado da página Claude"""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    current_input: str = ""
    session_id: str = ""
    is_loading: bool = False
    selected_mode: str = "chat"  # chat, code_gen, code_analyze, task
    code_language: str = "python"
    code_framework: str = ""
    analysis_type: str = "analyze"
    task_agents: List[str] = field(default_factory=list)
    error_message: str = ""
    success_message: str = ""


def claude_chat_page(state: AppState):
    """
    Página principal do Claude Chat
    """
    claude_state = me.state(ClaudePageState)
    
    # Inicializar sessão se necessário
    if not claude_state.session_id:
        claude_state.session_id = f"claude_session_{datetime.now().timestamp()}"
    
    with page_scaffold():
        with me.box(style=me.Style(
            padding=me.Padding.all(20),
            display="flex",
            flex_direction="column",
            height="100vh",
            gap=20
        )):
            # Header
            _render_header(claude_state)
            
            # Modo de operação
            _render_mode_selector(claude_state)
            
            # Área principal
            with me.box(style=me.Style(
                flex_grow=1,
                display="flex",
                gap=20,
                min_height=0
            )):
                # Chat/Output area
                _render_chat_area(claude_state)
                
                # Configurações (se necessário)
                if claude_state.selected_mode != "chat":
                    _render_config_panel(claude_state)
            
            # Input area
            _render_input_area(claude_state)
            
            # Status messages
            _render_status_messages(claude_state)


def _render_header(state: ClaudePageState):
    """Renderiza o header da página"""
    with me.box(style=me.Style(
        display="flex",
        justify_content="space-between",
        align_items="center",
        padding=me.Padding.all(10),
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        border_radius=10,
        color="white"
    )):
        me.text("🤖 Claude Assistant", 
               style=me.Style(font_size=24, font_weight="bold"))
        
        with me.box(style=me.Style(display="flex", gap=10)):
            me.text(f"Sessão: {state.session_id[:8]}...", 
                   style=me.Style(font_size=12, opacity=0.8))
            
            me.button("Nova Sessão",
                     on_click=_clear_session,
                     style=me.Style(
                         background="rgba(255,255,255,0.2)",
                         color="white",
                         border="1px solid rgba(255,255,255,0.3)",
                         padding=me.Padding.symmetric(horizontal=15, vertical=5),
                         border_radius=5
                     ))


def _render_mode_selector(state: ClaudePageState):
    """Renderiza o seletor de modo"""
    modes = [
        ("chat", "💬 Chat"),
        ("code_gen", "🔧 Gerar Código"),
        ("code_analyze", "🔍 Analisar Código"),
        ("task", "📋 Executar Tarefa")
    ]
    
    with me.box(style=me.Style(
        display="flex",
        gap=10,
        padding=me.Padding.all(10),
        background="#f8f9fa",
        border_radius=8
    )):
        me.text("Modo:", style=me.Style(font_weight="bold"))
        
        for mode_id, mode_label in modes:
            is_selected = state.selected_mode == mode_id
            me.button(
                mode_label,
                on_click=lambda e, m=mode_id: _set_mode(e, m),
                style=me.Style(
                    background="#667eea" if is_selected else "white",
                    color="white" if is_selected else "#333",
                    border="1px solid #667eea",
                    padding=me.Padding.symmetric(horizontal=15, vertical=8),
                    border_radius=5,
                    font_weight="bold" if is_selected else "normal"
                )
            )


def _render_chat_area(state: ClaudePageState):
    """Renderiza a área de chat/output"""
    with me.box(style=me.Style(
        flex_grow=1,
        background="white",
        border="1px solid #e0e0e0",
        border_radius=8,
        padding=me.Padding.all(15),
        overflow_y="auto",
        display="flex",
        flex_direction="column",
        gap=10
    )):
        if not state.messages:
            me.text("👋 Olá! Sou o Claude Assistant. Como posso ajudar?",
                   style=me.Style(
                       color="#666",
                       font_style="italic",
                       text_align="center",
                       padding=me.Padding.all(20)
                   ))
        else:
            for msg in state.messages:
                _render_message(msg)
        
        # Loading indicator
        if state.is_loading:
            with me.box(style=me.Style(
                display="flex",
                justify_content="center",
                padding=me.Padding.all(10)
            )):
                me.text("🔄 Claude está pensando...",
                       style=me.Style(
                           color="#667eea",
                           font_style="italic"
                       ))


def _render_message(msg: Dict[str, Any]):
    """Renderiza uma mensagem individual"""
    is_user = msg.get("role") == "user"
    
    with me.box(style=me.Style(
        display="flex",
        justify_content="flex-end" if is_user else "flex-start",
        margin=me.Margin.symmetric(vertical=5)
    )):
        with me.box(style=me.Style(
            max_width="70%",
            padding=me.Padding.all(12),
            background="#667eea" if is_user else "#f0f2f5",
            color="white" if is_user else "#333",
            border_radius=15,
            border_bottom_right_radius=5 if is_user else None,
            border_bottom_left_radius=5 if not is_user else None
        )):
            # Header da mensagem
            with me.box(style=me.Style(
                display="flex",
                justify_content="space-between",
                margin=me.Margin.bottom(5),
                font_size=12,
                opacity=0.8
            )):
                me.text("👤 Você" if is_user else "🤖 Claude")
                me.text(msg.get("timestamp", ""))
            
            # Conteúdo
            content = msg.get("content", "")
            
            # Se for código, renderizar com formatação
            if "```" in content:
                _render_code_content(content)
            else:
                me.text(content, style=me.Style(white_space="pre-wrap"))


def _render_code_content(content: str):
    """Renderiza conteúdo com blocos de código"""
    parts = content.split("```")
    
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Texto normal
            if part.strip():
                me.text(part.strip(), style=me.Style(white_space="pre-wrap"))
        else:
            # Bloco de código
            lines = part.split("\n")
            language = lines[0] if lines else ""
            code = "\n".join(lines[1:]) if len(lines) > 1 else part
            
            with me.box(style=me.Style(
                background="#2d2d2d",
                color="#f8f8f2",
                padding=me.Padding.all(10),
                border_radius=5,
                margin=me.Margin.symmetric(vertical=5),
                font_family="monospace",
                font_size=14,
                overflow_x="auto"
            )):
                if language:
                    me.text(f"// {language}", 
                           style=me.Style(
                               color="#75715e",
                               font_size=12,
                               margin=me.Margin.bottom(5)
                           ))
                me.text(code, style=me.Style(white_space="pre"))


def _render_config_panel(state: ClaudePageState):
    """Renderiza o painel de configurações para modos específicos"""
    with me.box(style=me.Style(
        width=300,
        background="white",
        border="1px solid #e0e0e0",
        border_radius=8,
        padding=me.Padding.all(15)
    )):
        me.text("⚙️ Configurações", 
               style=me.Style(
                   font_size=18,
                   font_weight="bold",
                   margin=me.Margin.bottom(15)
               ))
        
        if state.selected_mode == "code_gen":
            _render_code_gen_config(state)
        elif state.selected_mode == "code_analyze":
            _render_code_analyze_config(state)
        elif state.selected_mode == "task":
            _render_task_config(state)


def _render_code_gen_config(state: ClaudePageState):
    """Configurações para geração de código"""
    me.text("Linguagem:", style=me.Style(font_weight="bold"))
    me.select(
        options=[
            me.SelectOption(label="Python", value="python"),
            me.SelectOption(label="JavaScript", value="javascript"),
            me.SelectOption(label="TypeScript", value="typescript"),
            me.SelectOption(label="Java", value="java"),
            me.SelectOption(label="C++", value="cpp"),
            me.SelectOption(label="Go", value="go"),
            me.SelectOption(label="Rust", value="rust")
        ],
        value=state.code_language,
        on_change=lambda e: setattr(state, "code_language", e.value),
        style=me.Style(
            width="100%",
            margin=me.Margin.bottom(10)
        )
    )
    
    me.text("Framework (opcional):", style=me.Style(font_weight="bold"))
    me.input(
        value=state.code_framework,
        on_change=lambda e: setattr(state, "code_framework", e.value),
        placeholder="Ex: React, Django, FastAPI...",
        style=me.Style(
            width="100%",
            margin=me.Margin.bottom(10)
        )
    )


def _render_code_analyze_config(state: ClaudePageState):
    """Configurações para análise de código"""
    me.text("Tipo de Análise:", style=me.Style(font_weight="bold"))
    
    analysis_types = [
        ("analyze", "📊 Análise Geral"),
        ("review", "🔍 Review de Código"),
        ("optimize", "⚡ Otimização"),
        ("explain", "💡 Explicação")
    ]
    
    for type_id, type_label in analysis_types:
        is_selected = state.analysis_type == type_id
        me.button(
            type_label,
            on_click=lambda e, t=type_id: setattr(state, "analysis_type", t),
            style=me.Style(
                width="100%",
                background="#667eea" if is_selected else "white",
                color="white" if is_selected else "#333",
                border="1px solid #667eea",
                padding=me.Padding.all(8),
                border_radius=5,
                margin=me.Margin.bottom(5),
                text_align="left"
            )
        )


def _render_task_config(state: ClaudePageState):
    """Configurações para execução de tarefas"""
    me.text("Agentes para Perspectivas:", 
           style=me.Style(font_weight="bold"))
    
    agents = [
        "developer",
        "reviewer",
        "tester",
        "architect",
        "security",
        "performance"
    ]
    
    for agent in agents:
        is_selected = agent in state.task_agents
        me.checkbox(
            label=f"🤖 {agent.capitalize()}",
            checked=is_selected,
            on_change=lambda e, a=agent: _toggle_agent(e, a),
            style=me.Style(margin=me.Margin.bottom(5))
        )


def _render_input_area(state: ClaudePageState):
    """Renderiza a área de input"""
    with me.box(style=me.Style(
        display="flex",
        gap=10,
        padding=me.Padding.all(10),
        background="white",
        border="1px solid #e0e0e0",
        border_radius=8
    )):
        # Input baseado no modo
        if state.selected_mode in ["code_analyze"]:
            me.textarea(
                value=state.current_input,
                on_change=lambda e: setattr(state, "current_input", e.value),
                placeholder="Cole seu código aqui...",
                style=me.Style(
                    flex_grow=1,
                    min_height=100,
                    font_family="monospace",
                    font_size=14,
                    padding=me.Padding.all(10),
                    border="1px solid #ddd",
                    border_radius=5
                )
            )
        else:
            placeholder = _get_placeholder(state.selected_mode)
            me.input(
                value=state.current_input,
                on_change=lambda e: setattr(state, "current_input", e.value),
                placeholder=placeholder,
                style=me.Style(
                    flex_grow=1,
                    padding=me.Padding.all(10),
                    border="1px solid #ddd",
                    border_radius=5
                )
            )
        
        # Botão enviar
        me.button(
            "🚀 Enviar" if not state.is_loading else "⏳ Processando...",
            on_click=_send_message,
            disabled=state.is_loading or not state.current_input.strip(),
            style=me.Style(
                background="#667eea" if not state.is_loading else "#999",
                color="white",
                padding=me.Padding.symmetric(horizontal=20, vertical=10),
                border_radius=5,
                font_weight="bold",
                cursor="pointer" if not state.is_loading else "not-allowed"
            )
        )


def _render_status_messages(state: ClaudePageState):
    """Renderiza mensagens de status"""
    if state.error_message:
        with me.box(style=me.Style(
            padding=me.Padding.all(10),
            background="#fee",
            border="1px solid #fcc",
            border_radius=5,
            color="#c00",
            margin=me.Margin.top(10)
        )):
            me.text(f"❌ {state.error_message}")
    
    if state.success_message:
        with me.box(style=me.Style(
            padding=me.Padding.all(10),
            background="#efe",
            border="1px solid #cfc",
            border_radius=5,
            color="#080",
            margin=me.Margin.top(10)
        )):
            me.text(f"✅ {state.success_message}")


def _get_placeholder(mode: str) -> str:
    """Retorna o placeholder apropriado para o modo"""
    placeholders = {
        "chat": "Digite sua mensagem...",
        "code_gen": "Descreva o código que deseja gerar...",
        "code_analyze": "Cole o código para análise...",
        "task": "Descreva a tarefa a executar..."
    }
    return placeholders.get(mode, "Digite sua mensagem...")


def _set_mode(e: me.ClickEvent, mode: str):
    """Define o modo de operação"""
    state = me.state(ClaudePageState)
    state.selected_mode = mode
    state.current_input = ""


def _toggle_agent(e: me.CheckboxChangeEvent, agent: str):
    """Toggle de agente para tarefas"""
    state = me.state(ClaudePageState)
    if agent in state.task_agents:
        state.task_agents.remove(agent)
    else:
        state.task_agents.append(agent)


async def _send_message(e: me.ClickEvent):
    """Envia mensagem para o Claude"""
    state = me.state(ClaudePageState)
    
    if not state.current_input.strip():
        return
    
    # Limpar mensagens de status
    state.error_message = ""
    state.success_message = ""
    state.is_loading = True
    
    # Adicionar mensagem do usuário
    user_message = {
        "role": "user",
        "content": state.current_input,
        "timestamp": datetime.now().strftime("%H:%M")
    }
    state.messages.append(user_message)
    
    # Preparar request baseado no modo
    try:
        async with httpx.AsyncClient() as client:
            if state.selected_mode == "chat":
                response = await client.post(
                    "http://localhost:8085/claude/query",
                    json={
                        "query": state.current_input,
                        "session_id": state.session_id
                    }
                )
            
            elif state.selected_mode == "code_gen":
                response = await client.post(
                    "http://localhost:8085/claude/generate",
                    json={
                        "description": state.current_input,
                        "language": state.code_language,
                        "framework": state.code_framework or None
                    }
                )
            
            elif state.selected_mode == "code_analyze":
                response = await client.post(
                    "http://localhost:8085/claude/analyze",
                    json={
                        "code": state.current_input,
                        "language": state.code_language,
                        "analysis_type": state.analysis_type
                    }
                )
            
            elif state.selected_mode == "task":
                response = await client.post(
                    "http://localhost:8085/claude/execute",
                    json={
                        "task": state.current_input,
                        "agents": state.task_agents if state.task_agents else None
                    }
                )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                
                if result.get("success"):
                    # Extrair conteúdo baseado no modo
                    if state.selected_mode == "chat":
                        content = result.get("content", "")
                    elif state.selected_mode == "code_gen":
                        content = f"```{state.code_language}\n{result.get('code', '')}\n```"
                    elif state.selected_mode == "code_analyze":
                        content = result.get("analysis", "")
                    elif state.selected_mode == "task":
                        content = result.get("result", "")
                    
                    # Adicionar resposta do Claude
                    claude_message = {
                        "role": "assistant",
                        "content": content,
                        "timestamp": datetime.now().strftime("%H:%M")
                    }
                    state.messages.append(claude_message)
                    state.success_message = "Resposta recebida com sucesso!"
                else:
                    state.error_message = result.get("error", "Erro desconhecido")
            else:
                state.error_message = f"Erro HTTP: {response.status_code}"
    
    except Exception as ex:
        state.error_message = f"Erro de conexão: {str(ex)}"
    
    finally:
        state.is_loading = False
        state.current_input = ""


def _clear_session(e: me.ClickEvent):
    """Limpa a sessão atual"""
    state = me.state(ClaudePageState)
    state.messages = []
    state.session_id = f"claude_session_{datetime.now().timestamp()}"
    state.current_input = ""
    state.error_message = ""
    state.success_message = "Nova sessão iniciada!"
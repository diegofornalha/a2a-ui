"""
Componentes aprimorados seguindo as melhores práticas do Mesop
Incluindo otimizações de performance, reutilização e acessibilidade
"""

import mesop as me
from typing import Callable, Any, Optional, List
from dataclasses import dataclass
from state.enhanced_state import StateManager, get_ui_state, get_form_state

# ============================================================================
# COMPONENTES DE UI OTIMIZADOS
# ============================================================================

@me.component
def enhanced_button(
    text: str,
    on_click: Callable,
    *,
    key: Optional[str] = None,
    disabled: bool = False,
    variant: str = "raised",
    loading: bool = False,
    icon: Optional[str] = None,
    tooltip: Optional[str] = None
):
    """Botão aprimorado com estados de loading, ícones e tooltips"""
    button_key = key or f"btn_{text.lower().replace(' ', '_')}"
    
    # Conteúdo do botão
    with me.content_button(
        key=button_key,
        type=variant,
        on_click=on_click if not loading else lambda e: None,
        disabled=disabled or loading,
        style=me.Style(
            opacity=0.6 if disabled or loading else 1.0,
            cursor="not-allowed" if disabled else "pointer"
        )
    ):
        if tooltip:
            with me.tooltip(message=tooltip):
                _render_button_content(text, icon, loading)
        else:
            _render_button_content(text, icon, loading)

def _render_button_content(text: str, icon: Optional[str], loading: bool):
    """Renderiza o conteúdo interno do botão"""
    with me.box(style=me.Style(display="flex", align_items="center", gap=8)):
        if loading:
            me.progress_spinner(style=me.Style(width=16, height=16))
        elif icon:
            me.icon(icon)
        me.text(text)


@me.component
def enhanced_input(
    label: str,
    value: str = "",
    *,
    key: Optional[str] = None,
    placeholder: str = "",
    input_type: str = "text",
    required: bool = False,
    validation_fn: Optional[Callable[[str], bool]] = None,
    on_change: Optional[Callable] = None,
    debounce_ms: int = 300
):
    """Input aprimorado com validação em tempo real"""
    input_key = key or f"input_{label.lower().replace(' ', '_')}"
    form_state = get_form_state()
    
    # Verificar se há erro de validação
    has_error = input_key in form_state.form_errors
    error_message = form_state.form_errors.get(input_key, "")
    
    with me.box(style=me.Style(margin=me.Margin(bottom=16))):
        me.input(
            key=input_key,
            label=label,
            value=value,
            placeholder=placeholder,
            type=input_type,
            appearance="outline",
            color="warn" if has_error else "primary",
            on_blur=lambda e: _handle_input_validation(
                input_key, e.value, validation_fn, required
            ),
            on_input=on_change if on_change else lambda e: None,
            style=me.Style(width="100%")
        )
        
        # Mostrar erro de validação
        if has_error:
            me.text(
                error_message,
                style=me.Style(
                    color=me.theme_var('error'),
                    font_size=12,
                    margin=me.Margin(top=4)
                )
            )
        
        # Indicador de campo obrigatório
        if required:
            me.text(
                "*",
                style=me.Style(
                    color=me.theme_var('error'),
                    font_size=12,
                    margin=me.Margin(top=4)
                )
            )

def _handle_input_validation(key: str, value: str, validation_fn: Optional[Callable], required: bool):
    """Manipula validação de input"""
    is_valid = True
    
    if required and not value.strip():
        is_valid = False
    elif validation_fn:
        is_valid = validation_fn(value)
    
    StateManager.validate_form_field("default", key, value)


@me.component  
def enhanced_dialog(
    dialog_name: str,
    title: str,
    *,
    width: str = "400px",
    max_width: str = "90vw",
    closable: bool = True
):
    """Dialog aprimorado com gestão de estado centralizada"""
    ui_state = get_ui_state()
    is_open = ui_state.dialogs_open.get(dialog_name, False)
    
    with me.box(
        style=me.Style(
            background="rgba(0,0,0,0.5)",
            display="block" if is_open else "none",
            height="100vh",
            width="100vw",
            position="fixed",
            top=0,
            left=0,
            z_index=9999,
            overflow="auto"
        )
    ):
        with me.box(
            style=me.Style(
                display="flex",
                align_items="center",
                justify_content="center",
                min_height="100vh",
                padding=me.Padding.all(20)
            )
        ):
            with me.box(
                style=me.Style(
                    background=me.theme_var("surface"),
                    border_radius=12,
                    width=width,
                    max_width=max_width,
                    padding=me.Padding.all(24),
                    box_shadow="0 10px 25px rgba(0,0,0,0.2)"
                )
            ):
                # Header do dialog
                with me.box(
                    style=me.Style(
                        display="flex",
                        justify_content="space-between",
                        align_items="center",
                        margin=me.Margin(bottom=20)
                    )
                ):
                    me.text(
                        title,
                        type="headline-6",
                        style=me.Style(font_weight=600)
                    )
                    
                    if closable:
                        with me.content_button(
                            type="icon",
                            on_click=lambda e: StateManager.toggle_dialog(dialog_name)
                        ):
                            me.icon("close")
                
                # Conteúdo do dialog
                me.slot()


@me.component
def notification_system():
    """Sistema de notificações/toasts aprimorado"""
    ui_state = get_ui_state()
    
    if not ui_state.notifications:
        return
    
    with me.box(
        style=me.Style(
            position="fixed",
            top=20,
            right=20,
            z_index=10000,
            display="flex",
            flex_direction="column",
            gap=12
        )
    ):
        for notification in ui_state.notifications[-5:]:  # Máximo 5 notificações
            _render_notification(notification)

def _render_notification(notification: dict):
    """Renderiza uma notificação individual"""
    colors = {
        "info": me.theme_var("primary"),
        "success": "#4CAF50",
        "warning": "#FF9800", 
        "error": "#F44336"
    }
    
    bg_color = colors.get(notification["type"], colors["info"])
    
    with me.box(
        style=me.Style(
            background=bg_color,
            color="white",
            padding=me.Padding.all(16),
            border_radius=8,
            min_width=300,
            max_width=400,
            box_shadow="0 4px 12px rgba(0,0,0,0.15)",
            animation="slideInRight 0.3s ease-out"
        )
    ):
        with me.box(
            style=me.Style(
                display="flex", 
                justify_content="space-between",
                align_items="center"
            )
        ):
            me.text(
                notification["message"],
                style=me.Style(flex_grow=1)
            )
            
            with me.content_button(
                type="icon",
                on_click=lambda e: _dismiss_notification(notification["id"]),
                style=me.Style(color="white")
            ):
                me.icon("close", style=me.Style(font_size=16))

def _dismiss_notification(notification_id: str):
    """Remove uma notificação específica"""
    ui_state = get_ui_state()
    ui_state.notifications = [
        n for n in ui_state.notifications 
        if n["id"] != notification_id
    ]


@me.component
def enhanced_table(
    data: List[dict],
    columns: List[dict],
    *,
    key: Optional[str] = None,
    searchable: bool = True,
    sortable: bool = True,
    paginated: bool = True,
    page_size: int = 10,
    on_row_click: Optional[Callable] = None
):
    """Tabela aprimorada com busca, ordenação e paginação"""
    table_key = key or "enhanced_table"
    
    # Estado local da tabela (poderia ser movido para estado global)
    with me.box(style=me.Style(width="100%")):
        
        # Barra de pesquisa
        if searchable:
            with me.box(style=me.Style(margin=me.Margin(bottom=16))):
                me.input(
                    placeholder="Buscar...",
                    key=f"{table_key}_search",
                    appearance="outline",
                    style=me.Style(width="100%")
                )
        
        # Renderizar tabela (versão simplificada)
        with me.box(
            style=me.Style(
                border=me.Border.all(me.BorderSide(width=1, color="#e0e0e0")),
                border_radius=8,
                overflow="hidden"
            )
        ):
            # Header
            with me.box(
                style=me.Style(
                    display="flex",
                    background="#f5f5f5",
                    font_weight=600
                )
            ):
                for col in columns:
                    with me.box(
                        style=me.Style(
                            padding=me.Padding.all(12),
                            flex_grow=1,
                            border_right=me.Border(
                                right=me.BorderSide(width=1, color="#e0e0e0")
                            )
                        )
                    ):
                        me.text(col["label"])
            
            # Dados
            for i, row in enumerate(data[:page_size]):
                row_style = me.Style(
                    display="flex",
                    background="#fafafa" if i % 2 == 0 else "white",
                    cursor="pointer" if on_row_click else "default"
                )
                
                with me.box(
                    style=row_style,
                    key=f"{table_key}_row_{i}",
                    on_click=lambda e, r=row: on_row_click(r) if on_row_click else None
                ):
                    for col in columns:
                        with me.box(
                            style=me.Style(
                                padding=me.Padding.all(12),
                                flex_grow=1,
                                border_right=me.Border(
                                    right=me.BorderSide(width=1, color="#e0e0e0")
                                )
                            )
                        ):
                            me.text(str(row.get(col["key"], "")))


@me.component 
def loading_overlay(
    loading: bool,
    message: str = "Carregando..."
):
    """Overlay de loading reutilizável"""
    if not loading:
        return
        
    with me.box(
        style=me.Style(
            position="fixed",
            top=0,
            left=0,
            width="100vw", 
            height="100vh",
            background="rgba(255,255,255,0.8)",
            z_index=9998,
            display="flex",
            align_items="center",
            justify_content="center",
            flex_direction="column"
        )
    ):
        me.progress_spinner(
            style=me.Style(width=48, height=48, margin=me.Margin(bottom=16))
        )
        me.text(
            message,
            style=me.Style(font_size=16, color="#666")
        )


# ============================================================================
# COMPONENTES DE LAYOUT AVANÇADOS  
# ============================================================================

@me.content_component
def responsive_grid(
    columns: int = 3,
    gap: int = 16,
    breakpoints: Optional[dict] = None
):
    """Grid responsivo que se adapta a diferentes tamanhos de tela"""
    default_breakpoints = {
        "mobile": 1,
        "tablet": 2, 
        "desktop": columns
    }
    
    breakpoints = breakpoints or default_breakpoints
    
    # Simplificado - em produção usaria media queries
    with me.box(
        style=me.Style(
            display="grid",
            grid_template_columns=f"repeat({columns}, 1fr)",
            gap=gap,
            width="100%"
        )
    ):
        me.slot()


@me.content_component  
def card_container(
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    actions: Optional[List] = None,
    elevated: bool = True
):
    """Container de card reutilizável com header e actions"""
    with me.box(
        style=me.Style(
            background=me.theme_var("surface"),
            border_radius=12,
            padding=me.Padding.all(24),
            box_shadow="0 2px 8px rgba(0,0,0,0.1)" if elevated else None,
            border=me.Border.all(me.BorderSide(width=1, color="#e0e0e0")) if not elevated else None
        )
    ):
        # Header do card
        if title or actions:
            with me.box(
                style=me.Style(
                    display="flex",
                    justify_content="space-between",
                    align_items="center",
                    margin=me.Margin(bottom=16)
                )
            ):
                if title:
                    with me.box():
                        me.text(title, type="headline-6", style=me.Style(font_weight=600))
                        if subtitle:
                            me.text(
                                subtitle, 
                                style=me.Style(color="#666", font_size=14)
                            )
                
                if actions:
                    with me.box(style=me.Style(display="flex", gap=8)):
                        for action in actions:
                            action()  # Renderizar cada action
        
        # Conteúdo do card
        me.slot()


# ============================================================================
# HELPERS E UTILITIES
# ============================================================================

def show_success_notification(message: str):
    """Helper para mostrar notificação de sucesso"""
    StateManager.add_notification(message, type="success")

def show_error_notification(message: str):
    """Helper para mostrar notificação de erro"""  
    StateManager.add_notification(message, type="error")

def show_info_notification(message: str):
    """Helper para mostrar notificação informativa"""
    StateManager.add_notification(message, type="info")

def open_dialog(dialog_name: str):
    """Helper para abrir dialog"""
    StateManager.toggle_dialog(dialog_name)

def close_dialog(dialog_name: str):
    """Helper para fechar dialog"""
    ui_state = get_ui_state()
    ui_state.dialogs_open[dialog_name] = False 
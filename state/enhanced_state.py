"""
Sistema de gestão de estado aprimorado para o Mesop UI
Seguindo as melhores práticas da documentação do Mesop
"""

import dataclasses
from dataclasses import field
from typing import Any, Literal
import mesop as me

# ============================================================================
# ESTADOS ESPECIALIZADOS POR FUNCIONALIDADE
# ============================================================================

@me.stateclass 
class ConversationState:
    """Estado específico para conversações - maior granularidade"""
    current_conversation_id: str = ""
    conversations: list[Any] = field(default_factory=list)
    messages: list[Any] = field(default_factory=list)
    
    # Estado de carregamento por conversa
    loading_conversations: dict[str, bool] = field(default_factory=dict)
    
    # Cache de mensagens para performance
    message_cache: dict[str, Any] = field(default_factory=dict)

@me.stateclass
class AgentState:
    """Estado específico para gerenciar agentes"""
    agents: list[Any] = field(default_factory=list)
    selected_agent: str = ""
    agent_capabilities: dict[str, Any] = field(default_factory=dict)
    
    # Estados de loading específicos
    loading_agents: bool = False
    syncing_agent: str = ""

@me.stateclass
class TaskState:
    """Estado específico para tarefas"""
    task_list: list[Any] = field(default_factory=list)
    active_tasks: dict[str, bool] = field(default_factory=dict)
    task_history: list[Any] = field(default_factory=list)
    
    # Filtros e paginação
    task_filter: str = ""
    current_page: int = 1
    tasks_per_page: int = 10

@me.stateclass
class UIState:
    """Estado específico para controles de UI"""
    sidenav_open: bool = False
    theme_mode: Literal['system', 'light', 'dark'] = 'system'
    current_page: str = "/"
    
    # Estados de dialogs
    dialogs_open: dict[str, bool] = field(default_factory=dict)
    
    # Estados de loading
    loading_states: dict[str, bool] = field(default_factory=dict)
    
    # Notificações/Toasts
    notifications: list[dict[str, Any]] = field(default_factory=list)

@me.stateclass
class FormState:
    """Estado para gerenciar formulários complexos"""
    form_data: dict[str, Any] = field(default_factory=dict)
    form_errors: dict[str, str] = field(default_factory=dict)
    form_validation: dict[str, bool] = field(default_factory=dict)
    
    # Estados de submissão
    submitting_forms: dict[str, bool] = field(default_factory=dict)

@me.stateclass
class PerformanceState:
    """Estado para tracking de performance"""
    polling_interval: int = 5
    background_tasks: dict[str, str] = field(default_factory=dict)
    
    # Cache para otimizações
    component_cache: dict[str, Any] = field(default_factory=dict)
    
    # Configurações de performance
    enable_optimistic_updates: bool = True
    batch_updates: bool = True


# ============================================================================
# UTILITIES PARA GESTÃO DE ESTADO
# ============================================================================

def get_conversation_state() -> ConversationState:
    """Helper para acessar estado de conversação"""
    return me.state(ConversationState)

def get_agent_state() -> AgentState:
    """Helper para acessar estado de agentes"""
    return me.state(AgentState)

def get_task_state() -> TaskState:
    """Helper para acessar estado de tarefas"""
    return me.state(TaskState)

def get_ui_state() -> UIState:
    """Helper para acessar estado de UI"""
    return me.state(UIState)

def get_form_state() -> FormState:
    """Helper para acessar estado de formulários"""
    return me.state(FormState)

def get_performance_state() -> PerformanceState:
    """Helper para acessar estado de performance"""
    return me.state(PerformanceState)


# ============================================================================
# GERENCIADORES DE ESTADO
# ============================================================================

class StateManager:
    """Gerenciador centralizado de estado seguindo boas práticas do Mesop"""
    
    @staticmethod
    def reset_conversation_state():
        """Reset do estado de conversação"""
        state = get_conversation_state()
        state.current_conversation_id = ""
        state.conversations = []
        state.messages = []
        state.loading_conversations = {}
        state.message_cache = {}
    
    @staticmethod
    def toggle_dialog(dialog_name: str):
        """Toggle de dialog usando estado especializado"""
        ui_state = get_ui_state()
        current_state = ui_state.dialogs_open.get(dialog_name, False)
        ui_state.dialogs_open[dialog_name] = not current_state
    
    @staticmethod
    def set_loading_state(component: str, loading: bool):
        """Gerenciamento centralizado de estados de loading"""
        ui_state = get_ui_state()
        ui_state.loading_states[component] = loading
    
    @staticmethod
    def add_notification(message: str, type: str = "info", duration: int = 5000):
        """Sistema de notificações"""
        ui_state = get_ui_state()
        notification = {
            "id": f"notif_{len(ui_state.notifications)}",
            "message": message,
            "type": type,
            "duration": duration,
            "timestamp": me.time.time() if hasattr(me, 'time') else 0
        }
        ui_state.notifications.append(notification)
    
    @staticmethod
    def validate_form_field(form_id: str, field_name: str, value: Any) -> bool:
        """Validação de campo de formulário"""
        form_state = get_form_state()
        
        # Exemplo de validação básica
        is_valid = True
        error_message = ""
        
        if field_name == "email":
            if "@" not in str(value):
                is_valid = False
                error_message = "Email inválido"
        elif field_name == "required" and not value:
            is_valid = False
            error_message = "Campo obrigatório"
        
        # Atualizar estado de validação
        validation_key = f"{form_id}_{field_name}"
        form_state.form_validation[validation_key] = is_valid
        
        if not is_valid:
            form_state.form_errors[validation_key] = error_message
        elif validation_key in form_state.form_errors:
            del form_state.form_errors[validation_key]
        
        return is_valid


# ============================================================================
# DECORATORS PARA OTIMIZAÇÃO
# ============================================================================

def with_loading_state(component_name: str):
    """Decorator para automatizar estados de loading"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            StateManager.set_loading_state(component_name, True)
            try:
                if callable(func):
                    result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                    return result
            finally:
                StateManager.set_loading_state(component_name, False)
        return wrapper
    return decorator

def with_error_handling(component_name: str):
    """Decorator para tratamento de erros com notificações"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            except Exception as e:
                StateManager.add_notification(
                    f"Erro em {component_name}: {str(e)}", 
                    type="error"
                )
                raise
        return wrapper
    return decorator 
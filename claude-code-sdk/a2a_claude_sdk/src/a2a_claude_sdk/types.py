"""
Tipos e interfaces para o A2A Claude SDK.

Este módulo define todos os tipos necessários para integração
entre o A2A UI e o Claude Code SDK.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)
from pathlib import Path


class AgentType(Enum):
    """Tipos de agentes suportados no sistema A2A."""
    
    ORCHESTRATOR = "orchestrator"
    PLANNER = "planner"
    EXECUTOR = "executor"
    GUARDIAN = "guardian"
    ANALYZER = "analyzer"
    CLAUDE = "claude"
    MCP = "mcp"
    CUSTOM = "custom"


class MessageRole(Enum):
    """Papéis de mensagem no sistema."""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"
    TOOL = "tool"


class ConversationState(Enum):
    """Estados de uma conversa."""
    
    IDLE = "idle"
    ACTIVE = "active"
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class PermissionMode(Enum):
    """Modos de permissão para operações."""
    
    AUTO = "auto"
    MANUAL = "manual"
    ACCEPT_EDITS = "acceptEdits"
    REVIEW = "review"
    DENY = "deny"


@dataclass
class AgentInfo:
    """Informações de um agente."""
    
    id: str
    name: str
    type: AgentType
    description: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "idle"
    metadata: Dict[str, Any] = field(default_factory=dict)
    host: Optional[str] = None
    port: Optional[int] = None


@dataclass
class Message:
    """Mensagem no sistema A2A."""
    
    id: str
    role: MessageRole
    content: str
    timestamp: str
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)


@dataclass
class Conversation:
    """Conversa entre agentes."""
    
    id: str
    title: str
    participants: List[str]
    messages: List[Message]
    state: ConversationState
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Tarefa a ser executada por agentes."""
    
    id: str
    title: str
    description: str
    assignee: Optional[str] = None
    status: str = "pending"
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class A2ASettings:
    """Configurações do A2A Claude SDK."""
    
    # Configurações básicas
    api_key: Optional[str] = None
    base_url: str = "http://localhost:8080"
    timeout: int = 30000
    
    # Configurações de agentes
    default_agent: str = "orchestrator"
    agent_discovery_enabled: bool = True
    agent_registry_path: Optional[Path] = None
    
    # Configurações do Claude
    claude_enabled: bool = True
    claude_model: str = "claude-3-opus-20240229"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7
    
    # Configurações MCP
    mcp_enabled: bool = False
    mcp_servers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Configurações de UI
    ui_theme: str = "light"
    ui_language: str = "pt-BR"
    show_agent_cards: bool = True
    
    # Permissões
    permission_mode: PermissionMode = PermissionMode.MANUAL
    allowed_tools: List[str] = field(default_factory=lambda: [
        "Read", "Write", "Bash", "WebSearch", "WebFetch"
    ])
    
    # Caminhos
    working_directory: Optional[Path] = None
    memory_path: Optional[Path] = None
    logs_path: Optional[Path] = None
    
    # Debug e logging
    debug: bool = False
    log_level: str = "INFO"
    trace_enabled: bool = False


@runtime_checkable
class Logger(Protocol):
    """Interface para logger."""
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log de debug."""
        ...
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log de informação."""
        ...
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log de aviso."""
        ...
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log de erro."""
        ...


class ToolCall(TypedDict):
    """Chamada de ferramenta."""
    
    id: str
    name: str
    arguments: Dict[str, Any]


class ToolResult(TypedDict):
    """Resultado de ferramenta."""
    
    tool_call_id: str
    output: Any
    error: Optional[str]


@dataclass
class AgentResponse:
    """Resposta de um agente."""
    
    agent_id: str
    message: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    thinking: Optional[str] = None
    confidence: float = 1.0


@dataclass
class WorkflowStep:
    """Passo em um workflow de agentes."""
    
    id: str
    name: str
    agent: str
    input: Any
    output: Optional[Any] = None
    status: str = "pending"
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Workflow:
    """Workflow de múltiplos agentes."""
    
    id: str
    name: str
    steps: List[WorkflowStep]
    status: str = "pending"
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


# Tipos para compatibilidade com Claude Code SDK
ClaudeMessage = Union[Message, Dict[str, Any]]
ClaudeOptions = Dict[str, Any]
ClaudeResponse = Dict[str, Any]


# Constantes úteis
DEFAULT_TIMEOUT = 30000
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MODEL = "claude-3-opus-20240229"

# Mapeamento de ferramentas A2A para Claude
TOOL_MAPPING = {
    "file_read": "Read",
    "file_write": "Write",
    "execute_command": "Bash",
    "web_search": "WebSearch",
    "web_fetch": "WebFetch",
    "create_task": "TodoWrite",
    "update_task": "TodoWrite",
}

# Estados válidos para tarefas
TASK_STATES = [
    "pending",
    "in_progress",
    "completed",
    "failed",
    "cancelled",
    "blocked",
]

# Prioridades de tarefas
TASK_PRIORITIES = {
    "low": 0,
    "normal": 1,
    "high": 2,
    "urgent": 3,
    "critical": 4,
}
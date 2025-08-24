"""
Patch temporário para resolver importações de tipos A2A
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class AgentCard:
    name: str
    description: str
    url: str
    provider: Optional[Dict[str, Any]] = None
    version: str = "1.0.0"
    documentationUrl: str = ""
    capabilities: Dict[str, Any] = None
    authentication: Dict[str, Any] = None
    defaultInputModes: List[str] = None
    defaultOutputModes: List[str] = None
    skills: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = {}
        if self.authentication is None:
            self.authentication = {}
        if self.defaultInputModes is None:
            self.defaultInputModes = ["text"]
        if self.defaultOutputModes is None:
            self.defaultOutputModes = ["text"]
        if self.skills is None:
            self.skills = []

# Outros tipos básicos necessários
@dataclass
class FileWithBytes:
    name: str
    content: bytes
    content_type: str = "application/octet-stream"

@dataclass
class Message:
    content: str
    role: str = "user"

@dataclass
class Part:
    content: str
    part_type: str = "text"

class Role:
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class Task:
    id: str
    description: str
    status: str = "pending"

class TaskState:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
"""
Patch para o Mesop para interceptar execução de handlers e evitar 
o erro "Unknown handler id" quando agentes desconectam.
"""

import mesop as me
from mesop.runtime import context
from mesop.exceptions import MesopException
import logging
from typing import Optional, Callable
from .handler_manager import handler_manager, is_handler_valid

logger = logging.getLogger(__name__)

# Salvar referência ao método original
_original_run_event_handler = None


def patch_mesop_handler():
    """
    Aplica patch no Mesop para interceptar execução de handlers.
    """
    global _original_run_event_handler
    
    # Salvar método original
    if hasattr(context.Context, 'run_event_handler'):
        _original_run_event_handler = context.Context.run_event_handler
        
        # Substituir com versão patcheada
        context.Context.run_event_handler = patched_run_event_handler
        logger.info("Mesop handler patched successfully")
    else:
        logger.error("Could not patch Mesop - run_event_handler not found")


def unpatch_mesop_handler():
    """
    Remove o patch do Mesop.
    """
    global _original_run_event_handler
    
    if _original_run_event_handler and hasattr(context.Context, 'run_event_handler'):
        context.Context.run_event_handler = _original_run_event_handler
        _original_run_event_handler = None
        logger.info("Mesop handler patch removed")


def patched_run_event_handler(self, event):
    """
    Versão patcheada do run_event_handler que verifica se o handler é válido.
    
    Args:
        self: Instância do Context
        event: Evento do usuário
    """
    handler_id = event.handler_id
    
    # Verificar se o handler é válido (agente online)
    if not is_handler_valid(handler_id):
        logger.warning(f"Handler {handler_id} is invalid (agent offline), skipping execution")
        
        # Em vez de lançar exceção, podemos:
        # 1. Mostrar mensagem de erro ao usuário
        # 2. Tentar reconectar ao agente
        # 3. Redirecionar para outra página
        
        # Por ora, vamos apenas logar e não executar
        # Isso evita o erro "Unknown handler id"
        return
    
    # Tentar executar o handler original
    try:
        # Chamar método original
        if _original_run_event_handler:
            _original_run_event_handler(self, event)
        else:
            # Fallback se não temos o método original
            handler = self._handlers.get(handler_id)
            if handler:
                handler(event)
            else:
                # Handler não encontrado - este é o erro que estamos evitando
                logger.error(f"Unknown handler id: {handler_id}")
                # Em vez de lançar exceção, apenas logar
                # raise MesopException(f"Unknown handler id: {handler_id}")
                
    except Exception as e:
        logger.error(f"Error executing handler {handler_id}: {e}")
        # Podemos tratar o erro de forma mais amigável aqui
        raise


def create_safe_handler(handler_fn: Callable, agent_url: str) -> Callable:
    """
    Cria um handler seguro que verifica se o agente está online.
    
    Args:
        handler_fn: Função handler original
        agent_url: URL do agente
        
    Returns:
        Handler seguro
    """
    def safe_handler(*args, **kwargs):
        # Verificar se agente está online
        if not handler_manager.agent_status.get(agent_url, True):
            logger.warning(f"Handler called for offline agent {agent_url}")
            # Podemos mostrar uma mensagem de erro ao usuário
            # ou tentar reconectar
            return
        
        # Executar handler original
        return handler_fn(*args, **kwargs)
    
    # Preservar metadados do handler original
    safe_handler.__name__ = handler_fn.__name__
    safe_handler.__module__ = handler_fn.__module__
    
    return safe_handler


class HandlerRegistry:
    """
    Registry para rastrear handlers e seus agentes associados.
    """
    
    def __init__(self):
        self.handlers = {}  # handler_id -> (handler_fn, agent_url)
    
    def register(self, handler_id: str, handler_fn: Callable, agent_url: str):
        """Registra um handler com seu agente."""
        self.handlers[handler_id] = (handler_fn, agent_url)
        handler_manager.register_handler(handler_id, agent_url)
    
    def unregister(self, handler_id: str):
        """Remove um handler do registro."""
        if handler_id in self.handlers:
            del self.handlers[handler_id]
            handler_manager.unregister_handler(handler_id)
    
    def get_agent_url(self, handler_id: str) -> Optional[str]:
        """Obtém a URL do agente para um handler."""
        if handler_id in self.handlers:
            return self.handlers[handler_id][1]
        return None


# Instância global do registry
handler_registry = HandlerRegistry()
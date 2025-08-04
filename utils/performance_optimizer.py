"""
Sistema de otimização de performance para Mesop UI
Implementa cache, lazy loading e otimizações de renderização
"""

import mesop as me
from typing import Any, Callable, Optional, Dict, List, TypeVar, Generic
from dataclasses import dataclass, field
from functools import wraps, lru_cache
import time
import weakref
from threading import Lock

# ============================================================================
# CACHE SYSTEM
# ============================================================================

T = TypeVar('T')

@dataclass
class CacheEntry(Generic[T]):
    """Entrada do cache com timestamp e TTL"""
    value: T
    timestamp: float
    ttl: float = 300  # 5 minutos padrão
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

class PerformanceCache:
    """Sistema de cache thread-safe com TTL"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    self._stats['hits'] += 1
                    return entry.value
                else:
                    del self._cache[key]
                    self._stats['evictions'] += 1
            
            self._stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: float = 300) -> None:
        """Armazena valor no cache"""
        with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl
            )
    
    def invalidate(self, key: str) -> None:
        """Remove entrada do cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()
            self._stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do cache"""
        with self._lock:
            return self._stats.copy()

# Instância global do cache
_performance_cache = PerformanceCache()

# ============================================================================
# DECORATORS DE PERFORMANCE
# ============================================================================

def cached_component(ttl: float = 300, key_func: Optional[Callable] = None):
    """
    Decorator para cache de componentes Mesop
    
    Args:
        ttl: Tempo de vida em segundos
        key_func: Função para gerar chave personalizada
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave do cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Verifica cache
            cached_result = _performance_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            _performance_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def debounce(wait_time: float = 0.3):
    """
    Decorator para debounce de eventos
    
    Args:
        wait_time: Tempo de espera em segundos
    """
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_called[0] >= wait_time:
                last_called[0] = current_time
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

# ============================================================================
# LAZY LOADING SYSTEM
# ============================================================================

@dataclass
class LazyContent:
    """Conteúdo carregado sob demanda"""
    loader: Callable[[], Any]
    placeholder: Optional[Any] = None
    loading_text: str = "Carregando..."
    error_text: str = "Erro ao carregar"
    loaded: bool = False
    content: Any = None
    error: Optional[Exception] = None

class LazyLoader:
    """Sistema de carregamento lazy para componentes"""
    
    def __init__(self):
        self._lazy_contents: Dict[str, LazyContent] = {}
        self._loading_states: Dict[str, bool] = {}
    
    def register_lazy_content(
        self,
        key: str,
        loader: Callable[[], Any],
        placeholder: Optional[Any] = None
    ) -> None:
        """Registra conteúdo para carregamento lazy"""
        self._lazy_contents[key] = LazyContent(
            loader=loader,
            placeholder=placeholder
        )
    
    def load_content(self, key: str) -> Any:
        """Carrega conteúdo sob demanda"""
        if key not in self._lazy_contents:
            return None
        
        lazy_content = self._lazy_contents[key]
        
        if lazy_content.loaded:
            return lazy_content.content
        
        if self._loading_states.get(key, False):
            return lazy_content.placeholder or lazy_content.loading_text
        
        try:
            self._loading_states[key] = True
            lazy_content.content = lazy_content.loader()
            lazy_content.loaded = True
            return lazy_content.content
        except Exception as e:
            lazy_content.error = e
            return lazy_content.error_text
        finally:
            self._loading_states[key] = False

# Instância global do lazy loader
_lazy_loader = LazyLoader()

# ============================================================================
# VIRTUAL SCROLLING
# ============================================================================

@dataclass
class VirtualScrollConfig:
    """Configuração para virtual scrolling"""
    item_height: int = 50
    container_height: int = 400
    overscan: int = 5
    total_items: int = 0

class VirtualScroller:
    """Sistema de virtual scrolling para listas grandes"""
    
    @staticmethod
    def calculate_visible_range(
        scroll_top: int,
        config: VirtualScrollConfig
    ) -> tuple[int, int]:
        """Calcula range de items visíveis"""
        visible_start = max(0, scroll_top // config.item_height - config.overscan)
        visible_end = min(
            config.total_items,
            visible_start + (config.container_height // config.item_height) + (2 * config.overscan)
        )
        return visible_start, visible_end
    
    @staticmethod
    def get_spacer_heights(
        visible_start: int,
        visible_end: int,
        config: VirtualScrollConfig
    ) -> tuple[int, int]:
        """Calcula alturas dos spacers"""
        top_spacer = visible_start * config.item_height
        bottom_spacer = (config.total_items - visible_end) * config.item_height
        return top_spacer, bottom_spacer

# ============================================================================
# MESOP PERFORMANCE UTILITIES
# ============================================================================

class MesopPerformanceMonitor:
    """Monitor de performance para componentes Mesop"""
    
    def __init__(self):
        self._render_times: Dict[str, List[float]] = {}
        self._component_counts: Dict[str, int] = {}
    
    def track_render_time(self, component_name: str, render_time: float) -> None:
        """Registra tempo de renderização"""
        if component_name not in self._render_times:
            self._render_times[component_name] = []
        
        self._render_times[component_name].append(render_time)
        
        # Mantém apenas os últimos 100 registros
        if len(self._render_times[component_name]) > 100:
            self._render_times[component_name] = self._render_times[component_name][-100:]
    
    def get_average_render_time(self, component_name: str) -> float:
        """Retorna tempo médio de renderização"""
        if component_name not in self._render_times:
            return 0.0
        
        times = self._render_times[component_name]
        return sum(times) / len(times) if times else 0.0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Retorna relatório de performance"""
        report = {
            'cache_stats': _performance_cache.get_stats(),
            'render_times': {},
            'component_counts': self._component_counts.copy()
        }
        
        for component, times in self._render_times.items():
            report['render_times'][component] = {
                'average': self.get_average_render_time(component),
                'count': len(times),
                'latest': times[-1] if times else 0.0
            }
        
        return report

# Instância global do monitor
_performance_monitor = MesopPerformanceMonitor()

# ============================================================================
# COMPONENT OPTIMIZATION HELPERS
# ============================================================================

def optimized_component(name: str):
    """
    Decorator para otimização automática de componentes
    
    Args:
        name: Nome do componente para tracking
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                render_time = end_time - start_time
                _performance_monitor.track_render_time(name, render_time)
        
        return wrapper
    return decorator

def batch_updates(updates: List[Callable]) -> None:
    """
    Executa múltiplas atualizações em lote
    
    Args:
        updates: Lista de funções de atualização
    """
    for update in updates:
        try:
            update()
        except Exception as e:
            print(f"Erro na atualização em lote: {e}")

# ============================================================================
# MEMORY MANAGEMENT
# ============================================================================

class MemoryManager:
    """Gerenciador de memória para componentes Mesop"""
    
    def __init__(self):
        self._weak_refs: Dict[str, weakref.ref] = {}
        self._cleanup_callbacks: Dict[str, List[Callable]] = {}
    
    def register_component(self, key: str, component: Any) -> None:
        """Registra componente para gerenciamento de memória"""
        self._weak_refs[key] = weakref.ref(component, self._cleanup_component)
    
    def _cleanup_component(self, weak_ref: weakref.ref) -> None:
        """Callback de limpeza quando componente é coletado pelo GC"""
        # Encontra a chave do componente
        key_to_remove = None
        for key, ref in self._weak_refs.items():
            if ref is weak_ref:
                key_to_remove = key
                break
        
        if key_to_remove:
            # Executa callbacks de limpeza
            if key_to_remove in self._cleanup_callbacks:
                for callback in self._cleanup_callbacks[key_to_remove]:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Erro no callback de limpeza: {e}")
                
                del self._cleanup_callbacks[key_to_remove]
            
            # Remove referência
            del self._weak_refs[key_to_remove]
    
    def add_cleanup_callback(self, key: str, callback: Callable) -> None:
        """Adiciona callback de limpeza para componente"""
        if key not in self._cleanup_callbacks:
            self._cleanup_callbacks[key] = []
        
        self._cleanup_callbacks[key].append(callback)
    
    def force_cleanup(self, key: str) -> None:
        """Força limpeza de componente"""
        if key in self._cleanup_callbacks:
            for callback in self._cleanup_callbacks[key]:
                try:
                    callback()
                except Exception as e:
                    print(f"Erro na limpeza forçada: {e}")
        
        # Remove referências
        if key in self._weak_refs:
            del self._weak_refs[key]
        if key in self._cleanup_callbacks:
            del self._cleanup_callbacks[key]

# Instância global do gerenciador de memória
_memory_manager = MemoryManager()

# ============================================================================
# PUBLIC API
# ============================================================================

def get_cache() -> PerformanceCache:
    """Retorna instância do cache de performance"""
    return _performance_cache

def get_lazy_loader() -> LazyLoader:
    """Retorna instância do lazy loader"""
    return _lazy_loader

def get_performance_monitor() -> MesopPerformanceMonitor:
    """Retorna instância do monitor de performance"""
    return _performance_monitor

def get_memory_manager() -> MemoryManager:
    """Retorna instância do gerenciador de memória"""
    return _memory_manager

def clear_all_caches() -> None:
    """Limpa todos os caches do sistema"""
    _performance_cache.clear()

def get_performance_report() -> Dict[str, Any]:
    """Retorna relatório completo de performance"""
    return _performance_monitor.get_performance_report() 
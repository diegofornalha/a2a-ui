"""
Sistema de roteamento aprimorado para Mesop UI
Implementa navigation guards, lazy loading e gestão avançada de rotas
"""

import mesop as me
from typing import Dict, Any, Callable, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse, parse_qs
import re
from functools import wraps
from utils.performance_optimizer import LazyLoader, get_lazy_loader, cached_component

# ============================================================================
# ROUTE CONFIGURATION
# ============================================================================

class RouteAccessLevel(Enum):
    """Níveis de acesso para rotas"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ADMIN = "admin"
    PREMIUM = "premium"

@dataclass
class RouteConfig:
    """Configuração de uma rota"""
    path: str
    component: Union[Callable, str]  # Componente ou string para lazy loading
    title: str = ""
    description: str = ""
    access_level: RouteAccessLevel = RouteAccessLevel.PUBLIC
    guards: List[Callable] = field(default_factory=list)
    lazy: bool = False
    cache_ttl: int = 300
    meta: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Se componente é string, ativar lazy loading
        if isinstance(self.component, str):
            self.lazy = True

@dataclass
class RouteParams:
    """Parâmetros da rota atual"""
    path: str
    params: Dict[str, str] = field(default_factory=dict)
    query: Dict[str, List[str]] = field(default_factory=dict)
    fragment: str = ""

@dataclass
class NavigationContext:
    """Contexto de navegação"""
    from_route: Optional[str] = None
    to_route: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    user_initiated: bool = True
    timestamp: float = 0.0

# ============================================================================
# ROUTE GUARDS
# ============================================================================

class RouteGuardResult:
    """Resultado de um guard de rota"""
    
    def __init__(self, allowed: bool, redirect_to: Optional[str] = None, message: Optional[str] = None):
        self.allowed = allowed
        self.redirect_to = redirect_to
        self.message = message

class RouteGuards:
    """Coleção de guards de rota padrão"""
    
    @staticmethod
    def require_auth(context: NavigationContext) -> RouteGuardResult:
        """Guard que requer autenticação"""
        # Aqui você verificaria se o usuário está autenticado
        # Por exemplo, verificando um token no estado
        state = me.state(AppState)  # Assumindo que existe um AppState
        
        if hasattr(state, 'user') and state.user is not None:
            return RouteGuardResult(allowed=True)
        else:
            return RouteGuardResult(
                allowed=False,
                redirect_to="/login",
                message="Você precisa estar logado para acessar esta página"
            )
    
    @staticmethod
    def require_admin(context: NavigationContext) -> RouteGuardResult:
        """Guard que requer privilégios de admin"""
        state = me.state(AppState)
        
        if hasattr(state, 'user') and state.user and getattr(state.user, 'is_admin', False):
            return RouteGuardResult(allowed=True)
        else:
            return RouteGuardResult(
                allowed=False,
                redirect_to="/unauthorized",
                message="Você não tem permissão para acessar esta página"
            )
    
    @staticmethod
    def require_premium(context: NavigationContext) -> RouteGuardResult:
        """Guard que requer assinatura premium"""
        state = me.state(AppState)
        
        if hasattr(state, 'user') and state.user and getattr(state.user, 'is_premium', False):
            return RouteGuardResult(allowed=True)
        else:
            return RouteGuardResult(
                allowed=False,
                redirect_to="/upgrade",
                message="Esta funcionalidade requer uma assinatura premium"
            )

# ============================================================================
# ENHANCED ROUTER
# ============================================================================

@me.stateclass
class RouterState:
    """Estado do roteador"""
    current_route: str = "/"
    current_params: RouteParams = RouteParams(path="/")
    navigation_history: List[str] = field(default_factory=list)
    is_loading: bool = False
    last_error: Optional[str] = None
    breadcrumbs: List[Dict[str, str]] = field(default_factory=list)

class EnhancedRouter:
    """Roteador aprimorado com funcionalidades avançadas"""
    
    def __init__(self):
        self.routes: Dict[str, RouteConfig] = {}
        self.route_patterns: Dict[str, re.Pattern] = {}
        self.lazy_loader = get_lazy_loader()
        self.middleware: List[Callable] = []
        self.error_handlers: Dict[int, Callable] = {}
        
        # Configurar handlers de erro padrão
        self.error_handlers[404] = self._default_404_handler
        self.error_handlers[403] = self._default_403_handler
        self.error_handlers[500] = self._default_500_handler
    
    def add_route(self, route_config: RouteConfig) -> None:
        """Adiciona uma rota ao sistema"""
        self.routes[route_config.path] = route_config
        
        # Compilar pattern para rotas com parâmetros
        pattern = self._compile_route_pattern(route_config.path)
        self.route_patterns[route_config.path] = pattern
        
        # Registrar componente lazy se necessário
        if route_config.lazy and isinstance(route_config.component, str):
            self.lazy_loader.register_lazy_content(
                route_config.path,
                lambda: self._load_component(route_config.component)
            )
    
    def _compile_route_pattern(self, path: str) -> re.Pattern:
        """Compila pattern de rota para matching com parâmetros"""
        # Converte /user/:id para /user/(?P<id>[^/]+)
        pattern = re.sub(r':([^/]+)', r'(?P<\1>[^/]+)', path)
        pattern = f"^{pattern}$"
        return re.compile(pattern)
    
    def _load_component(self, component_path: str) -> Callable:
        """Carrega componente dinamicamente"""
        # Implementar carregamento dinâmico baseado no path
        # Por exemplo: "pages.agent_list.agent_list_page"
        module_path, component_name = component_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[component_name])
        return getattr(module, component_name)
    
    def add_middleware(self, middleware: Callable) -> None:
        """Adiciona middleware ao roteador"""
        self.middleware.append(middleware)
    
    def set_error_handler(self, status_code: int, handler: Callable) -> None:
        """Define handler para código de erro específico"""
        self.error_handlers[status_code] = handler
    
    def navigate(self, path: str, params: Optional[Dict[str, Any]] = None, replace: bool = False) -> None:
        """Navega para uma rota específica"""
        state = me.state(RouterState)
        
        # Criar contexto de navegação
        context = NavigationContext(
            from_route=state.current_route,
            to_route=path,
            params=params or {},
            user_initiated=True,
            timestamp=time.time()
        )
        
        # Executar middleware
        for middleware in self.middleware:
            result = middleware(context)
            if result is False:
                return
        
        # Encontrar rota matching
        route_config, route_params = self._match_route(path)
        
        if not route_config:
            self._handle_error(404, f"Rota não encontrada: {path}")
            return
        
        # Executar guards
        guard_result = self._execute_guards(route_config, context)
        if not guard_result.allowed:
            if guard_result.redirect_to:
                self.navigate(guard_result.redirect_to, replace=True)
            else:
                self._handle_error(403, guard_result.message or "Acesso negado")
            return
        
        # Atualizar estado
        state.is_loading = True
        state.last_error = None
        
        # Atualizar histórico
        if not replace:
            state.navigation_history.append(state.current_route)
        
        # Atualizar rota atual
        state.current_route = path
        state.current_params = route_params
        
        # Atualizar breadcrumbs
        self._update_breadcrumbs(path, route_config)
        
        # Renderizar componente
        self._render_route(route_config, route_params)
        
        state.is_loading = False
    
    def _match_route(self, path: str) -> tuple[Optional[RouteConfig], RouteParams]:
        """Encontra rota matching e extrai parâmetros"""
        # Primeiro, tentativa de match exato
        if path in self.routes:
            return self.routes[path], RouteParams(path=path)
        
        # Depois, match com patterns
        for route_path, pattern in self.route_patterns.items():
            match = pattern.match(path)
            if match:
                params = match.groupdict()
                route_params = RouteParams(path=path, params=params)
                return self.routes[route_path], route_params
        
        return None, RouteParams(path=path)
    
    def _execute_guards(self, route_config: RouteConfig, context: NavigationContext) -> RouteGuardResult:
        """Executa guards da rota"""
        # Guards baseados em access level
        if route_config.access_level == RouteAccessLevel.AUTHENTICATED:
            result = RouteGuards.require_auth(context)
            if not result.allowed:
                return result
        
        elif route_config.access_level == RouteAccessLevel.ADMIN:
            result = RouteGuards.require_admin(context)
            if not result.allowed:
                return result
        
        elif route_config.access_level == RouteAccessLevel.PREMIUM:
            result = RouteGuards.require_premium(context)
            if not result.allowed:
                return result
        
        # Guards customizados
        for guard in route_config.guards:
            result = guard(context)
            if not result.allowed:
                return result
        
        return RouteGuardResult(allowed=True)
    
    def _update_breadcrumbs(self, path: str, route_config: RouteConfig) -> None:
        """Atualiza breadcrumbs baseado na rota atual"""
        state = me.state(RouterState)
        
        breadcrumbs = []
        path_parts = path.strip('/').split('/')
        current_path = ''
        
        for part in path_parts:
            if part:
                current_path += f'/{part}'
                
                # Encontrar configuração da rota
                matching_config = None
                for route_path, config in self.routes.items():
                    if route_path == current_path:
                        matching_config = config
                        break
                
                breadcrumbs.append({
                    'path': current_path,
                    'title': matching_config.title if matching_config else part.replace('-', ' ').title(),
                    'active': current_path == path
                })
        
        state.breadcrumbs = breadcrumbs
    
    def _render_route(self, route_config: RouteConfig, route_params: RouteParams) -> None:
        """Renderiza componente da rota"""
        try:
            if route_config.lazy:
                # Carregamento lazy
                component = self.lazy_loader.load_content(route_config.path)
            else:
                component = route_config.component
            
            if callable(component):
                # Aplicar cache se configurado
                if route_config.cache_ttl > 0:
                    component = cached_component(ttl=route_config.cache_ttl)(component)
                
                # Renderizar componente
                component(route_params)
            else:
                self._handle_error(500, f"Componente inválido para rota: {route_config.path}")
        
        except Exception as e:
            self._handle_error(500, f"Erro ao renderizar rota: {str(e)}")
    
    def _handle_error(self, status_code: int, message: str) -> None:
        """Manipula erros do roteador"""
        state = me.state(RouterState)
        state.last_error = message
        state.is_loading = False
        
        if status_code in self.error_handlers:
            self.error_handlers[status_code](message)
    
    def _default_404_handler(self, message: str) -> None:
        """Handler padrão para 404"""
        with me.box(style=me.Style(padding=me.Padding.all(24))):
            me.text("Página não encontrada", style=me.Style(font_size=24, font_weight="bold"))
            me.text(message, style=me.Style(color="red", margin=me.Margin(top=12)))
            me.button("Voltar ao início", on_click=lambda _: self.navigate("/"))
    
    def _default_403_handler(self, message: str) -> None:
        """Handler padrão para 403"""
        with me.box(style=me.Style(padding=me.Padding.all(24))):
            me.text("Acesso negado", style=me.Style(font_size=24, font_weight="bold"))
            me.text(message, style=me.Style(color="red", margin=me.Margin(top=12)))
            me.button("Voltar", on_click=lambda _: self.go_back())
    
    def _default_500_handler(self, message: str) -> None:
        """Handler padrão para 500"""
        with me.box(style=me.Style(padding=me.Padding.all(24))):
            me.text("Erro interno", style=me.Style(font_size=24, font_weight="bold"))
            me.text(message, style=me.Style(color="red", margin=me.Margin(top=12)))
            me.button("Recarregar", on_click=lambda _: self.reload())
    
    def go_back(self) -> None:
        """Volta para a rota anterior"""
        state = me.state(RouterState)
        if state.navigation_history:
            previous_route = state.navigation_history.pop()
            self.navigate(previous_route, replace=True)
    
    def reload(self) -> None:
        """Recarrega a rota atual"""
        state = me.state(RouterState)
        current_route = state.current_route
        self.navigate(current_route, replace=True)

# ============================================================================
# ROUTER UTILITIES
# ============================================================================

def parse_url(url: str) -> RouteParams:
    """Parseia URL e retorna parâmetros"""
    parsed = urlparse(url)
    
    return RouteParams(
        path=parsed.path,
        query=parse_qs(parsed.query),
        fragment=parsed.fragment
    )

def build_url(path: str, params: Optional[Dict[str, str]] = None, query: Optional[Dict[str, str]] = None) -> str:
    """Constrói URL com parâmetros"""
    url = path
    
    # Substituir parâmetros de path
    if params:
        for key, value in params.items():
            url = url.replace(f":{key}", str(value))
    
    # Adicionar query parameters
    if query:
        query_string = "&".join([f"{key}={value}" for key, value in query.items()])
        url += f"?{query_string}"
    
    return url

# ============================================================================
# DECORATORS
# ============================================================================

def route(path: str, **kwargs):
    """Decorator para registrar rotas"""
    def decorator(func):
        route_config = RouteConfig(
            path=path,
            component=func,
            **kwargs
        )
        
        # Registrar rota no roteador global
        global_router.add_route(route_config)
        
        return func
    return decorator

def require_auth(func):
    """Decorator para rotas que requerem autenticação"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Adicionar guard de autenticação
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator para rotas que requerem admin"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Adicionar guard de admin
        return func(*args, **kwargs)
    return wrapper

# ============================================================================
# GLOBAL ROUTER INSTANCE
# ============================================================================

# Instância global do roteador
global_router = EnhancedRouter()

# Funções de conveniência
def navigate(path: str, params: Optional[Dict[str, Any]] = None, replace: bool = False) -> None:
    """Navega para uma rota"""
    global_router.navigate(path, params, replace)

def go_back() -> None:
    """Volta para a rota anterior"""
    global_router.go_back()

def reload() -> None:
    """Recarrega a rota atual"""
    global_router.reload()

def get_router() -> EnhancedRouter:
    """Retorna instância do roteador"""
    return global_router 
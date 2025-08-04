"""
Sistema de validação de formulários aprimorado para Mesop UI
Implementa validação em tempo real, esquemas e feedback visual
"""

import mesop as me
from typing import Dict, Any, Callable, Optional, List, Union, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import re
from datetime import datetime
from functools import wraps
from utils.performance_optimizer import debounce

# ============================================================================
# VALIDATION RULES
# ============================================================================

class ValidationSeverity(Enum):
    """Severidade da validação"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"

@dataclass
class ValidationResult:
    """Resultado da validação"""
    is_valid: bool
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.ERROR
    field_name: str = ""
    
    def __post_init__(self):
        if self.is_valid and self.severity == ValidationSeverity.ERROR:
            self.severity = ValidationSeverity.SUCCESS

class ValidationRule(ABC):
    """Classe base para regras de validação"""
    
    def __init__(self, message: str = "", severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.message = message
        self.severity = severity
    
    @abstractmethod
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Valida o valor"""
        pass

class RequiredRule(ValidationRule):
    """Regra para campos obrigatórios"""
    
    def __init__(self, message: str = "Este campo é obrigatório"):
        super().__init__(message)
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        if value is None or value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
            return ValidationResult(False, self.message, self.severity, field_name)
        return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)

class MinLengthRule(ValidationRule):
    """Regra para comprimento mínimo"""
    
    def __init__(self, min_length: int, message: str = ""):
        self.min_length = min_length
        super().__init__(message or f"Deve ter pelo menos {min_length} caracteres")
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        if value is None:
            return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)
        
        if len(str(value)) < self.min_length:
            return ValidationResult(False, self.message, self.severity, field_name)
        return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)

class MaxLengthRule(ValidationRule):
    """Regra para comprimento máximo"""
    
    def __init__(self, max_length: int, message: str = ""):
        self.max_length = max_length
        super().__init__(message or f"Deve ter no máximo {max_length} caracteres")
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        if value is None:
            return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)
        
        if len(str(value)) > self.max_length:
            return ValidationResult(False, self.message, self.severity, field_name)
        return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)

class EmailRule(ValidationRule):
    """Regra para validação de email"""
    
    def __init__(self, message: str = "Digite um email válido"):
        super().__init__(message)
        self.pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        if value is None or value == "":
            return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)
        
        if not self.pattern.match(str(value)):
            return ValidationResult(False, self.message, self.severity, field_name)
        return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)

class PatternRule(ValidationRule):
    """Regra para validação com regex"""
    
    def __init__(self, pattern: str, message: str = "Formato inválido"):
        super().__init__(message)
        self.pattern = re.compile(pattern)
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        if value is None or value == "":
            return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)
        
        if not self.pattern.match(str(value)):
            return ValidationResult(False, self.message, self.severity, field_name)
        return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)

class NumericRule(ValidationRule):
    """Regra para validação numérica"""
    
    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None, 
                 message: str = ""):
        self.min_value = min_value
        self.max_value = max_value
        
        if not message:
            if min_value is not None and max_value is not None:
                message = f"Deve estar entre {min_value} e {max_value}"
            elif min_value is not None:
                message = f"Deve ser maior ou igual a {min_value}"
            elif max_value is not None:
                message = f"Deve ser menor ou igual a {max_value}"
            else:
                message = "Deve ser um número válido"
        
        super().__init__(message)
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        if value is None or value == "":
            return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)
        
        try:
            num_value = float(value)
            
            if self.min_value is not None and num_value < self.min_value:
                return ValidationResult(False, self.message, self.severity, field_name)
            
            if self.max_value is not None and num_value > self.max_value:
                return ValidationResult(False, self.message, self.severity, field_name)
            
            return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)
        
        except (ValueError, TypeError):
            return ValidationResult(False, "Deve ser um número válido", self.severity, field_name)

class CustomRule(ValidationRule):
    """Regra personalizada"""
    
    def __init__(self, validator_func: Callable[[Any], bool], message: str = "Valor inválido"):
        super().__init__(message)
        self.validator_func = validator_func
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        try:
            if self.validator_func(value):
                return ValidationResult(True, "", ValidationSeverity.SUCCESS, field_name)
            else:
                return ValidationResult(False, self.message, self.severity, field_name)
        except Exception:
            return ValidationResult(False, self.message, self.severity, field_name)

# ============================================================================
# FORM FIELD CONFIGURATION
# ============================================================================

@dataclass
class FieldConfig:
    """Configuração de um campo do formulário"""
    name: str
    label: str = ""
    placeholder: str = ""
    help_text: str = ""
    field_type: str = "text"
    rules: List[ValidationRule] = field(default_factory=list)
    required: bool = False
    disabled: bool = False
    readonly: bool = False
    options: List[Dict[str, Any]] = field(default_factory=list)  # Para select, radio, etc.
    
    def __post_init__(self):
        if self.required and not any(isinstance(rule, RequiredRule) for rule in self.rules):
            self.rules.insert(0, RequiredRule())
        
        if not self.label:
            self.label = self.name.replace('_', ' ').title()

# ============================================================================
# FORM STATE MANAGEMENT
# ============================================================================

@me.stateclass
class FormState:
    """Estado do formulário"""
    values: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, List[ValidationResult]] = field(default_factory=dict)
    warnings: Dict[str, List[ValidationResult]] = field(default_factory=dict)
    touched: Dict[str, bool] = field(default_factory=dict)
    dirty: Dict[str, bool] = field(default_factory=dict)
    is_submitting: bool = False
    is_valid: bool = True
    submit_attempted: bool = False
    
    def set_field_value(self, field_name: str, value: Any) -> None:
        """Define valor do campo"""
        self.values[field_name] = value
        self.touched[field_name] = True
        self.dirty[field_name] = True
    
    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """Obtém valor do campo"""
        return self.values.get(field_name, default)
    
    def has_errors(self, field_name: Optional[str] = None) -> bool:
        """Verifica se há erros"""
        if field_name:
            return field_name in self.errors and len(self.errors[field_name]) > 0
        return any(len(errors) > 0 for errors in self.errors.values())
    
    def get_field_errors(self, field_name: str) -> List[ValidationResult]:
        """Obtém erros do campo"""
        return self.errors.get(field_name, [])
    
    def clear_field_errors(self, field_name: str) -> None:
        """Limpa erros do campo"""
        if field_name in self.errors:
            self.errors[field_name] = []
    
    def clear_all_errors(self) -> None:
        """Limpa todos os erros"""
        self.errors.clear()
        self.warnings.clear()

# ============================================================================
# ENHANCED FORM VALIDATOR
# ============================================================================

class FormValidator:
    """Validador de formulários com funcionalidades avançadas"""
    
    def __init__(self, fields: List[FieldConfig]):
        self.fields = {field.name: field for field in fields}
        self.field_dependencies: Dict[str, List[str]] = {}
        self.cross_field_rules: List[Callable] = []
    
    def add_field_dependency(self, field_name: str, depends_on: List[str]) -> None:
        """Adiciona dependência entre campos"""
        self.field_dependencies[field_name] = depends_on
    
    def add_cross_field_rule(self, rule: Callable) -> None:
        """Adiciona regra que valida múltiplos campos"""
        self.cross_field_rules.append(rule)
    
    def validate_field(self, field_name: str, value: Any, form_state: FormState) -> List[ValidationResult]:
        """Valida um campo específico"""
        if field_name not in self.fields:
            return []
        
        field_config = self.fields[field_name]
        results = []
        
        # Validar regras individuais
        for rule in field_config.rules:
            result = rule.validate(value, field_name)
            if not result.is_valid or result.severity != ValidationSeverity.SUCCESS:
                results.append(result)
        
        return results
    
    def validate_all_fields(self, form_state: FormState) -> Dict[str, List[ValidationResult]]:
        """Valida todos os campos"""
        all_errors = {}
        all_warnings = {}
        
        # Validar campos individuais
        for field_name, field_config in self.fields.items():
            value = form_state.get_field_value(field_name)
            results = self.validate_field(field_name, value, form_state)
            
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
            
            if errors:
                all_errors[field_name] = errors
            if warnings:
                all_warnings[field_name] = warnings
        
        # Validar regras cross-field
        for rule in self.cross_field_rules:
            try:
                result = rule(form_state)
                if isinstance(result, list):
                    for r in result:
                        if r.severity == ValidationSeverity.ERROR:
                            if r.field_name not in all_errors:
                                all_errors[r.field_name] = []
                            all_errors[r.field_name].append(r)
                        elif r.severity == ValidationSeverity.WARNING:
                            if r.field_name not in all_warnings:
                                all_warnings[r.field_name] = []
                            all_warnings[r.field_name].append(r)
                elif isinstance(result, ValidationResult):
                    if result.severity == ValidationSeverity.ERROR:
                        if result.field_name not in all_errors:
                            all_errors[result.field_name] = []
                        all_errors[result.field_name].append(result)
                    elif result.severity == ValidationSeverity.WARNING:
                        if result.field_name not in all_warnings:
                            all_warnings[result.field_name] = []
                        all_warnings[result.field_name].append(result)
            except Exception as e:
                # Erro na regra cross-field
                error_result = ValidationResult(
                    False, 
                    f"Erro na validação: {str(e)}", 
                    ValidationSeverity.ERROR
                )
                if "form" not in all_errors:
                    all_errors["form"] = []
                all_errors["form"].append(error_result)
        
        # Atualizar estado do formulário
        form_state.errors = all_errors
        form_state.warnings = all_warnings
        form_state.is_valid = len(all_errors) == 0
        
        return all_errors
    
    def validate_dependencies(self, field_name: str, form_state: FormState) -> None:
        """Valida campos dependentes"""
        if field_name not in self.field_dependencies:
            return
        
        # Revalidar campos dependentes
        for dependent_field in self.field_dependencies[field_name]:
            if dependent_field in form_state.values:
                value = form_state.get_field_value(dependent_field)
                results = self.validate_field(dependent_field, value, form_state)
                
                errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
                warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
                
                if errors:
                    form_state.errors[dependent_field] = errors
                else:
                    form_state.clear_field_errors(dependent_field)
                
                if warnings:
                    form_state.warnings[dependent_field] = warnings

# ============================================================================
# FORM COMPONENTS
# ============================================================================

class EnhancedFormField:
    """Campo de formulário aprimorado"""
    
    @staticmethod
    def render_field(field_config: FieldConfig, form_state: FormState, validator: FormValidator) -> None:
        """Renderiza um campo do formulário"""
        field_value = form_state.get_field_value(field_config.name, "")
        has_errors = form_state.has_errors(field_config.name)
        field_errors = form_state.get_field_errors(field_config.name)
        
        with me.box(style=me.Style(margin=me.Margin(bottom=16))):
            # Label
            if field_config.label:
                label_style = me.Style(
                    font_weight="500",
                    margin=me.Margin(bottom=4),
                    color="red" if has_errors else "inherit"
                )
                me.text(field_config.label, style=label_style)
            
            # Campo de entrada
            input_style = me.Style(
                width="100%",
                padding=me.Padding.all(8),
                border=me.Border.all(
                    me.BorderSide(
                        color="red" if has_errors else "#ccc",
                        width=1,
                        style="solid"
                    )
                ),
                border_radius=4
            )
            
            if field_config.field_type == "text":
                me.input(
                    value=str(field_value),
                    placeholder=field_config.placeholder,
                    disabled=field_config.disabled,
                    on_input=lambda e: EnhancedFormField._handle_input(
                        e, field_config, form_state, validator
                    ),
                    style=input_style
                )
            
            elif field_config.field_type == "textarea":
                me.textarea(
                    value=str(field_value),
                    placeholder=field_config.placeholder,
                    disabled=field_config.disabled,
                    on_input=lambda e: EnhancedFormField._handle_input(
                        e, field_config, form_state, validator
                    ),
                    style=input_style
                )
            
            elif field_config.field_type == "select":
                me.select(
                    options=[
                        me.SelectOption(label=opt.get("label", ""), value=opt.get("value", ""))
                        for opt in field_config.options
                    ],
                    value=str(field_value),
                    disabled=field_config.disabled,
                    on_selection_change=lambda e: EnhancedFormField._handle_selection(
                        e, field_config, form_state, validator
                    ),
                    style=input_style
                )
            
            elif field_config.field_type == "checkbox":
                me.checkbox(
                    checked=bool(field_value),
                    disabled=field_config.disabled,
                    on_change=lambda e: EnhancedFormField._handle_checkbox(
                        e, field_config, form_state, validator
                    )
                )
            
            # Texto de ajuda
            if field_config.help_text:
                me.text(
                    field_config.help_text,
                    style=me.Style(
                        font_size=12,
                        color="#666",
                        margin=me.Margin(top=4)
                    )
                )
            
            # Erros
            if has_errors:
                for error in field_errors:
                    error_color = {
                        ValidationSeverity.ERROR: "red",
                        ValidationSeverity.WARNING: "orange",
                        ValidationSeverity.INFO: "blue"
                    }.get(error.severity, "red")
                    
                    me.text(
                        error.message,
                        style=me.Style(
                            font_size=12,
                            color=error_color,
                            margin=me.Margin(top=4)
                        )
                    )
    
    @staticmethod
    @debounce(0.5)
    def _handle_input(event, field_config: FieldConfig, form_state: FormState, validator: FormValidator) -> None:
        """Manipula entrada de texto"""
        form_state.set_field_value(field_config.name, event.value)
        
        # Validar campo em tempo real
        validator.validate_field(field_config.name, event.value, form_state)
        
        # Validar dependências
        validator.validate_dependencies(field_config.name, form_state)
    
    @staticmethod
    def _handle_selection(event, field_config: FieldConfig, form_state: FormState, validator: FormValidator) -> None:
        """Manipula seleção"""
        form_state.set_field_value(field_config.name, event.value)
        validator.validate_field(field_config.name, event.value, form_state)
        validator.validate_dependencies(field_config.name, form_state)
    
    @staticmethod
    def _handle_checkbox(event, field_config: FieldConfig, form_state: FormState, validator: FormValidator) -> None:
        """Manipula checkbox"""
        form_state.set_field_value(field_config.name, event.checked)
        validator.validate_field(field_config.name, event.checked, form_state)
        validator.validate_dependencies(field_config.name, form_state)

# ============================================================================
# ENHANCED FORM COMPONENT
# ============================================================================

@me.component
def enhanced_form(
    fields: List[FieldConfig],
    on_submit: Callable[[Dict[str, Any]], None],
    on_cancel: Optional[Callable] = None,
    title: str = "",
    description: str = "",
    submit_text: str = "Enviar",
    cancel_text: str = "Cancelar",
    show_cancel: bool = True
) -> None:
    """Componente de formulário aprimorado"""
    form_state = me.state(FormState)
    validator = FormValidator(fields)
    
    with me.box(style=me.Style(max_width="600px", margin=me.Margin.symmetric(horizontal="auto"))):
        # Título e descrição
        if title:
            me.text(title, style=me.Style(font_size=24, font_weight="bold", margin=me.Margin(bottom=8)))
        
        if description:
            me.text(description, style=me.Style(margin=me.Margin(bottom=24)))
        
        # Renderizar campos
        for field_config in fields:
            EnhancedFormField.render_field(field_config, form_state, validator)
        
        # Botões
        with me.box(style=me.Style(display="flex", justify_content="flex-end", gap=12, margin=me.Margin(top=24))):
            if show_cancel and on_cancel:
                me.button(
                    cancel_text,
                    on_click=lambda _: on_cancel(),
                    style=me.Style(
                        background_color="transparent",
                        color="#666",
                        border=me.Border.all(me.BorderSide(color="#ccc", width=1, style="solid"))
                    )
                )
            
            me.button(
                submit_text,
                disabled=form_state.is_submitting,
                on_click=lambda _: _handle_submit(form_state, validator, on_submit),
                style=me.Style(
                    background_color="#007bff",
                    color="white",
                    border=me.Border.all(me.BorderSide(color="#007bff", width=1, style="solid"))
                )
            )

def _handle_submit(form_state: FormState, validator: FormValidator, on_submit: Callable) -> None:
    """Manipula envio do formulário"""
    form_state.is_submitting = True
    form_state.submit_attempted = True
    
    # Validar todos os campos
    validator.validate_all_fields(form_state)
    
    if form_state.is_valid:
        try:
            on_submit(form_state.values)
        except Exception as e:
            # Adicionar erro de envio
            form_state.errors["form"] = [ValidationResult(
                False, 
                f"Erro ao enviar formulário: {str(e)}", 
                ValidationSeverity.ERROR, 
                "form"
            )]
            form_state.is_valid = False
    
    form_state.is_submitting = False

# ============================================================================
# COMMON VALIDATION SCHEMAS
# ============================================================================

class CommonSchemas:
    """Esquemas de validação comuns"""
    
    @staticmethod
    def login_form() -> List[FieldConfig]:
        """Formulário de login"""
        return [
            FieldConfig(
                name="email",
                label="Email",
                field_type="text",
                placeholder="seu@email.com",
                required=True,
                rules=[RequiredRule(), EmailRule()]
            ),
            FieldConfig(
                name="password",
                label="Senha",
                field_type="password",
                placeholder="••••••••",
                required=True,
                rules=[RequiredRule(), MinLengthRule(8)]
            )
        ]
    
    @staticmethod
    def user_profile_form() -> List[FieldConfig]:
        """Formulário de perfil do usuário"""
        return [
            FieldConfig(
                name="name",
                label="Nome Completo",
                field_type="text",
                placeholder="Seu nome completo",
                required=True,
                rules=[RequiredRule(), MinLengthRule(2), MaxLengthRule(100)]
            ),
            FieldConfig(
                name="email",
                label="Email",
                field_type="text",
                placeholder="seu@email.com",
                required=True,
                rules=[RequiredRule(), EmailRule()]
            ),
            FieldConfig(
                name="phone",
                label="Telefone",
                field_type="text",
                placeholder="(11) 99999-9999",
                rules=[PatternRule(r'^\(\d{2}\) \d{4,5}-\d{4}$', "Formato: (11) 99999-9999")]
            ),
            FieldConfig(
                name="bio",
                label="Biografia",
                field_type="textarea",
                placeholder="Conte um pouco sobre você...",
                rules=[MaxLengthRule(500)]
            )
        ]
    
    @staticmethod
    def agent_config_form() -> List[FieldConfig]:
        """Formulário de configuração de agente"""
        return [
            FieldConfig(
                name="name",
                label="Nome do Agente",
                field_type="text",
                placeholder="Nome do seu agente",
                required=True,
                rules=[RequiredRule(), MinLengthRule(3), MaxLengthRule(50)]
            ),
            FieldConfig(
                name="description",
                label="Descrição",
                field_type="textarea",
                placeholder="Descreva a função do agente...",
                required=True,
                rules=[RequiredRule(), MinLengthRule(10), MaxLengthRule(1000)]
            ),
            FieldConfig(
                name="model",
                label="Modelo",
                field_type="select",
                required=True,
                options=[
                    {"label": "GPT-4", "value": "gpt-4"},
                    {"label": "GPT-3.5 Turbo", "value": "gpt-3.5-turbo"},
                    {"label": "Claude", "value": "claude"}
                ],
                rules=[RequiredRule()]
            ),
            FieldConfig(
                name="max_tokens",
                label="Máximo de Tokens",
                field_type="text",
                placeholder="2048",
                rules=[NumericRule(min_value=100, max_value=8192)]
            ),
            FieldConfig(
                name="temperature",
                label="Temperatura",
                field_type="text",
                placeholder="0.7",
                rules=[NumericRule(min_value=0.0, max_value=2.0)]
            ),
            FieldConfig(
                name="enabled",
                label="Agente Ativo",
                field_type="checkbox"
            )
        ] 
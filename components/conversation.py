import uuid

import mesop as me

from a2a.types import Message, Part, Role, TextPart
from state.host_agent_service import (
    ListConversations,
    SendMessage,
    convert_message_to_state,
)
from state.state import AppState, StateMessage

from .chat_bubble import chat_bubble
from .emoji_chat import emoji_chat_bubble, process_emoji_in_text, get_emoji_help_text
from .form_render import form_sent, is_form, render_form


def get_mesop_docs_response() -> str:
    """Retorna informações sobre a documentação do Mesop"""
    return """
## 📚 Documentação do Mesop

**Mesop** é um framework Python para construir aplicações web interativas usando apenas Python, sem necessidade de HTML, CSS ou JavaScript.

### 🔗 Links Úteis:
- **Site Oficial**: [https://google.github.io/mesop/](https://google.github.io/mesop/)
- **GitHub**: [https://github.com/google/mesop](https://github.com/google/mesop)
- **Documentação**: [https://google.github.io/mesop/getting_started/](https://google.github.io/mesop/getting_started/)

### 🚀 Funcionalidades Principais:
- **Componentes Reativos**: Criação de interfaces usando decoradores `@me.component`
- **Estado Gerenciado**: Sistema de estado com `@me.stateclass` e `me.state()`
- **Eventos Interativos**: Manipulação de eventos como cliques, inputs, etc.
- **Theming**: Suporte a temas claro/escuro
- **Segurança**: Políticas de segurança configuráveis

### 🛠️ Componentes Utilizados nesta UI:
- `me.box()` - Containers e layouts
- `me.text()` - Textos e títulos
- `me.input()` - Campos de entrada
- `me.button()` - Botões interativos
- `me.markdown()` - Renderização de markdown
- `me.image()` - Exibição de imagens
- `me.table()` - Tabelas de dados
- `me.sidenav()` - Navegação lateral

### 📖 Exemplos de Uso:
```python
import mesop as me

@me.stateclass
class State:
    message: str = ""

@me.component
def app():
    state = me.state(State)
    me.input(label="Digite algo", on_blur=update_message)
    me.text(f"Mensagem: {state.message}")

def update_message(e: me.InputBlurEvent):
    state = me.state(State)
    state.message = e.value
```

**💡 Dica**: Esta UI foi construída inteiramente com Mesop! Explore os arquivos em `ui/components/` para ver exemplos práticos de implementação.
"""

def is_mesop_docs_command(message: str) -> bool:
    """Verifica se a mensagem é um comando para mostrar documentação do Mesop"""
    return message.strip().lower().startswith("@mesop docs")


def is_emoji_help_command(message: str) -> bool:
    """Verifica se a mensagem é um comando para mostrar ajuda sobre emojis"""
    return message.strip().lower().startswith("@emoji")


async def handle_mesop_docs_command(conversation_id: str, message_id: str):
    """Processa comando @Mesop docs"""
    app_state = me.state(AppState)
    
    # Criar mensagem de resposta com documentação
    docs_response = get_mesop_docs_response()
    
    # Adicionar resposta ao estado
    response_message = StateMessage(
        message_id=f"mesop-docs-{message_id}",
        role=Role.agent,
        content=[(docs_response, 'text/plain')],
    )
    
    if not app_state.messages:
        app_state.messages = []
    app_state.messages.append(response_message)
    
    # Atualizar conversa
    conversation = next(
        filter(
            lambda x: x.conversation_id == conversation_id,
            app_state.conversations,
        ),
        None,
    )
    if conversation:
        conversation.message_ids.append(response_message.message_id)


async def handle_emoji_help_command(conversation_id: str, message_id: str):
    """Processa comando @emoji help"""
    app_state = me.state(AppState)
    
    # Criar mensagem de resposta com ajuda sobre emojis
    emoji_help_response = get_emoji_help_text()
    
    # Adicionar resposta ao estado
    response_message = StateMessage(
        message_id=f"emoji-help-{message_id}",
        role=Role.agent,
        content=[(emoji_help_response, 'text/plain')],
    )
    
    if not app_state.messages:
        app_state.messages = []
    app_state.messages.append(response_message)
    
    # Atualizar conversa
    conversation = next(
        filter(
            lambda x: x.conversation_id == conversation_id,
            app_state.conversations,
        ),
        None,
    )
    if conversation:
        conversation.message_ids.append(response_message.message_id)


@me.stateclass
class PageState:
    """Local Page State"""

    conversation_id: str = ''
    message_content: str = ''


def on_blur(e: me.InputBlurEvent):
    """Input blur handler"""
    state = me.state(PageState)
    state.message_content = e.value


async def send_message(message: str, message_id: str = ''):
    state = me.state(PageState)
    app_state = me.state(AppState)
    
    # Verificar se é um comando @Mesop docs
    if is_mesop_docs_command(message):
        # Adicionar mensagem do usuário
        user_message = StateMessage(
            message_id=message_id,
            role=Role.user,
            content=[(message, 'text/plain')],
        )
        if not app_state.messages:
            app_state.messages = []
        app_state.messages.append(user_message)
        
        # Processar comando e adicionar resposta
        await handle_mesop_docs_command(state.conversation_id, message_id)
        return
    
    # Verificar se é um comando @emoji help
    if is_emoji_help_command(message):
        # Adicionar mensagem do usuário
        user_message = StateMessage(
            message_id=message_id,
            role=Role.user,
            content=[(message, 'text/plain')],
        )
        if not app_state.messages:
            app_state.messages = []
        app_state.messages.append(user_message)
        
        # Processar comando e adicionar resposta
        await handle_emoji_help_command(state.conversation_id, message_id)
        return
    
    # Processar mensagem normalmente
    c = next(
        (
            x
            for x in await ListConversations()
            if x.conversation_id == state.conversation_id
        ),
        None,
    )
    if not c:
        print('Conversation id ', state.conversation_id, ' not found')
    request = Message(
        messageId=message_id,
        contextId=state.conversation_id,
        role=Role.user,
        parts=[Part(root=TextPart(text=message))],
    )
    # Add message to state until refresh replaces it.
    state_message = convert_message_to_state(request)
    if not app_state.messages:
        app_state.messages = []
    app_state.messages.append(state_message)
    conversation = next(
        filter(
            lambda x: c and x.conversation_id == c.conversation_id,
            app_state.conversations,
        ),
        None,
    )
    if conversation:
        conversation.message_ids.append(state_message.message_id)
    await SendMessage(request)


async def send_message_enter(e: me.InputEnterEvent):  # pylint: disable=unused-argument
    """Send message handler"""
    yield
    state = me.state(PageState)
    state.message_content = e.value
    app_state = me.state(AppState)
    message_id = str(uuid.uuid4())
    app_state.background_tasks[message_id] = ''
    yield
    await send_message(state.message_content, message_id)
    yield


async def send_message_button(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Send message button handler"""
    yield
    state = me.state(PageState)
    app_state = me.state(AppState)
    message_id = str(uuid.uuid4())
    app_state.background_tasks[message_id] = ''
    await send_message(state.message_content, message_id)
    yield


@me.component
def conversation():
    """Conversation component with emoji support"""
    page_state = me.state(PageState)
    app_state = me.state(AppState)
    if 'conversation_id' in me.query_params:
        page_state.conversation_id = me.query_params['conversation_id']
        app_state.current_conversation_id = page_state.conversation_id
    with me.box(
        style=me.Style(
            display='flex',
            justify_content='space-between',
            flex_direction='column',
        )
    ):
        for message in app_state.messages:
            if is_form(message):
                render_form(message, app_state)
            elif form_sent(message, app_state):
                emoji_chat_bubble(
                    StateMessage(
                        message_id=message.message_id,
                        role=message.role,
                        content=[('Form submitted', 'text/plain')],
                    ),
                    message.message_id,
                )
            else:
                # Usar o componente com suporte a emoji
                emoji_chat_bubble(message, message.message_id)

        with me.box(
            style=me.Style(
                display='flex',
                flex_direction='row',
                gap=5,
                align_items='center',
                min_width=500,
                width='100%',
            )
        ):
            me.input(
                label='How can I help you?',
                on_blur=on_blur,
                on_enter=send_message_enter,
                style=me.Style(min_width='80vw'),
                placeholder='Digite sua mensagem, @Mesop docs para documentação, ou @emoji help para ajuda com emojis...',
            )
            with me.content_button(
                type='flat',
                on_click=send_message_button,
            ):
                me.icon(icon='send')

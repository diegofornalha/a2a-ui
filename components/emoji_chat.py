"""
Componente de Chat com Suporte a Emoji
Usando a biblioteca emoji para renderização e processamento de emojis
"""

import emoji
import mesop as me
from typing import List, Tuple, Any

from state.state import AppState, StateMessage


def process_emoji_in_text(text: str) -> str:
    """
    Processa emojis no texto usando a biblioteca emoji
    
    Args:
        text: Texto que pode conter códigos de emoji como :thumbs_up:
        
    Returns:
        Texto com emojis renderizados
    """
    try:
        # Converte códigos de emoji para emojis reais
        processed_text = emoji.emojize(text, language='alias')
        return processed_text
    except Exception as e:
        print(f"Erro ao processar emoji: {e}")
        return text


def extract_emoji_info(text: str) -> dict[str, Any]:
    """
    Extrai informações sobre emojis no texto
    
    Args:
        text: Texto para analisar
        
    Returns:
        Dicionário com informações sobre emojis encontrados
    """
    try:
        emoji_list = emoji.emoji_list(text)
        distinct_emojis = emoji.distinct_emoji_list(text)
        emoji_count = emoji.emoji_count(text)
        
        return {
            'total_emojis': emoji_count,
            'unique_emojis': len(distinct_emojis),
            'emoji_list': emoji_list,
            'distinct_emojis': distinct_emojis,
            'has_emoji': emoji_count > 0
        }
    except Exception as e:
        print(f"Erro ao extrair informações de emoji: {e}")
        return {
            'total_emojis': 0,
            'unique_emojis': 0,
            'emoji_list': [],
            'distinct_emojis': [],
            'has_emoji': False
        }


@me.component
def emoji_chat_bubble(message: StateMessage, key: str):
    """
    Componente de chat bubble com suporte a emoji
    """
    app_state = me.state(AppState)
    show_progress_bar = (
        message.message_id in app_state.background_tasks
        or message.message_id in app_state.message_aliases.values()
    )
    progress_text = ''
    if show_progress_bar:
        progress_text = app_state.background_tasks[message.message_id]
    
    if not message.content:
        print('No message content')
        return
    
    for pair in message.content:
        emoji_chat_box(
            pair[0],
            pair[1],
            message.role,
            key,
            progress_bar=show_progress_bar,
            progress_text=progress_text,
        )


def emoji_chat_box(
    content: str,
    media_type: str,
    role: str,
    key: str,
    progress_bar: bool,
    progress_text: str,
):
    """
    Renderiza uma caixa de chat com suporte a emoji
    """
    # Processa emojis no conteúdo
    processed_content = process_emoji_in_text(content)
    emoji_info = extract_emoji_info(processed_content)
    
    with me.box(
        style=me.Style(
            display='flex',
            justify_content=('space-between' if role == 'agent' else 'end'),
            min_width=500,
        ),
        key=key,
    ):
        with me.box(
            style=me.Style(display='flex', flex_direction='column', gap=5)
        ):
            if media_type == 'image/png':
                if '/message/file' not in content:
                    content = 'data:image/png;base64,' + content
                me.image(
                    src=content,
                    style=me.Style(
                        width='50%',
                        object_fit='contain',
                    ),
                )
            else:
                # Renderiza o conteúdo com emojis
                me.markdown(
                    processed_content,
                    style=me.Style(
                        font_family='Google Sans',
                        box_shadow=(
                            '0 1px 2px 0 rgba(60, 64, 67, 0.3), '
                            '0 1px 3px 1px rgba(60, 64, 67, 0.15)'
                        ),
                        padding=me.Padding(top=1, left=15, right=15, bottom=1),
                        margin=me.Margin(top=5, left=0, right=0, bottom=5),
                        background=(
                            me.theme_var('primary-container')
                            if role == 'user'
                            else me.theme_var('secondary-container')
                        ),
                        border_radius=15,
                    ),
                )
                
                # Mostra informações de emoji se houver
                if emoji_info['has_emoji']:
                    with me.box(
                        style=me.Style(
                            display='flex',
                            gap=8,
                            margin=me.Margin(top=5),
                            padding=me.Padding(all=8),
                            background=me.theme_var('surface-container'),
                            border_radius=8,
                        )
                    ):
                        me.text(
                            f"😊 {emoji_info['total_emojis']} emoji(s)",
                            style=me.Style(
                                font_size=12,
                                color=me.theme_var('on-surface-variant'),
                            )
                        )
                        
                        # Mostra emojis únicos encontrados
                        if emoji_info['distinct_emojis']:
                            emoji_display = ' '.join(emoji_info['distinct_emojis'][:5])
                            if len(emoji_info['distinct_emojis']) > 5:
                                emoji_display += '...'
                            
                            me.text(
                                f"Encontrados: {emoji_display}",
                                style=me.Style(
                                    font_size=12,
                                    color=me.theme_var('on-surface-variant'),
                                )
                            )
    
    if progress_bar:
        with me.box(
            style=me.Style(
                display='flex',
                justify_content=('space-between' if role == 'user' else 'end'),
                min_width=500,
            ),
            key=key,
        ):
            with me.box(
                style=me.Style(display='flex', flex_direction='column', gap=5)
            ):
                with me.box(
                    style=me.Style(
                        font_family='Google Sans',
                        box_shadow=(
                            '0 1px 2px 0 rgba(60, 64, 67, 0.3), '
                            '0 1px 3px 1px rgba(60, 64, 67, 0.15)'
                        ),
                        padding=me.Padding(top=1, left=15, right=15, bottom=1),
                        margin=me.Margin(top=5, left=0, right=0, bottom=5),
                        background=(
                            me.theme_var('primary-container')
                            if role == 'agent'
                            else me.theme_var('secondary-container')
                        ),
                        border_radius=15,
                    ),
                ):
                    if not progress_text:
                        progress_text = 'Working...'
                    me.text(
                        progress_text,
                        style=me.Style(
                            padding=me.Padding(
                                top=1, left=15, right=15, bottom=1
                            ),
                            margin=me.Margin(top=5, left=0, right=0, bottom=5),
                        ),
                    )
                    me.progress_bar(color='accent')


def create_emoji_response_template() -> str:
    """
    Cria um template de resposta com emojis para o Hello World Agent
    """
    return """
## 🌟 Resposta do Hello World Agent

### 📋 Informações da Resposta:
- **Status**: ✅ Sucesso
- **Tipo**: SUPER HELLO
- **Emoji Count**: 2
- **Enthusiasm Level**: SUPER

### 💬 Mensagem:
"You asked for SUPER, you got SUPER!" (Você pediu SUPER, você conseguiu SUPER!)

### 🎯 Detalhes Adicionais:
- **emoji_count**: 2
- **enthusiasm_level**: SUPER
- **response_type**: super_hello_world
- **timestamp**: {timestamp}

### 🚀 Funcionalidades Disponíveis:
- `hello_world` - Resposta básica
- `super_hello_world` - Resposta SUPER com emojis
- `emoji_analysis` - Análise de emojis na resposta

### 💡 Como Usar:
1. Digite "hello" para resposta básica
2. Digite "super hello" para resposta SUPER
3. Digite "@emoji" para análise de emojis

**🎉 O agente está funcionando perfeitamente com suporte a emoji!**
"""


def get_emoji_help_text() -> str:
    """
    Retorna texto de ajuda sobre emojis
    """
    return """
## 😊 Suporte a Emoji no Chat

### 🎯 Como Usar:
- Digite `:thumbs_up:` → 👍
- Digite `:heart:` → ❤️
- Digite `:smile:` → 😊
- Digite `:rocket:` → 🚀

### 📝 Exemplos:
- "Python é :thumbs_up:" → "Python é 👍"
- "Eu :heart: Mesop!" → "Eu ❤️ Mesop!"
- "Vamos :rocket: para o espaço!" → "Vamos 🚀 para o espaço!"

### 🔧 Comandos Especiais:
- `@emoji help` - Mostra esta ajuda
- `@emoji list` - Lista emojis disponíveis
- `@emoji count` - Conta emojis na mensagem

### 💡 Dica:
Os emojis são automaticamente processados e renderizados no chat!
""" 
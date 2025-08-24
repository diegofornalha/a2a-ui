#!/usr/bin/env python3
"""
Exemplo REAL do Claude Code SDK
Usando as classes TextBlock, UserMessage e AssistantMessage
"""

from claude_code_sdk import TextBlock, UserMessage, AssistantMessage
import json

print("=" * 60)
print("🚀 CLAUDE CODE SDK - Exemplo Real")
print(f"Versão do SDK: 0.0.20")
print("=" * 60)

# 1. Criando TextBlocks
print("\n📝 1. TextBlock - Bloco de texto simples")
print("-" * 40)

text_block = TextBlock(
    text="Olá! Este é um bloco de texto do Claude SDK.",
    type="text"
)
print(f"TextBlock criado: {text_block}")
print(f"  - Texto: {text_block.text}")
print(f"  - Tipo: {text_block.type}")

# 2. Criando UserMessage
print("\n👤 2. UserMessage - Mensagens do usuário")
print("-" * 40)

# Mensagem simples com string
user_msg_simple = UserMessage(
    content="Qual é a capital do Brasil?"
)
print(f"UserMessage simples: {user_msg_simple}")

# Mensagem com TextBlock
user_msg_block = UserMessage(
    content=[
        TextBlock(text="Explique o seguinte código Python:", type="text"),
        TextBlock(text="def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)", type="text")
    ]
)
print(f"UserMessage com blocos: {user_msg_block}")

# 3. Criando AssistantMessage
print("\n🤖 3. AssistantMessage - Respostas do Claude")
print("-" * 40)

assistant_msg = AssistantMessage(
    content="A capital do Brasil é Brasília, localizada no Distrito Federal."
)
print(f"AssistantMessage: {assistant_msg}")

# Resposta complexa com múltiplos blocos
assistant_complex = AssistantMessage(
    content=[
        TextBlock(text="Este código implementa a sequência de Fibonacci:", type="text"),
        TextBlock(text="• Caso base: retorna n se n <= 1", type="text"),
        TextBlock(text="• Caso recursivo: soma dos dois números anteriores", type="text"),
        TextBlock(text="• Complexidade: O(2^n) - não otimizado", type="text")
    ]
)
print(f"AssistantMessage complexa: {assistant_complex}")

# 4. Simulando uma conversa completa
print("\n💬 4. Conversa Completa")
print("-" * 40)

conversa = []

# Primeira interação
conversa.append(UserMessage("O que é Python?"))
conversa.append(AssistantMessage(
    "Python é uma linguagem de programação de alto nível, interpretada e de propósito geral. "
    "É conhecida por sua sintaxe clara e legibilidade."
))

# Segunda interação
conversa.append(UserMessage("Mostre um exemplo de lista"))
conversa.append(AssistantMessage([
    TextBlock("Aqui está um exemplo de lista em Python:", type="text"),
    TextBlock("numeros = [1, 2, 3, 4, 5]\nfrutas = ['maçã', 'banana', 'laranja']", type="text"),
    TextBlock("Você pode acessar elementos usando índices: frutas[0] retorna 'maçã'", type="text")
]))

# Exibindo a conversa
print("\n📖 Histórico da Conversa:")
for i, msg in enumerate(conversa, 1):
    if isinstance(msg, UserMessage):
        role = "👤 Usuário"
        icon = "❓"
    else:
        role = "🤖 Claude"
        icon = "💡"
    
    print(f"\n{icon} Mensagem {i} - {role}:")
    
    # Tratando content como string ou lista
    if isinstance(msg.content, str):
        print(f"   {msg.content}")
    elif isinstance(msg.content, list):
        for block in msg.content:
            if hasattr(block, 'text'):
                print(f"   • {block.text}")
            else:
                print(f"   • {block}")

# 5. Convertendo para formato de API
print("\n🔄 5. Formato para API")
print("-" * 40)

def message_to_dict(msg):
    """Converte mensagem para formato de dicionário"""
    role = "user" if isinstance(msg, UserMessage) else "assistant"
    
    if isinstance(msg.content, str):
        content = msg.content
    elif isinstance(msg.content, list):
        content = "\n".join([
            block.text if hasattr(block, 'text') else str(block) 
            for block in msg.content
        ])
    else:
        content = str(msg.content)
    
    return {
        "role": role,
        "content": content
    }

# Convertendo a conversa
api_format = [message_to_dict(msg) for msg in conversa]
print("Conversa no formato de API:")
print(json.dumps(api_format, indent=2, ensure_ascii=False))

# 6. Funcionalidades avançadas
print("\n⚡ 6. Funcionalidades Avançadas")
print("-" * 40)

# Criando mensagem com metadados (se suportado)
try:
    # Tentando criar mensagem com contexto adicional
    advanced_msg = UserMessage(
        content=[
            TextBlock("Analise este código e sugira melhorias:", type="text"),
            TextBlock("for i in range(len(lista)):\n    print(lista[i])", type="text")
        ]
    )
    print("✅ Mensagem avançada criada com sucesso")
    
    # Resposta detalhada
    response = AssistantMessage([
        TextBlock("Sugestões de melhoria:", type="text"),
        TextBlock("1. Use iteração direta: for item in lista:", type="text"),
        TextBlock("2. Se precisar do índice: for i, item in enumerate(lista):", type="text"),
        TextBlock("3. Código melhorado:\nfor item in lista:\n    print(item)", type="text")
    ])
    print("✅ Resposta com análise de código criada")
    
except Exception as e:
    print(f"⚠️ Erro ao criar mensagem avançada: {e}")

print("\n" + "=" * 60)
print("✅ Exemplo completo do Claude Code SDK executado com sucesso!")
print("=" * 60)
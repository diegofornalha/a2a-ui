#!/usr/bin/env python3
"""
ETAPA 1: ESTRUTURA BÁSICA
TextBlock, UserMessage, AssistantMessage
"""

# Entender a estrutura básica
from claude_code_sdk import TextBlock, UserMessage, AssistantMessage

print("=" * 60)
print("📚 ETAPA 1: ESTRUTURA BÁSICA DO CLAUDE SDK")
print("=" * 60)

# ==========================================
# 1. TextBlock - Bloco de texto simples
# ==========================================
print("\n1️⃣ TextBlock - Bloco de texto simples")
print("-" * 40)

# Criar um TextBlock
text_block = TextBlock(text="Olá! Eu sou um bloco de texto simples.")
print(f"✅ Criado: {text_block}")
print(f"📝 Conteúdo: {text_block.text}")

# Múltiplos TextBlocks
blocos = [
    TextBlock("Primeiro bloco de texto"),
    TextBlock("Segundo bloco de texto"),
    TextBlock("Terceiro bloco de texto")
]
print(f"\n📦 Lista com {len(blocos)} TextBlocks criada")
for i, bloco in enumerate(blocos, 1):
    print(f"   Bloco {i}: {bloco.text}")

# ==========================================
# 2. UserMessage - Mensagens do usuário
# ==========================================
print("\n2️⃣ UserMessage - Mensagens do usuário")
print("-" * 40)

# UserMessage com string simples
user_simples = UserMessage(content="Qual é a capital do Brasil?")
print(f"✅ Mensagem simples: {user_simples.content}")

# UserMessage com lista de TextBlocks
user_complexa = UserMessage(
    content=[
        TextBlock("Eu tenho três perguntas:"),
        TextBlock("1. O que é Python?"),
        TextBlock("2. Para que serve?"),
        TextBlock("3. Como começar a aprender?")
    ]
)
print(f"\n✅ Mensagem complexa com {len(user_complexa.content)} blocos")

# ==========================================
# 3. AssistantMessage - Respostas do Claude
# ==========================================
print("\n3️⃣ AssistantMessage - Respostas do Claude")
print("-" * 40)

# AssistantMessage simples
assistant_simples = AssistantMessage(
    content="A capital do Brasil é Brasília."
)
print(f"✅ Resposta simples: {assistant_simples.content}")

# AssistantMessage com múltiplos blocos
assistant_complexa = AssistantMessage(
    content=[
        TextBlock("Python é uma linguagem de programação:"),
        TextBlock("• Interpretada e de alto nível"),
        TextBlock("• Criada por Guido van Rossum em 1991"),
        TextBlock("• Usada em web, IA, ciência de dados, etc"),
        TextBlock("• Conhecida pela sintaxe clara e legível")
    ]
)
print(f"\n✅ Resposta complexa com {len(assistant_complexa.content)} blocos")

# ==========================================
# 4. Exemplo Prático: Conversa Completa
# ==========================================
print("\n4️⃣ Exemplo Prático: Conversa Completa")
print("-" * 40)

# Simulando uma conversa
conversa = []

# Pergunta 1
pergunta1 = UserMessage("O que é uma lista em Python?")
conversa.append(pergunta1)

resposta1 = AssistantMessage(
    content=[
        TextBlock("Uma lista em Python é uma estrutura de dados que:"),
        TextBlock("• Armazena múltiplos valores em sequência"),
        TextBlock("• É mutável (pode ser modificada)"),
        TextBlock("• Usa colchetes: [1, 2, 3, 'texto']"),
        TextBlock("• Permite diferentes tipos de dados")
    ]
)
conversa.append(resposta1)

# Pergunta 2
pergunta2 = UserMessage("Como adicionar itens a uma lista?")
conversa.append(pergunta2)

resposta2 = AssistantMessage(
    content=[
        TextBlock("Você pode adicionar itens de várias formas:"),
        TextBlock("• lista.append(item) - adiciona ao final"),
        TextBlock("• lista.insert(índice, item) - adiciona em posição específica"),
        TextBlock("• lista.extend([items]) - adiciona múltiplos itens"),
        TextBlock("• lista += [item] - concatenação")
    ]
)
conversa.append(resposta2)

# Exibindo a conversa
print("\n💬 Conversa simulada:")
for i, msg in enumerate(conversa):
    if isinstance(msg, UserMessage):
        print(f"\n👤 Usuário:")
        if isinstance(msg.content, str):
            print(f"   {msg.content}")
        else:
            for block in msg.content:
                print(f"   • {block.text}")
    
    elif isinstance(msg, AssistantMessage):
        print(f"\n🤖 Claude:")
        if isinstance(msg.content, str):
            print(f"   {msg.content}")
        else:
            for block in msg.content:
                print(f"   {block.text}")

# ==========================================
# 5. Padrões de Uso
# ==========================================
print("\n5️⃣ Padrões de Uso Comuns")
print("-" * 40)

def processar_mensagem(msg):
    """Função helper para processar qualquer tipo de mensagem"""
    if isinstance(msg.content, str):
        return msg.content
    elif isinstance(msg.content, list):
        return "\n".join([block.text for block in msg.content])
    return str(msg.content)

# Testando o processador
msg_teste = AssistantMessage(
    content=[
        TextBlock("Linha 1"),
        TextBlock("Linha 2"),
        TextBlock("Linha 3")
    ]
)
print("Mensagem processada:")
print(processar_mensagem(msg_teste))

# ==========================================
# RESUMO
# ==========================================
print("\n" + "=" * 60)
print("📋 RESUMO DA ETAPA 1")
print("=" * 60)
print("""
✅ Aprendemos:
   • TextBlock(text="...") - Cria blocos de texto
   • UserMessage(content=...) - Representa entrada do usuário
   • AssistantMessage(content=...) - Representa resposta do Claude
   • content pode ser string ou lista de TextBlocks

📝 Principais pontos:
   • TextBlock só aceita parâmetro 'text'
   • UserMessage e AssistantMessage aceitam string ou lista
   • Use isinstance() para verificar tipos
   • Processe content diferentemente se for string ou lista

🎯 Próximo passo: 
   • Etapa 2 - Função query() para interação real com Claude
""")
print("=" * 60)
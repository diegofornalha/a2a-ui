#!/usr/bin/env python3
"""
Exemplo COMPLETO do Claude Code SDK
Demonstrando TextBlock, UserMessage, AssistantMessage e query
"""

import anyio
from claude_code_sdk import (
    TextBlock,
    UserMessage, 
    AssistantMessage,
    ClaudeCodeOptions,
    ResultMessage,
    query
)

print("=" * 60)
print("🚀 CLAUDE CODE SDK - Guia Completo")
print("=" * 60)

# ==========================================
# PARTE 1: Estruturas Básicas
# ==========================================
print("\n📚 PARTE 1: Estruturas Básicas")
print("-" * 40)

# 1.1 TextBlock - Bloco de texto simples
print("\n1.1 TextBlock:")
text_block = TextBlock(text="Este é um bloco de texto do Claude SDK")
print(f"   ✅ Criado: {text_block}")
print(f"   📝 Conteúdo: {text_block.text}")

# 1.2 UserMessage - Mensagens do usuário
print("\n1.2 UserMessage:")
user_msg = UserMessage(content="Qual a diferença entre lista e tupla em Python?")
print(f"   ✅ Mensagem do usuário criada")
print(f"   📝 Conteúdo: {user_msg.content}")

# UserMessage com múltiplos blocos
user_msg_blocks = UserMessage(
    content=[
        TextBlock("Tenho duas perguntas sobre Python:"),
        TextBlock("1. Como criar uma função?"),
        TextBlock("2. O que são decoradores?")
    ]
)
print(f"   ✅ Mensagem com {len(user_msg_blocks.content)} blocos criada")

# 1.3 AssistantMessage - Respostas do Claude
print("\n1.3 AssistantMessage:")
assistant_msg = AssistantMessage(
    content="Listas são mutáveis, tuplas são imutáveis em Python."
)
print(f"   ✅ Resposta do assistente criada")
print(f"   📝 Conteúdo: {assistant_msg.content}")

# ==========================================
# PARTE 2: Usando a função query (assíncrona)
# ==========================================
print("\n📡 PARTE 2: Função query() - Interação com Claude")
print("-" * 40)

async def exemplo_basico():
    """Exemplo básico de query"""
    print("\n2.1 Query Básica:")
    print("   Pergunta: O que é Python?")
    print("   Resposta do Claude:")
    
    async for message in query(prompt="O que é Python em uma frase?"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"   🤖 {block.text}")

async def exemplo_com_opcoes():
    """Query com opções personalizadas"""
    print("\n2.2 Query com Opções Personalizadas:")
    
    options = ClaudeCodeOptions(
        system_prompt="Você é um professor de programação Python. Seja didático e use exemplos.",
        max_turns=1
    )
    
    print("   Pergunta: Como criar uma lista em Python?")
    print("   Resposta do Claude (modo professor):")
    
    async for message in query(
        prompt="Como criar uma lista em Python? Dê exemplos simples.",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"   📚 {block.text}")

async def exemplo_com_ferramentas():
    """Query usando ferramentas (Read, Write, etc)"""
    print("\n2.3 Query com Ferramentas:")
    
    options = ClaudeCodeOptions(
        allowed_tools=["Read", "Write"],
        system_prompt="Você é um assistente de código Python.",
        max_turns=2
    )
    
    print("   Tarefa: Criar arquivo exemplo_python.py com função de saudação")
    print("   Executando...")
    
    async for message in query(
        prompt="Crie um arquivo exemplo_python.py com uma função saudar(nome) que retorna 'Olá, {nome}!'",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"   ✍️ {block.text}")
        elif isinstance(message, ResultMessage):
            if message.total_cost_usd > 0:
                print(f"   💰 Custo: ${message.total_cost_usd:.6f}")

async def exemplo_conversacao():
    """Exemplo de conversação mais complexa"""
    print("\n2.4 Conversação Complexa:")
    
    options = ClaudeCodeOptions(
        system_prompt="Você é um expert em Python. Seja conciso mas completo.",
        max_turns=3
    )
    
    perguntas = [
        "O que são list comprehensions?",
        "Mostre um exemplo prático",
        "Quando devo usar e quando evitar?"
    ]
    
    for pergunta in perguntas:
        print(f"\n   👤 Pergunta: {pergunta}")
        
        async for message in query(prompt=pergunta, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        # Limita a exibição para não ficar muito longo
                        texto = block.text[:200] + "..." if len(block.text) > 200 else block.text
                        print(f"   🤖 {texto}")

# ==========================================
# PARTE 3: Exemplos Práticos
# ==========================================
print("\n🎯 PARTE 3: Exemplos Práticos")
print("-" * 40)

def criar_conversa_estruturada():
    """Cria uma conversa estruturada sem usar query"""
    print("\n3.1 Conversa Estruturada (sem API):")
    
    conversa = []
    
    # Adiciona pergunta
    pergunta = UserMessage("Como fazer debug em Python?")
    conversa.append(pergunta)
    print(f"   👤 User: {pergunta.content}")
    
    # Simula resposta
    resposta = AssistantMessage(content=[
        TextBlock("Existem várias formas de fazer debug em Python:"),
        TextBlock("1. print() - Método mais simples"),
        TextBlock("2. pdb - Python Debugger integrado"),
        TextBlock("3. breakpoint() - Python 3.7+"),
        TextBlock("4. IDEs com debug visual (PyCharm, VS Code)")
    ])
    conversa.append(resposta)
    
    print("   🤖 Assistant:")
    for block in resposta.content:
        print(f"      • {block.text}")
    
    return conversa

def exemplo_processamento_mensagens():
    """Mostra como processar diferentes tipos de mensagens"""
    print("\n3.2 Processamento de Mensagens:")
    
    # Diferentes tipos de conteúdo
    msg_string = AssistantMessage(content="Resposta simples como string")
    msg_blocks = AssistantMessage(content=[
        TextBlock("Resposta"),
        TextBlock("com múltiplos"),
        TextBlock("blocos de texto")
    ])
    
    def processar_mensagem(msg):
        """Processa qualquer tipo de mensagem"""
        if isinstance(msg.content, str):
            return msg.content
        elif isinstance(msg.content, list):
            return " ".join([
                block.text if isinstance(block, TextBlock) else str(block)
                for block in msg.content
            ])
        return str(msg.content)
    
    print(f"   String: {processar_mensagem(msg_string)}")
    print(f"   Blocos: {processar_mensagem(msg_blocks)}")

# ==========================================
# PARTE 4: Dicas e Boas Práticas
# ==========================================
print("\n💡 PARTE 4: Dicas e Boas Práticas")
print("-" * 40)

print("""
4.1 Estrutura do SDK:
   • TextBlock: Apenas aceita 'text' como parâmetro
   • UserMessage/AssistantMessage: Aceita string ou lista de TextBlocks
   • query(): Função assíncrona para interagir com Claude
   • ClaudeCodeOptions: Configura comportamento da query

4.2 Quando usar cada componente:
   • TextBlock: Para estruturar texto em blocos
   • UserMessage: Para representar entrada do usuário
   • AssistantMessage: Para representar resposta do Claude
   • query(): Para fazer chamadas reais à API

4.3 Opções importantes do ClaudeCodeOptions:
   • system_prompt: Define personalidade/contexto
   • max_turns: Limita número de interações
   • allowed_tools: Habilita ferramentas (Read, Write, etc)
   • model: Escolhe o modelo (opus, sonnet, haiku)

4.4 Tratamento de respostas:
   • Sempre verificar tipo com isinstance()
   • AssistantMessage contém a resposta
   • ResultMessage contém metadados (custo, tokens, etc)
   • Iterar sobre content quando for lista de blocos
""")

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
async def main():
    """Executa exemplos assíncronos"""
    print("\n" + "=" * 60)
    print("🚀 EXECUTANDO EXEMPLOS ASSÍNCRONOS")
    print("=" * 60)
    
    try:
        # Tenta executar queries reais
        await exemplo_basico()
        await exemplo_com_opcoes()
        # await exemplo_com_ferramentas()  # Comentado pois cria arquivos
        # await exemplo_conversacao()  # Comentado para economizar tokens
    except Exception as e:
        print(f"\n⚠️ Erro ao executar queries: {e}")
        print("   Certifique-se de que o Claude Code está configurado corretamente")

# Executa partes síncronas
print("\n" + "=" * 60)
print("🔧 EXECUTANDO EXEMPLOS SÍNCRONOS")
print("=" * 60)

conversa = criar_conversa_estruturada()
exemplo_processamento_mensagens()

print("\n" + "=" * 60)
print("✅ Exemplo completo do Claude Code SDK executado!")
print("   Para executar queries assíncronas, use:")
print("   python3 -m anyio claude_sdk_completo.py")
print("=" * 60)

# Para executar as partes assíncronas
if __name__ == "__main__":
    print("\n🔄 Tentando executar partes assíncronas...")
    try:
        anyio.run(main)
    except ImportError:
        print("   ⚠️ anyio não instalado. Instale com: pip install anyio")
    except Exception as e:
        print(f"   ⚠️ Erro: {e}")
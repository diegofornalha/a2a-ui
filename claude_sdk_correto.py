#!/usr/bin/env python3
"""
Exemplo CORRETO do Claude Code SDK v0.0.20
Usando as assinaturas corretas das classes
"""

from claude_code_sdk import TextBlock, UserMessage, AssistantMessage
import claude_code_sdk
import json

print("=" * 60)
print("🚀 CLAUDE CODE SDK - Exemplo Correto")
print(f"Versão do SDK: {claude_code_sdk.__version__}")
print("=" * 60)

# 1. TextBlock - apenas aceita text como parâmetro
print("\n📝 1. TextBlock - Bloco de texto simples")
print("-" * 40)

text_block = TextBlock(text="Olá! Este é um bloco de texto do Claude SDK.")
print(f"✅ TextBlock criado: {text_block}")
print(f"   Conteúdo: {text_block.text}")

# 2. UserMessage 
print("\n👤 2. UserMessage - Mensagens do usuário")
print("-" * 40)

# Mensagem simples com string
user_msg_simple = UserMessage(content="Qual é a capital do Brasil?")
print(f"✅ UserMessage simples criada")
print(f"   Conteúdo: {user_msg_simple.content}")

# Mensagem com lista de TextBlocks
user_msg_blocks = UserMessage(
    content=[
        TextBlock("Eu tenho duas perguntas:"),
        TextBlock("1. O que é Python?"),
        TextBlock("2. Como criar uma lista?")
    ]
)
print(f"✅ UserMessage com múltiplos blocos criada")
print(f"   Número de blocos: {len(user_msg_blocks.content) if isinstance(user_msg_blocks.content, list) else 1}")

# 3. AssistantMessage
print("\n🤖 3. AssistantMessage - Respostas do Claude")
print("-" * 40)

assistant_msg = AssistantMessage(
    content="A capital do Brasil é Brasília, localizada no Distrito Federal."
)
print(f"✅ AssistantMessage simples criada")
print(f"   Conteúdo: {assistant_msg.content}")

# Resposta com múltiplos blocos
assistant_blocks = AssistantMessage(
    content=[
        TextBlock("Python é uma linguagem de programação:"),
        TextBlock("• Interpretada e de alto nível"),
        TextBlock("• Sintaxe clara e legível"),
        TextBlock("• Multiplataforma e versátil")
    ]
)
print(f"✅ AssistantMessage com múltiplos blocos criada")

# 4. Construindo uma conversa
print("\n💬 4. Conversa Estruturada")
print("-" * 40)

class Conversa:
    def __init__(self):
        self.mensagens = []
    
    def adicionar_usuario(self, texto):
        """Adiciona mensagem do usuário"""
        if isinstance(texto, str):
            msg = UserMessage(content=texto)
        else:
            msg = UserMessage(content=[TextBlock(t) for t in texto])
        self.mensagens.append(msg)
        return msg
    
    def adicionar_assistente(self, texto):
        """Adiciona resposta do assistente"""
        if isinstance(texto, str):
            msg = AssistantMessage(content=texto)
        else:
            msg = AssistantMessage(content=[TextBlock(t) for t in texto])
        self.mensagens.append(msg)
        return msg
    
    def exibir(self):
        """Exibe a conversa formatada"""
        for i, msg in enumerate(self.mensagens, 1):
            role = "👤 Usuário" if isinstance(msg, UserMessage) else "🤖 Claude"
            print(f"\n{i}. {role}:")
            
            if isinstance(msg.content, str):
                print(f"   {msg.content}")
            elif isinstance(msg.content, list):
                for block in msg.content:
                    print(f"   • {block.text if hasattr(block, 'text') else block}")

# Criando uma conversa exemplo
conversa = Conversa()

# Interação 1
conversa.adicionar_usuario("O que é uma função em Python?")
conversa.adicionar_assistente([
    "Uma função em Python é um bloco de código reutilizável:",
    "def nome_funcao(parametros):",
    "    # código da função",
    "    return resultado"
])

# Interação 2
conversa.adicionar_usuario("Como criar uma lista?")
conversa.adicionar_assistente([
    "Você pode criar listas de várias formas:",
    "lista_vazia = []",
    "lista_numeros = [1, 2, 3, 4, 5]",
    "lista_mista = [1, 'texto', 3.14, True]"
])

print("\n📖 Exibindo a conversa:")
conversa.exibir()

# 5. Explorando a estrutura do SDK
print("\n🔍 5. Estrutura do Claude Code SDK")
print("-" * 40)

# Verificando atributos disponíveis
print("Módulos disponíveis no SDK:")
import inspect
for name in dir(claude_code_sdk):
    if not name.startswith('_'):
        obj = getattr(claude_code_sdk, name)
        if inspect.isclass(obj):
            print(f"  • Classe: {name}")
        elif inspect.isfunction(obj):
            print(f"  • Função: {name}")
        elif inspect.ismodule(obj):
            print(f"  • Módulo: {name}")

# 6. Exemplo prático de uso
print("\n🎯 6. Exemplo Prático - Assistente de Código")
print("-" * 40)

def criar_assistente_codigo():
    """Cria um assistente para ajudar com código"""
    mensagens = []
    
    # Pergunta do usuário
    pergunta = UserMessage(content="Como fazer um loop em Python?")
    mensagens.append(pergunta)
    print("👤 Pergunta:", pergunta.content)
    
    # Resposta estruturada
    resposta = AssistantMessage(content=[
        TextBlock("Em Python, você tem várias opções de loops:"),
        TextBlock("1. For loop: for item in lista:"),
        TextBlock("2. While loop: while condição:"),
        TextBlock("3. List comprehension: [x*2 for x in range(10)]"),
        TextBlock("4. For com range: for i in range(10):")
    ])
    mensagens.append(resposta)
    
    print("\n🤖 Resposta estruturada:")
    for block in resposta.content:
        print(f"   • {block.text}")
    
    return mensagens

# Executando o assistente
assistente_msgs = criar_assistente_codigo()

# 7. Serialização para API
print("\n📡 7. Preparando para envio à API")
print("-" * 40)

def preparar_para_api(mensagens):
    """Converte mensagens para formato de API"""
    resultado = []
    for msg in mensagens:
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
        
        resultado.append({
            "role": role,
            "content": content
        })
    
    return resultado

# Convertendo as mensagens
api_data = preparar_para_api(assistente_msgs)
print("Dados prontos para API:")
print(json.dumps(api_data, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("✅ Claude Code SDK v0.0.20 - Exemplo executado com sucesso!")
print("=" * 60)
print("\n💡 Principais aprendizados:")
print("   • TextBlock aceita apenas 'text' como parâmetro")
print("   • UserMessage e AssistantMessage aceitam string ou lista")
print("   • Content pode ser string ou lista de TextBlocks")
print("   • SDK focado em estruturação de mensagens para Claude")
print("=" * 60)
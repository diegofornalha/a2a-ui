#!/usr/bin/env python3
"""
ETAPA 3: ClaudeCodeOptions
Configurações para personalizar o comportamento do Claude
"""

import anyio
from claude_code_sdk import (
    ClaudeCodeOptions,
    query,
    AssistantMessage,
    TextBlock
)

print("=" * 60)
print("⚙️ ETAPA 3: ClaudeCodeOptions - PERSONALIZANDO O CLAUDE")
print("=" * 60)

# ==========================================
# 1. Opções Básicas
# ==========================================
async def opcoes_basicas():
    """Principais opções de configuração"""
    print("\n1️⃣ Opções Básicas de Configuração")
    print("-" * 40)
    
    # system_prompt - Personalizar comportamento
    options = ClaudeCodeOptions(
        system_prompt="You are a helpful Python teacher. Be concise and use examples.",
        max_turns=1  # Limitar interações
    )
    
    print("📝 Configurações:")
    print(f"   • system_prompt: Define personalidade/contexto")
    print(f"   • max_turns: 1 (limita número de interações)")
    
    print("\n🤖 Resposta com professor de Python:")
    async for message in query(
        prompt="What is a list in Python?",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"   {block.text[:200]}...")  # Limita output

# ==========================================
# 2. Escolhendo Modelo
# ==========================================
async def escolhendo_modelo():
    """Diferentes modelos disponíveis"""
    print("\n2️⃣ Escolhendo o Modelo (model)")
    print("-" * 40)
    
    modelos = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    
    print("📊 Modelos disponíveis:")
    for modelo in modelos:
        print(f"   • {modelo}")
    
    # Usando modelo específico
    options = ClaudeCodeOptions(
        model="claude-3-sonnet",  # Modelo balanceado
        system_prompt="Be extremely concise",
        max_turns=1
    )
    
    print("\n🤖 Testando com claude-3-sonnet:")
    async for message in query(
        prompt="Define Python in 5 words",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            if isinstance(message.content, str):
                print(f"   {message.content}")
            else:
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"   {block.text}")

# ==========================================
# 3. Múltiplos Turnos
# ==========================================
async def multiplos_turnos():
    """Configurando conversas mais longas"""
    print("\n3️⃣ Configurando Múltiplos Turnos")
    print("-" * 40)
    
    options = ClaudeCodeOptions(
        system_prompt="You are a Python expert. Help step by step.",
        max_turns=3  # Permite 3 interações
    )
    
    print("📝 max_turns=3 permite conversação mais longa")
    print("\n🗣️ Simulando conversa de 3 turnos:")
    
    prompts = [
        "What is a dictionary in Python?",
        "How do I add items to it?",
        "Can you show an example?"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nTurno {i} - Pergunta: {prompt}")
        print("Resposta: ", end="")
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                # Pega só a primeira linha para exemplo
                if isinstance(message.content, list) and message.content:
                    first = message.content[0]
                    if isinstance(first, TextBlock):
                        print(first.text[:100] + "...")
                        break

# ==========================================
# 4. System Prompts Especializados
# ==========================================
async def system_prompts_especializados():
    """Diferentes personalidades através do system_prompt"""
    print("\n4️⃣ System Prompts Especializados")
    print("-" * 40)
    
    personalidades = [
        {
            "nome": "Professor",
            "prompt": "You are a patient Python teacher. Explain concepts simply with examples.",
            "pergunta": "What is a variable?"
        },
        {
            "nome": "Expert",
            "prompt": "You are a Python expert. Give technical, precise answers.",
            "pergunta": "Explain Python's GIL"
        },
        {
            "nome": "Iniciante-Friendly",
            "prompt": "Explain everything like I'm a complete beginner. Use analogies.",
            "pergunta": "What is a function?"
        }
    ]
    
    for config in personalidades:
        print(f"\n🎭 Personalidade: {config['nome']}")
        print(f"   Pergunta: {config['pergunta']}")
        
        options = ClaudeCodeOptions(
            system_prompt=config['prompt'],
            max_turns=1
        )
        
        print("   Resposta: ", end="")
        async for message in query(prompt=config['pergunta'], options=options):
            if isinstance(message, AssistantMessage):
                if isinstance(message.content, list) and message.content:
                    first = message.content[0]
                    if isinstance(first, TextBlock):
                        print(first.text[:80] + "...")
                        break

# ==========================================
# 5. Combinando Múltiplas Opções
# ==========================================
async def combinando_opcoes():
    """Usando várias opções juntas"""
    print("\n5️⃣ Combinando Múltiplas Opções")
    print("-" * 40)
    
    # Configuração completa
    options = ClaudeCodeOptions(
        system_prompt="You are a Python coding assistant. Be helpful and precise.",
        model="claude-3-sonnet",
        max_turns=2,
        # Podemos adicionar mais opções conforme necessário
    )
    
    print("📝 Configuração completa:")
    print("   • system_prompt: Assistente de código Python")
    print("   • model: claude-3-sonnet")
    print("   • max_turns: 2")
    
    print("\n🤖 Testando configuração completa:")
    async for message in query(
        prompt="Create a simple Python function to calculate factorial",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            print("   Resposta recebida ✅")
            # Mostra apenas início da resposta
            if isinstance(message.content, list) and message.content:
                for block in message.content[:2]:  # Primeiros 2 blocos
                    if isinstance(block, TextBlock):
                        print(f"   {block.text[:100]}...")

# ==========================================
# 6. Preparando para Ferramentas (próxima etapa)
# ==========================================
async def preparacao_ferramentas():
    """Introdução ao allowed_tools (detalhado na etapa 5)"""
    print("\n6️⃣ Preparação para Ferramentas")
    print("-" * 40)
    
    print("📝 Prévia do allowed_tools:")
    print("   • Read - Leitura de arquivos")
    print("   • Write - Escrita de arquivos")
    print("   • Bash - Comandos do sistema")
    
    # Exemplo básico (será expandido na etapa 5)
    options = ClaudeCodeOptions(
        system_prompt="You are a file assistant",
        allowed_tools=["Read"],  # Permite apenas leitura
        max_turns=1
    )
    
    print("\n🔧 Com allowed_tools=['Read']:")
    print("   Claude pode ler arquivos mas não modificar")
    
    # Nota: Ferramentas serão exploradas em detalhe na etapa 5

# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================
async def main():
    """Executa todos os exemplos"""
    
    print("\n" + "🔄" * 30)
    print("EXECUTANDO EXEMPLOS DE ClaudeCodeOptions")
    print("🔄" * 30)
    
    try:
        await opcoes_basicas()
        await escolhendo_modelo()
        await multiplos_turnos()
        await system_prompts_especializados()
        await combinando_opcoes()
        await preparacao_ferramentas()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")

# ==========================================
# RESUMO E REFERÊNCIA RÁPIDA
# ==========================================
print("\n" + "=" * 60)
print("📋 RESUMO DA ETAPA 3 - ClaudeCodeOptions")
print("=" * 60)
print("""
✅ Principais Opções:
   • system_prompt - Define personalidade/contexto
   • max_turns - Limita número de interações
   • model - Escolhe modelo (opus, sonnet, haiku)
   • allowed_tools - Habilita ferramentas (próxima etapa)

📝 Exemplo básico:
   options = ClaudeCodeOptions(
       system_prompt="You are a helpful assistant",
       max_turns=1,
       model="claude-3-sonnet"
   )

🎯 Casos de uso:
   • Professor: system_prompt educacional
   • Expert: system_prompt técnico
   • Assistente: system_prompt helpful
   • Limitado: max_turns=1 para respostas únicas

💡 Dicas:
   • system_prompt é a opção mais poderosa
   • max_turns controla duração da conversa
   • model afeta velocidade e qualidade
   • Combine opções para casos específicos

🔜 Próxima etapa:
   • Etapa 4 - Tipos de blocos avançados
   • Etapa 5 - Ferramentas (Read, Write, Bash)
""")
print("=" * 60)

# Execução
if __name__ == "__main__":
    print("\n🚀 Iniciando exemplos de ClaudeCodeOptions...")
    try:
        anyio.run(main)
    except ImportError:
        print("❌ anyio não instalado. Instale com: pip install anyio")
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
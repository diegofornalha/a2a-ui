#!/usr/bin/env python3
"""
ETAPA 5: FERRAMENTAS (TOOLS)
Read, Write, Bash - Ordem progressiva de aprendizado
"""

import anyio
from claude_code_sdk import (
    query,
    ClaudeCodeOptions,
    AssistantMessage,
    TextBlock
)

print("=" * 60)
print("🔧 ETAPA 5: FERRAMENTAS - PODER REAL DO CLAUDE")
print("=" * 60)

# ==========================================
# ORDEM DE APRENDIZADO DAS FERRAMENTAS
# ==========================================
print("\n📚 ORDEM PROGRESSIVA DE APRENDIZADO:")
print("-" * 40)
print("""
1️⃣ Read - Leitura de arquivos (mais seguro)
2️⃣ Write - Escrita de arquivos (modifica sistema)
3️⃣ Bash - Comandos do sistema (mais poderoso)

⚠️ Sempre comece com Read, depois Write, por fim Bash
""")

# ==========================================
# 1. FERRAMENTA READ
# ==========================================
async def ferramenta_read():
    """Começando com Read - apenas leitura"""
    print("\n1️⃣ FERRAMENTA READ - Leitura de Arquivos")
    print("-" * 40)
    
    # Apenas Read permitido
    options = ClaudeCodeOptions(
        system_prompt="You are a file reader assistant. Help analyze files.",
        allowed_tools=["Read"],  # Só pode ler
        max_turns=1
    )
    
    print("🔍 Configuração:")
    print("   allowed_tools=['Read'] - Apenas leitura")
    print("\n📖 Exemplo: Lendo pyproject.toml")
    
    async for message in query(
        prompt="Read pyproject.toml and tell me the project name and version",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"   📄 {block.text[:200]}...")

# ==========================================
# 2. FERRAMENTA WRITE
# ==========================================
async def ferramenta_write():
    """Adicionando Write - leitura e escrita"""
    print("\n2️⃣ FERRAMENTA WRITE - Escrita de Arquivos")
    print("-" * 40)
    
    # Read + Write
    options = ClaudeCodeOptions(
        system_prompt="You are a Python file creator. Create clean, documented code.",
        allowed_tools=["Read", "Write"],  # Pode ler E escrever
        max_turns=2
    )
    
    print("📝 Configuração:")
    print("   allowed_tools=['Read', 'Write'] - Leitura e escrita")
    print("\n✍️ Exemplo: Criando um arquivo Python")
    
    async for message in query(
        prompt="Create a file called greetings.py with a function greet(name) that returns 'Hello, {name}!'",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            print("   ✅ Processando resposta...")
            for block in message.content:
                block_type = type(block).__name__
                if block_type == "TextBlock":
                    print(f"   💬 Claude: {block.text[:100]}...")
                else:
                    print(f"   🔧 Ação: {block_type}")

# ==========================================
# 3. FERRAMENTA BASH
# ==========================================
async def ferramenta_bash():
    """Adicionando Bash - controle total"""
    print("\n3️⃣ FERRAMENTA BASH - Comandos do Sistema")
    print("-" * 40)
    
    # Read + Write + Bash (poder total)
    options = ClaudeCodeOptions(
        system_prompt="You are a system administrator. Execute commands safely.",
        allowed_tools=["Read", "Write", "Bash"],  # Todas as ferramentas
        max_turns=3
    )
    
    print("⚡ Configuração:")
    print("   allowed_tools=['Read', 'Write', 'Bash'] - Controle total")
    print("\n🖥️ Exemplo: Listando arquivos Python")
    
    async for message in query(
        prompt="List all Python files in the current directory using ls",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"   🗂️ {block.text[:150]}...")

# ==========================================
# 4. COMBINAÇÕES PRÁTICAS
# ==========================================
async def combinacoes_praticas():
    """Combinações úteis de ferramentas"""
    print("\n4️⃣ COMBINAÇÕES PRÁTICAS DE FERRAMENTAS")
    print("-" * 40)
    
    combinacoes = [
        {
            "nome": "Analisador (Read only)",
            "tools": ["Read"],
            "uso": "Análise segura de código existente"
        },
        {
            "nome": "Editor (Read + Write)",
            "tools": ["Read", "Write"],
            "uso": "Modificar arquivos existentes"
        },
        {
            "nome": "Desenvolvedor (Read + Write + Bash)",
            "tools": ["Read", "Write", "Bash"],
            "uso": "Desenvolvimento completo com testes"
        }
    ]
    
    for combo in combinacoes:
        print(f"\n🎯 {combo['nome']}:")
        print(f"   Ferramentas: {combo['tools']}")
        print(f"   Uso ideal: {combo['uso']}")

# ==========================================
# 5. EXEMPLO PROGRESSIVO COMPLETO
# ==========================================
async def exemplo_progressivo():
    """Evolução gradual do uso de ferramentas"""
    print("\n5️⃣ EXEMPLO PROGRESSIVO - EVOLUÇÃO GRADUAL")
    print("-" * 40)
    
    # Passo 1: Só leitura
    print("\n📖 Passo 1: Apenas Read")
    options1 = ClaudeCodeOptions(
        allowed_tools=["Read"],
        max_turns=1
    )
    
    async for message in query(
        prompt="Check if file example.py exists",
        options=options1
    ):
        if isinstance(message, AssistantMessage):
            print("   ✓ Verificação concluída")
            break
    
    # Passo 2: Leitura e escrita
    print("\n📝 Passo 2: Read + Write")
    options2 = ClaudeCodeOptions(
        allowed_tools=["Read", "Write"],
        max_turns=1
    )
    
    async for message in query(
        prompt="Create example.py with a main function",
        options=options2
    ):
        if isinstance(message, AssistantMessage):
            print("   ✓ Arquivo criado")
            break
    
    # Passo 3: Tudo
    print("\n⚡ Passo 3: Read + Write + Bash")
    options3 = ClaudeCodeOptions(
        allowed_tools=["Read", "Write", "Bash"],
        max_turns=1
    )
    
    async for message in query(
        prompt="Run python example.py to test it",
        options=options3
    ):
        if isinstance(message, AssistantMessage):
            print("   ✓ Teste executado")
            break

# ==========================================
# 6. SEGURANÇA E BOAS PRÁTICAS
# ==========================================
print("\n6️⃣ SEGURANÇA E BOAS PRÁTICAS")
print("-" * 40)
print("""
⚠️ IMPORTANTES CONSIDERAÇÕES:

🔒 Segurança:
   • Comece sempre com Read apenas
   • Adicione Write quando necessário
   • Use Bash com muito cuidado
   
✅ Boas práticas:
   • Read: Para análise e compreensão
   • Write: Para criar/modificar código
   • Bash: Para executar e testar
   
🚫 Evite:
   • Bash desnecessário para operações simples
   • Write sem Read primeiro (pode sobrescrever)
   • Comandos Bash destrutivos (rm -rf, etc)
""")

# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================
async def main():
    print("\n" + "🔄" * 30)
    print("DEMONSTRANDO FERRAMENTAS")
    print("🔄" * 30)
    
    try:
        await ferramenta_read()
        await ferramenta_write()
        await ferramenta_bash()
        await combinacoes_praticas()
        await exemplo_progressivo()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")

# ==========================================
# RESUMO
# ==========================================
print("\n" + "=" * 60)
print("📋 RESUMO DA ETAPA 5 - FERRAMENTAS")
print("=" * 60)
print("""
✅ Ferramentas disponíveis:
   1. Read - Leitura de arquivos
   2. Write - Escrita de arquivos
   3. Bash - Comandos do sistema

📝 Ordem de aprendizado:
   allowed_tools=["Read"]                    # Começar
   allowed_tools=["Read", "Write"]           # Evoluir
   allowed_tools=["Read", "Write", "Bash"]   # Completo

🎯 Casos de uso:
   • Análise: Read apenas
   • Desenvolvimento: Read + Write
   • DevOps: Read + Write + Bash

⚡ Exemplo de uso:
   options = ClaudeCodeOptions(
       allowed_tools=["Read", "Write"],
       system_prompt="You are a Python developer"
   )

🔐 Segurança:
   • Sempre validar antes de Write
   • Cuidado com comandos Bash
   • Princípio do menor privilégio

🔜 Próxima etapa:
   • Etapa 6 - Modos de interação
   • Etapa 7 - ClaudeSDKClient avançado
""")
print("=" * 60)

# Execução
if __name__ == "__main__":
    print("\n🚀 Demonstrando ferramentas...")
    try:
        anyio.run(main)
    except ImportError:
        print("❌ anyio não instalado")
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido")
    except Exception as e:
        print(f"❌ Erro: {e}")
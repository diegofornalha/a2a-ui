#!/usr/bin/env python3
"""
ETAPA 4: TIPOS DE BLOCOS AVANÇADOS
ToolUseBlock, ToolResultBlock, ThinkingBlock
"""

import anyio
from claude_code_sdk import (
    query,
    ClaudeCodeOptions,
    AssistantMessage,
    TextBlock,
    # Blocos avançados (quando disponíveis)
    # ToolUseBlock,
    # ToolResultBlock,
    # ThinkingBlock
)

print("=" * 60)
print("🔧 ETAPA 4: BLOCOS AVANÇADOS - ALÉM DO TextBlock")
print("=" * 60)

# ==========================================
# 1. Tipos de Blocos
# ==========================================
print("\n1️⃣ Tipos de Blocos Disponíveis")
print("-" * 40)
print("""
📦 Progressão dos Blocos:
   1. TextBlock - Texto simples (já vimos)
   2. ToolUseBlock - Quando Claude usa ferramentas
   3. ToolResultBlock - Resultados das ferramentas
   4. ThinkingBlock - Raciocínio do modelo
""")

# ==========================================
# 2. ToolUseBlock - Uso de Ferramentas
# ==========================================
async def exemplo_tool_use_block():
    """Demonstra quando Claude usa ferramentas"""
    print("\n2️⃣ ToolUseBlock - Uso de Ferramentas")
    print("-" * 40)
    
    options = ClaudeCodeOptions(
        system_prompt="You are a file assistant. Use tools when needed.",
        allowed_tools=["Read", "Write"],
        max_turns=2
    )
    
    print("📝 Pedindo ao Claude para criar um arquivo:")
    print("   Prompt: 'Create a file hello.py with a hello world function'")
    print("\n🔍 Observando os tipos de blocos:")
    
    async for message in query(
        prompt="Create a file hello.py with a hello world function",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                # Verifica tipo de cada bloco
                block_type = type(block).__name__
                print(f"\n   📦 Bloco tipo: {block_type}")
                
                if isinstance(block, TextBlock):
                    print(f"      Texto: {block.text[:100]}...")
                # Quando ToolUseBlock estiver disponível:
                # elif isinstance(block, ToolUseBlock):
                #     print(f"      Ferramenta: {block.tool_name}")
                #     print(f"      Parâmetros: {block.parameters}")

# ==========================================
# 3. ToolResultBlock - Resultados
# ==========================================
async def exemplo_tool_result_block():
    """Mostra resultados de ferramentas"""
    print("\n3️⃣ ToolResultBlock - Resultados de Ferramentas")
    print("-" * 40)
    
    print("""
📊 Quando aparece ToolResultBlock:
   • Após Claude executar Read → resultado do arquivo
   • Após Claude executar Write → confirmação de escrita
   • Após Claude executar Bash → output do comando
""")
    
    options = ClaudeCodeOptions(
        allowed_tools=["Read"],
        max_turns=1
    )
    
    print("\n🔍 Exemplo: Lendo um arquivo")
    async for message in query(
        prompt="Read the file pyproject.toml and tell me the project name",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for i, block in enumerate(message.content, 1):
                block_type = type(block).__name__
                print(f"   Bloco {i}: {block_type}")
                # Quando ToolResultBlock estiver disponível:
                # if isinstance(block, ToolResultBlock):
                #     print(f"      Resultado: {block.result[:100]}...")

# ==========================================
# 4. ThinkingBlock - Raciocínio
# ==========================================
async def exemplo_thinking_block():
    """Demonstra o raciocínio do modelo"""
    print("\n4️⃣ ThinkingBlock - Raciocínio do Modelo")
    print("-" * 40)
    
    print("""
🧠 ThinkingBlock mostra:
   • Processo de pensamento do Claude
   • Planejamento antes de executar
   • Análise de problemas complexos
""")
    
    options = ClaudeCodeOptions(
        system_prompt="Think step by step before answering",
        max_turns=1
    )
    
    print("\n🤔 Pergunta complexa para ver o raciocínio:")
    async for message in query(
        prompt="What's the best way to implement a binary search tree in Python?",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                block_type = type(block).__name__
                if block_type == "ThinkingBlock":
                    print("   🧠 [PENSAMENTO DETECTADO]")
                elif isinstance(block, TextBlock):
                    print(f"   💬 Resposta: {block.text[:150]}...")

# ==========================================
# 5. Processando Diferentes Blocos
# ==========================================
async def processando_blocos_mistos():
    """Como processar uma resposta com vários tipos de blocos"""
    print("\n5️⃣ Processando Resposta com Blocos Mistos")
    print("-" * 40)
    
    options = ClaudeCodeOptions(
        allowed_tools=["Read", "Write"],
        system_prompt="Use tools and explain what you're doing",
        max_turns=2
    )
    
    print("📝 Estratégia de processamento:")
    print("""
    for block in message.content:
        if isinstance(block, TextBlock):
            # Processa texto
        elif block.__class__.__name__ == 'ToolUseBlock':
            # Processa uso de ferramenta
        elif block.__class__.__name__ == 'ToolResultBlock':
            # Processa resultado
        elif block.__class__.__name__ == 'ThinkingBlock':
            # Processa raciocínio
    """)
    
    # Exemplo prático
    async for message in query(
        prompt="Create a simple Python script that prints the current date",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            print(f"\n📨 Mensagem com {len(message.content)} blocos:")
            
            for i, block in enumerate(message.content, 1):
                block_type = type(block).__name__
                print(f"   {i}. {block_type}")
                
                # Processa cada tipo
                if isinstance(block, TextBlock):
                    preview = block.text[:50]
                    print(f"      → {preview}...")

# ==========================================
# 6. Padrão Completo de Processamento
# ==========================================
def processar_bloco_generico(block):
    """Função helper para processar qualquer tipo de bloco"""
    block_type = type(block).__name__
    
    if isinstance(block, TextBlock):
        return f"Texto: {block.text}"
    
    # Para blocos futuros/customizados
    if hasattr(block, 'tool_name'):
        return f"Ferramenta: {getattr(block, 'tool_name', 'unknown')}"
    
    if hasattr(block, 'result'):
        return f"Resultado: {getattr(block, 'result', 'unknown')}"
    
    if hasattr(block, 'thought'):
        return f"Pensamento: {getattr(block, 'thought', 'unknown')}"
    
    return f"Bloco desconhecido: {block_type}"

# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================
async def main():
    print("\n" + "🔄" * 30)
    print("EXPLORANDO TIPOS DE BLOCOS")
    print("🔄" * 30)
    
    try:
        await exemplo_tool_use_block()
        await exemplo_tool_result_block()
        await exemplo_thinking_block()
        await processando_blocos_mistos()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")

# ==========================================
# RESUMO
# ==========================================
print("\n" + "=" * 60)
print("📋 RESUMO DA ETAPA 4 - BLOCOS AVANÇADOS")
print("=" * 60)
print("""
✅ Tipos de Blocos:
   • TextBlock - Texto simples (sempre presente)
   • ToolUseBlock - Quando usa ferramentas
   • ToolResultBlock - Resultados de ferramentas
   • ThinkingBlock - Raciocínio do modelo

📝 Processamento genérico:
   for block in message.content:
       block_type = type(block).__name__
       if isinstance(block, TextBlock):
           # processar texto
       # verificar outros tipos...

🔍 Quando aparecem:
   • TextBlock: Sempre nas respostas
   • ToolUseBlock: Com allowed_tools
   • ToolResultBlock: Após execução de tools
   • ThinkingBlock: Em raciocínios complexos

💡 Dica importante:
   Use type(block).__name__ para identificar
   blocos quando a classe não está importada

🔜 Próxima etapa:
   • Etapa 5 - Ferramentas (Read, Write, Bash)
""")
print("=" * 60)

# Execução
if __name__ == "__main__":
    print("\n🚀 Explorando blocos avançados...")
    try:
        anyio.run(main)
    except ImportError:
        print("❌ anyio não instalado")
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido")
    except Exception as e:
        print(f"❌ Erro: {e}")
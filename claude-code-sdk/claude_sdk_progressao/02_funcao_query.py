#!/usr/bin/env python3
"""
ETAPA 2: FUNÇÃO query()
Foco principal do SDK - interação assíncrona com Claude
"""

import anyio
from claude_code_sdk import query, AssistantMessage, TextBlock

print("=" * 60)
print("🚀 ETAPA 2: FUNÇÃO query() - CORAÇÃO DO SDK")
print("=" * 60)

# ==========================================
# 1. Query Básica
# ==========================================
async def exemplo_basico():
    """Exemplo mais simples possível"""
    print("\n1️⃣ Query Básica - Exemplo Mínimo")
    print("-" * 40)
    print("Pergunta: What is 2 + 2?")
    print("Resposta:")
    
    async for message in query(prompt="What is 2 + 2?"):
        print(f"   Tipo de mensagem: {type(message).__name__}")
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"   🤖 {block.text}")

# ==========================================
# 2. Query com Processamento Detalhado
# ==========================================
async def exemplo_detalhado():
    """Mostra todos os detalhes da resposta"""
    print("\n2️⃣ Query com Processamento Detalhado")
    print("-" * 40)
    print("Pergunta: Explique Python em uma frase")
    print("\nProcessando resposta...")
    
    async for message in query(prompt="Explique Python em uma frase"):
        # Mostra o tipo de cada mensagem recebida
        print(f"\n📨 Mensagem recebida: {type(message).__name__}")
        
        if isinstance(message, AssistantMessage):
            print("   ✅ É uma AssistantMessage!")
            
            # Verifica se content é string ou lista
            if isinstance(message.content, str):
                print(f"   📝 Conteúdo (string): {message.content}")
            elif isinstance(message.content, list):
                print(f"   📦 Conteúdo (lista com {len(message.content)} blocos):")
                for i, block in enumerate(message.content, 1):
                    if isinstance(block, TextBlock):
                        print(f"      Bloco {i}: {block.text}")

# ==========================================
# 3. Query com Múltiplas Perguntas
# ==========================================
async def exemplo_multiplas_perguntas():
    """Fazendo várias perguntas em sequência"""
    print("\n3️⃣ Múltiplas Queries em Sequência")
    print("-" * 40)
    
    perguntas = [
        "O que é uma variável em Python?",
        "Como criar uma função?",
        "O que são listas?"
    ]
    
    for pergunta in perguntas:
        print(f"\n❓ Pergunta: {pergunta}")
        print("💬 Resposta:", end=" ")
        
        async for message in query(prompt=pergunta):
            if isinstance(message, AssistantMessage):
                # Pega apenas o primeiro bloco para manter conciso
                if isinstance(message.content, list) and len(message.content) > 0:
                    first_block = message.content[0]
                    if isinstance(first_block, TextBlock):
                        # Limita a resposta para ficar mais legível
                        texto = first_block.text[:100]
                        if len(first_block.text) > 100:
                            texto += "..."
                        print(texto)
                        break
                elif isinstance(message.content, str):
                    texto = message.content[:100]
                    if len(message.content) > 100:
                        texto += "..."
                    print(texto)
                    break

# ==========================================
# 4. Query com Tratamento de Erros
# ==========================================
async def exemplo_com_tratamento():
    """Mostra como tratar erros e exceções"""
    print("\n4️⃣ Query com Tratamento de Erros")
    print("-" * 40)
    
    try:
        print("Fazendo query...")
        message_count = 0
        
        async for message in query(prompt="Conte até 3 em Python"):
            message_count += 1
            
            if isinstance(message, AssistantMessage):
                print(f"✅ Resposta recebida (mensagem #{message_count})")
                
                # Processa apenas TextBlocks
                text_blocks = []
                if isinstance(message.content, list):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            text_blocks.append(block.text)
                
                if text_blocks:
                    print("📝 Conteúdo dos TextBlocks:")
                    for texto in text_blocks[:3]:  # Limita a 3 blocos
                        print(f"   • {texto[:50]}...")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

# ==========================================
# 5. Query com Coleta de Todas as Respostas
# ==========================================
async def exemplo_coleta_completa():
    """Coleta todas as respostas antes de processar"""
    print("\n5️⃣ Coletando Resposta Completa")
    print("-" * 40)
    
    print("Pergunta: Liste 3 benefícios de Python")
    
    # Coleta todas as mensagens
    todas_mensagens = []
    async for message in query(prompt="Liste 3 benefícios de Python"):
        todas_mensagens.append(message)
    
    # Processa após coletar tudo
    print(f"\n📊 Total de mensagens recebidas: {len(todas_mensagens)}")
    
    for i, msg in enumerate(todas_mensagens, 1):
        print(f"\nMensagem {i}: {type(msg).__name__}")
        
        if isinstance(msg, AssistantMessage):
            print("   Conteúdo do assistente:")
            if isinstance(msg.content, str):
                print(f"   {msg.content[:100]}...")
            elif isinstance(msg.content, list):
                for block in msg.content[:3]:  # Primeiros 3 blocos
                    if isinstance(block, TextBlock):
                        print(f"   • {block.text[:50]}...")

# ==========================================
# 6. Padrão de Uso Recomendado
# ==========================================
async def padrao_recomendado():
    """Padrão mais comum e recomendado de uso"""
    print("\n6️⃣ Padrão de Uso Recomendado")
    print("-" * 40)
    
    prompt = "Como criar uma lista em Python? Seja breve."
    print(f"Prompt: {prompt}")
    print("\nResposta do Claude:")
    
    # Padrão simples e eficaz
    async for message in query(prompt=prompt):
        if isinstance(message, AssistantMessage):
            # Processa content independente do tipo
            if isinstance(message.content, str):
                print(f"   {message.content}")
            elif isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"   {block.text}")

# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================
async def main():
    """Executa todos os exemplos"""
    
    print("\n" + "🔄" * 30)
    print("EXECUTANDO EXEMPLOS ASSÍNCRONOS")
    print("🔄" * 30)
    
    try:
        # Executa cada exemplo
        await exemplo_basico()
        await exemplo_detalhado()
        await exemplo_multiplas_perguntas()
        await exemplo_com_tratamento()
        await exemplo_coleta_completa()
        await padrao_recomendado()
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        print("💡 Dica: Verifique se o Claude Code está configurado corretamente")

# ==========================================
# RESUMO
# ==========================================
print("\n" + "=" * 60)
print("📋 RESUMO DA ETAPA 2 - query()")
print("=" * 60)
print("""
✅ O que aprendemos:
   • query() é uma função assíncrona (usar com async/await)
   • Retorna um AsyncIterator de mensagens
   • Principal tipo de retorno: AssistantMessage
   • content pode ser string ou lista de TextBlocks

📝 Padrão básico:
   async for message in query(prompt="sua pergunta"):
       if isinstance(message, AssistantMessage):
           # processar resposta

🔑 Pontos importantes:
   • SEMPRE verificar tipo com isinstance()
   • content pode ser string OU lista
   • TextBlock tem propriedade .text
   • Use anyio.run(main()) para executar

🎯 Próximo passo:
   • Etapa 3 - ClaudeCodeOptions para personalizar comportamento
""")
print("=" * 60)

# Execução
if __name__ == "__main__":
    print("\n🚀 Iniciando execução assíncrona...")
    print("   (Isso fará chamadas reais à API do Claude)")
    print("-" * 40)
    
    try:
        anyio.run(main)
    except ImportError:
        print("❌ anyio não está instalado")
        print("💡 Instale com: pip install anyio")
    except KeyboardInterrupt:
        print("\n⏹️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
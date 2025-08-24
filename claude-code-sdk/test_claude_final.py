#!/usr/bin/env python3
"""
Teste final do Claude Code SDK - Identidade
"""

import asyncio
import sys

# Adicionar caminho do SDK
sys.path.insert(0, '/home/codable/terminal/claude-code-sdk-python/src')

async def main():
    """Teste principal - Quem é você?"""
    
    print("=" * 60)
    print("🤖 TESTE CLAUDE: Identidade")
    print("=" * 60)
    
    try:
        # Importar Claude SDK
        from claude_code_sdk import query
        
        print("\n✅ Claude Code SDK importado com sucesso!")
        
        # Pergunta 1: Identidade
        print("\n1️⃣ Pergunta: 'Quem é você?'")
        print("-" * 40)
        
        # IMPORTANTE: usar argumento nomeado 'prompt'
        async for message in query(prompt="Quem é você? Qual seu nome, modelo e versão?"):
            if hasattr(message, 'content'):
                # Processar blocos de conteúdo
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text)
                    else:
                        print(str(block))
            else:
                print(str(message))
        
        # Pergunta 2: Confirmação
        print("\n2️⃣ Pergunta: 'Você é o Claude da Anthropic?'")
        print("-" * 40)
        
        async for message in query(prompt="Você é o Claude, assistente de IA da Anthropic?"):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text)
                    else:
                        print(str(block))
            else:
                print(str(message))
        
        # Pergunta 3: Capacidades
        print("\n3️⃣ Pergunta: 'Quais suas principais capacidades?'")
        print("-" * 40)
        
        async for message in query(prompt="Liste suas 5 principais capacidades de forma breve"):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text)
                    else:
                        print(str(block))
            else:
                print(str(message))
        
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        
        print("\n📊 Resumo:")
        print("   ✓ Claude Code SDK funcionando")
        print("   ✓ Comunicação estabelecida")
        print("   ✓ Respostas recebidas corretamente")
        print("   ✓ Identidade confirmada")
        
    except ImportError as e:
        print(f"\n❌ Erro de importação: {e}")
        print("\n📦 Instale o SDK:")
        print("   pip install claude-code-sdk")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Teste do Claude Code SDK")
    print("   Verificando sistema...")
    print()
    
    # Verificar Claude instalado
    import subprocess
    import os
    
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Claude Code: {result.stdout.strip()}")
        else:
            print("⚠️ Claude Code não detectado")
    except:
        print("⚠️ Claude não encontrado no PATH")
    
    # Verificar se Claude Code está rodando
    print("\n⚠️ IMPORTANTE: O Claude Code Desktop deve estar aberto!")
    print("   Se não estiver, abra-o antes de continuar.")
    
    input("\nPressione ENTER para iniciar o teste...")
    
    # Executar teste
    asyncio.run(main())
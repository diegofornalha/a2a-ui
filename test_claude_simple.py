#!/usr/bin/env python3
"""
Teste simples e direto do Claude Code SDK
"""

import asyncio
import sys

# Adicionar caminhos
sys.path.insert(0, '/home/codable/terminal/claude-code-sdk-python/src')

async def main():
    """Teste principal"""
    
    print("=" * 60)
    print("🤖 TESTE: Quem é você?")
    print("=" * 60)
    
    try:
        # Importar Claude SDK
        from claude_code_sdk import query
        
        print("\n✅ Claude Code SDK carregado!")
        
        # Fazer pergunta simples
        print("\n📝 Perguntando ao Claude...")
        print("-" * 40)
        
        # Query simples sem opções extras
        result = await query("Quem é você? Qual seu nome, modelo e versão?")
        
        print("\n🎯 RESPOSTA:")
        print("-" * 40)
        
        # Extrair conteúdo da resposta
        if hasattr(result, 'content'):
            print(result.content)
        else:
            print(str(result))
        
        print("-" * 40)
        print("\n✅ Teste concluído com sucesso!")
        
        # Informações sobre o modelo
        print("\n📊 Informações do Sistema:")
        print(f"   - SDK: claude-code-sdk")
        print(f"   - Método: query() direto")
        print(f"   - Local: Claude Code Desktop")
        
    except ImportError as e:
        print(f"\n❌ Erro de importação: {e}")
        print("\n📦 Instale o SDK:")
        print("   pip install claude-code-sdk")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Iniciando teste do Claude Code SDK...")
    print("   (Certifique-se de que o Claude Code está aberto)")
    print()
    
    # Verificar Claude no sistema
    import subprocess
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"✅ Claude instalado: {result.stdout.strip()}")
    except:
        print("⚠️ Claude Code não encontrado no PATH")
    
    # Executar teste
    asyncio.run(main())
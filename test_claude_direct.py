#!/usr/bin/env python3
"""
Teste direto do Claude Code SDK - Quem é você?
"""

import asyncio
import sys
import os

# Adicionar caminhos necessários
sys.path.insert(0, '/home/codable/terminal/claude-code-sdk-python/src')
sys.path.insert(0, '/home/codable/terminal/ai-sdk-provider-python/src')

async def test_claude_identity():
    """Testa identidade do Claude diretamente via SDK"""
    
    print("=" * 60)
    print("🤖 Teste Direto: Quem é o Claude?")
    print("=" * 60)
    
    try:
        # Importar Claude SDK
        from claude_code_sdk import query, ClaudeCodeOptions
        
        print("\n✅ Claude Code SDK importado com sucesso!")
        
        # Perguntar quem é
        print("\n📝 Perguntando: 'Quem é você?'")
        print("-" * 40)
        
        result = await query(
            "Quem é você? Me diga seu nome, modelo, versão e principais capacidades.",
            options=ClaudeCodeOptions(
                log_level="info"
            )
        )
        
        print("\n🎯 Resposta do Claude:")
        print("-" * 40)
        print(result.content if hasattr(result, 'content') else str(result))
        print("-" * 40)
        
        # Teste adicional - verificar se é realmente o Claude
        print("\n📝 Pergunta de confirmação...")
        result2 = await query("Você é o Claude da Anthropic?")
        
        print("\n🎯 Confirmação:")
        print("-" * 40)
        print(result2.content if hasattr(result2, 'content') else str(result2))
        
        print("\n✅ Teste concluído com sucesso!")
        
    except ImportError as e:
        print(f"\n❌ Erro de importação: {e}")
        print("   Certifique-se de que o Claude Code SDK está instalado:")
        print("   pip install claude-code-sdk")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


async def test_via_provider():
    """Testa via AI SDK Provider"""
    
    print("\n" + "=" * 60)
    print("🔧 Teste via AI SDK Provider")
    print("=" * 60)
    
    try:
        from ai_sdk_provider_claude_code import (
            ClaudeCodeProvider,
            ClaudeCodeSettings
        )
        
        print("\n✅ AI SDK Provider importado!")
        
        # Criar provider
        settings = ClaudeCodeSettings(
            model_id="opus",
            verbose=True
        )
        provider = ClaudeCodeProvider(settings=settings)
        
        print("\n📝 Testando via provider...")
        
        # Criar modelo de linguagem
        model = provider.language_model("opus")
        
        # Gerar resposta
        messages = [
            {"role": "user", "content": "Quem é você? Qual seu nome e modelo?"}
        ]
        
        result = await model.do_generate({
            "inputFormat": "messages",
            "mode": {"type": "regular"},
            "messages": messages,
            "system": "Você é o Claude, assistente da Anthropic."
        })
        
        print("\n🎯 Resposta via Provider:")
        print("-" * 40)
        print(result.text if hasattr(result, 'text') else str(result))
        
    except ImportError as e:
        print(f"\n⚠️ Provider não disponível: {e}")
    except Exception as e:
        print(f"\n❌ Erro no provider: {e}")


def main():
    """Função principal"""
    
    # Verificar se Claude está instalado
    import subprocess
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Claude Code detectado: {result.stdout.strip()}")
        else:
            print("⚠️ Claude Code não detectado no PATH")
    except:
        print("⚠️ Claude Code não encontrado")
        print("   Instale em: https://claude.ai/code")
        print("   Continuando teste mesmo assim...")
    
    # Executar testes
    asyncio.run(test_claude_identity())
    asyncio.run(test_via_provider())
    
    print("\n" + "=" * 60)
    print("🏁 Todos os testes concluídos!")
    print("=" * 60)


if __name__ == "__main__":
    main()
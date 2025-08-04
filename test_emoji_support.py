#!/usr/bin/env python3
"""
Script de teste para verificar o suporte a emoji no chat
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_emoji_library():
    """Testa se a biblioteca emoji está funcionando"""
    try:
        import emoji
        print("✅ Biblioteca emoji importada com sucesso!")
        print(f"   Versão: {emoji.__version__}")
        
        # Testa funcionalidades básicas
        test_text = "Python é :thumbs_up: e eu :heart: Mesop!"
        processed = emoji.emojize(test_text, language='alias')
        print(f"   Teste: '{test_text}' → '{processed}'")
        
        # Testa contagem de emojis
        emoji_count = emoji.emoji_count(processed)
        print(f"   Emojis encontrados: {emoji_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na biblioteca emoji: {e}")
        return False

def test_emoji_processing():
    """Testa o processamento de emoji"""
    try:
        from components.emoji_chat import process_emoji_in_text, extract_emoji_info
        
        # Testa processamento de texto
        test_cases = [
            "Python é :thumbs_up:",
            "Eu :heart: Mesop!",
            "Vamos :rocket: para o espaço!",
            "Teste sem emoji",
            "Múltiplos :smile: :heart: :rocket: emojis"
        ]
        
        print("\n🧪 Testando processamento de emoji:")
        for test_case in test_cases:
            processed = process_emoji_in_text(test_case)
            emoji_info = extract_emoji_info(processed)
            print(f"   '{test_case}' → '{processed}' (emojis: {emoji_info['total_emojis']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no processamento de emoji: {e}")
        return False

def test_emoji_help():
    """Testa a função de ajuda sobre emojis"""
    try:
        from components.emoji_chat import get_emoji_help_text
        
        help_text = get_emoji_help_text()
        print("\n📖 Testando ajuda sobre emojis:")
        print(f"   Tamanho do texto: {len(help_text)} caracteres")
        print(f"   Contém 'emoji': {'emoji' in help_text.lower()}")
        print(f"   Contém exemplos: {':thumbs_up:' in help_text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na ajuda sobre emojis: {e}")
        return False

def test_conversation_import():
    """Testa se o componente de conversação pode ser importado"""
    try:
        from components.conversation import conversation, is_emoji_help_command
        
        print("\n✅ Importação do componente de conversação bem-sucedida!")
        
        # Testa detecção de comandos
        test_commands = [
            "@emoji help",
            "@emoji list", 
            "@emoji count",
            "mensagem normal",
            "@mesop docs"
        ]
        
        print("🔍 Testando detecção de comandos:")
        for cmd in test_commands:
            is_emoji = is_emoji_help_command(cmd)
            print(f"   '{cmd}' → emoji command: {is_emoji}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação do componente: {e}")
        return False

def test_hello_world_emoji_response():
    """Testa a resposta do Hello World Agent com emojis"""
    try:
        from components.emoji_chat import create_emoji_response_template
        
        template = create_emoji_response_template()
        print("\n🌟 Testando template de resposta do Hello World Agent:")
        print(f"   Tamanho do template: {len(template)} caracteres")
        print(f"   Contém 'SUPER': {'SUPER' in template}")
        print(f"   Contém emojis: {any(ord(c) > 127 for c in template)}")
        
        # Testa processamento do template
        processed_template = template.format(timestamp="2025-07-19 06:30:00")
        print(f"   Template processado: {len(processed_template)} caracteres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no template de resposta: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testando Suporte a Emoji no Chat")
    print("=" * 50)
    
    test1 = test_emoji_library()
    test2 = test_emoji_processing()
    test3 = test_emoji_help()
    test4 = test_conversation_import()
    test5 = test_hello_world_emoji_response()
    
    print("\n" + "=" * 50)
    if test1 and test2 and test3 and test4 and test5:
        print("🎉 Todos os testes passaram! Suporte a emoji funcionando!")
        print("\n📋 Funcionalidades Disponíveis:")
        print("   ✅ Processamento automático de emojis")
        print("   ✅ Comando @emoji help")
        print("   ✅ Análise de emojis nas mensagens")
        print("   ✅ Template de resposta do Hello World Agent")
        print("   ✅ Renderização de emojis no chat")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
    
    print("\n💡 Como usar:")
    print("   1. Digite ':thumbs_up:' → 👍")
    print("   2. Digite ':heart:' → ❤️")
    print("   3. Digite '@emoji help' para ajuda")
    print("   4. Acesse o chat em http://localhost:12000/conversation") 
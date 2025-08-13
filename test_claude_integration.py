#!/usr/bin/env python3
"""
Script de teste para verificar a integração do Claude com A2A-UI
Testa todos os componentes criados
"""

import asyncio
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_claude_cli_client():
    """Testa o cliente Claude CLI"""
    print("\n🧪 Testando Claude CLI Client...")
    print("-" * 50)
    
    try:
        from service.client.claude_cli_client import ClaudeCLIClient
        
        client = ClaudeCLIClient()
        print("✅ Cliente inicializado")
        
        # Teste básico
        connected = await client.test_connection()
        if connected:
            print("✅ Conexão com Claude CLI funcionando")
        else:
            print("❌ Claude CLI não está respondendo")
            print("   Verifique se está instalado e logado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar cliente: {e}")
        return False


async def test_claude_agent():
    """Testa o agente Claude"""
    print("\n🧪 Testando Claude Agent...")
    print("-" * 50)
    
    try:
        from agents.claude_agent import get_claude_agent
        
        agent = get_claude_agent()
        print("✅ Agente inicializado")
        
        # Verificar status
        status = agent.get_status()
        print(f"📊 Status: {status['is_ready']}")
        print(f"📋 Capacidades: {', '.join(status['capabilities'])}")
        
        if not status['is_ready']:
            print("❌ Agente não está pronto")
            return False
        
        # Card do agente
        card = agent.get_agent_card()
        print(f"🎴 Agent ID: {card['id']}")
        print(f"📝 Descrição: {card['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar agente: {e}")
        return False


async def test_claude_service():
    """Testa o serviço Claude"""
    print("\n🧪 Testando Claude Service...")
    print("-" * 50)
    
    try:
        from service.server.claude_service import get_claude_service
        
        service = get_claude_service()
        print("✅ Serviço inicializado")
        
        # Verificar status
        status = service.get_status()
        print(f"📊 Inicializado: {status['initialized']}")
        print(f"🤖 Agente pronto: {status['agent_ready']}")
        
        if not status['initialized']:
            print("❌ Serviço não está inicializado")
            return False
        
        # Info do agente
        info = service.get_agent_info()
        print(f"📋 Nome: {info.get('name', 'N/A')}")
        print(f"🔧 Versão: {info.get('version', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar serviço: {e}")
        return False


def test_backend_imports():
    """Testa se o backend pode importar os módulos Claude"""
    print("\n🧪 Testando imports do backend...")
    print("-" * 50)
    
    try:
        # Tentar importar como o backend faria
        from service.server.claude_service import get_claude_service
        print("✅ Import do claude_service funcionando")
        
        # Verificar se o serviço pode ser criado
        service = get_claude_service()
        if service:
            print("✅ Serviço pode ser instanciado")
            return True
        else:
            print("❌ Falha ao criar instância do serviço")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False


def test_mesop_page():
    """Testa se a página Mesop pode ser importada"""
    print("\n🧪 Testando página Mesop...")
    print("-" * 50)
    
    try:
        from pages.claude_chat import claude_chat_page
        print("✅ Import da página claude_chat funcionando")
        
        # Verificar se a função existe
        if callable(claude_chat_page):
            print("✅ Função claude_chat_page disponível")
            return True
        else:
            print("❌ Função não é callable")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False


def check_files():
    """Verifica se todos os arquivos foram criados"""
    print("\n📁 Verificando arquivos criados...")
    print("-" * 50)
    
    files_to_check = [
        "service/client/claude_cli_client.py",
        "agents/claude_agent.py",
        "service/server/claude_service.py",
        "pages/claude_chat.py",
        "agent_cards/claude_agent.json",
        "start_a2a_with_claude.sh"
    ]
    
    all_exist = True
    for file in files_to_check:
        path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NÃO ENCONTRADO")
            all_exist = False
    
    return all_exist


async def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🔍 TESTE DE INTEGRAÇÃO CLAUDE + A2A-UI")
    print("=" * 60)
    
    results = []
    
    # 1. Verificar arquivos
    print("\n" + "=" * 60)
    print("ETAPA 1: Verificação de Arquivos")
    print("=" * 60)
    results.append(("Arquivos", check_files()))
    
    # 2. Testar cliente CLI
    print("\n" + "=" * 60)
    print("ETAPA 2: Cliente Claude CLI")
    print("=" * 60)
    results.append(("Cliente CLI", await test_claude_cli_client()))
    
    # 3. Testar agente
    print("\n" + "=" * 60)
    print("ETAPA 3: Agente Claude")
    print("=" * 60)
    results.append(("Agente", await test_claude_agent()))
    
    # 4. Testar serviço
    print("\n" + "=" * 60)
    print("ETAPA 4: Serviço Claude")
    print("=" * 60)
    results.append(("Serviço", await test_claude_service()))
    
    # 5. Testar imports do backend
    print("\n" + "=" * 60)
    print("ETAPA 5: Imports do Backend")
    print("=" * 60)
    results.append(("Backend Imports", test_backend_imports()))
    
    # 6. Testar página Mesop
    print("\n" + "=" * 60)
    print("ETAPA 6: Página Mesop")
    print("=" * 60)
    results.append(("Página Mesop", test_mesop_page()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n📝 Próximos passos:")
        print("1. Execute: ./start_a2a_with_claude.sh")
        print("2. Acesse: http://localhost:12000")
        print("3. Navegue para: http://localhost:12000/claude")
        print("4. Teste a interface do Claude Assistant!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima e corrija antes de continuar")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
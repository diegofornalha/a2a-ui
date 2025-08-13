#!/usr/bin/env python3
"""
Script de demonstração dos testes de API A2A.
Este script mostra como usar a estrutura de testes criada.
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_section(title):
    """Imprime seção formatada."""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_demo():
    """Executa demonstração dos testes."""
    print_header("DEMONSTRAÇÃO DOS TESTES DE API A2A")
    
    # Verifica se estamos no diretório correto
    current_dir = Path.cwd()
    if not (current_dir / "conftest.py").exists():
        print("❌ Execute este script do diretório tests/api/")
        return False
    
    print(f"📂 Diretório: {current_dir}")
    
    # Ativa ambiente virtual se existir
    venv_python = current_dir / "venv" / "bin" / "python"
    if venv_python.exists():
        python_cmd = str(venv_python)
        print("🐍 Usando ambiente virtual")
    else:
        python_cmd = "python"
        print("🐍 Usando Python do sistema")
    
    # Lista arquivos de teste
    print_section("Arquivos de Teste Disponíveis")
    test_files = list(current_dir.glob("test_*.py"))
    for i, test_file in enumerate(test_files, 1):
        print(f"{i:2d}. {test_file.name}")
    
    # Mostra configuração pytest
    print_section("Configuração Pytest")
    if (current_dir / "pytest.ini").exists():
        print("✅ pytest.ini configurado")
    else:
        print("❌ pytest.ini não encontrado")
    
    # Mostra marcadores disponíveis
    print_section("Marcadores Disponíveis")
    markers = [
        "agent_card - Testes de descoberta de agente",
        "message_send - Testes de envio de mensagem", 
        "message_stream - Testes de streaming",
        "error_handling - Testes de tratamento de erros",
        "integration - Testes de integração",
        "slow - Testes que podem demorar"
    ]
    for marker in markers:
        print(f"  🏷️  {marker}")
    
    # Verifica variáveis de ambiente
    print_section("Configuração de Ambiente")
    test_url = os.getenv('A2A_TEST_URL', 'http://localhost:8000')
    timeout = os.getenv('A2A_TEST_TIMEOUT', '30')
    print(f"🌐 URL de teste: {test_url}")
    print(f"⏱️  Timeout: {timeout}s")
    
    # Executa teste de validação
    print_section("Executando Teste de Validação")
    try:
        result = subprocess.run([
            python_cmd, "-m", "pytest", 
            "test_simple_validation.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Validação passou!")
            # Mostra apenas resumo
            lines = result.stdout.split('\n')
            for line in lines:
                if "passed" in line and "in" in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ Validação falhou!")
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
                
    except Exception as e:
        print(f"❌ Erro ao executar validação: {e}")
    
    # Mostra comandos úteis
    print_section("Comandos Úteis para Testes")
    commands = [
        ("Todos os testes", f"{python_cmd} -m pytest -v"),
        ("Apenas AgentCard", f"{python_cmd} -m pytest test_agent_card.py -v"),
        ("Apenas erros", f"{python_cmd} -m pytest -m error_handling -v"),
        ("Com relatório HTML", f"{python_cmd} -m pytest --html=report.html"),
        ("Com cobertura", f"{python_cmd} -m pytest --cov=. --cov-report=html"),
        ("Parar no primeiro erro", f"{python_cmd} -m pytest -x"),
        ("Testes não lentos", f"{python_cmd} -m pytest -m 'not slow'"),
        ("Usando script", f"{python_cmd} run_tests.py --verbose")
    ]
    
    for desc, cmd in commands:
        print(f"  📝 {desc}:")
        print(f"     {cmd}")
    
    # Instruções para teste real
    print_section("Para Testar um Servidor A2A Real")
    instructions = [
        "1. Inicie um servidor A2A (ex: HelloWorld)",
        "2. Configure a URL no arquivo .env:",
        "   echo 'A2A_TEST_URL=http://localhost:9999' > .env",
        "3. Execute os testes:",
        f"   {python_cmd} run_tests.py --url http://localhost:9999 --verbose",
        "4. Para testes específicos:",
        f"   {python_cmd} -m pytest test_agent_card.py -v",
        "5. Para debugging:",
        f"   {python_cmd} -m pytest test_agent_card.py::TestAgentCard::test_agent_card_discovery -v -s"
    ]
    
    for instruction in instructions:
        print(f"  {instruction}")
    
    # Estrutura dos testes
    print_section("Estrutura dos Testes")
    structure = [
        "test_agent_card.py - Testa /.well-known/agent.json",
        "test_message_send.py - Testa /message/send (JSON-RPC)",
        "test_message_stream.py - Testa /message/stream (SSE)",
        "test_error_handling.py - Testa cenários de erro",
        "test_helloworld_integration.py - Teste completo HelloWorld",
        "test_simple_validation.py - Validação da estrutura"
    ]
    
    for item in structure:
        print(f"  📄 {item}")
    
    print_header("DEMONSTRAÇÃO CONCLUÍDA")
    print("🎉 Estrutura de testes A2A criada com sucesso!")
    print("📚 Consulte o README.md para documentação completa")
    print("🚀 Execute os testes quando tiver um servidor A2A rodando")
    
    return True

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
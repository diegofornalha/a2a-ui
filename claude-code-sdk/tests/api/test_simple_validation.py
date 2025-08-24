"""
Teste simples de validação da estrutura de testes.
"""
import pytest
import os
from pathlib import Path

class TestValidation:
    """Testes de validação da estrutura."""
    
    def test_pytest_configuration(self):
        """Verifica se pytest está configurado corretamente."""
        # Verifica se estamos no diretório correto
        current_dir = Path.cwd()
        assert "tests/api" in str(current_dir) or "marseille" in str(current_dir), \
            f"Executando do diretório correto: {current_dir}"
        
        print(f"✅ Diretório de execução: {current_dir}")
    
    def test_environment_variables(self):
        """Verifica variáveis de ambiente para testes."""
        # URL padrão se não configurada
        test_url = os.getenv('A2A_TEST_URL', 'http://localhost:8000')
        print(f"✅ URL de teste: {test_url}")
        
        # Timeout padrão
        timeout = int(os.getenv('A2A_TEST_TIMEOUT', '30'))
        assert timeout > 0, "Timeout deve ser positivo"
        print(f"✅ Timeout: {timeout}s")
    
    def test_imports(self):
        """Verifica se as importações necessárias funcionam."""
        try:
            import requests
            print(f"✅ requests: {requests.__version__}")
        except ImportError:
            pytest.fail("requests não está instalado. Execute: pip install requests")
        
        try:
            import pytest
            print(f"✅ pytest: {pytest.__version__}")
        except ImportError:
            pytest.fail("pytest não está disponível")
    
    def test_fixtures_available(self, base_url, headers, sample_message, jsonrpc_request_template):
        """Verifica se todas as fixtures estão disponíveis."""
        assert base_url, "Fixture base_url deve estar disponível"
        assert headers, "Fixture headers deve estar disponível"
        assert sample_message, "Fixture sample_message deve estar disponível"
        assert jsonrpc_request_template, "Fixture jsonrpc_request_template deve estar disponível"
        
        print(f"✅ base_url: {base_url}")
        print(f"✅ headers: {headers}")
        print(f"✅ sample_message: {sample_message}")
        print(f"✅ jsonrpc_request_template: {jsonrpc_request_template}")
    
    def test_file_structure(self):
        """Verifica se a estrutura de arquivos está correta."""
        test_dir = Path(__file__).parent
        
        required_files = [
            "__init__.py",
            "conftest.py",
            "pytest.ini",
            "requirements.txt",
            "README.md",
            "test_agent_card.py",
            "test_message_send.py",
            "test_message_stream.py",
            "test_error_handling.py",
            "test_helloworld_integration.py",
            "run_tests.py"
        ]
        
        for filename in required_files:
            file_path = test_dir / filename
            assert file_path.exists(), f"Arquivo obrigatório não encontrado: {filename}"
        
        print(f"✅ Todos os arquivos obrigatórios estão presentes")
        print(f"   Diretório de testes: {test_dir}")
        print(f"   Total de arquivos verificados: {len(required_files)}")
    
    def test_readme_content(self):
        """Verifica se o README tem conteúdo básico."""
        readme_path = Path(__file__).parent / "README.md"
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            "# Testes de API A2A",
            "## Estrutura dos Testes",
            "## Como Executar",
            "AgentCard",
            "Message Send",
            "Message Stream",
            "Error Handling"
        ]
        
        for section in required_sections:
            assert section in content, f"Seção obrigatória não encontrada no README: {section}"
        
        print("✅ README.md tem todas as seções obrigatórias")
    
    def test_pytest_markers(self):
        """Verifica se os marcadores pytest estão configurados."""
        pytest_ini_path = Path(__file__).parent / "pytest.ini"
        
        with open(pytest_ini_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_markers = [
            "agent_card",
            "message_send", 
            "message_stream",
            "error_handling",
            "integration",
            "slow"
        ]
        
        for marker in required_markers:
            assert marker in content, f"Marcador não encontrado no pytest.ini: {marker}"
        
        print("✅ Todos os marcadores pytest estão configurados")
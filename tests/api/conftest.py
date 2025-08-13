"""
Configuração dos testes de API A2A.
"""
import pytest
import os
from typing import Dict, Any

@pytest.fixture
def base_url():
    """URL base do servidor A2A para testes."""
    return os.getenv('A2A_TEST_URL', 'http://localhost:8000')

@pytest.fixture
def headers():
    """Headers padrão para requisições A2A."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

@pytest.fixture
def sample_message():
    """Mensagem de exemplo para testes."""
    return {
        "role": "user",
        "parts": [
            {
                "kind": "text",
                "text": "Hello, this is a test message"
            }
        ],
        "messageId": "test-msg-001"
    }

@pytest.fixture
def jsonrpc_request_template():
    """Template básico para requisições JSON-RPC."""
    return {
        "jsonrpc": "2.0",
        "id": "test-request-001",
        "method": "",
        "params": {}
    }
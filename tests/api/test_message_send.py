"""
Testes para o endpoint /message/send (JSON-RPC).
"""
import pytest
import requests
import json
from typing import Dict, Any

class TestMessageSend:
    """Testes para envio de mensagens via JSON-RPC."""
    
    def test_message_send_basic(self, base_url: str, headers: Dict[str, str], 
                              sample_message: Dict[str, Any], 
                              jsonrpc_request_template: Dict[str, Any]):
        """Testa envio básico de mensagem."""
        url = f"{base_url}/message/send"
        
        # Prepara requisição JSON-RPC
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/send"
        request_data["params"] = {
            "message": sample_message
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        # Verifica status HTTP
        assert response.status_code == 200, f"Status esperado: 200, recebido: {response.status_code}"
        
        # Verifica se é JSON válido
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            pytest.fail("Resposta não é um JSON válido")
        
        # Validações JSON-RPC
        assert "jsonrpc" in response_data, "Resposta deve incluir campo jsonrpc"
        assert response_data["jsonrpc"] == "2.0", "Deve usar JSON-RPC 2.0"
        assert "id" in response_data, "Resposta deve incluir ID da requisição"
        assert response_data["id"] == request_data["id"], "ID da resposta deve corresponder ao da requisição"
        
        # Verifica se há resultado ou erro
        has_result = "result" in response_data
        has_error = "error" in response_data
        
        assert has_result or has_error, "Resposta deve conter 'result' ou 'error'"
        assert not (has_result and has_error), "Resposta não pode conter 'result' e 'error' simultaneamente"
        
        if has_result:
            result = response_data["result"]
            # Pode ser uma Message ou Task
            assert "type" in result or "kind" in result, "Resultado deve ter type ou kind"
            print(f"✅ Mensagem enviada com sucesso: {result}")
        else:
            error = response_data["error"]
            print(f"❌ Erro na requisição: {error}")
    
    def test_message_send_invalid_jsonrpc(self, base_url: str, headers: Dict[str, str]):
        """Testa envio com JSON-RPC malformado."""
        url = f"{base_url}/message/send"
        
        # JSON-RPC inválido (sem versão)
        invalid_request = {
            "id": "test-invalid",
            "method": "message/send",
            "params": {}
        }
        
        response = requests.post(url, json=invalid_request, headers=headers)
        
        # Deve retornar erro
        assert response.status_code == 200  # JSON-RPC usa 200 mesmo para erros
        response_data = response.json()
        
        assert "error" in response_data, "Deve retornar erro para JSON-RPC inválido"
        error = response_data["error"]
        assert error["code"] == -32600, "Código de erro deve ser -32600 (Invalid Request)"
        
        print(f"✅ Erro detectado corretamente: {error}")
    
    def test_message_send_missing_params(self, base_url: str, headers: Dict[str, str],
                                       jsonrpc_request_template: Dict[str, Any]):
        """Testa envio sem parâmetros obrigatórios."""
        url = f"{base_url}/message/send"
        
        # Requisição sem parâmetros
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/send"
        # Não inclui params
        
        response = requests.post(url, json=request_data, headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "error" in response_data, "Deve retornar erro para parâmetros faltando"
        error = response_data["error"]
        assert error["code"] == -32602, "Código de erro deve ser -32602 (Invalid params)"
        
        print(f"✅ Erro de parâmetros detectado: {error}")
    
    def test_message_send_with_context(self, base_url: str, headers: Dict[str, str],
                                     jsonrpc_request_template: Dict[str, Any]):
        """Testa envio de mensagem com contexto."""
        url = f"{base_url}/message/send"
        
        # Mensagem com contextId
        message_with_context = {
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": "This is a follow-up message"
                }
            ],
            "messageId": "test-msg-002",
            "contextId": "test-context-001"
        }
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/send"
        request_data["params"] = {
            "message": message_with_context
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verifica se o contexto é preservado na resposta
        if "result" in response_data:
            result = response_data["result"]
            if "contextId" in result:
                assert result["contextId"] == "test-context-001", \
                    "ContextId deve ser preservado"
            print(f"✅ Mensagem com contexto enviada: {result}")
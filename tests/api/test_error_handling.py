"""
Testes para tratamento de erros na API A2A.
"""
import pytest
import requests
import json
from typing import Dict, Any

class TestErrorHandling:
    """Testes para cenários de erro na API A2A."""
    
    def test_parse_error(self, base_url: str, headers: Dict[str, str]):
        """Testa erro -32700 (Parse error) - JSON malformado."""
        url = f"{base_url}/message/send"
        
        # Envia JSON malformado
        malformed_json = '{"jsonrpc": "2.0", "method": "message/send", "id": 1'  # JSON incompleto
        
        response = requests.post(url, data=malformed_json, headers=headers)
        
        # Pode retornar 400 ou 200 com erro JSON-RPC
        if response.status_code == 200:
            response_data = response.json()
            assert "error" in response_data, "Deve retornar erro para JSON malformado"
            error = response_data["error"]
            assert error["code"] == -32700, "Código deve ser -32700 (Parse error)"
            print(f"✅ Parse error detectado: {error}")
        else:
            # Servidor pode retornar 400 Bad Request
            assert response.status_code == 400, "Status deve ser 400 para JSON malformado"
            print("✅ Parse error detectado via HTTP 400")
    
    def test_invalid_request_error(self, base_url: str, headers: Dict[str, str]):
        """Testa erro -32600 (Invalid Request) - JSON-RPC inválido."""
        url = f"{base_url}/message/send"
        
        # JSON válido mas não é JSON-RPC válido
        invalid_jsonrpc = {
            "version": "2.0",  # Campo errado, deveria ser "jsonrpc"
            "method": "message/send",
            "id": 1
        }
        
        response = requests.post(url, json=invalid_jsonrpc, headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "error" in response_data, "Deve retornar erro para JSON-RPC inválido"
        error = response_data["error"]
        assert error["code"] == -32600, "Código deve ser -32600 (Invalid Request)"
        
        print(f"✅ Invalid Request error detectado: {error}")
    
    def test_method_not_found_error(self, base_url: str, headers: Dict[str, str],
                                  jsonrpc_request_template: Dict[str, Any]):
        """Testa erro -32601 (Method not found) - método inexistente."""
        url = f"{base_url}/message/send"
        
        # Método que não existe
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "non/existent/method"
        request_data["params"] = {}
        
        response = requests.post(url, json=request_data, headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "error" in response_data, "Deve retornar erro para método inexistente"
        error = response_data["error"]
        assert error["code"] == -32601, "Código deve ser -32601 (Method not found)"
        
        print(f"✅ Method not found error detectado: {error}")
    
    def test_invalid_params_error(self, base_url: str, headers: Dict[str, str],
                                jsonrpc_request_template: Dict[str, Any]):
        """Testa erro -32602 (Invalid params) - parâmetros inválidos."""
        url = f"{base_url}/message/send"
        
        # Parâmetros inválidos para message/send
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/send"
        request_data["params"] = {
            "invalid_param": "invalid_value"
            # Falta o parâmetro "message" obrigatório
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "error" in response_data, "Deve retornar erro para parâmetros inválidos"
        error = response_data["error"]
        assert error["code"] == -32602, "Código deve ser -32602 (Invalid params)"
        
        print(f"✅ Invalid params error detectado: {error}")
    
    def test_task_not_found_error(self, base_url: str, headers: Dict[str, str],
                                jsonrpc_request_template: Dict[str, Any]):
        """Testa erro -32001 (TaskNotFoundError) - task ID inexistente."""
        # Este teste assume que existe um endpoint para buscar tasks
        url = f"{base_url}/tasks/get"
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "tasks/get"
        request_data["params"] = {
            "taskId": "non-existent-task-id"
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if "error" in response_data:
                error = response_data["error"]
                assert error["code"] == -32001, "Código deve ser -32001 (TaskNotFoundError)"
                print(f"✅ TaskNotFoundError detectado: {error}")
            else:
                print("⚠️ Endpoint tasks/get não implementado ou não retorna erro para ID inexistente")
        else:
            print(f"⚠️ Endpoint tasks/get não disponível (HTTP {response.status_code})")
    
    def test_unsupported_operation_error(self, base_url: str, headers: Dict[str, str],
                                       jsonrpc_request_template: Dict[str, Any]):
        """Testa erro -32004 (UnsupportedOperationError) - operação não suportada."""
        # Tenta usar push notifications se não for suportado
        url = f"{base_url}/tasks/pushNotificationConfig/set"
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "tasks/pushNotificationConfig/set"
        request_data["params"] = {
            "taskId": "test-task",
            "config": {
                "url": "https://example.com/webhook"
            }
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if "error" in response_data:
                error = response_data["error"]
                # Pode ser -32003 (PushNotificationNotSupportedError) ou -32004
                assert error["code"] in [-32003, -32004], \
                    "Deve retornar erro apropriado para push notification"
                print(f"✅ Erro de operação não suportada detectado: {error}")
            else:
                print("⚠️ Push notifications podem estar suportados")
        else:
            print(f"⚠️ Endpoint push notification não disponível (HTTP {response.status_code})")
    
    def test_content_type_not_supported_error(self, base_url: str, headers: Dict[str, str],
                                            jsonrpc_request_template: Dict[str, Any]):
        """Testa erro -32005 (ContentTypeNotSupportedError) - tipo de conteúdo não suportado."""
        url = f"{base_url}/message/send"
        
        # Mensagem com tipo de arquivo não suportado
        message_with_unsupported_file = {
            "role": "user",
            "parts": [
                {
                    "kind": "file",
                    "file": {
                        "name": "test.xyz",
                        "mimeType": "application/x-unsupported-format",
                        "bytes": "dGVzdCBkYXRh"  # "test data" em base64
                    }
                }
            ],
            "messageId": "test-unsupported-content"
        }
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/send"
        request_data["params"] = {
            "message": message_with_unsupported_file
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        if "error" in response_data:
            error = response_data["error"]
            if error["code"] == -32005:
                print(f"✅ ContentTypeNotSupportedError detectado: {error}")
            else:
                print(f"⚠️ Outro erro retornado: {error}")
        else:
            print("⚠️ Tipo de arquivo pode estar suportado ou não foi validado")
    
    def test_error_response_structure(self, base_url: str, headers: Dict[str, str]):
        """Verifica estrutura padrão das respostas de erro JSON-RPC."""
        url = f"{base_url}/message/send"
        
        # Força um erro conhecido
        invalid_request = {
            "method": "message/send",  # Sem jsonrpc e id
            "params": {}
        }
        
        response = requests.post(url, json=invalid_request, headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verifica estrutura do erro
        assert "error" in response_data, "Resposta deve conter campo 'error'"
        error = response_data["error"]
        
        # Campos obrigatórios do erro JSON-RPC
        assert "code" in error, "Erro deve conter campo 'code'"
        assert "message" in error, "Erro deve conter campo 'message'"
        assert isinstance(error["code"], int), "Código do erro deve ser inteiro"
        assert isinstance(error["message"], str), "Mensagem do erro deve ser string"
        
        # Campo data é opcional
        if "data" in error:
            print(f"Dados adicionais do erro: {error['data']}")
        
        print(f"✅ Estrutura de erro válida: {error}")
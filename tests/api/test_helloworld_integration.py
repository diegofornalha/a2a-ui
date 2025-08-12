"""
Teste de integração específico para o agente HelloWorld.
Este é um exemplo prático de teste completo.
"""
import pytest
import requests
import json
import time
from typing import Dict, Any

class TestHelloworldIntegration:
    """Testes de integração para o agente HelloWorld A2A."""
    
    @pytest.fixture
    def helloworld_message(self):
        """Mensagem específica para o HelloWorld."""
        return {
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": "Hello World"
                }
            ],
            "messageId": "helloworld-test-001"
        }
    
    def test_helloworld_agent_discovery(self, base_url: str):
        """Testa descoberta do agente HelloWorld."""
        url = f"{base_url}/.well-known/agent.json"
        
        response = requests.get(url)
        assert response.status_code == 200, f"AgentCard não encontrado: {response.status_code}"
        
        agent_card = response.json()
        
        # Validações específicas do HelloWorld
        assert "name" in agent_card, "AgentCard deve ter nome"
        assert "helloworld" in agent_card["name"].lower(), \
            f"Esperado agente HelloWorld, encontrado: {agent_card['name']}"
        
        print(f"✅ Agente HelloWorld descoberto: {agent_card['name']}")
        print(f"   Versão: {agent_card.get('version', 'N/A')}")
        print(f"   Descrição: {agent_card.get('description', 'N/A')}")
        
        return agent_card
    
    def test_helloworld_basic_interaction(self, base_url: str, headers: Dict[str, str],
                                        helloworld_message: Dict[str, Any],
                                        jsonrpc_request_template: Dict[str, Any]):
        """Testa interação básica com HelloWorld."""
        url = f"{base_url}/message/send"
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/send"
        request_data["params"] = {
            "message": helloworld_message
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        assert response.status_code == 200, f"Erro na requisição: {response.status_code}"
        
        response_data = response.json()
        assert "result" in response_data, f"Resposta deve conter result: {response_data}"
        
        result = response_data["result"]
        
        # Verifica se é uma mensagem direta ou task
        if result.get("type") == "message":
            # Resposta direta
            assert result["role"] == "agent", "Resposta deve vir do agente"
            assert "parts" in result, "Mensagem deve ter parts"
            
            # Verifica conteúdo da resposta
            text_parts = [part for part in result["parts"] if part.get("kind") == "text"]
            assert len(text_parts) > 0, "Deve haver pelo menos uma parte de texto"
            
            response_text = text_parts[0]["text"].lower()
            assert "hello" in response_text, f"Resposta deve conter 'hello': {response_text}"
            
            print(f"✅ HelloWorld respondeu: {text_parts[0]['text']}")
            
        elif result.get("kind") == "task":
            # Resposta como task
            assert "id" in result, "Task deve ter ID"
            assert "status" in result, "Task deve ter status"
            
            task_status = result["status"]["state"]
            print(f"✅ Task criada com status: {task_status}")
            
            # Se task está completa, verifica artifacts
            if task_status == "completed" and "artifacts" in result:
                artifacts = result["artifacts"]
                assert len(artifacts) > 0, "Deve haver pelo menos um artifact"
                print(f"✅ {len(artifacts)} artifacts encontrados")
        
        else:
            pytest.fail(f"Tipo de resposta não reconhecido: {result}")
    
    def test_helloworld_streaming(self, base_url: str, headers: Dict[str, str],
                                helloworld_message: Dict[str, Any],
                                jsonrpc_request_template: Dict[str, Any]):
        """Testa streaming com HelloWorld (se suportado)."""
        # Primeiro verifica se streaming é suportado
        agent_card_url = f"{base_url}/.well-known/agent.json"
        agent_response = requests.get(agent_card_url)
        
        if agent_response.status_code == 200:
            agent_card = agent_response.json()
            capabilities = agent_card.get('capabilities', {})
            
            if not capabilities.get('streaming', False):
                pytest.skip("Agente HelloWorld não suporta streaming")
        
        # Testa streaming
        url = f"{base_url}/message/stream"
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/stream"
        request_data["params"] = {
            "message": helloworld_message
        }
        
        stream_headers = headers.copy()
        stream_headers["Accept"] = "text/event-stream"
        
        response = requests.post(url, json=request_data, headers=stream_headers, stream=True)
        
        assert response.status_code == 200, f"Erro no streaming: {response.status_code}"
        
        # Processa eventos SSE
        events_received = []
        final_received = False
        
        try:
            for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                if line.startswith('data: '):
                    event_data = line[6:]
                    try:
                        event_json = json.loads(event_data)
                        events_received.append(event_json)
                        
                        # Verifica se é evento final
                        if ("result" in event_json and 
                            event_json["result"].get("final") == True):
                            final_received = True
                            break
                            
                    except json.JSONDecodeError:
                        continue  # Ignora linhas que não são JSON
                
                # Timeout de segurança
                if len(events_received) > 20:
                    break
                    
        except Exception as e:
            print(f"⚠️ Erro ao processar stream: {e}")
        
        assert len(events_received) > 0, "Deve receber pelo menos um evento"
        
        if final_received:
            print(f"✅ Streaming completo: {len(events_received)} eventos, evento final recebido")
        else:
            print(f"⚠️ Streaming parcial: {len(events_received)} eventos, sem evento final")
    
    def test_helloworld_multiple_messages(self, base_url: str, headers: Dict[str, str],
                                        jsonrpc_request_template: Dict[str, Any]):
        """Testa múltiplas mensagens sequenciais."""
        url = f"{base_url}/message/send"
        
        messages = [
            "Hello",
            "How are you?",
            "Thank you!",
            "Goodbye"
        ]
        
        contextId = "helloworld-conversation-001"
        
        for i, message_text in enumerate(messages):
            message = {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": message_text
                    }
                ],
                "messageId": f"helloworld-msg-{i+1:03d}",
                "contextId": contextId
            }
            
            request_data = jsonrpc_request_template.copy()
            request_data["id"] = f"req-{i+1:03d}"
            request_data["method"] = "message/send"
            request_data["params"] = {
                "message": message
            }
            
            response = requests.post(url, json=request_data, headers=headers)
            
            assert response.status_code == 200, \
                f"Erro na mensagem {i+1}: {response.status_code}"
            
            response_data = response.json()
            assert "result" in response_data, \
                f"Mensagem {i+1} deve ter resultado"
            
            print(f"✅ Mensagem {i+1}/4 enviada: '{message_text}'")
            
            # Pequena pausa entre mensagens
            time.sleep(0.1)
        
        print("✅ Conversação de múltiplas mensagens completada")
    
    def test_helloworld_error_scenarios(self, base_url: str, headers: Dict[str, str],
                                      jsonrpc_request_template: Dict[str, Any]):
        """Testa cenários de erro com HelloWorld."""
        url = f"{base_url}/message/send"
        
        # Teste 1: Mensagem vazia
        empty_message = {
            "role": "user",
            "parts": [],  # Sem parts
            "messageId": "empty-msg"
        }
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/send"
        request_data["params"] = {
            "message": empty_message
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            if "error" in response_data:
                print(f"✅ Erro detectado para mensagem vazia: {response_data['error']}")
            else:
                print("⚠️ Mensagem vazia foi aceita")
        
        # Teste 2: Mensagem com tipo inválido
        invalid_message = {
            "role": "invalid_role",
            "parts": [
                {
                    "kind": "text",
                    "text": "Test with invalid role"
                }
            ],
            "messageId": "invalid-role-msg"
        }
        
        request_data["params"]["message"] = invalid_message
        response = requests.post(url, json=request_data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            if "error" in response_data:
                print(f"✅ Erro detectado para role inválido: {response_data['error']}")
            else:
                print("⚠️ Role inválido foi aceito")
    
    def test_helloworld_performance(self, base_url: str, headers: Dict[str, str],
                                  helloworld_message: Dict[str, Any],
                                  jsonrpc_request_template: Dict[str, Any]):
        """Testa performance básica do HelloWorld."""
        url = f"{base_url}/message/send"
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/send"
        request_data["params"] = {
            "message": helloworld_message
        }
        
        # Mede tempo de resposta
        start_time = time.time()
        response = requests.post(url, json=request_data, headers=headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200, "Requisição deve ser bem-sucedida"
        assert response_time < 5.0, f"Resposta muito lenta: {response_time:.2f}s"
        
        print(f"✅ Tempo de resposta: {response_time:.3f}s")
        
        # Verifica tamanho da resposta
        response_size = len(response.content)
        print(f"✅ Tamanho da resposta: {response_size} bytes")
        
        # Performance básica: deve responder em menos de 1 segundo
        if response_time < 1.0:
            print("🚀 Performance excelente (< 1s)")
        elif response_time < 3.0:
            print("👍 Performance aceitável (< 3s)")
        else:
            print("⚠️ Performance lenta (> 3s)")
    
    @pytest.mark.slow
    def test_helloworld_stress(self, base_url: str, headers: Dict[str, str],
                             jsonrpc_request_template: Dict[str, Any]):
        """Teste de stress básico (marcado como slow)."""
        url = f"{base_url}/message/send"
        
        num_requests = 10
        successful_requests = 0
        total_time = 0
        
        print(f"🔄 Executando {num_requests} requisições sequenciais...")
        
        for i in range(num_requests):
            message = {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": f"Stress test message {i+1}"
                    }
                ],
                "messageId": f"stress-{i+1:03d}"
            }
            
            request_data = jsonrpc_request_template.copy()
            request_data["id"] = f"stress-{i+1:03d}"
            request_data["method"] = "message/send"
            request_data["params"] = {
                "message": message
            }
            
            start_time = time.time()
            
            try:
                response = requests.post(url, json=request_data, headers=headers, timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    successful_requests += 1
                    total_time += (end_time - start_time)
                
            except requests.RequestException as e:
                print(f"⚠️ Erro na requisição {i+1}: {e}")
            
            # Pequena pausa para não sobrecarregar
            time.sleep(0.1)
        
        success_rate = (successful_requests / num_requests) * 100
        avg_response_time = total_time / successful_requests if successful_requests > 0 else 0
        
        print(f"✅ Teste de stress completo:")
        print(f"   Taxa de sucesso: {success_rate:.1f}% ({successful_requests}/{num_requests})")
        print(f"   Tempo médio de resposta: {avg_response_time:.3f}s")
        
        # Critérios de sucesso
        assert success_rate >= 90, f"Taxa de sucesso muito baixa: {success_rate}%"
        assert avg_response_time < 2.0, f"Tempo médio muito alto: {avg_response_time:.3f}s"
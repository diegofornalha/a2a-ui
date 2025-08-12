"""
Testes para o endpoint /message/stream (Server-Sent Events).
"""
import pytest
import requests
import json
import time
from typing import Dict, Any, Generator

class TestMessageStream:
    """Testes para streaming de mensagens via SSE."""
    
    def test_message_stream_basic(self, base_url: str, headers: Dict[str, str],
                                sample_message: Dict[str, Any],
                                jsonrpc_request_template: Dict[str, Any]):
        """Testa streaming básico de mensagem."""
        url = f"{base_url}/message/stream"
        
        # Prepara requisição JSON-RPC para streaming
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/stream"
        request_data["params"] = {
            "message": sample_message
        }
        
        # Headers para SSE
        stream_headers = headers.copy()
        stream_headers["Accept"] = "text/event-stream"
        
        response = requests.post(url, json=request_data, headers=stream_headers, stream=True)
        
        # Verifica status HTTP
        assert response.status_code == 200, f"Status esperado: 200, recebido: {response.status_code}"
        
        # Verifica Content-Type para SSE
        content_type = response.headers.get('content-type', '')
        assert 'text/event-stream' in content_type, f"Content-Type deve ser text/event-stream, recebido: {content_type}"
        
        # Processa eventos SSE
        events_received = []
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    event_data = line[6:]  # Remove 'data: '
                    try:
                        event_json = json.loads(event_data)
                        events_received.append(event_json)
                        
                        # Verifica estrutura JSON-RPC do evento
                        assert "jsonrpc" in event_json, "Evento SSE deve incluir jsonrpc"
                        assert event_json["jsonrpc"] == "2.0", "Deve usar JSON-RPC 2.0"
                        
                        # Se é o evento final, para de processar
                        if ("result" in event_json and 
                            event_json["result"].get("final") == True):
                            break
                            
                    except json.JSONDecodeError:
                        print(f"⚠️ Evento SSE não é JSON válido: {event_data}")
                
                # Timeout de segurança
                if len(events_received) > 10:
                    break
                    
        except Exception as e:
            print(f"⚠️ Erro ao processar stream: {e}")
        
        assert len(events_received) > 0, "Deve receber pelo menos um evento SSE"
        print(f"✅ Streaming concluído: {len(events_received)} eventos recebidos")
        
        # Verifica último evento se for final
        last_event = events_received[-1]
        if ("result" in last_event and 
            last_event["result"].get("final") == True):
            print("✅ Evento final detectado corretamente")
    
    def test_message_stream_capabilities_check(self, base_url: str):
        """Verifica se o agente suporta streaming antes de testar."""
        # Primeiro verifica o AgentCard
        agent_card_url = f"{base_url}/.well-known/agent.json"
        response = requests.get(agent_card_url)
        
        if response.status_code != 200:
            pytest.skip("AgentCard não disponível para verificar capabilities")
        
        agent_card = response.json()
        capabilities = agent_card.get('capabilities', {})
        streaming_supported = capabilities.get('streaming', False)
        
        if not streaming_supported:
            pytest.skip("Agente não suporta streaming (capabilities.streaming: false)")
        
        print(f"✅ Streaming suportado pelo agente: {agent_card['name']}")
    
    def test_message_stream_timeout(self, base_url: str, headers: Dict[str, str],
                                  jsonrpc_request_template: Dict[str, Any]):
        """Testa comportamento com timeout no streaming."""
        url = f"{base_url}/message/stream"
        
        # Mensagem que pode demorar para processar
        long_message = {
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": "This is a test message that might take longer to process"
                }
            ],
            "messageId": "test-msg-long"
        }
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/stream"
        request_data["params"] = {
            "message": long_message
        }
        
        stream_headers = headers.copy()
        stream_headers["Accept"] = "text/event-stream"
        
        # Timeout curto para testar
        try:
            response = requests.post(url, json=request_data, headers=stream_headers, 
                                   stream=True, timeout=5)
            
            # Se chegou até aqui, o servidor respondeu rapidamente
            assert response.status_code == 200
            print("✅ Servidor respondeu dentro do timeout")
            
        except requests.Timeout:
            print("⚠️ Timeout no streaming (comportamento aceitável)")
        except requests.RequestException as e:
            pytest.fail(f"Erro inesperado na requisição: {e}")
    
    def test_stream_without_streaming_capability(self, base_url: str, headers: Dict[str, str],
                                               jsonrpc_request_template: Dict[str, Any]):
        """Testa streaming em agente que não suporta (deve retornar erro)."""
        # Este teste assume que vamos forçar uma requisição mesmo sem capability
        url = f"{base_url}/message/stream"
        
        request_data = jsonrpc_request_template.copy()
        request_data["method"] = "message/stream"
        request_data["params"] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "test"}],
                "messageId": "test-no-stream"
            }
        }
        
        response = requests.post(url, json=request_data, headers=headers)
        
        # Se o agente não suporta streaming, deve retornar erro
        if response.status_code == 200:
            response_data = response.json()
            if "error" in response_data:
                error = response_data["error"]
                # Pode ser method not found ou unsupported operation
                assert error["code"] in [-32601, -32004], \
                    "Deve retornar erro appropriado para streaming não suportado"
                print(f"✅ Erro apropriado para streaming não suportado: {error}")
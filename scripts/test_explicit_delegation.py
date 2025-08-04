#!/usr/bin/env python3
"""
Script para testar delegação explícita ao Orchestrator Agent
"""

import asyncio
import httpx
import json
import uuid

UI_SERVER_URL = "http://localhost:12000"

async def test_explicit_delegation():
    """Testar delegação explícita ao Orchestrator Agent"""
    
    async with httpx.AsyncClient() as client:
        # Criar conversa
        conversation_payload = {
            "jsonrpc": "2.0",
            "method": "conversation/create",
            "id": "create_conv"
        }
        
        conv_response = await client.post(
            f"{UI_SERVER_URL}/conversation/create",
            json=conversation_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if conv_response.status_code != 200:
            print(f"❌ Erro ao criar conversa: {conv_response.status_code}")
            return
            
        conversation_id = conv_response.json()["result"]["conversation_id"]
        print(f"✅ Conversa criada: {conversation_id}")
        
        # Lista de mensagens para testar
        test_messages = [
            "Por favor, delegue para o Orchestrator Agent: O que é MCP?",
            "Use o Orchestrator Agent para explicar Model Context Protocol",
            "Delega essa pergunta sobre MCP para o Orchestrator Agent: Quais ferramentas MCP estão disponíveis?",
            "Conecte-me com o Orchestrator Agent para discutir ferramentas MCP"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🔍 Teste {i}/{len(test_messages)}")
            print(f"📤 Enviando: {message}")
            
            message_payload = {
                "messageId": str(uuid.uuid4()),
                "contextId": conversation_id,
                "role": "user",
                "parts": [{"kind": "text", "text": message}]
            }
            
            send_payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": message_payload,
                "id": f"send_msg_{i}"
            }
            
            response = await client.post(
                f"{UI_SERVER_URL}/message/send",
                json=send_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ Mensagem {i} enviada!")
                
                # Aguardar resposta
                await asyncio.sleep(3)
                
                # Buscar mensagens
                list_payload = {
                    "jsonrpc": "2.0",
                    "method": "message/list", 
                    "params": conversation_id,
                    "id": f"list_messages_{i}"
                }
                
                messages_response = await client.post(
                    f"{UI_SERVER_URL}/message/list",
                    json=list_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if messages_response.status_code == 200:
                    messages = messages_response.json().get("result", [])
                    
                    # Pegar a última resposta do agente
                    agent_messages = [m for m in messages if m.get("role") == "agent"]
                    if agent_messages:
                        last_response = agent_messages[-1]
                        parts = last_response.get("parts", [])
                        
                        if parts:
                            if isinstance(parts[0], dict) and "root" in parts[0]:
                                content = parts[0]["root"].get("text", str(parts[0]))
                            else:
                                content = str(parts[0])
                            
                            print(f"🤖 Resposta {i}: {content[:300]}...")
                            
                            # Verificar se mencionou delegação ou conhecimento MCP
                            if "delega" in content.lower() or "orchestrator" in content.lower():
                                print("✅ Delegação mencionada!")
                            if "mcp" in content.lower() and len(content) > 100:
                                print("✅ Resposta detalhada sobre MCP!")
                    
                    print("-" * 50)
            else:
                print(f"❌ Erro ao enviar mensagem {i}: {response.status_code}")
            
            # Pausa entre mensagens
            await asyncio.sleep(2)
        
        return conversation_id

async def test_list_agents_first():
    """Primeiro listar agentes, depois solicitar delegação"""
    
    async with httpx.AsyncClient() as client:
        # Criar conversa
        conversation_payload = {
            "jsonrpc": "2.0",
            "method": "conversation/create",
            "id": "create_conv_2"
        }
        
        conv_response = await client.post(
            f"{UI_SERVER_URL}/conversation/create",
            json=conversation_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if conv_response.status_code != 200:
            print(f"❌ Erro ao criar segunda conversa: {conv_response.status_code}")
            return
            
        conversation_id = conv_response.json()["result"]["conversation_id"]
        print(f"✅ Segunda conversa criada: {conversation_id}")
        
        # Primeiro: listar agentes
        list_message = "Liste todos os agentes disponíveis"
        
        message_payload = {
            "messageId": str(uuid.uuid4()),
            "contextId": conversation_id,
            "role": "user",
            "parts": [{"kind": "text", "text": list_message}]
        }
        
        send_payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": message_payload,
            "id": "list_agents_msg"
        }
        
        print(f"📤 Pedindo lista de agentes...")
        
        response = await client.post(
            f"{UI_SERVER_URL}/message/send",
            json=send_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Solicitação de lista enviada!")
            await asyncio.sleep(3)
            
            # Agora: solicitar MCP para Orchestrator Agent
            mcp_message = "Agora envie uma mensagem para o Orchestrator Agent perguntando sobre MCP (Model Context Protocol)"
            
            message_payload_2 = {
                "messageId": str(uuid.uuid4()),
                "contextId": conversation_id,
                "role": "user",
                "parts": [{"kind": "text", "text": mcp_message}]
            }
            
            send_payload_2 = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": message_payload_2,
                "id": "mcp_question_msg"
            }
            
            print(f"📤 Solicitando delegação para MCP...")
            
            response2 = await client.post(
                f"{UI_SERVER_URL}/message/send",
                json=send_payload_2,
                headers={"Content-Type": "application/json"}
            )
            
            if response2.status_code == 200:
                print(f"✅ Solicitação MCP enviada!")
                await asyncio.sleep(5)  # Mais tempo para processar
                
                # Buscar todas as mensagens
                list_payload = {
                    "jsonrpc": "2.0",
                    "method": "message/list", 
                    "params": conversation_id,
                    "id": "final_list_messages"
                }
                
                messages_response = await client.post(
                    f"{UI_SERVER_URL}/message/list",
                    json=list_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if messages_response.status_code == 200:
                    messages = messages_response.json().get("result", [])
                    print(f"\n📋 Conversa completa ({len(messages)} mensagens):")
                    
                    for i, msg in enumerate(messages):
                        role = msg.get("role", "unknown")
                        parts = msg.get("parts", [])
                        
                        if parts:
                            if isinstance(parts[0], dict) and "root" in parts[0]:
                                content = parts[0]["root"].get("text", str(parts[0]))
                            else:
                                content = str(parts[0])
                        else:
                            content = "No content"
                        
                        print(f"\n{i+1}. {role.upper()}: {content[:200]}...")
        
        return conversation_id

async def main():
    """Função principal"""
    print("🎯 Teste de Delegação Explícita ao Orchestrator Agent")
    print("=" * 60)
    
    print("\n1️⃣ Testando solicitações explícitas de delegação...")
    conv1 = await test_explicit_delegation()
    
    print("\n" + "=" * 60)
    print("2️⃣ Testando listar agentes primeiro e depois delegar...")
    conv2 = await test_list_agents_first()
    
    print(f"\n🎉 Testes de delegação concluídos!")
    if conv1:
        print(f"🌐 Conversa 1: http://localhost:12000/conversation?conversation_id={conv1}")
    if conv2:
        print(f"🌐 Conversa 2: http://localhost:12000/conversation?conversation_id={conv2}")

if __name__ == "__main__":
    asyncio.run(main()) 
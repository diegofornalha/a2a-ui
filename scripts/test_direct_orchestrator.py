#!/usr/bin/env python3
"""
Script para testar o Orchestrator Agent com mensagens específicas direcionadas
"""

import asyncio
import httpx
import json
import uuid

UI_SERVER_URL = "http://localhost:12000"

async def test_directed_message():
    """Testar mensagem direcionada ao Orchestrator Agent"""
    
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
        
        # Enviar mensagem direcionada ao Orchestrator Agent
        directed_message = "Orchestrator Agent, o que é MCP (Model Context Protocol)?"
        
        message_payload = {
            "messageId": str(uuid.uuid4()),
            "contextId": conversation_id,
            "role": "user",
            "parts": [{"kind": "text", "text": directed_message}]
        }
        
        send_payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": message_payload,
            "id": "send_msg"
        }
        
        print(f"📤 Enviando: {directed_message}")
        
        response = await client.post(
            f"{UI_SERVER_URL}/message/send",
            json=send_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Mensagem enviada com sucesso!")
            
            # Aguardar resposta
            print("⏳ Aguardando resposta...")
            await asyncio.sleep(5)
            
            # Buscar mensagens
            list_payload = {
                "jsonrpc": "2.0",
                "method": "message/list", 
                "params": conversation_id,
                "id": "list_messages"
            }
            
            messages_response = await client.post(
                f"{UI_SERVER_URL}/message/list",
                json=list_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if messages_response.status_code == 200:
                messages = messages_response.json().get("result", [])
                print(f"\n💬 Mensagens ({len(messages)}):")
                
                for msg in messages:
                    role = msg.get("role", "unknown")
                    parts = msg.get("parts", [])
                    
                    if parts:
                        if isinstance(parts[0], dict) and "root" in parts[0]:
                            content = parts[0]["root"].get("text", str(parts[0]))
                        else:
                            content = str(parts[0])
                    else:
                        content = "No content"
                    
                    print(f"\n{role.upper()}:")
                    print(f"{content[:500]}...")
            
            return conversation_id
        else:
            print(f"❌ Erro ao enviar: {response.status_code}")
            print(response.text)
            return None

async def test_alternative_message():
    """Testar mensagem alternativa mencionando especificamente MCP"""
    
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
            print(f"❌ Erro ao criar conversa: {conv_response.status_code}")
            return
            
        conversation_id = conv_response.json()["result"]["conversation_id"]
        print(f"✅ Segunda conversa criada: {conversation_id}")
        
        # Mensagem específica sobre agentes MCP
        specific_message = "Preciso falar com um agente que entenda de MCP e ferramentas de protocolo. Quais são as ferramentas MCP disponíveis?"
        
        message_payload = {
            "messageId": str(uuid.uuid4()),
            "contextId": conversation_id,
            "role": "user",
            "parts": [{"kind": "text", "text": specific_message}]
        }
        
        send_payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": message_payload,
            "id": "send_msg_2"
        }
        
        print(f"📤 Enviando: {specific_message}")
        
        response = await client.post(
            f"{UI_SERVER_URL}/message/send",
            json=send_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Segunda mensagem enviada!")
            
            # Aguardar e verificar resposta
            print("⏳ Aguardando resposta...")
            await asyncio.sleep(5)
            
            # Buscar mensagens
            list_payload = {
                "jsonrpc": "2.0",
                "method": "message/list", 
                "params": conversation_id,
                "id": "list_messages_2"
            }
            
            messages_response = await client.post(
                f"{UI_SERVER_URL}/message/list",
                json=list_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if messages_response.status_code == 200:
                messages = messages_response.json().get("result", [])
                print(f"\n💬 Segunda conversa - Mensagens ({len(messages)}):")
                
                for msg in messages:
                    role = msg.get("role", "unknown")
                    parts = msg.get("parts", [])
                    
                    if parts:
                        if isinstance(parts[0], dict) and "root" in parts[0]:
                            content = parts[0]["root"].get("text", str(parts[0]))
                        else:
                            content = str(parts[0])
                    else:
                        content = "No content"
                    
                    print(f"\n{role.upper()}:")
                    print(f"{content[:500]}...")
            
            return conversation_id
        else:
            print(f"❌ Erro ao enviar segunda mensagem: {response.status_code}")
            return None

async def main():
    """Função principal"""
    print("🎯 Teste Direcionado do Orchestrator Agent")
    print("=" * 50)
    
    print("\n1️⃣ Teste com direcionamento específico...")
    conv1 = await test_directed_message()
    
    print("\n" + "=" * 50)
    print("2️⃣ Teste com menção a MCP...")
    conv2 = await test_alternative_message()
    
    print(f"\n🎉 Testes concluídos!")
    if conv1:
        print(f"🌐 Conversa 1: http://localhost:12000/conversation?conversation_id={conv1}")
    if conv2:
        print(f"🌐 Conversa 2: http://localhost:12000/conversation?conversation_id={conv2}")

if __name__ == "__main__":
    asyncio.run(main()) 
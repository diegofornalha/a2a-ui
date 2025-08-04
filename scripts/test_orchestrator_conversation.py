#!/usr/bin/env python3
"""
Script para testar o Orchestrator Agent através de conversas automatizadas na UI
"""

import asyncio
import httpx
import json
import uuid
from typing import Dict, Any

# Configurações
UI_SERVER_URL = "http://localhost:12000"

async def create_conversation():
    """Criar uma nova conversa"""
    async with httpx.AsyncClient() as client:
        payload = {
            "jsonrpc": "2.0",
            "method": "conversation/create",
            "id": "create_conv"
        }
        
        response = await client.post(
            f"{UI_SERVER_URL}/conversation/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            conversation_id = result["result"]["conversation_id"]
            print(f"✅ Conversa criada: {conversation_id}")
            return conversation_id
        else:
            print(f"❌ Erro ao criar conversa: {response.status_code}")
            return None

async def send_message(conversation_id: str, message_text: str):
    """Enviar mensagem para a conversa"""
    async with httpx.AsyncClient() as client:
        message_payload = {
            "messageId": str(uuid.uuid4()),
            "contextId": conversation_id,
            "role": "user",
            "parts": [{"kind": "text", "text": message_text}]
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": message_payload,
            "id": "send_msg"
        }
        
        print(f"📤 Enviando: {message_text}")
        
        response = await client.post(
            f"{UI_SERVER_URL}/message/send",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Mensagem enviada")
            return result
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None

async def get_conversation_messages(conversation_id: str):
    """Obter mensagens da conversa"""
    async with httpx.AsyncClient() as client:
        payload = {
            "jsonrpc": "2.0",
            "method": "message/list",
            "params": conversation_id,
            "id": "list_messages"
        }
        
        response = await client.post(
            f"{UI_SERVER_URL}/message/list",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            messages = result.get("result", [])
            
            print(f"\n💬 Mensagens da conversa ({len(messages)}):")
            for msg in messages:
                role = msg.get("role", "unknown")
                parts = msg.get("parts", [])
                if parts and hasattr(parts[0], 'root') and hasattr(parts[0].root, 'text'):
                    content = parts[0].root.text
                elif parts and isinstance(parts[0], dict) and "text" in parts[0]:
                    content = parts[0]["text"]
                else:
                    content = str(parts)
                
                print(f"  {role}: {content[:100]}...")
            
            return messages
        else:
            print(f"❌ Erro ao obter mensagens: {response.status_code}")
            return []

async def test_orchestrator_capabilities():
    """Testar as capacidades do Orchestrator Agent"""
    
    print("🤖 Testando Orchestrator Agent na UI")
    print("=" * 50)
    
    # Criar conversa
    conversation_id = await create_conversation()
    if not conversation_id:
        return
    
    # Lista de perguntas para testar
    test_questions = [
        "O que é MCP (Model Context Protocol)?",
        "Quais ferramentas MCP estão disponíveis no sistema?",
        "Liste as tarefas que você é capaz de executar",
        "Como você coordena outros agentes usando MCP?",
        "Qual é o status atual do servidor MCP?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Teste {i}/{len(test_questions)}")
        print("-" * 30)
        
        # Enviar pergunta
        result = await send_message(conversation_id, question)
        if not result:
            continue
            
        # Aguardar processamento
        print("⏳ Aguardando resposta...")
        await asyncio.sleep(3)
        
        # Obter mensagens
        messages = await get_conversation_messages(conversation_id)
        
        # Aguardar mais um pouco se necessário
        await asyncio.sleep(2)
    
    print(f"\n🎉 Teste concluído!")
    print(f"🌐 Veja a conversa completa em: http://localhost:12000/conversation?conversation_id={conversation_id}")

async def check_agent_status():
    """Verificar status dos agentes"""
    async with httpx.AsyncClient() as client:
        try:
            # Listar agentes
            payload = {
                "jsonrpc": "2.0",
                "method": "agent/list",
                "id": "list_agents"
            }
            
            response = await client.post(
                f"{UI_SERVER_URL}/agent/list",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                agents = result.get("result", [])
                
                print(f"\n📋 Agentes disponíveis ({len(agents)}):")
                
                orchestrator_found = False
                for agent in agents:
                    name = agent.get("name", "Unknown")
                    url = agent.get("url", "Unknown")
                    skills = len(agent.get("skills", []))
                    
                    print(f"  • {name} - {url} ({skills} skills)")
                    
                    if name == "Orchestrator Agent":
                        orchestrator_found = True
                
                if orchestrator_found:
                    print("✅ Orchestrator Agent encontrado!")
                    return True
                else:
                    print("❌ Orchestrator Agent não encontrado!")
                    return False
            else:
                print(f"❌ Erro ao listar agentes: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False

async def main():
    """Função principal"""
    print("🚀 Script de Teste do Orchestrator Agent")
    print("=" * 50)
    
    # Verificar status dos agentes
    print("1️⃣ Verificando agentes disponíveis...")
    agent_ok = await check_agent_status()
    
    if not agent_ok:
        print("\n💡 Dica: Execute o script de adição do agente primeiro:")
        print("   uv run python scripts/add_orchestrator_agent.py")
        return
    
    # Testar capacidades
    print("\n2️⃣ Iniciando teste de capacidades...")
    await test_orchestrator_capabilities()
    
    print("\n🎯 Próximos passos:")
    print("• Acesse http://localhost:12000 para ver a UI")
    print("• Vá para http://localhost:12000/agents para ver os agentes")
    print("• Faça suas próprias perguntas sobre MCP!")

if __name__ == "__main__":
    asyncio.run(main()) 
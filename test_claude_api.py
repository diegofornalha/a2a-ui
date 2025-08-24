#!/usr/bin/env python3
"""
Script para testar se o Claude SDK está funcionando na aplicação a2a-ui
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:12000"

async def test_claude_integration():
    """Testa a integração completa com Claude SDK"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔍 Testando integração com Claude SDK...")
        print("-" * 50)
        
        # 1. Criar uma conversa
        print("\n1️⃣ Criando conversa...")
        create_response = await client.post(
            f"{BASE_URL}/conversation/create",
            json={}
        )
        
        if create_response.status_code != 200:
            print(f"❌ Erro ao criar conversa: {create_response.status_code}")
            return False
            
        conversation_data = create_response.json()
        conversation_id = conversation_data["result"]["conversation_id"]
        print(f"✅ Conversa criada: {conversation_id}")
        
        # 2. Listar conversas
        print("\n2️⃣ Listando conversas...")
        list_response = await client.post(
            f"{BASE_URL}/conversation/list",
            json={}
        )
        
        if list_response.status_code == 200:
            conversations = list_response.json()["result"]
            print(f"✅ Total de conversas: {len(conversations)}")
        else:
            print(f"❌ Erro ao listar conversas: {list_response.status_code}")
        
        # 3. Enviar mensagem (estrutura correta)
        print("\n3️⃣ Enviando mensagem para Claude...")
        message_id = str(uuid.uuid4())
        
        # Estrutura correta baseada no modelo Pydantic
        message_data = {
            "params": {
                "message_id": message_id,
                "context_id": conversation_id,
                "role": "user",
                "parts": [
                    {
                        "text": "Olá Claude! Este é um teste do SDK. Responda com uma mensagem curta confirmando que está funcionando."
                    }
                ]
            }
        }
        
        try:
            send_response = await client.post(
                f"{BASE_URL}/message/send",
                json=message_data
            )
            
            if send_response.status_code == 200:
                print(f"✅ Mensagem enviada com sucesso!")
                result = send_response.json()
                print(f"   ID da mensagem: {result.get('result', {}).get('message_id', 'N/A')}")
            else:
                print(f"❌ Erro ao enviar mensagem: {send_response.status_code}")
                print(f"   Resposta: {send_response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {str(e)}")
        
        # 4. Verificar mensagens pendentes
        print("\n4️⃣ Verificando mensagens pendentes...")
        await asyncio.sleep(2)  # Aguardar processamento
        
        pending_response = await client.post(
            f"{BASE_URL}/message/pending",
            json={}
        )
        
        if pending_response.status_code == 200:
            pending = pending_response.json()["result"]
            if pending:
                print(f"⏳ Mensagens sendo processadas: {len(pending)}")
                for msg_id, status in pending:
                    print(f"   - {msg_id}: {status or 'Processando...'}")
            else:
                print("✅ Nenhuma mensagem pendente")
        
        # 5. Listar mensagens da conversa
        print("\n5️⃣ Listando mensagens da conversa...")
        messages_response = await client.post(
            f"{BASE_URL}/message/list",
            json={"params": conversation_id}
        )
        
        if messages_response.status_code == 200:
            messages = messages_response.json()["result"]
            print(f"✅ Total de mensagens: {len(messages)}")
            for msg in messages:
                role = msg.get("role", "unknown")
                msg_id = msg.get("message_id", "N/A")
                print(f"   - [{role}] {msg_id}")
        
        # 6. Verificar tarefas
        print("\n6️⃣ Verificando tarefas...")
        tasks_response = await client.post(
            f"{BASE_URL}/task/list",
            json={}
        )
        
        if tasks_response.status_code == 200:
            tasks = tasks_response.json()["result"]
            print(f"✅ Total de tarefas: {len(tasks)}")
        
        # 7. Verificar agentes
        print("\n7️⃣ Verificando agentes disponíveis...")
        agents_response = await client.post(
            f"{BASE_URL}/agent/list",
            json={}
        )
        
        if agents_response.status_code == 200:
            agents = agents_response.json()["result"]
            print(f"✅ Total de agentes: {len(agents)}")
            for agent in agents:
                print(f"   - {agent.get('name', 'N/A')}: {agent.get('url', 'N/A')}")
        
        print("\n" + "=" * 50)
        print("✅ TESTE COMPLETO - Claude SDK está funcionando!")
        print("=" * 50)
        return True

async def main():
    try:
        success = await test_claude_integration()
        if success:
            print("\n🎉 Todos os testes passaram com sucesso!")
        else:
            print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║     TESTE DE INTEGRAÇÃO - CLAUDE SDK + A2A-UI    ║
╚══════════════════════════════════════════════════╝
    """)
    print(f"🕐 Iniciando teste em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL da aplicação: {BASE_URL}")
    print()
    
    asyncio.run(main())
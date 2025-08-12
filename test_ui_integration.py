#!/usr/bin/env python3
"""
Teste de integração da UI com Claude
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime

async def test_ui_message_flow():
    """Simula o fluxo de mensagem da UI"""
    
    print("🧪 Testando fluxo de mensagem UI -> Backend -> Claude")
    print("=" * 60)
    
    # 1. Criar conversação primeiro
    print("\n1️⃣ Criando conversação...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8085/conversation/create",
            json={}
        )
        conversation_data = response.json()
        conversation_id = conversation_data["result"]["conversation_id"]
        print(f"✅ Conversação criada: {conversation_id}")
    
    # 2. Enviar mensagem como a UI faria
    print("\n2️⃣ Enviando mensagem via /message/send...")
    message_id = str(uuid.uuid4())
    
    message_payload = {
        "params": {
            "messageId": message_id,
            "contextId": conversation_id,
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": "Olá Claude! Você está funcionando através da UI? Responda SIM ou NÃO."
                }
            ]
        }
    }
    
    print(f"📤 Payload: {json.dumps(message_payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:8085/message/send",
            json=message_payload
        )
        print(f"📥 Response status: {response.status_code}")
        send_result = response.json()
        print(f"📋 Send result: {json.dumps(send_result, indent=2)}")
    
    # 3. Aguardar processamento
    print("\n⏳ Aguardando processamento do Claude (15 segundos)...")
    await asyncio.sleep(15)
    
    # 4. Listar mensagens da conversação
    print("\n3️⃣ Listando mensagens da conversação...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8085/message/list",
            json={"params": conversation_id}
        )
        messages = response.json()
        print(f"📬 Total de mensagens: {len(messages.get('result', []))}")
        
        for msg in messages.get("result", []):
            role = msg.get("role", "unknown")
            parts = msg.get("parts", [])
            content = ""
            for part in parts:
                if isinstance(part, dict) and part.get("type") == "text":
                    content = part.get("text", "")[:100]
            print(f"\n  {role.upper()}: {content}")
    
    # 5. Verificar eventos
    print("\n4️⃣ Verificando eventos...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8085/events/get",
            json={}
        )
        events = response.json()
        print(f"📊 Total de eventos: {len(events.get('result', []))}")
        
        # Filtrar eventos desta conversação
        conv_events = [e for e in events.get("result", []) 
                      if e.get("contextId") == conversation_id]
        print(f"📊 Eventos desta conversação: {len(conv_events)}")
        
        for event in conv_events:
            actor = event.get("actor", "unknown")
            role = event.get("role", "unknown")
            content = event.get("content", [])
            text = ""
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")[:100]
            print(f"\n  {actor}/{role}: {text}")
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
    
    # Verificar se Claude respondeu
    claude_responded = any(
        msg.get("role") == "assistant" 
        for msg in messages.get("result", [])
    )
    
    if claude_responded:
        print("🎉 SUCESSO: Claude respondeu através da UI!")
    else:
        print("❌ PROBLEMA: Claude não respondeu. Verificar logs do backend.")
    
    return claude_responded

async def main():
    """Função principal"""
    success = await test_ui_message_flow()
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
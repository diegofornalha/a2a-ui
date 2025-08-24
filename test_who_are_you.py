#!/usr/bin/env python3
"""
Script para testar "Quem é você?" via API remota
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:12000"

async def test_who_are_you():
    """Testa perguntando quem é o agente"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🤖 Testando 'Quem é você?' com Claude SDK...")
        print("-" * 50)
        
        # 1. Criar uma nova conversa
        print("\n1️⃣ Criando nova conversa...")
        create_response = await client.post(
            f"{BASE_URL}/conversation/create",
            json={}
        )
        
        if create_response.status_code != 200:
            print(f"❌ Erro ao criar conversa: {create_response.status_code}")
            return
            
        conversation_data = create_response.json()
        conversation_id = conversation_data["result"]["conversation_id"]
        print(f"✅ Conversa criada: {conversation_id}")
        
        # 2. Enviar mensagem perguntando quem é
        print("\n2️⃣ Enviando pergunta: 'Quem é você?'...")
        message_id = str(uuid.uuid4())
        
        message_data = {
            "params": {
                "message_id": message_id,
                "context_id": conversation_id,
                "role": "user",
                "parts": [
                    {
                        "text": "Quem é você? Me diga seu nome, qual modelo você usa, sua versão e quais são suas principais capacidades."
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
                print(f"   ID da mensagem: {result.get('result', {}).get('message_id', message_id)}")
            else:
                print(f"❌ Erro ao enviar mensagem: {send_response.status_code}")
                print(f"   Resposta: {send_response.text}")
                return
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {str(e)}")
            return
        
        # 3. Aguardar processamento
        print("\n3️⃣ Aguardando resposta do Claude...")
        await asyncio.sleep(5)  # Aguardar mais tempo para processar
        
        # 4. Verificar mensagens pendentes
        print("\n4️⃣ Verificando status do processamento...")
        pending_response = await client.post(
            f"{BASE_URL}/message/pending",
            json={}
        )
        
        if pending_response.status_code == 200:
            pending = pending_response.json()["result"]
            if pending:
                print(f"⏳ Mensagens sendo processadas: {len(pending)}")
                for msg_id, status in pending:
                    if msg_id == message_id:
                        print(f"   - Sua mensagem: {status or 'Processando...'}")
            else:
                print("✅ Processamento concluído")
        
        # 5. Buscar mensagens da conversa
        print("\n5️⃣ Buscando resposta...")
        messages_response = await client.post(
            f"{BASE_URL}/message/list",
            json={"params": conversation_id}
        )
        
        if messages_response.status_code == 200:
            messages = messages_response.json()["result"]
            print(f"📨 Total de mensagens na conversa: {len(messages)}")
            
            print("\n" + "=" * 50)
            print("💬 CONVERSA:")
            print("=" * 50)
            
            for msg in messages:
                role = msg.get("role", "unknown")
                msg_id = msg.get("message_id", "N/A")
                parts = msg.get("parts", [])
                
                print(f"\n[{role.upper()}] (ID: {msg_id[:8]}...)")
                
                # Extrair texto das partes
                for part in parts:
                    if isinstance(part, dict):
                        # Verifica diferentes estruturas possíveis
                        if "text" in part:
                            print(f"   {part['text']}")
                        elif "root" in part and isinstance(part["root"], dict):
                            if "text" in part["root"]:
                                print(f"   {part['root']['text']}")
                            elif "data" in part["root"]:
                                print(f"   [Dados]: {json.dumps(part['root']['data'], indent=2)}")
                        else:
                            print(f"   [Conteúdo]: {json.dumps(part, indent=2)}")
                
                print("-" * 30)
        
        print("\n" + "=" * 50)
        print("✅ TESTE CONCLUÍDO")
        print("=" * 50)
        return True

async def main():
    try:
        success = await test_who_are_you()
        if success:
            print("\n🎉 Teste executado com sucesso!")
        else:
            print("\n⚠️ Teste falhou. Verifique os logs acima.")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║       TESTE: "QUEM É VOCÊ?" - CLAUDE SDK         ║
╚══════════════════════════════════════════════════╝
    """)
    print(f"🕐 Iniciando teste em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL da aplicação: {BASE_URL}")
    print()
    
    asyncio.run(main())
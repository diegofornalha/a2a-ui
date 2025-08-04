#!/usr/bin/env python3
"""
Script para adicionar o agente HelloWorld manualmente
"""

import asyncio
import httpx
import json


async def add_helloworld_agent():
    """Adiciona o agente HelloWorld ao sistema"""
    
    # URL do servidor UI
    server_url = "http://localhost:11000"
    
    # Informações do agente HelloWorld
    agent_info = {
        "url": "http://localhost:9998",
        "name": "HelloWorld Agent",
        "description": "Agente de teste Hello World",
        "enabled": True
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Registrar o agente
            response = await client.post(
                f"{server_url}/agent/register",
                json={
                    "jsonrpc": "2.0",
                    "method": "register",
                    "params": agent_info,
                    "id": "1"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Agente HelloWorld registrado com sucesso!")
                print(f"📍 URL: {agent_info['url']}")
                print(f"🤖 Nome: {agent_info['name']}")
                print(f"📝 Resposta: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Erro ao registrar agente: {response.status_code}")
                print(f"📝 Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    print("🚀 Adicionando agente HelloWorld...")
    asyncio.run(add_helloworld_agent())
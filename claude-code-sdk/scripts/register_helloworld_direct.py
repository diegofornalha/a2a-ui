#!/usr/bin/env python3
"""
Script para registrar o agente HelloWorld diretamente no servidor
"""

import asyncio
import httpx
import json


async def register_helloworld():
    """Registra o agente HelloWorld através do endpoint correto"""
    
    server_url = "http://localhost:12000"  # Servidor backend, não a UI
    
    # Criar o agent card para o HelloWorld
    agent_card = {
        "name": "HelloWorld Agent",
        "description": "Simple Hello World agent for testing",
        "url": "http://localhost:9998",
        "version": "1.0.0",
        "provider": {
            "organization": "Test Organization"
        },
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "capabilities": {
            "streaming": False,
            "pushNotifications": False
        },
        "skills": [
            {
                "name": "greeting",
                "description": "Responds with Hello World",
                "inputSchema": {},
                "outputSchema": {}
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Primeiro, tentar obter informações do agente
            print("📡 Verificando se o agente está acessível...")
            try:
                health_response = await client.get("http://localhost:9998/health")
                if health_response.status_code == 200:
                    print("✅ Agente HelloWorld está online!")
                else:
                    print("⚠️ Agente pode não estar totalmente funcional")
            except:
                print("❌ Não foi possível conectar ao agente HelloWorld na porta 9998")
                return
            
            # Registrar o agente
            print("\n🚀 Registrando agente no servidor...")
            response = await client.post(
                f"{server_url}/agent/register",
                json={
                    "jsonrpc": "2.0",
                    "method": "register",
                    "params": {
                        "path": "http://localhost:9998",
                        "agent_card": agent_card
                    },
                    "id": "register-helloworld"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Agente registrado com sucesso!")
                print(f"📝 Resposta: {json.dumps(result, indent=2)}")
                
                # Verificar se está na lista
                print("\n🔍 Verificando se o agente aparece na lista...")
                list_response = await client.post(
                    f"{server_url}/agent/list",
                    json={
                        "jsonrpc": "2.0",
                        "method": "list",
                        "params": {},
                        "id": "list-agents"
                    }
                )
                
                if list_response.status_code == 200:
                    agents = list_response.json().get('result', [])
                    helloworld_found = any(
                        'localhost:9998' in agent.get('agent_card', {}).get('url', '') 
                        for agent in agents
                    )
                    
                    if helloworld_found:
                        print("✅ HelloWorld Agent agora aparece na lista de agentes descobertos!")
                        print("🎉 Acesse http://localhost:11000/agents para ver o agente")
                    else:
                        print("⚠️ Agente registrado mas ainda não aparece na lista")
                        
            else:
                print(f"❌ Erro ao registrar: {response.status_code}")
                print(f"📝 Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🤖 Registrando HelloWorld Agent (localhost:9998)...")
    asyncio.run(register_helloworld())
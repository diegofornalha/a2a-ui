#!/usr/bin/env python3
"""
Script para verificar agentes registrados
"""

import asyncio
import httpx
import json


async def list_agents():
    """Lista todos os agentes registrados"""
    
    server_url = "http://localhost:11000"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Listar agentes
            response = await client.post(
                f"{server_url}/agent/list",
                json={
                    "jsonrpc": "2.0",
                    "method": "list",
                    "params": {},
                    "id": "1"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                agents = result.get('result', [])
                
                print(f"\n📡 Total de agentes registrados: {len(agents)}")
                print("=" * 60)
                
                for i, agent in enumerate(agents, 1):
                    agent_card = agent.get('agent_card', {})
                    print(f"\n🤖 Agente {i}:")
                    print(f"   Nome: {agent_card.get('name', 'Unknown')}")
                    print(f"   URL: {agent_card.get('url', 'Unknown')}")
                    print(f"   Descrição: {agent_card.get('description', 'N/A')}")
                    print(f"   Status: {'🟢 Online' if agent.get('is_online') else '🔴 Offline'}")
                    print(f"   Habilitado: {'✅' if agent.get('enabled') else '❌'}")
                    
                print("\n" + "=" * 60)
                
                # Verificar especificamente o HelloWorld
                helloworld_found = any(
                    'localhost:9998' in agent.get('agent_card', {}).get('url', '') 
                    for agent in agents
                )
                
                if helloworld_found:
                    print("✅ HelloWorld Agent (localhost:9998) está registrado!")
                else:
                    print("⚠️ HelloWorld Agent (localhost:9998) NÃO está registrado")
                    print("💡 Use o script add_helloworld_agent.py para adicionar")
                    
            else:
                print(f"❌ Erro ao listar agentes: {response.status_code}")
                print(f"📝 Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    print("🔍 Verificando agentes registrados...")
    asyncio.run(list_agents())
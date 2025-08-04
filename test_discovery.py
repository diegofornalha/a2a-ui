#!/usr/bin/env python3
"""
Teste direto do sistema de descoberta de agentes
"""

import asyncio
import httpx
from service.server.agent_discovery import AgentDiscovery

async def test_discovery():
    """Testa a descoberta de agentes diretamente"""
    print("🔍 Iniciando teste de descoberta...")
    
    async with httpx.AsyncClient() as client:
        discovery = AgentDiscovery(client, timeout=5.0)
        
        print("📡 Testando conexão direta com localhost:9999...")
        try:
            response = await client.get("http://localhost:9999/.well-known/agent.json", timeout=5.0)
            print(f"✅ Resposta localhost:9999: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"📝 Nome do agente: {data.get('name')}")
        except Exception as e:
            print(f"❌ Erro ao conectar localhost:9999: {e}")
        
        print("\n🔎 Executando descoberta completa...")
        agents = await discovery.discover_localhost_agents()
        
        print(f"🎯 Descobertos {len(agents)} agentes:")
        for agent in agents:
            print(f"  - {agent.name} ({agent.url})")
        
        return agents

if __name__ == "__main__":
    agents = asyncio.run(test_discovery())
    print(f"\n✅ Teste concluído! {len(agents)} agentes encontrados.")
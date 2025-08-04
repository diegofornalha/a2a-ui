#!/usr/bin/env python3
"""
Script para forçar descoberta de agentes no sistema UI
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from service.server.in_memory_manager import InMemoryFakeAgentManager
from service.server.agent_discovery import AgentDiscovery, auto_discover_and_register
import httpx

async def force_discovery():
    """Força descoberta e registro de agentes"""
    
    try:
        # Criar cliente HTTP
        async with httpx.AsyncClient() as client:
            # Criar discovery service
            discovery = AgentDiscovery(client, timeout=5.0)
            
            print("🔍 Descobrindo agentes localhost...")
            agents = await discovery.discover_localhost_agents()
            
            print(f"📊 {len(agents)} agentes descobertos:")
            for agent in agents:
                print(f"  - {agent.name} ({agent.url})")
                print(f"    📝 {agent.description}")
                
            # Verificar especificamente o Hello World
            hello_world = await discovery.get_agent_by_port(9999)
            if hello_world:
                print(f"\n✅ Hello World Agent está ativo!")
                print(f"   Nome: {hello_world.name}")
                print(f"   URL: {hello_world.url}")
                print(f"   Skills: {len(hello_world.skills)}")
            else:
                print("\n❌ Hello World Agent NÃO encontrado na porta 9999")
                
        return agents
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    agents = asyncio.run(force_discovery())
    print(f"\n🎯 Total: {len(agents)} agentes disponíveis")
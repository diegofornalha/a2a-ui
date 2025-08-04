#!/usr/bin/env python3
"""
Script simples para acionar descoberta de agentes via UI
"""

import httpx
import asyncio
import json

async def trigger_discovery():
    """Aciona descoberta de agentes na UI"""
    
    # Lista de portas conhecidas
    ports = [9999, 10000, 10030, 10100, 10101, 11000]
    
    async with httpx.AsyncClient() as client:
        print("🔍 Verificando agentes disponíveis...")
        
        # Primeiro, vamos verificar quais agentes estão ativos
        active_agents = []
        for port in ports:
            try:
                url = f"http://localhost:{port}/.well-known/agent.json"
                response = await client.get(url, timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Porta {port}: {data.get('name', 'Unknown')}")
                    active_agents.append({
                        'port': port,
                        'name': data.get('name'),
                        'url': f"http://localhost:{port}"
                    })
            except:
                pass
        
        print(f"\n📊 Total: {len(active_agents)} agentes ativos")
        
        # Verificar especificamente o Hello World
        hello_world_found = any(agent['port'] == 9999 for agent in active_agents)
        if hello_world_found:
            print("✅ Hello World Agent está ATIVO na porta 9999!")
        else:
            print("❌ Hello World Agent NÃO está ativo na porta 9999")
            
        # Tentar fazer uma requisição para a UI descobrir os agentes
        try:
            print("\n🚀 Tentando acionar descoberta na UI...")
            # Este endpoint pode não existir, mas vale tentar
            ui_response = await client.get("http://localhost:12000/api/discover_agents", timeout=5.0)
            print(f"📡 Resposta da UI: {ui_response.status_code}")
        except:
            print("⚠️ Não foi possível acionar descoberta diretamente na UI")
            
        return active_agents

if __name__ == "__main__":
    agents = asyncio.run(trigger_discovery())
    
    print("\n🎯 RESUMO:")
    print(f"- {len(agents)} agentes ativos")
    print("- Hello World precisa aparecer na lista de agentes da UI")
    print("- Acesse http://localhost:12000/agents e clique em 'Descobrir Agentes'")
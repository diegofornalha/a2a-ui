#!/usr/bin/env python3
"""
Teste de descoberta do agente Marvin
"""

import asyncio
import httpx
import json

async def test_marvin():
    """Testa se o agente Marvin está acessível"""
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        print("🔍 Testando descoberta do agente Marvin...")
        print("-" * 50)
        
        # Testar endpoint direto
        url = "http://localhost:10030/.well-known/agent.json"
        print(f"\n📡 Testando: {url}")
        
        try:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Agente encontrado!")
                print(f"   Nome: {data.get('name')}")
                print(f"   Descrição: {data.get('description')}")
                print(f"   URL: {data.get('url')}")
                print(f"   Versão: {data.get('version')}")
                print(f"   Protocolo: {data.get('protocolVersion')}")
                
                # Verificar descoberta automática
                print("\n🤖 Testando descoberta automática...")
                
                # Simular descoberta
                from service.server.agent_discovery import AgentDiscovery
                
                discovery = AgentDiscovery(client)
                agents = await discovery.discover_localhost_agents()
                
                print(f"\n📊 Agentes descobertos automaticamente: {len(agents)}")
                for agent in agents:
                    print(f"   - {agent.name} ({agent.url})")
                
                # Verificar se Marvin foi descoberto
                marvin_found = any("marvin" in agent.name.lower() or 
                                  "10030" in agent.url for agent in agents)
                
                if marvin_found:
                    print("\n✅ Marvin foi descoberto automaticamente!")
                else:
                    print("\n⚠️ Marvin NÃO foi descoberto automaticamente")
                    print("   Possíveis razões:")
                    print("   - Timeout muito baixo")
                    print("   - Porta não está na lista padrão")
                    print("   - Formato do agent card não reconhecido")
                    
            else:
                print(f"❌ Erro: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao conectar: {str(e)}")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║       TESTE: DESCOBERTA DO AGENTE MARVIN         ║
╚══════════════════════════════════════════════════╝
    """)
    
    asyncio.run(test_marvin())
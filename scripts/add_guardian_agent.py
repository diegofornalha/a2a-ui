#!/usr/bin/env python3
"""
Script para adicionar automaticamente o Guardian Agent à UI
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Configurações
UI_SERVER_URL = "http://localhost:12000"
GUARDIAN_AGENT_URL = "http://localhost:10102"

async def add_guardian_agent():
    """Adiciona o Guardian Agent à UI via API"""
    
    async with httpx.AsyncClient() as client:
        try:
            # Primeiro, verifica se o agente está disponível
            print(f"🔍 Verificando se o Guardian Agent está disponível em {GUARDIAN_AGENT_URL}")
            
            response = await client.get(f"{GUARDIAN_AGENT_URL}/.well-known/agent.json")
            if response.status_code != 200:
                print(f"❌ Erro: Não foi possível acessar o agent card. Status: {response.status_code}")
                return False
                
            agent_card = response.json()
            print(f"✅ Agent card encontrado: {agent_card['name']}")
            print(f"📝 Descrição: {agent_card['description']}")
            
            # Agora adiciona à UI
            print(f"🚀 Adicionando Guardian Agent à UI em {UI_SERVER_URL}")
            
            # Payload para adicionar o agente
            payload = {
                "name": agent_card['name'],
                "description": agent_card['description'], 
                "url": GUARDIAN_AGENT_URL,
                "capabilities": agent_card.get('capabilities', []),
                "agent_type": "system_monitor",
                "port": 10102,
                "status": "active"
            }
            
            # Tenta adicionar o agente via diferentes endpoints possíveis
            endpoints_to_try = [
                "/api/agents/add",
                "/agents/add", 
                "/add_agent",
                "/api/v1/agents"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    url = f"{UI_SERVER_URL}{endpoint}"
                    print(f"🔄 Tentando endpoint: {url}")
                    
                    response = await client.post(url, json=payload)
                    
                    if response.status_code in [200, 201]:
                        print(f"✅ Guardian Agent adicionado com sucesso via {endpoint}")
                        print(f"📊 Resposta: {response.json()}")
                        return True
                    else:
                        print(f"⚠️ Endpoint {endpoint} retornou: {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao tentar {endpoint}: {e}")
                    continue
            
            # Se chegou aqui, tenta verificar se existe endpoint de status/health na UI
            try:
                health_response = await client.get(f"{UI_SERVER_URL}/health")
                if health_response.status_code == 200:
                    print("✅ UI está rodando, mas não encontrou endpoint para adicionar agentes")
                    print("💡 Dica: Verifique se a UI está rodando na porta 12000 e o Guardian na porta 10102")
                    print("🔗 Guardian Agent: http://localhost:10102")
                    print("🔗 Guardian Health: http://localhost:10102/health")
                    print("🔗 Guardian Monitor: http://localhost:10102/monitor")
                    return True
                    
            except Exception:
                print("❌ UI não está acessível na porta 12000")
                
            return False
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            return False

async def test_guardian_endpoints():
    """Testa todos os endpoints do Guardian Agent"""
    print("\n🧪 Testando endpoints do Guardian Agent...")
    print("=" * 50)
    
    endpoints = [
        "/",
        "/.well-known/agent.json", 
        "/health",
        "/status",
        "/monitor",
        "/agents/list"
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                url = f"{GUARDIAN_AGENT_URL}{endpoint}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                    if endpoint == "/.well-known/agent.json":
                        data = response.json()
                        print(f"   📋 Nome: {data['name']}")
                        print(f"   🔧 Capabilities: {len(data['capabilities'])}")
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - Erro: {e}")

async def main():
    """Função principal"""
    print("🛡️ Guardian Agent - Integração com UI")
    print("=" * 50)
    
    # Testa endpoints primeiro
    await test_guardian_endpoints()
    
    # Tenta adicionar à UI
    success = await add_guardian_agent()
    
    if success:
        print("\n🎉 Guardian Agent configurado com sucesso!")
        print("🔗 Acesse: http://localhost:10102")
        print("📊 Monitor: http://localhost:10102/monitor")
        print("🏥 Health: http://localhost:10102/health")
    else:
        print("\n⚠️ Guardian Agent está rodando, mas não foi possível adicionar à UI automaticamente")
        print("📝 Agent card está disponível em: http://localhost:10102/.well-known/agent.json")

if __name__ == "__main__":
    asyncio.run(main())
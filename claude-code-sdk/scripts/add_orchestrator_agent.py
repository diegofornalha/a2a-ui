#!/usr/bin/env python3
"""
Script para adicionar automaticamente o Orchestrator Agent à UI
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Configurações
UI_SERVER_URL = "http://localhost:12000"
ORCHESTRATOR_AGENT_URL = "http://localhost:10101"

async def add_orchestrator_agent():
    """Adiciona o Orchestrator Agent à UI via API"""
    
    async with httpx.AsyncClient() as client:
        try:
            # Primeiro, verifica se o agente está disponível
            print(f"🔍 Verificando se o Orchestrator Agent está disponível em {ORCHESTRATOR_AGENT_URL}")
            
            response = await client.get(f"{ORCHESTRATOR_AGENT_URL}/.well-known/agent.json")
            if response.status_code != 200:
                print(f"❌ Erro: Não foi possível acessar o agent card. Status: {response.status_code}")
                return False
                
            agent_card = response.json()
            print(f"✅ Agent card encontrado: {agent_card['name']}")
            print(f"📝 Descrição: {agent_card['description']}")
            
            # Prepara o request para registrar o agente
            register_payload = {
                "jsonrpc": "2.0",
                "method": "agent/register",
                "params": ORCHESTRATOR_AGENT_URL,
                "id": "register_orchestrator"
            }
            
            print(f"📡 Registrando agente na UI...")
            
            # Registra o agente na UI
            register_response = await client.post(
                f"{UI_SERVER_URL}/agent/register",
                json=register_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if register_response.status_code == 200:
                result = register_response.json()
                print(f"✅ Agente registrado com sucesso!")
                print(f"📊 Resposta: {json.dumps(result, indent=2)}")
                
                # Verifica se o agente foi adicionado listando os agentes
                await list_agents()
                return True
            else:
                print(f"❌ Erro ao registrar agente. Status: {register_response.status_code}")
                print(f"📄 Resposta: {register_response.text}")
                return False
                
        except httpx.ConnectError as e:
            print(f"❌ Erro de conexão: {e}")
            print("💡 Dica: Verifique se a UI está rodando na porta 12000 e o Orchestrator na porta 10101")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False

async def list_agents():
    """Lista todos os agentes registrados na UI"""
    
    async with httpx.AsyncClient() as client:
        try:
            list_payload = {
                "jsonrpc": "2.0",
                "method": "agent/list",
                "id": "list_agents"
            }
            
            response = await client.post(
                f"{UI_SERVER_URL}/agent/list",
                json=list_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                agents = result.get("result", [])
                
                print(f"\n📋 Agentes registrados ({len(agents)}):")
                for i, agent in enumerate(agents, 1):
                    print(f"  {i}. {agent['name']} - {agent['url']}")
                    print(f"     📝 {agent['description']}")
                    print(f"     ⚡ Skills: {len(agent.get('skills', []))}")
                    print()
                
                return agents
            else:
                print(f"❌ Erro ao listar agentes. Status: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erro ao listar agentes: {e}")
            return []

async def remove_agent(agent_url: str):
    """Remove um agente específico da UI"""
    
    async with httpx.AsyncClient() as client:
        try:
            remove_payload = {
                "jsonrpc": "2.0", 
                "method": "agent/remove",
                "params": agent_url,
                "id": "remove_agent"
            }
            
            response = await client.post(
                f"{UI_SERVER_URL}/agent/remove",
                json=remove_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ Agente {agent_url} removido com sucesso!")
                return True
            else:
                print(f"❌ Erro ao remover agente. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao remover agente: {e}")
            return False

async def main():
    """Função principal"""
    print("🤖 Script para Gerenciar Orchestrator Agent na UI")
    print("=" * 50)
    
    print("\n1️⃣ Listando agentes atuais...")
    current_agents = await list_agents()
    
    # Verifica se o orchestrator já está registrado
    orchestrator_exists = any(
        agent['url'] == ORCHESTRATOR_AGENT_URL 
        for agent in current_agents
    )
    
    if orchestrator_exists:
        print(f"⚠️  Orchestrator Agent já está registrado!")
        print(f"🔄 Deseja remover e adicionar novamente? (s/n)")
        
        # Para automação, vamos assumir que sim
        await remove_agent(ORCHESTRATOR_AGENT_URL)
        
    print("\n2️⃣ Adicionando Orchestrator Agent...")
    success = await add_orchestrator_agent()
    
    if success:
        print("\n🎉 Orchestrator Agent foi adicionado com sucesso à UI!")
        print("🌐 Acesse http://localhost:12000/agents para ver todos os agentes")
        print("💬 Vá para http://localhost:12000/ para começar uma conversa")
    else:
        print("\n❌ Falha ao adicionar o Orchestrator Agent")

if __name__ == "__main__":
    asyncio.run(main()) 
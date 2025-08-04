#!/usr/bin/env python3
"""
Script para registrar o Hello World Agent na UI
"""

import asyncio
import httpx
import json

# Configurações
UI_SERVER_URL = "http://localhost:12000"
HELLO_WORLD_AGENT_URL = "http://localhost:9999"

async def register_hello_world():
    """Registra o Hello World Agent na UI"""
    
    async with httpx.AsyncClient() as client:
        try:
            # Verifica se o agente está disponível
            print(f"🔍 Verificando Hello World Agent em {HELLO_WORLD_AGENT_URL}")
            
            response = await client.get(f"{HELLO_WORLD_AGENT_URL}/.well-known/agent.json")
            if response.status_code != 200:
                print(f"❌ Erro: Não foi possível acessar o agent card. Status: {response.status_code}")
                return False
                
            agent_card = response.json()
            print(f"✅ Agent encontrado: {agent_card['name']}")
            print(f"📝 Descrição: {agent_card['description']}")
            
            # Registra o agente usando a API correta
            print(f"📡 Registrando agente na UI...")
            
            # Fazendo a requisição diretamente ao endpoint correto
            register_response = await client.post(
                f"{UI_SERVER_URL}/agent/register",
                json=HELLO_WORLD_AGENT_URL,
                headers={"Content-Type": "application/json"}
            )
            
            if register_response.status_code == 200:
                print(f"✅ Hello World Agent registrado com sucesso!")
                return True
            else:
                print(f"❌ Erro ao registrar agente. Status: {register_response.status_code}")
                print(f"📄 Resposta: {register_response.text}")
                return False
                
        except httpx.ConnectError as e:
            print(f"❌ Erro de conexão: {e}")
            print("💡 Verifique se a UI está rodando na porta 12000 e o Hello World na porta 9999")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False

async def main():
    """Função principal"""
    print("🌍 Registrando Hello World Agent na UI")
    print("=" * 50)
    
    success = await register_hello_world()
    
    if success:
        print("\n🎉 Hello World Agent foi registrado com sucesso!")
        print("🌐 Acesse http://localhost:12000/agents para ver o agente")
        print("📋 Ou http://localhost:12000/event_list para ver eventos")
    else:
        print("\n❌ Falha ao registrar o Hello World Agent")

if __name__ == "__main__":
    asyncio.run(main())
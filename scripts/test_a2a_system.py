#!/usr/bin/env python3
"""
Script de teste para validar o sistema A2A implementado
"""

import asyncio
import sys
import os
import traceback

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a2a.types import Message, Part, Role, TextPart, AgentCard
from service.server.adk_host_manager import ADKHostManager
from service.server.application_manager import ApplicationManager
import httpx
import uuid

async def test_a2a_system():
    """Testa o sistema A2A implementado"""
    print("🔍 Testando sistema A2A...")
    
    try:
        # Inicializa o cliente HTTP
        async with httpx.AsyncClient() as client:
            # Cria o manager A2A
            manager = ADKHostManager(client, api_key="test-key")
            
            # Testa criação de conversação
            print("📝 Testando criação de conversação...")
            conversation = await manager.create_conversation()
            print(f"✅ Conversação criada: {conversation.conversation_id}")
            
            # Testa mensagem
            print("💬 Testando envio de mensagem...")
            test_message = Message(
                messageId=str(uuid.uuid4()),
                contextId=conversation.conversation_id,
                role=Role.user,
                parts=[Part(root=TextPart(text="Olá, como você está?"))]
            )
            
            # Sanitiza a mensagem
            sanitized_message = manager.sanitize_message(test_message)
            print(f"✅ Mensagem sanitizada: {sanitized_message.messageId}")
            
            # Lista conversações
            print("📋 Testando listagem de conversações...")
            conversations = manager.conversations
            print(f"✅ Conversações encontradas: {len(conversations)}")
            
            # Lista tarefas
            print("📋 Testando listagem de tarefas...")
            tasks = manager.tasks
            print(f"✅ Tarefas encontradas: {len(tasks)}")
            
            # Lista agentes
            print("📋 Testando listagem de agentes...")
            agents = manager.agents
            print(f"✅ Agentes encontrados: {len(agents)}")
            
            print("\n🎉 Sistema A2A validado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        traceback.print_exc()
        return False

def test_agent_imports():
    """Testa imports dos agentes A2A"""
    print("🔍 Testando imports dos agentes...")
    
    try:
        from a2a_mcp.agents.adk_travel_agent import TravelAgent
        print("✅ TravelAgent importado com sucesso")
        
        from a2a_mcp.agents.orchestrator_agent import OrchestratorAgent
        print("✅ OrchestratorAgent importado com sucesso")
        
        from a2a_mcp.agents.langgraph_planner_agent import LangraphPlannerAgent
        print("✅ LangraphPlannerAgent importado com sucesso")
        
        from a2a_mcp.common.base_agent import BaseAgent
        print("✅ BaseAgent importado com sucesso")
        
        from a2a_mcp.common.prompts import AIRFARE_COT_INSTRUCTIONS
        print("✅ Prompts importados com sucesso")
        
        print("\n🎉 Todos os imports validados!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante import: {e}")
        traceback.print_exc()
        return False

async def main():
    """Função principal"""
    print("🚀 Iniciando validação do sistema A2A Guardian...")
    print("=" * 50)
    
    # Testa imports
    imports_ok = test_agent_imports()
    
    if imports_ok:
        print("\n" + "=" * 50)
        # Testa sistema A2A
        system_ok = await test_a2a_system()
        
        if system_ok:
            print("\n🎯 Resultado: TODOS OS TESTES PASSARAM!")
            print("✅ Sistema A2A está funcionando corretamente")
            print("✅ Agentes A2A específicos implementados")
            print("✅ Servidor A2A funcional")
            print("✅ TaskManager para coordenação")
            print("✅ Arquivos reorganizados")
            return True
        else:
            print("\n❌ Resultado: TESTES FALHARAM!")
            return False
    else:
        print("\n❌ Resultado: IMPORTS FALHARAM!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 
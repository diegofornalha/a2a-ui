#!/usr/bin/env python3
"""
Script de teste para verificar se o erro AgentInfo foi corrigido
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_agent_info_import():
    """Testa se a importação de AgentInfoState funciona corretamente"""
    try:
        from state.agent_state import AgentInfoState, AgentState
        print("✅ Importação de AgentInfoState bem-sucedida!")
        
        # Testa criação de instância
        agent_info = AgentInfoState(
            name="Test Agent",
            description="Test Description",
            url="http://localhost:9999",
            port=9999
        )
        print("✅ Criação de instância AgentInfoState bem-sucedida!")
        print(f"   Nome: {agent_info.name}")
        print(f"   URL: {agent_info.url}")
        print(f"   Porta: {agent_info.port}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_agent_state():
    """Testa se o AgentState funciona corretamente"""
    try:
        from state.agent_state import AgentState, AgentInfoState
        
        # Simula o que acontece na página
        agent_list = []
        test_agents = [
            {
                'name': 'Hello World Agent',
                'description': 'Simple test agent',
                'url': 'http://localhost:9999',
                'port': 9999,
                'status': 'online',
                'is_online': True,
                'enabled': True,
                'capabilities': {},
                'version': '1.0.0'
            }
        ]
        
        for agent in test_agents:
            agent_info = AgentInfoState(
                name=agent.get('name', 'Unknown'),
                description=agent.get('description', ''),
                url=agent.get('url', ''),
                port=agent.get('port', 0),
                status=agent.get('status', 'unknown'),
                is_online=agent.get('is_online', False),
                enabled=agent.get('enabled', False),
                capabilities=agent.get('capabilities', {}),
                version=agent.get('version', '1.0.0')
            )
            agent_list.append(agent_info)
        
        print("✅ Criação de lista de agentes bem-sucedida!")
        print(f"   Número de agentes: {len(agent_list)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de AgentState: {e}")
        return False

def test_page_import():
    """Testa se a página de agentes pode ser importada"""
    try:
        from pages.agents_page_improved import agents_page_improved
        print("✅ Importação da página de agentes bem-sucedida!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação da página: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testando correção do erro AgentInfo...")
    print("=" * 50)
    
    test1 = test_agent_info_import()
    test2 = test_agent_state()
    test3 = test_page_import()
    
    print("=" * 50)
    if test1 and test2 and test3:
        print("🎉 Todos os testes passaram! O erro foi corrigido!")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.") 
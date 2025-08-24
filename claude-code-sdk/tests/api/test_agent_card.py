"""
Testes para o endpoint /.well-known/agent.json (AgentCard).
"""
import pytest
import requests
import json
from typing import Dict, Any

class TestAgentCard:
    """Testes para descoberta de agente via AgentCard."""
    
    def test_agent_card_discovery(self, base_url: str):
        """Testa se o endpoint /.well-known/agent.json retorna um AgentCard válido."""
        url = f"{base_url}/.well-known/agent.json"
        
        response = requests.get(url)
        
        # Verifica status HTTP
        assert response.status_code == 200, f"Status esperado: 200, recebido: {response.status_code}"
        
        # Verifica Content-Type
        assert 'application/json' in response.headers.get('content-type', ''), \
            "Content-Type deve ser application/json"
        
        # Verifica se é JSON válido
        try:
            agent_card = response.json()
        except json.JSONDecodeError:
            pytest.fail("Resposta não é um JSON válido")
        
        # Validações básicas do AgentCard
        assert isinstance(agent_card, dict), "AgentCard deve ser um objeto"
        
        # Campos obrigatórios
        required_fields = ['name', 'description', 'version', 'url']
        for field in required_fields:
            assert field in agent_card, f"Campo obrigatório '{field}' não encontrado"
            assert agent_card[field], f"Campo '{field}' não pode estar vazio"
        
        print(f"✅ AgentCard válido encontrado: {agent_card['name']} v{agent_card['version']}")
    
    def test_agent_card_capabilities(self, base_url: str):
        """Testa se as capabilities do agente estão bem formadas."""
        url = f"{base_url}/.well-known/agent.json"
        response = requests.get(url)
        
        assert response.status_code == 200
        agent_card = response.json()
        
        # Verifica capabilities se existir
        if 'capabilities' in agent_card:
            capabilities = agent_card['capabilities']
            assert isinstance(capabilities, dict), "Capabilities deve ser um objeto"
            
            # Verifica campos opcionais comuns
            if 'streaming' in capabilities:
                assert isinstance(capabilities['streaming'], bool), \
                    "capabilities.streaming deve ser boolean"
            
            if 'pushNotifications' in capabilities:
                assert isinstance(capabilities['pushNotifications'], bool), \
                    "capabilities.pushNotifications deve ser boolean"
            
            print(f"✅ Capabilities validadas: {capabilities}")
    
    def test_agent_card_skills(self, base_url: str):
        """Testa se as skills do agente estão bem formadas."""
        url = f"{base_url}/.well-known/agent.json"
        response = requests.get(url)
        
        assert response.status_code == 200
        agent_card = response.json()
        
        # Verifica skills se existir
        if 'skills' in agent_card:
            skills = agent_card['skills']
            assert isinstance(skills, list), "Skills deve ser uma lista"
            
            for skill in skills:
                assert isinstance(skill, dict), "Cada skill deve ser um objeto"
                assert 'id' in skill, "Skill deve ter um ID"
                assert 'name' in skill, "Skill deve ter um nome"
                
            print(f"✅ Skills validadas: {len(skills)} skills encontradas")
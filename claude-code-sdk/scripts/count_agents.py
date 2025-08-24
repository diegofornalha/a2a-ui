#!/usr/bin/env python3
"""
🤖 Contador de Agentes A2A
Script para contar e listar todos os agentes disponíveis no projeto
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

def find_agent_cards(root_dir: str = ".") -> List[Dict[str, Any]]:
    """Encontra todos os arquivos de agent cards no projeto"""
    agent_cards = []
    root_path = Path(root_dir)
    
    # Buscar arquivos .json em pastas agent_cards
    for agent_card_file in root_path.rglob("agent_cards/*.json"):
        try:
            with open(agent_card_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                agent_cards.append({
                    'file': str(agent_card_file),
                    'name': data.get('name', 'Unknown'),
                    'description': data.get('description', ''),
                    'url': data.get('url', ''),
                    'version': data.get('version', ''),
                    'skills': data.get('skills', []),
                    'capabilities': data.get('capabilities', {}),
                    'type': 'agent_card'
                })
        except Exception as e:
            print(f"❌ Erro ao ler {agent_card_file}: {e}")
    
    return agent_cards

def find_agent_executors(root_dir: str = ".") -> List[Dict[str, Any]]:
    """Encontra todos os agent executors no projeto"""
    executors = []
    root_path = Path(root_dir)
    
    # Buscar arquivos agent_executor.py
    for executor_file in root_path.rglob("*agent_executor*.py"):
        if "backup" in str(executor_file):
            continue
            
        try:
            # Ler o arquivo para extrair informações
            with open(executor_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extrair informações básicas
            executor_info = {
                'file': str(executor_file),
                'name': executor_file.parent.name,
                'path': str(executor_file.parent),
                'type': 'executor',
                'has_streaming': 'streaming' in content.lower(),
                'has_tools': 'tool' in content.lower(),
                'framework': detect_framework(content)
            }
            
            executors.append(executor_info)
            
        except Exception as e:
            print(f"❌ Erro ao ler {executor_file}: {e}")
    
    return executors

def detect_framework(content: str) -> str:
    """Detecta o framework usado no agent executor"""
    content_lower = content.lower()
    
    if 'crewai' in content_lower or 'crew' in content_lower:
        return 'CrewAI'
    elif 'langgraph' in content_lower:
        return 'LangGraph'
    elif 'autogen' in content_lower or 'ag2' in content_lower:
        return 'AutoGen/AG2'
    elif 'marvin' in content_lower:
        return 'Marvin'
    elif 'semantic' in content_lower:
        return 'Semantic Kernel'
    elif 'llama' in content_lower:
        return 'LlamaIndex'
    elif 'google' in content_lower or 'gemini' in content_lower:
        return 'Google ADK'
    elif 'openai' in content_lower:
        return 'OpenAI'
    else:
        return 'Custom'

def check_claude_configuration() -> Dict[str, Any]:
    """Verifica configurações relacionadas ao Claude"""
    claude_config = {
        'claude_sse_port': os.getenv('CLAUDE_CODE_SSE_PORT'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        'claude_model_references': []
    }
    
    # Buscar referências ao Claude no código
    root_path = Path(".")
    for py_file in root_path.rglob("*.py"):
        if "backup" in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'claude' in content.lower() or 'anthropic' in content.lower():
                claude_config['claude_model_references'].append(str(py_file))
                
        except Exception:
            pass
    
    return claude_config

def main():
    """Função principal"""
    print("🤖 Contador de Agentes A2A")
    print("=" * 50)
    
    # Encontrar agent cards
    agent_cards = find_agent_cards()
    
    # Encontrar agent executors
    executors = find_agent_executors()
    
    # Verificar configurações do Claude
    claude_config = check_claude_configuration()
    
    # Resumo
    print(f"\n📊 RESUMO DOS AGENTES DISPONÍVEIS:")
    print(f"   • Agent Cards: {len(agent_cards)}")
    print(f"   • Agent Executors: {len(executors)}")
    print(f"   • Total de Agentes: {len(agent_cards) + len(executors)}")
    
    # Detalhes dos Agent Cards
    if agent_cards:
        print(f"\n🎯 AGENT CARDS DISPONÍVEIS ({len(agent_cards)}):")
        for i, card in enumerate(agent_cards, 1):
            print(f"   {i}. {card['name']}")
            print(f"      📝 {card['description']}")
            print(f"      🔗 {card['url']}")
            print(f"      🛠️  {len(card['skills'])} skills")
            print(f"      📍 {card['file']}")
            print()
    
    # Detalhes dos Executors
    if executors:
        print(f"\n⚙️  AGENT EXECUTORS DISPONÍVEIS ({len(executors)}):")
        for i, executor in enumerate(executors, 1):
            print(f"   {i}. {executor['name']}")
            print(f"      🛠️  Framework: {executor['framework']}")
            print(f"      📡 Streaming: {'✅' if executor['has_streaming'] else '❌'}")
            print(f"      🔧 Tools: {'✅' if executor['has_tools'] else '❌'}")
            print(f"      📍 {executor['file']}")
            print()
    
    # Configurações do Claude
    print(f"\n🧠 CONFIGURAÇÕES DO CLAUDE:")
    if claude_config['claude_sse_port']:
        print(f"   • SSE Port: {claude_config['claude_sse_port']}")
    else:
        print(f"   • SSE Port: Não configurado")
    
    if claude_config['anthropic_api_key']:
        print(f"   • API Key: ✅ Configurado")
    else:
        print(f"   • API Key: ❌ Não configurado")
    
    if claude_config['claude_model_references']:
        print(f"   • Referências no código: {len(claude_config['claude_model_references'])}")
        for ref in claude_config['claude_model_references']:
            print(f"     - {ref}")
    else:
        print(f"   • Referências no código: Nenhuma encontrada")
    
    # Frameworks utilizados
    frameworks = {}
    for executor in executors:
        framework = executor['framework']
        frameworks[framework] = frameworks.get(framework, 0) + 1
    
    if frameworks:
        print(f"\n🏗️  FRAMEWORKS UTILIZADOS:")
        for framework, count in frameworks.items():
            print(f"   • {framework}: {count} agente(s)")
    
    print(f"\n🎉 TOTAL: {len(agent_cards) + len(executors)} agentes encontrados!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
🛡️ Guardian - Analisador de Projeto A2A
Sistema de análise para detectar problemas e validar implementações A2A
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json

class A2AGuardian:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.successes = []
        
    def analyze_project(self) -> Dict[str, Any]:
        """Analisa o projeto A2A em busca de problemas"""
        print("🛡️  Guardian A2A - Iniciando análise do projeto...")
        print("=" * 60)
        
        # Análises
        self._check_file_organization()
        self._check_a2a_agents()
        self._check_a2a_server()
        self._check_task_manager()
        self._check_dependencies()
        
        # Relatório final
        return self._generate_report()
    
    def _check_file_organization(self):
        """Verifica organização dos arquivos"""
        print("📁 Verificando organização dos arquivos...")
        
        # Verifica se existem arquivos soltos na raiz
        root_files = [f for f in self.project_root.iterdir() if f.is_file()]
        loose_files = [f for f in root_files if f.suffix in ['.py', '.sh', '.db'] 
                       and f.name not in ['main.py', 'pyproject.toml', 'README.md', 'Containerfile', 'uv.lock']]
        
        if loose_files:
            self.issues.append(f"🟡 {len(loose_files)} arquivos soltos encontrados: {[f.name for f in loose_files]}")
        else:
            self.successes.append("✅ Arquivos organizados corretamente")
            
        # Verifica estrutura de pastas
        expected_dirs = ['scripts', 'tests', 'data', 'a2a_mcp', 'service']
        for dir_name in expected_dirs:
            if (self.project_root / dir_name).exists():
                self.successes.append(f"✅ Pasta {dir_name}/ existe")
            else:
                self.issues.append(f"🟡 Pasta {dir_name}/ não encontrada")
    
    def _check_a2a_agents(self):
        """Verifica implementação dos agentes A2A"""
        print("🤖 Verificando agentes A2A...")
        
        agents_dir = self.project_root / "a2a_mcp" / "agents"
        if not agents_dir.exists():
            self.issues.append("🔴 Pasta a2a_mcp/agents/ não encontrada")
            return
            
        # Verifica agentes específicos
        expected_agents = {
            'adk_travel_agent.py': 'TravelAgent',
            'orchestrator_agent.py': 'OrchestratorAgent', 
            'langgraph_planner_agent.py': 'LangraphPlannerAgent',
            '__main__.py': 'Main do agente'
        }
        
        for agent_file, agent_name in expected_agents.items():
            agent_path = agents_dir / agent_file
            if agent_path.exists():
                self.successes.append(f"✅ {agent_name} implementado")
            else:
                self.issues.append(f"🟡 {agent_name} não encontrado")
        
        # Verifica base agent
        base_agent_path = self.project_root / "a2a_mcp" / "common" / "base_agent.py"
        if base_agent_path.exists():
            self.successes.append("✅ BaseAgent implementado")
        else:
            self.issues.append("🟡 BaseAgent não encontrado")
    
    def _check_a2a_server(self):
        """Verifica servidor A2A"""
        print("🖥️  Verificando servidor A2A...")
        
        server_files = [
            ('service/server/server.py', 'ConversationServer'),
            ('service/server/adk_host_manager.py', 'ADKHostManager'),
            ('service/server/application_manager.py', 'ApplicationManager'),
            ('main.py', 'Main Application')
        ]
        
        for file_path, component_name in server_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.successes.append(f"✅ {component_name} implementado")
            else:
                self.issues.append(f"🟡 {component_name} não encontrado")
    
    def _check_task_manager(self):
        """Verifica TaskManager"""
        print("⚙️  Verificando TaskManager...")
        
        task_manager_components = [
            ('service/server/adk_host_manager.py', 'ADKHostManager (TaskManager)'),
            ('service/server/in_memory_manager.py', 'InMemoryManager'),
            ('service/server/application_manager.py', 'ApplicationManager Interface')
        ]
        
        for file_path, component_name in task_manager_components:
            full_path = self.project_root / file_path
            if full_path.exists():
                # Verifica se tem funcionalidades de task management
                content = full_path.read_text()
                if 'task' in content.lower() or 'Task' in content:
                    self.successes.append(f"✅ {component_name} com funcionalidades de task")
                else:
                    self.issues.append(f"🟡 {component_name} sem funcionalidades de task")
            else:
                self.issues.append(f"🟡 {component_name} não encontrado")
    
    def _check_dependencies(self):
        """Verifica dependências"""
        print("📦 Verificando dependências...")
        
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            self.issues.append("🟡 pyproject.toml não encontrado")
            return
            
        content = pyproject_path.read_text()
        
        # Dependências críticas
        critical_deps = ['a2a-sdk', 'fastapi', 'mesop', 'google-genai', 'httpx']
        
        for dep in critical_deps:
            if dep in content:
                self.successes.append(f"✅ Dependência {dep} encontrada")
            else:
                self.issues.append(f"🟡 Dependência {dep} não encontrada")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Gera relatório final"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DO GUARDIAN")
        print("=" * 60)
        
        # Sucessos
        if self.successes:
            print("\n✅ SUCESSOS:")
            for success in self.successes:
                print(f"   {success}")
        
        # Problemas
        if self.issues:
            print(f"\n🚨 PROBLEMAS DETECTADOS ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   {issue}")
        else:
            print("\n🎉 NENHUM PROBLEMA DETECTADO!")
        
        # Classificação
        total_checks = len(self.successes) + len(self.issues)
        success_rate = (len(self.successes) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n📈 TAXA DE SUCESSO: {success_rate:.1f}%")
        
        if success_rate >= 90:
            status = "🟢 EXCELENTE"
        elif success_rate >= 70:
            status = "🟡 BOM"
        elif success_rate >= 50:
            status = "🟠 PRECISA MELHORAR"
        else:
            status = "🔴 CRÍTICO"
            
        print(f"🏆 STATUS GERAL: {status}")
        
        return {
            "status": status,
            "success_rate": success_rate,
            "successes": self.successes,
            "issues": self.issues,
            "total_checks": total_checks
        }

def main():
    """Função principal"""
    print("🛡️  Guardian A2A - Sistema de Análise de Projeto")
    print("=" * 60)
    
    # Determina o diretório do projeto
    project_root = "."
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    
    # Executa análise
    guardian = A2AGuardian(project_root)
    report = guardian.analyze_project()
    
    # Retorna código de saída baseado no status
    if report["success_rate"] >= 90:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 
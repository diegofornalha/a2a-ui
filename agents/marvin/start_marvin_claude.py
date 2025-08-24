#!/usr/bin/env python3
"""
Script para iniciar o agente Marvin usando Claude Code SDK.
NÃO precisa de API keys externas - usa Claude local!
"""

import sys
import os
import asyncio
import logging

# Adicionar caminhos necessários
sys.path.insert(0, '/home/codable/terminal/claude-code-sdk-python/src')
sys.path.insert(0, '/home/codable/terminal/ai-sdk-provider-python/src')
sys.path.insert(0, '/home/codable/terminal/app-agentflix/web/a2a-ui')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_claude():
    """Verifica se Claude está disponível."""
    import subprocess
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, None
    except:
        return False, None


async def main():
    """Função principal para iniciar o agente Marvin com Claude."""
    
    print("=" * 60)
    print("🤖 Agente Marvin com Claude Code SDK")
    print("=" * 60)
    print("✅ SEM necessidade de API Keys externas!")
    print("✅ Usa Claude Code Desktop local")
    print("=" * 60)
    
    # Verificar Claude
    has_claude, version = check_claude()
    if has_claude:
        print(f"✅ Claude detectado: {version}")
    else:
        print("⚠️ Claude Code não encontrado no PATH")
        print("   Instale em: https://claude.ai/code")
        print("   Continuando mesmo assim...")
    
    # Importar agente com Claude
    try:
        from agent_claude import ClaudeExtractorAgent
        
        print("\n✅ Agente Claude carregado com sucesso!")
        
        # Configurar agente de exemplo
        instructions = """
        Você é o Marvin, um assistente útil e inteligente.
        Você usa Claude Code SDK para processar informações.
        Seja conciso, preciso e útil em suas respostas.
        """
        
        # Criar agente
        agent = ClaudeExtractorAgent(
            instructions=instructions,
            result_type=dict  # Tipo genérico para exemplo
        )
        
        print("\n📋 Configuração do Agente:")
        print(f"   Nome: Marvin (powered by Claude)")
        print(f"   SDK: Claude Code SDK")
        print(f"   Modo: Local (sem cloud)")
        
        # Teste simples
        print("\n🧪 Teste rápido do agente...")
        print("-" * 40)
        
        test_query = "Olá Marvin! Quem é você e o que você pode fazer?"
        test_session = "test-session-001"
        
        print(f"Pergunta: {test_query}")
        print("Resposta: ", end="", flush=True)
        
        result = await agent.invoke(test_query, test_session)
        
        if result.get("text_parts"):
            for part in result["text_parts"]:
                if hasattr(part, 'text'):
                    print(part.text)
                else:
                    print(str(part))
        
        print("-" * 40)
        print("\n✅ Agente funcionando corretamente!")
        
        # Iniciar servidor A2A se necessário
        print("\n🚀 Iniciando servidor A2A do Marvin...")
        
        # Importar e executar servidor
        from server import serve_agent
        from agent_executor import create_marvin_agent
        
        # Substituir factory do agente para usar Claude
        def create_claude_marvin_agent():
            """Factory para criar agente Marvin com Claude."""
            return ClaudeExtractorAgent(
                instructions="""
                Você é o Marvin, assistente especializado em extração de informações.
                Use Claude Code SDK para processar queries dos usuários.
                Seja preciso, útil e faça perguntas clarificadoras quando necessário.
                """,
                result_type=dict
            )
        
        # Configurar porta
        port = int(os.getenv('MARVIN_PORT', '8180'))
        
        print(f"\n📡 Servidor A2A rodando na porta {port}")
        print(f"   URL: http://localhost:{port}")
        print("\nEndpoints disponíveis:")
        print(f"   POST http://localhost:{port}/invoke")
        print(f"   POST http://localhost:{port}/stream")
        print("\nPressione Ctrl+C para parar")
        print("-" * 60)
        
        # Executar servidor
        await serve_agent(create_claude_marvin_agent(), port=port)
        
    except ImportError as e:
        print(f"\n❌ Erro ao importar: {e}")
        print("\n📦 Verifique os caminhos:")
        print("   - Claude SDK: /home/codable/terminal/claude-code-sdk-python/src")
        print("   - Este script: agent_claude.py no mesmo diretório")
    except KeyboardInterrupt:
        print("\n\n⏹️ Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Iniciando Marvin com Claude Code SDK...")
    asyncio.run(main())
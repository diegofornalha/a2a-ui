#!/usr/bin/env python3
"""
Script para rodar o servidor MCP com Claude Code SDK
Configura todos os caminhos necessários
"""

import sys
import os

# Adicionar caminhos necessários
sys.path.insert(0, '/home/codable/terminal/claude-code-sdk-python/src')
sys.path.insert(0, '/home/codable/terminal/ai-sdk-provider-python/src')
sys.path.insert(0, '/home/codable/terminal/app-agentflix/web/a2a-ui')

print("=" * 60)
print("🚀 Servidor MCP com Claude Code SDK")
print("=" * 60)
print("✅ NÃO precisa de Google API Key!")
print("✅ Usa Claude Code local")
print("=" * 60)

# Verificar Claude
import subprocess
try:
    result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Claude detectado: {result.stdout.strip()}")
    else:
        print("⚠️ Claude não encontrado")
except:
    print("⚠️ Claude Code não está no PATH")

# Importar e executar servidor
try:
    from a2a_mcp.mcp.server import serve
    
    # Configurações
    host = os.getenv('MCP_HOST', 'localhost')
    port = int(os.getenv('MCP_PORT', '8175'))
    transport = os.getenv('MCP_TRANSPORT', 'http')  # Mudando para HTTP para teste
    
    print(f"\n📋 Configuração:")
    print(f"   Host: {host}")
    print(f"   Porta: {port}")
    print(f"   Transport: {transport}")
    print(f"   SDK: Claude Code")
    
    print("\n🔄 Iniciando servidor...")
    print(f"   URL: http://{host}:{port}")
    print("\n📝 Endpoints disponíveis:")
    print(f"   POST http://{host}:{port}/find_agent")
    print(f"   GET  http://{host}:{port}/list_all_agents")
    print(f"   POST http://{host}:{port}/analyze_agent_with_claude")
    print("\nPressione Ctrl+C para parar")
    print("-" * 60)
    
    # Executar servidor
    serve(host, port, transport)
    
except KeyboardInterrupt:
    print("\n\n⏹️ Servidor parado")
except ImportError as e:
    print(f"\n❌ Erro de importação: {e}")
    print("\n📦 Verifique se os caminhos estão corretos:")
    print("   - Claude SDK: /home/codable/terminal/claude-code-sdk-python/src")
    print("   - AI Provider: /home/codable/terminal/ai-sdk-provider-python/src")
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
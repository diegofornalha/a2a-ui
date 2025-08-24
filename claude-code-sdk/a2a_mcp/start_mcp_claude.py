#!/usr/bin/env python3
"""
Script principal para iniciar o servidor MCP com Claude Code SDK.
NÃO USA Google API - 100% Claude local!
"""

import os
import sys
import asyncio
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar servidor MCP com Claude
from a2a_mcp.mcp.server import serve, init_api_key


def main():
    """Função principal para iniciar o servidor."""
    print("=" * 60)
    print("🚀 A2A MCP Server com Claude Code SDK")
    print("=" * 60)
    print("✅ NÃO precisa de Google API Key!")
    print("✅ Usa Claude Code instalado localmente")
    print("✅ 100% gratuito e privado")
    print("=" * 60)
    
    # Verificar Claude
    try:
        import subprocess
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Claude Code detectado: {result.stdout.strip()}")
        else:
            print("⚠️ Claude Code não encontrado no PATH")
            print("   Instale em: https://claude.ai/code")
    except:
        print("⚠️ Claude Code não detectado")
        print("   Por favor, instale o Claude Code Desktop")
    
    # Configurações
    host = os.getenv('MCP_HOST', 'localhost')
    port = int(os.getenv('MCP_PORT', '8175'))
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    
    print(f"\n📋 Configuração:")
    print(f"   Host: {host}")
    print(f"   Porta: {port}")
    print(f"   Transport: {transport}")
    print(f"   SDK: Claude Code (local)")
    
    # NÃO precisa de API key!
    init_api_key()  # Função vazia, apenas para compatibilidade
    
    print("\n🔄 Iniciando servidor...")
    print("-" * 60)
    
    # Executar servidor
    try:
        serve(host, port, transport)
    except KeyboardInterrupt:
        print("\n\n⏹️ Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar servidor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
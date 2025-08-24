#!/usr/bin/env python3
"""
Script para iniciar o servidor Marvin
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Iniciar o servidor Marvin"""
    try:
        logger.info("🚀 Iniciando servidor Marvin...")
        
        # Verificar se temos as dependências
        from agents.marvin.agent import ExtractorAgent
        from agents.marvin.agent_executor import ExtractorAgentExecutor
        logger.info("✅ Dependências carregadas")
        
        # Importar o módulo principal
        from agents.marvin import __main__ as marvin_main
        
        # Simular os argumentos da linha de comando
        sys.argv = ['agents.marvin', '--host', 'localhost', '--port', '10030']
        
        logger.info("🌐 Iniciando servidor na porta 10030...")
        marvin_main.main()
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
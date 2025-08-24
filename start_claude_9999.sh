#!/bin/bash

# Script simplificado para iniciar na porta 12000
echo "🚀 Iniciando A2A-UI com Claude SDK na porta 12000..."

cd "$(dirname "$0")"

# Ativar venv se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instalar dependências mínimas se necessário
pip install -q claude-code-sdk anyio mesop 2>/dev/null

echo ""
echo "============================================"
echo "🌐 UI Mesop: http://localhost:12000"
echo "🤖 Usando: Claude Code SDK"
echo "⚡ Sem necessidade de API key!"
echo "============================================"
echo ""

# Executar Mesop diretamente
mesop main.py --port 12000
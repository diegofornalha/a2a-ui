#!/bin/bash
# Script para iniciar o servidor Marvin

echo "🚀 Iniciando servidor Marvin..."

# Verificar se o servidor já está rodando
if lsof -i :10030 > /dev/null 2>&1; then
    echo "⚠️  Servidor já está rodando na porta 10030"
    exit 1
fi

# Navegar para o diretório correto
cd /Users/agents/Desktop/codex/ui

# Iniciar o servidor
echo "📦 Iniciando servidor Marvin na porta 10030..."
uv run python agents/marvin/server.py

echo "✅ Servidor iniciado com sucesso!"
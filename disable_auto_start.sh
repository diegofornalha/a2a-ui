#!/bin/bash

# ============================================================================
# Script para Desabilitar Inicialização Automática de Processos
# ============================================================================

echo "🛑 Desabilitando inicialização automática de processos..."

# 1. Parar todos os processos do agent_manager
echo "📋 Parando processos do agent_manager..."
pkill -f "agent_manager.sh"
pkill -f "monitor start"
pkill -f "start all"

# 2. Parar todos os processos do servidor Mesop
echo "📋 Parando processos do servidor Mesop..."
pkill -f "uv run main.py"
pkill -f "python.*main.py"
pkill -f "uvicorn"

# 3. Verificar se há processos na porta 12000
echo "📋 Verificando porta 12000..."
if lsof -i :12000 > /dev/null 2>&1; then
    echo "⚠️  Ainda há processos na porta 12000. Matando..."
    lsof -i :12000 | awk 'NR>1 {print $2}' | xargs kill -9
fi

# 4. Verificar se há processos na porta 8085 (backend)
echo "📋 Verificando porta 8085..."
if lsof -i :8085 > /dev/null 2>&1; then
    echo "⚠️  Ainda há processos na porta 8085. Matando..."
    lsof -i :8085 | awk 'NR>1 {print $2}' | xargs kill -9
fi

# 5. Verificar se há processos de monitoramento
echo "📋 Verificando processos de monitoramento..."
ps aux | grep -E "monitor|watch|auto" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

# 6. Verificar se há processos relacionados ao projeto
echo "📋 Verificando processos relacionados ao projeto..."
ps aux | grep -E "claude-20x|agent" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

echo "✅ Todos os processos foram parados!"
echo ""
echo "📊 Status final:"
echo "   - Porta 12000: $(lsof -i :12000 > /dev/null 2>&1 && echo "❌ Ocupada" || echo "✅ Livre")"
echo "   - Porta 8085: $(lsof -i :8085 > /dev/null 2>&1 && echo "❌ Ocupada" || echo "✅ Livre")"
echo "   - Processos agent_manager: $(ps aux | grep agent_manager | grep -v grep | wc -l)"
echo "   - Processos Mesop: $(ps aux | grep -E "main.py|uvicorn" | grep -v grep | wc -l)"
echo ""
echo "🎉 Inicialização automática desabilitada com sucesso!" 
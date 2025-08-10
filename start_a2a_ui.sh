#!/bin/bash

# ============================================================================
# Script para Iniciar o Servidor A2A-UI
# ============================================================================

echo "🚀 Iniciando o servidor A2A-UI..."
echo ""

# 1. Verificar se Python está instalado
echo "📋 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não está instalado. Por favor, instale Python3 primeiro."
    exit 1
fi
echo "✅ Python3 encontrado: $(python3 --version)"

# 2. Verificar se uv está instalado (opcional)
echo "📋 Verificando uv (opcional)..."
if command -v uv &> /dev/null; then
    echo "✅ uv encontrado: $(uv --version)"
    USE_UV=true
else
    echo "⚠️  uv não encontrado. Usando python diretamente."
    USE_UV=false
fi

# 3. Parar processos existentes se estiverem rodando
echo ""
echo "📋 Verificando processos existentes..."

# Verificar porta 12000
if lsof -i :12000 > /dev/null 2>&1; then
    echo "⚠️  Porta 12000 está em uso. Parando processo existente..."
    lsof -i :12000 | awk 'NR>1 {print $2}' | xargs kill -9 2>/dev/null
    sleep 2
fi

# Verificar porta 8085 (backend)
if lsof -i :8085 > /dev/null 2>&1; then
    echo "⚠️  Porta 8085 está em uso. Parando processo existente..."
    lsof -i :8085 | awk 'NR>1 {print $2}' | xargs kill -9 2>/dev/null
    sleep 2
fi

# Parar processos Mesop/uvicorn existentes
pkill -f "python.*main.py" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
pkill -f "uv run main.py" 2>/dev/null

echo "✅ Processos anteriores limpos"

# 4. Definir diretório do projeto
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"
echo ""
echo "📁 Diretório do projeto: $PROJECT_DIR"

# 5. Verificar arquivo .env (opcional)
if [ -f ".env" ]; then
    echo "✅ Arquivo .env encontrado"
    source .env
else
    echo "⚠️  Arquivo .env não encontrado (opcional)"
fi

# 6. Configurar variáveis de ambiente
export A2A_UI_HOST="${A2A_UI_HOST:-0.0.0.0}"
export A2A_UI_PORT="${A2A_UI_PORT:-12000}"
export DEBUG_MODE="${DEBUG_MODE:-false}"

echo ""
echo "🔧 Configurações:"
echo "   - Host: $A2A_UI_HOST"
echo "   - Porta: $A2A_UI_PORT"
echo "   - Debug: $DEBUG_MODE"

# 7. Instalar dependências se necessário
if [ "$1" == "--install" ] || [ "$1" == "-i" ]; then
    echo ""
    echo "📦 Instalando dependências..."
    if [ "$USE_UV" == true ]; then
        uv pip install -r pyproject.toml
    else
        pip install -e .
    fi
fi

# 8. Iniciar o servidor
echo ""
echo "🌟 Iniciando servidor A2A-UI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$1" == "--background" ] || [ "$1" == "-b" ]; then
    # Executar em background
    echo "🔄 Executando em background..."
    
    if [ "$USE_UV" == true ]; then
        nohup uv run main.py > a2a_ui.log 2>&1 &
    else
        nohup python3 main.py > a2a_ui.log 2>&1 &
    fi
    
    SERVER_PID=$!
    echo "✅ Servidor iniciado em background (PID: $SERVER_PID)"
    echo "📝 Logs salvos em: $PROJECT_DIR/a2a_ui.log"
    echo ""
    echo "Para acompanhar os logs em tempo real:"
    echo "  tail -f a2a_ui.log"
    echo ""
    echo "Para parar o servidor:"
    echo "  kill $SERVER_PID"
    echo "  ou"
    echo "  ./disable_auto_start.sh"
else
    # Executar em foreground
    echo "🔄 Executando em foreground (pressione Ctrl+C para parar)..."
    echo ""
    
    if [ "$USE_UV" == true ]; then
        uv run main.py
    else
        python3 main.py
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Acesse a interface em:"
echo "   http://localhost:$A2A_UI_PORT"
echo "   http://$A2A_UI_HOST:$A2A_UI_PORT"
echo ""
echo "📚 Páginas disponíveis:"
echo "   - Home: http://localhost:$A2A_UI_PORT/"
echo "   - Agents: http://localhost:$A2A_UI_PORT/agents"
echo "   - Conversation: http://localhost:$A2A_UI_PORT/conversation"
echo "   - Events: http://localhost:$A2A_UI_PORT/event_list"
echo "   - Tasks: http://localhost:$A2A_UI_PORT/task_list"
echo "   - Settings: http://localhost:$A2A_UI_PORT/settings"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
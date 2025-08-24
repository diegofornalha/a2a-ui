#!/bin/bash
# Script melhorado para iniciar o servidor Marvin localmente

echo "🚀 Iniciando servidor Marvin..."

# Verificar se o servidor já está rodando
if lsof -i :10030 > /dev/null 2>&1; then
    echo "✅ Servidor Marvin já está rodando na porta 10030"
    
    # Testar se está respondendo
    if curl -s http://localhost:10030/.well-known/agent.json > /dev/null 2>&1; then
        echo "✅ Marvin está respondendo corretamente!"
        echo "📍 Endpoint: http://localhost:10030/"
        echo ""
        echo "Para adicionar ao A2A-UI:"
        echo "1. Acesse http://localhost:12000"
        echo "2. Clique em '🤖 Adicionar Agente Manualmente'"
        echo "3. Digite: http://localhost:10030/"
    else
        echo "⚠️  Servidor está na porta mas não responde"
    fi
    exit 0
fi

# Diretório base
BASE_DIR="/home/codable/terminal/app-agentflix/web/a2a-ui"

# Verificar onde o código do Marvin está
if [ -d "$BASE_DIR/agents/marvin" ]; then
    MARVIN_DIR="$BASE_DIR/agents/marvin"
    echo "📁 Usando Marvin de: $MARVIN_DIR"
elif [ -d "$BASE_DIR/agents-a2a/marvin" ]; then
    MARVIN_DIR="$BASE_DIR/agents-a2a/marvin"
    echo "📁 Usando Marvin de: $MARVIN_DIR"
else
    echo "❌ Diretório do Marvin não encontrado"
    exit 1
fi

# Navegar para o diretório
cd "$MARVIN_DIR"

# Iniciar o servidor
echo "📦 Iniciando servidor Marvin na porta 10030..."

# Verificar se existe server.py
if [ -f "server.py" ]; then
    # Tentar com uv primeiro
    if command -v uv &> /dev/null; then
        echo "Usando uv para executar..."
        uv run python server.py &
    # Senão, usar python diretamente
    elif [ -f ".venv/bin/python" ]; then
        echo "Usando venv local..."
        .venv/bin/python server.py &
    else
        echo "Usando python3 do sistema..."
        python3 server.py &
    fi
    
    # Aguardar servidor iniciar
    echo "⏳ Aguardando servidor iniciar..."
    sleep 3
    
    # Verificar se iniciou
    if curl -s http://localhost:10030/.well-known/agent.json > /dev/null 2>&1; then
        echo "✅ Servidor Marvin iniciado com sucesso!"
        echo "📍 Endpoint: http://localhost:10030/"
        echo ""
        echo "Para adicionar ao A2A-UI:"
        echo "1. Acesse http://localhost:12000"
        echo "2. Clique em '🤖 Adicionar Agente Manualmente'"
        echo "3. Digite: http://localhost:10030/"
    else
        echo "⚠️  Servidor pode estar iniciando ainda..."
    fi
else
    echo "❌ Arquivo server.py não encontrado em $MARVIN_DIR"
    exit 1
fi
#!/bin/bash

# Script para iniciar o servidor MCP com Claude Code SDK
# Não precisa de GOOGLE_API_KEY!

echo "🚀 Iniciando Agent Cards MCP Server com Claude Code SDK"
echo "=================================================="

# Verificar se Claude está instalado
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code não encontrado!"
    echo "Por favor, instale o Claude Code Desktop primeiro."
    echo "Download: https://claude.ai/code"
    exit 1
fi

echo "✅ Claude Code detectado: $(claude --version 2>/dev/null || echo 'instalado')"

# Diretório base
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

# Criar diretório de agent cards se não existir
if [ ! -d "agent_cards" ]; then
    echo "📁 Criando diretório agent_cards..."
    mkdir -p agent_cards
    
    # Criar alguns agent cards de exemplo
    cat > agent_cards/orchestrator.json << 'EOF'
{
    "name": "Orchestrator Agent",
    "description": "Coordena e delega tarefas entre múltiplos agentes",
    "url": "http://localhost:8001",
    "capabilities": ["delegation", "coordination", "task_planning"],
    "version": "1.0.0"
}
EOF

    cat > agent_cards/planner.json << 'EOF'
{
    "name": "Planner Agent", 
    "description": "Planeja e estrutura tarefas complexas",
    "url": "http://localhost:8002",
    "capabilities": ["planning", "breakdown", "scheduling"],
    "version": "1.0.0"
}
EOF

    cat > agent_cards/coder.json << 'EOF'
{
    "name": "Coder Agent",
    "description": "Especialista em desenvolvimento e código",
    "url": "http://localhost:8003",
    "capabilities": ["coding", "debugging", "refactoring"],
    "version": "1.0.0"
}
EOF

    echo "✅ Agent cards de exemplo criados"
fi

# Configurar ambiente Python
echo "🐍 Configurando ambiente Python..."

# Verificar se uv está instalado
if command -v uv &> /dev/null; then
    echo "Usando uv para gerenciar dependências..."
    UV_CMD="uv run"
else
    echo "Usando Python diretamente..."
    UV_CMD="python3"
fi

# Opções de execução
MODE=${1:-stdio}
HOST=${MCP_HOST:-localhost}
PORT=${MCP_PORT:-8175}

echo ""
echo "📋 Configuração:"
echo "  - Modo: $MODE"
echo "  - Host: $HOST" 
echo "  - Porta: $PORT"
echo "  - Claude SDK: Ativo"
echo "  - Google API: Não necessária!"
echo ""

# Executar servidor
if [ "$MODE" = "stdio" ]; then
    echo "🔌 Iniciando em modo STDIO (para integração com Claude Code)..."
    echo "Para testar, use: echo '{\"method\":\"tools/list\"}' | $0 stdio"
    exec $UV_CMD -m a2a_mcp.mcp.claude_server
else
    echo "🌐 Iniciando servidor HTTP em $HOST:$PORT..."
    MCP_HOST=$HOST MCP_PORT=$PORT MCP_TRANSPORT=http \
        exec $UV_CMD -m a2a_mcp.mcp.claude_server
fi
#!/bin/bash

echo "🚀 Iniciando servidor backend Claude Code SDK na porta 8085..."
echo ""

# Navegar para o diretório correto
cd /home/codable/terminal/app-agentflix/web/a2a-ui/claude-code-sdk

# Verificar se o arquivo backend_server.py existe
if [ ! -f "backend_server.py" ]; then
    echo "❌ Erro: backend_server.py não encontrado!"
    exit 1
fi

# Matar processo anterior se existir
echo "🔍 Verificando processos anteriores..."
pkill -f "backend_server.py" 2>/dev/null
sleep 1

# Iniciar servidor em background
echo "🚀 Iniciando servidor..."
nohup python backend_server.py > backend_server.log 2>&1 &
SERVER_PID=$!

echo "📝 PID do servidor: $SERVER_PID"

# Aguardar servidor iniciar
echo "⏳ Aguardando servidor iniciar..."
sleep 3

# Verificar se servidor está rodando
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Servidor iniciado com sucesso!"
    echo ""
    echo "📊 Endpoints disponíveis:"
    echo "   - Health Check: http://localhost:8085/health"
    echo "   - Claude Status: http://localhost:8085/claude/status"
    echo "   - Claude Query: http://localhost:8085/claude/query"
    echo ""
    echo "📝 Logs em: backend_server.log"
    echo "🛑 Para parar: kill $SERVER_PID"
    
    # Salvar PID em arquivo
    echo $SERVER_PID > backend_server.pid
    
    # Testar health check
    echo ""
    echo "🔍 Testando health check..."
    curl -s http://localhost:8085/health | python -m json.tool
    
else
    echo "❌ Erro ao iniciar servidor!"
    echo "📝 Verificar logs em: backend_server.log"
    tail -20 backend_server.log
    exit 1
fi
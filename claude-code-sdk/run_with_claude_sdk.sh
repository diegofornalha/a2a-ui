#!/bin/bash

# Script para executar o a2a-ui com Claude SDK
# Substitui completamente o uso do Gemini/Vertex AI

echo "============================================"
echo "🚀 A2A-UI com Claude Code SDK"
echo "============================================"

# Diretório base
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BASE_DIR"

# Verificar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -q --upgrade pip

# Instalar Claude Code SDK
echo "🤖 Instalando Claude Code SDK..."
pip install -q claude-code-sdk anyio

# Instalar outras dependências necessárias
echo "📦 Instalando dependências do projeto..."
pip install -q mesop fastapi uvicorn httpx pydantic python-dotenv

# Verificar instalação do Claude SDK
echo ""
echo "🔍 Verificando Claude Code SDK..."
python3 -c "import claude_code_sdk; print(f'✅ Claude SDK v{claude_code_sdk.__version__} instalado com sucesso!')" 2>/dev/null || {
    echo "❌ Erro ao importar Claude SDK"
    exit 1
}

# Configurar variáveis de ambiente
echo ""
echo "⚙️ Configurando ambiente..."
export USE_CLAUDE_SDK=true
export DISABLE_GEMINI=true
export A2A_BACKEND_URL="http://localhost:8000"

# Testar o agente Claude SDK
echo ""
echo "🧪 Testando Claude SDK Agent..."
python3 -c "
import sys
sys.path.insert(0, '.')
from agents.claude_sdk_agent import get_claude_sdk_agent
agent = get_claude_sdk_agent()
if agent.is_ready:
    print('✅ Claude SDK Agent está pronto!')
else:
    print('❌ Claude SDK Agent não está pronto')
    sys.exit(1)
" || exit 1

# Iniciar servidor backend
echo ""
echo "🌐 Iniciando servidor backend..."
python3 backend_server.py &
BACKEND_PID=$!
echo "   PID do backend: $BACKEND_PID"

# Aguardar servidor iniciar
sleep 3

# Verificar se o backend está rodando
curl -s http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend está rodando!"
else
    echo "❌ Backend não está respondendo"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Iniciar UI Mesop
echo ""
echo "🎨 Iniciando UI Mesop..."
echo "============================================"
echo "🌐 Acesse: http://localhost:12000"
echo "🤖 Usando: Claude Code SDK"
echo "⚡ Sem necessidade de API key!"
echo "============================================"
echo ""

# Executar Mesop
mesop main.py --port 12000

# Cleanup ao sair
echo ""
echo "🧹 Limpando processos..."
kill $BACKEND_PID 2>/dev/null
deactivate

echo "✅ Finalizado!"
#!/bin/bash

# Script para executar e manter o A2A-UI com Claude integrado
# Mantém os servidores rodando e reinicia se necessário

echo "🚀 A2A-UI + Claude Assistant - Sistema de Execução Contínua"
echo "============================================================"
echo ""

# Configurações
export A2A_UI_HOST=0.0.0.0
export A2A_UI_PORT=12000
export BACKEND_PORT=8085
export CLAUDE_ENABLED=true

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PIDs dos processos
BACKEND_PID=""
FRONTEND_PID=""

# Função para limpar processos ao sair
cleanup() {
    echo -e "\n${YELLOW}🛑 Parando servidores...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend parado${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend parado${NC}"
    fi
    
    # Matar qualquer processo órfão nas portas
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null
    lsof -ti:$A2A_UI_PORT | xargs kill -9 2>/dev/null
    
    echo -e "${GREEN}✅ Sistema encerrado${NC}"
    exit 0
}

# Configurar trap para limpar ao sair
trap cleanup EXIT INT TERM

# Função para verificar se Claude CLI está disponível
check_claude_cli() {
    if command -v claude &> /dev/null; then
        echo -e "${GREEN}✅ Claude CLI encontrado: $(claude --version 2>&1 | head -n 1)${NC}"
        return 0
    else
        echo -e "${RED}❌ Claude CLI não encontrado!${NC}"
        echo "   Instale com: npm install -g @anthropic-ai/claude-code"
        echo "   Ou faça login: claude login"
        return 1
    fi
}

# Função para verificar se porta está livre
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ Porta $port já está em uso. Liberando...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Função para iniciar o backend
start_backend() {
    echo -e "${BLUE}🔧 Iniciando Backend (porta $BACKEND_PORT)...${NC}"
    check_port $BACKEND_PORT
    
    python backend_server.py > backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Aguardar backend iniciar
    local count=0
    while ! curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; do
        if [ $count -gt 30 ]; then
            echo -e "${RED}❌ Backend falhou ao iniciar${NC}"
            return 1
        fi
        sleep 1
        count=$((count + 1))
    done
    
    echo -e "${GREEN}✅ Backend rodando (PID: $BACKEND_PID)${NC}"
    
    # Verificar status do Claude
    if curl -s http://localhost:$BACKEND_PORT/claude/status | grep -q "initialized.*true"; then
        echo -e "${GREEN}✅ Claude Service ativo${NC}"
    else
        echo -e "${YELLOW}⚠️ Claude Service pode não estar totalmente inicializado${NC}"
    fi
    
    return 0
}

# Função para iniciar o frontend
start_frontend() {
    echo -e "${BLUE}🌐 Iniciando Frontend (porta $A2A_UI_PORT)...${NC}"
    check_port $A2A_UI_PORT
    
    python main.py > frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Aguardar frontend iniciar
    local count=0
    while ! curl -s http://localhost:$A2A_UI_PORT > /dev/null 2>&1; do
        if [ $count -gt 30 ]; then
            echo -e "${RED}❌ Frontend falhou ao iniciar${NC}"
            return 1
        fi
        sleep 1
        count=$((count + 1))
    done
    
    echo -e "${GREEN}✅ Frontend rodando (PID: $FRONTEND_PID)${NC}"
    return 0
}

# Função para monitorar serviços
monitor_services() {
    while true; do
        # Verificar backend
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${YELLOW}⚠️ Backend parou. Reiniciando...${NC}"
            start_backend
        fi
        
        # Verificar frontend
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${YELLOW}⚠️ Frontend parou. Reiniciando...${NC}"
            start_frontend
        fi
        
        # Verificar saúde do backend
        if ! curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️ Backend não responde. Reiniciando...${NC}"
            kill $BACKEND_PID 2>/dev/null
            start_backend
        fi
        
        # Verificar saúde do frontend
        if ! curl -s http://localhost:$A2A_UI_PORT > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️ Frontend não responde. Reiniciando...${NC}"
            kill $FRONTEND_PID 2>/dev/null
            start_frontend
        fi
        
        sleep 5
    done
}

# Função principal
main() {
    echo -e "${BLUE}📋 Configuração:${NC}"
    echo "  - Frontend: http://localhost:$A2A_UI_PORT"
    echo "  - Backend: http://localhost:$BACKEND_PORT"
    echo "  - Claude: Ativado via CLI"
    echo ""
    
    # Verificar Claude CLI
    if ! check_claude_cli; then
        echo -e "${RED}Abortando: Claude CLI é necessário${NC}"
        exit 1
    fi
    
    echo ""
    
    # Iniciar serviços
    if ! start_backend; then
        echo -e "${RED}Falha ao iniciar backend${NC}"
        exit 1
    fi
    
    if ! start_frontend; then
        echo -e "${RED}Falha ao iniciar frontend${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Sistema A2A-UI + Claude totalmente operacional!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}📡 URLs disponíveis:${NC}"
    echo "  - Interface Principal: http://localhost:$A2A_UI_PORT"
    echo "  - Chat com Claude: http://localhost:$A2A_UI_PORT/conversation"
    echo "  - Lista de Agentes: http://localhost:$A2A_UI_PORT/agents"
    echo "  - Configurações: http://localhost:$A2A_UI_PORT/settings"
    echo ""
    echo -e "${BLUE}🤖 Endpoints Backend:${NC}"
    echo "  - Health Check: http://localhost:$BACKEND_PORT/health"
    echo "  - Claude Status: http://localhost:$BACKEND_PORT/claude/status"
    echo "  - Claude Info: http://localhost:$BACKEND_PORT/claude/info"
    echo ""
    echo -e "${YELLOW}📝 Logs:${NC}"
    echo "  - Backend: tail -f backend.log"
    echo "  - Frontend: tail -f frontend.log"
    echo ""
    echo -e "${YELLOW}Pressione Ctrl+C para parar o sistema${NC}"
    echo -e "${GREEN}Monitorando serviços... (reinicialização automática ativada)${NC}"
    echo ""
    
    # Monitorar serviços
    monitor_services
}

# Executar
main
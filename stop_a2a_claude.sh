#\!/bin/bash

# Script para parar o A2A-UI com Claude integrado

echo "🛑 Parando A2A-UI + Claude Assistant"
echo "===================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para matar processos em uma porta
kill_port() {
    local port=$1
    local name=$2
    
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "${YELLOW}Parando $name (porta $port)...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✅ $name parado${NC}"
    else
        echo -e "${YELLOW}$name não está rodando na porta $port${NC}"
    fi
}

# Parar Frontend
kill_port 12000 "Frontend"

# Parar Backend
kill_port 8085 "Backend"

# Matar processos Python relacionados
echo -e "${YELLOW}Procurando processos Python relacionados...${NC}"
ps aux | grep -E "(main\.py|backend_server\.py|run_a2a_claude)" | grep -v grep | awk '{print $2}' | while read pid; do
    if [ \! -z "$pid" ]; then
        echo -e "${YELLOW}Matando processo PID: $pid${NC}"
        kill -9 $pid 2>/dev/null
    fi
done

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Sistema A2A-UI + Claude totalmente encerrado\!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Para reiniciar, execute: ./run_a2a_claude.sh${NC}"

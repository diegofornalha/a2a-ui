#!/bin/bash

# Script para parar todos os agentes do sistema PRP + CrewAI

echo "🛑 Parando Sistema PRP + CrewAI"
echo "==============================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Para agentes usando PIDs salvos
if [ -d "logs" ]; then
    for pidfile in logs/*.pid; do
        if [ -f "$pidfile" ]; then
            PID=$(cat $pidfile)
            AGENT=$(basename $pidfile .pid)
            if kill -0 $PID 2>/dev/null; then
                echo -e "${RED}▶ Parando $AGENT (PID: $PID)${NC}"
                kill $PID
            fi
            rm -f $pidfile
        fi
    done
fi

# Para agentes por porta (fallback)
echo -e "\nVerificando portas..."
ports=(8001 8002 8003 8004 8005)
agents=("Orchestrator" "Estrategista" "Criativo Visual" "Copywriter" "Otimizador")

for i in ${!ports[@]}; do
    PID=$(lsof -ti :${ports[$i]})
    if [ ! -z "$PID" ]; then
        echo -e "${RED}▶ Parando ${agents[$i]} na porta ${ports[$i]} (PID: $PID)${NC}"
        kill $PID 2>/dev/null
    fi
done

echo -e "\n${GREEN}✅ Sistema PRP + CrewAI parado${NC}"
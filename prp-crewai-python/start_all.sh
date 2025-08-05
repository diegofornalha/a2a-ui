#!/bin/bash

# Script para iniciar todos os agentes do sistema PRP + CrewAI

echo "🚀 Iniciando Sistema PRP + CrewAI em Python"
echo "========================================="

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar se uma porta está em uso
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${YELLOW}⚠️  Porta $1 já está em uso${NC}"
        return 1
    fi
    return 0
}

# Verifica todas as portas
echo -e "${BLUE}Verificando portas...${NC}"
ports=(8001 8002 8003 8004 8005)
agents=("Orchestrator" "Estrategista" "Criativo Visual" "Copywriter" "Otimizador")

for i in ${!ports[@]}; do
    check_port ${ports[$i]}
    if [ $? -ne 0 ]; then
        echo "Por favor, libere a porta ${ports[$i]} antes de continuar"
        exit 1
    fi
done

echo -e "${GREEN}✅ Todas as portas estão livres${NC}"

# Cria diretório de logs se não existir
mkdir -p logs

# Inicia cada agente em background
echo -e "\n${BLUE}Iniciando agentes...${NC}"

# Orchestrator
echo -e "${GREEN}▶ Iniciando Orchestrator (porta 8001)${NC}"
source .venv/bin/activate && python orchestrator/orchestrator_main.py > logs/orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!
sleep 2

# Estrategista
echo -e "${GREEN}▶ Iniciando Estrategista (porta 8002)${NC}"
source .venv/bin/activate && python agents/estrategista_main.py > logs/estrategista.log 2>&1 &
ESTRATEGISTA_PID=$!
sleep 1

# Criativo Visual
echo -e "${GREEN}▶ Iniciando Criativo Visual (porta 8003)${NC}"
source .venv/bin/activate && python agents/criativo_main.py > logs/criativo.log 2>&1 &
CRIATIVO_PID=$!
sleep 1

# Copywriter
echo -e "${GREEN}▶ Iniciando Copywriter (porta 8004)${NC}"
source .venv/bin/activate && python agents/copywriter_main.py > logs/copywriter.log 2>&1 &
COPYWRITER_PID=$!
sleep 1

# Otimizador
echo -e "${GREEN}▶ Iniciando Otimizador (porta 8005)${NC}"
source .venv/bin/activate && python agents/otimizador_main.py > logs/otimizador.log 2>&1 &
OTIMIZADOR_PID=$!

# Salva PIDs para poder parar depois
echo $ORCHESTRATOR_PID > logs/orchestrator.pid
echo $ESTRATEGISTA_PID > logs/estrategista.pid
echo $CRIATIVO_PID > logs/criativo.pid
echo $COPYWRITER_PID > logs/copywriter.pid
echo $OTIMIZADOR_PID > logs/otimizador.pid

sleep 3

echo -e "\n${GREEN}✅ Sistema PRP + CrewAI iniciado com sucesso!${NC}"
echo -e "\n📡 URLs dos Agentes:"
echo -e "  - Orchestrator:     http://localhost:8001"
echo -e "  - Estrategista:     http://localhost:8002"
echo -e "  - Criativo Visual:  http://localhost:8003"
echo -e "  - Copywriter:       http://localhost:8004"
echo -e "  - Otimizador:       http://localhost:8005"
echo -e "\n📝 Logs disponíveis em: ./logs/"
echo -e "\n🛑 Para parar o sistema, execute: ./stop_all.sh"

# Mantém o script rodando
echo -e "\n${YELLOW}Sistema rodando. Pressione Ctrl+C para parar todos os agentes${NC}"

# Função para cleanup quando Ctrl+C é pressionado
cleanup() {
    echo -e "\n${YELLOW}Parando todos os agentes...${NC}"
    kill $ORCHESTRATOR_PID $ESTRATEGISTA_PID $CRIATIVO_PID $COPYWRITER_PID $OTIMIZADOR_PID 2>/dev/null
    rm -f logs/*.pid
    echo -e "${GREEN}✅ Sistema parado${NC}"
    exit 0
}

# Registra a função de cleanup
trap cleanup INT

# Aguarda indefinidamente
while true; do
    sleep 1
done
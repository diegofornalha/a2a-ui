#!/bin/bash

# Script de instalação do sistema PRP + CrewAI

echo "🚀 Configurando Sistema PRP + CrewAI"
echo "===================================="

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verifica se o uv está instalado
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv não encontrado. Instalando...${NC}"
    pip install uv
fi

# Cria ambiente virtual
echo -e "\n${BLUE}Criando ambiente virtual...${NC}"
uv venv

# Ativa ambiente virtual
echo -e "${BLUE}Ativando ambiente virtual...${NC}"
source .venv/bin/activate

# Instala dependências
echo -e "\n${BLUE}Instalando dependências...${NC}"
uv pip install -e .

# Cria arquivo .env se não existir
if [ ! -f .env ]; then
    echo -e "\n${BLUE}Criando arquivo .env...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Por favor, configure suas API keys em .env${NC}"
fi

# Cria diretórios necessários
echo -e "\n${BLUE}Criando estrutura de diretórios...${NC}"
mkdir -p logs
mkdir -p responses
mkdir -p examples/outputs

# Torna scripts executáveis
chmod +x start_all.sh stop_all.sh setup.sh

echo -e "\n${GREEN}✅ Instalação concluída!${NC}"
echo -e "\nPróximos passos:"
echo -e "1. Configure suas API keys em .env (opcional)"
echo -e "2. Execute: ${GREEN}./start_all.sh${NC} para iniciar o sistema"
echo -e "3. Teste com: ${GREEN}cd examples && python create_campaign.py${NC}"

echo -e "\n${BLUE}Documentação disponível em README.md${NC}"
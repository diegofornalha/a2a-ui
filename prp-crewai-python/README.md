# PRP + CrewAI System - Python

Sistema multi-agente para automação de campanhas de marketing digital usando o protocolo A2A (Agent-to-Agent).

## 🚀 Visão Geral

O sistema PRP + CrewAI coordena 4 agentes especializados para criar e otimizar campanhas de mídia paga:

- **🎯 Orchestrator** (porta 8001): Coordena todos os agentes e gerencia o fluxo de trabalho
- **📊 Estrategista** (porta 8002): Análise de mercado, personas e estratégia
- **🎨 Criativo Visual** (porta 8003): Geração de assets visuais otimizados
- **✍️ Copywriter** (porta 8004): Criação de copy persuasivo
- **⚡ Otimizador** (porta 8005): Análise e otimização de performance

## 📦 Instalação

### 1. Clonar o repositório
```bash
git clone <seu-repositorio>
cd prp-crewai-python
```

### 2. Criar ambiente virtual
```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 3. Instalar dependências
```bash
uv pip install -e .
```

### 4. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

## 🏃‍♂️ Executando o Sistema

### Iniciar todos os agentes
```bash
chmod +x start_all.sh stop_all.sh
./start_all.sh
```

### Parar todos os agentes
```bash
./stop_all.sh
```

### Executar agentes individualmente
```bash
# Terminal 1 - Orchestrator
python orchestrator/orchestrator_main.py

# Terminal 2 - Estrategista
python agents/estrategista_main.py

# Terminal 3 - Criativo Visual
python agents/criativo_main.py

# Terminal 4 - Copywriter
python agents/copywriter_main.py

# Terminal 5 - Otimizador
python agents/otimizador_main.py
```

## 🔗 APIs e Endpoints

### Orchestrator (porta 8001)
- `GET /` - Informações do agente
- `GET /.well-known/agent.json` - Configuração A2A
- `POST /api/campaign/create` - Criar nova campanha
- `GET /api/campaign/{id}/status` - Status da campanha
- `GET /api/agents/status` - Status de todos os agentes

### Agentes Especializados (portas 8002-8005)
- `GET /` - Informações do agente
- `GET /.well-known/agent.json` - Configuração A2A
- `POST /task` - Executar tarefa específica
- `GET /health` - Health check

## 📝 Exemplo de Uso

### Criar uma campanha completa

```python
import httpx
import asyncio

async def create_campaign():
    async with httpx.AsyncClient() as client:
        # Criar campanha via Orchestrator
        response = await client.post(
            "http://localhost:8001/api/campaign/create",
            json={
                "client_name": "Loja Virtual XYZ",
                "business_type": "E-commerce de Moda Feminina",
                "campaign_goal": "Aumentar vendas em 40% no próximo trimestre",
                "target_audience": {
                    "age_range": "25-45",
                    "gender": "female",
                    "interests": ["moda", "compras online", "tendências"],
                    "income_level": "média-alta"
                },
                "budget": 10000.00,
                "currency": "BRL",
                "duration_days": 30,
                "platforms": ["Facebook", "Instagram"]
            }
        )
        
        campaign = response.json()
        print(f"Campanha criada: {campaign['campaign_id']}")
        
        # Verificar status
        status_response = await client.get(
            f"http://localhost:8001/api/campaign/{campaign['campaign_id']}/status"
        )
        
        print(f"Status: {status_response.json()}")

# Executar
asyncio.run(create_campaign())
```

### Usar agente específico diretamente

```python
import httpx
import asyncio

async def analyze_performance():
    async with httpx.AsyncClient() as client:
        # Solicitar análise ao Otimizador
        response = await client.post(
            "http://localhost:8005/task",
            json={
                "task": "analyze_performance",
                "campaign_id": "campaign_001",
                "period": "last_7_days"
            }
        )
        
        analysis = response.json()
        print(f"Análise: {analysis}")

asyncio.run(analyze_performance())
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html

# Testes específicos
pytest tests/test_orchestrator.py
```

## 📊 Monitoramento

### Logs
Todos os logs são salvos em `./logs/`:
- `orchestrator.log`
- `estrategista.log`
- `criativo.log`
- `copywriter.log`
- `otimizador.log`

### Health Check
```bash
# Verificar status de todos os agentes
curl http://localhost:8001/api/agents/status

# Health check individual
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Orchestrator  │ (8001)
│   Coordenação   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ Est. │  │ Cri. │ (8002, 8003)
└───┬──┘  └──┬───┘
    │        │
┌───▼──┐  ┌──▼───┐
│ Copy │  │ Oti. │ (8004, 8005)
└──────┘  └──────┘
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```env
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Configurações do Sistema
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# URLs dos Agentes (se diferente do padrão)
ORCHESTRATOR_URL=http://localhost:8001
ESTRATEGISTA_URL=http://localhost:8002
CRIATIVO_URL=http://localhost:8003
COPYWRITER_URL=http://localhost:8004
OTIMIZADOR_URL=http://localhost:8005
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- Issues: [GitHub Issues](https://github.com/seu-usuario/prp-crewai-python/issues)
- Documentação: [Wiki](https://github.com/seu-usuario/prp-crewai-python/wiki)

---

**PRP + CrewAI** - Automatizando o sucesso em campanhas de marketing digital 🚀
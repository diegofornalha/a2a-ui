# 🤖 A2A MCP - Agent-to-Agent com Claude Code SDK

**IMPORTANTE: Este servidor usa CLAUDE CODE SDK, não Google API!**

## ✨ O que mudou?

- ✅ **SEM Google API Key** - Usa Claude Code Desktop local
- ✅ **SEM custos** - 100% gratuito usando Claude local
- ✅ **Privacidade total** - Dados processados localmente
- ✅ **Análise superior** - Claude entende contexto profundamente

## 🚀 Como Usar com Claude

### 1. Pré-requisitos

```bash
# Claude Code Desktop deve estar instalado
claude --version

# Instalar dependências Python
pip install claude-code-sdk mcp pandas numpy
```

### 2. Iniciar Servidor MCP

#### Opção A: Script Python
```bash
python start_mcp_claude.py
```

#### Opção B: Script Bash
```bash
./start_claude_mcp.sh
```

#### Opção C: Direto com módulo
```bash
python -m a2a_mcp.mcp.server
```

### 3. Configurar Porta (opcional)

```bash
# Porta padrão: 8175
MCP_PORT=9000 python start_mcp_claude.py

# Ou para Node.js A2A (porta 8174)
A2A_PORT=8174 node a2a-server.js
```

## 📊 Servidores e Portas

| Servidor | Porta | Tecnologia | Função |
|----------|-------|------------|--------|
| MCP Claude | 8175 | Python + Claude SDK | Análise semântica de agentes |
| A2A Node | 8174 | Node.js | Protocolo A2A |
| UI Backend | 8080 | FastAPI | Backend da UI |

## 🛠️ Ferramentas Disponíveis

### Com Claude SDK:

1. **find_agent** - Busca semântica usando Claude
2. **analyze_agent_with_claude** - Análise profunda com insights
3. **list_all_agents** - Lista todos os agentes
4. **find_resource** - Busca recursos

## 🏗️ Arquitetura

```
a2a_mcp/
├── mcp/
│   ├── server.py           # Servidor MCP com Claude SDK
│   ├── claude_server.py    # Servidor alternativo Claude
│   └── client.py           # Cliente MCP
├── agents/                 # Agentes A2A
├── common/                 # Utilidades
├── start_mcp_claude.py     # Script Python de inicialização
├── start_claude_mcp.sh     # Script Bash de inicialização
└── README.md              # Esta documentação
```

## 🔧 Configuração no Claude Code

Adicione ao `.claude/settings.json`:

```json
{
  "mcpServers": {
    "a2a-agent-cards": {
      "command": "python",
      "args": ["/caminho/para/start_mcp_claude.py"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      },
      "enabled": true
    }
  }
}
```

## 📝 Exemplos de Uso

### Python
```python
from a2a_mcp.mcp.server import find_agent

# Buscar agente
result = find_agent("preciso de um agente para planejar")
print(result)  # Retorna Planner Agent
```

### CLI
```bash
# Testar servidor
echo '{"method":"tools/list"}' | python start_mcp_claude.py

# Buscar agente
curl -X POST http://localhost:8175/find_agent \
  -H "Content-Type: application/json" \
  -d '{"query": "coding agent"}'
```

## 🎯 Integração A2A

O servidor mantém compatibilidade total com o protocolo A2A:

- **Discovery**: Auto-descoberta de agentes
- **Communication**: Comunicação inter-agentes
- **Delegation**: Delegação de tarefas
- **Multimodal**: Suporte a diferentes tipos de dados

## ⚠️ Troubleshooting

### Claude não encontrado
```bash
# Verificar instalação
which claude

# Adicionar ao PATH
export PATH="$PATH:/Applications/Claude.app/Contents/MacOS"
```

### Servidor não inicia
```bash
# Debug mode
MCP_LOG_LEVEL=debug python start_mcp_claude.py
```

## 🚀 Benefícios do Claude sobre Google

| Feature | Claude SDK | Google API |
|---------|-----------|------------|
| Custo | Grátis | Pago |
| Privacidade | 100% local | Cloud |
| Limite de requisições | Ilimitado | Com quota |
| Velocidade | Rápido (local) | Depende da internet |
| Compreensão | Contextual profunda | Embeddings numéricos |
| Instalação | Claude Desktop | API Key |

---

**Powered by Claude Code SDK - Sem API Keys, Sem Limites! 🚀**
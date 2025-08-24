# Integração Claude Code SDK com Sistema A2A

## 📚 Visão Geral

Este guia demonstra como integrar o **Claude Code SDK** com o sistema **A2A (Agent-to-Agent)** em sua aplicação, permitindo criar soluções poderosas de IA com comunicação entre agentes especializados.

## 🎯 O que é possível fazer?

### Capacidades do Claude Code SDK
- **Acesso programático ao LLM Claude**: Envie prompts e receba respostas estruturadas
- **Automação de código**: Geração, revisão, refatoração e testes automatizados
- **Contexto conversacional**: Mantém histórico para interações multi-turno
- **Integração com ferramentas externas**: Conecta com APIs, MCP e sistemas A2A
- **Saída flexível**: JSON estruturado, streaming, texto formatado

### Integração com A2A
- **Orquestração de agentes**: Coordene múltiplos agentes especializados
- **Pipeline de processamento**: Crie fluxos complexos de trabalho
- **Memória compartilhada**: Agentes compartilham contexto e aprendizados
- **Escalabilidade**: Execute tarefas em paralelo com múltiplos agentes

## 🚀 Instalação

### Python
```bash
pip install claude-code-sdk anthropic-ai
```

### Node.js/TypeScript
```bash
npm install @anthropic-ai/claude-code axios
```

## 💻 Exemplos de Implementação

### 1. Backend Python (Flask + Claude SDK + A2A)

```python
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions
import json
import os

app = Flask(__name__)
CORS(app)

class A2AIntegration:
    def __init__(self):
        self.agents = {}
        self.memory = {}
        
    async def create_agent(self, agent_type, task):
        """Cria um agente especializado via Claude SDK"""
        prompt = f"""
        Você é um agente {agent_type} em um sistema A2A.
        Tarefa: {task}
        
        Use o comando MCP para coordenar com outros agentes:
        - mcp__claude-flow__agent_spawn para criar novos agentes
        - mcp__claude-flow__memory_usage para compartilhar memória
        - mcp__claude-flow__task_orchestrate para coordenar tarefas
        """
        
        options = ClaudeCodeOptions(
            tools=["mcp", "file_operations", "bash"],
            max_tokens=4000
        )
        
        responses = []
        async for message in query(prompt=prompt, options=options):
            responses.append(message.content)
            
        return {
            "agent_type": agent_type,
            "task": task,
            "responses": responses
        }
    
    async def orchestrate_agents(self, main_task):
        """Orquestra múltiplos agentes para uma tarefa complexa"""
        # Define agentes necessários baseado na tarefa
        agent_config = self.analyze_task(main_task)
        
        # Cria agentes em paralelo
        tasks = []
        for agent in agent_config:
            tasks.append(self.create_agent(agent["type"], agent["task"]))
        
        results = await asyncio.gather(*tasks)
        
        # Consolida resultados
        return self.consolidate_results(results)
    
    def analyze_task(self, task):
        """Analisa tarefa e define agentes necessários"""
        # Lógica para determinar quais agentes criar
        if "API" in task:
            return [
                {"type": "system-architect", "task": "Design da arquitetura"},
                {"type": "backend-dev", "task": "Implementar endpoints"},
                {"type": "tester", "task": "Criar testes automatizados"},
                {"type": "api-docs", "task": "Documentar API"}
            ]
        return [{"type": "general", "task": task}]
    
    def consolidate_results(self, results):
        """Consolida resultados de múltiplos agentes"""
        consolidated = {
            "agents": len(results),
            "outputs": results,
            "summary": self.generate_summary(results)
        }
        return consolidated
    
    def generate_summary(self, results):
        """Gera resumo dos resultados"""
        return f"Processado por {len(results)} agentes com sucesso"

a2a = A2AIntegration()

@app.route('/api/process', methods=['POST'])
async def process_task():
    """Endpoint para processar tarefas com Claude + A2A"""
    data = request.json
    task = data.get('task')
    
    if not task:
        return jsonify({"error": "Task is required"}), 400
    
    try:
        result = await a2a.orchestrate_agents(task)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/create', methods=['POST'])
async def create_single_agent():
    """Cria um agente específico"""
    data = request.json
    agent_type = data.get('type', 'general')
    task = data.get('task')
    
    try:
        result = await a2a.create_agent(agent_type, task)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory', methods=['GET', 'POST'])
def manage_memory():
    """Gerencia memória compartilhada entre agentes"""
    if request.method == 'POST':
        data = request.json
        key = data.get('key')
        value = data.get('value')
        a2a.memory[key] = value
        return jsonify({"status": "stored"})
    else:
        return jsonify(a2a.memory)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### 2. Frontend React consumindo o SDK

```jsx
// ClaudeA2AInterface.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ClaudeA2AInterface = () => {
  const [task, setTask] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [agents, setAgents] = useState([]);
  const [memory, setMemory] = useState({});

  // Função para processar tarefa com múltiplos agentes
  const processTask = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/process', {
        task: task
      });
      setResults(response.data);
      updateAgentsList(response.data.outputs);
    } catch (error) {
      console.error('Erro ao processar tarefa:', error);
    } finally {
      setLoading(false);
    }
  };

  // Atualiza lista de agentes ativos
  const updateAgentsList = (outputs) => {
    const activeAgents = outputs.map(output => ({
      type: output.agent_type,
      status: 'completed',
      task: output.task
    }));
    setAgents(activeAgents);
  };

  // Busca memória compartilhada
  const fetchMemory = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/memory');
      setMemory(response.data);
    } catch (error) {
      console.error('Erro ao buscar memória:', error);
    }
  };

  useEffect(() => {
    // Atualiza memória periodicamente
    const interval = setInterval(fetchMemory, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="claude-a2a-interface">
      <h1>🤖 Claude Code + A2A Integration</h1>
      
      <div className="task-input">
        <textarea
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="Descreva sua tarefa complexa..."
          rows={4}
        />
        <button onClick={processTask} disabled={loading}>
          {loading ? 'Processando...' : 'Executar com A2A'}
        </button>
      </div>

      <div className="agents-panel">
        <h2>🐝 Agentes Ativos</h2>
        <div className="agents-grid">
          {agents.map((agent, idx) => (
            <div key={idx} className="agent-card">
              <h3>{agent.type}</h3>
              <p>{agent.task}</p>
              <span className={`status ${agent.status}`}>
                {agent.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {results && (
        <div className="results-panel">
          <h2>📊 Resultados</h2>
          <div className="summary">
            <p>Total de agentes: {results.agents}</p>
            <p>{results.summary}</p>
          </div>
          <div className="outputs">
            {results.outputs.map((output, idx) => (
              <div key={idx} className="output-card">
                <h4>Agente: {output.agent_type}</h4>
                <pre>{JSON.stringify(output.responses, null, 2)}</pre>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="memory-panel">
        <h2>🧠 Memória Compartilhada</h2>
        <pre>{JSON.stringify(memory, null, 2)}</pre>
      </div>
    </div>
  );
};

export default ClaudeA2AInterface;
```

### 3. Script de Configuração Automatizada

```bash
#!/bin/bash
# setup_claude_a2a.sh

echo "🚀 Configurando integração Claude Code SDK + A2A"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instalando..."
    brew install python3
fi

# Cria ambiente virtual
echo "📦 Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instala dependências Python
echo "📚 Instalando dependências Python..."
pip install claude-code-sdk flask flask-cors asyncio

# Configura variáveis de ambiente
echo "🔐 Configurando variáveis de ambiente..."
cat > .env << EOF
CLAUDE_API_KEY=your_api_key_here
A2A_ENABLED=true
MAX_AGENTS=10
MEMORY_PERSISTENCE=true
EOF

# Cria estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p src/{backend,frontend,agents,memory}
mkdir -p tests/{unit,integration}
mkdir -p docs

# Inicia servidor de desenvolvimento
echo "🎯 Iniciando servidor de desenvolvimento..."
python app.py &

echo "✅ Configuração concluída! Acesse http://localhost:5000"
```

## 🔧 Configuração Avançada

### Opções do Claude Code SDK

```python
options = ClaudeCodeOptions(
    # Ferramentas disponíveis
    tools=["mcp", "file_operations", "bash", "git"],
    
    # Limites
    max_tokens=8000,
    temperature=0.7,
    
    # Segurança
    safe_mode=True,
    allowed_commands=["npm", "python", "git"],
    
    # A2A específico
    enable_a2a=True,
    max_agents=10,
    agent_timeout=300,  # segundos
    
    # Memória
    persist_memory=True,
    memory_path="./a2a_memory"
)
```

## 🛡️ Segurança e Boas Práticas

### 1. Autenticação e Autorização

```python
from functools import wraps
import jwt

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/secure/process', methods=['POST'])
@require_auth
async def secure_process():
    # Processamento seguro
    pass
```

### 2. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/process', methods=['POST'])
@limiter.limit("10 per minute")
async def process_task():
    # Processamento com rate limiting
    pass
```

### 3. Validação de Entrada

```python
from marshmallow import Schema, fields, validate

class TaskSchema(Schema):
    task = fields.Str(required=True, validate=validate.Length(min=10, max=1000))
    agent_type = fields.Str(validate=validate.OneOf([
        'system-architect', 'coder', 'tester', 'reviewer'
    ]))
    priority = fields.Int(validate=validate.Range(min=1, max=10))

@app.route('/api/process', methods=['POST'])
async def process_task():
    schema = TaskSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    # Processa tarefa validada
```

## 🚀 Pipeline CI/CD

### GitHub Actions Workflow

```yaml
# .github/workflows/claude-a2a-deploy.yml
name: Deploy Claude A2A Integration

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run tests
        run: |
          pytest tests/ --verbose
      
      - name: Test A2A Integration
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        run: |
          python -m pytest tests/integration/test_a2a.py
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to Production
        run: |
          # Deploy script aqui
          echo "Deploying Claude A2A Integration"
```

## 📊 Monitoramento e Métricas

```python
# monitoring.py
import time
from prometheus_client import Counter, Histogram, Gauge

# Métricas
agent_requests = Counter('a2a_agent_requests_total', 
                         'Total agent requests',
                         ['agent_type'])

task_duration = Histogram('a2a_task_duration_seconds',
                         'Task processing duration')

active_agents = Gauge('a2a_active_agents',
                     'Number of active agents')

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        start_time = time.time()
        
        def custom_start_response(status, headers):
            duration = time.time() - start_time
            task_duration.observe(duration)
            return start_response(status, headers)
        
        return self.app(environ, custom_start_response)
```

## 🎯 Casos de Uso Práticos

### 1. Bot de Code Review Automatizado

```python
async def automated_code_review(pr_url):
    """Revisa PR automaticamente com múltiplos agentes"""
    agents = [
        ("code-analyzer", "Analisar qualidade do código"),
        ("security-manager", "Verificar vulnerabilidades"),
        ("performance-benchmarker", "Avaliar performance"),
        ("api-docs", "Verificar documentação")
    ]
    
    results = []
    for agent_type, task in agents:
        result = await a2a.create_agent(agent_type, f"{task} para {pr_url}")
        results.append(result)
    
    return consolidate_review_results(results)
```

### 2. Gerador de Aplicação Full-Stack

```python
async def generate_fullstack_app(requirements):
    """Gera aplicação completa com arquitetura A2A"""
    
    # Fase 1: Arquitetura
    architect = await a2a.create_agent(
        "system-architect",
        f"Design arquitetura para: {requirements}"
    )
    
    # Fase 2: Implementação paralela
    tasks = [
        a2a.create_agent("backend-dev", "Implementar API REST"),
        a2a.create_agent("mobile-dev", "Criar app React Native"),
        a2a.create_agent("ml-developer", "Implementar modelo ML"),
        a2a.create_agent("cicd-engineer", "Configurar pipeline")
    ]
    
    implementations = await asyncio.gather(*tasks)
    
    # Fase 3: Validação
    validator = await a2a.create_agent(
        "production-validator",
        "Validar implementação completa"
    )
    
    return {
        "architecture": architect,
        "implementation": implementations,
        "validation": validator
    }
```

## 📚 Recursos Adicionais

- [Documentação Claude Code SDK](https://docs.anthropic.com/claude-code/sdk)
- [Claude Flow GitHub](https://github.com/ruvnet/claude-flow)
- [Exemplos A2A](https://github.com/ruvnet/claude-flow/examples)
- [API Reference](https://docs.anthropic.com/api)

## 🤝 Suporte

- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Discord: [Community Server](https://discord.gg/claude-dev)
- Email: support@your-domain.com

---

**Desenvolvido com ❤️ usando Claude Code SDK + A2A**
# A2A UI - Interface de Gerenciamento de Agentes

Uma interface de usuário moderna para gerenciamento de agentes A2A (Agent-to-Agent), permitindo descoberta, registro e controle de agentes remotos e locais.

## 🚀 Características

- **Interface Web Moderna**: Interface responsiva e intuitiva para gerenciamento de agentes
- **Descoberta de Agentes**: Sistema automático de descoberta de agentes remotos
- **Gerenciamento Local**: Controle completo de agentes locais
- **Monitoramento em Tempo Real**: Status e logs em tempo real dos agentes
- **Multi-idioma**: Suporte para português, inglês e espanhol
- **Arquitetura Modular**: Componentes reutilizáveis e extensíveis

## 🛠️ Tecnologias

- **Frontend**: Next.js, React, TypeScript
- **Backend**: Python, FastAPI
- **UI Components**: Custom components com design system próprio
- **Estado**: Gerenciamento de estado centralizado
- **Comunicação**: WebSocket para atualizações em tempo real

## 📦 Instalação

### Pré-requisitos

- Node.js 18+ 
- Python 3.8+
- Git

### Configuração

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/a2a-ui.git
cd a2a-ui
```

2. **Instale as dependências Python**
```bash
pip install -r requirements.txt
```

3. **Instale as dependências Node.js**
```bash
npm install
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## 🚀 Execução

### Desenvolvimento

1. **Inicie o servidor backend**
```bash
python main.py
```

2. **Inicie o servidor frontend**
```bash
npm run dev
```

3. **Acesse a aplicação**
```
http://localhost:12000
```

### Produção

```bash
npm run build
npm start
```

## 📁 Estrutura do Projeto

```
A2A-UI/
├── components/          # Componentes React reutilizáveis
├── pages/              # Páginas da aplicação
├── service/            # Serviços e lógica de negócio
├── state/              # Gerenciamento de estado
├── utils/              # Utilitários e helpers
├── styles/             # Estilos e temas
├── scripts/            # Scripts de automação
├── tests/              # Testes automatizados
└── .well-known/        # Configurações de agente
```

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Servidor
PORT=12000
NODE_ENV=development

# Agentes
AGENT_DISCOVERY_ENABLED=true
AGENT_TIMEOUT=30000

# Logs
LOG_LEVEL=info
```

### Configuração de Agentes

O arquivo `.well-known/agent.json` define as capacidades e configurações do agente:

```json
{
  "name": "A2A UI Agent",
  "description": "Interface de usuário para gerenciamento de agentes A2A",
  "version": "1.0.0",
  "protocolVersion": "0.2.5",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "stateTransitionHistory": false
  }
}
```

## 🧪 Testes

```bash
# Testes unitários
npm test

# Testes de integração
npm run test:integration

# Cobertura de testes
npm run test:coverage
```

## 📚 Documentação

- [Guia de Desenvolvimento](./docs/DEVELOPMENT.md)
- [API Reference](./docs/API.md)
- [Arquitetura](./docs/ARCHITECTURE.md)
- [Deploy](./docs/DEPLOY.md)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/a2a-ui/issues)
- **Documentação**: [Wiki](https://github.com/seu-usuario/a2a-ui/wiki)
- **Email**: suporte@a2a-ui.com

## 🗺️ Roadmap

- [ ] Suporte a múltiplos protocolos de agente
- [ ] Interface de configuração visual
- [ ] Sistema de plugins
- [ ] Integração com CI/CD
- [ ] Métricas e analytics
- [ ] Modo offline

## 📊 Status do Projeto

![Build Status](https://github.com/seu-usuario/a2a-ui/workflows/CI/badge.svg)
![Test Coverage](https://codecov.io/gh/seu-usuario/a2a-ui/branch/main/graph/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

**A2A UI** - Simplificando o gerenciamento de agentes inteligentes 🚀
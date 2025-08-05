#!/bin/bash
# Script para criar package.json do otimizador

cat > agents/otimizador/package.json << 'EOF'
{
  "name": "prp-crewai-otimizador",
  "version": "1.0.0",
  "description": "Agente Otimizador de Performance para PRP + CrewAI",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {}
}
EOF

echo "✅ package.json criado para o agente otimizador"
cat agents/otimizador/package.json
#!/bin/bash

# ============================================================================
# Script para Prevenir Inicialização Automática de Processos
# ============================================================================

echo "🔒 Configurando prevenção de inicialização automática..."

# 1. Criar arquivo de flag para desabilitar auto-start
echo "📋 Criando flag de desabilitação..."
mkdir -p ../run
echo "$(date): Auto-start desabilitado pelo usuário" > ../run/auto_start_disabled.flag

# 2. Modificar permissões do agent_manager para prevenir execução
echo "📋 Modificando permissões do agent_manager..."
if [ -f ../agent_manager.sh ]; then
    chmod -x ../agent_manager.sh
    echo "✅ Permissões do agent_manager.sh removidas"
else
    echo "⚠️  agent_manager.sh não encontrado"
fi

# 3. Criar script de verificação que impede auto-start
cat > ../run/check_auto_start.sh << 'EOF'
#!/bin/bash
# Script para verificar se auto-start está desabilitado

if [ -f "auto_start_disabled.flag" ]; then
    echo "🚫 Auto-start está desabilitado. Para reabilitar, execute: chmod +x ../agent_manager.sh"
    exit 1
fi
EOF

chmod +x ../run/check_auto_start.sh

# 4. Criar script de reabilitação
cat > ../run/reable_auto_start.sh << 'EOF'
#!/bin/bash
# Script para reabilitar auto-start

echo "🔓 Reabilitando auto-start..."

# Remover flag de desabilitação
rm -f auto_start_disabled.flag

# Restaurar permissões
chmod +x ../agent_manager.sh

echo "✅ Auto-start reabilitado!"
echo "💡 Para iniciar manualmente: ../agent_manager.sh start all"
EOF

chmod +x ../run/reable_auto_start.sh

# 5. Criar documentação
cat > ../run/AUTO_START_CONTROL.md << 'EOF'
# Controle de Inicialização Automática

## Status Atual
- ✅ Auto-start desabilitado
- ✅ Porta 12000 livre
- ✅ Porta 8085 livre

## Comandos Úteis

### Para iniciar manualmente:
```bash
cd ui
uv run main.py
```

### Para reabilitar auto-start:
```bash
cd run
./reable_auto_start.sh
```

### Para verificar status:
```bash
lsof -i :12000
lsof -i :8085
ps aux | grep agent_manager
```

## Arquivos de Controle
- `auto_start_disabled.flag` - Flag de desabilitação
- `check_auto_start.sh` - Script de verificação
- `reable_auto_start.sh` - Script de reabilitação

## Data de Desabilitação
EOF

echo "$(date)" >> ../run/AUTO_START_CONTROL.md

echo ""
echo "✅ Prevenção de auto-start configurada!"
echo ""
echo "📋 Para iniciar manualmente:"
echo "   cd ui && uv run main.py"
echo ""
echo "📋 Para reabilitar auto-start:"
echo "   cd run && ./reable_auto_start.sh"
echo ""
echo "📋 Para verificar status:"
echo "   lsof -i :12000"
echo "   lsof -i :8085" 
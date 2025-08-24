#!/bin/bash
# Script para instalar/desinstalar o serviço Marvin no macOS usando launchd

MARVIN_DIR="/Users/agents/Desktop/claude-20x/agents/marvin"
PLIST_FILE="$MARVIN_DIR/com.marvin.agent.plist"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
LAUNCHD_PLIST="$LAUNCHD_DIR/com.marvin.agent.plist"

case "$1" in
    install)
        echo "📦 Instalando serviço Marvin..."
        
        # Criar diretório se não existir
        mkdir -p "$LAUNCHD_DIR"
        mkdir -p "$MARVIN_DIR/logs"
        
        # Copiar arquivo plist
        cp "$PLIST_FILE" "$LAUNCHD_PLIST"
        
        # Carregar o serviço
        launchctl load "$LAUNCHD_PLIST"
        
        echo "✅ Serviço Marvin instalado e iniciado"
        echo "   O Marvin agora iniciará automaticamente no login"
        ;;
        
    uninstall)
        echo "🗑️  Removendo serviço Marvin..."
        
        # Descarregar o serviço
        launchctl unload "$LAUNCHD_PLIST" 2>/dev/null || true
        
        # Remover arquivo plist
        rm -f "$LAUNCHD_PLIST"
        
        echo "✅ Serviço Marvin removido"
        ;;
        
    start)
        echo "🚀 Iniciando serviço Marvin..."
        launchctl start com.marvin.agent
        ;;
        
    stop)
        echo "🛑 Parando serviço Marvin..."
        launchctl stop com.marvin.agent
        ;;
        
    restart)
        echo "🔄 Reiniciando serviço Marvin..."
        launchctl stop com.marvin.agent
        sleep 2
        launchctl start com.marvin.agent
        ;;
        
    status)
        echo "📊 Status do serviço Marvin:"
        if launchctl list | grep -q com.marvin.agent; then
            echo "✅ Serviço carregado"
            launchctl list com.marvin.agent
        else
            echo "❌ Serviço não carregado"
        fi
        
        # Verificar se o processo está rodando
        if lsof -i :10030 > /dev/null 2>&1; then
            echo "✅ Marvin está rodando na porta 10030"
        else
            echo "❌ Marvin não está rodando na porta 10030"
        fi
        ;;
        
    logs)
        echo "📋 Logs do serviço Marvin:"
        echo "--- stdout ---"
        tail -n 20 "$MARVIN_DIR/logs/launchd_stdout.log" 2>/dev/null || echo "Nenhum log stdout"
        echo "--- stderr ---"
        tail -n 20 "$MARVIN_DIR/logs/launchd_stderr.log" 2>/dev/null || echo "Nenhum log stderr"
        echo "--- daemon ---"
        tail -n 20 "$MARVIN_DIR/logs/marvin_daemon.log" 2>/dev/null || echo "Nenhum log daemon"
        ;;
        
    *)
        echo "Uso: $0 {install|uninstall|start|stop|restart|status|logs}"
        echo ""
        echo "Comandos:"
        echo "  install   - Instala o serviço (auto-start no login)"
        echo "  uninstall - Remove o serviço"
        echo "  start     - Inicia o serviço"
        echo "  stop      - Para o serviço"
        echo "  restart   - Reinicia o serviço"
        echo "  status    - Mostra o status do serviço"
        echo "  logs      - Mostra os logs do serviço"
        exit 1
        ;;
esac
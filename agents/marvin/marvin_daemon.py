#!/usr/bin/env python3
"""
Daemon para manter o Marvin Agent sempre ativo
Monitora o processo e reinicia automaticamente se necessário
"""

import os
import sys
import time
import signal
import logging
import subprocess
import socket
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

class MarvinDaemon:
    def __init__(self):
        self.marvin_dir = Path(__file__).parent
        
        # Carregar variáveis de ambiente do arquivo .env
        env_file = self.marvin_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            
        self.log_dir = self.marvin_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        self.pid_file = self.marvin_dir / "marvin.pid"
        self.daemon_pid_file = self.marvin_dir / "daemon.pid"
        self.log_file = self.log_dir / "marvin_daemon.log"
        
        self.setup_logging()
        self.marvin_process = None
        self.running = False
        
    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MarvinDaemon')
        
    def is_port_in_use(self, port=10030):
        """Verifica se a porta está em uso"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
            
    def find_marvin_process(self):
        """Encontra o processo do Marvin"""
        try:
            # Usar lsof para verificar se a porta está sendo usada
            result = subprocess.run(['lsof', '-i', ':10030'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Header + pelo menos uma linha de processo
                    # Extrair PID da segunda linha
                    fields = lines[1].split()
                    if len(fields) >= 2:
                        pid = fields[1]
                        return {'pid': int(pid)}
        except:
            pass
        return None
        
    def start_marvin(self):
        """Inicia o processo do Marvin"""
        try:
            self.logger.info("🚀 Iniciando processo Marvin...")
            
            # Usar uv para executar com as dependências corretas
            ui_venv_python = "uv"
            
            # Comando para iniciar o Marvin
            cmd = [
                ui_venv_python,
                "run",
                "python",
                str(self.marvin_dir / "server.py")
            ]
            
            # Configurar environment
            env = os.environ.copy()
            env['PYTHONPATH'] = '/Users/agents/Desktop/claude-20x'
            
            # Iniciar o processo
            self.marvin_process = subprocess.Popen(
                cmd,
                cwd=self.marvin_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # Salvar PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.marvin_process.pid))
                
            self.logger.info(f"✅ Marvin iniciado com PID: {self.marvin_process.pid}")
            
            # Aguardar um pouco para verificar se iniciou corretamente
            time.sleep(3)
            
            if self.marvin_process.poll() is None:
                self.logger.info("✅ Marvin está rodando normalmente")
                return True
            else:
                self.logger.error("❌ Marvin falhou ao iniciar")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar Marvin: {e}")
            return False
            
    def stop_marvin(self):
        """Para o processo do Marvin"""
        try:
            # Tentar encontrar o processo
            marvin_proc = self.find_marvin_process()
            if marvin_proc:
                pid = marvin_proc['pid']
                self.logger.info(f"🛑 Parando processo Marvin (PID: {pid})")
                
                try:
                    # Enviar SIGTERM
                    os.kill(pid, signal.SIGTERM)
                    
                    # Aguardar terminar graciosamente
                    for _ in range(10):
                        try:
                            os.kill(pid, 0)  # Verifica se processo ainda existe
                            time.sleep(1)
                        except ProcessLookupError:
                            break  # Processo terminou
                    
                    # Forçar se necessário
                    try:
                        os.kill(pid, 0)  # Verifica se ainda existe
                        os.kill(pid, signal.SIGKILL)  # Força terminar
                    except ProcessLookupError:
                        pass  # Processo já terminou
                except ProcessLookupError:
                    pass  # Processo já não existe
                    
                self.logger.info("✅ Marvin parado")
                
            # Limpar arquivo PID
            if self.pid_file.exists():
                self.pid_file.unlink()
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao parar Marvin: {e}")
            
    def monitor_marvin(self):
        """Monitora o processo do Marvin e reinicia se necessário"""
        self.logger.info("👁️  Iniciando monitoramento do Marvin...")
        
        while self.running:
            try:
                # Verificar se o processo está rodando
                marvin_proc = self.find_marvin_process()
                port_in_use = self.is_port_in_use(10030)
                
                if not marvin_proc or not port_in_use:
                    self.logger.warning("⚠️  Marvin não está rodando, reiniciando...")
                    self.stop_marvin()  # Limpar qualquer processo morto
                    time.sleep(2)
                    self.start_marvin()
                else:
                    self.logger.debug(f"✅ Marvin rodando (PID: {marvin_proc['pid']})")
                    
                # Aguardar antes da próxima verificação
                time.sleep(30)  # Verificar a cada 30 segundos
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(10)
                
    def start_daemon(self):
        """Inicia o daemon"""
        self.logger.info("🎯 Iniciando Marvin Daemon...")
        
        # Salvar PID do daemon
        with open(self.daemon_pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.running = True
        
        # Iniciar Marvin se não estiver rodando
        if not self.find_marvin_process():
            self.start_marvin()
            
        # Iniciar monitoramento
        self.monitor_marvin()
        
    def stop_daemon(self):
        """Para o daemon"""
        self.logger.info("🛑 Parando Marvin Daemon...")
        self.running = False
        self.stop_marvin()
        
        # Limpar arquivo PID do daemon
        if self.daemon_pid_file.exists():
            self.daemon_pid_file.unlink()
            
        self.logger.info("✅ Daemon parado")
        
    def signal_handler(self, signum, frame):
        """Handler para sinais do sistema"""
        self.logger.info(f"📨 Recebido sinal {signum}")
        self.stop_daemon()
        sys.exit(0)
        
    def status(self):
        """Mostra o status do Marvin e do daemon"""
        marvin_proc = self.find_marvin_process()
        port_in_use = self.is_port_in_use(10030)
        daemon_running = self.daemon_pid_file.exists()
        
        print("📊 Status do Marvin:")
        print(f"  Processo Marvin: {'✅ Rodando' if marvin_proc else '❌ Parado'}")
        if marvin_proc:
            print(f"  PID: {marvin_proc['pid']}")
        print(f"  Porta 10030: {'✅ Em uso' if port_in_use else '❌ Livre'}")
        print(f"  Daemon: {'✅ Rodando' if daemon_running else '❌ Parado'}")
        
        if daemon_running:
            try:
                with open(self.daemon_pid_file, 'r') as f:
                    daemon_pid = int(f.read().strip())
                print(f"  Daemon PID: {daemon_pid}")
            except:
                pass

def main():
    daemon = MarvinDaemon()
    
    if len(sys.argv) < 2:
        print("Uso: python marvin_daemon.py [start|stop|restart|status]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "start":
        daemon.start_daemon()
    elif command == "stop":
        daemon.stop_daemon()
    elif command == "restart":
        daemon.stop_daemon()
        time.sleep(2)
        daemon.start_daemon()
    elif command == "status":
        daemon.status()
    else:
        print("Comando inválido. Use: start|stop|restart|status")
        sys.exit(1)

if __name__ == "__main__":
    main()
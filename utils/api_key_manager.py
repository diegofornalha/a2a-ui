import os
import json
from pathlib import Path


class ApiKeyManager:
    """Gerencia o armazenamento e recuperação da Google API Key"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.a2a-ui'
        self.config_file = self.config_dir / 'config.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Garante que o diretório de configuração existe"""
        self.config_dir.mkdir(exist_ok=True)
    
    def save_api_key(self, api_key: str) -> bool:
        """Salva a API key no arquivo de configuração"""
        try:
            config = self._load_config()
            config['google_api_key'] = api_key
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"API key salva em: {self.config_file}")
            return True
        except Exception as e:
            print(f"Erro ao salvar API key: {e}")
            return False
    
    def load_api_key(self) -> str | None:
        """Carrega a API key do arquivo de configuração"""
        try:
            config = self._load_config()
            api_key = config.get('google_api_key')
            
            if api_key:
                # Define a variável de ambiente
                os.environ['GOOGLE_API_KEY'] = api_key
                print("API key carregada do arquivo de configuração")
            
            return api_key
        except Exception as e:
            print(f"Erro ao carregar API key: {e}")
            return None
    
    def _load_config(self) -> dict:
        """Carrega o arquivo de configuração ou retorna um dict vazio"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def get_api_key(self) -> str | None:
        """Obtém a API key da variável de ambiente ou do arquivo"""
        # Primeiro verifica a variável de ambiente
        api_key = os.environ.get('GOOGLE_API_KEY')
        
        # Se não encontrar, tenta carregar do arquivo
        if not api_key:
            api_key = self.load_api_key()
        
        return api_key
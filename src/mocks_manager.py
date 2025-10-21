import re
import random
import logging
from typing import Dict, Any, List, Optional, Union
from src.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MocksManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        # Fallback em memória
        self.memory_mocks: Dict[str, Dict[str, Any]] = {}
        
        # Carrega mocks do banco para memória se conectado
        if self.db_manager.is_connected():
            self._load_mocks_from_db()
        
        logger.info(f"MocksManager inicializado - Banco conectado: {self.db_manager.is_connected()}")
    
    def _load_mocks_from_db(self):
        """Carrega todos os mocks do banco para a memória."""
        try:
            db_mocks = self.db_manager.get_all_mocks()
            for mock in db_mocks:
                mock_id = mock['id']
                self.memory_mocks[mock_id] = {
                    'uri': mock['uri'],
                    'http_method': mock['http_method'],
                    'status_code': mock['status_code'],
                    'response': mock['response'],
                    'uri_pattern': re.compile(f"^{mock['uri_pattern']}$")
                }
            logger.info(f"Carregados {len(db_mocks)} mocks do banco de dados")
        except Exception as e:
            logger.error(f"Erro ao carregar mocks do banco: {e}")
    
    def generate_id(self) -> str:
        """Gera um ID único de 6 dígitos para cada mock."""
        while True:
            mock_id = f"{random.randint(0, 999999):06}"
            if not self.mock_exists(mock_id):
                return mock_id
    
    @staticmethod
    def compile_uri_pattern_static(uri: str) -> str:
        """Converte URI com parâmetros dinâmicos em regex (string)."""
        return re.sub(r":(\w+)", r"(?P<\1>[^/]+)", uri)

    def compile_uri_pattern(self, uri: str) -> str:
        return MocksManager.compile_uri_pattern_static(uri)
    
    def create_mock(self, uri: str, http_method: str, status_code: int, response: Dict[str, Any]) -> str:
        """Cria ou atualiza mock por uri + http_method. Se banco estiver conectado, só persiste no banco."""
        if self.db_manager.is_connected():
            # Busca mock existente no banco
            db_mocks = self.db_manager.get_all_mocks()
            for mock in db_mocks:
                if mock['uri'] == uri and mock['http_method'] == http_method:
                    self.db_manager.update_mock(mock['id'], status_code, response)
                    return mock['id']
            # Se não existe, cria novo
            mock_id = self.generate_id()
            uri_pattern_str = self.compile_uri_pattern(uri)
            self.db_manager.create_mock(mock_id, uri, http_method, status_code, response, uri_pattern_str)
            return mock_id
        else:
            # Busca mock existente na memória
            for mock_id, mock_data in self.memory_mocks.items():
                if mock_data['uri'] == uri and mock_data['http_method'] == http_method:
                    self.update_mock(mock_id, status_code, response)
                    return mock_id
            # Se não existe, cria novo na memória
            mock_id = self.generate_id()
            uri_pattern_str = self.compile_uri_pattern(uri)
            uri_pattern_compiled = re.compile(f"^{uri_pattern_str}$")
            self.memory_mocks[mock_id] = {
                'uri': uri,
                'http_method': http_method,
                'status_code': status_code,
                'response': response,
                'uri_pattern': uri_pattern_compiled
            }
            return mock_id
    
    def get_mock(self, mock_id: str) -> Optional[Dict[str, Any]]:
        """Recupera um mock por ID. Se banco estiver conectado, só lê do banco."""
        if self.db_manager.is_connected():
            db_mock = self.db_manager.get_mock(mock_id)
            if db_mock:
                return {
                    'uri': db_mock['uri'],
                    'http_method': db_mock['http_method'],
                    'status_code': db_mock['status_code'],
                    'response': db_mock['response']
                }
            return None
        else:
            if mock_id in self.memory_mocks:
                mock_data = self.memory_mocks[mock_id].copy()
                mock_data.pop('uri_pattern', None)
                return mock_data
            return None
    
    def get_all_mocks(self) -> List[Dict[str, Any]]:
        """Recupera todos os mocks. Se banco estiver conectado, só lê do banco."""
        if self.db_manager.is_connected():
            try:
                db_mocks = self.db_manager.get_all_mocks()
                return [
                    {
                        'id': mock['id'],
                        'uri': mock['uri'],
                        'http_method': mock['http_method'],
                        'status_code': mock['status_code']
                    }
                    for mock in db_mocks
                ]
            except Exception as e:
                logger.error(f"Erro ao recuperar mocks do banco: {e}")
                return []
        else:
            return [
                {
                    'id': mock_id,
                    'uri': mock_data['uri'],
                    'http_method': mock_data['http_method'],
                    'status_code': mock_data['status_code']
                }
                for mock_id, mock_data in self.memory_mocks.items()
            ]
    
    def update_mock(self, mock_id: str, status_code: Optional[int] = None, 
                   response: Optional[Dict[str, Any]] = None,
                   uri: Optional[str] = None,
                   http_method: Optional[str] = None) -> bool:
        """Atualiza um mock existente, incluindo uri e método. Se banco estiver conectado, só atualiza no banco."""
        if not self.mock_exists(mock_id):
            return False
        success = True
        if self.db_manager.is_connected():
            if not self.db_manager.update_mock(mock_id, status_code, response, uri, http_method):
                logger.warning(f"Falha ao atualizar mock {mock_id} no banco")
                success = False
        else:
            if mock_id in self.memory_mocks:
                if status_code is not None:
                    self.memory_mocks[mock_id]['status_code'] = status_code
                if response is not None:
                    self.memory_mocks[mock_id]['response'] = response
                if uri is not None:
                    self.memory_mocks[mock_id]['uri'] = uri
                    self.memory_mocks[mock_id]['uri_pattern'] = re.compile(f"^{self.compile_uri_pattern(uri)}$")
                if http_method is not None:
                    self.memory_mocks[mock_id]['http_method'] = http_method
        return success
    
    def delete_mock(self, mock_id: str) -> bool:
        """Remove um mock. Se banco estiver conectado, só remove do banco."""
        if not self.mock_exists(mock_id):
            return False
        if self.db_manager.is_connected():
            if not self.db_manager.delete_mock(mock_id):
                logger.warning(f"Falha ao remover mock {mock_id} do banco")
                return False
            return True
        else:
            self.memory_mocks.pop(mock_id, None)
            return True
    
    def delete_all_mocks(self) -> bool:
        """Remove todos os mocks. Se banco estiver conectado, só remove do banco."""
        if self.db_manager.is_connected():
            if not self.db_manager.delete_all_mocks():
                logger.warning("Falha ao limpar mocks do banco")
                return False
            return True
        else:
            self.memory_mocks.clear()
            return True
    
    def mock_exists(self, mock_id: str) -> bool:
        """Verifica se um mock existe. Se banco estiver conectado, só verifica no banco."""
        if self.db_manager.is_connected():
            return self.db_manager.mock_exists(mock_id)
        else:
            return mock_id in self.memory_mocks
    
    def find_matching_mock(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """Encontra um mock que corresponde ao path e método."""
        for mock_id, mock_data in self.memory_mocks.items():
            if mock_data['http_method'] == method.upper():
                match = mock_data['uri_pattern'].match(path)
                if match:
                    return {
                        'mock_id': mock_id,
                        'status_code': mock_data['status_code'],
                        'response': mock_data['response'],
                        'variables': match.groupdict()
                    }
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema."""
        return {
            'database_connected': self.db_manager.is_connected(),
            'total_mocks': len(self.memory_mocks),
            'use_database': self.db_manager.use_database,
            'fallback_to_memory': self.db_manager.fallback_to_memory
        }
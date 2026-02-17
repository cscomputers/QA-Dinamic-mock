#!/usr/bin/env python3
"""
Mocks Manager com suporte a headers customizados
"""

import re
import random
import logging
from typing import Dict, Any, List, Optional
from src.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MocksManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        # Fallback em memória (usado apenas quando banco não está disponível)
        self.memory_mocks: Dict[str, Dict[str, Any]] = {}
        
        # Verifica se deve usar fallback
        if not self.db_manager.is_connected() and self.db_manager.use_database:
            logger.warning("⚠️  USANDO FALLBACK EM MEMÓRIA - Dados não serão persistidos")
        
        logger.info(f"MocksManager inicializado - Modo: {'Banco de dados' if self.db_manager.is_connected() else 'Memória (fallback)'}")
    
    def _is_using_database(self) -> bool:
        """Verifica se está usando banco de dados ativamente."""
        return self.db_manager.is_connected()
    
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
    
    def create_mock(self, uri: str, http_method: str, status_code: int, response: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> str:
        """Cria ou atualiza mock por uri + http_method."""
        if self._is_using_database():
            return self._create_mock_in_database(uri, http_method, status_code, response, headers)
        else:
            return self._create_mock_in_memory(uri, http_method, status_code, response, headers)
    
    def _create_mock_in_database(self, uri: str, http_method: str, status_code: int, response: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> str:
        """Cria mock no banco de dados."""
        # Busca mock existente no banco
        db_mocks = self.db_manager.get_all_mocks()
        for mock in db_mocks:
            if mock['uri'] == uri and mock['http_method'] == http_method:
                self.db_manager.update_mock(mock['id'], status_code, response, headers=headers)
                return mock['id']
        
        # Se não existe, cria novo
        mock_id = self.generate_id()
        uri_pattern_str = self.compile_uri_pattern(uri)
        self.db_manager.create_mock(mock_id, uri, http_method, status_code, response, uri_pattern_str, headers)
        return mock_id
    
    def _create_mock_in_memory(self, uri: str, http_method: str, status_code: int, response: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> str:
        """Cria mock na memória."""
        # Busca mock existente na memória
        for mock_id, mock_data in self.memory_mocks.items():
            if mock_data['uri'] == uri and mock_data['http_method'] == http_method:
                self.update_mock(mock_id, status_code, response, headers=headers)
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
            'headers': headers or {},
            'uri_pattern': uri_pattern_compiled
        }
        return mock_id
    
    def get_mock(self, mock_id: str) -> Optional[Dict[str, Any]]:
        """Recupera um mock por ID."""
        if self._is_using_database():
            return self._get_mock_from_database(mock_id)
        else:
            return self._get_mock_from_memory(mock_id)
    
    def _get_mock_from_database(self, mock_id: str) -> Optional[Dict[str, Any]]:
        """Recupera mock do banco."""
        db_mock = self.db_manager.get_mock(mock_id)
        if db_mock:
            return {
                'uri': db_mock['uri'],
                'http_method': db_mock['http_method'],
                'status_code': db_mock['status_code'],
                'response': db_mock['response'],
                'headers': db_mock.get('headers', {})
            }
        return None
    
    def _get_mock_from_memory(self, mock_id: str) -> Optional[Dict[str, Any]]:
        """Recupera mock da memória."""
        if mock_id in self.memory_mocks:
            mock_data = self.memory_mocks[mock_id].copy()
            # Remove o padrão compilado antes de retornar
            mock_data.pop('uri_pattern', None)
            return mock_data
        return None
    
    def get_all_mocks(self) -> List[Dict[str, Any]]:
        """Recupera todos os mocks."""
        if self._is_using_database():
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
                   response: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> bool:
        """Atualiza um mock existente."""
        if not self.mock_exists(mock_id):
            return False
        
        if self._is_using_database():
            return self.db_manager.update_mock(mock_id, status_code, response, headers=headers)
        else:
            if mock_id in self.memory_mocks:
                if status_code is not None:
                    self.memory_mocks[mock_id]['status_code'] = status_code
                if response is not None:
                    self.memory_mocks[mock_id]['response'] = response
                if headers is not None:
                    self.memory_mocks[mock_id]['headers'] = headers
            return True
    
    def delete_mock(self, mock_id: str) -> bool:
        """Remove um mock."""
        if not self.mock_exists(mock_id):
            return False
        
        if self._is_using_database():
            return self.db_manager.delete_mock(mock_id)
        else:
            self.memory_mocks.pop(mock_id, None)
            return True
    
    def delete_all_mocks(self) -> bool:
        """Remove todos os mocks."""
        if self._is_using_database():
            return self.db_manager.delete_all_mocks()
        else:
            self.memory_mocks.clear()
            return True
    
    def mock_exists(self, mock_id: str) -> bool:
        """Verifica se um mock existe."""
        if self._is_using_database():
            return self.db_manager.mock_exists(mock_id)
        else:
            return mock_id in self.memory_mocks
    
    def find_matching_mock(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """Encontra um mock que corresponde ao path e método."""
        if self._is_using_database():
            return self._find_mock_in_database(path, method)
        else:
            return self._find_mock_in_memory(path, method)
    
    def _find_mock_in_database(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """Busca mock no banco de dados."""
        db_mocks = self.db_manager.get_all_mocks()
        for mock in db_mocks:
            if mock['http_method'] == method.upper():
                pattern = re.compile(f"^{self.compile_uri_pattern(mock['uri'])}$")
                match = pattern.match(path)
                if match:
                    return {
                        'mock_id': mock['id'],
                        'status_code': mock['status_code'],
                        'response': mock['response'],
                        'headers': mock.get('headers', {}),
                        'variables': match.groupdict()
                    }
        return None
    
    def _find_mock_in_memory(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """Busca mock na memória."""
        for mock_id, mock_data in self.memory_mocks.items():
            if mock_data['http_method'] == method.upper():
                match = mock_data['uri_pattern'].match(path)
                if match:
                    return {
                        'mock_id': mock_id,
                        'status_code': mock_data['status_code'],
                        'response': mock_data['response'],
                        'headers': mock_data.get('headers', {}),
                        'variables': match.groupdict()
                    }
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema."""
        if self._is_using_database():
            total_mocks = len(self.db_manager.get_all_mocks())
            storage_mode = "Database"
        else:
            total_mocks = len(self.memory_mocks)
            storage_mode = "Memory (Fallback)" if self.db_manager.use_database else "Memory"
        
        return {
            'database_connected': self.db_manager.is_connected(),
            'storage_mode': storage_mode,
            'total_mocks': total_mocks,
            'use_database': self.db_manager.use_database,
            'fallback_to_memory': self.db_manager.fallback_to_memory
        }

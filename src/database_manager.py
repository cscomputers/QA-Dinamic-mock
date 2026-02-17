#!/usr/bin/env python3
"""
Database Manager com suporte a headers customizados
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, Column, String, Integer, Text, MetaData, Table, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.metadata = MetaData()
        self.mocks_table = None
        self.use_database = os.getenv("USE_DATABASE", "false").lower() == "true"
        self.fallback_to_memory = os.getenv("FALLBACK_TO_MEMORY", "true").lower() == "true"
        self.connected = False
        
        if self.use_database:
            self._setup_database()
    
    def _get_connection_string(self) -> str:
        """Constrói a string de conexão do PostgreSQL."""
        server = os.getenv("DB_SERVER", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "qa_api")
        username = os.getenv("DB_USER", "acloman")
        password = os.getenv("DB_PASSWORD")
        if not password:
            raise ValueError("DB_PASSWORD não foi configurada")
        return f"postgresql+psycopg2://{username}:{password}@{server}:{port}/{database}"
    
    def _setup_database(self):
        """Configura a conexão com o banco de dados."""
        try:
            connection_string = self._get_connection_string()
            self.engine = create_engine(connection_string, echo=False)
            
            # Define a tabela de mocks
            self.mocks_table = Table(
                'qa_api',
                self.metadata,
                Column('id', String(10), primary_key=True),
                Column('uri', String(500), nullable=False),
                Column('http_method', String(10), nullable=False),
                Column('status_code', Integer, nullable=False),
                Column('response_body', Text, nullable=False),
                Column('uri_pattern', String(500), nullable=False),
                Column('headers', JSONB, nullable=True, default={})
            )
            
            # Testa a conexão
            with self.engine.connect():
                logger.info("Conexão com banco de dados estabelecida com sucesso")
            
            # Cria a tabela se não existir
            self.metadata.create_all(self.engine)
            self.connected = True
            
        except Exception as e:
            logger.error(f"Erro ao conectar com banco de dados: {e}")
            if self.fallback_to_memory:
                logger.warning("⚠️  FALLBACK ATIVADO: Usando armazenamento em memória devido à falha na conexão com o banco")
                self.connected = False
            else:
                raise
    
    def is_connected(self) -> bool:
        """Verifica se está conectado ao banco."""
        if not self.use_database:
            return False
        
        if not self.engine:
            return False
            
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar conexão: {e}")
            self.connected = False
            return False
    
    def create_mock(self, mock_id: str, uri: str, http_method: str, 
                   status_code: int, response: Dict[str, Any], uri_pattern: str, 
                   headers: Optional[Dict[str, str]] = None) -> bool:
        """Cria um mock no banco de dados."""
        if not self.is_connected():
            return False
            
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    self.mocks_table.insert(),
                    {
                        'id': mock_id,
                        'uri': uri,
                        'http_method': http_method,
                        'status_code': status_code,
                        'response_body': json.dumps(response),
                        'uri_pattern': uri_pattern,
                        'headers': headers or {}
                    }
                )
            return True
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar mock no banco: {e}")
            return False
    
    def get_mock(self, mock_id: str) -> Optional[Dict[str, Any]]:
        """Recupera um mock do banco de dados."""
        if not self.is_connected():
            return None
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    self.mocks_table.select().where(self.mocks_table.c.id == mock_id)
                ).fetchone()
                
                if result:
                    # Tenta carregar headers se existir a coluna, senão usa dict vazio
                    try:
                        headers = result.headers if hasattr(result, 'headers') and result.headers else {}
                    except Exception:
                        headers = {}
                    
                    return {
                        'id': result.id,
                        'uri': result.uri,
                        'http_method': result.http_method,
                        'status_code': result.status_code,
                        'response': json.loads(result.response_body),
                        'uri_pattern': result.uri_pattern,
                        'headers': headers
                    }
        except SQLAlchemyError as e:
            logger.error(f"Erro ao recuperar mock do banco: {e}")
        return None
    
    def get_all_mocks(self) -> List[Dict[str, Any]]:
        """Recupera todos os mocks do banco de dados."""
        if not self.is_connected():
            return []
            
        try:
            with self.engine.connect() as conn:
                results = conn.execute(self.mocks_table.select()).fetchall()
                mocks = []
                for row in results:
                    mocks.append({
                        'id': row.id,
                        'uri': row.uri,
                        'http_method': row.http_method,
                        'status_code': row.status_code,
                        'response': json.loads(row.response_body),
                        'uri_pattern': row.uri_pattern,
                        'headers': row.headers if hasattr(row, 'headers') and row.headers else {}
                    })
                return mocks
        except SQLAlchemyError as e:
            logger.error(f"Erro ao recuperar mocks do banco: {e}")
        return []
    
    def update_mock(self, mock_id: str, status_code: Optional[int] = None, 
                   response: Optional[Dict[str, Any]] = None,
                   uri: Optional[str] = None,
                   http_method: Optional[str] = None,
                   headers: Optional[Dict[str, str]] = None) -> bool:
        """Atualiza um mock no banco de dados, incluindo uri e método."""
        if not self.is_connected():
            return False
            
        try:
            with self.engine.connect() as conn:
                update_data = {}
                if status_code is not None:
                    update_data['status_code'] = status_code
                if response is not None:
                    update_data['response_body'] = json.dumps(response)
                if uri is not None:
                    update_data['uri'] = uri
                    # Atualiza uri_pattern também
                    from src.mocks_manager import MocksManager
                    update_data['uri_pattern'] = MocksManager.compile_uri_pattern_static(uri)
                if http_method is not None:
                    update_data['http_method'] = http_method
                if headers is not None:
                    update_data['headers'] = headers
                    
                if update_data:
                    conn.execute(
                        self.mocks_table.update().where(
                            self.mocks_table.c.id == mock_id
                        ).values(**update_data)
                    )
                return True
        except SQLAlchemyError as e:
            logger.error(f"Erro ao atualizar mock no banco: {e}")
        return False
    
    def delete_mock(self, mock_id: str) -> bool:
        """Remove um mock do banco de dados."""
        if not self.is_connected():
            return False
            
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    self.mocks_table.delete().where(self.mocks_table.c.id == mock_id)
                )
            return True
        except SQLAlchemyError as e:
            logger.error(f"Erro ao remover mock do banco: {e}")
        return False
    
    def delete_all_mocks(self) -> bool:
        """Remove todos os mocks do banco de dados."""
        if not self.is_connected():
            return False
            
        try:
            with self.engine.connect() as conn:
                conn.execute(self.mocks_table.delete())
            return True
        except SQLAlchemyError as e:
            logger.error(f"Erro ao limpar mocks do banco: {e}")
        return False
    
    def mock_exists(self, mock_id: str) -> bool:
        """Verifica se um mock existe no banco."""
        if not self.is_connected():
            return False
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    self.mocks_table.select().where(self.mocks_table.c.id == mock_id)
                ).fetchone()
                return result is not None
        except SQLAlchemyError as e:
            logger.error(f"Erro ao verificar existência do mock: {e}")
        return False

"""
Gerenciador de conexão com o banco de dados MySQL
"""
import mysql.connector
from mysql.connector import Error
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

from config.settings import DATABASE_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerenciador de conexões com o banco de dados"""
    
    def __init__(self):
        self._connection = None
        self._connection_pool = None
        
    def create_connection(self) -> Optional[mysql.connector.MySQLConnection]:
        """Cria uma nova conexão com o banco de dados"""
        try:
            connection = mysql.connector.connect(**DATABASE_CONFIG)
            if connection.is_connected():
                logger.info("Conexão com MySQL estabelecida com sucesso")
                return connection
        except Error as e:
            logger.error(f"Erro ao conectar com MySQL: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões com o banco"""
        connection = None
        try:
            connection = self.create_connection()
            if connection:
                yield connection
            else:
                raise Exception("Não foi possível estabelecer conexão com o banco")
        except Error as e:
            logger.error(f"Erro na operação do banco: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[Any]:
        """Executa uma query no banco de dados"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                
                if fetch:
                    if 'SELECT' in query.upper():
                        return cursor.fetchall()
                    else:
                        return cursor.fetchone()
                else:
                    connection.commit()
                    return cursor.lastrowid if 'INSERT' in query.upper() else cursor.rowcount
                    
            except Error as e:
                logger.error(f"Erro ao executar query: {e}")
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def execute_many(self, query: str, data: list) -> int:
        """Executa múltiplas queries do mesmo tipo"""
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.executemany(query, data)
                connection.commit()
                return cursor.rowcount
            except Error as e:
                logger.error(f"Erro ao executar múltiplas queries: {e}")
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
        except Exception as e:
            logger.error(f"Teste de conexão falhou: {e}")
            return False
    
    def create_database_if_not_exists(self) -> bool:
        """Cria o banco de dados se não existir"""
        try:
            # Conecta sem especificar o banco
            config_without_db = DATABASE_CONFIG.copy()
            db_name = config_without_db.pop('database')
            
            connection = mysql.connector.connect(**config_without_db)
            cursor = connection.cursor()
            
            # Cria o banco se não existir
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            connection.commit()
            
            logger.info(f"Banco de dados '{db_name}' verificado/criado com sucesso")
            return True
            
        except Error as e:
            logger.error(f"Erro ao criar banco de dados: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def initialize_database(self) -> bool:
        """Inicializa o banco de dados com as tabelas necessárias"""
        try:
            # Primeiro, cria o banco se não existir
            if not self.create_database_if_not_exists():
                return False
            
            # Lê e executa o script SQL de criação das tabelas
            from pathlib import Path
            sql_file = Path(__file__).parent / 'create_tables.sql'
            
            if sql_file.exists():
                with open(sql_file, 'r', encoding='utf-8') as file:
                    sql_script = file.read()
                
                # Divide o script em comandos individuais
                commands = sql_script.split(';')
                
                with self.get_connection() as connection:
                    cursor = connection.cursor()
                    
                    for command in commands:
                        command = command.strip()
                        if command:
                            cursor.execute(command)
                    
                    connection.commit()
                    logger.info("Banco de dados inicializado com sucesso")
                    return True
            else:
                logger.error("Arquivo SQL de inicialização não encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            return False


# Instância global do gerenciador
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """Retorna a instância do gerenciador de banco de dados"""
    return db_manager


# Funções auxiliares para operações comuns
def execute_query(query: str, params: tuple = None, fetch: bool = False):
    """Executa uma query utilizando o gerenciador global"""
    return db_manager.execute_query(query, params, fetch)


def execute_many(query: str, data: list):
    """Executa múltiplas queries utilizando o gerenciador global"""
    return db_manager.execute_many(query, data)

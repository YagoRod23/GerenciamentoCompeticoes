"""
Utilitários para operações de banco de dados
"""
import logging
from typing import Optional, Any, Dict, List
from sqlalchemy.exc import SQLAlchemyError
from database.database import SessionLocal

logger = logging.getLogger(__name__)


class DatabaseUtils:
    """Utilitários para operações de banco de dados"""
    
    @staticmethod
    def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> Optional[List[Dict]]:
        """
        Executa uma query SQL customizada
        
        Args:
            query: Query SQL para executar
            params: Parâmetros da query
            
        Returns:
            Resultado da query ou None se erro
        """
        session = SessionLocal()
        try:
            result = session.execute(query, params or {})
            if result.returns_rows:
                return [dict(row) for row in result.fetchall()]
            else:
                session.commit()
                return []
        except SQLAlchemyError as e:
            logger.error(f"Erro ao executar query: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    @staticmethod
    def backup_database(backup_path: str) -> bool:
        """
        Faz backup do banco de dados
        
        Args:
            backup_path: Caminho para salvar o backup
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Implementação específica para SQLite
            import shutil
            from database.database import DATABASE_URL
            
            db_path = DATABASE_URL.replace('sqlite:///', '')
            shutil.copy2(db_path, backup_path)
            logger.info(f"Backup criado em: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return False
    
    @staticmethod
    def restore_database(backup_path: str) -> bool:
        """
        Restaura banco de dados do backup
        
        Args:
            backup_path: Caminho do arquivo de backup
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            import shutil
            from database.database import DATABASE_URL
            
            db_path = DATABASE_URL.replace('sqlite:///', '')
            shutil.copy2(backup_path, db_path)
            logger.info(f"Banco restaurado de: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False

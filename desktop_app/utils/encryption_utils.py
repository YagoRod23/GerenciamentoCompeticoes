"""
Utilitários para criptografia e hashing
"""
import bcrypt
import hashlib
import secrets
from typing import str


class EncryptionUtils:
    """Utilitários para criptografia"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash da senha usando bcrypt
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verifica se senha corresponde ao hash
        
        Args:
            password: Senha em texto plano
            hashed: Hash da senha
            
        Returns:
            True se corresponde, False caso contrário
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def generate_salt() -> str:
        """
        Gera salt aleatório
        
        Returns:
            Salt como string hexadecimal
        """
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_md5(text: str) -> str:
        """
        Gera hash MD5 de um texto
        
        Args:
            text: Texto para gerar hash
            
        Returns:
            Hash MD5 como string hexadecimal
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_sha256(text: str) -> str:
        """
        Gera hash SHA256 de um texto
        
        Args:
            text: Texto para gerar hash
            
        Returns:
            Hash SHA256 como string hexadecimal
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

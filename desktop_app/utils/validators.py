"""
Utilitários para validação de dados
"""
import re
from typing import Optional


class ValidationUtils:
    """Utilitários para validação de dados"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida formato de email
        
        Args:
            email: String do email
            
        Returns:
            True se válido, False caso contrário
        """
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """
        Valida CPF brasileiro
        
        Args:
            cpf: String do CPF
            
        Returns:
            True se válido, False caso contrário
        """
        if not cpf:
            return False
        
        # Remove formatação
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Valida primeiro dígito verificador
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        if int(cpf[9]) != digit1:
            return False
        
        # Valida segundo dígito verificador
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        return int(cpf[10]) == digit2
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Valida número de telefone brasileiro
        
        Args:
            phone: String do telefone
            
        Returns:
            True se válido, False caso contrário
        """
        if not phone:
            return False
        
        # Remove formatação
        phone = re.sub(r'[^0-9]', '', phone)
        
        # Aceita formatos: 11999999999 ou 1199999999
        return len(phone) in [10, 11] and phone.isdigit()
    
    @staticmethod
    def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitiza string removendo caracteres especiais
        
        Args:
            text: Texto a ser sanitizado
            max_length: Comprimento máximo
            
        Returns:
            Texto sanitizado
        """
        if not text:
            return ""
        
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Limita comprimento se especificado
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Valida força da senha
        
        Args:
            password: Senha a ser validada
            
        Returns:
            Tupla (é_válida, mensagem)
        """
        if len(password) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "Senha deve ter pelo menos uma letra maiúscula"
        
        if not re.search(r'[a-z]', password):
            return False, "Senha deve ter pelo menos uma letra minúscula"
        
        if not re.search(r'\d', password):
            return False, "Senha deve ter pelo menos um número"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Senha deve ter pelo menos um caractere especial"
        
        return True, "Senha válida"

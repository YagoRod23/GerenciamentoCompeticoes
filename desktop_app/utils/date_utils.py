"""
Utilitários para manipulação de datas
"""
from datetime import datetime, date, timedelta
from typing import Optional, Union


class DateUtils:
    """Utilitários para trabalhar com datas"""
    
    @staticmethod
    def format_date_br(date_obj: Union[date, datetime]) -> str:
        """
        Formata data no padrão brasileiro (dd/mm/yyyy)
        
        Args:
            date_obj: Objeto de data
            
        Returns:
            Data formatada como string
        """
        if date_obj is None:
            return ""
        return date_obj.strftime("%d/%m/%Y")
    
    @staticmethod
    def format_datetime_br(datetime_obj: datetime) -> str:
        """
        Formata data e hora no padrão brasileiro (dd/mm/yyyy HH:MM)
        
        Args:
            datetime_obj: Objeto de datetime
            
        Returns:
            Data e hora formatada como string
        """
        if datetime_obj is None:
            return ""
        return datetime_obj.strftime("%d/%m/%Y %H:%M")
    
    @staticmethod
    def parse_date_br(date_str: str) -> Optional[date]:
        """
        Converte string no formato brasileiro para objeto date
        
        Args:
            date_str: String no formato dd/mm/yyyy
            
        Returns:
            Objeto date ou None se inválido
        """
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return None
    
    @staticmethod
    def parse_datetime_br(datetime_str: str) -> Optional[datetime]:
        """
        Converte string no formato brasileiro para objeto datetime
        
        Args:
            datetime_str: String no formato dd/mm/yyyy HH:MM
            
        Returns:
            Objeto datetime ou None se inválido
        """
        try:
            return datetime.strptime(datetime_str, "%d/%m/%Y %H:%M")
        except ValueError:
            return None
    
    @staticmethod
    def calculate_age(birth_date: date) -> int:
        """
        Calcula idade baseada na data de nascimento
        
        Args:
            birth_date: Data de nascimento
            
        Returns:
            Idade em anos
        """
        if birth_date is None:
            return 0
        
        today = date.today()
        age = today.year - birth_date.year
        
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
            
        return age
    
    @staticmethod
    def days_between(start_date: date, end_date: date) -> int:
        """
        Calcula dias entre duas datas
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Número de dias
        """
        if start_date is None or end_date is None:
            return 0
        return (end_date - start_date).days
    
    @staticmethod
    def add_days(base_date: date, days: int) -> date:
        """
        Adiciona dias a uma data
        
        Args:
            base_date: Data base
            days: Número de dias a adicionar
            
        Returns:
            Nova data
        """
        return base_date + timedelta(days=days)

"""
Controller para autenticação de usuários
"""
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta

from database.models import User, UserType
from database.connection import execute_query


class AuthController:
    """Controlador de autenticação"""
    
    def __init__(self):
        self.current_user: Optional[User] = None
        self.session_start: Optional[datetime] = None
        self.max_session_duration = timedelta(hours=1)
        self.failed_attempts = {}
        self.max_attempts = 5
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Realiza login do usuário
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Verifica tentativas de login
            if self._is_blocked(username):
                return False, "Usuário temporariamente bloqueado devido a muitas tentativas de login"
            
            # Busca o usuário
            user = User.get_by_username(username)
            if not user:
                self._register_failed_attempt(username)
                return False, "Usuário ou senha incorretos"
            
            # Verifica a senha
            password_hash = self._hash_password(password)
            if user.password_hash != password_hash:
                self._register_failed_attempt(username)
                return False, "Usuário ou senha incorretos"
            
            # Login bem-sucedido
            self.current_user = user
            self.session_start = datetime.now()
            self._clear_failed_attempts(username)
            
            # Log do login
            self._log_login(user.id, True)
            
            return True, f"Login realizado com sucesso! Bem-vindo, {user.full_name}"
            
        except Exception as e:
            return False, f"Erro interno durante o login: {str(e)}"
    
    def logout(self) -> bool:
        """Realiza logout do usuário"""
        try:
            if self.current_user:
                self._log_login(self.current_user.id, False, is_logout=True)
                self.current_user = None
                self.session_start = None
            return True
        except Exception as e:
            print(f"Erro durante logout: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Verifica se há usuário autenticado"""
        if not self.current_user or not self.session_start:
            return False
        
        # Verifica se a sessão expirou
        if datetime.now() - self.session_start > self.max_session_duration:
            self.logout()
            return False
        
        return True
    
    def has_permission(self, required_level: UserType) -> bool:
        """
        Verifica se o usuário tem permissão para determinada ação
        
        Args:
            required_level: Nível mínimo de permissão necessário
        """
        if not self.is_authenticated():
            return False
        
        # Hierarquia de permissões: master > organization > public
        permission_levels = {
            UserType.PUBLIC: 1,
            UserType.ORGANIZATION: 2,
            UserType.MASTER: 3
        }
        
        user_level = permission_levels.get(self.current_user.user_type, 0)
        required_level_value = permission_levels.get(required_level, 3)
        
        return user_level >= required_level_value
    
    def create_user(self, username: str, password: str, user_type: UserType, 
                   full_name: str, email: str = "") -> Tuple[bool, str]:
        """
        Cria novo usuário (apenas usuários master podem criar outros usuários)
        """
        if not self.has_permission(UserType.MASTER):
            return False, "Apenas usuários master podem criar novos usuários"
        
        try:
            # Verifica se o usuário já existe
            existing_user = User.get_by_username(username)
            if existing_user:
                return False, "Nome de usuário já existe"
            
            # Valida dados
            if len(username) < 3:
                return False, "Nome de usuário deve ter pelo menos 3 caracteres"
            
            if len(password) < 6:
                return False, "Senha deve ter pelo menos 6 caracteres"
            
            if not full_name.strip():
                return False, "Nome completo é obrigatório"
            
            # Cria o usuário
            new_user = User(
                username=username,
                password_hash=self._hash_password(password),
                user_type=user_type,
                full_name=full_name,
                email=email,
                is_active=True
            )
            
            if new_user.save():
                return True, "Usuário criado com sucesso"
            else:
                return False, "Erro ao salvar usuário no banco de dados"
                
        except Exception as e:
            return False, f"Erro ao criar usuário: {str(e)}"
    
    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Altera senha do usuário atual"""
        if not self.is_authenticated():
            return False, "Usuário não autenticado"
        
        try:
            # Verifica senha atual
            current_hash = self._hash_password(current_password)
            if self.current_user.password_hash != current_hash:
                return False, "Senha atual incorreta"
            
            # Valida nova senha
            if len(new_password) < 6:
                return False, "Nova senha deve ter pelo menos 6 caracteres"
            
            # Atualiza a senha
            new_hash = self._hash_password(new_password)
            query = "UPDATE users SET password_hash = %s WHERE id = %s"
            execute_query(query, (new_hash, self.current_user.id))
            
            self.current_user.password_hash = new_hash
            
            return True, "Senha alterada com sucesso"
            
        except Exception as e:
            return False, f"Erro ao alterar senha: {str(e)}"
    
    def extend_session(self):
        """Estende a sessão atual"""
        if self.is_authenticated():
            self.session_start = datetime.now()
    
    def _hash_password(self, password: str) -> str:
        """Gera hash da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _is_blocked(self, username: str) -> bool:
        """Verifica se usuário está bloqueado por tentativas falhadas"""
        if username not in self.failed_attempts:
            return False
        
        attempts, last_attempt = self.failed_attempts[username]
        
        # Bloqueia por 15 minutos após 5 tentativas
        if attempts >= self.max_attempts:
            if datetime.now() - last_attempt < timedelta(minutes=15):
                return True
            else:
                # Reset após o período de bloqueio
                del self.failed_attempts[username]
        
        return False
    
    def _register_failed_attempt(self, username: str):
        """Registra tentativa de login falhada"""
        now = datetime.now()
        if username in self.failed_attempts:
            attempts, _ = self.failed_attempts[username]
            self.failed_attempts[username] = (attempts + 1, now)
        else:
            self.failed_attempts[username] = (1, now)
    
    def _clear_failed_attempts(self, username: str):
        """Limpa tentativas falhadas após login bem-sucedido"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    def _log_login(self, user_id: int, success: bool, is_logout: bool = False):
        """Registra tentativa de login no banco"""
        try:
            action = "logout" if is_logout else ("login_success" if success else "login_failed")
            query = """
            INSERT INTO user_logs (user_id, action, ip_address, created_at)
            VALUES (%s, %s, %s, %s)
            """
            # Note: Para uma aplicação desktop, o IP seria localhost ou identificador da máquina
            execute_query(query, (user_id, action, "desktop_app", datetime.now()))
        except Exception as e:
            print(f"Erro ao registrar log: {e}")


# Instância global do controlador de autenticação
auth_controller = AuthController()

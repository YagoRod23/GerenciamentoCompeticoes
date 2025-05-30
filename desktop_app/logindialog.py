"""
Dialog de login do sistema
"""
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLineEdit, QPushButton, QLabel, QMessageBox,
                           QCheckBox, QGroupBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

from desktop_app.controllers.auth_controller import auth_controller


class LoginThread(QThread):
    """Thread para realizar login sem travar a interface"""
    login_result = pyqtSignal(bool, str)
    
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
    
    def run(self):
        """Executa login em thread separada"""
        try:
            success, message = auth_controller.login(self.username, self.password)
            self.login_result.emit(success, message)
        except Exception as e:
            self.login_result.emit(False, f"Erro no login: {str(e)}")


class LoginDialog(QDialog):
    """Dialog de login"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Sistema de Competições Universitárias")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # Remove botões padrão do dialog
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.login_thread = None
        self.setup_ui()
        
        # Conecta Enter para fazer login
        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)
    
    def setup_ui(self):
        """Configura interface do dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Título
        title_label = QLabel("Sistema de Competições\nUniversitárias")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Grupo de login
        login_group = QGroupBox("Acesso ao Sistema")
        login_layout = QFormLayout(login_group)
        
        # Campo usuário
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu nome de usuário")
        self.username_input.setMaxLength(50)
        login_layout.addRow("Usuário:", self.username_input)
        
        # Campo senha
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setMaxLength(100)
        login_layout.addRow("Senha:", self.password_input)
        
        # Checkbox lembrar usuário
        self.remember_checkbox = QCheckBox("Lembrar usuário")
        login_layout.addRow("", self.remember_checkbox)
        
        layout.addWidget(login_group)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Entrar")
        self.login_button.clicked.connect(self.login)
        self.login_button.setDefault(True)
        buttons_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Foco inicial no campo usuário
        self.username_input.setFocus()
        
        # Carrega último usuário se existir
        self.load_saved_credentials()
    
    def login(self):
        """Realiza login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username:
            self.show_error("Digite o nome de usuário")
            self.username_input.setFocus()
            return
        
        if not password:
            self.show_error("Digite a senha")
            self.password_input.setFocus()
            return
        
        # Inicia login em thread separada
        self.start_login_process(username, password)
    
    def start_login_process(self, username, password):
        """Inicia processo de login"""
        self.login_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.status_label.setText("Autenticando...")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        
        # Cria e inicia thread de login
        self.login_thread = LoginThread(username, password)
        self.login_thread.login_result.connect(self.on_login_result)
        self.login_thread.start()
    
    def on_login_result(self, success, message):
        """Callback do resultado do login"""
        self.progress_bar.setVisible(False)
        self.login_button.setEnabled(True)
        
        if success:
            # Salva credenciais se solicitado
            if self.remember_checkbox.isChecked():
                self.save_credentials()
            
            self.status_label.setText("Login realizado com sucesso!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            # Pequeno delay para mostrar sucesso
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(500, self.accept)
        else:
            self.show_error(message)
            self.password_input.clear()
            self.password_input.setFocus()
    
    def show_error(self, message):
        """Mostra mensagem de erro"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def save_credentials(self):
        """Salva credenciais do usuário"""
        try:
            import os
            import json
            from pathlib import Path
            
            config_dir = Path.home() / '.sports_system'
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / 'user_config.json'
            config_data = {
                'last_username': self.username_input.text().strip()
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f)
                
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")
    
    def load_saved_credentials(self):
        """Carrega credenciais salvas"""
        try:
            import os
            import json
            from pathlib import Path
            
            config_file = Path.home() / '.sports_system' / 'user_config.json'
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                last_username = config_data.get('last_username', '')
                if last_username:
                    self.username_input.setText(last_username)
                    self.remember_checkbox.setChecked(True)
                    self.password_input.setFocus()
                    
        except Exception as e:
            print(f"Erro ao carregar credenciais: {e}")
    
    def keyPressEvent(self, event):
        """Intercepta teclas pressionadas"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

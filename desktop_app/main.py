"""
Janela principal da aplicação desktop
"""
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QMenuBar, QStatusBar, QAction, QTabWidget, QLabel,
                           QFrame, QPushButton, QMessageBox, QDialog, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont

from desktop_app.controllers.auth_controller import auth_controller
from desktop_app.views.login_dialog import LoginDialog
from desktop_app.views.dashboard_widget import DashboardWidget
from desktop_app.views.competitions_widget import CompetitionsWidget
from desktop_app.views.teams_widget import TeamsWidget
from desktop_app.views.games_widget import GamesWidget
from desktop_app.views.users_widget import UsersWidget
from desktop_app.views.reports_widget import ReportsWidget
from database.models import UserType


class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    # Sinais para comunicação entre componentes
    user_logged_in = pyqtSignal(object)
    user_logged_out = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestão de Competições Esportivas Universitárias")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Variáveis de estado
        self.current_user = None
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self._check_session)
        self.session_timer.start(60000)  # Verifica a cada minuto
        
        # Inicialização da interface
        self._setup_ui()
        self._setup_menu()
        self._setup_status_bar()
        
        # Conecta sinais
        self.user_logged_in.connect(self._on_user_logged_in)
        self.user_logged_out.connect(self._on_user_logged_out)
        
        # Força login inicial
        self._show_login_dialog()
    
    def _setup_ui(self):
        """Configura interface principal"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Header com informações do usuário
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(60)
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-bottom: 2px solid #34495e;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        header_layout = QHBoxLayout(self.header_frame)
        
        # Logo/Título
        title_label = QLabel("🏆 Sistema de Competições Universitárias")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Informações do usuário
        self.user_info_label = QLabel("Usuário não logado")
        self.user_info_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(self.user_info_label)
        
        # Botão de logout
        self.logout_button = QPushButton("Sair")
        self.logout_button.setMaximumWidth(80)
        self.logout_button.clicked.connect(self._logout)
        self.logout_button.setEnabled(False)
        header_layout.addWidget(self.logout_button)
        
        main_layout.addWidget(self.header_frame)
        
        # Área principal com abas
        self.tab_widget = QTabWidget()
        self.tab_widget.setEnabled(False)  # Desabilitado até login
        
        # Cria as abas principais
        self._create_tabs()
        
        main_layout.addWidget(self.tab_widget)
    
    def _create_tabs(self):
        """Cria as abas da aplicação"""
        
        # Dashboard
        self.dashboard_widget = DashboardWidget()
        self.tab_widget.addTab(self.dashboard_widget, "📊 Dashboard")
        
        # Competições
        self.competitions_widget = CompetitionsWidget()
        self.tab_widget.addTab(self.competitions_widget, "🏆 Competições")
        
        # Equipes
        self.teams_widget = TeamsWidget()
        self.tab_widget.addTab(self.teams_widget, "👥 Equipes")
        
        # Jogos
        self.games_widget = GamesWidget()
        self.tab_widget.addTab(self.games_widget, "⚽ Jogos")
        
        # Relatórios
        self.reports_widget = ReportsWidget()
        self.tab_widget.addTab(self.reports_widget, "📈 Relatórios")
        
        # Usuários (apenas para usuários master)
        self.users_widget = UsersWidget()
        self.tab_widget.addTab(self.users_widget, "👤 Usuários")
    
    def _setup_menu(self):
        """Configura menu principal"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("&Arquivo")
        
        login_action = QAction("&Login", self)
        login_action.setShortcut("Ctrl+L")
        login_action.triggered.connect(self._show_login_dialog)
        file_menu.addAction(login_action)
        
        logout_action = QAction("L&ogout", self)
        logout_action.setShortcut("Ctrl+O")
        logout_action.triggered.connect(self._logout)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Ferramentas
        tools_menu = menubar.addMenu("&Ferramentas")
        
        refresh_action = QAction("&Atualizar", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_current_tab)
        tools_menu.addAction(refresh_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("&Ajuda")
        
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        """Configura barra de status"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Sistema carregado. Faça login para começar.")
        
        # Labels na barra de status
        self.connection_label = QLabel("🔴 Desconectado")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        self.session_label = QLabel("")
        self.status_bar.addPermanentWidget(self.session_label)
    
    def _show_login_dialog(self):
        """Mostra dialog de login"""
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            user = auth_controller.current_user
            if user:
                self.current_user = user
                self.user_logged_in.emit(user)
                self.status_bar.showMessage(f"Login realizado com sucesso. Bem-vindo, {user.full_name}!")
            else:
                QMessageBox.warning(self, "Erro", "Falha na autenticação.")
    
    def _logout(self):
        """Realiza logout"""
        if self.current_user:
            reply = QMessageBox.question(
                self, "Confirmar Logout", 
                "Tem certeza que deseja sair?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                auth_controller.logout()
                self.current_user = None
                self.user_logged_out.emit()
                self.status_bar.showMessage("Logout realizado com sucesso.")
                self._show_login_dialog()
    
    def _on_user_logged_in(self, user):
        """Callback quando usuário faz login"""
        self.user_info_label.setText(f"👤 {user.full_name} ({user.user_type.value})")
        self.logout_button.setEnabled(True)
        self.tab_widget.setEnabled(True)
        self.connection_label.setText("🟢 Conectado")
        
        # Esconde aba de usuários se não for master
        users_tab_index = self.tab_widget.indexOf(self.users_widget)
        if user.user_type != UserType.MASTER:
            self.tab_widget.setTabVisible(users_tab_index, False)
        else:
            self.tab_widget.setTabVisible(users_tab_index, True)
        
        # Atualiza todas as abas
        self._refresh_all_tabs()
        
        # Inicia timer de sessão
        self._update_session_info()
    
    def _on_user_logged_out(self):
        """Callback quando usuário faz logout"""
        self.user_info_label.setText("Usuário não logado")
        self.logout_button.setEnabled(False)
        self.tab_widget.setEnabled(False)
        self.connection_label.setText("🔴 Desconectado")
        self.session_label.setText("")
    
    def _check_session(self):
        """Verifica validade da sessão"""
        if not auth_controller.is_authenticated():
            if self.current_user:  # Sessão expirou
                QMessageBox.information(
                    self, "Sessão Expirada", 
                    "Sua sessão expirou. Faça login novamente."
                )
                self.current_user = None
                self.user_logged_out.emit()
                self._show_login_dialog()
        else:
            auth_controller.extend_session()
            self._update_session_info()
    
    def _update_session_info(self):
        """Atualiza informações da sessão"""
        if auth_controller.is_authenticated() and auth_controller.session_start:
            elapsed = auth_controller.session_start.strftime("%H:%M")
            self.session_label.setText(f"⏱️ Sessão: {elapsed}")
    
    def _refresh_current_tab(self):
        """Atualiza aba atual"""
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()
            self.status_bar.showMessage("Dados atualizados.", 3000)
    
    def _refresh_all_tabs(self):
        """Atualiza todas as abas"""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'refresh'):
                widget.refresh()
    
    def _show_about(self):
        """Mostra informações sobre o sistema"""
        about_text = """
        <h3>Sistema de Gestão de Competições Esportivas Universitárias</h3>
        <p><b>Versão:</b> 1.0.0</p>
        <p><b>Desenvolvido para:</b> Gestão completa de competições esportivas universitárias</p>
        
        <p><b>Funcionalidades:</b></p>
        <ul>
        <li>✅ Gestão de equipes e atletas</li>
        <li>✅ Criação e gerenciamento de competições</li>
        <li>✅ Múltiplos formatos (eliminação, pontos corridos, grupos, etc.)</li>
        <li>✅ Controle de jogos e resultados</li>
        <li>✅ Sistema de suspensões automáticas</li>
        <li>✅ Relatórios e estatísticas</li>
        <li>✅ Controle de usuários e permissões</li>
        </ul>
        
        <p><b>Modalidades suportadas:</b> Futebol, Futsal, Vôlei, Basquete, Handebol</p>
        
        <p>© 2025 - Sistema desenvolvido para universidades brasileiras</p>
        """
        
        QMessageBox.about(self, "Sobre o Sistema", about_text)
    
    def closeEvent(self, event):
        """Intercepta fechamento da janela"""
        if self.current_user:
            reply = QMessageBox.question(
                self, "Confirmar Saída", 
                "Tem certeza que deseja fechar o sistema?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                auth_controller.logout()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class Application:
    """Classe principal da aplicação"""
    
    def __init__(self):
        from PyQt5.QtWidgets import QApplication
        
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Sistema de Competições Universitárias")
        self.app.setApplicationVersion("1.0.0")
        
        # Configura estilo da aplicação
        self.app.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #bdc3c7;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #85c1e0;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        self.main_window = MainWindow()
    
    def run(self):
        """Executa a aplicação"""
        self.main_window.show()
        return self.app.exec_()


def main():
    """Função principal"""
    try:
        app = Application()
        sys.exit(app.run())
    except Exception as e:
        print(f"Erro fatal na aplicação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

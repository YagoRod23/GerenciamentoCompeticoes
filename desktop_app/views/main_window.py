"""
Janela principal da aplicação
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional

from .base_window import BaseWindow
from .dashboard_window import DashboardWindow
from .login_window import show_login
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType


class MainWindow(BaseWindow):
    """Janela principal da aplicação"""
    
    def __init__(self):
        super().__init__("Sistema de Gestão Esportiva", 1200, 800)
        
        # Widgets principais
        self.notebook: Optional[ttk.Notebook] = None
        self.status_bar: Optional[ttk.Label] = None
        self.user_info_label: Optional[ttk.Label] = None
        
        # Abas
        self.dashboard_frame: Optional[ttk.Frame] = None
        self.teams_frame: Optional[ttk.Frame] = None
        self.competitions_frame: Optional[ttk.Frame] = None
        self.games_frame: Optional[ttk.Frame] = None
        self.reports_frame: Optional[ttk.Frame] = None
        self.admin_frame: Optional[ttk.Frame] = None
        
        # Verificar autenticação
        if not auth_controller.is_authenticated():
            self.show_login()
        else:
            self.setup_ui()
            self.update_status()
    
    def show_login(self):
        """Exibe janela de login"""
        self.hide()
        login_window = show_login(self.on_login_success)
        login_window.run()
    
    def on_login_success(self):
        """Callback chamado após login bem-sucedido"""
        self.show()
        self.setup_ui()
        self.update_status()
    
    def setup_ui(self):
        """Configura a interface principal"""
        # Limpar janela se já existir conteúdo
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Menu principal
        self.setup_menu()
        
        # Toolbar
        self.setup_toolbar()
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Criar abas baseado nas permissões do usuário
        self.create_tabs()
        
        # Barra de status
        self.setup_status_bar()
    
    def setup_menu(self):
        """Configura menu principal"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo...", command=self.show_new_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Importar...", command=self.import_data)
        file_menu.add_command(label="Exportar...", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.logout)
        
        # Menu Visualizar
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_command(label="Atualizar", command=self.refresh_all)
        view_menu.add_separator()
        view_menu.add_command(label="Dashboard", command=lambda: self.notebook.select(0))
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Backup", command=self.backup_database)
        tools_menu.add_command(label="Configurações", command=self.show_settings)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Manual do Usuário", command=self.show_help)
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def setup_toolbar(self):
        """Configura barra de ferramentas"""
        toolbar = ttk.Frame(self.window)
        toolbar.pack(fill="x", padx=5, pady=(5, 0))
        
        # Botões da toolbar
        ttk.Button(toolbar, text="Dashboard", command=lambda: self.notebook.select(0)).pack(side="left", padx=(0, 5))
        
        if auth_controller.has_permission(UserType.ORGANIZATION):
            ttk.Button(toolbar, text="Nova Equipe", command=self.new_team).pack(side="left", padx=(0, 5))
            ttk.Button(toolbar, text="Nova Competição", command=self.new_competition).pack(side="left", padx=(0, 5))
            ttk.Button(toolbar, text="Novo Jogo", command=self.new_game).pack(side="left", padx=(0, 5))
        
        # Separador
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # Informações do usuário
        self.user_info_label = ttk.Label(toolbar, text="")
        self.user_info_label.pack(side="right")
        
        # Botão logout
        ttk.Button(toolbar, text="Sair", command=self.logout).pack(side="right", padx=(0, 10))
    
    def create_tabs(self):
        """Cria as abas baseado nas permissões"""
        # Dashboard (todos os usuários)
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Equipes
        self.teams_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.teams_frame, text="Equipes")
        
        # Competições
        self.competitions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.competitions_frame, text="Competições")
        
        # Jogos
        self.games_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.games_frame, text="Jogos")
        
        # Relatórios
        if auth_controller.has_permission(UserType.ORGANIZATION):
            self.reports_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.reports_frame, text="Relatórios")
        
        # Administração (apenas administradores)
        if auth_controller.has_permission(UserType.ADMIN):
            self.admin_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.admin_frame, text="Administração")
        
        # Carregar conteúdo inicial
        self.load_dashboard()
        
        # Bind para mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
    
    def setup_status_bar(self):
        """Configura barra de status"""
        status_frame = ttk.Frame(self.window)
        status_frame.pack(fill="x", side="bottom")
        
        self.status_bar = ttk.Label(status_frame, text="Pronto", relief="sunken")
        self.status_bar.pack(fill="x", side="left", padx=5, pady=2)
    
    def load_dashboard(self):
        """Carrega o dashboard"""
        try:
            # Limpar frame
            self.clear_frame(self.dashboard_frame)
            
            # Criar dashboard
            dashboard = DashboardWindow(self.dashboard_frame)
            dashboard.setup_dashboard()
            
        except Exception as e:
            self.show_message("Erro", f"Erro ao carregar dashboard: {str(e)}", "error")
    
    def on_tab_change(self, event):
        """Chamado quando muda de aba"""
        selected_tab = event.widget.tab('current')['text']
        
        try:
            if selected_tab == "Equipes" and not hasattr(self, 'teams_loaded'):
                self.load_teams_tab()
                self.teams_loaded = True
            elif selected_tab == "Competições" and not hasattr(self, 'competitions_loaded'):
                self.load_competitions_tab()
                self.competitions_loaded = True
            elif selected_tab == "Jogos" and not hasattr(self, 'games_loaded'):
                self.load_games_tab()
                self.games_loaded = True
            elif selected_tab == "Relatórios" and not hasattr(self, 'reports_loaded'):
                self.load_reports_tab()
                self.reports_loaded = True
            elif selected_tab == "Administração" and not hasattr(self, 'admin_loaded'):
                self.load_admin_tab()
                self.admin_loaded = True
        
        except Exception as e:
            self.show_message("Erro", f"Erro ao carregar aba: {str(e)}", "error")
    
    def load_teams_tab(self):
        """Carrega aba de equipes"""
        from .teams_window import TeamsWindow
        teams_window = TeamsWindow(self.teams_frame)
        teams_window.setup_teams_view()
    
    def load_competitions_tab(self):
        """Carrega aba de competições"""
        from .competitions_window import CompetitionsWindow
        comp_window = CompetitionsWindow(self.competitions_frame)
        comp_window.setup_competitions_view()
    
    def load_games_tab(self):
        """Carrega aba de jogos"""
        from .games_window import GamesWindow
        games_window = GamesWindow(self.games_frame)
        games_window.setup_games_view()
    
    def load_reports_tab(self):
        """Carrega aba de relatórios"""
        from .reports_window import ReportsWindow
        reports_window = ReportsWindow(self.reports_frame)
        reports_window.setup_reports_view()
    
    def load_admin_tab(self):
        """Carrega aba de administração"""
        from .admin_window import AdminWindow
        admin_window = AdminWindow(self.admin_frame)
        admin_window.setup_admin_view()
    
    # Métodos de ação
    def show_new_menu(self):
        """Exibe menu de novos itens"""
        menu = tk.Menu(self.window, tearoff=0)
        
        if auth_controller.has_permission(UserType.ORGANIZATION):
            menu.add_command(label="Nova Equipe", command=self.new_team)
            menu.add_command(label="Nova Competição", command=self.new_competition)
            menu.add_command(label="Novo Jogo", command=self.new_game)
        
        if auth_controller.has_permission(UserType.ADMIN):
            menu.add_separator()
            menu.add_command(label="Novo Usuário", command=self.new_user)
        
        # Mostrar menu na posição do mouse
        try:
            menu.tk_popup(self.window.winfo_pointerx(), self.window.winfo_pointery())
        finally:
            menu.grab_release()
    
    def new_team(self):
        """Abre janela para nova equipe"""
        from .team_dialog import TeamDialog
        dialog = TeamDialog(self.window)
        if dialog.result:
            self.refresh_teams()
    
    def new_competition(self):
        """Abre janela para nova competição"""
        from .competition_dialog import CompetitionDialog
        dialog = CompetitionDialog(self.window)
        if dialog.result:
            self.refresh_competitions()
    
    def new_game(self):
        """Abre janela para novo jogo"""
        from .game_dialog import GameDialog
        dialog = GameDialog(self.window)
        if dialog.result:
            self.refresh_games()
    
    def new_user(self):
        """Abre janela para novo usuário"""
        from .user_dialog import UserDialog
        dialog = UserDialog(self.window)
        if dialog.result:
            self.refresh_admin()
    
    def refresh_all(self):
        """Atualiza todas as abas"""
        # Reset flags de carregamento
        for attr in ['teams_loaded', 'competitions_loaded', 'games_loaded', 
                    'reports_loaded', 'admin_loaded']:
            if hasattr(self, attr):
                delattr(self, attr)
        
        # Recarregar aba atual
        current_tab = self.notebook.tab(self.notebook.select(), 'text')
        self.on_tab_change(type('Event', (), {'widget': self.notebook})())
        
        self.update_status("Dados atualizados")
    
    def refresh_teams(self):
        """Atualiza aba de equipes"""
        if hasattr(self, 'teams_loaded'):
            delattr(self, 'teams_loaded')
            if self.notebook.tab(self.notebook.select(), 'text') == "Equipes":
                self.load_teams_tab()
    
    def refresh_competitions(self):
        """Atualiza aba de competições"""
        if hasattr(self, 'competitions_loaded'):
            delattr(self, 'competitions_loaded')
            if self.notebook.tab(self.notebook.select(), 'text') == "Competições":
                self.load_competitions_tab()
    
    def refresh_games(self):
        """Atualiza aba de jogos"""
        if hasattr(self, 'games_loaded'):
            delattr(self, 'games_loaded')
            if self.notebook.tab(self.notebook.select(), 'text') == "Jogos":
                self.load_games_tab()
    
    def refresh_admin(self):
        """Atualiza aba de administração"""
        if hasattr(self, 'admin_loaded'):
            delattr(self, 'admin_loaded')
            if self.notebook.tab(self.notebook.select(), 'text') == "Administração":
                self.load_admin_tab()
    
    def import_data(self):
        """Importa dados"""
        self.show_message("Em Desenvolvimento", "Funcionalidade em desenvolvimento", "info")
    
    def export_data(self):
        """Exporta dados"""
        self.show_message("Em Desenvolvimento", "Funcionalidade em desenvolvimento", "info")
    
    def backup_database(self):
        """Faz backup do banco de dados"""
        if auth_controller.has_permission(UserType.ADMIN):
            # Implementar backup
            self.show_message("Em Desenvolvimento", "Funcionalidade em desenvolvimento", "info")
        else:
            self.show_message("Acesso Negado", "Você não tem permissão para esta ação", "error")
    
    def show_settings(self):
        """Exibe configurações"""
        self.show_message("Em Desenvolvimento", "Funcionalidade em desenvolvimento", "info")
    
    def show_help(self):
        """Exibe ajuda"""
        help_text = """
        Sistema de Gestão Esportiva
        
        Este sistema permite gerenciar:
        - Equipes e jogadores
        - Competições e torneios
        - Jogos e resultados
        - Relatórios estatísticos
        
        Para mais informações, entre em contato com a administração.
        """
        self.show_message("Ajuda", help_text, "info")
    
    def show_about(self):
        """Exibe informações sobre o sistema"""
        about_text = """
        Sistema de Gestão Esportiva
        Versão 1.0
        
        Desenvolvido para gerenciamento de competições esportivas.
        
        © 2025 - Todos os direitos reservados
        """
        self.show_message("Sobre", about_text, "info")
    
    def update_status(self, message: str = ""):
        """Atualiza barra de status"""
        if not message:
            if auth_controller.current_user:
                user = auth_controller.current_user
                message = f"Usuário: {user.full_name} | Tipo: {user.user_type.value}"
            else:
                message = "Pronto"
        
        if self.status_bar:
            self.status_bar.config(text=message)
        
        if self.user_info_label and auth_controller.current_user:
            user = auth_controller.current_user
            self.user_info_label.config(text=f"{user.full_name} ({user.user_type.value})")
    
    def logout(self):
        """Faz logout do sistema"""
        if self.show_confirmation("Sair", "Deseja realmente sair do sistema?"):
            auth_controller.logout()
            self.close()
            
            # Mostrar tela de login novamente
            self.show_login()
    
    def on_closing(self):
        """Sobrescreve método de fechamento"""
        if self.show_confirmation("Sair", "Deseja realmente fechar o sistema?"):
            auth_controller.logout()
            self.window.quit()

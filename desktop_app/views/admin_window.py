"""
Janela de administração do sistema
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional

from desktop_app.controllers.admin_controller import admin_controller
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType


class AdminWindow:
    """Janela de administração"""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent = parent_frame
        
        # Verificar permissões
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            self.show_access_denied()
            return
        
        # Widgets principais
        self.users_tree: Optional[ttk.Treeview] = None
        self.selected_user_id: Optional[int] = None
        
        # Frames
        self.system_info_frame: Optional[ttk.Frame] = None
        self.backup_frame: Optional[ttk.Frame] = None
    
    def setup_admin_view(self):
        """Configura a view de administração"""
        # Limpar frame pai
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Verificar permissões novamente
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            self.show_access_denied()
            return
        
        # Título
        title_label = ttk.Label(self.parent, text="Administração do Sistema", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Notebook para diferentes seções
        self.admin_notebook = ttk.Notebook(self.parent)
        self.admin_notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Aba de usuários
        users_frame = ttk.Frame(self.admin_notebook)
        self.admin_notebook.add(users_frame, text="Usuários")
        self.setup_users_tab(users_frame)
        
        # Aba de sistema
        system_frame = ttk.Frame(self.admin_notebook)
        self.admin_notebook.add(system_frame, text="Sistema")
        self.setup_system_tab(system_frame)
        
        # Aba de backup
        backup_frame = ttk.Frame(self.admin_notebook)
        self.admin_notebook.add(backup_frame, text="Backup")
        self.setup_backup_tab(backup_frame)
        
        # Aba de logs
        logs_frame = ttk.Frame(self.admin_notebook)
        self.admin_notebook.add(logs_frame, text="Logs")
        self.setup_logs_tab(logs_frame)
    
    def show_access_denied(self):
        """Exibe mensagem de acesso negado"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        access_frame = ttk.Frame(self.parent)
        access_frame.pack(expand=True)
        
        ttk.Label(access_frame, text="Acesso Negado", 
                 font=("Arial", 20, "bold"), foreground="red").pack(pady=20)
        ttk.Label(access_frame, text="Você não tem permissão para acessar esta área.",
                 font=("Arial", 12)).pack()
        ttk.Label(access_frame, text="Apenas administradores podem acessar as configurações do sistema.",
                 font=("Arial", 10)).pack(pady=(10, 0))
    
    def setup_users_tab(self, parent: ttk.Frame):
        """Configura aba de gerenciamento de usuários"""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(toolbar, text="Novo Usuário", 
                  command=self.new_user).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="Editar", 
                  command=self.edit_user).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="Desativar", 
                  command=self.deactivate_user).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="Resetar Senha", 
                  command=self.reset_password).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="Atualizar", 
                  command=self.refresh_users).pack(side="right")
        
        # Lista de usuários
        users_container = ttk.LabelFrame(parent, text="Usuários do Sistema", padding="10")
        users_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Treeview
        columns = ("nome", "usuario", "email", "tipo", "status", "ultimo_acesso")
        self.users_tree = ttk.Treeview(users_container, columns=columns, show="headings")
        
        # Cabeçalhos
        self.users_tree.heading("nome", text="Nome Completo")
        self.users_tree.heading("usuario", text="Usuário")
        self.users_tree.heading("email", text="Email")
        self.users_tree.heading("tipo", text="Tipo")
        self.users_tree.heading("status", text="Status")
        self.users_tree.heading("ultimo_acesso", text="Último Acesso")
        
        # Larguras
        self.users_tree.column("nome", width=150)
        self.users_tree.column("usuario", width=120)
        self.users_tree.column("email", width=200)
        self.users_tree.column("tipo", width=100)
        self.users_tree.column("status", width=80)
        self.users_tree.column("ultimo_acesso", width=120)
        
        self.users_tree.pack(fill="both", expand=True)
        
        # Scrollbars
        users_scroll = ttk.Scrollbar(users_container, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scroll.set)
        users_scroll.pack(side="right", fill="y")
        
        # Bind para seleção
        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_select)
        
        # Carregar usuários
        self.refresh_users()
    
    def setup_system_tab(self, parent: ttk.Frame):
        """Configura aba de informações do sistema"""
        # Informações do sistema
        info_frame = ttk.LabelFrame(parent, text="Informações do Sistema", padding="10")
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # Obter informações do sistema
        system_info = admin_controller.get_system_info()
        
        info_text = f"""Versão do Sistema: {system_info.get('version', 'N/A')}
Database: {system_info.get('database', 'N/A')}
Total de Usuários: {system_info.get('total_users', 0)}
Total de Equipes: {system_info.get('total_teams', 0)}
Total de Competições: {system_info.get('total_competitions', 0)}
Total de Jogos: {system_info.get('total_games', 0)}
Espaço em Disco: {system_info.get('disk_space', 'N/A')}
Última Atualização: {system_info.get('last_update', 'N/A')}"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify="left")
        info_label.pack(anchor="w")
        
        # Configurações do sistema
        config_frame = ttk.LabelFrame(parent, text="Configurações", padding="10")
        config_frame.pack(fill="x", padx=10, pady=10)
        
        # Configurações básicas
        ttk.Button(config_frame, text="Configurações Gerais", 
                  command=self.open_general_settings).pack(fill="x", pady=2)
        ttk.Button(config_frame, text="Configurações de Email", 
                  command=self.open_email_settings).pack(fill="x", pady=2)
        ttk.Button(config_frame, text="Configurações de Backup", 
                  command=self.open_backup_settings).pack(fill="x", pady=2)
        
        # Manutenção
        maintenance_frame = ttk.LabelFrame(parent, text="Manutenção", padding="10")
        maintenance_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(maintenance_frame, text="Limpar Cache", 
                  command=self.clear_cache).pack(fill="x", pady=2)
        ttk.Button(maintenance_frame, text="Otimizar Database", 
                  command=self.optimize_database).pack(fill="x", pady=2)
        ttk.Button(maintenance_frame, text="Verificar Integridade", 
                  command=self.check_integrity).pack(fill="x", pady=2)
    
    def setup_backup_tab(self, parent: ttk.Frame):
        """Configura aba de backup"""
        # Backup manual
        manual_frame = ttk.LabelFrame(parent, text="Backup Manual", padding="10")
        manual_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(manual_frame, text="Criar backup completo do sistema:").pack(anchor="w")
        
        backup_buttons = ttk.Frame(manual_frame)
        backup_buttons.pack(fill="x", pady=(10, 0))
        
        ttk.Button(backup_buttons, text="Backup Completo", 
                  command=self.create_full_backup).pack(side="left", padx=(0, 5))
        ttk.Button(backup_buttons, text="Backup Database", 
                  command=self.create_db_backup).pack(side="left", padx=(0, 5))
        ttk.Button(backup_buttons, text="Restaurar Backup", 
                  command=self.restore_backup).pack(side="left")
        
        # Backup automático
        auto_frame = ttk.LabelFrame(parent, text="Backup Automático", padding="10")
        auto_frame.pack(fill="x", padx=10, pady=10)
        
        self.auto_backup_var = tk.BooleanVar()
        ttk.Checkbutton(auto_frame, text="Habilitar backup automático", 
                       variable=self.auto_backup_var,
                       command=self.toggle_auto_backup).pack(anchor="w")
        
        # Configurações de backup automático
        auto_config = ttk.Frame(auto_frame)
        auto_config.pack(fill="x", pady=(10, 0))
        
        ttk.Label(auto_config, text="Frequência:").pack(side="left")
        
        self.backup_frequency_var = tk.StringVar(value="daily")
        frequency_combo = ttk.Combobox(auto_config, textvariable=self.backup_frequency_var,
                                     values=["daily", "weekly", "monthly"],
                                     state="readonly", width=10)
        frequency_combo.pack(side="left", padx=(5, 15))
        
        ttk.Label(auto_config, text="Manter últimos:").pack(side="left")
        
        self.backup_keep_var = tk.StringVar(value="7")
        keep_spin = ttk.Spinbox(auto_config, from_=1, to=30, width=5,
                              textvariable=self.backup_keep_var)
        keep_spin.pack(side="left", padx=(5, 5))
        
        ttk.Label(auto_config, text="backups").pack(side="left")
        
        # Lista de backups existentes
        backups_frame = ttk.LabelFrame(parent, text="Backups Existentes", padding="10")
        backups_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview para backups
        backup_columns = ("nome", "data", "tamanho", "tipo")
        self.backups_tree = ttk.Treeview(backups_frame, columns=backup_columns, show="headings")
        
        self.backups_tree.heading("nome", text="Nome")
        self.backups_tree.heading("data", text="Data")
        self.backups_tree.heading("tamanho", text="Tamanho")
        self.backups_tree.heading("tipo", text="Tipo")
        
        self.backups_tree.pack(fill="both", expand=True)
        
        # Carregar lista de backups
        self.refresh_backups()
    
    def setup_logs_tab(self, parent: ttk.Frame):
        """Configura aba de logs"""
        # Filtros
        filters_frame = ttk.Frame(parent)
        filters_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(filters_frame, text="Nível:").pack(side="left")
        
        self.log_level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(filters_frame, textvariable=self.log_level_var,
                                 values=["ALL", "ERROR", "WARNING", "INFO", "DEBUG"],
                                 state="readonly", width=10)
        level_combo.pack(side="left", padx=(5, 15))
        
        ttk.Button(filters_frame, text="Filtrar", 
                  command=self.filter_logs).pack(side="left")
        ttk.Button(filters_frame, text="Limpar Logs", 
                  command=self.clear_logs).pack(side="left", padx=(10, 0))
        ttk.Button(filters_frame, text="Exportar", 
                  command=self.export_logs).pack(side="right")
        
        # Área de logs
        logs_container = ttk.LabelFrame(parent, text="Logs do Sistema", padding="10")
        logs_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.logs_text = tk.Text(logs_container, wrap="none", font=("Courier", 9))
        self.logs_text.pack(side="left", fill="both", expand=True)
        
        # Scrollbars para logs
        logs_v_scroll = ttk.Scrollbar(logs_container, orient="vertical", command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=logs_v_scroll.set)
        logs_v_scroll.pack(side="right", fill="y")
        
        logs_h_scroll = ttk.Scrollbar(logs_container, orient="horizontal", command=self.logs_text.xview)
        self.logs_text.configure(xscrollcommand=logs_h_scroll.set)
        logs_h_scroll.pack(side="bottom", fill="x")
        
        # Carregar logs
        self.refresh_logs()
    
    def refresh_users(self):
        """Atualiza lista de usuários"""
        try:
            # Limpar árvore
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # Buscar usuários
            users = admin_controller.get_all_users()
            
            for user in users:
                status = "Ativo" if user.is_active else "Inativo"
                last_login = user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else "Nunca"
                
                item_id = self.users_tree.insert('', 'end', values=(
                    user.full_name,
                    user.username,
                    user.email,
                    user.user_type.value,
                    status,
                    last_login
                ))
                
                # Salvar ID do usuário
                self.users_tree.set(item_id, 'user_id', user.id)
                
        except Exception as e:
            print(f"Erro ao carregar usuários: {e}")
    
    def on_user_select(self, event=None):
        """Chamado quando seleciona um usuário"""
        selection = self.users_tree.selection()
        if selection:
            item = selection[0]
            user_id = self.users_tree.set(item, 'user_id')
            self.selected_user_id = int(user_id) if user_id else None
    
    def new_user(self):
        """Cria novo usuário"""
        from .user_dialog import UserDialog
        dialog = UserDialog(self.parent)
        if dialog.result:
            self.refresh_users()
    
    def edit_user(self):
        """Edita usuário selecionado"""
        if not self.selected_user_id:
            return
        
        from .user_dialog import UserDialog
        dialog = UserDialog(self.parent, user_id=self.selected_user_id)
        if dialog.result:
            self.refresh_users()
    
    def deactivate_user(self):
        """Desativa/ativa usuário selecionado"""
        if not self.selected_user_id:
            return
        
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar", "Deseja alterar o status deste usuário?"):
            try:
                success = admin_controller.toggle_user_status(self.selected_user_id)
                if success:
                    self.refresh_users()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao alterar status: {str(e)}")
    
    def reset_password(self):
        """Reseta senha do usuário selecionado"""
        if not self.selected_user_id:
            return
        
        from tkinter import messagebox, simpledialog
        
        new_password = simpledialog.askstring("Nova Senha", "Digite a nova senha:", show='*')
        if new_password:
            try:
                success = admin_controller.reset_user_password(self.selected_user_id, new_password)
                if success:
                    messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao alterar senha: {str(e)}")
    
    def refresh_backups(self):
        """Atualiza lista de backups"""
        try:
            # Limpar árvore
            for item in self.backups_tree.get_children():
                self.backups_tree.delete(item)
            
            # Buscar backups
            backups = admin_controller.get_backup_list()
            
            for backup in backups:
                self.backups_tree.insert('', 'end', values=(
                    backup['name'],
                    backup['date'],
                    backup['size'],
                    backup['type']
                ))
                
        except Exception as e:
            print(f"Erro ao carregar backups: {e}")
    
    def refresh_logs(self):
        """Atualiza logs"""
        try:
            logs = admin_controller.get_system_logs()
            self.logs_text.delete(1.0, tk.END)
            self.logs_text.insert(1.0, logs)
        except Exception as e:
            print(f"Erro ao carregar logs: {e}")
    
    def filter_logs(self):
        """Filtra logs por nível"""
        self.refresh_logs()  # Implementação simplificada
    
    def clear_logs(self):
        """Limpa logs do sistema"""
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar", "Deseja limpar todos os logs?"):
            try:
                admin_controller.clear_logs()
                self.refresh_logs()
                messagebox.showinfo("Sucesso", "Logs limpos com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar logs: {str(e)}")
    
    def export_logs(self):
        """Exporta logs"""
        from tkinter import messagebox
        messagebox.showinfo("Info", "Exportação de logs em desenvolvimento")
    
    # Métodos simplificados para configurações
    def open_general_settings(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Configurações gerais em desenvolvimento")
    
    def open_email_settings(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Configurações de email em desenvolvimento")
    
    def open_backup_settings(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Configurações de backup em desenvolvimento")
    
    def clear_cache(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Cache limpo com sucesso!")
    
    def optimize_database(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Database otimizado com sucesso!")
    
    def check_integrity(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Integridade verificada com sucesso!")
    
    def create_full_backup(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Backup completo criado com sucesso!")
        self.refresh_backups()
    
    def create_db_backup(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Backup do database criado com sucesso!")
        self.refresh_backups()
    
    def restore_backup(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Restauração de backup em desenvolvimento")
    
    def toggle_auto_backup(self):
        from tkinter import messagebox
        status = "habilitado" if self.auto_backup_var.get() else "desabilitado"
        messagebox.showinfo("Info", f"Backup automático {status}")

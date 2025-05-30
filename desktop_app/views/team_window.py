"""
Janela de gerenciamento de equipes
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, List

from .base_window import BaseWindow
from desktop_app.controllers.team_controller import team_controller
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType


class TeamsWindow:
    """Janela de gerenciamento de equipes"""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent = parent_frame
        
        # Widgets principais
        self.search_var: Optional[tk.StringVar] = None
        self.teams_tree: Optional[ttk.Treeview] = None
        self.selected_team_id: Optional[int] = None
        
        # Frames
        self.toolbar_frame: Optional[ttk.Frame] = None
        self.teams_frame: Optional[ttk.Frame] = None
        self.details_frame: Optional[ttk.Frame] = None
    
    def setup_teams_view(self):
        """Configura a view de equipes"""
        # Limpar frame pai
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Título
        title_label = ttk.Label(self.parent, text="Gerenciamento de Equipes", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Toolbar
        self.setup_toolbar()
        
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20)
        
        # Painel esquerdo: Lista de equipes
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.setup_teams_list(left_panel)
        
        # Painel direito: Detalhes da equipe
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        
        self.setup_team_details(right_panel)
        
        # Carregar dados
        self.refresh_teams()
    
    def setup_toolbar(self):
        """Configura barra de ferramentas"""
        self.toolbar_frame = ttk.Frame(self.parent)
        self.toolbar_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Busca
        search_frame = ttk.Frame(self.toolbar_frame)
        search_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(0, 10))
        search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Botões
        button_frame = ttk.Frame(self.toolbar_frame)
        button_frame.pack(side="right")
        
        if auth_controller.has_permission(UserType.ORGANIZATION):
            ttk.Button(button_frame, text="Nova Equipe", 
                      command=self.new_team).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Editar", 
                      command=self.edit_team).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Excluir", 
                      command=self.delete_team).pack(side="left", padx=(0, 5))
        
        ttk.Button(button_frame, text="Atualizar", 
                  command=self.refresh_teams).pack(side="left")
    
    def setup_teams_list(self, parent: ttk.Frame):
        """Configura lista de equipes"""
        # Frame da lista
        list_frame = ttk.LabelFrame(parent, text="Equipes", padding="10")
        list_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = ("nome", "universidade", "atletas", "status")
        self.teams_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Cabeçalhos
        self.teams_tree.heading("nome", text="Nome")
        self.teams_tree.heading("universidade", text="Universidade")
        self.teams_tree.heading("atletas", text="Atletas")
        self.teams_tree.heading("status", text="Status")
        
        # Larguras
        self.teams_tree.column("nome", width=200)
        self.teams_tree.column("universidade", width=200)
        self.teams_tree.column("atletas", width=80)
        self.teams_tree.column("status", width=80)
        
        self.teams_tree.pack(fill="both", expand=True)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.teams_tree.yview)
        self.teams_tree.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side="right", fill="y")
        
        h_scroll = ttk.Scrollbar(list_frame, orient="horizontal", command=self.teams_tree.xview)
        self.teams_tree.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side="bottom", fill="x")
        
        # Bind para seleção
        self.teams_tree.bind("<<TreeviewSelect>>", self.on_team_select)
        self.teams_tree.bind("<Double-1>", self.on_team_double_click)
    
    def setup_team_details(self, parent: ttk.Frame):
        """Configura painel de detalhes da equipe"""
        self.details_frame = ttk.LabelFrame(parent, text="Detalhes da Equipe", padding="10")
        self.details_frame.pack(fill="both", expand=True)
        
        # Informações básicas
        info_frame = ttk.Frame(self.details_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        self.team_name_label = ttk.Label(info_frame, text="", font=("Arial", 12, "bold"))
        self.team_name_label.pack(anchor="w")
        
        self.team_university_label = ttk.Label(info_frame, text="")
        self.team_university_label.pack(anchor="w", pady=(5, 0))
        
        self.team_status_label = ttk.Label(info_frame, text="")
        self.team_status_label.pack(anchor="w", pady=(5, 0))
        
        # Lista de atletas
        athletes_label = ttk.Label(self.details_frame, text="Atletas:", font=("Arial", 10, "bold"))
        athletes_label.pack(anchor="w", pady=(0, 5))
        
        # Treeview de atletas
        athlete_columns = ("nome", "posicao", "numero")
        self.athletes_tree = ttk.Treeview(self.details_frame, columns=athlete_columns, 
                                        show="headings", height=8)
        
        self.athletes_tree.heading("nome", text="Nome")
        self.athletes_tree.heading("posicao", text="Posição")
        self.athletes_tree.heading("numero", text="Número")
        
        self.athletes_tree.column("nome", width=150)
        self.athletes_tree.column("posicao", width=100)
        self.athletes_tree.column("numero", width=60)
        
        self.athletes_tree.pack(fill="both", expand=True, pady=(0, 10))
        
        # Scrollbar para atletas
        athletes_scroll = ttk.Scrollbar(self.details_frame, orient="vertical", 
                                      command=self.athletes_tree.yview)
        self.athletes_tree.configure(yscrollcommand=athletes_scroll.set)
        athletes_scroll.pack(side="right", fill="y")
        
        # Botões de ação
        if auth_controller.has_permission(UserType.TEAM):
            action_frame = ttk.Frame(self.details_frame)
            action_frame.pack(fill="x")
            
            ttk.Button(action_frame, text="Gerenciar Atletas", 
                      command=self.manage_athletes).pack(fill="x", pady=(0, 5))
            ttk.Button(action_frame, text="Ver Estatísticas", 
                      command=self.view_statistics).pack(fill="x")
    
    def refresh_teams(self):
        """Atualiza lista de equipes"""
        try:
            # Limpar árvore
            for item in self.teams_tree.get_children():
                self.teams_tree.delete(item)
            
            # Buscar equipes
            teams = team_controller.get_all_teams()
            
            # Filtrar por busca se necessário
            search_term = self.search_var.get().lower() if self.search_var else ""
            if search_term:
                teams = [t for t in teams if search_term in t.name.lower() or 
                        search_term in t.university.lower()]
            
            # Adicionar na árvore
            for team in teams:
                athletes_count = len(team.get_athletes())
                status = "Ativa" if team.is_active else "Inativa"
                
                item_id = self.teams_tree.insert('', 'end', values=(
                    team.name,
                    team.university,
                    athletes_count,
                    status
                ))
                
                # Salvar ID da equipe no item
                self.teams_tree.set(item_id, 'team_id', team.id)
                
        except Exception as e:
            print(f"Erro ao carregar equipes: {e}")
    
    def on_search_change(self, event=None):
        """Chamado quando muda o texto de busca"""
        self.refresh_teams()
    
    def on_team_select(self, event=None):
        """Chamado quando seleciona uma equipe"""
        selection = self.teams_tree.selection()
        if not selection:
            self.clear_team_details()
            return
        
        item = selection[0]
        team_id = self.teams_tree.set(item, 'team_id')
        
        if team_id:
            self.selected_team_id = int(team_id)
            self.load_team_details(self.selected_team_id)
    
    def on_team_double_click(self, event=None):
        """Chamado quando clica duas vezes em uma equipe"""
        if self.selected_team_id:
            self.edit_team()
    
    def load_team_details(self, team_id: int):
        """Carrega detalhes da equipe selecionada"""
        try:
            team = team_controller.get_team_by_id(team_id)
            if not team:
                return
            
            # Atualizar informações básicas
            self.team_name_label.config(text=team.name)
            self.team_university_label.config(text=f"Universidade: {team.university}")
            status = "Ativa" if team.is_active else "Inativa"
            self.team_status_label.config(text=f"Status: {status}")
            
            # Limpar e carregar atletas
            for item in self.athletes_tree.get_children():
                self.athletes_tree.delete(item)
            
            athletes = team.get_athletes()
            for athlete in athletes:
                self.athletes_tree.insert('', 'end', values=(
                    athlete.full_name,
                    athlete.position or "N/A",
                    athlete.jersey_number or "N/A"
                ))
                
        except Exception as e:
            print(f"Erro ao carregar detalhes da equipe: {e}")
    
    def clear_team_details(self):
        """Limpa detalhes da equipe"""
        self.team_name_label.config(text="")
        self.team_university_label.config(text="")
        self.team_status_label.config(text="")
        
        for item in self.athletes_tree.get_children():
            self.athletes_tree.delete(item)
        
        self.selected_team_id = None
    
    def new_team(self):
        """Abre dialog para nova equipe"""
        from .team_dialog import TeamDialog
        dialog = TeamDialog(self.parent)
        if dialog.result:
            self.refresh_teams()
    
    def edit_team(self):
        """Edita equipe selecionada"""
        if not self.selected_team_id:
            return
        
        from .team_dialog import TeamDialog
        dialog = TeamDialog(self.parent, team_id=self.selected_team_id)
        if dialog.result:
            self.refresh_teams()
            self.load_team_details(self.selected_team_id)
    
    def delete_team(self):
        """Exclui equipe selecionada"""
        if not self.selected_team_id:
            return
        
        team = team_controller.get_team_by_id(self.selected_team_id)
        if not team:
            return
        
        # Confirmar exclusão
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar Exclusão", 
                              f"Deseja realmente excluir a equipe '{team.name}'?\n\n"
                              "Esta ação não pode ser desfeita."):
            try:
                success = team_controller.delete_team(self.selected_team_id)
                if success:
                    messagebox.showinfo("Sucesso", "Equipe excluída com sucesso!")
                    self.refresh_teams()
                    self.clear_team_details()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir a equipe.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir equipe: {str(e)}")
    
    def manage_athletes(self):
        """Abre janela de gerenciamento de atletas"""
        if not self.selected_team_id:
            return
        
        from .athletes_dialog import AthletesDialog
        dialog = AthletesDialog(self.parent, team_id=self.selected_team_id)
        if dialog.result:
            self.load_team_details(self.selected_team_id)
    
    def view_statistics(self):
        """Exibe estatísticas da equipe"""
        if not self.selected_team_id:
            return
        
        from .team_stats_dialog import TeamStatsDialog
        dialog = TeamStatsDialog(self.parent, team_id=self.selected_team_id)


### desktop_app/views/competitions_window.py


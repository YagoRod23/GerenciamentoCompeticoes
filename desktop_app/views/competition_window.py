"""
Janela de gerenciamento de competições
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional

from desktop_app.controllers.competition_controller import competition_controller
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType, CompetitionStatus


class CompetitionsWindow:
    """Janela de gerenciamento de competições"""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent = parent_frame
        
        # Widgets principais
        self.search_var: Optional[tk.StringVar] = None
        self.status_filter_var: Optional[tk.StringVar] = None
        self.competitions_tree: Optional[ttk.Treeview] = None
        self.selected_competition_id: Optional[int] = None
        
        # Frames de detalhes
        self.details_frame: Optional[ttk.Frame] = None
        self.standings_tree: Optional[ttk.Treeview] = None
    
    def setup_competitions_view(self):
        """Configura a view de competições"""
        # Limpar frame pai
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Título
        title_label = ttk.Label(self.parent, text="Gerenciamento de Competições", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Toolbar
        self.setup_toolbar()
        
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20)
        
        # Painel esquerdo: Lista de competições
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.setup_competitions_list(left_panel)
        
        # Painel direito: Detalhes e classificação
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.setup_competition_details(right_panel)
        
        # Carregar dados
        self.refresh_competitions()
    
    def setup_toolbar(self):
        """Configura barra de ferramentas"""
        toolbar_frame = ttk.Frame(self.parent)
        toolbar_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Filtros
        filters_frame = ttk.Frame(toolbar_frame)
        filters_frame.pack(side="left", fill="x", expand=True)
        
        # Busca
        ttk.Label(filters_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filters_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=(0, 15))
        search_entry.bind("<KeyRelease>", self.on_filter_change)
        
        # Filtro por status
        ttk.Label(filters_frame, text="Status:").pack(side="left", padx=(0, 5))
        
        self.status_filter_var = tk.StringVar(value="TODOS")
        status_combo = ttk.Combobox(filters_frame, textvariable=self.status_filter_var,
                                  values=["TODOS", "PLANEJADA", "EM_ANDAMENTO", "FINALIZADA"],
                                  state="readonly", width=15)
        status_combo.pack(side="left")
        status_combo.bind("<<ComboboxSelected>>", self.on_filter_change)
        
        # Botões
        button_frame = ttk.Frame(toolbar_frame)
        button_frame.pack(side="right")
        
        if auth_controller.has_permission(UserType.ORGANIZATION):
            ttk.Button(button_frame, text="Nova Competição", 
                      command=self.new_competition).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Editar", 
                      command=self.edit_competition).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Gerenciar", 
                      command=self.manage_competition).pack(side="left", padx=(0, 5))
        
        ttk.Button(button_frame, text="Atualizar", 
                  command=self.refresh_competitions).pack(side="left")
    
    def setup_competitions_list(self, parent: ttk.Frame):
        """Configura lista de competições"""
        list_frame = ttk.LabelFrame(parent, text="Competições", padding="10")
        list_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = ("nome", "temporada", "tipo", "status", "equipes")
        self.competitions_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Cabeçalhos
        self.competitions_tree.heading("nome", text="Nome")
        self.competitions_tree.heading("temporada", text="Temporada")
        self.competitions_tree.heading("tipo", text="Tipo")
        self.competitions_tree.heading("status", text="Status")
        self.competitions_tree.heading("equipes", text="Equipes")
        
        # Larguras
        self.competitions_tree.column("nome", width=200)
        self.competitions_tree.column("temporada", width=100)
        self.competitions_tree.column("tipo", width=120)
        self.competitions_tree.column("status", width=120)
        self.competitions_tree.column("equipes", width=80)
        
        self.competitions_tree.pack(fill="both", expand=True)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient="vertical", 
                               command=self.competitions_tree.yview)
        self.competitions_tree.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side="right", fill="y")
        
        # Bind para seleção
        self.competitions_tree.bind("<<TreeviewSelect>>", self.on_competition_select)
        self.competitions_tree.bind("<Double-1>", self.on_competition_double_click)
    
    def setup_competition_details(self, parent: ttk.Frame):
        """Configura painel de detalhes da competição"""
        self.details_frame = ttk.LabelFrame(parent, text="Detalhes da Competição", padding="10")
        self.details_frame.pack(fill="both", expand=True)
        
        # Informações básicas
        info_frame = ttk.Frame(self.details_frame)
        info_frame.pack(fill="x", pady=(0, 15))
        
        self.comp_name_label = ttk.Label(info_frame, text="", font=("Arial", 12, "bold"))
        self.comp_name_label.pack(anchor="w")
        
        self.comp_season_label = ttk.Label(info_frame, text="")
        self.comp_season_label.pack(anchor="w", pady=(2, 0))
        
        self.comp_type_label = ttk.Label(info_frame, text="")
        self.comp_type_label.pack(anchor="w", pady=(2, 0))
        
        self.comp_status_label = ttk.Label(info_frame, text="")
        self.comp_status_label.pack(anchor="w", pady=(2, 0))
        
        self.comp_dates_label = ttk.Label(info_frame, text="")
        self.comp_dates_label.pack(anchor="w", pady=(2, 0))
        
        # Notebook para classificação e outras informações
        self.details_notebook = ttk.Notebook(self.details_frame)
        self.details_notebook.pack(fill="both", expand=True)
        
        # Aba classificação
        standings_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(standings_frame, text="Classificação")
        
        # Treeview de classificação
        standings_columns = ("pos", "equipe", "j", "v", "e", "d", "gp", "gc", "sg", "pts")
        self.standings_tree = ttk.Treeview(standings_frame, columns=standings_columns,
                                         show="headings")
        
        # Cabeçalhos da classificação
        headers = {
            "pos": "Pos", "equipe": "Equipe", "j": "J", "v": "V", "e": "E", "d": "D",
            "gp": "GP", "gc": "GC", "sg": "SG", "pts": "Pts"
        }
        
        for col, header in headers.items():
            self.standings_tree.heading(col, text=header)
            if col == "equipe":
                self.standings_tree.column(col, width=120)
            else:
                self.standings_tree.column(col, width=40)
        
        self.standings_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar para classificação
        standings_scroll = ttk.Scrollbar(standings_frame, orient="vertical",
                                       command=self.standings_tree.yview)
        self.standings_tree.configure(yscrollcommand=standings_scroll.set)
        standings_scroll.pack(side="right", fill="y")
        
        # Aba informações gerais
        info_tab_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(info_tab_frame, text="Informações")
        
        self.info_text = tk.Text(info_tab_frame, height=10, wrap="word", state="disabled")
        self.info_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        info_scroll = ttk.Scrollbar(info_tab_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        info_scroll.pack(side="right", fill="y")
    
    def refresh_competitions(self):
        """Atualiza lista de competições"""
        try:
            # Limpar árvore
            for item in self.competitions_tree.get_children():
                self.competitions_tree.delete(item)
            
            # Buscar competições
            competitions = competition_controller.get_all_competitions()
            
            # Aplicar filtros
            search_term = self.search_var.get().lower() if self.search_var else ""
            status_filter = self.status_filter_var.get() if self.status_filter_var else "TODOS"
            
            for competition in competitions:
                # Filtro de busca
                if search_term and search_term not in competition.name.lower():
                    continue
                
                # Filtro de status
                if status_filter != "TODOS" and competition.status.value != status_filter:
                    continue
                
                # Contar equipes participantes
                teams_count = len(competition.get_participating_teams())
                
                item_id = self.competitions_tree.insert('', 'end', values=(
                    competition.name,
                    competition.season,
                    competition.competition_type.value,
                    competition.status.value,
                    teams_count
                ))
                
                # Salvar ID da competição
                self.competitions_tree.set(item_id, 'competition_id', competition.id)
                
        except Exception as e:
            print(f"Erro ao carregar competições: {e}")
    
    def on_filter_change(self, event=None):
        """Chamado quando muda filtros"""
        self.refresh_competitions()
    
    def on_competition_select(self, event=None):
        """Chamado quando seleciona uma competição"""
        selection = self.competitions_tree.selection()
        if not selection:
            self.clear_competition_details()
            return
        
        item = selection[0]
        comp_id = self.competitions_tree.set(item, 'competition_id')
        
        if comp_id:
            self.selected_competition_id = int(comp_id)
            self.load_competition_details(self.selected_competition_id)
    
    def on_competition_double_click(self, event=None):
        """Chamado quando clica duas vezes em uma competição"""
        if self.selected_competition_id and auth_controller.has_permission(UserType.ORGANIZATION):
            self.edit_competition()
    
    def load_competition_details(self, competition_id: int):
        """Carrega detalhes da competição selecionada"""
        try:
            competition = competition_controller.get_competition_by_id(competition_id)
            if not competition:
                return
            
            # Atualizar informações básicas
            self.comp_name_label.config(text=competition.name)
            self.comp_season_label.config(text=f"Temporada: {competition.season}")
            self.comp_type_label.config(text=f"Tipo: {competition.competition_type.value}")
            self.comp_status_label.config(text=f"Status: {competition.status.value}")
            
            dates_text = f"Início: {competition.start_date.strftime('%d/%m/%Y')}"
            if competition.end_date:
                dates_text += f" | Fim: {competition.end_date.strftime('%d/%m/%Y')}"
            self.comp_dates_label.config(text=dates_text)
            
            # Carregar classificação
            self.load_standings(competition_id)
            
            # Carregar informações detalhadas
            self.load_competition_info(competition)
            
        except Exception as e:
            print(f"Erro ao carregar detalhes da competição: {e}")
    
    def load_standings(self, competition_id: int):
        """Carrega classificação da competição"""
        try:
            # Limpar árvore de classificação
            for item in self.standings_tree.get_children():
                self.standings_tree.delete(item)
            
            # Buscar classificação
            standings = competition_controller.get_standings(competition_id)
            
            for i, standing in enumerate(standings, 1):
                from desktop_app.controllers.team_controller import team_controller
                team = team_controller.get_team_by_id(standing.team_id)
                
                self.standings_tree.insert('', 'end', values=(
                    i,  # Posição
                    team.name if team else "N/A",
                    standing.games_played,
                    standing.wins,
                    standing.draws,
                    standing.losses,
                    standing.goals_for,
                    standing.goals_against,
                    standing.goal_difference,
                    standing.points
                ))
                
        except Exception as e:
            print(f"Erro ao carregar classificação: {e}")
    
    def load_competition_info(self, competition):
        """Carrega informações detalhadas da competição"""
        try:
            self.info_text.config(state="normal")
            self.info_text.delete(1.0, tk.END)
            
            info = f"""Nome: {competition.name}
Temporada: {competition.season}
Tipo: {competition.competition_type.value}
Status: {competition.status.value}

Data de Início: {competition.start_date.strftime('%d/%m/%Y')}
Data de Fim: {competition.end_date.strftime('%d/%m/%Y') if competition.end_date else 'Não definida'}

Descrição:
{competition.description or 'Nenhuma descrição disponível.'}

Regulamento:
{competition.rules or 'Nenhum regulamento disponível.'}
"""
            
            self.info_text.insert(1.0, info)
            self.info_text.config(state="disabled")
            
        except Exception as e:
            print(f"Erro ao carregar informações da competição: {e}")
    
    def clear_competition_details(self):
        """Limpa detalhes da competição"""
        self.comp_name_label.config(text="")
        self.comp_season_label.config(text="")
        self.comp_type_label.config(text="")
        self.comp_status_label.config(text="")
        self.comp_dates_label.config(text="")
        
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)
        
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state="disabled")
        
        self.selected_competition_id = None
    
    def new_competition(self):
        """Abre dialog para nova competição"""
        from .competition_dialog import CompetitionDialog
        dialog = CompetitionDialog(self.parent)
        if dialog.result:
            self.refresh_competitions()
    
    def edit_competition(self):
        """Edita competição selecionada"""
        if not self.selected_competition_id:
            return
        
        from .competition_dialog import CompetitionDialog
        dialog = CompetitionDialog(self.parent, competition_id=self.selected_competition_id)
        if dialog.result:
            self.refresh_competitions()
            self.load_competition_details(self.selected_competition_id)
    
    def manage_competition(self):
        """Abre janela de gerenciamento da competição"""
        if not self.selected_competition_id:
            return
        
        from .competition_management_dialog import CompetitionManagementDialog
        dialog = CompetitionManagementDialog(self.parent, competition_id=self.selected_competition_id)
        if dialog.result:
            self.load_competition_details(self.selected_competition_id)

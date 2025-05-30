"""
Janela de gerenciamento de jogos
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Optional

from desktop_app.controllers.game_controller import game_controller
from desktop_app.controllers.competition_controller import competition_controller
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType, GameStatus


class GamesWindow:
    """Janela de gerenciamento de jogos"""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent = parent_frame
        
        # Widgets principais
        self.competition_filter_var: Optional[tk.StringVar] = None
        self.status_filter_var: Optional[tk.StringVar] = None
        self.games_tree: Optional[ttk.Treeview] = None
        self.selected_game_id: Optional[int] = None
        
        # Frames de detalhes
        self.details_frame: Optional[ttk.Frame] = None
    
    def setup_games_view(self):
        """Configura a view de jogos"""
        # Limpar frame pai
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Título
        title_label = ttk.Label(self.parent, text="Gerenciamento de Jogos", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Toolbar
        self.setup_toolbar()
        
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20)
        
        # Painel superior: Lista de jogos
        top_panel = ttk.Frame(main_frame)
        top_panel.pack(fill="both", expand=True, pady=(0, 10))
        
        self.setup_games_list(top_panel)
        
        # Painel inferior: Detalhes do jogo
        bottom_panel = ttk.Frame(main_frame)
        bottom_panel.pack(fill="x")
        
        self.setup_game_details(bottom_panel)
        
        # Carregar dados
        self.refresh_games()
    
    def setup_toolbar(self):
        """Configura barra de ferramentas"""
        toolbar_frame = ttk.Frame(self.parent)
        toolbar_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Filtros
        filters_frame = ttk.Frame(toolbar_frame)
        filters_frame.pack(side="left", fill="x", expand=True)
        
        # Filtro por competição
        ttk.Label(filters_frame, text="Competição:").pack(side="left", padx=(0, 5))
        
        self.competition_filter_var = tk.StringVar(value="TODAS")
        self.competition_combo = ttk.Combobox(filters_frame, textvariable=self.competition_filter_var,
                                            state="readonly", width=20)
        self.competition_combo.pack(side="left", padx=(0, 15))
        self.competition_combo.bind("<<ComboboxSelected>>", self.on_filter_change)
        
        # Filtro por status
        ttk.Label(filters_frame, text="Status:").pack(side="left", padx=(0, 5))
        
        self.status_filter_var = tk.StringVar(value="TODOS")
        status_combo = ttk.Combobox(filters_frame, textvariable=self.status_filter_var,
                                  values=["TODOS", "AGENDADO", "EM_ANDAMENTO", "FINALIZADO", "CANCELADO"],
                                  state="readonly", width=15)
        status_combo.pack(side="left")
        status_combo.bind("<<ComboboxSelected>>", self.on_filter_change)
        
        # Botões
        button_frame = ttk.Frame(toolbar_frame)
        button_frame.pack(side="right")
        
        if auth_controller.has_permission(UserType.ORGANIZATION):
            ttk.Button(button_frame, text="Novo Jogo", 
                      command=self.new_game).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Editar", 
                      command=self.edit_game).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Registrar Resultado", 
                      command=self.register_result).pack(side="left", padx=(0, 5))
        
        ttk.Button(button_frame, text="Atualizar", 
                  command=self.refresh_games).pack(side="left")
        
        # Carregar competições para o filtro
        self.load_competitions_filter()
    
    def setup_games_list(self, parent: ttk.Frame):
        """Configura lista de jogos"""
        list_frame = ttk.LabelFrame(parent, text="Jogos", padding="10")
        list_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = ("data", "hora", "competicao", "equipe_casa", "equipe_visitante", 
                  "resultado", "status")
        self.games_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Cabeçalhos
        self.games_tree.heading("data", text="Data")
        self.games_tree.heading("hora", text="Hora")
        self.games_tree.heading("competicao", text="Competição")
        self.games_tree.heading("equipe_casa", text="Casa")
        self.games_tree.heading("equipe_visitante", text="Visitante")
        self.games_tree.heading("resultado", text="Resultado")
        self.games_tree.heading("status", text="Status")
        
        # Larguras
        self.games_tree.column("data", width=80)
        self.games_tree.column("hora", width=60)
        self.games_tree.column("competicao", width=150)
        self.games_tree.column("equipe_casa", width=120)
        self.games_tree.column("equipe_visitante", width=120)
        self.games_tree.column("resultado", width=80)
        self.games_tree.column("status", width=100)
        
        self.games_tree.pack(fill="both", expand=True)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.games_tree.yview)
        self.games_tree.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side="right", fill="y")
        
        h_scroll = ttk.Scrollbar(list_frame, orient="horizontal", command=self.games_tree.xview)
        self.games_tree.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side="bottom", fill="x")
        
        # Bind para seleção
        self.games_tree.bind("<<TreeviewSelect>>", self.on_game_select)
        self.games_tree.bind("<Double-1>", self.on_game_double_click)
    
    def setup_game_details(self, parent: ttk.Frame):
        """Configura painel de detalhes do jogo"""
        self.details_frame = ttk.LabelFrame(parent, text="Detalhes do Jogo", padding="10")
        self.details_frame.pack(fill="x")
        
        # Frame principal de detalhes
        details_main = ttk.Frame(self.details_frame)
        details_main.pack(fill="x")
        
        # Coluna esquerda - Informações básicas
        left_column = ttk.Frame(details_main)
        left_column.pack(side="left", fill="x", expand=True)
        
        self.game_info_frame = ttk.Frame(left_column)
        self.game_info_frame.pack(fill="x", pady=(0, 10))
        
        self.game_competition_label = ttk.Label(self.game_info_frame, text="", 
                                              font=("Arial", 10, "bold"))
        self.game_competition_label.pack(anchor="w")
        
        self.game_teams_label = ttk.Label(self.game_info_frame, text="", 
                                        font=("Arial", 12, "bold"))
        self.game_teams_label.pack(anchor="w", pady=(5, 0))
        
        self.game_datetime_label = ttk.Label(self.game_info_frame, text="")
        self.game_datetime_label.pack(anchor="w")
        
        self.game_location_label = ttk.Label(self.game_info_frame, text="")
        self.game_location_label.pack(anchor="w")
        
        self.game_status_label = ttk.Label(self.game_info_frame, text="")
        self.game_status_label.pack(anchor="w")
        
        # Coluna direita - Resultado e estatísticas
        right_column = ttk.Frame(details_main)
        right_column.pack(side="right", fill="x", expand=True)
        
        # Frame de resultado
        result_frame = ttk.LabelFrame(right_column, text="Resultado", padding="5")
        result_frame.pack(fill="x")
        
        self.result_label = ttk.Label(result_frame, text="", font=("Arial", 14, "bold"))
        self.result_label.pack()
        
        # Frame de ações rápidas
        if auth_controller.has_permission(UserType.ORGANIZATION):
            actions_frame = ttk.Frame(right_column)
            actions_frame.pack(fill="x", pady=(10, 0))
            
            self.quick_actions_frame = ttk.LabelFrame(actions_frame, text="Ações Rápidas", padding="5")
            self.quick_actions_frame.pack(fill="x")
            
            # Botões serão criados dinamicamente baseados no status do jogo
    
    def load_competitions_filter(self):
        """Carrega competições para o filtro"""
        try:
            competitions = competition_controller.get_all_competitions()
            comp_names = ["TODAS"] + [comp.name for comp in competitions]
            self.competition_combo.config(values=comp_names)
        except Exception as e:
            print(f"Erro ao carregar competições: {e}")
    
    def refresh_games(self):
        """Atualiza lista de jogos"""
        try:
            # Limpar árvore
            for item in self.games_tree.get_children():
                self.games_tree.delete(item)
            
            # Buscar jogos
            games = game_controller.get_all_games()
            
            # Aplicar filtros
            comp_filter = self.competition_filter_var.get() if self.competition_filter_var else "TODAS"
            status_filter = self.status_filter_var.get() if self.status_filter_var else "TODOS"
            
            for game in games:
                # Filtro de competição
                if comp_filter != "TODAS":
                    competition = competition_controller.get_competition_by_id(game.competition_id)
                    if not competition or competition.name != comp_filter:
                        continue
                
                # Filtro de status
                if status_filter != "TODOS" and game.status.value != status_filter:
                    continue
                
                # Obter dados para exibição
                from desktop_app.controllers.team_controller import team_controller
                
                home_team = team_controller.get_team_by_id(game.home_team_id)
                away_team = team_controller.get_team_by_id(game.away_team_id)
                competition = competition_controller.get_competition_by_id(game.competition_id)
                
                # Formatrar resultado
                if game.home_score is not None and game.away_score is not None:
                    result = f"{game.home_score} x {game.away_score}"
                else:
                    result = "- x -"
                
                item_id = self.games_tree.insert('', 'end', values=(
                    game.game_date.strftime('%d/%m/%Y'),
                    game.game_time.strftime('%H:%M') if game.game_time else "",
                    competition.name if competition else "N/A",
                    home_team.name if home_team else "N/A",
                    away_team.name if away_team else "N/A",
                    result,
                    game.status.value
                ))
                
                # Salvar ID do jogo
                self.games_tree.set(item_id, 'game_id', game.id)
                
        except Exception as e:
            print(f"Erro ao carregar jogos: {e}")
    
    def on_filter_change(self, event=None):
        """Chamado quando muda filtros"""
        self.refresh_games()
    
    def on_game_select(self, event=None):
        """Chamado quando seleciona um jogo"""
        selection = self.games_tree.selection()
        if not selection:
            self.clear_game_details()
            return
        
        item = selection[0]
        game_id = self.games_tree.set(item, 'game_id')
        
        if game_id:
            self.selected_game_id = int(game_id)
            self.load_game_details(self.selected_game_id)
    
    def on_game_double_click(self, event=None):
        """Chamado quando clica duas vezes em um jogo"""
        if self.selected_game_id and auth_controller.has_permission(UserType.ORGANIZATION):
            self.edit_game()
    
    def load_game_details(self, game_id: int):
        """Carrega detalhes do jogo selecionado"""
        try:
            game = game_controller.get_game_by_id(game_id)
            if not game:
                return
            
            from desktop_app.controllers.team_controller import team_controller
            
            # Obter dados relacionados
            home_team = team_controller.get_team_by_id(game.home_team_id)
            away_team = team_controller.get_team_by_id(game.away_team_id)
            competition = competition_controller.get_competition_by_id(game.competition_id)
            
            # Atualizar informações básicas
            self.game_competition_label.config(text=f"Competição: {competition.name if competition else 'N/A'}")
            
            teams_text = f"{home_team.name if home_team else 'N/A'} vs {away_team.name if away_team else 'N/A'}"
            self.game_teams_label.config(text=teams_text)
            
            datetime_text = f"Data: {game.game_date.strftime('%d/%m/%Y')}"
            if game.game_time:
                datetime_text += f" às {game.game_time.strftime('%H:%M')}"
            self.game_datetime_label.config(text=datetime_text)
            
            location_text = f"Local: {game.location or 'Não informado'}"
            self.game_location_label.config(text=location_text)
            
            status_text = f"Status: {game.status.value}"
            self.game_status_label.config(text=status_text)
            
            # Atualizar resultado
            if game.home_score is not None and game.away_score is not None:
                result_text = f"{game.home_score} x {game.away_score}"
                
                # Determinar vencedor
                if game.home_score > game.away_score:
                    result_text += f"\nVitória: {home_team.name if home_team else 'Casa'}"
                elif game.away_score > game.home_score:
                    result_text += f"\nVitória: {away_team.name if away_team else 'Visitante'}"
                else:
                    result_text += "\nEmpate"
            else:
                result_text = "Aguardando resultado"
            
            self.result_label.config(text=result_text)
            
            # Atualizar ações rápidas
            self.update_quick_actions(game)
            
        except Exception as e:
            print(f"Erro ao carregar detalhes do jogo: {e}")
    
    def update_quick_actions(self, game):
        """Atualiza botões de ações rápidas baseado no status do jogo"""
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return
        
        # Limpar botões existentes
        for widget in self.quick_actions_frame.winfo_children():
            widget.destroy()
        
        if game.status == GameStatus.AGENDADO:
            ttk.Button(self.quick_actions_frame, text="Iniciar Jogo",
                      command=self.start_game).pack(fill="x", pady=1)
            ttk.Button(self.quick_actions_frame, text="Cancelar",
                      command=self.cancel_game).pack(fill="x", pady=1)
        
        elif game.status == GameStatus.EM_ANDAMENTO:
            ttk.Button(self.quick_actions_frame, text="Finalizar Jogo",
                      command=self.finish_game).pack(fill="x", pady=1)
            ttk.Button(self.quick_actions_frame, text="Registrar Eventos",
                      command=self.register_events).pack(fill="x", pady=1)
        
        elif game.status == GameStatus.FINALIZADO:
            ttk.Button(self.quick_actions_frame, text="Ver Relatório",
                      command=self.view_game_report).pack(fill="x", pady=1)
            ttk.Button(self.quick_actions_frame, text="Editar Resultado",
                      command=self.edit_result).pack(fill="x", pady=1)
    
    def clear_game_details(self):
        """Limpa detalhes do jogo"""
        self.game_competition_label.config(text="")
        self.game_teams_label.config(text="")
        self.game_datetime_label.config(text="")
        self.game_location_label.config(text="")
        self.game_status_label.config(text="")
        self.result_label.config(text="")
        
        # Limpar ações rápidas
        for widget in self.quick_actions_frame.winfo_children():
            widget.destroy()
        
        self.selected_game_id = None
    
    def new_game(self):
        """Abre dialog para novo jogo"""
        from .game_dialog import GameDialog
        dialog = GameDialog(self.parent)
        if dialog.result:
            self.refresh_games()
    
    def edit_game(self):
        """Edita jogo selecionado"""
        if not self.selected_game_id:
            return
        
        from .game_dialog import GameDialog
        dialog = GameDialog(self.parent, game_id=self.selected_game_id)
        if dialog.result:
            self.refresh_games()
            self.load_game_details(self.selected_game_id)
    
    def register_result(self):
        """Registra resultado do jogo"""
        if not self.selected_game_id:
            return
        
        from .game_result_dialog import GameResultDialog
        dialog = GameResultDialog(self.parent, game_id=self.selected_game_id)
        if dialog.result:
            self.refresh_games()
            self.load_game_details(self.selected_game_id)
    
    def start_game(self):
        """Inicia o jogo"""
        if not self.selected_game_id:
            return
        
        try:
            success = game_controller.start_game(self.selected_game_id)
            if success:
                self.refresh_games()
                self.load_game_details(self.selected_game_id)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Erro", f"Erro ao iniciar jogo: {str(e)}")
    
    def finish_game(self):
        """Finaliza o jogo"""
        if not self.selected_game_id:
            return
        
        self.register_result()
    
    def cancel_game(self):
        """Cancela o jogo"""
        if not self.selected_game_id:
            return
        
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar", "Deseja cancelar este jogo?"):
            try:
                success = game_controller.cancel_game(self.selected_game_id)
                if success:
                    self.refresh_games()
                    self.load_game_details(self.selected_game_id)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cancelar jogo: {str(e)}")
    
    def register_events(self):
        """Registra eventos do jogo"""
        if not self.selected_game_id:
            return
        
        from .game_events_dialog import GameEventsDialog
        dialog = GameEventsDialog(self.parent, game_id=self.selected_game_id)
    
    def view_game_report(self):
        """Exibe relatório do jogo"""
        if not self.selected_game_id:
            return
        
        from .game_report_dialog import GameReportDialog
        dialog = GameReportDialog(self.parent, game_id=self.selected_game_id)
    
    def edit_result(self):
        """Edita resultado do jogo"""
        self.register_result()


### desktop_app/views/reports_window.py


"""
Janela do dashboard principal
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
from typing import Optional, List

from .base_window import BaseWindow
from desktop_app.controllers.team_controller import team_controller
from desktop_app.controllers.competition_controller import competition_controller
from desktop_app.controllers.game_controller import game_controller
from desktop_app.controllers.auth_controller import auth_controller
from database.models import GameStatus, UserType


class DashboardWindow:
    """Dashboard principal do sistema"""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent = parent_frame
        
        # Widgets principais
        self.stats_frame: Optional[ttk.Frame] = None
        self.games_frame: Optional[ttk.Frame] = None
        self.standings_frame: Optional[ttk.Frame] = None
        self.recent_frame: Optional[ttk.Frame] = None
    
    def setup_dashboard(self):
        """Configura o dashboard"""
        # Limpar frame pai
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Frame principal com scroll
        main_canvas = tk.Canvas(self.parent)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = ttk.Label(scrollable_frame, text="Dashboard", 
                               style="Title.TLabel")
        title_label.pack(pady=(10, 20))
        
        # Container principal
        container = ttk.Frame(scrollable_frame)
        container.pack(fill="both", expand=True, padx=20)
        
        # Primeira linha: Estatísticas gerais
        self.setup_stats_section(container)
        
        # Segunda linha: Jogos e Standings
        self.setup_games_and_standings(container)
        
        # Terceira linha: Atividades recentes
        self.setup_recent_activities(container)
        
        # Carregar dados
        self.refresh_data()
    
    def setup_stats_section(self, parent: ttk.Frame):
        """Configura seção de estatísticas"""
        # Frame das estatísticas
        self.stats_frame = ttk.LabelFrame(parent, text="Resumo Geral", padding="10")
        self.stats_frame.pack(fill="x", pady=(0, 20))
        
        # Grid de estatísticas
        stats_grid = ttk.Frame(self.stats_frame)
        stats_grid.pack(fill="x")
        
        # Configurar colunas
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        
        # Cards de estatísticas
        self.create_stat_card(stats_grid, "Equipes Ativas", "0", 0, 0, "#2E86AB")
        self.create_stat_card(stats_grid, "Competições", "0", 0, 1, "#A23B72")
        self.create_stat_card(stats_grid, "Jogos Hoje", "0", 0, 2, "#5CB85C")
        self.create_stat_card(stats_grid, "Jogos Esta Semana", "0", 0, 3, "#F0AD4E")
    
    def create_stat_card(self, parent: ttk.Frame, title: str, value: str, 
                        row: int, col: int, color: str):
        """Cria um card de estatística"""
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Título
        title_label = ttk.Label(card_frame, text=title, style="Subtitle.TLabel")
        title_label.pack(pady=(10, 5))
        
        # Valor
        value_label = ttk.Label(card_frame, text=value, font=("Arial", 24, "bold"))
        value_label.pack(pady=(0, 10))
        
        # Salvar referência para atualização
        setattr(self, f"{title.lower().replace(' ', '_')}_label", value_label)
    
    def setup_games_and_standings(self, parent: ttk.Frame):
        """Configura seção de jogos e classificação"""
        # Frame horizontal
        games_standings_frame = ttk.Frame(parent)
        games_standings_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Jogos próximos (lado esquerdo)
        self.games_frame = ttk.LabelFrame(games_standings_frame, text="Próximos Jogos", padding="10")
        self.games_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Treeview para jogos
        games_columns = ("data", "hora", "casa", "visitante", "competicao")
        self.games_tree = ttk.Treeview(self.games_frame, columns=games_columns, 
                                      show="headings", height=8)
        
        # Cabeçalhos
        self.games_tree.heading("data", text="Data")
        self.games_tree.heading("hora", text="Hora")
        self.games_tree.heading("casa", text="Casa")
        self.games_tree.heading("visitante", text="Visitante")
        self.games_tree.heading("competicao", text="Competição")
        
        # Larguras das colunas
        self.games_tree.column("data", width=80)
        self.games_tree.column("hora", width=60)
        self.games_tree.column("casa", width=120)
        self.games_tree.column("visitante", width=120)
        self.games_tree.column("competicao", width=100)
        
        self.games_tree.pack(fill="both", expand=True)
        
        # Scrollbar para jogos
        games_scroll = ttk.Scrollbar(self.games_frame, orient="vertical", 
                                   command=self.games_tree.yview)
        self.games_tree.configure(yscrollcommand=games_scroll.set)
        games_scroll.pack(side="right", fill="y")
        
        # Classificação (lado direito)
        self.standings_frame = ttk.LabelFrame(games_standings_frame, text="Classificação", padding="10")
        self.standings_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Combobox para seleção de competição
        comp_label = ttk.Label(self.standings_frame, text="Competição:")
        comp_label.pack(anchor="w")
        
        self.competition_var = tk.StringVar()
        self.competition_combo = ttk.Combobox(self.standings_frame, textvariable=self.competition_var,
                                            state="readonly", width=30)
        self.competition_combo.pack(fill="x", pady=(0, 10))
        self.competition_combo.bind("<<ComboboxSelected>>", self.on_competition_change)
        
        # Treeview para classificação
        standings_columns = ("pos", "equipe", "j", "v", "e", "d", "gp", "gc", "sg", "pts")
        self.standings_tree = ttk.Treeview(self.standings_frame, columns=standings_columns,
                                         show="headings", height=8)
        
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
        
        self.standings_tree.pack(fill="both", expand=True)
        
        # Scrollbar para classificação
        standings_scroll = ttk.Scrollbar(self.standings_frame, orient="vertical",
                                       command=self.standings_tree.yview)
        self.standings_tree.configure(yscrollcommand=standings_scroll.set)
        standings_scroll.pack(side="right", fill="y")
    
    def setup_recent_activities(self, parent: ttk.Frame):
        """Configura seção de atividades recentes"""
        self.recent_frame = ttk.LabelFrame(parent, text="Atividades Recentes", padding="10")
        self.recent_frame.pack(fill="x", pady=(0, 20))
        
        # Treeview para atividades
        recent_columns = ("data", "tipo", "descricao")
        self.recent_tree = ttk.Treeview(self.recent_frame, columns=recent_columns,
                                      show="headings", height=6)
        
        # Cabeçalhos
        self.recent_tree.heading("data", text="Data/Hora")
        self.recent_tree.heading("tipo", text="Tipo")
        self.recent_tree.heading("descricao", text="Descrição")
        
        # Larguras
        self.recent_tree.column("data", width=120)
        self.recent_tree.column("tipo", width=100)
        self.recent_tree.column("descricao", width=400)
        
        self.recent_tree.pack(fill="both", expand=True)
        
        # Scrollbar
        recent_scroll = ttk.Scrollbar(self.recent_frame, orient="vertical",
                                    command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=recent_scroll.set)
        recent_scroll.pack(side="right", fill="y")
    
    def refresh_data(self):
        """Atualiza todos os dados do dashboard"""
        try:
            self.update_statistics()
            self.update_games()
            self.update_competitions()
            self.update_recent_activities()
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")
    
    def update_statistics(self):
        """Atualiza estatísticas gerais"""
        try:
            # Contar equipes ativas
            teams = team_controller.get_all_teams()
            active_teams = len([t for t in teams if t.is_active])
            
            # Contar competições
            competitions = competition_controller.get_all_competitions()
            total_competitions = len(competitions)
            
            # Jogos hoje
            today = date.today()
            today_games = game_controller.get_games_by_date(today)
            games_today = len(today_games)
            
            # Jogos esta semana
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            week_games = game_controller.get_games(date_from=week_start, date_to=week_end)
            games_week = len(week_games)
            
            # Atualizar labels
            if hasattr(self, 'equipes_ativas_label'):
                self.equipes_ativas_label.config(text=str(active_teams))
            if hasattr(self, 'competições_label'):
                self.competições_label.config(text=str(total_competitions))
            if hasattr(self, 'jogos_hoje_label'):
                self.jogos_hoje_label.config(text=str(games_today))
            if hasattr(self, 'jogos_esta_semana_label'):
                self.jogos_esta_semana_label.config(text=str(games_week))
                
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def update_games(self):
        """Atualiza lista de próximos jogos"""
        try:
            # Limpar árvore
            for item in self.games_tree.get_children():
                self.games_tree.delete(item)
            
            # Buscar próximos jogos (próximos 7 dias)
            today = date.today()
            week_end = today + timedelta(days=7)
            
            games = game_controller.get_games(
                date_from=today,
                date_to=week_end,
                status_filter=GameStatus.SCHEDULED
            )
            
            # Ordenar por data e hora
            games.sort(key=lambda g: (g.game_date, g.game_time or datetime.min.time()))
            
            # Adicionar jogos na árvore
            for game in games[:10]:  # Máximo 10 jogos
                home_team = team_controller.get_team_by_id(game.home_team_id)
                away_team = team_controller.get_team_by_id(game.away_team_id)
                competition = competition_controller.get_competition_by_id(game.competition_id)
                
                self.games_tree.insert('', 'end', values=(
                    game.game_date.strftime("%d/%m"),
                    game.game_time.strftime("%H:%M") if game.game_time else "",
                    home_team.name if home_team else "N/A",
                    away_team.name if away_team else "N/A",
                    competition.name if competition else "N/A"
                ))
                
        except Exception as e:
            print(f"Erro ao atualizar jogos: {e}")
    
    def update_competitions(self):
        """Atualiza lista de competições"""
        try:
            competitions = competition_controller.get_all_competitions()
            
            # Atualizar combobox
            comp_names = [f"{comp.name} ({comp.season})" for comp in competitions]
            self.competition_combo['values'] = comp_names
            
            # Selecionar primeira competição se houver
            if comp_names and not self.competition_var.get():
                self.competition_combo.current(0)
                self.update_standings()
                
        except Exception as e:
            print(f"Erro ao atualizar competições: {e}")
    
    def on_competition_change(self, event=None):
        """Chamado quando muda a competição selecionada"""
        self.update_standings()
    
    def update_standings(self):
        """Atualiza classificação da competição selecionada"""
        try:
            # Limpar árvore
            for item in self.standings_tree.get_children():
                self.standings_tree.delete(item)
            
            # Obter competição selecionada
            selected = self.competition_var.get()
            if not selected:
                return
            
            # Encontrar ID da competição
            competitions = competition_controller.get_all_competitions()
            competition_id = None
            
            for comp in competitions:
                if f"{comp.name} ({comp.season})" == selected:
                    competition_id = comp.id
                    break
            
            if not competition_id:
                return
            
            # Buscar classificação
            standings = competition_controller.get_standings(competition_id)
            
            # Adicionar na árvore
            for i, standing in enumerate(standings, 1):
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
            print(f"Erro ao atualizar classificação: {e}")
    
    def update_recent_activities(self):
        """Atualiza atividades recentes"""
        try:
            # Limpar árvore
            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)
            
            activities = []
            
            # Jogos recentes finalizados
            recent_games = game_controller.get_recent_games(limit=5)
            for game in recent_games:
                if game.status == GameStatus.FINISHED:
                    home_team = team_controller.get_team_by_id(game.home_team_id)
                    away_team = team_controller.get_team_by_id(game.away_team_id)
                    
                    activities.append({
                        'datetime': game.actual_end_time or game.updated_at,
                        'type': 'Jogo Finalizado',
                        'description': f"{home_team.name if home_team else 'N/A'} {game.home_score} x {game.away_score} {away_team.name if away_team else 'N/A'}"
                    })
            
            # Equipes criadas recentemente
            recent_teams = team_controller.get_recent_teams(limit=3)
            for team in recent_teams:
                activities.append({
                    'datetime': team.created_at,
                    'type': 'Nova Equipe',
                    'description': f"Equipe '{team.name}' foi cadastrada"
                })
            
            # Ordenar por data
            activities.sort(key=lambda x: x['datetime'], reverse=True)
            
            # Adicionar na árvore
            for activity in activities[:10]:  # Máximo 10 atividades
                self.recent_tree.insert('', 'end', values=(
                    activity['datetime'].strftime("%d/%m %H:%M"),
                    activity['type'],
                    activity['description']
                ))
                
        except Exception as e:
            print(f"Erro ao atualizar atividades recentes: {e}")

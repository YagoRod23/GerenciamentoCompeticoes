"""
Janela de relatórios e estatísticas
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from desktop_app.controllers.reports_controller import reports_controller
from desktop_app.controllers.competition_controller import competition_controller
from desktop_app.controllers.team_controller import team_controller


class ReportsWindow:
    """Janela de relatórios e estatísticas"""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent = parent_frame
        
        # Variáveis de controle
        self.report_type_var: Optional[tk.StringVar] = None
        self.competition_var: Optional[tk.StringVar] = None
        self.team_var: Optional[tk.StringVar] = None
        
        # Widgets
        self.canvas_frame: Optional[ttk.Frame] = None
        self.report_text: Optional[tk.Text] = None
    
    def setup_reports_view(self):
        """Configura a view de relatórios"""
        # Limpar frame pai
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Título
        title_label = ttk.Label(self.parent, text="Relatórios e Estatísticas", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(self.parent, text="Configurações do Relatório", padding="10")
        controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.setup_controls(controls_frame)
        
        # Notebook para diferentes tipos de visualização
        self.reports_notebook = ttk.Notebook(self.parent)
        self.reports_notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Aba de gráficos
        charts_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(charts_frame, text="Gráficos")
        self.setup_charts_tab(charts_frame)
        
        # Aba de relatórios textuais
        text_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(text_frame, text="Relatórios")
        self.setup_text_reports_tab(text_frame)
        
        # Aba de comparações
        comparison_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(comparison_frame, text="Comparações")
        self.setup_comparison_tab(comparison_frame)
    
    def setup_controls(self, parent: ttk.Frame):
        """Configura controles de filtros"""
        # Frame principal de controles
        main_controls = ttk.Frame(parent)
        main_controls.pack(fill="x")
        
        # Linha 1: Tipo de relatório
        row1 = ttk.Frame(main_controls)
        row1.pack(fill="x", pady=(0, 10))
        
        ttk.Label(row1, text="Tipo de Relatório:").pack(side="left")
        
        self.report_type_var = tk.StringVar(value="competicao_geral")
        report_types = [
            ("Estatísticas Gerais da Competição", "competicao_geral"),
            ("Performance de Equipes", "performance_equipes"),
            ("Estatísticas de Jogadores", "stats_jogadores"),
            ("Análise de Jogos", "analise_jogos"),
            ("Classificações", "classificacoes"),
            ("Artilharia", "artilharia")
        ]
        
        type_combo = ttk.Combobox(row1, textvariable=self.report_type_var,
                                values=[item[1] for item in report_types],
                                state="readonly", width=25)
        type_combo.pack(side="left", padx=(10, 0))
        
        # Mapear valores para textos legíveis
        self.report_type_map = {item[1]: item[0] for item in report_types}
        type_combo.bind("<<ComboboxSelected>>", self.on_report_type_change)
        
        # Linha 2: Filtros específicos
        row2 = ttk.Frame(main_controls)
        row2.pack(fill="x", pady=(0, 10))
        
        # Filtro por competição
        ttk.Label(row2, text="Competição:").pack(side="left")
        
        self.competition_var = tk.StringVar(value="TODAS")
        self.competition_combo = ttk.Combobox(row2, textvariable=self.competition_var,
                                            state="readonly", width=20)
        self.competition_combo.pack(side="left", padx=(10, 20))
        
        # Filtro por equipe
        ttk.Label(row2, text="Equipe:").pack(side="left")
        
        self.team_var = tk.StringVar(value="TODAS")
        self.team_combo = ttk.Combobox(row2, textvariable=self.team_var,
                                     state="readonly", width=20)
        self.team_combo.pack(side="left", padx=(10, 0))
        
        # Linha 3: Botões de ação
        row3 = ttk.Frame(main_controls)
        row3.pack(fill="x")
        
        ttk.Button(row3, text="Gerar Relatório", 
                  command=self.generate_report, style="Accent.TButton").pack(side="left")
        ttk.Button(row3, text="Exportar PDF", 
                  command=self.export_pdf).pack(side="left", padx=(10, 0))
        ttk.Button(row3, text="Exportar Excel", 
                  command=self.export_excel).pack(side="left", padx=(10, 0))
        
        # Carregar dados para os combos
        self.load_filter_data()
    
    def setup_charts_tab(self, parent: ttk.Frame):
        """Configura aba de gráficos"""
        # Frame para canvas matplotlib
        self.canvas_frame = ttk.Frame(parent)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Label inicial
        self.charts_label = ttk.Label(self.canvas_frame, 
                                    text="Selecione um tipo de relatório e clique em 'Gerar Relatório'",
                                    font=("Arial", 12))
        self.charts_label.pack(expand=True)
    
    def setup_text_reports_tab(self, parent: ttk.Frame):
        """Configura aba de relatórios textuais"""
        # Frame com scrollbar
        text_container = ttk.Frame(parent)
        text_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Texto com scrollbar
        self.report_text = tk.Text(text_container, wrap="word", font=("Courier", 10))
        self.report_text.pack(side="left", fill="both", expand=True)
        
        text_scroll = ttk.Scrollbar(text_container, orient="vertical", command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=text_scroll.set)
        text_scroll.pack(side="right", fill="y")
        
        # Texto inicial
        self.report_text.insert(1.0, "Aguardando geração de relatório...")
        self.report_text.config(state="disabled")
    
    def setup_comparison_tab(self, parent: ttk.Frame):
        """Configura aba de comparações"""
        # Frame de seleção para comparação
        selection_frame = ttk.LabelFrame(parent, text="Selecionar Equipes para Comparação", padding="10")
        selection_frame.pack(fill="x", padx=10, pady=10)
        
        # Lista de equipes disponíveis
        ttk.Label(selection_frame, text="Equipes Disponíveis:").pack(anchor="w")
        
        self.available_teams_listbox = tk.Listbox(selection_frame, height=5, selectmode="multiple")
        self.available_teams_listbox.pack(fill="x", pady=(5, 10))
        
        # Botões de controle
        buttons_frame = ttk.Frame(selection_frame)
        buttons_frame.pack(fill="x")
        
        ttk.Button(buttons_frame, text="Comparar Selecionadas", 
                  command=self.compare_teams).pack(side="left")
        ttk.Button(buttons_frame, text="Limpar Seleção", 
                  command=self.clear_comparison).pack(side="left", padx=(10, 0))
        
        # Frame para resultados da comparação
        self.comparison_results_frame = ttk.LabelFrame(parent, text="Resultados da Comparação", padding="10")
        self.comparison_results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Carregar equipes para comparação
        self.load_teams_for_comparison()
    
    def load_filter_data(self):
        """Carrega dados para os filtros"""
        try:
            # Carregar competições
            competitions = competition_controller.get_all_competitions()
            comp_names = ["TODAS"] + [comp.name for comp in competitions]
            self.competition_combo.config(values=comp_names)
            
            # Carregar equipes
            teams = team_controller.get_all_teams()
            team_names = ["TODAS"] + [team.name for team in teams]
            self.team_combo.config(values=team_names)
            
        except Exception as e:
            print(f"Erro ao carregar dados para filtros: {e}")
    
    def load_teams_for_comparison(self):
        """Carrega equipes para comparação"""
        try:
            teams = team_controller.get_all_teams()
            self.available_teams_listbox.delete(0, tk.END)
            
            for team in teams:
                self.available_teams_listbox.insert(tk.END, team.name)
                
        except Exception as e:
            print(f"Erro ao carregar equipes para comparação: {e}")
    
    def on_report_type_change(self, event=None):
        """Chamado quando muda o tipo de relatório"""
        # Atualizar interface baseado no tipo selecionado
        report_type = self.report_type_var.get()
        
        # Habilitar/desabilitar filtros baseado no tipo
        if report_type in ["stats_jogadores", "performance_equipes"]:
            self.team_combo.config(state="readonly")
        else:
            self.team_combo.config(state="disabled")
    
    def generate_report(self):
        """Gera o relatório selecionado"""
        try:
            report_type = self.report_type_var.get()
            competition = self.competition_var.get()
            team = self.team_var.get()
            
            # Obter IDs baseado nos nomes
            competition_id = None
            if competition != "TODAS":
                competitions = competition_controller.get_all_competitions()
                for comp in competitions:
                    if comp.name == competition:
                        competition_id = comp.id
                        break
            
            team_id = None
            if team != "TODAS":
                teams = team_controller.get_all_teams()
                for t in teams:
                    if t.name == team:
                        team_id = t.id
                        break
            
            # Gerar dados do relatório
            if report_type == "competicao_geral":
                self.generate_competition_general_report(competition_id)
            elif report_type == "performance_equipes":
                self.generate_teams_performance_report(competition_id, team_id)
            elif report_type == "stats_jogadores":
                self.generate_players_stats_report(competition_id, team_id)
            elif report_type == "analise_jogos":
                self.generate_games_analysis_report(competition_id)
            elif report_type == "classificacoes":
                self.generate_standings_report(competition_id)
            elif report_type == "artilharia":
                self.generate_top_scorers_report(competition_id)
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def generate_competition_general_report(self, competition_id: Optional[int]):
        """Gera relatório geral da competição"""
        try:
            data = reports_controller.get_competition_summary(competition_id)
            
            # Gerar gráfico
            self.clear_charts()
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle('Estatísticas Gerais da Competição')
            
            # Gráfico 1: Jogos por status
            status_data = data.get('games_by_status', {})
            if status_data:
                ax1.pie(status_data.values(), labels=status_data.keys(), autopct='%1.1f%%')
                ax1.set_title('Jogos por Status')
            
            # Gráfico 2: Gols por rodada
            goals_data = data.get('goals_by_round', {})
            if goals_data:
                ax2.bar(goals_data.keys(), goals_data.values())
                ax2.set_title('Gols por Rodada')
                ax2.set_xlabel('Rodada')
                ax2.set_ylabel('Gols')
            
            # Gráfico 3: Performance das equipes
            teams_performance = data.get('teams_performance', [])
            if teams_performance:
                teams = [tp['team_name'] for tp in teams_performance[:5]]  # Top 5
                points = [tp['points'] for tp in teams_performance[:5]]
                ax3.bar(teams, points)
                ax3.set_title('Top 5 Equipes - Pontos')
                ax3.tick_params(axis='x', rotation=45)
            
            # Gráfico 4: Estatísticas gerais
            stats = data.get('general_stats', {})
            if stats:
                labels = list(stats.keys())
                values = list(stats.values())
                ax4.bar(labels, values)
                ax4.set_title('Estatísticas Gerais')
                ax4.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Adicionar ao canvas
            canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Gerar relatório textual
            self.generate_text_report(data, "Relatório Geral da Competição")
            
        except Exception as e:
            print(f"Erro ao gerar relatório geral: {e}")
    
    def generate_teams_performance_report(self, competition_id: Optional[int], team_id: Optional[int]):
        """Gera relatório de performance das equipes"""
        try:
            data = reports_controller.get_teams_performance(competition_id, team_id)
            
            # Gerar gráfico
            self.clear_charts()
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            fig.suptitle('Performance das Equipes')
            
            if data:
                teams = [item['team_name'] for item in data]
                wins = [item['wins'] for item in data]
                goals_for = [item['goals_for'] for item in data]
                
                # Gráfico de vitórias
                ax1.bar(teams, wins)
                ax1.set_title('Vitórias por Equipe')
                ax1.tick_params(axis='x', rotation=45)
                
                # Gráfico de gols marcados
                ax2.bar(teams, goals_for)
                ax2.set_title('Gols Marcados por Equipe')
                ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Gerar relatório textual
            self.generate_text_report(data, "Relatório de Performance das Equipes")
            
        except Exception as e:
            print(f"Erro ao gerar relatório de performance: {e}")
    
    def generate_players_stats_report(self, competition_id: Optional[int], team_id: Optional[int]):
        """Gera relatório de estatísticas dos jogadores"""
        # Implementação simplificada
        self.show_message("Relatório de jogadores em desenvolvimento")
    
    def generate_games_analysis_report(self, competition_id: Optional[int]):
        """Gera relatório de análise de jogos"""
        # Implementação simplificada
        self.show_message("Análise de jogos em desenvolvimento")
    
    def generate_standings_report(self, competition_id: Optional[int]):
        """Gera relatório de classificações"""
        try:
            if not competition_id:
                competitions = competition_controller.get_all_competitions()
                if competitions:
                    competition_id = competitions[0].id
            
            standings = reports_controller.get_standings_data(competition_id)
            
            if not standings:
                self.show_message("Nenhum dado de classificação encontrado")
                return
            
            # Gerar gráfico
            self.clear_charts()
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            teams = [s['team_name'] for s in standings]
            points = [s['points'] for s in standings]
            
            bars = ax.bar(teams, points)
            ax.set_title('Classificação - Pontos por Equipe')
            ax.set_xlabel('Equipes')
            ax.set_ylabel('Pontos')
            
            # Colorir barras baseado na posição
            colors = ['gold', 'silver', '#CD7F32'] + ['lightblue'] * (len(bars) - 3)
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Gerar relatório textual
            self.generate_standings_text_report(standings)
            
        except Exception as e:
            print(f"Erro ao gerar relatório de classificação: {e}")
    
    def generate_top_scorers_report(self, competition_id: Optional[int]):
        """Gera relatório de artilharia"""
        # Implementação simplificada
        self.show_message("Relatório de artilharia em desenvolvimento")
    
    def generate_text_report(self, data, title: str):
        """Gera relatório textual"""
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        
        report = f"{title}\n"
        report += "=" * len(title) + "\n\n"
        
        if isinstance(data, dict):
            for key, value in data.items():
                report += f"{key}: {value}\n"
        elif isinstance(data, list):
            for i, item in enumerate(data, 1):
                report += f"{i}. {item}\n"
        
        self.report_text.insert(1.0, report)
        self.report_text.config(state="disabled")
    
    def generate_standings_text_report(self, standings):
        """Gera relatório textual de classificação"""
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        
        report = "CLASSIFICAÇÃO\n"
        report += "=" * 50 + "\n\n"
        
        report += f"{'Pos':<4} {'Equipe':<20} {'J':<3} {'V':<3} {'E':<3} {'D':<3} {'GP':<4} {'GC':<4} {'SG':<4} {'Pts':<4}\n"
        report += "-" * 60 + "\n"
        
        for i, team in enumerate(standings, 1):
            report += f"{i:<4} {team['team_name']:<20} {team['games_played']:<3} {team['wins']:<3} "
            report += f"{team['draws']:<3} {team['losses']:<3} {team['goals_for']:<4} "
            report += f"{team['goals_against']:<4} {team['goal_difference']:<4} {team['points']:<4}\n"
        
        self.report_text.insert(1.0, report)
        self.report_text.config(state="disabled")
    
    def clear_charts(self):
        """Limpa área de gráficos"""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
    
    def show_message(self, message: str):
        """Exibe mensagem na área de gráficos"""
        self.clear_charts()
        label = ttk.Label(self.canvas_frame, text=message, font=("Arial", 12))
        label.pack(expand=True)
    
    def compare_teams(self):
        """Compara equipes selecionadas"""
        selections = self.available_teams_listbox.curselection()
        if len(selections) < 2:
            from tkinter import messagebox
            messagebox.showwarning("Aviso", "Selecione pelo menos 2 equipes para comparar")
            return
        
        selected_teams = [self.available_teams_listbox.get(i) for i in selections]
        
        # Limpar frame de resultados
        for widget in self.comparison_results_frame.winfo_children():
            widget.destroy()
        
        # Criar comparação simples
        comparison_text = tk.Text(self.comparison_results_frame, height=15, wrap="word")
        comparison_text.pack(fill="both", expand=True)
        
        result = "COMPARAÇÃO ENTRE EQUIPES\n"
        result += "=" * 30 + "\n\n"
        
        for team_name in selected_teams:
            result += f"Equipe: {team_name}\n"
            # Aqui seria implementada a lógica real de comparação
            result += "- Estatísticas em desenvolvimento\n\n"
        
        comparison_text.insert(1.0, result)
        comparison_text.config(state="disabled")
    
    def clear_comparison(self):
        """Limpa seleção de comparação"""
        self.available_teams_listbox.selection_clear(0, tk.END)
        
        for widget in self.comparison_results_frame.winfo_children():
            widget.destroy()
    
    def export_pdf(self):
        """Exporta relatório para PDF"""
        from tkinter import messagebox
        messagebox.showinfo("Info", "Exportação para PDF em desenvolvimento")
    
    def export_excel(self):
        """Exporta relatório para Excel"""
        from tkinter import messagebox
        messagebox.showinfo("Info", "Exportação para Excel em desenvolvimento")


### desktop_app/views/admin_window.py


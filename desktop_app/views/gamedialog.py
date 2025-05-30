"""
Dialog para criação e edição de jogos
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, time
from typing import Optional, List

from desktop_app.controllers.game_controller import game_controller
from desktop_app.controllers.team_controller import team_controller
from desktop_app.controllers.competition_controller import competition_controller


class GameDialog:
    """Dialog para gerenciar jogos"""
    
    def __init__(self, parent, game_id: Optional[int] = None, competition_id: Optional[int] = None):
        self.parent = parent
        self.game_id = game_id
        self.competition_id = competition_id
        self.result = None
        
        # Variáveis de entrada
        self.competition_var = tk.StringVar()
        self.home_team_var = tk.StringVar()
        self.away_team_var = tk.StringVar()
        self.round_var = tk.StringVar(value="1")
        self.stadium_var = tk.StringVar()
        self.referee_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        
        # Dados
        self.competitions = []
        self.teams = []
        
        # Criar janela
        self.create_dialog()
        self.load_data()
        
        # Se editando, carregar dados
        if self.game_id:
            self.load_game_data()
    
    def create_dialog(self):
        """Cria a janela do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Novo Jogo" if not self.game_id else "Editar Jogo")
        self.dialog.geometry("600x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centralizar janela
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title = "Novo Jogo" if not self.game_id else "Editar Jogo"
        title_label = ttk.Label(main_frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook para organizar dados
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # Aba de informações básicas
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Informações Básicas")
        self.create_basic_form(basic_frame)
        
        # Aba de data e horário
        datetime_frame = ttk.Frame(self.notebook)
        self.notebook.add(datetime_frame, text="Data e Horário")
        self.create_datetime_form(datetime_frame)
        
        # Aba de local e arbitragem
        venue_frame = ttk.Frame(self.notebook)
        self.notebook.add(venue_frame, text="Local e Arbitragem")
        self.create_venue_form(venue_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self.save_game())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def create_basic_form(self, parent):
        """Cria formulário de informações básicas"""
        form_frame = ttk.Frame(parent, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Competição
        ttk.Label(form_frame, text="Competição *:").pack(anchor="w")
        self.competition_combo = ttk.Combobox(form_frame, textvariable=self.competition_var, 
                                            state="readonly", width=50)
        self.competition_combo.pack(fill="x", pady=(0, 15))
        self.competition_combo.bind('<<ComboboxSelected>>', self.on_competition_selected)
        
        # Equipes
        teams_frame = ttk.LabelFrame(form_frame, text="Equipes", padding="10")
        teams_frame.pack(fill="x", pady=(0, 15))
        
        # Time mandante
        ttk.Label(teams_frame, text="Time Mandante *:").pack(anchor="w")
        self.home_team_combo = ttk.Combobox(teams_frame, textvariable=self.home_team_var, 
                                          state="readonly", width=40)
        self.home_team_combo.pack(fill="x", pady=(0, 10))
        
        # VS label
        vs_label = ttk.Label(teams_frame, text="VS", font=("Arial", 12, "bold"))
        vs_label.pack(pady=5)
        
        # Time visitante
        ttk.Label(teams_frame, text="Time Visitante *:").pack(anchor="w")
        self.away_team_combo = ttk.Combobox(teams_frame, textvariable=self.away_team_var, 
                                          state="readonly", width=40)
        self.away_team_combo.pack(fill="x", pady=(0, 10))
        
        # Rodada
        ttk.Label(form_frame, text="Rodada:").pack(anchor="w")
        round_spin = ttk.Spinbox(form_frame, from_=1, to=50, 
                               textvariable=self.round_var, width=10)
        round_spin.pack(anchor="w", pady=(0, 15))
        
        # Observações
        ttk.Label(form_frame, text="Observações:").pack(anchor="w")
        self.notes_entry = ttk.Entry(form_frame, textvariable=self.notes_var, width=50)
        self.notes_entry.pack(fill="x", pady=(0, 15))
    
    def create_datetime_form(self, parent):
        """Cria formulário de data e horário"""
        form_frame = ttk.Frame(parent, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Data do jogo
        ttk.Label(form_frame, text="Data do Jogo *:").pack(anchor="w")
        self.game_date = DateEntry(form_frame, width=15, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  date_pattern='dd/mm/yyyy')
        self.game_date.pack(anchor="w", pady=(0, 20))
        
        # Horário
        time_frame = ttk.LabelFrame(form_frame, text="Horário", padding="10")
        time_frame.pack(fill="x", pady=(0, 20))
        
        time_controls = ttk.Frame(time_frame)
        time_controls.pack()
        
        # Hora
        ttk.Label(time_controls, text="Hora:").grid(row=0, column=0, padx=(0, 5))
        self.hour_var = tk.StringVar(value="15")
        hour_spin = ttk.Spinbox(time_controls, from_=0, to=23, format="%02.0f",
                               textvariable=self.hour_var, width=5)
        hour_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(time_controls, text=":").grid(row=0, column=2)
        
        # Minuto
        ttk.Label(time_controls, text="Minutos:").grid(row=0, column=3, padx=(5, 5))
        self.minute_var = tk.StringVar(value="00")
        minute_spin = ttk.Spinbox(time_controls, from_=0, to=59, format="%02.0f",
                                 textvariable=self.minute_var, width=5)
        minute_spin.grid(row=0, column=4, padx=5)
        
        # Previsão de duração
        duration_frame = ttk.LabelFrame(form_frame, text="Duração Prevista", padding="10")
        duration_frame.pack(fill="x")
        
        self.duration_var = tk.StringVar(value="90")
        ttk.Label(duration_frame, text="Minutos:").pack(side="left")
        duration_spin = ttk.Spinbox(duration_frame, from_=45, to=180, 
                                   textvariable=self.duration_var, width=10)
        duration_spin.pack(side="left", padx=(5, 0))
    
    def create_venue_form(self, parent):
        """Cria formulário de local e arbitragem"""
        form_frame = ttk.Frame(parent, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Local
        venue_frame = ttk.LabelFrame(form_frame, text="Local do Jogo", padding="10")
        venue_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(venue_frame, text="Estádio/Campo:").pack(anchor="w")
        self.stadium_entry = ttk.Entry(venue_frame, textvariable=self.stadium_var, width=50)
        self.stadium_entry.pack(fill="x", pady=(0, 10))
        
        # Botão para usar estádio do time mandante
        use_home_stadium_btn = ttk.Button(venue_frame, text="Usar Estádio do Time Mandante",
                                        command=self.use_home_stadium)
        use_home_stadium_btn.pack(anchor="w")
        
        # Arbitragem
        referee_frame = ttk.LabelFrame(form_frame, text="Arbitragem", padding="10")
        referee_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(referee_frame, text="Árbitro Principal:").pack(anchor="w")
        self.referee_entry = ttk.Entry(referee_frame, textvariable=self.referee_var, width=50)
        self.referee_entry.pack(fill="x", pady=(0, 10))
        
        # Status do jogo
        status_frame = ttk.LabelFrame(form_frame, text="Status", padding="10")
        status_frame.pack(fill="x")
        
        self.status_var = tk.StringVar(value="SCHEDULED")
        status_options = [
            ("Agendado", "SCHEDULED"),
            ("Em Andamento", "IN_PROGRESS"),
            ("Finalizado", "FINISHED"),
            ("Adiado", "POSTPONED"),
            ("Cancelado", "CANCELLED")
        ]
        
        for text, value in status_options:
            ttk.Radiobutton(status_frame, text=text, variable=self.status_var, 
                           value=value).pack(anchor="w", pady=2)
    
    def create_buttons(self, parent):
        """Cria botões do dialog"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_game, style="Accent.TButton").pack(side="right")
    
    def load_data(self):
        """Carrega dados necessários"""
        try:
            # Carregar competições
            self.competitions = competition_controller.get_active_competitions()
            competition_names = [f"{comp.name} ({comp.season})" for comp in self.competitions]
            self.competition_combo['values'] = competition_names
            
            # Se foi passada uma competição específica, selecioná-la
            if self.competition_id:
                for i, comp in enumerate(self.competitions):
                    if comp.id == self.competition_id:
                        self.competition_combo.set(competition_names[i])
                        self.on_competition_selected(None)
                        break
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
    
    def on_competition_selected(self, event):
        """Chamado quando uma competição é selecionada"""
        try:
            selected_index = self.competition_combo.current()
            if selected_index >= 0:
                competition = self.competitions[selected_index]
                
                # Carregar equipes da competição
                self.teams = team_controller.get_teams_by_competition(competition.id)
                team_names = [team.name for team in self.teams]
                
                self.home_team_combo['values'] = team_names
                self.away_team_combo['values'] = team_names
                
                # Limpar seleções anteriores
                self.home_team_var.set("")
                self.away_team_var.set("")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar equipes: {str(e)}")
    
    def use_home_stadium(self):
        """Usa o estádio do time mandante"""
        try:
            home_team_index = self.home_team_combo.current()
            if home_team_index >= 0:
                home_team = self.teams[home_team_index]
                if home_team.stadium:
                    self.stadium_var.set(home_team.stadium)
                else:
                    messagebox.showinfo("Info", "Time mandante não possui estádio cadastrado")
            else:
                messagebox.showwarning("Aviso", "Selecione primeiro o time mandante")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def load_game_data(self):
        """Carrega dados do jogo para edição"""
        try:
            game = game_controller.get_game_by_id(self.game_id)
            if game:
                # Competição
                for i, comp in enumerate(self.competitions):
                    if comp.id == game.competition_id:
                        self.competition_combo.set(f"{comp.name} ({comp.season})")
                        self.on_competition_selected(None)
                        break
                
                # Equipes
                for i, team in enumerate(self.teams):
                    if team.id == game.home_team_id:
                        self.home_team_combo.set(team.name)
                    if team.id == game.away_team_id:
                        self.away_team_combo.set(team.name)
                
                # Data e hora
                if game.game_datetime:
                    self.game_date.set_date(game.game_datetime.date())
                    self.hour_var.set(f"{game.game_datetime.hour:02d}")
                    self.minute_var.set(f"{game.game_datetime.minute:02d}")
                
                # Outros dados
                self.round_var.set(str(game.round_number or 1))
                self.stadium_var.set(game.stadium or "")
                self.referee_var.set(game.referee or "")
                self.notes_var.set(game.notes or "")
                
                if hasattr(game, 'status'):
                    self.status_var.set(game.status)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados do jogo: {str(e)}")
    
    def validate_form(self) -> bool:
        """Valida formulário"""
        if not self.competition_var.get():
            messagebox.showerror("Erro", "Selecione uma competição")
            self.notebook.select(0)
            return False
        
        if not self.home_team_var.get():
            messagebox.showerror("Erro", "Selecione o time mandante")
            self.notebook.select(0)
            return False
        
        if not self.away_team_var.get():
            messagebox.showerror("Erro", "Selecione o time visitante")
            self.notebook.select(0)
            return False
        
        if self.home_team_var.get() == self.away_team_var.get():
            messagebox.showerror("Erro", "Time mandante e visitante devem ser diferentes")
            self.notebook.select(0)
            return False
        
        # Validar horário
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Horário inválido")
            self.notebook.select(1)
            return False
        
        return True
    
    def save_game(self):
        """Salva dados do jogo"""
        if not self.validate_form():
            return
        
        try:
            # Encontrar IDs das equipes
            home_team_id = None
            away_team_id = None
            
            for team in self.teams:
                if team.name == self.home_team_var.get():
                    home_team_id = team.id
                if team.name == self.away_team_var.get():
                    away_team_id = team.id
            
            # Encontrar ID da competição
            competition_id = None
            comp_index = self.competition_combo.current()
            if comp_index >= 0:
                competition_id = self.competitions[comp_index].id
            
            # Criar datetime
            game_date = self.game_date.get_date()
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            game_datetime = datetime.combine(game_date, time(hour, minute))
            
            # Preparar dados
            game_data = {
                'competition_id': competition_id,
                'home_team_id': home_team_id,
                'away_team_id': away_team_id,
                'game_datetime': game_datetime,
                'round_number': int(self.round_var.get()) if self.round_var.get() else None,
                'stadium': self.stadium_var.get().strip() or None,
                'referee': self.referee_var.get().strip() or None,
                'notes': self.notes_var.get().strip() or None,
                'status': self.status_var.get()
            }
            
            if self.game_id:
                # Editar jogo existente
                success = game_controller.update_game(self.game_id, game_data)
                message = "Jogo atualizado com sucesso!"
            else:
                # Criar novo jogo
                game = game_controller.create_game(game_data)
                success = game is not None
                message = "Partida criado com sucesso!"
            
            if success:
                self.result = True
                messagebox.showinfo("Sucesso", message)
                self.dialog.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao salvar jogo")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar jogo: {str(e)}")
    
    def cancel(self):
        """Cancela operação"""
        self.result = False
        self.dialog.destroy()

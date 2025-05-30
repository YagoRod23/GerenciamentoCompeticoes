"""
Dialog para criação e edição de competições
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
from typing import Optional

from desktop_app.controllers.competition_controller import competition_controller
from database.models import CompetitionType


class CompetitionDialog:
    """Dialog para gerenciar competições"""
    
    def __init__(self, parent, competition_id: Optional[int] = None):
        self.parent = parent
        self.competition_id = competition_id
        self.result = None
        
        # Variáveis de entrada
        self.name_var = tk.StringVar()
        self.type_var = tk.StringVar(value=CompetitionType.LEAGUE.value)
        self.season_var = tk.StringVar(value=str(datetime.now().year))
        self.description_var = tk.StringVar()
        
        # Criar janela
        self.create_dialog()
        
        # Se editando, carregar dados
        if self.competition_id:
            self.load_competition_data()
    
    def create_dialog(self):
        """Cria a janela do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Nova Competição" if not self.competition_id else "Editar Competição")
        self.dialog.geometry("600x500")
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
        title = "Nova Competição" if not self.competition_id else "Editar Competição"
        title_label = ttk.Label(main_frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook para organizar dados
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # Aba de informações básicas
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Informações Básicas")
        self.create_basic_form(basic_frame)
        
        # Aba de datas
        dates_frame = ttk.Frame(self.notebook)
        self.notebook.add(dates_frame, text="Datas")
        self.create_dates_form(dates_frame)
        
        # Aba de configurações
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configurações")
        self.create_config_form(config_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self.save_competition())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Focar no primeiro campo
        self.name_entry.focus()
    
    def create_basic_form(self, parent):
        """Cria formulário de informações básicas"""
        form_frame = ttk.Frame(parent, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Nome da competição
        ttk.Label(form_frame, text="Nome da Competição *:").pack(anchor="w")
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=50)
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # Tipo de competição
        ttk.Label(form_frame, text="Tipo de Competição *:").pack(anchor="w")
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill="x", pady=(0, 15))
        
        # Radio buttons para tipo
        self.type_league_radio = ttk.Radiobutton(type_frame, text="Campeonato (Pontos Corridos)", 
                                               variable=self.type_var, value=CompetitionType.LEAGUE.value)
        self.type_league_radio.pack(anchor="w")
        
        self.type_knockout_radio = ttk.Radiobutton(type_frame, text="Copa (Eliminatório)", 
                                                 variable=self.type_var, value=CompetitionType.KNOCKOUT.value)
        self.type_knockout_radio.pack(anchor="w", pady=(5, 0))
        
        # Temporada
        ttk.Label(form_frame, text="Temporada *:").pack(anchor="w")
        season_spin = ttk.Spinbox(form_frame, from_=2020, to=2030, 
                                 textvariable=self.season_var, width=10)
        season_spin.pack(anchor="w", pady=(0, 15))
        
        # Descrição
        ttk.Label(form_frame, text="Descrição:").pack(anchor="w")
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.description_text = tk.Text(desc_frame, height=6, wrap="word")
        self.description_text.pack(side="left", fill="both", expand=True)
        
        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scroll.set)
        desc_scroll.pack(side="right", fill="y")
    
    def create_dates_form(self, parent):
        """Cria formulário de datas"""
        form_frame = ttk.Frame(parent, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Data de início
        ttk.Label(form_frame, text="Data de Início:").pack(anchor="w")
        self.start_date = DateEntry(form_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd/mm/yyyy')
        self.start_date.pack(anchor="w", pady=(0, 15))
        
        # Data de fim
        ttk.Label(form_frame, text="Data de Término:").pack(anchor="w")
        self.end_date = DateEntry(form_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2,
                                 date_pattern='dd/mm/yyyy')
        self.end_date.pack(anchor="w", pady=(0, 15))
        
        # Data limite para inscrições
        ttk.Label(form_frame, text="Data Limite para Inscrições:").pack(anchor="w")
        self.registration_deadline = DateEntry(form_frame, width=12, background='darkblue',
                                             foreground='white', borderwidth=2,
                                             date_pattern='dd/mm/yyyy')
        self.registration_deadline.pack(anchor="w", pady=(0, 15))
        
        # Configurar datas padrão
        today = date.today()
        self.start_date.set_date(today)
        self.registration_deadline.set_date(today)
    
    def create_config_form(self, parent):
        """Cria formulário de configurações"""
        form_frame = ttk.Frame(parent, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Número máximo de equipes
        ttk.Label(form_frame, text="Número Máximo de Equipes:").pack(anchor="w")
        self.max_teams_var = tk.StringVar(value="16")
        max_teams_spin = ttk.Spinbox(form_frame, from_=4, to=64, 
                                    textvariable=self.max_teams_var, width=10)
        max_teams_spin.pack(anchor="w", pady=(0, 15))
        
        # Configurações de pontuação (apenas para campeonatos)
        points_frame = ttk.LabelFrame(form_frame, text="Sistema de Pontuação", padding="10")
        points_frame.pack(fill="x", pady=(0, 15))
        
        points_grid = ttk.Frame(points_frame)
        points_grid.pack(fill="x")
        
        # Pontos por vitória
        ttk.Label(points_grid, text="Pontos por Vitória:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.win_points_var = tk.StringVar(value="3")
        ttk.Spinbox(points_grid, from_=0, to=10, textvariable=self.win_points_var, width=5).grid(row=0, column=1)
        
        # Pontos por empate
        ttk.Label(points_grid, text="Pontos por Empate:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        self.draw_points_var = tk.StringVar(value="1")
        ttk.Spinbox(points_grid, from_=0, to=10, textvariable=self.draw_points_var, width=5).grid(row=1, column=1, pady=(5, 0))
        
        # Pontos por derrota
        ttk.Label(points_grid, text="Pontos por Derrota:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        self.loss_points_var = tk.StringVar(value="0")
        ttk.Spinbox(points_grid, from_=0, to=10, textvariable=self.loss_points_var, width=5).grid(row=2, column=1, pady=(5, 0))
        
        # Opções adicionais
        options_frame = ttk.LabelFrame(form_frame, text="Opções", padding="10")
        options_frame.pack(fill="x")
        
        self.is_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Competição Ativa", 
                       variable=self.is_active_var).pack(anchor="w")
        
        self.allow_registration_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Permitir Inscrições", 
                       variable=self.allow_registration_var).pack(anchor="w", pady=(5, 0))
    
    def create_buttons(self, parent):
        """Cria botões do dialog"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_competition, style="Accent.TButton").pack(side="right")
    
    def load_competition_data(self):
        """Carrega dados da competição para edição"""
        try:
            competition = competition_controller.get_competition_by_id(self.competition_id)
            if competition:
                self.name_var.set(competition.name)
                self.type_var.set(competition.competition_type.value)
                self.season_var.set(str(competition.season))
                
                if competition.description:
                    self.description_text.insert(1.0, competition.description)
                
                if competition.start_date:
                    self.start_date.set_date(competition.start_date)
                if competition.end_date:
                    self.end_date.set_date(competition.end_date)
                if competition.registration_deadline:
                    self.registration_deadline.set_date(competition.registration_deadline)
                
                if competition.max_teams:
                    self.max_teams_var.set(str(competition.max_teams))
                
                # Configurações de pontuação
                if hasattr(competition, 'win_points'):
                    self.win_points_var.set(str(competition.win_points or 3))
                if hasattr(competition, 'draw_points'):
                    self.draw_points_var.set(str(competition.draw_points or 1))
                if hasattr(competition, 'loss_points'):
                    self.loss_points_var.set(str(competition.loss_points or 0))
                
                self.is_active_var.set(competition.is_active)
                # allow_registration seria uma nova propriedade
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados da competição: {str(e)}")
    
    def validate_form(self) -> bool:
        """Valida formulário"""
        if not self.name_var.get().strip():
            messagebox.showerror("Erro", "Nome da competição é obrigatório")
            self.notebook.select(0)  # Aba básica
            self.name_entry.focus()
            return False
        
        if not self.season_var.get().strip():
            messagebox.showerror("Erro", "Temporada é obrigatória")
            self.notebook.select(0)  # Aba básica
            return False
        
        # Validar datas
        start = self.start_date.get_date()
        end = self.end_date.get_date()
        registration = self.registration_deadline.get_date()
        
        if end and start and end < start:
            messagebox.showerror("Erro", "Data de término deve ser posterior à data de início")
            self.notebook.select(1)  # Aba de datas
            return False
        
        if registration and start and registration > start:
            messagebox.showerror("Erro", "Data limite para inscrições deve ser anterior ao início")
            self.notebook.select(1)  # Aba de datas
            return False
        
        return True
    
    def save_competition(self):
        """Salva dados da competição"""
        if not self.validate_form():
            return
        
        try:
            # Preparar dados
            competition_data = {
                'name': self.name_var.get().strip(),
                'competition_type': CompetitionType(self.type_var.get()),
                'season': int(self.season_var.get()),
                'description': self.description_text.get(1.0, tk.END).strip() or None,
                'start_date': self.start_date.get_date(),
                'end_date': self.end_date.get_date(),
                'registration_deadline': self.registration_deadline.get_date(),
                'max_teams': int(self.max_teams_var.get()) if self.max_teams_var.get() else None,
                'is_active': self.is_active_var.get()
            }
            
            # Adicionar configurações de pontuação
            if self.type_var.get() == CompetitionType.LEAGUE.value:
                competition_data.update({
                    'win_points': int(self.win_points_var.get()),
                    'draw_points': int(self.draw_points_var.get()),
                    'loss_points': int(self.loss_points_var.get())
                })
            
            if self.competition_id:
                # Editar competição existente
                success = competition_controller.update_competition(self.competition_id, competition_data)
                message = "Competição atualizada com sucesso!"
            else:
                # Criar nova competição
                competition = competition_controller.create_competition(competition_data)
                success = competition is not None
                message = "Competição criada com sucesso!"
            
            if success:
                self.result = True
                messagebox.showinfo("Sucesso", message)
                self.dialog.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao salvar competição")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar competição: {str(e)}")
    
    def cancel(self):
        """Cancela operação"""
        self.result = False
        self.dialog.destroy()

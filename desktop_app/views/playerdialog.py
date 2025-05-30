"""
Dialog para criação e edição de jogadores
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
from typing import Optional

from desktop_app.controllers.player_controller import player_controller
from desktop_app.controllers.team_controller import team_controller
from database.models import Position


class PlayerDialog:
    """Dialog para gerenciar jogadores"""
    
    def __init__(self, parent, player_id: Optional[int] = None, team_id: Optional[int] = None):
        self.parent = parent
        self.player_id = player_id
        self.team_id = team_id
        self.result = None
        
        # Variáveis de entrada
        self.name_var = tk.StringVar()
        self.shirt_number_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.nationality_var = tk.StringVar(value="Brasil")
        self.team_var = tk.StringVar()
        
        # Listas de dados
        self.teams = []
        self.positions = [pos.value for pos in Position]
        
        # Criar janela
        self.create_dialog()
        
        # Carregar dados
        self.load_teams()
        
        # Se editando, carregar dados do jogador
        if self.player_id:
            self.load_player_data()
        elif self.team_id:
            # Se criando jogador para equipe específica
            self.set_team_selection(self.team_id)
    
    def create_dialog(self):
        """Cria a janela do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Novo Jogador" if not self.player_id else "Editar Jogador")
        self.dialog.geometry("500x600")
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
        title = "Cadastro de Jogador" if not self.player_id else "Editar Jogador"
        title_label = ttk.Label(main_frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook para organizar dados
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # Aba de informações pessoais
        personal_frame = ttk.Frame(self.notebook)
        self.notebook.add(personal_frame, text="Dados Pessoais")
        self.create_personal_form(personal_frame)
        
        # Aba de informações do jogo
        game_frame = ttk.Frame(self.notebook)
        self.notebook.add(game_frame, text="Dados do Jogo")
        self.create_game_form(game_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self.save_player())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Focar no primeiro campo
        self.name_entry.focus()
    
    def create_personal_form(self, parent):
        """Cria formulário de dados pessoais"""
        form_frame = ttk.Frame(parent, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Nome completo
        ttk.Label(form_frame, text="Nome Completo *:").pack(anchor="w")
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=50)
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # Data de nascimento
        ttk.Label(form_frame, text="Data de Nascimento:").pack(anchor="w")
        self.birth_date = DateEntry(form_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd/mm/yyyy',
                                   year=2000)
        self.birth_date.pack(anchor="w", pady=(0, 15))
        
        # Nacionalidade
        ttk.Label(form_frame, text="Nacionalidade:").pack(anchor="w")
        nationality_frame = ttk.Frame(form_frame)
        nationality_frame.pack(fill="x", pady=(0, 15))
        
        self.nationality_combo = ttk.Combobox(nationality_frame, textvariable=self.nationality_var,
                                            values=self.get_countries(), width=30)
        self.nationality_combo.pack(anchor="w")
        
        # Altura e peso
        physical_frame = ttk.Frame(form_frame)
        physical_frame.pack(fill="x", pady=(0, 15))
        
        height_frame = ttk.Frame(physical_frame)
        height_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(height_frame, text="Altura (cm):").pack(anchor="w")
        height_spin = ttk.Spinbox(height_frame, from_=150, to=220, 
                                 textvariable=self.height_var, width=10)
        height_spin.pack(anchor="w")
        
        weight_frame = ttk.Frame(physical_frame)
        weight_frame.pack(side="right", padx=(20, 0))
        ttk.Label(weight_frame, text="Peso (kg):").pack(anchor="w")
        weight_spin = ttk.Spinbox(weight_frame, from_=50, to=120, 
                                 textvariable=self.weight_var, width=10)
        weight_spin.pack(anchor="w")
        
        # Observações
        ttk.Label(form_frame, text="Observações:").pack(anchor="w")
        obs_frame = ttk.Frame(form_frame)
        obs_frame.pack(fill="both", expand=True)
        
        self.observations_text = tk.Text(obs_frame, height=4, wrap="word")
        self.observations_text.pack(side="left", fill="both", expand=True)
        
        obs_scroll = ttk.Scrollbar(obs_frame, orient="vertical", command=self.observations_text.yview)
        self.observations_text.configure(yscrollcommand=obs_scroll.set)
        obs_scroll.pack(side="right", fill="y")
    
    def create_game_form(self, parent):
        """Cria formulário de dados do jogo"""
        form_frame = ttk.Frame(parent, padding="20")
        form_frame.pack(fill="both", expand=True)
        
        # Equipe
        ttk.Label(form_frame, text="Equipe *:").pack(anchor="w")
        self.team_combo = ttk.Combobox(form_frame, textvariable=self.team_var,
                                      state="readonly", width=40)
        self.team_combo.pack(fill="x", pady=(0, 15))
        
        # Número da camisa
        ttk.Label(form_frame, text="Número da Camisa *:").pack(anchor="w")
        number_frame = ttk.Frame(form_frame)
        number_frame.pack(fill="x", pady=(0, 15))
        
        self.shirt_number_spin = ttk.Spinbox(number_frame, from_=1, to=99, 
                                           textvariable=self.shirt_number_var, width=10)
        self.shirt_number_spin.pack(anchor="w")
        
        # Botão para verificar disponibilidade do número
        ttk.Button(number_frame, text="Verificar Disponibilidade", 
                  command=self.check_number_availability).pack(anchor="w", pady=(5, 0))
        
        # Posição
        ttk.Label(form_frame, text="Posição *:").pack(anchor="w")
        self.position_combo = ttk.Combobox(form_frame, textvariable=self.position_var,
                                          values=self.positions, state="readonly", width=20)
        self.position_combo.pack(anchor="w", pady=(0, 15))
        
        # Pé preferido
        ttk.Label(form_frame, text="Pé Preferido:").pack(anchor="w")
        self.preferred_foot_var = tk.StringVar(value="Direito")
        foot_frame = ttk.Frame(form_frame)
        foot_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Radiobutton(foot_frame, text="Direito", variable=self.preferred_foot_var, 
                       value="Direito").pack(side="left")
        ttk.Radiobutton(foot_frame, text="Esquerdo", variable=self.preferred_foot_var, 
                       value="Esquerdo").pack(side="left", padx=(10, 0))
        ttk.Radiobutton(foot_frame, text="Ambos", variable=self.preferred_foot_var, 
                       value="Ambos").pack(side="left", padx=(10, 0))
        
        # Status do jogador
        status_frame = ttk.LabelFrame(form_frame, text="Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 15))
        
        self.is_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(status_frame, text="Jogador Ativo", 
                       variable=self.is_active_var).pack(anchor="w")
        
        self.is_captain_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(status_frame, text="Capitão da Equipe", 
                       variable=self.is_captain_var).pack(anchor="w", pady=(5, 0))
        
        # Estatísticas (apenas para visualização se editando)
        if self.player_id:
            stats_frame = ttk.LabelFrame(form_frame, text="Estatísticas", padding="10")
            stats_frame.pack(fill="x")
            
            self.stats_label = ttk.Label(stats_frame, text="Carregando estatísticas...")
            self.stats_label.pack(anchor="w")
    
    def get_countries(self):
        """Retorna lista de países"""
        return [
            "Brasil", "Argentina", "Uruguai", "Chile", "Paraguai", "Bolívia",
            "Peru", "Colômbia", "Venezuela", "Equador", "Espanha", "Portugal",
            "França", "Alemanha", "Itália", "Inglaterra", "Holanda", "Bélgica",
            "México", "Estados Unidos", "Japão", "Coreia do Sul", "Outro"
        ]
    
    def load_teams(self):
        """Carrega lista de equipes"""
        try:
            self.teams = team_controller.get_all_teams()
            team_names = [f"{team.name} ({team.abbreviation})" for team in self.teams]
            self.team_combo['values'] = team_names
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar equipes: {str(e)}")
    
    def set_team_selection(self, team_id: int):
        """Define equipe selecionada"""
        for i, team in enumerate(self.teams):
            if team.id == team_id:
                self.team_combo.current(i)
                break
    
    def check_number_availability(self):
        """Verifica disponibilidade do número da camisa"""
        if not self.team_var.get() or not self.shirt_number_var.get():
            messagebox.showwarning("Aviso", "Selecione uma equipe e um número")
            return
        
        try:
            # Encontrar ID da equipe selecionada
            team_text = self.team_var.get()
            team_id = None
            for team in self.teams:
                if f"{team.name} ({team.abbreviation})" == team_text:
                    team_id = team.id
                    break
            
            if not team_id:
                return
            
            number = int(self.shirt_number_var.get())
            
            # Verificar se número está disponível
            is_available = player_controller.is_shirt_number_available(
                team_id, number, self.player_id
            )
            
            if is_available:
                messagebox.showinfo("Disponível", f"Número {number} está disponível!")
            else:
                messagebox.showwarning("Indisponível", 
                                     f"Número {number} já está sendo usado por outro jogador")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar número: {str(e)}")
    
    def load_player_data(self):
        """Carrega dados do jogador para edição"""
        try:
            player = player_controller.get_player_by_id(self.player_id)
            if player:
                self.name_var.set(player.name)
                self.shirt_number_var.set(str(player.shirt_number))
                
                if player.position:
                    self.position_var.set(player.position.value)
                
                if player.height:
                    self.height_var.set(str(player.height))
                if player.weight:
                    self.weight_var.set(str(player.weight))
                
                if player.nationality:
                    self.nationality_var.set(player.nationality)
                
                if player.birth_date:
                    self.birth_date.set_date(player.birth_date)
                
                if player.observations:
                    self.observations_text.insert(1.0, player.observations)
                
                # Definir equipe
                if player.team_id:
                    self.set_team_selection(player.team_id)
                
                # Status
                self.is_active_var.set(player.is_active)
                
                # Pé preferido
                if hasattr(player, 'preferred_foot') and player.preferred_foot:
                    self.preferred_foot_var.set(player.preferred_foot)
                
                # Carregar estatísticas
                if hasattr(self, 'stats_label'):
                    self.load_player_stats()
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados do jogador: {str(e)}")
    
    def load_player_stats(self):
        """Carrega estatísticas do jogador"""
        try:
            stats = player_controller.get_player_statistics(self.player_id)
            if stats:
                stats_text = f"Jogos: {stats.get('games', 0)} | "
                stats_text += f"Gols: {stats.get('goals', 0)} | "
                stats_text += f"Assistências: {stats.get('assists', 0)} | "
                stats_text += f"Cartões: {stats.get('yellow_cards', 0)}A {stats.get('red_cards', 0)}V"
                self.stats_label.config(text=stats_text)
            else:
                self.stats_label.config(text="Nenhuma estatística disponível")
        except Exception as e:
            self.stats_label.config(text="Erro ao carregar estatísticas")
    
    def create_buttons(self, parent):
        """Cria botões do dialog"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_player, style="Accent.TButton").pack(side="right")
    
    def validate_form(self) -> bool:
        """Valida formulário"""
        if not self.name_var.get().strip():
            messagebox.showerror("Erro", "Nome do jogador é obrigatório")
            self.notebook.select(0)  # Aba pessoal
            self.name_entry.focus()
            return False
        
        if not self.team_var.get():
            messagebox.showerror("Erro", "Equipe é obrigatória")
            self.notebook.select(1)  # Aba do jogo
            return False
        
        if not self.shirt_number_var.get():
            messagebox.showerror("Erro", "Número da camisa é obrigatório")
            self.notebook.select(1)  # Aba do jogo
            return False
        
        if not self.position_var.get():
            messagebox.showerror("Erro", "Posição é obrigatória")
            self.notebook.select(1)  # Aba do jogo
            return False
        
        # Validar número da camisa
        try:
            number = int(self.shirt_number_var.get())
            if number < 1 or number > 99:
                messagebox.showerror("Erro", "Número da camisa deve ser entre 1 e 99")
                return False
        except ValueError:
            messagebox.showerror("Erro", "Número da camisa deve ser um número válido")
            return False
        
        return True
    
    def save_player(self):
        """Salva dados do jogador"""
        if not self.validate_form():
            return
        
        try:
            # Encontrar ID da equipe selecionada
            team_text = self.team_var.get()
            team_id = None
            for team in self.teams:
                if f"{team.name} ({team.abbreviation})" == team_text:
                    team_id = team.id
                    break
            
            if not team_id:
                messagebox.showerror("Erro", "Equipe inválida")
                return
            
            # Preparar dados
            player_data = {
                'name': self.name_var.get().strip(),
                'team_id': team_id,
                'shirt_number': int(self.shirt_number_var.get()),
                'position': Position(self.position_var.get()),
                'birth_date': self.birth_date.get_date(),
                'height': int(self.height_var.get()) if self.height_var.get() else None,
                'weight': int(self.weight_var.get()) if self.weight_var.get() else None,
                'nationality': self.nationality_var.get().strip() or None,
                'observations': self.observations_text.get(1.0, tk.END).strip() or None,
                'is_active': self.is_active_var.get(),
                'preferred_foot': self.preferred_foot_var.get()
            }
            
            if self.player_id:
                # Editar jogador existente
                success = player_controller.update_player(self.player_id, player_data)
                message = "Jogador atualizado com sucesso!"
            else:
                # Criar novo jogador
                player = player_controller.create_player(player_data)
                success = player is not None
                message = "Jogador criado com sucesso!"
            
            if success:
                self.result = True
                messagebox.showinfo("Sucesso", message)
                self.dialog.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao salvar jogador")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar jogador: {str(e)}")
    
    def cancel(self):
        """Cancela operação"""
        self.result = False
        self.dialog.destroy()

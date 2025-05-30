"""
Dialog para criação e edição de equipes
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from desktop_app.controllers.team_controller import team_controller


class TeamDialog:
    """Dialog para gerenciar equipes"""
    
    def __init__(self, parent, team_id: Optional[int] = None):
        self.parent = parent
        self.team_id = team_id
        self.result = None
        
        # Variáveis de entrada
        self.name_var = tk.StringVar()
        self.abbreviation_var = tk.StringVar()
        self.city_var = tk.StringVar()
        self.state_var = tk.StringVar()
        self.founded_year_var = tk.StringVar()
        self.colors_var = tk.StringVar()
        self.stadium_var = tk.StringVar()
        self.coach_var = tk.StringVar()
        
        # Criar janela
        self.create_dialog()
        
        # Se editando, carregar dados
        if self.team_id:
            self.load_team_data()
    
    def create_dialog(self):
        """Cria a janela do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Nova Equipe" if not self.team_id else "Editar Equipe")
        self.dialog.geometry("500x400")
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
        title = "Cadastro de Equipe" if not self.team_id else "Editar Equipe"
        title_label = ttk.Label(main_frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Formulário
        self.create_form(main_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self.save_team())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Focar no primeiro campo
        self.name_entry.focus()
    
    def create_form(self, parent):
        """Cria formulário de dados"""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Nome da equipe
        ttk.Label(form_frame, text="Nome da Equipe *:").pack(anchor="w")
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=50)
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        # Abreviação
        ttk.Label(form_frame, text="Abreviação *:").pack(anchor="w")
        self.abbreviation_entry = ttk.Entry(form_frame, textvariable=self.abbreviation_var, width=10)
        self.abbreviation_entry.pack(anchor="w", pady=(0, 10))
        
        # Cidade e Estado
        location_frame = ttk.Frame(form_frame)
        location_frame.pack(fill="x", pady=(0, 10))
        
        city_frame = ttk.Frame(location_frame)
        city_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(city_frame, text="Cidade:").pack(anchor="w")
        ttk.Entry(city_frame, textvariable=self.city_var).pack(fill="x")
        
        state_frame = ttk.Frame(location_frame)
        state_frame.pack(side="right", padx=(10, 0))
        ttk.Label(state_frame, text="Estado:").pack(anchor="w")
        ttk.Entry(state_frame, textvariable=self.state_var, width=5).pack()
        
        # Ano de fundação
        ttk.Label(form_frame, text="Ano de Fundação:").pack(anchor="w")
        year_spin = ttk.Spinbox(form_frame, from_=1850, to=2024, 
                               textvariable=self.founded_year_var, width=10)
        year_spin.pack(anchor="w", pady=(0, 10))
        
        # Cores
        ttk.Label(form_frame, text="Cores:").pack(anchor="w")
        ttk.Entry(form_frame, textvariable=self.colors_var, width=30).pack(anchor="w", pady=(0, 10))
        
        # Estádio
        ttk.Label(form_frame, text="Estádio:").pack(anchor="w")
        ttk.Entry(form_frame, textvariable=self.stadium_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Técnico
        ttk.Label(form_frame, text="Técnico:").pack(anchor="w")
        ttk.Entry(form_frame, textvariable=self.coach_var, width=50).pack(fill="x", pady=(0, 10))
        
        # Nota sobre campos obrigatórios
        note_label = ttk.Label(form_frame, text="* Campos obrigatórios", 
                              font=("Arial", 8), foreground="gray")
        note_label.pack(anchor="w", pady=(10, 0))
    
    def create_buttons(self, parent):
        """Cria botões do dialog"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_team, style="Accent.TButton").pack(side="right")
    
    def load_team_data(self):
        """Carrega dados da equipe para edição"""
        try:
            team = team_controller.get_team_by_id(self.team_id)
            if team:
                self.name_var.set(team.name)
                self.abbreviation_var.set(team.abbreviation)
                self.city_var.set(team.city or "")
                self.state_var.set(team.state or "")
                self.founded_year_var.set(str(team.founded_year) if team.founded_year else "")
                self.colors_var.set(team.colors or "")
                self.stadium_var.set(team.stadium or "")
                self.coach_var.set(team.coach or "")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados da equipe: {str(e)}")
    
    def validate_form(self) -> bool:
        """Valida formulário"""
        if not self.name_var.get().strip():
            messagebox.showerror("Erro", "Nome da equipe é obrigatório")
            self.name_entry.focus()
            return False
        
        if not self.abbreviation_var.get().strip():
            messagebox.showerror("Erro", "Abreviação é obrigatória")
            self.abbreviation_entry.focus()
            return False
        
        # Validar ano se preenchido
        year_str = self.founded_year_var.get().strip()
        if year_str:
            try:
                year = int(year_str)
                if year < 1850 or year > 2024:
                    messagebox.showerror("Erro", "Ano deve estar entre 1850 e 2024")
                    return False
            except ValueError:
                messagebox.showerror("Erro", "Ano deve ser um número válido")
                return False
        
        return True
    
    def save_team(self):
        """Salva dados da equipe"""
        if not self.validate_form():
            return
        
        try:
            # Preparar dados
            team_data = {
                'name': self.name_var.get().strip(),
                'abbreviation': self.abbreviation_var.get().strip().upper(),
                'city': self.city_var.get().strip() or None,
                'state': self.state_var.get().strip().upper() or None,
                'founded_year': int(self.founded_year_var.get()) if self.founded_year_var.get().strip() else None,
                'colors': self.colors_var.get().strip() or None,
                'stadium': self.stadium_var.get().strip() or None,
                'coach': self.coach_var.get().strip() or None
            }
            
            if self.team_id:
                # Editar equipe existente
                success = team_controller.update_team(self.team_id, team_data)
                message = "Equipe atualizada com sucesso!"
            else:
                # Criar nova equipe
                team = team_controller.create_team(team_data)
                success = team is not None
                message = "Equipe criada com sucesso!"
            
            if success:
                self.result = True
                messagebox.showinfo("Sucesso", message)
                self.dialog.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao salvar equipe")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar equipe: {str(e)}")
    
    def cancel(self):
        """Cancela operação"""
        self.result = False
        self.dialog.destroy()



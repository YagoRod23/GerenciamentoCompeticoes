"""
Dialog para registrar resultados de um jogo
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from desktop_app.controllers.game_controller import game_controller


class GameResultDialog:
    """Dialog para registrar resultado de um jogo"""
    
    def __init__(self, parent, game_id: Optional[int] = None):
        self.parent = parent
        self.game_id = game_id
        self.result = None
        
        # Variáveis de entrada
        self.home_team_score_var = tk.StringVar()
        self.away_team_score_var = tk.StringVar()
        
        # Criar janela
        self.create_dialog()
        
        # Se game_id fornecido, carregar dados
        if self.game_id:
            self.load_game_data()
    
    def create_dialog(self):
        """Cria a janela do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Registrar Resultado do Jogo")
        self.dialog.geometry("350x200")
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
        title_label = ttk.Label(main_frame, text="Registrar Resultado do Jogo", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Formulário
        self.create_form(main_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self.save_result())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Focar no primeiro campo
        self.home_team_score_entry.focus()
    
    def create_form(self, parent):
        """Cria formulário de entrada de resultado"""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Pontuação do time da casa
        ttk.Label(form_frame, text="Pontuação do Time da Casa *:").pack(anchor="w")
        self.home_team_score_entry = ttk.Entry(form_frame, textvariable=self.home_team_score_var, width=10)
        self.home_team_score_entry.pack(anchor="w", pady=(0, 10))
        
        # Pontuação do time visitante
        ttk.Label(form_frame, text="Pontuação do Time Visitante *:").pack(anchor="w")
        self.away_team_score_entry = ttk.Entry(form_frame, textvariable=self.away_team_score_var, width=10)
        self.away_team_score_entry.pack(anchor="w", pady=(0, 10))

    def create_buttons(self, parent):
        """Cria botões do dialog"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_result, style="Accent.TButton").pack(side="right")
    
    def load_game_data(self):
        """Carrega dados do jogo para edição"""
        try:
            game = game_controller.get_game_by_id(self.game_id)
            if game:
                self.home_team_score_var.set(str(game.home_team_score) if game.home_team_score is not None else "")
                self.away_team_score_var.set(str(game.away_team_score) if game.away_team_score is not None else "")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados do jogo: {str(e)}")
    
    def validate_form(self) -> bool:
        """Valida formulário de resultado"""
        if not self.home_team_score_var.get().strip().isdigit():
            messagebox.showerror("Erro", "A pontuação do time da casa deve ser um número inteiro")
            self.home_team_score_entry.focus()
            return False
        
        if not self.away_team_score_var.get().strip().isdigit():
            messagebox.showerror("Erro", "A pontuação do time visitante deve ser um número inteiro")
            self.away_team_score_entry.focus()
            return False
        
        return True
    
    def save_result(self):
        """Salva resultado do jogo"""
        if not self.validate_form():
            return
        
        try:
            game_result_data = {
                'home_team_score': int(self.home_team_score_var.get().strip()),
                'away_team_score': int(self.away_team_score_var.get().strip())
            }
            
            success = game_controller.update_game_result(self.game_id, game_result_data)
            if success:
                messagebox.showinfo("Sucesso", "Resultado do jogo registrado com sucesso!")
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao registrar resultado do jogo")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar resultado do jogo: {str(e)}")
    
    def cancel(self):
        """Cancela operação"""
        self.result = False
        self.dialog.destroy()

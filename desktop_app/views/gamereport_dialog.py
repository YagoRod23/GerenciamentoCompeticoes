"""
Dialog para gerar e visualizar relatório de jogo
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from desktop_app.controllers.report_controller import report_controller


class GameReportDialog:
    """Dialog para visualização de relatório de jogo"""
    
    def __init__(self, parent, game_id: Optional[int] = None):
        self.parent = parent
        self.game_id = game_id
        self.report_content = ""
        
        # Criar janela
        self.create_dialog()
        
        # Se game_id fornecido, carregar relatório
        if self.game_id:
            self.load_game_report()
    
    def create_dialog(self):
        """Cria a janela do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Relatório do Jogo")
        self.dialog.geometry("600x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centralizar janela
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Relatório do Jogo", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Conteúdo do relatório
        self.create_report_content(main_frame)
        
        # Botões
        self.create_buttons(main_frame)
    
    def create_report_content(self, parent):
        """Cria campo para exibição do relatório"""
        report_frame = ttk.Frame(parent)
        report_frame.pack(fill="both", expand=True)
        
        self.report_text = tk.Text(report_frame, height=15, wrap="word")
        self.report_text.pack(side="left", fill="both", expand=True)
        
        report_scroll = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scroll.set)
        report_scroll.pack(side="right", fill="y")
    
    def create_buttons(self, parent):
        """Cria botões do dialog"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Fechar", 
                  command=self.close).pack(side="right")
    
    def load_game_report(self):
        """Carrega relatório do jogo"""
        try:
            report = report_controller.generate_game_report(self.game_id)
            self.report_content = report
            self.report_text.insert(1.0, self.report_content)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar relatório do jogo: {str(e)}")
    
    def close(self):
        """Fecha o diálogo"""
        self.dialog.destroy()

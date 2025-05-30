"""
Dialog para gerenciar eventos de um jogo
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from desktop_app.controllers.game_event_controller import game_event_controller
from desktop_app.controllers.game_controller import game_controller
from desktop_app.controllers.player_controller import player_controller


class GameEventsDialog:
    """Dialog para visualização e gerenciamento de eventos de um jogo"""
    
    def __init__(self, parent, game_id: Optional[int] = None):
        self.parent = parent
        self.game_id = game_id
        self.result = None
        
        # Variáveis e dados
        self.event_list = []
        self.selected_event = None
        
        # Criar janela
        self.create_dialog()
        
        # Carregar dados se game_id foi fornecido
        if self.game_id:
            self.load_game_events()
    
    def create_dialog(self):
        """Cria a janela do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Eventos do Jogo")
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
        title_label = ttk.Label(main_frame, text="Gerenciamento de Eventos do Jogo", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Lista de eventos
        self.create_events_list(main_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self.save_events())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def create_events_list(self, parent):
        """Cria lista de eventos"""
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.events_tree = ttk.Treeview(list_frame, columns=("minuto", "tipo", "jogador"), show="headings")
        self.events_tree.heading("minuto", text="Minuto")
        self.events_tree.heading("tipo", text="Tipo de Evento")
        self.events_tree.heading("jogador", text="Jogador")
        
        self.events_tree.pack(fill="both", expand=True, side="left")
        
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=list_scroll.set)
        list_scroll.pack(side="right", fill="y")
        
        # Botões de adição e remoção
        add_button = ttk.Button(parent, text="Adicionar Evento", command=self.add_event)
        add_button.pack(side="left", padx=(0, 5))
        
        remove_button = ttk.Button(parent, text="Remover Selecionado", command=self.remove_selected_event)
        remove_button.pack(side="left")
    
    def create_buttons(self, parent):
        """Cria botões do dialog"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_events, style="Accent.TButton").pack(side="right")
    
    def load_game_events(self):
        """Carrega eventos do jogo para edição"""
        try:
            self.event_list = game_event_controller.get_events_by_game_id(self.game_id)
            self.populate_tree()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar eventos do jogo: {str(e)}")
    
    def populate_tree(self):
        """Popula a treeview com eventos"""
        for event in self.events_tree.get_children():
            self.events_tree.delete(event)
        
        for event in self.event_list:
            player = player_controller.get_player_by_id(event.player_id)
            player_name = player.name if player else "Desconhecido"
            
            event_data = (
                event.minute,
                event.event_type,
                player_name
            )
            self.events_tree.insert('', 'end', values=event_data)
    
    def add_event(self):
        """Adiciona novo evento"""
        from .event_entry_dialog import EventEntryDialog
        dialog = EventEntryDialog(self.dialog, game_id=self.game_id)
        
        if dialog.result:
            event_data = dialog.result
            self.event_list.append(event_data)
            self.populate_tree()
    
    def remove_selected_event(self):
        """Remove o evento selecionado"""
        selected_item = self.events_tree.selection()
        if selected_item:
            event_idx = self.events_tree.index(selected_item)
            self.event_list.pop(event_idx)
            self.populate_tree()
    
    def save_events(self):
        """Salva eventos do jogo"""
        try:
            success = game_event_controller.save_events(self.game_id, self.event_list)
            if success:
                messagebox.showinfo("Sucesso", "Eventos salvos com sucesso!")
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao salvar eventos do jogo")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar eventos do jogo: {str(e)}")
    
    def cancel(self):
        """Cancela operação"""
        self.result = False
        self.dialog.destroy()

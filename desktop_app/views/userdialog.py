"""
Dialog para criação e edição de usuários
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from desktop_app.controllers.user_controller import user_controller
from database.models import UserType


class UserDialog:
    """Dialog para gerenciar usuários"""
    
    def __init__(self, parent, user_id: Optional[int] = None):
        self.parent = parent
        self.user_id = user_id
        self.result = None
        
        # Variáveis de entrada
        self.full_name_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.user_type_var = tk.StringVar(value=UserType.MEMBER.value)
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        self.is_active_var = tk.BooleanVar(value=True)
        
        # Criar janela
        self.create_dialog()
        
        # Se editando, carregar dados
        if self.user_id:
            self.load_user_data()
    
    def create_dialog(self):
        """Cria a janela do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Novo Usuário" if not self.user_id else "Editar Usuário")
        self.dialog.geometry("450x500")
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
        title = "Cadastro de Usuário" if not self.user_id else "Editar Usuário"
        title_label = ttk.Label(main_frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Formulário
        self.create_form(main_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self.save_user())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Focar no primeiro campo
        self.full_name_entry.focus()
    
    def create_form(self, parent):
        """Cria formulário de dados"""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Nome completo
        ttk.Label(form_frame, text="Nome Completo *:").pack(anchor="w")
        self.full_name_entry = ttk.Entry(form_frame, textvariable=self.full_name_var, width=40)
        self.full_name_entry.pack(fill="x", pady=(0, 10))
        
        # Nome de usuário
        ttk.Label(form_frame, text="Nome de Usuário *:").pack(anchor="w")
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=40)
        self.username_entry.pack(fill="x", pady=(0, 10))
        
        # E-mail
        ttk.Label(form_frame, text="E-mail:").pack(anchor="w")
        self.email_entry = ttk.Entry(form_frame, textvariable=self.email_var, width=40)
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        # Tipo de usuário
        ttk.Label(form_frame, text="Tipo de Usuário *:").pack(anchor="w")
        user_type_combo = ttk.Combobox(form_frame, textvariable=self.user_type_var, 
                                       values=[ut.value for ut in UserType], state="readonly")
        user_type_combo.pack(fill="x", pady=(0, 10))
        
        # Senha
        ttk.Label(form_frame, text="Senha *:").pack(anchor="w")
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show='*', width=40)
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        # Confirmar Senha
        ttk.Label(form_frame, text="Confirme a Senha *:").pack(anchor="w")
        self.confirm_password_entry = ttk.Entry(form_frame, textvariable=self.confirm_password_var, show='*', width=40)
        self.confirm_password_entry.pack(fill="x", pady=(0, 10))
        
        # Usuário ativo
        ttk.Checkbutton(form_frame, text="Usuário Ativo", variable=self.is_active_var).pack(anchor="w", pady=(5, 0))
    
    def create_buttons(self, parent):
        """Cria botões do dialog"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Salvar", 
                  command=self.save_user, style="Accent.TButton").pack(side="right")
    
    def load_user_data(self):
        """Carrega dados do usuário para edição"""
        try:
            user = user_controller.get_user_by_id(self.user_id)
            if user:
                self.full_name_var.set(user.full_name)
                self.username_var.set(user.username)
                self.email_var.set(user.email)
                self.user_type_var.set(user.user_type.value)
                self.is_active_var.set(user.is_active)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados do usuário: {str(e)}")
    
    def validate_form(self) -> bool:
        """Valida formulário"""
        if not self.full_name_var.get().strip():
            messagebox.showerror("Erro", "Nome completo é obrigatório")
            self.full_name_entry.focus()
            return False
        
        if not self.username_var.get().strip():
            messagebox.showerror("Erro", "Nome de usuário é obrigatório")
            self.username_entry.focus()
            return False
        
        if not self.password_var.get() == self.confirm_password_var.get():
            messagebox.showerror("Erro", "As senhas não coincidem")
            self.password_entry.focus()
            return False
        
        return True
    
    def save_user(self):
        """Salva dados do usuário"""
        if not self.validate_form():
            return
        
        try:
            # Preparar dados
            user_data = {
                'full_name': self.full_name_var.get().strip(),
                'username': self.username_var.get().strip(),
                'email': self.email_var.get().strip() or None,
                'user_type': UserType(self.user_type_var.get()),
                'password': self.password_var.get().strip(),
                'is_active': self.is_active_var.get()
            }
            
            if self.user_id:
                # Editar usuário existente
                success = user_controller.update_user(self.user_id, user_data)
                message = "Usuário atualizado com sucesso!"
            else:
                # Criar novo usuário
                user = user_controller.create_user(user_data)
                success = user is not None
                message = "Usuário criado com sucesso!"
            
            if success:
                self.result = True
                messagebox.showinfo("Sucesso", message)
                self.dialog.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao salvar usuário")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar usuário: {str(e)}")
    
    def cancel(self):
        """Cancela operação"""
        self.result = False
        self.dialog.destroy()

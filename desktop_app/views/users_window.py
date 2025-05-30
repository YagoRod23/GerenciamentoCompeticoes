"""
Janela de registro de usuário
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional

from .base_window import BaseWindow
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType


class RegisterWindow(BaseWindow):
    """Janela de registro"""
    
    def __init__(self):
        super().__init__("Registro - Sistema de Gestão Esportiva", 450, 600)
        
        # Widgets
        self.full_name_entry: Optional[ttk.Entry] = None
        self.username_entry: Optional[ttk.Entry] = None
        self.email_entry: Optional[ttk.Entry] = None
        self.password_entry: Optional[ttk.Entry] = None
        self.confirm_password_entry: Optional[ttk.Entry] = None
        self.user_type_var: Optional[tk.StringVar] = None
        self.organization_entry: Optional[ttk.Entry] = None
        self.register_button: Optional[ttk.Button] = None
        self.status_label: Optional[ttk.Label] = None
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Configura interface de registro"""
        # Frame principal com scroll
        main_canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo do registro
        content_frame = ttk.Frame(scrollable_frame, padding="30")
        content_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = ttk.Label(content_frame, text="Criar Nova Conta", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 30))
        
        # Formulário
        form_frame = ttk.Frame(content_frame)
        form_frame.pack(fill="x")
        
        # Nome completo
        ttk.Label(form_frame, text="Nome Completo:").pack(anchor="w")
        self.full_name_entry = ttk.Entry(form_frame, font=("Arial", 11))
        self.full_name_entry.pack(fill="x", pady=(5, 15))
        self.full_name_entry.focus()
        
        # Nome de usuário
        ttk.Label(form_frame, text="Nome de Usuário:").pack(anchor="w")
        self.username_entry = ttk.Entry(form_frame, font=("Arial", 11))
        self.username_entry.pack(fill="x", pady=(5, 15))
        
        # Email
        ttk.Label(form_frame, text="Email:").pack(anchor="w")
        self.email_entry = ttk.Entry(form_frame, font=("Arial", 11))
        self.email_entry.pack(fill="x", pady=(5, 15))
        
        # Tipo de usuário
        ttk.Label(form_frame, text="Tipo de Usuário:").pack(anchor="w")
        self.user_type_var = tk.StringVar(value="TEAM")
        
        user_types = [
            ("Equipe", "TEAM"),
            ("Organização", "ORGANIZATION"),
        ]
        
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill="x", pady=(5, 15))
        
        for text, value in user_types:
            ttk.Radiobutton(type_frame, text=text, variable=self.user_type_var,
                           value=value, command=self.on_type_change).pack(anchor="w")
        
        # Organização (apenas para tipo organização)
        self.org_label = ttk.Label(form_frame, text="Organização:")
        self.organization_entry = ttk.Entry(form_frame, font=("Arial", 11))
        
        # Senha
        ttk.Label(form_frame, text="Senha:").pack(anchor="w")
        self.password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 11))
        self.password_entry.pack(fill="x", pady=(5, 15))
        
        # Confirmar senha
        ttk.Label(form_frame, text="Confirmar Senha:").pack(anchor="w")
        self.confirm_password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 11))
        self.confirm_password_entry.pack(fill="x", pady=(5, 20))
        
        # Botões
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x")
        
        self.register_button = ttk.Button(button_frame, text="Registrar", 
                                        command=self.do_register, style="Accent.TButton")
        self.register_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.close)
        cancel_button.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Status
        self.status_label = ttk.Label(form_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))
        
        # Configurar visibilidade inicial
        self.on_type_change()
    
    def on_type_change(self):
        """Chamado quando muda o tipo de usuário"""
        if self.user_type_var.get() == "ORGANIZATION":
            self.org_label.pack(anchor="w")
            self.organization_entry.pack(fill="x", pady=(5, 15))
        else:
            self.org_label.pack_forget()
            self.organization_entry.pack_forget()
    
    def do_register(self):
        """Realiza o registro"""
        # Validar campos
        full_name = self.full_name_entry.get().strip()
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        user_type = self.user_type_var.get()
        organization = self.organization_entry.get().strip() if user_type == "ORGANIZATION" else None
        
        # Validações
        if not all([full_name, username, email, password, confirm_password]):
            self.status_label.config(text="Preencha todos os campos obrigatórios")
            return
        
        if user_type == "ORGANIZATION" and not organization:
            self.status_label.config(text="Preencha o campo Organização")
            return
        
        if password != confirm_password:
            self.status_label.config(text="Senhas não coincidem")
            return
        
        if len(password) < 6:
            self.status_label.config(text="Senha deve ter pelo menos 6 caracteres")
            return
        
        # Validar email básico
        if "@" not in email or "." not in email:
            self.status_label.config(text="Email inválido")
            return
        
        # Desabilitar botão durante registro
        self.register_button.config(state="disabled", text="Registrando...")
        self.status_label.config(text="")
        self.window.update()
        
        try:
            success, message = auth_controller.register(
                full_name=full_name,
                username=username,
                email=email,
                password=password,
                user_type=UserType(user_type),
                organization=organization
            )
            
            if success:
                self.show_message("Sucesso", "Conta criada com sucesso!\nFaça login para continuar.", "info")
                self.close()
            else:
                self.status_label.config(text=message)
                
        except Exception as e:
            self.status_label.config(text=f"Erro no registro: {str(e)}")
        
        finally:
            self.register_button.config(state="normal", text="Registrar")
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")


### desktop_app/views/teams_window.py


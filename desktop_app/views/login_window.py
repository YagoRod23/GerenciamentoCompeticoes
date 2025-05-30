"""
Janela de login do sistema
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from .base_window import BaseWindow
from desktop_app.controllers.auth_controller import auth_controller


class LoginWindow(BaseWindow):
    """Janela de login"""
    
    def __init__(self, on_success_callback: Optional[Callable] = None):
        super().__init__("Login - Sistema de Gestão Esportiva", 400, 300)
        self.on_success_callback = on_success_callback
        
        # Widgets
        self.username_entry: Optional[ttk.Entry] = None
        self.password_entry: Optional[ttk.Entry] = None
        self.remember_var: Optional[tk.BooleanVar] = None
        self.login_button: Optional[ttk.Button] = None
        self.status_label: Optional[ttk.Label] = None
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Configura interface de login"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.pack(fill="both", expand=True)
        
        # Logo/Título
        title_label = ttk.Label(main_frame, text="Sistema de Gestão Esportiva", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 30))
        
        # Frame do formulário
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x")
        
        # Campo usuário
        ttk.Label(form_frame, text="Usuário:").pack(anchor="w")
        self.username_entry = ttk.Entry(form_frame, font=("Arial", 11))
        self.username_entry.pack(fill="x", pady=(5, 15))
        self.username_entry.focus()
        
        # Campo senha
        ttk.Label(form_frame, text="Senha:").pack(anchor="w")
        self.password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 11))
        self.password_entry.pack(fill="x", pady=(5, 15))
        
        # Checkbox lembrar
        self.remember_var = tk.BooleanVar()
        remember_check = ttk.Checkbutton(form_frame, text="Lembrar usuário", 
                                       variable=self.remember_var)
        remember_check.pack(anchor="w", pady=(0, 20))
        
        # Botão login
        self.login_button = ttk.Button(form_frame, text="Entrar", 
                                     command=self.do_login, style="Accent.TButton")
        self.login_button.pack(fill="x", pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(form_frame, text="", foreground="red")
        self.status_label.pack()
        
        # Binds
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.do_login())
        
        # Link para registro (se permitido)
        register_frame = ttk.Frame(main_frame)
        register_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Label(register_frame, text="Não tem conta?").pack(side="left")
        register_link = ttk.Label(register_frame, text="Registrar", 
                                foreground="blue", cursor="hand2")
        register_link.pack(side="left", padx=(5, 0))
        register_link.bind("<Button-1>", lambda e: self.show_register())
    
    def do_login(self):
        """Realiza o login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="Preencha todos os campos")
            return
        
        # Desabilitar botão durante login
        self.login_button.config(state="disabled", text="Entrando...")
        self.status_label.config(text="")
        self.window.update()
        
        try:
            success, message = auth_controller.login(username, password)
            
            if success:
                # Salvar preferência de lembrar
                if self.remember_var.get():
                    # Implementar salvamento de preferências
                    pass
                
                # Chamar callback de sucesso
                if self.on_success_callback:
                    self.on_success_callback()
                
                self.close()
            else:
                self.status_label.config(text=message)
                
        except Exception as e:
            self.status_label.config(text=f"Erro no login: {str(e)}")
        
        finally:
            self.login_button.config(state="normal", text="Entrar")
    
    def show_register(self):
        """Exibe janela de registro"""
        from .register_window import RegisterWindow
        register_window = RegisterWindow()
        register_window.run()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        
        # Obter dimensões da tela
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calcular posição central
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")


def show_login(on_success_callback: Optional[Callable] = None) -> LoginWindow:
    """Função auxiliar para exibir janela de login"""
    return LoginWindow(on_success_callback)


### desktop_app/views/register_window.py


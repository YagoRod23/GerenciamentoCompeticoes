"""
Rotas públicas (login, logout, etc)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from database.database import SessionLocal
from database.models import User

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    """Página inicial"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('public/index.html')


@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Username e senha são obrigatórios.', 'error')
            return render_template('public/login.html')
        
        session = SessionLocal()
        try:
            user = session.query(User).filter_by(username=username).first()
            
            if user and user.is_active and check_password_hash(user.password_hash, password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Credenciais inválidas ou usuário inativo.', 'error')
        finally:
            session.close()
    return redirect(url_for('index')) 
    return render_template('public/login.html')


@public_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('public.index'))


@public_bp.route('/about')
def about():
    """Página sobre o sistema"""
    return render_template('public/about.html')


@public_bp.route('/contact')
def contact():
    """Página de contato"""
    return render_template('public/contact.html')

"""
Rotas para gestão de usuários
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from database.database import SessionLocal
from database.models import User, UserType
from desktop_app.controllers.user_controller import user_controller

user_bp = Blueprint('users', __name__)


@user_bp.route('/')
@login_required
def list_users():
    """Lista todos os usuários"""
    if current_user.user_type != UserType.ADMIN:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard.index'))
    
    session = SessionLocal()
    try:
        users = session.query(User).all()
        return render_template('users/list.html', users=users)
    finally:
        session.close()


@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Cria novo usuário"""
    if current_user.user_type != UserType.ADMIN:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        user_data = {
            'full_name': request.form.get('full_name'),
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'user_type': request.form.get('user_type'),
            'is_active': 'is_active' in request.form
        }
        
        if user_controller.create_user(user_data):
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('users.list_users'))
        else:
            flash('Erro ao criar usuário.', 'error')
    
    return render_template('users/form.html')


@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edita usuário existente"""
    if current_user.user_type != UserType.ADMIN and current_user.id != user_id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard.index'))
    
    user = user_controller.get_user_by_id(user_id)
    if not user:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('users.list_users'))
    
    if request.method == 'POST':
        user_data = {
            'full_name': request.form.get('full_name'),
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'user_type': request.form.get('user_type'),
            'is_active': 'is_active' in request.form
        }
        
        # Atualizar senha apenas se fornecida
        new_password = request.form.get('password')
        if new_password:
            user_data['password'] = new_password
        
        if user_controller.update_user(user_id, user_data):
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('users.list_users'))
        else:
            flash('Erro ao atualizar usuário.', 'error')
    
    return render_template('users/form.html', user=user)


@user_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Deleta usuário"""
    if current_user.user_type != UserType.ADMIN:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard.index'))
    
    if current_user.id == user_id:
        flash('Você não pode deletar seu próprio usuário.', 'error')
        return redirect(url_for('users.list_users'))
    
    if user_controller.delete_user(user_id):
        flash('Usuário deletado com sucesso!', 'success')
    else:
        flash('Erro ao deletar usuário.', 'error')
    
    return redirect(url_for('users.list_users'))


@user_bp.route('/profile')
@login_required
def profile():
    """Perfil do usuário logado"""
    return render_template('users/profile.html', user=current_user)


@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Alterar senha do usuário"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('users/change_password.html')
        
        if new_password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('users/change_password.html')
        
        if user_controller.change_password(current_user.id, current_password, new_password):
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('users.profile'))
        else:
            flash('Senha atual incorreta ou erro ao alterar senha.', 'error')
    
    return render_template('users/change_password.html')

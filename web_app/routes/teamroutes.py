"""
Rotas para gestão de equipes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from database.database import SessionLocal
from database.models import Team
from desktop_app.controllers.team_controller import team_controller

team_bp = Blueprint('teams', __name__)


@team_bp.route('/')
@login_required
def list_teams():
    """Lista todas as equipes"""
    session = SessionLocal()
    try:
        teams = session.query(Team).all()
        return render_template('teams/list.html', teams=teams)
    finally:
        session.close()


@team_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_team():
    """Cria nova equipe"""
    if request.method == 'POST':
        team_data = {
            'name': request.form.get('name'),
            'abbreviation': request.form.get('abbreviation'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'founded_year': request.form.get('founded_year'),
            'colors': request.form.get('colors'),
            'stadium': request.form.get('stadium'),
            'coach': request.form.get('coach')
        }
        
        if team_controller.create_team(team_data):
            flash('Equipe criada com sucesso!', 'success')
            return redirect(url_for('teams.list_teams'))
        else:
            flash('Erro ao criar equipe.', 'error')
    
    return render_template('teams/form.html')


@team_bp.route('/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    """Edita equipe existente"""
    team = team_controller.get_team_by_id(team_id)
    if not team:
        flash('Equipe não encontrada.', 'error')
        return redirect(url_for('teams.list_teams'))
    
    if request.method == 'POST':
        team_data = {
            'name': request.form.get('name'),
            'abbreviation': request.form.get('abbreviation'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'founded_year': request.form.get('founded_year'),
            'colors': request.form.get('colors'),
            'stadium': request.form.get('stadium'),
            'coach': request.form.get('coach')
        }
        
        if team_controller.update_team(team_id, team_data):
            flash('Equipe atualizada com sucesso!', 'success')
            return redirect(url_for('teams.list_teams'))
        else:
            flash('Erro ao atualizar equipe.', 'error')
    
    return render_template('teams/form.html', team=team)


@team_bp.route('/<int:team_id>/delete', methods=['POST'])
@login_required
def delete_team(team_id):
    """Deleta equipe"""
    if team_controller.delete_team(team_id):
        flash('Equipe deletada com sucesso!', 'success')
    else:
        flash('Erro ao deletar equipe.', 'error')
    
    return redirect(url_for('teams.list_teams'))


@team_bp.route('/<int:team_id>')
@login_required
def view_team(team_id):
    """Visualiza detalhes da equipe"""
    team = team_controller.get_team_by_id(team_id)
    if not team:
        flash('Equipe não encontrada.', 'error')
        return redirect(url_for('teams.list_teams'))
    
    return render_template('teams/detail.html', team=team)

"""
Rotas para gestão de competições
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from database.database import SessionLocal
from database.models import Competition, Team
from desktop_app.controllers.competition_controller import competition_controller
from desktop_app.controllers.team_controller import team_controller

competition_bp = Blueprint('competitions', __name__)


@competition_bp.route('/')
@login_required
def list_competitions():
    """Lista todas as competições"""
    session = SessionLocal()
    try:
        competitions = session.query(Competition).all()
        return render_template('competitions/list.html', competitions=competitions)
    finally:
        session.close()


@competition_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_competition():
    """Cria nova competição"""
    if request.method == 'POST':
        competition_data = {
            'name': request.form.get('name'),
            'competition_type': request.form.get('competition_type'),
            'season': request.form.get('season'),
            'description': request.form.get('description'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'registration_deadline': request.form.get('registration_deadline'),
            'max_teams': request.form.get('max_teams'),
            'is_active': 'is_active' in request.form
        }
        
        if competition_controller.create_competition(competition_data):
            flash('Competição criada com sucesso!', 'success')
            return redirect(url_for('competitions.list_competitions'))
        else:
            flash('Erro ao criar competição.', 'error')
    
    return render_template('competitions/form.html')


@competition_bp.route('/<int:competition_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_competition(competition_id):
    """Edita competição existente"""
    competition = competition_controller.get_competition_by_id(competition_id)
    if not competition:
        flash('Competição não encontrada.', 'error')
        return redirect(url_for('competitions.list_competitions'))
    
    if request.method == 'POST':
        competition_data = {
            'name': request.form.get('name'),
            'competition_type': request.form.get('competition_type'),
            'season': request.form.get('season'),
            'description': request.form.get('description'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'registration_deadline': request.form.get('registration_deadline'),
            'max_teams': request.form.get('max_teams'),
            'is_active': 'is_active' in request.form
        }
        
        if competition_controller.update_competition(competition_id, competition_data):
            flash('Competição atualizada com sucesso!', 'success')
            return redirect(url_for('competitions.list_competitions'))
        else:
            flash('Erro ao atualizar competição.', 'error')
    
    return render_template('competitions/form.html', competition=competition)


@competition_bp.route('/<int:competition_id>/delete', methods=['POST'])
@login_required
def delete_competition(competition_id):
    """Deleta competição"""
    if competition_controller.delete_competition(competition_id):
        flash('Competição deletada com sucesso!', 'success')
    else:
        flash('Erro ao deletar competição.', 'error')
    
    return redirect(url_for('competitions.list_competitions'))


@competition_bp.route('/<int:competition_id>')
@login_required
def view_competition(competition_id):
    """Visualiza detalhes da competição"""
    competition = competition_controller.get_competition_by_id(competition_id)
    if not competition:
        flash('Competição não encontrada.', 'error')
        return redirect(url_for('competitions.list_competitions'))
    
    return render_template('competitions/detail.html', competition=competition)


@competition_bp.route('/<int:competition_id>/standings')
@login_required
def competition_standings(competition_id):
    """Mostra classificação da competição"""
    competition = competition_controller.get_competition_by_id(competition_id)
    if not competition:
        flash('Competição não encontrada.', 'error')
        return redirect(url_for('competitions.list_competitions'))
    
    # Aqui você implementaria a lógica para calcular a classificação
    standings = []  # Placeholder
    
    return render_template('competitions/standings.html', 
                         competition=competition, 
                         standings=standings)


@competition_bp.route('/<int:competition_id>/register-team', methods=['POST'])
@login_required
def register_team(competition_id):
    """Registra equipe na competição"""
    team_id = request.form.get('team_id')
    
    if competition_controller.register_team_in_competition(competition_id, team_id):
        flash('Equipe registrada com sucesso!', 'success')
    else:
        flash('Erro ao registrar equipe.', 'error')
    
    return redirect(url_for('competitions.view_competition', competition_id=competition_id))

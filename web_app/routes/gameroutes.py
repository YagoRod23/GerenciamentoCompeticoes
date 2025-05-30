"""
Rotas para gestão de jogos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from database.database import SessionLocal
from database.models import Game, Team, Competition
from desktop_app.controllers.game_controller import game_controller
from desktop_app.controllers.team_controller import team_controller
from desktop_app.controllers.competition_controller import competition_controller

game_bp = Blueprint('games', __name__)


@game_bp.route('/')
@login_required
def list_games():
    """Lista todos os jogos"""
    session = SessionLocal()
    try:
        games = session.query(Game).order_by(Game.game_date.desc()).all()
        return render_template('games/list.html', games=games)
    finally:
        session.close()


@game_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_game():
    """Cria novo jogo"""
    if request.method == 'POST':
        game_data = {
            'home_team_id': request.form.get('home_team_id'),
            'away_team_id': request.form.get('away_team_id'),
            'competition_id': request.form.get('competition_id'),
            'game_date': request.form.get('game_date'),
            'game_time': request.form.get('game_time'),
            'location': request.form.get('location'),
            'round_number': request.form.get('round_number')
        }
        
        if game_controller.create_game(game_data):
            flash('Jogo criado com sucesso!', 'success')
            return redirect(url_for('games.list_games'))
        else:
            flash('Erro ao criar jogo.', 'error')
    
    teams = team_controller.get_all_teams()
    competitions = competition_controller.get_all_competitions()
    return render_template('games/form.html', teams=teams, competitions=competitions)


@game_bp.route('/<int:game_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_game(game_id):
    """Edita jogo existente"""
    game = game_controller.get_game_by_id(game_id)
    if not game:
        flash('Jogo não encontrado.', 'error')
        return redirect(url_for('games.list_games'))
    
    if request.method == 'POST':
        game_data = {
            'home_team_id': request.form.get('home_team_id'),
            'away_team_id': request.form.get('away_team_id'),
            'competition_id': request.form.get('competition_id'),
            'game_date': request.form.get('game_date'),
            'game_time': request.form.get('game_time'),
            'location': request.form.get('location'),
            'round_number': request.form.get('round_number'),
            'home_team_score': request.form.get('home_team_score'),
            'away_team_score': request.form.get('away_team_score'),
            'status': request.form.get('status')
        }
        
        if game_controller.update_game(game_id, game_data):
            flash('Jogo atualizado com sucesso!', 'success')
            return redirect(url_for('games.list_games'))
        else:
            flash('Erro ao atualizar jogo.', 'error')
    
    teams = team_controller.get_all_teams()
    competitions = competition_controller.get_all_competitions()
    return render_template('games/form.html', game=game, teams=teams, competitions=competitions)


@game_bp.route('/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    """Deleta jogo"""
    if game_controller.delete_game(game_id):
        flash('Jogo deletado com sucesso!', 'success')
    else:
        flash('Erro ao deletar jogo.', 'error')
    
    return redirect(url_for('games.list_games'))


@game_bp.route('/<int:game_id>')
@login_required
def view_game(game_id):
    """Visualiza detalhes do jogo"""
    game = game_controller.get_game_by_id(game_id)
    if not game:
        flash('Jogo não encontrado.', 'error')
        return redirect(url_for('games.list_games'))
    
    return render_template('games/detail.html', game=game)


@game_bp.route('/<int:game_id>/events')
@login_required
def game_events(game_id):
    """Gerencia eventos do jogo"""
    game = game_controller.get_game_by_id(game_id)
    if not game:
        flash('Jogo não encontrado.', 'error')
        return redirect(url_for('games.list_games'))
    
    return render_template('games/events.html', game=game)


@game_bp.route('/<int:game_id>/result', methods=['GET', 'POST'])
@login_required
def update_result(game_id):
    """Atualiza resultado do jogo"""
    game = game_controller.get_game_by_id(game_id)
    if not game:
        flash('Jogo não encontrado.', 'error')
        return redirect(url_for('games.list_games'))
    
    if request.method == 'POST':
        result_data = {
            'home_team_score': request.form.get('home_team_score'),
            'away_team_score': request.form.get('away_team_score'),
            'status': 'FINISHED'
        }
        
        if game_controller.update_game_result(game_id, result_data):
            flash('Resultado atualizado com sucesso!', 'success')
            return redirect(url_for('games.view_game', game_id=game_id))
        else:
            flash('Erro ao atualizar resultado.', 'error')
    
    return render_template('games/result.html', game=game)

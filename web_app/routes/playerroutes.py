"""
Rotas para gestão de jogadores
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from database.database import SessionLocal
from database.models import Player, Team
from desktop_app.controllers.player_controller import player_controller
from desktop_app.controllers.team_controller import team_controller

player_bp = Blueprint('players', __name__)


@player_bp.route('/')
@login_required
def list_players():
    """Lista todos os jogadores"""
    session = SessionLocal()
    try:
        players = session.query(Player).all()
        return render_template('players/list.html', players=players)
    finally:
        session.close()


@player_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_player():
    """Cria novo jogador"""
    if request.method == 'POST':
        player_data = {
            'name': request.form.get('name'),
            'position': request.form.get('position'),
            'age': request.form.get('age'),
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'nationality': request.form.get('nationality'),
            'team_id': request.form.get('team_id') if request.form.get('team_id') else None
        }
        
        if player_controller.create_player(player_data):
            flash('Jogador criado com sucesso!', 'success')
            return redirect(url_for('players.list_players'))
        else:
            flash('Erro ao criar jogador.', 'error')
    
    teams = team_controller.get_all_teams()
    return render_template('players/form.html', teams=teams)


@player_bp.route('/<int:player_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_player(player_id):
    """Edita jogador existente"""
    player = player_controller.get_player_by_id(player_id)
    if not player:
        flash('Jogador não encontrado.', 'error')
        return redirect(url_for('players.list_players'))
    
    if request.method == 'POST':
        player_data = {
            'name': request.form.get('name'),
            'position': request.form.get('position'),
            'age': request.form.get('age'),
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'nationality': request.form.get('nationality'),
            'team_id': request.form.get('team_id') if request.form.get('team_id') else None
        }
        
        if player_controller.update_player(player_id, player_data):
            flash('Jogador atualizado com sucesso!', 'success')
            return redirect(url_for('players.list_players'))
        else:
            flash('Erro ao atualizar jogador.', 'error')
    
    teams = team_controller.get_all_teams()
    return render_template('players/form.html', player=player, teams=teams)


@player_bp.route('/<int:player_id>/delete', methods=['POST'])
@login_required
def delete_player(player_id):
    """Deleta jogador"""
    if player_controller.delete_player(player_id):
        flash('Jogador deletado com sucesso!', 'success')
    else:
        flash('Erro ao deletar jogador.', 'error')
    
    return redirect(url_for('players.list_players'))


@player_bp.route('/<int:player_id>')
@login_required
def view_player(player_id):
    """Visualiza detalhes do jogador"""
    player = player_controller.get_player_by_id(player_id)
    if not player:
        flash('Jogador não encontrado.', 'error')
        return redirect(url_for('players.list_players'))
    
    return render_template('players/detail.html', player=player)


@player_bp.route('/api/by-team/<int:team_id>')
@login_required
def api_players_by_team(team_id):
    """API para obter jogadores de uma equipe"""
    players = player_controller.get_players_by_team(team_id)
    return jsonify([{
        'id': player.id,
        'name': player.name,
        'position': player.position
    } for player in players])

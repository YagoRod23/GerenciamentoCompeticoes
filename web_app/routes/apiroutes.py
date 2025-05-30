"""
Rotas da API REST
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from database.database import SessionLocal
from database.models import Team, Player, Game, Competition
from desktop_app.controllers.team_controller import team_controller
from desktop_app.controllers.player_controller import player_controller
from desktop_app.controllers.game_controller import game_controller
from desktop_app.controllers.competition_controller import competition_controller

api_bp = Blueprint('api', __name__)


@api_bp.route('/teams')
@login_required
def api_teams():
    """Lista todas as equipes via API"""
    teams = team_controller.get_all_teams()
    return jsonify([{
        'id': team.id,
        'name': team.name,
        'abbreviation': team.abbreviation,
        'city': team.city,
        'state': team.state
    } for team in teams])


@api_bp.route('/teams/<int:team_id>')
@login_required
def api_team_detail(team_id):
    """Detalhes de uma equipe via API"""
    team = team_controller.get_team_by_id(team_id)
    if not team:
        return jsonify({'error': 'Equipe não encontrada'}), 404
    
    return jsonify({
        'id': team.id,
        'name': team.name,
        'abbreviation': team.abbreviation,
        'city': team.city,
        'state': team.state,
        'founded_year': team.founded_year,
        'colors': team.colors,
        'stadium': team.stadium,
        'coach': team.coach
    })


@api_bp.route('/players')
@login_required
def api_players():
    """Lista todos os jogadores via API"""
    players = player_controller.get_all_players()
    return jsonify([{
        'id': player.id,
        'name': player.name,
        'position': player.position,
        'age': player.age,
        'team': player.team.name if player.team else None
    } for player in players])


@api_bp.route('/players/<int:player_id>')
@login_required
def api_player_detail(player_id):
    """Detalhes de um jogador via API"""
    player = player_controller.get_player_by_id(player_id)
    if not player:
        return jsonify({'error': 'Jogador não encontrado'}), 404
    
    return jsonify({
        'id': player.id,
        'name': player.name,
        'position': player.position,
        'age': player.age,
        'height': player.height,
        'weight': player.weight,
        'nationality': player.nationality,
        'team': player.team.name if player.team else None
    })


@api_bp.route('/games')
@login_required
def api_games():
    """Lista todos os jogos via API"""
    games = game_controller.get_all_games()
    return jsonify([{
        'id': game.id,
        'home_team': game.home_team.name if game.home_team else None,
        'away_team': game.away_team.name if game.away_team else None,
        'game_date': game.game_date.isoformat() if game.game_date else None,
        'home_score': game.home_team_score,
        'away_score': game.away_team_score,
        'status': game.status.value if game.status else None
    } for game in games])


@api_bp.route('/games/<int:game_id>')
@login_required
def api_game_detail(game_id):
    """Detalhes de um jogo via API"""
    game = game_controller.get_game_by_id(game_id)
    if not game:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    return jsonify({
        'id': game.id,
        'home_team': {
            'id': game.home_team.id,
            'name': game.home_team.name
        } if game.home_team else None,
        'away_team': {
            'id': game.away_team.id,
            'name': game.away_team.name
        } if game.away_team else None,
        'competition': game.competition.name if game.competition else None,
        'game_date': game.game_date.isoformat() if game.game_date else None,
        'game_time': game.game_time.isoformat() if game.game_time else None,
        'location': game.location,
        'home_score': game.home_team_score,
        'away_score': game.away_team_score,
        'status': game.status.value if game.status else None,
        'round_number': game.round_number
    })


@api_bp.route('/competitions')
@login_required
def api_competitions():
    """Lista todas as competições via API"""
    competitions = competition_controller.get_all_competitions()
    return jsonify([{
        'id': competition.id,
        'name': competition.name,
        'type': competition.competition_type.value if competition.competition_type else None,
        'season': competition.season,
        'is_active': competition.is_active
    } for competition in competitions])


@api_bp.route('/competitions/<int:competition_id>')
@login_required
def api_competition_detail(competition_id):
    """Detalhes de uma competição via API"""
    competition = competition_controller.get_competition_by_id(competition_id)
    if not competition:
        return jsonify({'error': 'Competição não encontrada'}), 404
    
    return jsonify({
        'id': competition.id,
        'name': competition.name,
        'type': competition.competition_type.value if competition.competition_type else None,
        'season': competition.season,
        'description': competition.description,
        'start_date': competition.start_date.isoformat() if competition.start_date else None,
        'end_date': competition.end_date.isoformat() if competition.end_date else None,
        'registration_deadline': competition.registration_deadline.isoformat() if competition.registration_deadline else None,
        'max_teams': competition.max_teams,
        'is_active': competition.is_active
    })


@api_bp.route('/statistics/dashboard')
@login_required
def api_dashboard_stats():
    """Estatísticas para o dashboard"""
    session = SessionLocal()
    try:
        stats = {
            'total_teams': session.query(Team).count(),
            'total_players': session.query(Player).count(),
            'total_games': session.query(Game).count(),
            'total_competitions': session.query(Competition).count(),
            'active_competitions': session.query(Competition).filter(Competition.is_active == True).count(),
            'recent_games': session.query(Game).filter(Game.status == 'FINISHED').count(),
            'scheduled_games': session.query(Game).filter(Game.status == 'SCHEDULED').count()
        }
        return jsonify(stats)
    finally:
        session.close()


@api_bp.errorhandler(404)
def api_not_found(error):
    """Handler para 404 na API"""
    return jsonify({'error': 'Endpoint não encontrado'}), 404


@api_bp.errorhandler(500)
def api_internal_error(error):
    """Handler para 500 na API"""
    return jsonify({'error': 'Erro interno do servidor'}), 500

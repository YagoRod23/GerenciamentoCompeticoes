"""
Rotas do dashboard principal
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from database.database import SessionLocal
from database.models import Team, Player, Game, Competition

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal"""
    session = SessionLocal()
    try:
        # Estatísticas gerais
        total_teams = session.query(Team).count()
        total_players = session.query(Player).count()
        total_games = session.query(Game).count()
        total_competitions = session.query(Competition).count()
        
        # Jogos recentes
        recent_games = session.query(Game).order_by(Game.game_date.desc()).limit(5).all()
        
        # Próximos jogos
        upcoming_games = session.query(Game).filter(
            Game.status == 'SCHEDULED'
        ).order_by(Game.game_date.asc()).limit(5).all()
        
        stats = {
            'total_teams': total_teams,
            'total_players': total_players,
            'total_games': total_games,
            'total_competitions': total_competitions
        }
        
        return render_template('dashboard/index.html', 
                             stats=stats,
                             recent_games=recent_games,
                             upcoming_games=upcoming_games)
    finally:
        session.close()


@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API para estatísticas do dashboard"""
    session = SessionLocal()
    try:
        stats = {
            'teams': session.query(Team).count(),
            'players': session.query(Player).count(),
            'games': session.query(Game).count(),
            'competitions': session.query(Competition).count()
        }
        return jsonify(stats)
    finally:
        session.close()

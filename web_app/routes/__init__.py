"""
Rotas da aplicação web
"""

from .public_routes import public_bp
from .dashboard_routes import dashboard_bp
from .team_routes import team_bp
from .player_routes import player_bp
from .competition_routes import competition_bp
from .game_routes import game_bp
from .user_routes import user_bp
from .api_routes import api_bp


def register_routes(app):
    """Registra todas as rotas na aplicação"""
    
    # Rotas públicas (login, etc)
    app.register_blueprint(public_bp)
    
    # Dashboard principal
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Gestão de equipes
    app.register_blueprint(team_bp, url_prefix='/teams')
    
    # Gestão de jogadores
    app.register_blueprint(player_bp, url_prefix='/players')
    
    # Gestão de competições
    app.register_blueprint(competition_bp, url_prefix='/competitions')
    
    # Gestão de jogos
    app.register_blueprint(game_bp, url_prefix='/games')
    
    # Gestão de usuários
    app.register_blueprint(user_bp, url_prefix='/users')
    
    # API endpoints
    app.register_blueprint(api_bp, url_prefix='/api')


__all__ = [
    'register_routes',
    'public_bp',
    'dashboard_bp',
    'team_bp',
    'player_bp',
    'competition_bp',
    'game_bp',
    'user_bp',
    'api_bp'
]

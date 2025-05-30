"""
Controllers para o aplicativo desktop
"""

from .auth_controller import auth_controller
from .competition_controller import competition_controller
from .game_controller import game_controller
from .game_event_controller import game_event_controller
from .player_controller import player_controller
from .report_controller import report_controller
from .team_controller import team_controller
from .user_controller import user_controller

__all__ = [
    'auth_controller',
    'competition_controller',
    'game_controller',
    'game_event_controller',
    'player_controller',
    'report_controller',
    'team_controller',
    'user_controller'
]

"""
Módulo de views do desktop app
"""

# Importar as principais janelas
from .main_window import MainWindow
from .login_window import LoginWindow
from .teams_window import TeamsWindow
from .competitions_window import CompetitionsWindow
from .games_window import GamesWindow
from .reports_window import ReportsWindow
from .admin_window import AdminWindow

# Importar dialogs
from .team_dialog import TeamDialog
from .competition_dialog import CompetitionDialog
from .game_dialog import GameDialog
from .player_dialog import PlayerDialog
from .user_dialog import UserDialog
from .game_result_dialog import GameResultDialog
from .game_events_dialog import GameEventsDialog
from .game_report_dialog import GameReportDialog

__all__ = [
    'MainWindow',
    'LoginWindow', 
    'TeamsWindow',
    'CompetitionsWindow',
    'GamesWindow',
    'ReportsWindow',
    'AdminWindow',
    'TeamDialog',
    'CompetitionDialog',
    'GameDialog',
    'PlayerDialog',
    'UserDialog',
    'GameResultDialog',
    'GameEventsDialog',
    'GameReportDialog'
]

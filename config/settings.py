"""
Configurações gerais do sistema
"""
import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações do banco de dados
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'sports_management'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4'
}

# Configurações da aplicação
APP_CONFIG = {
    'app_name': 'Sistema de Gestão de Competições Esportivas',
    'version': '1.0.0',
    'debug': os.getenv('DEBUG', 'False').lower() == 'true'
}

# Configurações de segurança
SECURITY_CONFIG = {
    'password_min_length': 6,
    'session_timeout': 3600,  # 1 hora em segundos
    'max_login_attempts': 5
}

# Configurações das modalidades esportivas
SPORTS_CONFIG = {
    'basketball': {
        'name': 'Basquete',
        'max_players_court': 5,
        'max_team_size': 20,
        'positions': ['Armador', 'Ala-Armador', 'Ala', 'Ala-Pivô', 'Pivô'],
        'scoring': ['2 pontos', '3 pontos', 'Lance livre'],
        'max_fouls_player': 5,
        'max_fouls_team_quarter': 4
    },
    'futsal': {
        'name': 'Futsal',
        'max_players_court': 5,
        'max_team_size': 20,
        'positions': ['Goleiro', 'Fixo', 'Ala', 'Pivô'],
        'cards': ['Amarelo', 'Vermelho'],
        'suspension_rules': {
            'yellow_cards': 2,  # Suspenso após 2 amarelos
            'red_card': 1       # Suspenso após 1 vermelho
        }
    },
    'volleyball': {
        'name': 'Vôlei',
        'max_players_court': 6,
        'max_team_size': 20,
        'positions': ['Levantador', 'Oposto', 'Central', 'Ponteiro', 'Líbero'],
        'sets_to_win': 3,
        'points_per_set': 25,
        'deciding_set_points': 15
    },
    'handball': {
        'name': 'Handebol',
        'max_players_court': 7,
        'max_team_size': 20,
        'positions': ['Goleiro', 'Armador Central', 'Armador Lateral', 'Meia', 'Ponta', 'Pivô'],
        'cards': ['Amarelo', 'Vermelho'],
        'suspension_rules': {
            'yellow_cards': 2,  # Suspenso após 2 amarelos
            'red_card': 1       # Suspenso após 1 vermelho
        }
    }
}

# Configurações de competição
COMPETITION_FORMATS = {
    'elimination': 'Eliminação Direta (Mata-mata)',
    'best_of_three': 'Melhor de Três Jogos',
    'swiss': 'Sistema Suíço',
    'groups_playoffs': 'Fase de Grupos + Playoffs',
    'round_robin': 'Pontos Corridos (Todos contra Todos)',
    'other': 'Outro Formato'
}

# Sugestões automáticas de formato baseado no número de equipes
FORMAT_SUGGESTIONS = {
    (2, 4): 'elimination',
    (5, 8): 'round_robin',
    (9, 16): 'groups_playoffs',
    (17, 32): 'swiss'
}

# Configurações de relatórios
REPORT_CONFIG = {
    'export_formats': ['PDF', 'Excel'],
    'temp_dir': BASE_DIR / 'temp',
    'reports_dir': BASE_DIR / 'reports'
}

# Configurações da interface web
WEB_CONFIG = {
    'host': os.getenv('WEB_HOST', '127.0.0.1'),
    'port': int(os.getenv('WEB_PORT', 5000)),
    'secret_key': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
}

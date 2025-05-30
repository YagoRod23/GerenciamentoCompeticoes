"""
Aplicação principal para o Sistema de Gerenciamento Esportivo
"""

from flask import Flask, render_template
from flask_login import LoginManager
from database.database import init_db
from database.models import User
import os

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')

    # Inicializa banco de dados com o app contexto
    with app.app_context():
        init_db()

    # Configuração do login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'public.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'

    @login_manager.user_loader
    def load_user(user_id):
        from database.database import SessionLocal
        session = SessionLocal()
        try:
            return session.query(User).get(int(user_id))
        finally:
            session.close()

    # Registro de Blueprints com proteção de ImportError caso os arquivos não existam

    try:
        from routes.public_routes import public_bp
        app.register_blueprint(public_bp)
    except ImportError:
        pass

    try:
        from routes.dashboard_routes import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    except ImportError:
        pass

    try:
        from routes.team_routes import team_bp
        app.register_blueprint(team_bp, url_prefix='/teams')
    except ImportError:
        pass

    try:
        from routes.player_routes import player_bp
        app.register_blueprint(player_bp, url_prefix='/players')
    except ImportError:
        pass

    try:
        from routes.competition_routes import competition_bp
        app.register_blueprint(competition_bp, url_prefix='/competitions')
    except ImportError:
        pass

    try:
        from routes.api_routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError:
        pass

    # Rota principal
    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

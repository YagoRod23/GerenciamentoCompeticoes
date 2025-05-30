"""
Widget do dashboard principal
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QLabel, QFrame, QPushButton, QScrollArea,
                           QGroupBox, QProgressBar, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette

from desktop_app.controllers.competition_controller import competition_controller
from desktop_app.controllers.team_controller import team_controller
from desktop_app.controllers.game_controller import game_controller
from database.models import GameStatus, CompetitionStatus
from datetime import date, datetime, timedelta


class StatsCard(QFrame):
    """Card para exibir estatísticas"""
    
    def __init__(self, title, value, subtitle="", color="#3498db"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel {{
                color: white;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Valor principal
        self.value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Subtítulo
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_font = QFont()
            subtitle_font.setPointSize(8)
            subtitle_label.setFont(subtitle_font)
            subtitle_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(subtitle_label)
    
    def update_value(self, value):
        """Atualiza valor do card"""
        self.value_label.setText(str(value))


class RecentActivityWidget(QWidget):
    """Widget para mostrar atividades recentes"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Atividades Recentes")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Lista de atividades
        self.activity_list = QListWidget()
        self.activity_list.setMaximumHeight(200)
        layout.addWidget(self.activity_list)
        
        self.refresh()
    
    def refresh(self):
        """Atualiza lista de atividades"""
        self.activity_list.clear()
        
        try:
            # Jogos recentes
            recent_games = game_controller.get_games(
                date_from=date.today() - timedelta(days=7)
            )
            
            for game in recent_games[:5]:
                if game.status == GameStatus.FINISHED:
                    home_team = game.get_home_team()
                    away_team = game.get_away_team()
                    
                    text = f"🏆 {home_team.name} {game.home_score} x {game.away_score} {away_team.name}"
                    item = QListWidgetItem(text)
                    self.activity_list.addItem(item)
                elif game.status == GameStatus.SCHEDULED:
                    home_team = game.get_home_team()
                    away_team = game.get_away_team()
                    game_date = game.game_date.strftime("%d/%m %H:%M")
                    
                    text = f"📅 {home_team.name} x {away_team.name} - {game_date}"
                    item = QListWidgetItem(text)
                    self.activity_list.addItem(item)
            
            if self.activity_list.count() == 0:
                item = QListWidgetItem("Nenhuma atividade recente")
                self.activity_list.addItem(item)
                
        except Exception as e:
            print(f"Erro ao carregar atividades: {e}")


class DashboardWidget(QWidget):
    """Widget principal do dashboard"""
    
    refresh_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.stats_cards = {}
        self.setup_ui()
        
        # Timer para atualizar dados periodicamente
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(60000)  # Atualiza a cada minuto
    
    def setup_ui(self):
        """Configura interface do dashboard"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Título do dashboard
        title_label = QLabel("📊 Dashboard - Visão Geral")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Cards de estatísticas
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        
        # Competições ativas
        self.stats_cards['competitions'] = StatsCard(
            "Competições Ativas", "0", "Em andamento", "#e74c3c"
        )
        stats_layout.addWidget(self.stats_cards['competitions'], 0, 0)
        
        # Total de equipes
        self.stats_cards['teams'] = StatsCard(
            "Equipes Cadastradas", "0", "Total", "#2ecc71"
        )
        stats_layout.addWidget(self.stats_cards['teams'], 0, 1)
        
        # Jogos hoje
        self.stats_cards['games_today'] = StatsCard(
            "Jogos Hoje", "0", "Programados", "#f39c12"
        )
        stats_layout.addWidget(self.stats_cards['games_today'], 0, 2)
        
        # Atletas cadastrados
        self.stats_cards['athletes'] = StatsCard(
            "Atletas", "0", "Cadastrados", "#9b59b6"
        )
        stats_layout.addWidget(self.stats_cards['athletes'], 0, 3)
        
        main_layout.addWidget(stats_frame)
        
        # Área de conteúdo com scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Layout principal do conteúdo
        content_layout = QHBoxLayout()
        
        # Coluna esquerda
        left_column = QVBoxLayout()
        
        # Próximos jogos
        self.next_games_group = QGroupBox("🏆 Próximos Jogos")
        next_games_layout = QVBoxLayout(self.next_games_group)
        
        self.next_games_list = QListWidget()
        self.next_games_list.setMaximumHeight(150)
        next_games_layout.addWidget(self.next_games_list)
        
        left_column.addWidget(self.next_games_group)
        
        # Competições em andamento
        self.competitions_group = QGroupBox("🏅 Competições em Andamento")
        competitions_layout = QVBoxLayout(self.competitions_group)
        
        self.competitions_list = QListWidget()
        self.competitions_list.setMaximumHeight(150)
        competitions_layout.addWidget(self.competitions_list)
        
        left_column.addWidget(self.competitions_group)
        
        content_layout.addLayout(left_column)
        
        # Coluna direita
        right_column = QVBoxLayout()
        
        # Atividades recentes
        self.activity_widget = RecentActivityWidget()
        right_column.addWidget(self.activity_widget)
        
        # Avisos e notificações
        self.notifications_group = QGroupBox("⚠️ Notificações")
        notifications_layout = QVBoxLayout(self.notifications_group)
        
        self.notifications_list = QListWidget()
        self.notifications_list.setMaximumHeight(150)
        notifications_layout.addWidget(self.notifications_list)
        
        right_column.addWidget(self.notifications_group)
        
        content_layout.addLayout(right_column)
        
        scroll_layout.addLayout(content_layout)
        
        # Botões de ação rápida
        actions_group = QGroupBox("⚡ Ações Rápidas")
        actions_layout = QHBoxLayout(actions_group)
        
        self.new_competition_btn = QPushButton("Nova Competição")
        self.new_competition_btn.clicked.connect(self._new_competition)
        actions_layout.addWidget(self.new_competition_btn)
        
        self.register_result_btn = QPushButton("Registrar Resultado")
        self.register_result_btn.clicked.connect(self._register_result)
        actions_layout.addWidget(self.register_result_btn)
        
        self.view_standings_btn = QPushButton("Ver Classificações")
        self.view_standings_btn.clicked.connect(self._view_standings)
        actions_layout.addWidget(self.view_standings_btn)
        
        self.generate_report_btn = QPushButton("Gerar Relatório")
        self.generate_report_btn.clicked.connect(self._generate_report)
        actions_layout.addWidget(self.generate_report_btn)
        
        scroll_layout.addWidget(actions_group)
        
        # Adiciona espaçamento no final
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Carrega dados iniciais
        self.refresh()
    
    def refresh(self):
        """Atualiza todos os dados do dashboard"""
        try:
            self._update_stats_cards()
            self._update_next_games()
            self._update_competitions()
            self._update_notifications()
            self.activity_widget.refresh()
            
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")
    
    def _update_stats_cards(self):
        """Atualiza cards de estatísticas"""
        try:
            # Competições ativas
            competitions = competition_controller.get_competitions()
            active_competitions = len([c for c in competitions if c.status == CompetitionStatus.ACTIVE])
            self.stats_cards['competitions'].update_value(active_competitions)
            
            # Total de equipes
            teams = team_controller.get_teams()
            self.stats_cards['teams'].update_value(len(teams))
            
            # Jogos hoje
            today_games = game_controller.get_games(
                date_from=date.today(),
                date_to=date.today()
            )
            self.stats_cards['games_today'].update_value(len(today_games))
            
            # Total de atletas
            total_athletes = 0
            for team in teams:
                athletes = team.get_athletes()
                total_athletes += len(athletes)
            self.stats_cards['athletes'].update_value(total_athletes)
            
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def _update_next_games(self):
        """Atualiza lista de próximos jogos"""
        self.next_games_list.clear()
        
        try:
            # Próximos 5 jogos programados
            upcoming_games = game_controller.get_games(
                status=GameStatus.SCHEDULED,
                date_from=date.today()
            )
            
            for game in upcoming_games[:5]:
                home_team = game.get_home_team()
                away_team = game.get_away_team()
                competition = game.get_competition()
                
                game_date = game.game_date.strftime("%d/%m %H:%M")
                text = f"{home_team.name} x {away_team.name} - {game_date}"
                if competition:
                    text += f" ({competition.name})"
                
                item = QListWidgetItem(text)
                self.next_games_list.addItem(item)
            
            if self.next_games_list.count() == 0:
                item = QListWidgetItem("Nenhum jogo programado")
                self.next_games_list.addItem(item)
                
        except Exception as e:
            print(f"Erro ao carregar próximos jogos: {e}")
    
    def _update_competitions(self):
        """Atualiza lista de competições ativas"""
        self.competitions_list.clear()
        
        try:
            competitions = competition_controller.get_competitions()
            active_competitions = [c for c in competitions if c.status == CompetitionStatus.ACTIVE]
            
            for competition in active_competitions:
                # Calcula progresso da competição
                total_games = len(competition.get_games())
                finished_games = len([g for g in competition.get_games() 
                                    if g.status == GameStatus.FINISHED])
                
                if total_games > 0:
                    progress = int((finished_games / total_games) * 100)
                    text = f"{competition.name} - {progress}% concluída"
                else:
                    text = f"{competition.name} - Não iniciada"
                
                item = QListWidgetItem(text)
                self.competitions_list.addItem(item)
            
            if self.competitions_list.count() == 0:
                item = QListWidgetItem("Nenhuma competição ativa")
                self.competitions_list.addItem(item)
                
        except Exception as e:
            print(f"Erro ao carregar competições: {e}")
    
    def _update_notifications(self):
        """Atualiza notificações do sistema"""
        self.notifications_list.clear()
        
        try:
            notifications = []
            
            # Verifica competições que precisam ser iniciadas
            competitions = competition_controller.get_competitions()
            for competition in competitions:
                if (competition.status == CompetitionStatus.DRAFT and 
                    competition.start_date <= date.today()):
                    notifications.append(f"⚠️ Competição '{competition.name}' pode ser iniciada")
            
            # Verifica jogos sem resultado há mais de 1 dia
            overdue_games = game_controller.get_games(
                status=GameStatus.SCHEDULED,
                date_to=date.today() - timedelta(days=1)
            )
            if overdue_games:
                notifications.append(f"⏰ {len(overdue_games)} jogo(s) pendente(s) de resultado")
            
            # Verifica equipes com poucos atletas
            teams = team_controller.get_teams()
            for team in teams:
                athletes = team.get_athletes()
                if len(athletes) < 11:  # Mínimo para futebol
                    notifications.append(f"👥 Equipe '{team.name}' com poucos atletas ({len(athletes)})")
            
            # Adiciona notificações à lista
            for notification in notifications[:5]:  # Máximo 5 notificações
                item = QListWidgetItem(notification)
                self.notifications_list.addItem(item)
            
            if self.notifications_list.count() == 0:
                item = QListWidgetItem("✅ Nenhuma notificação")
                self.notifications_list.addItem(item)
                
        except Exception as e:
            print(f"Erro ao carregar notificações: {e}")
    
    def _new_competition(self):
        """Abre dialog para nova competição"""
        # Emite sinal para janela principal trocar de aba
        self.parent().parent().tab_widget.setCurrentIndex(1)  # Aba de competições
    
    def _register_result(self):
        """Abre dialog para registrar resultado"""
        # Emite sinal para janela principal trocar de aba
        self.parent().parent().tab_widget.setCurrentIndex(3)  # Aba de jogos
    
    def _view_standings(self):
        """Abre aba de classificações"""
        # Emite sinal para janela principal trocar de aba
        self.parent().parent().tab_widget.setCurrentIndex(1)  # Aba de competições
    
    def _generate_report(self):
        """Abre aba de relatórios"""
        # Emite sinal para janela principal trocar de aba
        self.parent().parent().tab_widget.setCurrentIndex(4)  # Aba de relatórios

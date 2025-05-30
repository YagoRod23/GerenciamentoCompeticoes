from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_login import UserMixin
import enum

# Certifique-se de que a importação do módulo está correta
from .database import Base

class UserType(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

# Definições de modelos, por exemplo:
class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    user_type = Column(Enum(UserType), default=UserType.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def get_id(self):
        return str(self.id)

# Continuação com Team, Player, etc.


class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    city = Column(String(100))
    state = Column(String(50))
    founded_year = Column(Integer)
    stadium = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    players = relationship("Player", back_populates="team")
    home_games = relationship("Game", foreign_keys="Game.home_team_id", back_populates="home_team")
    away_games = relationship("Game", foreign_keys="Game.away_team_id", back_populates="away_team")

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    birth_date = Column(Date)
    position = Column(String(50))
    jersey_number = Column(Integer)
    height = Column(Float)  # em centímetros
    weight = Column(Float)  # em quilos
    nationality = Column(String(50))
    team_id = Column(Integer, ForeignKey('teams.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    team = relationship("Team", back_populates="players")
    statistics = relationship("PlayerStatistic", back_populates="player")

class Competition(Base):
    __tablename__ = 'competitions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    competition_type = Column(String(50))  # Liga, Copa, Torneio
    season = Column(String(20))
    start_date = Column(Date)
    end_date = Column(Date)
    registration_deadline = Column(Date)
    max_teams = Column(Integer)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    games = relationship("Game", back_populates="competition")
    team_competitions = relationship("TeamCompetition", back_populates="competition")

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    competition_id = Column(Integer, ForeignKey('competitions.id'))
    game_date = Column(DateTime)
    venue = Column(String(100))
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    status = Column(String(20), default='scheduled')  # scheduled, in_progress, finished, cancelled
    round_number = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_games")
    competition = relationship("Competition", back_populates="games")
    statistics = relationship("PlayerStatistic", back_populates="game")

class TeamCompetition(Base):
    __tablename__ = 'team_competitions'
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    competition_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)
    registration_date = Column(DateTime, default=func.now())
    points = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    
    # Relacionamentos
    team = relationship("Team")
    competition = relationship("Competition", back_populates="team_competitions")

class PlayerStatistic(Base):
    __tablename__ = 'player_statistics'
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    # Relacionamentos
    player = relationship("Player", back_populates="statistics")
    game = relationship("Game", back_populates="statistics")

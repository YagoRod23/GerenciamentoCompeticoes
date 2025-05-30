"""
Modelos de dados para o sistema de gestão esportiva
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from database.connection import execute_query, execute_many


class UserType(Enum):
    MASTER = "master"
    ORGANIZATION = "organization"
    PUBLIC = "public"


class SportType(Enum):
    BASKETBALL = "basketball"
    FUTSAL = "futsal"
    VOLLEYBALL = "volleyball"
    HANDBALL = "handball"


class CompetitionFormat(Enum):
    ELIMINATION = "elimination"
    BEST_OF_THREE = "best_of_three"
    SWISS = "swiss"
    GROUPS_PLAYOFFS = "groups_playoffs"
    ROUND_ROBIN = "round_robin"
    OTHER = "other"


class GameStatus(Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class EventType(Enum):
    GOAL = "goal"
    POINT_2 = "point_2"
    POINT_3 = "point_3"
    FREE_THROW = "free_throw"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    FOUL = "foul"
    SUBSTITUTION = "substitution"
    SET_POINT = "set_point"


@dataclass
class User:
    """Modelo para usuários do sistema"""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    user_type: UserType = UserType.PUBLIC
    full_name: str = ""
    email: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """Busca usuário pelo nome de usuário"""
        query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
        result = execute_query(query, (username,), fetch=True)
        
        if result:
            user_data = result[0]
            return cls(
                id=user_data['id'],
                username=user_data['username'],
                password_hash=user_data['password_hash'],
                user_type=UserType(user_data['user_type']),
                full_name=user_data['full_name'],
                email=user_data['email'],
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at'],
                is_active=user_data['is_active']
            )
        return None
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """Busca usuário pelo ID"""
        query = "SELECT * FROM users WHERE id = %s AND is_active = TRUE"
        result = execute_query(query, (user_id,), fetch=True)
        
        if result:
            user_data = result[0]
            return cls(
                id=user_data['id'],
                username=user_data['username'],
                password_hash=user_data['password_hash'],
                user_type=UserType(user_data['user_type']),
                full_name=user_data['full_name'],
                email=user_data['email'],
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at'],
                is_active=user_data['is_active']
            )
        return None
    
    def save(self) -> bool:
        """Salva o usuário no banco de dados"""
        try:
            if self.id:
                # Atualizar usuário existente
                query = """
                UPDATE users 
                SET username = %s, password_hash = %s, user_type = %s, 
                    full_name = %s, email = %s, is_active = %s
                WHERE id = %s
                """
                params = (self.username, self.password_hash, self.user_type.value,
                         self.full_name, self.email, self.is_active, self.id)
            else:
                # Criar novo usuário
                query = """
                INSERT INTO users (username, password_hash, user_type, full_name, email, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (self.username, self.password_hash, self.user_type.value,
                         self.full_name, self.email, self.is_active)
            
            result = execute_query(query, params)
            if not self.id and result:
                self.id = result
            return True
            
        except Exception as e:
            print(f"Erro ao salvar usuário: {e}")
            return False
    
    @classmethod
    def get_all(cls) -> List['User']:
        """Retorna todos os usuários ativos"""
        query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY full_name"
        results = execute_query(query, fetch=True)
        
        users = []
        if results:
            for user_data in results:
                users.append(cls(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    user_type=UserType(user_data['user_type']),
                    full_name=user_data['full_name'],
                    email=user_data['email'],
                    created_at=user_data['created_at'],
                    updated_at=user_data['updated_at'],
                    is_active=user_data['is_active']
                ))
        return users


@dataclass
class Venue:
    """Modelo para locais de jogos"""
    id: Optional[int] = None
    name: str = ""
    address: str = ""
    capacity: int = 0
    sports_available: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    is_active: bool = True
    
    @classmethod
    def get_all(cls) -> List['Venue']:
        """Retorna todos os locais ativos"""
        query = "SELECT * FROM venues WHERE is_active = TRUE ORDER BY name"
        results = execute_query(query, fetch=True)
        
        venues = []
        if results:
            for venue_data in results:
                sports_list = venue_data['sports_available'].split(',') if venue_data['sports_available'] else []
                venues.append(cls(
                    id=venue_data['id'],
                    name=venue_data['name'],
                    address=venue_data['address'],
                    capacity=venue_data['capacity'],
                    sports_available=sports_list,
                    created_at=venue_data['created_at'],
                    is_active=venue_data['is_active']
                ))
        return venues
    
    @classmethod
    def get_by_sport(cls, sport: str) -> List['Venue']:
        """Retorna locais que suportam o esporte especificado"""
        query = "SELECT * FROM venues WHERE FIND_IN_SET(%s, sports_available) > 0 AND is_active = TRUE ORDER BY name"
        results = execute_query(query, (sport,), fetch=True)
        
        venues = []
        if results:
            for venue_data in results:
                sports_list = venue_data['sports_available'].split(',') if venue_data['sports_available'] else []
                venues.append(cls(
                    id=venue_data['id'],
                    name=venue_data['name'],
                    address=venue_data['address'],
                    capacity=venue_data['capacity'],
                    sports_available=sports_list,
                    created_at=venue_data['created_at'],
                    is_active=venue_data['is_active']
                ))
        return venues
    
    def save(self) -> bool:
        """Salva o local no banco de dados"""
        try:
            sports_str = ','.join(self.sports_available) if self.sports_available else ''
            
            if self.id:
                # Atualizar local existente
                query = """
                UPDATE venues 
                SET name = %s, address = %s, capacity = %s, 
                    sports_available = %s, is_active = %s
                WHERE id = %s
                """
                params = (self.name, self.address, self.capacity, 
                         sports_str, self.is_active, self.id)
            else:
                # Criar novo local
                query = """
                INSERT INTO venues (name, address, capacity, sports_available, is_active)
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (self.name, self.address, self.capacity, sports_str, self.is_active)
            
            result = execute_query(query, params)
            if not self.id and result:
                self.id = result
            return True
            
        except Exception as e:
            print(f"Erro ao salvar local: {e}")
            return False


@dataclass
class Team:
    """Modelo para equipes"""
    id: Optional[int] = None
    name: str = ""
    short_name: str = ""
    logo_path: str = ""
    primary_color: str = "#000000"
    secondary_color: str = "#FFFFFF"
    contact_person: str = ""
    contact_phone: str = ""
    contact_email: str = ""
    created_at: Optional[datetime] = None
    is_active: bool = True
    
    @classmethod
    def get_all(cls) -> List['Team']:
        """Retorna todas as equipes ativas"""
        query = "SELECT * FROM teams WHERE is_active = TRUE ORDER BY name"
        results = execute_query(query, fetch=True)
        
        teams = []
        if results:
            for team_data in results:
                teams.append(cls(
                    id=team_data['id'],
                    name=team_data['name'],
                    short_name=team_data['short_name'],
                    logo_path=team_data['logo_path'],
                    primary_color=team_data['primary_color'],
                    secondary_color=team_data['secondary_color'],
                    contact_person=team_data['contact_person'],
                    contact_phone=team_data['contact_phone'],
                    contact_email=team_data['contact_email'],
                    created_at=team_data['created_at'],
                    is_active=team_data['is_active']
                ))
        return teams
    
    @classmethod
    def get_by_id(cls, team_id: int) -> Optional['Team']:
        """Busca equipe pelo ID"""
        query = "SELECT * FROM teams WHERE id = %s AND is_active = TRUE"
        result = execute_query(query, (team_id,), fetch=True)
        
        if result:
            team_data = result[0]
            return cls(
                id=team_data['id'],
                name=team_data['name'],
                short_name=team_data['short_name'],
                logo_path=team_data['logo_path'],
                primary_color=team_data['primary_color'],
                secondary_color=team_data['secondary_color'],
                contact_person=team_data['contact_person'],
                contact_phone=team_data['contact_phone'],
                contact_email=team_data['contact_email'],
                created_at=team_data['created_at'],
                is_active=team_data['is_active']
            )
        return None
    
    def save(self) -> bool:
        """Salva a equipe no banco de dados"""
        try:
            if self.id:
                # Atualizar equipe existente
                query = """
                UPDATE teams 
                SET name = %s, short_name = %s, logo_path = %s, 
                    primary_color = %s, secondary_color = %s, contact_person = %s,
                    contact_phone = %s, contact_email = %s, is_active = %s
                WHERE id = %s
                """
                params = (self.name, self.short_name, self.logo_path,
                         self.primary_color, self.secondary_color, self.contact_person,
                         self.contact_phone, self.contact_email, self.is_active, self.id)
            else:
                # Criar nova equipe
                query = """
                INSERT INTO teams (name, short_name, logo_path, primary_color, 
                                 secondary_color, contact_person, contact_phone, 
                                 contact_email, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.name, self.short_name, self.logo_path,
                         self.primary_color, self.secondary_color, self.contact_person,
                         self.contact_phone, self.contact_email, self.is_active)
            
            result = execute_query(query, params)
            if not self.id and result:
                self.id = result
            return True
            
        except Exception as e:
            print(f"Erro ao salvar equipe: {e}")
            return False
    
    def get_athletes(self) -> List['Athlete']:
        """Retorna os atletas da equipe"""
        return Athlete.get_by_team(self.id)


@dataclass
class Athlete:
    """Modelo para atletas"""
    id: Optional[int] = None
    team_id: Optional[int] = None
    name: str = ""
    jersey_number: Optional[int] = None
    position: str = ""
    birth_date: Optional[date] = None
    document_number: str = ""
    phone: str = ""
    email: str = ""
    emergency_contact: str = ""
    emergency_phone: str = ""
    is_captain: bool = False
    created_at: Optional[datetime] = None
    is_active: bool = True
    
    @classmethod
    def get_by_team(cls, team_id: int) -> List['Athlete']:
        """Retorna atletas de uma equipe"""
        query = "SELECT * FROM athletes WHERE team_id = %s AND is_active = TRUE ORDER BY jersey_number"
        results = execute_query(query, (team_id,), fetch=True)
        
        athletes = []
        if results:
            for athlete_data in results:
                athletes.append(cls(
                    id=athlete_data['id'],
                    team_id=athlete_data['team_id'],
                    name=athlete_data['name'],
                    jersey_number=athlete_data['jersey_number'],
                    position=athlete_data['position'],
                    birth_date=athlete_data['birth_date'],
                    document_number=athlete_data['document_number'],
                    phone=athlete_data['phone'],
                    email=athlete_data['email'],
                    emergency_contact=athlete_data['emergency_contact'],
                    emergency_phone=athlete_data['emergency_phone'],
                    is_captain=athlete_data['is_captain'],
                    created_at=athlete_data['created_at'],
                    is_active=athlete_data['is_active']
                ))
        return athletes
    
    @classmethod
    def get_by_id(cls, athlete_id: int) -> Optional['Athlete']:
        """Busca atleta pelo ID"""
        query = "SELECT * FROM athletes WHERE id = %s AND is_active = TRUE"
        result = execute_query(query, (athlete_id,), fetch=True)
        
        if result:
            athlete_data = result[0]
            return cls(
                id=athlete_data['id'],
                team_id=athlete_data['team_id'],
                name=athlete_data['name'],
                jersey_number=athlete_data['jersey_number'],
                position=athlete_data['position'],
                birth_date=athlete_data['birth_date'],
                document_number=athlete_data['document_number'],
                phone=athlete_data['phone'],
                email=athlete_data['email'],
                emergency_contact=athlete_data['emergency_contact'],
                emergency_phone=athlete_data['emergency_phone'],
                is_captain=athlete_data['is_captain'],
                created_at=athlete_data['created_at'],
                is_active=athlete_data['is_active']
            )
        return None
    
    def save(self) -> bool:
        """Salva o atleta no banco de dados"""
        try:
            if self.id:
                # Atualizar atleta existente
                query = """
                UPDATE athletes 
                SET team_id = %s, name = %s, jersey_number = %s, position = %s,
                    birth_date = %s, document_number = %s, phone = %s, email = %s,
                    emergency_contact = %s, emergency_phone = %s, is_captain = %s, is_active = %s
                WHERE id = %s
                """
                params = (self.team_id, self.name, self.jersey_number, self.position,
                         self.birth_date, self.document_number, self.phone, self.email,
                         self.emergency_contact, self.emergency_phone, self.is_captain, 
                         self.is_active, self.id)
            else:
                # Criar novo atleta
                query = """
                INSERT INTO athletes (team_id, name, jersey_number, position, birth_date,
                                    document_number, phone, email, emergency_contact,
                                    emergency_phone, is_captain, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.team_id, self.name, self.jersey_number, self.position,
                         self.birth_date, self.document_number, self.phone, self.email,
                         self.emergency_contact, self.emergency_phone, self.is_captain, self.is_active)
            
            result = execute_query(query, params)
            if not self.id and result:
                self.id = result
            return True
            
        except Exception as e:
            print(f"Erro ao salvar atleta: {e}")
            return False


@dataclass
class Competition:
    """Modelo para competições"""
    id: Optional[int] = None
    name: str = ""
    sport: SportType = SportType.FUTSAL
    format_type: CompetitionFormat = CompetitionFormat.ROUND_ROBIN
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "planning"
    max_teams: int = 16
    description: str = ""
    rules: str = ""
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def get_all(cls) -> List['Competition']:
        """Retorna todas as competições"""
        query = "SELECT * FROM competitions ORDER BY created_at DESC"
        results = execute_query(query, fetch=True)
        
        competitions = []
        if results:
            for comp_data in results:
                competitions.append(cls(
                    id=comp_data['id'],
                    name=comp_data['name'],
                    sport=SportType(comp_data['sport']),
                    format_type=CompetitionFormat(comp_data['format_type']),
                    start_date=comp_data['start_date'],
                    end_date=comp_data['end_date'],
                    status=comp_data['status'],
                    max_teams=comp_data['max_teams'],
                    description=comp_data['description'],
                    rules=comp_data['rules'],
                    created_by=comp_data['created_by'],
                    created_at=comp_data['created_at'],
                    updated_at=comp_data['updated_at']
                ))
        return competitions
    
    @classmethod
    def get_active(cls) -> List['Competition']:
        """Retorna competições ativas (em planejamento ou em andamento)"""
        query = "SELECT * FROM competitions WHERE status IN ('planning', 'ongoing') ORDER BY start_date"
        results = execute_query(query, fetch=True)
        
        competitions = []
        if results:
            for comp_data in results:
                competitions.append(cls(
                    id=comp_data['id'],
                    name=comp_data['name'],
                    sport=SportType(comp_data['sport']),
                    format_type=CompetitionFormat(comp_data['format_type']),
                    start_date=comp_data['start_date'],
                    end_date=comp_data['end_date'],
                    status=comp_data['status'],
                    max_teams=comp_data['max_teams'],
                    description=comp_data['description'],
                    rules=comp_data['rules'],
                    created_by=comp_data['created_by'],
                    created_at=comp_data['created_at'],
                    updated_at=comp_data['updated_at']
                ))
        return competitions
    
    def save(self) -> bool:
        """Salva a competição no banco de dados"""
        try:
            if self.id:
                # Atualizar competição existente
                query = """
                UPDATE competitions 
                SET name = %s, sport = %s, format_type = %s, start_date = %s,
                    end_date = %s, status = %s, max_teams = %s, description = %s, rules = %s
                WHERE id = %s
                """
                params = (self.name, self.sport.value, self.format_type.value, self.start_date,
                         self.end_date, self.status, self.max_teams, self.description, 
                         self.rules, self.id)
            else:
                # Criar nova competição
                query = """
                INSERT INTO competitions (name, sport, format_type, start_date, end_date,
                                        status, max_teams, description, rules, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.name, self.sport.value, self.format_type.value, self.start_date,
                         self.end_date, self.status, self.max_teams, self.description, 
                         self.rules, self.created_by)
            
            result = execute_query(query, params)
            if not self.id and result:
                self.id = result
            return True
            
        except Exception as e:
            print(f"Erro ao salvar competição: {e}")
            return False
    
    def get_registered_teams(self) -> List[Team]:
        """Retorna equipes inscritas na competição"""
        query = """
        SELECT t.* FROM teams t
        JOIN team_registrations tr ON t.id = tr.team_id
        WHERE tr.competition_id = %s AND tr.is_confirmed = TRUE
        ORDER BY t.name
        """
        results = execute_query(query, (self.id,), fetch=True)
        
        teams = []
        if results:
            for team_data in results:
                teams.append(Team(
                    id=team_data['id'],
                    name=team_data['name'],
                    short_name=team_data['short_name'],
                    logo_path=team_data['logo_path'],
                    primary_color=team_data['primary_color'],
                    secondary_color=team_data['secondary_color'],
                    contact_person=team_data['contact_person'],
                    contact_phone=team_data['contact_phone'],
                    contact_email=team_data['contact_email'],
                    created_at=team_data['created_at'],
                    is_active=team_data['is_active']
                ))
        return teams


@dataclass
class Game:
    """Modelo para jogos"""
    id: Optional[int] = None
    competition_id: int = 0
    home_team_id: int = 0
    away_team_id: int = 0
    venue_id: Optional[int] = None
    game_date: Optional[datetime] = None
    round_number: int = 1
    phase: str = "Fase Única"
    status: GameStatus = GameStatus.SCHEDULED
    home_score: int = 0
    away_score: int = 0
    home_sets: int = 0
    away_sets: int = 0
    observations: str = ""
    referee_name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def get_by_competition(cls, competition_id: int) -> List['Game']:
        """Retorna jogos de uma competição"""
        query = """
        SELECT g.*, ht.name as home_team_name, at.name as away_team_name, v.name as venue_name
        FROM games g
        LEFT JOIN teams ht ON g.home_team_id = ht.id
        LEFT JOIN teams at ON g.away_team_id = at.id
        LEFT JOIN venues v ON g.venue_id = v.id
        WHERE g.competition_id = %s
        ORDER BY g.game_date, g.round_number
        """
        results = execute_query(query, (competition_id,), fetch=True)
        
        games = []
        if results:
            for game_data in results:
                games.append(cls(
                    id=game_data['id'],
                    competition_id=game_data['competition_id'],
                    home_team_id=game_data['home_team_id'],
                    away_team_id=game_data['away_team_id'],
                    venue_id=game_data['venue_id'],
                    game_date=game_data['game_date'],
                    round_number=game_data['round_number'],
                    phase=game_data['phase'],
                    status=GameStatus(game_data['status']),
                    home_score=game_data['home_score'],
                    away_score=game_data['away_score'],
                    home_sets=game_data['home_sets'],
                    away_sets=game_data['away_sets'],
                    observations=game_data['observations'],
                    referee_name=game_data['referee_name'],
                    created_at=game_data['created_at'],
                    updated_at=game_data['updated_at']
                ))
        return games
    
    def save(self) -> bool:
        """Salva o jogo no banco de dados"""
        try:
            if self.id:
                # Atualizar jogo existente
                query = """
                UPDATE games 
                SET competition_id = %s, home_team_id = %s, away_team_id = %s, venue_id = %s,
                    game_date = %s, round_number = %s, phase = %s, status = %s,
                    home_score = %s, away_score = %s, home_sets = %s, away_sets = %s,
                    observations = %s, referee_name = %s
                WHERE id = %s
                """
                params = (self.competition_id, self.home_team_id, self.away_team_id, self.venue_id,
                         self.game_date, self.round_number, self.phase, self.status.value,
                         self.home_score, self.away_score, self.home_sets, self.away_sets,
                         self.observations, self.referee_name, self.id)
            else:
                # Criar novo jogo
                query = """
                INSERT INTO games (competition_id, home_team_id, away_team_id, venue_id,
                                 game_date, round_number, phase, status, home_score, away_score,
                                 home_sets, away_sets, observations, referee_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.competition_id, self.home_team_id, self.away_team_id, self.venue_id,
                         self.game_date, self.round_number, self.phase, self.status.value,
                         self.home_score, self.away_score, self.home_sets, self.away_sets,
                         self.observations, self.referee_name)
            
            result = execute_query(query, params)
            if not self.id and result:
                self.id = result
            return True
            
        except Exception as e:
            print(f"Erro ao salvar jogo: {e}")
            return False


# Funções auxiliares para operações específicas

def suggest_competition_format(num_teams: int) -> CompetitionFormat:
    """Sugere formato de competição baseado no número de equipes"""
    from config.settings import FORMAT_SUGGESTIONS
    
    for (min_teams, max_teams), format_name in FORMAT_SUGGESTIONS.items():
        if min_teams <= num_teams <= max_teams:
            return CompetitionFormat(format_name)
    
    # Padrão para muitas equipes
    if num_teams > 32:
        return CompetitionFormat.SWISS
    else:
        return CompetitionFormat.ROUND_ROBIN


def calculate_standings(competition_id: int) -> bool:
    """Calcula e atualiza a classificação de uma competição"""
    try:
        # Busca todos os jogos finalizados da competição
        query = """
        SELECT * FROM games 
        WHERE competition_id = %s AND status = 'finished'
        ORDER BY game_date
        """
        games = execute_query(query, (competition_id,), fetch=True)
        
        # Busca as equipes inscritas na competição
        query = """
        SELECT team_id FROM team_registrations 
        WHERE competition_id = %s AND is_confirmed = TRUE
        """
        teams = execute_query(query, (competition_id,), fetch=True)
        
        # Inicializa estatísticas das equipes
        team_stats = {}
        for team in teams:
            team_id = team['team_id']
            team_stats[team_id] = {
                'games_played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'points': 0,
                'sets_for': 0,
                'sets_against': 0
            }
        
        # Processa cada jogo
        for game in games:
            home_id = game['home_team_id']
            away_id = game['away_team_id']
            home_score = game['home_score']
            away_score = game['away_score']
            home_sets = game['home_sets']
            away_sets = game['away_sets']
            
            if home_id in team_stats and away_id in team_stats:
                # Atualiza jogos disputados
                team_stats[home_id]['games_played'] += 1
                team_stats[away_id]['games_played'] += 1
                
                # Atualiza gols/pontos
                team_stats[home_id]['goals_for'] += home_score
                team_stats[home_id]['goals_against'] += away_score
                team_stats[away_id]['goals_for'] += away_score
                team_stats[away_id]['goals_against'] += home_score
                
                # Atualiza sets (para vôlei)
                team_stats[home_id]['sets_for'] += home_sets
                team_stats[home_id]['sets_against'] += away_sets
                team_stats[away_id]['sets_for'] += away_sets
                team_stats[away_id]['sets_against'] += home_sets
                
                # Determina resultado
                if home_score > away_score:
                    # Vitória do mandante
                    team_stats[home_id]['wins'] += 1
                    team_stats[home_id]['points'] += 3
                    team_stats[away_id]['losses'] += 1
                elif home_score < away_score:
                    # Vitória do visitante
                    team_stats[away_id]['wins'] += 1
                    team_stats[away_id]['points'] += 3
                    team_stats[home_id]['losses'] += 1
                else:
                    # Empate
                    team_stats[home_id]['draws'] += 1
                    team_stats[home_id]['points'] += 1
                    team_stats[away_id]['draws'] += 1
                    team_stats[away_id]['points'] += 1
                
                # Calcula saldo de gols
                team_stats[home_id]['goal_difference'] = team_stats[home_id]['goals_for'] - team_stats[home_id]['goals_against']
                team_stats[away_id]['goal_difference'] = team_stats[away_id]['goals_for'] - team_stats[away_id]['goals_against']
        
        # Salva as estatísticas no banco
        for team_id, stats in team_stats.items():
            query = """
            INSERT INTO standings (competition_id, team_id, games_played, wins, draws, losses,
                                 goals_for, goals_against, goal_difference, points, sets_for, sets_against)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                games_played = VALUES(games_played),
                wins = VALUES(wins),
                draws = VALUES(draws),
                losses = VALUES(losses),
                goals_for = VALUES(goals_for),
                goals_against = VALUES(goals_against),
                goal_difference = VALUES(goal_difference),
                points = VALUES(points),
                sets_for = VALUES(sets_for),
                sets_against = VALUES(sets_against)
            """
            params = (competition_id, team_id, stats['games_played'], stats['wins'], 
                     stats['draws'], stats['losses'], stats['goals_for'], 
                     stats['goals_against'], stats['goal_difference'], stats['points'],
                     stats['sets_for'], stats['sets_against'])
            
            execute_query(query, params)
        
        # Atualiza posições baseadas em pontos, saldo de gols, etc.
        query = """
        UPDATE standings s1
        SET position = (
            SELECT COUNT(*) + 1 
            FROM standings s2 
            WHERE s2.competition_id = s1.competition_id 
            AND (s2.points > s1.points 
                 OR (s2.points = s1.points AND s2.goal_difference > s1.goal_difference)
                 OR (s2.points = s1.points AND s2.goal_difference = s1.goal_difference AND s2.goals_for > s1.goals_for))
        )
        WHERE s1.competition_id = %s
        """
        execute_query(query, (competition_id,))
        
        return True
        
    except Exception as e:
        print(f"Erro ao calcular classificação: {e}")
        return False

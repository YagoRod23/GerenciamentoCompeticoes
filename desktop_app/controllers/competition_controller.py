"""
Controller para gestão de competições
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import date, datetime

from database.models import (Competition, Team, Game, SportType, CompetitionFormat, 
                           GameStatus, calculate_standings, suggest_competition_format)
from database.connection import execute_query
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType


class CompetitionController:
    """Controlador para gestão de competições"""
    
    def __init__(self):
        self.current_competition: Optional[Competition] = None
    
    def create_competition(self, name: str, sport: SportType, format_type: CompetitionFormat,
                          start_date: date, end_date: date, max_teams: int,
                          description: str = "", rules: str = "") -> Tuple[bool, str]:
        """Cria uma nova competição"""
        
        # Verifica permissões
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para criar competições"
        
        try:
            # Validações
            if not name.strip():
                return False, "Nome da competição é obrigatório"
            
            if len(name) > 100:
                return False, "Nome da competição deve ter no máximo 100 caracteres"
            
            if start_date and end_date and start_date > end_date:
                return False, "Data de início não pode ser posterior à data de fim"
            
            if max_teams < 2:
                return False, "Competição deve ter pelo menos 2 equipes"
            
            if max_teams > 64:
                return False, "Máximo de 64 equipes por competição"
            
            # Verifica se já existe competição com mesmo nome
            query = "SELECT id FROM competitions WHERE name = %s"
            existing = execute_query(query, (name,), fetch=True)
            if existing:
                return False, "Já existe uma competição com este nome"
            
            # Cria a competição
            competition = Competition(
                name=name,
                sport=sport,
                format_type=format_type,
                start_date=start_date,
                end_date=end_date,
                max_teams=max_teams,
                description=description,
                rules=rules,
                created_by=auth_controller.current_user.id,
                status="planning"
            )
            
            if competition.save():
                self.current_competition = competition
                return True, "Competição criada com sucesso"
            else:
                return False, "Erro ao salvar competição"
                
        except Exception as e:
            return False, f"Erro ao criar competição: {str(e)}"
    
    def update_competition(self, competition_id: int, **kwargs) -> Tuple[bool, str]:
        """Atualiza dados de uma competição"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para editar competições"
        
        try:
            # Busca a competição
            competition = self.get_competition_by_id(competition_id)
            if not competition:
                return False, "Competição não encontrada"
            
            # Verifica se pode ser editada
            if competition.status not in ["planning"]:
                return False, "Apenas competições em planejamento podem ser editadas"
            
            # Atualiza os campos fornecidos
            updated = False
            for field, value in kwargs.items():
                if hasattr(competition, field):
                    setattr(competition, field, value)
                    updated = True
            
            if updated and competition.save():
                return True, "Competição atualizada com sucesso"
            else:
                return False, "Nenhuma alteração realizada"
                
        except Exception as e:
            return False, f"Erro ao atualizar competição: {str(e)}"
    
    def register_team(self, competition_id: int, team_id: int, 
                     group_name: str = None) -> Tuple[bool, str]:
        """Inscreve uma equipe em uma competição"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para inscrever equipes"
        
        try:
            # Verifica se a competição existe
            competition = self.get_competition_by_id(competition_id)
            if not competition:
                return False, "Competição não encontrada"
            
            # Verifica se a competição aceita inscrições
            if competition.status != "planning":
                return False, "Competição não aceita mais inscrições"
            
            # Verifica se a equipe existe
            team = Team.get_by_id(team_id)
            if not team:
                return False, "Equipe não encontrada"
            
            # Verifica se já está inscrita
            query = "SELECT id FROM team_registrations WHERE competition_id = %s AND team_id = %s"
            existing = execute_query(query, (competition_id, team_id), fetch=True)
            if existing:
                return False, "Equipe já inscrita nesta competição"
            
            # Verifica limite de equipes
            query = "SELECT COUNT(*) as count FROM team_registrations WHERE competition_id = %s"
            result = execute_query(query, (competition_id,), fetch=True)
            current_teams = result[0]['count'] if result else 0
            
            if current_teams >= competition.max_teams:
                return False, "Competição já atingiu o limite máximo de equipes"
            
            # Verifica se a equipe tem atletas suficientes
            athletes = team.get_athletes()
            if len(athletes) < 5:  # Mínimo básico para qualquer modalidade
                return False, "Equipe deve ter pelo menos 5 atletas para se inscrever"
            
            # Inscreve a equipe
            query = """
            INSERT INTO team_registrations (competition_id, team_id, group_name, is_confirmed)
            VALUES (%s, %s, %s, %s)
            """
            execute_query(query, (competition_id, team_id, group_name, True))
            
            return True, f"Equipe {team.name} inscrita com sucesso"
            
        except Exception as e:
            return False, f"Erro ao inscrever equipe: {str(e)}"
    
    def remove_team_registration(self, competition_id: int, team_id: int) -> Tuple[bool, str]:
        """Remove inscrição de uma equipe"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente"
        
        try:
            competition = self.get_competition_by_id(competition_id)
            if not competition:
                return False, "Competição não encontrada"
            
            if competition.status != "planning":
                return False, "Não é possível remover equipes de competição em andamento"
            
            query = "DELETE FROM team_registrations WHERE competition_id = %s AND team_id = %s"
            result = execute_query(query, (competition_id, team_id))
            
            if result > 0:
                return True, "Inscrição removida com sucesso"
            else:
                return False, "Inscrição não encontrada"
                
        except Exception as e:
            return False, f"Erro ao remover inscrição: {str(e)}"
    
    def start_competition(self, competition_id: int) -> Tuple[bool, str]:
        """Inicia uma competição"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente"
        
        try:
            competition = self.get_competition_by_id(competition_id)
            if not competition:
                return False, "Competição não encontrada"
            
            if competition.status != "planning":
                return False, "Competição não está em planejamento"
            
            # Verifica se tem equipes suficientes
            registered_teams = competition.get_registered_teams()
            if len(registered_teams) < 2:
                return False, "É necessário pelo menos 2 equipes para iniciar a competição"
            
            # Gera os jogos baseado no formato
            games_created = self._generate_games(competition, registered_teams)
            if not games_created:
                return False, "Erro ao gerar jogos da competição"
            
            # Atualiza status
            competition.status = "ongoing"
            if competition.save():
                return True, "Competição iniciada com sucesso"
            else:
                return False, "Erro ao atualizar status da competição"
                
        except Exception as e:
            return False, f"Erro ao iniciar competição: {str(e)}"
    
    def finish_competition(self, competition_id: int) -> Tuple[bool, str]:
        """Finaliza uma competição"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente"
        
        try:
            competition = self.get_competition_by_id(competition_id)
            if not competition:
                return False, "Competição não encontrada"
            
            if competition.status != "ongoing":
                return False, "Competição não está em andamento"
            
            # Verifica se todos os jogos foram finalizados
            query = """
            SELECT COUNT(*) as pending FROM games 
            WHERE competition_id = %s AND status NOT IN ('finished', 'cancelled')
            """
            result = execute_query(query, (competition_id,), fetch=True)
            pending_games = result[0]['pending'] if result else 0
            
            if pending_games > 0:
                return False, f"Ainda há {pending_games} jogos pendentes"
            
            # Calcula classificação final
            calculate_standings(competition_id)
            
            # Finaliza a competição
            competition.status = "finished"
            if competition.save():
                return True, "Competição finalizada com sucesso"
            else:
                return False, "Erro ao finalizar competição"
                
        except Exception as e:
            return False, f"Erro ao finalizar competição: {str(e)}"
    
    def get_competitions(self, status: str = None) -> List[Competition]:
        """Retorna lista de competições"""
        try:
            if status:
                query = "SELECT * FROM competitions WHERE status = %s ORDER BY created_at DESC"
                results = execute_query(query, (status,), fetch=True)
            else:
                query = "SELECT * FROM competitions ORDER BY created_at DESC"
                results = execute_query(query, fetch=True)
            
            competitions = []
            if results:
                for comp_data in results:
                    competitions.append(Competition(
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
            
        except Exception as e:
            print(f"Erro ao buscar competições: {e}")
            return []
    
    def get_competition_by_id(self, competition_id: int) -> Optional[Competition]:
        """Busca competição por ID"""
        try:
            query = "SELECT * FROM competitions WHERE id = %s"
            result = execute_query(query, (competition_id,), fetch=True)
            
            if result:
                comp_data = result[0]
                return Competition(
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
                )
            return None
            
        except Exception as e:
            print(f"Erro ao buscar competição: {e}")
            return None
    
    def get_standings(self, competition_id: int) -> List[Dict[str, Any]]:
        """Retorna classificação de uma competição"""
        try:
            query = """
            SELECT s.*, t.name as team_name, t.short_name
            FROM standings s
            JOIN teams t ON s.team_id = t.id
            WHERE s.competition_id = %s
            ORDER BY s.position ASC, s.points DESC, s.goal_difference DESC, s.goals_for DESC
            """
            results = execute_query(query, (competition_id,), fetch=True)
            
            standings = []
            if results:
                for standing in results:
                    standings.append({
                        'position': standing['position'],
                        'team_name': standing['team_name'],
                        'team_short_name': standing['short_name'],
                        'games_played': standing['games_played'],
                        'wins': standing['wins'],
                        'draws': standing['draws'],
                        'losses': standing['losses'],
                        'goals_for': standing['goals_for'],
                        'goals_against': standing['goals_against'],
                        'goal_difference': standing['goal_difference'],
                        'points': standing['points'],
                        'sets_for': standing['sets_for'],
                        'sets_against': standing['sets_against']
                    })
            
            return standings
            
        except Exception as e:
            print(f"Erro ao buscar classificação: {e}")
            return []
    
    def _generate_games(self, competition: Competition, teams: List[Team]) -> bool:
        """Gera jogos baseado no formato da competição"""
        try:
            if competition.format_type == CompetitionFormat.ROUND_ROBIN:
                return self._generate_round_robin_games(competition, teams)
            elif competition.format_type == CompetitionFormat.ELIMINATION:
                return self._generate_elimination_games(competition, teams)
            elif competition.format_type == CompetitionFormat.GROUPS_PLAYOFFS:
                return self._generate_groups_playoffs_games(competition, teams)
            else:
                # Para outros formatos, usar round robin como padrão
                return self._generate_round_robin_games(competition, teams)
                
        except Exception as e:
            print(f"Erro ao gerar jogos: {e}")
            return False
    
    def _generate_round_robin_games(self, competition: Competition, teams: List[Team]) -> bool:
        """Gera jogos em formato de pontos corridos"""
        try:
            games_to_create = []
            round_number = 1
            
            # Todos contra todos
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    home_team = teams[i]
                    away_team = teams[j]
                    
                    games_to_create.append((
                        competition.id, home_team.id, away_team.id, None,  # venue_id
                        None, round_number, "Fase Única", "scheduled",  # game_date, round, phase, status
                        0, 0, 0, 0, "", ""  # scores, sets, observations, referee
                    ))
            
            # Insere os jogos no banco
            if games_to_create:
                query = """
                INSERT INTO games (competition_id, home_team_id, away_team_id, venue_id,
                                 game_date, round_number, phase, status, home_score, away_score,
                                 home_sets, away_sets, observations, referee_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_many(query, games_to_create)
                
                # Inicializa tabela de classificação
                self._initialize_standings(competition.id, teams)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao gerar jogos round robin: {e}")
            return False
    
    def _generate_elimination_games(self, competition: Competition, teams: List[Team]) -> bool:
        """Gera jogos em formato eliminatório"""
        try:
            # Para eliminação simples, pareamento inicial
            games_to_create = []
            round_number = 1
            
            # Embaralha as equipes ou organiza por ranking se disponível
            import random
            teams_shuffled = teams.copy()
            random.shuffle(teams_shuffled)
            
            # Gera primeira rodada
            for i in range(0, len(teams_shuffled), 2):
                if i + 1 < len(teams_shuffled):
                    home_team = teams_shuffled[i]
                    away_team = teams_shuffled[i + 1]
                    
                    games_to_create.append((
                        competition.id, home_team.id, away_team.id, None,
                        None, round_number, "Primeira Fase", "scheduled",
                        0, 0, 0, 0, "", ""
                    ))
            
            if games_to_create:
                query = """
                INSERT INTO games (competition_id, home_team_id, away_team_id, venue_id,
                                 game_date, round_number, phase, status, home_score, away_score,
                                 home_sets, away_sets, observations, referee_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_many(query, games_to_create)
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao gerar jogos eliminatórios: {e}")
            return False
    
    def _generate_groups_playoffs_games(self, competition: Competition, teams: List[Team]) -> bool:
        """Gera jogos em formato de grupos + playoffs"""
        try:
            # Implementação simplificada: divide em grupos de 4
            num_teams = len(teams)
            teams_per_group = 4
            num_groups = (num_teams + teams_per_group - 1) // teams_per_group
            
            games_to_create = []
            
            for group_num in range(num_groups):
                start_idx = group_num * teams_per_group
                end_idx = min(start_idx + teams_per_group, num_teams)
                group_teams = teams[start_idx:end_idx]
                group_name = chr(65 + group_num)  # A, B, C, etc.
                
                # Round robin dentro do grupo
                for i in range(len(group_teams)):
                    for j in range(i + 1, len(group_teams)):
                        home_team = group_teams[i]
                        away_team = group_teams[j]
                        
                        games_to_create.append((
                            competition.id, home_team.id, away_team.id, None,
                            None, 1, f"Grupo {group_name}", "scheduled",
                            0, 0, 0, 0, "", ""
                        ))
                
                # Atualiza grupo das equipes
                for team in group_teams:
                    query = """
                    UPDATE team_registrations 
                    SET group_name = %s 
                    WHERE competition_id = %s AND team_id = %s
                    """
                    execute_query(query, (group_name, competition.id, team.id))
            
            if games_to_create:
                query = """
                INSERT INTO games (competition_id, home_team_id, away_team_id, venue_id,
                                 game_date, round_number, phase, status, home_score, away_score,
                                 home_sets, away_sets, observations, referee_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_many(query, games_to_create)
                
                self._initialize_standings(competition.id, teams)
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao gerar jogos de grupos: {e}")
            return False
    
    def _initialize_standings(self, competition_id: int, teams: List[Team]):
        """Inicializa tabela de classificação"""
        try:
            standings_data = []
            for team in teams:
                standings_data.append((competition_id, team.id))
            
            query = """
            INSERT INTO standings (competition_id, team_id, games_played, wins, draws, losses,
                                 goals_for, goals_against, goal_difference, points, sets_for, sets_against)
            VALUES (%s, %s, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            """
            execute_many(query, standings_data)
            
        except Exception as e:
            print(f"Erro ao inicializar classificação: {e}")


# Instância global do controlador de competições
competition_controller = CompetitionController()

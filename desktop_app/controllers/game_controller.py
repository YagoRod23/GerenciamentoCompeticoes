"""
Controller para gestão de jogos
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date, time, timedelta

from database.models import (Game, Team, Competition, GameStatus, calculate_standings,
                           update_standings_after_game)
from database.connection import execute_query
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType


class GameController:
    """Controlador para gestão de jogos"""
    
    def __init__(self):
        self.current_game: Optional[Game] = None
    
    def create_game(self, competition_id: int, home_team_id: int, away_team_id: int,
                   game_date: date, game_time: time, venue: str = "") -> Tuple[bool, str]:
        """Cria um novo jogo"""
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para criar jogos"
        
        try:
            # Validações
            if home_team_id == away_team_id:
                return False, "Uma equipe não pode jogar contra si mesma"
            
            # Verifica se as equipes existem
            home_team = Team.get_by_id(home_team_id)
            away_team = Team.get_by_id(away_team_id)
            
            if not home_team or not away_team:
                return False, "Uma ou ambas as equipes não foram encontradas"
            
            if not home_team.is_active or not away_team.is_active:
                return False, "Ambas as equipes devem estar ativas"
            
            # Verifica se a competição existe
            competition = Competition.get_by_id(competition_id)
            if not competition:
                return False, "Competição não encontrada"
            
            # Verifica conflito de horário para as equipes
            datetime_game = datetime.combine(game_date, game_time)
            conflict = self._check_schedule_conflict(home_team_id, away_team_id, datetime_game)
            if conflict:
                return False, f"Conflito de horário detectado: {conflict}"
            
            # Cria o jogo
            game = Game(
                competition_id=competition_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                game_date=game_date,
                game_time=game_time,
                venue=venue,
                status=GameStatus.SCHEDULED,
                created_by=auth_controller.current_user.id
            )
            
            if game.save():
                return True, "Jogo criado com sucesso"
            else:
                return False, "Erro ao salvar jogo no banco de dados"
                
        except Exception as e:
            return False, f"Erro ao criar jogo: {str(e)}"
    
    def update_game(self, game_id: int, **kwargs) -> Tuple[bool, str]:
        """Atualiza informações de um jogo"""
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para atualizar jogos"
        
        try:
            game = Game.get_by_id(game_id)
            if not game:
                return False, "Jogo não encontrado"
            
            # Não permite alterar jogos finalizados
            if game.status == GameStatus.FINISHED:
                return False, "Não é possível alterar jogos já finalizados"
            
            # Atualiza os campos permitidos
            allowed_fields = ['game_date', 'game_time', 'venue', 'home_team_id', 
                            'away_team_id', 'status']
            
            updated = False
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(game, field):
                    setattr(game, field, value)
                    updated = True
            
            if updated:
                game.updated_at = datetime.now()
                if game.save():
                    return True, "Jogo atualizado com sucesso"
                else:
                    return False, "Erro ao salvar alterações"
            else:
                return False, "Nenhuma alteração válida fornecida"
                
        except Exception as e:
            return False, f"Erro ao atualizar jogo: {str(e)}"
    
    def start_game(self, game_id: int) -> Tuple[bool, str]:
        """Inicia um jogo agendado"""
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para iniciar jogos"
        
        try:
            game = Game.get_by_id(game_id)
            if not game:
                return False, "Jogo não encontrado"
            
            if game.status != GameStatus.SCHEDULED:
                return False, f"Jogo deve estar agendado para ser iniciado. Status atual: {game.status.value}"
            
            # Atualiza status e horário de início
            game.status = GameStatus.IN_PROGRESS
            game.actual_start_time = datetime.now()
            game.updated_at = datetime.now()
            
            if game.save():
                self.current_game = game
                return True, "Jogo iniciado com sucesso"
            else:
                return False, "Erro ao iniciar jogo"
                
        except Exception as e:
            return False, f"Erro ao iniciar jogo: {str(e)}"
    
    def finish_game(self, game_id: int, home_score: int, away_score: int,
                   observations: str = "") -> Tuple[bool, str]:
        """Finaliza um jogo com o resultado"""
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para finalizar jogos"
        
        try:
            game = Game.get_by_id(game_id)
            if not game:
                return False, "Jogo não encontrado"
            
            if game.status == GameStatus.FINISHED:
                return False, "Jogo já foi finalizado"
            
            # Valida pontuações
            if home_score < 0 or away_score < 0:
                return False, "Pontuações devem ser valores positivos"
            
            # Atualiza o jogo
            game.status = GameStatus.FINISHED
            game.home_score = home_score
            game.away_score = away_score
            game.observations = observations
            game.actual_end_time = datetime.now()
            game.updated_at = datetime.now()
            
            if game.save():
                # Atualiza standings da competição
                success = update_standings_after_game(game)
                if success:
                    if self.current_game and self.current_game.id == game_id:
                        self.current_game = None
                    return True, "Jogo finalizado e standings atualizados com sucesso"
                else:
                    return True, "Jogo finalizado, mas houve erro ao atualizar standings"
            else:
                return False, "Erro ao finalizar jogo"
                
        except Exception as e:
            return False, f"Erro ao finalizar jogo: {str(e)}"
    
    def cancel_game(self, game_id: int, reason: str = "") -> Tuple[bool, str]:
        """Cancela um jogo"""
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para cancelar jogos"
        
        try:
            game = Game.get_by_id(game_id)
            if not game:
                return False, "Jogo não encontrado"
            
            if game.status == GameStatus.FINISHED:
                return False, "Não é possível cancelar um jogo já finalizado"
            
            game.status = GameStatus.CANCELLED
            game.observations = f"Cancelado: {reason}" if reason else "Cancelado"
            game.updated_at = datetime.now()
            
            if game.save():
                if self.current_game and self.current_game.id == game_id:
                    self.current_game = None
                return True, "Jogo cancelado com sucesso"
            else:
                return False, "Erro ao cancelar jogo"
                
        except Exception as e:
            return False, f"Erro ao cancelar jogo: {str(e)}"
    
    def get_games(self, competition_id: int = None, team_id: int = None,
                 status: GameStatus = None, date_from: date = None,
                 date_to: date = None) -> List[Game]:
        """Busca jogos com filtros opcionais"""
        try:
            query = "SELECT * FROM games WHERE 1=1"
            params = []
            
            if competition_id:
                query += " AND competition_id = %s"
                params.append(competition_id)
            
            if team_id:
                query += " AND (home_team_id = %s OR away_team_id = %s)"
                params.extend([team_id, team_id])
            
            if status:
                query += " AND status = %s"
                params.append(status.value)
            
            if date_from:
                query += " AND game_date >= %s"
                params.append(date_from)
            
            if date_to:
                query += " AND game_date <= %s"
                params.append(date_to)
            
            query += " ORDER BY game_date, game_time"
            
            results = execute_query(query, params, fetch=True)
            
            games = []
            if results:
                for game_data in results:
                    games.append(Game(
                        id=game_data['id'],
                        competition_id=game_data['competition_id'],
                        home_team_id=game_data['home_team_id'],
                        away_team_id=game_data['away_team_id'],
                        game_date=game_data['game_date'],
                        game_time=game_data['game_time'],
                        venue=game_data['venue'],
                        status=GameStatus(game_data['status']),
                        home_score=game_data['home_score'],
                        away_score=game_data['away_score'],
                        actual_start_time=game_data['actual_start_time'],
                        actual_end_time=game_data['actual_end_time'],
                        observations=game_data['observations'],
                        created_by=game_data['created_by'],
                        created_at=game_data['created_at'],
                        updated_at=game_data['updated_at']
                    ))
            
            return games
            
        except Exception as e:
            print(f"Erro ao buscar jogos: {e}")
            return []
    
    def get_game_by_id(self, game_id: int) -> Optional[Game]:
        """Busca jogo por ID"""
        return Game.get_by_id(game_id)
    
    def get_next_games(self, limit: int = 10) -> List[Game]:
        """Retorna próximos jogos agendados"""
        return self.get_games(
            status=GameStatus.SCHEDULED,
            date_from=date.today()
        )[:limit]
    
    def get_recent_games(self, limit: int = 10) -> List[Game]:
        """Retorna jogos recentes finalizados"""
        games = self.get_games(
            status=GameStatus.FINISHED,
            date_to=date.today()
        )
        # Retorna os mais recentes primeiro
        return sorted(games, key=lambda g: g.game_date, reverse=True)[:limit]
    
    def get_team_next_game(self, team_id: int) -> Optional[Game]:
        """Retorna próximo jogo de uma equipe"""
        games = self.get_games(
            team_id=team_id,
            status=GameStatus.SCHEDULED,
            date_from=date.today()
        )
        return games[0] if games else None
    
    def get_game_details(self, game_id: int) -> Dict[str, Any]:
        """Retorna detalhes completos de um jogo"""
        try:
            game = self.get_game_by_id(game_id)
            if not game:
                return {}
            
            # Busca informações das equipes
            home_team = Team.get_by_id(game.home_team_id)
            away_team = Team.get_by_id(game.away_team_id)
            competition = Competition.get_by_id(game.competition_id)
            
            return {
                'game': game,
                'home_team': home_team,
                'away_team': away_team,
                'competition': competition,
                'duration': self._calculate_game_duration(game),
                'winner': self._get_game_winner(game)
            }
            
        except Exception as e:
            print(f"Erro ao buscar detalhes do jogo: {e}")
            return {}
    
    def _check_schedule_conflict(self, home_team_id: int, away_team_id: int,
                               game_datetime: datetime, exclude_game_id: int = None) -> Optional[str]:
        """Verifica conflito de horário para as equipes"""
        try:
            # Margem de 2 horas antes e depois
            margin = timedelta(hours=2)
            start_window = game_datetime - margin
            end_window = game_datetime + margin
            
            query = """
            SELECT g.*, ht.name as home_name, at.name as away_name
            FROM games g
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE (g.home_team_id = %s OR g.away_team_id = %s OR 
                   g.home_team_id = %s OR g.away_team_id = %s)
            AND g.status IN ('scheduled', 'in_progress')
            AND DATETIME(g.game_date, g.game_time) BETWEEN %s AND %s
            """
            
            params = [home_team_id, home_team_id, away_team_id, away_team_id,
                     start_window, end_window]
            
            if exclude_game_id:
                query += " AND g.id != %s"
                params.append(exclude_game_id)
            
            results = execute_query(query, params, fetch=True)
            
            if results:
                conflict = results[0]
                return f"Conflito com jogo {conflict['home_name']} x {conflict['away_name']} em {conflict['game_date']} {conflict['game_time']}"
            
            return None
            
        except Exception as e:
            print(f"Erro ao verificar conflito de horário: {e}")
            return None
    
    def _calculate_game_duration(self, game: Game) -> Optional[timedelta]:
        """Calcula duração do jogo"""
        if game.actual_start_time and game.actual_end_time:
            return game.actual_end_time - game.actual_start_time
        return None
    
    def _get_game_winner(self, game: Game) -> Optional[str]:
        """Retorna o vencedor do jogo"""
        if game.status != GameStatus.FINISHED or game.home_score is None or game.away_score is None:
            return None
        
        if game.home_score > game.away_score:
            return "home"
        elif game.away_score > game.home_score:
            return "away"
        else:
            return "draw"


# Instância global do controlador de jogos
game_controller = GameController()

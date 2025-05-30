"""
Controller para gestão de equipes e atletas
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import date, datetime

from database.models import Team, Athlete, TechnicalStaff
from database.connection import execute_query, execute_many
from desktop_app.controllers.auth_controller import auth_controller
from database.models import UserType
from config.settings import SPORTS_CONFIG


class TeamController:
    """Controlador para gestão de equipes"""
    
    def __init__(self):
        self.current_team: Optional[Team] = None
    
    def create_team(self, name: str, short_name: str = "", logo_path: str = "",
                   primary_color: str = "#0066CC", secondary_color: str = "#FFFFFF",
                   contact_person: str = "", contact_phone: str = "", 
                   contact_email: str = "") -> Tuple[bool, str]:
        """Cria uma nova equipe"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para criar equipes"
        
        try:
            # Validações
            if not name.strip():
                return False, "Nome da equipe é obrigatório"
            
            if len(name) > 100:
                return False, "Nome da equipe deve ter no máximo 100 caracteres"
            
            # Verifica se já existe equipe com mesmo nome
            query = "SELECT id FROM teams WHERE name = %s AND is_active = TRUE"
            existing = execute_query(query, (name,), fetch=True)
            if existing:
                return False, "Já existe uma equipe com este nome"
            
            # Validação do nome abreviado
            if not short_name:
                short_name = name[:10]  # Primeiros 10 caracteres
            elif len(short_name) > 20:
                return False, "Nome abreviado deve ter no máximo 20 caracteres"
            
            # Cria a equipe
            team = Team(
                name=name,
                short_name=short_name,
                logo_path=logo_path,
                primary_color=primary_color,
                secondary_color=secondary_color,
                contact_person=contact_person,
                contact_phone=contact_phone,
                contact_email=contact_email,
                is_active=True
            )
            
            if team.save():
                self.current_team = team
                return True, "Equipe criada com sucesso"
            else:
                return False, "Erro ao salvar equipe"
                
        except Exception as e:
            return False, f"Erro ao criar equipe: {str(e)}"
    
    def update_team(self, team_id: int, **kwargs) -> Tuple[bool, str]:
        """Atualiza dados de uma equipe"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para editar equipes"
        
        try:
            # Busca a equipe
            team = Team.get_by_id(team_id)
            if not team:
                return False, "Equipe não encontrada"
            
            # Atualiza os campos fornecidos
            updated = False
            for field, value in kwargs.items():
                if hasattr(team, field) and field != 'id':
                    setattr(team, field, value)
                    updated = True
            
            if updated and team.save():
                return True, "Equipe atualizada com sucesso"
            else:
                return False, "Nenhuma alteração realizada"
                
        except Exception as e:
            return False, f"Erro ao atualizar equipe: {str(e)}"
    
    def delete_team(self, team_id: int) -> Tuple[bool, str]:
        """Desativa uma equipe"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para excluir equipes"
        
        try:
            # Verifica se a equipe existe
            team = Team.get_by_id(team_id)
            if not team:
                return False, "Equipe não encontrada"
            
            # Verifica se a equipe está em alguma competição ativa
            query = """
            SELECT c.name FROM competitions c
            JOIN team_registrations tr ON c.id = tr.competition_id
            WHERE tr.team_id = %s AND c.status IN ('planning', 'ongoing')
            """
            active_competitions = execute_query(query, (team_id,), fetch=True)
            
            if active_competitions:
                comp_names = [comp['name'] for comp in active_competitions]
                return False, f"Equipe não pode ser excluída pois está inscrita em: {', '.join(comp_names)}"
            
            # Desativa a equipe e seus atletas
            query = "UPDATE teams SET is_active = FALSE WHERE id = %s"
            execute_query(query, (team_id,))
            
            query = "UPDATE athletes SET is_active = FALSE WHERE team_id = %s"
            execute_query(query, (team_id,))
            
            return True, "Equipe excluída com sucesso"
            
        except Exception as e:
            return False, f"Erro ao excluir equipe: {str(e)}"
    
    def add_athlete(self, team_id: int, name: str, jersey_number: int, position: str = "",
                   birth_date: date = None, document_number: str = "", phone: str = "",
                   email: str = "", emergency_contact: str = "", emergency_phone: str = "",
                   is_captain: bool = False) -> Tuple[bool, str]:
        """Adiciona um atleta à equipe"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para gerenciar atletas"
        
        try:
            # Verifica se a equipe existe
            team = Team.get_by_id(team_id)
            if not team:
                return False, "Equipe não encontrada"
            
            # Validações
            if not name.strip():
                return False, "Nome do atleta é obrigatório"
            
            if len(name) > 100:
                return False, "Nome deve ter no máximo 100 caracteres"
            
            # Verifica limite de atletas por equipe
            current_athletes = len(team.get_athletes())
            max_athletes = 20  # Valor padrão das configurações
            
            if current_athletes >= max_athletes:
                return False, f"Equipe já atingiu o limite de {max_athletes} atletas"
            
            # Verifica se o número da camisa já está em uso
            if jersey_number:
                query = """
                SELECT id FROM athletes 
                WHERE team_id = %s AND jersey_number = %s AND is_active = TRUE
                """
                existing_number = execute_query(query, (team_id, jersey_number), fetch=True)
                if existing_number:
                    return False, f"Número da camisa {jersey_number} já está em uso"
            
            # Se for capitão, remove capitania dos outros
            if is_captain:
                query = "UPDATE athletes SET is_captain = FALSE WHERE team_id = %s"
                execute_query(query, (team_id,))
            
            # Cria o atleta
            athlete = Athlete(
                team_id=team_id,
                name=name,
                jersey_number=jersey_number,
                position=position,
                birth_date=birth_date,
                document_number=document_number,
                phone=phone,
                email=email,
                emergency_contact=emergency_contact,
                emergency_phone=emergency_phone,
                is_captain=is_captain,
                is_active=True
            )
            
            if athlete.save():
                return True, f"Atleta {name} adicionado com sucesso"
            else:
                return False, "Erro ao salvar atleta"
                
        except Exception as e:
            return False, f"Erro ao adicionar atleta: {str(e)}"
    
    def update_athlete(self, athlete_id: int, **kwargs) -> Tuple[bool, str]:
        """Atualiza dados de um atleta"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para editar atletas"
        
        try:
            # Busca o atleta
            athlete = Athlete.get_by_id(athlete_id)
            if not athlete:
                return False, "Atleta não encontrado"
            
            # Verifica se o número da camisa não está em conflito
            if 'jersey_number' in kwargs and kwargs['jersey_number']:
                new_number = kwargs['jersey_number']
                if new_number != athlete.jersey_number:
                    query = """
                    SELECT id FROM athletes 
                    WHERE team_id = %s AND jersey_number = %s AND id != %s AND is_active = TRUE
                    """
                    existing = execute_query(query, (athlete.team_id, new_number, athlete_id), fetch=True)
                    if existing:
                        return False, f"Número da camisa {new_number} já está em uso"
            
            # Se for definido como capitão, remove capitania dos outros
            if kwargs.get('is_captain', False):
                query = "UPDATE athletes SET is_captain = FALSE WHERE team_id = %s AND id != %s"
                execute_query(query, (athlete.team_id, athlete_id))
            
            # Atualiza os campos fornecidos
            updated = False
            for field, value in kwargs.items():
                if hasattr(athlete, field) and field != 'id':
                    setattr(athlete, field, value)
                    updated = True
            
            if updated and athlete.save():
                return True, "Atleta atualizado com sucesso"
            else:
                return False, "Nenhuma alteração realizada"
                
        except Exception as e:
            return False, f"Erro ao atualizar atleta: {str(e)}"
    
    def remove_athlete(self, athlete_id: int) -> Tuple[bool, str]:
        """Remove um atleta da equipe"""
        
        if not auth_controller.has_permission(UserType.ORGANIZATION):
            return False, "Permissão insuficiente para remover atletas"
        
        try:
            # Busca o atleta
            athlete = Athlete.get_by_id(athlete_id)
            if not athlete:
                return False, "Atleta não encontrado"
            
            # Verifica se o atleta tem participações em jogos
            query = """
            SELECT COUNT(*) as count FROM game_events 
            WHERE athlete_id = %s
            """
            result = execute_query(query, (athlete_id,), fetch=True)
            events_count = result[0]['count'] if result else 0
            
            if events_count > 0:
                # Se tem participações, apenas desativa
                athlete.is_active = False
                if athlete.save():
                    return True, "Atleta removido da equipe (mantido no histórico)"
                else:
                    return False, "Erro ao remover atleta"
            else:
                # Se não tem participações, pode deletar
                query = "DELETE FROM athletes WHERE id = %s"
                execute_query(query, (athlete_id,))
                return True, "Atleta removido definitivamente"
                
        except Exception as e:
            return False, f"Erro ao remover atleta: {str(e)}"
    
    def get_teams(self, active_only: bool = True) -> List[Team]:
        """Retorna lista de equipes"""
        try:
            if active_only:
                query = "SELECT * FROM teams WHERE is_active = TRUE ORDER BY name"
            else:
                query = "SELECT * FROM teams ORDER BY name, is_active DESC"
            
            results = execute_query(query, fetch=True)
            
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
            
        except Exception as e:
            print(f"Erro ao buscar equipes: {e}")
            return []
    
    def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """Busca equipe por ID"""
        return Team.get_by_id(team_id)
    
    def get_team_athletes(self, team_id: int, active_only: bool = True) -> List[Athlete]:
        """Retorna atletas de uma equipe"""
        try:
            if active_only:
                query = """
                SELECT * FROM athletes 
                WHERE team_id = %s AND is_active = TRUE 
                ORDER BY jersey_number, name
                """
            else:
                query = """
                SELECT * FROM athletes 
                WHERE team_id = %s 
                ORDER BY is_active DESC, jersey_number, name
                """
            
            results = execute_query(query, (team_id,), fetch=True)
            
            athletes = []
            if results:
                for athlete_data in results:
                    athletes.append(Athlete(
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
            
        except Exception as e:
            print(f"Erro ao buscar atletas: {e}")
            return []
    
    def get_athlete_by_id(self, athlete_id: int) -> Optional[Athlete]:
        """Busca atleta por ID"""
        return Athlete.get_by_id(athlete_id)
    
    def get_available_jersey_numbers(self, team_id: int) -> List[int]:
        """Retorna números de camisa disponíveis"""
        try:
            query = """
            SELECT jersey_number FROM athletes 
            WHERE team_id = %s AND is_active = TRUE AND jersey_number IS NOT NULL
            ORDER BY jersey_number
            """
            results = execute_query(query, (team_id,), fetch=True)
            
            used_numbers = [result['jersey_number'] for result in results] if results else []
            available_numbers = [i for i in range(1, 100) if i not in used_numbers]
            
            return available_numbers[:50]  # Retorna primeiros 50 disponíveis
            
        except Exception as e:
            print(f"Erro ao buscar números disponíveis: {e}")
            return list(range(1, 51))
    
    def get_team_statistics(self, team_id: int, competition_id: int = None) -> Dict[str, Any]:
        """Retorna estatísticas de uma equipe"""
        try:
            # Estatísticas básicas
            stats = {
                'total_athletes': 0,
                'total_games': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'points': 0
            }
            
            # Conta atletas ativos
            athletes = self.get_team_athletes(team_id)
            stats['total_athletes'] = len(athletes)
            
            # Estatísticas de jogos
            if competition_id:
                # Estatísticas de uma competição específica
                query = """
                SELECT * FROM standings 
                WHERE team_id = %s AND competition_id = %s
                """
                result = execute_query(query, (team_id, competition_id), fetch=True)
            else:
                # Estatísticas gerais (soma de todas as competições)
                query = """
                SELECT 
                    SUM(games_played) as total_games,
                    SUM(wins) as wins,
                    SUM(draws) as draws,
                    SUM(losses) as losses,
                    SUM(goals_for) as goals_for,
                    SUM(goals_against) as goals_against,
                    SUM(goal_difference) as goal_difference,
                    SUM(points) as points
                FROM standings 
                WHERE team_id = %s
                """
                result = execute_query(query, (team_id,), fetch=True)
            
            if result and result[0]:
                standing = result[0]
                stats.update({
                    'total_games': standing.get('total_games', 0) or standing.get('games_played', 0),
                    'wins': standing.get('wins', 0) or 0,
                    'draws': standing.get('draws', 0) or 0,
                    'losses': standing.get('losses', 0) or 0,
                    'goals_for': standing.get('goals_for', 0) or 0,
                    'goals_against': standing.get('goals_against', 0) or 0,
                    'goal_difference': standing.get('goal_difference', 0) or 0,
                    'points': standing.get('points', 0) or 0
                })
            
            return stats
            
        except Exception as e:
            print(f"Erro ao buscar estatísticas da equipe: {e}")
            return {
                'total_athletes': 0,
                'total_games': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'points': 0
            }
    
    def validate_team_for_sport(self, team_id: int, sport: str) -> Tuple[bool, str]:
        """Valida se uma equipe está apta para uma modalidade específica"""
        try:
            team = self.get_team_by_id(team_id)
            if not team:
                return False, "Equipe não encontrada"
            
            athletes = self.get_team_athletes(team_id)
            
            if sport not in SPORTS_CONFIG:
                return False, "Modalidade não configurada"
            
            sport_config = SPORTS_CONFIG[sport]
            min_players = sport_config['max_players_court'] + 2  # Mínimo: titulares + 2 reservas
            max_players = sport_config['max_team_size']
            
            # Verifica número mínimo de atletas
            if len(athletes) < min_players:
                return False, f"Equipe deve ter pelo menos {min_players} atletas para {sport_config['name']}"
            
            # Verifica número máximo de atletas
            if len(athletes) > max_players:
                return False, f"Equipe não pode ter mais que {max_players} atletas para {sport_config['name']}"
            
            # Verifica se tem capitão
            has_captain = any(athlete.is_captain for athlete in athletes)
            if not has_captain:
                return False, "Equipe deve ter um capitão designado"
            
            # Verifica números de camisa únicos
            jersey_numbers = [a.jersey_number for a in athletes if a.jersey_number]
            if len(jersey_numbers) != len(set(jersey_numbers)):
                return False, "Números de camisa devem ser únicos"
            
            return True, "Equipe apta para a modalidade"
            
        except Exception as e:
            return False, f"Erro ao validar equipe: {str(e)}"


# Instância global do controlador de equipes
team_controller = TeamController()

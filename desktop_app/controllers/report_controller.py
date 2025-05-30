"""
Controller para geração de relatórios
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from pathlib import Path
import json

from database.models import Competition, Team, Game, GameStatus, SportType
from database.connection import execute_query
from desktop_app.controllers.auth_controller import auth_controller
from desktop_app.controllers.competition_controller import competition_controller
from desktop_app.controllers.team_controller import team_controller
from desktop_app.controllers.game_controller import game_controller


class ReportController:
    """Controlador para geração de relatórios"""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_competition_report(self, competition_id: int) -> Dict[str, Any]:
        """Gera relatório completo de uma competição"""
        try:
            competition = competition_controller.get_competition_by_id(competition_id)
            if not competition:
                return {"error": "Competição não encontrada"}
            
            # Informações básicas da competição
            report = {
                "competition": {
                    "id": competition.id,
                    "name": competition.name,
                    "sport": competition.sport.value if competition.sport else "N/A",
                    "format": competition.format.value if competition.format else "N/A",
                    "start_date": competition.start_date.isoformat() if competition.start_date else None,
                    "end_date": competition.end_date.isoformat() if competition.end_date else None,
                    "status": competition.status,
                    "description": competition.description
                }
            }
            
            # Equipes participantes
            teams = competition_controller.get_competition_teams(competition_id)
            report["teams"] = []
            for team in teams:
                team_stats = team_controller.get_team_statistics(team.id, competition_id)
                report["teams"].append({
                    "id": team.id,
                    "name": team.name,
                    "short_name": team.short_name,
                    "statistics": team_stats
                })
            
            # Standings
            standings = competition_controller.get_standings(competition_id)
            report["standings"] = []
            for standing in standings:
                team = team_controller.get_team_by_id(standing.team_id)
                report["standings"].append({
                    "position": standing.position,
                    "team_name": team.name if team else "N/A",
                    "games_played": standing.games_played,
                    "wins": standing.wins,
                    "draws": standing.draws,
                    "losses": standing.losses,
                    "goals_for": standing.goals_for,
                    "goals_against": standing.goals_against,
                    "goal_difference": standing.goal_difference,
                    "points": standing.points
                })
            
            # Jogos
            games = game_controller.get_games(competition_id=competition_id)
            report["games"] = {
                "total": len(games),
                "scheduled": len([g for g in games if g.status == GameStatus.SCHEDULED]),
                "in_progress": len([g for g in games if g.status == GameStatus.IN_PROGRESS]),
                "finished": len([g for g in games if g.status == GameStatus.FINISHED]),
                "cancelled": len([g for g in games if g.status == GameStatus.CANCELLED]),
                "details": []
            }
            
            for game in games:
                home_team = team_controller.get_team_by_id(game.home_team_id)
                away_team = team_controller.get_team_by_id(game.away_team_id)
                
                game_detail = {
                    "id": game.id,
                    "home_team": home_team.name if home_team else "N/A",
                    "away_team": away_team.name if away_team else "N/A",
                    "date": game.game_date.isoformat(),
                    "time": game.game_time.isoformat() if game.game_time else None,
                    "venue": game.venue,
                    "status": game.status.value,
                    "home_score": game.home_score,
                    "away_score": game.away_score
                }
                report["games"]["details"].append(game_detail)
            
            # Estatísticas gerais
            report["statistics"] = self._calculate_competition_statistics(competition_id, games, teams)
            
            # Metadata do relatório
            report["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "generated_by": auth_controller.current_user.full_name if auth_controller.current_user else "Sistema"
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Erro ao gerar relatório: {str(e)}"}
    
    def generate_team_report(self, team_id: int, competition_id: int = None) -> Dict[str, Any]:
        """Gera relatório de uma equipe"""
        try:
            team = team_controller.get_team_by_id(team_id)
            if not team:
                return {"error": "Equipe não encontrada"}
            
            report = {
                "team": {
                    "id": team.id,
                    "name": team.name,
                    "short_name": team.short_name,
                    "contact_person": team.contact_person,
                    "contact_phone": team.contact_phone,
                    "contact_email": team.contact_email,
                    "is_active": team.is_active,
                    "created_at": team.created_at.isoformat() if team.created_at else None
                }
            }
            
            # Atletas
            athletes = team_controller.get_team_athletes(team_id)
            report["athletes"] = []
            for athlete in athletes:
                report["athletes"].append({
                    "id": athlete.id,
                    "name": athlete.name,
                    "jersey_number": athlete.jersey_number,
                    "position": athlete.position,
                    "is_captain": athlete.is_captain,
                    "is_active": athlete.is_active
                })
            
            # Estatísticas
            stats = team_controller.get_team_statistics(team_id, competition_id)
            report["statistics"] = stats
            
            # Histórico de jogos
            games = game_controller.get_games(team_id=team_id, competition_id=competition_id)
            report["games"] = {
                "total": len(games),
                "as_home": len([g for g in games if g.home_team_id == team_id]),
                "as_away": len([g for g in games if g.away_team_id == team_id]),
                "details": []
            }
            
            for game in games:
                is_home = game.home_team_id == team_id
                opponent_id = game.away_team_id if is_home else game.home_team_id
                opponent = team_controller.get_team_by_id(opponent_id)
                
                game_detail = {
                    "id": game.id,
                    "date": game.game_date.isoformat(),
                    "opponent": opponent.name if opponent else "N/A",
                    "is_home": is_home,
                    "venue": game.venue,
                    "status": game.status.value,
                    "team_score": game.home_score if is_home else game.away_score,
                    "opponent_score": game.away_score if is_home else game.home_score
                }
                
                if game.status == GameStatus.FINISHED and game.home_score is not None and game.away_score is not None:
                    if is_home:
                        result = "win" if game.home_score > game.away_score else "loss" if game.home_score < game.away_score else "draw"
                    else:
                        result = "win" if game.away_score > game.home_score else "loss" if game.away_score < game.home_score else "draw"
                    game_detail["result"] = result
                
                report["games"]["details"].append(game_detail)
            
            # Metadata
            report["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "generated_by": auth_controller.current_user.full_name if auth_controller.current_user else "Sistema",
                "competition_filter": competition_id
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Erro ao gerar relatório da equipe: {str(e)}"}
    
    def generate_games_schedule_report(self, competition_id: int = None, 
                                     date_from: date = None, date_to: date = None) -> Dict[str, Any]:
        """Gera relatório de programação de jogos"""
        try:
            # Define período padrão se não especificado
            if not date_from:
                date_from = date.today()
            if not date_to:
                date_to = date_from + timedelta(days=30)
            
            report = {
                "schedule": {
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat(),
                    "competition_id": competition_id
                }
            }
            
            # Busca jogos no período
            games = game_controller.get_games(
                competition_id=competition_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Organiza jogos por data
            games_by_date = {}
            for game in games:
                date_str = game.game_date.isoformat()
                if date_str not in games_by_date:
                    games_by_date[date_str] = []
                
                home_team = team_controller.get_team_by_id(game.home_team_id)
                away_team = team_controller.get_team_by_id(game.away_team_id)
                competition = competition_controller.get_competition_by_id(game.competition_id)
                
                games_by_date[date_str].append({
                    "id": game.id,
                    "time": game.game_time.isoformat() if game.game_time else None,
                    "home_team": home_team.name if home_team else "N/A",
                    "away_team": away_team.name if away_team else "N/A",
                    "competition": competition.name if competition else "N/A",
                    "venue": game.venue,
                    "status": game.status.value
                })
            
            # Ordena jogos dentro de cada data por horário
            for date_str in games_by_date:
                games_by_date[date_str].sort(key=lambda g: g["time"] or "00:00:00")
            
            report["games_by_date"] = games_by_date
            
            # Estatísticas do período
            report["statistics"] = {
                "total_games": len(games),
                "by_status": {
                    "scheduled": len([g for g in games if g.status == GameStatus.SCHEDULED]),
                    "in_progress": len([g for g in games if g.status == GameStatus.IN_PROGRESS]),
                    "finished": len([g for g in games if g.status == GameStatus.FINISHED]),
                    "cancelled": len([g for g in games if g.status == GameStatus.CANCELLED])
                },
                "total_days": (date_to - date_from).days + 1,
                "days_with_games": len(games_by_date)
            }
            
            # Metadata
            report["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "generated_by": auth_controller.current_user.full_name if auth_controller.current_user else "Sistema"
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Erro ao gerar relatório de programação: {str(e)}"}
    
    def save_report_to_file(self, report: Dict[str, Any], filename: str) -> Tuple[bool, str]:
        """Salva relatório em arquivo JSON"""
        try:
            if "error" in report:
                return False, report["error"]
            
            filepath = self.reports_dir / f"{filename}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            return True, f"Relatório salvo em: {filepath}"
            
        except Exception as e:
            return False, f"Erro ao salvar relatório: {str(e)}"
    
    def _calculate_competition_statistics(self, competition_id: int, 
                                        games: List[Game], teams: List[Team]) -> Dict[str, Any]:
        """Calcula estatísticas gerais da competição"""
        try:
            finished_games = [g for g in games if g.status == GameStatus.FINISHED and 
                            g.home_score is not None and g.away_score is not None]
            
            total_goals = sum(g.home_score + g.away_score for g in finished_games)
            
            stats = {
                "total_teams": len(teams),
                "total_games_scheduled": len(games),
                "games_finished": len(finished_games),
                "completion_percentage": (len(finished_games) / len(games) * 100) if games else 0,
                "total_goals": total_goals,
                "average_goals_per_game": total_goals / len(finished_games) if finished_games else 0,
                "wins": 0,
                "draws": 0,
                "highest_scoring_game": None,
                "most_wins_team": None,
                "best_attack": None,
                "best_defense": None
            }
            
            # Encontra jogo com mais gols
            if finished_games:
                highest_scoring = max(finished_games, key=lambda g: g.home_score + g.away_score)
                home_team = team_controller.get_team_by_id(highest_scoring.home_team_id)
                away_team = team_controller.get_team_by_id(highest_scoring.away_team_id)
                
                stats["highest_scoring_game"] = {
                    "home_team": home_team.name if home_team else "N/A",
                    "away_team": away_team.name if away_team else "N/A",
                    "score": f"{highest_scoring.home_score}-{highest_scoring.away_score}",
                    "total_goals": highest_scoring.home_score + highest_scoring.away_score,
                    "date": highest_scoring.game_date.isoformat()
                }
            
            # Conta vitórias e empates
            for game in finished_games:
                if game.home_score > game.away_score or game.away_score > game.home_score:
                    stats["wins"] += 1
                else:
                    stats["draws"] += 1
            
            # Busca estatísticas das equipes para encontrar melhores
            standings = competition_controller.get_standings(competition_id)
            if standings:
                # Equipe com mais vitórias
                most_wins = max(standings, key=lambda s: s.wins)
                team = team_controller.get_team_by_id(most_wins.team_id)
                stats["most_wins_team"] = {
                    "name": team.name if team else "N/A",
                    "wins": most_wins.wins
                }
                
                # Melhor ataque (mais gols marcados)
                best_attack = max(standings, key=lambda s: s.goals_for)
                team = team_controller.get_team_by_id(best_attack.team_id)
                stats["best_attack"] = {
                    "name": team.name if team else "N/A",
                    "goals": best_attack.goals_for
                }
                
                # Melhor defesa (menos gols sofridos)
                teams_with_games = [s for s in standings if s.games_played > 0]
                if teams_with_games:
                    best_defense = min(teams_with_games, key=lambda s: s.goals_against)
                    team = team_controller.get_team_by_id(best_defense.team_id)
                    stats["best_defense"] = {
                        "name": team.name if team else "N/A",
                        "goals_against": best_defense.goals_against
                    }
            
            return stats
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {e}")
            return {"error": "Erro ao calcular estatísticas"}


# Instância global do controlador de relatórios
report_controller = ReportController()

"""
Gerador de relatórios
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import tempfile
import os

from database.models import Team, Player, Game, Competition


class ReportGenerator:
    """Gerador de relatórios do sistema"""
    
    @staticmethod
    def generate_team_report(team: Team) -> str:
        """
        Gera relatório detalhado de uma equipe
        
        Args:
            team: Objeto Team
            
        Returns:
            Relatório como string
        """
        report = f"""
RELATÓRIO DA EQUIPE
==================

Nome: {team.name}
Abreviação: {team.abbreviation}
Cidade: {team.city or 'Não informado'}
Estado: {team.state or 'Não informado'}
Ano de Fundação: {team.founded_year or 'Não informado'}
Cores: {team.colors or 'Não informado'}
Estádio: {team.stadium or 'Não informado'}
Técnico: {team.coach or 'Não informado'}

Data de Criação: {team.created_at.strftime('%d/%m/%Y %H:%M') if team.created_at else 'Não informado'}
Última Atualização: {team.updated_at.strftime('%d/%m/%Y %H:%M') if team.updated_at else 'Não informado'}

Jogadores:
"""
        
        if hasattr(team, 'players') and team.players:
            for player in team.players:
                report += f"- {player.name}"
                if player.position:
                    report += f" ({player.position})"
                if player.age:
                    report += f" - {player.age} anos"
                report += "\n"
        else:
            report += "Nenhum jogador cadastrado.\n"
        
        return report
    
    @staticmethod
    def generate_competition_report(competition: Competition) -> str:
        """
        Gera relatório de uma competição
        
        Args:
            competition: Objeto Competition
            
        Returns:
            Relatório como string
        """
        report = f"""
RELATÓRIO DA COMPETIÇÃO
======================

Nome: {competition.name}
Tipo: {competition.competition_type.value}
Temporada: {competition.season}
Descrição: {competition.description or 'Não informado'}

Datas:
Início: {competition.start_date.strftime('%d/%m/%Y') if competition.start_date else 'Não informado'}
Término: {competition.end_date.strftime('%d/%m/%Y') if competition.end_date else 'Não informado'}
Limite de Inscrições: {competition.registration_deadline.strftime('%d/%m/%Y') if competition.registration_deadline else 'Não informado'}

Configurações:
Máximo de Equipes: {competition.max_teams or 'Ilimitado'}
Status: {'Ativa' if competition.is_active else 'Inativa'}

Equipes Participantes:
"""
        
        if hasattr(competition, 'teams') and competition.teams:
            for team in competition.teams:
                report += f"- {team.name}\n"
        else:
            report += "Nenhuma equipe inscrita.\n"
        
        return report
    
    @staticmethod
    def generate_game_report(game: Game) -> str:
        """
        Gera relatório de um jogo
        
        Args:
            game: Objeto Game
            
        Returns:
            Relatório como string
        """
        home_team_name = game.home_team.name if game.home_team else "Equipe não encontrada"
        away_team_name = game.away_team.name if game.away_team else "Equipe não encontrada"
        
        report = f"""
RELATÓRIO DO JOGO
================

Data: {game.game_date.strftime('%d/%m/%Y') if game.game_date else 'Não informado'}
Hora: {game.game_time.strftime('%H:%M') if game.game_time else 'Não informado'}

Equipes:
Casa: {home_team_name}
Visitante: {away_team_name}

Resultado:
"""
        
        if game.home_team_score is not None and game.away_team_score is not None:
            report += f"{home_team_name} {game.home_team_score} x {game.away_team_score} {away_team_name}\n"
            
            # Determinar vencedor
            if game.home_team_score > game.away_team_score:
                report += f"Vencedor: {home_team_name}\n"
            elif game.away_team_score > game.home_team_score:
                report += f"Vencedor: {away_team_name}\n"
            else:
                report += "Resultado: Empate\n"
        else:
            report += "Jogo ainda não realizado.\n"
        
        report += f"\nLocal: {game.location or 'Não informado'}\n"
        report += f"Status: {game.status.value if game.status else 'Não informado'}\n"
        
        # Eventos do jogo
        if hasattr(game, 'events') and game.events:
            report += "\nEventos do Jogo:\n"
            report += "----------------\n"
            for event in sorted(game.events, key=lambda x: x.minute):
                player_name = event.player.name if event.player else "Jogador não encontrado"
                report += f"{event.minute}' - {event.event_type.value} - {player_name}\n"
        
        return report
    
    @staticmethod
    def generate_standings_report(competition: Competition) -> str:
        """
        Gera relatório de classificação de uma competição
        
        Args:
            competition: Objeto Competition
            
        Returns:
            Relatório como string
        """
        report = f"""
CLASSIFICAÇÃO - {competition.name}
{competition.season}
{'=' * (len(competition.name) + len(str(competition.season)) + 4)}

Pos | Equipe                | J  | V  | E  | D  | GP | GC | SG | Pts
"""
        
        # Aqui você implementaria a lógica para calcular a classificação
        # Por enquanto, retorna um placeholder
        report += "1   | Exemplo Futebol Club | 10 | 7  | 2  | 1  | 18 | 8  | 10 | 23 |\n"
        report += "2   | Esporte Clube        | 10 | 6  | 3  | 1  | 15 | 7  | 8  | 21 |\n"
        
        return report
    
    @staticmethod
    def save_report_to_file(report_content: str, filename: str) -> str:
        """
        Salva relatório em arquivo
        
        Args:
            report_content: Conteúdo do relatório
            filename: Nome do arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return file_path

"""
Performance scoring system for UC Kingdom bot
Implements detailed performance criteria for 15+ player games
"""
from typing import Dict, List, Tuple, Optional
from database.models import Game, User
from game.role_distribution import get_team_for_role

class PerformanceSystem:
    def __init__(self):
        self.performance_criteria = {
            "villager": {
                "survive_to_end": 2,
                "help_eliminate_predator": 1,
                "win_as_team": 1,
                "special_role_bonus": 1
            },
            "predator": {
                "survive_to_end": 2,
                "successful_elimination": 1,
                "win_as_team": 1,
                "leadership_bonus": 1
            },
            "neutral": {
                "achieve_objective": 3,
                "survive_to_end": 1,
                "special_action_bonus": 1
            }
        }
    
    def calculate_performance_score(self, game: Game, player_id: int, role: str, 
                                  eliminated_players: List[int], winning_team: str,
                                  night_actions: Dict, votes: Dict) -> Tuple[int, int]:
        """
        Calculate performance score and stars for a player
        Returns (stars, bricks_earned)
        """
        if len(game.get_players_list()) < 15:
            return self._basic_scoring(role, player_id, eliminated_players, winning_team)
        
        return self._advanced_scoring(game, player_id, role, eliminated_players, 
                                    winning_team, night_actions, votes)
    
    def _basic_scoring(self, role: str, player_id: int, eliminated_players: List[int], 
                      winning_team: str) -> Tuple[int, int]:
        """Basic scoring for games with less than 15 players"""
        team = get_team_for_role(role)
        won = (winning_team == "villager" and team == "villager") or \
              (winning_team == "predator" and team in ["predator", "predator_aligned"])
        
        stars = 3 if won else 1
        bricks = 40 if won else 10
        
        if player_id not in eliminated_players:
            stars += 1
            bricks += 10
        
        return min(stars, 5), bricks
    
    def _advanced_scoring(self, game: Game, player_id: int, role: str,
                         eliminated_players: List[int], winning_team: str,
                         night_actions: Dict, votes: Dict) -> Tuple[int, int]:
        """Advanced scoring for 15+ player games"""
        team = get_team_for_role(role)
        stars = 0
        bricks = 10
        
        won = (winning_team == "villager" and team == "villager") or \
              (winning_team == "predator" and team in ["predator", "predator_aligned"])
        
        if won:
            stars += 1
            bricks += 30
        
        if player_id not in eliminated_players:
            stars += 2
            bricks += 20
        
        stars += self._calculate_role_specific_bonus(role, player_id, game, 
                                                   night_actions, votes)
        
        if role in ["lion", "leopard"]:
            stars += 1
        
        return min(stars, 5), min(bricks, 100)
    
    def _calculate_role_specific_bonus(self, role: str, player_id: int, game: Game,
                                     night_actions: Dict, votes: Dict) -> int:
        """Calculate role-specific performance bonuses"""
        bonus = 0
        
        if role == "lion":
            if self._survived_multiple_attacks(player_id, night_actions):
                bonus += 1
        elif role == "leopard":
            if self._led_successful_eliminations(player_id, night_actions):
                bonus += 1
        elif role == "owl":
            if self._successful_protections(player_id, night_actions):
                bonus += 1
        elif role == "hunter":
            if self._successful_investigations(player_id, night_actions):
                bonus += 1
        elif role == "fox":
            if self._achieved_fox_victory(player_id, game):
                bonus += 2
        
        return bonus
    
    def _survived_multiple_attacks(self, player_id: int, night_actions: Dict) -> bool:
        """Check if Lion survived multiple attacks"""
        attack_count = 0
        for round_actions in night_actions.values():
            if isinstance(round_actions, dict):
                for action in round_actions.values():
                    if isinstance(action, dict) and action.get('target') == player_id:
                        attack_count += 1
        return attack_count >= 2
    
    def _led_successful_eliminations(self, player_id: int, night_actions: Dict) -> bool:
        """Check if Leopard led successful eliminations"""
        successful_commands = 0
        for round_actions in night_actions.values():
            if isinstance(round_actions, dict):
                leopard_action = round_actions.get(player_id)
                if isinstance(leopard_action, dict) and leopard_action.get('action') == 'command':
                    successful_commands += 1
        return successful_commands >= 2
    
    def _successful_protections(self, player_id: int, night_actions: Dict) -> bool:
        """Check if Owl made successful protections"""
        protection_count = 0
        for round_actions in night_actions.values():
            if isinstance(round_actions, dict):
                owl_action = round_actions.get(player_id)
                if isinstance(owl_action, dict) and owl_action.get('action') == 'protect':
                    protection_count += 1
        return protection_count >= 2
    
    def _successful_investigations(self, player_id: int, night_actions: Dict) -> bool:
        """Check if Hunter made successful investigations"""
        investigation_count = 0
        for round_actions in night_actions.values():
            if isinstance(round_actions, dict):
                hunter_action = round_actions.get(player_id)
                if isinstance(hunter_action, dict) and hunter_action.get('action') == 'investigate':
                    investigation_count += 1
        return investigation_count >= 2
    
    def _achieved_fox_victory(self, player_id: int, game: Game) -> bool:
        """Check if Fox achieved their unique victory condition"""
        eliminated = game.get_eliminated_players()
        return player_id in eliminated
    
    def format_performance_results(self, results: Dict[int, Tuple[int, int]], 
                                 users: Dict[int, User], roles: Dict[int, str],
                                 winning_team: str) -> str:
        """Format performance results for display"""
        message = f"🏆 <b>Game Results - {winning_team.title()} Team Wins!</b>\n\n"
        
        winners = []
        notable_losers = []
        
        for player_id, (stars, bricks) in results.items():
            user = users.get(player_id)
            role = roles.get(player_id, "unknown")
            team = get_team_for_role(role)
            
            won = (winning_team == "villager" and team == "villager") or \
                  (winning_team == "predator" and team in ["predator", "predator_aligned"])
            
            star_display = "⭐" * stars
            player_result = f"{user.ign if user else 'Unknown'}: {star_display} (+{bricks} bricks)"
            
            if won:
                winners.append(player_result)
            elif stars >= 3:
                notable_losers.append(player_result)
        
        if winners:
            message += "🎉 <b>Winning Team:</b>\n"
            for winner in winners:
                message += f"  • {winner}\n"
        
        if notable_losers:
            message += "\n🌟 <b>Notable Performances:</b>\n"
            for performer in notable_losers:
                message += f"  • {performer}\n"
        
        return message

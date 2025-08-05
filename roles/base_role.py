from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from telegram import InlineKeyboardMarkup

class BaseRole(ABC):
    def __init__(self, role_name: str, team: str, emoji: str):
        self.role_name = role_name
        self.team = team
        self.emoji = emoji
        self.role_data: Dict[str, Any] = {}
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_win_condition(self) -> str:
        pass
    
    def has_night_action(self) -> bool:
        return False
    
    def get_night_action_message(self, player_name: str) -> str:
        return f"{self.emoji} {player_name}, you have no night action."
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        return None
    
    def can_be_targeted(self) -> bool:
        return True
    
    def on_attacked(self, attacker_id: int, game_data: Dict) -> Dict:
        return game_data
    
    def on_eliminated(self, game_data: Dict) -> Dict:
        return game_data
    
    def get_role_data(self) -> Dict[str, Any]:
        return self.role_data
    
    def set_role_data(self, data: Dict[str, Any]):
        self.role_data = data
    
    def get_performance_criteria(self) -> Dict[str, int]:
        return {
            "survive_to_end": 2,
            "help_eliminate_enemy": 3,
            "team_wins": 4
        }

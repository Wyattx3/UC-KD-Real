from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

@dataclass
class User:
    telegram_id: int
    ign: str
    rank_level: int = 0
    rank_stars: int = 1
    bricks: int = 0
    games_played: int = 0
    games_won: int = 0
    joined_date: datetime = None
    last_ign_change: datetime = None
    items: str = ""
    
    def get_items_list(self) -> List[str]:
        if not self.items:
            return []
        return json.loads(self.items)
    
    def add_item(self, item: str):
        items_list = self.get_items_list()
        items_list.append(item)
        self.items = json.dumps(items_list)
    
    def remove_item(self, item: str):
        items_list = self.get_items_list()
        if item in items_list:
            items_list.remove(item)
            self.items = json.dumps(items_list)
    
    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

@dataclass
class Game:
    game_id: str
    chat_id: int
    creator_id: int
    status: str
    players: str
    roles: str
    current_round: int = 1
    current_phase: str = "lobby"
    night_actions: str = ""
    votes: str = ""
    eliminated_players: str = ""
    game_data: str = ""
    created_at: datetime = None
    
    def get_players_list(self) -> List[int]:
        if not self.players:
            return []
        return json.loads(self.players)
    
    def get_roles_dict(self) -> Dict[int, str]:
        if not self.roles:
            return {}
        return json.loads(self.roles)
    
    def get_night_actions(self) -> Dict[str, Any]:
        if not self.night_actions:
            return {}
        return json.loads(self.night_actions)
    
    def get_votes_dict(self) -> Dict[int, int]:
        if not self.votes:
            return {}
        return json.loads(self.votes)
    
    def get_eliminated_players(self) -> List[int]:
        if not self.eliminated_players:
            return []
        return json.loads(self.eliminated_players)
    
    def get_game_data(self) -> Dict[str, Any]:
        if not self.game_data:
            return {}
        return json.loads(self.game_data)

@dataclass
class GamePlayer:
    game_id: str
    telegram_id: int
    role: str
    is_alive: bool = True
    night_action: str = ""
    vote_target: Optional[int] = None
    equipped_item: Optional[str] = None
    role_data: str = ""
    
    def get_role_data(self) -> Dict[str, Any]:
        if not self.role_data:
            return {}
        return json.loads(self.role_data)
    
    def set_role_data(self, data: Dict[str, Any]):
        self.role_data = json.dumps(data)

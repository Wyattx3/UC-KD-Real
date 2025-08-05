from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .base_role import BaseRole
from typing import Optional, Dict, Any

class Leopard(BaseRole):
    def __init__(self):
        super().__init__("leopard", "predator", "🐆")
        self.role_data = {"vulture_command_used": False}
    
    def get_description(self) -> str:
        return "Leader of the Jackal pack. Fast and decisive. Chooses nightly targets and can command Vulture once per game."
    
    def get_win_condition(self) -> str:
        return "Predators eliminate all Villagers and hostile Neutrals."
    
    def has_night_action(self) -> bool:
        return True
    
    def get_night_action_message(self, player_name: str) -> str:
        return f"🐆 {player_name}, who shall be your prey tonight?"
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        buttons = [[InlineKeyboardButton("Choose Target", callback_data=f"night_action_{game_id}_kill")]]
        
        if not self.role_data["vulture_command_used"]:
            buttons.append([InlineKeyboardButton("Command Vulture", callback_data=f"night_action_{game_id}_command_vulture")])
        
        return InlineKeyboardMarkup(buttons)

class Tiger(BaseRole):
    def __init__(self):
        super().__init__("tiger", "predator", "🐅")
        self.role_data = {"is_active_leader": False, "vulture_command_used": False}
    
    def get_description(self) -> str:
        return "Intelligent second-in-command. Becomes active leader if Leopard dies."
    
    def get_win_condition(self) -> str:
        return "Predators eliminate all Villagers and hostile Neutrals."
    
    def has_night_action(self) -> bool:
        return self.role_data.get("is_active_leader", False)
    
    def get_night_action_message(self, player_name: str) -> str:
        return f"🐅 {player_name}, the pack awaits your command. Who shall we hunt?"
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        if not self.role_data.get("is_active_leader", False):
            return None
        
        buttons = [[InlineKeyboardButton("Choose Target", callback_data=f"night_action_{game_id}_kill")]]
        
        if not self.role_data["vulture_command_used"]:
            buttons.append([InlineKeyboardButton("Command Vulture", callback_data=f"night_action_{game_id}_command_vulture")])
        
        return InlineKeyboardMarkup(buttons)

class Jackal(BaseRole):
    def __init__(self):
        super().__init__("jackal", "predator", "🐕")
    
    def get_description(self) -> str:
        return "Pack hunter loyal to Leopard/Tiger. Carries out kill orders from the pack leader."
    
    def get_win_condition(self) -> str:
        return "Predators eliminate all Villagers and hostile Neutrals."

class WildBoar(BaseRole):
    def __init__(self):
        super().__init__("wild_boar", "predator", "🐗")
    
    def get_description(self) -> str:
        return "Aggressive and territorial. Chooses locations to forage, blocking Herbivores and potentially killing."
    
    def get_win_condition(self) -> str:
        return "Predators eliminate all Villagers and hostile Neutrals."
    
    def has_night_action(self) -> bool:
        return True
    
    def get_night_action_message(self, player_name: str) -> str:
        return f"🐗 {player_name}, where would you like to rampage tonight?"
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("North Hill", callback_data=f"night_action_{game_id}_rampage_north")],
            [InlineKeyboardButton("South Stream", callback_data=f"night_action_{game_id}_rampage_south")],
            [InlineKeyboardButton("East Cave", callback_data=f"night_action_{game_id}_rampage_east")],
            [InlineKeyboardButton("West Lake", callback_data=f"night_action_{game_id}_rampage_west")]
        ])

class Vulture(BaseRole):
    def __init__(self):
        super().__init__("vulture", "predator_aligned", "🐦‍⬛")
    
    def get_description(self) -> str:
        return "Scavenger sided with predators. Can be ordered by Leopard/Tiger to sacrifice itself for the pack."
    
    def get_win_condition(self) -> str:
        return "Successfully sacrifice as ordered and Predator team wins, OR Predator team wins and Vulture survives."

class Crocodile(BaseRole):
    def __init__(self):
        super().__init__("crocodile", "predator_aligned", "🐊")
        self.role_data = {"attacks_remaining": 2}
    
    def get_description(self) -> str:
        return "Ambush predator at South Stream. Only animal that can injure Lion on first attack. Has two attack chances total."
    
    def get_win_condition(self) -> str:
        return "Successfully attack Lion AND Predator team wins."
    
    def has_night_action(self) -> bool:
        return self.role_data["attacks_remaining"] > 0
    
    def get_night_action_message(self, player_name: str) -> str:
        remaining = self.role_data["attacks_remaining"]
        return f"🐊 {player_name}, you have {remaining} attack{'s' if remaining != 1 else ''} remaining. Choose your target carefully."
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        if self.role_data["attacks_remaining"] <= 0:
            return None
        
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("Choose Target", callback_data=f"night_action_{game_id}_ambush")
        ]])

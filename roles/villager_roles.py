from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .base_role import BaseRole
from typing import Optional, Dict, Any

class Lion(BaseRole):
    def __init__(self):
        super().__init__("lion", "villager", "🦁")
        self.role_data = {"injured": False, "attacks_survived": 0}
    
    def get_description(self) -> str:
        return "Leader of the good animals. Immune to first predator attack (except Crocodile/Hunter). If attacked by Crocodile, becomes injured and vulnerable."
    
    def get_win_condition(self) -> str:
        return "Eliminate all Predators and hostile Neutrals, and survive."
    
    def on_attacked(self, attacker_id: int, game_data: Dict) -> Dict:
        attacker_role = game_data.get("roles", {}).get(attacker_id, "")
        
        if attacker_role == "crocodile":
            self.role_data["injured"] = True
            game_data["lion_injured"] = True
            return game_data
        elif attacker_role == "hunter":
            return game_data
        elif not self.role_data["injured"]:
            self.role_data["attacks_survived"] += 1
            game_data["attack_blocked"] = True
            game_data["attacker_revealed"] = attacker_id
            return game_data
        
        return game_data

class Owl(BaseRole):
    def __init__(self):
        super().__init__("owl", "villager", "🦉")
        self.role_data = {"last_healed": None, "self_heal_used": False}
    
    def get_description(self) -> str:
        return "Wise nocturnal healer. Can protect one player each night. Cannot heal same player twice in a row. Can self-heal once per game."
    
    def get_win_condition(self) -> str:
        return "Eliminate all Predators and hostile Neutrals, and survive."
    
    def has_night_action(self) -> bool:
        return True
    
    def get_night_action_message(self, player_name: str) -> str:
        return f"🦉 {player_name}, who would you like to protect tonight?"
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("Choose Target", callback_data=f"night_action_{game_id}_protect")
        ]])

class Turtle(BaseRole):
    def __init__(self):
        super().__init__("turtle", "villager", "🐢")
        self.role_data = {"shell_intact": True}
    
    def get_description(self) -> str:
        return "Slow and defensive. Hard shell protects from first attack, but cracks and becomes vulnerable afterward."
    
    def get_win_condition(self) -> str:
        return "Eliminate all Predators and hostile Neutrals, and survive."
    
    def on_attacked(self, attacker_id: int, game_data: Dict) -> Dict:
        if self.role_data["shell_intact"]:
            self.role_data["shell_intact"] = False
            game_data["attack_blocked"] = True
            game_data["turtle_shell_cracked"] = True
            return game_data
        
        return game_data

class Hunter(BaseRole):
    def __init__(self):
        super().__init__("hunter", "villager", "🏹")
    
    def get_description(self) -> str:
        return "The last uninfected human. Skilled tracker and marksman. Can investigate or kill each night."
    
    def get_win_condition(self) -> str:
        return "Eliminate all Predators and hostile Neutrals, and survive."
    
    def has_night_action(self) -> bool:
        return True
    
    def get_night_action_message(self, player_name: str) -> str:
        return f"🏹 {player_name}, choose your action for tonight:"
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Investigate", callback_data=f"night_action_{game_id}_investigate")],
            [InlineKeyboardButton("Kill", callback_data=f"night_action_{game_id}_kill")]
        ])

class Monkey(BaseRole):
    def __init__(self):
        super().__init__("monkey", "villager", "🐒")
    
    def get_description(self) -> str:
        return "Intelligent and talkative. Can role-block one player each night with endless chatter."
    
    def get_win_condition(self) -> str:
        return "Eliminate all Predators and hostile Neutrals, and survive."
    
    def has_night_action(self) -> bool:
        return True
    
    def get_night_action_message(self, player_name: str) -> str:
        return f"🐒 {player_name}, who would you like to chat with tonight?"
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("Choose Target", callback_data=f"night_action_{game_id}_roleblock")
        ]])

class Bat(BaseRole):
    def __init__(self):
        super().__init__("bat", "villager", "🦇")
        self.role_data = {"cave_destroyed": False}
    
    def get_description(self) -> str:
        return "Uses echolocation. If attacked, identifies attacker but loses cave and dies next night."
    
    def get_win_condition(self) -> str:
        return "Eliminate all Predators and hostile Neutrals, and survive."
    
    def on_attacked(self, attacker_id: int, game_data: Dict) -> Dict:
        if not self.role_data["cave_destroyed"]:
            self.role_data["cave_destroyed"] = True
            game_data["attack_blocked"] = True
            game_data["attacker_revealed"] = attacker_id
            game_data["bat_dies_next_night"] = True
            return game_data
        
        return game_data

class Hedgehog(BaseRole):
    def __init__(self):
        super().__init__("hedgehog", "villager", "🦔")
    
    def get_description(self) -> str:
        return "Spiny and dangerous. If attacked at night, both hedgehog and attacker die."
    
    def get_win_condition(self) -> str:
        return "Eliminate all Predators and hostile Neutrals, and survive."
    
    def on_attacked(self, attacker_id: int, game_data: Dict) -> Dict:
        game_data["mutual_destruction"] = attacker_id
        return game_data

class Herbivore(BaseRole):
    def __init__(self, animal_type: str, emoji: str):
        super().__init__(animal_type, "villager", emoji)
        self.role_data = {"stream_visits": 0}
    
    def get_description(self) -> str:
        return f"Grazer and cautious. Can visit locations each night to witness events. Cannot visit South Stream twice."
    
    def get_win_condition(self) -> str:
        return "Eliminate all Predators and hostile Neutrals, and survive."
    
    def has_night_action(self) -> bool:
        return True
    
    def get_night_action_message(self, player_name: str) -> str:
        return f"{self.emoji} {player_name}, where would you like to graze tonight?"
    
    def get_night_action_keyboard(self, game_id: str) -> Optional[InlineKeyboardMarkup]:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("North Hill", callback_data=f"night_action_{game_id}_visit_north")],
            [InlineKeyboardButton("South Stream", callback_data=f"night_action_{game_id}_visit_south")],
            [InlineKeyboardButton("East Cave", callback_data=f"night_action_{game_id}_visit_east")],
            [InlineKeyboardButton("West Lake", callback_data=f"night_action_{game_id}_visit_west")]
        ])

class Deer(Herbivore):
    def __init__(self):
        super().__init__("deer", "🦌")

class Giraffe(Herbivore):
    def __init__(self):
        super().__init__("giraffe", "🦒")

class Buffalo(Herbivore):
    def __init__(self):
        super().__init__("buffalo", "🐃")

class Cow(Herbivore):
    def __init__(self):
        super().__init__("cow", "🐄")

class Sheep(Herbivore):
    def __init__(self):
        super().__init__("sheep", "🐑")

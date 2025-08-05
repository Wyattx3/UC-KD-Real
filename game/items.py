import random
from typing import Dict, List, Optional
from config import ITEM_PROBABILITIES

class ItemSystem:
    def __init__(self):
        self.items = {
            "immortality_pill": {
                "name": "Immortality Pill",
                "emoji": "💊",
                "myanmar": "မသေဆေးဓာတ်လုံး",
                "description": "Survive one lethal attack during the night",
                "type": "defensive"
            },
            "reflection_mirror": {
                "name": "Reflection Mirror",
                "emoji": "🪞",
                "myanmar": "တန်ပြန်မှော်မှန်",
                "description": "Reflect harmful night actions back to attacker",
                "type": "defensive"
            },
            "sigma_banana": {
                "name": "Sigma Banana",
                "emoji": "🍌",
                "myanmar": "ငှက်ပျောသီး",
                "description": "Immunity to Monkey's role-blocking ability",
                "type": "passive"
            },
            "hecking_mask": {
                "name": "Hecking Mask",
                "emoji": "🎭",
                "myanmar": "ငတက်ပြား",
                "description": "Use another player's night ability instead of your own",
                "type": "active"
            },
            "mystic_eyes_amulet": {
                "name": "Mystic Eyes Amulet",
                "emoji": "🪬",
                "myanmar": "ပဥ္စလက်မျက်လုံး",
                "description": "Appear as innocent villager to investigations",
                "type": "passive"
            },
            "transformation_wand": {
                "name": "Transformation Wand",
                "emoji": "🪄",
                "myanmar": "အသွင်းပြောင်းတောင်ဝှေ့",
                "description": "Swap roles with target for one night",
                "type": "active"
            },
            "magic_gold_pot": {
                "name": "Magic Gold Pot (x2)",
                "emoji": "🏺",
                "myanmar": "မှော်ဝင်ရွှေအိုး",
                "description": "Double rewards if your team wins",
                "type": "passive"
            }
        }
    
    def perform_lucky_draw(self) -> str:
        items_list = []
        for item, probability in ITEM_PROBABILITIES.items():
            items_list.extend([item] * probability)
        
        return random.choice(items_list)
    
    def get_item_info(self, item_id: str) -> Optional[Dict]:
        if item_id.endswith("_bricks"):
            amount = item_id.split("_")[0]
            return {
                "name": f"{amount} Bricks",
                "emoji": "🧱",
                "description": f"Receive {amount} bricks",
                "type": "currency"
            }
        
        return self.items.get(item_id)
    
    def apply_item_effect(self, item_id: str, player_id: int, game_data: Dict) -> Dict:
        if item_id == "immortality_pill":
            game_data.setdefault("protected_players", set()).add(player_id)
        elif item_id == "reflection_mirror":
            game_data.setdefault("reflection_active", set()).add(player_id)
        elif item_id == "sigma_banana":
            game_data.setdefault("monkey_immune", set()).add(player_id)
        elif item_id == "mystic_eyes_amulet":
            game_data.setdefault("investigation_immune", set()).add(player_id)
        elif item_id == "magic_gold_pot":
            game_data.setdefault("double_rewards", set()).add(player_id)
        
        return game_data
    
    def get_lucky_draw_message(self, item_id: str) -> str:
        if item_id.endswith("_bricks"):
            amount = item_id.split("_")[0]
            return f"🎉 Congratulations! You won {amount} Bricks! 🧱"
        
        item_info = self.get_item_info(item_id)
        if item_info:
            return f"🎉 Congratulations! You won: {item_info['emoji']} {item_info['name']}!\n\n{item_info['description']}"
        
        return "🎉 Congratulations! You won a mysterious item!"
    
    def can_use_item_in_phase(self, item_id: str, phase: str) -> bool:
        if phase == "night":
            return item_id in ["hecking_mask", "transformation_wand"]
        return False
    
    def get_item_usage_keyboard(self, item_id: str, game_id: str):
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        if item_id == "hecking_mask":
            return InlineKeyboardMarkup([[
                InlineKeyboardButton("Use Hecking Mask", callback_data=f"use_item_{game_id}_{item_id}")
            ]])
        elif item_id == "transformation_wand":
            return InlineKeyboardMarkup([[
                InlineKeyboardButton("Use Transformation Wand", callback_data=f"use_item_{game_id}_{item_id}")
            ]])
        
        return None

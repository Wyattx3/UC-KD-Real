import asyncio
import json
from typing import Dict, List, Optional, Tuple
from telegram import Bot
from database.db_manager import DatabaseManager
from roles.role_factory import RoleFactory
from utils.messages import GameMessages

class PhaseManager:
    def __init__(self, game_id: str, db_manager: DatabaseManager, bot: Bot):
        self.game_id = game_id
        self.db = db_manager
        self.bot = bot
        self.role_factory = RoleFactory()
        self.messages = GameMessages()
        self.night_actions: Dict[int, str] = {}
    
    async def handle_night_phase(self):
        game = await self.db.get_game(self.game_id)
        if not game:
            return
        
        players = game.get_players_list()
        eliminated = game.get_eliminated_players()
        roles = game.get_roles_dict()
        
        alive_players = [p for p in players if p not in eliminated]
        
        for player_id in alive_players:
            role_name = roles.get(player_id)
            if role_name:
                role_instance = self.role_factory.create_role(role_name)
                if role_instance and role_instance.has_night_action():
                    await self._send_night_action_prompt(player_id, role_instance)
        
        await asyncio.sleep(60)
    
    async def _send_night_action_prompt(self, player_id: int, role_instance):
        try:
            user = await self.db.get_user(player_id)
            if user:
                message = role_instance.get_night_action_message(user.ign)
                keyboard = role_instance.get_night_action_keyboard(self.game_id)
                
                await self.bot.send_message(
                    chat_id=player_id,
                    text=message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
        except Exception as e:
            print(f"Failed to send night action prompt to {player_id}: {e}")
    
    async def handle_night_action(self, player_id: int, action: str, target_id: Optional[int] = None):
        game = await self.db.get_game(self.game_id)
        if not game or game.current_phase != "night":
            return False
        
        players = game.get_players_list()
        eliminated = game.get_eliminated_players()
        
        if player_id not in players or player_id in eliminated:
            return False
        
        action_data = {"action": action, "target": target_id}
        self.night_actions[player_id] = json.dumps(action_data)
        
        night_actions = game.get_night_actions()
        night_actions[str(player_id)] = action_data
        game.night_actions = json.dumps(night_actions)
        await self.db.update_game(game)
        
        return True
    
    async def resolve_night_actions(self) -> List[Tuple[int, str, str]]:
        game = await self.db.get_game(self.game_id)
        if not game:
            return []
        
        night_actions = game.get_night_actions()
        roles = game.get_roles_dict()
        deaths = []
        
        protected_players = set()
        kills = []
        
        for player_id_str, action_data in night_actions.items():
            player_id = int(player_id_str)
            role_name = roles.get(player_id)
            
            if not role_name:
                continue
            
            role_instance = self.role_factory.create_role(role_name)
            if not role_instance:
                continue
            
            action = action_data.get("action")
            target_id = action_data.get("target")
            
            if action == "protect" and target_id:
                protected_players.add(target_id)
            elif action == "kill" and target_id:
                kills.append((player_id, target_id, role_name))
        
        for killer_id, target_id, killer_role in kills:
            if target_id not in protected_players:
                target_role = roles.get(target_id, "unknown")
                user = await self.db.get_user(target_id)
                target_name = user.ign if user else "Unknown"
                
                deaths.append((target_id, target_name, target_role))
                
                eliminated = game.get_eliminated_players()
                eliminated.append(target_id)
                game.eliminated_players = json.dumps(eliminated)
        
        game.night_actions = ""
        await self.db.update_game(game)
        self.night_actions.clear()
        
        return deaths
    
    def get_night_action(self, player_id: int) -> Optional[Dict]:
        action_str = self.night_actions.get(player_id)
        if action_str:
            return json.loads(action_str)
        return None
    
    def has_submitted_action(self, player_id: int) -> bool:
        return player_id in self.night_actions

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.appwrite_manager import AppwriteManager
from game.game_manager import GameManager
from game.phase_manager import PhaseManager
from utils.messages import GameMessages

class GamePlayHandler:
    def __init__(self, db_manager: AppwriteManager, game_manager: GameManager):
        self.db = db_manager
        self.game_manager = game_manager
        self.messages = GameMessages()
    
    async def night_action_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        callback_data = query.data
        
        parts = callback_data.split("_")
        if len(parts) < 4:
            return
        
        game_id = parts[2]
        action = parts[3]
        
        game = await self.db.get_game(game_id)
        if not game or game.current_phase != "night":
            await query.edit_message_text("❌ Night phase is not active.")
            return
        
        players = game.get_players_list()
        eliminated = game.get_eliminated_players()
        
        if user_id not in players or user_id in eliminated:
            await query.edit_message_text("❌ You cannot perform actions.")
            return
        
        if action in ["kill", "protect", "investigate", "roleblock", "ambush"]:
            await self._handle_target_selection(query, game_id, action, user_id)
        elif action.startswith("visit_") or action.startswith("rampage_"):
            location = action.split("_")[1]
            phase_manager = self.game_manager.phase_managers.get(game_id)
            if phase_manager:
                success = await phase_manager.handle_night_action(user_id, action, None)
                if success:
                    await query.edit_message_text(
                        f"✅ You have chosen to go to the {location.title()}."
                    )
                else:
                    await query.edit_message_text("❌ Action failed.")
        elif action == "command_vulture":
            phase_manager = self.game_manager.phase_managers.get(game_id)
            if phase_manager:
                success = await phase_manager.handle_night_action(user_id, action, None)
                if success:
                    await query.edit_message_text("✅ Vulture has been commanded.")
                else:
                    await query.edit_message_text("❌ Action failed.")
    
    async def _handle_target_selection(self, query, game_id: str, action: str, user_id: int):
        game = await self.db.get_game(game_id)
        if not game:
            return
        
        players = game.get_players_list()
        eliminated = game.get_eliminated_players()
        alive_players = [p for p in players if p not in eliminated and p != user_id]
        
        keyboard = []
        for player_id in alive_players:
            user = await self.db.get_user(player_id)
            if user:
                button = InlineKeyboardButton(
                    user.ign,
                    callback_data=f"target_{game_id}_{action}_{player_id}"
                )
                keyboard.append([button])
        
        keyboard.append([InlineKeyboardButton("Cancel", callback_data=f"cancel_{game_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        action_text = {
            "kill": "eliminate",
            "protect": "protect",
            "investigate": "investigate",
            "roleblock": "chat with",
            "ambush": "ambush"
        }
        
        await query.edit_message_text(
            f"Choose who to {action_text.get(action, 'target')}:",
            reply_markup=reply_markup
        )
    
    async def target_selection_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        parts = callback_data.split("_")
        
        if len(parts) < 4:
            return
        
        game_id = parts[1]
        action = parts[2]
        target_id = int(parts[3])
        user_id = query.from_user.id
        
        phase_manager = self.game_manager.phase_managers.get(game_id)
        if phase_manager:
            success = await phase_manager.handle_night_action(user_id, action, target_id)
            
            if success:
                target_user = await self.db.get_user(target_id)
                target_name = target_user.ign if target_user else "Unknown"
                
                action_messages = {
                    "kill": f"✅ You have chosen to eliminate {target_name}.",
                    "protect": f"✅ You are protecting {target_name} tonight.",
                    "investigate": f"✅ You are investigating {target_name}.",
                    "roleblock": f"✅ You will chat with {target_name} tonight.",
                    "ambush": f"✅ You are preparing to ambush {target_name}."
                }
                
                message = action_messages.get(action, f"✅ Action performed on {target_name}.")
                await query.edit_message_text(message)
            else:
                await query.edit_message_text("❌ Action failed.")
    
    async def vote_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        parts = callback_data.split("_")
        
        if len(parts) < 3:
            return
        
        game_id = parts[1]
        target_id = int(parts[2])
        voter_id = query.from_user.id
        
        voting_system = self.game_manager.voting_systems.get(game_id)
        if voting_system:
            success = await voting_system.cast_vote(voter_id, target_id)
            
            if success:
                target_user = await self.db.get_user(target_id)
                target_name = target_user.ign if target_user else "Unknown"
                
                await query.answer(f"✅ You voted for {target_name}!", show_alert=True)
            else:
                await query.answer("❌ Vote failed!", show_alert=True)
    
    async def cancel_action_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text("❌ Action cancelled.")
    
    async def item_usage_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        parts = callback_data.split("_")
        
        if len(parts) < 4:
            return
        
        game_id = parts[2]
        item_id = parts[3]
        user_id = query.from_user.id
        
        game = await self.db.get_game(game_id)
        if not game:
            await query.edit_message_text("❌ Game not found.")
            return
        
        user = await self.db.get_user(user_id)
        if not user:
            return
        
        items = user.get_items_list()
        if item_id not in items:
            await query.edit_message_text("❌ You don't have this item.")
            return
        
        if item_id in ["hecking_mask", "transformation_wand"]:
            await self._handle_item_target_selection(query, game_id, item_id, user_id)
        else:
            await query.edit_message_text(f"✅ {item_id.replace('_', ' ').title()} activated!")
    
    async def _handle_item_target_selection(self, query, game_id: str, item_id: str, user_id: int):
        game = await self.db.get_game(game_id)
        if not game:
            return
        
        players = game.get_players_list()
        eliminated = game.get_eliminated_players()
        alive_players = [p for p in players if p not in eliminated and p != user_id]
        
        keyboard = []
        for player_id in alive_players:
            user = await self.db.get_user(player_id)
            if user:
                button = InlineKeyboardButton(
                    user.ign,
                    callback_data=f"item_target_{game_id}_{item_id}_{player_id}"
                )
                keyboard.append([button])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        item_names = {
            "hecking_mask": "Hecking Mask",
            "transformation_wand": "Transformation Wand"
        }
        
        await query.edit_message_text(
            f"Choose target for {item_names.get(item_id, 'item')}:",
            reply_markup=reply_markup
        )
    
    async def item_target_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        parts = callback_data.split("_")
        
        if len(parts) < 4:
            return
        
        game_id = parts[2]
        item_id = parts[3]
        target_id = int(parts[4])
        
        target_user = await self.db.get_user(target_id)
        target_name = target_user.ign if target_user else "Unknown"
        
        item_names = {
            "hecking_mask": "Hecking Mask",
            "transformation_wand": "Transformation Wand"
        }
        
        await query.edit_message_text(
            f"✅ {item_names.get(item_id, 'Item')} used on {target_name}!"
        )

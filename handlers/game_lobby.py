import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DatabaseManager
from game.game_manager import GameManager
from utils.messages import GameMessages
import config

class GameLobbyHandler:
    def __init__(self, db_manager: DatabaseManager, game_manager: GameManager):
        self.db = db_manager
        self.game_manager = game_manager
        self.messages = GameMessages()
        self.lobby_timers = {}
    
    async def create_game_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type == 'private':
            await update.message.reply_text(
                "❌ Games can only be created in group chats!"
            )
            return
        
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        user = await self.db.get_user(user_id)
        if not user:
            await update.message.reply_text(
                f"❌ Please register with me first! Click here: https://t.me/{config.BOT_USERNAME}?start=register"
            )
            return
        
        try:
            game_id = await self.game_manager.create_game(chat_id, user_id)
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("Join Game 🎮", callback_data=f"join_game_{game_id}")
            ]])
            
            message = (
                "🎮 <b>A new game of UC Kingdom is starting!</b>\n\n"
                f"🎯 Game ID: <code>{game_id}</code>\n"
                f"👑 Host: {user.ign}\n"
                f"👥 Players: 1/{config.MAX_PLAYERS}\n"
                f"⏰ Join within 90 seconds!\n\n"
                "Registered players, click the button below to enter!"
            )
            
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            self.lobby_timers[game_id] = asyncio.create_task(
                self._lobby_timeout(chat_id, game_id)
            )
            
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
        except Exception as e:
            await update.message.reply_text("❌ Failed to create game. Please try again.")
    
    async def join_game_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        game_id = query.data.split("_")[-1]
        
        user = await self.db.get_user(user_id)
        if not user:
            await query.answer(
                f"Please register with me first! Click here: https://t.me/{config.BOT_USERNAME}?start=register",
                show_alert=True
            )
            return
        
        success = await self.game_manager.join_game(game_id, user_id)
        
        if success:
            game = await self.db.get_game(game_id)
            if game:
                players = game.get_players_list()
                player_count = len(players)
                
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("Join Game 🎮", callback_data=f"join_game_{game_id}")
                ]])
                
                message = (
                    "🎮 <b>A new game of UC Kingdom is starting!</b>\n\n"
                    f"🎯 Game ID: <code>{game_id}</code>\n"
                    f"👥 Players: {player_count}/{config.MAX_PLAYERS}\n"
                    f"⏰ Join within 90 seconds!\n\n"
                    "Registered players, click the button below to enter!"
                )
                
                await query.edit_message_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                if player_count >= config.MIN_PLAYERS:
                    await asyncio.sleep(2)
                    await self._try_start_game(game_id, query.message.chat_id)
        else:
            await query.answer("❌ Failed to join game!", show_alert=True)
    
    async def _lobby_timeout(self, chat_id: int, game_id: str):
        await asyncio.sleep(90)
        
        game = await self.db.get_game(game_id)
        if game and game.status == "lobby":
            players = game.get_players_list()
            
            if len(players) >= config.MIN_PLAYERS:
                await self._try_start_game(game_id, chat_id)
            else:
                from telegram.ext import Application
                bot = Application.get_running().bot
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ Game {game_id} cancelled - not enough players ({len(players)}/{config.MIN_PLAYERS})"
                )
        
        if game_id in self.lobby_timers:
            del self.lobby_timers[game_id]
    
    async def _try_start_game(self, game_id: str, chat_id: int):
        try:
            success = await self.game_manager.start_game(game_id)
            
            if success:
                from telegram.ext import Application
                bot = Application.get_running().bot
                await bot.send_message(
                    chat_id=chat_id,
                    text="🎮 <b>Game is starting!</b> Roles are being assigned... Check your PMs!",
                    parse_mode='HTML'
                )
                
                if game_id in self.lobby_timers:
                    self.lobby_timers[game_id].cancel()
                    del self.lobby_timers[game_id]
            else:
                from telegram.ext import Application
                bot = Application.get_running().bot
                await bot.send_message(
                    chat_id=chat_id,
                    text="❌ Failed to start game. Please try again."
                )
        except Exception as e:
            from telegram.ext import Application
            bot = Application.get_running().bot
            await bot.send_message(
                chat_id=chat_id,
                text="❌ Error starting game. Please try again."
            )
    
    async def force_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ This command only works in group chats!")
            return
        
        chat_id = update.effective_chat.id
        game = await self.db.get_active_game_by_chat(chat_id)
        
        if not game:
            await update.message.reply_text("❌ No active game found in this chat.")
            return
        
        if game.creator_id != update.effective_user.id:
            await update.message.reply_text("❌ Only the game creator can force start.")
            return
        
        players = game.get_players_list()
        if len(players) < config.MIN_PLAYERS:
            await update.message.reply_text(
                f"❌ Need at least {config.MIN_PLAYERS} players to start. Current: {len(players)}"
            )
            return
        
        await self._try_start_game(game.game_id, chat_id)
    
    async def game_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ This command only works in group chats!")
            return
        
        chat_id = update.effective_chat.id
        game = await self.db.get_active_game_by_chat(chat_id)
        
        if not game:
            await update.message.reply_text("❌ No active game found in this chat.")
            return
        
        status = self.game_manager.get_game_status(game.game_id)
        if status:
            message = (
                f"🎮 <b>Game Status</b>\n\n"
                f"🎯 Game ID: <code>{status['game_id']}</code>\n"
                f"📊 Status: {status['status'].title()}\n"
                f"🌙 Phase: {status['phase'].title()}\n"
                f"🔄 Round: {status['round']}\n"
                f"👥 Players: {status['players']}"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text("❌ Could not retrieve game status.")

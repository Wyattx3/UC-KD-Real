import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.appwrite_manager import AppwriteManager
from utils.messages import UserMessages
from utils.keyboards import UserKeyboards
import config

WAITING_FOR_IGN = 1

class EnhancedRegistrationHandler:
    def __init__(self, db_manager: AppwriteManager):
        self.db = db_manager
        self.messages = UserMessages()
        self.keyboards = UserKeyboards()
        self.countdown_tasks = {}  # Store active countdown tasks
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = await self.db.get_user(user_id)
        
        if user:
            await self._show_main_menu(update, user)
        else:
            await self._show_registration_prompt(update)
    
    async def _show_registration_prompt(self, update: Update):
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("Register 📝", callback_data="register")
        ]])
        
        await update.message.reply_text(
            self.messages.get_welcome_message(),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def _show_main_menu(self, update: Update, user):
        keyboard = self.keyboards.get_main_menu_keyboard()
        
        await update.message.reply_text(
            self.messages.get_main_menu_message(user.ign),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def register_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "Please enter your desired In-Game Name (IGN):",
            parse_mode='HTML'
        )
        
        return WAITING_FOR_IGN
    
    async def handle_ign_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        ign = update.message.text.strip()
        
        if len(ign) < 2 or len(ign) > 20:
            await update.message.reply_text(
                "❌ IGN must be between 2 and 20 characters. Please try again:"
            )
            return WAITING_FOR_IGN
        
        try:
            user = await self.db.create_user(user_id, ign)
            await update.message.reply_text(
                f"✅ Registration successful! Welcome, {ign}!",
                parse_mode='HTML'
            )
            
            await self._show_main_menu(update, user)
            return ConversationHandler.END
            
        except Exception as e:
            await update.message.reply_text(
                "❌ Registration failed. Please try again later."
            )
            return ConversationHandler.END
    
    async def my_info_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user = await self.db.get_user(user_id)
        
        if not user:
            await query.edit_message_text("❌ User not found. Please register first.")
            return
        
        info_message = self.messages.get_user_info_message(user)
        keyboard = self.keyboards.get_user_info_keyboard()
        
        await query.edit_message_text(
            info_message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def change_ign_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        cooldown_info = await self.db.get_ign_change_cooldown(user_id)
        
        if not cooldown_info['can_change']:
            await self._start_countdown_display(query, user_id, cooldown_info)
            return
        
        await query.edit_message_text(
            "✅ <b>IGN Change Available!</b>\n\n"
            "You can now change your IGN. Click the button below to proceed.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✏️ Change IGN", callback_data="start_ign_change")
            ]]),
            parse_mode='HTML'
        )
    
    async def _start_countdown_display(self, query, user_id: int, initial_cooldown: dict):
        """Start real-time countdown display for IGN change cooldown"""
        message_id = query.message.message_id
        chat_id = query.message.chat_id
        
        if user_id in self.countdown_tasks:
            self.countdown_tasks[user_id].cancel()
        
        async def countdown_loop():
            try:
                remaining_seconds = initial_cooldown['remaining_seconds']
                
                while remaining_seconds > 0:
                    hours = remaining_seconds // 3600
                    minutes = (remaining_seconds % 3600) // 60
                    seconds = remaining_seconds % 60
                    
                    if hours > 0:
                        time_display = f"{hours}h {minutes}m {seconds}s"
                    elif minutes > 0:
                        time_display = f"{minutes}m {seconds}s"
                    else:
                        time_display = f"{seconds}s"
                    
                    message = (
                        f"⏰ <b>IGN Change Cooldown</b>\n\n"
                        f"You can change your IGN again in:\n"
                        f"🕐 <code>{time_display}</code>\n\n"
                        f"<i>This countdown updates every second...</i>"
                    )
                    
                    keyboard = InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄 Refresh", callback_data="refresh_cooldown"),
                        InlineKeyboardButton("❌ Cancel", callback_data="cancel_cooldown")
                    ]])
                    
                    try:
                        await query.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=message,
                            reply_markup=keyboard,
                            parse_mode='HTML'
                        )
                    except:
                        pass
                    
                    await asyncio.sleep(1)
                    remaining_seconds -= 1
                
                final_message = (
                    "✅ <b>IGN Change Available!</b>\n\n"
                    "You can now change your IGN. Click the button below to proceed."
                )
                
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("✏️ Change IGN", callback_data="start_ign_change")
                ]])
                
                await query.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=final_message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Countdown error: {e}")
            finally:
                if user_id in self.countdown_tasks:
                    del self.countdown_tasks[user_id]
        
        task = asyncio.create_task(countdown_loop())
        self.countdown_tasks[user_id] = task
    
    async def refresh_cooldown_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Refresh cooldown display"""
        query = update.callback_query
        await query.answer("🔄 Refreshing countdown...")
        
        user_id = query.from_user.id
        cooldown_info = await self.db.get_ign_change_cooldown(user_id)
        
        if cooldown_info['can_change']:
            await query.edit_message_text(
                "✅ <b>IGN Change Available!</b>\n\n"
                "You can now change your IGN. Click the button below to proceed.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✏️ Change IGN", callback_data="start_ign_change")
                ]]),
                parse_mode='HTML'
            )
        else:
            await self._start_countdown_display(query, user_id, cooldown_info)
    
    async def cancel_cooldown_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel cooldown display"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if user_id in self.countdown_tasks:
            self.countdown_tasks[user_id].cancel()
            del self.countdown_tasks[user_id]
        
        await query.edit_message_text(
            "❌ IGN change cancelled. You can try again later.",
            parse_mode='HTML'
        )
    
    async def handle_ign_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        new_ign = update.message.text.strip()
        
        if len(new_ign) < 2 or len(new_ign) > 20:
            await update.message.reply_text(
                "❌ IGN must be between 2 and 20 characters. Please try again:"
            )
            return WAITING_FOR_IGN
        
        try:
            await self.db.update_user_ign(user_id, new_ign)
            await update.message.reply_text(
                f"✅ IGN successfully changed to: {new_ign}"
            )
            
            user = await self.db.get_user(user_id)
            await self._show_main_menu(update, user)
            
            context.user_data.pop('changing_ign', None)
            return ConversationHandler.END
            
        except Exception as e:
            await update.message.reply_text(
                "❌ Failed to change IGN. Please try again later."
            )
            return ConversationHandler.END
    
    async def add_to_group_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        message = (
            "🤖 <b>Add UC Kingdom Bot to Your Group</b>\n\n"
            "Click the link below to add me to your group chat:\n"
            f"👉 https://t.me/{config.BOT_USERNAME}?startgroup=true\n\n"
            "Once added, use /creategame to start a new game!"
        )
        
        await query.edit_message_text(message, parse_mode='HTML')
    
    async def join_uc_era_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        message = (
            "🌌 <b>Join UC Era</b>\n\n"
            "Coming Soon! UC Kingdom is proud to be part of the future UC Era ecosystem.\n\n"
            "Stay tuned for more exciting features and games!"
        )
        
        await query.edit_message_text(message, parse_mode='HTML')
    
    async def cancel_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    def cleanup_countdown_tasks(self):
        """Clean up all active countdown tasks"""
        for task in self.countdown_tasks.values():
            task.cancel()
        self.countdown_tasks.clear()

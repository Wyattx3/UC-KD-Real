from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.appwrite_manager import AppwriteManager
from utils.messages import UserMessages
from utils.keyboards import UserKeyboards
import config

WAITING_FOR_IGN = 1

class RegistrationHandler:
    def __init__(self, db_manager: AppwriteManager):
        self.db = db_manager
        self.messages = UserMessages()
        self.keyboards = UserKeyboards()
    
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
        user = await self.db.get_user(user_id)
        
        if not user:
            await query.edit_message_text("❌ User not found.")
            return
        
        if user.last_ign_change:
            last_change = datetime.fromisoformat(user.last_ign_change)
            next_allowed = last_change + timedelta(hours=72)
            
            if datetime.now() < next_allowed:
                remaining = next_allowed - datetime.now()
                hours_left = int(remaining.total_seconds() // 3600)
                
                await query.edit_message_text(
                    f"❌ You can change your IGN again in {hours_left} hours."
                )
                return
        
        await query.edit_message_text(
            "Please enter your new In-Game Name (IGN):"
        )
        
        context.user_data['changing_ign'] = True
        return WAITING_FOR_IGN
    
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

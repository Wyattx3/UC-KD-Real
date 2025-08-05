import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DatabaseManager
from game.items import ItemSystem
from utils.messages import ItemMessages
import config

class ItemHandler:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.item_system = ItemSystem()
        self.messages = ItemMessages()
    
    async def lucky_draw_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user = await self.db.get_user(user_id)
        
        if not user:
            await query.edit_message_text("❌ User not found.")
            return
        
        if user.bricks < config.LUCKY_DRAW_COST:
            await query.edit_message_text(
                f"❌ Insufficient bricks! You need {config.LUCKY_DRAW_COST} bricks.\n"
                f"You currently have {user.bricks} bricks."
            )
            return
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Confirm Draw (1000 🧱)", callback_data="confirm_lucky_draw")],
            [InlineKeyboardButton("Cancel", callback_data="back_to_main")]
        ])
        
        await query.edit_message_text(
            self.messages.get_lucky_draw_confirmation(),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def confirm_lucky_draw_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user = await self.db.get_user(user_id)
        
        if not user or user.bricks < config.LUCKY_DRAW_COST:
            await query.edit_message_text("❌ Insufficient bricks!")
            return
        
        await query.edit_message_text(
            "🎰 Drawing... ✨",
            parse_mode='HTML'
        )
        
        await asyncio.sleep(3)
        
        item_won = self.item_system.perform_lucky_draw()
        
        new_bricks = user.bricks - config.LUCKY_DRAW_COST
        
        if item_won.endswith("_bricks"):
            brick_amount = int(item_won.split("_")[0])
            new_bricks += brick_amount
            
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as db:
                await db.execute(
                    "UPDATE users SET bricks = ? WHERE telegram_id = ?",
                    (new_bricks, user_id)
                )
                await db.commit()
        else:
            user.add_item(item_won)
            
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as db:
                await db.execute(
                    "UPDATE users SET bricks = ?, items = ? WHERE telegram_id = ?",
                    (new_bricks, user.items, user_id)
                )
                await db.commit()
        
        result_message = self.item_system.get_lucky_draw_message(item_won)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Draw Again", callback_data="lucky_draw")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_to_main")]
        ])
        
        await query.edit_message_text(
            result_message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def show_inventory_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user = await self.db.get_user(user_id)
        
        if not user:
            await query.edit_message_text("❌ User not found.")
            return
        
        items = user.get_items_list()
        
        if not items:
            message = "📦 <b>Your Inventory</b>\n\nYour inventory is empty. Try the Lucky Draw to get items!"
        else:
            message = "📦 <b>Your Inventory</b>\n\n"
            
            item_counts = {}
            for item in items:
                item_counts[item] = item_counts.get(item, 0) + 1
            
            for item_id, count in item_counts.items():
                item_info = self.item_system.get_item_info(item_id)
                if item_info:
                    name = item_info['name']
                    emoji = item_info['emoji']
                    description = item_info['description']
                    
                    if count > 1:
                        message += f"{emoji} <b>{name}</b> x{count}\n{description}\n\n"
                    else:
                        message += f"{emoji} <b>{name}</b>\n{description}\n\n"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Back", callback_data="my_info")]
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def item_selection_prompt(self, user_id: int, game_id: str, bot):
        user = await self.db.get_user(user_id)
        if not user:
            return
        
        items = user.get_items_list()
        if not items:
            await bot.send_message(
                chat_id=user_id,
                text="You have no items to use in this game.",
                parse_mode='HTML'
            )
            return
        
        keyboard = []
        unique_items = list(set(items))
        
        for item_id in unique_items:
            item_info = self.item_system.get_item_info(item_id)
            if item_info:
                button = InlineKeyboardButton(
                    f"{item_info['emoji']} {item_info['name']}",
                    callback_data=f"equip_item_{game_id}_{item_id}"
                )
                keyboard.append([button])
        
        keyboard.append([InlineKeyboardButton("No Item", callback_data=f"equip_item_{game_id}_none")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "🎒 <b>Item Selection</b>\n\n"
            "The first night is upon you. Do you wish to use an item from your inventory for this game?\n\n"
            "⚠️ <i>Items are consumed after the game ends, regardless of whether their effect was triggered.</i>"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def equip_item_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        parts = callback_data.split("_")
        
        if len(parts) < 4:
            return
        
        game_id = parts[2]
        item_id = parts[3]
        user_id = query.from_user.id
        
        if item_id == "none":
            await query.edit_message_text(
                "✅ No item equipped for this game."
            )
            return
        
        user = await self.db.get_user(user_id)
        if not user:
            return
        
        items = user.get_items_list()
        if item_id not in items:
            await query.edit_message_text("❌ You don't have this item.")
            return
        
        item_info = self.item_system.get_item_info(item_id)
        if item_info:
            await query.edit_message_text(
                f"✅ {item_info['emoji']} {item_info['name']} equipped for this game!\n\n"
                f"{item_info['description']}"
            )
        else:
            await query.edit_message_text("✅ Item equipped!")
    
    async def back_to_main_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user = await self.db.get_user(user_id)
        
        if user:
            from handlers.registration import RegistrationHandler
            handler = RegistrationHandler(self.db)
            await handler._show_main_menu(query, user)

import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ConversationHandler, filters
)

from database.appwrite_manager import AppwriteManager
from game.game_manager import GameManager
from handlers.enhanced_registration import EnhancedRegistrationHandler, WAITING_FOR_IGN
from handlers.game_lobby import GameLobbyHandler
from handlers.game_play import GamePlayHandler
from handlers.items import ItemHandler
import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UCKingdomBot:
    def __init__(self):
        self.db_manager = AppwriteManager(config.APPWRITE_API_KEY)
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        self.game_manager = None
        
        self.registration_handler = EnhancedRegistrationHandler(self.db_manager)
        self.item_handler = ItemHandler(self.db_manager)
        self.game_lobby_handler = None
        self.game_play_handler = None
    
    async def initialize(self):
        await self.db_manager.init_db()
        
        self.game_manager = GameManager(self.db_manager, self.application.bot)
        self.game_lobby_handler = GameLobbyHandler(self.db_manager, self.game_manager)
        self.game_play_handler = GamePlayHandler(self.db_manager, self.game_manager)
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        registration_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.registration_handler.register_callback, pattern="^register$"),
                CallbackQueryHandler(self.registration_handler.change_ign_callback, pattern="^change_ign$")
            ],
            states={
                WAITING_FOR_IGN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_ign_input)
                ]
            },
            fallbacks=[
                CommandHandler("cancel", self.registration_handler.cancel_conversation)
            ]
        )
        
        self.application.add_handler(CommandHandler("start", self.registration_handler.start_command))
        self.application.add_handler(registration_conv)
        
        self.application.add_handler(CallbackQueryHandler(
            self.registration_handler.my_info_callback, pattern="^my_info$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.registration_handler.add_to_group_callback, pattern="^add_to_group$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.registration_handler.join_uc_era_callback, pattern="^join_uc_era$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.registration_handler.refresh_cooldown_callback, pattern="^refresh_cooldown$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.registration_handler.cancel_cooldown_callback, pattern="^cancel_cooldown$"
        ))
        
        self.application.add_handler(CallbackQueryHandler(
            self.item_handler.lucky_draw_callback, pattern="^lucky_draw$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.item_handler.confirm_lucky_draw_callback, pattern="^confirm_lucky_draw$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.item_handler.show_inventory_callback, pattern="^show_inventory$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.item_handler.back_to_main_callback, pattern="^back_to_main$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.item_handler.equip_item_callback, pattern="^equip_item_"
        ))
        
        self.application.add_handler(CommandHandler("creategame", self.game_lobby_handler.create_game_command))
        self.application.add_handler(CommandHandler("forcestart", self.game_lobby_handler.force_start_command))
        self.application.add_handler(CommandHandler("status", self.game_lobby_handler.game_status_command))
        
        self.application.add_handler(CallbackQueryHandler(
            self.game_lobby_handler.join_game_callback, pattern="^join_game_"
        ))
        
        self.application.add_handler(CallbackQueryHandler(
            self.game_play_handler.night_action_callback, pattern="^night_action_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_play_handler.target_selection_callback, pattern="^target_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_play_handler.vote_callback, pattern="^vote_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_play_handler.cancel_action_callback, pattern="^cancel_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_play_handler.item_usage_callback, pattern="^use_item_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_play_handler.item_target_callback, pattern="^item_target_"
        ))
        
        self.application.add_error_handler(self._error_handler)
    
    async def _handle_ign_input(self, update: Update, context):
        if context.user_data.get('changing_ign'):
            return await self.registration_handler.handle_ign_change(update, context)
        else:
            return await self.registration_handler.handle_ign_input(update, context)
    
    async def _error_handler(self, update: Update, context):
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An error occurred. Please try again later."
                )
            except Exception:
                pass
    
    async def run(self):
        await self.initialize()
        
        logger.info("UC Kingdom Bot is starting...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

async def main():
    bot = UCKingdomBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())

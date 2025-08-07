#!/usr/bin/env python3
"""
Test script to verify the name change countdown display fix
"""
import asyncio
from datetime import datetime, timedelta
from database.appwrite_manager import AppwriteManager
from handlers.enhanced_registration import EnhancedRegistrationHandler
from telegram import Update, CallbackQuery, User, Message, Chat
from telegram.ext import ContextTypes
import config

class MockQuery:
    def __init__(self, user_id):
        self.from_user = User(id=user_id, first_name="Test", is_bot=False)
        self.data = "change_ign"
        self.message = Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            from_user=self.from_user
        )
    
    async def answer(self):
        pass
    
    async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
        print(f"📱 Message updated: {text}")
        if reply_markup:
            print(f"🔘 Buttons: {[btn.text for row in reply_markup.inline_keyboard for btn in row]}")

class MockContext:
    def __init__(self):
        self.user_data = {}

async def test_countdown_display_fix():
    print("🔧 Testing Name Change Countdown Display Fix...")
    
    db = AppwriteManager(config.APPWRITE_API_KEY)
    await db.init_db()
    
    test_user_id = 888888
    
    try:
        try:
            existing_user = await db.get_user(test_user_id)
            if existing_user:
                print("🧹 Cleaning up existing test user...")
        except:
            pass
        
        user = await db.create_user(test_user_id, "CountdownFixTestUser")
        print(f"✅ Created test user: {user.ign}")
        
        recent_change = datetime.now() - timedelta(hours=1)
        db.databases.update_document(
            database_id=db.database_id,
            collection_id=db.users_collection_id,
            document_id=str(test_user_id),
            data={'last_ign_change': recent_change.isoformat()}
        )
        print("✅ Set recent IGN change to trigger cooldown")
        
        cooldown_info = await db.get_ign_change_cooldown(test_user_id)
        print(f"📊 Cooldown info: can_change={cooldown_info['can_change']}, remaining={cooldown_info['remaining_seconds']}s")
        
        if cooldown_info['can_change']:
            print("❌ ERROR: User should be in cooldown")
            return False
        
        handler = EnhancedRegistrationHandler(db)
        mock_query = MockQuery(test_user_id)
        mock_context = MockContext()
        
        print("🔄 Testing change_ign_callback with cooldown...")
        await handler.change_ign_callback(
            Update(update_id=1, callback_query=mock_query),
            mock_context
        )
        
        print("✅ Countdown display test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_countdown_display_fix())
    if success:
        print("\n🎉 COUNTDOWN DISPLAY FIX VERIFIED!")
    else:
        print("\n❌ COUNTDOWN DISPLAY FIX FAILED!")

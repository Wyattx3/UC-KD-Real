#!/usr/bin/env python3
"""
Test script for Appwrite database migration and real-time countdown functionality
"""
import asyncio
import sys
sys.path.append('.')

from database.appwrite_manager import AppwriteManager
from handlers.enhanced_registration import EnhancedRegistrationHandler
import config

class AppwriteMigrationTest:
    def __init__(self):
        self.db_manager = AppwriteManager(config.APPWRITE_API_KEY)
    
    async def test_database_connection(self):
        """Test Appwrite database connection and initialization"""
        print("🔗 Testing Appwrite database connection...")
        
        try:
            await self.db_manager.init_db()
            print("✅ Appwrite database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def test_user_operations(self):
        """Test user creation, retrieval, and updates"""
        print("👤 Testing user operations...")
        
        try:
            test_user_id = 999999999
            test_ign = "TestUser"
            
            user = await self.db_manager.create_user(test_user_id, test_ign)
            print(f"✅ User created: {user.ign}")
            
            retrieved_user = await self.db_manager.get_user(test_user_id)
            if retrieved_user and retrieved_user.ign == test_ign:
                print("✅ User retrieval successful")
            else:
                print("❌ User retrieval failed")
                return False
            
            await self.db_manager.update_user_ign(test_user_id, "UpdatedTestUser")
            updated_user = await self.db_manager.get_user(test_user_id)
            if updated_user and updated_user.ign == "UpdatedTestUser":
                print("✅ User IGN update successful")
            else:
                print("❌ User IGN update failed")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ User operations test failed: {e}")
            return False
    
    async def test_cooldown_functionality(self):
        """Test IGN change cooldown functionality"""
        print("⏰ Testing cooldown functionality...")
        
        try:
            test_user_id = 999999998
            
            user = await self.db_manager.create_user(test_user_id, "CooldownTestUser")
            
            cooldown_info = await self.db_manager.get_ign_change_cooldown(test_user_id)
            if cooldown_info['can_change']:
                print("✅ New user can change IGN immediately")
            else:
                print("❌ New user cooldown check failed")
                return False
            
            await self.db_manager.update_user_ign(test_user_id, "UpdatedCooldownUser")
            
            cooldown_info = await self.db_manager.get_ign_change_cooldown(test_user_id)
            if not cooldown_info['can_change'] and cooldown_info['remaining_seconds'] > 0:
                print(f"✅ Cooldown active: {cooldown_info['remaining_seconds']} seconds remaining")
            else:
                print("❌ Cooldown not activated after IGN change")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Cooldown functionality test failed: {e}")
            return False
    
    async def test_game_operations(self):
        """Test game creation and retrieval"""
        print("🎮 Testing game operations...")
        
        try:
            test_game_id = "test_game_123"
            test_chat_id = -1001234567890
            test_creator_id = 999999997
            
            game = await self.db_manager.create_game(test_game_id, test_chat_id, test_creator_id)
            print(f"✅ Game created: {game.game_id}")
            
            retrieved_game = await self.db_manager.get_game(test_game_id)
            if retrieved_game and retrieved_game.game_id == test_game_id:
                print("✅ Game retrieval successful")
            else:
                print("❌ Game retrieval failed")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Game operations test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all Appwrite migration tests"""
        print("🚀 APPWRITE MIGRATION TEST SUITE")
        print("=" * 50)
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("User Operations", self.test_user_operations),
            ("Cooldown Functionality", self.test_cooldown_functionality),
            ("Game Operations", self.test_game_operations)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    print(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
                    failed += 1
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                failed += 1
            
            print("-" * 30)
        
        print(f"📊 TEST RESULTS: {passed}/{len(tests)} tests passed")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED - APPWRITE MIGRATION READY!")
            return True
        else:
            print(f"\n❌ {failed} TESTS FAILED - MIGRATION NEEDS FIXES")
            return False

async def main():
    test = AppwriteMigrationTest()
    success = await test.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

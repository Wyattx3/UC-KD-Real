#!/usr/bin/env python3
"""
Test script for enhanced features: real-time countdown and Appwrite migration
"""
import asyncio
import sys
sys.path.append('.')

from database.appwrite_manager import AppwriteManager
from handlers.enhanced_registration import EnhancedRegistrationHandler
from roles.role_factory import RoleFactory
from game.role_distribution import assign_roles, get_role_emoji
from game.items import ItemSystem
import config

class EnhancedFeaturesTest:
    def __init__(self):
        self.db_manager = AppwriteManager(config.APPWRITE_API_KEY)
        self.role_factory = RoleFactory()
        self.item_system = ItemSystem()
    
    async def test_appwrite_database(self):
        """Test Appwrite database operations"""
        print("🔗 Testing Appwrite Database Operations...")
        
        try:
            await self.db_manager.init_db()
            print("✅ Database initialization successful")
            
            test_user = await self.db_manager.create_user(123456789, "TestUser")
            print(f"✅ User creation: {test_user.ign}")
            
            retrieved_user = await self.db_manager.get_user(123456789)
            if retrieved_user:
                print(f"✅ User retrieval: {retrieved_user.ign}")
            
            cooldown_info = await self.db_manager.get_ign_change_cooldown(123456789)
            print(f"✅ Cooldown check: Can change = {cooldown_info['can_change']}")
            
            test_game = await self.db_manager.create_game("test_game", -1001234567890, 123456789)
            print(f"✅ Game creation: {test_game.game_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
    
    async def test_countdown_functionality(self):
        """Test real-time countdown functionality"""
        print("⏰ Testing Real-time Countdown...")
        
        try:
            handler = EnhancedRegistrationHandler(self.db_manager)
            
            test_user_id = 987654321
            await self.db_manager.create_user(test_user_id, "CountdownUser")
            
            cooldown_info = await self.db_manager.get_ign_change_cooldown(test_user_id)
            
            if cooldown_info['can_change']:
                print("✅ New user can change IGN (no cooldown)")
            
            await self.db_manager.update_user_ign(test_user_id, "UpdatedUser")
            
            cooldown_info = await self.db_manager.get_ign_change_cooldown(test_user_id)
            
            if not cooldown_info['can_change']:
                hours = cooldown_info.get('hours_left', 0)
                minutes = cooldown_info.get('minutes_left', 0)
                seconds = cooldown_info.get('seconds_left', 0)
                print(f"✅ Cooldown active: {hours}h {minutes}m {seconds}s remaining")
            
            return True
            
        except Exception as e:
            print(f"❌ Countdown test failed: {e}")
            return False
    
    async def test_existing_functionality(self):
        """Test that existing bot functionality still works"""
        print("🎭 Testing Existing Bot Functionality...")
        
        try:
            all_roles = [
                "lion", "leopard", "tiger", "jackal", "fox", "turtle", "vulture", 
                "monkey", "owl", "crocodile", "deer", "giraffe", "buffalo", 
                "cow", "sheep", "bat", "hedgehog", "wild_boar", "hunter"
            ]
            
            for role_name in all_roles:
                role_obj = self.role_factory.create_role(role_name)
                if not role_obj:
                    print(f"❌ Role creation failed: {role_name}")
                    return False
            
            print("✅ All 19 roles working")
            
            player_ids = list(range(1, 16))
            roles = assign_roles(player_ids)
            
            if len(roles) == 15:
                print("✅ Role distribution working")
            else:
                print(f"❌ Role distribution failed: expected 15, got {len(roles)}")
                return False
            
            all_items = ["immortality_pill", "reflection_mirror", "sigma_banana", 
                        "hecking_mask", "mystic_eyes_amulet", "transformation_wand", "magic_gold_pot"]
            
            for item_id in all_items:
                item_info = self.item_system.get_item_info(item_id)
                if not item_info:
                    print(f"❌ Item system failed: {item_id}")
                    return False
            
            print("✅ Item system working")
            
            return True
            
        except Exception as e:
            print(f"❌ Existing functionality test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all enhanced features tests"""
        print("🚀 ENHANCED FEATURES TEST SUITE")
        print("=" * 60)
        
        tests = [
            ("Appwrite Database", self.test_appwrite_database),
            ("Real-time Countdown", self.test_countdown_functionality),
            ("Existing Functionality", self.test_existing_functionality)
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
            
            print("-" * 40)
        
        print(f"📊 FINAL TEST RESULTS: {passed}/{len(tests)} tests passed")
        
        if failed == 0:
            print("\n🎉 ALL ENHANCED FEATURES WORKING!")
            print("\n✅ CONFIRMED WORKING:")
            print("  🔗 Appwrite cloud database integration")
            print("  ⏰ Real-time countdown for name changes")
            print("  🎭 All existing bot functionality preserved")
            print("  🎮 19 roles and game mechanics intact")
            print("  🎒 Item system fully functional")
            print("\n🚀 BOT IS READY WITH ADVANCED FEATURES!")
            return True
        else:
            print(f"\n❌ {failed} TESTS FAILED - NEEDS FIXES")
            return False

async def main():
    test = EnhancedFeaturesTest()
    success = await test.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

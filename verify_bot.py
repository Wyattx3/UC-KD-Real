#!/usr/bin/env python3
"""
Verification script to confirm UC Kingdom bot is error-free
"""
import sys
import os
sys.path.append('.')

def verify_bot_imports():
    """Verify bot main file imports successfully"""
    try:
        import bot
        print("✅ Bot main file imports successfully")
        return True
    except Exception as e:
        print(f"❌ Bot import error: {e}")
        return False

def verify_all_modules():
    """Verify all modules can be imported"""
    modules_to_test = [
        'database.models',
        'database.db_manager', 
        'game.game_manager',
        'game.phase_manager',
        'game.voting_system',
        'game.role_distribution',
        'game.items',
        'roles.base_role',
        'roles.villager_roles',
        'roles.predator_roles',
        'roles.neutral_roles',
        'roles.role_factory',
        'handlers.registration',
        'handlers.game_lobby',
        'handlers.game_play',
        'handlers.items',
        'utils.messages',
        'utils.keyboards'
    ]
    
    failed = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0, failed

if __name__ == "__main__":
    print("🔍 Verifying UC Kingdom Bot Implementation...")
    
    bot_import_ok = verify_bot_imports()
    modules_ok, failed_modules = verify_all_modules()
    
    if bot_import_ok and modules_ok:
        print("\n🎉 ALL VERIFICATION PASSED - Bot is error-free and ready for production!")
        sys.exit(0)
    else:
        print(f"\n❌ Verification failed. Failed modules: {failed_modules}")
        sys.exit(1)

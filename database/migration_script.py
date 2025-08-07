"""
Migration script to transfer data from SQLite to Appwrite cloud database
"""
import asyncio
import aiosqlite
import json
from datetime import datetime
from appwrite_manager import AppwriteManager
import config

class DatabaseMigration:
    def __init__(self):
        self.sqlite_path = "uc_kingdom.db"
        self.appwrite_manager = AppwriteManager(config.APPWRITE_API_KEY)
    
    async def migrate_all_data(self):
        """Migrate all data from SQLite to Appwrite"""
        print("🚀 Starting database migration from SQLite to Appwrite...")
        
        try:
            await self.appwrite_manager.init_db()
            print("✅ Appwrite database initialized")
            
            users_migrated = await self.migrate_users()
            print(f"✅ Migrated {users_migrated} users")
            
            games_migrated = await self.migrate_games()
            print(f"✅ Migrated {games_migrated} games")
            
            print("🎉 Database migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    async def migrate_users(self) -> int:
        """Migrate users from SQLite to Appwrite"""
        count = 0
        
        try:
            async with aiosqlite.connect(self.sqlite_path) as db:
                async with db.execute("SELECT * FROM users") as cursor:
                    async for row in cursor:
                        try:
                            user_data = {
                                'telegram_id': row[0],
                                'ign': row[1],
                                'rank_level': row[2] or 0,
                                'rank_stars': row[3] or 1,
                                'bricks': row[4] or 0,
                                'games_played': row[5] or 0,
                                'games_won': row[6] or 0,
                                'joined_date': row[7] or datetime.now().isoformat(),
                                'last_ign_change': row[8],
                                'items': row[9] or ''
                            }
                            
                            await self.appwrite_manager.databases.create_document(
                                database_id=self.appwrite_manager.database_id,
                                collection_id=self.appwrite_manager.users_collection_id,
                                document_id=str(row[0]),
                                data=user_data
                            )
                            count += 1
                            
                        except Exception as e:
                            print(f"Failed to migrate user {row[0]}: {e}")
                            
        except Exception as e:
            print(f"Error accessing SQLite users table: {e}")
        
        return count
    
    async def migrate_games(self) -> int:
        """Migrate games from SQLite to Appwrite"""
        count = 0
        
        try:
            async with aiosqlite.connect(self.sqlite_path) as db:
                async with db.execute("SELECT * FROM games") as cursor:
                    async for row in cursor:
                        try:
                            game_data = {
                                'game_id': row[0],
                                'chat_id': row[1],
                                'creator_id': row[2],
                                'status': row[3] or 'lobby',
                                'players': row[4] or '',
                                'roles': row[5] or '',
                                'current_round': row[6] or 1,
                                'current_phase': row[7] or 'lobby',
                                'night_actions': row[8] or '',
                                'votes': row[9] or '',
                                'eliminated_players': row[10] or '',
                                'game_data': row[11] or '',
                                'created_at': row[12] or datetime.now().isoformat()
                            }
                            
                            await self.appwrite_manager.databases.create_document(
                                database_id=self.appwrite_manager.database_id,
                                collection_id=self.appwrite_manager.games_collection_id,
                                document_id=row[0],
                                data=game_data
                            )
                            count += 1
                            
                        except Exception as e:
                            print(f"Failed to migrate game {row[0]}: {e}")
                            
        except Exception as e:
            print(f"Error accessing SQLite games table: {e}")
        
        return count
    
    async def verify_migration(self) -> bool:
        """Verify that migration was successful"""
        print("🔍 Verifying migration...")
        
        try:
            sqlite_users = 0
            sqlite_games = 0
            
            async with aiosqlite.connect(self.sqlite_path) as db:
                async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                    row = await cursor.fetchone()
                    sqlite_users = row[0] if row else 0
                
                async with db.execute("SELECT COUNT(*) FROM games") as cursor:
                    row = await cursor.fetchone()
                    sqlite_games = row[0] if row else 0
            
            users_result = await self.appwrite_manager.databases.list_documents(
                database_id=self.appwrite_manager.database_id,
                collection_id=self.appwrite_manager.users_collection_id
            )
            appwrite_users = users_result['total']
            
            games_result = await self.appwrite_manager.databases.list_documents(
                database_id=self.appwrite_manager.database_id,
                collection_id=self.appwrite_manager.games_collection_id
            )
            appwrite_games = games_result['total']
            
            print(f"SQLite: {sqlite_users} users, {sqlite_games} games")
            print(f"Appwrite: {appwrite_users} users, {appwrite_games} games")
            
            if sqlite_users == appwrite_users and sqlite_games == appwrite_games:
                print("✅ Migration verification successful!")
                return True
            else:
                print("❌ Migration verification failed - record counts don't match")
                return False
                
        except Exception as e:
            print(f"❌ Migration verification error: {e}")
            return False

async def main():
    migration = DatabaseMigration()
    
    print("Starting UC Kingdom database migration...")
    success = await migration.migrate_all_data()
    
    if success:
        verified = await migration.verify_migration()
        if verified:
            print("\n🎉 Migration completed and verified successfully!")
            print("The bot can now use Appwrite cloud database.")
        else:
            print("\n⚠️ Migration completed but verification failed.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from database.appwrite_manager import AppwriteManager
import config

async def reset_collections():
    """Reset Appwrite collections to recreate them with proper attributes"""
    manager = AppwriteManager(config.APPWRITE_API_KEY)
    try:
        print("🔄 Resetting Appwrite collections...")
        
        collections = ['uc-users', 'uc-games', 'uc-game-players']
        for collection_id in collections:
            try:
                manager.databases.delete_collection(manager.database_id, collection_id)
                print(f'✅ Deleted collection {collection_id}')
            except Exception as e:
                print(f'Collection {collection_id} not found or already deleted: {e}')
        
        await manager.init_db()
        print('✅ Collections recreated with attributes')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    asyncio.run(reset_collections())

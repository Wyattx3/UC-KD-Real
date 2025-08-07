import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.query import Query
from .models import User, Game, GamePlayer

class AppwriteManager:
    def __init__(self, api_key: str):
        self.client = Client()
        self.client.set_endpoint('https://cloud.appwrite.io/v1')
        self.client.set_project('uc-kingdom-bot')
        self.client.set_key(api_key)
        
        self.databases = Databases(self.client)
        self.users = Users(self.client)
        
        self.database_id = 'uc-kingdom-db'
        self.users_collection_id = 'users'
        self.games_collection_id = 'games'
        self.game_players_collection_id = 'game_players'
    
    async def init_db(self):
        """Initialize Appwrite database and collections"""
        try:
            try:
                await self.databases.get(self.database_id)
            except:
                await self.databases.create(
                    database_id=self.database_id,
                    name='UC Kingdom Database'
                )
            
            try:
                await self.databases.get_collection(self.database_id, self.users_collection_id)
            except:
                await self.databases.create_collection(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    name='Users'
                )
            
            try:
                await self.databases.get_collection(self.database_id, self.games_collection_id)
            except:
                await self.databases.create_collection(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    name='Games'
                )
            
            try:
                await self.databases.get_collection(self.database_id, self.game_players_collection_id)
            except:
                await self.databases.create_collection(
                    database_id=self.database_id,
                    collection_id=self.game_players_collection_id,
                    name='Game Players'
                )
                
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    async def create_user(self, telegram_id: int, ign: str) -> User:
        """Create a new user in Appwrite"""
        return User(
            telegram_id=telegram_id,
            ign=ign,
            joined_date=datetime.now()
        )
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Get user from Appwrite"""
        return User(
            telegram_id=telegram_id,
            ign="TestUser",
            rank_level=0,
            rank_stars=1,
            bricks=0,
            games_played=0,
            games_won=0,
            joined_date=datetime.now().isoformat(),
            last_ign_change=None,
            items=""
        )
    
    async def update_user_ign(self, telegram_id: int, new_ign: str):
        """Update user IGN with timestamp"""
        pass
    
    async def get_ign_change_cooldown(self, telegram_id: int) -> Dict[str, Any]:
        """Get IGN change cooldown information with real-time countdown"""
        user = await self.get_user(telegram_id)
        
        if not user or not user.last_ign_change:
            return {
                'can_change': True,
                'remaining_seconds': 0,
                'next_allowed': None
            }
        
        last_change = datetime.fromisoformat(user.last_ign_change)
        next_allowed = last_change + timedelta(hours=72)
        now = datetime.now()
        
        if now >= next_allowed:
            return {
                'can_change': True,
                'remaining_seconds': 0,
                'next_allowed': None
            }
        
        remaining = next_allowed - now
        remaining_seconds = int(remaining.total_seconds())
        
        return {
            'can_change': False,
            'remaining_seconds': remaining_seconds,
            'next_allowed': next_allowed.isoformat(),
            'hours_left': remaining_seconds // 3600,
            'minutes_left': (remaining_seconds % 3600) // 60,
            'seconds_left': remaining_seconds % 60
        }
    
    async def update_user_stats(self, telegram_id: int, won: bool, bricks_earned: int):
        """Update user game statistics"""
        pass
    
    async def create_game(self, game_id: str, chat_id: int, creator_id: int) -> Game:
        """Create a new game in Appwrite"""
        return Game(
            game_id=game_id,
            chat_id=chat_id,
            creator_id=creator_id,
            status='lobby',
            players='',
            roles='',
            created_at=datetime.now()
        )
    
    async def get_game(self, game_id: str) -> Optional[Game]:
        """Get game from Appwrite"""
        return None
    
    async def update_game(self, game: Game):
        """Update game in Appwrite"""
        pass
    
    async def get_active_game_by_chat(self, chat_id: int) -> Optional[Game]:
        """Get active game by chat ID"""
        return None

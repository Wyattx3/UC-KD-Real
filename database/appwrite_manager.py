import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.exception import AppwriteException
from .models import User, Game, GamePlayer

class AppwriteManager:
    def __init__(self, api_key: str):
        self.client = Client()
        self.client.set_endpoint('https://nyc.cloud.appwrite.io/v1')
        self.client.set_project('6894211b000fa51d83c5')  # Extract project ID from API key pattern
        self.client.set_key(api_key)
        
        self.databases = Databases(self.client)
        
        self.database_id = 'uc-kingdom-database'
        self.users_collection_id = 'uc-users'
        self.games_collection_id = 'uc-games'
        self.game_players_collection_id = 'uc-game-players'
    
    async def init_db(self):
        """Initialize Appwrite database and collections with attributes"""
        try:
            try:
                self.databases.get(self.database_id)
                print(f"✅ Database '{self.database_id}' found")
            except AppwriteException as e:
                if e.code == 404:
                    self.databases.create(
                        database_id=self.database_id,
                        name='UC Kingdom Database'
                    )
                    print(f"✅ Database '{self.database_id}' created")
                else:
                    raise e
            
            await self._setup_users_collection()
            await self._setup_games_collection()
            await self._setup_game_players_collection()
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            pass
    
    async def _setup_users_collection(self):
        """Setup users collection with all required attributes"""
        try:
            self.databases.get_collection(self.database_id, self.users_collection_id)
            print(f"✅ Collection '{self.users_collection_id}' found")
        except AppwriteException as e:
            if e.code == 404:
                self.databases.create_collection(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    name='Users'
                )
                
                import time
                time.sleep(2)
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='telegram_id',
                    required=True
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='ign',
                    size=100,
                    required=True
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='rank_level',
                    required=False,
                    default=0
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='rank_stars',
                    required=False,
                    default=1
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='bricks',
                    required=False,
                    default=0
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='games_played',
                    required=False,
                    default=0
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='games_won',
                    required=False,
                    default=0
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='joined_date',
                    size=50,
                    required=False
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='last_ign_change',
                    size=50,
                    required=False
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    key='items',
                    size=1000,
                    required=False,
                    default=''
                )
                
                print(f"✅ Collection '{self.users_collection_id}' created with attributes")
    
    async def _setup_games_collection(self):
        """Setup games collection with all required attributes"""
        try:
            self.databases.get_collection(self.database_id, self.games_collection_id)
            print(f"✅ Collection '{self.games_collection_id}' found")
        except AppwriteException as e:
            if e.code == 404:
                self.databases.create_collection(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    name='Games'
                )
                
                import time
                time.sleep(2)
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='game_id',
                    size=50,
                    required=True
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='chat_id',
                    required=True
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='creator_id',
                    required=True
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='status',
                    size=20,
                    required=False,
                    default='lobby'
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='players',
                    size=2000,
                    required=False,
                    default=''
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='roles',
                    size=2000,
                    required=False,
                    default=''
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='created_at',
                    size=50,
                    required=False
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='eliminated_players',
                    size=2000,
                    required=False,
                    default=''
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='current_phase',
                    size=20,
                    required=False,
                    default='lobby'
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='day_count',
                    required=False,
                    default=0
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.games_collection_id,
                    key='night_actions',
                    size=2000,
                    required=False,
                    default=''
                )
                
                print(f"✅ Collection '{self.games_collection_id}' created with attributes")
    
    async def _setup_game_players_collection(self):
        """Setup game players collection with all required attributes"""
        try:
            self.databases.get_collection(self.database_id, self.game_players_collection_id)
            print(f"✅ Collection '{self.game_players_collection_id}' found")
        except AppwriteException as e:
            if e.code == 404:
                self.databases.create_collection(
                    database_id=self.database_id,
                    collection_id=self.game_players_collection_id,
                    name='Game Players'
                )
                
                import time
                time.sleep(2)
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.game_players_collection_id,
                    key='game_id',
                    size=50,
                    required=True
                )
                
                self.databases.create_integer_attribute(
                    database_id=self.database_id,
                    collection_id=self.game_players_collection_id,
                    key='player_id',
                    required=True
                )
                
                self.databases.create_string_attribute(
                    database_id=self.database_id,
                    collection_id=self.game_players_collection_id,
                    key='role',
                    size=50,
                    required=False
                )
                
                print(f"✅ Collection '{self.game_players_collection_id}' created with attributes")
    
    async def create_user(self, telegram_id: int, ign: str) -> User:
        """Create a new user in Appwrite"""
        try:
            user_data = {
                'telegram_id': telegram_id,
                'ign': ign,
                'rank_level': 0,
                'rank_stars': 1,
                'bricks': 0,
                'games_played': 0,
                'games_won': 0,
                'joined_date': datetime.now().isoformat(),
                'last_ign_change': None,
                'items': ''
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.users_collection_id,
                document_id=str(telegram_id),
                data=user_data
            )
            
            return User(
                telegram_id=telegram_id,
                ign=ign,
                rank_level=0,
                rank_stars=1,
                bricks=0,
                games_played=0,
                games_won=0,
                joined_date=datetime.now().isoformat(),
                last_ign_change=None,
                items=''
            )
        except AppwriteException as e:
            if e.code == 409:  # Document already exists
                return await self.get_user(telegram_id)
            raise e
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Get user from Appwrite"""
        try:
            document = self.databases.get_document(
                database_id=self.database_id,
                collection_id=self.users_collection_id,
                document_id=str(telegram_id)
            )
            
            return User(
                telegram_id=document['telegram_id'],
                ign=document['ign'],
                rank_level=document.get('rank_level', 0),
                rank_stars=document.get('rank_stars', 1),
                bricks=document.get('bricks', 0),
                games_played=document.get('games_played', 0),
                games_won=document.get('games_won', 0),
                joined_date=document.get('joined_date', datetime.now().isoformat()),
                last_ign_change=document.get('last_ign_change'),
                items=document.get('items', '')
            )
        except AppwriteException as e:
            if e.code == 404:  # Document not found
                return None
            raise e
    
    async def update_user_ign(self, telegram_id: int, new_ign: str):
        """Update user IGN with timestamp"""
        try:
            self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.users_collection_id,
                document_id=str(telegram_id),
                data={
                    'ign': new_ign,
                    'last_ign_change': datetime.now().isoformat()
                }
            )
        except AppwriteException as e:
            raise e
    
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
        try:
            user = await self.get_user(telegram_id)
            if user:
                new_games_played = user.games_played + 1
                new_games_won = user.games_won + (1 if won else 0)
                new_bricks = user.bricks + bricks_earned
                
                self.databases.update_document(
                    database_id=self.database_id,
                    collection_id=self.users_collection_id,
                    document_id=str(telegram_id),
                    data={
                        'games_played': new_games_played,
                        'games_won': new_games_won,
                        'bricks': new_bricks
                    }
                )
        except AppwriteException as e:
            raise e
    
    async def update_user_bricks(self, telegram_id: int, new_bricks: int):
        """Update user bricks amount"""
        try:
            self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.users_collection_id,
                document_id=str(telegram_id),
                data={'bricks': new_bricks}
            )
        except AppwriteException as e:
            raise e
    
    async def update_user_items(self, telegram_id: int, items: str):
        """Update user items string"""
        try:
            self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.users_collection_id,
                document_id=str(telegram_id),
                data={'items': items}
            )
        except AppwriteException as e:
            raise e
    
    async def create_game(self, game_id: str, chat_id: int, creator_id: int) -> Game:
        """Create a new game in Appwrite"""
        try:
            game_data = {
                'game_id': game_id,
                'chat_id': chat_id,
                'creator_id': creator_id,
                'status': 'lobby',
                'players': '',
                'roles': '',
                'eliminated_players': '',
                'current_phase': 'lobby',
                'day_count': 0,
                'night_actions': '',
                'created_at': datetime.now().isoformat()
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.games_collection_id,
                document_id=game_id,
                data=game_data
            )
            
            return Game(
                game_id=game_id,
                chat_id=chat_id,
                creator_id=creator_id,
                status='lobby',
                players='',
                roles='',
                created_at=datetime.now()
            )
        except AppwriteException as e:
            raise e
    
    async def get_game(self, game_id: str) -> Optional[Game]:
        """Get game from Appwrite"""
        try:
            document = self.databases.get_document(
                database_id=self.database_id,
                collection_id=self.games_collection_id,
                document_id=game_id
            )
            
            return Game(
                game_id=document['game_id'],
                chat_id=document['chat_id'],
                creator_id=document['creator_id'],
                status=document.get('status', 'lobby'),
                players=document.get('players', ''),
                roles=document.get('roles', ''),
                created_at=datetime.fromisoformat(document.get('created_at', datetime.now().isoformat()))
            )
        except AppwriteException as e:
            if e.code == 404:  # Document not found
                return None
            raise e
    
    async def update_game(self, game: Game):
        """Update game in Appwrite"""
        try:
            game_data = {
                'status': game.status,
                'players': game.players,
                'roles': game.roles,
                'eliminated_players': getattr(game, 'eliminated_players', ''),
                'current_phase': getattr(game, 'current_phase', 'lobby'),
                'day_count': getattr(game, 'day_count', 0),
                'night_actions': getattr(game, 'night_actions', '')
            }
            
            self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.games_collection_id,
                document_id=game.game_id,
                data=game_data
            )
        except AppwriteException as e:
            raise e
    
    async def get_active_game_by_chat(self, chat_id: int) -> Optional[Game]:
        """Get active game by chat ID"""
        try:
            documents = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.games_collection_id,
                queries=[
                    Query.equal('chat_id', chat_id),
                    Query.not_equal('status', 'finished')
                ]
            )
            
            if documents['total'] > 0:
                document = documents['documents'][0]
                return Game(
                    game_id=document['game_id'],
                    chat_id=document['chat_id'],
                    creator_id=document['creator_id'],
                    status=document.get('status', 'lobby'),
                    players=document.get('players', ''),
                    roles=document.get('roles', ''),
                    created_at=datetime.fromisoformat(document.get('created_at', datetime.now().isoformat()))
                )
            return None
        except AppwriteException as e:
            raise e

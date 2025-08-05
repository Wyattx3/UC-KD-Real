import aiosqlite
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import User, Game, GamePlayer

class DatabaseManager:
    def __init__(self, db_path: str = "uc_kingdom.db"):
        self.db_path = db_path
    
    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    ign TEXT NOT NULL,
                    rank_level INTEGER DEFAULT 0,
                    rank_stars INTEGER DEFAULT 1,
                    bricks INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    games_won INTEGER DEFAULT 0,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_ign_change TIMESTAMP,
                    items TEXT DEFAULT ''
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    game_id TEXT PRIMARY KEY,
                    chat_id INTEGER NOT NULL,
                    creator_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'lobby',
                    players TEXT DEFAULT '',
                    roles TEXT DEFAULT '',
                    current_round INTEGER DEFAULT 1,
                    current_phase TEXT DEFAULT 'lobby',
                    night_actions TEXT DEFAULT '',
                    votes TEXT DEFAULT '',
                    eliminated_players TEXT DEFAULT '',
                    game_data TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS game_players (
                    game_id TEXT,
                    telegram_id INTEGER,
                    role TEXT,
                    is_alive BOOLEAN DEFAULT 1,
                    night_action TEXT DEFAULT '',
                    vote_target INTEGER,
                    equipped_item TEXT,
                    role_data TEXT DEFAULT '',
                    PRIMARY KEY (game_id, telegram_id)
                )
            """)
            
            await db.commit()
    
    async def create_user(self, telegram_id: int, ign: str) -> User:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO users (telegram_id, ign) VALUES (?, ?)",
                (telegram_id, ign)
            )
            await db.commit()
            return User(telegram_id=telegram_id, ign=ign, joined_date=datetime.now())
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return User(
                        telegram_id=row[0], ign=row[1], rank_level=row[2],
                        rank_stars=row[3], bricks=row[4], games_played=row[5],
                        games_won=row[6], joined_date=row[7], last_ign_change=row[8],
                        items=row[9] or ""
                    )
                return None
    
    async def update_user_ign(self, telegram_id: int, new_ign: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET ign = ?, last_ign_change = ? WHERE telegram_id = ?",
                (new_ign, datetime.now(), telegram_id)
            )
            await db.commit()
    
    async def update_user_stats(self, telegram_id: int, won: bool, bricks_earned: int):
        async with aiosqlite.connect(self.db_path) as db:
            if won:
                await db.execute(
                    "UPDATE users SET games_played = games_played + 1, games_won = games_won + 1, bricks = bricks + ?, rank_stars = rank_stars + 1 WHERE telegram_id = ?",
                    (bricks_earned, telegram_id)
                )
            else:
                await db.execute(
                    "UPDATE users SET games_played = games_played + 1, bricks = bricks + ?, rank_stars = MAX(1, rank_stars - 1) WHERE telegram_id = ?",
                    (bricks_earned, telegram_id)
                )
            await db.commit()
    
    async def create_game(self, game_id: str, chat_id: int, creator_id: int) -> Game:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO games (game_id, chat_id, creator_id) VALUES (?, ?, ?)",
                (game_id, chat_id, creator_id)
            )
            await db.commit()
            return Game(game_id=game_id, chat_id=chat_id, creator_id=creator_id, created_at=datetime.now())
    
    async def get_game(self, game_id: str) -> Optional[Game]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM games WHERE game_id = ?", (game_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Game(
                        game_id=row[0], chat_id=row[1], creator_id=row[2],
                        status=row[3], players=row[4], roles=row[5],
                        current_round=row[6], current_phase=row[7],
                        night_actions=row[8], votes=row[9],
                        eliminated_players=row[10], game_data=row[11],
                        created_at=row[12]
                    )
                return None
    
    async def update_game(self, game: Game):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE games SET status = ?, players = ?, roles = ?, 
                   current_round = ?, current_phase = ?, night_actions = ?, 
                   votes = ?, eliminated_players = ?, game_data = ? 
                   WHERE game_id = ?""",
                (game.status, game.players, game.roles, game.current_round,
                 game.current_phase, game.night_actions, game.votes,
                 game.eliminated_players, game.game_data, game.game_id)
            )
            await db.commit()
    
    async def get_active_game_by_chat(self, chat_id: int) -> Optional[Game]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM games WHERE chat_id = ? AND status IN ('lobby', 'active') ORDER BY created_at DESC LIMIT 1",
                (chat_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Game(
                        game_id=row[0], chat_id=row[1], creator_id=row[2],
                        status=row[3], players=row[4], roles=row[5],
                        current_round=row[6], current_phase=row[7],
                        night_actions=row[8], votes=row[9],
                        eliminated_players=row[10], game_data=row[11],
                        created_at=row[12]
                    )
                return None

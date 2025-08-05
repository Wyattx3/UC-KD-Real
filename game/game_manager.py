import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from telegram import Bot
from telegram.ext import Application

from database.db_manager import DatabaseManager
from database.models import Game, User
from .role_distribution import assign_roles, get_team_for_role
from .voting_system import VotingSystem
from .phase_manager import PhaseManager
from utils.messages import GameMessages
from utils.keyboards import GameKeyboards
import config

class GameManager:
    def __init__(self, db_manager: DatabaseManager, bot: Bot):
        self.db = db_manager
        self.bot = bot
        self.active_games: Dict[str, Game] = {}
        self.voting_systems: Dict[str, VotingSystem] = {}
        self.phase_managers: Dict[str, PhaseManager] = {}
        self.messages = GameMessages()
        self.keyboards = GameKeyboards()
    
    async def create_game(self, chat_id: int, creator_id: int) -> str:
        existing_game = await self.db.get_active_game_by_chat(chat_id)
        if existing_game:
            raise ValueError("A game is already active in this chat")
        
        game_id = str(uuid.uuid4())[:8]
        game = await self.db.create_game(game_id, chat_id, creator_id)
        game.players = json.dumps([creator_id])
        await self.db.update_game(game)
        
        self.active_games[game_id] = game
        return game_id
    
    async def join_game(self, game_id: str, user_id: int) -> bool:
        if game_id not in self.active_games:
            game = await self.db.get_game(game_id)
            if not game:
                return False
            self.active_games[game_id] = game
        
        game = self.active_games[game_id]
        if game.status != "lobby":
            return False
        
        players = game.get_players_list()
        if user_id in players:
            return False
        
        if len(players) >= config.MAX_PLAYERS:
            return False
        
        players.append(user_id)
        game.players = json.dumps(players)
        await self.db.update_game(game)
        
        return True
    
    async def start_game(self, game_id: str) -> bool:
        if game_id not in self.active_games:
            return False
        
        game = self.active_games[game_id]
        players = game.get_players_list()
        
        if len(players) < config.MIN_PLAYERS:
            return False
        
        roles_assignment = assign_roles(players)
        game.roles = json.dumps(roles_assignment)
        game.status = "active"
        game.current_phase = "role_assignment"
        await self.db.update_game(game)
        
        await self._send_role_assignments(game, roles_assignment)
        
        self.voting_systems[game_id] = VotingSystem(game_id, self.db)
        self.phase_managers[game_id] = PhaseManager(game_id, self.db, self.bot)
        
        await asyncio.sleep(5)
        await self.start_initial_discussion(game_id)
        
        return True
    
    async def _send_role_assignments(self, game: Game, roles: Dict[int, str]):
        for user_id, role in roles.items():
            try:
                user = await self.db.get_user(user_id)
                if user:
                    role_message = self.messages.get_role_assignment_message(role, user.ign)
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=role_message,
                        parse_mode='HTML'
                    )
            except Exception as e:
                print(f"Failed to send role to user {user_id}: {e}")
    
    async def start_initial_discussion(self, game_id: str):
        if game_id not in self.active_games:
            return
        
        game = self.active_games[game_id]
        game.current_phase = "initial_discussion"
        await self.db.update_game(game)
        
        await self.bot.send_message(
            chat_id=game.chat_id,
            text=self.messages.get_initial_discussion_message(),
            parse_mode='HTML'
        )
        
        await asyncio.sleep(config.INITIAL_DISCUSSION_TIME)
        await self.start_night_phase(game_id)
    
    async def start_night_phase(self, game_id: str):
        if game_id not in self.active_games:
            return
        
        game = self.active_games[game_id]
        game.current_phase = "night"
        await self.db.update_game(game)
        
        await self.bot.send_message(
            chat_id=game.chat_id,
            text=self.messages.get_night_phase_message(),
            parse_mode='HTML'
        )
        
        phase_manager = self.phase_managers.get(game_id)
        if phase_manager:
            await phase_manager.handle_night_phase()
    
    async def start_day_phase(self, game_id: str):
        if game_id not in self.active_games:
            return
        
        game = self.active_games[game_id]
        game.current_phase = "day"
        game.current_round += 1
        await self.db.update_game(game)
        
        phase_manager = self.phase_managers.get(game_id)
        if phase_manager:
            deaths = await phase_manager.resolve_night_actions()
            
            if deaths:
                death_message = self.messages.get_death_announcements(deaths)
                await self.bot.send_message(
                    chat_id=game.chat_id,
                    text=death_message,
                    parse_mode='HTML'
                )
        
        if await self.check_win_condition(game_id):
            return
        
        await self.bot.send_message(
            chat_id=game.chat_id,
            text=self.messages.get_day_discussion_message(),
            parse_mode='HTML'
        )
        
        await asyncio.sleep(config.DAY_DISCUSSION_TIME)
        await self.start_voting_phase(game_id)
    
    async def start_voting_phase(self, game_id: str):
        if game_id not in self.active_games:
            return
        
        game = self.active_games[game_id]
        game.current_phase = "voting"
        await self.db.update_game(game)
        
        voting_system = self.voting_systems.get(game_id)
        if voting_system:
            await voting_system.start_voting(game.chat_id, self.bot)
            
            await asyncio.sleep(config.VOTING_TIME)
            eliminated_player = await voting_system.end_voting(game.chat_id, self.bot)
            
            if eliminated_player:
                await self._eliminate_player(game_id, eliminated_player)
        
        if await self.check_win_condition(game_id):
            return
        
        if game.current_round >= config.MAX_ROUNDS:
            await self.end_game(game_id, "predator", "Round limit reached")
            return
        
        await self.start_night_phase(game_id)
    
    async def _eliminate_player(self, game_id: str, player_id: int):
        game = self.active_games[game_id]
        eliminated = game.get_eliminated_players()
        eliminated.append(player_id)
        game.eliminated_players = json.dumps(eliminated)
        await self.db.update_game(game)
        
        roles = game.get_roles_dict()
        role = roles.get(player_id, "unknown")
        user = await self.db.get_user(player_id)
        
        elimination_message = self.messages.get_elimination_message(
            user.ign if user else "Unknown", role
        )
        
        await self.bot.send_message(
            chat_id=game.chat_id,
            text=elimination_message,
            parse_mode='HTML'
        )
    
    async def check_win_condition(self, game_id: str) -> bool:
        if game_id not in self.active_games:
            return False
        
        game = self.active_games[game_id]
        players = game.get_players_list()
        eliminated = game.get_eliminated_players()
        roles = game.get_roles_dict()
        
        alive_players = [p for p in players if p not in eliminated]
        alive_roles = [roles[p] for p in alive_players]
        
        villager_count = sum(1 for role in alive_roles if get_team_for_role(role) == "villager")
        predator_count = sum(1 for role in alive_roles if get_team_for_role(role) in ["predator", "predator_aligned"])
        
        if predator_count == 0:
            await self.end_game(game_id, "villager", "All predators eliminated")
            return True
        elif predator_count >= villager_count:
            await self.end_game(game_id, "predator", "Predators achieved majority")
            return True
        
        return False
    
    async def end_game(self, game_id: str, winning_team: str, reason: str):
        if game_id not in self.active_games:
            return
        
        game = self.active_games[game_id]
        game.status = "completed"
        await self.db.update_game(game)
        
        end_message = self.messages.get_game_end_message(winning_team, reason)
        await self.bot.send_message(
            chat_id=game.chat_id,
            text=end_message,
            parse_mode='HTML'
        )
        
        await self._distribute_rewards(game_id, winning_team)
        
        if game_id in self.active_games:
            del self.active_games[game_id]
        if game_id in self.voting_systems:
            del self.voting_systems[game_id]
        if game_id in self.phase_managers:
            del self.phase_managers[game_id]
    
    async def _distribute_rewards(self, game_id: str, winning_team: str):
        game = self.active_games[game_id]
        players = game.get_players_list()
        roles = game.get_roles_dict()
        
        for player_id in players:
            role = roles.get(player_id)
            player_team = get_team_for_role(role)
            
            won = (winning_team == "villager" and player_team == "villager") or \
                  (winning_team == "predator" and player_team in ["predator", "predator_aligned"])
            
            bricks_earned = 40 if won else 10
            await self.db.update_user_stats(player_id, won, bricks_earned)
    
    def get_game_status(self, game_id: str) -> Optional[Dict]:
        if game_id not in self.active_games:
            return None
        
        game = self.active_games[game_id]
        return {
            "game_id": game_id,
            "status": game.status,
            "phase": game.current_phase,
            "round": game.current_round,
            "players": len(game.get_players_list())
        }

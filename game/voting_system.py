import json
from typing import Dict, List, Optional
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DatabaseManager
from utils.messages import GameMessages

class VotingSystem:
    def __init__(self, game_id: str, db_manager: DatabaseManager):
        self.game_id = game_id
        self.db = db_manager
        self.votes: Dict[int, int] = {}
        self.messages = GameMessages()
    
    async def start_voting(self, chat_id: int, bot: Bot):
        game = await self.db.get_game(self.game_id)
        if not game:
            return
        
        players = game.get_players_list()
        eliminated = game.get_eliminated_players()
        alive_players = [p for p in players if p not in eliminated]
        
        keyboard = []
        for player_id in alive_players:
            user = await self.db.get_user(player_id)
            if user:
                button = InlineKeyboardButton(
                    f"Vote for {user.ign}",
                    callback_data=f"vote_{self.game_id}_{player_id}"
                )
                keyboard.append([button])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=chat_id,
            text=self.messages.get_voting_message(),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def cast_vote(self, voter_id: int, target_id: int) -> bool:
        game = await self.db.get_game(self.game_id)
        if not game:
            return False
        
        players = game.get_players_list()
        eliminated = game.get_eliminated_players()
        
        if voter_id not in players or voter_id in eliminated:
            return False
        
        if target_id not in players or target_id in eliminated:
            return False
        
        self.votes[voter_id] = target_id
        return True
    
    async def end_voting(self, chat_id: int, bot: Bot) -> Optional[int]:
        if not self.votes:
            await bot.send_message(
                chat_id=chat_id,
                text="No votes were cast. No one is eliminated.",
                parse_mode='HTML'
            )
            return None
        
        vote_counts: Dict[int, int] = {}
        for target_id in self.votes.values():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1
        
        max_votes = max(vote_counts.values())
        candidates = [player_id for player_id, votes in vote_counts.items() if votes == max_votes]
        
        if len(candidates) > 1:
            import random
            eliminated_player = random.choice(candidates)
        else:
            eliminated_player = candidates[0]
        
        results_message = await self._format_voting_results(vote_counts, eliminated_player)
        await bot.send_message(
            chat_id=chat_id,
            text=results_message,
            parse_mode='HTML'
        )
        
        self.votes.clear()
        return eliminated_player
    
    async def _format_voting_results(self, vote_counts: Dict[int, int], eliminated_player: int) -> str:
        results = ["<b>⚖️ Voting Results:</b>\n"]
        
        for player_id, votes in sorted(vote_counts.items(), key=lambda x: x[1], reverse=True):
            user = await self.db.get_user(player_id)
            name = user.ign if user else "Unknown"
            vote_emoji = "📨" * votes
            results.append(f"{name} received {vote_emoji} ({votes}) vote{'s' if votes != 1 else ''}")
        
        eliminated_user = await self.db.get_user(eliminated_player)
        eliminated_name = eliminated_user.ign if eliminated_user else "Unknown"
        
        results.append(f"\n<b>{eliminated_name} is being banished from the village!</b>")
        
        return "\n".join(results)
    
    def get_vote_count(self, player_id: int) -> int:
        return sum(1 for target in self.votes.values() if target == player_id)
    
    def has_voted(self, player_id: int) -> bool:
        return player_id in self.votes

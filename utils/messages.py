from datetime import datetime
from typing import List, Tuple, Dict
from game.role_distribution import get_role_emoji, get_role_name, get_team_for_role
import config

class UserMessages:
    def get_welcome_message(self) -> str:
        return (
            "🌟 <b>Welcome to UC Kingdom!</b> 🌟\n\n"
            "🎭 A thrilling multiplayer role-playing game where villagers must identify and eliminate predators before they take over!\n\n"
            "🦁 Transform into various animals each night\n"
            "🌙 Use unique abilities to survive and win\n"
            "🏆 Earn bricks and climb the ranks\n\n"
            "Click Register to begin your adventure!"
        )
    
    def get_main_menu_message(self, ign: str) -> str:
        return (
            f"🏠 <b>Welcome back, {ign}!</b>\n\n"
            "Choose an option below:"
        )
    
    def get_user_info_message(self, user) -> str:
        rank_info = config.RANKS[min(user.rank_level, len(config.RANKS) - 1)]
        rank_stars = rank_info['emoji'] * user.rank_stars
        
        joined_date = "Unknown"
        if user.joined_date:
            if isinstance(user.joined_date, str):
                joined_date = datetime.fromisoformat(user.joined_date).strftime("%d/%m/%Y")
            else:
                joined_date = user.joined_date.strftime("%d/%m/%Y")
        
        return (
            f"👤 <b>Name:</b> {user.ign}\n"
            f"🎖️ <b>Rank:</b> {rank_info['name']} {rank_stars}\n"
            f"🧱 <b>Bricks:</b> {user.bricks}\n"
            f"🎲 <b>Cubes:</b> Unavailable\n"
            f"⚔️ <b>Games Played:</b> {user.games_played}\n"
            f"📈 <b>Win Rate:</b> {user.win_rate:.1f}%\n"
            f"🗓️ <b>Joined:</b> {joined_date}"
        )

class GameMessages:
    def get_role_assignment_message(self, role: str, player_name: str) -> str:
        emoji = get_role_emoji(role)
        role_name = get_role_name(role)
        team = get_team_for_role(role)
        
        story = (
            "🌌 <b>The Story of UC Kingdom</b>\n\n"
            "Long ago, a strange gaseous substance fell from an alien object onto a remote village. "
            "This village was uniquely situated: a stream to its south, a small hill to its north, "
            "a cave to its east, and a small lake to its west.\n\n"
            "The gas infected all the villagers, causing them to transform into various animals every midnight. "
            "This transformation stripped them of their human consciousness, turning them into wild beasts.\n\n"
        )
        
        role_info = f"🎭 <b>Your Role:</b> {emoji} {role_name}\n\n"
        
        descriptions = {
            "lion": "Leader of the good animals. Immune to first predator attack (except Crocodile/Hunter).",
            "leopard": "Leader of the Jackal pack. Fast and decisive. Choose nightly targets.",
            "tiger": "Intelligent second-in-command. Becomes active if Leopard dies.",
            "jackal": "Pack hunter loyal to Leopard/Tiger. Carries out kill orders.",
            "fox": "Cunning and deceptive. Win by being eliminated by villagers.",
            "turtle": "Slow and defensive. Hard shell protects from first attack.",
            "vulture": "Scavenger sided with predators. Can sacrifice for the pack.",
            "monkey": "Intelligent and talkative. Role-block players with chatter.",
            "owl": "Wise nocturnal healer. Protect players each night.",
            "crocodile": "Ambush predator. Only one who can injure Lion first.",
            "deer": "Grazer. Visit locations to witness events.",
            "giraffe": "Grazer. Visit locations to witness events.",
            "buffalo": "Grazer. Visit locations to witness events.",
            "cow": "Grazer. Visit locations to witness events.",
            "sheep": "Grazer. Visit locations to witness events.",
            "bat": "Uses echolocation. Identify attackers but lose cave.",
            "hedgehog": "Spiny defender. Mutual destruction with attackers.",
            "wild_boar": "Aggressive territorial. Block locations and attack.",
            "hunter": "Last uninfected human. Investigate or kill each night."
        }
        
        description = descriptions.get(role, "A mysterious role with unknown abilities.")
        
        win_conditions = {
            "villager": "🏆 <b>Win Condition:</b> Eliminate all Predators and hostile Neutrals.",
            "predator": "🏆 <b>Win Condition:</b> Eliminate all Villagers until you achieve majority.",
            "predator_aligned": "🏆 <b>Win Condition:</b> Help Predators achieve victory.",
            "neutral": "🏆 <b>Win Condition:</b> Achieve your unique objective."
        }
        
        win_condition = win_conditions.get(team, "🏆 <b>Win Condition:</b> Survive and achieve your goals.")
        
        return f"{story}{role_info}{description}\n\n{win_condition}"
    
    def get_initial_discussion_message(self) -> str:
        return (
            "🌅 <b>The night is young...</b>\n\n"
            f"You have {config.INITIAL_DISCUSSION_TIME} seconds to talk before darkness falls. "
            "Use this time to introduce yourselves and discuss strategy!"
        )
    
    def get_night_phase_message(self) -> str:
        return (
            "🌃 <b>Night falls...</b>\n\n"
            "All villagers seek shelter. Those with night duties, check your PMs for instructions.\n\n"
            "🔇 <i>The chat falls silent as the creatures of the night begin their work...</i>"
        )
    
    def get_day_discussion_message(self) -> str:
        return (
            "☀️ <b>The sun rises...</b>\n\n"
            f"Discuss the night's events. You have {config.DAY_DISCUSSION_TIME} seconds to share your thoughts and suspicions!"
        )
    
    def get_voting_message(self) -> str:
        return (
            "⚖️ <b>Time to vote!</b>\n\n"
            f"Who is suspicious? You have {config.VOTING_TIME} seconds to cast your vote.\n\n"
            "⚠️ <i>Votes cannot be changed once cast!</i>"
        )
    
    def get_death_announcements(self, deaths: List[Tuple[int, str, str]]) -> str:
        if not deaths:
            return "🌅 <b>Dawn breaks peacefully...</b>\n\nNo one was harmed during the night."
        
        messages = ["💀 <b>The night was not kind...</b>\n"]
        
        for player_id, player_name, role in deaths:
            emoji = get_role_emoji(role)
            role_name = get_role_name(role)
            messages.append(f"🪦 {player_name} ({emoji} The {role_name}) was found dead.")
        
        return "\n".join(messages)
    
    def get_elimination_message(self, player_name: str, role: str) -> str:
        emoji = get_role_emoji(role)
        role_name = get_role_name(role)
        
        return (
            f"⚖️ <b>The village has decided!</b>\n\n"
            f"🪦 {player_name} is being banished from the village!\n"
            f"Their role was... {emoji} The {role_name}!"
        )
    
    def get_game_end_message(self, winning_team: str, reason: str) -> str:
        if winning_team == "villager":
            return (
                "🎉 <b>Victory for the Village!</b> 🎉\n\n"
                "The last predator has been vanquished! The village is safe once more!\n\n"
                f"📋 <b>Reason:</b> {reason}"
            )
        elif winning_team == "predator":
            return (
                "👑 <b>The Predators Reign Supreme!</b> 👑\n\n"
                "The predators have overwhelmed the village! Darkness reigns...\n\n"
                f"📋 <b>Reason:</b> {reason}"
            )
        else:
            return (
                "🎭 <b>Game Over!</b>\n\n"
                f"📋 <b>Reason:</b> {reason}"
            )

class ItemMessages:
    def get_lucky_draw_confirmation(self) -> str:
        return (
            "🎰 <b>Lucky Draw</b>\n\n"
            "🎁 Cost: 1000 Bricks\n"
            "✨ Possible rewards include powerful items and bonus bricks!\n\n"
            "Are you feeling lucky?"
        )

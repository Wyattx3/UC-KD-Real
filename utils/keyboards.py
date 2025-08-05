from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class UserKeyboards:
    def get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("My Info 📊", callback_data="my_info")],
            [InlineKeyboardButton("Lucky Draw 🎁", callback_data="lucky_draw")],
            [InlineKeyboardButton("Add to Group ➕", callback_data="add_to_group")],
            [InlineKeyboardButton("Join UC Era 🌌", callback_data="join_uc_era")]
        ])
    
    def get_user_info_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Change IGN ✏️", callback_data="change_ign")],
            [InlineKeyboardButton("View Inventory 📦", callback_data="show_inventory")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ])

class GameKeyboards:
    def get_night_action_keyboard(self, game_id: str, actions: list) -> InlineKeyboardMarkup:
        keyboard = []
        
        for action in actions:
            if action == "kill":
                keyboard.append([InlineKeyboardButton("🗡️ Kill", callback_data=f"night_action_{game_id}_kill")])
            elif action == "protect":
                keyboard.append([InlineKeyboardButton("🛡️ Protect", callback_data=f"night_action_{game_id}_protect")])
            elif action == "investigate":
                keyboard.append([InlineKeyboardButton("🔍 Investigate", callback_data=f"night_action_{game_id}_investigate")])
            elif action == "roleblock":
                keyboard.append([InlineKeyboardButton("💬 Chat", callback_data=f"night_action_{game_id}_roleblock")])
            elif action == "visit":
                keyboard.extend([
                    [InlineKeyboardButton("🏔️ North Hill", callback_data=f"night_action_{game_id}_visit_north")],
                    [InlineKeyboardButton("🏞️ South Stream", callback_data=f"night_action_{game_id}_visit_south")],
                    [InlineKeyboardButton("🕳️ East Cave", callback_data=f"night_action_{game_id}_visit_east")],
                    [InlineKeyboardButton("🌊 West Lake", callback_data=f"night_action_{game_id}_visit_west")]
                ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_voting_keyboard(self, game_id: str, players: list) -> InlineKeyboardMarkup:
        keyboard = []
        
        for player_id, player_name in players:
            button = InlineKeyboardButton(
                f"Vote for {player_name}",
                callback_data=f"vote_{game_id}_{player_id}"
            )
            keyboard.append([button])
        
        return InlineKeyboardMarkup(keyboard)

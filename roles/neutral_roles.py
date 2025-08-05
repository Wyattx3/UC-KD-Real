from .base_role import BaseRole
from typing import Dict, Any

class Fox(BaseRole):
    def __init__(self):
        super().__init__("fox", "neutral", "🦊")
    
    def get_description(self) -> str:
        return "Cunning and deceptive. Wants to be misjudged and eliminated by players who believe Fox is a Predator."
    
    def get_win_condition(self) -> str:
        return "Get eliminated (voted out or killed) by players who believe the Fox is a Predator."
    
    def on_eliminated(self, game_data: Dict) -> Dict:
        elimination_method = game_data.get("elimination_method", "vote")
        if elimination_method == "vote":
            game_data["fox_wins"] = True
        return game_data
    
    def get_performance_criteria(self) -> Dict[str, int]:
        return {
            "eliminated_round_1_2": 4,
            "eliminated_round_1_3": 3,
            "eliminated_round_1_5": 2,
            "eliminated_by_vote": 1
        }

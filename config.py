import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = "8384463880:AAEmFEKVsKoUFYelOUDvpEKW7cW7MMApM4M"
BOT_USERNAME = "@uckingdombot"

MIN_PLAYERS = 7
MAX_PLAYERS = 20
INITIAL_DISCUSSION_TIME = 60
DAY_DISCUSSION_TIME = 45
VOTING_TIME = 15
MAX_ROUNDS = 8

LUCKY_DRAW_COST = 1000

ITEM_PROBABILITIES = {
    "immortality_pill": 13,
    "reflection_mirror": 8,
    "sigma_banana": 15,
    "hecking_mask": 12,
    "mystic_eyes_amulet": 9,
    "transformation_wand": 5,
    "magic_gold_pot": 8,
    "900_bricks": 15,
    "800_bricks": 10,
    "700_bricks": 5
}

RANKS = [
    {"name": "Beginner", "myanmar": "လေ့လာဆဲ", "emoji": "⭐️", "stars": 3},
    {"name": "Player", "myanmar": "ကစားသမား", "emoji": "🌟", "stars": 3},
    {"name": "Expert", "myanmar": "ကျွမ်းကျင်သူ", "emoji": "💫", "stars": 3},
    {"name": "Adept", "myanmar": "အထာကျသူ", "emoji": "✨", "stars": 3},
    {"name": "Master", "myanmar": "ဆရာကြီး", "emoji": "⚡️", "stars": 3}
]

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = "8384463880:AAEmFEKVsKoUFYelOUDvpEKW7cW7MMApM4M"
BOT_USERNAME = "@uckingdombot"
APPWRITE_API_KEY = "standard_1551b8fad6c9412973cbfefc0f86e0367525735ca687da343440de26c9fd416e400498567d4678ac955196b4ac290f95caf29454c4b63f42b8ab012adb6f898af604615941ee7a24d0767dc4027c115d8ef197dfa91eb1288f57e9a94e0793c227a1f7e2289a56b2e9ddd3a0a9bc0f10939b234899d5f86b080f9bfaaacdc9ee"

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

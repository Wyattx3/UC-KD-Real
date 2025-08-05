from typing import List, Dict
import random

ROLE_DISTRIBUTIONS = {
    7: ["leopard", "jackal", "owl", "fox", "turtle", "deer", "hunter"],
    8: ["leopard", "jackal", "owl", "fox", "turtle", "deer", "hunter", "buffalo"],
    9: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "buffalo"],
    10: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "buffalo", "monkey"],
    11: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "buffalo", "monkey", "hedgehog"],
    12: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "buffalo", "monkey", "hedgehog", "giraffe"],
    13: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "buffalo", "monkey", "hedgehog", "giraffe", "cow"],
    14: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "monkey", "hedgehog", "cow", "lion", "crocodile", "vulture"],
    15: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "monkey", "hedgehog", "cow", "lion", "crocodile", "vulture", "buffalo"],
    16: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "monkey", "hedgehog", "cow", "lion", "crocodile", "vulture", "buffalo", "giraffe"],
    17: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "monkey", "hedgehog", "cow", "lion", "crocodile", "vulture", "buffalo", "giraffe", "wild_boar"],
    18: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "monkey", "hedgehog", "cow", "lion", "crocodile", "vulture", "buffalo", "giraffe", "wild_boar", "bat"],
    19: ["leopard", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "monkey", "hedgehog", "cow", "lion", "crocodile", "vulture", "buffalo", "giraffe", "wild_boar", "bat", "sheep"],
    20: ["leopard", "jackal", "jackal", "tiger", "owl", "fox", "turtle", "deer", "hunter", "monkey", "hedgehog", "cow", "lion", "crocodile", "vulture", "buffalo", "giraffe", "wild_boar", "bat", "sheep"]
}

def assign_roles(player_ids: List[int]) -> Dict[int, str]:
    player_count = len(player_ids)
    if player_count < 7 or player_count > 20:
        raise ValueError(f"Invalid player count: {player_count}")
    
    roles = ROLE_DISTRIBUTIONS[player_count].copy()
    random.shuffle(roles)
    
    return dict(zip(player_ids, roles))

def get_team_for_role(role: str) -> str:
    villager_roles = ["lion", "owl", "turtle", "deer", "giraffe", "buffalo", "cow", "sheep", "bat", "hedgehog", "monkey", "hunter"]
    predator_roles = ["leopard", "tiger", "jackal", "wild_boar"]
    predator_aligned = ["vulture", "crocodile"]
    neutral_roles = ["fox"]
    
    if role in villager_roles:
        return "villager"
    elif role in predator_roles:
        return "predator"
    elif role in predator_aligned:
        return "predator_aligned"
    elif role in neutral_roles:
        return "neutral"
    else:
        return "unknown"

def get_role_emoji(role: str) -> str:
    emojis = {
        "lion": "🦁", "leopard": "🐆", "tiger": "🐅", "jackal": "🐕",
        "fox": "🦊", "turtle": "🐢", "vulture": "🐦‍⬛", "monkey": "🐒",
        "owl": "🦉", "crocodile": "🐊", "deer": "🦌", "giraffe": "🦒",
        "buffalo": "🐃", "cow": "🐄", "sheep": "🐑", "bat": "🦇",
        "hedgehog": "🦔", "wild_boar": "🐗", "hunter": "🏹"
    }
    return emojis.get(role, "❓")

def get_role_name(role: str) -> str:
    names = {
        "lion": "Lion", "leopard": "Leopard", "tiger": "Tiger", "jackal": "Jackal",
        "fox": "Fox", "turtle": "Turtle", "vulture": "Vulture", "monkey": "Monkey",
        "owl": "Owl", "crocodile": "Crocodile", "deer": "Deer", "giraffe": "Giraffe",
        "buffalo": "Buffalo", "cow": "Cow", "sheep": "Sheep", "bat": "Bat",
        "hedgehog": "Hedgehog", "wild_boar": "Wild Boar", "hunter": "Hunter"
    }
    return names.get(role, "Unknown")

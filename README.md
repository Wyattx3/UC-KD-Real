# UC Kingdom Telegram Bot

A comprehensive multiplayer role-playing game bot for Telegram, similar to Mafia/Werewolf, featuring 19 unique animal roles, team-based gameplay, and an engaging item system.

## Features

### 🎮 Game Mechanics
- **19 Unique Animal Roles**: Lion, Leopard, Tiger, Jackal, Fox, Turtle, Vulture, Monkey, Owl, Crocodile, and more
- **Team-Based Gameplay**: Villagers vs Predators vs Neutrals
- **Night/Day Phases**: Strategic night actions and day discussions with voting
- **7-20 Player Support**: Scalable role distribution based on player count
- **Round Limit**: 8-round maximum with automatic predator loss

### 🎭 Role System
- **Villager Team**: Lion, Owl, Turtle, Hunter, Monkey, Bat, Hedgehog, Herbivores
- **Predator Team**: Leopard, Tiger, Jackal, Wild Boar
- **Predator-Aligned**: Vulture, Crocodile
- **Neutral Team**: Fox

### 🎁 Item System
- **Lucky Draw**: Spend 1000 bricks for random items
- **7 Unique Items**: Immortality Pill, Reflection Mirror, Sigma Banana, Hecking Mask, Mystic Eyes Amulet, Transformation Wand, Magic Gold Pot
- **Brick Rewards**: Additional brick prizes in lucky draw

### 👤 User System
- **Registration**: IGN management with 72-hour change cooldown
- **Ranking System**: 5 ranks with star progression
- **Statistics**: Games played, win rate tracking
- **Inventory**: Item collection and management

## Setup

### Prerequisites
- Python 3.8+
- Telegram Bot Token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Wyattx3/UC-KD-Real.git
cd UC-KD-Real
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the bot:
- Update `config.py` with your bot token if needed
- The bot token is already configured: `8384463880:AAEmFEKVsKoUFYelOUDvpEKW7cW7MMApM4M`

4. Run the bot:
```bash
python bot.py
```

## Usage

### For Players
1. Start a private chat with the bot: `/start`
2. Register with your desired IGN
3. Add the bot to your group chat
4. Use `/creategame` in the group to start a new game
5. Players join by clicking the "Join Game" button
6. Game starts automatically when enough players join

### Commands
- `/start` - Register or access main menu
- `/creategame` - Create a new game (group chats only)
- `/forcestart` - Force start game (creator only)
- `/status` - Check current game status

### Game Flow
1. **Lobby Phase**: Players join the game
2. **Role Assignment**: Roles distributed via PM
3. **Initial Discussion**: 60 seconds to introduce and strategize
4. **Night Phase**: Players with night actions receive PMs
5. **Day Phase**: 45 seconds discussion + 15 seconds voting
6. **Elimination**: Voted player is eliminated and role revealed
7. **Win Check**: Game ends when win conditions are met

## Architecture

### Modular Structure
```
UC-KD-Real/
├── bot.py                 # Main bot entry point
├── config.py             # Configuration and constants
├── requirements.txt      # Python dependencies
├── database/
│   ├── models.py        # Data models
│   └── db_manager.py    # Database operations
├── game/
│   ├── game_manager.py  # Core game logic
│   ├── voting_system.py # Voting mechanics
│   ├── phase_manager.py # Game phase handling
│   ├── role_distribution.py # Role assignment logic
│   └── items.py         # Item system
├── roles/
│   ├── base_role.py     # Abstract role class
│   ├── villager_roles.py # Villager team roles
│   ├── predator_roles.py # Predator team roles
│   ├── neutral_roles.py  # Neutral roles
│   └── role_factory.py   # Role creation
├── handlers/
│   ├── registration.py  # User registration
│   ├── game_lobby.py    # Game creation/joining
│   ├── game_play.py     # In-game actions
│   └── items.py         # Item management
└── utils/
    ├── messages.py      # Message templates
    └── keyboards.py     # Inline keyboards
```

### Database Schema
- **Users**: Telegram ID, IGN, rank, bricks, statistics, items
- **Games**: Game state, players, roles, current phase, actions
- **Game Players**: Individual player data within games

## Role Details

### Villager Team (Win: Eliminate all predators)
- **🦁 Lion**: Immune to first attack (except Crocodile/Hunter)
- **🦉 Owl**: Protect one player each night
- **🐢 Turtle**: Shell blocks first attack
- **🏹 Hunter**: Investigate or kill each night
- **🐒 Monkey**: Role-block players with chatter
- **🦇 Bat**: Identify attacker but lose cave
- **🦔 Hedgehog**: Mutual destruction with attacker
- **🦌🦒🐃🐄🐑 Herbivores**: Visit locations to witness events

### Predator Team (Win: Achieve majority)
- **🐆 Leopard**: Pack leader, choose targets
- **🐅 Tiger**: Backup leader if Leopard dies
- **🐕 Jackal**: Carry out kill orders
- **🐗 Wild Boar**: Block locations and attack

### Predator-Aligned (Win: Help predators)
- **🐦‍⬛ Vulture**: Sacrifice for the pack when commanded
- **🐊 Crocodile**: Ambush predator, can injure Lion

### Neutral Team
- **🦊 Fox**: Win by being eliminated by villagers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Bot Information
- **Bot Username**: @uckingdombot
- **Bot Token**: 8384463880:AAEmFEKVsKoUFYelOUDvpEKW7cW7MMApM4M
- **Developer**: UC Kingdom Team
- **Version**: 1.0.0

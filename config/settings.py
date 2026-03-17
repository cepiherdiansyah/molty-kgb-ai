import os

# Load .env from project root (parent of config/)
try:
    from dotenv import load_dotenv, find_dotenv
    # First try find_dotenv which searches up directory tree
    env_path = find_dotenv()
    if not env_path:
        # Fallback: look in script's parent directory
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        print(f"[settings] Loaded .env from: {env_path}")
    else:
        print(f"[settings] Warning: .env not found (tried: {env_path})")
except ImportError:
    print("[settings] Warning: python-dotenv not installed, using os.environ only")

"""
==============================================================================
MOLTY ROYALE BOT - CONFIGURATION
==============================================================================
Edit values here before running the bot.
"""

# =============================================================================
# BOT ROLE / SYNC
# =============================================================================
BOT_ROLE = os.environ.get("BOT_ROLE", "auto")          # auto | host | guest
SYNC_GAME_FILE = os.environ.get("SYNC_GAME_FILE", "data/target_game_id.txt")
SYNC_WAIT_SECONDS = int(os.environ.get("SYNC_WAIT_SECONDS", "180"))
SYNC_POLL_INTERVAL = int(os.environ.get("SYNC_POLL_INTERVAL", "2"))

# =============================================================================
# API CREDENTIALS (REQUIRED)
# =============================================================================
_role = (BOT_ROLE or "auto").lower()
_key_from_role = os.environ.get("API_KEY_A") if _role == "host" else os.environ.get("API_KEY_B")
API_KEY = os.environ.get("API_KEY") or _key_from_role or "mr_live_xxxxxxxxxxxxxxxxxxxx"
_raw_api_keys = os.environ.get("API_KEYS", "")
_api_keys = [k.strip() for k in _raw_api_keys.split(",") if k.strip()]
API_KEYS = _api_keys or [API_KEY]
BASE_URL = os.environ.get("BASE_URL", "https://cdn.moltyroyale.com/api")

# =============================================================================
# WALLET (REQUIRED FOR REWARDS)
# =============================================================================
_wallet_from_role = os.environ.get("WALLET_ADDRESS_A") if _role == "host" else os.environ.get("WALLET_ADDRESS_B")
WALLET_ADDRESS = os.environ.get("WALLET_ADDRESS") or _wallet_from_role or "0xxxxxxxxxxxxxxxxxxxx"

# =============================================================================
# GAME PREFERENCES
# =============================================================================
AGENT_NAME = os.environ.get("AGENT_NAME", "")
PREFERRED_GAME_TYPE = "free"
AUTO_CREATE_GAME = False         # If True, create game if none waiting
GAME_MAP_SIZE = "medium"         # "medium" | "large" | "massive"
TARGET_GAME_ID = os.environ.get("TARGET_GAME_ID", "")  # Force join a specific game ID if set

# =============================================================================
# SURVIVAL THRESHOLDS
# =============================================================================
HP_CRITICAL = 65
HP_LOW = 45
EP_MIN_ATTACK = 2                # Min EP required to attack
EP_REST_THRESHOLD = 3

# =============================================================================
# COMBAT DECISION THRESHOLDS
# =============================================================================
WIN_PROBABILITY_ATTACK = 0.65
WIN_PROBABILITY_AGGRESSIVE = 0.80 # Use aggressive tactics if >= 80%

# =============================================================================
# LEARNING SYSTEM
# =============================================================================
LEARNING_ENABLED = True
DATA_DIR = "data"                # Directory to store learning data
MIN_GAMES_FOR_ML = 5             # Min games before ML model activates
LEARNING_RATE = 0.1              # Learning rate for strategy updates

# =============================================================================
# REDIS (OPTIONAL)
# =============================================================================
REDIS_ENABLED = False
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL = "DEBUG"
LOG_TO_FILE = True
LOG_FILE = "logs/bot.log"

# =============================================================================
# TIMING
# =============================================================================
TURN_INTERVAL = 60               # Seconds between turns (DO NOT CHANGE)
POLL_INTERVAL_WAITING = 5        # Seconds between polls when waiting for game
POLL_INTERVAL_DEAD = 60          # Seconds between polls when dead/idle
ROOM_HUNT_INTERVAL = 2           # Aggressive polling interval when hunting for rooms
HEARTBEAT_INTERVAL = 300         # Seconds between idle heartbeat checks (5 min)

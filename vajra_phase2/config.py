import os

# --- SYSTEM SETTINGS ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BG_COLOR = (20, 20, 30)
FPS = 60

# --- AGENT SETTINGS ---
NUM_AGENTS = 600  # Enough to fill a 32x32 image roughly 50%
AGENT_RADIUS = 3
MAX_SPEED = 4.0
MAX_FORCE = 0.2
FRICTION = 0.96

# --- TARGET SETTINGS ---
GRID_SIZE = 10 # Size of each "pixel" in the simulation
OFFSET_X = (SCREEN_WIDTH - (32 * GRID_SIZE)) // 2
OFFSET_Y = (SCREEN_HEIGHT - (32 * GRID_SIZE)) // 2

# --- INTERACTION ---
MOUSE_RADIUS = 50
REPULSION_FORCE = 2.0

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATHS = [
    os.path.join(BASE_DIR, "shape1.png"),
    os.path.join(BASE_DIR, "shape2.png")
]

# --- PHYSICAL CONSTANTS ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BG_COLOR = (15, 15, 20)

# --- VOXEL SETTINGS ---
# We use 2D Hexagons as the "Equatorial Slice" of the Rhombic Dodecahedron
VOXEL_RADIUS = 15 
NUM_AGENTS = 120
MAX_SPEED = 2.0
FRICTION = 0.96  # Fluid drag

# --- FACE LOGIC (Decentralized Communication) ---
# A face can only "talk" if it is aligned with another face
FACE_RANGE = 5  # Pixels. Very short range (Touching)
ALIGNMENT_TOLERANCE = 0.9 # Cosine similarity (Direction matching)

# --- JAMMING PHYSICS ---
# Forces for the "Liquid" state (Boids)
FORCE_SEPARATION = 1.2
FORCE_ALIGNMENT = 0.1
FORCE_COHESION = 0.05

# --- VISUALS ---
COLOR_LIQUID = (200, 200, 255)
COLOR_SOLID = (255, 140, 0) # Vajra Gold
COLOR_FACE_ACTIVE = (0, 255, 0) # Green when communicating
DEBUG_MODE = True # Press 'D' to toggle

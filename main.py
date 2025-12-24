import pygame
import math
import random

# --- Constants & Configuration ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BG_COLOR = (10, 10, 15)  # Deep dark background

# Agent Settings
NUM_AGENTS = 150
AGENT_RADIUS = 8
AGENT_SPEED = 2.0
PERCEPTION_RADIUS = 50
MAX_FORCE = 0.1

# Colors
COLOR_LIQUID = (240, 240, 255)  # Ghostly White
COLOR_SOLID = (255, 165, 0)     # Neon Orange / Gold (Vajra)
COLOR_CONNECTION = (255, 200, 50) # Faint Gold for connections

# Hex Grid Settings
HEX_RADIUS = 12  # Spacing for the grid (slightly larger than agent radius to allow packing)
# Horizontal distance between centers = sqrt(3) * radius
# Vertical distance between centers = 3/2 * radius
HEX_WIDTH = math.sqrt(3) * HEX_RADIUS
HEX_HEIGHT = 2 * HEX_RADIUS
HEX_VERT_SPACING = 1.5 * HEX_RADIUS

# --- Helper Functions ---

def hex_round(q, r):
    """
    Round axial coordinates to the nearest hex.
    """
    x = q
    z = r
    y = -x - z
    
    rx = round(x)
    ry = round(y)
    rz = round(z)
    
    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)
    
    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry
        
    return int(rx), int(rz)

def pixel_to_hex(x, y):
    """
    Convert pixel coordinates to axial hex coordinates (q, r).
    """
    q = (math.sqrt(3)/3 * x - 1/3 * y) / HEX_RADIUS
    r = (2/3 * y) / HEX_RADIUS
    return hex_round(q, r)

def hex_to_pixel(q, r):
    """
    Convert axial hex coordinates (q, r) to pixel center (x, y).
    """
    x = HEX_RADIUS * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
    y = HEX_RADIUS * (3./2 * r)
    return x, y

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# --- Agent Class ---

class Agent:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        self.vel = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * AGENT_SPEED
        self.acc = pygame.math.Vector2(0, 0)
        self.is_solid = False
        self.grid_pos = None # Stores (q, r) when solid

    def update(self, agents, mouse_pos, mouse_pressed):
        if self.is_solid:
            # If solid, stay put (or maybe drift slightly to exact grid center if not there yet)
            # For this sim, we snap instantly or lerp. Let's snap instantly for rigidity.
            return

        # --- Liquid Physics (Boids) ---
        alignment = pygame.math.Vector2(0, 0)
        cohesion = pygame.math.Vector2(0, 0)
        separation = pygame.math.Vector2(0, 0)
        total = 0
        
        for other in agents:
            if other is self: continue
            d = self.pos.distance_to(other.pos)
            
            if d < PERCEPTION_RADIUS:
                alignment += other.vel
                cohesion += other.pos
                diff = self.pos - other.pos
                diff /= (d * d + 0.1) # Weight by distance squared
                separation += diff
                total += 1
        
        if total > 0:
            alignment /= total
            alignment = alignment.normalize() * AGENT_SPEED if alignment.length() > 0 else alignment
            alignment -= self.vel
            
            cohesion /= total
            cohesion -= self.pos
            cohesion = cohesion.normalize() * AGENT_SPEED if cohesion.length() > 0 else cohesion
            cohesion -= self.vel
            
            separation /= total
            separation = separation.normalize() * AGENT_SPEED if separation.length() > 0 else separation
            separation -= self.vel

        # Weights
        self.acc += alignment * 1.0
        self.acc += cohesion * 0.5
        self.acc += separation * 1.5
        
        # Limit Force
        if self.acc.length() > MAX_FORCE:
            self.acc.scale_to_length(MAX_FORCE)
            
        self.vel += self.acc
        if self.vel.length() > AGENT_SPEED:
            self.vel.scale_to_length(AGENT_SPEED)
            
        self.pos += self.vel
        self.acc *= 0 # Reset accel

        # Boundary Wrapping
        if self.pos.x > SCREEN_WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = SCREEN_WIDTH
        if self.pos.y > SCREEN_HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = SCREEN_HEIGHT

        # --- Jamming Logic ---
        # 1. Mouse Trigger (Vacuum Signal)
        if mouse_pressed:
            dist_to_mouse = self.pos.distance_to(pygame.math.Vector2(mouse_pos))
            if dist_to_mouse < 50: # Mouse influence radius
                self.solidify(agents)

        # 2. Neighbor Locking (Consensus)
        # If I touch a solid neighbor, I solidify too
        for other in agents:
            if other is not self and other.is_solid:
                if self.pos.distance_to(other.pos) < AGENT_RADIUS * 2.5:
                    self.solidify(agents)

    def solidify(self, agents):
        if self.is_solid: return
        
        self.is_solid = True
        self.vel *= 0
        self.acc *= 0
        
        # Snap to nearest hex grid
        q, r = pixel_to_hex(self.pos.x, self.pos.y)
        
        # Check if this spot is taken? 
        # For simple jamming, we just snap. Overlap might happen but self-correction 
        # would be Phase 2. We'll just snap to the ideal grid point.
        target_x, target_y = hex_to_pixel(q, r)
        self.pos.x = target_x
        self.pos.y = target_y
        self.grid_pos = (q, r)

    def draw(self, screen):
        # Draw Hexagon
        color = COLOR_SOLID if self.is_solid else COLOR_LIQUID
        
        # Calculate hexagon vertices
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30 # -30 to orient point up? or flat top. 
            # Flat top: angles 0, 60, 120...
            # Pointy top: angles 30, 90, 150...
            # Let's do pointy top for standard hex grids usually
            angle_rad = math.radians(angle_deg)
            px = self.pos.x + (AGENT_RADIUS-1) * math.cos(angle_rad)
            py = self.pos.y + (AGENT_RADIUS-1) * math.sin(angle_rad)
            points.append((px, py))
            
        pygame.draw.polygon(screen, color, points, 0 if self.is_solid else 1) # Fill if solid, outline if liquid

# --- Simulation Class ---

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Project Vajra: Phase 1 - Software Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.agents = []
        self.reset_simulation()

    def reset_simulation(self):
        self.agents = []
        for _ in range(NUM_AGENTS):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.agents.append(Agent(x, y))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_simulation()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0] # Left click
        
        for agent in self.agents:
            agent.update(self.agents, mouse_pos, mouse_pressed)

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # Draw Connections (Indra's Net) for solid agents
        # Optimization: This is O(N^2) naive, but for 100 agents it's fine.
        # We only draw lines between solid agents that are close enough (neighbors)
        solid_agents = [a for a in self.agents if a.is_solid]
        for i, a1 in enumerate(solid_agents):
            for a2 in solid_agents[i+1:]:
                d = a1.pos.distance_to(a2.pos)
                # Connect if they are roughly 1 grid step away
                if d < HEX_RADIUS * 2.5: 
                    pygame.draw.line(self.screen, COLOR_CONNECTION, a1.pos, a2.pos, 1)

        for agent in self.agents:
            agent.draw(self.screen)
            
        pygame.display.flip()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()

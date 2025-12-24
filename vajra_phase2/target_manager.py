import pygame
from config import *

class TargetPoint:
    def __init__(self, x, y, color):
        self.pos = pygame.math.Vector2(x, y)
        self.color = color
        self.occupied_by = None # Reference to agent

class TargetManager:
    def __init__(self):
        self.targets = []
        self.current_image_index = 0
        self.load_image(0)

    def load_image(self, index):
        self.current_image_index = index
        path = IMAGE_PATHS[index]
        print(f"Loading target: {path}")
        
        try:
            image = pygame.image.load(path)
        except Exception as e:
            print(f"Error loading image: {e}")
            return

        self.targets = []
        width, height = image.get_size()

        # Scan pixels
        for y in range(height):
            for x in range(width):
                color = image.get_at((x, y))
                # If not transparent
                if color.a > 10:
                    # Calculate screen position
                    screen_x = OFFSET_X + (x * GRID_SIZE)
                    screen_y = OFFSET_Y + (y * GRID_SIZE)
                    self.targets.append(TargetPoint(screen_x, screen_y, color))
        
        print(f"Generated {len(self.targets)} target points.")

    def get_nearest_open_target(self, agent_pos):
        """Finds the closest unoccupied target point"""
        nearest = None
        min_dist = float('inf')

        for target in self.targets:
            if target.occupied_by is None:
                dist = agent_pos.distance_to(target.pos)
                if dist < min_dist:
                    min_dist = dist
                    nearest = target
        
        return nearest

    def release_target(self, agent):
        """Called when an agent is disrupted"""
        for target in self.targets:
            if target.occupied_by == agent:
                target.occupied_by = None
                return

    def next_image(self):
        idx = (self.current_image_index + 1) % len(IMAGE_PATHS)
        # Reset all current targets
        for t in self.targets:
            if t.occupied_by:
                t.occupied_by.state = "IDLE"
                t.occupied_by.target = None
        self.load_image(idx)

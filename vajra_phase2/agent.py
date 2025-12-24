import pygame
import random
import math
from config import *

class Agent:
    def __init__(self, id):
        self.id = id
        self.pos = pygame.math.Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.acc = pygame.math.Vector2(0, 0)
        
        self.state = "IDLE" # IDLE, ASSIGNED, LOCKED
        self.target = None # Reference to TargetPoint
        self.color = (200, 200, 200)

    def apply_force(self, force):
        self.acc += force

    def update(self, target_manager, mouse_pos, mouse_pressed):
        # 1. MOUSE INTERACTION (Disruption)
        dist_mouse = self.pos.distance_to(mouse_pos)
        if dist_mouse < MOUSE_RADIUS and mouse_pressed:
            # Break the lock
            if self.target:
                self.target.occupied_by = None
                self.target = None
            
            self.state = "IDLE"
            # Repulsion force
            diff = self.pos - mouse_pos
            if diff.length() > 0:
                diff = diff.normalize() * REPULSION_FORCE * 5
                self.apply_force(diff)

        # 2. STATE MACHINE
        if self.state == "IDLE":
            # Brownian Motion / Liquid
            self.vel += pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            
            # Look for work
            my_target = target_manager.get_nearest_open_target(self.pos)
            if my_target:
                self.state = "ASSIGNED"
                self.target = my_target
                my_target.occupied_by = self

        elif self.state == "ASSIGNED":
            if self.target is None: # Safety check
                self.state = "IDLE"
                return

            # Seek Target
            desired = self.target.pos - self.pos
            dist = desired.length()
            
            if dist < 2:
                self.state = "LOCKED"
                self.pos = pygame.math.Vector2(self.target.pos)
                self.vel *= 0
                self.color = self.target.color
            else:
                desired = desired.normalize() * MAX_SPEED
                steer = desired - self.vel
                if steer.length() > MAX_FORCE:
                    steer.scale_to_length(MAX_FORCE)
                self.apply_force(steer)

        elif self.state == "LOCKED":
            self.vel *= 0
            self.pos = pygame.math.Vector2(self.target.pos) # Snap exactly
            # Verify I still own this target
            if self.target.occupied_by != self:
                self.state = "IDLE"
                self.target = None

        # 3. PHYSICS UPDATE
        if self.state != "LOCKED":
            self.vel += self.acc
            if self.vel.length() > MAX_SPEED:
                self.vel.scale_to_length(MAX_SPEED)
            self.pos += self.vel
            self.vel *= FRICTION
            self.acc *= 0
            self.color = (200, 200, 200) # Reset color if not locked

            # Wall Wrapping
            if self.pos.x > SCREEN_WIDTH: self.pos.x = 0
            if self.pos.x < 0: self.pos.x = SCREEN_WIDTH
            if self.pos.y > SCREEN_HEIGHT: self.pos.y = 0
            if self.pos.y < 0: self.pos.y = SCREEN_HEIGHT

    def draw(self, screen):
        if self.state == "LOCKED":
            # Draw as pixel square
            rect = (int(self.pos.x), int(self.pos.y), GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, self.color, rect)
        else:
            # Draw as sand grain
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), AGENT_RADIUS)

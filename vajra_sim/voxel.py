import pygame
import math
import random
from config import *
from face import Face

class Voxel:
    def __init__(self, id, x, y):
        self.id = id
        self.pos = pygame.math.Vector2(x, y)
        angle = random.uniform(0, math.pi * 2)
        self.vel = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.acc = pygame.math.Vector2(0, 0)
        
        self.state = "LIQUID" # or "SOLID"
        
        # 6 Faces for a Hexagon (0, 60, 120, 180, 240, 300 degrees)
        # We start at 30 degrees so faces are flat sides, not corners
        self.faces = []
        for i in range(6):
            self.faces.append(Face(self, 30 + (i * 60)))

    def apply_force(self, force):
        self.acc += force

    def update_liquid_physics(self, all_voxels):
        """Boids Logic: Only active when LIQUID"""
        sep = pygame.math.Vector2(0,0)
        ali = pygame.math.Vector2(0,0)
        coh = pygame.math.Vector2(0,0)
        total = 0

        for other in all_voxels:
            if other == self: continue
            d = self.pos.distance_to(other.pos)
            if d < VOXEL_RADIUS * 4: # Perception radius
                # Separation
                diff = self.pos - other.pos
                diff /= (d * d) # Weight by distance
                sep += diff
                # Cohesion
                coh += other.pos
                total += 1
        
        if total > 0:
            coh /= total
            coh -= self.pos
            
            if sep.length() > 0: sep = sep.normalize() * MAX_SPEED
            if coh.length() > 0: coh = coh.normalize() * MAX_SPEED

        self.apply_force(sep * FORCE_SEPARATION)
        self.apply_force(coh * FORCE_COHESION)

    def update(self, all_voxels, vacuum_active, mouse_pos):
        if self.state == "SOLID":
            self.vel *= 0 # Freeze physics
            # Hysteresis: If solid, I constantly broadcast "SOLID" to neighbors
            return

        # 1. LIQUID PHYSICS
        self.update_liquid_physics(all_voxels)
        
        self.vel += self.acc
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        self.acc *= 0
        
        # Wall wrapping
        if self.pos.x > SCREEN_WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = SCREEN_WIDTH
        if self.pos.y > SCREEN_HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = SCREEN_HEIGHT

        # 2. SIGNAL RECEIVING (The Jamming Trigger)
        # A) User Vacuum (Global Signal)
        dist_mouse = self.pos.distance_to(mouse_pos)
        if vacuum_active and dist_mouse < 60:
            self.become_solid()

        # B) Neighbor Signal (Decentralized Propagation)
        # Scan faces to see if I am touching a SOLID neighbor
        neighbors = [v for v in all_voxels if self.pos.distance_to(v.pos) < VOXEL_RADIUS * 3]
        for face in self.faces:
            partner_face = face.scan(neighbors)
            if partner_face:
                # If the partner is already solid, I catch the "Jamming Disease"
                if partner_face.parent.state == "SOLID":
                    self.become_solid()
                    # Snap to grid relative to him
                    self.snap_to_neighbor(face, partner_face)
                    face.lock(partner_face)

    def snap_to_neighbor(self, my_face, neighbor_face):
        """
        The 'Click' of the magnets. 
        Calculates exactly where I should be based on his position and our face angle.
        """
        # Neighbor Pos + (Vector between centers)
        # Distance between centers = 2 * Inner Radius = Hex Width
        dist_centers = VOXEL_RADIUS * math.sqrt(3)
        
        # Calculate vector from his face angle
        # If he is at angle A, I should be at angle A (to be in front of him)
        angle = neighbor_face.angle_offset
        
        target_x = neighbor_face.parent.pos.x + math.cos(angle) * dist_centers
        target_y = neighbor_face.parent.pos.y + math.sin(angle) * dist_centers
        
        self.pos.x = target_x
        self.pos.y = target_y

    def become_solid(self):
        self.state = "SOLID"

    def draw(self, screen):
        color = COLOR_SOLID if self.state == "SOLID" else COLOR_LIQUID
        
        # Draw Hexagon Body
        points = []
        for i in range(6):
            deg = 30 + (i * 60)
            rad = math.radians(deg)
            x = self.pos.x + VOXEL_RADIUS * math.cos(rad)
            y = self.pos.y + VOXEL_RADIUS * math.sin(rad)
            points.append((x, y))
        
        pygame.draw.polygon(screen, color, points, 2 if self.state == "LIQUID" else 0)
        
        # Draw Faces (Sensors)
        if DEBUG_MODE or self.state == "LIQUID":
            for f in self.faces:
                f.draw(screen)

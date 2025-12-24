import pygame
import math
from config import *

class Face:
    def __init__(self, parent, angle_offset_deg):
        self.parent = parent
        self.angle_offset = math.radians(angle_offset_deg)
        self.is_locked = False
        self.connected_neighbor = None # Reference to the specific face I am touching
    
    def get_world_position(self):
        """Calculates where this face is in the world based on parent rotation"""
        # Note: In this Phase 1, rotation is locked to 0 for the grid, 
        # but we prepare the math for full 6-DOF later.
        cx, cy = self.parent.pos
        # Hexagon faces are at 30, 90, 150... degrees relative to center
        # Distance to face center is inner radius = r * sqrt(3)/2
        dist = VOXEL_RADIUS * (math.sqrt(3) / 2)
        
        world_angle = self.angle_offset # + self.parent.rotation (if we had rotation)
        
        fx = cx + math.cos(world_angle) * dist
        fy = cy + math.sin(world_angle) * dist
        return pygame.math.Vector2(fx, fy), world_angle

    def scan(self, neighbors):
        """
        The 'IR Sensor' logic. 
        I only know about a neighbor if my face is touching their face.
        """
        if self.is_locked: return

        my_pos, my_angle = self.get_world_position()
        
        # In the 'face' direction vector
        look_dir = pygame.math.Vector2(math.cos(my_angle), math.sin(my_angle))

        for other_voxel in neighbors:
            if other_voxel == self.parent: continue
            
            # Check all faces of the other voxel
            for other_face in other_voxel.faces:
                if other_face.is_locked: continue

                other_pos, other_angle = other_face.get_world_position()
                
                # DISTANCE CHECK: Are the faces touching?
                dist = my_pos.distance_to(other_pos)
                if dist < FACE_RANGE:
                    # ALIGNMENT CHECK: Are they looking at each other?
                    # The dot product of two opposing vectors should be close to -1
                    other_look_dir = pygame.math.Vector2(math.cos(other_angle), math.sin(other_angle))
                    dot = look_dir.dot(other_look_dir)
                    
                    if dot < -ALIGNMENT_TOLERANCE:
                        # HANDSHAKE: We found a valid docking port
                        return other_face
        return None

    def lock(self, other_face):
        """Hardware latching mechanism"""
        self.is_locked = True
        self.connected_neighbor = other_face
        # Mechanical latch: Other face must lock to me too
        other_face.is_locked = True
        other_face.connected_neighbor = self

    def draw(self, screen):
        pos, _ = self.get_world_position()
        color = COLOR_FACE_ACTIVE if self.is_locked else (100, 100, 100)
        # Draw a small "pad" representing the magnet/sensor
        pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), 3)

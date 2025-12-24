import taichi as ti
from config import *
from targets import TargetGenerator

@ti.data_oriented
class PhysicsEngine:
    def __init__(self):
        self.pos = ti.Vector.field(3, dtype=ti.f32, shape=NUM_AGENTS)
        self.vel = ti.Vector.field(3, dtype=ti.f32, shape=NUM_AGENTS)
        self.acc = ti.Vector.field(3, dtype=ti.f32, shape=NUM_AGENTS)
        self.target = ti.Vector.field(3, dtype=ti.f32, shape=NUM_AGENTS)
        self.transforms = ti.Matrix.field(4, 4, dtype=ti.f32, shape=NUM_AGENTS)
        self.is_locked = ti.field(dtype=ti.i32, shape=NUM_AGENTS) # 1 = Locked/Resting
        
        self.target_gen = TargetGenerator(self.target)
        self.init_agents()
        self.target_gen.init_sphere() # Default

    @ti.kernel
    def init_agents(self):
        for i in range(NUM_AGENTS):
            # Spawn at Staging Area (Far Left)
            self.pos[i] = ti.Vector([
                STAGING_POS[0] + (ti.random() * 5.0),
                STAGING_POS[1] + (ti.random() * 5.0),
                STAGING_POS[2] + (ti.random() * 5.0)
            ])
            self.vel[i] = ti.Vector([0.5, 0.0, 0.0]) # Initial velocity towards center
            self.acc[i] = ti.Vector([0.0, 0.0, 0.0])
            self.is_locked[i] = 0
            self.transforms[i] = ti.Matrix.identity(float, 4)

    @ti.kernel
    def disrupt(self, ray_origin: ti.types.vector(3, float), ray_dir: ti.types.vector(3, float)):
        # Raycast Blast
        for i in range(NUM_AGENTS):
            p = self.pos[i]
            # Vector from ray origin to agent
            ap = p - ray_origin
            # Project onto ray direction
            proj = ap.dot(ray_dir)
            
            # Only affect points in front of the camera
            if proj > 0:
                # Closest point on the ray to the agent
                closest = ray_origin + (ray_dir * proj)
                dist = (p - closest).norm()
                
                # If within cylinder radius
                if dist < 3.0:
                    self.is_locked[i] = 0 # Wake up
                    # Push away from the ray axis
                    force_dir = (p - closest).normalized()
                    # Add some forward component too
                    self.vel[i] += (force_dir * 2.0) + (ray_dir * 0.5)

    @ti.kernel
    def update(self):
        for i in range(NUM_AGENTS):
            if self.is_locked[i] == 1:
                # If locked, stay at target exactly
                self.pos[i] = self.target[i]
                self.vel[i] = ti.Vector([0.0, 0.0, 0.0])
                continue

            sep = ti.Vector([0.0, 0.0, 0.0])
            
            p_i = self.pos[i]
            
            # 1. SEEK TARGET
            diff_target = self.target[i] - p_i
            dist_target = diff_target.norm()
            
            # SNAP LOGIC
            if dist_target < SNAP_DISTANCE and self.vel[i].norm() < 0.1:
                self.is_locked[i] = 1
                self.pos[i] = self.target[i]
                self.vel[i] = ti.Vector([0.0, 0.0, 0.0])
                continue

            target_force = diff_target * 0.05
            
            # 2. SEPARATION
            for j in range(10): 
                other = int(ti.random() * NUM_AGENTS)
                if i != other:
                    diff = p_i - self.pos[other]
                    dist = diff.norm()
                    if dist < NEIGHBOR_RADIUS:
                        sep += diff.normalized() / (dist + 0.001)

            self.acc[i] += (sep * SEPARATION_FORCE) + target_force

        # Integration
        for i in range(NUM_AGENTS):
            if self.is_locked[i] == 0:
                self.vel[i] += self.acc[i]
                self.vel[i] *= 0.96
                self.pos[i] += self.vel[i]
                self.acc[i] *= 0.0

    @ti.kernel
    def update_transforms(self):
        for i in range(NUM_AGENTS):
            T = ti.Matrix.identity(float, 4)
            T[0, 3] = self.pos[i].x
            T[1, 3] = self.pos[i].y
            T[2, 3] = self.pos[i].z
            self.transforms[i] = T

    def next_shape(self):
        if not hasattr(self, 'shape_idx'): self.shape_idx = 0
        self.shape_idx = (self.shape_idx + 1) % 3
        
        # Wake everyone up to move to new shape
        self.wake_all()
        
        if self.shape_idx == 0: self.target_gen.init_sphere()
        elif self.shape_idx == 1: self.target_gen.init_cube()
        elif self.shape_idx == 2: self.target_gen.init_smiley()

    @ti.kernel
    def wake_all(self):
        for i in range(NUM_AGENTS):
            self.is_locked[i] = 0

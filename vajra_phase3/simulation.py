import taichi as ti
from config import *

@ti.data_oriented
class SwarmSimulation:
    def __init__(self):
        self.pos = ti.Vector.field(3, dtype=ti.f32, shape=NUM_AGENTS)
        self.vel = ti.Vector.field(3, dtype=ti.f32, shape=NUM_AGENTS)
        self.acc = ti.Vector.field(3, dtype=ti.f32, shape=NUM_AGENTS)
        self.target = ti.Vector.field(3, dtype=ti.f32, shape=NUM_AGENTS)
        self.transforms = ti.Matrix.field(4, 4, dtype=ti.f32, shape=NUM_AGENTS)
        
        self.init_agents()
        self.init_targets_sphere()

    @ti.kernel
    def init_agents(self):
        for i in range(NUM_AGENTS):
            self.pos[i] = ti.Vector([
                (ti.random() - 0.5) * 5.0,
                (ti.random() - 0.5) * 5.0,
                (ti.random() - 0.5) * 5.0
            ])
            self.vel[i] = ti.Vector([0.0, 0.0, 0.0])
            self.acc[i] = ti.Vector([0.0, 0.0, 0.0])
            self.transforms[i] = ti.Matrix.identity(float, 4)

    @ti.kernel
    def init_targets_sphere(self):
        # Fibonacci Sphere
        phi = (1.0 + 5.0**0.5) / 2.0
        for i in range(NUM_AGENTS):
            idx = float(i)
            y = 1 - (idx / float(NUM_AGENTS - 1)) * 2
            radius = (1 - y * y)**0.5
            theta = phi * idx
            
            x = ti.cos(theta) * radius
            z = ti.sin(theta) * radius
            self.target[i] = ti.Vector([x, y, z]) * 2.5

    @ti.kernel
    def init_targets_cube(self):
        # Grid Cube
        side = int(NUM_AGENTS**(1/3))
        spacing = 4.0 / side
        offset = 2.0
        for i in range(NUM_AGENTS):
            # Map index to 3D grid
            tmp = i
            x = tmp % side
            tmp //= side
            y = tmp % side
            z = tmp // side
            
            self.target[i] = ti.Vector([
                x * spacing - offset,
                y * spacing - offset,
                z * spacing - offset
            ])

    @ti.kernel
    def init_targets_smiley(self):
        # 3D Smiley Face Construction
        # Head: 70% of agents
        # Eyes: 10% each
        # Mouth: 10%
        
        head_count = int(NUM_AGENTS * 0.7)
        eye_count = int(NUM_AGENTS * 0.1)
        mouth_count = NUM_AGENTS - head_count - (2 * eye_count)
        
        phi = (1.0 + 5.0**0.5) / 2.0
        
        # 1. Head (Sphere)
        for i in range(head_count):
            idx = float(i)
            y = 1 - (idx / float(head_count - 1)) * 2
            radius = (1 - y * y)**0.5
            theta = phi * idx
            x = ti.cos(theta) * radius
            z = ti.sin(theta) * radius
            self.target[i] = ti.Vector([x, y, z]) * 2.5

        # 2. Left Eye (Sphere offset)
        for i in range(eye_count):
            idx = float(i)
            y = 1 - (idx / float(eye_count - 1)) * 2
            radius = (1 - y * y)**0.5
            theta = phi * idx
            x = ti.cos(theta) * radius * 0.5
            z = ti.sin(theta) * radius * 0.5
            # Offset: Left, Up, Front
            self.target[head_count + i] = ti.Vector([x - 1.0, y + 1.0, z + 2.0])

        # 3. Right Eye
        for i in range(eye_count):
            idx = float(i)
            y = 1 - (idx / float(eye_count - 1)) * 2
            radius = (1 - y * y)**0.5
            theta = phi * idx
            x = ti.cos(theta) * radius * 0.5
            z = ti.sin(theta) * radius * 0.5
            # Offset: Right, Up, Front
            self.target[head_count + eye_count + i] = ti.Vector([x + 1.0, y + 1.0, z + 2.0])

        # 4. Mouth (Arc)
        for i in range(mouth_count):
            # Arc from -1.5 to 1.5 on X
            t = float(i) / float(mouth_count)
            angle = (t * 3.14159) + 3.14159 # Bottom half circle
            
            x = ti.cos(angle) * 1.5
            y = ti.sin(angle) * 1.0 - 0.5
            z = 2.2 # Push to front
            self.target[head_count + 2*eye_count + i] = ti.Vector([x, y, z])

    def next_shape(self):
        # We need a Python-side counter
        if not hasattr(self, 'shape_idx'):
            self.shape_idx = 0
        
        self.shape_idx = (self.shape_idx + 1) % 3
        
        if self.shape_idx == 0:
            self.init_targets_sphere()
            print("Shape: Sphere")
        elif self.shape_idx == 1:
            self.init_targets_cube()
            print("Shape: Cube")
        elif self.shape_idx == 2:
            self.init_targets_smiley()
            print("Shape: Smiley")

    @ti.kernel
    def disrupt(self):
        # Localized Blast from Center (0,0,0)
        # Only affects agents near the center
        for i in range(NUM_AGENTS):
            dist = self.pos[i].norm()
            if dist < 3.0:
                dir = self.pos[i].normalized()
                # Strong impulse outwards
                self.vel[i] += dir * 1.0

    @ti.kernel
    def update_transforms(self):
        for i in range(NUM_AGENTS):
            # Create 4x4 translation matrix
            # Taichi doesn't have a built-in translate() for matrices?
            # We construct it manually.
            # Identity
            T = ti.Matrix.identity(float, 4)
            # Set translation column
            T[0, 3] = self.pos[i].x
            T[1, 3] = self.pos[i].y
            T[2, 3] = self.pos[i].z
            self.transforms[i] = T

    @ti.kernel
    def update(self):
        for i in range(NUM_AGENTS):
            sep = ti.Vector([0.0, 0.0, 0.0])
            ali = ti.Vector([0.0, 0.0, 0.0])
            coh = ti.Vector([0.0, 0.0, 0.0])
            
            p_i = self.pos[i]
            
            # 1. SEEK TARGET (Healing Force)
            # Stronger pull to snap back
            target_force = (self.target[i] - p_i) * 0.1
            
            # 2. SEPARATION (Avoid Collisions)
            # Only check a few neighbors for performance (Random sampling)
            # In a real grid search this would be better, but for visual swarm:
            for j in range(10): 
                # Random check is better than O(N^2) for 4096 on weak GPU without grid
                other = int(ti.random() * NUM_AGENTS)
                if i != other:
                    diff = p_i - self.pos[other]
                    dist = diff.norm()
                    if dist < NEIGHBOR_RADIUS:
                        sep += diff.normalized() / (dist + 0.001)

            # Apply Forces
            self.acc[i] += (sep * SEPARATION_FORCE) + target_force

        # Integration
        for i in range(NUM_AGENTS):
            self.vel[i] += self.acc[i]
            self.vel[i] *= 0.96 # Friction
            
            self.pos[i] += self.vel[i]
            self.acc[i] *= 0.0
        
        # Update transforms after position update
        # self.update_transforms() - Moved to main.py to avoid nested kernel call

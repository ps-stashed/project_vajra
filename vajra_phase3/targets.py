import taichi as ti
from config import *

@ti.data_oriented
class TargetGenerator:
    def __init__(self, target_field):
        self.target = target_field

    @ti.kernel
    def init_sphere(self):
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
    def init_cube(self):
        side = int(NUM_AGENTS**(1/3))
        if side == 0: side = 1
        spacing = 4.0 / side
        offset = 2.0
        for i in range(NUM_AGENTS):
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
    def init_smiley(self):
        head_count = int(NUM_AGENTS * 0.7)
        eye_count = int(NUM_AGENTS * 0.1)
        mouth_count = NUM_AGENTS - head_count - (2 * eye_count)
        phi = (1.0 + 5.0**0.5) / 2.0
        
        # Head
        for i in range(head_count):
            idx = float(i)
            y = 1 - (idx / float(head_count - 1)) * 2
            radius = (1 - y * y)**0.5
            theta = phi * idx
            x = ti.cos(theta) * radius
            z = ti.sin(theta) * radius
            self.target[i] = ti.Vector([x, y, z]) * 2.5

        # Left Eye
        for i in range(eye_count):
            idx = float(i)
            y = 1 - (idx / float(eye_count - 1)) * 2
            radius = (1 - y * y)**0.5
            theta = phi * idx
            x = ti.cos(theta) * radius * 0.5
            z = ti.sin(theta) * radius * 0.5
            self.target[head_count + i] = ti.Vector([x - 1.0, y + 1.0, z + 2.0])

        # Right Eye
        for i in range(eye_count):
            idx = float(i)
            y = 1 - (idx / float(eye_count - 1)) * 2
            radius = (1 - y * y)**0.5
            theta = phi * idx
            x = ti.cos(theta) * radius * 0.5
            z = ti.sin(theta) * radius * 0.5
            self.target[head_count + eye_count + i] = ti.Vector([x + 1.0, y + 1.0, z + 2.0])

        # Mouth
        for i in range(mouth_count):
            t = float(i) / float(mouth_count)
            angle = (t * 3.14159) + 3.14159
            x = ti.cos(angle) * 1.5
            y = ti.sin(angle) * 1.0 - 0.5
            z = 2.2
            self.target[head_count + 2*eye_count + i] = ti.Vector([x, y, z])

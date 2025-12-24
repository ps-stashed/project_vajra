import taichi as ti
import math
from config import *
from mesh_data import get_rhombic_dodecahedron_data

class Renderer:
    def __init__(self):
        self.window = ti.ui.Window("Project Vajra Phase 3: 3D GPU Swarm", (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.canvas = self.window.get_canvas()
        self.scene = self.window.get_scene()
        self.camera = ti.ui.Camera()
        
        self.gui = self.window.get_gui()
        
        # Camera State
        self.cam_yaw = 0.0
        self.cam_pitch = 0.0
        self.cam_dist = 15.0
        self.cam_pos = ti.Vector([0.0, 0.0, 15.0])
        self.cam_target = ti.Vector([0.0, 0.0, 0.0])
        self.prev_mouse = None
        
        # Mesh
        vertices, indices = get_rhombic_dodecahedron_data()
        vertices = vertices * VOXEL_SIZE
        self.mesh_vertices = ti.Vector.field(3, dtype=ti.f32, shape=len(vertices))
        self.mesh_indices = ti.field(dtype=ti.i32, shape=len(indices))
        self.mesh_vertices.from_numpy(vertices)
        self.mesh_indices.from_numpy(indices)

    def update_camera(self):
        # Manual Orbit Control
        mouse = self.window.get_cursor_pos()
        
        if self.window.is_pressed(ti.ui.RMB):
            if self.prev_mouse is None:
                self.prev_mouse = mouse
            
            dx = mouse[0] - self.prev_mouse[0]
            dy = mouse[1] - self.prev_mouse[1]
            
            self.cam_yaw -= dx * 3.0
            self.cam_pitch += dy * 3.0
            # Clamp pitch
            self.cam_pitch = max(-1.5, min(1.5, self.cam_pitch))
            
            self.prev_mouse = mouse
        else:
            self.prev_mouse = None

        # Zoom
        # Taichi UI doesn't expose scroll easily? We use W/S for zoom
        if self.window.is_pressed('w'): self.cam_dist -= 0.1
        if self.window.is_pressed('s'): self.cam_dist += 0.1
        self.cam_dist = max(0.1, self.cam_dist) # Allow getting very close

        # Calculate Position
        # Spherical coordinates
        x = self.cam_dist * math.cos(self.cam_pitch) * math.sin(self.cam_yaw)
        y = self.cam_dist * math.sin(self.cam_pitch)
        z = self.cam_dist * math.cos(self.cam_pitch) * math.cos(self.cam_yaw)
        
        self.cam_pos = ti.Vector([x, y, z])
        self.camera.position(x, y, z)
        self.camera.lookat(0, 0, 0)
        self.scene.set_camera(self.camera)

    def get_mouse_ray(self):
        mouse = self.window.get_cursor_pos() # (0..1, 0..1)
        
        # Basis Vectors
        forward = (self.cam_target - self.cam_pos).normalized()
        up = ti.Vector([0.0, 1.0, 0.0])
        right = forward.cross(up).normalized()
        real_up = right.cross(forward).normalized()
        
        # Screen Coordinates (-1 to 1)
        # Aspect Ratio
        aspect = WINDOW_WIDTH / WINDOW_HEIGHT
        fov = 60.0
        tan_half_fov = math.tan(math.radians(fov) / 2.0)
        
        screen_x = (mouse[0] - 0.5) * 2.0 * aspect * tan_half_fov
        screen_y = (mouse[1] - 0.5) * 2.0 * tan_half_fov
        
        # Ray Direction
        ray_dir = (forward + (right * screen_x) + (real_up * screen_y)).normalized()
        
        return self.cam_pos, ray_dir

    def render(self, physics):
        self.update_camera()
        
        # Lighting
        self.scene.point_light(pos=(0, 10, 10), color=(1, 1, 1))
        self.scene.ambient_light((0.1, 0.1, 0.1))
        
        # Draw Agents
        self.scene.mesh_instance(
            self.mesh_vertices,
            self.mesh_indices,
            transforms=physics.transforms,
            color=AGENT_COLOR
        )
        
        self.canvas.scene(self.scene)
        
        # UI
        self.gui.text("Controls:")
        self.gui.text("SPACE: Next Shape")
        self.gui.text("LMB: Blast (Raycast)")
        self.gui.text("RMB + Drag: Rotate")
        self.gui.text("W/S: Zoom")
        
        self.window.show()

    def handle_input(self, physics):
        if self.window.is_pressed(ti.ui.SPACE):
            physics.next_shape()
        
        if self.window.is_pressed(ti.ui.LMB):
            origin, direction = self.get_mouse_ray()
            physics.disrupt(origin, direction)
            
        return self.window.running

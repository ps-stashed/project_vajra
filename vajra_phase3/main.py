import taichi as ti
from physics import PhysicsEngine
from renderer import Renderer

# Initialize Taichi
ti.init(arch=ti.gpu)

def main():
    physics = PhysicsEngine()
    renderer = Renderer()
    
    running = True
    while running:
        # Input
        running = renderer.handle_input(physics)
        
        # Physics
        physics.update()
        physics.update_transforms()
        
        # Render
        renderer.render(physics)

if __name__ == "__main__":
    main()

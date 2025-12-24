import pygame
import sys
import random
from config import *
from voxel import Voxel

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Vajra: Decentralized Face Consensus v1.0")
    clock = pygame.time.Clock()
    
    # Spawn Agents
    voxels = []
    for i in range(NUM_AGENTS):
        v = Voxel(i, random.randint(50, SCREEN_WIDTH-50), random.randint(50, SCREEN_HEIGHT-50))
        voxels.append(v)

    running = True
    while running:
        # --- INPUT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # Reset
                    main()
                    return

        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())

        # --- UPDATE LOOP ---
        screen.fill(BG_COLOR)
        
        # Debug Grid (Optional Visual)
        if DEBUG_MODE:
            # Draw cursor vacuum range
            if mouse_pressed:
                pygame.draw.circle(screen, (50, 50, 50), (int(mouse_pos.x), int(mouse_pos.y)), 60, 1)

        # Update Voxels
        for v in voxels:
            v.update(voxels, mouse_pressed, mouse_pos)
            v.draw(screen)

        # --- DEBUG INFO ---
        font = pygame.font.SysFont("monospace", 15)
        solid_count = sum(1 for v in voxels if v.state == "SOLID")
        text = font.render(f"VOXELS: {NUM_AGENTS} | SOLID: {solid_count} | LIQUID: {NUM_AGENTS - solid_count}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

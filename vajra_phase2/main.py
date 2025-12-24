import pygame
import sys
from config import *
from agent import Agent
from target_manager import TargetManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Vajra Phase 2: Dynamic Image Reconstruction")
    clock = pygame.time.Clock()

    # Initialize Systems
    target_manager = TargetManager()
    
    # Spawn Agents
    agents = []
    for i in range(NUM_AGENTS):
        agents.append(Agent(i))

    running = True
    while running:
        # --- INPUT ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    target_manager.next_image()
                    # Wake up all agents to find new targets
                    for a in agents:
                        if a.state == "LOCKED":
                            a.state = "IDLE"
                            a.target = None

        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())

        # --- UPDATE ---
        screen.fill(BG_COLOR)

        # Draw Target Placeholders (Optional, faint outline)
        # for t in target_manager.targets:
        #     pygame.draw.rect(screen, (30, 30, 40), (t.pos.x, t.pos.y, GRID_SIZE, GRID_SIZE), 1)

        for agent in agents:
            agent.update(target_manager, mouse_pos, mouse_pressed)
            agent.draw(screen)

        # --- UI ---
        font = pygame.font.SysFont("monospace", 15)
        text = font.render(f"AGENTS: {NUM_AGENTS} | TARGETS: {len(target_manager.targets)} | [SPACE] Next Image", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

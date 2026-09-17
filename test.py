import sys
import pygame
from ui_economy import UIEconomy

# Initialize Pygame
pygame.init()

# Set up a 16:9 window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyberpunk Barista - UIEconomy Visual FX Tester")

clock = pygame.time.Clock()

# Initialize Economy System
economy = UIEconomy(screen)

print("\n--- TESTER CONTROLS ---")
print("[SPACE] : Complete Correct Order (+20 Credits, +30 XP)")
print("[W]     : Complete Incorrect Order (-$5 Waste Fee)")
print("[R]     : Reset Economy Data")
print("[ESC]   : Quit Tester\n")

running = True
while running:
    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # Simulate successful order completion
            elif event.key == pygame.K_SPACE:
                print("[TEST] Correct order served!")
                economy.serve_order(is_correct=True)

            # Simulate failed order
            elif event.key == pygame.K_w:
                print("[TEST] Incorrect order served!")
                economy.serve_order(is_correct=False)

            # Reset save state
            elif event.key == pygame.K_r:
                print("[TEST] Resetting economy data...")
                economy.reset_economy()

    # 2. Clear Screen with Dynamic Background Tint
    bg_color = economy.get_level_bg_color()
    screen.fill(bg_color)

    # 3. Draw Economy HUD Overlay & Visual FX
    economy.draw()

    # 4. Render Instructions Text Bottom Center
    font = pygame.font.SysFont("Consolas", 18)
    instructions = font.render(
        "PRESS: [SPACE] Correct Order | [W] Incorrect Order | [R] Reset | [ESC] Exit",
        True,
        (200, 200, 200),
    )
    instruct_rect = instructions.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
    )
    screen.blit(instructions, instruct_rect)

    # 5. Flip Display & Cap Framerate at 60 FPS
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
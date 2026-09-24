import pygame

from game_end_screen import GameEndScreen


pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Cyberpunk Café - End Screen Test")

end_screen = GameEndScreen(screen)

result = end_screen.run(
    player_name="BARISTA",
    level=3,
    successful_drinks=21,
    xp=450,
    credits=500,
)

print("[END SCREEN TEST] Result:", result)

pygame.quit()

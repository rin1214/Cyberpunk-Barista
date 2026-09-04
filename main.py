import pygame
import sys

from drink import Drink
from station import MixingStation

# Start Pygame
pygame.init()

# Configure the window size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyberpunk Barista - Game Engine")

#  Clock & FPS Engine
clock = pygame.time.Clock()
FPS = 60


# --------------------------------------------------
# Mahirah's Code of the - DRINK MIXING SYSTEM
# --------------------------------------------------

# Create the current drink
drink = Drink()

# Create the mixing station and connect it
# to the Drink object
mixing_station = MixingStation(drink)


# Main Game Loop
running = True
while running:

    # Delta Time Calculation 
    # clock.tick(60) caps game at 60 FPS and returns elapsed milliseconds.
    # Dividing by 1000.0 converts milliseconds into seconds (e.g., 0.016s).
    dt = clock.tick(FPS) / 1000.0

    # Event handling loop (checks for user inputs)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # User clicks the X button
            running = False

    # Paint the screen background dark gray (RGB: 20, 20, 30)
    screen.fill((20, 20, 30))


     # Draw Drink Mixing Station ( Mahirah)
    mixing_station.draw(screen)


    # Update the display to show what was drawn
    pygame.display.flip()



# Clean exit
pygame.quit()
sys.exit()
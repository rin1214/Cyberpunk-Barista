import sys
import pygame

from drink import Drink
from station import MixingStation

# Start Pygame
pygame.init()

# Configure the window size (16:9 Aspect Ratio)
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyberpunk Cafe - Game Engine (16:9)")

# Clock & FPS Engine
clock = pygame.time.Clock()
FPS = 60


# --------------------------------------------------
# CARD: background asset loader (NURIN)
# --------------------------------------------------
LEVEL_BACKGROUNDS = {
    1: "assets/places/cafe_lvl1.png",
    2: "assets/places/cafe_lvl2.png",
    3: "assets/places/cafe_lvl3.png",
}

bg_cache = {}


def load_level_background(level_num):
    """
    Safely loads, caches, and scales background PNG to 16:9 resolution (960x540).
    Prevents crashing if file is missing by returning a safe fallback surface.
    """
    if level_num in bg_cache:
        return bg_cache[level_num]

    path = LEVEL_BACKGROUNDS.get(level_num, LEVEL_BACKGROUNDS[1])
    try:
        raw_img = pygame.image.load(path).convert_alpha()
        # Scale image to match the 16:9 screen size
        scaled_img = pygame.transform.scale(raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_cache[level_num] = scaled_img
        print(f"[ASSET LOADER] Successfully loaded: {path}")
        return scaled_img
    except (pygame.error, FileNotFoundError) as e:
        # SAFE FALLBACK: Draw a dark purple canvas instead of crashing
        print(f"[SAFEGUARD WARNING] Could not find asset '{path}'. Using safe fallback color. ({e})")
        fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fallback.fill((25, 15, 35))  # Dark purple theme background
        bg_cache[level_num] = fallback
        return fallback


# Initial Game State
current_level = 1
active_bg = load_level_background(current_level)


# --------------------------------------------------
# Mahirah's Code - DRINK MIXING SYSTEM
# --------------------------------------------------

# Create the current drink
drink = Drink()

# Create the mixing station and connect it to the Drink object
mixing_station = MixingStation(drink)

# --------------------------------------------

# Main Game Loop
running = True
while running:

    # Delta Time Calculation (60 FPS Cap)
    dt = clock.tick(FPS) / 1000.0

    # Event handling loop (checks for user inputs)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # User clicks the X button
            running = False
            
        mixing_station.handle_event(event)

        # Debug Keybinds to test background level swapping (Press 1, 2, or 3)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_level = 1
                active_bg = load_level_background(1)
            elif event.key == pygame.K_2:
                current_level = 2
                active_bg = load_level_background(2)
            elif event.key == pygame.K_3:
                current_level = 3
                active_bg = load_level_background(3)

        # Safely pass events to mixing station
        try:
            mixing_station.handle_event(event)
        except Exception as e:
            print(f"[STATION ERROR] Event handling exception caught: {e}")

    # --------------------------------------------------
    # LAYERED RENDERING (Back to Front)
    # --------------------------------------------------

    # LAYER 1: Draw Active Background (PNG or Safe Fallback Surface)
    screen.blit(active_bg, (0, 0))

    # LAYER 2: Draw Drink Mixing Station (Mahirah's UI renders on top)
    try:
        mixing_station.draw(screen)
    except Exception as e:
        print(f"[STATION ERROR] Draw exception caught: {e}")

    # Update the display to show what was drawn
    pygame.display.flip()


# Clean exit
pygame.quit()
sys.exit()
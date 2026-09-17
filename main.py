import sys
import pygame

from drink import Drink
from station import MixingStation
from ui_economy import UIEconomy
from customer import Customer
from start_screen import StartScreen
from loading_screen import LoadingScreen

# Start Pygame Engine
pygame.init()

# Configure the window size
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
    Safely loads, caches, and scales background PNG to 16:9 resolution (1280x720).
    Prevents crashing if file is missing by returning a safe fallback surface.
    """
    if level_num in bg_cache:
        return bg_cache[level_num]

    path = LEVEL_BACKGROUNDS.get(level_num, LEVEL_BACKGROUNDS[1])
    try:
        raw_img = pygame.image.load(path).convert_alpha()
        scaled_img = pygame.transform.scale(raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_cache[level_num] = scaled_img
        print(f"[ASSET LOADER] Successfully loaded: {path}")
        return scaled_img
    except (pygame.error, FileNotFoundError) as e:
        print(
            f"[SAFEGUARD WARNING] Could not find asset '{path}'. Using safe fallback color. ({e})"
        )
        fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fallback.fill((25, 15, 35))
        bg_cache[level_num] = fallback
        return fallback


# ============================================================
# START SCREEN
# ============================================================
start_screen = StartScreen(screen)
player_name = start_screen.run()

# Player closed the start screen
if player_name is None:
    pygame.quit()
    sys.exit()

print(f"[PLAYER] Welcome to Cyberpunk Café, {player_name}!")

# ============================================================
# LOADING SCREEN
# ============================================================
economy = UIEconomy(screen=screen)
loading_screen = LoadingScreen(screen)

loading_ok = loading_screen.run(
    player_name=player_name,
    level=economy.level,
    duration=6.7
)

if not loading_ok:
    pygame.quit()
    sys.exit()

# --------------------------------------------------
# Mahirah's Code - DRINK MIXING SYSTEM
# --------------------------------------------------
drink = Drink()

# Create the mixing station and connect it to the Drink object
mixing_station = MixingStation(drink)


# Sync background and spawn first customer based on saved economy level
active_bg = load_level_background(economy.level)
active_customer = Customer(current_level=economy.level)


# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------
running = True
while running:

    # Delta Time Calculation (60 FPS Cap)
    dt = clock.tick(FPS) / 1000.0

    # Event handling loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Test Keybinds for Economy & Reset
            if event.key == pygame.K_c:
                # Test Correct Order (+20 Credits, +30 XP)
                economy.serve_order(is_correct=True)
                active_bg = load_level_background(economy.level)
            elif event.key == pygame.K_w:
                # Test Wrong Order (-5 Waste Fee, 0 XP)
                economy.serve_order(is_correct=False)
            elif event.key == pygame.K_r:
                # Reset economy back to Level 1
                economy.reset_economy()
                active_bg = load_level_background(economy.level)

        if event.type == pygame.KEYDOWN:
            # Reset Economy (R Key)
            if event.key == pygame.K_r:
                economy.reset_economy()
                mixing_station.reset()
                active_bg = load_level_background(economy.level)
                active_customer = Customer(current_level=economy.level)

            # Debug Level Swapping (1, 2, 3)
            elif event.key == pygame.K_1:
                economy.level = 1
                economy.location = economy.LOCATIONS[1]
                economy.save_economy_data()
                active_bg = load_level_background(1)
                active_customer = Customer(current_level=1)
            elif event.key == pygame.K_2:
                economy.level = 2
                economy.location = economy.LOCATIONS[2]
                economy.save_economy_data()
                active_bg = load_level_background(2)
                active_customer = Customer(current_level=2)
            elif event.key == pygame.K_3:
                economy.level = 3
                economy.location = economy.LOCATIONS[3]
                economy.save_economy_data()
                active_bg = load_level_background(3)

        # Safely pass events to mixing station
        try:
            mixing_station.handle_event(event)
        except Exception as e:
            print(f"[STATION ERROR] Event handling exception caught: {e}")

    # --------------------------------------------------
    # LAYERED RENDERING (Back to Front)
    # --------------------------------------------------

    # LAYER 1: Draw Nurin's Active Level Background Image
    screen.blit(active_bg, (0, 0))

    # LAYER 2: Draw Customer (Behind Counter, in front of BG)
    active_customer.draw(screen)

    # LAYER 3: Draw Drink Mixing Station
    try:
        mixing_station.draw(screen)
    except Exception as e:
        print(f"[STATION ERROR] Draw exception caught: {e}")

    # LAYER 4: Draw Neon Economy Overlay on Top
    economy.draw()

    # Refresh Screen
    pygame.display.flip()

# Clean exit
pygame.quit()
sys.exit()
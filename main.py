import sys
import pygame

from customer import Customer, CustomerState
from drink import Drink
from loading_screen import LoadingScreen
from start_screen import StartScreen
from station import MixingStation
from ui_economy import UIEconomy

# Start Pygame Engine
pygame.init()

# Configure the window size (16:9 Aspect Ratio)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyberpunk Barista - Game Engine (16:9)")

# Clock & FPS Engine
clock = pygame.time.Clock()
FPS = 60

# --------------------------------------------------
# BACKGROUND ASSET LOADER
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
        scaled_img = pygame.transform.scale(
            raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
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

if player_name is None:
    pygame.quit()
    sys.exit()

print(f"[PLAYER] Welcome to Cyberpunk Café, {player_name}!")

# ============================================================
# ECONOMY & LOADING SCREEN
# ============================================================
economy = UIEconomy(screen=screen, player_name=player_name)
loading_screen = LoadingScreen(screen)

loading_ok = loading_screen.run(
    player_name=player_name, level=economy.level, duration=6.7
)

if not loading_ok:
    pygame.quit()
    sys.exit()

# --------------------------------------------------
# DRINK MIXING SYSTEM & CUSTOMER INITIALIZATION
# --------------------------------------------------
drink = Drink()
mixing_station = MixingStation(drink)

active_bg = load_level_background(economy.level)
active_customer = Customer(current_level=economy.level)

# Spawning Engine Control Flags
spawn_timer = 0.0
SPAWN_DELAY = 1.5  # Time delay (seconds) before new customer enters


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

        # Pass events to mixing station
        try:
            mixing_station.handle_event(event)
        except Exception as e:
            print(f"[STATION ERROR] Event handling exception caught: {e}")

        if event.type == pygame.KEYDOWN:
            # Reset Economy (R Key)
            if event.key == pygame.K_r:
                economy.reset_economy()
                mixing_station.reset()
                active_bg = load_level_background(economy.level)
                active_customer = Customer(current_level=economy.level)
                spawn_timer = 0.0

            # Debug Level Swapping (1, 2, 3 Keys)
            elif event.key == pygame.K_1:
                economy.level = 1
                economy.location = economy.LOCATIONS[1]
                economy.save_economy_data()
                active_bg = load_level_background(1)
                active_customer = Customer(current_level=1)
                spawn_timer = 0.0
            elif event.key == pygame.K_2:
                economy.level = 2
                economy.location = economy.LOCATIONS[2]
                economy.save_economy_data()
                active_bg = load_level_background(2)
                active_customer = Customer(current_level=2)
                spawn_timer = 0.0
            elif event.key == pygame.K_3:
                economy.level = 3
                economy.location = economy.LOCATIONS[3]
                economy.save_economy_data()
                active_bg = load_level_background(3)
                active_customer = Customer(current_level=3)
                spawn_timer = 0.0

    # --------------------------------------------------
    # 1. SERVE DRINK EVALUATION
    # --------------------------------------------------
    if mixing_station.served:
        if active_customer and active_customer.state == CustomerState.WAITING:
            is_correct = active_customer.serve_drink(drink.get_data())

            old_level = economy.level
            economy.serve_order(is_correct=is_correct)

            # Level Up Transition
            if economy.level > old_level:
                print(
                    f"[LEVEL UP] Level {economy.level} unlocked: {economy.location}"
                )
                loading_screen = LoadingScreen(screen)
                loading_ok = loading_screen.run(
                    player_name=player_name, level=economy.level, duration=6.7
                )
                if not loading_ok:
                    running = False

        mixing_station.reset()

    # --------------------------------------------------
    # 2. UPDATE CUSTOMER FSM & QUEUE SPAWNING ENGINE
    # --------------------------------------------------
    if active_customer:
        old_state = active_customer.state
        active_customer.update(dt)

        # Catch Patience Expiration
        if (
            old_state == CustomerState.WAITING
            and active_customer.state == CustomerState.LEAVING
        ):
            economy.serve_order(is_correct=False)
            mixing_station.reset()

        # CLEANUP: Once customer finishes sliding off screen, remove them
        if active_customer.is_finished():
            active_customer = None
            spawn_timer = SPAWN_DELAY

    else:
        # SPAWNING ENGINE: Delay countdown before sliding in next customer
        spawn_timer -= dt
        if spawn_timer <= 0:
            active_bg = load_level_background(economy.level)
            active_customer = Customer(current_level=economy.level)

    # --------------------------------------------------
    # 3. LAYERED RENDERING
    # --------------------------------------------------
    # LAYER 1: Level Background
    screen.blit(active_bg, (0, 0))

    # LAYER 2: Customer Sprite & Speech Bubble
    if active_customer:
        active_customer.draw(screen)

    # LAYER 3: Mixing Station UI
    try:
        mixing_station.draw(screen)
    except Exception as e:
        print(f"[STATION ERROR] Draw exception caught: {e}")

    # LAYER 4: Neon Economy & Level UI
    economy.draw()

    # Refresh Screen
    pygame.display.flip()

# Clean exit
pygame.quit()
sys.exit()
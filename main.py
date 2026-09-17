import sys
import pygame

from drink import Drink
from station import MixingStation
from ui_economy import UIEconomy
from customer import Customer
from start_screen import StartScreen

# Start Pygame Engine
pygame.init()

# Configure the window size (16:9 Aspect Ratio)
SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyberpunk Cafe - Game Engine")

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

# --------------------------------------------------
# SYSTEM INITIALIZATION
# --------------------------------------------------
drink = Drink()
mixing_station = MixingStation(drink)
economy = UIEconomy(screen=screen)

# Sync background and spawn first customer based on saved economy level
active_bg = load_level_background(economy.level)
active_customer = Customer(current_level=economy.level)


# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------
running = True
while running:

    # Delta Time Calculation
    dt = clock.tick(FPS) / 1000.0

    # Event handling loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Pass event to mixing station (handles button clicks on +/- and Serve)
        mixing_station.handle_event(event)

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
                active_customer = Customer(current_level=3)

    # 1. Check if "SERVE DRINK" UI button was clicked on the mixing station
    if mixing_station.served:
        drink_data = drink.get_data()

        # INPUT ADAPTER: Maps slider inputs (>50 -> target range center)
        # Bridges mixing_station sliders with customer.py's internal targets
        adjusted_drink = {
            "sweetness": active_customer.target_sweetness if (drink_data.get("sweetness", 50) > 50) == (active_customer.target_sweetness > 50) else 0,
            "caffeine": active_customer.target_caffeine if (drink_data.get("caffeine", 50) > 50) == (active_customer.target_caffeine > 50) else 0,
            "temperature": active_customer.target_temperature if (drink_data.get("temperature", 50) > 50) == (active_customer.target_temperature > 50) else 0,
        }

        # Verify using adjusted dictionary so customer.py tolerance checks pass
        is_correct = active_customer.verify_order(adjusted_drink)

        # --- LOGGING OUTCOME ---
        print("\n" + "=" * 40)
        print(f"[ORDER EVALUATION] Dialogue Prompt: {active_customer.dialogue}")
        print(f"[ORDER EVALUATION] Raw Sliders: {drink_data}")
        print(
            f"[ORDER EVALUATION] Result: {'CORRECT (+20 Credits, +30 XP)' if is_correct else 'WRONG (-$10 Fee, +0 XP)'}"
        )
        print("=" * 40 + "\n")

        # Pass true boolean to UIEconomy
        economy.serve_order(is_correct=bool(is_correct))

        # Reset station states
        mixing_station.served = False
        mixing_station.reset()

        # Update background and spawn next customer
        active_bg = load_level_background(economy.level)
        active_customer = Customer(current_level=economy.level)

    # 2. Update Customer Patience Timer
    active_customer.update(dt)

    # 3. Check if Customer Patience Expired
    if active_customer.is_leaving:
        # Customer left unsatisfied: Apply -$10 waste fee and spawn next customer
        economy.serve_order(is_correct=False)
        mixing_station.reset()
        active_customer = Customer(current_level=economy.level)

    # LAYER 1: Draw Active Level Background Image
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
import sys
import os
import pygame

from customer import Customer, CustomerState
from drink import Drink
from level_unlock_screen import LevelUnlockScreen
from loading_screen import LoadingScreen
from start_screen import StartScreen
from station import MixingStation
from ui_economy import UIEconomy
from map_manager import MapManager
from map_screen import MapScreen  # Added clickable map screen
from leaderboard_manager import LeaderboardManager
from leaderboard_screen import LeaderboardScreen

# Start Pygame Engine
pygame.init()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyberpunk Barista - Game Engine (16:9)")

clock = pygame.time.Clock()
FPS = 60

LEVEL_BACKGROUNDS = {
    1: "assets/places/cafe_lvl1.png",
    2: "assets/places/cafe_lvl2.png",
    3: "assets/places/cafe_lvl3.png",
}

bg_cache = {}

def load_level_background(level_num):
    if level_num in bg_cache:
        return bg_cache[level_num]

    relative_path = LEVEL_BACKGROUNDS.get(level_num, LEVEL_BACKGROUNDS[1])
    path = os.path.join(PROJECT_ROOT, relative_path)
    try:
        raw_img = pygame.image.load(path).convert_alpha()
        scaled_img = pygame.transform.scale(raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_cache[level_num] = scaled_img
        return scaled_img
    except (pygame.error, FileNotFoundError):
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

# ============================================================
# ECONOMY, MAP MANAGER, LEADERBOARD & LOADING SCREEN
# ============================================================
economy = UIEconomy(screen=screen, player_name=player_name)
map_manager = MapManager(economy_ref=economy)
leaderboard_manager = LeaderboardManager(economy_ref=economy)
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

spawn_timer = 0.0
SPAWN_DELAY = 1.5

# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        try:
            mixing_station.handle_event(event)
        except Exception as e:
            print(f"[STATION ERROR] Event handling exception caught: {e}")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                economy.reset_economy()
                mixing_station.reset()
                active_bg = load_level_background(economy.level)
                active_customer = Customer(current_level=economy.level)
                spawn_timer = 0.0
            
            # Press 'M' to open the interactive, clickable district map
            elif event.key == pygame.K_m:
                map_screen = MapScreen(screen, map_manager, economy)
                map_screen.run()
                # Refresh background and customer after closing the map
                active_bg = load_level_background(economy.level)
                active_customer = Customer(current_level=economy.level)
                spawn_timer = 0.0

            # Press 'L' to open the interactive, clickable leaderboard screen
            elif event.key == pygame.K_l:
                lb_screen = LeaderboardScreen(screen, leaderboard_manager, economy)
                lb_screen.run()
                active_bg = load_level_background(economy.level)
                active_customer = Customer(current_level=economy.level)
                spawn_timer = 0.0

            elif event.key == pygame.K_1:
                if map_manager.nodes["neon_alley"].is_unlocked:
                    economy.level = 1
                    economy.location = economy.LOCATIONS[1]
                    active_bg = load_level_background(1)
                    active_customer = Customer(current_level=1)
                    spawn_timer = 0.0

            elif event.key == pygame.K_2:
                node = map_manager.nodes["cyber_dock"]
                if node.is_unlocked:
                    economy.level = 2
                    economy.location = economy.LOCATIONS[2]
                    economy.save_economy_data()
                    active_bg = load_level_background(2)
                    active_customer = Customer(current_level=2)
                    spawn_timer = 0.0

            elif event.key == pygame.K_3:
                node = map_manager.nodes["high_rise"]
                if node.is_unlocked:
                    economy.level = 3
                    economy.location = economy.LOCATIONS[3]
                    economy.save_economy_data()
                    active_bg = load_level_background(3)
                    active_customer = Customer(current_level=3)
                    spawn_timer = 0.0

    if mixing_station.served:
        if active_customer and active_customer.state == CustomerState.WAITING:
            is_correct = active_customer.serve_drink(drink.get_data())
            economy.serve_order(is_correct=is_correct)
        mixing_station.reset()

    if active_customer:
        old_state = active_customer.state
        active_customer.update(dt)

        if (
            old_state == CustomerState.WAITING
            and active_customer.state == CustomerState.LEAVING
        ):
            economy.serve_order(is_correct=is_correct)
            mixing_station.reset()

        if active_customer.is_finished():
            active_customer = None
            spawn_timer = SPAWN_DELAY
    else:
        spawn_timer -= dt
        if spawn_timer <= 0:
            active_bg = load_level_background(economy.level)
            active_customer = Customer(current_level=economy.level)

    screen.blit(active_bg, (0, 0))

    if active_customer:
        active_customer.draw(screen)

    try:
        mixing_station.draw(screen)
    except Exception as e:
        print(f"[STATION ERROR] {e}")

    economy.draw()
    pygame.display.flip()

pygame.quit()
sys.exit()
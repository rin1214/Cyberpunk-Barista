import sys
import os
import pygame
from audio_manager import AudioManager

from customer import Customer, CustomerState
from drink import Drink
from level_unlock_screen import LevelUnlockScreen
from loading_screen import LoadingScreen
from start_screen import StartScreen
from station import MixingStation
from ui_economy import UIEconomy
from progression import Progression
from rewards import RewardSystem
from accuracy import OrderAccuracy
from map_manager import MapManager
from map_screen import MapScreen
from leaderboard_manager import LeaderboardManager
from leaderboard_screen import LeaderboardScreen

pygame.init()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyberpunk Café - Game Engine")

audio_manager = AudioManager(project_root=PROJECT_ROOT)

clock = pygame.time.Clock()
FPS = 60

LEVEL_BACKGROUNDS = {
    1: "assets/places/cafe_lvl1.png",
    2: "assets/places/cafe_lvl2.png",
    3: "assets/places/cafe_lvl3.png",
}

bg_cache = {}


def load_level_background(level_num):
    """Load and scale the background image for the given level."""
    try:
        level_num = int(level_num)
    except (TypeError, ValueError):
        level_num = 1
    level_num = max(1, min(level_num, 3))

    if level_num in bg_cache:
        return bg_cache[level_num]

    relative_path = LEVEL_BACKGROUNDS.get(level_num, LEVEL_BACKGROUNDS[1])
    path = os.path.join(PROJECT_ROOT, relative_path)

    try:
        raw_image = pygame.image.load(path).convert_alpha()
        scaled_image = pygame.transform.smoothscale(
            raw_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        bg_cache[level_num] = scaled_image
        return scaled_image
    except (pygame.error, FileNotFoundError) as error:
        print(f"[MAIN] Could not load background {path}: {error}")
        fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fallback.fill((25, 15, 35))
        bg_cache[level_num] = fallback
        return fallback


MUSIC_FILE = os.path.join(
    PROJECT_ROOT, "assets", "mahirah", "audio", "cyberpunk_cafe_theme.wav"
)


def ensure_game_music(start_screen=None):
    """Ensure background music is playing without restarting it unnecessarily."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        volume = 0.30
        muted = False

        if start_screen is not None:
            try:
                volume = float(getattr(start_screen, "music_volume", 0.30))
            except (TypeError, ValueError):
                volume = 0.30
            muted = bool(getattr(start_screen, "muted", False))

        volume = max(0.0, min(volume, 1.0))
        pygame.mixer.music.set_volume(0.0 if muted else volume)

        if pygame.mixer.music.get_busy():
            return True

        if not os.path.exists(MUSIC_FILE):
            return False

        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play(-1)
        return True
    except pygame.error as error:
        print(f"[AUDIO ERROR] {error}")
        return False


def position_customer(customer):
    """Set the customer's initial spawn position."""
    if customer is None:
        return
    try:
        customer_x = 180
        counter_bottom = 690

        customer.x = customer_x
        customer.y_counter = counter_bottom
        customer.spawn_y = counter_bottom + 120
        customer.current_y = customer.spawn_y

        if hasattr(customer, "rect"):
            customer.rect.centerx = customer_x
            customer.rect.bottom = int(customer.current_y)
    except Exception as error:
        print(f"[MAIN] Customer positioning warning: {error}")


def create_customer(level):
    customer = Customer(current_level=level)
    position_customer(customer)
    return customer


def sync_station_order(mixing_station, customer):
    if customer is None:
        return
    order = getattr(customer, "order", None)
    if order is None:
        order = getattr(customer, "current_order", None)
    if order is not None:
        mixing_station.set_customer_order(order)


def refresh_customer(level, mixing_station):
    customer = create_customer(level)
    sync_station_order(mixing_station, customer)
    return customer


def sync_level_systems(economy, progression, mixing_station):
    try:
        economy.sync_progression(progression)
    except Exception as error:
        print(f"[MAIN] Economy sync warning: {error}")

    if mixing_station is not None:
        try:
            mixing_station.set_progression(progression)
        except Exception as error:
            print(f"[MAIN] Station progression sync warning: {error}")
        try:
            mixing_station.set_level(progression.level)
        except Exception as error:
            print(f"[MAIN] Station level sync warning: {error}")


def open_map(screen, map_manager, economy, progression, mixing_station):
    print("[MAIN] Opening Map.")
    map_screen = MapScreen(screen, map_manager, economy)
    map_screen.run()

    try:
        progression.level = max(1, min(int(economy.level), 3))
    except Exception:
        progression.level = 1
    try:
        progression.xp = max(0, int(economy.xp))
    except Exception:
        progression.xp = 0

    sync_level_systems(economy, progression, mixing_station)
    active_bg = load_level_background(progression.level)
    active_customer = refresh_customer(progression.level, mixing_station)
    ensure_game_music()
    return active_bg, active_customer


def open_leaderboard(screen, leaderboard_manager, economy, progression, mixing_station):
    print("[MAIN] Opening Leaderboard.")
    leaderboard_screen = LeaderboardScreen(screen, leaderboard_manager, economy)
    leaderboard_screen.run()

    try:
        progression.level = max(1, min(int(economy.level), 3))
    except Exception:
        progression.level = 1
    try:
        progression.xp = max(0, int(economy.xp))
    except Exception:
        progression.xp = 0

    sync_level_systems(economy, progression, mixing_station)
    active_bg = load_level_background(progression.level)
    active_customer = refresh_customer(progression.level, mixing_station)
    ensure_game_music()
    return active_bg, active_customer


def switch_level(level, economy, progression, mixing_station):
    try:
        level = int(level)
    except (TypeError, ValueError):
        level = 1
    level = max(1, min(level, 3))

    economy.set_level(level)
    progression.level = level

    sync_level_systems(economy, progression, mixing_station)
    active_bg = load_level_background(level)
    active_customer = refresh_customer(level, mixing_station)
    return active_bg, active_customer


# Start Screen Initialization
start_screen = StartScreen(screen)
player_name = start_screen.run()

if player_name is None:
    pygame.quit()
    sys.exit()

ensure_game_music(start_screen)

economy = UIEconomy(screen=screen, player_name=player_name)
progression = Progression(level=economy.level, xp=economy.xp)
progression.level = max(1, min(int(progression.level), 3))

reward_system = RewardSystem()
map_manager = MapManager(economy_ref=economy)
leaderboard_manager = LeaderboardManager(economy_ref=economy)
level_unlock_screen = LevelUnlockScreen(screen)
loading_screen = LoadingScreen(screen)

sync_level_systems(economy, progression, None)

ensure_game_music(start_screen)
loading_ok = loading_screen.run(
    player_name=player_name, level=progression.level, duration=6.7
)
if not loading_ok:
    pygame.quit()
    sys.exit()

ensure_game_music(start_screen)

drink = Drink()
mixing_station = MixingStation(
    drink=drink,
    level=progression.level,
    progression=progression,
    rewards=reward_system,
    economy=economy,
)

sync_level_systems(economy, progression, mixing_station)

active_bg = load_level_background(progression.level)
active_customer = refresh_customer(progression.level, mixing_station)

spawn_timer = 0.0
SPAWN_DELAY = 1.5

# Main Game Loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    if not pygame.mixer.music.get_busy():
        ensure_game_music(start_screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        try:
            mixing_station.handle_event(event)
        except Exception as error:
            print(f"[STATION ERROR] {error}")

        try:
            if mixing_station.consume_map_request():
                active_bg, active_customer = open_map(
                    screen, map_manager, economy, progression, mixing_station
                )
                spawn_timer = 0.0
        except Exception as error:
            print(f"[MAP ERROR] {error}")

        try:
            if mixing_station.consume_leaderboard_request():
                active_bg, active_customer = open_leaderboard(
                    screen, leaderboard_manager, economy, progression, mixing_station
                )
                spawn_timer = 0.0
        except Exception as error:
            print(f"[LEADERBOARD ERROR] {error}")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print("[MAIN] Resetting game...")
                try:
                    economy.reset_economy()
                    progression.reset()
                    reward_system.reset()
                    mixing_station.reset()
                except Exception as error:
                    print(f"[MAIN] Reset warning: {error}")

                progression.level = economy.level
                progression.xp = economy.xp
                sync_level_systems(economy, progression, mixing_station)
                active_bg = load_level_background(progression.level)
                active_customer = refresh_customer(progression.level, mixing_station)
                spawn_timer = 0.0

            elif event.key == pygame.K_m:
                active_bg, active_customer = open_map(
                    screen, map_manager, economy, progression, mixing_station
                )
                spawn_timer = 0.0

            elif event.key == pygame.K_l:
                active_bg, active_customer = open_leaderboard(
                    screen, leaderboard_manager, economy, progression, mixing_station
                )
                spawn_timer = 0.0

            elif event.key == pygame.K_1:
                node = map_manager.nodes.get("neon_alley")
                if node is not None and node.is_unlocked:
                    active_bg, active_customer = switch_level(
                        1, economy, progression, mixing_station
                    )
                    spawn_timer = 0.0

            elif event.key == pygame.K_2:
                node = map_manager.nodes.get("cyber_dock")
                if node is not None and node.is_unlocked:
                    active_bg, active_customer = switch_level(
                        2, economy, progression, mixing_station
                    )
                    spawn_timer = 0.0

            elif event.key == pygame.K_3:
                node = map_manager.nodes.get("high_rise")
                if node is not None and node.is_unlocked:
                    active_bg, active_customer = switch_level(
                        3, economy, progression, mixing_station
                    )
                    spawn_timer = 0.0

    try:
        mixing_station.update(dt)
    except Exception as error:
        print(f"[STATION UPDATE ERROR] {error}")

    if mixing_station.served:
        if active_customer is not None:
            if active_customer.state == CustomerState.WAITING:
                player_drink_data = mixing_station.get_player_drink_data()
                customer_order = getattr(active_customer, "order", None)
                if customer_order is None:
                    customer_order = getattr(active_customer, "current_order", None)

                accuracy_result = OrderAccuracy.check_order(
                    customer_order, player_drink_data
                )

                try:
                    served_quickly = active_customer.served_quickly()
                except Exception:
                    served_quickly = False

                reward_result = reward_system.calculate_reward(
                    accuracy_result, served_quickly=served_quickly
                )

                # Track XP/Credits for economy & leaderboard, but DO NOT trigger level ups automatically.
                progression.add_xp(reward_result.total_xp)

                try:
                    economy.apply_reward(reward_result)
                except Exception as error:
                    print(f"[ECONOMY] Reward warning: {error}")

                try:
                    economy.sync_progression(progression)
                    mixing_station.set_progression(progression)
                    mixing_station.set_level(progression.level)
                    economy.save_economy_data()
                except Exception as error:
                    print(f"[MAIN] Sync/Save warning: {error}")

                try:
                    active_customer.serve_drink(player_drink_data)
                except Exception as error:
                    print(f"[CUSTOMER] Serve reaction warning: {error}")

                try:
                    mixing_station.set_reward_feedback(
                        xp_delta=reward_result.total_xp,
                        credit_delta=reward_result.net_credits,
                    )
                except Exception as error:
                    print(f"[HUD] Reward feedback warning: {error}")

                print("----------------------------------------")
                print("[ORDER COMPLETE]")
                print(f"Accuracy: {accuracy_result.correct_count}/{accuracy_result.total_count} ({accuracy_result.percentage:.0f}%)")
                print(f"XP Earned: {reward_result.total_xp:+}")
                print(f"Credits Change: {reward_result.net_credits:+}")
                print("----------------------------------------")

        if running:
            try:
                mixing_station.reset()
            except Exception as error:
                print(f"[STATION RESET ERROR] {error}")

    if running and active_customer is not None:
        old_state = active_customer.state
        try:
            active_customer.update(dt)
        except Exception as error:
            print(f"[CUSTOMER UPDATE ERROR] {error}")

        if (
            old_state == CustomerState.WAITING
            and active_customer.state == CustomerState.LEAVING
        ):
            print("[CUSTOMER] Customer left without receiving correct drink.")
            try:
                mixing_station.reset()
            except Exception:
                pass

        try:
            if active_customer.is_finished():
                active_customer = None
                spawn_timer = SPAWN_DELAY
        except Exception as error:
            print(f"[CUSTOMER FINISHED ERROR] {error}")

    if running and active_customer is None:
        spawn_timer -= dt
        if spawn_timer <= 0:
            active_bg = load_level_background(progression.level)
            active_customer = refresh_customer(progression.level, mixing_station)
            spawn_timer = 0.0

    if not running:
        break

    screen.blit(active_bg, (0, 0))

    if active_customer is not None:
        try:
            active_customer.draw(screen)
        except Exception as error:
            print(f"[CUSTOMER DRAW ERROR] {error}")

    try:
        mixing_station.draw(screen)
    except Exception as error:
        print(f"[STATION DRAW ERROR] {error}")

    pygame.display.flip()

print("[MAIN] Shutting down Cyberpunk Café.")
try:
    audio_manager.shutdown()
except Exception:
    pass
pygame.quit()
sys.exit()
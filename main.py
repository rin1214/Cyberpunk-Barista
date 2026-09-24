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
    """Syncs player level & XP across Economy, Progression, and MixingStation components."""
    if economy is not None and progression is not None:
        try:
            economy.sync_progression(progression)
        except Exception as error:
            print(f"[MAIN] Economy sync warning: {error}")

    if mixing_station is not None and progression is not None:
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

# Ensure level retrieved from economy correctly parses as an integer up to level 3
try:
    current_saved_level = int(economy.level)
except (ValueError, TypeError):
    current_saved_level = 1
current_saved_level = max(1, min(current_saved_level, 3))

progression = Progression(level=current_saved_level, xp=economy.xp)
progression.level = current_saved_level

reward_system = RewardSystem()
map_manager = MapManager(economy_ref=economy)

# Force unlocks on map manager if level requirements are met
if progression.level >= 2 and "cyber_dock" in map_manager.nodes:
    map_manager.nodes["cyber_dock"].is_unlocked = True
if progression.level >= 3 and "high_rise" in map_manager.nodes:
    map_manager.nodes["high_rise"].is_unlocked = True

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

# Disable redundant top header on mixing station if supported
if hasattr(mixing_station, "show_header"):
    mixing_station.show_header = False
if hasattr(mixing_station, "draw_header"):
    mixing_station.draw_header = False

sync_level_systems(economy, progression, mixing_station)

active_bg = load_level_background(progression.level)
active_customer = refresh_customer(progression.level, mixing_station)

spawn_timer = 0.0
SPAWN_DELAY = 1.5

# --- Pause Menu State & Styling Variables ---
is_paused = False
font_title = pygame.font.SysFont("Arial", 42, bold=True)
font_button = pygame.font.SysFont("Arial", 26, bold=True)

pause_panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 150, 440, 300)
resume_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 - 35, 340, 56)
exit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 35, 340, 56)

CYAN = (75, 225, 255)
PINK = (255, 80, 190)
WHITE = (245, 248, 255)
PANEL_BG = (12, 18, 40)

# Main Game Loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    if not pygame.mixer.music.get_busy():
        ensure_game_music(start_screen)

    # Safely retrieve active combo multiplier from reward_system or fallback to 1
    current_combo = getattr(reward_system, "combo", getattr(reward_system, "combo_multiplier", 1))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        # Toggle pause state with ESC key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_paused = not is_paused
                continue

        # Handle Pause Menu Mouse Clicks
        if is_paused:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if resume_button_rect.collidepoint(mouse_pos):
                    is_paused = False
                elif exit_button_rect.collidepoint(mouse_pos):
                    running = False
            continue  # Skip all gameplay events while paused

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
                if node is None or node.is_unlocked or progression.level >= 1:
                    active_bg, active_customer = switch_level(
                        1, economy, progression, mixing_station
                    )
                    spawn_timer = 0.0

            elif event.key == pygame.K_2:
                node = map_manager.nodes.get("cyber_dock")
                if (node is not None and node.is_unlocked) or progression.level >= 2:
                    active_bg, active_customer = switch_level(
                        2, economy, progression, mixing_station
                    )
                    spawn_timer = 0.0

            elif event.key == pygame.K_3:
                node = map_manager.nodes.get("high_rise")
                if (node is not None and node.is_unlocked) or progression.level >= 3:
                    active_bg, active_customer = switch_level(
                        3, economy, progression, mixing_station
                    )
                    spawn_timer = 0.0

    # Skip updating game physics/timers if paused
    if is_paused:
        screen.blit(active_bg, (0, 0))
        if active_customer is not None:
            active_customer.draw(screen)
        mixing_station.draw(screen)
        economy.draw(combo_count=current_combo, dt=dt)

        # Draw Pause Menu Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 20, 190))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, PANEL_BG, pause_panel_rect, border_radius=14)
        pygame.draw.rect(screen, CYAN, pause_panel_rect, width=2, border_radius=14)

        title_surf = font_title.render("GAME PAUSED", True, CYAN)
        screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, pause_panel_rect.y + 45)))

        mouse_pos = pygame.mouse.get_pos()

        # Resume Button
        resume_hover = resume_button_rect.collidepoint(mouse_pos)
        resume_color = PINK if resume_hover else CYAN
        pygame.draw.rect(screen, (30, 20, 50), resume_button_rect, border_radius=10)
        pygame.draw.rect(screen, resume_color, resume_button_rect, width=2, border_radius=10)
        resume_text = font_button.render("RESUME GAME", True, WHITE)
        screen.blit(resume_text, resume_text.get_rect(center=resume_button_rect.center))

        # Exit Button
        exit_hover = exit_button_rect.collidepoint(mouse_pos)
        exit_color = PINK if exit_hover else CYAN
        pygame.draw.rect(screen, (30, 20, 50), exit_button_rect, border_radius=10)
        pygame.draw.rect(screen, exit_color, exit_button_rect, width=2, border_radius=10)
        exit_text = font_button.render("EXIT TO DESKTOP", True, WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))

        pygame.display.flip()
        continue

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

                # Pass current level into calculate_reward to scale combo bar XP properly
                reward_result = reward_system.calculate_reward(
                    accuracy_result,
                    served_quickly=served_quickly,
                    level=progression.level
                )

                progression.add_xp(reward_result.total_xp)

                try:
                    economy.apply_reward(reward_result)
                except Exception as error:
                    print(f"[ECONOMY] Reward warning: {error}")

                try:
                    sync_level_systems(economy, progression, mixing_station)
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

    # --- RENDER STEP ---
    screen.blit(active_bg, (0, 0))

    if active_customer is not None:
        try:
            active_customer.draw(screen)
        except Exception as error:
            print(f"[CUSTOMER DRAW ERROR] {error}")

    # Draw mixing station interactive elements first
    try:
        mixing_station.draw(screen)
    except Exception as error:
        print(f"[STATION DRAW ERROR] {error}")

    # Draw single active UIEconomy HUD on top
    try:
        economy.draw(combo_count=current_combo, dt=dt)
    except Exception as error:
        print(f"[UI ECONOMY DRAW ERROR] {error}")

    pygame.display.flip()

print("[MAIN] Shutting down Cyberpunk Café.")
try:
    audio_manager.shutdown()
except Exception:
    pass
pygame.quit()
sys.exit()
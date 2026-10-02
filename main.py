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
from progression import Progression
from rewards import RewardSystem
from accuracy import OrderAccuracy
from map_manager import MapManager
from map_screen import MapScreen
from leaderboard_manager import LeaderboardManager
from leaderboard_screen import LeaderboardScreen
from game_end_screen import GameEndScreen
from mini_challenges import MiniChallenge
from order_scene import OrderScene
from barista_selection import choose_barista

pygame.init()
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyberpunk Café - Game Engine")
clock = pygame.time.Clock()
FPS = 60

LEVEL_BACKGROUNDS = {
    1: "assets/places/cafe_lvl1.png",
    2: "assets/places/cafe_lvl2.png",
    3: "assets/places/cafe_lvl3.png",
}
bg_cache = {}

def load_level_background(level_num):
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
        scaled_image = pygame.transform.smoothscale(raw_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_cache[level_num] = scaled_image
        return scaled_image
    except (pygame.error, FileNotFoundError) as error:
        print(f"[MAIN] Could not load background {path}: {error}")
        fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fallback.fill((25, 15, 35))
        bg_cache[level_num] = fallback
        return fallback

MUSIC_FILE = os.path.join(PROJECT_ROOT, "assets", "audio", "cyberpunk_cafe_theme.wav")

def ensure_game_music(start_screen=None):
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
        else:
            # Keep the volume chosen in the F menu instead of resetting it to 30%
            station = globals().get("mixing_station")
            if station is not None:
                try:
                    volume = float(getattr(station, "music_volume", volume))
                except (TypeError, ValueError):
                    pass
                muted = bool(getattr(station, "music_muted", False))
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
    if economy is not None and progression is not None:
        try:
            economy.xp = max(0, int(progression.xp))
        except (TypeError, ValueError, AttributeError) as error:
            print(f"[MAIN] Economy XP sync warning: {error}")
    if mixing_station is not None and progression is not None:
        try:
            mixing_station.set_progression(progression)
        except Exception as error:
            print(f"[MAIN] Station progression sync warning: {error}")
        try:
            mixing_station.set_level(progression.level)
        except Exception as error:
            print(f"[MAIN] Station level sync warning: {error}")

def sync_saved_progress(economy, progression):
    try:
        level = max(1, min(int(economy.level), 3))
    except Exception:
        level = 1
    try:
        progression.xp = max(0, int(economy.xp))
    except Exception:
        progression.xp = 0
    return level

def open_map(screen, map_manager, economy, progression, mixing_station, active_customer):
    print("[MAIN] Opening Map.")
    old_level = progression.level
    map_screen = MapScreen(screen, map_manager, economy)
    map_screen.run()
    new_level = sync_saved_progress(economy, progression)
    if new_level > old_level:
        active_bg, new_customer = run_level_transition(
            new_level, economy, progression, mixing_station, economy.player_name
        )
        return active_bg, new_customer
    progression.level = new_level
    # Keep the mixing station's drink availability in sync with the
    # level selected on the map. This ensures Level 1 shows only the
    # first 3 drinks and Level 2 shows only the first 6 drinks.
    sync_level_systems(economy, progression, mixing_station)
    active_bg = load_level_background(progression.level)
    if active_customer is not None:
        sync_station_order(mixing_station, active_customer)
    ensure_game_music()
    return active_bg, active_customer

def open_leaderboard(screen, leaderboard_manager, economy, progression, mixing_station, active_customer):
    print("[MAIN] Opening Leaderboard.")
    leaderboard_screen = LeaderboardScreen(screen, leaderboard_manager, economy)
    leaderboard_screen.run()
    progression.level = sync_saved_progress(economy, progression)
    active_bg = load_level_background(progression.level)
    if active_customer is not None:
        sync_station_order(mixing_station, active_customer)
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
    if "order_scene" in globals():
        if hasattr(order_scene, "set_barista"):
            order_scene.set_barista(active_barista)
        order_scene.start(active_customer, level=progression.level)
    return active_bg, active_customer

# Start Screen Initialization
start_screen = StartScreen(screen)
player_name = start_screen.run()
if player_name is None:
    pygame.quit()
    sys.exit()

ensure_game_music(start_screen)
economy = UIEconomy(screen=screen, player_name=player_name)

# Barista selection is handled by barista_selection.py. Unlocks are per player.
active_barista = choose_barista(screen, economy, player_name)
if active_barista is None:
    pygame.quit()
    sys.exit()

try:
    current_saved_level = int(economy.level)
except (ValueError, TypeError):
    current_saved_level = 1
current_saved_level = max(1, min(current_saved_level, 3))
progression = Progression(level=current_saved_level, xp=economy.xp)
progression.level = current_saved_level
reward_system = RewardSystem()
map_manager = MapManager(economy_ref=economy)
leaderboard_manager = LeaderboardManager(economy_ref=economy)
level_unlock_screen = LevelUnlockScreen(screen)
loading_screen = LoadingScreen(screen)
mini_challenge = MiniChallenge()
sync_level_systems(economy, progression, None)
ensure_game_music(start_screen)

loading_ok = loading_screen.run(player_name=player_name, level=progression.level, duration=5.8)
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
    barista=active_barista,
)
if hasattr(mixing_station, "set_barista"):
    mixing_station.set_barista(active_barista)
if hasattr(mixing_station, "show_header"):
    mixing_station.show_header = False
if hasattr(mixing_station, "draw_header"):
    mixing_station.draw_header = False

sync_level_systems(economy, progression, mixing_station)
active_bg = load_level_background(progression.level)
active_customer = refresh_customer(progression.level, mixing_station)
order_scene = OrderScene(screen)
if hasattr(order_scene, "set_barista"):
    order_scene.set_barista(active_barista)
order_scene.start(active_customer, level=progression.level)

spawn_timer = 0.0
SPAWN_DELAY = 1.5
LEVEL_KEYS = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}
LEVEL_NODES = {1: "neon_alley", 2: "cyber_dock", 3: "high_rise"}
successful_drinks = 0

def run_level_transition(new_level, economy, progression, mixing_station, player_name):
    new_level = max(1, min(int(new_level), 3))
    if new_level >= 2:
        ensure_game_music()
        level_unlock_screen.run(level=new_level, duration=4.5)
    ensure_game_music()
    loading_screen.run(player_name=player_name, level=new_level, duration=5.8)
    active_bg, active_customer = switch_level(new_level, economy, progression, mixing_station)
    mixing_station.reset()
    sync_station_order(mixing_station, active_customer)
    economy.save_economy_data()
    ensure_game_music()
    return active_bg, active_customer


# Main Game Loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    if not pygame.mixer.music.get_busy():
        ensure_game_music(start_screen)
    current_combo = getattr(reward_system, "combo", getattr(reward_system, "combo_multiplier", 1))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
            
        if order_scene.active:
            order_scene.handle_event(event)
            continue

        if mini_challenge.active:
            mini_challenge.handle_event(event)

        try:
            mixing_station.handle_event(event)
        except Exception as error:
            print(f"[STATION ERROR] {error}")
        try:
            if mixing_station.consume_exit_request():
                try:
                    economy.save_economy_data()
                except Exception as error:
                    print(f"[MAIN] Exit save warning: {error}")
                GameEndScreen(screen).run(
                    player_name=economy.player_name,
                    level=progression.level,
                    successful_drinks=successful_drinks,
                    xp=economy.xp,
                    credits=economy.credits,
                )
                running = False
                continue
        except Exception as error:
            print(f"[EXIT ERROR] {error}")
        try:
            if mixing_station.consume_return_start_request():
                start_screen = StartScreen(screen)
                new_player_name = start_screen.run()
                if new_player_name is None:
                    running = False
                    continue
                player_name = new_player_name
                economy.player_name = player_name
                economy.load_economy_data()
                try:
                    current_lvl = int(economy.level)
                except (ValueError, TypeError):
                    current_lvl = 1
                progression.reset()
                progression.level = max(1, min(current_lvl, 3))
                progression.xp = max(0, int(economy.xp))
                reward_system.reset()
                successful_drinks = 0
                ensure_game_music(start_screen)
                active_barista = choose_barista(screen, economy, player_name)
                if active_barista is None:
                    running = False
                    continue
                if not loading_screen.run(player_name=player_name, level=progression.level, duration=5.8):
                    running = False
                    continue
                ensure_game_music(start_screen)
                if hasattr(mixing_station, "set_barista"):
                    mixing_station.set_barista(active_barista)
                if hasattr(order_scene, "set_barista"):
                    order_scene.set_barista(active_barista)
                mixing_station.reset()
                sync_level_systems(economy, progression, mixing_station)
                active_bg = load_level_background(progression.level)
                active_customer = refresh_customer(progression.level, mixing_station)
                order_scene.start(active_customer, level=progression.level)
                spawn_timer = 0.0
                continue
        except Exception as error:
            print(f"[RETURN TO START ERROR] {error}")
        try:
            if mixing_station.consume_map_request():
                active_bg, active_customer = open_map(
                    screen, map_manager, economy, progression, mixing_station, active_customer
                )
        except Exception as error:
            print(f"[MAP ERROR] {error}")
        try:
            if mixing_station.consume_leaderboard_request():
                active_bg, active_customer = open_leaderboard(
                    screen, leaderboard_manager, economy, progression, mixing_station, active_customer
                )
        except Exception as error:
            print(f"[LEADERBOARD ERROR] {error}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                try:
                    economy.reset_economy()
                    progression.reset()
                    reward_system.reset()
                    mixing_station.reset()
                except Exception as error:
                    print(f"[MAIN] Reset warning: {error}")
                successful_drinks = 0
                progression.level = economy.level
                progression.xp = economy.xp
                sync_level_systems(economy, progression, mixing_station)
                active_bg = load_level_background(progression.level)
                active_customer = refresh_customer(progression.level, mixing_station)
                if hasattr(order_scene, "set_barista"):
                    order_scene.set_barista(active_barista)
                order_scene.start(active_customer, level=progression.level)
                spawn_timer = 0.0
            elif event.key == pygame.K_m:
                active_bg, active_customer = open_map(
                    screen, map_manager, economy, progression, mixing_station, active_customer
                )
            elif event.key == pygame.K_l:
                active_bg, active_customer = open_leaderboard(
                    screen, leaderboard_manager, economy, progression, mixing_station, active_customer
                )
            elif event.key in LEVEL_KEYS:
                level = LEVEL_KEYS[event.key]
                node = map_manager.nodes.get(LEVEL_NODES[level])
                if (
                    (level == 1 and node is None)
                    or (node is not None and node.is_unlocked)
                    or progression.level >= level
                ):
                    active_bg, active_customer = switch_level(level, economy, progression, mixing_station)
                    spawn_timer = 0.0
                    
    if not running:
        break

    # MENU is the only pause control. While it is open, freeze the entire
    # gameplay update loop (customer patience, spawn timer, challenges, etc.)
    # but keep the menu/audio UI responsive. Resume simply falls through here
    # on the next frame and gameplay continues from the same state.
    if getattr(mixing_station, "show_menu_overlay", False):
        try:
            mixing_station.update(0.0)
        except Exception as error:
            print(f"[STATION MENU UPDATE ERROR] {error}")
        screen.blit(active_bg, (0, 0))
        if active_customer is not None:
            active_customer.draw(screen)
        mixing_station.draw(screen)
        pygame.display.flip()
        continue

    if order_scene.active:
        order_scene.update(dt)
        screen.blit(active_bg, (0, 0))
        order_scene.draw(screen)
        pygame.display.flip()
        continue

    screen.blit(active_bg, (0, 0))
    if active_customer is not None:
        active_customer.draw(screen)
    mixing_station.draw(screen)
    economy.draw(combo_count=current_combo, dt=dt)

    if mini_challenge.active or mini_challenge.done:
        mini_challenge.update(dt)
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
                accuracy_result = OrderAccuracy.check_order(customer_order, player_drink_data)
                try:
                    served_quickly = active_customer.served_quickly()
                except Exception:
                    served_quickly = False
                reward_result = reward_system.calculate_reward(
                    accuracy_result,
                    served_quickly=served_quickly,
                    level=progression.level
                )
                try:
                    base_credit_delta = int(getattr(reward_result, "net_credits", 0))
                except (TypeError, ValueError):
                    base_credit_delta = 0
                jax_bonus = (max(0, base_credit_delta) * 20 // 100) if active_barista == "Jax" else 0
                total_credit_delta = base_credit_delta + jax_bonus
                try:
                    current_xp = max(0, int(economy.xp))
                except (TypeError, ValueError, AttributeError):
                    current_xp = 0
                try:
                    xp_delta = int(reward_result.total_xp)
                except (TypeError, ValueError, AttributeError):
                    xp_delta = 0
                new_xp = max(0, current_xp + xp_delta)
                economy.set_xp(new_xp)
                progression.xp = economy.xp
                successful_order = (accuracy_result.correct_count == 4)
                if successful_order:
                    successful_drinks += 1
                try:
                    economy.apply_reward(reward_result)
                    if jax_bonus:
                        economy.credits = max(0, int(economy.credits) + jax_bonus)
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
                        credit_delta=total_credit_delta,
                    )
                except Exception as error:
                    print(f"[HUD] Reward feedback warning: {error}")
                if running:
                    try:
                        mixing_station.reset()
                    except Exception as error:
                        print(f"[STATION RESET ERROR] {error}")

    if (
        running
        and active_customer is not None
        and not mixing_station.challenge.paused
    ):
        old_state = active_customer.state
        try:
            active_customer.update(dt)
        except Exception as error:
            print(f"[CUSTOMER UPDATE ERROR] {error}")
        if old_state == CustomerState.WAITING and active_customer.state == CustomerState.LEAVING:
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
            if hasattr(order_scene, "set_barista"):
                order_scene.set_barista(active_barista)
            order_scene.start(active_customer, level=progression.level)
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
    try:
        mixing_station.draw(screen)
    except Exception as error:
        print(f"[STATION DRAW ERROR] {error}")
    if mini_challenge.active or mini_challenge.done:
        mini_challenge.draw(screen)
    if not getattr(mixing_station, "show_menu_overlay", False):
        try:
            economy.draw(combo_count=current_combo, dt=dt)
        except Exception as error:
            print(f"[UI ECONOMY DRAW ERROR] {error}")
    pygame.display.flip()

pygame.quit()
sys.exit()
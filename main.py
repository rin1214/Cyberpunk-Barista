import sys
import os
import pygame

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MUSIC_FILE = os.path.abspath(os.path.join(PROJECT_ROOT, "assets", "mahirah", "audio", "lofihiphop.wav"))

# --- AUDIO PRE-INITIALIZATION ---
# Pre-init mixer with standard frequency and large buffer size for smooth playback
try:
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
except Exception as pre_init_err:
    print(f"[AUDIO] Pre-init warning: {pre_init_err}")

pygame.init()

if not pygame.mixer.get_init():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    except Exception as init_err:
        print(f"[AUDIO ERROR] Could not initialize mixer: {init_err}")

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

# Max gain settings
music_volume = 1.0
sfx_volume = 1.0
is_muted = False

def ensure_game_music():
    global music_volume, is_muted
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        
        target_vol = 0.0 if is_muted else music_volume
        pygame.mixer.music.set_volume(target_vol)

        if not pygame.mixer.music.get_busy():
            if os.path.exists(MUSIC_FILE):
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(target_vol)
                print(f"[AUDIO] Music playing loop set to output ({target_vol * 100:.0f}%)")
            else:
                print(f"[AUDIO ERROR] Music file not found at path: {MUSIC_FILE}")
        return True
    except pygame.error as error:
        print(f"[AUDIO ERROR] Exception during music play: {error}")
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
    active_bg = load_level_background(progression.level)
    if active_customer is not None:
        sync_station_order(mixing_station, active_customer)
    ensure_game_music()
    return active_bg, active_customer

def open_leaderboard(screen, leaderboard_manager, economy, progression, mixing_station, active_customer):
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
        order_scene.start(active_customer, level=progression.level)
    return active_bg, active_customer

# --- START SCREEN INITIALIZATION ---
start_screen = StartScreen(screen)
player_name = start_screen.run()
if player_name is None:
    pygame.quit()
    sys.exit()

ensure_game_music()

economy = UIEconomy(screen=screen, player_name=player_name)
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

loading_ok = loading_screen.run(player_name=player_name, level=progression.level, duration=5.8)
if not loading_ok:
    pygame.quit()
    sys.exit()

ensure_game_music()

drink = Drink()
mixing_station = MixingStation(
    drink=drink,
    level=progression.level,
    progression=progression,
    rewards=reward_system,
    economy=economy,
)
if hasattr(mixing_station, "show_header"):
    mixing_station.show_header = False
if hasattr(mixing_station, "draw_header"):
    mixing_station.draw_header = False
sync_level_systems(economy, progression, mixing_station)
active_bg = load_level_background(progression.level)
active_customer = refresh_customer(progression.level, mixing_station)
order_scene = OrderScene(screen)
order_scene.start(active_customer, level=progression.level)
spawn_timer = 0.0
SPAWN_DELAY = 1.5
LEVEL_KEYS = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}
LEVEL_NODES = {1: "neon_alley", 2: "cyber_dock", 3: "high_rise"}
successful_drinks = 0
total_successful_drinks = 0
game_finished = False

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

# --- PAUSE MENU SETUP ---
is_paused = False
is_dragging_music = False
is_dragging_sfx = False

font_title = pygame.font.SysFont("Arial", 38, bold=True)
font_label = pygame.font.SysFont("Arial", 16, bold=True)
font_button = pygame.font.SysFont("Arial", 22, bold=True)

pause_panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 230, SCREEN_HEIGHT // 2 - 230, 460, 460)
resume_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 100, 340, 50)
exit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 160, 340, 50)

music_track_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 80, 240, 8)
sfx_track_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 10, 240, 8)
mute_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 35, 120, 36)

CYAN = (75, 225, 255)
PINK = (255, 80, 190)
WHITE = (245, 248, 255)
PANEL_BG = (12, 18, 40)
TRACK_BG = (35, 45, 75)

# --- MAIN GAME LOOP ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    
    if not pygame.mixer.music.get_busy() and not is_muted:
        ensure_game_music()
        
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

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_paused = not is_paused
                is_dragging_music = False
                is_dragging_sfx = False
                continue

        if is_paused:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if resume_button_rect.collidepoint(mouse_pos):
                    is_paused = False
                elif exit_button_rect.collidepoint(mouse_pos):
                    running = False
                elif mute_button_rect.collidepoint(mouse_pos):
                    is_muted = not is_muted
                    pygame.mixer.music.set_volume(0.0 if is_muted else music_volume)
                elif music_track_rect.inflate(20, 20).collidepoint(mouse_pos):
                    is_dragging_music = True
                    rel_x = max(0, min(mouse_pos[0] - music_track_rect.x, music_track_rect.width))
                    music_volume = rel_x / float(music_track_rect.width)
                    if music_volume > 0:
                        is_muted = False
                    pygame.mixer.music.set_volume(0.0 if is_muted else music_volume)
                elif sfx_track_rect.inflate(20, 20).collidepoint(mouse_pos):
                    is_dragging_sfx = True
                    rel_x = max(0, min(mouse_pos[0] - sfx_track_rect.x, sfx_track_rect.width))
                    sfx_volume = rel_x / float(sfx_track_rect.width)
                    if sfx_volume > 0:
                        is_muted = False

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                is_dragging_music = False
                is_dragging_sfx = False

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging_music:
                    rel_x = max(0, min(event.pos[0] - music_track_rect.x, music_track_rect.width))
                    music_volume = rel_x / float(music_track_rect.width)
                    if music_volume > 0:
                        is_muted = False
                    pygame.mixer.music.set_volume(0.0 if is_muted else music_volume)
                elif is_dragging_sfx:
                    rel_x = max(0, min(event.pos[0] - sfx_track_rect.x, sfx_track_rect.width))
                    sfx_volume = rel_x / float(sfx_track_rect.width)
                    if sfx_volume > 0:
                        is_muted = False

            continue

        try:
            mixing_station.handle_event(event)
        except Exception as error:
            print(f"[STATION ERROR] {error}")
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
                total_successful_drinks = 0
                game_finished = False
                progression.level = economy.level
                progression.xp = economy.xp
                sync_level_systems(economy, progression, mixing_station)
                active_bg = load_level_background(progression.level)
                active_customer = refresh_customer(progression.level, mixing_station)
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

    if order_scene.active:
        order_scene.update(dt)
        screen.blit(active_bg, (0, 0))
        order_scene.draw(screen)
        pygame.display.flip()
        continue

    # --- PAUSE MENU OVERLAY ---
    if is_paused:
        screen.blit(active_bg, (0, 0))
        if active_customer is not None:
            active_customer.draw(screen)
        mixing_station.draw(screen)
        economy.draw(combo_count=current_combo, dt=dt)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 20, 190))
        screen.blit(overlay, (0, 0))
        
        pygame.draw.rect(screen, PANEL_BG, pause_panel_rect, border_radius=14)
        pygame.draw.rect(screen, CYAN, pause_panel_rect, width=2, border_radius=14)
        
        title_surf = font_title.render("GAME PAUSED", True, CYAN)
        screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, pause_panel_rect.y + 35)))
        
        sound_header = font_button.render("AUDIO SETTINGS", True, PINK)
        screen.blit(sound_header, sound_header.get_rect(center=(SCREEN_WIDTH // 2, pause_panel_rect.y + 75)))
        
        m_vol_pct = 0 if is_muted else int(music_volume * 100)
        m_label = font_label.render(f"MUSIC VOLUME: {m_vol_pct}%", True, WHITE)
        screen.blit(m_label, m_label.get_rect(center=(SCREEN_WIDTH // 2, pause_panel_rect.y + 110)))
        
        pygame.draw.rect(screen, TRACK_BG, music_track_rect, border_radius=4)
        m_fill = 0 if is_muted else int(music_track_rect.width * music_volume)
        if m_fill > 0:
            pygame.draw.rect(screen, CYAN, pygame.Rect(music_track_rect.x, music_track_rect.y, m_fill, music_track_rect.height), border_radius=4)
            
        m_handle_x = music_track_rect.x if is_muted else music_track_rect.x + m_fill
        pygame.draw.circle(screen, PINK, (m_handle_x, music_track_rect.centery), 9)
        pygame.draw.circle(screen, WHITE, (m_handle_x, music_track_rect.centery), 9, width=2)
        
        s_vol_pct = 0 if is_muted else int(sfx_volume * 100)
        s_label = font_label.render(f"SOUND EFFECTS: {s_vol_pct}%", True, WHITE)
        screen.blit(s_label, s_label.get_rect(center=(SCREEN_WIDTH // 2, pause_panel_rect.y + 180)))
        
        pygame.draw.rect(screen, TRACK_BG, sfx_track_rect, border_radius=4)
        s_fill = 0 if is_muted else int(sfx_track_rect.width * sfx_volume)
        if s_fill > 0:
            pygame.draw.rect(screen, CYAN, pygame.Rect(sfx_track_rect.x, sfx_track_rect.y, s_fill, sfx_track_rect.height), border_radius=4)
            
        s_handle_x = sfx_track_rect.x if is_muted else sfx_track_rect.x + s_fill
        pygame.draw.circle(screen, PINK, (s_handle_x, sfx_track_rect.centery), 9)
        pygame.draw.circle(screen, WHITE, (s_handle_x, sfx_track_rect.centery), 9, width=2)
        
        mouse_pos = pygame.mouse.get_pos()
        mute_hover = mute_button_rect.collidepoint(mouse_pos)
        mute_bg = (50, 20, 40) if is_muted else (20, 40, 60)
        mute_border = PINK if (is_muted or mute_hover) else CYAN
        pygame.draw.rect(screen, mute_bg, mute_button_rect, border_radius=8)
        pygame.draw.rect(screen, mute_border, mute_button_rect, width=2, border_radius=8)
        
        mute_text_str = "UNMUTE" if is_muted else "MUTE"
        mute_text = font_label.render(mute_text_str, True, WHITE)
        screen.blit(mute_text, mute_text.get_rect(center=mute_button_rect.center))
        
        resume_hover = resume_button_rect.collidepoint(mouse_pos)
        resume_color = PINK if resume_hover else CYAN
        pygame.draw.rect(screen, (30, 20, 50), resume_button_rect, border_radius=10)
        pygame.draw.rect(screen, resume_color, resume_button_rect, width=2, border_radius=10)
        resume_text = font_button.render("RESUME GAME", True, WHITE)
        screen.blit(resume_text, resume_text.get_rect(center=resume_button_rect.center))
        
        exit_hover = exit_button_rect.collidepoint(mouse_pos)
        exit_color = PINK if exit_hover else CYAN
        pygame.draw.rect(screen, (30, 20, 50), exit_button_rect, border_radius=10)
        pygame.draw.rect(screen, exit_color, exit_button_rect, width=2, border_radius=10)
        exit_text = font_button.render("EXIT TO DESKTOP", True, WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))
        
        pygame.display.flip()
        continue

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
                    total_successful_drinks += 1
                if progression.level >= 3 and successful_drinks >= 10:
                    game_finished = True
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
                if running:
                    try:
                        mixing_station.reset()
                    except Exception as error:
                        print(f"[STATION RESET ERROR] {error}")
                if game_finished:
                    end_screen = GameEndScreen(screen)
                    end_result = end_screen.run(
                        player_name=economy.player_name,
                        level=progression.level,
                        successful_drinks=total_successful_drinks,
                        xp=progression.xp,
                        credits=economy.credits,
                    )
                    if end_result == "play_again":
                        economy.reset_economy()
                        progression.reset()
                        reward_system.reset()
                        mixing_station.reset()
                        successful_drinks = 0
                        total_successful_drinks = 0
                        game_finished = False
                        progression.level = 1
                        progression.xp = 0
                        sync_level_systems(economy, progression, mixing_station)
                        active_bg = load_level_background(1)
                        active_customer = refresh_customer(1, mixing_station)
                        order_scene.start(active_customer, level=progression.level)
                        spawn_timer = 0.0
                        ensure_game_music()
                    elif end_result == "main_menu":
                        start_screen = StartScreen(screen)
                        new_player_name = start_screen.run()
                        if new_player_name is not None:
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
                            mixing_station.reset()
                            successful_drinks = 0
                            total_successful_drinks = 0
                            game_finished = False
                            sync_level_systems(economy, progression, mixing_station)
                            active_bg = load_level_background(progression.level)
                            active_customer = refresh_customer(progression.level, mixing_station)
                            order_scene.start(active_customer, level=progression.level)
                            spawn_timer = 0.0
                            ensure_game_music()
                        else:
                            running = False
                    else:
                        running = False
    if running and not game_finished and active_customer is not None:
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
    if running and not game_finished and active_customer is None:
        spawn_timer -= dt
        if spawn_timer <= 0:
            active_bg = load_level_background(progression.level)
            active_customer = refresh_customer(progression.level, mixing_station)
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
    try:
        economy.draw(combo_count=current_combo, dt=dt)
    except Exception as error:
        print(f"[UI ECONOMY DRAW ERROR] {error}")
    pygame.display.flip()

pygame.quit()
sys.exit()
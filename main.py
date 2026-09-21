"""
============================================================
CYBERPUNK CAFÉ
MAIN GAME ENGINE
============================================================

MASTER GAME FLOW
------------------------------------------------------------

START SCREEN
     ↓
LOADING SCREEN
     ↓
LEVEL 1 GAMEPLAY
     ↓
CUSTOMER ORDER
     ↓
DRINK MIXING
     ↓
SERVE
     ↓
ACCURACY CHECK
     ↓
REWARD / XP / CREDITS
     ↓
LEVEL UP?
     │
     ├── NO ───────→ NEXT CUSTOMER
     │
     └── YES
             ↓
        LEVEL UNLOCK
             ↓
        LOADING SCREEN
             ↓
        NEW LEVEL
             ↓
        NEW CUSTOMER
             ↓
        GAMEPLAY


FINAL LEVELS
------------------------------------------------------------

LEVEL 1
Back Alley Kiosk

LEVEL 2
Neon Lounge

LEVEL 3
Cyber Penthouse

LEVEL 3 is the maximum level.


MUSIC
------------------------------------------------------------

The Start Screen starts the Cyberpunk Café music.

main.py then makes sure that music continues playing
throughout the game.

The following screens NEVER stop the music:

    • Loading Screen
    • Level Unlock Screen
    • Gameplay
    • Map
    • Leaderboard

============================================================
"""

import sys
import os
import pygame


# ============================================================
# PROJECT SYSTEM IMPORTS
# ============================================================

from customer import (
    Customer,
    CustomerState,
)

from drink import Drink

from level_unlock_screen import (
    LevelUnlockScreen,
)

from loading_screen import (
    LoadingScreen,
)

from start_screen import (
    StartScreen,
)

from station import (
    MixingStation,
)

from ui_economy import (
    UIEconomy,
)

from progression import (
    Progression,
)

from rewards import (
    RewardSystem,
)

from accuracy import (
    OrderAccuracy,
)

from map_manager import (
    MapManager,
)

from map_screen import (
    MapScreen,
)

from leaderboard_manager import (
    LeaderboardManager,
)

from leaderboard_screen import (
    LeaderboardScreen,
)


# ============================================================
# PYGAME INITIALISATION
# ============================================================

pygame.init()


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# MASTER SCREEN SIZE
# ============================================================

SCREEN_WIDTH = 1280

SCREEN_HEIGHT = 720


screen = pygame.display.set_mode(
    (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
    )
)


pygame.display.set_caption(
    "Cyberpunk Café - Game Engine"
)


# ============================================================
# GAME CLOCK
# ============================================================

clock = pygame.time.Clock()

FPS = 60


# ============================================================
# FINAL LEVEL BACKGROUNDS
# ============================================================

LEVEL_BACKGROUNDS = {

    1: "assets/places/cafe_lvl1.png",

    2: "assets/places/cafe_lvl2.png",

    3: "assets/places/cafe_lvl3.png",

}


# ============================================================
# BACKGROUND CACHE
# ============================================================

bg_cache = {}


# ============================================================
# LOAD LEVEL BACKGROUND
# ============================================================

def load_level_background(
    level_num,
):
    """
    Load the correct café background.

    Level 1:
        Back Alley Kiosk

    Level 2:
        Neon Lounge

    Level 3:
        Cyber Penthouse
    """

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    try:

        level_num = int(level_num)

    except (
        TypeError,
        ValueError,
    ):

        level_num = 1

    level_num = max(
        1,
        min(
            level_num,
            3,
        ),
    )

    # --------------------------------------------------------
    # CACHE
    # --------------------------------------------------------

    if level_num in bg_cache:

        return bg_cache[level_num]

    # --------------------------------------------------------
    # FILE
    # --------------------------------------------------------

    relative_path = LEVEL_BACKGROUNDS.get(
        level_num,
        LEVEL_BACKGROUNDS[1],
    )

    path = os.path.join(
        PROJECT_ROOT,
        relative_path,
    )

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    try:

        raw_image = pygame.image.load(
            path
        ).convert_alpha()

        scaled_image = pygame.transform.smoothscale(
            raw_image,
            (
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
            ),
        )

        bg_cache[level_num] = (
            scaled_image
        )

        print(
            "[MAIN] Loaded Level "
            f"{level_num} background:"
        )

        print(
            f"       {path}"
        )

        return scaled_image

    except (
        pygame.error,
        FileNotFoundError,
    ) as error:

        print(
            "[MAIN] Background loading error:"
        )

        print(
            f"       {path}"
        )

        print(
            f"       {error}"
        )

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        fallback = pygame.Surface(
            (
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
            )
        )

        fallback.fill(
            (
                20,
                15,
                35,
            )
        )

        bg_cache[level_num] = fallback

        return fallback


# ============================================================
# MUSIC
# ============================================================

MUSIC_FILE = os.path.join(
    PROJECT_ROOT,
    "assets",
    "mahirah",
    "audio",
    "cyberpunk_cafe_theme.wav",
)


def ensure_game_music(
    start_screen=None,
):
    """
    Make sure the Cyberpunk Café background music is playing.

    IMPORTANT:

    This function does NOT restart the music if it is already
    playing.

    Therefore:

        Start Screen
            ↓
        Loading
            ↓
        Level 1
            ↓
        Level Unlock
            ↓
        Loading
            ↓
        Level 2
            ↓
        Level 3

    all use the same continuous music playback.
    """

    try:

        # ----------------------------------------------------
        # INITIALISE MIXER IF NECESSARY
        # ----------------------------------------------------

        if not pygame.mixer.get_init():

            pygame.mixer.init()

        # ----------------------------------------------------
        # DETERMINE VOLUME
        # ----------------------------------------------------

        volume = 0.30

        muted = False

        if start_screen is not None:

            try:

                volume = float(
                    getattr(
                        start_screen,
                        "music_volume",
                        volume,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                volume = 0.30

            muted = bool(
                getattr(
                    start_screen,
                    "muted",
                    False,
                )
            )

        # ----------------------------------------------------
        # SAFETY CLAMP
        # ----------------------------------------------------

        volume = max(
            0.0,
            min(
                volume,
                1.0,
            ),
        )

        # ----------------------------------------------------
        # APPLY VOLUME
        # ----------------------------------------------------

        if muted:

            pygame.mixer.music.set_volume(
                0.0
            )

        else:

            pygame.mixer.music.set_volume(
                volume
            )

        # ----------------------------------------------------
        # MUSIC ALREADY PLAYING
        # ----------------------------------------------------

        if pygame.mixer.music.get_busy():

            print(
                "[AUDIO] Music is already playing."
            )

            return True

        # ----------------------------------------------------
        # MUSIC FILE CHECK
        # ----------------------------------------------------

        if not os.path.exists(
            MUSIC_FILE
        ):

            print(
                "[AUDIO ERROR] Music file not found:"
            )

            print(
                f"       {MUSIC_FILE}"
            )

            return False

        # ----------------------------------------------------
        # LOAD ONLY WHEN NOT ALREADY PLAYING
        # ----------------------------------------------------

        pygame.mixer.music.load(
            MUSIC_FILE
        )

        pygame.mixer.music.play(
            -1
        )

        print(
            "[AUDIO] Cyberpunk Café music "
            "is now playing continuously."
        )

        return True

    except pygame.error as error:

        print(
            f"[AUDIO ERROR] {error}"
        )

        return False


# ============================================================
# CUSTOMER POSITION
# ============================================================

def position_customer(
    customer,
    spawning=False,
):
    """
    Position the customer in the lower-left café area.

    Customer.py remains responsible for the actual movement.
    """

    if customer is None:

        return

    try:

        # ----------------------------------------------------
        # FINAL COUNTER POSITION
        # ----------------------------------------------------

        counter_bottom = 690

        customer_x = 180

        customer.x = (
            customer_x
        )

        customer.y_counter = (
            counter_bottom
        )

        # ----------------------------------------------------
        # SPAWN POSITION
        # ----------------------------------------------------

        customer.spawn_y = (
            counter_bottom + 120
        )

        if spawning:

            customer.current_y = (
                customer.spawn_y
            )

        else:

            customer.current_y = (
                counter_bottom
            )

        # ----------------------------------------------------
        # RECTANGLE
        # ----------------------------------------------------

        if hasattr(
            customer,
            "rect",
        ):

            customer.rect.centerx = (
                customer_x
            )

            customer.rect.bottom = int(
                customer.current_y
            )

    except Exception as error:

        print(
            "[MAIN] Customer positioning warning:"
        )

        print(
            f"       {error}"
        )


# ============================================================
# CREATE CUSTOMER
# ============================================================

def create_customer(
    level,
):
    """
    Create a customer using the current level.
    """

    customer = Customer(
        current_level=level
    )

    position_customer(
        customer,
        spawning=True,
    )

    return customer


# ============================================================
# GIVE CUSTOMER ORDER TO STATION
# ============================================================

def sync_station_order(
    mixing_station,
    customer,
):
    """
    Send the customer's order to the mixing station.
    """

    if customer is None:

        return

    # --------------------------------------------------------
    # CURRENT ORDER
    # --------------------------------------------------------

    order = getattr(
        customer,
        "order",
        None,
    )

    # --------------------------------------------------------
    # COMPATIBILITY
    # --------------------------------------------------------

    if order is None:

        order = getattr(
            customer,
            "current_order",
            None,
        )

    # --------------------------------------------------------
    # SEND ORDER
    # --------------------------------------------------------

    if order is not None:

        mixing_station.set_customer_order(
            order
        )


# ============================================================
# REFRESH CUSTOMER
# ============================================================

def refresh_customer(
    level,
    mixing_station,
):
    """
    Create a fresh customer and send their order to the station.
    """

    customer = create_customer(
        level
    )

    sync_station_order(
        mixing_station,
        customer,
    )

    return customer


# ============================================================
# SYNCHRONISE GAME SYSTEMS
# ============================================================

def sync_level_systems(
    economy,
    progression,
    mixing_station,
):
    """
    Keep Economy, Progression and MixingStation synchronized.
    """

    # --------------------------------------------------------
    # ECONOMY
    # --------------------------------------------------------

    try:

        economy.sync_progression(
            progression
        )

    except Exception as error:

        print(
            "[MAIN] Economy sync warning:"
        )

        print(
            f"       {error}"
        )

    # --------------------------------------------------------
    # MIXING STATION
    # --------------------------------------------------------

    if mixing_station is not None:

        try:

            mixing_station.set_progression(
                progression
            )

        except Exception as error:

            print(
                "[MAIN] Station progression sync warning:"
            )

            print(
                f"       {error}"
            )

        try:

            mixing_station.set_level(
                progression.level
            )

        except Exception as error:

            print(
                "[MAIN] Station level sync warning:"
            )

            print(
                f"       {error}"
            )


# ============================================================
# OPEN MAP
# ============================================================

def open_map(
    screen,
    map_manager,
    economy,
    progression,
    mixing_station,
):
    """
    Open the existing collaborator Map screen.

    Map.py / map_manager.py are not modified here.
    """

    print(
        "[MAIN] Opening Map."
    )

    map_screen = MapScreen(
        screen,
        map_manager,
        economy,
    )

    map_screen.run()

    # --------------------------------------------------------
    # SYNCHRONISE AFTER MAP
    # --------------------------------------------------------

    try:

        progression.level = max(
            1,
            min(
                int(
                    economy.level
                ),
                3,
            ),
        )

    except Exception:

        progression.level = 1

    try:

        progression.xp = max(
            0,
            int(
                economy.xp
            ),
        )

    except Exception:

        progression.xp = 0

    sync_level_systems(
        economy,
        progression,
        mixing_station,
    )

    active_bg = load_level_background(
        progression.level
    )

    active_customer = refresh_customer(
        progression.level,
        mixing_station,
    )

    return (
        active_bg,
        active_customer,
    )


# ============================================================
# OPEN LEADERBOARD
# ============================================================

def open_leaderboard(
    screen,
    leaderboard_manager,
    economy,
    progression,
    mixing_station,
):
    """
    Open the existing collaborator Leaderboard screen.
    """

    print(
        "[MAIN] Opening Leaderboard."
    )

    leaderboard_screen = (
        LeaderboardScreen(
            screen,
            leaderboard_manager,
            economy,
        )
    )

    leaderboard_screen.run()

    # --------------------------------------------------------
    # SYNCHRONISE AFTER LEADERBOARD
    # --------------------------------------------------------

    try:

        progression.level = max(
            1,
            min(
                int(
                    economy.level
                ),
                3,
            ),
        )

    except Exception:

        progression.level = 1

    try:

        progression.xp = max(
            0,
            int(
                economy.xp
            ),
        )

    except Exception:

        progression.xp = 0

    sync_level_systems(
        economy,
        progression,
        mixing_station,
    )

    active_bg = load_level_background(
        progression.level
    )

    active_customer = refresh_customer(
        progression.level,
        mixing_station,
    )

    return (
        active_bg,
        active_customer,
    )


# ============================================================
# MANUAL LEVEL SWITCH
# ============================================================

def switch_level(
    level,
    economy,
    progression,
    mixing_station,
):
    """
    Debug/manual level switching.

    This is separate from natural XP progression.

    It is kept for compatibility with the existing
    keyboard controls.
    """

    try:

        level = int(level)

    except (
        TypeError,
        ValueError,
    ):

        level = 1

    level = max(
        1,
        min(
            level,
            3,
        ),
    )

    # --------------------------------------------------------
    # SET ECONOMY LEVEL
    # --------------------------------------------------------

    economy.set_level(
        level
    )

    # --------------------------------------------------------
    # SET PROGRESSION LEVEL
    # --------------------------------------------------------

    progression.level = (
        level
    )

    progression.xp = 0

    try:

        economy.xp = 0

    except Exception:

        pass

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    economy.save_economy_data()

    # --------------------------------------------------------
    # SYNC
    # --------------------------------------------------------

    sync_level_systems(
        economy,
        progression,
        mixing_station,
    )

    # --------------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------------

    active_bg = load_level_background(
        level
    )

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    active_customer = refresh_customer(
        level,
        mixing_station,
    )

    return (
        active_bg,
        active_customer,
    )


# ============================================================
# LEVEL TRANSITION
# ============================================================

def run_level_transition(
    new_level,
    player_name,
    screen,
    level_unlock_screen,
    loading_screen,
    progression,
    economy,
    mixing_station,
):
    """
    Run the complete level transition.

    THIS IS THE IMPORTANT FIX.

    Normal gameplay does not draw while these screens
    are active.

    Sequence:

        Level Up
            ↓
        Unlock Screen
            ↓
        Loading Screen
            ↓
        New Background
            ↓
        New Customer
            ↓
        Resume Gameplay
    """

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    try:

        new_level = int(
            new_level
        )

    except (
        TypeError,
        ValueError,
    ):

        new_level = 1

    new_level = max(
        1,
        min(
            new_level,
            3,
        ),
    )

    print()
    print(
        "================================================"
    )

    print(
        "[MAIN] STARTING LEVEL TRANSITION"
    )

    print(
        f"[MAIN] New Level: {new_level}"
    )

    print(
        "================================================"
    )

    # --------------------------------------------------------
    # CLEAR OLD CUSTOMER / STATION
    # --------------------------------------------------------

    try:

        mixing_station.reset()

    except Exception as error:

        print(
            "[MAIN] Station reset warning:"
        )

        print(
            f"       {error}"
        )

    # --------------------------------------------------------
    # CLEAR OLD DISPLAY
    #
    # This guarantees the transition screen gets a clean
    # display surface.
    # --------------------------------------------------------

    screen.fill(
        (
            8,
            10,
            28,
        )
    )

    pygame.display.flip()

    # --------------------------------------------------------
    # MAKE SURE MUSIC CONTINUES
    # --------------------------------------------------------

    ensure_game_music()

    # ========================================================
    # LEVEL UNLOCK SCREEN
    # ========================================================

    if new_level >= 2:

        print(
            "[MAIN] Showing Level Unlock Screen..."
        )

        unlock_ok = (
            level_unlock_screen.run(
                level=new_level,
                duration=4.5,
            )
        )

        if not unlock_ok:

            print(
                "[MAIN] Level unlock screen requested quit."
            )

            return False

    # --------------------------------------------------------
    # MUSIC CHECK
    # --------------------------------------------------------

    ensure_game_music()

    # ========================================================
    # LOADING SCREEN
    # ========================================================

    print(
        "[MAIN] Showing Loading Screen..."
    )

    loading_ok = (
        loading_screen.run(
            player_name=player_name,
            level=new_level,
            duration=6.7,
        )
    )

    if not loading_ok:

        print(
            "[MAIN] Loading screen requested quit."
        )

        return False

    # --------------------------------------------------------
    # MUSIC CHECK
    # --------------------------------------------------------

    ensure_game_music()

    # ========================================================
    # SET NEW BACKGROUND
    # ========================================================

    active_bg = load_level_background(
        new_level
    )

    # ========================================================
    # SYNCHRONISE PROGRESSION
    # ========================================================

    progression.level = (
        new_level
    )

    sync_level_systems(
        economy,
        progression,
        mixing_station,
    )

    # ========================================================
    # UPDATE STATION
    # ========================================================

    try:

        mixing_station.reset()

    except Exception:

        pass

    try:

        mixing_station.set_progression(
            progression
        )

    except Exception:

        pass

    try:

        mixing_station.set_level(
            new_level
        )

    except Exception:

        pass

    # ========================================================
    # NEW CUSTOMER
    # ========================================================

    active_customer = refresh_customer(
        new_level,
        mixing_station,
    )

    # ========================================================
    # SAVE NEW LEVEL
    # ========================================================

    try:

        economy.sync_progression(
            progression
        )

    except Exception:

        pass

    try:

        economy.save_economy_data()

    except Exception as error:

        print(
            "[MAIN] Save warning:"
        )

        print(
            f"       {error}"
        )

    # ========================================================
    # FINAL DISPLAY
    # ========================================================

    screen.blit(
        active_bg,
        (
            0,
            0,
        ),
    )

    try:

        active_customer.draw(
            screen
        )

    except Exception as error:

        print(
            "[MAIN] Customer draw warning:"
        )

        print(
            f"       {error}"
        )

    try:

        mixing_station.draw(
            screen
        )

    except Exception as error:

        print(
            "[MAIN] Station draw warning:"
        )

        print(
            f"       {error}"
        )

    pygame.display.flip()

    # --------------------------------------------------------
    # MUSIC
    # --------------------------------------------------------

    ensure_game_music()

    print(
        f"[MAIN] LEVEL {new_level} TRANSITION COMPLETE."
    )

    print(
        "[MAIN] Returning to normal gameplay."
    )

    print()

    return (
        active_bg,
        active_customer,
        True,
    )


# ============================================================
# START SCREEN
# ============================================================

start_screen = StartScreen(
    screen
)

player_name = start_screen.run()


# ============================================================
# START SCREEN EXIT
# ============================================================

if player_name is None:

    pygame.quit()

    sys.exit()


# ============================================================
# IMPORTANT:
# TAKE OVER GLOBAL MUSIC AFTER START SCREEN
# ============================================================

ensure_game_music(
    start_screen
)


# ============================================================
# ECONOMY
# ============================================================

economy = UIEconomy(
    screen=screen,
    player_name=player_name,
)


# ============================================================
# PROGRESSION
# ============================================================

progression = Progression(
    level=economy.level,
    xp=economy.xp,
)


# ============================================================
# FORCE FINAL LEVEL LIMIT
# ============================================================

progression.level = max(
    1,
    min(
        int(
            progression.level
        ),
        3,
    ),
)


# ============================================================
# REWARD SYSTEM
# ============================================================

reward_system = RewardSystem()


# ============================================================
# MAP MANAGER
# ============================================================

map_manager = MapManager(
    economy_ref=economy
)


# ============================================================
# LEADERBOARD MANAGER
# ============================================================

leaderboard_manager = (
    LeaderboardManager(
        economy_ref=economy
    )
)


# ============================================================
# LOADING SCREEN
# ============================================================

loading_screen = LoadingScreen(
    screen
)


# ============================================================
# LEVEL UNLOCK SCREEN
# ============================================================

level_unlock_screen = (
    LevelUnlockScreen(
        screen
    )
)


# ============================================================
# SYNCHRONISE SYSTEMS
# ============================================================

sync_level_systems(
    economy,
    progression,
    None,
)


# ============================================================
# INITIAL LOADING SCREEN
# ============================================================

ensure_game_music(
    start_screen
)

loading_ok = loading_screen.run(
    player_name=player_name,
    level=progression.level,
    duration=6.7,
)

if not loading_ok:

    pygame.quit()

    sys.exit()


# ============================================================
# MAKE SURE MUSIC SURVIVED LOADING
# ============================================================

ensure_game_music(
    start_screen
)


# ============================================================
# LEGACY DRINK OBJECT
# ============================================================

drink = Drink()


# ============================================================
# MIXING STATION
# ============================================================

mixing_station = MixingStation(
    drink=drink,
    level=progression.level,
    progression=progression,
    rewards=reward_system,
    economy=economy,
)


# ============================================================
# INITIAL BACKGROUND
# ============================================================

active_bg = load_level_background(
    progression.level
)


# ============================================================
# FIRST CUSTOMER
# ============================================================

active_customer = refresh_customer(
    progression.level,
    mixing_station,
)


# ============================================================
# CUSTOMER SPAWN SETTINGS
# ============================================================

spawn_timer = 0.0

SPAWN_DELAY = 1.5


# ============================================================
# MAIN GAME LOOP
# ============================================================

running = True


while running:

    # ========================================================
    # DELTA TIME
    # ========================================================

    dt = (
        clock.tick(
            FPS
        )
        / 1000.0
    )

    # ========================================================
    # KEEP MUSIC ALIVE
    # ========================================================
    #
    # This does NOT restart music when it is already playing.
    #
    # It only protects against another screen accidentally
    # stopping the music.
    # ========================================================

    if not pygame.mixer.music.get_busy():

        ensure_game_music(
            start_screen
        )

    # ========================================================
    # EVENT LOOP
    # ========================================================

    for event in pygame.event.get():

        # ====================================================
        # QUIT
        # ====================================================

        if event.type == pygame.QUIT:

            running = False

            continue

        # ====================================================
        # MIXING STATION
        # ====================================================

        try:

            mixing_station.handle_event(
                event
            )

        except Exception as error:

            print(
                "[STATION ERROR] "
                "Event handling exception:"
            )

            print(
                f"       {error}"
            )

        # ====================================================
        # MAP BUTTON
        # ====================================================

        try:

            if (
                mixing_station.consume_map_request()
            ):

                (
                    active_bg,
                    active_customer,
                ) = open_map(
                    screen,
                    map_manager,
                    economy,
                    progression,
                    mixing_station,
                )

                spawn_timer = 0.0

                # Music continues after Map.
                ensure_game_music(
                    start_screen
                )

        except Exception as error:

            print(
                "[MAP ERROR]"
            )

            print(
                f"       {error}"
            )

        # ====================================================
        # LEADERBOARD BUTTON
        # ====================================================

        try:

            if (
                mixing_station
                .consume_leaderboard_request()
            ):

                (
                    active_bg,
                    active_customer,
                ) = open_leaderboard(
                    screen,
                    leaderboard_manager,
                    economy,
                    progression,
                    mixing_station,
                )

                spawn_timer = 0.0

                # Music continues after Leaderboard.
                ensure_game_music(
                    start_screen
                )

        except Exception as error:

            print(
                "[LEADERBOARD ERROR]"
            )

            print(
                f"       {error}"
            )

        # ====================================================
        # KEYBOARD CONTROLS
        # ====================================================

        if event.type == pygame.KEYDOWN:

            # =================================================
            # R = RESET
            # =================================================

            if event.key == pygame.K_r:

                print(
                    "[MAIN] Resetting game..."
                )

                try:

                    economy.reset_economy()

                except Exception as error:

                    print(
                        "[MAIN] Economy reset warning:"
                    )

                    print(
                        f"       {error}"
                    )

                try:

                    progression.reset()

                except Exception as error:

                    print(
                        "[MAIN] Progression reset warning:"
                    )

                    print(
                        f"       {error}"
                    )

                try:

                    reward_system.reset()

                except Exception as error:

                    print(
                        "[MAIN] Reward reset warning:"
                    )

                    print(
                        f"       {error}"
                    )

                try:

                    mixing_station.reset()

                except Exception as error:

                    print(
                        "[MAIN] Station reset warning:"
                    )

                    print(
                        f"       {error}"
                    )

                # ------------------------------------------------
                # SYNCHRONISE
                # ------------------------------------------------

                progression.level = (
                    economy.level
                )

                progression.xp = (
                    economy.xp
                )

                sync_level_systems(
                    economy,
                    progression,
                    mixing_station,
                )

                active_bg = (
                    load_level_background(
                        progression.level
                    )
                )

                active_customer = (
                    refresh_customer(
                        progression.level,
                        mixing_station,
                    )
                )

                spawn_timer = 0.0

            # =================================================
            # M = MAP
            # =================================================

            elif event.key == pygame.K_m:

                try:

                    (
                        active_bg,
                        active_customer,
                    ) = open_map(
                        screen,
                        map_manager,
                        economy,
                        progression,
                        mixing_station,
                    )

                    spawn_timer = 0.0

                    ensure_game_music(
                        start_screen
                    )

                except Exception as error:

                    print(
                        "[MAP ERROR]"
                    )

                    print(
                        f"       {error}"
                    )

            # =================================================
            # L = LEADERBOARD
            # =================================================

            elif event.key == pygame.K_l:

                try:

                    (
                        active_bg,
                        active_customer,
                    ) = open_leaderboard(
                        screen,
                        leaderboard_manager,
                        economy,
                        progression,
                        mixing_station,
                    )

                    spawn_timer = 0.0

                    ensure_game_music(
                        start_screen
                    )

                except Exception as error:

                    print(
                        "[LEADERBOARD ERROR]"
                    )

                    print(
                        f"       {error}"
                    )

            # =================================================
            # 1 = LEVEL 1 DEBUG
            # =================================================

            elif event.key == pygame.K_1:

                try:

                    node = (
                        map_manager.nodes.get(
                            "neon_alley"
                        )
                    )

                    if (
                        node is not None
                        and node.is_unlocked
                    ):

                        (
                            active_bg,
                            active_customer,
                        ) = switch_level(
                            1,
                            economy,
                            progression,
                            mixing_station,
                        )

                        spawn_timer = 0.0

                except Exception as error:

                    print(
                        "[LEVEL 1 SWITCH ERROR]"
                    )

                    print(
                        f"       {error}"
                    )

            # =================================================
            # 2 = LEVEL 2 DEBUG
            # =================================================

            elif event.key == pygame.K_2:

                try:

                    node = (
                        map_manager.nodes.get(
                            "cyber_dock"
                        )
                    )

                    if (
                        node is not None
                        and node.is_unlocked
                    ):

                        (
                            active_bg,
                            active_customer,
                        ) = switch_level(
                            2,
                            economy,
                            progression,
                            mixing_station,
                        )

                        spawn_timer = 0.0

                except Exception as error:

                    print(
                        "[LEVEL 2 SWITCH ERROR]"
                    )

                    print(
                        f"       {error}"
                    )

            # =================================================
            # 3 = LEVEL 3 DEBUG
            # =================================================

            elif event.key == pygame.K_3:

                try:

                    node = (
                        map_manager.nodes.get(
                            "high_rise"
                        )
                    )

                    if (
                        node is not None
                        and node.is_unlocked
                    ):

                        (
                            active_bg,
                            active_customer,
                        ) = switch_level(
                            3,
                            economy,
                            progression,
                            mixing_station,
                        )

                        spawn_timer = 0.0

                except Exception as error:

                    print(
                        "[LEVEL 3 SWITCH ERROR]"
                    )

                    print(
                        f"       {error}"
                    )

    # ========================================================
    # UPDATE MIXING STATION
    # ========================================================

    try:

        mixing_station.update(
            dt
        )

    except Exception as error:

        print(
            "[STATION ERROR] "
            "Update exception:"
        )

        print(
            f"       {error}"
        )

    # ========================================================
    # SERVE COMPLETED DRINK
    # ========================================================

    if (
        mixing_station.served
    ):

        if (
            active_customer is not None
        ):

            if (
                active_customer.state
                == CustomerState.WAITING
            ):

                # ==============================================
                # PLAYER DRINK
                # ==============================================

                player_drink_data = (
                    mixing_station
                    .get_player_drink_data()
                )

                # ==============================================
                # CUSTOMER ORDER
                # ==============================================

                customer_order = getattr(
                    active_customer,
                    "order",
                    None,
                )

                if customer_order is None:

                    customer_order = getattr(
                        active_customer,
                        "current_order",
                        None,
                    )

                # ==============================================
                # ACCURACY
                # ==============================================

                accuracy_result = (
                    OrderAccuracy.check_order(
                        customer_order,
                        player_drink_data,
                    )
                )

                # ==============================================
                # CUSTOMER SPEED
                # ==============================================

                try:

                    served_quickly = (
                        active_customer
                        .served_quickly()
                    )

                except Exception:

                    served_quickly = False

                # ==============================================
                # REWARD
                # ==============================================

                reward_result = (
                    reward_system.calculate_reward(
                        accuracy_result,
                        served_quickly=served_quickly,
                    )
                )

                # ==============================================
                # OLD LEVEL
                # ==============================================

                old_level = (
                    progression.level
                )

                # ==============================================
                # ADD / REMOVE XP
                # ==============================================

                progression.add_xp(
                    reward_result.total_xp
                )

                # ==============================================
                # CREDITS
                # ==============================================

                try:

                    economy.apply_reward(
                        reward_result
                    )

                except Exception as error:

                    print(
                        "[ECONOMY] Reward warning:"
                    )

                    print(
                        f"       {error}"
                    )

                # ==============================================
                # CHECK NEW LEVEL
                # ==============================================

                new_level = (
                    progression.level
                )

                level_changed = (
                    new_level
                    > old_level
                )

                # ==============================================
                # SYNCHRONISE ECONOMY
                # ==============================================

                try:

                    economy.sync_progression(
                        progression
                    )

                except Exception as error:

                    print(
                        "[MAIN] Economy sync warning:"
                    )

                    print(
                        f"       {error}"
                    )

                # ==============================================
                # CUSTOMER REACTION
                # ==============================================

                try:

                    active_customer.serve_drink(
                        player_drink_data
                    )

                except Exception as error:

                    print(
                        "[CUSTOMER] Serve reaction warning:"
                    )

                    print(
                        f"       {error}"
                    )

                # ==============================================
                # REWARD HUD
                # ==============================================

                try:

                    mixing_station.set_reward_feedback(
                        xp_delta=(
                            reward_result.total_xp
                        ),
                        credit_delta=(
                            reward_result.net_credits
                        ),
                    )

                except Exception as error:

                    print(
                        "[HUD] Reward feedback warning:"
                    )

                    print(
                        f"       {error}"
                    )

                # ==============================================
                # TERMINAL RESULT
                # ==============================================

                print(
                    "----------------------------------------"
                )

                print(
                    "[ORDER COMPLETE]"
                )

                print(
                    f"Accuracy: "
                    f"{accuracy_result.correct_count}/"
                    f"{accuracy_result.total_count}"
                )

                print(
                    f"Accuracy Percentage: "
                    f"{accuracy_result.percentage:.0f}%"
                )

                print(
                    f"Served Quickly: "
                    f"{served_quickly}"
                )

                if (
                    reward_result.total_xp
                    >= 0
                ):

                    print(
                        f"XP Earned: "
                        f"+{reward_result.total_xp}"
                    )

                else:

                    print(
                        f"XP Penalty: "
                        f"{reward_result.total_xp}"
                    )

                print(
                    f"Credits Change: "
                    f"{reward_result.net_credits:+}"
                )

                if getattr(
                    reward_result,
                    "xp_penalty",
                    0,
                ) > 0:

                    print(
                        f"XP Penalty Applied: "
                        f"-{reward_result.xp_penalty}"
                    )

                if getattr(
                    reward_result,
                    "credit_penalty",
                    0,
                ) > 0:

                    print(
                        f"Credit Penalty Applied: "
                        f"-{reward_result.credit_penalty}"
                    )

                print(
                    f"Combo: "
                    f"{reward_result.combo_count}"
                )

                print(
                    f"Current Level: "
                    f"{progression.level}"
                )

                print(
                    f"Current Location: "
                    f"{progression.get_current_location()}"
                )

                print(
                    "----------------------------------------"
                )

                # ==============================================
                # LEVEL TRANSITION
                # ==============================================
                #
                # IMPORTANT:
                #
                # We DO NOT change active_bg before the
                # unlock screen.
                #
                # We DO NOT create a new customer before
                # the transition.
                #
                # The entire transition takes place first.
                #
                # ==============================================

                if level_changed:

                    print(
                        f"[LEVEL UP] "
                        f"Level {old_level} "
                        f"-> {new_level}"
                    )

                    # ------------------------------------------
                    # Remove old customer from gameplay.
                    # ------------------------------------------

                    active_customer = None

                    # ------------------------------------------
                    # Run transition as ONE BLOCK.
                    # ------------------------------------------

                    transition_result = (
                        run_level_transition(
                            new_level,
                            player_name,
                            screen,
                            level_unlock_screen,
                            loading_screen,
                            progression,
                            economy,
                            mixing_station,
                        )
                    )

                    # ------------------------------------------
                    # PLAYER CLOSED GAME
                    # ------------------------------------------

                    if (
                        transition_result
                        is False
                    ):

                        running = False

                    # ------------------------------------------
                    # SUCCESS
                    # ------------------------------------------

                    elif (
                        isinstance(
                            transition_result,
                            tuple,
                        )
                        and len(
                            transition_result
                        ) == 3
                    ):

                        (
                            active_bg,
                            active_customer,
                            transition_ok,
                        ) = (
                            transition_result
                        )

                        if not transition_ok:

                            running = False

                        else:

                            spawn_timer = 0.0

                    # ------------------------------------------
                    # SAFETY
                    # ------------------------------------------

                    else:

                        print(
                            "[MAIN] "
                            "Unexpected transition result."
                        )

                # ==============================================
                # SAVE AFTER ORDER
                # ==============================================

                try:

                    economy.save_economy_data()

                except Exception as error:

                    print(
                        "[MAIN] Save warning:"
                    )

                    print(
                        f"       {error}"
                    )

        # ----------------------------------------------------
        # RESET STATION
        #
        # Only reset after the transition has completed.
        # ----------------------------------------------------

        if running:

            try:

                mixing_station.reset()

            except Exception as error:

                print(
                    "[STATION] Reset warning:"
                )

                print(
                    f"       {error}"
                )

    # ========================================================
    # CUSTOMER UPDATE
    # ========================================================

    if (
        running
        and active_customer is not None
    ):

        old_state = (
            active_customer.state
        )

        # ----------------------------------------------------
        # UPDATE CUSTOMER
        # ----------------------------------------------------

        try:

            active_customer.update(
                dt
            )

        except Exception as error:

            print(
                "[CUSTOMER UPDATE ERROR]"
            )

            print(
                f"       {error}"
            )

        # ----------------------------------------------------
        # KEEP CUSTOMER POSITIONED
        # ----------------------------------------------------

        position_customer(
            active_customer
        )

        # ----------------------------------------------------
        # CUSTOMER LEFT
        # ----------------------------------------------------

        if (
            old_state
            == CustomerState.WAITING
            and
            active_customer.state
            == CustomerState.LEAVING
        ):

            print(
                "[CUSTOMER] Customer left "
                "without receiving the correct drink."
            )

            try:

                mixing_station.reset()

            except Exception:

                pass

        # ----------------------------------------------------
        # CUSTOMER FINISHED
        # ----------------------------------------------------

        try:

            if (
                active_customer.is_finished()
            ):

                active_customer = None

                spawn_timer = (
                    SPAWN_DELAY
                )

        except Exception as error:

            print(
                "[CUSTOMER] Finished-state warning:"
            )

            print(
                f"       {error}"
            )

    # ========================================================
    # SPAWN NEXT CUSTOMER
    # ========================================================

    if (
        running
        and active_customer is None
    ):

        spawn_timer -= dt

        if spawn_timer <= 0:

            active_bg = (
                load_level_background(
                    progression.level
                )
            )

            active_customer = (
                refresh_customer(
                    progression.level,
                    mixing_station,
                )
            )

            spawn_timer = 0.0

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    if not running:

        break

    screen.blit(
        active_bg,
        (
            0,
            0,
        ),
    )

    # ========================================================
    # DRAW CUSTOMER
    # ========================================================

    if (
        active_customer is not None
    ):

        try:

            active_customer.draw(
                screen
            )

        except Exception as error:

            print(
                "[CUSTOMER DRAW ERROR]"
            )

            print(
                f"       {error}"
            )

    # ========================================================
    # DRAW MIXING STATION
    # ========================================================

    try:

        mixing_station.draw(
            screen
        )

    except Exception as error:

        print(
            "[STATION ERROR] "
            "Draw exception:"
        )

        print(
            f"       {error}"
        )

    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()


# ============================================================
# SHUTDOWN
# ============================================================

print(
    "[MAIN] Shutting down Cyberpunk Café."
)


pygame.quit()

sys.exit()
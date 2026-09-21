"""
============================================================
CYBERPUNK CAFÉ
MAIN GAME ENGINE
============================================================

MASTER GAME FLOW
------------------------------------------------------------

START SCREEN
        ↓
INITIAL LOADING
        ↓
LEVEL 1 GAMEPLAY
        ↓
CUSTOMER
        ↓
DRINK MIXING
        ↓
SERVE
        ↓
ACCURACY
        ↓
REWARD
        ↓
XP / CREDITS
        ↓
LEVEL UP?
     /       \
   NO         YES
   ↓           ↓
NEXT       LEVEL UNLOCK
CUSTOMER        ↓
             LOADING
                ↓
             NEW LEVEL
                ↓
           NEW CUSTOMER


FINAL LEVELS
------------------------------------------------------------

LEVEL 1
Back Alley Kiosk

LEVEL 2
Neon Lounge

LEVEL 3
Cyber Penthouse

LEVEL 3 is the maximum.


IMPORTANT CUSTOMER RULE
------------------------------------------------------------

customer.py owns customer movement.

main.py ONLY initializes the customer's starting position.

main.py must NOT repeatedly overwrite:

    customer.current_y
    customer.rect.bottom

during the main game loop.

Otherwise the customer cannot finish leaving
after being served.


MUSIC RULE
------------------------------------------------------------

The music starts from the Start Screen.

main.py keeps the same music playing.

The music is NOT restarted when:

    • gameplay starts
    • Level Unlock Screen appears
    • Loading Screen appears
    • Level 2 begins
    • Level 3 begins
    • Map opens
    • Leaderboard opens

============================================================
"""

import sys
import os
import pygame


# ============================================================
# IMPORT GAME SYSTEMS
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
# INITIALISE PYGAME
# ============================================================

pygame.init()


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# MASTER GAME SIZE
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
    "Cyberpunk Café - Game Engine (16:9)"
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
    Load the background belonging to the player's level.

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

        level_num = int(
            level_num
        )

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

        return bg_cache[
            level_num
        ]

    # --------------------------------------------------------
    # FILE PATH
    # --------------------------------------------------------

    relative_path = (
        LEVEL_BACKGROUNDS.get(
            level_num,
            LEVEL_BACKGROUNDS[1],
        )
    )

    path = os.path.join(
        PROJECT_ROOT,
        relative_path,
    )

    # --------------------------------------------------------
    # LOAD IMAGE
    # --------------------------------------------------------

    try:

        raw_image = pygame.image.load(
            path
        ).convert_alpha()

        scaled_image = (
            pygame.transform.smoothscale(
                raw_image,
                (
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                ),
            )
        )

        bg_cache[
            level_num
        ] = scaled_image

        print(
            "[MAIN] Loaded Level "
            f"{level_num} background:"
        )

        print(
            f"       {path}"
        )

        return scaled_image

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    except (
        pygame.error,
        FileNotFoundError,
    ) as error:

        print(
            "[MAIN] Could not load background:"
        )

        print(
            f"       {path}"
        )

        print(
            f"       {error}"
        )

        fallback = pygame.Surface(
            (
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
            )
        )

        fallback.fill(
            (
                25,
                15,
                35,
            )
        )

        bg_cache[
            level_num
        ] = fallback

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

    This function does NOT restart the music when music is
    already playing.

    Therefore the same music continues through:

        Start Screen
        Gameplay
        Unlock Screen
        Loading Screen
        Level 2
        Level 3
    """

    try:

        # ----------------------------------------------------
        # INITIALISE MIXER IF NECESSARY
        # ----------------------------------------------------

        if not pygame.mixer.get_init():

            pygame.mixer.init()

        # ----------------------------------------------------
        # DEFAULT VOLUME
        # ----------------------------------------------------

        volume = 0.30

        muted = False

        # ----------------------------------------------------
        # USE START SCREEN SETTINGS
        # ----------------------------------------------------

        if start_screen is not None:

            try:

                volume = float(
                    getattr(
                        start_screen,
                        "music_volume",
                        0.30,
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
        # CLAMP VOLUME
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
        # ALREADY PLAYING
        # ----------------------------------------------------

        if pygame.mixer.music.get_busy():

            return True

        # ----------------------------------------------------
        # CHECK MUSIC FILE
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
        # LOAD AND PLAY
        # ----------------------------------------------------

        pygame.mixer.music.load(
            MUSIC_FILE
        )

        pygame.mixer.music.play(
            -1
        )

        print(
            "[AUDIO] Cyberpunk Café music "
            "started/continued."
        )

        return True

    except pygame.error as error:

        print(
            "[AUDIO ERROR]"
        )

        print(
            f"       {error}"
        )

        return False


# ============================================================
# CUSTOMER INITIAL POSITION
# ============================================================

def position_customer(
    customer,
):
    """
    Set the customer's INITIAL position.

    IMPORTANT:

    This function is called only when a customer is created.

    It is NOT called every frame.

    customer.py controls the customer's movement after this.
    """

    if customer is None:

        return

    try:

        # ----------------------------------------------------
        # CUSTOMER X POSITION
        # ----------------------------------------------------

        customer_x = 180

        # ----------------------------------------------------
        # COUNTER POSITION
        # ----------------------------------------------------

        counter_bottom = 690

        # ----------------------------------------------------
        # BASIC POSITION DATA
        # ----------------------------------------------------

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

        customer.current_y = (
            customer.spawn_y
        )

        # ----------------------------------------------------
        # INITIAL RECTANGLE
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
    Create a new customer.

    Customer.py owns:

        • order generation
        • patience
        • movement
        • FSM
        • serving
        • leaving
    """

    customer = Customer(
        current_level=level
    )

    # --------------------------------------------------------
    # INITIAL POSITION ONLY
    # --------------------------------------------------------

    position_customer(
        customer
    )

    return customer


# ============================================================
# SEND CUSTOMER ORDER TO STATION
# ============================================================

def sync_station_order(
    mixing_station,
    customer,
):
    """
    Give the current customer order to the Mixing Station.
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
    # SEND TO STATION
    # --------------------------------------------------------

    if order is not None:

        mixing_station.set_customer_order(
            order
        )


# ============================================================
# CREATE AND SYNC CUSTOMER
# ============================================================

def refresh_customer(
    level,
    mixing_station,
):
    """
    Create a customer and immediately give their order
    to the Mixing Station.
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
# SYNCHRONISE LEVEL SYSTEMS
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
    # STATION
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
    Open the existing Map system.

    After returning:

        • progression is synchronized
        • background is refreshed
        • a new customer is created
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
    # SYNC FROM ECONOMY
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

    active_bg = (
        load_level_background(
            progression.level
        )
    )

    # --------------------------------------------------------
    # NEW CUSTOMER
    # --------------------------------------------------------

    active_customer = (
        refresh_customer(
            progression.level,
            mixing_station,
        )
    )

    # --------------------------------------------------------
    # MUSIC
    # --------------------------------------------------------

    ensure_game_music()

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
    Open the existing Leaderboard system.
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
    # SYNC FROM ECONOMY
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

    active_bg = (
        load_level_background(
            progression.level
        )
    )

    # --------------------------------------------------------
    # NEW CUSTOMER
    # --------------------------------------------------------

    active_customer = (
        refresh_customer(
            progression.level,
            mixing_station,
        )
    )

    # --------------------------------------------------------
    # MUSIC
    # --------------------------------------------------------

    ensure_game_music()

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
    Debug/manual level switch.

    This is NOT the normal progression system.

    Normal gameplay uses XP to advance levels.
    """

    try:

        level = int(
            level
        )

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
    # ECONOMY
    # --------------------------------------------------------

    economy.set_level(
        level
    )

    # --------------------------------------------------------
    # PROGRESSION
    # --------------------------------------------------------

    progression.level = (
        level
    )

    progression.xp = 0

    # --------------------------------------------------------
    # ECONOMY XP
    # --------------------------------------------------------

    try:

        economy.xp = 0

    except Exception:

        pass

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        economy.save_economy_data()

    except Exception as error:

        print(
            "[MAIN] Manual level save warning:"
        )

        print(
            f"       {error}"
        )

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

    active_bg = (
        load_level_background(
            level
        )
    )

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    active_customer = (
        refresh_customer(
            level,
            mixing_station,
        )
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
    Run the COMPLETE level-up sequence.

    IMPORTANT:

    Normal gameplay is paused while this function runs.

    Sequence:

        Level Up
            ↓
        Level Unlock Screen
            ↓
        Loading Screen
            ↓
        New Background
            ↓
        New Customer
            ↓
        Resume Gameplay

    Music is intentionally kept alive.
    """

    # --------------------------------------------------------
    # SAFE LEVEL
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
        "[MAIN] LEVEL TRANSITION START"
    )

    print(
        f"[MAIN] New Level: {new_level}"
    )

    print(
        "================================================"
    )

    # --------------------------------------------------------
    # MAKE SURE MUSIC IS RUNNING
    # --------------------------------------------------------

    ensure_game_music()

    # ========================================================
    # LEVEL UNLOCK
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
                "[MAIN] Unlock screen requested quit."
            )

            return None

    # --------------------------------------------------------
    # KEEP MUSIC
    # --------------------------------------------------------

    ensure_game_music()

    # ========================================================
    # LOADING
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

        return None

    # --------------------------------------------------------
    # KEEP MUSIC
    # --------------------------------------------------------

    ensure_game_music()

    # ========================================================
    # SET NEW LEVEL
    # ========================================================

    progression.level = (
        new_level
    )

    # ========================================================
    # SYNCHRONISE SYSTEMS
    # ========================================================

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

    except Exception as error:

        print(
            "[MAIN] Station reset warning:"
        )

        print(
            f"       {error}"
        )

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
    # NEW BACKGROUND
    # ========================================================

    active_bg = (
        load_level_background(
            new_level
        )
    )

    # ========================================================
    # NEW CUSTOMER
    # ========================================================

    active_customer = (
        refresh_customer(
            new_level,
            mixing_station,
        )
    )

    # ========================================================
    # SAVE
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
            "[MAIN] Level save warning:"
        )

        print(
            f"       {error}"
        )

    # ========================================================
    # SHOW NEW LEVEL ONCE
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

    except Exception:

        pass

    try:

        mixing_station.draw(
            screen
        )

    except Exception:

        pass

    pygame.display.flip()

    # ========================================================
    # FINAL MUSIC CHECK
    # ========================================================

    ensure_game_music()

    print(
        f"[MAIN] LEVEL {new_level} "
        "TRANSITION COMPLETE."
    )

    print(
        "[MAIN] Returning to gameplay."
    )

    print()

    return (
        active_bg,
        active_customer,
    )


# ============================================================
# START SCREEN
# ============================================================

start_screen = StartScreen(
    screen
)


player_name = start_screen.run()


# ============================================================
# EXIT FROM START SCREEN
# ============================================================

if player_name is None:

    pygame.quit()

    sys.exit()


# ============================================================
# MUSIC HANDOFF
# ============================================================
#
# StartScreen has already been responsible for starting
# the music.
#
# We now keep it alive from the main game.
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
# FINAL LEVEL SAFETY
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
# LEVEL UNLOCK SCREEN
# ============================================================

level_unlock_screen = (
    LevelUnlockScreen(
        screen
    )
)


# ============================================================
# LOADING SCREEN
# ============================================================

loading_screen = LoadingScreen(
    screen
)


# ============================================================
# INITIAL SYNCHRONISATION
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
# MUSIC AFTER INITIAL LOADING
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
# INITIAL SYNCHRONISATION WITH STATION
# ============================================================

sync_level_systems(
    economy,
    progression,
    mixing_station,
)


# ============================================================
# INITIAL BACKGROUND
# ============================================================

active_bg = (
    load_level_background(
        progression.level
    )
)


# ============================================================
# FIRST CUSTOMER
# ============================================================

active_customer = (
    refresh_customer(
        progression.level,
        mixing_station,
    )
)


# ============================================================
# CUSTOMER SPAWN TIMER
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
        # MIXING STATION INPUT
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
                mixing_station
                .consume_map_request()
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

        except Exception as error:

            print(
                "[LEADERBOARD ERROR]"
            )

            print(
                f"       {error}"
            )


        # ====================================================
        # KEYBOARD
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

                # ---------------------------------------------
                # SYNC
                # ---------------------------------------------

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

                # ---------------------------------------------
                # BACKGROUND
                # ---------------------------------------------

                active_bg = (
                    load_level_background(
                        progression.level
                    )
                )

                # ---------------------------------------------
                # CUSTOMER
                # ---------------------------------------------

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
    # SERVED DRINK PROCESSING
    # ========================================================

    if mixing_station.served:

        # ----------------------------------------------------
        # ONLY PROCESS IF A CUSTOMER IS PRESENT
        # ----------------------------------------------------

        if (
            active_customer is not None
        ):

            # ------------------------------------------------
            # ONLY PROCESS A WAITING CUSTOMER
            # ------------------------------------------------

            if (
                active_customer.state
                == CustomerState.WAITING
            ):

                # =============================================
                # PLAYER DRINK DATA
                # =============================================

                player_drink_data = (
                    mixing_station
                    .get_player_drink_data()
                )

                # =============================================
                # CUSTOMER ORDER
                # =============================================

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

                # =============================================
                # ACCURACY
                # =============================================

                accuracy_result = (
                    OrderAccuracy.check_order(
                        customer_order,
                        player_drink_data,
                    )
                )

                # =============================================
                # SPEED
                # =============================================

                try:

                    served_quickly = (
                        active_customer
                        .served_quickly()
                    )

                except Exception:

                    served_quickly = False

                # =============================================
                # REWARD
                # =============================================

                reward_result = (
                    reward_system.calculate_reward(
                        accuracy_result,
                        served_quickly=(
                            served_quickly
                        ),
                    )
                )

                # =============================================
                # OLD LEVEL
                # =============================================

                old_level = (
                    progression.level
                )

                # =============================================
                # ADD / REMOVE XP
                # =============================================

                progression.add_xp(
                    reward_result.total_xp
                )

                # =============================================
                # CREDITS
                # =============================================

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

                # =============================================
                # NEW LEVEL
                # =============================================

                new_level = (
                    progression.level
                )

                level_changed = (
                    new_level
                    > old_level
                )

                # =============================================
                # SYNC
                # =============================================

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

                try:

                    mixing_station.set_progression(
                        progression
                    )

                except Exception:

                    pass

                try:

                    mixing_station.set_level(
                        progression.level
                    )

                except Exception:

                    pass

                # =============================================
                # SAVE
                # =============================================

                try:

                    economy.save_economy_data()

                except Exception as error:

                    print(
                        "[MAIN] Save warning:"
                    )

                    print(
                        f"       {error}"
                    )

                # =============================================
                # CUSTOMER REACTION
                # =============================================

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

                # =============================================
                # REWARD HUD
                # =============================================

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

                # =============================================
                # TERMINAL INFORMATION
                # =============================================

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

                # ---------------------------------------------
                # XP PENALTY
                # ---------------------------------------------

                if getattr(
                    reward_result,
                    "xp_penalty",
                    0,
                ) > 0:

                    print(
                        f"XP Penalty Applied: "
                        f"-{reward_result.xp_penalty}"
                    )

                # ---------------------------------------------
                # CREDIT PENALTY
                # ---------------------------------------------

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

                try:

                    current_location = (
                        progression
                        .get_current_location()
                    )

                except Exception:

                    current_location = (
                        "Unknown"
                    )

                print(
                    f"Current Location: "
                    f"{current_location}"
                )

                print(
                    "----------------------------------------"
                )

                # =============================================
                # LEVEL-UP TRANSITION
                # =============================================

                if level_changed:

                    print(
                        f"[LEVEL UP] "
                        f"Level {old_level} "
                        f"-> {new_level}"
                    )

                    # -----------------------------------------
                    # VERY IMPORTANT:
                    #
                    # We do NOT call position_customer().
                    #
                    # We let the old customer finish naturally.
                    #
                    # However, because the level transition must
                    # happen immediately after the level-up, the
                    # old customer will be replaced after the
                    # transition.
                    # -----------------------------------------

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

                    # -----------------------------------------
                    # PLAYER CLOSED GAME
                    # -----------------------------------------

                    if (
                        transition_result
                        is None
                    ):

                        running = False

                    # -----------------------------------------
                    # SUCCESS
                    # -----------------------------------------

                    else:

                        (
                            active_bg,
                            active_customer,
                        ) = (
                            transition_result
                        )

                        spawn_timer = 0.0

                # =============================================
                # NORMAL ORDER COMPLETION
                # =============================================

                else:

                    # ------------------------------------------------
                    # DO NOT REPLACE THE CUSTOMER HERE.
                    #
                    # customer.py now controls its leaving animation.
                    # ------------------------------------------------

                    pass

        # ----------------------------------------------------
        # RESET STATION AFTER SERVE PROCESSING
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

        # ----------------------------------------------------
        # SAVE OLD STATE
        # ----------------------------------------------------

        old_state = (
            active_customer.state
        )

        # ----------------------------------------------------
        # CUSTOMER OWNS MOVEMENT
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
        # CUSTOMER RAN OUT OF PATIENCE
        # ----------------------------------------------------

        if (
            old_state
            == CustomerState.WAITING
            and
            active_customer.state
            == CustomerState.LEAVING
        ):

            print(
                "[CUSTOMER] "
                "Customer left without receiving "
                "the correct drink."
            )

            try:

                mixing_station.reset()

            except Exception:

                pass

        # ----------------------------------------------------
        # CUSTOMER FINISHED LEAVING
        # ----------------------------------------------------

        try:

            if (
                active_customer.is_finished()
            ):

                print(
                    "[CUSTOMER] "
                    "Customer finished leaving."
                )

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

            # ------------------------------------------------
            # CURRENT LEVEL BACKGROUND
            # ------------------------------------------------

            active_bg = (
                load_level_background(
                    progression.level
                )
            )

            # ------------------------------------------------
            # NEW CUSTOMER
            # ------------------------------------------------

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
# CLEAN SHUTDOWN
# ============================================================

print(
    "[MAIN] Shutting down Cyberpunk Café."
)

pygame.quit()

sys.exit()
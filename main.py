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
# MASTER GAME SIZE
# ============================================================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
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
# LEVEL BACKGROUNDS
# ============================================================

LEVEL_BACKGROUNDS = {
    1: "assets/places/cafe_lvl1.png",
    2: "assets/places/cafe_lvl2.png",
    3: "assets/places/cafe_lvl3.png",
}

bg_cache = {}


def load_level_background(level_num):
    """
    Load and cache the background for the current level.
    """

    if level_num in bg_cache:
        return bg_cache[level_num]

    relative_path = LEVEL_BACKGROUNDS.get(
        level_num,
        LEVEL_BACKGROUNDS[1],
    )

    path = os.path.join(
        PROJECT_ROOT,
        relative_path,
    )

    try:

        raw_img = pygame.image.load(
            path
        ).convert_alpha()

        scaled_img = pygame.transform.scale(
            raw_img,
            (
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
            ),
        )

        bg_cache[level_num] = scaled_img

        return scaled_img

    except (
        pygame.error,
        FileNotFoundError,
    ):

        print(
            f"[MAIN] Could not load background: {path}"
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

        bg_cache[level_num] = fallback

        return fallback


# ============================================================
# CUSTOMER HELPERS
# ============================================================

def create_customer(level):
    """
    Create a customer for the current level.
    """

    customer = Customer(
        current_level=level
    )

    position_customer(
        customer,
        spawning=True,
    )

    return customer


def position_customer(
    customer,
    spawning=False,
):
    """
    Put the customer in the lower-left café area.

    The customer is positioned above the counter rather than
    in the middle of the screen.

    We only initialise the movement coordinates here. We do
    not overwrite the customer's rectangle every frame,
    because customer.py controls the movement animation.
    """

    if customer is None:
        return

    try:

        # ----------------------------------------------------
        # FINAL COUNTER POSITION
        # ----------------------------------------------------

        counter_bottom = 690
        customer_x = 180

        customer.x = customer_x
        customer.y_counter = counter_bottom

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

        if hasattr(customer, "rect"):

            customer.rect.centerx = (
                customer_x
            )

            customer.rect.bottom = int(
                customer.current_y
            )

    except Exception as e:

        print(
            f"[MAIN] Customer positioning warning: {e}"
        )


def sync_station_order(
    mixing_station,
    customer,
):
    """
    Give the current customer order to the station.
    """

    if customer is None:
        return

    order = getattr(
        customer,
        "order",
        None,
    )

    if order is None:

        order = getattr(
            customer,
            "current_order",
            None,
        )

    if order is not None:

        mixing_station.set_customer_order(
            order
        )


# ============================================================
# SYSTEM SYNCHRONISATION
# ============================================================

def sync_level_systems(
    economy,
    progression,
    mixing_station,
):
    """
    Keep Economy, Progression and MixingStation synchronized.
    """

    try:

        economy.sync_progression(
            progression
        )

    except Exception as e:

        print(
            f"[MAIN] Economy sync warning: {e}"
        )

    try:

        mixing_station.set_progression(
            progression
        )

    except Exception as e:

        print(
            f"[MAIN] Station progression sync warning: {e}"
        )

    try:

        mixing_station.set_level(
            progression.level
        )

    except Exception as e:

        print(
            f"[MAIN] Station level sync warning: {e}"
        )


# ============================================================
# REFRESH CURRENT CUSTOMER
# ============================================================

def refresh_customer(
    level,
    mixing_station,
):
    """
    Create a fresh customer and give their order to the station.
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
# MAP
# ============================================================

def open_map(
    screen,
    map_manager,
    economy,
    progression,
    mixing_station,
):
    """
    Open the Map screen and synchronize the game afterward.
    """

    map_screen = MapScreen(
        screen,
        map_manager,
        economy,
    )

    map_screen.run()

    progression.level = economy.level
    progression.xp = economy.xp

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
# LEADERBOARD
# ============================================================

def open_leaderboard(
    screen,
    leaderboard_manager,
    economy,
    progression,
    mixing_station,
):
    """
    Open the Leaderboard screen and return to gameplay.
    """

    leaderboard_screen = LeaderboardScreen(
        screen,
        leaderboard_manager,
        economy,
    )

    leaderboard_screen.run()

    progression.level = economy.level
    progression.xp = economy.xp

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
# LEVEL SWITCH
# ============================================================

def switch_level(
    level,
    economy,
    progression,
    mixing_station,
):
    """
    Switch the active game to a requested unlocked level.
    """

    economy.set_level(
        level
    )

    progression.level = level

    # Keyboard level switching is treated as a manual
    # location selection, so the XP for the selected test
    # level is reset exactly as in the existing system.
    progression.xp = 0

    try:
        economy.xp = 0
    except Exception:
        pass

    economy.save_economy_data()

    sync_level_systems(
        economy,
        progression,
        mixing_station,
    )

    active_bg = load_level_background(
        level
    )

    active_customer = refresh_customer(
        level,
        mixing_station,
    )

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

if player_name is None:

    pygame.quit()
    sys.exit()


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

leaderboard_manager = LeaderboardManager(
    economy_ref=economy
)


# ============================================================
# LOADING SCREEN
# ============================================================

loading_screen = LoadingScreen(
    screen
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

    dt = clock.tick(
        FPS
    ) / 1000.0


    # ========================================================
    # EVENT LOOP
    # ========================================================

    for event in pygame.event.get():

        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # ----------------------------------------------------
        # MIXING STATION INPUT
        # ----------------------------------------------------

        try:

            mixing_station.handle_event(
                event
            )

        except Exception as e:

            print(
                f"[STATION ERROR] "
                f"Event handling exception: {e}"
            )


        # ====================================================
        # VISIBLE MAP BUTTON
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

        except Exception as e:

            print(
                f"[MAP BUTTON ERROR] {e}"
            )


        # ====================================================
        # VISIBLE LEADERBOARD BUTTON
        # ====================================================

        try:

            if (
                mixing_station.consume_leaderboard_request()
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

        except Exception as e:

            print(
                f"[LEADERBOARD BUTTON ERROR] {e}"
            )


        # ====================================================
        # KEYBOARD
        # ====================================================

        if event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # R = RESET
            # ------------------------------------------------

            if event.key == pygame.K_r:

                print(
                    "[MAIN] Resetting game..."
                )

                economy.reset_economy()

                progression.reset()

                reward_system.reset()

                mixing_station.reset()

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


            # ------------------------------------------------
            # M = MAP
            # ------------------------------------------------

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

                except Exception as e:

                    print(
                        f"[MAP ERROR] {e}"
                    )


            # ------------------------------------------------
            # L = LEADERBOARD
            # ------------------------------------------------

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

                except Exception as e:

                    print(
                        f"[LEADERBOARD ERROR] {e}"
                    )


            # ------------------------------------------------
            # 1 = LEVEL 1
            # ------------------------------------------------

            elif event.key == pygame.K_1:

                node = map_manager.nodes.get(
                    "neon_alley"
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


            # ------------------------------------------------
            # 2 = LEVEL 2
            # ------------------------------------------------

            elif event.key == pygame.K_2:

                node = map_manager.nodes.get(
                    "cyber_dock"
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


            # ------------------------------------------------
            # 3 = LEVEL 3
            # ------------------------------------------------

            elif event.key == pygame.K_3:

                node = map_manager.nodes.get(
                    "high_rise"
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


    # ========================================================
    # UPDATE MIXING STATION
    # ========================================================

    try:

        mixing_station.update(
            dt
        )

    except Exception as e:

        print(
            f"[STATION ERROR] "
            f"Update exception: {e}"
        )


    # ========================================================
    # SERVE COMPLETED DRINK
    # ========================================================

    if mixing_station.served:

        if active_customer is not None:

            if (
                active_customer.state
                == CustomerState.WAITING
            ):

                # ------------------------------------------------
                # PLAYER DRINK
                # ------------------------------------------------

                player_drink_data = (
                    mixing_station.get_player_drink_data()
                )

                # ------------------------------------------------
                # CUSTOMER ORDER
                # ------------------------------------------------

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

                # ------------------------------------------------
                # ACCURACY
                # ------------------------------------------------

                accuracy_result = (
                    OrderAccuracy.check_order(
                        customer_order,
                        player_drink_data,
                    )
                )

                # ------------------------------------------------
                # REAL CUSTOMER SPEED
                # ------------------------------------------------
                #
                # Customer.py now owns the 15-second timer.
                #
                # served_quickly() checks whether the customer
                # still has at least 50% of their patience.
                #

                try:

                    served_quickly = (
                        active_customer.served_quickly()
                    )

                except Exception:

                    served_quickly = False

                # ------------------------------------------------
                # REWARD
                # ------------------------------------------------

                reward_result = (
                    reward_system.calculate_reward(
                        accuracy_result,
                        served_quickly=served_quickly,
                    )
                )

                # ------------------------------------------------
                # LEVEL / XP
                # ------------------------------------------------

                old_level = (
                    progression.level
                )

                progression.add_xp(
                    reward_result.total_xp
                )

                # ------------------------------------------------
                # CREDITS
                # ------------------------------------------------

                economy.apply_reward(
                    reward_result
                )

                # ------------------------------------------------
                # SYNC
                # ------------------------------------------------

                economy.sync_progression(
                    progression
                )

                mixing_station.set_progression(
                    progression
                )

                mixing_station.set_level(
                    progression.level
                )

                # ------------------------------------------------
                # SAVE
                # ------------------------------------------------

                economy.save_economy_data()

                # ------------------------------------------------
                # CUSTOMER REACTION
                # ------------------------------------------------

                try:

                    active_customer.serve_drink(
                        player_drink_data
                    )

                except Exception as e:

                    print(
                        f"[CUSTOMER] "
                        f"Serve reaction warning: {e}"
                    )

                # ------------------------------------------------
                # HUD REWARD FEEDBACK
                # ------------------------------------------------

                try:

                    mixing_station.set_reward_feedback(
                        xp_delta=reward_result.total_xp,
                        credit_delta=reward_result.net_credits,
                    )

                except Exception as e:

                    print(
                        f"[HUD] Reward feedback warning: {e}"
                    )

                # ------------------------------------------------
                # LEVEL-UP
                # ------------------------------------------------

                if progression.level > old_level:

                    print(
                        f"[LEVEL UP] "
                        f"Level {old_level} -> "
                        f"{progression.level}"
                    )

                    economy.sync_progression(
                        progression
                    )

                    mixing_station.set_progression(
                        progression
                    )

                    mixing_station.set_level(
                        progression.level
                    )

                    active_bg = (
                        load_level_background(
                            progression.level
                        )
                    )

                    # --------------------------------------------
                    # SHOW LOADING SCREEN FOR THE NEW LEVEL
                    # --------------------------------------------

                    try:

                        loading_ok = (
                            loading_screen.run(
                                player_name=player_name,
                                level=progression.level,
                                duration=6.7,
                            )
                        )

                        if not loading_ok:

                            running = False

                    except Exception as e:

                        print(
                            f"[LOADING] "
                            f"Level transition warning: {e}"
                        )

                # ------------------------------------------------
                # TERMINAL RESULT
                # ------------------------------------------------

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

                print(
                    f"XP Earned: "
                    f"+{reward_result.total_xp}"
                )

                print(
                    f"Credits Change: "
                    f"{reward_result.net_credits:+}"
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
                    "----------------------------------------"
                )

        # ----------------------------------------------------
        # RESET STATION
        # ----------------------------------------------------

        mixing_station.reset()


    # ========================================================
    # CUSTOMER UPDATE
    # ========================================================

    if active_customer is not None:

        old_state = (
            active_customer.state
        )

        active_customer.update(
            dt
        )

        # ----------------------------------------------------
        # CUSTOMER RAN OUT OF PATIENCE
        # ----------------------------------------------------

        if (
            old_state == CustomerState.WAITING
            and active_customer.state
            == CustomerState.LEAVING
        ):

            print(
                "[CUSTOMER] Customer left "
                "without receiving the correct drink."
            )

            mixing_station.reset()

        # ----------------------------------------------------
        # CUSTOMER FINISHED
        # ----------------------------------------------------

        if active_customer.is_finished():

            active_customer = None

            spawn_timer = (
                SPAWN_DELAY
            )


    # ========================================================
    # SPAWN NEXT CUSTOMER
    # ========================================================

    else:

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


    # ========================================================
    
    # DRAW BACKGROUND
    # ========================================================

    screen.blit(
        active_bg,
        (0, 0),
    )


    # ========================================================
    # DRAW CUSTOMER
    # ========================================================

    if active_customer is not None:

        try:

            active_customer.draw(
                screen
            )

        except Exception as e:

            print(
                f"[CUSTOMER DRAW ERROR] {e}"
            )


    # ========================================================
    # DRAW MIXING STATION
    # ========================================================

    try:

        mixing_station.draw(
            screen
        )

    except Exception as e:

        print(
            f"[STATION ERROR] "
            f"Draw exception: {e}"
        )


    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()


# ============================================================
# SHUTDOWN
# ============================================================

pygame.quit()

sys.exit()

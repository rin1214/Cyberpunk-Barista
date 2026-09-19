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


# Cache prevents the same background image from being loaded
# from disk every time we create a new customer.

bg_cache = {}


def load_level_background(level_num):
    """
    Loads the correct café background for the current level.

    If the image has already been loaded, we reuse it from
    bg_cache instead of loading it again.
    """

    # --------------------------------------------------------
    # CHECK CACHE
    # --------------------------------------------------------

    if level_num in bg_cache:

        return bg_cache[level_num]

    # --------------------------------------------------------
    # FIND FILE
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
    # LOAD IMAGE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

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
# HELPER FUNCTIONS
# ============================================================

def create_customer(level):
    """
    Creates a new customer using the current level.

    Keeping customer creation in one function makes it much
    easier to change customer positioning/initialisation later.
    """

    customer = Customer(
        current_level=level
    )

    return customer


def position_customer(customer):
    """
    Controls where the customer appears on the café screen.

    IMPORTANT:
        Customer positioning belongs to main.py.

    station.py only draws the mixing station and current order.
    """

    if customer is None:
        return

    # --------------------------------------------------------
    # CUSTOMER POSITION
    # --------------------------------------------------------
    #
    # The exact Customer drawing system may use its own
    # internal rectangle. We safely check for common
    # possibilities before changing it.

    if hasattr(customer, "rect"):

        try:

            customer.rect.center = (
                230,
                330,
            )

        except Exception:
            pass

    elif hasattr(customer, "x") and hasattr(customer, "y"):

        try:
            customer.x = 230
            customer.y = 430

        except Exception:
            pass


def sync_station_order(
    mixing_station,
    customer,
):
    """
    Sends the customer's current order to the mixing station.

    The customer system remains the owner of the order.
    The station only displays and uses a copy/reference.
    """

    if customer is None:
        return

    order = getattr(
        customer,
        "order",
        None,
    )

    # Some versions of Customer may expose the order under
    # another name. Try current_order as a compatibility option.

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


def sync_level_systems(
    economy,
    progression,
    mixing_station,
):
    """
    Keeps the economy, progression and mixing station aware
    of the same current level.

    Progression owns actual XP/level progression.

    UIEconomy keeps the saved player profile/location.

    MixingStation only reads the current level so it knows
    which drinks should be unlocked.
    """

    # --------------------------------------------------------
    # PROGRESSION → ECONOMY
    # --------------------------------------------------------

    try:

        economy.sync_progression(
            progression
        )

    except Exception as e:

        print(
            f"[MAIN] Economy progression sync warning: {e}"
        )

    # --------------------------------------------------------
    # PROGRESSION → STATION
    # --------------------------------------------------------

    try:

        mixing_station.set_progression(
            progression
        )

    except Exception as e:

        print(
            f"[MAIN] Station progression sync warning: {e}"
        )

    # --------------------------------------------------------
    # LEVEL
    # --------------------------------------------------------

    mixing_station.set_level(
        progression.level
    )


# ============================================================
# START SCREEN
# ============================================================

start_screen = StartScreen(
    screen
)

player_name = start_screen.run()


# ------------------------------------------------------------
# PLAYER CLOSED START SCREEN
# ------------------------------------------------------------

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
#
# UIEconomy stores the player's saved level/XP.
#
# Progression becomes the system responsible for actually
# calculating XP and level-ups.
#

progression = Progression(
    level=economy.level,
    xp=economy.xp,
)


# ============================================================
# REWARD SYSTEM
# ============================================================
#
# RewardSystem calculates:
#
#     base XP
#     base credits
#     combo bonus
#     speed bonus
#     mistake penalty
#
# It does NOT control the player's level.
#

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


# ------------------------------------------------------------
# LOADING FAILED / CANCELLED
# ------------------------------------------------------------

if not loading_ok:

    pygame.quit()
    sys.exit()


# ============================================================
# LEGACY DRINK OBJECT
# ============================================================
#
# This is retained because other collaborator code may still
# reference Drink.
#
# The new mixing station itself uses PlayerDrink.
#

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
# BACKGROUND
# ============================================================

active_bg = load_level_background(
    progression.level
)


# ============================================================
# FIRST CUSTOMER
# ============================================================

active_customer = create_customer(
    progression.level
)

position_customer(
    active_customer
)

sync_station_order(
    mixing_station,
    active_customer,
)


# ============================================================
# CUSTOMER SPAWN SETTINGS
# ============================================================

spawn_timer = 0.0

SPAWN_DELAY = 1.5


# ============================================================
# GAME LOOP
# ============================================================

running = True


while running:

    # ========================================================
    # DELTA TIME
    # ========================================================
    #
    # dt = time since the previous frame.
    #
    # Dividing milliseconds by 1000 converts them to seconds.
    #

    dt = clock.tick(
        FPS
    ) / 1000.0


    # ========================================================
    # EVENT LOOP
    # ========================================================

    for event in pygame.event.get():

        # ----------------------------------------------------
        # CLOSE GAME
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
                f"[STATION ERROR] Event handling exception caught: {e}"
            )

        # ----------------------------------------------------
        # KEYBOARD INPUT
        # ----------------------------------------------------

        if event.type == pygame.KEYDOWN:

            # =================================================
            # R = RESET GAME
            # =================================================

            if event.key == pygame.K_r:

                print(
                    "[MAIN] Resetting game..."
                )

                # Reset saved economy.
                economy.reset_economy()

                # Reset progression.
                progression.reset()

                # Reset reward combo/session.
                reward_system.reset()

                # Reset mixing station.
                mixing_station.reset()

                # Update level.
                progression.level = economy.level

                # Reload background.
                active_bg = load_level_background(
                    progression.level
                )

                # Create new customer.
                active_customer = create_customer(
                    progression.level
                )

                position_customer(
                    active_customer
                )

                sync_station_order(
                    mixing_station,
                    active_customer,
                )

                spawn_timer = 0.0

            # =================================================
            # M = MAP
            # =================================================

            elif event.key == pygame.K_m:

                map_screen = MapScreen(
                    screen,
                    map_manager,
                    economy,
                )

                map_screen.run()

                # ------------------------------------------------
                # MAP MAY HAVE CHANGED LEVEL
                # ------------------------------------------------

                progression.level = economy.level

                progression.xp = economy.xp

                # ------------------------------------------------
                # REFRESH BACKGROUND
                # ------------------------------------------------

                active_bg = load_level_background(
                    progression.level
                )

                # ------------------------------------------------
                # NEW CUSTOMER
                # ------------------------------------------------

                active_customer = create_customer(
                    progression.level
                )

                position_customer(
                    active_customer
                )

                sync_station_order(
                    mixing_station,
                    active_customer,
                )

                # ------------------------------------------------
                # REFRESH STATION
                # ------------------------------------------------

                mixing_station.set_level(
                    progression.level
                )

                spawn_timer = 0.0

            # =================================================
            # L = LEADERBOARD
            # =================================================

            elif event.key == pygame.K_l:

                lb_screen = LeaderboardScreen(
                    screen,
                    leaderboard_manager,
                    economy,
                )

                lb_screen.run()

                # ------------------------------------------------
                # REFRESH GAME STATE
                # ------------------------------------------------

                active_bg = load_level_background(
                    progression.level
                )

                active_customer = create_customer(
                    progression.level
                )

                position_customer(
                    active_customer
                )

                sync_station_order(
                    mixing_station,
                    active_customer,
                )

                spawn_timer = 0.0

            # =================================================
            # 1 = LEVEL 1
            # =================================================

            elif event.key == pygame.K_1:

                node = map_manager.nodes.get(
                    "neon_alley"
                )

                if (
                    node is not None
                    and node.is_unlocked
                ):

                    economy.set_level(
                        1
                    )

                    progression.level = 1
                    progression.xp = 0

                    mixing_station.set_level(
                        1
                    )

                    active_bg = load_level_background(
                        1
                    )

                    active_customer = create_customer(
                        1
                    )

                    position_customer(
                        active_customer
                    )

                    sync_station_order(
                        mixing_station,
                        active_customer,
                    )

                    spawn_timer = 0.0

            # =================================================
            # 2 = LEVEL 2
            # =================================================

            elif event.key == pygame.K_2:

                node = map_manager.nodes.get(
                    "cyber_dock"
                )

                if (
                    node is not None
                    and node.is_unlocked
                ):

                    economy.set_level(
                        2
                    )

                    progression.level = 2
                    progression.xp = 0

                    economy.save_economy_data()

                    mixing_station.set_level(
                        2
                    )

                    active_bg = load_level_background(
                        2
                    )

                    active_customer = create_customer(
                        2
                    )

                    position_customer(
                        active_customer
                    )

                    sync_station_order(
                        mixing_station,
                        active_customer,
                    )

                    spawn_timer = 0.0

            # =================================================
            # 3 = LEVEL 3
            # =================================================

            elif event.key == pygame.K_3:

                node = map_manager.nodes.get(
                    "high_rise"
                )

                if (
                    node is not None
                    and node.is_unlocked
                ):

                    economy.set_level(
                        3
                    )

                    progression.level = 3
                    progression.xp = 0

                    economy.save_economy_data()

                    mixing_station.set_level(
                        3
                    )

                    active_bg = load_level_background(
                        3
                    )

                    active_customer = create_customer(
                        3
                    )

                    position_customer(
                        active_customer
                    )

                    sync_station_order(
                        mixing_station,
                        active_customer,
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
            f"[STATION ERROR] Update exception: {e}"
        )


    # ========================================================
    # SERVE COMPLETED DRINK
    # ========================================================
    #
    # This is one of the most important parts of the new
    # architecture.
    #
    # We DO NOT call:
    #
    #     economy.serve_order()
    #
    # because that was the old reward system.
    #
    # Instead:
    #
    #     Customer order
    #           ↓
    #     OrderAccuracy
    #           ↓
    #     RewardSystem
    #           ↓
    #     Progression
    #           ↓
    #     UIEconomy
    #

    if mixing_station.served:

        # ----------------------------------------------------
        # MAKE SURE A CUSTOMER EXISTS
        # ----------------------------------------------------

        if active_customer is not None:

            # ------------------------------------------------
            # ONLY SERVE A WAITING CUSTOMER
            # ------------------------------------------------

            if (
                active_customer.state
                == CustomerState.WAITING
            ):

                # ============================================
                # PLAYER DRINK
                # ============================================

                player_drink_data = (
                    mixing_station.get_player_drink_data()
                )

                # ============================================
                # CUSTOMER ORDER
                # ============================================

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

                # ============================================
                # ORDER ACCURACY
                # ============================================

                accuracy_result = (
                    OrderAccuracy.check_order(
                        customer_order,
                        player_drink_data,
                    )
                )

                # ============================================
                # SPEED
                # ============================================
                #
                # For now we do not invent a new timing rule.
                #
                # The reward system accepts served_quickly,
                # so this can be connected to a proper customer
                # timer later.
                #
                # We use False until the customer timing system
                # is explicitly connected.
                #

                served_quickly = False

                # ============================================
                # CALCULATE REWARD
                # ============================================

                reward_result = (
                    reward_system.calculate_reward(
                        accuracy_result,
                        served_quickly=served_quickly,
                    )
                )

                # ============================================
                # ADD XP
                # ============================================

                old_level = progression.level

                progression.add_xp(
                    reward_result.total_xp
                )

                # ============================================
                # ADD / REMOVE CREDITS
                # ============================================

                economy.apply_reward(
                    reward_result
                )

                # ============================================
                # SYNC ECONOMY WITH PROGRESSION
                # ============================================

                economy.sync_progression(
                    progression
                )

                # ============================================
                # SAVE
                # ============================================

                economy.save_economy_data()

                # ============================================
                # CUSTOMER REACTION
                # ============================================
                #
                # Customer still owns the actual customer
                # state/reaction logic.
                #
                # We let it process the served drink.
                #

                try:

                    active_customer.serve_drink(
                        player_drink_data
                    )

                except Exception as e:

                    print(
                        f"[CUSTOMER] Serve reaction warning: {e}"
                    )

                # ============================================
                # LEVEL-UP DETECTION
                # ============================================

                if progression.level > old_level:

                    print(
                        f"[LEVEL UP] "
                        f"Level {old_level} -> "
                        f"{progression.level}"
                    )

                    # Update economy.
                    economy.sync_progression(
                        progression
                    )

                    # Update station.
                    mixing_station.set_progression(
                        progression
                    )

                    mixing_station.set_level(
                        progression.level
                    )

                    # Update background.
                    active_bg = load_level_background(
                        progression.level
                    )

                # ============================================
                # DISPLAY RESULT IN TERMINAL
                # ============================================

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
        # RESET STATION AFTER SERVING
        # ----------------------------------------------------

        mixing_station.reset()

        # ----------------------------------------------------
        # WAIT FOR CUSTOMER TO FINISH LEAVING
        # ----------------------------------------------------
        #
        # We do not immediately delete the customer.
        # Customer.py remains responsible for its leaving
        # animation/state.
        #


    # ========================================================
    # CUSTOMER UPDATE
    # ========================================================

    if active_customer is not None:

        old_state = active_customer.state

        # ----------------------------------------------------
        # UPDATE CUSTOMER
        # ----------------------------------------------------

        active_customer.update(
            dt
        )

        # ----------------------------------------------------
        # KEEP CUSTOMER ON LEFT SIDE
        # ----------------------------------------------------

        position_customer(
            active_customer
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
                "[CUSTOMER] Customer left without "
                "receiving the correct drink."
            )

            # ------------------------------------------------
            # IMPORTANT
            # ------------------------------------------------
            #
            # We do NOT use economy.serve_order(False)
            # anymore.
            #
            # The RewardSystem is responsible for the reward
            # calculation when an order is actually served.
            #
            # A customer leaving is not automatically treated
            # as a served drink.
            #

            mixing_station.reset()

        # ----------------------------------------------------
        # CUSTOMER FINISHED
        # ----------------------------------------------------

        if active_customer.is_finished():

            active_customer = None

            spawn_timer = SPAWN_DELAY


    # ========================================================
    # SPAWN NEXT CUSTOMER
    # ========================================================

    else:

        spawn_timer -= dt

        if spawn_timer <= 0:

            # ------------------------------------------------
            # REFRESH BACKGROUND
            # ------------------------------------------------

            active_bg = load_level_background(
                progression.level
            )

            # ------------------------------------------------
            # CREATE CUSTOMER
            # ------------------------------------------------

            active_customer = create_customer(
                progression.level
            )

            position_customer(
                active_customer
            )

            # ------------------------------------------------
            # GIVE ORDER TO STATION
            # ------------------------------------------------

            sync_station_order(
                mixing_station,
                active_customer,
            )


    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    screen.blit(
        active_bg,
        (
            0,
            0,
        )
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
            f"[STATION ERROR] Draw exception: {e}"
        )


    # ========================================================
    # OLD ECONOMY HUD
    # ========================================================
    #
    # IMPORTANT:
    #
    # We intentionally DO NOT call:
    #
    #     economy.draw()
    #
    # here.
    #
    # The mixing station now owns the compact gameplay HUD
    # display so we don't get two different Level/XP/Credits
    # displays on the screen.
    #


    # ========================================================
    # UPDATE SCREEN
    # ========================================================

    pygame.display.flip()


# ============================================================
# SHUTDOWN
# ============================================================

pygame.quit()

sys.exit()
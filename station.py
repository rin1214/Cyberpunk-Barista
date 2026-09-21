from __future__ import annotations

import math
import os
import time

import pygame

from drink import (
    PlayerDrink,
    DRINK_MENU,
    TEMPERATURE_OPTIONS,
    CAFFEINE_OPTIONS,
    SWEETNESS_OPTIONS,
    get_recipe,
    is_drink_unlocked,
    is_valid_drink,
)

from game_state import (
    MixingGameState,
    GameState,
)


# ============================================================
# CYBERPUNK CAFÉ
# MIXING STATION
# ============================================================
#
# MASTER GAME SIZE
# 1280 x 720
#
# CLEAN / CUTE / FUTURISTIC CYBERPUNK CAFÉ UI
#
# GAME FLOW
#
# SELECT DRINK
#       ↓
# CUSTOMISE
#       ↓
# READY TO BLEND
#       ↓
# BLENDING
#       ↓
# READY TO SERVE
#       ↓
# SERVE
#
# IMPORTANT:
#
# The player can change drinks BEFORE blending.
#
# Once blending starts, the drink is locked.
#
# ============================================================


class MixingStation:

    # ========================================================
    # MASTER SIZE
    # ========================================================

    WIDTH = 1280
    HEIGHT = 720

    # ========================================================
    # COLOURS
    # ========================================================

    CYAN = (75, 225, 255)
    CYAN_LIGHT = (165, 245, 255)

    PINK = (255, 80, 190)
    PINK_LIGHT = (255, 165, 225)

    PURPLE = (185, 105, 255)

    WHITE = (245, 248, 255)
    SOFT_WHITE = (215, 222, 240)

    MUTED = (125, 140, 170)

    YELLOW = (255, 220, 100)

    GREEN = (90, 235, 165)

    LOCKED = (65, 70, 95)

    # ========================================================
    # TRANSLUCENT PANEL COLOURS
    # ========================================================

    PANEL = (7, 12, 30, 175)

    BUTTON = (9, 17, 38, 185)

    BUTTON_SELECTED = (
        65,
        15,
        65,
        205,
    )

    # ========================================================
    # INITIALISE
    # ========================================================

    def __init__(
        self,
        drink=None,
        level=1,
        progression=None,
        rewards=None,
        economy=None,
    ):

        self.drink = drink

        self.player_drink = PlayerDrink()

        self.game_state = MixingGameState()

        self.progression = progression
        self.rewards = rewards
        self.economy = economy

        self.level = max(
            1,
            int(level),
        )

        self.customer_order = None

        self.served = False

        # ====================================================
        # TOP-RIGHT NAVIGATION REQUESTS
        # ====================================================
        #
        # These flags let main.py open the full Map and
        # Leaderboard screens without coupling this station
        # directly to those screen classes.
        #
        self.map_requested = False
        self.leaderboard_requested = False

        # ====================================================
        # REWARD FEEDBACK
        # ====================================================
        #
        # main.py can update these after an order is scored.
        # They are displayed in the HUD so the player can see
        # XP/credit additions or deductions.
        #
        self.last_xp_change = 0
        self.last_credit_change = 0
        self.reward_feedback_until = 0.0

        # ====================================================
        # TIMING SLIDERS
        # ====================================================
        # Each customisation parameter has a continuously moving
        # indicator. The player clicks when the indicator reaches
        # the requested customer zone.
        self.slider_time = 0.0
        self.slider_speeds = {
            "temperature": 0.72,
            "caffeine": 0.88,
            "sweetness": 1.04,
        }
        self.slider_phases = {
            "temperature": 0.00,
            "caffeine": 0.33,
            "sweetness": 0.67,
        }
        self.slider_results = {
            "temperature": None,
            "caffeine": None,
            "sweetness": None,
        }
        self.slider_feedback = {
            "temperature": "WAITING",
            "caffeine": "WAITING",
            "sweetness": "WAITING",
        }

        # ====================================================
        # BLENDER
        # ====================================================

        self.blend_start_time = 0.0

        self.blend_duration = 1.8

        self.blender_angle = 0.0

        self.blender_pulse = 0.0

        # ====================================================
        # PROJECT PATHS
        # ====================================================

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.drink_dir = os.path.join(
            self.base_dir,
            "assets",
            "mahirah",
            "drinks",
        )

        self.font_dir = os.path.join(
            self.base_dir,
            "assets",
            "fonts",
        )

        # ====================================================
        # FONTS
        # ====================================================

        self._create_fonts()

        # ====================================================
        # DRINK IMAGES
        # ====================================================

        self.drink_images = {}

        self._load_drink_images()

        # ====================================================
        # UI LAYOUT
        # ====================================================

        self._create_layout()

        # ====================================================
        # LEGACY COMPATIBILITY
        # ====================================================

        self._attach_legacy_bridge()

    # ========================================================
    # FIND FONT
    # ========================================================

    def _find_font(
        self,
        preferred_names,
    ):

        # ----------------------------------------------------
        # SEARCH PROJECT FONT FOLDER
        # ----------------------------------------------------

        if os.path.isdir(
            self.font_dir
        ):

            all_files = []

            for root, _, files in os.walk(
                self.font_dir
            ):

                for filename in files:

                    if filename.lower().endswith(
                        (
                            ".ttf",
                            ".otf",
                        )
                    ):

                        all_files.append(
                            os.path.join(
                                root,
                                filename,
                            )
                        )

            for wanted in preferred_names:

                wanted_lower = wanted.lower()

                for path in all_files:

                    if wanted_lower in os.path.basename(
                        path
                    ).lower():

                        return path

        # ----------------------------------------------------
        # SYSTEM FONT
        # ----------------------------------------------------

        for name in preferred_names:

            try:

                path = pygame.font.match_font(
                    name
                )

                if path:

                    return path

            except Exception:

                pass

        return None

    # ========================================================
    # CREATE FONTS
    # ========================================================

    def _create_fonts(self):

        pygame.font.init()

        # ----------------------------------------------------
        # FUTURISTIC FONT
        # ----------------------------------------------------

        cyber_path = self._find_font(
            [
                "audiowide",
                "orbitron",
                "oxanium",
                "rajdhani",
                "neuropol",
            ]
        )

        # ----------------------------------------------------
        # CLEAN FONT
        # ----------------------------------------------------

        clean_path = self._find_font(
            [
                "rajdhani",
                "segoe",
                "bahnschrift",
                "trebuchet",
                "verdana",
            ]
        )

        # ----------------------------------------------------
        # MAIN UI FONT
        # ----------------------------------------------------

        if cyber_path:

            self.font_title = pygame.font.Font(
                cyber_path,
                20,
            )

            self.font_big_title = pygame.font.Font(
                cyber_path,
                22,
            )

            self.font_menu = pygame.font.Font(
                cyber_path,
                11,
            )

            self.font_button = pygame.font.Font(
                cyber_path,
                13,
            )

            self.font_hud = pygame.font.Font(
                cyber_path,
                13,
            )

        else:

            self.font_title = pygame.font.SysFont(
                "Arial",
                20,
                bold=True,
            )

            self.font_big_title = pygame.font.SysFont(
                "Arial",
                22,
                bold=True,
            )

            self.font_menu = pygame.font.SysFont(
                "Arial",
                11,
                bold=True,
            )

            self.font_button = pygame.font.SysFont(
                "Arial",
                13,
                bold=True,
            )

            self.font_hud = pygame.font.SysFont(
                "Arial",
                13,
                bold=True,
            )

        # ----------------------------------------------------
        # CLEAN LABEL FONT
        # ----------------------------------------------------

        if clean_path:

            self.font_category = pygame.font.Font(
                clean_path,
                15,
            )

            self.font_small = pygame.font.Font(
                clean_path,
                11,
            )

            self.font_medium = pygame.font.Font(
                clean_path,
                15,
            )

        else:

            self.font_category = pygame.font.SysFont(
                "Arial",
                15,
                bold=True,
            )

            self.font_small = pygame.font.SysFont(
                "Arial",
                11,
                bold=True,
            )

            self.font_medium = pygame.font.SysFont(
                "Arial",
                15,
                bold=True,
            )

    # ========================================================
    # UI LAYOUT
    # ========================================================

    def _create_layout(self):

        # ====================================================
        # TOP HUD — FLUSH TO THE TOP
        # ====================================================

        self.hud_rect = pygame.Rect(8, 4, 870, 52)

        self.map_button = pygame.Rect(900, 6, 120, 44)
        self.leaderboard_button = pygame.Rect(1030, 6, 190, 44)

        # ====================================================
        # DRINK MENU — 11% SMALLER / MORE BACKGROUND VISIBLE
        # ====================================================

        self.menu_rect = pygame.Rect(530, 62, 740, 165)
        self.menu_slots = []

        slot_width = 77
        slot_height = 135
        gap = 5
        start_x = 538
        start_y = 75

        for index, drink_name in enumerate(DRINK_MENU):
            x = start_x + index * (slot_width + gap)
            self.menu_slots.append(
                (drink_name, pygame.Rect(x, start_y, slot_width, slot_height))
            )

        # ====================================================
        # CUSTOMISE PANEL
        # ====================================================

        self.customise_rect = pygame.Rect(600, 390, 320, 300)

        # Three moving timing sliders.
        track_x = self.customise_rect.x + 25
        track_w = self.customise_rect.width - 50
        self.slider_tracks = {
            "temperature": pygame.Rect(track_x, 475, track_w, 12),
            "caffeine": pygame.Rect(track_x, 550, track_w, 12),
            "sweetness": pygame.Rect(track_x, 625, track_w, 12),
        }

        # ====================================================
        # BLENDER — PRETTY, COMPACT VERSION
        # ====================================================

        self.blender_rect = pygame.Rect(935, 390, 215, 300)
        self.blender_jug_rect = pygame.Rect(970, 465, 140, 130)
        self.blend_button = pygame.Rect(950, 632, 185, 48)

        # ====================================================
        # PREVIEW
        # ====================================================

        self.preview_rect = pygame.Rect(1160, 390, 110, 300)
        self.preview_image_rect = pygame.Rect(1170, 445, 90, 130)
        self.serve_button = pygame.Rect(1168, 632, 94, 48)

    # ========================================================
    # LOAD DRINK IMAGES
    # ========================================================

    def _load_drink_images(self):

        for drink_name in DRINK_MENU:

            filename = (
                drink_name
                .lower()
                .replace(
                    " ",
                    "_",
                )
                + ".png"
            )

            path = os.path.join(
                self.drink_dir,
                filename,
            )

            try:

                image = pygame.image.load(
                    path
                ).convert_alpha()

                self.drink_images[
                    drink_name
                ] = image

            except (
                pygame.error,
                FileNotFoundError,
            ):

                print(
                    "[STATION] Could not load "
                    f"drink image: {path}"
                )

                self.drink_images[
                    drink_name
                ] = None

    # ========================================================
    # LEVEL
    # ========================================================

    def set_level(
        self,
        level,
    ):

        try:

            self.level = max(
                1,
                int(level),
            )

        except (
            TypeError,
            ValueError,
        ):

            self.level = 1

    # ========================================================
    # PROGRESSION
    # ========================================================

    def set_progression(
        self,
        progression,
    ):

        self.progression = progression

        if progression is not None:

            self.set_level(
                getattr(
                    progression,
                    "level",
                    self.level,
                )
            )

    # ========================================================
    # REWARDS
    # ========================================================

    def set_rewards(
        self,
        rewards,
    ):

        self.rewards = rewards

    # ========================================================
    # ECONOMY
    # ========================================================

    def set_economy(
        self,
        economy,
    ):

        self.economy = economy

    # ========================================================
    # REWARD FEEDBACK
    # ========================================================

    def set_reward_feedback(
        self,
        xp_delta=0,
        credit_delta=0,
    ):
        """Show the latest XP/credit change in the HUD."""

        try:
            self.last_xp_change = int(xp_delta)
        except (TypeError, ValueError):
            self.last_xp_change = 0

        try:
            self.last_credit_change = int(credit_delta)
        except (TypeError, ValueError):
            self.last_credit_change = 0

        self.reward_feedback_until = (
            time.monotonic() + 2.5
        )

    # ========================================================
    # NAVIGATION REQUESTS
    # ========================================================

    def consume_map_request(self):
        requested = self.map_requested
        self.map_requested = False
        return requested

    def consume_leaderboard_request(self):
        requested = self.leaderboard_requested
        self.leaderboard_requested = False
        return requested

    # ========================================================
    # CUSTOMER ORDER
    # ========================================================

    def set_order(
        self,
        order,
    ):

        self.customer_order = order

        self.game_state.set_order(
            order
        )

        self.player_drink.reset()

        self._reset_sliders()

        self.served = False

        self._sync_legacy_values()

    # ========================================================
    # MAIN.PY COMPATIBILITY
    # ========================================================

    def set_customer_order(
        self,
        order,
    ):

        self.set_order(
            order
        )

    # ========================================================
    # LEGACY BRIDGE
    # ========================================================

    def _attach_legacy_bridge(self):

        if self.drink is None:

            return

        try:

            self.drink.get_data = (
                self.get_player_drink_data
            )

        except Exception:

            pass

    # ========================================================
    # SYNC LEGACY DRINK
    # ========================================================

    def _sync_legacy_values(self):

        if self.drink is None:

            return

        temperature_map = {
            "Cold": 25,
            "Normal": 50,
            "Hot": 75,
        }

        caffeine_map = {
            "Low": 25,
            "Normal": 50,
            "High": 75,
        }

        sweetness_map = {
            "Less": 25,
            "Normal": 50,
            "Extra": 75,
        }

        try:

            self.drink.temperature = (
                temperature_map.get(
                    self.player_drink.temperature,
                    50,
                )
            )

            self.drink.caffeine = (
                caffeine_map.get(
                    self.player_drink.caffeine,
                    50,
                )
            )

            self.drink.sweetness = (
                sweetness_map.get(
                    self.player_drink.sweetness,
                    50,
                )
            )

        except Exception:

            pass

    # ========================================================
    # CHANGE SELECTED DRINK
    # ========================================================
    #
    # IMPORTANT FIX:
    #
    # The player can change drinks before blending.
    #
    # Example:
    #
    # Neon Latte
    #     ↓
    # Milkyway
    #     ↓
    # Void Chai
    #
    # Every time the drink changes, the previous
    # customisation is cleared.
    #
    # ========================================================

    def _change_selected_drink(
        self,
        drink_name,
    ):

        # ----------------------------------------------------
        # SET NEW DRINK
        # ----------------------------------------------------

        self.player_drink.drink_name = (
            drink_name
        )

        # ----------------------------------------------------
        # CLEAR PREVIOUS SETTINGS
        # ----------------------------------------------------

        self.player_drink.temperature = None

        self.player_drink.caffeine = None

        self.player_drink.sweetness = None

        # ----------------------------------------------------
        # RESET GAME STATE CUSTOMISATION
        # ----------------------------------------------------

        self.game_state.selected_drink = (
            drink_name
        )

        self.game_state.selected_temperature = (
            None
        )

        self.game_state.selected_caffeine = (
            None
        )

        self.game_state.selected_sweetness = (
            None
        )

        self.game_state.blend_finished = False

        self.game_state.served = False

        # ----------------------------------------------------
        # RETURN TO CUSTOMISE STATE
        # ----------------------------------------------------

        self.game_state.state = (
            GameState.CUSTOMISE
        )

        self._reset_sliders()

        self.served = False

        self._sync_legacy_values()

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt=0.0,
    ):

        # The timing sliders only move while the player is
        # customising a selected drink.
        if self.game_state.can_customize() and self.player_drink.drink_name:
            self.slider_time += max(0.0, float(dt))

        self._update_blending()

    # ========================================================
    # SLIDER MOTION
    # ========================================================

    def _slider_position(self, parameter):
        """Return a 0..1 ping-pong position for a slider."""

        speed = self.slider_speeds[parameter]
        phase = self.slider_phases[parameter]
        cycle = (self.slider_time * speed + phase) % 2.0

        if cycle <= 1.0:
            return cycle

        return 2.0 - cycle

    def _slider_option_from_position(self, parameter):
        """Convert the moving indicator position to one of 3 options."""

        options = {
            "temperature": TEMPERATURE_OPTIONS,
            "caffeine": CAFFEINE_OPTIONS,
            "sweetness": SWEETNESS_OPTIONS,
        }[parameter]

        position = self._slider_position(parameter)
        centers = (0.08, 0.50, 0.92)
        index = min(
            range(3),
            key=lambda i: abs(position - centers[i]),
        )
        return options[index], abs(position - centers[index])

    def _reset_sliders(self):
        self.slider_time = 0.0
        self.slider_results = {
            "temperature": None,
            "caffeine": None,
            "sweetness": None,
        }
        self.slider_feedback = {
            "temperature": "WAITING",
            "caffeine": "WAITING",
            "sweetness": "WAITING",
        }

    def _get_customer_target(self, parameter):
        if self.customer_order is None:
            return None
        return getattr(self.customer_order, parameter, None)

    def _lock_slider(self, parameter):
        """Capture the current moving position as the player's choice."""

        if not self.game_state.can_customize():
            return

        value, distance = self._slider_option_from_position(parameter)

        # The indicator must be close enough to a zone to count.
        # This creates the timing challenge.
        if distance > 0.15:
            self.slider_feedback[parameter] = "MISSED"
            self.slider_results[parameter] = False
            return

        if parameter == "temperature":
            accepted = self.game_state.select_temperature(value)
            if accepted:
                self.player_drink.temperature = value
        elif parameter == "caffeine":
            accepted = self.game_state.select_caffeine(value)
            if accepted:
                self.player_drink.caffeine = value
        else:
            accepted = self.game_state.select_sweetness(value)
            if accepted:
                self.player_drink.sweetness = value

        target = self._get_customer_target(parameter)
        correct = target is not None and value == target
        self.slider_results[parameter] = correct
        self.slider_feedback[parameter] = "CORRECT" if correct else "WRONG"
        self._sync_legacy_values()

    # ========================================================
    # UPDATE BLENDING
    # ========================================================

    def _update_blending(self):

        if (
            self.game_state.state
            != GameState.BLENDING
        ):

            return

        current_time = (
            time.monotonic()
        )

        elapsed = (
            current_time
            - self.blend_start_time
        )

        self.blender_angle = (
            elapsed
            * 720
        ) % 360

        self.blender_pulse = (
            math.sin(
                elapsed * 10
            )
            * 0.5
            + 0.5
        )

        if (
            elapsed
            >= self.blend_duration
        ):

            self.game_state.finish_blending()

            self._sync_legacy_values()

    # ========================================================
    # HANDLE EVENTS
    # ========================================================

    def handle_event(
        self,
        event,
    ):

        if event.type != pygame.MOUSEBUTTONDOWN:

            return

        if event.button != 1:

            return

        mouse = event.pos

        self._update_blending()

        # ====================================================
        # MAP BUTTON
        # ====================================================

        if self.map_button.collidepoint(mouse):
            self.map_requested = True
            return

        # ====================================================
        # LEADERBOARD BUTTON
        # ====================================================

        if self.leaderboard_button.collidepoint(mouse):
            self.leaderboard_requested = True
            return

        # ====================================================
        # DRINK MENU
        # ====================================================

        for (
            drink_name,
            rect,
        ) in self.menu_slots:

            if not rect.collidepoint(
                mouse
            ):

                continue

            # ------------------------------------------------
            # VALID DRINK
            # ------------------------------------------------

            if not is_valid_drink(
                drink_name
            ):

                return

            # ------------------------------------------------
            # CHECK UNLOCK
            # ------------------------------------------------

            if not is_drink_unlocked(
                drink_name,
                self.level,
            ):

                return

            # ------------------------------------------------
            # DRINK IS LOCKED AFTER BLEND
            # ------------------------------------------------

            if self.game_state.state in (
                GameState.BLENDING,
                GameState.READY_TO_SERVE,
                GameState.SERVED,
            ):

                return

            # ------------------------------------------------
            # CHANGE DRINK
            # ------------------------------------------------

            self._change_selected_drink(
                drink_name
            )

            return

        # ====================================================
        # CUSTOMISATION TIMING SLIDERS
        # ====================================================

        if self.game_state.can_customize():

            for parameter, rect in self.slider_tracks.items():
                if rect.collidepoint(mouse):
                    self._lock_slider(parameter)
                    return

        # ====================================================
        # BLEND BUTTON
        # ====================================================

        if self.blend_button.collidepoint(
            mouse
        ):

            if self.game_state.start_blending():

                self.blend_start_time = (
                    time.monotonic()
                )

                self.blender_angle = 0.0

            return

        # ====================================================
        # SERVE BUTTON
        # ====================================================

        if self.serve_button.collidepoint(
            mouse
        ):

            if self.game_state.serve():

                self.served = True

                self._sync_legacy_values()

            return

    # ========================================================
    # PLAYER DRINK DATA
    # ========================================================

    def get_player_drink_data(self):

        return (
            self.game_state
            .get_player_drink_data()
        )

    # ========================================================
    # LEGACY DATA
    # ========================================================

    def get_data(self):

        return self.get_player_drink_data()

    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        screen,
    ):

        self._update_blending()

        self._draw_hud(
            screen
        )

        self._draw_menu(
            screen
        )

        self._draw_customise(
            screen
        )

        self._draw_blender(
            screen
        )

        self._draw_preview(
            screen
        )

    # ========================================================
    # HUD
    # ========================================================

    def _draw_hud(
        self,
        screen,
    ):
        """Draw the compact-but-wide player information HUD."""

        rect = self.hud_rect

        self._panel(
            screen,
            rect,
            self.CYAN,
            self.PANEL,
            radius=12,
            width=2,
        )

        # ----------------------------------------------------
        # READ CURRENT PLAYER DATA
        # ----------------------------------------------------

        level = self.level
        xp = 0
        credits = 0
        player_name = "PLAYER"
        location = "UNKNOWN"
        combo = 0

        if self.progression is not None:
            level = getattr(
                self.progression,
                "level",
                level,
            )
            xp = getattr(
                self.progression,
                "xp",
                xp,
            )

        if self.economy is not None:
            player_name = getattr(
                self.economy,
                "player_name",
                player_name,
            )

            credits = getattr(
                self.economy,
                "credits",
                credits,
            )

            if hasattr(self.economy, "get_credits"):
                try:
                    credits = self.economy.get_credits()
                except Exception:
                    pass

            location = getattr(
                self.economy,
                "location",
                location,
            )

        if self.rewards is not None:
            combo = getattr(
                self.rewards,
                "combo",
                combo,
            )

        if not player_name:
            player_name = "PLAYER"

        if not location:
            location = "UNKNOWN"

        # ----------------------------------------------------
        # NEXT-LEVEL XP REQUIREMENT
        # ----------------------------------------------------

        max_xp = 100

        if self.progression is not None:

            xp_requirements = getattr(
                self.progression,
                "xp_requirements",
                None,
            )

            if isinstance(
                xp_requirements,
                dict,
            ):
                max_xp = xp_requirements.get(
                    level,
                    100,
                )

            else:
                possible = getattr(
                    self.progression,
                    "xp_required",
                    None,
                )

                if callable(possible):
                    try:
                        possible = possible()
                    except Exception:
                        possible = 100

                if possible is not None:
                    max_xp = possible

        try:
            max_xp = max(
                1,
                int(max_xp),
            )
        except (TypeError, ValueError):
            max_xp = 100

        try:
            xp = int(xp)
        except (TypeError, ValueError):
            xp = 0

        try:
            credits = int(credits)
        except (TypeError, ValueError):
            credits = 0

        # ----------------------------------------------------
        # PLAYER NAME
        # ----------------------------------------------------

        name_text = self.font_hud.render(
            str(player_name)[:14].upper(),
            True,
            self.WHITE,
        )

        screen.blit(
            name_text,
            (35, 20),
        )

        # ----------------------------------------------------
        # LEVEL
        # ----------------------------------------------------

        level_text = self.font_small.render(
            f"LEVEL {level}",
            True,
            self.CYAN_LIGHT,
        )

        screen.blit(
            level_text,
            (35, 40),
        )

        # ----------------------------------------------------
        # XP LABEL
        # ----------------------------------------------------

        xp_label = self.font_small.render(
            "XP",
            True,
            self.PINK_LIGHT,
        )

        screen.blit(
            xp_label,
            (150, 22),
        )

        # ----------------------------------------------------
        # XP BAR
        # ----------------------------------------------------

        xp_bar = pygame.Rect(
            174,
            20,
            225,
            18,
        )

        pygame.draw.rect(
            screen,
            (18, 25, 48),
            xp_bar,
            border_radius=9,
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            xp_bar,
            width=1,
            border_radius=9,
        )

        ratio = max(
            0.0,
            min(
                1.0,
                xp / max_xp,
            ),
        )

        fill_width = int(
            (xp_bar.width - 6)
            * ratio
        )

        if fill_width > 0:
            pygame.draw.rect(
                screen,
                self.CYAN,
                pygame.Rect(
                    xp_bar.x + 3,
                    xp_bar.y + 3,
                    fill_width,
                    xp_bar.height - 6,
                ),
                border_radius=6,
            )

        xp_number = self.font_small.render(
            f"{xp}/{max_xp}",
            True,
            self.WHITE,
        )

        screen.blit(
            xp_number,
            xp_number.get_rect(
                center=xp_bar.center,
            ),
        )

        # ----------------------------------------------------
        # CREDITS
        # ----------------------------------------------------

        credit_text = self.font_hud.render(
            f"CREDITS ${credits}",
            True,
            self.YELLOW,
        )

        screen.blit(
            credit_text,
            (420, 20),
        )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        location_text = self.font_small.render(
            f"LOCATION: {str(location).upper()}",
            True,
            self.SOFT_WHITE,
        )

        screen.blit(
            location_text,
            (420, 40),
        )

        combo_text = self.font_small.render(
            f"COMBO x{combo}",
            True,
            self.PINK_LIGHT,
        )

        screen.blit(
            combo_text,
            (650, 40),
        )

        # ----------------------------------------------------
        # REWARD FEEDBACK
        # ----------------------------------------------------

        if time.monotonic() < self.reward_feedback_until:

            feedback_parts = []

            if self.last_xp_change > 0:
                feedback_parts.append(
                    f"+{self.last_xp_change} XP"
                )
            elif self.last_xp_change < 0:
                feedback_parts.append(
                    f"{self.last_xp_change} XP"
                )

            if self.last_credit_change > 0:
                feedback_parts.append(
                    f"+${self.last_credit_change}"
                )
            elif self.last_credit_change < 0:
                feedback_parts.append(
                    f"-${abs(self.last_credit_change)}"
                )

            if feedback_parts:

                feedback = self.font_small.render(
                    "  ".join(feedback_parts),
                    True,
                    self.GREEN
                    if (
                        self.last_xp_change >= 0
                        and self.last_credit_change >= 0
                    )
                    else self.PINK_LIGHT,
                )

                screen.blit(
                    feedback,
                    (600, 20),
                )

        # ----------------------------------------------------
        # TOP-RIGHT NAVIGATION
        # ----------------------------------------------------

        self._action_button(
            screen,
            self.map_button,
            "MAP  [M]",
            self.CYAN,
            True,
            large=False,
        )

        self._action_button(
            screen,
            self.leaderboard_button,
            "LEADERBOARD  [L]",
            self.PINK,
            True,
            large=False,
        )

    # ========================================================
    # DRINK MENU
    # ========================================================

    def _draw_menu(
        self,
        screen,
    ):

        self._panel(
            screen,
            self.menu_rect,
            self.CYAN,
            self.PANEL,
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = self.font_title.render(
            "CYBERPUNK DRINK MENU",
            True,
            self.CYAN_LIGHT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.menu_rect.centerx,
                    89,
                )
            ),
        )

        # ----------------------------------------------------
        # DRINK CARDS
        # ----------------------------------------------------

        for (
            drink_name,
            rect,
        ) in self.menu_slots:

            unlocked = is_drink_unlocked(
                drink_name,
                self.level,
            )

            selected = (
                self.player_drink.drink_name
                == drink_name
            )

            if selected:

                border = self.PINK_LIGHT

                fill = self.BUTTON_SELECTED

            elif unlocked:

                border = self.CYAN

                fill = self.BUTTON

            else:

                border = self.LOCKED

                fill = (
                    6,
                    9,
                    22,
                    135,
                )

            self._panel(
                screen,
                rect,
                border,
                fill,
                radius=12,
                width=1,
            )

            image = self.drink_images.get(
                drink_name
            )

            image_area = pygame.Rect(
                rect.x + 6,
                rect.y + 7,
                rect.width - 12,
                112,
            )

            if image is not None:

                self._image_fit(
                    screen,
                    image,
                    image_area,
                    unlocked,
                )

            if not unlocked:

                self._draw_lock(
                    screen,
                    rect.centerx,
                    rect.y + 64,
                )

            self._draw_drink_name(
                screen,
                drink_name,
                rect,
                unlocked,
            )

    # ========================================================
    # DRINK NAME
    # ========================================================

    def _draw_drink_name(
        self,
        screen,
        drink_name,
        rect,
        unlocked,
    ):

        colour = (
            self.WHITE
            if unlocked
            else self.LOCKED
        )

        # ----------------------------------------------------
        # TWO-LINE NAMES
        # ----------------------------------------------------

        if drink_name == "Hologram Frappe":

            lines = [
                "HOLOGRAM",
                "FRAPPE",
            ]

        elif drink_name == "Stardust Matcha":

            lines = [
                "STARDUST",
                "MATCHA",
            ]

        elif drink_name == "Cyber Fuel":

            lines = [
                "CYBER",
                "FUEL",
            ]

        elif drink_name == "Pixel Lemint":

            lines = [
                "PIXEL",
                "LEMINT",
            ]

        elif drink_name == "Caramel Byte":

            lines = [
                "CARAMEL",
                "BYTE",
            ]

        else:

            lines = [
                drink_name.upper()
            ]

        # ----------------------------------------------------
        # SINGLE LINE
        # ----------------------------------------------------

        if len(lines) == 1:

            text = self.font_menu.render(
                lines[0],
                True,
                colour,
            )

            screen.blit(
                text,
                text.get_rect(
                    center=(
                        rect.centerx,
                        rect.bottom - 14,
                    )
                ),
            )

        # ----------------------------------------------------
        # TWO LINES
        # ----------------------------------------------------

        else:

            first = self.font_menu.render(
                lines[0],
                True,
                colour,
            )

            second = self.font_menu.render(
                lines[1],
                True,
                colour,
            )

            screen.blit(
                first,
                first.get_rect(
                    center=(
                        rect.centerx,
                        rect.bottom - 24,
                    )
                ),
            )

            screen.blit(
                second,
                second.get_rect(
                    center=(
                        rect.centerx,
                        rect.bottom - 11,
                    )
                ),
            )

    # ========================================================
    # CUSTOMISE PANEL
    # ========================================================

    def _draw_customise(
        self,
        screen,
    ):

        self._panel(
            screen,
            self.customise_rect,
            self.CYAN,
            (6, 12, 29, 190),
            radius=14,
            width=2,
        )

        title = self.font_big_title.render(
            "CUSTOMISE YOUR DRINK",
            True,
            self.CYAN_LIGHT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(self.customise_rect.centerx, 420)
            ),
        )

        instruction = self.font_small.render(
            "CLICK WHEN THE INDICATOR HITS THE CORRECT ZONE!",
            True,
            self.SOFT_WHITE,
        )

        screen.blit(
            instruction,
            instruction.get_rect(
                center=(self.customise_rect.centerx, 444)
            ),
        )

        self._draw_timing_slider(
            screen, "temperature", "TEMPERATURE", TEMPERATURE_OPTIONS, self.CYAN, 465
        )
        self._draw_timing_slider(
            screen, "caffeine", "CAFFEINE LEVEL", CAFFEINE_OPTIONS, self.YELLOW, 540
        )
        self._draw_timing_slider(
            screen, "sweetness", "SWEETNESS LEVEL", SWEETNESS_OPTIONS, self.PINK_LIGHT, 615
        )

    def _draw_timing_slider(
        self,
        screen,
        parameter,
        label,
        options,
        accent,
        track_y,
    ):

        track = self.slider_tracks[parameter]

        label_surface = self.font_category.render(
            label,
            True,
            accent,
        )

        screen.blit(
            label_surface,
            (track.x, track.y - 26),
        )

        # Track glow.
        glow = pygame.Rect(
            track.x - 2,
            track.y - 2,
            track.width + 4,
            track.height + 4,
        )
        glow_surface = pygame.Surface(
            glow.size,
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            glow_surface,
            (*accent, 70),
            glow_surface.get_rect(),
            border_radius=8,
        )
        screen.blit(
            glow_surface,
            glow.topleft,
        )

        pygame.draw.rect(
            screen,
            (15, 24, 48),
            track,
            border_radius=6,
        )
        pygame.draw.rect(
            screen,
            accent,
            track,
            width=2,
            border_radius=6,
        )

        # Three target zones. Their positions are deliberately
        # obvious, but the correct zone is not highlighted.
        centers = (0.08, 0.50, 0.92)

        for index, option in enumerate(options):
            cx = int(track.x + track.width * centers[index])

            pygame.draw.line(
                screen,
                (105, 120, 150),
                (cx, track.y - 5),
                (cx, track.bottom + 5),
                1,
            )

            text = self.font_small.render(
                option.upper(),
                True,
                self.WHITE,
            )

            screen.blit(
                text,
                text.get_rect(
                    center=(cx, track.bottom + 18)
                ),
            )

        # Moving indicator.
        position = self._slider_position(parameter)
        indicator_x = int(
            track.x + track.width * position
        )

        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (indicator_x, track.centery),
            9,
        )

        pygame.draw.circle(
            screen,
            accent,
            (indicator_x, track.centery),
            7,
        )

        pygame.draw.circle(
            screen,
            self.WHITE,
            (indicator_x, track.centery),
            2,
        )

        # Result feedback appears only after the player clicks.
        result = self.slider_results[parameter]
        if result is True:
            feedback = "✓ CORRECT"
            colour = self.GREEN
        elif result is False:
            feedback = self.slider_feedback[parameter]
            colour = self.PINK_LIGHT
        else:
            feedback = "CLICK"
            colour = self.MUTED

        feedback_text = self.font_small.render(
            feedback,
            True,
            colour,
        )

        screen.blit(
            feedback_text,
            (track.right - feedback_text.get_width(), track.y - 26),
        )

    # ========================================================
    # BLENDER
    # ========================================================

    def _draw_blender(
        self,
        screen,
    ):

        # ----------------------------------------------------
        # TRANSLUCENT PANEL
        # ----------------------------------------------------

        self._panel(
            screen,
            self.blender_rect,
            self.PURPLE,
            (
                6,
                10,
                27,
                145,
            ),
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = self.font_big_title.render(
            "BLENDER",
            True,
            self.CYAN_LIGHT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.blender_rect.centerx,
                    self.blender_rect.y + 20,
                )
            ),
        )

        jug = self.blender_jug_rect.copy()

        is_blending = (
            self.game_state.state
            == GameState.BLENDING
        )

        # ====================================================
        # JUG MOVEMENT
        # ====================================================

        if is_blending:

            jug.x += int(
                math.sin(
                    time.monotonic()
                    * 30
                )
                * 2
            )

            jug.y += int(
                math.cos(
                    time.monotonic()
                    * 25
                )
            )

        # ====================================================
        # BLENDER GLOW
        # ====================================================

        if is_blending:

            glow_surface = pygame.Surface(
                (
                    jug.width + 28,
                    jug.height + 28,
                ),
                pygame.SRCALPHA,
            )

            alpha = int(
                30
                + self.blender_pulse
                * 40
            )

            pygame.draw.rect(
                glow_surface,
                (
                    75,
                    225,
                    255,
                    alpha,
                ),
                glow_surface.get_rect(),
                border_radius=25,
                width=5,
            )

            screen.blit(
                glow_surface,
                (
                    jug.x - 14,
                    jug.y - 14,
                ),
            )

        # ====================================================
        # JUG BODY
        # ====================================================

        pygame.draw.rect(
            screen,
            (
                17,
                25,
                52,
            ),
            jug,
            border_radius=23,
        )

        pygame.draw.rect(
            screen,
            self.CYAN_LIGHT,
            jug,
            width=2,
            border_radius=23,
        )

        # Sleek lid and neon rim.
        lid = pygame.Rect(
            jug.x + 24,
            jug.y - 8,
            jug.width - 48,
            18,
        )
        pygame.draw.rect(
            screen,
            (20, 24, 48),
            lid,
            border_radius=8,
        )
        pygame.draw.rect(
            screen,
            self.PINK_LIGHT,
            lid,
            width=2,
            border_radius=8,
        )

        # ====================================================
        # INNER GLASS
        # ====================================================

        inner = pygame.Rect(
            jug.x + 11,
            jug.y + 13,
            jug.width - 22,
            jug.height - 28,
        )

        pygame.draw.rect(
            screen,
            (
                7,
                12,
                28,
            ),
            inner,
            border_radius=17,
        )

        # ====================================================
        # HANDLE
        # ====================================================

        handle = pygame.Rect(
            jug.right - 2,
            jug.y + 28,
            22,
            52,
        )

        pygame.draw.rect(
            screen,
            (
                18,
                25,
                52,
            ),
            handle,
            border_radius=13,
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            handle,
            width=2,
            border_radius=13,
        )

        # ====================================================
        # LIQUID
        # ====================================================

        drink_name = (
            self.player_drink.drink_name
        )

        if drink_name:

            recipe = get_recipe(
                drink_name
            )

            if recipe:

                liquid_colour = (
                    recipe.liquid_color
                )

            else:

                liquid_colour = (
                    150,
                    150,
                    255,
                )

            # ------------------------------------------------
            # HOLOGRAM FRAPPE
            # ------------------------------------------------

            if (
                drink_name
                == "Hologram Frappe"
                and is_blending
            ):

                cycle = (
                    time.monotonic()
                    * 3
                )

                liquid_colour = (
                    int(
                        180
                        + 55
                        * (
                            math.sin(
                                cycle
                            )
                            + 1
                        )
                        / 2
                    ),
                    int(
                        150
                        + 80
                        * (
                            math.sin(
                                cycle + 2
                            )
                            + 1
                        )
                        / 2
                    ),
                    int(
                        200
                        + 55
                        * (
                            math.sin(
                                cycle + 4
                            )
                            + 1
                        )
                        / 2
                    ),
                )

            liquid_height = (
                inner.height - 22
            )

            if is_blending:

                liquid_height += int(
                    math.sin(
                        time.monotonic()
                        * 12
                    )
                    * 4
                )

            liquid = pygame.Rect(
                inner.x + 4,
                inner.bottom
                - liquid_height
                - 4,
                inner.width - 8,
                liquid_height,
            )

            pygame.draw.rect(
                screen,
                liquid_colour,
                liquid,
                border_radius=14,
            )

            # ------------------------------------------------
            # LIQUID HIGHLIGHT
            # ------------------------------------------------

            highlight_colour = (
                min(
                    255,
                    liquid_colour[0]
                    + 45,
                ),
                min(
                    255,
                    liquid_colour[1]
                    + 45,
                ),
                min(
                    255,
                    liquid_colour[2]
                    + 45,
                ),
            )

            highlight = pygame.Rect(
                liquid.x + 7,
                liquid.y + 6,
                liquid.width - 14,
                6,
            )

            pygame.draw.rect(
                screen,
                highlight_colour,
                highlight,
                border_radius=4,
            )

            shimmer_y = int(
                liquid.y
                + liquid.height * (0.35 + 0.12 * math.sin(time.monotonic() * 2.5))
            )
            pygame.draw.line(
                screen,
                (255, 255, 255, 110),
                (liquid.x + 12, shimmer_y),
                (liquid.right - 12, shimmer_y),
                1,
            )

            # ------------------------------------------------
            # WAVES
            # ------------------------------------------------

            if is_blending:

                wave_y = (
                    liquid.y + 25
                )

                wave_width = (
                    liquid.width - 22
                )

                wave_left = (
                    liquid.x + 11
                )

                points = []

                for index in range(9):

                    px = (
                        wave_left
                        + index
                        * (
                            wave_width
                            / 8
                        )
                    )

                    py = (
                        wave_y
                        + math.sin(
                            time.monotonic()
                            * 8
                            + index
                        )
                        * 5
                    )

                    points.append(
                        (
                            int(px),
                            int(py),
                        )
                    )

                pygame.draw.lines(
                    screen,
                    self.WHITE,
                    False,
                    points,
                    2,
                )

            # ------------------------------------------------
            # BUBBLES
            # ------------------------------------------------

            if is_blending:

                current_time = (
                    time.monotonic()
                )

                for index in range(6):

                    phase = (
                        current_time
                        * (
                            1.5
                            + index
                            * 0.18
                        )
                        + index
                    )

                    bubble_x = (
                        liquid.x
                        + 20
                        + (
                            index
                            * 19
                        )
                        % max(
                            20,
                            liquid.width
                            - 30,
                        )
                    )

                    bubble_y = (
                        liquid.bottom
                        - 15
                        - (
                            phase
                            * 32
                        )
                        % max(
                            20,
                            liquid.height
                            - 20,
                        )
                    )

                    pygame.draw.circle(
                        screen,
                        (
                            240,
                            250,
                            255,
                        ),
                        (
                            int(
                                bubble_x
                            ),
                            int(
                                bubble_y
                            ),
                        ),
                        3,
                    )

        else:

            text = self.font_small.render(
                "SELECT A DRINK",
                True,
                self.MUTED,
            )

            screen.blit(
                text,
                text.get_rect(
                    center=inner.center
                ),
            )

        # ====================================================
        # BLENDER CORE
        # ====================================================

        core_x = jug.centerx
        core_y = jug.bottom - 20

        pygame.draw.circle(
            screen,
            (
                12,
                17,
                35,
            ),
            (
                core_x,
                core_y,
            ),
            11,
        )

        pygame.draw.circle(
            screen,
            self.PINK,
            (
                core_x,
                core_y,
            ),
            3,
        )

        # ====================================================
        # ROTATING BLADES
        # ====================================================

        if is_blending:

            angle = math.radians(
                self.blender_angle
            )

            for offset in (
                0,
                math.pi / 2,
                math.pi,
                3 * math.pi / 2,
            ):

                blade_angle = (
                    angle + offset
                )

                end_x = (
                    core_x
                    + math.cos(
                        blade_angle
                    )
                    * 25
                )

                end_y = (
                    core_y
                    + math.sin(
                        blade_angle
                    )
                    * 25
                )

                pygame.draw.line(
                    screen,
                    self.CYAN_LIGHT,
                    (
                        core_x,
                        core_y,
                    ),
                    (
                        int(end_x),
                        int(end_y),
                    ),
                    3,
                )

        # ====================================================
        # BLENDER BASE
        # ====================================================

        base = pygame.Rect(
            jug.x - 10,
            jug.bottom - 2,
            jug.width + 20,
            22,
        )

        pygame.draw.rect(
            screen,
            (
                22,
                18,
                40,
            ),
            base,
            border_radius=10,
        )

        pygame.draw.rect(
            screen,
            self.PINK,
            base,
            width=1,
            border_radius=10,
        )

        # ====================================================
        # BLEND PROGRESS
        # ====================================================

        if is_blending:

            elapsed = (
                time.monotonic()
                - self.blend_start_time
            )

            ratio = max(
                0,
                min(
                    1,
                    elapsed
                    / self.blend_duration,
                ),
            )

            progress_rect = pygame.Rect(
                self.blend_button.x + 8,
                self.blend_button.y - 8,
                self.blend_button.width - 16,
                4,
            )

            pygame.draw.rect(
                screen,
                (
                    20,
                    25,
                    45,
                ),
                progress_rect,
                border_radius=2,
            )

            pygame.draw.rect(
                screen,
                self.CYAN,
                pygame.Rect(
                    progress_rect.x,
                    progress_rect.y,
                    int(
                        progress_rect.width
                        * ratio
                    ),
                    progress_rect.height,
                ),
                border_radius=2,
            )

        # ====================================================
        # BLEND BUTTON
        # ====================================================

        self._action_button(
            screen,
            self.blend_button,
            (
                "BLENDING..."
                if is_blending
                else "BLEND"
            ),
            self.PINK,
            self.game_state.can_blend(),
            large=True,
        )

    # ========================================================
    # PREVIEW
    # ========================================================

    def _draw_preview(
        self,
        screen,
    ):

        # ----------------------------------------------------
        # PANEL
        # ----------------------------------------------------

        self._panel(
            screen,
            self.preview_rect,
            self.PINK,
            (
                7,
                10,
                26,
                140,
            ),
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = self.font_title.render(
            "PREVIEW",
            True,
            self.PINK_LIGHT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.preview_rect.centerx,
                    431,
                )
            ),
        )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image = self.drink_images.get(
            self.player_drink.drink_name
        )

        if image is not None:

            self._image_fit(
                screen,
                image,
                self.preview_image_rect,
                True,
            )

        else:

            text = self.font_small.render(
                "NO DRINK",
                True,
                self.MUTED,
            )

            screen.blit(
                text,
                text.get_rect(
                    center=self.preview_image_rect.center,
                ),
            )

        # ----------------------------------------------------
        # READY
        # ----------------------------------------------------

        ready = (
            self.game_state.state
            == GameState.READY_TO_SERVE
        )

        if ready:

            ready_text = self.font_small.render(
                "READY!",
                True,
                self.GREEN,
            )

            screen.blit(
                ready_text,
                ready_text.get_rect(
                    center=(
                        self.preview_rect.centerx,
                        602,
                    ),
                ),
            )

        # ----------------------------------------------------
        # SERVE
        # ----------------------------------------------------

        self._action_button(
            screen,
            self.serve_button,
            "SERVE",
            self.CYAN,
            self.game_state.can_serve(),
            large=False,
        )

    # ========================================================
    # CLEAN PANEL
    # ========================================================

    def _panel(
        self,
        screen,
        rect,
        border,
        fill,
        radius=14,
        width=2,
    ):

        # ----------------------------------------------------
        # TRANSLUCENT BACKGROUND
        # ----------------------------------------------------

        surface = pygame.Surface(
            rect.size,
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            surface,
            fill,
            surface.get_rect(),
            border_radius=radius,
        )

        screen.blit(
            surface,
            rect.topleft,
        )

        # ----------------------------------------------------
        # SINGLE BORDER
        # ----------------------------------------------------

        pygame.draw.rect(
            screen,
            border,
            rect,
            width=width,
            border_radius=radius,
        )

    # ========================================================
    # ACTION BUTTON
    # ========================================================

    def _action_button(
        self,
        screen,
        rect,
        text,
        accent,
        enabled,
        large=False,
    ):

        mouse = pygame.mouse.get_pos()

        hover = (
            enabled
            and rect.collidepoint(
                mouse
            )
        )

        if enabled:

            border = (
                self.PINK_LIGHT
                if hover
                else accent
            )

            fill = (
                45,
                12,
                52,
                205,
            )

            text_colour = self.WHITE

        else:

            border = (
                60,
                65,
                85,
            )

            fill = (
                7,
                10,
                22,
                160,
            )

            text_colour = self.MUTED

        # ----------------------------------------------------
        # HOVER
        # ----------------------------------------------------

        if hover:

            glow = pygame.Rect(
                rect.x - 2,
                rect.y - 2,
                rect.width + 4,
                rect.height + 4,
            )

            pygame.draw.rect(
                screen,
                (
                    255,
                    100,
                    210,
                ),
                glow,
                width=1,
                border_radius=13,
            )

        self._panel(
            screen,
            rect,
            border,
            fill,
            radius=12,
            width=1,
        )

        # ----------------------------------------------------
        # FONT
        # ----------------------------------------------------

        if large:

            font = self.font_big_title

        else:

            font = self.font_button

        label = font.render(
            text,
            True,
            text_colour,
        )

        screen.blit(
            label,
            label.get_rect(
                center=rect.center
            ),
        )

    # ========================================================
    # IMAGE FIT
    # ========================================================

    def _image_fit(
        self,
        screen,
        image,
        target,
        bright=True,
    ):

        if image is None:

            return

        width, height = (
            image.get_size()
        )

        if width <= 0 or height <= 0:

            return

        scale = min(
            target.width / width,
            target.height / height,
        )

        size = (
            max(
                1,
                int(
                    width * scale
                ),
            ),
            max(
                1,
                int(
                    height * scale
                ),
            ),
        )

        scaled = pygame.transform.smoothscale(
            image,
            size,
        )

        if not bright:

            scaled = scaled.copy()

            scaled.fill(
                (
                    70,
                    70,
                    90,
                    255,
                ),
                special_flags=(
                    pygame.BLEND_RGBA_MULT
                ),
            )

        destination = scaled.get_rect(
            center=target.center
        )

        screen.blit(
            scaled,
            destination,
        )

    # ========================================================
    # LOCK ICON
    # ========================================================

    def _draw_lock(
        self,
        screen,
        x,
        y,
    ):

        body = pygame.Rect(
            x - 9,
            y,
            18,
            15,
        )

        pygame.draw.rect(
            screen,
            self.LOCKED,
            body,
            border_radius=4,
        )

        pygame.draw.arc(
            screen,
            self.LOCKED,
            pygame.Rect(
                x - 6,
                y - 11,
                12,
                16,
            ),
            math.pi,
            2 * math.pi,
            2,
        )

        pygame.draw.circle(
            screen,
            (
                25,
                28,
                45,
            ),
            (
                x,
                y + 7,
            ),
            2,
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.player_drink.reset()

        self.game_state.reset()

        self.customer_order = None

        self.served = False

        self.map_requested = False
        self.leaderboard_requested = False

        self.last_xp_change = 0
        self.last_credit_change = 0
        self.reward_feedback_until = 0.0

        self._reset_sliders()

        self.blend_start_time = 0.0

        self.blender_angle = 0.0

        self.blender_pulse = 0.0

        self._sync_legacy_values()


# ============================================================
# END OF STATION.PY
# ============================================================
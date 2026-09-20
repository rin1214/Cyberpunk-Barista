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

from game_state import MixingGameState, GameState


class MixingStation:

    # ============================================================
    # MASTER SCREEN
    # ============================================================

    WIDTH = 1280
    HEIGHT = 720

    # ============================================================
    # UNIFIED PANEL STYLE
    # ============================================================

    PANEL = (8, 13, 31, 238)

    PANEL_INNER = (11, 18, 39, 245)

    BUTTON_DARK = (8, 12, 28)

    # ============================================================
    # ACCENT COLOURS
    # ============================================================

    CYAN = (70, 225, 255)
    CYAN_BRIGHT = (145, 245, 255)

    PINK = (255, 65, 190)
    PINK_BRIGHT = (255, 150, 225)

    PURPLE = (170, 90, 255)

    BLUE = (75, 165, 255)

    MINT = (100, 255, 210)

    YELLOW = (255, 210, 80)

    WHITE = (245, 248, 255)

    MUTED = (145, 155, 185)

    LOCKED = (70, 75, 100)

    GREEN = (75, 235, 160)

    RED = (255, 80, 100)

    # ============================================================
    # INITIALISATION
    # ============================================================

    def __init__(
        self,
        drink=None,
        level=1,
        progression=None,
        rewards=None,
        economy=None,
    ):

        # --------------------------------------------------------
        # LEGACY DRINK
        # --------------------------------------------------------

        self.drink = drink

        # --------------------------------------------------------
        # NEW PLAYER DRINK
        # --------------------------------------------------------

        self.player_drink = PlayerDrink()

        # --------------------------------------------------------
        # STATE MACHINE
        # --------------------------------------------------------

        self.game_state = MixingGameState()

        # --------------------------------------------------------
        # SYSTEM REFERENCES
        # --------------------------------------------------------

        self.progression = progression

        self.rewards = rewards

        self.economy = economy

        self.level = max(
            1,
            int(level),
        )

        # --------------------------------------------------------
        # CUSTOMER ORDER
        # --------------------------------------------------------

        self.customer_order = None

        # --------------------------------------------------------
        # SERVED FLAG
        # --------------------------------------------------------

        self.served = False

        # ========================================================
        # BLENDER ANIMATION
        # ========================================================

        self.blend_start_time = 0.0

        # Total active blending time.
        self.blend_duration = 1.8

        # Time used for the final settling effect.
        self.settle_duration = 0.25

        # --------------------------------------------------------
        # Blender animation variables
        # --------------------------------------------------------

        self.blender_angle = 0.0

        self.blender_rotation_speed = 720.0

        self.blender_shake = 0.0

        self.blender_bubble_offset = 0.0

        # ========================================================
        # FONTS
        # ========================================================

        self.font_small = pygame.font.SysFont(
            "arial",
            13,
            bold=True,
        )

        self.font_medium = pygame.font.SysFont(
            "arial",
            16,
            bold=True,
        )

        self.font_large = pygame.font.SysFont(
            "arial",
            23,
            bold=True,
        )

        self.font_xlarge = pygame.font.SysFont(
            "arial",
            29,
            bold=True,
        )

        # ========================================================
        # ASSET DIRECTORY
        # ========================================================

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.drink_dir = os.path.join(
            self.base_dir,
            "assets",
            "mahirah",
            "drinks",
        )

        # ========================================================
        # DRINK IMAGES
        # ========================================================

        self.drink_images = {}

        self._load_drink_images()

        # ========================================================
        # TOP HUD
        # ========================================================

        self.hud_rect = pygame.Rect(
            20,
            14,
            525,
            48,
        )

        # ========================================================
        # TOP-RIGHT DRINK MENU
        # ========================================================
        #
        # This is deliberately smaller than the previous version.
        #
        # The mixing station itself is NOT being reduced.
        #

        self.menu_rect = pygame.Rect(
            435,
            83,
            825,
            188,
        )

        # ========================================================
        # LARGE MIXING STATION
        # ========================================================
        #
        # Moved right and slightly lower.
        #
        # The station remains large.
        #

        self.customise_rect = pygame.Rect(
            455,
            410,
            305,
            295,
        )

        self.blender_rect = pygame.Rect(
            775,
            410,
            315,
            295,
        )

        self.preview_rect = pygame.Rect(
            1105,
            410,
            155,
            295,
        )

        # ========================================================
        # BLENDER
        # ========================================================

        self.blender_jug_rect = pygame.Rect(
            845,
            445,
            180,
            145,
        )

        self.blend_button = pygame.Rect(
            835,
            610,
            205,
            70,
        )

        # ========================================================
        # PREVIEW
        # ========================================================

        self.preview_image_rect = pygame.Rect(
            1120,
            455,
            125,
            125,
        )

        # --------------------------------------------------------
        # NO PLACE BUTTON
        # --------------------------------------------------------
        #
        # Only Serve remains.
        #

        self.serve_button = pygame.Rect(
            1120,
            615,
            125,
            60,
        )

        # ========================================================
        # TOPPINGS
        # ========================================================

        self.toppings_rect = pygame.Rect(
            775,
            680,
            315,
            25,
        )

        # ========================================================
        # MENU SLOTS
        # ========================================================

        self.menu_slots = []

        self._create_menu_slots()

        # ========================================================
        # CUSTOMISATION BUTTONS
        # ========================================================

        self.temperature_buttons = {}

        self.caffeine_buttons = {}

        self.sweetness_buttons = {}

        self._create_option_buttons()

        # ========================================================
        # LEGACY BRIDGE
        # ========================================================

        self._attach_legacy_bridge()

    # ============================================================
    # DRINK IMAGE LOADING
    # ============================================================

    def _load_drink_images(self):

        filenames = {
            "Neon Latte": "neon_latte.png",
            "Milkyway": "milkyway.png",
            "Void Chai": "void_chai.png",
            "Cyber Fuel": "cyber_fuel.png",
            "Hologram Frappe": "hologram_frappe.png",
            "Pixel Lemint": "pixel_lemint.png",
            "Caramel Byte": "caramel_byte.png",
            "Stardust Matcha": "stardust_matcha.png",
            "Meteorite": "meteorite.png",
        }

        for drink_name, filename in filenames.items():

            path = os.path.join(
                self.drink_dir,
                filename,
            )

            try:

                image = pygame.image.load(
                    path
                ).convert_alpha()

                self.drink_images[drink_name] = image

            except (
                pygame.error,
                FileNotFoundError,
            ):

                print(
                    f"[STATION] Could not load drink image: {path}"
                )

                self.drink_images[drink_name] = None

    # ============================================================
    # MENU
    # ============================================================

    def _create_menu_slots(self):

        self.menu_slots.clear()

        # --------------------------------------------------------
        # SMALLER 9-DRINK MENU
        # --------------------------------------------------------

        left = 448

        top = 91

        width = 88

        height = 166

        gap = 4

        for index, drink_name in enumerate(
            DRINK_MENU
        ):

            x = (
                left
                + index * (
                    width + gap
                )
            )

            rect = pygame.Rect(
                x,
                top,
                width,
                height,
            )

            self.menu_slots.append(
                (
                    drink_name,
                    rect,
                )
            )

    # ============================================================
    # OPTION BUTTONS
    # ============================================================

    def _create_option_buttons(self):

        # --------------------------------------------------------
        # CUSTOMISE PANEL
        # --------------------------------------------------------

        x_positions = (
            475,
            575,
            675,
        )

        # --------------------------------------------------------
        # TEMPERATURE
        # --------------------------------------------------------

        for x, value in zip(
            x_positions,
            TEMPERATURE_OPTIONS,
        ):

            self.temperature_buttons[value] = pygame.Rect(
                x,
                470,
                82,
                52,
            )

        # --------------------------------------------------------
        # CAFFEINE
        # --------------------------------------------------------

        for x, value in zip(
            x_positions,
            CAFFEINE_OPTIONS,
        ):

            self.caffeine_buttons[value] = pygame.Rect(
                x,
                538,
                82,
                52,
            )

        # --------------------------------------------------------
        # SWEETNESS
        # --------------------------------------------------------

        for x, value in zip(
            x_positions,
            SWEETNESS_OPTIONS,
        ):

            self.sweetness_buttons[value] = pygame.Rect(
                x,
                606,
                82,
                52,
            )

    # ============================================================
    # CUSTOMER ORDER
    # ============================================================

    def set_customer_order(
        self,
        order,
    ):

        self.customer_order = order

        self.player_drink.reset()

        self.game_state.set_order(
            order
        )

        self.served = False

        self._reset_blender_animation()

    def update_customer_order(
        self,
        order,
    ):

        self.set_customer_order(
            order
        )

    # ============================================================
    # LEVEL
    # ============================================================

    def set_level(
        self,
        level,
    ):

        try:

            level = int(level)

        except (
            TypeError,
            ValueError,
        ):

            level = 1

        self.level = max(
            1,
            level,
        )

    # ============================================================
    # PROGRESSION
    # ============================================================

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

    # ============================================================
    # REWARDS
    # ============================================================

    def set_rewards(
        self,
        rewards,
    ):

        self.rewards = rewards

    # ============================================================
    # ECONOMY
    # ============================================================

    def set_economy(
        self,
        economy,
    ):

        self.economy = economy

    # ============================================================
    # PLAYER DRINK DATA
    # ============================================================

    def get_player_drink_data(self):

        return (
            self.game_state
            .get_player_drink_data()
        )

    def get_data(self):

        return self.get_player_drink_data()

    # ============================================================
    # LEGACY BRIDGE
    # ============================================================

    def _attach_legacy_bridge(self):

        if self.drink is None:

            return

        try:

            self.drink.get_data = (
                self.get_data
            )

        except Exception:

            pass

    # ============================================================
    # LEGACY NUMERIC VALUES
    # ============================================================

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

    # ============================================================
    # BLENDER RESET
    # ============================================================

    def _reset_blender_animation(self):

        self.blend_start_time = 0.0

        self.blender_angle = 0.0

        self.blender_rotation_speed = 720.0

        self.blender_shake = 0.0

        self.blender_bubble_offset = 0.0

    # ============================================================
    # BLENDER UPDATE
    # ============================================================

    def _update_blending(
        self,
        dt=0.0,
    ):

        # --------------------------------------------------------
        # ONLY ANIMATE DURING BLENDING
        # --------------------------------------------------------

        if (
            self.game_state.state
            != GameState.BLENDING
        ):

            return

        now = time.monotonic()

        elapsed = (
            now
            - self.blend_start_time
        )

        # --------------------------------------------------------
        # ROTATING BLADES
        # --------------------------------------------------------

        self.blender_angle = (
            self.blender_angle
            + self.blender_rotation_speed
            * max(dt, 0.016)
        ) % 360

        # --------------------------------------------------------
        # LIQUID / JUG MOVEMENT
        # --------------------------------------------------------

        self.blender_shake = (
            math.sin(
                elapsed * 34.0
            )
            * 3.0
        )

        # --------------------------------------------------------
        # BUBBLE MOVEMENT
        # --------------------------------------------------------

        self.blender_bubble_offset = (
            elapsed * 80.0
        )

        # --------------------------------------------------------
        # BLENDING FINISHED
        # --------------------------------------------------------

        if elapsed >= self.blend_duration:

            # Tell GameState that the actual blender process
            # has completed.

            finished = (
                self.game_state
                .finish_blending()
            )

            if finished:

                self._sync_legacy_values()

                # The Place button no longer exists.
                #
                # GameState is already changed to
                # READY_TO_SERVE by finish_blending().
                #
                # Nothing else is required here.

    # ============================================================
    # INPUT
    # ============================================================

    def handle_event(
        self,
        event,
    ):

        if (
            event.type
            != pygame.MOUSEBUTTONDOWN
        ):

            return

        if event.button != 1:

            return

        mouse = event.pos

        # ========================================================
        # DRINK MENU
        # ========================================================

        for drink_name, rect in self.menu_slots:

            if not rect.collidepoint(
                mouse
            ):

                continue

            # ----------------------------------------------------
            # VALID DRINK
            # ----------------------------------------------------

            if not is_valid_drink(
                drink_name
            ):

                return

            # ----------------------------------------------------
            # LOCKED DRINK
            # ----------------------------------------------------

            if not is_drink_unlocked(
                drink_name,
                self.level,
            ):

                return

            # ----------------------------------------------------
            # DON'T CHANGE DRINK DURING BLENDING
            # ----------------------------------------------------

            if self.game_state.state in (
                GameState.BLENDING,
                GameState.READY_TO_SERVE,
                GameState.SERVED,
            ):

                return

            # ----------------------------------------------------
            # SELECT
            # ----------------------------------------------------

            if self.game_state.state != (
                GameState.SELECT_DRINK
            ):

                self.game_state.state = (
                    GameState.SELECT_DRINK
                )

            selected = (
                self.game_state.select_drink(
                    drink_name
                )
            )

            if selected:

                self.player_drink.drink_name = (
                    drink_name
                )

                self._sync_legacy_values()

            return

        # ========================================================
        # CUSTOMISATION
        # ========================================================

        if self.game_state.can_customize():

            # ----------------------------------------------------
            # TEMPERATURE
            # ----------------------------------------------------

            for value, rect in (
                self.temperature_buttons.items()
            ):

                if rect.collidepoint(
                    mouse
                ):

                    if (
                        self.game_state
                        .select_temperature(
                            value
                        )
                    ):

                        self.player_drink.temperature = (
                            value
                        )

                        self._sync_legacy_values()

                    return

            # ----------------------------------------------------
            # CAFFEINE
            # ----------------------------------------------------

            for value, rect in (
                self.caffeine_buttons.items()
            ):

                if rect.collidepoint(
                    mouse
                ):

                    if (
                        self.game_state
                        .select_caffeine(
                            value
                        )
                    ):

                        self.player_drink.caffeine = (
                            value
                        )

                        self._sync_legacy_values()

                    return

            # ----------------------------------------------------
            # SWEETNESS
            # ----------------------------------------------------

            for value, rect in (
                self.sweetness_buttons.items()
            ):

                if rect.collidepoint(
                    mouse
                ):

                    if (
                        self.game_state
                        .select_sweetness(
                            value
                        )
                    ):

                        self.player_drink.sweetness = (
                            value
                        )

                        self._sync_legacy_values()

                    return

        # ========================================================
        # BLEND
        # ========================================================

        if self.blend_button.collidepoint(
            mouse
        ):

            if self.game_state.start_blending():

                self.blend_start_time = (
                    time.monotonic()
                )

                self.blender_angle = 0.0

                self.blender_shake = 0.0

                self.blender_bubble_offset = 0.0

            return

        # ========================================================
        # SERVE
        # ========================================================

        if self.serve_button.collidepoint(
            mouse
        ):

            if self.game_state.can_serve():

                if self.game_state.serve():

                    self.served = True

                    self._sync_legacy_values()

            return

    # ============================================================
    # UPDATE
    # ============================================================

    def update(
        self,
        dt=0.0,
    ):

        self._update_blending(
            dt
        )

    # ============================================================
    # DRAW
    # ============================================================

    def draw(
        self,
        screen,
    ):

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

        self._draw_toppings(
            screen
        )

        self._draw_preview(
            screen
        )

    # ============================================================
    # HUD
    # ============================================================

    def _draw_hud(
        self,
        screen,
    ):

        self._panel(
            screen,
            self.hud_rect,
            self.CYAN,
            self.PANEL,
        )

        level = self.level

        xp = 0

        max_xp = 100

        credits = 0

        combo = 0

        # --------------------------------------------------------
        # PROGRESSION
        # --------------------------------------------------------

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

            if hasattr(
                self.progression,
                "get_xp_required",
            ):

                try:

                    max_xp = (
                        self.progression
                        .get_xp_required()
                    )

                except Exception:

                    max_xp = 100

        # --------------------------------------------------------
        # ECONOMY
        # --------------------------------------------------------

        if self.economy is not None:

            credits = getattr(
                self.economy,
                "credits",
                0,
            )

        # --------------------------------------------------------
        # COMBO
        # --------------------------------------------------------

        if self.rewards is not None:

            combo = getattr(
                self.rewards,
                "combo_count",
                getattr(
                    self.rewards,
                    "combo",
                    0,
                ),
            )

        # ========================================================
        # LEVEL
        # ========================================================

        level_surface = self.font_medium.render(
            f"★ LEVEL {level}",
            True,
            self.WHITE,
        )

        screen.blit(
            level_surface,
            (32, 29),
        )

        # ========================================================
        # XP
        # ========================================================

        xp_label = self.font_small.render(
            "XP",
            True,
            self.PINK_BRIGHT,
        )

        screen.blit(
            xp_label,
            (142, 31),
        )

        # --------------------------------------------------------
        # VERY COMPACT XP BAR
        # --------------------------------------------------------

        xp_bar = pygame.Rect(
            165,
            28,
            125,
            16,
        )

        pygame.draw.rect(
            screen,
            (18, 24, 48),
            xp_bar,
            border_radius=8,
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            xp_bar,
            width=2,
            border_radius=8,
        )

        if max_xp > 0:

            ratio = max(
                0.0,
                min(
                    1.0,
                    xp / max_xp,
                ),
            )

        else:

            ratio = 0.0

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
                center=xp_bar.center
            ),
        )

        # ========================================================
        # CREDITS
        # ========================================================

        credit_surface = self.font_medium.render(
            f"☕ ${credits}",
            True,
            self.YELLOW,
        )

        screen.blit(
            credit_surface,
            (310, 29),
        )

        # ========================================================
        # COMBO
        # ========================================================

        combo_surface = self.font_medium.render(
            f"🔥 ×{combo}",
            True,
            self.CYAN_BRIGHT,
        )

        screen.blit(
            combo_surface,
            (410, 29),
        )

    # ============================================================
    # MENU DRAW
    # ============================================================

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

        for drink_name, rect in self.menu_slots:

            unlocked = is_drink_unlocked(
                drink_name,
                self.level,
            )

            selected = (
                self.player_drink.drink_name
                == drink_name
            )

            # ----------------------------------------------------
            # SAME PANEL FILL
            # ----------------------------------------------------

            fill = self.PANEL_INNER

            if selected:

                border = self.PINK_BRIGHT

            elif unlocked:

                border = self.CYAN

            else:

                border = self.LOCKED

            self._panel(
                screen,
                rect,
                border,
                fill,
            )

            # ----------------------------------------------------
            # IMAGE
            # ----------------------------------------------------

            image = self.drink_images.get(
                drink_name
            )

            image_area = pygame.Rect(
                rect.x + 6,
                rect.y + 7,
                rect.width - 12,
                116,
            )

            if image is not None:

                self._image_fit(
                    screen,
                    image,
                    image_area,
                    unlocked,
                )

            # ----------------------------------------------------
            # LOCK
            # ----------------------------------------------------

            if not unlocked:

                self._draw_lock(
                    screen,
                    rect.centerx,
                    rect.y + 70,
                )

            # ----------------------------------------------------
            # NAME
            # ----------------------------------------------------

            name_surface = self.font_small.render(
                drink_name,
                True,
                (
                    self.WHITE
                    if unlocked
                    else self.LOCKED
                ),
            )

            screen.blit(
                name_surface,
                name_surface.get_rect(
                    center=(
                        rect.centerx,
                        rect.bottom - 20,
                    )
                ),
            )

    # ============================================================
    # CUSTOMISE
    # ============================================================

    def _draw_customise(
        self,
        screen,
    ):

        self._panel(
            screen,
            self.customise_rect,
            self.CYAN,
            self.PANEL,
        )

        title = self.font_large.render(
            "CUSTOMISE YOUR DRINK",
            True,
            self.CYAN_BRIGHT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.customise_rect.centerx,
                    432,
                )
            ),
        )

        self._draw_option_row(
            screen,
            "TEMPERATURE",
            self.temperature_buttons,
            self.player_drink.temperature,
        )

        self._draw_option_row(
            screen,
            "CAFFEINE LEVEL",
            self.caffeine_buttons,
            self.player_drink.caffeine,
        )

        self._draw_option_row(
            screen,
            "SWEETNESS LEVEL",
            self.sweetness_buttons,
            self.player_drink.sweetness,
        )

    # ============================================================
    # OPTION ROW
    # ============================================================

    def _draw_option_row(
        self,
        screen,
        label,
        buttons,
        selected,
    ):

        if not buttons:

            return

        first = next(
            iter(
                buttons.values()
            )
        )

        label_surface = self.font_small.render(
            label,
            True,
            self.CYAN,
        )

        screen.blit(
            label_surface,
            (
                first.x,
                first.y - 17,
            ),
        )

        enabled = (
            self.game_state.can_customize()
        )

        for value, rect in buttons.items():

            active = (
                value == selected
            )

            if active:

                fill = (
                    45,
                    15,
                    55,
                )

                border = self.PINK_BRIGHT

            elif enabled:

                fill = self.BUTTON_DARK

                border = self.CYAN

            else:

                fill = (
                    8,
                    11,
                    24,
                )

                border = self.LOCKED

            self._panel(
                screen,
                rect,
                border,
                fill,
            )

            text_surface = self.font_small.render(
                value,
                True,
                (
                    self.WHITE
                    if enabled
                    else self.MUTED
                ),
            )

            screen.blit(
                text_surface,
                text_surface.get_rect(
                    center=rect.center
                ),
            )

    # ============================================================
    # BLENDER
    # ============================================================

    def _draw_blender(
        self,
        screen,
    ):

        self._panel(
            screen,
            self.blender_rect,
            self.CYAN,
            self.PANEL,
        )

        title = self.font_large.render(
            "BLENDER",
            True,
            self.CYAN_BRIGHT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.blender_rect.centerx,
                    432,
                )
            ),
        )

        # --------------------------------------------------------
        # CURRENT ANIMATION TIME
        # --------------------------------------------------------

        now = time.monotonic()

        if (
            self.game_state.state
            == GameState.BLENDING
        ):

            elapsed = (
                now
                - self.blend_start_time
            )

        else:

            elapsed = 0.0

        # --------------------------------------------------------
        # JUG MOVEMENT
        # --------------------------------------------------------

        shake_x = 0.0

        shake_y = 0.0

        if (
            self.game_state.state
            == GameState.BLENDING
        ):

            shake_x = (
                math.sin(
                    elapsed * 34.0
                )
                * 3.0
            )

            shake_y = (
                math.cos(
                    elapsed * 42.0
                )
                * 1.5
            )

        jug = self.blender_jug_rect.move(
            int(shake_x),
            int(shake_y),
        )

        # --------------------------------------------------------
        # JUG OUTLINE
        # --------------------------------------------------------

        pygame.draw.rect(
            screen,
            (18, 25, 52),
            jug,
            border_radius=24,
        )

        pygame.draw.rect(
            screen,
            self.CYAN_BRIGHT,
            jug,
            width=3,
            border_radius=24,
        )

        # --------------------------------------------------------
        # HANDLE
        # --------------------------------------------------------

        handle = pygame.Rect(
            jug.right - 4,
            jug.y + 37,
            27,
            70,
        )

        pygame.draw.rect(
            screen,
            (18, 22, 45),
            handle,
            border_radius=12,
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            handle,
            width=2,
            border_radius=12,
        )

        # --------------------------------------------------------
        # SELECTED RECIPE
        # --------------------------------------------------------

        drink_name = (
            self.player_drink.drink_name
        )

        recipe = None

        if drink_name:

            recipe = get_recipe(
                drink_name
            )

        # --------------------------------------------------------
        # LIQUID
        # --------------------------------------------------------

        if recipe is not None:

            liquid_colour = (
                recipe.liquid_color
            )

            # Hologram Frappe gets a changing holographic colour.
            if drink_name == "Hologram Frappe":

                liquid_colour = (
                    self._hologram_colour(
                        elapsed
                    )
                )

            # ----------------------------------------------------
            # LIQUID HEIGHT
            # ----------------------------------------------------

            liquid_height = 88

            if (
                self.game_state.state
                == GameState.BLENDING
            ):

                liquid_height += int(
                    math.sin(
                        elapsed * 18.0
                    )
                    * 5
                )

            liquid = pygame.Rect(
                jug.x + 12,
                jug.bottom
                - liquid_height
                - 10,
                jug.width - 24,
                liquid_height,
            )

            # ----------------------------------------------------
            # LIQUID BODY
            # ----------------------------------------------------

            pygame.draw.rect(
                screen,
                liquid_colour,
                liquid,
                border_radius=16,
            )

            # ----------------------------------------------------
            # LIQUID GLOW
            # ----------------------------------------------------

            glow_colour = (
                min(
                    255,
                    liquid_colour[0] + 40,
                ),
                min(
                    255,
                    liquid_colour[1] + 40,
                ),
                min(
                    255,
                    liquid_colour[2] + 40,
                ),
            )

            pygame.draw.rect(
                screen,
                glow_colour,
                liquid,
                width=2,
                border_radius=16,
            )

            # ----------------------------------------------------
            # SURFACE WAVES
            # ----------------------------------------------------

            wave_y = (
                liquid.y + 13
            )

            wave_offset = 0.0

            if (
                self.game_state.state
                == GameState.BLENDING
            ):

                wave_offset = (
                    math.sin(
                        elapsed * 12.0
                    )
                    * 7
                )

            points = []

            for i in range(0, 11):

                px = (
                    liquid.x
                    + 10
                    + i
                    * (
                        (
                            liquid.width - 20
                        )
                        / 10
                    )
                )

                py = (
                    wave_y
                    + math.sin(
                        i * 1.5
                        + elapsed * 12.0
                    )
                    * 3
                    + wave_offset
                )

                points.append(
                    (
                        int(px),
                        int(py),
                    )
                )

            if len(points) >= 2:

                pygame.draw.lines(
                    screen,
                    self.WHITE,
                    False,
                    points,
                    2,
                )

            # ----------------------------------------------------
            # BLENDER VORTEX
            # ----------------------------------------------------

            if (
                self.game_state.state
                == GameState.BLENDING
            ):

                centre_x = (
                    liquid.centerx
                )

                centre_y = (
                    liquid.centery
                    + 5
                )

                for ring in range(3):

                    radius = (
                        16
                        + ring * 14
                        + int(
                            (
                                elapsed
                                * 35
                            )
                            % 12
                        )
                    )

                    pygame.draw.arc(
                        screen,
                        self.WHITE,
                        pygame.Rect(
                            centre_x - radius,
                            centre_y - radius // 2,
                            radius * 2,
                            radius,
                        ),
                        0.2,
                        2.8,
                        2,
                    )

            # ----------------------------------------------------
            # BUBBLES
            # ----------------------------------------------------

            self._draw_blender_bubbles(
                screen,
                liquid,
                elapsed,
            )

            # ----------------------------------------------------
            # DRINK-SPECIFIC EFFECTS
            # ----------------------------------------------------

            self._draw_drink_effect(
                screen,
                liquid,
                drink_name,
                elapsed,
            )

        else:

            select_text = self.font_medium.render(
                "SELECT A DRINK",
                True,
                self.MUTED,
            )

            screen.blit(
                select_text,
                select_text.get_rect(
                    center=jug.center,
                ),
            )

        # --------------------------------------------------------
        # BLENDER BLADE
        # --------------------------------------------------------

        self._draw_blender_blades(
            screen,
            jug,
            elapsed,
        )

        # --------------------------------------------------------
        # BASE
        # --------------------------------------------------------

        base = pygame.Rect(
            jug.x - 18,
            jug.bottom - 5,
            jug.width + 36,
            40,
        )

        pygame.draw.rect(
            screen,
            (22, 18, 40),
            base,
            border_radius=12,
        )

        pygame.draw.rect(
            screen,
            self.PINK,
            base,
            width=2,
            border_radius=12,
        )

        # --------------------------------------------------------
        # BLEND BUTTON
        # --------------------------------------------------------

        self._action_button(
            screen,
            self.blend_button,
            "BLEND",
            self.PINK,
            self.game_state.can_blend(),
        )

        # --------------------------------------------------------
        # BLENDING PROGRESS
        # --------------------------------------------------------

        if (
            self.game_state.state
            == GameState.BLENDING
        ):

            ratio = min(
                1.0,
                elapsed
                / self.blend_duration,
            )

            progress_rect = pygame.Rect(
                self.blender_rect.x + 25,
                590,
                self.blender_rect.width - 50,
                8,
            )

            pygame.draw.rect(
                screen,
                (20, 25, 45),
                progress_rect,
                border_radius=4,
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
                border_radius=4,
            )

    # ============================================================
    # BLENDER BLADES
    # ============================================================

    def _draw_blender_blades(
        self,
        screen,
        jug,
        elapsed,
    ):

        centre = (
            jug.centerx,
            jug.bottom - 33,
        )

        # --------------------------------------------------------
        # Only visibly spin during blending.
        # --------------------------------------------------------

        if (
            self.game_state.state
            == GameState.BLENDING
        ):

            angle = math.radians(
                self.blender_angle
            )

        else:

            angle = 0.0

        blade_length = 24

        for blade_angle in (
            angle,
            angle + math.pi,
        ):

            x2 = (
                centre[0]
                + math.cos(
                    blade_angle
                )
                * blade_length
            )

            y2 = (
                centre[1]
                + math.sin(
                    blade_angle
                )
                * blade_length
                * 0.45
            )

            pygame.draw.line(
                screen,
                self.WHITE,
                centre,
                (
                    int(x2),
                    int(y2),
                ),
                5,
            )

        pygame.draw.circle(
            screen,
            self.PINK_BRIGHT,
            centre,
            6,
        )

    # ============================================================
    # BLENDER BUBBLES
    # ============================================================

    def _draw_blender_bubbles(
        self,
        screen,
        liquid,
        elapsed,
    ):

        if (
            self.game_state.state
            != GameState.BLENDING
        ):

            return

        bubble_positions = (
            (
                0.20,
                0.75,
                4,
            ),
            (
                0.42,
                0.60,
                3,
            ),
            (
                0.66,
                0.78,
                5,
            ),
            (
                0.78,
                0.48,
                3,
            ),
            (
                0.31,
                0.40,
                3,
            ),
        )

        for index, (
            x_ratio,
            y_ratio,
            radius,
        ) in enumerate(
            bubble_positions
        ):

            rise = (
                elapsed
                * (
                    0.25
                    + index * 0.06
                )
            ) % 0.35

            x = (
                liquid.x
                + int(
                    liquid.width
                    * x_ratio
                )
            )

            y = (
                liquid.y
                + int(
                    liquid.height
                    * (
                        y_ratio
                        - rise
                    )
                )
            )

            if y < liquid.y + 5:

                y = (
                    liquid.bottom
                    - 15
                )

            pygame.draw.circle(
                screen,
                (
                    240,
                    250,
                    255,
                ),
                (
                    x,
                    y,
                ),
                radius,
                1,
            )

    # ============================================================
    # DRINK-SPECIFIC EFFECT
    # ============================================================

    def _draw_drink_effect(
        self,
        screen,
        liquid,
        drink_name,
        elapsed,
    ):

        if (
            self.game_state.state
            != GameState.BLENDING
        ):

            return

        # --------------------------------------------------------
        # MILKYWAY
        # --------------------------------------------------------

        if drink_name == "Milkyway":

            for index in range(5):

                x = (
                    liquid.x
                    + 15
                    + (
                        index * 29
                    )
                )

                y = (
                    liquid.y
                    + 20
                    + int(
                        math.sin(
                            elapsed * 4
                            + index
                        )
                        * 10
                    )
                )

                pygame.draw.circle(
                    screen,
                    self.WHITE,
                    (
                        x,
                        y,
                    ),
                    2,
                )

        # --------------------------------------------------------
        # PIXEL LEMINT
        # --------------------------------------------------------

        elif drink_name == "Pixel Lemint":

            for index in range(3):

                x = (
                    liquid.x
                    + 25
                    + index * 45
                )

                y = (
                    liquid.y
                    + 30
                    + int(
                        math.sin(
                            elapsed * 5
                            + index
                        )
                        * 8
                    )
                )

                pygame.draw.rect(
                    screen,
                    self.MINT,
                    pygame.Rect(
                        x,
                        y,
                        5,
                        5,
                    ),
                )

        # --------------------------------------------------------
        # STARDUST MATCHA
        # --------------------------------------------------------

        elif drink_name == "Stardust Matcha":

            for index in range(3):

                x = (
                    liquid.x
                    + 30
                    + index * 42
                )

                y = (
                    liquid.y
                    + 20
                    + int(
                        math.sin(
                            elapsed * 4
                            + index
                        )
                        * 12
                    )
                )

                self._draw_star(
                    screen,
                    x,
                    y,
                    5,
                    self.YELLOW,
                )

        # --------------------------------------------------------
        # METEORITE
        # --------------------------------------------------------

        elif drink_name == "Meteorite":

            for index in range(3):

                x = (
                    liquid.x
                    + 30
                    + index * 42
                )

                y = (
                    liquid.y
                    + 30
                    + int(
                        (
                            elapsed * 30
                            + index * 25
                        )
                        % max(
                            1,
                            liquid.height - 15,
                        )
                    )
                )

                pygame.draw.circle(
                    screen,
                    self.CYAN_BRIGHT,
                    (
                        x,
                        y,
                    ),
                    3,
                )

        # --------------------------------------------------------
        # CYBER FUEL
        # --------------------------------------------------------

        elif drink_name == "Cyber Fuel":

            for index in range(3):

                y = (
                    liquid.y
                    + 20
                    + index * 20
                )

                pygame.draw.line(
                    screen,
                    self.CYAN_BRIGHT,
                    (
                        liquid.x + 20,
                        y,
                    ),
                    (
                        liquid.right - 20,
                        y + 5,
                    ),
                    2,
                )

    # ============================================================
    # HOLOGRAM COLOUR
    # ============================================================

    def _hologram_colour(
        self,
        elapsed,
    ):

        colours = (
            (
                190,
                120,
                255,
            ),
            (
                90,
                220,
                255,
            ),
            (
                255,
                110,
                210,
            ),
            (
                120,
                255,
                220,
            ),
        )

        position = (
            elapsed * 3.0
        )

        index_a = int(
            position
        ) % len(colours)

        index_b = (
            index_a + 1
        ) % len(colours)

        fraction = (
            position
            - int(position)
        )

        colour_a = colours[index_a]

        colour_b = colours[index_b]

        return (
            int(
                colour_a[0]
                + (
                    colour_b[0]
                    - colour_a[0]
                )
                * fraction
            ),
            int(
                colour_a[1]
                + (
                    colour_b[1]
                    - colour_a[1]
                )
                * fraction
            ),
            int(
                colour_a[2]
                + (
                    colour_b[2]
                    - colour_a[2]
                )
                * fraction
            ),
        )

    # ============================================================
    # TOPPINGS
    # ============================================================

    def _draw_toppings(
        self,
        screen,
    ):

        text = self.font_small.render(
            "TOPPINGS • AUTOMATIC • VISUAL ONLY",
            True,
            self.MUTED,
        )

        screen.blit(
            text,
            (
                785,
                687,
            ),
        )

    # ============================================================
    # PREVIEW
    # ============================================================

    def _draw_preview(
        self,
        screen,
    ):

        self._panel(
            screen,
            self.preview_rect,
            self.CYAN,
            self.PANEL,
        )

        title = self.font_medium.render(
            "PREVIEW",
            True,
            self.PINK_BRIGHT,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.preview_rect.centerx,
                    432,
                )
            ),
        )

        # --------------------------------------------------------
        # IMAGE
        # --------------------------------------------------------

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
                    center=(
                        self.preview_image_rect.center
                    )
                ),
            )

        # --------------------------------------------------------
        # SERVE
        # --------------------------------------------------------

        self._action_button(
            screen,
            self.serve_button,
            "SERVE",
            self.CYAN,
            self.game_state.can_serve(),
        )

    # ============================================================
    # GENERIC PANEL
    # ============================================================

    def _panel(
        self,
        screen,
        rect,
        border,
        fill,
    ):

        surface = pygame.Surface(
            rect.size,
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            surface,
            fill,
            surface.get_rect(),
            border_radius=14,
        )

        screen.blit(
            surface,
            rect.topleft,
        )

        pygame.draw.rect(
            screen,
            border,
            rect,
            width=2,
            border_radius=14,
        )

    # ============================================================
    # ACTION BUTTON
    # ============================================================

    def _action_button(
        self,
        screen,
        rect,
        text,
        accent,
        enabled,
    ):

        mouse = pygame.mouse.get_pos()

        hover = (
            enabled
            and rect.collidepoint(mouse)
        )

        if enabled:

            border = (
                self.PINK_BRIGHT
                if hover
                else accent
            )

            fill = (
                45,
                15,
                55,
            )

            text_colour = self.WHITE

        else:

            border = self.LOCKED

            fill = (
                9,
                12,
                25,
            )

            text_colour = self.MUTED

        self._panel(
            screen,
            rect,
            border,
            fill,
        )

        label = self.font_large.render(
            text,
            True,
            text_colour,
        )

        screen.blit(
            label,
            label.get_rect(
                center=rect.center,
            ),
        )

    # ============================================================
    # IMAGE FIT
    # ============================================================

    def _image_fit(
        self,
        screen,
        image,
        target,
        bright=True,
    ):

        width, height = image.get_size()

        if (
            width <= 0
            or height <= 0
        ):

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
                    80,
                    80,
                    100,
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

    # ============================================================
    # LOCK ICON
    # ============================================================

    def _draw_lock(
        self,
        screen,
        x,
        y,
    ):

        body = pygame.Rect(
            x - 10,
            y,
            20,
            17,
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
                x - 7,
                y - 13,
                14,
                18,
            ),
            3.14,
            6.28,
            3,
        )

    # ============================================================
    # STAR
    # ============================================================

    def _draw_star(
        self,
        screen,
        x,
        y,
        radius,
        colour,
    ):

        points = []

        for index in range(10):

            angle = (
                -math.pi / 2
                + index
                * math.pi
                / 5
            )

            current_radius = (
                radius
                if index % 2 == 0
                else radius * 0.45
            )

            points.append(
                (
                    int(
                        x
                        + math.cos(angle)
                        * current_radius
                    ),
                    int(
                        y
                        + math.sin(angle)
                        * current_radius
                    ),
                )
            )

        pygame.draw.polygon(
            screen,
            colour,
            points,
        )

    # ============================================================
    # RESET
    # ============================================================

    def reset(self):

        self.player_drink.reset()

        self.game_state.reset()

        self.customer_order = None

        self.served = False

        self._reset_blender_animation()

        if self.drink is not None:

            try:

                self.drink.reset()

            except Exception:

                pass

        self._attach_legacy_bridge()
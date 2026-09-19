from __future__ import annotations

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
    # MASTER GAME SIZE
    # ============================================================

    WIDTH = 1280
    HEIGHT = 720

    # ============================================================
    # COLOURS
    # ============================================================

    DARK = (6, 8, 20)

    PANEL = (8, 13, 31, 235)
    PANEL_DARK = (5, 8, 20, 235)

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

    # ============================================================
    # INITIALISATION
    # ============================================================

    def __init__(
        self,
        drink,
        level=1,
        progression=None,
        rewards=None,
    ):

        # --------------------------------------------------------
        # EXISTING DRINK OBJECT
        # --------------------------------------------------------

        self.drink = drink

        # --------------------------------------------------------
        # NEW DRINK SYSTEM
        # --------------------------------------------------------

        self.player_drink = PlayerDrink()

        self.game_state = MixingGameState()

        # --------------------------------------------------------
        # PROGRESSION / REWARDS
        # --------------------------------------------------------

        self.progression = progression
        self.rewards = rewards

        self.level = level

        # --------------------------------------------------------
        # CUSTOMER ORDER
        # --------------------------------------------------------

        self.customer_order = None

        # --------------------------------------------------------
        # SERVED FLAG
        # --------------------------------------------------------

        self.served = False

        # --------------------------------------------------------
        # BLENDER
        # --------------------------------------------------------

        self.blend_start_time = 0

        self.blend_duration = 1.2

        # ========================================================
        # FONTS
        # ========================================================

        self.font_title = pygame.font.SysFont(
            "arial",
            20,
            bold=True,
        )

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
            25,
            bold=True,
        )

        self.font_xlarge = pygame.font.SysFont(
            "arial",
            32,
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
        # LOAD DRINK IMAGES
        # ========================================================

        self.drink_images = {}

        self._load_drink_images()

        # ========================================================
        # FINAL 1280 x 720 LAYOUT
        # ========================================================

        # --------------------------------------------------------
        # TOP HUD
        # --------------------------------------------------------

        self.hud_rect = pygame.Rect(
            398,
            12,
            860,
            55,
        )

        # --------------------------------------------------------
        # DRINK MENU
        # --------------------------------------------------------

        self.menu_rect = pygame.Rect(
            275,
            82,
            970,
            220,
        )

        # --------------------------------------------------------
        # CUSTOMER ORDER
        # --------------------------------------------------------

        self.order_rect = pygame.Rect(
            35,
            560,
            430,
            135,
        )

        # --------------------------------------------------------
        # CUSTOMISATION
        # --------------------------------------------------------

        self.customise_rect = pygame.Rect(
            490,
            400,
            300,
            295,
        )

        # --------------------------------------------------------
        # BLENDER
        # --------------------------------------------------------

        self.blender_rect = pygame.Rect(
            800,
            400,
            300,
            295,
        )

        # --------------------------------------------------------
        # FINAL PREVIEW
        # --------------------------------------------------------

        self.preview_rect = pygame.Rect(
            1110,
            400,
            145,
            295,
        )

        # --------------------------------------------------------
        # BLENDER JUG
        # --------------------------------------------------------

        self.blender_jug_rect = pygame.Rect(
            855,
            430,
            190,
            150,
        )

        # --------------------------------------------------------
        # BLEND BUTTON
        # --------------------------------------------------------

        self.blend_button = pygame.Rect(
            850,
            585,
            200,
            75,
        )

        # --------------------------------------------------------
        # PREVIEW IMAGE
        # --------------------------------------------------------

        self.preview_image_rect = pygame.Rect(
            1125,
            445,
            115,
            125,
        )

        # --------------------------------------------------------
        # PLACE INTO CUP
        # --------------------------------------------------------

        self.place_button = pygame.Rect(
            1120,
            580,
            125,
            45,
        )

        # --------------------------------------------------------
        # SERVE
        # --------------------------------------------------------

        self.serve_button = pygame.Rect(
            1120,
            635,
            125,
            45,
        )

        # --------------------------------------------------------
        # TOPPINGS
        # --------------------------------------------------------

        self.toppings_rect = pygame.Rect(
            800,
            665,
            300,
            30,
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
        # TOPPING INFORMATION
        # ========================================================

        self.topping_names = (
            "WHIPPED CREAM",
            "MINT",
            "CHOCOLATE",
            "CARAMEL",
            "STARDUST",
            "METEORITE",
        )

        # ========================================================
        # LEGACY COMPATIBILITY
        # ========================================================

        self._attach_legacy_bridge()

    # ============================================================
    # LOAD DRINK IMAGES
    # ============================================================

    def _load_drink_images(self):

        filenames = {

            "Neon Latte":
                "neon_latte.png",

            "Milkyway":
                "milkyway.png",

            "Void Chai":
                "void_chai.png",

            "Cyber Fuel":
                "cyber_fuel.png",

            "Hologram Frappe":
                "hologram_frappe.png",

            "Pixel Lemint":
                "pixel_lemint.png",

            "Caramel Byte":
                "caramel_byte.png",

            "Stardust Matcha":
                "stardust_matcha.png",

            "Meteorite":
                "meteorite.png",
        }

        for name, filename in filenames.items():

            path = os.path.join(
                self.drink_dir,
                filename,
            )

            try:

                image = pygame.image.load(
                    path
                ).convert_alpha()

                self.drink_images[name] = image

            except (
                pygame.error,
                FileNotFoundError,
            ):

                self.drink_images[name] = None

    # ============================================================
    # MENU
    # ============================================================

    def _create_menu_slots(self):

        # Nine large cards.

        left = 285

        top = 94

        width = 102

        height = 192

        gap = 5

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
    # CUSTOMISATION BUTTONS
    # ============================================================

    def _create_option_buttons(self):

        # --------------------------------------------------------
        # TEMPERATURE
        # --------------------------------------------------------

        x_positions = (
            510,
            610,
            710,
        )

        for x, value in zip(
            x_positions,
            TEMPERATURE_OPTIONS,
        ):

            self.temperature_buttons[value] = pygame.Rect(
                x,
                465,
                82,
                55,
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
                535,
                82,
                55,
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
                605,
                82,
                55,
            )

    # ============================================================
    # CUSTOMER ORDER
    # ============================================================

    def set_customer_order(self, order):

        self.customer_order = order

        self.player_drink.reset()

        self.game_state.set_order(
            order
        )

        self.served = False

    def update_customer_order(self, order):

        self.set_customer_order(
            order
        )

    # ============================================================
    # LEVEL
    # ============================================================

    def set_level(self, level):

        self.level = max(
            1,
            int(level),
        )

    # ============================================================
    # PROGRESSION
    # ============================================================

    def set_progression(self, progression):

        self.progression = progression

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

    def set_rewards(self, rewards):

        self.rewards = rewards

    # ============================================================
    # DRINK DATA
    # ============================================================

    def get_player_drink_data(self):

        return self.game_state.get_player_drink_data()

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
    # UPDATE BLENDING
    # ============================================================

    def _update_blending(self):

        if (
            self.game_state.state
            != GameState.BLENDING
        ):

            return

        elapsed = (
            time.monotonic()
            - self.blend_start_time
        )

        if elapsed >= self.blend_duration:

            self.game_state.finish_blending()

            self._sync_legacy_values()

    # ============================================================
    # INPUT
    # ============================================================

    def handle_event(self, event):

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        mouse = event.pos

        self._update_blending()

        # ========================================================
        # DRINK MENU
        # ========================================================

        for drink_name, rect in self.menu_slots:

            if not rect.collidepoint(mouse):
                continue

            if not is_valid_drink(drink_name):
                return

            if not is_drink_unlocked(
                drink_name,
                self.level,
            ):
                return

            if self.game_state.state in (
                GameState.BLENDING,
                GameState.BLENDED,
                GameState.CUP_READY,
                GameState.READY_TO_SERVE,
                GameState.SERVED,
            ):
                return

            self.game_state.state = (
                GameState.SELECT_DRINK
            )

            if self.game_state.select_drink(
                drink_name
            ):

                self.player_drink.drink_name = (
                    drink_name
                )

            return

        # ========================================================
        # CUSTOMISATION
        # ========================================================

        if self.game_state.can_customize():

            for value, rect in (
                self.temperature_buttons.items()
            ):

                if rect.collidepoint(mouse):

                    self.game_state.select_temperature(
                        value
                    )

                    self.player_drink.temperature = (
                        value
                    )

                    self._sync_legacy_values()

                    return

            for value, rect in (
                self.caffeine_buttons.items()
            ):

                if rect.collidepoint(mouse):

                    self.game_state.select_caffeine(
                        value
                    )

                    self.player_drink.caffeine = (
                        value
                    )

                    self._sync_legacy_values()

                    return

            for value, rect in (
                self.sweetness_buttons.items()
            ):

                if rect.collidepoint(mouse):

                    self.game_state.select_sweetness(
                        value
                    )

                    self.player_drink.sweetness = (
                        value
                    )

                    self._sync_legacy_values()

                    return

        # ========================================================
        # BLEND
        # ========================================================

        if self.blend_button.collidepoint(mouse):

            if self.game_state.start_blending():

                self.blend_start_time = (
                    time.monotonic()
                )

            return

        # ========================================================
        # PLACE INTO CUP
        # ========================================================

        if self.place_button.collidepoint(mouse):

            self.game_state.place_into_cup()

            return

        # ========================================================
        # SERVE
        # ========================================================

        if self.serve_button.collidepoint(mouse):

            if self.game_state.serve():

                self.served = True

                self._sync_legacy_values()

            return

    # ============================================================
    # DRAW
    # ============================================================

    def draw(self, screen):

        self._update_blending()

        self._draw_hud(screen)

        self._draw_menu(screen)

        self._draw_order(screen)

        self._draw_customise(screen)

        self._draw_blender(screen)

        self._draw_toppings(screen)

        self._draw_preview(screen)

    # ============================================================
    # HUD
    # ============================================================

    def _draw_hud(self, screen):

        rect = self.hud_rect

        self._panel(
            screen,
            rect,
            self.CYAN,
            self.PANEL_DARK,
        )

        level = self.level

        xp = 0

        max_xp = 100

        credits = 0

        combo = 0

        # --------------------------------------------------------
        # PROGRESSION DATA
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

            max_xp = getattr(
                self.progression,
                "xp_required",
                max_xp,
            )

            if callable(max_xp):

                max_xp = max_xp()

        # --------------------------------------------------------
        # REWARD DATA
        # --------------------------------------------------------

        if self.rewards is not None:

            credits = getattr(
                self.rewards,
                "credits",
                credits,
            )

            combo = getattr(
                self.rewards,
                "combo",
                combo,
            )

        # --------------------------------------------------------
        # LEVEL
        # --------------------------------------------------------

        level_text = self.font_large.render(
            f"★  LEVEL {level}",
            True,
            self.WHITE,
        )

        screen.blit(
            level_text,
            (420, 25),
        )

        # --------------------------------------------------------
        # XP LABEL
        # --------------------------------------------------------

        xp_label = self.font_large.render(
            "XP",
            True,
            self.PINK_BRIGHT,
        )

        screen.blit(
            xp_label,
            (595, 25),
        )

        # --------------------------------------------------------
        # XP BAR
        # --------------------------------------------------------

        xp_bar = pygame.Rect(
            650,
            27,
            205,
            22,
        )

        pygame.draw.rect(
            screen,
            (18, 24, 48),
            xp_bar,
            border_radius=11,
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            xp_bar,
            width=2,
            border_radius=11,
        )

        ratio = 0

        if max_xp > 0:

            ratio = max(
                0,
                min(
                    1,
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
                border_radius=8,
            )

        xp_number = self.font_small.render(
            f"{xp} / {max_xp}",
            True,
            self.WHITE,
        )

        screen.blit(
            xp_number,
            xp_number.get_rect(
                center=xp_bar.center
            ),
        )

        # --------------------------------------------------------
        # CREDITS
        # --------------------------------------------------------

        credit_text = self.font_large.render(
            f"☕ CREDITS   ${credits}",
            True,
            self.YELLOW,
        )

        screen.blit(
            credit_text,
            (875, 25),
        )

        # --------------------------------------------------------
        # COMBO
        # --------------------------------------------------------

        combo_text = self.font_large.render(
            f"🔥 COMBO × {combo}",
            True,
            self.CYAN_BRIGHT,
        )

        screen.blit(
            combo_text,
            (1070, 25),
        )

    # ============================================================
    # DRINK MENU
    # ============================================================

    def _draw_menu(self, screen):

        self._panel(
            screen,
            self.menu_rect,
            self.CYAN,
            self.PANEL_DARK,
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

            if selected:

                border = self.PINK_BRIGHT

                fill = (
                    45,
                    14,
                    52,
                    245,
                )

            elif unlocked:

                border = self.CYAN

                fill = (
                    10,
                    16,
                    34,
                    245,
                )

            else:

                border = (
                    50,
                    55,
                    80,
                )

                fill = (
                    8,
                    10,
                    22,
                    235,
                )

            self._panel(
                screen,
                rect,
                border,
                fill,
            )

            # ----------------------------------------------------
            # DRINK IMAGE
            # ----------------------------------------------------

            image = self.drink_images.get(
                drink_name
            )

            image_area = pygame.Rect(
                rect.x + 8,
                rect.y + 10,
                rect.width - 16,
                135,
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
                    rect.y + 80,
                )

            # ----------------------------------------------------
            # NAME
            # ----------------------------------------------------

            name = self.font_small.render(
                drink_name,
                True,
                (
                    self.WHITE
                    if unlocked
                    else self.LOCKED
                ),
            )

            screen.blit(
                name,
                name.get_rect(
                    center=(
                        rect.centerx,
                        rect.bottom - 27,
                    )
                ),
            )

    # ============================================================
    # CURRENT ORDER
    # ============================================================

    def _draw_order(self, screen):

        self._panel(
            screen,
            self.order_rect,
            self.PINK,
            self.PANEL,
        )

        title = self.font_medium.render(
            "☕  CURRENT ORDER",
            True,
            self.PINK_BRIGHT,
        )

        screen.blit(
            title,
            (55, 572),
        )

        if self.customer_order is None:

            text = self.font_medium.render(
                "WAITING FOR CUSTOMER...",
                True,
                self.MUTED,
            )

            screen.blit(
                text,
                (55, 625),
            )

            return

        order = self.customer_order

        drink_name = getattr(
            order,
            "drink",
            None,
        )

        temperature = getattr(
            order,
            "temperature",
            None,
        )

        caffeine = getattr(
            order,
            "caffeine",
            None,
        )

        sweetness = getattr(
            order,
            "sweetness",
            None,
        )

        # --------------------------------------------------------
        # SMALL DRINK IMAGE
        # --------------------------------------------------------

        image = self.drink_images.get(
            drink_name
        )

        if image is not None:

            self._image_fit(
                screen,
                image,
                pygame.Rect(
                    55,
                    600,
                    65,
                    80,
                ),
                True,
            )

        # --------------------------------------------------------
        # ORDER TEXT
        # --------------------------------------------------------

        drink_text = self.font_medium.render(
            str(drink_name),
            True,
            self.PINK_BRIGHT,
        )

        screen.blit(
            drink_text,
            (135, 600),
        )

        values = (
            temperature,
            caffeine,
            sweetness,
        )

        labels = (
            "Temperature",
            "Caffeine",
            "Sweetness",
        )

        for index, (label, value) in enumerate(
            zip(labels, values)
        ):

            text = self.font_small.render(
                f"{label}: {value}",
                True,
                self.WHITE,
            )

            screen.blit(
                text,
                (
                    135,
                    625 + index * 19,
                ),
            )

    # ============================================================
    # CUSTOMISE
    # ============================================================

    def _draw_customise(self, screen):

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
                    425,
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
                first.y - 18,
            ),
        )

        for value, rect in buttons.items():

            active = (
                value == selected
            )

            enabled = (
                self.game_state.can_customize()
            )

            if active:

                fill = (
                    50,
                    18,
                    62,
                )

                border = self.PINK_BRIGHT

            elif enabled:

                fill = (
                    10,
                    18,
                    38,
                )

                border = self.CYAN

            else:

                fill = (
                    8,
                    11,
                    24,
                )

                border = (
                    55,
                    60,
                    80,
                )

            self._panel(
                screen,
                rect,
                border,
                fill,
            )

            text = self.font_small.render(
                value,
                True,
                self.WHITE if enabled else self.MUTED,
            )

            screen.blit(
                text,
                text.get_rect(
                    center=rect.center,
                ),
            )

    # ============================================================
    # BLENDER
    # ============================================================

    def _draw_blender(self, screen):

        self._panel(
            screen,
            self.blender_rect,
            self.PURPLE,
            self.PANEL_DARK,
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
                    425,
                )
            ),
        )

        # --------------------------------------------------------
        # JUG
        # --------------------------------------------------------

        jug = self.blender_jug_rect

        pygame.draw.rect(
            screen,
            (22, 28, 55),
            jug,
            border_radius=22,
        )

        pygame.draw.rect(
            screen,
            self.CYAN_BRIGHT,
            jug,
            width=2,
            border_radius=22,
        )

        # --------------------------------------------------------
        # LIQUID
        # --------------------------------------------------------

        drink_name = (
            self.player_drink.drink_name
        )

        if drink_name:

            recipe = get_recipe(
                drink_name
            )

            liquid_colour = (
                recipe.liquid_color
                if recipe
                else (150, 150, 255)
            )

            height = 90

            if (
                self.game_state.state
                == GameState.BLENDING
            ):

                height += int(
                    time.monotonic()
                    * 10
                ) % 10

            liquid = pygame.Rect(
                jug.x + 12,
                jug.bottom - height - 10,
                jug.width - 24,
                height,
            )

            pygame.draw.rect(
                screen,
                liquid_colour,
                liquid,
                border_radius=15,
            )

            # Swirl.

            pygame.draw.arc(
                screen,
                WHITE,
                pygame.Rect(
                    liquid.x + 25,
                    liquid.y + 15,
                    liquid.width - 50,
                    35,
                ),
                0,
                5,
                3,
            )

        else:

            text = self.font_medium.render(
                "SELECT A DRINK",
                True,
                self.MUTED,
            )

            screen.blit(
                text,
                text.get_rect(
                    center=jug.center,
                ),
            )

        # --------------------------------------------------------
        # BASE
        # --------------------------------------------------------

        base = pygame.Rect(
            jug.x - 15,
            jug.bottom - 5,
            jug.width + 30,
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

    # ============================================================
    # TOPPINGS
    # ============================================================

    def _draw_toppings(self, screen):

        # Keep toppings visually small.
        # They are NOT clickable.

        title = self.font_small.render(
            "TOPPINGS  •  AUTOMATIC  •  VISUAL ONLY",
            True,
            self.MUTED,
        )

        screen.blit(
            title,
            (
                815,
                674,
            ),
        )

    # ============================================================
    # FINAL PREVIEW
    # ============================================================

    def _draw_preview(self, screen):

        self._panel(
            screen,
            self.preview_rect,
            self.PINK,
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
                    425,
                )
            ),
        )

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
                    center=self.preview_image_rect.center
                ),
            )

        # --------------------------------------------------------
        # PLACE INTO CUP
        # --------------------------------------------------------

        self._action_button(
            screen,
            self.place_button,
            "PLACE",
            self.PINK,
            self.game_state.can_place_into_cup(),
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

            border = (
                55,
                60,
                80,
            )

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
    # IMAGE SCALING
    # ============================================================

    def _image_fit(
        self,
        screen,
        image,
        target,
        bright=True,
    ):

        width, height = image.get_size()

        if width <= 0 or height <= 0:
            return

        scale = min(
            target.width / width,
            target.height / height,
        )

        size = (
            max(1, int(width * scale)),
            max(1, int(height * scale)),
        )

        scaled = pygame.transform.smoothscale(
            image,
            size,
        )

        if not bright:

            scaled = scaled.copy()

            scaled.fill(
                (80, 80, 100, 255),
                special_flags=pygame.BLEND_RGBA_MULT,
            )

        destination = scaled.get_rect(
            center=target.center,
        )

        screen.blit(
            scaled,
            destination,
        )

    # ============================================================
    # LOCK
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
    # RESET
    # ============================================================

    def reset(self):

        self.player_drink.reset()

        self.game_state.reset()

        self.customer_order = None

        self.served = False

        self.blend_start_time = 0

        if self.drink is not None:

            try:

                self.drink.reset()

            except Exception:
                pass

        self._attach_legacy_bridge()
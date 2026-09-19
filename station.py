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
    # UNIFIED PANEL COLOUR
    # ============================================================

    # ALL normal panels now use this same colour.
    PANEL = (8, 13, 31, 235)

    # Darker colour used only inside certain button states.
    BUTTON_DARK = (7, 11, 25)

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
        # PLAYER DRINK
        # --------------------------------------------------------

        self.player_drink = PlayerDrink()

        # --------------------------------------------------------
        # MIXING STATE
        # --------------------------------------------------------

        self.game_state = MixingGameState()

        # --------------------------------------------------------
        # GAME SYSTEM REFERENCES
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
        # SERVED
        # --------------------------------------------------------

        self.served = False

        # --------------------------------------------------------
        # BLENDER
        # --------------------------------------------------------

        self.blend_start_time = 0.0

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
        # DRINK IMAGES
        # ========================================================

        self.drink_images = {}

        self._load_drink_images()

        # ========================================================
        # HUD
        # ========================================================
        #
        # NOW STARTS FROM TOP LEFT.
        #

        self.hud_rect = pygame.Rect(
            20,
            15,
            510,
            50,
        )

        # ========================================================
        # DRINK MENU
        # ========================================================
        #
        # Reduced approximately 10%.
        #
        # It is aligned to the TOP RIGHT.
        #

        self.menu_rect = pygame.Rect(
            400,
            80,
            860,
            195,
        )

        # ========================================================
        # CURRENT ORDER
        # ========================================================
        #
        # Original width = 430
        #
        # New width:
        # 430 × 0.70 = 301
        #

        self.order_rect = pygame.Rect(
            35,
            560,
            300,
            135,
        )

        # ========================================================
        # CUSTOMISATION
        # ========================================================

        self.customise_rect = pygame.Rect(
            490,
            400,
            300,
            295,
        )

        # ========================================================
        # BLENDER
        # ========================================================

        self.blender_rect = pygame.Rect(
            800,
            400,
            300,
            295,
        )

        # ========================================================
        # PREVIEW
        # ========================================================

        self.preview_rect = pygame.Rect(
            1110,
            400,
            145,
            295,
        )

        # ========================================================
        # BLENDER JUG
        # ========================================================

        self.blender_jug_rect = pygame.Rect(
            855,
            430,
            190,
            150,
        )

        # ========================================================
        # BLEND BUTTON
        # ========================================================

        self.blend_button = pygame.Rect(
            850,
            585,
            200,
            75,
        )

        # ========================================================
        # PREVIEW IMAGE
        # ========================================================

        self.preview_image_rect = pygame.Rect(
            1125,
            445,
            115,
            125,
        )

        # ========================================================
        # SERVE BUTTON
        # ========================================================
        #
        # PLACE BUTTON HAS BEEN REMOVED.
        #

        self.serve_button = pygame.Rect(
            1120,
            600,
            125,
            60,
        )

        # ========================================================
        # TOPPINGS
        # ========================================================

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
        # LEGACY BRIDGE
        # ========================================================

        self._attach_legacy_bridge()

    # ============================================================
    # LOAD DRINK IMAGES
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
                    f"[STATION] Could not load: {path}"
                )

                self.drink_images[drink_name] = None

    # ============================================================
    # MENU SLOTS
    # ============================================================

    def _create_menu_slots(self):

        self.menu_slots.clear()

        # --------------------------------------------------------
        # 10% SMALLER THAN ORIGINAL
        # --------------------------------------------------------

        left = 405
        top = 88

        width = 92
        height = 173

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

        x_positions = (
            510,
            610,
            710,
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

        try:
            level = int(level)
        except (TypeError, ValueError):
            level = 1

        self.level = max(
            1,
            level,
        )

    # ============================================================
    # PROGRESSION
    # ============================================================

    def set_progression(self, progression):

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

    def set_rewards(self, rewards):

        self.rewards = rewards

    # ============================================================
    # ECONOMY
    # ============================================================

    def set_economy(self, economy):

        self.economy = economy

    # ============================================================
    # PLAYER DRINK DATA
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
    # BLENDING
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

            # ----------------------------------------------------
            # FINISH BLENDING
            # ----------------------------------------------------

            self.game_state.finish_blending()

            self._sync_legacy_values()

            # ----------------------------------------------------
            # AUTOMATICALLY PLACE INTO CUP
            # ----------------------------------------------------
            #
            # The PLACE button has been removed.
            #
            # Therefore, once blending is finished, the drink
            # automatically moves to READY_TO_SERVE.
            #

            if self.game_state.can_place_into_cup():

                self.game_state.place_into_cup()

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

                if rect.collidepoint(mouse):

                    if self.game_state.select_temperature(
                        value
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

                if rect.collidepoint(mouse):

                    if self.game_state.select_caffeine(
                        value
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

                if rect.collidepoint(mouse):

                    if self.game_state.select_sweetness(
                        value
                    ):

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
        # SERVE
        # ========================================================

        if self.serve_button.collidepoint(mouse):

            if self.game_state.can_serve():

                if self.game_state.serve():

                    self.served = True

                    self._sync_legacy_values()

            return

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, dt=0):

        self._update_blending()

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

        # ALL NORMAL PANELS USE THE SAME PANEL STYLE.
        self._panel(
            screen,
            rect,
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

        level_text = self.font_medium.render(
            f"★ LEVEL {level}",
            True,
            self.WHITE,
        )

        screen.blit(
            level_text,
            (35, 31),
        )

        # ========================================================
        # XP
        # ========================================================

        xp_label = self.font_medium.render(
            "XP",
            True,
            self.PINK_BRIGHT,
        )

        screen.blit(
            xp_label,
            (150, 31),
        )

        # --------------------------------------------------------
        # SMALLER XP BAR
        # --------------------------------------------------------

        xp_bar = pygame.Rect(
            180,
            28,
            145,
            18,
        )

        pygame.draw.rect(
            screen,
            (18, 24, 48),
            xp_bar,
            border_radius=9,
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            xp_bar,
            width=2,
            border_radius=9,
        )

        ratio = 0.0

        if max_xp > 0:

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
                border_radius=7,
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

        credit_text = self.font_medium.render(
            f"☕ ${credits}",
            True,
            self.YELLOW,
        )

        screen.blit(
            credit_text,
            (350, 31),
        )

        # ========================================================
        # COMBO
        # ========================================================

        combo_text = self.font_medium.render(
            f"🔥 × {combo}",
            True,
            self.CYAN_BRIGHT,
        )

        screen.blit(
            combo_text,
            (435, 31),
        )

    # ============================================================
    # DRINK MENU
    # ============================================================

    def _draw_menu(self, screen):

        # Unified panel colour.
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
            # CARD
            # ----------------------------------------------------

            if selected:

                border = self.PINK_BRIGHT

            elif unlocked:

                border = self.CYAN

            else:

                border = self.LOCKED

            # Same panel fill for every card.
            fill = self.PANEL

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
                rect.y + 8,
                rect.width - 12,
                120,
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
                        rect.bottom - 20,
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
            self.CYAN,
            self.PANEL,
        )

        title = self.font_medium.render(
            "☕ CURRENT ORDER",
            True,
            self.PINK_BRIGHT,
        )

        screen.blit(
            title,
            (50, 572),
        )

        # --------------------------------------------------------
        # NO CUSTOMER
        # --------------------------------------------------------

        if self.customer_order is None:

            text = self.font_small.render(
                "WAITING FOR CUSTOMER...",
                True,
                self.MUTED,
            )

            screen.blit(
                text,
                (50, 625),
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
        # IMAGE
        # --------------------------------------------------------

        image = self.drink_images.get(
            drink_name
        )

        if image is not None:

            self._image_fit(
                screen,
                image,
                pygame.Rect(
                    50,
                    600,
                    55,
                    75,
                ),
                True,
            )

        # --------------------------------------------------------
        # DRINK NAME
        # --------------------------------------------------------

        drink_text = self.font_small.render(
            str(drink_name),
            True,
            self.PINK_BRIGHT,
        )

        screen.blit(
            drink_text,
            (115, 600),
        )

        # --------------------------------------------------------
        # VALUES
        # --------------------------------------------------------

        values = (
            temperature,
            caffeine,
            sweetness,
        )

        labels = (
            "Temp",
            "Caffeine",
            "Sweet",
        )

        for index, (
            label,
            value,
        ) in enumerate(
            zip(
                labels,
                values,
            )
        ):

            text = self.font_small.render(
                f"{label}: {value}",
                True,
                self.WHITE,
            )

            screen.blit(
                text,
                (
                    115,
                    620 + index * 18,
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
                first.y - 18,
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

            text = self.font_small.render(
                value,
                True,
                self.WHITE
                if enabled
                else self.MUTED,
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
                    425,
                )
            ),
        )

        jug = self.blender_jug_rect

        # --------------------------------------------------------
        # JUG
        # --------------------------------------------------------

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
                else (
                    150,
                    150,
                    255,
                )
            )

            height = 90

            if (
                self.game_state.state
                == GameState.BLENDING
            ):

                height += (
                    int(
                        time.monotonic() * 10
                    ) % 10
                )

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

            # ----------------------------------------------------
            # SWIRL
            # ----------------------------------------------------

            pygame.draw.arc(
                screen,
                self.WHITE,
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
            self.CYAN,
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

        title = self.font_small.render(
            "TOPPINGS • AUTOMATIC • VISUAL ONLY",
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
    # PREVIEW
    # ============================================================

    def _draw_preview(self, screen):

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
        # SERVE ONLY
        # --------------------------------------------------------
        #
        # PLACE BUTTON HAS BEEN COMPLETELY REMOVED.
        #

        self._action_button(
            screen,
            self.serve_button,
            "SERVE",
            self.CYAN,
            self.game_state.can_serve(),
        )

    # ============================================================
    # PANEL
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

        if width <= 0 or height <= 0:
            return

        scale = min(
            target.width / width,
            target.height / height,
        )

        size = (
            max(
                1,
                int(width * scale),
            ),
            max(
                1,
                int(height * scale),
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
                special_flags=pygame.BLEND_RGBA_MULT,
            )

        destination = scaled.get_rect(
            center=target.center
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

        self.blend_start_time = 0.0

        if self.drink is not None:

            try:
                self.drink.reset()
            except Exception:
                pass

        self._attach_legacy_bridge()
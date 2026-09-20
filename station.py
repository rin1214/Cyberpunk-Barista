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


# ============================================================
# CYBERPUNK CAFÉ
# MIXING STATION
# ============================================================
#
# MASTER GAME SIZE:
#       1280 x 720
#
# WORKFLOW:
#
#       SELECT DRINK
#            ↓
#       CUSTOMISE
#            ↓
#       READY TO BLEND
#            ↓
#       BLENDING
#            ↓
#       READY TO SERVE
#            ↓
#       SERVE
#
# IMPORTANT:
#
# There is NO:
#
#       PLACE INTO CUP
#
# anymore.
#
# The blender automatically becomes ready to serve
# when blending finishes.
#
# ============================================================


class MixingStation:

    # ============================================================
    # MASTER SIZE
    # ============================================================

    WIDTH = 1280
    HEIGHT = 720

    # ============================================================
    # COLOURS
    # ============================================================

    DARK = (6, 8, 20)

    PANEL = (8, 13, 31, 235)
    PANEL_DARK = (5, 8, 20, 235)
    PANEL_INNER = (10, 17, 38)

    CYAN = (70, 225, 255)
    CYAN_BRIGHT = (145, 245, 255)

    PINK = (255, 65, 190)
    PINK_BRIGHT = (255, 150, 225)

    PURPLE = (170, 90, 255)

    BLUE = (75, 165, 255)

    MINT = (100, 255, 210)

    YELLOW = (255, 210, 80)

    WHITE = (245, 248, 255)
    SOFT_WHITE = (210, 220, 240)

    MUTED = (145, 155, 185)

    LOCKED = (70, 75, 100)

    GREEN = (75, 235, 160)

    RED = (255, 90, 120)

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
        # LEGACY DRINK OBJECT
        # --------------------------------------------------------

        self.drink = drink

        # --------------------------------------------------------
        # NEW PLAYER DRINK
        # --------------------------------------------------------

        self.player_drink = PlayerDrink()

        # --------------------------------------------------------
        # GAME STATE
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
        # SERVING
        # --------------------------------------------------------

        self.served = False

        # --------------------------------------------------------
        # BLENDER
        # --------------------------------------------------------

        self.blend_start_time = 0.0

        self.blend_duration = 1.8

        self.blender_angle = 0.0

        self.blender_pulse = 0.0

        # --------------------------------------------------------
        # PROJECT DIRECTORY
        # --------------------------------------------------------

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        # --------------------------------------------------------
        # DRINK ASSETS
        # --------------------------------------------------------

        self.drink_dir = os.path.join(
            self.base_dir,
            "assets",
            "mahirah",
            "drinks",
        )

        # --------------------------------------------------------
        # FONT ASSETS
        # --------------------------------------------------------

        self.font_dir = os.path.join(
            self.base_dir,
            "assets",
            "fonts",
        )

        # --------------------------------------------------------
        # FONTS
        # --------------------------------------------------------

        self._create_fonts()

        # --------------------------------------------------------
        # DRINK IMAGES
        # --------------------------------------------------------

        self.drink_images = {}

        self._load_drink_images()

        # --------------------------------------------------------
        # LAYOUT
        # --------------------------------------------------------

        self._create_layout()

        # --------------------------------------------------------
        # LEGACY CONNECTION
        # --------------------------------------------------------

        self._attach_legacy_bridge()

    # ============================================================
    # FONT SEARCH
    # ============================================================

    def _find_cyberpunk_font(self):

        preferred_names = [
            "Audiowide-Regular.ttf",
            "Audiowide.ttf",
            "audiowide.ttf",
            "Audiowide-Regular.otf",
            "Orbitron.ttf",
            "Rajdhani.ttf",
            "Oxanium.ttf",
        ]

        # --------------------------------------------------------
        # EXACT FILE SEARCH
        # --------------------------------------------------------

        for filename in preferred_names:

            path = os.path.join(
                self.font_dir,
                filename,
            )

            if os.path.isfile(path):

                return path

        # --------------------------------------------------------
        # SEARCH FONT DIRECTORY
        # --------------------------------------------------------

        if os.path.isdir(self.font_dir):

            candidates = []

            preferred_words = [
                "audiowide",
                "orbitron",
                "rajdhani",
                "oxanium",
                "neuropol",
                "ethnocentric",
                "agency",
                "cyber",
                "tech",
            ]

            for root, _, files in os.walk(
                self.font_dir
            ):

                for filename in files:

                    lower = filename.lower()

                    if not lower.endswith(
                        (
                            ".ttf",
                            ".otf",
                        )
                    ):

                        continue

                    score = 100

                    for index, word in enumerate(
                        preferred_words
                    ):

                        if word in lower:

                            score = index

                            break

                    candidates.append(
                        (
                            score,
                            os.path.join(
                                root,
                                filename,
                            ),
                        )
                    )

            if candidates:

                candidates.sort(
                    key=lambda item: item[0]
                )

                return candidates[0][1]

        # --------------------------------------------------------
        # INSTALLED FONT
        # --------------------------------------------------------

        try:

            installed = pygame.font.match_font(
                "audiowide"
            )

            if installed:

                return installed

        except Exception:

            pass

        return None

    # ============================================================
    # READABLE FONT
    # ============================================================

    def _find_readable_font(self):

        font_names = [
            "Bahnschrift",
            "Segoe UI",
            "Trebuchet MS",
            "Verdana",
            "Arial",
        ]

        for name in font_names:

            try:

                path = pygame.font.match_font(
                    name
                )

                if path:

                    return path

            except Exception:

                pass

        return None

    # ============================================================
    # CREATE FONT
    # ============================================================

    def _make_font(
        self,
        size,
        cyber=False,
        bold=False,
    ):

        font_path = None

        if cyber:

            font_path = (
                self._find_cyberpunk_font()
            )

        else:

            font_path = (
                self._find_readable_font()
            )

        if font_path:

            try:

                font = pygame.font.Font(
                    font_path,
                    size,
                )

                font.set_bold(
                    bold
                )

                return font

            except pygame.error:

                pass

        # --------------------------------------------------------
        # SAFE FALLBACK
        # --------------------------------------------------------

        try:

            return pygame.font.SysFont(
                "Arial",
                size,
                bold=bold,
            )

        except pygame.error:

            return pygame.font.Font(
                None,
                size,
            )

    # ============================================================
    # CREATE ALL FONTS
    # ============================================================

    def _create_fonts(self):

        pygame.font.init()

        # --------------------------------------------------------
        # FUTURISTIC TITLES
        # --------------------------------------------------------

        self.font_title = self._make_font(
            21,
            cyber=True,
            bold=True,
        )

        self.font_panel_title = self._make_font(
            20,
            cyber=True,
            bold=True,
        )

        # --------------------------------------------------------
        # BUTTONS
        # --------------------------------------------------------

        self.font_button = self._make_font(
            16,
            cyber=False,
            bold=True,
        )

        self.font_button_large = self._make_font(
            25,
            cyber=True,
            bold=True,
        )

        # --------------------------------------------------------
        # SMALL TEXT
        # --------------------------------------------------------

        self.font_small = self._make_font(
            12,
            cyber=False,
            bold=True,
        )

        self.font_label = self._make_font(
            13,
            cyber=True,
            bold=True,
        )

        self.font_medium = self._make_font(
            16,
            cyber=False,
            bold=True,
        )

        self.font_large = self._make_font(
            24,
            cyber=True,
            bold=True,
        )

        self.font_xlarge = self._make_font(
            31,
            cyber=True,
            bold=True,
        )

    # ============================================================
    # LAYOUT
    # ============================================================

    def _create_layout(self):

        # ========================================================
        # TOP HUD
        # ========================================================

        self.hud_rect = pygame.Rect(
            20,
            15,
            525,
            43,
        )

        # ========================================================
        # DRINK MENU
        # ========================================================

        self.menu_rect = pygame.Rect(
            435,
            83,
            825,
            188,
        )

        self.menu_slots = []

        slot_width = 86
        slot_height = 166
        gap = 5

        start_x = 445
        start_y = 94

        for index, drink_name in enumerate(
            DRINK_MENU
        ):

            x = (
                start_x
                + index
                * (
                    slot_width
                    + gap
                )
            )

            rect = pygame.Rect(
                x,
                start_y,
                slot_width,
                slot_height,
            )

            self.menu_slots.append(
                (
                    drink_name,
                    rect,
                )
            )

        # ========================================================
        # CUSTOMISE PANEL
        # ========================================================

        # About 5% wider than the previous version.

        self.customise_rect = pygame.Rect(
            445,
            410,
            320,
            295,
        )

        # ========================================================
        # BLENDER PANEL
        # ========================================================

        self.blender_rect = pygame.Rect(
            780,
            410,
            310,
            295,
        )

        # ========================================================
        # PREVIEW PANEL
        # ========================================================

        self.preview_rect = pygame.Rect(
            1105,
            410,
            155,
            295,
        )

        # ========================================================
        # CUSTOMISATION BUTTONS
        # ========================================================

        button_width = 86
        button_height = 45
        button_gap = 10

        button_x = (
            self.customise_rect.x
            + 20
        )

        row_1_y = 460
        row_2_y = 518
        row_3_y = 576

        # --------------------------------------------------------
        # TEMPERATURE
        # --------------------------------------------------------

        self.temperature_buttons = {}

        for index, value in enumerate(
            TEMPERATURE_OPTIONS
        ):

            x = (
                button_x
                + index
                * (
                    button_width
                    + button_gap
                )
            )

            self.temperature_buttons[
                value
            ] = pygame.Rect(
                x,
                row_1_y,
                button_width,
                button_height,
            )

        # --------------------------------------------------------
        # CAFFEINE
        # --------------------------------------------------------

        self.caffeine_buttons = {}

        for index, value in enumerate(
            CAFFEINE_OPTIONS
        ):

            x = (
                button_x
                + index
                * (
                    button_width
                    + button_gap
                )
            )

            self.caffeine_buttons[
                value
            ] = pygame.Rect(
                x,
                row_2_y,
                button_width,
                button_height,
            )

        # --------------------------------------------------------
        # SWEETNESS
        # --------------------------------------------------------

        self.sweetness_buttons = {}

        for index, value in enumerate(
            SWEETNESS_OPTIONS
        ):

            x = (
                button_x
                + index
                * (
                    button_width
                    + button_gap
                )
            )

            self.sweetness_buttons[
                value
            ] = pygame.Rect(
                x,
                row_3_y,
                button_width,
                button_height,
            )

        # ========================================================
        # TALL BLENDER
        # ========================================================

        self.blender_jug_rect = pygame.Rect(
            845,
            450,
            180,
            155,
        )

        # --------------------------------------------------------
        # LOWER BLEND BUTTON
        # --------------------------------------------------------

        self.blend_button = pygame.Rect(
            825,
            625,
            220,
            60,
        )

        # ========================================================
        # PREVIEW IMAGE
        # ========================================================

        self.preview_image_rect = pygame.Rect(
            1118,
            455,
            129,
            145,
        )

        # ========================================================
        # SERVE BUTTON
        # ========================================================

        self.serve_button = pygame.Rect(
            1120,
            625,
            125,
            60,
        )

    # ============================================================
    # LOAD DRINK IMAGES
    # ============================================================

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

    # ============================================================
    # LEVEL
    # ============================================================

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
    # CUSTOMER ORDER
    # ============================================================
    #
    # INTERNAL NAME:
    #
    #     set_order()
    #
    # ============================================================

    def set_order(
        self,
        order,
    ):

        self.customer_order = order

        self.game_state.set_order(
            order
        )

        self.player_drink.reset()

        self.served = False

        self._sync_legacy_values()

    # ============================================================
    # CUSTOMER ORDER COMPATIBILITY
    # ============================================================
    #
    # IMPORTANT:
    #
    # Your main.py calls:
    #
    #     mixing_station.set_customer_order(order)
    #
    # So this method MUST exist.
    #
    # It simply forwards the order to set_order().
    #
    # ============================================================

    def set_customer_order(
        self,
        order,
    ):

        self.set_order(
            order
        )

    # ============================================================
    # LEGACY BRIDGE
    # ============================================================

    def _attach_legacy_bridge(self):

        if self.drink is None:

            return

        try:

            self.drink.get_data = (
                self.get_player_drink_data
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
    # UPDATE
    # ============================================================
    #
    # IMPORTANT:
    #
    # main.py calls:
    #
    #     mixing_station.update(dt)
    #
    # Therefore dt is accepted here.
    #
    # The current blender animation uses monotonic time,
    # so dt does not need to be used directly yet.
    #
    # ============================================================

    def update(
        self,
        dt=0.0,
    ):

        self._update_blending()

    # ============================================================
    # BLENDER UPDATE
    # ============================================================

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

        # --------------------------------------------------------
        # ROTATING BLADES
        # --------------------------------------------------------

        self.blender_angle = (
            elapsed
            * 720
        ) % 360

        # --------------------------------------------------------
        # PULSE
        # --------------------------------------------------------

        self.blender_pulse = (
            math.sin(
                elapsed * 10
            )
            * 0.5
            + 0.5
        )

        # --------------------------------------------------------
        # FINISH BLENDING
        # --------------------------------------------------------

        if elapsed >= self.blend_duration:

            self.game_state.finish_blending()

            self._sync_legacy_values()

    # ============================================================
    # HANDLE EVENTS
    # ============================================================

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

        # ========================================================
        # DRINK MENU
        # ========================================================

        for (
            drink_name,
            rect,
        ) in self.menu_slots:

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
            # WAITING FOR ORDER
            # ----------------------------------------------------

            if (
                self.game_state.state
                == GameState.WAITING_FOR_ORDER
            ):

                self.game_state.state = (
                    GameState.SELECT_DRINK
                )

            # ----------------------------------------------------
            # SELECT DRINK
            # ----------------------------------------------------

            if (
                self.game_state.state
                == GameState.SELECT_DRINK
            ):

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

            for (
                value,
                rect,
            ) in self.temperature_buttons.items():

                if rect.collidepoint(
                    mouse
                ):

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

            for (
                value,
                rect,
            ) in self.caffeine_buttons.items():

                if rect.collidepoint(
                    mouse
                ):

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

            for (
                value,
                rect,
            ) in self.sweetness_buttons.items():

                if rect.collidepoint(
                    mouse
                ):

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

        if self.blend_button.collidepoint(
            mouse
        ):

            if self.game_state.start_blending():

                self.blend_start_time = (
                    time.monotonic()
                )

                self.blender_angle = 0

            return

        # ========================================================
        # SERVE
        # ========================================================

        if self.serve_button.collidepoint(
            mouse
        ):

            if self.game_state.serve():

                self.served = True

                self._sync_legacy_values()

            return

    # ============================================================
    # PLAYER DRINK DATA
    # ============================================================

    def get_player_drink_data(self):

        return (
            self.game_state
            .get_player_drink_data()
        )

    # ============================================================
    # LEGACY get_data()
    # ============================================================

    def get_data(self):

        return self.get_player_drink_data()

    # ============================================================
    # DRAW
    # ============================================================

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

    # ============================================================
    # HUD
    # ============================================================

    def _draw_hud(
        self,
        screen,
    ):

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

            max_xp = getattr(
                self.progression,
                "xp_required",
                max_xp,
            )

            if callable(
                max_xp
            ):

                try:

                    max_xp = max_xp()

                except Exception:

                    max_xp = 100

        # --------------------------------------------------------
        # ECONOMY
        # --------------------------------------------------------

        if self.economy is not None:

            credits = getattr(
                self.economy,
                "credits",
                credits,
            )

            if hasattr(
                self.economy,
                "get_credits",
            ):

                try:

                    credits = (
                        self.economy
                        .get_credits()
                    )

                except Exception:

                    pass

        # --------------------------------------------------------
        # REWARDS
        # --------------------------------------------------------

        if self.rewards is not None:

            combo = getattr(
                self.rewards,
                "combo",
                combo,
            )

        # --------------------------------------------------------
        # LEVEL
        # --------------------------------------------------------

        level_text = (
            self.font_button.render(
                f"LEVEL {level}",
                True,
                self.WHITE,
            )
        )

        screen.blit(
            level_text,
            (35, 28),
        )

        # --------------------------------------------------------
        # XP LABEL
        # --------------------------------------------------------

        xp_label = (
            self.font_small.render(
                "XP",
                True,
                self.PINK_BRIGHT,
            )
        )

        screen.blit(
            xp_label,
            (115, 31),
        )

        # --------------------------------------------------------
        # XP BAR
        # --------------------------------------------------------

        xp_bar = pygame.Rect(
            140,
            27,
            105,
            18,
        )

        pygame.draw.rect(
            screen,
            (
                18,
                24,
                48,
            ),
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

        ratio = 0

        try:

            if max_xp > 0:

                ratio = max(
                    0,
                    min(
                        1,
                        xp / max_xp,
                    ),
                )

        except (
            TypeError,
            ZeroDivisionError,
        ):

            ratio = 0

        fill_width = int(
            (
                xp_bar.width
                - 6
            )
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

        xp_number = (
            self.font_small.render(
                f"{xp}/{max_xp}",
                True,
                self.WHITE,
            )
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

        credit_text = (
            self.font_button.render(
                f"CREDITS  ${credits}",
                True,
                self.YELLOW,
            )
        )

        screen.blit(
            credit_text,
            (270, 28),
        )

        # --------------------------------------------------------
        # COMBO
        # --------------------------------------------------------

        combo_text = (
            self.font_button.render(
                f"COMBO x{combo}",
                True,
                self.CYAN_BRIGHT,
            )
        )

        screen.blit(
            combo_text,
            (405, 28),
        )

    # ============================================================
    # DRINK MENU
    # ============================================================

    def _draw_menu(
        self,
        screen,
    ):

        self._panel(
            screen,
            self.menu_rect,
            self.CYAN,
            self.PANEL_DARK,
        )

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

            # ----------------------------------------------------
            # SLOT COLOURS
            # ----------------------------------------------------

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
            # SELECTED GLOW
            # ----------------------------------------------------

            if selected:

                glow_rect = pygame.Rect(
                    rect.x - 3,
                    rect.y - 3,
                    rect.width + 6,
                    rect.height + 6,
                )

                pygame.draw.rect(
                    screen,
                    (
                        255,
                        110,
                        220,
                    ),
                    glow_rect,
                    width=2,
                    border_radius=16,
                )

            # ----------------------------------------------------
            # IMAGE
            # ----------------------------------------------------

            image = self.drink_images.get(
                drink_name
            )

            image_area = pygame.Rect(
                rect.x + 7,
                rect.y + 9,
                rect.width - 14,
                132,
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
                    rect.y + 72,
                )

            # ----------------------------------------------------
            # DRINK NAME
            # ----------------------------------------------------

            name_colour = (
                self.WHITE
                if unlocked
                else self.LOCKED
            )

            name_font = self.font_small

            if len(
                drink_name
            ) > 13:

                name_font = self._make_font(
                    10,
                    cyber=False,
                    bold=True,
                )

            name = name_font.render(
                drink_name.upper(),
                True,
                name_colour,
            )

            screen.blit(
                name,
                name.get_rect(
                    center=(
                        rect.centerx,
                        rect.bottom - 18,
                    ),
                ),
            )

    # ============================================================
    # CUSTOMISE PANEL
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

        # --------------------------------------------------------
        # TITLE
        # --------------------------------------------------------

        self._draw_fancy_title(
            screen,
            "CUSTOMISE YOUR DRINK",
            self.customise_rect.centerx,
            430,
            self.CYAN_BRIGHT,
        )

        # --------------------------------------------------------
        # TEMPERATURE
        # --------------------------------------------------------

        self._draw_option_row(
            screen,
            "TEMPERATURE",
            self.temperature_buttons,
            self.player_drink.temperature,
        )

        # --------------------------------------------------------
        # CAFFEINE
        # --------------------------------------------------------

        self._draw_option_row(
            screen,
            "CAFFEINE LEVEL",
            self.caffeine_buttons,
            self.player_drink.caffeine,
        )

        # --------------------------------------------------------
        # SWEETNESS
        # --------------------------------------------------------

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

        label_surface = (
            self.font_label.render(
                label,
                True,
                self.CYAN,
            )
        )

        screen.blit(
            label_surface,
            (
                first.x,
                first.y - 18,
            ),
        )

        for (
            value,
            rect,
        ) in buttons.items():

            active = (
                value
                == selected
            )

            enabled = (
                self.game_state
                .can_customize()
            )

            # ----------------------------------------------------
            # ACTIVE
            # ----------------------------------------------------

            if active:

                fill = (
                    58,
                    18,
                    68,
                )

                border = (
                    self.PINK_BRIGHT
                )

                text_colour = (
                    self.WHITE
                )

            # ----------------------------------------------------
            # NORMAL
            # ----------------------------------------------------

            elif enabled:

                fill = (
                    10,
                    18,
                    38,
                )

                border = (
                    self.CYAN
                )

                text_colour = (
                    self.WHITE
                )

            # ----------------------------------------------------
            # DISABLED
            # ----------------------------------------------------

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

                text_colour = (
                    self.MUTED
                )

            self._panel(
                screen,
                rect,
                border,
                fill,
            )

            # ----------------------------------------------------
            # ACTIVE DOT
            # ----------------------------------------------------

            if active:

                pygame.draw.circle(
                    screen,
                    self.PINK_BRIGHT,
                    (
                        rect.x + 10,
                        rect.y + 10,
                    ),
                    3,
                )

            # ----------------------------------------------------
            # TEXT
            # ----------------------------------------------------

            text = (
                self.font_button.render(
                    value.upper(),
                    True,
                    text_colour,
                )
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

    def _draw_blender(
        self,
        screen,
    ):

        self._panel(
            screen,
            self.blender_rect,
            self.PURPLE,
            self.PANEL_DARK,
        )

        # --------------------------------------------------------
        # TITLE
        # --------------------------------------------------------

        self._draw_fancy_title(
            screen,
            "BLENDER",
            self.blender_rect.centerx,
            430,
            self.CYAN_BRIGHT,
        )

        # --------------------------------------------------------
        # JUG
        # --------------------------------------------------------

        jug = self.blender_jug_rect.copy()

        is_blending = (
            self.game_state.state
            == GameState.BLENDING
        )

        # --------------------------------------------------------
        # JUG SHAKE
        # --------------------------------------------------------

        if is_blending:

            shake_x = int(
                math.sin(
                    time.monotonic()
                    * 30
                )
                * 2
            )

            shake_y = int(
                math.cos(
                    time.monotonic()
                    * 25
                )
                * 1
            )

            jug.x += shake_x
            jug.y += shake_y

        # --------------------------------------------------------
        # GLOW
        # --------------------------------------------------------

        if is_blending:

            glow_alpha = int(
                45
                + self.blender_pulse
                * 45
            )

            glow_surface = (
                pygame.Surface(
                    (
                        jug.width + 30,
                        jug.height + 30,
                    ),
                    pygame.SRCALPHA,
                )
            )

            pygame.draw.rect(
                glow_surface,
                (
                    70,
                    225,
                    255,
                    glow_alpha,
                ),
                glow_surface.get_rect(),
                border_radius=30,
                width=4,
            )

            screen.blit(
                glow_surface,
                (
                    jug.x - 15,
                    jug.y - 15,
                ),
            )

        # --------------------------------------------------------
        # JUG BODY
        # --------------------------------------------------------

        pygame.draw.rect(
            screen,
            (
                18,
                25,
                52,
            ),
            jug,
            border_radius=23,
        )

        pygame.draw.rect(
            screen,
            self.CYAN_BRIGHT,
            jug,
            width=3,
            border_radius=23,
        )

        # --------------------------------------------------------
        # INNER JUG
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # HANDLE
        # --------------------------------------------------------

        handle = pygame.Rect(
            jug.right - 2,
            jug.y + 35,
            28,
            65,
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

        # --------------------------------------------------------
        # SELECTED DRINK
        # --------------------------------------------------------

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

            # ----------------------------------------------------
            # HOLOGRAM FRAPPE
            # ----------------------------------------------------

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

            # ----------------------------------------------------
            # LIQUID HEIGHT
            # ----------------------------------------------------

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

            # ----------------------------------------------------
            # HIGHLIGHT
            # ----------------------------------------------------

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
                7,
            )

            pygame.draw.rect(
                screen,
                highlight_colour,
                highlight,
                border_radius=4,
            )

            # ----------------------------------------------------
            # WAVES
            # ----------------------------------------------------

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

                if len(points) >= 2:

                    pygame.draw.lines(
                        screen,
                        self.WHITE,
                        False,
                        points,
                        3,
                    )

            # ----------------------------------------------------
            # BUBBLES
            # ----------------------------------------------------

            if is_blending:

                current_time = (
                    time.monotonic()
                )

                for index in range(7):

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
                            (
                                phase
                                * 32
                            )
                            % max(
                                20,
                                liquid.height
                                - 20,
                            )
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

            # ----------------------------------------------------
            # NO DRINK
            # ----------------------------------------------------

            text = (
                self.font_small.render(
                    "SELECT A DRINK",
                    True,
                    self.MUTED,
                )
            )

            screen.blit(
                text,
                text.get_rect(
                    center=inner.center
                ),
            )

        # --------------------------------------------------------
        # BLENDER CORE
        # --------------------------------------------------------

        core_x = jug.centerx

        core_y = (
            jug.bottom - 25
        )

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
            14,
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

        # --------------------------------------------------------
        # ROTATING BLADES
        # --------------------------------------------------------

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
                    self.CYAN_BRIGHT,
                    (
                        core_x,
                        core_y,
                    ),
                    (
                        int(end_x),
                        int(end_y),
                    ),
                    4,
                )

        # --------------------------------------------------------
        # BLENDER BASE
        # --------------------------------------------------------

        base = pygame.Rect(
            jug.x - 12,
            jug.bottom - 2,
            jug.width + 24,
            27,
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
            width=2,
            border_radius=10,
        )

        # ========================================================
        # BLEND PROGRESS BAR
        # ========================================================

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
                self.blend_button.y - 9,
                self.blend_button.width - 16,
                5,
            )

            pygame.draw.rect(
                screen,
                (
                    20,
                    25,
                    45,
                ),
                progress_rect,
                border_radius=3,
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
                border_radius=3,
            )

        # ========================================================
        # BLEND BUTTON
        # ========================================================

        blend_enabled = (
            self.game_state.can_blend()
        )

        blend_text = (
            "BLENDING..."
            if is_blending
            else "BLEND"
        )

        self._action_button(
            screen,
            self.blend_button,
            blend_text,
            self.PINK,
            blend_enabled,
            large=True,
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
            self.PINK,
            self.PANEL,
        )

        # --------------------------------------------------------
        # TITLE
        # --------------------------------------------------------

        self._draw_fancy_title(
            screen,
            "PREVIEW",
            self.preview_rect.centerx,
            430,
            self.PINK_BRIGHT,
            small=True,
        )

        # --------------------------------------------------------
        # DRINK IMAGE
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

            text = (
                self.font_small.render(
                    "NO DRINK",
                    True,
                    self.MUTED,
                )
            )

            screen.blit(
                text,
                text.get_rect(
                    center=(
                        self.preview_image_rect.center
                    ),
                ),
            )

        # --------------------------------------------------------
        # READY INDICATOR
        # --------------------------------------------------------

        ready = (
            self.game_state.state
            == GameState.READY_TO_SERVE
        )

        if ready:

            ready_text = (
                self.font_small.render(
                    "READY!",
                    True,
                    self.GREEN,
                )
            )

            screen.blit(
                ready_text,
                ready_text.get_rect(
                    center=(
                        self.preview_rect.centerx,
                        600,
                    ),
                ),
            )

        # --------------------------------------------------------
        # SERVE BUTTON
        # --------------------------------------------------------

        self._action_button(
            screen,
            self.serve_button,
            "SERVE",
            self.CYAN,
            self.game_state.can_serve(),
            large=False,
        )

    # ============================================================
    # FANCY TITLE
    # ============================================================

    def _draw_fancy_title(
        self,
        screen,
        text,
        center_x,
        y,
        colour,
        small=False,
    ):

        font = (
            self.font_button
            if small
            else self.font_panel_title
        )

        label = font.render(
            text,
            True,
            colour,
        )

        # --------------------------------------------------------
        # LEFT DIAMOND
        # --------------------------------------------------------

        left_x = (
            center_x
            - label.get_width() // 2
            - 13
        )

        pygame.draw.polygon(
            screen,
            colour,
            [
                (
                    left_x,
                    y - 4,
                ),
                (
                    left_x + 4,
                    y,
                ),
                (
                    left_x,
                    y + 4,
                ),
                (
                    left_x - 4,
                    y,
                ),
            ],
        )

        # --------------------------------------------------------
        # RIGHT DIAMOND
        # --------------------------------------------------------

        right_x = (
            center_x
            + label.get_width() // 2
            + 13
        )

        pygame.draw.polygon(
            screen,
            colour,
            [
                (
                    right_x,
                    y - 4,
                ),
                (
                    right_x + 4,
                    y,
                ),
                (
                    right_x,
                    y + 4,
                ),
                (
                    right_x - 4,
                    y,
                ),
            ],
        )

        screen.blit(
            label,
            label.get_rect(
                center=(
                    center_x,
                    y,
                ),
            ),
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
        large=False,
    ):

        mouse = pygame.mouse.get_pos()

        hover = (
            enabled
            and rect.collidepoint(
                mouse
            )
        )

        # --------------------------------------------------------
        # ENABLED
        # --------------------------------------------------------

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

            text_colour = (
                self.WHITE
            )

        # --------------------------------------------------------
        # DISABLED
        # --------------------------------------------------------

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

            text_colour = (
                self.MUTED
            )

        # --------------------------------------------------------
        # HOVER GLOW
        # --------------------------------------------------------

        if hover:

            glow = pygame.Rect(
                rect.x - 3,
                rect.y - 3,
                rect.width + 6,
                rect.height + 6,
            )

            pygame.draw.rect(
                screen,
                (
                    255,
                    100,
                    210,
                ),
                glow,
                width=2,
                border_radius=15,
            )

        # --------------------------------------------------------
        # DRAW BUTTON
        # --------------------------------------------------------

        self._panel(
            screen,
            rect,
            border,
            fill,
        )

        font = (
            self.font_button_large
            if large
            else self.font_button
        )

        label = font.render(
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

        scaled = (
            pygame.transform.smoothscale(
                image,
                size,
            )
        )

        # --------------------------------------------------------
        # DIM LOCKED DRINK
        # --------------------------------------------------------

        if not bright:

            scaled = scaled.copy()

            scaled.fill(
                (
                    75,
                    75,
                    95,
                    255,
                ),
                special_flags=(
                    pygame.BLEND_RGBA_MULT
                ),
            )

        destination = (
            scaled.get_rect(
                center=target.center
            )
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

        # --------------------------------------------------------
        # BODY
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # SHACKLE
        # --------------------------------------------------------

        pygame.draw.arc(
            screen,
            self.LOCKED,
            pygame.Rect(
                x - 7,
                y - 13,
                14,
                18,
            ),
            math.pi,
            2 * math.pi,
            3,
        )

        # --------------------------------------------------------
        # KEYHOLE
        # --------------------------------------------------------

        pygame.draw.circle(
            screen,
            (
                25,
                28,
                45,
            ),
            (
                x,
                y + 8,
            ),
            2,
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

        self.blender_angle = 0.0

        self.blender_pulse = 0.0

        self._sync_legacy_values()
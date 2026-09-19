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
    """
    CYBERPUNK CAFÉ - MIXING STATION

    Final game resolution:
        1280 x 720

    This class controls:

        - 9-drink menu
        - locked/unlocked drinks
        - customer order display
        - temperature selection
        - caffeine selection
        - sweetness selection
        - blender
        - blending animation
        - visual toppings
        - final drink preview
        - place into cup
        - serve

    IMPORTANT:

    The customer itself is NOT drawn here.

    The customer system from customer.py remains responsible
    for drawing the actual customer.

    This station only provides the order panel underneath
    the customer.

    Existing main.py compatibility is preserved through:

        MixingStation(drink)
        handle_event(event)
        draw(screen)
        reset()
        served
    """

    WIDTH = 1280
    HEIGHT = 720

    # ============================================================
    # CYBERPUNK CAFÉ COLOUR PALETTE
    # ============================================================

    BG_PANEL = (8, 12, 28, 225)
    BG_PANEL_LIGHT = (15, 20, 42, 235)
    BG_PANEL_DARK = (5, 8, 20, 235)

    CYAN = (72, 232, 255)
    CYAN_BRIGHT = (135, 245, 255)

    PINK = (255, 72, 190)
    PINK_BRIGHT = (255, 150, 225)

    PURPLE = (170, 100, 255)
    BLUE = (80, 170, 255)

    MINT = (105, 255, 210)
    YELLOW = (255, 205, 90)

    WHITE = (245, 248, 255)
    MUTED = (145, 155, 185)

    LOCKED = (75, 80, 105)
    DARK = (6, 8, 18)

    GREEN = (75, 235, 160)
    RED = (255, 95, 125)

    # ============================================================
    # INITIALISE
    # ============================================================

    def __init__(
        self,
        drink,
        level=1,
        progression=None,
        rewards=None
    ):

        # --------------------------------------------------------
        # OLD DRINK OBJECT
        # --------------------------------------------------------

        # main.py currently passes the old Drink object.
        #
        # We keep it temporarily so the rest of the game can
        # continue working while the new station is integrated.

        self.drink = drink

        # --------------------------------------------------------
        # NEW PLAYER DRINK
        # --------------------------------------------------------

        self.player_drink = PlayerDrink()

        # --------------------------------------------------------
        # NEW GAME STATE
        # --------------------------------------------------------

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

        # This will later receive the real CustomerOrder
        # from customer.py/main.py.

        self.customer_order = None

        self.order_message = "WAITING FOR CUSTOMER"

        # --------------------------------------------------------
        # SERVE STATUS
        # --------------------------------------------------------

        # main.py already uses this.
        self.served = False

        # --------------------------------------------------------
        # BLENDING
        # --------------------------------------------------------

        self.blend_start_time = 0.0

        self.blend_duration = 1.2

        # ========================================================
        # FONTS
        # ========================================================

        self.font_hud = pygame.font.SysFont(
            "arial",
            20,
            bold=True
        )

        self.font_small = pygame.font.SysFont(
            "arial",
            13,
            bold=True
        )

        self.font_tiny = pygame.font.SysFont(
            "arial",
            11,
            bold=True
        )

        self.font_menu = pygame.font.SysFont(
            "arial",
            14,
            bold=True
        )

        self.font_panel = pygame.font.SysFont(
            "arial",
            18,
            bold=True
        )

        self.font_large = pygame.font.SysFont(
            "arial",
            27,
            bold=True
        )

        self.font_xlarge = pygame.font.SysFont(
            "arial",
            34,
            bold=True
        )

        # ========================================================
        # ASSET PATH
        # ========================================================

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.drink_asset_dir = os.path.join(
            self.base_dir,
            "assets",
            "mahirah",
            "drinks"
        )

        # ========================================================
        # LOAD DRINK IMAGES
        # ========================================================

        self.drink_images = {}

        self._load_drink_images()

        # ========================================================
        # UI LAYOUT
        # ========================================================
        #
        # Everything below uses 1280 x 720 coordinates.
        #
        # The background is NOT drawn here.
        #
        # This means your collaborators can use any café/location
        # background behind this station.
        # ========================================================

        # --------------------------------------------------------
        # TOP HUD
        # --------------------------------------------------------

        self.hud_rect = pygame.Rect(
            18,
            10,
            1244,
            43
        )

        # --------------------------------------------------------
        # 9-DRINK MENU
        # --------------------------------------------------------

        self.menu_rect = pygame.Rect(
            18,
            60,
            1244,
            125
        )

        # --------------------------------------------------------
        # CUSTOMER AREA
        # --------------------------------------------------------
        #
        # IMPORTANT:
        # No large UI box is drawn here.
        #
        # customer.py/main.py draw the actual customer here.
        #

        self.customer_area = pygame.Rect(
            18,
            198,
            300,
            248
        )

        # --------------------------------------------------------
        # CUSTOMER ORDER
        # --------------------------------------------------------
        #
        # Wide rectangle on the counter beneath customer.
        #

        self.order_rect = pygame.Rect(
            18,
            452,
            300,
            180
        )

        # --------------------------------------------------------
        # CUSTOMISATION
        # --------------------------------------------------------

        self.customise_rect = pygame.Rect(
            330,
            198,
            280,
            265
        )

        # --------------------------------------------------------
        # BLENDER
        # --------------------------------------------------------

        self.blender_rect = pygame.Rect(
            620,
            198,
            280,
            305
        )

        self.blender_jug_rect = pygame.Rect(
            665,
            215,
            190,
            180
        )

        # BLEND BUTTON IS DIRECTLY UNDER BLENDER
        self.blend_button = pygame.Rect(
            670,
            400,
            180,
            72
        )

        # --------------------------------------------------------
        # TOPPINGS
        # --------------------------------------------------------

        self.toppings_rect = pygame.Rect(
            620,
            512,
            280,
            186
        )

        # --------------------------------------------------------
        # FINAL PREVIEW
        # --------------------------------------------------------

        self.preview_rect = pygame.Rect(
            906,
            198,
            356,
            500
        )

        self.preview_image_rect = pygame.Rect(
            930,
            235,
            308,
            230
        )

        # --------------------------------------------------------
        # PLACE INTO CUP
        # --------------------------------------------------------

        self.place_button = pygame.Rect(
            930,
            482,
            308,
            72
        )

        # --------------------------------------------------------
        # SERVE
        # --------------------------------------------------------

        self.serve_button = pygame.Rect(
            930,
            570,
            308,
            86
        )

        # ========================================================
        # MENU BUTTONS
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
        # TOPPING DISPLAY
        # ========================================================
        #
        # These are VISUAL ONLY.
        # Players cannot click them.
        #

        self.topping_names = (

            (
                "whipped_cream",
                "WHIPPED CREAM"
            ),

            (
                "mint_leaves",
                "MINT"
            ),

            (
                "chocolate_bits",
                "CHOCOLATE"
            ),

            (
                "caramel_crunch",
                "CARAMEL"
            ),

            (
                "yellow_stardust",
                "STARDUST"
            ),

            (
                "meteorite_crumbs",
                "METEORITE"
            ),
        )

        # ========================================================
        # COMPATIBILITY BRIDGE
        # ========================================================

        self._attach_legacy_data_bridge()

    # ============================================================
    # LOAD DRINK IMAGES
    # ============================================================

    def _load_drink_images(self):

        """
        Load the nine existing drink PNG files.

        Expected folder:

            assets/mahirah/drinks/
        """

        filename_map = {

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

        for drink_name, filename in filename_map.items():

            path = os.path.join(
                self.drink_asset_dir,
                filename
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
                FileNotFoundError
            ):

                # The game will still run if an image
                # has not been found yet.

                self.drink_images[
                    drink_name
                ] = None

    # ============================================================
    # CREATE MENU SLOTS
    # ============================================================

    def _create_menu_slots(self):

        """
        Create all nine drink slots.

        All nine remain visible.

        Locked drinks are simply dimmed.
        """

        margin = 28

        gap = 8

        width = 124

        height = 108

        y = 69

        for index, drink_name in enumerate(
            DRINK_MENU
        ):

            x = (
                margin
                + index * (
                    width + gap
                )
            )

            rect = pygame.Rect(
                x,
                y,
                width,
                height
            )

            self.menu_slots.append(
                (
                    drink_name,
                    rect
                )
            )

    # ============================================================
    # CREATE CUSTOMISATION BUTTONS
    # ============================================================

    def _create_option_buttons(self):

        # --------------------------------------------------------
        # TEMPERATURE
        # --------------------------------------------------------

        for index, value in enumerate(
            TEMPERATURE_OPTIONS
        ):

            rect = pygame.Rect(
                325 + index * 88,
                270,
                78,
                48
            )

            self.temperature_buttons[
                value
            ] = rect

        # --------------------------------------------------------
        # CAFFEINE
        # --------------------------------------------------------

        for index, value in enumerate(
            CAFFEINE_OPTIONS
        ):

            rect = pygame.Rect(
                325 + index * 88,
                340,
                78,
                48
            )

            self.caffeine_buttons[
                value
            ] = rect

        # --------------------------------------------------------
        # SWEETNESS
        # --------------------------------------------------------

        for index, value in enumerate(
            SWEETNESS_OPTIONS
        ):

            rect = pygame.Rect(
                325 + index * 88,
                410,
                78,
                48
            )

            self.sweetness_buttons[
                value
            ] = rect

    # ============================================================
    # PUBLIC INTEGRATION METHODS
    # ============================================================

    def set_level(
        self,
        level
    ):

        """
        Update the player's current level.
        """

        self.level = max(
            1,
            int(level)
        )

    # ------------------------------------------------------------

    def set_progression(
        self,
        progression
    ):

        """
        Connect station to progression.py.
        """

        self.progression = progression

        self.set_level(
            getattr(
                progression,
                "level",
                self.level
            )
        )

    # ------------------------------------------------------------

    def set_rewards(
        self,
        rewards
    ):

        """
        Connect station to rewards.py.
        """

        self.rewards = rewards

    # ------------------------------------------------------------

    def set_customer_order(
        self,
        order
    ):

        """
        Receive the current CustomerOrder.

        The customer sprite itself is NOT controlled here.
        """

        self.customer_order = order

        self.order_message = ""

        self.game_state.set_order(
            order
        )

        self.player_drink.reset()

        self.served = False

    # ------------------------------------------------------------

    def update_customer_order(
        self,
        order
    ):

        """
        Alias for easy main.py integration.
        """

        self.set_customer_order(
            order
        )

    # ------------------------------------------------------------

    def get_player_drink_data(
        self
    ):

        """
        Return the new four-part drink data.
        """

        return self.game_state.get_player_drink_data()

    # ------------------------------------------------------------

    def get_data(
        self
    ):

        """
        Compatibility method.

        Returns:

            drink
            temperature
            caffeine
            sweetness
        """

        return self.get_player_drink_data()

    # ============================================================
    # LEGACY COMPATIBILITY
    # ============================================================

    def _attach_legacy_data_bridge(
        self
    ):

        """
        Connect the old Drink object's get_data()
        to our new data.

        This lets the existing main.py ask:

            drink.get_data()

        while receiving:

            {
                "drink": "...",
                "temperature": "...",
                "caffeine": "...",
                "sweetness": "..."
            }
        """

        if self.drink is not None:

            try:

                self.drink.get_data = (
                    self.get_data
                )

            except Exception:
                pass

    # ------------------------------------------------------------

    def _sync_legacy_numeric_values(
        self
    ):

        """
        Keep the old Drink object's numerical fields
        synchronized with our new three-level choices.

        Cold   = 25
        Normal = 50
        Hot    = 75

        Low    = 25
        Normal = 50
        High   = 75

        Less   = 25
        Normal = 50
        Extra  = 75
        """

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
                    50
                )
            )

            self.drink.caffeine = (
                caffeine_map.get(
                    self.player_drink.caffeine,
                    50
                )
            )

            self.drink.sweetness = (
                sweetness_map.get(
                    self.player_drink.sweetness,
                    50
                )
            )

        except Exception:
            pass

    # ============================================================
    # STATE HELPERS
    # ============================================================

    def _allow_selection_mode(
        self
    ):

        """
        During our transition into the new station,
        allow the menu to be tested even before the
        real customer-order connection is added.
        """

        if (
            self.game_state.state
            == GameState.WAITING_FOR_ORDER
        ):

            self.game_state.state = (
                GameState.SELECT_DRINK
            )

    # ------------------------------------------------------------

    def _drink_is_available(
        self,
        drink_name
    ):

        return (

            is_valid_drink(
                drink_name
            )

            and

            is_drink_unlocked(
                drink_name,
                self.level
            )
        )

    # ------------------------------------------------------------

    def _update_blending(
        self
    ):

        """
        Finish the blending animation automatically.
        """

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

            self._sync_legacy_numeric_values()

    # ============================================================
    # HANDLE PLAYER INPUT
    # ============================================================

    def handle_event(
        self,
        event
    ):

        if (
            event.type
            != pygame.MOUSEBUTTONDOWN
        ):

            return

        if event.button != 1:
            return

        self._update_blending()

        mouse = event.pos

        # ========================================================
        # DRINK MENU
        # ========================================================

        for drink_name, rect in (
            self.menu_slots
        ):

            if rect.collidepoint(
                mouse
            ):

                # Locked drink.
                if not self._drink_is_available(
                    drink_name
                ):

                    return

                # Cannot change drink after
                # blending has started.

                if self.game_state.state in (

                    GameState.BLENDING,

                    GameState.BLENDED,

                    GameState.CUP_READY,

                    GameState.READY_TO_SERVE,

                    GameState.SERVED,
                ):

                    return

                self._allow_selection_mode()

                if self.game_state.select_drink(
                    drink_name
                ):

                    self.player_drink.drink_name = (
                        drink_name
                    )

                    self.served = False

                return

        # ========================================================
        # TEMPERATURE
        # ========================================================

        if self.game_state.can_customize():

            for value, rect in (
                self.temperature_buttons.items()
            ):

                if rect.collidepoint(
                    mouse
                ):

                    self.game_state.select_temperature(
                        value
                    )

                    self.player_drink.temperature = (
                        value
                    )

                    self._sync_legacy_numeric_values()

                    return

            # ====================================================
            # CAFFEINE
            # ====================================================

            for value, rect in (
                self.caffeine_buttons.items()
            ):

                if rect.collidepoint(
                    mouse
                ):

                    self.game_state.select_caffeine(
                        value
                    )

                    self.player_drink.caffeine = (
                        value
                    )

                    self._sync_legacy_numeric_values()

                    return

            # ====================================================
            # SWEETNESS
            # ====================================================

            for value, rect in (
                self.sweetness_buttons.items()
            ):

                if rect.collidepoint(
                    mouse
                ):

                    self.game_state.select_sweetness(
                        value
                    )

                    self.player_drink.sweetness = (
                        value
                    )

                    self._sync_legacy_numeric_values()

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

            return

        # ========================================================
        # PLACE INTO CUP
        # ========================================================

        if self.place_button.collidepoint(
            mouse
        ):

            self.game_state.place_into_cup()

            return

        # ========================================================
        # SERVE
        # ========================================================

        if self.serve_button.collidepoint(
            mouse
        ):

            if self.game_state.serve():

                self.served = True

                self._sync_legacy_numeric_values()

            return

    # ============================================================
    # DRAW EVERYTHING
    # ============================================================

    def draw(
        self,
        screen
    ):

        self._update_blending()

        self._draw_hud(
            screen
        )

        self._draw_drink_menu(
            screen
        )

        self._draw_customer_order_area(
            screen
        )

        self._draw_customisation(
            screen
        )

        self._draw_blender(
            screen
        )

        self._draw_toppings(
            screen
        )

        self._draw_final_preview(
            screen
        )

    # ============================================================
    # HUD
    # ============================================================

    def _draw_hud(
        self,
        screen
    ):

        self._draw_panel(
            screen,
            self.hud_rect,
            self.CYAN,
            self.BG_PANEL
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
                level
            )

            xp = getattr(
                self.progression,
                "xp",
                xp
            )

            max_xp = getattr(
                self.progression,
                "xp_required",
                max_xp
            )

            if callable(max_xp):

                max_xp = max_xp()

        # --------------------------------------------------------
        # REWARDS
        # --------------------------------------------------------

        if self.rewards is not None:

            try:

                credits = (
                    self.rewards.get_total_credits()
                )

            except Exception:

                credits = getattr(
                    self.rewards,
                    "credits",
                    0
                )

            try:

                combo = (
                    self.rewards.get_combo()
                )

            except Exception:

                combo = getattr(
                    self.rewards,
                    "combo",
                    0
                )

        # --------------------------------------------------------
        # LEVEL
        # --------------------------------------------------------

        level_text = self.font_hud.render(
            f"LEVEL {level}",
            True,
            self.PINK_BRIGHT
        )

        screen.blit(
            level_text,
            (34, 20)
        )

        # --------------------------------------------------------
        # XP
        # --------------------------------------------------------

        xp_x = 145

        xp_y = 20

        xp_width = 420

        xp_height = 22

        xp_label = self.font_small.render(
            "XP",
            True,
            self.CYAN_BRIGHT
        )

        screen.blit(
            xp_label,
            (
                xp_x,
                xp_y + 3
            )
        )

        bar = pygame.Rect(
            xp_x + 30,
            xp_y,
            xp_width,
            xp_height
        )

        pygame.draw.rect(
            screen,
            (20, 24, 45),
            bar,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            bar,
            width=2,
            border_radius=10
        )

        ratio = 0

        if max_xp > 0:

            ratio = max(
                0,
                min(
                    1,
                    xp / max_xp
                )
            )

        fill = pygame.Rect(
            bar.x + 3,
            bar.y + 3,
            int(
                (bar.width - 6)
                * ratio
            ),
            bar.height - 6
        )

        if fill.width > 0:

            pygame.draw.rect(
                screen,
                self.PINK,
                fill,
                border_radius=8
            )

        xp_text = self.font_tiny.render(
            f"{xp} / {max_xp}",
            True,
            self.WHITE
        )

        screen.blit(
            xp_text,
            xp_text.get_rect(
                center=bar.center
            )
        )

        # --------------------------------------------------------
        # CREDITS
        # --------------------------------------------------------

        credits_text = self.font_hud.render(
            f"CREDITS  {credits}",
            True,
            self.YELLOW
        )

        screen.blit(
            credits_text,
            credits_text.get_rect(
                midright=(
                    1110,
                    31
                )
            )
        )

        # --------------------------------------------------------
        # COMBO
        # --------------------------------------------------------

        combo_text = self.font_hud.render(
            f"COMBO  x{combo}",
            True,
            self.MINT
        )

        screen.blit(
            combo_text,
            combo_text.get_rect(
                midright=(
                    1245,
                    31
                )
            )
        )

    # ============================================================
    # DRINK MENU
    # ============================================================

    def _draw_drink_menu(
        self,
        screen
    ):

        self._draw_panel(
            screen,
            self.menu_rect,
            self.PURPLE,
            self.BG_PANEL_DARK
        )

        for drink_name, rect in (
            self.menu_slots
        ):

            unlocked = (
                self._drink_is_available(
                    drink_name
                )
            )

            selected = (
                self.player_drink.drink_name
                == drink_name
            )

            hover = rect.collidepoint(
                pygame.mouse.get_pos()
            )

            # ----------------------------------------------------
            # CARD COLOUR
            # ----------------------------------------------------

            if selected:

                border = self.PINK_BRIGHT

                fill = (
                    50,
                    16,
                    52,
                    245
                )

            elif unlocked:

                border = self.CYAN

                fill = (
                    13,
                    18,
                    37,
                    240
                )

            else:

                border = (
                    60,
                    65,
                    90
                )

                fill = (
                    8,
                    10,
                    22,
                    235
                )

            if (
                hover
                and unlocked
            ):

                border = self.PINK_BRIGHT

            self._draw_panel(
                screen,
                rect,
                border,
                fill
            )

            # ----------------------------------------------------
            # DRINK IMAGE
            # ----------------------------------------------------

            image = self.drink_images.get(
                drink_name
            )

            image_rect = pygame.Rect(
                rect.x + 14,
                rect.y + 5,
                rect.width - 28,
                72
            )

            if image is not None:

                self._draw_image_fit(
                    screen,
                    image,
                    image_rect,
                    unlocked
                )

            else:

                self._draw_drink_placeholder(
                    screen,
                    image_rect,
                    drink_name,
                    unlocked
                )

            # ----------------------------------------------------
            # LOCK
            # ----------------------------------------------------

            if not unlocked:

                self._draw_lock(
                    screen,
                    rect.centerx,
                    rect.y + 43
                )

            # ----------------------------------------------------
            # NAME
            # ----------------------------------------------------

            name_color = (
                self.WHITE
                if unlocked
                else self.LOCKED
            )

            name_surface = self.font_menu.render(
                drink_name,
                True,
                name_color
            )

            name_rect = name_surface.get_rect(
                center=(
                    rect.centerx,
                    rect.bottom - 17
                )
            )

            screen.blit(
                name_surface,
                name_rect
            )

    # ============================================================
    # CUSTOMER ORDER
    # ============================================================

    def _draw_customer_order_area(
        self,
        screen
    ):

        # --------------------------------------------------------
        # CUSTOMER AREA
        # --------------------------------------------------------
        #
        # NOTHING is drawn over the customer here.
        #
        # customer.py/main.py own the customer sprite.
        #

        # --------------------------------------------------------
        # ORDER PANEL
        # --------------------------------------------------------

        self._draw_panel(
            screen,
            self.order_rect,
            self.PINK,
            self.BG_PANEL
        )

        title = self.font_panel.render(
            "CURRENT ORDER",
            True,
            self.PINK_BRIGHT
        )

        screen.blit(
            title,
            (34, 464)
        )

        order = self.customer_order

        # --------------------------------------------------------
        # NO CUSTOMER YET
        # --------------------------------------------------------

        if order is None:

            waiting = self.font_panel.render(
                self.order_message,
                True,
                self.MUTED
            )

            screen.blit(
                waiting,
                waiting.get_rect(
                    center=(
                        self.order_rect.centerx,
                        545
                    )
                )
            )

            return

        # --------------------------------------------------------
        # ORDER DATA
        # --------------------------------------------------------

        drink_name = getattr(
            order,
            "drink",
            None
        )

        temperature = getattr(
            order,
            "temperature",
            None
        )

        caffeine = getattr(
            order,
            "caffeine",
            None
        )

        sweetness = getattr(
            order,
            "sweetness",
            None
        )

        # --------------------------------------------------------
        # DRINK IMAGE
        # --------------------------------------------------------

        image = self.drink_images.get(
            drink_name
        )

        image_rect = pygame.Rect(
            34,
            500,
            62,
            70
        )

        if image is not None:

            self._draw_image_fit(
                screen,
                image,
                image_rect,
                True
            )

        # --------------------------------------------------------
        # DRINK NAME
        # --------------------------------------------------------

        drink_text = self.font_panel.render(
            str(drink_name),
            True,
            self.PINK_BRIGHT
        )

        screen.blit(
            drink_text,
            (108, 502)
        )

        # --------------------------------------------------------
        # TEMPERATURE
        # --------------------------------------------------------

        self._draw_order_line(
            screen,
            "TEMP",
            temperature,
            535,
            108
        )

        # --------------------------------------------------------
        # CAFFEINE
        # --------------------------------------------------------

        self._draw_order_line(
            screen,
            "CAFFEINE",
            caffeine,
            563,
            108
        )

        # --------------------------------------------------------
        # SWEETNESS
        # --------------------------------------------------------

        self._draw_order_line(
            screen,
            "SWEETNESS",
            sweetness,
            591,
            108
        )

        # --------------------------------------------------------
        # INSTRUCTION
        # --------------------------------------------------------

        instruction = self.font_tiny.render(
            "MATCH THE ORDER EXACTLY",
            True,
            self.CYAN
        )

        screen.blit(
            instruction,
            (108, 615)
        )

    # ------------------------------------------------------------

    def _draw_order_line(
        self,
        screen,
        label,
        value,
        y,
        x=118
    ):

        label_surface = self.font_tiny.render(
            label,
            True,
            self.MUTED
        )

        screen.blit(
            label_surface,
            (x, y)
        )

        value_surface = self.font_small.render(
            (
                str(value)
                if value is not None
                else "---"
            ),
            True,
            self.WHITE
        )

        screen.blit(
            value_surface,
            (
                x + 82,
                y - 2
            )
        )

    # ============================================================
    # CUSTOMISATION
    # ============================================================

    def _draw_customisation(
        self,
        screen
    ):

        self._draw_panel(
            screen,
            self.customise_rect,
            self.CYAN,
            self.BG_PANEL
        )

        title = self.font_panel.render(
            "CUSTOMISE YOUR DRINK",
            True,
            self.CYAN_BRIGHT
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.customise_rect.centerx,
                    225
                )
            )
        )

        # Temperature.

        self._draw_option_row(
            screen,
            "TEMPERATURE",
            self.temperature_buttons,
            self.player_drink.temperature
        )

        # Caffeine.

        self._draw_option_row(
            screen,
            "CAFFEINE",
            self.caffeine_buttons,
            self.player_drink.caffeine
        )

        # Sweetness.

        self._draw_option_row(
            screen,
            "SWEETNESS",
            self.sweetness_buttons,
            self.player_drink.sweetness
        )

    # ------------------------------------------------------------

    def _draw_option_row(
        self,
        screen,
        label,
        buttons,
        selected
    ):

        first = next(
            iter(
                buttons.values()
            )
        )

        label_surface = self.font_tiny.render(
            label,
            True,
            self.MUTED
        )

        screen.blit(
            label_surface,
            (
                first.x,
                first.y - 18
            )
        )

        for value, rect in (
            buttons.items()
        ):

            active = (
                value == selected
            )

            enabled = (
                self.game_state.can_customize()
            )

            if active:

                fill = (
                    45,
                    18,
                    65
                )

                border = self.PINK_BRIGHT

                text_color = self.WHITE

            elif enabled:

                fill = (
                    12,
                    18,
                    38
                )

                border = self.CYAN

                text_color = self.WHITE

            else:

                fill = (
                    9,
                    12,
                    25
                )

                border = (
                    50,
                    55,
                    80
                )

                text_color = self.MUTED

            self._draw_panel(
                screen,
                rect,
                border,
                fill
            )

            text = self.font_small.render(
                value,
                True,
                text_color
            )

            screen.blit(
                text,
                text.get_rect(
                    center=rect.center
                )
            )

    # ============================================================
    # BLENDER
    # ============================================================

    def _draw_blender(
        self,
        screen
    ):

        self._draw_panel(
            screen,
            self.blender_rect,
            self.PURPLE,
            self.BG_PANEL_DARK
        )

        title = self.font_panel.render(
            "BLENDER",
            True,
            self.PURPLE
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.blender_rect.centerx,
                    218
                )
            )
        )

        # --------------------------------------------------------
        # GLASS JUG
        # --------------------------------------------------------

        pygame.draw.rect(
            screen,
            (25, 30, 52),
            self.blender_jug_rect,
            border_radius=22
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            self.blender_jug_rect,
            width=2,
            border_radius=22
        )

        # --------------------------------------------------------
        # LIQUID
        # --------------------------------------------------------

        if self.player_drink.drink_name:

            recipe = get_recipe(
                self.player_drink.drink_name
            )

            if recipe:

                liquid_color = (
                    recipe.liquid_color
                )

            else:

                liquid_color = (
                    120,
                    150,
                    255
                )

            liquid_height = 90

            if (
                self.game_state.state
                == GameState.BLENDING
            ):

                pulse = int(
                    (
                        time.monotonic()
                        * 180
                    )
                    % 15
                )

                liquid_height = (
                    90 + pulse
                )

                self._draw_blend_particles(
                    screen
                )

            liquid_rect = pygame.Rect(

                self.blender_jug_rect.x + 12,

                self.blender_jug_rect.bottom
                - liquid_height
                - 10,

                self.blender_jug_rect.width - 24,

                liquid_height
            )

            pygame.draw.rect(
                screen,
                liquid_color,
                liquid_rect,
                border_radius=14
            )

            # Liquid swirl.

            cx, cy = (
                liquid_rect.center
            )

            pygame.draw.arc(

                screen,

                self.WHITE,

                pygame.Rect(
                    cx - 42,
                    cy - 15,
                    84,
                    30
                ),

                0,

                4.8,

                3
            )

        else:

            empty = self.font_small.render(
                "SELECT A DRINK",
                True,
                self.MUTED
            )

            screen.blit(
                empty,
                empty.get_rect(
                    center=(
                        self.blender_jug_rect.center
                    )
                )
            )

        # --------------------------------------------------------
        # BLENDER BASE
        # --------------------------------------------------------

        base = pygame.Rect(

            self.blender_jug_rect.x - 12,

            self.blender_jug_rect.bottom - 5,

            self.blender_jug_rect.width + 24,

            35
        )

        pygame.draw.rect(
            screen,
            (24, 18, 45),
            base,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            self.PINK,
            base,
            width=2,
            border_radius=10
        )

        # --------------------------------------------------------
        # BLEND BUTTON
        # --------------------------------------------------------
        #
        # DIRECTLY UNDER THE BLENDER.
        #

        self._draw_action_button(

            screen,

            self.blend_button,

            "BLEND",

            self.CYAN,

            self.game_state.can_blend()
        )

        # --------------------------------------------------------
        # BLEND STATUS
        # --------------------------------------------------------

        if (
            self.game_state.state
            == GameState.BLENDING
        ):

            blend_text = self.font_small.render(
                "BLENDING...",
                True,
                self.PINK_BRIGHT
            )

            screen.blit(
                blend_text,
                blend_text.get_rect(
                    center=(
                        self.blender_rect.centerx,
                        484
                    )
                )
            )

        elif (
            self.game_state.state
            == GameState.BLENDED
        ):

            done = self.font_small.render(
                "BLEND COMPLETE",
                True,
                self.MINT
            )

            screen.blit(
                done,
                done.get_rect(
                    center=(
                        self.blender_rect.centerx,
                        484
                    )
                )
            )

    # ------------------------------------------------------------

    def _draw_blend_particles(
        self,
        screen
    ):

        cx, cy = (
            self.blender_jug_rect.center
        )

        points = (

            (
                cx - 45,
                cy - 55
            ),

            (
                cx + 42,
                cy - 40
            ),

            (
                cx - 52,
                cy + 12
            ),

            (
                cx + 50,
                cy + 25
            ),
        )

        for x, y in points:

            pygame.draw.circle(
                screen,
                self.CYAN_BRIGHT,
                (
                    x,
                    y
                ),
                3
            )

            pygame.draw.circle(
                screen,
                self.PINK_BRIGHT,
                (
                    x + 7,
                    y - 5
                ),
                2
            )

    # ============================================================
    # TOPPINGS
    # ============================================================

    def _draw_toppings(
        self,
        screen
    ):

        self._draw_panel(
            screen,
            self.toppings_rect,
            self.PINK,
            self.BG_PANEL
        )

        title = self.font_panel.render(
            "TOPPINGS",
            True,
            self.PINK_BRIGHT
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.toppings_rect.centerx,
                    532
                )
            )
        )

        subtitle = self.font_tiny.render(
            "AUTOMATIC • VISUAL ONLY",
            True,
            self.MUTED
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    self.toppings_rect.centerx,
                    550
                )
            )
        )

        # --------------------------------------------------------
        # VISUAL TOPPING BINS
        # --------------------------------------------------------
        #
        # THESE ARE NOT CLICKABLE.
        #

        topping_colours = (

            (255, 245, 250),

            (100, 255, 210),

            (120, 75, 45),

            (230, 160, 55),

            (255, 220, 80),

            (110, 180, 255),
        )

        for index, (_, name) in enumerate(
            self.topping_names
        ):

            row = index // 3

            col = index % 3

            x = (
                625
                + col * 88
            )

            y = (
                565
                + row * 58
            )

            rect = pygame.Rect(
                x,
                y,
                78,
                48
            )

            self._draw_panel(
                screen,
                rect,
                (
                    70,
                    80,
                    120
                ),
                (
                    12,
                    16,
                    34
                )
            )

            pygame.draw.circle(
                screen,
                topping_colours[index],
                (
                    rect.centerx,
                    rect.y + 15
                ),
                8
            )

            text = self.font_tiny.render(
                name,
                True,
                self.WHITE
            )

            screen.blit(
                text,
                text.get_rect(
                    center=(
                        rect.centerx,
                        rect.bottom - 10
                    )
                )
            )

    # ============================================================
    # FINAL DRINK PREVIEW
    # ============================================================

    def _draw_final_preview(
        self,
        screen
    ):

        self._draw_panel(
            screen,
            self.preview_rect,
            self.PINK,
            self.BG_PANEL
        )

        title = self.font_panel.render(
            "FINAL DRINK PREVIEW",
            True,
            self.PINK_BRIGHT
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.preview_rect.centerx,
                    220
                )
            )
        )

        # --------------------------------------------------------
        # PREVIEW FRAME
        # --------------------------------------------------------

        pygame.draw.rect(
            screen,
            (8, 12, 30),
            self.preview_image_rect,
            border_radius=18
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            self.preview_image_rect,
            width=2,
            border_radius=18
        )

        # --------------------------------------------------------
        # DRINK IMAGE
        # --------------------------------------------------------

        drink_name = (
            self.player_drink.drink_name
        )

        image = self.drink_images.get(
            drink_name
        )

        if image is not None:

            self._draw_image_fit(

                screen,

                image,

                self.preview_image_rect.inflate(
                    -40,
                    -20
                ),

                True
            )

        else:

            preview_text = self.font_large.render(

                (
                    drink_name
                    if drink_name
                    else "NO DRINK YET"
                ),

                True,

                self.MUTED
            )

            screen.blit(

                preview_text,

                preview_text.get_rect(
                    center=(
                        self.preview_image_rect.center
                    )
                )
            )

        # --------------------------------------------------------
        # PLACE INTO CUP
        # --------------------------------------------------------

        self._draw_action_button(

            screen,

            self.place_button,

            "PLACE INTO CUP",

            self.PINK,

            self.game_state.can_place_into_cup()
        )

        # --------------------------------------------------------
        # SERVE
        # --------------------------------------------------------

        self._draw_action_button(

            screen,

            self.serve_button,

            "SERVE",

            self.CYAN,

            self.game_state.can_serve()
        )

    # ============================================================
    # GENERIC PANEL
    # ============================================================

    def _draw_panel(
        self,
        screen,
        rect,
        border_color,
        fill
    ):

        # --------------------------------------------------------
        # TRANSPARENT FILL
        # --------------------------------------------------------

        surface = pygame.Surface(
            rect.size,
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            surface,
            fill,
            surface.get_rect(),
            border_radius=16
        )

        screen.blit(
            surface,
            rect.topleft
        )

        # --------------------------------------------------------
        # NEON BORDER
        # --------------------------------------------------------

        pygame.draw.rect(
            screen,
            border_color,
            rect,
            width=2,
            border_radius=16
        )

    # ============================================================
    # ACTION BUTTON
    # ============================================================

    def _draw_action_button(
        self,
        screen,
        rect,
        label,
        accent,
        enabled
    ):

        hover = (

            enabled

            and

            rect.collidepoint(
                pygame.mouse.get_pos()
            )
        )

        if enabled:

            if hover:

                fill = (
                    55,
                    22,
                    65
                )

                border = (
                    self.PINK_BRIGHT
                )

            else:

                fill = (
                    30,
                    16,
                    48
                )

                border = accent

            text_color = (
                self.WHITE
            )

        else:

            fill = (
                10,
                13,
                27
            )

            border = (
                55,
                60,
                82
            )

            text_color = (
                self.MUTED
            )

        self._draw_panel(
            screen,
            rect,
            border,
            fill
        )

        inner = rect.inflate(
            -10,
            -10
        )

        pygame.draw.rect(
            screen,
            (
                45,
                50,
                75
            )
            if not enabled
            else border,
            inner,
            width=1,
            border_radius=12
        )

        text = self.font_xlarge.render(
            label,
            True,
            text_color
        )

        screen.blit(
            text,
            text.get_rect(
                center=rect.center
            )
        )

    # ============================================================
    # DRAW IMAGE
    # ============================================================

    def _draw_image_fit(
        self,
        screen,
        image,
        target,
        bright=True
    ):

        source_width, source_height = (
            image.get_size()
        )

        if (
            source_width <= 0
            or source_height <= 0
        ):

            return

        scale = min(

            target.width
            / source_width,

            target.height
            / source_height
        )

        new_size = (

            max(
                1,
                int(
                    source_width
                    * scale
                )
            ),

            max(
                1,
                int(
                    source_height
                    * scale
                )
            )
        )

        scaled = pygame.transform.smoothscale(
            image,
            new_size
        )

        # Dim locked drinks.
        if not bright:

            scaled = scaled.copy()

            scaled.fill(
                (
                    90,
                    90,
                    110,
                    255
                ),
                special_flags=pygame.BLEND_RGBA_MULT
            )

        destination = (
            scaled.get_rect(
                center=target.center
            )
        )

        screen.blit(
            scaled,
            destination
        )

    # ============================================================
    # DRINK PLACEHOLDER
    # ============================================================

    def _draw_drink_placeholder(
        self,
        screen,
        rect,
        drink_name,
        unlocked
    ):

        color = (
            self.CYAN
            if unlocked
            else self.LOCKED
        )

        pygame.draw.ellipse(
            screen,
            color,
            rect.inflate(
                -50,
                -5
            ),
            2
        )

        text = self.font_tiny.render(
            "DRINK",
            True,
            color
        )

        screen.blit(
            text,
            text.get_rect(
                center=rect.center
            )
        )

    # ============================================================
    # LOCK ICON
    # ============================================================

    def _draw_lock(
        self,
        screen,
        x,
        y
    ):

        body = pygame.Rect(
            x - 10,
            y - 2,
            20,
            18
        )

        pygame.draw.rect(
            screen,
            self.LOCKED,
            body,
            border_radius=4
        )

        pygame.draw.arc(

            screen,

            self.LOCKED,

            pygame.Rect(
                x - 7,
                y - 13,
                14,
                18
            ),

            3.14,

            6.28,

            3
        )

    # ============================================================
    # RESET
    # ============================================================

    def reset(
        self
    ):

        """
        Prepare station for the next customer.
        """

        self.player_drink.reset()

        self.game_state.reset()

        self.customer_order = None

        self.order_message = (
            "WAITING FOR CUSTOMER"
        )

        self.served = False

        self.blend_start_time = 0.0

        if self.drink is not None:

            try:

                self.drink.reset()

            except Exception:
                pass

        self._attach_legacy_data_bridge()


# ================================================================
# OPTIONAL STANDALONE TEST
# ================================================================
#
# This section is NOT used by main.py.
#
# It allows station.py to be tested by itself if needed.
# ================================================================

if __name__ == "__main__":

    pygame.init()

    screen = pygame.display.set_mode(
        (
            1280,
            720
        )
    )

    pygame.display.set_caption(
        "Cyberpunk Café - Mixing Station Test"
    )

    from drink import Drink

    legacy_drink = Drink()

    station = MixingStation(
        legacy_drink,
        level=3
    )

    clock = pygame.time.Clock()

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            station.handle_event(
                event
            )

        screen.fill(
            (
                5,
                7,
                18
            )
        )

        station.draw(
            screen
        )

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
import os
import random
import pygame

from drink import (
    TEMPERATURE_OPTIONS,
    CAFFEINE_OPTIONS,
    SWEETNESS_OPTIONS,
    get_unlocked_drinks,
)


# ============================================================
# 1280x720 GAME SCALING
# ============================================================

GAME_WIDTH = 1280
GAME_HEIGHT = 720

BASE_WIDTH = 960
BASE_HEIGHT = 540

SCALE_X = GAME_WIDTH / BASE_WIDTH
SCALE_Y = GAME_HEIGHT / BASE_HEIGHT


def sx(value):
    """Convert a 960x540 X coordinate to the 1280x720 game size."""
    return int(round(value * SCALE_X))


def sy(value):
    """Convert a 960x540 Y coordinate to the 1280x720 game size."""
    return int(round(value * SCALE_Y))


# ============================================================
# CUSTOMER STATES
# ============================================================

class CustomerState:
    """
    These are the different stages of a customer's life.
    """

    SPAWNING = "spawning"
    ORDERING = "ordering"
    WAITING = "waiting"
    SERVED = "served"
    LEAVING = "leaving"


# ============================================================
# CUSTOMER ORDER
# ============================================================

class CustomerOrder:
    """
    Stores exactly what one customer wants.

    Every order contains:

        1. Drink
        2. Temperature
        3. Caffeine
        4. Sweetness
    """

    def __init__(
        self,
        drink,
        temperature,
        caffeine,
        sweetness,
    ):
        self.drink = drink
        self.temperature = temperature
        self.caffeine = caffeine
        self.sweetness = sweetness

    def get_data(self):
        """
        Convert the order into a dictionary.

        This makes it easy for other systems to read.
        """

        return {
            "drink": self.drink,
            "temperature": self.temperature,
            "caffeine": self.caffeine,
            "sweetness": self.sweetness,
        }

    def __str__(self):
        """
        Human-readable version of the order.
        """

        return (
            f"{self.drink} | "
            f"{self.temperature} | "
            f"{self.caffeine} Caffeine | "
            f"{self.sweetness} Sweet"
        )


# ============================================================
# CUSTOMER
# ============================================================

class Customer:
    """
    Manages:

        - customer appearance
        - customer movement
        - customer FSM
        - customer order
        - patience
        - order verification
        - feedback
        - speech UI
    """

    def __init__(self, x=360, y_counter=405, current_level=1):

        # ----------------------------------------------------
        # POSITION
        # ----------------------------------------------------

        self.x = sx(x)
        self.y_counter = sy(y_counter)

        # ----------------------------------------------------
        # CURRENT LEVEL
        # ----------------------------------------------------

        self.level = current_level

        # ----------------------------------------------------
        # CUSTOMER TYPE
        # ----------------------------------------------------

        self.customer_types = [
            "runner",
            "exec",
            "hacker",
        ]

        self.current_type = random.choice(
            self.customer_types
        )

        self.image = self._load_sprite(
            self.current_type
        )

        # ----------------------------------------------------
        # FSM STATE
        # ----------------------------------------------------

        self.state = CustomerState.SPAWNING

        # ----------------------------------------------------
        # MOVEMENT
        # ----------------------------------------------------

        self.spawn_y = (
            self.y_counter + sy(120)
        )

        self.current_y = self.spawn_y

        self.rect = self.image.get_rect()

        self.rect.centerx = self.x
        self.rect.bottom = int(self.current_y)

        # ----------------------------------------------------
        # CUSTOMER ORDER
        # ----------------------------------------------------

        self.order = self._generate_order()

        # ----------------------------------------------------
        # BACKWARD-COMPATIBILITY VALUES
        # ----------------------------------------------------
        #
        # These will eventually be removed.
        #
        # The old main.py / station.py may still refer to
        # target_sweetness, target_caffeine and
        # target_temperature.
        #
        # We temporarily keep them so the migration is safe.
        #

        self.target_sweetness = self._sweetness_to_number(
            self.order.sweetness
        )

        self.target_caffeine = self._caffeine_to_number(
            self.order.caffeine
        )

        self.target_temperature = self._temperature_to_number(
            self.order.temperature
        )

        # ----------------------------------------------------
        # PATIENCE
        # ----------------------------------------------------

        self.max_patience = 20.0
        self.current_patience = self.max_patience

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.font = pygame.font.SysFont(
            "Consolas",
            sy(12),
            bold=True
        )

        self.dialogue = self._generate_dialogue()

        self.feedback_text = ""

        self.feedback_color = (
            0,
            255,
            150
        )

    # ========================================================
    # ORDER GENERATION
    # ========================================================

    def _generate_order(self):
        """
        Generate a legal order using the drinks unlocked
        at the customer's current level.
        """

        unlocked_drinks = get_unlocked_drinks(
            self.level
        )

        # Safety check.
        #
        # There should always be at least the three
        # Level 1 drinks available.
        if not unlocked_drinks:
            unlocked_drinks = get_unlocked_drinks(1)

        drink = random.choice(
            unlocked_drinks
        )

        temperature = random.choice(
            TEMPERATURE_OPTIONS
        )

        caffeine = random.choice(
            CAFFEINE_OPTIONS
        )

        sweetness = random.choice(
            SWEETNESS_OPTIONS
        )

        return CustomerOrder(
            drink=drink,
            temperature=temperature,
            caffeine=caffeine,
            sweetness=sweetness,
        )

    # ========================================================
    # OLD NUMERIC COMPATIBILITY
    # ========================================================

    def _sweetness_to_number(self, sweetness):
        """
        Temporary conversion for the old system.

        New system:
            Less = 25
            Normal = 50
            Extra = 75
        """

        values = {
            "Less": 25,
            "Normal": 50,
            "Extra": 75,
        }

        return values.get(
            sweetness,
            50
        )

    def _caffeine_to_number(self, caffeine):
        """
        Temporary conversion for the old system.

        New system:
            Low = 25
            Normal = 50
            High = 75
        """

        values = {
            "Low": 25,
            "Normal": 50,
            "High": 75,
        }

        return values.get(
            caffeine,
            50
        )

    def _temperature_to_number(self, temperature):
        """
        Temporary conversion for the old system.

        New system:
            Cold = 25
            Normal = 50
            Hot = 75
        """

        values = {
            "Cold": 25,
            "Normal": 50,
            "Hot": 75,
        }

        return values.get(
            temperature,
            50
        )

    # ========================================================
    # SPRITE
    # ========================================================

    def _load_sprite(self, ctype):
        """
        Load a customer image and scale it to the game size.
        """

        filename = f"{ctype}.png"

        project_root = os.path.dirname(
            os.path.abspath(__file__)
        )

        path = os.path.join(
            project_root,
            "assets",
            "customers",
            filename
        )

        if os.path.exists(path):

            img = pygame.image.load(
                path
            ).convert_alpha()

        else:

            img = pygame.Surface(
                (
                    sx(180),
                    sy(220)
                ),
                pygame.SRCALPHA
            )

            img.fill(
                (
                    100,
                    100,
                    150
                )
            )

        return pygame.transform.scale(
            img,
            (
                sx(180),
                sy(220)
            )
        )

    # ========================================================
    # DIALOGUE
    # ========================================================

    def _generate_dialogue(self):
        """
        Generate customer speech from the actual order.
        """

        return (
            f"{self.order.drink} / "
            f"{self.order.temperature} / "
            f"{self.order.caffeine} Caffeine / "
            f"{self.order.sweetness} Sweet"
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):
        """
        Update the customer's FSM and movement.
        """

        # ----------------------------------------------------
        # SPAWNING
        # ----------------------------------------------------

        if self.state == CustomerState.SPAWNING:

            if self.current_y > self.y_counter:

                self.current_y -= (
                    sy(120) * dt
                )

                if self.current_y <= self.y_counter:

                    self.current_y = self.y_counter

                    self.state = (
                        CustomerState.ORDERING
                    )

            self.rect.bottom = int(
                self.current_y
            )

        # ----------------------------------------------------
        # ORDERING
        # ----------------------------------------------------

        elif self.state == CustomerState.ORDERING:

            self.state = CustomerState.WAITING

        # ----------------------------------------------------
        # WAITING
        # ----------------------------------------------------

        elif self.state == CustomerState.WAITING:

            self.current_patience -= dt

            if self.current_patience <= 0:

                self.current_patience = 0.0

                self.feedback_text = (
                    "TOO SLOW!"
                )

                self.feedback_color = (
                    255,
                    50,
                    80
                )

                self.state = (
                    CustomerState.LEAVING
                )

        # ----------------------------------------------------
        # SERVED / LEAVING
        # ----------------------------------------------------

        elif self.state in (
            CustomerState.SERVED,
            CustomerState.LEAVING,
        ):

            if self.current_y < self.spawn_y:

                self.current_y += (
                    sy(150) * dt
                )

            self.rect.bottom = int(
                self.current_y
            )

    # ========================================================
    # SERVE
    # ========================================================

    def serve_drink(self, drink_data):
        """
        Evaluate the player's completed drink.

        Returns:
            True  = correct order
            False = incorrect order
        """

        if self.state != CustomerState.WAITING:
            return False

        success = self.verify_order(
            drink_data
        )

        if success:

            self.feedback_text = "PERFECT!"

            self.feedback_color = (
                0,
                255,
                150
            )

            self.state = (
                CustomerState.SERVED
            )

        else:

            self.feedback_text = (
                "WRONG DRINK!"
            )

            self.feedback_color = (
                255,
                50,
                80
            )

            self.state = (
                CustomerState.LEAVING
            )

        return success

    # ========================================================
    # ORDER VERIFICATION
    # ========================================================

    def verify_order(self, drink_data):
        """
        Compare the customer's exact order with the
        player's completed drink.

        The new system uses exact matching.

        There is NO +/-20 tolerance anymore.
        """

        if not isinstance(
            drink_data,
            dict
        ):

            return False

        player_drink = drink_data.get(
            "drink"
        )

        player_temperature = drink_data.get(
            "temperature"
        )

        player_caffeine = drink_data.get(
            "caffeine"
        )

        player_sweetness = drink_data.get(
            "sweetness"
        )

        # ----------------------------------------------------
        # DRINK
        # ----------------------------------------------------

        drink_ok = (
            player_drink
            == self.order.drink
        )

        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        temperature_ok = (
            player_temperature
            == self.order.temperature
        )

        # ----------------------------------------------------
        # CAFFEINE
        # ----------------------------------------------------

        caffeine_ok = (
            player_caffeine
            == self.order.caffeine
        )

        # ----------------------------------------------------
        # SWEETNESS
        # ----------------------------------------------------

        sweetness_ok = (
            player_sweetness
            == self.order.sweetness
        )

        # ----------------------------------------------------
        # ALL FOUR MUST MATCH
        # ----------------------------------------------------

        return (
            drink_ok
            and temperature_ok
            and caffeine_ok
            and sweetness_ok
        )

    # ========================================================
    # ACCURACY DETAILS
    # ========================================================

    def get_order_accuracy(self, drink_data):
        """
        Return detailed accuracy information.

        This will later be moved into accuracy.py,
        but keeping it here temporarily makes the
        migration easier.
        """

        if not isinstance(
            drink_data,
            dict
        ):

            drink_data = {}

        drink_ok = (
            drink_data.get("drink")
            == self.order.drink
        )

        temperature_ok = (
            drink_data.get("temperature")
            == self.order.temperature
        )

        caffeine_ok = (
            drink_data.get("caffeine")
            == self.order.caffeine
        )

        sweetness_ok = (
            drink_data.get("sweetness")
            == self.order.sweetness
        )

        correct_count = sum(
            (
                drink_ok,
                temperature_ok,
                caffeine_ok,
                sweetness_ok,
            )
        )

        return {
            "drink": drink_ok,
            "temperature": temperature_ok,
            "caffeine": caffeine_ok,
            "sweetness": sweetness_ok,
            "correct": correct_count,
            "total": 4,
            "percentage": correct_count * 25,
        }

    # ========================================================
    # FINISHED
    # ========================================================

    def is_finished(self):
        """
        Returns True when the customer has completely
        left the screen.
        """

        return (
            self.state
            in (
                CustomerState.SERVED,
                CustomerState.LEAVING,
            )
            and
            self.current_y >= self.spawn_y
        )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self, screen):
        """
        Draw customer and relevant UI.
        """

        # ----------------------------------------------------
        # CUSTOMER SPRITE
        # ----------------------------------------------------

        screen.blit(
            self.image,
            self.rect
        )

        # ----------------------------------------------------
        # ACTIVE CUSTOMER UI
        # ----------------------------------------------------

        if self.state in (
            CustomerState.ORDERING,
            CustomerState.WAITING,
        ):

            self._draw_patience_bar(
                screen
            )

            self._draw_speech_bubble(
                screen
            )

        # ----------------------------------------------------
        # FEEDBACK
        # ----------------------------------------------------

        elif self.feedback_text:

            self._draw_feedback(
                screen
            )

    # ========================================================
    # PATIENCE BAR
    # ========================================================

    def _draw_patience_bar(self, screen):

        bar_w = sx(120)
        bar_h = sy(10)

        bar_x = (
            self.rect.centerx
            - (bar_w // 2)
        )

        bar_y = (
            self.rect.top
            - sy(20)
        )

        pygame.draw.rect(
            screen,
            (30, 30, 40),
            (
                bar_x,
                bar_y,
                bar_w,
                bar_h,
            ),
            border_radius=sy(4),
        )

        ratio = max(
            0.0,
            self.current_patience
            / self.max_patience
        )

        fill_w = int(
            (bar_w - 2)
            * ratio
        )

        if ratio > 0.5:

            color = (
                0,
                230,
                120
            )

        elif ratio > 0.25:

            color = (
                255,
                200,
                0
            )

        else:

            color = (
                255,
                50,
                80
            )

        if fill_w > 0:

            pygame.draw.rect(
                screen,
                color,
                (
                    bar_x + sx(1),
                    bar_y + sy(1),
                    fill_w,
                    bar_h - sy(2),
                ),
                border_radius=sy(3),
            )

        pygame.draw.rect(
            screen,
            (100, 110, 130),
            (
                bar_x,
                bar_y,
                bar_w,
                bar_h,
            ),
            width=1,
            border_radius=sy(4),
        )

    # ========================================================
    # SPEECH BUBBLE
    # ========================================================

    def _draw_speech_bubble(self, screen):

        txt_surf = self.font.render(
            self.dialogue,
            True,
            (0, 240, 255)
        )

        pad_x = sx(10)
        pad_y = sy(10)

        bubble_w = (
            txt_surf.get_width()
            + (pad_x * 2)
        )

        bubble_h = (
            txt_surf.get_height()
            + (pad_y * 2)
        )

        bubble_x = (
            self.rect.centerx
            - (bubble_w // 2)
        )

        bubble_y = (
            self.rect.top
            - sy(60)
        )

        bubble_rect = pygame.Rect(
            bubble_x,
            bubble_y,
            bubble_w,
            bubble_h
        )

        # ----------------------------------------------------
        # BACKGROUND
        # ----------------------------------------------------

        bg_surf = pygame.Surface(
            (
                bubble_w,
                bubble_h
            ),
            pygame.SRCALPHA
        )

        bg_surf.fill(
            (
                10,
                14,
                25,
                220
            )
        )

        screen.blit(
            bg_surf,
            bubble_rect.topleft
        )

        # ----------------------------------------------------
        # BORDER
        # ----------------------------------------------------

        pygame.draw.rect(
            screen,
            (0, 220, 255),
            bubble_rect,
            width=2,
            border_radius=sy(8)
        )

        # ----------------------------------------------------
        # POINTER
        # ----------------------------------------------------

        pointer_pts = [
            (
                self.rect.centerx - sx(6),
                bubble_y + bubble_h
            ),
            (
                self.rect.centerx + sx(6),
                bubble_y + bubble_h
            ),
            (
                self.rect.centerx,
                bubble_y + bubble_h + sy(8)
            ),
        ]

        pygame.draw.polygon(
            screen,
            (0, 220, 255),
            pointer_pts
        )

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        screen.blit(
            txt_surf,
            (
                bubble_x + pad_x,
                bubble_y + pad_y
            )
        )

    # ========================================================
    # FEEDBACK
    # ========================================================

    def _draw_feedback(self, screen):

        txt = self.font.render(
            self.feedback_text,
            True,
            self.feedback_color
        )

        screen.blit(
            txt,
            (
                self.rect.centerx
                - (txt.get_width() // 2),
                self.rect.top - sy(40)
            )
        )
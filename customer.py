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
    """Convert a 960x540 X coordinate to 1280x720."""
    return int(round(value * SCALE_X))


def sy(value):
    """Convert a 960x540 Y coordinate to 1280x720."""
    return int(round(value * SCALE_Y))


# ============================================================
# CUSTOMER STATES
# ============================================================

class CustomerState:

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

        return {
            "drink": self.drink,
            "temperature": self.temperature,
            "caffeine": self.caffeine,
            "sweetness": self.sweetness,
        }

    def __str__(self):

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

    def __init__(
        self,
        x=180,
        y_counter=500,
        current_level=1,
    ):

        # ----------------------------------------------------
        # POSITION
        # ----------------------------------------------------

        self.x = sx(x)
        self.y_counter = sy(y_counter)

        # ----------------------------------------------------
        # LEVEL
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
        # STATE
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

        self.rect.bottom = int(
            self.current_y
        )

        # ----------------------------------------------------
        # ORDER
        # ----------------------------------------------------

        self.order = self._generate_order()

        # ----------------------------------------------------
        # BACKWARD COMPATIBILITY
        # ----------------------------------------------------

        self.target_sweetness = (
            self._sweetness_to_number(
                self.order.sweetness
            )
        )

        self.target_caffeine = (
            self._caffeine_to_number(
                self.order.caffeine
            )
        )

        self.target_temperature = (
            self._temperature_to_number(
                self.order.temperature
            )
        )

        # ----------------------------------------------------
        # CUSTOMER PATIENCE
        # ----------------------------------------------------
        #
        # FINAL VALUE:
        #
        #       15 SECONDS
        #
        # This is the complete customer order timer.
        #

        self.max_patience = 15.0

        self.current_patience = (
            self.max_patience
        )

        # ----------------------------------------------------
        # QUICK SERVICE THRESHOLD
        # ----------------------------------------------------
        #
        # The player receives the speed bonus if they
        # serve the customer while at least 50% of the
        # customer's patience remains.
        #
        # This means:
        #
        # 15 seconds × 50% = 7.5 seconds
        #
        # Therefore a service completed with 7.5 seconds
        # or more remaining counts as "quick".
        #

        self.quick_service_ratio = 0.50

        # ----------------------------------------------------
        # FONTS
        # ----------------------------------------------------

        self.font_small = pygame.font.SysFont(
            "Consolas",
            sy(11),
            bold=True,
        )

        self.font_order = pygame.font.SysFont(
            "Consolas",
            sy(12),
            bold=True,
        )

        self.font_timer = pygame.font.SysFont(
            "Consolas",
            sy(11),
            bold=True,
        )

        self.font_feedback = pygame.font.SysFont(
            "Consolas",
            sy(18),
            bold=True,
        )

        # ----------------------------------------------------
        # DIALOGUE
        # ----------------------------------------------------

        self.dialogue = (
            self._generate_dialogue()
        )

        # ----------------------------------------------------
        # FEEDBACK
        # ----------------------------------------------------

        self.feedback_text = ""

        self.feedback_color = (
            0,
            255,
            150,
        )

    # ========================================================
    # ORDER GENERATION
    # ========================================================

    def _generate_order(self):

        unlocked_drinks = (
            get_unlocked_drinks(
                self.level
            )
        )

        if not unlocked_drinks:

            unlocked_drinks = (
                get_unlocked_drinks(1)
            )

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
    # NUMERIC COMPATIBILITY
    # ========================================================

    def _sweetness_to_number(
        self,
        sweetness,
    ):

        values = {
            "Less": 25,
            "Normal": 50,
            "Extra": 75,
        }

        return values.get(
            sweetness,
            50,
        )

    def _caffeine_to_number(
        self,
        caffeine,
    ):

        values = {
            "Low": 25,
            "Normal": 50,
            "High": 75,
        }

        return values.get(
            caffeine,
            50,
        )

    def _temperature_to_number(
        self,
        temperature,
    ):

        values = {
            "Cold": 25,
            "Normal": 50,
            "Hot": 75,
        }

        return values.get(
            temperature,
            50,
        )

    # ========================================================
    # LOAD CUSTOMER SPRITE
    # ========================================================

    def _load_sprite(
        self,
        ctype,
    ):

        filename = (
            f"{ctype}.png"
        )

        project_root = (
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        path = os.path.join(
            project_root,
            "assets",
            "customers",
            filename,
        )

        if os.path.exists(path):

            img = pygame.image.load(
                path
            ).convert_alpha()

        else:

            img = pygame.Surface(
                (
                    sx(180),
                    sy(220),
                ),
                pygame.SRCALPHA,
            )

            img.fill(
                (
                    100,
                    100,
                    150,
                )
            )

        return pygame.transform.scale(
            img,
            (
                sx(180),
                sy(220),
            ),
        )

    # ========================================================
    # DIALOGUE
    # ========================================================

    def _generate_dialogue(self):

        return (
            f"{self.order.drink} / "
            f"{self.order.temperature} / "
            f"{self.order.caffeine} Caffeine / "
            f"{self.order.sweetness} Sweet"
        )

    # ========================================================
    # PATIENCE RATIO
    # ========================================================

    def get_remaining_patience_ratio(self):

        if self.max_patience <= 0:

            return 0.0

        ratio = (
            self.current_patience
            / self.max_patience
        )

        return max(
            0.0,
            min(
                1.0,
                ratio,
            ),
        )

    # ========================================================
    # QUICK SERVICE
    # ========================================================

    def served_quickly(self):
        """
        Returns True if the customer was served while
        at least 50% of their patience remained.
        """

        if self.state != (
            CustomerState.SERVED
        ):

            return False

        return (
            self.get_remaining_patience_ratio()
            >= self.quick_service_ratio
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt,
    ):

        # ----------------------------------------------------
        # SPAWNING
        # ----------------------------------------------------

        if self.state == (
            CustomerState.SPAWNING
        ):

            if self.current_y > (
                self.y_counter
            ):

                self.current_y -= (
                    sy(120) * dt
                )

                if self.current_y <= (
                    self.y_counter
                ):

                    self.current_y = (
                        self.y_counter
                    )

                    self.state = (
                        CustomerState.ORDERING
                    )

            self.rect.bottom = int(
                self.current_y
            )

        # ----------------------------------------------------
        # ORDERING
        # ----------------------------------------------------

        elif self.state == (
            CustomerState.ORDERING
        ):

            self.state = (
                CustomerState.WAITING
            )

        # ----------------------------------------------------
        # WAITING
        # ----------------------------------------------------

        elif self.state == (
            CustomerState.WAITING
        ):

            self.current_patience -= dt

            if self.current_patience <= 0:

                self.current_patience = 0.0

                self.feedback_text = (
                    "TOO SLOW!"
                )

                self.feedback_color = (
                    255,
                    50,
                    80,
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

            if self.current_y < (
                self.spawn_y
            ):

                self.current_y += (
                    sy(150) * dt
                )

                if self.current_y > (
                    self.spawn_y
                ):

                    self.current_y = (
                        self.spawn_y
                    )

            self.rect.bottom = int(
                self.current_y
            )

    # ========================================================
    # SERVE DRINK
    # ========================================================

    def serve_drink(
        self,
        drink_data,
    ):

        if self.state != (
            CustomerState.WAITING
        ):

            return False

        success = self.verify_order(
            drink_data
        )

        if success:

            self.feedback_text = (
                "PERFECT!"
            )

            self.feedback_color = (
                0,
                255,
                150,
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
                80,
            )

            self.state = (
                CustomerState.LEAVING
            )

        return success

    # ========================================================
    # VERIFY ORDER
    # ========================================================

    def verify_order(
        self,
        drink_data,
    ):

        if not isinstance(
            drink_data,
            dict,
        ):

            return False

        player_drink = (
            drink_data.get("drink")
        )

        player_temperature = (
            drink_data.get("temperature")
        )

        player_caffeine = (
            drink_data.get("caffeine")
        )

        player_sweetness = (
            drink_data.get("sweetness")
        )

        drink_ok = (
            player_drink
            == self.order.drink
        )

        temperature_ok = (
            player_temperature
            == self.order.temperature
        )

        caffeine_ok = (
            player_caffeine
            == self.order.caffeine
        )

        sweetness_ok = (
            player_sweetness
            == self.order.sweetness
        )

        return (
            drink_ok
            and temperature_ok
            and caffeine_ok
            and sweetness_ok
        )

    # ========================================================
    # ORDER ACCURACY
    # ========================================================

    def get_order_accuracy(
        self,
        drink_data,
    ):

        if not isinstance(
            drink_data,
            dict,
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

        return (
            self.state
            in (
                CustomerState.SERVED,
                CustomerState.LEAVING,
            )
            and
            self.current_y >= (
                self.spawn_y
            )
        )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        screen,
    ):

        # ----------------------------------------------------
        # ORDER BUBBLE
        # ----------------------------------------------------

        if self.state in (
            CustomerState.ORDERING,
            CustomerState.WAITING,
        ):

            self._draw_speech_bubble(
                screen
            )

        # ----------------------------------------------------
        # CUSTOMER
        # ----------------------------------------------------

        screen.blit(
            self.image,
            self.rect,
        )

        # ----------------------------------------------------
        # FEEDBACK
        # ----------------------------------------------------

        if self.feedback_text:

            if self.state in (
                CustomerState.SERVED,
                CustomerState.LEAVING,
            ):

                self._draw_feedback(
                    screen
                )

    # ========================================================
    # ORDER BUBBLE
    # ========================================================

    def _draw_speech_bubble(
        self,
        screen,
    ):

        # ----------------------------------------------------
        # BUBBLE SIZE
        # ----------------------------------------------------

        bubble_w = sx(255)
        bubble_h = sy(142)

        bubble_x = (
            self.rect.centerx
            - bubble_w // 2
        )

        bubble_y = (
            self.rect.top
            - sy(158)
        )

        bubble_rect = pygame.Rect(
            bubble_x,
            bubble_y,
            bubble_w,
            bubble_h,
        )

        # Keep bubble inside screen.

        if bubble_rect.left < sx(12):

            bubble_rect.left = sx(12)

        if bubble_rect.right > (
            GAME_WIDTH - sx(12)
        ):

            bubble_rect.right = (
                GAME_WIDTH - sx(12)
            )

        # ----------------------------------------------------
        # SHADOW
        # ----------------------------------------------------

        shadow_rect = (
            bubble_rect.move(
                sx(3),
                sy(4),
            )
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0, 120),
            shadow_rect,
            border_radius=sy(12),
        )

        # ----------------------------------------------------
        # BACKGROUND
        # ----------------------------------------------------

        bg_surface = pygame.Surface(
            bubble_rect.size,
            pygame.SRCALPHA,
        )

        bg_surface.fill(
            (
                8,
                12,
                25,
                235,
            )
        )

        screen.blit(
            bg_surface,
            bubble_rect.topleft,
        )

        # ----------------------------------------------------
        # BORDER
        # ----------------------------------------------------

        pygame.draw.rect(
            screen,
            (0, 225, 255),
            bubble_rect,
            width=2,
            border_radius=sy(12),
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = self.font_order.render(
            "CUSTOMER ORDER",
            True,
            (255, 110, 220),
        )

        screen.blit(
            header,
            (
                bubble_rect.x + sx(12),
                bubble_rect.y + sy(8),
            ),
        )

        # ----------------------------------------------------
        # HEADER LINE
        # ----------------------------------------------------

        pygame.draw.line(
            screen,
            (55, 90, 120),
            (
                bubble_rect.x + sx(12),
                bubble_rect.y + sy(27),
            ),
            (
                bubble_rect.right - sx(12),
                bubble_rect.y + sy(27),
            ),
            width=1,
        )

        # ----------------------------------------------------
        # ORDER VALUES
        # ----------------------------------------------------

        order_lines = [
            (
                "DRINK",
                self.order.drink,
            ),
            (
                "TEMP",
                self.order.temperature,
            ),
            (
                "CAFFEINE",
                self.order.caffeine,
            ),
            (
                "SWEETNESS",
                self.order.sweetness,
            ),
        ]

        text_y = (
            bubble_rect.y + sy(34)
        )

        for label, value in order_lines:

            label_surface = (
                self.font_small.render(
                    label,
                    True,
                    (120, 145, 170),
                )
            )

            value_surface = (
                self.font_small.render(
                    str(value),
                    True,
                    (225, 245, 255),
                )
            )

            screen.blit(
                label_surface,
                (
                    bubble_rect.x + sx(12),
                    text_y,
                ),
            )

            screen.blit(
                value_surface,
                (
                    bubble_rect.x + sx(82),
                    text_y,
                ),
            )

            text_y += sy(17)

        # ----------------------------------------------------
        # PATIENCE LABEL
        # ----------------------------------------------------

        patience_y = (
            bubble_rect.bottom
            - sy(45)
        )

        patience_label = (
            self.font_small.render(
                "PATIENCE",
                True,
                (255, 200, 100),
            )
        )

        screen.blit(
            patience_label,
            (
                bubble_rect.x + sx(12),
                patience_y,
            ),
        )

        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------

        seconds_left = max(
            0.0,
            self.current_patience,
        )

        timer_text = (
            self.font_timer.render(
                f"{seconds_left:04.1f}s",
                True,
                self._get_patience_color(),
            )
        )

        screen.blit(
            timer_text,
            (
                bubble_rect.right - sx(58),
                patience_y,
            ),
        )

        # ----------------------------------------------------
        # TIMER BAR
        # ----------------------------------------------------

        bar_x = (
            bubble_rect.x + sx(12)
        )

        bar_y = (
            bubble_rect.bottom - sy(23)
        )

        bar_w = (
            bubble_rect.width - sx(24)
        )

        bar_h = sy(10)

        pygame.draw.rect(
            screen,
            (25, 30, 45),
            (
                bar_x,
                bar_y,
                bar_w,
                bar_h,
            ),
            border_radius=sy(5),
        )

        ratio = (
            self.get_remaining_patience_ratio()
        )

        fill_w = int(
            bar_w * ratio
        )

        if fill_w > 0:

            pygame.draw.rect(
                screen,
                self._get_patience_color(),
                (
                    bar_x,
                    bar_y,
                    fill_w,
                    bar_h,
                ),
                border_radius=sy(5),
            )

        pygame.draw.rect(
            screen,
            (80, 110, 140),
            (
                bar_x,
                bar_y,
                bar_w,
                bar_h,
            ),
            width=1,
            border_radius=sy(5),
        )

        # ----------------------------------------------------
        # POINTER
        # ----------------------------------------------------

        pointer_x = (
            self.rect.centerx
        )

        pointer_x = max(
            bubble_rect.left + sx(25),
            min(
                pointer_x,
                bubble_rect.right - sx(25),
            ),
        )

        pointer_top = (
            bubble_rect.bottom
        )

        pointer_points = [
            (
                pointer_x - sx(9),
                pointer_top,
            ),
            (
                pointer_x + sx(9),
                pointer_top,
            ),
            (
                pointer_x,
                pointer_top + sy(12),
            ),
        ]

        pygame.draw.polygon(
            screen,
            (8, 12, 25),
            pointer_points,
        )

        pygame.draw.line(
            screen,
            (0, 225, 255),
            (
                pointer_x - sx(9),
                pointer_top,
            ),
            (
                pointer_x,
                pointer_top + sy(12),
            ),
            width=2,
        )

        pygame.draw.line(
            screen,
            (0, 225, 255),
            (
                pointer_x,
                pointer_top + sy(12),
            ),
            (
                pointer_x + sx(9),
                pointer_top,
            ),
            width=2,
        )

    # ========================================================
    # PATIENCE COLOR
    # ========================================================

    def _get_patience_color(self):

        ratio = (
            self.get_remaining_patience_ratio()
        )

        if ratio > 0.50:

            return (
                0,
                235,
                150,
            )

        elif ratio > 0.25:

            return (
                255,
                205,
                70,
            )

        return (
            255,
            60,
            100,
        )

    # ========================================================
    # FEEDBACK
    # ========================================================

    def _draw_feedback(
        self,
        screen,
    ):

        txt = (
            self.font_feedback.render(
                self.feedback_text,
                True,
                self.feedback_color,
            )
        )

        feedback_x = (
            self.rect.centerx
            - txt.get_width() // 2
        )

        feedback_y = (
            self.rect.top - sy(42)
        )

        shadow = (
            self.font_feedback.render(
                self.feedback_text,
                True,
                (0, 0, 0),
            )
        )

        screen.blit(
            shadow,
            (
                feedback_x + sx(2),
                feedback_y + sy(2),
            ),
        )

        screen.blit(
            txt,
            (
                feedback_x,
                feedback_y,
            ),
        )
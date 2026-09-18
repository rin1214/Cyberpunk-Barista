import os
import random
import pygame

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
    return int(round(value * SCALE_X))


def sy(value):
    return int(round(value * SCALE_Y))


class CustomerState:
    SPAWNING = "spawning"
    ORDERING = "ordering"
    WAITING = "waiting"
    SERVED = "served"
    LEAVING = "leaving"


class Customer:
    """
    Manages FSM customer states, scaled sprite rendering, order generation,
    patience decay, slide animations, and cyberpunk speech UI.
    """

    def __init__(self, x=360, y_counter=405, current_level=1):
        self.x = sx(x)
        self.y_counter = sy(y_counter)  # Target Y coordinate behind counter
        self.level = current_level

        # Archetypes & Sprite
        self.customer_types = ["runner", "exec", "hacker"]
        self.current_type = random.choice(self.customer_types)
        self.image = self._load_sprite(self.current_type)

        # FSM State & Slide Animation Coordinates
        self.state = CustomerState.SPAWNING
        self.spawn_y = self.y_counter + sy(120)  # Off-screen starting position
        self.current_y = self.spawn_y

        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.bottom = int(self.current_y)

        # Target Recipe Generation
        self.target_sweetness = random.randint(20, 80)
        self.target_caffeine = random.randint(20, 80)
        self.target_temperature = random.randint(20, 80)

        # Patience Timer Settings
        self.max_patience = 20.0
        self.current_patience = self.max_patience

        # UI & Fonts
        self.font = pygame.font.SysFont("Consolas", sy(12), bold=True)
        self.dialogue = self._generate_dialogue()
        self.feedback_text = ""
        self.feedback_color = (0, 255, 150)

    def _load_sprite(self, ctype):
        """Loads character image asset and scales using resolution helper."""
        filename = f"{ctype}.png"
        project_root = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(project_root, "assets", "customers", filename)

        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
        else:
            img = pygame.Surface((sx(180), sy(220)), pygame.SRCALPHA)
            img.fill((100, 100, 150))

        return pygame.transform.scale(img, (sx(180), sy(220)))

    def _generate_dialogue(self):
        """Generates thematic customer order text based on parameters."""
        sweet_str = (
            "Extra Sweet"
            if self.target_sweetness >= 70
            else ("Unsweetened" if self.target_sweetness <= 30 else "Balanced")
        )
        caf_str = (
            "High Caffeine"
            if self.target_caffeine >= 70
            else ("Decaf" if self.target_caffeine <= 30 else "Standard Caf")
        )
        temp_str = (
            "Piping Hot"
            if self.target_temperature >= 70
            else ("Iced" if self.target_temperature <= 30 else "Warm")
        )
        return f"{caf_str} / {temp_str} / {sweet_str}"

    def update(self, dt):
        """FSM State Machine Engine & Movement Updates."""
        # 1. SPAWNING: Slide up into position behind counter
        if self.state == CustomerState.SPAWNING:
            if self.current_y > self.y_counter:
                self.current_y -= sy(120) * dt
                if self.current_y <= self.y_counter:
                    self.current_y = self.y_counter
                    self.state = CustomerState.ORDERING
            self.rect.bottom = int(self.current_y)

        # 2. ORDERING -> Transition immediately to WAITING loop
        elif self.state == CustomerState.ORDERING:
            self.state = CustomerState.WAITING

        # 3. WAITING: Patience decay
        elif self.state == CustomerState.WAITING:
            self.current_patience -= dt
            if self.current_patience <= 0:
                self.current_patience = 0.0
                self.feedback_text = "TOO SLOW!"
                self.feedback_color = (255, 50, 80)
                self.state = CustomerState.LEAVING

        # 4. SERVED / LEAVING: Slide down off counter
        elif self.state in (CustomerState.SERVED, CustomerState.LEAVING):
            if self.current_y < self.spawn_y:
                self.current_y += sy(150) * dt
            self.rect.bottom = int(self.current_y)

    def serve_drink(self, drink_data):
        """Evaluates drink accuracy and moves customer into terminal FSM state."""
        if self.state != CustomerState.WAITING:
            return False

        success = self.verify_order(drink_data)
        if success:
            self.feedback_text = "PERFECT!"
            self.feedback_color = (0, 255, 150)
            self.state = CustomerState.SERVED
        else:
            self.feedback_text = "WRONG DRINK!"
            self.feedback_color = (255, 50, 80)
            self.state = CustomerState.LEAVING

        return success

    def verify_order(self, drink_data):
        """Validates brewed drink against target parameters (+/- 20 tolerance)."""
        if isinstance(drink_data, dict):
            sweetness = drink_data.get("sweetness", 50)
            caffeine = drink_data.get("caffeine", 50)
            temperature = drink_data.get("temperature", 50)
        else:
            sweetness = getattr(drink_data, "sweetness", 50)
            caffeine = getattr(drink_data, "caffeine", 50)
            temperature = getattr(drink_data, "temperature", 50)

        tol = 20
        sweet_ok = abs(sweetness - self.target_sweetness) <= tol
        caf_ok = abs(caffeine - self.target_caffeine) <= tol
        temp_ok = abs(temperature - self.target_temperature) <= tol

        return sweet_ok and caf_ok and temp_ok

    def is_finished(self):
        """Returns True when customer has slid completely off-screen for cleanup."""
        return (
            self.state in (CustomerState.SERVED, CustomerState.LEAVING)
            and self.current_y >= self.spawn_y
        )

    def draw(self, screen):
        """Renders customer sprite, patience bar, and UI elements."""
        # 1. Render Customer Sprite
        screen.blit(self.image, self.rect)

        # 2. Render UI according to state
        if self.state in (CustomerState.ORDERING, CustomerState.WAITING):
            self._draw_patience_bar(screen)
            self._draw_speech_bubble(screen)
        elif self.feedback_text:
            self._draw_feedback(screen)

    def _draw_patience_bar(self, screen):
        """Draws dynamic patience bar above customer head."""
        bar_w = sx(120)
        bar_h = sy(10)
        bar_x = self.rect.centerx - (bar_w // 2)
        bar_y = self.rect.top - sy(20)

        pygame.draw.rect(
            screen, (30, 30, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=sy(4)
        )

        ratio = max(0.0, self.current_patience / self.max_patience)
        fill_w = int((bar_w - 2) * ratio)

        if ratio > 0.5:
            color = (0, 230, 120)
        elif ratio > 0.25:
            color = (255, 200, 0)
        else:
            color = (255, 50, 80)

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
            (bar_x, bar_y, bar_w, bar_h),
            width=1,
            border_radius=sy(4),
        )

    def _draw_speech_bubble(self, screen):
        """Draws cyberpunk order bubble with pointer arrow above head."""
        txt_surf = self.font.render(self.dialogue, True, (0, 240, 255))
        pad_x = sx(10)
        pad_y = sy(10)

        bubble_w = txt_surf.get_width() + (pad_x * 2)
        bubble_h = txt_surf.get_height() + (pad_y * 2)

        bubble_x = self.rect.centerx - (bubble_w // 2)
        bubble_y = self.rect.top - sy(60)

        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_w, bubble_h)

        # Semi-transparent dark background
        bg_surf = pygame.Surface((bubble_w, bubble_h), pygame.SRCALPHA)
        bg_surf.fill((10, 14, 25, 220))
        screen.blit(bg_surf, bubble_rect.topleft)

        # Neon Cyan Border
        pygame.draw.rect(
            screen, (0, 220, 255), bubble_rect, width=2, border_radius=sy(8)
        )

        # Pointer Triangle
        pointer_pts = [
            (self.rect.centerx - sx(6), bubble_y + bubble_h),
            (self.rect.centerx + sx(6), bubble_y + bubble_h),
            (self.rect.centerx, bubble_y + bubble_h + sy(8)),
        ]
        pygame.draw.polygon(screen, (0, 220, 255), pointer_pts)

        # Text render
        screen.blit(txt_surf, (bubble_x + pad_x, bubble_y + pad_y))

    def _draw_feedback(self, screen):
        """Renders popup feedback text (PERFECT / WRONG DRINK / TOO SLOW)."""
        txt = self.font.render(self.feedback_text, True, self.feedback_color)
        screen.blit(txt, (self.rect.centerx - (txt.get_width() // 2), self.rect.top - sy(40)))
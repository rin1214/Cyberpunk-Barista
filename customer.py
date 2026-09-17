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


class Customer:
    """
    Manages customer state, sprite rendering, order generation,
    patience decay, and speech UI.
    """

    def __init__(self, x=360, y_counter=405, current_level=1):
        self.x = sx(x)
        self.y_counter = sy(y_counter)  # Y-coordinate where the counter top rests
        self.level = current_level  # Stored for difficulty scaling if needed

        # Customer archetypes and asset paths
        self.customer_types = ["runner", "exec", "hacker"]
        self.current_type = random.choice(self.customer_types)

        # Load & Scale Sprite for Half-Body View
        self.image = self._load_sprite(self.current_type)

        # Anchor sprite bottom directly to the counter top
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.bottom = self.y_counter

        # Target Recipe Generation
        self.target_sweetness = random.randint(20, 80)
        self.target_caffeine = random.randint(20, 80)
        self.target_temperature = random.randint(20, 80)

        # Patience Timer Settings (in seconds)
        self.max_patience = 20.0
        self.current_patience = self.max_patience
        self.is_leaving = False

        # Speech Bubble UI Font
        self.font = pygame.font.SysFont("Consolas", sy(12), bold=True)
        self.dialogue = self._generate_dialogue()

    def _load_sprite(self, ctype):
        """Loads character image asset and scales to a close-up waist-up size."""
        filename = f"{ctype}.png"
        path = os.path.join("assets", "customers", filename)

        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
        else:
            # Fallback surface if image file is missing
            img = pygame.Surface((sx(180), sy(220)), pygame.SRCALPHA)
            img.fill((100, 100, 150))

        # Scale up half-body sprite so character feels close behind the counter
        return pygame.transform.scale(img,(sx(180), sy(220)))

    def _generate_dialogue(self):
        """Generates thematic customer order text based on parameters."""
        sweet_str = "Sweet" if self.target_sweetness > 50 else "Bitter"
        caf_str = (
            "High Caffeine" if self.target_caffeine > 50 else "Low Caffeine"
        )
        temp_str = "Hot" if self.target_temperature > 50 else "Cold"
        return f"{caf_str} / {temp_str} / {sweet_str}"

    def update(self, dt):
        """Decays customer patience over time."""
        if not self.is_leaving:
            self.current_patience -= dt
            if self.current_patience <= 0:
                self.current_patience = 0.0
                self.is_leaving = True

    def is_patience_expired(self):
        """Returns True if patience timer reaches zero."""
        return self.current_patience <= 0

    def draw(self, screen):
        """Renders customer sprite, speech bubble, and patience bar."""
        # 1. Render Customer Sprite
        screen.blit(self.image, self.rect)

        # 2. Render Patience Bar (Above Head)
        self._draw_patience_bar(screen)

        # 3. Render Speech Bubble (Above Head / Bar)
        self._draw_speech_bubble(screen)

    def _draw_patience_bar(self, screen):
        """Draws a dynamic patience progress bar above customer."""
        bar_w = sx(120)
        bar_h = sy(10)
        bar_x = self.rect.centerx - (bar_w // 2)
        bar_y = self.rect.top - sy(20)

        # Background track
        pygame.draw.rect(
            screen, (30, 30, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=4
        )

        # Dynamic fill amount & color (Green -> Yellow -> Red)
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
                    bar_h - sy(2)),
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
        """Draws cyberpunk order bubble above customer head."""
        txt_surf = self.font.render(self.dialogue, True, (0, 240, 255))
        pad_x = sx(10)
        pad_y = sy(10)

        bubble_w = txt_surf.get_width() + (pad_x * 2)
        bubble_h = txt_surf.get_height() + (pad_y * 2)

        bubble_x = self.rect.centerx - (bubble_w // 2)
        bubble_y = self.rect.top - (sy(60))

        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_w, bubble_h)

        # Semi-transparent dark background
        bg_surf = pygame.Surface((bubble_w, bubble_h), pygame.SRCALPHA)
        bg_surf.fill((10, 14, 25, 220))
        screen.blit(bg_surf, bubble_rect.topleft)

        # Neon Cyan Border
        pygame.draw.rect(
            screen, (0, 220, 255), bubble_rect, width=2, border_radius=sy(8)
        )

        # Speech bubble pointer pointing down towards head
        pointer_pts = [
            (self.rect.centerx - (sx(6)), bubble_y + bubble_h),
            (self.rect.centerx + sx(6), bubble_y + bubble_h),
            (self.rect.centerx, bubble_y + bubble_h + sy(8)),
        ]
        pygame.draw.polygon(screen, (0, 220, 255), pointer_pts)

        # Text render
        screen.blit(txt_surf, (bubble_x + pad_x, bubble_y + pad_y))

    def verify_order(self, drink_data):
        """
        Validates brewed drink against target requirements (tolerance threshold +/- 20).
        Accepts dictionary or Drink object.
        """
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
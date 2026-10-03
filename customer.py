import os
import random
import pygame
from drink import (
    TEMPERATURE_OPTIONS,
    CAFFEINE_OPTIONS,
    SWEETNESS_OPTIONS,
    get_unlocked_drinks,
)

# Track last drink ordered so the next customer never repeats the same drink
_last_drink: str | None = None

# 1280x720 Game Resolution Scaling Helpers
GAME_WIDTH = 1280
GAME_HEIGHT = 720
BASE_WIDTH = 960
BASE_HEIGHT = 540
SCALE_X = GAME_WIDTH / BASE_WIDTH
SCALE_Y = GAME_HEIGHT / BASE_HEIGHT

# Unified Sprite Size Constants for Synchronization
SPRITE_BASE_WIDTH = 180
SPRITE_BASE_HEIGHT = 220

# What the customer says after being served (keyed by how many of the 4 parts were right).
REACTION_LINES = {
    0: ("I can't stand around all day. I'm out of here!", (255, 50, 80)),
    1: ("This tastes awful. I'm leaving a bad review.", (255, 50, 80)),
    2: ("You got half of it wrong. Pay attention next time.", (255, 170, 60)),
    3: ("Great work! Just missing that final touch.", (0, 225, 255)),
    4: ("Absolute perfection. Keep up the great work!", (0, 255, 150)),
}
REACTION_SECONDS = 2.5   # how long the dialogue stays on screen
LEAVE_SECONDS = 2.5      # how long the slow walk-away / fade-out takes
# Said when the customer runs out of patience (same bubble + timer as the others)
TIMEOUT_REACTION = ("Too slow! I'm not waiting any longer.", (255, 50, 80))

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

class CustomerOrder:
    def __init__(self, drink, temperature, caffeine, sweetness):
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
        return f"{self.drink} | {self.temperature} | {self.caffeine} Caffeine | {self.sweetness} Sweet"

class Customer:
    # Full archetype profile 
    ARCHETYPE_DETAILS = {
        "runner": {"patience": 35.0, "pay_mult": 1.0, "weight": 50},
        "exec": {"patience": 35.0, "pay_mult": 1.8, "weight": 30},
        "hacker": {"patience": 35.0, "pay_mult": 1.3, "weight": 20},
        "drone_pilot": {"patience": 30.0, "pay_mult": 1.4, "weight": 15},
        "corp_spy": {"patience": 18.0, "pay_mult": 2.5, "weight": 8},  # Rare, low patience, high pay
        "cyberpunk_cat": {"patience": 18.0, "pay_mult": 3.0, "weight": 4},  # Rare, low patience, highest pay
    }

    def __init__(self, x=360, y_counter=405, current_level=1):
        self.x = sx(x)
        self.y_counter = sy(y_counter)
        self.level = current_level
        
        # Level-based customer pools (Level 1: runner/exec/hacker, Level 2: +drone_pilot, Level 3: +corp_spy & cyberpunk_cat)
        if self.level == 1:
            self.customer_pool = ["runner", "exec", "hacker"]
            self.pool_weights = [50, 30, 20]
        elif self.level == 2:
            self.customer_pool = ["runner", "exec", "hacker", "drone_pilot"]
            self.pool_weights = [40, 25, 20, 15]
        else:
            self.customer_pool = ["runner", "exec", "hacker", "drone_pilot", "corp_spy", "cyberpunk_cat"]
            self.pool_weights = [30, 20, 18, 16, 10, 6]
            
        self.current_type = random.choices(self.customer_pool, weights=self.pool_weights, k=1)[0]
        
        # Pull custom archetype multipliers
        archetype_info = self.ARCHETYPE_DETAILS.get(self.current_type, {"patience": 30.0, "pay_mult": 1.0})
        self.pay_multiplier = archetype_info["pay_mult"]
        
        # Load both front (station view) and back (order view) synchronized sprites
        self.image = self._load_sprite(self.current_type, back_view=False)
        self.back_image = self._load_sprite(self.current_type, back_view=True)
        
        self.state = CustomerState.SPAWNING
        
        self.spawn_y = self.y_counter + sy(120)
        self.current_y = self.spawn_y
        
        # Synchronized rect positioning using exact base dimensions
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.bottom = int(self.current_y)
        
        self.order = self._generate_order()
        
        # Legacy compatibility values 
        self.target_sweetness = self._sweetness_to_number(self.order.sweetness)
        self.target_caffeine = self._caffeine_to_number(self.order.caffeine)
        self.target_temperature = self._temperature_to_number(self.order.temperature)
        
        # Patience is determined by the customer archetype only.
        self.max_patience = archetype_info["patience"]
        self.current_patience = self.max_patience
        
        # UI fonts and feedback setup
        self.font_small = pygame.font.SysFont("Consolas", sy(11), bold=True)
        self.font_order = pygame.font.SysFont("Consolas", sy(12), bold=True)
        self.font_timer = pygame.font.SysFont("Consolas", sy(11), bold=True)
        self.font_feedback = pygame.font.SysFont("Consolas", sy(18), bold=True)
        self.font_reaction = pygame.font.SysFont("Consolas", sy(13), bold=True)
        self.font = self.font_small
        
        self.quick_service_ratio = 0.50
        self.dialogue = self._generate_dialogue()
        self.feedback_text = ""
        self.feedback_color = (0, 255, 150)

        # Reaction dialogue + slow leave (used after a drink is served with 1-4 correct)
        self.reaction_text = ""
        self.reaction_color = (0, 225, 255)
        self.reaction_timer = 0.0
        self.leave_progress = 0.0
        self.leave_start_y = self.current_y

    def _generate_order(self):
        global _last_drink
        unlocked_drinks = get_unlocked_drinks(self.level)
        if not unlocked_drinks:
            unlocked_drinks = get_unlocked_drinks(1)

        # Exclude the last drink so no two customers in a row order the same thing
        pool = [d for d in unlocked_drinks if d != _last_drink]
        if not pool:   # only one drink available – can't avoid repeating
            pool = unlocked_drinks

        chosen = random.choice(pool)
        _last_drink = chosen

        return CustomerOrder(
            drink=chosen,
            temperature=random.choice(TEMPERATURE_OPTIONS),
            caffeine=random.choice(CAFFEINE_OPTIONS),
            sweetness=random.choice(SWEETNESS_OPTIONS),
        )

    def _sweetness_to_number(self, sweetness):
        values = {"Less": 25, "Normal": 50, "Extra": 75}
        return values.get(sweetness, 50)

    def _caffeine_to_number(self, caffeine):
        values = {"Low": 25, "Normal": 50, "High": 75}
        return values.get(caffeine, 50)

    def _temperature_to_number(self, temperature):
        values = {"Cold": 25, "Normal": 50, "Hot": 75}
        return values.get(temperature, 50)

    def _load_sprite(self, ctype, back_view=False):
        """Loads and strictly synchronizes all front/back character sprites to a uniform scale resolution."""
        suffix = "back" if back_view else ""
        filenames = [f"{ctype}{suffix}.png", f"{ctype}_{suffix}.png" if suffix else f"{ctype}_front.png"]
        
        project_root = os.path.dirname(os.path.abspath(__file__))
        path = None
        for fname in filenames:
            test_path = os.path.join(project_root, "assets", "customers", fname)
            if os.path.exists(test_path):
                path = test_path
                break
                
        # Universal fallback if image file is missing
        if not path or not os.path.exists(path):
            img = pygame.Surface((sx(SPRITE_BASE_WIDTH), sy(SPRITE_BASE_HEIGHT)), pygame.SRCALPHA)
            base_color = (255, 0, 110) if "spy" in ctype or "cat" in ctype else (0, 240, 255)
            if back_view:
                base_color = tuple(max(0, c - 40) for c in base_color)
            img.fill(base_color)
        else:
            img = pygame.image.load(path).convert_alpha()
            
        return pygame.transform.smoothscale(img, (sx(SPRITE_BASE_WIDTH), sy(SPRITE_BASE_HEIGHT)))

    def _generate_dialogue(self):
        return f"{self.order.drink} / {self.order.temperature} / {self.order.caffeine} Caffeine / {self.order.sweetness} Sweet"

    def update(self, dt):
        if self.state == CustomerState.SPAWNING:
            if self.current_y > self.y_counter:
                self.current_y -= sy(120) * dt
                if self.current_y <= self.y_counter:
                    self.current_y = self.y_counter
                    self.state = CustomerState.ORDERING
            self.rect.bottom = int(self.current_y)
            
        elif self.state == CustomerState.ORDERING:
            self.state = CustomerState.WAITING
            
        elif self.state == CustomerState.WAITING:
            self.current_patience -= dt
            if self.current_patience <= 0:
                self.current_patience = 0.0
                # Show a proper dialogue bubble instead of a quick "TOO SLOW!" ghost exit
                self.feedback_text = ""
                self.reaction_text, self.reaction_color = TIMEOUT_REACTION
                self.reaction_timer = REACTION_SECONDS
                self.leave_progress = 0.0
                self.leave_start_y = self.current_y
                self.state = CustomerState.LEAVING
                
        elif self.state in (CustomerState.SERVED, CustomerState.LEAVING):
            if self.reaction_text:
                if self.reaction_timer > 0:
                    # Customer stays and talks first
                    self.reaction_timer = max(0.0, self.reaction_timer - dt)
                elif self.leave_progress < 1.0:
                    # Then slowly walks away while fading out
                    self.leave_progress = min(1.0, self.leave_progress + dt / LEAVE_SECONDS)
                    self.current_y = self.leave_start_y + (self.spawn_y - self.leave_start_y) * self.leave_progress
            elif self.current_y < self.spawn_y:
                self.current_y += sy(150) * dt
            self.rect.bottom = int(self.current_y)

    def serve_drink(self, drink_data, correct_count=None):
        if self.state != CustomerState.WAITING:
            return False
            
        success = self.verify_order(drink_data)

        if correct_count is None:
            correct_count = self.get_order_accuracy(drink_data)["correct"]
        try:
            reaction = REACTION_LINES.get(int(correct_count))
        except (TypeError, ValueError):
            reaction = None
        if reaction:
            # 0-4 correct: say a short line for 2.5s, then leave slowly
            self.reaction_text, self.reaction_color = reaction
            self.reaction_timer = REACTION_SECONDS
            self.leave_progress = 0.0
            self.leave_start_y = self.current_y
            self.feedback_text = ""
            self.state = CustomerState.SERVED if success else CustomerState.LEAVING
            return success

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
        if not isinstance(drink_data, dict):
            return False
            
        drink_ok = drink_data.get("drink") == self.order.drink
        temperature_ok = drink_data.get("temperature") == self.order.temperature
        caffeine_ok = drink_data.get("caffeine") == self.order.caffeine
        sweetness_ok = drink_data.get("sweetness") == self.order.sweetness
        
        return drink_ok and temperature_ok and caffeine_ok and sweetness_ok

    def get_order_accuracy(self, drink_data):
        if not isinstance(drink_data, dict):
            drink_data = {}
            
        drink_ok = drink_data.get("drink") == self.order.drink
        temperature_ok = drink_data.get("temperature") == self.order.temperature
        caffeine_ok = drink_data.get("caffeine") == self.order.caffeine
        sweetness_ok = drink_data.get("sweetness") == self.order.sweetness
        
        correct_count = sum((drink_ok, temperature_ok, caffeine_ok, sweetness_ok))
        return {
            "drink": drink_ok,
            "temperature": temperature_ok,
            "caffeine": caffeine_ok,
            "sweetness": sweetness_ok,
            "correct": correct_count,
            "total": 4,
            "percentage": correct_count * 25,
        }

    def is_finished(self):
        if self.reaction_text:
            return (
                self.state in (CustomerState.SERVED, CustomerState.LEAVING)
                and self.reaction_timer <= 0
                and self.leave_progress >= 1.0
            )
        return (
            self.state in (CustomerState.SERVED, CustomerState.LEAVING)
            and self.current_y >= self.spawn_y
        )

    def get_remaining_patience_ratio(self):
        if self.max_patience <= 0:
            return 0.0
        ratio = self.current_patience / self.max_patience
        return max(0.0, min(1.0, ratio))

    def served_quickly(self):
        if self.state not in (CustomerState.WAITING, CustomerState.SERVED):
            return False
        return self.get_remaining_patience_ratio() >= self.quick_service_ratio

    def _get_patience_color(self):
        ratio = self.get_remaining_patience_ratio()
        if ratio > 0.50:
            return (0, 235, 150)
        if ratio > 0.25:
            return (255, 205, 70)
        return (255, 60, 100)

    def draw(self, screen, view_mode="front"):
        current_sprite = self.back_image if view_mode == "back" else self.image
        
        if self.state in (CustomerState.ORDERING, CustomerState.WAITING):
            self._draw_speech_bubble(screen)
            
        # Fade the customer out while they walk away after their reaction
        alpha = 255
        if self.reaction_text and self.leave_progress > 0:
            alpha = int(255 * (1.0 - self.leave_progress))
        if alpha < 255:
            faded = current_sprite.copy()
            faded.set_alpha(max(0, alpha))
            screen.blit(faded, self.rect)
        else:
            screen.blit(current_sprite, self.rect)
        
        if self.feedback_text and self.state in (CustomerState.SERVED, CustomerState.LEAVING):
            self._draw_feedback(screen)

        if (
            self.reaction_text
            and self.reaction_timer > 0
            and self.state in (CustomerState.SERVED, CustomerState.LEAVING)
        ):
            self._draw_reaction_bubble(screen)

    def _wrap_text(self, text, font, max_width):
        lines, line = [], ""
        for word in text.split():
            test = (line + " " + word).strip()
            if font.size(test)[0] <= max_width or not line:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def _draw_reaction_bubble(self, screen):
        pad_x, pad_y = sx(12), sy(9)
        max_text_w = sx(230)
        lines = self._wrap_text(self.reaction_text, self.font_reaction, max_text_w)
        line_h = self.font_reaction.get_linesize()
        text_w = max(self.font_reaction.size(line)[0] for line in lines)
        bubble_w = text_w + pad_x * 2
        bubble_h = line_h * len(lines) + pad_y * 2

        bubble_rect = pygame.Rect(0, 0, bubble_w, bubble_h)
        bubble_rect.centerx = self.rect.centerx
        bubble_rect.bottom = self.rect.top - sy(16)
        bubble_rect.left = max(sx(12), bubble_rect.left)
        bubble_rect.right = min(GAME_WIDTH - sx(12), bubble_rect.right)
        bubble_rect.top = max(sy(10), bubble_rect.top)

        bg_surface = pygame.Surface(bubble_rect.size, pygame.SRCALPHA)
        bg_surface.fill((8, 12, 25, 235))
        screen.blit(bg_surface, bubble_rect.topleft)
        pygame.draw.rect(screen, self.reaction_color, bubble_rect, width=2, border_radius=sy(10))

        text_y = bubble_rect.y + pad_y
        for line in lines:
            surface = self.font_reaction.render(line, True, (235, 245, 255))
            screen.blit(surface, (bubble_rect.x + pad_x, text_y))
            text_y += line_h

        pointer_x = max(bubble_rect.left + sx(20), min(self.rect.centerx, bubble_rect.right - sx(20)))
        pointer_top = bubble_rect.bottom
        points = [
            (pointer_x - sx(8), pointer_top),
            (pointer_x + sx(8), pointer_top),
            (pointer_x, pointer_top + sy(11)),
        ]
        pygame.draw.polygon(screen, (8, 12, 25), points)
        pygame.draw.line(screen, self.reaction_color, (pointer_x - sx(8), pointer_top), (pointer_x, pointer_top + sy(11)), width=2)
        pygame.draw.line(screen, self.reaction_color, (pointer_x, pointer_top + sy(11)), (pointer_x + sx(8), pointer_top), width=2)

    def _draw_speech_bubble(self, screen):
        bubble_w = sx(255)
        bubble_h = sy(142)
        bubble_x = self.rect.centerx - (bubble_w // 2)
        bubble_y = self.rect.top - sy(158)
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_w, bubble_h)
        
        if bubble_rect.left < sx(12):
            bubble_rect.left = sx(12)
        if bubble_rect.right > GAME_WIDTH - sx(12):
            bubble_rect.right = GAME_WIDTH - sx(12)
            
        shadow_rect = bubble_rect.move(sx(3), sy(4))
        shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 120))
        screen.blit(shadow_surface, shadow_rect.topleft)
        
        bg_surface = pygame.Surface(bubble_rect.size, pygame.SRCALPHA)
        bg_surface.fill((8, 12, 25, 235))
        screen.blit(bg_surface, bubble_rect.topleft)
        
        pygame.draw.rect(screen, (0, 225, 255), bubble_rect, width=2, border_radius=sy(12))
        
        header = self.font_order.render(f"CUSTOMER: {self.current_type.upper()}", True, (255, 110, 220))
        screen.blit(header, (bubble_rect.x + sx(12), bubble_rect.y + sy(8)))
        pygame.draw.line(screen, (55, 90, 120), (bubble_rect.x + sx(12), bubble_rect.y + sy(27)), (bubble_rect.right - sx(12), bubble_rect.y + sy(27)), width=1)
        
        # Show clues not straight away drinks name
        drink_profiles = {
            "Neon Latte": "smooth coffee + creamy",
            "Milkyway": "creamy + chocolate",
            "Void Chai": "warm + spiced",
            "Cyber Fuel": "powerful + energy boost",
            "Hologram Frappe": "cold + colourful + fun",
            "Pixel Lemint": "cool + refreshing + minty",
            "Stardust Matcha": "earthy + smooth + calming",
            "Caramel Byte": "rich + sweet + caramel",
            "Meteorite": "cold + strong futuristic kick",
        }

        hint = drink_profiles.get(
            self.order.drink,
            "something that fits the customer's mood"
        )

        order_lines = [
            ("HINT", hint),
            ("TEMP", self.order.temperature),
            ("CAFFEINE", self.order.caffeine),
            ("SWEETNESS", self.order.sweetness),
        ]

        text_y = bubble_rect.y + sy(34)
        for label, value in order_lines:
            label_surface = self.font_small.render(label, True, (120, 145, 170))
            value_surface = self.font_small.render(str(value), True, (225, 245, 255))
            screen.blit(label_surface, (bubble_rect.x + sx(12), text_y))
            screen.blit(value_surface, (bubble_rect.x + sx(82), text_y))
            text_y += sy(17)
            
        patience_y = bubble_rect.bottom - sy(45)
        patience_label = self.font_small.render("PATIENCE", True, (255, 200, 100))
        screen.blit(patience_label, (bubble_rect.x + sx(12), patience_y))
        
        seconds_left = max(0.0, self.current_patience)
        timer_surface = self.font_timer.render(f"{seconds_left:04.1f}s", True, self._get_patience_color())
        screen.blit(timer_surface, (bubble_rect.right - sx(58), patience_y))
        
        bar_x = bubble_rect.x + sx(12)
        bar_y = bubble_rect.bottom - sy(23)
        bar_w = bubble_rect.width - sx(24)
        bar_h = sy(10)
        
        pygame.draw.rect(screen, (25, 30, 45), (bar_x, bar_y, bar_w, bar_h), border_radius=sy(5))
        ratio = self.get_remaining_patience_ratio()
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, self._get_patience_color(), (bar_x, bar_y, fill_w, bar_h), border_radius=sy(5))
        pygame.draw.rect(screen, (80, 110, 140), (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=sy(5))
        
        pointer_x = max(bubble_rect.left + sx(25), min(self.rect.centerx, bubble_rect.right - sx(25)))
        pointer_top = bubble_rect.bottom
        pointer_points = [
            (pointer_x - sx(9), pointer_top),
            (pointer_x + sx(9), pointer_top),
            (pointer_x, pointer_top + sy(12)),
        ]
        pygame.draw.polygon(screen, (8, 12, 25), pointer_points)
        pygame.draw.line(screen, (0, 225, 255), (pointer_x - sx(9), pointer_top), (pointer_x, pointer_top + sy(12)), width=2)
        pygame.draw.line(screen, (0, 225, 255), (pointer_x, pointer_top + sy(12)), (pointer_x + sx(9), pointer_top), width=2)

    def _draw_feedback(self, screen):
        txt = self.font_feedback.render(self.feedback_text, True, self.feedback_color)
        screen.blit(txt, (self.rect.centerx - (txt.get_width() // 2), self.rect.top - sy(40)))
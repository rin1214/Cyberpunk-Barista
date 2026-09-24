import os
import random
import pygame
from drink import (
    TEMPERATURE_OPTIONS,
    CAFFEINE_OPTIONS,
    SWEETNESS_OPTIONS,
    get_unlocked_drinks,
)

# 1280x720 Game Resolution Scaling Helpers
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
    def __init__(self, x=360, y_counter=405, current_level=1):
        self.x = sx(x)
        self.y_counter = sy(y_counter)
        self.level = current_level
        
        self.customer_types = ["runner", "exec", "hacker"]
        self.current_type = random.choice(self.customer_types)
        self.image = self._load_sprite(self.current_type)
        
        self.state = CustomerState.SPAWNING
        
        self.spawn_y = self.y_counter + sy(120)
        self.current_y = self.spawn_y
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.bottom = int(self.current_y)
        
        self.order = self._generate_order()
        
        # Legacy compatibility values for older systems
        self.target_sweetness = self._sweetness_to_number(self.order.sweetness)
        self.target_caffeine = self._caffeine_to_number(self.order.caffeine)
        self.target_temperature = self._temperature_to_number(self.order.temperature)
        
        self.max_patience = 18.0
        self.current_patience = self.max_patience
        
        # UI fonts and feedback setup
        self.font_small = pygame.font.SysFont("Consolas", sy(11), bold=True)
        self.font_order = pygame.font.SysFont("Consolas", sy(12), bold=True)
        self.font_timer = pygame.font.SysFont("Consolas", sy(11), bold=True)
        self.font_feedback = pygame.font.SysFont("Consolas", sy(18), bold=True)
        self.font = self.font_small
        
        self.quick_service_ratio = 0.50
        self.dialogue = self._generate_dialogue()
        self.feedback_text = ""
        self.feedback_color = (0, 255, 150)

    def _generate_order(self):
        unlocked_drinks = get_unlocked_drinks(self.level)
        if not unlocked_drinks:
            unlocked_drinks = get_unlocked_drinks(1)
        
        return CustomerOrder(
            drink=random.choice(unlocked_drinks),
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

    def _load_sprite(self, ctype):
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
                self.feedback_text = "TOO SLOW!"
                self.feedback_color = (255, 50, 80)
                self.state = CustomerState.LEAVING
                
        elif self.state in (CustomerState.SERVED, CustomerState.LEAVING):
            if self.current_y < self.spawn_y:
                self.current_y += sy(150) * dt
            self.rect.bottom = int(self.current_y)

    def serve_drink(self, drink_data):
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

    def draw(self, screen):
        if self.state in (CustomerState.ORDERING, CustomerState.WAITING):
            self._draw_speech_bubble(screen)
            
        screen.blit(self.image, self.rect)
        
        if self.feedback_text and self.state in (CustomerState.SERVED, CustomerState.LEAVING):
            self._draw_feedback(screen)

    def _draw_patience_bar(self, screen):
        bar_w = sx(120)
        bar_h = sy(10)
        bar_x = self.rect.centerx - (bar_w // 2)
        bar_y = self.rect.top - sy(20)
        
        pygame.draw.rect(screen, (30, 30, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=sy(4))
        ratio = self.get_remaining_patience_ratio()
        fill_w = int((bar_w - 2) * ratio)
        
        if fill_w > 0:
            pygame.draw.rect(screen, self._get_patience_color(), (bar_x + sx(1), bar_y + sy(1), fill_w, bar_h - sy(2)), border_radius=sy(3))
        pygame.draw.rect(screen, (100, 110, 130), (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=sy(4))

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
            
        # Shadow
        shadow_rect = bubble_rect.move(sx(3), sy(4))
        shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 120))
        screen.blit(shadow_surface, shadow_rect.topleft)
        
        # Background
        bg_surface = pygame.Surface(bubble_rect.size, pygame.SRCALPHA)
        bg_surface.fill((8, 12, 25, 235))
        screen.blit(bg_surface, bubble_rect.topleft)
        
        # Border
        pygame.draw.rect(screen, (0, 225, 255), bubble_rect, width=2, border_radius=sy(12))
        
        # Header
        header = self.font_order.render("CUSTOMER ORDER", True, (255, 110, 220))
        screen.blit(header, (bubble_rect.x + sx(12), bubble_rect.y + sy(8)))
        pygame.draw.line(screen, (55, 90, 120), (bubble_rect.x + sx(12), bubble_rect.y + sy(27)), (bubble_rect.right - sx(12), bubble_rect.y + sy(27)), width=1)
        
        # Order Details Text Loop
        order_lines = [
            ("DRINK", self.order.drink),
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
            
        # Patience Section
        patience_y = bubble_rect.bottom - sy(45)
        patience_label = self.font_small.render("PATIENCE", True, (255, 200, 100))
        screen.blit(patience_label, (bubble_rect.x + sx(12), patience_y))
        
        seconds_left = max(0.0, self.current_patience)
        timer_surface = self.font_timer.render(f"{seconds_left:04.1f}s", True, self._get_patience_color())
        screen.blit(timer_surface, (bubble_rect.right - sx(58), patience_y))
        
        # Patience Bar UI
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
        
        # Speech Pointer Triangle
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
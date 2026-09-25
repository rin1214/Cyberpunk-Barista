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
from game_state import (
    MixingGameState,
    GameState,
)
from mini_challenges import MiniChallenge

class MixingStation:
    WIDTH = 1280
    HEIGHT = 720

    CYAN = (75, 225, 255)
    CYAN_LIGHT = (165, 245, 255)
    PINK = (255, 80, 190)
    PINK_LIGHT = (255, 165, 225)
    PURPLE = (185, 105, 255)
    WHITE = (245, 248, 255)
    SOFT_WHITE = (215, 222, 240)
    MUTED = (125, 140, 170)
    YELLOW = (255, 220, 100)
    GREEN = (90, 235, 165)
    LOCKED = (65, 70, 95)

    PANEL = (7, 12, 30, 175)
    BUTTON = (9, 17, 38, 185)
    BUTTON_SELECTED = (65, 15, 65, 205)

    def __init__(
        self,
        drink=None,
        level=1,
        progression=None,
        rewards=None,
        economy=None,
    ):
        self.drink = drink
        self.player_drink = PlayerDrink()
        self.game_state = MixingGameState()
        self.progression = progression
        self.rewards = rewards
        self.economy = economy
        self.level = max(1, int(level))
        self.customer_order = None
        self.served = False
        self.challenge = MiniChallenge()
        self.liquid_unlocked = False
        self.assembly_phase = "empty"
        self.assembly_started = 0.0
        self.ingredient_drop_start = 0.0

        self.map_requested = False
        self.leaderboard_requested = False

        self.last_xp_change = 0
        self.last_credit_change = 0
        self.reward_feedback_until = 0.0

        self._last_time = time.monotonic()

        self.slider_positions = {
            "temperature": 0.08,
            "caffeine": 0.50,
            "sweetness": 0.92,
        }
        self.slider_directions = {
            "temperature": 1.0,
            "caffeine": -1.0,
            "sweetness": 1.0,
        }
        self.slider_speeds = {
            "temperature": 0.62,
            "caffeine": 0.74,
            "sweetness": 0.86,
        }
        self.slider_locked = {
            "temperature": False,
            "caffeine": False,
            "sweetness": False,
        }
        self.slider_results = {
            "temperature": None,
            "caffeine": None,
            "sweetness": None,
        }
        self.slider_feedback = {
            "temperature": "CLICK",
            "caffeine": "CLICK",
            "sweetness": "CLICK",
        }

        self.blend_start_time = 0.0
        self.blend_duration = 1.8
        self.blender_angle = 0.0
        self.blender_pulse = 0.0

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.drink_dir = os.path.join(self.base_dir, "assets", "mahirah", "drinks")
        self.font_dir = os.path.join(self.base_dir, "assets", "fonts")

        self._create_fonts()
        self.drink_images = {}
        self._load_drink_images()
        self._create_layout()
        self._attach_legacy_bridge()

    def _find_font(self, preferred_names):
        if os.path.isdir(self.font_dir):
            all_files = []
            for root, _, files in os.walk(self.font_dir):
                for filename in files:
                    if filename.lower().endswith((".ttf", ".otf")):
                        all_files.append(os.path.join(root, filename))
            for wanted in preferred_names:
                wanted_lower = wanted.lower()
                for path in all_files:
                    if wanted_lower in os.path.basename(path).lower():
                        return path
        for name in preferred_names:
            try:
                path = pygame.font.match_font(name)
                if path:
                    return path
            except Exception:
                pass
        return None

    def _create_fonts(self):
        pygame.font.init()
        cyber_path = self._find_font(["audiowide", "orbitron", "oxanium", "rajdhani", "neuropol"])
        clean_path = self._find_font(["rajdhani", "segoe", "bahnschrift", "trebuchet", "verdana"])

        if cyber_path:
            self.font_title = pygame.font.Font(cyber_path, 20)
            self.font_big_title = pygame.font.Font(cyber_path, 22)
            self.font_menu = pygame.font.Font(cyber_path, 11)
            self.font_button = pygame.font.Font(cyber_path, 13)
            self.font_hud = pygame.font.Font(cyber_path, 13)
        else:
            self.font_title = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_big_title = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_menu = pygame.font.SysFont("Arial", 11, bold=True)
            self.font_button = pygame.font.SysFont("Arial", 13, bold=True)
            self.font_hud = pygame.font.SysFont("Arial", 13, bold=True)

        if clean_path:
            self.font_category = pygame.font.Font(clean_path, 15)
            self.font_small = pygame.font.Font(clean_path, 11)
            self.font_medium = pygame.font.Font(clean_path, 15)
        else:
            self.font_category = pygame.font.SysFont("Arial", 15, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 11, bold=True)
            self.font_medium = pygame.font.SysFont("Arial", 15, bold=True)

    def _create_layout(self):
        self.hud_rect = pygame.Rect(8, 4, 870, 52)
        self.map_button = pygame.Rect(900, 6, 120, 44)
        self.leaderboard_button = pygame.Rect(1030, 6, 190, 44)

        self.menu_rect = pygame.Rect(530, 62, 740, 165)
        self.menu_slots = []
        slot_width = 77
        slot_height = 135
        gap = 5
        start_x = 538
        start_y = 75
        for index, drink_name in enumerate(DRINK_MENU):
            x = start_x + index * (slot_width + gap)
            self.menu_slots.append((drink_name, pygame.Rect(x, start_y, slot_width, slot_height)))

        self.customise_rect = pygame.Rect(600, 390, 320, 300)
        track_x = self.customise_rect.x + 25
        track_w = self.customise_rect.width - 50
        self.slider_tracks = {
            "temperature": pygame.Rect(track_x, 475, track_w, 12),
            "caffeine": pygame.Rect(track_x, 550, track_w, 12),
            "sweetness": pygame.Rect(track_x, 625, track_w, 12),
        }
        self.slider_hitboxes = {
            "temperature": pygame.Rect(track_x - 12, 452, track_w + 24, 48),
            "caffeine": pygame.Rect(track_x - 12, 527, track_w + 24, 48),
            "sweetness": pygame.Rect(track_x - 12, 602, track_w + 24, 48),
        }

        self.blender_rect = pygame.Rect(935, 390, 215, 300)
        self.blender_jug_rect = pygame.Rect(970, 465, 140, 130)
        self.blend_button = pygame.Rect(950, 632, 185, 48)

        self.preview_rect = pygame.Rect(1160, 390, 110, 300)
        self.preview_image_rect = pygame.Rect(1170, 445, 90, 130)
        self.serve_button = pygame.Rect(1168, 632, 94, 48)

    def _load_drink_images(self):
        for drink_name in DRINK_MENU:
            filename = drink_name.lower().replace(" ", "_") + ".png"
            path = os.path.join(self.drink_dir, filename)
            try:
                image = pygame.image.load(path).convert_alpha()
                self.drink_images[drink_name] = image
            except (pygame.error, FileNotFoundError):
                self.drink_images[drink_name] = None

    def set_level(self, level):
        try:
            self.level = max(1, int(level))
        except (TypeError, ValueError):
            self.level = 1

    def set_progression(self, progression):
        self.progression = progression
        if progression is not None:
            self.set_level(getattr(progression, "level", self.level))

    def set_rewards(self, rewards):
        self.rewards = rewards

    def set_economy(self, economy):
        self.economy = economy

    def set_reward_feedback(self, xp_delta=0, credit_delta=0):
        try:
            self.last_xp_change = int(xp_delta)
        except (TypeError, ValueError):
            self.last_xp_change = 0
        try:
            self.last_credit_change = int(credit_delta)
        except (TypeError, ValueError):
            self.last_credit_change = 0
        self.reward_feedback_until = time.monotonic() + 2.5

    def consume_map_request(self):
        requested = self.map_requested
        self.map_requested = False
        return requested

    def consume_leaderboard_request(self):
        requested = self.leaderboard_requested
        self.leaderboard_requested = False
        return requested

    def set_order(self, order):
        self.customer_order = order
        self.game_state.set_order(order)
        self.player_drink.reset()
        self._reset_sliders()
        self.served = False
        self._sync_legacy_values()

    def set_customer_order(self, order):
        self.set_order(order)

    def _attach_legacy_bridge(self):
        if self.drink is None:
            return
        try:
            self.drink.get_data = self.get_player_drink_data
        except Exception:
            pass

    def _sync_legacy_values(self):
        if self.drink is None:
            return
        temperature_map = {"Cold": 25, "Normal": 50, "Hot": 75}
        caffeine_map = {"Low": 25, "Normal": 50, "High": 75}
        sweetness_map = {"Less": 25, "Normal": 50, "Extra": 75}
        try:
            self.drink.temperature = temperature_map.get(self.player_drink.temperature, 50)
            self.drink.caffeine = caffeine_map.get(self.player_drink.caffeine, 50)
            self.drink.sweetness = sweetness_map.get(self.player_drink.sweetness, 50)
        except Exception:
            pass

    def _change_selected_drink(self, drink_name):
        self.player_drink.drink_name = drink_name
        self.player_drink.temperature = None
        self.player_drink.caffeine = None
        self.player_drink.sweetness = None

        self.game_state.selected_drink = drink_name
        self.game_state.selected_temperature = None
        self.game_state.selected_caffeine = None
        self.game_state.selected_sweetness = None
        self.game_state.blend_finished = False
        self.game_state.served = False
        self.game_state.state = GameState.CUSTOMISE
        self._reset_sliders()
        self.served = False
        self.liquid_unlocked = False
        self.assembly_phase = "empty"
        self.challenge.start_challenge(drink_name)
        self._sync_legacy_values()

    def update(self, dt=0.0):
        current_time = time.monotonic()
        if dt == 0.0:
            dt = current_time - self._last_time
        self._last_time = current_time
        dt = max(0.0, min(dt, 0.1))

        if self.game_state.can_customize() and self.player_drink.drink_name:
            for parameter in self.slider_positions:
                if self.slider_locked[parameter]:
                    continue
                self.slider_positions[parameter] += (
                    self.slider_speeds[parameter]
                    * self.slider_directions[parameter]
                    * dt
                )
                if self.slider_positions[parameter] >= 1.0:
                    self.slider_positions[parameter] = 1.0
                    self.slider_directions[parameter] = -1.0
                elif self.slider_positions[parameter] <= 0.0:
                    self.slider_positions[parameter] = 0.0
                    self.slider_directions[parameter] = 1.0
        self.challenge.update(dt)
        if self.challenge.done:
            self.liquid_unlocked = True
        self._update_blending()
        self._update_assembly()

    def _slider_position(self, parameter):
        return self.slider_positions[parameter]

    def _slider_option_from_position(self, parameter):
        options = {
            "temperature": TEMPERATURE_OPTIONS,
            "caffeine": CAFFEINE_OPTIONS,
            "sweetness": SWEETNESS_OPTIONS,
        }[parameter]
        position = self._slider_position(parameter)
        centers = (0.08, 0.50, 0.92)
        index = min(range(3), key=lambda i: abs(position - centers[i]))
        return options[index], abs(position - centers[index])

    def _reset_sliders(self):
        self.slider_positions = {
            "temperature": 0.08,
            "caffeine": 0.50,
            "sweetness": 0.92,
        }
        self.slider_directions = {
            "temperature": 1.0,
            "caffeine": -1.0,
            "sweetness": 1.0,
        }
        self.slider_locked = {
            "temperature": False,
            "caffeine": False,
            "sweetness": False,
        }
        self.slider_results = {
            "temperature": None,
            "caffeine": None,
            "sweetness": None,
        }
        self.slider_feedback = {
            "temperature": "CLICK",
            "caffeine": "CLICK",
            "sweetness": "CLICK",
        }

    def _get_customer_target(self, parameter):
        if self.customer_order is None:
            return None
        return getattr(self.customer_order, parameter, None)

    def _unlock_slider(self, parameter):
        self.slider_locked[parameter] = False
        self.slider_results[parameter] = None
        self.slider_feedback[parameter] = "ADJUSTING"
        if parameter == "temperature":
            self.player_drink.temperature = None
            self.game_state.selected_temperature = None
        elif parameter == "caffeine":
            self.player_drink.caffeine = None
            self.game_state.selected_caffeine = None
        else:
            self.player_drink.sweetness = None
            self.game_state.selected_sweetness = None
        self.game_state.state = GameState.CUSTOMISE
        self._sync_legacy_values()

    def _lock_slider(self, parameter):
        if not self.game_state.can_customize():
            return
        value, distance = self._slider_option_from_position(parameter)
        if parameter == "temperature":
            accepted = self.game_state.select_temperature(value)
            if accepted:
                self.player_drink.temperature = value
        elif parameter == "caffeine":
            accepted = self.game_state.select_caffeine(value)
            if accepted:
                self.player_drink.caffeine = value
        else:
            accepted = self.game_state.select_sweetness(value)
            if accepted:
                self.player_drink.sweetness = value
        if not accepted:
            return
        self.slider_locked[parameter] = True
        target = self._get_customer_target(parameter)
        correct = target is not None and value == target
        self.slider_results[parameter] = correct
        self.slider_feedback[parameter] = "CORRECT" if correct else "WRONG"
        self._sync_legacy_values()

    def _update_assembly(self):
        if self.assembly_phase == "empty":
            return
        elapsed = time.monotonic() - self.assembly_started
        phases = (("ice", 1.25), ("pour", 1.25), ("topping", 0.9))
        total = 0.0
        for name, duration in phases:
            if elapsed < total + duration:
                self.assembly_phase = name
                return
            total += duration
        self.assembly_phase = "ready"
        if self.game_state.state == GameState.BLENDING:
            self.game_state.finish_blending()
            self._sync_legacy_values()

    def _start_assembly(self):
        self.assembly_phase = "ice"
        self.assembly_started = time.monotonic()

    def _update_blending(self):
        if self.game_state.state != GameState.BLENDING:
            return
        current_time = time.monotonic()
        elapsed = current_time - self.blend_start_time
        self.blender_angle = (elapsed * 720) % 360
        self.blender_pulse = math.sin(elapsed * 10) * 0.5 + 0.5
        if elapsed >= self.blend_duration:
            self._start_assembly()

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if event.button != 1:
            return
        mouse = event.pos
        self._update_blending()
        if self.challenge.active:
            self.challenge.handle_event(event)
            return

        if self.map_button.collidepoint(mouse):
            self.map_requested = True
            return

        if self.leaderboard_button.collidepoint(mouse):
            self.leaderboard_requested = True
            return

        for drink_name, rect in self.menu_slots:
            if not rect.collidepoint(mouse):
                continue
            if not is_valid_drink(drink_name):
                return
            if not is_drink_unlocked(drink_name, self.level):
                return
            if self.game_state.state in (
                GameState.BLENDING,
                GameState.READY_TO_SERVE,
                GameState.SERVED,
            ):
                return
            self._change_selected_drink(drink_name)
            return

        if self.game_state.state in (
            GameState.CUSTOMISE,
            GameState.READY_TO_BLEND,
        ):
            for parameter, rect in self.slider_hitboxes.items():
                if not rect.collidepoint(mouse):
                    continue
                if self.slider_locked[parameter]:
                    self._unlock_slider(parameter)
                else:
                    self._lock_slider(parameter)
                return

        if self.blend_button.collidepoint(mouse):
            if self.challenge.done:
                self.liquid_unlocked = True
            if self.liquid_unlocked and self.game_state.start_blending():
                self.blend_start_time = time.monotonic()
                self.blender_angle = 0.0
            return

        if self.serve_button.collidepoint(mouse):
            if self.game_state.serve():
                self.served = True
                self._sync_legacy_values()
            return

    def get_player_drink_data(self):
        return self.game_state.get_player_drink_data()

    def get_data(self):
        return self.get_player_drink_data()

    def draw(self, screen):
        self._update_blending()
        self._draw_hud(screen)
        self._draw_menu(screen)
        self._draw_customise(screen)
        self._draw_blender(screen)
        self._draw_preview(screen)
        self.challenge.draw(screen)

    def _draw_hud(self, screen):
        self._action_button(screen, self.map_button, "MAP  [M]", self.CYAN, True, large=False)
        self._action_button(screen, self.leaderboard_button, "LEADERBOARD  [L]", self.PINK, True, large=False)

    def _draw_menu(self, screen):
        self._panel(screen, self.menu_rect, self.CYAN, self.PANEL)
        title = self.font_title.render("CYBERPUNK DRINK MENU", True, self.CYAN_LIGHT)
        screen.blit(title, title.get_rect(center=(self.menu_rect.centerx, 89)))

        for drink_name, rect in self.menu_slots:
            unlocked = is_drink_unlocked(drink_name, self.level)
            selected = self.player_drink.drink_name == drink_name
            if selected:
                border = self.PINK_LIGHT
                fill = self.BUTTON_SELECTED
            elif unlocked:
                border = self.CYAN
                fill = self.BUTTON
            else:
                border = self.LOCKED
                fill = (6, 9, 22, 135)
            self._panel(screen, rect, border, fill, radius=12, width=1)
            image = self.drink_images.get(drink_name)
            image_area = pygame.Rect(rect.x + 6, rect.y + 7, rect.width - 12, 112)
            if image is not None:
                self._image_fit(screen, image, image_area, unlocked)
            if not unlocked:
                self._draw_lock(screen, rect.centerx, rect.y + 64)
            self._draw_drink_name(screen, drink_name, rect, unlocked)

    def _draw_drink_name(self, screen, drink_name, rect, unlocked):
        colour = self.WHITE if unlocked else self.LOCKED
        if drink_name == "Hologram Frappe":
            lines = ["HOLOGRAM", "FRAPPE"]
        elif drink_name == "Stardust Matcha":
            lines = ["STARDUST", "MATCHA"]
        elif drink_name == "Cyber Fuel":
            lines = ["CYBER", "FUEL"]
        elif drink_name == "Pixel Lemint":
            lines = ["PIXEL", "LEMINT"]
        elif drink_name == "Caramel Byte":
            lines = ["CARAMEL", "BYTE"]
        else:
            lines = [drink_name.upper()]

        if len(lines) == 1:
            text = self.font_menu.render(lines[0], True, colour)
            screen.blit(text, text.get_rect(center=(rect.centerx, rect.bottom - 14)))
        else:
            first = self.font_menu.render(lines[0], True, colour)
            second = self.font_menu.render(lines[1], True, colour)
            screen.blit(first, first.get_rect(center=(rect.centerx, rect.bottom - 24)))
            screen.blit(second, second.get_rect(center=(rect.centerx, rect.bottom - 11)))

    def _draw_customise(self, screen):
        self._panel(screen, self.customise_rect, self.CYAN, (6, 12, 29, 190), radius=14, width=2)
        title = self.font_big_title.render("CUSTOMISE YOUR DRINK", True, self.CYAN_LIGHT)
        screen.blit(title, title.get_rect(center=(self.customise_rect.centerx, 420)))
        instruction = self.font_small.render("CLICK WHEN THE INDICATOR HITS THE CORRECT ZONE!", True, self.SOFT_WHITE)
        screen.blit(instruction, instruction.get_rect(center=(self.customise_rect.centerx, 444)))

        self._draw_timing_slider(screen, "temperature", "TEMPERATURE", TEMPERATURE_OPTIONS, self.CYAN, 465)
        self._draw_timing_slider(screen, "caffeine", "CAFFEINE LEVEL", CAFFEINE_OPTIONS, self.YELLOW, 540)
        self._draw_timing_slider(screen, "sweetness", "SWEETNESS LEVEL", SWEETNESS_OPTIONS, self.PINK_LIGHT, 615)

    def _draw_timing_slider(self, screen, parameter, label, options, accent, track_y):
        track = self.slider_tracks[parameter]
        label_surface = self.font_category.render(label, True, accent)
        screen.blit(label_surface, (track.x, track.y - 26))

        glow = pygame.Rect(track.x - 2, track.y - 2, track.width + 4, track.height + 4)
        glow_surface = pygame.Surface(glow.size, pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*accent, 70), glow_surface.get_rect(), border_radius=8)
        screen.blit(glow_surface, glow.topleft)

        pygame.draw.rect(screen, (15, 24, 48), track, border_radius=6)
        pygame.draw.rect(screen, accent, track, width=2, border_radius=6)

        centers = (0.08, 0.50, 0.92)
        zone_width = max(34, int(track.width * 0.16))
        for index, option in enumerate(options):
            cx = int(track.x + track.width * centers[index])
            zone_rect = pygame.Rect(cx - zone_width // 2, track.y - 5, zone_width, track.height + 10)
            pygame.draw.rect(screen, (*accent, 28), zone_rect, border_radius=7)
            pygame.draw.line(screen, (105, 120, 150), (cx, track.y - 5), (cx, track.bottom + 5), 1)
            text = self.font_small.render(option.upper(), True, self.WHITE)
            screen.blit(text, text.get_rect(center=(cx, track.bottom + 18)))

        position = self._slider_position(parameter)
        indicator_x = int(track.x + track.width * position)
        pygame.draw.circle(screen, (0, 0, 0), (indicator_x, track.centery), 9)
        pygame.draw.circle(screen, accent, (indicator_x, track.centery), 7)
        pygame.draw.circle(screen, self.WHITE, (indicator_x, track.centery), 2)
        if self.slider_locked[parameter]:
            pygame.draw.circle(screen, self.WHITE, (indicator_x, track.centery), 11, width=2)

        result = self.slider_results[parameter]
        locked = self.slider_locked[parameter]
        if locked and result is True:
            feedback = "✓ LOCKED"
            colour = self.GREEN
        elif locked and result is False:
            feedback = "✕ WRONG"
            colour = self.PINK_LIGHT
        elif self.slider_feedback[parameter] == "ADJUSTING":
            feedback = "ADJUSTING"
            colour = self.CYAN_LIGHT
        else:
            feedback = "CLICK"
            colour = self.MUTED

        feedback_text = self.font_small.render(feedback, True, colour)
        screen.blit(feedback_text, (track.right - feedback_text.get_width(), track.y - 26))

    def _ingredients_for(self, drink):
        return {
            "Neon Latte": ["milk","coffee","syrup"], "Milkyway": ["milk","chocolate","star"],
            "Void Chai": ["milk","spice","syrup"], "Cyber Fuel": ["milk","battery","ice"],
            "Hologram Frappe": ["milk","orb","star"], "Pixel Lemint": ["water","mint","ice"],
            "Caramel Byte": ["milk","cookie","caramel"], "Stardust Matcha": ["milk","matcha","star"],
            "Meteorite": ["milk","meteor","ice"],
        }.get(drink, ["milk"])

    def _draw_ingredient(self, screen, kind, x, y, scale=1.0):
        c = self.CYAN_LIGHT
        if kind == "milk": pygame.draw.ellipse(screen,(240,248,255),(x-16,y-10,x+16,y+10))
        elif kind == "coffee": pygame.draw.circle(screen,(105,65,45),(x,y),12)
        elif kind == "chocolate": pygame.draw.rect(screen,(90,55,45),(x-12,y-9,24,18),border_radius=4)
        elif kind == "syrup": pygame.draw.line(screen,(225,135,90),(x-10,y-8),(x+10,y+8),5)
        elif kind == "mint": pygame.draw.ellipse(screen,(90,235,165),(x-7,y-14,x+8,y+9))
        elif kind == "cookie": pygame.draw.circle(screen,(205,140,80),(x,y),12)
        elif kind == "caramel": pygame.draw.line(screen,(240,175,85),(x-12,y),(x+12,y),5)
        elif kind == "matcha": pygame.draw.circle(screen,(165,195,105),(x,y),12)
        elif kind == "battery": pygame.draw.rect(screen,(120,220,255),(x-11,y-14,22,28),border_radius=4)
        elif kind == "orb": pygame.draw.circle(screen,(210,150,255),(x,y),12)
        elif kind == "ice": pygame.draw.rect(screen,(190,235,255),(x-9,y-9,18,18),border_radius=4)
        elif kind == "star":
            pts=[(x+math.cos(-math.pi/2+i*math.pi/2.5)*13,y+math.sin(-math.pi/2+i*math.pi/2.5)*13) for i in range(5)]
            pygame.draw.polygon(screen,(255,225,110),pts)
        elif kind == "spice": pygame.draw.circle(screen,(235,155,95),(x,y),10)
        elif kind == "water": pygame.draw.circle(screen,(130,205,255),(x,y),11)
        elif kind == "meteor": pygame.draw.polygon(screen,(220,235,250),[(x-13,y),(x+10,y-7),(x+6,y+9)])

    def _draw_blender(self, screen):
        self._panel(screen, self.blender_rect, self.PURPLE, (6, 10, 27, 145))
        title = self.font_big_title.render("BLENDER", True, self.CYAN_LIGHT)
        screen.blit(title, title.get_rect(center=(self.blender_rect.centerx, self.blender_rect.y + 20)))

        jug = self.blender_jug_rect.copy()
        is_blending = self.game_state.state == GameState.BLENDING

        if is_blending:
            jug.x += int(math.sin(time.monotonic() * 30) * 2)
            jug.y += int(math.cos(time.monotonic() * 25))

        if is_blending:
            glow_surface = pygame.Surface((jug.width + 28, jug.height + 28), pygame.SRCALPHA)
            alpha = int(30 + self.blender_pulse * 40)
            pygame.draw.rect(glow_surface, (75, 225, 255, alpha), glow_surface.get_rect(), border_radius=25, width=5)
            screen.blit(glow_surface, (jug.x - 14, jug.y - 14))

        pygame.draw.rect(screen, (17, 25, 52), jug, border_radius=23)
        pygame.draw.rect(screen, self.CYAN_LIGHT, jug, width=2, border_radius=23)

        lid = pygame.Rect(jug.x + 24, jug.y - 8, jug.width - 48, 18)
        pygame.draw.rect(screen, (20, 24, 48), lid, border_radius=8)
        pygame.draw.rect(screen, self.PINK_LIGHT, lid, width=2, border_radius=8)

        inner = pygame.Rect(jug.x + 11, jug.y + 13, jug.width - 22, jug.height - 28)
        pygame.draw.rect(screen, (7, 12, 28), inner, border_radius=17)

        handle = pygame.Rect(jug.right - 2, jug.y + 28, 22, 52)
        pygame.draw.rect(screen, (18, 25, 52), handle, border_radius=13)
        pygame.draw.rect(screen, self.CYAN, handle, width=2, border_radius=13)

        drink_name = self.player_drink.drink_name
        if is_blending and drink_name:
            recipe = get_recipe(drink_name)
            liquid_colour = recipe.liquid_color if recipe else (150,150,255)
            if time.monotonic() - self.blend_start_time < 0.55:
                pygame.draw.line(screen, liquid_colour, (jug.centerx, jug.y-20), (jug.centerx, jug.y+28), 8)
                pygame.draw.circle(screen, self.WHITE, (jug.centerx, jug.y+30), 4)
            ingredients = self._ingredients_for(drink_name)
            elapsed = time.monotonic() - self.blend_start_time
            for i, kind in enumerate(ingredients):
                t = elapsed - i * 0.28
                if 0 <= t <= 0.7:
                    x = jug.centerx + (i - (len(ingredients)-1)/2) * 30
                    y = jug.y - 15 + min(75, t * 150)
                    self._draw_ingredient(screen, kind, int(x), int(y), 0.65)
        if drink_name and (self.liquid_unlocked or is_blending):
            recipe = get_recipe(drink_name)
            liquid_colour = recipe.liquid_color if recipe else (150, 150, 255)

            if drink_name == "Hologram Frappe" and is_blending:
                cycle = time.monotonic() * 3
                liquid_colour = (
                    int(180 + 55 * (math.sin(cycle) + 1) / 2),
                    int(150 + 80 * (math.sin(cycle + 2) + 1) / 2),
                    int(200 + 55 * (math.sin(cycle + 4) + 1) / 2),
                )

            liquid_height = inner.height - 22
            if is_blending:
                liquid_height += int(math.sin(time.monotonic() * 12) * 4)

            liquid = pygame.Rect(inner.x + 4, inner.bottom - liquid_height - 4, inner.width - 8, liquid_height)
            pygame.draw.rect(screen, liquid_colour, liquid, border_radius=14)

            highlight_colour = (
                min(255, liquid_colour[0] + 45),
                min(255, liquid_colour[1] + 45),
                min(255, liquid_colour[2] + 45),
            )
            highlight = pygame.Rect(liquid.x + 7, liquid.y + 6, liquid.width - 14, 6)
            pygame.draw.rect(screen, highlight_colour, highlight, border_radius=4)

            shimmer_y = int(liquid.y + liquid.height * (0.35 + 0.12 * math.sin(time.monotonic() * 2.5)))
            pygame.draw.line(screen, (255, 255, 255, 110), (liquid.x + 12, shimmer_y), (liquid.right - 12, shimmer_y), 1)

            if is_blending:
                wave_y = liquid.y + 25
                wave_width = liquid.width - 22
                wave_left = liquid.x + 11
                points = []
                for index in range(9):
                    px = wave_left + index * (wave_width / 8)
                    py = wave_y + math.sin(time.monotonic() * 8 + index) * 5
                    points.append((int(px), int(py)))
                pygame.draw.lines(screen, self.WHITE, False, points, 2)

                current_time = time.monotonic()
                for index in range(6):
                    phase = current_time * (1.5 + index * 0.18) + index
                    bubble_x = liquid.x + 20 + (index * 19) % max(20, liquid.width - 30)
                    bubble_y = liquid.bottom - 15 - (phase * 32) % max(20, liquid.height - 20)
                    pygame.draw.circle(screen, (240, 250, 255), (int(bubble_x), int(bubble_y)), 3)
        else:
            text = self.font_small.render("COMPLETE INGREDIENT CHALLENGE", True, self.MUTED)
            screen.blit(text, text.get_rect(center=inner.center))

        core_x = jug.centerx
        core_y = jug.bottom - 20
        pygame.draw.circle(screen, (12, 17, 35), (core_x, core_y), 11)
        pygame.draw.circle(screen, self.PINK, (core_x, core_y), 3)

        if is_blending:
            angle = math.radians(self.blender_angle)
            for offset in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
                blade_angle = angle + offset
                end_x = core_x + math.cos(blade_angle) * 25
                end_y = core_y + math.sin(blade_angle) * 25
                pygame.draw.line(screen, self.CYAN_LIGHT, (core_x, core_y), (int(end_x), int(end_y)), 3)

        base = pygame.Rect(jug.x - 10, jug.bottom - 2, jug.width + 20, 22)
        pygame.draw.rect(screen, (22, 18, 40), base, border_radius=10)
        pygame.draw.rect(screen, self.PINK, base, width=1, border_radius=10)

        if is_blending:
            elapsed = time.monotonic() - self.blend_start_time
            ratio = max(0, min(1, elapsed / self.blend_duration))
            progress_rect = pygame.Rect(
                self.blend_button.x + 8,
                self.blend_button.y - 8,
                self.blend_button.width - 16,
                4,
            )
            pygame.draw.rect(screen, (20, 25, 45), progress_rect, border_radius=2)
            pygame.draw.rect(
                screen,
                self.CYAN,
                pygame.Rect(
                    progress_rect.x,
                    progress_rect.y,
                    int(progress_rect.width * ratio),
                    progress_rect.height,
                ),
                border_radius=2,
            )

        self._action_button(
            screen,
            self.blend_button,
            ("BLENDING..." if is_blending else "BLEND"),
            self.PINK,
            self.game_state.can_blend() and self.liquid_unlocked and self.assembly_phase == "empty",
            large=True,
        )

    def _draw_preview(self, screen):
        self._panel(screen, self.preview_rect, self.PINK, (7, 10, 26, 150))
        title = self.font_title.render("CUP STATION", True, self.PINK_LIGHT)
        screen.blit(title, title.get_rect(center=(self.preview_rect.centerx, 420)))
        self._draw_cup_sequence(screen)
        ready = self.game_state.state == GameState.READY_TO_SERVE and self.assembly_phase == "ready"
        label = "READY!" if ready else self.assembly_phase.upper()
        colour = self.GREEN if ready else self.CYAN_LIGHT
        txt = self.font_small.render(label, True, colour)
        screen.blit(txt, txt.get_rect(center=(self.preview_rect.centerx, 600)))
        self._action_button(screen, self.serve_button, "SERVE", self.CYAN, ready, large=False)

    def _draw_cup_sequence(self, screen):
        r = pygame.Rect(self.preview_rect.x + 20, 455, 70, 125)
        cx = r.centerx
        pygame.draw.polygon(screen, (225,235,250), [(r.x+7,r.y),(r.right-7,r.y),(r.right-16,r.bottom),(r.x+16,r.bottom)])
        pygame.draw.polygon(screen, (35,45,70), [(r.x+12,r.y+8),(r.right-12,r.y+8),(r.right-20,r.bottom-12),(r.x+20,r.bottom-12)])
        phase = self.assembly_phase
        if phase in ("ice","pour","topping","ready"):
            for i in range(5):
                x = r.x + 18 + (i%2)*25; y = r.y + 18 + (i//2)*24
                pygame.draw.rect(screen, (205,235,255), (x,y,15,12), border_radius=3)
        if phase in ("pour","topping","ready") and self.player_drink.drink_name:
            recipe = get_recipe(self.player_drink.drink_name); c = recipe.liquid_color if recipe else (150,150,255)
            pygame.draw.polygon(screen,c,[(r.x+16,r.y+45),(r.right-16,r.y+45),(r.right-22,r.bottom-10),(r.x+22,r.bottom-10)])
            if phase == "pour":
                pygame.draw.line(screen,c,(cx,425),(cx,r.y+45),8)
        if phase in ("topping","ready"):
            self._draw_toppings(screen,cx,r.y+42)
        if phase == "ice":
            crusher = pygame.Rect(r.x-5, r.y-28, r.width+10, 18)
            pygame.draw.rect(screen,(25,35,60),crusher,border_radius=6)
            pygame.draw.rect(screen,self.CYAN,crusher,2,border_radius=6)
            yy = int(r.y-8 + math.sin(time.monotonic()*12)*6)
            pygame.draw.line(screen,self.PINK,(cx,yy),(cx,r.y+10),5)
        if phase == "ready":
            pygame.draw.arc(screen,self.CYAN_LIGHT,(r.x-5,r.y-10,r.width+10,35),math.pi,2*math.pi,3)

    def _draw_toppings(self,screen,cx,y):
        toppings = get_recipe(self.player_drink.drink_name).toppings if self.player_drink.drink_name else ()
        for i,t in enumerate(toppings[:3]):
            x=cx+(i-1)*18
            if "mint" in t: pygame.draw.ellipse(screen,(90,235,165),(x-8,y-8,x+8,y+8))
            elif "chocolate" in t or "cookie" in t: pygame.draw.circle(screen,(90,55,45),(x,y),7)
            elif "caramel" in t: pygame.draw.line(screen,(235,170,80),(x-8,y-5),(x+8,y+5),4)
            elif "meteor" in t: pygame.draw.polygon(screen,(210,230,250),[(x-7,y),(x+5,y-6),(x+8,y+6)])
            else: pygame.draw.circle(screen,(245,245,255),(x,y),8)

    def _panel(self, screen, rect, border, fill, radius=14, width=2):
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, fill, surface.get_rect(), border_radius=radius)
        screen.blit(surface, rect.topleft)
        pygame.draw.rect(screen, border, rect, width=width, border_radius=radius)

    def _action_button(self, screen, rect, text, accent, enabled, large=False):
        mouse = pygame.mouse.get_pos()
        hover = enabled and rect.collidepoint(mouse)
        if enabled:
            border = self.PINK_LIGHT if hover else accent
            fill = (45, 12, 52, 205)
            text_colour = self.WHITE
        else:
            border = (60, 65, 85)
            fill = (7, 10, 22, 160)
            text_colour = self.MUTED

        if hover:
            glow = pygame.Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4)
            pygame.draw.rect(screen, (255, 100, 210), glow, width=1, border_radius=13)

        self._panel(screen, rect, border, fill, radius=12, width=1)
        font = self.font_big_title if large else self.font_button
        label = font.render(text, True, text_colour)
        screen.blit(label, label.get_rect(center=rect.center))

    def _image_fit(self, screen, image, target, bright=True):
        if image is None:
            return
        width, height = image.get_size()
        if width <= 0 or height <= 0:
            return
        scale = min(target.width / width, target.height / height)
        size = (max(1, int(width * scale)), max(1, int(height * scale)))
        scaled = pygame.transform.smoothscale(image, size)
        if not bright:
            scaled = scaled.copy()
            scaled.fill((70, 70, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
        destination = scaled.get_rect(center=target.center)
        screen.blit(scaled, destination)

    def _draw_lock(self, screen, x, y):
        body = pygame.Rect(x - 9, y, 18, 15)
        pygame.draw.rect(screen, self.LOCKED, body, border_radius=4)
        pygame.draw.arc(screen, self.LOCKED, pygame.Rect(x - 6, y - 11, 12, 16), math.pi, 2 * math.pi, 2)
        pygame.draw.circle(screen, (25, 28, 45), (x, y + 7), 2)

    def reset(self):
        self.player_drink.reset()
        self.game_state.reset()
        self.customer_order = None
        self.served = False
        self.challenge = MiniChallenge()
        self.liquid_unlocked = False
        self.assembly_phase = "empty"
        self.assembly_started = 0.0
        self.map_requested = False
        self.leaderboard_requested = False
        self.last_xp_change = 0
        self.last_credit_change = 0
        self.reward_feedback_until = 0.0
        self._reset_sliders()
        self.blend_start_time = 0.0
        self.blender_angle = 0.0
        self.blender_pulse = 0.0
        self._sync_legacy_values()
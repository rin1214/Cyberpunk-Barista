import json
import os
import pygame
from drink import LEVEL_PRICES

class UIEconomy:
    SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_data.json")
    
    STARTING_CREDITS = 100
    STARTING_XP = 0
    STARTING_LEVEL = 1
    MAX_LEVEL = 3
    MIN_CREDITS = 0

    # Costs required to unlock levels via map nodes using credits
    LEVEL_UNLOCK_COSTS = {
        1: 0,    # Level 1 is unlocked by default
        2: 250,  # Cost for Neon Lounge
        3: 500   # Cost for Cyber Penthouse
    }

    DRINK_PRICES = LEVEL_PRICES

    LOCATIONS = {
        1: "Back Alley Kiosk",
        2: "Neon Lounge",
        3: "Cyber Penthouse",
    }
    
    # Cyberpunk Theme Palette
    COLOR_BG_SOLID = (12, 14, 22)     
    COLOR_BORDER = (0, 240, 255)      # Cyan
    COLOR_TEXT = (240, 245, 255)      # White
    COLOR_GOLD = (255, 200, 0)        # Gold
    COLOR_PINK = (255, 0, 110)        # Pink
    COLOR_CYAN = (0, 240, 255)        # Cyan

    def __init__(self, screen, player_name="Player"):
        self.screen = screen
        self.player_name = str(player_name).strip() if player_name else "Player"
        if not self.player_name:
            self.player_name = "Player"
            
        self.credits = self.STARTING_CREDITS
        self.xp = self.STARTING_XP
        self.level = self.STARTING_LEVEL
        self.location = self.LOCATIONS[self.STARTING_LEVEL]
        
        # Track unlocked levels
        self.unlocked_levels = {
            1: True,
            2: False,
            3: False
        }
        
        self.load_economy_data()

    def get_drink_price(self, drink_name=None, level=None):
        if drink_name:
            from drink import get_drink_price
            return get_drink_price(drink_name)

        target_level = self.level if level is None else level
        try:
            target_level = int(target_level)
        except (TypeError, ValueError):
            target_level = self.STARTING_LEVEL
        return self.DRINK_PRICES.get(target_level, self.DRINK_PRICES[1])

    def serve_order(self, is_correct=True, drink_name=None, accuracy_multiplier=1.0):
        if not is_correct:
            return 0
        try:
            multiplier = max(0.0, float(accuracy_multiplier))
        except (TypeError, ValueError):
            multiplier = 0.0
        earned = int(self.get_drink_price(drink_name=drink_name) * multiplier)
        self.add_credits(earned)
        return earned

    def add_credits(self, amount):
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False
        self.credits += amount
        if self.credits < self.MIN_CREDITS:
            self.credits = self.MIN_CREDITS
        self.save_economy_data()
        return True

    def get_credits(self):
        return self.credits

    def set_credits(self, amount):
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False
        self.credits = max(self.MIN_CREDITS, amount)
        self.save_economy_data()
        return True

    def spend_credits(self, amount):
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False
        if amount < 0 or self.credits < amount:
            return False
        self.credits -= amount
        self.save_economy_data()
        return True

    def is_level_unlocked(self, level):
        """Checks if a specific level has been unlocked via map nodes."""
        return self.unlocked_levels.get(int(level), False)

    def can_unlock_level(self, level):
        """Determines if the player can afford and unlock the target level."""
        level = int(level)
        if self.is_level_unlocked(level):
            return False
        cost = self.LEVEL_UNLOCK_COSTS.get(level, 0)
        return self.credits >= cost

    def unlock_level_with_credits(self, level):
        level = int(level)
        if self.can_unlock_level(level):
            cost = self.LEVEL_UNLOCK_COSTS.get(level, 0)
            if self.spend_credits(cost):
                self.unlocked_levels[level] = True
                self.save_economy_data()
                return True
        return False

    def apply_reward(self, reward_result):
        if reward_result is None:
            return False
        if hasattr(reward_result, "net_credits"):
            credit_change = reward_result.net_credits
        elif hasattr(reward_result, "total_credits"):
            credit_change = reward_result.total_credits
        else:
            return False
        return self.add_credits(credit_change)

    def set_level(self, level):
        try:
            level = int(level)
        except (TypeError, ValueError):
            return False
        
        # Prevent jumping to locked levels unless unlocked via map node
        if not self.is_level_unlocked(level):
            return False
            
        self.level = max(1, min(level, self.MAX_LEVEL))
        self.location = self.LOCATIONS.get(self.level, self.LOCATIONS[1])
        self.save_economy_data()
        return True

    def set_xp(self, xp):
        try:
            xp = int(xp)
        except (TypeError, ValueError):
            return False
        self.xp = max(0, xp)
        self.save_economy_data()
        return True

    def get_level(self):
        return self.level

    def get_xp(self):
        return self.xp

    def get_player_name(self):
        return self.player_name

    def get_location(self):
        return self.location

    def reset_economy(self):
        self.credits = self.STARTING_CREDITS
        self.xp = self.STARTING_XP
        self.level = self.STARTING_LEVEL
        self.location = self.LOCATIONS[self.STARTING_LEVEL]
        self.unlocked_levels = {1: True, 2: False, 3: False}
        self.save_economy_data()

    def save_economy_data(self):
        all_profiles = {}
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r", encoding="utf-8") as file:
                    all_profiles = json.load(file)
                if not isinstance(all_profiles, dict):
                    all_profiles = {}
            except (IOError, json.JSONDecodeError):
                all_profiles = {}

        for name, profile in all_profiles.items():
            if not isinstance(profile, dict):
                continue
            try:
                saved_level = int(profile.get("level", 1))
            except (TypeError, ValueError):
                saved_level = 1
            saved_level = max(1, min(saved_level, self.MAX_LEVEL))
            profile["level"] = saved_level
            profile["location"] = self.LOCATIONS.get(saved_level, self.LOCATIONS[1])
            try:
                profile["xp"] = max(0, int(profile.get("xp", 0)))
            except (TypeError, ValueError):
                profile["xp"] = 0
            try:
                profile["credits"] = max(self.MIN_CREDITS, int(profile.get("credits", self.STARTING_CREDITS)))
            except (TypeError, ValueError):
                profile["credits"] = self.STARTING_CREDITS

        self.level = max(1, min(int(self.level), self.MAX_LEVEL))
        self.xp = max(0, int(self.xp))
        self.credits = max(self.MIN_CREDITS, int(self.credits))
        self.location = self.LOCATIONS.get(self.level, self.LOCATIONS[1])

        serialized_unlocked = {str(k): v for k, v in self.unlocked_levels.items()}

        all_profiles[self.player_name] = {
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "location": self.location,
            "unlocked_levels": serialized_unlocked,
        }
        try:
            with open(self.SAVE_FILE, "w", encoding="utf-8") as file:
                json.dump(all_profiles, file, indent=4)
        except IOError as e:
            print(f"[ECONOMY ERROR] Could not save economy data: {e}")

    def load_economy_data(self):
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r", encoding="utf-8") as file:
                    all_profiles = json.load(file)
                if not isinstance(all_profiles, dict):
                    all_profiles = {}
                if self.player_name in all_profiles:
                    player_data = all_profiles[self.player_name]
                    if not isinstance(player_data, dict):
                        player_data = {}
                    try:
                        self.credits = max(self.MIN_CREDITS, int(player_data.get("credits", self.STARTING_CREDITS)))
                    except (TypeError, ValueError):
                        self.credits = self.STARTING_CREDITS
                    try:
                        self.xp = max(0, int(player_data.get("xp", self.STARTING_XP)))
                    except (TypeError, ValueError):
                        self.xp = self.STARTING_XP
                    try:
                        self.level = int(player_data.get("level", self.STARTING_LEVEL))
                    except (TypeError, ValueError):
                        self.level = self.STARTING_LEVEL
                        
                    self.level = max(1, min(self.level, self.MAX_LEVEL))
                    self.location = self.LOCATIONS.get(self.level, self.LOCATIONS[1])
                    
                    saved_unlocked = player_data.get("unlocked_levels", {1: True})
                    self.unlocked_levels = {int(k): bool(v) for k, v in saved_unlocked.items()}
                    self.unlocked_levels[1] = True
                    
                    self.save_economy_data()
                    return
            except (IOError, json.JSONDecodeError, TypeError, ValueError):
                pass

        self.credits = self.STARTING_CREDITS
        self.xp = self.STARTING_XP
        self.level = self.STARTING_LEVEL
        self.location = self.LOCATIONS[self.STARTING_LEVEL]
        self.unlocked_levels = {1: True, 2: False, 3: False}
        self.save_economy_data()

    def get_level_bg_color(self):
        colors = {
            1: (15, 10, 25),
            2: (25, 10, 20),
            3: (20, 5, 30),
        }
        return colors.get(self.level, colors[3])

    def get_data(self):
        return {
            "player_name": self.player_name,
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "location": self.location,
            "unlocked_levels": self.unlocked_levels,
            "drink_price": self.get_drink_price(),
        }

    # =========================================================================
    # CYBERPUNK HUD DRAWING IMPLEMENTATION
    # =========================================================================
    def draw_hud(self, combo_count=1):
        screen_w = self.screen.get_width()
        
        hud_height = 60
        hud_width = min(680, screen_w - 320)
        hud_rect = pygame.Rect(10, 2, hud_width, hud_height)
        
        pygame.draw.rect(self.screen, self.COLOR_BG_SOLID, hud_rect, border_radius=4)
        pygame.draw.rect(self.screen, self.COLOR_BORDER, hud_rect, 2, border_radius=4)
        pygame.draw.line(self.screen, self.COLOR_CYAN, (hud_rect.x + 5, hud_rect.y), (hud_rect.x + 35, hud_rect.y), 4)
        pygame.draw.line(self.screen, self.COLOR_CYAN, (hud_rect.right - 35, hud_rect.bottom), (hud_rect.right - 5, hud_rect.bottom), 4)
        
        font_main = pygame.font.SysFont("Consolas", 15, bold=True)
        font_sub = pygame.font.SysFont("Consolas", 12, bold=True)
        
        # Barista Name & Location
        name_txt = font_main.render(f"BARISTA: {self.player_name.upper()}", True, self.COLOR_BORDER)
        loc_txt = font_sub.render(f"LOCATION: {self.location.upper()}", True, self.COLOR_TEXT)
        self.screen.blit(name_txt, (hud_rect.x + 12, hud_rect.y + 12))
        self.screen.blit(loc_txt, (hud_rect.x + 12, hud_rect.y + 36))
        
        pygame.draw.line(self.screen, (50, 60, 80), (hud_rect.x + 220, hud_rect.y + 10), (hud_rect.x + 220, hud_rect.bottom - 10), 1)
        
        # Level & XP
        xp_x = hud_rect.x + 232
        
        lvl_txt = font_main.render(f"LVL {self.level}", True, self.COLOR_CYAN)
        xp_num_txt = font_main.render(f"{self.xp:,} XP", True, self.COLOR_TEXT)
        
        self.screen.blit(lvl_txt, (xp_x, hud_rect.y + 12))
        self.screen.blit(xp_num_txt, (xp_x, hud_rect.y + 34))
            
        pygame.draw.line(self.screen, (50, 60, 80), (hud_rect.x + 375, hud_rect.y + 10), (hud_rect.x + 375, hud_rect.bottom - 10), 1)
        
        # Credits Display
        cred_x = hud_rect.x + 388
        cred_lbl = font_sub.render("CREDITS", True, (150, 160, 180))
        cred_val = font_main.render(f"${self.credits:,}", True, self.COLOR_GOLD)
        self.screen.blit(cred_lbl, (cred_x, hud_rect.y + 12))
        self.screen.blit(cred_val, (cred_x, hud_rect.y + 32))
        
        pygame.draw.line(self.screen, (50, 60, 80), (hud_rect.x + 500, hud_rect.y + 10), (hud_rect.x + 500, hud_rect.bottom - 10), 1)
        
        # Combo Counter Display
        combo_x = hud_rect.x + 512
        combo_txt = font_main.render("COMBO", True, self.COLOR_PINK)
        combo_val = font_main.render(f"x{combo_count}", True, self.COLOR_PINK)
        self.screen.blit(combo_txt, (combo_x, hud_rect.y + 12))
        self.screen.blit(combo_val, (combo_x, hud_rect.y + 32))

    def draw(self, combo_count=1, dt=0):
        self.draw_hud(combo_count=combo_count)
import pygame
import json
import os

class UIEconomy:
    LOCATIONS = {
        1: "Back Alley Kiosk",
        2: "Neon Lounge",
        3: "Cyber Penthouse"
    }

    MAX_LEVEL = 3

    def __init__(self, screen, save_file="save_data.json"):
        self.screen = screen
        self.save_file = save_file
        
        # Base economy stats
        self.credits = 0
        self.xp = 0
        self.level = 1
        self.location = "Back Alley Kiosk"
        
        # High-Voltage Neon Color Palette (Max Brightness)
        self.COLOR_LASER_CYAN = (0, 255, 255)     # Maximum intensity cyan
        self.COLOR_CYAN_GLOW = (0, 180, 220)      # Outer border glow
        self.COLOR_HOT_PINK = (255, 0, 128)       # Ultra neon magenta
        self.COLOR_ELECTRIC_YELLOW = (255, 230, 0) # High-lumens yellow
        self.COLOR_PURE_WHITE = (255, 255, 255)   # Header text
        
        # Backgrounds with high contrast against bright neon
        self.COLOR_PANEL_BG = (20, 14, 40)        # Dark high-contrast panel box
        self.COLOR_BAR_BG = (45, 35, 75)          # Bar background
        
        # Initialize Pygame fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_stats = pygame.font.SysFont("Consolas", 16, bold=True)
        
        # Load save data upon initialization
        self.load_economy_data()

    @property
    def target_xp(self):
        """Calculates required XP dynamically based on level."""
        return int(100 * (1.5 ** (self.level - 1)))

    def load_economy_data(self):
        """Loads credits, xp, level, and location from JSON."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as file:
                    data = json.load(file)
                    economy = data.get("economy", {})
                    self.credits = economy.get("credits", 0)
                    self.xp = economy.get("xp", 0)
                    self.level = min(economy.get("level", 1), self.MAX_LEVEL)
                    self.location = economy.get("location", "Back Alley Kiosk")
            except (json.JSONDecodeError, IOError):
                print("[UIEconomy] Warning: Corrupted save_data.json file. Initializing defaults.")
                self.save_economy_data()
        else:
            self.save_economy_data()

    def save_economy_data(self):
        """Saves current credits, xp, level, and location string to JSON."""
        data = {
            "economy": {
                "credits": self.credits,
                "xp": self.xp,
                "level": self.level,
                "location": self.location
            }
        }
        try:
            with open(self.save_file, "w") as file:
                json.dump(data, file, indent=4)
        except IOError:
            print("[UIEconomy] Error: Failed to write to save_data.json")

    def add_credits(self, amount):
        """Add credits and trigger an automatic save."""
        self.credits += amount
        self.save_economy_data()

    def add_xp(self, amount):
        """Add XP up to max level (3), update location names, and auto-save."""
        if self.level >= self.MAX_LEVEL:
            self.xp = self.target_xp
            self.save_economy_data()
            return

        self.xp += amount
        while self.xp >= self.target_xp and self.level < self.MAX_LEVEL:
            self.xp -= self.target_xp
            self.level += 1

        if self.level >= self.MAX_LEVEL:
            self.level = self.MAX_LEVEL
            self.location = self.LOCATIONS[3]
            self.xp = self.target_xp
        elif self.level == 2:
            self.location = self.LOCATIONS[2]
        else:
            self.location = self.LOCATIONS[1]

        self.save_economy_data()

    def set_location(self, new_location_name):
        """Manually update location string and auto-save."""
        self.location = new_location_name
        self.save_economy_data()

    def get_level_bg_color(self):
        """Returns deep dark backgrounds for maximum contrast against bright neon."""
        bg_colors = [
            (11, 7, 26),     # Level 1: Deep Dark Purple
            (28, 5, 38),     # Level 2: Deep Dark Pink/Violet
            (5, 20, 36)      # Level 3: Deep Dark Cyber Cyan
        ]
        index = min(self.level - 1, len(bg_colors) - 1)
        return bg_colors[index]

    def draw(self):
        """Renders HUD overlay with high-contrast neon borders."""
        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(self.get_level_bg_color())
        
        # 16:9 Relative positioning
        padding = int(screen_w * 0.02)
        hud_w = int(screen_w * 0.32)
        hud_h = int(screen_h * 0.20)
        
        # Main HUD Box
        hud_rect = pygame.Rect(padding, padding, hud_w, hud_h)
        pygame.draw.rect(self.screen, self.COLOR_PANEL_BG, hud_rect, border_radius=8)
        
        # Neon Glow Effect (Dual-Layer Border)
        glow_rect = pygame.Rect(padding - 2, padding - 2, hud_w + 4, hud_h + 4)
        pygame.draw.rect(self.screen, self.COLOR_CYAN_GLOW, glow_rect, 1, border_radius=10)
        pygame.draw.rect(self.screen, self.COLOR_LASER_CYAN, hud_rect, 3, border_radius=8)
        
        text_x = padding + 15
        
        # 1. Location Header
        location_text = self.font_stats.render(f"LOC: {self.location.upper()}", True, self.COLOR_PURE_WHITE)
        self.screen.blit(location_text, (text_x, padding + 10))

        # 2. Credits (Electric Yellow)
        credits_text = self.font_title.render(f"CREDITS: ${self.credits}", True, self.COLOR_ELECTRIC_YELLOW)
        self.screen.blit(credits_text, (text_x, padding + 32))
        
        # 3. Level (Hot Pink)
        lvl_display = "LEVEL: 3 (MAX)" if self.level >= 3 else f"LEVEL: {self.level}"
        level_text = self.font_stats.render(lvl_display, True, self.COLOR_HOT_PINK)
        self.screen.blit(level_text, (text_x, padding + 62))
        
        # 4. Neon Progress Bar
        bar_x = text_x
        bar_y = padding + 88
        bar_w = hud_w - 30
        bar_h = 18
        
        progress_ratio = min(self.xp / self.target_xp, 1.0) if self.target_xp > 0 else 0
        fill_w = int(bar_w * progress_ratio)
        
        pygame.draw.rect(self.screen, self.COLOR_BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        if fill_w > 0:
            pygame.draw.rect(self.screen, self.COLOR_LASER_CYAN, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, self.COLOR_LASER_CYAN, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)
        
        # Progress Bar Text
        xp_str = "MAX LEVEL REACHED" if self.level >= 3 else f"{self.xp} / {self.target_xp} XP"
        xp_text = self.font_stats.render(xp_str, True, self.COLOR_PURE_WHITE)
        text_rect = xp_text.get_rect(center=(bar_x + bar_w // 2, bar_y + bar_h // 2))
        self.screen.blit(xp_text, text_rect)
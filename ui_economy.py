import pygame
import json
import os

SAVE_FILE = "save_data.json"

LOCATIONS = {
    1: "Back Alley Kiosk",
    2: "Neon Lounge",
    3: "Cyber Penthouse"
}

# Neon colour palette for each level background
BACKGROUND_COLORS = {
    1: (255, 0, 150),   # Hot Neon Pink
    2: (0, 220, 255),   # Electric Cyan
    3: (160, 30, 255)   # Bright Neon Purple
}

class EconomyHUD:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.hud_height = 60
        
        self.data = self.load_data()
        self.update_location_name()

        pygame.font.init()
        self.font = pygame.font.SysFont("Consolas", 15, bold=True)
        self.badge_font = pygame.font.SysFont("Consolas", 13, bold=True)

        # UI Colors
        self.BG_COLOR = (15, 15, 30)
        self.BORDER_COLOR = (0, 240, 255)
        self.GOLD_COLOR = (255, 215, 0)
        self.PURPLE_COLOR = (180, 70, 255)
        self.BAR_BG = (40, 40, 60)

    def load_data(self):
        """Reads player stats from save_data.json."""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "credits": 0,
            "xp": 0,
            "level": 1,
            "location_theme": "Back Alley Kiosk"
        }

    def update_location_name(self):
        """Updates location name depending on current player level (max level 3)."""
        current_lvl = min(self.data.get("level", 1), 3)
        self.data["location_theme"] = LOCATIONS.get(current_lvl, "Cyber Penthouse")

    def get_background_color(self):
        """Returns the bright neon background color matching the current level."""
        current_lvl = min(self.data.get("level", 1), 3)
        return BACKGROUND_COLORS.get(current_lvl, (160, 30, 255))

    def add_reward(self, credits_earned, xp_earned):
        """Updates XP and Credits post-shift, handling level ups (max LVL 3)."""
        self.data["credits"] += credits_earned
        
        if self.data["level"] < 3:
            self.data["xp"] += xp_earned
            
            xp_needed = self.data["level"] * 100
            while self.data["xp"] >= xp_needed and self.data["level"] < 3:
                self.data["xp"] -= xp_needed
                self.data["level"] += 1
                xp_needed = self.data["level"] * 100
                
            self.update_location_name()
            
        self.save_data()

    def save_data(self):
        """Saves current state back to save_data.json."""
        with open(SAVE_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def draw(self, surface):
        """Renders Top Banner with Credits, LVL, XP Text, Progress Bar, and Zone."""
        credits = self.data.get("credits", 0)
        xp = self.data.get("xp", 0)
        level = min(self.data.get("level", 1), 3)
        theme = self.data.get("location_theme", "Back Alley Kiosk")

        # Top banner background & border line
        hud_rect = pygame.Rect(0, 0, self.screen_width, self.hud_height)
        pygame.draw.rect(surface, self.BG_COLOR, hud_rect)
        pygame.draw.line(surface, self.BORDER_COLOR, (0, self.hud_height), (self.screen_width, self.hud_height), 2)

        # Credits section
        credits_text = self.font.render(f"CREDITS: ${credits}", True, self.GOLD_COLOR)
        surface.blit(credits_text, (20, 20))

        # Level, XP and XP progress bar
        level_label = self.font.render(f"LVL {level}", True, self.PURPLE_COLOR)
        surface.blit(level_label, (self.screen_width // 2 - 140, 20))

        bar_x = self.screen_width // 2 - 70
        bar_y = 23
        bar_w = 120
        bar_h = 14

        if level >= 3:
            xp_text = self.font.render("XP: MAX", True, self.PURPLE_COLOR)
            progress = 1.0
        else:
            xp_needed = level * 100
            progress = min(xp / xp_needed, 1.0)
            xp_text = self.font.render(f"XP: {xp}/{xp_needed}", True, self.PURPLE_COLOR)

        surface.blit(xp_text, (bar_x + bar_w + 10, 20))

        # XP progress bar
        pygame.draw.rect(surface, self.BAR_BG, (bar_x, bar_y, bar_w, bar_h))
        if progress > 0:
            pygame.draw.rect(surface, self.PURPLE_COLOR, (bar_x, bar_y, int(bar_w * progress), bar_h))
        pygame.draw.rect(surface, self.BORDER_COLOR, (bar_x, bar_y, bar_w, bar_h), 1)

        # Location Text
        theme_text = self.badge_font.render(f"ZONE: {theme.upper()}", True, self.BORDER_COLOR)
        surface.blit(theme_text, (self.screen_width - theme_text.get_width() - 20, 20))
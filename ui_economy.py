import json
import os
import pygame

class UIEconomy:
    SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_data.json")
    
    STARTING_CREDITS = 100
    STARTING_XP = 0
    STARTING_LEVEL = 1
    MAX_LEVEL = 3
    MIN_CREDITS = 0

    # XP targets required per level
    LEVEL_XP_REQUIREMENTS = {
        1: 500,
        2: 1200,
        3: 2500
    }

    LOCATIONS = {
        1: "Back Alley Kiosk",
        2: "Neon Lounge",
        3: "Cyber Penthouse",
    }

    # Cyberpunk Theme Palette
    COLOR_BG_SOLID = (12, 14, 22)       # Solid dark chassis
    COLOR_BORDER = (0, 240, 255)       # Cyan border glow
    COLOR_TEXT = (240, 245, 255)       # Soft white text
    COLOR_GOLD = (255, 200, 0)         # Credits gold
    COLOR_PINK = (255, 0, 110)         # Combo pink / XP high-fill
    COLOR_CYAN = (0, 240, 255)         # XP low-fill
    COLOR_SEG_EMPTY = (30, 35, 50)    # Empty XP segment

    def __init__(self, screen, player_name="Player"):
        self.screen = screen
        self.player_name = str(player_name).strip() if player_name else "Player"
        if not self.player_name:
            self.player_name = "Player"

        self.credits = self.STARTING_CREDITS
        self.xp = self.STARTING_XP
        self.level = self.STARTING_LEVEL
        self.location = self.LOCATIONS[self.STARTING_LEVEL]

        self.load_economy_data()

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

    def serve_order(self, is_correct=True):
        return True

    def sync_progression(self, progression):
        if progression is None:
            return False

        try:
            self.level = int(progression.level)
        except (TypeError, ValueError):
            self.level = self.STARTING_LEVEL

        self.level = max(1, min(self.level, self.MAX_LEVEL))

        try:
            self.xp = max(0, int(progression.xp))
        except (TypeError, ValueError):
            self.xp = self.STARTING_XP

        if hasattr(progression, "get_current_location"):
            location = progression.get_current_location()
            if location in self.LOCATIONS.values():
                self.location = location
            else:
                self.location = self.LOCATIONS.get(self.level, self.LOCATIONS[1])
        else:
            self.location = self.LOCATIONS.get(self.level, self.LOCATIONS[1])

        self.save_economy_data()
        return True

    def set_level(self, level):
        try:
            level = int(level)
        except (TypeError, ValueError):
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

        all_profiles[self.player_name] = {
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "location": self.location,
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

                    self.save_economy_data()
                    return
            except (IOError, json.JSONDecodeError, TypeError, ValueError):
                pass

        self.credits = self.STARTING_CREDITS
        self.xp = self.STARTING_XP
        self.level = self.STARTING_LEVEL
        self.location = self.LOCATIONS[self.STARTING_LEVEL]
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
        }

    # =========================================================================
    # CYBERPUNK HUD DRAWING IMPLEMENTATION
    # =========================================================================
    def draw_hud(self, combo_count=1):
        """Draws the top Cyber-Deck HUD header constrained before MAP/LEADERBOARD buttons."""
        screen_w = self.screen.get_width()
        
        # Dimensions (Constrained width to stop before MAP & LEADERBOARD buttons)
        hud_height = 65
        hud_width = min(680, screen_w - 320)
        hud_rect = pygame.Rect(10, 10, hud_width, hud_height)

        # Draw SOLID background panel
        pygame.draw.rect(self.screen, self.COLOR_BG_SOLID, hud_rect, border_radius=4)

        # Cyber Chassis Border & Corner Cut Accents
        pygame.draw.rect(self.screen, self.COLOR_BORDER, hud_rect, 2, border_radius=4)
        pygame.draw.line(self.screen, self.COLOR_CYAN, (hud_rect.x + 5, hud_rect.y), (hud_rect.x + 35, hud_rect.y), 4)
        pygame.draw.line(self.screen, self.COLOR_CYAN, (hud_rect.right - 35, hud_rect.bottom), (hud_rect.right - 5, hud_rect.bottom), 4)

        # Fonts
        font_main = pygame.font.SysFont("Consolas", 15, bold=True)
        font_sub = pygame.font.SysFont("Consolas", 12, bold=True)

        # 1. Barista Name & 2. Location (Left Block)
        name_txt = font_main.render(f"BARISTA: {self.player_name.upper()}", True, self.COLOR_BORDER)
        loc_txt = font_sub.render(f"LOCATION: {self.location.upper()}", True, self.COLOR_TEXT)
        self.screen.blit(name_txt, (hud_rect.x + 12, hud_rect.y + 12))
        self.screen.blit(loc_txt, (hud_rect.x + 12, hud_rect.y + 36))

        # Divider line 1
        pygame.draw.line(self.screen, (50, 60, 80), (hud_rect.x + 220, hud_rect.y + 10), (hud_rect.x + 220, hud_rect.bottom - 10), 1)

        # 3. Level & 4. XP Bar (Center Block)
        xp_x = hud_rect.x + 232
        target_xp = self.LEVEL_XP_REQUIREMENTS.get(self.level, 2500)
        
        lvl_txt = font_main.render(f"LVL {self.level}", True, self.COLOR_CYAN)
        xp_num_txt = font_sub.render(f"{self.xp}/{target_xp} XP", True, self.COLOR_TEXT)
        
        self.screen.blit(lvl_txt, (xp_x, hud_rect.y + 12))
        self.screen.blit(xp_num_txt, (xp_x + 65, hud_rect.y + 14))

        # Segmented XP Bar
        bar_x = xp_x
        bar_y = hud_rect.y + 38
        bar_w = 175
        bar_h = 12
        num_segments = 10
        seg_gap = 2
        seg_w = (bar_w - (seg_gap * (num_segments - 1))) // num_segments

        # Calculate filled segments ratio
        xp_ratio = min(1.0, max(0.0, self.xp / float(target_xp)))
        filled_segments = int(xp_ratio * num_segments)

        for i in range(num_segments):
            seg_x = bar_x + i * (seg_w + seg_gap)
            seg_rect = pygame.Rect(seg_x, bar_y, seg_w, bar_h)

            if i < filled_segments:
                color = self.COLOR_PINK if i >= 7 else self.COLOR_CYAN
                pygame.draw.rect(self.screen, color, seg_rect)
            else:
                pygame.draw.rect(self.screen, self.COLOR_SEG_EMPTY, seg_rect)
            
            pygame.draw.rect(self.screen, (10, 15, 25), seg_rect, 1)

        # Divider line 2
        pygame.draw.line(self.screen, (50, 60, 80), (hud_rect.x + 425, hud_rect.y + 10), (hud_rect.x + 425, hud_rect.bottom - 10), 1)

        # 5. Credits Display
        cred_x = hud_rect.x + 438
        cred_lbl = font_sub.render("CREDITS", True, (150, 160, 180))
        cred_val = font_main.render(f"${self.credits:,}", True, self.COLOR_GOLD)

        self.screen.blit(cred_lbl, (cred_x, hud_rect.y + 12))
        self.screen.blit(cred_val, (cred_x, hud_rect.y + 32))

        # Divider line 3
        pygame.draw.line(self.screen, (50, 60, 80), (hud_rect.x + 550, hud_rect.y + 10), (hud_rect.x + 550, hud_rect.bottom - 10), 1)

        # 6. Combo Counter Display (Inside HUD Chassis)
        combo_x = hud_rect.x + 562
        combo_txt = font_main.render("COMBO", True, self.COLOR_PINK)
        combo_val = font_main.render(f"x{combo_count}", True, self.COLOR_PINK)

        self.screen.blit(combo_txt, (combo_x, hud_rect.y + 12))
        self.screen.blit(combo_val, (combo_x, hud_rect.y + 32))

    def draw(self, combo_count=1, dt=0):
        """Standard draw call forwarder."""
        self.draw_hud(combo_count=combo_count)
import json
import os
import pygame


class UIEconomy:
    SAVE_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "save_data.json"
    )

    LOCATIONS = {
        1: "NEON ALLEY CAFE",
        2: "CYBER DOCK COFFEE",
        3: "HIGH-RISE BAR",
    }

    NEON_COLORS = {
        1: {"primary": (0, 255, 204), "accent": (0, 200, 255), "bg": (15, 10, 25)},
        2: {"primary": (255, 0, 128), "accent": (255, 100, 0), "bg": (25, 10, 20)},
        3: {"primary": (180, 0, 255), "accent": (0, 255, 150), "bg": (20, 5, 30)},
    }

    def __init__(self, screen, player_name="Player"):
        self.screen = screen
        self.player_name = player_name.strip() if player_name else "Player"

        self.credits = 100
        self.xp = 0  # XP starts at 0 and only goes UP for the leaderboard
        self.level = 1
        self.location = self.LOCATIONS[1]

        self.load_economy_data()

    def serve_order(self, is_correct: bool):
        """Earns credits (spendable) and XP (lifetime score) independently."""
        if is_correct:
            self.credits += 25  # Spendable currency goes up
            self.xp += 50       # Leaderboard XP goes up more for correct orders
        else:
            self.credits = max(0, self.credits - 5)  # Penalty only hits spendable credits
            # XP is never lost on mistakes, preserving lifetime progress!

        self.save_economy_data()

    def spend_credits(self, amount: int) -> bool:
        """Call this when buying map levels or upgrades using credits only."""
        if self.credits >= amount:
            self.credits -= amount
            self.save_economy_data()
            return True
        return False

    def reset_economy(self):
        self.credits = 100
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]
        self.save_economy_data()

    def save_economy_data(self):
        all_profiles = {}

        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    all_profiles = json.load(f)
            except (IOError, json.JSONDecodeError):
                all_profiles = {}

        all_profiles[self.player_name] = {
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "location": self.location,
        }

        try:
            with open(self.SAVE_FILE, "w") as f:
                json.dump(all_profiles, f, indent=4)
        except IOError as e:
            print(f"[ECONOMY ERROR] Could not save economy data: {e}")

    def load_economy_data(self):
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    all_profiles = json.load(f)

                if self.player_name in all_profiles:
                    p_data = all_profiles[self.player_name]
                    self.credits = p_data.get("credits", 100)
                    self.xp = p_data.get("xp", 0)  # Loaded independently
                    self.level = p_data.get("level", 1)
                    self.location = self.LOCATIONS.get(self.level, f"Sector {self.level} Hub")
                    print(f"[ECONOMY] Loaded profile for '{self.player_name}'")
                    return
            except (IOError, json.JSONDecodeError) as e:
                print(f"[ECONOMY ERROR] Could not parse save file ({e}). Starting fresh.")

        print(f"[ECONOMY] Initialized new profile for '{self.player_name}'")
        self.credits = 100
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]
        self.save_economy_data()

    def get_level_bg_color(self):
        palette = self.NEON_COLORS.get(
            self.level, self.NEON_COLORS[3 if self.level > 3 else 1]
        )
        return palette["bg"]

    def draw(self):
        screen_w, screen_h = self.screen.get_size()

        padding = int(screen_w * 0.02)
        hud_w = int(screen_w * 0.35)
        hud_h = int(screen_h * 0.17)

        palette = self.NEON_COLORS.get(
            self.level, self.NEON_COLORS[3 if self.level > 3 else 1]
        )
        primary_color = palette["primary"]
        accent_color = palette["accent"]

        dashboard_rect = pygame.Rect(padding, padding, hud_w, hud_h)

        hud_surface = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        hud_surface.fill((15, 10, 25, 210))
        self.screen.blit(hud_surface, (padding, padding))

        pygame.draw.rect(
            self.screen, primary_color, dashboard_rect, width=2, border_radius=8
        )

        title_size = max(14, int(screen_h * 0.028))
        body_size = max(12, int(screen_h * 0.022))

        font_title = pygame.font.SysFont("Consolas", title_size, bold=True)
        font_body = pygame.font.SysFont("Consolas", body_size)

        # Header: Barista Name & Map Level
        header_str = f"BARISTA: {self.player_name.upper()} | MAP LVL {self.level}"
        header_txt = font_title.render(header_str, True, primary_color)
        self.screen.blit(header_txt, (padding + 12, padding + int(hud_h * 0.12)))

        # Location Info
        loc_str = f"LOC: {self.location.upper()}"
        loc_txt = font_body.render(loc_str, True, (200, 220, 255))
        self.screen.blit(loc_txt, (padding + 12, padding + int(hud_h * 0.40)))

        # Distinct Credits and XP Display
        stats_str = f"CREDITS: ${self.credits} | XP: {self.xp}"
        stats_txt = font_body.render(stats_str, True, (255, 255, 255))
        self.screen.blit(stats_txt, (padding + 12, padding + int(hud_h * 0.68)))

        # Top Right Prompts
        map_prompt_str = "[PRESS 'M' FOR MAP]"
        map_prompt_txt = font_body.render(map_prompt_str, True, accent_color)
        prompt_rect = map_prompt_txt.get_rect(topright=(screen_w - padding, padding + 4))
        self.screen.blit(map_prompt_txt, prompt_rect)

        lb_prompt_str = "[PRESS 'L' FOR LEADERBOARD]"
        lb_prompt_txt = font_body.render(lb_prompt_str, True, (255, 0, 128))
        lb_rect = lb_prompt_txt.get_rect(topright=(screen_w - padding, padding + 32))
        self.screen.blit(lb_prompt_txt, lb_rect)
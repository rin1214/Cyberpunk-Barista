import json
import os
import pygame


class UIEconomy:

    # 16:9 Neon Level Palette & Location Names
    NEON_COLORS = {
        1: {
            "primary": (186, 85, 211),
            "accent": (255, 105, 180),
            "bg": (25, 15, 35),
        },  # Level 1: Back Alley Kiosk (Neon Purple / Pink)
        2: {
            "primary": (0, 245, 255),
            "accent": (50, 205, 50),
            "bg": (10, 25, 40),
        },  # Level 2: Neon Lounge (Cyber Cyan / Lime)
        3: {
            "primary": (255, 215, 0),
            "accent": (255, 69, 0),
            "bg": (35, 20, 10),
        },  # Level 3+: Cyber Penthouse (Gold / Orange Fire)
    }

    LOCATIONS = {
        1: "Back Alley Kiosk",
        2: "Neon Lounge",
        3: "Cyber Penthouse",
    }

    SAVE_FILE = "save_data.json"

    def __init__(self, screen, player_name="Player"):
        self.screen = screen
        self.player_name = player_name.strip() if player_name else "Player"
        
        # State Defaults
        self.credits = 100
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]

        # Load specific saved data for this player name
        self.load_economy_data()

    def get_xp_for_next_level(self):
        """Calculates total XP needed for current level advancement."""
        return self.level * 100

    def serve_order(self, is_correct: bool):
        """
        Updates economy on order completion.
        Correct: +20 Credits, +30 XP.
        Incorrect: -$5 Waste Fee, +0 XP.
        """
        if is_correct:
            self.credits += 20
            self.xp += 30
            self.check_level_up()
        else:
            self.credits = max(0, self.credits - 5)  # Prevents negative credits

        self.save_economy_data()

    def check_level_up(self):
        """Handles multi-level progression dynamic logic without a level cap."""
        while self.xp >= self.get_xp_for_next_level():
            self.xp -= self.get_xp_for_next_level()
            self.level += 1
            self.location = self.LOCATIONS.get(
                self.level, f"Sector {self.level} Hub"
            )

    def reset_economy(self):
        """Resets economy for current player and updates save file back to defaults."""
        self.credits = 100
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]
        self.save_economy_data()

    def save_economy_data(self):
        """Persists current player state into JSON file under their player name key."""
        all_profiles = {}
        
        # Read existing profiles first so we don't overwrite other players
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    all_profiles = json.load(f)
            except (IOError, json.JSONDecodeError):
                all_profiles = {}

        # Save active player's profile data
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
        """Loads state from JSON file if profile for self.player_name is present."""
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    all_profiles = json.load(f)
                
                # Retrieve specifically for this player name
                if self.player_name in all_profiles:
                    p_data = all_profiles[self.player_name]
                    self.credits = p_data.get("credits", 100)
                    self.xp = p_data.get("xp", 0)
                    self.level = p_data.get("level", 1)
                    self.location = self.LOCATIONS.get(
                        self.level, f"Sector {self.level} Hub"
                    )
                    print(f"[ECONOMY] Loaded profile for '{self.player_name}'")
                    return
            except (IOError, json.JSONDecodeError) as e:
                print(f"[ECONOMY ERROR] Could not parse save file ({e}). Starting fresh.")

        # Default setup if profile does not exist yet
        print(f"[ECONOMY] Initialized new profile for '{self.player_name}'")
        self.credits = 100
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]
        self.save_economy_data()

    def get_level_bg_color(self):
        """Returns the dark background fallback tint matching level."""
        palette = self.NEON_COLORS.get(self.level, self.NEON_COLORS[3 if self.level > 3 else 1])
        return palette["bg"]

    def draw(self):
        """Renders HUD overlay with high-contrast neon borders top-left."""
        screen_w, screen_h = self.screen.get_size()

        # 16:9 Relative positioning
        padding = int(screen_w * 0.02)
        hud_w = int(screen_w * 0.35)
        hud_h = int(screen_h * 0.22)

        # Use Level 3 palette styling for levels > 3
        palette = self.NEON_COLORS.get(self.level, self.NEON_COLORS[3 if self.level > 3 else 1])
        primary_color = palette["primary"]
        accent_color = palette["accent"]

        # Outer Neon Dashboard Container
        dashboard_rect = pygame.Rect(padding, padding, hud_w, hud_h)

        # Semi-transparent dark backing box for readability
        hud_surface = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        hud_surface.fill((15, 10, 25, 210))
        self.screen.blit(hud_surface, (padding, padding))

        # Glowing Border
        pygame.draw.rect(
            self.screen, primary_color, dashboard_rect, width=2, border_radius=8
        )

        # Fonts Setup
        title_size = max(14, int(screen_h * 0.028))
        body_size = max(12, int(screen_h * 0.022))

        font_title = pygame.font.SysFont("Consolas", title_size, bold=True)
        font_body = pygame.font.SysFont("Consolas", body_size)

        # Header Text (Player Name & Level)
        header_str = f"BARISTA: {self.player_name.upper()} | LVL {self.level}"
        header_txt = font_title.render(header_str, True, primary_color)
        self.screen.blit(
            header_txt, (padding + 12, padding + int(hud_h * 0.08))
        )

        # Location Text
        loc_str = f"LOC: {self.location.upper()}"
        loc_txt = font_body.render(loc_str, True, (200, 220, 255))
        self.screen.blit(
            loc_txt, (padding + 12, padding + int(hud_h * 0.32))
        )

        # Credits Text
        credits_str = f"CREDITS: ${self.credits}"
        credits_txt = font_body.render(credits_str, True, (255, 255, 255))
        self.screen.blit(
            credits_txt, (padding + 12, padding + int(hud_h * 0.52))
        )

        # XP Progress Bar Setup
        bar_x = padding + 12
        bar_y = padding + int(hud_h * 0.74)
        bar_w = hud_w - 24
        bar_h = int(hud_h * 0.18)

        target_xp = self.get_xp_for_next_level()
        xp_str = f"XP: {self.xp}/{target_xp}"
        fill_ratio = min(1.0, max(0.0, self.xp / target_xp))

        fill_w = int(bar_w * fill_ratio)

        # XP Track Background
        pygame.draw.rect(
            self.screen, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=4
        )

        # XP Filled Bar
        if fill_w > 0:
            pygame.draw.rect(
                self.screen,
                accent_color,
                (bar_x, bar_y, fill_w, bar_h),
                border_radius=4,
            )

        # XP Track Border
        pygame.draw.rect(
            self.screen, primary_color, (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=4
        )

        # XP Numeric Text Overlay
        xp_txt = font_body.render(xp_str, True, (255, 255, 255))
        xp_rect = xp_txt.get_rect(center=(bar_x + bar_w // 2, bar_y + bar_h // 2))
        self.screen.blit(xp_txt, xp_rect)
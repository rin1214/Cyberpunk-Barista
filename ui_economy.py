import json
import os
import random
import pygame


class LevelParticle:
    """Explosive particle FX spawned during level-up events."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-7, -2)
        self.radius = random.randint(3, 6)
        self.lifetime = 35  # Frames to render
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(
                surface, self.color, (int(self.x), int(self.y)), self.radius
            )


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

    def __init__(self, screen):
        self.screen = screen
        self.credits = 100
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]

        # Smooth XP interpolation tracker
        self.display_xp = 0.0

        # Visual FX state management
        self.particles = []
        self.level_up_banner_timer = 0

        # Load saved data if available
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
        leveled_up = False
        while self.xp >= self.get_xp_for_next_level():
            self.xp -= self.get_xp_for_next_level()
            self.display_xp = 0.0  # Reset animated tracker for new level
            self.level += 1
            self.location = self.LOCATIONS.get(
                self.level, f"Sector {self.level} Hub"
            )
            leveled_up = True

        if leveled_up:
            # Trigger Visual FX
            self.level_up_banner_timer = 90  # ~1.5 seconds at 60 FPS
            palette = self.NEON_COLORS.get(
                self.level, self.NEON_COLORS[3 if self.level > 3 else 1]
            )

            # Spawn particle burst around top HUD box
            screen_w, screen_h = self.screen.get_size()
            center_x = int(screen_w * 0.18)
            center_y = int(screen_h * 0.12)
            for _ in range(45):
                self.particles.append(
                    LevelParticle(center_x, center_y, palette["accent"])
                )

    def reset_economy(self):
        """Resets economy and save file back to defaults."""
        self.credits = 100
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]
        self.display_xp = 0.0
        self.save_economy_data()

    def save_economy_data(self):
        """Persists current state into JSON file."""
        data = {
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "location": self.location,
        }
        try:
            with open(self.SAVE_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"[ECONOMY ERROR] Could not save economy data: {e}")

    def load_economy_data(self):
        """Loads state from JSON file if present."""
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    data = json.load(f)
                    self.credits = data.get("credits", 100)
                    self.xp = data.get("xp", 0)
                    self.level = data.get("level", 1)
                    self.location = self.LOCATIONS.get(
                        self.level, f"Sector {self.level} Hub"
                    )
                    self.display_xp = float(self.xp)
            except (IOError, json.JSONDecodeError) as e:
                print(f"[ECONOMY ERROR] Corrupt save file, resetting. ({e})")
                self.reset_economy()

    def get_level_bg_color(self):
        """Returns the dark background fallback tint matching level."""
        palette = self.NEON_COLORS.get(
            self.level, self.NEON_COLORS[3 if self.level > 3 else 1]
        )
        return palette["bg"]

    def draw(self):
        """Renders HUD overlay with high-contrast neon borders top-left."""
        screen_w, screen_h = self.screen.get_size()

        # 16:9 Relative positioning
        padding = int(screen_w * 0.02)
        hud_w = int(screen_w * 0.32)
        hud_h = int(screen_h * 0.20)

        # Use Level 3 palette styling for levels > 3
        palette = self.NEON_COLORS.get(
            self.level, self.NEON_COLORS[3 if self.level > 3 else 1]
        )
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
        title_size = max(14, int(screen_h * 0.03))
        body_size = max(12, int(screen_h * 0.025))

        font_title = pygame.font.SysFont("Consolas", title_size, bold=True)
        font_body = pygame.font.SysFont("Consolas", body_size)

        # Header Text (Location & Level)
        header_str = f"LVL {self.level} | {self.location.upper()}"
        header_txt = font_title.render(header_str, True, primary_color)
        self.screen.blit(
            header_txt, (padding + 12, padding + int(hud_h * 0.1))
        )

        # Credits Text
        credits_str = f"CREDITS: ${self.credits}"
        credits_txt = font_body.render(credits_str, True, (255, 255, 255))
        self.screen.blit(
            credits_txt, (padding + 12, padding + int(hud_h * 0.4))
        )

        # XP Progress Bar Setup
        bar_x = padding + 12
        bar_y = padding + int(hud_h * 0.70)
        bar_w = hud_w - 24
        bar_h = int(hud_h * 0.16)

        target_xp = self.get_xp_for_next_level()

        # Smooth XP Interpolation (10% step each frame toward current target XP)
        self.display_xp += (self.xp - self.display_xp) * 0.10

        fill_ratio = min(1.0, max(0.0, self.display_xp / target_xp))
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
        xp_str = f"XP: {int(self.display_xp)}/{target_xp}"
        xp_txt = font_body.render(xp_str, True, (255, 255, 255))
        xp_rect = xp_txt.get_rect(center=(bar_x + bar_w // 2, bar_y + bar_h // 2))
        self.screen.blit(xp_txt, xp_rect)

        # -------------------------------------------------------------
        # Level Up Particle Effects & Center Banner Overlay
        # -------------------------------------------------------------
        for p in self.particles[:]:
            p.update()
            p.draw(self.screen)
            if p.lifetime <= 0:
                self.particles.remove(p)

        if self.level_up_banner_timer > 0:
            self.level_up_banner_timer -= 1

            banner_size = max(16, int(screen_h * 0.04))
            banner_font = pygame.font.SysFont("Consolas", banner_size, bold=True)
            banner_str = f"LEVEL UP! WELCOME TO {self.location.upper()}"
            banner_txt = banner_font.render(banner_str, True, accent_color)

            banner_rect = banner_txt.get_rect(
                center=(screen_w // 2, int(screen_h * 0.15))
            )

            # Dark Backing Container with Glowing Border
            bg_rect = banner_rect.inflate(32, 16)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((10, 10, 20, 230))

            self.screen.blit(bg_surface, bg_rect.topleft)
            pygame.draw.rect(
                self.screen, accent_color, bg_rect, width=2, border_radius=8
            )
            self.screen.blit(banner_txt, banner_rect)
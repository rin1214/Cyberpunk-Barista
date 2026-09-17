import json
import os
import random
import pygame


class Particle:
    """Cyberpunk neon particle FX for level-up and order rewards."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.color = color
        self.alpha = 255
        self.radius = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 5
        if self.radius > 0.5:
            self.radius -= 0.1

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(s, (self.x - self.radius, self.y - self.radius))


class UIEconomy:
    LOCATIONS = {
        1: "Back Alley Kiosk",
        2: "Neon Lounge",
        3: "Cyber Penthouse"
    }

    XP_PER_LEVEL = 100

    def __init__(self, screen, save_file="save_data.json"):
        self.screen = screen
        self.save_file = save_file

        # Default Progression State
        self.credits = 0
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]

        # UI Animation Properties
        self.displayed_xp = 0.0
        self.particles = []
        self.banner_timer = 0  # Frame counter for Level-Up banner

        # Load saved data
        self.load_economy_data()

        # Fonts setup
        self.font_large = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 18)
        self.font_banner = pygame.font.SysFont("Consolas", 42, bold=True)

    def serve_order(self, is_correct=True):
        """Processes order outcome: updates credits, gains XP, and triggers FX."""
        if is_correct:
            self.credits += 20
            self.add_xp(30)
            self._spawn_particles(color=(0, 255, 200))  # Cyan/Teal particle burst
        else:
            self.credits = max(0, self.credits - 10)    # UPDATED: -$10 Waste fee penalty
            self._spawn_particles(color=(255, 50, 50))  # Red warning particle burst

        self.save_economy_data()

    def add_xp(self, amount):
        """Adds XP and handles leveling thresholds."""
        self.xp += amount
        while self.xp >= self.XP_PER_LEVEL:
            self.xp -= self.XP_PER_LEVEL
            self.level += 1
            self.location = self.LOCATIONS.get(self.level, f"Sector {self.level} Hub")
            self.banner_timer = 120  # Show banner for ~2 seconds (120 frames @ 60FPS)
            self._spawn_particles(color=(255, 0, 220), count=50) # Magenta explosion

    def _spawn_particles(self, color, count=20):
        for _ in range(count):
            self.particles.append(Particle(150, 50, color))

    def draw(self):
        """Renders the economy HUD top-bar and floating particles."""
        # 1. Smooth XP Bar Lerp Animation
        target_xp = self.xp
        self.displayed_xp += (target_xp - self.displayed_xp) * 0.1

        # 2. Draw Top HUD Background Bar
        hud_bg = pygame.Surface((self.screen.get_width(), 60), pygame.SRCALPHA)
        hud_bg.fill((10, 10, 20, 200))  # Semi-transparent dark overlay
        self.screen.blit(hud_bg, (0, 0))

        # 3. Draw Text Displays (Credits, Level, Location)
        cred_text = self.font_large.render(f"CREDITS: ${self.credits}", True, (0, 255, 200))
        lvl_text = self.font_large.render(f"LVL {self.level}", True, (255, 0, 220))
        loc_text = self.font_small.render(f"LOCATION: {self.location}", True, (200, 200, 200))

        self.screen.blit(cred_text, (20, 15))
        self.screen.blit(lvl_text, (260, 15))
        self.screen.blit(loc_text, (380, 22))

        # 4. Draw XP Progress Bar
        bar_x, bar_y, bar_w, bar_h = 700, 20, 200, 18
        pygame.draw.rect(self.screen, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        fill_w = int((self.displayed_xp / self.XP_PER_LEVEL) * bar_w)
        if fill_w > 0:
            pygame.draw.rect(self.screen, (255, 0, 220), (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, (0, 255, 200), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)

        # 5. Update & Draw Particles
        for p in self.particles[:]:
            p.update()
            p.draw(self.screen)
            if p.alpha <= 0:
                self.particles.remove(p)

        # 6. Render Level-Up Banner Overlay
        if self.banner_timer > 0:
            self.banner_timer -= 1
            banner_surf = self.font_banner.render("LEVEL UP! NEW LOCATION UNLOCKED!", True, (255, 255, 0))
            rect = banner_surf.get_rect(center=(self.screen.get_width() // 2, 120))
            self.screen.blit(banner_surf, rect)

    def load_economy_data(self):
        """Loads progression from JSON storage file."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    data = json.load(f)
                    self.credits = data.get("credits", 0)
                    self.xp = data.get("xp", 0)
                    self.level = data.get("level", 1)
                    self.location = data.get("location", self.LOCATIONS[1])
                    self.displayed_xp = float(self.xp)
            except Exception as e:
                print(f"[ECONOMY ERROR] Could not read {self.save_file}: {e}")

    def save_economy_data(self):
        """Saves current state to JSON file."""
        data = {
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "location": self.location
        }
        try:
            with open(self.save_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[ECONOMY ERROR] Could not write to {self.save_file}: {e}")

    def reset_economy(self):
        """Resets saved economy progression back to Level 1."""
        self.credits = 0
        self.xp = 0
        self.level = 1
        self.location = self.LOCATIONS[1]
        self.displayed_xp = 0.0
        self.save_economy_data()
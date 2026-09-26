"""CYBERPUNK CAFÉ — Loading Screen (reusable, all three levels)"""

import os
import pygame


class LoadingScreen:
    WIDTH, HEIGHT, FPS = 1280, 720, 60
    DEFAULT_DURATION = 5.8

    LEVEL_INFO = {
        1: ("BACK ALLEY KIOSK", "SECTOR 01"),
        2: ("NEON LOUNGE",      "SECTOR 02"),
        3: ("CYBER PENTHOUSE",  "SECTOR 03"),
    }
    MESSAGES = [
        "Initializing Café Network...",
        "Syncing Customer Database...",
        "Calibrating Drink Dispenser...",
        "Preparing Neon Menu...",
        "Warming Coffee Machines...",
        "Connecting Café Systems...",
        "Almost Ready...",
    ]

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        root = os.path.dirname(os.path.abspath(__file__))
        start_dir   = os.path.join(root, "assets", "mahirah", "start")
        loading_dir = os.path.join(root, "assets", "mahirah", "loading")

        self.background = self._load("loading_bg.png", loading_dir) \
                       or self._load("start_bg.png", start_dir)
        self.logo = self._load("logo_cyberpunk_cafe.png", start_dir)

        # Pre-scale background once and cache it
        self._bg_scaled = None
        if self.background:
            iw, ih = self.background.get_size()
            scale = max(self.WIDTH / iw, self.HEIGHT / ih)
            size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            self._bg_scaled = (pygame.transform.smoothscale(self.background, size),
                               ((self.WIDTH - size[0]) // 2, (self.HEIGHT - size[1]) // 2))

        # Pre-scale logo once and cache it
        self._logo_scaled = None
        if self.logo:
            iw, ih = self.logo.get_size()
            scale = min(430 / iw, 145 / ih)
            size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            img = pygame.transform.smoothscale(self.logo, size)
            self._logo_scaled = (img, img.get_rect(center=(640, 105)))

        # Pre-build overlay surface
        self._overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((5, 8, 20, 35))

        # Fonts
        def font(size, bold=False):
            return pygame.font.SysFont("Consolas", size, bold=bold)

        self.f_title   = font(30, True)
        self.f_name    = font(25, True)
        self.f_msg     = font(19, True)
        self.f_small   = font(16)
        self.f_percent = font(24, True)

    # ------------------------------------------------------------------ helpers

    def _load(self, filename, folder):
        path = os.path.join(folder, filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            print(f"[LOADING ASSET] Loaded: {path}")
            return img
        except (pygame.error, FileNotFoundError) as e:
            print(f"[LOADING ASSET WARNING] {path}\n       {e}")
            return None

    def _blit_center(self, text, font, color, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(640, y)))

    # ------------------------------------------------------------------ draw

    def _draw_frame(self, player_name, location, sector, smooth, msg_index):
        # Background
        if self._bg_scaled:
            self.screen.blit(*self._bg_scaled)
            self.screen.blit(self._overlay, (0, 0))
        else:
            self.screen.fill((18, 15, 35))

        # Logo
        if self._logo_scaled:
            self.screen.blit(*self._logo_scaled)

        # Panel
        rect = pygame.Rect(315, 185, 650, 430)
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((8, 12, 28, 185))
        self.screen.blit(panel, rect.topleft)
        pygame.draw.rect(self.screen, (0, 220, 255),     rect, 2,  border_radius=14)
        pygame.draw.rect(self.screen, (255, 100, 200), rect.inflate(-12, -12), 1, border_radius=10)

        # Text rows
        self._blit_center(f"WELCOME, {player_name}!", self.f_name,  (255, 180, 235), 245)
        self._blit_center(location,                    self.f_title, (0, 235, 255),   285)
        self._blit_center(sector,                      self.f_small, (210, 220, 245), 315)

        # Progress bar
        x, y, w, h = 400, 350, 480, 26
        pygame.draw.rect(self.screen, (15, 20, 38), (x, y, w, h), border_radius=13)
        fill_w = int((w - 6) * max(0.0, min(1.0, smooth)))
        if fill_w:
            pygame.draw.rect(self.screen, (255, 100, 205),
                             (x + 3, y + 3, fill_w, h - 6), border_radius=10)
            hi_w = min(80, fill_w)
            pygame.draw.rect(self.screen, (80, 225, 255),
                             (x + 3 + fill_w - hi_w, y + 3, hi_w, h - 6), border_radius=10)
        pygame.draw.rect(self.screen, (0, 225, 255), (x, y, w, h), 2, border_radius=13)

        pct = self.f_percent.render(f"{int(smooth * 100)}%", True, (255, 255, 255))
        self.screen.blit(pct, pct.get_rect(midleft=(900, 363)))

        # Scrolling message
        msg  = self.MESSAGES[msg_index % len(self.MESSAGES)]
        pfx  = self.f_small.render(">>", True, (255, 100, 205))
        mtxt = self.f_msg.render(msg,  True, (220, 235, 255))
        self.screen.blit(pfx,  (410, 405))
        self.screen.blit(mtxt, (445, 403))

        # Footer
        self._blit_center("GOOD COFFEE  ✦  BRIGHTER PEOPLE",  self.f_small, (255, 190, 235), 565)
        self._blit_center("Preparing your café experience...", self.f_small, (180, 205, 235), 595)

    # ------------------------------------------------------------------ public

    def run(self, player_name="Barista", level=1, duration=DEFAULT_DURATION):
        """Display loading screen. Returns True when done, False on quit."""
        player_name = str(player_name).strip().upper() or "BARISTA"
        try:
            level = max(1, min(int(level), 3))
        except (TypeError, ValueError):
            level = 1

        location, sector = self.LEVEL_INFO[level]
        print(f"[LOADING SCREEN] Level {level} — {location} ({duration}s)")

        start = pygame.time.get_ticks()
        self.clock.tick(self.FPS)

        while True:
            elapsed = (pygame.time.get_ticks() - start) / 1000.0
            if elapsed >= duration:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

            progress = min(1.0, elapsed / duration)
            smooth   = progress * progress * (3.0 - 2.0 * progress)
            msg_idx  = min(len(self.MESSAGES) - 1, int(progress * len(self.MESSAGES)))

            self._draw_frame(player_name, location, sector, smooth, msg_idx)
            pygame.display.flip()
            self.clock.tick(self.FPS)

        # Commit full 100% frame before handing back control
        self._draw_frame(player_name, location, sector, 1.0, len(self.MESSAGES) - 1)
        pygame.display.flip()

        print(f"[LOADING SCREEN] Level {level} done.")
        return True

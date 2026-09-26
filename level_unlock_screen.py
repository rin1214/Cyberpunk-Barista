"""CYBERPUNK CAFÉ — Level Unlock Screen"""

import os
import pygame


class LevelUnlockScreen:
    WIDTH, HEIGHT, FPS = 1280, 720, 60
    DISPLAY_TIME = 4.5
    LEVEL_IMAGES = {2: "level_2_unlock.png", 3: "level_3_unlock.png"}

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self._root = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "assets", "mahirah", "unlock")
        self._cache = {}
        self.images = {lvl: self._load(fn) for lvl, fn in self.LEVEL_IMAGES.items()}

    def _load(self, filename):
        path = os.path.join(self._root, filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            print(f"[UNLOCK ASSET] Loaded: {path}")
            return img
        except (pygame.error, FileNotFoundError) as e:
            print(f"[UNLOCK ASSET ERROR] {path}\n       {e}")
            return None

    def _draw_image(self, image):
        if image is None:
            self.screen.fill((15, 10, 30))
            font = pygame.font.SysFont("Consolas", 34, bold=True)
            surf = font.render("LEVEL UNLOCKED", True, (0, 225, 255))
            self.screen.blit(surf, surf.get_rect(center=(640, 340)))
            return

        if image not in self._cache:
            iw, ih = image.get_size()
            scale = max(self.WIDTH / iw, self.HEIGHT / ih)
            size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            scaled = pygame.transform.smoothscale(image, size)
            pos = ((self.WIDTH - size[0]) // 2, (self.HEIGHT - size[1]) // 2)
            self._cache[image] = (scaled, pos)

        scaled, pos = self._cache[image]
        self.screen.blit(scaled, pos)

    def _draw_effect(self, elapsed):
        lines = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        for y in range(0, self.HEIGHT, 4):
            pygame.draw.line(lines, (255, 255, 255, 10), (0, y), (self.WIDTH, y))
        self.screen.blit(lines, (0, 0))

        glow_y = int(elapsed * 35) % self.HEIGHT
        glow = pygame.Surface((self.WIDTH, 35), pygame.SRCALPHA)
        glow.fill((120, 220, 255, 12))
        self.screen.blit(glow, (0, glow_y - 17))

    def run(self, level, duration=DISPLAY_TIME):
        """Display unlock artwork. Returns True when done, False on quit."""
        try:
            level = max(2, min(int(level), 3))
        except (TypeError, ValueError):
            level = 2

        image = self.images.get(level)
        print(f"[UNLOCK SCREEN] Level {level} — {'artwork loaded' if image else 'fallback'}")

        start = pygame.time.get_ticks()
        self.clock.tick(self.FPS)

        while True:
            elapsed = (pygame.time.get_ticks() - start) / 1000.0
            if elapsed >= duration:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            self._draw_image(image)
            self._draw_effect(elapsed)
            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.display.flip()
        return True

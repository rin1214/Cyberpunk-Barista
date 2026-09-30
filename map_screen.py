import os
import math
import pygame


class MapScreen:
    WIDTH, HEIGHT = 1280, 720
    FPS = 60

    CYAN = (55, 225, 255)
    PINK = (255, 70, 205)
    GOLD = (255, 195, 70)
    GREEN = (90, 255, 195)
    WHITE = (240, 245, 255)
    MUTED = (145, 155, 180)
    DARK = (6, 9, 24)

    def __init__(self, screen, map_manager, economy, project_root=None):
        self.screen = screen
        self.map_manager = map_manager
        self.economy = economy

        root = project_root or os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(root, "assets", "mahirah", "ui",
                            "district_map_bg.png")

        self.bg = None
        if os.path.exists(path):
            try:
                self.bg = pygame.image.load(path).convert()
                print(f"[MAP] Background loaded: {path}")
            except pygame.error as e:
                print(f"[MAP] Background error: {e}")

        self.clock = pygame.time.Clock()
        self.time = 0
        self.hovered = None

        self.title = pygame.font.SysFont("Consolas", 34, bold=True)
        self.sub = pygame.font.SysFont("Consolas", 15, bold=True)
        self.name = pygame.font.SysFont("Consolas", 19, bold=True)
        self.small = pygame.font.SysFont("Consolas", 13, bold=True)
        self.icon = pygame.font.SysFont("Segoe UI Symbol", 42, bold=True)

        self.back_rect = pygame.Rect(1040, 25, 205, 50)

    # ------------------------------------------------------------
    # BASIC DRAWING
    # ------------------------------------------------------------

    def _panel(self, rect, border):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        s.fill((*self.DARK, 215))
        self.screen.blit(s, rect.topleft)
        pygame.draw.rect(
            self.screen, border, rect, 2, border_radius=9
        )

    def _text(self, text, font, color, center):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=center))

    def _color(self, node):
        return {
            1: self.PINK,
            2: self.CYAN,
            3: self.GOLD
        }.get(node.level_req, self.CYAN)

    # ------------------------------------------------------------
    # BACKGROUND
    # ------------------------------------------------------------

    def _draw_background(self):
        w, h = self.screen.get_size()

        if self.bg:
            iw, ih = self.bg.get_size()
            scale = max(w / iw, h / ih)
            size = (int(iw * scale), int(ih * scale))
            img = pygame.transform.smoothscale(self.bg, size)

            self.screen.blit(
                img,
                ((w - size[0]) // 2, (h - size[1]) // 2)
            )
        else:
            self.screen.fill(self.DARK)

        # Extra dimming so UI remains readable.
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((4, 6, 20, 55))
        self.screen.blit(shade, (0, 0))

    # ------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------

    def _draw_header(self):
        self._panel(
            pygame.Rect(28, 20, 350, 55),
            self.PINK
        )

        self._text(
            "☕ CYBERPUNK CAFÉ",
            self.name,
            self.PINK,
            (203, 42)
        )

        self._text(
            "GOOD COFFEE  ✦  BRIGHTER PEOPLE",
            self.small,
            self.WHITE,
            (203, 63)
        )

        self._panel(
            pygame.Rect(825, 20, 195, 55),
            self.CYAN
        )

        self._text(
            f"CREDITS: ${self.economy.credits}",
            self.small,
            self.GOLD,
            (922, 47)
        )

        mouse = pygame.mouse.get_pos()
        hover = self.back_rect.collidepoint(mouse)
        color = self.PINK if hover else self.CYAN

        self._panel(self.back_rect, color)

        self._text(
            "‹  BACK TO CAFÉ",
            self.small,
            color,
            self.back_rect.center
        )

    # ------------------------------------------------------------
    # TITLE
    # ------------------------------------------------------------

    def _draw_title(self):
        w = self.screen.get_width()

        self._text(
            "DISTRICT MAP",
            self.title,
            self.CYAN,
            (w // 2, 105)
        )

        self._text(
            "SELECT YOUR NEXT CAFÉ LOCATION",
            self.sub,
            self.WHITE,
            (w // 2, 137)
        )

        pygame.draw.line(
            self.screen,
            self.CYAN,
            (w // 2 - 170, 153),
            (w // 2 + 170, 153),
            1
        )

    # ------------------------------------------------------------
    # LOCATION ICONS
    # ------------------------------------------------------------

    def _draw_icon(self, node):
        x, y = node.pos
        base = self._color(node)

        # Locked locations are intentionally dim.
        if not node.is_unlocked:
            base = tuple(max(35, int(c * 0.38)) for c in base)

        active = self.economy.level == node.level_req
        hover = self.hovered == node

        # Glow
        if active or hover:
            pulse = (math.sin(self.time * 3) + 1) / 2
            glow = pygame.Surface((180, 180), pygame.SRCALPHA)

            for r, a in [(76, 15), (68, 25), (60, 40)]:
                pygame.draw.circle(
                    glow,
                    (*base, int(a + pulse * 12)),
                    (90, 90),
                    r
                )

            self.screen.blit(glow, (x - 90, y - 90))

        # Main icon circle
        pygame.draw.circle(
            self.screen,
            self.DARK,
            (x, y),
            60
        )

        pygame.draw.circle(
            self.screen,
            base,
            (x, y),
            60,
            3
        )

        pygame.draw.circle(
            self.screen,
            base,
            (x, y),
            49,
            1
        )

        # Location-specific symbol
        if node.level_req == 1:
            symbol = "☕"
        elif node.level_req == 2:
            symbol = "✦"
        else:
            symbol = "◇"

        self._text(
            symbol,
            self.icon,
            base,
            (x, y)
        )

        # Lock
        if not node.is_unlocked:
            self._text(
                "🔒",
                self.small,
                self.WHITE,
                (x, y + 39)
            )

    # ------------------------------------------------------------
    # NODE LABEL
    # ------------------------------------------------------------

    def _draw_label(self, node):
        x, y = node.pos
        color = self._color(node)

        if not node.is_unlocked:
            color = tuple(max(45, int(c * 0.55)) for c in color)

        box = pygame.Rect(x - 120, y + 72, 240, 60)
        self._panel(box, color)

        self._text(
            node.name,
            self.name,
            self.WHITE,
            (x, y + 91)
        )

        if node.is_unlocked:
            active = self.economy.level == node.level_req
            status = "ACTIVE" if active else "UNLOCKED"
            status_color = self.GREEN if active else self.CYAN
        else:
            status = f"🔒  UNLOCK (${node.cost})"
            status_color = color

        self._text(
            status,
            self.small,
            status_color,
            (x, y + 115)
        )

    # ------------------------------------------------------------
    # ROUTE
    # ------------------------------------------------------------

    def _draw_route(self):
        nodes = list(self.map_manager.nodes.values())

        for a, b in zip(nodes, nodes[1:]):
            pygame.draw.line(
                self.screen,
                (15, 15, 35),
                a.pos,
                b.pos,
                8
            )

            color = self._color(a)

            if not a.is_unlocked:
                color = (55, 55, 75)

            pygame.draw.line(
                self.screen,
                color,
                a.pos,
                b.pos,
                3
            )

            # Moving route pulse
            p = (self.time * 0.15) % 1
            px = int(a.pos[0] + (b.pos[0] - a.pos[0]) * p)
            py = int(a.pos[1] + (b.pos[1] - a.pos[1]) * p)

            pygame.draw.circle(
                self.screen,
                self.WHITE,
                (px, py),
                4
            )

    # ------------------------------------------------------------
    # CURRENT LOCATION
    # ------------------------------------------------------------

    def _draw_current(self):
        node = next(
            (
                n for n in self.map_manager.nodes.values()
                if n.level_req == self.economy.level
            ),
            None
        )

        if not node:
            return

        rect = pygame.Rect(28, 570, 350, 105)
        self._panel(rect, self._color(node))

        self._text(
            "CURRENT LOCATION",
            self.small,
            self.WHITE,
            (110, 590)
        )

        self._text(
            node.name,
            self.name,
            self._color(node),
            (190, 618)
        )

        desc = node.description
        if len(desc) > 45:
            desc = desc[:42] + "..."

        self._text(
            desc,
            self.small,
            self.MUTED,
            (203, 650)
        )

    # ------------------------------------------------------------
    # STATUS LEGEND
    # ------------------------------------------------------------

    def _draw_legend(self):
        rect = pygame.Rect(1040, 570, 205, 105)
        self._panel(rect, self.CYAN)

        self._text(
            "DISTRICT STATUS",
            self.small,
            self.WHITE,
            (1142, 588)
        )

        entries = [
            ("ACTIVE", self.GREEN),
            ("UNLOCKED", self.CYAN),
            ("LOCKED", self.MUTED)
        ]

        for i, (label, color) in enumerate(entries):
            y = 610 + i * 19

            pygame.draw.circle(
                self.screen,
                color,
                (1065, y),
                5,
                2
            )

            self._text(
                label,
                self.small,
                color,
                (1120, y)
            )

    # ------------------------------------------------------------
    # INPUT / MAIN LOOP
    # ------------------------------------------------------------

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(self.FPS) / 1000
            self.time += dt

            self.map_manager.check_unlocks()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_m):
                        return True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button != 1:
                        continue

                    if self.back_rect.collidepoint(event.pos):
                        return True

                    for node_id, node in self.map_manager.nodes.items():
                        hitbox = pygame.Rect(
                            node.pos[0] - 75,
                            node.pos[1] - 75,
                            150,
                            220
                        )

                        if hitbox.collidepoint(event.pos):

                            if node.is_unlocked:
                                success = self.economy.set_level(
                                    node.level_req
                                )
                            else:
                                success = self.map_manager.unlock_node(
                                    node_id
                                )

                            if success:
                                self.economy.level = node.level_req
                                self.economy.location = (
                                    self.economy.LOCATIONS.get(
                                        node.level_req,
                                        node.name
                                    )
                                )
                                self.economy.save_economy_data()
                                print(
                                    f"[MAP] Selected: {node.name}"
                                )
                                return True

            # Hover
            mouse = pygame.mouse.get_pos()
            self.hovered = None

            for node in self.map_manager.nodes.values():
                hitbox = pygame.Rect(
                    node.pos[0] - 75,
                    node.pos[1] - 75,
                    150,
                    220
                )

                if hitbox.collidepoint(mouse):
                    self.hovered = node
                    break

            # Draw
            self._draw_background()
            self._draw_route()
            self._draw_header()
            self._draw_title()

            for node in self.map_manager.nodes.values():
                self._draw_icon(node)
                self._draw_label(node)

            self._draw_current()
            self._draw_legend()

            footer = self.small.render(
                "Click a location to travel or unlock  •  [M] / [ESC] Return",
                True,
                self.MUTED
            )

            self.screen.blit(
                footer,
                footer.get_rect(
                    center=(self.WIDTH // 2, self.HEIGHT - 18)
                )
            )

            pygame.display.flip()

        return True
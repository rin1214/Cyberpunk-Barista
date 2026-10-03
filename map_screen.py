import os
import math
import pygame


class MapScreen:
    W, H, FPS = 1280, 720, 60

    CYAN  = (50, 225, 255)
    PINK  = (255, 75, 205)
    GOLD  = (255, 195, 65)
    GREEN = (70, 255, 185)
    WHITE = (235, 240, 255)
    MUTED = (145, 155, 180)
    DARK  = (7, 9, 22)

    def __init__(self, screen, map_manager, economy, project_root=None):
        self.screen, self.map_manager, self.economy = screen, map_manager, economy
        self.clock = pygame.time.Clock()
        self.t, self.hover = 0, None
        root = project_root or os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(root, "assets", "ui", "district_map_bg.png")

        try:
            self.bg = pygame.image.load(path).convert()
            print(f"[MAP] Loaded: {path}")
        except (pygame.error, FileNotFoundError):
            self.bg = None
            print("[MAP] Background not found.")

        font_path = os.path.join(root, "assets", "fonts", "Orbitron-Black.ttf")
        try:
            self.title = pygame.font.Font(font_path, 46)
        except Exception:
            self.title = pygame.font.SysFont("Consolas", 39, bold=True)

        self.subtitle = pygame.font.SysFont("Consolas", 15, bold=True)
        self.name     = pygame.font.SysFont("Consolas", 18, bold=True)
        self.body     = pygame.font.SysFont("Consolas", 14, bold=True)
        self.small    = pygame.font.SysFont("Consolas", 12, bold=True)
        self.back     = pygame.Rect(1040, 24, 205, 50)

    # BASIC UI
   
    def panel(self, rect, border, alpha=205):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        s.fill((*self.DARK, alpha))
        self.screen.blit(s, rect.topleft)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=9)

    def text(self, value, font, color, pos):
        s = font.render(str(value), True, color)
        self.screen.blit(s, s.get_rect(center=pos))

    def color(self, node):
        return {1: self.PINK, 2: self.CYAN, 3: self.GOLD}.get(node.level_req, self.CYAN)

    def node_hitbox(self, node):
        return pygame.Rect(node.pos[0] - 75, node.pos[1] - 75, 150, 220)

   
    # BACKGROUND, HEADER, TITLE

    def draw_background(self):
        w, h = self.screen.get_size()
        if self.bg:
            iw, ih = self.bg.get_size()
            scale = max(w / iw, h / ih)
            size = (int(iw * scale), int(ih * scale))
            self.screen.blit(pygame.transform.smoothscale(self.bg, size), ((w - size[0]) // 2, (h - size[1]) // 2))
        else:
            self.screen.fill(self.DARK)

        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((3, 5, 18, 58))
        self.screen.blit(shade, (0, 0))

    def draw_header(self):
        self.panel(pygame.Rect(28, 24, 300, 50), self.PINK)
        self.text(f"CREDITS: ${self.economy.credits}", self.body, self.GOLD, (178, 49))

        border = self.PINK if self.back.collidepoint(pygame.mouse.get_pos()) else self.CYAN
        self.panel(self.back, border)
        self.text("‹  BACK TO CAFÉ", self.body, border, self.back.center)

    def draw_title(self):
        cx = (328 + 1040) // 2
        self.text("DISTRICT MAP", self.title, self.CYAN, (cx, 110))
        self.text("SELECT YOUR NEXT CAFÉ LOCATION", self.subtitle, self.WHITE, (cx, 142))
        pygame.draw.line(self.screen, self.CYAN, (cx - 185, 158), (cx + 185, 158), 1)

    # LOCATION ICONS

    def draw_icon(self, node):
        x, y = node.pos
        col = self.color(node)
        unlocked = node.is_unlocked
        active = self.economy.level == node.level_req
        hover = self.hover is node

        if not unlocked:
            col = tuple(max(35, int(c * 0.38)) for c in col)

        # Soft glow
        if unlocked and (active or hover):
            pulse = (math.sin(self.t * 3) + 1) / 2
            glow = pygame.Surface((180, 180), pygame.SRCALPHA)
            for radius, alpha in ((72, 12), (64, 20), (56, 32)):
                pygame.draw.circle(glow, (*col, int(alpha + pulse * 8)), (90, 90), radius)
            self.screen.blit(glow, (x - 90, y - 90))

        # Outer rings
        pygame.draw.circle(self.screen, (5, 8, 20), (x, y), 59)
        pygame.draw.circle(self.screen, col, (x, y), 59, 3)
        pygame.draw.circle(self.screen, col, (x, y), 49, 1)

        # Level-specific district icons
        if node.level_req == 1:
            pygame.draw.rect(self.screen, col, (x - 23, y - 12, 38, 28), 3, border_radius=5)
            pygame.draw.arc(self.screen, col, (x + 10, y - 7, 20, 19), -1.5, 1.5, 3)
            pygame.draw.line(self.screen, col, (x - 14, y - 20), (x - 9, y - 28), 2)
            pygame.draw.line(self.screen, col, (x, y - 20), (x + 5, y - 29), 2)
        elif node.level_req == 2:
            pts = [(x-25, y-22), (x+25, y-22), (x+12, y+5), (x+6, y+12), (x+6, y+23), (x-6, y+23), (x-6, y+12), (x-12, y+5)]
            pygame.draw.lines(self.screen, col, True, pts, 3)
            pygame.draw.line(self.screen, col, (x - 20, y + 29), (x + 20, y + 29), 3)
            pygame.draw.line(self.screen, col, (x, y + 12), (x, y + 25), 3)
            pygame.draw.circle(self.screen, col, (x + 14, y - 27), 3)
        else:
            bldg = [(x-22, y+27), (x-22, y-15), (x-9, y-15), (x-9, y-32), (x+9, y-32), (x+9, y-15), (x+22, y-15), (x+22, y+27)]
            pygame.draw.lines(self.screen, col, True, bldg, 3)
            for ox in (-15, 0, 15):
                pygame.draw.line(self.screen, col, (x + ox, y - 5), (x + ox, y + 5), 2)
            pygame.draw.line(self.screen, col, (x - 30, y + 28), (x + 30, y + 28), 3)
            pygame.draw.circle(self.screen, col, (x, y - 43), 3)

        # Lock badge
        if not unlocked:
            pygame.draw.circle(self.screen, (10, 12, 28), (x + 39, y + 39), 15)
            pygame.draw.circle(self.screen, self.MUTED, (x + 39, y + 39), 15, 2)
            pygame.draw.rect(self.screen, self.MUTED, (x + 32, y + 38, 14, 11), 2, border_radius=2)
            pygame.draw.arc(self.screen, self.MUTED, (x + 34, y + 30, 10, 12), math.pi, 2 * math.pi, 2)

    # LOCATION LABELS & ROUTE

    def draw_label(self, node):
        x, y = node.pos
        col = self.color(node)
        if not node.is_unlocked:
            col = tuple(max(40, int(c * 0.5)) for c in col)

        self.panel(pygame.Rect(x - 125, y + 72, 250, 58), col, 220)
        self.text(node.name, self.name, self.WHITE, (x, y + 91))

        if node.is_unlocked:
            active = self.economy.level == node.level_req
            status, status_col = ("ACTIVE", self.GREEN) if active else ("UNLOCKED", self.CYAN)
        else:
            status, status_col = f"LOCKED  •  ${node.cost}", self.MUTED

        self.text(status, self.small, status_col, (x, y + 114))

    def draw_route(self):
        nodes = list(self.map_manager.nodes.values())
        for a, b in zip(nodes, nodes[1:]):
            pygame.draw.line(self.screen, (30, 28, 60), a.pos, b.pos, 5)
            if a.is_unlocked and b.is_unlocked:
                pygame.draw.line(self.screen, (55, 120, 155), a.pos, b.pos, 2)

    # CURRENT LOCATION & DISTRICT STATUS

    def draw_current(self):
        node = next((n for n in self.map_manager.nodes.values() if n.level_req == self.economy.level), None)
        if not node: return

        self.panel(pygame.Rect(28, 575, 350, 105), self.color(node))
        self.text("CURRENT LOCATION", self.small, self.WHITE, (110, 592))
        self.text(node.name, self.name, self.color(node), (190, 620))
        desc = node.description if len(node.description) <= 43 else node.description[:40] + "..."
        self.text(desc, self.small, self.MUTED, (203, 651))

    def draw_status(self):
        rect = pygame.Rect(1010, 568, 245, 118)
        self.panel(rect, self.CYAN, alpha=220)
        self.text("DISTRICT STATUS", self.small, self.WHITE, (1132, 585))
        pygame.draw.line(self.screen, self.CYAN, (1020, 595), (1245, 595), 1)

        self.map_manager.check_unlocks()
        for i, node in enumerate(self.map_manager.nodes.values()):
            y = 614 + i * 22
            active = self.economy.level == node.level_req
            if active:
                status_text, col = f"LV.{node.level_req}  ACTIVE", self.GREEN
                pygame.draw.circle(self.screen, col, (1030, y), 6)
            elif node.is_unlocked:
                status_text, col = f"LV.{node.level_req}  UNLOCKED", self.CYAN
                pygame.draw.circle(self.screen, col, (1030, y), 6, 2)
            else:
                status_text, col = f"LV.{node.level_req}  LOCKED", self.MUTED
                pygame.draw.line(self.screen, col, (1024, y - 4), (1036, y + 4), 2)
                pygame.draw.line(self.screen, col, (1036, y - 4), (1024, y + 4), 2)
            self.text(status_text, self.small, col, (1148, y))

    # INPUT & MAIN LOOP
    
    def update_hover(self):
        m = pygame.mouse.get_pos()
        self.hover = next((n for n in self.map_manager.nodes.values() if self.node_hitbox(n).collidepoint(m)), None)

    def run(self):
        while True:
            self.t += self.clock.tick(self.FPS) / 1000
            self.map_manager.check_unlocks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_m):
                    return True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back.collidepoint(event.pos):
                        return True
                    for node_id, node in self.map_manager.nodes.items():
                        if self.node_hitbox(node).collidepoint(event.pos):
                            if self.map_manager.select_node(node_id):
                                self.economy.level = node.level_req
                                self.economy.location = self.economy.LOCATIONS.get(node.level_req, node.name)
                                self.economy.save_economy_data()
                                print(f"[MAP] Selected: {node.name}")
                                return True

            self.update_hover()
            self.draw_background()
            self.draw_route()
            self.draw_header()
            self.draw_title()

            for node in self.map_manager.nodes.values():
                self.draw_icon(node)
                self.draw_label(node)

            self.draw_current()
            self.draw_status()

            footer = self.small.render("CLICK A LOCATION TO TRAVEL OR UNLOCK  •  [M] / [ESC] RETURN", True, self.MUTED)
            self.screen.blit(footer, footer.get_rect(center=(640, 703)))
            pygame.display.flip()
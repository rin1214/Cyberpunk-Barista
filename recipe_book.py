import os
import math
import pygame
from drink import DRINK_MENU, get_recipe, is_drink_unlocked

def _load_font(filename: str, size: int, bold: bool = True) -> pygame.font.Font:
    """Load an Orbitron TTF font from assets/fonts with graceful system font fallback."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "assets", "fonts", filename)
    if os.path.exists(path):
        try:
            return pygame.font.Font(path, size)
        except Exception:
            pass
    return pygame.font.SysFont("arial", size, bold=bold)



RECIPE_PROFILES = {
    "Neon Latte": {
        "profile": "coffee • creamy • smooth",
        "topping": "Whipped Cream",
        "level": 1,
        "price": 12,
        "badge_type": "crystal",
        "badge_color": (195, 120, 255),
    },
    "Milkyway": {
        "profile": "creamy • chocolate • comforting",
        "topping": "Whipped Cream • Chocolate Bits",
        "level": 1,
        "price": 12,
        "badge_type": "bean",
        "badge_color": (175, 110, 70),
    },
    "Void Chai": {
        "profile": "spiced • warm • rich",
        "topping": "Whipped Cream",
        "level": 1,
        "price": 12,
        "badge_type": "crystal",
        "badge_color": (190, 120, 255),
    },
    "Cyber Fuel": {
        "profile": "energy • powerful • futuristic",
        "topping": "No topping",
        "level": 2,
        "price": 18,
        "badge_type": "bolt",
        "badge_color": (75, 235, 255),
    },
    "Hologram Frappe": {
        "profile": "cold • colourful • playful",
        "topping": "Whipped Cream",
        "level": 2,
        "price": 18,
        "badge_type": "star",
        "badge_color": (255, 135, 225),
    },
    "Pixel Lemint": {
        "profile": "minty • refreshing • cool",
        "topping": "Mint Leaves",
        "level": 2,
        "price": 18,
        "badge_type": "leaf",
        "badge_color": (110, 255, 130),
    },
    "Caramel Byte": {
        "profile": "caramel • rich • sweet",
        "topping": "Whipped Cream • Caramel Crunch",
        "level": 3,
        "price": 22,
        "badge_type": "cube",
        "badge_color": (255, 175, 55),
    },
    "Stardust Matcha": {
        "profile": "earthy • smooth • calming",
        "topping": "Yellow Stardust",
        "level": 3,
        "price": 22,
        "badge_type": "sparkle",
        "badge_color": (255, 235, 105),
    },
    "Meteorite": {
        "profile": "cold • intense • futuristic",
        "topping": "Meteorite Crumbs",
        "level": 3,
        "price": 22,
        "badge_type": "shard",
        "badge_color": (135, 220, 255),
    },
}

# The exact 3x3 layout ordered by level
RECIPE_GRID_ORDER = [
    # Row 0: Level 1
    "Neon Latte", "Milkyway", "Void Chai",
    # Row 1: Level 2
    "Cyber Fuel", "Hologram Frappe", "Pixel Lemint",
    # Row 2: Level 3
    "Caramel Byte", "Stardust Matcha", "Meteorite",
]


class RecipeBook:
    """Cyberpunk Cafe Recipe Book Overlay: Clean, authentic cyberpunk recipe handbook."""

    WIDTH, HEIGHT = 1280, 720

    # Color Palette
    CYAN = (0, 240, 255)
    CYAN_LIGHT = (95, 245, 255)
    CYAN_DIM = (0, 180, 210)
    PINK = (255, 42, 133)
    PINK_LIGHT = (255, 140, 205)
    WHITE = (245, 248, 255)
    SOFT_WHITE = (210, 220, 242)
    MUTED_TEXT = (145, 168, 205)
    LOCKED_TITLE = (125, 160, 210)
    LOCKED_SUB = (75, 100, 140)

    def __init__(self):
        pygame.font.init()
        self.is_open = False

        # Panel coordinates
        self.panel = pygame.Rect(55, 50, 1170, 630)
        self.close_button = pygame.Rect(1095, 72, 105, 34)
        self.level_badge = pygame.Rect(935, 75, 145, 28)

        # Typography
        self.font_title = _load_font("Orbitron-Bold.ttf", 23, bold=True)
        self.font_sub = _load_font("Orbitron-Medium.ttf", 12, bold=False)
        self.font_card_title = _load_font("Orbitron-Bold.ttf", 15, bold=True)
        self.font_label = _load_font("Orbitron-Bold.ttf", 11, bold=True)
        self.font_val = _load_font("Orbitron-Medium.ttf", 10, bold=False)
        self.font_locked_title = _load_font("Orbitron-Bold.ttf", 13, bold=True)
        self.font_locked_sub = _load_font("Orbitron-Medium.ttf", 11, bold=False)
        self.font_badge = _load_font("Orbitron-Bold.ttf", 11, bold=True)
        self.font_close = _load_font("Orbitron-Bold.ttf", 12, bold=True)

        # Drink Sprites (74x111 cached)
        self.drink_sprites = {}
        self._load_drink_sprites()

    def _load_drink_sprites(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        drinks_dir = os.path.join(base_dir, "assets", "drinks")
        sprite_size = (74, 111)

        for drink_name in RECIPE_GRID_ORDER:
            fname = drink_name.lower().replace(" ", "_") + ".png"
            path = os.path.join(drinks_dir, fname)
            if os.path.exists(path):
                try:
                    raw = pygame.image.load(path)
                    scaled = pygame.transform.smoothscale(raw, sprite_size).convert_alpha()
                    # Clean solid black backgrounds (such as in milkyway and void_chai)
                    corner = scaled.get_at((0, 0))
                    if corner.a > 100 and max(corner.r, corner.g, corner.b) <= 22:
                        px = pygame.PixelArray(scaled)
                        w, h = scaled.get_size()
                        for x in range(w):
                            for y in range(h):
                                col = scaled.unmap_rgb(px[x, y])
                                max_c = max(col.r, col.g, col.b)
                                if max_c <= 14:
                                    px[x, y] = (0, 0, 0, 0)
                                elif max_c <= 32:
                                    alpha = int((max_c - 14) / 18.0 * 255)
                                    px[x, y] = (col.r, col.g, col.b, alpha)
                        del px

                    self.drink_sprites[drink_name] = scaled
                except Exception as e:
                    print(f"[RECIPE_BOOK] Error loading {path}: {e}")
                    self.drink_sprites[drink_name] = None
            else:
                self.drink_sprites[drink_name] = None

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def toggle(self):
        self.is_open = not self.is_open

    def handle_event(self, event, current_level: int = 1) -> bool:
        """Handle keyboard & mouse interaction. Returns True if event consumed."""
        if not self.is_open:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_r):
                self.close()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button.collidepoint(event.pos):
                self.close()
                return True
            # Clicking outside modal closes it
            if not self.panel.collidepoint(event.pos):
                self.close()
                return True
            return True

        return False

    def draw(self, screen: pygame.Surface, current_level: int = 1):
        """Render the complete 3-tier Recipe Book UI overlay."""
        if not self.is_open:
            return

        # 1. Dark semi-transparent dim backdrop
        dim = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        dim.fill((3, 6, 16, 225))
        screen.blit(dim, (0, 0))

        # 2. Main Cyberpunk Panel Container
        panel_surf = pygame.Surface(self.panel.size, pygame.SRCALPHA)
        panel_surf.fill((7, 12, 28, 246))
        screen.blit(panel_surf, self.panel.topleft)

        # Panel Border (Vibrant Magenta Glow)
        pygame.draw.rect(screen, (255, 42, 133, 70), self.panel.inflate(4, 4), 1, border_radius=22)
        pygame.draw.rect(screen, self.PINK, self.panel, 2, border_radius=20)

        # 3. Cybernetic Circuit Traces on left and right borders
        self._draw_circuit_accents(screen)

        # 4. Header Bar
        self._draw_header(screen, current_level)

        # 5. Grid of 9 Recipe Cards
        self._draw_grid(screen, current_level)

    def _draw_circuit_accents(self, screen: pygame.Surface):
        """Draw tech circuit lines with 45-degree angle branches along modal borders."""
        cyan = self.CYAN
        p = self.panel

        # Left edge circuit trace
        lx = p.left + 1
        pygame.draw.line(screen, cyan, (lx, p.top + 70), (lx, p.bottom - 70), 1)
        # Branches
        pygame.draw.lines(screen, cyan, False, [(lx, p.top + 160), (lx + 8, p.top + 160), (lx + 14, p.top + 166)], 1)
        pygame.draw.circle(screen, cyan, (lx + 16, p.top + 168), 2)
        pygame.draw.lines(screen, cyan, False, [(lx, p.bottom - 160), (lx + 8, p.bottom - 160), (lx + 14, p.bottom - 166)], 1)
        pygame.draw.circle(screen, cyan, (lx + 16, p.bottom - 168), 2)

        # Right edge circuit trace
        rx = p.right - 2
        pygame.draw.line(screen, cyan, (rx, p.top + 70), (rx, p.bottom - 70), 1)
        # Branches
        pygame.draw.lines(screen, cyan, False, [(rx, p.top + 160), (rx - 8, p.top + 160), (rx - 14, p.top + 166)], 1)
        pygame.draw.circle(screen, cyan, (rx - 16, p.top + 168), 2)
        pygame.draw.lines(screen, cyan, False, [(rx, p.bottom - 160), (rx - 8, p.bottom - 160), (rx - 14, p.bottom - 166)], 1)
        pygame.draw.circle(screen, cyan, (rx - 16, p.bottom - 168), 2)

    def _draw_header(self, screen: pygame.Surface, current_level: int):
        """Draw header icon, title, subtitle, level pill, and close button."""
        # Neon coffee icon above title
        self._draw_neon_coffee_icon(screen, (640, 68))

        # Title: CYBERPUNK CAFE (Cyan) + RECIPE BOOK (Pink)
        t_cyber = self.font_title.render("CYBERPUNK CAFE", True, self.CYAN)
        t_rec = self.font_title.render(" RECIPE BOOK", True, self.PINK)
        total_w = t_cyber.get_width() + t_rec.get_width()
        start_x = 640 - (total_w // 2)
        y_title = 84
        screen.blit(t_cyber, (start_x, y_title))
        screen.blit(t_rec, (start_x + t_cyber.get_width(), y_title))

        # Subtitle
        sub = self.font_sub.render("Study the profiles before choosing a drink from the menu.", True, self.SOFT_WHITE)
        screen.blit(sub, sub.get_rect(center=(640, 114)))

        # Level Pill Badge: [ RECIPES • LEVEL X ]
        pygame.draw.rect(screen, (10, 20, 42), self.level_badge, border_radius=14)
        pygame.draw.rect(screen, self.CYAN, self.level_badge, 1, border_radius=14)
        badge_txt = self.font_badge.render(f"RECIPES • LEVEL {current_level}", True, self.CYAN)
        screen.blit(badge_txt, badge_txt.get_rect(center=self.level_badge.center))

        # Close Button: [ CLOSE  X ]
        mouse = pygame.mouse.get_pos()
        hover = self.close_button.collidepoint(mouse)
        close_fill = (45, 14, 34) if hover else (18, 8, 22)
        close_border = self.PINK_LIGHT if hover else self.PINK
        pygame.draw.rect(screen, close_fill, self.close_button, border_radius=8)
        pygame.draw.rect(screen, close_border, self.close_button, 2, border_radius=8)
        close_txt = self.font_close.render("CLOSE   X", True, close_border)
        screen.blit(close_txt, close_txt.get_rect(center=self.close_button.center))

    def _draw_neon_coffee_icon(self, screen: pygame.Surface, center: tuple[int, int]):
        """Render a small glowing pink coffee cup icon with steam."""
        cx, cy = center
        pink = self.PINK

        # Cup body
        cup_rect = pygame.Rect(cx - 8, cy - 3, 16, 12)
        pygame.draw.rect(screen, pink, cup_rect, border_radius=3)
        # Cup rim
        pygame.draw.line(screen, pink, (cx - 10, cy - 4), (cx + 10, cy - 4), 2)
        # Cup handle
        pygame.draw.arc(screen, pink, pygame.Rect(cx + 6, cy - 2, 7, 8), -1.5, 1.5, 2)
        # Steam trails
        pygame.draw.lines(screen, (255, 140, 205), False, [(cx - 4, cy - 6), (cx - 6, cy - 9), (cx - 4, cy - 12)], 1)
        pygame.draw.lines(screen, (255, 140, 205), False, [(cx + 2, cy - 6), (cx + 4, cy - 9), (cx + 2, cy - 12)], 1)

    def _draw_grid(self, screen: pygame.Surface, current_level: int):
        """Render the 3x3 cards grid with correct locked/unlocked states."""
        mouse = pygame.mouse.get_pos()

        # Grid Geometry
        card_w, card_h = 366, 162
        gap_x, gap_y = 15, 12
        grid_start_x = 76
        grid_start_y = 138

        for i, drink_name in enumerate(RECIPE_GRID_ORDER):
            col = i % 3
            row = i // 3
            card_rect = pygame.Rect(
                grid_start_x + col * (card_w + gap_x),
                grid_start_y + row * (card_h + gap_y),
                card_w, card_h
            )

            info = RECIPE_PROFILES.get(drink_name, {})
            unlock_level = info.get("level", 1)
            is_unlocked = current_level >= unlock_level

            if is_unlocked:
                self._draw_unlocked_card(screen, card_rect, drink_name, info, card_rect.collidepoint(mouse))
            else:
                self._draw_locked_card(screen, card_rect)

    def _draw_unlocked_card(self, screen: pygame.Surface, rect: pygame.Rect, drink_name: str, info: dict, hovered: bool):
        """Draw an active, glowing drink card with illustration and profile."""
        # Background
        bg_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        bg_surf.fill((9, 18, 42, 235))
        screen.blit(bg_surf, rect.topleft)

        # Border
        border_col = self.CYAN_LIGHT if hovered else self.CYAN
        border_w = 2 if hovered else 1
        pygame.draw.rect(screen, border_col, rect, border_w, border_radius=12)

        # 1. Drink Illustration (Left side)
        img = self.drink_sprites.get(drink_name)
        if img:
            screen.blit(img, (rect.x + 10, rect.y + 24))
        else:
            self._draw_fallback_cup(screen, rect.x + 48, rect.y + 80)

        # 2. Topping / Special Badge Icon (beside drink cup)
        self._draw_topping_badge(screen, rect.x + 80, rect.y + 128, info.get("badge_type"), info.get("badge_color"))

        # 3. Text Column (Right side)
        tx = rect.x + 96

        # Title
        title_surf = self.font_card_title.render(drink_name.upper(), True, self.CYAN)
        screen.blit(title_surf, (tx, rect.y + 14))

        # Data Lines
        recipe = get_recipe(drink_name)
        price = recipe.price if recipe else info.get("price", 12)
        unlock_lvl = recipe.unlock_level if recipe else info.get("level", 1)

        self._draw_card_line(screen, "PROFILE:", info.get("profile", ""), tx, rect.y + 42)
        self._draw_card_line(screen, "TOPPING:", info.get("topping", "None"), tx, rect.y + 70)
        self._draw_card_line(screen, "LEVEL:", str(unlock_lvl), tx, rect.y + 98)
        self._draw_card_line(screen, "PRICE:", f"${price}", tx, rect.y + 126)

    def _draw_card_line(self, screen: pygame.Surface, label: str, val: str, x: int, y: int):
        """Draw a single key-value row with cyan label and soft white value."""
        lbl_surf = self.font_label.render(label, True, self.CYAN)
        screen.blit(lbl_surf, (x, y))
        val_x = x + lbl_surf.get_width() + 6
        val_surf = self.font_val.render(val, True, self.WHITE)
        screen.blit(val_surf, (val_x, y))

    def _draw_locked_card(self, screen: pygame.Surface, rect: pygame.Rect):
        """Draw a locked card with cup silhouette, lock icon, and unlock info."""
        # Background
        bg_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        bg_surf.fill((6, 10, 22, 225))
        screen.blit(bg_surf, rect.topleft)

        # Subtle dark border
        pygame.draw.rect(screen, (24, 40, 68), rect, 1, border_radius=12)

        # Left: Faint Cup Silhouette
        self._draw_cup_silhouette(screen, rect.x + 48, rect.y + 80)

        # Right / Center: Padlock Icon and text
        center_x = rect.x + 225

        # Padlock
        lock_y = rect.y + 54
        # Shackle
        pygame.draw.arc(screen, (90, 125, 175), pygame.Rect(center_x - 9, lock_y - 15, 18, 16), 0, 3.14159, 2)
        # Lock body
        pygame.draw.rect(screen, (55, 80, 115), pygame.Rect(center_x - 12, lock_y - 4, 24, 18), border_radius=4)
        pygame.draw.rect(screen, (80, 115, 160), pygame.Rect(center_x - 12, lock_y - 4, 24, 18), 1, border_radius=4)
        # Keyhole
        pygame.draw.circle(screen, (20, 32, 50), (center_x, lock_y + 3), 2)
        pygame.draw.line(screen, (20, 32, 50), (center_x, lock_y + 3), (center_x, lock_y + 8), 1)

        # LOCKED text
        locked_txt = self.font_locked_title.render("LOCKED", True, self.LOCKED_TITLE)
        screen.blit(locked_txt, locked_txt.get_rect(center=(center_x, rect.y + 90)))

        # Subtitle
        sub_txt = self.font_locked_sub.render("Unlock at higher level", True, self.LOCKED_SUB)
        screen.blit(sub_txt, sub_txt.get_rect(center=(center_x, rect.y + 114)))

    def _draw_cup_silhouette(self, screen: pygame.Surface, cx: int, cy: int):
        """Draw a faint cup silhouette on the left side of locked cards."""
        color = (18, 28, 48)
        rim_color = (32, 50, 80)

        # Cup body trapezoid
        pts = [
            (cx - 20, cy - 32),
            (cx + 20, cy - 32),
            (cx + 15, cy + 38),
            (cx - 15, cy + 38),
        ]
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, rim_color, pts, 1)

        # Cup lid
        pygame.draw.ellipse(screen, rim_color, pygame.Rect(cx - 22, cy - 38, 44, 12), 1)

        # Straw
        pygame.draw.line(screen, rim_color, (cx + 4, cy - 36), (cx + 12, cy - 50), 2)

    def _draw_fallback_cup(self, screen: pygame.Surface, cx: int, cy: int):
        """Fallback cup vector if drink PNG fails to load."""
        pts = [(cx - 22, cy - 34), (cx + 22, cy - 34), (cx + 16, cy + 40), (cx - 16, cy + 40)]
        pygame.draw.polygon(screen, (25, 45, 80), pts)
        pygame.draw.polygon(screen, self.CYAN, pts, 2)
        pygame.draw.ellipse(screen, self.PINK, pygame.Rect(cx - 23, cy - 42, 46, 14), 2)

    def _draw_topping_badge(self, screen: pygame.Surface, x: int, y: int, badge_type: str, color: tuple):
        """Draw a tiny illustrated vector badge representing the topping / element."""
        if not color:
            color = (200, 200, 255)

        if badge_type == "crystal":
            pts = [(x, y - 8), (x + 6, y), (x, y + 8), (x - 6, y)]
            pygame.draw.polygon(screen, color, pts)
            pygame.draw.polygon(screen, (255, 255, 255), [(x, y - 8), (x + 3, y), (x, y + 3), (x - 3, y)])

        elif badge_type == "bean":
            pygame.draw.ellipse(screen, color, pygame.Rect(x - 6, y - 5, 12, 10))
            pygame.draw.arc(screen, (255, 200, 160), pygame.Rect(x - 5, y - 4, 10, 8), 0.5, 2.5, 1)

        elif badge_type == "bolt":
            pts = [(x + 2, y - 8), (x - 4, y - 1), (x, y - 1), (x - 2, y + 8), (x + 4, y + 1), (x, y + 1)]
            pygame.draw.polygon(screen, color, pts)

        elif badge_type == "star":
            pts = []
            for i in range(10):
                r = 8 if i % 2 == 0 else 4
                ang = -math.pi / 2 + i * math.pi / 5
                pts.append((x + math.cos(ang) * r, y + math.sin(ang) * r))
            pygame.draw.polygon(screen, color, pts)

        elif badge_type == "leaf":
            pygame.draw.ellipse(screen, color, pygame.Rect(x - 7, y - 5, 14, 10))
            pygame.draw.line(screen, (200, 255, 220), (x - 6, y), (x + 6, y), 1)

        elif badge_type == "cube":
            pts_top = [(x, y - 6), (x + 6, y - 3), (x, y), (x - 6, y - 3)]
            pts_l = [(x - 6, y - 3), (x, y), (x, y + 6), (x - 6, y + 3)]
            pts_r = [(x, y), (x + 6, y - 3), (x + 6, y + 3), (x, y + 6)]
            pygame.draw.polygon(screen, (255, 215, 110), pts_top)
            pygame.draw.polygon(screen, color, pts_l)
            pygame.draw.polygon(screen, (210, 135, 30), pts_r)

        elif badge_type == "sparkle":
            pts = [(x, y - 8), (x + 2, y - 2), (x + 8, y), (x + 2, y + 2), (x, y + 8), (x - 2, y + 2), (x - 8, y), (x - 2, y - 2)]
            pygame.draw.polygon(screen, color, pts)

        elif badge_type == "shard":
            pts = [(x - 5, y - 6), (x + 6, y - 4), (x + 4, y + 7), (x - 6, y + 4)]
            pygame.draw.polygon(screen, color, pts)
            pygame.draw.polygon(screen, (255, 255, 255), pts, 1)

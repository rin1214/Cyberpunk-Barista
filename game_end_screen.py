import os
import pygame


WIDTH, HEIGHT, FPS = 1280, 720, 60
ROOT = os.path.dirname(os.path.abspath(__file__))
END_DIR = os.path.join(ROOT, "assets", "end_game")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
BG_FILE = os.path.join(END_DIR, "end_game_background.png")

CYAN = (104, 235, 255)
PINK = (255, 121, 218)
PURPLE = (177, 126, 255)
GOLD = (255, 218, 120)
WHITE = (245, 248, 255)
SOFT = (190, 202, 225)
MUTED = (125, 141, 171)
PANEL = (17, 21, 38)


class GameEndScreen:
    def __init__(self, screen):
        self.screen, self.clock = screen, pygame.time.Clock()
        self.bg, self.cats, self.font = self._image(BG_FILE, (WIDTH, HEIGHT), False), self._cats(), self._fonts()
        self.buttons = {}
        self.phase = 0
        self.phase_start = pygame.time.get_ticks()
        self.running, self.result = True, None
        self.player_name, self.level = "BARISTA", 3
        self.successful_drinks = self.xp = self.credits = 0

    def _image(self, path, size, alpha=True):
        try:
            image = pygame.image.load(path)
            image = image.convert_alpha() if alpha else image.convert()
            return pygame.transform.smoothscale(image, size)
        except (pygame.error, FileNotFoundError):
            fallback = pygame.Surface(size, pygame.SRCALPHA)
            fallback.fill((10, 12, 24, 255))
            return fallback

    def _cats(self):
        return [
            self._image(os.path.join(END_DIR, "cat_wave", f"{i:02d}.png"), (330, 330))
            for i in range(1, 9)
            if os.path.exists(os.path.join(END_DIR, "cat_wave", f"{i:02d}.png"))
        ]

    def _font_file(self, words):
        if not os.path.isdir(FONT_DIR):
            return None
        return next((
            os.path.join(FONT_DIR, name) for name in os.listdir(FONT_DIR)
            if name.lower().endswith((".ttf", ".otf"))
            and any(word in name.lower() for word in words)
        ), None)

    def _fonts(self):
        def make(words, size, bold=False):
            try:
                path = self._font_file(words)
                return pygame.font.Font(path, size) if path else pygame.font.SysFont("arial", size, bold=bold)
            except pygame.error:
                return pygame.font.SysFont("arial", size, bold=bold)

        return {
            "hero": make(["orbitron-bold", "orbitron black", "orbitron"], 54, True),
            "title": make(["orbitron-bold", "orbitron"], 38, True),
            "head": make(["orbitron-bold", "orbitron"], 30, True),
            "medium": make(["orbitron-medium", "orbitron"], 21, True),
            "body": make(["orbitron-light", "orbitron"], 18),
            "button": make(["orbitron-medium", "orbitron"], 19, True),
        }

    def text(self, value, font, center, color=WHITE):
        image = self.font[font].render(str(value), True, color)
        self.screen.blit(image, image.get_rect(center=center))

    def panel(self, rect, accent=CYAN, alpha=235):
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (*PANEL, alpha), surface.get_rect(), border_radius=20)
        pygame.draw.rect(surface, (*accent, 180), surface.get_rect(), 2, border_radius=20)
        self.screen.blit(surface, rect.topleft)
        pygame.draw.line(self.screen, accent, (rect.x + 18, rect.y), (rect.x + 75, rect.y), 2)

    def button(self, key, rect, label, accent):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (38, 46, 76, 250) if hover else (28, 34, 58, 245), surface.get_rect(), border_radius=12)
        pygame.draw.rect(surface, (*accent, 240), surface.get_rect(), 2, border_radius=12)
        self.screen.blit(surface, rect.topleft)
        self.text(label, "button", rect.center)
        self.buttons[key] = rect

    def header(self):
        self.text("CYBERPUNK CAFÉ", "title", (640, 42), CYAN)
        pygame.draw.line(self.screen, (*CYAN, 120), (370, 70), (910, 70), 1)

    def background(self):
        self.screen.blit(self.bg, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 7, 18, 125))
        self.screen.blit(overlay, (0, 0))

    def elapsed(self):
        return (pygame.time.get_ticks() - self.phase_start) / 1000

    def cat(self, center=(365, 340)):
        if self.cats:
            index = int(self.elapsed() / 0.10) % len(self.cats)
            bob = int(4 * ((index % 4) - 1.5))
            image = self.cats[index]
            self.screen.blit(image, image.get_rect(center=(center[0], center[1] + bob)))

    def bubble(self):
        rect = pygame.Rect(300, 125, 300, 88)
        self.panel(rect, PINK)
        self.text("BYEEEE!!", "head", rect.center, PINK)
        pygame.draw.polygon(self.screen, PANEL, [(335, rect.bottom), (315, rect.bottom + 28), (375, rect.bottom)])

    def phase_update(self):
        limits = (2.5, 3.5, 2.0)
        if self.phase < 3 and self.elapsed() >= limits[self.phase]:
            self.phase += 1
            self.phase_start = pygame.time.get_ticks()

    def closing(self):
        self.header()
        rect = pygame.Rect(235, 190, 810, 245)
        self.panel(rect, CYAN)
        self.text("THE LAST ORDER", "hero", (640, 270))
        self.text("HAS BEEN SERVED", "hero", (640, 335), CYAN)
        self.text("The café is closing for the night...", "body", (640, 397), SOFT)

    def waving(self):
        self.header()
        left = pygame.Rect(100, 115, 520, 450)
        self.panel(left, PINK)
        self.cat((360, 330))
        self.bubble()
        self.text("SEE YOU NEXT SHIFT", "medium", (360, 515), SOFT)
        right = pygame.Rect(670, 185, 510, 310)
        self.panel(right, CYAN)
        for value, font, center, color in (
            ("SHIFT COMPLETE", "head", (925, 260), CYAN),
            ("You made it", "medium", (925, 325), WHITE),
            ("through the night.", "medium", (925, 360), WHITE),
            ("Thanks for serving", "body", (925, 420), SOFT),
            ("the Cyberpunk Café!", "body", (925, 450), SOFT),
        ):
            self.text(value, font, center, color)

    def thanks(self):
        self.header()
        rect = pygame.Rect(205, 180, 870, 300)
        self.panel(rect, PURPLE)
        self.text("THANK YOU", "hero", (640, 270))
        self.text("FOR PLAYING!", "hero", (640, 335), PURPLE)
        self.text(f"Great work, {self.player_name}!", "medium", (640, 405), SOFT)

    def stat(self, y, label, value, accent):
        self.text(label, "body", (850, y), SOFT)
        self.text(value, "medium", (1110, y), accent)
        pygame.draw.line(self.screen, (*MUTED, 70), (780, y + 23), (1160, y + 23), 1)

    def final(self):
        self.header()
        left = pygame.Rect(85, 120, 590, 485)
        self.panel(left, PINK)
        self.cat((380, 335))
        self.text("SHIFT COMPLETE", "head", (380, 505), PINK)
        self.text("BYEEEE!!", "medium", (380, 540))
        right = pygame.Rect(710, 120, 485, 400)
        self.panel(right, CYAN)
        self.text("FINAL STATS", "head", (952, 175), CYAN)
        pygame.draw.line(self.screen, (*CYAN, 120), (760, 205), (1145, 205), 1)
        for args in (
            (250, "SUCCESSFUL DRINKS", self.successful_drinks, PINK),
            (300, "FINAL LEVEL", self.level, PURPLE),
            (350, "TOTAL XP", self.xp, CYAN),
            (400, "CURRENT CREDITS", f"${self.credits}", GOLD),
        ):
            self.stat(*args)
        self.buttons.clear()
        self.button("exit", pygame.Rect(842, 555, 220, 58), "EXIT TO DESKTOP", PINK)

    def draw(self):
        self.background()
        (self.closing, self.waving, self.thanks, self.final)[min(self.phase, 3)]()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.result, self.running = "quit", False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.result, self.running = "exit_to_desktop", False
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN) and self.phase < 3:
                    self.phase += 1
                    self.phase_start = pygame.time.get_ticks()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.phase < 3:
                    self.phase += 1
                    self.phase_start = pygame.time.get_ticks()
                elif self.buttons.get("exit", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    self.result, self.running = "exit_to_desktop", False

    def run(self, player_name="BARISTA", level=3, successful_drinks=0, xp=0, credits=0):
        self.player_name = str(player_name).upper()
        self.level, self.successful_drinks = int(level), int(successful_drinks)
        self.xp, self.credits = int(xp), int(credits)
        self.phase, self.phase_start = 0, pygame.time.get_ticks()
        self.running, self.result = True, None
        while self.running:
            self.events()
            self.phase_update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        return self.result
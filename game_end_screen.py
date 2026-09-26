import os
import pygame

WIDTH, HEIGHT = 1280, 720
FPS = 60

ROOT = os.path.dirname(os.path.abspath(__file__))
END_DIR = os.path.join(ROOT, "assets", "mahirah", "end_game")
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
        self.bg = self._image(BG_FILE, (WIDTH, HEIGHT), False)
        self.cats = self._cats()
        self.font = self._fonts()
        self.buttons = {}
        self.phase = 0
        self.phase_start = pygame.time.get_ticks()
        self.running = True
        self.result = None
        self.player_name = "BARISTA"
        self.level = 3
        self.successful_drinks = 0
        self.xp = 0
        self.credits = 0

    def _image(self, path, size, alpha=True):
        try:
            img = pygame.image.load(path)
            img = img.convert_alpha() if alpha else img.convert()
            return pygame.transform.smoothscale(img, size)
        except (pygame.error, FileNotFoundError):
            s = pygame.Surface(size, pygame.SRCALPHA)
            s.fill((10, 12, 24, 255))
            return s

    def _cats(self):
        return [
            self._image(
                os.path.join(END_DIR, "cat_wave", f"{i:02d}.png"),
                (330, 330)
            )
            for i in range(1, 9)
            if os.path.exists(os.path.join(END_DIR, "cat_wave", f"{i:02d}.png"))
        ]

    def _font_file(self, words):
        if not os.path.isdir(FONT_DIR):
            return None
        for name in os.listdir(FONT_DIR):
            low = name.lower()
            if low.endswith((".ttf", ".otf")) and any(w in low for w in words):
                return os.path.join(FONT_DIR, name)
        return None

    def _fonts(self):
        def make(words, size, bold=False):
            try:
                path = self._font_file(words)
                return pygame.font.Font(path, size) if path else pygame.font.SysFont(
                    "arial", size, bold=bold
                )
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
        img = self.font[font].render(str(value), True, color)
        self.screen.blit(img, img.get_rect(center=center))

    def panel(self, rect, accent=CYAN, alpha=235):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*PANEL, alpha), s.get_rect(), border_radius=20)
        pygame.draw.rect(
            s, (*accent, 180), s.get_rect(), 2, border_radius=20
        )
        self.screen.blit(s, rect.topleft)
        pygame.draw.line(
            self.screen, accent, (rect.x + 18, rect.y),
            (rect.x + 75, rect.y), 2
        )

    def button(self, key, rect, label, accent):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            s, (38, 46, 76, 250) if hover else (28, 34, 58, 245),
            s.get_rect(), border_radius=12
        )
        pygame.draw.rect(s, (*accent, 240), s.get_rect(), 2, border_radius=12)
        self.screen.blit(s, rect.topleft)
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

    def cat(self, center=(365, 340)):
        if not self.cats:
            return
        i = int(self.elapsed() / 0.10) % len(self.cats)
        bob = int(4 * ((i % 4) - 1.5))
        img = self.cats[i]
        self.screen.blit(img, img.get_rect(center=(center[0], center[1] + bob)))

    def bubble(self):
        r = pygame.Rect(300, 125, 300, 88)
        self.panel(r, PINK)
        self.text("BYEEEE!!", "head", r.center, PINK)
        pygame.draw.polygon(
            self.screen, PANEL,
            [(335, r.bottom), (315, r.bottom + 28), (375, r.bottom)]
        )

    def elapsed(self):
        return (pygame.time.get_ticks() - self.phase_start) / 1000

    def phase_update(self):
        t = self.elapsed()
        if self.phase == 0 and t >= 2.5:
            self.phase, self.phase_start = 1, pygame.time.get_ticks()
        elif self.phase == 1 and t >= 3.5:
            self.phase, self.phase_start = 2, pygame.time.get_ticks()
        elif self.phase == 2 and t >= 2.0:
            self.phase, self.phase_start = 3, pygame.time.get_ticks()

    def closing(self):
        self.header()
        r = pygame.Rect(235, 190, 810, 245)
        self.panel(r, CYAN)
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
        self.text("SHIFT COMPLETE", "head", (925, 260), CYAN)
        self.text("You made it", "medium", (925, 325))
        self.text("through the night.", "medium", (925, 360))
        self.text("Thanks for serving", "body", (925, 420), SOFT)
        self.text("the Cyberpunk Café!", "body", (925, 450), SOFT)

    def thanks(self):
        self.header()
        r = pygame.Rect(205, 180, 870, 300)
        self.panel(r, PURPLE)
        self.text("THANK YOU", "hero", (640, 270))
        self.text("FOR PLAYING!", "hero", (640, 335), PURPLE)
        self.text(
            f"Great work, {self.player_name}!",
            "medium", (640, 405), SOFT
        )

    def stat(self, y, label, value, accent):
        self.text(label, "body", (850, y), SOFT)
        self.text(value, "medium", (1110, y), accent)
        pygame.draw.line(
            self.screen, (*MUTED, 70), (780, y + 23), (1160, y + 23), 1
        )

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
        pygame.draw.line(
            self.screen, (*CYAN, 120), (760, 205), (1145, 205), 1
        )

        self.stat(250, "SUCCESSFUL DRINKS", self.successful_drinks, PINK)
        self.stat(300, "FINAL LEVEL", self.level, PURPLE)
        self.stat(350, "TOTAL XP", self.xp, CYAN)
        self.stat(400, "CREDITS EARNED", f"${self.credits}", GOLD)

        self.buttons.clear()
        self.button("play_again", pygame.Rect(735, 555, 205, 58), "PLAY AGAIN", CYAN)
        self.button("main_menu", pygame.Rect(955, 555, 205, 58), "MAIN MENU", PINK)

    def draw(self):
        self.background()
        if self.phase == 0:
            self.closing()
        elif self.phase == 1:
            self.waving()
        elif self.phase == 2:
            self.thanks()
        else:
            self.final()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.result, self.running = "quit", False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.result, self.running = "main_menu", False
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self.phase < 3:
                        self.phase += 1
                        self.phase_start = pygame.time.get_ticks()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.phase < 3:
                    self.phase += 1
                    self.phase_start = pygame.time.get_ticks()
                    continue

                if self.buttons.get("play_again", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    self.result, self.running = "play_again", False
                elif self.buttons.get("main_menu", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                    self.result, self.running = "main_menu", False

    def run(
        self,
        player_name="BARISTA",
        level=3,
        successful_drinks=0,
        xp=0,
        credits=0,
    ):
        self.player_name = str(player_name).upper()
        self.level = int(level)
        self.successful_drinks = int(successful_drinks)
        self.xp = int(xp)
        self.credits = int(credits)
        self.phase = 0
        self.phase_start = pygame.time.get_ticks()
        self.running, self.result = True, None

        while self.running:
            self.events()
            self.phase_update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        return self.result

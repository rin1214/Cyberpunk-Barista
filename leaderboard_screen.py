import os
import pygame


class LeaderboardScreen:
    W, H = 1280, 720
    FPS = 60

    PINK = (255, 70, 200)
    CYAN = (40, 225, 255)
    GOLD = (255, 195, 70)
    SILVER = (175, 220, 240)
    BRONZE = (255, 125, 145)
    WHITE = (235, 240, 255)
    MUTED = (145, 155, 180)
    DARK = (7, 9, 22)

    def __init__(self, screen, leaderboard_manager, economy, project_root=None):
        self.screen = screen
        self.lb = leaderboard_manager
        self.economy = economy
        self.clock = pygame.time.Clock()

        root = project_root or os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            root, "assets", "mahirah", "ui", "leaderboard_bg.png"
        )

        try:
            self.bg = pygame.image.load(path).convert()
        except (pygame.error, FileNotFoundError):
            self.bg = None

        self.title = pygame.font.SysFont("Consolas", 36, bold=True)
        self.sub = pygame.font.SysFont("Consolas", 15, bold=True)
        self.head = pygame.font.SysFont("Consolas", 13, bold=True)
        self.body = pygame.font.SysFont("Consolas", 16, bold=True)
        self.small = pygame.font.SysFont("Consolas", 11, bold=True)

        self.close = pygame.Rect(495, 648, 290, 48)

    def text(self, value, font, color, pos):
        s = font.render(str(value), True, color)
        self.screen.blit(s, s.get_rect(center=pos))

    def panel(self, rect, color, alpha=215):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        s.fill((*self.DARK, alpha))
        self.screen.blit(s, rect.topleft)
        pygame.draw.rect(self.screen, color, rect, 2, border_radius=10)

    def draw_background(self):
        w, h = self.screen.get_size()

        if self.bg:
            iw, ih = self.bg.get_size()
            scale = max(w / iw, h / ih)
            size = int(iw * scale), int(ih * scale)
            image = pygame.transform.smoothscale(self.bg, size)
            self.screen.blit(
                image,
                ((w - size[0]) // 2, (h - size[1]) // 2)
            )
        else:
            self.screen.fill(self.DARK)

        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((3, 5, 18, 115))
        self.screen.blit(shade, (0, 0))

    def draw_header(self):
        self.text("♛", self.title, self.PINK, (640, 48))
        self.text(
            "DISTRICT LEADERBOARD",
            self.title, self.CYAN, (640, 87)
        )
        self.text(
            "CYBERPUNK CAFÉ  //  TOP BARISTAS",
            self.sub, self.WHITE, (640, 120)
        )

        pygame.draw.line(
            self.screen, self.PINK, (455, 137), (610, 137), 2
        )
        pygame.draw.line(
            self.screen, self.CYAN, (670, 137), (825, 137), 2
        )

        credits = pygame.Rect(1040, 24, 205, 48)
        self.panel(credits, self.CYAN)
        self.text(
            f"CREDITS: ${self.economy.credits}",
            self.head, self.GOLD, credits.center
        )

    def draw_table(self, players):
        table = pygame.Rect(290, 155, 700, 465)
        self.panel(table, self.PINK, 225)

        cols = [
            ("RANK", 345),
            ("BARISTA", 485),
            ("LEVEL", 700),
            ("CREDITS", 815),
            ("XP", 925)
        ]

        for label, x in cols:
            self.text(label, self.head, self.MUTED, (x, 185))

        pygame.draw.line(
            self.screen, (70, 75, 110),
            (315, 207), (965, 207), 1
        )

        current = str(
            getattr(self.economy, "player_name", "")
        ).strip().lower()

        max_xp = max((p["xp"] for p in players), default=1)
        y = 220

        for i, p in enumerate(players[:8]):
            name = str(p["name"])
            xp = p["xp"]
            level = p["level"]
            credits = p["credits"]

            mine = name.strip().lower() == current

            accent = (
                self.GOLD if i == 0 else
                self.SILVER if i == 1 else
                self.BRONZE if i == 2 else
                self.CYAN if mine else
                (55, 70, 105)
            )

            row = pygame.Rect(310, y, 660, 40)

            if mine:
                self.panel(row, self.CYAN, 120)
            elif i < 3:
                self.panel(row, accent, 65)

            self.text(
                f"#{i + 1}", self.body,
                accent if i < 3 or mine else self.WHITE,
                (350, y + 20)
            )

            self.text(
                name.upper(), self.body,
                self.CYAN if mine else self.WHITE,
                (490, y + 20)
            )

            self.text(
                f"LV {level}", self.body,
                accent if i < 3 else self.WHITE,
                (700, y + 20)
            )

            self.text(
                f"${credits}", self.body,
                self.GOLD if i == 0 else self.WHITE,
                (815, y + 20)
            )

            # XP bar
            bx, by, bw, bh = 855, y + 13, 72, 12

            pygame.draw.rect(
                self.screen, (25, 30, 48),
                (bx, by, bw, bh), border_radius=4
            )

            fill = max(2, int(bw * xp / max_xp))

            pygame.draw.rect(
                self.screen, accent,
                (bx, by, fill, bh), border_radius=4
            )

            self.text(
                xp, self.small,
                accent if mine else self.MUTED,
                (950, y + 20)
            )

            if mine:
                self.text(
                    "YOU ♡", self.small,
                    self.CYAN, (930, y + 8)
                )

            y += 47

    def draw_footer(self):
        hover = self.close.collidepoint(pygame.mouse.get_pos())
        color = self.PINK if hover else self.CYAN

        self.panel(self.close, color)

        self.text(
            "‹  CLOSE [ L / ESC ]",
            self.body, color, self.close.center
        )

        self.text(
            "CYBERPUNK CAFÉ  //  BARISTA NETWORK",
            self.small, self.MUTED, (220, 695)
        )

        self.text(
            "PEOPLE  ✦  COFFEE  ✦  POSSIBILITIES",
            self.small, self.MUTED, (1060, 695)
        )

    def run(self):
        self.lb.update_current_player_score()

        while True:
            self.clock.tick(self.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_l):
                        return True

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.close.collidepoint(event.pos)
                ):
                    return True

            players = self.lb.get_ranked_players()

            self.draw_background()
            self.draw_header()
            self.draw_table(players)
            self.draw_footer()

            pygame.display.flip()
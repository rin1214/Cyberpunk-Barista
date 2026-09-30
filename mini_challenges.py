"""
mini_challenges.py
Cyberpunk Café - Mini Challenges
"""

import math
import random
import pygame

CHALLENGES = {
    "Neon Latte": {
        "title": "MILK MATCH",
        "ingredient": "MILK",
        "accent": (120, 235, 255),
        "tile_colors": [
            (245, 248, 255),
            (175, 225, 255),
            (210, 190, 255),
            (255, 220, 235),
            (150, 245, 220),
        ],
        "symbols": ["milk", "coffee", "syrup", "foam", "ice"],
    },
    "Milkyway": {
        "title": "STARDUST MATCH",
        "ingredient": "STARDUST",
        "accent": (205, 170, 255),
        "tile_colors": [
            (235, 220, 255),
            (175, 145, 255),
            (120, 210, 255),
            (255, 235, 150),
            (245, 175, 225),
        ],
        "symbols": ["milk", "chocolate", "star", "syrup", "ice"],
    },
    "Void Chai": {
        "title": "SPICE MATCH",
        "ingredient": "SPICE",
        "accent": (255, 175, 125),
        "tile_colors": [
            (255, 205, 150),
            (205, 155, 255),
            (255, 150, 185),
            (175, 235, 190),
            (245, 220, 150),
        ],
        "symbols": ["milk", "spice", "syrup", "star", "ice"],
    },
    "Cyber Fuel": {
        "title": "POWER MATCH",
        "ingredient": "POWER",
        "accent": (100, 190, 255),
        "tile_colors": [
            (115, 210, 255),
            (110, 140, 255),
            (185, 235, 255),
            (170, 255, 215),
            (245, 225, 100),
        ],
        "symbols": ["milk", "battery", "ice", "power", "star"],
    },
    "Hologram Frappe": {
        "title": "HOLO MATCH",
        "ingredient": "HOLO",
        "accent": (235, 160, 255),
        "tile_colors": [
            (255, 175, 230),
            (170, 225, 255),
            (190, 175, 255),
            (150, 255, 225),
            (255, 235, 150),
        ],
        "symbols": ["milk", "orb", "star", "ice", "syrup"],
    },
    "Pixel Lemint": {
        "title": "MINT MATCH",
        "ingredient": "MINT",
        "accent": (115, 245, 200),
        "tile_colors": [
            (120, 245, 205),
            (190, 255, 220),
            (120, 215, 255),
            (235, 225, 110),
            (190, 170, 255),
        ],
        "symbols": ["water", "mint", "ice", "star", "syrup"],
    },
    "Meteorite": {
        "title": "DEFLECTION FIELD",
        "ingredient": "METEORITE DUST",
        "accent": (255, 90, 120),
    },
    "Stardust Matcha": {
        "title": "OVERDRIVE LASER THREAD",
        "ingredient": "STARDUST MATCHA",
        "accent": (140, 255, 120),
    },
    "Caramel Byte": {
        "title": "CYBER WIRE SOLDER",
        "ingredient": "CARAMEL BYTE",
        "accent": (255, 180, 60),
    },
}


class MiniChallenge:
    N = 5
    TILE = 62
    GAP = 6
    TYPES = 5
    TARGET_STRIKES = 3

    def __init__(self):
        pygame.font.init()
        self.panel = pygame.Rect(280, 92, 720, 540)
        self.grid = pygame.Rect(473, 275, 334, 334)
        self.ft = pygame.font.SysFont("arial", 29, True)
        self.fb = pygame.font.SysFont("arial", 21, True)
        self.fs = pygame.font.SysFont("arial", 17, True)
        self.fi = pygame.font.SysFont("arial", 14, True)
        self.strike_title_font = pygame.font.SysFont("arial", 18, True)
        self.strike_big_font = pygame.font.SysFont("arial", 40, True)
        self.timer_ring_font = pygame.font.SysFont("arial", 16, True)

        self.active = False
        self.done = False
        self.drink = ""
        self.title = "INGREDIENT MATCH"
        self.ingredient = "INGREDIENT"
        self.accent = (120, 235, 255)
        self.colors = [
            (245, 248, 255),
            (175, 225, 255),
            (210, 190, 255),
            (255, 220, 235),
            (150, 245, 220),
        ]
        self.symbols = ["milk", "syrup", "coffee", "ice", "mint"]
        self.board = []
        self.selected = None
        self.strikes = 0
        self.time_left = 18.0
        self.message_timer = 0
        self.message = ""
        self.done_timer = 0
        self.pulse = 0

        # Level 3 Specific States
        self.level_mode = "MATCH3"
        self.center_pos = (640, 430)

        # Meteorite (360 Deflection Survival)
        self.shield_angle = 0
        self.debris_list = []
        self.spawn_timer = 0
        self.blocked_count = 0

        # Stardust Matcha (WASD/Arrow 10-Second Survival Runner)
        self.player_lane = 1
        self.barriers = []
        self.barrier_timer = 0
        self.key_cooldown = 0.0
        self.dodged_count = 0
        self.last_open_lane = -1

        # Caramel Byte (Cyber Wire Solder)
        self.solder_path = []
        self.glitch_tiles = set()
        self.is_soldering = False

    def start_challenge(self, drink_name):
        self.drink = drink_name
        d = CHALLENGES.get(drink_name, CHALLENGES["Neon Latte"])
        self.title = d.get("title", "INGREDIENT MATCH")
        self.ingredient = d.get("ingredient", "INGREDIENT")
        self.accent = d.get("accent", (120, 235, 255))
        self.colors = d.get(
            "tile_colors",
            [
                (245, 248, 255),
                (175, 225, 255),
                (210, 190, 255),
                (255, 220, 235),
                (150, 245, 220),
            ],
        )
        self.symbols = d.get(
            "symbols", ["milk", "syrup", "coffee", "ice", "mint"]
        )

        self.active = True
        self.done = False
        self.selected = None
        self.strikes = 0
        self.message_timer = 0
        self.done_timer = 0
        self.pulse = 0

        if drink_name == "Meteorite":
            self.level_mode = "DEFLECT"
            self.time_left = 10.0
            self.blocked_count = 0
            self.message = "SURVIVE 10s! MOUSE ROTATES ORBITAL SHIELD"
            self.debris_list = []
            self.spawn_timer = 0
        elif drink_name == "Stardust Matcha":
            self.level_mode = "WASD_RUN"
            self.time_left = 10.0
            self.dodged_count = 0
            self.message = "SURVIVE 10s! USE A/D OR LEFT/RIGHT TO DODGE"
            self.player_lane = 1
            self.barriers = []
            self.barrier_timer = 0
            self.key_cooldown = 0.0
            self.last_open_lane = -1
        elif drink_name == "Caramel Byte":
            self.level_mode = "SOLDER"
            self.time_left = 999.0
            self.message = f"CONNECT GREEN TO BLUE (STAGE {self.strikes + 1}/3)"
            self._reset_solder_board()
        else:
            self.level_mode = "MATCH3"
            self.time_left = 18.0
            self.message = "MATCH 3 INGREDIENTS"
            self.board = self._new_board()

    def _has_solder_path(self, glitches):
        queue = [(r, 0) for r in range(self.N) if (r, 0) not in glitches]
        visited = set(queue)

        while len(queue) > 0:
            r, c = queue.pop(0)

            if c == self.N - 1:
                return True

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.N and 0 <= nc < self.N:
                    if (nr, nc) not in visited and (nr, nc) not in glitches:
                        visited.add((nr, nc))
                        queue.append((nr, nc))

        return False

    def _reset_solder_board(self):
        self.solder_path = []
        self.is_soldering = False
        while True:
            glitches = set()
            while len(glitches) < 6:
                r = random.randint(0, 4)
                c = random.randint(1, 3)
                glitches.add((r, c))
            if self._has_solder_path(glitches):
                self.glitch_tiles = glitches
                break

    def handle_event(self, event):
        if not self.active:
            return

        if self.level_mode == "WASD_RUN":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    self.player_lane = max(0, self.player_lane - 1)
                    self.key_cooldown = 0.15
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.player_lane = min(2, self.player_lane + 1)
                    self.key_cooldown = 0.15
            return

        if self.level_mode == "SOLDER":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = self._cell(event.pos)
                if cell and cell[1] == 0 and cell not in self.glitch_tiles:
                    self.is_soldering = True
                    self.solder_path = [cell]
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_soldering:
                    self.is_soldering = False
                    self.solder_path = []
            return

        if self.level_mode == "MATCH3":
            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                return

            cell = self._cell(event.pos)
            if cell is None:
                return

            if self.selected is None:
                self.selected = cell
                self.message = "CHOOSE A NEIGHBOUR"
                self.message_timer = 0.6
                return

            if cell == self.selected:
                self.selected = None
                return

            a = self.selected
            self.selected = None

            # Verify adjacent neighbor swap
            if abs(a[0] - cell[0]) + abs(a[1] - cell[1]) == 1:
                self._try_swap(a, cell)
            else:
                self.selected = cell
                self.message = "TILES MUST BE ADJACENT"
                self.message_timer = 0.6

    def update(self, dt):
        if not self.active and not self.done:
            return False

        self.pulse += dt
        self.message_timer = max(0, self.message_timer - dt)

        if self.active:
            if self.level_mode != "SOLDER":
                self.time_left = max(0, self.time_left - dt)

            if self.time_left <= 0 and self.level_mode != "SOLDER":
                if self.level_mode in ("DEFLECT", "WASD_RUN"):
                    self._finish()
                else:
                    self._time_up()

            if self.level_mode == "DEFLECT":
                self._update_deflect(dt)
            elif self.level_mode == "WASD_RUN":
                self._update_wasd(dt)
            elif self.level_mode == "SOLDER":
                self._update_solder(dt)

        elif self.done:
            self.done_timer -= dt
            if self.done_timer <= 0:
                self.done = False
                return True

        return False

    def _update_deflect(self, dt):
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - self.center_pos[0], my - self.center_pos[1]
        self.shield_angle = math.atan2(dy, dx)

        self.spawn_timer += dt
        if self.spawn_timer >= 0.75:
            self.spawn_timer = 0
            ang = random.uniform(0, math.pi * 2)
            dist = 220
            x = self.center_pos[0] + math.cos(ang) * dist
            y = self.center_pos[1] + math.sin(ang) * dist
            self.debris_list.append({"x": x, "y": y, "ang": ang, "dist": dist})

        for deb in self.debris_list[:]:
            deb["dist"] -= 140 * dt
            deb["x"] = self.center_pos[0] + math.cos(deb["ang"]) * deb["dist"]
            deb["y"] = self.center_pos[1] + math.sin(deb["ang"]) * deb["dist"]

            if 60 <= deb["dist"] <= 80:
                diff = abs(
                    (deb["ang"] - self.shield_angle + math.pi) % (2 * math.pi)
                    - math.pi
                )
                if diff <= 0.35:
                    self.debris_list.remove(deb)
                    self.blocked_count += 1
                    self.message = (
                        f"DEFLECTED! TOTAL BLOCKED: {self.blocked_count}"
                    )
                    self.message_timer = 0.5

            elif deb["dist"] < 25:
                self.debris_list.remove(deb)
                self.time_left = 10.0
                self.blocked_count = 0
                self.debris_list = []
                self.message = "CORE HIT! RESETTING TIMER..."
                self.message_timer = 1.2

    def _update_wasd(self, dt):
        if self.key_cooldown > 0:
            self.key_cooldown = max(0.0, self.key_cooldown - dt)
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player_lane = max(0, self.player_lane - 1)
                self.key_cooldown = 0.18
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player_lane = min(2, self.player_lane + 1)
                self.key_cooldown = 0.18

        self.barrier_timer += dt
        if self.barrier_timer >= 0.8:
            self.barrier_timer = 0

            choices = [0, 1, 2]
            if self.last_open_lane in choices:
                choices.remove(self.last_open_lane)

            open_lane = random.choice(choices)
            self.last_open_lane = open_lane

            for l in range(3):
                if l != open_lane:
                    self.barriers.append({"lane": l, "y": 250})

        for b in self.barriers[:]:
            b["y"] += 280 * dt
            if 500 <= b["y"] <= 540 and b["lane"] == self.player_lane:
                self.barriers.remove(b)
                self.time_left = 10.0
                self.dodged_count = 0
                self.barriers = []
                self.last_open_lane = -1
                self.message = "HIT BY LASER! TIMER RESET..."
                self.message_timer = 1.0

            elif b["y"] > 580:
                self.barriers.remove(b)
                if b["lane"] == (self.player_lane + 1) % 3:
                    self.dodged_count += 1
                    self.message = f"DODGED! TOTAL: {self.dodged_count}"
                    self.message_timer = 0.5

    def _update_solder(self, dt):
        if not self.is_soldering:
            return

        cell = self._cell(pygame.mouse.get_pos())
        if cell is None:
            return

        if cell in self.glitch_tiles:
            self.is_soldering = False
            self.solder_path = []
            self.message = "SHORT CIRCUIT! GLITCH TILE HIT"
            self.message_timer = 0.8
            return

        last = self.solder_path[-1]
        if cell != last:
            if abs(cell[0] - last[0]) + abs(cell[1] - last[1]) == 1:
                self.solder_path.append(cell)

                if cell[1] == 4:
                    self.is_soldering = False
                    self.strikes += 1
                    self.message = f"CIRCUIT CONNECTED ({self.strikes}/{self.TARGET_STRIKES})"
                    self.message_timer = 0.8
                    if self.strikes >= self.TARGET_STRIKES:
                        self._finish()
                    else:
                        self._reset_solder_board()

    def draw(self, screen):
        if not self.active and not self.done:
            return

        ov = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        ov.fill((5, 8, 22, 180))
        screen.blit(ov, (0, 0))

        pygame.draw.rect(
            screen, self.accent, self.panel.inflate(12, 12), border_radius=24
        )
        pygame.draw.rect(screen, (18, 22, 43), self.panel, border_radius=20)
        pygame.draw.rect(screen, self.accent, self.panel, 2, border_radius=20)

        if self.done:
            self._draw_done(screen)
            return

        self._text(screen, self.title, self.ft, self.accent, 124)
        self._text(screen, self.drink.upper(), self.fb, (242, 245, 255), 154)
        self._text(
            screen,
            f"{self.ingredient}  •  LEVEL 3 PREPARATION",
            self.fs,
            (205, 212, 235),
            180,
        )

        if self.level_mode == "SOLDER":
            self._text(
                screen,
                "Goal: Connect Green to Blue. Avoid Red tiles!",
                self.fi,
                (0, 230, 204),
                201,
            )

        self._draw_strikes(screen)

        if self.level_mode == "DEFLECT":
            self._draw_deflect(screen)
        elif self.level_mode == "WASD_RUN":
            self._draw_wasd(screen)
        elif self.level_mode == "SOLDER":
            self._draw_solder(screen)
        else:
            self._draw_board(screen)

        self._text(
            screen,
            self.message if self.message_timer > 0 else "COMPLETE THE CHALLENGE",
            self.fs,
            (230, 235, 250),
            625,
        )

        if self.level_mode != "SOLDER":
            sec = max(0, int(self.time_left + 0.999))
            col = (255, 145, 165) if self.time_left <= 3 else self.accent
            self._text(screen, f"TIME  {sec}s", self.fs, col, 682)

    def _draw_deflect(self, screen):
        cx, cy = self.center_pos
        pygame.draw.circle(screen, (40, 50, 80), (cx, cy), 70, 2)
        pygame.draw.circle(screen, self.accent, (cx, cy), 22)

        sec = max(0, int(self.time_left + 0.999))
        timer_text = f"{sec}s"
        t_surf = self.timer_ring_font.render(timer_text, True, (15, 20, 35))
        screen.blit(t_surf, t_surf.get_rect(center=(cx, cy)))

        sa = self.shield_angle
        arc_rect = pygame.Rect(cx - 70, cy - 70, 140, 140)
        pygame.draw.arc(screen, (255, 255, 255), arc_rect, -sa - 0.35, -sa + 0.35, 7)

        for deb in self.debris_list:
            pygame.draw.circle(
                screen, (255, 100, 100), (int(deb["x"]), int(deb["y"])), 8
            )

    def _draw_wasd(self, screen):
        lanes_x = [540, 640, 740]
        for x in lanes_x:
            pygame.draw.line(screen, (40, 50, 80), (x, 250), (x, 560), 2)

        px = lanes_x[self.player_lane]
        pygame.draw.circle(screen, self.accent, (px, 520), 16)

        for b in self.barriers:
            bx = lanes_x[b["lane"]]
            pygame.draw.rect(
                screen, (255, 60, 90), (bx - 30, int(b["y"]), 60, 12), border_radius=4
            )

    def _draw_solder(self, screen):
        step = self.TILE + self.GAP
        for r in range(self.N):
            for c in range(self.N):
                rect = pygame.Rect(
                    self.grid.x + c * step,
                    self.grid.y + r * step,
                    self.TILE,
                    self.TILE,
                )
                if (r, c) in self.glitch_tiles:
                    pygame.draw.rect(screen, (220, 50, 70), rect, border_radius=10)
                    self._text(screen, "X", self.fb, (255, 255, 255), rect.centery)
                elif c == 0:
                    pygame.draw.rect(screen, (60, 180, 100), rect, border_radius=10)
                elif c == 4:
                    pygame.draw.rect(screen, (100, 140, 255), rect, border_radius=10)
                else:
                    pygame.draw.rect(screen, (30, 36, 60), rect, border_radius=10)

                pygame.draw.rect(screen, (60, 70, 100), rect, 2, border_radius=10)

        if len(self.solder_path) > 1:
            pts = []
            for r, c in self.solder_path:
                px = self.grid.x + c * step + self.TILE // 2
                py = self.grid.y + r * step + self.TILE // 2
                pts.append((px, py))
            pygame.draw.lines(screen, self.accent, False, pts, 6)

    def _new_board(self):
        for _ in range(500):
            b = [[None] * self.N for _ in range(self.N)]
            valid = True
            for r in range(self.N):
                for c in range(self.N):
                    choices = list(range(self.TYPES))
                    random.shuffle(choices)
                    picked = None
                    for v in choices:
                        if c >= 2 and b[r][c - 1] == v and b[r][c - 2] == v:
                            continue
                        if r >= 2 and b[r - 1][c] == v and b[r - 2][c] == v:
                            continue
                        picked = v
                        break
                    if picked is None:
                        valid = False
                        break
                    b[r][c] = picked
                if not valid:
                    break
            if valid and self._has_move(b):
                return b

        b = []
        for r in range(self.N):
            row = []
            for c in range(self.N):
                row.append(random.choice(range(self.TYPES)))
            b.append(row)
        return b

    def _matches(self, b=None):
        b = self.board if b is None else b
        out = set()
        for r in range(self.N):
            for c in range(self.N - 2):
                if b[r][c] is not None and b[r][c] == b[r][c + 1] == b[r][c + 2]:
                    out.update((r, c + i) for i in range(3))
        for c in range(self.N):
            for r in range(self.N - 2):
                if b[r][c] is not None and b[r + 1][c] == b[r + 2][c] == b[r][c]:
                    out.update((r + i, c) for i in range(3))
        return {(r, c) for r, c in out if b[r][c] is not None}

    def _has_move(self, b):
        for r in range(self.N):
            for c in range(self.N):
                for dr, dc in ((0, 1), (1, 0)):
                    nr, nc = r + dr, c + dc
                    if nr >= self.N or nc >= self.N:
                        continue
                    b[r][c], b[nr][nc] = b[nr][nc], b[r][c]
                    ok = bool(self._matches(b))
                    b[r][c], b[nr][nc] = b[nr][nc], b[r][c]
                    if ok:
                        return True
        return False

    def _swap(self, a, b):
        r, c = a
        nr, nc = b
        self.board[r][c], self.board[nr][nc] = (
            self.board[nr][nc],
            self.board[r][c],
        )

    def _resolve(self):
        hit = self._matches()
        if not hit:
            return False
        for r, c in hit:
            self.board[r][c] = None
        for c in range(self.N):
            vals = [
                self.board[r][c]
                for r in range(self.N)
                if self.board[r][c] is not None
            ]
            for r in range(self.N - 1, -1, -1):
                self.board[r][c] = vals.pop() if vals else None
        for r in range(self.N):
            for c in range(self.N):
                if self.board[r][c] is not None:
                    continue
                choices = list(range(self.TYPES))
                random.shuffle(choices)
                self.board[r][c] = next(
                    (
                        v
                        for v in choices
                        if not (
                            c > 1 and self.board[r][c - 1] == self.board[r][c - 2] == v
                        )
                        and not (
                            r > 1 and self.board[r - 1][c] == self.board[r - 2][c] == v
                        )
                    ),
                    random.randrange(self.TYPES),
                )
        if self._matches() or not self._has_move(self.board):
            self.board = self._new_board()
        self.strikes += 1
        self.message = f"STRIKE {self.strikes} / {self.TARGET_STRIKES}"
        self.message_timer = 0.8
        if self.strikes >= self.TARGET_STRIKES:
            self._finish()
        return True

    def _try_swap(self, a, b):
        self._swap(a, b)
        if self._matches():
            return self._resolve()
        self._swap(a, b)
        self.message = "TRY ANOTHER SWAP"
        self.message_timer = 0.8
        return False

    def _cell(self, pos):
        if not self.grid.collidepoint(pos):
            return None
        step = self.TILE + self.GAP
        x, y = pos
        c, r = (x - self.grid.x) // step, (y - self.grid.y) // step
        if not (0 <= r < self.N and 0 <= c < self.N):
            return None
        if (
            (x - self.grid.x) % step >= self.TILE
            or (y - self.grid.y) % step >= self.TILE
        ):
            return None
        return int(r), int(c)

    def _time_up(self):
        self.active = False
        self.done = False
        self.selected = None
        self.strikes = 0
        self.time_left = 18.0
        self.message = "TIME'S UP - TRY AGAIN!"
        self.active = True
        if self.level_mode == "MATCH3":
            self.board = self._new_board()
        elif self.level_mode == "SOLDER":
            self._reset_solder_board()

    def _finish(self):
        self.active = False
        self.done = True
        self.selected = None
        self.done_timer = 1.2
        self.message = "INGREDIENT READY!"

    def _text(self, screen, text, font, color, y):
        s = font.render(text, True, color)
        screen.blit(s, s.get_rect(center=(640, y)))

    def _draw_strikes(self, screen):
        y_title = 216 if self.level_mode == "SOLDER" else 210
        y_val = 244 if self.level_mode == "SOLDER" else 238
        y_bars = 267 if self.level_mode == "SOLDER" else 263

        if self.level_mode == "DEFLECT":
            self._text(
                screen, "METEORITES BLOCKED", self.strike_title_font, (210, 218, 240), y_title
            )
            surf = self.strike_big_font.render(str(self.blocked_count), True, self.accent)
            screen.blit(surf, surf.get_rect(center=(640, y_val)))
            return
        elif self.level_mode == "WASD_RUN":
            self._text(
                screen, "LASERS DODGED", self.strike_title_font, (210, 218, 240), y_title
            )
            surf = self.strike_big_font.render(str(self.dodged_count), True, self.accent)
            screen.blit(surf, surf.get_rect(center=(640, y_val)))
            return

        self._text(
            screen, "STRIKES", self.strike_title_font, (210, 218, 240), y_title
        )
        value = f"{self.strikes} / {self.TARGET_STRIKES}"
        pulse = 1.0 + 0.04 * math.sin(self.pulse * 8) if self.strikes else 1.0
        surf = self.strike_big_font.render(
            value, True, self.accent if self.strikes else (235, 240, 255)
        )
        if pulse != 1.0:
            surf = pygame.transform.smoothscale(
                surf,
                (int(surf.get_width() * pulse), int(surf.get_height() * pulse)),
            )
        screen.blit(surf, surf.get_rect(center=(640, y_val)))
        for i in range(self.TARGET_STRIKES):
            x = 570 + i * 70
            filled = i < self.strikes
            r = pygame.Rect(x, y_bars, 50, 10)
            pygame.draw.rect(screen, (45, 52, 78), r, border_radius=5)
            if filled:
                pygame.draw.rect(screen, self.accent, r, border_radius=5)
                pygame.draw.circle(screen, (250, 255, 255), (x + 25, y_bars + 5), 3)

    def _draw_board(self, screen):
        mouse = self._cell(pygame.mouse.get_pos())
        step = self.TILE + self.GAP
        for r in range(self.N):
            for c in range(self.N):
                rect = pygame.Rect(
                    self.grid.x + c * step,
                    self.grid.y + r * step,
                    self.TILE,
                    self.TILE,
                )
                v = self.board[r][c]
                col = self.colors[v % len(self.colors)]
                pygame.draw.rect(screen, (27, 32, 57), rect, border_radius=12)
                if mouse == (r, c):
                    pygame.draw.rect(
                        screen, (100, 115, 155), rect.inflate(4, 4), 2, border_radius=14
                    )
                if self.selected == (r, c):
                    pygame.draw.rect(
                        screen, self.accent, rect.inflate(6, 6), 3, border_radius=15
                    )
                glow = pygame.Surface(
                    (self.TILE + 14, self.TILE + 14), pygame.SRCALPHA
                )
                pygame.draw.circle(glow, (*col, 35), (38, 38), 24)
                screen.blit(glow, (rect.x - 7, rect.y - 7))
                inner = rect.inflate(-8, -8)
                pygame.draw.rect(screen, col, inner, border_radius=14)
                self._icon(
                    screen, rect.center, self.symbols[v % len(self.symbols)], col
                )

    def _icon(self, s, center, k, col):
        x, y = center
        d = tuple(max(25, v - 85) for v in col)
        w = (248, 252, 255)
        if k == "milk":
            r = pygame.Rect(x - 10, y - 10, 20, 22)
            pygame.draw.rect(s, w, r, border_radius=5)
            pygame.draw.rect(s, d, r, 2, border_radius=5)
            pygame.draw.rect(s, d, (x - 6, y - 15, 12, 6), border_radius=2)
        elif k == "coffee":
            pygame.draw.ellipse(s, (105, 65, 48), (x - 13, y - 10, 26, 20))
            pygame.draw.arc(
                s, (235, 190, 145), (x - 7, y - 8, 14, 16), 1.1, 5.1, 2
            )
        elif k == "syrup":
            pygame.draw.rect(
                s, (255, 235, 245), (x - 10, y - 6, 20, 18), border_radius=5
            )
            pygame.draw.rect(s, d, (x - 10, y - 6, 20, 18), 2, border_radius=5)
            pygame.draw.rect(s, col, (x - 6, y - 14, 12, 8), border_radius=3)
        elif k in ("spice", "matcha"):
            pygame.draw.circle(
                s,
                (190, 105, 70) if k == "spice" else (165, 195, 105),
                (x, y),
                12,
            )
            pygame.draw.circle(
                s,
                (250, 190, 130) if k == "spice" else (225, 245, 170),
                (x - 3, y - 3),
                3,
            )
        elif k == "battery":
            pygame.draw.rect(
                s, (120, 220, 255), (x - 10, y - 12, 20, 24), border_radius=4
            )
            pygame.draw.rect(s, d, (x - 10, y - 12, 20, 24), 2, border_radius=4)
            pygame.draw.rect(
                s, (245, 235, 110), (x - 3, y - 4, 6, 8), border_radius=2
            )
        elif k == "power":
            pygame.draw.polygon(
                s,
                (250, 235, 120),
                [
                    (x + 2, y - 14),
                    (x - 7, y + 1),
                    (x, y + 1),
                    (x - 4, y + 14),
                    (x + 9, y - 4),
                    (x + 2, y - 4),
                ],
            )
        elif k == "orb":
            pygame.draw.circle(s, (215, 170, 255), (x, y), 12)
            pygame.draw.circle(s, w, (x - 4, y - 4), 3)
        elif k == "mint":
            pygame.draw.polygon(
                s,
                (90, 235, 165),
                [
                    (x, y + 13),
                    (x - 12, y + 2),
                    (x - 7, y - 11),
                    (x + 4, y - 14),
                    (x + 11, y - 4),
                    (x + 7, y + 8),
                ],
            )
            pygame.draw.line(s, (55, 155, 115), (x, y + 10), (x + 3, y - 8), 2)
        elif k == "water":
            pygame.draw.polygon(
                s,
                (130, 205, 255),
                [(x, y - 14), (x + 11, y + 3), (x, y + 14), (x - 11, y + 3)],
            )
        elif k == "star":
            pts = [
                (
                    x + math.cos(-math.pi / 2 + i * math.pi / 2.5) * 14,
                    y + math.sin(-math.pi / 2 + i * math.pi / 2.5) * 14,
                )
                for i in range(5)
            ]
            pygame.draw.polygon(s, (255, 225, 110), pts)
            pygame.draw.circle(s, (255, 250, 205), (x, y), 3)
        elif k == "ice":
            pts = [
                (x - 12, y - 8),
                (x + 4, y - 14),
                (x + 13, y - 4),
                (x + 9, y + 12),
                (x - 7, y + 14),
                (x - 14, y + 3),
            ]
            pygame.draw.polygon(s, (215, 245, 255), pts)
            pygame.draw.polygon(s, d, pts, 2)
            pygame.draw.line(s, w, (x - 7, y - 5), (x + 4, y - 9), 2)
        else:
            pygame.draw.circle(s, w, (x, y), 11)

    def _draw_done(self, s):
        self._text(
            s,
            "INGREDIENT READY!",
            pygame.font.SysFont("arial", 38, True),
            self.accent,
            255,
        )
        self._text(
            s,
            f"{self.ingredient} is ready for the blender.",
            self.fb,
            (235, 240, 255),
            300,
        )

        stat_text = f"STRIKES COMPLETED  {self.strikes} / {self.TARGET_STRIKES}"
        if self.level_mode == "DEFLECT":
            stat_text = f"METEORITES BLOCKED: {self.blocked_count}"
        elif self.level_mode == "WASD_RUN":
            stat_text = f"LASERS DODGED: {self.dodged_count}"

        self._text(s, stat_text, self.fs, (205, 212, 235), 355)
        pygame.draw.circle(s, (25, 32, 58), (640, 435), 68)
        pygame.draw.circle(s, self.accent, (640, 435), 68, 3)
        self._icon(
            s,
            (640, 435),
            self.symbols[1 % len(self.symbols)],
            (230, 240, 255),
        )
        self._text(
            s,
            "Returning to the Mixing Station...",
            self.fs,
            (145, 155, 185),
            535,
        )
import math
import random
import pygame

# -------------------------------------------------------------
# CHALLENGE METADATA & INGREDIENT CONFIGURATIONS
# -------------------------------------------------------------
CHALLENGES = {
    "Neon Latte": {
        "title": "MILK MATCH OVERDRIVE", "ingredient": "MILK", "accent": (120, 235, 255),
        "tile_colors": [(245, 248, 255), (175, 225, 255), (210, 190, 255), (255, 220, 235), (150, 245, 220)],
        "symbols": ["milk", "coffee", "syrup", "foam", "ice"],
    },
    "Milkyway": {
        "title": "STARDUST HYPER MATCH", "ingredient": "STARDUST", "accent": (205, 170, 255),
        "tile_colors": [(235, 220, 255), (175, 145, 255), (120, 210, 255), (255, 235, 150), (245, 175, 225)],
        "symbols": ["milk", "chocolate", "star", "syrup", "ice"],
    },
    "Void Chai": {
        "title": "QUANTUM SPICE MATCH", "ingredient": "SPICE", "accent": (255, 175, 125),
        "tile_colors": [(255, 205, 150), (205, 155, 255), (255, 150, 185), (175, 235, 190), (245, 220, 150)],
        "symbols": ["milk", "spice", "syrup", "star", "ice"],
    },
    "Cyber Fuel": {"title": "GRAVITY SHIELD PROTOCOL", "ingredient": "METEORITE DUST", "accent": (255, 90, 120)},
    "Hologram Frappe": {"title": "OVERDRIVE LASER THREAD", "ingredient": "STARDUST MATCHA", "accent": (140, 255, 120)},
    "Pixel Lemint": {"title": "PIXEL CIRCUIT LINK", "ingredient": "CARAMEL BYTE", "accent": (255, 180, 60)},
    "Meteorite": {"title": "NEON DASH EXTREME", "ingredient": "METEORITE CORE", "accent": (255, 90, 120)},
    "Stardust Matcha": {"title": "HYPER FLICK AIM ARENA", "ingredient": "STARDUST MATCHA", "accent": (140, 255, 120)},
    "Caramel Byte": {"title": "RHYTHM BLITZ", "ingredient": "CARAMEL BYTE", "accent": (255, 180, 60)},
}

# Pre-defined guide text for all non-Match3 modes
GUIDE_DATA = {
    "DEFLECT": ("GRAVITY SHIELD PROTOCOL", [
        "Move the shield with your mouse.",
        "Block incoming debris before it hits the core.",
        "Block 15 objects to complete the challenge."
    ]),
    "WASD_RUN": ("OVERDRIVE RUN", [
        "Use A / D or LEFT / RIGHT to change lanes.",
        "Avoid the barriers and keep moving forward.",
        "Dodge 15 barriers to complete the challenge."
    ]),
    "SOLDER": ("PIXEL CIRCUIT LINK", [
        "Click and drag from IN to OUT to connect the circuit.",
        "Avoid the red glitch tiles while drawing the path.",
        "Complete 5 connections to finish."
    ]),
    "NEON_DASH": ("NEON DASH EXTREME", [
        "Press SPACE / W / UP or click to jump.",
        "Jump over spikes and drones without crashing.",
        "Reach 2,800 points to complete the challenge.",
        "Misses and crashes cost score/combo."
    ]),
    "AIM_RUSH": ("HYPER FLICK AIM ARENA", [
        "Click the bright targets as quickly as possible.",
        "Avoid the red X / danger targets.",
        "Reach 3,800 points to complete the challenge.",
        "Avoid danger targets and keep your combo."
    ]),
    "RHYTHM_RUSH": ("RHYTHM BLITZ", [
        "Click the matching lane when each note reaches the hit line.",
        "Use your mouse to hit the notes accurately.",
        "Reach 3,000 points to complete the challenge.",
        "Accuracy and combo are critical."
    ]),
}


class MiniChallenge:
    """Manages all ingredient calibration mini-games and interactive trials."""
    N, TILE, GAP, TYPES, TARGET_STRIKES = 5, 62, 6, 5, 3

    def __init__(self):
        pygame.font.init()
        # UI Layout Rectangles
        self.panel = pygame.Rect(280, 92, 720, 540)
        self.exit_button = pygame.Rect(928, 162, 58, 28)
        self.pause_button = pygame.Rect(846, 162, 76, 28)
        self.guide_button = pygame.Rect(928, 126, 58, 28)
        self.grid = pygame.Rect(473, 275, 334, 334)

        # Typography
        self.ft = pygame.font.SysFont("arial", 29, True)
        self.fb = pygame.font.SysFont("arial", 21, True)
        self.fs = pygame.font.SysFont("arial", 17, True)
        self.fi = pygame.font.SysFont("arial", 14, True)
        self.strike_title_font = pygame.font.SysFont("arial", 16, True)
        self.strike_big_font = pygame.font.SysFont("arial", 36, True)
        self.timer_ring_font = pygame.font.SysFont("arial", 16, True)
        self.fd = pygame.font.SysFont("arial", 38, True)

        # Global Game State
        self.active = self.done = self.failed = self.paused = self.show_guide = False
        self.drink, self.title, self.ingredient = "", "INGREDIENT MATCH", "INGREDIENT"
        self.accent = (120, 235, 255)
        self.colors = [(245, 248, 255), (175, 225, 255), (210, 190, 255), (255, 220, 235), (150, 245, 220)]
        self.symbols = ["milk", "syrup", "coffee", "ice", "mint"]
        self.board, self.selected, self.strikes, self.time_left = [], None, 0, 18.0
        self.message_timer, self.message, self.done_timer, self.pulse = 0, "", 0, 0
        self.particles, self.floating_texts = [], []
        self.screen_shake, self.jumpscare_flash = 0.0, 0.0
        self.level_mode, self.center_pos = "MATCH3", (640, 430)

        # Mode-specific Attributes
        self.shield_angle, self.debris_list, self.spawn_timer, self.blocked_count, self.target_blocked = 0, [], 0, 0, 8
        self.player_lane, self.barriers, self.barrier_timer, self.key_cooldown = 1, [], 0, 0.0
        self.dodged_count, self.target_dodged, self.last_open_lane = 0, 15, -1
        self.is_soldering, self.solder_path, self.glitch_tiles = False, [], set()
        self.solder_connections, self.target_connections, self.glitch_timer, self.pulse_phase = 0, 5, 0.0, 0.0
        self.dash_player_y, self.dash_velocity, self.dash_on_ground = 535.0, 0.0, True
        self.dash_obstacles, self.dash_spawn_timer, self.dash_speed = [], 0.0, 340.0
        self.dash_score, self.dash_combo, self.target_dash_score = 0, 0, 2800
        self.aim_targets, self.aim_targets_left, self.aim_combo = [], 20, 0
        self.aim_score, self.aim_best_combo, self.aim_spawn_timer, self.target_aim_score = 0, 0, 0.0, 3800
        self.rhythm_notes, self.rhythm_spawn_timer, self.rhythm_hit_count = [], 0.0, 0
        self.rhythm_combo, self.rhythm_score, self.rhythm_speed, self.target_rhythm_score = 0, 0, 320.0, 3000

    # -------------------------------------------------------------
    # VISUAL EFFECTS & PARTICLES
    # -------------------------------------------------------------
    def add_particles(self, x, y, color, count=12, speed_mult=1.0):
        for _ in range(count):
            a = random.uniform(0, math.pi * 2)
            speed = random.uniform(25, 130) * speed_mult
            self.particles.append({
                "x": x, "y": y, "vx": math.cos(a) * speed, "vy": math.sin(a) * speed,
                "life": random.uniform(0.3, 0.6), "color": color, "size": random.randint(2, 5),
            })

    def add_floating_text(self, text, x, y, color=(255, 230, 100)):
        self.floating_texts.append({"text": text, "x": x, "y": y, "vy": -50.0, "life": 0.5, "color": color})

    # -------------------------------------------------------------
    # CHALLENGE INITIALIZATION
    # -------------------------------------------------------------
    def start_challenge(self, drink_name):
        self.drink = drink_name
        d = CHALLENGES.get(drink_name, CHALLENGES["Neon Latte"])
        self.title = d.get("title", "INGREDIENT MATCH")
        self.ingredient = d.get("ingredient", "INGREDIENT")
        self.accent = d.get("accent", (120, 235, 255))
        self.colors = d.get("tile_colors", self.colors)
        self.symbols = d.get("symbols", self.symbols)

        self.active, self.done, self.failed, self.paused, self.show_guide = True, False, False, False, True
        self.selected, self.strikes, self.message_timer, self.done_timer = None, 0, 0, 0
        self.particles.clear()
        self.floating_texts.clear()
        self.screen_shake = self.jumpscare_flash = 0
        self.message = ""

        if drink_name == "Cyber Fuel":
            self.level_mode, self.time_left, self.blocked_count = "DEFLECT", 999.0, 0
            self.debris_list, self.spawn_timer = [], 0
        elif drink_name == "Hologram Frappe":
            self.level_mode, self.time_left, self.target_dodged, self.dodged_count = "WASD_RUN", 999.0, 15, 0
            self.player_lane, self.barriers, self.barrier_timer = 1, [], 0
            self.key_cooldown, self.last_open_lane = 0, -1
        elif drink_name == "Pixel Lemint":
            self.level_mode, self.time_left, self.target_connections, self.solder_connections = "SOLDER", 999.0, 5, 0
            self._reset_solder_board()
        elif drink_name == "Meteorite":
            self.level_mode = "NEON_DASH"
            self._start_neon_dash()
        elif drink_name == "Stardust Matcha":
            self.level_mode = "AIM_RUSH"
            self._start_aim_rush()
        elif drink_name == "Caramel Byte":
            self.level_mode = "RHYTHM_RUSH"
            self._start_rhythm_rush()
        else:
            self.level_mode, self.time_left = "MATCH3", 20
            self.board = self._new_board()

    # -------------------------------------------------------------
    # SOLDER CIRCUIT GRAPH SOLVER & GENERATOR
    # -------------------------------------------------------------
    def _solder_has_path(self, glitch_tiles):
        last_col = self.N - 1
        seen = {(r, 0) for r in range(self.N)}
        stack = list(seen)
        while stack:
            r, c = stack.pop()
            if c == last_col:
                return True
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.N and 0 <= nc < self.N and (nr, nc) not in seen and (nr, nc) not in glitch_tiles:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return False

    def _reset_solder_board(self):
        self.solder_path, self.is_soldering = [], False
        interior = [(r, c) for r in range(self.N) for c in range(1, self.N - 1)]
        count, glitch = 10, set()
        for attempt in range(300):
            if attempt and attempt % 60 == 0:
                count = max(4, count - 1)
            glitch = set(random.sample(interior, count))
            if self._solder_has_path(glitch):
                break
        else:
            glitch = set()
        self.glitch_tiles, self.glitch_timer = glitch, 0

    # -------------------------------------------------------------
    # EVENT HANDLING
    # -------------------------------------------------------------
    def handle_event(self, event):
        if not self.active or self.done or self.failed:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit_button.collidepoint(event.pos):
                self._exit_challenge()
                return
            if self.show_guide:
                if pygame.Rect(565, 500, 150, 40).collidepoint(event.pos):
                    self.show_guide = False
                return
            if self.guide_button.collidepoint(event.pos):
                self.show_guide = True
                return
            if self.pause_button.collidepoint(event.pos):
                self.paused = not self.paused
                return

        if self.paused:
            return

        if self.level_mode == "WASD_RUN" and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.player_lane = max(0, self.player_lane - 1)
                self.key_cooldown = 0.08
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.player_lane = min(2, self.player_lane + 1)
                self.key_cooldown = 0.08

        elif self.level_mode == "NEON_DASH":
            jump = (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP)) or (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            )
            if jump and self.dash_on_ground:
                self.dash_velocity, self.dash_on_ground = -580, False
                self.add_particles(450, 535, self.accent, 10)

        elif self.level_mode == "AIM_RUSH":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._aim_click(*event.pos)

        elif self.level_mode == "RHYTHM_RUSH":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._rhythm_press(max(0, min(3, int((event.pos[0] - 500) / 70))))

        elif self.level_mode == "SOLDER":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = self._cell(event.pos)
                if cell and cell[1] == 0 and cell not in self.glitch_tiles:
                    self.is_soldering = True
                    self.solder_path = [cell]
                    self.add_particles(*event.pos, self.accent, 8)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_soldering:
                    self.is_soldering = False
                    self.solder_path = []
                    self.screen_shake = 0.3
                    self.add_floating_text("CIRCUIT BROKEN!", 640, 400, (255, 100, 100))

        elif self.level_mode == "MATCH3":
            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                return
            cell = self._cell(event.pos)
            if cell is None:
                return
            if self.selected is None:
                self.selected = cell
            elif cell == self.selected:
                self.selected = None
            else:
                first = self.selected
                self.selected = None
                if abs(first[0] - cell[0]) + abs(first[1] - cell[1]) == 1:
                    self._try_swap(first, cell)
                else:
                    self.selected = cell

    # -------------------------------------------------------------
    # UPDATE & WIN CONDITION LOGIC
    # -------------------------------------------------------------
    def _is_target_reached(self):
        targets = {
            "DEFLECT": self.blocked_count >= self.target_blocked,
            "WASD_RUN": self.dodged_count >= self.target_dodged,
            "SOLDER": self.solder_connections >= self.target_connections,
            "NEON_DASH": self.dash_score >= self.target_dash_score,
            "AIM_RUSH": self.aim_score >= self.target_aim_score,
            "RHYTHM_RUSH": self.rhythm_score >= self.target_rhythm_score,
            "MATCH3": self.strikes >= self.TARGET_STRIKES,
        }
        return targets.get(self.level_mode, False)

    def update(self, dt):
        if not self.active:
            return False
        if self.failed:
            self.active = self.failed = False
            return False
        if self.done:
            self.done_timer -= dt
            if self.done_timer <= 0:
                self.active = self.done = False
                return True
            return False
        if self.paused or self.show_guide:
            return False

        self.pulse += dt
        self.pulse_phase += dt * 6
        self.message_timer = max(0, self.message_timer - dt)
        self.screen_shake = max(0, self.screen_shake - dt)
        self.jumpscare_flash = max(0, self.jumpscare_flash - dt)

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        for f in self.floating_texts[:]:
            f["y"] += f["vy"] * dt
            f["life"] -= dt
            if f["life"] <= 0:
                self.floating_texts.remove(f)

        if self.level_mode not in ("DEFLECT", "WASD_RUN", "SOLDER", "NEON_DASH", "AIM_RUSH", "RHYTHM_RUSH"):
            self.time_left = max(0, self.time_left - dt)
            if self.time_left <= 0:
                self._check_win_condition()

        updates = {
            "DEFLECT": self._update_deflect, "WASD_RUN": self._update_wasd, "SOLDER": self._update_solder,
            "NEON_DASH": self._update_neon_dash, "AIM_RUSH": self._update_aim_rush, "RHYTHM_RUSH": self._update_rhythm_rush,
        }
        if self.level_mode in updates:
            updates[self.level_mode](dt)

        if not self.done and self._is_target_reached():
            self._finish()
        return False

    def _check_win_condition(self):
        if self._is_target_reached():
            self._finish()
        else:
            self._fail()

    # -------------------------------------------------------------
    # NEON DASH
    # -------------------------------------------------------------
    def _start_neon_dash(self):
        self.time_left, self.dash_player_y, self.dash_velocity = 999.0, 535, 0
        self.dash_on_ground = True
        self.dash_obstacles = []
        self.dash_spawn_timer, self.dash_speed, self.dash_score, self.dash_combo = 0.5, 360, 0, 0
        self.message = ""

    def _update_neon_dash(self, dt):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.dash_on_ground:
            self.dash_velocity, self.dash_on_ground = -580, False

        ground = 535
        self.dash_velocity += 1400 * dt
        self.dash_player_y += self.dash_velocity * dt
        if self.dash_player_y >= ground:
            self.dash_player_y, self.dash_velocity, self.dash_on_ground = ground, 0, True

        self.dash_spawn_timer -= dt
        if self.dash_spawn_timer <= 0:
            self.dash_spawn_timer = random.uniform(0.6, 1.0)
            kind = random.choice(["spike", "spike", "double", "floating_drone"])
            w = 34 if kind == "spike" else 68 if kind == "double" else 45
            h = 42 if kind != "floating_drone" else 35
            y = ground if kind != "floating_drone" else ground - 75
            self.dash_obstacles.append({"x": 1040, "y": y, "kind": kind, "w": w, "h": h, "passed": False})

        for ob in self.dash_obstacles[:]:
            ob["x"] -= self.dash_speed * dt
            if not ob["passed"] and ob["x"] + ob["w"] < 450:
                ob["passed"] = True
                self.dash_score += 140 + self.dash_combo * 20
                self.dash_combo += 1
                self.dash_speed = min(540, self.dash_speed + 10)

            player = pygame.Rect(432, int(self.dash_player_y - 36), 36, 36)
            target = pygame.Rect(int(ob["x"]), int(ob["y"] - ob["h"]), ob["w"], ob["h"])
            if player.colliderect(target):
                self.dash_combo, self.screen_shake, self.jumpscare_flash = 0, 0.55, 0.4
                self.dash_score = max(0, self.dash_score - 180)
                self.dash_speed = max(360, self.dash_speed - 50)
                self.dash_obstacles.remove(ob)
                continue
            if ob["x"] < 300:
                self.dash_obstacles.remove(ob)

    def _draw_neon_dash(self, screen):
        ground = 535
        for x in range(360, 950, 70):
            pygame.draw.line(screen, (35, 48, 75), (x, ground), (x + 35, 590), 2)
        pygame.draw.line(screen, self.accent, (340, ground), (960, ground), 3)
        pygame.draw.circle(screen, self.accent, (450, int(self.dash_player_y - 18)), 18)

        for ob in self.dash_obstacles:
            x, y, w, h = int(ob["x"]), int(ob["y"]), ob["w"], ob["h"]
            if ob["kind"] in ("spike", "double"):
                count = 1 if ob["kind"] == "spike" else 2
                sw = w / count
                for i in range(count):
                    pygame.draw.polygon(screen, (255, 75, 105), [
                        (x + i * sw, ground), (x + (i + 0.5) * sw, ground - h), (x + (i + 1) * sw, ground)
                    ])
            else:
                pygame.draw.rect(screen, (255, 140, 60), (x, y - h, w, h), border_radius=6)

        self._text(screen, f"SCORE {self.dash_score} / {self.target_dash_score}", self.fs, self.accent, 220)
        self._text(screen, f"COMBO x{self.dash_combo}", self.fs, (255, 230, 120), 240)

    # -------------------------------------------------------------
    # AIM RUSH
    # -------------------------------------------------------------
    def _start_aim_rush(self):
        self.time_left, self.aim_targets, self.aim_targets_left = 999.0, [], 20
        self.aim_combo = self.aim_score = self.aim_best_combo = self.aim_spawn_timer = 0

    def _aim_click(self, mx, my):
        for target in self.aim_targets[:]:
            if math.hypot(mx - target["x"], my - target["y"]) <= target["r"]:
                if target["is_bomb"]:
                    self.aim_combo, self.screen_shake, self.jumpscare_flash = 0, 0.6, 0.45
                    self.aim_score = max(0, self.aim_score - 200)
                    self.add_floating_text("BREACH! -200", mx, my - 20, (255, 50, 50))
                else:
                    self.aim_targets_left -= 1
                    self.aim_combo += 1
                    self.aim_best_combo = max(self.aim_best_combo, self.aim_combo)
                    bonus = 150 + self.aim_combo * 35
                    self.aim_score += bonus
                    self.screen_shake = 0.12
                    self.add_floating_text(f"+{bonus}", mx, my, (150, 255, 180))
                self.aim_targets.remove(target)
                return
        self.aim_combo, self.screen_shake = 0, 0.15
        self.aim_score = max(0, self.aim_score - 50)

    def _update_aim_rush(self, dt):
        self.aim_spawn_timer -= dt
        if self.aim_spawn_timer <= 0 and len(self.aim_targets) < 5:
            self.aim_spawn_timer = random.uniform(0.3, 0.55)
            self.aim_targets.append({
                "x": random.randint(400, 880), "y": random.randint(310, 530), "r": random.randint(22, 30),
                "is_bomb": random.random() < 0.32, "vx": random.uniform(-70, 70), "vy": random.uniform(-70, 70),
                "life": random.uniform(1.4, 2.5),
            })

        for target in self.aim_targets[:]:
            target["x"] += target["vx"] * dt
            target["y"] += target["vy"] * dt
            if target["x"] < 380 or target["x"] > 900:
                target["vx"] *= -1
            if target["y"] < 290 or target["y"] > 560:
                target["vy"] *= -1
            target["life"] -= dt
            if target["life"] <= 0:
                self.aim_targets.remove(target)
                if not target["is_bomb"]:
                    self.aim_combo = 0

    def _draw_aim_rush(self, screen):
        area = pygame.Rect(360, 275, 560, 310)
        pygame.draw.rect(screen, (15, 20, 38), area, border_radius=14)
        pygame.draw.rect(screen, self.accent, area, 2, border_radius=14)

        for target in self.aim_targets:
            x, y, r = int(target["x"]), int(target["y"]), int(target["r"])
            color = (255, 60, 90) if target["is_bomb"] else self.accent
            pygame.draw.circle(screen, tuple(c // 3 for c in color), (x, y), r + 6)
            pygame.draw.circle(screen, color, (x, y), r)
            pygame.draw.circle(screen, (245, 248, 255), (x, y), max(3, r // 3))
            if target["is_bomb"]:
                self._text(screen, "X", self.fs, (255, 255, 255), y)

        self._text(screen, f"SCORE {self.aim_score} / {self.target_aim_score}", self.fs, self.accent, 220)
        self._text(screen, f"COMBO x{self.aim_combo}", self.fs, (255, 230, 120), 240)

    # -------------------------------------------------------------
    # RHYTHM BLITZ
    # -------------------------------------------------------------
    def _start_rhythm_rush(self):
        self.time_left, self.rhythm_notes = 999.0, []
        self.rhythm_spawn_timer, self.rhythm_hit_count = 0.2, 0
        self.rhythm_combo, self.rhythm_score, self.rhythm_speed = 0, 0, 340

    def _rhythm_press(self, lane):
        notes = [n for n in self.rhythm_notes if n["lane"] == lane and not n["hit"]]
        if not notes:
            self.rhythm_combo, self.rhythm_score = 0, max(0, self.rhythm_score - 100)
            return

        note = min(notes, key=lambda n: abs(n["y"] - 530))
        diff = abs(note["y"] - 530)
        if diff > 75:
            self.rhythm_combo, self.rhythm_score = 0, max(0, self.rhythm_score - 100)
            return

        grade, points = ("PERFECT!", 400) if diff <= 15 else ("GOOD", 250) if diff <= 38 else ("OK", 120)
        note["hit"] = True
        self.rhythm_hit_count += 1
        self.rhythm_combo += 1
        self.rhythm_score += points + self.rhythm_combo * 20
        self.rhythm_speed = min(480, self.rhythm_speed + 6)

        x = [500, 570, 640, 710][lane]
        self.add_particles(x, 530, self.accent, 12)
        self.add_floating_text(grade, x, 500, (255, 230, 100))

    def _update_rhythm_rush(self, dt):
        self.rhythm_spawn_timer -= dt
        if self.rhythm_spawn_timer <= 0:
            self.rhythm_spawn_timer = max(0.24, 0.5 - self.rhythm_hit_count * 0.008)
            self.rhythm_notes.append({"lane": random.randrange(4), "y": 275, "hit": False})

        for note in self.rhythm_notes[:]:
            note["y"] += self.rhythm_speed * dt
            if note["y"] > 585 and not note["hit"]:
                self.rhythm_notes.remove(note)
                self.rhythm_combo, self.rhythm_score = 0, max(0, self.rhythm_score - 80)
            elif note["hit"]:
                self.rhythm_notes.remove(note)

    def _draw_rhythm_rush(self, screen):
        lane_x = [500, 570, 640, 710]
        for i, x in enumerate(lane_x):
            rect = pygame.Rect(x - 29, 275, 58, 305)
            pygame.draw.rect(screen, (20, 27, 48), rect, border_radius=8)
            pygame.draw.rect(screen, self.accent, rect, 2, border_radius=8)
            self._text(screen, "ASDF"[i], self.fs, (180, 190, 220), 595)

        pygame.draw.line(screen, self.accent, (465, 530), (745, 530), 10)
        for note in self.rhythm_notes:
            x = lane_x[note["lane"]]
            pygame.draw.circle(screen, self.accent, (x, int(note["y"])), 18)
            pygame.draw.circle(screen, (245, 248, 255), (x, int(note["y"])), 7)

        self._text(screen, f"SCORE {self.rhythm_score} / {self.target_rhythm_score}", self.fs, self.accent, 220)
        self._text(screen, f"COMBO x{self.rhythm_combo}", self.fs, (255, 230, 120), 240)

    # -------------------------------------------------------------
    # DEFLECT, WASD RUN & SOLDER LOGIC
    # -------------------------------------------------------------
    def _update_deflect(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.shield_angle = math.atan2(my - self.center_pos[1], mx - self.center_pos[0])
        self.spawn_timer += dt
        if self.spawn_timer >= 0.5:
            self.spawn_timer = 0
            ang = random.uniform(0, math.pi * 2)
            self.debris_list.append({
                "x": self.center_pos[0] + math.cos(ang) * 230,
                "y": self.center_pos[1] + math.sin(ang) * 230,
                "ang": ang, "dist": 230
            })

        for debris in self.debris_list[:]:
            debris["dist"] -= 190 * dt
            debris["x"] = self.center_pos[0] + math.cos(debris["ang"]) * debris["dist"]
            debris["y"] = self.center_pos[1] + math.sin(debris["ang"]) * debris["dist"]

            if 55 <= debris["dist"] <= 85:
                diff = abs((debris["ang"] - self.shield_angle + math.pi) % (2 * math.pi) - math.pi)
                if diff <= 0.42:
                    self.debris_list.remove(debris)
                    self.blocked_count += 1
                    self.add_particles(debris["x"], debris["y"], self.accent, 10)
                    if self.blocked_count >= self.target_blocked:
                        self._finish()
            elif debris["dist"] < 25:
                self.debris_list.clear()
                self.screen_shake, self.jumpscare_flash = 0.6, 0.45

    def _update_wasd(self, dt):
        if self.key_cooldown > 0:
            self.key_cooldown = max(0, self.key_cooldown - dt)
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player_lane = max(0, self.player_lane - 1)
                self.key_cooldown = 0.1
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player_lane = min(2, self.player_lane + 1)
                self.key_cooldown = 0.1

        self.barrier_timer += dt
        if self.barrier_timer >= 0.55:
            self.barrier_timer = 0
            open_lane = random.choice([l for l in (0, 1, 2) if l != self.last_open_lane])
            self.last_open_lane = open_lane
            for lane in range(3):
                if lane != open_lane:
                    self.barriers.append({"lane": lane, "y": 250})

        for barrier in self.barriers[:]:
            barrier["y"] += 380 * dt
            if 500 <= barrier["y"] <= 540 and barrier["lane"] == self.player_lane:
                self.barriers.clear()
                self.screen_shake, self.jumpscare_flash = 0.6, 0.45
                self.dodged_count = max(0, self.dodged_count - 3)
                self.last_open_lane = -1
            elif barrier["y"] > 580:
                self.barriers.remove(barrier)
                self.dodged_count += 1
                if self.dodged_count >= self.target_dodged:
                    self._finish()
                    return

    def _update_solder(self, dt):
        self.glitch_timer += dt
        if self.glitch_timer >= 1.6:
            self.glitch_timer = 0
            if not self.is_soldering and len(self.glitch_tiles) > 4:
                old = random.choice(list(self.glitch_tiles))
                remaining = self.glitch_tiles - {old}
                options = [(r, c) for r in range(self.N) for c in range(1, self.N - 1) if (r, c) not in self.glitch_tiles]
                random.shuffle(options)
                for new in options:
                    candidate = remaining | {new}
                    if self._solder_has_path(candidate):
                        self.glitch_tiles = candidate
                        break

        if not self.is_soldering:
            return

        cell = self._cell(pygame.mouse.get_pos())
        if not cell:
            return

        if cell in self.glitch_tiles:
            self.is_soldering, self.solder_path = False, []
            self.screen_shake, self.jumpscare_flash = 0.6, 0.35
            self.solder_connections = max(0, self.solder_connections - 1)
            self.add_floating_text("SHORT CIRCUIT! -1", 640, 420, (255, 60, 90))
            return

        last = self.solder_path[-1]
        if cell != last:
            adjacent = abs(cell[0] - last[0]) + abs(cell[1] - last[1]) == 1
            if adjacent and cell not in self.solder_path:
                self.solder_path.append(cell)
                step = self.TILE + self.GAP
                x = self.grid.x + cell[1] * step + self.TILE // 2
                y = self.grid.y + cell[0] * step + self.TILE // 2
                self.add_particles(x, y, self.accent, 6)
                if cell[1] == 4:
                    self.is_soldering = False
                    self.solder_connections += 1
                    self.add_floating_text("LINK SECURED! +1", 640, 420, (120, 255, 180))
                    if self.solder_connections >= self.target_connections:
                        self._finish()
                    else:
                        self._reset_solder_board()

    # -------------------------------------------------------------
    # MAIN DRAW PIPELINE
    # -------------------------------------------------------------
    def draw(self, screen):
        if not self.active:
            return

        shake_x = random.uniform(-10, 10) if self.screen_shake > 0 else 0
        shake_y = random.uniform(-10, 10) if self.screen_shake > 0 else 0

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((5, 8, 22, 200))
        screen.blit(overlay, (0, 0))

        panel = self.panel.move(int(shake_x), int(shake_y))
        pygame.draw.rect(screen, self.accent, panel.inflate(14, 14), border_radius=24)
        pygame.draw.rect(screen, (12, 16, 35), panel, border_radius=20)
        pygame.draw.rect(screen, self.accent, panel, 2, border_radius=20)

        if self.jumpscare_flash > 0:
            flash = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            flash.fill((255, 0, 40, int(140 * self.jumpscare_flash / 0.45)))
            screen.blit(flash, (0, 0))

        if self.done:
            self._draw_done(screen)
            return

        self._text(screen, self.title, self.ft, self.accent, 124)
        self._text(screen, self.drink.upper(), self.fb, (242, 245, 255), 154)
        self._text(screen, f"{self.ingredient} • CYBERNETIC TRIAL", self.fs, (205, 212, 235), 180)

        self._draw_status_tracker(screen)

        drawers = {
            "DEFLECT": self._draw_deflect, "WASD_RUN": self._draw_wasd, "SOLDER": self._draw_solder,
            "NEON_DASH": self._draw_neon_dash, "AIM_RUSH": self._draw_aim_rush, "RHYTHM_RUSH": self._draw_rhythm_rush,
        }
        if self.level_mode in drawers:
            drawers[self.level_mode](screen)
        else:
            self._draw_board(screen)

        for p in self.particles:
            pygame.draw.circle(screen, p["color"], (int(p["x"] + shake_x), int(p["y"] + shake_y)), p["size"])

        for f in self.floating_texts:
            self._text(screen, f["text"], self.fs, f["color"], int(f["y"]))

        if self.level_mode not in ("DEFLECT", "WASD_RUN", "SOLDER", "NEON_DASH", "AIM_RUSH", "RHYTHM_RUSH"):
            seconds = max(0, int(self.time_left + 0.999))
            time_color = (255, 100, 120) if self.time_left <= 4 else self.accent
            self._text(screen, f"TIME  {seconds}s", self.fs, time_color, 682)

        if self.paused:
            pause = pygame.Surface(self.panel.size, pygame.SRCALPHA)
            pause.fill((5, 8, 22, 190))
            screen.blit(pause, self.panel.topleft)
            self._text(screen, "PAUSED", self.strike_big_font, self.accent, self.panel.centery)

        self._draw_challenge_controls(screen)
        if self.show_guide:
            self._draw_guide(screen)

    def _draw_challenge_controls(self, screen):
        mouse = pygame.mouse.get_pos()
        buttons = (
            (self.guide_button, "? GUIDE"),
            (self.pause_button, "RESUME" if self.paused else "PAUSE"),
            (self.exit_button, "EXIT")
        )
        for rect, label in buttons:
            hover = rect.collidepoint(mouse)
            fill = (45, 20, 50) if hover else (18, 24, 48)
            border = (255, 170, 210) if hover else self.accent
            pygame.draw.rect(screen, fill, rect, border_radius=7)
            pygame.draw.rect(screen, border, rect, 2, border_radius=7)
            text = self.fi.render(label, True, (248, 250, 255))
            screen.blit(text, text.get_rect(center=rect.center))

    # -------------------------------------------------------------
    # GUIDE & TUTORIAL OVERLAY
    # -------------------------------------------------------------
    def _draw_guide(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((4, 7, 18, 215))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(400, 220, 480, 270)
        pygame.draw.rect(screen, (8, 12, 28), box, border_radius=16)
        pygame.draw.rect(screen, self.accent, box, 2, border_radius=16)
        self._text(screen, "HOW TO PLAY", self.fb, self.accent, 260)

        if self.level_mode == "MATCH3":
            self._text(screen, "MATCH THE ICONS", self.ft, (245, 248, 255), 305)
            self._text(screen, "Swap adjacent icons and create 3 matches.", self.fs, (210, 218, 240), 350)
            self._text(screen, "♥ ♥ ♥  =  COMPLETE", self.fs, (255, 180, 205), 400)
        else:
            title, lines = GUIDE_DATA.get(self.level_mode, ("LEVEL GUIDE", ["Follow the on-screen instructions to complete the challenge."]))
            self._text(screen, title, self.ft, (245, 248, 255), 305)
            for idx, line in enumerate(lines):
                self._text(screen, line, self.fs, (210, 218, 240), 350 + idx * 34)

        button = pygame.Rect(565, 500, 150, 40)
        pygame.draw.rect(screen, (18, 24, 48), button, border_radius=8)
        pygame.draw.rect(screen, self.accent, button, 2, border_radius=8)
        self._text(screen, "GOT IT", self.fs, (248, 250, 255), 520)

    # -------------------------------------------------------------
    # MATCH-3 BOARD ENGINE
    # -------------------------------------------------------------
    def _new_board(self):
        for _ in range(500):
            board = [[None] * self.N for _ in range(self.N)]
            valid = True
            for r in range(self.N):
                for c in range(self.N):
                    choices = list(range(self.TYPES))
                    random.shuffle(choices)
                    picked = next((
                        val for val in choices
                        if not (c >= 2 and board[r][c - 1] == val and board[r][c - 2] == val)
                        and not (r >= 2 and board[r - 1][c] == val and board[r - 2][c] == val)
                    ), None)
                    if picked is None:
                        valid = False
                        break
                    board[r][c] = picked
                if not valid:
                    break
            if valid and self._has_move(board):
                return board
        return [
            [0, 1, 0, 2, 3],
            [4, 0, 1, 3, 2],
            [1, 2, 3, 4, 0],
            [2, 3, 4, 0, 1],
            [3, 4, 0, 1, 2],
        ]

    def _matches(self, board=None):
        board = self.board if board is None else board
        matches = set()
        for r in range(self.N):
            for c in range(self.N - 2):
                if board[r][c] is not None and board[r][c] == board[r][c + 1] == board[r][c + 2]:
                    matches.update((r, c + i) for i in range(3))
        for c in range(self.N):
            for r in range(self.N - 2):
                if board[r][c] is not None and board[r][c] == board[r + 1][c] == board[r + 2][c]:
                    matches.update((r + i, c) for i in range(3))
        return matches

    def _has_move(self, board):
        for r in range(self.N):
            for c in range(self.N):
                for dr, dc in ((0, 1), (1, 0)):
                    nr, nc = r + dr, c + dc
                    if nr < self.N and nc < self.N:
                        board[r][c], board[nr][nc] = board[nr][nc], board[r][c]
                        good = bool(self._matches(board))
                        board[r][c], board[nr][nc] = board[nr][nc], board[r][c]
                        if good:
                            return True
        return False

    def _swap(self, a, b):
        self.board[a[0]][a[1]], self.board[b[0]][b[1]] = self.board[b[0]][b[1]], self.board[a[0]][a[1]]

    def _resolve(self):
        matches = self._matches()
        if not matches:
            return False
        for r, c in matches:
            self.board[r][c] = None

        for c in range(self.N):
            values = [self.board[r][c] for r in range(self.N) if self.board[r][c] is not None]
            for r in range(self.N - 1, -1, -1):
                self.board[r][c] = values.pop() if values else None

        self._refill_board()

        self.strikes += 1
        if self.strikes >= self.TARGET_STRIKES:
            self._finish()
        return True

    def _refill_board(self):
        base_board = [row[:] for row in self.board]
        empty_cells = [
            (r, c)
            for r in range(self.N)
            for c in range(self.N)
            if base_board[r][c] is None
        ]

        for _ in range(100):
            board = [row[:] for row in base_board]
            filled = True
            for r, c in empty_cells:
                choices = list(range(self.TYPES))
                random.shuffle(choices)
                for value in choices:
                    board[r][c] = value
                    if not self._matches(board):
                        break
                else:
                    filled = False
                    break

            if filled and self._has_move(board):
                self.board = board
                return

        self.board = self._new_board()

    def _try_swap(self, a, b):
        self._swap(a, b)
        if self._matches():
            return self._resolve()
        self._swap(a, b)
        return False

    def _cell(self, pos):
        if not self.grid.collidepoint(pos):
            return None
        step = self.TILE + self.GAP
        c, r = (pos[0] - self.grid.x) // step, (pos[1] - self.grid.y) // step
        if 0 <= r < self.N and 0 <= c < self.N and (pos[0] - self.grid.x) % step < self.TILE and (pos[1] - self.grid.y) % step < self.TILE:
            return int(r), int(c)
        return None

    # -------------------------------------------------------------
    # STATUS & MODE-SPECIFIC RENDERERS
    # -------------------------------------------------------------
    def _draw_status_tracker(self, screen):
        y = 208
        if self.level_mode == "DEFLECT":
            self._text(screen, f"BLOCKED: {self.blocked_count} / TARGET {self.target_blocked}", self.strike_title_font, (210, 218, 240), y)
        elif self.level_mode == "WASD_RUN":
            self._text(screen, f"DODGED: {self.dodged_count} / TARGET {self.target_dodged}", self.strike_title_font, (210, 218, 240), y)
        elif self.level_mode == "SOLDER":
            self._text(screen, f"CIRCUITS LINKED: {self.solder_connections} / TARGET {self.target_connections}", self.strike_title_font, (210, 218, 240), y)
        elif self.level_mode == "MATCH3":
            hearts = "♥" * self.strikes + "♡" * (3 - self.strikes)
            self._text(screen, hearts, self.strike_big_font, (255, 170, 205), y)

    def _draw_board(self, screen):
        mouse = self._cell(pygame.mouse.get_pos())
        step = self.TILE + self.GAP
        for r in range(self.N):
            for c in range(self.N):
                rect = pygame.Rect(self.grid.x + c * step, self.grid.y + r * step, self.TILE, self.TILE)
                value = self.board[r][c]
                tile_color = self.colors[value % len(self.colors)]
                pygame.draw.rect(screen, (27, 32, 57), rect, border_radius=12)
                if mouse == (r, c):
                    pygame.draw.rect(screen, (100, 115, 155), rect.inflate(4, 4), 2, border_radius=14)
                if self.selected == (r, c):
                    pygame.draw.rect(screen, self.accent, rect.inflate(6, 6), 3, border_radius=15)
                pygame.draw.rect(screen, tile_color, rect.inflate(-8, -8), border_radius=14)
                self._icon(screen, rect.center, self.symbols[value % len(self.symbols)])

    def _draw_deflect(self, screen):
        cx, cy = self.center_pos
        pygame.draw.circle(screen, (40, 50, 80), (cx, cy), 70, 2)
        pygame.draw.circle(screen, self.accent, (cx, cy), 22)
        pygame.draw.arc(screen, (255, 255, 255), pygame.Rect(cx - 70, cy - 70, 140, 140), -self.shield_angle - 0.4, -self.shield_angle + 0.4, 7)
        for debris in self.debris_list:
            pygame.draw.circle(screen, (255, 80, 100), (int(debris["x"]), int(debris["y"])), 8)

    def _draw_wasd(self, screen):
        lanes = [540, 640, 740]
        for x in lanes:
            pygame.draw.line(screen, (40, 50, 80), (x, 250), (x, 560), 2)
        pygame.draw.circle(screen, self.accent, (lanes[self.player_lane], 520), 16)
        for barrier in self.barriers:
            pygame.draw.rect(screen, (255, 60, 90), (lanes[barrier["lane"]] - 30, int(barrier["y"]), 60, 12), border_radius=4)

    def _draw_solder(self, screen):
        step = self.TILE + self.GAP
        for r in range(self.N):
            for c in range(self.N):
                rect = pygame.Rect(self.grid.x + c * step, self.grid.y + r * step, self.TILE, self.TILE)
                glitch = (r, c) in self.glitch_tiles
                color = (230, 40, 75) if glitch else (50, 190, 120) if c == 0 else (80, 150, 255) if c == 4 else (25, 34, 60)
                pygame.draw.rect(screen, color, rect, border_radius=10)
                pygame.draw.rect(screen, (55, 70, 110), rect, 2, border_radius=10)
                label = "X" if glitch else "IN" if c == 0 else "OUT" if c == 4 else None
                if label:
                    font = self.fb if glitch else self.fs
                    label_img = font.render(label, True, (255, 255, 255))
                    screen.blit(label_img, label_img.get_rect(center=rect.center))

        if len(self.solder_path) > 1:
            points = [(self.grid.x + c * step + self.TILE // 2, self.grid.y + r * step + self.TILE // 2) for r, c in self.solder_path]
            pygame.draw.lines(screen, (255, 255, 255), False, points, 8)
            pygame.draw.lines(screen, self.accent, False, points, 4)

    # -------------------------------------------------------------
    # FINISH, FAIL & HELPER UTILITIES
    # -------------------------------------------------------------
    def _finish(self):
        self.done, self.selected, self.show_guide, self.done_timer = True, None, False, 1.2

    def _fail(self):
        self.failed, self.selected, self.show_guide = True, None, False

    def _exit_challenge(self):
        self.active = self.done = self.failed = self.paused = self.show_guide = False
        self.selected = None
        self.particles.clear()
        self.floating_texts.clear()

    def _text(self, screen, text, font, color, y):
        surface = font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=(640, y)))

    # -------------------------------------------------------------
    # INGREDIENT ICONS & CUTE FACES
    # -------------------------------------------------------------
    def _icon(self, s, center, kind):
        x, y = center
        ink, cream = (68, 76, 98), (255, 252, 246)

        if kind == "milk":
            pygame.draw.polygon(s, ink, [(x - 10, y - 8), (x - 3, y - 14), (x + 9, y - 10), (x + 10, y + 11), (x - 10, y + 11)])
            pygame.draw.polygon(s, (246, 253, 255), [(x - 8, y - 7), (x - 2, y - 11), (x + 7, y - 8), (x + 8, y + 9), (x - 8, y + 9)])
            pygame.draw.polygon(s, (151, 216, 235), [(x - 2, y - 10), (x + 7, y - 7), (x + 7, y - 2), (x - 2, y - 4)])
            self._cute_face(s, x, y + 3)

        elif kind == "coffee":
            pygame.draw.ellipse(s, ink, (x - 12, y + 7, 24, 7))
            pygame.draw.circle(s, ink, (x + 9, y - 1), 7)
            pygame.draw.circle(s, cream, (x + 9, y - 1), 3)
            pygame.draw.rect(s, ink, (x - 12, y - 9, 21, 19), border_radius=6)
            pygame.draw.rect(s, (194, 123, 85), (x - 10, y - 7, 17, 14), border_radius=5)
            pygame.draw.ellipse(s, (104, 62, 50), (x - 10, y - 8, 17, 7))
            self._cute_face(s, x - 1, y + 1)

        elif kind == "syrup":
            pygame.draw.rect(s, ink, (x - 4, y - 13, 8, 6), border_radius=2)
            pygame.draw.rect(s, (244, 184, 207), (x - 3, y - 12, 6, 4), border_radius=2)
            pygame.draw.rect(s, ink, (x - 10, y - 7, 20, 20), border_radius=5)
            pygame.draw.rect(s, (255, 239, 245), (x - 8, y - 5, 16, 16), border_radius=4)
            pygame.draw.rect(s, (244, 139, 183), (x - 7, y + 3, 14, 6), border_radius=3)
            self._cute_face(s, x, y + 1)

        elif kind in ("spice", "matcha"):
            powder = (198, 119, 78) if kind == "spice" else (139, 190, 111)
            pygame.draw.ellipse(s, ink, (x - 12, y - 8, 24, 21))
            pygame.draw.ellipse(s, (255, 239, 221), (x - 10, y - 7, 20, 16))
            pygame.draw.ellipse(s, powder, (x - 9, y - 8, 18, 10))
            pygame.draw.circle(s, (255, 229, 159), (x - 4, y - 8), 3)
            self._cute_face(s, x, y + 1)

        elif kind == "star":
            pts = [(x + math.cos(-math.pi / 2 + i * math.pi / 2.5) * 14, y + math.sin(-math.pi / 2 + i * math.pi / 2.5) * 14) for i in range(5)]
            pygame.draw.polygon(s, ink, pts)
            pts_inner = [(x + math.cos(-math.pi / 2 + i * math.pi / 2.5) * 11, y + math.sin(-math.pi / 2 + i * math.pi / 2.5) * 11) for i in range(5)]
            pygame.draw.polygon(s, (255, 222, 105), pts_inner)
            self._cute_face(s, x, y + 2)

        elif kind == "ice":
            pygame.draw.rect(s, ink, (x - 11, y - 11, 22, 22), border_radius=7)
            pygame.draw.rect(s, (202, 238, 250), (x - 9, y - 9, 18, 18), border_radius=6)
            pygame.draw.line(s, (246, 255, 255), (x - 5, y - 6), (x - 2, y - 3), 2)
            self._cute_face(s, x, y + 2)

        elif kind == "foam":
            for cx, cy, r in ((x - 5, y + 1, 8), (x + 4, y - 2, 10), (x + 10, y + 3, 6)):
                pygame.draw.circle(s, ink, (cx, cy), r)
            for cx, cy, r in ((x - 5, y + 1, 6), (x + 4, y - 2, 8), (x + 10, y + 3, 4)):
                pygame.draw.circle(s, cream, (cx, cy), r)
            self._cute_face(s, x + 2, y + 3)

        elif kind == "chocolate":
            pygame.draw.rect(s, ink, (x - 12, y - 10, 24, 20), border_radius=4)
            pygame.draw.rect(s, (132, 78, 61), (x - 10, y - 8, 20, 16), border_radius=3)
            pygame.draw.line(s, (194, 130, 101), (x, y - 7), (x, y + 7), 2)
            pygame.draw.line(s, (194, 130, 101), (x - 8, y), (x + 8, y), 2)
            self._cute_face(s, x, y + 1)

        else:
            pygame.draw.ellipse(s, (164, 214, 139), (x - 11, y - 7, 22, 15))
            pygame.draw.line(s, (81, 145, 98), (x - 8, y + 8), (x + 8, y - 8), 2)
            self._cute_face(s, x, y + 2)

    def _cute_face(self, s, x, y):
        eye = (68, 76, 98)
        pygame.draw.circle(s, eye, (x - 3, y - 1), 1)
        pygame.draw.circle(s, eye, (x + 3, y - 1), 1)
        pygame.draw.lines(s, eye, False, [(x - 2, y + 3), (x, y + 4), (x + 2, y + 3)], 1)
        pygame.draw.circle(s, (255, 164, 177), (x - 6, y + 2), 1)
        pygame.draw.circle(s, (255, 164, 177), (x + 6, y + 2), 1)

    def _draw_done(self, screen):
        self._text(screen, "INGREDIENT READY!", self.fd, self.accent, 255)
        self._text(screen, f"{self.ingredient} successfully calibrated.", self.fb, (235, 240, 255), 300)
        self._text(screen, "Returning to Mixing Station...", self.fs, (145, 155, 185), 450)
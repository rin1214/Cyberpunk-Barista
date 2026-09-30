"""
mini_challenges.py
Cyberpunk Café - Mini Challenges (Modern Cyberpunk Arcade Edition v5)
"""

import math
import random
import pygame

CHALLENGES = {
    "Neon Latte": {
        "title": "MILK MATCH OVERDRIVE",
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
        "title": "STARDUST HYPER MATCH",
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
        "title": "QUANTUM SPICE MATCH",
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
        "title": "DEFLECTION FIELD V2",
        "ingredient": "METEORITE DUST",
        "accent": (255, 90, 120),
    },
    "Hologram Frappe": {
        "title": "OVERDRIVE LASER THREAD",
        "ingredient": "STARDUST MATCHA",
        "accent": (140, 255, 120),
    },
    "Pixel Lemint": {
        "title": "QUANTUM SOLDER OVERDRIVE",
        "ingredient": "CARAMEL BYTE",
        "accent": (255, 180, 60),
    },
    "Meteorite": {
        "title": "NEON DASH EXTREME",
        "ingredient": "METEORITE CORE",
        "accent": (255, 90, 120),
    },
    "Stardust Matcha": {
        "title": "HYPER FLICK AIM ARENA",
        "ingredient": "STARDUST MATCHA",
        "accent": (140, 255, 120),
    },
    "Caramel Byte": {
        "title": "RHYTHM BLITZ",
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
        self.strike_title_font = pygame.font.SysFont("arial", 16, True)
        self.strike_big_font = pygame.font.SysFont("arial", 36, True)
        self.timer_ring_font = pygame.font.SysFont("arial", 16, True)

        self.active = False
        self.done = False
        self.failed = False
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
        self.particles = []
        self.floating_texts = []
        self.screen_shake = 0.0
        self.jumpscare_flash = 0.0

        self.level_mode = "MATCH3"
        self.center_pos = (640, 430)

        # Deflect
        self.shield_angle = 0
        self.debris_list = []
        self.spawn_timer = 0
        self.blocked_count = 0
        self.target_blocked = 12

        # WASD Run
        self.player_lane = 1
        self.barriers = []
        self.barrier_timer = 0
        self.key_cooldown = 0.0
        self.dodged_count = 0
        self.target_dodged = 14
        self.last_open_lane = -1

        # Solder (Enhanced Level 3)
        self.is_soldering = False
        self.solder_path = []
        self.glitch_tiles = set()
        self.solder_connections = 0
        self.target_connections = 5
        self.glitch_timer = 0.0
        self.pulse_phase = 0.0

        # Neon Dash
        self.dash_player_y = 535.0
        self.dash_velocity = 0.0
        self.dash_on_ground = True
        self.dash_obstacles = []
        self.dash_spawn_timer = 0.0
        self.dash_speed = 340.0
        self.dash_score = 0
        self.dash_combo = 0
        self.target_dash_score = 1200

        # Aim Rush
        self.aim_targets = []
        self.aim_targets_left = 20
        self.aim_combo = 0
        self.aim_score = 0
        self.aim_best_combo = 0
        self.aim_spawn_timer = 0.0
        self.target_aim_score = 2200

        # Rhythm Rush
        self.rhythm_notes = []
        self.rhythm_spawn_timer = 0.0
        self.rhythm_hit_count = 0
        self.rhythm_combo = 0
        self.rhythm_score = 0
        self.rhythm_speed = 320.0
        self.target_rhythm_score = 2500

    def add_particles(self, x, y, color, count=12, speed_mult=1.0):
        for _ in range(count):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(25, 130) * speed_mult
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(ang) * spd,
                    "vy": math.sin(ang) * spd,
                    "life": random.uniform(0.3, 0.6),
                    "max_life": 0.6,
                    "color": color,
                    "size": random.randint(2, 5),
                }
            )

    def add_floating_text(self, text, x, y, color=(255, 230, 100)):
        self.floating_texts.append(
            {"text": text, "x": x, "y": y, "vy": -50.0, "life": 0.5, "color": color}
        )

    def start_challenge(self, drink_name):
        self.drink = drink_name
        d = CHALLENGES.get(drink_name, CHALLENGES["Neon Latte"])
        self.title = d.get("title", "INGREDIENT MATCH")
        self.ingredient = d.get("ingredient", "INGREDIENT")
        self.accent = d.get("accent", (120, 235, 255))
        self.colors = d.get("tile_colors", self.colors)
        self.symbols = d.get("symbols", self.symbols)

        self.active = True
        self.done = False
        self.failed = False
        self.selected = None
        self.strikes = 0
        self.message_timer = 0
        self.done_timer = 0
        self.particles.clear()
        self.floating_texts.clear()
        self.screen_shake = 0.0
        self.jumpscare_flash = 0.0

        if drink_name == "Cyber Fuel":
            self.level_mode = "DEFLECT"
            self.time_left = 16.0
            self.blocked_count = 0
            self.message = ""
            self.debris_list, self.spawn_timer = [], 0
        elif drink_name == "Hologram Frappe":
            self.level_mode = "WASD_RUN"
            self.time_left = 16.0
            self.dodged_count = 0
            self.message = ""
            self.player_lane, self.barriers, self.barrier_timer = 1, [], 0
            self.key_cooldown, self.last_open_lane = 0.0, -1
        elif drink_name == "Pixel Lemint":
            self.level_mode = "SOLDER"
            self.time_left = 22.0
            self.message = ""
            self.solder_connections = 0
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
            self.level_mode = "MATCH3"
            self.time_left = 20.0
            self.message = ""
            self.board = self._new_board()

    def _reset_solder_board(self):
        self.solder_path, self.is_soldering = [], False
        # Create shifting hazard nodes across the grid
        self.glitch_tiles = {
            (random.randint(0, 4), random.randint(1, 3)) for _ in range(10)
        }
        self.glitch_timer = 0.0

    def handle_event(self, event):
        if not self.active or self.done or self.failed:
            return

        if self.level_mode == "WASD_RUN" and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.player_lane = max(0, self.player_lane - 1)
                self.key_cooldown = 0.08
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.player_lane = min(2, self.player_lane + 1)
                self.key_cooldown = 0.08

        elif self.level_mode == "NEON_DASH":
            if (
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP)
            ) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                if self.dash_on_ground:
                    self.dash_velocity = -580.0
                    self.dash_on_ground = False
                    self.add_particles(450, 535, self.accent, 10)

        elif (
            self.level_mode == "AIM_RUSH"
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            mx, my = event.pos
            hit_any = False
            for t in self.aim_targets[:]:
                if math.hypot(mx - t["x"], my - t["y"]) <= t["r"]:
                    hit_any = True
                    if t["is_bomb"]:
                        self.aim_combo = 0
                        self.screen_shake = 0.6
                        self.jumpscare_flash = 0.45
                        self.aim_score = max(0, self.aim_score - 200)
                        self.add_particles(mx, my, (255, 20, 40), 30, 2.0)
                        self.add_floating_text(
                            "⚠️️ BREACH! -200", mx, my - 20, (255, 50, 50)
                        )
                    else:
                        self.aim_targets_left -= 1
                        self.aim_combo += 1
                        self.aim_best_combo = max(
                            self.aim_best_combo, self.aim_combo
                        )
                        bonus = 150 + self.aim_combo * 35
                        self.aim_score += bonus
                        self.screen_shake = 0.12
                        self.add_particles(mx, my, self.accent, 16)
                        self.add_floating_text(
                            f"+{bonus}", mx, my, (150, 255, 180)
                        )
                    self.aim_targets.remove(t)
                    break

            if not hit_any:
                self.aim_combo = 0
                self.screen_shake = 0.15
                self.aim_score = max(0, self.aim_score - 50)

        elif self.level_mode == "RHYTHM_RUSH":
            if event.type == pygame.KEYDOWN:
                lane_keys = {
                    pygame.K_a: 0,
                    pygame.K_s: 1,
                    pygame.K_d: 2,
                    pygame.K_f: 3,
                }
                if event.key in lane_keys:
                    self._rhythm_press(lane_keys[event.key])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._rhythm_press(
                    max(0, min(3, int((event.pos[0] - 500) / 70)))
                )

        elif self.level_mode == "SOLDER":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = self._cell(event.pos)
                if cell and cell[1] == 0 and cell not in self.glitch_tiles:
                    self.is_soldering, self.solder_path = True, [cell]
                    self.add_particles(event.pos[0], event.pos[1], self.accent, 8)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_soldering:
                    # Released midway without reaching column 4 -> snap fail/penalty
                    self.is_soldering, self.solder_path = False, []
                    self.screen_shake = 0.3
                    self.add_floating_text("CIRCUIT BROKEN!", 640, 400, (255, 100, 100))

        elif (
            self.level_mode == "MATCH3"
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            cell = self._cell(event.pos)
            if not cell:
                return
            if not self.selected:
                self.selected = cell
            elif cell == self.selected:
                self.selected = None
            else:
                a, self.selected = self.selected, None
                if abs(a[0] - cell[0]) + abs(a[1] - cell[1]) == 1:
                    self._try_swap(a, cell)
                else:
                    self.selected = cell

    def update(self, dt):
        if not self.active:
            return False

        if self.failed:
            self.active = False
            self.failed = False
            return False

        if self.done:
            self.done_timer -= dt
            if self.done_timer <= 0:
                self.active = False
                self.done = False
                return True
            return False

        self.pulse += dt
        self.pulse_phase += dt * 6.0
        self.message_timer = max(0, self.message_timer - dt)
        self.screen_shake = max(0.0, self.screen_shake - dt)
        self.jumpscare_flash = max(0.0, self.jumpscare_flash - dt)

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        for ft in self.floating_texts[:]:
            ft["y"] += ft["vy"] * dt
            ft["life"] -= dt
            if ft["life"] <= 0:
                self.floating_texts.remove(ft)

        self.time_left = max(0, self.time_left - dt)

        if self.time_left <= 0:
            self._check_win_condition()

        if self.level_mode == "DEFLECT":
            self._update_deflect(dt)
        elif self.level_mode == "WASD_RUN":
            self._update_wasd(dt)
        elif self.level_mode == "SOLDER":
            self._update_solder(dt)
        elif self.level_mode == "NEON_DASH":
            self._update_neon_dash(dt)
        elif self.level_mode == "AIM_RUSH":
            self._update_aim_rush(dt)
        elif self.level_mode == "RHYTHM_RUSH":
            self._update_rhythm_rush(dt)

        return False

    def _check_win_condition(self):
        passed = False
        if self.level_mode == "DEFLECT":
            passed = self.blocked_count >= self.target_blocked
        elif self.level_mode == "WASD_RUN":
            passed = self.dodged_count >= self.target_dodged
        elif self.level_mode == "SOLDER":
            passed = self.solder_connections >= self.target_connections
        elif self.level_mode == "NEON_DASH":
            passed = self.dash_score >= self.target_dash_score
        elif self.level_mode == "AIM_RUSH":
            passed = self.aim_score >= self.target_aim_score
        elif self.level_mode == "RHYTHM_RUSH":
            passed = self.rhythm_score >= self.target_rhythm_score
        elif self.level_mode == "MATCH3":
            passed = self.strikes >= self.TARGET_STRIKES

        if passed:
            self._finish()
        else:
            self._fail()

    def _start_neon_dash(self):
        self.time_left = 18.0
        self.dash_player_y, self.dash_velocity, self.dash_on_ground = (
            535.0,
            0.0,
            True,
        )
        self.dash_obstacles, self.dash_spawn_timer, self.dash_speed = (
            [],
            0.5,
            360.0,
        )
        self.dash_score, self.dash_combo = 0, 0
        self.message = ""

    def _update_neon_dash(self, dt):
        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        ) and self.dash_on_ground:
            self.dash_velocity = -580.0
            self.dash_on_ground = False
            self.add_particles(450, 535, self.accent, 10)

        ground_y = 535.0
        self.dash_velocity += 1400.0 * dt
        self.dash_player_y += self.dash_velocity * dt
        if self.dash_player_y >= ground_y:
            self.dash_player_y, self.dash_velocity, self.dash_on_ground = (
                ground_y,
                0.0,
                True,
            )

        self.dash_spawn_timer -= dt
        if self.dash_spawn_timer <= 0:
            self.dash_spawn_timer = random.uniform(0.6, 1.0)
            kind = random.choice(["spike", "spike", "double", "floating_drone"])
            w = 34 if kind == "spike" else (68 if kind == "double" else 45)
            h = 42 if kind != "floating_drone" else 35
            y_offset = ground_y if kind != "floating_drone" else ground_y - 75
            self.dash_obstacles.append(
                {
                    "x": 1040.0,
                    "y": y_offset,
                    "kind": kind,
                    "w": w,
                    "h": h,
                    "passed": False,
                }
            )

        for ob in self.dash_obstacles[:]:
            ob["x"] -= self.dash_speed * dt
            if not ob["passed"] and ob["x"] + ob["w"] < 450:
                ob["passed"] = True
                self.dash_score += 140 + self.dash_combo * 20
                self.dash_combo += 1
                self.dash_speed = min(540.0, self.dash_speed + 10.0)

            ox, oy, ow, oh = ob["x"], ob["y"] - ob["h"], ob["w"], ob["h"]
            player_rect = pygame.Rect(432, int(self.dash_player_y - 36), 36, 36)
            obs_rect = pygame.Rect(int(ox), int(oy), ow, oh)
            if player_rect.colliderect(obs_rect):
                self.dash_combo = 0
                self.screen_shake = 0.55
                self.jumpscare_flash = 0.4
                self.dash_score = max(0, self.dash_score - 180)
                self.dash_speed = max(360.0, self.dash_speed - 50.0)
                self.add_particles(450, int(self.dash_player_y), (255, 40, 60), 20)
                self.dash_obstacles.remove(ob)
                continue
            if ob["x"] < 300:
                self.dash_obstacles.remove(ob)

    def _draw_neon_dash(self, screen):
        ground_y = 535
        for x in range(360, 950, 70):
            pygame.draw.line(screen, (35, 48, 75), (x, ground_y), (x + 35, 590), 2)
        pygame.draw.line(screen, self.accent, (340, ground_y), (960, ground_y), 3)
        pygame.draw.circle(
            screen, self.accent, (450, int(self.dash_player_y - 18)), 18
        )
        pygame.draw.rect(
            screen,
            (30, 40, 65),
            (428, int(self.dash_player_y - 3), 44, 8),
            border_radius=4,
        )
        for ob in self.dash_obstacles:
            x, y, w, h = int(ob["x"]), int(ob["y"]), ob["w"], ob["h"]
            if ob["kind"] in ("spike", "double"):
                count = 1 if ob["kind"] == "spike" else 2
                sw = w / count
                for i in range(count):
                    pygame.draw.polygon(
                        screen,
                        (255, 75, 105),
                        [
                            (x + i * sw, ground_y),
                            (x + (i + 0.5) * sw, ground_y - h),
                            (x + (i + 1) * sw, ground_y),
                        ],
                    )
            else:
                pygame.draw.rect(
                    screen,
                    (255, 140, 60),
                    (x, y - h, w, h),
                    border_radius=6,
                )
        self._text(screen, f"SCORE {self.dash_score} / TARGET {self.target_dash_score}", self.fs, self.accent, 300)
        self._text(
            screen, f"COMBO x{self.dash_combo}", self.fs, (255, 230, 120), 325
        )

    def _start_aim_rush(self):
        self.time_left, self.aim_targets_left, self.aim_combo, self.aim_score, self.aim_best_combo = (
            20.0,
            20,
            0,
            0,
            0,
        )
        self.aim_targets = []
        self.aim_spawn_timer = 0.0

    def _update_aim_rush(self, dt):
        self.aim_spawn_timer -= dt
        if self.aim_spawn_timer <= 0 and len(self.aim_targets) < 5:
            self.aim_spawn_timer = random.uniform(0.3, 0.55)
            is_bomb = random.random() < 0.32
            r = random.randint(22, 30)
            self.aim_targets.append(
                {
                    "x": random.randint(400, 880),
                    "y": random.randint(310, 530),
                    "r": r,
                    "is_bomb": is_bomb,
                    "vx": random.uniform(-70, 70),
                    "vy": random.uniform(-70, 70),
                    "life": random.uniform(1.4, 2.5),
                }
            )

        for t in self.aim_targets[:]:
            t["x"] += t["vx"] * dt
            t["y"] += t["vy"] * dt
            if t["x"] < 380 or t["x"] > 900:
                t["vx"] *= -1
            if t["y"] < 290 or t["y"] > 560:
                t["vy"] *= -1
            t["life"] -= dt
            if t["life"] <= 0:
                self.aim_targets.remove(t)
                if not t["is_bomb"]:
                    self.aim_combo = 0

    def _draw_aim_rush(self, screen):
        pygame.draw.rect(
            screen, (15, 20, 38), (360, 275, 560, 310), border_radius=14
        )
        pygame.draw.rect(
            screen, self.accent, (360, 275, 560, 310), 2, border_radius=14
        )

        for t in self.aim_targets:
            x, y, r = int(t["x"]), int(t["y"]), int(t["r"])
            col = (255, 60, 90) if t["is_bomb"] else self.accent
            pygame.draw.circle(
                screen, (col[0] // 3, col[1] // 3, col[2] // 3), (x, y), r + 6
            )
            pygame.draw.circle(screen, col, (x, y), r)
            pygame.draw.circle(
                screen, (245, 248, 255), (x, y), max(3, r // 3)
            )
            if t["is_bomb"]:
                self._text(screen, "X", self.fs, (255, 255, 255), y)

        self._text(
            screen, f"SCORE {self.aim_score} / TARGET {self.target_aim_score}", self.fs, self.accent, 300
        )
        self._text(
            screen, f"COMBO x{self.aim_combo}", self.fs, (255, 230, 120), 325
        )

    def _start_rhythm_rush(self):
        self.time_left, self.rhythm_notes, self.rhythm_spawn_timer = (
            22.0,
            [],
            0.2,
        )
        self.rhythm_hit_count, self.rhythm_combo, self.rhythm_score, self.rhythm_speed = (
            0,
            0,
            0,
            340.0,
        )

    def _rhythm_press(self, lane):
        candidates = [
            n for n in self.rhythm_notes if n["lane"] == lane and not n["hit"]
        ]
        if (
            not candidates
            or abs(min(candidates, key=lambda n: abs(n["y"] - 530))["y"] - 530)
            > 75
        ):
            self.rhythm_combo, self.screen_shake, self.rhythm_score = (
                0,
                0.2,
                max(0, self.rhythm_score - 100),
            )
            return
        note = min(candidates, key=lambda n: abs(n["y"] - 530))
        diff = abs(note["y"] - 530)
        grade, points = (
            ("PERFECT!", 400)
            if diff <= 15
            else (("GOOD", 250) if diff <= 38 else ("OK", 120))
        )
        note["hit"] = True
        self.rhythm_hit_count += 1
        self.rhythm_combo += 1
        self.rhythm_score += points + self.rhythm_combo * 20
        self.rhythm_speed = min(480.0, self.rhythm_speed + 6.0)
        self.screen_shake = 0.08
        lane_x = [500, 570, 640, 710]
        self.add_particles(lane_x[lane], 530, self.accent, 12)
        self.add_floating_text(grade, lane_x[lane], 500, (255, 230, 100))

    def _update_rhythm_rush(self, dt):
        self.rhythm_spawn_timer -= dt
        if self.rhythm_spawn_timer <= 0:
            self.rhythm_spawn_timer = max(0.24, 0.5 - self.rhythm_hit_count * 0.008)
            self.rhythm_notes.append(
                {"lane": random.randrange(4), "y": 275.0, "hit": False}
            )
        for note in self.rhythm_notes[:]:
            note["y"] += self.rhythm_speed * dt
            if note["y"] > 585 and not note["hit"]:
                self.rhythm_notes.remove(note)
                self.rhythm_combo, self.screen_shake, self.rhythm_score = (
                    0,
                    0.25,
                    max(0, self.rhythm_score - 80),
                )
            elif note.get("hit"):
                self.rhythm_notes.remove(note)

    def _draw_rhythm_rush(self, screen):
        lane_x = [500, 570, 640, 710]
        for i, x in enumerate(lane_x):
            pygame.draw.rect(
                screen, (20, 27, 48), (x - 29, 275, 58, 305), border_radius=8
            )
            pygame.draw.rect(
                screen, self.accent, (x - 29, 275, 58, 305), 2, border_radius=8
            )
            self._text(screen, "ASDF"[i], self.fs, (180, 190, 220), 595)
        pygame.draw.line(screen, self.accent, (465, 530), (745, 530), 5)
        for note in self.rhythm_notes:
            x = lane_x[note["lane"]]
            pygame.draw.circle(screen, self.accent, (x, int(note["y"])), 18)
            pygame.draw.circle(
                screen, (245, 248, 255), (x, int(note["y"])), 7
            )
        self._text(
            screen,
            f"SCORE {self.rhythm_score} / TARGET {self.target_rhythm_score}",
            self.fs,
            self.accent,
            300,
        )
        self._text(
            screen, f"COMBO x{self.rhythm_combo}", self.fs, (255, 230, 120), 325
        )

    def _update_deflect(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.shield_angle = math.atan2(
            my - self.center_pos[1], mx - self.center_pos[0]
        )
        self.spawn_timer += dt
        if self.spawn_timer >= 0.5:
            self.spawn_timer = 0
            ang = random.uniform(0, math.pi * 2)
            self.debris_list.append(
                {
                    "x": self.center_pos[0] + math.cos(ang) * 230,
                    "y": self.center_pos[1] + math.sin(ang) * 230,
                    "ang": ang,
                    "dist": 230,
                }
            )

        for deb in self.debris_list[:]:
            deb["dist"] -= 190 * dt
            deb["x"] = self.center_pos[0] + math.cos(deb["ang"]) * deb["dist"]
            deb["y"] = self.center_pos[1] + math.sin(deb["ang"]) * deb["dist"]
            if 55 <= deb["dist"] <= 85:
                if (
                    abs(
                        (deb["ang"] - self.shield_angle + math.pi)
                        % (2 * math.pi)
                        - math.pi
                    )
                    <= 0.42
                ):
                    self.debris_list.remove(deb)
                    self.blocked_count += 1
                    self.screen_shake = 0.08
                    self.add_particles(deb["x"], deb["y"], self.accent, 10)
            elif deb["dist"] < 25:
                self.debris_list.clear()
                self.screen_shake = 0.6
                self.jumpscare_flash = 0.45
                self.blocked_count = max(0, self.blocked_count - 3)

    def _update_wasd(self, dt):
        if self.key_cooldown > 0:
            self.key_cooldown = max(0.0, self.key_cooldown - dt)
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player_lane, self.key_cooldown = (
                    max(0, self.player_lane - 1),
                    0.1,
                )
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player_lane, self.key_cooldown = (
                    min(2, self.player_lane + 1),
                    0.1,
                )

        self.barrier_timer += dt
        if self.barrier_timer >= 0.55:
            self.barrier_timer = 0
            open_lane = random.choice(
                [l for l in [0, 1, 2] if l != self.last_open_lane]
            )
            self.last_open_lane = open_lane
            for l in range(3):
                if l != open_lane:
                    self.barriers.append({"lane": l, "y": 250})

        lanes_x = [540, 640, 740]
        for b in self.barriers[:]:
            b["y"] += 380 * dt
            if 500 <= b["y"] <= 540 and b["lane"] == self.player_lane:
                self.barriers.clear()
                self.screen_shake = 0.6
                self.jumpscare_flash = 0.45
                self.dodged_count = max(0, self.dodged_count - 3)
                self.last_open_lane = -1
            elif b["y"] > 580:
                self.barriers.remove(b)
                self.dodged_count += 1

    def _update_solder(self, dt):
        # Dynamic Glitch Hazard Shifts
        self.glitch_timer += dt
        if self.glitch_timer >= 1.6:
            self.glitch_timer = 0.0
            if not self.is_soldering and len(self.glitch_tiles) > 4:
                # Randomly mutate one glitch tile to keep player on toes
                to_remove = random.choice(list(self.glitch_tiles))
                self.glitch_tiles.remove(to_remove)
                new_tile = (random.randint(0, 4), random.randint(1, 3))
                self.glitch_tiles.add(new_tile)

        if not self.is_soldering:
            return
        
        cell = self._cell(pygame.mouse.get_pos())
        if not cell:
            return
            
        if cell in self.glitch_tiles:
            # Hit corruption trap! Break trace and penalize
            self.is_soldering, self.solder_path = False, []
            self.screen_shake = 0.6
            self.jumpscare_flash = 0.35
            self.solder_connections = max(0, self.solder_connections - 1)
            self.add_floating_text("⚡ SHORT CIRCUIT! -1", 640, 420, (255, 60, 90))
            return
            
        last = self.solder_path[-1]
        if cell != last:
            # Enforce continuous adjacent step tracing
            if abs(cell[0] - last[0]) + abs(cell[1] - last[1]) == 1:
                if cell not in self.solder_path:
                    self.solder_path.append(cell)
                    self.add_particles(
                        self.grid.x + cell[1] * (self.TILE + self.GAP) + self.TILE // 2,
                        self.grid.y + cell[0] * (self.TILE + self.GAP) + self.TILE // 2,
                        self.accent, 6
                    )
                    # Successful completion when hitting the right power terminal column (c == 4)
                    if cell[1] == 4:
                        self.is_soldering = False
                        self.solder_connections += 1
                        self.screen_shake = 0.15
                        self.add_floating_text(f"LINK SECURED! +1", 640, 420, (120, 255, 180))
                        if self.solder_connections >= self.target_connections:
                            self._finish()
                        else:
                            self._reset_solder_board()

    def draw(self, screen):
        if not self.active:
            return

        shake_x = random.uniform(-10, 10) if self.screen_shake > 0 else 0
        shake_y = random.uniform(-10, 10) if self.screen_shake > 0 else 0

        ov = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        ov.fill((5, 8, 22, 200))
        screen.blit(ov, (0, 0))

        panel_shaken = self.panel.move(int(shake_x), int(shake_y))
        pygame.draw.rect(
            screen, self.accent, panel_shaken.inflate(14, 14), border_radius=24
        )
        pygame.draw.rect(
            screen, (12, 16, 35), panel_shaken, border_radius=20
        )
        pygame.draw.rect(screen, self.accent, panel_shaken, 2, border_radius=20)

        if self.jumpscare_flash > 0:
            flash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            flash_surf.fill((255, 0, 40, int(140 * (self.jumpscare_flash / 0.45))))
            screen.blit(flash_surf, (0, 0))

        if self.done:
            self._draw_done(screen)
            return

        self._text(screen, self.title, self.ft, self.accent, 124)
        self._text(screen, self.drink.upper(), self.fb, (242, 245, 255), 154)
        self._text(
            screen,
            f"{self.ingredient} • CYBERNETIC TRIAL",
            self.fs,
            (205, 212, 235),
            180,
        )

        self._draw_status_tracker(screen)

        if self.level_mode == "DEFLECT":
            self._draw_deflect(screen)
        elif self.level_mode == "WASD_RUN":
            self._draw_wasd(screen)
        elif self.level_mode == "SOLDER":
            self._draw_solder(screen)
        elif self.level_mode == "NEON_DASH":
            self._draw_neon_dash(screen)
        elif self.level_mode == "AIM_RUSH":
            self._draw_aim_rush(screen)
        elif self.level_mode == "RHYTHM_RUSH":
            self._draw_rhythm_rush(screen)
        else:
            self._draw_board(screen)

        for p in self.particles:
            pygame.draw.circle(
                screen,
                p["color"],
                (int(p["x"] + shake_x), int(p["y"] + shake_y)),
                p["size"],
            )
        for ft in self.floating_texts:
            self._text(
                screen, ft["text"], self.fs, ft["color"], int(ft["y"])
            )

        sec = max(0, int(self.time_left + 0.999))
        self._text(
            screen,
            f"TIME  {sec}s",
            self.fs,
            (255, 100, 120) if self.time_left <= 4 else self.accent,
            682,
        )

    def _draw_deflect(self, screen):
        cx, cy = self.center_pos
        pygame.draw.circle(screen, (40, 50, 80), (cx, cy), 70, 2)
        pygame.draw.circle(screen, self.accent, (cx, cy), 22)
        t_surf = self.timer_ring_font.render(
            f"{max(0, int(self.time_left + 0.999))}s", True, (15, 20, 35)
        )
        screen.blit(t_surf, t_surf.get_rect(center=(cx, cy)))
        pygame.draw.arc(
            screen,
            (255, 255, 255),
            pygame.Rect(cx - 70, cy - 70, 140, 140),
            -self.shield_angle - 0.4,
            -self.shield_angle + 0.4,
            7,
        )
        for deb in self.debris_list:
            pygame.draw.circle(
                screen, (255, 80, 100), (int(deb["x"]), int(deb["y"])), 8
            )

    def _draw_wasd(self, screen):
        lanes_x = [540, 640, 740]
        for x in lanes_x:
            pygame.draw.line(screen, (40, 50, 80), (x, 250), (x, 560), 2)
        pygame.draw.circle(
            screen, self.accent, (lanes_x[self.player_lane], 520), 16
        )
        for b in self.barriers:
            pygame.draw.rect(
                screen,
                (255, 60, 90),
                (lanes_x[b["lane"]] - 30, int(b["y"]), 60, 12),
                border_radius=4,
            )

    def _draw_solder(self, screen):
        step = self.TILE + self.GAP
        # Draw background cyberpunk traces grid
        for r in range(self.N):
            for c in range(self.N):
                rect = pygame.Rect(
                    self.grid.x + c * step,
                    self.grid.y + r * step,
                    self.TILE,
                    self.TILE,
                )
                is_glitch = (r, c) in self.glitch_tiles
                
                if is_glitch:
                    col = (230, 40, 75)
                elif c == 0:
                    col = (50, 190, 120)  # Source nodes
                elif c == 4:
                    col = (80, 150, 255)  # Target nodes
                else:
                    col = (25, 34, 60)

                pygame.draw.rect(screen, col, rect, border_radius=10)
                
                if is_glitch:
                    # Draw warning hazard symbol/pulse
                    glow_val = int(150 + 100 * math.sin(self.pulse_phase))
                    pygame.draw.rect(screen, (255, glow_val, glow_val), rect, 2, border_radius=10)
                    self._text(screen, "✕", self.fb, (255, 255, 255), rect.centery)
                else:
                    pygame.draw.rect(screen, (55, 70, 110), rect, 2, border_radius=10)
                    if c == 0:
                        self._text(screen, "IN", self.fs, (255, 255, 255), rect.centery)
                    elif c == 4:
                        self._text(screen, "OUT", self.fs, (255, 255, 255), rect.centery)

        # Draw live tracing line with glowing energy effect
        if len(self.solder_path) > 0:
            points = [
                (
                    self.grid.x + c * step + self.TILE // 2,
                    self.grid.y + r * step + self.TILE // 2,
                )
                for r, c in self.solder_path
            ]
            if len(points) > 1:
                pygame.draw.lines(screen, (255, 255, 255), False, points, 8)
                pygame.draw.lines(screen, self.accent, False, points, 4)

    def _new_board(self):
        for _ in range(500):
            b = [[None] * self.N for _ in range(self.N)]
            valid = True
            for r in range(self.N):
                for c in range(self.N):
                    choices = list(range(self.TYPES))
                    random.shuffle(choices)
                    picked = next(
                        (
                            v
                            for v in choices
                            if not (
                                c >= 2 and b[r][c - 1] == v and b[r][c - 2] == v
                            )
                            and not (
                                r >= 2 and b[r - 1][c] == v and b[r - 2][c] == v
                            )
                        ),
                        None,
                    )
                    if picked is None:
                        valid = False
                        break
                    b[r][c] = picked
                if not valid:
                    break
            if valid and self._has_move(b):
                return b
        return [
            [random.randrange(self.TYPES) for _ in range(self.N)]
            for _ in range(self.N)
        ]

    def _matches(self, b=None):
        b = self.board if b is None else b
        out = set()
        for r in range(self.N):
            for c in range(self.N - 2):
                if (
                    b[r][c] is not None
                    and b[r][c] == b[r][c + 1] == b[r][c + 2]
                ):
                    out.update((r, c + i) for i in range(3))
        for c in range(self.N):
            for r in range(self.N - 2):
                if (
                    b[r][c] is not None
                    and b[r][c] == b[r + 1][c] == b[r + 2][c]
                ):
                    out.update((r + i, c) for i in range(3))
        return out

    def _has_move(self, b):
        for r in range(self.N):
            for c in range(self.N):
                for dr, dc in ((0, 1), (1, 0)):
                    nr, nc = r + dr, c + dc
                    if nr < self.N and nc < self.N:
                        b[r][c], b[nr][nc] = b[nr][nc], b[r][c]
                        ok = bool(self._matches(b))
                        b[r][c], b[nr][nc] = b[nr][nc], b[r][c]
                        if ok:
                            return True
        return False

    def _swap(self, a, b):
        self.board[a[0]][a[1]], self.board[b[0]][b[1]] = (
            self.board[b[0]][b[1]],
            self.board[a[0]][a[1]],
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
                if self.board[r][c] is None:
                    self.board[r][c] = random.randrange(self.TYPES)
        self.strikes += 1
        if self.strikes >= self.TARGET_STRIKES:
            self._finish()
        return True

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
        if (
            0 <= r < self.N
            and 0 <= c < self.N
            and (pos[0] - self.grid.x) % step < self.TILE
            and (pos[1] - self.grid.y) % step < self.TILE
        ):
            return int(r), int(c)
        return None

    def _finish(self):
        self.done, self.selected, self.done_timer = (
            True,
            None,
            1.2,
        )

    def _fail(self):
        self.failed, self.selected = True, None

    def _text(self, screen, text, font, color, y):
        s = font.render(text, True, color)
        screen.blit(s, s.get_rect(center=(640, y)))

    def _draw_status_tracker(self, screen):
        y_title = 208
        if self.level_mode == "DEFLECT":
            self._text(screen, f"BLOCKED: {self.blocked_count} / TARGET {self.target_blocked}", self.strike_title_font, (210, 218, 240), y_title)
            return
        elif self.level_mode == "WASD_RUN":
            self._text(screen, f"DODGED: {self.dodged_count} / TARGET {self.target_dodged}", self.strike_title_font, (210, 218, 240), y_title)
            return
        elif self.level_mode == "SOLDER":
            self._text(screen, f"QUANTUM LINKS: {self.solder_connections} / TARGET {self.target_connections}", self.strike_title_font, (210, 218, 240), y_title)
            return
        elif self.level_mode == "MATCH3":
            self._text(screen, f"STRIKES: {self.strikes} / {self.TARGET_STRIKES}", self.strike_title_font, (210, 218, 240), y_title)
            return

    def _draw_board(self, screen):
        mouse, step = self._cell(pygame.mouse.get_pos()), self.TILE + self.GAP
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
                        screen,
                        (100, 115, 155),
                        rect.inflate(4, 4),
                        2,
                        border_radius=14,
                    )
                if self.selected == (r, c):
                    pygame.draw.rect(
                        screen,
                        self.accent,
                        rect.inflate(6, 6),
                        3,
                        border_radius=15,
                    )
                pygame.draw.rect(
                    screen, col, rect.inflate(-8, -8), border_radius=14
                )
                self._icon(
                    screen,
                    rect.center,
                    self.symbols[v % len(self.symbols)],
                    col,
                )

    def _icon(self, s, center, k, col):
        x, y = center
        d = tuple(max(25, v - 85) for v in col)
        w = (248, 252, 255)
        if k == "milk":
            r = pygame.Rect(x - 10, y - 10, 20, 22)
            pygame.draw.rect(s, w, r, border_radius=5)
            pygame.draw.rect(s, d, r, 2, border_radius=5)
        elif k == "coffee":
            pygame.draw.ellipse(s, (105, 65, 48), (x - 13, y - 10, 26, 20))
        elif k == "syrup":
            pygame.draw.rect(
                s, (255, 235, 245), (x - 10, y - 6, 20, 18), border_radius=5
            )
        elif k in ("spice", "matcha"):
            pygame.draw.circle(
                s,
                (190, 105, 70) if k == "spice" else (165, 195, 105),
                (x, y),
                12,
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
            f"{self.ingredient} successfully calibrated.",
            self.fb,
            (235, 240, 255),
            300,
        )
        self._text(s, "Returning to Mixing Station...", self.fs, (145, 155, 185), 450)
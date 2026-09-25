"""
mini_challenges.py
Cyberpunk Café - Ingredient Match-3 Mini Challenge

This file is a drop-in replacement for the old reaction/action mini-games.

Gameplay:
    1. Select a drink in the Mixing Station.
    2. A 5x5 ingredient puzzle appears.
    3. Click one tile, then click an adjacent tile to swap.
    4. If the swap creates a match of 3 or more, the match is cleared.
    5. Make 3 successful matches.
    6. The challenge finishes and quickly hands control back to the Mixing Station.
    7. The player has 25 seconds for each attempt.

Mouse controls only. One simple timer, no lives, keyboard actions, or
complicated combos.
"""

import math
import random
import pygame


# ---------------------------------------------------------------------------
# DRINK THEMES
# ---------------------------------------------------------------------------

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
    },
    "Caramel Byte": {
        "title": "COOKIE MATCH",
        "ingredient": "COOKIE",
        "accent": (255, 190, 120),
        "tile_colors": [
            (225, 160, 100),
            (255, 205, 130),
            (190, 135, 105),
            (245, 180, 200),
            (170, 215, 255),
        ],
    },
    "Stardust Matcha": {
        "title": "MATCHA MATCH",
        "ingredient": "MATCHA",
        "accent": (170, 245, 145),
        "tile_colors": [
            (155, 230, 145),
            (200, 250, 165),
            (125, 210, 180),
            (235, 220, 120),
            (180, 165, 245),
        ],
    },
    "Meteorite": {
        "title": "METEOR MATCH",
        "ingredient": "METEOR",
        "accent": (125, 205, 255),
        "tile_colors": [
            (235, 245, 255),
            (145, 205, 255),
            (175, 175, 235),
            (255, 195, 120),
            (205, 220, 245),
        ],
    },
}


# ---------------------------------------------------------------------------
# MINI CHALLENGE
# ---------------------------------------------------------------------------

class MiniChallenge:
    """
    Small mouse-controlled Match-3 puzzle.

    The Mixing Station only needs these public members/methods:
        challenge.done
        start_challenge(drink_name)
        update(dt)
        handle_event(event)
        draw(screen)
    """

    GRID_SIZE = 5
    TILE_SIZE = 62
    GAP = 6

    TARGET_STRIKES = 3
    TILE_TYPES = 5
    CHALLENGE_TIME = 25.0
    DONE_DISPLAY_TIME = 0.35

    def __init__(self):
        self.active = False
        self.done = False

        self.drink = ""
        self.title = "INGREDIENT MATCH"
        self.ingredient = "INGREDIENT"
        self.accent = (120, 235, 255)
        self.tile_colors = []
        self.symbols = ["milk", "syrup", "coffee", "ice", "mint"]

        self.board = []
        self.selected = None

        self.strikes = 0
        self.message = "MATCH 3 INGREDIENTS"
        self.message_timer = 0.0
        self.time_left = self.CHALLENGE_TIME
        self.time_up = False

        # Animation for the finished state.
        self.done_timer = 0.0
        self.pulse = 0.0

        self.panel_rect = pygame.Rect(280, 95, 720, 535)
        self.grid_rect = pygame.Rect(375, 215, 0, 0)

        self.font_title = None
        self.font_text = None
        self.font_small = None
        self.font_big = None

        self._build_fonts()

    # -----------------------------------------------------------------------
    # SETUP
    # -----------------------------------------------------------------------

    def _build_fonts(self):
        """Create fonts without requiring an external font file."""
        self.font_title = pygame.font.SysFont("arial", 28, bold=True)
        self.font_text = pygame.font.SysFont("arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("arial", 16, bold=True)
        self.font_big = pygame.font.SysFont("arial", 38, bold=True)

    def start_challenge(self, drink_name):
        """Start a fresh puzzle for the selected drink."""
        data = CHALLENGES.get(drink_name, {
            "title": "INGREDIENT MATCH",
            "ingredient": "INGREDIENT",
            "accent": (120, 235, 255),
            "tile_colors": [
                (120, 235, 255),
                (205, 170, 255),
                (255, 180, 210),
                (150, 245, 210),
                (255, 225, 130),
            ],
        })

        self.drink = drink_name
        self.title = data["title"]
        self.ingredient = data["ingredient"]
        self.accent = data["accent"]
        self.tile_colors = data["tile_colors"]
        self.symbols = ["milk", "syrup", "coffee", "ice", "mint"]

        self.active = True
        self.done = False
        self.selected = None
        self.strikes = 0
        self.message = "MATCH 3 INGREDIENTS"
        self.message_timer = 0.0
        self.time_left = self.CHALLENGE_TIME
        self.time_up = False
        self.done_timer = 0.0
        self.pulse = 0.0

        self.board = self._create_board()

        board_size = (
            self.GRID_SIZE * self.TILE_SIZE
            + (self.GRID_SIZE - 1) * self.GAP
        )

        self.grid_rect = pygame.Rect(
            375,
            215,
            board_size,
            board_size,
        )

    # -----------------------------------------------------------------------
    # BOARD CREATION
    # -----------------------------------------------------------------------

    def _create_board(self):
        """
        Create a board with no automatic matches.

        This prevents the player from getting a free match before making
        a move.
        """
        for _ in range(200):
            board = [
                [
                    random.randrange(self.TILE_TYPES)
                    for _ in range(self.GRID_SIZE)
                ]
                for _ in range(self.GRID_SIZE)
            ]

            if not self._find_matches(board):
                return board

        # Extremely unlikely fallback.
        return self._safe_board()

    def _safe_board(self):
        """Deterministic no-match fallback."""
        board = []

        for row in range(self.GRID_SIZE):
            current = []

            for col in range(self.GRID_SIZE):
                current.append((row * 2 + col) % self.TILE_TYPES)

            board.append(current)

        return board

    # -----------------------------------------------------------------------
    # MATCH LOGIC
    # -----------------------------------------------------------------------

    def _find_matches(self, board=None):
        """
        Return a set of (row, col) cells belonging to horizontal or
        vertical groups of 3 or more.
        """
        if board is None:
            board = self.board

        matches = set()

        # Horizontal matches.
        for row in range(self.GRID_SIZE):
            start = 0

            while start < self.GRID_SIZE:
                value = board[row][start]
                end = start + 1

                while (
                    end < self.GRID_SIZE
                    and board[row][end] == value
                ):
                    end += 1

                if value is not None and end - start >= 3:
                    for col in range(start, end):
                        matches.add((row, col))

                start = end

        # Vertical matches.
        for col in range(self.GRID_SIZE):
            start = 0

            while start < self.GRID_SIZE:
                value = board[start][col]
                end = start + 1

                while (
                    end < self.GRID_SIZE
                    and board[end][col] == value
                ):
                    end += 1

                if value is not None and end - start >= 3:
                    for row in range(start, end):
                        matches.add((row, col))

                start = end

        return matches

    def _swap(self, first, second):
        """Swap two board cells."""
        r1, c1 = first
        r2, c2 = second

        self.board[r1][c1], self.board[r2][c2] = (
            self.board[r2][c2],
            self.board[r1][c1],
        )

    def _is_adjacent(self, first, second):
        """Check whether two cells share an edge."""
        r1, c1 = first
        r2, c2 = second

        return abs(r1 - r2) + abs(c1 - c2) == 1

    def _resolve_match(self):
        """
        Remove the current match, collapse columns, refill the board,
        and count one successful strike.
        """
        matches = self._find_matches()

        if not matches:
            return False

        for row, col in matches:
            self.board[row][col] = None

        # Collapse each column downward.
        for col in range(self.GRID_SIZE):
            remaining = [
                self.board[row][col]
                for row in range(self.GRID_SIZE)
                if self.board[row][col] is not None
            ]

            missing = self.GRID_SIZE - len(remaining)
            new_values = [
                random.randrange(self.TILE_TYPES)
                for _ in range(missing)
            ]

            values = new_values + remaining

            for row in range(self.GRID_SIZE):
                self.board[row][col] = values[row]

        self.strikes += 1
        self.message = f"MATCH {self.strikes} / {self.TARGET_STRIKES}"
        self.message_timer = 0.8

        if self.strikes >= self.TARGET_STRIKES:
            self._finish()

        return True

    def _try_swap(self, first, second):
        """
        Attempt a swap.

        A swap only counts if it creates a match.
        Otherwise the tiles are immediately returned to their original
        positions.
        """
        self._swap(first, second)

        if self._find_matches():
            self._resolve_match()
            return True

        self._swap(first, second)
        self.message = "TRY ANOTHER SWAP"
        self.message_timer = 0.8
        return False

    # -----------------------------------------------------------------------
    # INPUT
    # -----------------------------------------------------------------------

    def _cell_from_mouse(self, position):
        """Convert a mouse position into a board cell."""
        x, y = position

        if not self.grid_rect.collidepoint(position):
            return None

        step = self.TILE_SIZE + self.GAP

        col = (x - self.grid_rect.x) // step
        row = (y - self.grid_rect.y) // step

        if not (
            0 <= row < self.GRID_SIZE
            and 0 <= col < self.GRID_SIZE
        ):
            return None

        local_x = (x - self.grid_rect.x) % step
        local_y = (y - self.grid_rect.y) % step

        # Ignore the small gap between tiles.
        if local_x >= self.TILE_SIZE or local_y >= self.TILE_SIZE:
            return None

        return int(row), int(col)

    def handle_event(self, event):
        """Handle mouse interaction for the puzzle."""
        if not self.active:
            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        cell = self._cell_from_mouse(event.pos)

        if cell is None:
            return

        if self.selected is None:
            self.selected = cell
            self.message = "CHOOSE A NEIGHBOUR"
            self.message_timer = 0.6
            return

        if cell == self.selected:
            self.selected = None
            self.message = "MATCH 3 INGREDIENTS"
            self.message_timer = 0.5
            return

        if self._is_adjacent(self.selected, cell):
            first = self.selected
            self.selected = None
            self._try_swap(first, cell)
            return

        # Clicking another non-adjacent tile simply moves the selection.
        self.selected = cell
        self.message = "CHOOSE A NEIGHBOUR"
        self.message_timer = 0.6

    # -----------------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------------

    def update(self, dt):
        """Update UI animations and the 25-second puzzle timer."""
        if not self.active and not self.done:
            return

        self.pulse += dt

        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)

        if self.active:
            self.time_left = max(0.0, self.time_left - dt)

            if self.time_left <= 0:
                self._time_up()

        if self.done:
            self.done_timer += dt
            if self.done_timer >= self.DONE_DISPLAY_TIME:
                self.done = False
                self.done_timer = 0.0

    def _time_up(self):
        """Reset the puzzle when the player runs out of time."""
        self.time_up = True
        self.active = False
        self.selected = None
        self.strikes = 0
        self.message = "TIME'S UP - TRY AGAIN!"
        self.message_timer = 0.0
        self.time_left = self.CHALLENGE_TIME
        self.board = self._create_board()

        # Start a fresh attempt immediately so the player gets another
        # full 25 seconds rather than being trapped on a failure screen.
        self.active = True
        self.time_up = False

    def _finish(self):
        """Finish the challenge and unlock the Mixing Station."""
        self.active = False
        self.done = True
        self.selected = None
        self.done_timer = 0.0
        self.message = "INGREDIENT READY!"

    # -----------------------------------------------------------------------
    # DRAWING
    # -----------------------------------------------------------------------

    def draw(self, screen):
        """
        Draw the challenge over the existing Mixing Station.

        The background station remains visible underneath a translucent
        dark overlay, so the mini-game feels like part of the same game.
        """
        if not self.active and not self.done:
            return

        self._draw_overlay(screen)
        self._draw_panel(screen)

        if self.done:
            self._draw_done(screen)
        else:
            self._draw_active(screen)

    def _draw_overlay(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((5, 8, 22, 175))
        screen.blit(overlay, (0, 0))

    def _draw_panel(self, screen):
        # Soft outer glow.
        glow_rect = self.panel_rect.inflate(14, 14)
        pygame.draw.rect(
            screen,
            (self.accent[0], self.accent[1], self.accent[2]),
            glow_rect,
            border_radius=22,
        )

        pygame.draw.rect(
            screen,
            (18, 22, 43),
            self.panel_rect,
            border_radius=20,
        )

        pygame.draw.rect(
            screen,
            self.accent,
            self.panel_rect,
            width=2,
            border_radius=20,
        )

    def _draw_active(self, screen):
        # Title.
        title = self.font_title.render(
            self.title,
            True,
            self.accent,
        )

        title_rect = title.get_rect(
            center=(640, 128)
        )

        screen.blit(title, title_rect)

        # Drink name.
        drink = self.font_text.render(
            self.drink.upper(),
            True,
            (235, 240, 255),
        )

        screen.blit(
            drink,
            drink.get_rect(center=(640, 158)),
        )

        # Ingredient + progress.
        ingredient = self.font_small.render(
            f"{self.ingredient}   •   MATCH 3 INGREDIENTS",
            True,
            (185, 195, 220),
        )

        screen.blit(
            ingredient,
            ingredient.get_rect(center=(640, 188)),
        )

        # Timer.
        self._draw_timer(screen)

        # Strike indicators.
        self._draw_strikes(screen)

        # Board.
        self._draw_board(screen)

        # Bottom instruction.
        if self.message_timer > 0:
            message_text = self.message
        else:
            message_text = "CLICK TWO ADJACENT TILES TO SWAP"

        message = self.font_small.render(
            message_text,
            True,
            (220, 225, 245),
        )

        screen.blit(
            message,
            message.get_rect(center=(640, 572)),
        )

        hint = self.font_small.render(
            "Mouse only  •  25-second prep window  •  No penalty for trying",
            True,
            (125, 140, 175),
        )

        screen.blit(
            hint,
            hint.get_rect(center=(640, 595)),
        )

    def _draw_timer(self, screen):
        """Draw the remaining 25-second challenge time."""
        seconds = max(0, int(self.time_left + 0.999))

        timer_color = self.accent
        if self.time_left <= 5:
            timer_color = (255, 145, 165)

        label = self.font_small.render(
            f"TIME  {seconds}s",
            True,
            timer_color,
        )

        screen.blit(
            label,
            label.get_rect(center=(640, 650)),
        )

    def _draw_strikes(self, screen):
        label = self.font_small.render(
            "INGREDIENT MATCHES",
            True,
            (165, 175, 205),
        )

        screen.blit(
            label,
            label.get_rect(center=(640, 206)),
        )

        start_x = 575
        y = 207

        for index in range(self.TARGET_STRIKES):
            rect = pygame.Rect(
                start_x + index * 65,
                y,
                50,
                8,
            )

            if index < self.strikes:
                color = self.accent
            else:
                color = (55, 62, 85)

            pygame.draw.rect(
                screen,
                color,
                rect,
                border_radius=4,
            )

    def _draw_board(self, screen):
        mouse_cell = self._cell_from_mouse(pygame.mouse.get_pos())

        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                x = (
                    self.grid_rect.x
                    + col * (self.TILE_SIZE + self.GAP)
                )

                y = (
                    self.grid_rect.y
                    + row * (self.TILE_SIZE + self.GAP)
                )

                rect = pygame.Rect(
                    x,
                    y,
                    self.TILE_SIZE,
                    self.TILE_SIZE,
                )

                value = self.board[row][col]

                # Tile background.
                pygame.draw.rect(
                    screen,
                    (27, 32, 57),
                    rect,
                    border_radius=12,
                )

                # Hover highlight.
                if mouse_cell == (row, col):
                    pygame.draw.rect(
                        screen,
                        (90, 105, 145),
                        rect.inflate(4, 4),
                        width=2,
                        border_radius=14,
                    )

                # Selected tile.
                if self.selected == (row, col):
                    pygame.draw.rect(
                        screen,
                        self.accent,
                        rect.inflate(6, 6),
                        width=3,
                        border_radius=15,
                    )

                self._draw_tile(
                    screen,
                    rect,
                    value,
                    row,
                    col,
                )

    def _draw_tile(self, screen, rect, value, row, col):
        color = self.tile_colors[value % len(self.tile_colors)]

        center = rect.center

        # Tile glow.
        glow = pygame.Surface(
            (rect.width + 18, rect.height + 18),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow,
            (*color, 35),
            (glow.get_width() // 2, glow.get_height() // 2),
            24,
        )

        screen.blit(
            glow,
            (
                rect.centerx - glow.get_width() // 2,
                rect.centery - glow.get_height() // 2,
            ),
        )

        # Main rounded tile.
        inner = rect.inflate(-8, -8)

        pygame.draw.rect(
            screen,
            color,
            inner,
            border_radius=14,
        )

        # Ingredient symbol.
        self._draw_symbol(
            screen,
            center,
            value,
            color,
        )

    def _draw_symbol(self, screen, center, value, tile_color):
        """
        Draw cute café ingredients instead of abstract game symbols.

        The same five ingredient shapes are reused on the board:
            milk bottle, syrup bottle, coffee bean, ice cube, mint leaf.
        Drink colours still change the tile palette so every drink keeps
        its own identity.
        """
        cx, cy = center
        kind = self.symbols[value % len(self.symbols)]

        dark = (
            max(20, tile_color[0] - 85),
            max(20, tile_color[1] - 85),
            max(20, tile_color[2] - 85),
        )

        if kind == "milk":
            # Tiny milk bottle / carton.
            body = pygame.Rect(cx - 11, cy - 13, 22, 26)
            pygame.draw.rect(screen, (248, 252, 255), body, border_radius=5)
            pygame.draw.rect(screen, dark, body, width=2, border_radius=5)
            cap = pygame.Rect(cx - 7, cy - 17, 14, 6)
            pygame.draw.rect(screen, dark, cap, border_radius=3)
            pygame.draw.line(screen, tile_color, (cx - 6, cy - 2), (cx + 6, cy - 2), 3)
            pygame.draw.circle(screen, tile_color, (cx, cy + 7), 3)

        elif kind == "syrup":
            # Cute syrup bottle with a cap and little label.
            body = pygame.Rect(cx - 11, cy - 8, 22, 19)
            pygame.draw.rect(screen, (255, 235, 245), body, border_radius=6)
            pygame.draw.rect(screen, dark, body, width=2, border_radius=6)
            neck = pygame.Rect(cx - 6, cy - 15, 12, 8)
            pygame.draw.rect(screen, tile_color, neck, border_radius=3)
            pygame.draw.rect(screen, dark, neck, width=1, border_radius=3)
            pygame.draw.rect(screen, (255, 255, 255), (cx - 6, cy - 2, 12, 7), border_radius=3)
            pygame.draw.circle(screen, tile_color, (cx, cy + 1), 2)

        elif kind == "coffee":
            # Coffee bean.
            pygame.draw.ellipse(screen, (105, 65, 48), (cx - 14, cy - 11, 28, 22))
            pygame.draw.ellipse(screen, dark, (cx - 14, cy - 11, 28, 22), 2)
            pygame.draw.arc(
                screen,
                (235, 190, 145),
                pygame.Rect(cx - 7, cy - 9, 14, 18),
                math.radians(65),
                math.radians(295),
                2,
            )

        elif kind == "ice":
            # Sparkly ice cube.
            points = [
                (cx - 12, cy - 9),
                (cx + 4, cy - 14),
                (cx + 13, cy - 5),
                (cx + 9, cy + 12),
                (cx - 7, cy + 14),
                (cx - 14, cy + 4),
            ]
            pygame.draw.polygon(screen, (215, 245, 255), points)
            pygame.draw.polygon(screen, dark, points, 2)
            pygame.draw.line(screen, (255, 255, 255), (cx - 7, cy - 5), (cx + 4, cy - 9), 2)
            pygame.draw.line(screen, (255, 255, 255), (cx + 4, cy - 9), (cx + 7, cy + 4), 2)

        else:
            # Mint leaf with a little stem.
            leaf = [
                (cx, cy + 13),
                (cx - 12, cy + 2),
                (cx - 7, cy - 11),
                (cx + 4, cy - 14),
                (cx + 11, cy - 4),
                (cx + 7, cy + 8),
            ]
            pygame.draw.polygon(screen, (105, 235, 170), leaf)
            pygame.draw.polygon(screen, dark, leaf, 2)
            pygame.draw.line(screen, (55, 155, 115), (cx, cy + 10), (cx + 3, cy - 8), 2)
            pygame.draw.circle(screen, (255, 255, 255), (cx - 3, cy - 5), 2)

    def _draw_done(self, screen):
        pulse = (1.0 + __import__("math").sin(self.done_timer * 4.0)) * 0.5

        title_color = self.accent

        title = self.font_big.render(
            "INGREDIENT READY!",
            True,
            title_color,
        )

        screen.blit(
            title,
            title.get_rect(center=(640, 245)),
        )

        subtitle = self.font_text.render(
            f"{self.ingredient} is ready for the blender.",
            True,
            (235, 240, 255),
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(center=(640, 292)),
        )

        # Large ingredient icon.
        center = (640, 390)
        radius = int(58 + pulse * 6)

        pygame.draw.circle(
            screen,
            (25, 32, 58),
            center,
            radius + 12,
        )

        pygame.draw.circle(
            screen,
            self.accent,
            center,
            radius + 12,
            width=3,
        )

        pygame.draw.circle(
            screen,
            (230, 240, 255),
            center,
            radius - 6,
        )

        # Use the actual café ingredient set for the finished state.
        self._draw_symbol(
            screen,
            center,
            1,
            (230, 240, 255),
        )

        ready = self.font_text.render(
            "Your drink base is ready.",
            True,
            (190, 200, 225),
        )

        screen.blit(
            ready,
            ready.get_rect(center=(640, 505)),
        )

        continue_text = self.font_small.render(
            "Returning to the Mixing Station...",
            True,
            (125, 140, 175),
        )

        screen.blit(
            continue_text,
            continue_text.get_rect(center=(640, 555)),
        )

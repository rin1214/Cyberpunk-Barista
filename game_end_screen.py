"""
============================================================
CYBERPUNK CAFÉ
GAME END SCREEN
============================================================

This file controls the final game ending screen.

The ending sequence is:

    Final successful drink
            ↓
    Café closing animation
            ↓
    Cyber-cat celebration
            ↓
    Thank-you message
            ↓
    Final statistics
            ↓
    PLAY AGAIN / MAIN MENU

IMPORTANT:

This file does NOT control:

    • XP
    • Credits
    • Level progression
    • Customer orders
    • Drink mixing

Those systems remain in their existing files.

This screen only displays the final game result.
"""

import math
import pygame


# ============================================================
# GAME END SCREEN
# ============================================================

class GameEndScreen:

    # --------------------------------------------------------
    # INITIALISATION
    # --------------------------------------------------------

    def __init__(self, screen):

        self.screen = screen

        self.width = screen.get_width()
        self.height = screen.get_height()

        # ----------------------------------------------------
        # CLOCK
        # ----------------------------------------------------

        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # SCREEN STATE
        # ----------------------------------------------------

        self.running = True

        self.result = None

        # ----------------------------------------------------
        # ANIMATION TIMER
        # ----------------------------------------------------

        self.elapsed = 0.0

        # ----------------------------------------------------
        # ENDING PHASE
        # ----------------------------------------------------
        #
        # 0 = café closing
        # 1 = cat appears
        # 2 = thank-you message
        # 3 = final statistics
        #

        self.phase = 0

        # ----------------------------------------------------
        # PHASE TIMERS
        # ----------------------------------------------------

        self.phase_timer = 0.0

        # ----------------------------------------------------
        # BUTTON RECTANGLES
        # ----------------------------------------------------

        self.play_again_rect = pygame.Rect(
            self.width // 2 - 170,
            575,
            340,
            55,
        )

        self.main_menu_rect = pygame.Rect(
            self.width // 2 - 170,
            645,
            340,
            55,
        )

        # ----------------------------------------------------
        # FONTS
        # ----------------------------------------------------

        self.font_title = pygame.font.SysFont(
            "Arial",
            48,
            bold=True,
        )

        self.font_large = pygame.font.SysFont(
            "Arial",
            34,
            bold=True,
        )

        self.font_medium = pygame.font.SysFont(
            "Arial",
            25,
            bold=True,
        )

        self.font_small = pygame.font.SysFont(
            "Arial",
            19,
        )

        self.font_button = pygame.font.SysFont(
            "Arial",
            21,
            bold=True,
        )

        # ----------------------------------------------------
        # COLOURS
        # ----------------------------------------------------

        self.background = (
            7,
            10,
            27,
        )

        self.panel = (
            15,
            20,
            43,
        )

        self.panel_light = (
            23,
            30,
            58,
        )

        self.cyan = (
            75,
            225,
            255,
        )

        self.pink = (
            255,
            80,
            190,
        )

        self.purple = (
            175,
            100,
            255,
        )

        self.yellow = (
            255,
            220,
            100,
        )

        self.white = (
            245,
            248,
            255,
        )

        self.grey = (
            160,
            170,
            195,
        )

        # ----------------------------------------------------
        # CAT ANIMATION
        # ----------------------------------------------------

        self.cat_x = self.width // 2
        self.cat_y = 245

        self.cat_scale = 1.0

        self.cat_bob = 0.0
        self.cat_wave = 0.0

        # ----------------------------------------------------
        # LIGHTS
        # ----------------------------------------------------

        self.lights = []

        for i in range(12):

            x = 70 + i * 105

            self.lights.append(
                {
                    "x": x,
                    "y": 75,
                    "phase": i * 0.5,
                }
            )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.running = True

        self.result = None

        self.elapsed = 0.0

        self.phase = 0

        self.phase_timer = 0.0

        self.cat_bob = 0.0
        self.cat_wave = 0.0

    # ========================================================
    # START
    # ========================================================

    def run(
        self,
        player_name="BARISTA",
        level=3,
        successful_drinks=21,
        xp=0,
        credits=0,
    ):

        self.reset()

        self.player_name = str(
            player_name
        )

        self.final_level = int(
            level
        )

        self.successful_drinks = int(
            successful_drinks
        )

        self.final_xp = int(
            xp
        )

        self.final_credits = int(
            credits
        )

        while self.running:

            dt = (
                self.clock.tick(60)
                / 1000.0
            )

            self.elapsed += dt
            self.phase_timer += dt

            # ------------------------------------------------
            # EVENTS
            # ------------------------------------------------

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    self.running = False

                    self.result = "quit"

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.running = False

                        self.result = "main_menu"

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        self.handle_click(
                            event.pos
                        )

            # ------------------------------------------------
            # UPDATE
            # ------------------------------------------------

            self.update(dt)

            # ------------------------------------------------
            # DRAW
            # ------------------------------------------------

            self.draw()

            pygame.display.flip()

        return self.result

    # ========================================================
    # HANDLE CLICK
    # ========================================================

    def handle_click(
        self,
        mouse_pos,
    ):

        # ----------------------------------------------------
        # PLAY AGAIN
        # ----------------------------------------------------

        if self.play_again_rect.collidepoint(
            mouse_pos
        ):

            self.result = "play_again"

            self.running = False

            return

        # ----------------------------------------------------
        # MAIN MENU
        # ----------------------------------------------------

        if self.main_menu_rect.collidepoint(
            mouse_pos
        ):

            self.result = "main_menu"

            self.running = False

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt,
    ):

        # ----------------------------------------------------
        # CAT BOBBING
        # ----------------------------------------------------

        self.cat_bob += dt * 3.0

        self.cat_wave += dt * 7.0

        # ----------------------------------------------------
        # ENDING PHASES
        # ----------------------------------------------------

        if self.phase == 0:

            # Café closing animation.

            if self.phase_timer >= 2.5:

                self.phase = 1

                self.phase_timer = 0.0

        elif self.phase == 1:

            # Cat appears.

            if self.phase_timer >= 2.0:

                self.phase = 2

                self.phase_timer = 0.0

        elif self.phase == 2:

            # Thank-you message.

            if self.phase_timer >= 2.0:

                self.phase = 3

                self.phase_timer = 0.0

        elif self.phase == 3:

            # Final statistics remain visible.

            pass

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    def draw_background(self):

        self.screen.fill(
            self.background
        )

        # ----------------------------------------------------
        # FLOOR
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            (
                10,
                14,
                32,
            ),
            (
                0,
                470,
                self.width,
                250,
            ),
        )

        # ----------------------------------------------------
        # CYBERPUNK HORIZONTAL LINES
        # ----------------------------------------------------

        for y in range(
            500,
            720,
            35,
        ):

            pygame.draw.line(
                self.screen,
                (
                    20,
                    28,
                    55,
                ),
                (
                    0,
                    y,
                ),
                (
                    self.width,
                    y,
                ),
                1,
            )

        # ----------------------------------------------------
        # NEON LIGHTS
        # ----------------------------------------------------

        for light in self.lights:

            pulse = (
                math.sin(
                    self.elapsed * 3
                    + light["phase"]
                )
                + 1
            ) / 2

            radius = int(
                4 + pulse * 3
            )

            pygame.draw.circle(
                self.screen,
                self.cyan,
                (
                    light["x"],
                    light["y"],
                ),
                radius,
            )

    # ========================================================
    # DRAW CAFÉ SIGN
    # ========================================================

    def draw_cafe_sign(self):

        sign_rect = pygame.Rect(
            self.width // 2 - 280,
            30,
            560,
            80,
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            sign_rect,
            border_radius=18,
        )

        pygame.draw.rect(
            self.screen,
            self.cyan,
            sign_rect,
            width=2,
            border_radius=18,
        )

        title = self.font_medium.render(
            "CYBERPUNK CAFÉ",
            True,
            self.cyan,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=sign_rect.center
            ),
        )

    # ========================================================
    # DRAW CLOSING MESSAGE
    # ========================================================

    def draw_closing_message(self):

        if self.phase == 0:

            title = self.font_title.render(
                "CAFÉ CLOSING...",
                True,
                self.pink,
            )

            self.screen.blit(
                title,
                title.get_rect(
                    center=(
                        self.width // 2,
                        145,
                    )
                ),
            )

            subtitle = self.font_small.render(
                "The last order has been served.",
                True,
                self.white,
            )

            self.screen.blit(
                subtitle,
                subtitle.get_rect(
                    center=(
                        self.width // 2,
                        180,
                    )
                ),
            )

        elif self.phase >= 1:

            title = self.font_title.render(
                "THANK YOU FOR PLAYING!",
                True,
                self.cyan,
            )

            self.screen.blit(
                title,
                title.get_rect(
                    center=(
                        self.width // 2,
                        145,
                    )
                ),
            )

    # ========================================================
    # DRAW CAT
    # ========================================================

    def draw_cat(self):

        # ----------------------------------------------------
        # BOBBING
        # ----------------------------------------------------

        bob = int(
            math.sin(
                self.cat_bob
            ) * 6
        )

        cx = self.cat_x
        cy = self.cat_y + bob

        # ----------------------------------------------------
        # GLOW
        # ----------------------------------------------------

        glow_radius = 105

        glow_surface = pygame.Surface(
            (
                glow_radius * 2,
                glow_radius * 2,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow_surface,
            (
                75,
                225,
                255,
                35,
            ),
            (
                glow_radius,
                glow_radius,
            ),
            glow_radius,
        )

        self.screen.blit(
            glow_surface,
            (
                cx - glow_radius,
                cy - glow_radius,
            ),
        )

        # ----------------------------------------------------
        # BODY
        # ----------------------------------------------------

        body_rect = pygame.Rect(
            cx - 60,
            cy + 45,
            120,
            90,
        )

        pygame.draw.ellipse(
            self.screen,
            (
                125,
                105,
                180,
            ),
            body_rect,
        )

        # ----------------------------------------------------
        # HEAD
        # ----------------------------------------------------

        head_rect = pygame.Rect(
            cx - 75,
            cy - 65,
            150,
            130,
        )

        pygame.draw.ellipse(
            self.screen,
            (
                155,
                125,
                205,
            ),
            head_rect,
        )

        # ----------------------------------------------------
        # EARS
        # ----------------------------------------------------

        left_ear = [
            (
                cx - 65,
                cy - 50,
            ),
            (
                cx - 85,
                cy - 105,
            ),
            (
                cx - 30,
                cy - 75,
            ),
        ]

        right_ear = [
            (
                cx + 65,
                cy - 50,
            ),
            (
                cx + 85,
                cy - 105,
            ),
            (
                cx + 30,
                cy - 75,
            ),
        ]

        pygame.draw.polygon(
            self.screen,
            (
                175,
                100,
                220,
            ),
            left_ear,
        )

        pygame.draw.polygon(
            self.screen,
            (
                175,
                100,
                220,
            ),
            right_ear,
        )

        # ----------------------------------------------------
        # EYES
        # ----------------------------------------------------

        pygame.draw.ellipse(
            self.screen,
            self.cyan,
            (
                cx - 45,
                cy - 25,
                28,
                35,
            ),
        )

        pygame.draw.ellipse(
            self.screen,
            self.cyan,
            (
                cx + 17,
                cy - 25,
                28,
                35,
            ),
        )

        # ----------------------------------------------------
        # PUPILS
        # ----------------------------------------------------

        pygame.draw.circle(
            self.screen,
            (
                10,
                15,
                30,
            ),
            (
                cx - 31,
                cy - 8,
            ),
            7,
        )

        pygame.draw.circle(
            self.screen,
            (
                10,
                15,
                30,
            ),
            (
                cx + 31,
                cy - 8,
            ),
            7,
        )

        # ----------------------------------------------------
        # NOSE
        # ----------------------------------------------------

        pygame.draw.polygon(
            self.screen,
            self.pink,
            [
                (
                    cx - 7,
                    cy + 10,
                ),
                (
                    cx + 7,
                    cy + 10,
                ),
                (
                    cx,
                    cy + 18,
                ),
            ],
        )

        # ----------------------------------------------------
        # MOUTH
        # ----------------------------------------------------

        pygame.draw.arc(
            self.screen,
            (
                50,
                30,
                70,
            ),
            (
                cx - 18,
                cy + 12,
                18,
                18,
            ),
            0,
            math.pi,
            2,
        )

        pygame.draw.arc(
            self.screen,
            (
                50,
                30,
                70,
            ),
            (
                cx,
                cy + 12,
                18,
                18,
            ),
            0,
            math.pi,
            2,
        )

        # ----------------------------------------------------
        # WAVING PAW
        # ----------------------------------------------------

        wave_angle = math.sin(
            self.cat_wave
        ) * 0.35

        paw_x = int(
            cx
            + 95
            + math.sin(
                self.cat_wave
            ) * 12
        )

        paw_y = int(
            cy
            - 20
            + math.cos(
                self.cat_wave
            ) * 8
        )

        pygame.draw.circle(
            self.screen,
            (
                155,
                125,
                205,
            ),
            (
                paw_x,
                paw_y,
            ),
            24,
        )

        # ----------------------------------------------------
        # PAW GLOW
        # ----------------------------------------------------

        pygame.draw.circle(
            self.screen,
            self.cyan,
            (
                paw_x,
                paw_y,
            ),
            5,
        )

    # ========================================================
    # DRAW STATISTICS
    # ========================================================

    def draw_statistics(self):

        if self.phase < 3:

            return

        panel = pygame.Rect(
            310,
            320,
            660,
            215,
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            panel,
            border_radius=18,
        )

        pygame.draw.rect(
            self.screen,
            self.purple,
            panel,
            width=2,
            border_radius=18,
        )

        title = self.font_medium.render(
            "FINAL CAFÉ STATISTICS",
            True,
            self.yellow,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    panel.centerx,
                    panel.y + 35,
                )
            ),
        )

        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        stats = [
            (
                "Successful Drinks",
                str(
                    self.successful_drinks
                ),
            ),
            (
                "Final Level",
                str(
                    self.final_level
                ),
            ),
            (
                "Final XP",
                str(
                    self.final_xp
                ),
            ),
            (
                "Credits",
                f"${self.final_credits}",
            ),
        ]

        start_y = panel.y + 75

        for index, (
            label,
            value,
        ) in enumerate(stats):

            y = (
                start_y
                + index * 32
            )

            label_surface = (
                self.font_small.render(
                    label,
                    True,
                    self.grey,
                )
            )

            value_surface = (
                self.font_small.render(
                    value,
                    True,
                    self.white,
                )
            )

            self.screen.blit(
                label_surface,
                (
                    panel.x + 50,
                    y,
                ),
            )

            self.screen.blit(
                value_surface,
                (
                    panel.right - 150,
                    y,
                ),
            )

    # ========================================================
    # DRAW BUTTON
    # ========================================================

    def draw_button(
        self,
        rect,
        text,
        accent,
        hover,
    ):

        if hover:

            fill = (
                35,
                35,
                65,
            )

        else:

            fill = (
                22,
                25,
                50,
            )

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=12,
        )

        pygame.draw.rect(
            self.screen,
            accent,
            rect,
            width=2,
            border_radius=12,
        )

        text_surface = (
            self.font_button.render(
                text,
                True,
                self.white,
            )
        )

        self.screen.blit(
            text_surface,
            text_surface.get_rect(
                center=rect.center
            ),
        )

    # ========================================================
    # DRAW BUTTONS
    # ========================================================

    def draw_buttons(self):

        if self.phase < 3:

            return

        mouse_pos = pygame.mouse.get_pos()

        play_hover = (
            self.play_again_rect.collidepoint(
                mouse_pos
            )
        )

        menu_hover = (
            self.main_menu_rect.collidepoint(
                mouse_pos
            )
        )

        self.draw_button(
            self.play_again_rect,
            "PLAY AGAIN",
            self.cyan,
            play_hover,
        )

        self.draw_button(
            self.main_menu_rect,
            "MAIN MENU",
            self.pink,
            menu_hover,
        )

    # ========================================================
    # DRAW EVERYTHING
    # ========================================================

    def draw(self):

        self.draw_background()

        self.draw_cafe_sign()

        self.draw_closing_message()

        # Cat becomes visible after
        # the café closing phase.

        if self.phase >= 1:

            self.draw_cat()

        self.draw_statistics()

        self.draw_buttons()
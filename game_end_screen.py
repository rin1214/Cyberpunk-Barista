
import math
import os
import pygame


# ============================================================
# GAME END SCREEN
# ============================================================

class GameEndScreen:

    # ========================================================
    # INITIALISATION
    # ========================================================

    def __init__(self, screen, project_root=None):

        self.screen = screen

        self.width = screen.get_width()
        self.height = screen.get_height()

        # ----------------------------------------------------
        # PROJECT ROOT
        # ----------------------------------------------------

        if project_root is not None:

            self.project_root = project_root

        else:

            self.project_root = os.path.dirname(
                os.path.abspath(__file__)
            )

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
        # ENDING PHASE
        #
        # 0 = closing message
        # 1 = cat waving
        # 2 = thank-you message
        # 3 = statistics/buttons
        # ----------------------------------------------------

        self.phase = 0

        self.phase_timer = 0.0
        self.elapsed = 0.0

        # ----------------------------------------------------
        # FINAL PLAYER INFORMATION
        # ----------------------------------------------------

        self.player_name = "BARISTA"

        self.final_level = 3

        self.successful_drinks = 21

        self.final_xp = 0

        self.final_credits = 0

        # ====================================================
        # BACKGROUND
        # ====================================================

        self.background = None

        # ====================================================
        # CYBER-CAT
        # ====================================================

        self.cat_frames = []

        self.cat_frame_index = 0

        self.cat_frame_timer = 0.0

        # Time between animation frames.
        #
        # Smaller number = faster waving.
        #

        self.cat_frame_speed = 0.10

        # Cat size on the game screen.

        self.cat_size = (
            330,
            330,
        )

        # Cat position.

        self.cat_position = (
            int(self.width * 0.25),
            int(self.height * 0.60),
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        self.play_again_rect = pygame.Rect(
            285,
            625,
            310,
            58,
        )

        self.main_menu_rect = pygame.Rect(
            685,
            625,
            310,
            58,
        )

        # ====================================================
        # FONTS
        # ====================================================

        self.font_title = pygame.font.SysFont(
            "Arial",
            50,
            bold=True,
        )

        self.font_large = pygame.font.SysFont(
            "Arial",
            32,
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
            22,
            bold=True,
        )

        # ====================================================
        # COLOURS
        # ====================================================

        self.white = (
            245,
            248,
            255,
        )

        self.cyan = (
            75,
            225,
            255,
        )

        self.pink = (
            255,
            95,
            205,
        )

        self.purple = (
            185,
            125,
            255,
        )

        self.gold = (
            255,
            220,
            115,
        )

        self.grey = (
            185,
            190,
            210,
        )

        self.panel = (
            18,
            21,
            43,
        )

        # ====================================================
        # LOAD ASSETS
        # ====================================================

        self.load_assets()

    # ========================================================
    # ASSET PATH
    # ========================================================

    def asset_path(
        self,
        *parts,
    ):

        return os.path.join(
            self.project_root,
            "assets",
            "mahirah",
            "end_game",
            *parts,
        )

    # ========================================================
    # LOAD ASSETS
    # ========================================================

    def load_assets(self):

        # ====================================================
        # BACKGROUND
        # ====================================================

        background_path = self.asset_path(
            "end_game_background.png"
        )

        try:

            image = pygame.image.load(
                background_path
            ).convert()

            self.background = (
                pygame.transform.smoothscale(
                    image,
                    (
                        self.width,
                        self.height,
                    ),
                )
            )

            print(
                "[END SCREEN] Background loaded."
            )

        except (
            pygame.error,
            FileNotFoundError,
        ) as error:

            print(
                "[END SCREEN] Background could not "
                f"be loaded: {error}"
            )

            self.background = pygame.Surface(
                (
                    self.width,
                    self.height,
                )
            )

            self.background.fill(
                (
                    8,
                    10,
                    25,
                )
            )

        # ====================================================
        # CAT WAVE FRAMES
        # ====================================================

        self.cat_frames.clear()

        for number in range(
            1,
            9,
        ):

            frame_path = self.asset_path(
                "cat_wave",
                f"{number:02d}.png",
            )

            try:

                frame = pygame.image.load(
                    frame_path
                ).convert_alpha()

                frame = (
                    pygame.transform.smoothscale(
                        frame,
                        self.cat_size,
                    )
                )

                self.cat_frames.append(
                    frame
                )

                print(
                    f"[END SCREEN] Cat frame "
                    f"{number} loaded."
                )

            except (
                pygame.error,
                FileNotFoundError,
            ) as error:

                print(
                    f"[END SCREEN] Cat frame "
                    f"{number} could not be loaded: "
                    f"{error}"
                )

        print(
            "[END SCREEN] Total cat frames loaded:",
            len(self.cat_frames),
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.running = True

        self.result = None

        self.phase = 0

        self.phase_timer = 0.0

        self.elapsed = 0.0

        self.cat_frame_index = 0

        self.cat_frame_timer = 0.0

    # ========================================================
    # RUN
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

            # ------------------------------------------------
            # DELTA TIME
            # ------------------------------------------------

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

            self.update(
                dt
            )

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

        # Buttons are only active once
        # final statistics appear.

        if self.phase < 3:

            return

        # ----------------------------------------------------
        # PLAY AGAIN
        # ----------------------------------------------------

        if self.play_again_rect.collidepoint(
            mouse_pos
        ):

            self.result = (
                "play_again"
            )

            self.running = False

            return

        # ----------------------------------------------------
        # MAIN MENU
        # ----------------------------------------------------

        if self.main_menu_rect.collidepoint(
            mouse_pos
        ):

            self.result = (
                "main_menu"
            )

            self.running = False

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt,
    ):

        # ====================================================
        # CAT WAVE ANIMATION
        # ====================================================

        if (
            self.phase >= 1
            and self.cat_frames
        ):

            self.cat_frame_timer += dt

            if (
                self.cat_frame_timer
                >= self.cat_frame_speed
            ):

                self.cat_frame_timer -= (
                    self.cat_frame_speed
                )

                self.cat_frame_index += 1

                if (
                    self.cat_frame_index
                    >= len(
                        self.cat_frames
                    )
                ):

                    self.cat_frame_index = 0

        # ====================================================
        # ENDING PHASES
        # ====================================================

        # ----------------------------------------------------
        # PHASE 0
        # ----------------------------------------------------

        if self.phase == 0:

            if self.phase_timer >= 2.5:

                self.phase = 1

                self.phase_timer = 0.0

        # ----------------------------------------------------
        # PHASE 1
        # ----------------------------------------------------

        elif self.phase == 1:

            if self.phase_timer >= 3.5:

                self.phase = 2

                self.phase_timer = 0.0

        # ----------------------------------------------------
        # PHASE 2
        # ----------------------------------------------------

        elif self.phase == 2:

            if self.phase_timer >= 2.0:

                self.phase = 3

                self.phase_timer = 0.0

        # ----------------------------------------------------
        # PHASE 3
        # ----------------------------------------------------

        elif self.phase == 3:

            # Final screen remains open.

            pass

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    def draw_background(
        self,
    ):

        # ----------------------------------------------------
        # BACKGROUND ART
        # ----------------------------------------------------

        self.screen.blit(
            self.background,
            (
                0,
                0,
            ),
        )

        # ----------------------------------------------------
        # DARK OVERLAY
        # ----------------------------------------------------
        #
        # Makes the background slightly darker so the
        # animated cat and UI stand out clearly.
        #

        overlay = pygame.Surface(
            (
                self.width,
                self.height,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (
                4,
                5,
                18,
                72,
            )
        )

        self.screen.blit(
            overlay,
            (
                0,
                0,
            ),
        )

    # ========================================================
    # DRAW TOP TITLE
    # ========================================================

    def draw_title(
        self,
    ):

        heading = self.font_medium.render(
            "CYBERPUNK CAFÉ",
            True,
            self.cyan,
        )

        heading_rect = (
            heading.get_rect(
                center=(
                    self.width // 2,
                    55,
                )
            )
        )

        self.screen.blit(
            heading,
            heading_rect,
        )

        # ----------------------------------------------------
        # NEON LINE
        # ----------------------------------------------------

        pygame.draw.line(
            self.screen,
            self.purple,
            (
                385,
                82,
            ),
            (
                895,
                82,
            ),
            2,
        )

    # ========================================================
    # DRAW CLOSING MESSAGE
    # ========================================================

    def draw_closing_message(
        self,
    ):

        if self.phase != 0:

            return

        title = self.font_title.render(
            "THE LAST ORDER HAS BEEN SERVED...",
            True,
            self.white,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    self.width // 2,
                    135,
                )
            ),
        )

        subtitle = self.font_small.render(
            "The café is closing for tonight.",
            True,
            self.grey,
        )

        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    self.width // 2,
                    175,
                )
            ),
        )

    # ========================================================
    # DRAW CAT
    # ========================================================

    def draw_cat(
        self,
    ):

        if not self.cat_frames:

            return

        # ----------------------------------------------------
        # CURRENT FRAME
        # ----------------------------------------------------

        frame = self.cat_frames[
            self.cat_frame_index
        ]

        # ----------------------------------------------------
        # SMALL FLOATING MOTION
        # ----------------------------------------------------

        bob = int(
            math.sin(
                self.elapsed * 2.5
            ) * 4
        )

        x = (
            self.cat_position[0]
            - frame.get_width() // 2
        )

        y = (
            self.cat_position[1]
            - frame.get_height() // 2
            + bob
        )

        # ----------------------------------------------------
        # SOFT CYAN GLOW
        # ----------------------------------------------------

        glow_surface = pygame.Surface(
            (
                frame.get_width() + 40,
                frame.get_height() + 40,
            ),
            pygame.SRCALPHA,
        )

        glow_alpha = int(
            30
            + (
                math.sin(
                    self.elapsed * 3
                )
                + 1
            )
            * 15
        )

        pygame.draw.ellipse(
            glow_surface,
            (
                75,
                225,
                255,
                glow_alpha,
            ),
            glow_surface.get_rect(),
        )

        self.screen.blit(
            glow_surface,
            (
                x - 20,
                y - 20,
            ),
        )

        # ----------------------------------------------------
        # CAT
        # ----------------------------------------------------

        self.screen.blit(
            frame,
            (
                x,
                y,
            ),
        )

    # ========================================================
    # DRAW BYEEEE BUBBLE
    # ========================================================

    def draw_bye_bubble(
        self,
    ):

        if self.phase < 1:

            return

        # ----------------------------------------------------
        # GENTLE APPEAR ANIMATION
        # ----------------------------------------------------

        progress = min(
            self.phase_timer / 0.7,
            1.0,
        )

        bubble_width = int(
            285
            * (
                0.85
                + 0.15 * progress
            )
        )

        bubble_height = int(
            82
            * (
                0.85
                + 0.15 * progress
            )
        )

        bubble_x = 85

        bubble_y = 205

        bubble = pygame.Rect(
            bubble_x,
            bubble_y,
            bubble_width,
            bubble_height,
        )

        # ----------------------------------------------------
        # BUBBLE
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            (
                15,
                17,
                38,
            ),
            bubble,
            border_radius=24,
        )

        pygame.draw.rect(
            self.screen,
            self.pink,
            bubble,
            width=3,
            border_radius=24,
        )

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        text = self.font_large.render(
            "BYEEEE!!",
            True,
            self.white,
        )

        self.screen.blit(
            text,
            text.get_rect(
                center=bubble.center
            ),
        )

        # ----------------------------------------------------
        # BUBBLE TAIL
        # ----------------------------------------------------

        pygame.draw.polygon(
            self.screen,
            (
                15,
                17,
                38,
            ),
            [
                (
                    bubble.centerx - 12,
                    bubble.bottom - 2,
                ),
                (
                    bubble.centerx + 10,
                    bubble.bottom - 2,
                ),
                (
                    bubble.centerx - 2,
                    bubble.bottom + 22,
                ),
            ],
        )

    # ========================================================
    # DRAW THANK YOU
    # ========================================================

    def draw_thank_you(
        self,
    ):

        if self.phase < 2:

            return

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
                    125,
                )
            ),
        )

        subtitle = self.font_small.render(
            "See you again at Cyberpunk Café!",
            True,
            self.white,
        )

        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    self.width // 2,
                    165,
                )
            ),
        )

    # ========================================================
    # DRAW FINAL STATISTICS
    # ========================================================

    def draw_statistics(
        self,
    ):

        if self.phase < 3:

            return

        # ----------------------------------------------------
        # PANEL
        # ----------------------------------------------------

        panel = pygame.Rect(
            625,
            205,
            540,
            355,
        )

        # ----------------------------------------------------
        # SHADOW
        # ----------------------------------------------------

        shadow = pygame.Surface(
            (
                panel.width + 18,
                panel.height + 18,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            shadow,
            (
                0,
                0,
                0,
                125,
            ),
            shadow.get_rect(),
            border_radius=22,
        )

        self.screen.blit(
            shadow,
            (
                panel.x - 9,
                panel.y + 8,
            ),
        )

        # ----------------------------------------------------
        # MAIN PANEL
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            self.panel,
            panel,
            border_radius=22,
        )

        pygame.draw.rect(
            self.screen,
            self.purple,
            panel,
            width=2,
            border_radius=22,
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = self.font_large.render(
            "FINAL CAFÉ STATISTICS",
            True,
            self.gold,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    panel.centerx,
                    panel.y + 40,
                )
            ),
        )

        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        rows = [
            (
                "Successful Drinks",
                f"{self.successful_drinks} / 21",
                self.pink,
            ),
            (
                "Final Level",
                f"Level {self.final_level}",
                self.cyan,
            ),
            (
                "Total XP",
                str(self.final_xp),
                self.purple,
            ),
            (
                "Credits Earned",
                f"${self.final_credits}",
                self.gold,
            ),
        ]

        start_y = (
            panel.y + 88
        )

        for index, (
            label,
            value,
            accent,
        ) in enumerate(rows):

            y = (
                start_y
                + index * 60
            )

            # Divider.

            pygame.draw.line(
                self.screen,
                (
                    55,
                    60,
                    90,
                ),
                (
                    panel.x + 35,
                    y + 42,
                ),
                (
                    panel.right - 35,
                    y + 42,
                ),
                1,
            )

            # Label.

            label_surface = (
                self.font_small.render(
                    label,
                    True,
                    self.grey,
                )
            )

            self.screen.blit(
                label_surface,
                (
                    panel.x + 35,
                    y,
                ),
            )

            # Value.

            value_surface = (
                self.font_medium.render(
                    value,
                    True,
                    accent,
                )
            )

            self.screen.blit(
                value_surface,
                value_surface.get_rect(
                    midright=(
                        panel.right - 35,
                        y + 10,
                    )
                ),
            )

    # ========================================================
    # DRAW BUTTON
    # ========================================================

    def draw_button(
        self,
        rect,
        label,
        accent,
        hovered,
    ):

        if hovered:

            fill = (
                34,
                27,
                62,
            )

        else:

            fill = (
                15,
                18,
                40,
            )

        # ----------------------------------------------------
        # BUTTON
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=15,
        )

        pygame.draw.rect(
            self.screen,
            accent,
            rect,
            width=3,
            border_radius=15,
        )

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        text = self.font_button.render(
            label,
            True,
            self.white,
        )

        self.screen.blit(
            text,
            text.get_rect(
                center=rect.center
            ),
        )

    # ========================================================
    # DRAW BUTTONS
    # ========================================================

    def draw_buttons(
        self,
    ):

        if self.phase < 3:

            return

        mouse_pos = (
            pygame.mouse.get_pos()
        )

        self.draw_button(
            self.play_again_rect,
            "PLAY AGAIN",
            self.pink,
            self.play_again_rect.collidepoint(
                mouse_pos
            ),
        )

        self.draw_button(
            self.main_menu_rect,
            "MAIN MENU",
            self.cyan,
            self.main_menu_rect.collidepoint(
                mouse_pos
            ),
        )

    # ========================================================
    # DRAW EVERYTHING
    # ========================================================

    def draw(
        self,
    ):

        # Background first.

        self.draw_background()

        # Top title.

        self.draw_title()

        # Initial closing message.

        self.draw_closing_message()

        # Cat and speech bubble.

        if self.phase >= 1:

            self.draw_cat()

            self.draw_bye_bubble()

        # Thank-you message.

        self.draw_thank_you()

        # Final statistics.

        self.draw_statistics()

        # Buttons.

        self.draw_buttons()
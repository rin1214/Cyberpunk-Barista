import pygame
import os


class StartScreen:
    """
    Cyberpunk Café - Start Screen

    This class controls:
    - Background image
    - Player name input
    - Enter Café button
    - Menu button
    - Audio settings menu
    - Music volume slider
    - Mute button
    - Keyboard and mouse interaction
    """

    # ---------------------------------------------------------
    # GAME RESOLUTION
    # ---------------------------------------------------------

    WIDTH = 1280
    HEIGHT = 720

    # ---------------------------------------------------------
    # COLOURS
    # ---------------------------------------------------------

    WHITE = (245, 245, 255)

    DARK_PANEL = (10, 15, 35)
    DARK_INPUT = (8, 18, 38)

    CYAN = (0, 220, 255)
    PINK = (220, 70, 240)
    BRIGHT_PINK = (255, 80, 220)

    GOLD = (255, 210, 90)
    GOLD_HOVER = (255, 190, 60)

    GREY = (80, 85, 110)

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(self, screen):

        # Store the Pygame screen
        self.screen = screen

        # Make sure Pygame's font system is available
        pygame.font.init()

        # -----------------------------------------------------
        # GAME STATE
        # -----------------------------------------------------

        self.running = True

        # Player's name
        self.name = ""

        # Is the player currently typing?
        self.name_active = False

        # Is the settings menu open?
        self.show_menu = False

        # Is audio muted?
        self.muted = False

        # Music volume
        # 0.0 = silent
        # 1.0 = maximum
        self.music_volume = 0.35

        # This will eventually contain the player's name
        # when they successfully start the game.
        self.player_name = None

        # -----------------------------------------------------
        # LOAD BACKGROUND
        # -----------------------------------------------------

        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )

        background_path = os.path.join(
            base_path,
            "assets",
            "mahirah",
            "start",
            "start_bg.png"
        )

        # Check that the image exists before trying to load it
        if not os.path.exists(background_path):

            raise FileNotFoundError(
                "\nCyberpunk Café start-screen background "
                "could not be found.\n\n"
                "Expected location:\n"
                f"{background_path}\n"
            )

        # Load the background
        self.background = pygame.image.load(
            background_path
        ).convert()

        # Scale background to our 1280x720 game resolution
        self.background = pygame.transform.scale(
            self.background,
            (self.WIDTH, self.HEIGHT)
        )

        # -----------------------------------------------------
        # FONTS
        # -----------------------------------------------------

        self.title_font = pygame.font.SysFont(
            "arial",
            42,
            bold=True
        )

        self.normal_font = pygame.font.SysFont(
            "arial",
            24
        )

        self.button_font = pygame.font.SysFont(
            "arial",
            26,
            bold=True
        )

        self.small_font = pygame.font.SysFont(
            "arial",
            18
        )

        # -----------------------------------------------------
        # NAME INPUT BOX
        # -----------------------------------------------------

        self.name_box = pygame.Rect(
            555,
            530,
            525,
            78
        )

        # -----------------------------------------------------
        # ENTER CAFÉ BUTTON
        # -----------------------------------------------------

        self.enter_button = pygame.Rect(
            570,
            645,
            510,
            72
        )

        # -----------------------------------------------------
        # MENU BUTTON
        # -----------------------------------------------------

        self.menu_button = pygame.Rect(
            1100,
            22,
            150,
            55
        )

        # -----------------------------------------------------
        # AUDIO MENU
        # -----------------------------------------------------

        self.menu_panel = pygame.Rect(
            380,
            155,
            520,
            410
        )

        self.close_menu_button = pygame.Rect(
            840,
            175,
            42,
            42
        )

        self.mute_button = pygame.Rect(
            470,
            455,
            160,
            48
        )

        self.volume_bar = pygame.Rect(
            470,
            350,
            340,
            12
        )

    # =========================================================
    # MAIN START SCREEN LOOP
    # =========================================================

    def run(self):

        # Clock controls our frame rate
        clock = pygame.time.Clock()

        while self.running:

            # -------------------------------------------------
            # PROCESS EVENTS
            # -------------------------------------------------

            for event in pygame.event.get():

                # Player closes the game window
                if event.type == pygame.QUIT:

                    self.running = False

                    return None

                # Send event to our event handler
                self.handle_event(event)

            # -------------------------------------------------
            # DRAW EVERYTHING
            # -------------------------------------------------

            self.draw()

            # Update the display
            pygame.display.flip()

            # Limit the screen to 60 FPS
            clock.tick(60)

        # Return the player's name
        return self.player_name

    # =========================================================
    # EVENT HANDLER
    # =========================================================

    def handle_event(self, event):

        # =====================================================
        # IF AUDIO MENU IS OPEN
        # =====================================================

        if self.show_menu:

            self.handle_menu_event(event)

            return

        # =====================================================
        # MOUSE CLICK
        # =====================================================

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_position = event.pos

            # -------------------------------------------------
            # NAME BOX
            # -------------------------------------------------

            if self.name_box.collidepoint(
                mouse_position
            ):

                self.name_active = True

            else:

                self.name_active = False

            # -------------------------------------------------
            # ENTER CAFÉ
            # -------------------------------------------------

            if self.enter_button.collidepoint(
                mouse_position
            ):

                self.start_game()

            # -------------------------------------------------
            # MENU
            # -------------------------------------------------

            if self.menu_button.collidepoint(
                mouse_position
            ):

                self.show_menu = True

        # =====================================================
        # KEYBOARD
        # =====================================================

        if event.type == pygame.KEYDOWN:

            # Only accept typing when the name box is active
            if self.name_active:

                # -------------------------------------------------
                # BACKSPACE
                # -------------------------------------------------

                if event.key == pygame.K_BACKSPACE:

                    self.name = self.name[:-1]

                # -------------------------------------------------
                # ENTER KEY
                # -------------------------------------------------

                elif event.key == pygame.K_RETURN:

                    self.start_game()

                # -------------------------------------------------
                # NORMAL CHARACTER
                # -------------------------------------------------

                else:

                    # Maximum name length
                    if len(self.name) < 18:

                        # Add typed character
                        self.name += event.unicode

    # =========================================================
    # START THE GAME
    # =========================================================

    def start_game(self):

        # Remove unnecessary spaces
        cleaned_name = self.name.strip()

        # Don't allow an empty name
        if cleaned_name == "":

            return

        # Store the player's name
        self.player_name = cleaned_name

        # Stop the start-screen loop
        self.running = False

    # =========================================================
    # MENU EVENT HANDLER
    # =========================================================

    def handle_menu_event(self, event):

        # =====================================================
        # MOUSE CLICK
        # =====================================================

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_position = event.pos

            # -------------------------------------------------
            # CLOSE MENU
            # -------------------------------------------------

            if self.close_menu_button.collidepoint(
                mouse_position
            ):

                self.show_menu = False

            # -------------------------------------------------
            # MUTE
            # -------------------------------------------------

            elif self.mute_button.collidepoint(
                mouse_position
            ):

                self.muted = not self.muted

            # -------------------------------------------------
            # MUSIC VOLUME
            # -------------------------------------------------

            elif self.volume_bar.collidepoint(
                mouse_position
            ):

                # Calculate where the mouse is inside the bar
                relative_x = (
                    mouse_position[0]
                    - self.volume_bar.x
                )

                # Convert that position into 0.0 - 1.0
                self.music_volume = max(
                    0.0,
                    min(
                        1.0,
                        relative_x
                        / self.volume_bar.width
                    )
                )

        # =====================================================
        # KEYBOARD
        # =====================================================

        if event.type == pygame.KEYDOWN:

            # ESC closes the menu
            if event.key == pygame.K_ESCAPE:

                self.show_menu = False

    # =========================================================
    # DRAW THE START SCREEN
    # =========================================================

    def draw(self):

        # -----------------------------------------------------
        # BACKGROUND
        # -----------------------------------------------------

        self.screen.blit(
            self.background,
            (0, 0)
        )

        # -----------------------------------------------------
        # INTERACTIVE UI
        # -----------------------------------------------------

        self.draw_interactive_ui()

        # -----------------------------------------------------
        # MENU
        # -----------------------------------------------------

        if self.show_menu:

            self.draw_menu()

    # =========================================================
    # DRAW INTERACTIVE UI
    # =========================================================

    def draw_interactive_ui(self):

        mouse_position = pygame.mouse.get_pos()

        # =====================================================
        # NAME INPUT BOX
        # =====================================================

        if self.name_active:

            border_color = self.CYAN

        else:

            border_color = self.PINK

        # Input background
        pygame.draw.rect(
            self.screen,
            self.DARK_INPUT,
            self.name_box,
            border_radius=12
        )

        # Input border
        pygame.draw.rect(
            self.screen,
            border_color,
            self.name_box,
            width=3,
            border_radius=12
        )

        # -----------------------------------------------------
        # NAME TEXT
        # -----------------------------------------------------

        if self.name:

            name_text = self.name

        else:

            name_text = "Enter your name..."

        name_surface = self.normal_font.render(
            name_text,
            True,
            self.WHITE
        )

        self.screen.blit(
            name_surface,
            (
                self.name_box.x + 55,
                self.name_box.y + 25
            )
        )

        # =====================================================
        # ENTER CAFÉ BUTTON
        # =====================================================

        hovering_enter = self.enter_button.collidepoint(
            mouse_position
        )

        if hovering_enter:

            button_border = self.GOLD_HOVER

        else:

            button_border = self.GOLD

        # Button background
        pygame.draw.rect(
            self.screen,
            (12, 16, 35),
            self.enter_button,
            border_radius=18
        )

        # Button border
        pygame.draw.rect(
            self.screen,
            button_border,
            self.enter_button,
            width=4,
            border_radius=18
        )

        # Button text
        enter_text = self.button_font.render(
            "ENTER THE CAFÉ  >>",
            True,
            self.WHITE
        )

        enter_text_rect = enter_text.get_rect(
            center=self.enter_button.center
        )

        self.screen.blit(
            enter_text,
            enter_text_rect
        )

        # =====================================================
        # MENU BUTTON
        # =====================================================

        hovering_menu = self.menu_button.collidepoint(
            mouse_position
        )

        if hovering_menu:

            menu_border = self.BRIGHT_PINK

        else:

            menu_border = self.CYAN

        # Menu background
        pygame.draw.rect(
            self.screen,
            (10, 18, 38),
            self.menu_button,
            border_radius=12
        )

        # Menu border
        pygame.draw.rect(
            self.screen,
            menu_border,
            self.menu_button,
            width=3,
            border_radius=12
        )

        # Menu text
        menu_text = self.normal_font.render(
            "MENU",
            True,
            self.WHITE
        )

        menu_text_rect = menu_text.get_rect(
            center=self.menu_button.center
        )

        self.screen.blit(
            menu_text,
            menu_text_rect
        )

    # =========================================================
    # DRAW AUDIO MENU
    # =========================================================

    def draw_menu(self):

        # -----------------------------------------------------
        # DARK SCREEN OVERLAY
        # -----------------------------------------------------

        overlay = pygame.Surface(
            (self.WIDTH, self.HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 20, 160)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        # -----------------------------------------------------
        # MENU PANEL
        # -----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            self.DARK_PANEL,
            self.menu_panel,
            border_radius=18
        )

        pygame.draw.rect(
            self.screen,
            self.PINK,
            self.menu_panel,
            width=3,
            border_radius=18
        )

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        title = self.title_font.render(
            "AUDIO SETTINGS",
            True,
            self.WHITE
        )

        title_rect = title.get_rect(
            centerx=self.menu_panel.centerx,
            y=self.menu_panel.y + 35
        )

        self.screen.blit(
            title,
            title_rect
        )

        # -----------------------------------------------------
        # MUSIC LABEL
        # -----------------------------------------------------

        music_label = self.normal_font.render(
            "MUSIC VOLUME",
            True,
            self.WHITE
        )

        self.screen.blit(
            music_label,
            (
                self.volume_bar.x,
                self.volume_bar.y - 45
            )
        )

        # -----------------------------------------------------
        # VOLUME BAR
        # -----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            self.GREY,
            self.volume_bar,
            border_radius=6
        )

        # Calculate filled portion
        fill_width = int(
            self.volume_bar.width
            * self.music_volume
        )

        if fill_width > 0:

            fill_rect = pygame.Rect(
                self.volume_bar.x,
                self.volume_bar.y,
                fill_width,
                self.volume_bar.height
            )

            pygame.draw.rect(
                self.screen,
                self.PINK,
                fill_rect,
                border_radius=6
            )

        # -----------------------------------------------------
        # VOLUME PERCENTAGE
        # -----------------------------------------------------

        volume_percentage = int(
            self.music_volume * 100
        )

        volume_text = self.small_font.render(
            f"{volume_percentage}%",
            True,
            self.WHITE
        )

        self.screen.blit(
            volume_text,
            (
                self.volume_bar.right + 15,
                self.volume_bar.y - 7
            )
        )

        # -----------------------------------------------------
        # MUTE BUTTON
        # -----------------------------------------------------

        if self.muted:

            mute_text = "UNMUTE"

        else:

            mute_text = "MUTE"

        pygame.draw.rect(
            self.screen,
            (15, 20, 40),
            self.mute_button,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            self.CYAN,
            self.mute_button,
            width=2,
            border_radius=10
        )

        mute_surface = self.normal_font.render(
            mute_text,
            True,
            self.WHITE
        )

        mute_rect = mute_surface.get_rect(
            center=self.mute_button.center
        )

        self.screen.blit(
            mute_surface,
            mute_rect
        )

        # -----------------------------------------------------
        # CLOSE BUTTON
        # -----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            (15, 20, 40),
            self.close_menu_button,
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            self.BRIGHT_PINK,
            self.close_menu_button,
            width=2,
            border_radius=8
        )

        close_surface = self.normal_font.render(
            "X",
            True,
            self.WHITE
        )

        close_rect = close_surface.get_rect(
            center=self.close_menu_button.center
        )

        self.screen.blit(
            close_surface,
            close_rect
        )


# =============================================================
# STANDALONE TEST
# =============================================================
#
# This section only runs when we directly execute:
#
#     python start_screen.py
#
# Later, main.py can import StartScreen without automatically
# running this section.
# =============================================================

if __name__ == "__main__":

    # Initialize Pygame
    pygame.init()

    # Create the 1280 x 720 window
    screen = pygame.display.set_mode(
        (
            StartScreen.WIDTH,
            StartScreen.HEIGHT
        )
    )

    # Window title
    pygame.display.set_caption(
        "Cyberpunk Café"
    )

    # Create our start screen
    start_screen = StartScreen(
        screen
    )

    # Run the start screen
    player_name = start_screen.run()

    # Shut down Pygame after the screen closes
    pygame.quit()

    # Show the result in the terminal
    print(
        "Player name:",
        player_name
    )
import pygame


class MixingStation:
    """
    The visual drink mixing station.

    This class is responsible for:
    - Displaying the drink controls
    - Creating clickable button areas
    - Showing current drink values
    - Providing a visually clear mixing interface
    """

    def __init__(self, drink):
        """
        Create the mixing station.

        Parameters:
            drink: The Drink object currently being prepared.
        """

        # Store the Drink object.
        # The station reads and later changes the values inside this object.
        self.drink = drink

        # --------------------------------------------------
        # FONTS
        # --------------------------------------------------

        # Arial is used because it is easy to read.
        self.title_font = pygame.font.SysFont(
            "arial",
            28,
            bold=True
        )

        self.label_font = pygame.font.SysFont(
            "arial",
            20,
            bold=True
        )

        self.value_font = pygame.font.SysFont(
            "arial",
            24,
            bold=True
        )

        self.button_font = pygame.font.SysFont(
            "arial",
            22,
            bold=True
        )

        self.serve_font = pygame.font.SysFont(
            "arial",
            20,
            bold=True
        )

        # --------------------------------------------------
        # PASTEL COLOR PALETTE
        # --------------------------------------------------

        # Background colors
        self.panel_color = (36, 39, 58)
        self.panel_inner_color = (30, 33, 48)

        # Soft pastel border
        self.border_color = (137, 211, 255)

        # Text colors
        self.title_color = (174, 224, 255)
        self.label_color = (225, 228, 240)
        self.value_color = (255, 255, 255)

        # Pastel button colors
        self.minus_color = (255, 174, 190)
        self.minus_hover = (255, 194, 207)

        self.plus_color = (160, 235, 203)
        self.plus_hover = (185, 245, 220)

        self.serve_color = (218, 166, 230)
        self.serve_hover = (234, 190, 244)

        # Dark text placed on bright buttons
        self.button_text_color = (40, 35, 50)

        # Value box border
        self.value_border_color = (177, 239, 221)

        # --------------------------------------------------
        # MAIN PANEL
        # --------------------------------------------------

        # A larger panel gives the controls enough space.
        self.panel_rect = pygame.Rect(
            455,
            55,
            310,
            510
        )

        # --------------------------------------------------
        # SWEETNESS BUTTONS
        # --------------------------------------------------

        self.sweetness_minus = pygame.Rect(
            485,
            175,
            60,
            50
        )

        self.sweetness_plus = pygame.Rect(
            675,
            175,
            60,
            50
        )

        # --------------------------------------------------
        # CAFFEINE BUTTONS
        # --------------------------------------------------

        self.caffeine_minus = pygame.Rect(
            485,
            290,
            60,
            50
        )

        self.caffeine_plus = pygame.Rect(
            675,
            290,
            60,
            50
        )

        # --------------------------------------------------
        # TEMPERATURE BUTTONS
        # --------------------------------------------------

        self.temperature_minus = pygame.Rect(
            485,
            405,
            60,
            50
        )

        self.temperature_plus = pygame.Rect(
            675,
            405,
            60,
            50
        )

        # --------------------------------------------------
        # VALUE BOXES
        # --------------------------------------------------

        self.sweetness_value_box = pygame.Rect(
            565,
            175,
            90,
            50
        )

        self.caffeine_value_box = pygame.Rect(
            565,
            290,
            90,
            50
        )

        self.temperature_value_box = pygame.Rect(
            565,
            405,
            90,
            50
        )

        # --------------------------------------------------
        # SERVE BUTTON
        # --------------------------------------------------

        self.serve_button = pygame.Rect(
            485,
            490,
            250,
            55
        )

    # ==================================================
    # DRAW THE ENTIRE MIXING STATION
    # ==================================================

    def draw(self, screen):
        """
        Draw the entire drink mixing station.
        """

        # Draw the main background panel.
        pygame.draw.rect(
            screen,
            self.panel_color,
            self.panel_rect,
            border_radius=20
        )

        # Draw a soft pastel border around the panel.
        pygame.draw.rect(
            screen,
            self.border_color,
            self.panel_rect,
            width=2,
            border_radius=20
        )

        # Draw title.
        self.draw_title(screen)

        # Draw each drink parameter.
        self.draw_parameter(
            screen,
            "SWEETNESS",
            self.drink.sweetness,
            130,
            self.sweetness_minus,
            self.sweetness_value_box,
            self.sweetness_plus
        )

        self.draw_parameter(
            screen,
            "CAFFEINE",
            self.drink.caffeine,
            245,
            self.caffeine_minus,
            self.caffeine_value_box,
            self.caffeine_plus
        )

        self.draw_parameter(
            screen,
            "TEMPERATURE",
            self.drink.temperature,
            360,
            self.temperature_minus,
            self.temperature_value_box,
            self.temperature_plus
        )

        # Draw the serve button.
        self.draw_serve_button(screen)

    # ==================================================
    # DRAW TITLE
    # ==================================================

    def draw_title(self, screen):
        """
        Draw the station title.
        """

        title_surface = self.title_font.render(
            "DRINK MIXING",
            True,
            self.title_color
        )

        title_rect = title_surface.get_rect(
            center=(
                self.panel_rect.centerx,
                90
            )
        )

        screen.blit(
            title_surface,
            title_rect
        )

        # Draw a smaller subtitle.
        subtitle_font = pygame.font.SysFont(
            "arial",
            13
        )

        subtitle_surface = subtitle_font.render(
            "CUSTOMIZE YOUR RECIPE",
            True,
            (165, 170, 190)
        )

        subtitle_rect = subtitle_surface.get_rect(
            center=(
                self.panel_rect.centerx,
                120
            )
        )

        screen.blit(
            subtitle_surface,
            subtitle_rect
        )

    # ==================================================
    # DRAW ONE PARAMETER
    # ==================================================

    def draw_parameter(
        self,
        screen,
        label,
        value,
        label_y,
        minus_button,
        value_box,
        plus_button
    ):
        """
        Draw one complete drink control.

        Each control contains:

        Parameter name
             ↓
        [ - ]  [ VALUE ]  [ + ]
        """

        # Draw parameter name.
        label_surface = self.label_font.render(
            label,
            True,
            self.label_color
        )

        screen.blit(
            label_surface,
            (485, label_y)
        )

        # Draw a subtle separator line.
        line_y = label_y + 32

        pygame.draw.line(
            screen,
            (65, 70, 95),
            (485, line_y),
            (735, line_y),
            1
        )

        # Draw the decrease button.
        self.draw_button(
            screen,
            minus_button,
            "-",
            self.minus_color,
            self.minus_hover
        )

        # Draw the value box.
        self.draw_value_box(
            screen,
            value_box,
            value
        )

        # Draw the increase button.
        self.draw_button(
            screen,
            plus_button,
            "+",
            self.plus_color,
            self.plus_hover
        )

    # ==================================================
    # DRAW VALUE BOX
    # ==================================================

    def draw_value_box(
        self,
        screen,
        rect,
        value
    ):
        """
        Draw the numerical value box.
        """

        # Dark inner background.
        pygame.draw.rect(
            screen,
            self.panel_inner_color,
            rect,
            border_radius=10
        )

        # Pastel border.
        pygame.draw.rect(
            screen,
            self.value_border_color,
            rect,
            width=2,
            border_radius=10
        )

        # Convert the number into text.
        value_surface = self.value_font.render(
            str(value),
            True,
            self.value_color
        )

        # Centre the number.
        value_rect = value_surface.get_rect(
            center=rect.center
        )

        screen.blit(
            value_surface,
            value_rect
        )

    # ==================================================
    # DRAW NORMAL BUTTON
    # ==================================================

    def draw_button(
        self,
        screen,
        rect,
        text,
        normal_color,
        hover_color
    ):
        """
        Draw a button.

        The color becomes slightly lighter
        when the player's mouse is hovering over it.
        """

        # Get current mouse position.
        mouse_position = pygame.mouse.get_pos()

        # Check whether the mouse is touching this button.
        if rect.collidepoint(mouse_position):

            # Use lighter hover color.
            button_color = hover_color

        else:

            # Use normal color.
            button_color = normal_color

        # Draw button background.
        pygame.draw.rect(
            screen,
            button_color,
            rect,
            border_radius=12
        )

        # Draw button text.
        text_surface = self.button_font.render(
            text,
            True,
            self.button_text_color
        )

        # Centre the text.
        text_rect = text_surface.get_rect(
            center=rect.center
        )

        screen.blit(
            text_surface,
            text_rect
        )

    # ==================================================
    # DRAW SERVE BUTTON
    # ==================================================

    def draw_serve_button(self, screen):
        """
        Draw the main SERVE DRINK button.
        """

        mouse_position = pygame.mouse.get_pos()

        # Check whether the mouse is hovering.
        if self.serve_button.collidepoint(mouse_position):

            button_color = self.serve_hover

        else:

            button_color = self.serve_color

        # Draw button.
        pygame.draw.rect(
            screen,
            button_color,
            self.serve_button,
            border_radius=12
        )

        # Draw button border.
        pygame.draw.rect(
            screen,
            (245, 225, 250),
            self.serve_button,
            width=2,
            border_radius=12
        )

        # Create button text.
        text_surface = self.serve_font.render(
            "SERVE DRINK",
            True,
            self.button_text_color
        )

        text_rect = text_surface.get_rect(
            center=self.serve_button.center
        )

        screen.blit(
            text_surface,
            text_rect
        )
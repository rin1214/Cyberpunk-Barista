import pygame


class MixingStation:
    """
    Interactive Drink Mixing Station.

    This class controls:
    - The visual mixing station
    - Sweetness controls
    - Caffeine controls
    - Temperature controls
    - Mouse interaction
    - Serve button
    """

    def __init__(self, drink):

        # Store the Drink object.
        # This allows the station to read and modify
        # the actual drink being prepared.
        self.drink = drink

        # ==================================================
        # FONTS
        # ==================================================

        self.title_font = pygame.font.SysFont(
            "arial",
            28,
            bold=True
        )

        self.subtitle_font = pygame.font.SysFont(
            "arial",
            13
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

        # ==================================================
        # PASTEL COLOR PALETTE
        # ==================================================

        # Main panel
        self.panel_color = (36, 39, 58)

        # Inner value boxes
        self.panel_inner_color = (30, 33, 48)

        # Soft pastel blue
        self.border_color = (137, 211, 255)

        # Text
        self.title_color = (174, 224, 255)
        self.label_color = (225, 228, 240)
        self.value_color = (255, 255, 255)
        self.subtitle_color = (165, 170, 190)

        # Pastel pink
        self.minus_color = (255, 174, 190)
        self.minus_hover = (255, 194, 207)

        # Pastel mint
        self.plus_color = (160, 235, 203)
        self.plus_hover = (185, 245, 220)

        # Pastel lavender
        self.serve_color = (218, 166, 230)
        self.serve_hover = (234, 190, 244)

        # Dark text for buttons
        self.button_text_color = (40, 35, 50)

        # Value box border
        self.value_border_color = (177, 239, 221)

        # ==================================================
        # MAIN PANEL
        # ==================================================

        self.panel_rect = pygame.Rect(
            455,
            55,
            310,
            510
        )

        # ==================================================
        # SWEETNESS BUTTONS
        # ==================================================

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

        # ==================================================
        # CAFFEINE BUTTONS
        # ==================================================

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

        # ==================================================
        # TEMPERATURE BUTTONS
        # ==================================================

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

        # ==================================================
        # VALUE BOXES
        # ==================================================

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

        # ==================================================
        # SERVE BUTTON
        # ==================================================

        self.serve_button = pygame.Rect(
            485,
            490,
            250,
            55
        )

        # ==================================================
        # SERVE STATUS
        # ==================================================

        self.served = False

    # ======================================================
    # DRAW EVERYTHING
    # ======================================================

    def draw(self, screen):

        # Main station panel
        pygame.draw.rect(
            screen,
            self.panel_color,
            self.panel_rect,
            border_radius=20
        )

        # Panel border
        pygame.draw.rect(
            screen,
            self.border_color,
            self.panel_rect,
            width=2,
            border_radius=20
        )

        # Title
        self.draw_title(screen)

        # Sweetness
        self.draw_parameter(
            screen,
            "SWEETNESS",
            self.drink.sweetness,
            145,
            self.sweetness_minus,
            self.sweetness_value_box,
            self.sweetness_plus
        )

        # Caffeine
        self.draw_parameter(
            screen,
            "CAFFEINE",
            self.drink.caffeine,
            260,
            self.caffeine_minus,
            self.caffeine_value_box,
            self.caffeine_plus
        )

        # Temperature
        self.draw_parameter(
            screen,
            "TEMPERATURE",
            self.drink.temperature,
            375,
            self.temperature_minus,
            self.temperature_value_box,
            self.temperature_plus
        )

        # Serve button
        self.draw_serve_button(screen)

    # ======================================================
    # DRAW TITLE
    # ======================================================

    def draw_title(self, screen):

        title_surface = self.title_font.render(
            "DRINK MIXING",
            True,
            self.title_color
        )

        title_rect = title_surface.get_rect(
            center=(
                self.panel_rect.centerx,
                88
            )
        )

        screen.blit(
            title_surface,
            title_rect
        )

        subtitle_surface = self.subtitle_font.render(
            "CUSTOMIZE YOUR RECIPE",
            True,
            self.subtitle_color
        )

        subtitle_rect = subtitle_surface.get_rect(
            center=(
                self.panel_rect.centerx,
                118
            )
        )

        screen.blit(
            subtitle_surface,
            subtitle_rect
        )

    # ======================================================
    # DRAW PARAMETER
    # ======================================================

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

        # Parameter name
        label_surface = self.label_font.render(
            label,
            True,
            self.label_color
        )

        screen.blit(
            label_surface,
            (485, label_y)
        )

        # Separator
        line_y = label_y + 32

        pygame.draw.line(
            screen,
            (65, 70, 95),
            (485, line_y),
            (735, line_y),
            1
        )

        # Minus button
        self.draw_button(
            screen,
            minus_button,
            "-",
            self.minus_color,
            self.minus_hover
        )

        # Number box
        self.draw_value_box(
            screen,
            value_box,
            value
        )

        # Plus button
        self.draw_button(
            screen,
            plus_button,
            "+",
            self.plus_color,
            self.plus_hover
        )

    # ======================================================
    # DRAW VALUE BOX
    # ======================================================

    def draw_value_box(
        self,
        screen,
        rect,
        value
    ):

        pygame.draw.rect(
            screen,
            self.panel_inner_color,
            rect,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            self.value_border_color,
            rect,
            width=2,
            border_radius=10
        )

        value_surface = self.value_font.render(
            str(value),
            True,
            self.value_color
        )

        value_rect = value_surface.get_rect(
            center=rect.center
        )

        screen.blit(
            value_surface,
            value_rect
        )

    # ======================================================
    # DRAW NORMAL BUTTON
    # ======================================================

    def draw_button(
        self,
        screen,
        rect,
        text,
        normal_color,
        hover_color
    ):

        mouse_position = pygame.mouse.get_pos()

        # Change color when mouse is over button
        if rect.collidepoint(mouse_position):
            button_color = hover_color
        else:
            button_color = normal_color

        pygame.draw.rect(
            screen,
            button_color,
            rect,
            border_radius=12
        )

        text_surface = self.button_font.render(
            text,
            True,
            self.button_text_color
        )

        text_rect = text_surface.get_rect(
            center=rect.center
        )

        screen.blit(
            text_surface,
            text_rect
        )

    # ======================================================
    # DRAW SERVE BUTTON
    # ======================================================

    def draw_serve_button(self, screen):

        mouse_position = pygame.mouse.get_pos()

        if self.serve_button.collidepoint(mouse_position):
            button_color = self.serve_hover
        else:
            button_color = self.serve_color

        pygame.draw.rect(
            screen,
            button_color,
            self.serve_button,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            (245, 225, 250),
            self.serve_button,
            width=2,
            border_radius=12
        )

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

    # ======================================================
    # HANDLE PLAYER INPUT
    # ======================================================

    def handle_event(self, event):

        # We only care about mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:

            # Only use left mouse button
            if event.button == 1:

                mouse_position = event.pos

                # ------------------------------------------
                # SWEETNESS
                # ------------------------------------------

                if self.sweetness_minus.collidepoint(
                    mouse_position
                ):

                    self.drink.decrease_sweetness()

                elif self.sweetness_plus.collidepoint(
                    mouse_position
                ):

                    self.drink.increase_sweetness()

                # ------------------------------------------
                # CAFFEINE
                # ------------------------------------------

                elif self.caffeine_minus.collidepoint(
                    mouse_position
                ):

                    self.drink.decrease_caffeine()

                elif self.caffeine_plus.collidepoint(
                    mouse_position
                ):

                    self.drink.increase_caffeine()

                # ------------------------------------------
                # TEMPERATURE
                # ------------------------------------------

                elif self.temperature_minus.collidepoint(
                    mouse_position
                ):

                    self.drink.decrease_temperature()

                elif self.temperature_plus.collidepoint(
                    mouse_position
                ):

                    self.drink.increase_temperature()

                # ------------------------------------------
                # SERVE
                # ------------------------------------------

                elif self.serve_button.collidepoint(
                    mouse_position
                ):

                    self.served = True

                    print("DRINK SERVED!")
                    print(self.drink.get_data())

    # ======================================================
    # RESET STATION
    # ======================================================

    def reset(self):

        self.drink.reset()

        self.served = False
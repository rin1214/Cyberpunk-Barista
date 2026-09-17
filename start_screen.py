import os
import math
import pygame


class StartScreen:
    """
    Cyberpunk Café - Mahirah polished start screen.

    Resolution: 1280 x 720

    Improvements in this version:
    - Audiowide support for the WELCOME, BARISTA heading.
    - Soft cyan + pink cyberpunk glow around the welcome heading.
    - Larger audio-settings header.
    - Larger, better-aligned music/SFX sliders.
    - Transparent PNG padding is trimmed automatically for UI assets.
    - PNG aspect ratios are preserved; no stretching of buttons/icons.
    - Separate Music Mute and SFX Mute controls.
    - Existing audio, name entry, hover, click and menu behaviour kept.
    - Compatible with: StartScreen(screen).run()

    FONT:
        Put Audiowide-Regular.ttf in:
            assets/fonts/Audiowide-Regular.ttf

        If the font file is not present, the game automatically falls
        back to a readable Windows/system font instead of crashing.
    """

    WIDTH = 1280
    HEIGHT = 720
    FPS = 60

    # ============================================================
    # COLORS
    # ============================================================
    BG_OVERLAY = (5, 8, 24)
    PANEL = (8, 14, 35)
    PANEL_2 = (11, 19, 46)
    CYAN = (45, 226, 255)
    BLUE = (73, 142, 255)
    PINK = (255, 55, 210)
    PURPLE = (180, 95, 255)
    WHITE = (245, 247, 255)
    SOFT_WHITE = (210, 218, 240)
    GOLD = (255, 190, 62)
    GREEN = (95, 255, 200)
    DARK = (15, 18, 35)
    MUTED = (120, 130, 160)

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # --------------------------------------------------------
        # Player state
        # --------------------------------------------------------
        self.player_name = ""
        self.name_active = False
        self.finished = False

        # --------------------------------------------------------
        # Audio state
        # --------------------------------------------------------
        self.music_volume = 0.30
        self.sfx_volume = 0.16

        self.music_muted = False
        self.sfx_muted = False
        self.audio_menu_open = False

        self.click_sound = None
        self.hover_sound = None

        self.last_hover = set()
        self.dragging_music = False
        self.dragging_sfx = False

        # --------------------------------------------------------
        # Project paths
        # --------------------------------------------------------
        self.project_root = os.path.dirname(os.path.abspath(__file__))

        self.start_root = os.path.join(
            self.project_root, "assets", "mahirah", "start"
        )
        self.ui_root = os.path.join(
            self.project_root, "assets", "mahirah", "ui"
        )
        self.audio_root = os.path.join(
            self.project_root, "assets", "mahirah", "audio"
        )
        self.font_root = os.path.join(
            self.project_root, "assets", "fonts"
        )

        # --------------------------------------------------------
        # Assets
        # --------------------------------------------------------
        self.background = None
        self.logo = None
        self.menu_asset = None
        self.menu_hover_asset = None
        self.enter_asset = None
        self.enter_hover_asset = None
        self.input_asset = None
        self.input_active_asset = None

        self.music_icon = None
        self.music_icon_off = None
        self.sound_icon = None
        self.sound_icon_off = None

        self.audio_header_asset = None
        self.close_asset = None
        self.close_hover_asset = None
        self.mute_asset = None
        self.mute_hover_asset = None
        self.slider_music_asset = None
        self.slider_sound_asset = None
        self.slider_fill_asset = None
        self.slider_knob_asset = None
        self.menu_panel_asset = None

        self.load_assets()
        self.create_fonts()
        self.create_layout()
        self.setup_audio()

    # ============================================================
    # ASSET HELPERS
    # ============================================================

    def find_file(self, folders, names):
        for folder in folders:
            for name in names:
                path = os.path.join(folder, name)
                if os.path.isfile(path):
                    return path
        return None

    def trim_transparent(self, image):
        """
        Remove transparent outer padding from a PNG while keeping
        the artwork's original proportions.

        Compatible with Pygame versions where Mask does not expose
        get_bounding_rect(). Uses get_bounding_rects() as a fallback.
        """
        if image is None:
            return None

        try:
            mask = pygame.mask.from_surface(image)

            # Newer/alternate Pygame builds may expose this directly.
            if hasattr(mask, "get_bounding_rect"):
                bbox = mask.get_bounding_rect()
            else:
                # Pygame 2.5.x can provide multiple connected bounds.
                rects = mask.get_bounding_rects()
                if not rects:
                    return image

                bbox = rects[0].copy()
                for rect in rects[1:]:
                    bbox.union_ip(rect)

            if bbox.width <= 0 or bbox.height <= 0:
                return image

            if bbox.topleft == (0, 0) and bbox.size == image.get_size():
                return image

            return image.subsurface(bbox).copy()

        except (pygame.error, AttributeError, ValueError, TypeError):
            return image

    def load_image_file(self, path, trim=False):
        if not path:
            return None

        try:
            image = pygame.image.load(path).convert_alpha()

            if trim:
                image = self.trim_transparent(image)

            return image

        except (pygame.error, FileNotFoundError):
            print(f"[MAHIRAH ASSET WARNING] Could not load: {path}")
            return None

    def load_first_image(self, names, folders, trim=False):
        path = self.find_file(folders, names)
        return self.load_image_file(path, trim=trim)

    def load_assets(self):
        start_folders = [
            self.start_root,
            os.path.join(self.project_root, "assets", "mahirah"),
        ]

        ui_folders = [
            self.ui_root,
            os.path.join(self.project_root, "assets", "mahirah"),
        ]

        # --------------------------------------------------------
        # START SCREEN ASSETS
        # --------------------------------------------------------
        self.background = self.load_first_image(
            [
                "cyberpunk_cafe_start_bg.png",
                "start_bg.png",
                "start_bg_clean_1280x720.png",
            ],
            start_folders,
        )

        self.logo = self.load_first_image(
            [
                "logo_cyberpunk_cafe.png",
                "cyberpunk_cafe_logo.png",
                "logo.png",
            ],
            start_folders,
        )

        self.menu_asset = self.load_first_image(
            ["button_menu.png"],
            start_folders,
            trim=True,
        )

        self.menu_hover_asset = self.load_first_image(
            ["button_menu_hover.png"],
            start_folders,
            trim=True,
        )

        self.enter_asset = self.load_first_image(
            ["button_enter.png"],
            start_folders,
            trim=True,
        )

        self.enter_hover_asset = self.load_first_image(
            ["button_enter_hover.png"],
            start_folders,
            trim=True,
        )

        self.input_asset = self.load_first_image(
            ["input_name.png"],
            start_folders,
            trim=True,
        )

        self.input_active_asset = self.load_first_image(
            ["input_name_active.png"],
            start_folders,
            trim=True,
        )

        # --------------------------------------------------------
        # AUDIO UI ASSETS
        # --------------------------------------------------------
        self.audio_header_asset = self.load_first_image(
            ["audio_settings_header.png"],
            ui_folders,
            trim=True,
        )

        self.close_asset = self.load_first_image(
            ["button_close.png"],
            ui_folders,
            trim=True,
        )

        self.close_hover_asset = self.load_first_image(
            ["button_close_hover.png"],
            ui_folders,
            trim=True,
        )

        self.mute_asset = self.load_first_image(
            ["button_mute.png"],
            ui_folders,
            trim=True,
        )

        self.mute_hover_asset = self.load_first_image(
            ["button_mute_hover.png"],
            ui_folders,
            trim=True,
        )

        self.music_icon = self.load_first_image(
            ["icon_music_on.png"],
            ui_folders,
            trim=True,
        )

        self.music_icon_off = self.load_first_image(
            ["icon_music_off.png"],
            ui_folders,
            trim=True,
        )

        self.sound_icon = self.load_first_image(
            ["icon_sound_on.png"],
            ui_folders,
            trim=True,
        )

        self.sound_icon_off = self.load_first_image(
            ["icon_sound_off.png"],
            ui_folders,
            trim=True,
        )

        self.slider_music_asset = self.load_first_image(
            ["slider_music_track.png"],
            ui_folders,
            trim=True,
        )

        self.slider_sound_asset = self.load_first_image(
            ["slider_sound_track.png"],
            ui_folders,
            trim=True,
        )

        self.slider_fill_asset = self.load_first_image(
            ["slider_fill.png"],
            ui_folders,
            trim=True,
        )

        self.slider_knob_asset = self.load_first_image(
            ["slider_knob.png"],
            ui_folders,
            trim=True,
        )

        self.menu_panel_asset = self.load_first_image(
            ["menu_panel.png"],
            ui_folders,
            trim=True,
        )

    # ============================================================
    # FONT SYSTEM
    # ============================================================

    def get_audiowide_path(self):
        """Find Audiowide in the project first, then installed fonts."""
        project_candidates = [
            "Audiowide-Regular.ttf",
            "Audiowide.ttf",
            "audiowide.ttf",
            "Audiowide-Regular.otf",
        ]

        path = self.find_file(
            [self.font_root],
            project_candidates,
        )

        if path:
            return path

        # This works automatically if Audiowide has been installed
        # on the computer.
        return pygame.font.match_font("audiowide")

    def get_ui_font_path(self):
        candidates = [
            "segoeuisb",
            "segoeui",
            "bahnschrift",
            "trebuchetms",
            "arial",
        ]

        for family in candidates:
            path = pygame.font.match_font(family)
            if path:
                return path

        return None

    def create_fonts(self):
        pygame.font.init()

        audiowide_path = self.get_audiowide_path()
        ui_font_path = self.get_ui_font_path()

        if audiowide_path:
            self.font_welcome = pygame.font.Font(
                audiowide_path,
                36,
            )
            self.audiowide_available = True
            print("[FONT] Audiowide loaded for WELCOME, BARISTA.")
        else:
            # Fallback still looks good with the glow treatment.
            fallback = ui_font_path or pygame.font.get_default_font()
            self.font_welcome = pygame.font.Font(
                fallback,
                34,
            )
            self.font_welcome.set_bold(True)
            self.audiowide_available = False

        def make(size, bold=False):
            if ui_font_path:
                font = pygame.font.Font(ui_font_path, size)
                font.set_bold(bold)
                return font

            return pygame.font.SysFont(
                "Segoe UI",
                size,
                bold=bold,
            )

        self.font_question = make(20, True)
        self.font_input = make(17, False)
        self.font_button = make(22, True)
        self.font_menu = make(18, True)

        self.font_panel_title = make(22, True)
        self.font_panel_label = make(16, True)
        self.font_panel_percent = make(15, True)
        self.font_small = make(12, True)

        self.font_logo_fallback = make(36, True)

    # ============================================================
    # LAYOUT
    # ============================================================

    def create_layout(self):
        center_x = self.WIDTH // 2

        # --------------------------------------------------------
        # MAIN SCREEN
        # --------------------------------------------------------
        self.logo_box = pygame.Rect(
            185, 72, 910, 255
        )

        # Welcome heading sits cleanly between logo and name area.
        self.welcome_rect = pygame.Rect(
            210, 346, 860, 48
        )

        self.question_rect = pygame.Rect(
            210, 397, 860, 32
        )

        self.input_box = pygame.Rect(
            center_x - 385,
            430,
            770,
            100,
        )

        self.enter_box = pygame.Rect(
            center_x - 350,
            545,
            700,
            100,
        )

        self.menu_box = pygame.Rect(
            1015, 25, 240, 80
        )

        self.logo_rect = pygame.Rect(self.logo_box)
        self.input_rect = pygame.Rect(self.input_box)
        self.enter_rect = pygame.Rect(self.enter_box)
        self.menu_rect = pygame.Rect(self.menu_box)

        # --------------------------------------------------------
        # AUDIO PANEL
        # --------------------------------------------------------
        self.audio_panel = pygame.Rect(
            865, 180, 390, 505
        )

        # MUCH LARGER header area.
        # Slightly smaller header so it never touches the close button.
        self.audio_header_box = pygame.Rect(
            888, 214, 292, 68
        )

        self.audio_close_box = pygame.Rect(
            1202, 216, 38, 38
        )

        # Larger icons.
        self.music_icon_box = pygame.Rect(
            895, 313, 62, 62
        )

        self.sfx_icon_box = pygame.Rect(
            895, 403, 62, 62
        )

        # MUCH WIDER / TALLER sliders.
        self.music_track_rect = pygame.Rect(
            962, 329, 218, 32
        )

        self.sfx_track_rect = pygame.Rect(
            962, 419, 218, 32
        )

        self.music_percent_rect = pygame.Rect(
            1180, 322, 55, 45
        )

        self.sfx_percent_rect = pygame.Rect(
            1180, 412, 55, 45
        )

        # Mute buttons remain at opposite ends.
        self.mute_music_box = pygame.Rect(
            890, 505, 160, 70
        )

        self.mute_sfx_box = pygame.Rect(
            1070, 505, 160, 70
        )

        self.mute_music_rect = pygame.Rect(self.mute_music_box)
        self.mute_sfx_rect = pygame.Rect(self.mute_sfx_box)

        self.audio_footer_rect = pygame.Rect(
            890, 612, 340, 38
        )

        # Actual click rectangles are initialized before first draw.
        self.audio_header_rect = pygame.Rect(self.audio_header_box)
        self.audio_close_rect = pygame.Rect(self.audio_close_box)
        self.music_icon_rect = pygame.Rect(self.music_icon_box)
        self.sound_icon_rect = pygame.Rect(self.sfx_icon_box)

    # ============================================================
    # AUDIO
    # ============================================================

    def setup_audio(self):
        self.music_path = self.find_file(
            [self.audio_root],
            ["cyberpunk_cafe_theme.wav"],
        )

        self.click_path = self.find_file(
            [self.audio_root],
            ["button_click.wav"],
        )

        self.hover_path = self.find_file(
            [self.audio_root],
            ["button_hover.wav"],
        )

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            if self.music_path:
                pygame.mixer.music.load(self.music_path)
                self.update_music_volume()
                pygame.mixer.music.play(-1)

            if self.click_path:
                self.click_sound = pygame.mixer.Sound(self.click_path)

            if self.hover_path:
                self.hover_sound = pygame.mixer.Sound(self.hover_path)

            self.update_sfx_volume()

            print("[AUDIO] Cyberpunk Café music started.")

        except pygame.error as error:
            print(f"[AUDIO WARNING] {error}")

    def update_sfx_volume(self):
        volume = 0.0 if self.sfx_muted else self.sfx_volume

        if self.click_sound:
            self.click_sound.set_volume(volume)

        if self.hover_sound:
            self.hover_sound.set_volume(volume)

    def update_music_volume(self):
        volume = 0.0 if self.music_muted else self.music_volume

        try:
            pygame.mixer.music.set_volume(volume)
        except pygame.error:
            pass

    def play_click(self):
        if self.click_sound and not self.sfx_muted:
            self.click_sound.set_volume(self.sfx_volume)
            self.click_sound.play()

    def play_hover(self):
        if self.hover_sound and not self.sfx_muted:
            self.hover_sound.set_volume(self.sfx_volume)
            self.hover_sound.play()

    def toggle_music_mute(self):
        self.music_muted = not self.music_muted
        self.update_music_volume()

    def toggle_sfx_mute(self):
        self.sfx_muted = not self.sfx_muted
        self.update_sfx_volume()

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

    # ============================================================
    # DRAWING HELPERS
    # ============================================================

    def fit_rect(self, image, box):
        """Fit an image inside a box while preserving its proportions."""
        if image is None:
            return pygame.Rect(box)

        iw, ih = image.get_size()

        if iw <= 0 or ih <= 0:
            return pygame.Rect(box)

        scale = min(
            box.width / float(iw),
            box.height / float(ih),
        )

        width = max(1, int(iw * scale))
        height = max(1, int(ih * scale))

        return pygame.Rect(
            box.centerx - width // 2,
            box.centery - height // 2,
            width,
            height,
        )

    def draw_image_fit(self, image, box):
        if image is None:
            return None

        rect = self.fit_rect(image, box)

        scaled = pygame.transform.smoothscale(
            image,
            rect.size,
        )

        self.screen.blit(scaled, rect)
        return rect

    def draw_neon_rect(
        self,
        rect,
        border_color,
        radius=16,
        thickness=2,
        glow=True,
    ):
        if glow:
            for amount, alpha in [
                (10, 30),
                (6, 50),
                (3, 70),
            ]:
                glow_surface = pygame.Surface(
                    (self.WIDTH, self.HEIGHT),
                    pygame.SRCALPHA,
                )

                glow_rect = rect.inflate(amount, amount)

                pygame.draw.rect(
                    glow_surface,
                    (*border_color, alpha),
                    glow_rect,
                    width=thickness + 2,
                    border_radius=radius + 3,
                )

                self.screen.blit(glow_surface, (0, 0))

        pygame.draw.rect(
            self.screen,
            border_color,
            rect,
            width=thickness,
            border_radius=radius,
        )

    def draw_corner_marks(self, rect):
        length = 18
        color = self.CYAN

        points = [
            (
                (rect.left + 12, rect.top + length),
                (rect.left + 12, rect.top + 12),
                (rect.left + length, rect.top + 12),
            ),
            (
                (rect.right - 12, rect.top + length),
                (rect.right - 12, rect.top + 12),
                (rect.right - length, rect.top + 12),
            ),
            (
                (rect.left + 12, rect.bottom - length),
                (rect.left + 12, rect.bottom - 12),
                (rect.left + length, rect.bottom - 12),
            ),
            (
                (rect.right - 12, rect.bottom - length),
                (rect.right - 12, rect.bottom - 12),
                (rect.right - length, rect.bottom - 12),
            ),
        ]

        for a, b, c in points:
            pygame.draw.lines(
                self.screen,
                color,
                False,
                [a, b, c],
                2,
            )

    # ============================================================
    # GLOWING TEXT
    # ============================================================

    def draw_glowing_text(
        self,
        text,
        font,
        center,
        main_color,
        glow_color=None,
        pink_glow=True,
    ):
        """
        Draw soft layered neon around text.

        The glow is intentionally subtle: it should look like a
        cyberpunk café sign rather than a giant bright effect.
        """
        if glow_color is None:
            glow_color = self.CYAN

        base = font.render(text, True, main_color)

        # Cyan glow layers.
        for radius, alpha in [
            (8, 24),
            (5, 34),
            (3, 48),
        ]:
            glow = font.render(text, True, glow_color)
            glow.set_alpha(alpha)

            for dx, dy in [
                (-radius, 0),
                (radius, 0),
                (0, -radius),
                (0, radius),
            ]:
                glow_rect = glow.get_rect(
                    center=(center[0] + dx, center[1] + dy)
                )
                self.screen.blit(glow, glow_rect)

        # Very soft pink offset gives the heading more depth.
        if pink_glow:
            pink = font.render(text, True, self.PINK)
            pink.set_alpha(28)

            pink_rect = pink.get_rect(
                center=(center[0] + 3, center[1] + 2)
            )
            self.screen.blit(pink, pink_rect)

        base_rect = base.get_rect(center=center)
        self.screen.blit(base, base_rect)

        return base_rect

    # ============================================================
    # BACKGROUND
    # ============================================================

    def draw_background(self):
        if self.background:
            bg = pygame.transform.smoothscale(
                self.background,
                (self.WIDTH, self.HEIGHT),
            )
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((18, 12, 38))

            for x in range(0, self.WIDTH, 80):
                height = 80 + ((x * 17) % 180)

                pygame.draw.rect(
                    self.screen,
                    (18, 25, 55),
                    (x, self.HEIGHT - height, 55, height),
                )

        overlay = pygame.Surface(
            (self.WIDTH, self.HEIGHT),
            pygame.SRCALPHA,
        )
        overlay.fill((*self.BG_OVERLAY, 45))
        self.screen.blit(overlay, (0, 0))

    # ============================================================
    # MAIN SCREEN
    # ============================================================

    def draw_logo(self):
        actual = self.draw_image_fit(
            self.logo,
            self.logo_box,
        )

        if actual:
            self.logo_rect = actual
            return

        title = self.font_logo_fallback.render(
            "Cyberpunk Café",
            True,
            self.WHITE,
        )

        self.screen.blit(
            title,
            title.get_rect(center=self.logo_box.center),
        )

    def draw_welcome(self):
        # Main futuristic heading with soft neon glow.
        self.draw_glowing_text(
            "WELCOME, BARISTA",
            self.font_welcome,
            self.welcome_rect.center,
            self.WHITE,
            self.CYAN,
            pink_glow=True,
        )

        question = self.font_question.render(
            "WHAT'S YOUR NAME?",
            True,
            self.WHITE,
        )

        self.screen.blit(
            question,
            question.get_rect(center=self.question_rect.center),
        )

    def draw_name_input(self):
        image = (
            self.input_active_asset
            if self.name_active and self.input_active_asset
            else self.input_asset
        )

        actual = self.draw_image_fit(
            image,
            self.input_box,
        )

        if actual:
            self.input_rect = actual
        else:
            # Procedural fallback with the same visual language as the project.
            self.input_rect = pygame.Rect(self.input_box)

            pygame.draw.rect(
                self.screen,
                self.PANEL,
                self.input_rect,
                border_radius=18,
            )

            self.draw_neon_rect(
                self.input_rect,
                self.PINK if self.name_active else self.CYAN,
                radius=18,
                thickness=3,
            )

            # Small user/profile icon.
            icon_center = (
                self.input_rect.left + 48,
                self.input_rect.centery,
            )

            pygame.draw.circle(
                self.screen,
                self.PANEL_2,
                icon_center,
                25,
            )

            pygame.draw.circle(
                self.screen,
                self.PINK,
                icon_center,
                25,
                2,
            )

            pygame.draw.circle(
                self.screen,
                self.WHITE,
                (icon_center[0], icon_center[1] - 7),
                7,
                2,
            )

            pygame.draw.arc(
                self.screen,
                self.WHITE,
                (
                    icon_center[0] - 12,
                    icon_center[1] - 1,
                    24,
                    22,
                ),
                math.pi,
                math.pi * 2,
                2,
            )

        display_text = (
            self.player_name
            if self.player_name
            else "Enter your name..."
        )

        text_color = (
            self.WHITE
            if self.player_name
            else (150, 160, 190)
        )

        available_left = self.input_rect.left + 92
        available_right = self.input_rect.right - 28
        available_width = max(20, available_right - available_left)

        shown_text = display_text

        while (
            shown_text
            and self.font_input.size(shown_text)[0] > available_width
        ):
            shown_text = shown_text[:-1]

        if shown_text != display_text:
            shown_text = shown_text.rstrip() + "..."

        text = self.font_input.render(
            shown_text,
            True,
            text_color,
        )

        text_rect = text.get_rect(
            midleft=(
                available_left,
                self.input_rect.centery,
            )
        )

        self.screen.blit(
            text,
            text_rect,
        )

        if self.name_active:
            cursor_x = min(
                text_rect.right + 5,
                self.input_rect.right - 20,
            )

            pygame.draw.line(
                self.screen,
                self.CYAN,
                (
                    cursor_x,
                    self.input_rect.centery - 15,
                ),
                (
                    cursor_x,
                    self.input_rect.centery + 15,
                ),
                2,
            )


    def draw_enter_button(self):
        mouse = pygame.mouse.get_pos()
        hover = self.enter_rect.collidepoint(mouse)

        image = (
            self.enter_hover_asset
            if hover and self.enter_hover_asset
            else self.enter_asset
        )

        actual = self.draw_image_fit(
            image,
            self.enter_box,
        )

        if actual:
            self.enter_rect = actual
            return

        # Procedural fallback.
        self.enter_rect = pygame.Rect(self.enter_box)

        pygame.draw.rect(
            self.screen,
            self.DARK,
            self.enter_rect,
            border_radius=20,
        )

        self.draw_neon_rect(
            self.enter_rect,
            self.GOLD,
            radius=20,
            thickness=3,
            glow=True,
        )

        # Small coffee-cup accent on the left.
        cup_x = self.enter_rect.left + 60
        cup_y = self.enter_rect.centery

        pygame.draw.arc(
            self.screen,
            self.GOLD,
            (
                cup_x - 20,
                cup_y - 16,
                42,
                34,
            ),
            0,
            math.pi,
            3,
        )

        pygame.draw.line(
            self.screen,
            self.GOLD,
            (
                cup_x - 20,
                cup_y,
            ),
            (
                cup_x + 22,
                cup_y,
            ),
            3,
        )

        text = self.font_button.render(
            "ENTER CAFÉ",
            True,
            self.GOLD,
        )

        self.screen.blit(
            text,
            text.get_rect(center=self.enter_rect.center),
        )

        arrows = self.font_button.render(
            ">>",
            True,
            self.GOLD,
        )

        arrows_rect = arrows.get_rect(
            midright=(
                self.enter_rect.right - 28,
                self.enter_rect.centery,
            )
        )

        self.screen.blit(
            arrows,
            arrows_rect,
        )


    def draw_menu_button(self):
        mouse = pygame.mouse.get_pos()
        hover = self.menu_rect.collidepoint(mouse)

        image = (
            self.menu_hover_asset
            if hover and self.menu_hover_asset
            else self.menu_asset
        )

        if image:
            actual = self.draw_image_fit(
                image,
                self.menu_box,
            )

            if actual:
                self.menu_rect = actual
                return

        self.menu_rect = pygame.Rect(self.menu_box)

        border = self.PINK if hover else self.CYAN

        pygame.draw.rect(
            self.screen,
            self.PANEL,
            self.menu_rect,
            border_radius=17,
        )

        self.draw_neon_rect(
            self.menu_rect,
            border,
            radius=17,
            thickness=2,
        )

        # Small settings gear fallback.
        gear_center = (
            self.menu_rect.left + 36,
            self.menu_rect.centery,
        )

        pygame.draw.circle(
            self.screen,
            self.CYAN,
            gear_center,
            15,
            2,
        )

        pygame.draw.circle(
            self.screen,
            self.CYAN,
            gear_center,
            5,
            2,
        )

        text = self.font_menu.render(
            "MENU",
            True,
            self.WHITE,
        )

        self.screen.blit(
            text,
            text.get_rect(center=self.menu_rect.center),
        )


    # ============================================================
    # AUDIO PANEL
    # ============================================================

    def draw_audio_panel(self):
        panel = self.audio_panel

        # --------------------------------------------------------
        # Background veil
        # --------------------------------------------------------
        veil = pygame.Surface(
            (self.WIDTH, self.HEIGHT),
            pygame.SRCALPHA,
        )
        veil.fill((0, 0, 10, 95))
        self.screen.blit(veil, (0, 0))

        # --------------------------------------------------------
        # Panel shadow
        # --------------------------------------------------------
        shadow = pygame.Surface(
            (panel.width + 20, panel.height + 20),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            shadow,
            (0, 0, 0, 155),
            (10, 10, panel.width, panel.height),
            border_radius=24,
        )

        self.screen.blit(
            shadow,
            (panel.left - 5, panel.top + 8),
        )

        # --------------------------------------------------------
        # Panel body
        # --------------------------------------------------------
        pygame.draw.rect(
            self.screen,
            self.PANEL,
            panel,
            border_radius=22,
        )

        self.draw_neon_rect(
            panel,
            self.CYAN,
            radius=22,
            thickness=2,
        )
        self.draw_corner_marks(panel)

        # --------------------------------------------------------
        # MUCH LARGER AUDIO HEADER
        # --------------------------------------------------------
        if self.audio_header_asset:
            actual = self.draw_image_fit(
                self.audio_header_asset,
                self.audio_header_box,
            )
            self.audio_header_rect = actual
        else:
            self.audio_header_rect = pygame.Rect(
                self.audio_header_box
            )

            pygame.draw.rect(
                self.screen,
                self.PANEL_2,
                self.audio_header_rect,
                border_radius=13,
            )

            self.draw_neon_rect(
                self.audio_header_rect,
                self.PINK,
                radius=13,
                thickness=2,
            )

            title = self.font_panel_title.render(
                "AUDIO SETTINGS",
                True,
                self.WHITE,
            )

            self.screen.blit(
                title,
                title.get_rect(center=self.audio_header_rect.center),
            )

        # --------------------------------------------------------
        # CLOSE BUTTON
        # --------------------------------------------------------
        mouse = pygame.mouse.get_pos()
        close_hover = self.audio_close_box.collidepoint(mouse)

        close_image = (
            self.close_hover_asset
            if close_hover and self.close_hover_asset
            else self.close_asset
        )

        if close_image:
            actual = self.draw_image_fit(
                close_image,
                self.audio_close_box,
            )
            self.audio_close_rect = actual
        else:
            self.audio_close_rect = pygame.Rect(
                self.audio_close_box
            )

            pygame.draw.rect(
                self.screen,
                self.PANEL_2,
                self.audio_close_rect,
                border_radius=8,
            )

            self.draw_neon_rect(
                self.audio_close_rect,
                self.PINK,
                radius=8,
                thickness=2,
            )

            pygame.draw.line(
                self.screen,
                self.WHITE,
                self.audio_close_rect.topleft,
                self.audio_close_rect.bottomright,
                2,
            )

            pygame.draw.line(
                self.screen,
                self.WHITE,
                self.audio_close_rect.topright,
                self.audio_close_rect.bottomleft,
                2,
            )

        # --------------------------------------------------------
        # DIVIDER
        # --------------------------------------------------------
        pygame.draw.line(
            self.screen,
            (55, 105, 150),
            (panel.left + 25, 300),
            (panel.right - 25, 300),
            1,
        )

        # --------------------------------------------------------
        # MUSIC LABEL
        # --------------------------------------------------------
        music_label = self.font_panel_label.render(
            "MUSIC VOLUME",
            True,
            self.WHITE,
        )

        self.screen.blit(
            music_label,
            music_label.get_rect(
                midleft=(965, 310)
            ),
        )

        # --------------------------------------------------------
        # SFX LABEL
        # --------------------------------------------------------
        sfx_label = self.font_panel_label.render(
            "SOUND EFFECTS",
            True,
            self.WHITE,
        )

        self.screen.blit(
            sfx_label,
            sfx_label.get_rect(
                midleft=(965, 400)
            ),
        )

        # --------------------------------------------------------
        # ICONS
        # --------------------------------------------------------
        music_icon = (
            self.music_icon_off
            if self.music_muted and self.music_icon_off
            else self.music_icon
        )

        sound_icon = (
            self.sound_icon_off
            if self.sfx_muted and self.sound_icon_off
            else self.sound_icon
        )

        if music_icon:
            self.music_icon_rect = self.draw_image_fit(
                music_icon,
                self.music_icon_box,
            )
        else:
            self.draw_audio_icon(
                self.music_icon_box,
                "music",
                self.music_muted,
            )
            self.music_icon_rect = pygame.Rect(self.music_icon_box)

        if sound_icon:
            self.sound_icon_rect = self.draw_image_fit(
                sound_icon,
                self.sfx_icon_box,
            )
        else:
            self.draw_audio_icon(
                self.sfx_icon_box,
                "sound",
                self.sfx_muted,
            )
            self.sound_icon_rect = pygame.Rect(self.sfx_icon_box)

        # --------------------------------------------------------
        # LARGE SLIDERS
        # --------------------------------------------------------
        self.draw_asset_slider(
            self.slider_music_asset,
            self.music_track_rect,
            self.music_volume,
            self.music_muted,
        )

        self.draw_asset_slider(
            self.slider_sound_asset,
            self.sfx_track_rect,
            self.sfx_volume,
            self.sfx_muted,
        )

        # --------------------------------------------------------
        # PERCENTAGES
        # --------------------------------------------------------
        music_percent = self.font_panel_percent.render(
            f"{int(self.music_volume * 100)}%",
            True,
            self.WHITE,
        )

        self.screen.blit(
            music_percent,
            music_percent.get_rect(
                center=self.music_percent_rect.center
            ),
        )

        sfx_percent = self.font_panel_percent.render(
            f"{int(self.sfx_volume * 100)}%",
            True,
            self.WHITE,
        )

        self.screen.blit(
            sfx_percent,
            sfx_percent.get_rect(
                center=self.sfx_percent_rect.center
            ),
        )

        # --------------------------------------------------------
        # MUTE BUTTONS
        # --------------------------------------------------------
        self.draw_asset_mute_button(
            self.mute_music_box,
            "MUTE MUSIC",
            self.music_muted,
            self.PINK,
        )

        self.draw_asset_mute_button(
            self.mute_sfx_box,
            "MUTE SFX",
            self.sfx_muted,
            self.CYAN,
        )

        # --------------------------------------------------------
        # FOOTER
        # --------------------------------------------------------
        pygame.draw.line(
            self.screen,
            (55, 105, 150),
            (panel.left + 25, 600),
            (panel.right - 25, 600),
            1,
        )

        footer = self.font_small.render(
            "GOOD DRINKS  •  BRIGHTER PEOPLE",
            True,
            (105, 165, 225),
        )

        self.screen.blit(
            footer,
            footer.get_rect(
                center=self.audio_footer_rect.center
            ),
        )

    def draw_asset_slider(self, track_asset, rect, value, muted):
        value = max(0.0, min(1.0, value))

        # Both slider rows use the exact same visual footprint.  The two
        # supplied PNGs have different native proportions, which previously
        # made the SFX slider render much smaller than the Music slider.
        # Normalising the track artwork here keeps the controls aligned while
        # leaving the fill and knob behaviour unchanged.
        track = pygame.Rect(rect)

        if track_asset:
            scaled_track = pygame.transform.smoothscale(
                track_asset,
                track.size,
            )
            self.screen.blit(scaled_track, track)
        else:
            pygame.draw.rect(
                self.screen,
                (35, 50, 85),
                track,
                border_radius=9,
            )

            pygame.draw.rect(
                self.screen,
                (35, 50, 85),
                track,
                border_radius=9,
            )

        # Fill is clipped so it never leaves the track.
        fill_width = int(track.width * value)

        if fill_width > 0:
            fill_box = pygame.Rect(
                track.left,
                track.top,
                fill_width,
                track.height,
            )

            if self.slider_fill_asset:
                scaled = pygame.transform.smoothscale(
                    self.slider_fill_asset,
                    (
                        max(1, fill_width),
                        max(1, track.height),
                    ),
                )

                old_clip = self.screen.get_clip()
                self.screen.set_clip(track)
                self.screen.blit(scaled, fill_box)
                self.screen.set_clip(old_clip)
            else:
                pygame.draw.rect(
                    self.screen,
                    self.MUTED if muted else self.PINK,
                    fill_box,
                    border_radius=8,
                )

        # Bigger knob for the larger slider.
        knob_x = int(track.left + track.width * value)

        if self.slider_knob_asset:
            knob_box = pygame.Rect(
                knob_x - 19,
                track.centery - 19,
                38,
                38,
            )
            self.draw_image_fit(
                self.slider_knob_asset,
                knob_box,
            )
        else:
            pygame.draw.circle(
                self.screen,
                self.PINK if not muted else self.MUTED,
                (knob_x, track.centery),
                10,
            )

    def draw_asset_mute_button(self, box, label, muted, accent):
        mouse = pygame.mouse.get_pos()
        hover = box.collidepoint(mouse)

        image = (
            self.mute_hover_asset
            if hover and self.mute_hover_asset
            else self.mute_asset
        )

        if image:
            actual = self.draw_image_fit(
                image,
                box,
            )

            if label == "MUTE MUSIC":
                self.mute_music_rect = actual or pygame.Rect(box)
            else:
                self.mute_sfx_rect = actual or pygame.Rect(box)

            return

        pygame.draw.rect(
            self.screen,
            self.PANEL_2,
            box,
            border_radius=12,
        )

        self.draw_neon_rect(
            box,
            accent,
            radius=12,
            thickness=2,
        )

        text = self.font_small.render(
            label,
            True,
            self.WHITE,
        )

        self.screen.blit(
            text,
            text.get_rect(center=box.center),
        )

    def draw_audio_icon(self, rect, kind, muted):
        accent = self.PINK if kind == "music" else self.CYAN

        pygame.draw.circle(
            self.screen,
            self.PANEL_2,
            rect.center,
            25,
        )

        pygame.draw.circle(
            self.screen,
            accent,
            rect.center,
            25,
            2,
        )

        x, y = rect.center

        if kind == "music":
            pygame.draw.line(
                self.screen,
                accent,
                (x + 5, y - 13),
                (x + 5, y + 8),
                3,
            )

            pygame.draw.line(
                self.screen,
                accent,
                (x + 5, y - 13),
                (x + 15, y - 16),
                3,
            )

            pygame.draw.circle(
                self.screen,
                accent,
                (x - 2, y + 10),
                6,
            )
        else:
            pygame.draw.polygon(
                self.screen,
                accent,
                [
                    (x - 15, y - 7),
                    (x - 7, y - 7),
                    (x + 5, y - 16),
                    (x + 5, y + 16),
                    (x - 7, y + 7),
                    (x - 15, y + 7),
                ],
                2,
            )

            pygame.draw.arc(
                self.screen,
                accent,
                (x - 2, y - 12, 28, 24),
                -math.pi / 3,
                math.pi / 3,
                2,
            )

        if muted:
            pygame.draw.line(
                self.screen,
                self.WHITE,
                (rect.left + 12, rect.top + 12),
                (rect.right - 12, rect.bottom - 12),
                3,
            )

    # ============================================================
    # PROCEDURAL SLIDER FALLBACK
    # ============================================================

    def draw_slider(self, rect, value, muted):
        """
        Compatibility fallback for a simple procedural slider.
        The main audio panel uses draw_asset_slider() when the supplied
        track/knob assets exist.
        """
        value = max(0.0, min(1.0, value))

        pygame.draw.rect(
            self.screen,
            (20, 30, 60),
            rect.inflate(8, 10),
            border_radius=10,
        )

        pygame.draw.rect(
            self.screen,
            (55, 80, 120),
            rect,
            border_radius=8,
        )

        fill_width = int(rect.width * value)

        if fill_width > 0:
            fill_rect = pygame.Rect(
                rect.left,
                rect.top,
                fill_width,
                rect.height,
            )

            pygame.draw.rect(
                self.screen,
                self.MUTED if muted else self.PINK,
                fill_rect,
                border_radius=8,
            )

        knob_x = int(rect.left + rect.width * value)

        pygame.draw.circle(
            self.screen,
            self.PANEL_2,
            (knob_x, rect.centery),
            10,
        )

        pygame.draw.circle(
            self.screen,
            self.MUTED if muted else self.PINK,
            (knob_x, rect.centery),
            10,
            2,
        )

    # ============================================================
    # PROCEDURAL MUTE BUTTON FALLBACK
    # ============================================================

    def draw_mute_button(self, rect, label, muted, accent):
        """
        Compatibility fallback for a procedural mute button.
        The main audio panel uses draw_asset_mute_button() when its
        supplied PNG assets are available.
        """
        hover = rect.collidepoint(pygame.mouse.get_pos())

        border = (
            self.WHITE
            if muted
            else (self.PINK if hover else accent)
        )

        pygame.draw.rect(
            self.screen,
            self.PANEL_2,
            rect,
            border_radius=13,
        )

        self.draw_neon_rect(
            rect,
            border,
            radius=13,
            thickness=2,
            glow=True,
        )

        icon_x = rect.left + 26
        icon_y = rect.centery

        pygame.draw.polygon(
            self.screen,
            border,
            [
                (icon_x - 9, icon_y - 5),
                (icon_x - 3, icon_y - 5),
                (icon_x + 6, icon_y - 12),
                (icon_x + 6, icon_y + 12),
                (icon_x - 3, icon_y + 5),
                (icon_x - 9, icon_y + 5),
            ],
            2,
        )

        if muted:
            pygame.draw.line(
                self.screen,
                self.WHITE,
                (icon_x - 11, icon_y - 13),
                (icon_x + 10, icon_y + 13),
                3,
            )

        text = self.font_small.render(
            label,
            True,
            self.WHITE,
        )

        self.screen.blit(
            text,
            text.get_rect(
                center=(rect.centerx + 12, rect.centery),
            ),
        )

    # ============================================================
    # SLIDER VALUE
    # ============================================================

    def slider_value(self, rect, mouse_x):
        value = (
            mouse_x - rect.left
        ) / float(rect.width)

        return max(0.0, min(1.0, value))

    # ============================================================
    # NAME
    # ============================================================

    def accept_name(self):
        cleaned = " ".join(
            self.player_name.strip().split()
        )

        if not cleaned:
            return False

        self.player_name = cleaned[:24]
        self.finished = True
        self.play_click()

        return True

    # ============================================================
    # HOVER SOUND
    # ============================================================

    def update_hover_sound(self):
        mouse = pygame.mouse.get_pos()
        targets = set()

        if not self.audio_menu_open:
            if self.menu_rect.collidepoint(mouse):
                targets.add("menu")

            if self.input_rect.collidepoint(mouse):
                targets.add("input")

            if self.enter_rect.collidepoint(mouse):
                targets.add("enter")
        else:
            if self.audio_close_rect.collidepoint(mouse):
                targets.add("close")

            if self.mute_music_rect.collidepoint(mouse):
                targets.add("mute_music")

            if self.mute_sfx_rect.collidepoint(mouse):
                targets.add("mute_sfx")

        new_targets = targets - self.last_hover

        if new_targets:
            self.play_hover()

        self.last_hover = targets

    # ============================================================
    # EVENTS
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.stop_music()
            return None

        # --------------------------------------------------------
        # KEYBOARD
        # --------------------------------------------------------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.audio_menu_open:
                    self.audio_menu_open = False
                    self.dragging_music = False
                    self.dragging_sfx = False
                    return ""

                self.stop_music()
                return None

            if self.audio_menu_open:
                return ""

            if event.key == pygame.K_RETURN:
                self.accept_name()

            elif event.key == pygame.K_BACKSPACE:
                if self.name_active:
                    self.player_name = self.player_name[:-1]

            elif (
                self.name_active
                and event.unicode
                and event.unicode.isprintable()
                and len(self.player_name) < 24
            ):
                self.player_name += event.unicode

        # --------------------------------------------------------
        # MOUSE DOWN
        # --------------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                return ""

            mouse = event.pos

            # AUDIO PANEL
            if self.audio_menu_open:
                if self.audio_close_rect.collidepoint(mouse):
                    self.play_click()
                    self.audio_menu_open = False
                    self.dragging_music = False
                    self.dragging_sfx = False
                    return ""

                if self.music_track_rect.inflate(0, 28).collidepoint(mouse):
                    self.dragging_music = True
                    self.music_volume = self.slider_value(
                        self.music_track_rect,
                        mouse[0],
                    )
                    self.update_music_volume()
                    return ""

                if self.sfx_track_rect.inflate(0, 28).collidepoint(mouse):
                    self.dragging_sfx = True
                    self.sfx_volume = self.slider_value(
                        self.sfx_track_rect,
                        mouse[0],
                    )
                    self.update_sfx_volume()
                    return ""

                if self.mute_music_rect.collidepoint(mouse):
                    self.play_click()
                    self.toggle_music_mute()
                    return ""

                if self.mute_sfx_rect.collidepoint(mouse):
                    self.play_click()
                    self.toggle_sfx_mute()
                    return ""

                return ""

            # MAIN SCREEN
            if self.menu_rect.collidepoint(mouse):
                self.play_click()
                self.audio_menu_open = True
                self.name_active = False
                return ""

            if self.input_rect.collidepoint(mouse):
                self.play_click()
                self.name_active = True
                return ""

            if self.enter_rect.collidepoint(mouse):
                self.accept_name()
                return ""

        # --------------------------------------------------------
        # MOUSE MOTION
        # --------------------------------------------------------
        if event.type == pygame.MOUSEMOTION:
            if self.audio_menu_open:
                if self.dragging_music:
                    self.music_volume = self.slider_value(
                        self.music_track_rect,
                        event.pos[0],
                    )
                    self.update_music_volume()

                if self.dragging_sfx:
                    self.sfx_volume = self.slider_value(
                        self.sfx_track_rect,
                        event.pos[0],
                    )
                    self.update_sfx_volume()

        # --------------------------------------------------------
        # MOUSE UP
        # --------------------------------------------------------
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_music = False
                self.dragging_sfx = False

        return (
            "START"
            if self.finished
            else ""
        )

    # ============================================================
    # DRAW
    # ============================================================

    def draw(self):
        self.draw_background()
        self.draw_logo()
        self.draw_welcome()
        self.draw_name_input()
        self.draw_enter_button()
        self.draw_menu_button()

        if self.audio_menu_open:
            self.draw_audio_panel()

        self.update_hover_sound()
        pygame.display.flip()

    # ============================================================
    # RUN
    # ============================================================

    def run(self):
        while True:
            for event in pygame.event.get():
                result = self.handle_event(event)

                if result is None:
                    return None

                if result == "START":
                    self.stop_music()
                    return self.player_name

            self.draw()
            self.clock.tick(self.FPS)


# ================================================================
# STANDALONE TEST
# ================================================================

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode(
        (
            StartScreen.WIDTH,
            StartScreen.HEIGHT,
        )
    )

    pygame.display.set_caption("Cyberpunk Café")

    start = StartScreen(screen)
    player = start.run()

    print(f"Player name: {player}")

    pygame.quit()
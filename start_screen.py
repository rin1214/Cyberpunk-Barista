import os
import math
import pygame


class StartScreen:
    """
    Cyberpunk Café — Mahirah start screen (1280 × 720).

    Usage:  StartScreen(screen).run()
    Returns: player name string, or None if the window was closed.

    Font: place Audiowide-Regular.ttf in assets/fonts/
          Falls back to a system font automatically.
    """

    WIDTH, HEIGHT, FPS = 1280, 720, 60

    # ── Colour palette ──────────────────────────────────────────────────────
    BG_OVERLAY = (5, 8, 24)
    PANEL      = (8, 14, 35)
    PANEL_2    = (11, 19, 46)
    CYAN       = (45, 226, 255)
    BLUE       = (73, 142, 255)
    PINK       = (255, 55, 210)
    PURPLE     = (180, 95, 255)
    WHITE      = (245, 247, 255)
    SOFT_WHITE = (210, 218, 240)
    GOLD       = (255, 190, 62)
    GREEN      = (95, 255, 200)
    DARK       = (15, 18, 35)
    MUTED      = (120, 130, 160)

    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()

        # Player / UI state
        self.player_name    = ""
        self.name_active    = False
        self.finished       = False
        self.audio_menu_open = False
        self.music_volume   = 0.30
        self.sfx_volume     = 0.16
        self.music_muted    = False
        self.sfx_muted      = False
        self.click_sound    = None
        self.hover_sound    = None
        self.last_hover     = set()
        self.dragging_music = False
        self.dragging_sfx   = False

        # Paths
        root = os.path.dirname(os.path.abspath(__file__))
        self.start_root = os.path.join(root, "assets", "mahirah", "start")
        self.ui_root    = os.path.join(root, "assets", "mahirah", "ui")
        self.audio_root = os.path.join(root, "assets", "mahirah", "audio")
        self.font_root  = os.path.join(root, "assets", "fonts")

        self.load_assets()
        self.create_fonts()
        self.create_layout()
        self.setup_audio()

    # ── Asset helpers ────────────────────────────────────────────────────────

    def find_file(self, folders, names):
        for folder in folders:
            for name in names:
                path = os.path.join(folder, name)
                if os.path.isfile(path):
                    return path
        return None

    def trim_transparent(self, image):
        """Strip transparent outer padding while preserving proportions."""
        if image is None:
            return None
        try:
            mask = pygame.mask.from_surface(image)
            if hasattr(mask, "get_bounding_rect"):
                bbox = mask.get_bounding_rect()
            else:
                rects = mask.get_bounding_rects()
                if not rects:
                    return image
                bbox = rects[0].copy()
                for r in rects[1:]:
                    bbox.union_ip(r)
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
            img = pygame.image.load(path).convert_alpha()
            return self.trim_transparent(img) if trim else img
        except (pygame.error, FileNotFoundError):
            print(f"[MAHIRAH ASSET WARNING] Could not load: {path}")
            return None

    def load_first_image(self, names, folders, trim=False):
        return self.load_image_file(self.find_file(folders, names), trim=trim)

    def load_assets(self):
        sf = [self.start_root, os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mahirah")]
        uf = [self.ui_root,    os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mahirah")]

        self.background         = self.load_first_image(["cyberpunk_cafe_start_bg.png", "start_bg.png", "start_bg_clean_1280x720.png"], sf)
        self.logo               = self.load_first_image(["logo_cyberpunk_cafe.png", "cyberpunk_cafe_logo.png", "logo.png"], sf)
        self.menu_asset         = self.load_first_image(["button_menu.png"],        sf, trim=True)
        self.menu_hover_asset   = self.load_first_image(["button_menu_hover.png"],  sf, trim=True)
        self.enter_asset        = self.load_first_image(["button_enter.png"],       sf, trim=True)
        self.enter_hover_asset  = self.load_first_image(["button_enter_hover.png"], sf, trim=True)
        self.input_asset        = self.load_first_image(["input_name.png"],         sf, trim=True)
        self.input_active_asset = self.load_first_image(["input_name_active.png"],  sf, trim=True)

        self.audio_header_asset  = self.load_first_image(["audio_settings_header.png"], uf, trim=True)
        self.close_asset         = self.load_first_image(["button_close.png"],       uf, trim=True)
        self.close_hover_asset   = self.load_first_image(["button_close_hover.png"], uf, trim=True)
        self.mute_asset          = self.load_first_image(["button_mute.png"],        uf, trim=True)
        self.mute_hover_asset    = self.load_first_image(["button_mute_hover.png"],  uf, trim=True)
        self.music_icon          = self.load_first_image(["icon_music_on.png"],      uf, trim=True)
        self.music_icon_off      = self.load_first_image(["icon_music_off.png"],     uf, trim=True)
        self.sound_icon          = self.load_first_image(["icon_sound_on.png"],      uf, trim=True)
        self.sound_icon_off      = self.load_first_image(["icon_sound_off.png"],     uf, trim=True)
        self.slider_music_asset  = self.load_first_image(["slider_music_track.png"], uf, trim=True)
        self.slider_sound_asset  = self.load_first_image(["slider_sound_track.png"], uf, trim=True)
        self.slider_fill_asset   = self.load_first_image(["slider_fill.png"],        uf, trim=True)
        self.slider_knob_asset   = self.load_first_image(["slider_knob.png"],        uf, trim=True)
        self.menu_panel_asset    = self.load_first_image(["menu_panel.png"],         uf, trim=True)

    # ── Fonts ────────────────────────────────────────────────────────────────

    def get_audiowide_path(self):
        path = self.find_file([self.font_root],
                              ["Audiowide-Regular.ttf", "Audiowide.ttf",
                               "audiowide.ttf", "Audiowide-Regular.otf"])
        return path or pygame.font.match_font("audiowide")

    def get_ui_font_path(self):
        for family in ["segoeuisb", "segoeui", "bahnschrift", "trebuchetms", "arial"]:
            path = pygame.font.match_font(family)
            if path:
                return path
        return None

    def create_fonts(self):
        pygame.font.init()
        aw_path = self.get_audiowide_path()
        ui_path = self.get_ui_font_path()

        if aw_path:
            self.font_welcome = pygame.font.Font(aw_path, 36)
            self.audiowide_available = True
            print("[FONT] Audiowide loaded for WELCOME, BARISTA.")
        else:
            fallback = ui_path or pygame.font.get_default_font()
            self.font_welcome = pygame.font.Font(fallback, 34)
            self.font_welcome.set_bold(True)
            self.audiowide_available = False

        def make(size, bold=False):
            if ui_path:
                f = pygame.font.Font(ui_path, size)
                f.set_bold(bold)
                return f
            return pygame.font.SysFont("Segoe UI", size, bold=bold)

        self.font_question     = make(20, True)
        self.font_input        = make(17)
        self.font_button       = make(22, True)
        self.font_menu         = make(18, True)
        self.font_panel_title  = make(22, True)
        self.font_panel_label  = make(16, True)
        self.font_panel_percent= make(15, True)
        self.font_small        = make(12, True)
        self.font_logo_fallback= make(36, True)

    # ── Layout ───────────────────────────────────────────────────────────────

    def create_layout(self):
        cx = self.WIDTH // 2

        # Main screen rects
        self.logo_box    = pygame.Rect(185, 72,  910, 255)
        self.welcome_rect= pygame.Rect(210, 346, 860, 48)
        self.question_rect= pygame.Rect(210, 397, 860, 32)
        self.input_box   = pygame.Rect(cx - 385, 430, 770, 100)
        self.enter_box   = pygame.Rect(cx - 350, 545, 700, 100)
        self.menu_box    = pygame.Rect(1015, 25, 240, 80)

        self.logo_rect  = pygame.Rect(self.logo_box)
        self.input_rect = pygame.Rect(self.input_box)
        self.enter_rect = pygame.Rect(self.enter_box)
        self.menu_rect  = pygame.Rect(self.menu_box)

        # Audio panel rects
        self.audio_panel       = pygame.Rect(865, 180, 390, 505)
        self.audio_header_box  = pygame.Rect(888, 214, 292, 68)
        self.audio_close_box   = pygame.Rect(1202, 216, 38, 38)
        self.music_icon_box    = pygame.Rect(895, 313, 62, 62)
        self.sfx_icon_box      = pygame.Rect(895, 403, 62, 62)
        self.music_track_rect  = pygame.Rect(962, 329, 218, 32)
        self.sfx_track_rect    = pygame.Rect(962, 419, 218, 32)
        self.music_percent_rect= pygame.Rect(1180, 322, 55, 45)
        self.sfx_percent_rect  = pygame.Rect(1180, 412, 55, 45)
        self.mute_music_box    = pygame.Rect(890, 505, 160, 70)
        self.mute_sfx_box      = pygame.Rect(1070, 505, 160, 70)
        self.audio_footer_rect = pygame.Rect(890, 612, 340, 38)

        self.mute_music_rect  = pygame.Rect(self.mute_music_box)
        self.mute_sfx_rect    = pygame.Rect(self.mute_sfx_box)
        self.audio_header_rect= pygame.Rect(self.audio_header_box)
        self.audio_close_rect = pygame.Rect(self.audio_close_box)
        self.music_icon_rect  = pygame.Rect(self.music_icon_box)
        self.sound_icon_rect  = pygame.Rect(self.sfx_icon_box)

    # ── Audio ────────────────────────────────────────────────────────────────

    def setup_audio(self):
        self.music_path = self.find_file([self.audio_root], ["cyberpunk_cafe_theme.wav"])
        self.click_path = self.find_file([self.audio_root], ["button_click.wav"])
        self.hover_path = self.find_file([self.audio_root], ["button_hover.wav"])
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
        except pygame.error as e:
            print(f"[AUDIO WARNING] {e}")

    def update_sfx_volume(self):
        vol = 0.0 if self.sfx_muted else self.sfx_volume
        if self.click_sound: self.click_sound.set_volume(vol)
        if self.hover_sound: self.hover_sound.set_volume(vol)

    def update_music_volume(self):
        try:
            pygame.mixer.music.set_volume(0.0 if self.music_muted else self.music_volume)
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

    # ── Drawing helpers ──────────────────────────────────────────────────────

    def fit_rect(self, image, box):
        """Fit image inside box preserving aspect ratio."""
        if image is None:
            return pygame.Rect(box)
        iw, ih = image.get_size()
        if iw <= 0 or ih <= 0:
            return pygame.Rect(box)
        scale  = min(box.width / float(iw), box.height / float(ih))
        w, h   = max(1, int(iw * scale)), max(1, int(ih * scale))
        return pygame.Rect(box.centerx - w // 2, box.centery - h // 2, w, h)

    def draw_image_fit(self, image, box):
        if image is None:
            return None
        rect = self.fit_rect(image, box)
        self.screen.blit(pygame.transform.smoothscale(image, rect.size), rect)
        return rect

    def draw_neon_rect(self, rect, border_color, radius=16, thickness=2, glow=True):
        if glow:
            surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            for amount, alpha in [(10, 30), (6, 50), (3, 70)]:
                pygame.draw.rect(surf, (*border_color, alpha),
                                 rect.inflate(amount, amount),
                                 width=thickness + 2, border_radius=radius + 3)
            self.screen.blit(surf, (0, 0))
        pygame.draw.rect(self.screen, border_color, rect, width=thickness, border_radius=radius)

    def draw_corner_marks(self, rect):
        color, l = self.CYAN, 18
        for pts in [
            [(rect.left+12, rect.top+l),    (rect.left+12,  rect.top+12),    (rect.left+l,  rect.top+12)],
            [(rect.right-12, rect.top+l),   (rect.right-12, rect.top+12),    (rect.right-l, rect.top+12)],
            [(rect.left+12, rect.bottom-l), (rect.left+12,  rect.bottom-12), (rect.left+l,  rect.bottom-12)],
            [(rect.right-12,rect.bottom-l), (rect.right-12, rect.bottom-12), (rect.right-l, rect.bottom-12)],
        ]:
            pygame.draw.lines(self.screen, color, False, pts, 2)

    def draw_glowing_text(self, text, font, center, main_color, glow_color=None, pink_glow=True):
        """Soft layered neon around text — cyberpunk café sign style."""
        if glow_color is None:
            glow_color = self.CYAN
        base = font.render(text, True, main_color)
        for radius, alpha in [(8, 24), (5, 34), (3, 48)]:
            glow = font.render(text, True, glow_color)
            glow.set_alpha(alpha)
            for dx, dy in [(-radius, 0), (radius, 0), (0, -radius), (0, radius)]:
                self.screen.blit(glow, glow.get_rect(center=(center[0]+dx, center[1]+dy)))
        if pink_glow:
            pink = font.render(text, True, self.PINK)
            pink.set_alpha(28)
            self.screen.blit(pink, pink.get_rect(center=(center[0]+3, center[1]+2)))
        self.screen.blit(base, base.get_rect(center=center))
        return base.get_rect(center=center)

    # ── Background ───────────────────────────────────────────────────────────

    def draw_background(self):
        if self.background:
            self.screen.blit(pygame.transform.smoothscale(self.background, (self.WIDTH, self.HEIGHT)), (0, 0))
        else:
            self.screen.fill((18, 12, 38))
            for x in range(0, self.WIDTH, 80):
                h = 80 + ((x * 17) % 180)
                pygame.draw.rect(self.screen, (18, 25, 55), (x, self.HEIGHT - h, 55, h))
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((*self.BG_OVERLAY, 45))
        self.screen.blit(overlay, (0, 0))

    # ── Main screen elements ─────────────────────────────────────────────────

    def draw_logo(self):
        actual = self.draw_image_fit(self.logo, self.logo_box)
        if actual:
            self.logo_rect = actual
            return
        title = self.font_logo_fallback.render("Cyberpunk Café", True, self.WHITE)
        self.screen.blit(title, title.get_rect(center=self.logo_box.center))

    def draw_welcome(self):
        name = self.player_name.strip() or "BARISTA"
        self.draw_glowing_text(f"WELCOME, {name.upper()}", self.font_welcome,
                               self.welcome_rect.center, self.WHITE, self.CYAN, pink_glow=True)
        q = self.font_question.render("WHAT'S YOUR NAME?", True, self.WHITE)
        self.screen.blit(q, q.get_rect(center=self.question_rect.center))

    def draw_name_input(self):
        image = (self.input_active_asset if self.name_active and self.input_active_asset
                 else self.input_asset)
        actual = self.draw_image_fit(image, self.input_box)
        if actual:
            self.input_rect = actual
        else:
            self.input_rect = pygame.Rect(self.input_box)
            pygame.draw.rect(self.screen, self.PANEL, self.input_rect, border_radius=18)
            self.draw_neon_rect(self.input_rect, self.PINK if self.name_active else self.CYAN,
                                radius=18, thickness=3)
            ic = (self.input_rect.left + 48, self.input_rect.centery)
            pygame.draw.circle(self.screen, self.PANEL_2, ic, 25)
            pygame.draw.circle(self.screen, self.PINK, ic, 25, 2)
            pygame.draw.circle(self.screen, self.WHITE, (ic[0], ic[1] - 7), 7, 2)
            pygame.draw.arc(self.screen, self.WHITE,
                            (ic[0]-12, ic[1]-1, 24, 22), math.pi, math.pi*2, 2)

        display_text = self.player_name or "Enter your name..."
        text_color   = self.WHITE if self.player_name else (150, 160, 190)
        avail_left   = self.input_rect.left + 92
        avail_width  = max(20, self.input_rect.right - 28 - avail_left)
        shown = display_text
        while shown and self.font_input.size(shown)[0] > avail_width:
            shown = shown[:-1]
        if shown != display_text:
            shown = shown.rstrip() + "..."
        txt = self.font_input.render(shown, True, text_color)
        self.screen.blit(txt, txt.get_rect(midleft=(avail_left, self.input_rect.centery)))

        if self.name_active:
            cx = min(txt.get_rect(midleft=(avail_left, self.input_rect.centery)).right + 5,
                     self.input_rect.right - 20)
            pygame.draw.line(self.screen, self.CYAN,
                             (cx, self.input_rect.centery - 15),
                             (cx, self.input_rect.centery + 15), 2)

    def draw_enter_button(self):
        mouse = pygame.mouse.get_pos()
        hover = self.enter_rect.collidepoint(mouse)
        image = self.enter_hover_asset if hover and self.enter_hover_asset else self.enter_asset
        actual = self.draw_image_fit(image, self.enter_box)
        if actual:
            self.enter_rect = actual
            return
        self.enter_rect = pygame.Rect(self.enter_box)
        pygame.draw.rect(self.screen, self.DARK, self.enter_rect, border_radius=20)
        self.draw_neon_rect(self.enter_rect, self.GOLD, radius=20, thickness=3, glow=True)
        cx, cy = self.enter_rect.left + 60, self.enter_rect.centery
        pygame.draw.arc(self.screen, self.GOLD, (cx-20, cy-16, 42, 34), 0, math.pi, 3)
        pygame.draw.line(self.screen, self.GOLD, (cx-20, cy), (cx+22, cy), 3)
        t = self.font_button.render("ENTER CAFÉ", True, self.GOLD)
        self.screen.blit(t, t.get_rect(center=self.enter_rect.center))
        arr = self.font_button.render(">>", True, self.GOLD)
        self.screen.blit(arr, arr.get_rect(midright=(self.enter_rect.right-28, self.enter_rect.centery)))

    def draw_menu_button(self):
        mouse = pygame.mouse.get_pos()
        hover = self.menu_rect.collidepoint(mouse)
        image = self.menu_hover_asset if hover and self.menu_hover_asset else self.menu_asset
        if image:
            actual = self.draw_image_fit(image, self.menu_box)
            if actual:
                self.menu_rect = actual
                return
        self.menu_rect = pygame.Rect(self.menu_box)
        border = self.PINK if hover else self.CYAN
        pygame.draw.rect(self.screen, self.PANEL, self.menu_rect, border_radius=17)
        self.draw_neon_rect(self.menu_rect, border, radius=17, thickness=2)
        gc = (self.menu_rect.left + 36, self.menu_rect.centery)
        pygame.draw.circle(self.screen, self.CYAN, gc, 15, 2)
        pygame.draw.circle(self.screen, self.CYAN, gc, 5,  2)
        t = self.font_menu.render("MENU", True, self.WHITE)
        self.screen.blit(t, t.get_rect(center=self.menu_rect.center))

    # ── Audio panel ──────────────────────────────────────────────────────────

    def draw_audio_panel(self):
        panel = self.audio_panel
        mouse = pygame.mouse.get_pos()

        # Veil + shadow
        veil = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 10, 95))
        self.screen.blit(veil, (0, 0))
        shadow = pygame.Surface((panel.width+20, panel.height+20), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 155), (10, 10, panel.width, panel.height), border_radius=24)
        self.screen.blit(shadow, (panel.left-5, panel.top+8))

        # Panel body
        pygame.draw.rect(self.screen, self.PANEL, panel, border_radius=22)
        self.draw_neon_rect(panel, self.CYAN, radius=22, thickness=2)
        self.draw_corner_marks(panel)

        # Header
        if self.audio_header_asset:
            self.audio_header_rect = self.draw_image_fit(self.audio_header_asset, self.audio_header_box)
        else:
            self.audio_header_rect = pygame.Rect(self.audio_header_box)
            pygame.draw.rect(self.screen, self.PANEL_2, self.audio_header_rect, border_radius=13)
            self.draw_neon_rect(self.audio_header_rect, self.PINK, radius=13, thickness=2)
            t = self.font_panel_title.render("AUDIO SETTINGS", True, self.WHITE)
            self.screen.blit(t, t.get_rect(center=self.audio_header_rect.center))

        # Close button
        close_hover  = self.audio_close_box.collidepoint(mouse)
        close_image  = self.close_hover_asset if close_hover and self.close_hover_asset else self.close_asset
        if close_image:
            self.audio_close_rect = self.draw_image_fit(close_image, self.audio_close_box)
        else:
            self.audio_close_rect = pygame.Rect(self.audio_close_box)
            pygame.draw.rect(self.screen, self.PANEL_2, self.audio_close_rect, border_radius=8)
            self.draw_neon_rect(self.audio_close_rect, self.PINK, radius=8, thickness=2)
            pygame.draw.line(self.screen, self.WHITE, self.audio_close_rect.topleft,    self.audio_close_rect.bottomright, 2)
            pygame.draw.line(self.screen, self.WHITE, self.audio_close_rect.topright,   self.audio_close_rect.bottomleft,  2)

        # Divider
        pygame.draw.line(self.screen, (55, 105, 150), (panel.left+25, 300), (panel.right-25, 300), 1)

        # Labels
        for text, y in [("MUSIC VOLUME", 310), ("SOUND EFFECTS", 400)]:
            lbl = self.font_panel_label.render(text, True, self.WHITE)
            self.screen.blit(lbl, lbl.get_rect(midleft=(965, y)))

        # Icons
        music_icon = self.music_icon_off if self.music_muted and self.music_icon_off else self.music_icon
        sound_icon = self.sound_icon_off if self.sfx_muted   and self.sound_icon_off else self.sound_icon
        if music_icon:
            self.music_icon_rect = self.draw_image_fit(music_icon, self.music_icon_box)
        else:
            self.draw_audio_icon(self.music_icon_box, "music", self.music_muted)
            self.music_icon_rect = pygame.Rect(self.music_icon_box)
        if sound_icon:
            self.sound_icon_rect = self.draw_image_fit(sound_icon, self.sfx_icon_box)
        else:
            self.draw_audio_icon(self.sfx_icon_box, "sound", self.sfx_muted)
            self.sound_icon_rect = pygame.Rect(self.sfx_icon_box)

        # Sliders
        self.draw_asset_slider(self.slider_music_asset, self.music_track_rect, self.music_volume, self.music_muted)
        self.draw_asset_slider(self.slider_sound_asset, self.sfx_track_rect,   self.sfx_volume,   self.sfx_muted)

        # Percentages
        for val, rect in [(self.music_volume, self.music_percent_rect), (self.sfx_volume, self.sfx_percent_rect)]:
            pct = self.font_panel_percent.render(f"{int(val*100)}%", True, self.WHITE)
            self.screen.blit(pct, pct.get_rect(center=rect.center))

        # Mute buttons
        self.draw_asset_mute_button(self.mute_music_box, "MUTE MUSIC", self.music_muted, self.PINK)
        self.draw_asset_mute_button(self.mute_sfx_box,   "MUTE SFX",   self.sfx_muted,   self.CYAN)

        # Footer
        pygame.draw.line(self.screen, (55, 105, 150), (panel.left+25, 600), (panel.right-25, 600), 1)
        footer = self.font_small.render("GOOD DRINKS  •  BRIGHTER PEOPLE", True, (105, 165, 225))
        self.screen.blit(footer, footer.get_rect(center=self.audio_footer_rect.center))

    def draw_asset_slider(self, track_asset, rect, value, muted):
        value = max(0.0, min(1.0, value))
        track = pygame.Rect(rect)
        if track_asset:
            self.screen.blit(pygame.transform.smoothscale(track_asset, track.size), track)
        else:
            pygame.draw.rect(self.screen, (35, 50, 85), track, border_radius=9)

        fill_w = int(track.width * value)
        if fill_w > 0:
            fill_box = pygame.Rect(track.left, track.top, fill_w, track.height)
            if self.slider_fill_asset:
                scaled = pygame.transform.smoothscale(self.slider_fill_asset,
                                                      (max(1, fill_w), max(1, track.height)))
                old_clip = self.screen.get_clip()
                self.screen.set_clip(track)
                self.screen.blit(scaled, fill_box)
                self.screen.set_clip(old_clip)
            else:
                pygame.draw.rect(self.screen, self.MUTED if muted else self.PINK,
                                 fill_box, border_radius=8)

        knob_x = int(track.left + track.width * value)
        if self.slider_knob_asset:
            self.draw_image_fit(self.slider_knob_asset,
                                pygame.Rect(knob_x-19, track.centery-19, 38, 38))
        else:
            pygame.draw.circle(self.screen, self.PINK if not muted else self.MUTED,
                               (knob_x, track.centery), 10)

    def draw_asset_mute_button(self, box, label, muted, accent):
        mouse = pygame.mouse.get_pos()
        hover = box.collidepoint(mouse)
        image = self.mute_hover_asset if hover and self.mute_hover_asset else self.mute_asset
        if image:
            actual = self.draw_image_fit(image, box)
            if label == "MUTE MUSIC":
                self.mute_music_rect = actual or pygame.Rect(box)
            else:
                self.mute_sfx_rect = actual or pygame.Rect(box)
            return
        pygame.draw.rect(self.screen, self.PANEL_2, box, border_radius=12)
        self.draw_neon_rect(box, accent, radius=12, thickness=2)
        t = self.font_small.render(label, True, self.WHITE)
        self.screen.blit(t, t.get_rect(center=box.center))

    def draw_audio_icon(self, rect, kind, muted):
        accent = self.PINK if kind == "music" else self.CYAN
        pygame.draw.circle(self.screen, self.PANEL_2, rect.center, 25)
        pygame.draw.circle(self.screen, accent,       rect.center, 25, 2)
        x, y = rect.center
        if kind == "music":
            pygame.draw.line(self.screen, accent, (x+5, y-13), (x+5, y+8), 3)
            pygame.draw.line(self.screen, accent, (x+5, y-13), (x+15, y-16), 3)
            pygame.draw.circle(self.screen, accent, (x-2, y+10), 6)
        else:
            pygame.draw.polygon(self.screen, accent,
                                [(x-15,y-7),(x-7,y-7),(x+5,y-16),(x+5,y+16),(x-7,y+7),(x-15,y+7)], 2)
            pygame.draw.arc(self.screen, accent, (x-2, y-12, 28, 24), -math.pi/3, math.pi/3, 2)
        if muted:
            pygame.draw.line(self.screen, self.WHITE,
                             (rect.left+12, rect.top+12), (rect.right-12, rect.bottom-12), 3)

    # Legacy procedural slider / mute-button fallbacks (kept for compatibility)
    def draw_slider(self, rect, value, muted):
        value = max(0.0, min(1.0, value))
        pygame.draw.rect(self.screen, (20, 30, 60),  rect.inflate(8, 10), border_radius=10)
        pygame.draw.rect(self.screen, (55, 80, 120), rect, border_radius=8)
        fill_w = int(rect.width * value)
        if fill_w > 0:
            pygame.draw.rect(self.screen, self.MUTED if muted else self.PINK,
                             pygame.Rect(rect.left, rect.top, fill_w, rect.height), border_radius=8)
        knob_x = int(rect.left + rect.width * value)
        pygame.draw.circle(self.screen, self.PANEL_2, (knob_x, rect.centery), 10)
        pygame.draw.circle(self.screen, self.MUTED if muted else self.PINK, (knob_x, rect.centery), 10, 2)

    def draw_mute_button(self, rect, label, muted, accent):
        hover  = rect.collidepoint(pygame.mouse.get_pos())
        border = self.WHITE if muted else (self.PINK if hover else accent)
        pygame.draw.rect(self.screen, self.PANEL_2, rect, border_radius=13)
        self.draw_neon_rect(rect, border, radius=13, thickness=2, glow=True)
        ix, iy = rect.left + 26, rect.centery
        pygame.draw.polygon(self.screen, border,
                            [(ix-9,iy-5),(ix-3,iy-5),(ix+6,iy-12),(ix+6,iy+12),(ix-3,iy+5),(ix-9,iy+5)], 2)
        if muted:
            pygame.draw.line(self.screen, self.WHITE, (ix-11, iy-13), (ix+10, iy+13), 3)
        t = self.font_small.render(label, True, self.WHITE)
        self.screen.blit(t, t.get_rect(center=(rect.centerx+12, rect.centery)))

    # ── Value helpers ────────────────────────────────────────────────────────

    def slider_value(self, rect, mouse_x):
        return max(0.0, min(1.0, (mouse_x - rect.left) / float(rect.width)))

    # ── Name acceptance ──────────────────────────────────────────────────────

    def accept_name(self):
        cleaned = " ".join(self.player_name.strip().split())
        if not cleaned:
            return False
        self.player_name = cleaned[:24]
        self.finished    = True
        self.play_click()
        return True

    # ── Hover sound ──────────────────────────────────────────────────────────

    def update_hover_sound(self):
        mouse   = pygame.mouse.get_pos()
        targets = set()
        if not self.audio_menu_open:
            if self.menu_rect.collidepoint(mouse):  targets.add("menu")
            if self.input_rect.collidepoint(mouse): targets.add("input")
            if self.enter_rect.collidepoint(mouse): targets.add("enter")
        else:
            if self.audio_close_rect.collidepoint(mouse): targets.add("close")
            if self.mute_music_rect.collidepoint(mouse):  targets.add("mute_music")
            if self.mute_sfx_rect.collidepoint(mouse):    targets.add("mute_sfx")
        if targets - self.last_hover:
            self.play_hover()
        self.last_hover = targets

    # ── Events ───────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.stop_music()
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.audio_menu_open:
                    self.audio_menu_open = self.dragging_music = self.dragging_sfx = False
                    return ""
                self.stop_music()
                return None
            if self.audio_menu_open:
                return ""
            if event.key == pygame.K_RETURN:
                self.accept_name()
            elif event.key == pygame.K_BACKSPACE and self.name_active:
                self.player_name = self.player_name[:-1]
            elif (self.name_active and event.unicode
                  and event.unicode.isprintable() and len(self.player_name) < 24):
                self.player_name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = event.pos
            if self.audio_menu_open:
                if self.audio_close_rect.collidepoint(mouse):
                    self.play_click()
                    self.audio_menu_open = self.dragging_music = self.dragging_sfx = False
                    return ""
                if self.music_track_rect.inflate(0, 28).collidepoint(mouse):
                    self.dragging_music = True
                    self.music_volume   = self.slider_value(self.music_track_rect, mouse[0])
                    self.update_music_volume()
                    return ""
                if self.sfx_track_rect.inflate(0, 28).collidepoint(mouse):
                    self.dragging_sfx = True
                    self.sfx_volume   = self.slider_value(self.sfx_track_rect, mouse[0])
                    self.update_sfx_volume()
                    return ""
                if self.mute_music_rect.collidepoint(mouse):
                    self.play_click(); self.toggle_music_mute(); return ""
                if self.mute_sfx_rect.collidepoint(mouse):
                    self.play_click(); self.toggle_sfx_mute();   return ""
                return ""

            if self.menu_rect.collidepoint(mouse):
                self.play_click(); self.audio_menu_open = True; self.name_active = False; return ""
            if self.input_rect.collidepoint(mouse):
                self.play_click(); self.name_active = True; return ""
            if self.enter_rect.collidepoint(mouse):
                self.accept_name(); return ""

        if event.type == pygame.MOUSEMOTION and self.audio_menu_open:
            if self.dragging_music:
                self.music_volume = self.slider_value(self.music_track_rect, event.pos[0])
                self.update_music_volume()
            if self.dragging_sfx:
                self.sfx_volume = self.slider_value(self.sfx_track_rect, event.pos[0])
                self.update_sfx_volume()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_music = self.dragging_sfx = False

        return "START" if self.finished else ""

    # ── Draw & run ───────────────────────────────────────────────────────────

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


# ── Standalone test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((StartScreen.WIDTH, StartScreen.HEIGHT))
    pygame.display.set_caption("Cyberpunk Café")
    player = StartScreen(screen).run()
    print(f"Player name: {player}")
    pygame.quit()
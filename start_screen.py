import os
import pygame

class StartScreen:
    """Cyberpunk Café — Start Screen (1280 × 720).
    Compact, high-performance, and fully asset-integrated.
    """
    WIDTH, HEIGHT, FPS = 1280, 720, 60

    # ── Theme Colors ──────────────────────────────────────────────────────────
    CYAN    = (45, 226, 255)
    PINK    = (255, 55, 210)
    GOLD    = (255, 190, 62)
    WHITE   = (245, 247, 255)
    PANEL   = (8, 14, 35)
    PANEL_2 = (11, 19, 46)
    DARK    = (15, 18, 35)
    MUTED   = (120, 130, 160)

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # State
        self.player_name = ""
        self.name_active = False
        self.finished = False
        self.audio_menu_open = False
        self.music_volume = 0.30
        self.sfx_volume = 0.16
        self.music_muted = False
        self.sfx_muted = False
        self.dragging_music = False
        self.dragging_sfx = False
        self.last_hover = set()

        # Paths & Assets
        root = os.path.dirname(os.path.abspath(__file__))
        self.start_root = os.path.join(root, "assets", "mahirah", "start")
        self.ui_root    = os.path.join(root, "assets", "mahirah", "ui")
        self.audio_root = os.path.join(root, "assets", "mahirah", "audio")
        self.font_root  = os.path.join(root, "assets", "fonts")

        self._load_all_assets()
        self._init_fonts()
        self._init_layout()
        self._init_audio()

    @property
    def muted(self):
        return self.music_muted

    # ── Asset & Font Initialization ──────────────────────────────────────────

    def _load_img(self, folder, name, trim=False):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            return None
        try:
            surf = pygame.image.load(path).convert_alpha()
            if trim:
                bb = surf.get_bounding_rect()
                if bb.width and bb.height:
                    surf = surf.subsurface(bb).copy()
            return surf
        except Exception:
            return None

    def _load_all_assets(self):
        sf, uf = self.start_root, self.ui_root
        # Main Start UI
        self.bg            = self._load_img(sf, "start_bg.png")
        self.logo          = self._load_img(sf, "logo_cyberpunk_cafe.png")
        self.btn_enter     = self._load_img(sf, "button_enter.png", trim=True)
        self.btn_enter_h   = self._load_img(sf, "button_enter_hover.png", trim=True)
        self.btn_menu      = self._load_img(sf, "button_menu.png", trim=True)
        self.btn_menu_h    = self._load_img(sf, "button_menu_hover.png", trim=True)
        self.input_bg      = self._load_img(sf, "input_name.png", trim=True)
        self.input_bg_act  = self._load_img(sf, "input_name_active.png", trim=True)

        # Audio Dialog UI
        self.audio_header  = self._load_img(uf, "audio_settings_header.png", trim=True)
        self.btn_close     = self._load_img(uf, "button_close.png", trim=True)
        self.btn_close_h   = self._load_img(uf, "button_close_hover.png", trim=True)
        self.btn_mute      = self._load_img(uf, "button_mute.png", trim=True)
        self.btn_mute_h    = self._load_img(uf, "button_mute_hover.png", trim=True)
        self.icon_music_on = self._load_img(uf, "icon_music_on.png", trim=True)
        self.icon_music_off= self._load_img(uf, "icon_music_off.png", trim=True)
        self.icon_sfx_on   = self._load_img(uf, "icon_sound_on.png", trim=True)
        self.icon_sfx_off  = self._load_img(uf, "icon_sound_off.png", trim=True)
        self.track_music   = self._load_img(uf, "slider_music_track.png", trim=True)
        self.track_sound   = self._load_img(uf, "slider_sound_track.png", trim=True)
        self.slider_fill   = self._load_img(uf, "slider_fill.png", trim=True)
        self.slider_knob   = self._load_img(uf, "slider_knob.png", trim=True)

    def _init_fonts(self):
        pygame.font.init()
        # Find best title font (Orbitron or Audiowide, fallback to Segoe UI)
        title_font_path = None
        for fn in ["Orbitron-Bold.ttf", "Audiowide-Regular.ttf", "Orbitron-Medium.ttf"]:
            p = os.path.join(self.font_root, fn)
            if os.path.isfile(p):
                title_font_path = p
                break

        def make_font(size, bold=False, title=False):
            if title and title_font_path:
                return pygame.font.Font(title_font_path, size)
            for fam in ["Segoe UI Semibold", "Segoe UI", "Arial"]:
                f = pygame.font.match_font(fam)
                if f:
                    res = pygame.font.Font(f, size)
                    res.set_bold(bold)
                    return res
            return pygame.font.SysFont("Segoe UI", size, bold=bold)

        self.font_welcome = make_font(34, bold=True, title=True)
        self.font_sub     = make_font(18, bold=True)
        self.font_input   = make_font(18)
        self.font_btn     = make_font(22, bold=True)
        self.font_panel   = make_font(16, bold=True)
        self.font_pct     = make_font(15, bold=True)
        self.font_small   = make_font(12, bold=True)

    def _init_layout(self):
        cx = self.WIDTH // 2
        self.logo_rect      = pygame.Rect(185, 70, 910, 255)
        self.welcome_center = (cx, 368)
        self.question_center= (cx, 412)
        self.input_rect     = pygame.Rect(cx - 385, 430, 770, 100)
        self.enter_rect     = pygame.Rect(cx - 350, 545, 700, 100)
        self.menu_rect      = pygame.Rect(1015, 25, 240, 80)

        # Audio Panel
        self.audio_panel       = pygame.Rect(865, 180, 390, 505)
        self.audio_header_rect = pygame.Rect(888, 214, 292, 68)
        self.audio_close_rect  = pygame.Rect(1202, 216, 38, 38)
        self.icon_music_rect   = pygame.Rect(895, 313, 62, 62)
        self.icon_sfx_rect     = pygame.Rect(895, 403, 62, 62)
        self.music_track_rect  = pygame.Rect(962, 329, 218, 32)
        self.sfx_track_rect    = pygame.Rect(962, 419, 218, 32)
        self.music_pct_rect    = pygame.Rect(1180, 322, 55, 45)
        self.sfx_pct_rect      = pygame.Rect(1180, 412, 55, 45)
        self.mute_music_rect   = pygame.Rect(890, 505, 160, 70)
        self.mute_sfx_rect     = pygame.Rect(1070, 505, 160, 70)

    def _init_audio(self):
        self.click_sound = None
        self.hover_sound = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            theme = os.path.join(self.audio_root, "cyberpunk_cafe_theme.wav")
            if os.path.isfile(theme):
                pygame.mixer.music.load(theme)
                self.update_music_volume()
                pygame.mixer.music.play(-1)
            click_p = os.path.join(self.audio_root, "button_click.wav")
            hover_p = os.path.join(self.audio_root, "button_hover.wav")
            if os.path.isfile(click_p):
                self.click_sound = pygame.mixer.Sound(click_p)
            if os.path.isfile(hover_p):
                self.hover_sound = pygame.mixer.Sound(hover_p)
            self.update_sfx_volume()
        except pygame.error as e:
            print(f"[AUDIO] Init error: {e}")

    # ── Audio Control ────────────────────────────────────────────────────────

    def update_music_volume(self):
        try:
            pygame.mixer.music.set_volume(0.0 if self.music_muted else self.music_volume)
        except pygame.error:
            pass

    def update_sfx_volume(self):
        vol = 0.0 if self.sfx_muted else self.sfx_volume
        if self.click_sound: self.click_sound.set_volume(vol)
        if self.hover_sound: self.hover_sound.set_volume(vol)

    def play_click(self):
        if self.click_sound and not self.sfx_muted:
            self.click_sound.play()

    def play_hover(self):
        if self.hover_sound and not self.sfx_muted:
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

    # ── Drawing Primitives ───────────────────────────────────────────────────

    def draw_fit(self, img, box):
        """Fit image within box preserving aspect ratio."""
        if not img:
            return pygame.Rect(box)
        w, h = img.get_size()
        scale = min(box.width / w, box.height / h)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        rect = pygame.Rect(box.centerx - nw // 2, box.centery - nh // 2, nw, nh)
        self.screen.blit(pygame.transform.smoothscale(img, (nw, nh)), rect)
        return rect

    def draw_neon_rect(self, rect, color, radius=16, thickness=2, glow=True):
        if glow:
            surf = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            for pad, alpha in [(8, 30), (4, 60)]:
                pygame.draw.rect(surf, (*color, alpha), rect.inflate(pad, pad),
                                 width=thickness + 2, border_radius=radius + 2)
            self.screen.blit(surf, (0, 0))
        pygame.draw.rect(self.screen, color, rect, width=thickness, border_radius=radius)

    def draw_glow_text(self, text, font, center, color, glow_color=CYAN):
        base = font.render(text, True, color)
        for offset, alpha in [(-2, 35), (2, 35), (-1, 65), (1, 65)]:
            glow = font.render(text, True, glow_color)
            glow.set_alpha(alpha)
            self.screen.blit(glow, glow.get_rect(center=(center[0] + offset, center[1])))
            self.screen.blit(glow, glow.get_rect(center=(center[0], center[1] + offset)))
        r = base.get_rect(center=center)
        self.screen.blit(base, r)
        return r

    # ── Screen Component Drawing ─────────────────────────────────────────────

    def draw_background(self):
        if self.bg:
            self.screen.blit(pygame.transform.smoothscale(self.bg, (self.WIDTH, self.HEIGHT)), (0, 0))
        else:
            self.screen.fill(self.DARK)
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 24, 45))
        self.screen.blit(overlay, (0, 0))

    def draw_main_ui(self):
        mouse = pygame.mouse.get_pos()

        # Logo
        if self.logo:
            self.draw_fit(self.logo, self.logo_rect)
        else:
            self.draw_glow_text("CYBERPUNK CAFÉ", self.font_welcome, self.logo_rect.center, self.WHITE)

        # Welcome text
        name_str = (self.player_name.strip() or "BARISTA").upper()
        self.draw_glow_text(f"WELCOME, {name_str}", self.font_welcome, self.welcome_center, self.WHITE, self.CYAN)
        sub = self.font_sub.render("WHAT'S YOUR NAME?", True, self.WHITE)
        self.screen.blit(sub, sub.get_rect(center=self.question_center))

        # Name input box
        inp_img = self.input_bg_act if (self.name_active and self.input_bg_act) else self.input_bg
        if inp_img:
            self.draw_fit(inp_img, self.input_rect)
        else:
            pygame.draw.rect(self.screen, self.PANEL, self.input_rect, border_radius=18)
            self.draw_neon_rect(self.input_rect, self.PINK if self.name_active else self.CYAN, radius=18)

        # Input text & cursor
        display_text = self.player_name or "Enter your name..."
        color = self.WHITE if self.player_name else self.MUTED
        txt_surf = self.font_input.render(display_text, True, color)
        txt_rect = txt_surf.get_rect(midleft=(self.input_rect.left + 92, self.input_rect.centery))
        self.screen.blit(txt_surf, txt_rect)

        if self.name_active and (pygame.time.get_ticks() // 500) % 2 == 0:
            cx = min(txt_rect.right + 4, self.input_rect.right - 30)
            pygame.draw.line(self.screen, self.CYAN, (cx, self.input_rect.centery - 14),
                             (cx, self.input_rect.centery + 14), 2)

        # Enter café button
        hover_enter = self.enter_rect.collidepoint(mouse)
        enter_img = self.btn_enter_h if (hover_enter and self.btn_enter_h) else self.btn_enter
        if enter_img:
            self.draw_fit(enter_img, self.enter_rect)
        else:
            pygame.draw.rect(self.screen, self.DARK, self.enter_rect, border_radius=20)
            self.draw_neon_rect(self.enter_rect, self.GOLD, radius=20, glow=True)
            t = self.font_btn.render("ENTER CAFÉ >>", True, self.GOLD)
            self.screen.blit(t, t.get_rect(center=self.enter_rect.center))

        # Top-right Menu button
        hover_menu = self.menu_rect.collidepoint(mouse)
        menu_img = self.btn_menu_h if (hover_menu and self.btn_menu_h) else self.btn_menu
        if menu_img:
            self.draw_fit(menu_img, self.menu_rect)
        else:
            pygame.draw.rect(self.screen, self.PANEL, self.menu_rect, border_radius=16)
            self.draw_neon_rect(self.menu_rect, self.PINK if hover_menu else self.CYAN, radius=16)
            t = self.font_btn.render("MENU", True, self.WHITE)
            self.screen.blit(t, t.get_rect(center=self.menu_rect.center))

    def draw_slider(self, track_img, rect, val, muted):
        val = max(0.0, min(1.0, val))
        if track_img:
            self.screen.blit(pygame.transform.smoothscale(track_img, rect.size), rect)
        else:
            pygame.draw.rect(self.screen, (35, 50, 85), rect, border_radius=9)

        fill_w = int(rect.width * val)
        if fill_w > 0:
            fill_rect = pygame.Rect(rect.left, rect.top, fill_w, rect.height)
            if self.slider_fill:
                scaled = pygame.transform.smoothscale(self.slider_fill, (fill_w, rect.height))
                old_clip = self.screen.get_clip()
                self.screen.set_clip(rect)
                self.screen.blit(scaled, fill_rect)
                self.screen.set_clip(old_clip)
            else:
                pygame.draw.rect(self.screen, self.MUTED if muted else self.PINK, fill_rect, border_radius=8)

        knob_x = int(rect.left + rect.width * val)
        if self.slider_knob:
            self.draw_fit(self.slider_knob, pygame.Rect(knob_x - 19, rect.centery - 19, 38, 38))
        else:
            pygame.draw.circle(self.screen, self.MUTED if muted else self.PINK, (knob_x, rect.centery), 9)

    def draw_mute_button(self, box, label, muted, accent):
        hover = box.collidepoint(pygame.mouse.get_pos())
        img = self.btn_mute_h if (hover and self.btn_mute_h) else self.btn_mute
        if img:
            self.draw_fit(img, box)
        else:
            pygame.draw.rect(self.screen, self.PANEL_2, box, border_radius=12)
            self.draw_neon_rect(box, accent, radius=12)
            t = self.font_small.render(label, True, self.WHITE)
            self.screen.blit(t, t.get_rect(center=box.center))

    def draw_audio_icon(self, box, kind, muted):
        img = (self.icon_music_off if muted else self.icon_music_on) if kind == "music" \
              else (self.icon_sfx_off if muted else self.icon_sfx_on)
        if img:
            self.draw_fit(img, box)
        else:
            color = self.MUTED if muted else (self.PINK if kind == "music" else self.CYAN)
            pygame.draw.circle(self.screen, self.PANEL_2, box.center, 25)
            pygame.draw.circle(self.screen, color, box.center, 25, 2)

    def draw_audio_dialog(self):
        mouse = pygame.mouse.get_pos()

        # Dimmed backdrop & panel box
        veil = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 10, 100))
        self.screen.blit(veil, (0, 0))

        pygame.draw.rect(self.screen, self.PANEL, self.audio_panel, border_radius=22)
        self.draw_neon_rect(self.audio_panel, self.CYAN, radius=22)

        # Header & Close button
        if self.audio_header:
            self.draw_fit(self.audio_header, self.audio_header_rect)
        else:
            t = self.font_panel.render("AUDIO SETTINGS", True, self.WHITE)
            self.screen.blit(t, t.get_rect(center=self.audio_header_rect.center))

        hover_close = self.audio_close_rect.collidepoint(mouse)
        close_img = self.btn_close_h if (hover_close and self.btn_close_h) else self.btn_close
        if close_img:
            self.draw_fit(close_img, self.audio_close_rect)
        else:
            pygame.draw.rect(self.screen, self.PANEL_2, self.audio_close_rect, border_radius=8)
            self.draw_neon_rect(self.audio_close_rect, self.PINK, radius=8)

        # Dividers
        pygame.draw.line(self.screen, (55, 105, 150), (self.audio_panel.left + 25, 300), (self.audio_panel.right - 25, 300), 1)
        pygame.draw.line(self.screen, (55, 105, 150), (self.audio_panel.left + 25, 600), (self.audio_panel.right - 25, 600), 1)

        # Sliders & Icons
        self.draw_audio_icon(self.icon_music_rect, "music", self.music_muted)
        self.draw_audio_icon(self.icon_sfx_rect, "sound", self.sfx_muted)

        lbl_m = self.font_panel.render("MUSIC VOLUME", True, self.WHITE)
        lbl_s = self.font_panel.render("SOUND EFFECTS", True, self.WHITE)
        self.screen.blit(lbl_m, (965, 308))
        self.screen.blit(lbl_s, (965, 398))

        self.draw_slider(self.track_music, self.music_track_rect, self.music_volume, self.music_muted)
        self.draw_slider(self.track_sound, self.sfx_track_rect, self.sfx_volume, self.sfx_muted)

        pct_m = self.font_pct.render(f"{int(self.music_volume * 100)}%", True, self.WHITE)
        pct_s = self.font_pct.render(f"{int(self.sfx_volume * 100)}%", True, self.WHITE)
        self.screen.blit(pct_m, pct_m.get_rect(center=self.music_pct_rect.center))
        self.screen.blit(pct_s, pct_s.get_rect(center=self.sfx_pct_rect.center))

        # Mute Buttons
        self.draw_mute_button(self.mute_music_rect, "MUTE MUSIC", self.music_muted, self.PINK)
        self.draw_mute_button(self.mute_sfx_rect, "MUTE SFX", self.sfx_muted, self.CYAN)

        # Footer
        footer = self.font_small.render("GOOD DRINKS  •  BRIGHTER PEOPLE", True, (105, 165, 225))
        self.screen.blit(footer, footer.get_rect(center=(self.audio_panel.centerx, 630)))

    # ── Event Handling & Loop ────────────────────────────────────────────────

    def accept_name(self):
        cleaned = " ".join(self.player_name.strip().split())
        if not cleaned:
            return False
        self.player_name = cleaned[:24]
        self.finished = True
        self.play_click()
        return True

    def _slider_val(self, rect, mouse_x):
        return max(0.0, min(1.0, (mouse_x - rect.left) / float(rect.width)))

    def update_hover_sound(self):
        m = pygame.mouse.get_pos()
        if self.audio_menu_open:
            active = {k for k, r in [("close", self.audio_close_rect), ("mute_m", self.mute_music_rect),
                                     ("mute_s", self.mute_sfx_rect)] if r.collidepoint(m)}
        else:
            active = {k for k, r in [("menu", self.menu_rect), ("input", self.input_rect),
                                     ("enter", self.enter_rect)] if r.collidepoint(m)}
        if active - self.last_hover:
            self.play_hover()
        self.last_hover = active

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

            if not self.audio_menu_open:
                if event.key == pygame.K_RETURN:
                    self.accept_name()
                elif event.key == pygame.K_BACKSPACE and self.name_active:
                    self.player_name = self.player_name[:-1]
                elif self.name_active and event.unicode and event.unicode.isprintable() and len(self.player_name) < 24:
                    self.player_name += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m = event.pos
            if self.audio_menu_open:
                if self.audio_close_rect.collidepoint(m):
                    self.play_click()
                    self.audio_menu_open = self.dragging_music = self.dragging_sfx = False
                elif self.music_track_rect.inflate(0, 24).collidepoint(m):
                    self.dragging_music = True
                    self.music_volume = self._slider_val(self.music_track_rect, m[0])
                    self.update_music_volume()
                elif self.sfx_track_rect.inflate(0, 24).collidepoint(m):
                    self.dragging_sfx = True
                    self.sfx_volume = self._slider_val(self.sfx_track_rect, m[0])
                    self.update_sfx_volume()
                elif self.mute_music_rect.collidepoint(m):
                    self.play_click()
                    self.toggle_music_mute()
                elif self.mute_sfx_rect.collidepoint(m):
                    self.play_click()
                    self.toggle_sfx_mute()
            else:
                if self.menu_rect.collidepoint(m):
                    self.play_click()
                    self.audio_menu_open = True
                    self.name_active = False
                elif self.input_rect.collidepoint(m):
                    self.play_click()
                    self.name_active = True
                elif self.enter_rect.collidepoint(m):
                    self.accept_name()
                else:
                    self.name_active = False

        elif event.type == pygame.MOUSEMOTION and self.audio_menu_open:
            if self.dragging_music:
                self.music_volume = self._slider_val(self.music_track_rect, event.pos[0])
                self.update_music_volume()
            if self.dragging_sfx:
                self.sfx_volume = self._slider_val(self.sfx_track_rect, event.pos[0])
                self.update_sfx_volume()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_music = self.dragging_sfx = False

        return "START" if self.finished else ""

    def draw(self):
        self.draw_background()
        self.draw_main_ui()
        if self.audio_menu_open:
            self.draw_audio_dialog()
        self.update_hover_sound()
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                res = self.handle_event(event)
                if res is None:
                    return None
                if res == "START":
                    self.stop_music()
                    return self.player_name
            self.draw()
            self.clock.tick(self.FPS)

if __name__ == "__main__":
    pygame.init()
    scr = pygame.display.set_mode((StartScreen.WIDTH, StartScreen.HEIGHT))
    pygame.display.set_caption("Cyberpunk Café")
    name = StartScreen(scr).run()
    print(f"Selected Barista Name: {name}")
    pygame.quit()
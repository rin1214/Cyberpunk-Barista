import os
import pygame

# --- Audio file locations ---
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
MUSIC_FILE = os.path.join(AUDIO_DIR, "cyberpunk_cafe_theme.wav")

# The one AudioSettings object shared by every screen
_active_audio = None


class AudioSettings:
    DEFAULT_MUSIC_VOLUME = 0.80   
    DEFAULT_SFX_VOLUME = 0.16

    def __init__(self, music_volume=DEFAULT_MUSIC_VOLUME, sfx_volume=DEFAULT_SFX_VOLUME):
        global _active_audio
        _active_audio = self

        # --- State ---
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self.music_muted = False
        self.sfx_muted = False
        self.dragging_slider = None          # None, "music" or "sfx"
        self.registered_sfx = []             # pygame.mixer.Sound objects kept in sync
        self.sfx = {}                        # named gameplay sounds: click / hover / blender
        self._hover_key = None               # which button the mouse is currently over
        self._music_missing_reported = False

        # --- Layout ---
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.music_track = pygame.Rect(0, 0, 0, 0)
        self.sfx_track = pygame.Rect(0, 0, 0, 0)
        self.music_mute_btn = pygame.Rect(0, 0, 0, 0)
        self.sfx_mute_btn = pygame.Rect(0, 0, 0, 0)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def set_layout(self, panel_rect):
        """Position the audio controls inside the centered menu panel."""
        self.panel_rect = pygame.Rect(panel_rect)
        x, y = self.panel_rect.x, self.panel_rect.y
        self.music_track = pygame.Rect(x + 180, y + 175, 360, 14)
        self.sfx_track = pygame.Rect(x + 180, y + 265, 360, 14)
        self.music_mute_btn = pygame.Rect(x + 100, y + 335, 220, 44)
        self.sfx_mute_btn = pygame.Rect(x + 380, y + 335, 220, 44)

    # ------------------------------------------------------------------
    # Volume control
    # ------------------------------------------------------------------
    def register_sfx_sound(self, sound_obj):
        """Register a pygame Sound so its volume stays synchronized."""
        if sound_obj and sound_obj not in self.registered_sfx:
            self.registered_sfx.append(sound_obj)
            sound_obj.set_volume(self.get_effective_sfx_volume())

    def get_effective_music_volume(self):
        return 0.0 if self.music_muted else self.music_volume

    def get_effective_sfx_volume(self):
        """Actual sound effects volume (0.0 if muted)."""
        return 0.0 if self.sfx_muted else self.sfx_volume

    def apply_volumes(self):
        """Apply current volume and mute settings directly to the pygame mixer."""
        if not pygame.mixer.get_init():
            return
        pygame.mixer.music.set_volume(self.get_effective_music_volume())
        sfx_vol = self.get_effective_sfx_volume()
        for snd in self.registered_sfx:
            try:
                snd.set_volume(sfx_vol)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Gameplay sound effects
    # ------------------------------------------------------------------
    SFX_FILES = {
        "click": "button_click.wav",
        "hover": "button_hover.wav",
        "blender": "blender.wav",
    }

    def load_sfx(self, audio_dir=AUDIO_DIR):
        """Load the sound effects from audio_dir (safe to call more than once).
        A missing file is skipped, so that sound simply stays silent."""
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error as error:
                print(f"[AUDIO] Could not start mixer: {error}")
                return
        for name, filename in self.SFX_FILES.items():
            if name in self.sfx:
                continue
            path = os.path.join(audio_dir, filename)
            if not os.path.isfile(path):
                print(f"[AUDIO] Sound effect not found: {path}")
                continue
            try:
                sound = pygame.mixer.Sound(path)
            except pygame.error as error:
                print(f"[AUDIO] Could not load {filename}: {error}")
                continue
            self.sfx[name] = sound
            self.register_sfx_sound(sound)

    def play_sfx(self, name):
        sound = self.sfx.get(name)
        if sound is not None and not self.sfx_muted:
            sound.play()

    def play_click(self):
        self.play_sfx("click")

    def play_hover(self):
        self.play_sfx("hover")

    def update_hover(self, key):
        """Call every frame with the id of the button under the mouse (or None).
        Plays the hover sound once each time the mouse enters a new button."""
        if key != self._hover_key:
            self._hover_key = key
            if key is not None:
                self.play_hover()

    def stop_sfx(self, name, fade_ms=0):
        sound = self.sfx.get(name)
        if sound is None:
            return
        if fade_ms > 0:
            sound.fadeout(fade_ms)
        else:
            sound.stop()

    # ------------------------------------------------------------------
    # Background music
    # ------------------------------------------------------------------
    def start_music(self, restart=True):
        """Load and loop the theme at the current volume.
        restart=False leaves it alone if it is already playing."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if not os.path.isfile(MUSIC_FILE):
                if not self._music_missing_reported:
                    print(f"[AUDIO] Music not found: {MUSIC_FILE}")
                    self._music_missing_reported = True
                return False
            if restart or not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.play(-1)
            self.apply_volumes()
            return True
        except pygame.error as error:
            print(f"[AUDIO ERROR] {error}")
            return False

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    @staticmethod
    def _slider_value(track, mouse_x):
        return max(0.0, min(1.0, (mouse_x - track.x) / track.width))

    def handle_mouse_down(self, pos):
        """Handle a left click. Returns True if the click hit an audio control."""
        if self.music_track.inflate(20, 20).collidepoint(pos):
            self.dragging_slider = "music"
            self.music_volume = self._slider_value(self.music_track, pos[0])
            self.apply_volumes()
            return True
        if self.sfx_track.inflate(20, 20).collidepoint(pos):
            self.dragging_slider = "sfx"
            self.sfx_volume = self._slider_value(self.sfx_track, pos[0])
            self.apply_volumes()
            return True
        if self.music_mute_btn.collidepoint(pos):
            self.music_muted = not self.music_muted
            self.apply_volumes()
            return True
        if self.sfx_mute_btn.collidepoint(pos):
            self.sfx_muted = not self.sfx_muted
            self.apply_volumes()
            return True
        return False

    def handle_mouse_up(self):
        self.dragging_slider = None

    def update_drag(self, mouse_x):
        """Call every frame while the menu is open so sliders follow the mouse."""
        if self.dragging_slider == "music":
            self.music_volume = self._slider_value(self.music_track, mouse_x)
            self.apply_volumes()
        elif self.dragging_slider == "sfx":
            self.sfx_volume = self._slider_value(self.sfx_track, mouse_x)
            self.apply_volumes()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, screen, ui):
        rect = self.panel_rect

        # Header title box
        head_box = pygame.Rect(rect.x + (rect.width - 400) // 2, rect.y + 25, 400, 48)
        ui._panel(screen, head_box, ui.CYAN, (12, 22, 48, 230), radius=12, width=2)
        htxt = ui.font_big_title.render("AUDIO SETTINGS", True, ui.CYAN_LIGHT)
        screen.blit(htxt, htxt.get_rect(center=head_box.center))

        # Subtitle under header
        sub = ui.font_small.render("CYBERPUNK CAFÉ  //  SYSTEM CONTROLS", True, ui.MUTED)
        screen.blit(sub, sub.get_rect(center=(rect.centerx, rect.y + 92)))

        # Separator line
        pygame.draw.line(screen, (35, 50, 85), (rect.x + 40, rect.y + 115), (rect.right - 40, rect.y + 115), 1)

        # --- MUSIC VOLUME ---
        m_lbl = ui.font_hud.render("MUSIC VOLUME", True, ui.WHITE)
        screen.blit(m_lbl, (rect.x + 180, rect.y + 145))

        pygame.draw.rect(screen, (15, 25, 50), self.music_track, border_radius=7)
        pygame.draw.rect(screen, ui.CYAN, self.music_track, width=1, border_radius=7)
        cur_m = 0.0 if self.music_muted else self.music_volume
        fill_m = pygame.Rect(self.music_track.x, self.music_track.y, int(self.music_track.width * cur_m), self.music_track.height)
        pygame.draw.rect(screen, ui.CYAN, fill_m, border_radius=7)

        hx = self.music_track.x + int(self.music_track.width * cur_m)
        pygame.draw.circle(screen, ui.PINK, (hx, self.music_track.centery), 11)
        pygame.draw.circle(screen, ui.WHITE, (hx, self.music_track.centery), 5)

        m_pct = ui.font_hud.render(f"{int(cur_m * 100)}%", True, ui.WHITE)
        screen.blit(m_pct, (self.music_track.right + 20, self.music_track.y - 2))

        # --- SOUND EFFECTS ---
        s_lbl = ui.font_hud.render("SOUND EFFECTS", True, ui.WHITE)
        screen.blit(s_lbl, (rect.x + 180, rect.y + 235))

        pygame.draw.rect(screen, (15, 25, 50), self.sfx_track, border_radius=7)
        pygame.draw.rect(screen, ui.CYAN, self.sfx_track, width=1, border_radius=7)
        cur_s = 0.0 if self.sfx_muted else self.sfx_volume
        fill_s = pygame.Rect(self.sfx_track.x, self.sfx_track.y, int(self.sfx_track.width * cur_s), self.sfx_track.height)
        pygame.draw.rect(screen, ui.PINK, fill_s, border_radius=7)

        shx = self.sfx_track.x + int(self.sfx_track.width * cur_s)
        pygame.draw.circle(screen, ui.CYAN, (shx, self.sfx_track.centery), 11)
        pygame.draw.circle(screen, ui.WHITE, (shx, self.sfx_track.centery), 5)

        s_pct = ui.font_hud.render(f"{int(cur_s * 100)}%", True, ui.WHITE)
        screen.blit(s_pct, (self.sfx_track.right + 20, self.sfx_track.y - 2))

        # --- MUTE BUTTONS ---
        m_txt = "UNMUTE MUSIC" if self.music_muted else "MUTE MUSIC"
        s_txt = "UNMUTE SFX" if self.sfx_muted else "MUTE SFX"
        ui._action_button(screen, self.music_mute_btn, m_txt, ui.PINK if self.music_muted else ui.CYAN, True, large=False)
        ui._action_button(screen, self.sfx_mute_btn, s_txt, ui.PINK if self.sfx_muted else ui.CYAN, True, large=False)


# ----------------------------------------------------------------------
# One shared AudioSettings for the whole game
# ----------------------------------------------------------------------
def get_audio():
    """Return the single AudioSettings object every screen shares (start screen,
    game screen...). It is created the first time it is asked for, so volume,
    mute state and loaded sounds carry over between screens."""
    if _active_audio is None:
        AudioSettings()          
    return _active_audio


def ensure_game_music(start_screen=None):
    """Make sure the theme is playing at the shared volume."""
    return get_audio().start_music(restart=False)


def keep_music_running(start_screen=None):
    """Call every frame: restarts the theme if it stopped."""
    if not pygame.mixer.get_init() or not pygame.mixer.music.get_busy():
        ensure_game_music(start_screen)
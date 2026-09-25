import os
import pygame


class AudioManager:

    def __init__(self, project_root=None):

        # ====================================================
        # PROJECT ROOT
        # ====================================================

        if project_root is None:

            project_root = os.path.dirname(
                os.path.abspath(__file__)
            )

        self.project_root = project_root

        # ====================================================
        # VOLUME SETTINGS
        # ====================================================

        self.music_volume = 0.45

        self.sfx_volume = 0.65

        # ====================================================
        # STATUS
        # ====================================================

        self.music_started = False

        self.initialised = False

        # ====================================================
        # SOUND STORAGE
        # ====================================================

        self.sounds = {}

        # ====================================================
        # INITIALISE AUDIO
        # ====================================================

        self._initialise_mixer()

        # ====================================================
        # LOAD MUSIC
        # ====================================================

        self._load_music()

        # ====================================================
        # LOAD SOUND EFFECTS
        # ====================================================

        self._load_sound_effects()

        self.initialised = True

    # ========================================================
    # AUDIO PATH
    # ========================================================

    def _audio_path(self, filename):

        return os.path.join(
            self.project_root,
            "assets",
            "mahirah",
            "audio",
            filename,
        )

    # ========================================================
    # INITIALISE MIXER
    # ========================================================

    def _initialise_mixer(self):

        try:

            if not pygame.mixer.get_init():

                pygame.mixer.init()

        except pygame.error as error:

            print(
                "[AUDIO] Mixer could not be initialised:"
            )

            print(
                f"[AUDIO] {error}"
            )

    # ========================================================
    # LOAD BACKGROUND MUSIC
    # ========================================================

    def _load_music(self):

        self.music_file = self._audio_path(
            "cyberpunk_cafe_theme.wav"
        )

        if os.path.exists(
            self.music_file
        ):

            print(
                "[AUDIO] Background music found."
            )

        else:

            print(
                "[AUDIO] WARNING: Background music not found:"
            )

            print(
                f"[AUDIO] {self.music_file}"
            )

    # ========================================================
    # LOAD SOUND EFFECTS
    # ========================================================

    def _load_sound_effects(self):

        sound_files = {

            "button_click":
                "button_click.wav",

            "button_hover":
                "button_hover.wav",

            "drink_select":
                "drink_select.wav",

            "customise":
                "customise.wav",

            "blend":
                "blend.wav",

            "drink_ready":
                "drink_ready.wav",

            "serve":
                "serve.wav",

            "correct":
                "correct.wav",

            "incorrect":
                "incorrect.wav",

            "level_up":
                "level_up.wav",

            "map":
                "map.wav",

            "leaderboard":
                "leaderboard.wav",
        }

        for sound_name, filename in sound_files.items():

            path = self._audio_path(
                filename
            )

            # ------------------------------------------------
            # OPTIONAL FILE
            # ------------------------------------------------

            if not os.path.exists(
                path
            ):

                print(
                    "[AUDIO] Optional SFX not found: "
                    f"{filename}"
                )

                continue

            # ------------------------------------------------
            # LOAD
            # ------------------------------------------------

            try:

                sound = pygame.mixer.Sound(
                    path
                )

                sound.set_volume(
                    self.sfx_volume
                )

                self.sounds[
                    sound_name
                ] = sound

                print(
                    f"[AUDIO] Loaded SFX: {filename}"
                )

            except pygame.error as error:

                print(
                    f"[AUDIO] Could not load {filename}:"
                )

                print(
                    f"[AUDIO] {error}"
                )

    # ========================================================
    # START MUSIC
    # ========================================================

    def play_music(
        self,
        fade_ms=1000,
    ):
        """
        Start the Cyberpunk Café background music.

        If music is already playing, DO NOTHING.

        This prevents the music from restarting whenever
        the player changes screens.
        """

        if not self.initialised:

            return

        if not os.path.exists(
            self.music_file
        ):

            return

        try:

            # ------------------------------------------------
            # DO NOT RESTART MUSIC
            # ------------------------------------------------

            if pygame.mixer.music.get_busy():

                self.music_started = True

                return

            # ------------------------------------------------
            # VOLUME
            # ------------------------------------------------

            pygame.mixer.music.set_volume(
                self.music_volume
            )

            # ------------------------------------------------
            # LOAD MUSIC
            # ------------------------------------------------

            pygame.mixer.music.load(
                self.music_file
            )

            # ------------------------------------------------
            # LOOP FOREVER
            # ------------------------------------------------

            pygame.mixer.music.play(
                loops=-1,
                fade_ms=fade_ms,
            )

            self.music_started = True

            print(
                "[AUDIO] Background music started."
            )

        except pygame.error as error:

            print(
                "[AUDIO] Could not start background music:"
            )

            print(
                f"[AUDIO] {error}"
            )

    # ========================================================
    # STOP MUSIC
    # ========================================================

    def stop_music(
        self,
        fade_ms=1000,
    ):

        try:

            if pygame.mixer.music.get_busy():

                pygame.mixer.music.fadeout(
                    fade_ms
                )

            self.music_started = False

        except pygame.error:

            pass

    # ========================================================
    # PAUSE MUSIC
    # ========================================================

    def pause_music(self):

        try:

            pygame.mixer.music.pause()

        except pygame.error:

            pass

    # ========================================================
    # RESUME MUSIC
    # ========================================================

    def resume_music(self):

        try:

            pygame.mixer.music.unpause()

        except pygame.error:

            pass

    # ========================================================
    # PLAY SOUND EFFECT
    # ========================================================

    def play_sfx(
        self,
        sound_name,
    ):

        sound = self.sounds.get(
            sound_name
        )

        if sound is None:

            return

        try:

            sound.set_volume(
                self.sfx_volume
            )

            sound.play()

        except pygame.error as error:

            print(
                f"[AUDIO] Could not play "
                f"{sound_name}:"
            )

            print(
                f"[AUDIO] {error}"
            )

    # ========================================================
    # MUSIC VOLUME
    # ========================================================

    def set_music_volume(
        self,
        volume,
    ):

        try:

            volume = float(
                volume
            )

        except (
            TypeError,
            ValueError,
        ):

            volume = self.music_volume

        self.music_volume = max(
            0.0,
            min(
                volume,
                1.0,
            ),
        )

        try:

            pygame.mixer.music.set_volume(
                self.music_volume
            )

        except pygame.error:

            pass

    # ========================================================
    # SFX VOLUME
    # ========================================================

    def set_sfx_volume(
        self,
        volume,
    ):

        try:

            volume = float(
                volume
            )

        except (
            TypeError,
            ValueError,
        ):

            volume = self.sfx_volume

        self.sfx_volume = max(
            0.0,
            min(
                volume,
                1.0,
            ),
        )

        for sound in self.sounds.values():

            sound.set_volume(
                self.sfx_volume
            )

    # ========================================================
    # MUTE MUSIC
    # ========================================================

    def mute_music(self):

        try:

            pygame.mixer.music.set_volume(
                0.0
            )

        except pygame.error:

            pass

    # ========================================================
    # UNMUTE MUSIC
    # ========================================================

    def unmute_music(self):

        try:

            pygame.mixer.music.set_volume(
                self.music_volume
            )

        except pygame.error:

            pass

    # ========================================================
    # MUTE SFX
    # ========================================================

    def mute_sfx(self):

        for sound in self.sounds.values():

            sound.set_volume(
                0.0
            )

    # ========================================================
    # UNMUTE SFX
    # ========================================================

    def unmute_sfx(self):

        for sound in self.sounds.values():

            sound.set_volume(
                self.sfx_volume
            )

    # ========================================================
    # SHUTDOWN
    # ========================================================

    def shutdown(self):

        try:

            pygame.mixer.music.stop()

            for sound in self.sounds.values():

                sound.stop()

        except pygame.error:

            pass
"""
CYBERPUNK CAFÉ
CENTRAL AUDIO MANAGER

This file controls:

    - Background music
    - Sound effects
    - Music volume
    - Sound-effect volume

IMPORTANT:

The audio manager is designed so that the same background
music can continue across the entire game.

The music should NOT restart every time the player changes
from one screen to another.

Game flow:

    Start Screen
        ↓
    Loading Screen
        ↓
    Gameplay
        ↓
    Level Unlock Screen
        ↓
    Loading Screen
        ↓
    Gameplay
        ↓
    Map
        ↓
    Leaderboard

The AudioManager stays alive throughout this process.
"""


import os
import pygame


class AudioManager:
    """
    Central manager for all Cyberpunk Café audio.
    """

    # ============================================================
    # INITIALISATION
    # ============================================================

    def __init__(self, project_root=None):
        """
        Create the audio manager.

        project_root:
            The main folder of the Cyberpunk Café project.

        If it is not provided, the folder containing this file
        is used.
        """

        if project_root is None:
            project_root = os.path.dirname(
                os.path.abspath(__file__)
            )

        self.project_root = project_root

        # --------------------------------------------------------
        # AUDIO SETTINGS
        # --------------------------------------------------------

        self.music_volume = 0.45
        self.sfx_volume = 0.65

        self.music_started = False
        self.initialised = False

        # --------------------------------------------------------
        # SOUND STORAGE
        # --------------------------------------------------------

        self.sounds = {}

        # --------------------------------------------------------
        # INITIALISE PYGAME MIXER
        # --------------------------------------------------------

        self._initialise_mixer()

        # --------------------------------------------------------
        # LOAD AUDIO
        # --------------------------------------------------------

        self._load_music()
        self._load_sound_effects()

        self.initialised = True

    # ============================================================
    # PATH HELPERS
    # ============================================================

    def _audio_path(self, filename):
        """
        Return the absolute path to an audio file.

        All Cyberpunk Café audio is stored under:

            assets/mahirah/audio/
        """

        return os.path.join(
            self.project_root,
            "assets",
            "mahirah",
            "audio",
            filename
        )

    # ============================================================
    # MIXER
    # ============================================================

    def _initialise_mixer(self):
        """
        Initialise pygame's audio mixer.

        If audio cannot be initialised, the game can still run.
        """

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

    # ============================================================
    # MUSIC
    # ============================================================

    def _load_music(self):
        """
        Store the path to the Cyberpunk Café background music.
        """

        self.music_file = self._audio_path(
            "cyberpunk_cafe_theme.wav"
        )

        if os.path.exists(self.music_file):
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

    # ============================================================
    # SOUND EFFECTS
    # ============================================================

    def _load_sound_effects(self):
        """
        Load available sound effects.

        Missing sound effects do NOT crash the game.
        """

        sound_files = {
            "button_click": "button_click.wav",
            "button_hover": "button_hover.wav",
            "drink_select": "drink_select.wav",
            "customise": "customise.wav",
            "blend": "blend.wav",
            "drink_ready": "drink_ready.wav",
            "serve": "serve.wav",
            "correct": "correct.wav",
            "incorrect": "incorrect.wav",
            "level_up": "level_up.wav",
            "map": "map.wav",
            "leaderboard": "leaderboard.wav",
        }

        for sound_name, filename in sound_files.items():

            path = self._audio_path(
                filename
            )

            if not os.path.exists(path):
                print(
                    f"[AUDIO] Optional SFX not found: {filename}"
                )
                continue

            try:
                sound = pygame.mixer.Sound(
                    path
                )

                sound.set_volume(
                    self.sfx_volume
                )

                self.sounds[sound_name] = sound

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

    # ============================================================
    # START MUSIC
    # ============================================================

    def play_music(self, fade_ms=1000):
        """
        Start the background music.

        IMPORTANT:

        If the music is already playing, this method does
        NOTHING.

        Therefore changing screens will not restart the music.
        """

        if not self.initialised:
            return

        if not os.path.exists(
            self.music_file
        ):
            return

        try:

            # If music is already playing, leave it alone.
            if pygame.mixer.music.get_busy():

                self.music_started = True

                return

            pygame.mixer.music.set_volume(
                self.music_volume
            )

            pygame.mixer.music.load(
                self.music_file
            )

            pygame.mixer.music.play(
                loops=-1,
                fade_ms=fade_ms
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

    # ============================================================
    # STOP MUSIC
    # ============================================================

    def stop_music(self, fade_ms=1000):
        """
        Stop the background music.

        This should normally only be used when completely
        closing the game.
        """

        try:

            if pygame.mixer.music.get_busy():

                pygame.mixer.music.fadeout(
                    fade_ms
                )

            self.music_started = False

        except pygame.error as error:

            print(
                "[AUDIO] Could not stop music:"
            )
            print(
                f"[AUDIO] {error}"
            )

    # ============================================================
    # PAUSE MUSIC
    # ============================================================

    def pause_music(self):
        """
        Temporarily pause the background music.
        """

        try:

            pygame.mixer.music.pause()

        except pygame.error as error:

            print(
                "[AUDIO] Could not pause music:"
            )
            print(
                f"[AUDIO] {error}"
            )

    # ============================================================
    # RESUME MUSIC
    # ============================================================

    def resume_music(self):
        """
        Resume previously paused background music.
        """

        try:

            pygame.mixer.music.unpause()

        except pygame.error as error:

            print(
                "[AUDIO] Could not resume music:"
            )
            print(
                f"[AUDIO] {error}"
            )

    # ============================================================
    # PLAY SOUND EFFECT
    # ============================================================

    def play_sfx(self, sound_name):
        """
        Play a loaded sound effect.

        Example:

            audio.play_sfx("button_click")
        """

        if sound_name not in self.sounds:
            return

        try:

            sound = self.sounds[
                sound_name
            ]

            sound.set_volume(
                self.sfx_volume
            )

            sound.play()

        except pygame.error as error:

            print(
                f"[AUDIO] Could not play {sound_name}:"
            )
            print(
                f"[AUDIO] {error}"
            )

    # ============================================================
    # VOLUME
    # ============================================================

    def set_music_volume(self, volume):
        """
        Set music volume from 0.0 to 1.0.
        """

        self.music_volume = max(
            0.0,
            min(
                float(volume),
                1.0
            )
        )

        try:

            pygame.mixer.music.set_volume(
                self.music_volume
            )

        except pygame.error:
            pass

    def set_sfx_volume(self, volume):
        """
        Set sound-effect volume from 0.0 to 1.0.
        """

        self.sfx_volume = max(
            0.0,
            min(
                float(volume),
                1.0
            )
        )

        for sound in self.sounds.values():

            sound.set_volume(
                self.sfx_volume
            )

    # ============================================================
    # MUTE / UNMUTE
    # ============================================================

    def mute_music(self):
        """
        Temporarily mute music without stopping it.
        """

        try:

            pygame.mixer.music.set_volume(
                0.0
            )

        except pygame.error:
            pass

    def unmute_music(self):
        """
        Restore the selected music volume.
        """

        try:

            pygame.mixer.music.set_volume(
                self.music_volume
            )

        except pygame.error:
            pass

    def mute_sfx(self):
        """
        Temporarily mute all sound effects.
        """

        for sound in self.sounds.values():

            sound.set_volume(
                0.0
            )

    def unmute_sfx(self):
        """
        Restore the selected sound-effect volume.
        """

        for sound in self.sounds.values():

            sound.set_volume(
                self.sfx_volume
            )

    # ============================================================
    # SHUTDOWN
    # ============================================================

    def shutdown(self):
        """
        Stop all audio when the game completely closes.
        """

        try:

            pygame.mixer.music.stop()

            for sound in self.sounds.values():
                sound.stop()

        except pygame.error:
            pass
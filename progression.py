"""
CYBERPUNK CAFÉ
PLAYER PROGRESSION SYSTEM

The game has exactly 3 playable levels:

    Level 1 -> Back Alley Kiosk
    Level 2 -> Neon Lounge
    Level 3 -> Cyber Penthouse

Level 3 is the absolute maximum.

XP rules:
    Level 1 -> Level 2 : 100 XP
    Level 2 -> Level 3 : 250 XP

Positive XP can cause a level-up.
Negative XP can reduce the player's current XP, but can never
reduce the player's level.

Credits are handled by ui_economy.py.
Order rewards are handled by rewards.py.
Order accuracy is handled by accuracy.py.
"""

from drink import get_unlocked_drinks


class Progression:
    """Stores and manages the player's level and XP."""

    # ------------------------------------------------------------
    # GAME LIMIT
    # ------------------------------------------------------------

    MAX_LEVEL = 3

    # XP required to move from the listed level to the next level.
    # Level 3 has no next level, but 450 is used as its XP display cap.
    XP_REQUIREMENTS = {
        1: 100,   # Level 1 -> Level 2
        2: 250,   # Level 2 -> Level 3
        3: 450,   # Level 3 is the final level
    }

    # ------------------------------------------------------------
    # LEVEL LOCATIONS
    # ------------------------------------------------------------

    LOCATION_UNLOCKS = {
        1: "Back Alley Kiosk",
        2: "Neon Lounge",
        3: "Cyber Penthouse",
    }

    # ------------------------------------------------------------
    # LEVEL FEATURES
    # ------------------------------------------------------------

    FEATURE_UNLOCKS = {
        1: [
            "Basic Café",
        ],
        2: [
            "New Drinks",
        ],
        3: [
            "New Drinks",
        ],
    }

    def __init__(self, level=1, xp=0):
        self.level = self._clamp_level(level)
        self.xp = self._clamp_xp_value(xp, self.level)

        # True only when add_xp() actually moves the player
        # from one level to another.
        self.level_up = False

        # Used by main.py to know which level was left.
        self.previous_level = self.level

    # ------------------------------------------------------------
    # VALUE VALIDATION
    # ------------------------------------------------------------

    @staticmethod
    def _safe_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _clamp_level(self, level):
        level = self._safe_int(level, 1)
        return max(1, min(level, self.MAX_LEVEL))

    def _clamp_xp_value(self, xp, level=None):
        if level is None:
            level = self.level

        xp = self._safe_int(xp, 0)
        xp = max(0, xp)

        maximum = self.XP_REQUIREMENTS.get(level)

        if maximum is not None:
            xp = min(xp, maximum)

        return xp

    def _clamp_xp(self):
        self.xp = self._clamp_xp_value(
            self.xp,
            self.level
        )

    # ------------------------------------------------------------
    # ADD / DEDUCT XP
    # ------------------------------------------------------------

    def add_xp(self, amount):
        """
        Add or deduct XP.

        Positive XP may cause a level-up.
        Negative XP reduces XP but NEVER de-levels the player.

        Returns:
            True  -> a level-up happened
            False -> no level-up happened
        """

        amount = self._safe_int(amount, 0)

        self.level_up = False

        # Mistake penalty.
        if amount < 0:
            self.xp += amount
            self._clamp_xp()
            return False

        # Nothing to add, or already at Level 3.
        if amount == 0 or self.is_max_level():
            return False

        self.xp += amount

        return self.check_level_up()

    # ------------------------------------------------------------
    # LEVEL-UP CHECK
    # ------------------------------------------------------------

    def check_level_up(self):
        """
        Check whether the current XP crosses a level threshold.

        Only these transitions are possible:

            1 -> 2
            2 -> 3

        Level 3 can NEVER become Level 4.
        """

        self.level_up = False

        while (
            self.level < self.MAX_LEVEL
            and self.level in self.XP_REQUIREMENTS
            and self.xp >= self.XP_REQUIREMENTS[self.level]
        ):

            self.previous_level = self.level

            required_xp = self.XP_REQUIREMENTS[self.level]

            self.xp -= required_xp
            self.level += 1

            self.level_up = True

        self._clamp_xp()

        return self.level_up

    # ------------------------------------------------------------
    # XP INFORMATION
    # ------------------------------------------------------------

    def get_xp_required(self):
        """Return XP required for the player's current level."""

        return self.XP_REQUIREMENTS.get(
            self.level
        )

    def get_xp_progress(self):
        """Return current-level XP progress from 0.0 to 1.0."""

        required_xp = self.get_xp_required()

        if required_xp is None or required_xp <= 0:
            return 1.0

        return max(
            0.0,
            min(
                self.xp / required_xp,
                1.0
            )
        )

    def get_xp_percentage(self):
        """Return current-level XP progress as a percentage."""

        return self.get_xp_progress() * 100

    # ------------------------------------------------------------
    # DRINK UNLOCKS
    # ------------------------------------------------------------

    def get_unlocked_drinks(self):
        """Return the drinks unlocked at the current level."""

        return get_unlocked_drinks(
            self.level
        )

    # ------------------------------------------------------------
    # LOCATION
    # ------------------------------------------------------------

    def get_current_location(self):
        """Return the location belonging to the current level."""

        return self.LOCATION_UNLOCKS.get(
            self.level,
            self.LOCATION_UNLOCKS[1]
        )

    # ------------------------------------------------------------
    # FEATURES
    # ------------------------------------------------------------

    def get_unlocked_features(self):
        """Return all features unlocked up to the current level."""

        unlocked_features = []

        for level in range(
            1,
            self.level + 1
        ):

            unlocked_features.extend(
                self.FEATURE_UNLOCKS.get(
                    level,
                    []
                )
            )

        return unlocked_features

    # ------------------------------------------------------------
    # LEVEL-UP STATUS
    # ------------------------------------------------------------

    def has_levelled_up(self):
        return self.level_up

    def get_previous_level(self):
        return self.previous_level

    def clear_level_up(self):
        self.level_up = False

    # ------------------------------------------------------------
    # LEVEL NAME
    # ------------------------------------------------------------

    def get_level_name(self):
        return f"LEVEL {self.level}"

    # ------------------------------------------------------------
    # MAX LEVEL
    # ------------------------------------------------------------

    def is_max_level(self):
        return self.level >= self.MAX_LEVEL

    # ------------------------------------------------------------
    # SAVE DATA
    # ------------------------------------------------------------

    def get_data(self):
        return {
            "level": self.level,
            "xp": self.xp
        }

    # ------------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------------

    def set_data(self, data):
        """
        Load level/XP from a save dictionary.

        Loading a save does NOT create a new level-up event.
        The level-up flag is therefore cleared after loading.
        """

        if not isinstance(data, dict):
            return

        loaded_level = self._safe_int(
            data.get(
                "level",
                1
            ),
            1
        )

        loaded_xp = self._safe_int(
            data.get(
                "xp",
                0
            ),
            0
        )

        self.level = self._clamp_level(
            loaded_level
        )

        self.xp = max(
            0,
            loaded_xp
        )

        # Normalize old save data into the current
        # 3-level progression system.
        self.level_up = False
        self.previous_level = self.level

        self.check_level_up()

        # Loading an existing save is NOT a new level-up event.
        self.level_up = False
        self.previous_level = self.level

        self._clamp_xp()

    # ------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------

    def reset(self):
        self.level = 1
        self.xp = 0
        self.level_up = False
        self.previous_level = 1
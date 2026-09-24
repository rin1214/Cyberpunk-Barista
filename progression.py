"""
============================================================
CYBERPUNK CAFÉ
PROGRESSION SYSTEM
============================================================

This file stores and manages the player's level and XP progression.
"""

from drink import get_unlocked_drinks


class Progression:
    """Stores and manages the player's level and XP."""

    MAX_LEVEL = 3

    # Scaled to match RewardSystem target requirements (10 segments total per level)
    XP_REQUIREMENTS = {
        1: 500,
        2: 1200,
        3: 2500,
    }

    LOCATION_UNLOCKS = {
        1: "Back Alley Kiosk",
        2: "Neon Lounge",
        3: "Cyber Penthouse",
    }

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

        self.level_up = False
        self.previous_level = self.level

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

        maximum = self.XP_REQUIREMENTS.get(level, 500)

        # Allow XP to reach the full target requirement for the current level
        if maximum is not None:
            xp = min(xp, maximum)

        return xp

    def _clamp_xp(self):
        self.xp = self._clamp_xp_value(
            self.xp,
            self.level
        )

    def add_xp(self, amount):
        """
        Add or deduct XP.
        Automatic level-ups are disabled; XP is tracked for score/leaderboard and level targets.
        """
        amount = self._safe_int(amount, 0)
        self.level_up = False

        # Add or deduct XP without triggering auto level-ups
        self.xp += amount
        self._clamp_xp()
        return False

    def check_level_up(self):
        """
        Disabled automatic level transitions based on XP.
        Levels are unlocked via map nodes using credits.
        """
        self.level_up = False
        self._clamp_xp()
        return False

    def get_xp_required(self):
        """Return XP required for the player's current level."""
        return self.XP_REQUIREMENTS.get(
            self.level,
            500
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

    def get_unlocked_drinks(self):
        """Return the drinks unlocked at the current level."""
        return get_unlocked_drinks(
            self.level
        )

    def get_current_location(self):
        """Return the location belonging to the current level."""
        return self.LOCATION_UNLOCKS.get(
            self.level,
            self.LOCATION_UNLOCKS[1]
        )

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

    def has_levelled_up(self):
        return self.level_up

    def get_previous_level(self):
        return self.previous_level

    def clear_level_up(self):
        self.level_up = False

    def get_level_name(self):
        return f"LEVEL {self.level}"

    def is_max_level(self):
        return self.level >= self.MAX_LEVEL

    def get_data(self):
        return {
            "level": self.level,
            "xp": self.xp
        }

    def set_data(self, data):
        """Load level/XP from a save dictionary without auto leveling up."""
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

        self.level_up = False
        self.previous_level = self.level
        self._clamp_xp()

    def reset(self):
        self.level = 1
        self.xp = 0
        self.level_up = False
        self.previous_level = 1
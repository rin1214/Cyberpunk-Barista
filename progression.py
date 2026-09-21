"""
CYBERPUNK CAFÉ
PLAYER PROGRESSION SYSTEM

FINAL GAME RULES
----------------
The game has exactly 3 playable levels:

    Level 1 -> Neon Alley
    Level 2 -> Cyber District
    Level 3 -> Neon Skyline

Level 3 is the absolute maximum.

XP progression is earned from PERFECT 4/4 drinks only.
An imperfect order can deduct XP, but it can never create
a level-up by itself.

Credits/money are handled by UIEconomy.
Order rewards are handled by rewards.py.
Order accuracy is handled by accuracy.py.
"""

from drink import get_unlocked_drinks


class Progression:

    # ============================================================
    # FINAL GAME LIMIT
    # ============================================================

    MAX_LEVEL = 3

    # ============================================================
    # INITIALISATION
    # ============================================================

    def __init__(
        self,
        level=1,
        xp=0,
    ):
        self.level = max(
            1,
            min(
                int(level),
                self.MAX_LEVEL,
            ),
        )

        self.xp = max(
            0,
            int(xp),
        )

        self.level_up = False
        self.previous_level = self.level

        # XP needed to advance FROM the level.
        #
        # Level 1 -> 2 = 100 XP
        # Level 2 -> 3 = 250 XP
        #
        # Level 3 has no next level, but 450 is retained as
        # the Level 3 progress cap so the HUD can show 450/MAX.

        self.xp_requirements = {
            1: 100,
            2: 250,
            3: 450,
        }

        # ========================================================
        # ONLY THREE LOCATIONS
        # ========================================================

        self.location_unlocks = {
            1: "Neon Alley",
            2: "Cyber District",
            3: "Neon Skyline",
        }

        # ========================================================
        # ONLY THREE LEVEL FEATURE SETS
        # ========================================================

        self.feature_unlocks = {
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

        # Keep Level 3 XP inside its visible maximum.
        self._clamp_xp()

    # ============================================================
    # INTERNAL XP CLAMP
    # ============================================================

    def _clamp_xp(self):
        """
        Keep XP valid for the current level.

        XP can never be negative.

        At Level 3, XP is capped at 450 because Level 3
        is the final level.
        """

        self.xp = max(
            0,
            int(self.xp),
        )

        required = self.xp_requirements.get(
            self.level
        )

        if required is not None:
            self.xp = min(
                self.xp,
                required,
            )

    # ============================================================
    # ADD / DEDUCT XP
    # ============================================================

    def add_xp(
        self,
        amount,
    ):
        """
        Add or deduct XP.

        Positive XP can cause a level-up.

        Negative XP is a mistake penalty. It reduces the
        current level's progress but NEVER de-levels the player.

        Returns True if a level-up occurred.
        """

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return False

        self.level_up = False

        # --------------------------------------------------------
        # XP DEDUCTION
        # --------------------------------------------------------

        if amount < 0:

            self.xp += amount
            self._clamp_xp()

            return False

        # --------------------------------------------------------
        # NO POSITIVE PROGRESSION BEYOND LEVEL 3
        # --------------------------------------------------------

        if amount == 0 or self.is_max_level():

            return False

        # --------------------------------------------------------
        # ADD POSITIVE XP
        # --------------------------------------------------------

        self.xp += amount

        return self.check_level_up()

    # ============================================================
    # LEVEL-UP CHECK
    # ============================================================

    def check_level_up(self):
        """
        Advance only through the two real level transitions:

            1 -> 2
            2 -> 3

        Level 3 can never become Level 4.
        """

        self.level_up = False

        while (
            self.level < self.MAX_LEVEL
            and self.level in self.xp_requirements
            and self.xp >= self.xp_requirements[self.level]
        ):

            self.previous_level = self.level

            required_xp = self.xp_requirements[
                self.level
            ]

            self.xp -= required_xp
            self.level += 1
            self.level_up = True

        self._clamp_xp()

        return self.level_up

    # ============================================================
    # XP REQUIRED
    # ============================================================

    def get_xp_required(self):

        return self.xp_requirements.get(
            self.level
        )

    # ============================================================
    # XP PROGRESS
    # ============================================================

    def get_xp_progress(self):

        required_xp = self.get_xp_required()

        if required_xp is None or required_xp <= 0:
            return 1.0

        return max(
            0.0,
            min(
                self.xp / required_xp,
                1.0,
            ),
        )

    # ============================================================
    # XP PERCENTAGE
    # ============================================================

    def get_xp_percentage(self):

        return (
            self.get_xp_progress()
            * 100
        )

    # ============================================================
    # UNLOCKED DRINKS
    # ============================================================

    def get_unlocked_drinks(self):

        return get_unlocked_drinks(
            self.level
        )

    # ============================================================
    # CURRENT LOCATION
    # ============================================================

    def get_current_location(self):

        return self.location_unlocks.get(
            self.level,
            "Neon Skyline",
        )

    # ============================================================
    # FEATURES
    # ============================================================

    def get_unlocked_features(self):

        unlocked_features = []

        for level in range(
            1,
            self.level + 1,
        ):

            unlocked_features.extend(
                self.feature_unlocks.get(
                    level,
                    [],
                )
            )

        return unlocked_features

    # ============================================================
    # LEVEL-UP STATUS
    # ============================================================

    def has_levelled_up(self):

        return self.level_up

    # ============================================================
    # PREVIOUS LEVEL
    # ============================================================

    def get_previous_level(self):

        return self.previous_level

    # ============================================================
    # LEVEL NAME
    # ============================================================

    def get_level_name(self):

        return f"LEVEL {self.level}"

    # ============================================================
    # MAX LEVEL
    # ============================================================

    def is_max_level(self):

        return self.level >= self.MAX_LEVEL

    # ============================================================
    # SAVE DATA
    # ============================================================

    def get_data(self):

        return {
            "level": self.level,
            "xp": self.xp,
        }

    # ============================================================
    # LOAD DATA
    # ============================================================

    def set_data(
        self,
        data,
    ):

        if not isinstance(
            data,
            dict,
        ):
            return

        try:
            loaded_level = int(
                data.get(
                    "level",
                    1,
                )
            )
        except (TypeError, ValueError):
            loaded_level = 1

        try:
            loaded_xp = int(
                data.get(
                    "xp",
                    0,
                )
            )
        except (TypeError, ValueError):
            loaded_xp = 0

        self.level = max(
            1,
            min(
                loaded_level,
                self.MAX_LEVEL,
            ),
        )

        self.xp = max(
            0,
            loaded_xp,
        )

        self.level_up = False
        self.previous_level = self.level

        # If an old save contains enough XP for a legitimate
        # Level 2/3 transition, preserve that progression.
        # Never allow the old Level 4-10 system to return.
        self.check_level_up()

        self.level_up = False

    # ============================================================
    # CLEAR LEVEL-UP FLAG
    # ============================================================

    def clear_level_up(self):

        self.level_up = False

    # ============================================================
    # RESET
    # ============================================================

    def reset(self):

        self.level = 1
        self.xp = 0
        self.level_up = False
        self.previous_level = 1

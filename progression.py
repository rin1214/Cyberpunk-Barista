"""
============================================================
CYBERPUNK CAFÉ
PLAYER PROGRESSION SYSTEM
============================================================

Controls:

    • Player level
    • Player XP
    • XP requirements
    • Level-ups
    • Drink unlock progression
    • Location progression
    • Feature progression

The game has EXACTLY 3 levels.

LEVEL 1
    Back Alley Kiosk

LEVEL 2
    Neon Lounge

LEVEL 3
    Cyber Penthouse
============================================================
"""

from drink import get_unlocked_drinks


class Progression:

    # ========================================================
    # GAME LIMIT
    # ========================================================

    MAX_LEVEL = 3

    # ========================================================
    # INITIALISATION
    # ========================================================

    def __init__(
        self,
        level=1,
        xp=0,
    ):

        # ----------------------------------------------------
        # LEVEL
        # ----------------------------------------------------

        try:
            level = int(level)
        except (TypeError, ValueError):
            level = 1

        self.level = max(
            1,
            min(
                level,
                self.MAX_LEVEL,
            ),
        )

        # ----------------------------------------------------
        # XP
        # ----------------------------------------------------

        try:
            xp = int(xp)
        except (TypeError, ValueError):
            xp = 0

        self.xp = max(
            0,
            xp,
        )

        # ----------------------------------------------------
        # LEVEL-UP STATUS
        # ----------------------------------------------------

        self.level_up = False

        self.previous_level = self.level

        # ====================================================
        # XP REQUIREMENTS
        # ====================================================

        self.xp_requirements = {

            # Level 1 → Level 2
            1: 100,

            # Level 2 → Level 3
            2: 250,
        }

        # ====================================================
        # OFFICIAL LOCATIONS
        # ====================================================

        self.location_unlocks = {

            1: "Back Alley Kiosk",

            2: "Neon Lounge",

            3: "Cyber Penthouse",
        }

        # ====================================================
        # FEATURES
        # ====================================================

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

    # ========================================================
    # ADD XP
    # ========================================================

    def add_xp(
        self,
        amount,
    ):
        """
        Add or remove XP.

        Positive XP:
            Adds XP and checks for level-up.

        Negative XP:
            Removes XP but NEVER de-levels the player.

        Level 3 is the maximum level.
        """

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            amount = 0

        self.level_up = False

        # ----------------------------------------------------
        # NEGATIVE XP
        # ----------------------------------------------------

        if amount < 0:

            self.xp += amount

            self.xp = max(
                0,
                self.xp,
            )

            return False

        # ----------------------------------------------------
        # NO XP
        # ----------------------------------------------------

        if amount == 0:

            return False

        # ----------------------------------------------------
        # LEVEL 3 IS MAXIMUM
        # ----------------------------------------------------

        if self.level >= self.MAX_LEVEL:

            return False

        # ----------------------------------------------------
        # ADD XP
        # ----------------------------------------------------

        self.xp += amount

        # ----------------------------------------------------
        # CHECK LEVEL-UP
        # ----------------------------------------------------

        return self.check_level_up()

    # ========================================================
    # LEVEL-UP CHECK
    # ========================================================

    def check_level_up(self):
        """
        Check whether enough XP has been earned
        to reach the next level.

        Any extra XP carries over.
        """

        self.level_up = False

        while (
            self.level < self.MAX_LEVEL
            and self.level in self.xp_requirements
            and self.xp >= self.xp_requirements[self.level]
        ):

            # ------------------------------------------------
            # SAVE OLD LEVEL
            # ------------------------------------------------

            self.previous_level = self.level

            # ------------------------------------------------
            # REQUIRED XP
            # ------------------------------------------------

            required_xp = self.xp_requirements[
                self.level
            ]

            # ------------------------------------------------
            # REMOVE XP USED FOR LEVEL-UP
            # ------------------------------------------------

            self.xp -= required_xp

            # ------------------------------------------------
            # ADVANCE LEVEL
            # ------------------------------------------------

            self.level += 1

            # ------------------------------------------------
            # MARK LEVEL-UP
            # ------------------------------------------------

            self.level_up = True

        return self.level_up

    # ========================================================
    # GET XP REQUIRED
    # ========================================================

    def get_xp_required(self):
        """
        Return XP required for the next level.

        Level 1:
            100

        Level 2:
            250

        Level 3:
            None
        """

        if self.level >= self.MAX_LEVEL:

            return None

        return self.xp_requirements.get(
            self.level
        )

    # ========================================================
    # GET XP PROGRESS
    # ========================================================

    def get_xp_progress(self):
        """
        Return XP progress between 0.0 and 1.0.
        """

        required_xp = self.get_xp_required()

        if required_xp is None:

            return 1.0

        if required_xp <= 0:

            return 1.0

        progress = (
            self.xp / required_xp
        )

        return max(
            0.0,
            min(
                progress,
                1.0,
            ),
        )

    # ========================================================
    # GET XP PERCENTAGE
    # ========================================================

    def get_xp_percentage(self):
        """
        Return XP progress as a percentage.
        """

        return (
            self.get_xp_progress()
            * 100
        )

    # ========================================================
    # GET UNLOCKED DRINKS
    # ========================================================

    def get_unlocked_drinks(self):
        """
        Return drinks unlocked at the current level.

        drink.py remains responsible for the actual
        drink unlock definitions.
        """

        return get_unlocked_drinks(
            self.level
        )

    # ========================================================
    # GET CURRENT LOCATION
    # ========================================================

    def get_current_location(self):
        """
        Return the official location for the current level.
        """

        return self.location_unlocks.get(
            self.level,
            "Back Alley Kiosk",
        )

    # ========================================================
    # GET UNLOCKED LOCATIONS
    # ========================================================

    def get_unlocked_locations(self):
        """
        Return all locations unlocked up to the
        current level.
        """

        locations = []

        for level in range(
            1,
            self.level + 1,
        ):

            location = self.location_unlocks.get(
                level
            )

            if location is not None:

                locations.append(
                    location
                )

        return locations

    # ========================================================
    # CHECK LOCATION UNLOCK
    # ========================================================

    def is_location_unlocked(
        self,
        level,
    ):
        """
        Return True if the requested level
        is currently unlocked.
        """

        try:
            level = int(level)
        except (TypeError, ValueError):
            return False

        return (
            1
            <= level
            <= self.level
            <= self.MAX_LEVEL
        )

    # ========================================================
    # GET UNLOCKED FEATURES
    # ========================================================

    def get_unlocked_features(self):
        """
        Return all features unlocked up to
        the current level.
        """

        unlocked_features = []

        for level in range(
            1,
            self.level + 1,
        ):

            features = self.feature_unlocks.get(
                level,
                [],
            )

            unlocked_features.extend(
                features
            )

        return unlocked_features

    # ========================================================
    # HAS LEVELLED UP
    # ========================================================

    def has_levelled_up(self):
        """
        Return True if the most recent XP addition
        caused a level-up.
        """

        return self.level_up

    # ========================================================
    # GET PREVIOUS LEVEL
    # ========================================================

    def get_previous_level(self):
        """
        Return the level before the most recent
        level-up.
        """

        return self.previous_level

    # ========================================================
    # SET LEVEL
    # ========================================================

    def set_level(
        self,
        level,
    ):
        """
        Manually synchronise the level.

        The level is always restricted to 1–3.
        """

        try:
            level = int(level)
        except (TypeError, ValueError):
            level = 1

        self.level = max(
            1,
            min(
                level,
                self.MAX_LEVEL,
            ),
        )

        self.level_up = False

        self.previous_level = self.level

        self.xp = max(
            0,
            int(self.xp),
        )

    # ========================================================
    # SET XP
    # ========================================================

    def set_xp(
        self,
        xp,
    ):
        """
        Directly set XP.

        XP can never be negative.
        """

        try:
            xp = int(xp)
        except (TypeError, ValueError):
            xp = 0

        self.xp = max(
            0,
            xp,
        )

    # ========================================================
    # RESET PROGRESSION
    # ========================================================

    def reset(self):
        """
        Completely reset progression.

        Result:

            Level = 1
            XP = 0

        Location becomes:

            Back Alley Kiosk

        Credits are NOT handled here.
        UIEconomy handles credits.
        """

        self.level = 1

        self.xp = 0

        self.level_up = False

        self.previous_level = 1

    # ========================================================
    # GET PROGRESSION DATA
    # ========================================================

    def get_progression_data(self):
        """
        Return progression information as a dictionary.
        """

        return {

            "level":
                self.level,

            "xp":
                self.xp,

            "xp_required":
                self.get_xp_required(),

            "xp_percentage":
                self.get_xp_percentage(),

            "location":
                self.get_current_location(),

            "unlocked_drinks":
                self.get_unlocked_drinks(),

            "unlocked_features":
                self.get_unlocked_features(),
        }

    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    def print_progression(self):
        """
        Print progression information to the terminal.
        """

        print(
            "========================================"
        )

        print(
            "CYBERPUNK CAFÉ PROGRESSION"
        )

        print(
            "========================================"
        )

        print(
            f"Level: {self.level}"
        )

        print(
            f"XP: {self.xp}"
        )

        print(
            f"Location: "
            f"{self.get_current_location()}"
        )

        print(
            "Unlocked Drinks:"
        )

        for drink in self.get_unlocked_drinks():

            print(
                f"  - {drink}"
            )

        print(
            "========================================"
        )
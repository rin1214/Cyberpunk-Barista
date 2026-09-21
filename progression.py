"""
============================================================
CYBERPUNK CAFÉ
PLAYER PROGRESSION SYSTEM
============================================================

This system controls:

    • Current level
    • Current XP
    • XP required for the next level
    • Level-up detection
    • Drink unlocks
    • Location unlocks
    • Feature unlocks

IMPORTANT:

Credits / money are handled separately by UIEconomy.

Order rewards are handled by rewards.py.

Order accuracy is handled by accuracy.py.

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
        #
        # The game can never be below Level 1
        # or above Level 3.
        #

        self.level = max(
            1,
            min(
                int(level),
                self.MAX_LEVEL,
            ),
        )

        # ----------------------------------------------------
        # XP
        # ----------------------------------------------------
        #
        # XP can never be negative.
        #

        self.xp = max(
            0,
            int(xp),
        )

        # ----------------------------------------------------
        # LEVEL-UP STATUS
        # ----------------------------------------------------

        self.level_up = False

        self.previous_level = self.level

        # ====================================================
        # XP REQUIREMENTS
        # ====================================================
        #
        # These values mean:
        #
        # Level 1 → Level 2 requires 100 XP
        #
        # Level 2 → Level 3 requires 250 XP
        #
        # Level 3 is the maximum level.
        #
        # There is NO Level 4.
        #

        self.xp_requirements = {

            1: 100,

            2: 250,

        }

        # ====================================================
        # LOCATIONS
        # ====================================================
        #
        # These are the OFFICIAL Cyberpunk Café
        # location names.
        #
        # Do not change these unless the game design
        # changes again.
        #

        self.location_unlocks = {

            1: "Back Alley Kiosk",

            2: "Neon Lounge",

            3: "Cyber Penthouse",

        }

        # ====================================================
        # FEATURES
        # ====================================================
        #
        # Features unlocked at each level.
        #

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
        Add XP to the player.

        Positive XP:
            Adds XP and checks for level-up.

        Negative XP:
            Removes XP but NEVER lowers the player's level.

        Zero:
            Does nothing.

        Returns:

            True
                if the player levelled up.

            False
                if the player did not level up.
        """

        # ----------------------------------------------------
        # Convert the value safely to an integer.
        # ----------------------------------------------------

        try:

            amount = int(
                amount
            )

        except (
            TypeError,
            ValueError,
        ):

            amount = 0

        # ----------------------------------------------------
        # RESET LEVEL-UP STATUS
        # ----------------------------------------------------

        self.level_up = False

        # ====================================================
        # NEGATIVE XP
        # ====================================================
        #
        # Mistakes can remove XP.
        #
        # However:
        #
        # Level 3 must NEVER become Level 2.
        #
        # Level 2 must NEVER become Level 1.
        #
        # Therefore negative XP only reduces the current
        # XP amount.
        #

        if amount < 0:

            self.xp += amount

            self.xp = max(
                0,
                self.xp,
            )

            return False

        # ====================================================
        # ZERO XP
        # ====================================================

        if amount == 0:

            return False

        # ====================================================
        # MAX LEVEL
        # ====================================================
        #
        # Once the player reaches Level 3, there is no
        # Level 4.
        #
        # Additional XP is therefore not used for another
        # level-up.
        #

        if self.level >= self.MAX_LEVEL:

            return False

        # ====================================================
        # ADD XP
        # ====================================================

        self.xp += amount

        # ====================================================
        # CHECK LEVEL-UP
        # ====================================================

        return self.check_level_up()

    # ========================================================
    # LEVEL-UP CHECK
    # ========================================================

    def check_level_up(self):
        """
        Check whether the player has enough XP to advance.

        XP carries over after a level-up.

        Example:

            Level 1
            90 XP

            Player earns 30 XP.

            90 + 30 = 120 XP

            Required = 100 XP

            Player becomes Level 2.

            Remaining XP = 20
        """

        # ----------------------------------------------------
        # Reset level-up flag.
        # ----------------------------------------------------

        self.level_up = False

        # ----------------------------------------------------
        # Keep checking while a level-up is possible.
        #
        # Because the maximum level is 3, this can only
        # move:
        #
        # Level 1 → Level 2
        #
        # or
        #
        # Level 2 → Level 3
        # ----------------------------------------------------

        while (

            self.level < self.MAX_LEVEL

            and

            self.level in self.xp_requirements

            and

            self.xp >= self.xp_requirements[
                self.level
            ]

        ):

            # ------------------------------------------------
            # Remember the previous level.
            # ------------------------------------------------

            self.previous_level = (
                self.level
            )

            # ------------------------------------------------
            # Get XP needed for this level-up.
            # ------------------------------------------------

            required_xp = (
                self.xp_requirements[
                    self.level
                ]
            )

            # ------------------------------------------------
            # Remove the XP used for the level-up.
            #
            # Any remaining XP carries forward.
            # ------------------------------------------------

            self.xp -= required_xp

            # ------------------------------------------------
            # Increase the level.
            # ------------------------------------------------

            self.level += 1

            # ------------------------------------------------
            # Tell the game a level-up happened.
            # ------------------------------------------------

            self.level_up = True

        return self.level_up

    # ========================================================
    # XP REQUIRED
    # ========================================================

    def get_xp_required(self):
        """
        Return the amount of XP required to reach the
        next level.

        Returns:

            100
                while at Level 1.

            250
                while at Level 2.

            None
                at Level 3 because Level 3 is the maximum.
        """

        if self.level >= self.MAX_LEVEL:

            return None

        return self.xp_requirements.get(
            self.level
        )

    # ========================================================
    # XP PROGRESS
    # ========================================================

    def get_xp_progress(self):
        """
        Return XP progress as a decimal between 0.0 and 1.0.

        Example:

            50 / 100 XP

        returns:

            0.5
        """

        required_xp = (
            self.get_xp_required()
        )

        # ----------------------------------------------------
        # Level 3 is complete.
        # ----------------------------------------------------

        if required_xp is None:

            return 1.0

        # ----------------------------------------------------
        # Safety check.
        # ----------------------------------------------------

        if required_xp <= 0:

            return 1.0

        # ----------------------------------------------------
        # Calculate progress.
        # ----------------------------------------------------

        progress = (
            self.xp
            / required_xp
        )

        # ----------------------------------------------------
        # Keep result between 0 and 1.
        # ----------------------------------------------------

        return max(
            0.0,
            min(
                progress,
                1.0,
            ),
        )

    # ========================================================
    # XP PERCENTAGE
    # ========================================================

    def get_xp_percentage(self):
        """
        Return XP progress as a percentage.

        Example:

            50 / 100 XP

        returns:

            50.0
        """

        return (
            self.get_xp_progress()
            * 100
        )

    # ========================================================
    # UNLOCKED DRINKS
    # ========================================================

    def get_unlocked_drinks(self):
        """
        Return the drinks unlocked for the current level.

        The drink unlock rules themselves are stored in
        drink.py.

        Progression simply asks drink.py which drinks are
        available for the current level.
        """

        return get_unlocked_drinks(
            self.level
        )

    # ========================================================
    # CURRENT LOCATION
    # ========================================================

    def get_current_location(self):
        """
        Return the official location name for the
        current level.
        """

        return self.location_unlocks.get(
            self.level,
            "Back Alley Kiosk",
        )

    # ========================================================
    # UNLOCKED LOCATIONS
    # ========================================================

    def get_unlocked_locations(self):
        """
        Return all locations unlocked up to the current level.

        Example:

            Level 1:
                ["Back Alley Kiosk"]

            Level 2:
                [
                    "Back Alley Kiosk",
                    "Neon Lounge"
                ]

            Level 3:
                [
                    "Back Alley Kiosk",
                    "Neon Lounge",
                    "Cyber Penthouse"
                ]
        """

        locations = []

        for level in range(
            1,
            self.level + 1,
        ):

            location = (
                self.location_unlocks.get(
                    level
                )
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
        Return True if the requested level/location
        has been unlocked.
        """

        try:

            level = int(
                level
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

        return (
            1
            <= level
            <= self.level
            <= self.MAX_LEVEL
        )

    # ========================================================
    # UNLOCKED FEATURES
    # ========================================================

    def get_unlocked_features(self):
        """
        Return all features unlocked up to the current level.
        """

        unlocked_features = []

        for level in range(
            1,
            self.level + 1,
        ):

            features = (
                self.feature_unlocks.get(
                    level,
                    [],
                )
            )

            unlocked_features.extend(
                features
            )

        return unlocked_features

    # ========================================================
    # LEVEL-UP STATUS
    # ========================================================

    def has_levelled_up(self):
        """
        Return True if a level-up occurred during the
        most recent XP addition.
        """

        return self.level_up

    # ========================================================
    # PREVIOUS LEVEL
    # ========================================================

    def get_previous_level(self):
        """
        Return the level the player was at before the
        most recent level-up.
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
        Manually set the current level.

        This is mainly useful for synchronising the
        progression system with saved game data.

        The level is always clamped between 1 and 3.
        """

        try:

            level = int(
                level
            )

        except (
            TypeError,
            ValueError,
        ):

            level = 1

        self.level = max(
            1,
            min(
                level,
                self.MAX_LEVEL,
            ),
        )

        self.level_up = False

        self.previous_level = (
            self.level
        )

        # ----------------------------------------------------
        # Make sure XP never becomes negative.
        # ----------------------------------------------------

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
        Manually set XP.

        XP can never become negative.
        """

        try:

            xp = int(
                xp
            )

        except (
            TypeError,
            ValueError,
        ):

            xp = 0

        self.xp = max(
            0,
            xp,
        )

    # ========================================================
    # GET CURRENT PROGRESSION DATA
    # ========================================================

    def get_progression_data(self):
        """
        Return the important progression information
        as a dictionary.

        Useful for saving, debugging, or displaying
        progression information.
        """

        return {

            "level": self.level,

            "xp": self.xp,

            "xp_required": (
                self.get_xp_required()
            ),

            "xp_percentage": (
                self.get_xp_percentage()
            ),

            "location": (
                self.get_current_location()
            ),

            "unlocked_drinks": (
                self.get_unlocked_drinks()
            ),

            "unlocked_features": (
                self.get_unlocked_features()
            ),

        }

    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    def print_progression(self):
        """
        Print the current progression information
        to the VS Code terminal.

        This is useful while testing.
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
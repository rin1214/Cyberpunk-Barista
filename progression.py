"""
============================================================
CYBERPUNK CAFÉ
PLAYER PROGRESSION SYSTEM
============================================================

FINAL GAME PROGRESSION
------------------------------------------------------------

There are ONLY 3 levels.

LEVEL 1
    Back Alley Kiosk

LEVEL 2
    Neon Lounge

LEVEL 3
    Cyber Penthouse

There is NO Level 4.

------------------------------------------------------------
XP REQUIREMENTS
------------------------------------------------------------

Level 1 -> Level 2
    100 XP

Level 2 -> Level 3
    250 XP

Level 3
    Maximum level

------------------------------------------------------------
RESPONSIBILITIES
------------------------------------------------------------

This file controls:

    • Player level
    • Player XP
    • Level-up detection
    • Level-up status
    • Drink unlock progression
    • Location progression
    • Feature unlocks

This file does NOT control:

    • Credits
    • Money
    • Saving player profiles
    • Order accuracy
    • Customer behaviour
    • Reward calculation

Those systems are handled by:

    ui_economy.py
    accuracy.py
    customer.py
    rewards.py

============================================================
"""

from drink import get_unlocked_drinks


class Progression:

    # ========================================================
    # FINAL GAME LEVEL LIMIT
    # ========================================================

    MAX_LEVEL = 3

    # ========================================================
    # XP REQUIREMENTS
    #
    # The number represents the XP needed to advance
    # FROM that level.
    #
    # Level 1 -> Level 2 = 100 XP
    # Level 2 -> Level 3 = 250 XP
    #
    # There is intentionally no Level 3 -> Level 4.
    # ========================================================

    XP_REQUIREMENTS = {

        1: 100,

        2: 250,

    }

    # ========================================================
    # FINAL LOCATION NAMES
    # ========================================================

    LOCATION_UNLOCKS = {

        1: "Back Alley Kiosk",

        2: "Neon Lounge",

        3: "Cyber Penthouse",

    }

    # ========================================================
    # FINAL FEATURE UNLOCKS
    # ========================================================

    FEATURE_UNLOCKS = {

        # ----------------------------------------------------
        # LEVEL 1
        # ----------------------------------------------------

        1: [

            "Basic Café",

            "Neon Latte",

            "Milkyway",

            "Void Chai",

        ],

        # ----------------------------------------------------
        # LEVEL 2
        # ----------------------------------------------------

        2: [

            "Cyber Fuel",

            "Hologram Frappe",

            "Pixel Lemint",

        ],

        # ----------------------------------------------------
        # LEVEL 3
        # ----------------------------------------------------

        3: [

            "Caramel Byte",

            "Stardust Matcha",

            "Meteorite",

        ],

    }

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        level=1,
        xp=0,
    ):

        # ====================================================
        # SAFE LEVEL
        # ====================================================

        try:

            level = int(level)

        except (
            TypeError,
            ValueError,
        ):

            level = 1

        # ----------------------------------------------------
        # Never allow a level below 1.
        # Never allow a level above 3.
        # ----------------------------------------------------

        self.level = max(
            1,
            min(
                level,
                self.MAX_LEVEL,
            ),
        )

        # ====================================================
        # SAFE XP
        # ====================================================

        try:

            xp = int(xp)

        except (
            TypeError,
            ValueError,
        ):

            xp = 0

        # ----------------------------------------------------
        # XP can never be negative.
        # ----------------------------------------------------

        self.xp = max(
            0,
            xp,
        )

        # ====================================================
        # LEVEL-UP STATUS
        # ====================================================

        self.level_up = False

        self.previous_level = self.level

        # ====================================================
        # COMPATIBILITY ATTRIBUTES
        #
        # Some existing files use these instance attributes
        # instead of the class constants.
        #
        # Keeping them prevents compatibility problems.
        # ====================================================

        self.xp_requirements = dict(
            self.XP_REQUIREMENTS
        )

        self.location_unlocks = dict(
            self.LOCATION_UNLOCKS
        )

        self.feature_unlocks = {

            level: list(features)

            for level, features
            in self.FEATURE_UNLOCKS.items()

        }

    # ========================================================
    # CLAMP XP
    # ========================================================

    def _clamp_xp(self):

        """
        Prevent XP from ever becoming negative.
        """

        if self.xp < 0:

            self.xp = 0

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
            Can cause a level-up.

        Negative XP:
            Deducts XP.

        IMPORTANT:

        A mistake can reduce XP to 0, but it can NEVER
        reduce the player's current level.

        Returns:

            True
                if the player levelled up.

            False
                otherwise.
        """

        # ----------------------------------------------------
        # Convert amount safely.
        # ----------------------------------------------------

        try:

            amount = int(amount)

        except (
            TypeError,
            ValueError,
        ):

            return False

        # ----------------------------------------------------
        # Reset level-up flag before this XP transaction.
        # ----------------------------------------------------

        self.level_up = False

        # ====================================================
        # NEGATIVE XP
        # ====================================================

        if amount < 0:

            self.xp += amount

            self._clamp_xp()

            return False

        # ====================================================
        # ZERO XP
        # ====================================================

        if amount == 0:

            return False

        # ====================================================
        # LEVEL 3 IS THE MAXIMUM
        # ====================================================

        if self.level >= self.MAX_LEVEL:

            self.level = self.MAX_LEVEL

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
    # CHECK LEVEL-UP
    # ========================================================

    def check_level_up(self):
        """
        Checks whether enough XP has been collected
        to advance to the next level.

        XP remaining after the level-up is carried forward.

        Example:

            Level 1
            XP = 80

            Gain 40 XP

            Total XP = 120

            100 XP is used for Level 2.

            New result:

                Level = 2
                XP = 20
        """

        # ----------------------------------------------------
        # Reset this transaction's level-up flag.
        # ----------------------------------------------------

        self.level_up = False

        # ====================================================
        # ALREADY AT MAXIMUM
        # ====================================================

        if self.level >= self.MAX_LEVEL:

            self.level = self.MAX_LEVEL

            return False

        # ====================================================
        # CHECK FOR ONE OR MORE LEVEL-UPS
        # ====================================================

        while self.level < self.MAX_LEVEL:

            # ------------------------------------------------
            # Find XP requirement for current level.
            # ------------------------------------------------

            required_xp = (
                self.xp_requirements.get(
                    self.level
                )
            )

            # ------------------------------------------------
            # Safety check.
            # ------------------------------------------------

            if required_xp is None:

                break

            # ------------------------------------------------
            # Not enough XP yet.
            # ------------------------------------------------

            if self.xp < required_xp:

                break

            # ------------------------------------------------
            # Remember old level.
            # ------------------------------------------------

            self.previous_level = self.level

            # ------------------------------------------------
            # Consume required XP.
            # ------------------------------------------------

            self.xp -= required_xp

            self._clamp_xp()

            # ------------------------------------------------
            # Advance level.
            # ------------------------------------------------

            self.level += 1

            # ------------------------------------------------
            # Record that a level-up occurred.
            # ------------------------------------------------

            self.level_up = True

            print(
                "[PROGRESSION] "
                f"Level {self.previous_level} "
                f"-> {self.level}"
            )

            # ------------------------------------------------
            # Level 3 is the maximum.
            # ------------------------------------------------

            if self.level >= self.MAX_LEVEL:

                self.level = self.MAX_LEVEL

                break

        return self.level_up

    # ========================================================
    # GET CURRENT LOCATION
    # ========================================================

    def get_current_location(self):
        """
        Compatibility method.

        Existing main.py and ui_economy.py use:

            progression.get_current_location()

        This method returns the correct location for the
        player's current level.
        """

        return self.location_unlocks.get(
            self.level,
            self.location_unlocks[1],
        )

    # ========================================================
    # GET LOCATION
    # ========================================================

    def get_location(self):
        """
        Modern/short version of get_current_location().
        """

        return self.get_current_location()

    # ========================================================
    # GET XP REQUIRED FOR NEXT LEVEL
    # ========================================================

    def get_xp_required(self):
        """
        Returns the XP needed to reach the next level.

        Level 1:
            returns 100

        Level 2:
            returns 250

        Level 3:
            returns None because Level 3 is maximum.
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
        Returns information useful for the HUD.

        Example:

        {
            "current": 40,
            "required": 100,
            "percentage": 40.0,
            "max_level": False
        }
        """

        required = self.get_xp_required()

        # ----------------------------------------------------
        # LEVEL 3
        # ----------------------------------------------------

        if required is None:

            return {

                "current": self.xp,

                "required": None,

                "percentage": 100.0,

                "max_level": True,

            }

        # ----------------------------------------------------
        # Calculate percentage.
        # ----------------------------------------------------

        percentage = (
            self.xp
            / float(required)
        ) * 100.0

        # ----------------------------------------------------
        # Keep percentage between 0 and 100.
        # ----------------------------------------------------

        percentage = max(
            0.0,
            min(
                percentage,
                100.0,
            ),
        )

        return {

            "current": self.xp,

            "required": required,

            "percentage": percentage,

            "max_level": False,

        }

    # ========================================================
    # GET UNLOCKED DRINKS
    # ========================================================

    def get_unlocked_drinks(self):
        """
        Returns the drinks unlocked at the player's
        current level.

        Drink unlocking remains controlled by drink.py.
        """

        try:

            return get_unlocked_drinks(
                self.level
            )

        except Exception as error:

            print(
                "[PROGRESSION] "
                f"Could not get unlocked drinks: {error}"
            )

            return []

    # ========================================================
    # CHECK WHETHER A DRINK IS UNLOCKED
    # ========================================================

    def is_drink_unlocked(
        self,
        drink_name,
    ):
        """
        Returns True if the specified drink is unlocked
        at the current player level.
        """

        try:

            return drink_name in (
                self.get_unlocked_drinks()
            )

        except Exception:

            return False

    # ========================================================
    # GET FEATURE UNLOCKS
    # ========================================================

    def get_feature_unlocks(
        self,
        level=None,
    ):
        """
        Returns features associated with a level.

        If no level is supplied, the current player level
        is used.
        """

        if level is None:

            level = self.level

        try:

            level = int(level)

        except (
            TypeError,
            ValueError,
        ):

            level = self.level

        return list(
            self.feature_unlocks.get(
                level,
                [],
            )
        )

    # ========================================================
    # GET LEVEL INFORMATION
    # ========================================================

    def get_level_info(self):
        """
        Returns a complete dictionary describing the
        current progression state.

        Useful for:

            • HUD
            • Loading screen
            • Map
            • Debugging
            • Future UI
        """

        return {

            "level":
                self.level,

            "xp":
                self.xp,

            "location":
                self.get_current_location(),

            "xp_required":
                self.get_xp_required(),

            "max_level":
                self.level >= self.MAX_LEVEL,

            "unlocked_drinks":
                self.get_unlocked_drinks(),

            "features":
                self.get_feature_unlocks(),

            "level_up":
                self.level_up,

            "previous_level":
                self.previous_level,

        }

    # ========================================================
    # GET LEVEL
    # ========================================================

    def get_level(self):

        return self.level

    # ========================================================
    # GET XP
    # ========================================================

    def get_xp(self):

        return self.xp

    # ========================================================
    # GET CURRENT LEVEL
    # ========================================================

    def get_current_level(self):

        return self.level

    # ========================================================
    # IS MAX LEVEL
    # ========================================================

    def is_max_level(self):

        return self.level >= self.MAX_LEVEL

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        """
        Completely reset progression.

        Result:

            Level = 1
            XP = 0
            Location = Back Alley Kiosk
        """

        self.level = 1

        self.xp = 0

        self.level_up = False

        self.previous_level = 1

        print(
            "[PROGRESSION] "
            "Progression reset to Level 1."
        )

    # ========================================================
    # SET LEVEL
    # ========================================================

    def set_level(
        self,
        level,
    ):
        """
        Safely set the current level.

        This is mainly a compatibility/debug helper.

        Normal gameplay should advance levels through XP.
        """

        try:

            level = int(level)

        except (
            TypeError,
            ValueError,
        ):

            return False

        self.level = max(
            1,
            min(
                level,
                self.MAX_LEVEL,
            ),
        )

        # ----------------------------------------------------
        # Do not pretend this was a natural level-up.
        # ----------------------------------------------------

        self.level_up = False

        self.previous_level = self.level

        # ----------------------------------------------------
        # XP must remain valid.
        # ----------------------------------------------------

        self._clamp_xp()

        return True

    # ========================================================
    # SET XP
    # ========================================================

    def set_xp(
        self,
        xp,
    ):
        """
        Directly set XP.

        This does not automatically change the level.

        Normal gameplay should use add_xp().
        """

        try:

            xp = int(xp)

        except (
            TypeError,
            ValueError,
        ):

            return False

        self.xp = max(
            0,
            xp,
        )

        return True

    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    def debug_print(self):
        """
        Prints the current progression state to the
        VS Code terminal.
        """

        print(
            "========================================"
        )

        print(
            "[PROGRESSION DEBUG]"
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

        required = self.get_xp_required()

        if required is None:

            print(
                "Next Level: MAXIMUM"
            )

        else:

            print(
                f"XP Required: {required}"
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
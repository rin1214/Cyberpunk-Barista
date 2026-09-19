"""
CYBERPUNK CAFÉ
PLAYER PROGRESSION SYSTEM

This system controls:

    • Current level
    • Current XP
    • XP required for the next level
    • Level-up detection
    • Drink unlocks
    • Location unlocks
    • Feature unlocks

IMPORTANT:

Credits/money are handled separately by UIEconomy.

Order rewards are handled by rewards.py.

Order accuracy is handled by accuracy.py.
"""

from drink import get_unlocked_drinks


class Progression:

    # ============================================================
    # INITIALISATION
    # ============================================================

    def __init__(
        self,
        level=1,
        xp=0,
    ):

        # --------------------------------------------------------
        # BASIC PROGRESSION
        # --------------------------------------------------------

        self.level = max(
            1,
            int(level),
        )

        self.xp = max(
            0,
            int(xp),
        )

        # --------------------------------------------------------
        # LEVEL-UP STATUS
        # --------------------------------------------------------

        self.level_up = False

        self.previous_level = (
            self.level
        )

        # --------------------------------------------------------
        # XP REQUIREMENTS
        #
        # XP needed to advance FROM that level.
        #
        # Level 1 → 100 XP
        # Level 2 → 250 XP
        # Level 3 → 450 XP
        # etc.
        # --------------------------------------------------------

        self.xp_requirements = {

            1: 100,

            2: 250,

            3: 450,

            4: 700,

            5: 1000,

            6: 1350,

            7: 1750,

            8: 2200,

            9: 2700,

            10: 3300,
        }

        # --------------------------------------------------------
        # LOCATIONS
        # --------------------------------------------------------

        self.location_unlocks = {

            1: "Neon Alley",

            2: "Cyber District",

            3: "Neon Skyline",

            4: "Penthouse Café",

            5: "Cyber Plaza",

            6: "Digital Garden",

            7: "Neon Market",

            8: "Skyline Lounge",

            9: "Cyber City",

            10: "Grand Cyber Café",
        }

        # --------------------------------------------------------
        # FEATURES
        # --------------------------------------------------------

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

            4: [
                "New Location",
            ],

            5: [
                "Special Customers",
            ],

            6: [
                "Advanced Café",
            ],

            7: [
                "Rush Hour",
            ],

            8: [
                "Rare Drinks",
            ],

            9: [
                "VIP Customers",
            ],

            10: [
                "Grand Café",
            ],
        }

    # ============================================================
    # ADD XP
    # ============================================================

    def add_xp(
        self,
        amount,
    ):
        """
        Add XP to the player.

        Returns True if at least one level-up occurred.
        """

        amount = int(amount)

        if amount <= 0:

            return False

        self.xp += amount

        return self.check_level_up()

    # ============================================================
    # LEVEL-UP CHECK
    # ============================================================

    def check_level_up(self):
        """
        Checks whether the player has enough XP
        to advance.

        Any remaining XP carries into the new level.

        Example:

            Level 1
            90 / 100 XP

            Earn 45 XP

            Total = 135 XP

            Level up!

            New level:
            2

            Remaining XP:
            35
        """

        self.level_up = False

        while (

            self.level < 10

            and

            self.level
            in self.xp_requirements

            and

            self.xp
            >= self.xp_requirements[
                self.level
            ]

        ):

            # ----------------------------------------------------
            # REMEMBER OLD LEVEL
            # ----------------------------------------------------

            self.previous_level = (
                self.level
            )

            # ----------------------------------------------------
            # XP REQUIRED
            # ----------------------------------------------------

            required_xp = (
                self.xp_requirements[
                    self.level
                ]
            )

            # ----------------------------------------------------
            # REMOVE XP USED
            # ----------------------------------------------------

            self.xp -= required_xp

            # ----------------------------------------------------
            # LEVEL UP
            # ----------------------------------------------------

            self.level += 1

            self.level_up = True

        return self.level_up

    # ============================================================
    # XP REQUIRED
    # ============================================================

    def get_xp_required(self):

        if self.level >= 10:

            return None

        return self.xp_requirements.get(
            self.level
        )

    # ============================================================
    # XP PROGRESS
    # ============================================================

    def get_xp_progress(self):

        required_xp = (
            self.get_xp_required()
        )

        if required_xp is None:

            return 1.0

        if required_xp <= 0:

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
    # LOCATION
    # ============================================================

    def get_current_location(self):

        return self.location_unlocks.get(
            self.level,
            "Unknown Location",
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
    # CURRENT LEVEL NAME
    # ============================================================

    def get_level_name(self):

        return (
            f"LEVEL {self.level}"
        )

    # ============================================================
    # MAX LEVEL
    # ============================================================

    def is_max_level(self):

        return self.level >= 10

    # ============================================================
    # SAVE DATA
    # ============================================================

    def get_data(self):

        return {

            "level":
                self.level,

            "xp":
                self.xp,
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

        self.level = max(
            1,
            int(
                data.get(
                    "level",
                    1,
                )
            ),
        )

        self.xp = max(
            0,
            int(
                data.get(
                    "xp",
                    0,
                )
            ),
        )

        self.level_up = False

        self.previous_level = (
            self.level
        )

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
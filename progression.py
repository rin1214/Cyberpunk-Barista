from drink import get_unlocked_drinks


class Progression:
    """
    Handles the player's long-term progression.

    This class manages:
        - Current level
        - Current XP
        - XP required for the next level
        - Level-up detection
        - Drink unlocks
        - Location unlocks
        - Feature unlocks
    """

    def __init__(self):
        # ------------------------------------------
        # BASIC PLAYER PROGRESSION
        # ------------------------------------------

        self.level = 1
        self.xp = 0

        # ------------------------------------------
        # LEVEL-UP INFORMATION
        # ------------------------------------------

        self.level_up = False

        # Stores the level reached during the
        # most recent level-up.
        self.previous_level = 1

        # ------------------------------------------
        # XP REQUIREMENTS
        # ------------------------------------------

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

        # ------------------------------------------
        # LOCATION UNLOCKS
        # ------------------------------------------

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

        # ------------------------------------------
        # FEATURE UNLOCKS
        # ------------------------------------------

        self.feature_unlocks = {
            1: ["Basic Café"],
            2: ["New Drinks"],
            3: ["New Drinks"],
            4: ["New Location"],
            5: ["Special Customers"],
            6: ["Advanced Café"],
            7: ["Rush Hour"],
            8: ["Rare Drinks"],
            9: ["VIP Customers"],
            10: ["Grand Café"],
        }

    # ==================================================
    # XP SYSTEM
    # ==================================================

    def add_xp(self, amount):
        """
        Add XP to the player's progression.

        Returns True if the player levelled up.
        """

        if amount <= 0:
            return False

        self.xp += amount

        return self.check_level_up()

    # ==================================================
    # LEVEL-UP CHECK
    # ==================================================

    def check_level_up(self):
        """
        Check whether the player has enough XP
        to reach the next level.

        XP left over after a level-up is carried
        into the next level.
        """

        self.level_up = False

        while (
            self.level < 10
            and self.level in self.xp_requirements
            and self.xp >= self.xp_requirements[self.level]
        ):

            # Remember the level before changing it.
            self.previous_level = self.level

            # XP required for this level-up.
            required_xp = self.xp_requirements[self.level]

            # Remove the XP used for the level-up.
            self.xp -= required_xp

            # Increase the player's level.
            self.level += 1

            # Tell the game that a level-up happened.
            self.level_up = True

        return self.level_up

    # ==================================================
    # XP REQUIRED FOR NEXT LEVEL
    # ==================================================

    def get_xp_required(self):
        """
        Returns the total XP required for the
        player's current level.

        Returns None if the player is at the
        maximum level.
        """

        if self.level >= 10:
            return None

        return self.xp_requirements.get(self.level)

    # ==================================================
    # XP PROGRESS
    # ==================================================

    def get_xp_progress(self):
        """
        Returns XP progress as a decimal between 0 and 1.

        Example:

            50 / 100 XP
            = 0.5

        This can later be used to draw an XP bar.
        """

        required_xp = self.get_xp_required()

        if required_xp is None:
            return 1.0

        return min(
            self.xp / required_xp,
            1.0
        )

    # ==================================================
    # XP PERCENTAGE
    # ==================================================

    def get_xp_percentage(self):
        """
        Returns XP progress as a percentage.

        Example:

            50 / 100
            = 50%
        """

        return self.get_xp_progress() * 100

    # ==================================================
    # UNLOCKED DRINKS
    # ==================================================

    def get_unlocked_drinks(self):
        """
        Returns all drinks unlocked at the
        player's current level.
        """

        return get_unlocked_drinks(self.level)

    # ==================================================
    # LOCATION
    # ==================================================

    def get_current_location(self):
        """
        Returns the location belonging to
        the player's current level.
        """

        return self.location_unlocks.get(
            self.level,
            "Unknown Location"
        )

    # ==================================================
    # UNLOCKED FEATURES
    # ==================================================

    def get_unlocked_features(self):
        """
        Returns all features unlocked up to
        the player's current level.
        """

        unlocked_features = []

        for level in range(1, self.level + 1):

            features = self.feature_unlocks.get(
                level,
                []
            )

            unlocked_features.extend(features)

        return unlocked_features

    # ==================================================
    # LEVEL-UP STATUS
    # ==================================================

    def has_levelled_up(self):
        """
        Returns True when a level-up has happened.
        """

        return self.level_up

    # ==================================================
    # PREVIOUS LEVEL
    # ==================================================

    def get_previous_level(self):
        """
        Returns the level the player had before
        the most recent level-up.
        """

        return self.previous_level

    # ==================================================
    # CLEAR LEVEL-UP FLAG
    # ==================================================

    def clear_level_up(self):
        """
        Clears the level-up notification.

        This will be useful after the game has shown
        the Level Up screen.
        """

        self.level_up = False




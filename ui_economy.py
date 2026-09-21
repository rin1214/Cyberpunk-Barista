"""
============================================================
CYBERPUNK CAFÉ
UI ECONOMY / PLAYER PROFILE SYSTEM
============================================================

This file manages:

    • Credits / money
    • Player name
    • Saved profile
    • Current level compatibility
    • Current XP compatibility
    • Current location
    • Credit transactions
    • Save / load system

IMPORTANT SYSTEM SEPARATION
----------------------------

UIEconomy
    ↓
    Handles MONEY and PLAYER PROFILE

Progression
    ↓
    Handles XP and LEVELS

RewardSystem
    ↓
    Calculates XP and CREDIT rewards/penalties

Accuracy
    ↓
    Checks how accurately the player made
    the customer's requested drink

MixingStation
    ↓
    Handles the actual drink-making gameplay


IMPORTANT
---------

UIEconomy does NOT decide:

    "Was the order correct?"

RewardSystem does that calculation.

UIEconomy only receives the final credit change
and stores it.

============================================================
"""


import json
import os


class UIEconomy:

    # ========================================================
    # SAVE FILE
    # ========================================================

    SAVE_FILE = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "save_data.json"
    )

    # ========================================================
    # DEFAULT PLAYER VALUES
    # ========================================================

    STARTING_CREDITS = 100

    STARTING_XP = 0

    STARTING_LEVEL = 1

    # ========================================================
    # GAME LEVEL LIMIT
    # ========================================================

    MAX_LEVEL = 3

    # ========================================================
    # CREDIT LIMIT
    # ========================================================

    MIN_CREDITS = 0

    # ========================================================
    # OFFICIAL LOCATION NAMES
    # ========================================================
    #
    # These names must match progression.py.
    #
    # Level 1 → Back Alley Kiosk
    # Level 2 → Neon Lounge
    # Level 3 → Cyber Penthouse
    #
    # These are the ONLY three game locations.
    # ========================================================

    LOCATIONS = {

        1: "Back Alley Kiosk",

        2: "Neon Lounge",

        3: "Cyber Penthouse",

    }

    # ========================================================
    # INITIALISATION
    # ========================================================

    def __init__(
        self,
        screen,
        player_name="Player",
    ):

        # ----------------------------------------------------
        # SCREEN
        # ----------------------------------------------------

        self.screen = screen

        # ----------------------------------------------------
        # PLAYER NAME
        # ----------------------------------------------------

        if player_name:

            self.player_name = (
                str(player_name).strip()
            )

        else:

            self.player_name = "Player"

        # Prevent an empty name.

        if not self.player_name:

            self.player_name = "Player"

        # ----------------------------------------------------
        # PLAYER CREDITS
        # ----------------------------------------------------

        self.credits = (
            self.STARTING_CREDITS
        )

        # ----------------------------------------------------
        # XP COMPATIBILITY VALUE
        #
        # Progression is the real authority for XP.
        # This value exists for compatibility with
        # systems such as the leaderboard.
        # ----------------------------------------------------

        self.xp = (
            self.STARTING_XP
        )

        # ----------------------------------------------------
        # LEVEL COMPATIBILITY VALUE
        #
        # Progression is the real authority for level.
        # ----------------------------------------------------

        self.level = (
            self.STARTING_LEVEL
        )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        self.location = (
            self.LOCATIONS[
                self.STARTING_LEVEL
            ]
        )

        # ----------------------------------------------------
        # LOAD SAVED PLAYER
        # ----------------------------------------------------

        self.load_economy_data()

    # ========================================================
    # CREDIT MANAGEMENT
    # ========================================================

    def add_credits(
        self,
        amount,
    ):
        """
        Add or remove credits.

        Positive amount:
            Earn credits.

        Negative amount:
            Lose credits.

        Credits can never go below zero.
        """

        try:

            amount = int(amount)

        except (
            TypeError,
            ValueError,
        ):

            return False

        # ----------------------------------------------------
        # APPLY CREDIT CHANGE
        # ----------------------------------------------------

        self.credits += amount

        # ----------------------------------------------------
        # PREVENT NEGATIVE MONEY
        # ----------------------------------------------------

        if self.credits < self.MIN_CREDITS:

            self.credits = (
                self.MIN_CREDITS
            )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        self.save_economy_data()

        return True

    # ========================================================
    # GET CREDITS
    # ========================================================

    def get_credits(self):

        return self.credits

    # ========================================================
    # SET CREDITS
    # ========================================================

    def set_credits(
        self,
        amount,
    ):
        """
        Directly set the player's credit amount.
        """

        try:

            amount = int(amount)

        except (
            TypeError,
            ValueError,
        ):

            return False

        self.credits = max(
            self.MIN_CREDITS,
            amount,
        )

        self.save_economy_data()

        return True

    # ========================================================
    # SPEND CREDITS
    # ========================================================

    def spend_credits(
        self,
        amount,
    ):
        """
        Spend credits.

        Returns True if successful.

        Returns False if there are not enough credits.
        """

        try:

            amount = int(amount)

        except (
            TypeError,
            ValueError,
        ):

            return False

        # ----------------------------------------------------
        # Invalid purchase amount
        # ----------------------------------------------------

        if amount < 0:

            return False

        # ----------------------------------------------------
        # Not enough money
        # ----------------------------------------------------

        if self.credits < amount:

            return False

        # ----------------------------------------------------
        # PAY
        # ----------------------------------------------------

        self.credits -= amount

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        self.save_economy_data()

        return True

    # ========================================================
    # APPLY REWARD RESULT
    # ========================================================

    def apply_reward(
        self,
        reward_result,
    ):
        """
        Apply the final credit result produced by RewardSystem.

        The reward object may provide:

            net_credits

        or:

            total_credits
        """

        if reward_result is None:

            return False

        # ----------------------------------------------------
        # READ FINAL CREDIT CHANGE
        # ----------------------------------------------------

        if hasattr(
            reward_result,
            "net_credits",
        ):

            credit_change = (
                reward_result.net_credits
            )

        elif hasattr(
            reward_result,
            "total_credits",
        ):

            credit_change = (
                reward_result.total_credits
            )

        else:

            return False

        # ----------------------------------------------------
        # APPLY
        # ----------------------------------------------------

        return self.add_credits(
            credit_change
        )

    # ========================================================
    # COMPATIBILITY METHOD
    # ========================================================

    def serve_order(
        self,
        is_correct=True,
    ):
        """
        Compatibility method for older collaborator code.

        The current game should use:

            RewardSystem
                ↓
            economy.apply_reward()

        This method intentionally does not give rewards
        so that the player cannot receive rewards twice.
        """

        return True

    # ========================================================
    # PROGRESSION SYNCHRONISATION
    # ========================================================

    def sync_progression(
        self,
        progression,
    ):
        """
        Synchronise the economy compatibility values
        with the real Progression system.

        Progression remains the authority.

        Updates:

            economy.level
            economy.xp
            economy.location
        """

        if progression is None:

            return False

        # ----------------------------------------------------
        # LEVEL
        # ----------------------------------------------------

        try:

            self.level = int(
                progression.level
            )

        except (
            TypeError,
            ValueError,
        ):

            self.level = (
                self.STARTING_LEVEL
            )

        # ----------------------------------------------------
        # CLAMP LEVEL
        # ----------------------------------------------------

        self.level = max(
            1,
            min(
                self.level,
                self.MAX_LEVEL,
            ),
        )

        # ----------------------------------------------------
        # XP
        # ----------------------------------------------------

        try:

            self.xp = max(
                0,
                int(
                    progression.xp
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            self.xp = (
                self.STARTING_XP
            )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------
        #
        # Prefer Progression's location.
        # If it does not provide one, use this file's
        # official location table.
        # ----------------------------------------------------

        if hasattr(
            progression,
            "get_current_location",
        ):

            location = (
                progression.get_current_location()
            )

            # -----------------------------------------------
            # Make sure the location is one of our official
            # three locations.
            # -----------------------------------------------

            if location in self.LOCATIONS.values():

                self.location = location

            else:

                self.location = (
                    self.LOCATIONS[
                        self.level
                    ]
                )

        else:

            self.location = (
                self.LOCATIONS[
                    self.level
                ]
            )

        return True

    # ========================================================
    # SET LEVEL
    # ========================================================

    def set_level(
        self,
        level,
    ):
        """
        Update the compatibility level.

        Level is always restricted to:

            1
            2
            3
        """

        try:

            level = int(level)

        except (
            TypeError,
            ValueError,
        ):

            return False

        # ----------------------------------------------------
        # CLAMP LEVEL
        # ----------------------------------------------------

        self.level = max(
            1,
            min(
                level,
                self.MAX_LEVEL,
            ),
        )

        # ----------------------------------------------------
        # UPDATE LOCATION
        # ----------------------------------------------------

        self.location = (
            self.LOCATIONS[
                self.level
            ]
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        self.save_economy_data()

        return True

    # ========================================================
    # SET XP
    # ========================================================

    def set_xp(
        self,
        xp,
    ):
        """
        Update the compatibility XP value.

        XP can never become negative.
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

        self.save_economy_data()

        return True

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
    # GET PLAYER NAME
    # ========================================================

    def get_player_name(self):

        return self.player_name

    # ========================================================
    # GET LOCATION
    # ========================================================

    def get_location(self):

        return self.location

    # ========================================================
    # RESET ECONOMY
    # ========================================================

    def reset_economy(self):
        """
        Reset the player's economy/profile values.

        Result:

            Credits  = $100
            XP       = 0
            Level    = 1
            Location = Back Alley Kiosk
        """

        self.credits = (
            self.STARTING_CREDITS
        )

        self.xp = (
            self.STARTING_XP
        )

        self.level = (
            self.STARTING_LEVEL
        )

        self.location = (
            self.LOCATIONS[
                self.STARTING_LEVEL
            ]
        )

        self.save_economy_data()

    # ========================================================
    # SAVE ECONOMY DATA
    # ========================================================

    def save_economy_data(self):
        """
        Save the player's profile into save_data.json.

        Multiple player profiles can exist in the same file.

        Example:

        {
            "Lucy": {
                "credits": 200,
                "xp": 75,
                "level": 1,
                "location": "Back Alley Kiosk"
            },

            "Rin": {
                "credits": 350,
                "xp": 140,
                "level": 2,
                "location": "Neon Lounge"
            }
        }
        """

        all_profiles = {}

        # ----------------------------------------------------
        # READ EXISTING PROFILES
        # ----------------------------------------------------

        if os.path.exists(
            self.SAVE_FILE
        ):

            try:

                with open(
                    self.SAVE_FILE,
                    "r",
                    encoding="utf-8",
                ) as file:

                    all_profiles = (
                        json.load(file)
                    )

                # Make sure the save file contains
                # a dictionary.

                if not isinstance(
                    all_profiles,
                    dict,
                ):

                    all_profiles = {}

            except (
                IOError,
                json.JSONDecodeError,
            ):

                all_profiles = {}

        # ----------------------------------------------------
        # NORMALISE EXISTING PLAYER LOCATIONS
        # ----------------------------------------------------
        #
        # This is important because older save data may
        # contain:
        #
        # "BACK ALLEY KIOSK"
        # "NEON LOUNGE"
        # "CYBER PENTHOUSE"
        #
        # or even the newer incorrect names.
        #
        # We now determine location from LEVEL instead.
        # ----------------------------------------------------

        for name, profile in all_profiles.items():

            if not isinstance(
                profile,
                dict,
            ):

                continue

            try:

                saved_level = int(
                    profile.get(
                        "level",
                        1,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                saved_level = 1

            saved_level = max(
                1,
                min(
                    saved_level,
                    self.MAX_LEVEL,
                ),
            )

            profile["level"] = (
                saved_level
            )

            # -----------------------------------------------
            # Make the location automatically match the
            # player's level.
            # -----------------------------------------------

            profile["location"] = (
                self.LOCATIONS[
                    saved_level
                ]
            )

            # -----------------------------------------------
            # Keep XP valid.
            # -----------------------------------------------

            try:

                profile["xp"] = max(
                    0,
                    int(
                        profile.get(
                            "xp",
                            0,
                        )
                    ),
                )

            except (
                TypeError,
                ValueError,
            ):

                profile["xp"] = 0

            # -----------------------------------------------
            # Keep credits valid.
            # -----------------------------------------------

            try:

                profile["credits"] = max(
                    self.MIN_CREDITS,
                    int(
                        profile.get(
                            "credits",
                            self.STARTING_CREDITS,
                        )
                    ),
                )

            except (
                TypeError,
                ValueError,
            ):

                profile["credits"] = (
                    self.STARTING_CREDITS
                )

        # ----------------------------------------------------
        # SAVE CURRENT PLAYER
        # ----------------------------------------------------

        self.level = max(
            1,
            min(
                int(self.level),
                self.MAX_LEVEL,
            ),
        )

        self.xp = max(
            0,
            int(self.xp),
        )

        self.credits = max(
            self.MIN_CREDITS,
            int(self.credits),
        )

        # Always derive location from level.

        self.location = (
            self.LOCATIONS[
                self.level
            ]
        )

        all_profiles[
            self.player_name
        ] = {

            "credits":
                self.credits,

            "xp":
                self.xp,

            "level":
                self.level,

            "location":
                self.location,
        }

        # ----------------------------------------------------
        # WRITE FILE
        # ----------------------------------------------------

        try:

            with open(
                self.SAVE_FILE,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    all_profiles,
                    file,
                    indent=4,
                )

        except IOError as e:

            print(
                "[ECONOMY ERROR] "
                f"Could not save economy data: {e}"
            )

    # ========================================================
    # LOAD ECONOMY DATA
    # ========================================================

    def load_economy_data(self):
        """
        Load the player's saved profile.

        If no saved profile exists,
        create a new player.

        IMPORTANT:

        Location is always calculated from the saved level.

        This prevents old location names from remaining in
        the save file.
        """

        # ----------------------------------------------------
        # CHECK SAVE FILE
        # ----------------------------------------------------

        if os.path.exists(
            self.SAVE_FILE
        ):

            try:

                with open(
                    self.SAVE_FILE,
                    "r",
                    encoding="utf-8",
                ) as file:

                    all_profiles = (
                        json.load(file)
                    )

                if not isinstance(
                    all_profiles,
                    dict,
                ):

                    all_profiles = {}

                # ------------------------------------------------
                # FIND PLAYER
                # ------------------------------------------------

                if (
                    self.player_name
                    in all_profiles
                ):

                    player_data = (
                        all_profiles[
                            self.player_name
                        ]
                    )

                    if not isinstance(
                        player_data,
                        dict,
                    ):

                        player_data = {}

                    # --------------------------------------------
                    # CREDITS
                    # --------------------------------------------

                    try:

                        self.credits = max(
                            self.MIN_CREDITS,
                            int(
                                player_data.get(
                                    "credits",
                                    self.STARTING_CREDITS,
                                )
                            ),
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        self.credits = (
                            self.STARTING_CREDITS
                        )

                    # --------------------------------------------
                    # XP
                    # --------------------------------------------

                    try:

                        self.xp = max(
                            0,
                            int(
                                player_data.get(
                                    "xp",
                                    self.STARTING_XP,
                                )
                            ),
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        self.xp = (
                            self.STARTING_XP
                        )

                    # --------------------------------------------
                    # LEVEL
                    # --------------------------------------------

                    try:

                        self.level = int(
                            player_data.get(
                                "level",
                                self.STARTING_LEVEL,
                            )
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        self.level = (
                            self.STARTING_LEVEL
                        )

                    # --------------------------------------------
                    # LEVEL MUST BE 1–3
                    # --------------------------------------------

                    self.level = max(
                        1,
                        min(
                            self.level,
                            self.MAX_LEVEL,
                        ),
                    )

                    # --------------------------------------------
                    # LOCATION
                    #
                    # DO NOT TRUST OLD SAVED LOCATION.
                    #
                    # Calculate it from the level.
                    # --------------------------------------------

                    self.location = (
                        self.LOCATIONS[
                            self.level
                        ]
                    )

                    print(
                        "[ECONOMY] "
                        f"Loaded profile for "
                        f"'{self.player_name}'"
                    )

                    # ------------------------------------------------
                    # Save once after loading.
                    #
                    # This automatically cleans old location names
                    # from the save file.
                    # ------------------------------------------------

                    self.save_economy_data()

                    return

            except (
                IOError,
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ) as error:

                print(
                    "[ECONOMY ERROR] "
                    f"Could not load save data "
                    f"({error}). "
                    "Starting fresh."
                )

        # ========================================================
        # CREATE NEW PROFILE
        # ========================================================

        print(
            "[ECONOMY] "
            f"Initialized new profile for "
            f"'{self.player_name}'"
        )

        self.credits = (
            self.STARTING_CREDITS
        )

        self.xp = (
            self.STARTING_XP
        )

        self.level = (
            self.STARTING_LEVEL
        )

        self.location = (
            self.LOCATIONS[
                self.STARTING_LEVEL
            ]
        )

        self.save_economy_data()

    # ========================================================
    # BACKGROUND COLOR
    # ========================================================

    def get_level_bg_color(self):
        """
        Return a compatible background color for older systems.
        """

        colors = {

            1: (15, 10, 25),

            2: (25, 10, 20),

            3: (20, 5, 30),

        }

        return colors.get(
            self.level,
            colors[3],
        )

    # ========================================================
    # SAVE DATA EXPORT
    # ========================================================

    def get_data(self):
        """
        Return the player's economy data as a dictionary.
        """

        return {

            "player_name":
                self.player_name,

            "credits":
                self.credits,

            "xp":
                self.xp,

            "level":
                self.level,

            "location":
                self.location,

        }

    # ========================================================
    # OLD ECONOMY HUD
    # ========================================================
    #
    # The current game draws its HUD elsewhere.
    #
    # This empty method remains for compatibility with
    # older code that may still call:
    #
    #     economy.draw()
    #
    # ========================================================

    def draw(self):

        pass
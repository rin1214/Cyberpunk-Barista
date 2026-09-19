"""
============================================================
CYBERPUNK CAFÉ
UI ECONOMY / PLAYER PROFILE SYSTEM
============================================================

This file manages the player's:

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

Example:

    Customer order = 3/4 correct

    RewardSystem calculates:

        Base credits       = +$24
        Mistake penalty    = -$10
        Combo bonus        = +$0
        Speed bonus        = +$0

        Final credit change = +$14

    UIEconomy then does:

        economy.add_credits(14)

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
    # CREDIT LIMIT
    # ========================================================

    MIN_CREDITS = 0

    # ========================================================
    # LOCATION NAMES
    #
    # These are kept compatible with the existing
    # map/economy system.
    # ========================================================

    LOCATIONS = {

        1: "BACK ALLEY KIOSK",

        2: "NEON LOUNGE",

        3: "CYBER PENTHOUSE",

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
        #
        # Some older systems expect UIEconomy to have
        # access to the Pygame screen.
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
        #
        # Starting money.
        # ----------------------------------------------------

        self.credits = (
            self.STARTING_CREDITS
        )

        # ----------------------------------------------------
        # XP COMPATIBILITY VALUE
        #
        # IMPORTANT:
        #
        # Progression is the real authority for XP.
        #
        # This value exists so older systems such as
        # the leaderboard can still access:
        #
        #     economy.xp
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
        Add credits to the player's wallet.

        Positive number:
            Adds money.

        Negative number:
            Removes money.

        Credits can NEVER go below zero.

        Example:

            Current credits = $100

            add_credits(30)

            New credits = $130


        Example with penalty:

            Current credits = $100

            add_credits(-10)

            New credits = $90
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

        Useful when synchronising systems.
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
        Spend credits on something such as:

            • map upgrades
            • café upgrades
            • future cosmetics
            • future items

        Returns:

            True
                Purchase successful.

            False
                Not enough credits.
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
        Applies the final credit result produced by
        RewardSystem.

        Expected RewardResult:

            reward_result.total_credits

        The value may be:

            positive
                player earned credits

            zero
                no credit change

            negative
                player lost credits because of a penalty

        Example:

            total_credits = 14

            $100 → $114


        Example:

            total_credits = -5

            $100 → $95
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

        --------------------------------------------------------
        IMPORTANT
        --------------------------------------------------------

        The NEW game should NOT use this method for rewards.

        The new system should use:

            RewardSystem
                ↓
            economy.apply_reward()

        This method exists so older code does not immediately
        break while the new architecture is being integrated.

        It intentionally does NOT award or remove credits,
        because doing so could cause double rewards.
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
        Synchronises UIEconomy's compatibility values
        with the real Progression system.

        Progression remains the authority.

        This updates:

            economy.level
            economy.xp
            economy.location
        """

        if progression is None:

            return False

        # ----------------------------------------------------
        # LEVEL
        # ----------------------------------------------------

        self.level = int(
            progression.level
        )

        # ----------------------------------------------------
        # XP
        # ----------------------------------------------------

        self.xp = int(
            progression.xp
        )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        if hasattr(
            progression,
            "get_current_location",
        ):

            self.location = (
                progression.get_current_location()
            )

        else:

            self.location = (
                self.LOCATIONS.get(
                    self.level,
                    f"SECTOR {self.level} HUB",
                )
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
        Updates the compatibility level.

        Normally main.py should synchronize this from
        Progression instead of changing it directly.
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
            level,
        )

        self.location = (
            self.LOCATIONS.get(
                self.level,
                f"SECTOR {self.level} HUB",
            )
        )

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
        Updates the compatibility XP value.

        Progression should normally be used to
        actually change XP.
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

            Credits = $100
            XP      = 0
            Level   = 1
            Location = Back Alley Kiosk

        IMPORTANT:

        Progression.reset() should ALSO be called by main.py
        when performing a complete game reset.
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

                # Make sure the file contains a dictionary.

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
        # SAVE CURRENT PLAYER
        # ----------------------------------------------------

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

                    # --------------------------------------------
                    # CREDITS
                    # --------------------------------------------

                    self.credits = max(
                        self.MIN_CREDITS,
                        int(
                            player_data.get(
                                "credits",
                                self.STARTING_CREDITS,
                            )
                        ),
                    )

                    # --------------------------------------------
                    # COMPATIBILITY XP
                    # --------------------------------------------

                    self.xp = max(
                        0,
                        int(
                            player_data.get(
                                "xp",
                                self.STARTING_XP,
                            )
                        ),
                    )

                    # --------------------------------------------
                    # COMPATIBILITY LEVEL
                    # --------------------------------------------

                    self.level = max(
                        1,
                        int(
                            player_data.get(
                                "level",
                                self.STARTING_LEVEL,
                            )
                        ),
                    )

                    # --------------------------------------------
                    # LOCATION
                    # --------------------------------------------

                    self.location = (
                        self.LOCATIONS.get(
                            self.level,
                            f"SECTOR {self.level} HUB",
                        )
                    )

                    print(
                        "[ECONOMY] "
                        f"Loaded profile for "
                        f"'{self.player_name}'"
                    )

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
        Returns a compatible background color
        for older systems.
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
        Returns the player's economy data as a dictionary.

        Useful for other systems.
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
    # OLD ECONOMY HUD REMOVED
    # ========================================================

    def draw(self):
      

        pass
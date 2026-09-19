"""
CYBERPUNK CAFÉ
REWARD SYSTEM

This file calculates the rewards earned after serving
a customer.

The reward system handles:

    • Accuracy rewards
    • Combo rewards
    • Speed rewards
    • XP earned
    • Credits / money earned

IMPORTANT:

This class does NOT control the player's level.

Progression.py controls:
    • Level
    • XP progression
    • Level ups
    • Drink unlocks
    • Location progression
"""


from dataclasses import dataclass


# ============================================================
# REWARD RESULT
# ============================================================

@dataclass
class RewardResult:

    # --------------------------------------------------------
    # BASE REWARD
    # --------------------------------------------------------

    base_xp: int

    base_credits: int

    # --------------------------------------------------------
    # COMBO BONUS
    # --------------------------------------------------------

    combo_bonus_xp: int

    combo_bonus_credits: int

    # --------------------------------------------------------
    # SPEED BONUS
    # --------------------------------------------------------

    speed_bonus_xp: int

    speed_bonus_credits: int

    # --------------------------------------------------------
    # FINAL REWARD
    # --------------------------------------------------------

    total_xp: int

    total_credits: int

    # --------------------------------------------------------
    # CURRENT COMBO
    # --------------------------------------------------------

    combo_count: int

    # ========================================================
    # POSITIVE REWARD
    # ========================================================

    @property
    def is_positive(self):

        return (

            self.total_xp > 0

            or

            self.total_credits > 0

        )

    # ========================================================
    # ACCURACY TEXT
    # ========================================================

    @property
    def accuracy_text(self):

        return (
            f"{self.combo_count}"
        )


# ============================================================
# REWARD SYSTEM
# ============================================================

class RewardSystem:

    """
    Calculates rewards after each customer.

    RewardSystem does NOT control:

        • player level
        • XP progression
        • drink unlocks
        • locations

    Those systems belong to Progression.
    """

    # ========================================================
    # BASE REWARDS
    # ========================================================

    BASE_REWARDS = {

        # Perfect order
        4: (
            40,
            30,
        ),

        # 3 / 4
        3: (
            30,
            24,
        ),

        # 2 / 4
        2: (
            20,
            18,
        ),

        # 1 / 4
        1: (
            10,
            10,
        ),

        # 0 / 4
        0: (
            5,
            5,
        ),
    }

    # ========================================================
    # COMBO
    # ========================================================

    COMBO_XP_BONUS = 5

    COMBO_CREDITS_BONUS = 3

    # ========================================================
    # SPEED
    # ========================================================

    SPEED_XP_BONUS = 10

    SPEED_CREDITS_BONUS = 5

    # ========================================================
    # INITIALISATION
    # ========================================================

    def __init__(self):

        # Current perfect-order combo.
        self.combo = 0

        # Total credits earned during this
        # current gameplay session.
        self.total_credits_earned = 0

        # Total XP earned during this
        # current gameplay session.
        self.total_xp_earned = 0

    # ========================================================
    # BASE REWARD
    # ========================================================

    def get_base_reward(
        self,
        correct_count,
    ):

        return self.BASE_REWARDS.get(
            int(correct_count),
            (
                0,
                0,
            ),
        )

    # ========================================================
    # UPDATE COMBO
    # ========================================================

    def update_combo(
        self,
        correct_count,
    ):

        """
        Perfect orders increase the combo.

        Anything below 4/4 resets the combo.
        """

        if int(correct_count) == 4:

            self.combo += 1

        else:

            self.combo = 0

        return self.combo

    # ========================================================
    # CALCULATE REWARD
    # ========================================================

    def calculate_reward(
        self,
        accuracy_result,
        served_quickly=False,
    ):

        """
        Calculates the complete reward.

        accuracy_result is expected to contain:

            accuracy_result.correct_count

        Example:

            4 / 4
            3 / 4
            2 / 4
            1 / 4
            0 / 4
        """

        # ----------------------------------------------------
        # GET ACCURACY
        # ----------------------------------------------------

        correct_count = int(
            accuracy_result.correct_count
        )

        # Keep the value safely inside
        # the expected 0–4 range.

        correct_count = max(
            0,
            min(
                correct_count,
                4,
            ),
        )

        # ----------------------------------------------------
        # BASE REWARD
        # ----------------------------------------------------

        (
            base_xp,
            base_credits,
        ) = self.get_base_reward(
            correct_count
        )

        # ----------------------------------------------------
        # UPDATE COMBO
        # ----------------------------------------------------

        combo_count = (
            self.update_combo(
                correct_count
            )
        )

        # ----------------------------------------------------
        # COMBO BONUS
        # ----------------------------------------------------

        combo_bonus_xp = 0

        combo_bonus_credits = 0

        if combo_count >= 2:

            combo_bonus_xp = (

                combo_count - 1

            ) * self.COMBO_XP_BONUS

            combo_bonus_credits = (

                combo_count - 1

            ) * self.COMBO_CREDITS_BONUS

        # ----------------------------------------------------
        # SPEED BONUS
        # ----------------------------------------------------

        speed_bonus_xp = 0

        speed_bonus_credits = 0

        if served_quickly:

            speed_bonus_xp = (
                self.SPEED_XP_BONUS
            )

            speed_bonus_credits = (
                self.SPEED_CREDITS_BONUS
            )

        # ----------------------------------------------------
        # TOTAL XP
        # ----------------------------------------------------

        total_xp = (

            base_xp

            + combo_bonus_xp

            + speed_bonus_xp

        )

        # ----------------------------------------------------
        # TOTAL CREDITS
        # ----------------------------------------------------

        total_credits = (

            base_credits

            + combo_bonus_credits

            + speed_bonus_credits

        )

        # ----------------------------------------------------
        # SESSION TOTALS
        # ----------------------------------------------------

        self.total_xp_earned += (
            total_xp
        )

        self.total_credits_earned += (
            total_credits
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        return RewardResult(

            base_xp=base_xp,

            base_credits=base_credits,

            combo_bonus_xp=combo_bonus_xp,

            combo_bonus_credits=
                combo_bonus_credits,

            speed_bonus_xp=
                speed_bonus_xp,

            speed_bonus_credits=
                speed_bonus_credits,

            total_xp=total_xp,

            total_credits=
                total_credits,

            combo_count=combo_count,
        )

    # ========================================================
    # CURRENT COMBO
    # ========================================================

    def get_combo(self):

        return self.combo

    # ========================================================
    # TOTAL CREDITS
    # ========================================================

    def get_total_credits(self):

        return (
            self.total_credits_earned
        )

    # ========================================================
    # TOTAL XP
    # ========================================================

    def get_total_xp(self):

        return (
            self.total_xp_earned
        )

    # ========================================================
    # DATA
    # ========================================================

    def get_data(self):

        return {

            "combo":
                self.combo,

            "total_credits_earned":
                self.total_credits_earned,

            "total_xp_earned":
                self.total_xp_earned,
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.combo = 0

        self.total_credits_earned = 0

        self.total_xp_earned = 0
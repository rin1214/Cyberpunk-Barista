"""
============================================================
CYBERPUNK CAFÉ
REWARD SYSTEM
============================================================

This file calculates the rewards and penalties earned
after serving one customer.

The RewardSystem handles:

    • Accuracy rewards
    • Mistake penalties
    • Combo rewards
    • Speed rewards
    • XP earned
    • Credits earned/lost

IMPORTANT:

This class does NOT control the player's level.

Progression.py controls:

    • XP
    • Level
    • Level-ups
    • Drink unlocks
    • Location progression


UIEconomy controls:

    • Player credits
    • Saving credits
    • Loading credits
    • Spending credits
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
    # MISTAKE PENALTY
    # --------------------------------------------------------

    credit_penalty: int

    # --------------------------------------------------------
    # FINAL XP
    # --------------------------------------------------------

    total_xp: int

    # --------------------------------------------------------
    # FINAL CREDIT CHANGE
    # --------------------------------------------------------

    net_credits: int

    # --------------------------------------------------------
    # COMBO
    # --------------------------------------------------------

    combo_count: int

    # ========================================================
    # POSITIVE REWARD
    # ========================================================

    @property
    def is_positive(self):
        """
        Returns True when the player gained something.

        XP is included because XP can still be positive
        even when a credit penalty occurs.
        """

        return (
            self.total_xp > 0
            or
            self.net_credits > 0
        )

    # ========================================================
    # ACCURACY TEXT
    # ========================================================

    @property
    def accuracy_text(self):
        """
        Compatibility property.

        Actual accuracy information will come from
        accuracy.py.
        """

        return ""


# ============================================================
# REWARD SYSTEM
# ============================================================

class RewardSystem:

    """
    Calculates the reward for one completed customer order.

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

        # ----------------------------------------------------
        # PERFECT ORDER
        # ----------------------------------------------------

        4: (
            40,
            30,
        ),

        # ----------------------------------------------------
        # 3 / 4
        # ----------------------------------------------------

        3: (
            30,
            24,
        ),

        # ----------------------------------------------------
        # 2 / 4
        # ----------------------------------------------------

        2: (
            20,
            18,
        ),

        # ----------------------------------------------------
        # 1 / 4
        # ----------------------------------------------------

        1: (
            10,
            10,
        ),

        # ----------------------------------------------------
        # 0 / 4
        # ----------------------------------------------------

        0: (
            5,
            5,
        ),
    }

    # ========================================================
    # MISTAKE PENALTY
    # ========================================================

    # Every imperfect order receives a $10 penalty.

    MISTAKE_CREDIT_PENALTY = 10

    # ========================================================
    # COMBO
    # ========================================================

    # Every additional perfect order in a combo
    # gives +5 XP.

    COMBO_XP_BONUS = 5

    # Every additional perfect order in a combo
    # gives +3 credits.

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

        # ----------------------------------------------------
        # CURRENT COMBO
        # ----------------------------------------------------

        self.combo = 0

        # ----------------------------------------------------
        # SESSION TOTAL CREDITS
        # ----------------------------------------------------

        self.total_credits_earned = 0

        # ----------------------------------------------------
        # SESSION TOTAL XP
        # ----------------------------------------------------

        self.total_xp_earned = 0

        # ----------------------------------------------------
        # SESSION TOTAL PENALTIES
        # ----------------------------------------------------

        self.total_credit_penalties = 0

    # ========================================================
    # BASE REWARD
    # ========================================================

    def get_base_reward(
        self,
        correct_count,
    ):
        """
        Returns:

            (base_xp, base_credits)

        based on the number of correct requirements.
        """

        try:

            correct_count = int(
                correct_count
            )

        except (
            TypeError,
            ValueError,
        ):

            correct_count = 0

        # Keep the number between 0 and 4.

        correct_count = max(
            0,
            min(
                correct_count,
                4,
            ),
        )

        return self.BASE_REWARDS.get(
            correct_count,
            (
                0,
                0,
            ),
        )

    # ========================================================
    # GET MISTAKE PENALTY
    # ========================================================

    def get_mistake_penalty(
        self,
        correct_count,
    ):
        """
        Returns the credit penalty.

        Perfect order:
            4/4 → $0 penalty

        Any imperfect order:
            3/4 → $10 penalty
            2/4 → $10 penalty
            1/4 → $10 penalty
            0/4 → $10 penalty
        """

        try:

            correct_count = int(
                correct_count
            )

        except (
            TypeError,
            ValueError,
        ):

            correct_count = 0

        if correct_count == 4:

            return 0

        return self.MISTAKE_CREDIT_PENALTY

    # ========================================================
    # UPDATE COMBO
    # ========================================================

    def update_combo(
        self,
        correct_count,
    ):
        """
        Perfect orders increase the combo.

        Any imperfect order resets the combo to zero.
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
        Calculate the complete reward for one customer.

        accuracy_result must contain:

            accuracy_result.correct_count

        Examples:

            4/4
            3/4
            2/4
            1/4
            0/4
        """

        # ====================================================
        # GET CORRECT COUNT
        # ====================================================

        try:

            correct_count = int(
                accuracy_result.correct_count
            )

        except (
            AttributeError,
            TypeError,
            ValueError,
        ):

            correct_count = 0

        # Keep value safely between 0 and 4.

        correct_count = max(
            0,
            min(
                correct_count,
                4,
            ),
        )

        # ====================================================
        # BASE REWARD
        # ====================================================

        (
            base_xp,
            base_credits,
        ) = self.get_base_reward(
            correct_count
        )

        # ====================================================
        # UPDATE COMBO
        # ====================================================

        combo_count = (
            self.update_combo(
                correct_count
            )
        )

        # ====================================================
        # COMBO BONUS
        # ====================================================

        combo_bonus_xp = 0

        combo_bonus_credits = 0

        # ----------------------------------------------------
        # Combo starts giving a bonus from combo 2.
        #
        # Combo 1:
        #   no bonus
        #
        # Combo 2:
        #   +5 XP
        #   +3 credits
        #
        # Combo 3:
        #   +10 XP
        #   +6 credits
        #
        # Combo 4:
        #   +15 XP
        #   +9 credits
        # ----------------------------------------------------

        if combo_count >= 2:

            combo_bonus_xp = (
                (combo_count - 1)
                * self.COMBO_XP_BONUS
            )

            combo_bonus_credits = (
                (combo_count - 1)
                * self.COMBO_CREDITS_BONUS
            )

        # ====================================================
        # SPEED BONUS
        # ====================================================

        speed_bonus_xp = 0

        speed_bonus_credits = 0

        if served_quickly:

            speed_bonus_xp = (
                self.SPEED_XP_BONUS
            )

            speed_bonus_credits = (
                self.SPEED_CREDITS_BONUS
            )

        # ====================================================
        # MISTAKE PENALTY
        # ====================================================

        credit_penalty = (
            self.get_mistake_penalty(
                correct_count
            )
        )

        # ====================================================
        # FINAL XP
        # ====================================================

        total_xp = (

            base_xp

            + combo_bonus_xp

            + speed_bonus_xp

        )

        # ====================================================
        # FINAL CREDIT CHANGE
        # ====================================================

        net_credits = (

            base_credits

            + combo_bonus_credits

            + speed_bonus_credits

            - credit_penalty

        )

        # ====================================================
        # SESSION STATISTICS
        # ====================================================

        self.total_xp_earned += (
            total_xp
        )

        # Only count actual earned credits here.
        #
        # A negative net result is not added as
        # "credits earned."

        if net_credits > 0:

            self.total_credits_earned += (
                net_credits
            )

        # Store penalty statistics.

        self.total_credit_penalties += (
            credit_penalty
        )

        # ====================================================
        # RETURN RESULT
        # ====================================================

        return RewardResult(

            base_xp=base_xp,

            base_credits=base_credits,

            combo_bonus_xp=
                combo_bonus_xp,

            combo_bonus_credits=
                combo_bonus_credits,

            speed_bonus_xp=
                speed_bonus_xp,

            speed_bonus_credits=
                speed_bonus_credits,

            credit_penalty=
                credit_penalty,

            total_xp=
                total_xp,

            net_credits=
                net_credits,

            combo_count=
                combo_count,
        )

    # ========================================================
    # CURRENT COMBO
    # ========================================================

    def get_combo(self):

        return self.combo

    # ========================================================
    # TOTAL XP EARNED
    # ========================================================

    def get_total_xp(self):

        return (
            self.total_xp_earned
        )

    # ========================================================
    # TOTAL CREDITS EARNED
    # ========================================================

    def get_total_credits(self):

        return (
            self.total_credits_earned
        )

    # ========================================================
    # TOTAL PENALTIES
    # ========================================================

    def get_total_credit_penalties(self):

        return (
            self.total_credit_penalties
        )

    # ========================================================
    # SESSION DATA
    # ========================================================

    def get_data(self):

        return {

            "combo":
                self.combo,

            "total_xp_earned":
                self.total_xp_earned,

            "total_credits_earned":
                self.total_credits_earned,

            "total_credit_penalties":
                self.total_credit_penalties,
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        """
        Reset temporary/session reward information.
        """

        self.combo = 0

        self.total_credits_earned = 0

        self.total_xp_earned = 0

        self.total_credit_penalties = 0
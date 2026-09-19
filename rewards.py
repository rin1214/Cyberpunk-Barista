from dataclasses import dataclass


@dataclass
class RewardResult:
    """
    Stores the rewards earned from serving
    one customer.
    """

    base_xp: int
    base_credits: int

    combo_bonus_xp: int
    combo_bonus_credits: int

    speed_bonus_xp: int
    speed_bonus_credits: int

    total_xp: int
    total_credits: int

    combo_count: int

    @property
    def is_positive(self):
        """
        Returns True if the player earned
        a reward.
        """

        return (
            self.total_xp > 0
            or self.total_credits > 0
        )


class RewardSystem:
    """
    Calculates XP and credit rewards.

    This class does NOT control the player's
    level. That job belongs to Progression.
    """

    # ==========================================
    # BASE REWARDS
    # ==========================================

    BASE_REWARDS = {
        4: (40, 30),
        3: (30, 24),
        2: (20, 18),
        1: (10, 10),
        0: (5, 5),
    }

    # ==========================================
    # COMBO REWARDS
    # ==========================================

    COMBO_XP_BONUS = 5
    COMBO_CREDITS_BONUS = 3

    # ==========================================
    # SPEED REWARDS
    # ==========================================

    SPEED_XP_BONUS = 10
    SPEED_CREDITS_BONUS = 5

    def __init__(self):
        self.combo = 0
        self.total_credits_earned = 0

    # ==========================================
    # ACCURACY REWARD
    # ==========================================

    def get_base_reward(self, correct_count):
        """
        Returns the base XP and credits
        for the accuracy result.
        """

        return self.BASE_REWARDS.get(
            correct_count,
            (0, 0)
        )

    # ==========================================
    # COMBO
    # ==========================================

    def update_combo(self, correct_count):
        """
        Updates the player's combo.

        A perfect order increases the combo.

        A less-than-perfect order resets it.
        """

        if correct_count == 4:
            self.combo += 1
        else:
            self.combo = 0

        return self.combo

    # ==========================================
    # CALCULATE REWARD
    # ==========================================

    def calculate_reward(
        self,
        accuracy_result,
        served_quickly=False
    ):
        """
        Calculate the complete reward for
        the current customer.

        Returns a RewardResult.
        """

        correct_count = accuracy_result.correct_count

        # --------------------------------------
        # Base reward
        # --------------------------------------

        base_xp, base_credits = self.get_base_reward(
            correct_count
        )

        # --------------------------------------
        # Update combo
        # --------------------------------------

        combo_count = self.update_combo(
            correct_count
        )

        # --------------------------------------
        # Combo bonus
        # --------------------------------------

        combo_bonus_xp = 0
        combo_bonus_credits = 0

        if combo_count >= 2:

            combo_bonus_xp = (
                combo_count - 1
            ) * self.COMBO_XP_BONUS

            combo_bonus_credits = (
                combo_count - 1
            ) * self.COMBO_CREDITS_BONUS

        # --------------------------------------
        # Speed bonus
        # --------------------------------------

        speed_bonus_xp = 0
        speed_bonus_credits = 0

        if served_quickly:

            speed_bonus_xp = self.SPEED_XP_BONUS
            speed_bonus_credits = self.SPEED_CREDITS_BONUS

        # --------------------------------------
        # Total reward
        # --------------------------------------

        total_xp = (
            base_xp
            + combo_bonus_xp
            + speed_bonus_xp
        )

        total_credits = (
            base_credits
            + combo_bonus_credits
            + speed_bonus_credits
        )

        # --------------------------------------
        # Store lifetime credits
        # --------------------------------------

        self.total_credits_earned += total_credits

        return RewardResult(
            base_xp=base_xp,
            base_credits=base_credits,

            combo_bonus_xp=combo_bonus_xp,
            combo_bonus_credits=combo_bonus_credits,

            speed_bonus_xp=speed_bonus_xp,
            speed_bonus_credits=speed_bonus_credits,

            total_xp=total_xp,
            total_credits=total_credits,

            combo_count=combo_count
        )

    # ==========================================
    # CURRENT COMBO
    # ==========================================

    def get_combo(self):
        """
        Returns the current combo count.
        """

        return self.combo

    # ==========================================
    # TOTAL CREDITS
    # ==========================================

    def get_total_credits(self):
        """
        Returns the total credits earned
        during the current session.
        """

        return self.total_credits_earned

    # ==========================================
    # RESET
    # ==========================================

    def reset(self):
        """
        Reset rewards for a new game.
        """

        self.combo = 0
        self.total_credits_earned = 0
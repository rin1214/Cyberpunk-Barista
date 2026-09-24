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
    • Combo rewards (1 bar of XP added at combo milestones 2, 4, 6...)
    • Speed rewards
    • XP earned
    • Credits earned/lost
"""

from dataclasses import dataclass


# ============================================================
# REWARD RESULT
# ============================================================

@dataclass
class RewardResult:

    base_xp: int
    base_credits: int

    combo_bonus_xp: int
    combo_bonus_credits: int

    speed_bonus_xp: int
    speed_bonus_credits: int

    xp_penalty: int
    credit_penalty: int

    total_xp: int
    net_credits: int

    combo_count: int

    @property
    def is_positive(self):
        return (self.total_xp > 0 or self.net_credits > 0)

    @property
    def accuracy_text(self):
        return ""


# ============================================================
# REWARD SYSTEM
# ============================================================

class RewardSystem:

    BASE_REWARDS = {
        4: (40, 30),
        3: (0, 0),
        2: (0, 0),
        1: (0, 0),
        0: (0, 0),
    }

    LEVEL_XP_TARGETS = {
        1: 500,
        2: 1200,
        3: 2500,
    }

    MISTAKE_XP_PENALTY = 10
    MISTAKE_CREDIT_PENALTY = 10

    COMBO_CREDITS_BONUS = 3

    SPEED_XP_BONUS = 10
    SPEED_CREDITS_BONUS = 5

    def __init__(self):
        self.combo = 0
        self.total_credits_earned = 0
        self.total_xp_earned = 0
        self.total_credit_penalties = 0

    def get_base_reward(self, correct_count):
        try:
            correct_count = int(correct_count)
        except (TypeError, ValueError):
            correct_count = 0

        correct_count = max(0, min(correct_count, 4))
        return self.BASE_REWARDS.get(correct_count, (0, 0))

    def get_mistake_xp_penalty(self, correct_count):
        try:
            correct_count = int(correct_count)
        except (TypeError, ValueError):
            correct_count = 0

        if correct_count == 4:
            return 0
        return self.MISTAKE_XP_PENALTY

    def get_mistake_penalty(self, correct_count):
        try:
            correct_count = int(correct_count)
        except (TypeError, ValueError):
            correct_count = 0

        if correct_count == 4:
            return 0
        return self.MISTAKE_CREDIT_PENALTY

    def update_combo(self, correct_count):
        if int(correct_count) == 4:
            self.combo += 1
        else:
            self.combo = 0
        return self.combo

    def calculate_reward(self, accuracy_result, served_quickly=False, level=1):
        try:
            correct_count = int(accuracy_result.correct_count)
        except (AttributeError, TypeError, ValueError):
            correct_count = 0

        correct_count = max(0, min(correct_count, 4))

        base_xp, base_credits = self.get_base_reward(correct_count)
        combo_count = self.update_combo(correct_count)

        # ====================================================
        # COMBO BONUS (Add 1 bar of XP whenever combo hitting 2, 4, 6...)
        # ====================================================

        combo_bonus_xp = 0
        combo_bonus_credits = 0

        if combo_count >= 2:
            target_xp = self.LEVEL_XP_TARGETS.get(int(level), 500)
            xp_per_bar = target_xp // 10

            # When combo reaches every even milestone (2, 4, 6...), grant +1 bar of XP for that order
            if combo_count % 2 == 0:
                combo_bonus_xp = xp_per_bar

            combo_bonus_credits = (combo_count - 1) * self.COMBO_CREDITS_BONUS

        # ====================================================
        # SPEED BONUS
        # ====================================================

        speed_bonus_xp = 0
        speed_bonus_credits = 0

        if served_quickly and correct_count == 4:
            speed_bonus_xp = self.SPEED_XP_BONUS
            speed_bonus_credits = self.SPEED_CREDITS_BONUS

        # ====================================================
        # MISTAKE PENALTIES
        # ====================================================

        credit_penalty = self.get_mistake_penalty(correct_count)
        xp_penalty = self.get_mistake_xp_penalty(correct_count)

        # ====================================================
        # FINAL XP & CREDITS
        # ====================================================

        if correct_count == 4:
            total_xp = base_xp + combo_bonus_xp + speed_bonus_xp
            net_credits = base_credits + combo_bonus_credits + speed_bonus_credits
        else:
            total_xp = -xp_penalty
            net_credits = -credit_penalty

        if total_xp > 0:
            self.total_xp_earned += total_xp

        if net_credits > 0:
            self.total_credits_earned += net_credits

        self.total_credit_penalties += credit_penalty

        return RewardResult(
            base_xp=base_xp,
            base_credits=base_credits,
            combo_bonus_xp=combo_bonus_xp,
            combo_bonus_credits=combo_bonus_credits,
            speed_bonus_xp=speed_bonus_xp,
            speed_bonus_credits=speed_bonus_credits,
            xp_penalty=xp_penalty,
            credit_penalty=credit_penalty,
            total_xp=total_xp,
            net_credits=net_credits,
            combo_count=combo_count,
        )

    def get_combo(self):
        return self.combo

    def get_total_xp(self):
        return self.total_xp_earned

    def get_total_credits(self):
        return self.total_credits_earned

    def get_total_credit_penalties(self):
        return self.total_credit_penalties

    def get_data(self):
        return {
            "combo": self.combo,
            "total_xp_earned": self.total_xp_earned,
            "total_credits_earned": self.total_credits_earned,
            "total_credit_penalties": self.total_credit_penalties,
        }

    def reset(self):
        self.combo = 0
        self.total_credits_earned = 0
        self.total_xp_earned = 0
        self.total_credit_penalties = 0
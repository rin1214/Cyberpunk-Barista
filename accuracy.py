from dataclasses import dataclass


# ============================================================
# ACCURACY RESULT
# ============================================================

@dataclass
class AccuracyResult:

    # --------------------------------------------------------
    # INDIVIDUAL CHECKS
    # --------------------------------------------------------

    drink_correct: bool

    temperature_correct: bool

    caffeine_correct: bool

    sweetness_correct: bool

    # ========================================================
    # CORRECT COUNT
    # ========================================================

    @property
    def correct_count(self):


        return sum(
            [
                self.drink_correct,
                self.temperature_correct,
                self.caffeine_correct,
                self.sweetness_correct,
            ]
        )

    # ========================================================
    # TOTAL COUNT
    # ========================================================

    @property
    def total_count(self):
        """
        There are always four requirements.
        """

        return 4

    # ========================================================
    # PERCENTAGE
    # ========================================================

    @property
    def percentage(self):
        """
        Converts the accuracy result into
        a percentage.

        Example:

            3 / 4

            = 75%
        """

        return (
            self.correct_count
            / self.total_count
        ) * 100

    # ========================================================
    # PERFECT ORDER
    # ========================================================

    @property
    def is_perfect(self):
        """
        Returns True only when all four requirements
        are correct.
        """

        return (
            self.correct_count
            == self.total_count
        )

    # ========================================================
    # HAS MISTAKE
    # ========================================================

    @property
    def has_mistake(self):
        """
        Returns True if at least one requirement
        is incorrect.
        """

        return not self.is_perfect

    # ========================================================
    # SUMMARY
    # ========================================================

    def get_summary(self):
        """
        Returns a readable accuracy summary.

        Example:

            3/4 correct (75%)
        """

        return (
            f"{self.correct_count}/"
            f"{self.total_count} "
            f"correct "
            f"({self.percentage:.0f}%)"
        )

    # ========================================================
    # INDIVIDUAL RESULTS
    # ========================================================

    def get_results(self):
        """
        Returns all four accuracy checks as a dictionary.

        Useful for displaying which parts of the order
        were correct or incorrect.
        """

        return {

            "drink":
                self.drink_correct,

            "temperature":
                self.temperature_correct,

            "caffeine":
                self.caffeine_correct,

            "sweetness":
                self.sweetness_correct,
        }


# ============================================================
# ORDER ACCURACY
# ============================================================

class OrderAccuracy:
    """
    Compares the customer's requested order with
    the player's completed drink.
    """

    # ========================================================
    # CHECK ORDER
    # ========================================================

    @staticmethod
    def check_order(
        customer_order,
        player_drink,
    ):
        """
        Compare all four requirements.

        Customer:

            customer_order.drink
            customer_order.temperature
            customer_order.caffeine
            customer_order.sweetness

        Player:

            player_drink["drink"]
            player_drink["temperature"]
            player_drink["caffeine"]
            player_drink["sweetness"]

        Returns:

            AccuracyResult
        """

        # ====================================================
        # SAFETY CHECK
        # ====================================================

        if customer_order is None:

            return AccuracyResult(
                drink_correct=False,
                temperature_correct=False,
                caffeine_correct=False,
                sweetness_correct=False,
            )

        if player_drink is None:

            return AccuracyResult(
                drink_correct=False,
                temperature_correct=False,
                caffeine_correct=False,
                sweetness_correct=False,
            )

        # ====================================================
        # DRINK
        # ====================================================

        drink_correct = (

            customer_order.drink

            ==

            player_drink.get(
                "drink"
            )

        )

        # ====================================================
        # TEMPERATURE
        # ====================================================

        temperature_correct = (

            customer_order.temperature

            ==

            player_drink.get(
                "temperature"
            )

        )

        # ====================================================
        # CAFFEINE
        # ========================================================

        caffeine_correct = (

            customer_order.caffeine

            ==

            player_drink.get(
                "caffeine"
            )

        )

        # ====================================================
        # SWEETNESS
        # ========================================================

        sweetness_correct = (

            customer_order.sweetness

            ==

            player_drink.get(
                "sweetness"
            )

        )

        # ====================================================
        # RETURN RESULT
        # ========================================================

        return AccuracyResult(

            drink_correct=
                drink_correct,

            temperature_correct=
                temperature_correct,

            caffeine_correct=
                caffeine_correct,

            sweetness_correct=
                sweetness_correct,
        )

    # ========================================================
    # ALIAS
    # ========================================================

    @staticmethod
    def compare_order(
        customer_order,
        player_drink,
    ):


        return OrderAccuracy.check_order(
            customer_order,
            player_drink,
        )
    
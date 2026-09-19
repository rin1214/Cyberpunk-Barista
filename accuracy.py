from dataclasses import dataclass


@dataclass
class AccuracyResult:
    """
    Stores the result of checking a player's drink
    against the customer's order.
    """

    drink_correct: bool
    temperature_correct: bool
    caffeine_correct: bool
    sweetness_correct: bool

    @property
    def correct_count(self):
        """
        Returns how many of the 4 requirements
        were correct.
        """

        return sum([
            self.drink_correct,
            self.temperature_correct,
            self.caffeine_correct,
            self.sweetness_correct
        ])

    @property
    def total_count(self):
        """
        There are always 4 things to check.
        """

        return 4

    @property
    def percentage(self):
        """
        Converts the accuracy into a percentage.
        """

        return (self.correct_count / self.total_count) * 100

    @property
    def is_perfect(self):
        """
        Returns True when all 4 requirements
        are correct.
        """

        return self.correct_count == self.total_count

    def get_summary(self):
        """
        Returns a simple text summary.
        """

        return (
            f"{self.correct_count}/{self.total_count} "
            f"correct ({self.percentage:.0f}%)"
        )


class OrderAccuracy:
    """
    Compares a customer's order with
    the player's completed drink.
    """

    @staticmethod
    def check_order(customer_order, player_drink):
        """
        Compare the customer's order and
        the player's drink.

        Returns an AccuracyResult.
        """

        drink_correct = (
            customer_order.drink
            == player_drink.get("drink")
        )

        temperature_correct = (
            customer_order.temperature
            == player_drink.get("temperature")
        )

        caffeine_correct = (
            customer_order.caffeine
            == player_drink.get("caffeine")
        )

        sweetness_correct = (
            customer_order.sweetness
            == player_drink.get("sweetness")
        )

        return AccuracyResult(
            drink_correct=drink_correct,
            temperature_correct=temperature_correct,
            caffeine_correct=caffeine_correct,
            sweetness_correct=sweetness_correct
        ) 



   
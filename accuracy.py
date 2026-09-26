from dataclasses import dataclass


@dataclass(frozen=True)
class AccuracyResult:
    drink_correct: bool
    temperature_correct: bool
    caffeine_correct: bool
    sweetness_correct: bool

    @property
    def correct_count(self):
        return sum(self.get_results().values())

    @property
    def total_count(self):
        return 4

    @property
    def percentage(self):
        return self.correct_count / self.total_count * 100

    @property
    def is_perfect(self):
        return self.correct_count == self.total_count

    @property
    def has_mistake(self):
        return not self.is_perfect

    def get_summary(self):
        return f"{self.correct_count}/{self.total_count} correct ({self.percentage:.0f}%)"

    def get_results(self):
        return {name: getattr(self, f"{name}_correct") for name in (
            "drink", "temperature", "caffeine", "sweetness"
        )}


class OrderAccuracy:
    FIELDS = ("drink", "temperature", "caffeine", "sweetness")

    @staticmethod
    def check_order(customer_order, player_drink):
        player_drink = player_drink or {}
        return AccuracyResult(*(
            customer_order is not None
            and getattr(customer_order, field, None) == player_drink.get(field)
            for field in OrderAccuracy.FIELDS
        ))

    compare_order = check_order
    
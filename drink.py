class Drink:
    """
    Represent three adjustable parameters:
    - Sweetness
    - Caffeine
    - Temperature

    All values are kept between MIN_VALUE and MAX_VALUE.
    """

    MIN_VALUE = 0
    MAX_VALUE = 100
    DEFAULT_VALUE = 50
    ADJUSTMENT_AMOUNT = 10

    def __init__(self):
        """Create a new drink with default values."""

        self.sweetness = self.DEFAULT_VALUE
        self.caffeine = self.DEFAULT_VALUE
        self.temperature = self.DEFAULT_VALUE

    # --------------------------------------------------
    # SWEETNESS CONTROLS
    # --------------------------------------------------

    def increase_sweetness(self):
        """Increase sweetness without going above the maximum."""

        self.sweetness = min(
            self.MAX_VALUE,
            self.sweetness + self.ADJUSTMENT_AMOUNT
        )

    def decrease_sweetness(self):
        """Decrease sweetness without going below the minimum."""

        self.sweetness = max(
            self.MIN_VALUE,
            self.sweetness - self.ADJUSTMENT_AMOUNT
        )

    # --------------------------------------------------
    # CAFFEINE CONTROLS
    # --------------------------------------------------

    def increase_caffeine(self):
        """Increase caffeine without going above the maximum."""

        self.caffeine = min(
            self.MAX_VALUE,
            self.caffeine + self.ADJUSTMENT_AMOUNT
        )

    def decrease_caffeine(self):
        """Decrease caffeine without going below the minimum."""

        self.caffeine = max(
            self.MIN_VALUE,
            self.caffeine - self.ADJUSTMENT_AMOUNT
        )

    # --------------------------------------------------
    # TEMPERATURE CONTROLS
    # --------------------------------------------------

    def increase_temperature(self):
        """Increase temperature without going above the maximum."""

        self.temperature = min(
            self.MAX_VALUE,
            self.temperature + self.ADJUSTMENT_AMOUNT
        )

    def decrease_temperature(self):
        """Decrease temperature without going below the minimum."""

        self.temperature = max(
            self.MIN_VALUE,
            self.temperature - self.ADJUSTMENT_AMOUNT
        )

    # --------------------------------------------------
    # DRINK MANAGEMENT
    # --------------------------------------------------

    def reset(self):
        """
        Reset the drink back to its default values.

        This will be used after a customer has been served.
        """

        self.sweetness = self.DEFAULT_VALUE
        self.caffeine = self.DEFAULT_VALUE
        self.temperature = self.DEFAULT_VALUE

    def get_data(self):
        """
        Return the current drink data as a dictionary.

        This data can be sent to the evaluation system.
        """

        return {
            "sweetness": self.sweetness,
            "caffeine": self.caffeine,
            "temperature": self.temperature
        }

    def __str__(self):
        """
        Return a readable text version of the drink.
        Useful for testing and debugging.
        """

        return (
            f"Drink("
            f"Sweetness={self.sweetness}, "
            f"Caffeine={self.caffeine}, "
            f"Temperature={self.temperature}"
            f")"
        )
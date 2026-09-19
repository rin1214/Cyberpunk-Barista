from dataclasses import dataclass
from typing import Optional


# ============================================================
# CYBERPUNK CAFÉ - DRINK SYSTEM
# ============================================================
#
# This file contains the game's drink information.
#
# We have:
#   9 official drinks
#   3 temperature choices
#   3 caffeine choices
#   3 sweetness choices
#
# Therefore:
#
#   3 x 3 x 3 = 27 combinations per drink
#
#   9 x 27 = 243 possible drink/order combinations
#
# ============================================================


# ============================================================
# 1. CUSTOMISATION OPTIONS
# ============================================================

TEMPERATURE_OPTIONS = (
    "Cold",
    "Normal",
    "Hot",
)

CAFFEINE_OPTIONS = (
    "Low",
    "Normal",
    "High",
)

SWEETNESS_OPTIONS = (
    "Less",
    "Normal",
    "Extra",
)


# ============================================================
# 2. DRINK RECIPE
# ============================================================

@dataclass(frozen=True)
class DrinkRecipe:
    """
    Stores the permanent information about one drink.

    A recipe describes WHAT the drink is.

    It does not describe what a particular customer ordered.
    """

    name: str
    unlock_level: int
    toppings: tuple[str, ...]
    liquid_color: tuple[int, int, int]

    def is_unlocked(self, current_level: int) -> bool:
        """
        Returns True if the player has unlocked this drink.
        """

        return current_level >= self.unlock_level


# ============================================================
# 3. PLAYER-MADE DRINK
# ============================================================

@dataclass
class PlayerDrink:
    """
    Stores the drink currently being made by the player.

    This describes WHAT the player selected.
    """

    drink_name: Optional[str] = None
    temperature: Optional[str] = None
    caffeine: Optional[str] = None
    sweetness: Optional[str] = None

    def has_drink(self) -> bool:
        """Returns True if the player selected a drink."""

        return self.drink_name is not None

    def has_temperature(self) -> bool:
        """Returns True if temperature was selected."""

        return self.temperature is not None

    def has_caffeine(self) -> bool:
        """Returns True if caffeine was selected."""

        return self.caffeine is not None

    def has_sweetness(self) -> bool:
        """Returns True if sweetness was selected."""

        return self.sweetness is not None

    def is_fully_customised(self) -> bool:
        """
        Returns True only when all four required
        drink choices have been made.
        """

        return (
            self.has_drink()
            and self.has_temperature()
            and self.has_caffeine()
            and self.has_sweetness()
        )

    def reset(self) -> None:
        """Clear the player's current drink."""

        self.drink_name = None
        self.temperature = None
        self.caffeine = None
        self.sweetness = None

    def get_data(self) -> dict:
        """
        Return the player's drink as a dictionary.

        This will later be used by the accuracy system.
        """

        return {
            "drink": self.drink_name,
            "temperature": self.temperature,
            "caffeine": self.caffeine,
            "sweetness": self.sweetness,
        }


# ============================================================
# 4. OFFICIAL CYBERPUNK CAFÉ DRINKS
# ============================================================

DRINK_RECIPES = {

    # --------------------------------------------------------
    # LEVEL 1
    # --------------------------------------------------------

    "Neon Latte": DrinkRecipe(
        name="Neon Latte",
        unlock_level=1,
        toppings=("whipped_cream",),
        liquid_color=(255, 170, 220),
    ),

    "Galaxy Mocha": DrinkRecipe(
        name="Galaxy Mocha",
        unlock_level=1,
        toppings=("whipped_cream", "chocolate_bits"),
        liquid_color=(95, 65, 130),
    ),

    "Void Chai": DrinkRecipe(
        name="Void Chai",
        unlock_level=1,
        toppings=("whipped_cream",),
        liquid_color=(255, 190, 130),
    ),

    # --------------------------------------------------------
    # LEVEL 2
    # --------------------------------------------------------

    "Cyber Fuel": DrinkRecipe(
        name="Cyber Fuel",
        unlock_level=2,
        toppings=(),
        liquid_color=(155, 220, 255),
    ),

    "Hologram Frappe": DrinkRecipe(
        name="Hologram Frappe",
        unlock_level=2,
        toppings=("whipped_cream",),
        liquid_color=(210, 180, 255),
    ),

    "Caramel Byte": DrinkRecipe(
        name="Caramel Byte",
        unlock_level=2,
        toppings=("whipped_cream", "caramel_crunch"),
        liquid_color=(220, 165, 95),
    ),

    # --------------------------------------------------------
    # LEVEL 3
    # --------------------------------------------------------

    "Pixel Lemint": DrinkRecipe(
        name="Pixel Lemint",
        unlock_level=3,
        toppings=("mint_leaves",),
        liquid_color=(255, 225, 90),
    ),

    "Stardust Matcha": DrinkRecipe(
        name="Stardust Matcha",
        unlock_level=3,
        toppings=("yellow_stardust",),
        liquid_color=(150, 205, 125),
    ),

    "Meteorite": DrinkRecipe(
        name="Meteorite",
        unlock_level=3,
        toppings=("meteorite_crumbs",),
        liquid_color=(235, 245, 255),
    ),
}


# ============================================================
# 5. DRINK MENU ORDER
# ============================================================

DRINK_MENU = (
    "Neon Latte",
    "Galaxy Mocha",
    "Void Chai",
    "Cyber Fuel",
    "Hologram Frappe",
    "Caramel Byte",
    "Pixel Lemint",
    "Stardust Matcha",
    "Meteorite",
)


# ============================================================
# 6. DRINK SYSTEM HELPER FUNCTIONS
# ============================================================

def get_recipe(drink_name: str) -> Optional[DrinkRecipe]:
    """
    Find a recipe by drink name.

    Returns:
        DrinkRecipe if the drink exists.
        None if it does not exist.
    """

    return DRINK_RECIPES.get(drink_name)


def is_valid_drink(drink_name: str) -> bool:
    """
    Check whether a drink name exists in our official menu.
    """

    return drink_name in DRINK_RECIPES


def is_drink_unlocked(drink_name: str, current_level: int) -> bool:
    """
    Check whether a particular drink is unlocked.
    """

    recipe = get_recipe(drink_name)

    if recipe is None:
        return False

    return recipe.is_unlocked(current_level)


def get_unlocked_drinks(current_level: int) -> list[str]:
    """
    Return all drinks available at the current level.
    """

    return [
        drink_name
        for drink_name in DRINK_MENU
        if is_drink_unlocked(drink_name, current_level)
    ]


def get_locked_drinks(current_level: int) -> list[str]:
    """
    Return all drinks that are still locked.
    """

    return [
        drink_name
        for drink_name in DRINK_MENU
        if not is_drink_unlocked(drink_name, current_level)
    ]


def is_valid_temperature(value: str) -> bool:
    """Check whether a temperature selection is valid."""

    return value in TEMPERATURE_OPTIONS


def is_valid_caffeine(value: str) -> bool:
    """Check whether a caffeine selection is valid."""

    return value in CAFFEINE_OPTIONS


def is_valid_sweetness(value: str) -> bool:
    """Check whether a sweetness selection is valid."""

    return value in SWEETNESS_OPTIONS


# ============================================================
# 7. BACKWARD COMPATIBILITY
# ============================================================
#
# The current station.py still uses the old numeric Drink class.
#
# We are temporarily keeping this class so the game does not
# immediately break while we migrate the Mixing Station.
#
# THIS CLASS WILL EVENTUALLY BE REMOVED.
#
# Do not build new gameplay features using this class.
#


class Drink:
    """
    Temporary compatibility class for the OLD Mixing Station.

    OLD SYSTEM:
        sweetness = 0-100
        caffeine = 0-100
        temperature = 0-100

    NEW SYSTEM:
        drink name
        temperature choice
        caffeine choice
        sweetness choice

    This class exists only during our transition.
    """

    MIN_VALUE = 0
    MAX_VALUE = 100
    DEFAULT_VALUE = 50
    ADJUSTMENT_AMOUNT = 10

    def __init__(self):
        """Create a legacy drink."""

        self.sweetness = self.DEFAULT_VALUE
        self.caffeine = self.DEFAULT_VALUE
        self.temperature = self.DEFAULT_VALUE

    # --------------------------------------------------------
    # OLD SWEETNESS CONTROLS
    # --------------------------------------------------------

    def increase_sweetness(self):
        self.sweetness = min(
            self.MAX_VALUE,
            self.sweetness + self.ADJUSTMENT_AMOUNT
        )

    def decrease_sweetness(self):
        self.sweetness = max(
            self.MIN_VALUE,
            self.sweetness - self.ADJUSTMENT_AMOUNT
        )

    # --------------------------------------------------------
    # OLD CAFFEINE CONTROLS
    # --------------------------------------------------------

    def increase_caffeine(self):
        self.caffeine = min(
            self.MAX_VALUE,
            self.caffeine + self.ADJUSTMENT_AMOUNT
        )

    def decrease_caffeine(self):
        self.caffeine = max(
            self.MIN_VALUE,
            self.caffeine - self.ADJUSTMENT_AMOUNT
        )

    # --------------------------------------------------------
    # OLD TEMPERATURE CONTROLS
    # --------------------------------------------------------

    def increase_temperature(self):
        self.temperature = min(
            self.MAX_VALUE,
            self.temperature + self.ADJUSTMENT_AMOUNT
        )

    def decrease_temperature(self):
        self.temperature = max(
            self.MIN_VALUE,
            self.temperature - self.ADJUSTMENT_AMOUNT
        )

    # --------------------------------------------------------
    # OLD RESET
    # --------------------------------------------------------

    def reset(self):
        """Reset the old numeric values."""

        self.sweetness = self.DEFAULT_VALUE
        self.caffeine = self.DEFAULT_VALUE
        self.temperature = self.DEFAULT_VALUE

    # --------------------------------------------------------
    # OLD DATA FORMAT
    # --------------------------------------------------------

    def get_data(self):
        """
        Temporary old data format.

        This will later be replaced by PlayerDrink.get_data().
        """

        return {
            "sweetness": self.sweetness,
            "caffeine": self.caffeine,
            "temperature": self.temperature
        }

    def __str__(self):
        return (
            f"LegacyDrink("
            f"Sweetness={self.sweetness}, "
            f"Caffeine={self.caffeine}, "
            f"Temperature={self.temperature}"
            f")"
        )
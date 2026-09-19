from dataclasses import dataclass


# ============================================================
# PLAYER CUSTOMISATION OPTIONS
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
# DRINK RECIPE
# ============================================================

@dataclass(frozen=True)
class DrinkRecipe:
    """
    Stores the permanent information about one drink.

    A DrinkRecipe describes what the drink IS.

    It does not describe what the player is currently making.
    """

    name: str
    unlock_level: int
    toppings: tuple
    liquid_color: tuple

    def is_unlocked(self, level):
        """
        Returns True if this drink is unlocked
        at the given player level.
        """

        return level >= self.unlock_level


# ============================================================
# PLAYER DRINK
# ============================================================

@dataclass
class PlayerDrink:
    """
    Stores the drink currently being made by the player.

    Example:

        drink_name = "Milkyway"
        temperature = "Hot"
        caffeine = "High"
        sweetness = "Extra"
    """

    drink_name: str = None
    temperature: str = None
    caffeine: str = None
    sweetness: str = None

    # --------------------------------------------------------
    # CHECK DRINK
    # --------------------------------------------------------

    def has_drink(self):
        """
        Returns True if a drink has been selected.
        """

        return self.drink_name is not None

    # --------------------------------------------------------
    # CHECK TEMPERATURE
    # --------------------------------------------------------

    def has_temperature(self):
        """
        Returns True if temperature has been selected.
        """

        return self.temperature is not None

    # --------------------------------------------------------
    # CHECK CAFFEINE
    # --------------------------------------------------------

    def has_caffeine(self):
        """
        Returns True if caffeine has been selected.
        """

        return self.caffeine is not None

    # --------------------------------------------------------
    # CHECK SWEETNESS
    # --------------------------------------------------------

    def has_sweetness(self):
        """
        Returns True if sweetness has been selected.
        """

        return self.sweetness is not None

    # --------------------------------------------------------
    # CHECK COMPLETE CUSTOMISATION
    # --------------------------------------------------------

    def is_fully_customised(self):
        """
        Returns True when all four required choices
        have been selected.
        """

        return (
            self.has_drink()
            and self.has_temperature()
            and self.has_caffeine()
            and self.has_sweetness()
        )

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    def reset(self):
        """
        Clears the player's current drink.
        """

        self.drink_name = None
        self.temperature = None
        self.caffeine = None
        self.sweetness = None

    # --------------------------------------------------------
    # GET DATA
    # --------------------------------------------------------

    def get_data(self):
        """
        Returns the player's drink information
        as a dictionary.

        This dictionary will later be passed
        to the accuracy system.
        """

        return {
            "drink": self.drink_name,
            "temperature": self.temperature,
            "caffeine": self.caffeine,
            "sweetness": self.sweetness,
        }


# ============================================================
# OFFICIAL CYBERPUNK CAFÉ DRINK RECIPES
# ============================================================

DRINK_RECIPES = {

    # --------------------------------------------------------
    # LEVEL 1
    # --------------------------------------------------------

    "Neon Latte": DrinkRecipe(
        name="Neon Latte",
        unlock_level=1,

        toppings=(
            "whipped_cream",
        ),

        liquid_color=(
            255,
            150,
            210,
        ),
    ),

    "Milkyway": DrinkRecipe(
        name="Milkyway",
        unlock_level=1,

        toppings=(
            "whipped_cream",
            "chocolate_bits",
        ),

        liquid_color=(
            105,
            75,
            145,
        ),
    ),

    "Void Chai": DrinkRecipe(
        name="Void Chai",
        unlock_level=1,

        toppings=(
            "whipped_cream",
        ),

        liquid_color=(
            255,
            190,
            135,
        ),
    ),

    # --------------------------------------------------------
    # LEVEL 2
    # --------------------------------------------------------

    "Cyber Fuel": DrinkRecipe(
        name="Cyber Fuel",
        unlock_level=2,

        toppings=(),

        liquid_color=(
            155,
            220,
            255,
        ),
    ),

    "Hologram Frappe": DrinkRecipe(
        name="Hologram Frappe",
        unlock_level=2,

        toppings=(
            "whipped_cream",
        ),

        liquid_color=(
            190,
            170,
            255,
        ),
    ),

    "Pixel Lemint": DrinkRecipe(
        name="Pixel Lemint",
        unlock_level=2,

        toppings=(
            "mint_leaves",
        ),

        liquid_color=(
            255,
            225,
            95,
        ),
    ),

    # --------------------------------------------------------
    # LEVEL 3
    # --------------------------------------------------------

    "Caramel Byte": DrinkRecipe(
        name="Caramel Byte",
        unlock_level=3,

        toppings=(
            "whipped_cream",
            "caramel_crunch",
        ),

        liquid_color=(
            205,
            135,
            70,
        ),
    ),

    "Stardust Matcha": DrinkRecipe(
        name="Stardust Matcha",
        unlock_level=3,

        toppings=(
            "yellow_stardust",
        ),

        liquid_color=(
            165,
            195,
            105,
        ),
    ),

    "Meteorite": DrinkRecipe(
        name="Meteorite",
        unlock_level=3,

        toppings=(
            "meteorite_crumbs",
        ),

        liquid_color=(
            235,
            245,
            255,
        ),
    ),
}


# ============================================================
# OFFICIAL MENU ORDER
# ============================================================

DRINK_MENU = (
    "Neon Latte",
    "Milkyway",
    "Void Chai",
    "Cyber Fuel",
    "Hologram Frappe",
    "Pixel Lemint",
    "Caramel Byte",
    "Stardust Matcha",
    "Meteorite",
)


# ============================================================
# RECIPE LOOKUP
# ============================================================

def get_recipe(drink_name):
    """
    Return the recipe for a drink.

    Returns None if the drink does not exist.
    """

    return DRINK_RECIPES.get(drink_name)


# ============================================================
# VALID DRINK CHECK
# ============================================================

def is_valid_drink(drink_name):
    """
    Returns True if the drink exists in the
    official Cyberpunk Café menu.
    """

    return drink_name in DRINK_RECIPES


# ============================================================
# UNLOCK CHECK
# ============================================================

def is_drink_unlocked(drink_name, level):
    """
    Returns True if the specified drink is unlocked
    at the player's current level.
    """

    recipe = get_recipe(drink_name)

    if recipe is None:
        return False

    return recipe.is_unlocked(level)


# ============================================================
# GET UNLOCKED DRINKS
# ============================================================

def get_unlocked_drinks(level):
    """
    Returns a list of all drinks unlocked at
    the player's current level.
    """

    return [
        drink_name
        for drink_name in DRINK_MENU
        if is_drink_unlocked(drink_name, level)
    ]


# ============================================================
# GET LOCKED DRINKS
# ============================================================

def get_locked_drinks(level):
    """
    Returns a list of drinks that are still locked
    at the player's current level.
    """

    return [
        drink_name
        for drink_name in DRINK_MENU
        if not is_drink_unlocked(drink_name, level)
    ]


# ============================================================
# GET ALL DRINKS
# ============================================================

def get_all_drinks():
    """
    Returns all 9 official drinks in menu order.
    """

    return list(DRINK_MENU)


# ============================================================
# VALID TEMPERATURE
# ============================================================

def is_valid_temperature(temperature):
    """
    Checks whether a temperature choice is valid.
    """

    return temperature in TEMPERATURE_OPTIONS


# ============================================================
# VALID CAFFEINE
# ============================================================

def is_valid_caffeine(caffeine):
    """
    Checks whether a caffeine choice is valid.
    """

    return caffeine in CAFFEINE_OPTIONS


# ============================================================
# VALID SWEETNESS
# ============================================================

def is_valid_sweetness(sweetness):
    """
    Checks whether a sweetness choice is valid.
    """

    return sweetness in SWEETNESS_OPTIONS


# ============================================================
# VALID PLAYER DRINK
# ============================================================

def validate_player_drink(player_drink):
    """
    Checks whether a PlayerDrink contains valid
    drink and customisation choices.

    Returns True when everything is valid.
    """

    if not isinstance(player_drink, PlayerDrink):
        return False

    if not is_valid_drink(player_drink.drink_name):
        return False

    if not is_valid_temperature(player_drink.temperature):
        return False

    if not is_valid_caffeine(player_drink.caffeine):
        return False

    if not is_valid_sweetness(player_drink.sweetness):
        return False

    return True


# ============================================================
# LEGACY DRINK CLASS
# ============================================================
#
# This class temporarily exists so the current station.py
# and other older parts of the project can continue running.
#
# The NEW system above uses:
#
#     PlayerDrink
#
# The older system uses:
#
#     Drink
#
# Once station.py has been fully converted to the new
# system, this legacy class can be removed.
# ============================================================

class Drink:
    """
    Temporary backwards-compatible Drink class.

    This keeps the current older mixing station working
    while we transition to the new data-driven system.
    """

    def __init__(self):
        # Old numerical values used by the previous
        # mixing station.
        self.sweetness = 50
        self.caffeine = 50
        self.temperature = 50

    # --------------------------------------------------------
    # SWEETNESS
    # --------------------------------------------------------

    def increase_sweetness(self):
        """
        Increase sweetness by 10.
        """

        self.sweetness = min(
            100,
            self.sweetness + 10
        )

    def decrease_sweetness(self):
        """
        Decrease sweetness by 10.
        """

        self.sweetness = max(
            0,
            self.sweetness - 10
        )

    # --------------------------------------------------------
    # CAFFEINE
    # --------------------------------------------------------

    def increase_caffeine(self):
        """
        Increase caffeine by 10.
        """

        self.caffeine = min(
            100,
            self.caffeine + 10
        )

    def decrease_caffeine(self):
        """
        Decrease caffeine by 10.
        """

        self.caffeine = max(
            0,
            self.caffeine - 10
        )

    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    def increase_temperature(self):
        """
        Increase temperature by 10.
        """

        self.temperature = min(
            100,
            self.temperature + 10
        )

    def decrease_temperature(self):
        """
        Decrease temperature by 10.
        """

        self.temperature = max(
            0,
            self.temperature - 10
        )

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    def reset(self):
        """
        Reset the old numerical drink values.
        """

        self.sweetness = 50
        self.caffeine = 50
        self.temperature = 50

    # --------------------------------------------------------
    # GET OLD DATA
    # --------------------------------------------------------

    def get_data(self):
        """
        Returns the old numerical drink format.

        This is temporary compatibility for the existing
        station/main system.

        The new accuracy system will eventually use
        PlayerDrink data instead.
        """

        return {
            "sweetness": self.sweetness,
            "caffeine": self.caffeine,
            "temperature": self.temperature,
        }


# ============================================================
# END OF DRINK.PY
# ============================================================
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
    name: str
    unlock_level: int
    toppings: tuple
    liquid_color: tuple

    def is_unlocked(self, level):
        try:
            return int(level) >= self.unlock_level
        except (TypeError, ValueError):
            return False


# ============================================================
# PLAYER DRINK
# ============================================================

@dataclass
class PlayerDrink:



    drink_name: str = None

    temperature: str = None

    caffeine: str = None

    sweetness: str = None

    # ========================================================
    # DRINK SELECTED?
    # ========================================================

    def has_drink(self):

        return self.drink_name is not None

    # ========================================================
    # TEMPERATURE SELECTED?
    # ========================================================

    def has_temperature(self):

        return (
            self.temperature
            is not None
        )

    # ========================================================
    # CAFFEINE SELECTED?
    # ========================================================

    def has_caffeine(self):

        return (
            self.caffeine
            is not None
        )

    # ========================================================
    # SWEETNESS SELECTED?
    # ========================================================

    def has_sweetness(self):

        return (
            self.sweetness
            is not None
        )

    # ========================================================
    # FULLY CUSTOMISED?
    # ========================================================

    def is_fully_customised(self):

        return (

            self.has_drink()

            and

            self.has_temperature()

            and

            self.has_caffeine()

            and

            self.has_sweetness()

        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.drink_name = None

        self.temperature = None

        self.caffeine = None

        self.sweetness = None

    # ========================================================
    # GET DATA
    # ========================================================

    def get_data(self):
        """
        Returns the completed drink as a dictionary.

        This is the format used by accuracy.py.
        """

        return {

            "drink":
                self.drink_name,

            "temperature":
                self.temperature,

            "caffeine":
                self.caffeine,

            "sweetness":
                self.sweetness,

        }


# ============================================================
# OFFICIAL CYBERPUNK CAFÉ RECIPES
# ============================================================

DRINK_RECIPES = {

    # ========================================================
    # LEVEL 1
    # ========================================================

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

    # ========================================================
    # LEVEL 2
    # ========================================================

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

    # ========================================================
    # LEVEL 3
    # ========================================================

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

def get_recipe(
    drink_name,
):
    """
    Returns the recipe for the specified drink.

    Returns None if the drink does not exist.
    """

    return DRINK_RECIPES.get(
        drink_name
    )


# ============================================================
# VALID DRINK
# ============================================================

def is_valid_drink(
    drink_name,
):

    return (
        drink_name
        in DRINK_RECIPES
    )


# ============================================================
# DRINK UNLOCK CHECK
# ============================================================

def is_drink_unlocked(
    drink_name,
    level,
):
    """
    Returns True when the drink is unlocked
    at the player's current level.
    """

    recipe = get_recipe(
        drink_name
    )

    if recipe is None:

        return False

    return recipe.is_unlocked(
        level
    )


# ============================================================
# GET UNLOCKED DRINKS
# ============================================================

def get_unlocked_drinks(
    level,
):
    """
    Returns all currently unlocked drinks
    in official menu order.
    """

    return [

        drink_name

        for drink_name
        in DRINK_MENU

        if is_drink_unlocked(
            drink_name,
            level,
        )

    ]


# ============================================================
# GET LOCKED DRINKS
# ============================================================

def get_locked_drinks(
    level,
):
    """
    Returns all drinks that are still locked.
    """

    return [

        drink_name

        for drink_name
        in DRINK_MENU

        if not is_drink_unlocked(
            drink_name,
            level,
        )

    ]


# ============================================================
# GET ALL DRINKS
# ============================================================

def get_all_drinks():

    return list(
        DRINK_MENU
    )


# ============================================================
# TEMPERATURE VALIDATION
# ============================================================

def is_valid_temperature(
    temperature,
):

    return (
        temperature
        in TEMPERATURE_OPTIONS
    )


# ============================================================
# CAFFEINE VALIDATION
# ============================================================

def is_valid_caffeine(
    caffeine,
):

    return (
        caffeine
        in CAFFEINE_OPTIONS
    )


# ============================================================
# SWEETNESS VALIDATION
# ============================================================

def is_valid_sweetness(
    sweetness,
):

    return (
        sweetness
        in SWEETNESS_OPTIONS
    )


# ============================================================
# PLAYER DRINK VALIDATION
# ============================================================

def validate_player_drink(
    player_drink,
):
    """
    Checks whether the player's current drink
    contains valid selections.

    IMPORTANT:

    This checks whether the values are VALID.

    It does NOT check whether the values MATCH
    the customer's order.

    Matching is handled by accuracy.py.
    """

    if not isinstance(
        player_drink,
        PlayerDrink,
    ):

        return False

    # --------------------------------------------------------
    # DRINK
    # --------------------------------------------------------

    if not is_valid_drink(
        player_drink.drink_name
    ):

        return False

    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    if not is_valid_temperature(
        player_drink.temperature
    ):

        return False

    # --------------------------------------------------------
    # CAFFEINE
    # --------------------------------------------------------

    if not is_valid_caffeine(
        player_drink.caffeine
    ):

        return False

    # --------------------------------------------------------
    # SWEETNESS
    # --------------------------------------------------------

    if not is_valid_sweetness(
        player_drink.sweetness
    ):

        return False

    return True


# ============================================================
# GET DRINK TOPPINGS
# ============================================================

def get_drink_toppings(
    drink_name,
):
    """
    Returns the toppings automatically associated
    with the selected drink.

    Example:

        Milkyway
        ↓
        ["whipped_cream", "chocolate_bits"]
    """

    recipe = get_recipe(
        drink_name
    )

    if recipe is None:

        return ()

    return recipe.toppings


# ============================================================
# GET DRINK COLOR
# ============================================================

def get_drink_color(
    drink_name,
):
    """
    Returns the liquid colour for a drink.
    """

    recipe = get_recipe(
        drink_name
    )

    if recipe is None:

        return (
            255,
            255,
            255,
        )

    return recipe.liquid_color


# ============================================================
# LEGACY DRINK CLASS
# ============================================================
#
# This remains temporarily because your existing
# collaborator code may still import:
#
#     from drink import Drink
#
# The NEW mixing station will eventually use PlayerDrink.
#
# ============================================================

class Drink:

    """
    Temporary backwards-compatible Drink class.

    Old station code uses numerical values from 0–100.

    New system uses:

        PlayerDrink
        ↓
        exact named options

    This class prevents older collaborator code from
    breaking during the transition.
    """

    def __init__(self):

        # ----------------------------------------------------
        # OLD NUMERICAL VALUES
        # ----------------------------------------------------

        self.sweetness = 50

        self.caffeine = 50

        self.temperature = 50

    # ========================================================
    # SWEETNESS
    # ========================================================

    def increase_sweetness(self):

        self.sweetness = min(
            100,
            self.sweetness + 10,
        )

    def decrease_sweetness(self):

        self.sweetness = max(
            0,
            self.sweetness - 10,
        )

    # ========================================================
    # CAFFEINE
    # ========================================================

    def increase_caffeine(self):

        self.caffeine = min(
            100,
            self.caffeine + 10,
        )

    def decrease_caffeine(self):

        self.caffeine = max(
            0,
            self.caffeine - 10,
        )

    # ========================================================
    # TEMPERATURE
    # ========================================================

    def increase_temperature(self):

        self.temperature = min(
            100,
            self.temperature + 10,
        )

    def decrease_temperature(self):

        self.temperature = max(
            0,
            self.temperature - 10,
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.sweetness = 50

        self.caffeine = 50

        self.temperature = 50

    # ========================================================
    # LEGACY DATA
    # ========================================================

    def get_data(self):

        return {

            "sweetness":
                self.sweetness,

            "caffeine":
                self.caffeine,

            "temperature":
                self.temperature,
        }
from dataclasses import dataclass


TEMPERATURE_OPTIONS = ("Cold", "Normal", "Hot")
CAFFEINE_OPTIONS = ("Low", "Normal", "High")
SWEETNESS_OPTIONS = ("Less", "Normal", "Extra")


LEVEL_PRICES = {
    1: 12,
    2: 18,
    3: 22,
}
@dataclass(frozen=True)
class DrinkRecipe:
    name: str
    unlock_level: int
    toppings: tuple
    liquid_color: tuple

    @property
    def price(self) -> int:
        """Return the price based on the drink's unlock level."""
        return LEVEL_PRICES.get(self.unlock_level, 5)

    def is_unlocked(self, level):
        try:
            return int(level) >= self.unlock_level
        except (TypeError, ValueError):
            return False


@dataclass
class PlayerDrink:
    drink_name: str = None
    temperature: str = None
    caffeine: str = None
    sweetness: str = None

    def has_drink(self):
        return self.drink_name is not None

    def has_temperature(self):
        return self.temperature is not None

    def has_caffeine(self):
        return self.caffeine is not None

    def has_sweetness(self):
        return self.sweetness is not None

    def is_fully_customised(self):
        return all(value is not None for value in (
            self.drink_name, self.temperature, self.caffeine, self.sweetness
        ))

    def reset(self):
        self.drink_name = self.temperature = self.caffeine = self.sweetness = None

    def get_data(self):
        return {
            "drink": self.drink_name,
            "temperature": self.temperature,
            "caffeine": self.caffeine,
            "sweetness": self.sweetness,
        }


DRINK_RECIPES = {
    "Neon Latte": DrinkRecipe("Neon Latte", 1, ("whipped_cream",), (255, 150, 210)),
    "Milkyway": DrinkRecipe("Milkyway", 1, ("whipped_cream", "chocolate_bits"), (105, 75, 145)),
    "Void Chai": DrinkRecipe("Void Chai", 1, ("whipped_cream",), (255, 190, 135)),
    "Cyber Fuel": DrinkRecipe("Cyber Fuel", 2, (), (155, 220, 255)),
    "Hologram Frappe": DrinkRecipe("Hologram Frappe", 2, ("whipped_cream",), (190, 170, 255)),
    "Pixel Lemint": DrinkRecipe("Pixel Lemint", 2, ("mint_leaves",), (255, 225, 95)),
    "Caramel Byte": DrinkRecipe("Caramel Byte", 3, ("whipped_cream", "caramel_crunch"), (205, 135, 70)),
    "Stardust Matcha": DrinkRecipe("Stardust Matcha", 3, ("yellow_stardust",), (165, 195, 105)),
    "Meteorite": DrinkRecipe("Meteorite", 3, ("meteorite_crumbs",), (235, 245, 255)),
}

DRINK_MENU = tuple(DRINK_RECIPES)


def get_recipe(drink_name):
    return DRINK_RECIPES.get(drink_name)


def get_drink_price(drink_name):
    """Retrieves the price for a specific drink based on its level tier."""
    recipe = get_recipe(drink_name)
    return recipe.price if recipe else 5


def is_valid_drink(drink_name):
    return drink_name in DRINK_RECIPES


def is_drink_unlocked(drink_name, level):
    recipe = get_recipe(drink_name)
    return recipe is not None and recipe.is_unlocked(level)


def get_unlocked_drinks(level):
    return [name for name in DRINK_MENU if is_drink_unlocked(name, level)]


def get_locked_drinks(level):
    return [name for name in DRINK_MENU if not is_drink_unlocked(name, level)]


def get_all_drinks():
    return list(DRINK_MENU)


def is_valid_temperature(value):
    return value in TEMPERATURE_OPTIONS


def is_valid_caffeine(value):
    return value in CAFFEINE_OPTIONS


def is_valid_sweetness(value):
    return value in SWEETNESS_OPTIONS


def validate_player_drink(player_drink):
    return (
        isinstance(player_drink, PlayerDrink)
        and is_valid_drink(player_drink.drink_name)
        and is_valid_temperature(player_drink.temperature)
        and is_valid_caffeine(player_drink.caffeine)
        and is_valid_sweetness(player_drink.sweetness)
    )


def get_drink_toppings(drink_name):
    recipe = get_recipe(drink_name)
    return recipe.toppings if recipe else ()


def get_drink_color(drink_name):
    recipe = get_recipe(drink_name)
    return recipe.liquid_color if recipe else (255, 255, 255)


class Drink:
    def __init__(self):
        self.reset()

    def _change(self, field, amount):
        setattr(self, field, max(0, min(100, getattr(self, field) + amount)))

    def increase_sweetness(self):
        self._change("sweetness", 10)

    def decrease_sweetness(self):
        self._change("sweetness", -10)

    def increase_caffeine(self):
        self._change("caffeine", 10)

    def decrease_caffeine(self):
        self._change("caffeine", -10)

    def increase_temperature(self):
        self._change("temperature", 10)

    def decrease_temperature(self):
        self._change("temperature", -10)

    def reset(self):
        self.sweetness = self.caffeine = self.temperature = 50

    def get_data(self):
        return {
            "sweetness": self.sweetness,
            "caffeine": self.caffeine,
            "temperature": self.temperature,
        }
"""
CYBERPUNK CAFÉ
GAME STATE SYSTEM

This file controls the LOGICAL stage of making a drink.

It does NOT:
    - draw anything
    - load images
    - draw buttons
    - control the visual mixing station

The MixingStation uses this class to ask:

    "Can I perform this action right now?"

The visual interface remains inside station.py.
"""


from enum import Enum, auto


# ============================================================
# GAME STATES
# ============================================================

class GameState(Enum):
    """
    Represents the current stage of making a drink.
    """

    # No active order.
    WAITING_FOR_ORDER = auto()

    # Customer order exists.
    # Player needs to select a drink.
    SELECT_DRINK = auto()

    # Drink selected.
    # Player needs to customise it.
    CUSTOMISE = auto()

    # Temperature, caffeine and sweetness selected.
    # Player can press BLEND.
    READY_TO_BLEND = auto()

    # Blender animation is running.
    BLENDING = auto()

    # Blender finished.
    # Drink is automatically ready to serve.
    READY_TO_SERVE = auto()

    # Drink has been served.
    SERVED = auto()


# ============================================================
# MIXING GAME STATE
# ============================================================

class MixingGameState:
    """
    Controls the logical drink-making workflow.

    IMPORTANT:

    This class does not decide whether the player's drink
    is CORRECT.

    Accuracy is handled by accuracy.py.

    Rewards are handled by rewards.py.
    """

    def __init__(self):

        # ----------------------------------------------------
        # CURRENT STATE
        # ----------------------------------------------------

        self.state = (
            GameState.WAITING_FOR_ORDER
        )

        # ----------------------------------------------------
        # CUSTOMER ORDER
        # ----------------------------------------------------

        self.current_order = None

        # ----------------------------------------------------
        # PLAYER SELECTIONS
        # ----------------------------------------------------

        self.selected_drink = None

        self.selected_temperature = None

        self.selected_caffeine = None

        self.selected_sweetness = None

        # ----------------------------------------------------
        # BLENDER
        # ----------------------------------------------------

        self.blend_finished = False

        # ----------------------------------------------------
        # SERVING
        # ----------------------------------------------------

        self.served = False

    # ========================================================
    # ORDER
    # ========================================================

    def set_order(self, order):
        """
        Give the mixing station a new customer order.

        Starting a new order clears the previous drink.
        """

        self.current_order = order

        self.clear_player_selections()

        self.blend_finished = False

        self.served = False

        self.state = (
            GameState.SELECT_DRINK
        )

    # ========================================================
    # CLEAR PLAYER SELECTIONS
    # ========================================================

    def clear_player_selections(self):
        """
        Clear all current player selections.
        """

        self.selected_drink = None

        self.selected_temperature = None

        self.selected_caffeine = None

        self.selected_sweetness = None

    # ========================================================
    # DRINK SELECTION
    # ========================================================

    def can_select_drink(self):
        """
        Return True if the player can select a drink.
        """

        return (
            self.state
            == GameState.SELECT_DRINK
        )

    def select_drink(self, drink_name):
        """
        Select a drink.

        SELECT_DRINK
              ↓
        CUSTOMISE
        """

        if not self.can_select_drink():
            return False

        if not drink_name:
            return False

        self.selected_drink = drink_name

        # Start fresh customisation for this drink.
        self.selected_temperature = None
        self.selected_caffeine = None
        self.selected_sweetness = None

        self.blend_finished = False
        self.served = False

        self.state = (
            GameState.CUSTOMISE
        )

        return True

    # ========================================================
    # CUSTOMISATION
    # ========================================================

    def can_customize(self):
        """
        Return True if the player can customise the drink.
        """

        return (
            self.state
            == GameState.CUSTOMISE
        )

    # ========================================================
    # TEMPERATURE
    # ========================================================

    def can_select_temperature(self):
        """
        Return True if temperature can be selected.
        """

        return self.can_customize()

    def select_temperature(self, temperature):
        """
        Select:

            Cold
            Normal
            Hot
        """

        if not self.can_select_temperature():
            return False

        if temperature is None:
            return False

        self.selected_temperature = temperature

        self._check_customisation_complete()

        return True

    # ========================================================
    # CAFFEINE
    # ========================================================

    def can_select_caffeine(self):
        """
        Return True if caffeine can be selected.
        """

        return self.can_customize()

    def select_caffeine(self, caffeine):
        """
        Select:

            Low
            Normal
            High
        """

        if not self.can_select_caffeine():
            return False

        if caffeine is None:
            return False

        self.selected_caffeine = caffeine

        self._check_customisation_complete()

        return True

    # ========================================================
    # SWEETNESS
    # ========================================================

    def can_select_sweetness(self):
        """
        Return True if sweetness can be selected.
        """

        return self.can_customize()

    def select_sweetness(self, sweetness):
        """
        Select:

            Less
            Normal
            Extra
        """

        if not self.can_select_sweetness():
            return False

        if sweetness is None:
            return False

        self.selected_sweetness = sweetness

        self._check_customisation_complete()

        return True

    # ========================================================
    # CHECK CUSTOMISATION
    # ========================================================

    def _check_customisation_complete(self):
        """
        Check whether all three customisation categories
        have been selected.

        IMPORTANT:

        These values do NOT have to be correct.

        Accuracy is checked later when the drink is served.
        """

        complete = (
            self.selected_temperature is not None
            and
            self.selected_caffeine is not None
            and
            self.selected_sweetness is not None
        )

        if complete:

            self.state = (
                GameState.READY_TO_BLEND
            )

    # ========================================================
    # BLEND
    # ========================================================

    def can_blend(self):
        """
        Return True when the BLEND button should be active.

        This method is required by station.py.
        """

        return (
            self.state
            == GameState.READY_TO_BLEND
        )

    def start_blending(self):
        """
        Start the blender.

        READY_TO_BLEND
              ↓
           BLENDING
        """

        if not self.can_blend():
            return False

        self.blend_finished = False

        self.state = (
            GameState.BLENDING
        )

        return True

    # ========================================================
    # BLENDER FINISHED
    # ========================================================

    def finish_blending(self):
        """
        Finish the blender animation.

        BLENDING
            ↓
        READY_TO_SERVE

        There is NO separate:
            BLENDED
            CUP_READY
            PLACE INTO CUP

        step.
        """

        if (
            self.state
            != GameState.BLENDING
        ):
            return False

        self.blend_finished = True

        self.state = (
            GameState.READY_TO_SERVE
        )

        return True

    # ========================================================
    # SERVE
    # ========================================================

    def can_serve(self):
        """
        Return True when the SERVE button should be active.
        """

        return (
            self.state
            == GameState.READY_TO_SERVE
            and
            self.blend_finished
        )

    def serve(self):
        """
        Serve the completed drink.

        READY_TO_SERVE
              ↓
           SERVED
        """

        if not self.can_serve():
            return False

        self.served = True

        self.state = (
            GameState.SERVED
        )

        return True

    # ========================================================
    # PLAYER DRINK DATA
    # ========================================================

    def get_player_drink_data(self):
        """
        Return the drink created by the player.

        accuracy.py uses this information to determine
        whether the order was correct.
        """

        return {
            "drink": self.selected_drink,

            "temperature":
                self.selected_temperature,

            "caffeine":
                self.selected_caffeine,

            "sweetness":
                self.selected_sweetness,
        }

    # ========================================================
    # STATE CHECKS
    # ========================================================

    def is_waiting_for_order(self):
        """
        Check whether there is no active order.
        """

        return (
            self.state
            == GameState.WAITING_FOR_ORDER
        )

    def is_selecting_drink(self):
        """
        Check whether the player is selecting a drink.
        """

        return (
            self.state
            == GameState.SELECT_DRINK
        )

    def is_customising(self):
        """
        Check whether the player is customising.
        """

        return (
            self.state
            == GameState.CUSTOMISE
        )

    def is_ready_to_blend(self):
        """
        Check whether BLEND can be pressed.
        """

        return (
            self.state
            == GameState.READY_TO_BLEND
        )

    def is_blending(self):
        """
        Check whether the blender is running.
        """

        return (
            self.state
            == GameState.BLENDING
        )

    def is_ready_to_serve(self):
        """
        Check whether the drink is ready to serve.
        """

        return (
            self.state
            == GameState.READY_TO_SERVE
        )

    def is_served(self):
        """
        Check whether the drink has been served.
        """

        return (
            self.state
            == GameState.SERVED
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        """
        Completely reset the mixing station.
        """

        self.state = (
            GameState.WAITING_FOR_ORDER
        )

        self.current_order = None

        self.clear_player_selections()

        self.blend_finished = False

        self.served = False
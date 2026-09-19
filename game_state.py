"""
============================================================
CYBERPUNK CAFÉ
GAME STATE SYSTEM
============================================================

This file controls the logical stage of the drink-making
process.

It does NOT draw anything.

It controls what the player is allowed to do.

MAIN FLOW
---------

WAITING_FOR_ORDER
        ↓
SELECT_DRINK
        ↓
CUSTOMISE
        ↓
READY_TO_BLEND
        ↓
BLENDING
        ↓
BLENDED
        ↓
READY_TO_SERVE
        ↓
SERVED


The system prevents invalid actions such as:

    • Serving before the drink is ready
    • Placing a drink into the cup before blending
    • Blending before all selections are made
    • Changing the drink while blending
    • Serving twice
    • Blending twice
============================================================
"""


from enum import Enum, auto


# ============================================================
# GAME STATE
# ============================================================

class GameState(Enum):

    # --------------------------------------------------------
    # No active customer order.
    # --------------------------------------------------------

    WAITING_FOR_ORDER = auto()

    # --------------------------------------------------------
    # Customer has an order.
    #
    # Player must choose the drink.
    # --------------------------------------------------------

    SELECT_DRINK = auto()

    # --------------------------------------------------------
    # Drink selected.
    #
    # Player chooses:
    #
    #   Temperature
    #   Caffeine
    #   Sweetness
    # --------------------------------------------------------

    CUSTOMISE = auto()

    # --------------------------------------------------------
    # All customisation choices are complete.
    #
    # Player can press BLEND.
    # --------------------------------------------------------

    READY_TO_BLEND = auto()

    # --------------------------------------------------------
    # Blender is currently running.
    # --------------------------------------------------------

    BLENDING = auto()

    # --------------------------------------------------------
    # Blender has finished.
    #
    # Player can put the drink into the cup.
    # --------------------------------------------------------

    BLENDED = auto()

    # --------------------------------------------------------
    # Drink has been placed into the cup.
    #
    # Player can now serve.
    # --------------------------------------------------------

    READY_TO_SERVE = auto()

    # --------------------------------------------------------
    # Drink has been served.
    # --------------------------------------------------------

    SERVED = auto()


# ============================================================
# MIXING GAME STATE
# ============================================================

class MixingGameState:

    """
    Controls the logical state of the Mixing Station.

    This class does not draw anything.

    It only controls whether actions are allowed.
    """

    # ========================================================
    # INITIALISATION
    # ========================================================

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
        # CUP
        # ----------------------------------------------------

        self.cup_filled = False

        # ----------------------------------------------------
        # SERVING
        # ----------------------------------------------------

        self.served = False

    # ========================================================
    # SET CUSTOMER ORDER
    # ========================================================

    def set_order(
        self,
        order,
    ):
        """
        Give the Mixing Station a new customer order.

        Starting state:

            SELECT_DRINK
        """

        self.current_order = order

        # ----------------------------------------------------
        # Clear old drink
        # ----------------------------------------------------

        self.clear_player_selections()

        # ----------------------------------------------------
        # Reset blender
        # ----------------------------------------------------

        self.blend_finished = False

        # ----------------------------------------------------
        # Reset cup
        # ----------------------------------------------------

        self.cup_filled = False

        # ----------------------------------------------------
        # Reset serving
        # ----------------------------------------------------

        self.served = False

        # ----------------------------------------------------
        # Start new order
        # ----------------------------------------------------

        self.state = (
            GameState.SELECT_DRINK
        )

    # ========================================================
    # CLEAR PLAYER SELECTIONS
    # ========================================================

    def clear_player_selections(self):

        self.selected_drink = None

        self.selected_temperature = None

        self.selected_caffeine = None

        self.selected_sweetness = None

    # ========================================================
    # DRINK SELECTION
    # ========================================================

    def can_select_drink(self):
        """
        The player can only select a drink when
        the station is waiting for the drink selection.
        """

        return (
            self.state
            == GameState.SELECT_DRINK
        )

    # --------------------------------------------------------

    def select_drink(
        self,
        drink_name,
    ):
        """
        Select the player's drink.

        Once selected, the player moves to CUSTOMISE.
        """

        if not self.can_select_drink():

            return False

        if not drink_name:

            return False

        self.selected_drink = (
            drink_name
        )

        self.state = (
            GameState.CUSTOMISE
        )

        return True

    # ========================================================
    # CUSTOMISATION
    # ========================================================

    def can_customize(self):

        return (
            self.state
            == GameState.CUSTOMISE
        )

    # ========================================================
    # TEMPERATURE
    # ========================================================

    def can_select_temperature(self):

        return self.can_customize()

    # --------------------------------------------------------

    def select_temperature(
        self,
        temperature,
    ):

        if not self.can_select_temperature():

            return False

        if not temperature:

            return False

        self.selected_temperature = (
            temperature
        )

        self._check_customisation_complete()

        return True

    # ========================================================
    # CAFFEINE
    # ========================================================

    def can_select_caffeine(self):

        return self.can_customize()

    # --------------------------------------------------------

    def select_caffeine(
        self,
        caffeine,
    ):

        if not self.can_select_caffeine():

            return False

        if not caffeine:

            return False

        self.selected_caffeine = (
            caffeine
        )

        self._check_customisation_complete()

        return True

    # ========================================================
    # SWEETNESS
    # ========================================================

    def can_select_sweetness(self):

        return self.can_customize()

    # --------------------------------------------------------

    def select_sweetness(
        self,
        sweetness,
    ):

        if not self.can_select_sweetness():

            return False

        if not sweetness:

            return False

        self.selected_sweetness = (
            sweetness
        )

        self._check_customisation_complete()

        return True

    # ========================================================
    # CHECK CUSTOMISATION
    # ========================================================

    def _check_customisation_complete(self):
        """
        Check whether all three customisation values
        have been selected.
        """

        complete = (

            self.selected_temperature
            is not None

            and

            self.selected_caffeine
            is not None

            and

            self.selected_sweetness
            is not None

        )

        if complete:

            self.state = (
                GameState.READY_TO_BLEND
            )

    # ========================================================
    # BLENDING
    # ========================================================

    def can_blend(self):
        """
        Blending is only possible after all three
        customisation values have been selected.
        """

        return (
            self.state
            == GameState.READY_TO_BLEND
        )

    # --------------------------------------------------------

    def start_blending(self):

        if not self.can_blend():

            return False

        self.blend_finished = False

        self.state = (
            GameState.BLENDING
        )

        return True

    # ========================================================
    # FINISH BLENDING
    # ========================================================

    def finish_blending(self):
        """
        Called when the blender animation/timer finishes.
        """

        if (
            self.state
            != GameState.BLENDING
        ):

            return False

        self.blend_finished = True

        self.state = (
            GameState.BLENDED
        )

        return True

    # ========================================================
    # PLACE INTO CUP
    # ========================================================

    def can_place_into_cup(self):
        """
        The player can only place the drink into
        the cup after blending is complete.
        """

        return (

            self.state
            == GameState.BLENDED

            and

            self.blend_finished

            and

            not self.cup_filled

        )

    # --------------------------------------------------------

    def place_into_cup(self):

        if not self.can_place_into_cup():

            return False

        # ----------------------------------------------------
        # Fill cup
        # ----------------------------------------------------

        self.cup_filled = True

        # ----------------------------------------------------
        # Move directly to READY_TO_SERVE
        # ----------------------------------------------------

        self.state = (
            GameState.READY_TO_SERVE
        )

        return True

    # ========================================================
    # READY TO SERVE
    # ========================================================

    def can_serve(self):
        """
        Serving is allowed only after:

            • Drink has been selected
            • All customisation is complete
            • Blending is complete
            • Drink has been placed into cup
        """

        return (

            self.state
            == GameState.READY_TO_SERVE

            and

            self.cup_filled

            and

            not self.served

        )

    # ========================================================
    # SERVE
    # ========================================================

    def serve(self):
        """
        Mark the current order as served.

        main.py will then perform:

            1. Accuracy check
            2. Reward calculation
            3. XP update
            4. Credit update
            5. Level-up check
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
        Return the player's completed drink.

        This dictionary is passed to accuracy.py.
        """

        return {

            "drink":
                self.selected_drink,

            "temperature":
                self.selected_temperature,

            "caffeine":
                self.selected_caffeine,

            "sweetness":
                self.selected_sweetness,
        }

    # ========================================================
    # ORDER DATA
    # ========================================================

    def get_current_order(self):

        return self.current_order

    # ========================================================
    # STATE CHECKS
    # ========================================================

    def is_waiting_for_order(self):

        return (
            self.state
            == GameState.WAITING_FOR_ORDER
        )

    # --------------------------------------------------------

    def is_selecting_drink(self):

        return (
            self.state
            == GameState.SELECT_DRINK
        )

    # --------------------------------------------------------

    def is_customising(self):

        return (
            self.state
            == GameState.CUSTOMISE
        )

    # --------------------------------------------------------

    def is_blending(self):

        return (
            self.state
            == GameState.BLENDING
        )

    # --------------------------------------------------------

    def is_blended(self):

        return (
            self.state
            == GameState.BLENDED
        )

    # --------------------------------------------------------

    def is_ready_to_serve(self):

        return (
            self.state
            == GameState.READY_TO_SERVE
        )

    # --------------------------------------------------------

    def is_served(self):

        return (
            self.state
            == GameState.SERVED
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        """
        Completely reset the current drink-making process.
        """

        self.state = (
            GameState.WAITING_FOR_ORDER
        )

        self.current_order = None

        self.clear_player_selections()

        self.blend_finished = False

        self.cup_filled = False

        self.served = False
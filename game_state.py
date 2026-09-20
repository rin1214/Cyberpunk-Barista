from enum import Enum, auto


# ============================================================
# CYBERPUNK CAFÉ
# GAME STATE SYSTEM
# ============================================================
#
# This file controls the LOGICAL stage of making a drink.
#
# It does NOT draw anything.
# It does NOT handle images.
# It does NOT handle buttons visually.
#
# The MixingStation asks this class:
#
#     "Can I do this action right now?"
#
# This keeps the gameplay rules separate from the graphics.
#
# ============================================================


class GameState(Enum):
    """
    Represents the current stage of the drink-making process.
    """

    # --------------------------------------------------------
    # No active order is currently being processed.
    # --------------------------------------------------------

    WAITING_FOR_ORDER = auto()

    # --------------------------------------------------------
    # A customer has an order.
    #
    # The player must choose the drink.
    # --------------------------------------------------------

    SELECT_DRINK = auto()

    # --------------------------------------------------------
    # The drink has been selected.
    #
    # The player must choose:
    #
    #   Temperature
    #   Caffeine
    #   Sweetness
    # --------------------------------------------------------

    CUSTOMISE = auto()

    # --------------------------------------------------------
    # All three customisation choices are complete.
    #
    # The player can now press BLEND.
    # --------------------------------------------------------

    READY_TO_BLEND = auto()

    # --------------------------------------------------------
    # Blender is currently running.
    # --------------------------------------------------------

    BLENDING = auto()

    # --------------------------------------------------------
    # Blender has finished.
    #
    # There is NO PLACE INTO CUP step anymore.
    #
    # The drink automatically becomes ready to serve.
    # --------------------------------------------------------

    READY_TO_SERVE = auto()

    # --------------------------------------------------------
    # The drink has been served.
    # --------------------------------------------------------

    SERVED = auto()


# ============================================================
# MIXING GAME STATE
# ============================================================


class MixingGameState:
    """
    Controls the logical state of the Mixing Station.

    This class does not draw anything.

    It only manages:

        - customer order
        - drink selection
        - customisation
        - blending
        - serving

    ========================================================
    NEW GAMEPLAY FLOW
    ========================================================

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
        READY_TO_SERVE
                ↓
        SERVED

    ========================================================

    There is deliberately NO:

        BLENDED
        CUP_READY
        PLACE INTO CUP

    because the player should not have to press a
    separate Place button anymore.
    """

    def __init__(self):

        # ====================================================
        # CURRENT STATE
        # ====================================================

        self.state = (
            GameState.WAITING_FOR_ORDER
        )

        # ====================================================
        # CUSTOMER ORDER
        # ====================================================

        self.current_order = None

        # ====================================================
        # PLAYER SELECTIONS
        # ====================================================

        self.selected_drink = None

        self.selected_temperature = None

        self.selected_caffeine = None

        self.selected_sweetness = None

        # ====================================================
        # BLENDER
        # ====================================================

        self.blend_finished = False

        # ====================================================
        # SERVING
        # ====================================================

        self.served = False

    # ========================================================
    # ORDER
    # ========================================================

    def set_order(self, order):
        """
        Give the Mixing Station a new customer order.

        Starting a new order clears all previous
        drink-making selections.
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
        Remove all current player selections.
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
        Returns True when the player is allowed
        to select a drink.
        """

        return (
            self.state
            == GameState.SELECT_DRINK
        )

    def select_drink(
        self,
        drink_name,
    ):
        """
        Select a drink.

        Once selected, the game moves to CUSTOMISE.
        """

        if not self.can_select_drink():

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
        """
        Returns True when the player is allowed
        to change the drink customisation.
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
        Returns True if temperature can be selected.
        """

        return self.can_customize()

    def select_temperature(
        self,
        temperature,
    ):
        """
        Select the drink temperature.
        """

        if not self.can_select_temperature():

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
        """
        Returns True if caffeine can be selected.
        """

        return self.can_customize()

    def select_caffeine(
        self,
        caffeine,
    ):
        """
        Select the drink caffeine level.
        """

        if not self.can_select_caffeine():

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
        """
        Returns True if sweetness can be selected.
        """

        return self.can_customize()

    def select_sweetness(
        self,
        sweetness,
    ):
        """
        Select the drink sweetness level.
        """

        if not self.can_select_sweetness():

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
        Check whether all three customisation
        categories have been selected.

        Required:

            Temperature
            Caffeine
            Sweetness
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
        Returns True when the player can press BLEND.
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

        There is deliberately no intermediate
        BLENDED or CUP_READY state.
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
    # SERVING
    # ========================================================

    def can_serve(self):
        """
        Returns True when the finished drink
        can be served.
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
        Return the completed player drink.

        The result is a dictionary because the existing
        accuracy/reward systems use this format.
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
    # STATE CHECK HELPERS
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
        Check whether the player is selecting
        the drink.
        """

        return (
            self.state
            == GameState.SELECT_DRINK
        )

    def is_customising(self):
        """
        Check whether the player is customising
        the drink.
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
        Check whether the drink has already been served.
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
        Completely reset the mixing station state.
        """

        self.state = (
            GameState.WAITING_FOR_ORDER
        )

        self.current_order = None

        self.clear_player_selections()

        self.blend_finished = False

        self.served = False


# ============================================================
# END OF GAME_STATE.PY
# ============================================================
from enum import Enum, auto


# ============================================================
# CYBERPUNK CAFÉ
# GAME STATE SYSTEM
# ============================================================
#
# This file controls the LOGICAL stages of making a drink.
#
# It does NOT draw anything.
#
# It does NOT control:
#   - graphics
#   - blender animation
#   - customer graphics
#   - XP
#   - credits
#   - rewards
#
# Those responsibilities belong to other files.
#
# The MixingStation asks this system:
#
#   "Can I do this action right now?"
#
# and this class returns True or False.
#
# ============================================================


class GameState(Enum):
    """
    Represents the current stage of the drink-making process.
    """

    # --------------------------------------------------------
    # NO ACTIVE ORDER
    # --------------------------------------------------------

    WAITING_FOR_ORDER = auto()

    # --------------------------------------------------------
    # CUSTOMER HAS AN ORDER
    #
    # Player must select the requested drink.
    # --------------------------------------------------------

    SELECT_DRINK = auto()

    # --------------------------------------------------------
    # DRINK SELECTED
    #
    # Player must choose:
    #
    #   Temperature
    #   Caffeine
    #   Sweetness
    # --------------------------------------------------------

    CUSTOMISE = auto()

    # --------------------------------------------------------
    # ALL CUSTOMISATION COMPLETE
    #
    # Player can now press BLEND.
    # --------------------------------------------------------

    READY_TO_BLEND = auto()

    # --------------------------------------------------------
    # BLENDER IS RUNNING
    #
    # station.py controls the actual animation.
    # --------------------------------------------------------

    BLENDING = auto()

    # --------------------------------------------------------
    # BLENDING FINISHED
    #
    # Drink is automatically ready to serve.
    #
    # There is NO PLACE INTO CUP state anymore.
    # --------------------------------------------------------

    READY_TO_SERVE = auto()

    # --------------------------------------------------------
    # DRINK HAS BEEN SERVED
    # --------------------------------------------------------

    SERVED = auto()


# ============================================================
# MIXING STATION CONTROLLER
# ============================================================


class MixingGameState:
    """
    Controls the logical state of the Mixing Station.

    This class does NOT draw anything.

    It only controls what the player is allowed to do.
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

        A new order starts a completely fresh drink-making
        process.
        """

        self.current_order = order

        # Clear previous drink.
        self.clear_player_selections()

        # Reset blender.
        self.blend_finished = False

        # Reset serving.
        self.served = False

        # The player now needs to choose a drink.
        self.state = (
            GameState.SELECT_DRINK
        )

    # ========================================================
    # CLEAR PLAYER SELECTIONS
    # ========================================================

    def clear_player_selections(self):
        """
        Clears all current drink selections.
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
        Returns True when the player is allowed to select
        a drink from the menu.
        """

        return (
            self.state
            == GameState.SELECT_DRINK
        )

    def select_drink(self, drink_name):
        """
        Selects the player's drink.

        Once a drink is selected, the state changes to
        CUSTOMISE.
        """

        if not self.can_select_drink():

            return False

        if not drink_name:

            return False

        self.selected_drink = drink_name

        self.state = (
            GameState.CUSTOMISE
        )

        return True

    # ========================================================
    # CUSTOMISATION
    # ========================================================

    def can_customize(self):
        """
        Returns True when the player can change:

            Temperature
            Caffeine
            Sweetness
        """

        return (
            self.state
            == GameState.CUSTOMISE
        )

    # ========================================================
    # TEMPERATURE
    # ========================================================

    def can_select_temperature(self):

        return self.can_customize()

    def select_temperature(self, temperature):
        """
        Selects temperature.
        """

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

    def select_caffeine(self, caffeine):
        """
        Selects caffeine level.
        """

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

    def select_sweetness(self, sweetness):
        """
        Selects sweetness level.
        """

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
        Checks whether all three customisation choices
        have been selected.
        """

        complete = (
            self.selected_drink is not None
            and
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
    # BLENDING
    # ========================================================

    def can_blend(self):
        """
        Returns True only when all drink choices are complete.
        """

        return (
            self.state
            == GameState.READY_TO_BLEND
        )

    def start_blending(self):
        """
        Starts the logical blender state.

        station.py will handle the visual animation.
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
        Called by station.py when the blender animation
        has actually finished.

        The drink immediately becomes ready to serve.

        There is no CUP_READY state anymore.
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
    # READY TO SERVE
    # ========================================================

    def can_serve(self):
        """
        Returns True when the completed drink can be served.
        """

        return (
            self.state
            == GameState.READY_TO_SERVE
            and
            self.blend_finished
        )

    # ========================================================
    # SERVE
    # ========================================================

    def serve(self):
        """
        Marks the drink as served.
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
        Returns the player's current drink data.

        The result is a dictionary containing:

            drink
            temperature
            caffeine
            sweetness

        This is passed to OrderAccuracy.
        """

        return {
            "drink": self.selected_drink,

            "temperature": (
                self.selected_temperature
            ),

            "caffeine": (
                self.selected_caffeine
            ),

            "sweetness": (
                self.selected_sweetness
            ),
        }

    # ========================================================
    # CURRENT ORDER
    # ========================================================

    def get_current_order(self):
        """
        Returns the customer's current order.
        """

        return self.current_order

    # ========================================================
    # STATE CHECK HELPERS
    # ========================================================

    def is_waiting(self):

        return (
            self.state
            == GameState.WAITING_FOR_ORDER
        )

    def is_selecting_drink(self):

        return (
            self.state
            == GameState.SELECT_DRINK
        )

    def is_customising(self):

        return (
            self.state
            == GameState.CUSTOMISE
        )

    def is_ready_to_blend(self):

        return (
            self.state
            == GameState.READY_TO_BLEND
        )

    def is_blending(self):

        return (
            self.state
            == GameState.BLENDING
        )

    def is_ready_to_serve(self):

        return (
            self.state
            == GameState.READY_TO_SERVE
        )

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
        Completely resets the Mixing Station state.
        """

        self.state = (
            GameState.WAITING_FOR_ORDER
        )

        self.current_order = None

        self.clear_player_selections()

        self.blend_finished = False

        self.served = False
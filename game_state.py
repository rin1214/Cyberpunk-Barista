from enum import Enum, auto


# ============================================================
# CYBERPUNK CAFÉ
# GAME STATE SYSTEM
# ============================================================
#
# This file controls the logical stage of the drink-making
# process.
#
# The visual buttons will eventually ask this system:
#
#     "Am I allowed to be used right now?"
#
# The answer depends on the current GameState.
#
# ============================================================


class GameState(Enum):
    """
    Represents the current stage of the drink-making process.
    """

    # --------------------------------------------------------
    # No customer/order is currently being processed.
    # --------------------------------------------------------

    WAITING_FOR_ORDER = auto()

    # --------------------------------------------------------
    # Customer has an order.
    # Player must choose the drink.
    # --------------------------------------------------------

    SELECT_DRINK = auto()

    # --------------------------------------------------------
    # Drink has been selected.
    # Player must choose:
    #
    # Temperature
    # Caffeine
    # Sweetness
    # --------------------------------------------------------

    CUSTOMISE = auto()

    # --------------------------------------------------------
    # All four required selections have been made.
    # Player may press BLEND.
    # --------------------------------------------------------

    READY_TO_BLEND = auto()

    # --------------------------------------------------------
    # Blender is currently running.
    # --------------------------------------------------------

    BLENDING = auto()

    # --------------------------------------------------------
    # Blender has finished.
    # Player may place drink into cup.
    # --------------------------------------------------------

    BLENDED = auto()

    # --------------------------------------------------------
    # Drink has been placed into the cup.
    # --------------------------------------------------------

    CUP_READY = auto()

    # --------------------------------------------------------
    # Everything required for serving is complete.
    # --------------------------------------------------------

    READY_TO_SERVE = auto()

    # --------------------------------------------------------
    # Drink has been served.
    # --------------------------------------------------------

    SERVED = auto()


# ============================================================
# MIXING STATION CONTROLLER
# ============================================================

class MixingGameState:
    """
    Controls the logical state of the Mixing Station.

    This class does NOT draw anything.

    It only answers questions such as:

        Can the player select a drink?
        Can the player change temperature?
        Can the player blend?
        Can the player place the drink into a cup?
        Can the player serve?
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
        # CUP
        # ----------------------------------------------------

        self.cup_filled = False

        # ----------------------------------------------------
        # SERVING
        # ----------------------------------------------------

        self.served = False

    # ========================================================
    # ORDER
    # ========================================================

    def set_order(self, order):
        """
        Give the Mixing Station a new customer order.
        """

        self.current_order = order

        # Start a fresh drink-making process.

        self.clear_player_selections()

        self.blend_finished = False

        self.cup_filled = False

        self.served = False

        self.state = GameState.SELECT_DRINK

    # ========================================================
    # CLEAR PLAYER SELECTIONS
    # ========================================================

    def clear_player_selections(self):
        """
        Remove the player's current drink selections.
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
        Returns True if the player is allowed to select
        a drink.
        """

        return self.state == GameState.SELECT_DRINK

    def select_drink(self, drink_name):
        """
        Select a drink.

        This action is only allowed during SELECT_DRINK.
        """

        if not self.can_select_drink():

            return False

        self.selected_drink = drink_name

        # Once a drink is selected, the player can
        # customise it.

        self.state = GameState.CUSTOMISE

        return True

    # ========================================================
    # CUSTOMISATION
    # ========================================================

    def can_customize(self):
        """
        Returns True if the player can change
        temperature, caffeine or sweetness.
        """

        return self.state == GameState.CUSTOMISE

    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    def can_select_temperature(self):

        return self.can_customize()

    def select_temperature(self, temperature):

        if not self.can_select_temperature():

            return False

        self.selected_temperature = temperature

        self._check_customisation_complete()

        return True

    # --------------------------------------------------------
    # CAFFEINE
    # --------------------------------------------------------

    def can_select_caffeine(self):

        return self.can_customize()

    def select_caffeine(self, caffeine):

        if not self.can_select_caffeine():

            return False

        self.selected_caffeine = caffeine

        self._check_customisation_complete()

        return True

    # --------------------------------------------------------
    # SWEETNESS
    # --------------------------------------------------------

    def can_select_sweetness(self):

        return self.can_customize()

    def select_sweetness(self, sweetness):

        if not self.can_select_sweetness():

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
    # BLENDING
    # ========================================================

    def can_blend(self):

        return self.state == GameState.READY_TO_BLEND

    def start_blending(self):

        if not self.can_blend():

            return False

        self.blend_finished = False

        self.state = GameState.BLENDING

        return True

    # ========================================================
    # BLENDER FINISHED
    # ========================================================

    def finish_blending(self):

        if self.state != GameState.BLENDING:

            return False

        self.blend_finished = True

        self.state = GameState.BLENDED

        return True

    # ========================================================
    # PLACE INTO CUP
    # ========================================================

    def can_place_into_cup(self):

        return (
            self.state == GameState.BLENDED
            and
            self.blend_finished
        )

    def place_into_cup(self):

        if not self.can_place_into_cup():

            return False

        self.cup_filled = True

        self.state = GameState.CUP_READY

        return True

    # ========================================================
    # READY TO SERVE
    # ========================================================

    def can_serve(self):

        return (
            self.state == GameState.CUP_READY
            and
            self.cup_filled
        )

    # ========================================================
    # SERVE
    # ========================================================

    def serve(self):

        if not self.can_serve():

            return False

        self.served = True

        self.state = GameState.SERVED

        return True

    # ========================================================
    # PLAYER DRINK DATA
    # ========================================================

    def get_player_drink_data(self):
        """
        Return the player's completed drink information.
        """

        return {
            "drink": self.selected_drink,
            "temperature": self.selected_temperature,
            "caffeine": self.selected_caffeine,
            "sweetness": self.selected_sweetness,
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.state = (
            GameState.WAITING_FOR_ORDER
        )

        self.current_order = None

        self.clear_player_selections()

        self.blend_finished = False

        self.cup_filled = False

        self.served = False
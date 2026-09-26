from enum import Enum, auto


class GameState(Enum):
    WAITING_FOR_ORDER = auto()
    SELECT_DRINK = auto()
    CUSTOMISE = auto()
    READY_TO_BLEND = auto()
    BLENDING = auto()
    READY_TO_SERVE = auto()
    SERVED = auto()


class MixingGameState:
    _OPTIONS = ("selected_temperature", "selected_caffeine", "selected_sweetness")

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = GameState.WAITING_FOR_ORDER
        self.current_order = None
        self.clear_player_selections()
        self.blend_finished = self.served = False

    def clear_player_selections(self):
        self.selected_drink = None
        self.selected_temperature = None
        self.selected_caffeine = None
        self.selected_sweetness = None

    def set_order(self, order):
        self.current_order = order
        self.clear_player_selections()
        self.blend_finished = self.served = False
        self.state = GameState.SELECT_DRINK

    def can_select_drink(self):
        return self.state == GameState.SELECT_DRINK

    def select_drink(self, drink_name):
        if not self.can_select_drink() or not drink_name:
            return False
        self.selected_drink = drink_name
        self.selected_temperature = self.selected_caffeine = self.selected_sweetness = None
        self.blend_finished = self.served = False
        self.state = GameState.CUSTOMISE
        return True

    def can_customize(self):
        return self.state == GameState.CUSTOMISE

    can_select_temperature = can_customize
    can_select_caffeine = can_customize
    can_select_sweetness = can_customize

    def _select_option(self, field, value):
        if not self.can_customize() or value is None:
            return False
        setattr(self, field, value)
        if all(getattr(self, option) is not None for option in self._OPTIONS):
            self.state = GameState.READY_TO_BLEND
        return True

    def select_temperature(self, value):
        return self._select_option("selected_temperature", value)

    def select_caffeine(self, value):
        return self._select_option("selected_caffeine", value)

    def select_sweetness(self, value):
        return self._select_option("selected_sweetness", value)

    def can_blend(self):
        return self.state == GameState.READY_TO_BLEND

    def start_blending(self):
        if not self.can_blend():
            return False
        self.blend_finished = False
        self.state = GameState.BLENDING
        return True

    def finish_blending(self):
        if self.state != GameState.BLENDING:
            return False
        self.blend_finished = True
        self.state = GameState.READY_TO_SERVE
        return True

    def can_serve(self):
        return self.state == GameState.READY_TO_SERVE and self.blend_finished

    def serve(self):
        if not self.can_serve():
            return False
        self.served = True
        self.state = GameState.SERVED
        return True

    def get_player_drink_data(self):
        return {
            "drink": self.selected_drink,
            "temperature": self.selected_temperature,
            "caffeine": self.selected_caffeine,
            "sweetness": self.selected_sweetness,
        }

    def _is_state(self, state):
        return self.state == state

    def is_waiting_for_order(self):
        return self._is_state(GameState.WAITING_FOR_ORDER)

    def is_selecting_drink(self):
        return self._is_state(GameState.SELECT_DRINK)

    def is_customising(self):
        return self._is_state(GameState.CUSTOMISE)

    def is_ready_to_blend(self):
        return self._is_state(GameState.READY_TO_BLEND)

    def is_blending(self):
        return self._is_state(GameState.BLENDING)

    def is_ready_to_serve(self):
        return self._is_state(GameState.READY_TO_SERVE)

    def is_served(self):
        return self._is_state(GameState.SERVED)
class MapNode:
    def __init__(self, name, level_req, x, y, description, cost=0):
        self.name = name
        self.level_req = level_req
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.description = description
        self.cost = cost
        self.is_unlocked = False


class MapManager:
    def __init__(self, economy=None, economy_ref=None):
        self.economy = economy if economy is not None else economy_ref

        self.nodes = {
            "neon_alley": MapNode(
                "Back Alley Kiosk", 1, 225, 390,
                "The gritty starting district. Neon lights and simple brews."
            ),
            "cyber_dock": MapNode(
                "Neon Lounge", 2, 700, 370,
                "Bustling shipping docks with heavy cybernetic foot traffic.",
                250
            ),
            "high_rise": MapNode(
                "Cyber Penthouse", 3, 1120, 375,
                "Elite skyscraper lounge for high-tier corporate clients.",
                500
            )
        }

        self.check_unlocks()

    def check_unlocks(self):
        for node in self.nodes.values():
            node.is_unlocked = (
                node.level_req == 1 or
                self.economy.is_level_unlocked(node.level_req)
            )

    def unlock_node(self, node_id):
        return self.select_node(node_id)

    def select_node(self, node_id):
        node = self.nodes.get(node_id)

        if not node:
            return False

        self.check_unlocks()

        if not node.is_unlocked:
            if not self.economy.unlock_level_with_credits(
                node.level_req
            ):
                return False
            node.is_unlocked = True

        return self.economy.set_level(node.level_req)
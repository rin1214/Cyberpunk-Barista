class SkillNode:
    def __init__(self, node_id, name, level_req, cost, description, pos, prerequisites=None):
        self.node_id = node_id
        self.name = name
        self.level_req = level_req  # Level number (1, 2, or 3)
        self.cost = cost            # Shift credits required to unlock
        self.description = description
        self.pos = pos              # (x, y) coordinates for the click UI
        self.prerequisites = prerequisites if prerequisites else []
        self.is_unlocked = (level_req == 1)  # Level 1 is unlocked by default

class MapManager:
    def __init__(self, economy_ref):
        self.economy = economy_ref
        self.nodes = {}
        self._initialize_default_nodes()

    def _initialize_default_nodes(self):
        """Initializes your 3 map nodes with visual screen coordinates."""
        self.add_node(SkillNode("neon_alley", "Neon Alley", 1, 0, "The starting underground district cafe.", (320, 360)))
        self.add_node(SkillNode("cyber_dock", "Cyber Dock", 2, 50, "A humid, neon-lit dockside bar.", (640, 360), prerequisites=["neon_alley"]))
        self.add_node(SkillNode("high_rise", "High Rise Bar", 3, 120, "An upscale lounge overlooking the skyline.", (960, 360), prerequisites=["cyber_dock"]))

    def add_node(self, node):
        self.nodes[node.node_id] = node

    def unlock_node(self, node_id):
        """Manually unlocks a map node using player credits if prerequisites are met."""
        if node_id not in self.nodes:
            print(f"[MAP MANAGER] Error: Node '{node_id}' does not exist.")
            return False

        node = self.nodes[node_id]

        if node.is_unlocked:
            return True

        # Check prerequisites
        for prereq_id in node.prerequisites:
            if not self.nodes[prereq_id].is_unlocked:
                print(f"[MAP MANAGER] Cannot unlock [{node.name}]. Missing required map: [{self.nodes[prereq_id].name}]")
                return False

        # Check credit balance
        if self.economy.credits < node.cost:
            print(f"[MAP MANAGER] Not enough credits for [{node.name}]. Need {node.cost}c, have {self.economy.credits}c.")
            return False

        # Deduct credits and unlock
        self.economy.credits -= node.cost
        node.is_unlocked = True
        self.economy.save_economy_data()

        print(f"[MAP MANAGER] SUCCESS: Unlocked map [{node.name}] for {node.cost} credits!")
        return True
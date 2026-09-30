class MapNode:
    def __init__(self, name, level_req, x, y, description, cost=0):
        self.name = name
        self.level_req = level_req
        self.x = x
        self.y = y
        self.pos = (x, y)  # Required by map_screen.py for drawing lines and nodes[cite: 10]
        self.description = description
        self.cost = cost   # Required by map_screen.py to show unlock/travel costs[cite: 10]
        self.is_unlocked = False

class MapManager:
    def __init__(self, economy_ref):
        self.economy = economy_ref
        
        # Define districts/nodes on the map with individual costs[cite: 10]
        self.nodes = {
            "neon_alley": MapNode("Back Alley Kiosk", level_req=1, x=280, y=360, description="The gritty starting district. Neon lights and simple brews.", cost=0),
            "cyber_dock": MapNode("Neon Lounge", level_req=2, x=640, y=360, description="Bustling shipping docks with heavy cybernetic foot traffic.", cost=250),
            "high_rise":  MapNode("Cyber Penthouse", level_req=3, x=1000, y=360, description="Elite skyscraper lounge for high-tier corporate clients.", cost=500)
        }
        
        self.check_unlocks()

    def check_unlocks(self):
        """Strictly checks UIEconomy purchase states. Level 1 is always free/unlocked; others require explicit credit purchase."""
        for node_key, node in self.nodes.items():
            if node.level_req == 1:
                node.is_unlocked = True
            else:
                # Only unlock if explicitly purchased and tracked in economy
                if hasattr(self.economy, "is_level_unlocked"):
                    node.is_unlocked = self.economy.is_level_unlocked(node.level_req)
                else:
                    node.is_unlocked = False

    def unlock_node(self, node_key):
        """Bridge method matching what map_screen.py expects for unlocking/selecting nodes[cite: 10]."""
        return self.select_node(node_key)

    def select_node(self, node_key):
        """Selects a node, forces a credit purchase if locked, and updates current level/location[cite: 10]."""
        if node_key not in self.nodes:
            return False
            
        node = self.nodes[node_key]
        self.check_unlocks()
        
        # 1. If already unlocked via prior purchase, travel there immediately[cite: 10]
        if node.is_unlocked:
            success = self.economy.set_level(node.level_req)
            return success
        
        # 2. If locked, force a credit purchase through UIEconomy[cite: 10]
        if hasattr(self.economy, "unlock_level_with_credits"):
            if self.economy.unlock_level_with_credits(node.level_req):
                node.is_unlocked = True
                self.economy.set_level(node.level_req)
                return True
        else:
            if self.economy.credits >= node.cost:
                if self.economy.spend_credits(node.cost):
                    node.is_unlocked = True
                    self.economy.set_level(node.level_req)
                    return True
                    
        return False
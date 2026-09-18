class MapNode:
    def __init__(self, name, level_req, x, y, description, cost=0):
        self.name = name
        self.level_req = level_req
        self.x = x
        self.y = y
        self.pos = (x, y)  # Required by map_screen.py for drawing lines and nodes
        self.description = description
        self.cost = cost   # Required by map_screen.py to show unlock/travel costs
        self.is_unlocked = False

class MapManager:
    def __init__(self, economy_ref):
        self.economy = economy_ref
        
        # Define districts/nodes on the map with individual costs
        self.nodes = {
            "neon_alley": MapNode("Back Alley Kiosk", level_req=1, x=280, y=360, description="The gritty starting district. Neon lights and simple brews.", cost=0),
            "cyber_dock": MapNode("Neon Lounge", level_req=2, x=640, y=360, description="Bustling shipping docks with heavy cybernetic foot traffic.", cost=150),
            "high_rise":  MapNode("Cyber Penthouse", level_req=3, x=1000, y=360, description="Elite skyscraper lounge for high-tier corporate clients.", cost=300)
        }
        
        self.check_unlocks()

    def check_unlocks(self):
        """Automatically unlocks nodes based on the player's saved level or economy progress."""
        current_lvl = getattr(self.economy, "level", 1)
        
        if current_lvl >= 1:
            self.nodes["neon_alley"].is_unlocked = True
        if current_lvl >= 2:
            self.nodes["neon_alley"].is_unlocked = True
            self.nodes["cyber_dock"].is_unlocked = True
        if current_lvl >= 3:
            self.nodes["neon_alley"].is_unlocked = True
            self.nodes["cyber_dock"].is_unlocked = True
            self.nodes["high_rise"].is_unlocked = True

    def unlock_node(self, node_key):
        """Bridge method matching what map_screen.py expects for unlocking/selecting nodes."""
        return self.select_node(node_key)

    def select_node(self, node_key):
        """Selects a node, handles credit deduction if locking requires a purchase, and updates economy level."""
        if node_key in self.nodes:
            node = self.nodes[node_key]
            self.check_unlocks()
            
            # If already unlocked, just travel there
            if node.is_unlocked:
                self.economy.level = node.level_req
                if node.level_req in self.economy.LOCATIONS:
                    self.economy.location = self.economy.LOCATIONS[node.level_req]
                self.economy.save_economy_data()
                return True
            
            # If locked, check if player has enough credits to buy it
            elif not node.is_unlocked and self.economy.credits >= node.cost:
                if self.economy.spend_credits(node.cost):
                    node.is_unlocked = True
                    self.economy.level = node.level_req
                    if node.level_req in self.economy.LOCATIONS:
                        self.economy.location = self.economy.LOCATIONS[node.level_req]
                    self.economy.save_economy_data()
                    return True
        return False
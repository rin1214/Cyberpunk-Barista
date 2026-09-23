import os
import pygame


class MapScreen:
    def __init__(self, screen, map_manager, economy, project_root=None):
        self.screen = screen
        self.map_manager = map_manager
        self.economy = economy

        if project_root is None:
            project_root = os.path.dirname(os.path.abspath(__file__))
        self.project_root = project_root

        # UI fonts
        self.font_title = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_body = pygame.font.SysFont("Consolas", 18)
        self.font_small = pygame.font.SysFont("Consolas", 14)

        # Dictionary to store pictures for each node
        self.node_images = {}
        self._load_node_images()

    def _load_node_images(self):
        # Map node names or IDs to image filenames
        # Make sure you place these images in assets/images/nodes/
        image_mapping = {
            "back alley kiosk": "kiosk.png",
            "neon lounge": "lounge.png",
            "cyber penthouse": "penthouse.png"
        }

        for node_id, node in self.map_manager.nodes.items():
            # Check by node name lowercased
            filename = image_mapping.get(node.name.lower(), f"{node_id}.png")
            img_path = os.path.join(self.project_root, "assets", "images", "nodes", filename)

            try:
                if os.path.exists(img_path):
                    # Load and scale to fit the 200x100 node card box
                    img = pygame.image.load(img_path).convert_alpha()
                    self.node_images[node_id] = pygame.transform.smoothscale(img, (200, 100))
                else:
                    self.node_images[node_id] = None
            except pygame.error:
                self.node_images[node_id] = None

    def _draw_cyber_grid(self, screen_w, screen_h):
        # Draw a faint cyberpunk grid pattern in the background
        grid_color = (25, 18, 40)
        grid_spacing = 40
        for x in range(0, screen_w, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, screen_h), 1)
        for y in range(0, screen_h, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (screen_w, y), 1)

    def _draw_tech_corners(self, rect, color, length=10, thickness=2):
        # Draw tech bracket corners around node boxes for HUD styling
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        pygame.draw.line(self.screen, color, (x, y), (x + length, y), thickness)
        pygame.draw.line(self.screen, color, (x, y), (x, y + length), thickness)
        pygame.draw.line(self.screen, color, (x + w, y), (x + w - length, y), thickness)
        pygame.draw.line(self.screen, color, (x + w, y), (x + w, y + length), thickness)
        pygame.draw.line(self.screen, color, (x, y + h), (x + length, y + h), thickness)
        pygame.draw.line(self.screen, color, (x, y + h), (x, y + h - length), thickness)
        pygame.draw.line(self.screen, color, (x + w, y + h), (x + w - length, y + h), thickness)
        pygame.draw.line(self.screen, color, (x + w, y + h), (x + w, y + h - length), thickness)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            dt = clock.tick(60) / 1000.0
            screen_w, screen_h = self.screen.get_size()

            # Handle player inputs
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse click
                        pos = event.pos
                        for node_id, node in self.map_manager.nodes.items():
                            rect = pygame.Rect(node.pos[0] - 100, node.pos[1] - 50, 200, 100)
                            if rect.collidepoint(pos):
                                if node.is_unlocked:
                                    # Switch active level location only if clicked
                                    self.economy.level = node.level_req
                                    self.economy.location = self.economy.LOCATIONS.get(node.level_req, node.name)
                                    self.economy.save_economy_data()
                                    print(f"[MAP] Switched active location to {node.name}")
                                    running = False
                                else:
                                    # Attempt to unlock locked node
                                    if self.map_manager.unlock_node(node_id):
                                        self.economy.level = node.level_req
                                        self.economy.location = self.economy.LOCATIONS.get(node.level_req, node.name)
                                        self.economy.save_economy_data()
                                        running = False

            # Render background color and tech grid
            self.screen.fill((12, 8, 22))
            self._draw_cyber_grid(screen_w, screen_h)

            # Title Header & Credits
            title_surf = self.font_title.render("DISTRICT MAP // SELECT STATION", True, (0, 255, 204))
            title_rect = title_surf.get_rect(center=(screen_w // 2, 60))
            self.screen.blit(title_surf, title_rect)

            credits_surf = self.font_body.render(f"CREDITS: ${self.economy.credits}", True, (255, 255, 255))
            self.screen.blit(credits_surf, (50, 50))

            hint_surf = self.font_small.render("Click unlocked nodes to switch, or locked nodes to unlock. Press [M] or [ESC] to return.", True, (150, 150, 180))
            hint_rect = hint_surf.get_rect(center=(screen_w // 2, screen_h - 40))
            self.screen.blit(hint_surf, hint_rect)

            # Draw glowing circuit connection lines between nodes
            node_list = list(self.map_manager.nodes.values())
            for i in range(len(node_list) - 1):
                p1 = node_list[i].pos
                p2 = node_list[i+1].pos
                pygame.draw.line(self.screen, (50, 30, 70), p1, p2, 6)
                pygame.draw.line(self.screen, (0, 255, 204), p1, p2, 2)

            # Draw Node Picture Cards
            for node_id, node in self.map_manager.nodes.items():
                rect = pygame.Rect(node.pos[0] - 100, node.pos[1] - 50, 200, 100)
                
                # Determine border color based on status
                if node.is_unlocked:
                    border_col = (0, 255, 204) if self.economy.level == node.level_req else (0, 140, 110)
                else:
                    border_col = (255, 60, 110)

                # Draw the node picture if it exists, otherwise fallback to a dark rectangle
                node_img = self.node_images.get(node_id)
                if node_img:
                    # Apply a dark tint or draw image directly
                    self.screen.blit(node_img, rect.topleft)
                    # Add a semi-transparent dark overlay so text is readable over pictures
                    overlay = pygame.Surface((200, 100), pygame.SRCALPHA)
                    overlay.fill((10, 8, 20, 150))
                    self.screen.blit(overlay, rect.topleft)
                else:
                    bg_col = (18, 35, 42) if node.is_unlocked else (38, 18, 30)
                    pygame.draw.rect(self.screen, bg_col, rect, border_radius=10)

                # Draw outer neon border & tech corners
                pygame.draw.rect(self.screen, border_col, rect, width=2, border_radius=10)
                if node.is_unlocked:
                    self._draw_tech_corners(rect, (0, 255, 204), length=10, thickness=2)

                # Node Title Text with shadow for readability
                name_surf = self.font_body.render(node.name, True, (255, 255, 255))
                name_rect = name_surf.get_rect(center=(node.pos[0], node.pos[1] - 15))
                self.screen.blit(name_surf, name_rect)

                # Status / Cost Text
                if node.is_unlocked:
                    status_text = "ACTIVE" if self.economy.level == node.level_req else "UNLOCKED"
                    status_surf = self.font_small.render(status_text, True, (0, 255, 150))
                else:
                    status_text = f"UNLOCK (${node.cost})"
                    status_surf = self.font_small.render(status_text, True, (255, 120, 150))
                
                status_rect = status_surf.get_rect(center=(node.pos[0], node.pos[1] + 18))
                self.screen.blit(status_surf, status_rect)

            pygame.display.flip()
        return True
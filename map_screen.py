import pygame

class MapScreen:
    def __init__(self, screen, map_manager, economy):
        self.screen = screen
        self.map_manager = map_manager
        self.economy = economy
        self.font_title = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_body = pygame.font.SysFont("Consolas", 18)
        self.font_small = pygame.font.SysFont("Consolas", 14)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            dt = clock.tick(60) / 1000.0
            screen_w, screen_h = self.screen.get_size()

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
                            # Define bounding box for each node button (200x100 pixels centered at node.pos)
                            rect = pygame.Rect(node.pos[0] - 100, node.pos[1] - 50, 200, 100)
                            if rect.collidepoint(pos):
                                if node.is_unlocked:
                                    # Switch active level
                                    self.economy.level = node.level_req
                                    self.economy.location = self.economy.LOCATIONS.get(node.level_req, node.name)
                                    self.economy.save_economy_data()
                                    print(f"[MAP] Switched active location to {node.name}")
                                    running = False
                                else:
                                    # Try to unlock node
                                    if self.map_manager.unlock_node(node_id):
                                        self.economy.level = node.level_req
                                        self.economy.location = self.economy.LOCATIONS.get(node.level_req, node.name)
                                        self.economy.save_economy_data()
                                        running = False

            # Render Map Background
            self.screen.fill((12, 8, 22))

            # Title Header
            title_surf = self.font_title.render("DISTRICT MAP // SELECT STATION", True, (0, 255, 204))
            title_rect = title_surf.get_rect(center=(screen_w // 2, 60))
            self.screen.blit(title_surf, title_rect)

            credits_surf = self.font_body.render(f"CREDITS: ${self.economy.credits}", True, (255, 255, 255))
            self.screen.blit(credits_surf, (50, 50))

            hint_surf = self.font_small.render("Click unlocked nodes to switch, or locked nodes to unlock. Press [M] or [ESC] to return.", True, (150, 150, 180))
            hint_rect = hint_surf.get_rect(center=(screen_w // 2, screen_h - 40))
            self.screen.blit(hint_surf, hint_rect)

            # Draw connecting lines between nodes
            node_list = list(self.map_manager.nodes.values())
            for i in range(len(node_list) - 1):
                p1 = node_list[i].pos
                p2 = node_list[i+1].pos
                pygame.draw.line(self.screen, (70, 50, 90), p1, p2, 4)

            # Draw Node Buttons
            for node_id, node in self.map_manager.nodes.items():
                rect = pygame.Rect(node.pos[0] - 100, node.pos[1] - 50, 200, 100)
                
                if node.is_unlocked:
                    bg_col = (20, 45, 45)
                    border_col = (0, 255, 204) if self.economy.level == node.level_req else (0, 160, 130)
                else:
                    bg_col = (40, 20, 30)
                    border_col = (255, 60, 110)

                pygame.draw.rect(self.screen, bg_col, rect, border_radius=10)
                pygame.draw.rect(self.screen, border_col, rect, width=2, border_radius=10)

                # Node Title Text
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
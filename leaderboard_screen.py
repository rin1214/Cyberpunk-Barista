import pygame

class LeaderboardScreen:
    def __init__(self, screen, leaderboard_manager, economy):
        self.screen = screen
        self.lb_manager = leaderboard_manager
        self.economy = economy
        self.font_title = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_body = pygame.font.SysFont("Consolas", 18)
        self.font_small = pygame.font.SysFont("Consolas", 14)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        # Ensure current player stats are synced before displaying
        self.lb_manager.update_current_player_score()

        while running:
            clock.tick(60)
            screen_w, screen_h = self.screen.get_size()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_l:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Close button rect at bottom center
                        close_rect = pygame.Rect(screen_w // 2 - 100, screen_h - 90, 200, 45)
                        if close_rect.collidepoint(event.pos):
                            running = False

            # Render Background Overlay
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((10, 8, 20, 230))
            self.screen.blit(overlay, (0, 0))

            # Title Header
            title_surf = self.font_title.render("DISTRICT LEADERBOARD // TOP BARISTAS", True, (255, 0, 128))
            title_rect = title_surf.get_rect(center=(screen_w // 2, 70))
            self.screen.blit(title_surf, title_rect)

            # Table Container Box
            table_rect = pygame.Rect(screen_w // 2 - 350, 130, 700, 430)
            pygame.draw.rect(self.screen, (25, 15, 35), table_rect, border_radius=12)
            pygame.draw.rect(self.screen, (255, 0, 128), table_rect, width=2, border_radius=12)

            # Table Headers
            header_y = 155
            rank_h = self.font_body.render("RANK", True, (150, 150, 180))
            name_h = self.font_body.render("BARISTA", True, (150, 150, 180))
            level_h = self.font_body.render("LEVEL", True, (150, 150, 180))
            xp_h = self.font_body.render("XP / CREDITS", True, (150, 150, 180))

            self.screen.blit(rank_h, (table_rect.x + 30, header_y))
            self.screen.blit(name_h, (table_rect.x + 130, header_y))
            self.screen.blit(level_h, (table_rect.x + 400, header_y))
            self.screen.blit(xp_h, (table_rect.x + 530, header_y))

            pygame.draw.line(self.screen, (70, 40, 70), (table_rect.x + 20, header_y + 30), (table_rect.right - 20, header_y + 30), 2)

            # Render Player Rows (Top 8)
            players = self.lb_manager.get_ranked_players()[:8]
            row_y = header_y + 45

            for idx, p in enumerate(players):
                is_current_player = p["name"].lower() == self.economy.player_name.lower()
                row_color = (0, 255, 204) if is_current_player else (255, 255, 255)

                rank_txt = self.font_body.render(f"#{idx + 1}", True, row_color)
                name_txt = self.font_body.render(p["name"].upper(), True, row_color)
                lvl_txt = self.font_body.render(str(p["level"]), True, row_color)
                xp_txt = self.font_body.render(f"${p['xp']}", True, row_color)

                self.screen.blit(rank_txt, (table_rect.x + 35, row_y))
                self.screen.blit(name_txt, (table_rect.x + 130, row_y))
                self.screen.blit(lvl_txt, (table_rect.x + 415, row_y))
                self.screen.blit(xp_txt, (table_rect.x + 545, row_y))

                row_y += 42

            # Close Button
            close_rect = pygame.Rect(screen_w // 2 - 100, screen_h - 90, 200, 45)
            pygame.draw.rect(self.screen, (40, 20, 45), close_rect, border_radius=8)
            pygame.draw.rect(self.screen, (0, 255, 204), close_rect, width=2, border_radius=8)
            
            close_surf = self.font_body.render("CLOSE [L / ESC]", True, (0, 255, 204))
            close_r = close_surf.get_rect(center=close_rect.center)
            self.screen.blit(close_surf, close_r)

            pygame.display.flip()
        return True
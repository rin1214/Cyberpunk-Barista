import pygame

class MixingStation:
    def __init__(self, drink):
        self.drink = drink

        # FONTS
        self.title_font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.label_font = pygame.font.SysFont("Consolas", 12, bold=True)
        self.btn_font = pygame.font.SysFont("Consolas", 18, bold=True)
        self.serve_font = pygame.font.SysFont("Consolas", 16, bold=True)

        # ANCHOR TO RIGHT SIDE (620 to 930 X)
        self.panel_rect = pygame.Rect(620, 110, 320, 410)

        # ADJUSTED BUTTON & METER RECTS
        self.sweetness_minus = pygame.Rect(640, 175, 35, 35)
        self.sweetness_bar   = pygame.Rect(685, 180, 190, 25)
        self.sweetness_plus  = pygame.Rect(885, 175, 35, 35)

        self.caffeine_minus  = pygame.Rect(640, 255, 35, 35)
        self.caffeine_bar    = pygame.Rect(685, 260, 190, 25)
        self.caffeine_plus   = pygame.Rect(885, 255, 35, 35)

        self.temp_minus      = pygame.Rect(640, 335, 35, 35)
        self.temp_bar        = pygame.Rect(685, 340, 190, 25)
        self.temp_plus       = pygame.Rect(885, 335, 35, 35)

        self.serve_button    = pygame.Rect(640, 445, 280, 50)
        self.served = False

    def draw(self, screen):
        # 1. Translucent Cyberpunk Workbench Panel
        panel_surf = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        panel_surf.fill((14, 16, 28, 225))
        screen.blit(panel_surf, self.panel_rect.topleft)

        # Neon Outer Frame
        pygame.draw.rect(screen, (0, 220, 255), self.panel_rect, width=2, border_radius=12)

        # Header Title
        title_txt = self.title_font.render("// DRINK DISPENSER //", True, (0, 240, 255))
        screen.blit(title_txt, (self.panel_rect.x + 35, self.panel_rect.y + 15))

        # 2. Controls & Dynamic Color Meters
        self._draw_control(screen, "SWEETNESS", self.drink.sweetness, 155, 
                           self.sweetness_minus, self.sweetness_bar, self.sweetness_plus, (255, 100, 200))
        
        self._draw_control(screen, "CAFFEINE", self.drink.caffeine, 235, 
                           self.caffeine_minus, self.caffeine_bar, self.caffeine_plus, (0, 220, 255))

        # Temperature shifts color: Cold Blue -> Hot Red
        temp_color = (255, 60, 60) if self.drink.temperature > 60 else (60, 180, 255)
        self._draw_control(screen, "TEMPERATURE", self.drink.temperature, 315, 
                           self.temp_minus, self.temp_bar, self.temp_plus, temp_color)

        # 3. Dynamic Mixing Cup Preview
        self._draw_cup_preview(screen)

        # 4. Serve Button
        self._draw_serve_btn(screen)

    def _draw_control(self, screen, label, value, y_pos, btn_minus, bar_rect, btn_plus, color):
        # Label
        lbl_txt = self.label_font.render(f"{label}: {value}%", True, (220, 225, 240))
        screen.blit(lbl_txt, (bar_rect.x, y_pos))

        # Minus Button
        m_pos = pygame.mouse.get_pos()
        m_color = (255, 80, 120) if btn_minus.collidepoint(m_pos) else (180, 50, 90)
        pygame.draw.rect(screen, m_color, btn_minus, border_radius=6)
        txt = self.btn_font.render("-", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=btn_minus.center))

        # Meter Track
        pygame.draw.rect(screen, (20, 22, 35), bar_rect, border_radius=6)
        fill_w = int((bar_rect.width - 4) * (value / 100.0))
        if fill_w > 0:
            pygame.draw.rect(screen, color, (bar_rect.x + 2, bar_rect.y + 2, fill_w, bar_rect.height - 4), border_radius=4)
        pygame.draw.rect(screen, (70, 80, 110), bar_rect, width=1, border_radius=6)

        # Plus Button
        p_color = (0, 240, 160) if btn_plus.collidepoint(m_pos) else (0, 160, 110)
        pygame.draw.rect(screen, p_color, btn_plus, border_radius=6)
        txt = self.btn_font.render("+", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=btn_plus.center))

    def _draw_cup_preview(self, screen):
        # Calculates fluid tint based on parameters
        r = min(255, int((self.drink.temperature / 100.0) * 255))
        g = min(255, int((self.drink.sweetness / 100.0) * 200))
        b = min(255, int((self.drink.caffeine / 100.0) * 255))
        fluid_color = (max(40, r), max(40, g), max(40, b))

        cup_x, cup_y = 765, 385
        # Glass Cup Backing
        pygame.draw.rect(screen, (20, 25, 40), (cup_x, cup_y, 30, 45), border_radius=4)
        # Dynamic Fluid Level
        pygame.draw.rect(screen, fluid_color, (cup_x + 2, cup_y + 10, 26, 33), border_radius=3)
        # Neon Glass Outline
        pygame.draw.rect(screen, (0, 240, 255), (cup_x, cup_y, 30, 45), width=2, border_radius=4)

    def _draw_serve_btn(self, screen):
        m_pos = pygame.mouse.get_pos()
        btn_color = (255, 0, 128) if self.serve_button.collidepoint(m_pos) else (180, 0, 95)
        
        pygame.draw.rect(screen, btn_color, self.serve_button, border_radius=8)
        pygame.draw.rect(screen, (255, 150, 220), self.serve_button, width=2, border_radius=8)

        txt = self.serve_font.render("[SERVE DRINK]", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.serve_button.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.sweetness_minus.collidepoint(pos): self.drink.decrease_sweetness()
            elif self.sweetness_plus.collidepoint(pos): self.drink.increase_sweetness()
            elif self.caffeine_minus.collidepoint(pos): self.drink.decrease_caffeine()
            elif self.caffeine_plus.collidepoint(pos): self.drink.increase_caffeine()
            elif self.temp_minus.collidepoint(pos): self.drink.decrease_temperature()
            elif self.temp_plus.collidepoint(pos): self.drink.increase_temperature()
            elif self.serve_button.collidepoint(pos): self.served = True

    def reset(self):
        self.drink.reset()
        self.served = False
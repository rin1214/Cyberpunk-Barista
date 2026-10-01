import math
import os
import random
import pygame

class OrderScene:
    """Animated order scene with randomized customers: back view during order, front view during mixing."""

    def __init__(self, screen):
        self.screen = screen
        self.active = False
        self.customer = None
        self.current_level = 1
        self.t = 0.0
        self.phase = 0  # 0 = Customer speaking order, 1 = Barista responding, 2 = Ready to finish
        self.customer_text = ""
        self.barista_text = ""
        self.shown = 0
        self.ready = False
        
        self.font = pygame.font.Font(None, 28)
        self.small = pygame.font.Font(None, 22)
        self.big = pygame.font.Font(None, 34)
        
        self.accent = (70, 235, 255)
        self.pink = (255, 75, 190)
        
        self.barista_name = "Ryu"
        self.barista_image = None
        self.back_customer_images = self._load_all_back_customer_sprites()
        self.level_backgrounds = self._load_level_backgrounds()
        self._load_selected_barista()

    def set_barista(self, barista_name):
        """Switch the order-scene avatar to the selected barista."""
        if barista_name not in ("Ryu", "Kira", "Jax"):
            barista_name = "Ryu"
        self.barista_name = barista_name
        self._load_selected_barista()

    def _load_selected_barista(self):
        project_root = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            project_root, "assets", "mahirah", "baristas",
            f"{self.barista_name.lower()}.png"
        )
        self.barista_image = None
        if os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert_alpha()
                # Small order-scene portrait: behind the counter, not a giant foreground sprite.
                self.barista_image = pygame.transform.smoothscale(raw, (285, 285))
                print(f"[ORDER SCENE] Loaded {self.barista_name} avatar.")
            except pygame.error as error:
                print(f"[ORDER SCENE] Could not load {path}: {error}")
        else:
            print(f"[ORDER SCENE] Missing barista avatar: {path}")

    def _load_single_back_sprite(self, filename):
        project_root = os.path.dirname(os.path.abspath(__file__))
        paths_to_try = [
            os.path.join(project_root, "assets", "customers", filename),
            os.path.join(project_root, "assets", "cutomer", filename),
            os.path.join(project_root, "assets", "customer", filename),
            os.path.join(project_root, filename)
        ]
        
        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    return pygame.transform.smoothscale(img, (220, 270))
                except pygame.error as e:
                    print(f"[WARNING] Failed to load {path}: {e}")
        return None

    def _load_all_back_customer_sprites(self):
        """Loads back-facing sprites for all 6 cyberpunk archetypes including the Cyberpunk Cat & Corp Spy."""
        archetypes = ["runner", "hacker", "exec", "drone_pilot", "corp_spy", "cyberpunk_cat"]
        sprites = {}
        for ctype in archetypes:
            img = (
                self._load_single_back_sprite(f"{ctype}_back.png") or 
                self._load_single_back_sprite(f"{ctype}back.png")
            )
            sprites[ctype] = img
        return sprites

    def _load_level_backgrounds(self):
        project_root = os.path.dirname(os.path.abspath(__file__))
        bgs = {}
        for lvl in range(1, 4):
            path = os.path.join(project_root, "assets", "places", f"cafe_lvl{lvl}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    bgs[lvl] = pygame.transform.smoothscale(img, (1280, 720))
                except Exception:
                    bgs[lvl] = None
        return bgs

    def start(self, customer, level=1):
        self.customer = customer
        self.current_level = max(1, min(level, 3))
        self.active = True
        self.t = 0.0
        self.phase = 0
        self.shown = 0
        self.ready = False
        
        # Synchronize customer type properties across all 6 expanded archetypes
        available_types = ["runner", "hacker", "exec", "drone_pilot", "corp_spy", "cyberpunk_cat"]
        if hasattr(self.customer, "current_type") and self.customer.current_type in available_types:
            self.customer.customer_type = self.customer.current_type
        elif hasattr(self.customer, "customer_type") and self.customer.customer_type in available_types:
            self.customer.current_type = self.customer.customer_type
        else:
            chosen = random.choice(available_types)
            self.customer.current_type = chosen
            self.customer.customer_type = chosen

        # Save original front-facing sprite before switching to back view for order dialogue
        if self.customer:
            if not hasattr(self.customer, "original_image") or self.customer.original_image is None:
                if hasattr(self.customer, "image"):
                    self.customer.original_image = self.customer.image

            # Assign and sync the correct back-view sprite
            if hasattr(self.customer, "back_image") and self.customer.back_image is not None:
                self.customer.image = self.customer.back_image
            else:
                back_img = self.back_customer_images.get(self.customer.current_type)
                if back_img and hasattr(self.customer, "image"):
                    self.customer.image = back_img

        self.customer_text = self._make_customer_text(customer)
        self.barista_text = "Got it! Logging recipe parameters into the brew queue now..."

    def _make_customer_text(self, customer):
        o = customer.order
        return f"Hi! Can I get one {o.drink}, temperature {o.temperature.lower()}, {o.caffeine.lower()} caffeine, and {o.sweetness.lower()} sweet?"

    def handle_event(self, event):
        """Processes clicks or keypresses to skip text typing or advance dialogues."""
        if not self.active:
            return
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            if event.type == pygame.KEYDOWN and event.key not in (pygame.K_SPACE, pygame.K_RETURN):
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button != 1:
                return
            self._handle_advance()

    def _handle_advance(self):
        if self.phase == 0:
            if self.shown < len(self.customer_text):
                self.shown = len(self.customer_text)
            else:
                self.phase = 1
                self.t = 0.0
                self.shown = 0
        elif self.phase == 1:
            if self.shown < len(self.barista_text):
                self.shown = len(self.barista_text)
            else:
                self.phase = 2
                self.ready = True
        elif self.ready:
            self._finish()

    def _finish(self):
        self.active = False
        if self.customer:
            # front-facing sprite for workstation mixing/waiting phase!
            if hasattr(self.customer, "original_image") and self.customer.original_image is not None:
                self.customer.image = self.customer.original_image
            elif hasattr(self.customer, "_load_sprite") and hasattr(self.customer, "current_type"):
                self.customer.image = self.customer._load_sprite(self.customer.current_type, back_view=False)
            
            self.customer.state = "waiting"
            if hasattr(self.customer, "y_counter"):
                self.customer.current_y = self.customer.y_counter
                self.customer.rect.bottom = int(self.customer.y_counter)

    def update(self, dt):
        if not self.active:
            return
        self.t += dt
        
        if self.phase == 0:
            self.shown = int(self.t * 18)
            if self.shown >= len(self.customer_text):
                self.shown = len(self.customer_text)
        elif self.phase == 1:
            self.shown = int(self.t * 22)
            if self.shown >= len(self.barista_text):
                self.shown = len(self.barista_text)
                self.phase = 2
                self.ready = True

    def draw(self, screen):
        if not self.active or not self.customer:
            return
        bg = self.level_backgrounds.get(self.current_level)
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((15, 10, 25))
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((5, 8, 20, 110))
        screen.blit(overlay, (0, 0))
        self._customer(screen)
        self._barista(screen)
        if self.phase == 0:
            self._draw_customer_bubble(screen)
        else:
            self._draw_barista_bubble(screen)
            
        self._top(screen)

    def _customer(self, screen):
        cust_type = getattr(self.customer, "current_type", getattr(self.customer, "customer_type", "runner"))
        cust_img = None
        if hasattr(self.customer, "back_image") and self.customer.back_image:
            cust_img = pygame.transform.smoothscale(self.customer.back_image, (220, 270))
        else:
            cust_img = self.back_customer_images.get(cust_type)
            if not cust_img and hasattr(self.customer, "image"):
                cust_img = pygame.transform.smoothscale(self.customer.image, (220, 270))
        
        if not cust_img:
            cust_img = pygame.Surface((220, 270), pygame.SRCALPHA)
            cust_img.fill((100, 100, 150))

        bob = math.sin(self.t * 4) * 3
        rect = cust_img.get_rect(midbottom=(420, 700 + bob))
        screen.blit(cust_img, rect)
        customer_name = str(cust_type).replace("_", " ").upper()
        self._label(screen, customer_name, rect.centerx, rect.bottom + 6, self.accent)

    def _barista(self, screen):
        x, y = 750, 570
        bob = math.sin(self.t * 3.0) * 1.5

        if self.barista_image is None:
            return

        # Keep the character compact enough to read as staff behind the counter.
        target_w, target_h = 235, 235
        image = pygame.transform.smoothscale(
            self.barista_image, (target_w, target_h)
        )
        rect = image.get_rect(midbottom=(x, y + bob))

        # level at the game's 1280x720 resolution.
        counter_top = 575
        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(0, 0, screen.get_width(), counter_top))
        screen.blit(image, rect)
        screen.set_clip(old_clip)

        # Put the name below the counter, like the customer's name.
        self._label(
            screen,
            self.barista_name.upper(),
            x,
            600 + bob,
            self.pink
        )

    def _draw_customer_bubble(self, screen):
        bx, by, bw, bh = 140, 80, 520, 145
        bubble_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(screen, (10, 18, 40), bubble_rect, border_radius=16)
        pygame.draw.rect(screen, self.accent, bubble_rect, width=2, border_radius=16)
        screen.blit(self.big.render("CUSTOMER ORDER", True, self.pink), (bx + 20, by + 12))
        current_text = self.customer_text[:self.shown]
        self._wrap(screen, current_text, bx + 20, by + 48, bw - 40)
        
        hint = "► CLICK TO SKIP / CONTINUE"
        screen.blit(self.small.render(hint, True, self.accent), (bx + 20, by + 112))
        points = [(390, bubble_rect.bottom), (420, bubble_rect.bottom), (405, bubble_rect.bottom + 16)]
        pygame.draw.polygon(screen, (10, 18, 40), points)
        pygame.draw.line(screen, self.accent, (390, bubble_rect.bottom), (405, bubble_rect.bottom + 16), 2)
        pygame.draw.line(screen, self.accent, (405, bubble_rect.bottom + 16), (420, bubble_rect.bottom), 2)

    def _draw_barista_bubble(self, screen):
        bx, by, bw, bh = 620, 80, 520, 145
        bubble_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(screen, (20, 12, 40), bubble_rect, border_radius=16)
        pygame.draw.rect(screen, self.pink, bubble_rect, width=2, border_radius=16)
        screen.blit(self.big.render("BARISTA RESPONSE", True, self.accent), (bx + 20, by + 12))
        current_text = self.barista_text[:self.shown]
        self._wrap(screen, current_text, bx + 20, by + 48, bw - 40)
        hint = "► CLICK TO START MIXING" if self.ready else "► CLICK TO SKIP"
        screen.blit(self.small.render(hint, True, self.accent), (bx + 20, by + 112))
        points = [(830, bubble_rect.bottom), (860, bubble_rect.bottom), (845, bubble_rect.bottom + 16)]
        pygame.draw.polygon(screen, (20, 12, 40), points)
        pygame.draw.line(screen, self.pink, (830, bubble_rect.bottom), (845, bubble_rect.bottom + 16), 2)
        pygame.draw.line(screen, self.pink, (845, bubble_rect.bottom + 16), (860, bubble_rect.bottom), 2)

    def _top(self, screen):
        text = "INCOMING ORDER TRANSMISSION" if not self.ready else "READY TO MIX DRINK"
        s = self.font.render(text, True, (235, 245, 255))
        screen.blit(s, s.get_rect(center=(640, 30)))

    def _wrap(self, screen, text, x, y, width):
        words = text.split()
        line = ""
        yy = y
        for word in words:
            test = (line + " " + word).strip()
            if self.font.size(test)[0] > width:
                screen.blit(self.font.render(line, True, (225, 235, 250)), (x, yy))
                yy += 24
                line = word
            else:
                line = test
        if line:
            screen.blit(self.font.render(line, True, (225, 235, 250)), (x, yy))

    def _label(self, screen, text, x, y, color):
        s = self.small.render(text, True, color)
        screen.blit(s, s.get_rect(center=(x, y)))
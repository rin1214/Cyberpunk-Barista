from __future__ import annotations
import math, os, time, pygame
from drink import (
    PlayerDrink, DRINK_MENU, TEMPERATURE_OPTIONS,
    CAFFEINE_OPTIONS, SWEETNESS_OPTIONS, get_recipe,
    is_drink_unlocked, is_valid_drink,
)
from game_state import MixingGameState, GameState
from mini_challenges import MiniChallenge
from audio_settings import get_audio
from recipe_book import RecipeBook


class MixingStation:
    WIDTH, HEIGHT = 1280, 720

    # --- Colour palette ---
    CYAN        = (75, 225, 255)
    CYAN_LIGHT  = (165, 245, 255)
    PINK        = (255, 80, 190)
    PINK_LIGHT  = (255, 165, 225)
    PURPLE      = (185, 105, 255)
    WHITE       = (245, 248, 255)
    SOFT_WHITE  = (215, 222, 240)
    MUTED       = (125, 140, 170)
    YELLOW      = (255, 220, 100)
    GREEN       = (90, 235, 165)
    LOCKED      = (65, 70, 95)
    PANEL           = (7, 12, 30, 175)
    BUTTON          = (9, 17, 38, 185)
    BUTTON_SELECTED = (65, 15, 65, 205)

    # Drink names longer than one word are split across two lines in the menu
    SPLIT_NAMES = {
        "Hologram Frappe": ("HOLOGRAM", "FRAPPE"),
        "Stardust Matcha": ("STARDUST", "MATCHA"),
        "Cyber Fuel":      ("CYBER",    "FUEL"),
        "Pixel Lemint":    ("PIXEL",    "LEMINT"),
        "Caramel Byte":    ("CARAMEL",  "BYTE"),
    }

    # Pixel ingredients drawn inside the blender for each drink
    _INGREDIENTS = {
        "Neon Latte":      ["milk","coffee","syrup"],
        "Milkyway":        ["milk","chocolate","star"],
        "Void Chai":       ["milk","spice","syrup"],
        "Cyber Fuel":      ["milk","battery","ice"],
        "Hologram Frappe": ["milk","orb","star"],
        "Pixel Lemint":    ["water","mint","ice"],
        "Caramel Byte":    ["milk","cookie","caramel"],
        "Stardust Matcha": ["milk","matcha","star"],
        "Meteorite":       ["milk","meteor","ice"],
    }

    # ------------------------------------------------------------------ init

    def __init__(self, drink=None, level=1, progression=None, rewards=None, economy=None, barista="Ryu"):
        self.drink = drink
        self.barista = barista if barista in ("Ryu", "Kira", "Jax") else "Ryu"
        self.player_drink = PlayerDrink()
        self.game_state   = MixingGameState()
        self.progression, self.rewards, self.economy = progression, rewards, economy
        self.level = max(1, int(level))
        self.audio = get_audio()   # shared with the start screen

        base = os.path.dirname(os.path.abspath(__file__))
        self.drink_dir = os.path.join(base, "assets", "drinks")
        self.ui_dir    = os.path.join(base, "assets", "ui")
        self.font_dir  = os.path.join(base, "assets", "fonts")

        self._init_state()
        self._load_ui_images()
        self._create_fonts()
        self.drink_images = {}
        self._load_drink_images()
        self._create_layout()
        self._attach_legacy_bridge()
        self.audio.load_sfx()
        self.audio.apply_volumes()

    def _init_state(self):
        """Reset all gameplay state (called on init and reset)."""
        self.challenge         = MiniChallenge()
        self.customer_order    = None
        self.served            = False
        self.liquid_unlocked   = False
        self.assembly_phase    = "empty"
        self.assembly_started  = 0.0
        self.blend_start_time  = 0.0
        self.blender_angle     = 0.0
        self.blender_pulse     = 0.0
        self.blend_duration    = self._prep_duration(0.7)
        self._last_time        = time.monotonic()
        self.last_xp_change    = 0
        self.last_credit_change = 0
        self.reward_feedback_until = 0.0
        self.menu_requested        = False
        self.map_requested         = False
        self.leaderboard_requested = False
        self.exit_requested        = False
        self.return_start_requested = False
        self.show_menu_overlay     = False
        self.recipe_book           = RecipeBook()
        self.show_recipes_overlay  = False
        self.slider_speeds = {"temperature": 0.62, "caffeine": 0.74, "sweetness": 0.86}
        self._reset_sliders()

    # ------------------------------------------------------------------ assets

    def _load_ui_images(self):
        """Load fullscreen audio-menu background."""
        bg_path = os.path.join(self.ui_dir, "audio_menu_bg.png")
        self.audio_bg_img = None
        if os.path.exists(bg_path):
            try:
                loaded = pygame.image.load(bg_path).convert_alpha()
                self.audio_bg_img = pygame.transform.smoothscale(loaded, (self.WIDTH, self.HEIGHT))
            except Exception as e:
                print(f"[UI] Error loading audio_menu_bg.png: {e}")

    def _load_drink_images(self):
        """Load a PNG for every drink in the menu."""
        for name in DRINK_MENU:
            fn = name.lower().replace(" ", "_") + ".png"
            try:
                self.drink_images[name] = pygame.image.load(os.path.join(self.drink_dir, fn)).convert_alpha()
            except (pygame.error, FileNotFoundError):
                self.drink_images[name] = None

    # ------------------------------------------------------------------ fonts

    def _find_font(self, preferred_names):
        """Search assets/fonts then system fonts for a preferred typeface."""
        if os.path.isdir(self.font_dir):
            for root, _, files in os.walk(self.font_dir):
                for f in files:
                    if f.lower().endswith((".ttf", ".otf")) and any(w.lower() in f.lower() for w in preferred_names):
                        return os.path.join(root, f)
        for name in preferred_names:
            try:
                p = pygame.font.match_font(name)
                if p: return p
            except Exception: pass
        return None

    def _create_fonts(self):
        pygame.font.init()
        cyber = self._find_font(["audiowide", "orbitron", "oxanium", "rajdhani", "neuropol"])
        clean = self._find_font(["rajdhani", "segoe", "bahnschrift", "trebuchet", "verdana"])
        f = lambda path, sz, b=True: pygame.font.Font(path, sz) if path else pygame.font.SysFont("Arial", sz, bold=b)

        self.font_title     = f(cyber, 18)
        self.font_big_title = f(cyber, 19)
        self.font_menu      = f(cyber, 10)
        self.font_button    = f(cyber, 12)
        self.font_hud       = f(cyber, 12)
        self.font_cup_title = f(cyber, 16)
        self.font_category  = f(clean, 13)
        self.font_small     = f(clean, 10)
        self.font_medium    = f(clean, 13)
        self.font_close     = pygame.font.SysFont("consolas,couriernew,lucidaconsole,monospace", 17, bold=True)
        self.font_hint      = pygame.font.SysFont("consolas,couriernew,lucidaconsole,monospace", 12, bold=True)

    # ------------------------------------------------------------------ layout

    def _create_layout(self):
        """Define all Rect positions for panels, buttons and sliders."""
        self.hud_rect = pygame.Rect(8, 4, 730, 52)

        # Top-bar navigation buttons
        # Keep MENU for the existing settings/pause feature and add a separate
        # RECIPES button for the new read-only recipe book.
        self.menu_button        = pygame.Rect(750,  6, 90, 44)
        self.recipes_button     = pygame.Rect(845, 6, 110, 44)
        self.map_button         = pygame.Rect(960, 6, 100, 44)
        self.leaderboard_button = pygame.Rect(1065, 6, 155, 44)
        self.recipes_overlay = self.recipe_book.panel
        self.recipes_close_button = self.recipe_book.close_button

        # Drink-selection menu row
        self.menu_rect  = pygame.Rect(440, 72, 840, 177)
        self.menu_slots = [
            (drink, pygame.Rect(452 + i * 92, 84, 92, 155))
            for i, drink in enumerate(DRINK_MENU)
        ]

        # Customise panel + animated sliders
        self.customise_rect = pygame.Rect(502, 390, 370, 300)
        tx, tw = self.customise_rect.x + 25, self.customise_rect.width - 50
        params_y = (("temperature", 475), ("caffeine", 550), ("sweetness", 625))
        self.slider_tracks   = {p: pygame.Rect(tx, y, tw, 12) for p, y in params_y}
        self.slider_hitboxes = {p: pygame.Rect(tx - 12, y - 23, tw + 24, 48) for p, y in params_y}

        # Blender panel (increased horizontal width by 10%: 237 -> 261)
        self.blender_rect     = pygame.Rect(872,  390, 261, 300)
        self.blender_jug_rect = pygame.Rect(self.blender_rect.centerx - 87, 465, 174, 130)
        self.blend_button     = pygame.Rect(self.blender_rect.centerx - 107, 632, 215, 48)

        # Cup-preview / serve panel (increased horizontal width by 10%: 134 -> 147)
        self.preview_rect       = pygame.Rect(1133, 390, 147, 300)
        self.preview_image_rect = pygame.Rect(self.preview_rect.centerx - 64, 445, 129, 140)
        self.serve_button       = pygame.Rect(self.preview_rect.centerx - 63, 632, 127, 48)

        # Pause/settings overlay modal
        mw, mh = 700, 590
        self.overlay_rect      = pygame.Rect((self.WIDTH - mw) // 2, (self.HEIGHT - mh) // 2 - 40, mw, mh)
        self.close_overlay_btn = pygame.Rect((self.WIDTH - 250) // 2, self.overlay_rect.bottom + 22, 250, 42)
        self.audio.set_layout(self.overlay_rect)
        self.resume_menu_btn  = pygame.Rect(self.overlay_rect.x + 80,  self.overlay_rect.y + 410, 250, 48)
        self.exit_menu_btn    = pygame.Rect(self.overlay_rect.x + 370, self.overlay_rect.y + 410, 250, 48)
        self.return_start_btn = pygame.Rect(self.overlay_rect.x + 80,  self.overlay_rect.y + 472, 540, 48)

    # ------------------------------------------------------------------ audio proxy
    # Other modules still reference these names directly on the station object.

    def register_sfx_sound(self, sound_obj): self.audio.register_sfx_sound(sound_obj)
    def get_effective_sfx_volume(self):      return self.audio.get_effective_sfx_volume()

    @property
    def music_volume(self): return self.audio.music_volume
    @music_volume.setter
    def music_volume(self, v): self.audio.music_volume = v; self.audio.apply_volumes()

    @property
    def sfx_volume(self): return self.audio.sfx_volume
    @sfx_volume.setter
    def sfx_volume(self, v): self.audio.sfx_volume = v; self.audio.apply_volumes()

    @property
    def music_muted(self): return self.audio.music_muted
    @music_muted.setter
    def music_muted(self, v): self.audio.music_muted = bool(v); self.audio.apply_volumes()

    @property
    def sfx_muted(self): return self.audio.sfx_muted
    @sfx_muted.setter
    def sfx_muted(self, v): self.audio.sfx_muted = bool(v); self.audio.apply_volumes()

    # ------------------------------------------------------------------ setters

    def set_barista(self, barista):
        self.barista = barista if barista in ("Ryu", "Kira", "Jax") else "Ryu"
        self.blend_duration = self._prep_duration(0.7)

    def set_level(self, level):
        try: self.level = max(1, int(level))
        except (TypeError, ValueError): self.level = 1

    def set_progression(self, progression):
        self.progression = progression
        if progression is not None:
            self.set_level(getattr(progression, "level", self.level))

    def set_rewards(self, rewards):   self.rewards = rewards
    def set_economy(self, economy):   self.economy = economy

    def set_reward_feedback(self, xp_delta=0, credit_delta=0):
        try: self.last_xp_change = int(xp_delta)
        except (TypeError, ValueError): self.last_xp_change = 0
        try: self.last_credit_change = int(credit_delta)
        except (TypeError, ValueError): self.last_credit_change = 0
        self.reward_feedback_until = time.monotonic() + 2.5

    def set_order(self, order):
        self.customer_order = order
        self.game_state.set_order(order)
        self.player_drink.reset()
        self._reset_sliders()
        self.served = False
        self._sync_legacy_values()

    set_customer_order = set_order

    # ------------------------------------------------------------------ request flags
    # Callers poll these once per frame via consume_*_request().

    def _consume(self, attr):
        val = getattr(self, attr)
        setattr(self, attr, False)
        return val

    def consume_menu_request(self):        return self._consume("menu_requested")
    def consume_map_request(self):         return self._consume("map_requested")
    def consume_leaderboard_request(self): return self._consume("leaderboard_requested")
    def consume_exit_request(self):        return self._consume("exit_requested")
    def consume_return_start_request(self):return self._consume("return_start_requested")

    # ------------------------------------------------------------------ legacy bridge

    def _attach_legacy_bridge(self):
        if self.drink is not None:
            try: self.drink.get_data = self.get_player_drink_data
            except Exception: pass

    def _sync_legacy_values(self):
        """Keep the optional legacy drink object in sync with player_drink."""
        if self.drink is None: return
        maps = {
            "temperature": {"Cold": 25, "Normal": 50, "Hot": 75},
            "caffeine":    {"Low": 25,  "Normal": 50, "High": 75},
            "sweetness":   {"Less": 25, "Normal": 50, "Extra": 75},
        }
        try:
            for k, m in maps.items():
                setattr(self.drink, k, m.get(getattr(self.player_drink, k), 50))
        except Exception: pass

    def get_player_drink_data(self): return self.game_state.get_player_drink_data()
    get_data = get_player_drink_data

    # ------------------------------------------------------------------ barista helpers

    def _prep_multiplier(self):
        return 1.20 if self.barista == "Kira" else 1.0

    def _prep_duration(self, duration):
        return float(duration) / self._prep_multiplier()

    # ------------------------------------------------------------------ sliders

    def _reset_sliders(self):
        self.slider_positions  = {"temperature": 0.08, "caffeine": 0.50, "sweetness": 0.92}
        self.slider_directions = {"temperature": 1.0,  "caffeine": -1.0, "sweetness": 1.0}
        self.slider_locked     = {k: False  for k in self.slider_positions}
        self.slider_results    = {k: None   for k in self.slider_positions}
        self.slider_feedback   = {k: "CLICK" for k in self.slider_positions}

    def _slider_option_from_position(self, parameter):
        opts = {"temperature": TEMPERATURE_OPTIONS, "caffeine": CAFFEINE_OPTIONS, "sweetness": SWEETNESS_OPTIONS}[parameter]
        pos  = self.slider_positions[parameter]
        idx  = min(range(3), key=lambda i: abs(pos - (0.08, 0.50, 0.92)[i]))
        return opts[idx], abs(pos - (0.08, 0.50, 0.92)[idx])

    def _unlock_slider(self, parameter):
        self.slider_locked[parameter]   = False
        self.slider_results[parameter]  = None
        self.slider_feedback[parameter] = "ADJUSTING"
        setattr(self.player_drink, parameter, None)
        setattr(self.game_state, f"selected_{parameter}", None)
        self.game_state.state = GameState.CUSTOMISE
        self._sync_legacy_values()

    def _lock_slider(self, parameter):
        if not self.game_state.can_customize(): return
        val, _ = self._slider_option_from_position(parameter)
        if not getattr(self.game_state, f"select_{parameter}")(val): return
        setattr(self.player_drink, parameter, val)
        self.slider_locked[parameter] = True
        target  = getattr(self.customer_order, parameter, None) if self.customer_order else None
        correct = target is not None and val == target
        self.slider_results[parameter]  = correct
        self.slider_feedback[parameter] = "CORRECT" if correct else "WRONG"
        self._sync_legacy_values()

    def _change_selected_drink(self, drink_name):
        self.player_drink.drink_name = drink_name
        self.game_state.selected_drink = drink_name
        for f in ("temperature", "caffeine", "sweetness"):
            setattr(self.player_drink, f, None)
            setattr(self.game_state, f"selected_{f}", None)
        self.game_state.blend_finished = self.game_state.served = self.served = self.liquid_unlocked = False
        self.game_state.state = GameState.CUSTOMISE
        self.assembly_phase = "empty"
        self._reset_sliders()
        self.challenge.start_challenge(drink_name)
        self._sync_legacy_values()

    # ------------------------------------------------------------------ update

    def update(self, dt=0.0):
        now = time.monotonic()
        dt  = max(0.0, min(dt or (now - self._last_time), 0.1))
        self._last_time = now

        self._update_hover_sound()

        if self.show_menu_overlay:
            self.audio.update_drag(pygame.mouse.get_pos()[0])
            return   # Pause all gameplay while overlay is open

        if self.game_state.can_customize() and self.player_drink.drink_name:
            for p, pos in self.slider_positions.items():
                if self.slider_locked[p]: continue
                nxt = pos + self.slider_speeds[p] * self._prep_multiplier() * self.slider_directions[p] * dt
                if nxt >= 1.0:   nxt, self.slider_directions[p] = 1.0, -1.0
                elif nxt <= 0.0: nxt, self.slider_directions[p] = 0.0,  1.0
                self.slider_positions[p] = nxt

        self.challenge.update(dt)
        if self.challenge.done:
            self.liquid_unlocked = True
        self._update_blending()
        self._update_assembly()

    def _update_blending(self):
        if self.game_state.state != GameState.BLENDING: return
        el = time.monotonic() - self.blend_start_time
        self.blender_angle = (el * 720) % 360
        self.blender_pulse = math.sin(el * 10) * 0.5 + 0.5
        if el >= self.blend_duration and self.assembly_phase == "empty":
            self.assembly_phase, self.assembly_started = "ice", time.monotonic()

    def _update_assembly(self):
        """Sequence cup through ice → pour → topping → ready."""
        if self.assembly_phase == "empty": return
        elapsed = time.monotonic() - self.assembly_started
        phases  = (("ice", self._prep_duration(0.4)), ("pour", self._prep_duration(0.4)), ("topping", self._prep_duration(0.4)))
        tot = 0.0
        for name, dur in phases:
            if elapsed < tot + dur:
                self.assembly_phase = name
                return
            tot += dur
        self.assembly_phase = "ready"
        if self.game_state.state == GameState.BLENDING:
            self.game_state.finish_blending()
            self.audio.stop_sfx("blender", 150)
            self._sync_legacy_values()

    # ------------------------------------------------------------------ hover / click sounds

    def _interactive_targets(self):
        """(key, rect) pairs the mouse can hover or click right now (for sounds)."""
        if self.show_recipes_overlay or self.recipe_book.is_open:
            return []
        if self.show_menu_overlay:
            return [
                ("resume", self.resume_menu_btn), ("exit", self.exit_menu_btn),
                ("return", self.return_start_btn), ("close", self.close_overlay_btn),
                ("mute_music", self.audio.music_mute_btn), ("mute_sfx", self.audio.sfx_mute_btn),
            ]
        if self.challenge.active:
            return []
        targets = [("recipes", self.recipes_button), ("menu", self.menu_button),
                   ("map", self.map_button), ("leaderboard", self.leaderboard_button)]
        for drink_name, rect in self.menu_slots:
            if is_valid_drink(drink_name) and is_drink_unlocked(drink_name, self.level):
                targets.append((f"drink:{drink_name}", rect))
        if self.game_state.state in (GameState.CUSTOMISE, GameState.READY_TO_BLEND):
            targets += [(f"slider:{p}", r) for p, r in self.slider_hitboxes.items()]
        targets += [("blend", self.blend_button), ("serve", self.serve_button)]
        return targets

    def _target_at(self, pos):
        for key, rect in self._interactive_targets():
            if rect.collidepoint(pos):
                return key
        return None

    def _update_hover_sound(self):
        self.audio.update_hover(self._target_at(pygame.mouse.get_pos()))

    # ------------------------------------------------------------------ events

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                self.show_menu_overlay = not self.show_menu_overlay; return
            elif event.key == pygame.K_m and not self.show_menu_overlay:
                self.map_requested = True; return
            elif event.key == pygame.K_l and not self.show_menu_overlay:
                self.leaderboard_requested = True; return

        if self.show_recipes_overlay or self.recipe_book.is_open:
            if self.recipe_book.handle_event(event, self.level):
                self.show_recipes_overlay = self.recipe_book.is_open
                return
            if not self.recipe_book.is_open:
                self.show_recipes_overlay = False
                return
            return

        if self.show_menu_overlay:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = event.pos
                if self._target_at(mouse):
                    self.audio.play_click()
                if   self.resume_menu_btn.collidepoint(mouse):  self.show_menu_overlay = False
                elif self.exit_menu_btn.collidepoint(mouse):    self.show_menu_overlay = False; self.exit_requested = True
                elif self.return_start_btn.collidepoint(mouse): self.show_menu_overlay = False; self.return_start_requested = True
                elif self.close_overlay_btn.collidepoint(mouse):self.show_menu_overlay = False
                elif self.audio.handle_mouse_down(mouse): pass
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.audio.handle_mouse_up()
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1: return
        mouse = event.pos

        if self.challenge.active:
            self.challenge.handle_event(event); return

        if self._target_at(mouse):
            self.audio.play_click()

        if   self.recipes_button.collidepoint(mouse):
            self.recipe_book.open()
            self.show_recipes_overlay = True
            return
        elif self.menu_button.collidepoint(mouse):        self.show_menu_overlay = True; return
        elif self.map_button.collidepoint(mouse):         self.map_requested = True; return
        elif self.leaderboard_button.collidepoint(mouse): self.leaderboard_requested = True; return

        for drink_name, rect in self.menu_slots:
            if rect.collidepoint(mouse):
                if is_valid_drink(drink_name) and is_drink_unlocked(drink_name, self.level):
                    if self.game_state.state not in (GameState.BLENDING, GameState.READY_TO_SERVE, GameState.SERVED):
                        self._change_selected_drink(drink_name)
                return

        if self.game_state.state in (GameState.CUSTOMISE, GameState.READY_TO_BLEND):
            for param, rect in self.slider_hitboxes.items():
                if rect.collidepoint(mouse):
                    (self._unlock_slider if self.slider_locked[param] else self._lock_slider)(param)
                    return

        if self.blend_button.collidepoint(mouse):
            if self.challenge.done: self.liquid_unlocked = True
            if self.liquid_unlocked and self.game_state.start_blending():
                self.blend_start_time, self.blender_angle = time.monotonic(), 0.0
                self.audio.play_sfx("blender")
            return

        if self.serve_button.collidepoint(mouse) and self.game_state.serve():
            self.served = True
            self._sync_legacy_values()

    # ------------------------------------------------------------------ draw

    def draw(self, screen):
        """Render the full mixing station UI."""
        self._draw_hud(screen)
        self._draw_menu(screen)
        self._draw_customise(screen)
        self._draw_blender(screen)
        self._draw_preview(screen)
        self.challenge.draw(screen)
        if self.show_menu_overlay:
            self._draw_audio_menu_overlay(screen)
        if self.show_recipes_overlay or self.recipe_book.is_open:
            self.recipe_book.draw(screen, self.level)

    def _draw_hud(self, screen):
        if self.show_menu_overlay: return
        self._action_button(screen, self.menu_button,        "MENU  [F]",         self.YELLOW, True, large=False)
        self._action_button(screen, self.recipes_button,     "RECIPES",            self.CYAN,   True, large=False, active=(self.show_recipes_overlay or self.recipe_book.is_open))
        self._action_button(screen, self.map_button,         "MAP  [M]",           self.CYAN,   True, large=False)
        self._action_button(screen, self.leaderboard_button, "LEADERBOARD  [L]",   self.PINK,   True, large=False)

    def _draw_audio_menu_overlay(self, screen):
        """Full-screen pause/settings overlay with audio controls and menu actions."""
        # Background: custom image or dark fallback
        if self.audio_bg_img:
            screen.blit(self.audio_bg_img, (0, 0))
            dim = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            dim.fill((2, 4, 12, 110))
            screen.blit(dim, (0, 0))
        else:
            dark = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            dark.fill((2, 4, 12, 220))
            screen.blit(dark, (0, 0))

        self._panel(screen, self.overlay_rect, self.PINK, (7, 12, 32, 245), radius=20, width=2)
        self.audio.draw(screen, self)

        self._action_button(screen, self.resume_menu_btn,  "RESUME GAME",            self.CYAN, True, large=False)
        self._action_button(screen, self.exit_menu_btn,    "EXIT TO DESKTOP",         self.PINK, True, large=False)
        self._action_button(screen, self.return_start_btn, "RETURN TO START SCREEN",  self.CYAN, True, large=False)

        pygame.draw.line(screen, (35, 50, 85),
            (self.overlay_rect.x + 40, self.overlay_rect.bottom - 55),
            (self.overlay_rect.right - 40, self.overlay_rect.bottom - 55), 1)
        tag = self.font_small.render("RESUME OR EXIT  •  USE MENU BUTTON", True, self.CYAN_LIGHT)
        screen.blit(tag, tag.get_rect(center=(self.overlay_rect.centerx, self.overlay_rect.bottom - 30)))

        # Close button + hint text
        self._action_button(screen, self.close_overlay_btn, "CLOSE  [F / ESC]", self.PINK, True, large=False)
        hint = self.font_hint.render("ADJUST VOLUME BASED ON YOUR PREFERENCE", True, self.MUTED)
        screen.blit(hint, hint.get_rect(center=(self.close_overlay_btn.centerx, self.close_overlay_btn.bottom + 22)))

    # ------------------------------------------------------------------ menu panel

    def _draw_menu(self, screen):
        """Drink selection row at the top of the station."""
        self._panel(screen, self.menu_rect, self.CYAN, self.PANEL)
        title = self.font_title.render("CYBERPUNK DRINK MENU", True, self.CYAN_LIGHT)
        screen.blit(title, title.get_rect(center=(self.menu_rect.centerx, 99)))

        for drink_name, rect in self.menu_slots:
            unlocked = is_drink_unlocked(drink_name, self.level)
            selected = self.player_drink.drink_name == drink_name
            border = self.PINK_LIGHT if selected else (self.CYAN if unlocked else self.LOCKED)
            fill   = self.BUTTON_SELECTED if selected else (self.BUTTON if unlocked else (6, 9, 22, 135))
            self._panel(screen, rect, border, fill, radius=12, width=1)

            img = self.drink_images.get(drink_name)
            if img: self._image_fit(screen, img, pygame.Rect(rect.x + 6, rect.y + 7, rect.width - 12, 130), unlocked)
            if not unlocked: self._draw_lock(screen, rect.centerx, rect.y + 74)
            self._draw_drink_name(screen, drink_name, rect, unlocked)

    def _draw_drink_name(self, screen, drink_name, rect, unlocked):
        col = self.WHITE if unlocked else self.LOCKED
        if drink_name in self.SPLIT_NAMES:
            l1, l2 = self.SPLIT_NAMES[drink_name]
            for text, cy in ((l1, rect.bottom - 24), (l2, rect.bottom - 11)):
                s = self.font_menu.render(text, True, col)
                screen.blit(s, s.get_rect(center=(rect.centerx, cy)))
        else:
            t = self.font_menu.render(drink_name.upper(), True, col)
            screen.blit(t, t.get_rect(center=(rect.centerx, rect.bottom - 14)))

    # ------------------------------------------------------------------ customise panel

    def _draw_customise(self, screen):
        """Animated slider panel for temperature, caffeine and sweetness."""
        self._panel(screen, self.customise_rect, self.CYAN, (6, 12, 29, 190), radius=14, width=2)
        t = self.font_big_title.render("CUSTOMISE YOUR DRINK", True, self.CYAN_LIGHT)
        screen.blit(t, t.get_rect(center=(self.customise_rect.centerx, 420)))
        sub = self.font_small.render("CLICK WHEN THE INDICATOR HITS THE CORRECT ZONE!", True, self.SOFT_WHITE)
        screen.blit(sub, sub.get_rect(center=(self.customise_rect.centerx, 444)))

        self._draw_timing_slider(screen, "temperature", "TEMPERATURE",    TEMPERATURE_OPTIONS, self.CYAN)
        self._draw_timing_slider(screen, "caffeine",    "CAFFEINE LEVEL", CAFFEINE_OPTIONS,    self.YELLOW)
        self._draw_timing_slider(screen, "sweetness",   "SWEETNESS LEVEL",SWEETNESS_OPTIONS,   self.PINK_LIGHT)

    def _draw_timing_slider(self, screen, param, label, options, accent):
        track = self.slider_tracks[param]
        screen.blit(self.font_category.render(label, True, accent), (track.x, track.y - 26))

        glow = pygame.Surface((track.width + 4, track.height + 4), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*accent, 70), glow.get_rect(), border_radius=8)
        screen.blit(glow, (track.x - 2, track.y - 2))

        pygame.draw.rect(screen, (15, 24, 48), track, border_radius=6)
        pygame.draw.rect(screen, accent, track, width=2, border_radius=6)

        centers = (0.08, 0.50, 0.92)
        zw = max(34, int(track.width * 0.16))
        for idx, opt in enumerate(options):
            cx = int(track.x + track.width * centers[idx])
            pygame.draw.rect(screen, (*accent, 28), pygame.Rect(cx - zw // 2, track.y - 5, zw, track.height + 10), border_radius=7)
            pygame.draw.line(screen, (105, 120, 150), (cx, track.y - 5), (cx, track.bottom + 5), 1)
            t = self.font_small.render(opt.upper(), True, self.WHITE)
            screen.blit(t, t.get_rect(center=(cx, track.bottom + 18)))

        ix = int(track.x + track.width * self.slider_positions[param])
        pygame.draw.circle(screen, (0, 0, 0), (ix, track.centery), 9)
        pygame.draw.circle(screen, accent,     (ix, track.centery), 7)
        pygame.draw.circle(screen, self.WHITE, (ix, track.centery), 2)
        if self.slider_locked[param]:
            pygame.draw.circle(screen, self.WHITE, (ix, track.centery), 11, width=2)

        res, locked = self.slider_results[param], self.slider_locked[param]
        if   locked and res is True:                        fb, col = "✓ LOCKED",  self.GREEN
        elif locked and res is False:                        fb, col = "✕ WRONG",   self.PINK_LIGHT
        elif self.slider_feedback[param] == "ADJUSTING":    fb, col = "ADJUSTING", self.CYAN_LIGHT
        else:                                                fb, col = "CLICK",     self.MUTED

        fbt = self.font_small.render(fb, True, col)
        screen.blit(fbt, (track.right - fbt.get_width(), track.y - 26))

    # ------------------------------------------------------------------ blender panel

    def _draw_ingredient(self, screen, kind, x, y):
        """Draw a single pixel ingredient icon inside the blender jug."""
        if   kind == "milk":      pygame.draw.ellipse(screen, (240,248,255),(x-16,y-10,32,20))
        elif kind == "coffee":    pygame.draw.circle(screen, (105,65,45),(x,y),12)
        elif kind == "chocolate": pygame.draw.rect(screen,(90,55,45),(x-12,y-9,24,18),border_radius=4)
        elif kind == "syrup":     pygame.draw.line(screen,(225,135,90),(x-10,y-8),(x+10,y+8),5)
        elif kind == "mint":      pygame.draw.ellipse(screen,(90,235,165),(x-7,y-14,15,23))
        elif kind == "cookie":    pygame.draw.circle(screen,(205,140,80),(x,y),12)
        elif kind == "caramel":   pygame.draw.line(screen,(240,175,85),(x-12,y),(x+12,y),5)
        elif kind == "matcha":    pygame.draw.circle(screen,(165,195,105),(x,y),12)
        elif kind == "battery":   pygame.draw.rect(screen,(120,220,255),(x-11,y-14,22,28),border_radius=4)
        elif kind == "orb":       pygame.draw.circle(screen,(210,150,255),(x,y),12)
        elif kind == "ice":       pygame.draw.rect(screen,(190,235,255),(x-9,y-9,18,18),border_radius=4)
        elif kind == "star":
            pts = [(x+math.cos(-math.pi/2+i*math.pi/2.5)*13, y+math.sin(-math.pi/2+i*math.pi/2.5)*13) for i in range(5)]
            pygame.draw.polygon(screen,(255,225,110),pts)
        elif kind == "spice":  pygame.draw.circle(screen,(235,155,95),(x,y),10)
        elif kind == "water":  pygame.draw.circle(screen,(130,205,255),(x,y),11)
        elif kind == "meteor": pygame.draw.polygon(screen,(220,235,250),[(x-13,y),(x+10,y-7),(x+6,y+9)])

    def _draw_blender(self, screen):
        """Animated blender jug with liquid fill, spin blades and ingredient pour."""
        self._panel(screen, self.blender_rect, self.PURPLE, (6, 10, 27, 145))
        t = self.font_big_title.render("BLENDER", True, self.CYAN_LIGHT)
        screen.blit(t, t.get_rect(center=(self.blender_rect.centerx, self.blender_rect.y + 22)))

        jug = self.blender_jug_rect.copy()
        is_blending = self.game_state.state == GameState.BLENDING

        if is_blending:
            jug.x += int(math.sin(time.monotonic() * 30) * 2)
            jug.y += int(math.cos(time.monotonic() * 25))
            glow = pygame.Surface((jug.width + 28, jug.height + 28), pygame.SRCALPHA)
            pygame.draw.rect(glow, (75, 225, 255, int(30 + self.blender_pulse * 40)), glow.get_rect(), border_radius=25, width=5)
            screen.blit(glow, (jug.x - 14, jug.y - 14))

        pygame.draw.rect(screen, (17, 25, 52),     jug, border_radius=23)
        pygame.draw.rect(screen, self.CYAN_LIGHT,  jug, width=2, border_radius=23)

        lid = pygame.Rect(jug.x + 24, jug.y - 8, jug.width - 48, 18)
        pygame.draw.rect(screen, (20, 24, 48),   lid, border_radius=8)
        pygame.draw.rect(screen, self.PINK_LIGHT, lid, width=2, border_radius=8)

        inner  = pygame.Rect(jug.x + 11, jug.y + 13, jug.width - 22, jug.height - 28)
        handle = pygame.Rect(jug.right - 2, jug.y + 28, 22, 52)
        pygame.draw.rect(screen, (7, 12, 28), inner,  border_radius=17)
        pygame.draw.rect(screen, (18, 25, 52), handle, border_radius=13)
        pygame.draw.rect(screen, self.CYAN,    handle, width=2, border_radius=13)

        drink_name = self.player_drink.drink_name
        if is_blending and drink_name:
            recipe = get_recipe(drink_name)
            col = recipe.liquid_color if recipe else (150, 150, 255)
            if time.monotonic() - self.blend_start_time < 0.55:
                pygame.draw.line(screen, col, (jug.centerx, jug.y - 20), (jug.centerx, jug.y + 28), 8)
                pygame.draw.circle(screen, self.WHITE, (jug.centerx, jug.y + 30), 4)
            ingredients = self._INGREDIENTS.get(drink_name, ["milk"])
            elapsed = time.monotonic() - self.blend_start_time
            for i, kind in enumerate(ingredients):
                te = elapsed - i * 0.28
                if 0 <= te <= 0.7:
                    x = jug.centerx + (i - (len(ingredients) - 1) / 2) * 30
                    y = jug.y - 15 + min(75, te * 150)
                    self._draw_ingredient(screen, kind, int(x), int(y))

        if drink_name and (self.liquid_unlocked or is_blending):
            recipe = get_recipe(drink_name)
            col = recipe.liquid_color if recipe else (150, 150, 255)
            if drink_name == "Hologram Frappe" and is_blending:
                cyc = time.monotonic() * 3
                col = (
                    int(180 + 55 * (math.sin(cyc) + 1) / 2),
                    int(150 + 80 * (math.sin(cyc + 2) + 1) / 2),
                    int(200 + 55 * (math.sin(cyc + 4) + 1) / 2),
                )
            lh = inner.height - 22 + (int(math.sin(time.monotonic() * 12) * 4) if is_blending else 0)
            liquid = pygame.Rect(inner.x + 4, inner.bottom - lh - 4, inner.width - 8, lh)
            pygame.draw.rect(screen, col, liquid, border_radius=14)
            hcol = (min(255, col[0] + 45), min(255, col[1] + 45), min(255, col[2] + 45))
            pygame.draw.rect(screen, hcol, pygame.Rect(liquid.x + 7, liquid.y + 6, liquid.width - 14, 6), border_radius=4)
            shimmer_y = int(liquid.y + liquid.height * (0.35 + 0.12 * math.sin(time.monotonic() * 2.5)))
            pygame.draw.line(screen, (255, 255, 255, 110), (liquid.x + 12, shimmer_y), (liquid.right - 12, shimmer_y), 1)

            if is_blending:
                pts = [
                    (int(liquid.x + 11 + idx * ((liquid.width - 22) / 8)),
                     int(liquid.y + 25 + math.sin(time.monotonic() * 8 + idx) * 5))
                    for idx in range(9)
                ]
                pygame.draw.lines(screen, self.WHITE, False, pts, 2)
                now = time.monotonic()
                for idx in range(6):
                    ph = now * (1.5 + idx * 0.18) + idx
                    bx = liquid.x + 20 + (idx * 19) % max(20, liquid.width - 30)
                    by = liquid.bottom - 15 - (ph * 32) % max(20, liquid.height - 20)
                    pygame.draw.circle(screen, (240, 250, 255), (int(bx), int(by)), 3)
        else:
            txt = self.font_small.render("COMPLETE INGREDIENT CHALLENGE", True, self.MUTED)
            screen.blit(txt, txt.get_rect(center=inner.center))

        core_x, core_y = jug.centerx, jug.bottom - 20
        pygame.draw.circle(screen, (12, 17, 35), (core_x, core_y), 11)
        pygame.draw.circle(screen, self.PINK,    (core_x, core_y), 3)
        if is_blending:
            angle = math.radians(self.blender_angle)
            for off in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
                ex = core_x + math.cos(angle + off) * 25
                ey = core_y + math.sin(angle + off) * 25
                pygame.draw.line(screen, self.CYAN_LIGHT, (core_x, core_y), (int(ex), int(ey)), 3)

        base = pygame.Rect(jug.x - 10, jug.bottom - 2, jug.width + 20, 22)
        pygame.draw.rect(screen, (22, 18, 40), base, border_radius=10)
        pygame.draw.rect(screen, self.PINK,    base, width=1, border_radius=10)

        if is_blending:
            ratio = max(0, min(1, (time.monotonic() - self.blend_start_time) / self.blend_duration))
            pr = pygame.Rect(self.blend_button.x + 8, self.blend_button.y - 8, self.blend_button.width - 16, 4)
            pygame.draw.rect(screen, (20, 25, 45), pr, border_radius=2)
            pygame.draw.rect(screen, self.CYAN, pygame.Rect(pr.x, pr.y, int(pr.width * ratio), pr.height), border_radius=2)

        self._action_button(
            screen, self.blend_button,
            "BLENDING..." if is_blending else "BLEND",
            self.PINK,
            self.game_state.can_blend() and self.liquid_unlocked and self.assembly_phase == "empty",
            large=True,
        )

    # ------------------------------------------------------------------ preview / cup panel

    def _draw_preview(self, screen):
        """Cup assembly preview and serve button."""
        self._panel(screen, self.preview_rect, self.PINK, (7, 10, 26, 150))
        t = self.font_cup_title.render("CUP STATION", True, self.PINK_LIGHT)
        screen.blit(t, t.get_rect(center=(self.preview_rect.centerx, 420)))
        self._draw_cup_sequence(screen)

        ready = self.game_state.state == GameState.READY_TO_SERVE and self.assembly_phase == "ready"
        label = "READY!" if ready else self.assembly_phase.upper()
        col   = self.GREEN if ready else self.CYAN_LIGHT
        txt   = self.font_small.render(label, True, col)
        screen.blit(txt, txt.get_rect(center=(self.preview_rect.centerx, 600)))
        self._action_button(screen, self.serve_button, "SERVE", self.CYAN, ready, large=False)

    def _draw_cup_sequence(self, screen):
        r     = pygame.Rect(self.preview_rect.centerx - 47, 455, 95, 125)
        cx    = r.centerx
        phase = self.assembly_phase

        # Cup outline (shared)
        cup_pts = [(r.x+7, r.y), (r.right-7, r.y), (r.right-16, r.bottom), (r.x+16, r.bottom)]

        if phase == "ready":
            img = self.drink_images.get(self.player_drink.drink_name)
            if img:
                self._image_fit(screen, img, self.preview_image_rect.inflate(-4, -4), True)
            else:
                pygame.draw.polygon(screen, (225, 235, 250), cup_pts)
                recipe = get_recipe(self.player_drink.drink_name)
                c = recipe.liquid_color if recipe else (150, 150, 255)
                pygame.draw.polygon(screen, c, [(r.x+16, r.y+45), (r.right-16, r.y+45), (r.right-22, r.bottom-10), (r.x+22, r.bottom-10)])
            return

        pygame.draw.polygon(screen, (225, 235, 250), cup_pts)
        pygame.draw.polygon(screen, (35, 45, 70), [(r.x+12, r.y+8), (r.right-12, r.y+8), (r.right-20, r.bottom-12), (r.x+20, r.bottom-12)])

        if phase in ("ice", "pour", "topping"):
            for i in range(5):
                pygame.draw.rect(screen, (205, 235, 250), (r.x + 20 + (i % 2) * 28, r.y + 18 + (i // 2) * 24, 15, 12), border_radius=3)

        if phase in ("pour", "topping") and self.player_drink.drink_name:
            recipe = get_recipe(self.player_drink.drink_name)
            c = recipe.liquid_color if recipe else (150, 150, 255)
            pygame.draw.polygon(screen, c, [(r.x+16, r.y+45), (r.right-16, r.y+45), (r.right-22, r.bottom-10), (r.x+22, r.bottom-10)])
            if phase == "pour":
                pygame.draw.line(screen, c, (cx, 425), (cx, r.y + 45), 8)

        if phase == "topping":
            self._draw_toppings(screen, cx, r.y + 42)

        if phase == "ice":
            crusher = pygame.Rect(r.x - 5, r.y - 28, r.width + 10, 18)
            pygame.draw.rect(screen, (25, 35, 60), crusher, border_radius=6)
            pygame.draw.rect(screen, self.CYAN, crusher, 2, border_radius=6)
            yy = int(r.y - 8 + math.sin(time.monotonic() * 12) * 6)
            pygame.draw.line(screen, self.PINK, (cx, yy), (cx, r.y + 10), 5)

    def _draw_toppings(self, screen, cx, y):
        toppings = get_recipe(self.player_drink.drink_name).toppings if self.player_drink.drink_name else ()
        for i, t in enumerate(toppings[:3]):
            x = cx + (i - 1) * 18
            if   "mint"      in t: pygame.draw.ellipse(screen, (90, 235, 165),   (x-8, y-8, 16, 16))
            elif "chocolate" in t or "cookie" in t: pygame.draw.circle(screen, (90, 55, 45), (x, y), 7)
            elif "caramel"   in t: pygame.draw.line(screen, (235, 170, 80), (x-8, y-5), (x+8, y+5), 4)
            elif "meteor"    in t: pygame.draw.polygon(screen, (210, 230, 250), [(x-7,y),(x+5,y-6),(x+8,y+6)])
            else:                   pygame.draw.circle(screen, (245, 245, 255), (x, y), 8)

    # ------------------------------------------------------------------ primitives

    def _panel(self, screen, rect, border, fill, radius=14, width=2):
        """Draw a rounded, semi-transparent panel with a glowing border."""
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, fill, s.get_rect(), border_radius=radius)
        screen.blit(s, rect.topleft)
        pygame.draw.rect(screen, border, rect, width=width, border_radius=radius)

    def _action_button(self, screen, rect, text, accent, enabled, large=False, active=False):
        """Draw a cyberpunk-styled button with hover glow."""
        hover  = enabled and rect.collidepoint(pygame.mouse.get_pos())
        border = (self.PINK_LIGHT if hover else (self.CYAN_LIGHT if active else accent)) if enabled else (60, 65, 85)
        fill   = (25, 45, 85, 230) if active else ((45, 12, 52, 205) if enabled else (7, 10, 22, 160))
        col    = self.CYAN_LIGHT if active else (self.WHITE if enabled else self.MUTED)
        if hover or active:
            pygame.draw.rect(screen, (75, 235, 255) if active else (255, 100, 210), rect.inflate(4, 4), width=1, border_radius=13)
        self._panel(screen, rect, border, fill, radius=12, width=1)
        font = self.font_big_title if large else self.font_button
        lbl  = font.render(text, True, col)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    def _image_fit(self, screen, image, target, bright=True):
        """Scale-fit an image into target Rect, optionally dimming it."""
        if not image or target.width <= 0 or target.height <= 0: return
        w, h = image.get_size()
        if w <= 0 or h <= 0: return
        scale  = min(target.width / w, target.height / h)
        scaled = pygame.transform.smoothscale(image, (max(1, int(w * scale)), max(1, int(h * scale))))
        if not bright:
            scaled = scaled.copy()
            scaled.fill((70, 70, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(scaled, scaled.get_rect(center=target.center))

    def _draw_lock(self, screen, x, y):
        pygame.draw.rect(screen, self.LOCKED, pygame.Rect(x - 9, y, 18, 15), border_radius=4)
        pygame.draw.arc(screen, self.LOCKED, pygame.Rect(x - 6, y - 11, 12, 16), math.pi, 2 * math.pi, 2)
        pygame.draw.circle(screen, (25, 28, 45), (x, y + 7), 2)

    # ------------------------------------------------------------------ reset

    def reset(self):
        """Reset gameplay only — barista selection is preserved."""
        self.audio.stop_sfx("blender")
        self.player_drink.reset()
        self.game_state.reset()
        self._init_state()
        self._sync_legacy_values()
"""Compact ingredient-themed mini challenges for Cyberpunk Café."""
import math, random, time
import pygame

CHALLENGES = {
    "Neon Latte":      ("MILK DROP", "milk", "catch", (235,245,255)),
    "Milkyway":        ("STAR ALIGN", "star", "target", (190,180,255)),
    "Void Chai":       ("SPICE SWIRL", "spice", "orbit", (255,185,120)),
    "Cyber Fuel":      ("POWER CELLS", "battery", "sequence", (120,220,255)),
    "Hologram Frappe": ("HOLO MATCH", "orb", "match", (220,150,255)),
    "Pixel Lemint":    ("MINT CATCH", "mint", "catch", (120,245,190)),
    "Caramel Byte":    ("COOKIE STACK", "cookie", "stack", (220,155,90)),
    "Stardust Matcha": ("STAR BURST", "star", "burst", (210,225,120)),
    "Meteorite":       ("METEOR TAP", "meteor", "tap", (210,235,255)),
}

class MiniChallenge:
    """One reusable mini-game engine; each drink supplies a different mode."""
    def __init__(self):
        self.active = False; self.done = False; self.drink = None
        self.title = ""; self.icon = ""; self.mode = ""; self.accent = (75,225,255)
        self.strikes = 0; self.target = 3; self.start = 0.0; self.round = 0
        self.pos = [0,0]; self.goal = [0,0]; self.options = []; self.sequence = []
        self.flash = 0.0; self.message = ""; self.message_color = (245,248,255); self.done_at = 0.0
        self.area = pygame.Rect(310, 125, 660, 470)
        self.fonts = {}

    def _fonts(self):
        if self.fonts: return
        self.fonts = {
            "title": pygame.font.SysFont("Arial", 28, bold=True),
            "head": pygame.font.SysFont("Arial", 20, bold=True),
            "body": pygame.font.SysFont("Arial", 16, bold=True),
            "big": pygame.font.SysFont("Arial", 34, bold=True),
        }

    def start_challenge(self, drink):
        data = CHALLENGES.get(drink)
        if not data: return
        self._fonts(); self.drink = drink; self.title,self.icon,self.mode,self.accent = data
        self.active=True; self.done=False; self.strikes=0; self.round=0; self.start=time.monotonic()
        self.flash=0; self.message=""; self._new_round()

    def _new_round(self):
        self.round += 1; self.flash=0
        if self.mode == "catch":
            self.pos=[random.randint(390,890),180]
        elif self.mode in ("target","orbit"):
            self.goal=[random.randint(430,850),random.randint(250,470)]
        elif self.mode == "sequence":
            self.sequence=[random.randint(0,2) for _ in range(3)]; self.options=[]
        elif self.mode == "match":
            self.goal=[random.randint(430,850),random.randint(250,470)]
            self.pos=[random.randint(390,850),random.randint(250,470)]
        elif self.mode == "stack":
            self.pos=[random.randint(430,850),330]
        elif self.mode == "burst":
            self.options=[(random.randint(420,860),random.randint(240,470)) for _ in range(5)]
        elif self.mode == "tap":
            self.pos=[random.randint(430,850),random.randint(250,470)]

    def update(self, dt):
        if not self.active:
            if self.done and time.monotonic()-self.done_at > 0.9: self.done=False
            return
        now=time.monotonic(); self.flash=max(0,self.flash-dt)
        if self.mode == "catch":
            self.pos[1] += 170*dt
            if self.pos[1] > 500: self._miss()
        elif self.mode == "orbit":
            a=now*2.3; self.pos=[self.area.centerx+int(math.cos(a)*190), self.area.centery+int(math.sin(a)*135)]
        elif self.mode == "target":
            a=now*1.8; self.pos=[self.area.centerx+int(math.cos(a)*180), self.area.centery+int(math.sin(a)*115)]
        elif self.mode == "match":
            a=now*2; self.pos=[self.area.centerx+int(math.sin(a)*210), self.area.centery+int(math.cos(a*1.3)*125)]
        elif self.mode == "tap":
            a=now*1.7; self.pos=[self.area.centerx+int(math.cos(a)*205), self.area.centery+int(math.sin(a*1.4)*125)]

    def _hit(self, ok=True):
        if ok:
            self.strikes += 1; self.flash=.35; self.message="NICE!"; self.message_color=(90,235,165)
            if self.strikes >= self.target:
                self.active=False; self.done=True; self.done_at=time.monotonic(); self.message="LIQUID UNLOCKED!"
            else: self._new_round()
        else: self._miss()

    def _miss(self):
        self.flash=.25; self.message="MISS!"; self.message_color=(255,120,190); self._new_round()

    def handle_event(self,event):
        if not self.active or event.type != pygame.MOUSEBUTTONDOWN or event.button != 1: return False
        p=event.pos
        if not self.area.collidepoint(p): return True
        if self.mode in ("catch","target","orbit","match","tap"):
            r=42 if self.mode != "tap" else 48; self._hit(math.dist(p,self.pos)<=r)
        elif self.mode == "sequence":
            self._hit(self.area.collidepoint(p))
        elif self.mode == "stack":
            self._hit(abs(p[0]-self.pos[0])<70 and abs(p[1]-self.pos[1])<55)
        elif self.mode == "burst":
            hit=None
            for i,q in enumerate(self.options):
                if math.dist(p,q)<35: hit=i; break
            self._hit(hit is not None)
        return True

    def draw(self,screen):
        if not self.active and not self.done: return
        overlay=pygame.Surface(screen.get_size(),pygame.SRCALPHA); overlay.fill((3,6,20,205)); screen.blit(overlay,(0,0))
        pygame.draw.rect(screen,(9,15,38),self.area,border_radius=24)
        pygame.draw.rect(screen,self.accent,self.area,2,border_radius=24)
        f=self.fonts
        screen.blit(f["title"].render(self.title,True,self.accent), (self.area.x+28,self.area.y+22))
        screen.blit(f["body"].render(f"STRIKES  {self.strikes}/{self.target}",True,(245,248,255)), (self.area.right-170,self.area.y+28))
        if self.done:
            self._done(screen); return
        self._draw_mode(screen)
        if self.message:
            screen.blit(f["head"].render(self.message,True,self.message_color), f["head"].render(self.message,True,self.message_color).get_rect(center=(self.area.centerx,545)))
        hint=f["body"].render(self._hint(),True,(190,202,225)); screen.blit(hint,hint.get_rect(center=(self.area.centerx,575)))

    def _hint(self):
        return {"catch":"Catch the ingredient!","target":"Click the moving ingredient inside the target.","orbit":"Hit the spice while it circles the core.","sequence":"Click the highlighted power cells in order.","match":"Catch the matching holo ingredient.","stack":"Build the topping stack.","burst":"Collect one ingredient before it vanishes.","tap":"Tap the meteor fragment!"}.get(self.mode,"Hit the ingredient!")

    def _draw_mode(self,s):
        cx,cy=self.area.centerx,350
        if self.mode=="catch": self._ingredient(s,self.pos,self.icon,1.0)
        elif self.mode in ("target","match"):
            pygame.draw.circle(s,(*self.accent,70),self.goal,52,2); self._ingredient(s,self.pos,self.icon,1.0)
        elif self.mode=="orbit":
            pygame.draw.circle(s,(35,50,80), (cx,350),115,2); pygame.draw.circle(s,self.accent,(cx,350),18); self._ingredient(s,self.pos,self.icon,1.0)
        elif self.mode=="sequence":
            for i,x in enumerate((520,640,760)):
                col=self.accent if i==self.round%3 else (50,65,95)
                pygame.draw.rect(s,col,(x-35,300,70,70),border_radius=15); self._ingredient(s,(x,335),"battery",.65)
        elif self.mode=="stack":
            for i in range(self.strikes): self._ingredient(s,(self.area.centerx,450-i*55),"cookie",.8)
            self._ingredient(s,self.pos,"cookie",1)
        elif self.mode=="burst":
            for p in self.options: self._ingredient(s,p,"star",.75)
        elif self.mode=="tap": self._ingredient(s,self.pos,"meteor",1.1)

    def _ingredient(self,s,pos,kind,scale=1):
        x,y=map(int,pos); c=self.accent
        if kind=="milk": pygame.draw.ellipse(s,(240,248,255),(x-25,y-18,x+25,y+18))
        elif kind=="star":
            pts=[]
            for i in range(10):
                a=-math.pi/2+i*math.pi/5; r=24 if i%2==0 else 10; pts.append((x+math.cos(a)*r,y+math.sin(a)*r))
            pygame.draw.polygon(s,c,pts)
        elif kind=="spice": pygame.draw.circle(s,(230,150,90),(x,y),18); pygame.draw.circle(s,(255,220,130),(x-5,y-5),5)
        elif kind=="battery": pygame.draw.rect(s,c,(x-22,y-28,x+44,y+56),border_radius=7); pygame.draw.rect(s,(20,35,55),(x-12,y-16,x+24,y+30),border_radius=4)
        elif kind=="orb": pygame.draw.circle(s,c,(x,y),24); pygame.draw.circle(s,(255,255,255),(x-7,y-7),6)
        elif kind=="mint":
            pygame.draw.ellipse(s,(90,235,165),(x-9,y-25,x+9,y+5)); pygame.draw.ellipse(s,(120,255,190),(x-2,y-5,x+16,y+25)); pygame.draw.line(s,(30,130,90),(x,y-12),(x+8,y+18),3)
        elif kind=="cookie": pygame.draw.circle(s,(205,140,80),(x,y),25); [pygame.draw.circle(s,(70,45,35),(x+dx,y+dy),4) for dx,dy in ((-8,-7),(9,-4),(-3,9))]
        else: pygame.draw.circle(s,(235,245,255),(x,y),25); pygame.draw.polygon(s,(100,170,255),[(x-25,y),(x+20,y-10),(x+8,y+18)])

    def _done(self,s):
        f=self.fonts; text=f["big"].render("LIQUID UNLOCKED!",True,(90,235,165)); s.blit(text,text.get_rect(center=self.area.center))
        sub=f["body"].render("Your drink base is ready for the blender.",True,(220,230,245)); s.blit(sub,sub.get_rect(center=(self.area.centerx,self.area.centery+50)))

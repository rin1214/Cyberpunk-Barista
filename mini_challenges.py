"""
mini_challenges.py
Cyberpunk Café - Ingredient Match-3 Mini Challenge

This file is a drop-in replacement for the old reaction/action mini-games.

Gameplay:
    1. Select a drink in the Mixing Station.
    2. A 5x5 ingredient puzzle appears.
    3. Click one tile, then click an adjacent tile to swap.
    4. If the swap creates a match of 3 or more, the match is cleared.
    5. Make 3 successful matches.
    6. The challenge finishes and quickly hands control back to the Mixing Station.
    7. The player has 25 seconds for each attempt.

Mouse controls only. One simple timer, no lives, keyboard actions, or
complicated combos.
"""

import math
import random
import pygame


# ---------------------------------------------------------------------------
# DRINK THEMES
# ---------------------------------------------------------------------------

CHALLENGES = {
    "Neon Latte": {
        "title": "MILK MATCH",
        "ingredient": "MILK",
        "accent": (120, 235, 255),
        "tile_colors": [
            (245, 248, 255),
            (175, 225, 255),
            (210, 190, 255),
            (255, 220, 235),
            (150, 245, 220),
        ],
        "symbols": ["milk", "coffee", "syrup", "foam", "ice"],
    },
    "Milkyway": {
        "title": "STARDUST MATCH",
        "ingredient": "STARDUST",
        "accent": (205, 170, 255),
        "tile_colors": [
            (235, 220, 255),
            (175, 145, 255),
            (120, 210, 255),
            (255, 235, 150),
            (245, 175, 225),
        ],
        "symbols": ["milk", "chocolate", "star", "syrup", "ice"],
    },
    "Void Chai": {
        "title": "SPICE MATCH",
        "ingredient": "SPICE",
        "accent": (255, 175, 125),
        "tile_colors": [
            (255, 205, 150),
            (205, 155, 255),
            (255, 150, 185),
            (175, 235, 190),
            (245, 220, 150),
        ],
        "symbols": ["milk", "spice", "syrup", "star", "ice"],
    },
    "Cyber Fuel": {
        "title": "POWER MATCH",
        "ingredient": "POWER",
        "accent": (100, 190, 255),
        "tile_colors": [
            (115, 210, 255),
            (110, 140, 255),
            (185, 235, 255),
            (170, 255, 215),
            (245, 225, 100),
        ],
        "symbols": ["milk", "battery", "ice", "power", "star"],
    },
    "Hologram Frappe": {
        "title": "HOLO MATCH",
        "ingredient": "HOLO",
        "accent": (235, 160, 255),
        "tile_colors": [
            (255, 175, 230),
            (170, 225, 255),
            (190, 175, 255),
            (150, 255, 225),
            (255, 235, 150),
        ],
        "symbols": ["milk", "orb", "star", "ice", "syrup"],
    },
    "Pixel Lemint": {
        "title": "MINT MATCH",
        "ingredient": "MINT",
        "accent": (115, 245, 200),
        "tile_colors": [
            (120, 245, 205),
            (190, 255, 220),
            (120, 215, 255),
            (235, 225, 110),
            (190, 170, 255),
        ],
        "symbols": ["water", "mint", "ice", "star", "syrup"],
    },
    "Caramel Byte": {
        "title": "COOKIE MATCH",
        "ingredient": "COOKIE",
        "accent": (255, 190, 120),
        "tile_colors": [
            (225, 160, 100),
            (255, 205, 130),
            (190, 135, 105),
            (245, 180, 200),
            (170, 215, 255),
        ],
        "symbols": ["milk", "cookie", "caramel", "chocolate", "ice"],
    },
    "Stardust Matcha": {
        "title": "MATCHA MATCH",
        "ingredient": "MATCHA",
        "accent": (170, 245, 145),
        "tile_colors": [
            (155, 230, 145),
            (200, 250, 165),
            (125, 210, 180),
            (235, 220, 120),
            (180, 165, 245),
        ],
        "symbols": ["milk", "matcha", "star", "mint", "ice"],
    },
    "Meteorite": {
        "title": "METEOR MATCH",
        "ingredient": "METEOR",
        "accent": (125, 205, 255),
        "tile_colors": [
            (235, 245, 255),
            (145, 205, 255),
            (175, 175, 235),
            (255, 195, 120),
            (205, 220, 245),
        ],
        "symbols": ["milk", "meteor", "ice", "star", "orb"],
    },
}


# ---------------------------------------------------------------------------

# MINI CHALLENGE

class MiniChallenge:
    """Compact 5x5 drink-themed Match-3 used by station.py."""
    N, TILE, GAP, TYPES = 5, 62, 6, 5
    TARGET_STRIKES, CHALLENGE_TIME = 3, 18.0

    def __init__(self):
        pygame.font.init()
        self.panel = pygame.Rect(280, 92, 720, 540)
        self.grid = pygame.Rect(473, 275, 334, 334)  # centered in 1280x720
        self.ft = pygame.font.SysFont("arial", 29, True)
        self.fb = pygame.font.SysFont("arial", 21, True)
        self.fs = pygame.font.SysFont("arial", 17, True)
        self.strike_title_font = pygame.font.SysFont("arial", 18, True)
        self.strike_big_font = pygame.font.SysFont("arial", 40, True)
        self.done = self.active = False
        self.drink = ""
        self.title, self.ingredient = "INGREDIENT MATCH", "INGREDIENT"
        self.accent = (120, 235, 255)
        self.colors = [(245,248,255),(175,225,255),(210,190,255),(255,220,235),(150,245,220)]
        self.symbols = ["milk","syrup","coffee","ice","mint"]
        self.board, self.selected = [], None
        self.strikes, self.time_left, self.message_timer = 0, self.CHALLENGE_TIME, 0
        self.message, self.done_timer, self.pulse = "MATCH 3 INGREDIENTS", 0, 0

    def start_challenge(self, drink_name):
        d = CHALLENGES.get(drink_name, {})
        self.drink, self.title = drink_name, d.get("title", "INGREDIENT MATCH")
        self.ingredient, self.accent = d.get("ingredient", "INGREDIENT"), d.get("accent", (120,235,255))
        self.colors = d.get("tile_colors", self.colors)
        self.symbols = d.get("symbols", ["milk","syrup","coffee","ice","mint"])
        self.active, self.done, self.selected = True, False, None
        self.strikes, self.time_left, self.message_timer = 0, self.CHALLENGE_TIME, 0
        self.message, self.done_timer, self.pulse = "MATCH 3 INGREDIENTS", 0, 0
        self.board = self._new_board()

    def _new_board(self):
        for _ in range(300):
            b=[]
            for r in range(self.N):
                row=[]
                for c in range(self.N):
                    choices=list(range(self.TYPES)); random.shuffle(choices)
                    for v in choices:
                        if c>1 and row[-1]==row[-2]==v: continue
                        if r>1 and b[r-1][c]==b[r-2][c]==v: continue
                        row.append(v); break
                b.append(row)
            if self._has_move(b): return b
        return [[(r*2+c)%self.TYPES for c in range(self.N)] for r in range(self.N)]

    def _matches(self, b=None):
        b = self.board if b is None else b
        out=set()
        for r in range(self.N):
            for c in range(self.N-2):
                if b[r][c] is not None and b[r][c]==b[r][c+1]==b[r][c+2]:
                    out.update((r,c+i) for i in range(3))
        for c in range(self.N):
            for r in range(self.N-2):
                if b[r][c] is not None and b[r][c]==b[r+1][c]==b[r+2][c]:
                    out.update((r+i,c) for i in range(3))
        # Expand 3-runs to 4/5 when present.
        return {(r,c) for r,c in out if b[r][c] is not None}

    def _has_move(self,b):
        for r in range(self.N):
            for c in range(self.N):
                for dr,dc in ((0,1),(1,0)):
                    nr,nc=r+dr,c+dc
                    if nr>=self.N or nc>=self.N: continue
                    b[r][c],b[nr][nc]=b[nr][nc],b[r][c]
                    ok=bool(self._matches(b))
                    b[r][c],b[nr][nc]=b[nr][nc],b[r][c]
                    if ok:return True
        return False

    def _swap(self,a,b):
        r,c=a; nr,nc=b; self.board[r][c],self.board[nr][nc]=self.board[nr][nc],self.board[r][c]

    def _resolve(self):
        hit=self._matches()
        if not hit:return False
        for r,c in hit:self.board[r][c]=None
        for c in range(self.N):
            vals=[self.board[r][c] for r in range(self.N) if self.board[r][c] is not None]
            for r in range(self.N-1,-1,-1): self.board[r][c]=vals.pop() if vals else None
        for r in range(self.N):
            for c in range(self.N):
                if self.board[r][c] is not None: continue
                choices=list(range(self.TYPES)); random.shuffle(choices)
                self.board[r][c]=next((v for v in choices if not(c>1 and self.board[r][c-1]==self.board[r][c-2]==v) and not(r>1 and self.board[r-1][c]==self.board[r-2][c]==v)), random.randrange(self.TYPES))
        if self._matches() or not self._has_move(self.board): self.board=self._new_board()
        self.strikes+=1; self.message=f"STRIKE {self.strikes} / {self.TARGET_STRIKES}"; self.message_timer=.8
        if self.strikes>=self.TARGET_STRIKES:self._finish()
        return True

    def _try_swap(self,a,b):
        self._swap(a,b)
        if self._matches(): return self._resolve()
        self._swap(a,b); self.message="TRY ANOTHER SWAP"; self.message_timer=.8; return False

    def _cell(self,pos):
        if not self.grid.collidepoint(pos): return None
        step=self.TILE+self.GAP; x,y=pos; c,r=(x-self.grid.x)//step,(y-self.grid.y)//step
        if not(0<=r<self.N and 0<=c<self.N): return None
        if (x-self.grid.x)%step>=self.TILE or (y-self.grid.y)%step>=self.TILE:return None
        return int(r),int(c)

    def handle_event(self,event):
        if not self.active or event.type!=pygame.MOUSEBUTTONDOWN or event.button!=1:return
        cell=self._cell(event.pos)
        if cell is None:return
        if self.selected is None:self.selected=cell; self.message="CHOOSE A NEIGHBOUR"; self.message_timer=.6; return
        if cell==self.selected:self.selected=None; return
        a=self.selected; self.selected=None
        if abs(a[0]-cell[0])+abs(a[1]-cell[1])==1:self._try_swap(a,cell)
        else:self.selected=cell

    def update(self,dt):
        if not self.active and not self.done:return
        self.pulse+=dt; self.message_timer=max(0,self.message_timer-dt)
        if self.active:
            self.time_left=max(0,self.time_left-dt)
            if self.time_left<=0:self._time_up()
        elif self.done:
            self.done_timer=max(0,self.done_timer-dt)
            if self.done_timer<=0:self.done=False

    def _time_up(self):
        self.active=False; self.done=False; self.selected=None
        self.strikes=0; self.time_left=self.CHALLENGE_TIME; self.message="TIME'S UP - TRY AGAIN!"
        # Start a fresh attempt immediately, matching the existing station flow.
        self.active=True; self.board=self._new_board()

    def _finish(self):
        # Never allow the popup's total lifetime to exceed 18 seconds.
        self.active=False; self.done=True; self.selected=None
        self.done_timer=min(.22,max(0,self.time_left)); self.message="INGREDIENT READY!"

    def _text(self,screen,text,font,color,y):
        s=font.render(text,True,color); screen.blit(s,s.get_rect(center=(640,y)))

    def draw(self,screen):
        if not self.active and not self.done:return
        ov=pygame.Surface(screen.get_size(),pygame.SRCALPHA); ov.fill((5,8,22,180)); screen.blit(ov,(0,0))
        pygame.draw.rect(screen,self.accent,self.panel.inflate(12,12),border_radius=24)
        pygame.draw.rect(screen,(18,22,43),self.panel,border_radius=20)
        pygame.draw.rect(screen,self.accent,self.panel,2,border_radius=20)
        if self.done:self._draw_done(screen); return
        self._text(screen,self.title,self.ft,self.accent,128)
        self._text(screen,self.drink.upper(),self.fb,(242,245,255),158)
        self._text(screen,f"{self.ingredient}  •  MATCH 3 INGREDIENTS",self.fs,(205,212,235),187)
        self._draw_strikes(screen)
        self._draw_board(screen)
        self._text(screen,self.message if self.message_timer else "CLICK TWO ADJACENT TILES TO SWAP",self.fs,(230,235,250),625)
        self._text(screen,"Mouse only  •  18-second prep window  •  No penalty for trying",self.fs,(145,155,185),650)
        sec=max(0,int(self.time_left+0.999)); col=(255,145,165) if self.time_left<=5 else self.accent
        self._text(screen,f"TIME  {sec}s",self.fs,col,682)

    def _draw_strikes(self,screen):
        # Large, playful progress display: the player can see 0/3, 1/3, 2/3 or 3/3 instantly.
        self._text(screen,"STRIKES",self.strike_title_font,(210,218,240),210)
        value=f"{self.strikes} / {self.TARGET_STRIKES}"
        pulse=1.0 + 0.04*math.sin(self.pulse*8) if self.strikes else 1.0
        font=self.strike_big_font
        surf=font.render(value,True,self.accent if self.strikes else (235,240,255))
        if pulse != 1.0:
            surf=pygame.transform.smoothscale(surf,(int(surf.get_width()*pulse),int(surf.get_height()*pulse)))
        screen.blit(surf,surf.get_rect(center=(640,238)))
        for i in range(self.TARGET_STRIKES):
            x=570+i*70
            filled=i<self.strikes
            r=pygame.Rect(x,263,50,10)
            pygame.draw.rect(screen,(45,52,78),r,border_radius=5)
            if filled:
                pygame.draw.rect(screen,self.accent,r,border_radius=5)
                pygame.draw.circle(screen,(250,255,255),(x+25,268),3)

    def _draw_board(self,screen):
        mouse=self._cell(pygame.mouse.get_pos()); step=self.TILE+self.GAP
        for r in range(self.N):
            for c in range(self.N):
                rect=pygame.Rect(self.grid.x+c*step,self.grid.y+r*step,self.TILE,self.TILE); v=self.board[r][c]; col=self.colors[v%len(self.colors)]
                pygame.draw.rect(screen,(27,32,57),rect,border_radius=12)
                if mouse==(r,c):pygame.draw.rect(screen,(100,115,155),rect.inflate(4,4),2,border_radius=14)
                if self.selected==(r,c):pygame.draw.rect(screen,self.accent,rect.inflate(6,6),3,border_radius=15)
                glow=pygame.Surface((self.TILE+14,self.TILE+14),pygame.SRCALPHA); pygame.draw.circle(glow,(*col,35),(38,38),24); screen.blit(glow,(rect.x-7,rect.y-7))
                inner=rect.inflate(-8,-8); pygame.draw.rect(screen,col,inner,border_radius=14); self._icon(screen,rect.center,self.symbols[v%len(self.symbols)],col)

    def _icon(self,s,center,k,col):
        x,y=center; d=tuple(max(25,v-85) for v in col); w=(248,252,255)
        if k=="milk":
            r=pygame.Rect(x-10,y-10,20,22); pygame.draw.rect(s,w,r,border_radius=5); pygame.draw.rect(s,d,r,2,border_radius=5); pygame.draw.rect(s,d,(x-6,y-15,12,6),border_radius=2)
        elif k=="coffee": pygame.draw.ellipse(s,(105,65,48),(x-13,y-10,26,20)); pygame.draw.arc(s,(235,190,145),(x-7,y-8,14,16),1.1,5.1,2)
        elif k=="chocolate": pygame.draw.rect(s,(92,58,48),(x-12,y-10,24,20),border_radius=5); pygame.draw.line(s,(190,125,105),(x-7,y-5),(x+7,y+5),2)
        elif k=="syrup": pygame.draw.rect(s,(255,235,245),(x-10,y-6,20,18),border_radius=5); pygame.draw.rect(s,d,(x-10,y-6,20,18),2,border_radius=5); pygame.draw.rect(s,col,(x-6,y-14,12,8),border_radius=3)
        elif k in ("spice","matcha"): pygame.draw.circle(s,(190,105,70) if k=="spice" else (165,195,105),(x,y),12); pygame.draw.circle(s,(250,190,130) if k=="spice" else (225,245,170),(x-3,y-3),3)
        elif k=="battery": pygame.draw.rect(s,(120,220,255),(x-10,y-12,20,24),border_radius=4); pygame.draw.rect(s,d,(x-10,y-12,20,24),2,border_radius=4); pygame.draw.rect(s,(245,235,110),(x-3,y-4,6,8),border_radius=2)
        elif k=="power": pygame.draw.polygon(s,(250,235,120),[(x+2,y-14),(x-7,y+1),(x,y+1),(x-4,y+14),(x+9,y-4),(x+2,y-4)])
        elif k=="orb": pygame.draw.circle(s,(215,170,255),(x,y),12); pygame.draw.circle(s,w,(x-4,y-4),3)
        elif k=="mint": pygame.draw.polygon(s,(90,235,165),[(x,y+13),(x-12,y+2),(x-7,y-11),(x+4,y-14),(x+11,y-4),(x+7,y+8)]); pygame.draw.line(s,(55,155,115),(x,y+10),(x+3,y-8),2)
        elif k=="water": pygame.draw.polygon(s,(130,205,255),[(x,y-14),(x+11,y+3),(x,y+14),(x-11,y+3)])
        elif k=="cookie":
            pygame.draw.circle(s,(205,140,80),(x,y),12)
            for dx,dy in [(-5,-4),(5,-2),(-2,5),(6,5)]:pygame.draw.circle(s,(95,60,45),(x+dx,y+dy),2)
        elif k=="caramel": pygame.draw.line(s,(240,175,85),(x-12,y-6),(x+12,y+6),4); pygame.draw.line(s,(255,220,130),(x-9,y+4),(x+9,y-4),2)
        elif k=="star":
            pts=[(x+math.cos(-math.pi/2+i*math.pi/2.5)*14,y+math.sin(-math.pi/2+i*math.pi/2.5)*14) for i in range(5)]; pygame.draw.polygon(s,(255,225,110),pts); pygame.draw.circle(s,(255,250,205),(x,y),3)
        elif k=="ice":
            pts=[(x-12,y-8),(x+4,y-14),(x+13,y-4),(x+9,y+12),(x-7,y+14),(x-14,y+3)]; pygame.draw.polygon(s,(215,245,255),pts); pygame.draw.polygon(s,d,pts,2); pygame.draw.line(s,w,(x-7,y-5),(x+4,y-9),2)
        elif k=="foam":
            for dx,dy,r in [(-7,2,8),(0,-4,9),(8,2,8)]:pygame.draw.circle(s,w,(x+dx,y+dy),r)
        elif k=="meteor":
            pts=[(x-13,y),(x-4,y-10),(x+10,y-6),(x+14,y+5),(x+3,y+13),(x-9,y+8)]; pygame.draw.polygon(s,(220,235,250),pts); pygame.draw.polygon(s,(100,170,225),pts,2); pygame.draw.circle(s,(150,195,235),(x+4,y-3),3)
        else: pygame.draw.circle(s,w,(x,y),11)

    def _draw_done(self,s):
        self._text(s,"INGREDIENT READY!",pygame.font.SysFont("arial",38,True),self.accent,255)
        self._text(s,f"{self.ingredient} is ready for the blender.",self.fb,(235,240,255),300)
        self._text(s,f"STRIKES COMPLETED  {self.strikes} / {self.TARGET_STRIKES}",self.fs,(205,212,235),355)
        pygame.draw.circle(s,(25,32,58),(640,435),68); pygame.draw.circle(s,self.accent,(640,435),68,3)
        self._icon(s,(640,435),self.symbols[1%len(self.symbols)],(230,240,255))
        self._text(s,"Returning to the Mixing Station...",self.fs,(145,155,185),535)

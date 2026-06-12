"""
Арканоид — красивая игра для Windows с PyGame
10 уровней с уникальными узорами блоков
Управление: ← → (стрелки), ПРОБЕЛ — старт, ↑↓ — выбор уровня
Сборка exe: pyinstaller --onefile --windowed --name Арканоид arkanoid.py
"""

import pygame
import sys
import math
import random
import json
import os

# ─── Инициализация ───────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ─── Константы ───────────────────────────────────────────────
W, H = 800, 600
FPS = 60
TITLE = "Арканоид"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BRICK_COLS = 10
BRICK_ROWS = 8
BRICK_W = 70
BRICK_H = 22
BRICK_PAD = 4
BRICK_OFF_X = (W - (BRICK_COLS * (BRICK_W + BRICK_PAD) - BRICK_PAD)) // 2
BRICK_OFF_Y = 55

PADDLE_W = 120
PADDLE_H = 14
PADDLE_SPEED = 13  # 7 +25% = 9, затем +50% = 13

BALL_R = 8
BALL_SPEED = 5.75  # +15% от 5

SPEED_BOOST_DURATION = 15000  # 15 секунд в мс

HS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arkanoid_hs.json")

# ─── Цветовые схемы уровней (10 тем) ────────────────────────
LEVEL_THEMES = [
    {   # 1 — Радуга
        "name": "Радуга",
        "bg_top": (10, 10, 46), "bg_bottom": (26, 26, 78),
        "brick_colors": [
            ((255,71,87),(255,107,129)), ((255,99,72),(255,127,80)),
            ((255,165,2),(255,179,68)), ((46,213,115),(123,237,159)),
            ((30,144,255),(112,161,255)), ((168,85,247),(192,132,252)),
            ((6,182,212),(103,232,249)), ((255,107,129),(255,71,87)),
        ],
        "paddle_color": ((168,85,247),(79,70,229)),
        "ball_color": ((255,255,255),(192,132,252)),
    },
    {   # 2 — Огонь
        "name": "Огонь",
        "bg_top": (30,5,0), "bg_bottom": (60,15,5),
        "brick_colors": [
            ((180,20,0),(220,50,20)), ((200,40,0),(240,80,30)),
            ((220,60,0),(255,120,40)), ((240,100,0),(255,160,50)),
            ((255,140,0),(255,200,60)), ((255,180,20),(255,220,80)),
            ((200,60,0),(240,100,30)), ((160,30,0),(200,60,20)),
        ],
        "paddle_color": ((255,120,0),(200,40,0)),
        "ball_color": ((255,255,200),(255,160,0)),
    },
    {   # 3 — Лёд
        "name": "Лёд",
        "bg_top": (5,10,30), "bg_bottom": (15,25,60),
        "brick_colors": [
            ((100,180,255),(140,210,255)), ((80,160,240),(120,200,255)),
            ((120,200,255),(160,230,255)), ((150,220,255),(190,240,255)),
            ((180,240,255),(210,255,255)), ((200,250,255),(230,255,255)),
            ((130,210,255),(170,240,255)), ((90,170,245),(130,210,255)),
        ],
        "paddle_color": ((120,220,255),(60,140,220)),
        "ball_color": ((220,250,255),(140,200,255)),
    },
    {   # 4 — Лес
        "name": "Лес",
        "bg_top": (5,20,5), "bg_bottom": (15,40,15),
        "brick_colors": [
            ((34,139,34),(60,179,60)), ((0,100,0),(40,140,40)),
            ((85,107,47),(120,140,70)), ((107,142,35),(140,170,60)),
            ((0,128,0),(50,160,50)), ((46,125,50),(80,160,80)),
            ((60,179,113),(100,200,140)), ((34,100,34),(70,140,70)),
        ],
        "paddle_color": ((60,179,113),(34,100,34)),
        "ball_color": ((200,255,200),(100,200,100)),
    },
    {   # 5 — Золото
        "name": "Золото",
        "bg_top": (25,15,0), "bg_bottom": (50,30,5),
        "brick_colors": [
            ((184,134,11),(218,165,32)), ((150,100,0),(190,140,20)),
            ((218,165,32),(230,190,60)), ((139,90,0),(170,120,20)),
            ((255,215,0),(255,235,100)), ((160,120,0),(200,160,30)),
            ((200,150,20),(240,190,60)), ((140,100,0),(180,140,30)),
        ],
        "paddle_color": ((218,165,32),(150,100,0)),
        "ball_color": ((255,255,220),(255,215,0)),
    },
    {   # 6 — Космос
        "name": "Космос",
        "bg_top": (0,0,10), "bg_bottom": (10,0,30),
        "brick_colors": [
            ((75,0,130),(100,20,160)), ((138,43,226),(160,80,240)),
            ((25,25,112),(60,60,150)), ((106,90,205),(130,120,220)),
            ((72,61,139),(100,90,170)), ((147,112,219),(170,140,230)),
            ((60,20,120),(90,50,150)), ((123,104,238),(150,130,250)),
        ],
        "paddle_color": ((138,43,226),(75,0,130)),
        "ball_color": ((230,230,255),(147,112,219)),
    },
    {   # 7 — Неон
        "name": "Неон",
        "bg_top": (5,5,15), "bg_bottom": (15,10,30),
        "brick_colors": [
            ((255,0,128),(255,60,160)), ((0,255,128),(60,255,160)),
            ((0,128,255),(60,160,255)), ((255,255,0),(255,255,80)),
            ((255,0,255),(255,80,255)), ((0,255,255),(80,255,255)),
            ((255,128,0),(255,160,60)), ((128,0,255),(160,60,255)),
        ],
        "paddle_color": ((0,255,255),(0,128,128)),
        "ball_color": ((255,255,255),(0,255,200)),
    },
    {   # 8 — Закат
        "name": "Закат",
        "bg_top": (40,10,30), "bg_bottom": (80,20,50),
        "brick_colors": [
            ((255,94,77),(255,120,100)), ((255,154,0),(255,180,60)),
            ((255,206,84),(255,220,120)), ((255,127,80),(255,150,100)),
            ((200,50,100),(220,80,130)), ((255,183,77),(255,200,110)),
            ((255,110,60),(255,140,90)), ((180,40,80),(200,70,110)),
        ],
        "paddle_color": ((255,154,0),(200,50,100)),
        "ball_color": ((255,240,200),(255,180,100)),
    },
    {   # 9 — Океан
        "name": "Океан",
        "bg_top": (0,10,20), "bg_bottom": (0,30,50),
        "brick_colors": [
            ((0,105,148),(30,140,180)), ((0,128,128),(40,160,160)),
            ((70,130,180),(100,160,200)), ((0,150,136),(40,180,160)),
            ((64,224,208),(100,240,220)), ((0,180,210),(40,200,230)),
            ((100,180,220),(130,200,240)), ((0,140,180),(30,170,200)),
        ],
        "paddle_color": ((0,150,136),(0,100,100)),
        "ball_color": ((200,240,255),(100,200,240)),
    },
    {   # 10 — Тьма
        "name": "Тьма",
        "bg_top": (5,5,5), "bg_bottom": (15,15,20),
        "brick_colors": [
            ((80,80,80),(110,110,110)), ((60,60,60),(90,90,90)),
            ((100,100,100),(130,130,130)), ((50,50,50),(80,80,80)),
            ((120,120,120),(150,150,150)), ((70,70,70),(100,100,100)),
            ((90,90,90),(120,120,120)), ((40,40,40),(70,70,70)),
        ],
        "paddle_color": ((150,150,150),(80,80,80)),
        "ball_color": ((220,220,220),(150,150,150)),
    },
]

# ─── Узоры уровней (10 штук) ────────────────────────────────
LEVEL_PATTERNS = [
    # 1: Полные ряды
    [
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
    ],
    # 2: Ромб
    [
        [0,0,0,0,1,1,0,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,0,0,1,1,0,0,0,0],
    ],
    # 3: Шахматная доска с крестом
    [
        [1,0,1,0,1,1,0,1,0,1],
        [0,1,0,1,1,1,1,0,1,0],
        [1,0,1,1,1,1,1,1,0,1],
        [0,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,1,1,0],
        [1,0,1,1,1,1,1,1,0,1],
        [0,1,0,1,1,1,1,0,1,0],
    ],
    # 4: Пирамида
    [
        [0,0,0,0,1,1,0,0,0,0],
        [0,0,0,0,1,1,0,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,0],
    ],
    # 5: Зигзаг
    [
        [1,1,1,1,1,0,0,0,0,0],
        [0,0,0,0,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,1,1],
        [1,1,1,0,0,0,0,0,0,0],
        [0,0,1,1,1,1,0,0,0,0],
        [0,0,0,0,0,1,1,1,1,0],
        [1,1,0,0,0,0,0,0,1,1],
        [1,1,1,1,1,1,0,0,0,0],
    ],
    # 6: Сердце
    [
        [0,1,1,0,0,0,0,1,1,0],
        [1,1,1,1,0,0,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,0,0,1,1,0,0,0,0],
    ],
    # 7: Двойной ромб
    [
        [0,0,1,0,0,0,0,1,0,0],
        [0,1,1,1,0,0,1,1,1,0],
        [1,1,0,1,1,1,1,0,1,1],
        [1,0,0,0,1,1,0,0,0,1],
        [1,0,0,0,1,1,0,0,0,1],
        [1,1,0,1,1,1,1,0,1,1],
        [0,1,1,1,0,0,1,1,1,0],
        [0,0,1,0,0,0,0,1,0,0],
    ],
    # 8: Стены с проходами
    [
        [1,1,1,1,0,0,1,1,1,1],
        [1,1,1,1,0,0,1,1,1,1],
        [1,1,1,1,0,0,1,1,1,1],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [1,1,1,1,0,0,1,1,1,1],
        [1,1,1,1,0,0,1,1,1,1],
        [1,1,1,1,0,0,1,1,1,1],
    ],
    # 9: Спираль
    [
        [1,1,1,1,1,1,1,1,1,1],
        [0,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,1,0,1],
        [1,0,1,1,1,1,0,1,0,1],
        [1,0,1,0,0,0,0,1,0,1],
        [1,0,1,1,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,0,0,1],
    ],
    # 10: Крест
    [
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
    ],
]

# ─── HP блоков по уровням ──────────────────────────────────
LEVEL_HP = [
    [1,1,2,2,2,3,3,3],
    [1,1,2,2,3,3,2,1],
    [2,2,2,3,3,3,2,2],
    [1,2,2,3,3,2,2,1],
    [2,2,3,3,3,3,2,2],
    [1,1,2,3,3,2,1,1],
    [2,3,3,4,4,3,3,2],
    [2,2,3,3,3,3,2,2],
    [3,3,3,4,4,3,3,3],
    [3,3,4,4,4,4,3,3],
]

NUM_LEVELS = len(LEVEL_THEMES)

# ─── Звуки ──────────────────────────────────────────────────
def make_sound(freq, duration, vol=0.15, wave='sine'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        if wave == 'sine':
            val = math.sin(2 * math.pi * freq * t)
        elif wave == 'square':
            val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave == 'sawtooth':
            val = 2.0 * (freq * t - math.floor(freq * t + 0.5))
        else:
            val = math.sin(2 * math.pi * freq * t)
        env = max(0, 1.0 - t / duration)
        v = int(val * env * vol * 32767)
        v = max(-32768, min(32767, v))
        buf.extend(v.to_bytes(2, 'little', signed=True))
        buf.extend(v.to_bytes(2, 'little', signed=True))
    return pygame.mixer.Sound(buffer=bytes(buf))

SND_BOUNCE  = make_sound(500, 0.08, 0.1, 'square')
SND_BREAK   = make_sound(700, 0.12, 0.12, 'sawtooth')
SND_LOSE    = make_sound(200, 0.35, 0.12, 'sawtooth')
SND_POWERUP = make_sound(880, 0.1, 0.1, 'sine')
SND_WIN     = make_sound(660, 0.15, 0.1, 'sine')
SND_LEVELUP = make_sound(440, 0.1, 0.1, 'sine')
SND_EXPIRE  = make_sound(300, 0.15, 0.08, 'triangle')
SND_SELECT  = make_sound(350, 0.06, 0.08, 'sine')

def play_bounce():  SND_BOUNCE.play()
def play_break():   SND_BREAK.play()
def play_lose():    SND_LOSE.play()
def play_powerup(): SND_POWERUP.play()
def play_win():     SND_WIN.play()
def play_expire():  SND_EXPIRE.play()
def play_select():  SND_SELECT.play()

def play_levelup():
    SND_LEVELUP.play()
    pygame.time.delay(80)
    SND_LEVELUP.play()

# ─── Шрифты ─────────────────────────────────────────────────
def get_font(size):
    for name in ['segoeui', 'arial', 'tahoma', 'verdana']:
        f = pygame.font.SysFont(name, size)
        if f:
            return f
    return pygame.font.Font(None, size)

# ─── Звёзды ─────────────────────────────────────────────────
class Star:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(0, H)
        self.size = random.uniform(0.5, 2)
        self.phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.brightness = 0.3 + 0.3 * math.sin(pygame.time.get_ticks() * 0.002 + self.phase)

    def draw(self, surf):
        b = self.brightness
        color = (int(255*b), int(255*b), int(240*b))
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), int(self.size))

# ─── Частицы ────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, speed=3, glow=False):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, speed)
        self.dx = math.cos(angle) * spd
        self.dy = math.sin(angle) * spd
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.035)
        self.size = random.uniform(2, 6)
        self.color = color
        self.glow = glow

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.06
        self.life -= self.decay
        return self.life > 0

    def draw(self, surf):
        if self.life <= 0:
            return
        s = max(1, int(self.size * self.life))
        color = self.color[:3]
        if self.glow:
            glow_surf = pygame.Surface((s*6, s*6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 80), (s*3, s*3), s*3)
            surf.blit(glow_surf, (int(self.x)-s*3, int(self.y)-s*3))
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), s)

# ─── Блок ───────────────────────────────────────────────────
class Brick:
    def __init__(self, row, col, hp, colors):
        self.x = BRICK_OFF_X + col * (BRICK_W + BRICK_PAD)
        self.y = BRICK_OFF_Y + row * (BRICK_H + BRICK_PAD)
        self.w = BRICK_W
        self.h = BRICK_H
        self.max_hp = hp
        self.hp = hp
        self.alive = True
        self.c1, self.c2 = colors

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surf):
        if not self.alive:
            return
        for i in range(self.h):
            t = i / self.h
            r = int(self.c1[0] * (1-t) + self.c2[0] * t)
            g = int(self.c1[1] * (1-t) + self.c2[1] * t)
            b = int(self.c1[2] * (1-t) + self.c2[2] * t)
            pygame.draw.line(surf, (r,g,b), (self.x, self.y+i), (self.x+self.w, self.y+i))
        shine = pygame.Surface((self.w, self.h//2), pygame.SRCALPHA)
        shine.fill((255,255,255,30))
        surf.blit(shine, (self.x, self.y+1))
        pygame.draw.rect(surf, (255,255,255,40), (self.x, self.y, self.w, self.h), 1, border_radius=4)
        if self.max_hp > 1:
            f = get_font(11)
            txt = f.render(str(self.hp), True, WHITE)
            surf.blit(txt, (self.x + self.w//2 - txt.get_width()//2,
                           self.y + self.h//2 - txt.get_height()//2))

# ─── Платформа ──────────────────────────────────────────────
class Paddle:
    def __init__(self, theme):
        self.w = PADDLE_W
        self.h = PADDLE_H
        self.x = W//2 - self.w//2
        self.y = H - 40
        self.c1, self.c2 = theme["paddle_color"]

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT]:
            self.x += PADDLE_SPEED
        self.x = max(0, min(W - self.w, self.x))

    def draw(self, surf):
        for i in range(self.h):
            t = i / self.h
            r = int(self.c1[0]*(1-t) + self.c2[0]*t)
            g = int(self.c1[1]*(1-t) + self.c2[1]*t)
            b = int(self.c1[2]*(1-t) + self.c2[2]*t)
            pygame.draw.line(surf, (r,g,b), (int(self.x), self.y+i),
                           (int(self.x+self.w), self.y+i))
        shine = pygame.Surface((self.w-8, self.h//2), pygame.SRCALPHA)
        shine.fill((255,255,255,40))
        surf.blit(shine, (int(self.x)+4, self.y+2))
        pygame.draw.rect(surf, (200,200,255,80), (int(self.x), self.y, self.w, self.h), 1, border_radius=7)

# ─── Шар ────────────────────────────────────────────────────
class Ball:
    def __init__(self, x=None, y=None, dx=None, dy=None, theme_idx=0):
        self.x = x or W//2
        self.y = y or H - 52
        angle = random.uniform(-0.6, 0.6) - math.pi/2
        self.dx = dx or math.cos(angle) * BALL_SPEED
        self.dy = dy or math.sin(angle) * BALL_SPEED
        self.r = BALL_R
        self.trail = []
        self.theme_idx = theme_idx

    def update(self, paddle, bricks, particles, powerups):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 14:
            self.trail.pop(0)

        self.x += self.dx
        self.y += self.dy

        if self.x - self.r < 0:
            self.x = self.r
            self.dx = abs(self.dx)
            play_bounce()
        if self.x + self.r > W:
            self.x = W - self.r
            self.dx = -abs(self.dx)
            play_bounce()
        if self.y - self.r < 0:
            self.y = self.r
            self.dy = abs(self.dy)
            play_bounce()

        # Платформа
        if (self.dy > 0 and
            self.y + self.r >= paddle.y and
            self.y + self.r <= paddle.y + paddle.h + 6 and
            self.x >= paddle.x - 4 and
            self.x <= paddle.x + paddle.w + 4):
            self.y = paddle.y - self.r
            hit = (self.x - (paddle.x + paddle.w/2)) / (paddle.w/2)
            angle = hit * (math.pi * 0.75) - math.pi/2
            spd = math.sqrt(self.dx**2 + self.dy**2)
            self.dx = math.cos(angle) * spd
            self.dy = math.sin(angle) * spd
            self.dy = -abs(self.dy)
            play_bounce()
            theme = LEVEL_THEMES[self.theme_idx]
            bc = theme["ball_color"][1]
            for _ in range(5):
                particles.append(Particle(self.x, self.y, bc, 2))

        # Блоки
        for br in bricks:
            if not br.alive:
                continue
            if (self.x + self.r > br.x and self.x - self.r < br.x + br.w and
                self.y + self.r > br.y and self.y - self.r < br.y + br.h):
                destroyed = br.hit()
                if destroyed:
                    play_break()
                    for _ in range(20):
                        particles.append(Particle(br.x+br.w//2, br.y+br.h//2,
                                                   random.choice([br.c1, br.c2]), 5, glow=True))
                    if random.random() < 0.22:
                        powerups.append(PowerUp(br.x+br.w//2, br.y+br.h//2, self.theme_idx))
                else:
                    play_bounce()
                    for _ in range(6):
                        particles.append(Particle(self.x, self.y, br.c1, 2.5))
                ol = (self.x + self.r) - br.x
                or_ = (br.x + br.w) - (self.x - self.r)
                ot = (self.y + self.r) - br.y
                ob = (br.y + br.h) - (self.y - self.r)
                mn = min(ol, or_, ot, ob)
                if mn == ol or mn == or_:
                    self.dx = -self.dx
                else:
                    self.dy = -self.dy
                break

        if self.y - self.r > H:
            return True
        return False

    def draw(self, surf):
        theme = LEVEL_THEMES[self.theme_idx]
        bc1, bc2 = theme["ball_color"]
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 80)
            size = max(1, int(self.r * (i / len(self.trail))))
            trail_surf = pygame.Surface((size*2+2, size*2+2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*bc2, alpha), (size+1, size+1), size)
            surf.blit(trail_surf, (int(tx)-size-1, int(ty)-size-1))
        ball_surf = pygame.Surface((self.r*2+4, self.r*2+4), pygame.SRCALPHA)
        for r in range(self.r, 0, -1):
            t = r / self.r
            red = int(bc1[0]*(1-t) + bc2[0]*t)
            grn = int(bc1[1]*(1-t) + bc2[1]*t)
            blu = int(bc1[2]*(1-t) + bc2[2]*t)
            pygame.draw.circle(ball_surf, (red,grn,blu,200), (self.r+2, self.r+2), r)
        surf.blit(ball_surf, (int(self.x)-self.r-2, int(self.y)-self.r-2))

# ─── Бонусы ─────────────────────────────────────────────────
PW_TYPES = [
    {'type': 'wide',  'color': (46,213,115),  'label': 'W'},
    {'type': 'multi', 'color': (255,165,2),   'label': 'M'},
    {'type': 'life',  'color': (255,71,87),   'label': '+'},
    {'type': 'slow',  'color': (30,144,255),  'label': 'S'},
    {'type': 'fast',  'color': (255,50,50),   'label': 'F'},
]

class PowerUp:
    def __init__(self, x, y, theme_idx):
        self.x = x
        self.y = y
        self.dy = 2
        self.w = 30
        self.h = 20
        self.t = random.choice(PW_TYPES)
        self.theme_idx = theme_idx

    def update(self):
        self.y += self.dy
        return self.y < H

    def draw(self, surf):
        rect = pygame.Rect(int(self.x - self.w//2), int(self.y), self.w, self.h)
        pygame.draw.rect(surf, self.t['color'], rect, border_radius=6)
        pygame.draw.rect(surf, (255,255,255,80), rect, 1, border_radius=6)
        f = get_font(13)
        txt = f.render(self.t['label'], True, WHITE)
        surf.blit(txt, (int(self.x) - txt.get_width()//2,
                       int(self.y) + self.h//2 - txt.get_height()//2))

    def apply(self, paddle, balls, theme_idx):
        tp = self.t['type']
        if tp == 'wide':
            paddle.w = min(220, paddle.w + 30)
            paddle.x = min(paddle.x, W - paddle.w)
        elif tp == 'multi':
            new_balls = []
            for b in balls:
                new_balls.append(Ball(b.x, b.y, b.dx*0.8+1.5, b.dy, theme_idx))
                new_balls.append(Ball(b.x, b.y, b.dx*0.8-1.5, b.dy, theme_idx))
            balls.extend(new_balls)
        elif tp == 'life':
            return 'life'
        elif tp == 'slow':
            for b in balls:
                b.dx *= 0.7
                b.dy *= 0.7
            return 'slow'
        elif tp == 'fast':
            for b in balls:
                b.dx *= 1.4
                b.dy *= 1.4
            return 'fast'
        return None

# ─── Основная игра ──────────────────────────────────────────
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.stars = [Star() for _ in range(60)]
        self.load_high_score()
        self.state = 'level_select'
        self.selected_level = 0

    def load_high_score(self):
        try:
            with open(HS_FILE, 'r') as f:
                self.high_score = json.load(f).get('high_score', 0)
        except:
            self.high_score = 0

    def save_high_score(self):
        try:
            with open(HS_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

    def start_level(self, level_idx):
        self.level_idx = level_idx
        self.theme = LEVEL_THEMES[level_idx]
        self.pattern = LEVEL_PATTERNS[level_idx]
        self.hp_map = LEVEL_HP[level_idx]
        self.state = 'start'
        self.paddle = Paddle(self.theme)
        self.balls = [Ball(theme_idx=level_idx)]
        self.bricks = []
        self.particles = []
        self.powerups = []
        self.shake = 0
        self.score = 0
        self.lives = 3
        self._prev_alive = sum(1 for r in range(BRICK_ROWS) for c in range(BRICK_COLS) if self.pattern[r][c])
        self.slow_timer = 0
        self.fast_timer = 0
        self._build_bricks()

    def _build_bricks(self):
        self.bricks = []
        pattern = self.pattern
        hp_map = self.hp_map
        colors = self.theme["brick_colors"]
        for r in range(BRICK_ROWS):
            for c in range(BRICK_COLS):
                if pattern[r][c]:
                    hp = hp_map[r]
                    col_idx = r % len(colors)
                    self.bricks.append(Brick(r, c, hp, colors[col_idx]))

    def next_level(self):
        if self.level_idx < NUM_LEVELS - 1:
            self.start_level(self.level_idx + 1)
            play_levelup()
        else:
            self.state = 'win'
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            play_win()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_high_score()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'level_select':
                        self.save_high_score()
                        pygame.quit()
                        sys.exit()
                    elif self.state in ('start', 'playing', 'level_complete', 'gameover', 'win'):
                        self.state = 'level_select'
                elif self.state == 'level_select':
                    if event.key == pygame.K_UP:
                        self.selected_level = (self.selected_level - 1) % NUM_LEVELS
                        play_select()
                    elif event.key == pygame.K_DOWN:
                        self.selected_level = (self.selected_level + 1) % NUM_LEVELS
                        play_select()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.start_level(self.selected_level)
                elif self.state == 'start':
                    if event.key == pygame.K_SPACE:
                        self.state = 'playing'
                elif self.state == 'gameover':
                    if event.key == pygame.K_SPACE:
                        self.start_level(self.selected_level)
                        self.state = 'playing'
                elif self.state == 'win':
                    if event.key == pygame.K_SPACE:
                        self.state = 'level_select'
                elif self.state == 'level_complete':
                    if event.key == pygame.K_SPACE:
                        self.next_level()

    def _revert_speed(self):
        for b in self.balls:
            spd = math.sqrt(b.dx**2 + b.dy**2)
            if spd > 0.01:
                target = BALL_SPEED
                ratio = target / spd
                b.dx *= ratio
                b.dy *= ratio

    def update(self):
        for s in self.stars:
            s.update()

        if self.state == 'level_select':
            return

        if self.state != 'playing':
            self.particles = [p for p in self.particles if p.update()]
            return

        # Подсчёт очков
        current_alive = sum(1 for b in self.bricks if b.alive)
        if hasattr(self, '_prev_alive'):
            destroyed = self._prev_alive - current_alive
            if destroyed > 0:
                self.score += destroyed * 15
        self._prev_alive = current_alive

        # Таймеры бонусов скорости
        if self.slow_timer > 0:
            self.slow_timer -= self.clock.get_time()
            if self.slow_timer <= 0:
                self.slow_timer = 0
                self._revert_speed()
                play_expire()

        if self.fast_timer > 0:
            self.fast_timer -= self.clock.get_time()
            if self.fast_timer <= 0:
                self.fast_timer = 0
                self._revert_speed()
                play_expire()

        keys = pygame.key.get_pressed()
        self.paddle.update(keys)

        # Шары
        for ball in self.balls[:]:
            lost = ball.update(self.paddle, self.bricks, self.particles, self.powerups)
            if lost:
                self.balls.remove(ball)
                if not self.balls:
                    self.lives -= 1
                    play_lose()
                    if self.lives <= 0:
                        self.state = 'gameover'
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.save_high_score()
                    else:
                        self.balls.append(Ball(theme_idx=self.level_idx))

        # Проверка победы
        if all(not br.alive for br in self.bricks):
            self.state = 'level_complete'
            play_levelup()

        # Бонусы
        for pw in self.powerups[:]:
            if not pw.update():
                self.powerups.remove(pw)
                continue
            if (pw.y + pw.h >= self.paddle.y and
                pw.y <= self.paddle.y + self.paddle.h and
                pw.x + pw.w//2 >= self.paddle.x and
                pw.x - pw.w//2 <= self.paddle.x + self.paddle.w):
                result = pw.apply(self.paddle, self.balls, self.level_idx)
                if result == 'life':
                    self.lives += 1
                elif result == 'slow':
                    self.slow_timer = SPEED_BOOST_DURATION
                    self.fast_timer = 0
                elif result == 'fast':
                    self.fast_timer = SPEED_BOOST_DURATION
                    self.slow_timer = 0
                play_powerup()
                for _ in range(15):
                    self.particles.append(Particle(pw.x, pw.y, pw.t['color'], 4, glow=True))
                self.powerups.remove(pw)

        self.particles = [p for p in self.particles if p.update()]

        if self.shake > 0:
            self.shake *= 0.88
            if self.shake < 0.3:
                self.shake = 0

    def draw(self):
        # Фон
        if self.state == 'level_select':
            bg_top = (10, 10, 30)
            bg_bottom = (20, 15, 50)
        else:
            bg_top = self.theme["bg_top"]
            bg_bottom = self.theme["bg_bottom"]

        for y in range(H):
            t = y / H
            r = int(bg_top[0]*(1-t) + bg_bottom[0]*t)
            g = int(bg_top[1]*(1-t) + bg_bottom[1]*t)
            b = int(bg_top[2]*(1-t) + bg_bottom[2]*t)
            pygame.draw.line(self.screen, (r,g,b), (0, y), (W, y))

        for s in self.stars:
            s.draw(self.screen)

        # ─── Меню выбора уровня ───
        if self.state == 'level_select':
            self._draw_level_select()
            pygame.display.flip()
            return

        # Игровое поле
        offset_x, offset_y = 0, 0
        if self.shake > 0:
            offset_x = int((random.random()-0.5) * self.shake * 3)
            offset_y = int((random.random()-0.5) * self.shake * 3)

        game_surf = pygame.Surface((W, H), pygame.SRCALPHA)

        for br in self.bricks:
            br.draw(game_surf)
        for pw in self.powerups:
            pw.draw(game_surf)
        self.paddle.draw(game_surf)
        for ball in self.balls:
            ball.draw(game_surf)
        for p in self.particles:
            p.draw(game_surf)

        self.screen.blit(game_surf, (offset_x, offset_y))

        # UI
        f_ui = get_font(18)
        theme = self.theme
        blocks_left = sum(1 for b in self.bricks if b.alive)
        texts = [
            (f"Уровень: {self.level_idx+1} — {theme['name']}", (15, 8)),
            (f"Блоки: {blocks_left}", (15, 30)),
            (f"Очки: {self.score}", (W//2 - 50, 8)),
            (f"Жизни: {self.lives}", (W//2 - 50, 30)),
            (f"Рекорд: {self.high_score}", (W - 200, 8)),
        ]
        for text, pos in texts:
            shadow = f_ui.render(text, True, (0,0,0))
            surf = f_ui.render(text, True, WHITE)
            self.screen.blit(shadow, (pos[0]+1, pos[1]+1))
            self.screen.blit(surf, pos)

        # Таймеры бонусов
        timer_y = 52
        if self.slow_timer > 0:
            remaining = self.slow_timer / 1000.0
            f_timer = get_font(14)
            txt = f_timer.render(f"Замедление: {remaining:.1f}с", True, (30,144,255))
            self.screen.blit(txt, (15, timer_y))
            bar_w = 120
            progress = self.slow_timer / SPEED_BOOST_DURATION
            pygame.draw.rect(self.screen, (30,144,255,60), (15, timer_y+18, bar_w, 4), border_radius=2)
            pygame.draw.rect(self.screen, (30,144,255,180), (15, timer_y+18, int(bar_w*progress), 4), border_radius=2)
        if self.fast_timer > 0:
            remaining = self.fast_timer / 1000.0
            f_timer = get_font(14)
            txt = f_timer.render(f"Ускорение: {remaining:.1f}с", True, (255,80,80))
            self.screen.blit(txt, (15, timer_y))
            bar_w = 120
            progress = self.fast_timer / SPEED_BOOST_DURATION
            pygame.draw.rect(self.screen, (255,80,80,60), (15, timer_y+18, bar_w, 4), border_radius=2)
            pygame.draw.rect(self.screen, (255,80,80,180), (15, timer_y+18, int(bar_w*progress), 4), border_radius=2)

        # Оверлеи
        if self.state == 'start':
            self._draw_overlay(
                f"УРОВЕНЬ {self.level_idx + 1}",
                theme["name"],
                "ПРОБЕЛ — старт  |  ← → — управление  |  ESC — меню"
            )
        elif self.state == 'level_complete':
            if self.level_idx < NUM_LEVELS - 1:
                self._draw_overlay(
                    f"УРОВЕНЬ {self.level_idx + 1} ПРОЙДЕН!",
                    f"Счёт: {self.score}",
                    "ПРОБЕЛ — следующий уровень  |  ESC — меню"
                )
            else:
                self._draw_overlay(
                    "ПОБЕДА!",
                    f"Финальный счёт: {self.score}",
                    "ПРОБЕЛ — к выбору уровня"
                )
        elif self.state == 'gameover':
            self._draw_overlay(
                "ИГРА ОКОНЧЕНА",
                f"Счёт: {self.score}",
                "ПРОБЕЛ — рестарт  |  ESC — меню"
            )
        elif self.state == 'win':
            self._draw_overlay(
                "ВЫ ПРОШЛИ ВСЮ ИГРУ!",
                f"Финальный счёт: {self.score}",
                "ПРОБЕЛ — к выбору уровня"
            )

        pygame.display.flip()

    def _draw_level_select(self):
        """Меню выбора уровня с превью узора."""
        f_title = get_font(42)
        f_sub = get_font(22)
        f_level = get_font(20)
        f_hint = get_font(16)

        # Заголовок
        title = f_title.render("ВЫБЕРИТЕ УРОВЕНЬ", True, (200,180,255))
        self.screen.blit(title, (W//2 - title.get_width()//2, 20))

        hint = f_hint.render("↑↓ — выбор  |  ПРОБЕЛ/ENTER — старт  |  ESC — выход", True, (100,100,140))
        self.screen.blit(hint, (W//2 - hint.get_width()//2, 65))

        # Рисуем карточки уровней (2 колонки x 5 рядов)
        card_w = 320
        card_h = 75
        cols = 2
        start_x = (W - cols * (card_w + 20)) // 2
        start_y = 95

        for i in range(NUM_LEVELS):
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + 20)
            y = start_y + row * (card_h + 10)

            theme = LEVEL_THEMES[i]
            is_selected = (i == self.selected_level)

            # Фон карточки
            if is_selected:
                bg_color = (40, 35, 70)
                border_color = theme["brick_colors"][0][0]
                border_w = 3
            else:
                bg_color = (25, 22, 45)
                border_color = (60, 55, 80)
                border_w = 1

            card_rect = pygame.Rect(x, y, card_w, card_h)
            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, card_rect, border_w, border_radius=8)

            # Номер и название
            num_color = theme["brick_colors"][0][0] if is_selected else (180, 170, 200)
            name_surf = f_level.render(f"{i+1}. {theme['name']}", True, num_color)
            self.screen.blit(name_surf, (x + 12, y + 8))

            # Мини-превью узора
            preview_x = x + 12
            preview_y = y + 35
            mini_w = 56
            mini_h = 17
            mini_pad = 3
            pattern = LEVEL_PATTERNS[i]
            for r in range(BRICK_ROWS):
                for c in range(BRICK_COLS):
                    if pattern[r][c]:
                        px = preview_x + c * (mini_w + mini_pad)
                        py = preview_y + r * (mini_h + mini_pad)
                        color = theme["brick_colors"][r % len(theme["brick_colors"])][0]
                        if not is_selected:
                            color = (color[0]//3, color[1]//3, color[2]//3)
                        pygame.draw.rect(self.screen, color, (px, py, mini_w, mini_h), border_radius=2)

            # Количество блоков
            block_count = sum(pattern[r][c] for r in range(BRICK_ROWS) for c in range(BRICK_COLS))
            count_surf = f_hint.render(f"Блоков: {block_count}", True, (120, 110, 150))
            self.screen.blit(count_surf, (x + card_w - count_surf.get_width() - 12, y + 8))

        # Рекорд
        hs_surf = f_sub.render(f"Рекорд: {self.high_score}", True, (150, 140, 180))
        self.screen.blit(hs_surf, (W//2 - hs_surf.get_width()//2, H - 40))

    def _draw_overlay(self, title, subtitle, hint):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        f_title = get_font(48)
        f_sub = get_font(24)
        f_hint = get_font(18)

        tc = self.theme["brick_colors"][0][0]
        title_surf = f_title.render(title, True, tc)
        title_shadow = f_title.render(title, True, (0,0,0))
        self.screen.blit(title_shadow, (W//2 - title_surf.get_width()//2+2, H//2-72))
        self.screen.blit(title_surf, (W//2 - title_surf.get_width()//2, H//2-70))

        sub_surf = f_sub.render(subtitle, True, (180, 180, 220))
        self.screen.blit(sub_surf, (W//2 - sub_surf.get_width()//2, H//2))

        hint_surf = f_hint.render(hint, True, (100, 100, 140))
        self.screen.blit(hint_surf, (W//2 - hint_surf.get_width()//2, H//2+60))


if __name__ == '__main__':
    game = Game()
    game.run()

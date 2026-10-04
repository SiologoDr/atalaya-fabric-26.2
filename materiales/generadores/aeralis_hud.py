"""
La barra de jefe de Aeralis, la Mariposa del Vendaval, pintada pixel a pixel
(nada de la de vanilla). Misma composicion que la de Nerea, con lo suyo:

  aeralis_barra_marco.png        el marco: marmol de nube con dos alitas encima y
                                 el hueco redondo del emblema (208x26)
  aeralis_barra_viento.png       el relleno: viento que corre, en grises para
                                 tenirlo con el color de cada fase (64x8)
  aeralis_barra_nucleo_N.png     el emblema: el ojo de la tormenta de cada fase,
                                 cada vez mas agrietado por los rayos, y el
                                 liberado en oro (16x16)
  aeralis_barra_pluma*.png       las muescas de fase: una pluma entera o rasgada
  aeralis_barra_nombre.png       "AERALIS" en letras de pixel
  aeralis_barra_fase_N.png       "FASE I".."FASE IV" y aeralis_barra_libre.png

Uso: python aeralis_hud.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image
import math, os, sys, random

RAIZ = sys.argv[1]
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
os.makedirs(GUI, exist_ok=True)
rnd = random.Random(19)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


NUBE = [hexc(c) for c in ('1c2232', '323c52', '56627c', '8592ac', 'b8c4d8', 'e2e8f2')]
CIELO = [hexc(c) for c in ('2a4a78', '4f8fc0', '8fd6ff', 'cfeeff', 'f4fbff')]
PLATA = [hexc(c) for c in ('5a6274', '8a93a6', 'b8c0d0', 'dde3ee', 'f6f8fc')]

# --------------------------------------------------------------- marco
W, H = 208, 26
BX0, BX1, BY0, BY1 = 28, 199, 9, 16
EC, ER = 13.0, 12.6
m = Image.new('RGBA', (W, H), (0, 0, 0, 0))
p = m.load()
for y in range(H):
    for x in range(W):
        dentro_barra = BX0 - 3 <= x <= BX1 + 3 and BY0 - 3 <= y <= BY1 + 3
        d = math.hypot(x + 0.5 - EC, y + 0.5 - EC)
        if dentro_barra or d <= ER:
            borde = (x in (BX0 - 3, BX1 + 3) or y in (BY0 - 3, BY1 + 3)) and dentro_barra and d > ER - 1
            if d <= ER and d > ER - 1.2:
                p[x, y] = NUBE[0]
            elif d <= ER - 1.2 and d > ER - 3.0:
                k = 5 if (y + 0.5 < EC - 3) else 4 if y + 0.5 < EC + 3 else 3
                p[x, y] = NUBE[k] if rnd.random() > 0.15 else NUBE[k - 1]
            elif d <= ER - 3.0:
                p[x, y] = hexc('0a0e18')
            elif borde:
                p[x, y] = NUBE[0]
            elif BX0 <= x <= BX1 and BY0 <= y <= BY1:
                p[x, y] = hexc('070a12')
            else:
                k = 5 if y < BY0 - 1 else 3 if y > BY1 + 1 else 4
                # vetas de marmol: lineas diagonales mas oscuras
                if (x * 2 + y * 5) % 23 == 0:
                    k -= 2
                p[x, y] = NUBE[k] if rnd.random() > 0.18 else NUBE[k - 1]
# remaches de plata
for x in range(BX0 + 10, BX1 - 4, 22):
    for dx in (0, 1):
        p[x + dx, BY0 - 2] = PLATA[4] if dx == 0 else PLATA[2]
        p[x + dx, BY1 + 2] = PLATA[3] if dx == 0 else PLATA[1]
# dos alitas sobre el marco (la izquierda queda libre para el nombre y la derecha para la fase)
for cx in (98, 120):
    for k in range(6):
        for dx in range(-k, k + 1):
            yy = BY0 - 3 - (5 - k)
            xa, xb = cx - 6 + k, cx + 6 - k
            if 0 <= yy < H:
                p[xa, yy] = CIELO[3] if k > 2 else PLATA[3]
                p[xb, yy] = CIELO[3] if k > 2 else PLATA[3]
    p[cx, BY0 - 4] = PLATA[4]
    p[cx, BY0 - 5] = CIELO[4]
# la punta derecha: un ala que se deshace en viento
for k in range(7):
    p[BX1 + 4 + k // 2, BY0 - 3 + k] = PLATA[3]
    p[BX1 + 4 + k // 2, BY1 + 3 - k] = PLATA[2]
for k in range(4):
    p[min(W - 1, BX1 + 7 + k), BY0 + 3] = CIELO[3][:3] + (200 - k * 45,)
m.save(os.path.join(GUI, 'aeralis_barra_marco.png'))

# --------------------------------------------------------------- viento (relleno)
aw, ah = 64, 8
a = Image.new('RGBA', (aw, ah), (0, 0, 0, 0))
p = a.load()
for y in range(ah):
    for x in range(aw):
        t = y / (ah - 1)
        v = 225 - 95 * t
        # estelas de viento: rayas largas y finas que corren
        if (x + y * 9) % 21 < 7 and y in (1, 3, 5):
            v = 255
        elif (x * 3 + y * 7) % 31 == 0:
            v = min(255, v + 40)
        p[x, y] = (int(v), int(v), int(v), 255)
a.save(os.path.join(GUI, 'aeralis_barra_viento.png'))

# --------------------------------------------------------------- emblema: el ojo de la tormenta
COLORES = {1: ('f2ffff', '5fd2ff'), 2: ('eef0ff', '7f8cff'), 3: ('fff7d6', 'b07cff'), 4: ('ffffff', 'ff4fd8'),
           'libre': ('fffbe0', 'ffc23a')}
GRIETAS = {1: 0, 2: 2, 3: 4, 4: 7, 'libre': 0}
S = 16
for clave, (c1, c2) in COLORES.items():
    r = random.Random(str(clave))
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    q = im.load()
    a1, b1 = hexc(c1), hexc(c2)
    for j in range(S):
        for i in range(S):
            dx, dy = i + 0.5 - S / 2, j + 0.5 - S / 2
            if abs(dx) + abs(dy) > S / 2 - 0.5:
                continue
            if abs(dx) + abs(dy) > S / 2 - 1.8:
                q[i, j] = (16, 20, 34, 255)
                continue
            d = math.hypot(dx, dy) / (S / 2 - 1)
            ang = math.atan2(dy, dx)
            brazo = (ang - 2.4 * math.log(max(d, 0.08))) % math.pi
            if brazo < 1.1 or d < 0.16:
                q[i, j] = tuple(int(a1[k] + (b1[k] - a1[k]) * min(1.0, d * 1.2)) for k in range(3)) + (255,)
            else:
                q[i, j] = (22, 28, 48, 255)
    for _ in range(GRIETAS[clave]):
        x, y = r.randrange(4, 12), r.randrange(4, 12)
        for _ in range(r.randint(2, 4)):
            if 0 <= x < S and 0 <= y < S and q[x, y][3] and q[x, y][:3] != (16, 20, 34):
                q[x, y] = (255, 250, 220, 255) if clave == 4 else (12, 10, 22, 255)
            x += r.choice((-1, 0, 1))
            y += r.choice((-1, 1))
    im.save(os.path.join(GUI, f'aeralis_barra_nucleo_{clave}.png'))


# --------------------------------------------------------------- muescas: una pluma, entera o rasgada
def pluma(rota):
    im = Image.new('RGBA', (6, 12), (0, 0, 0, 0))
    q = im.load()
    for y in range(12):
        for x in range(6):
            ancho = 2.6 * math.sin(math.pi * (y + 0.5) / 12)
            if abs(x + 0.5 - 3) <= ancho:
                if rota and 4 <= y <= 7 and x >= 3:
                    continue                           # rasgada por el viento
                q[x, y] = PLATA[4] if x == 2 or x == 3 else PLATA[2] if x < 3 else PLATA[1]
    return im


pluma(False).save(os.path.join(GUI, 'aeralis_barra_pluma.png'))
pluma(True).save(os.path.join(GUI, 'aeralis_barra_pluma_rota.png'))

# --------------------------------------------------------------- letras en pixel
GLIFOS = {
    'A': [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    'E': ["######", "##....", "##....", "#####.", "##....", "##....", "######"],
    'R': ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    'L': ["##....", "##....", "##....", "##....", "##....", "##....", "######"],
    'I': ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    'S': [".#####", "##....", "##....", ".####.", "....##", "....##", "#####."],
    'F': ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    'V': ["##..##", "##..##", "##..##", "##..##", ".####.", ".####.", "..##.."],
    'B': ["#####.", "##..##", "##..##", "#####.", "##..##", "##..##", "#####."],
    ' ': ["..", "..", "..", "..", "..", "..", ".."],
}


def palabra(texto, relleno, borde, sombra, ancho=None, derecha=False):
    puntos = set()
    x = 0
    for ch in texto:
        g = GLIFOS[ch]
        for fy, fila in enumerate(g):
            for fx, c in enumerate(fila):
                if c == '#':
                    puntos.add((x + fx, fy))
        x += len(g[0]) + 1
    w_txt = x - 1 + 2
    w = ancho or w_txt
    h = 10
    ox = (w - w_txt if derecha else 0) + 1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    q = im.load()
    for (px, py) in puntos:
        for dx in (0, 1, -1):
            xx, yy = px + ox + dx, py + 3
            if 0 <= xx < w and 0 <= yy < h:
                q[xx, yy] = sombra
    for (px, py) in puntos:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = px + ox + dx, py + 1 + dy
                if 0 <= xx < w and 0 <= yy < h and (px + dx, py + dy) not in puntos:
                    q[xx, yy] = borde
    for (px, py) in puntos:
        q[px + ox, py + 1] = relleno(py)
    return im


def cielo(fila):
    rampa = ['ffffff', 'f2fbff', 'e0f3ff', 'c8e9fc', 'acdaf6', '90c8ee', '78b4e0']
    return hexc(rampa[fila])


def gris(fila):
    v = [255, 246, 236, 224, 210, 196, 182][fila]
    return (v, v, v, 255)


BORDE = hexc('0a0e18')
SOMBRA = (0, 0, 0, 110)
nombre = palabra('AERALIS', cielo, BORDE, SOMBRA)
nombre.save(os.path.join(GUI, 'aeralis_barra_nombre.png'))
ANCHO_FASE = 64
for n, romano in ((1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV')):
    palabra('FASE ' + romano, gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, f'aeralis_barra_fase_{n}.png'))
palabra('LIBRE', gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, 'aeralis_barra_libre.png'))
print('nombre', nombre.size, 'fase', (ANCHO_FASE, 10))

if len(sys.argv) > 2:
    prev = Image.new('RGBA', (208 * 4, 26 * 4 + 120), (90, 110, 150, 255))
    marco = Image.open(os.path.join(GUI, 'aeralis_barra_marco.png'))
    prev.alpha_composite(marco.resize((832, 104), Image.NEAREST), (0, 30))
    prev.alpha_composite(nombre.resize((nombre.width * 4, 40), Image.NEAREST), (28 * 4, 0))
    x = 4
    for clave in (1, 2, 3, 4, 'libre'):
        im = Image.open(os.path.join(GUI, f'aeralis_barra_nucleo_{clave}.png')).resize((64, 64), Image.NEAREST)
        prev.alpha_composite(im, (x, 140))
        x += 80
    prev.alpha_composite(Image.open(os.path.join(GUI, 'aeralis_barra_viento.png')).resize((192, 24), Image.NEAREST), (x + 10, 150))
    prev.alpha_composite(Image.open(os.path.join(GUI, 'aeralis_barra_pluma.png')).resize((24, 48), Image.NEAREST), (x + 220, 140))
    prev.alpha_composite(Image.open(os.path.join(GUI, 'aeralis_barra_pluma_rota.png')).resize((24, 48), Image.NEAREST), (x + 250, 140))
    prev.save(sys.argv[2])
    print('ok')

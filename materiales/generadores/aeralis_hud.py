"""
La barra de jefe de Aeralis del remake (octubre de 2026), pintada pixel a pixel
(nada de la de vanilla). Las piezas (en grises lo que tine el juego):

  aeralis_barra_marco_N.png      el marco de cada fase (240x44): el ala que sale
                                 del emblema por encima de la barra (con su ocelo y
                                 el filo encendido), otra pequena detras, la nube de
                                 tormenta del marco, el hueco del relleno y el aro
                                 del emblema con la corona de puas; y el liberado
  aeralis_barra_relleno_N.png    el relleno de cada fase (64x9, se repite y corre):
                                 la tormenta oscura abajo, el color y el filo claro
                                 arriba, con vetas de viento
  aeralis_barra_nucleo_N.png     el ojo de la tormenta del emblema (24x24)
  aeralis_barra_ojo*.png         las muescas de fase: un ojo de tormenta en grises
                                 (se tine) o apagado al pasarlo (7x7)
  aeralis_barra_cristal*.png     los nucleos del Juicio bajo la barra, en pie (en
                                 grises) o rotos (5x9)
  aeralis_barra_nombre.png       "AERALIS" en letras de pixel
  aeralis_barra_fase_N.png       "FASE I".."FASE IV" y aeralis_barra_libre.png

La antigua (marco de 208x26 con dos alitas, viento en grises y plumas) se quito;
su diseno de propuesta esta en viento_remake_hud.py.

Uso: python aeralis_hud.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image
import math, os, sys

RAIZ = sys.argv[1]
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
os.makedirs(GUI, exist_ok=True)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


NUBE = [hexc(c) for c in ('0e121c', '1c2232', '323c52', '56627c', '8592ac', 'c8d2e2')]
RAMPAS = {
    1: ('10283c', '1d4f74', '2f86b8', '5fd2ff', 'a8ecff', 'f2ffff'),
    2: ('141838', '242c70', '3e4cb0', '7f8cff', 'bcc4ff', 'eef0ff'),
    3: ('1c1238', '3a2470', '6c48b8', 'b07cff', 'dcc0ff', 'fff7d6'),
    4: ('2a0a26', '5c1452', 'a42c8c', 'ff4fd8', 'ffb0ee', 'ffffff'),
    'libre': ('5a3a10', '9a6a1a', 'd6a032', 'ffc23a', 'ffe9a8', 'fffbe0'),
}

# Medidas (las mismas en AeralisBarraHud)
NW, NH = 240, 44
HX0, HX1, HY0, HY1 = 40, 230, 22, 31
EC = (19, 26)
ER = 15.5
NUCLEO = 24


def dentro(poly, x, y):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1:
            c = not c
    return c


def marco(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
    px = im.load()

    def pon(x, y, c):
        if 0 <= x < NW and 0 <= y < NH:
            px[x, y] = c

    def ala(poly, ocelo, raiz):
        pts = {(x, y) for y in range(NH) for x in range(NW) if dentro(poly, x + 0.5, y + 0.5)}
        largo = max(math.hypot(x - raiz[0], y - raiz[1]) for x, y in pts)
        for (x, y) in pts:
            vec = sum((x + dx, y + dy) in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            d = math.hypot(x - raiz[0], y - raiz[1]) / largo
            if (x, y - 1) not in pts:
                pon(x, y, NUBE[0])
            elif vec < 4:
                pon(x, y, R[4])
            else:
                c = NUBE[1] if d < 0.3 else R[1] if d < 0.55 else R[2] if d < 0.8 else R[3]
                if (x * 2 + y * 3) % 9 == 0 and d > 0.4:
                    c = R[4]
                pon(x, y, (*c[:3], 240))
        ox, oy, orad = ocelo
        for dy in range(-orad, orad + 1):
            for dx in range(-orad, orad + 1):
                dd = math.hypot(dx, dy)
                if dd <= orad + 0.4 and (ox + dx, oy + dy) in pts:
                    pon(ox + dx, oy + dy, R[5] if dd < orad * 0.4 else R[3] if dd < orad * 0.75 else NUBE[0])

    ala([(30, 21), (38, 13), (52, 6), (70, 2), (88, 1), (92, 4), (88, 10), (80, 15), (66, 19), (48, 22)], (70, 9, 3), (30, 21))
    ala([(10, 16), (6, 10), (1, 6), (0, 9), (2, 15), (6, 19)], (4, 11, 1), (10, 16))
    # el marco de nube de tormenta y el hueco vacio
    for y in range(HY0 - 3, HY1 + 3):
        for x in range(HX0 - 8, HX1 + 3):
            if HX0 <= x < HX1 and HY0 <= y < HY1:
                pon(x, y, (*NUBE[0][:3], 255))
                continue
            if y in (HY0 - 3, HY1 + 2) or x in (HX0 - 8, HX1 + 2):
                pon(x, y, NUBE[0])
            elif y == HY0 - 2:
                pon(x, y, NUBE[4])
            elif y == HY1 + 1:
                pon(x, y, NUBE[1])
            else:
                pon(x, y, NUBE[2] if (x + y) % 5 else NUBE[3])
    # la corona de puas y el aro del emblema (el ojo va aparte)
    for k in range(5):
        ang = math.radians(-90 + (k - 2) * 28)
        for q in range(4):
            x = round(EC[0] + math.cos(ang) * (ER + q))
            y = round(EC[1] + math.sin(ang) * (ER + q))
            pon(x, y, R[4] if q == 3 else NUBE[1])
            pon(x + 1, y, NUBE[0] if q < 3 else R[3])
    for y in range(NH):
        for x in range(40):
            d = math.hypot(x + 0.5 - EC[0], y + 0.5 - EC[1])
            if d <= ER:
                pon(x, y, NUBE[0] if d > ER - 1.2 else R[4] if d > ER - 2.6 else NUBE[1] if d > ER - 3.6 else NUBE[0])
    return im


def relleno(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    w, h = 64, HY1 - HY0
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            c = R[[4, 3, 3, 2, 2, 2, 1, 1, 0][min(8, y)]]
            if (x + y * 2) % 16 < 3 and 1 <= y <= 6:
                c = R[4]
            px[x, y] = c
    return im


def nucleo(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    im = Image.new('RGBA', (NUCLEO, NUCLEO), (0, 0, 0, 0))
    px = im.load()
    c0 = NUCLEO / 2
    rmax = ER - 3.6
    for y in range(NUCLEO):
        for x in range(NUCLEO):
            d = math.hypot(x + 0.5 - c0, y + 0.5 - c0)
            if d > rmax:
                continue
            a = math.atan2(y + 0.5 - c0, x + 0.5 - c0)
            brazo = (a - 2.6 * math.log(max(d, 0.5) / rmax)) % (2 * math.pi / 3) < 0.95
            px[x, y] = R[5] if d < 2.2 else (R[3] if d < 6 else R[2]) if brazo else NUBE[0]
    return im


def ojo(apagado):
    im = Image.new('RGBA', (7, 7), (0, 0, 0, 0))
    px = im.load()
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            d = abs(dx) + abs(dy)
            if d > 3:
                continue
            if apagado:
                c = NUBE[1] if d < 3 else NUBE[0]
            else:
                v = [255, 205, 130, 40][d]
                c = (v, v, v, 255)
            px[3 + dx, 3 + dy] = c
    return im


def cristal(roto):
    im = Image.new('RGBA', (5, 9), (0, 0, 0, 0))
    px = im.load()
    for dy in range(-4, 5):
        semi = 2 - abs(dy) // 2
        for dx in range(-semi, semi + 1):
            borde = abs(dx) == semi or abs(dy) == 4
            if roto:
                c = NUBE[0] if borde else NUBE[2]
            else:
                v = 255 if dx == 0 and dy < 0 else 60 if borde else 190
                c = (v, v, v, 255)
            px[2 + dx, 4 + dy] = c
    return im


for clave in (1, 2, 3, 4, 'libre'):
    marco(clave).save(os.path.join(GUI, f'aeralis_barra_marco_{clave}.png'))
    relleno(clave).save(os.path.join(GUI, f'aeralis_barra_relleno_{clave}.png'))
    nucleo(clave).save(os.path.join(GUI, f'aeralis_barra_nucleo_{clave}.png'))
ojo(False).save(os.path.join(GUI, 'aeralis_barra_ojo.png'))
ojo(True).save(os.path.join(GUI, 'aeralis_barra_ojo_apagado.png'))
cristal(False).save(os.path.join(GUI, 'aeralis_barra_cristal.png'))
cristal(True).save(os.path.join(GUI, 'aeralis_barra_cristal_roto.png'))
for viejo in ('aeralis_barra_marco.png', 'aeralis_barra_viento.png', 'aeralis_barra_pluma.png', 'aeralis_barra_pluma_rota.png'):
    if os.path.exists(os.path.join(GUI, viejo)):
        os.remove(os.path.join(GUI, viejo))

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
    'U': ["##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
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
# La Furia del Vendaval (el Juicio fallido): en grises, el juego lo tine y lo hace latir.
palabra('FURIA', gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, 'aeralis_barra_furia.png'))
print('barra', (NW, NH), '| nombre', nombre.size, '| fase', (ANCHO_FASE, 10))

if len(sys.argv) > 2:
    # La barra montada como en el juego, en las cuatro fases y liberada, a x3.
    K = 3
    filas = []
    for clave, vida in ((1, 0.92), (2, 0.66), (3, 0.41), (4, 0.18), ('libre', 0.0)):
        b = Image.open(os.path.join(GUI, f'aeralis_barra_marco_{clave}.png')).copy()
        rel = Image.open(os.path.join(GUI, f'aeralis_barra_relleno_{clave}.png'))
        lleno = round((HX1 - HX0) * vida)
        for x in range(0, lleno, 64):
            b.alpha_composite(rel.crop((0, 0, min(64, lleno - x), rel.height)), (HX0 + x, HY0))
        b.alpha_composite(Image.open(os.path.join(GUI, f'aeralis_barra_nucleo_{clave}.png')), (EC[0] - NUCLEO // 2, EC[1] - NUCLEO // 2))
        filas.append(b.resize((NW * K, NH * K), Image.NEAREST))
    prev = Image.new('RGBA', (NW * K + 20, (NH * K + 10) * len(filas) + 10), (40, 56, 92, 255))
    for k, f in enumerate(filas):
        prev.alpha_composite(f, (10, 10 + k * (NH * K + 10)))
    prev.save(sys.argv[2])
    print('ok')

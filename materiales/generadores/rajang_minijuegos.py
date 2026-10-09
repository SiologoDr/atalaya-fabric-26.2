"""
Las texturas de los minijuegos de Rajang (octubre de 2026): El Rayo del Prisma,
El Impostor de Jade, Glifos del Templo y Suelo que se Hunde. Con la paleta del
templo (el jade de los totems y el oro del idolo, ver idolo_oro.py) y las
reglas de DISENO.md: silueta como datos, rampa de cinco tonos con el borde
tenido del color, nada de negro ni blanco puros.

  item/prisma_jade.png              el Prisma de Jade (16 x 16): el cristal en su engaste de oro
  entity/rajang/trampa.png          la trampa de oro (64 x 64): el aro de oro con greca, el fondo
                                    del hoyo pintado con su hondura, los pinchos de jade y las
                                    cabezas de jaguar de las esquinas
  entity/rajang/luz_prisma.png      el punto de luz del prisma (32 x 32), en pixeles
  entity/rajang/luz_rayo.png        el rayo (16 x 8): el alma clara y el canto de jade
  entity/rajang/glifo_columna.png   la columna de los glifos (128 x 64): fuste, zocalo y capitel
  entity/rajang/glifos.png          los ocho glifos tallados (192 x 24, 24 cada uno)
  entity/rajang/glifos_brillo.png   lo que brilla de cada glifo (el mismo dibujo, encendido)
  entity/rajang/losa.png            la losa del Suelo que se Hunde (48 x 64, 3 x 3 bloques): cara, canto y tapa
  entity/rajang/losa_grietas.png    las tres grietas de la losa pisada (48 x 144)
  particle/rajang_huella.png        la huella de jaguar del impostor (16 x 16)
  gui/rajang_glifos.png             los ocho glifos para el panel del Vidente (192 x 24)

Uso: python rajang_minijuegos.py <raiz del proyecto> [hoja.png]
"""
import math
import os
import random
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
ASSETS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')

# El jade del templo (los totems y el pilar del altar) y el oro del idolo.
JUNTA = (16, 30, 21)
JADE_OSC = (27, 49, 34)
JADE = (36, 66, 45)
JADE_CLARO = (50, 90, 61)
JADE_LUZ = (74, 124, 88)
ORO_CANTO = (110, 70, 16)
ORO_SOMBRA = (150, 96, 22)
ORO = (211, 154, 34)
ORO_CLARO = (255, 194, 58)
ORO_BRILLO = (255, 240, 168)
# El jade encendido (la maldicion de los glifos y las grietas).
VERDE_HONDO = (40, 120, 60)
VERDE = (90, 200, 100)
VERDE_VIVO = (140, 255, 90)
VERDE_NUCLEO = (226, 255, 196)


def lienzo(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def pon(im, x, y, c, a=255):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), tuple(c) + (a,))


def mezcla(a, b, k):
    return tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


def de_ascii(im, x0, y0, filas, colores):
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch in colores:
                pon(im, x0 + x, y0 + y, colores[ch])


def piedra_jade(im, x0, y0, w, h, sem, hiladas=8, vetas=True):
    """Sillares de jade: hiladas de bloques con su junta, cada bloque de un
    tono algo distinto y alguna veta clara (la piedra de los totems)."""
    r = random.Random(sem)
    y = 0
    fila = 0
    while y < h:
        alto = min(hiladas, h - y)
        x = -(r.randrange(3, 9) if fila % 2 else 0)
        while x < w:
            ancho = r.randrange(7, 13)
            base = r.choice((JADE, JADE, JADE_OSC, JADE_CLARO))
            for yy in range(alto):
                for xx in range(ancho):
                    px, py = x + xx, y + yy
                    if not (0 <= px < w):
                        continue
                    if yy == alto - 1 or xx == ancho - 1:
                        c = JUNTA
                    elif yy == 0 or xx == 0:
                        c = mezcla(base, JADE_LUZ, 0.35)
                    else:
                        c = base
                        if r.random() < 0.12:
                            c = mezcla(base, JUNTA, 0.35)
                    pon(im, x0 + px, y0 + py, c)
            if vetas and r.random() < 0.35:
                # una veta clara en diagonal
                vx, vy = x + r.randrange(1, max(2, ancho - 2)), y + 1
                for k in range(r.randrange(2, 5)):
                    if 0 <= vx + k < w and vy + k < y + alto - 1:
                        pon(im, x0 + vx + k, y0 + vy + k, JADE_LUZ)
            x += ancho
        y += alto
        fila += 1


def greca_oro(im, x0, y0, w, h):
    """Banda de oro con la greca escalonada del templo (la del peto de Rajang)."""
    for y in range(h):
        for x in range(w):
            if y == 0:
                c = ORO_BRILLO if x % 4 else ORO_CLARO
            elif y == h - 1:
                c = ORO_CANTO
            else:
                # el escalon: sube y baja cada 8 pixeles
                k = x % 8
                alto = 1 + (k if k < 4 else 7 - k) * (h - 3) // 3
                c = ORO_SOMBRA if y == alto or y == alto + 1 else (ORO_CLARO if y < alto else ORO)
            pon(im, x0 + x, y0 + y, c)


# ======================================================================
#  EL PRISMA DE JADE (item)
# ======================================================================
PRISMA = [
    '................',
    '.......bb.......',
    '......bNCb......',
    '......bNCMb.....',
    '.....bNCCMb.....',
    '.....bNCCMSb....',
    '....bNCCCMSb....',
    '....bNCCMMSb....',
    '...bNCCCMMSSb...',
    '...bNCCCMMSSb...',
    '...bCCCMMMSSb...',
    '..OYYWYYYYYYGO..',
    '..ODGGGjGGGGDO..',
    '...OGDDDDDDGO...',
    '....OODDDDOO....',
    '......OOOO......',
]
PRISMA_COLOR = {
    'b': (14, 58, 34), 'S': (28, 104, 60), 'M': (48, 160, 92), 'C': (110, 222, 140), 'N': (214, 255, 200),
    'O': ORO_CANTO, 'D': ORO_SOMBRA, 'G': ORO, 'Y': ORO_CLARO, 'W': ORO_BRILLO, 'j': VERDE_VIVO,
}


def prisma():
    im = lienzo(16, 16)
    de_ascii(im, 0, 0, PRISMA, PRISMA_COLOR)
    # dos motas de luz sueltas (DISENO.md, punto 8)
    pon(im, 12, 2, (180, 255, 190))
    pon(im, 2, 6, (110, 222, 140))
    return im


# ======================================================================
#  LA TRAMPA DE ORO
# ======================================================================
def trampa():
    im = lienzo(64, 64)
    # El canto del aro: la greca de oro.
    greca_oro(im, 0, 0, 64, 8)
    # La cara de arriba del aro: oro con incrustaciones de jade cada bloque.
    for y in range(8):
        for x in range(64):
            c = ORO if (x + y) % 5 else ORO_CLARO
            if y in (0, 7):
                c = ORO_SOMBRA
            if 2 <= y <= 5 and x % 16 in (6, 7, 8, 9):
                c = VERDE if y in (3, 4) and x % 16 in (7, 8) else JADE_CLARO
            pon(im, x, 8 + y, c)
    # El fondo del hoyo (3 x 3 bloques): las paredes pintadas en perspectiva,
    # cada vez mas hondas, y el suelo de piedra negra con raices.
    r = random.Random(11)
    for y in range(48):
        for x in range(48):
            d = min(x, y, 47 - x, 47 - y)
            if d < 10:
                # la pared: hiladas que se estrechan al bajar
                k = d / 10.0
                base = mezcla(JADE_OSC, (8, 14, 10), k)
                if d % 3 == 2:
                    base = mezcla(base, JUNTA, 0.6)
                c = base
            else:
                c = (10, 17, 12) if r.random() < 0.8 else (16, 26, 19)
            pon(im, x, 16 + y, c)
    # Unas raices sueltas en el fondo.
    for _ in range(5):
        x, y = r.randrange(12, 36), r.randrange(12, 36)
        for k in range(r.randrange(3, 7)):
            pon(im, x + k, 16 + y + (k // 2), (34, 26, 16))
    # El pincho de jade: un cristal que se aclara hacia la punta.
    for y in range(16):
        for x in range(16):
            k = y / 15.0
            c = mezcla((150, 255, 170), (30, 110, 62), k)
            if x in (0, 15):
                c = mezcla(c, (14, 58, 34), 0.6)
            elif x in (5, 6):
                c = mezcla(c, VERDE_NUCLEO, 0.35)
            pon(im, 48 + x, 16 + y, c)
    # La cabeza de jaguar de oro de las esquinas (cara y tapa).
    CABEZA = [
        'OOOO........OOOO',
        'OYGO........OGYO',
        'OGGOOOOOOOOOOGGO',
        'OGYYYYYYYYYYYYGO',
        'OGYWYYYYYYYYWYGO',
        'OGjJjYYYYYYjJjGO',
        'OGjjjGYYYYGjjjGO',
        'OGGGGGYYYYGGGGGO',
        'OGYYYYDDDDYYYYGO',
        'OGYYYYDDDDYYYYGO',
        'OGGYYYYDDYYYYGGO',
        'OGDYWYYYYYYWYDGO',
        'OGDDWOWOOWOWDDGO',
        'OGGDDDDDDDDDDGGO',
        'OOGGGGGGGGGGGGOO',
        'OOOOOOOOOOOOOOOO',
    ]
    col = {'O': ORO_CANTO, 'D': ORO_SOMBRA, 'G': ORO, 'Y': ORO_CLARO, 'W': ORO_BRILLO, 'J': JADE_CLARO, 'j': VERDE_VIVO}
    de_ascii(im, 48, 32, CABEZA, col)
    for y in range(16):
        for x in range(16):
            d = min(x, y, 15 - x, 15 - y)
            c = ORO_CANTO if d == 0 else ORO_SOMBRA if d == 1 else (ORO_CLARO if (x + y) % 2 else ORO)
            if d == 4:
                c = ORO_SOMBRA
            if 5 <= x <= 10 and 5 <= y <= 10:
                c = VERDE if 6 <= x <= 9 and 6 <= y <= 9 else JADE_CLARO
            pon(im, 48 + x, 48 + y, c)
    return im


# ======================================================================
#  LA LUZ DEL PRISMA
# ======================================================================
def luz():
    im = lienzo(32, 32)
    c = 15.5
    for y in range(32):
        for x in range(32):
            dx, dy = abs(x - c), abs(y - c)
            d = max(dx, dy) * 0.55 + (dx + dy) * 0.45   # un octogono de pixeles
            rayo = (min(dx, dy) < 1.0 and max(dx, dy) < 15) or (abs(dx - dy) < 0.8 and max(dx, dy) < 9)
            if d < 3.0:
                pon(im, x, y, VERDE_NUCLEO, 255)
            elif d < 5.5:
                pon(im, x, y, (170, 255, 170), 240)
            elif d < 8.5:
                pon(im, x, y, VERDE_VIVO, 190)
            elif d < 11.0:
                pon(im, x, y, VERDE, 120)
            elif rayo:
                pon(im, x, y, VERDE_VIVO, int(200 * (1 - max(dx, dy) / 16)))
            elif d < 12.5 and (x + y) % 2 == 0:
                pon(im, x, y, VERDE, 70)
    return im


def rayo():
    im = lienzo(16, 8)
    filas = [(VERDE, 70), (VERDE_VIVO, 150), ((180, 255, 180), 230), (VERDE_NUCLEO, 255),
             (VERDE_NUCLEO, 255), ((180, 255, 180), 230), (VERDE_VIVO, 150), (VERDE, 70)]
    for y, (c, a) in enumerate(filas):
        for x in range(16):
            # unos pulsos de luz que corren por el rayo
            k = 1.0 if (x // 2) % 4 else 0.82
            pon(im, x, y, mezcla(c, (255, 255, 255), 0.0) if k == 1.0 else mezcla(c, VERDE, 0.3), int(a * k))
    return im


# ======================================================================
#  GLIFOS DEL TEMPLO
# ======================================================================
# Ocho glifos de 20 x 20 (el panel mide 24 con el marco). Macizos y gruesos,
# que se distingan de lejos y se puedan nombrar: Jaguar, Serpiente, Sol, Luna,
# Mano, Calavera, Piramide y Ojo. El orden es el de MinijuegosRajang.GLIFOS.
JAGUAR = [
    '....................',
    '.###............###.',
    '.####..........####.',
    '.#####........#####.',
    '.##################.',
    '.##################.',
    '.###....####....###.',
    '.###.##.####.##.###.',
    '.###....####....###.',
    '.##################.',
    '.########..########.',
    '..######....######..',
    '..#######..#######..',
    '..##.#########.#.#..',
    '...##.##....##.##...',
    '...###..####..###...',
    '....############....',
    '.....##########.....',
    '.......######.......',
    '....................',
]
SERPIENTE = [
    '....................',
    '........#####.......',
    '.......#######......',
    '......###.##.##.....',
    '......#########.##..',
    '.......#######.#....',
    '.....####...........',
    '....####............',
    '....####............',
    '.....########.......',
    '.......#########....',
    '............#####...',
    '.............####...',
    '.............####...',
    '...##.......####....',
    '..####....######....',
    '..###########.......',
    '...#########........',
    '.....####...........',
    '....................',
]
MANO = [
    '....................',
    '.......##..##.......',
    '....##.##..##.##....',
    '....##.##..##.##....',
    '....##.##..##.##....',
    '....##.##..##.##....',
    '....##.##..##.##....',
    '....############..##',
    '....############.###',
    '....###########.###.',
    '....##############..',
    '....#############...',
    '....###...######....',
    '....###.#.######....',
    '....###...######....',
    '.....##########.....',
    '.....##########.....',
    '......########......',
    '......########......',
    '....................',
]
CALAVERA = [
    '....................',
    '......########......',
    '....############....',
    '...##############...',
    '..################..',
    '..################..',
    '..###....##....###..',
    '..###....##....###..',
    '..###....##....###..',
    '..#######..#######..',
    '...######..######...',
    '....############....',
    '.....##########.....',
    '.....#.#.##.#.#.....',
    '.....##########.....',
    '......#.#..#.#......',
    '......########......',
    '....................',
    '....................',
    '....................',
]


def glifo_formula(nombre):
    s = [[False] * 20 for _ in range(20)]
    c = 9.5
    for y in range(20):
        for x in range(20):
            dx, dy = x - c, y - c
            d = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            if nombre == 'sol':
                rayo = d < 9.6 and abs(math.sin(a * 4)) < 0.38 and d > 6.2
                s[y][x] = d < 5.2 or rayo
                if 2.0 < d < 3.2:
                    s[y][x] = False
            elif nombre == 'luna':
                s[y][x] = d < 8.6 and math.hypot(dx - 4.2, dy + 2.0) > 6.6
            elif nombre == 'piramide':
                # cuatro gradas y el templo arriba, con la escalinata en medio
                fila = y - 3
                if 0 <= fila < 4:
                    s[y][x] = abs(dx) < 2.6
                elif 4 <= fila < 16:
                    grada = (fila - 4) // 3
                    s[y][x] = abs(dx) < 4.6 + grada * 2.0
                if 7 <= y <= 18 and abs(dx) < 1.0:
                    s[y][x] = (y % 2 == 0)
                if 4 <= y <= 5 and abs(dx) < 1.0:
                    s[y][x] = False
            elif nombre == 'ojo':
                almendra = abs(dy) < 7.5 * (1 - (dx / 9.6) ** 2) if abs(dx) < 9.6 else False
                s[y][x] = almendra and not (d < 4.6 and d > 2.0)
                if d < 2.0:
                    s[y][x] = True
                if abs(dy) < 7.5 * (1 - (dx / 9.6) ** 2) - 2.0 and d >= 4.6:
                    s[y][x] = False
    return s


def de_filas(filas):
    return [[ch == '#' for ch in fila] for fila in filas]


GLIFOS = [
    ('jaguar', de_filas(JAGUAR)),
    ('serpiente', de_filas(SERPIENTE)),
    ('sol', glifo_formula('sol')),
    ('luna', glifo_formula('luna')),
    ('mano', de_filas(MANO)),
    ('calavera', de_filas(CALAVERA)),
    ('piramide', glifo_formula('piramide')),
    ('ojo', glifo_formula('ojo')),
]


def panel_glifo(im, x0, s, modo):
    """modo 'talla': el glifo tallado hondo en el jade, con su marco de oro.
    'brillo': solo el glifo, encendido (se pinta encima a plena luz).
    'hud': oro sobre jade oscuro, para el panel del Vidente."""
    for y in range(24):
        for x in range(24):
            marco = min(x, y, 23 - x, 23 - y)
            gx, gy = x - 2, y - 2
            dentro = 0 <= gx < 20 and 0 <= gy < 20 and s[gy][gx]
            if modo == 'talla':
                if marco == 0:
                    c = ORO_CANTO
                elif marco == 1:
                    c = ORO_CLARO if (x + y) % 3 else ORO
                elif dentro:
                    # la talla: mas honda arriba (sombra) y con el canto de abajo claro
                    arriba = gy > 0 and not s[gy - 1][gx]
                    c = JUNTA if arriba else (14, 26, 18)
                else:
                    abajo_talla = gy > 0 and 0 <= gx < 20 and gy - 1 < 20 and s[gy - 1][gx]
                    c = JADE_LUZ if abajo_talla else (JADE if (x * 7 + y * 3) % 11 else JADE_CLARO)
                pon(im, x0 + x, y, c)
            elif modo == 'brillo':
                if dentro:
                    borde = any(not (0 <= gx + a < 20 and 0 <= gy + b < 20 and s[gy + b][gx + a])
                                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    pon(im, x0 + x, y, VERDE_VIVO if borde else (200, 255, 170))
            else:
                if marco == 0:
                    c = ORO_CANTO
                elif dentro:
                    borde = any(not (0 <= gx + a < 20 and 0 <= gy + b < 20 and s[gy + b][gx + a])
                                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    c = ORO if borde else ORO_CLARO
                else:
                    c = (12, 26, 17) if (x + y) % 2 else (16, 32, 21)
                pon(im, x0 + x, y, c)


def glifos(modo):
    im = lienzo(24 * len(GLIFOS), 24)
    for i, (_, s) in enumerate(GLIFOS):
        panel_glifo(im, 24 * i, s, modo)
    return im


def columna():
    im = lienzo(128, 64)
    # El fuste (26 x 52): sillares de jade; el panel del glifo lo pone el renderer.
    piedra_jade(im, 0, 0, 26, 52, 7, 9)
    # Una franja de oro arriba y abajo del fuste.
    greca_oro(im, 0, 0, 26, 3)
    greca_oro(im, 0, 49, 26, 3)
    # El zocalo: canto con greca (35 x 8) y la cara de arriba (35 x 35).
    greca_oro(im, 26, 0, 35, 8)
    piedra_jade(im, 26, 8, 35, 35, 8, 7)
    for i in range(35):
        for (x, y) in ((26 + i, 8), (26 + i, 42), (26, 8 + i), (60, 8 + i)):
            pon(im, x, y, ORO)
    # El capitel: canto (32 x 8) y tapa (32 x 32), con el sol de jade en medio.
    greca_oro(im, 64, 0, 32, 8)
    piedra_jade(im, 64, 8, 32, 32, 9, 8, False)
    for y in range(32):
        for x in range(32):
            d = math.hypot(x - 15.5, y - 15.5)
            if d < 4.5:
                pon(im, 64 + x, 8 + y, VERDE if d < 2.5 else JADE_LUZ)
            elif d < 5.8:
                pon(im, 64 + x, 8 + y, ORO_CLARO)
            if min(x, y, 31 - x, 31 - y) == 0:
                pon(im, 64 + x, 8 + y, ORO_SOMBRA)
    return im


# ======================================================================
#  SUELO QUE SE HUNDE: la losa y sus grietas
# ======================================================================
# La losa mide 3 x 3 bloques: 48 pixeles, a 16 por bloque como el resto.
L = 48


def losa():
    im = lienzo(L, L + 16)
    r = random.Random(23)
    m0 = (L - 1) / 2.0
    # La cara: jade pulido, el filo de oro y el rombo del templo.
    for y in range(L):
        for x in range(L):
            d = min(x, y, L - 1 - x, L - 1 - y)
            if d == 0:
                c = ORO_CANTO
            elif d == 1:
                c = ORO if (x + y) % 2 else ORO_CLARO
            elif d == 2:
                c = JUNTA
            else:
                c = JADE if r.random() < 0.78 else (JADE_CLARO if r.random() < 0.6 else JADE_OSC)
            pon(im, x, y, c)
    # El rombo de en medio, con el ojo de jade, y unas esquinas de oro.
    for y in range(L):
        for x in range(L):
            m = abs(x - m0) + abs(y - m0)
            if 10.5 < m < 12.6:
                pon(im, x, y, ORO_SOMBRA)
            elif m < 4.8:
                pon(im, x, y, VERDE if m < 2.4 else JADE_LUZ)
            elif 4.8 <= m < 6.3:
                pon(im, x, y, ORO_CLARO)
            esquina = min(x, L - 1 - x) + min(y, L - 1 - y)
            if 4 <= min(x, L - 1 - x) <= 6 and 4 <= min(y, L - 1 - y) <= 6 and esquina <= 11:
                pon(im, x, y, ORO_SOMBRA if esquina == 11 else ORO)
    # Unas vetas claras.
    for _ in range(7):
        vx, vy = r.randrange(5, L - 8), r.randrange(5, L - 8)
        for k in range(4):
            if abs(vx + k - m0) + abs(vy + k - m0) > 14:
                pon(im, vx + k, vy + k, JADE_LUZ)
    # El canto (L x 8): piedra de jade con la junta y el filo de oro arriba.
    piedra_jade(im, 0, L, L, 8, 31, 8)
    for x in range(L):
        pon(im, x, L, ORO_CLARO if x % 3 else ORO)
    # La cara de abajo: piedra oscura.
    for y in range(8):
        for x in range(L):
            pon(im, x, L + 8 + y, JADE_OSC if (x + y) % 3 else JUNTA)
    return im


def grietas():
    """Tres grietas que crecen desde donde se pisa: la raja oscura con el
    jade encendido dentro (la luz de la maldicion que sale por ella)."""
    im = lienzo(L, 3 * L)
    r = random.Random(5)
    m0 = (L - 1) / 2.0
    ramas = []
    # Ramas que salen del centro hacia fuera, con quiebros.
    for i in range(8):
        a = 2 * math.pi * i / 8 + r.uniform(-0.3, 0.3)
        p = [(m0, m0)]
        x, y = m0, m0
        largo = r.uniform(22, 33)
        paso = 0
        while paso < largo:
            a += r.uniform(-0.35, 0.35)
            x += math.cos(a)
            y += math.sin(a)
            p.append((x, y))
            paso += 1
        ramas.append(p)
    for etapa in range(3):
        alcance = (0.4, 0.7, 1.0)[etapa]
        for p in ramas:
            hasta = max(2, int(len(p) * alcance))
            for k, (x, y) in enumerate(p[:hasta]):
                xi, yi = int(x), int(y)
                if 1 <= xi < L - 1 and 1 <= yi < L - 1:
                    pon(im, xi, etapa * L + yi, VERDE_VIVO if (k % 3 == 1 and etapa > 0) else (12, 20, 14))
                    # el borde de la raja, algo mas claro
                    if etapa == 2 and k % 2 == 0 and 1 <= xi + 1 < L - 1:
                        pon(im, xi + 1, etapa * L + yi, (20, 34, 24))
        if etapa == 2:
            # el centro hundido
            for y in range(L):
                for x in range(L):
                    if (x - m0) ** 2 + (y - m0) ** 2 < 14:
                        pon(im, x, 2 * L + y, VERDE if (x + y) % 2 else (12, 20, 14))
    return im


# ======================================================================
#  LA HUELLA DEL IMPOSTOR (particula)
# ======================================================================
HUELLA = [
    '................',
    '....##....##....',
    '...####..####...',
    '...####..####...',
    '.##.##....##.##.',
    '####........####',
    '####........####',
    '.##..######..##.',
    '....########....',
    '...##########...',
    '..############..',
    '..############..',
    '..###########...',
    '...##.####.##...',
    '....#......#....',
    '................',
]


def huella():
    im = lienzo(16, 16)
    s = de_filas(HUELLA)
    for y in range(16):
        for x in range(16):
            if s[y][x]:
                borde = any(not (0 <= x + a < 16 and 0 <= y + b < 16 and s[y + b][x + a])
                            for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                pon(im, x, y, (110, 230, 140) if borde else (190, 255, 190))
    return im


# ======================================================================
def guardar(im, ruta):
    ruta = os.path.join(ASSETS, ruta)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    im.save(ruta)
    print('  ', os.path.relpath(ruta, ASSETS), im.size)
    return im


def main():
    hechas = [
        guardar(prisma(), 'textures/item/prisma_jade.png'),
        guardar(trampa(), 'textures/entity/rajang/trampa.png'),
        guardar(luz(), 'textures/entity/rajang/luz_prisma.png'),
        guardar(rayo(), 'textures/entity/rajang/luz_rayo.png'),
        guardar(columna(), 'textures/entity/rajang/glifo_columna.png'),
        guardar(glifos('talla'), 'textures/entity/rajang/glifos.png'),
        guardar(glifos('brillo'), 'textures/entity/rajang/glifos_brillo.png'),
        guardar(losa(), 'textures/entity/rajang/losa.png'),
        guardar(grietas(), 'textures/entity/rajang/losa_grietas.png'),
        guardar(huella(), 'textures/particle/rajang_huella.png'),
        guardar(glifos('hud'), 'textures/gui/rajang_glifos.png'),
    ]
    with open(os.path.join(ASSETS, 'particles/rajang_huella.json'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('{\n  "textures": [\n    "atalaya:rajang_huella"\n  ]\n}\n')
    if len(sys.argv) > 2:
        # Hoja para mirar: todo a x8 sobre el gris del juego.
        escala = 6
        grandes = [h.resize((h.width * escala, h.height * escala), Image.NEAREST) for h in hechas]
        ancho = 1400
        x = y = alto = 0
        pos = []
        for g in grandes:
            if x + g.width > ancho:
                x, y, alto = 0, y + alto + 10, 0
            pos.append((x, y))
            x += g.width + 10
            alto = max(alto, g.height)
        hoja = Image.new('RGBA', (ancho, y + alto), (58, 58, 64, 255))
        for g, p in zip(grandes, pos):
            hoja.paste(g, p, g)
        hoja.save(sys.argv[2])


if __name__ == '__main__':
    main()

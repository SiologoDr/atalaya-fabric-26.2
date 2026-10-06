"""
La barra de jefe de Nerea, pintada aqui pixel a pixel (nada de la de vanilla).
Desde el remake de octubre de 2026 es del tamano y el estilo de la de Aeralis
(240x44), con lo suyo: una ola encima en vez del ala, el corazon entre
costillas en el emblema y eslabones en las muescas.

  nerea_barra_marco_N.png      el marco de cada fase (240x44): la ola que sale
                               del emblema y rompe a la derecha por encima de la
                               barra, el marco de prismarina vieja con percebes y
                               corales, el hueco y el aro del emblema con cuatro
                               eslabones de oxido; y el de la Furia y el liberado
  nerea_barra_relleno_N.png    el agua de cada fase con su cresta de espuma (64x9,
                               se repite y corre)
  nerea_barra_corazon_N.png    el emblema: el corazon maldito entre dos costillas
                               (24x24), cada fase mas rajado; en la IV, abiertas
  nerea_barra_eslabon*.png     las muescas: un eslabon entero o partido (7x10)

  La vista de la Mirada del Abismo (lo que cambia en la barra mientras mira):
  nerea_barra_mascara.png      su calavera con la corona, en lugar del corazon
                               (24x24), con las cuencas vacias
  nerea_barra_ojo.png          un ojo encendido en grises (el juego lo tine del
                               color de la fase), 6x6
  nerea_barra_grieta_N.png     las grietas que le salen con los impactos (1-4)
  nerea_barra_ojo_roto.png     el ojo reventado
  nerea_barra_marea.png        la marea que baja: el tiempo que le queda al rayo,
                               agua en grises que se tine (64x5, en bucle)

  nerea_barra_nombre.png       "NEREA" en letras de pixel
  nerea_barra_fase_N.png       "FASE I".."FASE IV", nerea_barra_libre.png y
                               nerea_barra_furia.png, en grises para tenirlos
  mob_effect/corriente_abismal.png   el icono del efecto Corriente Abismal

Uso: python nerea_hud.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image
import math, os, sys, random

RAIZ = sys.argv[1]
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
os.makedirs(GUI, exist_ok=True)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


PRIS = [hexc(c) for c in ('0b1f21', '173b3c', '22504d', '2f6660', '3f7f76', '5aa596', '8fd0bd')]
HUESO = [hexc(c) for c in ('5c5545', '8a8068', 'b3a98c', 'd3c9aa', 'ece4c8')]
CORAL = [hexc(c) for c in ('7a1636', 'a8204a', 'd8336a', 'f2618f')]
OXIDO = [hexc(c) for c in ('2a1a12', '4a2a18', '6e3c1e', '9a5726', 'c47a3a')]
FONDO = hexc('050e12')
OSCURO = hexc('02080a')
ESPUMA = hexc('eaffff')
# El agua de cada fase (de oscuro a la espuma), la Furia (verde abismo) y el oro de la liberacion.
RAMPAS = {
    1: ('062a36', '0e4e60', '1b8aa4', '3fe0ff', 'a8f4ff', 'eaffff'),
    2: ('1a1240', '2e2a7a', '5c4ac4', '9a6bff', 'd2c2ff', 'f0e4ff'),
    3: ('2c0a3c', '561670', '9a2ac0', 'd43cff', 'f0a8ff', 'ffd8f8'),
    4: ('3a0612', '700e24', 'b81a3e', 'ff2050', 'ffa0b2', 'ffe0e6'),
    'furia': ('021e1a', '064438', '0e8a6c', '20f0b0', '9effe0', 'e6fff6'),
    'libre': ('3a2606', '8f6418', 'c28d28', 'ffc23a', 'ffe9a8', 'fffbe0'),
}
CLAVES = (1, 2, 3, 4, 'furia', 'libre')

# Medidas (las mismas en NereaBarraHud)
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


# --------------------------------------------------------------- el marco
def marco(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    rnd = random.Random(8)
    im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
    px = im.load()

    def pon(x, y, c):
        if 0 <= x < NW and 0 <= y < NH:
            px[x, y] = c

    # la ola: sale del emblema, sube y rompe hacia la derecha por encima de la
    # barra; cuerpo del color de la fase, mas claro arriba, el borde de espuma
    # y el rizo oscuro por dentro
    poly = [(24, 20), (27, 13), (34, 7), (45, 3), (58, 1), (70, 1), (80, 3), (88, 7), (93, 12), (92, 16),
            (88, 13), (83, 11), (78, 12), (76, 15), (79, 18), (86, 20), (100, 20)]
    pts = {(x, y) for y in range(NH) for x in range(110) if dentro(poly, x + 0.5, y + 0.5)}
    for (x, y) in pts:
        arriba = (x, y - 1) not in pts
        borde = any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1)))
        if arriba:
            c = ESPUMA if (x * 5 + y) % 7 else R[5]
        elif (x, y - 2) not in pts:
            c = R[5]
        elif borde:
            c = OSCURO
        else:
            t = (y - 1) / 19.0
            c = R[4] if t < 0.25 else R[3] if t < 0.5 else R[2] if t < 0.75 else R[1]
            if (x + 2 * y) % 9 == 0:
                c = R[4]
        pon(x, y, c)
    for (x, y) in ((84, 14), (85, 14), (86, 15), (82, 13), (81, 14), (81, 15), (83, 16)):
        if (x, y) in pts:
            pon(x, y, R[1])                     # el rizo
    for (x, y) in ((92, 8), (95, 10), (90, 5), (97, 13), (86, 3), (99, 16)):
        pon(x, y, ESPUMA)                       # espuma que salta de la cresta
    # una ola pequena detras del emblema, a la izquierda
    poly2 = [(10, 16), (6, 11), (2, 8), (0, 10), (2, 15), (6, 19)]
    for y in range(NH):
        for x in range(14):
            if dentro(poly2, x + 0.5, y + 0.5):
                pon(x, y, R[4] if y < 11 else R[2])
    # el marco de prismarina vieja, con el hueco
    y_top, y_bot = HY0 - 3, HY1 + 2
    x_izq, x_der = HX0 - 8, HX1 + 2
    for y in range(y_top, y_bot + 1):
        for x in range(x_izq, x_der + 1):
            if HX0 <= x < HX1 and HY0 <= y < HY1:
                pon(x, y, FONDO)
                continue
            if y in (y_top, y_bot) or x in (x_izq, x_der):
                pon(x, y, PRIS[0])
                continue
            k = 5 if y == y_top + 1 else 2 if y == y_bot - 1 else rnd.choice((3, 3, 4, 3))
            if (x - x_izq) % 9 == 0:
                k = 1                           # junta de bloque
            pon(x, y, PRIS[k])
    for x in range(HX0, HX1):
        pon(x, HY0, OSCURO)
    # percebes en el canto de abajo y corales en el de arriba
    for x in range(HX0 + 14, HX1 - 6, 31):
        pon(x, y_bot - 1, HUESO[3])
        pon(x + 1, y_bot - 1, HUESO[2])
        pon(x, y_bot, HUESO[1])
    for x, alto, c in ((HX0 + 60, 4, 1), (HX0 + 118, 5, 2), (HX1 - 22, 3, 3)):
        for k in range(alto):
            pon(x, y_top - 1 - k, CORAL[min(3, c + k // 2)])
        pon(x - 1, y_top - alto + 1, CORAL[c])
        pon(x + 1, y_top - alto, CORAL[c])
    # la punta derecha: el ancla
    ax = x_der + 2
    for k in range(y_bot - y_top + 1):
        pon(ax, y_top + k, PRIS[2] if k % 3 else PRIS[3])
    for k in range(5):
        pon(ax + 1 + k // 2, y_top + 1 + k, OXIDO[3])
        pon(ax + 1 + k // 2, y_bot - 1 - k, OXIDO[2])
    # el aro del emblema: prismarina, y cuatro eslabones de oxido (las cadenas del pecho)
    for y in range(NH):
        for x in range(40):
            dx, dy = x + 0.5 - EC[0], y + 0.5 - EC[1]
            d = math.hypot(dx, dy)
            if d > ER:
                continue
            luz = -(dx + dy) / (2 * ER)
            ang = math.atan2(dy, dx)
            if d > ER - 1.2:
                pon(x, y, PRIS[0])
            elif d > ER - 3.4:
                eslabon = abs((ang + math.pi / 4) % (math.pi / 2) - math.pi / 4) < 0.22
                if eslabon:
                    pon(x, y, OXIDO[4] if luz > 0.15 else OXIDO[3] if luz > -0.2 else OXIDO[2])
                else:
                    pon(x, y, PRIS[6 if luz > 0.2 else 5 if luz > 0 else 4 if luz > -0.25 else 3])
            elif d > ER - 4.4:
                pon(x, y, R[2])
            else:
                pon(x, y, FONDO)
    return im


# --------------------------------------------------------------- el relleno
def relleno(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    w, h = 64, HY1 - HY0
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            cresta = 1.6 + 0.9 * math.sin(x / w * math.tau * 2) + 0.4 * math.sin(x / w * math.tau * 5 + 1)
            k = [3, 3, 3, 2, 2, 2, 1, 1, 0][y]
            if abs(y - cresta) < 0.7:
                k = 5                           # la cresta de la ola
            elif y < cresta:
                k = 4                           # espuma por encima
            elif (x * 7 + y * 13) % 29 == 0 and y > 3:
                k = 4                           # burbujitas
            px[x, y] = R[k]
    return im


# --------------------------------------------------------------- el emblema: el corazon entre costillas
COLORES_CORAZON = {1: ('ffd0e0', 'e0144c'), 2: ('eaa6c6', 'b0124a'), 3: ('bb7aa0', '7a0e44'), 4: ('7c4a6a', '3e0828'),
                   'furia': ('d6fff0', '18b890'), 'libre': ('f0fffa', '35e0b0')}
GRIETAS = {1: 0, 2: 2, 3: 4, 4: 7, 'furia': 5, 'libre': 0}


def corazon(clave):
    im = Image.new('RGBA', (NUCLEO, NUCLEO), (0, 0, 0, 0))
    q = im.load()
    c0 = NUCLEO / 2
    escala = 7.4
    forma = set()
    for j in range(NUCLEO):
        for i in range(NUCLEO):
            x = (i + 0.5 - c0) / escala
            y = -(j + 0.5 - c0) / escala + 0.15
            if (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0:
                forma.add((i, j))
    borde = {(i, j) for (i, j) in forma if any((i + a, j + b) not in forma for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    a1, b1 = hexc(COLORES_CORAZON[clave][0]), hexc(COLORES_CORAZON[clave][1])
    for (i, j) in forma:
        if (i, j) in borde:
            q[i, j] = (30, 6, 18, 255)
        else:
            d = min(1.0, math.hypot(i - 8, j - 7) / 11)
            q[i, j] = tuple(int(a1[k] + (b1[k] - a1[k]) * d) for k in range(3)) + (255,)
    for (i, j) in ((7, 6), (8, 6), (7, 7)):    # el brillo del lobulo izquierdo
        if (i, j) in forma and (i, j) not in borde:
            q[i, j] = tuple(min(255, int(v * 0.5 + 255 * 0.5)) for v in q[i, j][:3]) + (255,)
    r = random.Random(str(clave))
    for _ in range(GRIETAS[clave]):
        x, y = r.randrange(7, 17), r.randrange(7, 15)
        for _ in range(r.randint(2, 5)):
            if (x, y) in forma and (x, y) not in borde:
                q[x, y] = (24, 4, 12, 255)
            x += r.choice((-1, 0, 1))
            y += r.choice((-1, 1))
    # las costillas: dos barras de hueso por delante, con el esternon; en la IV
    # (y en la Furia) se abren y les falta el tramo de dentro
    abiertas = clave in (4, 'furia')
    for y in (9, 14):
        for x in range(3, 21):
            centro = abs(x - c0 + 0.5)
            if abiertas and centro < 6:
                continue
            if centro > 1.0:
                q[x, y] = HUESO[3] if y == 9 else HUESO[2]
                if q[x, y + 1][3] == 0 or (x, y + 1) in forma:
                    q[x, y + 1] = HUESO[1]
    if not abiertas:
        for y in range(7, 18):
            q[11, y] = HUESO[3]
            q[12, y] = HUESO[2]
    return im


# --------------------------------------------------------------- la vista de la Mirada: la calavera
def mascara():
    """Su calavera con la corona de prismarina y coral, las cuencas vacias (los
    ojos los pone el HUD encima) y la boca de dientes."""
    im = Image.new('RGBA', (NUCLEO, NUCLEO), (0, 0, 0, 0))
    q = im.load()
    rnd = random.Random(31)
    for y in range(5, 22):
        for x in range(4, 20):
            dx = abs(x + 0.5 - 12)
            ancho = 7.6 if y < 17 else 7.6 - (y - 16) * 0.9
            if dx > ancho or (y >= 19 and dx > 5.5):
                continue
            luz = -((x - 12) + (y - 10)) / 16
            k = 4 if luz > 0.25 else 3 if luz > -0.1 else 2
            if rnd.random() < 0.08:
                k -= 1
            q[x, y] = HUESO[max(1, k)]
    # las cuencas: dos agujeros de 6x6 donde van los ojos
    for ox in (5, 13):
        for y in range(10, 16):
            for x in range(ox, ox + 6):
                if (x - ox) in (0, 5) and (y - 10) in (0, 5):
                    continue
                q[x, y] = OSCURO
    # la nariz y la boca de dientes
    for (x, y) in ((11, 16), (12, 16), (11, 17), (12, 17)):
        q[x, y] = (40, 30, 22, 255)
    for x in range(7, 17):
        q[x, 19] = (30, 22, 16, 255) if x % 2 else HUESO[4]
    # el contorno
    solido = {(x, y) for y in range(NUCLEO) for x in range(NUCLEO) if q[x, y][3]}
    for (x, y) in list(solido):
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + a, y + b) not in solido and 0 <= x + a < NUCLEO and 0 <= y + b < NUCLEO and q[x + a, y + b][3] == 0:
                q[x + a, y + b] = (36, 30, 22, 255)
    # la corona: aro de prismarina, puas y dos corales
    for x in range(4, 20):
        q[x, 5] = PRIS[5]
        q[x, 4] = PRIS[3]
    for x, alto in ((5, 3), (8, 4), (12, 4), (16, 3), (18, 2)):
        for k in range(alto):
            q[x, 3 - k] = PRIS[4] if k < alto - 1 else PRIS[6]
    for (x, y, c) in ((10, 3, 2), (10, 2, 3), (9, 1, 3), (14, 3, 1), (14, 2, 2), (15, 1, 3)):
        q[x, y] = CORAL[c]
    return im


def ojo():
    """Un ojo encendido, en grises para tenirlo: blanco en el centro y oscuro al borde."""
    im = Image.new('RGBA', (6, 6), (0, 0, 0, 0))
    q = im.load()
    for y in range(6):
        for x in range(6):
            if (x in (0, 5) and y in (0, 5)):
                continue
            d = math.hypot(x + 0.5 - 3, y + 0.5 - 3)
            v = 255 if d < 1.2 else 220 if d < 2.0 else 150
            q[x, y] = (v, v, v, 255)
    return im


GRIETA_PUNTOS = [
    [(2, 1), (2, 2), (3, 3)],
    [(4, 1), (4, 2), (1, 4), (2, 4)],
    [(1, 2), (3, 4), (4, 4), (0, 3)],
    [(3, 0), (5, 2), (2, 5), (1, 1), (4, 3)],
]


def grieta(n):
    """Las grietas que salen con los impactos: cada etapa suma las anteriores."""
    im = Image.new('RGBA', (6, 6), (0, 0, 0, 0))
    q = im.load()
    for etapa in range(n):
        for (x, y) in GRIETA_PUNTOS[etapa]:
            q[x, y] = (12, 6, 16, 255)
    return im


def ojo_roto():
    im = Image.new('RGBA', (6, 6), (0, 0, 0, 0))
    q = im.load()
    for (x, y, c) in ((1, 1, 2), (4, 1, 1), (2, 2, 3), (3, 3, 1), (1, 4, 2), (4, 4, 3), (2, 4, 1), (3, 1, 2)):
        q[x, y] = PRIS[c]
    return im


def marea_tira():
    """El agua de la marea que baja, en grises (64x5, en bucle): la espuma arriba."""
    im = Image.new('RGBA', (64, 5), (0, 0, 0, 0))
    q = im.load()
    for x in range(64):
        cresta = 1 if math.sin(x / 64 * math.tau * 4) > 0.3 else 0
        for y in range(5):
            if y < cresta:
                continue
            v = 255 if y == cresta else [235, 205, 175, 150, 130][y]
            if (x * 5 + y * 3) % 17 == 0 and y > 1:
                v = 245
            q[x, y] = (v, v, v, 255)
    return im


# --------------------------------------------------------------- eslabones de las muescas
def eslabon(roto):
    im = Image.new('RGBA', (7, 10), (0, 0, 0, 0))
    q = im.load()
    dibujo = (["..ooo..", ".oabbo.", "oab.cbo", "ob...co", "ob...co", "ob...co", "ob...co", "oac.bco", ".obbco.", "..ooo.."]
              if not roto else
              ["..ooo..", ".oabbo.", "oab.cbo", "ob...o.", ".o.....", ".....o.", ".o...co", "oac.bco", ".obbco.", "..ooo.."])
    pal = {'o': OSCURO, 'a': OXIDO[4], 'b': OXIDO[3], 'c': OXIDO[2]}
    for y, fila in enumerate(dibujo):
        for x, ch in enumerate(fila):
            if ch != '.':
                q[x, y] = pal[ch]
    return im


for clave in CLAVES:
    marco(clave).save(os.path.join(GUI, f'nerea_barra_marco_{clave}.png'))
    relleno(clave).save(os.path.join(GUI, f'nerea_barra_relleno_{clave}.png'))
    corazon(clave).save(os.path.join(GUI, f'nerea_barra_corazon_{clave}.png'))
mascara().save(os.path.join(GUI, 'nerea_barra_mascara.png'))
ojo().save(os.path.join(GUI, 'nerea_barra_ojo.png'))
for n in range(1, 5):
    grieta(n).save(os.path.join(GUI, f'nerea_barra_grieta_{n}.png'))
ojo_roto().save(os.path.join(GUI, 'nerea_barra_ojo_roto.png'))
marea_tira().save(os.path.join(GUI, 'nerea_barra_marea.png'))
eslabon(False).save(os.path.join(GUI, 'nerea_barra_eslabon.png'))
eslabon(True).save(os.path.join(GUI, 'nerea_barra_eslabon_roto.png'))
for viejo in ('nerea_barra_marco.png', 'nerea_barra_agua.png'):
    if os.path.exists(os.path.join(GUI, viejo)):
        os.remove(os.path.join(GUI, viejo))

# --------------------------------------------------------------- letras en pixel
# Nada de la fuente de Minecraft: el nombre y la fase van dibujados a mano,
# letras gruesas de 6x7 con borde oscuro y sombra, como talladas en hueso.
GLIFOS = {
    'N': ["##..##", "###.##", "######", "##.###", "##..##", "##..##", "##..##"],
    'E': ["######", "##....", "##....", "#####.", "##....", "##....", "######"],
    'R': ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    'A': [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    'F': ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    'S': [".#####", "##....", "##....", ".####.", "....##", "....##", "#####."],
    'I': ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    'V': ["##..##", "##..##", "##..##", "##..##", ".####.", ".####.", "..##.."],
    'L': ["##....", "##....", "##....", "##....", "##....", "##....", "######"],
    'B': ["#####.", "##..##", "##..##", "#####.", "##..##", "##..##", "#####."],
    'U': ["##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    ' ': ["..", "..", "..", "..", "..", "..", ".."],
}


def palabra(texto, relleno_fn, borde, sombra, ancho=None, derecha=False):
    """La palabra con borde de 1 px alrededor y sombra 1 px abajo. 'relleno_fn(fila)'
    da el color de cada fila (degradado). Si se da 'ancho', el lienzo es fijo y
    el texto va pegado a la izquierda o a la derecha."""
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
    h = 7 + 3
    ox = (w - w_txt if derecha else 0) + 1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    q = im.load()
    for (px, py) in puntos:                                  # sombra
        for dx, dy in ((0, 2), (1, 2), (-1, 2)):
            xx, yy = px + ox + dx, py + 1 + dy
            if 0 <= xx < w and 0 <= yy < h:
                q[xx, yy] = sombra
    for (px, py) in puntos:                                  # borde
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = px + ox + dx, py + 1 + dy
                if 0 <= xx < w and 0 <= yy < h and (px + dx, py + dy) not in puntos:
                    q[xx, yy] = borde
    for (px, py) in puntos:                                  # relleno
        q[px + ox, py + 1] = relleno_fn(py)
    return im


def nacar(fila):
    """Nacar a espuma de arriba abajo: el nombre de Nerea."""
    rampa = ['f4fbf6', 'e6f6ef', 'd2efe6', 'bfe6dc', 'a6d9cf', '8ccabf', '74b8ad']
    return hexc(rampa[fila])


def gris(fila):
    """En grises, para tenirlo con el color de la fase desde el HUD."""
    v = [255, 246, 236, 224, 210, 196, 182][fila]
    return (v, v, v, 255)


BORDE = hexc('061214')
SOMBRA = (0, 0, 0, 110)
palabra('NEREA', nacar, BORDE, SOMBRA).save(os.path.join(GUI, 'nerea_barra_nombre.png'))
ANCHO_FASE = 64
for n, romano in ((1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV')):
    palabra('FASE ' + romano, gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, f'nerea_barra_fase_{n}.png'))
palabra('LIBRE', gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, 'nerea_barra_libre.png'))
palabra('FURIA', gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, 'nerea_barra_furia.png'))
print('barra', (NW, NH), '| nombre', Image.open(os.path.join(GUI, 'nerea_barra_nombre.png')).size, '| fase', (ANCHO_FASE, 10))

# --------------------------------------------------------------- icono de la Corriente Abismal (efecto, 18x18)
# Un remolino de agua oscura que tira hacia abajo, con su cresta de espuma y
# las burbujas que suben: la corriente de fondo que te frena.
EFE = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/mob_effect')
os.makedirs(EFE, exist_ok=True)
ABISMO = [hexc(c) for c in ('081a2e', '0f2f4f', '1b4f7a', '2f78a6', '5aa8cf', 'a6e0f0', 'f0fbff')]
ic = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
q = ic.load()
for y in range(18):
    for x in range(18):
        dx, dy = x + 0.5 - 9, y + 0.5 - 9.5
        r = math.hypot(dx, dy)
        if r > 8.2:
            continue
        ang = math.atan2(dy, dx)
        # espiral logaritmica de dos brazos que se cierra hacia el centro
        brazo = (ang - 1.9 * math.log(max(r, 0.6))) % math.pi
        if r < 1.6:
            q[x, y] = ABISMO[0]
        elif brazo < 0.95:
            k = min(6, 2 + int((8.2 - r) / 2.2) + (1 if brazo < 0.35 else 0))
            q[x, y] = ABISMO[k]
        elif r > 7.2:
            q[x, y] = ABISMO[1]
        else:
            q[x, y] = ABISMO[1] if brazo < 1.6 else ABISMO[0]
for (bx, by) in ((14, 3), (15, 1), (3, 2)):                 # burbujas
    q[bx, by] = ABISMO[6]
ic.save(os.path.join(EFE, 'corriente_abismal.png'))

# --------------------------------------------------------------- vista previa: la barra montada
if len(sys.argv) > 2:
    def tex(n):
        return Image.open(os.path.join(GUI, n + '.png')).convert('RGBA')

    def tenir(im, rgb):
        im = im.copy()
        q2 = im.load()
        for y in range(im.height):
            for x in range(im.width):
                c = q2[x, y]
                q2[x, y] = (c[0] * rgb[0] // 255, c[1] * rgb[1] // 255, c[2] * rgb[2] // 255, c[3])
        return im

    def montar(clave, vida, mirada=None):
        b = tex(f'nerea_barra_marco_{clave}').copy()
        rel = tex(f'nerea_barra_relleno_{clave}')
        lleno = round(190 * vida)
        for x in range(0, lleno, 64):
            b.alpha_composite(rel.crop((0, 0, min(64, lleno - x), 9)), (HX0 + x, HY0))
        for corte in (0.75, 0.5, 0.25):
            e = tex('nerea_barra_eslabon_roto' if vida < corte else 'nerea_barra_eslabon')
            b.alpha_composite(e, (HX0 + round(190 * corte) - 3, HY0 - 1))
        col = hexc(RAMPAS[clave][3])
        if mirada is None:
            b.alpha_composite(tex(f'nerea_barra_corazon_{clave}'), (EC[0] - 12, EC[1] - 12))
        else:
            golpes, quedan = mirada
            b.alpha_composite(tex('nerea_barra_mascara'), (EC[0] - 12, EC[1] - 12))
            for i, g in enumerate(golpes):
                ox, oy = EC[0] - 12 + (5, 13)[i], EC[1] - 12 + 10
                if g >= 10:
                    b.alpha_composite(tex('nerea_barra_ojo_roto'), (ox, oy))
                else:
                    b.alpha_composite(tenir(tex('nerea_barra_ojo'), col), (ox, oy))
                    if g > 0:
                        b.alpha_composite(tex(f'nerea_barra_grieta_{min(4, 1 + g * 4 // 10)}'), (ox, oy))
            tira = tenir(tex('nerea_barra_marea'), col)
            w = round(150 * quedan)
            for x in range(0, w, 64):
                b.alpha_composite(tira.crop((0, 0, min(64, w - x), 5)), (HX0 + 20 + x, 36))
        b.alpha_composite(tex('nerea_barra_nombre'), (98, 9))
        return b

    filas = [montar(1, 0.92), montar(2, 0.66), montar(3, 0.41, ((3, 10), 0.6)), montar(4, 0.18), montar('furia', 0.3),
             montar('libre', 0.0)]
    K = 3
    prev = Image.new('RGBA', (NW * K + 20, (NH * K + 10) * len(filas) + 10), (40, 56, 70, 255))
    for k, f in enumerate(filas):
        prev.alpha_composite(f.resize((NW * K, NH * K), Image.NEAREST), (10, 10 + k * (NH * K + 10)))
    prev.save(sys.argv[2])
    print('ok')

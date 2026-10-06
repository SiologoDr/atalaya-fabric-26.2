"""
La barra de Nerea al estilo de las de Aeralis y Rajang del remake (propuesta),
pixel a pixel, junto a la de hoy. Solo vista previa: no escribe nada en el repo.

  - Mismas medidas que la de Aeralis (240x44, hueco de 190x9).
  - El emblema: el corazon maldito entre las costillas, con su aro de prismarina
    y cuatro eslabones de oxido (las cadenas del pecho); en cada fase el corazon
    se raja y se apaga.
  - Encima del marco, en lugar del ala o de la cresta: una ola que sale del
    emblema y rompe hacia la derecha, con la cresta de espuma, en el color de
    la fase.
  - El marco de prismarina vieja con percebes y corales.
  - El relleno con el color dentro (agua con su cresta de espuma), el frente
    encendido y el rastro claro al recibir dano.
  - Las muescas: eslabones de cadena con un remache del color de la fase;
    partidos al pasarlos.
  - Durante la Mirada del Abismo, bajo la barra, como el Sello de Rajang y el
    Juicio de Aeralis: los dos OJOS (con sus grietas: cuantos impactos les
    faltan) y la losa del tiempo que le queda al rayo, roja al final.
  - Con la Furia de las Mareas, todo en verde abismo y el rotulo FURIA.

Uso: python nerea_remake_hud.py <raiz del proyecto> <carpeta de salida>
"""
from PIL import Image
import math, os, random, sys

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
FOTOS = os.path.join(os.environ['TEMP'], r'claude\c--Users-USUARIO-juan-atalaya-fabric-26-2'
                     r'\8b154ffb-6f8b-471a-ab02-bedda2001893\scratchpad\nerea_antes')
os.makedirs(SALIDA, exist_ok=True)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


PRIS = [hexc(c) for c in ('0b1f21', '173b3c', '22504d', '2f6660', '3f7f76', '5aa596', '8fd0bd')]
HUESO = [hexc(c) for c in ('5c5545', '8a8068', 'b3a98c', 'd3c9aa', 'ece4c8')]
CORAL = [hexc(c) for c in ('7a1636', 'a8204a', 'd8336a', 'f2618f')]
OXIDO = [hexc(c) for c in ('2a1a12', '4a2a18', '6e3c1e', '9a5726', 'c47a3a')]
NACAR = [hexc(c) for c in ('6a4862', 'a0788e', 'd0a6bc', 'f0d2e2', 'fff4fa')]
FONDO = hexc('050e12')
ESPUMA_C = hexc('eaffff')
OSCURO = hexc('02080a')
# El agua de cada fase (de oscuro a la espuma), la Furia (verde abismo) y el oro de la liberacion.
RAMPAS = {
    1: ('062a36', '0e4e60', '1b8aa4', '3fe0ff', 'a8f4ff', 'eaffff'),
    2: ('1a1240', '2e2a7a', '5c4ac4', '9a6bff', 'd2c2ff', 'f0e4ff'),
    3: ('2c0a3c', '561670', '9a2ac0', 'd43cff', 'f0a8ff', 'ffd8f8'),
    4: ('3a0612', '700e24', 'b81a3e', 'ff2050', 'ffa0b2', 'ffe0e6'),
    'furia': ('021e1a', '064438', '0e8a6c', '20f0b0', '9effe0', 'e6fff6'),
    'libre': ('3a2606', '8f6418', 'c28d28', 'ffc23a', 'ffe9a8', 'fffbe0'),
}
COLOR_ROTULO = {1: 0x3FE0FF, 2: 0x9A6BFF, 3: 0xD43CFF, 4: 0xFF2050, 'furia': 0x20F0B0, 'libre': 0xFFC23A}

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


# ---------------------------------------------------------------- el marco
def marco(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    rnd = random.Random(8)
    im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
    px = im.load()

    def pon(x, y, c):
        if 0 <= x < NW and 0 <= y < NH:
            px[x, y] = c

    # la ola: sale del emblema, sube y rompe hacia la derecha por encima de la
    # barra (como el ala de Aeralis y la cresta de Rajang); cuerpo del color de
    # la fase, mas claro arriba, el borde de espuma y el rizo oscuro por dentro
    poly = [(24, 20), (27, 13), (34, 7), (45, 3), (58, 1), (70, 1), (80, 3), (88, 7), (93, 12), (92, 16),
            (88, 13), (83, 11), (78, 12), (76, 15), (79, 18), (86, 20), (100, 20)]
    pts = {(x, y) for y in range(NH) for x in range(110) if dentro(poly, x + 0.5, y + 0.5)}
    for (x, y) in pts:
        arriba = (x, y - 1) not in pts
        borde = any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1)))
        if arriba:
            c = ESPUMA_C if (x * 5 + y) % 7 else R[5]
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
    # el rizo: la parte de dentro de la ola, oscura
    for (x, y) in ((84, 14), (85, 14), (86, 15), (82, 13), (81, 14), (81, 15), (83, 16)):
        if (x, y) in pts:
            pon(x, y, R[1])
    # espuma que salta de la cresta
    for (x, y) in ((92, 8), (95, 10), (90, 5), (97, 13), (86, 3), (99, 16)):
        pon(x, y, ESPUMA_C)
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
                k = 1                                                # junta de bloque
            pon(x, y, PRIS[k])
    for x in range(HX0, HX1):
        pon(x, HY0, OSCURO)
    # percebes y corales sobre el canto de abajo
    for x in range(HX0 + 14, HX1 - 6, 31):
        pon(x, y_bot - 1, HUESO[3]); pon(x + 1, y_bot - 1, HUESO[2]); pon(x, y_bot, HUESO[1])
    for x, alto, c in ((HX0 + 60, 4, 1), (HX0 + 118, 5, 2), (HX1 - 22, 3, 3)):
        for k in range(alto):
            pon(x, y_top - 1 - k, CORAL[min(3, c + k // 2)])
        pon(x - 1, y_top - alto + 1, CORAL[c]); pon(x + 1, y_top - alto, CORAL[c])
    # la punta derecha: el ancla
    ax = x_der + 2
    for k in range(y_bot - y_top + 1):
        pon(ax, y_top + k, PRIS[2] if k % 3 else PRIS[3])
    for k in range(5):
        pon(ax + 1 + k // 2, y_top + 1 + k, OXIDO[3]); pon(ax + 1 + k // 2, y_bot - 1 - k, OXIDO[2])
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


# ---------------------------------------------------------------- el relleno
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
                k = 5
            elif y < cresta:
                k = 4
            elif (x * 7 + y * 13) % 29 == 0 and y > 3:
                k = 4                                    # burbujitas
            px[x, y] = R[k]
    return im


# ---------------------------------------------------------------- el emblema: el corazon entre costillas
def corazon(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    libre = clave == 'libre'
    nivel = 4 if clave == 'furia' else 1 if libre else clave
    im = Image.new('RGBA', (NUCLEO, NUCLEO), (0, 0, 0, 0))
    px = im.load()
    c0 = NUCLEO / 2
    rojo = [hexc(c) for c in ('3e0828', '7a0e44', 'b0124a', 'e0144c', 'ff6a9a', 'ffd0e0')]
    if libre:
        rojo = [hexc(c) for c in ('0c3a2c', '1a6a50', '26a07a', '35e0b0', '9ff5d8', 'e8fff8')]
    apaga = {1: 0, 2: 1, 3: 2, 4: 3}[nivel]
    for y in range(NUCLEO):
        for x in range(NUCLEO):
            dx, dy = x + 0.5 - c0, y + 0.5 - c0
            # un corazon: dos lobulos y la punta
            q = (dx / 8.5) ** 2 + ((dy + 1.0) / 8.0 - abs(dx / 8.5) ** 0.7 * 0.55) ** 2
            if q < 1:
                d = math.hypot(dx + 1.5, dy + 2.5) / 9
                k = 5 if d < 0.2 else 4 if d < 0.4 else 3 if d < 0.7 else 2
                px[x, y] = rojo[max(0, k - apaga)]
    # las grietas, mas cada fase
    rnd = random.Random(nivel)
    for _ in range({1: 0, 2: 2, 3: 4, 4: 7}[nivel] if not libre else 0):
        gx, gy = rnd.randint(7, 16), rnd.randint(7, 15)
        for _ in range(rnd.randint(3, 6)):
            if px[gx, gy][3]:
                px[gx, gy] = (34, 4, 16, 255)
            gx += rnd.choice((-1, 0, 1)); gy += rnd.choice((-1, 1))
    # las costillas: dos barras de hueso finas por delante, con hueco en medio
    for y in (9, 14):
        for x in range(3, 21):
            if abs(x - c0 + 0.5) > 2.5 and px[x, y][3]:
                px[x, y] = HUESO[3]
            elif abs(x - c0 + 0.5) > 2.5:
                px[x, y] = HUESO[2]
    # en la IV las costillas se abren: les falta el tramo de dentro
    if nivel == 4 and not libre:
        for y in (9, 14):
            for x in range(6, 18):
                if px[x, y][:3] in (HUESO[3][:3], HUESO[2][:3]):
                    px[x, y] = (0, 0, 0, 0)
    return im


# ---------------------------------------------------------------- muescas y ojos
PAL = {'o': OSCURO, 'a': OXIDO[4], 'b': OXIDO[3], 'c': OXIDO[2], 'd': OXIDO[1]}
ESLABON = ["..ooo..",
           ".oabbo.",
           "oab.cbo",
           "ob...co",
           "ob.L.co",
           "ob...co",
           "ob...co",
           "oac.bco",
           ".obbco.",
           "..ooo.."]
ESLABON_ROTO = ["..ooo..",
                ".oabbo.",
                "oab.cbo",
                "ob...o.",
                ".o.....",
                ".....o.",
                ".o...co",
                "oac.bco",
                ".obbco.",
                "..ooo.."]
OJO = ["..ooooo..",
       ".oPPPPPo.",
       "oPQQQQQPo",
       "oPQWWWQPo",
       "oPQWWWQPo",
       "oPQQQQQPo",
       ".oPPPPPo.",
       "..ooooo.."]
OJO_ROTO = ["..ooooo..",
            ".odddddo.",
            "oddoddddo",
            "odddoddo.",
            "o.dddoddo",
            "oddddddo.",
            ".odd.ddo.",
            "..ooooo.."]


def pintar(im, dibujo, paleta, ox=0, oy=0):
    q = im.load()
    for y, fila in enumerate(dibujo):
        for x, c in enumerate(fila):
            if c != '.' and 0 <= ox + x < im.width and 0 <= oy + y < im.height:
                q[ox + x, oy + y] = paleta[c]


def tenir(im, rgb):
    im = im.copy()
    q = im.load()
    r, g, b = (rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255
    for y in range(im.height):
        for x in range(im.width):
            c = q[x, y]
            q[x, y] = (c[0] * r // 255, c[1] * g // 255, c[2] * b // 255, c[3])
    return im


def cargar(n):
    return Image.open(os.path.join(GUI, n + '.png')).convert('RGBA')


# Las letras: las de la barra de hoy ("NEREA", "FASE N", "LIBERADO") y FURIA con el mismo trazo
GLIFOS = {
    'F': ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    'U': ["##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    'R': ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    'I': ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    'A': [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
}


def palabra(texto, ancho=64):
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
    ox = ancho - w_txt + 1
    im = Image.new('RGBA', (ancho, 10), (0, 0, 0, 0))
    q = im.load()
    for (px_, py) in puntos:
        for dx in (0, 1, -1):
            if 0 <= px_ + ox + dx < ancho:
                q[px_ + ox + dx, py + 3] = (0, 0, 0, 110)
    for (px_, py) in puntos:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = px_ + ox + dx, py + 1 + dy
                if 0 <= xx < ancho and 0 <= yy < 10 and (px_ + dx, py + dy) not in puntos:
                    q[xx, yy] = hexc('061214')
    for (px_, py) in puntos:
        v = [255, 246, 236, 224, 210, 196, 182][py]
        q[px_ + ox, py + 1] = (v, v, v, 255)
    return im


def nueva(clave, vida, fantasma=None, mirada=None, ojos=(0, 0), aguanta=6):
    """La barra nueva montada como la montaria NereaBarraHud."""
    R = [hexc(c) for c in RAMPAS[clave]]
    im = marco(clave)
    q = im.load()
    lleno = round(190 * vida)
    if fantasma and fantasma > vida:
        for x in range(lleno, round(190 * fantasma)):
            for y in range(HY0, HY1):
                q[HX0 + x, y] = (0xEA, 0xFF, 0xFF, 0xD8)
    rel = relleno(clave)
    x = 0
    while x < lleno:
        w = min(64, lleno - x)
        im.alpha_composite(rel.crop((0, 0, w, 9)), (HX0 + x, HY0))
        x += w
    if lleno >= 2:
        for y in range(HY0, HY1):
            q[HX0 + lleno - 1, y] = R[5]
            q[HX0 + lleno - 2, y] = R[5] if y < HY0 + 4 else R[4]
    for corte in (0.75, 0.5, 0.25):
        ex = HX0 + round(190 * corte) - 3
        pasado = vida < corte
        pal = dict(PAL, L=R[4])
        pintar(im, ESLABON_ROTO if pasado else ESLABON, pal, ex, HY0 - 1)
    im.alpha_composite(corazon(clave), (EC[0] - NUCLEO // 2, EC[1] - NUCLEO // 2))
    im.alpha_composite(cargar('nerea_barra_nombre'), (98, 9))
    if clave == 'furia':
        rot = tenir(palabra('FURIA'), COLOR_ROTULO[clave])
    else:
        rot = tenir(cargar('nerea_barra_libre' if clave == 'libre' else f'nerea_barra_fase_{clave}'), COLOR_ROTULO[clave])
    im.alpha_composite(rot, (HX0 + 190 - 64 + 1, 8))
    if mirada is not None:
        # los dos ojos: enteros, rajandose con cada impacto, o rotos
        for k in range(2):
            golpes = ojos[k]
            roto = golpes >= aguanta
            pal = {'o': OSCURO, 'P': R[2], 'Q': R[4], 'W': R[5], 'd': PRIS[1]}
            pintar(im, OJO_ROTO if roto else OJO, pal, HX0 + 4 + k * 12, 35)
            if not roto:
                rr = random.Random(k)
                for _ in range(golpes):
                    gx, gy = HX0 + 6 + k * 12 + rr.randint(0, 4), 37 + rr.randint(0, 3)
                    q[gx, gy] = OSCURO
        lx0, lx1, ly = HX0 + 32, HX1 - 2, 37
        for y in range(ly, ly + 5):
            for x in range(lx0, lx1):
                q[x, y] = PRIS[0] if y in (ly, ly + 4) or x in (lx0, lx1 - 1) else FONDO
        n = round((lx1 - lx0 - 2) * mirada)
        col = R[3] if mirada > 0.25 else hexc('ff5a3a')
        for x in range(lx0 + 1, lx0 + 1 + n):
            for y in range(ly + 1, ly + 4):
                q[x, y] = R[4] if y == ly + 1 else col
    return im


def antigua(clave, vida):
    """La barra de hoy, como la monta NereaBarraHud (208x26)."""
    color = COLOR_ROTULO[1 if clave == 'furia' else clave]
    im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
    ox, oy = (NW - 208) // 2, 8
    im.alpha_composite(cargar('nerea_barra_marco'), (ox, oy))
    hx, hy = ox + 28, oy + 9
    lleno = round(172 * vida)
    rel = tenir(cargar('nerea_barra_agua'), color)
    x = 0
    while x < lleno:
        w = min(64, lleno - x)
        im.alpha_composite(rel.crop((0, 0, w, 8)), (hx + x, hy))
        x += w
    for corte in (0.75, 0.5, 0.25):
        mu = 'nerea_barra_eslabon_roto' if vida < corte else 'nerea_barra_eslabon'
        e = cargar(mu)
        im.alpha_composite(e, (hx + round(172 * corte) - e.width // 2, hy - 2))
    cor = 'nerea_barra_corazon_libre' if clave == 'libre' else 'nerea_barra_corazon_4' if clave == 'furia' else f'nerea_barra_corazon_{clave}'
    im.alpha_composite(cargar(cor), (ox + 13 - 8, oy + 13 - 8))
    im.alpha_composite(cargar('nerea_barra_nombre'), (hx, oy + 7 - 10))
    rot = 'nerea_barra_libre' if clave == 'libre' else 'nerea_barra_fase_4' if clave == 'furia' else f'nerea_barra_fase_{clave}'
    im.alpha_composite(tenir(cargar(rot), color), (hx + 172 - 64 + 1, oy + 7 - 10))
    return im


# ---------------------------------------------------------------- hojas
ESTADOS = [('1', 1, 0.92, 0.97, None, (0, 0)), ('2', 2, 0.66, None, None, (0, 0)),
           ('3', 3, 0.41, None, 0.55, (2, 6)), ('4', 4, 0.18, 0.26, None, (0, 0)),
           ('furia', 'furia', 0.22, None, None, (0, 0)), ('libre', 'libre', 0.0, None, None, (0, 0))]
K = 4
for nombre, clave, vida, fantasma, mirada, ojos in ESTADOS:
    antigua(clave, vida).resize((NW * K, NH * K), Image.NEAREST).save(os.path.join(SALIDA, f'barra_antes_{nombre}.png'))
    nueva(clave, vida, fantasma, mirada, ojos).resize((NW * K, NH * K), Image.NEAREST).save(
        os.path.join(SALIDA, f'barra_nueva_{nombre}.png'))


def en_partida(foto, clave, vida, mirada=None, ojos=(0, 0), salida=None):
    im = Image.open(foto).convert('RGBA')
    q = im.load()
    W = im.width
    for y in range(0, 70):
        fila = sorted([q[x, y][:3] for x in list(range(0, 200)) + list(range(W - 200, W))], key=sum)
        c = fila[len(fila) // 2]
        for x in range(205, W - 205):
            q[x, y] = (*c, 255)
    barra = nueva(clave, vida, None, mirada, ojos).resize((NW * 2, NH * 2), Image.NEAREST)
    im.alpha_composite(barra, ((W - NW * 2) // 2, 10))
    im.convert('RGB').save(salida)


en_partida(os.path.join(FOTOS, 'nerea_antes_rompeolas.png'), 2, 0.7, salida=os.path.join(SALIDA, 'partida_fase2.png'))
en_partida(os.path.join(FOTOS, 'nerea_antes_mirada.png'), 3, 0.45, 0.55, (2, 6), salida=os.path.join(SALIDA, 'partida_mirada.png'))
print('ok', SALIDA)

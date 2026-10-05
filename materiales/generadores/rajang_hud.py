"""
La barra de jefe de Rajang, el Jaguar de Jade, pintada pixel a pixel (nada de
la de vanilla). Misma composicion y medidas que la de Nerea y la de Aeralis,
con lo suyo:

  rajang_barra_marco.png         el marco: jade tallado en bloques con incrustaciones
                                 de oro escalonadas, la cresta de cristales encima,
                                 el colgante de oro debajo, la punta escalonada y el
                                 hueco redondo del emblema con su aro de oro (208x26)
  rajang_barra_relleno.png       el relleno: estratos de piedra con vetas de energia
                                 que corren, en grises para tenirlo con el color de
                                 cada fase (64x8, en bucle horizontal)
  rajang_barra_sol_N.png         el emblema: el sol de jade de cada fase, cada vez
                                 mas rajado y con la maldicion brillando por las
                                 grietas, y el liberado en oro (16x16)
  rajang_barra_muesca*.png       las muescas de fase: un colmillo de jade con su
                                 casquillo de oro, entero o partido (6x12)
  rajang_barra_nombre.png        "RAJANG" en letras de pixel (48x10)
  rajang_barra_fase_N.png        "FASE I".."FASE IV" y rajang_barra_libre.png
                                 ("LIBERADO"), en grises para tenirlos (64x10)

Colores de fase pensados para el codigo (el relleno y el rotulo se tinen):
  I 0x58C886 (jade)  II 0x8CFF5A (verde)  III 0xC8FF2A (lima)  IV 0xE6FF4A
  liberado 0xF8D97C / 0xE2B443 (oro)

Uso: python rajang_hud.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image
import math, os, sys, random

RAIZ = sys.argv[1]
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
os.makedirs(GUI, exist_ok=True)
rnd = random.Random(33)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


# jade de oscuro a esmeralda claro, y el oro de las placas
JADE = [hexc(c) for c in ('07160e', '0e2a1c', '143a27', '1c4e34', '266444', '387a56', '3aa866', '58c886', '86e2a8')]
ORO = [hexc(c) for c in ('3a2606', '5e400e', '8f6418', 'c28d28', 'e2b443', 'f8d97c')]
FONDO = hexc('06120c')          # el fondo del hueco y del emblema


def pintar(im, dibujo, paleta, ox=0, oy=0):
    """Cada letra del dibujo es un color de la paleta; '.' no pinta."""
    q = im.load()
    for y, fila in enumerate(dibujo):
        for x, c in enumerate(fila):
            if c != '.' and 0 <= ox + x < im.width and 0 <= oy + y < im.height:
                q[ox + x, oy + y] = paleta[c]
    return im


# --------------------------------------------------------------- marco
W, H = 208, 26
BX0, BX1, BY0, BY1 = 28, 199, 9, 16            # el hueco de la barra, 172x8
EC, ER = 13.0, 12.6                            # el emblema: centro y radio
m = Image.new('RGBA', (W, H), (0, 0, 0, 0))
p = m.load()

# los bloques de jade: cada uno con su tono, juntas oscuras y bisel
TAM_BLOQUE = 11
tono_arriba = {i: rnd.choice((6, 6, 7, 5)) for i in range(0, 40)}
tono_abajo = {i: rnd.choice((4, 5, 5, 4)) for i in range(0, 40)}


def piedra(x, y):
    arriba = y < BY0
    lado = not (BY0 - 2 <= y <= BY1 + 2) or x < BX0 or x > BX1
    if arriba:
        u = x - (BX0 - 3)
        b, i = u // TAM_BLOQUE, u % TAM_BLOQUE
        k = tono_arriba[b]
        if i == 0:
            return JADE[2]                          # junta
        if y == BY0 - 2:
            k += 1                                  # canto de arriba, a la luz
        if i == 1:
            k += 1
        elif i == TAM_BLOQUE - 1:
            k -= 1
    elif y > BY1:
        u = x - (BX0 - 3) + TAM_BLOQUE // 2         # juntas al tresbolillo
        b, i = u // TAM_BLOQUE, u % TAM_BLOQUE
        k = tono_abajo[b]
        if i == 0:
            return JADE[1]
        if y == BY1 + 2:
            k -= 1                                  # canto de abajo, en sombra
        if i == 1:
            k += 1
        elif i == TAM_BLOQUE - 1:
            k -= 1
    else:                                           # los costados del hueco
        k = 5 if x < BX0 else 4
        if y == BY0:
            k += 1
    r = rnd.random()
    if r < 0.12:
        k -= 1
    elif r < 0.16:
        k += 1
    if rnd.random() < 0.025:
        return JADE[8]                              # esmeralda suelta
    return JADE[max(1, min(8, k))]


for y in range(H):
    for x in range(W):
        dentro_barra = BX0 - 3 <= x <= BX1 + 3 and BY0 - 3 <= y <= BY1 + 3
        d = math.hypot(x + 0.5 - EC, y + 0.5 - EC)
        if dentro_barra or d <= ER:
            borde = (x in (BX0 - 3, BX1 + 3) or y in (BY0 - 3, BY1 + 3)) and dentro_barra and d > ER - 1
            if ER - 1.2 < d <= ER:
                p[x, y] = JADE[0]
            elif ER - 2.5 < d <= ER - 1.2:
                # el aro de jade del emblema, con la luz arriba a la izquierda,
                # y ocho tachones de oro, como los rayos de un sol
                luz = -((x + 0.5 - EC) + (y + 0.5 - EC)) / (2 * ER)
                ang = math.atan2(y + 0.5 - EC, x + 0.5 - EC) - math.pi / 8
                rayo = abs((ang + math.pi / 8) % (math.pi / 4) - math.pi / 8) < 0.15
                if rayo:
                    p[x, y] = ORO[5] if luz > 0.2 else ORO[4] if luz > -0.15 else ORO[3]
                    continue
                k = 7 if luz > 0.18 else 6 if luz > -0.05 else 5 if luz > -0.25 else 4
                if rnd.random() < 0.12:
                    k -= 1
                p[x, y] = JADE[k]
            elif ER - 3.5 < d <= ER - 2.5:
                # el aro de oro, por dentro
                luz = -((x + 0.5 - EC) + (y + 0.5 - EC)) / (2 * ER)
                p[x, y] = ORO[5] if luz > 0.25 else ORO[4] if luz > 0.0 else ORO[3] if luz > -0.3 else ORO[2]
            elif d <= ER - 3.5:
                p[x, y] = FONDO
            elif borde:
                p[x, y] = JADE[0]
            elif BX0 <= x <= BX1 and BY0 <= y <= BY1:
                p[x, y] = FONDO
            else:
                p[x, y] = piedra(x, y)
# sombra dentro del hueco: el canto de arriba proyecta
for x in range(BX0, BX1 + 1):
    p[x, BY0] = hexc('030a06')

# incrustaciones de oro: piramides escalonadas en el canto de arriba y
# piramides invertidas en el de abajo, al tresbolillo
for x in range(BX0 + 9, BX1 - 6, 22):
    for (dx, dy, c) in ((1, 0, ORO[5]), (2, 0, ORO[4]),
                        (0, 1, ORO[4]), (1, 1, ORO[3]), (2, 1, ORO[3]), (3, 1, ORO[2])):
        p[x + dx, BY0 - 2 + dy] = c
    for (dx, dy, c) in ((0, 0, ORO[4]), (1, 0, ORO[3]), (2, 0, ORO[3]), (3, 0, ORO[2]),
                        (1, 1, ORO[2]), (2, 1, ORO[1])):
        p[x + 11 + dx, BY1 + 1 + dy] = c

PAL = {'o': JADE[0], 'O': hexc('020805'),
       'y': ORO[5], 'Y': ORO[4], 'G': ORO[3], 'g': ORO[2], 'h': ORO[1],
       '8': JADE[8], '7': JADE[7], '6': JADE[6], '5': JADE[5], '4': JADE[4], '3': JADE[3],
       'w': hexc('e8fff0')}

# la cresta de cristales sobre una base de oro escalonada, en el centro de la barra
CRESTA = [
    ".........oo.........",
    "........o8wo........",
    "........o876o.......",
    "...oo...o876o..oo...",
    "..o8wo..o865o.o86o..",
    "..o876oo87655o8765o.",
    ".ooyYYYYYYYYYYYYGGgo",
]
# la ultima fila de la cresta (la base de oro) cae sobre el canto oscuro del marco
pintar(m, CRESTA, PAL, 104, BY0 - 3 - 6)

# el colgante de oro bajo el centro: un dintel escalonado con una esmeralda
COLGANTE = [
    ".oyYYYGGGGgo.",
    "..oYG676Ggo..",
    "...ogG8Ggo...",
    "....ohhho....",
]
pintar(m, COLGANTE, PAL, 107, BY1 + 4)

# la punta derecha: un remate de oro escalonado, como el costado de un templo
PUNTA = [
    "oo...",
    "yGo..",
    "YGGo.",
    "oYGo.",
    "oYGgo",
    "oyYGo",
    "ooYGgo",
    "ooGgho",
    "oYGgo",
    "oGgho",
    "oGgo.",
    "ogho.",
    "oho..",
    "oo...",
]
for j, fila in enumerate(PUNTA):
    for i, c in enumerate(fila):
        if c != '.' and BX1 + 3 + i < W:
            p[BX1 + 3 + i, BY0 - 3 + j] = PAL[c]
m.save(os.path.join(GUI, 'rajang_barra_marco.png'))

# --------------------------------------------------------------- relleno: piedra con energia
aw, ah = 64, 8
a = Image.new('RGBA', (aw, ah), (0, 0, 0, 0))
p = a.load()
TAU = 2 * math.pi
for y in range(ah):
    for x in range(aw):
        t = y / (ah - 1)
        v = 236 - 96 * t
        # estratos de roca: una junta oscura que ondula
        e1 = 4.6 + 1.1 * math.sin(TAU * x / 64 * 2 + 0.7) + 0.5 * math.sin(TAU * x / 64 * 5 + 2.0)
        if abs(y - e1) < 0.5:
            v -= 46
        elif abs(y - e1 + 1) < 0.5:
            v += 10                                 # el canto claro sobre la junta
        # la veta de energia que corre por arriba: rayas brillantes partidas
        e2 = 1.6 + 0.9 * math.sin(TAU * x / 32 + 1.3)
        if abs(y - e2) < 0.5 and (x * 3) % 16 < 11:
            v = 255
        # grano de piedra y guijarros
        if (x * 7 + y * 13) % 29 == 0:
            v += 22
        elif (x * 5 + y * 11) % 23 == 0:
            v -= 24
        v += rnd.randint(-6, 6)
        p[x, y] = (int(max(0, min(255, v))),) * 3 + (255,)
# guijarros sueltos de dos pixeles, con su sombra
for (gx, gy) in ((9, 6), (27, 5), (44, 6), (57, 3), (19, 3)):
    for (dx, dy, dv) in ((0, 0, 30), (1, 0, 20), (0, 1, -20), (1, 1, -30)):
        xx, yy = (gx + dx) % aw, gy + dy
        if yy < ah:
            v = p[xx, yy][0]
            p[xx, yy] = (max(0, min(255, v + dv)),) * 3 + (255,)
a.save(os.path.join(GUI, 'rajang_barra_relleno.png'))

# --------------------------------------------------------------- emblema: el sol de jade
# 'o' contorno; 'R' rayo de oro (se sombrea solo); 'D' disco de jade (se sombrea solo)
SOL = [
    ".......oo.......",
    "......oRRo......",
    "..oo.oRRRRo.oo..",
    "..oRooooooooRo..",
    "...oRoDDDDoRo...",
    "..oooDDDDDDooo..",
    ".oRoDDDDDDDDoRo.",
    "oRRoDDDDDDDDoRRo",
    "oRRoDDDDDDDDoRRo",
    ".oRoDDDDDDDDoRo.",
    "..oooDDDDDDooo..",
    "...oRoDDDDoRo...",
    "..oRooooooooRo..",
    "..oo.oRRRRo.oo..",
    "......oRRo......",
    ".......oo.......",
]
NUCLEO = {(7, 7), (8, 7), (7, 8), (8, 8)}
# las grietas, del centro hacia fuera; cada fase abre las suyas y las anteriores
GRIETAS = {
    2: [[(9, 6), (10, 6), (10, 5)], [(6, 9), (5, 9), (5, 10)]],
    3: [[(9, 6), (10, 6), (10, 5), (11, 4)], [(6, 9), (5, 9), (5, 10), (4, 11)],
        [(9, 9), (9, 10), (10, 11), (10, 12)], [(6, 7), (5, 6), (4, 6)]],
    4: [[(9, 6), (10, 6), (10, 5), (11, 4), (12, 3)], [(6, 9), (5, 9), (5, 10), (4, 11), (3, 12)],
        [(9, 9), (9, 10), (10, 11), (10, 12)], [(6, 7), (5, 6), (4, 6), (3, 6)],
        [(8, 6), (8, 5), (9, 4), (9, 3), (9, 2)], [(9, 8), (10, 8), (11, 9), (12, 9), (13, 10)],
        [(7, 9), (7, 10), (6, 11), (6, 12)], [(6, 6), (6, 5), (5, 4)]],
}
BRILLO = {1: ('dfffe8', '86e2a8'), 2: ('f0ffe0', '8cff5a'), 3: ('fbffe0', 'c8ff2a'), 4: ('ffffff', 'e6ff4a'),
          'libre': ('fffbe8', 'f8d97c')}
S = 16


def sol(clave):
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    q = im.load()
    libre = clave == 'libre'
    claro, color = hexc(BRILLO[clave][0]), hexc(BRILLO[clave][1])
    oscurece = 1 if clave == 4 else 0                # en la IV el jade se apaga
    for y, fila in enumerate(SOL):
        for x, c in enumerate(fila):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8
            luz = -(dx + dy) / 11.0
            if c == 'o':
                q[x, y] = JADE[0] if not libre else ORO[0]
            elif c == 'R':
                r = ORO if True else None
                k = 5 if luz > 0.35 else 4 if luz > -0.05 else 3 if luz > -0.4 else 2
                if libre:
                    k = min(5, k + 1)
                q[x, y] = r[k]
            elif c == 'D':
                d = math.hypot(dx, dy)
                if libre:
                    k = 5 if luz > 0.25 else 4 if luz > -0.15 else 3
                    if 2.2 < d < 3.3:
                        k = 2 if luz < 0.1 else 3            # el surco tallado
                    q[x, y] = ORO[k]
                else:
                    k = 7 if luz > 0.3 else 6 if luz > 0.0 else 5 if luz > -0.3 else 4
                    if 2.2 < d < 3.3:
                        k = 3 if luz < 0.1 else 4            # el surco tallado alrededor del nucleo
                    elif d >= 3.3 and luz > 0.45:
                        k = 8                                # brillo del canto
                    q[x, y] = JADE[max(2, k - oscurece)]
    # el nucleo
    for (x, y) in NUCLEO:
        q[x, y] = claro if (x, y) == (7, 7) else color
    if clave in (2, 3, 4):
        for (x, y) in ((7, 6), (6, 7), (8, 6), (6, 8), (9, 7), (7, 9), (9, 8), (8, 9)):
            if q[x, y][3] and SOL[y][x] == 'D':
                q[x, y] = mezclar(q[x, y], color, 0.45 if clave < 4 else 0.7)   # halo
    for grieta in GRIETAS.get(clave, []):
        for n, (x, y) in enumerate(grieta):
            base = SOL[y][x]
            q[x, y] = claro if (n == 0 and clave == 4) else color
            # sombra de la grieta abajo a la derecha, para que se vea honda
            sx, sy = x + 1, y + 1
            if 0 <= sx < S and 0 <= sy < S and SOL[sy][sx] in 'DR' and (sx, sy) not in NUCLEO \
                    and all((sx, sy) not in g for g in GRIETAS[clave]):
                q[sx, sy] = mezclar(q[sx, sy], JADE[0], 0.55)
    if clave == 4:
        # un rayo arrancado: le falta la punta de arriba a la derecha
        for (x, y) in ((13, 1), (14, 1), (13, 2), (14, 2)):
            q[x, y] = (0, 0, 0, 0)
        q[12, 2] = JADE[0]
        q[13, 2] = JADE[0]
        q[12, 1] = (0, 0, 0, 0)
    return im


for clave in (1, 2, 3, 4, 'libre'):
    sol(clave).save(os.path.join(GUI, f'rajang_barra_sol_{clave}.png'))


# --------------------------------------------------------------- muescas: un colmillo de jade
COLMILLO = [
    ".oooo.",
    "oyYGgo",
    "ohhhho",
    "o8765o",
    "o8765o",
    "o876o.",
    ".o86o.",
    ".o76o.",
    ".o75o.",
    "..o6o.",
    "..o5o.",
    "...o..",
]
COLMILLO_ROTO = [
    ".oooo.",
    "oyYGgo",
    "ohhhho",
    "o8765o",
    "o8765o",
    "o8o5o.",
    ".o.o..",
    "......",
    "......",
    "......",
    "......",
    "......",
]
for nombre, dib in (('rajang_barra_muesca', COLMILLO), ('rajang_barra_muesca_rota', COLMILLO_ROTO)):
    im = Image.new('RGBA', (6, 12), (0, 0, 0, 0))
    pintar(im, dib, PAL)
    im.save(os.path.join(GUI, nombre + '.png'))

# --------------------------------------------------------------- letras en pixel
GLIFOS = {
    'A': [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    'B': ["#####.", "##..##", "##..##", "#####.", "##..##", "##..##", "#####."],
    'D': ["#####.", "##..##", "##..##", "##..##", "##..##", "##..##", "#####."],
    'E': ["######", "##....", "##....", "#####.", "##....", "##....", "######"],
    'F': ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    'G': [".#####", "##....", "##....", "##.###", "##..##", "##..##", ".####."],
    'I': ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    'J': ["....##", "....##", "....##", "....##", "##..##", "##..##", ".####."],
    'L': ["##....", "##....", "##....", "##....", "##....", "##....", "######"],
    'N': ["##..##", "###.##", "######", "##.###", "##..##", "##..##", "##..##"],
    'O': [".####.", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    'R': ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    'S': [".#####", "##....", "##....", ".####.", "....##", "....##", "#####."],
    'V': ["##..##", "##..##", "##..##", "##..##", ".####.", ".####.", "..##.."],
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
        q[px + ox, py + 1] = relleno(px, py)
    return im


def jade_claro(fx, fila):
    rampa = ['ffffff', 'f0fff4', 'dcfbe6', 'c2f3d4', 'a6e9bf', '8adcaa', '72d098']
    return hexc(rampa[fila])


def gris(fx, fila):
    v = [255, 246, 236, 224, 210, 196, 182][fila]
    return (v, v, v, 255)


BORDE = hexc('04100a')
SOMBRA = (0, 0, 0, 110)
NOMBRE_ANCHO = 48
nombre = palabra('RAJANG', jade_claro, BORDE, SOMBRA, NOMBRE_ANCHO)
nombre.save(os.path.join(GUI, 'rajang_barra_nombre.png'))
ANCHO_FASE = 64
for n, romano in ((1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV')):
    palabra('FASE ' + romano, gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, f'rajang_barra_fase_{n}.png'))
palabra('LIBERADO', gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, 'rajang_barra_libre.png'))
print('nombre', nombre.size, 'fase', (ANCHO_FASE, 10))

# --------------------------------------------------------------- vista previa: la barra montada en cada fase
if len(sys.argv) > 2:
    COLOR_FASE = {1: 0x58C886, 2: 0x8CFF5A, 3: 0xC8FF2A, 4: 0xE6FF4A, 'libre': 0xF8D97C}

    def tenir(im, rgb):
        im = im.copy()
        q = im.load()
        r, g, b = (rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255
        for y in range(im.height):
            for x in range(im.width):
                c = q[x, y]
                q[x, y] = (c[0] * r // 255, c[1] * g // 255, c[2] * b // 255, c[3])
        return im

    def montar(clave, vida):
        lienzo = Image.new('RGBA', (W, 34), (0, 0, 0, 0))
        y0 = 6
        lienzo.alpha_composite(Image.open(os.path.join(GUI, 'rajang_barra_marco.png')), (0, y0))
        hx, hy = BX0, y0 + BY0
        lleno = round(172 * vida)
        rel = tenir(Image.open(os.path.join(GUI, 'rajang_barra_relleno.png')), COLOR_FASE[clave])
        x = 0
        while x < lleno:
            w = min(64, lleno - x)
            lienzo.alpha_composite(rel.crop((0, 0, w, 8)), (hx + x, hy))
            x += w
        for corte in (0.75, 0.5, 0.25):
            ex = hx + round(172 * corte) - 3
            mu = 'rajang_barra_muesca_rota' if vida < corte else 'rajang_barra_muesca'
            lienzo.alpha_composite(Image.open(os.path.join(GUI, mu + '.png')), (ex, hy - 2))
        lienzo.alpha_composite(Image.open(os.path.join(GUI, f'rajang_barra_sol_{clave}.png')), (13 - 8, y0 + 13 - 8))
        ly = y0 + 7 - 10
        lienzo.alpha_composite(Image.open(os.path.join(GUI, 'rajang_barra_nombre.png')), (hx, ly))
        rot = 'rajang_barra_libre' if clave == 'libre' else f'rajang_barra_fase_{clave}'
        lienzo.alpha_composite(tenir(Image.open(os.path.join(GUI, rot + '.png')), COLOR_FASE[clave]), (hx + 172 - 64 + 1, ly))
        return lienzo

    K = 4
    prev = Image.new('RGBA', (W * K + 40, 5 * 34 * K + 200), (92, 120, 84, 255))
    # un fondo de "mundo" para juzgar el contraste: cielo arriba, hierba abajo
    q = prev.load()
    for y in range(prev.height):
        for x in range(prev.width):
            if (x // 64 + y // 64) % 2:
                q[x, y] = (110, 140, 100, 255)
    for i, (clave, vida) in enumerate(((1, 0.92), (2, 0.66), (3, 0.41), (4, 0.18), ('libre', 0.0))):
        im = montar(clave, vida)
        prev.alpha_composite(im.resize((W * K, 34 * K), Image.NEAREST), (20, 10 + i * 34 * K))
    x = 20
    yb = 10 + 5 * 34 * K + 10
    for clave in (1, 2, 3, 4, 'libre'):
        im = Image.open(os.path.join(GUI, f'rajang_barra_sol_{clave}.png')).resize((128, 128), Image.NEAREST)
        prev.alpha_composite(im, (x, yb))
        x += 140
    for f in ('rajang_barra_muesca', 'rajang_barra_muesca_rota'):
        prev.alpha_composite(Image.open(os.path.join(GUI, f + '.png')).resize((48, 96), Image.NEAREST), (x, yb))
        x += 60
    prev.alpha_composite(Image.open(os.path.join(GUI, 'rajang_barra_relleno.png')).resize((256, 32), Image.NEAREST), (x, yb))
    prev.alpha_composite(tenir(Image.open(os.path.join(GUI, 'rajang_barra_relleno.png')), 0xC8FF2A).resize((256, 32), Image.NEAREST), (x, yb + 40))
    prev.alpha_composite(tenir(Image.open(os.path.join(GUI, 'rajang_barra_relleno.png')), 0x58C886).resize((256, 32), Image.NEAREST), (x, yb + 80))
    prev.save(sys.argv[2])
    print('ok')

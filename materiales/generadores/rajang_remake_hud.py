"""
La barra de Rajang al estilo de la de Aeralis del remake (propuesta), pixel a
pixel, junto a la de hoy. Solo vista previa: no escribe nada en el repo.

  - Mismas medidas que la de Aeralis (240x44, hueco de 190x9), para que las
    tres barras vayan a juego.
  - El emblema: la placa de oro en espiral cuadrada de su armadura sobre un
    disco de jade, con las grietas de la maldicion encendidas en el color de
    la fase (mas grietas cada fase); dentro de un aro de jade con ocho
    tachones de oro.
  - Encima del marco, en lugar del ala: la cresta de cristales de jade de su
    lomo, que sale del emblema y baja hacia la derecha, en el color de la fase.
  - El marco de bloques de jade con incrustaciones de oro y la punta de templo.
  - El relleno con el color dentro de la imagen (estratos de roca con la veta
    de energia), su frente encendido y el rastro claro al recibir dano.
  - Las muescas: colmillos de jade con casquillo de oro y la punta encendida;
    partidos al pasarlos.
  - Durante el Sello de la Tierra, bajo la barra: los cuatro totems del Sello
    (columnas de piedra verde con sus glifos; los rotos, partidos y apagados) y
    la losa del tiempo que se vacia (roja al final).
  - Con la Furia de Jade, todo en verde vivo y el rotulo FURIA.

Uso: python rajang_remake_hud.py <raiz del proyecto> <carpeta de salida>
     python rajang_remake_hud.py <raiz del proyecto> --juego

Con --juego (desde octubre de 2026, cuando la barra paso al juego) escribe las
piezas que usa RajangBarraHud en textures/gui y no saca las hojas:
  rajang_barra_marco_N.png     el marco de cada fase, la Furia y el liberado (240x44)
  rajang_barra_relleno_N.png   la energia de cada uno, con el color dentro (64x9)
  rajang_barra_nucleo_N.png    el sol de jade de cada uno (24x24)
  rajang_barra_colmillo(_roto).png   las muescas (7x12)
  rajang_barra_totem(_roto).png      los totems del Sello, como en el juego (7x9)
Las letras (el nombre, la fase, LIBERADO y FURIA) siguen saliendo de
rajang_hud.py y rajang_mejoras_extras.py.
"""
from PIL import Image, ImageFilter
import math, os, random, sys

JUEGO = '--juego' in sys.argv
_ARGS = [a for a in sys.argv[1:] if a != '--juego']
RAIZ = _ARGS[0]
SALIDA = _ARGS[1] if len(_ARGS) > 1 else None
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
FOTOS = os.path.join(RAIZ, 'run/screenshots')
if SALIDA:
    os.makedirs(SALIDA, exist_ok=True)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


JADE = [hexc(c) for c in ('07160e', '0e2a1c', '143a27', '1c4e34', '266444', '387a56', '3aa866', '58c886', '86e2a8')]
ORO = [hexc(c) for c in ('3a2606', '5e400e', '8f6418', 'c28d28', 'e2b443', 'f8d97c')]
FONDO = hexc('06120c')
OSCURO = hexc('030a06')
RAMPAS = {
    1: ('07160e', '143a27', '266444', '3aa866', '86e2a8', 'dfffe8'),
    2: ('0c1e08', '1f4a14', '3f8a24', '8cff5a', 'c8ffa8', 'f0ffe0'),
    3: ('1a2008', '3e5010', '7a9a18', 'c8ff2a', 'e6ffa0', 'fbffe0'),
    4: ('22200a', '4e4a10', '9a9418', 'e6ff4a', 'f6ffb0', 'ffffff'),
    'furia': ('06200a', '0e5418', '2aa830', '7cff3a', 'c4ffa0', 'f4fff0'),
    'libre': ('3a2606', '8f6418', 'c28d28', 'f8d97c', 'fff0c0', 'fffbe8'),
}
COLOR_ROTULO = {1: 0x58C886, 2: 0x8CFF5A, 3: 0xC8FF2A, 4: 0xE6FF4A, 'furia': 0x7CFF3A, 'libre': 0xF8D97C}

NW, NH = 240, 44
HX0, HX1, HY0, HY1 = 40, 230, 22, 31
EC = (19, 26)
ER = 15.5
SOL = 24


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
    rnd = random.Random(33)
    im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
    px = im.load()

    def pon(x, y, c):
        if 0 <= x < NW and 0 <= y < NH:
            px[x, y] = c

    def cristal(cx, base, alto, ancho, lean):
        """Un cristal de jade del lomo: cara clara a la izquierda, oscura a la derecha."""
        poly = [(cx - ancho / 2, base), (cx + ancho / 2, base),
                (cx + ancho / 2 + lean * alto * 0.5, base - alto * 0.55),
                (cx + lean * alto, base - alto),
                (cx - ancho / 2 + lean * alto * 0.5, base - alto * 0.62)]
        pts = {(x, y) for y in range(NH) for x in range(NW) if dentro(poly, x + 0.5, y + 0.5)}
        for (x, y) in pts:
            borde = any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, -1)))
            t = (base - y) / alto
            eje = cx + lean * alto * t
            if borde:
                c = JADE[0]
            elif x < eje:
                c = R[3] if t > 0.45 else R[2]
                if (x - 1, y) not in pts or (x - 2, y) not in pts:
                    c = R[4]
            else:
                c = R[2] if t > 0.45 else R[1]
            if t > 0.86 and not borde:
                c = R[5]
            pon(x, y, c)

    # el marco de bloques de jade, con la junta al tresbolillo
    y_top, y_bot = HY0 - 3, HY1 + 2
    x_izq, x_der = HX0 - 8, HX1 + 2
    for y in range(y_top, y_bot + 1):
        for x in range(x_izq, x_der + 1):
            if HX0 <= x < HX1 and HY0 <= y < HY1:
                pon(x, y, FONDO)
                continue
            if y in (y_top, y_bot) or x in (x_izq, x_der):
                pon(x, y, JADE[0])
                continue
            arriba = y < HY0
            u = x - x_izq + (0 if arriba else 6)
            i = u % 12
            if i == 0:
                pon(x, y, JADE[2] if arriba else JADE[1])
                continue
            k = 6 if arriba else 4
            if y == y_top + 1:
                k += 1
            if y == y_bot - 1:
                k -= 1
            if i == 1:
                k += 1
            elif i == 11:
                k -= 1
            r = rnd.random()
            k += -1 if r < 0.12 else 1 if r < 0.16 else 0
            pon(x, y, JADE[8] if rnd.random() < 0.02 else JADE[max(1, min(8, k))])
    for x in range(HX0, HX1):
        pon(x, HY0, OSCURO)
    # incrustaciones de oro escalonadas, arriba y abajo
    for x in range(HX0 + 60, HX1 - 8, 24):
        for (dx, dy, c) in ((1, 0, ORO[5]), (2, 0, ORO[4]), (0, 1, ORO[4]), (1, 1, ORO[3]), (2, 1, ORO[3]), (3, 1, ORO[2])):
            pon(x + dx, y_top + 1 + dy, c)
    for x in range(HX0 + 4, HX1 - 8, 24):
        for (dx, dy, c) in ((0, 0, ORO[4]), (1, 0, ORO[3]), (2, 0, ORO[3]), (3, 0, ORO[2]), (1, 1, ORO[2]), (2, 1, ORO[1])):
            pon(x + 12 + dx, HY1 + dy, c)
    # la punta derecha: el costado escalonado de un templo
    for j in range(y_bot - y_top + 1):
        hondo = 1 + min(j, y_bot - y_top - j) // 2
        for i in range(hondo + 1):
            x = x_der + 1 + i
            pon(x, y_top + j, JADE[0] if i == hondo else ORO[5 - min(3, i + (j > 7))])
    # la cresta de cristales del lomo: sale del emblema y baja a la derecha
    base = y_top + 1
    for (x0, x1) in ((27, 90),):
        for x in range(x0, x1):
            pon(x, base, ORO[4] if x % 4 else ORO[2])
            pon(x, base - 1, JADE[0])
    # de atras (los pequenos, a la derecha) hacia delante, que se monten
    for (cx, alto, ancho, lean) in ((84, 5, 6, 0.5), (78, 7, 7, 0.5), (71, 9, 8, 0.45), (63, 12, 9, 0.4),
                                    (54, 15, 10, 0.32), (44, 18, 11, 0.24), (33, 20, 12, 0.14)):
        cristal(cx, base - 1, alto, ancho, lean)
    cristal(5, 17, 10, 6, -0.4)          # uno pequeno detras del emblema
    # el aro del emblema: jade con ocho tachones de oro, y oro por dentro
    for y in range(NH):
        for x in range(40):
            dx, dy = x + 0.5 - EC[0], y + 0.5 - EC[1]
            d = math.hypot(dx, dy)
            if d > ER:
                continue
            luz = -(dx + dy) / (2 * ER)
            if d > ER - 1.2:
                pon(x, y, JADE[0])
            elif d > ER - 3.2:
                ang = math.atan2(dy, dx)
                rayo = abs((ang + math.pi / 8) % (math.pi / 4) - math.pi / 8) < 0.16
                if rayo:
                    pon(x, y, ORO[5] if luz > 0.2 else ORO[4] if luz > -0.15 else ORO[3])
                else:
                    pon(x, y, JADE[7 if luz > 0.18 else 6 if luz > -0.05 else 5 if luz > -0.25 else 4])
            elif d > ER - 4.2:
                pon(x, y, ORO[5] if luz > 0.25 else ORO[4] if luz > 0.0 else ORO[3] if luz > -0.3 else ORO[2])
            else:
                pon(x, y, FONDO)
    return im


# ---------------------------------------------------------------- el relleno
def relleno(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    rnd = random.Random(7)
    w, h = 64, HY1 - HY0
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    tau = 2 * math.pi
    for y in range(h):
        for x in range(w):
            k = [4, 3, 3, 3, 2, 2, 2, 1, 0][y]
            e1 = 5.4 + 1.1 * math.sin(tau * x / 64 * 2 + 0.7) + 0.5 * math.sin(tau * x / 64 * 5 + 2.0)
            if abs(y - e1) < 0.5:
                k -= 1                                  # la junta de los estratos
            e2 = 1.8 + 0.9 * math.sin(tau * x / 32 + 1.3)
            if abs(y - e2) < 0.5 and (x * 3) % 16 < 11:
                k = 5                                   # la veta de energia
            if (x * 7 + y * 13) % 29 == 0:
                k += 1
            elif (x * 5 + y * 11) % 23 == 0 or rnd.random() < 0.05:
                k -= 1
            px[x, y] = R[max(0, min(5, k))]
    return im


# ---------------------------------------------------------------- el emblema
# La espiral cuadrada de oro de sus placas (11x11)
GRECA = set()
for (x0, y0, x1, y1) in ((0, 0, 0, 10), (0, 0, 10, 0), (10, 0, 10, 10), (2, 10, 10, 10), (2, 2, 2, 10), (2, 2, 8, 2),
                         (8, 2, 8, 8), (4, 8, 8, 8), (4, 4, 4, 8), (4, 4, 6, 4), (6, 4, 6, 6)):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            GRECA.add((x, y))
GRIETAS = {
    1: [],
    2: [[(18, 7), (19, 6), (20, 5)], [(6, 17), (5, 18), (4, 19)]],
    3: [[(18, 7), (19, 6), (20, 5), (21, 4)], [(6, 17), (5, 18), (4, 19), (3, 20)],
        [(18, 17), (19, 18), (19, 19), (20, 20)], [(6, 7), (5, 6), (5, 5), (4, 4)]],
    4: [[(18, 7), (19, 6), (20, 5), (21, 4)], [(6, 17), (5, 18), (4, 19), (3, 20)],
        [(18, 17), (19, 18), (19, 19), (20, 20)], [(6, 7), (5, 6), (5, 5), (4, 4)],
        [(12, 5), (12, 4), (13, 3), (13, 2)], [(19, 12), (20, 12), (21, 13)], [(12, 19), (11, 20), (11, 21)],
        [(5, 12), (4, 11), (3, 11), (2, 12)]],
}


def sol(clave):
    R = [hexc(c) for c in RAMPAS[clave]]
    libre = clave == 'libre'
    nivel = 4 if clave == 'furia' else clave if not libre else 1
    im = Image.new('RGBA', (SOL, SOL), (0, 0, 0, 0))
    px = im.load()
    c0 = SOL / 2
    for y in range(SOL):
        for x in range(SOL):
            dx, dy = x + 0.5 - c0, y + 0.5 - c0
            d = math.hypot(dx, dy)
            if d > ER - 4.2:
                continue
            luz = -(dx + dy) / 22.0
            if libre:
                px[x, y] = ORO[4 if luz > 0.1 else 3 if luz > -0.2 else 2]
            else:
                k = 6 if luz > 0.25 else 5 if luz > 0.0 else 4 if luz > -0.25 else 3
                px[x, y] = JADE[k - (1 if nivel == 4 else 0)]
    # la placa en espiral, con su luz arriba a la izquierda y la sombra al otro lado
    ox = oy = 7
    for (gx, gy) in GRECA:
        x, y = ox + gx, oy + gy
        luz = -((gx - 5) + (gy - 5)) / 10.0
        px[x, y] = (R[5] if libre else ORO[5]) if luz > 0.35 else ORO[4] if luz > -0.1 else ORO[3]
        if (gx + 1, gy + 1) not in GRECA and 0 <= x + 1 < SOL and 0 <= y + 1 < SOL and (gx + 1 > 10 or gy + 1 > 10 or True):
            if px[x + 1, y + 1] in [JADE[k] for k in range(9)]:
                px[x + 1, y + 1] = JADE[1]
    # el corazon de la espiral, encendido
    px[ox + 5, oy + 5] = R[5]
    px[ox + 5, oy + 6] = R[3]
    for g in GRIETAS[nivel] if not libre else []:
        for n, (x, y) in enumerate(g):
            px[x, y] = R[5] if n == 0 else R[3]
            if 0 <= x + 1 < SOL and 0 <= y + 1 < SOL and px[x + 1, y + 1][3]:
                px[x + 1, y + 1] = mezclar(px[x + 1, y + 1], JADE[0], 0.5)
    return im


# ---------------------------------------------------------------- muescas y totems
PAL = {'o': JADE[0], 'y': ORO[5], 'Y': ORO[4], 'G': ORO[3], 'g': ORO[2], 'h': ORO[1],
       '8': JADE[8], '7': JADE[7], '6': JADE[6], '5': JADE[5], '4': JADE[4], '3': JADE[3], '2': JADE[2]}
COLMILLO = ["ooooooo",
            "oyYYGgo",
            "ohhhhho",
            "o88765o",
            "o8765Lo",
            ".o76Lo.",
            ".o76Lo.",
            "..o6Lo.",
            "..oLLo.",
            "...oLo.",
            "...oo..",
            "......."]
COLMILLO_ROTO = ["ooooooo",
                 "oyYYGgo",
                 "ohhhhho",
                 "o87o54o",
                 "o8o.o4o",
                 ".o...o.",
                 ".......",
                 ".......",
                 ".......",
                 ".......",
                 ".......",
                 "......."]
# El totem del Sello tal como esta en el juego (TotemSelloRenderer): una columna
# de piedra verde en tres tramos, cada uno con su glifo encendido, bandas de oro
# entre tramos, el remate de oro y la base. Roto: se le cae el tramo de arriba,
# se raja y los glifos se apagan.
TOTEM = [".oYYGo.",
         "o45L54o",
         "oYYYYGo",
         "o4L5L4o",
         "o45L54o",
         "oYYYYGo",
         "o4LLL4o",
         "o45554o",
         "ooooooo"]
TOTEM_ROTO = [".......",
              "..o.o..",
              "oo3o3oo",
              "o3d4o3o",
              "o34d43o",
              "oGYoYGo",
              "o3ddd3o",
              "o34443o",
              "ooooooo"]


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
    ruta = os.path.join(GUI, n + '.png')
    if os.path.exists(ruta):
        return Image.open(ruta).convert('RGBA')
    # Las piezas de la barra de antes ya no estan en el arbol (la nueva las
    # sustituyo): se sacan de git, de antes del cambio.
    import io, subprocess
    rel = 'src/main/resources/assets/atalaya/textures/gui/' + n + '.png'
    datos = subprocess.run(['git', '-C', RAIZ, 'show', 'f26e9f1:' + rel], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(datos)).convert('RGBA')


def nueva(clave, vida, fantasma=None, sello=None, totems_rotos=0):
    """La barra nueva montada como la montaria RajangBarraHud."""
    R = [hexc(c) for c in RAMPAS[clave]]
    im = marco(clave)
    q = im.load()
    lleno = round(190 * vida)
    if fantasma and fantasma > vida:
        for x in range(lleno, round(190 * fantasma)):
            for y in range(HY0, HY1):
                q[HX0 + x, y] = (0xF0, 0xFF, 0xE0, 0xD8)
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
        pal = dict(PAL, L=R[4] if not pasado else JADE[3])
        pintar(im, COLMILLO_ROTO if pasado else COLMILLO, pal, ex, HY0 - 4)
    im.alpha_composite(sol(clave), (EC[0] - SOL // 2, EC[1] - SOL // 2))
    im.alpha_composite(cargar('rajang_barra_nombre'), (92, 9))
    rot = 'rajang_barra_libre' if clave == 'libre' else 'rajang_barra_furia' if clave == 'furia' else f'rajang_barra_fase_{clave}'
    im.alpha_composite(tenir(cargar(rot), COLOR_ROTULO[clave]), (HX0 + 190 - 64 + 1, 8))
    if sello is not None:
        # los cuatro totems y la losa del tiempo, bajo la barra
        for k in range(4):
            roto = totems_rotos & (1 << k)
            pal = dict(PAL, L=(143, 235, 112, 255), d=JADE[1])   # el verde de los glifos de totem_brillo.png
            pintar(im, TOTEM_ROTO if roto else TOTEM, pal, HX0 + 6 + k * 10, 35)
        lx0, lx1, ly = HX0 + 50, HX1 - 2, 37
        for y in range(ly, ly + 5):
            for x in range(lx0, lx1):
                q[x, y] = JADE[0] if y in (ly, ly + 4) or x in (lx0, lx1 - 1) else FONDO
        n = round((lx1 - lx0 - 2) * sello)
        col = R[3] if sello > 0.25 else hexc('ff5a3a')
        for x in range(lx0 + 1, lx0 + 1 + n):
            for y in range(ly + 1, ly + 4):
                q[x, y] = R[4] if y == ly + 1 else col
    return im


def antigua(clave, vida, sello=None, totems_rotos=0):
    """La barra de hoy, como la monta RajangBarraHud (208x26, mas el Sello debajo)."""
    color = COLOR_ROTULO[clave]
    im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
    ox, oy = (NW - 208) // 2, 8
    im.alpha_composite(cargar('rajang_barra_marco'), (ox, oy))
    hx, hy = ox + 28, oy + 9
    lleno = round(172 * vida)
    rel = tenir(cargar('rajang_barra_relleno'), color)
    x = 0
    while x < lleno:
        w = min(64, lleno - x)
        im.alpha_composite(rel.crop((0, 0, w, 8)), (hx + x, hy))
        x += w
    for corte in (0.75, 0.5, 0.25):
        mu = 'rajang_barra_muesca_rota' if vida < corte else 'rajang_barra_muesca'
        im.alpha_composite(cargar(mu), (hx + round(172 * corte) - 3, hy - 2))
    nombre_sol = 'rajang_barra_sol_libre' if clave == 'libre' else 'rajang_barra_sol_4' if clave == 'furia' else f'rajang_barra_sol_{clave}'
    im.alpha_composite(cargar(nombre_sol), (ox + 13 - 8, oy + 13 - 8))
    im.alpha_composite(cargar('rajang_barra_nombre'), (hx, oy + 7 - 10))
    rot = 'rajang_barra_libre' if clave == 'libre' else 'rajang_barra_furia' if clave == 'furia' else f'rajang_barra_fase_{clave}'
    im.alpha_composite(tenir(cargar(rot), color), (hx + 172 - 64 + 1, oy + 7 - 10))
    if sello is not None:
        q = im.load()
        y0 = oy + 26 + 1
        x = hx + 44
        ancho = 172 - 44
        for yy in range(y0 - 1, y0 + 4):
            for xx in range(x - 1, x + ancho + 1):
                q[xx, yy] = (0x10, 0x20, 0x16, 0xC0)
        for yy in range(y0, y0 + 3):
            for xx in range(x, x + round(ancho * sello)):
                q[xx, yy] = (0x7C, 0xFF, 0x5A, 255) if sello > 0.25 else (0xFF, 0x5A, 0x3A, 255)
        for i in range(4):
            tx = hx + i * 10
            roto = totems_rotos & (1 << i)
            for yy in range(y0 - 1, y0 + 5):
                for xx in range(tx, tx + 7):
                    q[xx, yy] = (0x18, 0x2A, 0x1E, 0xD0)
            for yy in range(y0, y0 + 4):
                for xx in range(tx + 1, tx + 6):
                    q[xx, yy] = (0x3A, 0x3A, 0x32, 255) if roto else (0x8C, 0xFF, 0x5A, 255)
    return im


# ---------------------------------------------------------------- al juego
if JUEGO:
    for clave in (1, 2, 3, 4, 'furia', 'libre'):
        marco(clave).save(os.path.join(GUI, f'rajang_barra_marco_{clave}.png'))
        relleno(clave).save(os.path.join(GUI, f'rajang_barra_relleno_{clave}.png'))
        sol(clave).save(os.path.join(GUI, f'rajang_barra_nucleo_{clave}.png'))
    for nombre, dibujo, pal in (('colmillo', COLMILLO, dict(PAL, L=JADE[7])),
                                ('colmillo_roto', COLMILLO_ROTO, dict(PAL, L=JADE[3])),
                                ('totem', TOTEM, dict(PAL, L=(143, 235, 112, 255), d=JADE[1])),
                                ('totem_roto', TOTEM_ROTO, dict(PAL, L=(143, 235, 112, 255), d=JADE[1]))):
        im = Image.new('RGBA', (len(dibujo[0]), len(dibujo)), (0, 0, 0, 0))
        pintar(im, dibujo, pal)
        im.save(os.path.join(GUI, f'rajang_barra_{nombre}.png'))
    # Las piezas de la barra de antes (208x26) ya no las usa nadie.
    for viejo in ['rajang_barra_marco', 'rajang_barra_relleno', 'rajang_barra_muesca', 'rajang_barra_muesca_rota',
                  'rajang_barra_sol_libre'] + [f'rajang_barra_sol_{n}' for n in (1, 2, 3, 4)]:
        if os.path.exists(os.path.join(GUI, viejo + '.png')):
            os.remove(os.path.join(GUI, viejo + '.png'))
    print('barra de Rajang escrita en', GUI)
    sys.exit(0)


# ---------------------------------------------------------------- hojas
ESTADOS = [('Fase I', 1, 0.92, 0.97, None, 0), ('Fase II', 2, 0.66, None, None, 0),
           ('Fase III, durante el Sello', 3, 0.41, None, 0.6, 0b0101), ('Fase IV', 4, 0.18, 0.26, None, 0),
           ('Furia de Jade', 'furia', 0.22, None, None, 0), ('Liberado', 'libre', 0.0, None, None, 0)]

K = 4
fondo = (36, 52, 40, 255)
for nombre, clave, vida, fantasma, sello, rotos in ESTADOS:
    pass
hoja = Image.new('RGBA', (NW * K * 2 + 60, len(ESTADOS) * (NH * K + 20) + 20), fondo)
for i, (nombre, clave, vida, fantasma, sello, rotos) in enumerate(ESTADOS):
    y = 20 + i * (NH * K + 20)
    a = antigua(clave, vida, sello, rotos).resize((NW * K, NH * K), Image.NEAREST)
    n = nueva(clave, vida, fantasma, sello, rotos).resize((NW * K, NH * K), Image.NEAREST)
    hoja.alpha_composite(a, (20, y))
    hoja.alpha_composite(n, (NW * K + 40, y))
hoja.save(os.path.join(SALIDA, 'rajang_barra_hoja.png'))

# Por separado, para la ficha: antes y despues de cada estado, a 4x
for i, (nombre, clave, vida, fantasma, sello, rotos) in enumerate(ESTADOS):
    clave_txt = str(clave)
    antigua(clave, vida, sello, rotos).resize((NW * K, NH * K), Image.NEAREST).save(os.path.join(SALIDA, f'barra_antes_{clave_txt}.png'))
    nueva(clave, vida, fantasma, sello, rotos).resize((NW * K, NH * K), Image.NEAREST).save(os.path.join(SALIDA, f'barra_nueva_{clave_txt}.png'))


# En partida: la foto de una escena con la barra de hoy tapada por la nueva
def en_partida(foto, clave, vida, sello=None, rotos=0, salida=None):
    im = Image.open(foto).convert('RGBA')
    q = im.load()
    W = im.width
    # se tapa la barra de hoy con el cielo de cada fila (la mediana de los lados)
    for y in range(0, 70):
        fila = sorted([q[x, y][:3] for x in list(range(0, 200)) + list(range(W - 200, W))], key=sum)
        c = fila[len(fila) // 2]
        for x in range(205, W - 205):
            q[x, y] = (*c, 255)
    barra = nueva(clave, vida, None, sello, rotos).resize((NW * 2, NH * 2), Image.NEAREST)
    im.alpha_composite(barra, ((W - NW * 2) // 2, 10))
    im.convert('RGB').save(salida)


en_partida(os.path.join(FOTOS, 'ronda6', 'rajang_garra.png'), 1, 0.92, salida=os.path.join(SALIDA, 'partida_fase1.png'))
en_partida(os.path.join(FOTOS, 'ronda5', 'rajang_sello_pulso.png'), 3, 0.41, 0.6, 0b0101, salida=os.path.join(SALIDA, 'partida_sello.png'))
en_partida(os.path.join(FOTOS, 'ronda5', 'rajang_furia.png'), 'furia', 0.22, salida=os.path.join(SALIDA, 'partida_furia.png'))
print('ok', SALIDA)

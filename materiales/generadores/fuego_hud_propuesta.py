"""
La barra del Caballero Solar (propuesta), pixel a pixel, al estilo de las de
Aeralis, Rajang y Nerea del remake. Solo vista previa para la ficha: no
escribe nada en el repo.

  - Mismas medidas que las otras tres (240x44, hueco de 190x9 en (40,22),
    emblema centrado en (19,26)).
  - El emblema: un sol con el filo de oro y ocho rayos cortos y, delante, el
    yelmo del caballero: acero quemado, la rendija en T encendida y una corona
    de llamas encima, que crece con cada fase.
  - Encima del marco, en lugar del ala, la ola o los cristales: llamas que
    lamen el canto, del emblema hacia la derecha, en el color de la fase.
  - El marco de acero quemado con grietas de lava finas (mas cada fase, y
    carmesi en la IV), el filo de oro y la punta de rayo a la derecha.
  - El relleno con el color dentro (lava que corre con su costra y lenguas
    por arriba), el frente encendido y el rastro claro del ultimo golpe,
    igual que en la de Rajang.
  - Las muescas: rayos de sol de oro; al pasarlas, apagadas y rajadas.
  - Bajo la barra, como los totems de Rajang y los ojos de Nerea:
      fuentes     las tres fuentes solares y la carga del sol (fase III)
      trompetas   los cuatro angeles y la melodia (fase II)
      ofrenda     el sol con el cautivo y su liberacion (lo que ven los demas)
      grito       el cuerno carmesi junto a la fase (fase IV, Grito de guerra)
  - Con la Furia, todo en fuego azul y el rotulo FURIA.
  - Ademas: los tres iconos de la Quemadura (18x18) y la pantalla de la
    Ofrenda al sol (las teclas a seguir), normal y fallada.

Uso: python fuego_hud_propuesta.py <carpeta de salida>

Escribe en la carpeta las barras a x4 (barra_*.png), las mismas a x1 en raw/,
quemadura.png (x6 sobre pizarra) y qte.png / qte_fallo.png (854x480).
"""
from PIL import Image
from collections import deque
import math, os, random, sys

SALIDA = sys.argv[1]
RAW = os.path.join(SALIDA, 'raw')
os.makedirs(RAW, exist_ok=True)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mezclar(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def alfa(c, a):
    return (c[0], c[1], c[2], a)


# ---------------------------------------------------------------- paletas
# Acero quemado y oro: las dos rampas de la ficha. El contorno no es negro: es
# el tono mas hondo del acero, y el fondo del hueco tira al pardo.
ACERO = [hexc(c) for c in ('1c1416', '2b1d1c', '3d2a25', '54382d', '6e4a38')]
ORO = [hexc(c) for c in ('5a3410', '8a5418', 'c07c22', 'e8a83a', 'ffd77a')]
CONTORNO = hexc('120b0b')
FONDO = hexc('140c0a')
OSCURO = hexc('0a0606')
BASALTO = [hexc(c) for c in ('1a1716', '2c2725', '433b36', '5e544b', '7c7064')]
MARMOL = [hexc(c) for c in ('4c4640', '7c7468', 'a8a090', 'd0c8b2', 'f0e9d6')]
VERDE = [hexc(c) for c in ('0c2410', '1c5222', '348c34', '62cc4e', 'aef08e', 'e6ffd4')]
CARMESI = [hexc(c) for c in ('2c0408', '6e0a16', 'b8142a', 'ff2a3a', 'ff9a84', 'ffe4d8')]
ROJO = hexc('ff4a2a')
# El fuego de cada fase, de la brasa honda al nucleo (el [3] es el color de la
# fase). El nucleo nunca es blanco puro: tira al color.
RAMPAS = {
    1: ('2a0c04', '6a1e06', 'b84a0c', 'ff8a1e', 'ffc070', 'fff0d0'),
    2: ('2e1404', '7a3a08', 'c87810', 'ffc23a', 'ffe48a', 'fffae0'),
    3: ('3a1c06', '8a5014', 'd8a038', 'fff0b0', 'fffadc', 'fffff2'),
    4: ('2c0408', '6e0a16', 'b8142a', 'ff2a3a', 'ff9a84', 'ffe4d8'),
    'furia': ('041828', '0a3c62', '1a78b8', '5ad8ff', 'b4f2ff', 'f0fdff'),
}
COLOR_ROTULO = {1: 0xFF8A1E, 2: 0xFFC23A, 3: 0xFFF0B0, 4: 0xFF2A3A, 'furia': 0x5AD8FF}
RASTRO = {'fuego': (0xFF, 0xF2, 0xD8, 0xD8), 'furia': (0xE4, 0xF8, 0xFF, 0xD8)}


def rampa(clave):
    return [hexc(c) for c in RAMPAS[clave]]


def nivel_de(clave):
    return 4 if clave == 'furia' else clave


NW, NH = 240, 44
HX0, HX1, HY0, HY1 = 40, 230, 22, 31
EC = (19, 26)
ER = 15.5
NUC = 24
ALTO_ESPECIAL = 56


def dentro(poly, x, y):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1:
            c = not c
    return c


VEC4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def capas(pts, suelo=None):
    """Pasos hasta el aire mas cercano (vecindad-4, DISENO 18). Lo que queda por
    debajo de 'suelo' no cuenta como aire: el fuego sigue detras del marco."""
    d = {}
    cola = deque()
    for (x, y) in pts:
        for dx, dy in VEC4:
            n = (x + dx, y + dy)
            if n not in pts and not (suelo is not None and n[1] >= suelo):
                d[(x, y)] = 0
                cola.append((x, y))
                break
    while cola:
        p = cola.popleft()
        for dx, dy in VEC4:
            n = (p[0] + dx, p[1] + dy)
            if n in pts and n not in d:
                d[n] = d[p] + 1
                cola.append(n)
    for p in pts:
        d.setdefault(p, 9)
    return d


def borde4(pts, suelo=None):
    """El contorno se calcula: el aire que toca la forma por un lado."""
    fuera = set()
    for (x, y) in pts:
        for dx, dy in VEC4:
            n = (x + dx, y + dy)
            if n not in pts and not (suelo is not None and n[1] >= suelo):
                fuera.add(n)
    return fuera


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


# ---------------------------------------------------------------- letras en pixel
# Las de rajang_hud.py (relleno, contorno de un pixel y sombra), con las que
# faltaban para este jefe y la pantalla de la ofrenda. La exclamacion de abrir
# va escrita como \u00a1 para que el fichero siga siendo ASCII.
GLIFOS = {
    'A': [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    'B': ["#####.", "##..##", "##..##", "#####.", "##..##", "##..##", "#####."],
    'C': [".#####", "##....", "##....", "##....", "##....", "##....", ".#####"],
    'D': ["#####.", "##..##", "##..##", "##..##", "##..##", "##..##", "#####."],
    'E': ["######", "##....", "##....", "#####.", "##....", "##....", "######"],
    'F': ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    'G': [".#####", "##....", "##....", "##.###", "##..##", "##..##", ".####."],
    'I': ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    'L': ["##....", "##....", "##....", "##....", "##....", "##....", "######"],
    'N': ["##..##", "###.##", "######", "##.###", "##..##", "##..##", "##..##"],
    'O': [".####.", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    'R': ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    'S': [".#####", "##....", "##....", ".####.", "....##", "....##", "#####."],
    'T': ["######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##.."],
    'U': ["##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    'V': ["##..##", "##..##", "##..##", "##..##", ".####.", ".####.", "..##.."],
    'W': ["##...##", "##...##", "##...##", "##.#.##", "#######", "###.###", "##...##"],
    '!': ["##", "##", "##", "##", "##", "..", "##"],
    '\u00a1': ["##", "..", "##", "##", "##", "##", "##"],
    ' ': ["..", "..", "..", "..", "..", "..", ".."],
}
# Una letra pequena (3x5) para los rotulos de la pantalla de la ofrenda.
MINI = {
    'A': ["###", "#.#", "###", "#.#", "#.#"], 'B': ["##.", "#.#", "##.", "#.#", "##."],
    'C': ["###", "#..", "#..", "#..", "###"], 'E': ["###", "#..", "##.", "#..", "###"],
    'G': ["###", "#..", "#.#", "#.#", "###"], 'I': ["###", ".#.", ".#.", ".#.", "###"],
    'L': ["#..", "#..", "#..", "#..", "###"], 'N': ["##.", "#.#", "#.#", "#.#", "#.#"],
    'O': ["###", "#.#", "#.#", "#.#", "###"], 'R': ["##.", "#.#", "##.", "#.#", "#.#"],
    'S': ["###", "#..", "###", "..#", "###"], 'T': ["###", ".#.", ".#.", ".#.", ".#."],
    'U': ["#.#", "#.#", "#.#", "#.#", "###"], 'M': ["#.#", "###", "###", "#.#", "#.#"],
    'P': ["##.", "#.#", "##.", "#..", "#.."], 'D': ["##.", "#.#", "#.#", "#.#", "##."],
    ' ': ["..", "..", "..", "..", ".."],
}
BORDE_LETRA = hexc('140806')
SOMBRA = (0, 0, 0, 110)


def palabra(texto, relleno, borde=BORDE_LETRA, sombra=SOMBRA, ancho=None, derecha=False, glifos=GLIFOS, escala=1):
    """La misma que rajang_hud.py: relleno, contorno de un pixel y sombra."""
    puntos = set()
    x = 0
    alto_g = len(glifos['A'])
    for ch in texto:
        g = glifos[ch]
        for fy, fila in enumerate(g):
            for fx, c in enumerate(fila):
                if c == '#':
                    for sx in range(escala):
                        for sy in range(escala):
                            puntos.add(((x + fx) * escala + sx, fy * escala + sy))
        x += len(g[0]) + 1
    w_txt = (x - 1) * escala + 2
    w = ancho or w_txt
    h = alto_g * escala + 3
    ox = (w - w_txt if derecha else 0) + 1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    q = im.load()
    for (px, py) in puntos:
        for dx in (0, 1, -1):
            xx, yy = px + ox + dx, py + 3
            if 0 <= xx < w and 0 <= yy < h and sombra:
                q[xx, yy] = sombra
    for (px, py) in puntos:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = px + ox + dx, py + 1 + dy
                if 0 <= xx < w and 0 <= yy < h and (px + dx, py + dy) not in puntos:
                    q[xx, yy] = borde
    for (px, py) in puntos:
        q[px + ox, py + 1] = relleno(px, py // escala)
    return im


def gris(fx, fila):
    v = [255, 246, 236, 224, 210, 196, 182][min(6, fila)]
    return (v, v, v, 255)


def oro_claro(fx, fila):
    return hexc(['fffbea', 'fff3cc', 'ffe8ac', 'ffdc8c', 'f8cc70', 'eebb58', 'e0a844'][min(6, fila)])


def de_rampa(colores):
    return lambda fx, fila: colores[min(len(colores) - 1, fila)]


NOMBRE = palabra('NOVILIS', oro_claro)
ROTULO_X = HX0 + 190 - 64 + 1
# El nombre va donde el de Rajang (x = 92) si cabe antes de FASE IV con el sitio
# del cuerno del Grito; la cresta acaba antes del nombre.
NOMBRE_X = min(92, ROTULO_X + 64 - 43 - 17 - NOMBRE.width)
CRESTA_FIN = NOMBRE_X - 3
# Las lenguas de la cresta: (centro, media base, alto, cuanto se va a la derecha)
LENGUAS = ((30, 6, 20, 0.26), (41, 5, 15, 0.32), (50, 4, 11, 0.38), (57, 3, 8, 0.45), (63, 2, 5, 0.5))


# ---------------------------------------------------------------- fuego
def lengua(cx, base, semi, alto, lean):
    """Una lengua de fuego: panza abajo, la punta se va hacia la derecha."""
    tx = cx + lean * alto
    return [(cx - semi, base), (cx - semi - 0.8 + lean * alto * 0.2, base - alto * 0.35),
            (cx - semi * 0.45 + lean * alto * 0.62, base - alto * 0.72), (tx, base - alto),
            (cx + semi * 0.25 + lean * alto * 0.55, base - alto * 0.55),
            (cx + semi + 0.5 + lean * alto * 0.15, base - alto * 0.2), (cx + semi, base)]


def fuego(pon, pts, R, suelo=None, contorno=True):
    """Un cuerpo de fuego: el color por pasos hasta el aire (borde frio, nucleo
    caliente), y el contorno calculado en el tono mas hondo de la fase."""
    d = capas(pts, suelo)
    if contorno:
        for p in borde4(pts, suelo):
            pon(p[0], p[1], R[0])
    for (x, y), k in d.items():
        pon(x, y, R[min(5, 2 + k)])


# ---------------------------------------------------------------- el marco
GRIETAS_V = [((0, 0), (1, 1), (2, 1), (3, 0)), ((0, 1), (1, 0), (2, 0), (3, 1), (4, 1)),
             ((0, 0), (1, 0), (2, 1), (3, 1)), ((0, 1), (1, 1), (2, 0))]


def lista_grietas():
    rnd = random.Random(41)
    out = []
    xs = list(range(HX0 + 6, HX1 - 8, 15))
    rnd.shuffle(xs)
    for x in xs:
        out.append((x + rnd.randint(-3, 3), rnd.choice(('abajo', 'abajo', 'arriba')), rnd.choice(GRIETAS_V)))
    return out


GRIETAS = lista_grietas()
CUANTAS_GRIETAS = {1: 3, 2: 5, 3: 7, 4: 12, 'furia': 12}
ALTO_CRESTA = {1: 0.78, 2: 0.88, 3: 0.95, 4: 1.0, 'furia': 1.0}


def marco(clave, alto=NH):
    R = rampa(clave)
    nivel = nivel_de(clave)
    rnd = random.Random(19)
    im = Image.new('RGBA', (NW, alto), (0, 0, 0, 0))
    px = im.load()

    def pon(x, y, c):
        if 0 <= x < NW and 0 <= y < alto:
            px[x, y] = c

    y_top, y_bot = HY0 - 3, HY1 + 2
    x_izq, x_der = HX0 - 8, HX1 + 2

    # la cresta: lenguas de fuego que salen del emblema y lamen el canto hacia
    # la derecha, las grandes junto al emblema (como los cristales de Rajang)
    f = ALTO_CRESTA[clave]
    pts = set()
    # el lecho de fuego sobre el canto, que adelgaza hacia la derecha
    for x in range(22, CRESTA_FIN):
        h = 5.5 - 4.5 * (x - 22) / (CRESTA_FIN - 22)
        for y in range(round(y_top + 1 - h), y_top + 1):
            pts.add((x, y))
    for (cx, semi, h, lean) in LENGUAS:
        poly = lengua(cx, y_top + 1, semi, h * f, lean)
        pts |= {(x, y) for y in range(0, y_top + 1) for x in range(18, 90) if dentro(poly, x + 0.5, y + 0.5)}
    # una pequena detras del emblema, a la izquierda, que se va hacia fuera
    poly = lengua(7, 18, 3, 11 * f, -0.45)
    pts |= {(x, y) for y in range(0, 18) for x in range(0, 16) if dentro(poly, x + 0.5, y + 0.5)}
    fuego(pon, pts, R, suelo=y_top + 1)
    # chispas sueltas, repartidas sin simetria
    for (x, y, k) in ((50, 3, 4), (63, 6, 3), (69, 10, 4), (42, 1, 3), (3, 4, 3), (58, 13, 3)):
        if (x, y) not in pts and y < y_top and (f > 0.8 or k == 4):
            pon(x, y, R[k])

    # el marco de acero quemado, en placas de 16 con su junta
    for y in range(y_top, y_bot + 1):
        for x in range(x_izq, x_der + 1):
            if HX0 <= x < HX1 and HY0 <= y < HY1:
                pon(x, y, FONDO)
                continue
            if y in (y_top, y_bot) or x in (x_izq, x_der):
                pon(x, y, CONTORNO)
                continue
            u = (x - x_izq) % 16
            if y == y_top + 1:
                # el filo de oro, con su brillo al empezar cada placa
                c = ORO[1] if u == 0 else ORO[4] if u in (1, 2) else ORO[3]
                if u not in (0, 1, 2) and rnd.random() < 0.08:
                    c = ORO[4]
            elif y == y_bot - 1:
                c = ACERO[0] if u == 0 else ACERO[1]
            elif y < HY0:
                c = ACERO[1] if u == 0 else ACERO[4] if u == 1 else ACERO[3]
                if u > 1 and rnd.random() < 0.15:
                    c = ACERO[2]
            else:
                c = ACERO[0] if u == 0 else ACERO[3] if u == 1 else ACERO[2]
                if u > 1 and rnd.random() < 0.12:
                    c = ACERO[1]
            pon(x, y, c)
    for x in range(HX0, HX1):
        pon(x, HY0, OSCURO)
    # remaches de oro abajo, en el centro de cada placa
    for x in range(x_izq + 8, x_der - 4, 16):
        pon(x, y_bot - 1, ORO[3])
        pon(x + 1, y_bot - 1, ORO[1])
    # las grietas de lava: pocas en la I, muchas en la IV (y entonces carmesi,
    # tambien cruzando el oro)
    G = CARMESI if nivel == 4 and clave != 'furia' else R
    for (x0, banda, forma) in GRIETAS[:CUANTAS_GRIETAS[clave]]:
        y0 = HY1 if banda == 'abajo' else HY0 - 1
        for n, (dx, dy) in enumerate(forma):
            yy = y0 + dy if banda == 'abajo' else y0 - dy
            if banda == 'arriba' and yy < HY0 - 1 and nivel < 4:
                continue
            c = G[4] if n == len(forma) // 2 else G[3] if 0 < n < len(forma) - 1 else G[2]
            pon(x0 + dx, yy, c)
    # la punta derecha: un rayo de oro
    yc = (y_top + y_bot) // 2
    for i in range(8):
        semi = 7 - i
        for dy in range(-semi, semi + 1):
            borde = abs(dy) == semi or i == 7
            if borde:
                c = CONTORNO
            elif dy == 0:
                c = R[4]
            else:
                c = ORO[4] if dy < -semi / 2 else ORO[3] if dy < 0 else ORO[2] if dy <= semi / 2 else ORO[1]
            pon(x_der + i, yc + dy, c)

    # el emblema: el aro de acero quemado, los ocho rayos de oro del sol (los
    # cuatro rectos asoman mas por fuera del aro) y el filo de oro del disco
    rayos = set()
    for y in range(NH):
        for x in range(40):
            dx, dy = x + 0.5 - EC[0], y + 0.5 - EC[1]
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            k = round(ang / (math.pi / 4))
            da = ang - k * math.pi / 4
            largo = 19.6 if k % 2 == 0 else 17.4
            ancho = 2.7 * (1 - (d - 10.5) / (largo - 10.5))
            if 10.5 < d < largo and abs(d * math.sin(da)) < ancho:
                rayos.add((x, y))
    for (x, y) in borde4(rayos):
        if math.hypot(x + 0.5 - EC[0], y + 0.5 - EC[1]) > ER - 1.2:
            pon(x, y, CONTORNO)
    for y in range(NH):
        for x in range(40):
            dx, dy = x + 0.5 - EC[0], y + 0.5 - EC[1]
            d = math.hypot(dx, dy)
            luz = -(dx + dy) / (2 * ER)
            if (x, y) in rayos and d > ER - 4.2:
                c = ORO[4] if luz > 0.15 else ORO[3] if luz > -0.15 else ORO[2]
                if d > ER + 0.5:
                    c = ORO[4] if luz > -0.1 else ORO[3]
                pon(x, y, c)
                continue
            if d > ER:
                continue
            if d > ER - 1.2:
                pon(x, y, CONTORNO)
            elif d > ER - 3.2:
                pon(x, y, ACERO[4 if luz > 0.25 else 3 if luz > 0.0 else 2 if luz > -0.25 else 1])
            elif d > ER - 4.2:
                pon(x, y, ORO[4] if luz > 0.25 else ORO[3] if luz > -0.05 else ORO[2] if luz > -0.3 else ORO[1])
            else:
                pon(x, y, FONDO)
    return im


# ---------------------------------------------------------------- el relleno
def relleno(clave):
    """La lava que corre: lenguas por arriba, el rio encendido, la costra oscura
    abajo y vetas en diagonal que dicen hacia donde va. Se repite cada 64."""
    R = rampa(clave)
    rnd = random.Random(5)
    w, h = 64, HY1 - HY0
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    tau = 2 * math.pi
    for y in range(h):
        for x in range(w):
            k = [3, 4, 4, 4, 3, 3, 2, 2, 1][y]
            # las lenguas de arriba: puntas claras y el hueco entre ellas mas hondo
            cresta = 1.2 + 0.9 * math.sin(tau * x / 16) + 0.5 * math.sin(tau * x / 64 * 3 + 1.1)
            if y < cresta:
                k = 2 if y == 0 else 3
            elif y < cresta + 1:
                k = 5
            # vetas de lava en diagonal (corren hacia la derecha)
            if 1 <= y <= 5 and (x - 2 * y) % 13 in (0, 1):
                k = 5 if y < 4 else 4
            # la costra: placas oscuras abajo
            costra = 6.4 + 0.9 * math.sin(tau * x / 32 + 0.4) + 0.4 * math.sin(tau * x / 64 * 5)
            if y > costra:
                k = min(k, 1)
                if (x * 5 + y * 3) % 17 == 0:
                    k = 3
            if rnd.random() < 0.04:
                k = max(1, k - 1)
            px[x, y] = R[max(0, min(5, k))]
    return im


# ---------------------------------------------------------------- el emblema: sol y yelmo
# El yelmo (un gran yelmo de cubo) se escribe como datos: medias anchuras por
# fila sobre el eje 12.0, y encima los rasgos. Ancho par para que la rendija
# vertical, de 2, quede centrada.
EJE = 12
YELMO_ARRIBA = 10
#              10 11 12 13 14 15 16 17 18 19 20 21
YELMO_SEMI = [5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 4]
FILA_ARO = 1          # el aro de oro de donde sale la corona
FILA_OJOS = 4         # la rendija de los ojos
BAJA_RENDIJA = 8      # hasta donde baja la rendija vertical
# La corona de llamas, por fases: alto de cada columna sobre el aro (12
# columnas, simetrica): tres llamas, la de en medio mas alta. La I apenas
# asoma; la IV arde alta.
CORONA = {
    1: [0, 1, 2, 1, 1, 3, 3, 1, 1, 2, 1, 0],
    2: [0, 2, 3, 1, 2, 4, 4, 2, 1, 3, 2, 0],
    3: [1, 3, 4, 2, 2, 5, 5, 2, 2, 4, 3, 1],
    4: [1, 4, 5, 2, 3, 7, 7, 3, 2, 5, 4, 1],
}


def yelmo_puntos():
    pts = set()
    for i, semi in enumerate(YELMO_SEMI):
        for x in range(EJE - semi, EJE + semi):
            pts.add((x, YELMO_ARRIBA + i))
    return pts


def nucleo(clave):
    R = rampa(clave)
    nivel = nivel_de(clave)
    im = Image.new('RGBA', (NUC, NUC), (0, 0, 0, 0))
    px = im.load()
    c0 = NUC / 2

    def pon(x, y, c):
        if 0 <= x < NUC and 0 <= y < NUC:
            px[x, y] = c

    # la cara del sol: arde mas junto al yelmo (contraluz) y se apaga hacia el filo
    for y in range(NUC):
        for x in range(NUC):
            dx, dy = x + 0.5 - c0, y + 0.5 - c0
            d = math.hypot(dx, dy)
            if d > ER - 4.2:
                continue
            luz = -(dx + dy) / 22.0
            k = 5 if d < 7.5 else 4 if d < 9.2 else 3 if d < 10.4 else 2
            if luz < -0.3 and k > 2:
                k -= 1
            pon(x, y, R[k])
    # la corona de llamas: nace del aro del yelmo, con contorno para leerse contra el sol
    base = YELMO_ARRIBA + FILA_ARO
    pts = set()
    for i, h in enumerate(CORONA[nivel]):
        x = EJE - 6 + i
        for y in range(base - h - 1, base):
            pts.add((x, y))
    for p in borde4(pts, suelo=base):
        pon(p[0], p[1], OSCURO)
    for (x, y) in pts:
        alto = base - y
        pon(x, y, R[5] if alto <= 2 else R[4] if (x, y - 1) in pts else R[3])
    # el yelmo: contorno, acero de cilindro (luz a la izquierda), el aro de oro,
    # la rendija en T encendida y dos remaches
    pts = yelmo_puntos()
    for p in borde4(pts):
        pon(p[0], p[1], OSCURO)
    for (x, y) in pts:
        i = y - YELMO_ARRIBA
        u = (x - (EJE - 6)) / 12.0           # 0 a la izquierda, 1 a la derecha
        k = 4 if 0.12 < u < 0.3 else 3 if u < 0.5 else 2 if u < 0.72 else 1 if u < 0.9 else 0
        if i <= 1:
            k = min(4, k + 1)
        if i >= len(YELMO_SEMI) - 2:
            k = max(0, k - 1)
        c = ACERO[k]
        if i == FILA_ARO:
            c = ORO[4] if u < 0.3 else ORO[3] if u < 0.65 else ORO[2]
        elif i == FILA_ARO + 1:
            c = mezclar(ACERO[k], OSCURO, 0.4)
        if i == FILA_OJOS and EJE - 5 <= x < EJE + 5:
            c = R[5] if x < EJE + 2 else R[4]
        if i == FILA_OJOS - 1 and EJE - 5 <= x < EJE + 5:
            c = mezclar(c, OSCURO, 0.5)             # la ceja de la rendija
        if FILA_OJOS < i <= BAJA_RENDIJA and EJE - 1 <= x <= EJE:
            c = R[5] if i < FILA_OJOS + 3 else R[4] if i < BAJA_RENDIJA else R[3]
        pon(x, y, c)
    for (x, y) in ((EJE - 4, YELMO_ARRIBA + 7), (EJE + 3, YELMO_ARRIBA + 7)):
        pon(x, y, ORO[3])
    return im


# ---------------------------------------------------------------- muescas
PAL_MUESCA = {'o': CONTORNO, 'Y': ORO[4], 'G': ORO[3], 'g': ORO[2], 'h': ORO[1],
              '1': ACERO[0], '2': ACERO[1], '3': ACERO[2], '4': ACERO[3], '5': ACERO[4]}
# El rayo de sol de oro: un tachon en el canto de arriba con el nucleo
# encendido y la punta que baja sobre el fuego. Pasado: apagado y rajado, sin
# punta.
RAYO = ["...o...",
        "..oYo..",
        ".oYGGo.",
        "oYGWGgo",
        ".oGggo.",
        ".oLLLo.",
        "..oLo..",
        "..oLo..",
        "...o..."]
RAYO_ROTO = ["...o...",
             "..o4o..",
             ".o4o3o.",
             "o43o22o",
             ".o3o2o.",
             "..o1o..",
             "...o...",
             ".......",
             "......."]


# ---------------------------------------------------------------- piezas de las vistas especiales
# La fuente solar (11x18): el orbe del sol (con cuatro destellos, para que no
# sea una perla) en su copa de oro, el capitel, la columna de basalto y la
# basa de oro. Entera, rajada (5 de 10 golpes: la grieta deja salir la luz) y
# rota (sin orbe, la columna partida y apagada).
FUENTE = ["....ooo....",
          ".s.oWVVo.s.",
          "..oWWVvvo..",
          "s.oWVVvvo.s",
          "..oVVvvro..",
          "...ovrro...",
          "..ooooooo..",
          "..oYYGGgo..",
          "oYYYYGGGggo",
          "ohhhhhhhhho",
          "..o54322o..",
          "..o54322o..",
          "..o54322o..",
          "..o54322o..",
          "..o54322o..",
          ".oYYYGGggo.",
          "oYGGGGGggho",
          "ooooooooooo"]
FUENTE_RAJADA = ["....ooo....",
                 "...oWoVo...",
                 "..oWWVovo..",
                 "..oWVovvo..",
                 "..oVoovro..",
                 "...ovrro...",
                 "..ooooooo..",
                 "..oYYGogo..",
                 "oYYYYGoGggo",
                 "ohhhhhohhho",
                 "..o54Lo2o..",
                 "..o5oL22o..",
                 "..o54oL2o..",
                 "..o5L3o2o..",
                 "..o5oL22o..",
                 ".oYYYoGggo.",
                 "oYGGGoGggho",
                 "ooooooooooo"]
FUENTE_ROTA = ["...........",
               "...........",
               "...........",
               "...........",
               "...........",
               "...........",
               "...........",
               "...........",
               "..o........",
               ".o1o..o....",
               "..o2o.o1o..",
               "..o2o12oo..",
               "..o21o11o..",
               "..o2o111o..",
               "..o21o11o..",
               ".oggghhh0o.",
               "oghhhhhhh0o",
               "ooooooooooo"]


def angel(roto=False):
    """El angel de piedra (14x16), de perfil hacia la derecha: el ala alzada
    detras, la cabeza, la tunica, el pedestal con su filo de oro y la trompeta
    de oro con la campana abierta. Roto: un monton de cascotes, un trozo de
    ala y la trompeta doblada encima."""
    W, H = 14, 16
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    q = im.load()
    piezas = {}
    if not roto:
        for y in range(H):
            for x in range(W):
                cx, cy = x + 0.5, y + 0.5
                if dentro([(0.2, 0.2), (3.0, 2.4), (5.6, 6.2), (5.6, 10.2), (2.6, 10.6), (0.6, 6.0)], cx, cy):
                    piezas[(x, y)] = 'ala'
                if math.hypot(cx - 7.0, cy - 3.6) <= 2.1:
                    piezas[(x, y)] = 'cabeza'
                if dentro([(5.2, 5.8), (8.6, 5.8), (10.4, 13.0), (3.4, 13.0)], cx, cy):
                    piezas[(x, y)] = 'cuerpo'
                if 2 <= x <= 11 and 13 <= y <= 14:
                    piezas[(x, y)] = 'pedestal'
        for p in ((8, 6), (9, 6), (9, 5)):
            piezas[p] = 'cuerpo'                          # el brazo
        for p in ((9, 4), (10, 4), (11, 3), (12, 2), (12, 3), (13, 1), (13, 2), (13, 3), (13, 4), (12, 1), (12, 4)):
            piezas[p] = 'oro'                             # la trompeta y su campana
    else:
        for y in range(H):
            for x in range(W):
                cx, cy = x + 0.5, y + 0.5
                if dentro([(1.5, 13.2), (3.0, 10.6), (5.0, 9.4), (7.0, 10.2), (8.6, 8.8), (10.6, 10.4), (12.0, 13.2)], cx, cy):
                    piezas[(x, y)] = 'cuerpo'
                if 2 <= x <= 11 and 13 <= y <= 14:
                    piezas[(x, y)] = 'pedestal'
        for p in ((3, 9), (4, 8), (4, 9), (5, 8)):
            piezas[p] = 'ala'
        for p in ((8, 8), (9, 7), (10, 7), (10, 8)):
            piezas[p] = 'oro'
    for (x, y) in borde4(set(piezas)):
        if 0 <= x < W and 0 <= y < H:
            q[x, y] = CONTORNO
    for (x, y), k in piezas.items():
        luz = (x, y - 1) not in piezas or (x - 1, y) not in piezas
        sombra = (x + 1, y) not in piezas or (x, y + 1) not in piezas
        if k == 'oro':
            c = ORO[4] if luz else ORO[2] if sombra else ORO[3]
        elif k == 'pedestal':
            c = ORO[3] if y == 13 else MARMOL[1]
        elif k == 'ala':
            c = MARMOL[4] if luz else MARMOL[2] if (x + y) % 3 == 0 else MARMOL[3]
        else:
            c = MARMOL[4] if luz else MARMOL[1] if sombra else MARMOL[3] if x < 7 else MARMOL[2]
        q[x, y] = c
    if roto:
        for (x, y) in ((5, 11), (8, 11), (6, 12), (10, 12)):
            q[x, y] = CONTORNO                            # las juntas de los cascotes
    else:
        q[8, 3] = MARMOL[1]                               # el ojo
    return im


def losa(q, x0, x1, y0, alto):
    """La losa oscura de los medidores de debajo, como la del Sello."""
    for y in range(y0, y0 + alto):
        for x in range(x0, x1):
            q[x, y] = CONTORNO if y in (y0, y0 + alto - 1) or x in (x0, x1 - 1) else FONDO


# ---------------------------------------------------------------- la barra montada
def barra(clave, vida, rastro=None, alto=NH):
    """La barra montada como la montaria el HUD del juego."""
    R = rampa(clave)
    im = marco(clave, alto)
    q = im.load()
    lleno = round(190 * vida)
    if rastro and rastro > vida:
        c = RASTRO['furia' if clave == 'furia' else 'fuego']
        for x in range(lleno, round(190 * rastro)):
            for y in range(HY0, HY1):
                q[HX0 + x, y] = c
    rel = relleno(clave)
    x = 0
    while x < lleno:
        w = min(64, lleno - x)
        im.alpha_composite(rel.crop((0, 0, w, 9)), (HX0 + x, HY0))
        x += w
    if lleno >= 3:
        # el frente encendido, con una chispa que salta por encima del canto
        for y in range(HY0, HY1):
            q[HX0 + lleno - 1, y] = R[5]
            q[HX0 + lleno - 2, y] = R[5] if y < HY0 + 5 else R[4]
            q[HX0 + lleno - 3, y] = R[4] if y < HY0 + 3 else q[HX0 + lleno - 3, y]
        q[HX0 + lleno - 1, HY0 - 1] = R[4]
        q[HX0 + lleno - 2, HY0 - 2] = R[3]
    for corte in (0.75, 0.5, 0.25):
        ex = HX0 + round(190 * corte) - 3
        pasado = vida < corte
        pal = dict(PAL_MUESCA, L=R[4], W=R[5])
        pintar(im, RAYO_ROTO if pasado else RAYO, pal, ex, HY0 - 5)
    im.alpha_composite(nucleo(clave), (EC[0] - NUC // 2, EC[1] - NUC // 2))
    im.alpha_composite(NOMBRE, (NOMBRE_X, 9))
    if clave == 'furia':
        rot = palabra('FURIA', gris, ancho=64, derecha=True)
    else:
        rot = palabra('FASE ' + ['I', 'II', 'III', 'IV'][clave - 1], gris, ancho=64, derecha=True)
    im.alpha_composite(tenir(rot, COLOR_ROTULO[clave]), (ROTULO_X, 8))
    return im


# ---------------------------------------------------------------- las vistas especiales
ORBE = [hexc(c) for c in ('d06a10', 'ffa63a', 'ffd77a', 'fff6d8')]


def sol_pequeno(q, cx, cy, cs, radio=3.2, largo=5.4):
    """Un sol pequeno: disco y ocho rayos, con su contorno."""
    oscuro, medio, claro, nucleo_c = cs
    pts = set()
    n = int(largo) + 1
    for dy in range(-n, n + 1):
        for dx in range(-n, n + 1):
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            da = abs((ang + math.pi / 8) % (math.pi / 4) - math.pi / 8)
            if d <= radio or (d <= largo and d * math.sin(da) < 0.55 * (1.6 - d / largo)):
                pts.add((cx + dx, cy + dy))
    for (x, y) in borde4(pts):
        q[x, y] = CONTORNO
    for (x, y) in pts:
        d = math.hypot(x - cx, y - cy)
        luz = (cx - x) + (cy - y)
        q[x, y] = (nucleo_c if d < radio * 0.4 else claro if d < radio * 0.75 or luz > 1 else medio) if d <= radio else claro
    return pts


def vista_fuentes(estados=('rota', 'rajada', 'entera'), carga=0.7):
    clave = 3
    im = barra(clave, 0.38, 0.44, ALTO_ESPECIAL)
    q = im.load()
    pal = dict(PAL_MUESCA, r=ORBE[0], v=ORBE[1], V=ORBE[2], W=ORBE[3], s=ORBE[2], L=ORBE[2], h=ORO[1], g=ORO[2],
               **{'0': ORO[0], '1': BASALTO[0], '2': BASALTO[1], '3': BASALTO[2], '4': BASALTO[3], '5': BASALTO[4]})
    for k, e in enumerate(estados):
        dib = {'entera': FUENTE, 'rajada': FUENTE_RAJADA, 'rota': FUENTE_ROTA}[e]
        pintar(im, dib, pal, HX0 + k * 13, 36)
    # la carga del sol: se llena hacia la explosion; del oro al rojo segun se
    # acerca al final, y el ultimo tramo, aun vacio, rayado en rojo hondo
    lx0, lx1, ly = HX0 + 44, HX1 - 12, 42
    losa(q, lx0, lx1, ly, 7)
    ancho = lx1 - lx0 - 2
    n = round(ancho * carga)
    for i in range(ancho):
        t = i / ancho
        if t >= 0.8 and i >= n and i % 3 == 0:
            for y in range(ly + 1, ly + 6):
                q[lx0 + 1 + i, y] = hexc('3a0c0a')
        if i < n:
            if t < 0.4:
                cs = (ORO[4], ORO[3], ORO[2])
            elif t < 0.62:
                cs = (hexc('ffc070'), hexc('ff9a2e'), hexc('d86a14'))
            elif t < 0.8:
                cs = (hexc('ff9a6a'), hexc('ff5a2a'), hexc('c02a10'))
            else:
                cs = (hexc('ff8a84'), ROJO, hexc('a8100c'))
            for y in range(ly + 1, ly + 6):
                r = y - ly - 1
                q[lx0 + 1 + i, y] = cs[0] if r == 0 else cs[1] if r < 4 else cs[2]
    if n > 1:
        for y in range(ly + 1, ly + 6):
            q[lx0 + n, y] = hexc('fff4e0')
    # al final de la losa, el estallido que viene
    sol_pequeno(q, lx1 + 5, ly + 3, (hexc('3a0408'), ROJO, hexc('ffb08a'), hexc('fff0e0')))
    return im


def llama_pequena(q, cx, base, R):
    poly = lengua(cx, base, 3, 11, 0.12)
    pts = {(x, y) for y in range(base - 12, base + 1) for x in range(cx - 6, cx + 7) if dentro(poly, x + 0.5, y + 0.5)}

    def pon(x, y, c):
        q[x, y] = c
    fuego(pon, pts, R)


def vista_trompetas(rotos=(0,), melodia=0.6):
    clave = 2
    im = barra(clave, 0.62, None, ALTO_ESPECIAL)
    q = im.load()
    for k in range(4):
        im.alpha_composite(angel(k in rotos), (HX0 - 2 + k * 15, 36))
    # la melodia: un pentagrama corto; las notas se encienden de izquierda a
    # derecha y las ultimas se ponen rojas (si se completa, Furia)
    lx0, lx1, ly = HX0 + 62, HX1 - 12, 38
    losa(q, lx0, lx1, ly, 13)
    for j in range(5):
        for x in range(lx0 + 2, lx1 - 2):
            q[x, ly + 2 + 2 * j] = ACERO[2]
    alturas = [7, 5, 6, 4, 3, 5, 2, 4, 6, 3, 1, 2, 4, 3, 5, 1]
    notas = len(alturas)
    paso = (lx1 - lx0 - 12) / notas
    for i, a in enumerate(alturas):
        t = (i + 1) / notas
        x = round(lx0 + 8 + i * paso)
        y = ly + 2 + a          # la cabeza, en linea o en espacio
        if t <= melodia:
            cab = ORO[4] if t < 0.75 else hexc('ff8a7a')
            pal_ = ORO[3] if t < 0.75 else ROJO
        elif t > 0.75:
            cab, pal_ = hexc('5a1a16'), hexc('4a1412')
        else:
            cab, pal_ = ACERO[4], ACERO[3]
        q[x, y] = cab
        q[x + 1, y] = pal_
        q[x, y + 1] = pal_
        q[x + 1, y + 1] = pal_
        for s in range(1, 5):
            if y - s > ly:
                q[x + 1, y - s] = pal_
    # la clave al principio (un garabato de oro) y la llama azul al final
    for (dx, dy) in ((0, 1), (1, 0), (2, 1), (2, 2), (1, 3), (0, 4), (0, 5), (1, 6), (2, 6), (2, 7), (1, 8),
                     (1, 9), (0, 10), (1, 5), (1, 7)):
        q[lx0 + 3 + dx, ly + 1 + dy] = ORO[3]
    llama_pequena(q, lx1 + 5, ly + 10, rampa('furia'))
    return im


def sol_cautivo(q, cx, cy):
    """El sol de la ofrenda (19x19) con el cautivo dentro: la cabeza cuadrada de
    un jugador a contraluz, con los ojos claros para que se lea como cara. El
    sol tiene que asomar alrededor: con un disco mas pequeno parecia un marco."""
    sol_pequeno(q, cx, cy, (ORO[1], ORO[3], ORO[4], hexc('fff4d0')), radio=6.3, largo=9.4)
    for dy in range(-3, 3):
        for dx in range(-3, 3):
            borde = dx in (-3, 2) or dy in (-3, 2)
            q[cx + dx, cy + dy] = CONTORNO if borde else ACERO[1]
    for dx in range(-2, 2):
        q[cx + dx, cy - 2] = ACERO[3]                     # el pelo, un poco mas claro
    q[cx - 2, cy] = MARMOL[3]                             # los ojos
    q[cx + 1, cy] = MARMOL[3]


def vista_ofrenda(liberacion=0.45):
    clave = 1
    im = barra(clave, 0.8, None, ALTO_ESPECIAL)
    q = im.load()
    sol_cautivo(q, HX0 + 10, 45)
    lx0, lx1, ly = HX0 + 25, HX1 - 2, 42
    losa(q, lx0, lx1, ly, 7)
    n = round((lx1 - lx0 - 2) * liberacion)
    for x in range(lx0 + 1, lx0 + 1 + n):
        for y in range(ly + 1, ly + 6):
            r = y - ly - 1
            q[x, y] = VERDE[4] if r == 0 else VERDE[3] if r < 4 else VERDE[2]
    if n:
        for y in range(ly + 1, ly + 6):
            q[lx0 + n, y] = VERDE[5]
    return im


def cuerno(q, ox, oy):
    """El cuerno de guerra carmesi (16x15). Lo que lo separa de una guindilla
    (las dos primeras pruebas) es la curva en media luna y la campana: el
    cuerpo se abre de golpe al final y se ve la boca oscura con su filo de oro.
    La boquilla de oro arriba a la izquierda, dos abrazaderas de oro y el grito
    saliendo por encima de la campana."""
    W, H, Y0 = 16, 15, 4
    P0, P1, P2 = (1.5, Y0 + 2.5), (7.0, Y0 + 10.0), (13.0, Y0 + 5.0)
    curva = []
    for i in range(121):
        t = i / 120
        curva.append((t, (1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0],
                      (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1], 0.8 + 3.0 * t ** 1.8))
    pts = {}
    for y in range(H):
        for x in range(W):
            cerca = [(math.hypot(x + 0.5 - bx, y + 0.5 - by), t) for (t, bx, by, r) in curva
                     if math.hypot(x + 0.5 - bx, y + 0.5 - by) <= r]
            if cerca:
                pts[(x, y)] = min(cerca)[1]           # el punto de la curva mas cercano
    # la boca: una elipse perpendicular a la curva en la campana
    tx, ty = P2[0] - P1[0], P2[1] - P1[1]
    n = math.hypot(tx, ty)
    tx, ty = tx / n, ty / n
    boca, filo = set(), set()
    for y in range(H):
        for x in range(W):
            vx, vy = x + 0.5 - (P2[0] + tx * 0.6), y + 0.5 - (P2[1] + ty * 0.6)
            a = vx * tx + vy * ty          # a lo largo
            b = -vx * ty + vy * tx         # a lo ancho
            e = (a / 1.2) ** 2 + (b / 2.8) ** 2
            if e <= 1:
                boca.add((x, y))
            elif e <= 2.2 and a > -1.4:
                filo.add((x, y))
    todo = set(pts) | boca | filo
    for (x, y) in borde4(todo):
        if 0 <= x < W and 0 <= y < H:
            q[ox + x, oy + y] = CONTORNO
    for (x, y), t in pts.items():
        luz = (x, y - 1) not in todo
        sombra = (x, y + 1) not in todo
        c = CARMESI[4] if luz else CARMESI[1] if sombra else CARMESI[3] if (x, y - 2) not in todo else CARMESI[2]
        if t < 0.08 or 0.36 < t < 0.44 or 0.62 < t < 0.69:
            c = ORO[4] if luz else ORO[1] if sombra else ORO[3]
        q[ox + x, oy + y] = c
    for (x, y) in filo:
        q[ox + x, oy + y] = ORO[4] if (x, y - 1) not in todo or (x + 1, y) not in todo else ORO[3]
    for (x, y) in boca:
        q[ox + x, oy + y] = CARMESI[0]
    # el grito: tres rayitas que salen de la campana hacia arriba
    for (x, y) in ((11, 2), (12, 1), (14, 1), (14, 0), (15, 3)):
        q[ox + x, oy + y] = CARMESI[4]


def vista_grito():
    im = barra(4, 0.15, 0.22)
    q = im.load()
    ancho_fase4 = 43
    cuerno(q, ROTULO_X + 64 - ancho_fase4 - 16, 2)
    return im


# ---------------------------------------------------------------- la quemadura (18x18)
# Tres llamas dibujadas a mano (DISENO 18): la I pequena y naranja, la II mas
# grande y roja con una lengua a cada lado, la III grande y carmesi con una
# calavera en el nucleo. El numero romano, con sus remates, va arriba a la
# derecha, donde la punta de la llama deja sitio. Las rampas van por encima
# de 119 de luminancia (DISENO 4-bis; el carmesi no sube mas sin volverse
# rosa, como pasa con marcado). La calavera es informacion: va honda (DISENO 19).
LLAMAS = {
    1: ["..................",
        "..................",
        "..................",
        "..................",
        "..................",
        ".......#..........",
        ".......##.........",
        "......###.........",
        "......####........",
        ".....#####........",
        "....######.#......",
        "....########......",
        "....########......",
        "....########......",
        ".....######.......",
        "......####........",
        "..................",
        ".................."],
    2: ["..................",
        "..................",
        "..................",
        ".......#..........",
        ".......##.........",
        "......###.........",
        "...#..####........",
        "...#.#####........",
        "..##.######.#.....",
        "..##########.#....",
        "..###########.....",
        "..############....",
        "..############....",
        "..############....",
        "...##########.....",
        "....########......",
        "......####........",
        ".................."],
    3: ["..................",
        ".......#..........",
        ".......##.........",
        "..#...###.........",
        "..##..###.........",
        "..##.#####........",
        ".###.######..#....",
        ".##########..##...",
        ".###########.##...",
        "..#############...",
        "..#############...",
        ".###############..",
        ".###############..",
        ".###############..",
        "..#############...",
        "...###########....",
        ".....#######......",
        ".................."],
}
RAMPAS_QUEMADURA = {
    1: ('ff8a2e', 'ffa646', 'ffc466', 'ffe09a', 'fff6dc'),
    2: ('ff6a3a', 'ff8a4a', 'ffae5e', 'ffd690', 'fff2d6'),
    3: ('ff3a4e', 'ff5a62', 'ff8078', 'ffbcae', 'fff0e8'),
}
ROMANOS = {1: ["###", ".#.", ".#.", ".#.", "###"],
           2: ["#####", ".#.#.", ".#.#.", ".#.#.", "#####"],
           3: ["#######", ".#.#.#.", ".#.#.#.", ".#.#.#.", "#######"]}
MOTAS_QUEMADURA = {1: [(4, 7, 1), (11, 13, 0)], 2: [(1, 4, 1), (14, 13, 0), (5, 2, 0)],
                   3: [(1, 1, 1), (15, 8, 0), (16, 15, 1), (4, 0, 0)]}


def quemadura(grado):
    """Una llama que crece y se oscurece hacia el carmesi; marcas I, II, III."""
    im = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
    q = im.load()
    R = [hexc(c) for c in RAMPAS_QUEMADURA[grado]]
    pts = {(x, y) for y, fila in enumerate(LLAMAS[grado]) for x, c in enumerate(fila) if c == '#'}
    d = capas(pts)
    abajo = max(y for _, y in pts)
    for (x, y), k in d.items():
        # el nucleo caliente va abajo, donde la llama es ancha (DISENO 6)
        k = min(4, k + (1 if abajo - y <= 6 else 0))
        q[x, y] = R[k]
    for (x, y, k) in MOTAS_QUEMADURA[grado]:
        q[x, y] = R[k]
    if grado == 3:
        # la calavera en el nucleo: cuencas, nariz y dientes, en carmesi hondo
        hondo = hexc('7a0a1c')
        for (x, y) in ((5, 10), (6, 10), (5, 11), (6, 11), (10, 10), (11, 10), (10, 11), (11, 11),
                       (8, 12), (6, 14), (8, 14), (10, 14), (7, 13), (9, 13)):
            q[x, y] = hondo
    rom = ROMANOS[grado]
    ox = 17 - len(rom[0])
    for fy, fila in enumerate(rom):
        for fx, c in enumerate(fila):
            if c == '#':
                q[ox + fx, fy] = hexc('fff3dc')
    return im


# ---------------------------------------------------------------- la pantalla de la ofrenda
# Se dibuja a 427x240 pixeles de interfaz (la pantalla a escala de GUI 2) y se
# saca a x2. Fondo transparente: va encima del juego.
QW, QH = 427, 240
# Las teclas: de acero quemado con el filo de oro y la letra de oro, como la
# barra. La de ahora, de oro entero y encendida; las hechas, grises con su
# marca verde; la fallada, carmesi y rajada.
ESTILOS_TECLA = {
    # contorno, brillo, cara, sombra, labio, labio hondo, letra, canto de la letra
    'actual': (hexc('3a2008'), hexc('fff2c0'), ORO[4], ORO[3], ORO[2], ORO[1], hexc('3a2008'), hexc('fff2c0')),
    'siguiente': (CONTORNO, ACERO[4], ACERO[3], ACERO[2], ACERO[1], ACERO[0], ORO[4], CONTORNO),
    'hecha': (hexc('1a1918'), hexc('6a6662'), hexc('54504c'), hexc('46423f'), hexc('302e2c'), hexc('242220'),
              hexc('8a8580'), hexc('1a1918')),
    'rota': (CARMESI[0], CARMESI[4], CARMESI[2], CARMESI[1], hexc('4a0610'), CARMESI[0], CARMESI[5], CARMESI[0]),
}
# ancho, alto, labio y escala de la letra
TAMANOS = {'actual': (28, 28, 4, 2), 'siguiente': (18, 18, 3, 1), 'hecha': (14, 14, 2, 1), 'rota': (28, 28, 4, 2)}


def ancho_tecla(letra, estilo):
    w, h, labio, esc = TAMANOS[estilo]
    return w if letra != ' ' else round(w * 1.9)


def tecla(q, x0, y0, letra, estilo, apagar=0.0):
    """Una tecla con su cara, su labio (el canto de abajo, que le da cuerpo) y
    la letra. ' ' es el ESPACIO, mas ancha y con su simbolo."""
    w, h, labio, esc = TAMANOS[estilo]
    w = ancho_tecla(letra, estilo)
    cs = [mezclar(c, OSCURO, apagar) for c in ESTILOS_TECLA[estilo]]
    contorno, brillo, cara, sombra, lab, lab2, c_letra, c_borde = cs
    for y in range(h):
        for x in range(w):
            if (x in (0, w - 1)) and (y in (0, h - 1)):
                continue                                              # esquinas romas
            if x in (0, w - 1) or y in (0, h - 1):
                c = contorno
            elif y >= h - 1 - labio:
                c = lab2 if y == h - 2 or x == w - 2 else lab
            elif y == 1 or x == 1:
                c = brillo
            elif x == w - 2 or y == h - 2 - labio:
                c = sombra
            else:
                c = cara
            q[x0 + x, y0 + y] = c
    if estilo == 'siguiente':
        for x in range(2, w - 2):
            q[x0 + x, y0 + 1] = mezclar(ORO[2], OSCURO, apagar)      # el filo de oro
    # la letra (o el simbolo del espacio), centrada en la cara
    cara_h = h - 2 - labio
    if letra == ' ':
        # el simbolo del espacio: una barra con los extremos levantados
        sw = w - 10 * esc
        alto_s = 2 * esc
        pts = set()
        for t in range(esc):
            for x in range(sw):
                pts.add((x, alto_s + t))
            for y in range(alto_s + esc):
                pts.add((t, y))
                pts.add((sw - 1 - t, y))
        lx = x0 + (w - sw) // 2
        ly = y0 + 1 + (cara_h - (alto_s + esc)) // 2
    else:
        g = GLIFOS[letra]
        pts = {(fx * esc + sx, fy * esc + sy) for fy, fila in enumerate(g) for fx, c in enumerate(fila) if c == '#'
               for sx in range(esc) for sy in range(esc)}
        gw, gh = len(g[0]) * esc, len(g) * esc
        lx = x0 + (w - gw) // 2
        ly = y0 + 1 + (cara_h - gh) // 2
    for (x, y) in pts:
        if (x, y + 1) not in pts:
            q[lx + x, ly + y + 1] = c_borde                           # el canto de la letra
    for (x, y) in pts:
        q[lx + x, ly + y] = c_letra
    return w, h


def halo(q, x0, y0, w, h, color, radio=4):
    """El brillo de la tecla de ahora: un halo escalonado (no un degradado) y
    rayitos de sol."""
    for y in range(y0 - radio - 3, y0 + h + radio + 3):
        for x in range(x0 - radio - 3, x0 + w + radio + 3):
            dx = max(x0 - x, 0, x - (x0 + w - 1))
            dy = max(y0 - y, 0, y - (y0 + h - 1))
            d = math.hypot(dx, dy)
            if 0 < d <= radio:
                q[x, y] = alfa(color, (180, 115, 65, 30)[min(3, int(d - 0.01))])
    cx, cy = x0 + w // 2, y0 + h // 2
    for (dx, dy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        for k in range(3):
            x = cx + dx * (w // 2 + radio + 1 + k) - (1 if dx > 0 else 0)
            y = cy + dy * (h // 2 + radio + 1 + k) - (1 if dy > 0 else 0)
            q[x, y] = alfa(color, (230, 150, 70)[k])
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        for k in range(2):
            x = (x0 - 2 - k if sx < 0 else x0 + w + 1 + k)
            y = (y0 - 2 - k if sy < 0 else y0 + h + 1 + k)
            q[x, y] = alfa(color, (200, 110)[k])


def marca_verde(q, x, y):
    """La marca de hecho: una palomita verde con su contorno."""
    pts = {(0, 2), (1, 3), (2, 4), (3, 3), (4, 2), (5, 1), (6, 0), (1, 2), (2, 3), (3, 2), (4, 1), (5, 0)}
    for (px_, py) in borde4(pts):
        q[x + px_, y + py] = VERDE[0]
    for (px_, py) in pts:
        q[x + px_, y + py] = VERDE[4] if py < 2 or px_ < 2 else VERDE[3]


def grietas_tecla(q, x0, y0, w, h):
    """La tecla fallada: rajada en dos, una esquina saltada y esquirlas."""
    hondo = CARMESI[0]
    for (x, y) in ((13, 1), (13, 2), (12, 3), (12, 4), (13, 5), (14, 6), (14, 7), (13, 8), (12, 9), (12, 10),
                   (13, 11), (14, 12), (14, 13), (15, 14), (15, 15), (14, 16), (14, 17), (13, 18), (13, 19),
                   (13, 20), (12, 21), (12, 22), (11, 23), (11, 24), (12, 25), (12, 26),
                   (14, 9), (15, 9), (16, 8), (17, 8), (18, 7), (11, 15), (10, 15), (9, 16), (8, 16), (7, 17)):
        if 0 < x < w - 1 and 0 < y < h - 1:
            q[x0 + x, y0 + y] = hondo
    for (x, y) in ((x, y) for y in range(0, 5) for x in range(w - 6, w) if x - (w - 6) > y):
        q[x0 + x, y0 + y] = (0, 0, 0, 0)                               # la esquina saltada
    for (x, y) in ((w - 6, 1), (w - 5, 1), (w - 4, 2), (w - 3, 2), (w - 2, 3), (w - 1, 4)):
        q[x0 + x, y0 + y] = CARMESI[0]
    for (x, y, c) in ((w + 2, -2, CARMESI[3]), (w + 3, -3, CARMESI[2]), (w + 5, 1, CARMESI[4]), (w + 1, 3, CARMESI[2]),
                      (-3, 6, CARMESI[3]), (-4, 7, CARMESI[2])):
        q[x0 + x, y0 + y] = c


def reloj(q, x, y):
    """Un reloj de arena de oro (5x7) para la losa del tiempo."""
    dib = ["ooooo", "oYYGo", ".oGo.", "..o..", ".oGo.", "oGGgo", "ooooo"]
    pal = {'o': ORO[0], 'Y': ORO[4], 'G': ORO[3], 'g': ORO[2]}
    for fy, fila in enumerate(dib):
        for fx, c in enumerate(fila):
            if c != '.':
                q[x + fx, y + fy] = pal[c]


def qte(fallo=False):
    im = Image.new('RGBA', (QW, QH), (0, 0, 0, 0))
    q = im.load()
    cx = QW // 2
    # el titulo
    titulo = palabra('OFRENDA AL SOL', oro_claro)
    im.alpha_composite(titulo, (cx - titulo.width // 2, 106))
    if fallo:
        rotulo = palabra('\u00a1FALLASTE!', de_rampa([CARMESI[5], CARMESI[4], CARMESI[4], CARMESI[3], CARMESI[3],
                                                      CARMESI[3], CARMESI[2]]), borde=CARMESI[0])
        im.alpha_composite(rotulo, (cx - rotulo.width // 2, 119))
    else:
        sub = palabra('SIGUE LAS TECLAS', de_rampa([hexc(c) for c in ('f0e4cc', 'e0d2b8', 'd0c0a4', 'c0ae92', 'b09e82')]),
                      glifos=MINI)
        im.alpha_composite(sub, (cx - sub.width // 2, 120))
    # las teclas: las hechas a la izquierda, la de ahora en el centro, las
    # cuatro siguientes a la derecha, cada una un poco mas apagada
    hechas, actual, siguientes = ['W', 'D'], 'A', ['S', ' ', 'D', 'W']
    yc = 148
    estilo_actual = 'rota' if fallo else 'actual'
    wa, ha = ancho_tecla(actual, estilo_actual), TAMANOS[estilo_actual][1]
    xa = cx - wa // 2
    ya = yc - ha // 2
    if not fallo:
        halo(q, xa, ya, wa, ha, ORO[4])
    tecla(q, xa, ya, actual, estilo_actual)
    if fallo:
        grietas_tecla(q, xa, ya, wa, ha)
    x = xa + wa + 9
    for i, l in enumerate(siguientes):
        w, h = ancho_tecla(l, 'siguiente'), TAMANOS['siguiente'][1]
        tecla(q, x, yc - h // 2 + 2, l, 'siguiente', apagar=(0.0, 0.22, 0.4, 0.55)[i])
        x += w + 4
    x = xa - 9
    for l in reversed(hechas):
        w, h = ancho_tecla(l, 'hecha'), TAMANOS['hecha'][1]
        x -= w
        tecla(q, x, yc - h // 2 + 4, l, 'hecha')
        marca_verde(q, x + w - 6, yc - h // 2 + 4 + h - 7)
        x -= 4
    # la liberacion: lo que lleva el cautivo; al fallar retrocede (el rastro rojo)
    bx0, bx1, by = cx - 80, cx + 80, 176
    eti = palabra('LIBERACION', de_rampa([VERDE[5], VERDE[4], VERDE[4], VERDE[3], VERDE[3]]), glifos=MINI)
    im.alpha_composite(eti, (bx0 - 1, by - 9))
    losa(q, bx0, bx1, by, 7)
    ancho = bx1 - bx0 - 2
    lib, antes = (0.25, 0.4) if fallo else (0.4, None)
    n = round(ancho * lib)
    if antes:
        for x in range(n, round(ancho * antes)):
            for y in range(by + 1, by + 6):
                q[bx0 + 1 + x, y] = alfa(CARMESI[3], 0xD8)
    for x in range(n):
        for y in range(by + 1, by + 6):
            r = y - by - 1
            q[bx0 + 1 + x, y] = VERDE[4] if r == 0 else VERDE[3] if r < 4 else VERDE[2]
    for y in range(by + 1, by + 6):
        q[bx0 + n, y] = VERDE[5]
    # el tiempo: una losa fina que se vacia hacia la izquierda; el ultimo
    # cuarto (el de la izquierda) va en rojo
    ty = by + 11
    reloj(q, bx0 - 8, ty - 1)
    losa(q, bx0, bx1, ty, 5)
    t = 0.18 if fallo else 0.55
    n = round(ancho * t)
    for x in range(ancho):
        rojo = x < ancho * 0.25
        if x < n:
            for y in range(ty + 1, ty + 4):
                q[bx0 + 1 + x, y] = (ROJO if y > ty + 1 else hexc('ff9a84')) if rojo else (ORO[3] if y > ty + 1 else ORO[4])
        elif rojo and x % 3 == 0:
            for y in range(ty + 1, ty + 4):
                q[bx0 + 1 + x, y] = hexc('3a0c0a')
    return im


# ---------------------------------------------------------------- salida
K = 4
ESTADOS = [
    ('fase1', lambda: barra(1, 0.85, 0.91)),
    ('fase2', lambda: barra(2, 0.62, 0.69)),
    ('fase3', lambda: barra(3, 0.38, 0.45)),
    ('fase4', lambda: barra(4, 0.15, 0.22)),
    ('furia', lambda: barra('furia', 0.3, 0.36)),
    ('fuentes', vista_fuentes),
    ('trompetas', vista_trompetas),
    ('ofrenda', vista_ofrenda),
    ('grito', vista_grito),
]
for nombre, hacer in ESTADOS:
    im = hacer()
    im.save(os.path.join(RAW, f'barra_{nombre}.png'))
    im.resize((im.width * K, im.height * K), Image.NEAREST).save(os.path.join(SALIDA, f'barra_{nombre}.png'))

# La quemadura: los tres iconos sobre una pizarra oscura como el marco de los
# efectos, a x6
PIZARRA = (0x2a, 0x2a, 0x2e, 255)
hoja = Image.new('RGBA', (4 + 3 * 22, 26), PIZARRA)
for g in (1, 2, 3):
    ic = quemadura(g)
    ic.save(os.path.join(RAW, f'quemadura_{g}.png'))
    hoja.alpha_composite(ic, (4 + (g - 1) * 22, 4))
hoja.resize((hoja.width * 6, hoja.height * 6), Image.NEAREST).save(os.path.join(SALIDA, 'quemadura.png'))

# La pantalla de la ofrenda, normal y fallada, a x2 (854x480)
for nombre, fallo in (('qte', False), ('qte_fallo', True)):
    im = qte(fallo)
    im.save(os.path.join(RAW, f'{nombre}.png'))
    im.resize((QW * 2, QH * 2), Image.NEAREST).save(os.path.join(SALIDA, f'{nombre}.png'))
print('ok', SALIDA)

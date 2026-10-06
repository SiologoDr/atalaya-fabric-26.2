"""
Las piezas del HUD de Novilis, el Caballero Solar, para el juego: su barra de
jefe (NovilisBarraHud), la pantalla de la Ofrenda al Sol (OfrendaHud) y los
iconos de la Quemadura (QuemaduraHud y el efecto).

El dibujo es el de la propuesta aprobada (fuego_hud_propuesta.py), copiado y
partido en las piezas que el HUD monta en cada fotograma, como hace
rajang_remake_hud.py --juego. Lo que la propuesta no tenia y aqui se anade:
  - la barra del liberado (oro en calma: sin grietas de lava, la cresta baja);
  - los pasos intermedios de las fuentes (tres grados de rajado) y de los
    angeles (dos), para que cada golpe se note;
  - las 26 letras (la Ofrenda ya no pide WASD y espacio, sino letras A-Z);
  - el rotulo de acierto, \u00a1LIBRE!;
  - el icono del efecto (textures/mob_effect/quemadura.png).

Uso: python novilis_hud.py <raiz del proyecto> [<carpeta de vista previa>]

Escribe en textures/gui (todas con el prefijo novilis_):
  barra_marco_N.png        el marco de cada fase, la Furia y el liberado (240x44)
  barra_relleno_N.png      el fuego de cada uno, con el color dentro (64x9)
  barra_nucleo_N.png       el yelmo ante el sol de cada uno (24x24)
  barra_rayo_N.png         la muesca entera, del color de cada uno (7x9)
  barra_rayo_roto.png      la muesca ya pasada (7x9)
  barra_nombre.png         NOVILIS (46x10)
  barra_fase_1..4.png, barra_furia.png, barra_libre.png
                           los rotulos, en gris para tenirlos (64x10)
  barra_cuerno.png         el cuerno del Grito de guerra (16x15)
  barra_fuente*.png        la fuente solar: entera, rajada_1..3 y rota (11x18)
  barra_carga_losa.png, barra_carga.png, barra_estallido.png
                           la carga del sol (134x7, 132x5) y el estallido (13x13)
  barra_estatua*.png       el angel: entero, rajada_1..2 y rota (14x16)
  barra_melodia.png, barra_melodia_luz.png
                           el pentagrama apagado y encendido (116x13)
  barra_llama_azul.png     la Furia que espera al final de la melodia (13x13)
  barra_ofrenda_sol.png, barra_cautivo.png
                           el sol de la ofrenda (21x21) y la cabeza (6x6)
  barra_liberacion_losa.png, barra_liberacion.png
                           la liberacion que ven los demas (163x7, 161x5)
  qte_*.png                la pantalla de la ofrenda (ver mas abajo)
  quemadura_1..3.png       la quemadura junto a los corazones (18x18)

Con la carpeta de vista previa monta ademas, con esas mismas piezas y en las
posiciones del Java, las barras y la pantalla de la ofrenda, a x4.
"""
from PIL import Image
from collections import deque
import math, os, random, sys

RAIZ = sys.argv[1]
VISTA = sys.argv[2] if len(sys.argv) > 2 else None
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
EFECTO = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/mob_effect')
if VISTA:
    os.makedirs(VISTA, exist_ok=True)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mezclar(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def alfa(c, a):
    return (c[0], c[1], c[2], a)


def redondo(v):
    """Redondeo a la mitad hacia arriba, como Math.round del Java (el round de
    Python va al par y moveria un pixel las cosas que el HUD coloca)."""
    return int(math.floor(v + 0.5))


# ---------------------------------------------------------------- paletas
# Las de la propuesta. Acero quemado y oro; el contorno no es negro: es el
# tono mas hondo del acero, y el fondo del hueco tira al pardo.
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
# fase). El nucleo nunca es blanco puro: tira al color. El liberado: oro
# palido y en calma, la luz del sol sin el fuego.
RAMPAS = {
    1: ('2a0c04', '6a1e06', 'b84a0c', 'ff8a1e', 'ffc070', 'fff0d0'),
    2: ('2e1404', '7a3a08', 'c87810', 'ffc23a', 'ffe48a', 'fffae0'),
    3: ('3a1c06', '8a5014', 'd8a038', 'fff0b0', 'fffadc', 'fffff2'),
    4: ('2c0408', '6e0a16', 'b8142a', 'ff2a3a', 'ff9a84', 'ffe4d8'),
    'furia': ('041828', '0a3c62', '1a78b8', '5ad8ff', 'b4f2ff', 'f0fdff'),
    'libre': ('4a3410', '9a7428', 'd8b45a', 'f8dc8c', 'fff2c8', 'fffcf0'),
}
CLAVES = (1, 2, 3, 4, 'furia', 'libre')


def rampa(clave):
    return [hexc(c) for c in RAMPAS[clave]]


def nivel_de(clave):
    return 4 if clave == 'furia' else 1 if clave == 'libre' else clave


NW, NH = 240, 44
HX0, HX1, HY0, HY1 = 40, 230, 22, 31
EC = (19, 26)
ER = 15.5
NUC = 24


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


def dibujo(filas, paleta):
    im = Image.new('RGBA', (len(filas[0]), len(filas)), (0, 0, 0, 0))
    pintar(im, filas, paleta)
    return im


def tenir(im, rgb, a=255):
    """Lo que hace el color del blit: multiplica (tambien el alfa)."""
    im = im.copy()
    q = im.load()
    r, g, b = (rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255
    for y in range(im.height):
        for x in range(im.width):
            c = q[x, y]
            q[x, y] = (c[0] * r // 255, c[1] * g // 255, c[2] * b // 255, c[3] * a // 255)
    return im


def guardar(im, nombre, carpeta=GUI):
    im.save(os.path.join(carpeta, nombre + '.png'))
    return im


# ---------------------------------------------------------------- letras en pixel
# Las de rajang_hud.py (relleno, contorno de un pixel y sombra) y la propuesta,
# con las 26 que pide ahora la Ofrenda: H, J, K, M, P, Q, X, Y y Z son nuevas,
# del mismo trazo (dos pixeles de grueso, 6 de ancho; la M y la W, 7). La
# exclamacion de abrir va escrita como \u00a1 para que el fichero siga siendo ASCII.
GLIFOS = {
    'A': [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    'B': ["#####.", "##..##", "##..##", "#####.", "##..##", "##..##", "#####."],
    'C': [".#####", "##....", "##....", "##....", "##....", "##....", ".#####"],
    'D': ["#####.", "##..##", "##..##", "##..##", "##..##", "##..##", "#####."],
    'E': ["######", "##....", "##....", "#####.", "##....", "##....", "######"],
    'F': ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    'G': [".#####", "##....", "##....", "##.###", "##..##", "##..##", ".####."],
    'H': ["##..##", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    'I': ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    'J': ["....##", "....##", "....##", "....##", "##..##", "##..##", ".####."],
    'K': ["##..##", "##.##.", "####..", "###...", "####..", "##.##.", "##..##"],
    'L': ["##....", "##....", "##....", "##....", "##....", "##....", "######"],
    'M': ["##...##", "###.###", "#######", "##.#.##", "##...##", "##...##", "##...##"],
    'N': ["##..##", "###.##", "######", "##.###", "##..##", "##..##", "##..##"],
    'O': [".####.", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    'P': ["#####.", "##..##", "##..##", "#####.", "##....", "##....", "##...."],
    'Q': [".####.", "##..##", "##..##", "##..##", "##.###", ".####.", "....##"],
    'R': ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    'S': [".#####", "##....", "##....", ".####.", "....##", "....##", "#####."],
    'T': ["######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##.."],
    'U': ["##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    'V': ["##..##", "##..##", "##..##", "##..##", ".####.", ".####.", "..##.."],
    'W': ["##...##", "##...##", "##...##", "##.#.##", "#######", "###.###", "##...##"],
    'X': ["##..##", "##..##", ".####.", "..##..", ".####.", "##..##", "##..##"],
    'Y': ["##..##", "##..##", "##..##", ".####.", "..##..", "..##..", "..##.."],
    'Z': ["######", "....##", "...##.", "..##..", ".##...", "##....", "######"],
    '!': ["##", "##", "##", "##", "##", "..", "##"],
    '\u00a1': ["##", "..", "##", "##", "##", "##", "##"],
    ' ': ["..", "..", "..", "..", "..", "..", ".."],
}
LETRAS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
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


def ancho_texto(texto, glifos=GLIFOS):
    """Lo que ocupa el texto de palabra() sin el lienzo fijo (con su contorno)."""
    return sum(len(glifos[ch][0]) + 1 for ch in texto) - 1 + 2


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
# Los rotulos de la derecha (con su ancho de texto: el cuerno del Grito se pone
# justo a su izquierda, sea cual sea).
ROTULOS = {1: 'FASE I', 2: 'FASE II', 3: 'FASE III', 4: 'FASE IV', 'furia': 'FURIA', 'libre': 'LIBERADO'}


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
# El liberado: sin grietas de lava, la cresta baja y sin chispas. En calma.
CUANTAS_GRIETAS = {1: 3, 2: 5, 3: 7, 4: 12, 'furia': 12, 'libre': 0}
ALTO_CRESTA = {1: 0.78, 2: 0.88, 3: 0.95, 4: 1.0, 'furia': 1.0, 'libre': 0.62}


def marco(clave, alto=NH):
    R = rampa(clave)
    nivel = nivel_de(clave)
    libre = clave == 'libre'
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
        if libre:
            h *= 0.7
        for y in range(round(y_top + 1 - h), y_top + 1):
            pts.add((x, y))
    for (cx, semi, h, lean) in LENGUAS:
        # el liberado: las lenguas apenas se inclinan, ya no las empuja nada
        poly = lengua(cx, y_top + 1, semi, h * f, lean * (0.45 if libre else 1.0))
        pts |= {(x, y) for y in range(0, y_top + 1) for x in range(18, 90) if dentro(poly, x + 0.5, y + 0.5)}
    # una pequena detras del emblema, a la izquierda, que se va hacia fuera
    poly = lengua(7, 18, 3, 11 * f, -0.45 * (0.45 if libre else 1.0))
    pts |= {(x, y) for y in range(0, 18) for x in range(0, 16) if dentro(poly, x + 0.5, y + 0.5)}
    fuego(pon, pts, R, suelo=y_top + 1)
    # chispas sueltas, repartidas sin simetria (el liberado no echa chispas)
    for (x, y, k) in ((50, 3, 4), (63, 6, 3), (69, 10, 4), (42, 1, 3), (3, 4, 3), (58, 13, 3)):
        if not libre and (x, y) not in pts and y < y_top and (f > 0.8 or k == 4):
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


# ---------------------------------------------------------------- las fuentes solares (11x18)
# El orbe del sol (con cuatro destellos, para que no sea una perla) en su copa
# de oro, el capitel, la columna de basalto y la basa de oro. Se raja en tres
# pasos (la grieta deja salir la luz 'L') y al romperse se queda sin orbe, con
# la columna partida y apagada.
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
# 1-3 golpes: una grieta fina en la columna y otra en el orbe; aun echa chispas
FUENTE_RAJADA_1 = ["....ooo....",
                   ".s.oWVVo.s.",
                   "..oWWVvvo..",
                   "s.oWVVovo.s",
                   "..oVVvvro..",
                   "...ovrro...",
                   "..ooooooo..",
                   "..oYYGGgo..",
                   "oYYYYGGGggo",
                   "ohhhhhhhhho",
                   "..o54322o..",
                   "..o54o22o..",
                   "..o54Lo2o..",
                   "..o543o2o..",
                   "..o54322o..",
                   ".oYYYGGggo.",
                   "oYGGGGGggho",
                   "ooooooooooo"]
# 4-6 golpes: la de la propuesta. Rajada de arriba abajo, sin chispas
FUENTE_RAJADA_2 = ["....ooo....",
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
# 7-9 golpes: a punto de caer. Al orbe le falta un trozo, el capitel se parte,
# la columna se abre en dos y por todas las grietas sale la luz
FUENTE_RAJADA_3 = ["....oo.....",
                   "...oWo.o...",
                   "..oWoVo....",
                   "..oVovvo...",
                   "..oVovro...",
                   "...ovro....",
                   "..ooo.ooo..",
                   "..oYoGogo..",
                   "oYYoYGoGggo",
                   "ohhohhohhho",
                   "..o5Lo22o..",
                   "..oL4oL2o..",
                   "..o5oL22o..",
                   "..oL3oL2o..",
                   "..o5oLLo...",
                   ".oYoYoGgo..",
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
ORBE = [hexc(c) for c in ('d06a10', 'ffa63a', 'ffd77a', 'fff6d8')]
PAL_FUENTE = dict(PAL_MUESCA, r=ORBE[0], v=ORBE[1], V=ORBE[2], W=ORBE[3], s=ORBE[2], L=ORBE[2], h=ORO[1], g=ORO[2],
                  **{'0': ORO[0], '1': BASALTO[0], '2': BASALTO[1], '3': BASALTO[2], '4': BASALTO[3],
                     '5': BASALTO[4]})


# ---------------------------------------------------------------- los angeles de las trompetas (14x16)
# Las grietas de los dos pasos intermedios: (x, y) sobre el angel entero, en
# marmol hondo. La 2 lleva las de la 1 y mas, y la trompeta se le tuerce.
GRIETAS_ANGEL = {
    1: ((2, 4), (3, 5), (3, 6), (7, 8), (6, 9), (6, 10), (7, 11)),
    2: ((2, 4), (3, 5), (3, 6), (4, 7), (7, 8), (6, 9), (6, 10), (7, 11), (8, 12), (6, 2), (5, 3),
        (9, 9), (9, 10), (4, 11), (5, 12)),
}


def angel(roto=False, grietas=0):
    """El angel de piedra (14x16), de perfil hacia la derecha: el ala alzada
    detras, la cabeza, la tunica, el pedestal con su filo de oro y la trompeta
    de oro con la campana abierta. Rajado: grietas en el marmol (y en la 2 la
    trompeta torcida). Roto: un monton de cascotes, un trozo de ala y la
    trompeta doblada encima."""
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
        if grietas >= 2:
            # la trompeta, torcida hacia abajo
            trompeta = ((9, 4), (10, 4), (11, 4), (12, 4), (12, 3), (13, 3), (13, 4), (13, 5), (13, 6), (12, 5))
        else:
            trompeta = ((9, 4), (10, 4), (11, 3), (12, 2), (12, 3), (13, 1), (13, 2), (13, 3), (13, 4), (12, 1), (12, 4))
        for p in trompeta:
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
        for (x, y) in GRIETAS_ANGEL.get(grietas, ()):
            if (x, y) in piezas and piezas[(x, y)] != 'oro':
                q[x, y] = MARMOL[0]
    return im


def losa(q, x0, x1, y0, alto):
    """La losa oscura de los medidores de debajo, como la del Sello."""
    for y in range(y0, y0 + alto):
        for x in range(x0, x1):
            q[x, y] = CONTORNO if y in (y0, y0 + alto - 1) or x in (x0, x1 - 1) else FONDO


def lienzo(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return im, im.load()


# ---------------------------------------------------------------- soles, llama y cuerno
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


def llama_pequena(q, cx, base, R):
    poly = lengua(cx, base, 3, 11, 0.12)
    pts = {(x, y) for y in range(base - 12, base + 1) for x in range(cx - 6, cx + 7) if dentro(poly, x + 0.5, y + 0.5)}

    def pon(x, y, c):
        q[x, y] = c
    fuego(pon, pts, R)


def cabeza_cautivo(q, cx, cy):
    """La cabeza cuadrada de un jugador a contraluz, con los ojos claros para
    que se lea como cara (6x6, de cx-3 a cx+2)."""
    for dy in range(-3, 3):
        for dx in range(-3, 3):
            borde = dx in (-3, 2) or dy in (-3, 2)
            q[cx + dx, cy + dy] = CONTORNO if borde else ACERO[1]
    for dx in range(-2, 2):
        q[cx + dx, cy - 2] = ACERO[3]                     # el pelo, un poco mas claro
    q[cx - 2, cy] = MARMOL[3]                             # los ojos
    q[cx + 1, cy] = MARMOL[3]


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


# ---------------------------------------------------------------- las piezas de debajo
# Medidas de las vistas de debajo, relativas al marco (las del Java).
CARGA_X, CARGA_Y, CARGA_ANCHO = HX0 + 44, 42, (HX1 - 12) - (HX0 + 44)        # 84, 42, 134
MELODIA_X, MELODIA_Y, MELODIA_ANCHO, MELODIA_ALTO = HX0 + 62, 38, (HX1 - 12) - (HX0 + 62), 13   # 102, 38, 116
LIBERA_X, LIBERA_Y, LIBERA_ANCHO = HX0 + 25, 42, (HX1 - 2) - (HX0 + 25)      # 65, 42, 163
ALTURAS_NOTAS = [7, 5, 6, 4, 3, 5, 2, 4, 6, 3, 1, 2, 4, 3, 5, 1]
PASO_NOTAS = (MELODIA_ANCHO - 12) / len(ALTURAS_NOTAS)                          # 6.5


def nota_x(i):
    """Donde cae la nota i dentro del pentagrama (el Java la recorta igual)."""
    return 8 + redondo(i * PASO_NOTAS)


def carga_losa():
    """La losa de la carga del sol; el ultimo tramo, rayado en rojo hondo (lo
    tapa el relleno segun se llena)."""
    im, q = lienzo(CARGA_ANCHO, 7)
    losa(q, 0, CARGA_ANCHO, 0, 7)
    ancho = CARGA_ANCHO - 2
    for i in range(ancho):
        if i / ancho >= 0.8 and i % 3 == 0:
            for y in range(1, 6):
                q[1 + i, y] = hexc('3a0c0a')
    return im


def carga_relleno():
    """La carga entera: del oro al rojo segun se acerca la explosion. El HUD la
    recorta por la izquierda."""
    ancho = CARGA_ANCHO - 2
    im, q = lienzo(ancho, 5)
    for i in range(ancho):
        t = i / ancho
        if t < 0.4:
            cs = (ORO[4], ORO[3], ORO[2])
        elif t < 0.62:
            cs = (hexc('ffc070'), hexc('ff9a2e'), hexc('d86a14'))
        elif t < 0.8:
            cs = (hexc('ff9a6a'), hexc('ff5a2a'), hexc('c02a10'))
        else:
            cs = (hexc('ff8a84'), ROJO, hexc('a8100c'))
        for r in range(5):
            q[i, r] = cs[0] if r == 0 else cs[1] if r < 4 else cs[2]
    return im


def estallido():
    im, q = lienzo(13, 13)
    sol_pequeno(q, 6, 6, (hexc('3a0408'), ROJO, hexc('ffb08a'), hexc('fff0e0')))
    return im


def melodia(encendida):
    """El pentagrama corto con sus 16 notas: apagadas o todas encendidas (el HUD
    recorta la encendida hasta la ultima nota que ha sonado). Las de la ultima
    cuarta parte van en rojo: si suenan todas, Furia."""
    im, q = lienzo(MELODIA_ANCHO, MELODIA_ALTO)
    losa(q, 0, MELODIA_ANCHO, 0, MELODIA_ALTO)
    for j in range(5):
        for x in range(2, MELODIA_ANCHO - 2):
            q[x, 2 + 2 * j] = ACERO[2]
    notas = len(ALTURAS_NOTAS)
    for i, a in enumerate(ALTURAS_NOTAS):
        t = (i + 1) / notas
        x = nota_x(i)
        y = 2 + a          # la cabeza, en linea o en espacio
        if encendida:
            cab = ORO[4] if t <= 0.75 else hexc('ff8a7a')
            pal_ = ORO[3] if t <= 0.75 else ROJO
        elif t > 0.75:
            cab, pal_ = hexc('5a1a16'), hexc('4a1412')
        else:
            cab, pal_ = ACERO[4], ACERO[3]
        q[x, y] = cab
        q[x + 1, y] = pal_
        q[x, y + 1] = pal_
        q[x + 1, y + 1] = pal_
        for s in range(1, 5):
            if y - s > 0:
                q[x + 1, y - s] = pal_
    # la clave al principio (un garabato de oro)
    for (dx, dy) in ((0, 1), (1, 0), (2, 1), (2, 2), (1, 3), (0, 4), (0, 5), (1, 6), (2, 6), (2, 7), (1, 8),
                     (1, 9), (0, 10), (1, 5), (1, 7)):
        q[3 + dx, 1 + dy] = ORO[3]
    return im


def llama_azul():
    im, q = lienzo(13, 13)
    llama_pequena(q, 6, 12, rampa('furia'))
    return im


def ofrenda_sol():
    """El sol de la ofrenda (21x21). El cautivo va aparte, encima: el sol tiene
    que asomar alrededor (con un disco mas pequeno parecia un marco)."""
    im, q = lienzo(21, 21)
    sol_pequeno(q, 10, 10, (ORO[1], ORO[3], ORO[4], hexc('fff4d0')), radio=6.3, largo=9.4)
    return im


def cautivo():
    im, q = lienzo(6, 6)
    cabeza_cautivo(q, 3, 3)
    return im


def liberacion_losa(ancho):
    im, q = lienzo(ancho, 7)
    losa(q, 0, ancho, 0, 7)
    return im


def liberacion_relleno(ancho):
    im, q = lienzo(ancho, 5)
    for x in range(ancho):
        for r in range(5):
            q[x, r] = VERDE[4] if r == 0 else VERDE[3] if r < 4 else VERDE[2]
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


# El icono del efecto, en el inventario y arriba a la derecha: la llama de la
# II sin numero (el nivel ya lo escribe el juego), centrada, con la rampa
# subida entera por encima de 153 (DISENO 4-bis: el marco del efecto es casi
# negro). Rojo anaranjado: se separa del oro de la insolacion y del coral de
# marcado (DISENO 4).
RAMPA_EFECTO = ('ff7642', 'ff9452', 'ffb664', 'ffd894', 'fff4dc')
MOTAS_EFECTO = [(2, 4, 1), (15, 12, 0), (6, 2, 0), (14, 4, 1)]


def quemadura_efecto():
    im = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
    q = im.load()
    R = [hexc(c) for c in RAMPA_EFECTO]
    pts = {(x + 1, y) for y, fila in enumerate(LLAMAS[2]) for x, c in enumerate(fila) if c == '#'}
    d = capas(pts)
    abajo = max(y for _, y in pts)
    for (x, y), k in d.items():
        k = min(4, k + (1 if abajo - y <= 6 else 0))
        q[x, y] = R[k]
    for (x, y, k) in MOTAS_EFECTO:
        if (x, y) not in pts:
            q[x, y] = R[k]
    return im


# ---------------------------------------------------------------- la pantalla de la ofrenda
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
# Las celdas del atlas de letras. Con estas anchuras, centrar la celda en la
# tecla deja cada letra donde la dejaba la propuesta (centrada en la cara).
CELDA_GRANDE = (14, 15)      # 7 de ancho x2, 7 de alto x2 y el canto
CELDA_PEQUENA = (8, 8)       # 7 de ancho y uno de aire, 7 de alto y el canto


def tecla_base(estilo):
    """La tecla sin letra: su cara, su brillo y su labio (el canto de abajo,
    que le da cuerpo). Las esquinas, romas."""
    w, h, labio, esc = TAMANOS[estilo]
    contorno, brillo, cara, sombra, lab, lab2, c_letra, c_borde = ESTILOS_TECLA[estilo]
    im, q = lienzo(w, h)
    for y in range(h):
        for x in range(w):
            if (x in (0, w - 1)) and (y in (0, h - 1)):
                continue
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
            q[x, y] = c
    if estilo == 'siguiente':
        for x in range(2, w - 2):
            q[x, 1] = ORO[2]                              # el filo de oro
    return im


def letra_en(q, ox, oy, letra, estilo, celda):
    """La letra de la tecla, centrada en su celda, con el canto debajo."""
    w, h, labio, esc = TAMANOS[estilo]
    c_letra, c_borde = ESTILOS_TECLA[estilo][6:8]
    g = GLIFOS[letra]
    pts = {(fx * esc + sx, fy * esc + sy) for fy, fila in enumerate(g) for fx, c in enumerate(fila) if c == '#'
           for sx in range(esc) for sy in range(esc)}
    lx = ox + (celda[0] - len(g[0]) * esc) // 2
    for (x, y) in pts:
        if (x, y + 1) not in pts:
            q[lx + x, oy + y + 1] = c_borde                # el canto de la letra
    for (x, y) in pts:
        q[lx + x, oy + y] = c_letra


def atlas_letras(estilos, celda):
    """Las 26 letras en fila, una fila por estilo."""
    im, q = lienzo(celda[0] * len(LETRAS), celda[1] * len(estilos))
    for fila, estilo in enumerate(estilos):
        for i, letra in enumerate(LETRAS):
            letra_en(q, i * celda[0], fila * celda[1], letra, estilo, celda)
    return im


def celda_de(estilo):
    return CELDA_GRANDE if TAMANOS[estilo][3] == 2 else CELDA_PEQUENA


def sitio_letra(estilo):
    """Donde va la celda de la letra dentro de la tecla (lo usa el Java)."""
    w, h, labio, esc = TAMANOS[estilo]
    celda = celda_de(estilo)
    cara_h = h - 2 - labio
    return (w - celda[0]) // 2, 1 + (cara_h - 7 * esc) // 2


# El halo de la tecla de ahora: escalonado (no un degradado) y con rayitos de
# sol. La tecla va en (HALO_BORDE, HALO_BORDE) de su lienzo.
HALO_BORDE = 7


def halo(color=ORO[4], radio=4):
    w = h = 28
    x0 = y0 = HALO_BORDE
    im, q = lienzo(w + 2 * HALO_BORDE, h + 2 * HALO_BORDE)
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
    return im


def marca():
    """La marca de hecho: una palomita verde con su contorno (9x7; la palomita
    empieza en (1,1))."""
    im, q = lienzo(9, 7)
    pts = {(0, 2), (1, 3), (2, 4), (3, 3), (4, 2), (5, 1), (6, 0), (1, 2), (2, 3), (3, 2), (4, 1), (5, 0)}
    for (px_, py) in borde4(pts):
        q[1 + px_, 1 + py] = VERDE[0]
    for (px_, py) in pts:
        q[1 + px_, 1 + py] = VERDE[4] if py < 2 or px_ < 2 else VERDE[3]
    return im


# La tecla fallada se monta en tres capas: la base rota (con la esquina
# saltada), la letra y, encima, las grietas que la cruzan y las esquirlas que
# saltan fuera. La tecla va en (GRIETAS_X, GRIETAS_Y) del lienzo de las grietas.
GRIETAS_X, GRIETAS_Y = 4, 3
LINEAS_GRIETA = ((13, 1), (13, 2), (12, 3), (12, 4), (13, 5), (14, 6), (14, 7), (13, 8), (12, 9), (12, 10),
                 (13, 11), (14, 12), (14, 13), (15, 14), (15, 15), (14, 16), (14, 17), (13, 18), (13, 19),
                 (13, 20), (12, 21), (12, 22), (11, 23), (11, 24), (12, 25), (12, 26),
                 (14, 9), (15, 9), (16, 8), (17, 8), (18, 7), (11, 15), (10, 15), (9, 16), (8, 16), (7, 17))


def tecla_rota():
    im = tecla_base('rota')
    q = im.load()
    w, h = im.size
    for (x, y) in ((x, y) for y in range(0, 5) for x in range(w - 6, w) if x - (w - 6) > y):
        q[x, y] = (0, 0, 0, 0)                                       # la esquina saltada
    for (x, y) in ((w - 6, 1), (w - 5, 1), (w - 4, 2), (w - 3, 2), (w - 2, 3), (w - 1, 4)):
        q[x, y] = CARMESI[0]
    return im


def grietas_rota():
    w, h = 28, 28
    im, q = lienzo(w + GRIETAS_X + 6, h + GRIETAS_Y)
    for (x, y) in LINEAS_GRIETA:
        if 0 < x < w - 1 and 0 < y < h - 1:
            q[GRIETAS_X + x, GRIETAS_Y + y] = CARMESI[0]
    for (x, y, c) in ((w + 2, -2, CARMESI[3]), (w + 3, -3, CARMESI[2]), (w + 5, 1, CARMESI[4]), (w + 1, 3, CARMESI[2]),
                      (-3, 6, CARMESI[3]), (-4, 7, CARMESI[2])):
        q[GRIETAS_X + x, GRIETAS_Y + y] = c
    return im


def reloj():
    """Un reloj de arena de oro (5x7) para la losa del tiempo."""
    return dibujo(["ooooo", "oYYGo", ".oGo.", "..o..", ".oGo.", "oGGgo", "ooooo"],
                  {'o': ORO[0], 'Y': ORO[4], 'G': ORO[3], 'g': ORO[2]})


QTE_ANCHO = 160              # la losa de la liberacion y la del tiempo
CUARTO_ROJO = 0.25           # el ultimo cuarto del tiempo (el de la izquierda), en rojo


def tiempo_losa():
    """La losa del tiempo: el ultimo cuarto, aun vacio, rayado en rojo hondo."""
    im, q = lienzo(QTE_ANCHO, 5)
    losa(q, 0, QTE_ANCHO, 0, 5)
    ancho = QTE_ANCHO - 2
    for x in range(ancho):
        if x < ancho * CUARTO_ROJO and x % 3 == 0:
            for y in range(1, 4):
                q[1 + x, y] = hexc('3a0c0a')
    return im


def tiempo_relleno():
    """El tiempo entero: rojo en su ultimo cuarto, oro en el resto. El HUD lo
    recorta: se vacia hacia la izquierda."""
    ancho = QTE_ANCHO - 2
    im, q = lienzo(ancho, 3)
    for x in range(ancho):
        rojo = x < ancho * CUARTO_ROJO
        for y in range(3):
            q[x, y] = (ROJO if y > 0 else hexc('ff9a84')) if rojo else (ORO[3] if y > 0 else ORO[4])
    return im


# ================================================================ al juego
def escribir():
    piezas = {}

    def pieza(nombre, im, carpeta=GUI):
        piezas[nombre] = im
        guardar(im, nombre, carpeta)

    # -- la barra
    for clave in CLAVES:
        R = rampa(clave)
        pieza(f'novilis_barra_marco_{clave}', marco(clave))
        pieza(f'novilis_barra_relleno_{clave}', relleno(clave))
        pieza(f'novilis_barra_nucleo_{clave}', nucleo(clave))
        pieza(f'novilis_barra_rayo_{clave}', dibujo(RAYO, dict(PAL_MUESCA, L=R[4], W=R[5])))
    pieza('novilis_barra_rayo_roto', dibujo(RAYO_ROTO, PAL_MUESCA))
    pieza('novilis_barra_nombre', NOMBRE)
    for clave, texto in ROTULOS.items():
        nombre = f'novilis_barra_fase_{clave}' if isinstance(clave, int) else f'novilis_barra_{clave}'
        pieza(nombre, palabra(texto, gris, ancho=64, derecha=True))
    im, q = lienzo(16, 15)
    cuerno(q, 0, 0)
    pieza('novilis_barra_cuerno', im)
    # -- las fuentes
    for nombre, filas in (('fuente', FUENTE), ('fuente_rajada_1', FUENTE_RAJADA_1), ('fuente_rajada_2', FUENTE_RAJADA_2),
                          ('fuente_rajada_3', FUENTE_RAJADA_3), ('fuente_rota', FUENTE_ROTA)):
        pieza('novilis_barra_' + nombre, dibujo(filas, PAL_FUENTE))
    pieza('novilis_barra_carga_losa', carga_losa())
    pieza('novilis_barra_carga', carga_relleno())
    pieza('novilis_barra_estallido', estallido())
    # -- las trompetas
    pieza('novilis_barra_estatua', angel())
    pieza('novilis_barra_estatua_rajada_1', angel(grietas=1))
    pieza('novilis_barra_estatua_rajada_2', angel(grietas=2))
    pieza('novilis_barra_estatua_rota', angel(roto=True))
    pieza('novilis_barra_melodia', melodia(False))
    pieza('novilis_barra_melodia_luz', melodia(True))
    pieza('novilis_barra_llama_azul', llama_azul())
    # -- la ofrenda, como la ven los demas
    pieza('novilis_barra_ofrenda_sol', ofrenda_sol())
    pieza('novilis_barra_cautivo', cautivo())
    pieza('novilis_barra_liberacion_losa', liberacion_losa(LIBERA_ANCHO))
    pieza('novilis_barra_liberacion', liberacion_relleno(LIBERA_ANCHO - 2))
    # -- la pantalla de la ofrenda (la del cautivo)
    pieza('novilis_qte_tecla_actual', tecla_base('actual'))
    pieza('novilis_qte_tecla_siguiente', tecla_base('siguiente'))
    pieza('novilis_qte_tecla_hecha', tecla_base('hecha'))
    pieza('novilis_qte_tecla_rota', tecla_rota())
    pieza('novilis_qte_grietas', grietas_rota())
    pieza('novilis_qte_halo', halo())
    pieza('novilis_qte_marca', marca())
    pieza('novilis_qte_letras_grandes', atlas_letras(('actual', 'rota'), CELDA_GRANDE))
    pieza('novilis_qte_letras_pequenas', atlas_letras(('siguiente', 'hecha'), CELDA_PEQUENA))
    pieza('novilis_qte_titulo', palabra('OFRENDA AL SOL', oro_claro))
    pieza('novilis_qte_sigue', palabra('SIGUE LAS TECLAS', de_rampa([hexc(c) for c in ('f0e4cc', 'e0d2b8', 'd0c0a4',
                                                                                        'c0ae92', 'b09e82')]),
                                       glifos=MINI))
    pieza('novilis_qte_fallaste', palabra('\u00a1FALLASTE!', de_rampa([CARMESI[5], CARMESI[4], CARMESI[4], CARMESI[3],
                                                                       CARMESI[3], CARMESI[3], CARMESI[2]]),
                                          borde=CARMESI[0]))
    pieza('novilis_qte_libre', palabra('\u00a1LIBRE!', de_rampa([VERDE[5], VERDE[4], VERDE[4], VERDE[3], VERDE[3],
                                                                 VERDE[3], VERDE[2]]), borde=VERDE[0]))
    pieza('novilis_qte_etiqueta', palabra('LIBERACION', de_rampa([VERDE[5], VERDE[4], VERDE[4], VERDE[3], VERDE[3]]),
                                          glifos=MINI))
    pieza('novilis_qte_liberacion_losa', liberacion_losa(QTE_ANCHO))
    pieza('novilis_qte_liberacion', liberacion_relleno(QTE_ANCHO - 2))
    pieza('novilis_qte_tiempo_losa', tiempo_losa())
    pieza('novilis_qte_tiempo', tiempo_relleno())
    pieza('novilis_qte_reloj', reloj())
    # -- la quemadura
    for grado in (1, 2, 3):
        pieza(f'novilis_quemadura_{grado}', quemadura(grado))
    pieza('quemadura', quemadura_efecto(), EFECTO)
    return piezas


PIEZAS = escribir()

# Las medidas que el Java tiene que copiar, para comprobarlas a ojo.
print('nombre', NOMBRE.size, 'en x =', NOMBRE_X)
print('ancho del texto de los rotulos:', {k: ancho_texto(v) for k, v in ROTULOS.items()})
print('titulo', PIEZAS['novilis_qte_titulo'].size, 'sigue', PIEZAS['novilis_qte_sigue'].size,
      'fallaste', PIEZAS['novilis_qte_fallaste'].size, 'libre', PIEZAS['novilis_qte_libre'].size,
      'etiqueta', PIEZAS['novilis_qte_etiqueta'].size)
print('letra en la tecla:', {e: sitio_letra(e) for e in TAMANOS})
print('notas en x:', [nota_x(i) for i in range(len(ALTURAS_NOTAS))])
print(len(PIEZAS), 'piezas escritas en', GUI, 'y', EFECTO)
if not VISTA:
    sys.exit(0)


# ================================================================ vista previa
# Montadas como las monta el Java, con las mismas piezas y posiciones.
def P(nombre):
    return PIEZAS[nombre]


def pegar(im, pieza, x, y, tinte=0xFFFFFF, a=255, ancho=None):
    if tinte != 0xFFFFFF or a != 255:
        pieza = tenir(pieza, tinte, a)
    if ancho is not None:
        if ancho <= 0:
            return
        pieza = pieza.crop((0, 0, ancho, pieza.height))
    im.alpha_composite(pieza, (x, y))


def rect(im, x0, y0, x1, y1, c):
    q = im.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if 0 <= x < im.width and 0 <= y < im.height:
                fondo = q[x, y]
                a = c[3] / 255
                q[x, y] = tuple(int(c[i] * a + fondo[i] * (1 - a)) for i in range(3)) + (max(fondo[3], c[3]),)


ALTO = 56
COLOR_ROTULO = {1: 0xFF8A1E, 2: 0xFFC23A, 3: 0xFFF0B0, 4: 0xFF2A3A, 'furia': 0x5AD8FF, 'libre': 0xFFD77A}


def montar(clave, vida, rastro=None, grito=False, fuentes=None, carga=0.0, estatuas=None, melodia_k=0.0,
           ofrenda=None, cautivo_=True):
    R = rampa(clave)
    im = Image.new('RGBA', (NW, ALTO), (0, 0, 0, 0))
    pegar(im, P(f'novilis_barra_marco_{clave}'), 0, 0)
    hx, hy = HX0, HY0
    lleno = redondo(190 * vida)
    if rastro and rastro > vida:
        rect(im, hx + lleno, hy, hx + redondo(190 * rastro), hy + 9,
             (0xE4, 0xF8, 0xFF, 0xD8) if clave == 'furia' else (0xFF, 0xF2, 0xD8, 0xD8))
    x = 0
    while x < lleno:
        w = min(64, lleno - x)
        pegar(im, P(f'novilis_barra_relleno_{clave}'), hx + x, hy, ancho=w)
        x += w
    if lleno >= 3:
        rect(im, hx + lleno - 3, hy, hx + lleno - 2, hy + 3, R[4])
        rect(im, hx + lleno - 2, hy, hx + lleno - 1, hy + 5, R[5])
        rect(im, hx + lleno - 2, hy + 5, hx + lleno - 1, hy + 9, R[4])
        rect(im, hx + lleno - 1, hy, hx + lleno, hy + 9, R[5])
        rect(im, hx + lleno - 1, hy - 1, hx + lleno, hy, R[4])
        rect(im, hx + lleno - 2, hy - 2, hx + lleno - 1, hy - 1, R[3])
    for corte in (0.75, 0.5, 0.25):
        ex = hx + redondo(190 * corte) - 3
        pegar(im, P('novilis_barra_rayo_roto' if vida < corte else f'novilis_barra_rayo_{clave}'), ex, hy - 5)
    pegar(im, P(f'novilis_barra_nucleo_{clave}'), EC[0] - NUC // 2, EC[1] - NUC // 2)
    pegar(im, P('novilis_barra_nombre'), NOMBRE_X, 9)
    rot = f'novilis_barra_fase_{clave}' if isinstance(clave, int) else f'novilis_barra_{clave}'
    pegar(im, P(rot), ROTULO_X, 8, COLOR_ROTULO[clave])
    if grito:
        pegar(im, P('novilis_barra_cuerno'), ROTULO_X + 64 - (ancho_texto(ROTULOS[clave]) - 1) - 16, 2)
    if fuentes is not None:
        for k, golpes in enumerate(fuentes):
            n = ('fuente_rota' if golpes >= 10 else 'fuente' if golpes <= 0
                 else f'fuente_rajada_{1 + min(2, (golpes - 1) * 3 // 9)}')
            pegar(im, P('novilis_barra_' + n), HX0 + k * 13, 36)
        pegar(im, P('novilis_barra_carga_losa'), CARGA_X, CARGA_Y)
        n = redondo((CARGA_ANCHO - 2) * carga)
        pegar(im, P('novilis_barra_carga'), CARGA_X + 1, CARGA_Y + 1, ancho=n)
        if n > 1:
            rect(im, CARGA_X + n, CARGA_Y + 1, CARGA_X + n + 1, CARGA_Y + 6, hexc('fff4e0'))
        pegar(im, P('novilis_barra_estallido'), CARGA_X + CARGA_ANCHO - 1, CARGA_Y - 3)
    if estatuas is not None:
        for k, golpes in enumerate(estatuas):
            n = ('estatua_rota' if golpes >= 10 else 'estatua' if golpes <= 0
                 else f'estatua_rajada_{1 + min(1, (golpes - 1) * 2 // 9)}')
            pegar(im, P('novilis_barra_' + n), HX0 - 2 + k * 15, 36)
        pegar(im, P('novilis_barra_melodia'), MELODIA_X, MELODIA_Y)
        sonadas = int(melodia_k * 16 + 1e-4)
        if sonadas > 0:
            w = MELODIA_ANCHO if sonadas >= 16 else 8 + redondo(sonadas * PASO_NOTAS) - 1
            pegar(im, P('novilis_barra_melodia_luz'), MELODIA_X, MELODIA_Y, ancho=w)
        pegar(im, P('novilis_barra_llama_azul'), MELODIA_X + MELODIA_ANCHO - 1, MELODIA_Y - 2)
    if ofrenda is not None:
        pegar(im, P('novilis_barra_ofrenda_sol'), HX0, 35)
        if cautivo_:
            pegar(im, P('novilis_barra_cautivo'), HX0 + 7, 42)
        pegar(im, P('novilis_barra_liberacion_losa'), LIBERA_X, LIBERA_Y)
        n = redondo((LIBERA_ANCHO - 2) * ofrenda)
        pegar(im, P('novilis_barra_liberacion'), LIBERA_X + 1, LIBERA_Y + 1, ancho=n)
        if n > 0:
            rect(im, LIBERA_X + n, LIBERA_Y + 1, LIBERA_X + n + 1, LIBERA_Y + 6, VERDE[5])
    return im


def montar_qte(teclas, indice, tiempo, fallo=False, exito=False, w=427, h=240):
    """La pantalla de la ofrenda, como la monta OfrendaHud."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    cx = w // 2
    yc = min(h // 2 + 28, h - 86)
    pegar(im, P('novilis_qte_titulo'), cx - P('novilis_qte_titulo').width // 2, yc - 42)
    if fallo:
        sub, sy = P('novilis_qte_fallaste'), yc - 29
    elif exito:
        sub, sy = P('novilis_qte_libre'), yc - 29
    else:
        sub, sy = P('novilis_qte_sigue'), yc - 28
    pegar(im, sub, cx - sub.width // 2, sy)
    actual = min(indice, len(teclas) - 1)
    xa, ya = cx - 14, yc - 14
    if not fallo:
        pegar(im, P('novilis_qte_halo'), xa - HALO_BORDE, ya - HALO_BORDE)
    lx, ly = sitio_letra('actual')
    cg = CELDA_GRANDE
    pegar(im, P('novilis_qte_tecla_rota' if fallo else 'novilis_qte_tecla_actual'), xa, ya)
    letra = ord(teclas[actual]) - ord('A')
    im.alpha_composite(P('novilis_qte_letras_grandes').crop((letra * cg[0], (1 if fallo else 0) * cg[1],
                                                             (letra + 1) * cg[0], (2 if fallo else 1) * cg[1])),
                       (xa + lx, ya + ly))
    if fallo:
        pegar(im, P('novilis_qte_grietas'), xa - GRIETAS_X, ya - GRIETAS_Y)
    if exito:
        pegar(im, P('novilis_qte_marca'), xa + 21, ya + 20)
    cp = CELDA_PEQUENA
    x = xa + 28 + 9
    for j, apagar in enumerate((0.0, 0.22, 0.4, 0.55)):
        i = actual + 1 + j
        if exito or i >= len(teclas):
            break
        g = 255 - int(255 * apagar)
        tinte = (g << 16) | (g << 8) | g
        pegar(im, P('novilis_qte_tecla_siguiente'), x, yc - 7, tinte)
        sx, sy2 = sitio_letra('siguiente')
        letra = ord(teclas[i]) - ord('A')
        pegar(im, P('novilis_qte_letras_pequenas').crop((letra * cp[0], 0, (letra + 1) * cp[0], cp[1])),
              x + sx, yc - 7 + sy2, tinte)
        x += 22
    x = xa - 9
    for j, apagar in enumerate((0.0, 0.0, 0.3, 0.5)):
        i = actual - 1 - j
        if i < 0:
            break
        g = 255 - int(255 * apagar)
        tinte = (g << 16) | (g << 8) | g
        x -= 14
        pegar(im, P('novilis_qte_tecla_hecha'), x, yc - 3, tinte)
        sx, sy2 = sitio_letra('hecha')
        letra = ord(teclas[i]) - ord('A')
        pegar(im, P('novilis_qte_letras_pequenas').crop((letra * cp[0], cp[1], (letra + 1) * cp[0], 2 * cp[1])),
              x + sx, yc - 3 + sy2, tinte)
        pegar(im, P('novilis_qte_marca'), x + 7, yc + 3, tinte)
        x -= 4
    bx0, by = cx - 80, yc + 28
    pegar(im, P('novilis_qte_etiqueta'), bx0 - 1, by - 9)
    pegar(im, P('novilis_qte_liberacion_losa'), bx0, by)
    ancho = QTE_ANCHO - 2
    lib = 1.0 if exito else indice / len(teclas)
    n = redondo(ancho * (lib * 0.6 if fallo else lib))
    if fallo:
        rect(im, bx0 + 1 + n, by + 1, bx0 + 1 + redondo(ancho * lib), by + 6, alfa(CARMESI[3], 0xD8))
    pegar(im, P('novilis_qte_liberacion'), bx0 + 1, by + 1, ancho=n)
    if n > 0:
        rect(im, bx0 + n, by + 1, bx0 + n + 1, by + 6, VERDE[5])
    ty = by + 11
    pegar(im, P('novilis_qte_reloj'), bx0 - 8, ty - 1)
    pegar(im, P('novilis_qte_tiempo_losa'), bx0, ty)
    pegar(im, P('novilis_qte_tiempo'), bx0 + 1, ty + 1, ancho=redondo(ancho * tiempo))
    return im


K = 4
ESTADOS = [
    ('fase1', lambda: montar(1, 0.85, 0.91)),
    ('fase2', lambda: montar(2, 0.62, 0.69)),
    ('fase3', lambda: montar(3, 0.38, 0.45)),
    ('fase4', lambda: montar(4, 0.15, 0.22, grito=True)),
    ('furia', lambda: montar('furia', 0.3, 0.36, grito=True)),
    ('libre', lambda: montar('libre', 0.0)),
    ('fuentes', lambda: montar(3, 0.38, 0.44, fuentes=(10, 5, 0), carga=0.7)),
    ('fuentes_pasos', lambda: montar(3, 0.38, None, fuentes=(2, 8, 9), carga=0.92)),
    ('trompetas', lambda: montar(2, 0.62, None, estatuas=(10, 3, 7, 0), melodia_k=0.6)),
    ('trompetas_furia', lambda: montar(2, 0.55, None, estatuas=(10, 10, 6, 1), melodia_k=0.85)),
    ('ofrenda', lambda: montar(1, 0.8, None, ofrenda=0.45)),
]
for nombre, hacer in ESTADOS:
    im = hacer()
    im.resize((im.width * K, im.height * K), Image.NEAREST).save(os.path.join(VISTA, f'barra_{nombre}.png'))

# Todas las barras juntas sobre un cielo de fuego, a x2
hoja = Image.new('RGBA', (NW * 2 + 40, len(ESTADOS) * (ALTO * 2 + 10) + 10), (0x6a, 0x3a, 0x22, 255))
for i, (nombre, hacer) in enumerate(ESTADOS):
    im = hacer()
    hoja.alpha_composite(im.resize((NW * 2, ALTO * 2), Image.NEAREST), (20, 10 + i * (ALTO * 2 + 10)))
hoja.save(os.path.join(VISTA, 'hoja_barras.png'))

for nombre, args in (('qte', dict(teclas='KRZAQMXW', indice=3, tiempo=0.55)),
                     ('qte_inicio', dict(teclas='HJYPBQ', indice=0, tiempo=0.95)),
                     ('qte_fallo', dict(teclas='KRZAQMXW', indice=3, tiempo=0.18, fallo=True)),
                     ('qte_libre', dict(teclas='KRZAQMXW', indice=8, tiempo=0.3, exito=True))):
    im = montar_qte(**args)
    fondo = Image.new('RGBA', im.size, (0x5a, 0x40, 0x30, 255))
    fondo.alpha_composite(im)
    fondo.resize((im.width * 2, im.height * 2), Image.NEAREST).save(os.path.join(VISTA, f'{nombre}.png'))
    recorte = fondo.crop((70, 95, 357, 200))
    recorte.resize((recorte.width * 4, recorte.height * 4), Image.NEAREST).save(os.path.join(VISTA, f'{nombre}_x4.png'))

# Las letras, a x6
for n in ('novilis_qte_letras_grandes', 'novilis_qte_letras_pequenas'):
    im = P(n)
    f = Image.new('RGBA', im.size, (0x5a, 0x40, 0x30, 255))
    f.alpha_composite(im)
    f.resize((im.width * 6, im.height * 6), Image.NEAREST).save(os.path.join(VISTA, n + '.png'))

# Las piezas pequenas de debajo y la quemadura, a x8 sobre pizarra
PIZARRA = (0x2a, 0x2a, 0x2e, 255)
fila = ['novilis_barra_fuente', 'novilis_barra_fuente_rajada_1', 'novilis_barra_fuente_rajada_2',
        'novilis_barra_fuente_rajada_3', 'novilis_barra_fuente_rota', 'novilis_barra_estatua',
        'novilis_barra_estatua_rajada_1', 'novilis_barra_estatua_rajada_2', 'novilis_barra_estatua_rota',
        'novilis_quemadura_1', 'novilis_quemadura_2', 'novilis_quemadura_3', 'quemadura']
hoja = Image.new('RGBA', (4 + sum(P(n).width + 4 for n in fila), 26), PIZARRA)
x = 4
for n in fila:
    hoja.alpha_composite(P(n), (x, 4))
    x += P(n).width + 4
hoja.resize((hoja.width * 8, hoja.height * 8), Image.NEAREST).save(os.path.join(VISTA, 'piezas.png'))
hoja.resize((hoja.width * 2, hoja.height * 2), Image.NEAREST).save(os.path.join(VISTA, 'piezas_x2.png'))
print('vista previa en', VISTA)

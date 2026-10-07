"""
Los iconos de las habilidades de las armaduras de los jefes (octubre de 2026):
el HUD los pinta junto a la barra rapida, dentro de su marco, con la recarga
encima (se oscurece de arriba abajo) y una barra del color del elemento
mientras dura la activa (HabilidadHud.java).

  manantial  agua (Nerea, el sanador): un surtidor que brota de su poza, se
             abre en un paraguas de agua y deja caer gotas; arriba, el
             destello en cruz de la curacion.
  muralla    tierra (Rajang, el tanque): una muralla de bloques de jade con
             sus almenas rematadas de oro y un cristal que crece en medio.
  corriente  viento (Aeralis, el apoyo): un remolino que sube, de bandas que
             se estrechan hacia abajo, con dos flechas de aire a los lados.
  furia      fuego (Novilis, el dano): el sol al rojo con una corona de tres
             llamas que suben y rayos cortos; el canto carmesi de la furia.

Como se dibujan (ver DISENO.md): la silueta se escribe como datos (discos,
anchuras por fila, poligonos) y el color se calcula por anillos, contando los
pasos hasta el aire (el borde 0, sus vecinos 1...), mas un empujon de luz
arriba a la izquierda. Van sobre el fondo oscuro del marco, asi que la rampa
entera va por encima (sin borde casi negro: el canto es un tono medio del
propio color) y cada uno se lee por el matiz: cian, verde, lavanda y ambar.

  marco      22x22: el marco del icono, de oro oscuro y neutro (no es de
             ningun elemento), con el fondo oscuro donde va el icono (18x18,
             a dos pixeles del borde).

Escribe textures/gui/habilidad/{manantial,muralla,corriente,furia,marco}.png.

Uso: python habilidades_iconos.py <raiz> [hoja.png]
"""
import math, os, sys
from PIL import Image, ImageDraw

RAIZ = sys.argv[1]
HOJA = sys.argv[2] if len(sys.argv) > 2 else None
SALIDA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/habilidad')
N = 18
MARCO = 22


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def rampa(*cs):
    return [hexc(c) for c in cs]


# ----------------------------------------------------------------------
#  Las rampas: del canto (un tono medio, no negro) al nucleo (casi blanco,
#  tirando al color). Una por elemento y alguna de acento.
# ----------------------------------------------------------------------
AGUA = rampa('2386b4', '33b4e0', '62d8f8', 'a4eeff', 'e2fcff')
JADE = rampa('25884c', '38b066', '62d888', 'a6f2b8', 'e2ffe8')
ORO = rampa('a8762a', 'd6a03e', 'f2c868', 'ffe6a2')
LAVANDA = rampa('6d62d8', '8f86f2', 'b4acff', 'd8d2ff', 'f6f4ff')
CIELO = rampa('3f8fe0', '62b8ff', '9cdcff', 'dcf4ff')
FUEGO = rampa('c8341e', 'ee6418', 'ff9a26', 'ffc84a', 'ffe98e', 'fffbe6')


# ----------------------------------------------------------------------
#  Herramientas: mascaras (conjuntos de pixeles) y su sombreado
# ----------------------------------------------------------------------
def disco(c, r):
    return {(x, y) for y in range(N) for x in range(N) if math.hypot(x + 0.5 - c[0], y + 0.5 - c[1]) <= r}


def por_filas(desde_y, centro, semis):
    """Anchuras por fila: semis[i] es la semianchura de la fila desde_y + i,
    alrededor de 'centro' (con centro en x.0 las filas salen pares y simetricas)."""
    out = set()
    for i, s in enumerate(semis):
        for x in range(N):
            if abs(x + 0.5 - centro) <= s:
                out.add((x, desde_y + i))
    return out


def lengua(base, punta, ancho, curva=0.0):
    """Una lengua de fuego o un chorro: de la base a la punta, con la
    semianchura que mengua (y se tuerce de lado con 'curva')."""
    out = set()
    (bx, by), (px, py) = base, punta
    for y in range(N):
        for x in range(N):
            for k in range(41):
                t = k / 40
                cx = bx + (px - bx) * t + curva * math.sin(t * math.pi)
                cy = by + (py - by) * t
                if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= ancho * (1 - t) ** 0.8 + 0.35:
                    out.add((x, y))
                    break
    return out


def anillos(mascara):
    """Pasos hasta el aire (vecindad de 4): 0 el borde, 1 sus vecinos..."""
    hondo = {}
    frente = [p for p in mascara if any((p[0] + dx, p[1] + dy) not in mascara
                                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for p in frente:
        hondo[p] = 0
    paso = 0
    while frente:
        paso += 1
        nuevo = []
        for p in frente:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (p[0] + dx, p[1] + dy)
                if q in mascara and q not in hondo:
                    hondo[q] = paso
                    nuevo.append(q)
        frente = nuevo
    return hondo


def pintar(im, mascara, rp, luz=(5.5, 5.5), alcance=9.0, base=0):
    """Pinta la mascara con su rampa por anillos y con un tono mas cerca de la
    luz (arriba a la izquierda): el canto, del tono 'base'."""
    px = im.load()
    hondo = anillos(mascara)
    for (x, y), h in hondo.items():
        if not (0 <= x < im.width and 0 <= y < im.height):
            continue
        k = base + min(h, len(rp) - 1 - base)
        if h > 0 and math.hypot(x + 0.5 - luz[0], y + 0.5 - luz[1]) < alcance * 0.55:
            k += 1
        px[x, y] = rp[max(0, min(len(rp) - 1, k))]


def puntos(im, lista):
    px = im.load()
    for x, y, c in lista:
        px[x, y] = c


# ----------------------------------------------------------------------
#  manantial: el surtidor
# ----------------------------------------------------------------------
def manantial():
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    # La poza: una elipse ancha abajo.
    poza = {(x, y) for y in range(N) for x in range(N) if ((x + 0.5 - 9) / 7.2) ** 2 + ((y + 0.5 - 14.6) / 2.3) ** 2 <= 1}
    # El chorro que sube, ancho abajo y fino arriba.
    chorro = por_filas(4, 9.0, [1.0, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.9, 2.3])
    # El paraguas: un arco de agua que se abre arriba y cae a los lados.
    paraguas = {(x, y) for y in range(N) for x in range(N)
                if 3.3 <= math.hypot(x + 0.5 - 9, (y + 0.5 - 8.6) * 1.2) <= 5.4 and y + 0.5 < 9.2}
    agua = poza | chorro | paraguas
    pintar(im, agua, AGUA, luz=(7.0, 6.0))
    # El reflejo de la poza y la espuma donde cae el chorro.
    puntos(im, [(5, 14, AGUA[3]), (6, 14, AGUA[4]), (11, 15, AGUA[3]), (8, 13, AGUA[4]), (9, 13, AGUA[4])])
    # Las gotas que caen de los bordes del paraguas.
    puntos(im, [(2, 10, AGUA[2]), (3, 10, AGUA[3]), (3, 11, AGUA[2]), (14, 10, AGUA[3]), (15, 10, AGUA[2]),
                (14, 11, AGUA[2]), (1, 12, AGUA[1]), (16, 12, AGUA[1])])
    # La curacion: un destello en cruz arriba a la derecha.
    puntos(im, [(15, 0, AGUA[3]), (14, 1, AGUA[3]), (15, 1, AGUA[4]), (16, 1, AGUA[3]), (15, 2, AGUA[3])])
    puntos(im, [(2, 3, AGUA[2])])
    return im


# ----------------------------------------------------------------------
#  muralla: la muralla de jade
# ----------------------------------------------------------------------
def muralla():
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    lienzo = {(x, y) for y in range(8, 17) for x in range(2, 16)}
    almenas = {(x, y) for y in range(5, 8) for x in list(range(2, 5)) + list(range(7, 11)) + list(range(13, 16))}
    muro = lienzo | almenas
    pintar(im, muro, JADE, luz=(5.0, 7.0), alcance=10)
    px = im.load()
    # Las juntas entre los bloques (un tono medio, no negro), a matajunta.
    for y in (10, 13):
        for x in range(3, 15):
            px[x, y] = JADE[0]
    for y0, juntas in ((8, (6, 11)), (11, (4, 9, 13)), (14, (6, 11))):
        for y in range(y0, y0 + 2 if y0 < 14 else 16):
            for x in juntas:
                px[x, y] = JADE[0]
    # El brillo de la arista de arriba de cada bloque.
    for y0, tramos in ((11, ((3, 3), (5, 8), (10, 12), (14, 14))), (14, ((3, 5), (7, 10), (12, 14)))):
        for a, b in tramos:
            for x in range(a, b + 1):
                px[x, y0] = JADE[3]
    # El oro que remata las almenas.
    for xs in (range(2, 5), range(7, 11), range(13, 16)):
        for x in xs:
            px[x, 5] = ORO[2] if x in (2, 7, 13) else ORO[1]
    # El cristal de jade que crece en medio.
    cristal = por_filas(0, 9.0, [0.3, 0.8, 1.0, 1.2, 1.4])
    pintar(im, cristal, JADE, luz=(8.0, 1.5), alcance=4, base=1)
    puntos(im, [(8, 1, JADE[4]), (8, 2, JADE[4])])
    # Esquirlas que saltan.
    puntos(im, [(1, 2, JADE[2]), (16, 3, JADE[2]), (14, 1, JADE[3]), (5, 3, JADE[1])])
    return im


# ----------------------------------------------------------------------
#  corriente: el remolino que sube
# ----------------------------------------------------------------------
def corriente():
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    px = im.load()
    # Cinco bandas que se estrechan hacia abajo, cada una corrida a un lado
    # (asi gira): (fila de arriba, x de la izquierda, x de la derecha).
    bandas = [(1, 2, 15), (4, 4, 14), (7, 4, 12), (10, 6, 12), (13, 7, 10), (15, 8, 9)]
    for y, a, b in bandas:
        for x in range(a, b + 1):
            arriba = y < 15 and not (x == a or x == b)
            px[x, y] = LAVANDA[4] if (x - a) < (b - a) * 0.35 else LAVANDA[3]
            if y + 1 < N and y < 15:
                px[x, y + 1] = LAVANDA[2] if arriba else LAVANDA[1]
        # Las puntas de cada banda, enroscadas: un pixel que cae del extremo.
        px[a, y] = LAVANDA[2]
        if y < 15:
            px[b, y + 1] = LAVANDA[0]
            if b + 1 < N:
                px[b + 1, y + 1] = LAVANDA[1] if y < 13 else LAVANDA[0]
    # Un hilo de cielo que sube por dentro.
    for x, y in ((9, 14), (9, 12), (10, 11), (9, 9), (8, 8), (9, 6), (10, 5), (9, 3), (8, 2)):
        px[x, y] = CIELO[3] if y < 8 else CIELO[2]
    # Dos flechas de aire a los lados, hacia arriba.
    for cx, cy in ((1, 10), (16, 8)):
        puntos(im, [(cx, cy - 1, CIELO[2]), (cx - 1, cy, CIELO[1]) if cx > 0 else (cx, cy, CIELO[1]),
                    (cx + 1, cy, CIELO[1]) if cx + 1 < N else (cx, cy, CIELO[1]), (cx, cy + 1, CIELO[0])])
    return im


# ----------------------------------------------------------------------
#  furia: el sol al rojo con su corona de llamas
# ----------------------------------------------------------------------
def furia():
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    centro = (9.0, 11.6)
    llamas = (lengua((9.0, 9.0), (9.0, 0.6), 2.9) |
              lengua((6.2, 9.6), (3.4, 2.6), 2.2, curva=-0.8) |
              lengua((11.8, 9.6), (14.6, 2.6), 2.2, curva=0.8))
    sol = disco(centro, 4.6)
    # Rayos cortos a los lados y abajo.
    rayos = set()
    for ang in (180, 215, 270, 325, 0):
        a = math.radians(ang)
        for r in (5.2, 6.0):
            rayos.add((int(centro[0] + math.cos(a) * r), int(centro[1] - math.sin(a) * r)))
    todo = llamas | sol | rayos
    # Todo el fuego por anillos (el canto carmesi), y el sol encima, mas claro.
    pintar(im, todo, FUEGO, luz=(8.0, 6.0), alcance=8)
    pintar(im, sol, FUEGO, luz=(8.0, 10.0), alcance=6, base=2)
    px = im.load()
    for p in rayos:
        if 0 <= p[0] < N and 0 <= p[1] < N:
            px[p] = FUEGO[1]
    # El alma blanca del sol.
    for p in disco((centro[0] - 0.4, centro[1] - 0.4), 1.6):
        px[p] = FUEGO[5]
    # Brasas que saltan.
    puntos(im, [(1, 5, FUEGO[2]), (16, 4, FUEGO[2]), (2, 1, FUEGO[3]), (15, 0, FUEGO[1]), (12, 0, FUEGO[3])])
    return im


# ----------------------------------------------------------------------
#  marco: el marco del icono (22x22)
# ----------------------------------------------------------------------
def marco():
    im = Image.new('RGBA', (MARCO, MARCO), (0, 0, 0, 0))
    px = im.load()
    BORDE = hexc('140f0c')
    ORO_CLARO, ORO_MEDIO, ORO_HONDO = hexc('c9a256'), hexc('9c7a3a'), hexc('5e4520')
    for y in range(MARCO):
        for x in range(MARCO):
            canto = min(x, y, MARCO - 1 - x, MARCO - 1 - y)
            if canto == 0:
                # El filo de fuera, oscuro; las esquinas redondeadas (sin el pixel de la esquina).
                if (x in (0, MARCO - 1)) and (y in (0, MARCO - 1)):
                    continue
                px[x, y] = BORDE
            elif canto == 1:
                # El oro con bisel: claro arriba y a la izquierda, hondo abajo y a la derecha.
                c = ORO_CLARO if (y == 1 or x == 1) else ORO_HONDO
                if (x, y) in ((1, MARCO - 2), (MARCO - 2, 1)):
                    c = ORO_MEDIO
                px[x, y] = c
            else:
                # El fondo del hueco: oscuro, con una sombra por dentro junto al oro.
                d = math.hypot(x + 0.5 - MARCO / 2, y + 0.5 - MARCO / 2) / (MARCO / 2)
                v = int(34 - 12 * d)
                fondo = (v, v - 3, v + 2, 236)
                if canto == 2 and (x == 2 or y == 2):
                    fondo = (12, 10, 14, 240)
                px[x, y] = fondo
    # Los remaches de las esquinas.
    for x, y in ((1, 1), (MARCO - 2, 1), (1, MARCO - 2), (MARCO - 2, MARCO - 2)):
        px[x, y] = hexc('f0d48a') if (x, y) == (1, 1) else ORO_CLARO
    return im


ICONOS = {'manantial': manantial, 'muralla': muralla, 'corriente': corriente, 'furia': furia}

os.makedirs(SALIDA, exist_ok=True)
SALIDAS = {}
for nombre, fn in ICONOS.items():
    im = fn()
    im.save(os.path.join(SALIDA, f'{nombre}.png'))
    SALIDAS[nombre] = im
SALIDAS['marco'] = marco()
SALIDAS['marco'].save(os.path.join(SALIDA, 'marco.png'))
print('ok:', ', '.join(SALIDAS), '->', SALIDA)

# ----------------------------------------------------------------------
#  Hoja de control: cada icono dentro del marco, a 8x; y a tamano real (x1,
#  x2, x3) junto a una barra rapida de mentira: normal, en recarga (gris y
#  oscurecido de arriba abajo, como en el HUD) y activo (con la barra).
# ----------------------------------------------------------------------
if HOJA:
    COLOR = {'manantial': (0x4F, 0xD8, 0xE8), 'muralla': (0x5B, 0xE3, 0x8A), 'corriente': (0xC9, 0xA6, 0xFF),
             'furia': (0xFF, 0xB2, 0x38)}

    def en_marco(icono, estado='normal'):
        m = SALIDAS['marco'].copy()
        ic = icono.copy()
        if estado == 'recarga':
            ic = Image.eval(ic, lambda v: v)
            p = ic.load()
            for y in range(N):
                for x in range(N):
                    r, g, b, a = p[x, y]
                    p[x, y] = (r * 0x6A // 255, g * 0x6A // 255, b * 0x6A // 255, a)
        m.alpha_composite(ic, (2, 2))
        d = ImageDraw.Draw(m)
        if estado == 'recarga':
            sombra = Image.new('RGBA', (N, 11), (0, 0, 0, 0x99))
            m.alpha_composite(sombra, (2, 2))
        elif estado == 'activa':
            d.rectangle((1, MARCO - 3, MARCO - 2, MARCO - 2), fill=(0, 0, 0, 0xAA))
            d.rectangle((1, MARCO - 3, 13, MARCO - 2), fill=COLOR_ACTUAL + (255,))
        return m

    hoja = Image.new('RGBA', (4 * (MARCO * 8 + 12) + 12, MARCO * 8 + 24 + 3 * (MARCO * 3 + 12) + 12), (48, 50, 58, 255))
    for i, nombre in enumerate(ICONOS):
        COLOR_ACTUAL = COLOR[nombre]
        g = en_marco(SALIDAS[nombre]).resize((MARCO * 8, MARCO * 8), Image.NEAREST)
        hoja.alpha_composite(g, (12 + i * (MARCO * 8 + 12), 12))
        y0 = MARCO * 8 + 24
        for f, estado in enumerate(('normal', 'recarga', 'activa')):
            m = en_marco(SALIDAS[nombre], estado)
            x0 = 12 + i * (MARCO * 8 + 12)
            yy = y0 + f * (MARCO * 3 + 12)
            ImageDraw.Draw(hoja).rectangle((x0, yy, x0 + MARCO * 8, yy + MARCO * 3 + 4), fill=(20, 22, 28, 255))
            hoja.alpha_composite(m, (x0 + 4, yy + 4))
            hoja.alpha_composite(m.resize((MARCO * 2, MARCO * 2), Image.NEAREST), (x0 + 32, yy + 4))
            hoja.alpha_composite(m.resize((MARCO * 3, MARCO * 3), Image.NEAREST), (x0 + 82, yy + 4))
    os.makedirs(os.path.dirname(os.path.abspath(HOJA)), exist_ok=True)
    hoja.save(HOJA)
    print('hoja', HOJA)

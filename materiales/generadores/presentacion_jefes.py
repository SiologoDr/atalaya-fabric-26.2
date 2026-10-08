"""
Los rotulos de la presentacion de los jefes: lo que sale en mitad de la
pantalla, entre las bandas negras, cuando un jefe despierta y ruge. Solo el
NOMBRE y lo que es (JEFE DEL FUEGO), con una linea de adorno debajo (Juan,
08-10-2026: sin el epiteto ni el lema).

Van en LETRAS DE PIXEL, las mismas de las barras de vida (rajang_hud.py,
novilis_hud.py: dos pixeles de trazo, siete de alto, contorno oscuro de un
pixel y sombra debajo), no en fuentes de ordenador (Juan, 08-10-2026: "las
letras de la presentacion deben ser pixeles, podrias usar las mismas de la
barra de vida"). Para el antetitulo, una letra de pixel pequena (3x5) del
mismo estilo.

Todo se dibuja en un lienzo de 240x82 pixeles de arte y se amplia sin
suavizar (vecino mas proximo) por 2, 3, 4 y 6: salen los cuatro anchos que usa
PresentacionHud (480, 720, 960 y 1440 pixeles de pantalla) con los pixeles
cuadrados y nitidos.

El Java anima cada capa por separado (fundido, un poco de desliz vertical,
cortina que se abre desde el centro y un destello que la barre), asi que el
rotulo va partido en capas sobre lienzos identicos que se apilan tal cual.

Uso: python presentacion_jefes.py <raiz del proyecto> [<carpeta de hoja>]

Escribe en textures/gui/presentacion:
  <jefe>_<W>_nombre.png            el nombre con su halo (sin idioma)
  <jefe>_<W>_linea.png             el adorno bajo el nombre (sin idioma)
  <jefe>_<idioma>_<W>_ante.png     el antetitulo (JEFE DEL MAR...)
con W en 480, 720, 960 y 1440, alto W/240*82, e idioma es o en. El destello
(destello.png) no es letra y no se toca.

Composicion (centro de cada renglon, en pixeles de arte de los 82 de alto):
antetitulo 12, nombre 37, linea 58.

Con la carpeta de hoja monta una vista previa de los cuatro a 480 sobre una
captura del juego (854x480, la ventana por defecto).
"""
import os, sys, glob
from PIL import Image

RAIZ = sys.argv[1]
HOJA = sys.argv[2] if len(sys.argv) > 2 else None
SALIDA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/presentacion')
CAPTURAS = os.path.join(RAIZ, 'run/screenshots')
BASE_W, BASE_H = 240, 82
ANCHOS = (480, 720, 960, 1440)
IDIOMAS = ('es', 'en')

Y_ANTE = 12
Y_NOMBRE = 37
Y_LINEA = 58

JEFES = {
    'nerea': dict(
        nombre='NEREA',
        ante={'es': 'JEFE DEL MAR', 'en': 'SEA BOSS'},
        acento=(110, 236, 220), halo=(40, 220, 210), linea=(255, 70, 140), blanco=(240, 246, 244),
        epi=(205, 228, 230), gris=(178, 200, 202), sombra=(2, 14, 18)),
    'aeralis': dict(
        nombre='AERALIS',
        ante={'es': 'JEFE DEL AIRE', 'en': 'AIR BOSS'},
        acento=(120, 214, 255), halo=(120, 150, 255), linea=(190, 140, 255), blanco=(240, 244, 252),
        epi=(205, 214, 236), gris=(184, 194, 214), sombra=(6, 6, 22)),
    'rajang': dict(
        nombre='RAJANG',
        ante={'es': 'JEFE DE LA TIERRA', 'en': 'EARTH BOSS'},
        acento=(118, 236, 158), halo=(60, 210, 110), linea=(248, 217, 124), blanco=(244, 248, 236),
        epi=(212, 232, 214), gris=(182, 204, 188), sombra=(3, 12, 8)),
    # sin poster: ORO[4] y CARMESI[3] de novilis_hud.py, y el halo del fuego
    'novilis': dict(
        nombre='NOVILIS',
        ante={'es': 'JEFE DEL FUEGO', 'en': 'FIRE BOSS'},
        acento=(255, 206, 110), halo=(255, 116, 28), linea=(255, 42, 58), blanco=(252, 246, 234),
        epi=(240, 224, 206), gris=(206, 192, 182), sombra=(20, 6, 4)),
}

# ----------------------------------------------------------------------
#  Las letras. GRANDE: las de las barras de vida (novilis_hud.py), 7 de
#  alto; las tildes y la virgulilla van encima, con una fila de aire.
#  PEQUENA: 3x5 (la M y la W, 5 de ancho; la N, 4).
#  Las filas de mas arriba de la letra (tildes) se cuentan desde abajo:
#  cada glifo se apoya en la linea base.
# ----------------------------------------------------------------------
GRANDE = {
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
    '.': ["..", "..", "..", "..", "..", "##", "##"],
    ',': ["..", "..", "..", "..", "..", "##", ".#"],
    ' ': ["..", "..", "..", "..", "..", "..", ".."],
}
TILDE_6 = ["...##.", "..##..", "......"]
TILDE_4 = ["..##", ".##.", "...."]
for _b, _a in (('A', 'Á'), ('E', 'É'), ('O', 'Ó'), ('U', 'Ú')):
    GRANDE[_a] = TILDE_6 + GRANDE[_b]
GRANDE['Í'] = TILDE_4 + GRANDE['I']
GRANDE['Ñ'] = [".##..#", "#..##.", "......"] + GRANDE['N']

PEQUENA = {
    'A': [".#.", "#.#", "###", "#.#", "#.#"], 'B': ["##.", "#.#", "##.", "#.#", "##."],
    'C': [".##", "#..", "#..", "#..", ".##"], 'D': ["##.", "#.#", "#.#", "#.#", "##."],
    'E': ["###", "#..", "##.", "#..", "###"], 'F': ["###", "#..", "##.", "#..", "#.."],
    'G': [".##", "#..", "#.#", "#.#", ".##"], 'H': ["#.#", "#.#", "###", "#.#", "#.#"],
    'I': ["###", ".#.", ".#.", ".#.", "###"], 'J': ["..#", "..#", "..#", "#.#", ".#."],
    'K': ["#.#", "#.#", "##.", "#.#", "#.#"], 'L': ["#..", "#..", "#..", "#..", "###"],
    'M': ["#...#", "##.##", "#.#.#", "#...#", "#...#"], 'N': ["#..#", "##.#", "#.##", "#..#", "#..#"],
    'O': [".#.", "#.#", "#.#", "#.#", ".#."], 'P': ["##.", "#.#", "##.", "#..", "#.."],
    'Q': [".#.", "#.#", "#.#", "##.", ".##"], 'R': ["##.", "#.#", "##.", "#.#", "#.#"],
    'S': [".##", "#..", ".#.", "..#", "##."], 'T': ["###", ".#.", ".#.", ".#.", ".#."],
    'U': ["#.#", "#.#", "#.#", "#.#", "###"], 'V': ["#.#", "#.#", "#.#", "#.#", ".#."],
    'W': ["#...#", "#...#", "#.#.#", "##.##", "#...#"], 'X': ["#.#", "#.#", ".#.", "#.#", "#.#"],
    'Y': ["#.#", "#.#", ".#.", ".#.", ".#."], 'Z': ["###", "..#", ".#.", "#..", "###"],
    '.': [".", ".", ".", ".", "#"], ',': [".", ".", ".", "#", "#"],
    ' ': ["..", "..", "..", "..", ".."],
}
for _b, _a in (('A', 'Á'), ('E', 'É'), ('I', 'Í'), ('O', 'Ó'), ('U', 'Ú')):
    PEQUENA[_a] = ["..#", "..."] + PEQUENA[_b]
PEQUENA['Ñ'] = [".#.#", "#.#.", "...."] + PEQUENA['N']

SOMBRA = (0, 0, 0, 115)


def mezcla(a, b, k):
    return tuple(int(round(a[i] * (1 - k) + b[i] * k)) for i in range(3))


def puntos_texto(txt, glifos, escala=1, aire=0):
    """Los pixeles de tinta del texto (x, y) con la linea base en y=0 (y crece
    hacia abajo: la letra ocupa de -alto a -1) y la fila de cada uno dentro de
    su glifo contada desde arriba de la letra sin tilde (las tildes, negativa)."""
    alto_l = len(glifos['A'])
    puntos = {}
    x = 0
    for ch in txt.upper():
        g = glifos[ch]
        arriba = len(g) - alto_l
        for fy, fila in enumerate(g):
            for fx, c in enumerate(fila):
                if c != '#':
                    continue
                fila_letra = fy - arriba
                for sx in range(escala):
                    for sy in range(escala):
                        puntos[((x + fx) * escala + sx, (fila_letra - alto_l) * escala + sy)] = fila_letra
        x += len(g[0]) + 1 + aire
    ancho = (x - 1 - aire) * escala
    return puntos, ancho, alto_l * escala


def pintar_texto(im, txt, glifos, cx, cy, relleno, borde, escala=1, aire=0, sombra_dy=1, halo=None):
    """Pinta el texto centrado en cx y con el centro de la letra en cy: halo
    escalonado (opcional), sombra, contorno de un pixel y relleno por filas."""
    puntos, ancho, alto_t = puntos_texto(txt, glifos, escala, aire)
    ox = cx - ancho // 2
    oy = cy + alto_t // 2
    q = im.load()
    W, H = im.size
    tinta = {(x + ox, y + oy) for (x, y) in puntos}

    def poner(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            q[x, y] = c

    if halo:
        color, alfas = halo
        for d in range(len(alfas), 1, -1):
            a = alfas[d - 1]
            for (x, y) in tinta:
                for dx in range(-d, d + 1):
                    for dy in (-d, d):
                        poner_halo(q, W, H, x + dx, y + dy, color, a)
                for dy in range(-d + 1, d):
                    for dx in (-d, d):
                        poner_halo(q, W, H, x + dx, y + dy, color, a)
    for (x, y) in tinta:
        for dy in range(1, sombra_dy + 1):
            if (x, y + dy) not in tinta:
                poner(x, y + dy + 1, SOMBRA)
    for (x, y) in tinta:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) not in tinta:
                    poner(x + dx, y + dy, borde + (255,))
    for (x, y), fila in puntos.items():
        poner(x + ox, y + oy, relleno(fila) + (255,))
    xs = [x for x, _ in tinta]
    return min(xs), max(xs)


def poner_halo(q, W, H, x, y, color, a):
    """El halo: solo donde aun no hay nada mas fuerte."""
    if 0 <= x < W and 0 <= y < H:
        ya = q[x, y][3]
        nueva = int(round(255 * a))
        if nueva > ya:
            q[x, y] = color + (nueva,)


def rampa(arriba, abajo, filas=7):
    return lambda fila: mezcla(arriba, abajo, min(1.0, max(0.0, fila / (filas - 1))))


def lienzo():
    return Image.new('RGBA', (BASE_W, BASE_H), (0, 0, 0, 0))


def oscuro(j):
    return mezcla(j['sombra'], (0, 0, 0), 0.3)


# ----------------------------------------------------------------------
#  Las capas (en pixeles de arte)
# ----------------------------------------------------------------------
def capa_nombre(j):
    im = lienzo()
    relleno = rampa(j['blanco'], mezcla(j['blanco'], j['halo'], 0.42))
    pintar_texto(im, j['nombre'], GRANDE, BASE_W // 2, Y_NOMBRE, relleno, oscuro(j), escala=4, aire=1, sombra_dy=2,
                 halo=(j['halo'], [0.0, 0.62, 0.42, 0.24, 0.10]))
    return im


def capa_ante(j, idioma):
    im = lienzo()
    relleno = rampa(mezcla(j['acento'], (255, 255, 255), 0.25), j['acento'], 5)
    x0, x1 = pintar_texto(im, j['ante'][idioma], PEQUENA, BASE_W // 2, Y_ANTE, relleno, oscuro(j), aire=1)
    # dos trazos a los lados que se apagan hacia fuera a saltos
    q = im.load()
    for lado, borde in ((-1, x0 - 5), (1, x1 + 5)):
        for k in range(16):
            x = borde + lado * k
            if k >= 10 and k % 2 == 1:
                continue
            if k >= 13:
                continue
            q[x, Y_ANTE] = j['acento'] + (255,)
            q[x, Y_ANTE + 1] = SOMBRA
    return im


def capa_linea(j):
    im = lienzo()
    q = im.load()
    cx, cy = BASE_W // 2, Y_LINEA
    claro = mezcla(j['linea'], (255, 255, 255), 0.55)
    oscuro_ = oscuro(j) + (255,)

    def rombo(x0, r, nucleo):
        for dy in range(-r, r + 1):
            for dx in range(-(r - abs(dy)), r - abs(dy) + 1):
                c = claro if abs(dx) + abs(dy) <= nucleo else j['linea']
                q[x0 + dx, cy + dy] = c + (255,)
        for dy in range(-r - 1, r + 2):
            for dx in range(-(r + 1 - abs(dy)), r + 2 - abs(dy)):
                if q[x0 + dx, cy + dy][3] == 0:
                    q[x0 + dx, cy + dy] = oscuro_
    # la raya: sale pasado el rombo pequeno y se apaga hacia fuera a saltos
    for lado in (-1, 1):
        for k in range(10, 86):
            if k > 62 and k % 2 == 1:
                continue
            if k > 76 and k % 4 != 0:
                continue
            x = cx + lado * k
            c = claro if k < 20 else j['linea']
            q[x, cy] = c + (255,)
            q[x, cy + 1] = SOMBRA
    rombo(cx, 3, 1)
    rombo(cx - 7, 1, 0)
    rombo(cx + 7, 1, 0)
    return im


def ampliar(im, w):
    k = w // BASE_W
    return im.resize((BASE_W * k, BASE_H * k), Image.NEAREST)


def comprobar():
    """Que todo quepa en el lienzo (con su contorno)."""
    for nombre, j in JEFES.items():
        _, a, _ = puntos_texto(j['nombre'], GRANDE, 4, 1)
        assert a + 12 <= BASE_W, (nombre, 'nombre', a)
        for idioma in IDIOMAS:
            for clave, glifos in (('ante', PEQUENA),):
                aire = 1 if clave == 'ante' else 0
                _, a, _ = puntos_texto(j[clave][idioma], glifos, 1, aire)
                assert a + 4 <= BASE_W, (nombre, clave, idioma, a)


def vista(carpeta, capas):
    """Los cuatro a 480 sobre una captura del juego (854x480)."""
    capturas = sorted(glob.glob(os.path.join(CAPTURAS, '*.png')))
    fondo = Image.open(capturas[-1]).convert('RGBA').resize((854, 480)) if capturas else Image.new('RGBA', (854, 480), (90, 140, 200, 255))
    hoja = Image.new('RGB', (854 * 2, 480 * 4))
    for i, (jefe, idioma) in enumerate((('nerea', 'es'), ('aeralis', 'es'), ('rajang', 'es'), ('novilis', 'es'),
                                         ('nerea', 'en'), ('aeralis', 'en'), ('rajang', 'en'), ('novilis', 'en'))):
        f = fondo.copy()
        w = 480
        h = w // BASE_W * BASE_H
        x0, y0 = (854 - w) // 2, int(round(480 * 0.69 - h / 2))
        for nombre in (f'{jefe}_{w}_nombre', f'{jefe}_{w}_linea', f'{jefe}_{idioma}_{w}_ante'):
            f.alpha_composite(capas[nombre], (x0, y0))
        hoja.paste(f.convert('RGB'), ((i // 4) * 854, (i % 4) * 480))
    hoja.save(os.path.join(carpeta, 'presentacion_pixel_480.png'))


def main():
    comprobar()
    os.makedirs(SALIDA, exist_ok=True)
    capas = {}

    def guardar(nombre, im):
        capas[nombre] = im
        im.save(os.path.join(SALIDA, nombre + '.png'))

    for jefe, j in JEFES.items():
        base = {'nombre': capa_nombre(j), 'linea': capa_linea(j)}
        for idioma in IDIOMAS:
            base['ante_' + idioma] = capa_ante(j, idioma)
        for w in ANCHOS:
            guardar(f'{jefe}_{w}_nombre', ampliar(base['nombre'], w))
            guardar(f'{jefe}_{w}_linea', ampliar(base['linea'], w))
            for idioma in IDIOMAS:
                guardar(f'{jefe}_{idioma}_{w}_ante', ampliar(base['ante_' + idioma], w))
    print(len(capas), 'texturas en', SALIDA)
    if HOJA:
        vista(HOJA, capas)
        print('vista en', HOJA)


if __name__ == '__main__':
    main()

"""
El Momento Maldición (15-10-2026): nuestro «momento Reviil» de DEDsafío. Juan: «quiero que lo hagas mil veces
mejor, que me sorprendas». Los compañeros dejaron una idea (vídeo, sonido y música), pero aquí todo se crea: la
cinemática es nuestra (el Sello que se dibuja, el núcleo que se carga, la pantalla que revienta, sin texto) y se pinta
en el juego con trazos (MomentoMaldicionHud y CieloRoto). Este script hace:

  textures/item/momento_cartel_NN       el rótulo del aviso del chat, MOMENTO FRACTURA: en letras de metal rojo con
                                        un brillo que lo cruza (cuadros animados que el chat pinta seguidos)
  textures/item/momento_fractura        el icono del aviso (el sello rojo y rajado)
  textures/entity/momento/cielo         todo lo del cielo roto en una hoja (16-10-2026), para que el juego lo pinte de una
                                        tanda y en orden: la cinta de las grietas (suave de lado a lado), un blanco
                                        liso y la niebla de detrás del hueco
  textures/gui/momento/                 las piezas suaves de la cinemática (16-10-2026, para que nada se vea en cajas
                                        ni en escalones): el brillo, el disco, el haz de luz, el brillo de un trazo,
                                        la viñeta del latido y un triángulo suave que el juego estira (los trozos de
                                        cristal de la fractura), todas con su .mcmeta (blur)
  textures/gui/momento/reloj            el contador de la prueba (16-10-2026): los números y los dos puntos, blancos con
                                        su contorno oscuro (el juego los tiñe de rojo al final); sin blur, a píxeles
  textures/particle/maldicion_mota_N    las motas que suben en el mundo maldito (brasas rojas que parpadean)
  textures/particle/maldicion_ceniza_N  y la ceniza negra que cae, con sus JSON

Los sonidos y la música, momento_maldicion_sonidos.py.

Uso: python momento_maldicion.py <raiz del proyecto>
"""
import json
import math
import os
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'


def H(h, a=255):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


# ----------------------------------------------------------------------------------------------------------------
#  Las letras: las de las barras de vida (presentacion_jefes.py), 7 de alto y trazo de 2, con lo que le faltaba al
#  título y al reloj (números, signos, la diéresis).
# ----------------------------------------------------------------------------------------------------------------
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
    '0': [".####.", "##..##", "##.###", "######", "###.##", "##..##", ".####."],
    '1': ["..##..", ".###..", "####..", "..##..", "..##..", "..##..", "######"],
    '2': [".####.", "##..##", "....##", "...##.", "..##..", ".##...", "######"],
    '3': ["#####.", "....##", "....##", ".####.", "....##", "....##", "#####."],
    '4': ["...##.", "..###.", ".####.", "##.##.", "######", "...##.", "...##."],
    '5': ["######", "##....", "#####.", "....##", "....##", "##..##", ".####."],
    '6': [".####.", "##....", "##....", "#####.", "##..##", "##..##", ".####."],
    '7': ["######", "....##", "...##.", "..##..", "..##..", "..##..", "..##.."],
    '8': [".####.", "##..##", "##..##", ".####.", "##..##", "##..##", ".####."],
    '9': [".####.", "##..##", "##..##", ".#####", "....##", "....##", ".####."],
    '.': ["..", "..", "..", "..", "..", "##", "##"],
    ',': ["..", "..", "..", "..", "..", "##", ".#"],
    ':': ["..", "##", "##", "..", "##", "##", ".."],
    ';': ["..", "##", "##", "..", "##", "##", ".#"],
    '!': ["##", "##", "##", "##", "##", "..", "##"],
    '¡': ["##", "..", "##", "##", "##", "##", "##"],
    '?': [".####.", "##..##", "....##", "...##.", "..##..", "......", "..##.."],
    '¿': ["..##..", "......", "..##..", ".##...", "##....", "##..##", ".####."],
    '-': ["....", "....", "....", "####", "....", "....", "...."],
    "'": ["##", "##", ".#", "..", "..", "..", ".."],
    '"': ["##.##", "##.##", ".#..#", ".....", ".....", ".....", "....."],
    '/': ["....##", "....##", "...##.", "..##..", ".##...", "##....", "##...."],
    '(': [".##", "##.", "##.", "##.", "##.", "##.", ".##"],
    ')': ["##.", ".##", ".##", ".##", ".##", ".##", "##."],
    '#': [".##.##", "######", ".##.##", ".##.##", "######", ".##.##", "......"],
    ' ': ["...", "...", "...", "...", "...", "...", "..."],
}
TILDE_6 = ["...##.", "..##..", "......"]
for _b, _a in (('A', 'Á'), ('E', 'É'), ('O', 'Ó'), ('U', 'Ú')):
    GRANDE[_a] = TILDE_6 + GRANDE[_b]
GRANDE['Í'] = ["..##", ".##.", "...."] + GRANDE['I']
GRANDE['Ñ'] = [".##..#", "#..##.", "......"] + GRANDE['N']
GRANDE['Ü'] = ["##..##", "......"] + GRANDE['U']

# El alfabeto maldito: runas del mismo trazo que no son letras. El título sale primero escrito en ellas, que se
def comprobar():
    for k, g in GRANDE.items():
        assert len(g) in (7, 9, 10), (k, len(g))
        assert len({len(f) for f in g}) == 1, (k, [len(f) for f in g])


# ----------------------------------------------------------------------------------------------------------------
#  Las partículas del mundo maldito
# ----------------------------------------------------------------------------------------------------------------
MOTAS = [
    # La brasa maldita: un punto al rojo blanco con su halo, que late (tres cuadros).
    ['........', '........', '...rr...', '..rRRr..', '..rRRr..', '...rr...', '........', '........'],
    ['........', '...hh...', '..hRRh..', '.hRWWRh.', '.hRWWRh.', '..hRRh..', '...hh...', '........'],
    ['........', '........', '...hh...', '..hRRh..', '..hRRh..', '...hh...', '........', '........'],
]
CENIZAS = [
    ['........', '........', '..kk....', '..kKk...', '...kKk..', '....kr..', '........', '........'],
    ['........', '...k....', '..kKk...', '..kKKk..', '...kkr..', '........', '........', '........'],
    ['........', '........', '....kk..', '...kKk..', '..kKk...', '..rk....', '........', '........'],
]
PARTICULA = {'r': H('a01010'), 'R': H('ff3a20'), 'W': H('ffd8a0'), 'h': H('ff2010', 120), 'k': H('0c0406'),
             'K': H('241014'), }


def particulas():
    """Las texturas de las dos partículas del mundo maldito y sus JSON."""
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/particle')
    for nombre, cuadros in (('maldicion_mota', MOTAS), ('maldicion_ceniza', CENIZAS)):
        for k, filas in enumerate(cuadros):
            im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
            for y, f in enumerate(filas):
                for x, c in enumerate(f):
                    if c != '.':
                        im.putpixel((x, y), PARTICULA[c])
            im.save(os.path.join(carpeta, f'{nombre}_{k}.png'))
        ruta = os.path.join(RAIZ, f'src/main/resources/assets/atalaya/particles/{nombre}.json')
        with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'textures': [f'atalaya:{nombre}_{k}' for k in range(len(cuadros))]}, fh, indent=2)
            fh.write('\n')


# El icono del aviso del chat (16 x 16): un orbe rojo con el sello dentro, rajado y al rojo blanco por la grieta.
ICONO = [
    '................',
    '.....kkkkkk.....',
    '...kkRRrrRRkk...',
    '..kRRLrRrrRRRk..',
    '..kRLLRWrRrRRk..',
    '.kRRLRRrWrRrRRk.',
    '.kRrRrRrWWrRrRk.',
    '.kRRrRRRrWrRRRk.',
    '.kRrRrRRrWWrRrk.',
    '.kRRRrRRRrWrRRk.',
    '..kRRRrRrRWrRk..',
    '..kRRRRrRRrWRk..',
    '...kkRRRRRRkk...',
    '.....kkkkkk.....',
    '................',
    '................',
]
ICONO_COLOR = {'k': H('2a0406'), 'R': H('c81c1c'), 'r': H('801010'), 'L': H('ff7a60'), 'W': H('fff0d8')}


def icono():
    """El icono del chat, en textures/item (entra solo en el atlas de objetos)."""
    assert all(len(f) == 16 for f in ICONO)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, f in enumerate(ICONO):
        for x, c in enumerate(f):
            if c != '.':
                im.putpixel((x, y), ICONO_COLOR[c])
    im.save(os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item/momento_fractura.png'))


# ----------------------------------------------------------------------------------------------------------------
#  El rótulo del chat: MOMENTO FRACTURA: en letras de metal rojo con su brillo que pasa
# ----------------------------------------------------------------------------------------------------------------
# El chat pinta cada sprite como una letra de 8 de ancho, seguidas y sin hueco: el rótulo se parte en cuadros de 32 x 32
# (cuatro veces la letra normal), cada uno con la misma animación, así el brillo cruza el rótulo entero a la vez.
CARTEL = 'MOMENTO FRACTURA:'
CARTEL_ESC = 3
CARTEL_CUADROS = 36       # los cuadros de la animación (de 2 ticks): el brillo cruza en los 22 primeros
CARTEL_CRUZA = 22


def metal(v):
    """El color del metal rojo pulido a la altura v (0 arriba, 1 abajo): reflejo, rojo vivo, el horizonte oscuro,
    rojo hondo y el reflejo de abajo."""
    tramos = [(0.0, (255, 226, 214)), (0.14, (255, 120, 104)), (0.42, (226, 40, 52)), (0.48, (96, 8, 16)),
              (0.56, (150, 14, 24)), (0.84, (214, 44, 48)), (1.0, (255, 120, 88))]
    for (v0, c0), (v1, c1) in zip(tramos, tramos[1:]):
        if v <= v1:
            k = (v - v0) / (v1 - v0)
            return tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3))
    return tramos[-1][1]


def cartel():
    """El rótulo en metal: las letras de las barras a escala 3 con su bisel, contorno oscuro y halo rojo, y en cada
    cuadro de la animación una franja de luz en diagonal (con un destello en estrella) que lo cruza."""
    e = CARTEL_ESC
    ancho_txt = sum((len(GRANDE[c][0]) + 1) * e for c in CARTEL) - e
    cuadros = -(-(ancho_txt + 16) // 32)
    W, Hh = cuadros * 32, 32
    x0 = (W - ancho_txt) // 2
    y0 = 6
    # La máscara de las letras.
    dentro = [[False] * W for _ in range(Hh)]
    x = x0
    for c in CARTEL:
        g = GRANDE[c]
        for fy, fila in enumerate(g):
            for fx, ch in enumerate(fila):
                if ch == '#':
                    for dy in range(e):
                        for dx in range(e):
                            dentro[y0 + fy * e + dy][x + fx * e + dx] = True
        x += (len(g[0]) + 1) * e
    alto_letra = 7 * e

    def es(px, py):
        return 0 <= px < W and 0 <= py < Hh and dentro[py][px]

    import math
    tiras = [Image.new('RGBA', (32, 32 * CARTEL_CUADROS), (0, 0, 0, 0)) for _ in range(cuadros)]
    for f in range(CARTEL_CUADROS):
        im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
        # Por dónde va la franja de luz (fuera del rótulo en los cuadros de descanso).
        franja = -30 + (W + 60) * f / (CARTEL_CRUZA - 1) if f < CARTEL_CRUZA else -1000
        for py in range(Hh):
            for px in range(W):
                if es(px, py):
                    v = (py - y0) / (alto_letra - 1)
                    r, g, b = metal(v)
                    # Bisel: luz arriba a la izquierda, sombra abajo a la derecha.
                    if not es(px - 1, py) or not es(px, py - 1):
                        r, g, b = (min(255, int(c * 1.25 + 30)) for c in (r, g, b))
                    elif not es(px + 1, py) or not es(px, py + 1):
                        r, g, b = (int(c * 0.6) for c in (r, g, b))
                    d = abs(px - franja - (py - y0) * 0.55)
                    if d < 9:
                        k = (1 - d / 9) ** 1.3
                        r, g, b = (int(c + (255 - c) * k) for c in (r, g, b))
                    d2 = abs(px - (franja - 14) - (py - y0) * 0.55)
                    if d2 < 3:
                        k = (1 - d2 / 3) * 0.6
                        r, g, b = (int(c + (255 - c) * k) for c in (r, g, b))
                    im.putpixel((px, py), (r, g, b, 255))
                else:
                    # Contorno oscuro pegado a la letra y, más fuera, el halo rojo.
                    cerca = min((abs(dx) + abs(dy) for dx in range(-3, 4) for dy in range(-3, 4) if es(px + dx, py + dy)),
                                default=99)
                    if cerca <= 1:
                        im.putpixel((px, py), (26, 2, 6, 255))
                    elif cerca <= 4:
                        a = int(150 * (1 - (cerca - 1) / 4))
                        d = abs(px - franja - (py - y0) * 0.55)
                        brilla = max(0.0, 1 - d / 8)
                        im.putpixel((px, py), (255, int(32 + 150 * brilla), int(16 + 120 * brilla), min(255, a + int(80 * brilla))))
        # El destello en estrella en lo alto de la franja.
        if 0 <= franja < W:
            sx, sy = int(franja + 2), y0 + 2
            for k in range(-5, 6):
                for (px, py) in ((sx + k, sy), (sx, sy + k)):
                    if 0 <= px < W and 0 <= py < Hh:
                        a = int(255 * (1 - abs(k) / 6))
                        im.putpixel((px, py), (255, 250, 240, max(a, im.getpixel((px, py))[3])))
        for i in range(cuadros):
            tiras[i].paste(im.crop((i * 32, 0, i * 32 + 32, 32)), (0, f * 32))
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
    for viejo in os.listdir(carpeta):
        if viejo.startswith('momento_cartel_'):
            os.remove(os.path.join(carpeta, viejo))
    for i, tira in enumerate(tiras):
        ruta = os.path.join(carpeta, f'momento_cartel_{i:02d}.png')
        tira.save(ruta)
        with open(ruta + '.mcmeta', 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'animation': {'frametime': 2, 'interpolate': False}}, fh, indent=2)
            fh.write('\n')
    print('cartel:', cuadros, 'cuadros de 32 x 32,', CARTEL_CUADROS, 'fotogramas')
    return cuadros


def cielo():
    """La hoja del cielo roto (256 x 256, a píxeles, sin blur):

        y 0-31      (libre: los ojos son cuadrados rojos lisos, sin textura)
        x 0-127,    la niebla gris de detrás de los huecos (Juan: «otro espacio, negros y gris, no morado»): sin
        y 32-159    costura; el juego la pasea despacio en dos capas
        x 128-255,  la cinta de las grietas: blanca, opaca en el centro y que se desvanece hacia los lados (128 de
        y 32-63     ancho: no se ven escalones)
        x 128-255,  un blanco liso (los huecos, los trozos que caen, la pared de los huecos)
        y 64-95
    """
    import numpy as np
    hoja = np.zeros((256, 256, 4), np.uint8)
    hoja[32:160, 0:128] = _vacio()
    for x in range(128):
        d = abs(x - 63.5) / 63.5
        a = math.exp(-(d / 0.42) ** 2) if d < 0.98 else 0.0
        hoja[32:64, 128 + x] = (255, 255, 255, int(255 * min(1.0, a * 1.08)))
    hoja[64:96, 128:256] = (255, 255, 255, 255)
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/momento')
    os.makedirs(carpeta, exist_ok=True)
    Image.fromarray(hoja, 'RGBA').save(os.path.join(carpeta, 'cielo.png'))
    for viejo in ('grieta.png', 'grieta.png.mcmeta', 'ojos.png', 'vacio.png', 'vacio.png.mcmeta', 'cielo.png.mcmeta'):
        if os.path.exists(os.path.join(carpeta, viejo)):
            os.remove(os.path.join(carpeta, viejo))
    print('cielo: la hoja de 256 x 256')


def _mcmeta(ruta):
    """Que se estire suave (filtro lineal) y sin repetirse por los bordes."""
    with open(ruta + '.mcmeta', 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps({'texture': {'blur': True, 'clamp': True}}, indent=2) + '\n')


def _suave(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def hud():
    """Las piezas suaves de la cinemática (blancas: el juego les pone el color)."""
    from PIL import ImageDraw, ImageFilter
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/momento')
    os.makedirs(carpeta, exist_ok=True)

    def guardar(im, nombre):
        ruta = os.path.join(carpeta, nombre + '.png')
        im.save(ruta)
        _mcmeta(ruta)

    def campo(w, h, f):
        im = Image.new('RGBA', (w, h), (255, 255, 255, 0))
        px = im.load()
        for y in range(h):
            for x in range(w):
                px[x, y] = (255, 255, 255, int(round(255 * max(0.0, min(1.0, f(x, y))))))
        return im

    # el brillo: una campana redonda que se apaga en el borde
    guardar(campo(128, 128, lambda x, y: math.exp(-((math.hypot(x - 63.5, y - 63.5) / 63.5) / 0.42) ** 2)
                  * (1 - _suave(0.85, 1.0, math.hypot(x - 63.5, y - 63.5) / 63.5))), 'brillo')
    # el disco: lleno, con el borde suave (sin escalones)
    guardar(campo(256, 256, lambda x, y: 1 - _suave(0.965, 1.0, math.hypot(x - 127.5, y - 127.5) / 127.5)), 'disco')
    # el haz de luz: campana de lado a lado, que nace suave y se apaga hacia la punta
    guardar(campo(128, 32, lambda x, y: math.exp(-(abs(y - 15.5) / 15.5 / 0.45) ** 2) * _suave(0, 10, x)
                  * (1 - x / 127.0) ** 1.4), 'haz')
    # el brillo de un trazo: campana de lado a lado, con las puntas redondeadas
    guardar(campo(64, 16, lambda x, y: math.exp(-(abs(y - 7.5) / 7.5 / 0.45) ** 2) * _suave(0, 14, x)
                  * _suave(0, 14, 63 - x)), 'trazo')
    # la viñeta del latido: nada en buena parte del centro y el color solo hacia los bordes
    guardar(campo(256, 144, lambda x, y: _suave(0.72, 1.3, math.hypot((x - 127.5) / 127.5, (y - 71.5) / 71.5))),
            'vineta')
    # el triangulo: el de abajo a la izquierda de su cuadrado (de la esquina de arriba a la izquierda a las otras dos),
    # dibujado a 4x y reducido (el lado largo, suave): el juego lo estira a cualquier triangulo (los trozos de cristal
    # de la fractura)
    big = Image.new('L', (256, 256), 0)
    ImageDraw.Draw(big).polygon([(0, 0), (256, 0), (0, 256)], fill=255)
    tri = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
    tri.putalpha(big.resize((64, 64), Image.LANCZOS))
    guardar(tri, 'triangulo')
    for viejo in os.listdir(carpeta):
        if viejo.startswith('esquirla'):
            os.remove(os.path.join(carpeta, viejo))
    print('hud: brillo, disco, haz, trazo, vineta y triangulo')


RELOJ = '0123456789:'
RELOJ_CELDA = 28      # el ancho de cada número (todos iguales, para que el contador no baile); los dos puntos, 16
RELOJ_PUNTOS = 16
RELOJ_ALTO = 32


def reloj():
    """El contador de la prueba de la tierra, arriba en el centro de la pantalla (Juan, 16-10-2026: «el número debe
    ser más pequeño y de color blanco»): las letras de las barras a escala 3, blancas con un poco de bisel (el juego
    las tiñe de rojo en los diez últimos segundos), el contorno oscuro y una sombra suave para que se lean encima de
    cualquier cosa."""
    e, m = 3, 5
    anchos = [RELOJ_PUNTOS if c == ':' else RELOJ_CELDA for c in RELOJ]
    W = sum(anchos)
    im = Image.new('RGBA', (W, RELOJ_ALTO), (0, 0, 0, 0))
    x0 = 0
    for c, aw in zip(RELOJ, anchos):
        g = GRANDE[c]
        ox = x0 + (aw - len(g[0]) * e) // 2
        oy = m
        dentro = set()
        for fy, fila in enumerate(g):
            for fx, ch in enumerate(fila):
                if ch == '#':
                    for dy in range(e):
                        for dx in range(e):
                            dentro.add((ox + fx * e + dx, oy + fy * e + dy))
        alto = 7 * e
        for py in range(RELOJ_ALTO):
            for px in range(x0, x0 + aw):
                if (px, py) in dentro:
                    v = (py - oy) / (alto - 1)
                    k = int(255 - 40 * v)
                    if (px - 1, py) not in dentro or (px, py - 1) not in dentro:
                        k = 255
                    elif (px + 1, py) not in dentro or (px, py + 1) not in dentro:
                        k = int(k * 0.78)
                    im.putpixel((px, py), (k, k, k, 255))
                else:
                    cerca = min((abs(dx) + abs(dy) for dx in range(-3, 4) for dy in range(-3, 4)
                                 if (px + dx, py + dy) in dentro), default=99)
                    if cerca <= 1:
                        im.putpixel((px, py), (18, 8, 10, 255))
                    elif cerca <= 3:
                        im.putpixel((px, py), (0, 0, 0, int(110 * (1 - (cerca - 1) / 3))))
        x0 += aw
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/momento')
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, 'reloj.png')
    im.save(ruta)
    if os.path.exists(ruta + '.mcmeta'):
        os.remove(ruta + '.mcmeta')
    print('reloj:', W, 'x', RELOJ_ALTO)


def _vacio():
    """Lo que hay detrás de los huecos: una niebla gris sobre nada (transparente donde no hay niebla; el negro lo pone
    el juego debajo), en 128 x 128 y sin costura."""
    import numpy as np
    n = 128

    def capa(celdas, semilla):
        rng = np.random.default_rng(semilla)
        g = rng.random((celdas, celdas))
        t = np.arange(n) / n * celdas
        i0 = np.floor(t).astype(int) % celdas
        i1 = (i0 + 1) % celdas
        f = t - np.floor(t)
        f = f * f * (3 - 2 * f)
        fy = f[:, None]
        fx = f[None, :]
        a = g[i0][:, i0]
        b = g[i0][:, i1]
        c = g[i1][:, i0]
        d = g[i1][:, i1]
        return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy

    v = capa(4, 1) * 0.5 + capa(8, 2) * 0.3 + capa(16, 3) * 0.2
    densidad = np.clip((v - 0.42) / 0.38, 0, 1) ** 1.5
    tono = 0.75 + 0.25 * capa(16, 4)
    im = np.zeros((n, n, 4), np.uint8)
    for k, c in enumerate((150, 146, 150)):
        im[..., k] = np.clip(c * tono, 0, 255).astype(np.uint8)
    im[..., 3] = (densidad * 200).astype(np.uint8)
    # Unas motas lejanas, grises.
    rng = np.random.default_rng(5)
    for _ in range(22):
        x, y = rng.integers(0, n, 2)
        b = int(rng.uniform(150, 230))
        im[y, x] = (b, b, b, 255)
    return im



def main():
    comprobar()
    particulas()
    icono()
    cielo()
    hud()
    reloj()
    cartel()
    print('ok')


if __name__ == '__main__':
    main()

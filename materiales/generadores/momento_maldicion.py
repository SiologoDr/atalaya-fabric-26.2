"""
El Momento Maldición (15-10-2026): nuestro «momento Reviil» de DEDsafío. Juan: «quiero que lo hagas mil veces
mejor, que me sorprendas». Los compañeros dejaron una idea (vídeo, sonido y música), pero aquí todo se crea: la
cinemática es nuestra (el Sello que se dibuja, el núcleo que se carga, la pantalla que revienta, sin texto) y se pinta
en el juego sin texturas (MomentoMaldicionHud y CieloRoto). Este script hace solo:

  textures/item/momento_cartel_NN       el rótulo del aviso del chat, MOMENTO FRACTURA: en letras de metal rojo con
                                        un brillo que lo cruza (cuadros animados que el chat pinta seguidos)
  textures/item/momento_fractura        el icono del aviso (el sello rojo y rajado)
  textures/entity/momento/grieta        la cinta de las grietas del cielo
  textures/particle/maldicion_mota_N    las motas que suben en el mundo maldito (brasas rojas que parpadean)
  textures/particle/maldicion_ceniza_N  y la ceniza negra que cae, con sus JSON

Los sonidos y la música, momento_maldicion_sonidos.py.

Uso: python momento_maldicion.py <raiz del proyecto>
"""
import json
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


def grieta():
    """La cinta de las grietas del cielo (8 x 32): blanca, opaca en el centro y que se desvanece hacia los lados."""
    perfil = [0.0, 0.16, 0.42, 1.0, 1.0, 0.42, 0.16, 0.0]
    im = Image.new('RGBA', (8, 32), (0, 0, 0, 0))
    for x, a in enumerate(perfil):
        for y in range(32):
            im.putpixel((x, y), (255, 255, 255, int(255 * a)))
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/momento')
    os.makedirs(carpeta, exist_ok=True)
    im.save(os.path.join(carpeta, 'grieta.png'))


def main():
    comprobar()
    particulas()
    icono()
    grieta()
    cartel()
    print('ok')


if __name__ == '__main__':
    main()

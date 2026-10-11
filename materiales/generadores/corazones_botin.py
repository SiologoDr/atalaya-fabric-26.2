"""
Los corazones de los jefes (10-10-2026, Juan: "el drop de cada boss va a ser un
corazon de cada tipo y diseno de boss, que despues se va a usar para otra cosa;
por el momento va a estar sin utilidad"). Uno por jefe, con su paleta y lo suyo
dentro, y late (dos cuadros: "pum-pum" y una pausa):

  - corazon_nerea:   prismarina honda con una perla y la cadena que la ataba.
  - corazon_aeralis: alas palidas con el ocelo de sus alas y un rayo.
  - corazon_rajang:  jade con el meandro de oro de su templo.
  - corazon_novilis: brasa de oro con el sol en medio y grietas de lava.

Uso: python corazones_botin.py <raiz del proyecto>

(No confundir con corazones_jefes.py: esos son los del HUD del jugador.)
"""
import json
import os
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'

FORMA = [
    '................',
    '..OOOO....OOOO..',
    '.OxxxxO..OxxxxO.',
    'OxxxxxxOOxxxxxxO',
    'OxxxxxxxxxxxxxxO',
    'OxxxxxxxxxxxxxxO',
    'OxxxxxxxxxxxxxxO',
    '.OxxxxxxxxxxxxO.',
    '..OxxxxxxxxxxO..',
    '...OxxxxxxxxO...',
    '....OxxxxxxO....',
    '.....OxxxxO.....',
    '......OxxO......',
    '.......OO.......',
    '................',
    '................',
]

# Lo de dentro de cada uno (16 x 16, sobre la forma; '.' deja el relleno).
DIBUJOS = {
    'nerea': [
        '................',
        '................',
        '..ww............',
        '..wP........k...',
        '...........k.k..',
        '..........k.k...',
        '.........k.k....',
        '......pp.k......',
        '.....pPPp.......',
        '.....pPPp.......',
        '......pp........',
        '................',
        '................',
        '................',
        '................',
        '................',
    ],
    'aeralis': [
        '................',
        '................',
        '..ww............',
        '..w.........y...',
        '...........y....',
        '......aaa.yy....',
        '.....aKKKa.y....',
        '.....aKeKa......',
        '.....aKKKa......',
        '......aaa.......',
        '................',
        '................',
        '................',
        '................',
        '................',
        '................',
    ],
    'rajang': [
        '................',
        '................',
        '..ww............',
        '..w.............',
        '....ggggggg.....',
        '....g.....g.....',
        '....g.ggg.g.....',
        '....g.g.g.g.....',
        '....g.g...g.....',
        '....g.ggggg.....',
        '................',
        '................',
        '................',
        '................',
        '................',
        '................',
    ],
    'novilis': [
        '................',
        '................',
        '..ww............',
        '..w.....r.......',
        '.......r....r...',
        '......sss..r....',
        '.....sSSSs.r....',
        '.r...sSWSs......',
        '..r..sSSSs......',
        '..r...sss.......',
        '.......r........',
        '........r.......',
        '................',
        '................',
        '................',
        '................',
    ],
}

PALETAS = {
    # O canto, a/b relleno de arriba y de abajo, y lo del dibujo.
    'nerea': {'O': (12, 52, 62), 'a': (90, 210, 205), 'b': (28, 112, 120), 'w': (235, 255, 252), 'p': (200, 230, 240),
              'P': (250, 252, 255), 'k': (70, 80, 92)},
    'aeralis': {'O': (58, 38, 104), 'a': (240, 232, 255), 'b': (176, 146, 236), 'w': (255, 255, 255), 'y': (255, 240, 120),
                'K': (36, 22, 52), 'e': (250, 180, 60)},
    'rajang': {'O': (12, 46, 32), 'a': (96, 200, 140), 'b': (30, 110, 72), 'w': (210, 255, 225), 'g': (238, 190, 56)},
    'novilis': {'O': (70, 20, 10), 'a': (255, 200, 80), 'b': (214, 92, 24), 'w': (255, 250, 220), 'r': (150, 20, 12),
                's': (255, 214, 90), 'S': (255, 240, 170), 'W': (255, 255, 255)},
}


def mezclar(c1, c2, k):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))


def cuadro(jefe, latido):
    p = PALETAS[jefe]
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, fila in enumerate(FORMA):
        for x, ch in enumerate(fila):
            if ch == '.':
                continue
            if ch == 'O':
                c = p['O']
                if latido:
                    c = mezclar(c, p['a'], 0.35)
            else:
                c = mezclar(p['a'], p['b'], (y - 2) / 10.0)
                if latido:
                    c = mezclar(c, (255, 255, 255), 0.18)
            d = DIBUJOS[jefe][y][x]
            if d != '.' and ch == 'x':
                c = p[d]
                if latido:
                    c = mezclar(c, (255, 255, 255), 0.15)
            im.putpixel((x, y), c + (255,))
    return im


def main():
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
    for jefe in PALETAS:
        tira = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
        tira.paste(cuadro(jefe, False), (0, 0))
        tira.paste(cuadro(jefe, True), (0, 16))
        ruta = os.path.join(carpeta, f'corazon_{jefe}.png')
        tira.save(ruta)
        # Pum-pum y pausa.
        meta = {'animation': {'frames': [{'index': 0, 'time': 16}, {'index': 1, 'time': 3}, {'index': 0, 'time': 3},
                                         {'index': 1, 'time': 3}]}}
        with open(ruta + '.mcmeta', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(meta, f, indent=2)
            f.write('\n')
    print('ok')


if __name__ == '__main__':
    main()

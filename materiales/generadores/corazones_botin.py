"""
Los corazones de los jefes (10-10-2026, Juan: "el drop de cada boss va a ser un
corazon de cada tipo y diseno de boss, que despues se va a usar para otra cosa;
por el momento va a estar sin utilidad"). Es lo único que suelta cada jefe.

Los primeros "se veían muy simples" (11-10-2026). Juan eligió estos en la página
de propuestas y se mejoraron a partir de lo que eligió:

  - corazon_nerea:   prismarina con dos cadenas oxidadas en aspa (un eslabón de
                     frente en cada lóbulo), la perla donde se cruzan y las puntas
                     rotas colgando (el A).
  - corazon_aeralis: pálido, con sus alas de mariposa y el ocelo naranja, las
                     antenas y el ocelo de sus alas en el pecho (el A).
  - corazon_rajang:  jade en su marco de oro, con el meandro del templo y las
                     manchas del jaguar (el A).
  - corazon_novilis: oro al rojo con las llamas sobre los lóbulos (lenguas de
                     varias alturas que se avivan al latir; Juan: "mejora sus
                     llamas") y las grietas de lava al rojo blanco (el B).

Laten (dos cuadros: "pum-pum" y una pausa). Al latir se aclara el corazón (y lo
que brilla dentro); las cadenas, las alas y el marco se quedan quietos.

Uso: python corazones_botin.py <raiz del proyecto>

(No confundir con corazones_jefes.py: esos son los del HUD del jugador.)
"""
import json
import os
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'


def H(h):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# Cada corazón: su paleta, lo que late y el dibujo (16 x 16). En todos, O es el canto, L/A/B/C el relleno de la luz a
# la sombra y W el brillo del lóbulo.
CORAZONES = {
    # P/w/p/u la perla, K/k los eslabones (claro y oscuro), R el óxido de las puntas.
    'nerea': ({'O': H('0c343e'), 'L': H('9af0e8'), 'A': H('5ad2cd'), 'B': H('2a9a98'), 'W': H('ebfffc'), 'P': H('fafcff'),
               'w': H('ffffff'), 'p': H('b8d4e8'), 'u': H('7a98b4'), 'K': H('7a8696'), 'k': H('3a3e48'), 'R': H('b8683a')},
              'LABW', [
        '................',
        '..OOOO....OOOO..',
        '.OWWLLO..OAAAAO.',
        'OKKLLLAOOAAAAKKO',
        'OKLkLAAAAAAAKAkO',
        'OLkkAAAPPAAAkkBO',
        'OAAAKAPwPpAKBBBO',
        '.OAAAkPPpukBBBO.',
        '..OAAAkpukBBBO..',
        '...OAKBBBBKBO...',
        '....kBBBBBBk....',
        '...R.OBBBBO.R...',
        '......OBBO......',
        '.......OO.......',
        '................',
        '................',
    ]),
    # n/U/u/L las alas, o/e/y el ocelo, K las antenas y la pupila.
    'aeralis': ({'O': H('3a2668'), 'L': H('ffffff'), 'A': H('ece4ff'), 'B': H('c0a8f0'), 'W': H('ffffff'), 'n': H('5a3ea0'),
                 'U': H('d8f0ff'), 'u': H('9ad8ff'), 'o': H('ff8a3c'), 'e': H('f8b43c'), 'y': H('fff078'), 'K': H('241634')},
                'LABWey', [
        'nnn..y...y..nnn.',
        'nLUnn.K.K.nnULn.',
        'nUoUUn.K.nUUoUn.',
        'noKoUunKnuUoKon.',
        'nUoUuunKnuuUoUn.',
        '.nUuOOOKOOOuUn..',
        '..nOWWLOAAAOn...',
        '..OLWLKKKAAAO...',
        '..OLAKeyeKBBO...',
        '..OAAKyKyKBBO...',
        '...OAKeyeKBO....',
        '....OAKKKBO.....',
        '.....OBBBO......',
        '......OBO.......',
        '.......O........',
        '................',
    ]),
    # n/g/G el marco y el meandro de oro, C las manchas del jaguar.
    'rajang': ({'O': H('0c2e20'), 'L': H('9af0c0'), 'A': H('60c88c'), 'B': H('1e8a56'), 'C': H('125a38'), 'W': H('d2ffe1'),
                'n': H('8a5a10'), 'g': H('eebe38'), 'G': H('fff09a')},
               'LABCW', [
        '................',
        '..nnnn....nnnn..',
        '.ngGGgn..ngGGgn.',
        'ngWLLLgnngAACAgn',
        'nGLCLAgGGgACACGn',
        'ngLLAggggggABBgn',
        'ngACAgAAAAgBCBgn',
        '.ngAAgAggAgBBgn.',
        '..ngCgAAgAgCgn..',
        '...ngggggAggn...',
        '....ngBBBBgn....',
        '.....nggggn.....',
        '......ngGn......',
        '.......nn.......',
        '................',
        '................',
    ]),
    # q/R/f/y/Y las llamas (de la punta roja al corazón blanco), r/R/y la lava de las grietas (oscura por fuera, al
    # rojo blanco por dentro).
    'novilis': ({'O': H('461408'), 'L': H('fff4c0'), 'A': H('ffd060'), 'B': H('f0901c'), 'W': H('ffffff'), 'f': H('ff8a20'),
                 'q': H('c0280c'), 'r': H('961408'), 'R': H('ff5020'), 'y': H('ffe070'), 'Y': H('fffbe0')},
                'LABWRyY', [
        '...q.........q..',
        '..qR.q.....q.Rq.',
        '.qRfqRq...qRqfRq',
        '.RfyYyR..RyYyfR.',
        '.OWWLLO..OAAAAO.',
        'OLWLLLAOOrAAAAAO',
        'OLLLLAAArRAAAABO',
        'OLLrAAAAyrAABBBO',
        'OAAARrAARAABBrBO',
        '.OAAArRRyBBBRrO.',
        '..OAAABARrBRrO..',
        '...OABBByRrBO...',
        '....OBBBRBBO....',
        '.....OBBrBO.....',
        '......OBBO......',
        '.......OO.......',
    ]),
}


# Las filas que cambian al latir (además de aclararse): las llamas de Novilis se avivan.
LATIDO = {
    'novilis': {0: '..q..q.....q..q.', 1: '.qR.qR.....Rq.Rq', 2: '.RfqRfR...RfRqfR', 3: '.fyYYyf..fyYYyf.'},
}


def mezclar(c1, c2, k):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))


def cuadro(jefe, latido):
    paleta, late, dibujo = CORAZONES[jefe]
    if latido:
        dibujo = [LATIDO.get(jefe, {}).get(y, f) for y, f in enumerate(dibujo)]
    assert len(dibujo) == 16 and all(len(f) == 16 for f in dibujo), (jefe, [len(f) for f in dibujo])
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, fila in enumerate(dibujo):
        for x, ch in enumerate(fila):
            if ch == '.':
                continue
            c = paleta[ch]
            if latido and ch in late:
                c = mezclar(c, (255, 255, 255), 0.2)
            elif latido and ch == 'O':
                # El canto se hincha hacia el relleno.
                c = mezclar(c, paleta['B'], 0.3)
            im.putpixel((x, y), c + (255,))
    return im


def main():
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
    for jefe in CORAZONES:
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

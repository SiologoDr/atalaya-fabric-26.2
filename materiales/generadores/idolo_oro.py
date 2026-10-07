"""
El Idolo de Oro de Rajang (octubre de 2026): la estatuilla del jaguar que
arranca de su templo y lanza. Item de 16 x 16: la cabeza del jaguar sentado,
de oro, con los ojos de jade y el pedestal. Silueta escrita como datos y la
rampa del oro de su mascara (DISENO.md, puntos 3 y 4): canto oscuro, nucleo
claro, sin negro.

Uso: python idolo_oro.py <raiz del proyecto>
"""
import os
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'

DIBUJO = [
    '................',
    '...OO......OO...',
    '..OYGO....OGYO..',
    '..OGGGOOOOGGGO..',
    '..OGYYYYYYYYGO..',
    '.OGYWYYYYYYWYGO.',
    '.OGjJGYYYYGJjGO.',
    '.OGGGYYDDYYGGGO.',
    '..OGYYDDDDYYGO..',
    '..OGGYWYYWYGGO..',
    '...OGGGGGGGGO...',
    '...OGYYOOYYGO...',
    '..OGGYYOOYYGGO..',
    '..OGYYGOOGYYGO..',
    '.OOOOOOOOOOOOOO.',
    '.ODGGGGGGGGGGDO.',
]
COLOR = {
    'O': (110, 70, 16),     # canto
    'D': (150, 96, 22),     # sombra
    'G': (211, 154, 34),    # oro
    'Y': (255, 194, 58),    # oro claro
    'W': (255, 240, 168),   # brillo
    'J': (58, 168, 102),    # jade
    'j': (140, 255, 90),    # jade encendido
}


def main():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, fila in enumerate(DIBUJO):
        assert len(fila) == 16, (y, len(fila))
        for x, c in enumerate(fila):
            if c in COLOR:
                im.putpixel((x, y), COLOR[c] + (255,))
    p = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item/idolo_oro.png')
    im.save(p)
    print('ok', p)


if __name__ == '__main__':
    main()

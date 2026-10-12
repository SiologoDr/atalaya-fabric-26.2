"""
Los iconos de los objetos de apoyo (11-10-2026, Juan: "un item para reparar la armadura de un compañero, que no se
pueda a ti mismo, aparte de tener un item que te recupera todos los corazones"). Los eligió Juan en la página de
propuestas, con sus colores (no los de los tótems):

  - kit_reparacion: el yunque de bolsillo de hierro con la correa de cuero en la cintura (el D, sin asa).
  - corazon_vida:   un corazón que se come (antes era un elixir en un cáliz; Juan: "cambiémoslo a un corazón que se
                    pueda comer"): rojo y brillante entre dos alas de oro con sus plumas (el F, mejorado).

Uso: python objetos_apoyo.py <raiz del proyecto>
"""
import json
import os
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'


def H(h):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


ICONOS = {
    # El yunque de bolsillo, sin el asa (por sus huecos se colaba la luz en la mano).
    'kit_reparacion': ({'k': H('1e1e22'), 'n': H('3c3c44'), 'm': H('5a5a64'), 's': H('8c8c96'), 'l': H('b4b4be'), 'w': H('e2e2ea'), 'O': H('9a6a3a'), 't': H('7a4a2a')}, [
        '................',
        '................',
        '................',
        '................',
        '..kkkkkkkkkkkk..',
        '.kllwwllllllssk.',
        '..klllsssssmmk..',
        '...kkkmssmkkk...',
        '....ktOkkOtk....',
        '....ktOOOOtk....',
        '....kmlsssmk....',
        '...kmlsssssmk...',
        '..kmssssssssmk..',
        '..knnnnnnnnnnk..',
        '..kkkkkkkkkkkk..',
        '................',
    ]),
    # El corazón que se come, entre dos alas de oro (G/g/d las plumas, n el canto de las alas).
    'corazon_vida': ({'O': H('3a0a10'), 'L': H('ffb0b8'), 'A': H('ff5a6a'), 'B': H('d42a3a'), 'W': H('fff0f0'),
                      'G': H('fff0a0'), 'g': H('f2c844'), 'd': H('c89a2a'), 'n': H('8a5a10')}, [
        'G.............G.',
        'gG...........Gg.',
        'ngGG.......GGgn.',
        'dngGGG...GGGgnd.',
        '.dngGGG.GGGgnd..',
        'GGdnOOO.OOOndGG.',
        'gGGOWWLOAAAOGGg.',
        '.gOLWLAAAAAAOg..',
        '..OLAAAAAABBO...',
        '..OAAAAAABBBO...',
        '...OAAABBBBO....',
        '....OABBBBO.....',
        '.....OBBBO......',
        '......OBO.......',
        '.......O........',
        '................',
    ]),
}


def pintar(nombre):
    paleta, dibujo = ICONOS[nombre]
    assert len(dibujo) == 16 and all(len(f) == 16 for f in dibujo), (nombre, [len(f) for f in dibujo])
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, fila in enumerate(dibujo):
        for x, c in enumerate(fila):
            if c != '.':
                im.putpixel((x, y), (*paleta[c], 255))
    return im


def escribir():
    for nombre in ICONOS:
        pintar(nombre).save(os.path.join(RAIZ, f'src/main/resources/assets/atalaya/textures/item/{nombre}.png'))
        with open(os.path.join(RAIZ, f'src/main/resources/assets/atalaya/models/item/{nombre}.json'), 'w',
                  encoding='utf-8', newline='\n') as fh:
            json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': f'atalaya:item/{nombre}'}}, fh, indent=2)
            fh.write('\n')
        with open(os.path.join(RAIZ, f'src/main/resources/assets/atalaya/items/{nombre}.json'), 'w',
                  encoding='utf-8', newline='\n') as fh:
            json.dump({'model': {'type': 'minecraft:model', 'model': f'atalaya:item/{nombre}'}}, fh, indent=2)
            fh.write('\n')
        print(nombre)


if __name__ == '__main__':
    escribir()

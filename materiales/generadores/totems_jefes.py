"""
Los tótems del mod (11-10-2026, Juan: "agrega más tipos de tótem con todo lo que tenemos").

Los dibujos los eligió Juan en la página de propuestas («Tótems de Atalaya», cuatro tandas): figuritas de oro con la
paleta del tótem de la inmortalidad, la cara en sombra con dos ojos de esmeralda, el tocado de cada criatura y el
cuerpo de tótem con los brazos abiertos (o con su objeto al costado, como el de Yiatzo). La mayoría van "pulidos":
luz arriba a la izquierda, el brazo derecho en sombra y el contorno de abajo más oscuro.

Uso: python totems_jefes.py <raiz del proyecto>
"""
import json
import os
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'


def H(h):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# La paleta del tótem de la inmortalidad: a y c, los marrones del contorno; b, e y d, los dorados claros; f e i, los
# dorados de sombra; g y h, la esmeralda.
PALETA = {
    'a': H('a05b23'), 'b': H('eadb84'), 'c': H('85400f'), 'd': H('fdfbee'), 'e': H('f8eea5'), 'f': H('d1a75d'),
    'g': H('41e67f'), 'h': H('00bb46'), 'i': H('c58742'),
}

TOTEMS = {
    # Moctezuma: el penacho en abanico, el yelmo de águila con el pico sobre la cara en sombra y la gema del pecho.
    'moctezuma': [
        '..a.a.a..a.a.a..',
        '.aeaeaeaaeaeaea.',
        '.abebebeebebefc.',
        '..aabbbbbbbfac..',
        '...abffddfffc...',
        '...abcceeccbc...',
        '...abcgeegcbc...',
        '...abchiihcbc...',
        '....abccccbc....',
        '..aaaabbbbaaaa..',
        '.aeeebaggabfffa.',
        '.abbbabhhbaffia.',
        '..aaaabffbaaac..',
        '....abfbbfic....',
        '....abfaafic....',
        '....aaa..ccc....',
    ],
    # Yiatzo: la capucha en punta, la cara en sombra, la túnica y el bastón con el orbe.
    'yiatzo': [
        '.......a.....ag.',
        '......aba...aghg',
        '.....aeeba...ahc',
        '....aeebbba..cc.',
        '...aefffffba.cc.',
        '...abcccccbc.cc.',
        '...abcgccgfc.cc.',
        '...afchcchcfacc.',
        '..aabfccccffacc.',
        '.aebffbffbffbcc.',
        '.abfaibbbbiaccc.',
        '..aaabfeeffaacc.',
        '...aefibbifbacc.',
        '..aefifbbfifbcc.',
        '..afic.ff.aifcc.',
        '..ac.a.ac.a.ac..',
    ],
    # Atlahua: la corona de coral con perlas, las aletas y la barba de algas.
    'atlahua': [
        '..a..a....a..a..',
        '..ae.ea..ae.ea..',
        '...aeaaaaaaea...',
        '...abbbbbbbba...',
        '...adbdbbdbda...',
        '..aabccccccbaa..',
        '.aeabcgccgcbaea.',
        '..aabchcchcbaa..',
        '....aiaiiaia....',
        '..aaaabbbbaaaa..',
        '.abeebabbabeeba.',
        '.abbbabffbabbba.',
        '..aaaabffbaaaa..',
        '....abfbbfba....',
        '....abfaafba....',
        '....aaa..aaa....',
    ],
    # Xiuhquetzal: la cresta en tres llamas, la capucha de ave con el pico y las alas por brazos.
    'xiuhquetzal': [
        '..a....aa....a..',
        '..ea..aeba..ae..',
        '...ea.abfc.ae...',
        '....aaebbbac....',
        '...aebffffbba...',
        '...abccccccbc...',
        '...abcgccgcbc...',
        '...abchcchcbc...',
        '....abcddcbc....',
        '.a..aabbbbaa..a.',
        'aeaabeebbffbaafa',
        'aebbbbbffbbbbfia',
        '.abeaabffbaafic.',
        '..aa.abffba.cc..',
        '...abeaeeafic...',
        '...aa.a..c.cc...',
    ],
    # Nerea: la venera detrás, el cráneo en sombra y las cadenas de las muñecas.
    'nerea': [
        '....aaaaaaaa....',
        '..aaebebebebaa..',
        '.aebefbbbbfebea.',
        '.abeaabbbfaaefc.',
        '.aeaabffffbaaec.',
        '..aabccccccbac..',
        '...abcgccgcbc...',
        '...abchcchcbc...',
        '....abdcdcbc....',
        '..aaaabbbbaaaa..',
        '.aeeebaggabfffa.',
        '.abbbabhhbaffia.',
        '.caaaabffbaaacc.',
        '.a..abfbbfic..a.',
        '.c..abfaafic..c.',
        '....aaa..ccc....',
    ],
    # Rajang: la máscara de jaguar con las orejas, las manchas y los colmillos.
    'rajang': [
        '...aa......aa...',
        '..aeea....aeba..',
        '..abfaaaaaabfc..',
        '..abibbbbbbifc..',
        '..abfffffffffc..',
        '..abccccccccbc..',
        '..abcgccccgcbc..',
        '..abchcccchcbc..',
        '...acdccccdcc...',
        '..aaaabbbbaaaa..',
        '.aeeebaggabfffa.',
        '.abbbabhhbaffia.',
        '..aaaabffbaaac..',
        '....abfbbfic....',
        '....abfaafic....',
        '....aaa..ccc....',
    ],
    # Dos Vidas: la cara partida, un ojo abierto y otro cerrado.
    'dos_vidas': [
        '......aaaa......',
        '.....aeeeba.....',
        '....aebbbbba....',
        '...aeffbfffba...',
        '...abccbcccbc...',
        '...abcgfcccbc...',
        '...abchfcaacba..',
        '...abccbcccbc...',
        '....abcbccbc....',
        '..aaaabbbbaaaa..',
        '.aeeebabbabfffa.',
        '.abbbabffbaffia.',
        '..aaaabffbaaac..',
        '....abfbbfic....',
        '....abfaafic....',
        '....aaa..ccc....',
    ],
    # El Viajero: el sombrero de ala ancha y la cara en su sombra.
    'viajero': [
        '......aaaa......',
        '.....abeeba.....',
        '.....abbbba.....',
        '.aaaaabbbbaaaaa.',
        'abeebbbbbbbbbbba',
        '.aaaaccccccaaaa.',
        '....acgccgca....',
        '....achcchca....',
        '.....acccca.....',
        '..aaaabbbbaaaa..',
        '.abeebaggabeeba.',
        '.abbbabhhbabbba.',
        '..aaaabffbaaaa..',
        '....abfbbfba....',
        '....abfaafba....',
        '....aaa..aaa....',
    ],
    # Aeralis: las antenas, la capucha y las alas de mariposa por brazos.
    'aeralis': [
        '...a........a...',
        '....a......a....',
        '.....a.aa.a.....',
        '......aeba......',
        '.....aeebba.....',
        '....aefeffba....',
        '....abccccbc....',
        '....acgccgcc....',
        '....achcchcc....',
        'aaa..abbbba..aaa',
        'abeaabeebbfbaafc',
        'abgbbbbffbbbbhfc',
        'abhbaabffbaabgfc',
        '.abba.abfba.afc.',
        '..aa.abfafic.c..',
        '.....aaa.cc.....',
    ],
    # Novilis: el yelmo con el penacho que cae hacia atrás y su espada.
    'novilis': [
        '......aaaa...aa.',
        '.....aeeeba.adda',
        '......aaefc.adea',
        '.....aaefac.adea',
        '....abbffbbaadea',
        '...abccccccbadea',
        '...abcgccgcbadea',
        '...abchcchcbadea',
        '....abccccbcadea',
        '..aaaabbbbaabdea',
        '.aeeebabbabffaaa',
        '.abbbabffbaffica',
        '..aaaabffbaaaca.',
        '....abfbbfic.aa.',
        '....abfaafic....',
        '....aaa..ccc....',
    ],
}


def pintar(nombre):
    dibujo = TOTEMS[nombre]
    assert len(dibujo) == 16 and all(len(f) == 16 for f in dibujo), (nombre, [len(f) for f in dibujo])
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, fila in enumerate(dibujo):
        for x, c in enumerate(fila):
            if c != '.':
                im.putpixel((x, y), (*PALETA[c], 255))
    return im


def escribir():
    tex = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
    modelos = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/models/item')
    items = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/items')
    for nombre in TOTEMS:
        n = f'totem_{nombre}'
        pintar(nombre).save(os.path.join(tex, n + '.png'))
        with open(os.path.join(modelos, n + '.json'), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': f'atalaya:item/{n}'}}, fh, indent=2)
            fh.write('\n')
        with open(os.path.join(items, n + '.json'), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'model': {'type': 'minecraft:model', 'model': f'atalaya:item/{n}'}}, fh, indent=2)
            fh.write('\n')
        print(n)


if __name__ == '__main__':
    escribir()

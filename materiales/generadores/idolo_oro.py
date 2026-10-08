"""
El Idolo de Oro de Rajang (octubre de 2026): la estatuilla del jaguar que
arranca de su templo y lanza.

  - El icono del inventario (16 x 16): la cabeza del jaguar sentado, de oro,
    con los ojos de jade y el pedestal. Silueta escrita como datos y la rampa
    del oro de su mascara (DISENO.md, puntos 3 y 4): canto oscuro, nucleo
    claro, sin negro.
  - El idolo en 3D (08-10-2026, Juan: "mejora el idolo haz un diseno 3d"): el
    jaguar sentado sobre su pedestal de dos gradas, hecho por piezas (cabeza
    con hocico y orejas, pecho con el sol de jade, patas delanteras con las
    garras, la cola enroscada en la grada) con su textura de 64 x 64 a un pixel
    por dieciseisavo, las manchas del jaguar en el oro. Es el modelo del
    objeto en la mano, tirado en el suelo, en la cabeza de quien lo lleva y
    sobre el pilar (en el inventario sigue el icono).
  - El pilar del altar (08-10-2026, Juan: "donde debe poner el idolo debe ser
    en un pilar pequeno, corto"): zocalo de jade, fuste de jade con el jaguar
    tallado en oro, capitel de oro con el hueco del idolo. altar_pilar.png y
    altar_pilar_brillo.png (las vetas que brillan mientras espera el idolo);
    AltarIdoloRenderer lo monta con la misma medida.

Uso: python idolo_oro.py <raiz del proyecto>
"""
import json
import os
import random
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
    # el jade de la piedra del pilar (el de los totems del Sello, algo mas claro)
    'k': (16, 30, 21),      # junta
    'n': (27, 49, 34),      # jade oscuro
    'm': (36, 66, 45),      # jade
    'l': (50, 90, 61),      # jade claro
}


def icono():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, fila in enumerate(DIBUJO):
        assert len(fila) == 16, (y, len(fila))
        for x, c in enumerate(fila):
            if c in COLOR:
                im.putpixel((x, y), COLOR[c] + (255,))
    return im


# ----------------------------------------------------------------------
#  El idolo en 3D
# ----------------------------------------------------------------------
# Cada pieza: nombre, desde, hasta (en dieciseisavos; el frente mira al norte,
# -z) y la materia de sus caras. Las caras con dibujo propio van en CARAS
# (vistas desde fuera, la fila de arriba es la de arriba).
PIEZAS = [
    ('base', (2, 0, 2), (14, 2, 14), 'pedestal'),
    ('grada', (3, 2, 3), (13, 3, 13), 'grada'),
    ('cuerpo', (5, 3, 5), (11, 9, 11), 'oro'),
    ('pata_izq', (5, 3, 3), (7, 7, 5), 'oro'),
    ('pata_der', (9, 3, 3), (11, 7, 5), 'oro'),
    ('cabeza', (4, 9, 3), (12, 14, 9), 'oro'),
    ('hocico', (6, 9, 2), (10, 11, 3), 'oro'),
    ('oreja_izq', (4, 14, 5), (6, 16, 7), 'oro'),
    ('oreja_der', (10, 14, 5), (12, 16, 7), 'oro'),
    ('cola', (11, 3, 6), (12, 4, 12), 'cola'),
    ('cola_punta', (8, 3, 11), (11, 4, 12), 'cola'),
]

CARAS = {
    ('cabeza', 'north'): [
        'GYYjjYYG',
        'OjJGGJjO',
        'GYYYYYYG',
        'GGYYYYGG',
        'OGGDDGGO',
    ],
    ('hocico', 'north'): [
        'YDDY',
        'WOOW',
    ],
    ('hocico', 'up'): ['YWWY'],
    ('cuerpo', 'north'): [
        'GYYYYG',
        'GYWWYG',
        'GWjjWG',
        'GWJJWG',
        'GYWWYG',
        'GGYYGG',
    ],
    ('pata_izq', 'north'): ['YG', 'GG', 'GD', 'WW'],
    ('pata_der', 'north'): ['GY', 'GG', 'DG', 'WW'],
    ('oreja_izq', 'north'): ['YG', 'DG'],
    ('oreja_der', 'north'): ['GY', 'GD'],
    ('base', 'north'): [
        'ODGYGDjDGYGD',
        'OODDOOJOODDO',
    ],
    ('grada', 'north'): ['GYGYGWWGYGYG'[:10]],
}

TEX = 64
rng = random.Random(1008)


def manchas(w, h, base, sem):
    """Oro con las rosetas del jaguar (anillos de sombra con el centro algo mas oscuro)."""
    r = random.Random(sem)
    img = [[base for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if r.random() < 0.1:
                img[y][x] = 'Y'
    n = max(1, (w * h) // 14)
    for _ in range(n):
        cx, cy = r.randrange(w), r.randrange(h)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            if 0 <= cx + dx < w and 0 <= cy + dy < h and r.random() < 0.8:
                img[cy + dy][cx + dx] = 'D'
    return img


def materia(nombre, cara, w, h, sem):
    if nombre == 'oro':
        img = manchas(w, h, 'G', sem)
        if cara not in ('up', 'down') and h > 1:
            # El canto de abajo, mas oscuro; el de arriba con brillo.
            img[-1] = ['D' if c != 'O' else c for c in img[-1]]
            img[0] = ['Y' if c == 'G' else c for c in img[0]]
        return img
    if nombre == 'cola':
        return [['D' if (x + y) % 3 == 0 else 'G' for x in range(w)] for y in range(h)]
    if nombre == 'grada':
        return [['Y' if (x + y) % 2 == 0 else 'G' for x in range(w)] for y in range(h)]
    if nombre == 'pedestal':
        if cara == 'up':
            # Por arriba se ve el borde de la base alrededor de la grada: oro con greca.
            return [['Y' if (x == 0 or y == 0 or x == w - 1 or y == h - 1) else ('G' if (x + y) % 2 else 'D')
                     for x in range(w)] for y in range(h)]
        if cara == 'down':
            return [['O'] * w for _ in range(h)]
        fila0 = ''.join('ODGY'[(x * 3) % 4] if x not in (0, w - 1) else 'O' for x in range(w))
        return [list(fila0)[:w], ['O'] * w][:h]
    raise ValueError(nombre)


def colocar(rects, w, h):
    """Estantes: devuelve (u, v) libre de w x h en la textura de TEX x TEX."""
    x, y, alto = colocar.x, colocar.y, colocar.alto
    if x + w > TEX:
        x, y, alto = 0, y + alto, 0
    assert y + h <= TEX, 'no cabe la textura del idolo'
    colocar.x, colocar.y, colocar.alto = x + w, y, max(alto, h)
    return x, y


colocar.x = colocar.y = colocar.alto = 0


def idolo_3d():
    tex = Image.new('RGBA', (TEX, TEX), (0, 0, 0, 0))
    elementos = []
    caras_orden = ['north', 'south', 'east', 'west', 'up', 'down']
    # Primero las mas anchas, para que el estante quede apretado.
    trabajos = []
    for nombre, a, b, mat in PIEZAS:
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        dim = {'north': (dx, dy), 'south': (dx, dy), 'east': (dz, dy), 'west': (dz, dy), 'up': (dx, dz), 'down': (dx, dz)}
        for cara in caras_orden:
            trabajos.append((nombre, cara, dim[cara], mat))
    trabajos.sort(key=lambda t: -t[2][1])
    uvs = {}
    for k, (nombre, cara, (w, h), mat) in enumerate(trabajos):
        u, v = colocar(None, w, h)
        dibujo = CARAS.get((nombre, cara))
        if dibujo is not None:
            assert len(dibujo) == h and all(len(f) == w for f in dibujo), (nombre, cara, w, h)
            img = [list(f) for f in dibujo]
        else:
            img = materia(mat, cara, w, h, 1000 + k)
        for y in range(h):
            for x in range(w):
                tex.putpixel((u + x, v + y), COLOR[img[y][x]] + (255,))
        uvs[(nombre, cara)] = [u / 4.0, v / 4.0, (u + w) / 4.0, (v + h) / 4.0]
    for nombre, a, b, mat in PIEZAS:
        caras = {}
        for cara in caras_orden:
            # Las caras tapadas del todo (la de abajo de las piezas que pisan otra) se quitan.
            if cara == 'down' and nombre not in ('base', 'cabeza', 'hocico'):
                continue
            caras[cara] = {'uv': uvs[(nombre, cara)], 'texture': '#idolo'}
        elementos.append({'name': nombre, 'from': list(a), 'to': list(b), 'faces': caras})
    modelo = {
        'textures': {'idolo': 'atalaya:item/idolo_oro_3d', 'particle': 'atalaya:item/idolo_oro'},
        'elements': elementos,
        'display': {
            'thirdperson_righthand': {'rotation': [0, 45, 0], 'translation': [0, 2.5, 0], 'scale': [0.4, 0.4, 0.4]},
            'thirdperson_lefthand': {'rotation': [0, 225, 0], 'translation': [0, 2.5, 0], 'scale': [0.4, 0.4, 0.4]},
            'firstperson_righthand': {'rotation': [0, 135, 0], 'translation': [1, 0, 0], 'scale': [0.3, 0.3, 0.3]},
            'firstperson_lefthand': {'rotation': [0, 225, 0], 'translation': [1, 0, 0], 'scale': [0.3, 0.3, 0.3]},
            'ground': {'rotation': [0, 0, 0], 'translation': [0, 3, 0], 'scale': [0.6, 0.6, 0.6]},
            'gui': {'rotation': [20, 160, 0], 'translation': [0, 0, 0], 'scale': [0.75, 0.75, 0.75]},
            'head': {'rotation': [0, 180, 0], 'translation': [0, 13, 0], 'scale': [0.9, 0.9, 0.9]},
            # Fijo: tal cual (lo pintan la cabeza del portador y el pilar, con su escala y su giro).
            'fixed': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [1, 1, 1]},
        },
    }
    return tex, modelo


# ----------------------------------------------------------------------
#  El pilar del altar (64 x 64). Medidas en dieciseisavos, como en
#  AltarIdoloRenderer: zocalo 23 x 4, fuste 16 x 13, capitel 21 x 4; las tapas
#  del capitel (21 x 21) y del zocalo (23 x 23).
# ----------------------------------------------------------------------
PILAR = {
    'fuste': (0, 0, 16, 13),
    'zocalo': (0, 16, 23, 4),
    'capitel': (0, 24, 21, 4),
    'capitel_tapa': (24, 0, 21, 21),
    'zocalo_tapa': (24, 24, 23, 23),
}

# El jaguar tallado en el fuste (16 x 13): la cabeza de frente en lineas de oro.
FUSTE = [
    'kmmlmmmnmmmlmmmk',
    'kmY.mmmmmmmm.Ymk',
    'kmYY.mmmmmm.YYmk',
    'kmYGYYYYYYYYGYmk',
    'kmY.jm.mm.mj.Ymk',
    'kmY.mm.mm.mm.Ymk',
    'kmmY.mYYYYm.Ymmk',
    'kmmmY.mWWm.Ymmmk',
    'kmmmmYYmmYYmmmmk',
    'kmlmmmmmmmmmmlmk',
    'kmmnmmlmmlmmnmmk',
    'kYGYGYGYGYGYGYGk',
    'kkkkkkkkkkkkkkkk',
]


def pilar():
    r = random.Random(4417)
    tex = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    brillo = Image.new('RGBA', (64, 64), (0, 0, 0, 255))

    def pon(x, y, c, luce=False):
        tex.putpixel((x, y), COLOR[c] + (255,))
        if luce:
            brillo.putpixel((x, y), tuple(int(v * 0.85) for v in COLOR[c]) + (255,))

    # Fuste: la piedra de jade (los puntos de FUSTE son jade al azar) con el jaguar.
    u0, v0, w, h = PILAR['fuste']
    for y, fila in enumerate(FUSTE):
        assert len(fila) == w, (y, len(fila))
        for x, c in enumerate(fila):
            if c == '.':
                c = r.choice('mmnl')
            pon(u0 + x, v0 + y, c, luce=c in 'YGWj')
    # Zocalo: jade oscuro con junta y una greca de oro arriba.
    u0, v0, w, h = PILAR['zocalo']
    for y in range(h):
        for x in range(w):
            if y == 0:
                c = 'Y' if x % 2 == 0 else 'G'
            elif y == h - 1:
                c = 'k'
            else:
                c = r.choice('nnm') if x % 6 else 'k'
            pon(u0 + x, v0 + y, c, luce=(y == 0))
    # Capitel: oro con canto oscuro abajo y brillo arriba.
    u0, v0, w, h = PILAR['capitel']
    for y in range(h):
        for x in range(w):
            c = 'W' if y == 0 and x % 4 == 1 else 'Y' if y == 0 else 'O' if y == h - 1 else ('G' if (x + y) % 3 else 'D')
            pon(u0 + x, v0 + y, c, luce=(y == 0))
    # Tapa del capitel: oro, con el hueco del idolo (el cuadro de su base, 12 x 12) en jade.
    u0, v0, w, h = PILAR['capitel_tapa']
    for y in range(h):
        for x in range(w):
            borde = x in (0, w - 1) or y in (0, h - 1)
            dentro = 4 <= x <= w - 5 and 4 <= y <= h - 5
            filo = dentro and (x in (4, w - 5) or y in (4, h - 5))
            if borde:
                c = 'O'
            elif filo:
                c = 'j'
            elif dentro:
                c = r.choice('mml')
            else:
                c = 'Y' if (x + y) % 2 else 'G'
            pon(u0 + x, v0 + y, c, luce=filo)
    # Tapa del zocalo (y por debajo): jade con las juntas.
    u0, v0, w, h = PILAR['zocalo_tapa']
    for y in range(h):
        for x in range(w):
            c = 'k' if x in (0, w - 1) or y in (0, h - 1) or (x % 8 == 0) else r.choice('nnm')
            pon(u0 + x, v0 + y, c)
    return tex, brillo


def main():
    base = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
    icono().save(os.path.join(base, 'textures/item/idolo_oro.png'))
    tex, modelo = idolo_3d()
    tex.save(os.path.join(base, 'textures/item/idolo_oro_3d.png'))
    with open(os.path.join(base, 'models/item/idolo_oro_3d.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(modelo, f, indent=2)
        f.write('\n')
    # En el inventario, el icono; en todo lo demas, el idolo en 3D.
    definicion = {'model': {
        'type': 'minecraft:select',
        'property': 'minecraft:display_context',
        'cases': [{'when': 'gui', 'model': {'type': 'minecraft:model', 'model': 'atalaya:item/idolo_oro'}}],
        'fallback': {'type': 'minecraft:model', 'model': 'atalaya:item/idolo_oro_3d'},
    }}
    with open(os.path.join(base, 'items/idolo_oro.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(definicion, f, indent=2)
        f.write('\n')
    tex, brillo = pilar()
    tex.save(os.path.join(base, 'textures/entity/rajang/altar_pilar.png'))
    brillo.save(os.path.join(base, 'textures/entity/rajang/altar_pilar_brillo.png'))
    print('ok')


if __name__ == '__main__':
    main()

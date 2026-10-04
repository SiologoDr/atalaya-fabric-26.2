"""
Huevos generadores del Vigia, de Nerea y de Aeralis, dibujados pixel a pixel (16x16).

Siguen el estilo de los huevos de vanilla de 26.x: la misma silueta y la luz
desde arriba a la izquierda, con contorno de dos tonos, y encima los rasgos
de cada uno, que se salen de la silueta como los cuernos del Warden o las
puas del guardian:

  Vigia   tela oscura, sus dos antenas, el gran ojo ambar que maldice y las
          costillas de hueso con la brasa roja dentro; el bajo deshilachado
  Nerea   prismarina, la corona de coral, la calavera de hueso con los ojos
          cian, la cadena oxidada que le cruza el pecho y el corazon maldito
  Aeralis quitina azul pizarra, las alas de viento que asoman por los lados,
          las antenas con la punta encendida, los ojos cian y el ojo de la
          tormenta en el pecho

Uso: python huevos_jefes.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image
import os, sys, random

RAIZ = sys.argv[1]
ITEM = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')


def hexc(s):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


# La silueta del huevo de vanilla (12 de ancho, 14 de alto), una fila mas
# abajo para dejar sitio arriba a lo que sobresale: (fila, desde, hasta).
SILUETA = [(2, 6, 9), (3, 5, 10), (4, 4, 11), (5, 3, 12), (6, 3, 12), (7, 2, 13), (8, 2, 13), (9, 2, 13),
           (10, 2, 13), (11, 2, 13), (12, 2, 13), (13, 3, 12), (14, 4, 11), (15, 5, 10)]
DENTRO = {(x, y) for (y, a, b) in SILUETA for x in range(a, b + 1)}


def cascara(rampa, borde_luz, borde_sombra, semilla):
    """El huevo liso: contorno claro arriba-izquierda y oscuro abajo-derecha,
    y la cascara sombreada desde arriba a la izquierda, con algo de grano."""
    r = random.Random(semilla)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    p = im.load()
    for (x, y) in DENTRO:
        fuera = [(x + dx, y + dy) not in DENTRO for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1))]
        if any(fuera):
            p[x, y] = borde_luz if (fuera[0] or fuera[1]) and not (fuera[2] or fuera[3]) else borde_sombra
            continue
        luz = 0.62 - 0.075 * (x - 7.5) - 0.05 * (y - 8.5) + r.uniform(-0.09, 0.09)
        k = max(0, min(len(rampa) - 1, int(luz * len(rampa))))
        p[x, y] = rampa[k]
    return im


def pintar(im, dibujo, paleta):
    """Encima de la cascara: cada letra del dibujo es un color; '.' deja la cascara."""
    p = im.load()
    assert len(dibujo) == 16 and all(len(f) == 16 for f in dibujo), [len(f) for f in dibujo]
    for y, fila in enumerate(dibujo):
        for x, c in enumerate(fila):
            if c != '.':
                p[x, y] = paleta[c]
    return im


# ---------------------------------------------------------------- Vigia
VIGIA = {
    'o': hexc('2a2631'), 'O': hexc('120e10'),                       # contorno
    '1': hexc('2a2631'), '2': hexc('38333f'), '3': hexc('48424f'), '4': hexc('5a5363'),
    'b': hexc('c7bda3'), 'B': hexc('a39880'), 'h': hexc('e6dcc0'),  # hueso
    'e': hexc('fff0a8'), 'E': hexc('ffb43a'), 'x': hexc('c86a14'), 'X': hexc('6a3a0c'),  # el ojo
    'w': hexc('554638'), 'W': hexc('3a2816'),                       # antenas
    's': hexc('ffd36a'),                                            # chispa
    'r': hexc('ff5a2a'), 'R': hexc('a8261a'),                       # brasa en las costillas
}
vigia = cascara([VIGIA['1'], VIGIA['2'], VIGIA['2'], VIGIA['3'], VIGIA['4']], VIGIA['o'], VIGIA['O'], 'vigia')
pintar(vigia, [
    "...s........s...",
    "...w........w...",
    "....w......w....",
    ".....W....W.....",
    "......XXXX......",
    ".....XxEExX.....",
    "....XxEeeExX....",
    "....XxEeeExX....",
    ".....XxxxxX.....",
    "................",
    "....B..bb..B....",
    "...B.r.bh.r.B...",
    "...B..rbbr..B...",
    "....B..bb..B....",
    "....1O1O1O1O....",
    ".....O.O.O.O....",
], VIGIA)
# El bajo deshilachado: los huecos de la ultima fila son transparentes.
p = vigia.load()
for x in (6, 8, 10):
    p[x, 15] = (0, 0, 0, 0)
p[11, 15] = VIGIA['O']
vigia.save(os.path.join(ITEM, 'huevo_vigia.png'))

# ---------------------------------------------------------------- Nerea
NEREA = {
    'o': hexc('143532'), 'O': hexc('0b1f21'),                       # contorno
    '1': hexc('1d4a46'), '2': hexc('2a5c54'), '3': hexc('3b8075'), '4': hexc('5aa596'), '5': hexc('8fd0bd'),
    'b': hexc('d3c9aa'), 'B': hexc('97907a'), 'h': hexc('ece4c8'),  # hueso
    'c': hexc('d8336a'), 'C': hexc('a8204a'), 'k': hexc('f2618f'), 'K': hexc('7a1636'),  # coral
    'e': hexc('e8fffa'), 'E': hexc('3fe0cc'),                       # ojos
    'r': hexc('ff6a8e'), 'R': hexc('e0144c'), 'D': hexc('220410'),  # corazon y pecho
    'q': hexc('c47a3a'), 'Q': hexc('6e3c1e'),                       # cadena
}
nerea = cascara([NEREA['1'], NEREA['2'], NEREA['3'], NEREA['3'], NEREA['4']], NEREA['o'], NEREA['O'], 'nerea')
pintar(nerea, [
    "....k..kk..k....",
    "...kc..cc..ck...",
    "....cC.CC.Cc....",
    ".....KCKKCK.....",
    ".....BbhhbB.....",
    "....bEebbeEb....",
    "....BbbBBbbB....",
    ".....bDbbDb.....",
    "................",
    ".QqqQqqQQqqQqqQ.",
    "................",
    ".....rR..Rr.....",
    ".....RRRRRR.....",
    "......RRRR......",
    ".......RR.......",
    "................",
], NEREA)
# La cadena le cruza el pecho y se sale por los lados; debajo, el corazon.
nerea.save(os.path.join(ITEM, 'huevo_nerea.png'))

# ---------------------------------------------------------------- Aeralis
AERALIS = {
    'o': hexc('1f2738'), 'O': hexc('0b0f18'),                       # contorno
    '1': hexc('141a26'), '2': hexc('1f2738'), '3': hexc('2b3550'), '4': hexc('3c4a6c'),
    'p': hexc('b8c3d7'), 'P': hexc('8592ac'),                       # pelaje del collar
    'a': hexc('2b3550'), 'k': hexc('f2ffff'),                       # antenas y su punta encendida
    'E': hexc('5fd2ff'), 'e': hexc('e8fbff'),                       # ojos compuestos
    'm': hexc('dff2ff'), 'M': hexc('6fa8d8'), 'c': hexc('5fd2ff'),  # alas de viento y su ocelo
    'n': hexc('5fd2ff'), 'N': hexc('f2ffff'),                       # el ojo de la tormenta
}
aeralis = cascara([AERALIS['1'], AERALIS['2'], AERALIS['3'], AERALIS['3'], AERALIS['4']], AERALIS['o'], AERALIS['O'], 'aeralis')
pintar(aeralis, [
    "...k........k...",
    "...a........a...",
    "....a......a....",
    ".....a....a.....",
    ".....PppppP.....",
    ".M...EeppeE...M.",
    "MmM..EEppEE..MmM",
    "MmcM...PP...McmM",
    "MmmM..NnnN..MmmM",
    ".MmM..nNNn..MmM.",
    ".MmmM......MmmM.",
    "..MmM......MmM..",
    "...MM......MM...",
    "................",
    "................",
    "................",
], AERALIS)
aeralis.save(os.path.join(ITEM, 'huevo_aeralis.png'))

if len(sys.argv) > 2:
    VAN = sys.argv[3] if len(sys.argv) > 3 else None
    fila = [vigia, nerea, aeralis]
    if VAN:
        for f in ('warden', 'guardian', 'drowned', 'wither_skeleton'):
            fila.append(Image.open(os.path.join(VAN, f + '_spawn_egg.png')).convert('RGBA'))
    hoja = Image.new('RGBA', (len(fila) * 140 + 20, 260), (139, 139, 139, 255))
    for i, im in enumerate(fila):
        hoja.alpha_composite(im.resize((128, 128), Image.NEAREST), (10 + i * 140, 10))
        for k, esc in enumerate((1, 2, 3)):
            hoja.alpha_composite(im.resize((16 * esc, 16 * esc), Image.NEAREST), (10 + i * 140 + k * 36, 150 + (3 - esc) * 8))
    hoja.save(sys.argv[2])
    print('ok')

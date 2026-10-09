"""Texturas de los minijuegos de Nerea (octubre de 2026).

  textures/entity/nerea/solido.png   gris con grano (16 x 16) para las cajas de
                                     la morena, el canon, la pila y el corcho:
                                     el color lo pone el tinte (DISENO.md, 7)
  textures/item/cana_abismo.png      la Cana del Abismo (16 x 16): la cana en
                                     diagonal, de madera abisal, con el sedal y
                                     el anzuelo de espuma
  textures/item/perla_abismo.png     la Perla del Abismo (16 x 16): perla blanca
                                     con el reflejo cian y su mota de brillo
  textures/item/bala_canon.png       la Bala de canon (16 x 16): bola de hierro
  textures/entity/nerea/morena.png   la piel de las morenas (64 x 64): la red
                                     clara de la morena reticulada, el vientre,
                                     la aleta, la cabeza, la boca, los dientes,
                                     el ojo y la roca del borde del agujero;
                                     las regiones, en LADO, LOMO... (MorenaDibujo)

Uso: python nerea_minijuegos.py [raiz del proyecto]
"""
import json
import math
import os
import random
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
TEX = os.path.join(RAIZ, 'src', 'main', 'resources', 'assets', 'atalaya', 'textures')


def solido():
    r = random.Random(7)
    im = Image.new('RGBA', (16, 16))
    px = im.load()
    for y in range(16):
        for x in range(16):
            v = 214 + r.randint(-26, 26)
            px[x, y] = (v, v, v, 255)
    return im


def contorno(px, solido_, color):
    for (x, y) in list(solido_):
        if any((x + dx, y + dy) not in solido_ for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            px[x, y] = color + (255,)


def cana():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    # La rampa de la madera abisal (borde a nucleo) y el mango.
    BORDE, OSCURO, MEDIO, CLARO = (0x14, 0x2A, 0x32), (0x1F, 0x46, 0x52), (0x2E, 0x6E, 0x80), (0x5F, 0xA8, 0xB8)
    MANGO = (0x3A, 0x26, 0x1A)
    vara = set()
    for i in range(13):
        x, y = 1 + i, 14 - i
        vara.add((x, y))
        vara.add((x + 1, y))
    for (x, y) in vara:
        px[x, y] = (MEDIO if x + y == 15 else CLARO) + (255,)
    for i in range(4):
        px[1 + i, 14 - i] = MANGO + (255,)
        px[2 + i, 14 - i] = (0x52, 0x38, 0x26, 255)
    contorno(px, vara, BORDE)
    # El sedal cuelga de la punta y el anzuelo de espuma.
    for y in range(3, 11):
        px[14, y] = (0xD8, 0xE8, 0xF0, 255)
    px[13, 11] = (0x7F, 0xE8, 0xFF, 255)
    px[14, 11] = (0x7F, 0xE8, 0xFF, 255)
    px[13, 12] = (0x4F, 0xB8, 0xD0, 255)
    # Motas (DISENO.md, 8)
    px[3, 4] = OSCURO + (255,)
    px[11, 13] = MEDIO + (255,)
    return im


def bola(r_, colores, brillo):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    c = 7.5
    puntos = set()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - c, y - c)
            if d <= r_:
                puntos.add((x, y))
                # Radial con el nucleo arriba a la izquierda.
                dn = math.hypot(x - (c - 2), y - (c - 2))
                k = 0 if dn < 1.6 else 1 if dn < 3.2 else 2 if dn < 4.8 else 3
                px[x, y] = colores[k] + (255,)
    contorno(px, puntos, colores[4])
    for (x, y) in brillo:
        px[x, y] = (255, 255, 255, 255)
    return im


def hexc(t, a=255):
    return (int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16), a)


# La morena del abismo (octubre de 2026, Juan: "mejora su diseno"): verde
# abisal con la red de lineas claras de las morenas reticuladas, vientre
# palido, aleta oscura con el filo claro, boca magenta y ojos cian de la
# maldicion de Nerea.
PIEL = [hexc(c) for c in ('0f241f', '173429', '1f4535', '2a5843', '376b52')]
RED = [hexc(c) for c in ('8c9a4a', 'aebc62', 'cdd682', 'e4e8a6')]
VIENTRE = [hexc(c) for c in ('7c7a48', '9a9858', 'b8b674', 'd2cf92')]
BOCA = [hexc(c) for c in ('2a0612', '520c22', '7e1636', 'a8244c', 'd04a6c')]
DIENTE = [hexc(c) for c in ('a8a08a', 'cfc8b0', 'ece6d2', 'fbf8ee')]
OJO = [hexc(c) for c in ('0b4f63', '1b8aa6', '3fe0ff', '9ff4ff', 'eaffff')]
ROCA = [hexc(c) for c in ('121c1d', '1a2a2a', '24393a', '2f4a48', '3d5c58')]
MUSGO = [hexc(c) for c in ('243a1e', '34502a', '486a36')]

# Donde va cada cosa en morena.png (64 x 64); MorenaDibujo usa las mismas.
LADO = (0, 0, 64, 12)
LOMO = (0, 12, 64, 8)
PANZA = (0, 20, 64, 6)
ALETA = (0, 26, 64, 8)
CAB_LADO = (0, 34, 16, 12)
CAB_ARRIBA = (16, 34, 16, 12)
HOCICO = (32, 34, 8, 8)
MANDIBULA = (40, 34, 16, 8)
BOCA_R = (56, 34, 8, 8)
DIENTE_R = (0, 46, 4, 4)
OJO_R = (4, 46, 4, 4)
ROCA_R = (8, 46, 16, 16)
EXTREMO = (24, 46, 8, 8)
FARINGE = (32, 46, 8, 8)


def red_morena(r, w, h, celdas, oscuro=0, grosor=0.62):
    """La red de la morena reticulada: celdas de Voronoi oscuras y sus bordes
    claros. Devuelve, por pixel, (es_linea, tono de la celda)."""
    sitios = [(r.uniform(0, w), r.uniform(-1, h + 1)) for _ in range(celdas)]
    tonos = [r.randint(1, 3) - oscuro for _ in sitios]
    out = {}
    for y in range(h):
        for x in range(w):
            ds = []
            for i, (sx, sy) in enumerate(sitios):
                # la textura da la vuelta a lo largo: que la red no se corte
                dx = min(abs(x + 0.5 - sx), w - abs(x + 0.5 - sx))
                ds.append((math.hypot(dx, (y + 0.5 - sy) * 1.15), i))
            ds.sort()
            linea = ds[1][0] - ds[0][0] < grosor
            out[x, y] = (linea, max(0, tonos[ds[0][1]]))
    return out


def morena_tex():
    r = random.Random(11)
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    px = im.load()

    def region(reg, fn):
        x0, y0, w, h = reg
        for y in range(h):
            for x in range(w):
                c = fn(x, y, w, h)
                if c is not None:
                    px[x0 + x, y0 + y] = c

    # El costado: la red sobre el verde; abajo pasa al vientre y arriba al lomo.
    red = red_morena(r, 64, 12, 24)
    def lado(x, y, w, h):
        linea, tono = red[x, y]
        if y >= h - 2:
            return VIENTRE[1 + (x + y) % 2] if not linea else VIENTRE[3]
        if linea:
            return RED[1 if y > 2 else 0] if (x * 7 + y * 3) % 9 else RED[2]
        return PIEL[min(4, tono + (1 if y > h // 2 else 0))]
    region(LADO, lado)
    red2 = red_morena(r, 64, 8, 16, oscuro=1, grosor=0.5)
    def lomo(x, y, w, h):
        linea, tono = red2[x, y]
        return RED[0] if linea else PIEL[max(0, tono)]
    region(LOMO, lomo)
    def panza(x, y, w, h):
        return VIENTRE[2 + (1 if (x + 2 * y) % 5 == 0 else 0)] if r.random() > 0.12 else VIENTRE[1]
    region(PANZA, panza)
    # La aleta: radios oscuros, el filo claro arriba y un borde ondulado (lo
    # transparente lo recorta el cutout).
    ondas = [1 + int(1.2 + 1.2 * math.sin(x * 0.9) + r.random() * 0.8) for x in range(64)]
    def aleta(x, y, w, h):
        if y < ondas[x] - 1:
            return None
        if y < ondas[x] + 1:
            return RED[2]
        return PIEL[0] if x % 3 == 0 else PIEL[1 + (y > 4)]
    region(ALETA, aleta)
    red3 = red_morena(r, 16, 12, 9, grosor=0.55)
    def cab_lado(x, y, w, h):
        linea, tono = red3[x, y]
        if 9 <= x <= 11 and 3 <= y <= 8 and x - 9 == (y - 3) // 3:
            return PIEL[0]                       # la hendidura de la agalla
        if y >= h - 2:
            return VIENTRE[2]
        return RED[1] if linea else PIEL[min(4, tono + 1)]
    region(CAB_LADO, cab_lado)
    red4 = red_morena(r, 16, 12, 8, oscuro=1, grosor=0.5)
    region(CAB_ARRIBA, lambda x, y, w, h: RED[0] if red4[x, y][0] else PIEL[red4[x, y][1]])
    def hocico(x, y, w, h):
        if (x, y) in ((2, 2), (5, 2)):
            return PIEL[0]                       # los orificios de la nariz
        return PIEL[2] if y < 5 else VIENTRE[1]
    region(HOCICO, hocico)
    def mandibula(x, y, w, h):
        if y < 2:
            return BOCA[3]                       # el labio de dentro
        return VIENTRE[3] if (x * 5 + y * 3) % 7 else RED[1]
    region(MANDIBULA, mandibula)
    region(BOCA_R, lambda x, y, w, h: BOCA[min(4, 1 + (abs(x - 3.5) < 2) + (y < 4) + (r.random() < 0.15))])
    region(DIENTE_R, lambda x, y, w, h: DIENTE[3 - y if y < 4 else 0])
    def ojo(x, y, w, h):
        if x in (1, 2) and 0 <= y <= 3:
            return hexc('0b1a1e')                # la pupila, una rendija
        return OJO[3] if (x + y) % 3 == 0 else OJO[2]
    region(OJO_R, ojo)
    def roca(x, y, w, h):
        v = r.random()
        if v < 0.12:
            return MUSGO[r.randint(0, 2)]
        k = 1 + int(2.6 * (1 - y / h) * r.uniform(0.6, 1.2))
        return ROCA[max(0, min(4, k))]
    region(ROCA_R, roca)
    region(EXTREMO, lambda x, y, w, h: PIEL[1 + (x + y) % 2])
    region(FARINGE, lambda x, y, w, h: BOCA[4] if (x + y) % 3 else BOCA[3])
    return im


HIERRO = [hexc(c) for c in ('121216', '1c1c21', '27272d', '34343c', '45454f', '5c5c68')]
OXIDO = [hexc(c) for c in ('3a2216', '5a3420', '7a4a2a')]


def bala_tex():
    """La piel de la bala de canon (16 x 16): hierro fundido con grano, picaduras
    y algun roce de oxido. La bala es de pixeles (tres cajas cruzadas, BalaDibujo)
    y cada cara toma el trozo del centro de su tamano, a un texel por pixel."""
    r = random.Random(5)
    im = Image.new('RGBA', (16, 16))
    px = im.load()
    for y in range(16):
        for x in range(16):
            k = 2 + (1 if r.random() < 0.3 else 0) - (1 if r.random() < 0.18 else 0)
            px[x, y] = HIERRO[k]
    for _ in range(14):
        x, y = r.randrange(16), r.randrange(16)
        px[x, y] = HIERRO[0]
    for (x, y) in ((5, 5), (6, 5), (5, 6)):
        px[x, y] = HIERRO[4]
    for _ in range(3):
        cx, cy = r.randrange(3, 13), r.randrange(3, 13)
        for _ in range(4):
            x, y = min(15, max(0, cx + r.randint(-1, 1))), min(15, max(0, cy + r.randint(-1, 1)))
            px[x, y] = OXIDO[r.randint(0, 2)]
    return im


BRONCE = [hexc(c) for c in ('2a1c0c', '4a3416', '7a5a26', 'a87e3a', 'd0a85a')]
VERDIN = [hexc(c) for c in ('1c3a32', '2e5a4a', '4e8a70')]


def catalejo():
    """El catalejo del Canon del Naufragio (128 x 128; Juan: "que sea como el
    telescopio y ahi este la mira"): fuera del circulo, negro; el aro de bronce
    verdeado con sus remaches; dentro, el cristal limpio con la cruz fina, las
    marcas de caida por debajo del centro y una sombra que oscurece el borde.
    La mira del centro la pone el juego encima (nerea_mira_canon.png)."""
    N = 128
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    px = im.load()
    c = (N - 1) / 2
    R = 58.0
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - c, y - c)
            if d > R + 4:
                px[x, y] = (4, 6, 8, 255)
            elif d > R:
                # el aro: bronce con luz arriba a la izquierda, verdin abajo
                luz = -((x - c) + (y - c)) / (2 * d + 1e-6)
                k = 4 if luz > 0.45 else 3 if luz > 0.1 else 2 if luz > -0.3 else 1
                col = BRONCE[k]
                if luz < -0.45 and (x * 3 + y) % 5 == 0:
                    col = VERDIN[1]
                if d > R + 3:
                    col = BRONCE[0]
                px[x, y] = col
            elif d > R - 1:
                px[x, y] = BRONCE[0]
            else:
                # el cristal: transparente, con sombra hacia el borde
                a = int(150 * max(0.0, (d - (R - 14)) / 14) ** 1.6)
                px[x, y] = (6, 14, 18, a)
    # remaches
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        x, y = int(round(c + math.cos(a) * (R + 2))), int(round(c + math.sin(a) * (R + 2)))
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            px[x + dx, y + dy] = BRONCE[4] if (dx, dy) == (0, 0) else BRONCE[2]
    # la cruz fina, cortada en el centro (alli va la mira)
    tinta = (12, 20, 24, 210)
    for i in range(int(c - R + 3), int(c + R - 2)):
        if abs(i - c) > 18:
            px[int(c), i] = tinta
            px[i, int(c)] = tinta
    # marcas de caida bajo el centro: cada vez mas anchas
    for k, y in enumerate((int(c) + 24, int(c) + 32, int(c) + 40)):
        for x in range(int(c) - 3 - 2 * k, int(c) + 4 + 2 * k):
            px[x, y] = tinta
    return im


def bala_icono():
    """La Bala de canon en el inventario: una bola de hierro con su brillo arriba
    a la izquierda, el reflejo frio abajo a la derecha, la costura y picaduras."""
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    c = 7.5
    puntos = set()
    for y in range(16):
        for x in range(16):
            if math.hypot(x - c, y - c) <= 6.6:
                puntos.add((x, y))
    for (x, y) in puntos:
        dx, dy = x - c, y - c
        # Luz de arriba a la izquierda.
        nz = math.sqrt(max(0.0, 6.6 ** 2 - dx * dx - dy * dy)) / 6.6
        luz = (-dx * 0.55 - dy * 0.65) / 6.6 + nz * 0.55
        k = 0 if luz < -0.05 else 1 if luz < 0.2 else 2 if luz < 0.42 else 3 if luz < 0.6 else 4
        px[x, y] = HIERRO[k]
        # El reflejo frio del borde de abajo a la derecha.
        if 5.2 < math.hypot(dx, dy) and dx + dy > 4:
            px[x, y] = hexc('3c4654')
    for x in range(3, 13):
        if (x, 8) in puntos:
            px[x, 8] = HIERRO[3] if x < 6 else HIERRO[2]
    for (x, y) in ((9, 4), (10, 11), (5, 10), (11, 7)):
        px[x, y] = HIERRO[0]
    for (x, y) in ((4, 4), (5, 4), (4, 5)):
        px[x, y] = HIERRO[5]
    px[5, 3] = hexc('8a8a98')
    contorno(px, puntos, (0x0a, 0x0a, 0x0e))
    return im


def mira_canon():
    """La mira del Canon del Naufragio (33 x 33, en blanco: el color lo pone el
    codigo): un aro con cuatro marcas, la cruz fina y el punto del centro, con
    un contorno oscuro para que se lea sobre el cielo y sobre Nerea."""
    im = Image.new('RGBA', (33, 33), (0, 0, 0, 0))
    px = im.load()
    c = 16
    pts = set()
    for y in range(33):
        for x in range(33):
            d = math.hypot(x - c, y - c)
            if 11.4 <= d <= 12.6:
                pts.add((x, y))
    for k in range(4):
        dx, dy = ((0, -1), (1, 0), (0, 1), (-1, 0))[k]
        for i in range(9, 15):
            pts.add((c + dx * i, c + dy * i))
    for i in (-5, -4, -3, 3, 4, 5):
        pts.add((c + i, c))
        pts.add((c, c + i))
    pts.add((c, c))
    for (x, y) in pts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q not in pts and 0 <= q[0] < 33 and 0 <= q[1] < 33:
                    px[q] = (10, 14, 18, 170)
    for (x, y) in pts:
        px[x, y] = (255, 255, 255, 255)
    return im


PARTICULAS = os.path.join(RAIZ, 'src', 'main', 'resources', 'assets', 'atalaya', 'particles')


def particula(nombre, frames):
    nombres = []
    for i, im in enumerate(frames):
        n = f'{nombre}_{i}'
        im.save(os.path.join(TEX, 'particle', n + '.png'))
        nombres.append(f'atalaya:{n}')
    with open(os.path.join(PARTICULAS, nombre + '.json'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps({'textures': nombres}, indent=2) + '\n')
    print('ok particula', nombre, len(frames))


def nota(forma):
    """Una nota de musica de 8 x 8 en blanco con su contorno (la tine el codigo):
    0 corchea, 1 dos corcheas unidas, 2 negra, 3 la nota rota (fallo)."""
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    px = im.load()
    pts = set()
    if forma == 0:
        pts |= {(1, 5), (2, 5), (1, 6), (2, 6), (3, 6), (3, 5), (3, 4), (3, 3), (3, 2), (3, 1), (4, 1), (5, 2), (5, 3)}
    elif forma == 1:
        pts |= {(0, 6), (1, 6), (1, 5), (0, 5), (2, 5), (2, 4), (2, 3), (2, 2), (2, 1), (3, 1), (4, 1), (5, 1),
                (5, 2), (5, 3), (5, 4), (4, 5), (5, 5), (6, 5), (4, 6), (5, 6)}
    elif forma == 2:
        pts |= {(2, 5), (3, 5), (2, 6), (3, 6), (4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1)}
    else:
        pts |= {(1, 5), (2, 6), (3, 5), (4, 4), (3, 2), (4, 1), (5, 2)}
    for (x, y) in pts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q not in pts and 0 <= q[0] < 8 and 0 <= q[1] < 8:
                    px[q] = (40, 30, 70, 200)
    for (x, y) in pts:
        px[x, y] = (255, 255, 255, 255) if y < 4 else (226, 236, 255, 255)
    return im


def humo(f):
    """Humo de polvora: una bocanada redonda, parda y gris, mas clara arriba;
    en cada fotograma se aclara y se deshilacha por el borde (la particula ya
    crece sola)."""
    r = random.Random(f + 41)
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    px = im.load()
    ramp = [hexc(c) for c in ('2e2a26', '45403a', '5e5850', '7a7368', '958e82', 'aaa498')]
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - 3.5, y - 3.5) / 3.7
            if d > 1:
                continue
            if d > 0.72 and r.random() < 0.18 + 0.2 * f:
                continue
            k = min(5, f + (2 if y < 3 else 1 if y < 5 else 0) + (1 if d < 0.4 else 0))
            px[x, y] = ramp[k][:3] + (235 - f * 50,)
    return im


def fogonazo(f):
    """El fogonazo del canonazo: estrella de fuego que se cierra."""
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    px = im.load()
    l = 3.6 - f * 0.9
    for y in range(8):
        for x in range(8):
            dx, dy = abs(x - 3.5), abs(y - 3.5)
            d = math.hypot(dx, dy)
            if d <= l * 0.55 or (min(dx, dy) <= 0.6 and max(dx, dy) <= l) or (abs(dx - dy) <= 0.6 and d <= l * 0.8):
                k = d / max(l, 0.1)
                px[x, y] = hexc('fffbe0') if k < 0.3 else hexc('ffd24a') if k < 0.6 else hexc('ff7a1a')
    return im


# El Canon del Naufragio (Juan: "mejora el diseno del canon, se ve muy simple"):
# todo en canon.png (64 x 64); CanonNaufragioRenderer usa las mismas regiones.
CANON_BRONCE = (0, 0, 32, 8)
CANON_ARO = (32, 0, 8, 8)
CANON_BOCA = (40, 0, 8, 8)
CANON_HIERRO = (48, 0, 8, 8)
CANON_PERCEBES = (56, 0, 8, 8)
CANON_MADERA = (0, 8, 32, 8)
CANON_VETA = (32, 8, 8, 8)
CANON_RUEDA = (0, 16, 16, 16)
CANON_ALGA = (16, 16, 8, 16)
CANON_CUERDA = (24, 16, 8, 8)
CANON_VERDIN = (32, 16, 8, 8)
BRONCE_C = [hexc(c) for c in ('3a2610', '5e4018', '8c6c32', 'b08a46', 'd8b46a', 'f0d898')]
VERDIN_C = [hexc(c) for c in ('1c3a32', '2e5a4a', '4e8a70', '74b498')]
MADERA_C = [hexc(c) for c in ('1e140c', '2c1e12', '3e2a18', '52381f', '66482a')]
ALGA_C = [hexc(c) for c in ('1a3a1a', '2a5a24', '3e7a30', '5a9a3e')]
HUESO_C = [hexc(c) for c in ('5c5545', '8a8068', 'b3a98c', 'd3c9aa')]


def canon_tex():
    r = random.Random(17)
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    px = im.load()

    def region(reg, fn):
        x0, y0, w, h = reg
        for y in range(h):
            for x in range(w):
                c = fn(x, y, w, h)
                if c is not None:
                    px[x0 + x, y0 + y] = c

    # Bronce del canon: brillo a lo largo, sombra abajo y manchas de verdin.
    manchas = [(r.randrange(32), r.randrange(8), r.uniform(1.2, 2.6)) for _ in range(6)]

    def bronce(x, y, w, h):
        for (mx, my, mr) in manchas:
            if math.hypot(x - mx, (y - my) * 1.4) < mr:
                return VERDIN_C[1 + (x + y) % 2]
        k = 4 if y == 1 else 3 if y < 4 else 2 if y < 6 else 1
        if r.random() < 0.12:
            k -= 1
        return BRONCE_C[k]
    region(CANON_BRONCE, bronce)
    region(CANON_ARO, lambda x, y, w, h: BRONCE_C[5] if y == 1 else BRONCE_C[1] if y in (0, 7) else BRONCE_C[4] if y < 4 else BRONCE_C[3])

    def boca(x, y, w, h):
        d = math.hypot(x - 3.5, y - 3.5)
        return (8, 6, 4, 255) if d < 2.2 else BRONCE_C[4] if d < 3.0 else BRONCE_C[2]
    region(CANON_BOCA, boca)

    def hierro(x, y, w, h):
        if (x, y) in ((2, 2), (5, 5)):
            return (90, 90, 100, 255)
        return (36, 36, 42, 255) if (x + y) % 3 else (28, 28, 32, 255)
    region(CANON_HIERRO, hierro)

    def percebes(x, y, w, h):
        cx, cy = (2, 2), (5, 4)
        for (a, b) in ((2, 2), (5, 4), (2, 6)):
            d = math.hypot(x - a, y - b)
            if d < 0.9:
                return (20, 16, 12, 255)
            if d < 2.0:
                return HUESO_C[3] if y < b else HUESO_C[2]
        return HUESO_C[1] if r.random() < 0.5 else VERDIN_C[1]
    region(CANON_PERCEBES, percebes)

    # Madera de barco hundido: vetas a lo largo, junta de tablon, clavos y verdin.
    def madera(x, y, w, h):
        if y == 4:
            return MADERA_C[0]
        if (x, y) in ((3, 2), (19, 6), (29, 2)):
            return (70, 70, 76, 255)
        if r.random() < 0.06:
            return ALGA_C[0]
        k = 3 if (x // 3 + y) % 5 == 0 else 2
        if y in (0, 5):
            k += 1
        return MADERA_C[min(4, k)]
    region(CANON_MADERA, madera)

    def veta(x, y, w, h):
        d = math.hypot(x - 3.5, y - 3.5)
        return MADERA_C[3] if int(d) % 2 else MADERA_C[2]
    region(CANON_VETA, veta)

    # La rueda de cureña: aro de madera, cuatro radios y el cubo; entre los radios, nada.
    def rueda(x, y, w, h):
        dx, dy = x - 7.5, y - 7.5
        d = math.hypot(dx, dy)
        if d > 7.6:
            return None
        if d > 6.0:
            return MADERA_C[4] if dy < 0 else MADERA_C[2]
        if d > 5.2:
            return (36, 36, 42, 255)        # el fleje de hierro por dentro del aro
        if d < 2.0:
            return (36, 36, 42, 255) if d < 1.0 else MADERA_C[3]
        if abs(dx) < 1.0 or abs(dy) < 1.0:
            return MADERA_C[3]
        return None
    region(CANON_RUEDA, rueda)

    # Un alga larga que cuelga: cinta ondulada verde.
    def alga(x, y, w, h):
        c = 3.5 + 1.6 * math.sin(y * 0.8)
        if abs(x - c) < 1.2 + (0.6 if y % 5 == 2 else 0):
            return ALGA_C[3] if x < c else ALGA_C[2] if y < 12 else ALGA_C[1]
        return None
    region(CANON_ALGA, alga)
    region(CANON_CUERDA, lambda x, y, w, h: hexc('8a7048') if (x + y) % 4 < 2 else hexc('5e4a30'))
    region(CANON_VERDIN, lambda x, y, w, h: VERDIN_C[r.randint(1, 3)])
    return im


def main():
    salidas = {
        os.path.join(TEX, 'entity', 'nerea', 'solido.png'): solido(),
        os.path.join(TEX, 'item', 'cana_abismo.png'): cana(),
        os.path.join(TEX, 'entity', 'nerea', 'morena.png'): morena_tex(),
        os.path.join(TEX, 'item', 'perla_abismo.png'): bola(5.6, [(0xF6, 0xFF, 0xFF), (0xD6, 0xF4, 0xFA), (0xA8, 0xE0, 0xEE),
                                                               (0x78, 0xC4, 0xD8), (0x3A, 0x7E, 0x96)], [(5, 5)]),
        os.path.join(TEX, 'item', 'bala_canon.png'): bala_icono(),
        os.path.join(TEX, 'entity', 'nerea', 'bala.png'): bala_tex(),
        os.path.join(TEX, 'gui', 'nerea_mira_canon.png'): mira_canon(),
        os.path.join(TEX, 'gui', 'nerea_catalejo.png'): catalejo(),
        os.path.join(TEX, 'entity', 'nerea', 'canon.png'): canon_tex(),
    }
    for ruta, im in salidas.items():
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        im.save(ruta)
        print('ok', ruta)
    particula('nerea_nota', [nota(i) for i in range(4)])
    particula('nerea_humo', [humo(f) for f in range(4)])
    particula('nerea_fogonazo', [fogonazo(f) for f in range(3)])


if __name__ == '__main__':
    main()

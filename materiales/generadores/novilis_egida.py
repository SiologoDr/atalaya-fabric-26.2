"""La Egida de la Sombra del Escudo de Novilis (octubre de 2026) y su sombra.

Salen tres texturas en assets/atalaya/textures/entity/novilis:

  egida.png         el escudo: 26 x 32 (un texel = 0,1 bloques; el escudo mide
                    2,6 x 3,2 bloques). Placa de hierro quemado como la armadura
                    de Novilis, canto de oro y el sol en medio (nucleo, cruz y
                    ocho rayos), como en la ficha (novilis_mecanicas_escenas.py,
                    egida_modelo).
  egida_brillo.png  lo que brilla cuando mira al sol: el sol del emblema y el
                    canto, en oro claro; lo demas transparente.
  sombra.png        la sombra del suelo (16 x 32): blanca, la pone oscura el
                    color del vertice. Opaca junto al escudo, se aclara hacia el
                    final y tiene los bordes suaves.

La paleta sale de novilis_f2.png y novilis_brillo_f2.png (DISENO.md, punto 1):
los hierros 160f10/1f1717/2c2020 y los oros 633c11 a ffd77a.

Uso: python novilis_egida.py [raiz del proyecto] [carpeta de vista previa]
"""
import math
import os
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
VISTA = sys.argv[2] if len(sys.argv) > 2 else None
SALIDA = os.path.join(RAIZ, 'src', 'main', 'resources', 'assets', 'atalaya', 'textures', 'entity', 'novilis')

ANCHO, ALTO = 26, 32
CX, CY = 12.5, 15.5

# Hierro quemado (de borde a nucleo) y oro (de borde a nucleo): cinco pasos cada uno.
HIERRO = [(0x12, 0x0C, 0x0D), (0x16, 0x0F, 0x10), (0x1F, 0x17, 0x17), (0x29, 0x1E, 0x1E), (0x2C, 0x20, 0x20)]
ORO = [(0x63, 0x3C, 0x11), (0x8A, 0x54, 0x18), (0xC0, 0x7C, 0x22), (0xE8, 0xA8, 0x3A), (0xFF, 0xD7, 0x7A)]
LUZ = [(0xFF, 0xC2, 0x3A), (0xFF, 0xD5, 0x6C), (0xFF, 0xE8, 0x9E), (0xFF, 0xF2, 0xB8)]
CANTO = 2          # anchura del canto de oro (pixeles)


def emblema():
    """Los pixeles del sol del centro: {(x, y): nivel}, nivel 0 (canto) a 3 (nucleo)."""
    out = {}
    for y in range(ALTO):
        for x in range(ANCHO):
            d = math.hypot(x - CX, y - CY)
            if d <= 3.3:
                out[(x, y)] = 3 if d < 1.4 else 2 if d < 2.4 else 1
            # la cruz: hasta 5 pixeles del centro, de 2 de ancho
            elif (abs(x - CX) <= 0.6 and abs(y - CY) <= 5.2) or (abs(y - CY) <= 0.6 and abs(x - CX) <= 5.2):
                out[(x, y)] = 1
    # los ocho rayos: puntos de 2 x 2 a 7 pixeles del centro
    for a in range(8):
        ang = math.tau * a / 8 + math.tau / 16
        rx, ry = CX + math.cos(ang) * 7.2, CY + math.sin(ang) * 7.2
        for dx in (-0.5, 0.5):
            for dy in (-0.5, 0.5):
                out[(int(round(rx + dx - 0.01)), int(round(ry + dy - 0.01)))] = 1
    # el contorno, calculado (DISENO.md, punto 5): lo que toca el aire es canto
    solido = set(out)
    for (x, y) in list(out):
        if any((x + dx, y + dy) not in solido for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and out[(x, y)] >= 2:
            out[(x, y)] = 1
    return out


def en_canto(x, y):
    return x < CANTO or y < CANTO or x >= ANCHO - CANTO or y >= ALTO - CANTO


def escudo():
    im = Image.new('RGBA', (ANCHO, ALTO))
    px = im.load()
    sol = emblema()
    for y in range(ALTO):
        for x in range(ANCHO):
            if en_canto(x, y):
                # el canto: oscuro por fuera, claro por dentro, y mas luz arriba
                fuera = x == 0 or y == 0 or x == ANCHO - 1 or y == ALTO - 1
                k = 0 if fuera else 2
                if not fuera and y < ALTO / 2:
                    k = 3
                px[x, y] = ORO[k] + (255,)
                continue
            if (x, y) in sol:
                px[x, y] = ORO[1 + sol[(x, y)]] + (255,)
                continue
            # la placa: radial, mas clara arriba y al centro (DISENO.md, punto 6)
            d = math.hypot((x - CX) / ANCHO, (y - CY + 4) / ALTO)
            k = 4 if d < 0.16 else 3 if d < 0.27 else 2 if d < 0.38 else 1
            # justo dentro del canto, una linea oscura que lo separa
            if x == CANTO or y == CANTO or x == ANCHO - CANTO - 1 or y == ALTO - CANTO - 1:
                k = 0
            px[x, y] = HIERRO[k] + (255,)
    # remaches de oro en las cuatro esquinas de dentro
    for (x, y) in ((4, 4), (ANCHO - 5, 4), (4, ALTO - 5), (ANCHO - 5, ALTO - 5)):
        px[x, y] = ORO[3] + (255,)
    # dos grietas de lava, como las de su armadura (asimetricas: DISENO.md, punto 8)
    for (x, y) in ((6, 22), (7, 23), (7, 24), (8, 25), (19, 7), (18, 8), (18, 9)):
        px[x, y] = ORO[2] + (255,)
    return im


def brillo():
    im = Image.new('RGBA', (ANCHO, ALTO), (0, 0, 0, 0))
    px = im.load()
    sol = emblema()
    for (x, y), nivel in sol.items():
        px[x, y] = LUZ[min(3, nivel + 1)] + (255,)
    # un halo suave alrededor del nucleo
    for y in range(ALTO):
        for x in range(ANCHO):
            if (x, y) in sol or en_canto(x, y):
                continue
            d = math.hypot(x - CX, y - CY)
            if d < 6.0:
                a = int(120 * (1.0 - d / 6.0) ** 1.5)
                px[x, y] = LUZ[0] + (a,)
    # el canto de dentro brilla (lo que le da el sol)
    for y in range(ALTO):
        for x in range(ANCHO):
            if en_canto(x, y) and not (x == 0 or y == 0 or x == ANCHO - 1 or y == ALTO - 1):
                px[x, y] = LUZ[2] + (200,)
    return im


def sombra():
    w, h = 16, 32
    im = Image.new('RGBA', (w, h))
    px = im.load()
    for y in range(h):
        largo = y / (h - 1)
        a_largo = 1.0 - 0.6 * largo ** 1.3
        if y < 2:
            a_largo *= 0.6 + 0.2 * y
        for x in range(w):
            u = (x + 0.5) / w
            lado = min(u, 1.0 - u) / 0.22
            a_lado = 1.0 if lado >= 1.0 else lado * lado * (3 - 2 * lado)
            px[x, y] = (255, 255, 255, int(255 * a_largo * a_lado))
    return im


def main():
    os.makedirs(SALIDA, exist_ok=True)
    piezas = {'egida': escudo(), 'egida_brillo': brillo(), 'sombra': sombra()}
    for nombre, im in piezas.items():
        im.save(os.path.join(SALIDA, nombre + '.png'))
        print('ok', nombre, im.size)
    if VISTA:
        os.makedirs(VISTA, exist_ok=True)
        fondo = Image.new('RGBA', (ANCHO * 12 * 3 + 40, ALTO * 12 + 20), (70, 60, 56, 255))
        fondo.alpha_composite(piezas['egida'].resize((ANCHO * 12, ALTO * 12), Image.NEAREST), (10, 10))
        junta = piezas['egida'].copy()
        junta.alpha_composite(piezas['egida_brillo'])
        fondo.alpha_composite(junta.resize((ANCHO * 12, ALTO * 12), Image.NEAREST), (20 + ANCHO * 12, 10))
        s = piezas['sombra'].resize((16 * 12, 32 * 12), Image.NEAREST)
        oscura = Image.new('RGBA', s.size, (22, 12, 8, 0))
        oscura.putalpha(s.getchannel('A'))
        fondo.alpha_composite(oscura, (30 + ANCHO * 24, 10))
        fondo.save(os.path.join(VISTA, 'egida_vista.png'))


if __name__ == '__main__':
    main()

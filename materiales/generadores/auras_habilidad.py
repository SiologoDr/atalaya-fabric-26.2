"""
Las auras de las habilidades de las armaduras (10-10-2026, Juan: "debe de
senalarte cuando la habilidad esta activa, en cada armadura; actualmente sale
solo un efecto de que lo activaste pero no sale si lo tienes ahorita"). Las
pinta HabilidadAuraLayer alrededor de quien la tiene activa, mientras dura:

  - jade_anillo.png     Muralla de Jade: el hexagono de jade con los vertices de
                        oro, tumbado a los pies (y uno grande y tenue donde
                        protege).
  - jade_cristal.png    los cristales de jade que le giran alrededor.
  - mareas_onda.png     Manantial: la onda de agua que sale de el y se abre.
  - vendaval_cinta.png  Corriente Ascendente: las cintas de viento que le suben
                        en espiral (se repite de arriba abajo).
  - vendaval_remolino.png  el remolino del suelo.
  - solar_halo.png      Furia Solar: el sol que le arde detras de la cabeza.

Uso: python auras_habilidad.py <raiz del proyecto>
"""
import math
import os
import random
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'


def lienzo(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def hexagono(dx, dy):
    """Distancia hexagonal (un hexagono regular de 'radio' 1 tiene distancia 1 en su borde)."""
    dx, dy = abs(dx), abs(dy)
    return max(dx * math.sqrt(3) / 2 + dy * 0.5, dy)


def jade_anillo():
    n = 64
    im = lienzo(n, n)
    for y in range(n):
        for x in range(n):
            dx, dy = (x + 0.5 - 32) / 30, (y + 0.5 - 32) / 30
            h = hexagono(dx, dy)
            if 0.80 <= h <= 1.0:
                k = (h - 0.80) / 0.20
                borde = k < 0.12 or k > 0.88
                c = (150, 240, 180) if borde else (46, 170, 110) if (x + y) % 5 else (70, 200, 135)
                im.putpixel((x, y), c + (235,))
    # Los vertices, de oro.
    for i in range(6):
        a = math.pi / 6 + i * math.pi / 3
        cx, cy = 32 + math.cos(a) * 27, 32 + math.sin(a) * 27
        for y in range(n):
            for x in range(n):
                if math.hypot(x + 0.5 - cx, y + 0.5 - cy) < 3.2:
                    brillo = math.hypot(x + 0.5 - cx + 1, y + 0.5 - cy + 1) < 1.5
                    im.putpixel((x, y), ((255, 240, 170) if brillo else (232, 182, 52)) + (255,))
    return im


def jade_cristal():
    w, h = 16, 32
    im = lienzo(w, h)
    for y in range(h):
        # Punta arriba (y 0..9), cuerpo (9..27), punta abajo corta.
        if y < 10:
            ancho = 1 + y * 0.6
        elif y < 28:
            ancho = 6.5
        else:
            ancho = 6.5 - (y - 27) * 1.6
        for x in range(w):
            d = x + 0.5 - 8
            if abs(d) <= ancho:
                faceta = d / max(ancho, 0.1)
                if abs(faceta) > 0.8:
                    c = (24, 96, 62)
                elif faceta < -0.15:
                    c = (60, 180, 115)
                elif faceta < 0.25:
                    c = (150, 245, 190)
                else:
                    c = (40, 140, 92)
                im.putpixel((x, y), c + (240,))
    return im


def mareas_onda():
    n = 64
    im = lienzo(n, n)
    r = random.Random(5)
    for y in range(n):
        for x in range(n):
            d = math.hypot(x + 0.5 - 32, y + 0.5 - 32)
            if 25.0 <= d <= 31.0:
                k = 1.0 - abs(d - 28.5) / 3.5
                a = math.atan2(y - 32, x - 32)
                espuma = (math.sin(a * 9) > 0.55 and d > 28.0) or r.random() < 0.04
                c = (235, 255, 255) if espuma else (90, 215, 240) if k > 0.45 else (40, 150, 210)
                im.putpixel((x, y), c + (int(80 + 170 * k),))
    return im


def vendaval_cinta():
    w, h = 16, 64
    im = lienzo(w, h)
    r = random.Random(9)
    vetas = [(r.uniform(2, 14), r.uniform(0, h), r.uniform(8, 22)) for _ in range(9)]
    for y in range(h):
        for x in range(w):
            d = abs(x + 0.5 - 8) / 8
            base = max(0.0, 1.0 - d) ** 1.5
            a = 90 * base
            c = (205, 180, 255)
            for vx, vy, largo in vetas:
                dy = (y - vy) % h
                if abs(x + 0.5 - vx) < 0.9 and dy < largo:
                    a = max(a, 230 * (1.0 - dy / largo))
                    c = (245, 240, 255)
            if a > 4:
                im.putpixel((x, y), c + (int(a),))
    return im


def vendaval_remolino():
    n = 64
    im = lienzo(n, n)
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - 32, y + 0.5 - 32
            d = math.hypot(dx, dy)
            if d < 4 or d > 31:
                continue
            a = math.atan2(dy, dx)
            fase = (a - d / 7.0) % (2 * math.pi / 3)
            if fase < 0.55:
                k = 1.0 - fase / 0.55
                fuera = min(1.0, (31 - d) / 6.0)
                c = (245, 240, 255) if k > 0.75 else (190, 160, 250)
                im.putpixel((x, y), c + (int(210 * k * fuera),))
    return im


def solar_halo():
    n = 64
    im = lienzo(n, n)
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - 32, y + 0.5 - 32
            d = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            c = None
            if 11.0 <= d <= 14.5:
                c, al = ((255, 236, 150) if d < 12.2 else (246, 192, 60)), 255
            elif 14.5 < d <= 31.0:
                rayo = (a / (2 * math.pi / 12)) % 1.0
                largo = 31.0 if int(round(a / (2 * math.pi / 12))) % 2 == 0 else 24.0
                ancho = 0.16 * (1.0 - (d - 14.5) / (largo - 14.5 + 0.01))
                if d <= largo and abs(rayo - 0.5) > 0.5 - ancho:
                    pass
                if d <= largo and min(rayo, 1.0 - rayo) < ancho:
                    k = (d - 14.5) / (largo - 14.5)
                    c, al = ((255, 220, 110) if k < 0.4 else (240, 130, 30)), int(255 * (1.0 - 0.6 * k))
            elif d < 11.0:
                c, al = (255, 200, 80), int(70 * (d / 11.0))
            if c:
                im.putpixel((x, y), c + (al,))
    return im


def main():
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/habilidad')
    os.makedirs(carpeta, exist_ok=True)
    for nombre, f in (('jade_anillo', jade_anillo), ('jade_cristal', jade_cristal), ('mareas_onda', mareas_onda),
                      ('vendaval_cinta', vendaval_cinta), ('vendaval_remolino', vendaval_remolino), ('solar_halo', solar_halo)):
        f().save(os.path.join(carpeta, nombre + '.png'))
    print('ok')


if __name__ == '__main__':
    main()

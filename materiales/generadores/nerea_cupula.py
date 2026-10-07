"""
La cupula de refugio de la Marea Alta (Nerea, octubre de 2026; Juan: "la
burbuja tiene que ser celeste y como una cupula"). La textura se repite cuatro
veces alrededor de la media esfera y una de abajo arriba (v = 1 en el suelo).

  - el velo: celeste muy translucido, un poco mas denso hacia el suelo
  - la red de reflejos: lineas finas de agua clara (como la luz en una piscina),
    de pixeles enteros
  - el borde: dos filas abajo, claras y densas, donde la cupula toca el suelo
  - arriba, un brillo suave (la luz que le da desde el cielo)

Celeste de la rampa del agua de Nerea (DISENO.md: nucleo claro, canto mas
apagado, sin negro). El juego la tine de blanco (o de rojo si esta llena).

Uso: python nerea_cupula.py <raiz del proyecto>
"""
import math
import os
import random
import sys

from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
N = 32
VELO = (120, 210, 245)
RED = (205, 244, 255)
BORDE = (236, 252, 255)
CANTO = (90, 185, 230)


def main():
    rnd = random.Random(2610)
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    q = im.load()
    for y in range(N):
        k = y / (N - 1)                     # 0 arriba, 1 abajo (suelo)
        for x in range(N):
            a = int(92 + 44 * k)
            q[x, y] = VELO + (a,)
    # la red de reflejos: los bordes de unas celdas (como la luz en una piscina),
    # con los puntos repetidos alrededor para que la textura empalme sin costura
    puntos = [(rnd.uniform(0, N), rnd.uniform(0, N)) for _ in range(9)]
    for y in range(N):
        for x in range(N):
            ds = sorted(math.hypot(((x + 0.5 - px + N / 2) % N) - N / 2, ((y + 0.5 - py + N / 2) % N) - N / 2)
                        for px, py in puntos)
            if ds[1] - ds[0] < 1.1:
                q[x, y] = RED + (190,)
    # motas de luz sueltas
    for _ in range(10):
        x, y = rnd.randrange(N), rnd.randrange(4, N - 4)
        q[x, y] = BORDE + (210,)
    # el borde en el suelo: canto, claro, claro
    for x in range(N):
        q[x, N - 1] = CANTO + (230,)
        q[x, N - 2] = BORDE + (220,)
        q[x, N - 3] = RED + (180,)
    # el brillo de arriba
    for y in range(4):
        for x in range(N):
            r, g, b, a = q[x, y]
            q[x, y] = (min(255, r + 30), min(255, g + 12), b, min(255, a + 30 - 7 * y))
    p = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/nerea/cupula.png')
    im.save(p)
    print('ok', p)


if __name__ == '__main__':
    main()

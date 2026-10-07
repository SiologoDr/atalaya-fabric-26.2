"""
La calle de aviso del Rompeolas (testers, 07-10-2026: "los golpes llegan sin
aviso"): por donde va a correr cada pared de agua, pintado en el suelo durante
la espera de aviso.

Antes se reutilizaba el camino de la Gran Marea (baldosas claras pensadas para
blanco): tenida de rojo salia punteada y no se leia sobre la hierba (DISENO.md,
punto 19, corolario). Esta es propia:

  - los dos cantos, solidos: marcan el ancho exacto de la ola
  - por dentro, un velo rojo flojo
  - una flecha por baldosa apuntando hacia fuera (v crece al alejarse del jefe);
    el juego la desplaza, asi que corren en el sentido de la ola

El color va dentro de la imagen (punto 7: la rampa gira de rojo hondo a
salmon claro) y el juego la tine de blanco. Canto apagado, nucleo claro (punto 1).
32 x 32: la baldosa mide 5 bloques de largo y la calle 5,2 de ancho, asi los
texeles salen casi cuadrados.

Uso: python aviso_calle.py <raiz del proyecto>
"""
import os
import sys

import numpy as np
from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
N = 32

HONDO = (150, 24, 34)
ROJO = (232, 52, 44)
VIVO = (255, 96, 72)
CLARO = (255, 176, 150)


def main():
    out = np.zeros((N, N, 4), np.uint8)
    # el velo de dentro
    out[:, :, :3] = ROJO
    out[:, :, 3] = 64
    # la flecha: punta en la fila 24, brazos hacia atras hasta x = 5 y x = 26
    for y in range(N):
        for x in range(N):
            d = abs(x - 15.5)
            if d > 11:
                continue
            fondo = 24 - d * 0.75          # la fila del borde delantero en esa columna
            k = fondo - y                  # 0 en el borde delantero, crece hacia atras
            if 0 <= k < 5:
                col = CLARO if 1 <= k < 3 else VIVO if k < 4 else ROJO
                out[y, x, :3] = col
                out[y, x, 3] = 230 if col != ROJO else 170
    # los cantos: tres columnas a cada lado, de fuera a dentro hondo, vivo, claro
    for cols, col, a in (((0, 31), HONDO, 255), ((1, 30), VIVO, 255), ((2, 29), CLARO, 235), ((3, 28), VIVO, 150)):
        for c in cols:
            out[:, c, :3] = col
            out[:, c, 3] = a
    p = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/nerea/aviso_calle.png')
    Image.fromarray(out, 'RGBA').save(p)
    print('ok', p)


if __name__ == '__main__':
    main()

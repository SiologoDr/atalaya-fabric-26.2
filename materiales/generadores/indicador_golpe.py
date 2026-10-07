"""
El indicador de direccion del golpe (testers, 07-10-2026: "no podia distinguir de
donde venian los golpes"): un arco rojo que se pinta alrededor de la mira,
girado hacia donde vino el dano.

La textura es el trozo de arco de arriba (apunta "de frente"); el juego la gira.
Se pinta a la mitad (64 x 24 -> 32 x 12 de interfaz), asi sale limpia en
cualquier escala. Rampa de rojo con el canto mas oscuro (no negro) y el nucleo
claro tirando a rojo (DISENO.md, punto 4); las puntas se desvanecen.

Uso: python indicador_golpe.py <raiz del proyecto>
"""
import math
import os
import sys

import numpy as np
from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
W, H = 64, 24
CX, CY = 32.0, 120.0           # el centro del arco (la mira), debajo de la textura
R0, R1 = 104.0, 112.0          # grosor del arco
MEDIO = 17.0                   # media apertura en grados

BORDE = np.array([150, 24, 34], dtype=np.float32)
MEDIO_C = np.array([232, 52, 44], dtype=np.float32)
NUCLEO = np.array([255, 168, 150], dtype=np.float32)


def suave(k):
    k = np.clip(k, 0, 1)
    return k * k * (3 - 2 * k)


def main():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) + 0.5
    r = np.hypot(xx - CX, yy - CY)
    a = np.degrees(np.arctan2(xx - CX, CY - yy))
    dentro = (r >= R0) & (r <= R1) & (np.abs(a) <= MEDIO)
    k = (r - R0) / (R1 - R0)                      # 0 dentro (hacia la mira), 1 fuera
    centro = 1 - np.abs(k - 0.45) / 0.55          # 1 en el nucleo
    col = BORDE + (MEDIO_C - BORDE) * suave(centro * 1.6)[..., None]
    col = col + (NUCLEO - col) * suave((centro - 0.7) / 0.3)[..., None]
    alfa = suave((MEDIO - np.abs(a)) / 6.0) * (0.55 + 0.45 * suave(centro * 1.4))
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    out[..., 3] = np.where(dentro, (alfa * 255).astype(np.uint8), 0)
    p = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/indicador_golpe.png')
    Image.fromarray(out, 'RGBA').save(p)
    print('ok', p)


if __name__ == '__main__':
    main()

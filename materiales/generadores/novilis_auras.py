"""
Las auras de Novilis sobre su atlas (el de novilis_juego.py): la misma malla un
poco hinchada (NovilisMalla.crearAura) con estas texturas encima.

  novilis_aura_azul_0..11      la Furia: lenguas de fuego azul que suben
  novilis_aura_carmesi_0..11   el Dios de la Guerra: llamas carmesi

Doce cuadros que se funden uno con el siguiente (como las Furias de Nerea y
Aeralis): las llamas suben seguidas, sin saltos. Fuera de las lenguas es
transparente; brilla sin luz.

Uso: python novilis_auras.py <raiz del proyecto>
"""
import os, sys, math
import numpy as np
from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/novilis')
CUADROS = 12

COLORES = {
    'azul': [(10, 40, 110), (30, 120, 220), (90, 216, 255), (225, 248, 255)],
    'carmesi': [(70, 6, 14), (170, 16, 34), (255, 42, 58), (255, 200, 190)],
}


def aura(base, k, rampa):
    h, w = base.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    # Lenguas que suben (la v baja con el tiempo) y se mecen a los lados.
    sube = (yy + k * 16.0 / CUADROS) % 16.0
    meneo = 2.2 * np.sin(2 * math.pi * (xx / 11.0 + k / CUADROS)) + 1.4 * np.sin(2 * math.pi * (xx / 5.0 - k / CUADROS * 2))
    s = (sube + meneo) % 16.0
    lengua = np.clip(1.0 - np.abs(s - 8.0) / 8.0, 0, 1) ** 2.2
    trama = ((xx * 7 + yy * 3) % 5 < 3).astype(float) * 0.25 + 0.75
    v = lengua * trama
    out = np.zeros((h, w, 4), np.uint8)
    for i, umbral in enumerate((0.15, 0.4, 0.65, 0.85)):
        m = v > umbral
        out[m] = (*rampa[i], 255)
    out[base[..., 3] < 16] = 0
    return out


if __name__ == '__main__':
    base = np.array(Image.open(os.path.join(TEX, 'novilis_f1.png')).convert('RGBA'))
    for nombre, rampa in COLORES.items():
        for k in range(CUADROS):
            Image.fromarray(aura(base, k, rampa)).save(os.path.join(TEX, f'novilis_aura_{nombre}_{k}.png'))
    print('ok', CUADROS, 'cuadros x', len(COLORES))

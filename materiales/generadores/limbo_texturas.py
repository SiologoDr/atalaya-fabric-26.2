"""
Las texturas del Limbo (18-10-2026), a píxeles (16 x 16, como los bloques de Minecraft):

  textures/block/piedra_limbo   los muros y el techo del laberinto: sillares de una piedra gris violácea, con las juntas
                                hundidas y alguna veta violeta que apenas brilla
  textures/block/suelo_limbo    las losas del suelo: más oscuras, en cuadros grandes, con una runa gastada en algunas
  textures/block/farol_limbo    el farol de pared: un marco de piedra oscura con una llama fría (blanca y violeta) que
                                tiembla (animada, 4 cuadros)
  textures/block/salida_limbo   la salida: luz que da vueltas en espiral, del blanco al dorado y al violeta (animada,
                                8 cuadros)
  textures/particle/bestia_limbo_luz_0..2   las motas de luz que suben de la salida
  textures/particle/bestia_limbo_bruma_0..2 la bruma violeta que flota por el laberinto

Uso: python limbo_texturas.py <raíz>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
ASSETS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
BLOQUE = os.path.join(ASSETS, 'textures/block')
PARTICULA = os.path.join(ASSETS, 'textures/particle')
rng = np.random.default_rng(20261023)


def H(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), float)


def rampa(*c):
    return np.array([H(x) for x in c])


def guardar(arr, ruta, cuadros=None, tiempo=2):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(ruta)
    if cuadros:
        with open(ruta + '.mcmeta', 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'animation': {'frametime': tiempo, 'interpolate': False}}, fh, indent=2)
            fh.write('\n')
    print('ok', os.path.relpath(ruta, RAIZ))


PIEDRA = rampa('16121e', '221c2c', '2e263a', '3a3248', '4a4058', '5a4e6a')
VETA = rampa('3a2266', '5a34a0', '8a5ad8', 'c0a0ff')


def piedra():
    """Sillares de 8 x 4 (desplazados en hiladas), cada uno con su tono, el canto de arriba claro y la junta oscura."""
    a = np.zeros((16, 16, 3))
    for y in range(16):
        fila = y // 4
        for x in range(16):
            xx = (x + (fila % 2) * 4) % 16
            sillar = (fila, (x + (fila % 2) * 4) // 8)
            base = 2 + (hash(sillar) % 2)
            junta = (y % 4 == 3) or (xx % 8 == 7)
            idx = 0 if junta else base
            if not junta and y % 4 == 0:
                idx = min(5, base + 1)
            if not junta and rng.random() < 0.12:
                idx = max(1, idx - 1)
            a[y, x] = PIEDRA[idx]
    # Una veta violeta que cruza un sillar.
    x, y = 3, 1
    for k in range(9):
        if 0 <= x < 16 and 0 <= y < 16 and not (y % 4 == 3):
            a[y, x] = VETA[1 if k % 3 else 2]
        x += 1
        y += 1 if k % 2 else 0
    guardar(a, os.path.join(BLOQUE, 'piedra_limbo.png'))


SUELO = rampa('0e0b14', '17121f', '201a2b', '2a2236', '342b42')


def suelo():
    """Losas de 8 x 8 con su junta y el borde de arriba un pelo más claro; en una, una runa gastada."""
    a = np.zeros((16, 16, 3))
    for y in range(16):
        for x in range(16):
            junta = (x % 8 == 0) or (y % 8 == 0)
            losa = (x // 8, y // 8)
            base = 2 + ((losa[0] + losa[1]) % 2)
            idx = 0 if junta else base
            if not junta and (x % 8 == 1 or y % 8 == 1):
                idx = min(4, base + 1)
            if not junta and rng.random() < 0.1:
                idx = max(1, idx - 1)
            a[y, x] = SUELO[idx]
    # La runa (un ojo cerrado, de líneas de un píxel) en la losa de abajo a la derecha.
    for (x, y) in ((10, 12), (11, 11), (12, 11), (13, 11), (14, 12), (11, 13), (12, 13), (13, 13), (12, 14)):
        a[y, x] = VETA[0]
    guardar(a, os.path.join(BLOQUE, 'suelo_limbo.png'))


LLAMA = rampa('2a1a4a', '5a3aa0', '9070e0', 'c8b8ff', 'f4f0ff', 'ffffff')


def farol():
    """El farol de pared: marco de piedra oscura (2 px), dentro una reja de hierro negro y la llama fría que tiembla."""
    cuadros = []
    for k in range(4):
        a = np.zeros((16, 16, 3))
        for y in range(16):
            for x in range(16):
                borde = min(x, y, 15 - x, 15 - y)
                if borde < 2:
                    a[y, x] = PIEDRA[1 if borde == 0 else 3]
                else:
                    a[y, x] = PIEDRA[0]
        # La llama: una gota que tiembla (su punta se mueve).
        cx = 7.5 + (0.6 if k in (1, 2) else -0.4)
        for y in range(3, 14):
            for x in range(3, 13):
                v = (y - 3) / 10.0
                ancho = 3.6 * math.sin(math.pi * min(1.0, v * 1.05)) ** 0.8 * (0.85 + 0.15 * ((k + y) % 2))
                d = abs(x - (cx + (1 - v) * (0.8 if k % 2 else -0.8)))
                if d < ancho and y > 3 + (k % 2):
                    nivel = 1 + int((1 - d / ancho) * 4 * (0.6 + 0.4 * v))
                    a[y, x] = LLAMA[min(5, nivel)]
        # La reja: dos barrotes verticales y uno horizontal.
        for y in range(2, 14):
            a[y, 5] = a[y, 10] = H('0c0a10')
        for x in range(2, 14):
            a[8, x] = H('0c0a10')
        cuadros.append(a)
    guardar(np.vstack(cuadros), os.path.join(BLOQUE, 'farol_limbo.png'), cuadros=True, tiempo=3)


LUZ = rampa('3a1a6a', '7a4ac8', 'c098ff', 'ffe6a0', 'fff8e0', 'ffffff')


def salida():
    """La salida: brazos de luz en espiral que giran (8 cuadros), del violeta del borde al blanco del centro."""
    cuadros = []
    for k in range(8):
        a = np.zeros((16, 16, 3))
        for y in range(16):
            for x in range(16):
                u, v = x - 7.5, y - 7.5
                r = math.hypot(u, v) / 8.0
                ang = math.atan2(v, u)
                brazo = 0.5 + 0.5 * math.cos(3 * ang - 6.0 * r + k * math.tau / 8)
                n = (1.0 - min(1.0, r)) * 0.75 + brazo * 0.45
                a[y, x] = LUZ[min(5, max(0, int(n * 5.2)))]
        cuadros.append(a)
    guardar(np.vstack(cuadros), os.path.join(BLOQUE, 'salida_limbo.png'), cuadros=True, tiempo=2)


def particulas():
    def mota(k):
        n = 8
        a = np.zeros((n, n, 4))
        for y in range(n):
            for x in range(n):
                d = math.hypot(x - 3.5, y - 3.5)
                if d < 3.2 - k * 0.8:
                    c = LUZ[5] if d < 1.0 else LUZ[3] if d < 2.0 else LUZ[2]
                    a[y, x] = (*c, 255)
        return a

    def bruma(k):
        n = 16
        a = np.zeros((n, n, 4))
        for y in range(n):
            for x in range(n):
                d = math.hypot(x - 7.5, (y - 7.5) * 1.3)
                if d < 7.0 - k:
                    al = 60 if d > 4.5 - k * 0.5 else 95
                    a[y, x] = (*H('6a4aa0'), al)
        return a
    for nombre, fn in (('luz', mota), ('bruma', bruma)):
        nombres = []
        for k in range(3):
            n = f'bestia_limbo_{nombre}_{k}'
            os.makedirs(PARTICULA, exist_ok=True)
            Image.fromarray(fn(k).astype(np.uint8)).save(os.path.join(PARTICULA, n + '.png'))
            nombres.append(f'atalaya:{n}')
        os.makedirs(os.path.join(ASSETS, 'particles'), exist_ok=True)
        with open(os.path.join(ASSETS, f'particles/bestia_limbo_{nombre}.json'), 'w', encoding='utf-8',
                  newline='\n') as fh:
            json.dump({'textures': nombres}, fh, indent=2)
            fh.write('\n')
        print('ok particula', nombre)


def modelos():
    """Los blockstates y los modelos (cubos enteros) de los cuatro bloques."""
    for b in ('piedra_limbo', 'suelo_limbo', 'farol_limbo', 'salida_limbo'):
        ruta = os.path.join(ASSETS, f'blockstates/{b}.json')
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'variants': {'': {'model': f'atalaya:block/{b}'}}}, fh, indent=2)
            fh.write('\n')
        ruta = os.path.join(ASSETS, f'models/block/{b}.json')
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'parent': 'minecraft:block/cube_all', 'textures': {'all': f'atalaya:block/{b}'}}, fh, indent=2)
            fh.write('\n')
    print('ok modelos')


def main():
    piedra()
    suelo()
    farol()
    salida()
    particulas()
    modelos()


if __name__ == '__main__':
    main()

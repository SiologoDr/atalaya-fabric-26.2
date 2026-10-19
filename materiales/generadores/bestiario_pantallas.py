"""
Lo que los mobs del bestiario ponen en la pantalla y sus objetos (18-10-2026), a píxeles:

  textures/gui/bestiario/estatica    la estática de una pantalla sin señal (el Creeper Gelatina), en grano grueso y con
                                     las líneas de barrido; el HUD la mueve cada fotograma
  textures/gui/bestiario/sin_senal   «SIN SEÑAL» con las letras de píxel de los rótulos (las de la Ruleta)
  textures/gui/bestiario/nata        cuatro pegotes de nata con sus chorretones (el Creeper Tarta te pringa)
  textures/gui/bestiario/lianas      la barra de las lianas (el Creeper Enredadera te atrapa): el marco de madera
                                     enroscado y, debajo, el relleno de hojas
  textures/gui/bestiario/tecla       una tecla en blanco de 16 x 16 (suelta y pulsada), como la de la tecla espacio: el
                                     HUD le escribe encima la letra de la que toca (las lianas te piden W, A, S o D)
  textures/gui/bestiario/escarcha    la escarcha que cubre la pantalla al quedarte congelado (la Fauces de Escarcha):
                                     cristales en pluma que crecen desde los bordes, a píxeles
  textures/mob_effect/enraizado      el icono del efecto Enraizado (un brote con sus raíces)
  textures/mob_effect/congelado      el icono del efecto Congelado (un bloque de hielo)

Uso: python bestiario_pantallas.py <raíz>
"""
import os
import sys

import numpy as np
from PIL import Image

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
sys.argv = sys.argv[:1] + [RAIZ]
import ruleta  # noqa: E402  (las letras de píxel de los rótulos)

GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/bestiario')
ITEM = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
EFE = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/mob_effect')
rng = np.random.default_rng(20261018)


def H(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), float)


def guardar(arr, ruta):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(ruta)
    print('ok', os.path.relpath(ruta, RAIZ))


def vecinos(m, r=1):
    out = np.zeros_like(m)
    h, w = m.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if abs(dx) + abs(dy) <= r:
                out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] |= \
                    m[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
    return out


# ======================================================================================================================
#  La estática
# ======================================================================================================================
def estatica():
    """512 x 512 de grano gris en celdas de 2 x 2, con las líneas de barrido más oscuras y unas bandas que tiemblan
    (el HUD coge un trozo distinto cada fotograma)."""
    n = 512
    grano = rng.integers(0, 256, (n // 2, n // 2)).repeat(2, 0).repeat(2, 1).astype(float)
    grano = 30 + grano * 0.82
    ys = np.arange(n)[:, None]
    grano *= np.where((ys % 2) == 1, 0.72, 1.0)
    banda = 1.0 + 0.18 * np.sin(ys / n * np.pi * 9) * (rng.random((n, 1)) > 0.3)
    g = grano * banda
    arr = np.zeros((n, n, 4))
    arr[..., 0] = g * 0.96
    arr[..., 1] = g
    arr[..., 2] = g * 1.04
    arr[..., 3] = 255
    guardar(arr, os.path.join(GUI, 'estatica.png'))


# ======================================================================================================================
#  «SIN SEÑAL»
# ======================================================================================================================
def letras(texto, esc=4, grueso=2, hueco=6):
    """La máscara de un texto con las letras de píxel de los rótulos (con la tilde y la virgulilla encima)."""
    ancho = sum(len(ruleta.LETRA[c][0]) * esc + grueso + hueco for c in texto) - hueco
    alto = 7 * esc + esc
    m = np.zeros((alto + 8, ancho + 8), bool)
    x = 4
    y0 = 4 + esc
    for c in texto:
        g = ruleta.LETRA[c]
        tilde = ruleta.TILDES.get(c)
        quita = ruleta.SIN_FILA.get(c, 2)
        filas = g[:quita] + g[quita + 1:] if tilde else g
        dy0 = y0 + (esc if tilde else 0)
        for fy, fila in enumerate(filas):
            for fx, ch in enumerate(fila):
                if ch == '#':
                    m[dy0 + fy * esc:dy0 + (fy + 1) * esc, x + fx * esc:x + (fx + 1) * esc + grueso] = True
        if tilde:
            h = esc // 2
            cx = x + (len(g[0]) * esc) // 2
            celdas = {'tilde': ((1, 0), (0, 1)), 'dieresis': ((-2, 0), (-2, 1), (1, 0), (1, 1)),
                      'virgulilla': ((-2, 1), (-1, 0), (0, 1), (1, 0))}[tilde]
            for cxl, cyl in celdas:
                xa, ya = cx + cxl * h, y0 - esc + cyl * h + esc // 2
                m[ya:ya + h, xa:xa + h + grueso // 2] = True
        x += len(g[0]) * esc + grueso + hueco
    return m


def sin_senal():
    """Las letras blancas con el contorno negro y la sombra, como un rótulo de televisión."""
    m = letras('SIN SEÑAL', 4, 2, 6)
    h, w = m.shape
    arr = np.zeros((h + 4, w + 4, 4))
    mm = np.zeros((h + 4, w + 4), bool)
    mm[2:2 + h, 2:2 + w] = m
    contorno = vecinos(mm, 2) & ~mm
    sombra = np.zeros_like(mm)
    sombra[3:, 2:] = (mm | contorno)[:-3, :-2]
    sombra &= ~(mm | contorno)
    arr[sombra] = (0, 0, 0, 120)
    arr[contorno] = (10, 10, 14, 255)
    ys = np.arange(h + 4)[:, None] * np.ones((1, w + 4))
    claro = np.where(ys < (h + 4) * 0.5, 255, 222)
    arr[mm, 0] = claro[mm]
    arr[mm, 1] = claro[mm]
    arr[mm, 2] = claro[mm]
    arr[mm, 3] = 255
    guardar(arr, os.path.join(GUI, 'sin_senal.png'))
    return arr.shape


# ======================================================================================================================
#  La nata
# ======================================================================================================================
def nata():
    """Cuatro pegotes de nata (64 x 64 cada uno, en una tira de 256 x 64): una mancha redonda con salpicaduras y
    chorretones que caen, la luz arriba a la izquierda y el borde un poco más oscuro (a píxeles, sin suavizar)."""
    W = 64
    hoja = np.zeros((W, W * 4, 4))
    ys, xs = np.mgrid[0:W, 0:W].astype(float)
    for k in range(4):
        g = np.random.default_rng(700 + k)
        cx, cy = 32 + g.uniform(-4, 4), 26 + g.uniform(-3, 3)
        ang = np.arctan2(ys - cy, xs - cx)
        rr = np.hypot(xs - cx, ys - cy)
        borde = (15 + 2.2 * np.sin(ang * 2 + g.uniform(0, 6)) + 1.6 * np.sin(ang * 3 + g.uniform(0, 6))
                 + 1.0 * np.sin(ang * 7 + g.uniform(0, 6)))
        m = rr < borde
        # Salpicaduras alrededor.
        for _ in range(7):
            a = g.uniform(0, 2 * np.pi)
            d = g.uniform(20, 27)
            r = g.uniform(1.5, 3.2)
            m |= np.hypot(xs - (cx + np.cos(a) * d), ys - (cy + np.sin(a) * d)) < r
        # Chorretones: bajan desde el borde de abajo y acaban en gota.
        for _ in range(3):
            x0 = cx + g.uniform(-10, 10)
            largo = g.uniform(10, 24)
            ancho = g.uniform(1.8, 3.0)
            y0 = cy + 8
            m |= (np.abs(xs - x0) < ancho) & (ys > y0) & (ys < y0 + largo)
            m |= np.hypot(xs - x0, ys - (y0 + largo)) < ancho + 1.2
        m &= (xs > 0) & (xs < W - 1) & (ys > 0) & (ys < W - 1)
        luz = (xs - cx) * -0.5 + (ys - cy) * -0.6
        tono = np.where(luz > 6, 255, np.where(luz > -6, 244, 226))
        canto = vecinos(~m, 1) & m
        tono = np.where(canto, 206, tono)
        brillo = (np.hypot(xs - (cx - 6), ys - (cy - 6)) < 3.2) & m
        tono = np.where(brillo, 255, tono)
        trozo = np.zeros((W, W, 4))
        trozo[..., 0] = tono
        trozo[..., 1] = tono * 0.985
        trozo[..., 2] = tono * 0.955
        trozo[..., 3] = np.where(m, 255, 0)
        trozo[brillo, :3] = (255, 255, 255)
        hoja[:, k * W:(k + 1) * W] = trozo
    guardar(hoja, os.path.join(GUI, 'nata.png'))


# ======================================================================================================================
#  La barra de las lianas
# ======================================================================================================================
def lianas():
    """128 x 32: arriba el marco (una vara de madera de 120 x 12 con las lianas enroscadas y dos hojas) y abajo el
    relleno (hojas de azalea), que el HUD recorta según lo que falta para soltarse."""
    W, Hh = 128, 32
    arr = np.zeros((Hh, W, 4))
    madera = [H('24180e'), H('3a2816'), H('563c22'), H('765632'), H('987448')]
    hoja = [H('16300e'), H('244a18'), H('366624'), H('4e8632'), H('6ea644')]
    rosa = H('d8609c')
    x0, x1 = 2, 122
    for y in range(12):
        for x in range(x0, x1):
            borde = y in (0, 11) or x in (x0, x1 - 1)
            hueco = 2 <= y <= 9 and x0 + 2 <= x < x1 - 2
            if hueco:
                arr[y, x] = (*H('0e0a06'), 220)
            elif borde:
                arr[y, x] = (*madera[0], 255)
            else:
                arr[y, x] = (*madera[3 if y < 2 else 2], 255)
    # Las lianas enroscadas: una diagonal cada 9 píxeles por encima del marco.
    for k in range(x0 + 3, x1 - 3, 9):
        for d in range(12):
            x, y = k + d // 2, d
            if x0 <= x < x1:
                arr[y, x] = (*hoja[2 if d % 3 else 3], 255)
    # Dos hojas y una flor en las puntas.
    for (hx, hy) in ((0, 3), (1, 4), (0, 5), (123, 3), (124, 4), (125, 5), (124, 6)):
        arr[hy, hx] = (*hoja[3], 255)
    arr[2, 124] = (*rosa, 255)
    # El relleno: hojas en filas, con su nervio claro.
    for y in range(8):
        for x in range(116):
            v = hoja[2]
            if (x + (y // 2) * 3) % 6 == 0:
                v = hoja[4]
            elif y in (0, 7):
                v = hoja[1]
            elif (x + y) % 5 == 0:
                v = hoja[3]
            arr[16 + 2 + y, x0 + 2 + x] = (*v, 255)
    guardar(arr, os.path.join(GUI, 'lianas.png'))


# ======================================================================================================================
#  La tecla en blanco
# ======================================================================================================================
def tecla():
    """16 x 32: arriba la tecla suelta (la cara clara con su canto oscuro abajo y su sombra) y abajo la pulsada (más
    oscura, dos píxeles más abajo y sin canto), con los colores de tecla_espacio."""
    arr = np.zeros((32, 16, 4))
    borde, cara, canto, sombra, pulsada = H('1c1a18'), H('d6d2ca'), H('706c66'), H('343230'), H('a8a49c')
    for y0, c, con_canto in ((0, cara, True), (16 + 2, pulsada, False)):
        alto = 12 if con_canto else 10
        for y in range(alto + 1):
            for x in range(1, 15):
                yy = y0 + 1 + y
                if y in (0, alto) or x in (1, 14):
                    arr[yy, x] = (*borde, 255)
                elif con_canto and y == alto - 1:
                    arr[yy, x] = (*canto, 255)
                else:
                    arr[yy, x] = (*c, 255)
        for x in range(2, 15):
            arr[y0 + 1 + alto + 1, x] = (*sombra, 255)
    guardar(arr, os.path.join(GUI, 'tecla.png'))


# ======================================================================================================================
#  La escarcha (Congelado)
# ======================================================================================================================
def escarcha():
    """320 x 180: cristales en pluma (líneas de un píxel que crecen hacia dentro y echan ramas a 60 grados) desde los
    cuatro bordes, sobre una capa de escarcha que se espesa hacia el borde. El centro, limpio."""
    w, h = 320, 180
    ys, xs = np.mgrid[0:h, 0:w]
    borde = np.minimum(np.minimum(xs, w - 1 - xs), np.minimum(ys, h - 1 - ys)).astype(float)
    # Lo que llega la capa: entre 8 y 26 píxeles, ondulando.
    ang = np.arctan2(ys - h / 2, (xs - w / 2) * h / w)
    llega = 14 + 6 * np.sin(ang * 7 + 1.3) + 4 * np.sin(ang * 13 + 0.4)
    capa = np.clip(1.0 - borde / llega, 0, 1)
    cristal = np.zeros((h, w), bool)
    semillas = []
    for x in range(0, w, 7):
        semillas += [(x + rng.uniform(0, 5), 0.0), (x + rng.uniform(0, 5), h - 1.0)]
    for y in range(0, h, 7):
        semillas += [(0.0, y + rng.uniform(0, 5)), (w - 1.0, y + rng.uniform(0, 5))]
    pendientes = []
    for (x, y) in semillas:
        a = np.arctan2(h / 2 - y, (w / 2 - x) * h / w) + rng.normal(0, 0.35)
        pendientes.append((x, y, a, int(rng.integers(14, 46)), 0))
    while pendientes:
        x, y, a, L, nivel = pendientes.pop()
        for paso in range(L):
            xi, yi = int(round(x)), int(round(y))
            if not (0 <= xi < w and 0 <= yi < h):
                break
            cristal[yi, xi] = True
            x, y = x + np.cos(a), y + np.sin(a)
            a += rng.normal(0, 0.06)
            if nivel < 2 and paso > 2 and rng.random() < 0.09:
                lado = rng.choice((-1, 1))
                pendientes.append((x, y, a + lado * np.pi / 3, max(3, (L - paso) // 2), nivel + 1))
    halo = vecinos(cristal) & ~cristal
    arr = np.zeros((h, w, 4), float)
    # La capa: blanca azulada, más opaca al borde, en escalones (nada de degradado suave).
    esc = np.floor(capa * 4) / 4
    arr[..., :3] = H('cff4ff')
    arr[..., 3] = esc * 150
    arr[halo, :3] = H('9ee6ff')
    arr[halo, 3] = np.maximum(arr[halo, 3], 160)
    arr[cristal, :3] = H('f4feff')
    arr[cristal, 3] = 235
    guardar(arr, os.path.join(GUI, 'escarcha.png'))


# ======================================================================================================================
#  Los iconos de los efectos de las plantas
# ======================================================================================================================
ENRAIZADO = """
..................
.......LL.........
.....LLGG..LL.....
....LGGGG.LGGL....
.....gGGG.GGGg....
......ggG.Gg......
.........R........
.........R........
........HRr.......
.......HRRRr......
......HR.R.Rr.....
....HRr..R..rR....
...Rr...HRr...rR..
..Rr...R.R.r...rR.
.r....R..R..r....r
.....r...R...r....
.........r........
..................
"""


def iconos_efectos():
    colores = {'L': 'b8f070', 'G': '5aac36', 'g': '2f6a1c', 'H': 'c89a60', 'R': '8e6634', 'r': '4a3018'}
    filas = [f for f in ENRAIZADO.strip('\n').split('\n')]
    arr = np.zeros((18, 18, 4), float)
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch in colores:
                arr[y, x, :3] = H(colores[ch])
                arr[y, x, 3] = 255
    for (x, y) in ((3, 6), (14, 7), (2, 16), (15, 16)):
        arr[y, x] = (*H('d8ffb0'), 255)
    guardar(arr, os.path.join(EFE, 'enraizado.png'))
    # El bloque de hielo, en perspectiva: la cara de arriba clara, la izquierda media, la derecha oscura, con un
    # brillo en diagonal y una grieta.
    arr = np.zeros((18, 18, 4), float)
    arriba, izq, der, borde = H('e4fbff'), H('8ee2f6'), H('4ab4dc'), H('2a6a9a')
    for y in range(18):
        for x in range(18):
            px, py = x + 0.5, y + 0.5
            dx = abs(px - 9.0)
            sup = abs(px - 9.0) / 6.5 + abs(py - 5.0) / 3.5 <= 1.0
            costado = 2.5 <= px <= 15.5 and (py >= 5.0 + 3.5 * (1 - dx / 6.5)) and py <= 13.0 + 3.5 * (1 - dx / 6.5)
            if sup:
                arr[y, x] = (*arriba, 255)
            elif costado:
                arr[y, x] = (*(izq if px < 9.0 else der), 255)
    a = arr[..., 3] > 0
    contorno = vecinos(a) & ~a
    arr[contorno] = (*borde, 255)
    for (x, y) in ((5, 9), (5, 10), (6, 10), (6, 11), (4, 8)):
        arr[y, x] = (*H('ffffff'), 255)
    for (x, y) in ((12, 9), (13, 10), (12, 11), (13, 12)):
        arr[y, x] = (*H('2a7aa8'), 255)
    for (x, y) in ((8, 3), (9, 3), (10, 4)):
        arr[y, x] = (*H('ffffff'), 255)
    for (x, y) in ((1, 2), (16, 3), (0, 14), (17, 12)):
        arr[y, x] = (*H('c8f4ff'), 255)
    guardar(arr, os.path.join(EFE, 'congelado.png'))


def main():
    estatica()
    tecla()
    print('sin_senal', sin_senal())
    nata()
    lianas()
    escarcha()
    iconos_efectos()


if __name__ == '__main__':
    main()

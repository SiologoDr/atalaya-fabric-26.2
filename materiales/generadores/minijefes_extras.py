"""
Lo que acompana a los cuatro mini jefes en el juego, dibujado desde cero (nada de vanilla):

  textures/particle/mj_*.png (+ particles/mj_*.json)   sus particulas: astillas de jade y de obsidiana, polvo,
                                                       plumas de quetzal, fragmentos, el glifo donde cae algo, la
                                                       onda, jirones de viento, runas, gotas, espuma, burbujas,
                                                       brasas, llamas, plumas de fuego, ceniza, el destello y la
                                                       grieta de jade
  textures/entity/minijefes/efectos/*.png              lo grande de sus ataques: el brillo, el sol, las estelas
                                                       (obsidiana, viento y agua), la cuchilla de viento, los
                                                       anillos de viento y de fuego, el ciclon, la ola y su espuma,
                                                       el tsunami, el chorro, el cristal de jade, el remolino de la
                                                       tormenta, las llamas de la columna y la pluma de fuego
  textures/gui/minijefes/<nombre>_marco|relleno|nombre  su barra de vida, como la de los jefes pero mas baja (220x32;
                          |muesca|muesca_rota          la de los jefes mide 240x44): el medallon con su emblema, la
                                                       barra de bloques de su material con su punta, la cresta de su
                                                       elemento, la energia que corre, su nombre en las letras de
                                                       pixel de las barras y las muescas

Las particulas son pixel art pequeno (16x16, las de suelo 32x32), como las de los jefes. Las texturas de efecto
son blancas o de su color con la alfa como fuerza: el juego las tine y las suma.

Uso: python minijefes_extras.py <raiz del proyecto> [hoja de muestra.png | solo-barras]
"""
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image

import presentacion_jefes as pj

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
HOJA = sys.argv[2] if len(sys.argv) > 2 else None
ASSETS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
PART = os.path.join(ASSETS, 'textures/particle')
PJSON = os.path.join(ASSETS, 'particles')
EFECTOS = os.path.join(ASSETS, 'textures/entity/minijefes/efectos')
GUI = os.path.join(ASSETS, 'textures/gui/minijefes')
for d in (PART, PJSON, EFECTOS, GUI):
    os.makedirs(d, exist_ok=True)
MUESTRAS = []


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def lienzo(w, h):
    return np.zeros((h, w, 4), np.uint8)


def guardar(arr, ruta, muestra=True):
    im = Image.fromarray(np.asarray(arr, np.uint8), 'RGBA')
    im.save(ruta)
    if muestra:
        MUESTRAS.append((os.path.basename(ruta), im))


def rgba(color, alfa):
    """Una imagen de un color con la alfa dada (0 a 1)."""
    h, w = alfa.shape
    t = np.zeros((h, w, 4), np.uint8)
    t[..., :3] = np.array(color[:3], np.uint8)
    t[..., 3] = np.clip(alfa * 255, 0, 255).astype(np.uint8)
    return t


def gradiente(cols, k):
    """Color de una rampa (lista de (r, g, b)) en k (array de 0 a 1)."""
    cols = np.array(cols, float)
    k = np.clip(k, 0, 1) * (len(cols) - 1)
    i = np.minimum(k.astype(int), len(cols) - 2)
    f = (k - i)[..., None]
    return cols[i] * (1 - f) + cols[i + 1] * f


def ruido(h, w, celda, semilla, periodico=True):
    """Ruido suave (0 a 1) con celdas de 'celda' pixeles; periodico en los dos ejes si se pide."""
    r = np.random.default_rng(semilla)
    nx, ny = max(1, round(w / celda)), max(1, round(h / celda))
    g = r.random((ny + 1, nx + 1))
    if periodico:
        g[-1, :] = g[0, :]
        g[:, -1] = g[:, 0]
    yy, xx = np.mgrid[0:h, 0:w]
    fx, fy = xx / w * nx, yy / h * ny
    ix, iy = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a = g[iy, ix] * (1 - tx) + g[iy, ix + 1] * tx
    b = g[iy + 1, ix] * (1 - tx) + g[iy + 1, ix + 1] * tx
    return a * (1 - ty) + b * ty


def fbm(h, w, celda, semilla, octavas=3):
    v = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    for o in range(octavas):
        v += amp * ruido(h, w, max(1, celda / 2 ** o), semilla + o * 17)
        tot += amp
        amp *= 0.5
    return v / tot


def radial(n, cx=None, cy=None):
    cx = (n - 1) / 2 if cx is None else cx
    cy = (n - 1) / 2 if cy is None else cy
    yy, xx = np.mgrid[0:n, 0:n]
    return np.hypot(xx - cx, yy - cy) / (n / 2), np.arctan2(yy - cy, xx - cx)


def poligono(img, pts, color):
    """Rellena un poligono (puntos en pixeles) con un color (pixel art: dentro o fuera)."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    px, py = xx + 0.5, yy + 0.5
    dentro = np.zeros((h, w), bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        cruza = ((y1 > py) != (y2 > py)) & (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-9) + x1)
        dentro ^= cruza
    img[dentro] = color
    return dentro


def contorno(img, color, solo_vacio=True):
    """Un contorno de un pixel alrededor de lo pintado."""
    a = img[..., 3] > 0
    borde = np.zeros_like(a)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        borde |= np.roll(np.roll(a, dy, 0), dx, 1)
    borde &= ~a
    img[borde] = color
    return img


def particula(nombre, cuadros):
    for i, c in enumerate(cuadros):
        guardar(c, os.path.join(PART, f'{nombre}_{i}.png'))
    with open(os.path.join(PJSON, f'{nombre}.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'textures': [f'atalaya:{nombre}_{i}' for i in range(len(cuadros))]}, fh, indent=2)
        fh.write('\n')


# ======================================================================
#  Particulas
# ======================================================================
def astilla(semilla, cols, brillo, n=16, tam=(4, 7)):
    """Una astilla: un poligono irregular con su cara clara y su filo."""
    r = random.Random(semilla)
    img = lienzo(n, n)
    c = n / 2
    k = r.randint(4, 6)
    radios = [r.uniform(tam[0] * 0.5, tam[1] * 0.5) for _ in range(k)]
    radios[0] *= 1.6
    ang0 = r.uniform(0, 6.28)
    pts = [(c + math.cos(ang0 + 6.28 * i / k) * radios[i], c + math.sin(ang0 + 6.28 * i / k) * radios[i]) for i in range(k)]
    dentro = poligono(img, pts, hexc(cols[1]))
    yy, xx = np.mgrid[0:n, 0:n]
    cara = dentro & ((xx - c) * math.cos(ang0) + (yy - c) * math.sin(ang0) < 0)
    img[cara] = hexc(cols[2])
    oscuro = dentro & ((xx - c) * math.cos(ang0 + 2.0) + (yy - c) * math.sin(ang0 + 2.0) > 1.2)
    img[oscuro] = hexc(cols[0])
    # El destello del filo.
    px, py = int(pts[0][0]), int(pts[0][1])
    if 0 <= px < n and 0 <= py < n:
        img[py, px] = hexc(brillo)
    contorno(img, hexc(cols[0]))
    return img


def bocanada(semilla, cols, k, n=16, tam=1.0, alfa_max=0.9):
    """Una bocanada (polvo, espuma, humo): manchas que se abren y se aclaran con k (0 a 1)."""
    d, _ = radial(n)
    nz = fbm(n, n, 5, semilla, 2)
    r = (0.55 + 0.35 * k) * tam
    a = np.clip((r - d) / 0.25 + (nz - 0.5) * 1.2, 0, 1) * (1 - 0.55 * k) * alfa_max
    a = np.round(a * 4) / 4
    col = gradiente(cols, np.clip(nz * 0.8 + k * 0.4, 0, 1))
    img = lienzo(n, n)
    img[..., :3] = col.astype(np.uint8)
    img[..., 3] = (a * 255).astype(np.uint8)
    return img


def destello_estrella(n, k, puntas=4, color=(255, 255, 255)):
    d, ang = radial(n)
    rayos = np.abs(np.cos(ang * puntas / 2)) ** 18
    a = np.clip(1 - d / (0.35 + 0.3 * k), 0, 1) ** 1.6 + rayos * np.clip(1 - d / (0.95 - 0.2 * k), 0, 1) * 0.9
    a = np.clip(a * (1 - 0.3 * k), 0, 1)
    return rgba(color, np.round(a * 6) / 6)


def particulas():
    JADE = ('0a3424', '23925a', '7ee0a8')
    particula('mj_jade', [astilla(10 + i, JADE, 'e8fff0', tam=(3, 6)) for i in range(3)])
    OBS = ('0c0a12', '221a2e', '4a3a68')
    particula('mj_obsidiana', [astilla(20 + i, OBS, 'c8b8ff', tam=(4, 8)) for i in range(3)])
    particula('mj_polvo', [bocanada(30 + i, [(110, 92, 70), (150, 130, 104), (190, 172, 146)], i / 2) for i in range(3)])
    # Plumas de quetzal: verde, turquesa y la roja.
    plumas = []
    for i, (a, b, c) in enumerate((('0f4a32', '2fab6a', '7ee0a8'), ('146070', '3cc0cc', 'a8f0f0'), ('8a1a14', 'd0402a', 'f8d65c'))):
        img = lienzo(16, 16)
        for t in np.linspace(0, 1, 40):
            x, y = 3 + 10 * t, 13 - 10 * t
            w = 2.6 * math.sin(math.pi * min(1, t * 1.15))
            for s in np.linspace(-w, w, 9):
                px, py = int(x + s * 0.7), int(y + s * 0.7)
                if 0 <= px < 16 and 0 <= py < 16:
                    img[py, px] = hexc(c if abs(s) < 0.5 else (b if t < 0.8 else c))
        contorno(img, hexc(a))
        plumas.append(img)
    particula('mj_pluma', plumas)
    # El fragmento: una esquirla grande de obsidiana con el nucleo de jade encendido.
    frag = []
    for i in range(2):
        img = astilla(40 + i, OBS, 'c8b8ff', tam=(9, 14))
        d, _ = radial(16)
        nucleo = (d < 0.28) & (img[..., 3] > 0)
        img[nucleo] = hexc('7affb0')
        frag.append(img)
    particula('mj_fragmento', frag)
    # El glifo de jade donde va a caer un fragmento: un sol azteca (aro, rayos y el centro), dos brillos.
    marcas = []
    for k in range(2):
        n = 32
        d, ang = radial(n)
        a = np.zeros((n, n))
        a += (np.abs(d - 0.86) < 0.07) * 1.0
        a += (np.abs(d - 0.62) < 0.05) * 0.8
        a += ((d > 0.66) & (d < 0.84) & (np.abs(np.cos(ang * 8)) > 0.86)) * 0.9
        a += (d < 0.22) * 0.7 + ((np.abs(d - 0.38) < 0.05) & (np.abs(np.sin(ang * 4)) > 0.5)) * 0.8
        a = np.clip(a, 0, 1) * (0.75 + 0.25 * k)
        col = gradiente([(60, 200, 120), (170, 255, 200)], np.clip(1 - d, 0, 1))
        img = rgba((0, 0, 0), a)
        img[..., :3] = col.astype(np.uint8)
        marcas.append(img)
    particula('mj_marca', marcas)
    # La onda: un aro blanco (lo tine el juego) que se adelgaza.
    ondas = []
    for k in range(3):
        d, _ = radial(32)
        g = 0.09 - 0.025 * k
        a = np.exp(-((d - 0.86) / g) ** 2) + 0.25 * np.exp(-((d - 0.78) / 0.12) ** 2) * (d < 0.86)
        ondas.append(rgba((255, 255, 255), np.round(np.clip(a, 0, 1) * 6) / 6))
    particula('mj_onda', ondas)
    # Jirones de viento: un rizo que se abre y se deshace.
    vientos = []
    for k in range(3):
        n = 16
        img = lienzo(n, n)
        for t in np.linspace(0, 1, 60):
            ang = t * 4.5 + k * 0.6
            rr = 1.5 + 5.5 * t
            x, y = 8 + math.cos(ang) * rr, 8 + math.sin(ang) * rr * 0.6
            if 0 <= int(x) < n and 0 <= int(y) < n:
                a = int(255 * (1 - t * 0.5) * (1 - k * 0.3))
                img[int(y), int(x)] = (230, 250, 255, a) if t < 0.5 else (170, 230, 255, a)
        vientos.append(img)
    particula('mj_viento', vientos)
    # Runas de viento: cuatro glifos celestes.
    GLIFOS = [["..#..", ".#.#.", "#...#", ".#.#.", "..#.."], ["#.#.#", ".###.", "..#..", ".###.", "#.#.#"],
              ["###..", "#....", "#.###", "#...#", "####."], [".#.#.", "#####", ".#.#.", "#####", ".#.#."]]
    runas = []
    for g in GLIFOS:
        img = lienzo(16, 16)
        for y, f in enumerate(g):
            for x, c in enumerate(f):
                if c == '#':
                    img[5 + y, 5 + x] = hexc('c8f8ff')
        contorno(img, hexc('3aa8e0', 200))
        runas.append(img)
    particula('mj_runa', runas)
    # Gotas: una lagrima azul con su brillo.
    gotas = []
    for k in range(2):
        img = lienzo(16, 16)
        poligono(img, [(8, 4 + k), (10.5, 9), (10, 11), (8, 12), (6, 11), (5.5, 9)], hexc('4ab8e8'))
        img[9:11, 7] = hexc('e8fcff')
        contorno(img, hexc('1a5a8a'))
        gotas.append(img)
    particula('mj_gota', gotas)
    particula('mj_espuma', [bocanada(60 + i, [(150, 220, 230), (220, 248, 250), (255, 255, 255)], i / 2, alfa_max=0.95)
                            for i in range(3)])
    # Burbujas: un aro con su brillo, y al final revienta.
    burb = []
    for k in range(3):
        d, _ = radial(16)
        if k < 2:
            a = (np.abs(d - (0.42 + 0.05 * k)) < 0.1) * 0.9
            img = rgba((180, 240, 255), a)
            img[5, 6] = (255, 255, 255, 255)
        else:
            _, ang = radial(16)
            a = ((np.abs(d - 0.6) < 0.08) & (np.abs(np.sin(ang * 4)) > 0.7)) * 0.8
            img = rgba((200, 245, 255), a)
        burb.append(img)
    particula('mj_burbuja', burb)
    # Brasas: un punto que se apaga (blanco amarillo, naranja, rojo).
    brasas = []
    for k, (c1, c2) in enumerate((('fff4c0', 'ffb040'), ('ffd060', 'ff7a20'), ('ff8a28', 'c82018'))):
        d, _ = radial(16)
        img = rgba(hexc(c2), np.clip(1 - d / 0.35, 0, 1) ** 1.2)
        img[d < 0.14] = hexc(c1)
        brasas.append(img)
    particula('mj_brasa', brasas)
    # Llamas del fenix: rojo, naranja y amarillo con la punta violeta, cuatro cuadros.
    llamas = []
    for k in range(4):
        n = 16
        yy, xx = np.mgrid[0:n, 0:n]
        v = yy / (n - 1)
        nz = fbm(n, n, 4, 70 + k, 2)
        ancho = 0.42 * np.sin(np.pi * np.clip(v * 1.05, 0, 1)) ** 0.8 * (1 - 0.18 * k)
        x = (xx - 7.5) / 8 + (nz - 0.5) * 0.5 * (1 - v)
        a = np.clip((ancho - np.abs(x)) * 6, 0, 1) * (v > 0.12 + 0.08 * k)
        col = gradiente([(176, 64, 255), (255, 70, 40), (255, 150, 40), (255, 230, 140), (255, 250, 220)],
                        np.clip(v * 1.1 - np.abs(x) * 0.8, 0, 1))
        img = lienzo(n, n)
        img[..., :3] = col.astype(np.uint8)
        img[..., 3] = (np.round(a * 4) / 4 * 255).astype(np.uint8)
        llamas.append(img)
    particula('mj_llama', llamas)
    # Plumas de fuego: roja con la punta en llamas.
    pf = []
    for k in range(2):
        img = lienzo(16, 16)
        for t in np.linspace(0, 1, 48):
            x, y = 3 + 10 * t, 13 - 10 * t
            w = 2.4 * math.sin(math.pi * min(1, t * 1.1))
            for s in np.linspace(-w, w, 9):
                px, py = int(x + s * 0.7), int(y + s * 0.7)
                if 0 <= px < 16 and 0 <= py < 16:
                    c = ['b01c16', 'dc3018', 'ff8a28', 'ffd060'][min(3, int(t * 4))]
                    if t > 0.85 and k == 1:
                        c = 'c060ff'
                    img[py, px] = hexc(c)
        contorno(img, hexc('5a0a0c'))
        pf.append(img)
    particula('mj_pluma_fuego', pf)
    # Ceniza: copos grises.
    ceniza = []
    for k in range(2):
        img = lienzo(16, 16)
        r = random.Random(80 + k)
        for _ in range(4):
            x, y = r.randint(5, 10), r.randint(5, 10)
            img[y, x] = hexc(r.choice(['6a6460', '8a847e', '4a4440']))
        ceniza.append(img)
    particula('mj_ceniza', ceniza)
    particula('mj_destello', [destello_estrella(32, k / 2) for k in range(3)])
    # La grieta de jade: ramas que crecen desde el centro y brillan.
    grietas = []
    r = random.Random(90)
    ramas = []
    for i in range(6):
        ang = i / 6 * 6.28 + r.uniform(-0.3, 0.3)
        pts = [(16.0, 16.0)]
        for paso in range(5):
            ang += r.uniform(-0.6, 0.6)
            x, y = pts[-1]
            pts.append((x + math.cos(ang) * 3.0, y + math.sin(ang) * 3.0))
        ramas.append(pts)
    for k in range(5):
        img = lienzo(32, 32)
        for pts in ramas:
            for j in range(min(len(pts) - 1, k + 1)):
                (x1, y1), (x2, y2) = pts[j], pts[j + 1]
                for t in np.linspace(0, 1, 8):
                    x, y = int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t)
                    if 0 <= x < 32 and 0 <= y < 32:
                        img[y, x] = hexc('b8ffd8' if j < 2 else '4cc884')
        contorno(img, hexc('0f4a32', 200))
        grietas.append(img)
    particula('mj_grieta', grietas)


# ======================================================================
#  Texturas de efecto
# ======================================================================
def ef(nombre, img):
    guardar(img, os.path.join(EFECTOS, nombre + '.png'))


def efectos():
    # El brillo: blanco con caida suave (lo tine el juego).
    d, _ = radial(64)
    ef('brillo', rgba((255, 255, 255), np.clip(1 - d, 0, 1) ** 2.2))
    # El sol del fenix: nucleo blanco, corona naranja y rayos.
    d, ang = radial(128)
    rayos = (0.5 + 0.5 * np.cos(ang * 12)) ** 6 * np.clip(1 - d, 0, 1) ** 1.2
    a = np.clip(np.clip(1 - d / 0.55, 0, 1) ** 1.4 + rayos * 0.6, 0, 1)
    col = gradiente([(255, 60, 30), (255, 140, 40), (255, 220, 120), (255, 255, 240)], np.clip(1 - d / 0.8, 0, 1))
    img = lienzo(128, 128)
    img[..., :3] = col.astype(np.uint8)
    img[..., 3] = (a * 255).astype(np.uint8)
    ef('sol', img)

    # Estelas: en u de la cola (0) a la cabeza (1); en v de la punta del arma (0) a su base (1).
    def estela(nombre, borde, centro, base, w=64, h=32, semilla=1):
        yy, xx = np.mgrid[0:h, 0:w]
        v = yy / (h - 1)
        u = xx / (w - 1)
        rayas = fbm(h, w, 6, semilla, 2)
        a = np.clip((1 - v) ** 0.7 * (0.55 + 0.45 * rayas) + np.exp(-(v / 0.12) ** 2) * 0.6, 0, 1) * np.clip(u * 1.4, 0, 1)
        col = gradiente([borde, centro, base], v)
        img = lienzo(w, h)
        img[..., :3] = col.astype(np.uint8)
        img[..., 3] = (a * 255).astype(np.uint8)
        ef(nombre, img)
    estela('tajo_obsidiana', (200, 255, 225), (70, 220, 140), (40, 20, 70), semilla=3)
    estela('tajo_viento', (255, 255, 255), (170, 235, 255), (90, 170, 220), semilla=4)
    estela('tajo_agua', (240, 255, 255), (110, 220, 245), (20, 110, 160), semilla=5)

    # La cuchilla de viento: una media luna blanca con el filo celeste y rayas.
    n = 64
    yy, xx = np.mgrid[0:n, 0:n]
    x, y = (xx - 31.5) / 32, (yy - 31.5) / 32
    d1 = np.hypot(x, y + 0.35)
    d2 = np.hypot(x, y + 0.75)
    luna = (d1 < 0.95) & (d2 > 0.95)
    filo = np.clip(1 - np.abs(d1 - 0.93) / 0.08, 0, 1)
    rayas = fbm(n, n, 6, 7, 2)
    a = luna * (0.45 + 0.55 * filo) * (0.7 + 0.3 * rayas)
    col = gradiente([(140, 210, 255), (230, 250, 255), (255, 255, 255)], filo)
    img = lienzo(n, n)
    img[..., :3] = col.astype(np.uint8)
    img[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    ef('cuchilla_viento', img)

    # Bandas (en u alrededor, en v de arriba (0) a abajo (1)): viento, fuego, ola.
    def banda_viento(w=128, h=32):
        yy, xx = np.mgrid[0:h, 0:w]
        v = yy / (h - 1)
        rayas = ruido(h, w, 3, 11) * 0.5 + ruido(h, w, 7, 12) * 0.5
        rayas = np.clip((rayas - 0.35) * 2.2, 0, 1)
        estir = ruido(h, w, 16, 13)
        a = rayas * (v ** 0.8) * (0.6 + 0.4 * estir)
        col = gradiente([(150, 220, 255), (240, 252, 255)], rayas)
        img = lienzo(w, h)
        img[..., :3] = col.astype(np.uint8)
        img[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
        return img
    ef('anillo_viento', banda_viento())

    def banda_fuego(w=128, h=64, semilla=21):
        yy, xx = np.mgrid[0:h, 0:w]
        v = yy / (h - 1)
        nz = fbm(h, w, 10, semilla, 3)
        lenguas = 0.5 + 0.5 * np.sin(xx / w * 2 * np.pi * 10 + nz * 4)
        alto = 0.35 + 0.5 * lenguas * nz
        a = np.clip((v - (1 - alto)) * 5, 0, 1)
        col = gradiente([(170, 60, 255), (255, 60, 30), (255, 140, 40), (255, 220, 120), (255, 250, 220)],
                        np.clip((v - (1 - alto)) / alto, 0, 1))
        img = lienzo(w, h)
        img[..., :3] = col.astype(np.uint8)
        img[..., 3] = (a * 255).astype(np.uint8)
        return img
    ef('anillo_fuego', banda_fuego())

    # Las llamas de la columna: lenguas verticales (repetidas en u y en v).
    h, w = 128, 64
    yy, xx = np.mgrid[0:h, 0:w]
    nz = fbm(h, w, 12, 31, 3)
    lenguas = 0.5 + 0.5 * np.sin(xx / w * 2 * np.pi * 4 + nz * 5)
    a = np.clip(lenguas * 0.8 + nz * 0.5 - 0.2, 0, 1)
    # Solo las lenguas: donde no hay llama, transparente (si no, la columna se ve parda).
    col = gradiente([(255, 80, 30), (255, 140, 40), (255, 210, 100), (255, 250, 220)], a)
    img = lienzo(w, h)
    img[..., :3] = col.astype(np.uint8)
    img[..., 3] = (np.clip((a - 0.3) * 1.7, 0, 1) ** 1.2 * 235).astype(np.uint8)
    ef('llamas', img)

    # La ola (en anillo): agua honda abajo, clara arriba y la cresta de espuma.
    h, w = 64, 128
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / (h - 1)
    nz = fbm(h, w, 10, 41, 3)
    luz = 0.5 + 0.5 * np.sin(xx / w * 2 * np.pi * 6 + nz * 6 + v * 3)
    col = gradiente([(230, 255, 255), (120, 225, 240), (40, 150, 190), (14, 70, 110)], np.clip(v * 1.1 + (nz - 0.5) * 0.2, 0, 1))
    col = col + (luz[..., None] * 30 * (v[..., None] > 0.15))
    espuma = np.clip(1 - v / 0.14, 0, 1) * (0.6 + 0.4 * nz)
    col = col * (1 - espuma[..., None]) + 255 * espuma[..., None]
    a = np.clip(0.55 + 0.35 * (1 - v) + espuma, 0, 1)
    img = lienzo(w, h)
    img[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    img[..., 3] = (a * 255).astype(np.uint8)
    ef('ola', img)
    # La espuma (corona tumbada): manchas blancas.
    h, w = 16, 64
    nz = fbm(h, w, 4, 43, 2)
    a = np.clip((nz - 0.35) * 3, 0, 1)
    ef('espuma', rgba((245, 255, 255), a))
    # El tsunami: el muro de agua; la cresta (v = 0) de espuma, la base honda.
    h, w = 128, 128
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / (h - 1)
    nz = fbm(h, w, 14, 47, 4)
    vetas = 0.5 + 0.5 * np.sin(xx / w * 2 * np.pi * 5 + nz * 7 + v * 6)
    col = gradiente([(240, 255, 255), (150, 235, 245), (50, 170, 205), (16, 90, 130), (8, 40, 70)],
                    np.clip(v + (nz - 0.5) * 0.25, 0, 1))
    col = col + vetas[..., None] * 26
    espuma = np.clip(1 - v / 0.18, 0, 1) * (0.5 + 0.5 * nz)
    col = col * (1 - espuma[..., None]) + 255 * espuma[..., None]
    img = lienzo(w, h)
    img[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    img[..., 3] = (np.clip(0.78 + 0.2 * (1 - v) + espuma, 0, 1) * 255).astype(np.uint8)
    ef('tsunami', img)
    # El chorro: rayas de agua a lo largo (repetidas en v).
    h, w = 128, 64
    yy, xx = np.mgrid[0:h, 0:w]
    u = xx / (w - 1)
    rayas = ruido(h, w, 4, 51) * 0.6 + ruido(h, w, 9, 52) * 0.4
    centro = 1 - np.abs(u - 0.5) * 2
    a = np.clip(rayas * 1.2 - 0.25, 0, 1) * centro ** 0.6
    col = gradiente([(60, 170, 220), (180, 240, 255), (255, 255, 255)], rayas)
    img = lienzo(w, h)
    img[..., :3] = col.astype(np.uint8)
    img[..., 3] = (a * 255).astype(np.uint8)
    ef('chorro', img)
    # El ciclon: rayas en espiral (repetidas en u y v), gris palido con celeste y polvo.
    h, w = 128, 128
    yy, xx = np.mgrid[0:h, 0:w]
    u, v = xx / w, yy / h
    nz = fbm(h, w, 12, 61, 3)
    rayas = 0.5 + 0.5 * np.sin((u * 6 + v * 3) * 2 * np.pi + nz * 5)
    a = np.clip((rayas - 0.35) * 1.8, 0, 1) * (0.55 + 0.45 * nz)
    col = gradiente([(120, 120, 130), (200, 225, 240), (245, 252, 255)], rayas * nz + 0.2)
    img = lienzo(w, h)
    img[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    img[..., 3] = (a * 220).astype(np.uint8)
    ef('ciclon', img)
    # El cristal de jade: en u las caras, en v la punta (0 a 0,25) y el cuerpo con vetas y luz dentro.
    h, w = 64, 32
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / (h - 1)
    u = xx / (w - 1)
    nz = fbm(h, w, 6, 71, 3)
    vetas = np.abs(np.sin((u * 3 + nz * 2 + v * 4) * np.pi)) < 0.12
    col = gradiente([(10, 52, 36), (28, 122, 76), (47, 171, 106), (126, 224, 168), (220, 255, 232)],
                    np.clip(0.35 + 0.45 * nz + (1 - v) * 0.25, 0, 1))
    col[vetas] = (190, 255, 220)
    img = lienzo(w, h)
    img[..., :3] = col.astype(np.uint8)
    img[..., 3] = 240
    ef('cristal_jade', img)
    # El remolino de la tormenta: brazos de jade en espiral sobre un disco oscuro.
    n = 128
    d, ang = radial(n)
    brazo = 0.5 + 0.5 * np.cos(ang * 3 + d * 9)
    a = np.clip(1 - d, 0, 1) ** 0.7 * (0.35 + 0.65 * brazo ** 2) * (d < 1)
    col = gradiente([(10, 16, 14), (20, 80, 50), (70, 220, 140), (200, 255, 225)], np.clip(brazo * (1 - d) * 1.3, 0, 1))
    img = lienzo(n, n)
    img[..., :3] = col.astype(np.uint8)
    img[..., 3] = (np.clip(a, 0, 1) * 230).astype(np.uint8)
    ef('remolino_jade', img)
    # La pluma de fuego (en vuelo): roja, naranja y la punta amarilla, con llamas.
    n = 32
    img = lienzo(n, n)
    for t in np.linspace(0, 1, 120):
        x, y = 6 + 20 * t, 26 - 20 * t
        w = 4.5 * math.sin(math.pi * min(1, t * 1.1))
        for s in np.linspace(-w, w, 15):
            px, py = int(x + s * 0.7), int(y + s * 0.7)
            if 0 <= px < n and 0 <= py < n:
                c = ['b01c16', 'dc3018', 'ff8a28', 'ffd060', 'fff4c0'][min(4, int(t * 5))]
                img[py, px] = hexc(c)
    contorno(img, hexc('ff5a20', 160))
    ef('pluma_fuego', img)


# ======================================================================
#  La barra de vida de los mini jefes
# ======================================================================
# Como la de los jefes (Juan, 11-10-2026: "quiero que sea como los boses pero en cambio la altura va ser mas pequeno"):
# el medallon con su emblema a la izquierda, la barra larga de bloques de su material con su punta a la derecha, la
# cresta de su elemento que sale del medallon por encima del marco, el nombre encima y tres muescas de su material.
# Mide 220x32 (la de los jefes, 240x44); el hueco, 178x6.
ANCHO, ALTO = 220, 32
HX, HY, HW, HH = 34, 19, 178, 6
NOMBRE_W, NOMBRE_H = 96, 11
EC, ER = (14, 19), 12.5
MUESCA_W, MUESCA_H = 5, 11
# Las plumas de la cresta (Moctezuma y el fenix): (centro, alto, ancho, inclinacion), de atras hacia delante.
PLUMAS_CRESTA = ((80, 6, 6, 0.9), (73, 8, 7, 0.85), (65, 10, 8, 0.8), (56, 12, 8, 0.7), (47, 14, 9, 0.55),
                 (38, 15, 9, 0.42), (29, 16, 9, 0.28))

TEMAS = {
    'moctezuma': dict(nombre='MOCTEZUMA',
                      mat=('061612', '0b2a24', '10403a', '165648', '1f6e58', '2e8a6c', '3fae86', '66d2a6', 'a8f0cc'),
                      metal=('3a2606', '5e400e', '8f6418', 'c28d28', 'e2b443', 'f8d97c'), hueco='04120b',
                      relleno=[(16, 96, 58), (47, 171, 106), (126, 224, 168), (232, 184, 52)], letra=(244, 250, 236),
                      letra2=(126, 224, 168), sombra=(3, 14, 9)),
    'yiatzo': dict(nombre='YIATZO',
                   mat=('101216', '1c1f25', '272b33', '343943', '434956', '545b68', '6a7280', '8b94a2', 'b8c0cc'),
                   metal=('2e3238', '4e545c', '7c848e', 'a8b0ba', 'cdd4dc', 'eef2f6'), hueco='0a0c12',
                   relleno=[(40, 110, 160), (90, 190, 240), (180, 236, 255), (240, 252, 255)], letra=(240, 248, 252),
                   letra2=(150, 220, 250), sombra=(6, 10, 18)),
    'atlahua': dict(nombre='ATLAHUA',
                    mat=('041418', '08262c', '0c3a42', '125058', '18666e', '1f7e86', '2a9aa0', '4ec0c0', '8ee8e2'),
                    metal=('3a4450', '5e6a78', '8a96a6', 'b4bece', 'd8e0ea', 'f4f8fc'), hueco='020e14',
                    relleno=[(14, 72, 110), (26, 120, 136), (60, 192, 204), (200, 240, 240)], letra=(236, 250, 250),
                    letra2=(110, 236, 240), sombra=(2, 14, 20)),
    'xiuhquetzal': dict(nombre='XIUHQUETZAL',
                        mat=('1a0204', '2e0406', '440609', '5a0a0c', '7a1010', '9c1a14', 'c42a18', 'e8541e', 'ff8a28'),
                        metal=('5a3a08', '8a5a10', 'b8801c', 'd09a22', 'e8b834', 'ffe08a'), hueco='140203',
                        relleno=[(200, 40, 24), (255, 110, 30), (255, 190, 70), (255, 240, 190)], letra=(255, 246, 232),
                        letra2=(255, 196, 90), sombra=(22, 4, 6)),
}


class Pixeles:
    """Un lienzo RGBA para pintar pixel a pixel (como las barras de los jefes)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)

    def pon(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c

    def hay(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.a[y, x, 3] > 0


def _dentro(poly, x, y):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1:
            c = not c
    return c


def _pluma(px, cx, base, alto, ancho, lean, cols, punta=None, raquis=None):
    """Una pluma que sube desde 'base' (ancha abajo, punta redonda arriba, inclinada 'lean'): la cara clara a la
    izquierda, la oscura a la derecha, el raquis por el medio y la punta de otro color."""
    pts = []
    for k in range(9):
        t = k / 8
        w = ancho * 0.5 * math.sin(math.pi * min(1.0, 0.25 + 0.85 * t)) if t < 1 else 0
        pts.append((cx + lean * alto * t - w, base - alto * t))
    for k in range(8, -1, -1):
        t = k / 8
        w = ancho * 0.5 * math.sin(math.pi * min(1.0, 0.25 + 0.85 * t)) if t < 1 else 0
        pts.append((cx + lean * alto * t + w, base - alto * t))
    caja = [(x, y) for y in range(int(base - alto - 1), int(base) + 1) for x in range(int(cx - ancho), int(cx + ancho + lean * alto + 2))]
    dentro = {(x, y) for (x, y) in caja if _dentro(pts, x + 0.5, y + 0.5)}
    for (x, y) in dentro:
        t = (base - y) / max(1.0, alto)
        eje = cx + lean * alto * t
        borde = any((x + dx, y + dy) not in dentro for dx, dy in ((1, 0), (-1, 0), (0, -1)))
        if borde:
            c = cols[0]
        elif raquis is not None and abs(x + 0.5 - eje) < 0.6:
            c = raquis
        elif x < eje:
            c = cols[3] if t > 0.4 else cols[2]
        else:
            c = cols[2] if t > 0.4 else cols[1]
        if punta is not None and t > 0.78 and not borde:
            c = punta
        px.pon(x, y, c)


EMBLEMAS = {
    # 20x20, cada letra un color de la paleta del emblema ('.' nada).
    'moctezuma': ([
        "....f..F..F..f......",
        ".....fF.fF.Ff.......",
        "......FfFFfF........",
        "....yyYYYYYYyy......",
        "...yYGGGGGGGGYy.....",
        "...YG.eG..Ge.GY.....",
        "...YG..GGGG..GY.....",
        "....YGGyyyyGGY......",
        ".....YGyyyyGY.......",
        "......GyyyyG........",
        ".......GyyG.........",
        "........GG..........",
        "....................",
        "...kkk.......kkk....",
        "..kw.kkk...kkk.wk...",
        "...kkk.kkkkk.kkk....",
        "......kk...kk.......",
        "....................",
        "....................",
        "....................",
    ], {'f': hexc('2fab6a'), 'F': hexc('7ee0a8'), 'y': hexc('f8d65c'), 'Y': hexc('e8b834'), 'G': hexc('b07a18'),
        'e': hexc('7affb0'), 'k': hexc('1a1424'), 'w': hexc('c8b8ff')}),
    'yiatzo': ([
        ".........ww.........",
        "........wccw........",
        ".......wcCCcw.......",
        "......wcCWWCcw......",
        "......wcCWWCcw......",
        ".......wcCCcw.......",
        "........wccw........",
        ".......ssSSss.......",
        "......s.sSSs.s......",
        "......s..SS..s......",
        ".......s.SS.s.......",
        "........sSSs........",
        ".........SS.........",
        ".........SS.........",
        ".........SS.........",
        ".........SS.........",
        ".........SS.........",
        "........sSSs........",
        "....................",
        "....................",
    ], {'w': hexc('48b8e8'), 'c': hexc('7ae0ff'), 'C': hexc('c8f8ff'), 'W': hexc('ffffff'), 's': hexc('9ca4ac'),
        'S': hexc('3e4048')}),
    'atlahua': ([
        "...T......T......T..",
        "...T......T......T..",
        "...TT....TTT....TT..",
        "...tT....tTt....Tt..",
        "...tt.....t.....tt..",
        "....tt....t....tt...",
        ".....tttttttttttt...",
        "..........t.........",
        ".........RtR........",
        "........R.t.R.......",
        "..........t.........",
        "..........P.........",
        "..........P.........",
        "..........P.........",
        "..........P.........",
        "..........P.........",
        "..........P.........",
        "..........P.........",
        "....................",
        "....................",
    ], {'T': hexc('b8fbff'), 't': hexc('5ad4dc'), 'R': hexc('f06a3c'), 'P': hexc('0e3050')}),
    'xiuhquetzal': ([
        ".....v...Y...v......",
        ".....vY.YyY.Yv......",
        "......oYyyyYo.......",
        ".......oyyyo........",
        "......rRRRRRr.......",
        ".....rRe.RRRbb......",
        ".....rRRRRRbbBb.....",
        "......rRRRRR..B.....",
        "oO.....rRRR......Oo.",
        "OYo....rRRr.....oYO.",
        "oYOo..rmMMmr...oOYo.",
        ".oYO.rmMWWMmr.OYo...",
        "..oO..mMMMMm..Oo....",
        "......rmMMmr........",
        ".......rmmr.........",
        "........rr..........",
        "....................",
        "....................",
        "....................",
        "....................",
    ], {'v': hexc('c060ff'), 'Y': hexc('ffe08a'), 'y': hexc('fff4c0'), 'o': hexc('ff9a30'), 'O': hexc('dc3018'),
        'r': hexc('861212'), 'R': hexc('b01c16'), 'e': hexc('ffd060'), 'b': hexc('e8b834'), 'B': hexc('8a5a10'),
        'm': hexc('ff8a28'), 'M': hexc('ffd060'), 'W': hexc('fff8e0')}),
}


def marco(nombre, t):
    """El marco de la barra, como el de los jefes: bloques de su material con la junta al tresbolillo alrededor del
    hueco, sus incrustaciones, la punta de la derecha, la cresta que sale del medallon y el medallon con su emblema."""
    M = [hexc(c) for c in t['mat']]
    O = [hexc(c) for c in t['metal']]
    hueco = hexc(t['hueco'])
    rnd = random.Random(nombre)
    px = Pixeles(ANCHO, ALTO)
    y_top, y_bot = HY - 3, HY + HH + 2
    x_izq, x_der = HX - 7, HX + HW + 1
    # Los bloques, de 12 de largo, con la junta al tresbolillo; arriba mas claros que abajo.
    for y in range(y_top, y_bot + 1):
        for x in range(x_izq, x_der + 1):
            if HX <= x < HX + HW and HY <= y < HY + HH:
                px.pon(x, y, hueco)
                continue
            if y in (y_top, y_bot) or x in (x_izq, x_der):
                px.pon(x, y, M[0])
                continue
            arriba = y < HY
            i = (x - x_izq + (0 if arriba else 6)) % 12
            if i == 0:
                px.pon(x, y, M[2] if arriba else M[1])
                continue
            k = 6 if arriba else 4
            k += 1 if y == y_top + 1 else -1 if y == y_bot - 1 else 0
            k += 1 if i == 1 else -1 if i == 11 else 0
            r = rnd.random()
            k += -1 if r < 0.12 else 1 if r < 0.16 else 0
            px.pon(x, y, M[8] if rnd.random() < 0.02 else M[max(1, min(8, k))])
    for x in range(HX, HX + HW):
        px.pon(x, HY, M[0])
    # Las incrustaciones de su tema, arriba y abajo.
    if nombre == 'moctezuma':
        # La greca escalonada (xicalcoliuhqui) de oro.
        for x in range(HX + 30, HX + HW - 6, 22):
            for (dx, dy, c) in ((0, 1, O[3]), (1, 1, O[4]), (1, 0, O[5]), (2, 0, O[4]), (3, 0, O[3]), (3, 1, O[2])):
                px.pon(x + dx, y_top + 1 + dy, c)
        for x in range(HX + 8, HX + HW - 6, 22):
            for (dx, dy, c) in ((0, 0, O[4]), (1, 0, O[3]), (1, 1, O[2]), (2, 1, O[2]), (3, 0, O[3])):
                px.pon(x + 11 + dx, HY + HH + dy, c)
    elif nombre == 'yiatzo':
        # Filigrana de plata (puntos) y runas celestes en la banda de arriba.
        for x in range(HX + 4, HX + HW - 4, 6):
            px.pon(x, y_top + 1, O[4] if (x // 6) % 2 else O[3])
            px.pon(x + 3, y_bot - 1, O[2])
        for x in range(HX + 40, HX + HW - 8, 34):
            for (dx, dy) in ((0, 0), (1, 0), (2, 0), (1, 1)):
                px.pon(x + dx, y_top + 1 + dy, hexc('7ae0ff'))
    elif nombre == 'atlahua':
        # Perlas y conchas.
        for x in range(HX + 10, HX + HW - 6, 18):
            px.pon(x, y_top + 1, O[5])
            px.pon(x + 1, y_top + 1, O[3])
            px.pon(x + 9, y_bot - 1, O[4])
    else:
        # Escamas de pluma de oro.
        for x in range(HX + 6, HX + HW - 6, 8):
            px.pon(x, y_top + 1, O[4])
            px.pon(x + 1, y_top + 1, O[3])
            px.pon(x + 4, y_bot - 1, O[2])
    # La punta de la derecha.
    xp = x_der + 1
    if nombre == 'moctezuma':
        # Los dientes de obsidiana del macuahuitl.
        for (y0, y1) in ((y_top - 1, y_top + 4), (y_top + 4, y_top + 8), (y_top + 8, y_bot + 2)):
            m = (y0 + y1) / 2
            for y in range(y0, y1):
                largo = int(7 - abs(y + 0.5 - m) * 2.4)
                for i in range(max(1, largo)):
                    borde = i == largo - 1 or y in (y0, y1 - 1)
                    c = hexc('120c1a') if borde else hexc('8a78c8') if y < m - 0.5 and i < largo - 2 else hexc('3a2c50')
                    px.pon(xp + i, y, c)
    elif nombre == 'yiatzo':
        # La punta de plata del baston con el orbe de viento.
        for j in range(y_bot - y_top + 1):
            hondo = 1 + min(j, y_bot - y_top - j) // 2
            for i in range(hondo + 1):
                px.pon(xp + i, y_top + j, M[0] if i == hondo else O[5 - min(3, i)])
        cy = (y_top + y_bot) // 2
        for (dx, dy, c) in ((4, 0, 'ffffff'), (5, 0, 'c8f8ff'), (4, -1, '7ae0ff'), (4, 1, '7ae0ff'), (3, 0, '48b8e8')):
            px.pon(xp + dx, cy + dy, hexc(c))
    elif nombre == 'atlahua':
        # El tridente: tres puntas.
        for (y, largo) in ((y_top + 1, 6), ((y_top + y_bot) // 2, 7), (y_bot - 1, 6)):
            for i in range(largo):
                px.pon(xp + i, y, O[4] if i < largo - 1 else hexc('b8fbff'))
                px.pon(xp + i, y + 1, M[0] if i < largo - 2 else O[2])
        for y in range(y_top + 1, y_bot):
            px.pon(xp, y, O[3])
    else:
        # Una llama.
        for j in range(y_bot - y_top + 1):
            m = (y_bot - y_top) / 2
            largo = int(6 - abs(j - m) * 1.1 + rnd.random() * 1.5)
            for i in range(max(1, largo)):
                c = ['b01c16', 'dc3018', 'ff8a28', 'ffd060', 'fff4c0', 'c060ff'][min(5, i)]
                px.pon(xp + i, y_top + j, hexc(c))
    # La cresta: sale del medallon y baja hacia la derecha, por encima del marco.
    base = y_top
    if nombre == 'moctezuma':
        # Plumas de quetzal en abanico, con la punta de oro.
        verdes = [hexc('0b2a1c'), hexc('1f6e48'), hexc('2fab6a'), hexc('7ee0a8')]
        for (cx, alto, ancho, lean) in PLUMAS_CRESTA:
            _pluma(px, cx, base + 1, alto, ancho, lean, verdes, punta=O[4], raquis=O[3])
        _pluma(px, 5, 13, 11, 8, -0.55, verdes, punta=O[4], raquis=O[3])
    elif nombre == 'yiatzo':
        # Las losas de glifos que flotan, con su runa, y jirones de viento entre ellas.
        # El jiron de viento por detras: una curva que se enrosca entre las losas.
        for k in range(160):
            u = k / 159
            x = 24 + 58 * u
            y = base - 2 - 9 * (1 - u) * (0.6 + 0.4 * math.sin(u * 9))
            px.pon(x, y, hexc('7ae0ff') if k % 7 else hexc('ffffff'))
        runas = [((1, 1), (1, 2), (1, 3), (1, 4), (2, 2), (3, 1), (3, 3)),
                 ((1, 1), (2, 1), (3, 1), (2, 2), (2, 3), (1, 4), (3, 4)),
                 ((1, 2), (2, 1), (3, 2), (2, 3), (2, 4)), ((1, 1), (3, 1), (2, 2), (1, 3), (3, 3))]
        for i, (x0, y0, w, h) in enumerate(((23, 1, 8, 12), (34, 3, 8, 11), (45, 6, 7, 9), (55, 8, 6, 8), (64, 10, 5, 6))):
            for y in range(y0, y0 + h):
                for x in range(x0, x0 + w):
                    borde = x in (x0, x0 + w - 1) or y in (y0, y0 + h - 1)
                    c = M[0] if borde else M[7] if x == x0 + 1 or y == y0 + 1 else M[6] if x < x0 + w // 2 else M[5]
                    px.pon(x, y, c)
            for (dx, dy) in runas[i % len(runas)]:
                if dx < w - 1 and dy < h - 1:
                    px.pon(x0 + dx + (w - 5) // 2, y0 + dy + (h - 6) // 2, hexc('7ae0ff'))
    elif nombre == 'atlahua':
        # Ramas de coral que suben del marco, y burbujas.
        rojos = [hexc('5a1810'), hexc('c8322a'), hexc('e04a32'), hexc('ff9a60')]

        def rama(x, y, alto, lado, nivel, grueso):
            for k in range(alto):
                xx = x + (k // 3) * lado
                for g in range(grueso):
                    c = rojos[3] if k >= alto - 1 else rojos[2] if g == 0 else rojos[1]
                    px.pon(xx + g, y - k, c)
                for xb in (xx - 1, xx + grueso):
                    if not px.hay(xb, y - k):
                        px.pon(xb, y - k, rojos[0])
                if nivel > 0 and k in (alto // 3, alto * 2 // 3):
                    rama(xx + (grueso if lado > 0 else -1), y - k, max(3, alto // 2), lado if k == alto // 3 else -lado,
                         nivel - 1, max(1, grueso - 1))
            px.pon(x + ((alto - 1) // 3) * lado, y - alto, rojos[0])
        for (x, alto, lado) in ((24, 15, 1), (35, 13, -1), (44, 11, 1), (53, 9, 1), (61, 7, -1), (69, 5, 1)):
            rama(x, base, alto, lado, 2, 3 if alto > 10 else 2)
        for (x, y) in ((40, 3), (58, 5), (75, 9), (31, 1)):
            px.pon(x, y, hexc('96f5ff'))
            px.pon(x + 1, y, hexc('d8ffff'))
    else:
        # Plumas de fuego: rojas, naranjas y la punta violeta.
        fuego = [hexc('5a0a0c'), hexc('b01c16'), hexc('ff8a28'), hexc('ffd060')]
        for (cx, alto, ancho, lean) in PLUMAS_CRESTA:
            _pluma(px, cx, base + 1, alto, ancho, lean, fuego, punta=hexc('c060ff'), raquis=hexc('fff4c0'))
        _pluma(px, 5, 13, 11, 8, -0.55, fuego, punta=hexc('c060ff'), raquis=hexc('fff4c0'))
    # El medallon: un aro de su material con ocho tachones de metal y el emblema dentro.
    for y in range(ALTO):
        for x in range(ANCHO // 4):
            dx, dy = x + 0.5 - EC[0], y + 0.5 - EC[1]
            d = math.hypot(dx, dy)
            if d > ER:
                continue
            luz = -(dx + dy) / (2 * ER)
            if d > ER - 1.2:
                px.pon(x, y, M[0])
            elif d > ER - 3.0:
                ang = math.atan2(dy, dx)
                tachon = abs((ang + math.pi / 8) % (math.pi / 4) - math.pi / 8) < 0.2
                if tachon:
                    px.pon(x, y, O[5] if luz > 0.2 else O[4] if luz > -0.15 else O[3])
                else:
                    px.pon(x, y, M[7 if luz > 0.18 else 6 if luz > -0.05 else 5 if luz > -0.25 else 4])
            elif d > ER - 3.9:
                px.pon(x, y, O[5] if luz > 0.25 else O[4] if luz > 0.0 else O[3] if luz > -0.3 else O[2])
            else:
                px.pon(x, y, M[1] if luz > 0 else M[0])
    dib, pal = EMBLEMAS[nombre]
    for y, fila in enumerate(dib):
        for x, c in enumerate(fila):
            if c != '.':
                px.pon(EC[0] - 10 + x, EC[1] - 10 + y, pal[c])
    return px.a


def muescas(nombre, t):
    """Las tres muescas que van sobre el hueco (a 25, 50 y 75 %), de su material; partidas al pasarlas."""
    M = [hexc(c) for c in t['mat']]
    O = [hexc(c) for c in t['metal']]
    out = []
    for rota in (False, True):
        px = Pixeles(MUESCA_W, MUESCA_H)
        for y in range(MUESCA_H):
            for x in range(MUESCA_W):
                if rota and y < 4:
                    continue
                w = 2.5 if y < 3 else 1.5 - (y - 3) * 0.12
                if abs(x + 0.5 - MUESCA_W / 2) > w:
                    continue
                borde = abs(x + 0.5 - MUESCA_W / 2) > w - 1 or y in (0, MUESCA_H - 1)
                if y < 3:
                    c = O[1] if borde else (O[4] if x < MUESCA_W // 2 else O[3])
                elif nombre == 'moctezuma':
                    c = hexc('120c1a') if borde else (hexc('8a78c8') if x < MUESCA_W // 2 else hexc('3a2c50'))
                elif nombre == 'atlahua':
                    c = hexc('5a1810') if borde else (hexc('ff9a60') if x < MUESCA_W // 2 else hexc('c8322a'))
                elif nombre == 'xiuhquetzal':
                    c = hexc('2e0406') if borde else (hexc('ffd060') if x < MUESCA_W // 2 else hexc('dc3018'))
                else:
                    c = M[0] if borde else (M[8] if x < MUESCA_W // 2 else M[6])
                if rota:
                    c = tuple(int(v * 0.55) for v in c[:3]) + (255,)
                px.pon(x, y, c)
        out.append(px.a)
    return out


def nombre_barra(t):
    """El nombre en las letras de pixel de las barras (las GRANDE del cartel, a escala 1), en 96x11: la letra con
    su contorno arriba y abajo y la sombra (en 96x9 se perdia el contorno de arriba y se veia cortada)."""
    im = Image.new('RGBA', (NOMBRE_W, NOMBRE_H), (0, 0, 0, 0))
    relleno = pj.rampa(t['letra'], t['letra2'])
    pj.pintar_texto(im, t['nombre'], pj.GRANDE, 2 + (pj.puntos_texto(t['nombre'], pj.GRANDE, 1, 1)[1]) // 2, 5, relleno,
                    t['sombra'], escala=1, aire=1, sombra_dy=1)
    return np.array(im)


def relleno_barra(nombre, t):
    """La energia de su elemento: 64x6, repetible en u (el juego la hace correr)."""
    h, w = HH, 64
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / (h - 1)
    nz = ruido(h, w, 8, 101 + len(nombre)) * 0.6 + ruido(h, w, 3, 102 + len(nombre)) * 0.4
    k = np.clip(0.25 + 0.5 * nz + (1 - v) * 0.35, 0, 1)
    col = gradiente(t['relleno'], k)
    if nombre == 'moctezuma':
        brillos = ruido(h, w, 2, 103) > 0.78
        col[brillos] = (248, 214, 92)
    elif nombre == 'yiatzo':
        rayas = np.abs(np.sin((xx / w * 6 + v * 0.5) * np.pi)) > 0.94
        col[rayas] = (255, 255, 255)
    elif nombre == 'atlahua':
        ola = np.abs(v - (0.35 + 0.25 * np.sin(xx / w * 4 * np.pi))) < 0.12
        col[ola] = (200, 245, 250)
    else:
        chispa = ruido(h, w, 2, 104) > 0.8
        col[chispa] = (200, 110, 255)
    img = lienzo(w, h)
    img[..., :3] = col.astype(np.uint8)
    img[..., 3] = 255
    img[0, :, :3] = np.clip(img[0, :, :3].astype(int) + 40, 0, 255).astype(np.uint8)
    return img


def barras():
    for nombre, t in TEMAS.items():
        guardar(marco(nombre, t), os.path.join(GUI, f'{nombre}_marco.png'))
        guardar(relleno_barra(nombre, t), os.path.join(GUI, f'{nombre}_relleno.png'))
        guardar(nombre_barra(t), os.path.join(GUI, f'{nombre}_nombre.png'))
        entera, rota = muescas(nombre, t)
        guardar(entera, os.path.join(GUI, f'{nombre}_muesca.png'))
        guardar(rota, os.path.join(GUI, f'{nombre}_muesca_rota.png'))


def hoja_muestra(ruta):
    """Todo junto, ampliado, para revisar sin entrar al juego."""
    filas = []
    x = y = alto = 0
    W = 1400
    posiciones = []
    for nombre, im in MUESTRAS:
        k = 4 if im.width <= 32 else (2 if im.width <= 128 else 2)
        w, h = im.width * k, im.height * k
        if x + w > W:
            x, y, alto = 0, y + alto + 18, 0
        posiciones.append((nombre, im, x, y, k))
        x += w + 10
        alto = max(alto, h)
    hoja = Image.new('RGBA', (W, y + alto + 20), (60, 64, 70, 255))
    from PIL import ImageDraw
    dib = ImageDraw.Draw(hoja)
    for nombre, im, x, y, k in posiciones:
        hoja.alpha_composite(im.resize((im.width * k, im.height * k), Image.NEAREST), (x, y + 12))
        dib.text((x, y), nombre[:22], fill=(220, 220, 220))
    hoja.save(ruta)


if __name__ == '__main__':
    if HOJA == 'solo-barras':
        barras()
    else:
        particulas()
        efectos()
        barras()
    print(len(MUESTRAS), 'texturas')
    if HOJA and HOJA != 'solo-barras':
        hoja_muestra(HOJA)

"""
La Ruleta (17-10-2026): los cambios de dificultad de Atalaya, como la ruleta de DEDsafío pero a nuestra manera. Juan:
«vamos a hacer como un casino pero no de 3 sino de solo 1 ... la casilla se mueva, mueva, mueva y pare»; cuatro
iconos, uno por final: un huevo con un signo de interrogación (mob nuevo), una advertencia (cambio de dificultad), la
penalización y el minijuego; «en el chat amarillo si es cambio de dificultad, anaranjado si es un mob nuevo, celeste si
es penalización y verde si es minijuego». Es una tragaperras de un solo rodillo que sale en la pantalla (RuletaHud),
gira y para en uno de los cuatro. Este script hace:

  textures/gui/ruleta/maquina          la tragaperras en una hoja, a píxeles: el medallón (con el hueco redondo de la
                                       ventana), la bombilla encendida, el destello, la flecha y la moneda
  textures/gui/ruleta/iconos           los cuatro iconos del rodillo (48 x 48), nítidos
  textures/gui/ruleta/iconos_borrosos  los mismos corridos hacia abajo, para cuando gira deprisa (con blur)
  textures/item/ruleta_<final>         el icono de cada final para el chat (16 x 16)
  textures/item/ruleta_<final>_cartel_NN  el rótulo de cada final en letras de su color, con el brillo que lo cruza
                                       (cuadros animados que el chat pinta seguidos, como el del Momento)

Con una carpeta de salida, además, todas las propuestas de iconos y sus vistas (para la página en la que Juan elige).

Uso: python ruleta.py <raiz del proyecto> [carpeta de las propuestas]
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

import momento_maldicion as mm

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
PROPUESTAS = sys.argv[2] if len(sys.argv) > 2 else None

# Los cuatro finales, en el orden del rodillo (el mismo que Ruleta.Fin).
FINALES = ('mob', 'dificultad', 'penalizacion', 'minijuego')
# La propuesta de cada icono que va en el mod (Juan elige en la página).
ELEGIDOS = {'mob': 'A', 'dificultad': 'A', 'penalizacion': 'A', 'minijuego': 'A'}


def H(h, a=255):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def rampa(*colores):
    return np.array([H(c)[:3] for c in colores], float)


# ----------------------------------------------------------------------------------------------------------------
#  El pincel: formas por distancia con signo (negativa dentro), luz de arriba a la izquierda, colores en escalones
#  (pixel art limpio) y contorno de un píxel. Los iconos se diseñan en un cuadro de 32 unidades y se pintan a 32 o a
#  16 píxeles; la máquina, a una unidad por píxel.
# ----------------------------------------------------------------------------------------------------------------
LUZ = np.array([-0.52, -0.66, 0.54])
LUZ = LUZ / np.linalg.norm(LUZ)


def malla(n, lado=32.0):
    k = lado / n
    ys, xs = np.mgrid[0:n, 0:n].astype(float)
    return (xs + 0.5) * k, (ys + 0.5) * k, k


def malla_rect(w, h):
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    return xs + 0.5, ys + 0.5


def sd_circulo(x, y, cx, cy, r):
    return np.hypot(x - cx, y - cy) - r


def sd_elipse(x, y, cx, cy, rx, ry):
    return (np.hypot((x - cx) / rx, (y - cy) / ry) - 1) * min(rx, ry)


def sd_caja(x, y, cx, cy, hw, hh, r=0.0):
    qx = np.abs(x - cx) - hw + r
    qy = np.abs(y - cy) - hh + r
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def sd_segmento(x, y, ax, ay, bx, by, r):
    pax, pay = x - ax, y - ay
    bax, bay = bx - ax, by - ay
    h = np.clip((pax * bax + pay * bay) / (bax * bax + bay * bay), 0, 1)
    return np.hypot(pax - bax * h, pay - bay * h) - r


def sd_poligono(x, y, pts):
    """La distancia exacta a un polígono (cualquier orden de vértices)."""
    d = np.full(x.shape, np.inf)
    s = np.ones(x.shape)
    for i in range(len(pts)):
        vi, vj = pts[i], pts[i - 1]
        ex, ey = vj[0] - vi[0], vj[1] - vi[1]
        wx, wy = x - vi[0], y - vi[1]
        h = np.clip((wx * ex + wy * ey) / (ex * ex + ey * ey), 0, 1)
        bx, by = wx - ex * h, wy - ey * h
        d = np.minimum(d, bx * bx + by * by)
        c1 = y >= vi[1]
        c2 = y < vj[1]
        c3 = ex * wy > ey * wx
        s = np.where((c1 & c2 & c3) | (~c1 & ~c2 & ~c3), -s, s)
    return s * np.sqrt(d)


def sd_arco(x, y, cx, cy, r, a0, barrido, grosor):
    """Un arco de anillo (ángulos de pantalla: 0 a la derecha, pi/2 abajo), de a0 y barriendo hacia abajo."""
    ang = np.arctan2(y - cy, x - cx)
    rel = np.mod(ang - a0, 2 * np.pi)
    anillo = np.abs(np.hypot(x - cx, y - cy) - r)
    e0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
    e1 = (cx + r * math.cos(a0 + barrido), cy + r * math.sin(a0 + barrido))
    puntas = np.minimum(np.hypot(x - e0[0], y - e0[1]), np.hypot(x - e1[0], y - e1[1]))
    return np.where(rel <= barrido, anillo, puntas) - grosor


def sd_corazon(x, y, cx, abajo, escala):
    """El corazón (de Inigo Quilez): la punta en (cx, abajo) y de alto ~escala."""
    px = np.abs(x - cx) / escala
    py = (abajo - y) / escala
    a = np.hypot(px - 0.25, py - 0.75) - math.sqrt(2) / 4
    m = 0.5 * np.maximum(px + py, 0)
    b = np.sqrt(np.minimum((px) ** 2 + (py - 1) ** 2, (px - m) ** 2 + (py - m) ** 2)) * np.sign(px - py)
    return np.where(py + px > 1, a, b) * escala


def union(*ds):
    out = ds[0]
    for d in ds[1:]:
        out = np.minimum(out, d)
    return out


def esfera(x, y, cx, cy, rx, ry, amb=0.16):
    """Lo iluminado de una forma redonda (0 a 1), como si fuera un trozo de esfera."""
    nx = (x - cx) / rx
    ny = (y - cy) / ry
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    dif = np.clip(nx * LUZ[0] + ny * LUZ[1] + nz * LUZ[2], 0, 1)
    return np.clip(amb + (1 - amb) * dif, 0, 1)


def bisel(d, k, ancho, base=0.62, fuerza=0.38):
    """Lo iluminado de una forma plana con el canto biselado: la luz en los cantos de arriba a la izquierda."""
    gy, gx = np.gradient(d)
    ln = np.hypot(gx, gy) + 1e-9
    cara = gx / ln * LUZ[0] + gy / ln * LUZ[1]
    canto = np.clip(1 - (-d) / ancho, 0, 1)
    return np.clip(base + fuerza * cara * (canto > 0), 0, 1)


class Lienzo:
    """Un cuadro RGBA de n x m (float) al que se le van pegando capas."""

    def __init__(self, w, h=None):
        h = h or w
        self.rgb = np.zeros((h, w, 3))
        self.a = np.zeros((h, w))

    def pintar(self, mascara, color, alfa=1.0):
        """Pinta (encima) los píxeles de la máscara: color es un (3,) o un (h, w, 3)."""
        c = np.broadcast_to(np.asarray(color, float), self.rgb.shape)
        a = np.where(mascara, alfa, 0.0)
        self.rgb = self.rgb * (1 - a[..., None]) + c * a[..., None]
        self.a = self.a + a * (1 - self.a)

    def encima(self, otro):
        a = otro.a[..., None]
        self.rgb = self.rgb * (1 - a) + otro.rgb * a
        self.a = otro.a + self.a * (1 - otro.a)

    def lleno(self):
        return self.a > 0.5

    def contorno(self, color, diagonales=False):
        """Un contorno de un píxel por fuera de lo pintado."""
        a = self.lleno()
        v = np.zeros_like(a)
        v[1:, :] |= a[:-1, :]
        v[:-1, :] |= a[1:, :]
        v[:, 1:] |= a[:, :-1]
        v[:, :-1] |= a[:, 1:]
        if diagonales:
            v[1:, 1:] |= a[:-1, :-1]
            v[1:, :-1] |= a[:-1, 1:]
            v[:-1, 1:] |= a[1:, :-1]
            v[:-1, :-1] |= a[1:, 1:]
        self.pintar(v & ~a, color)
        return self

    def imagen(self):
        out = np.zeros(self.rgb.shape[:2] + (4,), np.uint8)
        out[..., :3] = np.clip(np.round(self.rgb), 0, 255)
        out[..., 3] = np.clip(np.round(self.a * 255), 0, 255)
        return Image.fromarray(out, 'RGBA')


def tono(r, s):
    """El color de la rampa r para lo iluminado s (0 a 1), en escalones."""
    i = np.clip(np.round(np.asarray(s) * (len(r) - 1)), 0, len(r) - 1).astype(int)
    return r[i]


def capa(n, d, color, contorno=None, umbral=0.0):
    """Una capa con lo de dentro de d pintado de color (y su contorno, si se pide)."""
    c = Lienzo(n)
    c.pintar(d < umbral, color)
    if contorno is not None:
        c.contorno(H(contorno)[:3])
    return c


# ----------------------------------------------------------------------------------------------------------------
#  Los signos: la interrogación y la exclamación, de trazo grueso
# ----------------------------------------------------------------------------------------------------------------
def sd_interrogacion(x, y, gx, gy, alto, grosor):
    """El ? de alto 'alto' con el centro en (gx, gy)."""
    r = alto * 0.22
    cy = gy - alto * 0.2
    a0, barrido = math.pi * 1.02, math.radians(232)
    gancho = sd_arco(x, y, gx, cy, r, a0, barrido, grosor)
    fx, fy = gx + r * math.cos(a0 + barrido), cy + r * math.sin(a0 + barrido)
    palo = sd_segmento(x, y, fx, fy, gx, gy + alto * 0.12, grosor)
    punto = sd_circulo(x, y, gx, gy + alto * 0.39, grosor * 1.25)
    return union(gancho, palo, punto)


def sd_exclamacion(x, y, gx, gy, alto, grosor):
    arriba = gy - alto * 0.42
    palo = union(sd_segmento(x, y, gx, arriba, gx, gy + alto * 0.04, grosor),
                 sd_segmento(x, y, gx, arriba, gx, arriba + alto * 0.18, grosor * 1.18))
    punto = sd_circulo(x, y, gx, gy + alto * 0.40, grosor * 1.15)
    return union(palo, punto)


# ----------------------------------------------------------------------------------------------------------------
#  Los iconos (cada propuesta, a 32 o a 16 píxeles)
# ----------------------------------------------------------------------------------------------------------------
def sd_huevo(x, y, cx, cy, rx, ry, punta=0.16):
    """Un huevo: una elipse más estrecha arriba."""
    t = np.clip((y - (cy - ry)) / (2 * ry), 0, 1)
    rxy = rx * (1 - punta + punta * 2 * np.sqrt(t) * (1 - 0.5 * t))
    return (np.hypot((x - cx) / rxy, (y - cy) / ry) - 1) * np.minimum(rxy, ry)


def mob_a(n):
    """El huevo moteado: crema, con motas naranjas y una ? naranja grande."""
    x, y, k = malla(n)
    crema = rampa('8a5a30', 'c99a62', 'e9cc98', 'f7e6c0', 'fffaf0')
    naranja = rampa('8a2e08', 'cc5410', 'ff8a1c', 'ffb14a', 'ffd28a')
    d = sd_huevo(x, y, 16, 17.2, 11.0, 13.6)
    s = esfera(x, y, 15.2, 16.0, 12.0, 15.0)
    L = Lienzo(n)
    L.pintar(d < 0, tono(crema, s))
    motas = [(8.6, 12.2, 1.5), (21.8, 9.4, 1.15), (23.6, 21.6, 1.7), (9.6, 24.2, 1.35), (15.5, 28.4, 1.05),
             (25.6, 15.2, 0.95), (7.0, 18.6, 1.0), (19.5, 26.0, 0.9)]
    if n < 32:
        motas = [(8.2, 12.0, 2.0), (23.4, 21.0, 2.2), (9.4, 24.0, 1.9), (22.4, 9.6, 1.6)]
    m = union(*[sd_circulo(x, y, mx, my, mr) for mx, my, mr in motas])
    L.pintar((m < 0) & (d < 0), tono(naranja, np.clip(s * 0.9, 0, 1)))
    L.contorno(H('3d200c')[:3])
    q = sd_interrogacion(x, y, 16.3, 17.6, 17.0, 1.75 if n >= 32 else 2.2)
    Q = Lienzo(n)
    Q.pintar(q < 0, tono(naranja, bisel(q, k, 1.6 * k, base=0.55, fuerza=0.4)))
    Q.contorno(H('4a1604')[:3])
    L.encima(Q)
    return L


def mob_b(n):
    """El huevo naranja: el cascarón naranja con manchas rojizas y la ? blanca."""
    x, y, k = malla(n)
    nar = rampa('5c1d06', 'a8400e', 'e0681c', 'ff9440', 'ffc488')
    roj = rampa('5a1404', '8e2408', 'b8380c', 'd8541a', 'e8742a')
    d = sd_huevo(x, y, 16, 17.2, 11.0, 13.6)
    s = esfera(x, y, 15.2, 16.0, 12.0, 15.0)
    L = Lienzo(n)
    L.pintar(d < 0, tono(nar, s))
    manchas = [(9.5, 11.5, 2.4), (22.5, 10.5, 1.8), (24.5, 22.5, 2.6), (8.5, 23.0, 2.0), (16.5, 28.5, 1.6)]
    if n < 32:
        manchas = [(9.0, 11.5, 2.8), (24.2, 22.0, 3.0), (8.4, 23.6, 2.4)]
    m = union(*[sd_circulo(x, y, mx, my, mr) for mx, my, mr in manchas])
    L.pintar((m < 0) & (d < 0), tono(roj, s))
    L.contorno(H('3a1004')[:3])
    q = sd_interrogacion(x, y, 16.3, 17.6, 17.0, 1.75 if n >= 32 else 2.2)
    blanco = rampa('b8a890', 'e8dcc8', 'fff6e8', 'ffffff')
    Q = Lienzo(n)
    Q.pintar(q < 0, tono(blanco, bisel(q, k, 1.6 * k, base=0.6, fuerza=0.4)))
    Q.contorno(H('3a1004')[:3])
    L.encima(Q)
    return L


def mob_c(n):
    """El huevo rajado: un cascarón oscuro en el que la grieta, encendida de naranja por dentro, es la ?."""
    x, y, k = malla(n)
    oscuro = rampa('1a0f0a', '2e1c12', '4a2e1e', '6a4630', '8c6448')
    d = sd_huevo(x, y, 16, 17.2, 11.0, 13.6)
    s = esfera(x, y, 15.2, 16.0, 12.0, 15.0)
    L = Lienzo(n)
    L.pintar(d < 0, tono(oscuro, s))
    # La grieta: la ? algo temblona.
    jx = x + 0.55 * np.sin(y * 2.1) * (1 if n >= 32 else 0.5)
    q = sd_interrogacion(jx, y, 16.3, 17.6, 17.0, 1.2 if n >= 32 else 1.9)
    halo = (q < 2.2 * k) & (d < -k)
    L.pintar(halo & (q >= 0), H('a8420e')[:3])
    L.pintar(q < 0, H('ff9a2a')[:3])
    if n >= 32:
        L.pintar(q < -0.55, H('ffe9a8')[:3])
    L.contorno(H('120804')[:3])
    return L


def triangulo(x, y, inset=0.0):
    pts = [(16, 3.2 + inset * 1.9), (29.6 - inset * 1.6, 27.6 - inset * 0.9), (2.4 + inset * 1.6, 27.6 - inset * 0.9)]
    return sd_poligono(x, y, pts)


def dificultad_a(n):
    """La advertencia: el triángulo amarillo de cantos redondos, con su borde oscuro y la ! negra."""
    x, y, k = malla(n)
    amar = rampa('a86c00', 'e0a400', 'ffd23a', 'ffe98a', 'fff8d0')
    d = triangulo(x, y) - 1.4
    L = Lienzo(n)
    L.pintar(d < 0, H('2a1a00')[:3])
    dentro = triangulo(x, y, 2.6 if n >= 32 else 3.0) - 1.0
    L.pintar(dentro < 0, tono(amar, bisel(dentro, k, 2.2 * k, base=0.58, fuerza=0.42)))
    e = sd_exclamacion(x, y, 16, 19.4, 13.4, 1.7 if n >= 32 else 2.1)
    L.pintar(e < 0, H('1a1000')[:3])
    L.contorno(H('140c00')[:3])
    return L


def dificultad_b(n):
    """El rombo de peligro: amarillo, con un filete negro por dentro y la ! negra (como una señal de carretera)."""
    x, y, k = malla(n)
    amar = rampa('a86c00', 'e0a400', 'ffd23a', 'ffe98a', 'fff8d0')
    pts = [(16, 1.6), (30.4, 16), (16, 30.4), (1.6, 16)]
    d = sd_poligono(x, y, pts) - 1.2
    L = Lienzo(n)
    L.pintar(d < 0, tono(amar, bisel(d, k, 2.0 * k, base=0.6, fuerza=0.4)))
    filete = (d < -2.4) & (d > (-4.0 if n >= 32 else -4.6))
    L.pintar(filete, H('1a1000')[:3])
    e = sd_exclamacion(x, y, 16, 16.8, 12.6, 1.6 if n >= 32 else 2.1)
    L.pintar(e < 0, H('1a1000')[:3])
    L.contorno(H('3a2600')[:3])
    return L


def dificultad_c(n):
    """El triángulo de obra: el borde a rayas negras y amarillas, el amarillo dentro y la ! negra."""
    x, y, k = malla(n)
    amar = rampa('a86c00', 'e0a400', 'ffd23a', 'ffe98a', 'fff8d0')
    d = triangulo(x, y) - 1.4
    L = Lienzo(n)
    rayas = np.floor((x + y) / (3.4 if n >= 32 else 4.0)) % 2 == 0
    L.pintar(d < 0, np.where(rayas[..., None], H('ffc81a')[:3], H('1a1000')[:3]))
    dentro = triangulo(x, y, 3.6 if n >= 32 else 4.0) - 1.0
    L.pintar(dentro < 0.9 * k, H('1a1000')[:3])
    L.pintar(dentro < 0, tono(amar, bisel(dentro, k, 2.0 * k, base=0.6, fuerza=0.4)))
    e = sd_exclamacion(x, y, 16, 20.0, 11.4, 1.55 if n >= 32 else 2.0)
    L.pintar(e < 0, H('1a1000')[:3])
    L.contorno(H('140c00')[:3])
    return L


ACERO = rampa('0e2238', '1f4b78', '3f86c0', '82c8f0', 'd8f6ff')


def penalizacion_a(n):
    """El grillete: la bola de hierro celeste, la cadena (un eslabón de frente con su hueco, otro de canto) y la
    argolla abierta."""
    x, y, k = malla(n)
    L = Lienzo(n)
    C = Lienzo(n)
    # La dirección de la cadena: de la anilla de la bola hacia la argolla.
    ux, uy = 0.707, -0.707
    vx, vy = 0.707, 0.707

    def eslabon(cx, cy, largo, ancho, grosor, de_frente):
        a = (x - cx) * ux + (y - cy) * uy
        b = (x - cx) * vx + (y - cy) * vy
        if de_frente:
            return np.abs(np.hypot(a / largo, b / ancho) - 1) * ancho - grosor
        return sd_caja(a, b, 0, 0, largo, grosor * 1.1, grosor)

    if n >= 32:
        partes = [eslabon(18.2, 12.4, 3.7, 2.6, 0.8, True), eslabon(22.3, 8.3, 2.6, 0.0, 0.9, False),
                  eslabon(25.9, 4.7, 3.7, 2.6, 0.8, True)]
    else:
        partes = [eslabon(18.4, 12.2, 3.4, 2.4, 1.15, True), eslabon(23.0, 7.6, 2.6, 0.0, 1.2, False)]
    cad = union(*partes)
    C.pintar(cad < 0, tono(ACERO, esfera(x, y, 19, 8, 9, 9, amb=0.35)))
    # La argolla, arriba a la derecha, abierta por abajo a la izquierda.
    if n < 32:
        arg = sd_arco(x, y, 27.0, 4.6, 3.0, math.radians(190), math.radians(255), 1.45)
        C.pintar(arg < 0, tono(ACERO, esfera(x, y, 25.5, 3.5, 5, 5, amb=0.35)))
    C.contorno(H('081624')[:3])
    L.encima(C)
    # La bola, con su anilla.
    B = Lienzo(n)
    d = sd_circulo(x, y, 11.6, 21.0, 9.4)
    s = esfera(x, y, 11.6, 21.0, 9.4, 9.4)
    anilla = np.abs(sd_circulo(x, y, 16.2, 13.6, 1.9 if n >= 32 else 2.0)) - (0.8 if n >= 32 else 1.0)
    B.pintar(anilla < 0, tono(ACERO, esfera(x, y, 15, 12, 4, 4, amb=0.3)))
    B.pintar(d < 0, tono(ACERO, s))
    if n >= 32:
        B.pintar(sd_circulo(x, y, 8.0, 17.0, 1.7) < 0, H('ffffff')[:3])
        B.pintar((np.abs(sd_circulo(x, y, 11.6, 33.6, 15.4)) < 0.5) & (d < -1.2), H('1f4b78')[:3])
    B.contorno(H('081624')[:3])
    L.encima(B)
    return L


def penalizacion_b(n):
    """El corazón roto: un corazón de hielo celeste partido en dos por una grieta en zigzag."""
    x, y, k = malla(n)
    hielo = rampa('0f3050', '2a6ea8', '58b4e8', '9ee0ff', 'e8fbff')
    zig = 16 + np.where(np.floor(y / 4.6) % 2 == 0, 1, -1) * ((y % 4.6) / 4.6 * 2.6 - 1.3)
    izq = x < zig
    sep = 1.4 if n >= 32 else 1.5
    L = Lienzo(n)
    for lado in (-1, 1):
        dx = x - lado * sep
        dy = y + (0.6 if lado < 0 else -0.2)
        d = sd_corazon(dx, dy, 16, 28.6, 21.4)
        mitad = izq if lado < 0 else ~izq
        mitad = mitad & (np.abs(x - zig) > sep * 0.9)
        s = esfera(dx, dy, 13.4, 14.0, 13.0, 13.0)
        M = Lienzo(n)
        M.pintar((d < 0) & mitad, tono(hielo, s))
        if n >= 32 and lado < 0:
            M.pintar((sd_circulo(dx, dy, 10.2, 10.6, 1.5) < 0) & (d < 0), H('ffffff')[:3])
        M.contorno(H('0a1e33')[:3])
        L.encima(M)
    return L


def penalizacion_c(n):
    """El mazo de juez: la cabeza de acero celeste con sus aros, el mango de madera y el golpe."""
    x, y, k = malla(n)
    madera = rampa('3a1e0e', '6a3a1c', '9a5e30', 'c8884c')
    L = Lienzo(n)
    # El mango, hacia abajo a la derecha.
    M = Lienzo(n)
    mango = sd_segmento(x, y, 13.0, 13.0, 28.0, 28.0, 1.7 if n >= 32 else 2.0)
    M.pintar(mango < 0, tono(madera, esfera(x, y, 20, 20, 11, 11, amb=0.35)))
    M.contorno(H('1a0c04')[:3])
    L.encima(M)
    # La cabeza, cruzada.
    giro = math.radians(-45)
    ca, sa = math.cos(giro), math.sin(giro)
    rx_ = (x - 12.2) * ca + (y - 12.2) * sa
    ry_ = -(x - 12.2) * sa + (y - 12.2) * ca
    cab = sd_caja(rx_, ry_, 0, 0, 9.8, 5.2, 1.6)
    s = np.clip(0.62 + 0.42 * (-ry_ / 5.2), 0, 1)
    C = Lienzo(n)
    C.pintar(cab < 0, tono(ACERO, s))
    aros = (np.abs(np.abs(rx_) - 6.6) < (0.9 if n >= 32 else 1.2)) & (cab < 0)
    C.pintar(aros, tono(ACERO, np.clip(s - 0.45, 0, 1)))
    C.contorno(H('081624')[:3])
    L.encima(C)
    return L


VERDE = rampa('0f3a14', '1f7a2a', '36b844', '7ae68a', 'd0ffd8')


def minijuego_a(n):
    """El mando: verde, con la cruceta, los botones y los dos de en medio."""
    x, y, k = malla(n)
    d = union(sd_caja(x, y, 16, 15.0, 13.4, 6.4, 5.0), sd_circulo(x, y, 8.0, 20.0, 6.6), sd_circulo(x, y, 24.0, 20.0, 6.6))
    s = esfera(x, y, 14.0, 13.0, 20.0, 13.0, amb=0.2)
    L = Lienzo(n)
    L.pintar(d < 0, tono(VERDE, s))
    g = 1.25 if n >= 32 else 1.6
    cruz = union(sd_caja(x, y, 8.6, 16.4, 3.9, g, 0.4), sd_caja(x, y, 8.6, 16.4, g, 3.9, 0.4))
    L.pintar(cruz < 0, H('0c1a0e')[:3])
    if n >= 32:
        L.pintar((cruz < 0) & (x < 8.6) & (y < 16.4) & (cruz > -0.9), H('2a4a2e')[:3])
    for bx, by, col in ((22.0, 18.0, 'e8ffe8'), (25.6, 14.4, 'fff07a')):
        b = sd_circulo(x, y, bx, by, 2.0 if n >= 32 else 2.3)
        L.pintar(b < 0.9 * k, H('0c1a0e')[:3])
        L.pintar(b < 0, H(col)[:3])
    if n >= 32:
        for bx in (14.2, 17.8):
            L.pintar(sd_caja(x, y, bx, 11.4, 1.3, 0.6, 0.5) < 0, H('0c1a0e')[:3])
    L.contorno(H('071a0a')[:3])
    return L


def minijuego_b(n):
    """El dado: verde, de lado (tres caras), con los puntos blancos."""
    x, y, k = malla(n)
    arriba = [(16, 2.6), (28.6, 9.4), (16, 16.2), (3.4, 9.4)]
    izq = [(3.4, 9.4), (16, 16.2), (16, 29.6), (3.4, 22.8)]
    der = [(16, 16.2), (28.6, 9.4), (28.6, 22.8), (16, 29.6)]
    L = Lienzo(n)
    for pts, col in ((arriba, '7ae68a'), (izq, '36b844'), (der, '1f7a2a')):
        L.pintar(sd_poligono(x, y, pts) < 0.2, H(col)[:3])
    # Los cantos de luz.
    if n >= 32:
        L.pintar((np.abs(sd_segmento(x, y, 3.4, 9.4, 16, 16.2, 0)) < 0.55), H('b8f7c2')[:3])
        L.pintar((np.abs(sd_segmento(x, y, 16, 16.2, 28.6, 9.4, 0)) < 0.55), H('b8f7c2')[:3])
        L.pintar((np.abs(sd_segmento(x, y, 16, 16.2, 16, 29.6, 0)) < 0.5), H('58cc66')[:3])

    def punto(cx, cy, ux, uy, vx, vy, r):
        # una elipse en la cara (u, v: los ejes de la cara)
        dx, dy = x - cx, y - cy
        det = ux * vy - uy * vx
        a = (dx * vy - dy * vx) / det
        b = (ux * dy - uy * dx) / det
        return np.hypot(a, b) - r

    rp = 0.22 if n >= 32 else 0.3
    caras = (
        ((16, 9.4), (6.3, 3.4), (-6.3, 3.4), [(0, 0)], 'ffffff'),
        ((9.7, 19.3), (6.3, 3.4), (0, 6.7), [(-0.5, -0.5), (0.5, 0.5)], 'f2fff4'),
        ((22.3, 19.3), (6.3, -3.4), (0, 6.7), [(-0.5, -0.5), (0, 0), (0.5, 0.5)] if n >= 32 else [(-0.45, -0.45), (0.45, 0.45)],
         'e0f8e4'),
    )
    for (cx, cy), (ux, uy), (vx, vy), pips, col in caras:
        for a, b in pips:
            px_, py_ = cx + a * ux + b * vx, cy + a * uy + b * vy
            L.pintar(punto(px_, py_, ux, uy, vx, vy, rp) < 0, H(col)[:3])
    L.contorno(H('071a0a')[:3])
    return L


def minijuego_c(n):
    """La palanca de recreativa: la bola verde, el palo cromado y la caja con su botón."""
    x, y, k = malla(n)
    L = Lienzo(n)
    caja = sd_caja(x, y, 16, 25.0, 12.6, 4.8, 2.0)
    C = Lienzo(n)
    C.pintar(caja < 0, np.where((y < 23.0)[..., None], H('2a4a2e')[:3], H('12261a')[:3]))
    if n >= 32:
        C.pintar((caja < 0) & (y < 21.4), H('3e6a44')[:3])
    bot = sd_elipse(x, y, 24.4, 22.4, 2.6, 1.5)
    C.pintar(bot < 0, H('7ae68a')[:3])
    C.contorno(H('071a0a')[:3])
    L.encima(C)
    P = Lienzo(n)
    palo = sd_segmento(x, y, 14.6, 22.0, 12.4, 10.0, 1.3 if n >= 32 else 1.6)
    gris = rampa('3a4250', '7a8496', 'c8d0dc', 'f4f8ff')
    P.pintar(palo < 0, tono(gris, esfera(x, y, 13, 16, 3, 12, amb=0.3)))
    P.contorno(H('101418')[:3])
    L.encima(P)
    B = Lienzo(n)
    d = sd_circulo(x, y, 12.0, 8.6, 6.4)
    B.pintar(d < 0, tono(VERDE, esfera(x, y, 12.0, 8.6, 6.4, 6.4)))
    if n >= 32:
        B.pintar(sd_circulo(x, y, 9.6, 6.2, 1.3) < 0, H('ffffff')[:3])
    B.contorno(H('071a0a')[:3])
    L.encima(B)
    return L


PROPUESTAS_ICONOS = {
    'mob': [('A', 'Huevo moteado', mob_a), ('B', 'Huevo naranja', mob_b), ('C', 'Huevo rajado', mob_c)],
    'dificultad': [('A', 'Triángulo', dificultad_a), ('B', 'Rombo', dificultad_b), ('C', 'Triángulo de obra', dificultad_c)],
    'penalizacion': [('A', 'Corazón roto', penalizacion_b), ('B', 'Grillete', penalizacion_a), ('C', 'Mazo de juez', penalizacion_c)],
    'minijuego': [('A', 'Mando', minijuego_a), ('B', 'Dado', minijuego_b), ('C', 'Palanca de recreativa', minijuego_c)],
}


def icono(final, letra, n):
    for l, _, f in PROPUESTAS_ICONOS[final]:
        if l == letra:
            return f(n).imagen()
    raise KeyError((final, letra))


def borroso(im, largo=17):
    """El icono corrido hacia abajo (lo que se ve cuando el rodillo gira deprisa): una media de copias desplazadas,
    con el alfa premultiplicado para que no salgan bordes oscuros."""
    a = np.asarray(im, float) / 255.0
    pre = a[..., :3] * a[..., 3:4]
    al = a[..., 3]
    n = a.shape[0]
    acc = np.zeros_like(pre)
    acc_a = np.zeros_like(al)
    pesos = 0.0
    for k in range(-largo // 2, largo // 2 + 1):
        w = 1.0 - abs(k) / (largo / 2 + 1)
        sh = np.roll(pre, k, axis=0)
        sa = np.roll(al, k, axis=0)
        if k > 0:
            sh[:k] = 0
            sa[:k] = 0
        elif k < 0:
            sh[k:] = 0
            sa[k:] = 0
        acc += w * sh
        acc_a += w * sa
        pesos += w
    acc /= pesos
    acc_a /= pesos
    rgb = np.where(acc_a[..., None] > 1e-6, acc / np.maximum(acc_a[..., None], 1e-6), 0)
    out = np.zeros((n, n, 4), np.uint8)
    out[..., :3] = np.clip(rgb * 255, 0, 255)
    out[..., 3] = np.clip(acc_a * 255, 0, 255)
    return Image.fromarray(out, 'RGBA')


# El lado de los iconos del rodillo (el medallón los enseña grandes: se pintan a 48, con su detalle, y no ampliados).
ICONO = 48


def iconos():
    """Los iconos elegidos, al mod: la tira del rodillo (nítida y corrida) y el de cada final para el chat."""
    gui = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/ruleta')
    item = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
    os.makedirs(gui, exist_ok=True)
    tira = Image.new('RGBA', (ICONO * len(FINALES), ICONO), (0, 0, 0, 0))
    tira_b = Image.new('RGBA', (ICONO * len(FINALES), ICONO), (0, 0, 0, 0))
    for i, f in enumerate(FINALES):
        grande = icono(f, ELEGIDOS[f], ICONO)
        tira.paste(grande, (ICONO * i, 0))
        tira_b.paste(borroso(grande, 25), (ICONO * i, 0))
        icono(f, ELEGIDOS[f], 16).save(os.path.join(item, f'ruleta_{f}.png'))
    tira.save(os.path.join(gui, 'iconos.png'))
    tira_b.save(os.path.join(gui, 'iconos_borrosos.png'))
    with open(os.path.join(gui, 'iconos_borrosos.png.mcmeta'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps({'texture': {'blur': True, 'clamp': True}}, indent=2) + '\n')
    print('iconos:', ', '.join(f'{f} {ELEGIDOS[f]}' for f in FINALES))


# ----------------------------------------------------------------------------------------------------------------
#  El medallón (a una unidad por píxel). Segunda versión, 17-10-2026. Juan: «usar bien su espacio, así como hace la
#  ruleta de DEDsafío, que es su círculo». La tragaperras es un medallón redondo en el que el rodillo lo ocupa casi
#  todo: el aro de oro con sus bombillas, un anillo de laca con el sol art déco y cuatro gemas (una por final), el aro
#  de cromo de la ventana y, arriba, la cresta con la atalaya. Lo que se mueve o se enciende lo pinta el juego encima
#  (RuletaHud): el rodillo por detrás del hueco, las bombillas, las gemas, el farol, las flechas, monedas y destellos.
#  Las medidas de aquí son las mismas que las de RuletaHud.
# ----------------------------------------------------------------------------------------------------------------
HOJA = 256
MED_W, MED_H = 176, 196
CX, CY = 88, 106          # el centro del círculo
R_ARO = 86                # el borde de fuera del aro de oro
R_BOMBILLAS = 80.5        # el círculo de las bombillas
R_LACA = 75               # el borde de dentro del aro (empieza la laca)
R_GEMAS = 68.5            # el círculo de las gemas
R_CROMO = 62              # el borde de fuera del aro de cromo
R_VENTANA = 57            # el hueco del rodillo
CRESTA = (88, 17)         # el centro del medallón de la atalaya, arriba
BOMBILLA = (176, 0, 7)    # la bombilla encendida (blanca: el juego la tiñe)
DESTELLO = (184, 0, 9)
FLECHA = (194, 0, 12)     # la flecha de la línea de premio, de 12 x 14 (apunta a la derecha)
MONEDA = (208, 0, 12)
# Las gemas, una por final (el orden de FINALES), en las diagonales: arriba a la izquierda el huevo, arriba a la
# derecha la advertencia, abajo a la derecha la penalización y abajo a la izquierda el minijuego.
GEMAS = (-135, -45, 45, 135)
GEMA_COLOR = {'mob': ('5a2204', 'c4500e', 'ff8a1c', 'ffc27a'), 'dificultad': ('5a4200', 'b88a00', 'ffd23a', 'fff0a0'),
              'penalizacion': ('0a2a48', '2a6ea8', '7fd8ff', 'd8f6ff'), 'minijuego': ('0a3a12', '1f7a2a', '6ee36e', 'd0ffd8')}


def bombillas():
    """Las 22 bombillas del aro, en el orden en que corre la luz: de arriba a la derecha, en el sentido de las agujas
    del reloj, hasta arriba a la izquierda (la cresta tapa las de arriba del todo)."""
    out = []
    for k in range(22):
        a = math.radians(-67.5 + 15 * k)
        out.append((int(round(CX + R_BOMBILLAS * math.cos(a))), int(round(CY + R_BOMBILLAS * math.sin(a)))))
    return out


def gemas():
    out = []
    for g in GEMAS:
        a = math.radians(g)
        out.append((int(round(CX + R_GEMAS * math.cos(a))), int(round(CY + R_GEMAS * math.sin(a)))))
    return out


LACA = rampa('0e0816', '1a0f26', '2a1a3a', '3b2650', '4e3466')
ORO = rampa('5a3608', '9a6214', 'd49a28', 'f2c64a', 'ffe58a', 'fff6d0')
CROMO = rampa('2a3040', '5a6478', '9aa4b8', 'd4dae6', 'ffffff')
CONTORNO = H('0a0610')[:3]


def sd_anillo(x, y, cx, cy, r0, r1):
    """Un anillo entre los radios r0 y r1 (negativo dentro)."""
    d = np.hypot(x - cx, y - cy)
    return np.maximum(d - r1, r0 - d)


def torre(x, y, cx, cy, s):
    """La atalaya del emblema, con el centro en (cx, cy) y a escala s: sus partes por distancia."""
    u = (x - cx) / s
    v = (y - cy) / s
    p = {
        'tejado': sd_poligono(u, v, [(0, -12.4), (6.8, -6.8), (-6.8, -6.8)]),
        'farol': sd_caja(u, v, 0, -5.1, 3.9, 1.8, 0.3),
        'balcon': sd_caja(u, v, 0, -2.4, 6.8, 1.0, 0.3),
        'fuste': sd_poligono(u, v, [(-3.4, -1.6), (3.4, -1.6), (5.2, 10.2), (-5.2, 10.2)]),
        'suelo': sd_caja(u, v, 0, 10.9, 8.6, 0.8, 0.3),
        'puerta': sd_caja(u, v, 0, 8.6, 1.2, 1.9, 0.9),
        'luz': sd_caja(u, v, 0, -5.1, 2.6, 1.0, 0.2),
    }
    return {k: d * s for k, d in p.items()}


def medallon():
    """La hoja del medallón."""
    W, Hh = MED_W, MED_H
    x, y = malla_rect(W, Hh)
    L = Lienzo(W, Hh)

    def bisel_de(d, ancho, base=0.6, fuerza=0.4):
        return bisel(d, 1.0, ancho, base=base, fuerza=fuerza)

    r = np.hypot(x - CX, y - CY)
    ang = np.arctan2(y - CY, x - CX)
    # Un poco más de luz arriba a la izquierda en todo el medallón (que tenga volumen).
    luz = np.clip(-((x - CX) * 0.55 + (y - CY) * 0.75) / (R_ARO * 1.6), -0.25, 0.25)
    # El anillo de laca, con el sol: rayos que alternan.
    laca = sd_anillo(x, y, CX, CY, R_CROMO - 0.5, R_LACA + 0.5)
    rayo = (np.floor((ang + math.pi) / math.radians(7.5)) % 2) == 0
    tono_laca = np.where(rayo, 0.42, 0.30) + luz * 0.6 + np.clip((R_LACA - r) / 40, 0, 0.12)
    L.pintar(laca < 0, tono(LACA, np.clip(tono_laca, 0, 1)))
    # Los filetes de oro del anillo de laca.
    for rf in (R_CROMO + 1.6, R_LACA - 1.4):
        L.pintar(np.abs(r - rf) < 0.55, tono(ORO, np.clip(0.55 + luz, 0, 1)))
    # Las gemas (apagadas: el juego las enciende), con su engaste de oro.
    for (gx, gy), f in zip(gemas(), FINALES):
        cx_, cy_ = gx + 0.5, gy + 0.5
        eng = sd_circulo(x, y, cx_, cy_, 4.8)
        L.pintar(eng < 0, tono(ORO, bisel_de(eng, 1.5, base=0.55)))
        gem = sd_poligono(x, y, [(cx_, cy_ - 3.4), (cx_ + 3.4, cy_), (cx_, cy_ + 3.4), (cx_ - 3.4, cy_)])
        c = rampa(*GEMA_COLOR[f])
        L.pintar(gem < 0, tono(c, np.clip(0.35 + 0.5 * esfera(x, y, cx_ - 0.8, cy_ - 0.8, 3.4, 3.4, amb=0.1) - 0.25, 0, 1)))
        L.pintar(sd_circulo(x, y, cx_ - 1.0, cy_ - 1.0, 0.7) < 0, c[3] * 0.85)
    # El remache de abajo.
    rem = sd_circulo(x, y, CX + 0.5, CY + R_GEMAS + 0.5, 2.2)
    L.pintar(rem < 0, tono(ORO, esfera(x, y, CX, CY + R_GEMAS, 2.2, 2.2, amb=0.35)))
    # El aro de oro, con dos surcos y su bisel.
    aro = sd_anillo(x, y, CX, CY, R_LACA, R_ARO)
    L.pintar(aro < 0, tono(ORO, np.clip(bisel_de(aro, 2.2, base=0.6, fuerza=0.42) + luz * 0.5, 0, 1)))
    for rs in (R_ARO - 1.9, R_LACA + 1.4):
        L.pintar((np.abs(r - rs) < 0.5) & (aro < -0.4), ORO[1])
    # Los casquillos de las bombillas (la bombilla apagada; el juego pinta la encendida encima).
    for bx, by in bombillas():
        cx_, cy_ = bx + 0.5, by + 0.5
        cas = sd_circulo(x, y, cx_, cy_, 3.7)
        L.pintar(cas < 0.8, ORO[0])
        L.pintar(cas < 0, tono(ORO, bisel_de(cas, 1.4, base=0.52)))
        vid = sd_circulo(x, y, cx_, cy_, 2.4)
        L.pintar(vid < 0, tono(rampa('2a1606', '4a2a0e', '6a4416', '8a6024'), esfera(x, y, cx_, cy_, 2.4, 2.4, amb=0.3)))
    # El aro de cromo de la ventana.
    cromo = sd_anillo(x, y, CX, CY, R_VENTANA, R_CROMO)
    L.pintar(cromo < 0, tono(CROMO, np.clip(bisel_de(cromo, 2.0, base=0.56, fuerza=0.44) + luz * 0.4, 0, 1)))
    # La cresta: un escudo de oro sobre el aro con el medallón de la atalaya.
    qx, qy = CRESTA
    escudo = union(sd_circulo(x, y, qx + 0.5, qy + 0.5, 16.2),
                   sd_poligono(x, y, [(qx - 11.5, qy + 6), (qx + 12.5, qy + 6), (qx + 16.5, qy + 15.5), (qx - 15.5, qy + 15.5)]))
    L.pintar(escudo < 0.9, CONTORNO)
    L.pintar(escudo < 0, tono(ORO, np.clip(bisel_de(escudo, 2.0, base=0.62, fuerza=0.4) + luz * 0.4, 0, 1)))
    disco = sd_circulo(x, y, qx + 0.5, qy + 0.5, 12.6)
    L.pintar(disco < 0, tono(LACA, 0.2 + 0.32 * esfera(x, y, qx, qy, 12.6, 12.6)))
    L.pintar((disco < 0) & (disco > -1.0), ORO[1])
    t = torre(x, y, qx + 0.5, qy + 1.2, 0.74)
    cuerpo = union(t['tejado'], t['farol'], t['balcon'], t['fuste'], t['suelo'])
    L.pintar(cuerpo < 0.7, LACA[0])
    L.pintar(cuerpo < 0, tono(ORO, bisel_de(cuerpo, 1.2, base=0.6, fuerza=0.42)))
    L.pintar(t['tejado'] < 0, tono(ORO, np.clip(0.55 + 0.45 * (qx + 0.5 - x) / 5, 0.2, 1)))
    L.pintar(t['puerta'] < 0, LACA[0])
    L.pintar(t['luz'] < 0, H('fff2c0')[:3])
    # Todo con su contorno oscuro, y el hueco de la ventana vacío.
    L.contorno(CONTORNO)
    vacio = r < R_VENTANA
    L.a[vacio] = 0.0
    L.rgb[vacio] = 0.0

    hoja = Lienzo(HOJA, HOJA)
    hoja.rgb[:Hh, :W] = L.rgb
    hoja.a[:Hh, :W] = L.a

    def pegar(lz, u, v):
        h_, w_ = lz.a.shape
        hoja.rgb[v:v + h_, u:u + w_] = lz.rgb
        hoja.a[v:v + h_, u:u + w_] = lz.a

    # La bombilla encendida: blanca y más blanca en el centro (el juego la tiñe del color que toque).
    u, v, n = BOMBILLA
    ex, ey = malla_rect(n, n)
    E = Lienzo(n)
    d = sd_circulo(ex, ey, n / 2, n / 2, 3.0)
    E.pintar(d < 0, np.where((sd_circulo(ex, ey, n / 2 - 0.6, n / 2 - 0.6, 1.4) < 0)[..., None], 255.0, 205.0))
    pegar(E, u, v)
    # El destello: una estrella de cuatro puntas.
    u, v, n = DESTELLO
    sx, sy = malla_rect(n, n)
    S = Lienzo(n)
    c = n / 2
    rombo = np.abs(sx - c) + np.abs(sy - c)
    cruz = np.minimum(np.abs(sx - c) * 4 + np.abs(sy - c), np.abs(sy - c) * 4 + np.abs(sx - c))
    S.pintar(cruz < 4.6, 200.0)
    S.pintar(rombo < 1.6, 255.0)
    pegar(S, u, v)
    # La flecha de la línea de premio (la de la derecha es la misma del revés).
    u, v, n = FLECHA
    fx, fy = malla_rect(12, 14)
    F = Lienzo(12, 14)
    fl = sd_poligono(fx, fy, [(1.2, 1.2), (10.6, 7.0), (1.2, 12.8)])
    F.pintar(fl < 0, tono(ORO, bisel(fl, 1.0, 1.4, base=0.66, fuerza=0.4)))
    F.contorno(CONTORNO)
    pegar(F, u, v)
    # La moneda, de frente (el juego la estrecha para que gire).
    u, v, n = MONEDA
    mx, my = malla_rect(n, n)
    M = Lienzo(n)
    d = sd_circulo(mx, my, n / 2, n / 2, n / 2 - 1.0)
    M.pintar(d < 0, tono(ORO, bisel(d, 1.0, 1.6, base=0.62)))
    est = sd_poligono(mx, my, [(n / 2 + 3.0 * math.cos(-math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else 0.45),
                                n / 2 + 3.0 * math.sin(-math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else 0.45))
                               for i in range(10)])
    M.pintar(est < 0, ORO[5])
    M.contorno(H('3a2204')[:3])
    pegar(M, u, v)

    gui = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/ruleta')
    os.makedirs(gui, exist_ok=True)
    hoja.imagen().save(os.path.join(gui, 'maquina.png'))
    print('medallon: hoja de', HOJA, 'x', HOJA, '; bombillas', len(bombillas()), '; gemas', gemas())


# Los textos de los rótulos del chat y su animación (la del de MOMENTO FRACTURA: 36 fotogramas de 2 ticks; el brillo
# cruza en los 22 primeros).
CARTELES = {'mob': 'NUEVO MOB:', 'dificultad': 'CAMBIO DE DIFICULTAD:', 'penalizacion': 'PENALIZACIÓN:',
            'minijuego': 'MINIJUEGO:'}
CARTEL_CUADROS = mm.CARTEL_CUADROS
CARTEL_CRUZA = mm.CARTEL_CRUZA


# ----------------------------------------------------------------------------------------------------------------
#  Los rótulos del chat. Segunda versión (17-10-2026). Juan: «ahorita no se lee muy bien; deja el brillo que pasa,
#  pero el tipo de letra y la textura que tiene es muy metálico». Las letras de antes ocupaban dos tercios del alto de
#  su cuadro (en el chat salían más pequeñas que el propio texto) y el metal (la franja oscura en medio, el bisel y el
#  halo) las volvía ruido. Ahora: una letra propia de 5 x 7 a escala 4 (28 de los 32 de alto: tan alta como el texto
#  del chat), colores planos y el brillo que cruza. Tres estilos para elegir:
#    A  Clara      la letra fina del color del final, con su contorno y su sombra
#    B  Negrita    la misma más gruesa, en dos tonos planos (arriba más clara) y con el contorno del color en oscuro
#    C  Etiqueta   las letras oscuras sobre una placa del color del final
# ----------------------------------------------------------------------------------------------------------------
LETRA = {
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    'D': ["###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    'J': ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ':': [".", "#", ".", ".", ".", "#", "."],
    '.': [".", ".", ".", ".", ".", ".", "#"],
    ',': ["..", "..", "..", "..", "..", ".#", "#."],
    '!': ["#", "#", "#", "#", "#", ".", "#"],
    '¡': ["#", ".", "#", "#", "#", "#", "#"],
    '?': [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    '¿': ["..#..", ".....", "..#..", ".#...", "#....", "#...#", ".###."],
    '-': ["...", "...", "...", "###", "...", "...", "..."],
    "'": ["#", "#", ".", ".", ".", ".", "."],
    ' ': ["..", "..", "..", "..", "..", "..", ".."],
}
# Las vocales con tilde: la letra pierde una fila de en medio (queda de 6, con su forma: la O sigue siendo una O) y
# baja una fila, y la tilde va arriba, a media escala (ver rotulo()). La Ñ pierde una de abajo, para no romper la
# diagonal.
for _b, _a in (('A', 'Á'), ('E', 'É'), ('I', 'Í'), ('O', 'Ó'), ('U', 'Ú'), ('N', 'Ñ')):
    LETRA[_a] = LETRA[_b]
TILDES = {'Á': 'tilde', 'É': 'tilde', 'Í': 'tilde', 'Ó': 'tilde', 'Ú': 'tilde', 'Ñ': 'virgulilla'}
SIN_FILA = {'Ñ': 5}
ROTULO_ESC = 4
# Los colores de cada final: el del chat, uno claro, uno hondo y uno oscuro (el contorno y las letras de la etiqueta).
ROTULO_COLOR = {
    'mob': ((255, 154, 60), (255, 216, 168), (206, 96, 22), (64, 22, 2)),
    'dificultad': ((255, 210, 58), (255, 241, 176), (214, 160, 18), (60, 40, 0)),
    'penalizacion': ((127, 216, 255), (222, 246, 255), (58, 150, 222), (6, 34, 62)),
    'minijuego': ((110, 227, 110), (212, 255, 212), (48, 168, 60), (4, 44, 12)),
}
ROTULOS = (('A', 'Clara'), ('B', 'Negrita'), ('C', 'Etiqueta'))
# El estilo que va en el mod (Juan elige en la página).
ROTULO = 'B'


def _mascara_texto(texto, esc, grueso, y0, ancho_extra):
    """La máscara de las letras (lista de filas de bools) y su ancho: cada letra a escala esc, engordada 'grueso'
    píxeles a la derecha, y la tilde a media escala encima de las que la llevan."""
    avance = []
    for c in texto:
        g = LETRA[c]
        avance.append(len(g[0]) * esc + grueso + ancho_extra)
    ancho = sum(avance) - ancho_extra
    return avance, ancho


def rotulo(texto, final, estilo):
    """Los cuadros del rótulo: una lista de imágenes (una por fotograma de la animación) del ancho de N cuadros de 32."""
    base, claro, hondo, oscuro = ROTULO_COLOR[final]
    etiqueta = estilo == 'C'
    esc = 3 if etiqueta else ROTULO_ESC
    grueso = 2 if estilo == 'B' else 0
    hueco = 5 if etiqueta else (7 if estilo == 'B' else 5)
    alto_letra = 7 * esc
    _, ancho_txt = _mascara_texto(texto, esc, grueso, 0, hueco)
    _, ancho_negrita = _mascara_texto(texto, ROTULO_ESC, 2, 0, 7)
    cuadros = -(-(ancho_negrita + 16) // 32)
    W, Hh = cuadros * 32, 32
    # Pegado a la izquierda (al icono): lo que sobra queda a la derecha, donde no se nota.
    x0 = 13 if etiqueta else 4
    y0 = (Hh - alto_letra) // 2
    dentro = np.zeros((Hh, W), bool)
    fila_de = np.full((Hh, W), -1.0)
    x = x0
    for c in texto:
        g = LETRA[c]
        tilde = TILDES.get(c)
        quita = SIN_FILA.get(c, 2)
        filas = g[:quita] + g[quita + 1:] if tilde else g      # con tilde, la letra queda de 6 filas y baja una
        dy0 = y0 + (esc if tilde else 0)
        for fy, fila in enumerate(filas):
            for fx, ch in enumerate(fila):
                if ch == '#':
                    ya, xa = dy0 + fy * esc, x + fx * esc
                    dentro[ya:ya + esc, xa:xa + esc + grueso] = True
                    fila_de[ya:ya + esc, xa:xa + esc + grueso] = (fy + (1 if tilde else 0)) / 6.0
        if tilde:
            # La tilde, a media escala, en la fila de arriba (que la letra ha dejado libre).
            m = esc // 2
            cx_ = x + (len(g[0]) * esc) // 2
            if tilde == 'tilde':
                celdas = ((1, 0), (0, 1))
            else:
                celdas = ((-2, 1), (-1, 0), (0, 1), (1, 0))
            for (cxl, cyl) in celdas:
                xa, ya = cx_ + cxl * m, y0 + cyl * m
                dentro[ya:ya + m, xa:xa + m + grueso // 2] = True
                fila_de[ya:ya + m, xa:xa + m + grueso // 2] = 0.0
        x += len(g[0]) * esc + grueso + hueco

    def mover(mask, dy, dx):
        out = np.zeros_like(mask)
        h, w = mask.shape
        out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = mask[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
        return out

    def vecinos(mask, r):
        out = np.zeros_like(mask)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if abs(dx) + abs(dy) <= r:
                    out |= mover(mask, dy, dx)
        return out

    ys, xs = np.mgrid[0:Hh, 0:W]
    cuadros_img = []
    for f in range(CARTEL_CUADROS):
        franja = -30 + (W + 60) * f / (CARTEL_CRUZA - 1) if f < CARTEL_CRUZA else -1000
        d = np.abs(xs - franja - (ys - y0) * 0.55)
        luz = np.where(d < 7, np.clip(1 - d / 7, 0, 1) ** 1.2, 0.0) + np.where(np.abs(xs - (franja - 12) - (ys - y0) * 0.55) < 2.5, 0.45, 0.0)
        rgb = np.zeros((Hh, W, 3))
        a = np.zeros((Hh, W))

        def poner(mask, color, alfa=1.0):
            nonlocal rgb, a
            col = np.broadcast_to(np.asarray(color, float), rgb.shape)
            rgb = np.where(mask[..., None], col, rgb)
            a = np.where(mask, alfa, a)

        if etiqueta:
            # La placa: del color del final, más clara arriba, con el canto de abajo hondo y el contorno oscuro.
            px0, px1, py0, py1 = 3, x0 + ancho_txt + 10, 2, Hh - 3
            placa = sd_caja(xs + 0.5, ys + 0.5, (px0 + px1) / 2, (py0 + py1) / 2, (px1 - px0) / 2, (py1 - py0) / 2, 5)
            borde = (placa < 1.2) & (placa >= 0)
            sombra = sd_caja(xs + 0.5, ys + 0.5, (px0 + px1) / 2 + 1, (py0 + py1) / 2 + 2, (px1 - px0) / 2, (py1 - py0) / 2, 5) < 0
            poner(sombra & ~(placa < 1.2), (0, 0, 0), 0.45)
            arriba = ys < (py0 + py1) / 2
            color_placa = np.where(arriba[..., None], np.array(claro) * 0.35 + np.array(base) * 0.65, np.array(base, float))
            color_placa = np.where((ys >= py1 - 3)[..., None], np.array(hondo, float), color_placa)
            color_placa = color_placa + (255 - color_placa) * luz[..., None] * 0.75
            poner(placa < 0, color_placa)
            poner(borde, oscuro)
            # Las letras, oscuras, con un filo claro abajo (como grabadas).
            filo = mover(dentro, 1, 0) & ~dentro & (placa < -1)
            poner(filo, np.array(claro, float))
            poner(dentro, oscuro)
        else:
            contorno = vecinos(dentro, 2 if estilo == 'B' else 1) & ~dentro
            sombra = mover(dentro | contorno, 2, 1) & ~(dentro | contorno)
            poner(sombra, (0, 0, 0), 0.5)
            poner(contorno, oscuro)
            if estilo == 'B':
                # Dos tonos planos: arriba el claro mezclado, abajo el del final; y un filo de luz arriba de cada trazo.
                tono_ = np.where((fila_de < 0.45)[..., None], np.array(base) * 0.6 + np.array(claro) * 0.4, np.array(base, float))
                filo = dentro & ~mover(dentro, 1, 0)
                tono_ = np.where(filo[..., None], np.array(claro, float), tono_)
            else:
                tono_ = np.broadcast_to(np.array(base, float), rgb.shape).copy()
                filo = dentro & ~mover(dentro, 1, 0)
                tono_ = np.where(filo[..., None], np.array(base) * 0.5 + np.array(claro) * 0.5, tono_)
            tono_ = tono_ + (255 - tono_) * luz[..., None]
            poner(dentro, tono_)
        # El destello en estrella en lo alto de la franja.
        if 0 <= franja < W:
            sx, sy = int(franja + 2), y0 + 1
            for k in range(-4, 5):
                for (qx, qy) in ((sx + k, sy), (sx, sy + k)):
                    if 0 <= qx < W and 0 <= qy < Hh:
                        al = 1 - abs(k) / 5
                        rgb[qy, qx] = rgb[qy, qx] * (1 - al) + 255 * al if a[qy, qx] > 0 else (255, 250, 240)
                        a[qy, qx] = max(a[qy, qx], al)
        im = np.zeros((Hh, W, 4), np.uint8)
        im[..., :3] = np.clip(rgb, 0, 255)
        im[..., 3] = np.clip(a * 255, 0, 255)
        cuadros_img.append(Image.fromarray(im))
    return cuadros_img


def carteles():
    """Los cuatro rótulos del mod (en el estilo ROTULO), partidos en cuadros de 32 x 32 animados; dice cuántos tiene
    cada uno (los mismos que Ruleta.Fin)."""
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
    for f in FINALES:
        texto = CARTELES[f]
        cuadros_img = rotulo(texto, f, ROTULO)
        n = cuadros_img[0].width // 32
        for viejo in os.listdir(carpeta):
            if viejo.startswith(f'ruleta_{f}_cartel_'):
                os.remove(os.path.join(carpeta, viejo))
        for i in range(n):
            tira = Image.new('RGBA', (32, 32 * CARTEL_CUADROS), (0, 0, 0, 0))
            for k, im in enumerate(cuadros_img):
                tira.paste(im.crop((i * 32, 0, i * 32 + 32, 32)), (0, k * 32))
            ruta = os.path.join(carpeta, f'ruleta_{f}_cartel_{i:02d}.png')
            tira.save(ruta)
            with open(ruta + '.mcmeta', 'w', encoding='utf-8', newline='\n') as fh:
                json.dump({'animation': {'frametime': 2, 'interpolate': False}}, fh, indent=2)
                fh.write('\n')
        print(f'rotulo {texto} ({ROTULO}):', n, 'cuadros')


def rotulos_propuestas(carpeta):
    """Los tres estilos de cada rótulo, como hojas de fotogramas (uno debajo de otro), para la página."""
    os.makedirs(carpeta, exist_ok=True)
    for estilo, _ in ROTULOS:
        for f in FINALES:
            cuadros_img = rotulo(CARTELES[f], f, estilo)
            w = cuadros_img[0].width
            hoja = Image.new('RGBA', (w, 32 * len(cuadros_img)), (0, 0, 0, 0))
            for k, im in enumerate(cuadros_img):
                hoja.paste(im, (0, 32 * k))
            hoja.save(os.path.join(carpeta, f'rotulo_{estilo}_{f}.png'))
    print('rotulos en', carpeta)


def propuestas(carpeta):
    """Todas las propuestas, a 48 (el rodillo) y a 16 (el chat), para la página."""
    os.makedirs(carpeta, exist_ok=True)
    for f, lista in PROPUESTAS_ICONOS.items():
        for letra, nombre, fn in lista:
            fn(ICONO).imagen().save(os.path.join(carpeta, f'{f}_{letra}_{ICONO}.png'))
            fn(16).imagen().save(os.path.join(carpeta, f'{f}_{letra}_16.png'))
    print('propuestas en', carpeta)


def main():
    iconos()
    medallon()
    carteles()
    if PROPUESTAS:
        propuestas(PROPUESTAS)
        rotulos_propuestas(PROPUESTAS)
    print('ok')


if __name__ == '__main__':
    main()

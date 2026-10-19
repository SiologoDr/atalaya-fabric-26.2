"""
Los iconos del catálogo (16 x 16, en el cuadro de 32 unidades del pincel de ruleta.py): uno por cambio de dificultad
(cambio/<id>) y uno por momento (momento/<id>). Los usa catalogo.py.

Se hacen con piezas que se repiten (un corazón, una calavera, una llama, una cara de creeper...) y una marca encima que
dice qué les pasa: tachado (ya no), una flecha (más o menos), un ×N, un rayo, un reloj... Así cada icono se lee de un
vistazo aunque sea pequeño.
"""
import math

import numpy as np

import menus_cambios as mc
from ruleta import (H, Lienzo, bisel, esfera, malla, rampa, sd_caja, sd_circulo, sd_corazon, sd_elipse,
                    sd_poligono, sd_segmento, tono, union)

OSCURO = mc.OSCURO
ORO = mc.ORO

# Las rampas de los materiales (de lo hondo a lo claro).
R_ROJO = rampa('6a0808', 'b8141a', 'e8322a', 'ff7a60', 'ffd0c8')
R_FUEGO = rampa('7a1a04', 'c84a0a', 'f08a1a', 'ffc84a', 'fff2b0')
R_AGUA = rampa('0a2a5a', '1a5aa0', '3a90d8', '7ac8f8', 'd0f0ff')
R_VERDE = rampa('0a3a12', '1a6a24', '3aa040', '7ad868', 'd0ffc0')
R_CREEPER = rampa('0e3a0e', '1f6a1f', '3c9a32', '6cc84e', 'b0f08a')
R_ZOMBI = rampa('1a3a24', '2a5a34', '3e7a48', '5e9e64', '9ad09a')
R_HUESO = rampa('5a5444', '8a8470', 'bab4a0', 'e2dcc8', 'faf6ea')
R_PIEDRA = rampa('2a2a30', '46464e', '6a6a74', '94949e', 'c8c8d0')
R_MORADO = rampa('2a0a4a', '5a1aa0', '8a3ae0', 'c080ff', 'f0d8ff')
R_ENDER = rampa('0a0a10', '14141e', '22222e', '34343e', '4a4a56')
R_MADERA = rampa('3a240e', '5e3c18', '8a5a26', 'b47e3c', 'deae66')
R_ORO = ORO
R_HIERRO = rampa('3a3e48', '6a707c', 'a0a6b2', 'd2d6de', 'f6f8fc')
R_TIERRA = rampa('3a2410', '5e3c1c', '86582c', 'ae7a44', 'd6a466')
R_HIERBA = rampa('1a4a10', '2e6e1a', '4a9a26', '74c43a', 'b0ec6a')
R_NOCHE = rampa('0a0a1e', '141432', '22224a', '34346a', '4e4e8e')
R_SCULK = rampa('041014', '08222a', '0e3a46', '18606e', '3ab0c0')
R_GAS = rampa('1a3a10', '3a6a1a', '6aa02a', 'a8d84a', 'e0ff9a')
R_BLANCO = rampa('8a8e9e', 'b8bcca', 'd8dce6', 'eef0f6', 'ffffff')


def nuevo(n):
    x, y, k = malla(n)
    return x, y, k, Lienzo(n)


def capa(n):
    return Lienzo(n)


# ----------------------------------------------------------------------------------------------------------------
#  Las marcas (lo que le pasa a la pieza)
# ----------------------------------------------------------------------------------------------------------------
def tachado(L, x, y):
    """La raya roja que tacha (de arriba a la derecha a abajo a la izquierda)."""
    T = Lienzo(L.a.shape[1])
    raya = sd_segmento(x, y, 26, 6, 6, 26, 2.4)
    T.pintar(raya < 0, H('e8322a')[:3])
    T.pintar((raya < -1.0) & (x + y < 32), H('ff7a60')[:3])
    T.contorno(H('3a0604')[:3])
    L.encima(T)


def flecha(L, x, y, arriba=True, cx=25.0, cy=8.0, color='ffffff'):
    """Una flecha gruesa (arriba o abajo) en la esquina."""
    T = Lienzo(L.a.shape[1])
    s = 1 if arriba else -1
    punta = sd_poligono(x, y, [(cx - 5.5, cy - s * 0.5), (cx + 5.5, cy - s * 0.5), (cx, cy - s * 6.5)])
    palo = sd_caja(x, y, cx, cy + s * 3.0, 2.2, 3.6)
    T.pintar(union(punta, palo) < 0, H(color)[:3])
    T.contorno(OSCURO)
    L.encima(T)


# Las cifras pequeñas (3 x 5) para los ×N.
CIFRAS = {
    'x': ["...", "#.#", ".#.", "#.#", "..."],
    '1': [".#.", "##.", ".#.", ".#.", "###"],
    '2': ["##.", "..#", ".#.", "#..", "###"],
    '3': ["##.", "..#", ".#.", "..#", "##."],
    '4': ["#.#", "#.#", "###", "..#", "..#"],
    '5': ["###", "#..", "##.", "..#", "##."],
    '0': ["###", "#.#", "#.#", "#.#", "###"],
    '%': ["#.#", "..#", ".#.", "#..", "#.#"],
    '+': ["...", ".#.", "###", ".#.", "..."],
    '-': ["...", "...", "###", "...", "..."],
}


def cifras(L, texto, x0, y0, color='ffffff', fondo=None):
    """Un texto pequeño en píxeles (para los ×3, ×10...), con su contorno oscuro. x0, y0 en píxeles del icono."""
    n = L.a.shape[1]
    T = Lienzo(n)
    x = x0
    for c in texto:
        g = CIFRAS[c]
        for fy, fila in enumerate(g):
            for fx, ch in enumerate(fila):
                if ch == '#' and 0 <= y0 + fy < n and 0 <= x + fx < n:
                    T.rgb[y0 + fy, x + fx] = H(color)[:3]
                    T.a[y0 + fy, x + fx] = 1.0
        x += len(g[0]) + 1
    T.contorno(OSCURO if fondo is None else H(fondo)[:3])
    L.encima(T)


def por(L, n_veces, color='ffe08a'):
    """La marca ×N abajo a la derecha."""
    t = 'x' + str(n_veces)
    ancho = len(t) * 4 - 1
    cifras(L, t, 15 - ancho, 10, color)


# ----------------------------------------------------------------------------------------------------------------
#  Las piezas
# ----------------------------------------------------------------------------------------------------------------
def corazon(L, x, y, k, cx=16.0, abajo=28.5, esc=22.5, mitad=False, rampa_=R_ROJO):
    d = sd_corazon(x, y, cx, abajo, esc)
    lleno = (d < 0) & ((x < cx) if mitad else True)
    L.pintar(lleno, tono(rampa_, esfera(x, y, cx - 4, abajo - 15.5, esc * 0.55, esc * 0.55, amb=0.25)))
    if mitad:
        L.pintar((d < 0) & (x >= cx), H('2a1018')[:3])
        L.pintar((d < 0) & (d > -1.6 * k) & (x >= cx), H('5a2a32')[:3])
    L.contorno(H('1a0204')[:3])


def calavera(L, x, y, k, cx=16.0, cy=15.0, esc=1.0, rampa_=R_HUESO, ojos='1a0a0a'):
    craneo = union(sd_circulo(x, y, cx, cy - 1 * esc, 10 * esc), sd_caja(x, y, cx, cy + 7 * esc, 6 * esc, 4.5 * esc, 1.5))
    L.pintar(craneo < 0, tono(rampa_, esfera(x, y, cx - 3 * esc, cy - 5 * esc, 11 * esc, 11 * esc, amb=0.3)))
    for lado in (-1, 1):
        L.pintar(sd_circulo(x, y, cx + lado * 4.3 * esc, cy + 0.5 * esc, 3.0 * esc) < 0, H(ojos)[:3])
    L.pintar(sd_poligono(x, y, [(cx - 1.4 * esc, cy + 6 * esc), (cx + 1.4 * esc, cy + 6 * esc), (cx, cy + 3.5 * esc)]) < 0,
             H(ojos)[:3])
    for i in (-1, 0, 1):
        L.pintar(sd_caja(x, y, cx + i * 2.6 * esc, cy + 10.2 * esc, 0.5 * esc, 1.6 * esc) < 0, H('6a6250')[:3])
    L.contorno(OSCURO)


def llama(L, x, y, k, cx=16.0, base=28.0, alto=24.0, ancho=9.0, rampa_=R_FUEGO):
    """Una llama de tres lenguas."""
    d = union(sd_poligono(x, y, [(cx - ancho, base - 6), (cx - ancho * 0.45, base - alto * 0.62), (cx, base - 6)]),
              sd_poligono(x, y, [(cx - ancho * 0.55, base - 4), (cx, base - alto), (cx + ancho * 0.55, base - 4)]),
              sd_poligono(x, y, [(cx, base - 6), (cx + ancho * 0.5, base - alto * 0.7), (cx + ancho, base - 6)]),
              sd_elipse(x, y, cx, base - 6, ancho, 6))
    L.pintar(d < 0, tono(rampa_, np.clip(0.25 + (base - y) / alto * 0.25 + (d < -2.5) * 0.35 + (d < -5) * 0.25, 0, 1)))
    L.contorno(H('3a0a02')[:3])


def gota(L, x, y, k, cx=16.0, cy=19.0, r=8.0, rampa_=R_AGUA):
    d = union(sd_circulo(x, y, cx, cy, r), sd_poligono(x, y, [(cx - r * 0.86, cy - r * 0.5), (cx + r * 0.86, cy - r * 0.5),
                                                              (cx, cy - r * 2.1)]))
    L.pintar(d < 0, tono(rampa_, esfera(x, y, cx - 2, cy - 2, r, r * 1.3, amb=0.3)))
    L.pintar(sd_circulo(x, y, cx - r * 0.4, cy - r * 0.2, r * 0.25) < 0, H('ffffff')[:3])
    L.contorno(H('041a3a')[:3])


def totem(L, x, y, k, cx=16.0, cy=16.0, esc=1.0):
    cuerpo = union(sd_caja(x, y, cx, cy + 4 * esc, 5.5 * esc, 7.5 * esc, 2.0),
                   sd_circulo(x, y, cx, cy - 6.5 * esc, 5.2 * esc),
                   sd_caja(x, y, cx, cy + 0.5 * esc, 10.5 * esc, 2.4 * esc, 1.2))
    L.pintar(cuerpo < 0, tono(ORO, esfera(x, y, cx - 2, cy - 4, 12, 14, amb=0.3)))
    for lado in (-1, 1):
        L.pintar(sd_circulo(x, y, cx + lado * 2.4 * esc, cy - 6.4 * esc, 1.4 * esc) < 0, H('2fbf6a')[:3])
    L.contorno(H('3a2204')[:3])


def cara_creeper(L, x, y, k, cx=16.0, cy=16.0, lado=12.0, rampa_=R_CREEPER, cargado=False):
    cara = sd_caja(x, y, cx, cy, lado, lado, 1.0)
    manchas = ((np.floor((x - cx) / 4) * 7 + np.floor((y - cy) / 4) * 3) % 5 == 0)
    L.pintar(cara < 0, tono(rampa_, np.clip(0.55 + manchas * 0.25 - (x - cx + y - cy) * 0.012, 0, 1)))
    negro = H('0a1a0a')[:3]
    s = lado / 12.0
    for lado_ in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado_ * 5 * s, cy - 4 * s, 3 * s, 3 * s) < 0, negro)
    boca = union(sd_caja(x, y, cx, cy + 2.5 * s, 2 * s, 3.5 * s), sd_caja(x, y, cx - 3.5 * s, cy + 6 * s, 1.5 * s, 3 * s),
                 sd_caja(x, y, cx + 3.5 * s, cy + 6 * s, 1.5 * s, 3 * s))
    L.pintar(boca < 0, negro)
    if cargado:
        aura = (np.abs(cara - 2.0) < 1.2) & (((x + y) // 3) % 2 == 0)
        L.pintar(aura, H('7ad8ff')[:3])
    L.contorno(OSCURO)


def cara_zombi(L, x, y, k, cx=16.0, cy=16.0, lado=12.0):
    cara = sd_caja(x, y, cx, cy, lado, lado, 1.0)
    L.pintar(cara < 0, tono(R_ZOMBI, np.clip(0.6 - (x - cx + y - cy) * 0.012 + (y > cy + 4) * 0.1, 0, 1)))
    L.pintar(sd_caja(x, y, cx, cy - lado * 0.75, lado, lado * 0.25) < 0, H('3a2a14')[:3])      # el pelo
    s = lado / 12.0
    for lado_ in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado_ * 5 * s, cy - 1 * s, 2.5 * s, 2 * s) < 0, H('0a1a0a')[:3])
    L.pintar(sd_caja(x, y, cx, cy + 6 * s, 4.5 * s, 1.2 * s) < 0, H('1a2a14')[:3])
    L.contorno(OSCURO)


def cara_enderman(L, x, y, k, cx=16.0, cy=16.0, lado=12.0):
    cara = sd_caja(x, y, cx, cy, lado, lado, 1.0)
    L.pintar(cara < 0, tono(R_ENDER, np.clip(0.6 - (x - cx + y - cy) * 0.012, 0, 1)))
    s = lado / 12.0
    for lado_ in (-1, 1):
        ojo = sd_caja(x, y, cx + lado_ * 5.5 * s, cy + 1 * s, 3.2 * s, 1.4 * s)
        L.pintar(ojo < 0, H('e080ff')[:3])
        L.pintar(sd_caja(x, y, cx + lado_ * 4 * s, cy + 1 * s, 1.4 * s, 1.4 * s) < 0, H('ffffff')[:3])
    L.contorno(H('8a3ae0')[:3])


def arana(L, x, y, k, cx=16.0, cy=17.0, esc=1.0, rampa_=R_ENDER, ojos='e8322a'):
    """Una araña vista de frente: el cuerpo, ocho patas en ángulo y los ojos rojos."""
    for lado in (-1, 1):
        for i, (dx, dy) in enumerate(((6, -5), (8, -1), (8, 3), (6, 7))):
            a = (cx + lado * 4 * esc, cy - 1 * esc + i * 1.6 * esc)
            b = (cx + lado * (4 + dx) * esc, cy + (dy - 3) * esc)
            c = (cx + lado * (6 + dx) * esc, cy + (dy + 4) * esc)
            L.pintar(union(sd_segmento(x, y, *a, *b, 1.0 * esc), sd_segmento(x, y, *b, *c, 1.0 * esc)) < 0, rampa_[2])
    cuerpo = union(sd_circulo(x, y, cx, cy - 4 * esc, 5.5 * esc), sd_elipse(x, y, cx, cy + 4 * esc, 7 * esc, 6.5 * esc))
    L.pintar(cuerpo < 0, tono(rampa_, esfera(x, y, cx - 2, cy - 2, 8 * esc, 9 * esc, amb=0.35)))
    for dx in (-2.4, -0.8, 0.8, 2.4):
        L.pintar(sd_circulo(x, y, cx + dx * esc, cy - 5 * esc, 0.9 * esc) < 0, H(ojos)[:3])
    L.contorno(OSCURO)


def perla(L, x, y, k, cx=16.0, cy=16.0, r=9.0):
    d = sd_circulo(x, y, cx, cy, r)
    L.pintar(d < 0, tono(rampa('0a3a32', '13705e', '2fae8e', '7ae8c8', 'd8fff2'), esfera(x, y, cx - 2, cy - 2, r, r, amb=0.2)))
    L.pintar(sd_elipse(x, y, cx, cy, r * 0.35, r * 0.6) < 0, H('06140f')[:3])
    L.contorno(H('041810')[:3])


def manzana(L, x, y, k, cx=16.0, cy=18.0, r=9.0, rampa_=R_ORO):
    d = union(sd_circulo(x, y, cx - r * 0.35, cy, r * 0.82), sd_circulo(x, y, cx + r * 0.35, cy, r * 0.82))
    L.pintar(d < 0, tono(rampa_, esfera(x, y, cx - 3, cy - 3, r, r, amb=0.25)))
    L.pintar(sd_segmento(x, y, cx, cy - r * 0.6, cx + 1.5, cy - r * 1.25, 1.1) < 0, H('5e3c18')[:3])
    L.pintar(sd_elipse(x, y, cx + 4.5, cy - r * 1.05, 3.2, 1.6) < 0, H('3aa040')[:3])
    L.contorno(OSCURO)


def puerta(L, x, y, k, cx=16.0, cy=16.0, rampa_=R_MADERA):
    hoja = sd_caja(x, y, cx, cy, 8, 13, 0.5)
    tabla = ((np.floor((x - cx + 8) / 4)) % 2 == 0)
    L.pintar(hoja < 0, tono(rampa_, np.clip(0.5 + tabla * 0.15 - (y - cy) * 0.008, 0, 1)))
    for vy in (-6, 4):
        L.pintar(sd_caja(x, y, cx, cy + vy, 5, 3) < 0, rampa_[1])
    L.pintar(sd_circulo(x, y, cx + 5, cy + 1, 1.3) < 0, H('f2c64a')[:3])
    L.contorno(OSCURO)


def boton(L, x, y, k, cx=16.0, cy=17.0):
    base_ = sd_caja(x, y, cx, cy + 4, 11, 4, 1.0)
    L.pintar(base_ < 0, tono(R_PIEDRA, bisel(base_, k, 1.6 * k, base=0.5)))
    b = sd_caja(x, y, cx, cy - 1, 6.5, 4, 1.4)
    L.pintar(b < 0, tono(R_ROJO, bisel(b, k, 1.6 * k, base=0.6)))
    L.contorno(OSCURO)


def placa(L, x, y, k, cx=16.0, cy=20.0):
    p = sd_caja(x, y, cx, cy, 12, 3.2, 1.0)
    L.pintar(p < 0, tono(R_PIEDRA, bisel(p, k, 1.6 * k, base=0.62)))
    L.pintar(sd_caja(x, y, cx, cy - 4.5, 12, 1.0) < 0, R_PIEDRA[3])
    L.contorno(OSCURO)


def cactus(L, x, y, k, cx=16.0):
    d = union(sd_caja(x, y, cx, 18, 5, 12, 2), sd_caja(x, y, cx - 8, 14, 2.5, 4.5, 1.5), sd_caja(x, y, cx - 6.5, 18, 4, 2, 1),
              sd_caja(x, y, cx + 8, 11, 2.5, 4.5, 1.5), sd_caja(x, y, cx + 6.5, 15, 4, 2, 1))
    L.pintar(d < 0, tono(R_VERDE, np.clip(0.55 - (x - cx) * 0.03, 0, 1)))
    for (px, py) in ((cx - 2, 10), (cx + 2, 16), (cx - 2, 22), (cx + 2, 27), (cx - 8, 12), (cx + 8, 9)):
        L.pintar(sd_circulo(x, y, px, py, 0.9) < 0, H('f8f4c0')[:3])
    L.contorno(OSCURO)


def bloque(L, x, y, k, rampa_, cx=16.0, cy=17.0, lado=11.0, vetas=None):
    """Un bloque en perspectiva (la cara de arriba más clara)."""
    frente = sd_caja(x, y, cx, cy + 2, lado, lado - 2, 0.5)
    arriba = sd_poligono(x, y, [(cx - lado, cy - lado + 4), (cx - lado + 4, cy - lado), (cx + lado, cy - lado),
                                (cx + lado - 4, cy - lado + 4)])
    L.pintar(frente < 0, tono(rampa_, np.clip(0.45 + (vetas(x, y) if vetas else 0), 0, 1)))
    L.pintar(arriba < 0, tono(rampa_, np.clip(0.75 + (vetas(x, y) if vetas else 0), 0, 1)))
    L.contorno(OSCURO)


def sol(L, x, y, k, cx=16.0, cy=16.0, r=7.0):
    for i in range(8):
        a = math.tau * i / 8
        L.pintar(sd_segmento(x, y, cx + math.cos(a) * (r + 2), cy + math.sin(a) * (r + 2), cx + math.cos(a) * (r + 6),
                             cy + math.sin(a) * (r + 6), 1.4) < 0, H('ffc84a')[:3])
    L.pintar(sd_circulo(x, y, cx, cy, r) < 0, tono(R_FUEGO, esfera(x, y, cx - 2, cy - 2, r, r, amb=0.5)))
    L.contorno(H('5a2a04')[:3])


def luna(L, x, y, k, cx=16.0, cy=16.0, r=10.0, rampa_=R_BLANCO):
    d = np.maximum(sd_circulo(x, y, cx, cy, r), -sd_circulo(x, y, cx + r * 0.55, cy - r * 0.35, r * 0.85))
    L.pintar(d < 0, tono(rampa_, esfera(x, y, cx - 3, cy - 3, r, r, amb=0.35)))
    L.contorno(OSCURO)


def nube(L, x, y, k, cx=16.0, cy=16.0, rampa_=R_GAS, esc=1.0):
    d = union(sd_circulo(x, y, cx - 6 * esc, cy + 2 * esc, 5 * esc), sd_circulo(x, y, cx, cy - 2 * esc, 7 * esc),
              sd_circulo(x, y, cx + 7 * esc, cy + 2 * esc, 5 * esc), sd_caja(x, y, cx, cy + 4 * esc, 10 * esc, 3 * esc, 2))
    L.pintar(d < 0, tono(rampa_, np.clip(0.4 + (cy - y) * 0.04 + (d < -2) * 0.2, 0, 1)))
    L.contorno(OSCURO)


def cama(L, x, y, k, cx=16.0, cy=19.0):
    L.pintar(sd_caja(x, y, cx, cy, 13, 4, 1) < 0, tono(R_ROJO, np.clip(0.55 - (y - cy) * 0.05, 0, 1)))
    L.pintar(sd_caja(x, y, cx - 9, cy - 3, 4, 2.5, 1) < 0, H('f0f0f0')[:3])
    L.pintar(sd_caja(x, y, cx, cy + 5.5, 13, 1.6) < 0, R_MADERA[2])
    for lado in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado * 12, cy + 8, 1.2, 2.5) < 0, R_MADERA[1])
    L.contorno(OSCURO)


def telarana(L, x, y, k, cx=16.0, cy=16.0, r=13.0, color='e8e8f0'):
    m = np.zeros_like(x, bool)
    for i in range(8):
        a = math.tau * i / 8 + 0.2
        m |= sd_segmento(x, y, cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r, 0.55) < 0
    rr = np.hypot(x - cx, y - cy)
    for anillo in (4.5, 8.5, 12.0):
        m |= np.abs(rr - anillo) < 0.55
    m &= rr < r + 0.5
    L.pintar(m, H(color)[:3])


def ojo(L, x, y, k, cx=16.0, cy=16.0, r=9.0, iris=R_MORADO):
    blanco = sd_elipse(x, y, cx, cy, r * 1.35, r * 0.85)
    L.pintar(blanco < 0, tono(R_BLANCO, esfera(x, y, cx - 2, cy - 2, r * 1.4, r, amb=0.5)))
    L.pintar(sd_circulo(x, y, cx, cy, r * 0.62) < 0, tono(iris, esfera(x, y, cx - 1.5, cy - 1.5, r * 0.6, r * 0.6, amb=0.3)))
    L.pintar(sd_elipse(x, y, cx, cy, r * 0.18, r * 0.5) < 0, H('0a0410')[:3])
    L.contorno(OSCURO)


def rayo(L, x, y, k, cx=16.0, cy=16.0, esc=1.0, color='fff27a'):
    d = sd_poligono(x, y, [(cx + 2 * esc, cy - 13 * esc), (cx - 6 * esc, cy + 1 * esc), (cx - 0.5 * esc, cy + 1 * esc),
                           (cx - 3 * esc, cy + 13 * esc), (cx + 6 * esc, cy - 2 * esc), (cx + 0.5 * esc, cy - 2 * esc)])
    L.pintar(d < 0, H(color)[:3])
    L.pintar(d < -1.2, H('ffffff')[:3])
    L.contorno(H('5a4a04')[:3])


def reloj(L, x, y, k, cx=16.0, cy=16.0, r=11.0):
    d = sd_circulo(x, y, cx, cy, r)
    L.pintar(d < 0, tono(ORO, bisel(d, k, 2.0 * k, base=0.62)))
    L.pintar(sd_circulo(x, y, cx, cy, r - 2.6) < 0, H('fbf3dc')[:3])
    L.pintar(sd_segmento(x, y, cx, cy, cx, cy - r * 0.6, 1.1) < 0, OSCURO)
    L.pintar(sd_segmento(x, y, cx, cy, cx + r * 0.45, cy + r * 0.15, 1.1) < 0, OSCURO)
    L.contorno(OSCURO)


def icono_falta(n=16):
    """El que sale mientras no tiene icono propio: una interrogación de oro sobre laca."""
    x, y, k, L = nuevo(n)
    d = sd_caja(x, y, 16, 16, 13, 13, 4)
    L.pintar(d < 0, mc.LACA[2])
    from ruleta import sd_interrogacion
    L.pintar(sd_interrogacion(x, y, 16, 16, 20, 2.6) < 0, ORO[3])
    L.contorno(OSCURO)
    return L


# ----------------------------------------------------------------------------------------------------------------
#  Los iconos, por su sprite
# ----------------------------------------------------------------------------------------------------------------
ICONOS = {}


def icono(nombre):
    def reg(fn):
        ICONOS[nombre] = fn
        return fn
    return reg


ICONOS['cambio/ni_un_totem_mas'] = mc.icono_totem
ICONOS['cambio/end_sellado'] = mc.icono_end
ICONOS['cambio/portales_arden'] = mc.icono_portal
ICONOS['momento/vida_a_medias'] = mc.icono_vida

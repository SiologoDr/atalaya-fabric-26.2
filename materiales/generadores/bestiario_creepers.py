"""
Los creepers del bestiario (18-10-2026, quinta vuelta). Juan, al verlos en el juego: «mejora la anatomía de los
creepers, y las texturas que se vean suaves; el creeper césped debe ser más chiquito y otro diseño, el creeper pastel
debe ser como un creeper normal, sus pies son muy chicos; los otros diseños de creeper son raros».

  la anatomía     la del creeper de vanilla, al doble: la cabeza de 16, el cuerpo de 16 x 24 x 8 y cuatro patas de
                  8 x 12 x 8, delante y detrás (no columnas de cajas iguales)
  lo suave        las texturas con el tono que corre seguido por la rampa, más claro arriba, con manchas grandes y
                  blandas (bestiario_limpio.suave16 y compañía), no motas de dos píxeles
  la cara         la de creeper, honda (los agujeros de verdad), y la máscara pintada con la misma luz que la cabeza

Antes (y rechazado): la cuarta vuelta tenía columnas de cajas iguales y texturas de motas; la segunda, la misma cara
de monstruo con quijada y dientes en todos («no como otra cosa»).

Uso: python bestiario_creepers.py <raíz> [carpeta de la ficha] [ids]
"""
import math
import os
import random
import sys

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario_limpio import rampa

CELDAS = L._CELDAS


# ======================================================================================================================
#  Las paletas y los pinceles de siempre, y lo de terminar (el huevo, el retrato, las partículas)
# ======================================================================================================================
LADOS = ((1, 'i'), (-1, 'd'))
PATAS = ('pata_di', 'pata_dd', 'pata_ti', 'pata_td')
AMARILLO = rampa('6a4a04', 'a8780a', 'd8a816', 'f2c62a', 'ffe478')
NEGRO_H = rampa('0a0a0c', '141418', '1e1e24', '2a2a32', '3a3a44')
ROJO = rampa('5a0606', '8a0c0c', 'd02020', 'ff5a40', 'ffd0b0')
VERDE = rampa('0a3a06', '1a6a0e', '3ac81a', '9aff5a', 'eaffd0')
ACERO = rampa('3a3e44', '5a6068', '8a929c', 'b8c0c8', 'e6eaee')
HUECO_V = rampa('020a02', '061206', '0a1a0a', '0e240e', '123012')
CIAN = rampa('06404a', '0a8a9a', '3ad8ff', 'aef6ff', 'f0ffff')
HUESO_S = rampa('2a3a3c', '4a6064', '7a9294', 'a8bebe', 'd2e2e0')
HUECO_C = rampa('010406', '020a0e', '041216', '061a20', '08222a')
NATA = rampa('b8a898', 'd8ccc0', 'ece4da', 'f8f2ea', 'ffffff')
MERMELADA = rampa('3a0408', '6a0a12', 'c0202e', 'ff5a5a', 'ffc0b0')
FUEGO = rampa('a04a04', 'e08a0a', 'ffc82a', 'fff08a', 'ffffff')
VELA = rampa('1a4a10', '2e7a1a', '4aa82a', '7ad04a', 'b0f080')
HUECO_T = rampa('140604', '200a06', '2c0e08', '3a120a', '48160c')
BRIZNA = rampa('12320a', '22521a', '3a7a24', '5aa232', '9ad25a')
HUECO_P = rampa('020802', '041004', '061806', '0a200a', '0e2a0e')
MAGMA = rampa('5a0c02', 'a82a06', 'e8640a', 'ffa82a', 'fff0a0')
HUECO_M = rampa('1a0402', '2a0804', '3a0c04', '4a1206', '5a1808')
LAVA = rampa('c8400a', 'ff8a1a', 'ffc23a', 'fff0a0', 'ffffff')
HUECO_W = rampa('020204', '06060a', '0a0a10', '0e0e16', '12121c')
HOJA_W = rampa('0a0e06', '141a0c', '1e2812', '2a3618', '3a4822')
ESPINA = rampa('1a0608', '3a0c10', '62161c', '8a2a2e', 'b04a48')
HUECO_E = rampa('0a0604', '120a06', '1a0e08', '22140a', '2a180c')
HUECO_G = rampa('010806', '02100c', '041812', '062018', '08281e')
HUESO_L = rampa('5a4a3a', '8a7a62', 'b8a888', 'dcd0b0', 'f4ecd8')
HUECO_L = rampa('120204', '200408', '2e060c', '3c0a10', '4a0e14')
CORAZON = rampa('4a0408', '8a0a14', 'd01a2a', 'ff4a5a', 'ffb0b0')
HUECO_A = rampa('0e0612', '180a1e', '220e2a', '2c1236', '361642')
VIDRIO = rampa('0a2a0a', '10461a', '1e7a2a', '3ac84a', 'c8ffc0')


def terminar(m, raiz, nombre_es, nombre_en, huevo, retrato, particulas=()):
    m.exportar(raiz)
    piel, contorno, dib = huevo
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    ojo, obj = retrato
    B.retrato(m, ojo=ojo, objetivo=obj, fov=34)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


def chispa(color, n=8):
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            d = np.hypot(x - 0.5, y - 0.5)
            centro = d < 0.16
            return (np.where(centro, 255, color[0]), np.where(centro, 240, color[1]), np.where(centro, 210, color[2]),
                    (d < 0.42 - k * 0.1) * 255)
        cuadros.append(B.sprite(n, f))
    return cuadros


def esquirla(color, n=8):
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            a = (np.abs(x - 0.5) + np.abs(y - 0.5) * (0.7 + 0.3 * k) < 0.38) * 255
            sombra = (x + y > 1.05)
            return (np.where(sombra, color[0] * 0.6, color[0]), np.where(sombra, color[1] * 0.6, color[1]),
                    np.where(sombra, color[2] * 0.6, color[2]), a)
        cuadros.append(B.sprite(n, f))
    return cuadros


def chapa16(r, r_sucio):
    """La chapa pintada del bidón: amarilla y moteada, con la pintura saltada en los cantos (asoma el hierro) y
    chorretones de suciedad que bajan de los remaches."""
    base = L.piel16(r, base=2, claro=0.12, oscuro=0.16)

    def fn(tw, th, cara, s):
        tex, _ = base(tw, th, cara, s)
        xs, ys = L._malla(tw, th)
        borde = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        a = L._azar(xs + 3, ys + 1, s + 11)
        saltado = (borde < 1) & (a < 0.45) | (borde == 1) & (a < 0.12)
        tex[saltado] = L._img(np.full((th, tw), 2), r_sucio)[saltado]
        if cara not in ('arriba', 'abajo'):
            chorro = ((xs % 7) == 3) & (ys >= 1) & (ys < 1 + ((xs * 5 + s) % 4)) & (borde >= 1)
            tex[chorro] = L._img(np.full((th, tw), 1), r)[chorro]
        return tex, None
    return fn


def almas16(r_luz, r_alma):
    """Lo de dentro de la jaula del pecho, como el warden: la luz de cian, más fuerte en el centro, y las caras de las
    almas (dos ojos y la boca en o, oscuros) que asoman."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        tex = L._img(np.clip(1 + d, 1, 4), r_luz)
        for (cx, cy) in ((0.3, 0.32), (0.7, 0.42), (0.42, 0.74)):
            x0, y0 = int(round(cx * tw)) - 2, int(round(cy * th)) - 2
            for (dx, dy) in ((0, 0), (3, 0), (1, 2), (2, 2), (1, 3), (2, 3)):
                x, y = x0 + dx, y0 + dy
                if 0 <= x < tw and 0 <= y < th:
                    tex[y, x, :3] = r_alma[1]
        return tex, tex.copy()
    return fn


def eje_de(rot):
    """Hacia dónde apunta el eje Y de una caja con ese giro (grados, el orden de ModelPart)."""
    return B.girar(rot)[:3, :3] @ np.array((0.0, 1.0, 0.0))


def gota(color, n=8):
    """Una gota (cae): redonda abajo y en punta arriba, con su brillo."""
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            d = np.hypot((x - 0.5) * (1.0 + 0.6 * np.clip(0.55 - y, 0, 1) * 4), y - 0.6)
            dentro = (d < 0.3 - 0.04 * k) | ((np.abs(x - 0.5) < 0.12 * (y - 0.15) * 3) & (y > 0.15) & (y < 0.6))
            brillo = np.hypot(x - 0.42, y - 0.55) < 0.08
            return (np.where(brillo, 255, color[0]), np.where(brillo, 250, color[1]), np.where(brillo, 230, color[2]),
                    dentro * 255)
        cuadros.append(B.sprite(n, f))
    return cuadros


def anillo(color, n=8):
    """Un anillo que se abre (una onda, una burbuja, una vibración)."""
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            d = np.hypot(x - 0.5, y - 0.5)
            r = 0.18 + 0.1 * k
            aro = np.abs(d - r) < 0.07
            brillo = aro & (x < 0.5) & (y < 0.5)
            return (np.where(brillo, 255, color[0]), np.where(brillo, 255, color[1]), np.where(brillo, 255, color[2]),
                    aro * 255)
        cuadros.append(B.sprite(n, f))
    return cuadros


def hojita(color, n=8):
    """Una hoja (o un pétalo, o una brizna) que cae dando vueltas: en almendra, con el nervio, en tres giros."""
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            a = (k - 1) * 0.6
            u = (x - 0.5) * math.cos(a) - (y - 0.5) * math.sin(a)
            v = (x - 0.5) * math.sin(a) + (y - 0.5) * math.cos(a)
            dentro = (np.abs(u) < 0.2 * np.sqrt(np.clip(1 - (v / 0.42) ** 2, 0, 1)))
            nervio = np.abs(u) < 0.04
            return (np.where(nervio, color[0] * 0.7, color[0]), np.where(nervio, color[1] * 0.7, color[1]),
                    np.where(nervio, color[2] * 0.7, color[2]), dentro * 255)
        cuadros.append(B.sprite(n, f))
    return cuadros


def huevo_creeper(px, filas, c, piel, ojo, motas=(), boca=None):
    """El dibujo del huevo: la piel del mob, la cara de creeper con los ojos encendidos y la boca, y sus motas (las
    señas: (x, y, color))."""
    for f in range(2, 15):
        a, b = filas[f]
        for x in range(a + 1, b):
            px[x, f] = c(piel)
    for f in (6, 7):
        for x in (5, 6, 9, 10):
            px[x, f] = c(ojo)
    for f, xs in ((9, (7, 8)), (10, (6, 7, 8, 9)), (11, (6, 9))):
        for x in xs:
            px[x, f] = c(boca or '0a0a0a')
    for x, y, col in motas:
        px[x, y] = c(col)


def fondo_hueco16(r, neon=None, pupila=None, sin_ojos=False, filas=(0, 8)):
    """Lo de dentro de los agujeros de la cara (la cara de delante de la cabeza retranqueada): oscuro, con la sombra en
    el canto de arriba; con 'neon', encendido (más claro hacia el centro de cada agujero); con 'pupila', un punto
    encendido abajo en cada ojo (el de vanilla, que mira desde el fondo)."""
    nc = L.H(neon) if neon else None
    pc = L.H(pupila) if pupila else None

    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        tex = L._img(np.full((th, tw), 1), r)
        if cara != 'frente':
            return tex, None
        f0, f1 = filas
        ci = np.minimum(7, (xs * 8) // tw)
        cj = f0 + np.minimum(f1 - f0 - 1, (ys * (f1 - f0)) // th)
        hueco = CELDAS[cj, ci].copy()
        if sin_ojos:
            hueco &= ~((cj == 2) | (cj == 3))
        # La distancia (en píxeles) al canto de cada agujero: 1 en el canto, 2 dentro... (se va comiendo el borde).
        d = np.zeros((th, tw), int)
        m = np.pad(hueco, 1, constant_values=False)
        while m.any():
            d += m[1:-1, 1:-1]
            m = m & ~L._borde_de(~m)
        # La sombra: la fila de arriba de cada agujero (la tapa el canto de la máscara).
        sombra = hueco & ~np.roll(hueco, 1, 0)
        tex[hueco] = L._img(np.full((th, tw), 0), r)[hueco]
        emis = None
        if nc is not None:
            luz = np.where(d >= 2, 1.0, 0.62)[..., None] * nc
            luz = np.where((d >= 3)[..., None], np.minimum(255, nc * 0.4 + 165), luz)
            if tw <= 8:
                # Al píxel de Minecraft (cada celda, un píxel): el agujero encendido entero y la fila de arriba, la
                # sombra del canto, algo más apagada.
                luz = np.broadcast_to(np.minimum(255, nc * 1.08), luz.shape)
            tex[hueco, :3] = luz[hueco]
            tex[sombra, :3] = nc * (0.62 if tw <= 8 else 0.38)
            emis = np.zeros_like(tex)
            emis[hueco] = tex[hueco]
        if pc is not None:
            ojo = hueco & ((cj == 2) | (cj == 3))
            x0 = np.where(ci < 4, np.round(1 * tw / 8), np.round(5 * tw / 8))
            x1 = np.where(ci < 4, np.round(3 * tw / 8), np.round(7 * tw / 8))
            dentro = np.where(ci < 4, x1 - 1 - xs, xs - x0)          # 0 en el canto de dentro (hacia la nariz)
            y1 = np.round((4 - f0) * th / (f1 - f0))
            punto = ojo & (dentro <= 1) & (dentro >= 0) & (ys == y1 - 2)
            if tw <= 8:
                # Al píxel de Minecraft: un píxel abajo, por dentro (hacia la nariz).
                punto = ojo & (dentro == 0) & (ys == y1 - 1)
            tex[punto, :3] = pc
            emis = np.zeros_like(tex) if emis is None else emis
            emis[punto] = tex[punto]
        return tex, emis
    return fn


def patas(m, padre, x, z, ancho, alto, pint, fondo=None, caras=None):
    """Las cuatro patas cortas (delante y detrás, a cada lado), como las del de vanilla."""
    for (fz, nz) in ((1, 'd'), (-1, 't')):
        for lado, ld in LADOS:
            n = m.parte(f'pata_{nz}{ld}', padre, (lado * x, alto, fz * z))
            m.caja_desde(n, (lado * x, 0, fz * z), (ancho, alto, fondo or ancho), pint, caras=caras)


def ventana16(r_marco, r_luz):
    """La mirilla del bidón: el marco negro con sus tornillos y, dentro, el líquido verde encendido con las burbujas."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        tex = L._img(np.full((th, tw), 2), r_marco)
        if cara != 'frente':
            return tex, None
        borde = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        dentro = borde >= 1
        nivel = ys >= th * 0.22
        luz = dentro & nivel
        tex[dentro & ~nivel] = L._img(np.full((th, tw), 1), r_luz)[dentro & ~nivel]
        tex[luz] = L._img(np.where(xs == 1, 4, 3), r_luz)[luz]
        burbuja = luz & (((xs * 3 + ys * 5 + s) % 11) == 0)
        tex[burbuja] = L._img(np.full((th, tw), 4), r_luz)[burbuja]
        tornillo = (borde == 0) & (((xs == 0) | (xs == tw - 1)) & ((ys == 1) | (ys == th - 2)))
        tex[tornillo] = L._img(np.full((th, tw), 4), r_marco)[tornillo]
        emis = np.zeros_like(tex)
        emis[luz] = tex[luz]
        return tex, emis
    return fn


def oreja16(r, rl):
    """La cara de la oreja del warden: el sculk oscuro con el canto, y dentro, la luz de cian (más fuerte en el medio)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        tex = L._img(np.where(d == 0, 0, 2), r)
        luz = d >= 1
        tex[luz] = L._img(np.clip(d + 1, 1, 4), rl)[luz]
        emis = np.zeros_like(tex)
        emis[luz] = tex[luz]
        return tex, emis
    return fn


def orejas_warden(m, padre, y_base, piel, luz, x0=5.4):
    """Las orejas del warden (sus zarcillos), en grande: dos palas anchas y planas que salen de lo alto de los lados de la
    cabeza, se abren hacia fuera, suben y se curvan un poco hacia atrás; por delante, la luz de cian que late (como las
    del warden). No ramas de ciervo."""
    cara = L.grueso('oreja_ciego', oreja16(SCULK, CIAN))
    for lado, ld in LADOS:
        n = m.parte(f'oreja_{ld}', padre, (lado * x0, y_base, 0.0))
        p = [np.array((lado * x0, y_base - 1.2, 0.0))]
        for (dx, dy, dz) in ((5.2, 3.2, 0.0), (3.6, 5.6, -0.6), (1.2, 5.4, -1.4)):
            p.append(p[-1] + np.array((lado * dx, dy, dz)))
        for k, (ancho, grueso) in enumerate(((6.4, 2.2), (5.2, 1.9), (3.6, 1.6))):
            m.viga(n, p[k], p[k + 1], grueso, piel, ancho=ancho, caras={'frente': cara, 'atras': cara}, extra=0.9)
        # La punta, algo más clara: un remate encendido.
        m.viga(n, p[3], p[3] + np.array((lado * 0.2, 1.6, -0.4)), 1.4, luz, ancho=2.2, extra=0.2)


def sensor(m, parte, centro, luz, borde, tam=2.6):
    """Una mancha de sculk que brilla (como las del warden): el centro encendido en su cerco oscuro, un poco en relieve."""
    x, y, z, cara = centro
    if cara == 'frente':
        m.caja(parte, (x, y, z + 0.1), (tam + 1.0, tam + 1.0, 0.2), borde)
        m.caja(parte, (x, y, z + 0.25), (tam, tam, 0.3), luz)
    else:
        sg = 1 if cara == 'der' else -1
        m.caja(parte, (x + sg * 0.1, y, z), (0.2, tam + 1.0, tam + 1.0), borde)
        m.caja(parte, (x + sg * 0.25, y, z), (0.3, tam, tam), luz)


# ======================================================================================================================
#  La base: el creeper de vanilla al doble, con la cara honda y la piel suave
# ======================================================================================================================
def cara_honda(m, parte, y0, Lc, piel_franja, pared, z_cara, prof=2.0, sin_ojos=False, filas=(0, 8)):
    """La máscara de la cara de creeper delante de la cabeza retranqueada, en tiras (las filas iguales, juntas); cada tira
    con la piel de su altura ('piel_franja(f0, f1)', la parte del alto de la cabeza que ocupa), para que la luz de la cara
    corra seguida. Por dentro de los agujeros, 'pared'."""
    c = Lc / 8.0
    f0_, f1_ = filas
    tiras_de = []
    for j in range(8):
        llenas = ~CELDAS[j].copy()
        if sin_ojos and j in (2, 3):
            llenas[:] = llenas | CELDAS[j]
        tiras, i = [], 0
        while i < 8:
            if llenas[i]:
                k = i
                while k < 8 and llenas[k]:
                    k += 1
                tiras.append((i, k))
                i = k
            else:
                i += 1
        tiras_de.append(tuple(tiras))
    j = f0_
    while j < f1_:
        k = j
        while k + 1 < f1_ and tiras_de[k + 1] == tiras_de[j]:
            k += 1
        piel = piel_franja(j / 8.0, (k + 1) / 8.0)
        for (i0, i1) in tiras_de[j]:
            x0, x1 = -Lc / 2 + i0 * c, -Lc / 2 + i1 * c
            ya, yb = y0 + Lc - (k + 1) * c, y0 + Lc - j * c
            caras = {'frente': piel, 'atras': None,
                     'izq': piel if i0 == 0 else pared, 'der': piel if i1 == 8 else pared,
                     'arriba': piel if j == f0_ else pared, 'abajo': piel if k == f1_ - 1 else pared}
            m.caja(parte, ((x0 + x1) / 2, (ya + yb) / 2, z_cara - prof / 2), (x1 - x0, yb - ya, prof), None,
                   caras=caras)
        j = k + 1


def cabeza(m, nombre, padre, y0, piel16, hueco_r, neon=None, pupila=None, Lc=16.0, prof=2.0, sin_ojos=False,
           caras=None, cara16=None):
    """La cabeza de creeper: el cubo de Lc retranqueado 'prof' por delante, con la cara honda. 'piel16(franja)' da la piel
    (de 16 por bloque) de una franja del alto de la cabeza; 'cara16', la de la máscara de la cara, si es otra (sin grietas
    que la ensucien). Devuelve lo alto de la cabeza."""
    m.parte('cabeza', padre, (0, y0, 0))
    piel = L.grueso(f'cabeza_{nombre}', piel16((0.0, 1.0)))
    fondo = L.grueso(f'hueco_{nombre}', fondo_hueco16(hueco_r, neon, pupila, sin_ojos))
    cc = {'frente': fondo}
    cc.update(caras or {})
    m.caja_desde('cabeza', (0, y0, -prof / 2), (Lc, Lc, Lc - prof), piel, caras=cc)
    pared = L.liso(f'pared_{nombre}', hueco_r, base=1)

    def franja(f0, f1):
        return L.grueso(f'cara_{nombre}_{int(round(f0 * 8))}{int(round(f1 * 8))}', (cara16 or piel16)((f0, f1)))
    cara_honda(m, 'cabeza', y0, Lc, franja, pared, Lc / 2, prof, sin_ojos)
    return y0 + Lc


def cuerpo(m, piel_cuerpo, piel_pata, alto_pata=12.0, alto=24.0, fondo=8.0, ancho=16.0, x=4.0, z=8.0, pata=8.0,
           caras_cuerpo=None):
    """El cuerpo del creeper de vanilla (al doble) y sus cuatro patas, delante y detrás. Devuelve dónde va la cabeza."""
    m.parte('cuerpo', None, (0, alto_pata, 0))
    patas(m, 'cuerpo', x, z, pata, alto_pata, piel_pata)
    m.caja_desde('cuerpo', (0, alto_pata, 0), (ancho, alto, fondo), piel_cuerpo, caras=caras_cuerpo)
    return alto_pata + alto


def anims(m, extra_siempre=None, extra_hinchado=None, paso=1.0, amp=34):
    """Las de todos, con más vida que las de vanilla: al andar, las patas en diagonal, el cuerpo que sube y baja y se
    mece, y la cabeza que lo compensa; quieto, respira y mira alrededor; la mecha (tiembla; el render lo hincha y lo hace
    parpadear) y la muerte (se derrumba)."""
    a = m.anim('andar', paso, bucle=True)
    di, dd, ti, td = PATAS
    a.onda(di, 'r', 0, amp)
    a.onda(td, 'r', 0, amp)
    a.onda(dd, 'r', 0, amp, fase=0.5)
    a.onda(ti, 'r', 0, amp, fase=0.5)
    a.onda('cuerpo', 'm', 1, 0.5, periodo=paso / 2, fase=0.25)
    a.onda('cuerpo', 'r', 2, 2.5, periodo=paso)
    a.onda('cabeza', 'r', 2, -2.0, periodo=paso)
    a.onda('cabeza', 'r', 1, 3.0, periodo=paso, fase=0.25)
    s = m.anim('siempre', 3.0, bucle=True)
    s.onda('cuerpo', 'e', 1, 0.012, base=1.0, periodo=3.0)
    if extra_siempre:
        extra_siempre(s)
    r = m.anim('reposo', 4.0, bucle=True)
    r.onda('cabeza', 'r', 1, 8, periodo=4.0)
    r.onda('cabeza', 'r', 0, 2.5, periodo=2.0, fase=0.2)
    r.onda('cuerpo', 'r', 2, 1.0, periodo=4.0, fase=0.4)
    h = m.anim('hinchado', 1.0)
    h.rot('cabeza', [(0, 0, 0, 0), (0.25, 3, 0, 2), (0.5, -2, 0, -2), (0.75, 3, 0, 2), (1.0, -3, 0, -3)])
    if extra_hinchado:
        extra_hinchado(h)
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.25, 8, 0, 4), (0.7, 70, 0, 12), (1.0, 88, 0, 14)])
    d.mov('cuerpo', [(0, 0, 0, 0), (0.7, 0, -2, 2), (1.0, 0, -4, 3)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.4, 18, 10, 0), (1.0, 28, 18, -10)])
    for n in PATAS:
        d.rot(n, [(0, 0, 0, 0), (0.6, -40, 0, 0), (1.0, -70, 0, 0)])


def glaseado16(r, r_punto=None, gotas=(2, 5)):
    """El glaseado: por arriba entero (con sus puntitos, si se piden) y por los lados, gotas de largos distintos (lo de
    fuera, transparente)."""
    g0, g1 = gotas

    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        if cara in ('arriba', 'abajo'):
            tex = L._rgba(L.color_continuo(r, L.tono_suave(tw, th, cara, s, 3.0, 0.6, 0.12, 6.0)))
            if r_punto is not None:
                punto = (((xs // 3) * 5 + (ys // 3) * 7 + s) % 5 == 0) & ((xs % 3) == 1) & ((ys % 3) == 1)
                tex[punto, :3] = r_punto[2]
            return tex, None
        largo = g0 + ((xs * 5 + s) % 3) + (((xs // 3) * 7 + s) % 2) * (g1 - g0 - 2)
        v = 3.4 - ys / max(1, th) * 1.2
        tex = L._rgba(L.color_continuo(r, v))
        fuera = ys >= largo
        tex[..., 3] = np.where(fuera, 0, 255)
        punta = (ys == largo - 1) & ~fuera
        tex[punta, :3] = r[2]
        return tex, None
    return fn


# ======================================================================================================================
#  El Atómico (Creeper Nuclear): el creeper-bidón, que gustó tal cual
# ======================================================================================================================
def atomico(raiz):
    m = B.Modelo('atomico', K=2, ancho=128)
    m.escala = 0.75
    fondo = chapa16(AMARILLO, NEGRO_H)
    chapa = L.grueso('chapa_atomico', fondo)
    zuncho = L.metal('zuncho_atomico', NEGRO_H, paso=4)
    rayas = L.rayas('peligro_atomico', AMARILLO, NEGRO_H, ancho=4, gastado=0.08, r_gastado=NEGRO_H)
    verde = L.luz('barra_atomico', VERDE)
    vaina = L.metal('vaina_atomico', ACERO, paso=3)
    y_pata, y_c1, y_cab = 8.0, 24.0, 26.0
    m.parte('cuerpo', None, (0, y_pata, 0))
    # Las patas: cortas, de hierro negro, con el pie de rayas de peligro (como las del original).
    patas(m, 'cuerpo', 4.0, 6.0, 8.0, y_pata, zuncho)
    for p in PATAS:
        pz = 6.0 if p[5] == 'd' else -6.0
        px = 4.0 if p[6] == 'i' else -4.0
        m.caja_desde(p, (px, -0.01, pz), (8.6, 2.8, 8.6), rayas)
    # El cuerpo: el bidón rechoncho (de chapa amarilla pintada, con la pintura saltada), con sus zunchos remachados, la
    # franja de rayas de peligro y la mirilla con el líquido verde encendido. (El trébol, tan chico, parecía otra cara.)
    m.caja_desde('cuerpo', (0, y_pata, 0), (16.0, y_c1 - y_pata, 14.0), chapa)
    m.caja_desde('cuerpo', (0, y_pata + 2.4, 0), (16.3, 4.6, 14.3), rayas)
    for y in (y_pata, y_c1 - 2.4):
        m.caja_desde('cuerpo', (0, y, 0), (17.0, 2.4, 15.0), zuncho)
    m.caja('cuerpo', (0, y_pata + 10.6, 7.15), (5.0, 6.0, 0.6), L.grueso('mirilla_atomico', ventana16(NEGRO_H, VIDRIO)))
    # En la espalda, tres barras de combustible encendidas en su vaina de acero: la del medio, corta; las de los lados,
    # largas y abiertas, asoman a los lados de la cabeza y la enmarcan (lo grande, como las espadas del Blaze).
    for k, x in enumerate((-6.2, 0.0, 6.2)):
        alto = 13.0 if k == 1 else 26.0
        base = np.array((x, y_pata + 3.0, -8.4))
        rot = (-6, 0, -x * 2.2)
        e = eje_de(rot)
        m.caja_desde('cuerpo', tuple(base), (3.2, alto, 3.2), verde, rot=rot)
        for f, a in ((0.08, 2.4), (0.55, 1.2), (0.97, 2.2)):
            m.caja('cuerpo', tuple(base + e * alto * f), (4.2, a, 4.2), vaina, rot=rot)
    # El cuello: el zuncho gordo entre el bidón y la cabeza.
    m.caja_desde('cuerpo', (0, y_c1, 0), (15.0, y_cab - y_c1, 13.0), zuncho)
    # La cabeza: la tapa del bidón, con la cara de creeper honda y encendida de verde por dentro (lo radiactivo).
    y1 = cabeza(m, 'atomico', 'cuerpo', y_cab, lambda fr: fondo, HUECO_V, neon='9aff5a',
                cara16=lambda fr: L.suave16(AMARILLO, base=2.4, luz=0.6, ruido=0.15, franja=fr))
    m.caja_desde('cabeza', (0, y1 - 2.4, 0), (17.0, 2.4, 17.0), zuncho)
    m.caja_desde('cabeza', (0, y_cab, 0), (17.0, 1.6, 17.0), zuncho)
    # El botón rojo del original, hecho sirena (su mecha es una sirena): la base remachada, la cúpula roja encendida con
    # el foco que gira dentro, y su jaula.
    rojo = L.luz('cupula_atomico', ROJO)
    jaula = L.metal('jaula_atomico', NEGRO_H, paso=3, remaches=False)
    m.caja_desde('cabeza', (0, y1, 0), (10.0, 1.6, 10.0), L.metal('base_detonador', NEGRO_H, paso=3))
    m.parte('sirena', 'cabeza', (0, y1 + 1.6, 0))
    m.caja_desde('sirena', (0, y1 + 1.6, 0), (7.0, 3.6, 7.0), rojo)
    m.caja_desde('sirena', (0, y1 + 5.2, 0), (4.6, 1.4, 4.6), rojo)
    m.caja('sirena', (0, y1 + 3.6, 3.6), (2.6, 2.6, 0.4), L.luz('foco_atomico', rampa('d02020', 'ff5a40', 'ffb090',
                                                                                      'ffe8d8', 'ffffff')))
    for dx in (-4.2, 4.2):
        for dz in (-4.2, 4.2):
            m.caja_desde('cabeza', (dx, y1 + 1.6, dz), (1.0, 5.8, 1.0), jaula)
    for dz in (-4.2, 4.2):
        m.caja('cabeza', (0, y1 + 7.8, dz), (9.4, 1.0, 1.0), jaula)
        m.caja('cabeza', (dz, y1 + 7.8, 0), (1.0, 1.0, 7.4), jaula)

    def extra(s):
        s.rot('sirena', [(0, 0, 0, 0, 0), (3.0, 0, 360, 0, 0)])

    def mecha(h):
        # La sirena se dispara: gira deprisa y late.
        h.rot('sirena', [(0, 0, 0, 0, 0), (1.0, 0, 1440, 0, 0)])
        h.esc('sirena', [(0, 1, 1, 1), (0.25, 1.2, 1.2, 1.2), (0.5, 1, 1, 1), (0.75, 1.2, 1.2, 1.2),
                         (1.0, 1.3, 1.3, 1.3)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    m.mirar(('cabeza', 0.6))
    m.paso = 2.4

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, 'd8a816', '9aff5a', boca='3ac81a',
                         motas=tuple((x, f, '1e1e24') for f in (4, 13) for x in range(3, 13)) + ((7, 2, 'd02020'),
                                                                                                (8, 2, 'd02020')))
    return terminar(m, raiz, 'Creeper Atómico', 'Atomic Creeper',
                       (('ffe478', 'f2c62a', 'd8a816'), ('3a3a44', '0a0a0c'), dib),
                       ((1.6, 2.2, 2.4), (0, 1.25, 0)),
                       particulas=(('radiacion', chispa((154, 255, 90))), ('chapa', esquirla((216, 168, 22)))))


# ======================================================================================================================
#  La Tarta (Creeper Cake): un creeper normal de tarta
# ======================================================================================================================
CHOCO = rampa('2e1408', '462010', '5e2e16', '7a3e1e', '98542a')
BIZCOCHO = rampa('6a4020', '86562c', 'a26e3a', 'bc864c', 'd4a062')


def pastel16(franja):
    """Los lados de la tarta: el bizcocho suave con su capa de nata de través por la mitad."""
    base = L.suave16(BIZCOCHO, base=2.2, luz=0.6, ruido=0.18, franja=franja)

    def fn(tw, th, cara, s):
        tex, _ = base(tw, th, cara, s)
        if cara in ('arriba', 'abajo'):
            return tex, None
        xs, ys = L._malla(tw, th)
        f0, f1 = franja
        t = f0 + (ys + 0.5) / th * (f1 - f0)
        capa = (t > 0.47) & (t < 0.56)
        tex[capa, :3] = L.color_continuo(NATA, np.full(capa.sum(), 3.0))
        sombra = (t >= 0.56) & (t < 0.6)
        tex[sombra, :3] = tex[sombra, :3] * 0.78
        return tex, None
    return fn


def tarta(raiz):
    m = B.Modelo('tarta', K=2, ancho=128)
    m.escala = 0.55
    choco = L.suave('choco_tarta', CHOCO, base=2.0, luz=0.8, ruido=0.2)
    y_cab = cuerpo(m, choco, choco)
    # Un cuello de glaseado que gotea por el pecho.
    m.caja_desde('cuerpo', (0, y_cab - 3.0, 0), (16.6, 3.0, 8.6), L.grueso('glaseado_cuerpo_tarta', glaseado16(NATA)))
    y1 = cabeza(m, 'tarta', 'cuerpo', y_cab, pastel16, HUECO_T, neon='d02838')
    # El glaseado de arriba (con los puntitos rojos del original), que gotea por los cantos.
    m.caja_desde('cabeza', (0, y1 - 3.2, 0), (17.0, 3.8, 17.0), L.grueso('glaseado_tarta', glaseado16(NATA, MERMELADA)))
    # La vela del original (verde y grande, encendida) y dos cerezas.
    m.parte('vela', 'cabeza', (1.0, y1 + 0.6, -1.0))
    m.caja_desde('vela', (1.0, y1 + 0.6, -1.0), (3.0, 11.0, 3.0), L.rayas('vela_tarta', VELA, NATA, ancho=2))
    m.caja_desde('vela', (1.0, y1 + 11.6, -1.0), (0.5, 1.2, 0.5), L.liso('mecha_tarta', HUECO_T, base=1))
    m.parte('llama', 'vela', (1.0, y1 + 12.4, -1.0))
    for giro in (0, 90):
        m.hoja('llama', (1.0, y1 + 12.4 + 3.0, -1.0), 3.6, 6.0, L.llama('llama_tarta', FUEGO), rot=(0, giro, 0))
    cereza = L.suave('cereza_tarta', MERMELADA, base=2.4, luz=1.2, ruido=0.1)
    for (x, z) in ((-4.6, 3.6), (4.8, 4.4)):
        m.caja('cabeza', (x, y1 + 1.9, z), (2.8, 2.8, 2.8), cereza)
        m.viga('cabeza', (x, y1 + 3.2, z), (x + 0.8, y1 + 5.2, z - 0.6), 0.5,
               L.liso('rabito', rampa('0a2a06', '14400c', '205a12', '2e7418', '3e8e20')))

    def extra(s):
        s.onda('llama', 'e', 1, 0.12, base=1.0, periodo=0.6)
        s.onda('vela', 'r', 2, 3, periodo=1.2)

    def mecha(h):
        h.esc('llama', [(0, 1, 1, 1), (0.5, 1.4, 1.7, 1.4), (1.0, 1.8, 2.4, 1.8)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    ap = m.anim('aparece', 0.8)
    ap.mov('cuerpo', [(0, 0, -6, 0), (0.25, 0, 8, 0), (0.45, 0, 0, 0), (0.55, 0, 1.0, 0), (0.65, 0, 0, 0)])
    ap.esc('cuerpo', [(0, 0.8, 0.8, 0.8), (0.25, 0.95, 1.12, 0.95), (0.45, 1.12, 0.86, 1.12), (0.65, 1, 1, 1)])
    m.mirar(('cabeza', 0.6))
    m.paso = 2.6

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '86562c', 'd02838', boca='2c0e08',
                         motas=tuple((x, f, 'f8f2ea') for f in (2, 3) for x in range(4, 12)) +
                         ((5, 4, 'f8f2ea'), (9, 4, 'f8f2ea'), (6, 2, 'c0202e'), (10, 3, 'c0202e'), (8, 1, '4aa82a')))
    return terminar(m, raiz, 'Creeper Tarta', 'Cake Creeper',
                       (('f8f2ea', 'ece4da', '86562c'), ('462010', '2e1408'), dib),
                       ((1.3, 1.9, 2.0), (0, 1.0, 0)),
                       particulas=(('miga', esquirla((166, 110, 58))), ('nata', esquirla((248, 242, 234)))))


# ======================================================================================================================
#  El Matojo (Creeper de Pasto): un creeper chiquito de hierba
# ======================================================================================================================
HIERBA = rampa('1c4214', '28581c', '347024', '42882c', '56a038')
AMARILLO_F = rampa('8a6a08', 'c8a014', 'f0cc28', 'ffe85a', 'fff8b0')
AMAPOLA = rampa('5a0a0a', '8e1414', 'c82020', 'f04a3a', 'ff9a80')


def hierba16(franja=(0.0, 1.0)):
    """La hierba suave: el verde que corre seguido, con briznas blandas de arriba abajo (más claras arriba)."""
    return L.vetas_suaves16(HIERBA, base=2.0, luz=0.7, paso=1.6, onda=0.5, fuerza=0.35, celda=6.0, franja=franja)


def flor(m, parte, base, rampa_p, alto=4.0):
    """Una flor chica de pradera: el tallo verde y la cabeza (un cubito de pétalos con el centro oscuro arriba)."""
    x, y, z = base
    m.viga(parte, (x, y, z), (x + 0.3, y + alto, z), 0.6, L.liso('tallo_flor_matojo', BRIZNA, base=2))
    m.caja(parte, (x + 0.3, y + alto + 0.9, z), (2.4, 1.8, 2.4), L.suave(f'flor_{rampa_p[2][0]:.0f}_matojo', rampa_p,
                                                                         base=2.6, luz=0.9, ruido=0.1))


def matojo(raiz):
    m = B.Modelo('matojo', K=2, ancho=128)
    m.escala = 0.34
    piel = L.grueso('piel_matojo', hierba16())
    brizna = L.brizna('brizna_matojo', BRIZNA)
    # Chiquito y rechoncho: la cabeza grande, el cuerpo corto y las patas cortas.
    y_cab = cuerpo(m, piel, piel, alto_pata=8.0, alto=12.0, fondo=8.0)
    y1 = cabeza(m, 'matojo', 'cuerpo', y_cab, lambda fr: hierba16(fr), HUECO_P, pupila='d8ff5a')
    # Encima, una matita de hierba con dos flores de pradera (un diente de león y una amapola), y briznas en los pies.
    rng = random.Random(9)
    m.parte('mata', 'cabeza', (0, y1, 0))
    for k in range(11):
        a = k / 11 * math.tau + rng.uniform(-0.2, 0.2)
        r_ = rng.uniform(1.0, 5.5)
        x, z = math.cos(a) * r_, math.sin(a) * r_
        L.colmillo(m, 'mata', (x, y1 - 0.3, z), (math.cos(a) * 0.35, 1.0, math.sin(a) * 0.35), rng.uniform(4.0, 7.0),
                   2.4, brizna, fila=(-math.sin(a), 0, math.cos(a)))
    flor(m, 'mata', (-3.0, y1, 2.0), AMARILLO_F, alto=5.0)
    flor(m, 'mata', (3.4, y1, -1.6), AMAPOLA, alto=4.0)
    for p in PATAS:
        pz = 8.0 if p[5] == 'd' else -8.0
        px = 4.0 if p[6] == 'i' else -4.0
        for k in range(3):
            a = rng.uniform(0, math.tau)
            L.colmillo(m, p, (px + math.cos(a) * 3.4, 0.2, pz + math.sin(a) * 3.4),
                       (math.cos(a) * 0.4, 1.0, math.sin(a) * 0.4), rng.uniform(2.6, 4.0), 2.0, brizna,
                       fila=(-math.sin(a), 0, math.cos(a)))

    def extra(s):
        s.onda('mata', 'r', 2, 6, periodo=1.5)
        s.onda('mata', 'r', 0, 4, periodo=2.0, fase=0.25)

    def mecha(h):
        h.esc('mata', [(0, 1, 1, 1), (0.4, 1.2, 1.3, 1.2), (1.0, 1.4, 1.5, 1.4)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha, paso=0.6, amp=40)
    ap = m.anim('aparece', 0.9)
    ap.mov('cuerpo', [(0, 0, -16, 0), (0.3, 0, 5, 0), (0.5, 0, 0, 0), (0.62, 0, 1.2, 0), (0.75, 0, 0, 0)])
    ap.esc('cuerpo', [(0, 0.5, 0.5, 0.5), (0.3, 0.92, 1.18, 0.92), (0.5, 1.18, 0.82, 1.18), (0.75, 1, 1, 1)])
    m.mirar(('cabeza', 0.6))
    m.paso = 0.9

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '42882c', '0a200a', boca='0a200a',
                         motas=((5, 2, '56a038'), (8, 1, '56a038'), (10, 2, '56a038'), (6, 1, 'f0cc28'), (9, 2, 'c82020'),
                                (6, 6, 'd8ff5a'), (10, 6, 'd8ff5a')))
    return terminar(m, raiz, 'Creeper Matojo', 'Bush Creeper',
                       (('56a038', '42882c', '28581c'), ('1c4214', '0e2a08'), dib),
                       ((0.7, 0.8, 1.0), (0, 0.42, 0)),
                       particulas=(('brizna', hojita((90, 162, 50))),))


# ======================================================================================================================
#  La Enredadera (Creeper de Raíz de Azalea)
# ======================================================================================================================
CORTEZA = rampa('2a1a0e', '3e2814', '56381c', '6e4a26', '8a6034')
MUSGO = rampa('1e3a10', '2c5016', '3c681e', '4e8028', '669a34')
HOJA_AZ = rampa('1a3a12', '24501a', '326a22', '42842c', '58a03a')
ROSA_AZ = rampa('7a2050', 'a83a74', 'd8609c', 'f08ec0', 'ffd0e6')


def corteza16(franja=(0.0, 1.0)):
    """La corteza de raíz: vetas blandas de arriba abajo (madera de azalea), con algo de musgo arriba."""
    vetas = L.vetas_suaves16(CORTEZA, base=2.0, luz=0.7, paso=2.2, onda=0.7, fuerza=0.4, celda=7.0, franja=franja)

    def fn(tw, th, cara, s):
        tex, _ = vetas(tw, th, cara, s)
        if cara == 'abajo':
            return tex, None
        xs, ys = L._malla(tw, th)
        f0, f1 = franja
        t = f0 + (ys + 0.5) / th * (f1 - f0) if cara != 'arriba' else np.zeros((th, tw))
        n = L._ruido(tw, th, s * 9 + 4, 5.0)
        a = np.clip((n - 0.55 - t * 0.9) / 0.1, 0, 1)[..., None]
        musgo = L.color_continuo(MUSGO, L.tono_suave(tw, th, cara, s + 3, 2.4, 0.5, 0.15, 5.0))
        return L._rgba(tex[..., :3] * (1 - a) + musgo * a), None
    return fn


def enredadera(raiz):
    m = B.Modelo('enredadera', K=2, ancho=128)
    m.escala = 0.55
    piel = L.grueso('piel_enredadera', corteza16())
    hojas = L.grueso('hojas_enredadera', L.manchas_suaves16(HOJA_AZ, ROSA_AZ, cuanto=0.18, celda=3.0, borde=0.05,
                                                             base=2.0, luz=0.7))
    flor = L.suave('flor_enredadera', ROSA_AZ, base=2.4, luz=0.9, ruido=0.12)
    hoja = L.brizna('hoja_enredadera', HOJA_AZ)
    liana = L.grueso('liana_enredadera', L.vetas_suaves16(CORTEZA, base=2.2, luz=0.4, paso=1.6, onda=0.4,
                                                          fuerza=0.3, vertical=False))
    y_cab = cuerpo(m, piel, piel)
    y1 = cabeza(m, 'enredadera', 'cuerpo', y_cab, corteza16, HUECO_E, neon='b04a80')
    # La mata de azalea en flor en la coronilla, con hojas que caen por los cantos.
    m.caja_desde('cabeza', (0, y1 - 1.2, -0.4), (17.4, 3.6, 17.4), hojas)
    m.caja_desde('cabeza', (0, y1 + 2.4, -0.8), (12.6, 2.8, 12.6), hojas)
    for (x, y, z, g) in ((-4.6, 2.4, 4.8, 2.2), (3.4, 2.4, 3.2, 1.8), (5.8, 5.2, -2.6, 2.2), (-2.4, 5.2, -3.6, 1.8),
                         (0.6, 5.2, 1.6, 2.4), (-6.8, 2.4, -4.0, 1.8), (7.2, 2.4, 5.0, 1.8)):
        m.caja('cabeza', (x, y1 + y - 0.2, z), (g, g, g), flor)
    for k in range(9):
        a = k / 9 * math.tau + 0.3
        x, z = math.cos(a) * 8.4, math.sin(a) * 8.4 - 0.4
        L.colmillo(m, 'cabeza', (x, y1 + 0.4, z), (math.cos(a) * 0.7, -1.0, math.sin(a) * 0.7), 4.6, 2.8, hoja,
                   fila=(-math.sin(a), 0, math.cos(a)))
    # Las lianas: dos raíces que le cuelgan de los lados de la cara y dos de la nuca, hasta las rodillas, con su flor en
    # la punta; con ellas te atrapa.
    for i, (x, z, largo) in enumerate(((-8.8, 4.0, 1.0), (8.8, 4.0, 1.0), (-8.6, -4.0, 0.8), (8.6, -4.0, 0.8))):
        lado = -1 if x < 0 else 1
        p0 = np.array((x, y_cab + 6.0, z))
        p1 = p0 + np.array((lado * 1.2, -8.0 * largo, 0.4))
        p2 = p1 + np.array((lado * 0.3, -8.0 * largo, 0.4))
        p3 = p2 + np.array((0.0, -6.0 * largo, 0.4))
        a_ = m.parte(f'liana{i}', 'cabeza', tuple(p0))
        b_ = m.parte(f'liana{i}b', a_, tuple(p1))
        c_ = m.parte(f'liana{i}c', b_, tuple(p2))
        m.viga(a_, p0, p1, 2.0, liana, extra=0.6)
        m.viga(b_, p1, p2, 1.7, liana, extra=0.6)
        m.viga(c_, p2, p3, 1.4, liana, extra=0.4)
        L.colmillo(m, c_, p3 + np.array((0, 0.6, 0)), (lado * 0.4, -1.0, 0.3), 4.0, 2.6, hoja)
        m.caja(c_, tuple(p3 + np.array((0, -0.2, 0.5))), (2.4, 2.4, 2.4), flor)

    def extra(s):
        for i in range(4):
            s.onda(f'liana{i}', 'r', 0, 6, periodo=1.6, fase=i * 0.23)
            s.onda(f'liana{i}b', 'r', 0, 9, periodo=1.6, fase=i * 0.23 + 0.15)
            s.onda(f'liana{i}c', 'r', 0, 12, periodo=1.6, fase=i * 0.23 + 0.3)

    def mecha(h):
        for i in range(4):
            lado = -1 if i % 2 == 0 else 1
            h.rot(f'liana{i}', [(0, 0, 0, 0), (1.0, -20, 0, lado * 25)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    a = m.anims['andar']
    for i in range(4):
        a.onda(f'liana{i}', 'r', 0, 10, fase=i * 0.25)
    at = m.anim('ataque', 0.9)
    for i in range(4):
        at.rot(f'liana{i}', [(0, 0, 0, 0), (0.12, 25, 0, 0), (0.3, -95, 0, 0), (0.75, -90, 0, 0), (0.9, 0, 0, 0)])
        at.rot(f'liana{i}b', [(0, 0, 0, 0), (0.12, 15, 0, 0), (0.3, -10, 0, 0), (0.75, -6, 0, 0), (0.9, 0, 0, 0)])
        at.rot(f'liana{i}c', [(0, 0, 0, 0), (0.3, -8, 0, 0), (0.9, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.12, -10, 0, 0), (0.3, 12, 0, 0), (0.9, 0, 0, 0)])
    est = m.anim('estado1', 1.0, bucle=True)
    for i in range(4):
        est.rot(f'liana{i}', [(0, -84, 0, 0), (0.5, -90, 0, 0), (1.0, -84, 0, 0)])
        est.rot(f'liana{i}b', [(0, -6, 0, 0), (0.5, -12, 0, 0), (1.0, -6, 0, 0)])
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '56381c', '1a0e08', boca='1a0e08',
                         motas=((5, 2, 'd8609c'), (8, 1, 'd8609c'), (10, 2, 'd8609c'), (4, 3, '42842c'), (6, 2, '42842c'),
                                (9, 2, '42842c'), (11, 3, '42842c'), (3, 8, '3c681e'), (12, 9, '3c681e')))
    return terminar(m, raiz, 'Creeper Enredadera', 'Vine Creeper',
                       (('8a6034', '6e4a26', '56381c'), ('2a1a0e', '0a0604'), dib),
                       ((1.5, 2.1, 2.4), (0, 1.2, 0)),
                       particulas=(('hoja', hojita((66, 132, 44))), ('flor', chispa((240, 142, 192)))))


# ======================================================================================================================
#  Los pinceles suaves de los demás
# ======================================================================================================================
def grietas_suaves16(r, rv, densidad=260, base=1.8, luz=0.6, franja=(0.0, 1.0)):
    """La roca suave con pocas grietas encendidas, y su resplandor que se funde alrededor (no una red de neón)."""
    def fn(tw, th, cara, s):
        v = L.tono_suave(tw, th, cara, s, base, luz, 0.18, 7.0, franja=franja)
        rgb = L.color_continuo(r, v)
        g = B.grietas(tw, th, s, cara, cuantas=max(1, (tw * th) // densidad), giro=0.5, ramas=0.07)
        h1 = B.vecinos(g)
        h2 = B.vecinos(g | h1)
        brillo = np.where(g, 1.0, np.where(h1, 0.22, np.where(h2, 0.06, 0.0)))[..., None]
        luzc = L.color_continuo(rv, np.where(g, 3.2, 1.6))
        rgb = rgb * (1 - brillo) + luzc * brillo
        tex = L._rgba(rgb)
        emis = np.zeros_like(tex)
        m = brillo[..., 0] > 0.1
        emis[m] = tex[m]
        return tex, emis
    return fn


def capullo_suave16(r, franja=(0.0, 1.0)):
    """El capullo de la rosa, suave: los pétalos cerrados en U imbricadas, con el canto apenas más oscuro."""
    def fn(tw, th, cara, s):
        v = L.tono_suave(tw, th, cara, s, 2.0, 0.6, 0.12, 6.0, franja=franja)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        sw, sh = 7.0, 5.0
        canto = np.zeros((th, tw))
        for fila in range(-1, th // int(sh) + 3):
            cy = fila * sh
            off = (sw / 2.0) * (fila % 2)
            cx = np.round((xs + 0.5 - off) / sw) * sw + off
            d = np.hypot(xs + 0.5 - cx, (ys + 0.5 - cy) * 1.1) / (sw * 0.62)
            canto = np.maximum(canto, np.clip(1 - np.abs(d - 0.92) / 0.12, 0, 1) * (d < 1.05))
        v = v - canto * 0.7
        return L._rgba(L.color_continuo(r, v)), None
    return fn


def gel_suave16(r, alfa=150):
    """El gel suave: translúcido, más claro arriba, con el brillo en el canto de arriba a la izquierda."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = L.tono_suave(tw, th, cara, s, 2.2, 0.8, 0.12, 8.0)
        v = v + np.where((xs == 0) | (ys == 0), 0.9, 0.0) + np.where((xs == 1) & (ys < th // 2), 0.6, 0.0)
        tex = L._rgba(L.color_continuo(r, v), alfa=alfa)
        return tex, None
    return fn


def carne_suave16(r, rv, franja=(0.0, 1.0)):
    """La carne viva, suave: el rojo que corre seguido, con unas venas finas y oscuras que serpentean (sin brillo)."""
    def fn(tw, th, cara, s):
        v = L.tono_suave(tw, th, cara, s, 2.0, 0.6, 0.2, 6.0, franja=franja)
        rgb = L.color_continuo(r, v)
        n = L._ruido(tw, th, s * 11 + 5, 6.0)
        vena = np.clip(1 - np.abs(n - 0.5) / 0.035, 0, 1)[..., None] * 0.7
        rgb = rgb * (1 - vena) + L.color_continuo(rv, np.full(v.shape, 2.0)) * vena
        return L._rgba(rgb), None
    return fn


def purpur_suave16(r, paso=8, franja=(0.0, 1.0)):
    """La púrpura suave: el bloque de losetas grandes, con las juntas apenas marcadas."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = L.tono_suave(tw, th, cara, s, 2.0, 0.6, 0.15, 7.0, franja=franja)
        junta = ((xs % paso) == 0) | ((ys % paso) == 0)
        v = v - junta * 0.5 + (((xs % paso) == 1) | ((ys % paso) == 1)) * 0.25
        return L._rgba(L.color_continuo(r, v)), None
    return fn


def costillas(m, parte, y_alto, n, paso, z_frente, ancho_cuerpo, pint, grueso=0.9):
    """Las costillas curvas, de dos en dos: del esternón hacia fuera y hacia atrás, por el costado."""
    for k in range(n):
        y = y_alto - k * paso
        for lado in (-1, 1):
            p0 = np.array((lado * 1.0, y, z_frente + 0.6))
            p1 = np.array((lado * ancho_cuerpo * 0.3, y - 0.8, z_frente + 0.7))
            p2 = np.array((lado * ancho_cuerpo * 0.46, y - 2.0, z_frente - 0.8))
            p3 = np.array((lado * (ancho_cuerpo / 2 + 0.2), y - 2.8, z_frente - 3.4))
            for a, b in ((p0, p1), (p1, p2), (p2, p3)):
                m.viga(parte, a, b, grueso, pint, ancho=grueso * 1.2, extra=0.4)


# ======================================================================================================================
#  El Ciego (Creeper Warden)
# ======================================================================================================================
SCULK = rampa('061418', '0a2026', '102e36', '183e48', '224e5a')


def ciego(raiz):
    m = B.Modelo('ciego', K=2, ancho=128)
    m.escala = 0.55
    sculk = lambda fr=(0.0, 1.0): L.suave16(SCULK, base=1.8, luz=0.6, ruido=0.25, celda=5.0, franja=fr)
    piel = L.grueso('piel_ciego', sculk())
    luz = L.luz_suave('luz_ciego', CIAN)
    borde = L.liso('borde_sensor_ciego', HUECO_C, base=2)
    hueso = L.grueso('hueso_ciego', L.suave16(HUESO_S, base=3.0, luz=0.6, ruido=0.1))
    y_cab = cuerpo(m, piel, piel)
    for p in PATAS:
        pz = 8.0 if p[5] == 'd' else -8.0
        px = 4.0 if p[6] == 'i' else -4.0
        m.caja(p, (px, 1.6, pz + (4.05 if pz > 0 else -4.05)), (5.0, 1.8, 0.2), luz)
    # El pecho del warden: las almas encendidas dentro de la jaula de costillas y el esternón; las manchas de sculk
    # de los hombros, que laten.
    m.parte('almas', 'cuerpo', (0, 24.0, 4.0))
    m.caja('almas', (0, 25.0, 4.02), (11.0, 14.0, 0.2), L.grueso('almas_ciego', almas16(CIAN, HUECO_C)))
    m.caja('cuerpo', (0, 25.6, 4.45), (1.4, 13.0, 0.9), hueso)
    costillas(m, 'cuerpo', 30.6, 3, 3.8, 4.0, 16.0, hueso, grueso=0.85)
    m.parte('manchas', 'cuerpo', (0, 30.0, 0))
    for lado in (-1, 1):
        sensor(m, 'manchas', (lado * 8.0, 31.0, 0.0, 'der' if lado > 0 else 'izq'), luz, borde)
        sensor(m, 'manchas', (lado * 5.6, 15.0, 4.0, 'frente'), luz, borde, tam=2.0)
    # La cabeza: la cara de creeper sin ojos, con la boca encendida de cian (la del original), y las orejas del warden.
    y1 = cabeza(m, 'ciego', 'cuerpo', y_cab, sculk, HUECO_C, neon='3ad8ff', sin_ojos=True)
    orejas_warden(m, 'cabeza', y1, piel, luz)

    def extra(s):
        for k, ld in enumerate(('i', 'd')):
            s.onda(f'oreja_{ld}', 'r', 2, 4 * (1 if ld == 'i' else -1), periodo=2.0, fase=k * 0.15)
        s.onda('almas', 'e', 1, 0.04, base=1.0, periodo=1.0)
        s.onda('manchas', 'e', 0, 0.03, base=1.0, periodo=1.0, fase=0.25)

    def mecha(h):
        for ld, sg in (('i', 1), ('d', -1)):
            h.rot(f'oreja_{ld}', [(0, 0, 0, 0)] + [(0.1 * k, 0, 0, sg * (8 if k % 2 else -3) * (1 + k * 0.12))
                                                  for k in range(1, 11)])
        h.esc('almas', [(0, 1, 1, 1), (1.0, 1.15, 1.15, 1.6)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    e2 = m.anim('especial2', 1.2)
    for ld, sg in (('i', 1), ('d', -1)):
        e2.rot(f'oreja_{ld}', [(0, 0, 0, 0), (0.15, 0, 0, sg * 18), (0.25, 0, 0, sg * 10), (0.35, 0, 0, sg * 18),
                               (0.45, 0, 0, sg * 10), (0.9, 0, 0, sg * 15), (1.2, 0, 0, 0)])
    e2.rot('cabeza', [(0, 0, 0, 0), (0.15, 0, 18, 0), (0.35, 0, -12, 0), (0.5, -14, 0, 0), (0.95, -14, 0, 0),
                      (1.2, 0, 0, 0)])
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '102e36', '102e36', boca='3ad8ff',
                         motas=((3, 3, '3ad8ff'), (12, 3, '3ad8ff'), (2, 2, '183e48'), (13, 2, '183e48'),
                                (7, 12, 'a8bebe'), (8, 12, 'a8bebe'), (7, 13, '3ad8ff'), (8, 13, '3ad8ff')))
    return terminar(m, raiz, 'Creeper Ciego', 'Blind Creeper',
                       (('224e5a', '183e48', '102e36'), ('06404a', '040e12'), dib),
                       ((1.5, 2.4, 2.4), (0, 1.3, 0)),
                       particulas=(('vibracion', anillo((58, 216, 255))), ('sculk', esquirla((20, 58, 68)))))


# ======================================================================================================================
#  El Volcánico (Creeper de Magma)
# ======================================================================================================================
BASALTO = rampa('100c0c', '1c1616', '2a2220', '3a302c', '4c403a')


def volcanico(raiz):
    m = B.Modelo('volcanico', K=2, ancho=128)
    m.escala = 0.55
    roca = lambda fr=(0.0, 1.0): grietas_suaves16(BASALTO, MAGMA, franja=fr)
    piel = L.grueso('piel_volcanico', roca())
    columna = L.grueso('columna_volcanico', L.vetas_suaves16(BASALTO, base=2.0, luz=0.7, paso=2.0, onda=0.2,
                                                             fuerza=0.35))
    lava = L.luz_suave('lava_volcanico', LAVA, centro=3.0)
    y_cab = cuerpo(m, piel, piel)
    # La cabeza: basalto con la cara de creeper honda y fundida por dentro (los ojos y la boca de lava, como el original).
    y1 = cabeza(m, 'volcanico', 'cuerpo', y_cab, roca, HUECO_M, neon='ffb21a',
                cara16=lambda fr: L.suave16(BASALTO, base=1.8, luz=0.6, ruido=0.18, franja=fr))
    # La corona de columnas de basalto del original, con la lava encima y un hilo que les cae.
    m.parte('corona', 'cabeza', (0, y1, 0))
    cols = ((0.0, -1.0, 10.0, 4.0), (-4.8, 0.6, 7.0, 3.6), (4.6, -0.4, 8.0, 3.6), (-2.2, -5.2, 6.0, 3.4),
            (2.8, 4.0, 5.0, 3.2), (5.4, -4.8, 5.0, 3.0))
    for k, (x, z, alto, g) in enumerate(cols):
        rot = (z * 1.8, 0.0, -x * 1.8)
        e = eje_de(rot)
        base = np.array((x, y1 - 1.0, z))
        m.caja_desde('corona', tuple(base), (g, alto, g), columna, rot=rot)
        tope = base + e * (alto - 0.5)
        m.caja('corona', tuple(tope), (g + 0.3, 1.4, g + 0.3), lava, rot=rot)
        if k % 2 == 0:
            lado = B.girar(rot)[:3, :3] @ np.array((g / 2 + 0.15, 0.0, 0.0))
            m.caja('corona', tuple(tope - e * (1.0 + alto * 0.12) + lado), (0.4, 2.0 + alto * 0.2, 1.0), lava, rot=rot)

    def extra(s):
        s.onda('corona', 'e', 1, 0.03, base=1.0, periodo=1.5)

    def mecha(h):
        h.esc('corona', [(0, 1, 1, 1), (0.5, 1.06, 1.3, 1.06), (1.0, 1.12, 1.6, 1.12)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '2a2220', 'ffd23a', boca='ffa82a',
                         motas=((4, 4, 'e8640a'), (11, 3, 'e8640a'), (3, 11, 'a82a06'), (12, 9, 'e8640a'),
                                (6, 2, '4c403a'), (8, 1, '4c403a'), (10, 2, '4c403a'), (8, 2, 'ffa82a')))
    return terminar(m, raiz, 'Creeper Volcánico', 'Volcanic Creeper',
                       (('4c403a', '3a302c', '2a2220'), ('e8640a', '5a0c02'), dib),
                       ((1.5, 2.2, 2.4), (0, 1.2, 0)),
                       particulas=(('brasa', chispa((255, 150, 40))), ('roca', esquirla((50, 42, 38))),
                                   ('gota', gota((255, 120, 20)))))


# ======================================================================================================================
#  El Marchito (Creeper de Wither Rose)
# ======================================================================================================================
TALLO = rampa('0c0e0c', '161a16', '222822', '303830', '404a40')
PETALO = rampa('1a0a0e', '3a1420', '5e1e2e', '8a2c40', 'c04a5e')
CORAZON_ROSA = rampa('3a0610', '5e0c18', '861a26', 'b02a36', 'd8485a')


def marchito(raiz):
    m = B.Modelo('marchito', K=2, ancho=128)
    m.escala = 0.55
    tallo = L.grueso('tallo_marchito', L.vetas_suaves16(TALLO, base=2.0, luz=0.7, paso=1.8, onda=0.3, fuerza=0.35))
    espina = L.diente('espina_marchito', ESPINA)
    petalo = L.petalo('petalo_marchito', PETALO)
    petalo2 = L.petalo('petalo2_marchito', L.juntar(CORAZON_ROSA[:2], PETALO[2:]))
    hoja = L.brizna('hoja_marchito', HOJA_W)
    y_cab = cuerpo(m, tallo, tallo)
    # La zarza: el tallo con sus espinas, y dos hojas mustias que le cuelgan de los hombros.
    for (x, y, z, hx, hz) in ((8.0, 17.0, 1.0, 1, 0.3), (-8.0, 21.0, -1.0, -1, -0.2), (8.0, 28.0, -1.6, 1, -0.3),
                              (-8.0, 31.0, 1.2, -1, 0.3), (2.4, 24.0, 4.0, 0.3, 1), (-3.0, 16.0, 4.0, -0.3, 1),
                              (-2.0, 29.0, -4.0, -0.3, -1)):
        L.colmillo(m, 'cuerpo', (x, y, z), (hx, 0.35, hz), 3.4, 2.0, espina)
    for lado, ld in LADOS:
        n = m.parte(f'hoja_{ld}', 'cuerpo', (lado * 8.0, y_cab - 2.0, 0.0))
        L.colmillo(m, n, (lado * 7.8, y_cab - 2.0, 0.0), (lado * 1.0, -0.5, 0.25), 10.0, 3.6, hoja, fila=(0, 0, 1))
    # La cabeza: el capullo de la rosa, con la cara de creeper honda y el rojo del corazón de la rosa dentro.
    y1 = cabeza(m, 'marchito', 'cuerpo', y_cab, lambda fr: capullo_suave16(PETALO, fr), HUECO_W, neon='c0303a')
    # La rosa marchita abierta encima (lo suyo): el corazón rojo oscuro y dos coronas de pétalos anchos, en copa.
    m.parte('rosa', 'cabeza', (0, y1, 0))
    m.caja('rosa', (0, y1 + 2.0, 0), (5.0, 4.0, 5.0), L.suave('corazon_rosa', CORAZON_ROSA, base=2.4, luz=0.8, ruido=0.1))
    for k in range(6):
        a = (k + 0.5) / 6 * math.tau
        x, z = math.cos(a) * 2.0, math.sin(a) * 2.0
        L.colmillo(m, 'rosa', (x, y1 + 0.8, z), (math.cos(a) * 0.45, 1.0, math.sin(a) * 0.45), 7.0, 6.4, petalo2,
                   fila=(-math.sin(a), 0, math.cos(a)), cruz=False)
    for k in range(8):
        a = k / 8 * math.tau
        x, z = math.cos(a) * 3.6, math.sin(a) * 3.6
        L.colmillo(m, 'rosa', (x, y1 + 0.3, z), (math.cos(a) * 0.8, 1.0, math.sin(a) * 0.8), 11.0, 10.0, petalo,
                   fila=(-math.sin(a), 0, math.cos(a)), cruz=False)

    def extra(s):
        s.onda('rosa', 'r', 1, 6, periodo=4.0)
        for k, ld in enumerate(('i', 'd')):
            s.onda(f'hoja_{ld}', 'r', 2, 6 * (1 if ld == 'i' else -1), periodo=1.5, fase=k * 0.3)

    def mecha(h):
        h.esc('rosa', [(0, 1, 1, 1), (0.5, 1.25, 0.9, 1.25), (1.0, 1.5, 0.8, 1.5)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '24141a', 'c0303a', boca='c0303a',
                         motas=((6, 1, '3a1e26'), (7, 1, '3a1e26'), (8, 1, '3a1e26'), (9, 1, '3a1e26'), (5, 2, '582a34'),
                                (10, 2, '582a34'), (7, 2, 'b02a36'), (8, 2, 'b02a36'), (3, 10, '222822'), (12, 11, '222822')))
    return terminar(m, raiz, 'Creeper Marchito', 'Withered Creeper',
                       (('582a34', '3a1e26', '24141a'), ('86806e', '120a0c'), dib),
                       ((1.6, 2.4, 2.6), (0, 1.25, 0)),
                       particulas=(('petalo', hojita((74, 26, 32))), ('ceniza', esquirla((134, 128, 110)))))


# ======================================================================================================================
#  La Gelatina (Creeper de Fluido)
# ======================================================================================================================
GEL = rampa('0e5244', '188270', '2aac94', '62dcc2', 'bafff2')
NUCLEO_G = rampa('041a14', '082a24', '0e3e36', '16564c', '207066')


def gelatina(raiz):
    m = B.Modelo('gelatina', K=2, ancho=128)
    m.escala = 0.55
    m.translucido = True
    gel = L.grueso('gel_gelatina', gel_suave16(GEL))
    nucleo16 = lambda fr=(0.0, 1.0): L.suave16(NUCLEO_G, base=2.0, luz=0.6, ruido=0.15, franja=fr)
    nucleo = L.grueso('nucleo_gelatina', nucleo16())
    luz = L.luz_suave('burbuja_gelatina', GEL)
    # Como el Slime: dentro, el creeper oscuro (el núcleo), y por fuera, el gel con la misma forma, más grande.
    m.parte('cuerpo', None, (0, 12.0, 0))
    patas(m, 'cuerpo', 4.0, 8.0, 5.0, 12.0, nucleo)
    for p in PATAS:
        pz = 8.0 if p[5] == 'd' else -8.0
        px = 4.0 if p[6] == 'i' else -4.0
        m.caja_desde(p, (px, -0.01, pz), (8.0, 12.02, 8.0), gel)
    m.caja_desde('cuerpo', (0, 12.0, 0), (11.0, 24.0, 4.0), nucleo)
    m.caja_desde('cuerpo', (0, 12.0, 0), (16.0, 24.2, 8.0), gel)
    y1 = cabeza(m, 'gelatina', 'cuerpo', 36.0, nucleo16, HUECO_G, neon='5affd8', Lc=16.0)
    m.caja_desde('cabeza', (0, 35.6, 0.4), (19.0, 19.0, 19.0), gel)
    for k, (x, largo) in enumerate(((-6.0, 3.0), (-1.4, 5.0), (3.0, 3.6), (7.0, 2.4))):
        n = m.parte(f'baba{k}', 'cabeza', (x, 35.6, 9.2))
        m.caja_desde(n, (x, 35.6 - largo, 9.2), (1.6, largo, 1.6), gel)
    for k, (x, y, z, g) in enumerate(((-8.4, 2.0, 5.0, 1.4), (8.6, 6.0, -4.0, 1.2), (-8.2, 10.0, -6.0, 1.0),
                                       (6.0, 1.0, 9.0, 1.0))):
        n = m.parte(f'burbuja{k}', 'cabeza', (x, 36.0 + y, z))
        m.caja(n, (x, 36.0 + y, z), (g, g, g), luz)

    def extra(s):
        for k in range(4):
            s.onda(f'baba{k}', 'e', 1, 0.12, base=1.0, periodo=2.0, fase=k * 0.17)
            s.mov(f'burbuja{k}', [(0, 0, -1.5, 0), (3.0, 0, 3.5, 0)])
        s.onda('cuerpo', 'e', 0, 0.02, base=1.0, periodo=1.5)

    def mecha(h):
        h.esc('cabeza', [(0, 1, 1, 1)] + [(0.1 * k, 1 + 0.012 * k * (1 if k % 2 else -1),
                                           1 - 0.01 * k * (1 if k % 2 else -1),
                                           1 + 0.012 * k * (1 if k % 2 else -1)) for k in range(1, 11)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '2aac94', '8affe8', boca='5affd8',
                         motas=((4, 3, 'bafff2'), (5, 3, 'bafff2'), (4, 4, 'bafff2'), (12, 11, '62dcc2'), (3, 12, '62dcc2'),
                                (11, 4, '62dcc2')))
    return terminar(m, raiz, 'Creeper Gelatina', 'Jelly Creeper',
                       (('62dcc2', '2aac94', '188270'), ('bafff2', '0e5244'), dib),
                       ((1.5, 2.2, 2.4), (0, 1.2, 0)),
                       particulas=(('burbuja', anillo((90, 216, 188))), ('gota', gota((36, 168, 142)))))


# ======================================================================================================================
#  El Latido (Creeper Visceral)
# ======================================================================================================================
CARNE = rampa('4a0a14', '701420', '942030', 'b8343e', 'd8565a')
VENA = rampa('2a0618', '420a26', '5a1034', '701844', '882254')


def latido(raiz):
    m = B.Modelo('latido', K=2, ancho=128)
    m.escala = 0.55
    carne16 = lambda fr=(0.0, 1.0): carne_suave16(CARNE, VENA, franja=fr)
    piel = L.grueso('piel_latido', carne16())
    hueso = L.grueso('hueso_latido', L.suave16(HUESO_L, base=3.0, luz=0.6, ruido=0.1))
    diente = L.diente('diente_latido', HUESO_L)
    hueco = L.boca('hueco_latido', HUECO_L, 'ff3a5a')
    corazon = L.grueso('corazon_latido', carne_suave16(CORAZON, VENA), pleno=True)
    y_cab = cuerpo(m, piel, piel)
    # El pecho abierto: el hueco encendido, el corazón que late saliendo entre las costillas, y el esternón.
    m.caja('cuerpo', (0, 24.0, 4.02), (11.0, 14.0, 0.2), hueco)
    m.parte('corazon', 'cuerpo', (0, 23.4, 5.4))
    m.caja('corazon', (0, 23.2, 5.4), (7.0, 8.0, 5.0), corazon)
    m.caja('corazon', (0.6, 18.6, 5.2), (4.0, 2.4, 4.0), corazon)
    m.caja('corazon', (-2.0, 27.8, 5.2), (3.2, 3.0, 3.4), corazon)
    m.caja('corazon', (2.2, 27.4, 4.8), (2.8, 2.8, 3.0), corazon)
    for (x, dx) in ((-1.4, -0.6), (1.6, 1.0)):
        m.viga('corazon', (x, 28.4, 5.0), (x + dx, 33.0, 3.4), 1.8, corazon, extra=0.4)
    costillas(m, 'cuerpo', 30.0, 3, 4.0, 7.6, 16.0, hueso, grueso=1.0)
    m.caja('cuerpo', (0, 29.6, 7.8), (1.6, 4.4, 1.0), hueso)
    # La cabeza: carne con la cara de creeper honda y encendida de rojo por dentro, y la corona de dientes del original.
    y1 = cabeza(m, 'latido', 'cuerpo', y_cab, carne16, HUECO_L, neon='ff3a5a')
    m.parte('corona', 'cabeza', (0, y1, 0))
    m.caja('corona', (0, y1 + 0.1, 0), (8.0, 0.2, 8.0), {'arriba': hueco})
    for k in range(10):
        a = k / 10 * math.tau
        x, z = math.cos(a) * 4.4, math.sin(a) * 4.4
        L.colmillo(m, 'corona', (x, y1 + 0.2, z), (math.cos(a) * 0.45, 1.0, math.sin(a) * 0.45), 4.0 + (k % 2) * 1.4,
                   2.5, diente, fila=(-math.sin(a), 0, math.cos(a)))

    latidos = [(0, 1, 1, 1), (0.12, 1.16, 1.16, 1.16), (0.24, 1, 1, 1), (0.36, 1.1, 1.1, 1.1), (0.55, 1, 1, 1),
               (1.2, 1, 1, 1), (1.32, 1.16, 1.16, 1.16), (1.44, 1, 1, 1), (1.56, 1.1, 1.1, 1.1), (1.75, 1, 1, 1),
               (2.4, 1, 1, 1), (2.52, 1.16, 1.16, 1.16), (2.64, 1, 1, 1), (2.76, 1.1, 1.1, 1.1), (2.95, 1, 1, 1),
               (3.0, 1, 1, 1)]

    def extra(s):
        s.esc('corazon', latidos)
        s.esc('corona', [(t, 1 + (x - 1) * 0.5, 1 - (x - 1) * 0.4, 1 + (x - 1) * 0.5) for (t, x, _, _) in latidos])

    def mecha(h):
        h.esc('corazon', [(0, 1, 1, 1)] + [(0.08 * k, 1.22 if k % 2 else 1.04, 1.22 if k % 2 else 1.04,
                                            1.22 if k % 2 else 1.04) for k in range(1, 13)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '942030', 'ff3a5a', boca='ff3a5a',
                         motas=((7, 13, 'd01a2a'), (8, 13, 'd01a2a'), (7, 12, 'ff4a5a'), (5, 2, 'dcd0b0'), (7, 2, 'dcd0b0'),
                                (9, 2, 'dcd0b0'), (11, 3, 'dcd0b0'), (3, 9, '5a1034'), (12, 10, '5a1034')))
    return terminar(m, raiz, 'Creeper Latido', 'Heartbeat Creeper',
                       (('b8343e', '942030', '701420'), ('5a1034', '4a0a14'), dib),
                       ((1.5, 2.2, 2.4), (0, 1.2, 0)),
                       particulas=(('sangre', gota((200, 26, 42))), ('hueso', esquirla((220, 208, 176))),
                                   ('onda', anillo((255, 74, 90)))))


# ======================================================================================================================
#  El Artillero (Creeper Shulker)
# ======================================================================================================================
PURPUR = rampa('4a284a', '623662', '7c467c', '985a98', 'b274b2')
CONCHA = rampa('3a1c42', '522860', '6c367c', '88489a', 'a460b4')


def artillero(raiz):
    m = B.Modelo('artillero', K=2, ancho=128)
    m.escala = 0.55
    piel = L.grueso('piel_artillero', purpur_suave16(PURPUR))
    concha16 = lambda fr=(0.0, 1.0): L.vetas_suaves16(CONCHA, base=2.0, luz=0.7, paso=2.4, onda=0.15, fuerza=0.3,
                                                      vertical=False, franja=fr)
    concha = L.grueso('concha_artillero', concha16())
    nucleo = L.boca('nucleo_artillero', HUECO_A, 'fff0a0')
    y_cab = cuerpo(m, piel, L.grueso('pilar_artillero', L.vetas_suaves16(PURPUR, base=2.0, luz=0.6, paso=2.0, onda=0.1,
                                                                        fuerza=0.3)))
    # Unas hombreras chicas de concha.
    for lado in (-1, 1):
        m.caja('cuerpo', (lado * 8.6, y_cab - 2.6, 0), (3.6, 5.0, 9.0), concha, rot=(0, 0, lado * -10))
    # La cabeza es una caja de shulker con la cara de creeper honda y encendida del amarillo del shulker: la parte de
    # abajo (con los ojos y la boca) y la tapa (la frente), que se abre desde atrás para disparar.
    Lc, prof = 16.0, 2.0
    m.parte('cabeza', 'cuerpo', (0, y_cab, 0))
    m.caja_desde('cabeza', (0, y_cab, -prof / 2), (Lc, 12.0, Lc - prof), concha,
                 caras={'frente': L.grueso('hueco_artillero', fondo_hueco16(HUECO_A, 'fff0a0', filas=(2, 8))),
                        'arriba': nucleo})

    def franja(f0, f1):
        return L.grueso(f'cara_artillero_{int(round(f0 * 8))}{int(round(f1 * 8))}', concha16((f0, f1)))
    cara_honda(m, 'cabeza', y_cab, Lc, franja, L.liso('pared_artillero', HUECO_A, base=1), Lc / 2, prof,
               filas=(2, 8))
    m.parte('tapa', 'cabeza', (0, y_cab + 12.0, -Lc / 2))
    m.caja_desde('tapa', (0, y_cab + 12.0, 0), (Lc, 4.0, Lc), concha, caras={'abajo': nucleo})
    m.caja_desde('tapa', (0, y_cab + 11.4, 0), (Lc + 1.4, 1.4, Lc + 1.4), concha)

    def extra(s):
        s.onda('tapa', 'r', 0, -1.0, periodo=3.0, base=-1.5)

    def mecha(h):
        h.rot('tapa', [(0, 0, 0, 0)] + [(0.1 * k, -8 if k % 2 else -2, 0, 0) for k in range(1, 11)])
    anims(m, extra_siempre=extra, extra_hinchado=mecha)
    at = m.anim('ataque', 1.0)
    at.rot('tapa', [(0, 0, 0, 0), (0.25, -75, 0, 0), (0.6, -75, 0, 0), (1.0, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.4, -6, 0, 0), (0.48, 8, 0, 0), (0.7, 0, 0, 0)])
    at.esc('cuerpo', [(0, 1, 1, 1), (0.45, 1, 1, 1), (0.5, 1.06, 0.94, 1.06), (0.65, 1, 1, 1)])
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        huevo_creeper(px, filas, c, '7c467c', 'fff4b0', boca='fff0a0',
                         motas=tuple((x, f, '6c367c') for f in (2, 3) for x in range(4, 12)) + ((7, 4, 'f0e070'),
                                                                                                 (8, 4, 'f0e070')))
    return terminar(m, raiz, 'Creeper Artillero', 'Gunner Creeper',
                       (('b274b2', '985a98', '7c467c'), ('6c367c', '3a1c42'), dib),
                       ((1.5, 2.2, 2.4), (0, 1.2, 0)),
                       particulas=(('chispa', chispa((255, 240, 160))), ('placa', esquirla((150, 82, 160)))))


MOBS = {'atomico': atomico, 'ciego': ciego, 'tarta': tarta, 'matojo': matojo, 'volcanico': volcanico,
        'marchito': marchito, 'enredadera': enredadera, 'gelatina': gelatina, 'latido': latido,
        'artillero': artillero}


# Lo que cuenta la ficha de cada uno: el nombre, el original del DEDsafío, la idea, las señas, el sitio de la foto, la
# referencia recortada del cartel (si la hay) y el centro de la cabeza (en bloques) para la foto de cerca.
FICHA = {
    'atomico': ('Creeper Atómico', 'Creeper Nuclear (DEDsafío 4)',
                'El creeper-bidón del original (amarillo, con zunchos negros, la cara de creeper y el botón rojo), mejor '
                'hecho: la cara honda con el verde de lo radiactivo dentro, y el botón rojo hecho sirena en su jaula, '
                'que gira cuando se enciende la mecha (su mecha es una sirena).',
                ['<b>Dos barras de combustible</b> encendidas a la espalda, que asoman a los lados de la cabeza.',
                 '<b>La mirilla</b> del bidón, con el líquido verde encendido; la franja de rayas de peligro y los '
                 'zunchos remachados; las patas de hierro negro con el pie de rayas, como las del original.'],
                'nieve', 'ref_nuclear.png', (0, 1.59, 0.38)),
    'ciego': ('Creeper Ciego', 'Creeper Warden (DEDsafío 3)',
              'Un creeper con el cuerpo del de siempre, de sculk suave, y lo del warden: su cara de creeper sin ojos, '
              'con la boca encendida de cian como la del original, y las orejas del warden, oscuras y con la luz '
              'dentro.',
              ['<b>Las orejas del warden</b>, anchas y curvas: tiemblan cuando te oye y cuando se le enciende la mecha.',
               '<b>El pecho del warden</b>: las almas encendidas dentro de la jaula de costillas.',
               'Las manchas de sculk que laten en los hombros y los pies encendidos.'],
              'cueva', 'ref_warden.png', (0, 1.51, 0.28)),
    'tarta': ('Creeper Tarta', 'Creeper Cake (DEDsafío 3 y 4)',
              'Un creeper normal, con sus patas de creeper, de chocolate, y la cabeza de tarta del original: el '
              'bizcocho con su capa de nata, el glaseado con los puntitos rojos que gotea por los cantos y la vela '
              'verde encendida. La cara de creeper es honda, con la mermelada encendida dentro.',
              ['<b>Un cuello de glaseado</b> que gotea por el pecho; <b>dos cerezas</b> junto a la vela.',
               'Con la mecha, la llama se aviva hasta hacerse enorme.'],
              'noche', 'ref_cake.png', (0, 1.51, 0.28)),
    'matojo': ('Creeper Matojo', 'Creeper de Pasto (DEDsafío 4)',
               'Un creeper chiquito y rechoncho de hierba, como el original: la cabeza grande, el cuerpo y las patas '
               'cortas, todo de hierba suave. La cara de creeper es honda y oscura, con un punto verde lima al fondo de '
               'cada ojo.',
               ['<b>Una matita</b> de hierba en la coronilla con dos flores de pradera (un diente de león y una '
                'amapola), y briznas en los pies.',
                'Sale de la hierba de un salto cuando la rompes, y con la mecha se le eriza la mata.'],
               'noche', 'ref_pasto.png', (0, 0.6, 0.17)),
    'volcanico': ('Creeper Volcánico', 'Creeper de Magma (DEDsafío 4)',
                  'Un creeper de basalto con pocas grietas de magma que brillan (el cuerpo, las patas y la nuca; la cara, '
                  'limpia), con la cara honda y fundida por dentro, como la del original.',
                  ['<b>La corona de columnas de basalto</b> del original, con la lava encima y un hilo de lava que les '
                   'cae: con la mecha, entra en erupción.',
                   'Va soltando brasas, y al estallar deja la lava.'],
                  'nether', 'ref_magma.png', (0, 1.51, 0.28)),
    'marchito': ('Creeper Marchito', 'Creeper de Wither Rose (DEDsafío 4)',
                 'Del original solo hay el aviso, sin cara. Es la rosa marchita hecha creeper: el cuerpo, el tallo negro '
                 'con sus espinas; la cabeza, el capullo, con la cara honda y el rojo del corazón de la rosa dentro.',
                 ['<b>La rosa marchita</b> abierta encima de la cabeza, en copa: con la mecha se abre del todo.',
                  'Dos hojas mustias que le cuelgan de los hombros.',
                  'Al estallar pone el Wither y siembra rosas marchitas.'],
                 'nether', None, (0, 1.51, 0.28)),
    'enredadera': ('Creeper Enredadera', 'Creeper de Raíz de Azalea (DEDsafío 4)',
                   'Del original solo hay los avisos (te enreda y estalla). Es un creeper de corteza de raíz, con musgo, la '
                   'mata de azalea en flor en la coronilla y la cara honda con un rosa de azalea al fondo.',
                   ['<b>Las lianas</b>: cuatro raíces que le cuelgan de los lados de la cabeza hasta las rodillas, con su '
                    'flor en la punta. Las lanza para atraparte y te arrastra; con la mecha, se tensan.'],
                   'noche', None, (0, 1.51, 0.28)),
    'gelatina': ('Creeper Gelatina', 'Creeper de Fluido (DEDsafío 4)',
                 'Del original solo hay el aviso (de Gleba, trepa, y al estallar te deja sin señal). Está hecho como el '
                 'Slime: un creeper de gel translúcido y, dentro, el creeper oscuro con la cara encendida de agua.',
                 ['<b>Babas</b> en la barbilla y <b>burbujas</b> encendidas que suben por dentro del gel.',
                  'Con la mecha, el gel tiembla cada vez más.'],
                 'noche', None, (0, 1.51, 0.33)),
    'latido': ('Creeper Latido', 'Creeper Visceral (DEDsafío 4)',
               'El creeper visceral del original: de carne viva, suave, con venas, y la cara de creeper honda y '
               'encendida de rojo por dentro.',
               ['<b>El corazón</b>, al aire entre las costillas abiertas del pecho: late (dos golpes y la pausa) y se '
                'desboca con la mecha.',
                '<b>La corona de dientes</b> del original, en la coronilla, que se abre con cada latido.',
                'Solo lo revienta el Altavoz.'],
               'nether', 'ref_visceral.png', (0, 1.51, 0.28)),
    'artillero': ('Creeper Artillero', 'Creeper Shulker (DEDsafío 3)',
                  'Del original solo hay los avisos (disparaba proyectiles de shulker que estallan). Un creeper de '
                  'púrpura con la cabeza de caja de shulker: la cara honda, encendida del amarillo del shulker.',
                  ['<b>La tapa de la caja</b> se abre para disparar el obús y deja ver el núcleo encendido; con la '
                   'mecha, traquetea.',
                   'Unas hombreras chicas de concha.'],
                  'end', None, (0, 1.51, 0.28)),
}

ORDEN = ('atomico', 'ciego', 'tarta', 'matojo', 'volcanico', 'marchito', 'enredadera', 'gelatina', 'latido', 'artillero')


def main():
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    carpeta = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ORDEN)
    hechos = [MOBS[p](raiz) for p in pedidos]
    if carpeta:
        import bestiario_escenas as be
        os.makedirs(carpeta, exist_ok=True)
        fotos = os.environ.get('SIN_FOTOS') != '1'
        secciones = []
        for mm in hechos:
            nombre, original, texto, lineas, sitio, ref, centro = FICHA[mm.id]
            heroe = f'{mm.id}_heroe.jpg'
            cab = f'{mm.id}_cabeza.jpg'
            if fotos:
                be.heroe(mm, sitio, os.path.join(carpeta, heroe))
                be.cabeza(mm, sitio, os.path.join(carpeta, cab), centro, dist=1.4 if mm.id != 'matojo' else 0.8)
            secciones.append((nombre, original, texto, lineas, heroe, cab,
                              ref if ref and os.path.exists(os.path.join(carpeta, ref)) else None))
        grupos = [f'creepers_juntos_{k // 5 + 1}.jpg' for k in range(0, len(hechos), 5)] if len(hechos) > 1 else []
        if fotos:
            for k, g in zip(range(0, len(hechos), 5), grupos):
                be.fila([(mm, None, 0.0) for mm in hechos[k:k + 5]], 'noche', os.path.join(carpeta, g))
        be.ficha(os.path.join(carpeta, 'creepers_ficha.html'), 'Los creepers, rediseñados',
                 'Los diez creepers del DEDsafío, rediseñados: todos con la anatomía del creeper de siempre (la cabeza, '
                 'el cuerpo alto y cuatro patas de verdad) y su cara de creeper, ahora honda, con texturas suaves; y '
                 'cada uno con lo suyo del DEDsafío, mejor hecho. Lo que se ve es el modelo del juego.',
                 secciones, grupos)


if __name__ == '__main__':
    main()

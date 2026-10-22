"""
El Dromoraptor Azul (DEDsafío 4, cartel del día 4; libro del juego: «El dromoraptor turquesa de aletas rojas:
muerde menos que el Rojo, pero corre muchísimo. También va en manada: sale con otros dos y se avisan»).

Rehecho con el mismo nivel de detalle anatómico, abanicos en escalera, aletas en los brazos, bloque sensorial translúcido
y animaciones de velociraptor que el Dromoraptor Verde:
  - Piel turquesa / azul océano brillante con motas verdiazuladas y vientre aguamarina suave.
  - Abanicos del lomo y aletas de los brazos con membrana escarlata / carmesí viva y radios cian brillantes.
  - Bloque amarillo translúcido en el hocico y dos crestas turquesa hacia atrás.
  - Animaciones: boca abierta jadeante con abanicos que respiran, cabeza a tirones de ave, carrera en zigzag con
    cola balanceada, mordisco veloz, llamada a la manada y salto de emboscada.
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
import bestiario_reptiles as R
from bestiario import T
from bestiario_hormigas import _azar1
from quiu.dromoraptor_verde import (
    CABEZA_DROMORAPTOR_VERDE,
    _franja_dromoraptor_verde,
    _lamina_dromoraptor_verde,
    _linea_dromoraptor_verde,
    _manchas_dromoraptor_verde,
    _poligono_dromoraptor_verde,
    _reemplazar_dromoraptor_verde,
    _sagital_dromoraptor_verde,
    _tex_dromoraptor_verde,
    dientes_dromoraptor_verde,
    boca_dromoraptor_verde,
    quitar_dromoraptor_verde,
)

ID = 'dromoraptor_azul'
TAM = 1.28

HUEVO = (
    ('1882a0', '0e5c74', '04222c'),
    ('ac1a22', '3a060a'),
    [
        ((9, 6), 'f0c818'), ((10, 6), '120a06'),
        ((5, 4), 'ac1a22'), ((6, 3), 'd62a34'), ((7, 4), 'ac1a22'),
        ((10, 3), 'c8c418'), ((11, 3), 'f0e040'),
    ],
)

# ======================================================================================================================
#  Rampas de color
# ======================================================================================================================
PIEL_DROMORAPTOR_AZUL = B.rampa('04222c', '083c4e', '0e5c74', '1882a0', '2aaac8')
OLIVA_DROMORAPTOR_AZUL = B.rampa('02161c', '052834', '0a4050', '106076', '1c849e')
VIENTRE_DROMORAPTOR_AZUL = B.rampa('0a2a34', '124250', '1e6274', '2e869c', '44a8be')
PATAS_DROMORAPTOR_AZUL = B.rampa('080c10', '10161c', '1c242c', '2e3842', '465462')
ANTEBRAZO_DROMORAPTOR_AZUL = B.rampa('0c1418', '141e24', '1e2c34', '2c3e48', '3e5462')
GARRA_DROMORAPTOR_AZUL = B.rampa('060708', '0a0c0e', '1c2024', '30363a', '485058')
MEMBRANA_DROMORAPTOR_AZUL = B.rampa('3a060a', '5c0a10', '821016', 'ac1a22', 'd62a34')
RADIO_DROMORAPTOR_AZUL = B.rampa('0a3e4c', '105c70', '1a829c', '2aaec8', '4cd0e8')
AMARILLO_DROMORAPTOR_AZUL = B.rampa('5a6010', '807a12', 'a89814', 'c0b02a', 'd4c440')
DIENTE_DROMORAPTOR_AZUL = B.rampa('8c826e', 'b8ac94', 'd2c8ae', 'e8e0c8', 'f2ecd8')
BOCA_DROMORAPTOR_AZUL = B.rampa('2e0a0c', '44100f', '5a1418', '741820', '8e1c24')
OJO_DROMORAPTOR_AZUL = {
    'a': B.H('f0c818'), 's': B.H('b89810'), 'k': B.H('081014'), 'n': B.H('04080c'),
    'm': B.H('0a4050'), 'M': B.H('052834'),
}


# ======================================================================================================================
#  Pintores
# ======================================================================================================================
def _piel_rgb_dromoraptor_azul(tw, th, s, t, cara):
    xs, ys = L._malla(tw, th)
    b = _manchas_dromoraptor_verde(xs, ys, s)
    b2 = _manchas_dromoraptor_verde(xs + 17, ys + 5, s + 101)
    a = _azar1(xs, ys, s * 7 + 5)
    vientre = (t + (b2 - 0.5) * 0.8) > 0.5
    v = 2.0 + (b > 0.62) * 1.0 - (b < 0.36) * 1.0 + ((a > 0.955) & (b > 0.45)) * 1.0
    if cara == 'abajo':
        v = v - 0.6
    azul = L.color_continuo(PIEL_DROMORAPTOR_AZUL, np.clip(np.round(v), 0, 4))
    mo = (_manchas_dromoraptor_verde(xs + 7, ys + 3, s + 211) < 0.2 + 0.25 * np.clip(t * 2, 0, 1)) & ~vientre
    vo = 1.6 + (b > 0.55) * 1.0
    azul = np.where(mo[..., None], L.color_continuo(OLIVA_DROMORAPTOR_AZUL, np.clip(np.round(vo), 0, 4)), azul)
    vv = 2.0 + (b > 0.6) * 1.0 - (b < 0.34) * 1.0 - (cara == 'abajo') * 0.8
    pardo = L.color_continuo(VIENTRE_DROMORAPTOR_AZUL, np.clip(np.round(vv), 0, 4))
    return np.where(vientre[..., None], pardo, azul)


def piel_dromoraptor_azul(nombre, modo='filas', verde=0.45, oliva=0.75, y0=None, y1=None, corte=None):
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        f = (ys + 0.5) / th
        if modo == 'verde':
            t = np.zeros((th, tw))
        elif modo == 'oliva':
            t = np.ones((th, tw))
        elif modo == 'cuello':
            g = (xs + 0.5) / tw
            if c == 'der':
                g = 1.0 - g
            if c in ('izq', 'der'):
                t = np.clip((g - 0.42) / 0.3, 0, 1)
            elif c == 'frente':
                t = np.ones((th, tw))
            else:
                t = np.zeros((th, tw))
        else:
            if c == 'arriba':
                t = np.zeros((th, tw))
            elif c == 'abajo':
                t = np.ones((th, tw))
            elif y0 is not None:
                y = y0 - f * (y0 - y1)
                t = np.clip((corte + 2.0 - y) / 4.0, 0, 1)
            else:
                t = np.clip((f - verde) / max(0.05, oliva - verde), 0, 1)
        return L._rgba(_piel_rgb_dromoraptor_azul(tw, th, s, t, c)), None
    return B.Pintor(nombre, fn)


def patas_dromoraptor_azul(nombre, paso=4, fase=1, rayas=True):
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s * 3 + 1)
        v = 1.4 + (a > 0.85) * 0.6 - (a < 0.1) * 0.5
        if c == 'arriba':
            v = v + 0.4
        elif c == 'abajo':
            v = v - 0.6
        elif rayas:
            v = np.where((ys + fase) % paso == 0, 3.4, v)
        return _tex_dromoraptor_verde(PATAS_DROMORAPTOR_AZUL, v), None
    return B.Pintor(nombre, fn)


def antebrazo_dromoraptor_azul(nombre):
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys // 3, s * 5 + 2)
        v = 1.6 + (a > 0.8) * 0.8 - (a < 0.15) * 0.6 + (c == 'arriba') * 0.5 - (c == 'abajo') * 0.6
        return _tex_dromoraptor_verde(ANTEBRAZO_DROMORAPTOR_AZUL, v), None
    return B.Pintor(nombre, fn)


def cabeza_dromoraptor_azul(nombre):
    def fn(tw, th, c, s):
        if c == 'abajo':
            return boca_dromoraptor_verde(nombre + '_b').fn(tw, th, c, s)
        rgb = _piel_rgb_dromoraptor_azul(tw, th, s, np.zeros((th, tw)), c)
        tex = L._rgba(rgb)
        if c in ('izq', 'der'):
            def pon(col, fila, letra):
                cc = col if c == 'izq' else tw - 1 - col
                if 0 <= cc < tw and 0 <= fila < th:
                    tex[fila, cc, :3] = np.round(OJO_DROMORAPTOR_AZUL[letra])
            for k in range(6):
                for f in range(1, 4):
                    pon(8 + k, f, 'm' if (k + f) % 3 else 'M')
            for k, letra in enumerate('akaa'):
                pon(4 + k, 2, letra)
                pon(4 + k, 3, 's' if letra == 'a' else 'k')
            pon(tw - 3, 1, 'n')
        return tex, None
    return B.Pintor(nombre, fn)


def mandibula_dromoraptor_azul(nombre):
    piel = piel_dromoraptor_azul(nombre + '_p', modo='oliva')
    boca = boca_dromoraptor_verde(nombre + '_b', base=2.6)

    def fn(tw, th, c, s):
        if c == 'arriba':
            return boca.fn(tw, th, c, s)
        tex, _ = piel.fn(tw, th, c, s)
        return tex, None
    return B.Pintor(nombre, fn)


def bloque_dromoraptor_azul(nombre):
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s * 3 + 9)
        v = 2.0 + (a > 0.88) * 1.0 - ((a < 0.14) & (ys > 1)) * 1.0
        if c == 'arriba':
            v = np.where((xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1), 4.0, 3.0 - (a < 0.12) * 1.0)
        else:
            v = np.where(xs == tw - 1, 1.0, v)
            v = np.where(ys == th - 1, 1.0, v)
            v = np.where(xs == 0, 3.0, v)
            v = np.where(ys == 0, 4.0, v)
        return _tex_dromoraptor_verde(AMARILLO_DROMORAPTOR_AZUL, v), None
    return B.Pintor(nombre, fn)


def cresta_dromoraptor_azul(nombre, ancho=2):
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        palo = xs >= tw - ancho
        bandera = (xs == tw - ancho - 1) & (ys < 2)
        dentro = palo | bandera
        a = _azar1(xs, ys, s * 5 + 7)
        v = 2.2 + (xs == tw - 1) * 0.8 - (ys > th * 0.7) * 0.6 + (a > 0.85) * 0.5
        return _tex_dromoraptor_verde(PIEL_DROMORAPTOR_AZUL, v, dentro), None
    return B.Pintor(nombre, fn)


def vela_dromoraptor_azul(nombre, rayos, asoma, colgando=False, resalte=0.3):
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c != 'frente':
            return tex, None
        U = xs + 0.5
        V = (ys + 0.5) if colgando else (th - 1 - ys) + 0.5
        P = [((ub * (tw - 1) + 0.5, vb * (th - 1) + 0.5), (ut * (tw - 1) + 0.5, vt * (th - 1) + 0.5))
             for (ub, vb), (ut, vt) in rayos]
        memb = np.zeros((th, tw), bool)
        hasta = np.ones((th, tw))
        for k in range(len(P) - 1):
            (a0, a1), (b0, b1) = P[k], P[k + 1]
            la, lb = math.dist(a0, a1), math.dist(b0, b1)
            pa, pb = asoma[k]
            fa, fb = max(0.0, 1 - pa / la), max(0.0, 1 - pb / lb)
            qa = (a0[0] + (a1[0] - a0[0]) * fa, a0[1] + (a1[1] - a0[1]) * fa)
            qb = (b0[0] + (b1[0] - b0[0]) * fb, b0[1] + (b1[1] - b0[1]) * fb)
            mk = _poligono_dromoraptor_verde(U, V, [a0, qa, qb, b0])
            memb |= mk
            borde_v = qa[1] + (qb[1] - qa[1]) * np.clip((U - qa[0]) / ((qb[0] - qa[0]) or 1e-9), 0, 1)
            hasta = np.where(mk, np.clip(V / np.maximum(borde_v, 1.0), 0, 1), hasta)
        a = _azar1(xs, ys, s * 7 + 3)
        bl = _manchas_dromoraptor_verde(xs, ys, s + 59)
        vm = 2.0 + 1.7 * hasta + (a > 0.86) * 0.6 - (a < 0.12) * 0.6
        fu = (hasta > 0.72) & (bl > 1.0 - resalte)
        vm = np.where(fu, 4.0, vm)
        tex = _tex_dromoraptor_verde(MEMBRANA_DROMORAPTOR_AZUL, vm, memb)
        for (p0, p1) in P:
            for (i, j, t) in _linea_dromoraptor_verde(p0, p1):
                col = i
                fila = j if colgando else th - 1 - j
                if 0 <= col < tw and 0 <= fila < th:
                    vr = 2.0 + 2.0 * t + (_azar1(col, fila, s + 3) > 0.8) * 0.5
                    tex[fila, col, :3] = np.round(L.color_continuo(RADIO_DROMORAPTOR_AZUL,
                                                                   np.array([float(np.clip(round(vr), 0, 4))]))[0])
                    tex[fila, col, 3] = 255
        return tex, None
    return B.Pintor(nombre, fn)


# ======================================================================================================================
#  Retexturizado y accesorios
# ======================================================================================================================
def retexturar_dromoraptor_azul(m):
    for k in range(8):
        y0, y1 = _franja_dromoraptor_verde(m, 'cuerpo', k)
        _reemplazar_dromoraptor_verde(m, 'cuerpo', k, piel_dromoraptor_azul(f'piel_tronco_{ID}_{k}', y0=y0, y1=y1, corte=16.5))
    _reemplazar_dromoraptor_verde(m, 'cuerpo', 8, piel_dromoraptor_azul(f'piel_cuello_{ID}', modo='cuello'))

    _reemplazar_dromoraptor_verde(m, 'cabeza', 0, cabeza_dromoraptor_azul(f'cabeza_{ID}'))
    _reemplazar_dromoraptor_verde(m, 'cabeza', 1, dientes_dromoraptor_verde(f'dientes_arriba_{ID}', arriba=True))
    _reemplazar_dromoraptor_verde(m, 'mandibula', 0, mandibula_dromoraptor_azul(f'mandibula_{ID}'))
    _reemplazar_dromoraptor_verde(m, 'mandibula', 1, dientes_dromoraptor_verde(f'dientes_abajo_{ID}', arriba=False, encia=1, largos=(1, 2)))

    for parte in ('cola', 'cola2'):
        for k in range(2):
            _reemplazar_dromoraptor_verde(m, parte, k, piel_dromoraptor_azul(f'piel_{parte}_{ID}_{k}', verde=0.4, oliva=0.8))

    garra_pie = R.garras_lamina(f'garra_pie_{ID}', GARRA_DROMORAPTOR_AZUL, n=1, curva=0.9, adelante=True)
    hoz = R.garras_lamina(f'hoz_{ID}', GARRA_DROMORAPTOR_AZUL, n=1, curva=1.4, adelante=True)
    gancho = R.garras_lamina(f'gancho_{ID}', GARRA_DROMORAPTOR_AZUL, n=1, curva=1.7, adelante=True)

    for ld in ('i', 'd'):
        _reemplazar_dromoraptor_verde(m, f'pierna_{ld}', 0, piel_dromoraptor_azul(f'muslo_{ID}', verde=0.35, oliva=0.7))
        _reemplazar_dromoraptor_verde(m, f'cana_{ld}', 0, patas_dromoraptor_azul(f'espinilla_{ID}', paso=4, fase=2))
        _reemplazar_dromoraptor_verde(m, f'cana_{ld}', 1, patas_dromoraptor_azul(f'cana_{ID}', paso=4, fase=1))
        _reemplazar_dromoraptor_verde(m, f'cana_{ld}', 2, patas_dromoraptor_azul(f'pie_{ID}', rayas=False))
        for k in (3, 4, 5):
            _reemplazar_dromoraptor_verde(m, f'cana_{ld}', k, garra_pie)
        _reemplazar_dromoraptor_verde(m, f'cana_{ld}', 6, hoz)

        _reemplazar_dromoraptor_verde(m, f'brazo_{ld}', 0, piel_dromoraptor_azul(f'brazo_{ID}', modo='verde'))
        _reemplazar_dromoraptor_verde(m, f'brazo_{ld}', 1, antebrazo_dromoraptor_azul(f'antebrazo_{ID}'))
        for k in (2, 3):
            _reemplazar_dromoraptor_verde(m, f'brazo_{ld}', k, gancho)


def bloque_y_crestas_dromoraptor_azul(m):
    px = 1.0 / TAM
    c = CABEZA_DROMORAPTOR_VERDE
    largo, ancho, alto = 6.0, 6.0, 7.0
    z1 = c['frente'] - px
    z0 = z1 - largo
    m.caja('cabeza', (0, c['techo'] + alto / 2, (z0 + z1) / 2), (ancho, alto, largo),
           bloque_dromoraptor_azul(f'bloque_{ID}'), caras={'abajo': None})
    cresta = cresta_dromoraptor_azul(f'cresta_{ID}')
    w = 3 * px
    zc = z0 - px - 2 * px
    for k, sobre in enumerate((alto + px, alto * 0.62)):
        z = zc - k * 3 * px + px / 2
        M = _sagital_dromoraptor_verde(z, c['techo'] - px, inclina=-12)
        _lamina_dromoraptor_verde(m, 'cabeza', M, w, sobre + px, cresta)


ABANICOS_DROMORAPTOR_AZUL = (
    ('abanico_cola', 'cola2', -33.0, -18.0, 22.2, 15.2,
     [((0.20, 0.0), (0.0, 0.34)), ((0.48, 0.0), (0.24, 0.74)), ((0.72, 0.0), (0.47, 0.92)), ((1.0, 0.0), (0.70, 1.0))],
     [(0.6, 3.5), (1.0, 3.0), (1.0, 2.5)]),
    ('abanico_cadera', 'cola', -17.0, -9.0, 22.8, 8.6,
     [((0.25, 0.0), (0.0, 0.45)), ((0.62, 0.0), (0.36, 1.0)), ((1.0, 0.0), (0.80, 0.82))],
     [(0.6, 3.0), (3.0, 1.0)]),
    ('abanico_lomo', 'cuerpo', -7.0, 7.0, 23.4, 14.2,
     [((0.30, 0.0), (0.0, 0.50)), ((0.40, 0.0), (0.20, 0.86)), ((0.50, 0.0), (0.50, 1.0)), ((0.60, 0.0), (0.80, 0.86)),
      ((0.70, 0.0), (1.0, 0.50))],
     [(0.6, 3.0), (0.8, 3.0), (3.0, 0.8), (3.0, 0.6)]),
)


def abanicos_dromoraptor_azul(m):
    for nombre, padre, z0, z1, y, alto, rayos, asoma in ABANICOS_DROMORAPTOR_AZUL:
        m.parte(nombre, padre, (0, y, (z0 + z1) / 2))
        vela = vela_dromoraptor_azul(f'{nombre}_{ID}', rayos, asoma)
        _lamina_dromoraptor_verde(m, nombre, _sagital_dromoraptor_verde((z0 + z1) / 2, y), z1 - z0, alto, vela)


def aletas_brazos_dromoraptor_azul(m):
    rayos = [((0.02, 0.0), (0.0, 0.92)), ((0.21, 0.0), (0.15, 1.0)), ((0.40, 0.0), (0.33, 0.95)),
             ((0.59, 0.0), (0.53, 1.0)), ((0.78, 0.0), (0.74, 0.94)), ((0.97, 0.0), (0.96, 0.98))]
    asoma = [(1.0, 3.0)] * 5
    aleta = vela_dromoraptor_azul(f'aleta_brazo_{ID}', rayos, asoma, colgando=True, resalte=0.25)
    for lado, ld in R.LADOS:
        z0, z1 = 3.6, 17.2
        arriba, abajo = 8.6, 0.4
        M = T(lado * 5.6, abajo, (z0 + z1) / 2) @ B.girar((0, -90, 0))
        _lamina_dromoraptor_verde(m, f'brazo_{ld}', M, z1 - z0, arriba - abajo, aleta)


# ======================================================================================================================
#  Animaciones
# ======================================================================================================================
from quiu.dromoraptor_verde import anims_dromoraptor_verde


# ======================================================================================================================
#  Construcción final
# ======================================================================================================================
def construir():
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0
    R.dromoraptor(m, piel_dromoraptor_azul(f'piel_{ID}'), patas_dromoraptor_azul(f'patas_{ID}'),
                  PIEL_DROMORAPTOR_AZUL, (MEMBRANA_DROMORAPTOR_AZUL, RADIO_DROMORAPTOR_AZUL),
                  (cresta_dromoraptor_azul(f'cresta0_{ID}'), bloque_dromoraptor_azul(f'bloque0_{ID}')),
                  DIENTE_DROMORAPTOR_AZUL)
    retexturar_dromoraptor_azul(m)
    quitar_dromoraptor_verde(m)
    bloque_y_crestas_dromoraptor_azul(m)
    abanicos_dromoraptor_azul(m)
    aletas_brazos_dromoraptor_azul(m)
    m.anims.clear()
    anims_dromoraptor_verde(m)
    return m


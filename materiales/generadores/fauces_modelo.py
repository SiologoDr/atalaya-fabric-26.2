"""
Bocetos de tres jefes hechos «de la cabeza hacia fuera» (12-10-2026). Juan, tras
las Cuatro Materias: «creo que nos estamos alejando del objetivo de Espinara y
Ofidia, sus disenos de como se ven». Lo que tienen las dos y aqui manda:

  - la cabeza es la imagen: grande, de frente, con una boca enorme abierta;
  - la boca encendida por dentro con UN solo color neon, que alumbra la escena;
  - cosas que salen alrededor de la cabeza y la enmarcan (petalos; senuelos y capucha);
  - un cuerpo oscuro, casi de un color, que se alza; colosal y en plano bajo.

  A  Lutia, el Cisne de Luto            neon CIAN
     cisne negro + boca de lamprea + velos de luto + corona de lirios; las alas, en
     abanico detras de la cabeza, acaban en encaje
  B  Farolera, la Arana de los Farolillos   neon AMBAR
     arana + farolillo de papel + senuelo de pez abisal: el abdomen es un farol que
     alumbra la cueva; las patas de delante, en alto, enmarcan los colmillos
  C  Otonara, la Dragona de Hojarasca    neon CARMESI
     dragona de corteza + craneo de ciervo con astas de rama + alas de hojas de
     otono; por dentro arde como una chimenea

Mismas cajas con las caras pintadas que bestias_modelo (8 px por bloque).
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import (cubo, caja_c, viga, redondo, pua, garra, dientes, punto, _ruido, _tonos, _luz, _imagen,
                            _emis, _paseo, p_hueso, p_diente)

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 16

# ----------------------------------------------------------------------
#  Rampas
# ----------------------------------------------------------------------
LUTO = _r('060508', '110d16', '1e1828', '302840', '6e6e88')
ENCAJE = _r('1e1e24', '3a3a44', '62626e', '9a9aa6', 'cfcfd8')
PICO = _r('3a0606', '6a0c0c', '9a1616', 'c42a22', 'e8d8c8')
CARNE = _r('140306', '2c0810', '4a121c', '6e2430', '98404c')
LIRIO = _r('8a9a8a', 'b8c4b8', 'dce6dc', 'f0f6f0', 'fcfffc')

QUIT_A = _r('080605', '120e0a', '1e1710', '2e2318', '463422')
ORILLA = _r('3a1a06', '6a3410', '9a5420', 'd48a3a', 'f4c070')
FAROL = _r('3a1604', '8a3e0a', 'd8781a', 'ffb840', 'fff0b0')
SEDA = _r('8a8478', 'b8b2a6', 'dcd8ce', 'eeebe4', 'fbfaf6')
COLMILLO = _r('120e0c', '4a4236', 'a89e86', 'ded6c2', 'f6f2e6')

CORTEZA = _r('0c0907', '1a140f', '2a2018', '3e3024', '584634')
HOJA_R = _r('2a0604', '5a0e08', '8e1a0e', 'c02e18', 'e85a36')
HOJA_N = _r('3a1604', '6e3008', 'a8520e', 'dc8020', 'f6b04c')
HOJA_O = _r('3a2a04', '6e520a', 'a88414', 'd8b032', 'f4da78')
RAMA = _r('100c08', '1e1610', '2e2218', '42321f', '5a462e')
CARMESI = ('ffe0c0', 'ff2a1a')


# ----------------------------------------------------------------------
#  Pintores de Lutia
# ----------------------------------------------------------------------
def p_pluma_luto(tw, th, cara, s):
    """Plumas de luto: negras con reflejo violeta, al tresbolillo, con el canto
    algo mas claro y alguna punta de plata."""
    rng = random.Random(s)
    ys, xs = np.mgrid[0:th, 0:tw]
    ancho, alto = 4, 5
    fila = ys // alto
    u = (xs + np.where(fila % 2 == 1, 2, 0)) % ancho - (ancho - 1) / 2
    v = ys % alto
    borde = (alto - 1) - np.abs(u) * 1.0
    idx = np.where(v > borde, 3, np.where(v > borde - 1.0, 2, np.where(np.abs(u) < 0.6, 2, 1)))
    plata = (idx == 3) & (_ruido(tw, th, s, 2.0) > 0.68)
    idx[plata] = 4
    idx[(_ruido(tw, th, s + 1, 3.0) < 0.25) & (idx < 3)] = 0
    return _imagen(_luz(idx, cara, 0), LUTO), None


def p_encaje(tw, th, cara, s):
    """Encaje de luto: malla de rombos con flores tejidas; lo demas, agujero."""
    t = np.zeros((th, tw, 4), np.uint8)
    ys, xs = np.mgrid[0:th, 0:tw]
    malla = ((xs + ys) % 4 == 0) | ((xs - ys) % 4 == 0)
    flores = ((xs % 8 - 3.5) ** 2 + (ys % 8 - 3.5) ** 2) <= 3.0
    m = malla | flores
    idx = np.where(flores, 2, 1)
    img = _imagen(idx, ENCAJE)
    t[m] = img[m]
    if cara not in ('arriba', 'abajo') and th > 4:
        t[-1, :] = (0, 0, 0, 0)
        t[-2, ::2] = (0, 0, 0, 0)
    return t, None


def p_pico(tw, th, cara, s):
    """El pico del cisne negro: rojo, con una banda palida cerca de la punta."""
    idx = 2 + (_ruido(tw, th, s, 2.5) > 0.55).astype(int)
    ys = np.arange(th)[:, None] * np.ones((1, tw))
    idx[(ys > th * 0.72) & (ys < th * 0.84)] = 4
    return _imagen(_luz(idx, cara), PICO), None


def p_carne(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.8)
    return _imagen(_luz(idx, cara), CARNE), None


def p_disco(tw, th, cara, s, glow=('f4ffff', '6ad8ff'), rampa=CARNE):
    """El disco de la boca (lamprea): anillos de dientes sobre la carne oscura y la
    luz en el centro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    cx, cy = (tw - 1) / 2, (th - 1) / 2
    d = np.hypot((xs - cx) / max(tw / 2, 1), (ys - cy) / max(th / 2, 1))
    ang = np.arctan2(ys - cy, xs - cx)
    idx = np.where(d < 1.0, 1, 0)
    dientes_m = np.zeros((th, tw), bool)
    for r0, n in ((0.42, 10), (0.62, 14), (0.82, 18)):
        dientes_m |= (np.abs(d - r0) < 0.07) & ((np.floor(ang / (TAU / (2 * n))) % 2) == 0)
    tex = _imagen(idx, rampa)
    tex[dientes_m] = (232, 228, 214, 255)
    c1, c2 = nm._hex(glow[0]), nm._hex(glow[1])
    centro = d < 0.3
    for y, x in zip(*np.nonzero(centro)):
        k = d[y, x] / 0.3
        tex[y, x] = (*qm._mezcla(c1, c2, k), 255)
    return tex, _emis(tex, centro, 230)


def p_boca_luz(tw, th, cara, s, c1='f4ffff', c2='38c8f0', oscuro='06283a'):
    """El interior de la boca encendido: luz que sale de dentro, mas fuerte hacia la
    garganta, con el borde oscuro y las encias marcadas."""
    ys, xs = np.mgrid[0:th, 0:tw]
    v = ys / max(th - 1, 1)
    u = np.abs(xs - (tw - 1) / 2) / max(tw / 2, 1)
    k = np.clip(0.15 + v * 0.75 + u * 0.35, 0, 1)
    a, b, o = nm._hex(c1), nm._hex(c2), nm._hex(oscuro)
    t = np.zeros((th, tw, 4), np.uint8)
    for y in range(th):
        for x in range(tw):
            kk = k[y, x]
            c = qm._mezcla(a, b, kk / 0.7) if kk < 0.7 else qm._mezcla(b, o, (kk - 0.7) / 0.3)
            t[y, x] = (*c, 255)
    t[(xs % 3 == 0) & (u > 0.75)] = (*o, 255)
    return t, _emis(t, k < 0.85, 235)


def p_boca_ambar(tw, th, cara, s):
    return p_boca_luz(tw, th, cara, s, 'fff2c0', 'ff9a1e', '3a1404')


def p_lirio(tw, th, cara, s):
    idx = np.full((th, tw), 3)
    xs = np.arange(tw)
    idx[:, np.abs(xs - (tw - 1) / 2) < 0.6] = 2
    idx[:1, :] = 4
    tex = _imagen(_luz(idx, cara), LIRIO)
    return tex, _emis(tex, idx >= 3, 60)


def p_ojo_rojo(tw, th, cara, s):
    return qm._emisivo('ffd0c0', 'ff1a1a', max(2, tw), max(2, th)), None


def p_luz_luna(tw, th, cara, s):
    return qm._emisivo('f8ffff', '7ae4ff', max(2, tw), max(2, th)), None


# ----------------------------------------------------------------------
#  Pintores de Farolera
# ----------------------------------------------------------------------
def p_quitina_a(tw, th, cara, s):
    """Quitina de arana: placas oscuras con la junta negra y el canto naranja a la luz."""
    n = max(2, tw * th // 50)
    d1, d2, ic, sx, sy = qm._celdas(s, n, max(tw, 2), max(th, 2))
    d1, d2, sx, sy = d1[:th, :tw], d2[:th, :tw], sx[:th, :tw], sy[:th, :tw]
    ed = d2 - d1
    idx = np.where(ed < 0.8, 0, np.where(ed < 1.6, 2, 1))
    tex = _imagen(_luz(idx, cara, 0), QUIT_A)
    canto = (ed >= 0.8) & (ed < 1.5) & ((sx + sy) < 0)
    tex[canto] = (*ORILLA[2], 255)
    return tex, None


def p_farol_ar(tw, th, cara, s):
    """El abdomen-farol: ambar que brilla, con las varillas oscuras del farolillo y
    las sombras de los huevos dentro. Las tapas, de quitina."""
    if cara in ('arriba', 'abajo'):
        return p_quitina_a(tw, th, cara, s)
    rng = random.Random(s)
    ys, xs = np.mgrid[0:th, 0:tw]
    v = _ruido(tw, th, s, 3.0)
    idx = np.where(v > 0.55, 4, 3)
    idx[(xs % 7) == 0] = 1
    for _ in range(max(1, tw * th // 90)):
        cx, cy, r = rng.uniform(0, tw), rng.uniform(1, th - 1), rng.uniform(0.8, 1.6)
        idx[(np.hypot(xs - cx, ys - cy) < r) & (idx > 0)] = 2
    tex = _imagen(idx, FAROL)
    return tex, _emis(tex, idx >= 2, 185)


def p_seda(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.4) + 1
    tex = _imagen(np.clip(idx, 0, 4), SEDA)
    return tex, _emis(tex, idx >= 4, 40)


def p_colmillo(tw, th, cara, s):
    """Colmillo: hueso claro en la raiz y negro en la punta (la punta abajo)."""
    ys = np.arange(th)[:, None] * np.ones((1, tw))
    idx = np.clip(4 - (ys / max(th, 1) * 4.2).astype(int), 0, 4)
    if cara in ('arriba',):
        idx[:] = 4
    return _imagen(idx, COLMILLO), None


def p_ojo_ambar(tw, th, cara, s):
    return qm._emisivo('ffd070', 'c84a08', max(2, tw), max(2, th)), None


def p_ojo_negro(tw, th, cara, s):
    """Ojo grande de arana: negro pulido con un punto de brillo y un hilo de ambar
    en el canto."""
    ys, xs = np.mgrid[0:th, 0:tw]
    cx, cy = (tw - 1) / 2, (th - 1) / 2
    d = np.hypot((xs - cx) / max(tw / 2, 1), (ys - cy) / max(th / 2, 1))
    t = np.zeros((th, tw, 4), np.uint8)
    t[:] = (8, 6, 7, 255)
    t[d > 0.86] = (90, 46, 14, 255)
    t[(np.abs(xs - cx * 0.62) < max(1, tw / 12)) & (np.abs(ys - cy * 0.55) < max(1, th / 12))] = (246, 238, 226, 255)
    return t, None


def p_disco_ambar(tw, th, cara, s):
    return p_disco(tw, th, cara, s, glow=('fff4c0', 'ff8a10'), rampa=_r('0e0604', '1e0e08', '3a1a0c', '5a2a14', '7a3c1e'))


def p_pelusa(tw, th, cara, s):
    return bm.p_pelo(tw, th, cara, s, _r('0a0806', '16120e', '241c14', '3a2c1e', '5a4430'))


# ----------------------------------------------------------------------
#  Pintores de Otonara
# ----------------------------------------------------------------------
def p_corteza(tw, th, cara, s):
    """Corteza vieja: surcos a lo largo y, en alguno, la brasa de dentro (emisivo)."""
    rng = random.Random(s)
    ys, xs = np.mgrid[0:th, 0:tw]
    v = _ruido(tw, th, s, 3.0)
    idx = np.where(v > 0.55, 3, 2)
    surco = ((xs + 1.5 * np.sin(ys * 0.35 + s)) % 4) < 1.0
    idx[surco] = 1
    idx[surco & (_ruido(tw, th, s + 2, 2.0) > 0.7)] = 0
    tex = _imagen(_luz(idx, cara), CORTEZA)
    brasa = surco & (_ruido(tw, th, s + 9, 3.0) > 0.86)
    if brasa.any():
        tex[brasa] = (255, 60, 30, 255)
        return tex, _emis(tex, brasa, 200)
    return tex, None


def _hoja(tw, th, s, rampa):
    """Hoja de otono vista de frente (el largo, en vertical): forma de lanza, nervio
    en medio y nervios de lado; fuera de la forma, transparente."""
    t = np.zeros((th, tw, 4), np.uint8)
    ys, xs = np.mgrid[0:th, 0:tw]
    v = ys / max(th - 1, 1)
    u = (xs - (tw - 1) / 2) / max(tw / 2, 1)
    ancho = np.sin(np.pi * np.clip(v, 0, 1)) ** 0.8
    dentro = np.abs(u) <= ancho * 0.98
    idx = 2 + (_ruido(tw, th, s, 2.0) > 0.55).astype(int)
    idx[np.abs(u) < 0.12] = 4
    idx[((v * 9 + np.abs(u) * 3) % 1.6 < 0.3) & (np.abs(u) > 0.15)] = 3
    idx[np.abs(u) > ancho * 0.8] = 1
    img = _imagen(idx, rampa)
    t[dentro] = img[dentro]
    return t


def p_hoja_r(tw, th, cara, s):
    return _hoja(tw, th, s, HOJA_R), None


def p_hoja_n(tw, th, cara, s):
    return _hoja(tw, th, s, HOJA_N), None


def p_hoja_o(tw, th, cara, s):
    return _hoja(tw, th, s, HOJA_O), None


def p_rama(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.5)
    idx[:, ::3] -= 1
    return _imagen(np.clip(_luz(idx, cara), 0, 4), RAMA), None


def p_brasa_roja(tw, th, cara, s):
    return qm._emisivo('ffd8b0', 'ff2a1a', max(2, tw), max(2, th), oscuro='5a0606', semilla=s % 5), None


def p_musgo(tw, th, cara, s):
    return bm.p_musgo(tw, th, cara, s)


for _p in (p_ojo_rojo, p_luz_luna, p_ojo_ambar, p_brasa_roja):
    bm.PLENOS.add(_p)


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def tubo(out, ctrl, radios, pintor, n=14, pasos=3, semilla=0):
    """Un cuerpo redondeado (a escalones de pixel) a lo largo de una curva suave.
    Devuelve los puntos y las tangentes de la curva."""
    pts, tans = em.catmull(ctrl, n)
    for i in range(n - 1):
        p0, p1 = pts[i], pts[i + 1]
        k = i / (n - 2)
        r = radios[0] + (radios[1] - radios[0]) * k
        L = float(np.linalg.norm(p1 - p0))
        M = em.marco(p0, p1 - p0)
        for w, h in _pasos(r, pasos):
            cubo(out, M, -w, -h, -0.08, 2 * w, 2 * h, L + 0.16, pintor, semilla=semilla + i % 3)
    return pts, tans


def _pasos(r, n):
    k = 1.0 / math.cos(math.radians(90 / (n + 1)))
    return [(r * k * math.cos(math.radians(90 * (i + 1) / (n + 1))), r * k * math.sin(math.radians(90 * (i + 1) / (n + 1))))
            for i in range(n)]


def ovoide_z(out, M, rx, ry, rz, pintor, capas=8, pasos=3, semilla=0):
    """Un ovoide a lo largo de la z local, en rodajas redondeadas a escalones."""
    for k in range(capas):
        z0 = -rz + 2 * rz * k / capas
        z1 = z0 + 2 * rz / capas
        zm = (z0 + z1) / 2
        f = math.sqrt(max(0.05, 1 - (zm / rz) ** 2))
        for w, h in _pasos(1.0, pasos):
            cubo(out, M, -w * rx * f, -h * ry * f, z0, 2 * w * rx * f, 2 * h * ry * f, z1 - z0 + 0.02, pintor, semilla=semilla + k % 3)


def hoja(out, M, largo, ancho, pintor, semilla=0):
    """Una hoja plana: el largo por la z local, la cara mirando a la y."""
    cubo(out, M, -ancho / 2, -0.04, 0, ancho, 0.08, largo, pintor, semilla=semilla)


def ejes(p, ex, ey):
    ex = np.asarray(ex, float)
    ex = ex / np.linalg.norm(ex)
    ey = np.asarray(ey, float)
    ey = ey - ex * (ey @ ex)
    ey = ey / np.linalg.norm(ey)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = ex, ey, np.cross(ex, ey), p
    return M


# ======================================================================
#  A · LUTIA, el Cisne de Luto (neon cian)
# ======================================================================
def lutia(abre=62.0, semilla=1):
    out = []
    rng = random.Random(semilla)
    # el cuerpo, que flota con la mitad bajo el agua
    for (y0, y1, rx, rz) in ((-0.4, 1.0, 3.3, 4.6), (1.0, 2.0, 3.1, 4.3), (2.0, 2.8, 2.5, 3.7), (2.8, 3.3, 1.6, 2.7)):
        redondo(out, vr.T(0, 0, -0.8), y0, y1, rx, rz, p_pluma_luto, n=4, semilla=1)
    for k in range(7):                                         # la cola levantada
        a = (k - 3) * 14
        M = vr.T(0, 2.4, -4.9) @ vr.Ry(a * D) @ vr.Rx(-120 * D)
        cubo(out, M, -0.35, 0, -0.05, 0.7, 1.6 + 0.2 * (3 - abs(k - 3)), 0.1, p_pluma_luto, semilla=2)
    # el cuello en ese, alzado, y la cabeza que se lanza hacia delante
    ctrl = [(0, 2.0, 2.4), (0, 4.6, 4.2), (0, 7.4, 4.0), (0, 10.0, 2.8), (0, 11.9, 3.2), (0, 12.3, 4.6)]
    pts, tans = tubo(out, ctrl, (1.35, 0.85), p_pluma_luto, n=18, pasos=3, semilla=3)
    Mh = em.marco(pts[-1] + np.array((0, 0.15, 0.55)), (0, -0.3, 1.0)) @ np.diag([1.8, 1.8, 1.8, 1.0])
    redondo(out, Mh @ vr.T(0, -0.1, -0.25), -0.8, 0.85, 1.0, 1.0, p_pluma_luto, n=3, semilla=4)     # la cabeza
    # el pico rojo, abierto de par en par como unas fauces: encendido por dentro, con
    # dientes de lamprea en los bordes y la boca de lamprea al fondo de la garganta
    Ms = Mh @ vr.T(0, 0.2, 0.55) @ vr.Rx(-abre * 0.42 * D)
    M = Ms
    for k, (w, h, l, curva) in enumerate(((1.15, 0.42, 1.1, 6), (0.95, 0.36, 1.0, 8), (0.72, 0.3, 0.9, 12), (0.46, 0.24, 0.6, 26))):
        cubo(out, M, -w / 2, -h, 0.0, w, h, l + 0.04, p_pico, caras={'abajo': p_boca_luz}, semilla=6 + k)
        for j in range(3):
            for sx in (1, -1):
                pua(out, M @ vr.T(sx * (w / 2 - 0.08), -h, 0.2 + j * l / 3) @ vr.Rx(180 * D) @ vr.Rx(-30 * D), 0.05, 0.3 - k * 0.04, p_diente,
                    semilla=10 + j)
        M = M @ vr.T(0, 0, l) @ vr.Rx(curva * D)
    cubo(out, M, -0.18, -0.3, 0.0, 0.36, 0.3, 0.3, bm.p_garra_ave, semilla=14)                 # la una del pico
    Mi = Mh @ vr.T(0, -0.45, 0.45) @ vr.Rx(abre * 0.6 * D)
    M = Mi
    for k, (w, h, l) in enumerate(((1.0, 0.34, 1.05), (0.8, 0.3, 0.95), (0.56, 0.24, 0.8))):
        cubo(out, M, -w / 2, 0.0, 0.0, w, h, l + 0.04, p_pico, caras={'arriba': p_boca_luz}, semilla=15 + k)
        for j in range(3):
            for sx in (1, -1):
                pua(out, M @ vr.T(sx * (w / 2 - 0.08), h, 0.2 + j * l / 3) @ vr.Rx(30 * D), 0.05, 0.26 - k * 0.04, p_diente, semilla=18 + j)
        M = M @ vr.T(0, 0, l) @ vr.Rx(-6 * D)
    cubo(out, Mh, -0.62, -0.62, 0.42, 1.24, 1.0, 0.1, p_disco, semilla=21)                     # la garganta
    for k in range(10):
        a = k * TAU / 10
        pua(out, Mh @ vr.T(math.cos(a) * 0.42, -0.12 + math.sin(a) * 0.38, 0.5) @ vr.Rz(a - TAU / 4) @ vr.Rx(70 * D), 0.05, 0.24, p_diente,
            semilla=22)
    for s in (1, -1):                                         # los ojos rojos
        cubo(out, Mh, s * 0.98 - 0.05, 0.2, -0.2, 0.1, 0.22, 0.34, p_ojo_rojo, semilla=11)
    # la corona de lirios y el velo de luto que cae por el cuello
    for k in range(6):
        a = (k / 5 - 0.5) * 200 * D
        Ml = Mh @ vr.T(math.sin(a) * 0.9, 0.75 + math.cos(a) * 0.25, -0.35 - abs(math.sin(a)) * 0.3)
        for j in range(6):
            cubo(out, Ml @ vr.Rz(j * 60 * D) @ vr.Rx(-40 * D), -0.12, 0, -0.03, 0.24, 0.55, 0.06, p_lirio, semilla=12)
        cubo(out, Ml, -0.06, -0.06, -0.06, 0.12, 0.25, 0.12, p_luz_luna, semilla=13)
    nuca = punto(Mh, (0, 0.55, -0.9))
    for k, (x, largo, caida) in enumerate(((-0.45, 2.6, 50), (0.0, 3.4, 42), (0.45, 2.8, 52), (-0.8, 1.8, 62), (0.8, 2.0, 60))):
        M = ejes(nuca + np.array((x, 0, 0)), (1, 0, 0), (0, 0.35, -1)) @ vr.Rx(-caida * 0.3 * D)
        cubo(out, M, -0.2, 0, -0.05, 0.4, largo * 0.55, 0.1, p_pluma_luto, semilla=23)
        M2 = M @ vr.T(0, largo * 0.55, 0) @ vr.Rx(caida * D)
        cubo(out, M2, -0.17, 0, -0.04, 0.34, largo * 0.55, 0.08, p_pluma_luto, semilla=24)
        cubo(out, M2 @ vr.T(0, largo * 0.55 - 0.05, 0), -0.12, 0, -0.04, 0.24, 0.35, 0.08, p_luz_luna, semilla=25)
    # las alas: alzadas detras del cuello como dos abanicos de plumas solapadas, con las
    # puntas de encaje
    for s in (1, -1):
        hom = np.array((s * 2.2, 2.8, 0.2))
        arco = [hom, np.array((s * 3.6, 5.2, -0.4)), np.array((s * 4.0, 7.6, -1.2)), np.array((s * 3.4, 9.6, -2.0))]
        apts, atans = em.catmull(arco, 12)
        centro = np.array((s * 1.0, 4.6, -1.2))
        viga_pts = apts
        for i in range(len(viga_pts) - 1):
            viga(out, viga_pts[i], viga_pts[i + 1], 0.7, 0.7, p_pluma_luto, extra=0.15, semilla=15)
        for fila, (largo0, largo1, atras, ancho) in enumerate(((1.6, 2.2, 0.0, 1.3), (2.6, 3.6, -0.18, 1.25), (3.4, 5.4, -0.36, 1.2))):
            for i in range(0, len(apts), 1):
                t_ = i / (len(apts) - 1)
                base = apts[i] + np.array((0, 0, atras))
                radial = base - centro
                radial = radial / np.linalg.norm(radial)
                tang = atans[i] / np.linalg.norm(atans[i])
                M = ejes(base, tang, radial) @ vr.Rz(-s * (6 + 4 * fila) * D)
                largo = largo0 + (largo1 - largo0) * t_
                cubo(out, M, -ancho / 2, -0.2, -0.07, ancho, largo, 0.14, p_pluma_luto, semilla=16 + fila)
    # lirios sueltos en el agua, delante
    return out, {'cabeza': Mh}


# ======================================================================
#  B · FAROLERA, la Arana de los Farolillos (neon ambar)
# ======================================================================
def farolera(abre=1.0, semilla=2):
    out = []
    rng = random.Random(semilla)
    # el cefalotorax acorazado
    for (y0, y1, rx, rz) in ((2.6, 3.6, 2.2, 2.6), (3.6, 4.6, 2.5, 2.9), (4.6, 5.3, 1.9, 2.3), (5.3, 5.6, 1.1, 1.4)):
        redondo(out, vr.T(0, 0, 1.6), y0, y1, rx, rz, p_quitina_a, n=4, semilla=1)
    # la cara: ocho ojos pequenos de ambar en dos filas, los queliceros muy abiertos y encendidos
    # por dentro, los colmillos y la boca
    for (x, y, r) in ((-0.42, 5.2, 0.22), (0.42, 5.2, 0.22), (-1.0, 5.05, 0.17), (1.0, 5.05, 0.17),
                      (-0.75, 5.65, 0.14), (0.75, 5.65, 0.14), (-0.25, 5.75, 0.12), (0.25, 5.75, 0.12)):
        redondo(out, vr.T(x, y - r, 4.25 - abs(x) * 0.35), 0, 2 * r, r, r, p_ojo_ambar, n=2, semilla=2)
    for s in (1, -1):
        Mq = vr.T(s * 1.0, 4.2, 4.0) @ vr.Ry(s * 34 * abre * D) @ vr.Rx(16 * D)
        cubo(out, Mq, -0.72, -2.6, -0.62, 1.44, 2.7, 1.25, p_pelusa, caras={'izq' if s > 0 else 'der': p_boca_ambar}, semilla=3)
        p0 = punto(Mq, (0, -2.6, 0.15))
        p1 = p0 + np.array((s * 0.25, -0.7, 0.75))
        p2 = p1 + np.array((-s * 0.75, -0.45, 0.1))
        viga(out, p0, p1, 0.46, 0.46, p_quitina_a, semilla=4)
        viga(out, p1, p2, 0.32, 0.32, bm.p_garra_ave, semilla=5)
        hom = np.array((s * 1.5, 3.3, 3.9))                    # los pedipalpos
        p1 = hom + np.array((s * 0.7, -0.3, 1.0))
        p2 = p1 + np.array((s * 0.1, -1.0, 0.5))
        viga(out, hom, p1, 0.36, 0.36, p_quitina_a, semilla=6)
        viga(out, p1, p2, 0.3, 0.3, p_quitina_a, semilla=7)
        redondo(out, vr.T(*p2), -0.3, 0.2, 0.32, 0.32, p_pelusa, n=2, semilla=8)
    cubo(out, vr.T(0, 0, 0), -0.95, 2.3, 4.25, 1.9, 2.7, 0.1, p_disco_ambar, semilla=9)
    for anillo, (rx, ry, n) in enumerate(((0.85, 1.25, 16), (0.6, 0.95, 12), (0.36, 0.62, 8))):
        for k in range(n):
            a = k * TAU / n + anillo * 0.2
            pua(out, vr.T(math.cos(a) * rx, 3.65 + math.sin(a) * ry, 4.33 - anillo * 0.05) @ vr.Rz(a - TAU / 4) @ vr.Rx(65 * D), 0.06,
                0.36 - anillo * 0.05, p_diente, semilla=10)
    # el abdomen: un farol que alumbra, alzado detras
    Ma = vr.T(0, 6.0, -3.6) @ vr.Rx(22 * D)
    for (z0, z1, r) in ((-4.0, -3.0, 2.0), (-3.0, -1.6, 3.0), (-1.6, 0.4, 3.5), (0.4, 2.0, 3.2), (2.0, 3.1, 2.3), (3.1, 3.7, 1.3)):
        for w, h in _pasos(r, 4):
            cubo(out, Ma, -w, -h * 0.92, z0, 2 * w, 2 * h * 0.92, z1 - z0, p_farol_ar, semilla=11)
    for k in range(3):                                         # las hileras y la seda
        cubo(out, Ma, -0.3 + k * 0.3 - 0.1, -0.4, -4.4, 0.2, 0.2, 0.5, p_quitina_a, semilla=12)
    cola = punto(Ma, (0, -0.3, -4.3))
    viga(out, cola, cola + np.array((0.4, 14, -2.0)), 0.08, 0.08, p_seda, semilla=13)
    viga(out, cola, np.array((0.8, 0.0, -10.0)), 0.07, 0.07, p_seda, semilla=13)
    # las ocho patas: las dos de delante en alto, las demas abiertas y clavadas
    patas = (((2.6, 4.0), (3.0, 9.0, 4.4), (2.6, 10.6, 6.6), None),
             ((2.0, 3.8), (4.8, 7.6, 3.0), (7.4, 3.0, 4.6), (8.0, 0.0, 5.4)),
             ((1.2, 3.6), (5.4, 7.8, 0.6), (8.4, 3.0, -0.6), (9.0, 0.0, -1.2)),
             ((0.4, 3.6), (5.0, 7.4, -2.4), (7.6, 3.0, -4.4), (8.0, 0.0, -5.6)))
    for s in (1, -1):
        for k, ((zc, yc), rod, tob, pie) in enumerate(patas):
            cox = np.array((s * 2.2, yc, zc + 1.6 - 1.6))
            rodilla = np.array((s * rod[0], rod[1], rod[2]))
            tobillo = np.array((s * tob[0], tob[1], tob[2]))
            viga(out, cox, rodilla, 0.6, 0.6, p_quitina_a, extra=0.15, semilla=14)
            redondo(out, vr.T(*rodilla), -0.4, 0.4, 0.42, 0.42, p_quitina_a, n=2, semilla=15)
            viga(out, rodilla, tobillo, 0.48, 0.48, p_quitina_a, extra=0.1, semilla=16)
            if pie is not None:
                viga(out, tobillo, np.array((s * pie[0], pie[1], pie[2])), 0.3, 0.3, p_quitina_a, semilla=17)
            else:
                viga(out, tobillo, tobillo + np.array((-s * 0.2, 0.5, 1.4)), 0.3, 0.3, p_quitina_a, semilla=17)
            for j in range(3):                               # puas en el femur
                p = cox + (rodilla - cox) * (0.3 + 0.25 * j)
                pua(out, em.marco(p, rodilla - cox, up=(s, 1, 0)) @ vr.Rx(-60 * D), 0.06, 0.45, p_colmillo, semilla=18)
    # los farolillos que le cuelgan (de ahi nacen las crias)
    for k, (x, z, largo) in enumerate(((-1.6, -2.0, 2.2), (1.8, -3.0, 1.6), (0.4, -5.6, 2.8), (-2.4, -4.8, 1.2), (2.6, -0.6, 2.4))):
        arriba = punto(Ma, (x, -2.8, z + 3.6))
        abajo = arriba + np.array((0, -largo, 0))
        viga(out, arriba, abajo, 0.06, 0.06, p_seda, semilla=19)
        redondo(out, vr.T(*abajo), -0.75, 0.0, 0.34, 0.34, p_farol_ar, n=3, semilla=20)
    return out, {}


# ======================================================================
#  C · OTONARA, la Dragona de Hojarasca (neon carmesi)
# ======================================================================
HOJAS = (p_hoja_r, p_hoja_n, p_hoja_o)


def otonara(abre=38.0, semilla=3):
    out = []
    rng = random.Random(semilla)
    # el cuerpo de corteza, con el pecho alzado
    Mt = vr.T(0, 5.4, -0.4) @ vr.Rx(-20 * D)
    ovoide_z(out, Mt, 2.0, 1.9, 3.4, p_corteza, capas=8, pasos=3, semilla=1)
    for k in range(6):                                         # musgo en el lomo
        caja_c(out, Mt, rng.uniform(-0.8, 0.8), 1.75, -2.4 + k * 0.9, 0.9, 0.25, 0.8, p_musgo, semilla=2)
    # las patas de raiz
    for s in (1, -1):
        cad, rod, tob, pie = (np.array((s * 1.5, 4.6, -1.4)), np.array((s * 2.1, 2.9, 0.6)), np.array((s * 2.0, 1.1, -0.8)),
                              np.array((s * 2.0, 0.2, 0.4)))
        viga(out, cad, rod, 1.4, 1.4, p_corteza, extra=0.3, semilla=3)
        viga(out, rod, tob, 1.0, 1.0, p_corteza, extra=0.2, semilla=4)
        viga(out, tob, pie, 0.8, 0.8, p_corteza, extra=0.1, semilla=5)
        for k in (-0.5, 0.0, 0.5):
            garra(out, pie + np.array((k, 0.1, 0.2)), (k * 0.5, -0.1, 1), (0, -1, 0.4), 0.8, 0.5, 0.26, p_rama, semilla=6)
    # el cuello en ese y la crin de hojas por detras
    ctrl = [(0, 6.6, 2.4), (0, 8.8, 3.6), (0, 11.0, 3.2), (0, 12.6, 3.8), (0, 13.2, 5.4)]
    pts, tans = tubo(out, ctrl, (1.3, 0.72), p_corteza, n=14, pasos=3, semilla=7)
    for i in range(1, len(pts) - 1, 1):
        t = tans[i] / np.linalg.norm(tans[i])
        M = em.marco(pts[i], t)
        r = 1.3 + (0.72 - 1.3) * i / (len(pts) - 2)
        for s in (-1, 0, 1):
            Mh_ = M @ vr.T(s * 0.35, r * 0.8, 0) @ vr.Rz(-s * 25 * D) @ vr.Rx(-115 * D)
            hoja(out, Mh_, 1.5 + 0.3 * (i % 2), 0.7, HOJAS[(i + s) % 3], semilla=8)
    # la cabeza: craneo de ciervo, astas de rama, la boca abierta que arde
    Mh = em.marco(pts[-1] + np.array((0, 0.1, 0.4)), (0, -0.3, 1.0)) @ np.diag([1.5, 1.5, 1.5, 1.0])
    cubo(out, Mh, -0.72, -0.55, -0.85, 1.44, 1.3, 1.1, p_hueso, semilla=9)                 # la nuca
    cubo(out, Mh, -0.88, 0.3, -0.1, 1.76, 0.42, 1.0, p_hueso, semilla=10)                    # la ceja
    cubo(out, Mh, -0.7, -0.5, -0.1, 1.4, 0.85, 1.05, p_hueso, semilla=10)
    for s in (1, -1):
        cubo(out, Mh, s * 0.78 - 0.18, -0.4, 0.3, 0.36, 0.55, 0.95, p_hueso, semilla=11)    # los pomulos
        cubo(out, Mh, s * 0.72 - 0.08, 0.0, 0.15, 0.16, 0.42, 0.7, bm.p_garra_ave, semilla=12)   # la cuenca
        cubo(out, Mh, s * 0.78 - 0.04, 0.07, 0.25, 0.08, 0.28, 0.42, p_brasa_roja, semilla=13)   # la brasa del ojo
    for (z0, z1, w, h) in ((0.9, 2.0, 1.0, 0.85), (2.0, 2.9, 0.8, 0.72), (2.9, 3.45, 0.6, 0.6)):
        cubo(out, Mh, -w / 2, -0.5, z0, w, h, z1 - z0, p_hueso, semilla=14)                 # el hocico, que afina
    cubo(out, Mh, -0.22, 0.32, 0.6, 0.44, 0.18, 2.6, p_hueso, semilla=15)                  # la cresta de la nariz
    cubo(out, Mh, -0.3, -0.05, 3.38, 0.6, 0.35, 0.06, bm.p_garra_ave, semilla=14)       # la nariz
    for k in range(7):                                        # dientes de espina arriba
        z = 1.2 + k * 0.32
        for s in (1, -1):
            pua(out, Mh @ vr.T(s * 0.38, -0.5, z) @ vr.Rx(180 * D), 0.06, 0.35 + (k % 2) * 0.15, p_rama, semilla=15)
    Mj = Mh @ vr.T(0, -0.6, 0.4) @ vr.Rx(abre * D)
    cubo(out, Mj, -0.5, -0.4, 0.0, 1.0, 0.4, 3.0, p_hueso, caras={'arriba': p_brasa_roja}, semilla=16)
    for k in range(6):
        for s in (1, -1):
            pua(out, Mj @ vr.T(s * 0.35, 0.0, 0.5 + k * 0.4), 0.06, 0.32 + (k % 2) * 0.12, p_rama, semilla=17)
    cubo(out, Mh, -0.5, -0.62, 0.3, 1.0, 0.2, 2.4, p_brasa_roja, semilla=18)
    for s in (1, -1):                                         # las astas de rama, con alguna hoja
        base = punto(Mh, (s * 0.55, 0.7, -0.3))
        p1 = base + np.array((s * 1.0, 1.6, -0.6))
        p2 = p1 + np.array((s * 1.0, 1.4, -0.4))
        p3 = p2 + np.array((s * 0.4, 1.0, 0.3))
        for a, b, g in ((base, p1, 0.32), (p1, p2, 0.26), (p2, p3, 0.18)):
            viga(out, a, b, g, g, p_rama, semilla=19)
        for (q, d) in ((p1, (s * 0.2, 1.1, 0.6)), (p2, (s * 1.0, 0.6, 0.4)), (p2, (-s * 0.3, 1.0, -0.5)), (p1, (s * 0.9, 0.3, -0.8))):
            fin = q + np.array(d)
            viga(out, q, fin, 0.15, 0.15, p_rama, semilla=20)
            hoja(out, ejes(fin, (1, 0, 0), (0, 0.3, 1)) @ vr.Rx(-60 * D), 0.9, 0.45, HOJAS[rng.randrange(3)], semilla=21)
    # las alas: brazo de rama y la membrana hecha de hojas de otono
    for s in (1, -1):
        hom = np.array((s * 1.6, 7.0, 1.2))
        codo = np.array((s * 3.8, 9.2, 0.2))
        mun = np.array((s * 5.4, 10.8, -0.8))
        viga(out, hom, codo, 0.75, 0.75, p_corteza, extra=0.2, semilla=22)
        viga(out, codo, mun, 0.6, 0.6, p_corteza, extra=0.2, semilla=23)
        puntas = [np.array((s * 6.4, 14.4, -1.6)), np.array((s * 9.0, 12.8, -2.4)), np.array((s * 10.4, 9.6, -2.8)), np.array((s * 9.6, 6.4, -2.6))]
        raices = [hom + np.array((0, -0.4, -1.4)), np.array((s * 2.2, 5.4, -2.4))]
        for tp in puntas:
            viga(out, mun, tp, 0.26, 0.26, p_rama, extra=0.1, semilla=24)
        bordes = [codo] + puntas + raices
        for j in range(len(bordes) - 1):
            a, b = bordes[j], bordes[j + 1]
            for k in range(6):
                u = (k + 0.5) / 6
                for t_ in (0.35, 0.68, 0.92):
                    p = mun + ((a + (b - a) * u) - mun) * t_
                    if j >= len(puntas):
                        p = hom + ((a + (b - a) * u) - hom) * t_
                    radial = p - mun
                    if np.linalg.norm(radial) < 0.1:
                        continue
                    M = ejes(p, np.cross(radial, (0, 0, 1)) + np.array((0, 0, 0.01)), radial) @ vr.Ry(rng.uniform(-20, 20) * D)
                    M = M @ vr.Rx(-90 * D)
                    hoja(out, M, 1.5 + rng.uniform(0, 0.6), 0.9, HOJAS[rng.randrange(3)], semilla=25)
    # la cola larga, que acaba en un manojo de hojas
    ctrl = [(0, 4.6, -3.0), (0, 3.4, -6.0), (1.4, 2.2, -8.6), (3.0, 1.4, -10.2), (4.4, 1.6, -11.2)]
    pts, tans = tubo(out, ctrl, (1.2, 0.35), p_corteza, n=14, pasos=3, semilla=26)
    fin = pts[-1]
    for k in range(9):
        a = k * TAU / 9
        M = em.marco(fin, tans[-1]) @ vr.Rz(a) @ vr.Rx(-35 * D)
        hoja(out, M, 1.6, 0.8, HOJAS[k % 3], semilla=27)
    return out, {}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

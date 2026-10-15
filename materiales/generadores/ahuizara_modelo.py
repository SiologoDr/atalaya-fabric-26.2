"""
Ahuizara y sus tipos (15-10-2026). Juan: «hagamos otro boss y sus 3 tipos». Lo aprendido hasta ahora: un monstruo
inventado con rastros de la referencia (Kelpia), una idea propia que mande en la silueta, la receta de las fauces
encendidas y, para los tipos, la misma pose: «esto de los tipos es de un solo boss, una misma pose pero diferentes»
(Zotzara).

Ahuizara, la Mano del Agua: sale del ahuizotl de los aztecas, la bestia de los canales que ahogaba a la gente y luego
le comia los ojos, los dientes y las unas. Del ahuizotl le quedan rastros: el pelo negro y mojado, las patas que son
manos y, sobre todo, la mano al final de la cola. Lo nuestro: una bestia larga y flaca, agazapada para saltar, que
anda sobre cuatro manos de dedos largos y lleva la cola arqueada sobre el lomo, con una mano enorme abierta encima de
la cabeza, como una corona de dedos que va a agarrarte. La cabeza manda: ancha y chata, con los ojos grandes y
encendidos y las fauces abiertas que arden (el paladar en escalones, los dientes en hojas, los colmillos y el nucleo
al fondo).

Los tres tipos tienen la misma pose (agazapada, con la cola-mano en alto) y cambian la mano de la cola, las orejas y
el color:

    A  la Mano     una mano de cinco dedos abierta sobre la cabeza; orejas pequenas y redondas; turquesa
    B  la Garra    una mano de tres dedos largos de garra, con placas de hueso en los nudillos de todas las manos;
                   orejas largas echadas atras; rosa mexicano
    C  la Gemela   dos colas, con una mano a cada lado de la cabeza; orejas con penachos; cempasuchil
"""
import math
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt
import kelpia_modelo as km
from kelpia_modelo import hilera, colmillo, _u

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.62
CABEZA = 1.4

VARIANTES = {
    'A': dict(
        clave='HA', nombre='la Mano', corto='mano', cola='una', mano='abierta', orejas='redondas', nudillos=False,
        piel=_r('06080a', '0c1014', '141a20', '1e2630', '2a3442'),
        palma=_r('101216', '1a1e24', '262c34', '343c46', '444e5a'),
        casco=_r('16140e', '262218', '383224', '4e4634', '665c46'),
        neon=('e6fffa', '2ae6d0', '045a50'),
    ),
    'B': dict(
        clave='HB', nombre='la Garra', corto='garra', cola='una', mano='garra', orejas='largas', nudillos=True,
        piel=_r('0c0608', '160c10', '22121a', '301a24', '422430'),
        palma=_r('180e12', '24161c', '322028', '422c36', '563a46'),
        casco=_r('1a1410', '2a2018', '3c2e22', '524030', '6a5440'),
        hueso=_r('3a3030', '5a4c4a', '7e6e6a', 'a2928c', 'c4b4ac'),
        neon=('ffe0ee', 'ff2a8a', '6a0430'),
    ),
    'C': dict(
        clave='HC', nombre='la Gemela', corto='gemela', cola='dos', mano='abierta', orejas='penachos', nudillos=False,
        piel=_r('0a0a06', '14140c', '1e1e12', '2a2a1a', '383824'),
        palma=_r('16160e', '222216', '30301e', '40402a', '525236'),
        casco=_r('18140c', '282014', '3a2e1e', '50402a', '6a5638'),
        neon=('fff0d6', 'ff8a1a', '6a2a04'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    """Los de Kelpia para lo comun (el ojo, el paladar, los dientes, el nucleo, la garra, el hueso) y los propios: el
    pelo negro y mojado, en mechones a lo largo, y la piel de las palmas, con sus pliegues."""
    W = dict(V, alga=V['piel'], mancha=V['piel'])
    P = km.pintores(W)
    k = V['clave']

    def reg(nombre, fn):
        fn.__name__ = 'ahu%s_%s' % (k, nombre)
        P[nombre] = fn
        return fn

    def pelo(tw, th, cara, s):
        """El pelo mojado: oscuro, en mechones pegados a lo largo del cuerpo, con alguno mas claro donde brilla el agua."""
        ys, xs = np.mgrid[0:th, 0:tw]
        de_traves = xs if cara in ('arriba', 'abajo') else ys
        idx = np.where(de_traves % 5 == 0, 3, np.where(de_traves % 5 == 2, 1, 2))
        idx = np.where((de_traves % 11 == 7), 4, idx)
        if cara == 'abajo':
            idx = np.clip(idx, 1, 2)
        return _imagen(_bisel(idx, 1, 1), V['piel']), None
    reg('piel', pelo)

    def palma(tw, th, cara, s):
        """La piel de las manos: lisa y algo mas clara, con los pliegues de traves."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys % 4 == 0, 1, 2)
        return _imagen(_bisel(idx, 1, 1), V['palma']), None
    reg('palma', palma)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def mano(out, P, base, adelante, arriba, escala=1.0, dedos=4, largo=1.0, garra=1.0, cierra=0.5, pulgar=True,
         nudillos=False, abanico=14.0, semilla=0):
    """Una mano de dedos largos: la palma en base, los dedos abiertos en abanico hacia adelante que se doblan hacia
    abajo (hacia -arriba) segun cierra, con una garra de cuerno en cada punta, y el pulgar a un lado. Con nudillos,
    una placa de hueso en el dorso de cada dedo."""
    f = _u(adelante)
    u = _u(np.asarray(arriba, float) - f * (np.asarray(arriba, float) @ f))
    e = np.cross(u, f)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = e, u, f, np.asarray(base, float)
    g = escala
    caja(out, M, -1.9 * g, 1.9 * g, -0.75 * g, 0.75 * g, -1.2 * g, 2.6 * g, P['palma'], semilla=semilla)
    xs = np.linspace(-1.45, 1.45, dedos) if dedos > 1 else [0.0]
    for i, x in enumerate(xs):
        abre = (x / 1.45) * abanico * D if dedos > 1 else 0.0
        d = f * math.cos(abre) + e * math.sin(abre)
        p = pt(M, (x * g, 0.1 * g, 2.4 * g))
        puntos = [p]
        tramos = [1.9, 1.6, 1.3]
        for j, t in enumerate(tramos):
            baja = (-0.25 + cierra * (j + 0.5) * 0.55)
            dd = _u(d * math.cos(baja) - u * math.sin(baja))
            p = p + dd * t * largo * g
            puntos.append(p)
        rad = [0.62 * g, 0.52 * g, 0.44 * g, 0.36 * g]
        jm.tubo(out, puntos, rad, [P['palma']] * 3, semilla=semilla + 1)
        for q, r in zip(puntos[1:-1], rad[1:-1]):
            caja(out, vr.T(*q), -r * 1.12, r * 1.12, -r * 1.12, r * 1.12, -r * 1.12, r * 1.12, P['palma'], semilla=semilla + 2)
        if nudillos:
            for q in puntos[:-1]:
                caja(out, vr.T(*(q + u * 0.45 * g)), -0.5 * g, 0.5 * g, -0.25 * g, 0.25 * g, -0.6 * g, 0.6 * g, P['hueso'], semilla=semilla + 3)
        punta = puntos[-1]
        dd = _u(puntos[-1] - puntos[-2])
        jm.tubo(out, [punta, punta + dd * 1.1 * garra * g, punta + dd * 1.5 * garra * g - u * 1.1 * garra * g],
                [0.42 * g, 0.28 * g, 0.06 * g], [P['casco'], P['casco']], semilla=semilla + 4)
    if pulgar:
        p0 = pt(M, (-2.0 * g, 0.0, 0.6 * g))
        d = _u(-e * 0.8 + f * 0.6)
        p1 = p0 + d * 1.6 * g
        p2 = p1 + _u(d - u * 0.8) * 1.3 * g
        jm.tubo(out, [p0, p1, p2], [0.58 * g, 0.46 * g, 0.36 * g], [P['palma'], P['palma']], semilla=semilla + 5)
        dd = _u(p2 - p1)
        jm.tubo(out, [p2, p2 + dd * 1.0 * g, p2 + dd * 1.3 * g - u * 0.9 * g], [0.36 * g, 0.24 * g, 0.06 * g],
                [P['casco'], P['casco']], semilla=semilla + 6)


def oreja(out, P, Mh, s, forma, semilla=0):
    """Las orejas: pequenas y redondas, largas y echadas atras, o redondas con un penacho de pelos de punta."""
    p = P['piel']
    if forma == 'largas':
        b = pt(Mh, (s * 2.6, 3.8, -2.4))
        jm.tubo(out, [b, pt(Mh, (s * 3.9, 5.6, -4.6)), pt(Mh, (s * 5.0, 7.4, -7.4))], [1.1, 0.8, 0.15], [p, p], semilla=semilla)
        jm.tubo(out, [pt(Mh, (s * 2.8, 3.5, -2.8)), pt(Mh, (s * 4.4, 4.8, -5.4)), pt(Mh, (s * 5.4, 5.4, -8.2))], [0.9, 0.6, 0.12], [p, p],
                semilla=semilla)
        return
    x0 = 2.7 if s > 0 else -4.1
    bm.cubo(out, Mh, x0, 2.8, -3.4, 1.4, 2.2, 1.6, p, semilla=semilla)
    bm.cubo(out, Mh, x0 + 0.2 * s, 3.2, -3.7, 1.0, 1.4, 2.2, p, semilla=semilla)
    if forma == 'penachos':
        for k, (dx, dz) in enumerate(((0.0, 0.0), (0.5, -0.6), (-0.4, 0.5))):
            q = pt(Mh, (s * (3.4 + dx), 4.8, -2.7 + dz))
            jm.tubo(out, [q, q + _u(Mh[:3, 1] + Mh[:3, 0] * s * 0.3) * (2.8 - k * 0.6)], [0.45, 0.08], [p], semilla=semilla + k)


def cabeza(out, Mh, P, V, abre=38.0, semilla=0):
    """La cabeza de Ahuizara, con el hocico hacia +z y la boca en y=0: ancha y chata, con el craneo plano, los ojos grandes
    y encendidos delante, la nariz de cuero y las orejas de su tipo. Las fauces, abiertas desde muy atras: el paladar
    encendido en escalones, los dientes en hojas, dos colmillos arriba y dos abajo, el suelo de la boca encendido y el
    nucleo al fondo. Devuelve la boca."""
    p = P['piel']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -3.2, 0.0, -4.0, 6.4, 4.0, 5.5, p, caras=F, semilla=semilla)                   # el craneo
    bm.cubo(out, Mh, -2.6, 0.3, 1.5, 5.2, 3.0, 4.0, p, caras=F, semilla=semilla + 1)               # el hocico
    bm.cubo(out, Mh, -1.4, 2.1, 5.3, 2.8, 1.2, 0.7, P['casco'], semilla=semilla + 2)               # la nariz
    for s in (1, -1):
        bm.cubo(out, Mh, 1.7 if s > 0 else -3.0, 2.4, 0.4, 1.3, 1.4, 1.2, P['ojo'], semilla=semilla + 3)   # los ojos, grandes
        bm.cubo(out, Mh, 1.5 if s > 0 else -3.2, 3.8, 0.0, 1.7, 0.5, 1.8, p, semilla=semilla + 4)           # la ceja
        oreja(out, P, Mh, s, V['orejas'], semilla=semilla + 5)
    hilera(out, Mh, [(-2.4, 0.2), (-2.4, 5.3), (2.4, 5.3), (2.4, 0.2)], 0.6, -1.1, P['dientes_arriba'], semilla=semilla + 6)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.7, 0.6, 4.7), 3.2, 1.0, (0, -1, 0.05), P, semilla=semilla + 7)
    caja(out, Mh, -2.4, 2.4, -2.0, 0.2, -3.3, -3.0, P['nucleo'], semilla=semilla + 8)
    Mj = Mh @ vr.T(0.0, 0.0, -3.4) @ vr.Rx(abre * D)                                                # la quijada de abajo
    bm.cubo(out, Mj, -3.0, -3.0, -0.6, 6.0, 3.0, 4.8, p, caras={'arriba': P['boca']}, semilla=semilla + 9)
    bm.cubo(out, Mj, -2.4, -1.9, 4.2, 4.8, 1.9, 4.4, p, caras={'arriba': P['boca']}, semilla=semilla + 10)
    hilera(out, Mj, [(-2.1, 3.4), (-2.1, 8.4), (2.1, 8.4), (2.1, 3.4)], 0.0, 1.0, P['dientes_abajo'], semilla=semilla + 11)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.6, 0.0, 7.9), 2.6, 0.9, (0, 1, 0.05), P, semilla=semilla + 12)
    return pt(Mh, (0.0, -0.8, 2.8))


def _cabeza_en(out, P, V, nuca, mira, abre, semilla=0):
    R = em.marco((0.0, 0.0, 0.0), _u(np.array(mira, float)), up=(0.0, 1.0, 0.0))
    o = np.asarray(nuca, float) - pt(R, np.array((0.0, 4.0, -3.6)) * CABEZA)
    Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
    bm.PPB = PPB / CABEZA
    boca = cabeza(out, Mh, P, V, abre=abre, semilla=semilla)
    bm.PPB = PPB
    return Mh, boca


def cola(out, P, V, raiz, lado=0.0, semilla=0):
    """La cola: sale de la grupa, sube arqueada sobre el lomo y acaba en la mano, abierta sobre la cabeza y con los
    dedos hacia delante y abajo, como para agarrar. lado la abre hacia un lado (en la Gemela)."""
    raiz = np.asarray(raiz, float)
    x = lado
    ctrl = [raiz, raiz + (x * 0.1, 3.0, -4.0), np.array((x * 0.4, 26.0, -21.0)), np.array((x * 0.7, 34.0, -14.0)),
            np.array((x * 0.9, 36.5, -4.0)), np.array((x, 33.0, 3.5))]
    ps, rs, _ = jm.a_lo_largo(ctrl, 14, ((0.0, 2.8), (0.4, 2.0), (1.0, 1.3)))
    jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=semilla)
    muneca = np.asarray(ps[-1], float)
    caja(out, vr.T(*muneca), -1.6, 1.6, -1.6, 1.6, -1.6, 1.6, P['piel'], semilla=semilla + 1)
    adelante = _u(np.array((x * 0.05, 0.2, 1.0)))                       # los dedos hacia delante, con las garras hacia abajo
    arriba = np.array((x * 0.05, 1.0, -0.2))
    if V['mano'] == 'garra':
        mano(out, P, muneca + adelante * 1.0, adelante, arriba, escala=2.0, dedos=3, largo=1.5, garra=1.8, cierra=1.1,
             pulgar=False, nudillos=V['nudillos'], abanico=26.0, semilla=semilla + 2)
    else:
        mano(out, P, muneca + adelante * 1.0, adelante, arriba, escala=1.9 if V['cola'] == 'una' else 1.5, dedos=4,
             largo=1.15, cierra=1.0, nudillos=V['nudillos'], abanico=24.0, semilla=semilla + 2)


# ======================================================================
#  AHUIZARA
# ======================================================================
def ahuizara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        pelvis, pecho = np.array((0.0, 12.0, -13.0)), np.array((0.0, 13.0, 5.0))
        eje = _u(pecho - pelvis)
        ps, rs, _ = jm.a_lo_largo([pelvis - eje * 3.0, np.array((0.0, 14.8, -4.0)), pecho + eje * 1.5], 8,
                                  ((0.0, 3.4), (0.2, 4.4), (0.5, 4.0), (0.8, 4.8), (1.0, 4.0)))
        jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=10)
        cuello = [pecho + np.array((0.0, 0.5, 1.0)), np.array((0.0, 14.5, 9.5))]
        jm.tubo(out, cuello, [3.4, 2.8], [P['piel']], semilla=11)
        Mh, boca = _cabeza_en(out, P, V, np.array((0.0, 16.2, 10.0)), (0.0, -0.22, 1.0), 38.0, semilla=20)
        # las patas, que son manos: las de delante, apoyadas; las de atras, encogidas para saltar
        for s in (1, -1):
            hombro, codo, muneca = np.array((s * 4.0, 12.0, 5.0)), np.array((s * 8.2, 8.6, 3.0)), np.array((s * 7.8, 2.6, 8.8))
            jm.tubo(out, [hombro, codo, muneca], [3.0, 2.2, 1.7], [P['piel'], P['piel']], semilla=30)
            caja(out, vr.T(*codo), -2.2, 2.2, -2.2, 2.2, -2.2, 2.2, P['piel'], semilla=31)
            mano(out, P, np.array((s * 7.9, 1.0, 9.6)), (s * 0.12, 0.0, 1.0), (0.0, 1.0, 0.0), escala=1.1, cierra=0.6,
                 nudillos=V['nudillos'], semilla=32)
            cadera, rodilla, tobillo = np.array((s * 3.6, 11.0, -12.0)), np.array((s * 8.2, 10.6, -6.5)), np.array((s * 7.8, 3.0, -14.0))
            jm.tubo(out, [cadera, rodilla, tobillo], [3.6, 2.4, 1.8], [P['piel'], P['piel']], semilla=40)
            caja(out, vr.T(*rodilla), -2.4, 2.4, -2.4, 2.4, -2.4, 2.4, P['piel'], semilla=41)
            mano(out, P, np.array((s * 7.9, 1.0, -12.4)), (s * 0.18, 0.0, 1.0), (0.0, 1.0, 0.0), escala=1.15, cierra=0.6,
                 nudillos=V['nudillos'], semilla=42)
        # la cola (o las dos colas), con la mano sobre la cabeza
        raiz = pelvis - eje * 3.0 + np.array((0.0, 1.0, 0.0))
        if V['cola'] == 'dos':
            for s in (1, -1):
                cola(out, P, V, raiz + np.array((s * 1.2, 0.0, 0.0)), lado=s * 8.0, semilla=50)
        else:
            cola(out, P, V, raiz, semilla=50)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

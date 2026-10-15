"""
Mirmara y sus tipos (15-10-2026). Juan, al guardar a Ayunara: «guardalo me gusto, y crea otro boss». Lo que funciona:
una leyenda con rastros, una idea que enmarque la cabeza (algas, orejas, la mano y las astas ya estan) y los tres tipos
con la misma pose.

Mirmara, la Boca de la Arena: sale del mirmecoleon, el «hormiga-leon» de los bestiarios medievales, y de la hormiga
leon de verdad, que espera al fondo de su embudo de arena a que algo resbale. Es un monstruo que vive enterrado en un
embudo enorme del desierto: solo asoman el pecho, en anillos con cerdas, las cuatro patas de delante abiertas sobre la
arena, la grupa detras y la cabeza ancha y chata, con los ojillos encendidos en dos tuberculos. La cabeza manda, con
las fauces abiertas que arden (el paladar en escalones, los dientes en hojas, los colmillos y el nucleo al fondo), y la
enmarcan dos mandibulas enormes en hoz, como unas pinzas. El embudo, con su borde de arena, es parte del jefe.

Los tres tipos tienen la misma pose (erguida en el embudo, mirando hacia abajo, con las mandibulas abiertas) y
cambian las mandibulas:

    A  la Hoz        dos mandibulas lisas y curvas, con tres dientes junto a la base; turquesa
    B  la Sierra     dos mandibulas dentadas por dentro de punta a punta; carmin
    C  la Horquilla  cuatro mandibulas (dos grandes y dos pequenas debajo), con la punta abierta en horquilla; lima
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
CABEZA = 1.5
ARENA = _r('5a4a34', '725e42', '8a7452', 'a48c66', 'bea47c')

VARIANTES = {
    'A': dict(
        clave='MA', nombre='la Hoz', corto='hoz', mandibulas='hoz',
        piel=_r('0e0a08', '18120e', '241c16', '322820', '42362c'),
        cuerno=_r('1a120c', '2c1e14', '42301e', '5c4430', '7a5c42'),
        casco=_r('16120e', '241e18', '362c24', '4a3e32', '625444'),
        neon=('e6fffa', '2affd8', '045a4a'),
    ),
    'B': dict(
        clave='MB', nombre='la Sierra', corto='sierra', mandibulas='sierra',
        piel=_r('0e0808', '181010', '241818', '322222', '422e2e'),
        cuerno=_r('1e0c0c', '321414', '4a2020', '663030', '864646'),
        casco=_r('180e0e', '261818', '382424', '4c3434', '644646'),
        neon=('ffe4ea', 'ff2a5a', '6a0420'),
    ),
    'C': dict(
        clave='MC', nombre='la Horquilla', corto='horquilla', mandibulas='horquilla',
        piel=_r('0a0c08', '12160e', '1a2014', '242c1c', '303a26'),
        cuerno=_r('161a0c', '242c14', '36401e', '4c582c', '66743c'),
        casco=_r('12140e', '1e2218', '2c3224', '3c4432', '505a44'),
        neon=('f6ffe0', 'b6ff2a', '3a5a04'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    """Los de Kelpia para lo comun (el ojo, el paladar, los dientes, el nucleo, las cerdas) y los propios: la quitina
    en anillos, con polvo de arena por encima; el cuerno de las mandibulas, mas claro hacia la punta; y la arena."""
    W = dict(V, alga=V['piel'], mancha=V['piel'], hueso=V['cuerno'])
    P = km.pintores(W)
    k = V['clave']

    def reg(nombre, fn):
        fn.__name__ = 'mir%s_%s' % (k, nombre)
        P[nombre] = fn
        return fn

    def quitina(tw, th, cara, s):
        """La quitina: oscura, en anillos con el canto claro; por arriba, polvo de arena."""
        ys, xs = np.mgrid[0:th, 0:tw]
        de_traves, a_lo_largo = (xs, ys) if cara in ('arriba', 'abajo') else (ys, xs)
        idx = np.where(a_lo_largo % 8 == 0, 3, np.where(a_lo_largo % 8 == 1, 1, 2))
        t = _imagen(_bisel(idx, 1, 1), V['piel'])
        if cara == 'arriba':
            polvo = ((xs * 7 + ys * 13) % 11) < 3
            t[polvo] = _imagen(np.full((th, tw), 1), ARENA)[polvo]
        return t, None
    reg('piel', quitina)

    def cuerno(tw, th, cara, s):
        """El cuerno de las mandibulas: en bandas de traves, con el filo claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        de_traves, a_lo_largo = (xs, ys) if cara in ('arriba', 'abajo') else (ys, xs)
        idx = np.where(a_lo_largo % 6 < 2, 3, 2)
        return _imagen(_bisel(idx, 2, 1), V['cuerno']), None
    reg('cuerno', cuerno)

    reg('hondo', jm.liso([V['piel'][0], V['piel'][0], V['piel'][0], V['piel'][1], V['piel'][1]], 1, 1, 0))

    def arena(tw, th, cara, s):
        """La arena del embudo: lisa, con ondas de traves; los lados, mas oscuros."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys + xs // 5) % 6 == 0, 2, 3)
        return _imagen(idx, ARENA), None
    reg('arena', arena)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def embudo(out, P, r_in=8.0, r_borde=20.0, r_fuera=28.0, alto=8.0, n=36, semilla=0):
    """El embudo: un cono de arena que baja del borde al agujero, y por fuera otro que baja al suelo; en medio, lo
    hondo, en sombra."""
    def anillo(r, y):
        return [np.array((math.cos(TAU * i / n) * r, y, math.sin(TAU * i / n) * r)) for i in range(n + 1)]
    for (ra, ya), (rb, yb) in (((r_in, -0.4), (r_borde, alto)), ((r_borde, alto), (r_fuera, 0.0))):
        A, B = anillo(ra, ya), anillo(rb, yb)
        for i in range(n):
            ancho = float(np.linalg.norm(B[i + 1] - B[i]))
            largo = float(np.linalg.norm(B[i] - A[i]))
            if ra < rb:
                lamina(out, (A[i + 1], A[i], B[i], B[i + 1]), P['arena'], ancho, largo, semilla=semilla + i % 4)
            else:
                lamina(out, (A[i], A[i + 1], B[i + 1], B[i]), P['arena'], ancho, largo, semilla=semilla + i % 4)
    caja(out, np.eye(4), -r_in, r_in, -0.8, -0.4, -r_in, r_in, P['hondo'], semilla=semilla)
    caja(out, np.eye(4), -r_in * 0.7, r_in * 0.7, -0.8, -0.4, -r_in * 1.1, r_in * 1.1, P['hondo'], semilla=semilla)


def cerdas(out, P, base, fuera, n=4, largo=3.0, semilla=0):
    """Un manojo de cerdas tiesas que salen hacia fuera."""
    base, fuera = np.asarray(base, float), _u(fuera)
    lado = _u(np.cross(fuera, (0.0, 1.0, 0.0))) if abs(fuera[1]) < 0.9 else np.array((1.0, 0.0, 0.0))
    for k in range(n):
        d = _u(fuera + lado * (k - (n - 1) / 2) * 0.35 + np.array((0.0, 0.25 * (k % 2), 0.0)))
        jm.tubo(out, [base, base + d * largo * (0.8 + 0.2 * (k % 2))], [0.32, 0.06], [P['casco']], semilla=semilla + k)


def mandibula(out, P, Mh, s, tipo, abajo=0.0, escala=1.0, semilla=0):
    """Una mandibula en hoz (en coordenadas de la cabeza), de la base, a un lado de las fauces, a la punta, delante y
    hacia dentro. 'hoz' lleva tres dientes junto a la base; 'sierra', dientes de punta a punta; 'horquilla', la punta
    abierta en dos."""
    def q(x, y, z):
        return pt(Mh, (s * x * escala, 1.2 + (y - 1.2) * escala - abajo, 1.5 + (z - 1.5) * escala))
    ctrl = [q(3.4, 1.2, 1.5), q(5.4, 1.4, 4.6), q(5.6, 1.5, 8.0), q(4.2, 1.4, 10.6), q(2.0, 1.2, 11.8)]
    ps, rs, ts = jm.a_lo_largo(ctrl, 10, ((0.0, 1.15 * escala), (0.5, 0.8 * escala), (1.0, 0.25 * escala)))
    jm.tubo(out, ps, rs, [P['cuerno']] * (len(ps) - 1), semilla=semilla)
    dentro = lambda p: _u(np.asarray(pt(Mh, (0.0, 1.2, np.dot(np.asarray(p) - pt(Mh, (0, 0, 0)), _u(Mh[:3, 2])) / CABEZA))) - p)
    if tipo == 'hoz':
        dientes = (2, 3, 4)
    elif tipo == 'sierra':
        dientes = range(1, 10)
    else:
        dientes = (3, 5)
    for k in dientes:
        p = np.asarray(ps[k], float)
        d = dentro(p)
        jm.tubo(out, [p, p + d * (rs[k] + 1.2 * escala)], [rs[k] * 0.55, 0.08], [P['dientes_abajo'] if False else P['cuerno']], semilla=semilla + 1)
    if tipo == 'horquilla':                                             # la punta, abierta en dos
        p = np.asarray(ps[-2], float)
        d = _u(np.asarray(ps[-1]) - np.asarray(ps[-2]))
        arriba = _u(Mh[:3, 1])
        for v in (1, -1):
            jm.tubo(out, [p, p + _u(d + arriba * v * 0.9) * 2.6 * escala], [0.4 * escala, 0.08], [P['cuerno']], semilla=semilla + 2)


def cabeza(out, Mh, P, V, abre=40.0, semilla=0):
    """La cabeza de Mirmara, con el hocico hacia +z y la boca en y=0: ancha y chata, como la de la hormiga leon, con
    los ojillos encendidos en un tuberculo a cada lado. Las fauces, abiertas desde muy atras: el paladar encendido en
    escalones, los dientes en hojas, dos colmillos arriba y dos abajo, el suelo de la boca encendido y el nucleo al
    fondo. Y a los lados, las mandibulas de su tipo. Devuelve la boca."""
    p = P['piel']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -4.0, 0.0, -4.0, 8.0, 3.6, 5.5, p, caras=F, semilla=semilla)                   # el craneo, chato
    bm.cubo(out, Mh, -2.4, 3.6, -3.6, 4.8, 0.8, 4.4, p, semilla=semilla + 1)                       # y su lomo
    bm.cubo(out, Mh, -3.0, 0.3, 1.5, 6.0, 2.6, 3.4, p, caras=F, semilla=semilla + 2)               # la boca de arriba
    for s in (1, -1):                                                                              # los tuberculos con los ojillos
        x0 = 3.6 if s > 0 else -5.0
        bm.cubo(out, Mh, x0, 2.0, -1.4, 1.4, 1.8, 2.6, p, semilla=semilla + 3)
        for k, (y, z) in enumerate(((3.0, -1.0), (2.4, 0.0), (3.2, 0.4))):
            xo = 4.95 if s > 0 else -5.25
            bm.cubo(out, Mh, xo, y, z, 0.3, 0.5, 0.5, P['ojo'], semilla=semilla + 4)
        cerdas(out, P, pt(Mh, (s * 3.8, 3.4, -3.2)), Mh[:3, :3] @ np.array((s * 1.0, 0.6, -0.5)), n=3, largo=2.6, semilla=semilla + 5)
    hilera(out, Mh, [(-2.8, 0.2), (-2.8, 4.8), (2.8, 4.8), (2.8, 0.2)], 0.6, -1.1, P['dientes_arriba'], semilla=semilla + 6)
    for s in (1, -1):
        colmillo(out, Mh, (s * 2.0, 0.6, 4.3), 2.8, 0.9, (0, -1, 0.05), P, semilla=semilla + 7)
    caja(out, Mh, -2.6, 2.6, -2.0, 0.2, -3.3, -3.0, P['nucleo'], semilla=semilla + 8)
    Mj = Mh @ vr.T(0.0, 0.0, -3.4) @ vr.Rx(abre * D)                                                # la quijada de abajo
    bm.cubo(out, Mj, -3.6, -2.6, -0.6, 7.2, 2.6, 4.6, p, caras={'arriba': P['boca']}, semilla=semilla + 9)
    bm.cubo(out, Mj, -2.8, -1.8, 4.0, 5.6, 1.8, 4.0, p, caras={'arriba': P['boca']}, semilla=semilla + 10)
    hilera(out, Mj, [(-2.5, 3.0), (-2.5, 7.8), (2.5, 7.8), (2.5, 3.0)], 0.0, 1.0, P['dientes_abajo'], semilla=semilla + 11)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.9, 0.0, 7.3), 2.4, 0.8, (0, 1, 0.05), P, semilla=semilla + 12)
    for s in (1, -1):                                                                              # las mandibulas
        mandibula(out, P, Mh, s, V['mandibulas'], semilla=semilla + 20)
        if V['mandibulas'] == 'horquilla':
            mandibula(out, P, Mh, s, 'hoz', abajo=1.6, escala=0.62, semilla=semilla + 30)
    return pt(Mh, (0.0, -0.8, 2.6))


def pata(out, P, puntos, semilla=0):
    """Una pata de insecto: la coxa, el muslo que sube, la tibia que baja a la arena y el tarso con su una, con espinas
    en la tibia."""
    puntos = [np.asarray(p, float) for p in puntos]
    jm.tubo(out, puntos, [1.7, 1.3, 0.9, 0.6, 0.3], [P['piel']] * 4, semilla=semilla)
    for q, r in zip(puntos[1:3], (1.5, 1.1)):
        caja(out, vr.T(*q), -r, r, -r, r, -r, r, P['piel'], semilla=semilla + 1)
    for t in (0.3, 0.6):                                                # las espinas de la tibia
        q = puntos[2] + (puntos[3] - puntos[2]) * t
        d = _u(np.cross(puntos[3] - puntos[2], (0.0, 1.0, 0.0)))
        if d @ (q - np.array((0.0, q[1], 0.0))) < 0:
            d = -d
        jm.tubo(out, [q, q + d * 1.8 + np.array((0.0, 0.6, 0.0))], [0.3, 0.06], [P['casco']], semilla=semilla + 2)


# ======================================================================
#  MIRMARA
# ======================================================================
def mirmara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        embudo(out, P, semilla=1)
        # la grupa, que asoma detras, gorda y en anillos
        gps, grs, _ = jm.a_lo_largo([np.array((0.0, -3.0, -4.0)), np.array((0.0, 4.0, -9.0)), np.array((0.0, 1.0, -14.0))], 6,
                                    ((0.0, 6.0), (0.5, 6.4), (1.0, 3.5)))
        jm.tubo(out, gps, grs, [P['piel']] * (len(gps) - 1), semilla=10)
        for k in (1, 3, 5):
            for s in (1, -1):
                q = np.asarray(gps[k], float) + np.array((s * grs[k] * 0.8, grs[k] * 0.5, 0.0))
                cerdas(out, P, q, (s * 1.0, 0.8, 0.0), n=3, largo=2.8, semilla=11)
        # el pecho, que sale erguido del embudo, en anillos con cerdas
        pecho = [np.array((0.0, -4.0, -1.0)), np.array((0.0, 6.0, 0.5)), np.array((0.0, 15.0, 2.0)), np.array((0.0, 22.0, 3.5)),
                 np.array((0.0, 26.0, 4.5))]
        jm.tubo(out, pecho, [6.6, 6.2, 5.6, 4.8, 4.0], [P['piel']] * 4, semilla=12)
        for q, r in zip(pecho[1:4], (6.4, 5.8, 5.0)):
            for s in (1, -1):
                cerdas(out, P, q + np.array((s * r * 0.9, 0.5, 0.0)), (s * 1.0, 0.4, 0.3), n=4, largo=3.4, semilla=13)
            cerdas(out, P, q + np.array((0.0, 0.5, -r * 0.9)), (0.0, 0.4, -1.0), n=3, largo=3.0, semilla=14)
        R = em.marco((0.0, 0.0, 0.0), _u(np.array((0.0, -0.55, 1.0))), up=(0.0, 1.0, 0.0))
        nuca = np.array((0.0, 29.0, 4.5))
        o = nuca - pt(R, np.array((0.0, 4.2, -3.6)) * CABEZA)
        Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
        bm.PPB = PPB / CABEZA
        boca = cabeza(out, Mh, P, V, abre=40.0, semilla=20)
        bm.PPB = PPB
        # las cuatro patas de delante, abiertas hasta el borde del embudo
        for s in (1, -1):
            pata(out, P, [np.array((s * 4.6, 19.0, 3.0)), np.array((s * 11.0, 24.0, 6.0)), np.array((s * 15.5, 15.0, 9.0)),
                          np.array((s * 17.5, 8.4, 9.5)), np.array((s * 18.4, 7.6, 10.8))], semilla=40)
            pata(out, P, [np.array((s * 5.4, 12.0, 0.0)), np.array((s * 12.0, 17.0, -1.0)), np.array((s * 16.5, 10.0, -3.0)),
                          np.array((s * 18.6, 7.8, -4.5)), np.array((s * 19.4, 7.4, -6.0))], semilla=50)
    finally:
        bm.PPB = ppb
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, 0.8, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

"""
Ayunara y sus tipos (15-10-2026). Juan, al guardar a Ahuizara: «sigamos con otro boss y sus 3 tipos». Lo que funciona:
una leyenda con rastros (no una copia), una idea que mande en la silueta, la receta de las fauces encendidas y los tres
tipos con la misma pose. Lo que ya enmarca otras cabezas (las algas de Kelpia, las orejas de Zotzara, la mano de
Ahuizara) no se repite: aqui son las astas.

Ayunara, la Hambre del Bosque Helado: sale del wendigo de los pueblos del norte, el espiritu del hambre que vaga por
los bosques en invierno y nunca se sacia. Del wendigo le quedan rastros: la flacura, las costillas marcadas, las patas
de pezuna, el frio y, sobre todo, las astas. No es la calavera de ciervo de siempre: es un monstruo alto y erguido,
con los brazos largos que le cuelgan hasta las rodillas y acaban en garras de hielo, la escarcha que le crece en los
hombros y una cabeza nuestra, larga, sin labios, con los dientes siempre a la vista y las fauces abiertas que arden
(el paladar en escalones, los dientes en hojas, los colmillos y el nucleo al fondo). Encima, las astas enormes, con
carambanos colgando, le hacen de corona.

Los tres tipos tienen la misma pose (de pie, encorvada hacia delante, con los brazos colgando abiertos y la cabeza
adelantada) y cambian las astas:

    A  la Ramosa     astas de muchas puntas, que suben y se abren como las de un ciervo viejo; hielo
    B  la Palmeada   astas anchas en pala, con puas por el borde; sangre
    C  la Retorcida  astas que se retuercen hacia arriba como raices secas, con ramitas de punta; violeta
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
CABEZA = 1.7

VARIANTES = {
    'A': dict(
        clave='YA', nombre='la Ramosa', corto='ramosa', astas='ramosa',
        piel=_r('08090c', '101218', '181c24', '222832', '2e3542'),
        asta=_r('2a2620', '423c32', '5e5646', '7e7460', '9e947c'),
        hielo=_r('5a7a8c', '84a8ba', 'aed0de', 'd2ecf4', 'f2fcff'),
        casco=_r('100e0c', '1a1714', '26221e', '34302a', '443e36'),
        neon=('f0fcff', '6ae0ff', '0a4a66'),
    ),
    'B': dict(
        clave='YB', nombre='la Palmeada', corto='palmeada', astas='palmeada',
        piel=_r('0c0808', '161010', '221818', '302222', '402e2e'),
        asta=_r('2c2420', '463a32', '625244', '826e5c', 'a28c76'),
        hielo=_r('6a7a86', '94a8b4', 'bcd0da', 'dcecf2', 'f6fcff'),
        casco=_r('120c0a', '1c1612', '28201a', '362c24', '46392e'),
        neon=('ffe4e4', 'ff2a2a', '6a0606'),
    ),
    'C': dict(
        clave='YC', nombre='la Retorcida', corto='retorcida', astas='retorcida',
        piel=_r('0a080e', '120e18', '1c1624', '262032', '322a42'),
        asta=_r('262228', '3c363e', '565058', '746c76', '948c96'),
        hielo=_r('6a6a8c', '9494b4', 'bcbcda', 'dedef4', 'f8f8ff'),
        casco=_r('0e0c10', '18141a', '221e26', '2e2832', '3c3442'),
        neon=('f6e8ff', 'c04aff', '3a0a6a'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    """Los de Kelpia para lo comun (la piel, el ojo, el paladar, los dientes, el nucleo, la pezuna) y los propios: el
    asta, con sus estrias, y el hielo, en facetas claras."""
    W = dict(V, alga=V['piel'], mancha=V['piel'], hueso=V['asta'])
    P = km.pintores(W)
    k = V['clave']

    def reg(nombre, fn):
        fn.__name__ = 'ayu%s_%s' % (k, nombre)
        P[nombre] = fn
        return fn

    def asta(tw, th, cara, s):
        """El asta: hueso viejo, con estrias a lo largo y algun nudo mas oscuro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        de_traves, a_lo_largo = (xs, ys) if cara in ('arriba', 'abajo') else (ys, xs)
        idx = np.where(de_traves % 3 == 0, 2, 3)
        idx = np.where(a_lo_largo % 9 == 0, 1, idx)
        return _imagen(_bisel(idx, 1, 1), V['asta']), None
    reg('asta', asta)

    def hielo(tw, th, cara, s):
        """El hielo: facetas claras en diagonal, con el canto blanco."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs + ys) // 3) % 2 == 0, 3, 2)
        return _imagen(_bisel(idx, 2, 1), V['hielo']), None
    reg('hielo', hielo)

    def pala(tw, th, cara, s):
        """La pala del asta (en la Palmeada): el hueso liso, con las vetas que bajan hacia la base."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs % 4 == 0, 2, 3)
        idx = np.where(ys < 1, 4, idx)
        return _imagen(idx, V['asta']), None
    reg('pala', pala)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def rama(out, P, pts, r0, r1, semilla=0):
    """Un tramo de asta por los puntos, de grueso r0 a r1."""
    pts = [np.asarray(p, float) for p in pts]
    rs = list(np.linspace(r0, r1, len(pts)))
    jm.tubo(out, pts, rs, [P['asta']] * (len(pts) - 1), semilla=semilla)


def carambano(out, P, p, largo, semilla=0):
    """Un carambano que cuelga: tres cajas que se afinan hacia abajo."""
    p = np.asarray(p, float)
    for k, (w, h) in enumerate(((0.45, 0.4), (0.3, 0.35), (0.15, 0.25))):
        y0 = -largo * sum((0.4, 0.35, 0.25)[:k])
        caja(out, vr.T(*p), -w, w, y0 - largo * h, y0, -w, w, P['hielo'], semilla=semilla + k)


def astas(out, P, Mh, s, tipo, semilla=0):
    """Un asta (s = 1 la derecha, -1 la izquierda), en coordenadas de la cabeza, con sus carambanos."""
    def q(x, y, z):
        return pt(Mh, (s * x, y, z))
    colgar = []
    if tipo == 'ramosa':
        viga = [q(1.6, 4.2, -1.2), q(4.2, 7.0, -2.2), q(7.2, 10.8, -2.4), q(9.4, 14.6, -3.4), q(10.6, 18.4, -2.4)]
        rama(out, P, viga, 0.95, 0.3, semilla=semilla)
        for base, punta in ((q(2.6, 5.4, -1.6), q(3.6, 7.6, 2.0)), (q(4.6, 7.6, -2.3), q(5.4, 12.0, 0.2)),
                            (q(7.6, 11.4, -2.5), q(8.0, 15.8, 0.4)), (q(9.6, 15.0, -3.3), q(12.6, 17.4, -1.4)),
                            (q(6.0, 9.2, -2.3), q(9.4, 9.8, -4.6))):
            medio = (base + punta) / 2 + np.array((0.0, 0.6, 0.0))
            rama(out, P, [base, medio, punta], 0.55, 0.15, semilla=semilla + 1)
        colgar = [q(4.6, 7.4, -2.3), q(7.4, 10.8, -2.5), q(9.6, 14.6, -3.4), q(6.4, 9.3, -2.3)]
    elif tipo == 'palmeada':
        viga = [q(1.6, 4.2, -1.2), q(4.4, 5.6, -2.0), q(7.0, 6.6, -2.4)]
        rama(out, P, viga, 0.95, 0.75, semilla=semilla)
        borde = [q(6.4, 5.8, -2.0), q(9.6, 6.4, -1.4), q(12.4, 8.6, -1.8), q(13.4, 12.0, -2.6), q(12.2, 15.2, -3.4),
                 q(9.8, 16.4, -3.6), q(7.4, 14.8, -3.0)]
        centro = q(8.0, 9.4, -2.4)
        for a, b in zip(borde, borde[1:]):                              # la pala, de dos caras
            for quad in ((centro, centro, b, a), (centro, centro, a, b)):
                lamina(out, quad, P['pala'], float(np.linalg.norm(b - a)), float(np.linalg.norm((a + b) / 2 - centro)), semilla=semilla + 1)
        for a, b in zip(borde, borde[1:]):                              # el canto, grueso
            jm.tubo(out, [a, b], [0.5, 0.5], [P['asta']], semilla=semilla + 2)
        for k, a in enumerate(borde[1:]):                               # las puas del borde
            d = _u(a - centro)
            jm.tubo(out, [a, a + d * 2.4 + np.array((0.0, 0.8, 0.0))], [0.45, 0.1], [P['asta']], semilla=semilla + 3)
        rama(out, P, [q(4.0, 5.6, -1.9), q(4.6, 7.4, 1.4), q(4.2, 8.6, 3.0)], 0.55, 0.15, semilla=semilla + 4)   # la punta de la frente
        colgar = [borde[1], borde[2], q(8.0, 5.8, -2.0)]
    else:                                                               # retorcida: sube en espiral, como una raiz
        viga = []
        for k in range(9):
            t = k / 8
            a = t * 2.2 * math.pi
            viga.append(q(1.6 + t * 7.0 + math.sin(a) * 1.6, 4.2 + t * 15.0, -1.2 - t * 2.0 + math.cos(a) * 1.8))
        rama(out, P, viga, 1.0, 0.25, semilla=semilla)
        for k in (2, 4, 6):                                             # ramitas de punta
            b = viga[k]
            d = _u(b - viga[k - 1])
            fuera = np.asarray(pt(Mh, (s * 1.0, 0.3, 0.0))) - np.asarray(pt(Mh, (0.0, 0.0, 0.0)))
            p1 = b + _u(d + fuera * 0.8) * 2.4
            rama(out, P, [b, p1, p1 + _u(d) * 1.6], 0.45, 0.1, semilla=semilla + 1)
        colgar = [viga[2], viga[4], viga[5]]
    for k, c in enumerate(colgar):
        carambano(out, P, np.asarray(c, float) - np.array((0.0, 0.5, 0.0)), 2.0 + (k % 2) * 1.2, semilla=semilla + 10 + k)


def cabeza(out, Mh, P, V, abre=42.0, semilla=0):
    """La cabeza de Ayunara, con el hocico hacia +z y la boca en y=0: larga y flaca, con la ceja de hueso que tapa los
    ojos hundidos y encendidos, los pomulos marcados y sin labios: los dientes se ven siempre. Las fauces, abiertas
    desde muy atras: el paladar encendido en escalones, los dientes en hojas, dos colmillos largos arriba y dos abajo,
    el suelo de la boca encendido y el nucleo al fondo. Encima, las astas de su tipo. Devuelve la boca."""
    p = P['piel']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -2.6, 0.0, -3.6, 5.2, 4.2, 4.8, p, caras=F, semilla=semilla)                   # el craneo
    bm.cubo(out, Mh, -2.0, 0.3, 1.2, 4.0, 3.0, 4.6, p, caras=F, semilla=semilla + 1)               # el hocico, largo
    bm.cubo(out, Mh, -1.6, 0.6, 5.8, 3.2, 2.4, 1.4, p, caras=F, semilla=semilla + 2)               # la punta
    bm.cubo(out, Mh, -1.1, 2.2, 6.9, 2.2, 0.8, 0.4, P['casco'], semilla=semilla + 3)               # la nariz
    for s in (1, -1):
        bm.cubo(out, Mh, 1.8 if s > 0 else -2.4, 2.6, 0.0, 0.6, 0.9, 1.0, P['ojo'], semilla=semilla + 4)    # los ojos, hundidos
        bm.cubo(out, Mh, 1.4 if s > 0 else -3.0, 3.5, -0.6, 1.6, 0.8, 2.2, P['hueso'], semilla=semilla + 5)  # la ceja de hueso
        bm.cubo(out, Mh, 2.2 if s > 0 else -3.0, 0.8, -1.6, 0.8, 1.6, 2.4, p, semilla=semilla + 6)          # el pomulo
        astas(out, P, Mh, s, V['astas'], semilla=semilla + 20)
    hilera(out, Mh, [(-1.9, -0.6), (-1.9, 6.9), (1.9, 6.9), (1.9, -0.6)], 0.6, -1.3, P['dientes_arriba'], semilla=semilla + 7)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.4, 0.6, 6.4), 3.6, 0.9, (0, -1, 0.05), P, semilla=semilla + 8)
    caja(out, Mh, -2.0, 2.0, -2.0, 0.2, -2.9, -2.6, P['nucleo'], semilla=semilla + 9)
    Mj = Mh @ vr.T(0.0, 0.0, -3.0) @ vr.Rx(abre * D)                                                # la quijada de abajo
    bm.cubo(out, Mj, -2.4, -2.8, -0.6, 4.8, 2.8, 4.6, p, caras={'arriba': P['boca']}, semilla=semilla + 10)
    bm.cubo(out, Mj, -1.9, -1.8, 4.0, 3.8, 1.8, 5.8, p, caras={'arriba': P['boca']}, semilla=semilla + 11)
    hilera(out, Mj, [(-1.7, 2.4), (-1.7, 9.6), (1.7, 9.6), (1.7, 2.4)], 0.0, 1.1, P['dientes_abajo'], semilla=semilla + 12)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.3, 0.0, 9.1), 2.8, 0.8, (0, 1, 0.05), P, semilla=semilla + 13)
    return pt(Mh, (0.0, -0.8, 3.0))


def garras(out, P, muneca, abajo, fuera, semilla=0):
    """La mano: una palma estrecha y tres dedos largos que acaban en garras de hielo, colgando."""
    muneca, abajo, fuera = np.asarray(muneca, float), _u(abajo), _u(fuera)
    caja(out, vr.T(*muneca), -1.1, 1.1, -1.1, 1.1, -1.1, 1.1, P['piel'], semilla=semilla)
    adelante = _u(np.cross(fuera, abajo))
    for k, x in enumerate((-0.9, 0.0, 0.9)):
        b = muneca + fuera * x + abajo * 0.8
        m = b + abajo * 2.4 + adelante * 0.5 + fuera * x * 0.4
        f = m + abajo * 2.0 + adelante * 1.2
        jm.tubo(out, [b, m, f], [0.5, 0.4, 0.3], [P['piel'], P['piel']], semilla=semilla + 1)
        jm.tubo(out, [f, f + abajo * 1.4 + adelante * 1.4, f + abajo * 2.0 + adelante * 2.6], [0.38, 0.22, 0.05],
                [P['hielo'], P['hielo']], semilla=semilla + 2)


def pezuna(out, P, menudillo, punta, semilla=0):
    """La pezuna partida en dos, en el suelo."""
    menudillo, punta = np.asarray(menudillo, float), np.asarray(punta, float)
    jm.tubo(out, [menudillo, punta], [1.0, 0.9], [P['piel']], semilla=semilla)
    for x in (-0.65, 0.65):
        caja(out, vr.T(punta[0] + x, 0.0, punta[2]), -0.55, 0.55, 0.0, 1.5, -1.0, 1.6, P['casco'], semilla=semilla + 1)


def _cabeza_en(out, P, V, nuca, mira, abre, semilla=0):
    R = em.marco((0.0, 0.0, 0.0), _u(np.array(mira, float)), up=(0.0, 1.0, 0.0))
    o = np.asarray(nuca, float) - pt(R, np.array((0.0, 4.2, -3.4)) * CABEZA)
    Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
    bm.PPB = PPB / CABEZA
    boca = cabeza(out, Mh, P, V, abre=abre, semilla=semilla)
    bm.PPB = PPB
    return Mh, boca


# ======================================================================
#  AYUNARA
# ======================================================================
def ayunara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        pelvis, pecho = np.array((0.0, 22.0, -1.0)), np.array((0.0, 34.0, 2.5))          # encorvada hacia delante
        eje = _u(pecho - pelvis)
        # el tronco: la cintura muy estrecha y el pecho hondo, con las costillas marcadas y los huesos de la cadera
        ps, rs, _ = jm.a_lo_largo([pelvis, (pelvis + pecho) / 2 + np.array((0.0, 0.0, -0.8)), pecho], 6,
                                  ((0.0, 3.2), (0.4, 2.0), (0.8, 4.0), (1.0, 3.6)))
        jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=10, achata=1.2)
        for k in range(4):
            c = pelvis + (pecho - pelvis) * (0.6 + k * 0.1)
            r = 3.5
            for s_ in (1, -1):
                arco = [c + np.array((s_ * 1.0, 0.5, r * 1.15)), c + np.array((s_ * r * 0.9, 0.0, r * 0.8)),
                        c + np.array((s_ * r * 1.1, -0.6, 0.0)), c + np.array((s_ * r * 0.9, -1.0, -r * 0.7))]
                jm.tubo(out, arco, [0.5, 0.55, 0.55, 0.4], [P['piel']] * 3, semilla=11)
        for s_ in (1, -1):
            caja(out, vr.T(s_ * 2.8, 23.6, 0.2), -1.0, 1.0, -0.8, 0.8, -1.4, 1.4, P['hueso'], semilla=12)          # la cadera
            caja(out, vr.T(s_ * 2.6, 34.6, -1.6) @ vr.Rz(s_ * 0.3), -1.4, 1.4, -1.0, 1.0, -0.5, 0.5, P['hueso'], semilla=12)  # el omoplato
        for k in range(6):                                              # el espinazo
            q = pelvis + (pecho - pelvis) * (k / 5) + np.array((0.0, 0.0, -3.4))
            caja(out, vr.T(*q), -0.5, 0.5, -0.4, 0.4, -0.7, 0.3, P['hueso'], semilla=12)
        cuello = [pecho + np.array((0.0, 1.0, 0.5)), pecho + np.array((0.0, 4.0, 4.0))]
        jm.tubo(out, cuello, [2.4, 1.9], [P['piel']], semilla=13)
        Mh, boca = _cabeza_en(out, P, V, cuello[1] + np.array((0.0, 1.6, -0.6)), (0.0, -0.2, 1.0), 42.0, semilla=20)
        # la escarcha que le crece en los hombros
        for s_ in (1, -1):
            for k, (dx, dy, dz, h) in enumerate(((4.4, 35.6, 1.4, 2.4), (5.6, 34.8, 0.2, 1.8), (3.4, 36.0, 0.0, 1.6), (5.0, 35.2, 2.8, 1.4))):
                M = vr.T(s_ * dx, dy, dz) @ vr.Rz(-s_ * (0.3 + 0.15 * k)) @ vr.Rx(0.2 * (k - 1.5))
                caja(out, M, -0.5, 0.5, 0.0, h, -0.5, 0.5, P['hielo'], semilla=14 + k)
        # los brazos, largos y flacos, colgando abiertos hasta las rodillas
        for s_ in (1, -1):
            hombro, codo, muneca = np.array((s_ * 4.4, 34.0, 2.0)), np.array((s_ * 7.6, 26.0, 1.0)), np.array((s_ * 8.6, 17.0, 3.0))
            jm.tubo(out, [hombro, codo, muneca], [1.9, 1.3, 1.0], [P['piel'], P['piel']], semilla=30)
            caja(out, vr.T(*codo), -1.4, 1.4, -1.4, 1.4, -1.4, 1.4, P['piel'], semilla=31)
            garras(out, P, muneca, (0.0, -1.0, 0.15), (s_, 0.0, 0.0), semilla=32)
        # las patas de pezuna, abiertas, con la rodilla hacia delante y el corvejon hacia atras
        for s_ in (1, -1):
            cadera, rodilla, corvejon = np.array((s_ * 3.0, 21.0, -1.0)), np.array((s_ * 5.5, 13.5, 3.5)), np.array((s_ * 5.8, 7.0, -2.5))
            menudillo = np.array((s_ * 6.2, 1.8, -0.5))
            jm.tubo(out, [cadera, rodilla, corvejon, menudillo], [2.8, 1.6, 1.0, 0.9], [P['piel']] * 3, semilla=40)
            for q_, r_ in ((rodilla, 1.7), (corvejon, 1.1)):
                caja(out, vr.T(*q_), -r_, r_, -r_, r_, -r_, r_, P['piel'], semilla=41)
            pezuna(out, P, menudillo, np.array((s_ * 6.2, 0.0, 1.2)), semilla=42)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

"""
Sedara y sus tipos (15-10-2026). Juan, al guardar a Ayunara: «guardalo me gusto, y crea otro boss». Antes se probaron
y se aparcaron sin ensenarlos Mirmara (un hormiga-leon en su embudo de arena: con patas de insecto se leia como una
arana) y Aklutara (el akhlut inuit, orca y lobo: se leia como un perro negro tumbado, una mezcla de dos animales).

Sedara, la Sed del Monte: sale del chupacabras de Puerto Rico y de Mexico, el que baja de noche a los corrales y deja a
las cabras sin sangre. Del chupacabras le quedan rastros: los ojos grandes y encendidos, los dos colmillos largos para
beber, las patas fuertes de saltador, las manos de tres garras, la piel de cuero gris y, sobre todo, la fila de puas
que se le eriza por el lomo. Lo nuestro: esa cresta se abre desde la frente como un abanico detras de la cabeza y la
enmarca; y la cabeza manda, con las fauces abiertas que arden (el paladar en escalones, los dientes en hojas, los
colmillos y el nucleo al fondo).

Los tres tipos tienen la misma pose (agazapada sobre las patas de saltar, con los brazos tendidos para agarrar) y
cambian la cresta:

    A  las Puas      puas sueltas, largas y anilladas, que se abren en abanico; carmin
    B  la Erizada    ademas de la corona, puas por todo el lomo y los hombros, como un erizo; verde acido
    C  los Garfios   dos filas de garfios curvos hacia atras, como espinas de zarza; ambar
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

VARIANTES = {
    'A': dict(
        clave='SA', nombre='las Puas', corto='puas', cresta='puas',
        piel=_r('0a0c0c', '121616', '1c2222', '283030', '364040'),
        pua=_r('1a1614', '2e2824', '4a423a', '6e6458', '948a7c'),
        casco=_r('141210', '201c18', '2e2822', '3e362e', '524840'),
        neon=('ffe6ea', 'ff2a4a', '6a0414'),
    ),
    'B': dict(
        clave='SB', nombre='la Erizada', corto='erizada', cresta='erizo',
        piel=_r('0a0c08', '12160e', '1a2014', '242c1c', '303a26'),
        pua=_r('16180e', '262a18', '3c4226', '565e38', '76804e'),
        casco=_r('12140e', '1e2218', '2c3224', '3c4432', '505a44'),
        neon=('f6ffe6', '9aff2a', '2a5a04'),
    ),
    'C': dict(
        clave='SC', nombre='los Garfios', corto='garfios', cresta='garfios',
        piel=_r('0e0a08', '18120e', '241c16', '322820', '42362c'),
        pua=_r('1e160e', '342618', '503c26', '705638', '96764e'),
        casco=_r('16120e', '241e18', '362c24', '4a3e32', '625444'),
        neon=('fff4e0', 'ffb21a', '6a4004'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    """Los de Kelpia para lo comun (el ojo, el paladar, los dientes, el nucleo, las garras) y los propios: la piel de
    cuero, con arrugas de traves; las puas, anilladas; y la membrana de la Vela, en bandas."""
    W = dict(V, alga=V['piel'], mancha=V['piel'], hueso=V['pua'])
    P = km.pintores(W)
    k = V['clave']

    def reg(nombre, fn):
        fn.__name__ = 'sed%s_%s' % (k, nombre)
        P[nombre] = fn
        return fn

    def cuero(tw, th, cara, s):
        """El cuero: gris oscuro, con arrugas de traves que no llegan de lado a lado."""
        ys, xs = np.mgrid[0:th, 0:tw]
        de_traves, a_lo_largo = (xs, ys) if cara in ('arriba', 'abajo') else (ys, xs)
        idx = np.full((th, tw), 2)
        arruga = (a_lo_largo % 5 == 0) & (((de_traves // 3) + (a_lo_largo // 5)) % 3 != 0)
        idx = np.where(arruga, 1, idx)
        if cara == 'abajo':
            idx = idx + 1
        return _imagen(_bisel(idx, 1, 1), V['piel']), None
    reg('piel', cuero)

    def pua(tw, th, cara, s):
        """La pua: anillada en claro y oscuro, como las del puerco espin."""
        ys, xs = np.mgrid[0:th, 0:tw]
        de_traves, a_lo_largo = (xs, ys) if cara in ('arriba', 'abajo') else (ys, xs)
        idx = np.where((a_lo_largo // 3) % 2 == 0, 3, 1)
        return _imagen(idx, V['pua']), None
    reg('pua', pua)

    def vela(tw, th, cara, s):
        """La membrana de la Vela: oscura, en bandas que bajan a la base, con el canto de arriba un poco mas claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 3) % 2 == 0, 2, 1)
        idx = np.where(ys < 1, 3, idx)
        return _imagen(idx, V['piel']), None
    reg('vela', vela)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def cresta(out, P, linea, normales, largos, tipo, cerrada=True, semilla=0):
    """La cresta, a lo largo de la linea del lomo (de la frente hacia la cola): cada pua sale por su normal, echada un
    poco atras. 'puas': sueltas y anilladas; 'erizo': ademas, otras dos a los lados de cada una, por todo el lomo;
    'garfios': dos filas curvas hacia atras. ('vela', unidas por una membrana, se descarto: era la gola del
    dilofosaurio.)"""
    puntas = []
    for k, (q, n, L) in enumerate(zip(linea, normales, largos)):
        q, n = np.asarray(q, float), _u(n)
        atras = _u(np.asarray(linea[min(k + 1, len(linea) - 1)], float) - np.asarray(linea[max(k - 1, 0)], float)) if cerrada else np.zeros(3)
        if tipo == 'garfios':
            for lado in (1, -1):
                b = q + np.array((lado * 0.9, 0.0, 0.0))
                d = _u(n + np.array((lado * 0.35, 0.0, 0.0)))
                m = b + d * L * 0.55
                t = m + _u(d + atras * 1.3) * L * 0.5 - n * 0.4
                jm.tubo(out, [b, m, t], [0.75, 0.5, 0.1], [P['pua'], P['pua']], semilla=semilla + k % 3)
            continue
        d = _u(n + atras * 0.45)
        t = q + d * L
        jm.tubo(out, [q, q + d * L * 0.5, t], [0.7, 0.45, 0.08], [P['pua'], P['pua']], semilla=semilla + k % 3)
        puntas.append((q, t))
        if tipo == 'erizo' and cerrada:                                 # y dos mas a los lados, por todo el lomo
            lado = _u(np.cross(n, atras if np.linalg.norm(atras) > 0 else np.array((0.0, 0.0, 1.0))))
            for v in (1, -1):
                for f, a_ in ((1.6, 0.8), (3.0, 1.4)):
                    b = q + lado * v * f - _u(n) * 0.4 * a_
                    dd = _u(n + lado * v * a_ + atras * 0.5)
                    jm.tubo(out, [b, b + dd * L * 0.45, b + dd * L * 0.85], [0.6, 0.4, 0.08], [P['pua'], P['pua']], semilla=semilla + 3)
    if tipo == 'vela':
        for (q0, t0), (q1, t1) in zip(puntas, puntas[1:]):
            m0, m1 = q0 + (t0 - q0) * 0.9, q1 + (t1 - q1) * 0.9
            L = max(float(np.linalg.norm(m1 - m0)), 0.4)
            H = max(float(np.linalg.norm(m0 - q0)), 0.4)
            lamina(out, (q0, q1, m1, m0), P['vela'], L, H, semilla=semilla + 5)
            lamina(out, (q1, q0, m0, m1), P['vela'], L, H, semilla=semilla + 5)


def cabeza(out, Mh, P, abre=42.0, semilla=0):
    """La cabeza de Sedara, con el hocico hacia +z y la boca en y=0: ancha atras y afilada delante, con los ojos grandes
    y almendrados, encendidos y echados hacia atras, y dos ranuras por narices. Las fauces, abiertas desde muy atras: el
    paladar encendido en escalones, los dientes en hojas, los dos colmillos largos de beber arriba y dos mas cortos
    abajo, el suelo de la boca encendido y el nucleo al fondo. Devuelve la boca."""
    p = P['piel']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -3.2, 0.0, -4.0, 6.4, 4.2, 5.2, p, caras=F, semilla=semilla)                   # el craneo, ancho
    bm.cubo(out, Mh, -2.6, 0.3, 1.2, 5.2, 3.2, 3.0, p, caras=F, semilla=semilla + 1)               # el hocico, que se afila
    bm.cubo(out, Mh, -1.8, 0.6, 4.2, 3.6, 2.4, 1.8, p, caras=F, semilla=semilla + 2)
    for s in (1, -1):
        M = Mh @ vr.T(s * 2.4, 3.0, 0.4) @ vr.Rz(s * 0.3) @ vr.Ry(s * 0.35)                        # los ojos, grandes y rasgados
        caja(out, M, -0.9, 0.9, -0.55, 0.55, -1.4, 1.2, P['ojo'], semilla=semilla + 3)
        bm.cubo(out, Mh, 1.6 if s > 0 else -2.8, 3.9, -0.8, 1.2, 0.6, 2.2, p, semilla=semilla + 4)        # el parpado de arriba
        bm.cubo(out, Mh, s * 0.8 - 0.2, 2.6, 5.9, 0.4, 0.3, 0.2, P['casco'], semilla=semilla + 5)          # las narices, ranuras
    hilera(out, Mh, [(-2.4, 0.2), (-2.4, 5.6), (2.4, 5.6), (2.4, 0.2)], 0.6, -1.0, P['dientes_arriba'], semilla=semilla + 6)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.3, 0.6, 5.2), 4.6, 1.0, (0, -1, 0.08), P, semilla=semilla + 7)      # los colmillos de beber
    caja(out, Mh, -2.4, 2.4, -2.0, 0.2, -3.3, -3.0, P['nucleo'], semilla=semilla + 8)
    Mj = Mh @ vr.T(0.0, 0.0, -3.4) @ vr.Rx(abre * D)                                                # la quijada de abajo
    bm.cubo(out, Mj, -2.9, -2.6, -0.6, 5.8, 2.6, 4.6, p, caras={'arriba': P['boca']}, semilla=semilla + 9)
    bm.cubo(out, Mj, -2.2, -1.6, 4.0, 4.4, 1.6, 4.4, p, caras={'arriba': P['boca']}, semilla=semilla + 10)
    hilera(out, Mj, [(-2.0, 3.2), (-2.0, 8.2), (2.0, 8.2), (2.0, 3.2)], 0.0, 1.0, P['dientes_abajo'], semilla=semilla + 11)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.5, 0.0, 7.7), 2.2, 0.8, (0, 1, 0.05), P, semilla=semilla + 12)
    return pt(Mh, (0.0, -0.8, 2.6))


def mano(out, P, muneca, adelante, semilla=0):
    """La mano de tres dedos largos, abiertos hacia delante, con garras curvas hacia abajo."""
    muneca, f = np.asarray(muneca, float), _u(adelante)
    e = _u(np.cross((0.0, 1.0, 0.0), f))
    caja(out, vr.T(*muneca), -1.2, 1.2, -1.0, 1.0, -1.2, 1.2, P['piel'], semilla=semilla)
    for k, g in enumerate((-22, 0, 22)):
        d = _u(f * math.cos(g * D) + e * math.sin(g * D))
        a = muneca + d * 1.0
        b = a + d * 2.6 + np.array((0.0, 0.3, 0.0))
        c = b + d * 2.2 + np.array((0.0, -0.6, 0.0))
        jm.tubo(out, [a, b, c], [0.55, 0.45, 0.35], [P['piel'], P['piel']], semilla=semilla + 1)
        jm.tubo(out, [c, c + d * 1.2 + np.array((0.0, -0.4, 0.0)), c + d * 1.6 + np.array((0.0, -1.6, 0.0))], [0.38, 0.24, 0.05],
                [P['casco'], P['casco']], semilla=semilla + 2)


def pie(out, P, tobillo, punta, semilla=0):
    """El pie largo de saltador, apoyado, con tres dedos y sus garras."""
    tobillo, punta = np.asarray(tobillo, float), np.asarray(punta, float)
    jm.tubo(out, [tobillo, punta], [1.3, 1.0], [P['piel']], semilla=semilla)
    f = _u(np.array((punta[0] - tobillo[0], 0.0, punta[2] - tobillo[2])))
    e = _u(np.cross((0.0, 1.0, 0.0), f))
    for g in (-25, 0, 25):
        d = _u(f * math.cos(g * D) + e * math.sin(g * D))
        a = punta + d * 0.6
        b = a + d * 2.0
        jm.tubo(out, [a, b], [0.6, 0.5], [P['piel']], semilla=semilla + 1)
        jm.tubo(out, [b, b + d * 1.2 + np.array((0.0, -0.3, 0.0))], [0.4, 0.06], [P['casco']], semilla=semilla + 2)


# ======================================================================
#  SEDARA
# ======================================================================
def sedara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        cadera, pecho = np.array((0.0, 17.5, -4.0)), np.array((0.0, 26.0, 4.0))
        # el tronco, inclinado hacia delante
        ps, rs, _ = jm.a_lo_largo([cadera + np.array((0.0, -0.5, -2.0)), (cadera + pecho) / 2 + np.array((0.0, 0.6, -0.6)), pecho], 6,
                                  ((0.0, 3.6), (0.5, 2.8), (1.0, 4.0)))
        jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=10, achata=1.1)
        cuello = [pecho + np.array((0.0, 1.0, 1.0)), np.array((0.0, 29.0, 8.0))]
        jm.tubo(out, cuello, [3.2, 2.6], [P['piel']], semilla=11)
        R = em.marco((0.0, 0.0, 0.0), _u(np.array((0.0, -0.25, 1.0))), up=(0.0, 1.0, 0.0))
        nuca = np.array((0.0, 31.0, 8.5))
        o = nuca - pt(R, np.array((0.0, 4.2, -3.6)) * CABEZA)
        Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
        bm.PPB = PPB / CABEZA
        boca = cabeza(out, Mh, P, abre=42.0, semilla=20)
        bm.PPB = PPB
        # la cola, corta y fina
        cps, crs, _ = jm.a_lo_largo([cadera + np.array((0.0, -0.5, -2.0)), np.array((0.0, 13.0, -10.0)), np.array((0.0, 9.0, -14.0))], 6,
                                    ((0.0, 2.6), (1.0, 0.5)))
        jm.tubo(out, cps, crs, [P['piel']] * (len(cps) - 1), semilla=12)
        # la cresta: de la frente, por el cuello y el lomo, hasta la grupa
        linea, normales, largos = [], [], []
        abanico = []                                                    # en la nuca, un abanico de puas alrededor de la cabeza
        for k, g in enumerate(np.linspace(-78.0, 78.0, 9)):
            a = g * D
            q = pt(Mh, (math.sin(a) * 2.8, 2.6 + math.cos(a) * 2.2, -3.6))
            n = Mh[:3, :3] @ np.array((math.sin(a), math.cos(a) * 0.9, -0.55))
            abanico.append((q, n, 13.0 - 5.0 * abs(g) / 78.0))
        cresta(out, P, [q for q, _, _ in abanico], [n for _, n, _ in abanico], [L for _, _, L in abanico], V['cresta'],
               cerrada=False, semilla=25)
        for t in np.linspace(0.0, 1.0, 9):                              # por el cuello y el lomo
            i = t * (len(ps) - 1)
            j = min(int(i), len(ps) - 2)
            w = i - j
            q = np.asarray(ps[len(ps) - 1 - j], float) * (1 - w) + np.asarray(ps[len(ps) - 2 - j], float) * w
            r = rs[len(rs) - 1 - j] * (1 - w) + rs[len(rs) - 2 - j] * w
            arriba = _u(np.cross(np.cross(_u(pecho - cadera), (0.0, 1.0, 0.0)), _u(pecho - cadera)))
            arriba = -arriba if arriba[1] < 0 else arriba
            linea.append(q + arriba * r * 0.9)
            normales.append(arriba + np.array((0.0, 0.0, -0.3)))
            largos.append(8.5 - 5.0 * t)
        cresta(out, P, linea, normales, largos, V['cresta'], semilla=30)
        # los brazos, tendidos hacia delante para agarrar
        for s in (1, -1):
            hombro, codo, muneca = np.array((s * 4.0, 25.0, 4.5)), np.array((s * 9.5, 20.0, 3.5)), np.array((s * 12.0, 15.0, 9.0))
            jm.tubo(out, [hombro, codo, muneca], [2.0, 1.4, 1.0], [P['piel'], P['piel']], semilla=40)
            caja(out, vr.T(*codo), -1.7, 1.7, -1.7, 1.7, -1.7, 1.7, P['piel'], semilla=41)
            mano(out, P, muneca, (s * 0.45, -0.1, 1.0), semilla=42)
        # las patas de saltador: el muslo grueso, la rodilla delante y el corvejon alto atras
        for s in (1, -1):
            c, rodilla, tobillo = np.array((s * 3.4, 17.0, -4.0)), np.array((s * 5.6, 11.0, 4.0)), np.array((s * 5.4, 5.5, -5.5))
            jm.tubo(out, [c, rodilla, tobillo], [3.4, 2.0, 1.2], [P['piel'], P['piel']], semilla=50)
            caja(out, vr.T(*rodilla), -2.0, 2.0, -2.0, 2.0, -2.0, 2.0, P['piel'], semilla=51)
            pie(out, P, tobillo, np.array((s * 5.8, 0.9, 3.0)), semilla=52)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

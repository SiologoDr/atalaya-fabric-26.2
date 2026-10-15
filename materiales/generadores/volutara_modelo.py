"""
Volutara y sus formas (14-10-2026). Juan, al aprobar a Kelpia: «ahora si me gusto, excelente trabajo, este si se
acerco a lo que busco… hagamos el siguiente boss». La leccion de Kelpia: un monstruo inventado, con solo rastros de la
referencia, y una idea propia que mande en la silueta.

Volutara, la Ermitana del Mar Seco: un monstruo que vive dentro de una caracola gigante y la carga, como un ermitano.
Del caracol le quedan rastros: la concha en espiral, los ojos en la punta de dos tallos y la radula (la boca llena de
filas de dientecillos). Todo lo demas es nuestro: sale de la concha con un cuerpo grueso y oscuro, se apoya en dos
brazos fuertes con garras y brazales de concha, y la cabeza manda por delante, ancha, con las fauces abiertas que arden
(el paladar en escalones, los dientes en hojas, los colmillos, el suelo de la boca con la radula encendida y el nucleo
al fondo). La boca de la caracola, forrada de nacar, se abre detras de la cabeza como una capucha y la enmarca.

Las tres formas cambian la concha, y con ella la silueta:

    A  la Torre      una caracola alta, en espiral de cuatro vueltas, que sube hacia atras; arena con bandas; cian
    B  la Rueda      una concha de amonites, enroscada en un plano y de pie sobre el lomo como una rueda, con
                     costillas; bronce; magenta
    C  la Corona     una caracola baja y ancha (la caracola arana) cuyo labio se abre en siete dedos largos y curvos
                     alrededor de la cabeza, como una corona de garras; marfil; naranja
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
import sierpe_modelo as sm
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
ESCALA = 0.7
CABEZA = 1.3

VARIANTES = {
    'A': dict(
        clave='VA', nombre='la Torre', corto='torre', concha_forma='torre',
        piel=_r('080a10', '0e121a', '161c26', '202834', '2c3644'),
        concha=_r('2a2014', '4a3a24', '6e5836', '94784a', 'b89a62'),
        banda=_r('180e08', '28160c', '3a2012', '4e2c18', '643a20'),
        nacar=_r('4a4652', '76707e', 'a49cac', 'cec6d4', 'eee8f2'),
        casco=_r('14161a', '22262c', '343a42', '4a525c', '626c78'),
        neon=('e8fcff', '2ad8ff', '04406a'),
    ),
    'B': dict(
        clave='VB', nombre='la Rueda', corto='rueda', concha_forma='rueda',
        piel=_r('0c0810', '140e1a', '1e1626', '2a2034', '382a44'),
        concha=_r('1e1a10', '3a2e16', '5e4a22', '86702e', 'b09a44'),
        banda=_r('120e08', '201810', '302416', '42341e', '584628'),
        nacar=_r('4a4250', '786c80', 'a898ae', 'd2c4d6', 'f2e8f4'),
        casco=_r('16121a', '241e2a', '362e3e', '4c4256', '645870'),
        neon=('ffe6fa', 'ff3ad0', '5a0448'),
    ),
    'C': dict(
        clave='VC', nombre='la Corona', corto='corona', concha_forma='corona',
        piel=_r('0a0c08', '12160e', '1a2016', '242c1e', '303a28'),
        concha=_r('2a2622', '4a443c', '6e665a', '968c7c', 'bab2a2'),
        banda=_r('1a1410', '2a201a', '3c2e24', '50402e', '66523c'),
        nacar=_r('524a46', '807670', 'aca29a', 'd4cac2', 'f2ece6'),
        casco=_r('16140e', '262218', '383224', '4e4634', '665c46'),
        neon=('fff0e2', 'ff5a1a', '6a1a04'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    """Los de Kelpia para lo comun (la piel, el ojo, el paladar, los dientes, el nucleo, la garra) y los propios: la
    concha de cada forma, el nacar y el suelo de la boca con la radula."""
    W = dict(V, alga=V['concha'], hueso=V['concha'], mancha=V['concha'])
    P = km.pintores(W)
    k = V['clave']
    nuc, neo, hon = V['neon']

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'vol%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    forma = V['concha_forma']

    def concha(tw, th, cara, s):
        """La concha: en la Torre, bandas a lo largo de la espiral; en la Rueda, costillas de traves; en la Corona,
        lisa, con una linea de crecimiento de traves cada poco y una banda clara a lo largo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        de_traves, a_lo_largo = (xs, ys) if cara in ('arriba', 'abajo') else (ys, xs)     # en las cajas de los tubos
        if forma == 'torre':
            idx = np.where((de_traves % 12) < 5, 3, 2)
            t = _imagen(idx, V['concha'])
            banda = (de_traves % 12) >= 9
            t[banda] = _imagen(np.full((th, tw), 2), V['banda'])[banda]
            return t, None
        if forma == 'rueda':
            idx = np.where(a_lo_largo % 6 < 2, 4, np.where(a_lo_largo % 6 < 3, 3, 2))
            idx = np.where(a_lo_largo % 6 == 5, 1, idx)
            return _imagen(idx, V['concha']), None
        idx = np.where((de_traves // 3) % 4 == 1, 3, 2)
        idx = np.where(a_lo_largo % 10 == 0, 1, idx)
        return _imagen(idx, V['concha']), None
    reg('concha', concha)

    def nacar(tw, th, cara, s):
        """El nacar del labio: liso y claro, en ondas suaves de traves."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((ys + xs // 3) // 3) % 3 == 0, 4, 3)
        idx = np.where(((ys + xs // 3) // 3) % 5 == 4, 2, idx)
        return _imagen(idx, V['nacar']), None
    reg('nacar', nacar)

    hondo = jm.liso([V['piel'][0], V['piel'][0], V['piel'][1], V['piel'][2], V['piel'][3]], 1, 1, 0)   # lo de dentro, en sombra
    reg('hondo', hondo)

    def boca(tw, th, cara, s):
        """El suelo de la boca: la radula, una cinta de filas de dientecillos en pico que brillan, con la encia oscura a
        los lados."""
        ys, xs = np.mgrid[0:th, 0:tw]
        u = np.abs((xs + 0.5) / tw - 0.5) * 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((u > 0.7)[..., None], np.array(V['piel'][1]), np.array(c_h))
        fila = (ys - (np.abs(xs - (tw - 1) / 2) * 0.6).astype(int)) % 4
        diente = (u <= 0.7) & (fila == 0)
        col = np.where(diente[..., None], np.array(qm._mezcla(c_m, c_n, 0.35)), col)
        col = np.where(((u <= 0.7) & (fila == 1))[..., None], np.array(c_m), col)
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, u <= 0.7, 110)
    reg('boca', boca)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def garras(out, P, base, adelante, escala=1.0, semilla=0):
    """Tres garras de cuerno, gruesas, abiertas hacia delante y con la punta en gancho hacia el suelo."""
    base, adelante = np.asarray(base, float), _u(adelante)
    e = _u(np.cross((0.0, 1.0, 0.0), adelante))
    abajo = np.array((0.0, -1.0, 0.0))
    for g in (-30, 0, 30):
        d = _u(adelante * math.cos(g * D) + e * math.sin(g * D))
        p0 = base + d * 0.8 * escala
        p1 = p0 + d * 2.2 * escala + abajo * 0.2 * escala
        p2 = p1 + d * 1.2 * escala + abajo * 1.4 * escala
        jm.tubo(out, [p0, p1, p2], [0.95 * escala, 0.7 * escala, 0.18 * escala], [P['casco'], P['casco']], semilla=semilla)


def cabeza(out, Mh, P, abre=34.0, semilla=0):
    """La cabeza de Volutara, con el hocico hacia +z y la boca en y=0: ancha y redonda por arriba, con una quilla y dos
    montes de los que salen los tallos de los ojos (no tiene otros), un labio ancho por delante y, a los lados de las
    fauces, dos tentaculos cortos que se curvan hacia abajo. Las fauces, abiertas desde muy atras: el paladar encendido en
    escalones, los dientes en hojas, dos pares de colmillos arriba y uno abajo, el suelo de la boca con la radula
    encendida y el nucleo al fondo. Devuelve la boca y las bases de los dos tallos."""
    p = P['piel']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -3.4, 0.0, -4.0, 6.8, 4.4, 5.5, p, caras=F, semilla=semilla)                   # el craneo
    bm.cubo(out, Mh, -2.6, 4.4, -3.4, 5.2, 0.9, 4.2, p, semilla=semilla + 1)                       # y su lomo, redondo
    bm.cubo(out, Mh, -3.0, 0.3, 1.5, 6.0, 3.4, 4.5, p, caras=F, semilla=semilla + 2)               # el hocico
    bm.cubo(out, Mh, -3.2, 0.5, 5.6, 6.4, 1.8, 1.4, p, caras=F, semilla=semilla + 3)               # el labio, ancho
    bm.cubo(out, Mh, -2.2, 3.7, 1.8, 4.4, 0.6, 3.6, p, semilla=semilla + 4)                        # el caballete
    bm.cubo(out, Mh, -0.6, 5.2, -3.2, 1.2, 0.7, 4.6, p, semilla=semilla + 12)                       # la quilla
    for s in (1, -1):
        bm.cubo(out, Mh, s * 1.6 - 1.0, 4.9, -2.6, 2.0, 0.8, 2.0, p, semilla=semilla + 13)            # los montes de los tallos
        q = [pt(Mh, (s * 3.0, 1.6, 5.4)), pt(Mh, (s * 4.6, 0.8, 7.2)), pt(Mh, (s * 5.2, -1.6, 7.8)), pt(Mh, (s * 4.6, -3.4, 7.0))]
        ps, rs, _ = jm.a_lo_largo(q, 6, ((0.0, 1.0 * CABEZA), (0.6, 0.7 * CABEZA), (1.0, 0.25 * CABEZA)))   # los tentaculos
        jm.tubo(out, ps, rs, [p] * (len(ps) - 1), semilla=semilla + 14)
    hilera(out, Mh, [(-2.9, 0.2), (-2.9, 6.8), (2.9, 6.8), (2.9, 0.2)], 0.6, -1.2, P['dientes_arriba'], semilla=semilla + 5)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.9, 0.6, 6.4), 3.2, 1.0, (0, -1, 0.1), P, semilla=semilla + 6)
        colmillo(out, Mh, (s * 2.7, 0.6, 3.0), 2.3, 0.8, (0, -1, 0.0), P, semilla=semilla + 6)
    caja(out, Mh, -2.4, 2.4, -2.0, 0.2, -3.3, -3.0, P['nucleo'], semilla=semilla + 7)
    Mj = Mh @ vr.T(0.0, 0.0, -3.5) @ vr.Rx(abre * D)                                                # la quijada de abajo
    bm.cubo(out, Mj, -3.2, -3.8, -0.8, 6.4, 3.8, 5.4, p, caras={'arriba': P['boca']}, semilla=semilla + 8)
    bm.cubo(out, Mj, -2.9, -2.5, 4.6, 5.8, 2.5, 5.8, p, caras={'arriba': P['boca']}, semilla=semilla + 9)
    hilera(out, Mj, [(-2.6, 3.4), (-2.6, 10.1), (2.6, 10.1), (2.6, 3.4)], 0.0, 1.1, P['dientes_abajo'], semilla=semilla + 10)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.9, 0.0, 9.6), 2.5, 0.9, (0, 1, 0.08), P, semilla=semilla + 11)
    return pt(Mh, (0.0, -0.8, 3.0)), [pt(Mh, (s * 1.6, 5.1, -1.6)) for s in (1, -1)]


def tallo(out, P, base, puntas, semilla=0):
    """Un tallo de ojo: un tubo blando que sube ondulado, con anillos oscuros, y el ojo encendido en la punta."""
    pts = [np.asarray(base, float)] + [np.asarray(q, float) for q in puntas]
    ps, rs, _ = jm.a_lo_largo(pts, 8, ((0.0, 1.2), (0.7, 0.8), (1.0, 0.75)))
    jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=semilla)
    for q, r in list(zip(ps, rs))[2:-1:2]:
        caja(out, vr.T(*q), -r * 1.15, r * 1.15, -0.25, 0.25, -r * 1.15, r * 1.15, P['casco'], semilla=semilla + 1)
    q = np.asarray(ps[-1], float)
    caja(out, vr.T(*q), -1.3, 1.3, -1.1, 1.3, -1.3, 1.3, P['ojo'], semilla=semilla + 2)
    caja(out, vr.T(*q), -1.55, 1.55, -1.3, -0.7, -1.55, 1.55, P['piel'], semilla=semilla + 3)       # el parpado de abajo


def _espiral(forma, r1, ap):
    """Los puntos y los radios de la concha, de la punta (o el centro) a la boca, que queda en ap mirando hacia +z.
    'torre' y 'corona' suben en cono; 'rueda' se enrosca en el plano x=0."""
    ap = np.asarray(ap, float)
    pts, rad, ejes = [], [], []
    if forma == 'rueda':
        R1, Rmin, vueltas = r1 * 1.55, 1.6, 2.6
        k = math.log(R1 / Rmin) / (TAU * vueltas)
        C = ap + np.array((0.0, R1, 0.0))
        n = 90
        for i in range(n + 1):
            phi = -TAU * vueltas * (1 - i / n)
            R = R1 * math.exp(k * phi)
            pts.append(C + R * np.array((0.0, -math.cos(phi), math.sin(phi))))
            rad.append(r1 * R / R1)
        return pts, rad, C, np.array((1.0, 0.0, 0.0))
    vueltas, alto, rmin = (4.5, 3.0, 0.8) if forma == 'torre' else (2.6, 1.6, 1.6)
    K = math.log(r1 / rmin)
    n = 110 if forma == 'torre' else 80
    loc = []
    for i in range(n + 1):
        s = i / n
        r = r1 * math.exp(-K * (1 - s))
        th = TAU * vueltas * s
        R = r * 1.12
        loc.append((np.array((-R * math.cos(th), alto * (r1 - r), R * math.sin(th))), r))
    e, t = loc[-1][0], _u(loc[-1][0] - loc[-2][0])                     # la boca y hacia donde se abre
    psi = math.atan2(t[0], t[2])
    inclina = -0.42 if forma == 'torre' else -0.25
    M = vr.T(*ap) @ vr.Rx(inclina) @ vr.Ry(-psi) @ vr.T(*(-e))
    for q, r in loc:
        pts.append(pt(M, q))
        rad.append(r)
    eje = _u(M[:3, :3] @ np.array((0.0, 1.0, 0.0)))
    return pts, rad, pt(M, (0.0, 0.0, 0.0)), eje


def concha(out, P, forma, r1, ap, semilla=0):
    """La caracola: el tubo en espiral que crece hasta la boca; en la Rueda, las costillas de traves. Luego el labio
    de nacar, abierto alrededor de la boca y mas alto por arriba, como una capucha, y lo hondo de dentro, en sombra; en
    la Corona, el labio se abre en siete dedos largos y curvos alrededor de la cabeza."""
    pts, rad, centro, eje = _espiral(forma, r1, ap)
    jm.tubo(out, pts, rad, [P['concha']] * (len(pts) - 1), semilla=semilla, arriba=eje if forma != 'rueda' else (1.0, 0.0, 0.0))
    if forma == 'rueda':                                                # las costillas
        for i in range(4, len(pts) - 2, 4):
            a, b = np.asarray(pts[i], float), np.asarray(pts[i + 1], float)
            d = _u(b - a)
            jm.tubo(out, [a - d * 0.25, a + d * 0.25], [rad[i] * 1.14, rad[i] * 1.14], [P['concha']], semilla=semilla + 1,
                    arriba=(1.0, 0.0, 0.0))
    # el labio de nacar y lo hondo
    ap = np.asarray(ap, float)
    d = _u(np.asarray(pts[-1], float) - np.asarray(pts[-2], float))
    M = em.marco(ap + d * r1 * 0.4, d, up=(0.0, 1.0, 0.0))
    caja(out, M, -r1 * 0.92, r1 * 0.92, -r1 * 0.92, r1 * 0.92, 0.2, 0.6, P['hondo'], semilla=semilla + 5)
    caja(out, M, -r1 * 0.66, r1 * 0.66, -r1 * 1.0, r1 * 1.0, 0.2, 0.6, P['hondo'], semilla=semilla + 5)
    caja(out, M, -r1 * 1.0, r1 * 1.0, -r1 * 0.66, r1 * 0.66, 0.2, 0.6, P['hondo'], semilla=semilla + 5)
    n = 18
    anillo = []
    for i in range(n + 1):
        a = TAU * i / n
        c, s_ = math.cos(a), math.sin(a)
        fuera = r1 * (1.32 + 0.55 * max(0.0, s_) ** 1.5)
        dentro = pt(M, (c * r1 * 0.95, s_ * r1 * 0.95, 0.6))
        borde = pt(M, (c * fuera, s_ * fuera, 1.6 + 1.6 * max(0.0, s_)))
        anillo.append((dentro, borde, s_))
    for (a0, b0, s0), (a1, b1, s1) in zip(anillo, anillo[1:]):
        if min(a0[1], a1[1], b0[1], b1[1]) < 0.3:
            continue
        L = max(float(np.linalg.norm(a1 - a0)), 0.4)
        H = max(float(np.linalg.norm(b0 - a0)), 0.4)
        lamina(out, (a0, a1, b1, b0), P['nacar'], L, H, semilla=semilla + 6)
        lamina(out, (a1, a0, b0, b1), P['concha'], L, H, semilla=semilla + 7)
    if forma == 'corona':                                               # los siete dedos del labio
        for k, g in enumerate(np.linspace(-25.0, 205.0, 7)):
            a = g * D
            c, s_ = math.cos(a), math.sin(a)
            fuera = r1 * (1.32 + 0.55 * max(0.0, s_) ** 1.5)
            base = pt(M, (c * fuera * 0.92, s_ * fuera * 0.92, 1.4 + 1.4 * max(0.0, s_)))
            largo = r1 * (1.25 if k in (2, 3, 4) else 1.0)
            m1 = pt(M, (c * (fuera + largo * 0.45), s_ * (fuera + largo * 0.45), 3.0 + 2.0 * max(0.0, s_)))
            m2 = pt(M, (c * (fuera + largo * 0.85), s_ * (fuera + largo * 0.85) + 1.0, 3.0 + 1.0 * max(0.0, s_)))
            punta = pt(M, (c * (fuera + largo * 1.05), s_ * (fuera + largo * 1.05) + 3.0, 0.5))      # la punta, en gancho
            if min(base[1], m1[1], m2[1], punta[1]) < 0.5:
                continue
            ps, rs, _ = jm.a_lo_largo([base, m1, m2, punta], 7, ((0.0, 1.5), (0.6, 0.9), (1.0, 0.2)))
            jm.tubo(out, ps, rs, [P['concha']] * (len(ps) - 1), semilla=semilla + 8)
            jm.tubo(out, ps[:4], [r * 0.7 for r in rs[:4]], [P['nacar']] * 3, semilla=semilla + 9)
    return centro


def _cabeza_en(out, P, nuca, mira, abre, semilla=0):
    R = em.marco((0.0, 0.0, 0.0), _u(np.array(mira, float)), up=(0.0, 1.0, 0.0))
    o = np.asarray(nuca, float) - pt(R, np.array((0.0, 5.3, -3.6)) * CABEZA)
    Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
    bm.PPB = PPB / CABEZA
    boca, bases = cabeza(out, Mh, P, abre=abre, semilla=semilla)
    bm.PPB = PPB
    return Mh, boca, bases


# ======================================================================
#  VOLUTARA
# ======================================================================
def volutara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    forma = V['concha_forma']
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        r1 = {'torre': 10.0, 'rueda': 8.5, 'corona': 10.0}[forma]
        ap = np.array((0.0, 6.0 + r1, -6.0))                           # la boca de la concha, a la altura de la cabeza
        concha(out, P, forma, r1, ap, semilla=10)
        # el pie: ancho y chato, en el suelo, debajo de la concha
        jm.tubo(out, [np.array((0.0, 2.6, -15.0)), np.array((0.0, 3.0, -5.0)), np.array((0.0, 2.8, 3.0))], [3.6, 5.2, 4.6],
                [P['piel'], P['piel']], semilla=19, arriba=(0.0, 1.0, 0.0), achata=0.62)
        # el cuerpo, que sale de la concha y baja al pie
        jm.tubo(out, [ap + np.array((0.0, -2.5, -3.0)), np.array((0.0, 8.0, 0.5)), np.array((0.0, 3.5, 1.5))], [r1 * 0.6, 5.2, 4.4],
                [P['piel'], P['piel']], semilla=20)
        pecho = ap + np.array((0.0, -0.5, 7.0))
        jm.tubo(out, [ap + np.array((0.0, -1.0, -3.0)), pecho], [r1 * 0.68, 5.4], [P['piel']], semilla=21)
        # la cabeza, por delante, en medio del nacar
        Mh, boca, bases = _cabeza_en(out, P, pecho + np.array((0.0, 7.0, 0.5)), (0.0, -0.3, 1.0), 34.0, semilla=30)
        # los tallos de los ojos
        for s, b in zip((1, -1), bases):
            puntas = [pt(Mh, (s * 2.6, 9.0, -0.6)), pt(Mh, (s * 3.8, 12.4, 1.2)), pt(Mh, (s * 4.2, 14.2, 3.2))]
            tallo(out, P, b, puntas, semilla=40)
        # los brazos, con los brazales de concha, bajando al suelo
        for s in (1, -1):
            h = pecho + np.array((s * 4.6, -1.5, -0.5))
            codo = pecho + np.array((s * 10.5, -2.0, 0.5))
            muneca = np.array((s * 11.0, 3.2, pecho[2] + 6.5))
            mano = np.array((s * 11.1, 1.9, pecho[2] + 8.2))
            jm.tubo(out, [h, codo, muneca, mano], [3.0, 2.6, 2.3, 1.9], [P['piel']] * 3, semilla=50)
            caja(out, vr.T(*codo), -2.6, 2.6, -2.6, 2.6, -2.6, 2.6, P['piel'], semilla=51)
            dd = muneca - codo
            jm.tubo(out, [codo + dd * 0.2, codo + dd * 0.78], [2.85, 2.6], [P['concha']], semilla=52, arriba=(s, 0.0, 0.0))
            caja(out, vr.T(*mano), -2.0, 2.0, -1.2, 1.2, -1.6, 1.8, P['piel'], semilla=53)
            garras(out, P, mano + np.array((0.0, 0.0, 1.0)), (s * 0.15, 0.0, 1.0), escala=1.4, semilla=54)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

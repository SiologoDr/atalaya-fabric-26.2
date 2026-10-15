"""
Caribdis y sus formas (14-10-2026). Juan, al rechazar a Tifon: «sigamos con otro boss y sus tipos». Lo que si gusto ese
dia fueron las jefas del bestiario griego (la Gorgona y Escila), asi que la siguiente es Caribdis, la pareja de Escila en
el mito: la hija de Poseidon que se convirtio en el monstruo que se traga el mar.

Una jefa con el cuerpo de jefa_modelo (el de la Gorgona y Escila: mujer adulta de cajas y la cara C3 con mirada de
jefa), con los brazos en alto, llamando al remolino; el quiton oscuro con el ribete de nacar, la melena que flota como
en el agua y una tiara de nacar con una perla que arde. No tiene piernas: sale, sobre un tallo de carne, del fondo de
unas fauces colosales que arden por dentro en escalones (de la sombra al neon y al blanco del nucleo), con los dientes
dibujados en hojas.

Las tres formas cambian las fauces, y con ellas la silueta:

    A  el Remolino     un crater de fauces en el suelo: el labio de escamas con puas, los escalones de luz que bajan
                       hasta el nucleo y un anillo de dientes en cada escalon; ella en el centro; azul de abismo
    B  el Leviatan     unas mandibulas gigantes: la de abajo en el suelo, con la lengua, y la de arriba alzada detras de
                       ella como un arco, con los ojos encendidos y los dientes colgando; carmesi
    C  la Concha       una concha abierta: la valva de abajo, honda, y la de arriba alzada en abanico detras de ella, con
                       los radios, el borde de dientes y los ojos que arden a lo largo del borde; perla dorada
"""
import math
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
import escila_modelo as es
from escila_modelo import hilera, colmillo, _u

TAU = math.tau
D = vr.D2R
_r = bm._r
GRANDE = 1.2
CADERA_Y = 21.0                                   # a que altura le quedan las caderas (unidades de la jefa)
NACAR = es.NACAR

VARIANTES = {
    'A': dict(
        clave='A', nombre='el Remolino', corto='remolino',
        piel=_r('6c7884', '92a0ac', 'b6c4ce', 'd0dce4', 'eef4f8'),
        pelo=_r('04080e', '08101a', '0e1a28', '162638', '22364c'),
        tela=_r('040a12', '08121e', '0e1c2c', '16283c', '223850'),
        escama=_r('040a12', '08121e', '0e1c2c', '16283c', '223850'),
        mar=_r('04070c', '080e16', '0e1620', '16202c', '202c3a'),
        vientre=_r('162030', '223044', '30425a', '425672', '58708e'),
        aleta=_r('04070c', '080e16', '0c141e', '121c28', '1a2634'),
        coral=NACAR, concha=_r('1a2230', '2a3446', '3e4a60', '56647c', '74849c'),
        oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('04060a', '0a0e14', '12161e', '1c222c', '28303c'),
        pelaje=_r('04070c', '080e16', '0e1620', '16202c', '202c3a'), medias=NACAR,
        neon=('eef6ff', '3a9aff', '06244a'), ojos=('3a9aff', '0a3a7a', 'b0d8ff'), labios='4a5664', marca='16283c',
    ),
    'B': dict(
        clave='B', nombre='el Leviatan', corto='leviatan',
        piel=_r('7c6a6a', 'a28e8e', 'c6b2b0', 'e0cecc', 'f6eceb'),
        pelo=_r('0e0406', '1a080a', '2a0e12', '3e161a', '562026'),
        tela=_r('12060a', '200a10', '301018', '441822', '5c222e'),
        escama=_r('12060a', '200a10', '301018', '441822', '5c222e'),
        mar=_r('0c0606', '160c0c', '201212', '2c1a1a', '3a2424'),
        vientre=_r('2e1e1c', '442c2a', '5e403c', '7a5650', '987068'),
        aleta=_r('0c0606', '160c0c', '1c0e0e', '261414', '321c1c'),
        coral=NACAR, concha=_r('2e1e1c', '442c2a', '5e403c', '7a5650', '987068'),
        oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('0a0606', '140c0c', '1e1414', '2a1e1e', '3a2a2a'),
        pelaje=_r('0c0606', '160c0c', '201212', '2c1a1a', '3a2424'), medias=NACAR,
        neon=('ffe2e6', 'ff2a46', '6a0410'), ojos=('ff2a46', '8a0a14', 'ffa0aa'), labios='6a2a30', marca='8a1a24',
    ),
    'C': dict(
        clave='C', nombre='la Concha', corto='concha',
        piel=_r('7e7062', 'a4968a', 'c8bcae', 'e2d8cc', 'f8f2ea'),
        pelo=_r('100a04', '1e1408', '2e200e', '423016', '5a4420'),
        tela=_r('1a1408', '2a2010', '3e3018', '544222', '6e5a30'),
        escama=_r('1a1408', '2a2010', '3e3018', '544222', '6e5a30'),
        mar=_r('0e0c08', '18140e', '221e16', '2e281e', '3c3428'),
        vientre=_r('3a3020', '544632', '706048', '8e7c62', 'ae9c80'),
        aleta=_r('0e0c08', '18140e', '1e1a12', '282218', '342c20'),
        coral=NACAR, concha=_r('3e3426', '5a4e3a', '7a6c54', '9c8e72', 'c0b294'),
        oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('0a0806', '14100c', '1e1812', '2a2218', '382e22'),
        pelaje=_r('0e0c08', '18140e', '221e16', '2e281e', '3c3428'), medias=NACAR,
        neon=('fff8e6', 'ffd27a', '6a4a10'), ojos=('ffd27a', '8a6014', 'fff0c0'), labios='6a5040', marca='544222',
    ),
}
for _v in VARIANTES.values():
    _v.setdefault('ribete', NACAR)
    _v.setdefault('guante', _v['tela'])


def pintores(V):
    """Los de Escila (cuerpo de jefa y monstruo) y los de Caribdis: los escalones de luz de las fauces, la carne honda y
    la concha en radios."""
    P = es.pintores(V)
    reg = P['_reg']
    nuc, neo, hon = V['neon']
    c_n, c_m, c_h = (np.array(nm._hex(c)) for c in (nuc, neo, hon))

    def escalon(col, brilla):
        def f(tw, th, cara, s):
            t = np.zeros((th, tw, 4), np.uint8)
            ys, xs = np.mgrid[0:th, 0:tw]
            base = np.array(col)
            raya = (ys % 4 == 0)
            t[..., :3] = np.where(raya[..., None], base * 0.82, base)
            t[..., 3] = 255
            return t, (_emis(t, np.ones((th, tw), bool), brilla) if brilla else None)
        return f
    reg('carne', escalon(c_h * 0.55, 0))
    reg('paso1', escalon(c_h, 150))
    reg('paso2', escalon(qm._mezcla(c_h, c_m, 0.6), 210))
    reg('paso3', escalon(c_m, 235))
    reg('paso4', escalon(qm._mezcla(c_m, c_n, 0.55), 245))

    def concha(tw, th, cara, s):
        """La concha: radios anchos con el surco oscuro y el lomo claro, en bandas de crecimiento."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = xs % 7
        idx = np.where(f == 0, 1, np.where(f < 3, 2, np.where(f < 6, 3, 4)))
        idx = np.where(ys % 9 == 0, idx - 1, idx)
        return _imagen(np.clip(idx, 0, 4), V['concha']), None
    reg('concha', concha)
    return P


# ----------------------------------------------------------------------
#  Piezas del monstruo
# ----------------------------------------------------------------------
def anillo(out, r_in, r_out, y0, y1, pintor, n=32, semilla=0):
    """Un anillo de cajas alrededor del eje (una banda de r_in a r_out, de y0 a y1)."""
    rm = (r_in + r_out) / 2
    for k in range(n):
        a = TAU * (k + 0.5) / n
        p = np.array((math.sin(a) * rm, y0, math.cos(a) * rm))
        tang = np.array((math.cos(a), 0.0, -math.sin(a)))
        M = em.marco(p, tang, up=(0.0, 1.0, 0.0))
        L = TAU * r_out / n
        caja(out, M, -(r_out - r_in) / 2, (r_out - r_in) / 2, 0.0, y1 - y0, -L / 2 - 0.08, L / 2 + 0.08, pintor, semilla=semilla + k % 3)


def corona_de_dientes(out, P, r, y, alto, n=28, semilla=0):
    """Un anillo de dientes dibujados en hojas, en el borde de un escalon, que suben."""
    pts = [(math.sin(TAU * k / n) * r, math.cos(TAU * k / n) * r) for k in range(n + 1)]
    hilera(out, jm.I4, pts, y, alto, P['dientes_abajo'], semilla=semilla)


def crater(out, P, semilla=0):
    """A: el crater de fauces: el labio de escamas con puas por fuera, los escalones de luz que bajan hasta el nucleo y
    un anillo de dientes en el borde de cada escalon."""
    anillo(out, 24.0, 29.0, 0.0, 8.5, P['mar'], n=36, semilla=semilla)                                # el labio
    anillo(out, 23.0, 25.0, 8.0, 9.2, P['vientre_mar'], n=36, semilla=semilla + 1)
    for k in range(18):                                                                                # las puas del labio
        a = TAU * (k + 0.25) / 18
        p = np.array((math.sin(a) * 28.0, 6.0, math.cos(a) * 28.0))
        es_ = np.array((math.sin(a), 0.6, math.cos(a)))
        jm.tubo(out, [p, p + es_ * 3.0, p + es_ * 5.5 + np.array((0.0, 1.0, 0.0))], [0.9, 0.55, 0.2], [P['hueso'] if 'hueso' in P else P['garra']] * 2,
                semilla=semilla + 2)
    pasos = ((19.0, 24.0, 6.6, 'carne'), (14.0, 19.0, 5.0, 'paso1'), (9.5, 14.0, 3.6, 'paso2'), (5.0, 9.5, 2.4, 'paso3'),
             (0.0, 5.0, 1.2, 'paso4'))
    for j, (ri, ro, y1, pin) in enumerate(pasos):
        anillo(out, max(ri, 0.6), ro, 0.0, y1, P[pin], n=max(10, int(ro * 1.5)), semilla=semilla + 3 + j)
        if ri > 1:
            corona_de_dientes(out, P, ri + 0.4, y1, 4.2 - j * 0.7, n=max(14, int(ri * 1.6)), semilla=semilla + 10 + j)
    corona_de_dientes(out, P, 24.2, 6.6, 4.8, n=40, semilla=semilla + 20)


def mandibulas(out, P, semilla=0):
    """B: las mandibulas del leviatan: la de abajo en el suelo, en U, con el suelo de la boca encendido, la lengua y los
    dientes que suben; y la de arriba, alzada detras de ella como un arco, con el paladar encendido por debajo, los
    dientes y los colmillos que cuelgan, los ojos encendidos y las puas del lomo. Devuelve los ojos."""
    m = P['mar']
    for j, (z0, z1, w) in enumerate(((-14.0, -4.0, 28.0), (-4.0, 6.0, 26.0), (6.0, 13.0, 22.0), (13.0, 18.0, 16.0), (18.0, 21.0, 9.0))):
        bm.cubo(out, jm.I4, -w / 2, 0.0, z0, w, 4.0, z1 - z0, m, caras={'arriba': P['boca']}, semilla=semilla + j % 2)
    caja(out, jm.I4, -5.0, 5.0, 4.0, 5.2, -10.0, 12.0, P['carne'], semilla=semilla + 3)                 # la lengua
    pts = [(-13.4, -12.0), (-12.6, 6.0), (-10.6, 13.0), (-7.6, 18.0), (-4.2, 20.6), (4.2, 20.6), (7.6, 18.0), (10.6, 13.0),
           (12.6, 6.0), (13.4, -12.0)]
    hilera(out, jm.I4, pts, 4.0, 3.6, P['dientes_abajo'], semilla=semilla + 4)
    for x in (-6.0, 6.0):
        colmillo(out, jm.I4, (x, 4.0, 19.0), 6.0, 1.8, (0, 1, 0.1), P, semilla=semilla + 5)
    Ma = vr.T(0.0, 4.5, -13.0) @ vr.Rx(-68 * D)                                                        # la de arriba, alzada
    for j, (z0, z1, w) in enumerate(((0.0, 10.0, 28.5), (10.0, 20.0, 26.5), (20.0, 27.0, 22.5), (27.0, 32.0, 16.5), (32.0, 35.0, 9.5))):
        bm.cubo(out, Ma, -w / 2, -1.0, z0, w, 5.0, z1 - z0, m, caras={'abajo': P['paso2']}, semilla=semilla + 6 + j % 2)
    pts = [(-13.6, 2.0), (-12.8, 20.0), (-10.8, 27.0), (-7.8, 32.0), (-4.4, 34.6), (4.4, 34.6), (7.8, 32.0), (10.8, 27.0),
           (12.8, 20.0), (13.6, 2.0)]
    hilera(out, Ma, pts, -1.0, -4.0, P['dientes_arriba'], semilla=semilla + 8)
    for x in (-6.5, 6.5):
        colmillo(out, Ma, (x, -1.0, 33.0), 7.0, 2.0, (0, -1, 0.1), P, semilla=semilla + 9)
    ojos = []
    for s in (1, -1):                                                                                  # los ojos
        caja(out, Ma, s * 9.0 - 2.0, s * 9.0 + 2.0, 3.6, 5.4, 22.0, 25.0, P['ojo_perro'], semilla=semilla + 10)
        caja(out, Ma, s * 9.0 - 2.6, s * 9.0 + 2.6, 5.2, 6.0, 21.0, 26.0, m, semilla=semilla + 11)
        ojos.append(pt(Ma, (s * 9.0, 6.5, 23.5)))
    for k in range(7):                                                                                 # las puas del lomo
        p = pt(Ma, (0.0, 4.0, 4.0 + k * 4.2))
        d = Ma[:3, :3] @ np.array((0.0, 1.0, -0.3))
        jm.tubo(out, [p, p + _u(d) * (4.0 - abs(k - 3) * 0.5)], [0.9, 0.2], [P['garra']], semilla=semilla + 12)
    return ojos


def concha(out, P, semilla=0):
    """C: la concha abierta: la valva de abajo, honda, en el suelo, y la de arriba alzada en abanico detras de ella; las
    dos con los radios por fuera y el nacar encendido por dentro; el borde de dientes en hojas y los ojos que arden a lo
    largo del borde de la de arriba. Devuelve dos ojos."""
    n = 13
    ojos = []
    for valva, (ang0, r, alto, inclina) in enumerate(((0.0, 24.0, 5.0, 0.0), (0.0, 30.0, 0.0, 74.0))):
        Mv = vr.T(0.0, 1.0, -12.0) @ vr.Rx(-inclina * D) if valva == 1 else vr.T(0.0, 0.0, -12.0)
        base = np.array((0.0, 0.0, 0.0))
        bordes = []
        for k in range(n + 1):
            a = (-80 + 160 * k / n) * D
            u = np.array((math.sin(a), 0.0, math.cos(a)))
            bordes.append(u * r + np.array((0.0, alto if valva == 0 else 0.0, 0.0)))
        for k in range(n):
            a0, a1 = pt(Mv, bordes[k]), pt(Mv, bordes[k + 1])
            c0 = pt(Mv, base + np.array((0.0, 0.0 if valva else 0.0, 0.0)))
            hond = pt(Mv, (bordes[k] + bordes[k + 1]) * 0.5 + np.array((0.0, -3.5 if valva == 0 else 0.0, 0.0)))
            if valva == 1:
                hond = pt(Mv, (bordes[k] + bordes[k + 1]) * 0.5 + np.array((0.0, 3.0, 0.0)))
            ancho = float(np.linalg.norm(a1 - a0))
            largo = float(np.linalg.norm(a0 - c0))
            lamina(out, (c0, c0, a1, a0), P['paso3'], ancho, largo, semilla=semilla + valva)            # el nacar, por dentro
            lamina(out, (c0, c0, a0, a1), P['concha'], ancho, largo, semilla=semilla + valva)
            jm.tubo(out, [c0, hond * 0.0 + (a0 + a1) / 2 + (pt(Mv, (0.0, 2.6, 0.0)) - pt(Mv, (0.0, 0.0, 0.0))) * (1 if valva else 0)],
                    [0.8, 1.6], [P['concha']], semilla=semilla + 2)
        borde = [pt(Mv, b) for b in bordes]
        jm.tubo(out, borde, [1.0] * len(borde), [P['concha']] * (len(borde) - 1), semilla=semilla + 3)
        for k in range(n):                                                                             # los dientes del borde
            a0, a1 = borde[k], borde[k + 1]
            hacia = (pt(Mv, (0.0, 0.0, 0.0)) - (a0 + a1) / 2)
            arriba_ = np.cross(a1 - a0, hacia)
            if valva == 0:
                if arriba_[1] < 0:
                    arriba_ = -arriba_
            else:
                if arriba_[2] < 0:
                    arriba_ = -arriba_
            h = _u(arriba_) * 3.2
            lamina(out, (a0, a1, a1 + h, a0 + h), P['dientes_abajo'], float(np.linalg.norm(a1 - a0)), 3.2, semilla=semilla + 4)
            lamina(out, (a1, a0, a0 + h, a1 + h), P['dientes_abajo'], float(np.linalg.norm(a1 - a0)), 3.2, semilla=semilla + 4)
            if valva == 1 and k % 2 == 0:                                                              # los ojos del borde
                q = (a0 + a1) / 2 + _u(arriba_) * -1.2 + _u(-hacia) * 0.6
                caja(out, vr.T(*q), -0.9, 0.9, -0.9, 0.9, -0.9, 0.9, P['ojo_perro'], semilla=semilla + 5)
                ojos.append(q)
    return ojos[len(ojos) // 2 - 1: len(ojos) // 2 + 1]


def jefa(out, P, V, semilla=0):
    """La mujer: el torso con el quiton, los brazos en alto, la cabeza C3, la melena que flota y la tiara con la perla;
    alzada sobre el tallo de carne que sale de las fauces. Devuelve la cara."""
    sup = []
    tl = P['tela_lisa']
    bm.PPB = jm.PPB * GRANDE
    jm.torso(sup, P, {'cadera': tl, 'cintura': tl, 'pecho': tl, 'busto': P['tela'], 'ribete': P['nacar']})
    caja(sup, jm.I4, -3.6, 3.6, 30.6, 31.4, -2.2, 2.2, P['nacar'], semilla=50)                        # el cinturon de perlas
    for s in (1, -1):
        jm.brazo(sup, P, s, 'B2', dict(abd=150, flex=12, codo=26, giro=-40, mun=-10, cierra=0.15),
                 {'manga': None, 'puno': P['nacar']})
    Mh = vr.T(0.0, jm.CUELLO_Y, 0.2) @ vr.Rx(4 * D)
    jm.cabeza(sup, Mh, P, V)
    caja(sup, Mh, -4.55, 4.55, -2.0, 7.0, -4.95, -3.6, P['pelo'], semilla=59)
    for k in range(9):                                                                                 # la melena que flota
        f = (k - 4) / 4
        b = pt(Mh, (f * 3.8, 5.0 - abs(f) * 2.5, -4.2))
        fuera = np.array((f * 1.0, 0.0, 0.0))
        ctrl = [b, b + fuera * 5.0 + np.array((0.0, 2.0, -4.0)), b + fuera * 10.0 + np.array((0.0, -1.0 + abs(f) * 3.0, -6.0)),
                b + fuera * 14.0 + np.array((0.0, -6.0 + abs(f) * 6.0, -4.0))]
        ps, rs, _ = jm.a_lo_largo(ctrl, 8, ((0.0, 1.2), (0.6, 0.9), (1.0, 0.35)))
        jm.tubo(sup, ps, rs, [P['pelo']] * (len(ps) - 1), semilla=60 + k % 4)
    for k in range(7):                                                                                 # la tiara de nacar
        x = (k - 3) * 1.25
        h = 2.8 - abs(k - 3) * 0.55
        caja(sup, Mh, x - 0.35, x + 0.35, 7.6, 7.6 + h, 3.4, 4.1, P['nacar'], semilla=70)
    caja(sup, Mh, -0.7, 0.7, 7.7, 9.1, 4.1, 4.8, P['luz'], semilla=72)                               # la perla
    bm.PPB = jm.PPB
    Ms = vr.T(0.0, CADERA_Y, 0.0) @ np.diag([GRANDE] * 3 + [1.0]) @ vr.T(0.0, -24.0, 0.0)
    out += qm.transformar(sup, Ms)
    # el tallo de carne, de las caderas al fondo de las fauces, con un faldon de aletas
    ps, rs, _ = jm.a_lo_largo([np.array((0.0, CADERA_Y + 1.0, 0.0)), np.array((0.0, CADERA_Y - 6.0, 0.6)), np.array((0.0, 1.0, 0.0))], 6,
                              ((0.0, 5.0), (0.5, 4.2), (1.0, 6.0)))
    jm.tubo(out, ps, rs, [P['mar']] * (len(ps) - 1), semilla=semilla)
    for k in range(10):
        a = TAU * k / 10
        u = np.array((math.sin(a), 0.0, math.cos(a)))
        b = np.array((0.0, CADERA_Y + 1.5, 0.0)) + u * 4.6
        dirs = [u * 0.6 + np.array((0.0, -1.0, 0.0)) + np.array((math.cos(a), 0.0, -math.sin(a))) * t for t in (-0.35, 0.0, 0.35)]
        es.aleta_rayos(out, P, b, dirs, [6.0, 7.0, 6.0], semilla=semilla + 2)
    return pt(Ms @ Mh, (0.0, 4.0, 4.2))


# ======================================================================
#  CARIBDIS
# ======================================================================
def caribdis(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    if 'hueso' not in P:
        P['hueso'] = P['nacar']
    ppb = bm.PPB
    bm.PPB = jm.PPB
    out = []
    try:
        cara = jefa(out, P, V, semilla=80)
        if tipo == 'A':
            crater(out, P, semilla=100)
            luces = [np.array((0.0, 2.0, 0.0)), np.array((0.0, 5.0, 16.0)), np.array((0.0, 5.0, -16.0))]
        elif tipo == 'B':
            luces = [np.array((0.0, 6.0, 10.0))] + mandibulas(out, P, semilla=100)
        else:
            luces = [np.array((0.0, 4.0, 6.0))] + concha(out, P, semilla=100)
    finally:
        bm.PPB = ppb
    E = np.diag([jm.ESCALA] * 3 + [1.0])
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    return out, {'boca': luces[0], 'luces': luces, 'cara': pt(E, cara)}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

"""
Tifon y sus formas (14-10-2026). Juan, al guardar a Escila: «me gusta este, dejalo en fichas y sigamos con otro».
El bestiario griego hecho monstruo, como la Gorgona, el Minotauro, Cerbero y Escila: el quinto es Tifon, el padre de
los monstruos.

Un titan de escamas oscuras: de la cintura para arriba, el torso macizo con los escudos del vientre, los hombros de
hueso con puas, los brazos con garras y una cabeza de dragon con cuernos y las fauces abiertas que arden por dentro
(el paladar en escalones, los dientes dibujados en hojas, cuatro colmillos y el nucleo al fondo). De la cintura para
abajo, dos serpientes enormes que bajan al suelo, dan la vuelta y se alzan a los lados, cada una con su cabeza de
fauces encendidas. Lo que le enmarca la cabeza es la melena de cabezas de dragon que le brota de los hombros.

Las tres formas cambian la silueta:

    A  Tifon                    la cabeza de dragon con la melena de seis cabezas; ambar
    B  el de las Cien Cabezas   no tiene cabeza propia: del cuello le sale una corona de nueve cabezas de dragon, la
                                del medio mas grande; cian de tormenta
    C  el del Etna              la cabeza con los cuernos mas grandes y la melena; sale de un monte de roca volcanica
                                con grietas de lava, con las serpientes enroscadas en el; magma
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
from sierpe_modelo import _bisel, _degradado, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.55
CABEZA = 1.75
DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')

VARIANTES = {
    'A': dict(
        clave='A', nombre='Tifon', corto='tifon',
        escama=_r('0c0a08', '16130e', '221d16', '302820', '42382c'),
        vientre=_r('2a2014', '403220', '58462e', '72603e', '8e7a52'),
        hueso=_r('4a4030', '6e624a', '948666', 'b8aa88', 'd8ccac'),
        cuerno=_r('1a140c', '2e2416', '463822', '5e4e32', '7a6646'),
        neon=('fff2d6', 'ffaa22', '6a3a04'),
    ),
    'B': dict(
        clave='B', nombre='el de las Cien Cabezas', corto='cien',
        escama=_r('080a0e', '0e1218', '161c24', '202834', '2c3646'),
        vientre=_r('1a2028', '28323e', '3a4656', '505e70', '6a7a8e'),
        hueso=_r('3e4650', '5c6672', '7e8894', 'a0aab4', 'c2cad2'),
        cuerno=_r('0e1218', '18202a', '263040', '344256', '485870'),
        neon=('eefcff', '5ae0ff', '0a4a6a'),
    ),
    'C': dict(
        clave='C', nombre='el del Etna', corto='etna',
        escama=_r('0e0806', '180e0a', '24140e', '321c14', '44261c'),
        vientre=_r('2a1a10', '40281a', '583826', '724a32', '8e6042'),
        hueso=_r('4a3a30', '6e5648', '947666', 'b89888', 'd8baac'),
        cuerno=_r('180c08', '2a140c', '421e12', '5a2a1a', '763a24'),
        roca=_r('0c0a0a', '161414', '201c1c', '2c2626', '3a3232'),
        neon=('fff0e0', 'ff4a14', '6a1004'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'tif%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']
    reg('escama', lambda tw, th, c, s: (_imagen(_bisel(sm._escamas_cara(tw, th, c), 1, 1), V['escama']), None))
    reg('vientre', lambda tw, th, c, s: (_imagen(sm._escudos(tw, th, 4), V['vientre']), None))
    reg('hueso', jm.liso(V['hueso'], 3, 1, 1))
    reg('garra', jm.liso(_r('060504', '0e0c0a', '181512', '24201b', '322c26'), 2, 1, 1))

    def cuerno(tw, th, cara, s):
        """El cuerno: en anillos, con la junta oscura y el canto claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        largo_y = th >= tw
        v = ys if largo_y else xs
        idx = np.where(v % 4 == 0, 1, np.where(v % 4 == 1, 3, 2))
        return _imagen(idx, V['cuerno']), None
    reg('cuerno', cuerno)

    def roca(tw, th, cara, s):
        """La roca del volcan: oscura, en manchas grandes, con grietas de lava que arden."""
        idx = sm._manchas(tw, th, s, celda=8.0, umbral=0.6, alto=0.8)
        idx = np.array([1, 2, 2, 3, 3])[idx]
        t = _imagen(_bisel(idx), V.get('roca', V['escama']))
        ys, xs = np.mgrid[0:th, 0:tw]
        x = xs + ((ys // 3) % 2) * 2 + (s % 9)
        grieta = ((x % 14) < 2) & ((ys // 9) % 3 != 2)
        c_m = np.array(nm._hex(neo))
        t[..., :3] = np.where(grieta[..., None], c_m, t[..., :3])
        return t, _emis(t, grieta, 220)
    reg('roca', roca)

    def ojo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = nm._hex(neo)
        t[..., 3] = 255
        if tw >= 3:
            t[:, tw // 2, :3] = nm._hex(nuc)
        return t, _emis(t, np.ones((th, tw), bool), 230)
    reg('ojo', ojo)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def boca(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        u = (xs + 0.5) / tw
        dd = np.minimum(u, 1 - u) * 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((dd < 0.2)[..., None], np.array(c_h),
                       np.where((dd < 0.46)[..., None], np.array(qm._mezcla(c_h, c_m, 0.6)),
                                np.where((dd < 0.76)[..., None], np.array(c_m), np.array(qm._mezcla(c_m, c_n, 0.6)))))
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, dd >= 0.2, 230)
    reg('boca', boca)

    def nucleo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((r < 0.45)[..., None], np.array(c_n),
                       np.where((r < 0.8)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m)))
        col = np.where((r > 1.0)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 1.0, 240)
    reg('nucleo', nucleo)

    def _hojas_de_dientes(tw, th, colgando):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTES]
        n = max(1, (tw + 1) // 5)
        x0 = (tw - (n * 5 - 1)) // 2
        for i in range(n):
            x = x0 + i * 5
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.68)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)
                if f > 0.85:
                    pix = ((x + 1, c[4]),)
                elif f > 0.6:
                    pix = ((x + 1, c[4]), (x + 2, c[3]))
                else:
                    pix = ((x, c[2]), (x + 1, c[4]), (x + 2, c[3]), (x + 3, c[1]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
        return t, None
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, False))

    def colmillo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [np.array((*cc, 255)) for cc in DIENTES]
        for y in range(th):
            f = y / max(th - 1, 1)
            w = (1.0 - f) ** 0.8 * tw / 2
            cx = (tw - 1) / 2
            for x in range(tw):
                d = x - cx
                if abs(d) <= w:
                    t[y, x] = c[4] if d < -w * 0.2 else (c[3] if d < w * 0.4 else c[1])
        return t, None
    reg('colmillo', colmillo)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def _u(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado, h = float(np.linalg.norm(B - A)), float(np.linalg.norm(A2 - A))
        if alto < 0:
            lamina(out, (A2, B2, B, A), pintor, lado, h, semilla + j)
            lamina(out, (B2, A2, A, B), pintor, lado, h, semilla + j)
        else:
            lamina(out, (A, B, B2, A2), pintor, lado, h, semilla + j)
            lamina(out, (B, A, A2, B2), pintor, lado, h, semilla + j)


def colmillo(out, M, base, largo, ancho, abajo, P, semilla=0):
    b = pt(M, base)
    d = _u(M[:3, :3] @ np.asarray(abajo, float))
    for lado in (M[:3, 0], M[:3, 2]):
        l = _u(lado - d * (lado @ d))
        p0, p1 = b - l * ancho / 2, b + l * ancho / 2
        q0, q1 = p0 + d * largo, p1 + d * largo
        lamina(out, (q0, q1, p1, p0), P['colmillo'], ancho, largo, semilla)
        lamina(out, (q1, q0, p0, p1), P['colmillo'], ancho, largo, semilla)


def pua(out, p, d, r, h, pintor, semilla=0):
    M = em.marco(np.asarray(p, float), np.asarray(d, float))
    caja(out, M, -r, r, -r, r, -0.4, h * 0.45, pintor, semilla=semilla)
    caja(out, M, -r * 0.64, r * 0.64, -r * 0.64, r * 0.64, h * 0.4, h * 0.76, pintor, semilla=semilla + 1)
    caja(out, M, -r * 0.32, r * 0.32, -r * 0.32, r * 0.32, h * 0.72, h, pintor, semilla=semilla + 2)


def cuerno(out, P, M, base, dirs, largos, grueso, semilla=0):
    """Un cuerno en anillos, de tramos que se afinan y se curvan (dirs en el marco M)."""
    p = pt(M, base)
    for j, (d, L) in enumerate(zip(dirs, largos)):
        q = p + _u(M[:3, :3] @ np.asarray(d, float)) * L
        g = grueso * (1.0 - 0.27 * j)
        jm.tubo(out, [p, q], [g, g * 0.8], [P['cuerno']], semilla=semilla + j)
        p = q


def cabeza_dragon(out, Mh, P, abre=34.0, cuernos=1.0, semilla=0):
    """La cabeza de dragon, con el hocico hacia +z: el craneo con el ceno en angulo y los ojos encendidos; los
    cuernos echados atras, en anillos; las puas de las mejillas; el hocico ancho con el caballete y las fosas; y las
    fauces abiertas: el paladar encendido, los dientes en hojas, dos colmillos arriba y dos abajo, el suelo de la
    boca encendido y el nucleo al fondo; y las puas de la barbilla. Devuelve el centro de la boca."""
    e = P['escama']
    caja(out, Mh, -3.6, 3.6, 0.0, 5.0, -3.8, 2.4, e, semilla=semilla)                                 # el craneo
    caja(out, Mh, -3.0, 3.0, 4.8, 5.8, -3.4, 1.0, e, semilla=semilla + 1)
    for s in (1, -1):
        x0, x1 = sorted((s * 1.7, s * 3.3))
        caja(out, Mh, x0, x1, 3.4, 4.1, 2.35, 2.6, P['ojo'], semilla=semilla + 2)                     # los ojos
        Mc = Mh @ vr.T(s * 2.4, 4.45, 2.45) @ vr.Rz(s * 20 * D)                                       # el ceno
        caja(out, Mc, -1.8, 1.8, -0.3, 0.6, -0.7, 0.7, P['hueso'], semilla=semilla + 3)
        if cuernos > 0:                                                                                # los cuernos
            cuerno(out, P, Mh, (s * 2.6, 5.2, -1.4), [(s * 0.5, 0.7, -0.8), (s * 0.3, 0.3, -1.0), (s * 0.1, -0.2, -1.0),
                                                       (s * 0.0, -0.6, -0.6)], [4.0 * cuernos, 3.6 * cuernos, 3.0 * cuernos, 2.2 * cuernos],
                   0.95 * min(1.3, cuernos), semilla=semilla + 4)
        for k in range(2):                                                                             # las puas de las mejillas
            pua(out, pt(Mh, (s * 3.5, 1.2 - k * 1.2, -1.5 - k * 1.2)), Mh[:3, :3] @ np.array((s * 1.0, -0.1, -0.8)), 0.4, 2.6 - k * 0.6,
                P['hueso'], semilla=semilla + 5)
    bm.cubo(out, Mh, -2.8, 0.8, 2.3, 5.6, 2.6, 7.2, e, caras={'abajo': P['fauces']}, semilla=semilla + 6)   # el hocico
    caja(out, Mh, -1.5, 1.5, 3.2, 3.9, 2.3, 9.0, P['hueso'], semilla=semilla + 7)
    for s in (1, -1):
        caja(out, Mh, s * 1.4 - 0.35, s * 1.4 + 0.35, 2.4, 3.2, 9.45, 9.6, P['garra'], semilla=semilla + 8)   # las fosas
    hilera(out, Mh, [(-2.55, 2.6), (-2.55, 9.2), (2.55, 9.2), (2.55, 2.6)], 0.85, -1.2, P['dientes_arriba'], semilla=semilla + 9)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.9, 0.85, 8.6), 3.0, 1.0, (0, -1, 0.05), P, semilla=semilla + 10)
    caja(out, Mh, -2.0, 2.0, -1.6, 0.85, 2.0, 2.3, P['nucleo'], semilla=semilla + 11)                 # el nucleo
    Mj = Mh @ vr.T(0, 0.8, 1.4) @ vr.Rx(abre * D)                                                     # la mandibula
    bm.cubo(out, Mj, -2.6, -1.8, 0.0, 5.2, 1.8, 8.2, e, caras={'arriba': P['boca'], 'abajo': P['vientre']}, semilla=semilla + 12)
    hilera(out, Mj, [(-2.35, 1.2), (-2.35, 8.0), (2.35, 8.0), (2.35, 1.2)], 0.0, 1.1, P['dientes_abajo'], semilla=semilla + 13)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.8, 0.0, 7.4), 2.4, 0.9, (0, 1, 0.05), P, semilla=semilla + 14)
    for k in range(3):                                                                                 # las puas de la barbilla
        pua(out, pt(Mj, ((k - 1) * 1.4, -1.6, 4.5 - abs(k - 1) * 1.2)), Mj[:3, :3] @ np.array(((k - 1) * 0.3, -1.0, -0.3)), 0.35,
            2.0, P['hueso'], semilla=semilla + 15)
    return pt(Mh, (0.0, 0.4, 5.2))


def cuello_con_cabeza(out, P, ctrl, r0, r1, mira, escala, abre=32.0, cuernos=0.6, semilla=0):
    """Un cuello de serpiente por la curva y, al final, una cabeza de dragon a la escala dada que mira hacia 'mira'.
    Devuelve el centro de la boca."""
    ps, rs, _ = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], 10, ((0.0, r0), (0.7, r1), (1.0, r1 * 1.1)))
    jm.tubo(out, ps, rs, [P['escama']] * (len(ps) - 1), semilla=semilla)
    mira = _u(mira)
    Mc = em.marco(ps[-1], mira, up=(0.0, 1.0, 0.0)) @ vr.T(0, -2.2 * escala, -1.8 * escala) @ np.diag([escala] * 3 + [1.0])
    ppb = bm.PPB
    bm.PPB = PPB / escala
    boca = cabeza_dragon(out, Mc, P, abre=abre, cuernos=cuernos, semilla=semilla + 20)
    bm.PPB = ppb
    return boca


def torso(out, P):
    """El torso de titan: la cintura con los escudos del vientre por delante, el pecho ancho y hondo de escamas con
    los pectorales, los hombros de hueso con tres puas cada uno y la cresta de puas por la espalda."""
    e = P['escama']
    caja(out, jm.I4, -5.4, 5.4, 22.0, 27.6, -3.8, 3.8, e, semilla=100)                               # la cintura
    caja(out, jm.I4, -5.8, 5.8, 27.4, 32.6, -4.0, 4.0, e, semilla=101)
    for j, y in enumerate((22.6, 24.4, 26.2, 28.0, 29.8, 31.6)):                                      # los escudos del vientre
        caja(out, jm.I4, -3.4 + 0.1 * (j < 3), 3.4, y, y + 1.6, 3.6, 4.4, P['vientre'], semilla=102 + j % 2)
    caja(out, jm.I4, -8.0, 8.0, 32.4, 41.2, -4.8, 4.8, e, semilla=105)                               # el pecho
    for s_ in (1, -1):                                                                                 # los pectorales
        x0, x1 = sorted((s_ * 0.3, s_ * 7.2))
        caja(out, jm.I4, x0, x1, 35.0, 40.6, 4.6, 5.9, e, semilla=106)
    caja(out, jm.I4, -9.6, 9.6, 38.8, 43.0, -4.4, 4.4, e, semilla=107)                               # los hombros
    for s_ in (1, -1):                                                                                 # las hombreras de hueso
        for j in range(3):
            M = vr.T(s_ * (7.5 + 0.6 * j), 43.0 - 0.6 * j, -1.5 + 1.8 * j) @ vr.Rz(-s_ * (18 + 14 * j) * D)
            caja(out, M, -2.6, 2.6, -1.2, 0.6, -2.0, 2.0, P['hueso'], semilla=108)
            pua(out, pt(M, (0.0, 0.5, 0.0)), M[:3, :3] @ np.array((0.0, 1.0, -0.2)), 0.6, 3.6 - 0.6 * j, P['hueso'], semilla=109)
    caja(out, jm.I4, -2.4, 2.4, 42.6, 46.0, -2.6, 2.4, e, semilla=110)                               # el cuello
    for j in range(6):                                                                                 # la cresta de la espalda
        pua(out, (0.0, 26.0 + j * 3.2, -4.6 - 0.2 * j), (0.0, 0.4, -1.0), 0.55, 2.6 + (j % 2) * 0.8, P['hueso'], semilla=111)


HOMBRO = np.array((11.0, 39.6, 0.0))
L_BRAZO, L_ANTEBRAZO = 10.0, 9.0


def brazo(out, P, s, pose):
    """Un brazo enorme de escamas: el brazo, el antebrazo con las puas de hueso por fuera y la mano de garra."""
    Mh = (vr.T(s * HOMBRO[0], HOMBRO[1], HOMBRO[2]) @ vr.Rz(s * pose.get('abd', 10) * D) @ vr.Rx(-pose.get('flex', 0) * D)
          @ vr.Ry(-s * pose.get('giro', 0) * D))
    Mc = Mh @ vr.T(0, -L_BRAZO, -3.3) @ vr.Rx(-pose.get('codo', 10) * D) @ vr.T(0, 0, 3.6)
    Mm = Mc @ vr.T(0, -L_ANTEBRAZO, 0) @ vr.Rx(-pose.get('mun', 0) * D)
    e = P['escama']
    caja(out, Mh, -3.2, 3.2, -L_BRAZO, 2.0, -3.2, 3.2, e, semilla=120)
    caja(out, Mh, -3.9, 3.9, -3.6, 3.2, -3.9, 3.9, e, semilla=121)                                   # el deltoide
    caja(out, Mc, -3.5, 3.5, -L_ANTEBRAZO, 0.0, -3.5, 3.5, e, semilla=122)
    caja(out, Mc, -3.7, 3.7, -L_ANTEBRAZO + 0.2, -L_ANTEBRAZO + 2.0, -3.7, 3.7, P['hueso'], semilla=123)   # la muñequera de hueso
    for j in range(3):                                                                                 # las puas del antebrazo
        pua(out, pt(Mc, (s * 3.4, -1.6 - 2.4 * j, -1.0)), Mc[:3, :3] @ np.array((s * 1.0, 0.4, -0.6)), 0.5, 2.6 - 0.4 * j,
            P['hueso'], semilla=124)
    return jm.mano(out, Mm, s, 'garra', e, una=P['garra'], k=2.7, cierra=pose.get('cierra', 0.4))


def pierna_serpiente(out, P, s, alzada=True, semilla=0):
    """Una pierna de serpiente: baja de la cadera, llega al suelo, da la vuelta por detras y se alza a un lado,
    por delante, con su cabeza de fauces encendidas. Devuelve la boca."""
    ctrl = [(s * 3.4, 24.0, -1.0), (s * 6.0, 14.0, -6.5), (s * 9.5, 4.8, -9.5), (s * 15.5, 3.6, -7.0), (s * 18.5, 3.6, 1.0),
            (s * 17.0, 4.2, 8.0), (s * 20.5, 10.0, 9.5), (s * 22.5, 18.0, 7.5), (s * 21.5, 25.0, 8.0)]
    ps, rs, _ = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], 22, ((0.0, 5.4), (0.3, 4.6), (0.6, 3.8), (1.0, 3.0)))
    jm.tubo(out, ps, rs, [P['escama']] * (len(ps) - 1), semilla=semilla)
    for k in range(1, len(ps) - 1, 2):                                                                # los escudos por debajo
        d = ps[k + 1] - ps[k - 1]
        abajo = _u(np.cross(d, np.array((s * 1.0, 0.0, 0.0))))
        if abajo[1] > 0:
            abajo = -abajo
        M = em.marco(ps[k] + abajo * rs[k] * 0.86, d, up=-abajo)
        caja(out, M, -rs[k] * 0.62, rs[k] * 0.62, -0.25, 0.25, -0.9, 0.9, P['vientre'], semilla=semilla + 1)
    mira = np.array((-s * 0.3, -0.1, 1.0))
    return cuello_con_cabeza(out, P, [ps[-1], ps[-1] + np.array((-s * 0.6, 3.5, 2.0)), ps[-1] + np.array((-s * 1.2, 5.5, 5.0))],
                             3.0, 2.8, mira, 1.15, abre=38.0, cuernos=0.6, semilla=semilla + 2)


def melena(out, P, n, tam, semilla=0):
    """La melena de cabezas de dragon que brota de los hombros y la espalda, en abanico detras de la cabeza y mirando
    hacia delante. Devuelve las bocas."""
    bocas = []
    for j in range(n):
        f = (j - (n - 1) / 2) / max((n - 1) / 2, 1)                                                   # de -1 a 1
        a = f * 78 * D                                                                                # en arco
        b = np.array((f * 7.0, 41.5 - abs(f) * 1.5, -3.5))
        R_ = 15.0
        fin = np.array((math.sin(a) * R_, 47.0 + math.cos(a) * R_ * 0.75, 0.5))
        ctrl = [b, b + np.array((f * 2.0, 5.0, -3.5)), (b + fin) / 2 + np.array((0.0, 2.0, -3.0)), fin]
        mira = np.array((f * 0.55, -0.12, 1.0))
        bocas.append(cuello_con_cabeza(out, P, ctrl, 2.0 * tam / 0.6, 1.6 * tam / 0.6, mira, tam, abre=30.0 + (j % 2) * 8,
                                       cuernos=0.45, semilla=semilla + j))
    return bocas


def corona_de_cabezas(out, P, semilla=0):
    """B: donde iria la cabeza, una corona de nueve cabezas de dragon que salen del cuello en abanico, la del medio
    mas grande y mas alta. Devuelve las bocas, la del medio primero."""
    bocas = []
    base = np.array((0.0, 44.0, 0.0))
    orden = [0, -1, 1, -2, 2, -3, 3, -4, 4]
    for j, k in enumerate(orden):
        f = k / 4
        tam = 1.35 if k == 0 else 0.92 - 0.04 * abs(k)
        a = f * 82 * D
        R_ = 15.0 if k == 0 else 17.0
        fin = base + np.array((math.sin(a) * R_, 4.0 + math.cos(a) * R_ * 0.8, 1.5))
        b = base + np.array((f * 3.0, -1.0, -0.5))
        ctrl = [b, b + np.array((f * 3.0, 4.0, -2.0)), (b + fin) / 2 + np.array((0.0, 1.5, -1.5)), fin]
        mira = np.array((f * 0.6, -0.15, 1.0))
        bocas.append(cuello_con_cabeza(out, P, ctrl, 2.8 if k == 0 else 2.0, 2.4 if k == 0 else 1.6, mira, tam,
                                       abre=36.0 if k == 0 else 30.0 + (abs(k) % 2) * 8, cuernos=0.8 if k == 0 else 0.4,
                                       semilla=semilla + j))
    return bocas


def monte(out, P, semilla=0):
    """C: el monte de roca volcanica del que sale, en escalones, con grietas de lava; y las serpientes enroscadas en el."""
    rng = np.random.RandomState(7)
    for i in range(22):                                                                                # bloques de roca ladeados
        t = i / 21
        a = rng.uniform(0, TAU)
        r = (1.0 - t) * 14.0 * rng.uniform(0.5, 1.0)
        y = t * 20.0
        w = 9.0 - t * 5.0 + rng.uniform(-1, 1)
        M = vr.T(math.sin(a) * r, y, math.cos(a) * r * 0.8) @ vr.Ry(rng.uniform(0, 3)) @ vr.Rz(rng.uniform(-0.25, 0.25)) @ vr.Rx(rng.uniform(-0.2, 0.2))
        caja(out, M, -w, w, -2.0, w * 0.7 + 2.0, -w * 0.8, w * 0.8, P['roca'], semilla=semilla + i % 5)
    caja(out, jm.I4, -7.0, 7.0, 14.0, 24.0, -6.0, 6.0, P['roca'], semilla=semilla + 9)


def serpiente_enroscada(out, P, s, semilla=0):
    """C: una serpiente que se enrosca al monte y alza la cabeza a un lado. Devuelve la boca."""
    ctrl = []
    for k in range(9):
        a = s * (k / 8) * 1.6 * math.pi + (0.0 if s > 0 else math.pi)
        r = 18.0 - k * 0.9
        ctrl.append(np.array((math.sin(a) * r, 3.0 + k * 2.2, math.cos(a) * r * 0.75)))
    ps, rs, _ = jm.a_lo_largo(ctrl, 18, ((0.0, 4.2), (0.6, 3.6), (1.0, 3.0)))
    jm.tubo(out, ps, rs, [P['escama']] * (len(ps) - 1), semilla=semilla)
    fin = ps[-1]
    mira = _u(np.array((-fin[0] * 0.03, 0.1, 1.0)))
    return cuello_con_cabeza(out, P, [fin, fin + np.array((0.0, 4.0, 3.0)), fin + np.array((s * 2.0, 7.0, 7.0))], 3.0, 2.6, mira, 0.9,
                             abre=36.0, cuernos=0.5, semilla=semilla + 2)


# ======================================================================
#  TIFON
# ======================================================================
POSE = {1: dict(abd=62, flex=34, codo=46, giro=-30, mun=-10, cierra=0.3),
        -1: dict(abd=38, flex=40, codo=62, giro=-40, mun=-15, cierra=0.3)}


def tifon(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    luces = []
    try:
        cuerpo = []
        torso(cuerpo, P)
        for s in (1, -1):
            brazo(cuerpo, P, s, POSE[s])
        if tipo == 'B':
            luces += corona_de_cabezas(cuerpo, P, semilla=200)
        else:
            Mh = vr.T(0.0, 44.6, 3.0) @ vr.Rx(12 * D) @ np.diag([CABEZA] * 3 + [1.0])
            bm.PPB = PPB / CABEZA
            luces.append(cabeza_dragon(cuerpo, Mh, P, abre=38.0, cuernos=1.0 if tipo == 'A' else 1.45, semilla=150))
            bm.PPB = PPB
            luces += melena(cuerpo, P, 6, 0.78, semilla=170)
        if tipo == 'C':                                                            # sale del monte
            monte(out, P, semilla=300)
            out += qm.transformar(cuerpo, vr.T(0.0, 2.0, 0.0))
            luces = [pt(vr.T(0.0, 2.0, 0.0), p) for p in luces]
            for s in (1, -1):
                luces.append(serpiente_enroscada(out, P, s, semilla=320 + (s > 0)))
        else:
            out += cuerpo
            for s in (1, -1):
                luces.append(pierna_serpiente(out, P, s, semilla=320 + (s > 0)))
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    return out, {'boca': luces[0], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

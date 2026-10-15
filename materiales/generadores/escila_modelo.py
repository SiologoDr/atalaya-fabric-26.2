"""
Escila y sus formas (14-10-2026). Juan: «sigue como lo estabas haciendo antes de hoy». El bestiario griego hecho
monstruo, como la Gorgona, el Minotauro y Cerbero: la cuarta del bestiario es Escila, el monstruo del estrecho.

Una jefa con el cuerpo de jefa_modelo (el de la Gorgona: mujer adulta de cajas, la cara C3 con mirada de jefa y las
garras B6), pero de la cintura para abajo es monstruo: la alza una masa de diez tentaculos enroscados en la punta, y
de la cintura le salen, en cuellos largos, los perros marinos del mito, con las fauces abiertas que arden por dentro
(el paladar encendido, los dientes dibujados en hojas, cuatro colmillos y el nucleo al fondo), las orejas de aleta y
las agallas encendidas. Lleva un corpino de escamas con el ribete de nacar, la melena mojada que le cae por la espalda
y una corona de coral con una perla que arde.

Las tres formas cambian lo que le sale de la cintura:

    A  Escila         seis perros marinos en abanico a su alrededor; aguamarina
    B  la de las Morenas  ocho morenas de cuello largo y fino, con las fauces estrechas llenas de agujas; coral
    C  la Madre de los Perros  tres perros enormes, mas grandes que ella; oro
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
ALZA = 15.0                                     # lo que la alzan los tentaculos (en unidades de la jefa)
GRANDE = 1.25                                   # la mujer, mas grande que el cuerpo de jefa, para que mande
NACAR = _r('6a6470', '9a94a2', 'c6c0cc', 'e4e0ea', 'faf8fc')
DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')

VARIANTES = {
    'A': dict(
        clave='A', nombre='Escila', corto='escila',
        piel=_r('6e7a7c', '94a2a2', 'b8c6c4', 'd2dedc', 'eef6f4'),
        pelo=_r('04100e', '0a1a18', '122824', '1c3a34', '2a5048'),
        tela=_r('062420', '0c3830', '145044', '1e6a5a', '2e8a74'),
        escama=_r('061c1a', '0c2c28', '143e38', '1e544c', '2c6e64'),
        mar=_r('040a0c', '081416', '0e1e20', '162a2e', '22383c'),
        vientre=_r('1a2a28', '2a3e3a', '3e5450', '566e68', '728a84'),
        aleta=_r('040a0c', '081416', '0c1a1e', '122428', '1a3034'),
        coral=_r('3a0a0e', '5e1418', '8a2226', 'b43a36', 'dc6a58'),
        oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('040808', '0a1212', '121c1c', '1c2828', '283838'),
        pelaje=_r('061c1a', '0c2c28', '143e38', '1e544c', '2c6e64'), medias=NACAR,
        neon=('eafff8', '3affd6', '045a48'), ojos=('3affd6', '0a6a54', 'b0ffee'), labios='4a5a5c', marca='145044',
        cabezas=6,
    ),
    'B': dict(
        clave='B', nombre='la de las Morenas', corto='morenas',
        piel=_r('7c6e6a', 'a2948e', 'c6b8b0', 'e0d4cc', 'f6eeea'),
        pelo=_r('100606', '1e0a0a', '2e1210', '421a16', '5c2620'),
        tela=_r('2a0c0a', '421410', '5e1e18', '7c2a20', '9e3a2c'),
        escama=_r('1c0a08', '2c120e', '3e1a14', '54241c', '6e3226'),
        mar=_r('0c0806', '160e0c', '201612', '2c1e18', '3c2a22'),
        vientre=_r('2e2418', '443626', '5e4c36', '7a6448', '98805e'),
        aleta=_r('0c0806', '160e0c', '1c120e', '261812', '322018'),
        coral=_r('3a0a0e', '5e1418', '8a2226', 'b43a36', 'dc6a58'),
        oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('0a0606', '140c0c', '1e1414', '2a1e1e', '3a2a2a'),
        pelaje=_r('1c0a08', '2c120e', '3e1a14', '54241c', '6e3226'), medias=NACAR,
        neon=('ffe8e0', 'ff5a46', '6a1008'), ojos=('ff5a46', '8a1a10', 'ffb0a0'), labios='6a3a34', marca='8a2a20',
        cabezas=8,
    ),
    'C': dict(
        clave='C', nombre='la Madre de los Perros', corto='madre',
        piel=_r('7a6a54', 'a08e74', 'c2b094', 'dccab0', 'f2e6d2'),
        pelo=_r('0c0804', '181008', '26180c', '362212', '4c3018'),
        tela=_r('2a1e08', '42300e', '5e4414', '7c5a1e', '9e742a'),
        escama=_r('16120a', '241c10', '342818', '483822', '604a2e'),
        mar=_r('0a0806', '14100c', '1e1812', '2a2218', '382e22'),
        vientre=_r('2c2618', '423a26', '5c5236', '786c48', '988a5e'),
        aleta=_r('0a0806', '14100c', '1a150e', '241c12', '302618'),
        coral=_r('3a2a08', '5e440e', '8a6614', 'b48a22', 'dcb43a'),
        oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('0a0806', '14100c', '1e1812', '2a2218', '382e22'),
        pelaje=_r('16120a', '241c10', '342818', '483822', '604a2e'), medias=NACAR,
        neon=('fff6dc', 'ffc23a', '6a4204'), ojos=('ffc23a', '8a5a08', 'ffe6a0'), labios='6a4a3a', marca='7c5a1e',
        cabezas=3,
    ),
}
for _v in VARIANTES.values():
    _v.setdefault('ribete', NACAR)
    _v.setdefault('guante', _v['tela'])


# ----------------------------------------------------------------------
#  Los pintores: los del cuerpo (jefa_modelo) y los del monstruo
# ----------------------------------------------------------------------
def pintores(V):
    P = jm.pintores(V, 'esc%s' % V['clave'])
    reg = P['_reg']
    nuc, neo, hon = V['neon']

    def mar(tw, th, cara, s):
        """La piel del monstruo: escamas pequenas en U, oscuras y limpias."""
        return _imagen(_bisel(sm._escamas_cara(tw, th, cara), 1, 1), V['mar']), None
    reg('mar', mar)
    reg('vientre_mar', lambda tw, th, c, s: (_imagen(sm._escudos(tw, th, 4), V['vientre']), None))

    def tentaculo(tw, th, cara, s):
        """El tentaculo: oscuro y liso, en anillos anchos con la junta un poco mas oscura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys % 7) == 0, 1, 2)
        return _imagen(_bisel(idx, 1, 1), V['mar']), None
    reg('tentaculo', tentaculo)

    def ventosa(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = xs % 6, ys % 6
        d = np.hypot(cx - 2.5, cy - 2.5)
        idx = np.where(d < 1.1, 1, np.where(d < 2.3, 3, 2))
        return _imagen(idx, V['vientre']), None
    reg('ventosa', ventosa)

    def aleta(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 2) % 2 == 0, 2, 1)
        idx = np.where((xs % 6) == 0, 4, idx)
        return _imagen(idx, V['aleta']), None
    reg('aleta', aleta)
    reg('coral', jm.liso(V['coral'], 3, 1, 1))
    reg('nacar', jm.liso(NACAR, 3, 1, 1))

    def ojo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = nm._hex(neo)
        t[..., 3] = 255
        if tw >= 3:
            t[:, tw // 2, :3] = nm._hex(nuc)
        return t, _emis(t, np.ones((th, tw), bool), 230)
    reg('ojo_perro', ojo)

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

    def _hojas_de_dientes(tw, th, colgando, paso=5):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTES]
        n = max(1, (tw + 1) // paso)
        x0 = (tw - (n * paso - 1)) // 2
        for i in range(n):
            x = x0 + i * paso
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.68)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)
                if f > 0.8 or paso < 5:
                    pix = ((x + 1, c[4]),) if f > 0.5 or paso >= 5 else ((x, c[3]), (x + 1, c[4]))
                elif f > 0.55:
                    pix = ((x + 1, c[4]), (x + 2, c[3]))
                else:
                    pix = ((x, c[2]), (x + 1, c[4]), (x + 2, c[3]), (x + 3, c[1]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
        return t, None
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, False))
    reg('agujas_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, True, 3))
    reg('agujas_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, False, 3))

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
#  Piezas del monstruo
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
    """Un colmillo en dos hojas cruzadas."""
    b = pt(M, base)
    d = _u(M[:3, :3] @ np.asarray(abajo, float))
    for lado in (M[:3, 0], M[:3, 2]):
        l = _u(lado - d * (lado @ d))
        p0, p1 = b - l * ancho / 2, b + l * ancho / 2
        q0, q1 = p0 + d * largo, p1 + d * largo
        lamina(out, (q0, q1, p1, p0), P['colmillo'], ancho, largo, semilla)
        lamina(out, (q1, q0, p0, p1), P['colmillo'], ancho, largo, semilla)


def aleta_rayos(out, P, base, dirs, largos, semilla=0):
    """Una aleta de radios: los radios finos de hueso oscuro y la membrana en bandas entre cada dos."""
    base = np.asarray(base, float)
    puntas = [base + _u(d) * L for d, L in zip(dirs, largos)]
    for p in puntas:
        jm.tubo(out, [base, p], [0.32, 0.14], [P['mar']], semilla=semilla)
    for a, b in zip(puntas, puntas[1:]):
        an, al = max(float(np.linalg.norm(b - a)), 0.3), max(float(np.linalg.norm(a - base)), 0.3)
        lamina(out, (base, base, b, a), P['aleta'], an, al, semilla=semilla + 1)
        lamina(out, (base, base, a, b), P['aleta'], an, al, semilla=semilla + 1)


def perro(out, Mh, P, abre=38.0, semilla=0):
    """La cabeza de perro marino, con el hocico hacia +z: el craneo con la coronilla en escalon y el ceno; los ojos
    encendidos; las orejas de aleta, de tres radios; las agallas encendidas detras de la mandibula; el hocico largo con
    su caballete y la trufa; y las fauces abiertas: el paladar encendido, los dientes en hojas, dos colmillos arriba y
    dos abajo, el suelo de la boca encendido y el nucleo al fondo. Devuelve el centro de la boca."""
    m = P['mar']
    caja(out, Mh, -3.3, 3.3, 0.0, 5.2, -3.4, 2.4, m, semilla=semilla)                                 # el craneo
    caja(out, Mh, -2.6, 2.6, 5.0, 5.9, -2.8, 1.2, m, semilla=semilla + 1)
    for s in (1, -1):
        x0, x1 = sorted((s * 1.6, s * 3.1))
        caja(out, Mh, x0, x1, 3.6, 4.3, 2.35, 2.6, P['ojo_perro'], semilla=semilla + 2)               # los ojos
        Mc = Mh @ vr.T(s * 2.3, 4.55, 2.55) @ vr.Rz(s * 18 * D)                                       # el ceno
        caja(out, Mc, -1.6, 1.6, -0.3, 0.55, -0.6, 0.65, m, semilla=semilla + 3)
        b = pt(Mh, (s * 3.1, 3.8, -1.6))                                                              # las orejas de aleta
        dirs = [Mh[:3, :3] @ np.array((s * a, b_, -1.0)) for a, b_ in ((0.5, 1.1), (0.9, 0.6), (1.1, 0.1))]
        aleta_rayos(out, P, b, dirs, [5.6, 5.0, 3.8], semilla=semilla + 4)
        for k in range(3):                                                                            # las agallas
            M = Mh @ vr.T(s * 3.32, 1.6 - k * 0.0, -0.6 - k * 0.9)
            caja(out, M, -0.06, 0.06, -1.3, 1.3, -0.18, 0.18, P['luz'], semilla=semilla + 5)
    bm.cubo(out, Mh, -2.4, 0.8, 2.3, 4.8, 2.6, 8.4, m, caras={'abajo': P['fauces']}, semilla=semilla + 6)  # el hocico
    caja(out, Mh, -1.4, 1.4, 3.3, 4.0, 2.3, 9.8, m, semilla=semilla + 7)
    caja(out, Mh, -1.3, 1.3, 2.3, 3.7, 10.6, 11.3, P['garra'], semilla=semilla + 8)                   # la trufa
    hilera(out, Mh, [(-2.15, 2.6), (-2.15, 10.5), (2.15, 10.5), (2.15, 2.6)], 0.85, -1.1, P['dientes_arriba'], semilla=semilla + 9)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.7, 0.85, 9.8), 2.8, 0.9, (0, -1, 0.05), P, semilla=semilla + 10)
    caja(out, Mh, -1.8, 1.8, -1.5, 0.85, 2.0, 2.3, P['nucleo'], semilla=semilla + 11)                 # el nucleo
    Mj = Mh @ vr.T(0, 0.8, 1.4) @ vr.Rx(abre * D)                                                     # la mandibula
    bm.cubo(out, Mj, -2.2, -1.6, 0.0, 4.4, 1.6, 9.0, m, caras={'arriba': P['boca'], 'abajo': P['vientre_mar']}, semilla=semilla + 12)
    hilera(out, Mj, [(-1.95, 1.2), (-1.95, 8.8), (1.95, 8.8), (1.95, 1.2)], 0.0, 1.0, P['dientes_abajo'], semilla=semilla + 13)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.55, 0.0, 8.0), 2.3, 0.8, (0, 1, 0.05), P, semilla=semilla + 14)
    return pt(Mh, (0.0, 0.4, 5.5))


def morena(out, Mh, P, abre=34.0, semilla=0):
    """La cabeza de morena, con el hocico hacia +z: larga y estrecha, con los ojos pequenos delante, las fauces
    estrechas llenas de agujas en hojas, el paladar encendido, dos colmillos en la punta y el nucleo al fondo; y la
    cresta de aleta que le corre por la nuca."""
    m = P['mar']
    caja(out, Mh, -2.2, 2.2, 0.0, 3.8, -3.2, 2.0, m, semilla=semilla)
    bm.cubo(out, Mh, -1.7, 0.6, 1.8, 3.4, 2.4, 9.6, m, caras={'abajo': P['fauces']}, semilla=semilla + 1)
    caja(out, Mh, -1.1, 1.1, 2.8, 3.5, 2.0, 10.4, m, semilla=semilla + 2)
    for s in (1, -1):
        x0, x1 = sorted((s * 1.3, s * 1.8))
        caja(out, Mh, x0, x1, 2.4, 3.1, 7.6, 8.6, P['ojo_perro'], semilla=semilla + 3)
    hilera(out, Mh, [(-1.5, 2.0), (-1.5, 11.2), (1.5, 11.2), (1.5, 2.0)], 0.6, -0.9, P['agujas_arriba'], semilla=semilla + 4)
    colmillo(out, Mh, (0.0, 0.6, 11.0), 2.2, 0.7, (0, -1, 0.1), P, semilla=semilla + 5)
    caja(out, Mh, -1.3, 1.3, -0.8, 0.6, 1.6, 1.9, P['nucleo'], semilla=semilla + 6)
    Mj = Mh @ vr.T(0, 0.6, 1.2) @ vr.Rx(abre * D)
    bm.cubo(out, Mj, -1.6, -1.3, 0.0, 3.2, 1.3, 10.2, m, caras={'arriba': P['boca'], 'abajo': P['vientre_mar']}, semilla=semilla + 7)
    hilera(out, Mj, [(-1.4, 0.8), (-1.4, 10.0), (1.4, 10.0), (1.4, 0.8)], 0.0, 0.9, P['agujas_abajo'], semilla=semilla + 8)
    colmillo(out, Mj, (0.0, 0.0, 9.6), 1.9, 0.6, (0, 1, 0.1), P, semilla=semilla + 9)
    dirs = [Mh[:3, :3] @ np.array((0.0, 1.0, -0.6 - 0.5 * k)) for k in range(4)]                      # la cresta
    aleta_rayos(out, P, pt(Mh, (0.0, 3.6, 0.5)), dirs, [3.0, 3.4, 3.2, 2.6], semilla=semilla + 10)
    return pt(Mh, (0.0, 0.3, 6.0))


def tentaculo(out, P, angulo, alcance, semilla=0):
    """Un tentaculo de la base: sale del borde de abajo del cuerpo, baja hacia fuera, se apoya y se enrosca en la
    punta, sin llegar recto al suelo; con las ventosas por debajo."""
    u = np.array((math.sin(angulo), 0.0, math.cos(angulo)))
    lado = np.array((u[2], 0.0, -u[0]))
    b = u * 7.0 + np.array((0.0, ALZA + 9.0, 0.0))
    ctrl = [b, u * 11.0 + np.array((0.0, ALZA + 4.0, 0.0)), u * (alcance * 0.65) + np.array((0.0, 4.5, 0.0)),
            u * alcance + np.array((0.0, 1.6, 0.0)) + lado * 1.5, u * (alcance + 2.5) + np.array((0.0, 4.0, 0.0)) + lado * 3.0,
            u * (alcance + 1.0) + np.array((0.0, 6.0, 0.0)) + lado * 4.5]
    pts, rs, ts = jm.a_lo_largo(ctrl, 16, ((0.0, 2.7), (0.4, 2.0), (0.75, 1.15), (1.0, 0.4)))
    jm.tubo(out, pts, rs, [P['tentaculo']] * (len(pts) - 1), semilla=semilla)
    for k in range(2, len(pts) - 2, 2):                                                               # las ventosas
        d = pts[k + 1] - pts[k]
        abajo = _u(np.cross(d, lado))
        if abajo[1] > 0:
            abajo = -abajo
        M = em.marco(pts[k] + abajo * rs[k] * 0.92, abajo, up=d)
        r = rs[k] * 0.45
        caja(out, M, -r, r, -r, r, -0.1, 0.25, P['ventosa'], semilla=semilla + 1)


# ======================================================================
#  ESCILA
# ======================================================================
POSE = dict(brazos={1: dict(abd=135, flex=18, codo=34, giro=-60, mun=-10, cierra=0.2),
                    -1: dict(abd=42, flex=34, codo=58, giro=-40, mun=-15, cierra=0.2)},
            cabeza=(8, -4))


def escila(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = jm.PPB
    out = []
    luces = []
    try:
        # ---- la mujer, alzada sobre el monstruo
        sup = []
        esc = P['escama']
        bm.PPB = jm.PPB * GRANDE
        jm.torso(sup, P, {'cadera': esc, 'cintura': esc, 'pecho': esc, 'busto': esc, 'ribete': P['nacar']})
        caja(sup, jm.I4, -3.7, 3.7, 31.0, 31.8, -2.2, 2.2, P['nacar'], semilla=50)                       # el cinturon de nacar
        for s in (1, -1):
            jm.brazo(sup, P, s, 'B6', POSE['brazos'][s], {'escama': esc, 'pelaje': P['mar'], 'una': P['garra']})
        tx, tz = POSE['cabeza']
        Mh = vr.T(0.0, jm.CUELLO_Y, 0.2) @ vr.Rx(tx * D) @ vr.Rz(tz * D)
        jm.cabeza(sup, Mh, P, V)
        caja(sup, Mh, -4.55, 4.55, -4.0, 7.0, -4.95, -3.6, P['pelo'], semilla=59)                       # la melena de detras
        for k, x in enumerate((-3.4, -1.7, 0.0, 1.7, 3.4)):                                             # que cae mojada
            b = pt(Mh, (x, 0.0, -4.4))
            ctrl = [b, b + np.array((x * 0.1, -6.0, -1.6)), b + np.array((x * 0.25, -13.0, -2.2)), b + np.array((x * 0.35, -19.0 + abs(x), -1.4))]
            ps, rs, _ = jm.a_lo_largo(ctrl, 6, ((0.0, 1.0), (1.0, 0.5)))
            jm.tubo(sup, ps, rs, [P['pelo']] * (len(ps) - 1), semilla=60 + k)
        for k, (x, h, a) in enumerate(((-3.0, 3.6, 18), (-1.5, 5.0, 8), (0.0, 6.0, 0), (1.5, 5.0, -8), (3.0, 3.6, -18))):   # la corona de coral
            b = pt(Mh, (x, 7.6, -0.4))
            d = Mh[:3, :3] @ np.array((math.sin(-a * D), 1.0, -0.15))
            ctrl = [b, b + _u(d) * h * 0.5, b + _u(d) * h + np.array((x * 0.15, 0.0, 0.0))]
            jm.tubo(sup, ctrl, [0.45, 0.35, 0.2], [P['coral']] * 2, semilla=70)
            r_ = _u(np.cross(d, (0.0, 0.0, 1.0)) + np.array((1e-3, 0, 0)))
            q = b + _u(d) * h * 0.55
            jm.tubo(sup, [q, q + r_ * (1.2 if x <= 0 else -1.2) + _u(d) * 1.2], [0.3, 0.15], [P['coral']], semilla=71)
        caja(sup, Mh, -0.65, 0.65, 7.3, 8.6, 3.6, 4.6, P['luz'], semilla=72)                             # la perla
        bm.PPB = jm.PPB
        Ms = vr.T(0.0, ALZA + 24.0, 0.0) @ np.diag([GRANDE] * 3 + [1.0]) @ vr.T(0.0, -24.0, 0.0)
        out += qm.transformar(sup, Ms)
        cara = pt(Ms @ Mh, (0.0, 4.0, 4.2))
        # ---- el cuerpo del monstruo: de las caderas a la base de los tentaculos, con un faldon de escamas
        Y = ALZA
        for i, (y0, y1, r) in enumerate(((Y + 21.0, Y + 25.0, 5.6), (Y + 16.0, Y + 21.0, 7.6), (Y + 11.5, Y + 16.0, 8.4),
                                         (Y + 8.0, Y + 11.5, 7.4))):
            for kx, kz in ((1.0, 0.7), (0.72, 1.0)):
                caja(out, jm.I4, -r * kx, r * kx, y0, y1, -r * kz, r * kz, P['mar'], semilla=80 + i)
        for k in range(12):                                                                             # el faldon de escamas
            a = TAU * k / 12
            M = vr.T(math.sin(a) * 5.4, Y + 24.6, math.cos(a) * 3.9) @ vr.Ry(a) @ vr.Rx(28 * D)
            caja(out, M, -1.9, 1.9, -5.0, 0.0, -0.3, 0.3, P['escama'], semilla=84)
        n_t = 10
        for k in range(n_t):
            tentaculo(out, P, TAU * (k + 0.5) / n_t, 26.0 + (k % 3) * 2.5, semilla=90 + k % 4)
        # ---- los perros (o las morenas) que le salen de la cintura
        n = V['cabezas']
        if tipo == 'A':
            angs = [-128, -78, -30, 30, 78, 128]
            esc_c, largo, alto, r0 = 1.15, 16.0, 9.0, 2.4
        elif tipo == 'B':
            angs = [-150, -112, -70, -26, 26, 70, 112, 150]
            esc_c, largo, alto, r0 = 1.0, 20.0, 14.0, 1.5
        else:
            angs = [-62, 0, 62]
            esc_c, largo, alto, r0 = 1.7, 17.0, 6.0, 3.6
        for j, a in enumerate(angs):
            aa = a * D
            u = np.array((math.sin(aa), 0.0, math.cos(aa)))
            b = np.array((u[0] * 5.0, Y + 18.0 + (j % 2) * 1.5, u[2] * 4.6))
            sube = alto * (1.0 - 0.25 * abs(a) / 150)
            ctrl = [b, b + u * largo * 0.35 + np.array((0.0, sube * 0.15, 0.0)), b + u * largo * 0.7 + np.array((0.0, sube * 0.7, 0.0)),
                    b + u * largo + np.array((0.0, sube, 2.5))]
            ps, rs, _ = jm.a_lo_largo(ctrl, 9, ((0.0, r0 * 1.15), (0.6, r0), (1.0, r0 * 1.05)))
            jm.tubo(out, ps, rs, [P['mar']] * (len(ps) - 1), semilla=100 + j)
            mira = _u(u * 0.95 + np.array((0.0, -0.08, 0.75)))                                            # miran afuera y adelante
            Mc = em.marco(ps[-1] + mira * r0 * 0.4, mira, up=(0.0, 1.0, 0.0)) @ vr.T(0, -2.0 * esc_c, -2.0 * esc_c) @ np.diag([esc_c] * 3 + [1.0])
            bm.PPB = jm.PPB / esc_c
            if tipo == 'B':
                boca = morena(out, Mc, P, semilla=110 + j)
            else:
                boca = perro(out, Mc, P, abre=32.0 if j % 2 == 0 else 26.0, semilla=110 + j)
            bm.PPB = jm.PPB
            luces.append((abs(a), boca))
        luces = [b for _, b in sorted(luces, key=lambda t: t[0])]
    finally:
        bm.PPB = ppb
    E = np.diag([jm.ESCALA] * 3 + [1.0])
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    cara = pt(E, cara)
    return out, {'boca': luces[0], 'luces': luces, 'cara': cara}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

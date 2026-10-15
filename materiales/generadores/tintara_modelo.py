"""
Tintara y sus formas (14-10-2026). Juan, al guardar a Murena: «sigue con otro boss diferente». Y antes: «crea tus
monstruos; si debes usar animales usalos; monstruos, leyendas, mitologias… pero que no sea igual, tenemos que poner
nuestro toque».

Tintara, la Reina del Abismo: un kraken, la leyenda del mar hecha con lo que tienen los cefalopodos de verdad. La cabeza
es el manto, grande, con dos ojos enormes de pupila rasgada que arden; debajo, en el centro de los brazos, el pico: dos
mandibulas negras en gancho, abiertas, con las fauces encendidas por dentro (el paladar en escalones, la radula de
dientes dibujados en hojas y el nucleo al fondo). Los brazos, gruesos en la base, se enroscan en la punta y llevan las
ventosas por debajo. Lo nuestro: los dibujos de luz de los cefalopodos (anillos que arden, la capa con espinas, las
mazas con ganchos), cada forma con el suyo.

Las tres formas cambian la silueta:

    A  la de los Anillos   un pulpo alzado sobre cinco brazos y con tres en alto, enroscados; la piel con anillos que
                           arden; azul
    B  la Vampira          los ocho brazos alzados en un paraguas, unidos por una capa de membrana con espinas por dentro,
                           que se abre alrededor del pico; dos aletas como orejas en el manto; carmesi
    C  la Gigante          un calamar: el manto alto y en punta, con dos aletas arriba; ocho brazos cortos enroscados en el
                           suelo y dos tentaculos larguisimos alzados por encima, con mazas de ventosas y ganchos; ambar
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
from sierpe_modelo import _bisel, _degradado, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.6
DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')
PICO = _r('060506', '0e0c0e', '181518', '24202a', '34303c')

VARIANTES = {
    'A': dict(
        clave='A', nombre='la de los Anillos', corto='anillos', dibujo_piel='anillos',
        piel=_r('0c0a06', '16120c', '221c12', '30281a', '403624'),
        ventosa=_r('3a3020', '5a4c34', '7c6c4e', '9e8e6e', 'c0b292'),
        membrana=_r('0c0a06', '16120c', '1e1810', '2a2216', '362c1e'),
        neon=('eef6ff', '3a9aff', '06244a'),
    ),
    'B': dict(
        clave='B', nombre='la Vampira', corto='vampira', dibujo_piel='puntos',
        piel=_r('120406', '1e080c', '2c0e12', '3c161a', '502024'),
        ventosa=_r('3a1a1c', '5a2a2c', '7c4044', '9e5c60', 'c08084'),
        membrana=_r('0e0406', '1a080a', '260c10', '341216', '441a1e'),
        neon=('ffe2e6', 'ff2a46', '6a0410'),
    ),
    'C': dict(
        clave='C', nombre='la Gigante', corto='gigante', dibujo_piel='cromas',
        piel=_r('140a06', '22120a', '321a10', '442418', '5a3222'),
        ventosa=_r('4a3a28', '6e5a40', '927a5c', 'b49c7c', 'd4bea0'),
        membrana=_r('140a06', '22120a', '2c180e', '3a2014', '4a2a1a'),
        neon=('fff2d6', 'ffb02a', '6a3a04'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'tin%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']
    c_m = np.array(nm._hex(neo))

    def piel(tw, th, cara, s):
        """La piel: lisa y oscura, con el dibujo de cada forma: anillos que arden (A), puntos claros (B) o las manchas
        de los cromatoforos en dos tonos (C)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        base = _imagen(_bisel(np.full((th, tw), 2), 1, 1), V['piel'])
        if V['dibujo_piel'] == 'anillos':
            cx, cy = xs // 9, ys // 9
            jx = (cx * 5 + cy * 3 + s) % 3 + 3
            jy = (cx * 3 + cy * 7 + s * 2) % 3 + 3
            d = np.hypot(xs % 9 - jx, ys % 9 - jy)
            aro = (d > 1.6) & (d < 2.8)
            base[..., :3] = np.where(aro[..., None], c_m, base[..., :3])
            return base, _emis(base, aro, 220)
        if V['dibujo_piel'] == 'puntos':
            cx, cy = xs // 6, ys // 6
            jx = (cx * 5 + cy * 3 + s) % 3 + 1
            jy = (cx * 3 + cy * 7 + s * 2) % 3 + 1
            d = np.hypot(xs % 6 - jx, ys % 6 - jy)
            m = d < 0.9
            base[..., :3] = np.where(m[..., None], np.array(nm._hex('8a3a40')), base[..., :3])
            return base, None
        idx = sm._manchas(tw, th, s, celda=6.0, umbral=0.6, alto=0.82)
        t = _imagen(_bisel(np.where(idx >= 3, 3, 2), 1, 1), V['piel'])
        return t, None
    reg('piel', piel)

    def ventosa(tw, th, cara, s):
        """La ventosa: un aro claro con el hueco oscuro."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        idx = np.where(r < 0.45, 0, np.where(r < 0.8, 3, 2))
        return _imagen(idx, V['ventosa']), None
    reg('ventosa', ventosa)

    def membrana(tw, th, cara, s):
        """La capa de la Vampira: oscura, en bandas a lo largo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 3) % 2 == 0, 2, 1)
        idx = np.where((ys % 10) == 0, 3, idx)
        return _imagen(idx, V['membrana']), None
    reg('membrana', membrana)
    reg('pico', jm.liso(PICO, 3, 1, 1))
    reg('gancho', jm.liso(DIENTES, 3, 1, 1))

    def ojo(tw, th, cara, s):
        """El ojo: el iris del neon en anillos, con la pupila rasgada en horizontal, como la de un pulpo."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_h = np.array(nm._hex(nuc)), np.array(nm._hex(hon))
        col = np.where((r < 0.4)[..., None], qm._mezcla(c_m, c_n, 0.5), np.where((r < 0.85)[..., None], c_m, c_h))
        pupila = (np.abs(ys - cy) < max(0.7, th * 0.1)) & (np.abs(xs - cx) < tw * 0.32)
        col = np.where(pupila[..., None], np.array((8, 6, 6)), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, ~pupila & (r < 0.85), 230)
    reg('ojo', ojo)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def nucleo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_h = nm._hex(nuc), nm._hex(hon)
        col = np.where((r < 0.45)[..., None], np.array(c_n),
                       np.where((r < 0.8)[..., None], np.array(qm._mezcla(nm._hex(neo), c_n, 0.4)), np.array(nm._hex(neo))))
        col = np.where((r > 1.0)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 1.0, 240)
    reg('nucleo', nucleo)

    def _hojas_de_dientes(tw, th, colgando):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTES]
        n = max(1, (tw + 1) // 4)
        x0 = (tw - (n * 4 - 1)) // 2
        for i in range(n):
            x = x0 + i * 4
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.7)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)
                pix = ((x + 1, c[4]),) if f > 0.6 else ((x, c[3]), (x + 1, c[4]), (x + 2, c[2]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
        return t, None
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, False))
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


def bulto(out, M, rx, ry, rz, pintor, semilla=0):
    """Un bulto redondeado de cajas cruzadas (un elipsoide a lo Minecraft)."""
    for kx, ky, kz in ((1.0, 0.72, 0.8), (0.82, 0.9, 0.82), (0.72, 1.0, 0.72), (0.8, 0.72, 1.0)):
        caja(out, M, -rx * kx, rx * kx, -ry * ky, ry * ky, -rz * kz, rz * kz, pintor, semilla=semilla)


def brazo(out, P, ctrl, r0, ventosas=True, semilla=0, n=18, r1=None):
    """Un brazo: grueso en la base, que se afina y se enrosca en la punta; con las ventosas por el lado de dentro (el
    de abajo de la curva). Devuelve los puntos."""
    ps, rs, _ = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], n, ((0.0, r0), (0.45, r0 * 0.72), (0.85, r0 * 0.32),
                                                                        (1.0, r1 if r1 is not None else r0 * 0.14)))
    jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=semilla)
    if ventosas:
        for k in range(1, len(ps) - 2, 2):
            d = ps[k + 1] - ps[k - 1]
            curva = (ps[k + 1] - ps[k]) - (ps[k] - ps[k - 1])
            dentro = curva - _u(d) * (curva @ _u(d))
            if np.linalg.norm(dentro) < 1e-4:
                dentro = np.array((0.0, -1.0, 0.0))
            dentro = _u(dentro)
            M = em.marco(ps[k] + dentro * rs[k] * 0.9, dentro, up=d)
            r = rs[k] * 0.62
            caja(out, M, -r, r, -r, r, -0.1, 0.22, P['ventosa'], semilla=semilla + 1)
    return ps, rs


def espiral(p0, d, arriba, largo, vueltas=1.2, n=7):
    """Los puntos de un brazo que sale de p0 hacia d y acaba enroscado en espiral hacia 'arriba'."""
    p0, d, arriba = np.asarray(p0, float), _u(d), _u(arriba)
    lado = _u(np.cross(d, arriba))
    pts = [p0]
    for j in range(1, n + 1):
        t = j / n
        if t < 0.6:
            pts.append(p0 + d * largo * t + arriba * largo * 0.1 * math.sin(t * math.pi))
        else:
            u = (t - 0.6) / 0.4
            a = u * vueltas * TAU
            r = largo * 0.16 * (1.0 - 0.6 * u)
            c = p0 + d * largo * 0.6
            pts.append(c + d * math.sin(a) * r * 1.4 + arriba * (1.0 - math.cos(a)) * r + lado * u * 0.6)
    return pts


def pico(out, P, M, abre=36.0, semilla=0):
    """El pico, de cara a +z: la mandibula de arriba, negra y en gancho hacia abajo; la de abajo, que se abre; dentro,
    el paladar encendido, la radula de dientes en hojas y el nucleo al fondo. Devuelve la boca."""
    k = P['pico']
    bm.cubo(out, M, -2.4, 0.0, -2.0, 4.8, 2.8, 4.4, k, caras={'abajo': P['fauces']}, semilla=semilla)
    bm.cubo(out, M, -1.8, -0.2, 2.4, 3.6, 2.4, 1.8, k, caras={'abajo': P['fauces']}, semilla=semilla + 1)
    Mg = M @ vr.T(0.0, 0.2, 4.2) @ vr.Rx(48 * D)                                                       # el gancho
    caja(out, Mg, -1.3, 1.3, -0.2, 1.8, 0.0, 2.2, k, semilla=semilla + 2)
    caja(out, Mg @ vr.T(0.0, 0.0, 2.0) @ vr.Rx(30 * D), -0.8, 0.8, -0.1, 1.2, 0.0, 1.6, k, semilla=semilla + 2)
    hilera(out, M, [(-2.1, -1.6), (-2.1, 3.8), (2.1, 3.8), (2.1, -1.6)], 0.0, -1.0, P['dientes_arriba'], semilla=semilla + 3)
    Mj = M @ vr.T(0.0, 0.0, -1.8) @ vr.Rx(abre * D)                                                    # la de abajo
    bm.cubo(out, Mj, -2.2, -2.0, 0.0, 4.4, 2.0, 5.0, k, caras={'arriba': P['fauces']}, semilla=semilla + 4)
    caja(out, Mj @ vr.T(0.0, -1.0, 5.0) @ vr.Rx(-35 * D), -1.4, 1.4, -0.8, 0.8, 0.0, 1.8, k, semilla=semilla + 5)
    hilera(out, Mj, [(-1.9, 0.4), (-1.9, 4.6), (1.9, 4.6), (1.9, 0.4)], 0.0, 0.9, P['dientes_abajo'], semilla=semilla + 6)
    caja(out, M, -1.6, 1.6, -2.2, 0.2, -1.9, -1.6, P['nucleo'], semilla=semilla + 7)
    return pt(M, (0.0, -0.8, 1.6))


def ojo(out, P, centro, mira, r, semilla=0):
    """Un ojo enorme, abombado, que mira hacia 'mira', con el parpado de piel por arriba y por abajo."""
    M = em.marco(np.asarray(centro, float), _u(mira), up=(0.0, 1.0, 0.0))
    bulto(out, M, r * 1.25, r * 1.25, r * 0.7, P['piel'], semilla=semilla)
    caja(out, M, -r, r, -r * 0.9, r * 0.9, 0.0, r * 0.95, P['ojo'], semilla=semilla + 1)
    caja(out, M, -r * 1.15, r * 1.15, r * 0.7, r * 1.2, -r * 0.4, r * 0.95, P['piel'], semilla=semilla + 2)    # el parpado
    return pt(M, (0.0, 0.0, r * 1.2))


# ======================================================================
#  TINTARA
# ======================================================================
def tintara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    luces = []
    rng = random.Random(5)
    try:
        if tipo == 'A':
            O = np.array((0.0, 13.0, 2.0))                                     # el centro de los brazos
            bulto(out, vr.T(0.0, 27.0, -5.0) @ vr.Rx(-20 * D), 8.5, 11.0, 8.5, P['piel'], semilla=1)        # el manto
            bulto(out, vr.T(0.0, 18.0, -1.0), 8.0, 6.5, 7.5, P['piel'], semilla=2)                          # la cabeza
            for s in (1, -1):
                luces.append(ojo(out, P, (s * 6.6, 19.0, 2.6), (s * 0.85, 0.05, 0.6), 2.6, semilla=3))
            Mp = em.marco(O + np.array((0.0, 0.5, 5.6)), (0.0, -0.35, 1.0), up=(0.0, 1.0, 0.0))
            luces.insert(0, pico(out, P, Mp, semilla=10))
            for k in range(8):                                                 # los brazos
                a = (k + 0.5) * TAU / 8
                u = np.array((math.sin(a), 0.0, math.cos(a)))
                b = O + u * 4.5 + np.array((0.0, -1.0, 0.0))
                if k in (0, 7, 3):                                             # tres alzados
                    arriba = np.array((0.0, 1.0, 0.0))
                    d = _u(u * 0.6 + np.array((0.0, 1.0, 0.0)))
                    ctrl = espiral(b, d, -u + np.array((0.0, 0.3, 0.0)), 26.0, vueltas=1.1)
                else:                                                          # los que la sostienen
                    ctrl = [b, b + u * 6.0 + np.array((0.0, -6.0, 0.0)), b + u * 13.0 + np.array((0.0, -11.0, 0.0))]
                    ctrl += espiral(ctrl[-1], u, np.array((0.0, 1.0, 0.0)), 12.0, vueltas=1.0, n=5)[1:]
                brazo(out, P, ctrl, 3.0, semilla=20 + k % 3)
        elif tipo == 'B':
            O = np.array((0.0, 16.0, 3.0))
            bulto(out, vr.T(0.0, 24.0, -9.0) @ vr.Rx(-55 * D), 7.0, 10.0, 7.0, P['piel'], semilla=1)        # el manto, atras
            for s in (1, -1):                                                  # las aletas como orejas
                b = np.array((s * 6.0, 30.0, -12.0))
                lamina(out, (b, b + np.array((s * 7.0, 4.0, -2.0)), b + np.array((s * 6.0, 8.5, -4.0)), b + np.array((0.0, 6.0, -3.0))),
                       P['membrana'], 7.0, 8.0, semilla=4)
                lamina(out, (b + np.array((0.0, 6.0, -3.0)), b + np.array((s * 6.0, 8.5, -4.0)), b + np.array((s * 7.0, 4.0, -2.0)), b),
                       P['membrana'], 7.0, 8.0, semilla=4)
            bulto(out, vr.T(0.0, 18.0, -2.0), 7.0, 6.0, 6.5, P['piel'], semilla=2)
            for s in (1, -1):
                luces.append(ojo(out, P, (s * 6.4, 21.0, 0.5), (s * 0.8, 0.1, 0.6), 3.2, semilla=3))
            Mp = em.marco(O + np.array((0.0, -1.5, 4.0)), (0.0, -0.1, 1.0), up=(0.0, 1.0, 0.0))
            luces.insert(0, pico(out, P, Mp, semilla=10))
            puntas = []
            for k in range(8):                                                 # el paraguas
                a = (k / 8) * TAU + 0.2
                rad = np.array((math.sin(a), math.cos(a), 0.0))               # en el plano de la cara
                b = O + rad * 4.0 + np.array((0.0, 0.0, 2.0))
                d = _u(rad * 1.0 + np.array((0.0, 0.0, 0.75)))
                fuera = _u(rad + np.array((0.0, 0.0, -0.4)))
                ctrl = espiral(b, d, fuera, 24.0, vueltas=0.9)
                ps, rs = brazo(out, P, ctrl, 2.7, semilla=20 + k % 3)
                puntas.append((ps, rs))
                for j in range(2, 10, 2):                                      # las espinas de dentro
                    q = ps[j]
                    dentro = _u(O - q + np.array((0.0, 0.0, 6.0)))
                    jm.tubo(out, [q, q + dentro * 1.8], [rs[j] * 0.3, 0.1], [P['piel']], semilla=25)
            for k in range(8):                                                 # la capa entre brazo y brazo
                (pa, ra), (pb, rb) = puntas[k], puntas[(k + 1) % 8]
                for j in range(0, 10):
                    a0, a1 = pa[j], pa[j + 1]
                    b0, b1 = pb[j], pb[j + 1]
                    W = max(float(np.linalg.norm(b0 - a0)), 0.5)
                    L = max(float(np.linalg.norm(a1 - a0)), 0.5)
                    lamina(out, (a0, b0, b1, a1), P['membrana'], W, L, semilla=30)
                    lamina(out, (a1, b1, b0, a0), P['membrana'], W, L, semilla=30)
            for k in range(3):                                                 # tres brazos de apoyo, por detras
                a = math.pi + (k - 1) * 0.7
                u = np.array((math.sin(a), 0.0, math.cos(a)))
                b = O + u * 3.0 + np.array((0.0, -3.0, -2.0))
                ctrl = [b, b + u * 5.0 + np.array((0.0, -7.0, 0.0)), b + u * 10.0 + np.array((0.0, -13.0, 0.0))]
                ctrl += espiral(ctrl[-1], u, np.array((0.0, 1.0, 0.0)), 8.0, n=4)[1:]
                brazo(out, P, ctrl, 2.4, semilla=40)
        else:
            O = np.array((0.0, 10.0, 2.0))
            pts = [np.array((0.0, 12.0, -1.0)), np.array((0.0, 26.0, -3.0)), np.array((0.0, 40.0, -4.0)), np.array((0.0, 50.0, -4.5))]
            ps, rs, _ = jm.a_lo_largo(pts, 10, ((0.0, 7.0), (0.3, 7.2), (0.75, 5.0), (1.0, 1.2)))
            jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=1)                                      # el manto en punta
            for s in (1, -1):                                                  # las aletas de arriba
                b0, b1 = np.array((s * 2.0, 38.0, -4.0)), np.array((s * 1.0, 50.0, -4.5))
                c = np.array((s * 10.0, 44.0, -4.0))
                lamina(out, (b0, c, c, b1), P['membrana'], 10.0, 12.0, semilla=4)
                lamina(out, (b1, c, c, b0), P['membrana'], 10.0, 12.0, semilla=4)
            bulto(out, vr.T(0.0, 13.0, 0.0), 6.5, 5.5, 6.0, P['piel'], semilla=2)
            for s in (1, -1):
                luces.append(ojo(out, P, (s * 5.8, 14.0, 1.5), (s * 0.9, 0.05, 0.5), 3.4, semilla=3))
            Mp = em.marco(O + np.array((0.0, -1.0, 5.0)), (0.0, -0.3, 1.0), up=(0.0, 1.0, 0.0))
            luces.insert(0, pico(out, P, Mp, semilla=10))
            for k in range(8):                                                 # los brazos cortos
                a = (k + 0.5) * TAU / 8
                u = np.array((math.sin(a), 0.0, math.cos(a)))
                b = O + u * 3.8 + np.array((0.0, -1.5, 0.0))
                ctrl = [b, b + u * 4.0 + np.array((0.0, -5.0, 0.0)), b + u * 8.0 + np.array((0.0, -7.6, 0.0))]
                ctrl += espiral(ctrl[-1], u, np.array((0.0, 1.0, 0.0)), 8.0, n=4)[1:]
                brazo(out, P, ctrl, 2.4, semilla=20 + k % 3)
            for s in (1, -1):                                                  # los dos tentaculos largos
                b = O + np.array((s * 2.5, 0.5, 3.0))
                ctrl = [b, b + np.array((s * 5.0, 8.0, 5.0)), b + np.array((s * 11.0, 20.0, 4.0)), b + np.array((s * 14.0, 33.0, 1.0)),
                        b + np.array((s * 12.0, 42.0, 2.0)), b + np.array((s * 8.0, 46.0, 5.0))]
                ps, rs = brazo(out, P, ctrl, 1.6, ventosas=False, semilla=40, n=16, r1=1.2)
                M = em.marco(ps[-1], ps[-1] - ps[-3], up=(s * 1.0, 0.0, 0.0))  # la maza
                for j, (w, L) in enumerate(((1.8, 2.5), (2.2, 3.0), (1.6, 2.4), (0.9, 1.6))):
                    caja(out, M, -w, w, -0.9, 0.9, 0.0, L, P['piel'], semilla=41)
                    for x in (-w * 0.5, w * 0.5):
                        caja(out, M, x - 0.45, x + 0.45, 0.85, 1.15, 0.4, L - 0.4, P['ventosa'], semilla=42)
                    if j in (1, 2):
                        jm.tubo(out, [pt(M, (0.0, 1.0, L * 0.5)), pt(M, (0.0, 2.6, L * 0.3))], [0.35, 0.1], [P['gancho']], semilla=43)
                    M = M @ vr.T(0.0, 0.0, L) @ vr.Rx(-12 * D)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -min(y0, 0.0), 0.0)
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    return out, {'boca': luces[0], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

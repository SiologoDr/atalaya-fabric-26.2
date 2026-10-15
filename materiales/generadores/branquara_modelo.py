"""
Branquara y sus formas (14-10-2026). Juan: «sigue como lo estabas haciendo antes de hoy»: la receta de Lumara,
Espinara, Simara y Riscara (la cabeza manda, grande y con las fauces abiertas que arden; algo la enmarca; el cuerpo
oscuro se alza; texturas limpias; tres formas que cambian la silueta).

Branquara, la Salamandra del Cenote: una salamandra colosal, inventada (salamandra, dragon y algo nuevo), que se alza
sobre las patas de atras con las garras de delante en alto y la cola con aleta enroscada en el suelo. Manda la cabeza:
ancha y plana, en U, con las fauces enormes abiertas, el paladar encendido en escalones, los dientes dibujados en
hojas, cuatro colmillos y el nucleo al fondo de la garganta. Lo nuevo, lo que la enmarca: las branquias de fuera,
tres a cada lado de la nuca, que cambian en cada forma. La piel es oscura, con manchas grandes y limpias; el vientre,
en escudos.

    A  la Plumada    las branquias en penacho, con plumillas que arden en la punta; aleta en el lomo y la cola; ambar
    B  la Cornuda    las branquias hechas cuernos de hueso que se ramifican; puas de hueso por el lomo; coral
    C  la Barbada    las branquias largas que cuelgan como barbas, con bulbos de luz; una vela alta en el lomo;
                     turquesa
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
from sierpe_modelo import _bisel, _degradado, _escudos, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

D = vr.D2R
_r = bm._r
PPB = 5
ESCALA = 0.6
CABEZA = 1.35

DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')
VARIANTES = {
    'A': dict(
        clave='A', nombre='la Plumada', corto='plumada', patron='manchas',
        piel=_r('0e0c08', '18150e', '242016', '322c1e', '443c2a'),
        mancha=_r('2a1e0a', '3e2c0e', '584014', '74561e', '8e6c2a'),
        vientre=_r('1e1a12', '2e281c', '403828', '544a36', '6a5e46'),
        hueso=_r('4a4234', '6e6450', '948870', 'b8ac92', 'd8ceb6'),
        aleta=_r('0e0c08', '18150e', '221e14', '2e281c', '3c3424'),
        neon=('fff2d6', 'ffb02a', '6a3a04'),
    ),
    'B': dict(
        clave='B', nombre='la Cornuda', corto='cornuda', patron='manchas',
        piel=_r('100a0a', '1a1010', '261818', '342222', '462e2c'),
        mancha=_r('22100c', '2e140e', '3c1a12', '4c2016', '5e2a1e'),
        vientre=_r('201614', '30221e', '42302a', '563e36', '6c5046'),
        hueso=_r('3a302a', '584a42', '766660', '948480', 'b2a49c'),
        aleta=_r('100a0a', '1a1010', '241616', '301e1e', '3e2828'),
        neon=('ffe6dc', 'ff5a3c', '6a1404'),
    ),
    'C': dict(
        clave='C', nombre='la Barbada', corto='barbada', patron='lunares',
        piel=_r('080c0e', '0e1418', '162024', '202c32', '2c3c44'),
        mancha=_r('2e3c42', '405258', '546a72', '6a848c', '86a2aa'),
        vientre=_r('161c1e', '222a2e', '323e42', '445256', '58686c'),
        hueso=_r('3e4848', '5c6a6a', '7e8e8c', 'a2b2ae', 'c6d4d0'),
        aleta=_r('080c0e', '0e1418', '141c20', '1c262c', '263238'),
        neon=('e6fffa', '2affd2', '04524a'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'bra%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def piel(tw, th, cara, s):
        """La piel: lisa y oscura, con manchas grandes de borde limpio (o lunares redondos) en el color de la mancha."""
        if V['patron'] == 'lunares':
            ys, xs = np.mgrid[0:th, 0:tw]
            cx, cy = xs // 12, ys // 12
            jx = (cx * 7 + cy * 13 + s) % 6 + 3
            jy = (cx * 11 + cy * 5 + s * 3) % 6 + 3
            d = np.hypot(xs % 12 - jx, ys % 12 - jy)
            idx = np.where(d < 0.8, 4, np.where(d < 1.7, 3, 2))
            base = _imagen(_bisel(np.full((th, tw), 2), 1, 1), V['piel'])
            man = _imagen(np.where(idx >= 4, 3, 2), V['mancha'])
            return np.where((idx >= 3)[..., None], man, base).astype(np.uint8), None
        idx = sm._manchas(tw, th, s, celda=13.0, umbral=0.66, alto=0.84)
        base = _imagen(_bisel(np.clip(idx, 1, 2), 1, 1), V['piel'])
        man = _imagen(np.where(idx >= 4, 3, 2), V['mancha'])
        t = np.where((idx >= 3)[..., None], man, base)
        return t.astype(np.uint8), None
    reg('piel', piel)
    reg('vientre', lambda tw, th, c, s: (_imagen(_escudos(tw, th, 5), V['vientre']), None))
    reg('hueso', jm.liso(V['hueso'], 3, 1, 1))
    reg('lengua', jm.liso(_r('14060a', '1e0a10', '2a0e16', '38141e', '481a28'), 2, 1, 1))
    reg('garra', jm.liso(_r('0a0908', '141210', '1e1b18', '2a2622', '38332e'), 2, 1, 1))

    def aleta(tw, th, cara, s):
        """La aleta: oscura, en bandas a lo largo, con los radios claros."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 3) % 2 == 0, 2, 1)
        idx = np.where((xs % 9) == 0, 4, idx)
        return _imagen(idx, V['aleta']), None
    reg('aleta', aleta)

    def pluma(tw, th, cara, s):
        """Las plumillas de las branquias: oscuras en la base y del neon hacia la punta (que arde)."""
        t = np.zeros((th, tw, 4), np.uint8)
        largo_x = tw >= th
        n = tw if largo_x else th
        u = (np.arange(n) + 0.5) / n
        c_n, c_m, c_h = (np.array(nm._hex(c)) for c in (nuc, neo, hon))
        col = np.where((u < 0.45)[:, None], c_h * 0.45, np.where((u < 0.75)[:, None], c_h, np.where((u < 0.92)[:, None], c_m, c_n)))
        if largo_x:
            t[..., :3] = col[None, :, :]
        else:
            t[..., :3] = col[::-1][:, None, :]
        t[..., 3] = 255
        m = (u >= 0.75)
        mask = np.broadcast_to(m[None, :], (th, tw)) if largo_x else np.broadcast_to(m[::-1][:, None], (th, tw))
        return t, _emis(t, mask, 230)
    reg('pluma', pluma)

    def ojo(tw, th, cara, s):
        """El ojo: el iris del neon, con la pupila rasgada en vertical y el canto oscuro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        r = np.hypot((xs - cx) / max(tw / 2, 1), (ys - cy) / max(th / 2, 1))
        col = np.where((r < 0.55)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m))
        pupila = np.abs(xs - cx) < max(0.6, tw * 0.09)
        col = np.where(pupila[..., None], np.array((12, 8, 6)), col)
        col = np.where((r > 0.92)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, ~pupila & (r <= 0.92), 225)
    reg('ojo', ojo)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def boca(tw, th, cara, s):
        """El suelo de la boca: en escalones de luz del borde (sombra) al centro (blanco)."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        u = (xs + 0.5) / tw
        dd = np.minimum(u, 1 - u) * 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((dd < 0.18)[..., None], np.array(c_h),
                       np.where((dd < 0.45)[..., None], np.array(qm._mezcla(c_h, c_m, 0.6)),
                                np.where((dd < 0.75)[..., None], np.array(c_m), np.array(qm._mezcla(c_m, c_n, 0.6)))))
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, dd >= 0.18, 230)
    reg('boca', boca)

    def nucleo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((r < 0.4)[..., None], np.array(c_n),
                       np.where((r < 0.75)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m)))
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
            y = 0 if colgando else th - 1
            for xx in range(max(x, 0), min(x + 4, tw)):
                t[y, xx] = c[1]
        return t, None
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, False))

    def colmillo(tw, th, cara, s):
        """Un colmillo dibujado en una hoja: ancho arriba y en punta abajo, con la luz a la izquierda."""
        t = np.zeros((th, tw, 4), np.uint8)
        c = [np.array((*cc, 255)) for cc in DIENTES]
        for y in range(th):
            f = y / max(th - 1, 1)
            w = (1.0 - f) ** 0.8 * tw / 2
            cx = (tw - 1) / 2 + f * tw * 0.12
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
    """Una hilera de dientes dibujados en hojas, por los lados de un poligono (en el plano y del marco M)."""
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
    """Un colmillo en dos hojas cruzadas (se lee de frente y de lado), de base en el marco M hacia 'abajo'."""
    b = pt(M, base)
    d = M[:3, :3] @ np.asarray(abajo, float)
    d = _u(d)
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


def cabeza(out, Mh, P, abre=38.0):
    """La cabeza de salamandra, de cara a +z: ancha, plana y en U, con los ojos arriba y a los lados; las fauces
    enormes abiertas, el paladar encendido, los dientes en hojas, cuatro colmillos y el nucleo al fondo.
    Devuelve el centro de la boca y la nuca (donde nacen las branquias)."""
    pi_ = P['piel']
    F = {'abajo': P['fauces']}
    for j, (z0, z1, w, y1) in enumerate(((-5.5, -1.0, 13.6, 3.8), (-1.0, 2.6, 12.4, 3.5), (2.6, 5.2, 10.6, 3.1),
                                         (5.2, 6.9, 8.4, 2.7), (6.9, 7.9, 6.0, 2.3), (7.9, 8.4, 3.6, 1.8))):
        bm.cubo(out, Mh, -w / 2, 0.0, z0, w, y1, z1 - z0, pi_, caras=F, semilla=1 + j % 2)          # el craneo, en U
    bm.cubo(out, Mh, -7.2, 0.6, -4.8, 14.4, 2.4, 4.6, pi_, caras=F, semilla=3)                       # las mejillas
    bm.cubo(out, Mh, -5.0, 3.6, -5.0, 10.0, 0.7, 5.6, pi_, semilla=5)                                # la frente
    bm.cubo(out, Mh, -0.8, 3.0, 1.0, 1.6, 0.6, 6.0, pi_, semilla=5)                                  # la quilla del hocico
    for s in (1, -1):
        x0 = 3.0 if s > 0 else -5.2
        bm.cubo(out, Mh, x0, 2.8, 1.6, 2.2, 1.8, 2.4, P['ojo'], semilla=6)                            # los ojos
        bm.cubo(out, Mh, x0 - 0.3, 4.4, 1.0, 2.8, 0.8, 3.4, pi_, semilla=7)                           # la ceja
        bm.cubo(out, Mh, s * 2.2 - 0.35, 2.9, 7.2, 0.7, 0.5, 0.4, P['garra'], semilla=8)              # la nariz
    hilera(out, Mh, [(-6.4, -4.0), (-5.9, 2.4), (-4.9, 5.0), (-3.8, 6.7), (-2.6, 7.7), (2.6, 7.7), (3.8, 6.7), (4.9, 5.0),
                     (5.9, 2.4), (6.4, -4.0)],
           0.0, -1.5, P['dientes_arriba'], semilla=9)
    for x in (-2.4, 2.4):
        colmillo(out, Mh, (x, 0.0, 7.2), 3.4, 1.3, (0, -1, 0.1), P, semilla=10)
    # la mandibula de abajo, muy abierta
    Mj = Mh @ vr.T(0, 0.2, -5.0) @ vr.Rx(abre * D)
    J = {'arriba': P['boca'], 'abajo': P['vientre']}
    for j, (z0, z1, w, h) in enumerate(((0.0, 4.5, 13.0, 2.4), (4.5, 8.0, 11.8, 2.2), (8.0, 10.4, 9.8, 2.0),
                                        (10.4, 12.0, 7.4, 1.8), (12.0, 12.9, 4.6, 1.6))):
        bm.cubo(out, Mj, -w / 2, -h, z0, w, h, z1 - z0, pi_, caras=J, semilla=11 + j % 2)
    bm.cubo(out, Mj, -1.7, 0.0, 0.5, 3.4, 0.55, 6.5, P['lengua'], semilla=16)                          # la lengua
    bm.cubo(out, Mj, -1.2, 0.0, 7.0, 2.4, 0.45, 1.6, P['lengua'], semilla=16)
    hilera(out, Mj, [(-6.1, 1.0), (-5.5, 7.6), (-4.5, 10.0), (-3.3, 11.7), (-2.0, 12.6), (2.0, 12.6), (3.3, 11.7), (4.5, 10.0),
                     (5.5, 7.6), (6.1, 1.0)],
           0.0, 1.7, P['dientes_abajo'], semilla=13)
    for x in (-2.6, 2.6):
        colmillo(out, Mj, (x * 0.9, 0.0, 11.6), 2.8, 1.2, (0, 1, -0.1), P, semilla=14)
    # el nucleo al fondo de la garganta
    Mv = Mh @ vr.T(0, -0.4, -4.2) @ vr.Rx(abre * 0.5 * D)
    bm.cubo(out, Mv, -4.0, -4.6, 0.0, 8.0, 4.6, 0.1, None, caras={'frente': P['nucleo']}, semilla=15)
    return pt(Mh, (0.0, -2.5, 2.0)), Mh


def branquias(out, P, Mh, tipo, semilla=0):
    """Las branquias de fuera: tres a cada lado de la nuca, que enmarcan la cabeza. En la Plumada, tallos curvos con
    plumillas que arden en la punta; en la Cornuda, cuernos de hueso que se ramifican; en la Barbada, tallos largos
    que cuelgan como barbas y acaban en un bulbo de luz."""
    puntas = []
    for s in (1, -1):
        for j, (y, dl, L) in enumerate(((2.4, (0.55, 1.0, -0.45), 15.0), (0.6, (1.0, 0.35, -0.55), 14.0),
                                         (-1.2, (0.9, -0.25, -0.6), 11.0))):
            base = pt(Mh, (s * 6.8, y, -3.6))
            d = _u(Mh[:3, :3] @ np.array((s * dl[0], dl[1], dl[2])))
            if tipo == 'C':                                                        # cintas hacia atras
                d = _u(Mh[:3, :3] @ np.array((s * 0.75, 0.35 - 0.35 * j, -0.75)))
                L = L * 1.3
            lado = _u(np.cross(d, Mh[:3, 1]))
            arriba = _u(np.cross(lado, d))
            curva = arriba if tipo != 'C' else -arriba
            ctrl = [base, base + d * L * 0.35 + curva * L * 0.08, base + d * L * 0.7 + curva * L * 0.12,
                    base + d * L + curva * (L * 0.05 if tipo != 'C' else -L * 0.1)]
            if tipo == 'C':
                pts, rs, ts = jm.a_lo_largo(ctrl, 10, ((0.0, 1.0), (1.0, 1.0)))
                jm.tubo(out, pts, [0.9 - 0.06 * k for k in range(len(pts))], [P['piel']] * (len(pts) - 1), semilla=semilla + 2)
                altos = [3.6 * math.sin(math.pi * min(1.0, k / 10 * 1.05)) ** 0.7 + 0.2 for k in range(len(pts))]
                for sgn in (1, -1):
                    aleta(out, P, pts, [arriba * sgn] * len(pts), altos, rayos=False, semilla=semilla + 5)
                puntas.append(pts[-1])
                continue
            if tipo == 'B':                                                        # cuernos que se ramifican
                pts, rs, ts = jm.a_lo_largo(ctrl, 8, ((0.0, 1.5), (0.6, 0.9), (1.0, 0.35)))
                jm.tubo(out, pts, rs, [P['hueso']] * (len(pts) - 1), semilla=semilla)
                for t_ in (0.4, 0.7):
                    q = pts[int(t_ * 8)]
                    rama = _u(d * 0.4 + arriba * 1.0)
                    jm.tubo(out, [q, q + rama * L * 0.22, q + rama * L * 0.3 + d * L * 0.05], [0.7, 0.45, 0.25],
                            [P['hueso']] * 2, semilla=semilla + 1)
                puntas.append(pts[-1])
                continue
            pts, rs, ts = jm.a_lo_largo(ctrl, 10, ((0.0, 1.1), (1.0, 0.45)))
            jm.tubo(out, pts, rs, [P['piel']] * (len(pts) - 1), semilla=semilla + 2)
            if tipo == 'A':                                                        # las plumillas
                fino = jm.a_lo_largo(ctrl, 20, ((0.0, 1.0), (1.0, 1.0)))[0]
                for k in range(2, 21):
                    q = fino[k]
                    t_ = k / 20
                    l = 3.6 - 2.2 * t_
                    for sgn in (1, -1):
                        f = _u(arriba * 0.85 + lado * sgn * 0.55 - d * 0.45)
                        M = em.marco(q, f, up=d)
                        caja(out, M, -0.12, 0.12, -0.28, 0.28, 0.0, l, P['pluma'], semilla=semilla + 3)
            puntas.append(pts[-1])
    return puntas


def aleta(out, P, base, arriba, altos, rayos=True, borde=True, semilla=0):
    """Una aleta a lo largo de una linea (base, con su 'arriba' en cada punto): la membrana oscura en bandas, los
    radios de hueso y, si borde, el canto encendido."""
    tops = [b + a * h for b, a, h in zip(base, arriba, altos)]
    for k in range(len(base) - 1):
        a0, a1, b0, b1 = base[k], base[k + 1], tops[k], tops[k + 1]
        L = float(np.linalg.norm(a1 - a0))
        H = max(float(np.linalg.norm(b0 - a0)), float(np.linalg.norm(b1 - a1)), 0.4)
        lamina(out, (a0, a1, b1, b0), P['aleta'], max(L, 0.4), H, semilla=semilla)
        lamina(out, (a1, a0, b0, b1), P['aleta'], max(L, 0.4), H, semilla=semilla)
        if rayos and altos[k] > 0.6:
            jm.tubo(out, [a0, b0 + (b0 - a0) * 0.1], [0.3, 0.15], [P['hueso']], semilla=semilla + 1)
    if borde:
        jm.tubo(out, tops, [0.32] * len(tops), [P['luz']] * (len(tops) - 1), semilla=semilla + 2)


def pata(out, P, puntos, radios, dedos, adelante, abajo, abre=1.0, semilla=0):
    """Una pata de salamandra: el muslo y la canilla gruesos y, al final, la mano o el pie con cuatro dedos abiertos
    y la garra oscura."""
    puntos = [np.asarray(p, float) for p in puntos]
    jm.tubo(out, puntos, radios, [P['piel']] * (len(puntos) - 1), semilla=semilla)
    for p, r in zip(puntos[1:-1], radios[1:-1]):
        caja(out, vr.T(*p), -r, r, -r, r, -r, r, P['piel'], semilla=semilla + 1)
    fin = puntos[-1]
    adelante, abajo = _u(adelante), _u(abajo)
    for j, a in enumerate((-42, -14, 14, 42)):
        Md = em.marco(fin, adelante, up=-abajo) @ vr.Ry(a * abre * D)
        for k, (l, w) in enumerate(((dedos, 0.75), (dedos * 0.8, 0.6))):
            caja(out, Md, -w, w, -w * 0.8, w * 0.8, -0.2, l, P['piel'], semilla=semilla + 2)
            Md = Md @ vr.T(0, 0, l) @ vr.Rx(10 * D)
        Md = Md @ vr.Rx(25 * D)
        caja(out, Md, -0.45, 0.45, -0.45, 0.45, -0.1, 1.8, P['garra'], semilla=semilla + 3)
        caja(out, Md @ vr.T(0, 0, 1.6) @ vr.Rx(30 * D), -0.28, 0.28, -0.28, 0.28, -0.1, 1.2, P['garra'], semilla=semilla + 3)


# ======================================================================
#  BRANQUARA
# ======================================================================
def branquara(tipo='A', abre=38.0):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    luces = []
    try:
        # el tronco, que se alza de la pelvis al pecho, con el vientre en escudos por delante
        esp = [np.array(p, float) for p in ((0, 9, -6), (0, 16, -2), (0, 24, 3.0), (0, 31, 7.0), (0, 36, 10.0))]
        pts, rs, ts = jm.a_lo_largo(esp, 10, ((0.0, 6.0), (0.3, 6.4), (0.7, 5.4), (1.0, 4.4)))
        jm.tubo(out, pts, rs, [P['piel']] * (len(pts) - 1), semilla=10)
        for j in range(len(pts) - 1):
            d = pts[j + 1] - pts[j]
            M = em.marco(pts[j], d, up=(0.0, 0.0, 1.0))
            r = (rs[j] + rs[j + 1]) / 2
            caja(out, M, -r * 0.62, r * 0.62, r * 0.6, r * 1.0, 0.0, float(np.linalg.norm(d)) + 0.2, P['vientre'], semilla=11)
        # la cola, que baja al suelo y se enrosca a un lado
        cola = [np.array(p, float) for p in ((0, 9, -6), (0, 6, -15), (1.5, 3.4, -24), (6.0, 2.8, -32), (12.0, 3.4, -36),
                                             (17.0, 4.2, -34))]
        cpts, crs, cts = jm.a_lo_largo(cola, 14, ((0.0, 5.6), (0.4, 3.8), (0.8, 1.8), (1.0, 0.8)))
        jm.tubo(out, cpts, crs, [P['piel']] * (len(cpts) - 1), semilla=12)
        # las patas de atras, abiertas como las de una salamandra, y las de delante, en alto
        for s in (1, -1):
            pata(out, P, [(s * 5.0, 8.0, -4.5), (s * 11.0, 10.0, -1.5), (s * 13.5, 1.8, 2.0)], [3.4, 2.8, 2.0], 2.2,
                 (s * 0.3, 0, 1.0), (0, -1, 0), semilla=20)
            pata(out, P, [(s * 5.0, 27.0, 6.0), (s * 11.5, 25.0, 10.0), (s * 13.5, 30.0, 15.5)], [2.8, 2.3, 1.8], 2.4,
                 (s * 0.2, 0.5, 1.0), (0, 0.3, 1.0), abre=1.3, semilla=24)
        # la cabeza, ancha, echada hacia delante y un poco hacia abajo, hacia quien la mira
        Mh = vr.T(0.0, 40.0, 17.0) @ vr.Rx(16 * D) @ np.diag([CABEZA] * 3 + [1.0])
        jm.tubo(out, [esp[-1], pt(Mh, (0.0, 0.8, -4.5))], [4.4, 4.6], [P['piel']], semilla=13)
        bm.PPB = PPB / CABEZA
        boca, Mh = cabeza(out, Mh, P, abre)
        bm.PPB = PPB
        luces.append(boca)
        puntas = branquias(out, P, Mh, tipo, semilla=30)
        # el lomo: la aleta (A), puas de hueso (B) o una vela alta (C), del cuello a la punta de la cola
        lomo = [pt(Mh, (0.0, 3.6, -4.0))] + [p + np.array((0.0, 0.0, -r * 0.92)) for p, r in zip(pts[::-1], rs[::-1])]
        lomo += [p + np.array((0.0, r * 0.95, 0.0)) for p, r in zip(cpts[1:], crs[1:])]
        arr = [_u(np.array((0.0, 0.3, -1.0)))] * (len(pts) + 1) + [np.array((0.0, 1.0, 0.0))] * (len(cpts) - 1)
        n = len(lomo)
        if tipo == 'B':
            for k in range(1, n - 2, 2):
                h = 3.6 * math.sin(math.pi * k / n) + 1.2
                pua(out, lomo[k], arr[k] + np.array((0.0, 0.25, 0.0)), 0.7, h, P['hueso'], semilla=40)
        else:
            alto = 9.0 if tipo == 'C' else 3.4
            altos = [alto * (math.sin(math.pi * min(1.0, (k / (n - 1)) * 1.1)) ** 0.8) + 0.3 for k in range(n)]
            aleta(out, P, lomo, arr, altos, semilla=41)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    return out, {'boca': luces[0], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

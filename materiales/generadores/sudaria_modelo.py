"""
Sudaria y sus formas (14-10-2026). Juan: «no todo tiene que ver con una boca con dientes grande; pudiste haber
hecho como una momia, algo asi raro» y «no todo es hacer una cabeza grande». Elegido con libertad.

Una criatura amortajada: alta y enjuta, de brazos muy largos, envuelta de pies a cabeza en vendas oscuras. No tiene
boca ni cabeza grande. Lo que manda es la luz que lleva dentro, que se le escapa por las rendijas de las vendas, y un
solo ojo encendido que asoma por un hueco de la cara, un poco a un lado. De las manos le salen las garras desnudas
y de todo el cuerpo le cuelgan cabos de venda sueltos. Todo de cajas y laminas, con texturas limpias (las vendas en
bandas diagonales, con la junta oscura y alguna encendida).

Las tres formas cambian la silueta:

    A  la Reptante   a cuatro patas, con el lomo arqueado, las manos en el suelo y la cabeza baja que mira hacia
                     arriba; los cabos de venda arrastran; ambar
    B  la Desatada   erguida, con los brazos en alto; las vendas del pecho se le abren en un hueco por donde se ve la
                     luz de dentro y los cabos sueltos le giran alrededor en arcos enormes; carmesi
    C  la Velada     cubierta por un velo que le cae de la cabeza al suelo, como una campana de tela, con los dos
                     brazos fuera abriendolo; el ojo arde en la sombra de la capucha y la luz sale por el bajo; blanco
"""
import math, random
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

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 8
ESCALA = 0.68

GARRA = _r('060506', '0c0a0c', '141114', '1e1a1e', '2a242a')
VARIANTES = {
    'A': dict(
        clave='A', nombre='la Reptante', corto='reptante',
        venda=_r('16120c', '221c14', '2e261c', '3c3326', '4c4232'),
        velo=_r('16120c', '221c14', '2e261c', '3c3326', '4c4232'),
        dentro=_r('080605', '0e0b08', '16110c', '201810', '2a2016'),
        neon=('fff2d6', 'ffb22a', '6a3a04'),
    ),
    'B': dict(
        clave='B', nombre='la Desatada', corto='desatada',
        venda=_r('1a1214', '261a1c', '322426', '423032', '543e40'),
        velo=_r('1a1214', '261a1c', '322426', '423032', '543e40'),
        dentro=_r('0a0506', '12080a', '1a0c0e', '241214', '30181a'),
        neon=('ffe2e6', 'ff2a46', '6a0410'),
    ),
    'C': dict(
        clave='C', nombre='la Velada', corto='velada',
        venda=_r('141618', '1e2124', '292d30', '363b3f', '464c51'),
        velo=_r('16181a', '202326', '2b2f33', '393e43', '4a5056'),
        dentro=_r('060708', '0b0c0e', '111316', '181b1e', '202428'),
        neon=('ffffff', 'cfefff', '2a5a7a'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'sud%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def _vendas(tw, th, s, luz):
        """Las vendas: bandas diagonales de 8 pixeles en dos tonos, con la junta oscura de 2; con luz, una de
        cada tres juntas es una rendija encendida."""
        ys, xs = np.mgrid[0:th, 0:tw]
        d = xs + ys + (s % 5)
        banda = d // 8
        pos = d % 8
        idx = np.where(banda % 2 == 0, 2, 3)
        junta = pos < 2
        idx = np.where(junta, 1, idx)
        t = _imagen(idx, V['venda'])
        e = None
        if luz:
            rendija = junta & (banda % 3 == 1)
            c_m = np.array(nm._hex(neo))
            t[..., :3] = np.where(rendija[..., None], c_m, t[..., :3])
            e = _emis(t, rendija, 230)
        return t, e

    reg('venda', lambda tw, th, c, s: _vendas(tw, th, s, False))
    reg('venda_luz', lambda tw, th, c, s: _vendas(tw, th, s, True))

    def cinta(tw, th, cara, s):
        """Un cabo de venda suelto (pintado de traves sobre la lamina): el centro claro, los cantos oscuros y
        una costura a lo largo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        u = np.abs((xs + 0.5) / tw - 0.5) * 2
        idx = np.where(u < 0.45, 3, np.where(u < 0.8, 2, 1))
        idx = np.where((ys % 6) == 0, idx - 1, idx)
        return _imagen(np.clip(idx, 0, 4), V['venda']), None
    reg('cinta', cinta)

    def velo(tw, th, cara, s):
        """El velo: tela en pliegues verticales anchos, con la sombra del pliegue y el canto claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = xs % 8
        idx = np.where(f < 2, 1, np.where(f < 5, 2, np.where(f < 7, 3, 4)))
        return _imagen(idx, V['velo']), None
    reg('velo', velo)

    def dentro(tw, th, cara, s):
        """Lo de dentro: oscuro y liso, con grietas finas encendidas en zigzag."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx = _bisel(idx, 1, 1)
        t = _imagen(idx, V['dentro'])
        grieta = ((xs + (ys // 3) % 2 * 2 + (s % 5)) % 9 == 0) & ((ys // 6) % 2 == 0)
        c_m = np.array(nm._hex(neo))
        t[..., :3] = np.where(grieta[..., None], c_m, t[..., :3])
        return t, _emis(t, grieta, 220)
    reg('dentro', dentro)
    reg('garra', jm.liso(GARRA, 2, 1, 1))

    def ojo(tw, th, cara, s):
        """El ojo: redondo, en anillos, del blanco del centro al neon, con el canto oscuro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((r < 0.35)[..., None], np.array(c_n),
                       np.where((r < 0.7)[..., None], np.array(qm._mezcla(c_m, c_n, 0.35)), np.array(c_m)))
        col = np.where((r > 0.92)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r <= 0.92, 240)
    reg('ojo', ojo)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def _u(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def miembro(out, P, puntos, radios, pintor, semilla=0):
    """Un miembro vendado: un tubo de bloques por los puntos, con un anillo de venda en cada junta."""
    puntos = [np.asarray(p, float) for p in puntos]
    jm.tubo(out, puntos, radios, [pintor] * (len(puntos) - 1), semilla=semilla)
    for j in range(1, len(puntos) - 1):
        r = radios[j] * 0.98
        caja(out, vr.T(*puntos[j]), -r, r, -r, r, -r, r, pintor, semilla=semilla + 1)


def cinta(out, P, ctrl, ancho, giro=0.0, semilla=0, n=14):
    """Un cabo de venda suelto: una tira a lo largo de la curva, que se retuerce poco a poco (giro, en vueltas) y
    se estrecha al final, cortada en bisel."""
    ctrl = [np.asarray(c, float) for c in ctrl]
    pts, _, ts = jm.a_lo_largo(ctrl, n, ((0.0, 1.0), (1.0, 1.0)))
    ref = np.array((0.0, 1.0, 0.0))
    filas = []
    for k, p in enumerate(pts):
        a = pts[min(k + 1, n)] - pts[max(k - 1, 0)]
        t_ = _u(a)
        lado = np.cross(t_, ref)
        if np.linalg.norm(lado) < 0.2:
            lado = np.cross(t_, np.array((1.0, 0.0, 0.0)))
        lado = _u(lado)
        normal = np.cross(lado, t_)
        ang = giro * TAU * ts[k]
        lado = lado * math.cos(ang) + normal * math.sin(ang)
        w = ancho / 2 * (1.0 if ts[k] < 0.8 else 1.0 - (ts[k] - 0.8) * 2.5)
        corte = 0.6 * ancho if k == n else 0.0
        filas.append((p - lado * w, p + lado * w + t_ * corte))
    for k in range(n):
        (a0, b0), (a1, b1) = filas[k], filas[k + 1]
        L = float(np.linalg.norm(pts[k + 1] - pts[k]))
        W_ = max(float(np.linalg.norm(b0 - a0)), 0.5)
        lamina(out, (a0, b0, b1, a1), P['cinta'], W_, max(L, 0.5), semilla=semilla)
        lamina(out, (a1, b1, b0, a0), P['cinta'], W_, max(L, 0.5), semilla=semilla)


def mano(out, P, muneca, adelante, abajo, abre=1.0, semilla=0):
    """Una mano de dedos muy largos, vendados, con la garra desnuda y oscura: tres dedos y el pulgar."""
    muneca, adelante, abajo = np.asarray(muneca, float), _u(adelante), _u(abajo)
    lado = _u(np.cross(abajo, adelante))
    M = em.marco(muneca, adelante, up=-abajo)
    caja(out, M, -1.6, 1.6, -0.9, 0.9, -0.4, 2.6, P['venda'], semilla=semilla)                       # la palma
    for j, (x, a, L) in enumerate(((-1.1, -16, 1.0), (0.0, 0, 1.15), (1.1, 16, 1.0), (-1.8, -60, 0.65))):
        Md = M @ vr.T(x, 0, 2.4 if j < 3 else 0.8) @ vr.Ry(a * abre * D)
        for k, (l, w) in enumerate(((2.6, 0.5), (2.2, 0.42))):
            Md = Md @ vr.Rx(18 * D)
            caja(out, Md, -w, w, -w, w, -0.1, l * L, P['venda'], semilla=semilla + 1)
            Md = Md @ vr.T(0, 0, l * L)
        Md = Md @ vr.Rx(28 * D)                                                                         # la garra
        caja(out, Md, -0.36, 0.36, -0.36, 0.36, -0.1, 1.6 * L, P['garra'], semilla=semilla + 2)
        caja(out, Md @ vr.T(0, 0, 1.5 * L) @ vr.Rx(30 * D), -0.22, 0.22, -0.22, 0.22, -0.1, 1.0 * L, P['garra'], semilla=semilla + 2)


def cabeza(out, Mh, P, V, semilla=0):
    """La cabeza, a la medida del cuerpo, de cara a +z: un huevo alargado de vendas, con dos tiras cruzadas sobre
    la cara y un hueco, un poco a la izquierda, por donde asoma el ojo, redondo y encendido; detras, los cabos de
    la venda de la cabeza. Devuelve el ojo."""
    v = P['venda']
    caja(out, Mh, -2.6, 2.6, -3.0, 3.0, -2.8, 2.4, v, semilla=semilla)
    caja(out, Mh, -2.2, 2.2, -3.5, 3.5, -2.4, 2.0, v, semilla=semilla + 1)
    caja(out, Mh, -3.0, 3.0, -2.4, 2.4, -2.4, 2.0, v, semilla=semilla + 2)
    caja(out, Mh, -2.0, 2.0, -2.4, 2.6, -3.2, 2.8, v, semilla=semilla + 3)
    Mb = Mh @ vr.T(0, 1.0, -2.0) @ vr.Rx(35 * D)                                                       # el craneo, hacia atras
    caja(out, Mb, -2.2, 2.2, -2.2, 2.2, -4.6, 0.6, v, semilla=semilla + 7)
    caja(out, Mb, -1.5, 1.5, -1.5, 1.5, -6.4, -4.2, v, semilla=semilla + 8)
    caja(out, Mh, -2.6, 0.8, -0.6, 2.2, 2.3, 2.7, P['dentro'], semilla=semilla + 5)                    # el hueco
    caja(out, Mh, -2.3, 0.5, -0.45, 2.05, 2.6, 2.85, P['ojo'], semilla=semilla + 6)                    # el ojo
    for y, a in ((2.3, -14), (-0.75, -14), (-2.4, 10)):                                                # las vendas de la cara
        Mt = Mh @ vr.T(0, y, 2.75) @ vr.Rz(a * D)
        caja(out, Mt, -3.3, 3.3, -0.65, 0.65, -0.25, 0.3, P['cinta'], semilla=semilla + 4)
    return pt(Mh, (-0.9, 0.8, 3.2))


def velo(out, P, cima, radio_suelo, alto_suelo, abre=0.0, semilla=0):
    """El velo: una campana de tela que cae de la cabeza al suelo en paneles con pliegues, abierta por delante
    (abre, en grados) para que salgan los brazos; con la capucha alrededor de la cabeza."""
    cima = np.asarray(cima, float)
    n = 16
    for k in range(n):
        a0, a1 = TAU * k / n, TAU * (k + 1) / n
        mid = (a0 + a1) / 2
        hueco = abs(((mid + math.pi) % TAU) - math.pi)                                                 # 0 = de frente
        if hueco < abre * D / 2:
            continue
        fil = []
        for a in (a0, a1):
            u = np.array((math.sin(a), 0.0, math.cos(a)))
            arriba = cima + u * 3.4
            abajo_ = np.array((u[0] * radio_suelo, alto_suelo, u[2] * radio_suelo))
            medio = arriba + (abajo_ - arriba) * 0.45 + u * 2.0
            fil.append((arriba, medio, abajo_))
        for j in range(2):
            p0, p1 = fil[0][j], fil[1][j]
            q0, q1 = fil[0][j + 1], fil[1][j + 1]
            ancho = float(np.linalg.norm(p1 - p0) + np.linalg.norm(q1 - q0)) / 2
            alto = float(np.linalg.norm(q0 - p0))
            lamina(out, (q0, q1, p1, p0), P['velo'], max(ancho, 0.5), alto, semilla=semilla)
            lamina(out, (p0, p1, q1, q0), P['velo'], max(ancho, 0.5), alto, semilla=semilla)
    for k in range(n):                                                                                 # el bajo, encendido
        a0, a1 = TAU * k / n, TAU * (k + 1) / n
        mid = (a0 + a1) / 2
        if abs(((mid + math.pi) % TAU) - math.pi) < abre * D / 2:
            continue
        p0 = np.array((math.sin(a0) * radio_suelo, alto_suelo + 0.3, math.cos(a0) * radio_suelo))
        p1 = np.array((math.sin(a1) * radio_suelo, alto_suelo + 0.3, math.cos(a1) * radio_suelo))
        jm.tubo(out, [p0, p1], [0.4, 0.4], [P['luz']], semilla=semilla + 1)


# ======================================================================
#  SUDARIA
# ======================================================================
POSES = {
    # pelvis, lomo, pecho, cuello, cabeza (centro), inclinacion de la cabeza;
    # hombro, codo, muneca, (adelante, abajo) de la mano; cadera, rodilla, tobillo, punta del pie
    'A': dict(espina=[(0, 22, -7), (0, 31, -2), (0, 33, 5), (0, 32.5, 10)], cabeza=((0, 33.0, 14.5), -24),
              hombro=(7.0, 31.5, 5.0), codo=(12.5, 20.0, 10.0), muneca=(12.5, 6.0, 16.0), mano=((0.15, -0.3, 1.0), (0, -1, 0.2)),
              cadera=(4.0, 21.0, -7.0), rodilla=(6.5, 12.0, 0.0), tobillo=(6.0, 2.6, -8.0), pie=(6.0, 0.6, -3.0)),
    'B': dict(espina=[(0, 25, 0), (0, 33, 0.5), (0, 41, 2.5), (0, 46, 3.5)], cabeza=((0, 50.5, 4.8), -6),
              hombro=(7.0, 43.0, 2.0), codo=(15.0, 49.0, 3.0), muneca=(20.0, 58.0, 5.0), mano=((0.3, 1.0, 0.3), (0, 0.2, 1)),
              cadera=(4.0, 24.0, 0.0), rodilla=(5.0, 13.0, 2.5), tobillo=(5.5, 3.0, -0.5), pie=(5.5, 0.6, 4.0)),
    'C': dict(espina=[(0, 25, 0), (0, 33, 0.5), (0, 41, 2.0), (0, 46, 3.0)], cabeza=((0, 50.0, 4.4), 8),
              hombro=(7.0, 43.0, 2.0), codo=(10.5, 33.0, 8.0), muneca=(15.0, 24.0, 13.0), mano=((0.5, -0.4, 1.0), (0, -1, 0.3)),
              cadera=(4.0, 24.0, 0.0), rodilla=(4.6, 13.0, 1.5), tobillo=(4.8, 3.0, -0.5), pie=(4.8, 0.6, 4.0)),
}


def sudaria(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    Q = POSES[tipo]
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    luces = []
    rng = random.Random(7)
    try:
        esp = [np.array(p, float) for p in Q['espina']]
        # el tronco: enjuto en la cintura, ancho en el pecho y con la giba de los hombros; las vendas con rendijas
        pts, rs, ts = jm.a_lo_largo(esp, 8, ((0.0, 4.6), (0.3, 3.6), (0.7, 5.6), (1.0, 4.4)))
        jm.tubo(out, pts, rs, [P['venda_luz']] * (len(pts) - 1), semilla=10, achata=0.8)
        for j in range(1, len(pts) - 1, 2):                                                           # los anillos de venda
            M = em.marco(pts[j], pts[j + 1] - pts[j - 1], up=(0.0, 0.0, 1.0))
            g = rs[j] * 1.08
            caja(out, M, -g, g, -g * 0.85, g * 0.85, -0.5, 0.5, P['venda'], semilla=11)
        pecho = pts[6]
        if tipo == 'B':                                                                              # el hueco del pecho, abierto
            adelante = np.array((0.0, 0.1, 1.0))
            M = em.marco(pecho + adelante * (rs[6] * 0.55), adelante)
            caja(out, M, -3.4, 3.4, -5.4, 4.4, -1.2, 0.6, P['dentro'], semilla=12)
            caja(out, M, -2.2, 2.2, -3.4, 2.6, 0.4, 0.9, P['luz'], semilla=13)
            for s in (1, -1):                                                                        # los bordes de venda, abiertos
                caja(out, M @ vr.T(s * 3.9, -0.5, 0.3) @ vr.Rz(s * 6 * D), -0.8, 0.8, -6.0, 5.0, -0.6, 1.3, P['venda'], semilla=14)
            luces.append(pt(M, (0.0, -0.3, 1.8)))
        else:                                                                                        # una rendija en el pecho
            adelante = _u(np.array((0.0, -0.2 if tipo == 'A' else 0.1, 1.0)))
            M = em.marco(pecho + adelante * (rs[6] * 0.7), adelante)
            caja(out, M, -0.5, 0.5, -2.6, 2.2, -0.4, 0.5, P['luz'], semilla=13)
            luces.append(pt(M, (0.0, 0.0, 1.4)))
        # la cabeza
        c, incl = Q['cabeza']
        Mh = vr.T(*c) @ vr.Rx(incl * D)
        jm.tubo(out, [esp[-1], pt(Mh, (0.0, -1.2, -2.0))], [2.4, 2.0], [P['venda']], semilla=15)
        ojo = cabeza(out, Mh, P, V, semilla=20)
        luces.insert(0, ojo)
        for k, (x, y) in enumerate(((1.6, 2.2), (-1.0, 2.8))):                                       # los cabos de la cabeza
            b = pt(Mh, (x, y, -2.8))
            atras = Mh[:3, :3] @ np.array((0.0, 0.0, -1.0))
            cinta(out, P, [b, b + atras * 4 + np.array((x * 0.8, -3.0, 0.0)), b + atras * 7 + np.array((x * 2.0, -9.0, 0.0)),
                           b + atras * 8 + np.array((x * 2.5, -15.0 + k * 3, 0.0))], 1.8, giro=0.4, semilla=21)
        # los brazos y las manos
        for s in (1, -1):
            h = np.array(Q['hombro']) * (s, 1, 1)
            co = np.array(Q['codo']) * (s, 1, 1)
            mu = np.array(Q['muneca']) * (s, 1, 1)
            caja(out, vr.T(*h), -2.8, 2.8, -2.6, 2.6, -2.6, 2.6, P['venda'], semilla=30)
            miembro(out, P, [h, co, mu], [2.4, 1.9, 1.5], P['venda'], semilla=31)
            ad, ab = Q['mano']
            mano(out, P, mu, np.array(ad) * (s, 1, 1), np.array(ab) * (s, 1, 1), abre=1.0 if tipo != 'B' else 1.6, semilla=33)
            for t in (0.35, 0.7):                                                                    # los cabos de los brazos
                b = co + (mu - co) * t
                if tipo == 'B':
                    cinta(out, P, [b, b + np.array((s * 6, -4, -3)), b + np.array((s * 9, -14, 2)), b + np.array((s * 6, -24, 6))],
                          1.6, giro=0.6, semilla=34)
                else:
                    cinta(out, P, [b, b + np.array((s * 1.0, -3.0, -1.0)), b + np.array((s * 1.5, -6.0, -2.5)),
                                   b + np.array((s * 1.2, -min(b[1] - 0.3, 10.0), -4.0))], 1.4, giro=0.3, semilla=34)
        # las piernas
        if tipo != 'C':
            for s in (1, -1):
                ca, ro, to, pi = (np.array(Q[n]) * (s, 1, 1) for n in ('cadera', 'rodilla', 'tobillo', 'pie'))
                miembro(out, P, [ca, ro, to], [2.4, 1.9, 1.4], P['venda'], semilla=40)
                M = em.marco(to, pi - to)
                caja(out, M, -1.2, 1.2, -0.9, 1.0, -0.6, float(np.linalg.norm(pi - to)) + 1.0, P['venda'], semilla=41)
                for j, a in enumerate((-14, 0, 14)):                                                  # las garras del pie
                    Mg = em.marco(pi, pi - to) @ vr.Ry(a * D) @ vr.T((j - 1) * 0.7, 0, 0.6) @ vr.Rx(20 * D)
                    caja(out, Mg, -0.3, 0.3, -0.3, 0.3, -0.1, 1.4, P['garra'], semilla=42)
        # B: los cabos sueltos giran a su alrededor en arcos enormes
        if tipo == 'B':
            for k in range(8):
                a = TAU * k / 8 + 0.3
                r0, r1 = 12.0, 22.0 + (k % 2) * 4
                y0 = 16 + k * 4
                ctrl = [esp[1 + k % 3] + np.array((math.sin(a) * 3, 0, math.cos(a) * 3))]
                for j in range(1, 5):
                    aa = a + j * 0.55
                    rr = r0 + (r1 - r0) * j / 4
                    ctrl.append(np.array((math.sin(aa) * rr, y0 + j * 4.5 - (k % 3) * 3, math.cos(aa) * rr * 0.75)))
                cinta(out, P, ctrl, 2.6, giro=0.8, semilla=50 + k, n=20)
        # A: los cabos que arrastran del lomo
        if tipo == 'A':
            for k, x in enumerate((-2.5, 0.5, 3.0)):
                b = esp[1] + np.array((x, 3.0, -2.0))
                cinta(out, P, [b, b + np.array((x * 0.5, -1.0, -6.0)), b + np.array((x * 0.8, -12.0, -9.0)),
                               np.array((b[0] + x, 0.3, b[2] - 16.0 - k * 2))], 2.0, giro=0.3, semilla=60 + k)
        # C: el velo, de la cabeza al suelo, abierto por delante para los brazos, y la capucha
        if tipo == 'C':
            cima = np.array(c) + np.array((0.0, 2.6, -0.8))
            velo(out, P, cima, 15.0, 0.0, abre=70.0, semilla=70)
            Mc = vr.T(*c) @ vr.Rx(incl * D)
            for (x0, x1, y0, y1, z0, z1) in ((-4.6, 4.6, 2.2, 4.8, -5.0, 4.4), (-3.8, 3.8, 4.6, 6.0, -4.6, 3.2),
                                             (-2.6, 2.6, 5.8, 6.8, -3.8, 1.6), (-5.0, -3.2, -4.4, 3.4, -4.8, 4.2),
                                             (3.2, 5.0, -4.4, 3.4, -4.8, 4.2), (-4.2, 4.2, -3.0, 4.6, -6.6, -3.8)):
                caja(out, Mc, x0, x1, y0, y1, z0, z1, P['velo'], semilla=71)
            for s in (1, -1):                                                                        # los cabos bajo el velo
                for t in (0.0, 1.0):
                    b = np.array((s * (3.5 + t * 2), 18.0 - t * 4, 6.0))
                    cinta(out, P, [b, b + np.array((s * 0.5, -6, 1)), b + np.array((s * 1.0, -12 + t * 2, 2)),
                                   np.array((b[0] + s, 0.3, b[2] + 4))], 1.6, giro=0.3, semilla=72)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    return out, {'boca': luces[0], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

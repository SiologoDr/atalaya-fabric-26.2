"""
Almenara, la Gargola de las Atalayas (13-10-2026). Juan: «ahora hagamos un boss con sus 3 tipos,
con borde blanco», despues de cerrar Lumara («el mejor diseno que me gusto»).

Una gargola de piedra que vela las atalayas en ruinas: se agazapa sobre un capitel roto, se
agarra al borde con las garras y asoma la cabeza como un canalon. Su boca es la almenara, el
fuego de senal de las atalayas: arde por dentro con su neon, y esa luz se le escapa por las
grietas de la piedra. Hecha con lo aprendido en Lumara: la cabeza manda (grande y maciza, se hace
sin escala y se pone agrandada), los dientes van dibujados en hojas, la piedra esta dibujada a
mano, los tambores de la cola son de una pieza y cada foto lleva el borde blanco y ninguna letra.

Los tres tipos cambian de FORMA:

    A  Alada                   alas de piedra abiertas hacia arriba y atras; neon cian
    B  de los Cuatro Brazos    sin alas: un segundo par de brazos alzado, con las garras
                               abiertas, y una cresta de puas con vela; neon oro
    C  del Manto               las alas cerradas por delante como una capucha: de la piedra
                               solo asoman la boca encendida, los ojos y los cuernos, que la
                               atraviesan; neon violeta

Mismo oficio que Lumara: cajas con las caras pintadas a 8 px por bloque, sin ruido.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
import sierpe_modelo as sm
from bestias_modelo import cubo, viga, pua, punto, _imagen, _emis
from sierpe_modelo import _bisel, lamina, bola
from riscara_modelo import bloque
from lumara_modelo import prisma5, _hilera, _dir, _marco_sin_giro

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 8

VARIANTES = {
    'A': dict(
        clave='A', nombre='Alada',
        piedra=_r('161a22', '252b38', '38404f', '515b6c', '737e8f'),
        membrana=_r('0a0d14', '121722', '1b2231', '263044', '34405a'),
        cuerno=_r('101216', '1c2026', '2c323a', '424a54', '5e6874'),
        garra=_r('0c0e12', '171b22', '232934', '343c4a', '4a5466'),
        colmillo=_r('5e5a52', '8e887c', 'bdb6a6', 'ddd8ca', 'f4f1e8'),
        sillar=_r('121419', '1c1f27', '2a2e38', '3b404c', '525866'),
        neon=('effcff', '4fdcff', '0b4a66'),
    ),
    'B': dict(
        clave='B', nombre='de los Cuatro Brazos',
        piedra=_r('1c1614', '2e2522', '453833', '5e4f47', '7d6c61'),
        membrana=_r('100c0a', '1a1412', '261e1a', '342a24', '463a32'),
        cuerno=_r('120e0c', '211a16', '332a24', '4a3e35', '665649'),
        garra=_r('0e0b0a', '1a1513', '28201d', '3a302b', '52453d'),
        colmillo=_r('66604f', '988f78', 'c4baa0', 'e0d8c2', 'f6f2e6'),
        sillar=_r('151110', '221b19', '322825', '453833', '5e4d45'),
        neon=('fffbe6', 'ffd23c', '6a4a06'),
    ),
    'C': dict(
        clave='C', nombre='del Manto',
        piedra=_r('17131e', '262031', '3a3149', '524663', '6f6184'),
        membrana=_r('0e0a14', '17121f', '221b2e', '2f2640', '3f3456'),
        cuerno=_r('110e16', '1e1926', '2e2738', '43394f', '5c4f6c'),
        garra=_r('0d0b12', '18151f', '25202e', '362f42', '4c425c'),
        colmillo=_r('625c64', '938a96', 'c0b6c4', 'ded6e0', 'f5f1f6'),
        sillar=_r('120f17', '1c1824', '2a2434', '3b3349', '524762'),
        neon=('fbf0ff', 'c35aff', '4a0c6a'),
    ),
}

# ----------------------------------------------------------------------
#  La piedra, dibujada a mano: una tesela de 32 x 32 con desgastes claros (3 y 4) que tienen su
#  sombra (1) abajo a la derecha, poros, grietas finas (1) y, pocas, las grietas que brillan (5):
#  por ahi se escapa la luz de la almenara. 2 es el fondo.
# ----------------------------------------------------------------------
_PIEZAS = {
    'P1': ("..3333...",
           ".334433..",
           "33444333.",
           "333333331",
           ".3333311.",
           "...111..."),
    'P2': (".333..",
           "33433.",
           "333331",
           ".3311.",
           "..1..."),
    'P3': (".33.",
           "3431",
           ".11."),
    'Q1': ("1.1",
           ".1."),
    'Q2': ("11",
           "1."),
    'F1': ("1......",
           ".11....",
           "...11..",
           ".....11"),
    'F2': ("....1",
           "...1.",
           "..11.",
           ".1...",
           "1...."),
    'G1': ("5.........",
           "15........",
           ".155......",
           "...15.....",
           "....155...",
           "......15..",
           ".......155"),
    'G2': ("...5..",
           "..51..",
           ".55...",
           "5.1...",
           "5....."),
}
_LUGARES = (('P1', 1, 2), ('P1', 18, 15), ('P2', 3, 20), ('P2', 22, 3), ('P3', 12, 9), ('P3', 27, 26), ('P3', 10, 26),
            ('Q1', 8, 4), ('Q1', 15, 22), ('Q1', 29, 10), ('Q1', 6, 14), ('Q2', 20, 28), ('Q2', 25, 18),
            ('F1', 13, 1), ('F2', 24, 10), ('F1', 5, 24), ('G1', 9, 13), ('G2', 25, 22))


def _hacer_tesela():
    t = np.full((32, 32), 2)
    for nombre, f0, c0 in _LUGARES:
        for i, fila in enumerate(_PIEZAS[nombre]):
            for j, ch in enumerate(fila):
                if ch != '.':
                    t[(f0 + i) % 32, (c0 + j) % 32] = int(ch)
    return t


TESELA = _hacer_tesela()


def _tesela(tw, th, s):
    rng = random.Random(s)
    f0, c0 = rng.randrange(32), rng.randrange(32)
    return TESELA[(np.arange(th)[:, None] + f0) % 32, (np.arange(tw)[None, :] + c0) % 32]


def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'alm%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def _piedra(tw, th, s, rampa, luz=True, mapa=None):
        idx = _tesela(tw, th, s)
        grieta = idx == 5
        base = np.where(grieta, 1, idx)
        if mapa is not None:
            base = np.array(mapa)[base]
        tex = _imagen(_bisel(base), rampa)
        if luz and grieta.any():
            tex[grieta] = (*nm._hex(neo), 255)
            return tex, _emis(tex, grieta, 210)
        return tex, None

    def piedra(tw, th, cara, s):
        """La piedra del cuerpo, dibujada a mano, con las grietas por donde se escapa la luz."""
        return _piedra(tw, th, s, V['piedra'])
    reg('piedra', piedra)

    def piedra_lisa(tw, th, cara, s):
        """La misma piedra sin grietas que brillen (para lo pequeno)."""
        return _piedra(tw, th, s + 3, V['piedra'], luz=False)
    reg('piedra_lisa', piedra_lisa)

    def sillar(tw, th, cara, s):
        """La piedra del capitel: mas oscura y sin luz, para que la gargola se lea encima."""
        return _piedra(tw, th, s + 7, V['sillar'], luz=False)
    reg('sillar', sillar)

    def cuerno(tw, th, cara, s):
        """Los cuernos: anillos oscuros cada tres pixeles a lo largo y el canto claro."""
        largo_x = tw >= th
        ys, xs = np.mgrid[0:th, 0:tw]
        a = xs if largo_x else ys
        idx = np.where((a % 3) == 0, 1, 2)
        if th >= 3 and largo_x:
            idx[0, :] = np.maximum(idx[0, :], 3)
        if tw >= 3 and not largo_x:
            idx[:, 0] = np.maximum(idx[:, 0], 3)
        return _imagen(idx, V['cuerno']), None
    reg('cuerno', cuerno)

    def garra(tw, th, cara, s):
        """Las garras: oscuras y lisas, con una raya clara a lo largo."""
        idx = np.full((th, tw), 2)
        if tw >= th and th >= 2:
            idx[0, :] = 4
            idx[-1, :] = 1
        elif tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 1
        return _imagen(idx, V['garra']), None
    reg('garra', garra)

    def _hojas_de_dientes(tw, th, rampa, colgando):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in rampa]
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

    def colmillos(tw, th, cara, s):
        """Los dientes de arriba, dibujados en una hoja que cuelga del paladar (no cubos)."""
        return _hojas_de_dientes(tw, th, V['colmillo'], True)
    reg('colmillos', colmillos)

    def dientes(tw, th, cara, s):
        """Los dientes de abajo, en una hoja de pie sobre el borde."""
        return _hojas_de_dientes(tw, th, V['colmillo'], False)
    reg('dientes', dientes)

    def boca(tw, th, cara, s):
        """Por dentro de la boca, la almenara: bandas en V del neon, hondas en los bordes y casi
        blancas en el centro."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        u = (xs + 0.5) / tw
        dd = np.minimum(u, 1 - u) * 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((dd < 0.2)[..., None], np.array(c_h),
                       np.where((dd < 0.46)[..., None], np.array(qm._mezcla(c_h, c_m, 0.6)),
                                np.where((dd < 0.76)[..., None], np.array(c_m), np.array(qm._mezcla(c_m, c_n, 0.65)))))
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, dd >= 0.2, 235)
    reg('boca', boca)

    def nucleo(tw, th, cara, s):
        """El fondo de la garganta: el fuego de la almenara, redondo y casi blanco en el centro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        dentro = r < 1.0
        col = np.where((r < 0.45)[..., None], np.array(c_n),
                       np.where((r < 0.75)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m)))
        col = np.where(((r > 0.9) & dentro)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = np.where(dentro, 255, 0)
        return t, _emis(t, dentro & (r < 0.9), 240)
    reg('nucleo', nucleo)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)

    def chorro(tw, th, cara, s):
        """El chorro de la almenara: la luz que se derrama de la canaleta como el agua de una
        gargola. Casi blanca en el centro, del neon hacia los bordes, con vetas que bajan, y abajo
        se deshace en pixeles."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        u = np.abs((xs + 0.5) / tw - 0.5) * 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((u < 0.34)[..., None], np.array(c_n), np.where((u < 0.72)[..., None], np.array(c_m), np.array(c_h)))
        rng = random.Random(s)
        for x in range(tw):                                            # vetas que bajan
            if rng.random() < 0.35:
                y0 = rng.randrange(max(1, th))
                col[y0:y0 + rng.randint(2, max(3, th // 3)), x] = qm._mezcla(c_m, c_h, 0.5)
        v = ys / max(th - 1, 1)
        quedan = ~((v > 0.78) & (((xs + ys) % 2) == 0)) & ~((v > 0.9) & ((xs % 2) == 0))
        t[..., :3] = col
        t[..., 3] = np.where(quedan, 255, 0)
        return t, _emis(t, quedan, 235)
    reg('chorro', chorro)

    def charco(tw, th, cara, s):
        """El charco de luz donde cae el chorro: redondo, claro en el centro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        r = np.hypot(xs - (tw - 1) / 2, ys - (th - 1) / 2) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        dentro = r < 1.0
        col = np.where((r < 0.35)[..., None], np.array(c_n), np.where((r < 0.7)[..., None], np.array(c_m), np.array(c_h)))
        anillo = dentro & (r > 0.82) & (((xs + ys) % 2) == 0)
        t[..., :3] = col
        t[..., 3] = np.where(dentro & ~anillo, 255, 0)
        return t, _emis(t, dentro & ~anillo, 220)
    reg('charco', charco)

    def membrana(tw, th, cara, s):
        """La membrana de las alas: oscura, en bandas a lo largo de los dedos; el borde libre (arriba
        en la textura) recortado en arco y con el canto un poco mas claro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        u = (xs + 0.5) / tw
        idx = np.where(((xs // 3) % 2) == 0, 2, 1)
        v = 1 - (ys + 0.5) / th
        idx = np.where(v < 0.25, np.maximum(idx - 1, 0), idx)
        img = _imagen(idx, V['membrana'])
        borde = (th - 1) * (0.03 + 0.2 * np.sin(np.pi * u))
        fuera = ys < borde
        canto = (~fuera) & (ys < borde + 1.6)
        img[canto] = (*V['membrana'][4], 255)
        t[~fuera] = img[~fuera]
        return t, None
    reg('membrana', membrana)

    def membrana_lisa(tw, th, cara, s):
        """La misma membrana con el borde recto (la vela de la cresta)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs // 3) % 2) == 0, 2, 1)
        idx = np.where(ys < 1, 3, idx)
        return _imagen(idx, V['membrana']), None
    reg('membrana_lisa', membrana_lisa)

    def manto(tw, th, cara, s):
        """El manto (las alas cerradas): la membrana en bandas, con el borde de abajo deshecho en
        jirones (abajo en la textura)."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs // 3) % 2) == 0, 2, 1)
        idx = np.where((xs % 6) == 0, 3, idx)
        rng = random.Random(s)
        cortes = np.array([rng.randint(0, max(1, th // 5)) for _ in range((tw + 1) // 2)])
        cortes = np.repeat(cortes, 2)[:tw]
        fin = th - 1 - cortes[None, :]
        idx = np.where(ys > fin - 2, 0, idx)
        img = _imagen(idx, V['membrana'])
        dentro = ys <= fin
        t[dentro] = img[dentro]
        return t, None
    reg('manto', manto)
    return P


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def _pano(out, raiz, a, b, pintor, semilla=0):
    """Un pano de membrana de la raiz al tramo a-b, que es su borde libre."""
    raiz, a, b = np.asarray(raiz, float), np.asarray(a, float), np.asarray(b, float)
    lamina(out, (raiz, raiz, b, a), pintor, float(np.linalg.norm(b - a)), float(np.linalg.norm((a + b) / 2 - raiz)), semilla)


def _garra(out, p, d, largo, grueso, P, semilla=0, curva=(0.0, -1.0, 0.3)):
    """Una garra de dos tramos que se dobla hacia 'curva'."""
    p = np.asarray(p, float)
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    q = p + d * largo * 0.6
    viga(out, p, q, grueso, grueso, P['garra'], extra=grueso * 0.3, semilla=semilla)
    c = np.asarray(curva, float)
    c = c / np.linalg.norm(c)
    pua(out, em.marco(q, c) @ vr.Rx(90 * D), grueso * 0.42, largo * 0.55, P['garra'], semilla=semilla + 1)


def _mano(out, muneca, frente, abajo, P, s, ancho=1.0, n=4, largo=1.1, semilla=0):
    """Una mano de piedra con 'n' garras hacia 'frente' que se doblan hacia 'abajo'."""
    muneca = np.asarray(muneca, float)
    frente = np.asarray(frente, float)
    frente = frente / np.linalg.norm(frente)
    lado = np.cross(np.array((0.0, 1.0, 0.0)), frente)
    if np.linalg.norm(lado) < 1e-6:
        lado = np.array((1.0, 0.0, 0.0))
    lado = lado / np.linalg.norm(lado)
    M = em.marco(muneca, frente)
    cubo(out, M, -ancho * 0.6, -0.45, -0.2, ancho * 1.2, 0.9, 1.1, P['piedra_lisa'], semilla=semilla)
    for j in range(n):
        f = (j - (n - 1) / 2) / max(n - 1, 1)
        p = muneca + frente * 0.85 + lado * f * ancho * 1.1
        _garra(out, p, frente + lado * f * 0.4, largo, 0.32, P, semilla=semilla + 2 + j, curva=abajo)


def _tambores(out, ctrl, radios, P, semilla=0, puas=True):
    """Una cola de tambores de piedra de una pieza (sin rodajas), con un anillo en cada junta y
    una pua encima de cada tambor; devuelve los puntos de las juntas."""
    curva, _ = em.catmull(ctrl, 400)
    curva = [np.asarray(p, float) for p in curva]
    L = [0.0]
    for a, b in zip(curva, curva[1:]):
        L.append(L[-1] + float(np.linalg.norm(b - a)))
    total = L[-1]

    def en(m):
        i = min(max(int(np.searchsorted(L, m)), 1), len(curva) - 1)
        f = (m - L[i - 1]) / max(L[i] - L[i - 1], 1e-9)
        return curva[i - 1] + (curva[i] - curva[i - 1]) * min(max(f, 0.0), 1.0)

    def radio(m):
        return float(np.interp(m / total, (0.0, 1.0), radios))

    cortes = [0.0]
    while True:
        largo = max(1.2, 2.2 * radio(cortes[-1]))
        if cortes[-1] + largo > total - 0.6:
            break
        cortes.append(cortes[-1] + largo)
    cortes.append(total)
    pts = [en(m) for m in cortes]
    for j in range(len(pts) - 1):
        d = pts[j + 1] - pts[j]
        r = radio((cortes[j] + cortes[j + 1]) / 2)
        M = _marco_sin_giro(pts[j], d) if abs(d[0]) < 0.9 * np.linalg.norm(d) else em.marco(pts[j], d)
        cubo(out, M, -r, -r, -0.3, 2 * r, 2 * r, float(np.linalg.norm(d)) + 0.6, P['piedra'], semilla=semilla + j)
        rb = r * 1.12
        cubo(out, M @ vr.T(0, 0, -0.3), -rb, -rb, 0, 2 * rb, 2 * rb, 0.6, P['piedra_lisa'], semilla=semilla + 30 + j)
        if puas:
            pua(out, M @ vr.T(0, r * 0.8, float(np.linalg.norm(d)) * 0.4) @ vr.Rx(-35 * D), r * 0.32, r * 1.1, P['cuerno'],
                semilla=semilla + 60 + j)
    return pts


# ----------------------------------------------------------------------
#  El capitel roto, donde se posa
# ----------------------------------------------------------------------
ALTO = 8.3                         # lo alto del capitel: ahi apoya las patas


def capitel(out, P):
    """El capitel roto de una columna de las atalayas: el fuste redondo (a escalones de pixel),
    el equino que se ensancha y el abaco cuadrado con una esquina partida; dos cascotes al pie."""
    bm.redondo(out, vr.T(0, 0, -0.4), 0.0, 6.0, 2.4, 2.4, P['sillar'], n=3, semilla=1)
    bm.redondo(out, vr.T(0, 0, -0.4), 6.0, 7.4, 3.4, 3.4, P['sillar'], n=3, semilla=4)
    for i, (x0, z0) in enumerate(((-4.1, -4.5), (0.0, -4.5), (-4.1, -0.4), (0.0, -0.4))):
        alto = 0.5 if i == 0 else 0.9                                                         # la esquina partida
        cubo(out, vr.T(0, 7.4, 0), x0, 0, z0, 4.1, alto, 4.1, P['sillar'], semilla=8 + i)
    cubo(out, vr.T(-4.6, 0, -5.2) @ vr.Ry(25 * D), -0.8, 0, -0.7, 1.6, 1.1, 1.4, P['sillar'], semilla=13)
    cubo(out, vr.T(-3.4, 0, -6.4) @ vr.Ry(-15 * D), -0.5, 0, -0.5, 1.0, 0.7, 1.0, P['sillar'], semilla=14)


# ----------------------------------------------------------------------
#  El cuerpo agazapado
# ----------------------------------------------------------------------
def cuerpo(out, V, P):
    """Agazapada sobre el capitel: las ancas, el vientre y el pecho ancho echados hacia delante;
    las patas de atras dobladas, con los pies y sus garras sobre la piedra; los brazos agarrados
    al borde de delante, con las garras por fuera; las puas del lomo y la cola de tambores que
    baja enroscandose por la columna hasta una punta de pala."""
    k = V['clave']
    H = ALTO
    bloque(out, vr.T(0, H + 2.5, -1.7) @ vr.Rx(-10 * D), 3.8, 2.6, 2.8, P['piedra'], semilla=1)            # las ancas
    bloque(out, vr.T(0, H + 3.9, -0.2) @ vr.Rx(-35 * D), 3.5, 2.8, 2.7, P['piedra'], semilla=3)            # el vientre
    bloque(out, vr.T(0, H + 5.4, 1.5) @ vr.Rx(-25 * D), 4.8, 3.3, 3.3, P['piedra'], semilla=5)             # el pecho
    cubo(out, vr.T(0, H + 5.4, 1.5) @ vr.Rx(-25 * D), -1.4, -1.9, 1.5, 2.8, 2.6, 0.4, P['piedra_lisa'], semilla=7)  # el esternon
    for s in (1, -1):
        # la pata de atras: el muslo hacia delante, la pierna hacia atras y el pie en la piedra
        cad, rod, tob = (np.array((s * 1.8, H + 2.6, -1.6)), np.array((s * 2.6, H + 2.0, 0.7)),
                         np.array((s * 2.4, H + 0.8, -1.3)))
        viga(out, cad, rod, 2.0, 2.1, P['piedra'], extra=0.4, semilla=10)
        bola(out, vr.T(*rod), 1.0, P['piedra'], semilla=11)
        viga(out, rod, tob, 1.3, 1.3, P['piedra'], extra=0.3, semilla=12)
        pie = np.array((s * 2.45, H + 0.3, -0.4))
        viga(out, tob, pie, 1.2, 0.8, P['piedra_lisa'], extra=0.3, semilla=13)
        _mano(out, pie, (0.0, -0.1, 1.0), (0.0, -1.0, 0.25), P, s, ancho=0.9, n=3, largo=0.9, semilla=14)
        # el brazo: del hombro al codo, que sale hacia fuera y atras, y la mano en el borde
        hom, codo, mun = (np.array((s * 2.4, H + 6.2, 1.9)), np.array((s * 3.4, H + 4.0, 2.4)),
                          np.array((s * 2.9, H + 1.3, 3.8)))
        viga(out, hom, codo, 1.6, 1.6, P['piedra'], extra=0.35, semilla=20)
        bola(out, vr.T(*codo), 0.85, P['piedra'], semilla=21)
        pua(out, em.marco(codo, (s * 0.4, 0.2, -1.0)) @ vr.Rx(90 * D), 0.25, 1.1, P['cuerno'], semilla=22)    # la pua del codo
        viga(out, codo, mun, 1.25, 1.25, P['piedra'], extra=0.3, semilla=23)
        _mano(out, mun + np.array((0.0, -0.75, 0.35)), (0.0, -0.15, 1.0), (0.0, -1.0, 0.15), P, s, ancho=1.0, n=4, largo=1.2,
              semilla=24)
    # las puas del lomo, del cuello a la cola
    for j, (y, z, l) in enumerate(((7.3, 0.9, 1.3), (6.7, -0.2, 1.5), (5.7, -1.2, 1.4), (4.5, -2.1, 1.2), (3.4, -2.9, 1.0))):
        pua(out, vr.T(0, H + y, z) @ vr.Rx(-40 * D), 0.3, l * (1.5 if k == 'B' else 1.0), P['cuerno'], semilla=30 + j)
    # la cola: baja por detras y se enrosca alrededor de la columna, pegada a ella, hasta una pala
    # delante, a un lado
    ctrl = [(0.0, H + 2.0, -2.9)]
    for ang, y, rr in ((285, H + 0.2, 4.4), (320, H - 1.4, 4.5), (355, H - 2.9, 3.9), (25, H - 4.1, 3.4), (55, H - 5.0, 3.2),
                       (85, H - 5.6, 3.2)):
        a = math.radians(ang)
        ctrl.append((rr * math.cos(a), y, rr * math.sin(a) - 0.4))
    pts = _tambores(out, ctrl, (1.05, 0.42), P, semilla=40)
    d = pts[-1] - pts[-2]
    d = d / np.linalg.norm(d)
    Mp = em.marco(pts[-1], d, up=(1.0, 0.0, 0.0))
    for j, (w, l) in enumerate(((1.6, 0.9), (1.1, 0.7), (0.6, 0.6))):                                      # la pala
        z0 = sum(ll for _, ll in ((1.6, 0.9), (1.1, 0.7), (0.6, 0.6))[:j])
        cubo(out, Mp, -0.12, -w / 2, z0, 0.24, w, l, P['cuerno'], semilla=70 + j)


# ----------------------------------------------------------------------
#  La cabeza (se hace sin escala; almenara() la pone agrandada)
# ----------------------------------------------------------------------
def cabeza(out, Mh, V, P):
    """La cabeza de la gargola, grande y ancha: el craneo mas ancho que alto, el ceno fruncido de
    dos cejas de piedra, los ojos redondos encendidos debajo, los carrillos, el morro corto y
    ancho con la nariz chata y la boca abierta de par en par, en grito, con los dientes
    dibujados en hojas y dos colmillos grandes. De la boca sale la canaleta de piedra, como en
    las gargolas de verdad, por la que se derrama la luz de la almenara. Orejas de murcielago,
    dos cuernos que van hacia atras y suben, y una cresta. Devuelve la punta de la canaleta."""
    # el rostro, de frente y alto: la frente arriba, los ojos, la nariz chata y, debajo, la boca
    cubo(out, Mh, -2.2, -0.2, -2.6, 4.4, 3.1, 3.2, P['piedra'], semilla=1)                               # el craneo
    cubo(out, Mh, -1.8, 2.9, -2.2, 3.6, 0.5, 2.4, P['piedra_lisa'], semilla=2)                           # la coronilla
    for s in (1, -1):
        cubo(out, Mh, 1.6 if s > 0 else -2.8, -0.9, -1.6, 1.2, 2.0, 2.4, P['piedra'], semilla=3)         # los carrillos
        Mc = Mh @ vr.T(s * 0.95, 2.6, 0.75) @ vr.Rz(-s * 16 * D) @ vr.Rx(12 * D)
        cubo(out, Mc, -1.05, -0.3, -0.5, 2.1, 0.6, 1.0, P['piedra'], semilla=4)                          # el ceno
        cubo(out, Mh @ vr.T(s * 0.95, 1.95, 0.62), -0.45, -0.35, 0, 0.9, 0.7, 0.12, None, caras={'frente': P['ojo']},
             semilla=5)                                                                                   # el ojo
        pua(out, em.marco(punto(Mh, (s * 2.7, 0.2, -0.8)), _dir(Mh, (s * 1.0, -0.2, -0.8))) @ vr.Rx(90 * D), 0.24, 1.1,
            P['cuerno'], semilla=6)                                                                       # la pua de la quijada
    cubo(out, Mh, -0.8, 0.8, 0.5, 1.6, 0.8, 0.9, P['piedra_lisa'], semilla=7)                           # la nariz chata
    for s in (1, -1):
        cubo(out, Mh, s * 0.42 - 0.17, 0.95, 1.38, 0.34, 0.3, 0.06, P['garra'], semilla=8)
    # el labio de arriba, corto y ancho, con los dientes colgando de su borde
    Mu = Mh @ vr.T(0, -0.15, 0.5) @ vr.Rx(-4 * D)
    W, R, L = 3.4, 1.0, 1.6
    prisma5(out, Mu, W, 0.0, 0.9, R, L, {'arriba': P['piedra'], 'proa': P['piedra'], 'lados': P['piedra'], 'atras': P['piedra'],
                                         'abajo': P['boca']}, semilla=9)
    _hilera(out, Mu, W, R, L, 0.02, -1.0, P['colmillos'], semilla=10)
    for s in (1, -1):                                                                                    # los colmillos grandes
        a = punto(Mu, (s * 1.3, 0.02, R - 0.2))
        b = punto(Mu, (s * 1.0, 0.02, R + 0.1))
        abajo = _dir(Mu, (0.0, -1.8, 0.1))
        lamina(out, (a + abajo, b + abajo, b, a), P['colmillos'], float(np.linalg.norm(b - a)), 1.8, 12 + (s > 0))
    # la de abajo, en grito
    Ml = Mh @ vr.T(0, -0.5, 0.2) @ vr.Rx(48 * D)
    prisma5(out, Ml, 3.2, -1.0, 0.0, 2.0, 2.7, {'arriba': P['boca'], 'abajo': P['piedra'], 'lados': P['piedra'],
                                                 'proa': P['piedra'], 'atras': P['piedra']}, semilla=20)
    _hilera(out, Ml, 3.2, 2.0, 2.7, 0.0, 0.7, P['dientes'], semilla=22, mete=0.22)
    Mv = em.marco(punto(Mh, (0.0, -0.3, 0.2)), _dir(Mh, (0.0, 0.05, 1.0)))
    cubo(out, Mv, -1.3, -1.3, 0, 2.6, 2.6, 0.05, None, caras={'frente': P['nucleo']}, semilla=24)      # el fuego del fondo
    # la canaleta: un caz de piedra que sale de la boca, hacia delante y un poco abajo, con la luz dentro
    Mk = Mh @ vr.T(0, -0.7, 0.0) @ vr.Rx(20 * D)
    largo = 4.4
    cubo(out, Mk, -0.62, -0.3, 0, 1.24, 0.32, largo, P['piedra'], semilla=25)
    for s in (1, -1):
        cubo(out, Mk, (0.44 if s > 0 else -0.62), -0.3, 0, 0.18, 0.62, largo, P['piedra_lisa'], semilla=26)
    cubo(out, Mk, -0.44, 0.02, 0.05, 0.88, 0.04, largo - 0.1, None, caras={'arriba': P['chorro']}, semilla=27)
    cubo(out, Mk, -0.7, -0.38, largo - 0.35, 1.4, 0.75, 0.4, P['piedra_lisa'], semilla=28)                  # el labio de la punta
    for s in (1, -1):
        # la oreja de murcielago, plana, hacia fuera y atras
        Me = em.marco(punto(Mh, (s * 2.3, 2.2, -1.2)), _dir(Mh, (s * 1.0, 0.35, -0.4))) @ vr.Rx(90 * D)
        cubo(out, Me, -0.75, 0, -0.09, 1.5, 2.0, 0.18, P['piedra_lisa'], semilla=29)
        cubo(out, Me, -0.45, 2.0, -0.08, 0.9, 0.9, 0.16, P['piedra_lisa'], semilla=30)
        cubo(out, Me, -0.18, 2.9, -0.07, 0.36, 0.7, 0.14, P['piedra_lisa'], semilla=31)
        # el cuerno: sale de la coronilla, va hacia atras y sube
        p = punto(Mh, (s * 1.35, 3.0, -1.1))
        for j in range(8):
            a = 0.15 + j * 0.2
            d = _dir(Mh, (s * 0.32, math.sin(a), -math.cos(a)))
            q = p + d * 0.78
            g = 0.9 - j * 0.085
            viga(out, p, q, g, g, P['cuerno'], extra=0.12, semilla=32 + j)
            p = q
    for j, z in enumerate((-0.4, -1.3, -2.2)):                                                            # la cresta
        pua(out, em.marco(punto(Mh, (0.0, 3.35, z)), _dir(Mh, (0.0, 1.0, -0.6))) @ vr.Rx(90 * D), 0.22, 0.9 - 0.15 * j,
            P['cuerno'], semilla=42 + j)
    return punto(Mk, (0.0, 0.0, largo))


def chorro(out, tip, P, alto_suelo=0.25, semilla=0):
    """El chorro de luz que cae de la canaleta hasta el suelo, con una curva hacia delante, hecho de
    dos hojas cruzadas (se ve desde cualquier lado), y el charco donde cae."""
    tip = np.asarray(tip, float)
    caida = tip[1] - alto_suelo
    pts = [tip + np.array((0.0, -caida * t, 1.4 * (1 - (1 - t) ** 2))) for t in np.linspace(0, 1, 7)]
    for j in range(len(pts) - 1):
        a, b = pts[j], pts[j + 1]
        w = 0.42 + 0.22 * j / (len(pts) - 1)
        for lado in (np.array((1.0, 0.0, 0.0)), np.array((0.0, 0.0, 1.0))):
            lamina(out, (b - lado * w, b + lado * w, a + lado * w, a - lado * w), P['chorro'], 2 * w, float(np.linalg.norm(b - a)),
                   semilla + j)
    fin = pts[-1]
    cubo(out, vr.T(fin[0], 0.02, fin[2]), -1.6, 0, -1.6, 3.2, 0.04, 3.2, None, caras={'arriba': P['charco']}, semilla=semilla + 9)
    return fin


# ----------------------------------------------------------------------
#  Lo de cada tipo
# ----------------------------------------------------------------------
def alas(out, P):
    """A: las alas de piedra, abiertas hacia arriba y atras: el brazo (hombro, codo y muneca, con
    la garra del pulgar) y cuatro dedos en abanico, con la membrana oscura en bandas entre ellos."""
    H = ALTO
    for s in (1, -1):
        S = np.array((s * 2.0, H + 6.6, 0.6))
        E = S + np.array((s * 2.4, 3.4, -2.2))
        W = E + np.array((s * 1.4, 3.6, 0.8))
        F = [W + np.array((s * 1.0, 5.4, -1.0)), W + np.array((s * 4.2, 3.6, -1.8)), W + np.array((s * 5.6, 0.4, -2.4)),
             W + np.array((s * 4.6, -3.0, -2.6))]
        viga(out, S, E, 1.4, 1.4, P['piedra'], extra=0.3, semilla=80)
        viga(out, E, W, 1.1, 1.1, P['piedra'], extra=0.28, semilla=81)
        bola(out, vr.T(*E), 0.8, P['piedra'], semilla=82)
        bola(out, vr.T(*W), 0.7, P['piedra'], semilla=83)
        _garra(out, W + np.array((0.0, 0.4, 0.3)), (s * 0.2, 0.6, 1.0), 1.0, 0.3, P, semilla=84, curva=(0.0, -0.6, 1.0))
        for j, t in enumerate(F):
            g = 0.55 - 0.04 * j
            viga(out, W, t, g, g, P['piedra'], extra=0.1, semilla=85 + j)
        for j in range(3):
            _pano(out, W, F[j], F[j + 1], P['membrana'], semilla=90 + j + 10 * (s > 0))
        _pano(out, E, W, F[3], P['membrana'], semilla=94 + 10 * (s > 0))


def brazos_altos(out, P):
    """B: un segundo par de brazos que sale de lo alto del lomo y se alza, con las garras
    abiertas; y la cresta: puas largas con una vela de membrana entre ellas."""
    H = ALTO
    for s in (1, -1):
        hom = np.array((s * 2.3, H + 6.9, 0.4))
        bloque(out, vr.T(*hom), 2.0, 1.8, 2.0, P['piedra'], semilla=99)                       # el hombro de arriba
        codo = hom + np.array((s * 3.0, 2.2, 0.3))
        mun = codo + np.array((s * 0.3, 3.0, 1.8))
        viga(out, hom, codo, 1.75, 1.75, P['piedra'], extra=0.35, semilla=100)
        bola(out, vr.T(*codo), 1.0, P['piedra'], semilla=101)
        pua(out, em.marco(codo, (s * 0.6, -0.4, -1.0)) @ vr.Rx(90 * D), 0.3, 1.4, P['cuerno'], semilla=102)
        viga(out, codo, mun, 1.45, 1.45, P['piedra'], extra=0.3, semilla=103)
        frente = np.array((s * 0.25, 0.8, 0.6))
        _mano(out, mun, frente, (s * 0.3, -0.2, 1.0), P, s, ancho=1.5, n=4, largo=2.1, semilla=104)
    # la cresta: cinco puas largas por el lomo, unidas por una vela
    H = ALTO
    raiz = [np.array((0.0, H + y, z)) for y, z in ((7.6, 1.0), (7.0, -0.2), (6.0, -1.2), (4.8, -2.1), (3.7, -2.9))]
    puntas = [r + np.array((0.0, 3.2 - 0.4 * j, -1.6 - 0.2 * j)) for j, r in enumerate(raiz)]
    for j, (a, b) in enumerate(zip(raiz, puntas)):
        viga(out, a, b, 0.32, 0.32, P['cuerno'], extra=0.1, semilla=110 + j)
        pua(out, em.marco(b, b - a) @ vr.Rx(90 * D), 0.16, 0.7, P['cuerno'], semilla=115 + j)
    for j in range(len(raiz) - 1):
        lamina(out, (raiz[j], raiz[j + 1], puntas[j + 1], puntas[j]), P['membrana_lisa'],
               float(np.linalg.norm(puntas[j + 1] - puntas[j])), float(np.linalg.norm(puntas[j] - raiz[j])), 120 + j)


def manto(out, P):
    """C: las alas cerradas por delante como una capucha. De cada hombro sube el hueso del ala, pasa
    por encima de la cabeza y baja delante, hasta la garra del pulgar; de el bajan cuatro dedos
    hasta el capitel, y entre ellos cuelga la membrana en pliegues, con el borde deshecho en
    jirones. Delante queda abierto: asoman la boca, la canaleta, el chorro y los brazos, y los
    cuernos atraviesan la capucha."""
    H = ALTO
    lados = []
    for s in (1, -1):
        arco = [np.array((s * 2.1, H + 6.4, 0.2)), np.array((s * 3.2, H + 9.9, 1.0)), np.array((s * 2.3, H + 12.6, 3.6)),
                np.array((s * 1.6, H + 12.3, 6.8)), np.array((s * 2.1, H + 10.6, 8.6))]
        for j in range(len(arco) - 1):
            g = 1.25 - 0.15 * j
            viga(out, arco[j], arco[j + 1], g, g, P['piedra'], extra=0.25, semilla=130 + j)
        bola(out, vr.T(*arco[1]), 0.8, P['piedra'], semilla=135)
        _garra(out, arco[-1], (s * 0.2, -0.8, 0.6), 1.3, 0.36, P, semilla=136, curva=(0.0, -1.0, -0.2))
        # los dedos: bajan del arco hasta abajo, abriendose; son los pliegues del manto
        dedos = []
        for j, (i, f, sale) in enumerate(((1, 0.5, 4.6), (2, 0.4, 4.4), (3, 0.0, 4.0), (3, 0.9, 3.6))):
            a = arco[i] + (arco[i + 1] - arco[i]) * f
            pie = np.array((s * sale, H + 0.8 + 0.5 * j, a[2] - 0.6 + 0.4 * j))
            viga(out, a, pie, 0.5, 0.5, P['piedra'], extra=0.1, semilla=137 + j)
            dedos.append((a, pie))
        lados.append((arco, dedos))
        # la membrana, en pliegues entre los dedos (el borde de abajo, en jirones)
        for j in range(len(dedos) - 1):
            (a, pa), (b, pb) = dedos[j], dedos[j + 1]
            lamina(out, (pa, pb, b, a) if s > 0 else (pb, pa, a, b), P['manto'], float(np.linalg.norm(b - a)),
                   float(np.linalg.norm(pa - a)), 140 + j + 10 * (s > 0))
        a0, p0 = dedos[0]                                                    # de lo alto del hombro al primer dedo
        atras = np.array((s * 3.0, H + 0.8, -0.8))
        lamina(out, (atras, p0, a0, arco[0]) if s > 0 else (p0, atras, arco[0], a0), P['manto'], float(np.linalg.norm(a0 - arco[0])),
               float(np.linalg.norm(p0 - a0)), 148 + (s > 0))
    # por detras y por arriba, el pano que une los dos lados
    (ad, dd), (ai, di) = lados[0], lados[1]
    for j in range(2):
        a, b = ai[j + 1], ad[j + 1]
        lamina(out, (np.array((a[0] * 1.35, H + 0.8, a[2] - 1.0)), np.array((b[0] * 1.35, H + 0.8, b[2] - 1.0)), b, a), P['manto'],
               float(np.linalg.norm(b - a)), float(a[1] - H - 0.8), 160 + j)
    for j in (1, 2):
        lamina(out, (ai[j], ad[j], ad[j + 1], ai[j + 1]), P['manto'], float(np.linalg.norm(ad[j + 1] - ai[j + 1])),
               float(np.linalg.norm(ai[j + 1] - ai[j])), 170 + j)


# ======================================================================
#  ALMENARA
# ======================================================================
ESC_CABEZA = 1.4


def almenara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    out = []
    capitel(out, P)
    cuerpo(out, V, P)
    # el cuello, corto y grueso, del pecho hacia delante; encima, la cabeza que asoma como un canalon
    H = ALTO
    viga(out, np.array((0.0, H + 6.6, 2.4)), np.array((0.0, H + 7.3, 4.3)), 2.0, 2.0, P['piedra'], extra=0.4, semilla=200)
    Hc = np.array((0.0, H + 7.5, 5.4))
    cab = []
    Mh0 = em.marco(np.zeros(3), (0.0, -0.3, 1.0))
    ppb = bm.PPB
    bm.PPB = ppb / ESC_CABEZA
    try:
        punta = cabeza(cab, Mh0, V, P)
    finally:
        bm.PPB = ppb
    Mpon = vr.T(*Hc) @ np.diag([ESC_CABEZA, ESC_CABEZA, ESC_CABEZA, 1.0])
    out += qm.transformar(cab, Mpon)
    Mh = Mpon @ Mh0
    fin = chorro(out, punto(Mpon, punta), P)                                    # la luz que se derrama hasta el suelo
    if tipo == 'A':
        alas(out, P)
    elif tipo == 'B':
        brazos_altos(out, P)
    else:
        manto(out, P)
    return out, {'cabeza': Mh, 'boca': punto(Mh, (0.0, -1.0, 2.0)), 'charco': fin}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

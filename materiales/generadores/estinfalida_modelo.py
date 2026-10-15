"""
La Estinfalida y sus formas (14-10-2026). Juan, al guardar a Cerbero y descartar la Tarasca («tenemos bosses
que se parecen»): «ahora create otro boss y sus tipos».

Un cuerpo que no se parece a ningun jefe de las fichas: un ave de presa. Es del mismo bestiario griego que la
Gorgona, el Minotauro y Cerbero: las aves del lago Estinfalo, las de Ares, que comian hombres y lanzaban sus
plumas de bronce como dardos (el sexto trabajo de Heracles). No es un aguila agrandada: las plumas de las
alas, la cola y la corona son hojas de bronce, y el pico es una boca con dientes. Con la receta de la guia
(materiales/fichas/COMO_HACEMOS_LOS_MONSTRUOS.md): la cabeza manda, grande y mirando a camara, con el pico
abierto que arde por dentro con un solo neon en escalones (los dientes dibujados en hojas a lo largo del
filo, dos colmillos bajo el gancho y el nucleo al fondo de la garganta) y los ojos encendidos bajo un ceno de
aguila que sobresale; la enmarcan la corona de plumas y la gola. El cuerpo es oscuro, de plumaje en U, con
las patas de escamas y las garras negras. Todo de cajas, con texturas limpias.

Las tres formas cambian la silueta:

    A  la Estinfalida       de pie, con las dos alas abiertas en alto como en un blason, la corona de plumas
                            en abanico y la cola abierta; rojo de Ares
    B  la Picada            cayendo en picado: el cuerpo de cabeza, las alas en V hacia atras, las garras
                            por delante y abiertas, la corona echada atras; verde de patina
    C  la Reina del Lago    erguida, con cuatro alas abiertas en aspa, la gran corona de plumas como un sol
                            y tres plumas de cola muy largas que arrastran; violeta
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _degradado, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.56
CABEZA = 1.8                                     # la cabeza manda: se hace sin escala y se agranda

DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')
GARRA = _r('08080a', '121214', '1c1c20', '28282e', '38383e')
VARIANTES = {
    'A': dict(
        clave='A', nombre='la Estinfalida', corto='estinfalida',
        plumaje=_r('0c0806', '160e0a', '22160e', '301f14', '422c1c'),
        pluma=_r('1e1008', '32200e', '4a3016', '6a4826', '9a7040'),
        pico=_r('2a1a0c', '4a2e14', '6e4a24', '967038', 'c09a58'),
        escama=_r('14100c', '221a14', '30261e', '42362a', '584a3a'),
        garra=GARRA, dientes=DIENTES, neon=('ffe6dc', 'ff3d2a', '6a0a04'),
    ),
    'B': dict(
        clave='B', nombre='la Picada', corto='picada',
        plumaje=_r('060c0a', '0c1612', '14221c', '1e3228', '2a4436'),
        pluma=_r('0c1814', '16281f', '223c30', '325a48', '4e8a70'),
        pico=_r('2a1a0c', '4a2e14', '6e4a24', '967038', 'c09a58'),
        escama=_r('0c1210', '161e1a', '222c26', '303c34', '424e46'),
        garra=GARRA, dientes=DIENTES, neon=('e4fff2', '3affa0', '045a32'),
    ),
    'C': dict(
        clave='C', nombre='la Reina del Lago', corto='reina',
        plumaje=_r('0a0810', '120e1a', '1c1628', '282036', '362c48'),
        pluma=_r('120e18', '1e1828', '2c243a', '40364f', '62587a'),
        pico=_r('2a200c', '4a3a16', '6e5a26', '967e3a', 'c0a85a'),
        escama=_r('100e16', '1a1622', '26202e', '342c3e', '463c52'),
        garra=GARRA, dientes=DIENTES, neon=('f2e6ff', 'b45aff', '3a0a6a'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'est%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def plumaje(tw, th, cara, s):
        """El plumaje del cuerpo: plumas en U al tresbolillo, con el canto claro de cada una."""
        ys, xs = np.mgrid[0:th, 0:tw]
        fila = ys // 4
        x = (xs + (fila % 2) * 2) % 5
        idx = np.full((th, tw), 2)
        idx = np.where((ys % 4) == 3, 1, idx)
        idx = np.where(((ys % 4) == 0) & (x == 2), 3, idx)
        idx = np.where(x == 4, np.minimum(idx, 1), idx)
        return _imagen(_bisel(idx, 1, 1), V['plumaje']), None
    reg('plumaje', plumaje)

    def pluma(tw, th, cara, s):
        """Una pluma de bronce: el raquis claro por el medio a lo largo, las placas de traves con su junta
        oscura y el canto oscuro; en los cantos finos, lisa."""
        if min(tw, th) < 3:
            return _imagen(np.full((th, tw), 2), V['pluma']), None
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        idx = np.full((n_a, n_l), 2)
        idx[:, np.arange(n_l) % 4 == 0] = 1
        idx[0, :] = 1
        idx[-1, :] = 3
        idx[n_a // 2, :] = 4
        if n_a >= 6:
            idx[n_a // 2 - 1, :] = 3
        if not largo_x:
            idx = idx.T
        return _imagen(idx, V['pluma']), None
    reg('pluma', pluma)
    reg('pico', jm.liso(V['pico'], 2, 1, 1))
    reg('pico_oscuro', jm.liso(V['pico'], 1, 1, 0))
    reg('garra', jm.liso(V['garra'], 2, 2, 1))

    def escama(tw, th, cara, s):
        """Las escamas de las patas: placas de traves con la junta oscura y el canto claro."""
        largo_x = tw >= th
        n = tw if largo_x else th
        a = np.arange(n)
        fila = np.where((a % 4) == 0, 1, np.where((a % 4) == 1, 3, 2))
        idx = np.tile(fila, ((th if largo_x else tw), 1))
        if not largo_x:
            idx = idx.T
        return _imagen(idx, V['escama']), None
    reg('escama', escama)

    def fauces(tw, th, cara, s):
        """El paladar: escalones de luz (blanco al fondo, el neon, la sombra) con sus estrias."""
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
                                np.where((dd < 0.76)[..., None], np.array(c_m), np.array(qm._mezcla(c_m, c_n, 0.65)))))
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
        dentro = r < 1.0
        col = np.where((r < 0.45)[..., None], np.array(c_n),
                       np.where((r < 0.75)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m)))
        col = np.where(((r > 0.9) & dentro)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = np.where(dentro, 255, 0)
        return t, _emis(t, dentro & (r < 0.9), 240)
    reg('nucleo', nucleo)

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
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, V['dientes'], True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, V['dientes'], False))

    def colmillo(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 1
        return _imagen(idx, V['dientes']), None
    reg('colmillo', colmillo)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def _u(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    """Una fila de dientes en hojas a lo largo de una linea quebrada en el plano del pico."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado, h = float(np.linalg.norm(B - A)), float(np.linalg.norm(A2 - A))
        if alto < 0:
            lamina(out, (A2, B2, B, A), pintor, lado, h, semilla + j)
        else:
            lamina(out, (A, B, B2, A2), pintor, lado, h, semilla + j)


def pluma(out, P, base, d, n, largo, ancho, pintor=None, semilla=0):
    """Una pluma de bronce: una hoja plana (de cara a n) que sale de base hacia d y acaba en punta, en tres
    escalones."""
    pin = pintor or P['pluma']
    M = em.marco(np.asarray(base, float), _u(d), up=_u(n))
    g = 0.24
    caja(out, M, -ancho / 2, ancho / 2, -g, g, -0.3, largo * 0.74, pin, semilla=semilla)
    caja(out, M, -ancho * 0.34, ancho * 0.34, -g * 0.9, g * 0.9, largo * 0.72, largo * 0.9, pin, semilla=semilla + 1)
    caja(out, M, -ancho * 0.14, ancho * 0.14, -g * 0.8, g * 0.8, largo * 0.88, largo, pin, semilla=semilla + 2)


def cabeza(out, Mh, P, abre=34.0):
    """La cabeza de ave de presa, con el pico hacia +z: el craneo con las mejillas anchas, el ceno de aguila que
    sobresale y los ojos encendidos bajo el; la cera; el pico ganchudo en escalones, abierto (el paladar
    encendido, los dientes en hojas a lo largo del filo, dos colmillos bajo el gancho, el suelo de la boca
    encendido y el nucleo al fondo); y las plumas de la barbilla."""
    plu = P['plumaje']
    caja(out, Mh, -3.4, 3.4, 0.0, 5.2, -3.8, 1.8, plu, semilla=1)                                     # el craneo
    caja(out, Mh, -2.8, 2.8, 5.0, 5.9, -3.2, 0.8, plu, semilla=2)
    caja(out, Mh, -3.9, 3.9, 0.4, 3.4, -3.4, 0.6, plu, semilla=3)                                      # las mejillas
    for s in (1, -1):
        x0, x1 = sorted((s * 1.3, s * 3.3))
        caja(out, Mh, x0, x1, 3.25, 4.15, 1.75, 2.0, P['ojo'], semilla=4)                              # los ojos
        Mc = Mh @ vr.T(s * 2.3, 4.55, 1.5) @ vr.Rz(s * 17 * D)                                         # el ceno
        caja(out, Mc, -2.0, 2.0, -0.3, 0.75, -1.4, 1.5, P['pico_oscuro'], semilla=5)
    caja(out, Mh, -1.4, 1.4, 1.4, 3.3, 1.6, 3.0, P['escama'], semilla=6)                              # la cera
    bm.cubo(out, Mh, -2.2, 1.0, 2.9, 4.4, 2.1, 3.1, P['pico'], caras={'abajo': P['fauces']}, semilla=7)
    bm.cubo(out, Mh, -1.7, 0.9, 6.0, 3.4, 2.0, 2.0, P['pico'], caras={'abajo': P['fauces']}, semilla=8)
    caja(out, Mh, -1.2, 1.2, 0.2, 2.5, 8.0, 9.2, P['pico'], semilla=9)                                # el gancho, corto:
    caja(out, Mh, -0.7, 0.7, -0.6, 1.6, 9.0, 9.8, P['pico'], semilla=10)                              # no tapa la boca
    hilera(out, Mh, [(-2.0, 3.1), (-1.5, 8.0), (1.5, 8.0), (2.0, 3.1)], 0.95, -0.9, P['dientes_arriba'], semilla=12)
    for s in (1, -1):                                                                                 # los colmillos
        M = Mh @ vr.T(s * 1.2, 0.95, 7.4)
        caja(out, M, -0.4, 0.4, -1.8, 0.0, -0.36, 0.36, P['colmillo'], semilla=13)
        caja(out, M, -0.22, 0.22, -2.7, -1.7, -0.2, 0.2, P['colmillo'], semilla=14)
    caja(out, Mh, -1.7, 1.7, -1.6, 1.0, 3.0, 3.3, P['nucleo'], semilla=15)                            # el nucleo
    Mj = Mh @ vr.T(0, 0.9, 2.6) @ vr.Rx(abre * D)                                                     # el pico de abajo
    bm.cubo(out, Mj, -1.95, -1.2, 0.0, 3.9, 1.2, 5.6, P['pico'], caras={'arriba': P['boca']}, semilla=16)
    caja(out, Mj, -1.4, 1.4, -1.0, 0.1, 5.4, 6.7, P['pico'], semilla=17)
    hilera(out, Mj, [(-1.75, 0.6), (-1.3, 5.4), (1.3, 5.4), (1.75, 0.6)], 0.0, 0.8, P['dientes_abajo'], semilla=18)
    caja(out, Mj, -1.9, 1.9, -2.3, -1.1, 0.2, 3.4, plu, semilla=19)                                  # la barbilla
    return pt(Mh, (0.0, 0.4, 5.5))


def corona(out, P, Mh, forma, semilla=0):
    """La corona de plumas de bronce que enmarca la cabeza: en abanico hacia arriba (la Estinfalida), echada
    hacia atras (la Picada) o en un gran sol alrededor de la cabeza (la Reina)."""
    R = Mh[:3, :3] / CABEZA
    if forma == 'atras':
        for j in range(7):
            f = (j - 3) / 3
            base = pt(Mh, (f * 2.2, 4.6 - abs(f) * 0.6, -2.4))
            d = R @ np.array((f * 0.35, 0.3, -1.0))
            pluma(out, P, base, d, R @ np.array((0.0, 1.0, 0.1)), (11.0 - 2.5 * abs(f)) * 1.2, 2.4, semilla=semilla + j % 3)
        return
    if forma == 'abanico':
        for s in (1, -1):
            for j in range(5):
                a = (20 + j * 17) * D
                u = np.array((s * math.sin(a), math.cos(a), 0.0))
                base = pt(Mh, (s * 2.4, 4.4, -0.6 - 0.5 * j))
                d = R @ (u + np.array((0.0, 0.0, -0.35)))
                pluma(out, P, base, d, R @ np.array((0.0, 0.0, 1.0)), (11.5 - 1.2 * j) * 1.2, 2.6, semilla=semilla + j % 3)
        return
    n, abre, largo = 13, 112, 10.5
    for j in range(n):
        a = (j - (n - 1) / 2) / ((n - 1) / 2) * abre * D
        u = np.array((math.sin(a), math.cos(a), 0.0))
        base = pt(Mh, (u[0] * 2.4, 2.9 + u[1] * 2.6, -2.6))
        d = R @ (u + np.array((0.0, 0.0, -0.45)))
        L = largo * (1.0 - 0.28 * abs(a) / (abre * D)) * (1.15 if j % 2 == 0 else 0.92)
        pluma(out, P, base, d, R @ np.array((0.0, 0.0, 1.0)), L * 1.2, 2.6, semilla=semilla + j % 3)


def gola(out, P, centro, eje, r, n=12, largo=6.0, semilla=0):
    """La gola: un aro de plumas alrededor de la base del cuello, que salen hacia fuera y hacia atras."""
    M = em.marco(np.asarray(centro, float), _u(eje))
    for k in range(n):
        a = (k + 0.5) * TAU / n
        u = np.array((math.cos(a), math.sin(a), 0.0))
        base = pt(M, u * r * 0.85)
        d = M[:3, :3] @ (u * 0.8 + np.array((0.0, 0.0, -0.6)))
        nn = M[:3, :3] @ u
        pluma(out, P, base, d, nn, largo, 2.4, semilla=semilla + k % 3)


def ala(out, P, hombro, codo, muneca, punta, atras, lado_visto=(0.0, 0.4, 1.0), largo=1.0, semilla=0):
    """Un ala de plumas de bronce: los huesos (tubos de plumaje) del hombro al codo, a la muneca y a la
    punta; las terciarias en el brazo, las secundarias en el antebrazo y las primarias en la mano, que se
    abren en abanico desde atras hasta la punta; y una fila de coberteras por encima (del lado que se ve).
    Cada pluma va un poco por delante de la anterior, como las tejas."""
    hombro, codo, muneca, punta = (np.asarray(p, float) for p in (hombro, codo, muneca, punta))
    atras = _u(atras)
    jm.tubo(out, [hombro, codo, muneca, punta], [3.2, 2.5, 1.8, 1.0], [P['plumaje']] * 3, semilla=semilla)
    n = _u(np.cross(muneca - codo, atras))
    if n @ np.asarray(lado_visto, float) < 0:
        n = -n
    k = 0
    for j in range(3):                                                                              # terciarias
        t = (j + 0.5) / 3
        b = hombro + (codo - hombro) * (0.35 + 0.65 * t)
        pluma(out, P, b - n * (0.4 + 0.05 * k), atras, n, 8.5 * largo, 4.4, semilla=semilla + k % 3)
        k += 1
    dm = _u(muneca - codo)
    for j in range(6):                                                                              # secundarias
        t = (j + 0.5) / 6
        b = codo + (muneca - codo) * t
        d = atras + dm * 0.15 * t
        pluma(out, P, b - n * (0.4 + 0.06 * k), d, n, 12.0 * largo * (0.94 + 0.06 * t), 4.6, semilla=semilla + k % 3)
        k += 1
    dp = _u(punta - muneca)
    for j in range(7):                                                                              # primarias
        t = j / 6
        b = muneca + (punta - muneca) * (0.15 + 0.85 * t)
        d = _u(atras * (1.0 - t) + dp * t * 1.4)
        pluma(out, P, b - n * (0.4 + 0.06 * k), d, n, (13.0 + 6.0 * t) * largo, 3.8, semilla=semilla + k % 3)
        k += 1
    for j in range(7):                                                                              # coberteras
        t = (j + 0.5) / 7
        b = codo + (punta - codo) * t * 0.85
        pluma(out, P, b + n * 0.35, atras + dm * 0.2, n, 6.5 * largo, 4.2, pintor=P['plumaje'], semilla=semilla + j % 3)


def cola(out, P, base, atras, n_vis, abre=50.0, largo=13.0, cintas=False, semilla=0):
    """La cola: un abanico de plumas de bronce y una fila de coberteras mas cortas encima; la Reina lleva
    ademas tres plumas muy largas que arrastran."""
    atras = _u(atras)
    lado = _u(np.cross(n_vis, atras))
    for j in range(9):
        a = ((j - 4) / 4) * abre * D
        d = atras * math.cos(a) + lado * math.sin(a)
        pluma(out, P, base + n_vis * (0.05 * j), d, n_vis, largo * (1.0 - 0.15 * abs(j - 4) / 4), 3.0, semilla=semilla + j % 3)
    for j in range(7):
        a = ((j - 3) / 3) * abre * 0.7 * D
        d = atras * math.cos(a) + lado * math.sin(a)
        pluma(out, P, base + n_vis * 0.7, d, n_vis, largo * 0.55, 2.8, semilla=semilla + j % 3)
    if cintas:
        for j, a in enumerate((-14, 0, 14)):
            d = atras * math.cos(a * D) + lado * math.sin(a * D) + np.array((0.0, -0.32, 0.0))
            pluma(out, P, base + n_vis * 0.4, d, n_vis, 30.0 if j == 1 else 25.0, 2.6, semilla=semilla + 4)


def pata(out, P, cadera, rodilla, tobillo, adelante, abiertas=False, semilla=0):
    """La pata: el muslo de plumas con sus calzas (plumas que caen), el tarso de escamas, y el pie de cuatro
    dedos (tres delante y uno detras) con las garras negras y curvas. Abiertas, los dedos se separan para
    agarrar."""
    cadera, rodilla, tobillo = (np.asarray(p, float) for p in (cadera, rodilla, tobillo))
    jm.tubo(out, [cadera, rodilla], [3.6, 2.9], [P['plumaje']], semilla=semilla)
    for k in range(5):                                                                              # las calzas
        a = (k - 2) * 0.55
        u = _u(np.array((math.sin(a), 0.0, math.cos(a))))
        pluma(out, P, rodilla + u * 1.6 + np.array((0.0, 1.0, 0.0)), np.array((0.0, -1.0, 0.0)) + u * 0.35, u, 4.6, 2.2,
              pintor=P['pluma'], semilla=semilla + k % 3)
    M = em.marco(rodilla, tobillo - rodilla)
    L = float(np.linalg.norm(tobillo - rodilla))
    caja(out, M, -1.6, 1.6, -1.6, 1.6, -0.4, L + 0.4, P['escama'], semilla=semilla + 1)               # el tarso
    Mp = em.marco(tobillo, _u(adelante), up=(0.0, 1.0, 0.0))
    caja(out, Mp, -1.5, 1.5, -1.0, 1.0, -1.3, 1.3, P['escama'], semilla=semilla + 2)
    for ang in (-32, 0, 32, 180):
        baja = -30 if abiertas else 10
        Md = Mp @ vr.Ry(ang * D) @ vr.Rx(baja * D)
        L1, L2 = (3.6, 2.6) if ang != 180 else (2.4, 1.8)
        caja(out, Md, -0.62, 0.62, -0.62, 0.62, 0.6, L1, P['escama'], semilla=semilla + 3)
        M2 = Md @ vr.T(0, 0, L1) @ vr.Rx((25 if abiertas else 8) * D)
        caja(out, M2, -0.5, 0.5, -0.5, 0.5, -0.2, L2, P['escama'], semilla=semilla + 4)
        M3 = M2 @ vr.T(0, 0, L2) @ vr.Rx(38 * D)                                                     # la garra
        caja(out, M3, -0.4, 0.4, -0.4, 0.4, -0.2, 1.5, P['garra'], semilla=semilla + 5)
        caja(out, M3 @ vr.T(0, 0, 1.4) @ vr.Rx(40 * D), -0.25, 0.25, -0.25, 0.25, -0.1, 1.1, P['garra'], semilla=semilla + 6)


def tronco(out, P, Y, semilla=0):
    """El cuerpo de ave: un huevo de plumaje en U, con la pechera de plumas que caen en tres filas."""
    ctrl = [np.array(c, float) for c in ((0.0, Y - 0.6, -11.0), (0.0, Y, -4.0), (0.0, Y + 0.6, 2.0), (0.0, Y + 1.6, 6.5))]
    pts, rs, ts = jm.a_lo_largo(ctrl, 8, ((0.0, 3.8), (0.3, 6.0), (0.6, 6.8), (0.85, 6.6), (1.0, 5.0)))
    jm.tubo(out, pts, rs, [P['plumaje']] * (len(pts) - 1), semilla=semilla, achata=1.1)
    for fila, (y, z, n) in enumerate(((Y + 3.0, 6.6, 5), (Y + 0.4, 6.8, 5), (Y - 2.2, 6.0, 4))):     # la pechera
        for j in range(n):
            x = (j - (n - 1) / 2) * 2.0
            pluma(out, P, (x, y, z), (x * 0.05, -1.0, 0.25), (0.0, 0.2, 1.0), 4.4, 2.4, pintor=P['plumaje'],
                  semilla=semilla + 3 + j % 2)


# ======================================================================
#  LA ESTINFALIDA
# ======================================================================
def estinfalida(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    Y = 18.0
    cuerpo, resto = [], []
    try:
        tronco(cuerpo, P, Y, semilla=100)
        hombro = lambda s, dy=0.0, dz=0.0: np.array((s * 5.6, Y + 3.8 + dy, 1.0 + dz))
        for s in (1, -1):
            if tipo == 'A':                                                # abiertas en alto, como en un blason
                ala(cuerpo, P, hombro(s), (s * 12.0, Y + 9.0, -2.0), (s * 20.0, Y + 17.0, -1.0), (s * 27.0, Y + 25.0, -3.0),
                    (s * 0.35, -1.0, -0.25), semilla=120)
            elif tipo == 'B':                                              # en V, hacia atras
                ala(cuerpo, P, hombro(s), (s * 11.0, Y + 6.0, -3.0), (s * 16.0, Y + 8.0, -9.0), (s * 19.0, Y + 9.0, -18.0),
                    (-s * 0.25, 0.1, -1.0), lado_visto=(0.0, -0.3, 1.0), semilla=120)
            else:                                                          # cuatro alas en aspa
                ala(cuerpo, P, hombro(s, 0.6, -1.0), (s * 10.0, Y + 11.0, -2.0), (s * 15.0, Y + 20.0, -1.0),
                    (s * 19.0, Y + 29.0, -3.0), (s * 0.5, -1.0, -0.2), largo=0.92, semilla=120)
                ala(cuerpo, P, hombro(s, -4.2, -2.6), (s * 11.0, Y - 4.0, -3.0), (s * 18.0, Y - 4.0, -2.0),
                    (s * 25.0, Y - 7.0, -4.0), (s * 0.15, -1.0, -0.3), largo=0.85, semilla=125)
        cola(cuerpo, P, np.array((0.0, Y - 0.4, -10.5)), (0.0, -0.15 if tipo != 'B' else 0.25, -1.0), _u((0.0, 1.0, 0.1)),
             abre=(46.0 if tipo != 'C' else 56.0), largo=13.0, cintas=(tipo == 'C'), semilla=140)
        # la pose del cuerpo
        giro = {'A': -18.0, 'B': 32.0, 'C': -30.0}[tipo]
        Mc = vr.T(0.0, Y, -2.0) @ vr.Rx(giro * D) @ vr.T(0.0, -Y, 2.0)
        out = qm.transformar(cuerpo, Mc)
        # el cuello y la cabeza, colocados en el mundo para que la cabeza mire a camara
        base = pt(Mc, (0.0, Y + 2.0, 5.0))
        punta, cabeceo = {'A': ((0.0, 7.5, 5.0), -4.0), 'B': ((0.0, 0.5, 7.5), 22.0), 'C': ((0.0, 8.5, 3.5), 4.0)}[tipo]
        fin = base + np.array(punta)
        medio = base + (fin - base) * 0.5 + np.array((0.0, 0.8, -1.4))
        pts, rs, ts = jm.a_lo_largo([base, medio, fin], 6, ((0.0, 4.8), (1.0, 3.6)))
        jm.tubo(resto, pts, rs, [P['plumaje']] * (len(pts) - 1), semilla=150)
        gola(resto, P, pts[1], pts[2] - pts[0], rs[1], n=12, largo=6.5, semilla=155)
        giro = 14.0 if tipo == 'B' else 22.0                               # la cabeza se vuelve hacia quien mira
        Mh = vr.T(*fin) @ vr.Ry(giro * D) @ vr.Rx(cabeceo * D) @ np.diag([CABEZA] * 3 + [1.0]) @ vr.T(0.0, -1.8, 3.4)
        bm.PPB = PPB / CABEZA
        boca = cabeza(resto, Mh, P, abre=46.0)
        bm.PPB = PPB
        corona(resto, P, Mh, {'A': 'abanico', 'B': 'atras', 'C': 'sol'}[tipo], semilla=160)
        # las patas: de pie, o por delante con las garras abiertas (la Picada)
        for s in (1, -1):
            cad = pt(Mc, (s * 3.4, Y - 3.6, -1.0))
            if tipo == 'B':
                rod = cad + np.array((s * 1.2, -4.0, 5.0))
                tob = rod + np.array((s * 0.8, -5.5, 5.0))
                pata(resto, P, cad, rod, tob, (s * 0.15, -0.5, 1.0), abiertas=True, semilla=170)
            else:
                rod = cad + np.array((s * 0.8, -5.0, 3.0))
                tob = np.array((cad[0] + s * 1.6, 1.4, cad[2] + 1.0))
                pata(resto, P, cad, rod, tob, (s * 0.2, 0.0, 1.0), semilla=170)
        out += resto
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

"""
El Blaze de vanilla dibujado con su paleta (la cabeza de 8 x 8 x 8 con su cara y los tres anillos de cuatro varas de
2 x 8 x 2), solo para ponerlo al lado de los redisenos en la foto de escala. Sale de la segunda vuelta de la mejora del
Blaze (15-10-2026).
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import lamina
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 1

VARIANTES = {
    'A': dict(clave='BLA', nombre='el Coronado', corto='coronado', escala=1.5),
    'B': dict(clave='BLB', nombre='el Cornudo', corto='cornudo', escala=1.6),
    'C': dict(clave='BLC', nombre='el Fundido', corto='fundido', escala=1.7),
}

# la paleta de la textura del Blaze, fila a fila de arriba abajo (los mismos colores que la de vanilla)
FILAS = [('fff847', 'ffff84', 'fff847'), ('ffff84', 'fff847', 'ffd528'), ('ffd528', 'fcb217', 'fff847'),
         ('fc9600', 'ffd528', 'd17800'), ('d17800', 'fc9600', 'ab7501'), ('ab7501', '8b3401', 'd17800'),
         ('8b3401', '6c3100', '5f0201'), ('5f0201', '6c3100', '5f0201')]
FILAS = [tuple(nm._hex(c) for c in f) for f in FILAS]
ARRIBA = [nm._hex(c) for c in ('fff847', 'ffff84', 'ffd528', 'fff847')]
ABAJO = [nm._hex(c) for c in ('5f0201', '6c3100', '5f0201', '8b3401')]
OJO_B, OJO_N = nm._hex('ffffff'), nm._hex('310e0b')
FUEGO = ('fffbd0', 'ffc22a', 'd85a04')


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _moteado(tw, th, s, filas):
    """El moteado de la textura del Blaze: cada fila con su color y algun pixel de los vecinos, siempre igual."""
    t = np.zeros((th, tw, 4), np.uint8)
    for y in range(th):
        fila = filas[min(len(filas) - 1, int(y / max(th, 1) * len(filas)))]
        for x in range(tw):
            k = (x * 7 + y * 13 + s * 5 + (x * y) % 3) % 5
            c = fila[0] if k < 3 else fila[1 if k == 3 else 2]
            t[y, x] = (*c, 255)
    return t


def _brillo(t, umbral=520, alfa=110):
    """El Blaze se ve siempre encendido: lo claro de la textura brilla un poco."""
    m = t[..., :3].astype(int).sum(axis=2) > umbral
    return _emis(t, m, alfa)


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    neo = [nm._hex(c) for c in FUEGO]
    grietas = V['corto'] == 'fundido'

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'bl%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def cabeza(tw, th, cara, s):
        """La cabeza del Blaze: arriba amarilla, abajo roja oscura y los lados en degradado; la cara con los dos ojos
        (un pixel blanco y uno oscuro cada uno) en la cuarta fila. En el Fundido, grietas de lava que bajan."""
        if cara == 'arriba':
            t = _moteado(tw, th, s, [tuple(ARRIBA)])
        elif cara == 'abajo':
            t = _moteado(tw, th, s, [tuple(ABAJO)])
        else:
            t = _moteado(tw, th, s, FILAS)
        m = np.zeros((th, tw), bool)
        if cara == 'frente' and tw >= 8 and th >= 8:
            y = 3 * th // 8
            for x, c in ((1, OJO_B), (2, OJO_N), (tw - 3, OJO_N), (tw - 2, OJO_B)):
                t[y, x] = (*c, 255)
        if grietas and cara != 'abajo':
            rng = random.Random(s + 3)
            for _ in range(2 if cara != 'frente' else 1):
                x = rng.randrange(1, tw - 1)
                for y in range(th - 1, th // 3, -1):
                    if cara == 'frente' and y == 3 * th // 8:
                        break
                    t[y, x] = (*neo[1], 255)
                    m[y, x] = True
                    x = min(tw - 2, max(1, x + rng.choice((-1, 0, 0, 1))))
        e = _brillo(t)
        e[m] = t[m]
        e[m, 3] = 255
        return t, e
    reg('cabeza', cabeza)

    def vara(tw, th, cara, s):
        """La vara del Blaze: por los lados, amarilla arriba, naranja en medio y parda abajo; la tapa de arriba amarilla
        y la de abajo oscura."""
        if cara == 'arriba':
            t = _moteado(tw, th, s, [tuple(ARRIBA)])
        elif cara == 'abajo':
            t = _moteado(tw, th, s, [tuple(ABAJO)])
        else:
            t = _moteado(tw, th, s, [FILAS[0], FILAS[2], FILAS[3], FILAS[4], FILAS[5], FILAS[6]])
        return t, _brillo(t)
    reg('vara', vara)

    def quijada(tw, th, cara, s):
        """La quijada del Cornudo: la parte de abajo de la textura (naranja oscura y roja); por dentro, el fuego."""
        if cara == 'arriba':
            t = np.zeros((th, tw, 4), np.uint8)
            t[...] = (*neo[1], 255)
            ys, xs = np.mgrid[0:th, 0:tw]
            t[(ys + xs) % 3 == 0] = (*neo[0], 255)
            return t, _emis(t, np.ones((th, tw), bool), 255)
        t = _moteado(tw, th, s, FILAS[4:])
        return t, _brillo(t)
    reg('quijada', quijada)

    def boca(tw, th, cara, s):
        """El fuego de dentro de la boca."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[1], 255)
        t[(ys + xs) % 3 == 0] = (*neo[0], 255)
        return t, None
    reg('boca', boca, pleno=True)

    def llama(tw, th, cara, s):
        """La llama, en hoja: dos o tres lenguas que suben, amarillas por dentro y naranjas por fuera."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = 1 - (ys + 0.5) / th
        u = (xs + 0.5) / tw
        alto = 0.4 + 0.6 * np.abs(np.cos(u * math.pi * 1.5 + s * 0.7)) ** 0.7
        dentro = f < alto
        img = np.zeros((th, tw, 4), np.uint8)
        img[dentro] = (*neo[1], 255)
        img[dentro & (f < alto * 0.5) & (abs(u - 0.5) < 0.3)] = (*neo[0], 255)
        img[dentro & (f > alto - 0.18)] = (*neo[2], 255)
        img[..., 3] = np.where(dentro, 255, 0)
        return img, None
    reg('llama', llama, pleno=True)

    def nucleo(tw, th, cara, s):
        """El nucleo del Fundido: la vara al rojo, con las vetas de fuego."""
        t = _moteado(tw, th, s + 9, [FILAS[3], FILAS[4], FILAS[5]])
        ys, xs = np.mgrid[0:th, 0:tw]
        m = ((xs + ys * 2 + s) % 5) == 0
        t[m] = (*neo[0], 255)
        e = _brillo(t, umbral=380, alfa=160)
        e[m] = t[m]
        e[m, 3] = 255
        return t, e
    reg('nucleo', nucleo)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def marco_y(p, d, frente=(0.0, 0.0, 1.0)):
    """Un marco en p con el eje y hacia d (para que la vara tenga el amarillo arriba en todas sus caras)."""
    y = _u(d)
    f = np.asarray(frente, float)
    if abs(f @ y) > 0.95:
        f = np.array((1.0, 0.0, 0.0))
    x = _u(np.cross(y, f))
    z = np.cross(x, y)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p
    return M


def vara(out, P, abajo, arriba, grueso=2.0, semilla=0):
    """Una vara del Blaze, de abajo arriba."""
    abajo, arriba = np.asarray(abajo, float), np.asarray(arriba, float)
    L = float(np.linalg.norm(arriba - abajo))
    M = marco_y(abajo, arriba - abajo)
    bm.cubo(out, M, -grueso / 2, 0.0, -grueso / 2, grueso, L, grueso, P['vara'], semilla=semilla)


def hoja(out, P4, pintor, ancho, alto, semilla=0):
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def llama(out, P, base, ancho, alto, giro, semilla=0):
    """Una llama en hoja (dos, cruzadas) que sube desde base."""
    base = np.asarray(base, float)
    for g in (giro, giro + math.pi / 2):
        l = np.array((math.cos(g), 0.0, math.sin(g))) * ancho / 2
        sube = np.array((0.0, alto, 0.0))
        hoja(out, (base - l, base + l, base + l + sube, base - l + sube), P['llama'], ancho, alto, semilla)


def cabeza(out, P, H):
    """La cabeza del Blaze, 8 x 8 x 8, centrada en (0, H, 0), mirando a +z."""
    bm.cubo(out, vr.T(0.0, H, 0.0), -4.0, -4.0, -4.0, 8.0, 8.0, 8.0, P['cabeza'], semilla=1)


def anillo(out, P, y_arriba, radio, n, largo, giro=0.0, abre=0.0, uve=0.0, grueso=2.0, semilla=0):
    """Un anillo de n varas de pie (como las del Blaze), que pueden abrirse hacia fuera por arriba ('abre') o ir en
    uves, una inclinada a cada lado ('uve')."""
    for i in range(n):
        g = giro + TAU * i / n
        c, s = math.cos(g), math.sin(g)
        fuera = np.array((c, 0.0, s))
        tang = np.array((-s, 0.0, c))
        d = _u(np.array((0.0, 1.0, 0.0)) + fuera * abre + tang * uve * (1 if i % 2 == 0 else -1))
        centro = np.array((c * radio, y_arriba - largo / 2, s * radio))
        vara(out, P, centro - d * largo / 2, centro + d * largo / 2, grueso=grueso, semilla=semilla + i % 3)


# ======================================================================
#  A · EL CORONADO
# ======================================================================
def coronado(out, P):
    """La corona de varas sobre la cabeza, con fuego en las puntas, y cuatro anillos de varas (18 en vez de 12)."""
    H = 30.0
    cabeza(out, P, H)
    for i in range(8):                                                   # la corona: 8 varas en el borde de arriba
        g = TAU * i / 8 + TAU / 16
        x, z = math.cos(g) * 4.6, math.sin(g) * 4.6
        alto = 6.0 if i % 2 == 0 else 4.4
        d = _u(np.array((math.cos(g) * 0.25, 1.0, math.sin(g) * 0.25)))
        b = np.array((x, H + 2.0, z))
        vara(out, P, b, b + d * alto, grueso=1.6, semilla=i)
        llama(out, P, b + d * alto, 2.4, 3.2 if i % 2 == 0 else 2.4, g, semilla=i)
    anillo(out, P, H + 3.0, 10.0, 6, 8.0, giro=0.0, abre=0.18, semilla=10)
    anillo(out, P, H - 4.0, 9.0, 6, 8.0, giro=0.5, semilla=13)
    anillo(out, P, H - 11.0, 7.0, 4, 8.0, giro=0.2, semilla=16)
    anillo(out, P, H - 18.0, 4.5, 2, 7.0, giro=1.0, semilla=19)
    for g in (0.0, 2.1, 4.2):                                            # el fuego de debajo
        llama(out, P, np.array((math.cos(g) * 1.5, H - 26.0, math.sin(g) * 1.5)), 3.0, 5.0, g, semilla=21)
    return np.array((0.0, H, 4.0))


# ======================================================================
#  B · EL CORNUDO
# ======================================================================
def cornudo(out, P):
    """Dos cuernos de vara que suben de la cabeza, la quijada que se abre debajo con el fuego dentro y dos colmillos de
    vara, y las varas en uves."""
    H = 30.0
    cabeza(out, P, H)
    bm.cubo(out, vr.T(0.0, H - 4.0, 0.0), -3.6, -0.6, -3.6, 7.2, 0.6, 7.2, P['boca'], semilla=1)    # el fuego de la boca
    Mj = vr.T(0.0, H - 4.6, -4.0) @ vr.Rx(0.42)                                                      # la quijada
    bm.cubo(out, Mj, -4.0, -3.0, 0.0, 8.0, 3.0, 8.0, P['quijada'], semilla=2)
    for s in (-1, 1):                                                                               # los colmillos
        b = np.array((s * 3.0, H - 4.0, 3.4))
        vara(out, P, b + np.array((0.0, -3.4, 0.4)), b, grueso=1.2, semilla=3)
        b = pt(Mj, (s * 3.0, 0.0, 7.4))
        vara(out, P, b, b + np.array((0.0, 2.6, 0.4)), grueso=1.2, semilla=4)
    for s in (-1, 1):                                                                               # los cuernos
        pts = [np.array((s * 3.0, H + 3.0, -0.5)), np.array((s * 6.0, H + 8.0, -1.0)), np.array((s * 8.0, H + 13.0, -2.0)),
               np.array((s * 7.6, H + 17.0, -3.4))]
        for j, g in enumerate((2.4, 2.0, 1.5)):
            vara(out, P, pts[j], pts[j + 1], grueso=g, semilla=5 + j)
    anillo(out, P, H + 2.0, 10.0, 6, 9.0, giro=0.0, uve=0.4, grueso=2.4, semilla=10)
    anillo(out, P, H - 6.0, 8.0, 6, 9.0, giro=0.5, uve=0.4, grueso=2.4, semilla=13)
    anillo(out, P, H - 15.0, 5.0, 4, 8.0, giro=0.2, uve=0.4, grueso=2.2, semilla=16)
    for g in (0.0, 2.1, 4.2):
        llama(out, P, np.array((math.cos(g) * 1.5, H - 24.0, math.sin(g) * 1.5)), 3.0, 5.0, g, semilla=21)
    return np.array((0.0, H, 4.0))


# ======================================================================
#  C · EL FUNDIDO
# ======================================================================
def fundido(out, P):
    """La cabeza agrietada con lava y una cresta de llamas, el nucleo de fuego debajo (el humo hecho brasa) y dos aros de
    varas cruzados que giran alrededor, ademas del anillo de abajo."""
    H = 30.0
    cabeza(out, P, H)
    for i, (x, z, h) in enumerate(((-2.5, 0.0, 5.0), (0.0, 1.0, 7.0), (2.5, 0.0, 5.0), (-1.2, -2.2, 6.0), (1.2, -2.2, 6.0))):
        llama(out, P, np.array((x, H + 4.0, z)), 3.2, h, i * 0.6, semilla=i)                       # la cresta de llamas
    for j, (y, r) in enumerate(((H - 7.0, 3.4), (H - 12.5, 2.8), (H - 17.0, 2.0))):                # el nucleo
        bm.cubo(out, vr.T(0.0, y, 0.0), -r, -2.6, -r, 2 * r, 5.2, 2 * r, P['nucleo'], semilla=j)
    for inclina in (0.45, -0.45):                                                                   # los aros cruzados
        R = vr.Rz(inclina) @ vr.Rx(0.25 if inclina > 0 else -0.25)
        n = 10
        for i in range(n):
            g0, g1 = TAU * (i + 0.12) / n, TAU * (i + 0.88) / n
            a = pt(vr.T(0.0, H - 9.0, 0.0) @ R, (math.cos(g0) * 11.0, 0.0, math.sin(g0) * 11.0))
            b = pt(vr.T(0.0, H - 9.0, 0.0) @ R, (math.cos(g1) * 11.0, 0.0, math.sin(g1) * 11.0))
            if a[1] > b[1]:
                a, b = b, a
            vara(out, P, a, b, grueso=2.0, semilla=10 + i % 3)
    anillo(out, P, H - 18.0, 5.0, 4, 8.0, giro=0.3, semilla=16)
    for g in (0.0, 2.1, 4.2):
        llama(out, P, np.array((math.cos(g) * 1.5, H - 27.0, math.sin(g) * 1.5)), 3.0, 6.0, g, semilla=21)
    return np.array((0.0, H, 4.0))


DISENOS = {'A': coronado, 'B': cornudo, 'C': fundido}


def blaze(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        cara = DISENOS[tipo](out, P)
    finally:
        bm.PPB = ppb
    k = V['escala'] / 16.0                                                # de pixeles del modelo a bloques, agrandado
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([k, k, k, 1.0]) @ vr.T(0.0, -y0 + 6.0, 0.0)               # flota sobre el suelo
    out = qm.transformar(out, E)
    nuc = pt(E, (0.0, 20.0, 0.0))
    return out, {'cabeza': pt(E, cara), 'nucleo': nuc, 'luces': [nuc]}


def vanilla_a_escala():
    """El Blaze de vanilla tal cual (para compararlo): la cabeza y sus tres anillos de cuatro varas."""
    P = pintores(dict(clave='BLV', corto='vanilla'))
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        H = 22.0
        cabeza(out, P, H)
        anillo(out, P, H + 2.0, 9.0, 4, 8.0, giro=0.0, semilla=1)
        anillo(out, P, H - 2.0, 7.0, 4, 8.0, giro=0.4, semilla=2)
        anillo(out, P, H - 11.0, 5.0, 4, 8.0, giro=0.8, semilla=3)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([1 / 16.0] * 3 + [1.0]) @ vr.T(0.0, -y0 + 6.0, 0.0)
    return qm.transformar(out, E), {}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

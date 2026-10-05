"""
Aeralis, la Reina del Vendaval (el remake de octubre de 2026), para el juego:
la malla en piezas animables, su atlas de textura por fases y el codigo Java
que la construye. Es la UNICA fuente de la geometria. De aqui salen:
  - src/client/.../AeralisMalla.java            piezas, cajas y texOffs
  - textures/entity/aeralis/aeralis_fN.png     el atlas de cada fase
  - textures/entity/aeralis/aeralis_brillo_fN.png  lo que brilla
  - textures/entity/aeralis/aeralis_brillo_libre.png
y vendaval_juego_anim.py importa este modulo para animar y sacar los puntos
que usa el servidor (nucleo, ojos, punta de las alas).

La de antes del remake se guarda en vendaval_juego_v1.py (para la ficha).

Lo que trae el remake:
  - Alas mucho mas grandes (unos 35 bloques de envergadura en vez de 22; vuela
    4,5 bloques mas alta, con el torax a unos 15, para que las colas no rocen
    el suelo) y mas solidas: la tormenta oscura junto al cuerpo que se aclara
    hacia fuera, nubes que giran en espiral hacia los ocelos, el borde entero
    encendido, festones en el margen y, desde la fase II, jirones de viento.
  - La costa de cada ala es una vara de quitina de verdad (cajas).
  - Un halo de viento detras del torax, de 14 bloques, que gira.
  - Melena de nubes alrededor del cuello, con mechones abiertos.
  - Cabeza mayor, con una corona de siete puas de punta encendida, colmillos
    mas largos y antenas de pluma que barren hacia atras como cuernos.
  - Patas de delante de presa, con cuchilla, como una mantis.
  - El ojo de la tormenta del pecho, mayor y con un marco de puas.
  - Abdomen con juntas que brillan y cuatro cintas de viento.

Unidades: pixeles de modelo, Y hacia abajo, el frente mira a -Z, los pies de la
entidad en y=24. El renderer NO escala: un pixel de modelo es 1/16 de bloque.
La textura va a MEDIA resolucion: el atlas se declara de 1024 de ancho y el PNG
mide 512. Las piezas planas (alas, halo, cintas, nucleo) son cajas de grosor
cero con una imagen: la cara de delante la lleva tal cual y la de detras en
espejo, para que desde atras se vea el mismo dibujo traslucido.
"""
import math, random
import numpy as np
from PIL import Image
import nerea_modelo as nm
import viento_modelo as vm

DENSIDAD = 2
ANCHO_ATLAS = 1024
ESCALA = 1.0

TAM_SUP = (320, 210)
TAM_INF = (216, 236)
TAM_HALO = (224, 224)
TAM_CINTA = (16, 104)
TAM_CINTA_C = (14, 78)
TAM_NUCLEO = (40, 40)
ALTURA_TORAX = -100

_hex = nm._hex

# ----------------------------------------------------------------------
#  Paletas: las de vm.FASES y lo que el remake necesita encima
# ----------------------------------------------------------------------
EXTRA = {
    1: dict(tormenta=(40, 58, 92), nube=_hex('f4f8fc'), borde=_hex('9fe8ff'), halo=(196, 236, 255)),
    2: dict(tormenta=(34, 38, 96), nube=_hex('eceffa'), borde=_hex('a9b2ff'), halo=(182, 190, 255)),
    3: dict(tormenta=(36, 24, 86), nube=_hex('e2def4'), borde=_hex('cfa6ff'), halo=(214, 180, 255)),
    4: dict(tormenta=(30, 12, 50), nube=_hex('cfc8e6'), borde=_hex('ff7fe6'), halo=(255, 150, 236)),
}


def paleta(fase):
    """La paleta de una fase (1-4) o de la liberacion ('libre': la tormenta se
    despeja, la de la fase I, y lo que brilla pasa a oro)."""
    if fase == 'libre':
        P = dict(vm.FASES[1])
        P.update(EXTRA[1])
        P.update(brillo_c='fffbe0', brillo_b='ffc23a', borde=_hex('ffd36a'), halo=(255, 226, 150))
        return P
    P = dict(vm.FASES[fase])
    P.update(EXTRA[fase])
    return P


# ----------------------------------------------------------------------
#  Herramientas de pixel (numpy)
# ----------------------------------------------------------------------
def _ruido(W, H, celda, semilla):
    """Ruido de valor suave en [0, 1]."""
    r = np.random.default_rng(semilla)
    gw, gh = W // celda + 2, H // celda + 2
    g = r.random((gh, gw))
    y, x = np.mgrid[0:H, 0:W] / celda
    x0, y0 = x.astype(int), y.astype(int)
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0, x0] * (1 - fx) + g[y0, x0 + 1] * fx
    b = g[y0 + 1, x0] * (1 - fx) + g[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def _dentro(poly, X, Y):
    c = np.zeros(X.shape, bool)
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        cruza = (y1 > Y) != (y2 > Y)
        xc = (x2 - x1) * (Y - y1) / (y2 - y1 + 1e-12) + x1
        c ^= cruza & (X < xc)
    return c


def _erosion(m, k):
    out = m.copy()
    for _ in range(k):
        e = out.copy()
        e[1:, :] &= out[:-1, :]
        e[:-1, :] &= out[1:, :]
        e[:, 1:] &= out[:, :-1]
        e[:, :-1] &= out[:, 1:]
        out = e
    return out


def _linea(im, gl, x0, y0, x1, y1, col, glow=False, solo_dentro=True):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    H, W = im.shape[:2]
    for i in range(n + 1):
        t = i / n
        x, y = int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t)
        if 0 <= x < W and 0 <= y < H and (im[y, x, 3] > 0 or not solo_dentro):
            im[y, x] = col
            if glow:
                gl[y, x] = col


def _ojo(im, gl, cx, cy, R, P, giro=2.6):
    """Un ocelo de ciclon: aro oscuro, aro de luz, brazos en espiral y el ojo."""
    H, W = im.shape[:2]
    y, x = np.mgrid[0:H, 0:W] + 0.5
    d = np.hypot(x - cx, y - cy)
    a = np.arctan2(y - cy, x - cx)
    dentro = (d <= R) & (im[..., 3] > 0)
    costa = np.array((*P['costa'], 245))
    claro = np.array((*_hex(P['brillo_c']), 255))
    vivo = np.array((*_hex(P['brillo_b']), 255))
    brazo = (a - giro * np.log(np.maximum(d, 0.4) / R)) % (math.pi * 2 / 3) < 0.95
    for m, col, brilla in ((dentro & (d > R * 0.84), costa, False),
                           (dentro & (d > R * 0.66) & (d <= R * 0.84), claro, True),
                           (dentro & (d <= R * 0.66) & brazo, vivo, True),
                           (dentro & (d <= R * 0.66) & ~brazo, costa, False),
                           (dentro & (d <= R * 0.2), claro, True)):
        im[m] = col
        if brilla:
            gl[m] = col


def _rayo(im, gl, x, y, dx, dy, pasos, col, r):
    for _ in range(pasos):
        nx, ny = x + dx * r.uniform(1.5, 3.5) + r.uniform(-1.6, 1.6), y + dy * r.uniform(1.5, 3.5) + r.uniform(-1.6, 1.6)
        _linea(im, gl, x, y, nx, ny, col, True)
        if r.random() < 0.25:
            _linea(im, gl, nx, ny, nx + r.uniform(-4, 4), ny + r.uniform(-4, 4), col, True)
        x, y = nx, ny


# ----------------------------------------------------------------------
#  Las alas
# ----------------------------------------------------------------------
# (u, v): u hacia fuera del cuerpo, v hacia abajo. La raiz del ala en u=0.
POLY_SUP = [(0.0, 0.30), (0.10, 0.17), (0.30, 0.07), (0.55, 0.015), (0.80, 0.0), (0.95, 0.03), (1.0, 0.10),
            (0.97, 0.20), (0.92, 0.33), (0.89, 0.43), (0.83, 0.52), (0.78, 0.61), (0.70, 0.68), (0.63, 0.77),
            (0.53, 0.84), (0.43, 0.92), (0.31, 0.97), (0.19, 1.0), (0.08, 0.93), (0.0, 0.80)]
COSTA_SUP = [(0.0, 0.30), (0.30, 0.07), (0.80, 0.0), (1.0, 0.10)]
OJOS_SUP = [(0.55, 0.46, 0.15), (0.84, 0.17, 0.055)]
VENAS_SUP = [(0.97, 0.12), (0.92, 0.36), (0.80, 0.58), (0.62, 0.78), (0.42, 0.93), (0.2, 0.98)]
RAIZ_SUP = (0.0, 0.55)

POLY_INF = [(0.0, 0.0), (0.30, 0.0), (0.62, 0.05), (0.86, 0.16), (0.93, 0.28), (0.88, 0.40), (0.72, 0.49),
            (0.61, 0.55), (0.59, 0.63), (0.65, 0.73), (0.75, 0.84), (0.82, 0.93), (0.79, 1.0), (0.68, 0.99),
            (0.56, 0.90), (0.46, 0.76), (0.37, 0.64), (0.21, 0.56), (0.07, 0.44), (0.0, 0.27)]
COSTA_INF = [(0.0, 0.0), (0.62, 0.05), (0.93, 0.28)]
OJOS_INF = [(0.42, 0.25, 0.17), (0.76, 0.935, 0.07)]
VENAS_INF = [(0.9, 0.24), (0.74, 0.46), (0.6, 0.6), (0.78, 0.92), (0.3, 0.58), (0.08, 0.42)]
RAIZ_INF = (0.0, 0.12)


def _ala(W, H, poly, ojos, venas, raiz, fase, semilla):
    """Un ala del remake. Devuelve (imagen, brillo) RGBA."""
    P = paleta(fase)
    r = random.Random(semilla)
    pts = [(u * W, v * H) for u, v in poly]
    y, x = np.mgrid[0:H, 0:W] + 0.5
    dentro = _dentro(pts, x, y)
    ru, rv = raiz[0] * W, raiz[1] * H
    t = np.clip((np.hypot(x - ru, (y - rv) * 0.9) / W - 0.28) / 0.8, 0, 1)
    s = t * t * (3 - 2 * t)
    torm = np.array(P['tormenta'], float)
    mem = np.array(P['membrana'], float)
    blanco = np.array((246, 251, 255), float)
    base = torm[None, None] * (1 - s[..., None]) + mem[None, None] * s[..., None]
    base = base * (1 - 0.25 * s[..., None]) + blanco * 0.25 * s[..., None] ** 2
    n1, n2 = _ruido(W, H, 7, semilla), _ruido(W, H, 17, semilla + 1)
    base *= (0.8 + 0.24 * n1 + 0.14 * n2)[..., None]
    # nubes que giran hacia el ocelo grande
    cx, cy, R = ojos[0][0] * W, ojos[0][1] * H, ojos[0][2] * W
    de = np.hypot(x - cx, y - cy)
    ae = np.arctan2(y - cy, x - cx)
    brazo = ((ae + 2.2 * np.log(np.maximum(de, 0.5) / R)) % (math.pi * 2 / 3)) < 0.55
    giro = brazo & (de < R * 2.6) & (de > R)
    base[giro] = base[giro] * 0.75 + blanco * 0.25
    alfa = 236 - 70 * s + 14 * (n1 - 0.5)
    im = np.zeros((H, W, 4), np.uint8)
    im[..., :3] = np.clip(base, 0, 255).astype(np.uint8)
    im[..., 3] = np.where(dentro, np.clip(alfa, 0, 255), 0).astype(np.uint8)
    gl = np.zeros_like(im)
    # festones: muescas redondas a lo largo del margen de fuera
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        if min(x1, x2) < 0.45 * W:
            continue
        L = math.hypot(x2 - x1, y2 - y1)
        for k in range(1, int(L // 6) + 1):
            q = k * 6 / max(L, 1e-6)
            if q >= 1:
                break
            mx, my = x1 + (x2 - x1) * q, y1 + (y2 - y1) * q
            hueco = np.hypot(x - mx, y - my) < 2.3
            im[hueco, 3] = 0
    # desgarros en las fases altas
    for _ in range(int(14 * P['rasgado'])):
        hx, hy = r.uniform(0.55, 0.95) * W, r.uniform(0.15, 0.9) * H
        hr = r.uniform(1.4, 3.6)
        im[np.hypot(x - hx, (y - hy) * 0.7) < hr, 3] = 0
    # el borde: la costa oscura por fuera y, justo dentro, el filo encendido
    m = im[..., 3] > 0
    e1 = m & ~_erosion(m, 1)
    e2 = m & ~_erosion(m, 3) & ~e1
    borde = np.array((*P['borde'], 240))
    im[e2] = borde
    gl[e2] = borde
    im[e1] = (*P['costa'], 250)
    # la costa (borde de ataque), mas gruesa: la tapa la vara de quitina
    # las venas: de la raiz al margen, oscuras
    for (u1, v1) in venas:
        _linea(im, gl, ru, rv, u1 * W, v1 * H, (*P['vena'], 235))
    # rayos por las venas desde la fase III
    if P['rayos'] > 0:
        cb = (*_hex(P['brillo_c']), 255)
        for _ in range(int(2 + 4 * P['rayos'])):
            u1, v1 = r.choice(venas)
            dx, dy = u1 * W - ru, v1 * H - rv
            n = math.hypot(dx, dy)
            _rayo(im, gl, ru + dx * 0.15, rv + dy * 0.15, dx / n, dy / n, r.randint(6, 12), cb, r)
    for cxu, cyu, Ru in ojos:
        _ojo(im, gl, cxu * W, cyu * H, Ru * W, P)
    # jirones: el viento se lleva el margen (fase II en adelante)
    if P['rasgado'] > 0:
        m = im[..., 3] > 0
        borde_px = np.argwhere(m & ~_erosion(m, 1))
        for _ in range(int(160 * P['rasgado'])):
            by, bx = borde_px[r.randrange(len(borde_px))]
            if bx < 0.5 * W:
                continue
            dx, dy = bx - ru, by - rv
            n = math.hypot(dx, dy) + 1e-6
            largo = r.uniform(3, 9)
            for k in range(1, int(largo)):
                px_, py_ = int(bx + dx / n * k), int(by + dy / n * k + r.uniform(-0.6, 0.6))
                if 0 <= px_ < W and 0 <= py_ < H and im[py_, px_, 3] == 0:
                    im[py_, px_] = (*np.clip(mem * 1.1, 0, 255).astype(int), int(150 * (1 - k / largo)))
    return im, gl


# ----------------------------------------------------------------------
#  El halo, el nucleo y las cintas
# ----------------------------------------------------------------------
def _halo(fase):
    """El halo de viento: un aro de luz, una banda de nubes en espiral con
    doce marcas, y desde la III rayos por la banda."""
    P = paleta(fase)
    n = TAM_HALO[0] // DENSIDAD
    r = random.Random(40 + (0 if fase == 'libre' else fase))
    y, x = np.mgrid[0:n, 0:n] + 0.5
    c = n / 2
    d = np.hypot(x - c, y - c) / c
    a = np.arctan2(y - c, x - c)
    im = np.zeros((n, n, 4), np.uint8)
    gl = np.zeros_like(im)
    halo = np.array(P['halo'])
    claro = np.array(_hex(P['brillo_c']))
    banda = (d > 0.70) & (d < 0.93)
    nubes = ((a * 3 + 9.0 * d) % (2 * math.pi / 3)) < 1.2
    im[banda & nubes] = (*halo, 120)
    im[banda & ~nubes] = (*(halo * 0.75).astype(int), 60)
    for lo, hi, al in ((0.95, 0.99, 230), (0.66, 0.69, 200)):
        aro = (d > lo) & (d < hi)
        im[aro] = (*claro, al)
        gl[aro] = (*claro, 255)
    for k in range(12):
        ang = k * math.pi / 6
        for q in np.linspace(0.70, 0.93, 10):
            px_, py_ = int(c + math.cos(ang) * q * c), int(c + math.sin(ang) * q * c)
            if 0 <= px_ < n and 0 <= py_ < n:
                im[py_, px_] = (*claro, 230)
                gl[py_, px_] = (*claro, 255)
    if P['rayos'] > 0:
        for _ in range(int(3 + 6 * P['rayos'])):
            ang = r.uniform(0, 2 * math.pi)
            q = r.uniform(0.74, 0.9)
            x0, y0 = c + math.cos(ang) * q * c, c + math.sin(ang) * q * c
            for _ in range(r.randint(5, 9)):
                ang += r.uniform(0.04, 0.1)
                q = min(0.92, max(0.71, q + r.uniform(-0.04, 0.04)))
                x1, y1 = c + math.cos(ang) * q * c, c + math.sin(ang) * q * c
                _linea(im, gl, x0, y0, x1, y1, (*claro, 255), True, solo_dentro=False)
                x0, y0 = x1, y1
    return im, gl


def _nucleo(fase):
    P = paleta(fase)
    n = TAM_NUCLEO[0] // DENSIDAD
    im = np.zeros((n, n, 4), np.uint8)
    gl = np.zeros_like(im)
    y, x = np.mgrid[0:n, 0:n] + 0.5
    im[np.abs(x - n / 2) + np.abs(y - n / 2) <= n / 2] = (*P['quitina'][0], 255)
    _ojo(im, gl, n / 2, n / 2, n * 0.44, P, giro=3.0)
    return im, gl


def _cinta(fase, semilla, tam):
    P = paleta(fase)
    r = random.Random(semilla)
    W, H = tam[0] // DENSIDAD, tam[1] // DENSIDAD
    im = np.zeros((H, W, 4), np.uint8)
    gl = np.zeros_like(im)
    borde = np.array(P['borde'])
    for yy in range(H):
        t = yy / H
        cx = W / 2 + math.sin(t * 8 + semilla) * 1.6 * t
        ancho = (1 - t) * (W * 0.42) + 0.5
        for xx in range(W):
            d = abs(xx + 0.5 - cx)
            if d <= ancho:
                a = int(220 * (1 - t) + 25)
                if d > ancho - 1.0:
                    im[yy, xx] = (*borde, a)
                    gl[yy, xx] = (*borde, 255)
                else:
                    col = np.array(P['membrana']) * (0.78 + 0.2 * r.random()) * (1 - 0.25 * t) + 50 * t
                    im[yy, xx] = (*np.clip(col, 0, 255).astype(int), a)
    return im, gl


# ----------------------------------------------------------------------
#  Materiales del cuerpo (losetas de 16)
# ----------------------------------------------------------------------
def materiales(fase):
    P = paleta(fase)
    Q, F = P['quitina'], P['pelaje']
    nube = P['nube']
    bc, bb = _hex(P['brillo_c']), _hex(P['brillo_b'])

    def quitina(x, y, r):
        # placas con su junta oscura y el canto de arriba a la izquierda claro
        if x % 8 == 0 or y % 8 == 0:
            return Q[0]
        if x % 8 == 1 or y % 8 == 1:
            return Q[4] if r.random() < 0.7 else Q[3]
        return Q[r.choice([1, 2, 2, 2, 3])]

    def quitina_osc(x, y, r):
        return Q[r.choice([0, 0, 1, 1, 2])]

    def pelaje(x, y, r):
        b = r.choice([2, 3, 3, 4, 4])
        if (x * 3 + y) % 7 == 0:
            return nube
        if (x + y * 2) % 13 == 0:
            b = 1
        return F[b]

    def nube_m(x, y, r):
        return nube if r.random() < 0.6 else F[4]

    def anillos(x, y, r):
        if y % 8 == 6:
            return F[r.choice([2, 3])]
        if y % 8 == 7:
            return Q[0]
        return Q[r.choice([1, 2, 2, 3]) if x % 4 else 0]

    def ojo(x, y, r):
        borde = max(abs(x - 7.5), abs(y - 7.5)) / 7.5
        if x % 3 == 0 or y % 3 == 0:
            return tuple(int(bb[i] * 0.3) for i in range(3))
        k = max(0.0, 1 - 1.2 * borde)
        base = tuple(bb[i] * 0.65 for i in range(3))
        return tuple(int(base[i] + (bc[i] - base[i]) * k * 0.85) for i in range(3))

    def luz(x, y, r):
        # las vetas y las juntas que brillan: el color de la fase, con algun destello
        return bc if r.random() < 0.12 else bb

    return {
        'quitina': nm._loseta(301, quitina),
        'quitina_osc': nm._loseta(302, quitina_osc),
        'pelaje': nm._loseta(303, pelaje),
        'nube': nm._loseta(304, nube_m),
        'anillos': nm._loseta(305, anillos),
        'ojo': nm._loseta(306, ojo),
        'brillo': nm._loseta(307, nm.emisivo(P['brillo_c'], P['brillo_b'])),
        'luz': nm._loseta(308, luz),
    }


EMISIVOS = {'ojo', 'brillo', 'luz'}

# ----------------------------------------------------------------------
#  Las piezas
# ----------------------------------------------------------------------
class Parte:
    def __init__(self, nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
        self.nombre, self.padre = nombre, padre
        self.pivote = tuple(float(v) for v in pivote)
        self.rot = tuple(float(v) for v in rot)
        self.cajas = [tuple(c) for c in cajas]
        self.hijos = []


PARTES = {}
ORDEN = []


def parte(nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
    assert nombre not in PARTES, nombre
    p = Parte(nombre, padre, pivote, rot, cajas)
    PARTES[nombre] = p
    ORDEN.append(nombre)
    if padre:
        PARTES[padre].hijos.append(p)
    return p


PLANOS = {
    'ala_sup_izq': TAM_SUP, 'ala_sup_der': TAM_SUP, 'ala_inf_izq': TAM_INF, 'ala_inf_der': TAM_INF,
    'halo': TAM_HALO,
    'cinta_izq': TAM_CINTA, 'cinta_der': TAM_CINTA, 'cinta_izq2': TAM_CINTA_C, 'cinta_der2': TAM_CINTA_C,
}
NUCLEO = 'nucleo'


def _varas(nombre, ala, poly_costa, W, H, y0, s, gruesos):
    """La costa del ala hecha de cajas: un tramo por segmento, del grueso dado."""
    pts = [(u * W * s, y0 + v * H) for u, v in poly_costa]
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        L = math.hypot(bx - ax, by - ay)
        g = gruesos[i]
        ang = math.degrees(math.atan2(by - ay, bx - ax))
        parte(f'{nombre}{i}', ala, (ax, ay, 0), (0, 0, ang), [(0, -g / 2, -g / 2, L + g * 0.5, g, g, 'quitina_osc')])


def construir():
    PARTES.clear()
    ORDEN.clear()
    parte('cuerpo', None, (0, ALTURA_TORAX, 0))
    parte('torax', 'cuerpo', (0, 0, 0), (-8, 0, 0), [
        (-26, -28, -20, 52, 56, 40, 'quitina'),
        (-20, -31, 6, 40, 26, 16, 'quitina_osc'),            # la joroba de la espalda
        (-18, -10, -20.4, 36, 34, 1.4, 'quitina_osc'),       # el peto
        (-26.8, -18, -4, 1.2, 36, 3, 'luz'),                # las vetas de los costados
        (25.6, -18, -4, 1.2, 36, 3, 'luz'),
        (-22, 24, -17, 44, 7, 34, 'pelaje'),                 # el pelo de la cintura
    ])
    # El ojo de la tormenta, mayor, con un marco de ocho puas.
    parte('nucleo', 'torax', (0, 7, -20.6), cajas=[(-20, -20, -0.6, 40, 40, 0.6, NUCLEO)])
    for k in range(8):
        th = k * 45 + 22.5
        parte(f'marco{k}', 'nucleo', (math.cos(math.radians(th)) * 19, math.sin(math.radians(th)) * 19, -0.4),
              (0, 0, th + 90), [(-1.5, -8, -1.5, 3, 8, 3, 'quitina_osc')])
    # La melena de nubes y sus mechones (por los lados y la espalda: la cara queda libre).
    parte('melena', 'torax', (0, -24, 2), cajas=[
        (-40, -14, -28, 80, 22, 54, 'pelaje'),
        (-46, -8, -18, 12, 20, 38, 'pelaje'), (34, -8, -18, 12, 20, 38, 'pelaje'),
        (-30, -21, -24, 60, 8, 42, 'nube'),
    ])
    for k in range(10):
        a = math.radians(-150 + k * 300 / 9)
        parte(f'mechon{k}', 'melena', (38 * math.sin(a), -12, 2 + 25 * math.cos(a)),
              (-40 * math.cos(a), 0, 40 * math.sin(a)),
              [(-6, -30, -5, 12, 30, 10, 'pelaje'), (-4, -38, -4, 8, 9, 8, 'nube')])

    parte('cabeza', 'torax', (0, -31, -6), (14, 0, 0), [
        (-18, -28, -16, 36, 28, 30, 'quitina'),
        (-20, -33, -8, 40, 8, 24, 'pelaje'),                 # la cresta
        (-6, -8, -17.2, 12, 8, 1.2, 'quitina_osc'),          # la boca
        (-11, -2, -13, 22, 7, 16, 'pelaje'),                 # la barba
    ])
    # La corona: siete puas que se abren hacia atras, la del centro la mas larga.
    for k in range(7):
        z = -78 + k * 26
        L = 54 - abs(k - 3) * 7
        parte(f'pua{k}', 'cabeza', (math.sin(math.radians(z)) * 13, -27, 6), (-24 + abs(k - 3) * 3, 0, z),
              [(-3, -L, -3, 6, L, 6, 'quitina_osc'), (-2.2, -L - 8, -2.2, 4.4, 8, 4.4, 'brillo')])
    for s, n in ((1, 'izq'), (-1, 'der')):
        parte('ojo_' + n, 'cabeza', (12 * s, -15, -13), (0, 0, -18 * s), [(-6, -9, -5, 12, 18, 14, 'ojo')])
        parte('ceno_' + n, 'cabeza', (9 * s, -23, -17.5), (0, 0, -22 * s),
              [(-8 if s > 0 else -9, -3, -1, 17, 5, 6, 'quitina_osc')])
        parte('colmillo_' + n, 'cabeza', (6 * s, -3, -15), (-12, 0, -16 * s), [(-2, 0, -2, 4, 13, 4, 'quitina_osc')])
        parte('colmillo_punta_' + n, 'colmillo_' + n, (0, 13, 0), (-30, 0, 34 * s), [(-1.4, 0, -1.4, 2.8, 11, 2.8, 'nube')])
        barbas = []
        for i in range(16):
            L = 12 - abs(i - 6) * 0.85
            y = -8 - i * 4.6
            barbas.append((0.8, y, -0.6, L, 1.4, 1.2, 'pelaje'))
            barbas.append((-0.8 - L, y, -0.6, L, 1.4, 1.2, 'pelaje'))
        parte('antena_' + n, 'cabeza', (9 * s, -27, -8), (-40, 0, 36 * s),
              [(-1.6, -80, -1.6, 3.2, 80, 3.2, 'quitina_osc'), *barbas])
        parte('antena_punta_' + n, 'antena_' + n, (0, -80, 0), (-40, 0, -14 * s),
              [(-1, -14, -1, 2, 14, 2, 'quitina_osc'), (-2, -18, -2, 4, 4, 4, 'brillo')])

    # Las alas: planos con su imagen y la costa de cajas.
    for s, n in ((1, 'izq'), (-1, 'der')):
        W, H = TAM_SUP
        y0 = -H * 0.36
        parte('ala_sup_' + n, 'torax', (24 * s, -16, 14), (0, -12 * s, -10 * s),
              [(0.0 if s > 0 else -W, y0, 0.0, W, H, 0.0, 'ala_sup_' + n)])
        _varas('costa_sup_' + n, 'ala_sup_' + n, COSTA_SUP, W, H, y0, s, (8.5, 6.5, 4.5))
        W, H = TAM_INF
        y0 = -H * 0.04
        parte('ala_inf_' + n, 'torax', (22 * s, 12, 16), (0, -18 * s, -12 * s),
              [(0.0 if s > 0 else -W, y0, 0.0, W, H, 0.0, 'ala_inf_' + n)])
        _varas('costa_inf_' + n, 'ala_inf_' + n, COSTA_INF, W, H, y0, s, (7, 5))

    # El halo de viento, detras de la espalda.
    W, H = TAM_HALO
    parte('halo', 'torax', (0, -30, 30), cajas=[(-W / 2, -H / 2, 0, W, H, 0, 'halo')])

    # Seis patas: las de delante, de presa, con cuchilla.
    for s, n in ((1, 'izq'), (-1, 'der')):
        parte('pata0_' + n, 'torax', (16 * s, -6, -12), (-52, 0, 30 * s), [(-3, 0, -3, 6, 30, 6, 'quitina')])
        parte('pata0_' + n + '_tibia', 'pata0_' + n, (0, 30, 0), (-100, 0, 0), [
            (-2.2, 0, -2.2, 4.4, 32, 4.4, 'quitina_osc'),
            (-0.6, 3, -7, 1.2, 26, 5, 'quitina'),              # la cuchilla
            *[(-1, 6 + k * 6, -9.5, 2, 2, 3, 'nube') for k in range(4)],   # sus puas
        ])
        parte('pata0_' + n + '_garra', 'pata0_' + n + '_tibia', (0, 32, 0), (40, 0, 0), [(-1.5, 0, -1, 3, 11, 2, 'quitina_osc')])
        for i in (1, 2):
            rot = [None, (-6, 0, 52 * s), (30, 0, 52 * s)][i]
            nom = f'pata{i}_{n}'
            parte(nom, 'torax', (17 * s, -8 + i * 13, -8 + i * 4), rot, [(-2.5, 0, -2.5, 5, 30, 5, 'quitina'),
                                                                        (-3, 4, -3, 6, 6, 6, 'pelaje')])
            parte(nom + '_tibia', nom, (0, 30, 0), (50, 0, 0), [(-1.8, 0, -1.8, 3.6, 32, 3.6, 'quitina_osc')])
            parte(nom + '_garra', nom + '_tibia', (0, 32, 0), (34, 0, 0), [(-2, 0, -0.75, 4, 9, 1.5, 'quitina')])

    # El abdomen: cinco segmentos con juntas de luz; la punta con su aleta y cuatro cintas.
    parte('abdomen', 'torax', (0, 25, 4), (10, 0, 0), [(-18, 0, -15, 36, 22, 30, 'anillos'),
                                                       (-18.6, 20.4, -15.6, 37.2, 1.6, 31.2, 'luz')])
    parte('abdomen2', 'abdomen', (0, 22, 0), (8, 0, 0), [(-15, 0, -12, 30, 20, 24, 'anillos'),
                                                        (-15.6, 18.4, -12.6, 31.2, 1.6, 25.2, 'luz')])
    parte('abdomen3', 'abdomen2', (0, 20, 0), (8, 0, 0), [(-11.5, 0, -9, 23, 18, 18, 'anillos'),
                                                         (-12.1, 16.4, -9.6, 24.2, 1.6, 19.2, 'luz')])
    parte('abdomen4', 'abdomen3', (0, 18, 0), (10, 0, 0), [(-8, 0, -6.5, 16, 15, 13, 'anillos')])
    parte('punta', 'abdomen4', (0, 15, 0), (10, 0, 0), [(-4, 0, -3.5, 8, 11, 7, 'quitina'), (-2.5, 10, -2.5, 5, 5, 5, 'brillo'),
                                                        (-0.6, 1, 3, 1.2, 12, 9, 'quitina_osc')])
    for nom, x, rz, tam in (('cinta_izq', 2.0, -8, TAM_CINTA), ('cinta_der', -2.0, 9, TAM_CINTA),
                            ('cinta_izq2', 3.0, -22, TAM_CINTA_C), ('cinta_der2', -3.0, 24, TAM_CINTA_C)):
        parte(nom, 'punta', (x, 12, 0), (0, 0, rz), [(-tam[0] / 2, 0, 0, tam[0], tam[1], 0, nom)])


# ----------------------------------------------------------------------
#  Cinematica, atlas, pintura y cuadrilateros (como en vendaval_juego.py)
# ----------------------------------------------------------------------
T, Rx, Ry, Rz = nm.vr.T, nm.vr.Rx, nm.vr.Ry, nm.vr.Rz
D2R = math.pi / 180


def matrices(pose=None):
    pose = pose or {}
    out = {}

    def visitar(p, M):
        ex = pose.get(p.nombre, {})
        r = [p.rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        q = [p.pivote[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        e = ex.get('esc', (1, 1, 1))
        L = T(*q) @ Rz(r[2] * D2R) @ Ry(r[1] * D2R) @ Rx(r[0] * D2R) @ np.diag([e[0], e[1], e[2], 1.0])
        Mn = M @ L
        out[p.nombre] = Mn
        for h in p.hijos:
            visitar(h, Mn)

    for n in ORDEN:
        if PARTES[n].padre is None:
            visitar(PARTES[n], np.eye(4))
    return out


def punto(pose, pieza, local=(0, 0, 0)):
    M = matrices(pose)[pieza]
    return (M @ np.array([*local, 1.0]))[:3]


def a_bloques(p):
    """Del modelo (px, Y abajo, frente -Z) al espacio de la entidad en bloques:
    (izquierda, alto, frente)."""
    k = ESCALA / 16
    return (p[0] * k, (24.016 - p[1]) * k, -p[2] * k)


def tam_uv(c):
    x0, y0, z0, w, h, d, mat = c
    return int(math.ceil(2 * (d + w))) + 2, int(math.ceil(d + h)) + 2


def clave(c):
    return (round(c[3], 3), round(c[4], 3), round(c[5], 3), c[6])


def empaquetar():
    claves = {}
    for n in ORDEN:
        for c in PARTES[n].cajas:
            claves.setdefault(clave(c), c)
    orden = sorted(claves, key=lambda k: (-tam_uv(claves[k])[1], -tam_uv(claves[k])[0]))
    uv = {}
    x = y = fila = 0
    for k in orden:
        w, h = tam_uv(claves[k])
        w += (-w) % DENSIDAD
        h += (-h) % DENSIDAD
        if x + w > ANCHO_ATLAS:
            x, y, fila = 0, y + fila, 0
        uv[k] = (x, y)
        x += w
        fila = max(fila, h)
    alto = y + fila
    return uv, 1 << (alto - 1).bit_length()


def caras_uv(u, v, w, h, d):
    return {'arriba': (u + d, v, w, d), 'abajo': (u + d + w, v, w, d), 'oeste': (u, v + d, d, h),
            'frente': (u + d, v + d, w, h), 'este': (u + d + w, v + d, d, h), 'espalda': (u + 2 * d + w, v + d, w, h)}


def _redim(im, w, h):
    return np.array(Image.fromarray(im).resize((max(1, w), max(1, h)), Image.NEAREST))


_IMGS = {}


def imagenes(fase):
    if fase in _IMGS:
        return _IMGS[fase]
    out = {}
    W, H = TAM_SUP[0] // DENSIDAD, TAM_SUP[1] // DENSIDAD
    sup = _ala(W, H, POLY_SUP, OJOS_SUP, VENAS_SUP, RAIZ_SUP, fase, 17)
    W, H = TAM_INF[0] // DENSIDAD, TAM_INF[1] // DENSIDAD
    inf = _ala(W, H, POLY_INF, OJOS_INF, VENAS_INF, RAIZ_INF, fase, 18)
    out['ala_sup_izq'] = sup
    out['ala_sup_der'] = (sup[0][:, ::-1].copy(), sup[1][:, ::-1].copy())
    out['ala_inf_izq'] = inf
    out['ala_inf_der'] = (inf[0][:, ::-1].copy(), inf[1][:, ::-1].copy())
    out['halo'] = _halo(fase)
    for nom, sem in (('cinta_izq', 1), ('cinta_der', 2), ('cinta_izq2', 3), ('cinta_der2', 4)):
        out[nom] = _cinta(fase, sem, PLANOS[nom])
    out[NUCLEO] = _nucleo(fase)
    _IMGS[fase] = out
    return out


def pintar_atlas(uv, alto, fase=1):
    ancho_png, alto_png = ANCHO_ATLAS // DENSIDAD, alto // DENSIDAD
    base = np.zeros((alto_png, ancho_png, 4), np.uint8)
    brillo = np.zeros_like(base)
    mats = materiales(fase)
    imgs = imagenes(fase)
    rnd = random.Random(11)
    hechas = set()
    Q0 = paleta(fase)['quitina'][0]
    for n in ORDEN:
        for c in PARTES[n].cajas:
            k = clave(c)
            if k in hechas:
                continue
            hechas.add(k)
            u, v = uv[k]
            w, h, d, mat = k
            if mat in PLANOS or mat == NUCLEO:
                im, gl = imgs[mat]
                caras = caras_uv(u, v, w, h, d)
                for cara, espejo in (('frente', False), ('espalda', True)):
                    fx, fy, fw, fh = caras[cara]
                    x0, y0 = int(round(fx / DENSIDAD)), int(round(fy / DENSIDAD))
                    x1, y1 = int(round((fx + fw) / DENSIDAD)), int(round((fy + fh) / DENSIDAD))
                    if x1 <= x0 or y1 <= y0:
                        continue
                    a, b = im, gl
                    if a.shape[0] != y1 - y0 or a.shape[1] != x1 - x0:
                        a, b = _redim(a, x1 - x0, y1 - y0), _redim(b, x1 - x0, y1 - y0)
                    if espejo:
                        a, b = a[:, ::-1], b[:, ::-1]
                    base[y0:y1, x0:x1] = a
                    brillo[y0:y1, x0:x1] = b
                if mat == NUCLEO:
                    for cara in ('arriba', 'abajo', 'oeste', 'este'):
                        fx, fy, fw, fh = caras[cara]
                        x0, y0 = int(math.floor(fx / DENSIDAD)), int(math.floor(fy / DENSIDAD))
                        x1, y1 = int(math.ceil((fx + fw) / DENSIDAD)), int(math.ceil((fy + fh) / DENSIDAD))
                        if x1 > x0 and y1 > y0:
                            base[y0:y1, x0:x1] = (*Q0, 255)
                continue
            loseta = mats[mat]
            ox, oy = rnd.randrange(16), rnd.randrange(16)
            for cara, (fx, fy, fw, fh) in caras_uv(u, v, w, h, d).items():
                x0, y0 = int(math.floor(fx / DENSIDAD)), int(math.floor(fy / DENSIDAD))
                x1, y1 = int(math.ceil((fx + fw) / DENSIDAD)), int(math.ceil((fy + fh) / DENSIDAD))
                if x1 <= x0 or y1 <= y0:
                    continue
                yy, xx = np.mgrid[y0:y1, x0:x1]
                col = loseta[(yy - y0 + oy) % 16, (xx - x0 + ox) % 16].astype(float)
                if mat not in EMISIVOS:
                    j = (yy - y0) / max(1, (y1 - y0 - 1))
                    if cara == 'abajo':
                        col[..., :3] *= 0.72
                    elif cara != 'arriba':
                        col[..., :3] *= (1.0 - 0.10 * j)[..., None]
                        if y1 - y0 > 2:
                            col[-1, :, :3] *= 0.8
                            col[0, :, :3] = np.minimum(255, col[0, :, :3] * 1.12)
                base[y0:y1, x0:x1] = np.clip(col, 0, 255)
                if mat in EMISIVOS:
                    brillo[y0:y1, x0:x1] = np.clip(col, 0, 255)
    return base, brillo


# ----------------------------------------------------------------------
#  Exportar a Java
# ----------------------------------------------------------------------
def f(x):
    s = ('%.4f' % x).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s + 'F'


def var(n):
    return 'p_' + n


def java_malla(uv, alto):
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.model.geom.PartPose;',
         'import net.minecraft.client.model.geom.builders.CubeDeformation;',
         'import net.minecraft.client.model.geom.builders.CubeListBuilder;',
         'import net.minecraft.client.model.geom.builders.LayerDefinition;',
         'import net.minecraft.client.model.geom.builders.MeshDefinition;',
         'import net.minecraft.client.model.geom.builders.PartDefinition;', '',
         '/**',
         ' * La malla de Aeralis, la Reina del Vendaval. GENERADO por',
         ' * materiales/generadores/vendaval_juego.py: no se edita a mano. Cambiar una',
         ' * caja aqui sin cambiar el script descuadra la textura, que se pinta con la',
         ' * misma cuadricula (a media resolucion: el atlas se declara de ' + str(ANCHO_ATLAS) + ' y el PNG',
         ' * mide la mitad).',
         ' */',
         'public final class AeralisMalla {', '',
         '    private AeralisMalla() {', '    }', '',
         '    public static LayerDefinition crear() {',
         '        return crear(CubeDeformation.NONE);',
         '    }', '',
         '    /** La misma malla hinchada: la capa del aura de la Furia (como la de Rajang). */',
         '    public static LayerDefinition crearAura() {',
         '        return crear(new CubeDeformation(2.0F));',
         '    }', '',
         '    private static LayerDefinition crear(CubeDeformation infla) {',
         '        MeshDefinition malla = new MeshDefinition();',
         '        PartDefinition p_root = malla.getRoot();']
    for n in ORDEN:
        p = PARTES[n]
        padre = var(p.padre) if p.padre else 'p_root'
        cub = 'CubeListBuilder.create()'
        for c in p.cajas:
            u, v = uv[clave(c)]
            cub += f'\n                .texOffs({u}, {v}).addBox({f(c[0])}, {f(c[1])}, {f(c[2])}, {f(c[3])}, {f(c[4])}, {f(c[5])}, infla)'
        rx, ry, rz = [r * D2R for r in p.rot]
        pose = f'PartPose.offsetAndRotation({f(p.pivote[0])}, {f(p.pivote[1])}, {f(p.pivote[2])}, {f(rx)}, {f(ry)}, {f(rz)})'
        decl = f'PartDefinition {var(n)} = ' if p.hijos else ''
        L.append(f'        {decl}{padre}.addOrReplaceChild("{n}", {cub},\n                {pose});')
    L.append(f'        return LayerDefinition.create(malla, {ANCHO_ATLAS}, {alto});')
    L.append('    }')
    L.append('}')
    return '\n'.join(L) + '\n'


def quads(pose, uv, alto, modelo_a_mundo):
    Ms = matrices(pose)
    out = []
    for n in ORDEN:
        q, oculto = n, False
        while q:
            if pose.get(q, {}).get('oculto'):
                oculto = True
            q = PARTES[q].padre
        if oculto:
            continue
        M = modelo_a_mundo @ Ms[n]
        for c in PARTES[n].cajas:
            u, v = uv[clave(c)]
            for pts, uvs in nm.vr.caja_quads((u, v), c[:6], False, ANCHO_ATLAS, alto):
                w = [(M @ np.array([*q_, 1.0]))[:3] for q_ in pts]
                out.append((w, uvs, n, c[6]))
    return out


# ----------------------------------------------------------------------
#  Poses para la ficha (se suman a la de reposo)
# ----------------------------------------------------------------------
def _alas(sup, inf, sup_y=0.0, inf_y=0.0):
    return {'ala_sup_izq': {'rot': (0, -sup_y, -sup)}, 'ala_sup_der': {'rot': (0, sup_y, sup)},
            'ala_inf_izq': {'rot': (0, -inf_y, -inf)}, 'ala_inf_der': {'rot': (0, inf_y, inf)}}


HEROICA = {'torax': {'rot': (-14, 0, 0)}, 'cabeza': {'rot': (20, 0, 0)},
           **_alas(12, 4, 0, 4),
           'pata0_izq': {'rot': (-10, 0, 0)}, 'pata0_der': {'rot': (-10, 0, 0)},
           'colmillo_izq': {'rot': (-24, 0, -20)}, 'colmillo_der': {'rot': (-24, 0, 20)}}
ALETEO = {'torax': {'rot': (-10, 0, 0)}, 'cabeza': {'rot': (18, 0, 0)},
          **_alas(-24, -8, 34, 30),
          'colmillo_izq': {'rot': (-34, 0, -30)}, 'colmillo_der': {'rot': (-34, 0, 30)}}
JUICIO = {'torax': {'rot': (8, 0, 0)}, 'cabeza': {'rot': (28, 0, 0)}, **_alas(44, 16, 4, 8),
          'pata0_izq': {'rot': (-30, 0, 20)}, 'pata0_der': {'rot': (-30, 0, -20)}}
# El picado: las alas plegadas hacia atras, el cuerpo tumbado hacia delante.
PICADO = {'cuerpo': {'rot': (62, 0, 0)}, 'cabeza': {'rot': (-30, 0, 0)},
          'ala_sup_izq': {'rot': (0, 62, 8)}, 'ala_sup_der': {'rot': (0, -62, -8)},
          'ala_inf_izq': {'rot': (0, 66, -6)}, 'ala_inf_der': {'rot': (0, -66, 6)},
          'pata0_izq': {'rot': (-40, 0, -10)}, 'pata0_der': {'rot': (-40, 0, 10)},
          'abdomen': {'rot': (-14, 0, 0)}, 'abdomen2': {'rot': (-8, 0, 0)}}
# Posada tras el picado: en el suelo como una polilla en reposo, las alas
# cerradas hacia arriba, el abdomen tumbado detras y la cabeza baja, jadeando.
POSADA = {'cuerpo': {'rot': (-6, 0, 0)}, 'cabeza': {'rot': (22, 0, 0)}, **_alas(78, 58, 34, 30),
          'pata0_izq': {'rot': (30, 0, 0)}, 'pata0_der': {'rot': (30, 0, 0)},
          'pata1_izq': {'rot': (0, 0, -20)}, 'pata1_der': {'rot': (0, 0, 20)},
          'pata2_izq': {'rot': (0, 0, -20)}, 'pata2_der': {'rot': (0, 0, 20)},
          'abdomen': {'rot': (-78, 0, 0)}, 'abdomen2': {'rot': (-6, 0, 0)}}
# Escamas: las alas en lo alto, sacudidas.
ESCAMAS = {'torax': {'rot': (-20, 0, 0)}, 'cabeza': {'rot': (30, 0, 0)}, **_alas(52, 30, -8, 0)}

construir()

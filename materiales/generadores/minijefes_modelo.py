"""
Bocetos 3D de los cuatro mini jefes, en VOXELES (11-10-2026, Juan: "mejora los
disenos de los minijefes, tiene que estar como las imagenes que te pase... crea
mas bloques, no te limites"):

  - Moctezuma, el Guerrero Aguila de Jade (tierra): yelmo de aguila con el pico
    de oro, penacho de plumas de quetzal en abanico, hombreras de plumas,
    coraza de escamas de jade con el medallon de oro, chimalli con la cara de
    oro y macuahuitl de jade con dientes de obsidiana.
  - Yiatzo, el Mago del Viento: tunica de piedra gris con pliegues y runas,
    capucha honda sin cara, mangas anchas, baston con el orbe de viento en una
    jaula de plata, libro abierto con runas y glifos que flotan.
  - Atlahua, el Triton de las Profundidades (agua): rey del mar con la corona
    y las hombreras de coral, ojos de luz, barba de algas, armadura de escamas
    del abismo, capa de algas y tridente de coral con las puntas encendidas.
  - Xiuhquetzal, el Fenix de Llamas Rojas y Violetas (fuego): ave de fuego con
    el pecho de brasa, alas enormes de plumas rojas, naranjas y violetas que
    acaban en llamas, cresta de fuego y cola larga de quetzal.

Cada pieza es un monton de voxeles de 1 pixel de modelo (16 = 1 bloque), pero
no se ven los cubos (Juan: "no tiene que verse que esta conformado por
bloques... lo ocultan con color"): el color va por manchas y dibujos, como una
textura pintada, sin canto en cada cubo, y la luz sigue la forma (normales
suavizadas) y no cada escalon. Mismo marco que los demas bocetos: Y hacia abajo, el frente
mira a -Z, el suelo en y = 24; cada pieza es un nodo animable (nombre, origen,
giro, voxeles, hijos), asi que las poses giran piezas enteras.
"""
import contextlib
import functools
import math
import random

import numpy as np

import vigia_render as vr


def H(h, e=0.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), e)


def Hs(*hs, e=0.0):
    return [H(h, e) for h in hs]


# Los voxeles con nombre: brillan enteros y las escenas los buscan (la punta del tridente, el orbe...).
NOMBRADOS = {
    'mj_orbe': ((215, 250, 255), 1.0), 'mj_brasa': ((255, 238, 160), 1.0), 'mj_punta_coral': ((150, 245, 255), 1.0),
    'mj_ojo_oro': ((255, 205, 70), 1.0), 'mj_ojo_jade': ((130, 255, 175), 1.0), 'mj_ojo_viento': ((175, 240, 255), 1.0),
    'mj_ojo_abismo': ((130, 245, 255), 1.0), 'mj_ojo_fenix': ((255, 190, 60), 1.0), 'mj_gema': ((70, 215, 140), 0.75),
    'mj_senuelo': ((205, 255, 250), 1.0),
}


def _q(c):
    r, g, b, e = c
    return (max(0, min(255, int(r) // 5 * 5)), max(0, min(255, int(g) // 5 * 5)), max(0, min(255, int(b) // 5 * 5)),
            round(min(1.0, e), 1))


def rango(a, b):
    return range(math.floor(a), math.ceil(b))


def _hash(ix, iy, iz, s):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (s * 2654435761)
    h &= 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return (h & 0xffff) / 65535.0


def ruido(x, y, z, esc=2.5, s=0):
    """Ruido suave en 3D (0..1): manchas de unos 'esc' voxeles, para pintar por zonas y no cubo a cubo."""
    fx, fy, fz = x / esc, y / esc, z / esc
    ix, iy, iz = math.floor(fx), math.floor(fy), math.floor(fz)
    tx, ty, tz = fx - ix, fy - iy, fz - iz
    tx, ty, tz = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty), tz * tz * (3 - 2 * tz)
    v = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (tx if dx else 1 - tx) * (ty if dy else 1 - ty) * (tz if dz else 1 - tz)
                v += w * _hash(ix + dx, iy + dy, iz + dz, s)
    return v


class Vox:
    """Los voxeles de una pieza: (x, y, z) entero -> color (r, g, b, brillo) o un nombre de NOMBRADOS."""

    def __init__(self, semilla=0):
        self.d = {}
        self.r = random.Random(semilla)
        self._caras = None
        # Los voxeles apuntados por grupos (la capa, el faldon...): el juego los separa en su propia pieza para que
        # se muevan solos. Apuntarlos no cambia nada del dibujo.
        self.grupos = {}
        self._grabando = None

    def color(self, col, x, y, z, jitter=0.025):
        if callable(col):
            col = col(x, y, z, self.r)
        if isinstance(col, list):
            col = self.r.choice(col)
        if col is None or isinstance(col, str):
            return col
        if jitter:
            k = self.r.uniform(1 - jitter, 1 + jitter * 0.6)
            col = (col[0] * k, col[1] * k, col[2] * k, col[3])
        return _q(col)

    def pon(self, x, y, z, col, jitter=0.025):
        c = self.color(col, math.floor(x), math.floor(y), math.floor(z), jitter)
        if c is not None:
            self.d[(math.floor(x), math.floor(y), math.floor(z))] = c
            if self._grabando is not None:
                self._grabando.add((math.floor(x), math.floor(y), math.floor(z)))

    @contextlib.contextmanager
    def grupo(self, nombre):
        """Apunta en self.grupos[nombre] los voxeles que se ponen dentro."""
        previo = self._grabando
        self._grabando = self.grupos.setdefault(nombre, set())
        try:
            yield
        finally:
            self._grabando = previo

    def quita(self, x, y, z):
        self.d.pop((math.floor(x), math.floor(y), math.floor(z)), None)

    def caras(self):
        """Las caras a la vista, con su color y una normal suavizada: la de la cara mezclada con la que da el hueco
        de alrededor del voxel (radio 2), para que la luz siga la forma y no los escalones."""
        if self._caras is None:
            d = self.d
            pts, cols, nors = [], [], []
            for (x, y, z), c in d.items():
                caras = [(n, esq) for n, esq in _CARAS if (x + n[0], y + n[1], z + n[2]) not in d]
                if not caras:
                    continue
                g = np.zeros(3)
                for o in _ENTORNO:
                    if (x + o[0], y + o[1], z + o[2]) not in d:
                        g += o
                lg = np.linalg.norm(g)
                for n, esq in caras:
                    nn = np.array(n, float)
                    if lg > 1.5:
                        nn = nn * 0.35 + g / lg * 0.65
                        nn /= np.linalg.norm(nn) or 1.0
                    pts.append([(x + a, y + b, z + cc) for a, b, cc in esq])
                    cols.append(c)
                    nors.append(nn)
            self._caras = (np.array(pts, float).reshape(-1, 4, 3), cols, np.array(nors, float).reshape(-1, 3))
        return self._caras


_CARAS = (
    ((1, 0, 0), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((-1, 0, 0), ((0, 0, 1), (0, 1, 1), (0, 1, 0), (0, 0, 0))),
    ((0, 1, 0), ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 0, 1), ((1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 0, 1))),
    ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
)
_VECINOS = [d for d, _ in _CARAS]
_ENTORNO = [np.array((a, b, c), float) for a in range(-2, 3) for b in range(-2, 3) for c in range(-2, 3)
            if 0 < a * a + b * b + c * c <= 5]


# ----------------------------------------------------------------------
#  Formas
# ----------------------------------------------------------------------
def elipsoide(v, c, r, col, cond=None):
    cx, cy, cz = c
    rx, ry, rz = r
    for x in rango(cx - rx, cx + rx):
        for y in rango(cy - ry, cy + ry):
            for z in rango(cz - rz, cz + rz):
                px, py, pz = x + .5 - cx, y + .5 - cy, z + .5 - cz
                if (px / rx) ** 2 + (py / ry) ** 2 + (pz / rz) ** 2 <= 1 and (cond is None or cond(x + .5, y + .5, z + .5)):
                    v.pon(x, y, z, col)


def caja(v, x0, y0, z0, x1, y1, z1, col):
    for x in rango(x0, x1):
        for y in rango(y0, y1):
            for z in rango(z0, z1):
                v.pon(x, y, z, col)


def capsula(v, a, b, r0, r1, col, cond=None):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    l2 = float(ab @ ab) or 1e-9
    rm = max(r0, r1)
    lo, hi = np.minimum(a, b) - rm, np.maximum(a, b) + rm
    for x in rango(lo[0], hi[0]):
        for y in rango(lo[1], hi[1]):
            for z in rango(lo[2], hi[2]):
                p = np.array([x + .5, y + .5, z + .5])
                t = min(1.0, max(0.0, float((p - a) @ ab) / l2))
                if np.linalg.norm(p - (a + ab * t)) <= r0 + (r1 - r0) * t and (cond is None or cond(*p)):
                    v.pon(x, y, z, col)


def poli(v, pts, radios, col):
    for i in range(len(pts) - 1):
        capsula(v, pts[i], pts[i + 1], radios[i], radios[i + 1], col)


def anillo(v, y0, y1, r0, r1, col, cx=0.0, cz=0.0, kz=1.0):
    for y in range(y0, y1):
        for x in rango(cx - r1, cx + r1):
            for z in rango(cz - r1 * kz, cz + r1 * kz):
                d = math.hypot(x + .5 - cx, (z + .5 - cz) / kz)
                if r0 <= d <= r1:
                    v.pon(x, y, z, col)


def _unit(a):
    a = np.asarray(a, float)
    return a / (np.linalg.norm(a) or 1.0)


def _grad(cols, t):
    t = min(max(t, 0.0), 1.0) * (len(cols) - 1)
    i = min(int(t), len(cols) - 2)
    f = t - i
    a, b = cols[i], cols[i + 1]
    return tuple(a[k] + (b[k] - a[k]) * f for k in range(4))


def tira(v, p0, d, lado, largo, ancho, cols, punta=0.82, paso=0.4, llama=0, cols_llama=None, raquis=True, ensancha=0.0):
    """Una pluma (o aleta, o cinta): una hoja de un voxel de grueso que sale de p0 hacia d, ancha hacia 'lado'.
    cols va de la raiz a la punta; con llama, la punta se deshace en cubos de fuego sueltos."""
    p0, d, lado = np.asarray(p0, float), _unit(d), _unit(lado)
    n = int(largo / paso) + 1
    for k in range(n):
        t = k / max(1, n - 1)
        if t < punta:
            w = ancho * (0.35 + 0.65 * math.sin(math.pi * 0.5 * min(1.0, t / 0.35))) * (1 + ensancha * t)
        else:
            w = ancho * (1 + ensancha * t) * max(0.0, 1 - (t - punta) / (1 - punta)) ** 0.7
        c = _grad(cols, t)
        for s in np.arange(-w / 2, w / 2 + 1e-6, paso):
            p = p0 + d * (t * largo) + lado * s
            cc = c
            if raquis and abs(s) < 0.45 and t < 0.9:
                cc = (min(255, c[0] * 1.18), min(255, c[1] * 1.18), min(255, c[2] * 1.18), c[3])
            elif abs(s) > w / 2 - 0.5 and t > 0.15:
                cc = (c[0] * 0.8, c[1] * 0.8, c[2] * 0.8, c[3])
            v.pon(*p, cc)
    if llama:
        punta_p = p0 + d * largo
        cl = cols_llama or Hs('ffe08a', 'ff9a30', 'ff5ab0', 'c060ff', e=0.85)
        for _ in range(int(llama * 4)):
            u = v.r.uniform(0, llama)
            p = punta_p + d * u + lado * v.r.uniform(-1.4, 1.4) * (1 - u / (llama + 1))
            v.pon(*p, cl[min(len(cl) - 1, int(u / llama * len(cl)))])


def coral(v, base, d, largo, r, nivel, cols, puntas):
    base, d = np.asarray(base, float), _unit(d)
    fin = base + d * largo
    capsula(v, base, fin, r, max(0.5, r * 0.7), cols)
    v.pon(*fin, puntas)
    if nivel > 0:
        for k in range(2):
            ortho = _unit(np.cross(d, [0.3, 0.1, 1.0] if k else [1.0, 0.2, 0.1]))
            nd = _unit(d + ortho * v.r.uniform(0.55, 1.0) * (1 if v.r.random() < 0.5 else -1))
            coral(v, base + d * largo * v.r.uniform(0.45, 0.85), nd, largo * v.r.uniform(0.5, 0.7), r * 0.75, nivel - 1,
                  cols, puntas)


def relieve(v, p, salvo=()):
    """Cubos que asoman de la superficie. Ya no se usa (se veian los cubos); se deja para probar."""
    if p < 1.0:
        return
    nuevos = {}
    for (x, y, z), c in v.d.items():
        if isinstance(c, str) or c in salvo or v.r.random() > p:
            continue
        libres = [(x + dx, y + dy, z + dz) for dx, dy, dz in _VECINOS if (x + dx, y + dy, z + dz) not in v.d]
        if libres:
            k = v.r.uniform(0.92, 1.12)
            nuevos[v.r.choice(libres)] = _q((c[0] * k, c[1] * k, c[2] * k, c[3]))
    v.d.update(nuevos)


# ----------------------------------------------------------------------
#  Colores
# ----------------------------------------------------------------------
def _luma(c):
    return c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11


def P(cols, pesos=None, esc=2.4):
    """Un color de la paleta por manchas de unos 'esc' voxeles (de oscuro a claro), no uno al azar por cubo."""
    orden = sorted(cols, key=_luma)
    n = len(orden)
    s = int(sum(orden[0][:3])) + n * 7

    def f(x, y, z, r):
        v = ruido(x + .5, y + .5, z + .5, esc, s)
        return orden[min(n - 1, int(max(0.0, (v - 0.2) / 0.6) * n))]
    return f


def escamas(base, claro, oscuro, w=4, h=3):
    """Escamas pintadas de 'w' de ancho en hileras de 'h': la luz arriba en medio y la junta oscura abajo; el color
    de fondo, por manchas."""
    fondo = P(base)
    luz = sorted(claro, key=_luma)[len(claro) // 2]
    junta = sorted(oscuro, key=_luma)[0]

    def f(x, y, z, r):
        fila = y // h
        u = (x + z + (fila % 2) * (w // 2)) % w
        v = y % h
        if v == h - 1 and u != w // 2:
            return junta
        if v == 0 and 0 < u < w - 1:
            return luz
        return fondo(x, y, z, r)
    return f


JADE = Hs('0f4a32', '16603f', '1c7a4c', '23925a', '2fab6a')
JADE_CLARO = Hs('4cc884', '7ee0a8', '5ad494')
JADE_OSC = Hs('0a3424', '0d4030')
ORO = Hs('b07a18', 'd09a22', 'e8b834', 'f2c844')
ORO_CLARO = Hs('f8d65c', 'fff0a0')
ORO_OSC = Hs('8a5a10', '6a4410')
PIEL = Hs('6e3e1e', '824a24', '7a4422', '95582c')
CUERO = Hs('2e1a0e', '3c2414', '4c2e18', '5c3a1e')
OBS = Hs('0c0a12', '16121e', '221a2e', '2e2440')
ROJO = Hs('8a1a14', 'b0281c', 'd0402a')
MADERA = Hs('3e2814', '54361c', '6a4626')


# ======================================================================
#  MOCTEZUMA, el Guerrero Aguila de Jade
# ======================================================================
def _pierna_moctezuma(s, nombre):
    """Pierna de guerrero: muslo ancho arriba con el cuadriceps marcado, rodillera de oro, greba de jade por delante y
    el gemelo abultado por detras, tobillo fino."""
    muslo = Vox(11 + s)
    poli(muslo, [(0, 0, 0), (0, 5.5, -0.4), (0, 12.5, 0)], [3.7, 3.4, 2.4], P(PIEL))
    elipsoide(muslo, (s * 0.5, 5.0, -1.3), (2.9, 4.8, 2.4), P(PIEL))
    anillo(muslo, 0, 3, 2.6, 4.1, P(CUERO))
    anillo(muslo, 10, 12, 2.0, 3.1, P(ORO))
    rodilla = Vox(21 + s)
    elipsoide(rodilla, (0, 0.6, -2.0), (2.7, 2.4, 1.8), P(ORO))
    caja(rodilla, -1, -0.4, -4.1, 1, 1.6, -3.3, 'mj_gema')
    greba = escamas(JADE, JADE_CLARO, JADE_OSC)
    poli(rodilla, [(0, 1.2, 0), (0, 5.0, 0.3), (0, 10.4, 0.2)], [2.7, 2.8, 1.8],
         lambda x, y, z, r: greba(x, y, z, r) if z < 0.5 else r.choice(PIEL))
    elipsoide(rodilla, (0, 4.4, 1.4), (2.5, 3.8, 2.3), P(PIEL))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        base = (math.cos(a) * 2.8, 1.8, math.sin(a) * 2.8)
        capsula(rodilla, base, (math.cos(a) * 4.8, 4.4, math.sin(a) * 4.8), 0.7, 0.35, P(JADE_CLARO if k % 2 else JADE))
    anillo(rodilla, 9, 11, 1.2, 2.5, P(ORO))
    pie = Vox(31 + s)
    caja(pie, -2.9, 0, -6.0, 2.9, 2.6, 2.4, P(CUERO))
    caja(pie, -3.0, 0, -2.0, 3.0, 1.2, -0.8, P(ORO))
    caja(pie, -3.0, 0, -6.2, 3.0, 1.0, -5.2, P(JADE))
    return ['pierna_' + nombre, (3.7 * s, 1.0, 0), (0, 0, 0), muslo, [
        ['espinilla_' + nombre, (0, 12.5, 0), (0, 0, 0), rodilla, [
            ['pie_' + nombre, (0, 10.9, 0), (0, 0, 0), pie, []],
        ]],
    ]]


def _brazo_moctezuma(s, nombre, mano_hijos, antebrazo_hijos=()):
    """Brazo de guerrero: hombrera de jade sobre el deltoides, biceps y triceps, antebrazo grueso junto al codo con
    el brazal de jade, y la mano grande. Las plumas del hombro van en el torso (hombrera_)."""
    hombro = Vox(41 + s)
    elipsoide(hombro, (s * 0.6, -0.2, 0), (4.3, 3.7, 4.5), escamas(JADE, JADE_CLARO, JADE_OSC))
    anillo(hombro, 1, 3, 2.8, 4.6, P(ORO), cx=s * 0.6)
    caja(hombro, s * 0.6 - 1, -4.4, -1, s * 0.6 + 1, -3.2, 1, 'mj_gema')
    alas = Vox(46 + s)
    for k in range(9):
        a = math.radians(-60 + k * 15)
        d = (s * math.cos(a), math.sin(a), 0.12)
        cols = Hs('0e5a3c', '16804e', '22a060', '3cc07a', '9af0c0') if k % 3 else Hs('7a1410', 'b0281c', 'e05a30', 'f8d65c')
        tira(alas, (s * 3.8, -1.6, -1.6 + (k % 2) * 1.2), d, (0, 0, 1) if k % 2 else (0.2 * s, 0, 1), 10 + (k % 3) * 1.8,
             2.6, cols)
    brazo = Vox(51 + s)
    poli(brazo, [(0, 0, 0), (0, 4.6, 0), (0, 9.5, 0)], [2.9, 3.0, 2.3], P(PIEL))
    elipsoide(brazo, (0, 4.8, -1.2), (2.4, 3.4, 2.0), P(PIEL))
    elipsoide(brazo, (0, 4.2, 1.2), (2.3, 3.2, 1.8), P(PIEL))
    anillo(brazo, 1, 3, 2.0, 3.2, P(ORO))
    caja(brazo, -0.8, 1.2, -3.6, 0.8, 2.6, -2.8, 'mj_gema')
    antebrazo = Vox(61 + s)
    poli(antebrazo, [(0, 0, 0), (0, 2.8, -0.2), (0, 9.0, 0)], [2.5, 2.9, 2.0], escamas(JADE, JADE_CLARO, JADE_OSC))
    anillo(antebrazo, 1, 2, 2.0, 3.3, P(ORO))
    anillo(antebrazo, 7, 9, 1.4, 2.6, P(ORO))
    for k in range(5):
        tira(antebrazo, (s * 2.8, 1.5 + k * 1.0, -1 + k * 0.5), (s * 0.6, 1, 0.2), (0, 0.2, 1), 5.0, 1.7,
             Hs('16804e', '3cc07a', '9af0c0'))
    mano = Vox(71 + s)
    elipsoide(mano, (0, 2.0, 0), (2.7, 2.7, 2.7), P(PIEL))
    caja(mano, -2.2, 3.2, -2.6, 2.2, 4.4, -1.4, P(PIEL[2:]))
    return ['hombro_' + nombre, (10.4 * s, -16.6, 0), (0, 0, 0), hombro, [
        ['brazo_' + nombre, (0.6 * s, 2.0, 0), (0, 0, 0), brazo, [
            ['antebrazo_' + nombre, (0, 9.5, 0), (0, 0, 0), antebrazo, [
                *antebrazo_hijos,
                ['mano_' + nombre, (0, 9.0, 0), (0, 0, 0), mano, mano_hijos],
            ]],
        ]],
    ]], ['hombrera_' + nombre, (10.4 * s, -16.6, 0), (0, 0, 0), alas, []]


def _escudo():
    """El chimalli: aro de oro con cuadros de jade, un anillo de obsidiana, el campo de jade con grecas de oro y, en
    medio, la cara de oro (ojos de jade, la boca de obsidiana con dientes). Lo de oro asoma un voxel."""
    v = Vox(81)
    R = 9.6
    for x in rango(-R, R):
        for y in rango(-R, R):
            px, py = x + .5, y + .5
            d = math.hypot(px, py)
            if d > R:
                continue
            a = math.atan2(py, px)
            sale = False
            if d > 8.4:
                c = H('e8b834') if int((a + math.pi) / (2 * math.pi) * 28) % 2 else H('1c7a4c')
                sale = True
            elif d > 7.4:
                c = v.r.choice(OBS)
            elif d > 4.6:
                seg = int((a + math.pi) / (2 * math.pi) * 12)
                u = ((a + math.pi) / (2 * math.pi) * 12) % 1
                w = (d - 4.6) / 2.8
                greca = (u < 0.5 and (w < 0.34 or (0.33 < u < 0.5 and w < 0.7))) or \
                        (u >= 0.5 and (w > 0.66 or (0.5 <= u < 0.67 and w > 0.3)))
                c = v.r.choice(ORO) if greca else v.r.choice(JADE if seg % 2 else JADE_OSC + JADE[:2])
                sale = greca
            else:
                # La cara.
                c = v.r.choice(ORO)
                sale = True
                if 0.8 <= abs(px) <= 2.8 and -2.2 <= py <= -0.6:
                    c = 'mj_gema'
                elif abs(px) <= 2.4 and 1.4 <= py <= 2.6:
                    c, sale = v.r.choice(OBS), False
                    if int(px + 10) % 2 == 0 and py < 2.0:
                        c, sale = H('fff0a0'), True
                elif abs(px) < 0.8 and -0.6 < py < 1.2:
                    c = H('f8d65c')
                elif d > 3.9:
                    c, sale = v.r.choice(ORO_OSC), False
            v.pon(x, y, 0, c)
            if sale:
                v.pon(x, y, -1, c)
            v.pon(x, y, 1, v.r.choice(CUERO))
    # Un borde de plumas cortas por la mitad de abajo del aro (cortas: con el brazo delante no tapan la cara).
    for k in range(9):
        a = math.radians(20 + k * 17.5)
        d = (math.cos(a), math.sin(a), 0)
        tira(v, (math.cos(a) * 9.2, math.sin(a) * 9.2, 0.4), d, (-math.sin(a), math.cos(a), 0), 3.6 + (k % 2) * 1.2, 1.8,
             Hs('7a1410', 'b0281c', 'e05a30', 'f8d65c') if k % 2 else Hs('0e5a3c', '22a060', '9af0c0'))
    return ['escudo', (3.0, 3.2, 0), (0, -90, 0), v, []]


def _macuahuitl():
    v = Vox(91)
    capsula(v, (0, -3, 0), (0, 5.5, 0), 1.0, 1.0, P(MADERA))
    for y0 in (-2, 3):
        anillo(v, y0, y0 + 1, 0.4, 1.6, P(ORO))
    elipsoide(v, (0, -4.2, 0), (1.6, 1.4, 1.6), P(ORO))
    caja(v, -2.6, 5, -1.0, 2.6, 29, 1.0, lambda x, y, z, r: r.choice(ORO) if x in (-3, 2) and y % 4 == 0
         else r.choice(JADE + JADE_CLARO[:1]))
    caja(v, -0.5, 7, -1.4, 0.5, 27, -1.0, 'mj_gema')
    caja(v, -0.5, 7, 1.0, 0.5, 27, 1.4, 'mj_gema')
    for y in range(6, 29, 2):
        largo = 1.8 + (y % 4 == 0) * 0.6
        caja(v, -2.6 - largo, y, -0.6, -2.6, y + 1.4, 0.6, P(OBS + [H('6a50a0')]))
        caja(v, 2.6, y, -0.6, 2.6 + largo, y + 1.4, 0.6, P(OBS + [H('6a50a0')]))
    elipsoide(v, (0, 30, 0), (2.4, 2.2, 0.9), P(OBS))
    return ['macuahuitl', (0, 2.6, 0), (0, 0, 0), v, []]


@functools.lru_cache(None)
def moctezuma():
    """Cuerpo heroico (proporciones de figura heroica, unas 7 cabezas sin el penacho): hombros de casi 3 cabezas,
    pecho ancho y cintura estrecha (en V), piernas largas, brazos que llegan a medio muslo."""
    pelvis = Vox(1)
    for y in range(-3, 1):
        for x in rango(-6.8, 6.8):
            for z in rango(-4.7, 4.7):
                if ((x + .5) / 6.8) ** 2 + ((z + .5) / 4.7) ** 2 <= 1:
                    pelvis.pon(x, y, z, P(ORO) if y in (-3, 0) or (x + z) % 4 == 0 else P(CUERO))
    elipsoide(pelvis, (0, 2.2, 0.3), (6.2, 3.4, 4.4), P(CUERO))
    caja(pelvis, -2.6, -3.6, -5.6, 2.6, 0.6, -4.2, P(ORO))
    caja(pelvis, -1, -2.4, -6.2, 1, -0.4, -5.4, 'mj_gema')

    def taparrabo(x, y, z, r):
        if y in (5, 6):
            return r.choice(JADE)
        if y in (11, 12):
            return r.choice(ORO)
        if abs(x + .5) < 1 and y > 2:
            return r.choice(ROJO)
        return r.choice(CUERO)
    with pelvis.grupo('faldon_frente'):
        caja(pelvis, -3.4, 1, -5.2, 3.4, 16, -4.0, taparrabo)
    with pelvis.grupo('faldon_atras'):
        caja(pelvis, -3.4, 1, 4.2, 3.4, 18, 5.4, taparrabo)
    for x in range(-3, 3):
        largo = 2 + (x % 2) * 2
        with pelvis.grupo('faldon_frente'):
            caja(pelvis, x, 16, -5.2, x + 1, 16 + largo, -4.2, P(JADE_CLARO if x % 2 else ORO))
        with pelvis.grupo('faldon_atras'):
            caja(pelvis, x, 18, 4.4, x + 1, 18 + largo, 5.4, P(JADE_CLARO if x % 2 else ORO))
    for s in (1, -1):
        for k in range(5):
            tira(pelvis, (s * 6.6, 0, -2.6 + k * 1.3), (s * 0.35, 1, 0), (0, 0, 1), 8 + (k % 2) * 2.4, 2.2,
                 Hs('0e5a3c', '16804e', '22a060', '3cc07a', '9af0c0'))

    torso = Vox(2)

    def abdomen(x, y, z, r):
        # Los abdominales: surcos un poco mas oscuros, el central y uno cada 3 filas.
        if z + .5 < -3.2 and (abs(x + .5) < 0.6 or y % 3 == 0):
            return r.choice(PIEL[:1])
        return r.choice(PIEL[1:])
    elipsoide(torso, (0, -3.8, 0.3), (5.9, 5.0, 4.3), abdomen)
    coraza = escamas(JADE, JADE_CLARO, JADE_OSC)

    def pecho(x, y, z, r):
        if z + .5 < -2.2 or abs(x + .5) > 6.4:
            return coraza(x, y, z, r)
        return r.choice(CUERO)
    elipsoide(torso, (0, -12.6, 0.2), (9.4, 7.0, 5.5), pecho)
    for s in (1, -1):
        elipsoide(torso, (s * 3.9, -13.4, -3.0), (4.1, 3.3, 2.7), pecho)
        capsula(torso, (s * 2.4, -18.8, 0.6), (s * 8.8, -17.2, 0.6), 2.7, 2.3, coraza)
    anillo(torso, -1, 1, 4.4, 6.6, P(ORO), kz=0.72)
    for x in rango(-3.9, 3.9):
        for y in rango(-16.5, -8.7):
            px, py = x + .5, y + .5 + 12.6
            d = math.hypot(px, py)
            if d > 3.9:
                continue
            if d > 3.0:
                c = P(ORO)
            elif d > 2.2:
                c = P(JADE_OSC)
            elif abs(px) < 0.9 or abs(py) < 0.9:
                c = 'mj_gema'
            else:
                c = P(ORO_CLARO)
            torso.pon(x, y, -6.2, c)
            torso.pon(x, y, -7.2, c)
    for t in np.linspace(-1.25, 1.25, 28):
        x, y, z = 7.0 * math.sin(t), -19.0 + 3.8 * (1 - math.cos(t)) * 1.3, -4.6 - 1.0 * math.cos(t)
        caja(torso, x - 0.9, y - 0.9, z - 0.8, x + 0.9, y + 0.9, z + 0.6, P(ORO) if int((t + 2) * 8) % 2 else P(JADE_CLARO))
    for k in range(11):
        tira(torso, (-7.5 + k * 1.5, -19, 5.2 + (k % 2) * 0.6), (0, 1, 0.12), (1, 0, 0), 19 + (k % 3) * 2.4, 2.5,
             Hs('0b4a30', '12663f', '1c8a52', '2fab6a', '9af0c0') if k % 4 else Hs('6a1410', '9a2018', 'd04a28', 'f8d65c'))

    cuello = Vox(3)
    capsula(cuello, (0, 0.5, 0), (0, -2.6, 0), 2.7, 2.6, P(PIEL))
    anillo(cuello, -1, 1, 2.0, 3.3, P(ORO))

    cabeza = Vox(4)
    elipsoide(cabeza, (0, -4.4, -0.2), (3.4, 4.1, 3.4), P(PIEL))
    hueco = lambda x, y, z: not (z < -1.0 and y > -6.4 and abs(x) < 3.3)
    pluma_yelmo = escamas(Hs('0e5a3c', '16804e', '1c8a52', '22a060'), Hs('3cc07a', '6ad898'), JADE_OSC)
    elipsoide(cabeza, (0, -8.0, 0.8), (5.8, 5.6, 6.4), pluma_yelmo, hueco)
    caja(cabeza, -4.6, -7.6, -5.4, 4.6, -6.4, -3.6, P(ORO))
    caja(cabeza, -6.0, -10.4, -3.4, -5.0, -8.4, -1.4, 'mj_ojo_oro')
    caja(cabeza, 5.0, -10.4, -3.4, 6.0, -8.4, -1.4, 'mj_ojo_oro')
    caja(cabeza, -2.4, -5.4, -3.8, -1.0, -4.4, -3.2, 'mj_ojo_jade')
    caja(cabeza, 1.0, -5.4, -3.8, 2.4, -4.4, -3.2, 'mj_ojo_jade')
    caja(cabeza, -3.2, -3.6, -3.7, 3.2, -2.9, -3.2, P(JADE))
    for s in (1, -1):
        elipsoide(cabeza, (s * 4.8, -4.0, 0.2), (1.0, 1.7, 1.7), P(ORO))
        caja(cabeza, s * 4.8 - 0.5, -4.6, -0.5, s * 4.8 + 0.5, -3.4, 0.5, 'mj_gema')

    pico = Vox(5)
    poli(pico, [(0, -0.8, 1.0), (0, -1.0, -2.6), (0, 0.4, -5.4), (0, 2.8, -6.8), (0, 4.8, -6.2)], [3.3, 2.9, 2.2, 1.4, 0.7],
         lambda x, y, z, r: r.choice(ORO_CLARO) if y < -1 else r.choice(ORO))
    caja(pico, -2.2, -0.6, -3.4, -1.2, 0.4, -2.4, P(OBS))
    caja(pico, 1.2, -0.6, -3.4, 2.2, 0.4, -2.4, P(OBS))
    caja(pico, -0.6, 4.6, -7.0, 0.6, 5.8, -5.8, P(ORO_OSC))

    penacho = Vox(6)
    for i in range(19):
        a = math.radians(-112 + i * (224 / 18))
        d = (math.sin(a), -math.cos(a), 0.0)
        lado = (math.cos(a), math.sin(a), 0.0)
        largo = 15 + 9 * (1 - abs(i - 9) / 9)
        cols = Hs('0b4a30', '12663f', '1c8a52', '2fab6a', '6ad898', 'c8ffd8')
        if i % 4 == 2:
            cols = Hs('0b4a30', '12663f', '1c8a52', '2fab6a', 'f8d65c')
        tira(penacho, np.array(d) * 1.6 + [0, 0, (i % 2) * 1.0], d, lado, largo, 3.2, cols)
    for i in range(13):
        a = math.radians(-96 + i * 16)
        d = (math.sin(a), -math.cos(a), 0.0)
        tira(penacho, np.array(d) * 1.2 + [0, 0, -1.4], d, (math.cos(a), math.sin(a), 0), 10 + 3 * (1 - abs(i - 6) / 6), 2.6,
             Hs('0e5a50', '138070', '1aa088', '34c0a0', '9af0d8'))
    for i in range(9):
        a = math.radians(-80 + i * 20)
        d = (math.sin(a), -math.cos(a), 0.0)
        tira(penacho, np.array(d) * 1.0 + [0, 0, -2.6], d, (math.cos(a), math.sin(a), 0), 6 + 2 * (1 - abs(i - 4) / 4), 2.2,
             Hs('6a1410', '9a2018', 'd04a28', 'f8d65c'))
    elipsoide(penacho, (0, 0, -1.4), (2.6, 2.6, 1.6), P(ORO))
    caja(penacho, -1, -1, -3.4, 1, 1, -2.6, 'mj_gema')

    return ['raiz', (0, 0, 0), (0, 0, 0), None, [
        ['pelvis', (0, -3, 0), (0, 0, 0), pelvis, [
            _pierna_moctezuma(1, 'izq'), _pierna_moctezuma(-1, 'der'),
            ['torso', (0, -2, 0), (0, 0, 0), torso, [
                ['cuello', (0, -19.4, 0), (0, 0, 0), cuello, [
                    ['cabeza', (0, -2.4, 0), (0, 0, 0), cabeza, [
                        ['pico', (0, -7.8, -5.0), (0, 0, 0), pico, []],
                        ['penacho', (0, -10.6, 3.6), (-16, 0, 0), penacho, []],
                    ], 0.88],
                ]],
                *_brazo_moctezuma(1, 'izq', [], [['escudo', (3.4, 3.8, 0), (0, -90, 0), _escudo()[3], [], 1.15]]),
                *_brazo_moctezuma(-1, 'der', [_macuahuitl()]),
            ]],
        ]],
    ]]


# El macuahuitl, por delante y hacia arriba como la espada de un jugador (Juan, 11-10-2026: "su espada tiene que estar
# adelante como un jugador con su espada, no teniendolo atras").
MOCTEZUMA_REPOSO = {
    'hombro_izq': {'rot': (-30, 0, -8)}, 'antebrazo_izq': {'rot': (-50, 0, 0)},
    'hombro_der': {'rot': (-22, 0, 10)}, 'antebrazo_der': {'rot': (-48, 0, 0)}, 'macuahuitl': {'rot': (-72, 0, 0)},
}
MOCTEZUMA_HEROICA = {
    'pelvis': {'rot': (0, 18, 0)},
    'torso': {'rot': (8, -16, 0)},
    'cabeza': {'rot': (-8, -6, 0)},
    'pierna_izq': {'rot': (-28, 0, -6)}, 'espinilla_izq': {'rot': (34, 0, 0)}, 'pie_izq': {'rot': (-6, 0, 0)},
    'pierna_der': {'rot': (24, 0, 8)}, 'espinilla_der': {'rot': (20, 0, 0)}, 'pie_der': {'rot': (-30, 0, 0)},
    'hombro_izq': {'rot': (-75, 20, -10)}, 'antebrazo_izq': {'rot': (-40, 0, 0)},
    'hombro_der': {'rot': (-40, 0, 115)}, 'antebrazo_der': {'rot': (-50, 0, 0)}, 'macuahuitl': {'rot': (50, 0, 0)},
}


# ======================================================================
#  YIATZO, el Mago del Viento
# ======================================================================
GRIS = Hs('b4b8bc', 'a4a8ae', '969aa2')
GRIS_MED = Hs('868a92', '7a7e86')
GRIS_OSC = Hs('5e626a', '52565e', '484c54')
CARBON = Hs('2a2c32', '34363c', '3e4048')
PLATA = Hs('9ca4ac', 'c0c8d0', 'e2e8ee')
CIAN = H('7ae0ff', 1.0)
CIAN_SUAVE = H('48b8e8', 0.4)


_GRISES = sorted(GRIS_OSC + GRIS_MED + GRIS, key=lambda c: c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11)


def _tunica(x, y, z, r):
    # Los pliegues van en bandas suaves (claro en el lomo, oscuro en el fondo) con manchas grandes de desgaste.
    a = math.atan2(z + .5, x + .5)
    k = math.cos(a * 9 + y * 0.05)
    v = 0.52 + 0.34 * k + (ruido(x, y, z, 3.2, 11) - 0.5) * 0.3
    return _GRISES[min(len(_GRISES) - 1, max(0, int(v * len(_GRISES))))]


def _glifo(i, x, y):
    """Unos glifos de viento de 4 x 4: espirales, flechas y remolinos."""
    g = [
        ['1111', '1001', '1011', '1000'],
        ['0110', '1001', '0110', '1001'],
        ['1010', '0101', '1010', '0111'],
        ['1110', '0010', '1110', '1000'],
        ['0100', '1110', '0100', '0101'],
    ][i % 5]
    return g[y % 4][x % 4] == '1'


def _brazo_yiatzo(s, nombre, mano_hijos):
    """El brazo del mago: largo y delgado, perdido en una manga que se abre en campana."""
    hombro = Vox(141 + s)
    elipsoide(hombro, (0, 0, 0), (3.2, 3.0, 3.4), _tunica)
    brazo = Vox(151 + s)
    capsula(brazo, (0, 0, 0), (0, 9.5, 0), 2.6, 3.2, _tunica)
    antebrazo = Vox(161 + s)
    capsula(antebrazo, (0, 0, 0), (0, 10.5, 0), 3.2, 5.8, _tunica,
            cond=lambda x, y, z: not (y > 8.0 and math.hypot(x, z) < 4.0))
    for (x, y, z) in list(antebrazo.d):
        d = math.hypot(x + .5, z + .5)
        if y >= 9 and d >= 4.2:
            ang = int((math.atan2(z + .5, x + .5) + math.pi) / (2 * math.pi) * 18)
            antebrazo.d[(x, y, z)] = _q(CIAN_SUAVE) if (ang + y) % 6 == 0 else _q(CARBON[1])
    for y in range(6, 11):
        for x in rango(-3.8, 3.8):
            for z in rango(-3.8, 3.8):
                if math.hypot(x + .5, z + .5) < 3.8:
                    antebrazo.pon(x, y, z, H('060708'), jitter=0)
    mano = Vox(171 + s)
    elipsoide(mano, (0, 1.8, 0), (1.7, 2.4, 1.7), Hs('a8aeb6', 'b8bec6', '9aa0a8'))
    for k in range(4):
        capsula(mano, (-1.2 + k * 0.8, 3.4, -0.6), (-1.4 + k * 0.9, 5.6, -0.9), 0.45, 0.35, Hs('a8aeb6', '9aa0a8'))
    return ['hombro_' + nombre, (8.8 * s, -23.4, 0.4), (0, 0, 0), hombro, [
        ['brazo_' + nombre, (0, 1.4, 0), (0, 0, 0), brazo, [
            ['antebrazo_' + nombre, (0, 9.5, 0), (0, 0, 0), antebrazo, [
                ['mano_' + nombre, (0, 9.2, 0), (0, 0, 0), mano, mano_hijos],
            ]],
        ]],
    ]]


def _baston():
    """El baston, alto como un hombre y medio: madera gris con anillos de plata; arriba, ramas talladas que suben en
    espiral y se cierran sobre el orbe de viento, con la jaula de plata y los cristales."""
    v = Vox(181)
    capsula(v, (0, -40, 0), (0, 26, 0), 1.1, 1.0, P(CARBON))
    for y0 in (-30, -18, 2, 14, 24):
        anillo(v, y0, y0 + 1, 0.3, 1.8, P(PLATA))
    for y in range(-26, 16, 6):
        v.pon(0, y, -1.3, CIAN_SUAVE)
    for k in range(3):
        f = k * 2 * math.pi / 3
        pts = [(math.cos(f + t * 2.2) * (1.4 + t * 3.4), -34 - t * 7, math.sin(f + t * 2.2) * (1.4 + t * 3.4))
               for t in np.linspace(0, 1, 8)]
        pts += [(math.cos(f + 2.2 + t * 1.2) * (4.8 - t * 3.6), -41 - t * 6, math.sin(f + 2.2 + t * 1.2) * (4.8 - t * 3.6))
                for t in np.linspace(0.15, 1, 5)]
        poli(v, pts, [0.9] * len(pts), P(CARBON + GRIS_OSC[:1]))
    caja(v, -2.4, -42, -2.4, 2.4, -40, 2.4, P(PLATA))
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        pts = [(dx * 1.8, -41.5, dz * 1.8), (dx * 4.8, -44.8, dz * 4.8), (dx * 4.4, -48.6, dz * 4.4), (dx * 1.6, -51.8, dz * 1.6)]
        poli(v, pts, [0.7, 0.7, 0.6, 0.5], P(PLATA))
        elipsoide(v, (dx * 6.2, -46.0, dz * 6.2), (1.0, 1.6, 1.0), CIAN)
    elipsoide(v, (0, -46.4, 0), (3.2, 3.4, 3.2), 'mj_orbe')
    poli(v, [(0, -51.8, 0), (0, -54.8, 0), (0, -57.6, 0)], [1.2, 0.8, 0.3], P(PLATA))
    v.pon(0, -58.2, 0, CIAN)
    return ['baston', (0, 1.8, 0), (0, 0, 0), v, []]


def _libro():
    v = Vox(191)
    caja(v, -5.2, -0.4, -3.6, 5.2, 0.6, 3.6, P(Hs('16203a', '1c2a48', '22324e')))
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0 = 4.0 if sx > 0 else -5.2
            z0 = 2.4 if sz > 0 else -3.6
            caja(v, x0, -0.6, z0, x0 + 1.2, 0.8, z0 + 1.2, P(PLATA))
    papel = Hs('cfc6ae', 'e4dcc4', 'd8d0b8')
    caja(v, -4.8, -1.6, -3.2, -0.3, -0.4, 3.2, P(papel))
    caja(v, 0.3, -1.6, -3.2, 4.8, -0.4, 3.2, P(papel))
    for x in range(-4, 5):
        for z in range(-3, 3):
            if x in (-1, 0):
                continue
            if _glifo(x + 4 + (z + 3) // 4, x + 4, z + 3) and (x * 3 + z) % 2 == 0:
                v.d[(x, -2, z)] = _q(CIAN)
    for x in range(-2, 2):
        for z in range(-2, 2):
            if abs(x + .5) > 1 or abs(z + .5) > 1:
                v.pon(x, -6, z, CIAN, jitter=0)
    return ['libro', (0, 3.6, -1.6), (-62, 0, 0), v, []]


def _losa_glifo(i, semilla):
    v = Vox(semilla)
    for x in range(-3, 3):
        for y in range(-3, 3):
            v.pon(x, y, 0, P(Hs('3a4048', '464c56', '2e343c')))
            if _glifo(i, x + 3, y + 3) and abs(x + .5) < 2.5 and abs(y + .5) < 2.5:
                v.pon(x, y, -1, CIAN, jitter=0)
    return v


@functools.lru_cache(None)
def yiatzo():
    """El mago: alto y delgado, un poco encorvado (la cabeza adelantada), con la tunica larga en pliegues
    verticales, el manto pesado sobre los hombros y la capa por detras hasta el suelo, el cinturon con bolsas y un
    estuche de pergaminos."""
    cuerpo = Vox(101)
    # La tunica, entera hasta las rodillas (y = 12); de ahi abajo, jirones (Juan, 11-10-2026: "no parece un mago
    # levitando, mas bien un trozo de pilar levitando... su parte de abajo esta muy tiesa").
    perfil = [(-26, 9.0, 6.0), (-22, 8.6, 5.8), (-12, 7.0, 5.0), (-4, 6.4, 4.8), (6, 8.4, 6.2), (12, 9.6, 7.0)]

    def radios(y):
        for (y0, a0, b0), (y1, a1, b1) in zip(perfil, perfil[1:]):
            if y0 <= y <= y1:
                t = (y - y0) / (y1 - y0)
                return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
        return perfil[-1][1:]
    for y in range(-26, 13):
        rx, rz = radios(y + .5)
        for x in rango(-rx - 1, rx + 1):
            for z in rango(-rz - 1, rz + 1):
                a = math.atan2(z + .5, x + .5)
                pliegue = 1 + (0.06 * math.cos(9 * a) if y > -6 else 0)
                if ((x + .5) / (rx * pliegue)) ** 2 + ((z + .5) / (rz * pliegue)) ** 2 > 1:
                    continue
                c = _tunica(x, y, z, cuerpo.r)
                if abs(x + .5) < 2.6 and z + .5 < 0:
                    c = P(CARBON, esc=4)(x, y, z, cuerpo.r)
                    fila = (y + 20) % 7
                    if y > -20 and fila < 4 and abs(x + .5) < 2 and _glifo((y + 20) // 7, x + 2, fila):
                        c = GRIS[1] if (y + 20) // 7 % 2 else CIAN_SUAVE
                elif 7 <= y <= 10:
                    ang = int((a + math.pi) / (2 * math.pi) * 60)
                    c = P(CARBON, esc=4)(x, y, z, cuerpo.r)
                    if ang % 7 < 4 and _glifo(ang // 7, ang % 7, y - 7):
                        c = GRIS[0] if (ang // 7) % 3 else CIAN_SUAVE
                cuerpo.pon(x, y, z, c)
    # El bajo: jirones de tela que cuelgan de las rodillas y se abren un poco, de largos distintos y en punta (los de
    # delante, el panel oscuro de las runas). El juego los separa en dos piezas (falda y falda2) que ondean.
    rxh, rzh = radios(11.5)
    n = 22
    for k in range(n):
        a = 2 * math.pi * k / n
        cx, cz = math.cos(a) * (rxh - 0.7), math.sin(a) * (rzh - 0.7)
        delante = math.sin(a) < -0.85
        largo = (16 if delante else 9) + (k * 7 % 5) * 1.7
        d = (math.cos(a) * 0.3, 1.0, math.sin(a) * 0.3 + 0.08)
        lado = (-math.sin(a), 0, math.cos(a))
        cols = ([CARBON[2], CARBON[1], CARBON[0], H('1e2026')] if delante else
                [_GRISES[len(_GRISES) // 2], _GRISES[len(_GRISES) // 3], GRIS_OSC[2], CARBON[1]])
        # Nacen bajo el bajo de la tunica (escondidos dentro hasta y = 12): al ondear, su raiz no se ve.
        tira(cuerpo, (cx, 9.0, cz), d, lado, largo + 1.5, 4.0, cols, punta=0.55, raquis=False)
        if delante:
            for j in range(3):
                cuerpo.pon(cx, 14 + j * 4, cz - 0.6, CIAN_SUAVE, jitter=0)
    rx, rz = radios(-4)
    anillo(cuerpo, -5, -3, rx - 1.0, rx + 0.7, P(CARBON), kz=rz / rx)
    caja(cuerpo, -1.8, -5.6, -rz - 1.4, 1.8, -2.4, -rz + 0.2, P(PLATA))
    caja(cuerpo, -0.6, -4.6, -rz - 1.8, 0.6, -3.4, -rz - 1.2, CIAN_SUAVE)
    for sx in (-1, 1):
        caja(cuerpo, sx * rx * 0.62 - 1.6, -3, -rz * 0.8 - 1.6, sx * rx * 0.62 + 1.6, 1.2, -rz * 0.8 + 1.0,
             P(Hs('3a2a20', '4a3628', '5a4230')))
    capsula(cuerpo, (rx - 0.4, -4.4, 1.4), (rx + 0.6, 4.6, 2.4), 1.3, 1.3, P(Hs('5a4230', '6a5038')))
    anillo(cuerpo, -3, -2, 0.2, 1.6, P(PLATA), cx=rx - 0.2, cz=1.6)
    for x in (-3.4, 2.6):
        capsula(cuerpo, (x, -3, -rz), (x + 0.4, 5, -rz - 0.8), 0.4, 0.4, P(CARBON))
        caja(cuerpo, x - 1, 5, -rz - 1.6, x + 1, 8, -rz - 0.8, P(Hs('3a4048', '464c56')))
        cuerpo.pon(x, 6.4, -rz - 2.0, CIAN, jitter=0)
    # El manto, pesado, sobre los hombros y el pecho, y la capa por detras hasta el suelo, rota.
    elipsoide(cuerpo, (0, -24.4, 0.4), (10.6, 4.2, 7.4), P(Hs('3a4250', '46505e', '525c6a')))
    caja(cuerpo, -1.8, -25.8, -8.2, 1.8, -22.2, -6.8, P(PLATA))
    caja(cuerpo, -0.6, -24.6, -8.6, 0.6, -23.4, -8.0, CIAN_SUAVE)
    for k in range(13):
        x0 = -9 + k * 1.5
        largo = 44 + (k * 7) % 5
        with cuerpo.grupo('capa'):
            tira(cuerpo, (x0, -25, 7.0 + abs(x0) * 0.12), (0, 1, 0.08 + abs(x0) * 0.004), (1, 0, 0), largo, 2.0,
                 [H('3a4250'), H('46505e'), H('3a4250'), H('2e3440')], raquis=False, punta=0.95)

    capucha = Vox(102)
    abierto = lambda x, y, z: not (z < -1.8 and abs(x) < 4.0 and -10.8 < y < -0.6)
    elipsoide(capucha, (0, -6.4, 0.2), (6.6, 7.4, 7.0), _tunica, abierto)
    for x in rango(-4.0, 4.0):
        for y in rango(-10.8, -0.6):
            capucha.pon(x, y, -1.8, H('050608'), jitter=0)
            capucha.pon(x, y, -0.8, H('050608'), jitter=0)
    for (x, y, z) in list(capucha.d):
        if z < -2 and abs(x + .5) < 5.5 and (abs(x + .5) in (4.5, 5.5) or y in (-11, -12)):
            capucha.d[(x, y, z)] = _q(GRIS[0])
    capucha.pon(-2, -6, -2, H('3a9ac8', 0.5), jitter=0)
    capucha.pon(1, -6, -2, H('3a9ac8', 0.5), jitter=0)
    poli(capucha, [(0, -12.6, 1.8), (0, -15.6, 4.6), (0, -16.6, 8.0), (0, -15.2, 10.8), (0, -12.6, 12.2)],
         [3.0, 2.4, 1.8, 1.1, 0.6], _tunica)

    piedras = []
    for i, (x, y, z, rx_, ry_, rz_) in enumerate(((17, -14, -6, 10, 30, 8), (-18, -2, 5, -12, 50, 20), (15, 10, -8, 30, 10, -16),
                                                   (-15, -26, -4, -20, -30, 10), (-16, 12, -7, 6, 64, -8))):
        piedras.append([f'piedra{i}', (x, y, z), (rx_, ry_, rz_), _losa_glifo(i, 200 + i), [], 1.3])

    return ['raiz', (0, 0, 0), (0, 0, 0), None, [
        ['cuerpo', (0, 0, 0), (0, 0, 0), cuerpo, [
            ['capucha', (0, -25.6, -1.0), (12, 0, 0), capucha, []],
            _brazo_yiatzo(-1, 'der', [_baston()]),
            _brazo_yiatzo(1, 'izq', [['libro', (0, 4.6, -1.8), (-62, 0, 0), _libro()[3], [], 1.25]]),
            *piedras,
        ]],
    ]]


YIATZO_REPOSO = {
    'hombro_der': {'rot': (-24, 0, 6)}, 'antebrazo_der': {'rot': (-38, 0, 0)}, 'baston': {'rot': (62, 0, 0)},
    'hombro_izq': {'rot': (-40, 0, -12)}, 'antebrazo_izq': {'rot': (-52, 0, 10)},
}
YIATZO_HEROICA = {
    'cuerpo': {'rot': (4, 14, 0)},
    'capucha': {'rot': (-6, -8, 0)},
    'hombro_der': {'rot': (-150, -10, 20)}, 'antebrazo_der': {'rot': (-10, 0, 0)}, 'baston': {'rot': (180, 0, 0)},
    'hombro_izq': {'rot': (-60, 10, -24)}, 'antebrazo_izq': {'rot': (-46, 0, 14)},
}


# ======================================================================
#  ATLAHUA, el Triton de las Profundidades
# ======================================================================
TEAL = Hs('0e4a5a', '146070', '1a7888', '22909e')
CYAN_ESC = Hs('2aa8b8', '3cc0cc', '5ad4dc')
AZUL = Hs('0a2a4a', '10385e', '164872', '0e3050')
ESPUMA = Hs('c8f0f0', 'e8fcfc')
NACAR = Hs('aeb4c8', 'c8d4e0', 'e2e6f0', 'd8c8e0', 'c8e0dc')
CORAL = Hs('a8241c', 'c8322a', 'e04a32', 'f06a3c')
CORAL_PUNTA = Hs('ff9a60', 'ffb080', 'ff7a8a')
ALGA = Hs('0e3a20', '14502c', '1c6a38', '2a8448')
PRISMA = Hs('2a7a70', '3a9688', '4ab0a0', '62c4b4')
_ESCAMA_MAR = escamas(TEAL[1:3] + AZUL[2:3], CYAN_ESC[:1], AZUL[:1], w=5, h=3)
_ESCAMA_PRISMA = escamas(PRISMA[:3], CYAN_ESC[:1], TEAL[:1], w=5, h=3)


_TELA_MAR = P(TEAL[1:3] + AZUL[2:3], esc=4.0)


def _mar(x, y, z, r):
    """La tela de mar del cuerpo: azules y verdes por manchas grandes, con alguna marca de luz."""
    if ruido(x, y, z, 2.2, 77) > 0.88:
        return H('70e0f0', 0.5)
    return _TELA_MAR(x, y, z, r)


def _brazo_atlahua(s, nombre, mano_hijos):
    """Brazo de rey del mar: hombrera de prisma con coral y percebes, biceps y antebrazo gruesos con el brazal de
    nacar y la aleta, mano grande con garras."""
    hombro = Vox(341 + s)
    elipsoide(hombro, (s * 0.8, -0.6, 0), (5.0, 3.8, 5.2), _ESCAMA_PRISMA)
    anillo(hombro, 1, 3, 3.2, 5.6, P(NACAR), cx=s * 0.8)
    for k in range(5):
        a = k / 5 * 2 * math.pi + s
        base = (s * 0.8 + math.cos(a) * 2.6, -3.6, math.sin(a) * 2.8)
        coral(hombro, base, (s * 0.5 + math.cos(a) * 0.4, -1, math.sin(a) * 0.4), 7.5 + k % 2 * 2.5, 1.1, 2, P(CORAL),
              P(CORAL_PUNTA))
    brazo = Vox(351 + s)
    poli(brazo, [(0, 0, 0), (0, 4.8, 0), (0, 9.5, 0)], [3.1, 3.2, 2.5], _mar)
    elipsoide(brazo, (0, 4.8, -1.3), (2.6, 3.4, 2.1), _mar)
    antebrazo = Vox(361 + s)
    poli(antebrazo, [(0, 0, 0), (0, 3.0, -0.2), (0, 9.0, 0)], [2.7, 3.0, 2.2], _mar)
    anillo(antebrazo, 2, 5, 2.4, 3.6, P(NACAR))
    tira(antebrazo, (s * 3.0, 0.8, 0), (s * 0.35, 1, 0), (0, 0, 1), 9.0, 4.6, Hs('0e5068', '1a7890', '3ab0c8', '8ae8f0'),
         raquis=False)
    mano = Vox(371 + s)
    elipsoide(mano, (0, 2.0, 0), (2.8, 2.6, 2.8), P(TEAL))
    for dx in (-1.8, 0, 1.8):
        capsula(mano, (dx, 4.0, -1.4), (dx * 1.1, 6.2, -2.2), 0.6, 0.35, P(ESPUMA))
    return ['hombro_' + nombre, (11.2 * s, -17.2, 0), (0, 0, 0), hombro, [
        ['brazo_' + nombre, (0.4 * s, 2.2, 0), (0, 0, 0), brazo, [
            ['antebrazo_' + nombre, (0, 9.5, 0), (0, 0, 0), antebrazo, [
                ['mano_' + nombre, (0, 9.0, 0), (0, 0, 0), mano, mano_hijos],
            ]],
        ]],
    ]]


def _pierna_atlahua(s, nombre):
    muslo = Vox(381 + s)
    poli(muslo, [(0, 0, 0), (0, 5.5, -0.3), (0, 12.3, 0)], [3.9, 3.6, 2.6], _mar)
    elipsoide(muslo, (s * 0.5, 5.0, -1.3), (3.0, 4.8, 2.5), _mar)
    espinilla = Vox(391 + s)
    poli(espinilla, [(0, 0, 0), (0, 4.6, 0.3), (0, 10.4, 0)], [2.8, 2.9, 2.0], _ESCAMA_PRISMA)
    elipsoide(espinilla, (0, 4.2, 1.5), (2.6, 3.8, 2.3), _mar)
    anillo(espinilla, 0, 2, 2.2, 3.3, P(NACAR))
    tira(espinilla, (0, 1.6, 2.6), (0, 1, 0.3), (0, 0, 1), 8.0, 4.0, Hs('0e5068', '1a7890', '3ab0c8', '8ae8f0'), raquis=False)
    pie = Vox(401 + s)
    caja(pie, -3.0, 0, -5.6, 3.0, 2.6, 2.4, P(AZUL))
    for dx in (-2.4, -0.5, 1.4):
        capsula(pie, (dx + 0.5, 1.2, -5.4), (dx + 0.5, 2.0, -7.4), 0.6, 0.35, P(ESPUMA))
    return ['pierna_' + nombre, (3.9 * s, 1.2, 0), (0, 0, 0), muslo, [
        ['espinilla_' + nombre, (0, 12.3, 0), (0, 0, 0), espinilla, [
            ['pie_' + nombre, (0, 10.9, 0), (0, 0, 0), pie, []],
        ]],
    ]]


def _tridente():
    v = Vox(311)
    capsula(v, (0, -27, 0), (0, 21, 0), 1.0, 1.0, P(Hs('16222e', '1e3040', '263a4e')))
    for y in np.arange(-22, 14, 0.5):
        a = y * 0.9
        v.pon(math.cos(a) * 1.3, y, math.sin(a) * 1.3, P(CORAL))
    for y0 in (-24, -10, 6, 18):
        anillo(v, y0, y0 + 1, 0.4, 1.7, P(NACAR))
    caja(v, -6.4, -29.8, -1.2, 6.4, -27.4, 1.2, _ESCAMA_PRISMA)
    for s in (1, -1):
        poli(v, [(s * 5.4, -29.6, 0), (s * 5.8, -35.0, 0), (s * 5.2, -38.4, 0)], [1.0, 0.9, 0.7], P(PRISMA))
        elipsoide(v, (s * 5.2, -40.4, 0), (1.0, 2.0, 1.0), 'mj_punta_coral')
        coral(v, (s * 4.0, -29.8, 0.6), (s * 0.6, -1, 0.4), 3.6, 0.6, 1, P(CORAL), P(CORAL_PUNTA))
    poli(v, [(0, -29.6, 0), (0, -38, 0), (0, -41, 0)], [1.2, 1.0, 0.8], P(PRISMA))
    elipsoide(v, (0, -43.4, 0), (1.1, 2.6, 1.1), 'mj_punta_coral')
    elipsoide(v, (0, -28.6, -1.6), (1.1, 1.1, 1.1), 'mj_senuelo')
    coral(v, (-1.4, -27.6, 1.0), (-0.3, 1, 0.3), 3.4, 0.6, 1, P(CORAL), P(CORAL_PUNTA))
    return ['tridente', (0, 1.8, 0), (0, 0, 0), v, []]


@functools.lru_cache(None)
def atlahua():
    """El rey del mar: mas ancho y pesado que Moctezuma, con el cuello grueso, los hombros enormes cargados de coral,
    el faldon de escamas hasta las rodillas y la capa de algas hasta los tobillos."""
    pelvis = Vox(301)
    for y in range(-2, 15):
        rx, rz = 6.8 + (y + 2) * 0.17, 5.0 + (y + 2) * 0.14
        for x in rango(-rx, rx):
            for z in rango(-rz, rz):
                a = math.atan2(z + .5, x + .5)
                if ((x + .5) / rx) ** 2 + ((z + .5) / rz) ** 2 > 1:
                    continue
                if y >= 12 and int((a + math.pi) * 6) % 3 == 0:
                    continue
                c = _mar(x, y, z, pelvis.r)
                if y % 5 == 4:
                    c = pelvis.r.choice(NACAR[:2] + CYAN_ESC[:1])
                pelvis.pon(x, y, z, c)
    anillo(pelvis, -3, -1, 6.0, 7.4, P(NACAR), kz=0.75)
    elipsoide(pelvis, (0, -2, -6.0), (2.0, 1.8, 1.0), P(CORAL))
    for k in range(12):
        a = k / 12 * 2 * math.pi + 0.3
        x0, z0 = math.cos(a) * 7.0, math.sin(a) * 5.3
        pts = [(x0 + math.sin(t * 1.3 + k) * 0.6, -1 + t * 2.6, z0) for t in range(6 + k % 3)]
        poli(pelvis, pts, [0.6] * len(pts), P(ALGA))

    torso = Vox(302)
    elipsoide(torso, (0, -3.8, 0.3), (6.6, 5.2, 4.8), _mar)
    elipsoide(torso, (0, -13.0, 0.2), (10.2, 7.4, 5.9), _mar)
    for s in (1, -1):
        elipsoide(torso, (s * 4.2, -13.6, -3.2), (4.4, 3.5, 2.8), _mar)
        capsula(torso, (s * 2.6, -19.6, 0.6), (s * 9.6, -17.8, 0.6), 3.2, 2.6, _ESCAMA_PRISMA)
    for x in rango(-4.2, 4.2):
        for y in rango(-17, -8):
            px, py = x + .5, y + .5 + 12.6
            if py > 3.8 or math.hypot(px, py + 1) > 4.6:
                continue
            ang = math.atan2(px, py + 3.8)
            costilla = abs(math.sin(ang * 7)) < 0.4
            torso.pon(x, y, -6.2, P(NACAR) if costilla else P(NACAR[:2]))
            if costilla:
                torso.pon(x, y, -7.0, P(NACAR))
    elipsoide(torso, (0, -12.2, -7.4), (1.1, 1.1, 0.9), 'mj_senuelo')
    for t in np.linspace(-1.2, 1.2, 24):
        x, y, z = 7.4 * math.sin(t), -20.4 + 3.6 * (1 - math.cos(t)) * 1.2, -4.8 - 0.9 * math.cos(t)
        caja(torso, x - 0.9, y - 0.9, z - 0.7, x + 0.9, y + 0.9, z + 0.5, P(NACAR) if int((t + 2) * 7) % 2 else P(CYAN_ESC))
    for k in range(10):
        with torso.grupo('capa'):
            tira(torso, (-8.1 + k * 1.8, -20, 5.6 + (k % 2) * 0.6), (0, 1, 0.1), (1, 0, 0), 38 + (k % 3) * 3, 2.7,
                 Hs('0a2a3a', '0e4a5a', '146070', '1c6a38', '2a8448') if k % 2 else Hs('0a2a4a', '10385e', '1a7888', '3cc0cc'),
                 raquis=False)

    cuello = Vox(303)
    capsula(cuello, (0, 0.5, 0), (0, -2.8, 0), 3.2, 3.0, _mar)

    cabeza = Vox(304)
    elipsoide(cabeza, (0, -5.2, 0), (4.5, 5.2, 4.7), lambda x, y, z, r: r.choice(PRISMA) if z < -2 else _mar(x, y, z, r))
    caja(cabeza, -4.2, -7.6, -5.2, 4.2, -6.6, -3.6, P(NACAR))
    caja(cabeza, -3.2, -6.4, -5.0, -1.2, -5.2, -4.0, 'mj_ojo_abismo')
    caja(cabeza, 1.2, -6.4, -5.0, 3.2, -5.2, -4.0, 'mj_ojo_abismo')
    caja(cabeza, -0.6, -5.0, -5.4, 0.6, -2.6, -4.4, P(TEAL))
    anillo(cabeza, -10, -8, 3.4, 4.9, P(NACAR))
    for k in range(9):
        a = k / 9 * 2 * math.pi + 0.35
        base = (math.cos(a) * 4.0, -9.6, math.sin(a) * 4.0)
        coral(cabeza, base, (math.cos(a) * 0.55, -1, math.sin(a) * 0.55), 7.0 + (k % 3) * 2.2, 1.05, 2,
              P(CORAL if k % 3 else Hs('d04a8a', 'e06aa0', 'c03a70')), P(CORAL_PUNTA))
    for dx in (-1.6, 0, 1.6):
        poli(cabeza, [(dx, -9.6, -4.0), (dx * 1.2, -13.0 - (dx == 0) * 2, -4.4)], [0.8, 0.4], H('6ae8ff', 0.7))
    for s in (1, -1):
        tira(cabeza, (s * 4.2, -5.4, 0), (s * 1, -0.4, 0.4), (0, 1, 0.3), 4.6, 4.0, Hs('0e5068', '1a7890', '3ab0c8', '8ae8f0'),
             raquis=False)

    mandibula = Vox(305)
    caja(mandibula, -3.4, 0, -4.6, 3.4, 2.2, 0.6, P(PRISMA))
    caja(mandibula, -3.0, -0.6, -4.8, 3.0, 0.2, -4.0, P(ESPUMA))
    for k in range(11):
        x0 = -3.4 + k * 0.68
        largo = 7 + (5 - abs(k - 5)) * 1.1
        pts = [(x0 + math.sin(t * 0.9 + k) * 0.5, 2 + t * 1.6, -4.0 + t * 0.15) for t in range(int(largo / 1.6) + 1)]
        poli(mandibula, pts, [0.55] * len(pts), P(ALGA + TEAL[:1]))

    return ['raiz', (0, 0, 0), (0, 0, 0), None, [
        ['pelvis', (0, -3, 0), (0, 0, 0), pelvis, [
            _pierna_atlahua(1, 'izq'), _pierna_atlahua(-1, 'der'),
            ['torso', (0, -2, 0), (0, 0, 0), torso, [
                ['cuello', (0, -20.2, 0), (0, 0, 0), cuello, [
                    ['cabeza', (0, -2.8, 0), (0, 0, 0), cabeza, [
                        ['mandibula', (0, -1.6, 0), (0, 0, 0), mandibula, []],
                    ], 0.92],
                ]],
                _brazo_atlahua(1, 'izq', []),
                _brazo_atlahua(-1, 'der', [_tridente()]),
            ]],
        ]],
    ]]


ATLAHUA_REPOSO = {
    'hombro_der': {'rot': (-18, 0, 8)}, 'antebrazo_der': {'rot': (-40, 0, 0)}, 'tridente': {'rot': (58, 0, 0)},
    'hombro_izq': {'rot': (-10, 0, -10)}, 'antebrazo_izq': {'rot': (-20, 0, 0)},
}
ATLAHUA_HEROICA = {
    'pelvis': {'rot': (0, -14, 0)},
    'torso': {'rot': (10, 14, 0)},
    'cabeza': {'rot': (-12, 8, 0)}, 'mandibula': {'rot': (14, 0, 0)},
    'pierna_izq': {'rot': (-26, 0, -4)}, 'espinilla_izq': {'rot': (32, 0, 0)},
    'pierna_der': {'rot': (20, 0, 6)}, 'espinilla_der': {'rot': (14, 0, 0)}, 'pie_der': {'rot': (-24, 0, 0)},
    'hombro_der': {'rot': (-100, -20, 10)}, 'antebrazo_der': {'rot': (-20, 0, 0)}, 'tridente': {'rot': (100, 0, 0)},
    'hombro_izq': {'rot': (-40, 0, -50)}, 'antebrazo_izq': {'rot': (-60, 0, 0)},
}


# ======================================================================
#  XIUHQUETZAL, el Fenix de Llamas Rojas y Violetas
# ======================================================================
# Rehecho el 11-10-2026 (Juan: "el unico que su diseno esta raro, que no se ve imponente, es el del fenix... se siente
# mas un chiste"). Ahora es un ave de presa en vuelo, como en sus referencias: alas enormes y macizas como las de un
# aguila (coberteras en filas, secundarias y las diez primarias abiertas como dedos), el pecho de brasa con vetas,
# cabeza de aguila con el pico ganchudo, la ceja fiera y la cresta de fuego hacia atras, y la cola larga en lenguas
# de fuego. Rojo dominante; el violeta, solo en las puntas.
CARMESI = Hs('2e0406', '440609', '5a0a0c')
GRANATE = Hs('6e0c0e', '861212', '9c1814')
ROJO_F = Hs('b01c16', 'c82418', 'dc3018')
GARRA = Hs('0e0a0a', '1a1414', '261e1c')
ORO_PICO = Hs('b07a18', 'd09a22', 'e8b834')
PICO_OSC = Hs('2a1a12', '3a2414')
PLUMA_ROJA = [CARMESI[2], GRANATE[1], ROJO_F[1], ROJO_F[2], H('e8501c', 0.15), H('ff8a28', 0.4), H('ffc85a', 0.65)]
PLUMA_VIOLETA = [GRANATE[1], ROJO_F[1], H('e8501c', 0.15), H('ff7a30', 0.35), H('d050c8', 0.55), H('b048f0', 0.75)]
PLUMA_MIXTA = PLUMA_VIOLETA
LLAMA_F = Hs('ffe08a', 'ff9a30', 'ff5a3c', 'c060ff', e=0.85)
PRIM_R = [GRANATE[1], ROJO_F[1], ROJO_F[2], H('e8501c', 0.15), H('ff8a28', 0.4), H('ffc85a', 0.65)]
PRIM_V = [GRANATE[1], ROJO_F[1], ROJO_F[2], H('ff7a30', 0.3), H('d050c8', 0.5), H('b048f0', 0.7)]
SECUND = [GRANATE[1], ROJO_F[1], ROJO_F[2], H('e8501c', 0.15), H('ff8a28', 0.4), H('ffc85a', 0.6)]
COLA_F = [CARMESI[2], GRANATE[1], ROJO_F[1], ROJO_F[2], H('e8501c', 0.15), H('ff7a28', 0.3), H('ffa040', 0.45),
          H('ffc85a', 0.55), H('c050d8', 0.6)]
_PLUMON = escamas(GRANATE, ROJO_F[:2], CARMESI[:1], w=4, h=3)
_COBERTERA = escamas(GRANATE, ROJO_F[:1], CARMESI[:1], w=4, h=2)


def _plumaje(x, y, z, r):
    return _PLUMON(x, y, z, r)


def _osc(c, k):
    return (c[0] * k, c[1] * k, c[2] * k, c[3])


def _pecho(x, y, z, r):
    """El pecho: plumon carmesi con vetas de brasa que salen del corazon encendido."""
    if z + .5 < -3.4:
        d = math.hypot(x + .5, (y + .5 + 8) / 1.25)
        if d < 1.1:
            return 'mj_brasa'
        if d < 1.9:
            return H('ff9a30', 0.55)
        if d < 7.5 and abs(ruido(x, y, z, 1.6, 41) - 0.5) < 0.045 + 0.035 * (7.5 - d) / 7.5:
            return H('ff8a28', 0.5) if d < 4.5 else H('e8501c', 0.3)
    return _PLUMON(x, y, z, r)


def lengua(v, p0, d, lado, largo, ancho, cols, ondas=1.5, fase=0.0, llama=0):
    """Una pluma de fuego: una lengua ondulada que se estrecha, con el borde dentado como una llama."""
    p0, d, lado = np.asarray(p0, float), _unit(d), _unit(lado)
    n = int(largo / 0.4) + 1
    for k in range(n):
        t = k / max(1, n - 1)
        centro = lado * math.sin(t * math.pi * ondas + fase) * ancho * 0.45 * t
        w = ancho * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t / 0.3) * 0.5)) * (1 - t ** 2.2)
        w *= 0.8 + 0.2 * math.sin(t * 34 + fase * 3)
        c = _grad(cols, t)
        for sd in np.arange(-w / 2, w / 2 + 1e-6, 0.4):
            p = p0 + d * (t * largo) + centro + lado * sd
            v.pon(*p, _osc(c, 0.78) if abs(sd) > w / 2 - 0.5 else c)
    if llama:
        punta = p0 + d * largo + lado * math.sin(math.pi * ondas + fase) * ancho * 0.45
        for _ in range(int(llama * 4)):
            u = v.r.uniform(0, llama)
            v.pon(*(punta + d * u + lado * v.r.uniform(-1.2, 1.2) * (1 - u / (llama + 1))),
                  LLAMA_F[min(len(LLAMA_F) - 1, int(u / llama * len(LLAMA_F)))])


# --- El ala, pintada como un campo en (u, v): u hacia fuera, v hacia atras -----------------------------------------
_ALA_W = 26.0          # del hombro a la muneca


def _vle_brazo(u):
    return -2.6 * math.sin(math.pi * 0.5 * min(u, _ALA_W) / _ALA_W)


def _vle_mano(a):
    return 0.10 * a + 0.0022 * a * a


_PRIMARIAS = []
for _i in range(10):
    _oa = 1.2 + _i * 1.75
    _PRIMARIAS.append((_oa, _vle_mano(_oa) + 2.6, math.radians(14 + _i * 8.6), [27, 30, 33, 36, 39, 42, 44, 45, 43, 38][_i],
                       _i >= 6))
_ALULA = [(1.0, -0.6, math.radians(a), l) for a, l in ((-40, 7.0), (-26, 8.5), (-12, 7.0))]


def _celda_brazo(u, v):
    """El brazo del ala: el borde de ataque, las coberteras menores y mayores y las secundarias. (color, grueso) o None."""
    rel = v - _vle_brazo(u)
    if rel < -0.3 or u > _ALA_W + 1.5 or u < -3:
        return None
    if rel < 4.0:
        return GRANATE[min(2, int(ruido(u, v, 0, 2.2, 5) * 3))], 4
    if rel < 9.0:
        return _COBERTERA(int(u), int(rel), 0, None), 3
    if rel < 15.5:
        k = math.floor(u / 3.4)
        du = (u - (k + 0.5) * 3.4) / 1.7
        if rel <= 15.5 - du * du * 2.5:
            c = _grad([GRANATE[1], ROJO_F[0], ROJO_F[2]], (rel - 9) / 6.5)
            return (_osc(c, 0.72) if abs(du) > 0.78 else c), 2
    k2 = math.floor(u / 3.8)
    uc = (k2 + 0.5) * 3.8
    du2 = (u - uc) / 1.9
    # Junto al cuerpo (las terciarias) son mas largas: tapan el hueco entre el ala y el flanco.
    punta = 30 + 2 * math.cos(uc * 0.35) - 0.12 * uc + (4 if uc < 6 else 0) + (k2 * 7 % 3) * 0.8 + max(0.0, 8 - uc) * 1.1
    if 9 <= rel <= punta - du2 * du2 * 3.5:
        t = (rel - 9) / (punta - 9)
        c = _grad(SECUND, t)
        if abs(du2) < 0.2:
            c = _osc(c, 1.15)
        elif abs(du2) > 0.82:
            c = _osc(c, 0.72)
        return c, (2 if t < 0.55 else 1)
    return None


def _celda_mano(a, b):
    """La mano del ala (desde la muneca): el borde, las coberteras primarias, las diez primarias en abanico (las de
    fuera, encima) y la alula."""
    rel = b - _vle_mano(a)
    if 0 <= a <= 19:
        if -0.3 <= rel < 3.4:
            return GRANATE[min(2, int(ruido(a, b, 3, 2.2, 6) * 3))], (3 if a < 12 else 2)
        if 3.4 <= rel < 9.5 - 3.5 * a / 19:
            return _COBERTERA(int(a), int(rel), 1, None), 2
    for (oa, ob, ang, largo, viol) in reversed(_PRIMARIAS):
        da, db = a - oa, b - ob
        sa, ca = math.sin(ang), math.cos(ang)
        along = da * sa + db * ca
        if along < -1.0 or along > largo:
            continue
        perp = -da * ca + db * sa - 0.07 * max(0.0, along) ** 2 / largo
        t = max(0.0, along) / largo
        w = 4.6 * (0.8 + 0.2 * min(1.0, t / 0.2)) if t < 0.72 else 4.6 * max(0.0, (1 - t) / 0.28) ** 0.8
        if abs(perp) > w / 2:
            continue
        c = _grad(PRIM_V if viol else PRIM_R, t)
        if abs(perp) < 0.45 and t < 0.92:
            c = _osc(c, 1.15)
        elif abs(perp) > w / 2 - 0.6:
            c = _osc(c, 0.74)
        return c, (2 if t < 0.5 else 1)
    for (oa, ob, ang, largo) in _ALULA:
        da, db = a - oa, b - ob
        along = da * math.cos(ang) + db * math.sin(ang)
        perp = -da * math.sin(ang) + db * math.cos(ang)
        if 0 <= along <= largo and abs(perp) <= 1.3 * (1 - along / largo * 0.6):
            return _grad([GRANATE[1], ROJO_F[2], H('e8501c', 0.15)], along / largo), 2
    return None


def _ala(s, nombre):
    """Un ala de aguila de fuego: el brazo (del hombro a la muneca) y la mano (las primarias), cada uno su pieza."""
    brazo = Vox(441 + s)
    for cu in range(-2, int(_ALA_W) + 3):
        for cv in range(-6, 42):
            u, v = cu + .5, cv + .5
            celda = _celda_brazo(u, v)
            if not celda:
                continue
            col, th = celda
            yc = -0.10 * u + 0.05 * max(0.0, v - _vle_brazo(u))
            y0 = math.floor(yc - th / 2 + 0.5)
            for k in range(th):
                brazo.pon(s * u, y0 + k, v, col, jitter=0.02)
    elipsoide(brazo, (s * 0.8, 0.0, 2.6), (3.4, 3.2, 4.6), _PLUMON)
    # Las coberteras de debajo del ala (las axilares): un manto de plumas que cuelga de la raiz del ala hacia el
    # flanco, para que al alzarla no se vea hueco bajo el sobaco.
    for k in range(7):
        u0 = -1.5 + k * 1.6
        tira(brazo, (s * u0, 1.6, 1.0 + k * 0.4), (s * 0.15, 0.55, 1.0), (1, 0, 0), 10 - k * 0.6, 3.4,
             [GRANATE[0], GRANATE[1], ROJO_F[1], ROJO_F[2]], raquis=False)
    mano = Vox(451 + s)
    for ca in range(-8, 66):
        for cb in range(-14, 58):
            a, b = ca + .5, cb + .5
            celda = _celda_mano(a, b)
            if not celda:
                continue
            col, th = celda
            yc = -0.06 * a + 0.04 * max(0.0, b - _vle_mano(a))
            y0 = math.floor(yc - th / 2 + 0.5)
            for k in range(th):
                mano.pon(s * a, y0 + k, b, col, jitter=0.02)
    # Las llamas que se desprenden de las puntas de las primarias.
    for (oa, ob, ang, largo, viol) in _PRIMARIAS:
        d = np.array([math.sin(ang), math.cos(ang)])
        n = np.array([-math.cos(ang), math.sin(ang)])
        punta = np.array([oa, ob]) + d * largo + n * 0.07 * largo
        for _ in range(7):
            u = mano.r.uniform(0.5, 4.0)
            q = punta + d * u + n * mano.r.uniform(-1.0, 1.0)
            yc = -0.06 * q[0] + 0.04 * max(0.0, q[1] - _vle_mano(q[0]))
            mano.pon(s * q[0], yc, q[1], LLAMA_F[min(3, int(u))] if viol or u < 2.5 else LLAMA_F[1])
    # El ala cuelga de los hombros (pieza 'hombros'), que estan en (0, -11, 1.6) del cuerpo.
    return ['ala_' + nombre, (6.2 * s, 0.0, 0.0), (0, 0, 0), brazo, [
        ['mano_ala_' + nombre, (s * _ALA_W, -0.10 * _ALA_W, _vle_brazo(_ALA_W)), (0, 0, 0), mano, []],
    ]]


def _pata(s, nombre):
    """La pata de un ave de presa: el muslo en su 'pantalon' de plumas, el tarso escamado de oro y las garras."""
    muslo = Vox(461 + s)
    elipsoide(muslo, (0, 3.2, 0), (3.6, 5.0, 3.8), _PLUMON)
    for k in range(10):
        a = k / 10 * 2 * math.pi
        tira(muslo, (math.cos(a) * 3.2, 6.0, math.sin(a) * 3.2), (math.cos(a) * 0.25, 1, math.sin(a) * 0.25),
             (-math.sin(a), 0, math.cos(a)), 4.6, 2.2, [GRANATE[1], ROJO_F[2], H('e8501c', 0.15)], raquis=False)
    tarso = Vox(471 + s)
    capsula(tarso, (0, 0, 0), (0, 9.5, 0), 1.4, 1.15, lambda x, y, z, r: ORO_PICO[0] if y % 2 else ORO_PICO[2])
    garras = Vox(481 + s)
    for dx, dz, largo in ((-2.4, -4.4, 5.4), (0, -5.2, 6.0), (2.4, -4.4, 5.4), (0, 3.2, 3.6)):
        u = _unit((dx, 0.3, dz))
        fin = np.array([0, 0.6, 0]) + u * largo
        capsula(garras, (0, 0.6, 0), fin, 1.0, 0.75, P(ORO_PICO[:2]))
        poli(garras, [fin, fin + u * 1.4 + [0, 0.5, 0], fin + u * 1.7 + [0, 2.0, 0]], [0.75, 0.55, 0.3], P(GARRA))
    return ['pata_' + nombre, (3.6 * s, 4.4, 0.6), (-28, 0, 0), muslo, [
        ['tarso_' + nombre, (0, 7.6, 0.0), (34, 0, 0), tarso, [
            ['garras_' + nombre, (0, 9.5, 0), (-12, 0, 0), garras, []],
        ]],
    ]]


# Lo que va inclinado hacia delante el cuerpo del fenix respecto al boceto (grados).
XIUHQUETZAL_INCLINA = 60


@functools.lru_cache(None)
def xiuhquetzal():
    """El fenix en vuelo: pecho de ave de presa (la quilla) con el corazon de brasa, el cuello grueso con su gorguera,
    cabeza de aguila, alas enormes y la cola en lenguas de fuego. Flota: su raiz va 30 pixeles por encima del suelo."""
    cuerpo = Vox(401)
    elipsoide(cuerpo, (0, -8, -1.2), (7.0, 9.6, 7.0), _pecho)
    elipsoide(cuerpo, (0, 2.0, 1.0), (5.6, 6.4, 5.8), _PLUMON)
    for s in (1, -1):
        elipsoide(cuerpo, (s * 4.8, -11.0, 1.8), (3.8, 3.6, 4.4), _PLUMON)
    for k in range(9):
        tira(cuerpo, (-4 + k, -15, 4.6 + abs(k - 4) * 0.2), (0, 0.55, 1), (1, 0, 0), 7 + (k % 2) * 2, 2.2,
             [GRANATE[1], ROJO_F[1], H('e8501c', 0.15)], raquis=False)
    for s in (1, -1):
        for k in range(5):
            tira(cuerpo, (s * 5.6, -2 + k * 1.6, -1 + k * 0.6), (s * 0.25, 1, 0.3), (0, 0, 1), 6, 2.0,
                 [GRANATE[1], ROJO_F[2], H('ff7a30', 0.3)], raquis=False)
        # El flanco bajo el hombro: plumas que se abren hacia fuera y hacia atras (la otra mitad del sobaco).
        for k in range(6):
            tira(cuerpo, (s * 5.2, -9.5 + k * 1.7, 0.6 + k * 0.5), (s * 0.75, 1, 0.45), (0, 0, 1), 9 + (k % 2) * 2, 3.4,
                 [GRANATE[0], GRANATE[1], ROJO_F[1], ROJO_F[2]], raquis=False)

    cola = Vox(402)
    for k in range(7):
        tira(cola, (-3 + k, -1.0, 0), (0, 1, 0.1), (1, 0, 0), 8, 2.6, [GRANATE[1], ROJO_F[2], H('e8501c', 0.15)], raquis=False)
    for i in range(9):
        t = i / 8 - 0.5
        a = t * 1.1
        lengua(cola, (t * 6.0, 0, (i % 2) * 0.8), (math.sin(a), math.cos(a), 0.0), (math.cos(a), -math.sin(a), 0),
               40 + (1 - abs(t) * 2) * 18, 6.0, COLA_F, ondas=1.2 + (i % 3) * 0.3, fase=i * 0.9, llama=4)
    for s in (1, -1):
        lengua(cola, (s * 1.6, 0, -0.8), (s * 0.14, 1, 0), (1, 0, 0), 56, 5.0, COLA_F, ondas=2.2, fase=s, llama=6)

    cuello = Vox(403)
    capsula(cuello, (0, 0, 0), (0, -7.0, -1.2), 4.4, 3.8, _PLUMON)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        tira(cuello, (math.cos(a) * 3.8, -2.5, math.sin(a) * 3.8), (math.cos(a) * 0.6, 1, math.sin(a) * 0.6 + 0.3),
             (-math.sin(a), 0, math.cos(a)), 6.5, 2.4, [GRANATE[1], ROJO_F[2], H('ff7a30', 0.35), H('ffb040', 0.55)],
             raquis=False)
    cuello2 = Vox(404)
    capsula(cuello2, (0, 0, 0), (0, -6.0, -0.6), 3.8, 3.4, _PLUMON)

    cabeza = Vox(405)
    elipsoide(cabeza, (0, -3.4, 0.2), (3.7, 3.6, 4.6), _PLUMON)
    elipsoide(cabeza, (0, -2.0, -2.6), (3.0, 2.4, 2.4), _PLUMON)
    caja(cabeza, 2.6, -4.0, -2.8, 3.5, -3.0, -1.8, 'mj_ojo_fenix')
    caja(cabeza, -3.5, -4.0, -2.8, -2.6, -3.0, -1.8, 'mj_ojo_fenix')
    for s in (1, -1):
        elipsoide(cabeza, (s * 2.5, -5.0, -2.2), (1.9, 1.0, 2.4), P(CARMESI))
        for k, (y0, largo) in enumerate(((-2.0, 6.5), (-3.6, 7.5), (-1.0, 5.0))):
            tira(cabeza, (s * 3.0, y0, 0.4), (s * 0.35, 0.25 - k * 0.2, 1), (0, 1, 0), largo, 2.4,
                 [ROJO_F[1], H('e8501c', 0.15), H('ff8a28', 0.4)], raquis=False)
    pico = Vox(406)
    poli(pico, [(0, 0, 0.8), (0, 0.0, -2.4), (0, 1.0, -4.8), (0, 2.8, -6.0), (0, 4.4, -5.6)], [2.5, 2.1, 1.5, 1.0, 0.5],
         lambda x, y, z, r: r.choice(PICO_OSC) if (z < -4.6 and y > 1.5) else r.choice(ORO_PICO))
    pico_inf = Vox(407)
    poli(pico_inf, [(0, 0, 0.6), (0, 0.5, -3.4)], [1.5, 0.6], P(ORO_PICO[:2]))
    cresta = Vox(408)
    for i in range(9):
        lado = (i - 4) / 4
        lengua(cresta, (lado * 1.8, 0, -1.5 + abs(lado) * 1.2), (lado * 0.6, -1.25 + abs(lado) * 0.45, 0.85), (0, 0.6, 1.0),
               19 - abs(lado) * 6, 3.2, [GRANATE[1], ROJO_F[2], H('ff7a30', 0.35), H('ffb040', 0.55), H('d050c8', 0.6)],
               ondas=1.0, fase=i, llama=3)
    barba = Vox(409)
    for k in range(3):
        tira(barba, (-1 + k, 0, 0), (0, 1, 0.4), (1, 0, 0), 4 + k % 2 * 2, 1.8, [GRANATE[1], ROJO_F[2], H('ff7a30', 0.3)],
             raquis=False)

    # Vuela tendido (Juan, 11-10-2026: "todo su cuerpo deberia estar a 60 grados para adelante", las patas hacia
    # atras y la cabeza mirando a los jugadores, no al cielo): el cuerpo va INCLINA grados mas hacia delante que en el
    # boceto, el cuello sale de delante y se alza, la cabeza mira algo hacia abajo y la cola y las patas van hacia
    # atras. Los hombros (una pieza vacia) deshacen la inclinacion: las alas quedan como estaban (y baten igual).
    patas = [_pata(1, 'izq'), _pata(-1, 'der')]
    for pt in patas:
        pt[2] = (52, 0, 0)
    return ['raiz', (0, -30, 0), (0, 0, 0), None, [
        ['cuerpo', (0, -4.0, 0), (-12 + XIUHQUETZAL_INCLINA, 0, 0), cuerpo, [
            *patas,
            ['hombros', (0, -11.0, 1.6), (-XIUHQUETZAL_INCLINA, 0, 0), None, [_ala(1, 'izq'), _ala(-1, 'der')]],
            ['cola', (0, 6.5, 4.0), (57, 0, 0), cola, []],
            ['cuello', (0, -16.5, -2.8), (-28, 0, 0), cuello, [
                ['cuello2', (0, -6.6, -1.0), (-20, 0, 0), cuello2, [
                    ['cabeza', (0, -5.8, -0.4), (12, 0, 0), cabeza, [
                        ['pico', (0, -2.6, -4.6), (0, 0, 0), pico, []],
                        ['pico_inf', (0, -0.9, -4.4), (0, 0, 0), pico_inf, []],
                        ['cresta', (0, -6.4, 0.6), (0, 0, 0), cresta, []],
                        ['barba', (0, 0.6, -2.4), (14, 0, 0), barba, []],
                    ], 1.3],
                ]],
            ]],
        ]],
    ]]


# Las alas, desplegadas de cara (el giro en x cuelga las plumas: el filo arriba, las primarias abajo y hacia fuera),
# como un aguila heraldica; luego se levantan (giro en z) y se adelantan o se recogen (giro en y).
# Con el cuerpo tendido (vuela inclinado), las plumas colgando a plomo parecian una vela que no iba con el cuerpo
# (Juan, 11-10-2026: "sus alas estan raras ... como si se movieran de una manera que no va con el cuerpo"): ahora
# cuelgan XIUHQUETZAL_ALA_TENDIDA grados menos, hacia atras, a lo largo del cuerpo, y de frente se siguen viendo
# enteras. Y las patas, que iban estiradas hacia atras con las garras por detras de la cola ("sus pies estan atras,
# mas atras que su cola, es raro"), cuelgan recogidas bajo el vientre: XIUHQUETZAL_PATAS (muslo, tarso, garras).
XIUHQUETZAL_ALA_TENDIDA = 40
XIUHQUETZAL_PATAS = (-60, -80, 40)
XIUHQUETZAL_REPOSO = {
    'ala_izq': {'rot': (-76 + XIUHQUETZAL_ALA_TENDIDA, -10, -16)}, 'mano_ala_izq': {'rot': (0, 0, 8)},
    'ala_der': {'rot': (-76 + XIUHQUETZAL_ALA_TENDIDA, 10, 16)}, 'mano_ala_der': {'rot': (0, 0, -8)},
    **{f'{pieza}_{lado}': {'rot': (giro, 0, 0)} for lado in ('izq', 'der')
       for pieza, giro in zip(('pata', 'tarso', 'garras'), XIUHQUETZAL_PATAS)},
}
XIUHQUETZAL_HEROICA = {
    'cuerpo': {'rot': (-4, 0, 0)},
    'ala_izq': {'rot': (-70, -14, -38)}, 'mano_ala_izq': {'rot': (0, -4, -12)},
    'ala_der': {'rot': (-70, 14, 38)}, 'mano_ala_der': {'rot': (0, 4, 12)},
    'cuello': {'rot': (8, 0, 0)}, 'cabeza': {'rot': (-26, 0, 0)}, 'pico_inf': {'rot': (28, 0, 0)},
    'cola': {'rot': (-6, 0, 0)},
}


# ----------------------------------------------------------------------
#  Para las escenas: las plumas sueltas y las losetas del mundo
# ----------------------------------------------------------------------
def _gradiente(cols, t):
    t = min(max(t, 0.0), 1.0) * (len(cols) - 1)
    i = min(int(t), len(cols) - 2)
    f = t - i
    return tuple(int(cols[i][k] + (cols[i + 1][k] - cols[i][k]) * f) for k in range(3))


def img_pluma(w, h, cols, brillo=None, semilla=0, ancho=0.48, punta=0.86):
    """Una pluma suelta en imagen (para las que caen en las escenas): de la raiz (arriba) a la punta (abajo)."""
    r = random.Random(semilla)
    tex = np.zeros((h, w, 4), np.uint8)
    emis = np.zeros((h, w, 4), np.uint8) if brillo else None
    cx = (w - 1) / 2
    for y in range(h):
        t = y / (h - 1)
        perfil = math.sin(math.pi * min(1.0, 0.06 + t / punta * 0.94)) ** 0.55 if t < punta else \
            math.sin(math.pi * (1 - (t - punta) / (1 - punta) * 0.5)) * 0.9
        hw = ancho * w * max(0.0, perfil)
        for x in range(w):
            d = abs(x - cx)
            if d > hw + 0.25:
                continue
            c = _gradiente(cols, t)
            if d < 0.6:
                c = tuple(min(255, int(v * 1.25)) for v in c)
            elif (y + int(d * 1.6)) % 3 == 0:
                c = tuple(int(v * 0.72) for v in c)
            if r.random() < 0.04:
                c = tuple(int(v * 0.85) for v in c)
            tex[y, x] = (*c, 255)
            if brillo:
                k = max(0.0, (t - 0.35) / 0.65) ** 1.6
                if k > 0.05 and d >= 0.6:
                    emis[y, x] = (*_gradiente(brillo, t), int(255 * min(1.0, k)))
    return (tex, emis) if brillo else tex


def _loseta(semilla, cols, n=16):
    r = random.Random(semilla)
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            t[y, x] = (*r.choice(cols)[:3], 255)
    return t


MAT = {
    'mj_oro': _loseta(1, ORO + ORO_CLARO),
    'mj_obsidiana': _loseta(2, OBS + [H('6a50a0')]),
    'mj_ala': img_pluma(12, 64, [c[:3] for c in PLUMA_ROJA[2:]], brillo=[(255, 140, 40), (255, 200, 80), (255, 240, 170)],
                        semilla=4),
    'mj_ala_v': img_pluma(12, 64, [c[:3] for c in PLUMA_VIOLETA[2:]], brillo=[(190, 90, 255), (240, 150, 255), (255, 210, 240)],
                          semilla=5),
}


# ----------------------------------------------------------------------
#  Dibujo
# ----------------------------------------------------------------------
MINIJEFES = {
    'moctezuma': (moctezuma, MOCTEZUMA_REPOSO, MOCTEZUMA_HEROICA),
    'yiatzo': (yiatzo, YIATZO_REPOSO, YIATZO_HEROICA),
    'atlahua': (atlahua, ATLAHUA_REPOSO, ATLAHUA_HEROICA),
    'xiuhquetzal': (xiuhquetzal, XIUHQUETZAL_REPOSO, XIUHQUETZAL_HEROICA),
}
UV4 = [(0, 0), (1, 0), (1, 1), (0, 1)]
# Cuanto se agranda cada uno en el mundo. Primero 2 bloques mas de alto que el boceto (11-10-2026, Juan: "subele sus
# tamanos a 2 bloques mas de altura") y luego 4 mas ("el tamano ... debe ser un poco mas grande como 4 bloques mas de
# altura"): Moctezuma ~9,4 bloques sin el penacho, Yiatzo ~9,4 con la capucha, Atlahua ~10,2 con la corona de coral;
# Xiuhquetzal, en vuelo, ~8 de la cabeza a las garras y ~22 de ala a ala.
ESCALA = {'moctezuma': 2.394, 'yiatzo': 2.159, 'atlahua': 2.155, 'xiuhquetzal': 2.0}


def quads(raiz, pose, M):
    out = []

    def visitar(n, Mp):
        nombre, off, rot, vox, hijos = n[:5]
        esc0 = n[5] if len(n) > 5 else 1.0
        ex = pose.get(nombre, {})
        r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        p = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        L = vr.T(*p) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R) @ vr.S(esc0 * ex.get('esc', 1.0))
        Mn = Mp @ L
        if ex.get('oculto'):
            return
        if vox is not None and vox.d:
            pts, cols, nors = vox.caras()
            W = M @ Mn
            P_ = pts @ W[:3, :3].T + W[:3, 3]
            N_ = nors @ W[:3, :3].T
            N_ /= np.linalg.norm(N_, axis=1, keepdims=True) + 1e-9
            for i in range(len(cols)):
                out.append((P_[i], UV4, cols[i], N_[i]))
        for h in hijos:
            visitar(h, Mn)

    visitar(raiz, np.eye(4))
    return out


_TEX = {}


def textura(c):
    """El cubo: el color con el canto un poco mas oscuro y una luz arriba a la izquierda, para que se vea cada voxel."""
    if c in _TEX:
        return _TEX[c]
    if isinstance(c, str):
        rgb, e = NOMBRADOS[c]
    else:
        rgb, e = c[:3], c[3]
    n = 2
    t = np.zeros((n, n, 4), np.uint8)
    t[..., :3] = np.clip(np.array(rgb), 0, 255)
    t[..., 3] = 255
    emis = None
    if e >= 1:
        emis = t.copy()
    elif e >= 0.5:
        emis = t.copy()
        emis[..., 3] = int(255 * (e - 0.45) * 1.1)
    _TEX[c] = (t, emis, e)
    return _TEX[c]


def dibujar(lienzo, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    for q in qs:
        P_, UV, c = q[0], q[1], q[2]
        tex, emis, e = textura(c)
        if e >= 1:
            luz = np.ones(3)
        else:
            n = q[3] if len(q) > 3 else vr.normal(P_)
            luz = vr.iluminar(n, cam, P_.mean(axis=0), luces, ambiente) + e * 1.1
        b = brillo if e >= 1 else brillo * 0.6
        for tri in ((0, 1, 2), (0, 2, 3)):
            lienzo.triangulo(cam, [P_[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla, brillo=b)


def entidad_a_mundo(x, y, z, guinada, escala=1.0):
    return vr.entidad_a_mundo(x, y, z, guinada, escala)


def contar():
    for n, (hacer, _, _) in MINIJEFES.items():
        total, caras = 0, 0

        def visitar(nodo):
            nonlocal total, caras
            if nodo[3] is not None:
                total += len(nodo[3].d)
                caras += len(nodo[3].caras()[1])
            for h in nodo[4]:
                visitar(h)
        visitar(hacer())
        print(n, total, 'voxeles,', caras, 'caras a la vista', flush=True)


if __name__ == '__main__':
    contar()

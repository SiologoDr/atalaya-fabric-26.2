"""
Teaser de Nerea: unos 14 segundos, sin voz y casi sin ensenarla.

La camara entra en el mar justo bajo la superficie: haces de luz, nieve
marina, algas y las ruinas de prismarina hundidas. Por el fondo corren tres
cadenas oxidadas enormes (sus sellos) que pasan por el borde de un abismo y
caen hacia lo hondo. La camara las sigue: la luz se apaga y abajo, muy lejos,
late algo magenta. Negro. De pronto dos ojos cian se abren delante; su luz le
ensena la cara (la calavera con la corona de coral) y chilla. Negro. Su nombre.

El mar se pinta por pixel lanzando rayos (superficie, fondo, acantilado,
pilares, cadenas, haces de luz volumetricos). La cara es la malla del juego
(nerea_juego.py) con su atlas y su capa de brillo, iluminada por pixel con la
luz de sus propios ojos. El sonido se monta con sus .ogg (nerea_sonidos.py).

Uso: python nerea_teaser.py <raiz del proyecto> <carpeta de trabajo> <salida.mp4> [escala]
     python nerea_teaser.py <raiz> <trabajo> <hoja.png> [escala] --muestras    (TIEMPOS=1.0,2.5,... en segundos)
"""
import math, os, random, subprocess, sys, tempfile
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

RAIZ, TRAB, SALIDA = sys.argv[1], sys.argv[2], sys.argv[3]
ESCALA = float(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else 1.0
MUESTRAS = '--muestras' in sys.argv
GEN = os.path.join(RAIZ, 'materiales/generadores')
sys.path.insert(0, GEN)
os.environ['NEREA_SIN_FISICA'] = '1'
_argv = sys.argv
sys.argv = [_argv[0], RAIZ, tempfile.mkdtemp()]
_cwd = os.getcwd()
os.chdir(GEN)
import vigia_render as vr
import nerea_escenas as ne
import nerea_juego as nj
import nerea_juego_anim as na
os.chdir(_cwd)
sys.argv = _argv

FF = imageio_ffmpeg.get_ffmpeg_exe()
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
PART = os.path.join(A, 'particle')
SND = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/nerea')
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
FPS = 24
BARRA = int(H * 0.11)        # bandas negras de cine arriba y abajo
HV0, HV1 = BARRA, H - BARRA  # solo se pinta entre las bandas
os.makedirs(TRAB, exist_ok=True)
CUADROS = os.path.join(TRAB, 'cuadros')
os.makedirs(CUADROS, exist_ok=True)
TAU = math.tau
_CACHE = {}


def suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _paso(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1)
    return k * k * (3 - 2 * k)


def sprite(nombre, lado):
    clave = (nombre, lado)
    if clave not in _CACHE:
        im = Image.open(os.path.join(PART, nombre)).convert('RGBA')
        _CACHE[clave] = im.resize((max(1, lado), max(1, lado)), Image.NEAREST)
    return _CACHE[clave]


# ----------------------------------------------------------------------
#  Planos: (nombre, inicio, duracion)
# ----------------------------------------------------------------------
PLANOS_T = [('negro', 0.0, 0.8), ('descenso', 0.8, 7.6), ('cara', 8.4, 2.6), ('negro2', 11.0, 0.4),
            ('titulo', 11.4, 2.8)]
TOTAL = 14.2
# los latidos del abismo (segundos del video): el sonido y el pulso magenta van juntos
LATIDOS = [5.95, 6.75, 7.45, 8.05]


def plano_en(t):
    for nombre, t0, d in PLANOS_T:
        if t0 <= t < t0 + d:
            return nombre, t - t0, d
    return 'titulo', t - 11.4, 2.8


# ----------------------------------------------------------------------
#  Ruido (como en el teaser de Aeralis)
# ----------------------------------------------------------------------
_TAB = np.random.default_rng(31).random((256, 256)).astype(np.float32)
_TAB1 = np.random.default_rng(32).random(1024).astype(np.float32)


def _ruido(u, v, per=256):
    iu, iv = np.floor(u), np.floor(v)
    fu, fv = (u - iu).astype(np.float32), (v - iv).astype(np.float32)
    fu = fu * fu * (3 - 2 * fu)
    fv = fv * fv * (3 - 2 * fv)
    i0 = iu.astype(np.int64) % per
    i1 = (i0 + 1) % per
    j0 = iv.astype(np.int64) & 255
    j1 = (j0 + 1) & 255
    a, b, c, d = _TAB[j0, i0], _TAB[j0, i1], _TAB[j1, i0], _TAB[j1, i1]
    return a + (b - a) * fu + (c - a) * fv + (a - b - c + d) * fu * fv


def _fbm(u, v, oct=4, per=256, gan=0.5, pie=None):
    """Ruido fractal; las octavas mas finas que el pixel (pie) se apagan."""
    s, amp, tot = 0.0, 1.0, 0.0
    for k in range(oct):
        n = _ruido(u + 19.0 * k, v + 7.3 * k, min(256, per << k))
        if pie is not None:
            w = np.clip(1.5 - 2.0 * pie * (1 << k), 0, 1)
            n = 0.5 + (n - 0.5) * w
        s = s + amp * n
        tot += amp
        amp *= gan
        u, v = u * 2, v * 2
    return s / tot


def _ruido1(x):
    i = np.floor(x)
    f = x - i
    f = f * f * (3 - 2 * f)
    i0 = i.astype(np.int64) & 1023
    return _TAB1[i0] * (1 - f) + _TAB1[(i0 + 1) & 1023] * f


class CamT:
    """Como vr.Camara (la x de pantalla sale espejada respecto a la del mundo), con alabeo."""

    def __init__(self, ojo, obj, fov, alabeo=0.0):
        self.ojo = np.array(ojo, float)
        f = np.array(obj, float) - self.ojo
        f /= np.linalg.norm(f)
        r = np.cross(f, [0, 1, 0])
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        c, sn = math.cos(alabeo), math.sin(alabeo)
        self.f, self.r, self.u = f, r * c + u * sn, u * c - r * sn
        self.foco = (H / 2) / math.tan(math.radians(fov) / 2)
        self.W, self.H = W, H

    def proyectar(self, p):
        d = np.asarray(p, float) - self.ojo
        x, y, z = d @ self.r, d @ self.u, d @ self.f
        zz = np.maximum(z, 1e-3)
        return W / 2 + self.foco * x / zz, H / 2 - self.foco * y / zz, z

    def rayos(self, paso=1):
        """Direccion por pixel (D.f = 1: el parametro del rayo es la profundidad)."""
        clave = ('rej', paso)
        if clave not in _CACHE:
            xs = np.arange(0, W, paso, dtype=np.float32) + 0.5 * paso - W / 2
            ys = np.arange(HV0, HV1, paso, dtype=np.float32) + 0.5 * paso - H / 2
            _CACHE[clave] = (xs[None, :], ys[:, None])
        xs, ys = _CACHE[clave]
        a, b = xs / self.foco, ys / self.foco
        return [(self.f[k] + a * self.r[k] - b * self.u[k]).astype(np.float32) for k in range(3)]


def catmull(claves, s):
    """Interpola posiciones (t, (x, y, z)) con Catmull-Rom (tiempos uniformes por tramo)."""
    ts = [k[0] for k in claves]
    ps = [np.array(k[1], float) for k in claves]
    if s <= ts[0]:
        return ps[0]
    if s >= ts[-1]:
        return ps[-1]
    i = max(j for j in range(len(ts) - 1) if ts[j] <= s)
    u = (s - ts[i]) / (ts[i + 1] - ts[i])
    p0, p1, p2, p3 = ps[max(0, i - 1)], ps[i], ps[i + 1], ps[min(len(ps) - 1, i + 2)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


# ----------------------------------------------------------------------
#  El mar: superficie, fondo, acantilado, ruinas, cadenas y abismo
# ----------------------------------------------------------------------
FONDO = -28.0                       # la meseta del fondo
BORDE_Z = 72.0                      # alli empieza el abismo
VISIB = 40.0                        # metros de visibilidad del agua
C_AGUA = np.array([0.06, 0.36, 0.42], np.float32)      # el agua iluminada
C_SOL = np.array([0.82, 0.97, 1.0], np.float32)
C_ARENA = np.array([0.62, 0.58, 0.46], np.float32)
C_PRISMA = [np.array(c, np.float32) for c in ((0.30, 0.56, 0.50), (0.22, 0.46, 0.44), (0.38, 0.62, 0.55),
                                             (0.17, 0.34, 0.35), (0.27, 0.50, 0.42))]
C_OXIDO = np.array([0.55, 0.30, 0.16], np.float32)
C_ROCA = np.array([0.16, 0.20, 0.22], np.float32)
C_MAGENTA = np.array([1.0, 0.16, 0.50], np.float32)
CORAZON_ABISMO = np.array([0.0, -330.0, 124.0])        # donde late, muy abajo


def luz_prof(y):
    """La luz del sol que llega a esa profundidad."""
    return np.exp(np.minimum(y, 0.0) / 25.0)


def borde_z(x):
    return BORDE_Z + 7.0 * (_ruido1(x / 22.0 + 3.0) - 0.5) + 3.0 * (_ruido1(x / 7.0 + 11.0) - 0.5)


_CAM_OJO = [(0.0, (0.0, -2.0, -46.0)), (1.9, (1.5, -7.5, -19.0)), (3.8, (2.5, -13.0, 13.0)),
            (5.3, (1.0, -16.0, 47.0)), (6.3, (0.5, -19.0, 80.0)), (7.0, (0.0, -34.0, 86.0)),
            (7.8, (0.0, -62.0, 90.0))]
_CAM_OBJ = [(0.0, (0.0, -6.0, 0.0)), (1.9, (0.0, -15.0, 30.0)), (3.8, (-1.0, -22.0, 62.0)),
            (5.3, (0.0, -42.0, 100.0)), (6.3, (0.0, -105.0, 114.0)), (7.0, (0.0, -175.0, 118.0)),
            (7.8, (0.0, -270.0, 121.0))]


def camara_descenso(s):
    ojo = catmull(_CAM_OJO, s)
    obj = catmull(_CAM_OBJ, s)
    # el balanceo del agua
    ojo = ojo + np.array([0.25 * math.sin(s * 0.9), 0.18 * math.sin(s * 1.3 + 1.0), 0.0])
    return CamT(ojo, obj, 56.0, 0.03 * math.sin(s * 0.6) + 0.04 * suave((s - 5.0) / 2.0))


# --- las ruinas: cajas de prismarina (min x, y, z, max x, y, z)
def _ruinas():
    r = random.Random(4)
    cajas = []

    def pilar(x, z, alto, ancho=3, roto=True):
        a, b = ancho / 2, ancho / 2 + 1
        y0 = FONDO
        cajas.append((x - b, y0, z - b, x + b, y0 + 1.5, z + b))
        cajas.append((x - a, y0, z - a, x + a, y0 + alto, z + a))
        for yb in range(4, int(alto) - 2, 5):
            cajas.append((x - a - 0.4, y0 + yb, z - a - 0.4, x + a + 0.4, y0 + yb + 0.8, z + a + 0.4))
        if roto:
            cajas.append((x - a, y0 + alto, z - a, x + 0.5, y0 + alto + r.choice([1.5, 2.5]), z + 0.5))
        else:
            cajas.append((x - b, y0 + alto, z - b, x + b, y0 + alto + 1.2, z + b))
        for _ in range(3):                 # bloques caidos alrededor
            bx, bz = x + r.uniform(-7, 7), z + r.uniform(-7, 7)
            if abs(bx - x) > b + 0.5 or abs(bz - z) > b + 0.5:
                bx, bz = round(bx), round(bz)
                cajas.append((bx, y0, bz, bx + r.choice([1, 2]), y0 + r.choice([1, 1, 2]), bz + r.choice([1, 2])))

    # los tres pilares-ancla de las cadenas
    pilar(-15.0, 34.0, 11, 4, roto=False)
    pilar(14.0, 41.0, 13, 4, roto=False)
    pilar(-5.0, 54.0, 9, 4, roto=False)
    # ruinas sueltas
    pilar(-12.0, -8.0, 7)
    pilar(13.0, 4.0, 9)
    pilar(-22.0, 14.0, 5)
    pilar(24.0, 24.0, 8)
    pilar(-28.0, 50.0, 10)
    pilar(28.0, 58.0, 6)
    # un muro caido
    for k in range(6):
        cajas.append((6.0 + k * 2.0, FONDO, 18.0 + k * 0.6, 7.6 + k * 2.0, FONDO + 1.0 + (k % 3) * 0.8, 19.6 + k * 0.6))
    return np.array(cajas, np.float32)


RUINAS = _ruinas()
ANCLAS = [(-15.0, 34.0, 4), (14.0, 41.0, 4), (-5.0, 54.0, 4)]   # (x, z, ancho) de los pilares con cadena


# --- las cadenas: eslabones enormes, de los pilares al borde y abajo, al abismo
ESLABON = (3.0, 1.9, 0.5)          # largo, ancho, grueso (bloques)


def _cadenas():
    """Cada eslabon: (centro, eje u (a lo largo), eje v (ancho), eje w (grueso))."""
    out = []
    r = random.Random(8)
    for i, (x, z, ancho) in enumerate(ANCLAS):
        ini = np.array([x, FONDO + 3.0, z + ancho / 2 + 0.3])
        xe = x * 0.55 + r.uniform(-2, 2)
        labio = np.array([xe, FONDO + 0.7, float(borde_z(np.array([xe]))[0]) + 0.6])
        medio = (ini + labio) / 2 + np.array([r.uniform(-2.5, 2.5), -2.2, 0])
        medio[1] = max(medio[1], FONDO + 0.7)
        abajo = CORAZON_ABISMO + np.array([(i - 1) * 6.0, 140.0, -6.0])
        # tramo por el fondo (curva) y tramo colgando (recta hacia el corazon)
        pts = [ini + (medio - ini) * k for k in np.linspace(0, 1, 8)[:-1]]
        pts += [medio + (labio - medio) * k for k in np.linspace(0, 1, 8)[:-1]]
        pts += [labio + (abajo - labio) * k for k in np.linspace(0, 1, 40)]
        pts = np.array(pts)
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        acum = np.concatenate([[0.0], np.cumsum(seg)])
        paso = ESLABON[0] * 0.78
        s_, k = 0.0, 0
        giro0 = r.uniform(0, 1)
        while s_ < acum[-1]:
            j = min(int(np.searchsorted(acum, s_, side='right')) - 1, len(seg) - 1)
            c = pts[j] + (pts[j + 1] - pts[j]) * (s_ - acum[j]) / seg[j]
            u = (pts[j + 1] - pts[j]) / seg[j]
            ref = np.array([0.0, 1.0, 0.0]) if abs(u[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
            v = np.cross(u, ref)
            v /= np.linalg.norm(v)
            w = np.cross(u, v)
            ang = (k % 2) * math.pi / 2 + 0.25 * math.sin(k * 1.7 + giro0 * 6)
            v2, w2 = v * math.cos(ang) + w * math.sin(ang), w * math.cos(ang) - v * math.sin(ang)
            out.append((c, u, v2, w2))
            s_ += paso
            k += 1
    return out


CADENAS = _cadenas()


def cajas_rayo(cam, O, D, prof, col, tipo, luz_fn):
    """Interseccion por pixel con las cajas de las ruinas (alineadas) o con los
    eslabones (orientados, con su agujero). Pinta en col y prof."""
    Dx, Dy, Dz = D
    hv = Dx.shape
    if tipo == 'ruinas':
        lista = [(np.array([(c[0] + c[3]) / 2, (c[1] + c[4]) / 2, (c[2] + c[5]) / 2]),
                  np.eye(3), np.array([(c[3] - c[0]) / 2, (c[4] - c[1]) / 2, (c[5] - c[2]) / 2])) for c in RUINAS]
    else:
        med = np.array([ESLABON[0] / 2, ESLABON[1] / 2, ESLABON[2] / 2])
        lista = [(c, np.stack([u, v, w]), med) for c, u, v, w in CADENAS]
    for centro, R, med in lista:
        # recuadro en pantalla
        esq = np.array([centro + R.T @ (med * np.array(sg)) for sg in
                        ((-1, -1, -1), (-1, -1, 1), (-1, 1, -1), (-1, 1, 1), (1, -1, -1), (1, -1, 1), (1, 1, -1), (1, 1, 1))])
        px, py, pz = cam.proyectar(esq)
        if (pz < 0.3).all():
            continue
        if (pz < 0.3).any():
            x0, x1, y0, y1 = 0, W, 0, hv[0]
        else:
            if pz.min() > VISIB * 4.5:      # tan lejos que el agua ya lo tapa
                continue
            x0, x1 = max(0, int(px.min()) - 1), min(W, int(px.max()) + 2)
            y0, y1 = max(0, int(py.min()) - 1 - HV0), min(hv[0], int(py.max()) + 2 - HV0)
        if x0 >= x1 or y0 >= y1:
            continue
        sl = (slice(y0, y1), slice(x0, x1))
        dl = [R[k, 0] * Dx[sl] + R[k, 1] * Dy[sl] + R[k, 2] * Dz[sl] for k in range(3)]
        ol = R @ (O - centro)
        tmin = np.full(dl[0].shape, -1e9, np.float32)
        tmax = np.full(dl[0].shape, 1e9, np.float32)
        eje_n = np.zeros(dl[0].shape, np.int8)
        for k in range(3):
            dk = np.where(np.abs(dl[k]) < 1e-7, 1e-7, dl[k])
            ta, tb = (-med[k] - ol[k]) / dk, (med[k] - ol[k]) / dk
            lo, hi = np.minimum(ta, tb), np.maximum(ta, tb)
            nuevo = lo > tmin
            eje_n[nuevo] = k
            tmin = np.maximum(tmin, lo)
            tmax = np.minimum(tmax, hi)
        m = (tmax >= tmin) & (tmin > 0.05) & (tmin < prof[sl])
        if tipo != 'ruinas':
            # el agujero del eslabon: si entra por la cara grande dentro del hueco, no toca
            pu = ol[0] + tmin * dl[0]
            pv = ol[1] + tmin * dl[1]
            hueco = (eje_n == 2) & (np.abs(pu) < med[0] - 0.55) & (np.abs(pv) < med[1] - 0.5)
            m &= ~hueco
        if not m.any():
            continue
        t = tmin[m]
        P = np.stack([O[k] + t * d[sl][m] for k, d in enumerate((Dx, Dy, Dz))], 1)
        e = eje_n[m]
        sg = -np.sign(np.stack([dl[0][m], dl[1][m], dl[2][m]], 1)[np.arange(len(t)), e])
        n = (R.T[:, e] * sg).T.astype(np.float32)
        if tipo == 'ruinas':
            # bloques de prismarina: cada bloque de su tono, con junta
            uu = np.where(e == 0, P[:, 2], P[:, 0])
            vv = np.where(e == 1, P[:, 2], P[:, 1])
            bu, bv = np.floor(uu + 1e-3), np.floor(vv + 1e-3)
            tono = _TAB[(bv.astype(np.int64) + e * 37) & 255, bu.astype(np.int64) & 255]
            fu, fv = uu - bu, vv - bv
            junta = _paso(0.0, 0.08, np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv)))
            det = np.clip(1.6 - t / cam.foco * 9.0, 0, 1)
            idx = np.clip((tono * 5).astype(int), 0, 4)
            alb = np.stack(C_PRISMA)[idx] * ((1 - 0.45 * (1 - junta) * det))[:, None]
            alb = alb * (0.85 + 0.3 * _fbm(uu / 3.0, vv / 3.0 + e * 7, oct=2))[:, None]
        else:
            pu = (P - centro) @ R[0]
            moteado = _fbm(pu * 1.3 + 4.0, (P - centro) @ R[1] * 1.3, oct=3)
            alb = C_OXIDO * (0.55 + 0.9 * moteado)[:, None]
        rgb = alb * luz_fn(P, n)
        sub = col[sl]
        sub[m] = rgb
        sp = prof[sl]
        sp[m] = t


def luz_mar(P, n, tt, causticas=True):
    """Luz que baja de la superficie: difusa + causticas en lo que mira arriba."""
    L = luz_prof(P[:, 1])
    arriba = np.clip(n[:, 1], 0, 1)
    c = (0.16 + 0.5 * arriba + 0.22 * np.clip(-n[:, 2] * 0.5 + 0.5, 0, 1)) * L
    if causticas:
        c = c + caustica(P[:, 0], P[:, 2], tt) * arriba * L * 1.2
    return C_SOL[None] * c[:, None] + np.array([0.01, 0.02, 0.025], np.float32)[None]


def caustica(X, Z, tt, pie=None):
    n1 = _ruido((X + 0.5 * tt) / 1.1, (Z - 0.3 * tt) / 1.1)
    n2 = _ruido((X - 0.4 * tt) / 0.85 + 5.0, (Z + 0.45 * tt) / 0.85 + 9.0)
    n3 = _ruido((X + 0.2 * tt) / 2.6 + 13.0, (Z + 0.1 * tt) / 2.6 + 3.0)
    c = np.clip(1 - np.abs(n1 - n2) * 5.0, 0, 1) ** 3 * (0.5 + n3)
    if pie is not None:
        k = np.clip(1.5 - pie * 5.0, 0, 1)
        c = c * k + 0.16 * (1 - k)
    return c


def agua_dir(O, Dy, lon):
    """El color del agua hacia donde mira cada rayo: claro hacia arriba,
    negro hacia lo hondo."""
    elev = Dy / lon
    y = O[1] + 14.0 * elev
    k = luz_prof(y) * np.clip(0.42 + 0.58 * (elev + 0.35) / 1.35, 0.05, 1.0)
    return C_AGUA[None, None] * k[..., None]


def descenso(s, d):
    tt = s
    cam = camara_descenso(s)
    D = cam.rayos()
    Dx, Dy, Dz = D
    O = cam.ojo
    hv = Dx.shape
    lon = np.sqrt(Dx * Dx + Dy * Dy + Dz * Dz)
    col = np.zeros(hv + (3,), np.float32)
    prof = np.full(hv, np.inf, np.float32)

    # 1) la superficie, vista desde abajo: la ventana de Snell y su reflejo
    m = Dy > 1e-4
    if m.any():
        t = -O[1] / Dy[m]
        X, Z = O[0] + t * Dx[m], O[2] + t * Dz[m]
        cosv = Dy[m] / lon[m]
        pie = t / cam.foco / np.maximum(cosv, 0.05)
        rip = _fbm(X / 3.0 + tt * 0.3, Z / 3.0 - tt * 0.2, oct=4, pie=pie / 3.0)
        lineas = np.clip(1 - np.abs(_fbm(X / 1.6 - tt * 0.25, Z / 1.6 + tt * 0.3, oct=2, pie=pie / 1.6) - 0.5) * 9, 0, 1) ** 3
        ventana = _paso(0.63, 0.72, cosv + 0.06 * (rip - 0.5))
        c = C_AGUA[None] * (0.35 + 0.7 * rip)[:, None]
        c = c + C_SOL[None] * (0.35 * lineas)[:, None]
        c = c * (1 - ventana[:, None]) + C_SOL[None] * (1.1 + 0.4 * rip)[:, None] * ventana[:, None]
        col[m] = c
        prof[m] = t

    # 2) el fondo: arena con causticas y losas de prismarina; acaba en el borde del abismo
    m = Dy < -1e-4
    if m.any():
        t = (FONDO - O[1]) / Dy[m]
        X, Z = O[0] + t * Dx[m], O[2] + t * Dz[m]
        ok = Z < borde_z(X)
        idx = np.nonzero(m)
        m2 = (idx[0][ok], idx[1][ok])
        t, X, Z = t[ok], X[ok], Z[ok]
        pie = t / cam.foco / np.maximum(-Dy[m2] / lon[m2], 0.03)
        dunas = _fbm(X / 9.0, Z / 9.0, oct=4, pie=pie / 9.0)
        ondas = 0.5 + 0.5 * np.sin((X * 0.35 + Z * 1.6 + dunas * 6.0)) * np.clip(1.5 - pie * 2.0, 0, 1)
        alb = C_ARENA[None] * (0.7 + 0.25 * dunas + 0.12 * ondas)[:, None]
        # losas de prismarina alrededor de las ruinas
        bx, bz = np.floor(X / 1.0), np.floor(Z / 1.0)
        losa = (_fbm(X / 14.0 + 40, Z / 14.0, oct=2) > 0.56)
        tono = _TAB[bz.astype(np.int64) & 255, bx.astype(np.int64) & 255]
        fx, fz = X - bx, Z - bz
        junta = _paso(0.0, 0.07, np.minimum(np.minimum(fx, 1 - fx), np.minimum(fz, 1 - fz)))
        det = np.clip(1.5 - pie * 7.0, 0, 1)
        pris = np.stack(C_PRISMA)[np.clip((tono * 5).astype(int), 0, 4)] * (1 - 0.4 * (1 - junta) * det)[:, None]
        alb = np.where(losa[:, None], pris * 0.85, alb)
        # oscurece hacia el labio del abismo
        labio = _paso(0.0, 9.0, borde_z(X) - Z)
        P = np.stack([X, np.full_like(X, FONDO), Z], 1)
        nrm = np.tile(np.array([0, 1, 0], np.float32), (len(X), 1))
        L = luz_prof(FONDO)
        cau = caustica(X, Z, tt, pie=pie / 1.5)
        luz = C_SOL[None] * (L * (0.42 + 1.1 * cau))[:, None]
        col[m2] = alb * luz * (0.35 + 0.65 * labio)[:, None]
        prof[m2] = t

    # 3) la pared del abismo (se ve al mirar hacia atras, ya dentro)
    m = (Dz < -1e-4) & (O[2] > BORDE_Z - 6)
    if m.any():
        t = (BORDE_Z - O[2]) / Dz[m]
        X = O[0] + t * Dx[m]
        t = (borde_z(X) - O[2]) / Dz[m]
        X, Y = O[0] + t * Dx[m], O[1] + t * Dy[m]
        ok = (Y < FONDO) & (t > 0) & (t < prof[m])
        idx = np.nonzero(m)
        m2 = (idx[0][ok], idx[1][ok])
        if len(m2[0]):
            t, X, Y = t[ok], X[ok], Y[ok]
            roca = _fbm(X / 6.0, Y / 6.0, oct=4)
            c = C_ROCA[None] * (0.5 + 0.9 * roca)[:, None] * (luz_prof(Y) * 0.6)[:, None]
            col[m2] = c * C_SOL[None]
            prof[m2] = t

    # 4) ruinas y cadenas
    luz_fn = lambda P, n: luz_mar(P, n, tt)
    cajas_rayo(cam, O, D, prof, col, 'ruinas', luz_fn)
    k_lat = latido_k(0.8 + s)

    def luz_cadena(P, n):
        c = luz_mar(P, n, tt)
        L = CORAZON_ABISMO[None] - P
        dist = np.sqrt((L * L).sum(1))
        lam = np.clip((n * L).sum(1) / dist, 0, 1)
        return c + C_MAGENTA[None] * (k_lat * 3.0 * (0.25 + lam) / (1 + (dist / 190.0) ** 2))[:, None]
    cajas_rayo(cam, O, D, prof, col, 'cadenas', luz_cadena)

    # 5) el agua: niebla segun la distancia, con el color del agua en esa direccion
    agua = agua_dir(O, Dy, lon)
    tr = np.exp(-np.minimum(prof, 1e4) / VISIB)[..., None]
    col = col * tr + agua * (1 - tr)

    # 6) los haces de luz, volumetricos (a cuarto de resolucion)
    col += haces(cam, O, prof, tt)[..., None] * C_SOL[None, None] * 0.55

    # 7) el latido del abismo: un resplandor magenta muy abajo
    k = latido_k(0.8 + s)
    if k > 0.003:
        x, y, z = cam.proyectar(CORAZON_ABISMO)
        if z > 1:
            yy, xx = _rejilla_hv()
            rr = np.hypot(xx - x, yy - (y - HV0)) / (H * 0.5)
            col += (np.exp(-(rr / 0.05) ** 2) * 1.6 + np.exp(-(rr / 0.22) ** 2) * 0.4
                    + np.exp(-(rr / 0.7) ** 2) * 0.12)[..., None] * C_MAGENTA * k

    img = a_pantalla(col)
    # algas, nieve marina y burbujas
    algas(img, cam, prof, tt)
    nieve(img, cam, tt)
    burbujas_inmersion(img, s)
    return img


def latido_k(t):
    """Intensidad del pulso magenta a t segundos del video (sigue a LATIDOS)."""
    k = 0.0
    for t0 in LATIDOS:
        dt = t - t0
        if dt >= 0:
            k = max(k, math.exp(-dt / 0.16) + 0.55 * math.exp(-max(0.0, dt - 0.2) / 0.14) * (dt > 0.2))
    llegar = suave((t - 5.6) / 1.2)
    return 0.7 * k * llegar + 0.13 * llegar


def _rejilla_hv():
    if 'hv' not in _CACHE:
        yy, xx = np.mgrid[0:HV1 - HV0, 0:W].astype(np.float32)
        _CACHE['hv'] = (yy, xx)
    return _CACHE['hv']


def haces(cam, O, prof, tt):
    """Rayos de sol que atraviesan el agua: se marcha por cada rayo y se suma la
    luz que cruza (el patron de la superficie proyectado segun el sol)."""
    paso = 4
    Dx, Dy, Dz = cam.rayos(paso)
    pr = prof[paso // 2::paso, paso // 2::paso]
    hh, ww = min(pr.shape[0], Dx.shape[0]), min(pr.shape[1], Dx.shape[1])
    pr, Dx, Dy, Dz = pr[:hh, :ww], Dx[:hh, :ww], Dy[:hh, :ww], Dz[:hh, :ww]
    tfin = np.minimum(pr, 70.0)
    n = 22
    acum = np.zeros(Dx.shape, np.float32)
    sol = np.array([0.32, 1.0, 0.18])
    for i in range(n):
        t = tfin * (i + 0.5) / n
        Py = O[1] + t * Dy
        dentro = Py < 0
        Px, Pz = O[0] + t * Dx, O[2] + t * Dz
        Xs, Zs = Px - Py * sol[0] / sol[1], Pz - Py * sol[2] / sol[1]
        patron = np.clip((_fbm(Xs / 6.0 + tt * 0.12, Zs / 2.2, oct=2) - 0.5) * 4.5, 0, 1)
        acum += patron * luz_prof(Py) * np.exp(-t / VISIB) * dentro * (tfin / n)
    acum *= 0.045
    im = Image.fromarray(np.clip(acum * 255 / 1.0, 0, 255).astype(np.uint8)).resize((W, HV1 - HV0), Image.BILINEAR)
    return np.array(im.filter(ImageFilter.GaussianBlur(2 * ESCALA))).astype(np.float32) / 255 * 1.0


def a_pantalla(col):
    full = np.zeros((H, W, 3), np.float32)
    full[HV0:HV1] = np.clip(col, 0, 1)
    return Image.fromarray((full * 255).astype(np.uint8)).convert('RGBA')


# --- algas: cintas que se mecen, recortadas con la profundidad de la escena
def _algas():
    r = random.Random(11)
    out = []
    matas = [(r.uniform(-30, 30), r.uniform(-40, 62)) for _ in range(16)]
    while len(out) < 70:
        cx, cz = r.choice(matas)
        x, z = cx + r.gauss(0, 2.2), cz + r.gauss(0, 2.2)
        if abs(x) < 6 and z < 50:
            continue
        if any(abs(x - ax) < 3.5 and abs(z - az) < 3.5 for ax, az, _ in ANCLAS):
            continue
        out.append((x, z, r.uniform(5, 14), r.uniform(0, TAU), r.uniform(0.6, 1.0)))
    return out


ALGAS = _algas()


def algas(img, cam, prof, tt):
    capa = np.array(img).astype(np.float32)
    for x, z, alto, fase, tono in sorted(ALGAS, key=lambda a: -cam.proyectar((a[0], FONDO + a[2] / 2, a[1]))[2]):
        pts, anchos = [], []
        for k in range(14):
            h = k / 13
            dx = 1.4 * h ** 1.4 * math.sin(tt * 0.9 + fase + h * 2.5)
            dz = 0.9 * h ** 1.4 * math.cos(tt * 0.7 + fase)
            pts.append((x + dx, FONDO + alto * h, z + dz))
        P = np.array(pts)
        sx, sy, sz = cam.proyectar(P)
        if sz.min() < 4.0 or sz.min() > VISIB * 3:
            continue
        zm = float(sz.mean())
        marg = 1.2 * cam.foco / sz.min()
        bx0, bx1 = int(max(0, sx.min() - marg)), int(min(W, sx.max() + marg + 1))
        by0, by1 = int(max(HV0, sy.min() - marg)), int(min(HV1, sy.max() + marg + 1))
        if bx0 >= bx1 or by0 >= by1:
            continue
        mask = Image.new('L', (bx1 - bx0, by1 - by0), 0)
        dm = ImageDraw.Draw(mask)
        qx, qy = sx - bx0, sy - by0
        rh = random.Random(int(x * 100 + z))
        hojas = {k: (rh.choice((-1, 1)), rh.uniform(0.7, 1.5)) for k in range(2, 13) if rh.random() < 0.45}
        for k in range(13):
            w_ = max(1, int(0.9 * (1 - 0.55 * k / 13) * cam.foco / sz[k]))
            dm.line([(qx[k], qy[k]), (qx[k + 1], qy[k + 1])], fill=255, width=w_)
            if k in hojas:     # hojas
                lado, tam = hojas[k]
                hw = 1.3 * tam * cam.foco / sz[k]
                hx = qx[k] + lado * hw * 0.45
                dm.ellipse((hx - hw * 0.55, qy[k] - hw * 0.22, hx + hw * 0.55, qy[k] + hw * 0.22), fill=255)
        a = np.array(mask).astype(np.float32) / 255
        if not a.any():
            continue
        # tapada por lo que este mas cerca
        a *= (prof[by0 - HV0:by1 - HV0, bx0:bx1] > zm)
        L = float(luz_prof(np.array([FONDO + alto * 0.6]))[0])
        tr = math.exp(-zm / VISIB)
        c = np.array([0.16, 0.30, 0.16]) * tono * (0.3 + 0.9 * L)
        agua = C_AGUA * L * 0.8
        c = c * tr + agua * (1 - tr)
        sub = capa[by0:by1, bx0:bx1, :3]
        capa[by0:by1, bx0:bx1, :3] = sub * (1 - a[..., None]) + (c * 255)[None, None] * a[..., None]
    img.paste(Image.fromarray(np.clip(capa, 0, 255).astype(np.uint8)))


# --- nieve marina: motas en 3D que derivan
_NIEVE = np.random.default_rng(13).random((7000, 4)).astype(np.float32)


def nieve(img, cam, tt):
    p = _NIEVE
    X = -40 + 80 * p[:, 0] + 0.6 * np.sin(tt * 0.4 + p[:, 3] * 20)
    Y = -150 + 150 * p[:, 1] - 0.35 * tt
    Z = -60 + 200 * p[:, 2] + 0.5 * tt
    P = np.stack([X, Y, Z], 1)
    sx, sy, sz = cam.proyectar(P)
    ok = (sz > 0.4) & (sz < 30) & (sx > -20) & (sx < W + 20) & (sy > HV0) & (sy < HV1)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    L = luz_prof(Y)
    for i in np.nonzero(ok)[0]:
        z = sz[i]
        b = (0.35 + 0.65 * p[i, 3]) * (0.15 + 0.85 * L[i]) * math.exp(-z / VISIB)
        if b < 0.02:
            continue
        rr = max(0.6, 0.05 * cam.foco / z)
        g = int(255 * min(1.0, b))
        al = int(min(255, 255 * b * (1.6 if rr < 2 else 0.5)))
        d.ellipse((sx[i] - rr, sy[i] - rr, sx[i] + rr, sy[i] + rr), fill=(int(g * 0.75), g, g, al))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(0.6 * ESCALA)))


def burbujas_inmersion(img, s):
    """Al entrar: una nube de burbujas que sube y se aparta; luego alguna suelta."""
    r = random.Random(5)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for k in range(70):
        t0 = r.uniform(-0.3, 0.9) if k < 55 else r.uniform(1.0, 7.0)
        vida = s - t0
        if vida < 0 or vida > 2.2:
            continue
        x0, y0 = r.uniform(0.1, 0.9) * W, r.uniform(0.75, 1.15) * H
        vx = (x0 - W / 2) / W * 0.5 * H
        x = x0 + vx * vida + math.sin(vida * 6 + k) * 6 * ESCALA
        y = y0 - (0.35 + r.random() * 0.4) * H * vida
        lado = int(r.choice([10, 14, 20, 28, 40]) * ESCALA * (1.0 if k < 55 else 0.6))
        sp = sprite(f'nerea_burbuja_{r.randint(0, 1)}.png', lado)
        al = min(1.0, (2.2 - vida) / 0.6)
        if al < 1:
            sp = sp.copy()
            sp.putalpha(sp.getchannel('A').point(lambda v, al=al: int(v * al)))
        capa.alpha_composite(sp, (int(x - lado / 2), int(y - lado / 2)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(1.0 * ESCALA)))


# ----------------------------------------------------------------------
#  La cara: la malla del juego, iluminada por pixel con la luz de sus ojos
# ----------------------------------------------------------------------
UV, ALTO = nj.empaquetar()
TEX = vr.cargar(os.path.join(A, 'entity/nerea/nerea_f1.png'))
BRILLO = vr.cargar(os.path.join(A, 'entity/nerea/nerea_brillo_f1.png'))
OCULTAS = ['pierna_izq', 'pierna_der', 'algas_del', 'algas_tras', 'brazo_izq', 'brazo_der', 'tridente', 'cadena_mano',
           'molino_izq', 'molino_der', 'corazon_2', 'corazon_3', 'corazon_4', 'corazon_libre']


class LienzoD:
    """Rasterizado diferido: guarda por pixel el color de la textura, el brillo,
    la normal y la posicion en el mundo, y se ilumina despues."""

    def __init__(self):
        self.alb = np.zeros((H, W, 3), np.float32)
        self.emis = np.zeros((H, W, 3), np.float32)
        self.nrm = np.zeros((H, W, 3), np.float32)
        self.pos = np.zeros((H, W, 3), np.float32)
        self.alfa = np.zeros((H, W), np.float32)
        self.z = np.full((H, W), np.inf, np.float32)

    def triangulo(self, cam, P, UV_, n, tex, emis_tex, osc=1.0):
        s = [cam.proyectar(p) for p in P]
        if min(q[2] for q in s) < 0.05:
            return
        xs = [q[0] for q in s]
        ys = [q[1] for q in s]
        x0 = max(int(math.floor(min(xs))), 0)
        x1 = min(int(math.ceil(max(xs))), W - 1)
        y0 = max(int(math.floor(min(ys))), 0)
        y1 = min(int(math.ceil(max(ys))), H - 1)
        if x0 > x1 or y0 > y1:
            return
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = s
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            return
        l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l3 = 1 - l1 - l2
        dentro = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not dentro.any():
            return
        iw = l1 / az + l2 / bz + l3 / cz
        z = 1 / iw
        w1, w2, w3 = l1 / az * z, l2 / bz * z, l3 / cz * z
        u = w1 * UV_[0][0] + w2 * UV_[1][0] + w3 * UV_[2][0]
        v = w1 * UV_[0][1] + w2 * UV_[1][1] + w3 * UV_[2][1]
        th, tw = tex.shape[:2]
        tu = np.clip((u * tw).astype(int), 0, tw - 1)
        tv = np.clip((v * th).astype(int), 0, th - 1)
        texel = tex[tv, tu]
        zb = self.z[y0:y1 + 1, x0:x1 + 1]
        m = dentro & (texel[..., 3] > 25) & (z < zb)
        if not m.any():
            return
        sl = (slice(y0, y1 + 1), slice(x0, x1 + 1))
        self.alb[sl][m] = texel[..., :3][m] / 255.0 * osc
        et = emis_tex[tv, tu]
        self.emis[sl][m] = (et[..., :3] / 255.0 * (et[..., 3:4] / 255.0))[m]
        self.nrm[sl][m] = n
        P = [np.asarray(p, np.float32) for p in P]
        self.pos[sl][m] = (w1[..., None] * P[0] + w2[..., None] * P[1] + w3[..., None] * P[2])[m]
        self.alfa[sl][m] = 1.0
        zb[m] = z[m]


def pose_cara(s):
    """s: segundos del plano. Antes de abrir los ojos, la cabeza gacha y los
    ojos cerrados (una rendija); los abre de golpe, la alza un poco y chilla."""
    ab = s - 0.45
    if ab < 0:
        abre = 0.06
    elif ab < 0.07:
        abre = 0.06 + 1.19 * ab / 0.07
    else:
        abre = 1.25 - 0.25 * suave((ab - 0.07) / 0.12)
    gr = suave((s - 1.02) / 0.14)              # el chillido
    temb = math.sin(s * 63.0) * 1.5 * gr * (1 - suave((s - 2.2) / 0.3))
    alza = suave((s - 0.5) / 0.6)
    pose = {n: {'oculto': True} for n in OCULTAS}
    pose.update({
        'torso': {'rot': (6 - 10 * gr, 0, 0)},
        'cuello': {'rot': (8 - 8 * alza - 6 * gr, 0, 0)},
        'cabeza': {'rot': (12 - 9 * alza - 20 * gr + temb, 3 * math.sin(s * 0.8), temb * 0.4)},
        'mandibula': {'rot': (3 + 40 * gr + temb * 1.2, 0, 0)},
        'ojo_izq': {'esc': (1.0 + 0.15 * gr, abre, 1.0)},
        'ojo_der': {'esc': (1.0 + 0.15 * gr, abre, 1.0)},
    })
    return pose


def cara(s, d):
    pose = pose_cara(s)
    M = vr.entidad_a_mundo(0, 0, 0, 0, nj.ESCALA)

    def mundo(pieza, local=(0, 0, 0)):
        return (M @ np.array([*nj.punto(pose, pieza, local), 1.0]))[:3]

    cab = mundo('cabeza', (0, -6.5, 0))
    acerca = suave(s / d)
    gr = suave((s - 1.02) / 0.14)
    r = random.Random(int(s * 997) + 3)
    ojo_c = cab + np.array([1.6 - 0.25 * acerca, -0.95, -4.9 + 1.0 * acerca])
    obj = cab + np.array([0.1, 0.2, 0.0])
    sac = 0.07 * gr * (1 - suave((s - 2.1) / 0.4))
    if sac > 0:
        ojo_c = ojo_c + np.array([r.uniform(-1, 1), r.uniform(-1, 1), 0]) * sac
        obj = obj + np.array([r.uniform(-1, 1), r.uniform(-1, 1), 0]) * sac * 1.8
    cam = CamT(ojo_c, obj, 40.0, -0.04)

    # la luz de los ojos: se enciende de golpe al abrirlos y se dispara al chillar
    ab = s - 0.45
    k_ojo = 0.0 if ab < 0 else (1.6 * math.exp(-ab / 0.1) + suave(ab / 0.12)) * (1 + 0.7 * gr)
    k_ojo *= 1.0 + 0.06 * math.sin(s * 37.0)
    k_cor = 0.0 if ab < 0 else (0.08 + 0.22 * gr) * (0.7 + 0.3 * math.sin(s * 9.0))

    lz = LienzoD()
    for Pq, UVq, nombre in nj.quads(pose, UV, ALTO, M):
        c = np.mean(Pq, axis=0)
        if np.linalg.norm(c - cab) > 4.5:
            continue
        n = vr.normal(Pq)
        if n @ (cam.ojo - c) < 0:
            n = -n
        # lo de dentro de la boca (el cuello y la cavidad del pecho) queda en negro
        osc = 0.12 if nombre in ('torso', 'cuello') else 1.0
        if (nombre == 'mandibula' and n[1] > 0.45) or (nombre == 'cabeza' and n[1] < -0.45):
            osc = 0.1                      # la boca por dentro: un pozo negro
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UVq[k] for k in tri], n.astype(np.float32), TEX, BRILLO, osc)

    ojos = [mundo('ojo_izq', (0, 0, -1.2)), mundo('ojo_der', (0, 0, -1.2))]
    corazon = mundo('corazon', (0, 0, -6))
    cian = np.array([0.40, 0.92, 1.0], np.float32)
    luces = [(p, cian, 1.4 * k_ojo, 0.28, 0.0) for p in ojos] + [(p, cian, 0.05 * k_ojo, 1.8, 0.5) for p in ojos]
    luces.append((corazon, C_MAGENTA, 1.2 * k_cor, 1.2, 0.3))
    # al chillar, la maldicion le sube por la garganta: la boca brilla por dentro
    garganta = mundo('mandibula', (0, -2.5, -5))
    k_boca = 0.55 * gr * (1 - 0.5 * suave((s - 2.0) / 0.5)) * (0.85 + 0.15 * math.sin(s * 21.0))
    luces.append((garganta, C_MAGENTA, 0.9 * k_boca, 0.45, 0.4))
    col = np.zeros((H, W, 3), np.float32)
    for p, c, k, rad, envol in luces:
        if k <= 0:
            continue
        L = p[None, None].astype(np.float32) - lz.pos
        dist = np.sqrt((L * L).sum(2)) + 1e-4
        ndl = np.clip(((lz.nrm * L).sum(2) / dist + envol) / (1 + envol), 0, 1)
        col += lz.alb * c[None, None] * (k * ndl / (1 + (dist / rad) ** 2))[..., None]
    k_em = 0.0 if ab < 0 else min(1.0, ab / 0.05) * (0.85 + 0.45 * gr)
    col += lz.emis * k_em * np.array([0.8, 1.0, 1.0], np.float32)
    col *= lz.alfa[..., None]

    # el agua alrededor: negra; solo se ve donde la alumbran los ojos
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) if 'mg' not in _CACHE else _CACHE['mg']
    _CACHE['mg'] = (yy, xx)
    halo = np.zeros((H, W), np.float32)
    for p in ojos:
        x, y, z = cam.proyectar(p)
        rr = np.hypot(xx - x, yy - y) / H
        halo += np.exp(-(rr / 0.09) ** 2) * 0.35 + np.exp(-(rr / 0.35) ** 2) * 0.12
    fondo = halo[..., None] * np.array([0.05, 0.42, 0.48], np.float32) * k_ojo
    x, y, z = cam.proyectar(corazon)
    rr = np.hypot(xx - x, yy - y) / H
    fondo += (np.exp(-(rr / 0.3) ** 2) * 0.25)[..., None] * C_MAGENTA * k_cor
    arr = col + fondo * (1 - lz.alfa[..., None])
    if k_boca > 0:
        x, y, z = cam.proyectar(garganta)
        rr = np.hypot(xx - x, yy - y) / H
        arr += (np.exp(-(rr / 0.06) ** 2) * 0.35 + np.exp(-(rr / 0.18) ** 2) * 0.12)[..., None] * C_MAGENTA * k_boca
    arr = ne.bloom(np.clip(arr, 0, 1), np.clip(lz.emis * k_em, 0, 1),
                   radios=((4 * ESCALA, 0.8), (16 * ESCALA, 0.6), (55 * ESCALA, 0.5)))
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    motas_ojos(img, cam, ojos, k_ojo, s)
    if gr > 0:
        chillido(img, cam, mundo('mandibula', (0, 2, -9)), s - 1.02, ojos)
    if s > d - 0.12:
        img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, int(255 * suave((s - (d - 0.12)) / 0.1)))))
    return img


def motas_ojos(img, cam, ojos, k, s):
    """Motas del agua, solo visibles cerca de la luz de los ojos."""
    if k <= 0:
        return
    rng = np.random.default_rng(3)
    P = rng.random((900, 3)) * np.array([6.0, 5.0, 5.0]) + (ojos[0] + ojos[1]) / 2 - np.array([3.0, 2.5, 3.6])
    P[:, 1] += -0.08 * s
    P[:, 0] += 0.05 * np.sin(s + P[:, 2] * 3)
    sx, sy, sz = cam.proyectar(P)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for i in range(len(P)):
        if sz[i] < 0.3:
            continue
        dist = min(np.linalg.norm(P[i] - o) for o in ojos)
        b = min(k, 1.3) * 0.9 / (1 + (dist / 0.45) ** 2)
        if b < 0.03:
            continue
        rr = max(0.7, 0.012 * cam.foco / sz[i])
        al = int(min(255, 255 * b))
        d.ellipse((sx[i] - rr, sy[i] - rr, sx[i] + rr, sy[i] + rr), fill=(150, 240, 255, al))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(0.8 * ESCALA)))


def chillido(img, cam, boca, t, ojos):
    """Al chillar: le salen burbujas de la boca hacia la camara y el agua se
    empuja en un anillo que se abre."""
    r = random.Random(17)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for k in range(46):
        t0 = r.uniform(0, 0.7)
        vida = t - t0
        if vida < 0:
            continue
        v = np.array([r.uniform(-1.3, 1.3), r.uniform(-0.2, 1.4), r.uniform(-2.6, -0.8)])
        p = boca + v * vida * 1.6 + np.array([0, 0.5 * vida * vida, 0])
        x, y, z = cam.proyectar(p)
        if z < 0.25:
            continue
        lado = int(max(3, 0.07 * cam.foco / z * r.uniform(0.5, 1.3)))
        if lado > 0.4 * H:
            continue
        sp = sprite(f'nerea_burbuja_{r.randint(0, 1)}.png', lado)
        capa.alpha_composite(sp, (int(x - lado / 2), int(y - lado / 2)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(1.2 * ESCALA)))
    img.alpha_composite(capa)
    # la onda del grito
    bx, by, _ = cam.proyectar(boca)
    for k_, retraso in ((0, 0.0), (1, 0.35)):
        u = (t - retraso) / 1.1
        if 0 < u < 1:
            ar = Image.new('RGBA', img.size, (0, 0, 0, 0))
            rad = W * 0.85 * u ** 0.7
            ImageDraw.Draw(ar).ellipse((bx - rad, by - rad * 0.62, bx + rad, by + rad * 0.62),
                                       outline=(150, 240, 255, int(110 * (1 - u))), width=max(2, int(16 * ESCALA * (1 - u * 0.6))))
            img.alpha_composite(ar.filter(ImageFilter.GaussianBlur(10 * ESCALA)))


# ----------------------------------------------------------------------
#  Cierre: su nombre
# ----------------------------------------------------------------------
def fuente(n, t):
    return ImageFont.truetype('C:/Windows/Fonts/' + n, int(t * ESCALA))


def titulo(s):
    if 'fondo_t' not in _CACHE:
        y = np.linspace(0, 1, H)[:, None, None]
        f = np.array([0.012, 0.06, 0.075]) + (np.array([0.0, 0.008, 0.012]) - np.array([0.012, 0.06, 0.075])) * y ** 0.7
        f = np.broadcast_to(f, (H, W, 3)).copy()
        f += ne.rayos(W, H, 7, n=7)[..., None] * np.array([0.10, 0.34, 0.36]) * 0.6
        _CACHE['fondo_t'] = f
        g = os.path.join(A, 'gui')
        nombre = Image.open(os.path.join(g, 'nerea_barra_nombre.png')).convert('RGBA')
        nombre = nombre.crop(nombre.getbbox())
        k = max(1, int(W * 0.42 / nombre.width))
        _CACHE['nombre'] = nombre.resize((nombre.width * k, nombre.height * k), Image.NEAREST)
        cor = Image.open(os.path.join(g, 'nerea_barra_corazon_1.png')).convert('RGBA')
        _CACHE['corazon'] = cor
        esl = Image.open(os.path.join(g, 'nerea_barra_eslabon.png')).convert('RGBA')
        _CACHE['eslabon'] = esl
    entra = suave(s / 0.7)
    fondo = _CACHE['fondo_t'] * (0.35 + 0.65 * entra)
    img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    n = _CACHE['nombre']
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    x, y = (W - n.width) // 2, int(H * 0.47) - n.height // 2
    capa.alpha_composite(n, (x, y + int((1 - entra) * 18 * ESCALA)))
    # el corazon maldito, latiendo, entre dos eslabones
    lat = 0.0
    for t0 in (0.15, 0.55, 1.35, 1.75):
        if s >= t0:
            lat = max(lat, math.exp(-(s - t0) / 0.12))
    lado = int(150 * ESCALA * (1 + 0.1 * lat))
    cor = _CACHE['corazon'].resize((lado, lado), Image.NEAREST)
    cy = y - int(175 * ESCALA)
    capa.alpha_composite(cor, ((W - lado) // 2, cy - lado // 2))
    esl = _CACHE['eslabon']
    el = esl.resize((max(1, int(esl.width * 8 * ESCALA)), max(1, int(esl.height * 8 * ESCALA))), Image.NEAREST)
    el = el.rotate(90, expand=True)                 # eslabones tumbados, a cada lado del corazon
    for sg in (-1, 1):
        for j in range(3):
            cx_ = W // 2 + sg * int(lado * 0.5 + 10 * ESCALA + (j + 0.5) * el.width * 0.82)
            al = 1.0 - 0.3 * j
            e2 = el.copy()
            e2.putalpha(e2.getchannel('A').point(lambda v, al=al: int(v * al)))
            capa.alpha_composite(e2, (cx_ - el.width // 2, cy - el.height // 2))
    d = ImageDraw.Draw(capa)
    f2 = fuente('Montserrat-Bold.ttf', 26)
    t2 = 'P R Ó X I M A M E N T E'
    if s > 0.9:
        a2 = suave((s - 0.9) / 0.6)
        ty = y + n.height + int(52 * ESCALA)
        d.text(((W - d.textlength(t2, font=f2)) / 2, ty), t2, font=f2, fill=(110, 236, 220, int(255 * a2)))
        lw = int(70 * ESCALA * a2)
        d.rectangle((W // 2 - lw, ty + int(50 * ESCALA), W // 2 + lw, ty + int(54 * ESCALA)), fill=(255, 70, 140, int(255 * a2)))
    capa.putalpha(capa.getchannel('A').point(lambda v: int(v * entra)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(18 * ESCALA)))
    # el latido tine de magenta el agua alrededor del corazon
    if lat > 0.02:
        halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
        rr = int(170 * ESCALA)
        ImageDraw.Draw(halo).ellipse((W // 2 - rr, cy - rr, W // 2 + rr, cy + rr), fill=(255, 40, 120, int(70 * lat * entra)))
        img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(60 * ESCALA)))
    img.alpha_composite(capa)
    salida = suave((2.8 - s) / 0.6)
    if salida < 1:
        img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, int(255 * (1 - salida)))))
    return img


def acabar(img, t):
    """Grado de color, grano, vineta y bandas de cine."""
    if 'vin' not in _CACHE:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _CACHE['vin'] = 1 - 0.55 * np.clip(np.hypot((xx - W / 2) / (W * 0.6), (yy - H / 2) / (H * 0.6)) - 0.35, 0, 1) ** 1.4
    f = np.array(img.convert('RGB')).astype(np.float32) / 255.0
    f *= _CACHE['vin'][..., None]
    f = f * np.array([0.96, 1.0, 1.02], np.float32)
    f += np.random.default_rng(int(t * FPS)).normal(0, 0.008, (H, W, 1)).astype(np.float32)
    f[:BARRA] = 0
    f[H - BARRA:] = 0
    return Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8))


def fotograma(i):
    t = i / FPS
    nombre, s, d = plano_en(t)
    if nombre.startswith('negro'):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    elif nombre == 'titulo':
        img = titulo(s)
    else:
        img = {'descenso': descenso, 'cara': cara}[nombre](s, d)
        if nombre == 'descenso':
            k = suave(s / 0.6)
            if k < 1:
                img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, int(255 * (1 - k)))))
            # al final la luz se acaba del todo
            k = suave((s - (d - 0.35)) / 0.35)
            if k > 0:
                img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, int(255 * k))))
    return acabar(img, t)


# ----------------------------------------------------------------------
#  Sonido: solo los suyos
# ----------------------------------------------------------------------
SR = 48000


def cargar_ogg(nombre):
    x, sr = sf.read(os.path.join(SND, nombre + '.ogg'))
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        n = int(len(x) * SR / sr)
        x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)
    return x


def mezcla():
    n = int(TOTAL * SR)
    pista = np.zeros(n)

    def poner(nombre, t, vol=1.0, dur=None, fundido=0.15, desde=0.0, entrada=0.0, grave=False):
        x = cargar_ogg(nombre)[int(desde * SR):].copy()
        if dur:
            x = x[:int(dur * SR)].copy()
            f = min(len(x), int(fundido * SR))
            x[-f:] *= np.linspace(1, 0, f)
        if entrada:
            e = min(len(x), int(entrada * SR))
            x[:e] *= np.linspace(0, 1, e)
        if grave:          # bajo el agua, mas lejos: se apaga lo agudo
            k = np.exp(-np.arange(64) / 10.0)
            x = np.convolve(x, k / k.sum(), 'same')
        i = int(t * SR)
        x = x[:max(0, n - i)]
        pista[i:i + len(x)] += x * vol

    # el mar: el ambiente, la zambullida y las burbujas
    poner('ambiente1', 0.2, 0.55, dur=5.6, fundido=1.5, entrada=0.6)
    poner('burbujas', 0.75, 0.6)
    poner('burbuja_pompa1', 2.4, 0.25)
    poner('burbuja_pompa2', 3.7, 0.2)
    poner('ambiente2', 4.6, 0.45, dur=4.0, fundido=1.6, entrada=0.8, grave=True)
    # el abismo: el corazon late
    for k, t in enumerate(LATIDOS):
        poner(f'latido{k % 3 + 1}', t, 0.55 + 0.12 * k)
    # los ojos se abren y chilla
    poner('mirada_carga', 8.4 + 0.42, 0.85)
    poner('rugido1', 8.4 + 1.0, 1.0)
    poner('burbuja_revienta1', 8.4 + 1.05, 0.55)
    # su nombre: una cadena que se rompe y el ultimo latido
    poner('cadena_rompe1', 11.4, 0.6)
    poner('latido2', 11.4 + 0.15, 0.5)
    poner('latido3', 11.4 + 0.55, 0.4)
    poner('ambiente3', 11.4, 0.25, dur=2.8, fundido=1.4, entrada=0.4, grave=True)
    pista /= max(1e-9, np.max(np.abs(pista))) / 0.9
    est = np.stack([pista, np.roll(pista, int(0.012 * SR)) * 0.96], axis=1)
    ruta = os.path.join(TRAB, 'teaser.wav')
    sf.write(ruta, est.astype(np.float32), SR)
    return ruta


def main():
    total = int(TOTAL * FPS)
    if MUESTRAS:
        tiempos = [float(x) for x in os.environ.get('TIEMPOS', '1.2,3.0,5.0,6.6,7.6,8.95,9.6,12.5').split(',')]
        ims = [fotograma(int(round(t * FPS))) for t in tiempos]
        w, h = ims[0].size
        hoja = Image.new('RGB', (w * 2, h * ((len(ims) + 1) // 2)), (0, 0, 0))
        for k, im in enumerate(ims):
            hoja.paste(im, ((k % 2) * w, (k // 2) * h))
        hoja.save(SALIDA)
        print('muestras', len(ims))
        return
    for i in range(total):
        ruta = os.path.join(CUADROS, f'{i:04d}.png')
        if os.path.exists(ruta):
            continue
        fotograma(i).save(ruta)
        if i % 24 == 0:
            print('fotograma', i, '/', total, flush=True)
    audio = mezcla()
    r = subprocess.run([FF, '-y', '-v', 'error', '-framerate', str(FPS), '-i', os.path.join(CUADROS, '%04d.png'),
                        '-i', audio, '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-tune', 'grain',
                        '-maxrate', '9M', '-bufsize', '18M', '-pix_fmt', 'yuv420p',
                        '-vf', 'scale=1920:1080:flags=lanczos', '-c:a', 'aac', '-b:a', '224k', '-movflags', '+faststart',
                        '-shortest', SALIDA], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:])
        raise SystemExit(1)
    print('ok', SALIDA)


main()

"""
Teaser de Aeralis: unos 14 segundos, sin voz y casi sin ensenarla.

Un tornado gigante gira sobre la cima en plena tormenta. La camara se acerca;
un relampago, y por un instante, dentro, dos ojos cian. La camara se mete en
la pared del tornado (todo es viento que gira y ruge), sale al ojo de la
tormenta, donde de pronto no se oye nada... y un relampago le ensena la cara:
los ojos se encienden y chilla. Negro. Su nombre en pixel.

La cara se renderiza con la misma malla, texturas y animaciones del juego
(vendaval_juego*.py). El tornado se pinta por pixel lanzando rayos: el techo de
la tormenta que gira, la nube muro, el embudo en capas con estrias en helice,
la falda de polvo, las columnas de la Cima y los relampagos. El sonido se monta
con sus .ogg (aeralis_sonidos.py).

Uso: python aeralis_teaser.py <raiz del proyecto> <carpeta de trabajo> <salida.mp4> [escala]
     python aeralis_teaser.py <raiz> <trabajo> <hoja.png> [escala] --muestras    (unos fotogramas por plano)
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
_argv = sys.argv
sys.argv = [_argv[0], RAIZ, tempfile.mkdtemp()]
_cwd = os.getcwd()
os.chdir(GEN)
import vigia_render as vr
import nerea_escenas as ne
import vendaval_juego as vj
import vendaval_juego_anim as va
import viento_escenas as vs
os.chdir(_cwd)
sys.argv = _argv

FF = imageio_ffmpeg.get_ffmpeg_exe()
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
SND = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/aeralis')
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
FPS = 24
BARRA = int(H * 0.11)        # bandas negras de cine arriba y abajo
os.makedirs(TRAB, exist_ok=True)
CUADROS = os.path.join(TRAB, 'cuadros')
os.makedirs(CUADROS, exist_ok=True)

UV, ALTO = vj.empaquetar()
TEX = vr.cargar(os.path.join(A, 'entity/aeralis/aeralis_f1.png'))
BRILLO = vr.cargar(os.path.join(A, 'entity/aeralis/aeralis_brillo_f1.png'))
PLANOS = set(vj.PLANOS)
_EMIS = {}
_CACHE = {}


def emis(k):
    """La capa de brillo escalada: los ojos se encienden poco a poco."""
    q = round(max(0.0, k), 2)
    if q not in _EMIS:
        t = BRILLO.astype(float)
        t[..., :3] *= min(q, 1.0)
        _EMIS[q] = np.clip(t, 0, 255).astype(np.uint8) if q > 0 else None
    return _EMIS[q]


def suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def destello(t, picos):
    """Relampagos: picos (instante, fuerza) que se apagan en unos fotogramas."""
    v = 0.0
    for t0, k in picos:
        if t >= t0:
            v = max(v, k * math.exp(-(t - t0) / 0.07))
    return v


# ----------------------------------------------------------------------
#  Planos: (nombre, inicio, duracion)
# ----------------------------------------------------------------------
PLANOS_T = [('negro', 0.0, 1.0), ('tornado', 1.0, 5.2), ('dentro', 6.2, 1.9), ('ojo', 8.1, 2.5),
            ('negro2', 10.6, 0.6), ('titulo', 11.2, 3.0)]
TOTAL = 14.2


def plano_en(t):
    for nombre, t0, d in PLANOS_T:
        if t0 <= t < t0 + d:
            return nombre, t - t0, d
    return 'titulo', t - 11.2, 3.0


# ----------------------------------------------------------------------
#  El tornado gigante, por fuera
# ----------------------------------------------------------------------
# Se pinta por pixel, lanzando un rayo desde la camara: el techo de la
# tormenta que gira encima (mesociclon), la nube muro que cuelga de el, el
# embudo en capas translucidas, la falda de polvo de la base, las columnas
# de la Cima del Vendaval, las montanas del horizonte y los relampagos.
# Unidades: bloques. El embudo mide unos 300 de alto; las columnas, 20.
TAU = math.tau
HV0, HV1 = BARRA, H - BARRA            # solo se pinta entre las bandas de cine
TECHO = 370.0                          # base de la tormenta
MURO_Y0 = 258.0                        # base de la nube muro (de ahi cuelga el embudo)
MURO_R = 410.0
POLVO_ALTO, POLVO_R = 135.0, 190.0     # la falda de polvo y escombros

C_TECHO_OSC = np.array([0.030, 0.026, 0.068], np.float32)
C_TECHO_CLARO = np.array([0.25, 0.23, 0.42], np.float32)
C_HORIZ = np.array([0.58, 0.62, 0.84], np.float32)       # la franja clara detras de todo
C_CIAN = np.array([0.45, 0.80, 0.92], np.float32)
C_CIELO_ALTO = np.array([0.09, 0.08, 0.18], np.float32)
C_EMB_OSC = np.array([0.016, 0.015, 0.030], np.float32)
C_EMB_MED = np.array([0.15, 0.14, 0.22], np.float32)
C_EMB_CLARO = np.array([0.30, 0.29, 0.42], np.float32)
C_POLVO = np.array([0.36, 0.32, 0.36], np.float32)
L_CLAVE = np.array([0.55, 0.45, -0.70], np.float32)       # la luz difusa de la tormenta, desde delante
L_CLAVE /= np.linalg.norm(L_CLAVE)
C_ROCA = np.array([0.20, 0.20, 0.25], np.float32)
C_RAYO = np.array([0.80, 0.86, 1.00], np.float32)
C_RAYO_HALO = np.array([0.50, 0.46, 1.00], np.float32)

_TAB = np.random.default_rng(21).random((256, 256)).astype(np.float32)
_TAB1 = np.random.default_rng(22).random(1024).astype(np.float32)


def _ruido(u, v, per=256):
    """Ruido de valor suave; periodico en u con periodo per (para dar la vuelta al embudo)."""
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
    """Ruido fractal. pie: cuanto ruido cabe en un pixel; las octavas mas finas
    que el pixel se apagan a su valor medio (sin esto salen pelos y muare)."""
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


def _deriv(F, angulo=False):
    """Cuanto cambia F de un pixel al vecino (como las derivadas de una GPU);
    NaN donde no hay superficie."""
    dx = np.diff(F, axis=1)
    dy = np.diff(F, axis=0)
    if angulo:
        dx = (dx + np.pi) % TAU - np.pi
        dy = (dy + np.pi) % TAU - np.pi
    dx, dy = np.abs(dx), np.abs(dy)
    gx = np.fmin(np.pad(dx, ((0, 0), (0, 1)), constant_values=np.nan), np.pad(dx, ((0, 0), (1, 0)), constant_values=np.nan))
    gy = np.fmin(np.pad(dy, ((0, 1), (0, 0)), constant_values=np.nan), np.pad(dy, ((1, 0), (0, 0)), constant_values=np.nan))
    return np.nan_to_num(np.fmax(gx, gy), nan=0.0)


def _rayas(fase, pie_periodos):
    """Una raya senoidal que se apaga cuando su periodo no cabe en unos pixeles."""
    k = np.clip(1.5 - 2.5 * pie_periodos, 0, 1)
    return 0.5 + 0.5 * np.sin(fase) * k


def _ruido1(x):
    i = np.floor(x)
    f = x - i
    f = f * f * (3 - 2 * f)
    i0 = i.astype(np.int64) & 1023
    return _TAB1[i0] * (1 - f) + _TAB1[(i0 + 1) & 1023] * f


def _paso(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1)
    return k * k * (3 - 2 * k)


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

    def proyectar(self, p):
        d = np.asarray(p, float) - self.ojo
        x, y, z = d @ self.r, d @ self.u, d @ self.f
        zz = np.maximum(z, 1e-3)
        return W / 2 + self.foco * x / zz, H / 2 - self.foco * y / zz, z

    def rayos(self):
        """Direccion por pixel, con D.f = 1: el parametro del rayo es la profundidad."""
        if 'rej' not in _CACHE:
            xs = np.arange(W, dtype=np.float32) + 0.5 - W / 2
            ys = np.arange(HV0, HV1, dtype=np.float32) + 0.5 - H / 2
            _CACHE['rej'] = (xs[None, :], ys[:, None])
        xs, ys = _CACHE['rej']
        a, b = xs / self.foco, ys / self.foco
        return [(self.f[k] + a * self.r[k] - b * self.u[k]).astype(np.float32) for k in range(3)]


# --- la camara: se acerca despacio y al final el tornado la arrastra hacia su pared
_S = np.linspace(0, 5.6, 2241)
_VEL = np.maximum(70.0 + 16.0 * _S + 130.0 * _paso(4.1, 4.75, _S) - 170.0 * _paso(4.85, 5.4, _S), 8.0)
_Z = -730.0 + np.concatenate([[0.0], np.cumsum((_VEL[1:] + _VEL[:-1]) * 0.5 * np.diff(_S))])


def camara_tornado(s):
    z = float(np.interp(s, _S, _Z))
    k = suave(s / 4.2)
    rush = suave((s - 4.15) / 1.1)
    y = 4.0 + 5.0 * k + 88.0 * rush ** 1.4
    x = 34.0 * (1 - k) + 6.0 * (1 - rush) * k
    obj_y = (96.0 + 30.0 * k) * (1 - rush) + y * rush
    ojo = np.array([x, y, z])
    obj = np.array([2.0 - 8.0 * rush, obj_y, 0.0])
    # el viento la sacude cada vez mas
    sac = 0.25 + 2.2 * rush
    obj = obj + sac * np.array([math.sin(s * 23.0) + 0.6 * math.sin(s * 37.0 + 1.0),
                                math.sin(s * 19.0 + 2.0) + 0.5 * math.sin(s * 41.0), 0.0])
    alabeo = 0.025 * math.sin(s * 0.8) + 0.13 * rush + 0.02 * rush * math.sin(s * 29.0)
    return CamT(ojo, obj, 50.0 + 12.0 * rush, alabeo)


# --- la forma del tornado
def eje(y, tt):
    """El eje se tuerce: la cima va desplazada respecto a la base y ondula."""
    h = np.clip(y / MURO_Y0, 0, 1.1)
    ax = -34.0 * h ** 1.6 + 8.0 * np.sin(h * 5.0 + tt * 0.7) * h
    az = 12.0 * h + 6.0 * np.cos(h * 4.0 + tt * 0.55) * h
    return ax, az


def radio_embudo(y):
    h = np.clip(y / MURO_Y0, 0, 1.15)
    return 54.0 + 16.0 * h + (MURO_R - 70.0) * np.clip((h - 0.42) / 0.58, 0, None) ** 2.3


def giro(y):
    """Velocidad angular: mas rapido donde es estrecho."""
    return 0.6 * 55.0 / radio_embudo(y)


def cilindro(O, Dx, Dy, Dz, radio, tt):
    """Rayo contra una superficie de revolucion: se aproxima por el cilindro que
    tiene el radio de la altura a la que el rayo pasa mas cerca del eje."""
    forma = Dx.shape
    A = Dx * Dx + Dz * Dz + 1e-9
    # descarte rapido: rayos que pasan lejos del eje no tocan nada
    rmax = float(np.max(radio(np.linspace(-20.0, TECHO + 60.0, 160, dtype=np.float32)))) + 55.0
    B0 = O[0] * Dx + O[2] * Dz
    cand = (O[0] ** 2 + O[2] ** 2 - B0 * B0 / A < rmax * rmax) & (-B0 / A > -rmax)
    toca_f = np.zeros(forma, bool)
    tin_f = np.full(forma, np.inf, np.float32)
    tout_f = np.full(forma, np.inf, np.float32)
    q_f = np.ones(forma, np.float32)
    ax_f = np.zeros(forma, np.float32)
    az_f = np.zeros(forma, np.float32)
    if not cand.any():
        return toca_f, tin_f, tout_f, q_f, ax_f, az_f
    Dx, Dy, Dz, A = Dx[cand], Dy[cand], Dz[cand], A[cand]
    ax, az = 0.0, 0.0
    for _ in range(2):
        ox, oz = O[0] - ax, O[2] - az
        ts = -(ox * Dx + oz * Dz) / A
        ax, az = eje(O[1] + ts * Dy, tt)
    ox, oz = O[0] - ax, O[2] - az
    B = ox * Dx + oz * Dz
    ts = -B / A
    rho2 = np.maximum(ox * ox + oz * oz - B * B / A, 0)
    y = O[1] + ts * Dy
    R = radio(y)
    delta = np.sqrt(np.maximum(R * R - rho2, 0) / A)
    toca_f[cand] = (rho2 < R * R) & (ts > 0)
    tin_f[cand] = ts - delta
    tout_f[cand] = ts + delta
    q_f[cand] = np.sqrt(rho2) / R
    ax_f[cand] = ax
    az_f[cand] = az
    return toca_f, tin_f, tout_f, q_f, ax_f, az_f


# --- las columnas de la Cima: bloques de piedra
def _columnas():
    r = random.Random(12)
    cajas = []

    def columna(x, z, alto, ancho=4, rota=True):
        x, z, a, b = float(round(x)), float(round(z)), ancho / 2, ancho / 2 + 1
        cajas.append((x - b, 0, z - b, x + b, 2, z + b))
        cajas.append((x - a, 2, z - a, x + a, alto, z + a))
        for yb in range(9, int(alto) - 3, 9):
            cajas.append((x - a - 0.5, yb, z - a - 0.5, x + a + 0.5, yb + 1, z + a + 0.5))
        if rota:
            cajas.append((x - a, alto, z - a, x + r.choice([0, 1]), alto + r.choice([2, 3, 4]), z + r.choice([-1, 0, 1])))
            for _ in range(3):        # los bloques que se le cayeron
                bx, bz = x + r.uniform(-9, 9), z + r.uniform(-9, 9)
                if abs(bx - x) > b + 1 or abs(bz - z) > b + 1:
                    bx, bz = round(bx), round(bz)
                    cajas.append((bx, 0, bz, bx + r.choice([1, 2]), r.choice([1, 1, 2]), bz + r.choice([1, 2])))
        else:
            cajas.append((x - b, alto, z - b, x + b, alto + 2, z + b))

    for k in range(18):                    # el anillo del ruedo, alrededor del tornado
        ang = k / 18 * TAU + 0.15
        x, z = 175 * math.cos(ang), 175 * math.sin(ang)
        if z < 90 and r.random() < 0.85:
            columna(x, z, r.uniform(14, 30), rota=r.random() < 0.7)
    columna(-62, -430, 27)                 # las que pasan junto a la camara
    columna(78, -545, 36, ancho=6)
    columna(-128, -650, 19, rota=False)
    columna(122, -325, 24)
    columna(-95, -250, 31, ancho=5)
    return np.array(cajas, np.float32)


COLUMNAS = _columnas()


def pintar_columnas(cam, O, D, prof, col, luz_fn):
    """Interseccion rayo-caja por pixel (solo en el recuadro de cada caja)."""
    Dx, Dy, Dz = D
    for c in COLUMNAS:
        esq = np.array([(c[i], c[j], c[k]) for i in (0, 3) for j in (1, 4) for k in (2, 5)], float)
        px, py, pz = cam.proyectar(esq)
        if (pz < 0.5).all():
            continue                     # ya quedo detras de la camara
        if (pz < 0.5).any():
            x0, x1, y0, y1 = 0, W, 0, HV1 - HV0
        else:
            x0, x1 = max(0, int(px.min()) - 1), min(W, int(px.max()) + 2)
            y0, y1 = max(0, int(py.min()) - 1 - HV0), min(HV1 - HV0, int(py.max()) + 2 - HV0)
        if x0 >= x1 or y0 >= y1:
            continue
        sl = (slice(y0, y1), slice(x0, x1))
        dx, dy, dz = Dx[sl], Dy[sl], Dz[sl]
        tmin = np.zeros_like(dx)
        tmax = np.full_like(dx, 1e9)
        eje_n = np.zeros(dx.shape, np.int8)
        for k, dk in enumerate((dx, dy, dz)):
            inv = 1.0 / np.where(np.abs(dk) < 1e-7, 1e-7, dk)
            ta, tb = (c[k] - O[k]) * inv, (c[k + 3] - O[k]) * inv
            lo, hi = np.minimum(ta, tb), np.maximum(ta, tb)
            nuevo = lo > tmin
            eje_n[nuevo] = k
            tmin = np.maximum(tmin, lo)
            tmax = np.minimum(tmax, hi)
        m = (tmax >= tmin) & (tmin > 0.05) & (tmin < prof[sl])
        if not m.any():
            continue
        t = tmin[m]
        P = [O[k] + t * d[m] for k, d in enumerate((dx, dy, dz))]
        e = eje_n[m]
        n = np.zeros((len(t), 3), np.float32)
        sg = -np.sign(np.stack([dx[m], dy[m], dz[m]], 1)[np.arange(len(t)), e])
        n[np.arange(len(t)), e] = sg
        # bloques: una piedra por bloque con su junta
        uu = np.where(e == 0, P[2], P[0])
        vv = np.where(e == 1, P[2], P[1])
        bu, bv = np.floor(uu + 1e-3), np.floor(vv + 1e-3)
        tono = _TAB[(bv.astype(np.int64) + e * 37) & 255, bu.astype(np.int64) & 255]
        fu, fv = uu - bu, vv - bv
        junta = _paso(0.0, 0.07, np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv)))
        det = np.clip(1.6 - t / cam.foco * 9.0, 0, 1)
        alb = C_ROCA * ((0.78 + 0.45 * (tono - 0.5) * det) * (1 - 0.45 * (1 - junta) * det))[:, None]
        alb = alb * (1.0 + 0.25 * (e == 1))[:, None]
        rgb = alb * luz_fn(np.stack(P, 1), n)
        niebla = (1 - np.exp(-t / 2600.0))[:, None]
        rgb = rgb * (1 - niebla) + C_HORIZ * 0.55 * niebla
        sub = col[sl]
        sub[m] = rgb
        sp = prof[sl]
        sp[m] = t


# --- relampagos
def rayo_mundo(p0, p1, semilla, ramas=4):
    """Canal del rayo por desplazamiento del punto medio, con ramas."""
    r = random.Random(semilla)

    def partir(a, b, prof, desv):
        if prof == 0:
            return [a, b]
        m = (a + b) / 2 + np.array([r.gauss(0, 1), r.gauss(0, 0.5), r.gauss(0, 1)]) * desv
        return partir(a, m, prof - 1, desv * 0.5)[:-1] + partir(m, b, prof - 1, desv * 0.5)

    p0, p1 = np.array(p0, float), np.array(p1, float)
    largo = np.linalg.norm(p1 - p0)
    tronco = partir(p0, p1, 7, largo * 0.09)
    trazos = [(tronco, 1.0)]
    for _ in range(ramas):
        i = r.randint(len(tronco) // 6, len(tronco) * 3 // 4)
        a = tronco[i]
        dirr = (p1 - p0) / largo * 0.6 + np.array([r.uniform(-1, 1), r.uniform(-0.6, 0.1), r.uniform(-1, 1)])
        b = a + dirr * largo * r.uniform(0.18, 0.38)
        trazos.append((partir(a, b, 5, largo * 0.035), 0.5))
    return trazos


# Relampagos: (instantes y fuerzas, posicion de la luz, rayo visible o no)
RELAMPAGOS = [
    ([(0.75, 0.95), (0.83, 0.45), (0.92, 0.7)], (560.0, 330.0, 620.0), ('tierra', (600.0, TECHO, 700.0), (520.0, 0.0, 560.0), 31)),
    ([(2.18, 0.28), (2.27, 0.16)], (-1400.0, 420.0, 2600.0), None),
    ([(3.45, 1.0), (3.53, 0.5), (3.62, 0.75)], (-260.0, 400.0, 160.0),
     ('techo', (-1300.0, TECHO - 4, 1500.0), (250.0, TECHO - 4, -150.0), 47)),
    ([(4.72, 0.33)], (900.0, 420.0, 900.0), None),
    ([(1.62, 0.16)], (-2200.0, 380.0, 3200.0), None),           # fogonazos lejanos, sin trueno
    ([(2.92, 0.2), (2.99, 0.12)], (1800.0, 380.0, 2600.0), None),
    ([(4.12, 0.18)], (-900.0, 380.0, 1800.0), None),
    ([(4.97, 0.45), (5.05, 0.3), (5.13, 0.4)], (80.0, 330.0, -380.0), None),  # alumbra la pared al llegar
]


def luces_relampago(s):
    out = []
    for picos, pos, rayo in RELAMPAGOS:
        f = destello(s, picos)
        if f > 0.01:
            out.append((f, np.array(pos, np.float32), rayo))
    return out


def iluminar_t(P, n, luces, amb, rim=None):
    """Luz de los relampagos sobre puntos P (N,3) con normal n (N,3)."""
    c = np.broadcast_to(amb, (len(P), 3)).astype(np.float32).copy()
    for f, pos, _ in luces:
        L = pos - P
        dist = np.sqrt((L * L).sum(1)) + 1e-3
        lam = np.clip((n * L).sum(1) / dist, 0, 1)
        aten = f / (1 + (dist / 900.0) ** 2)
        c += (C_RAYO * 1.6)[None] * (lam * aten)[:, None] + (C_RAYO_HALO * 0.18 * f)[None]
    return c


# --- el decorado de fondo: techo, nube muro, cielo, montanas y suelo
def _fbm1(x, oct=5):
    s, amp, tot = 0.0, 1.0, 0.0
    for k in range(oct):
        s = s + amp * _ruido1(x * (2 ** k) + 37.0 * k)
        tot += amp
        amp *= 0.5
    return s / tot


def fondo_tornado(cam, D, tt, luces):
    Dx, Dy, Dz = D
    O = cam.ojo
    hv = Dx.shape
    col = np.zeros(hv + (3,), np.float32)
    prof = np.full(hv, np.inf, np.float32)
    lon = np.sqrt(Dx * Dx + Dy * Dy + Dz * Dz)
    elev = Dy / lon
    frente = np.clip(Dz / np.sqrt(Dx * Dx + Dz * Dz + 1e-9), -1, 1)
    # el cielo abierto (solo se ve por la franja del horizonte, detras de la tormenta)
    franja = np.exp(-np.maximum(elev, 0) / 0.06)
    tono = (0.5 + 0.5 * frente)[..., None]
    cian = np.exp(-(np.arctan2(Dx, Dz) / 0.3) ** 2)[..., None] * franja[..., None]
    col[:] = C_CIELO_ALTO + (C_HORIZ * tono - C_CIELO_ALTO) * franja[..., None] + (C_CIAN - C_HORIZ) * 0.45 * cian
    axT, azT = eje(np.float32(MURO_Y0), tt)
    flash = sum(f for f, _, _ in luces)

    def luz_nube(X, Z, base):
        """Los relampagos alumbran la nube por dentro alrededor de donde caen."""
        extra = np.zeros(X.shape + (3,), np.float32)
        for f, pos, _ in luces:
            d2 = (X - pos[0]) ** 2 + (Z - pos[2]) ** 2
            extra += (C_RAYO * 1.5 * f)[None] * np.exp(-d2 / (2 * 1000.0 ** 2))[:, None] * (0.2 + base[:, None] ** 1.5 * 1.3)
        return extra

    # 1) el techo de la tormenta, que gira: brazos en espiral, anillos y bultos
    m = Dy > 1e-4
    t = np.minimum((TECHO - O[1]) / Dy[m], 2e5)
    X, Z = O[0] + t * Dx[m], O[2] + t * Dz[m]
    rx, rz = X - axT, Z - azT
    rho = np.sqrt(rx * rx + rz * rz) + 1.0
    phi = np.arctan2(rz, rx)
    rot = tt * 0.08 * np.minimum(1.0, 650.0 / rho)
    lr = np.log(rho / 400.0)
    pie_m = t / cam.foco / np.maximum(elev[m], 0.015)
    bandas = _fbm((phi + rot + lr * 1.9) / TAU * 4, lr * 6.0, oct=5, per=4, pie=pie_m * 6.5 / rho)
    cr, sr = np.cos(rot), np.sin(rot)
    bultos = _fbm((rx * cr - rz * sr) / 230.0, (rx * sr + rz * cr) / 230.0, oct=5, pie=pie_m / 230.0)
    anillos = _rayas(rho / 75.0 + bultos * 5.0, pie_m / 470.0)
    cerca = np.exp(-((rho - 700.0) / 450.0) ** 2)
    val = 0.5 * bandas + 0.5 * bultos + 0.12 * cerca * (anillos - 0.5)
    val = np.clip((val - 0.32) * 2.3, 0, 1)
    c = C_TECHO_OSC + (C_TECHO_CLARO - C_TECHO_OSC) * (val ** 1.3)[:, None]
    c *= (1 - 0.45 * np.exp(-(rho / 1100.0) ** 2))[:, None]
    c += luz_nube(X, Z, val)
    borde = 6500.0 * (0.85 + 0.3 * _ruido1(phi * 3.0 + 40.0))
    hay = _paso(borde, borde * 0.88, rho)
    niebla = (1 - np.exp(-t / 2700.0))[:, None]
    cielo = col[m]
    c = c * (1 - niebla) + (cielo * 0.7 + C_HORIZ * 0.22) * niebla
    col[m] = cielo * (1 - hay[:, None]) + c * hay[:, None]
    prof[m] = np.where(hay > 0.5, t, np.inf)

    # 2) la nube muro: un plato enorme que cuelga y gira, con repisas
    def radio_muro(y):
        k = np.clip((y - MURO_Y0) / (TECHO - MURO_Y0), 0, 1)
        return MURO_R + 60.0 * k - 34.0 * np.sqrt(((y - MURO_Y0) / 27.0) % 1.0)

    toca, t_in, _, q, _, _ = cilindro(O, Dx, Dy, Dz, radio_muro, tt)
    yin = O[1] + t_in * Dy
    lado = toca & (yin > MURO_Y0) & (yin < TECHO) & (t_in < prof) & (t_in > 0)
    # la panza: el plano de abajo
    tp = (MURO_Y0 - O[1]) / np.where(np.abs(Dy) < 1e-6, 1e-6, Dy)
    Xp, Zp = O[0] + tp * Dx, O[2] + tp * Dz
    rp = np.sqrt((Xp - axT) ** 2 + (Zp - azT) ** 2)
    php = np.arctan2(Zp - azT, Xp - axT)
    panza = (tp > 0) & (rp < MURO_R * (0.92 + 0.12 * _ruido1(php * 5.0 + tt * 0.4))) & (tp < prof)
    usar_panza = panza & (~lado | (tp < t_in))
    lado &= ~usar_panza
    if lado.any():
        t = t_in[lado]
        X, Y, Z = O[0] + t * Dx[lado], yin[lado], O[2] + t * Dz[lado]
        ph = np.arctan2(Z - azT, X - axT) + tt * 0.075
        rep = ((Y - MURO_Y0) / 27.0) % 1.0
        Y2 = np.where(lado, yin, np.nan)
        pie = _deriv(Y2)[lado] / 6.0
        n1 = _fbm(ph / TAU * 16 + Y / 80.0, Y / 6.0, oct=5, per=16, pie=np.maximum(pie, 16 * 0.002))
        val = np.clip(0.15 + 0.85 * (1 - rep) ** 0.7 * n1 * 1.3, 0, 1)
        c = C_EMB_OSC + (C_TECHO_CLARO * 1.25 - C_EMB_OSC) * val[:, None]
        qq = q[lado]
        c += (C_HORIZ * 0.4)[None] * (qq ** 6)[:, None]
        c += luz_nube(X, Z, val)
        niebla = (1 - np.exp(-t / 4600.0))[:, None]
        col[lado] = c * (1 - niebla) + C_HORIZ * 0.5 * niebla
        prof[lado] = t
    if usar_panza.any():
        t = tp[usar_panza]
        X, Z = Xp[usar_panza], Zp[usar_panza]
        r_ = rp[usar_panza]
        ph = php[usar_panza] + tt * 0.09 * np.minimum(1.0, 200.0 / r_)
        pie_m = t / cam.foco / np.maximum(np.abs(elev[usar_panza]), 0.015)
        n1 = _fbm((ph + np.log(r_ / 60.0) * 1.4) / TAU * 8, r_ / 30.0, oct=5, per=8, pie=pie_m / 30.0)
        val = np.clip(n1 * 1.4 - 0.3, 0, 1)
        c = C_EMB_OSC * 0.7 + (C_EMB_MED - C_EMB_OSC) * (val ** 1.4)[:, None]
        c *= (0.55 + 0.45 * np.clip(r_ / MURO_R, 0, 1))[:, None]
        c += luz_nube(X, Z, val) * 0.8
        niebla = (1 - np.exp(-t / 4600.0))[:, None]
        col[usar_panza] = c * (1 - niebla) + C_HORIZ * 0.5 * niebla
        prof[usar_panza] = t

    # 3) montanas: dos sierras en el horizonte (mas clara la de atras), con un valle detras del tornado
    for zm, alto, sem, osc in ((6500.0, 520.0, 3.0, 0.6), (3400.0, 210.0, 9.0, 0.3)):
        ok = Dz > 1e-3
        t = np.where(ok, (zm - O[2]) / np.where(ok, Dz, 1.0), np.inf)
        X, Y = O[0] + t * Dx, O[1] + t * Dy
        f = _fbm1(X / 2600.0 + sem * 11.0, 6)
        perfil = alto * np.clip((f - 0.33) * 2.8, 0.04, 1.3) ** 1.25
        perfil *= 0.35 + 0.65 * _paso(300.0, 2200.0, np.abs(X - 150.0))
        mm = ok & (Y < perfil) & (t < prof) & (Y > -500)
        if mm.any():
            base = np.clip((perfil[mm] - Y[mm]) / (alto * 0.7), 0, 1)
            c = np.array([0.055, 0.052, 0.10], np.float32) * (0.9 + 0.5 * (1 - base))[:, None]
            # la niebla se pega abajo
            niebla = (osc + (1 - osc) * 0.55 * np.clip(1 - Y[mm] / (alto * 0.35), 0, 1))[:, None]
            c = c * (1 - niebla) + col[mm] * 0.85 * niebla
            # el filo de la sierra se recorta con los relampagos
            filo = np.exp(-(perfil[mm] - Y[mm]) / (alto * 0.03))
            c += (C_RAYO * 0.45)[None] * ((0.15 + flash) * filo)[:, None]
            col[mm] = c
            prof[mm] = t[mm]

    # 4) el suelo de la meseta: bloques de roca, mojados por la lluvia
    m = (Dy < -1e-5)
    t = -O[1] / Dy[m]
    vale = t < prof[m]
    idx = np.nonzero(m)
    m2 = (idx[0][vale], idx[1][vale])
    t = t[vale]
    X, Z = O[0] + t * Dx[m2], O[2] + t * Dz[m2]
    bx, bz = np.floor(X), np.floor(Z)
    tono = _TAB[bz.astype(np.int64) & 255, bx.astype(np.int64) & 255]
    fx, fz = X - bx, Z - bz
    junta = _paso(0.0, 0.06, np.minimum(np.minimum(fx, 1 - fx), np.minimum(fz, 1 - fz)))
    pie = t / cam.foco
    det = np.clip(1.5 - pie * 7.0, 0, 1)
    manchas = _fbm(X / 30.0, Z / 30.0, oct=3)
    alb = C_ROCA * ((0.8 + 0.6 * (tono - 0.5) * det) * (1 - 0.5 * (1 - junta) * det))[:, None]
    alb = alb * (0.7 + 0.6 * manchas)[:, None] + np.array([0.0, 0.04, 0.045], np.float32) * np.clip(manchas - 0.55, 0, 1)[:, None]
    ax0, az0 = eje(np.float32(0), tt)
    rho = np.sqrt((X - ax0) ** 2 + (Z - az0) ** 2)
    sombra = 1 - 0.5 * np.exp(-(rho / 450.0) ** 2)
    P = np.stack([X, np.zeros_like(X), Z], 1)
    nrm = np.tile(np.array([0, 1, 0], np.float32), (len(X), 1))
    luz = iluminar_t(P, nrm, luces, np.array([0.42, 0.42, 0.58], np.float32))
    c = alb * luz * sombra[:, None]
    # suelo mojado: refleja la franja clara del horizonte a ras, y los charcos el cielo
    raso = np.clip(1 + elev[m2] * 9.0, 0, 1) ** 5
    charco = np.clip((manchas - 0.58) * 6, 0, 1) * det
    c += C_HORIZ * ((0.26 * raso + 0.12 * charco) * (0.6 + 0.4 * tono))[:, None]
    c += (C_RAYO * 0.25 * flash)[None] * (raso + charco)[:, None]
    niebla = (1 - np.exp(-t / 2400.0))[:, None]
    c = c * (1 - niebla) + col[m2] * 0.85 * niebla
    col[m2] = c
    prof[m2] = t
    return col, prof


def capa_embudo(cam, D, tt, prof, radio, color_fn, cara='frente'):
    """Una capa del embudo (o de la falda de polvo): devuelve (mascara, rgb, alfa, t)."""
    Dx, Dy, Dz = D
    O = cam.ojo
    toca, t_in, t_out, q, ax, az = cilindro(O, Dx, Dy, Dz, radio, tt)
    t = np.where(t_in > 0.5, t_in, np.inf) if cara == 'frente' else np.where(t_out > 0.5, t_out, np.inf)
    m = toca & (t < prof)
    if not m.any():
        return None
    t2 = np.where(m, t, np.nan)
    Y2 = O[1] + t2 * Dy
    ph2 = np.arctan2(O[2] + t2 * Dz - az, O[0] + t2 * Dx - ax)
    pY, pA = _deriv(Y2)[m], _deriv(ph2, angulo=True)[m]      # metros y radianes por pixel
    t = t[m]
    X, Y, Z = O[0] + t * Dx[m], O[1] + t * Dy[m], O[2] + t * Dz[m]
    axm = ax[m] if np.ndim(ax) else ax
    azm = az[m] if np.ndim(az) else az
    rx, rz = X - axm, Z - azm
    phi = np.arctan2(rz, rx)
    qq = q[m]
    a, rgb = color_fn(X, Y, Z, phi, qq, t, rx, rz, pY, pA)
    return m, rgb, a, t


def sobre(col, m, rgb, a):
    a = np.clip(a, 0, 1)[:, None]
    col[m] = col[m] * (1 - a) + rgb * a


def tornado(s, d):
    tt = 1.0 + s
    cam = camara_tornado(s)
    D = cam.rayos()
    luces = luces_relampago(s)
    flash = sum(f for f, _, _ in luces)
    col, prof = fondo_tornado(cam, D, tt, luces)

    def luz_cols(P, n):
        amb = np.array([0.22, 0.22, 0.32], np.float32) + np.array([0.12, 0.12, 0.2], np.float32) * np.clip(n[:, 1:2], 0, 1)
        return iluminar_t(P, n, luces, amb)

    # el rayo visible: lejos, detras de las columnas y del embudo
    rayos_vis = [(f, r) for f, _, r in luces if r is not None]
    if rayos_vis:
        col = dibujar_rayos(cam, col, rayos_vis)
    pintar_columnas(cam, cam.ojo, D, prof, col, luz_cols)

    vista_rim = C_HORIZ * 0.9
    C_LAV = np.array([0.62, 0.62, 0.85], np.float32)

    def tinte_fondo(rgb, t):
        niebla = (1 - np.exp(-t / 2600.0))[:, None]
        return rgb * (1 - niebla) + C_HORIZ * 0.55 * niebla

    def normal_lado(rx, rz, X, Y, Z):
        ln = np.sqrt(rx * rx + rz * rz) + 1e-6
        return np.stack([X, Y, Z], 1), np.stack([rx / ln, np.zeros_like(rx), rz / ln], 1)

    def luz_volumen(P, n, amb, k_clave):
        """Ambiente + la luz difusa de delante (da volumen al cilindro) + relampagos."""
        lam = np.clip(n @ L_CLAVE, 0, 1)
        return iluminar_t(P, n, luces, amb) + C_LAV[None] * (k_clave * lam)[:, None]

    # --- la falda de polvo y escombros de la base
    def radio_polvo(y):
        k = np.clip(y / POLVO_ALTO, 0, 1)
        return POLVO_R * np.maximum(1 - k * k, 0) ** 0.6 * (0.82 + 0.3 * _ruido1(y / 16.0 - tt * 1.1)) + 1e-3

    def color_polvo(X, Y, Z, phi, q, t, rx, rz, pY, pA, atras=False):
        ang = phi + 0.5 * tt
        pie = np.maximum(pA * 64 / TAU, pY / 12.0)
        nb = _fbm(ang / TAU * 64, Y / 12.0 - tt * 0.9, oct=5, per=64, pie=pie)
        arriba = _fbm(ang / TAU * 64, (Y + 2.5) / 12.0 - tt * 0.9, oct=3, per=64, pie=pie)
        relieve = np.clip(0.55 + (arriba - nb) * 7.0, 0.1, 1.3)
        a = (0.92 if not atras else 0.7) * np.clip((nb - 0.3) * 3.2, 0, 1)
        a *= _paso(1.0, 0.55, q + 0.25 * (nb - 0.5)) * _paso(POLVO_ALTO, POLVO_ALTO * 0.25, Y)
        P, n = normal_lado(rx, rz, X, Y, Z)
        luz = luz_volumen(P, n, np.array([0.26, 0.25, 0.33], np.float32), 0.6)
        rgb = C_POLVO * (0.25 + 1.1 * (nb - 0.3))[:, None] * luz * (relieve * (0.55 + 0.45 * np.clip(Y / 60.0, 0, 1)))[:, None]
        rgb += (C_HORIZ * 0.55)[None] * (q ** 3 * nb)[:, None]
        rgb += (C_RAYO * 0.5 * flash)[None] * (q ** 3 * nb)[:, None]
        return a, tinte_fondo(rgb, t)

    capa = capa_embudo(cam, D, tt, prof, radio_polvo, lambda *a: color_polvo(*a, atras=True), cara='atras')
    if capa:
        sobre(col, *capa[:3])

    # --- escombros que orbitan: los de detras del eje
    trozos = escombros(cam, tt, s)
    pintar_escombros(col, trozos, detras=True, luces=luces, flash=flash)

    # --- el embudo: un nucleo denso con estrias que giran y una envoltura deshilachada
    def radio_env(y):
        return radio_embudo(y) * (1.2 + 0.2 * (_ruido1(y / 30.0 - tt * 0.8) - 0.5) + 0.08 * (_ruido1(y / 9.0 - tt * 1.6) - 0.5))

    def radio_nucleo(y):
        return radio_embudo(y) * (0.9 + 0.08 * (_ruido1(y / 22.0 - tt * 0.6 + 50.0) - 0.5))

    def color_envoltura(X, Y, Z, phi, q, t, rx, rz, pY, pA, atras=False):
        w = giro(Y) * 1.3
        ang = phi + w * tt
        n2 = _fbm(ang / TAU * 16, Y / 5.0, oct=4, per=16, pie=np.maximum(pA * 16 / TAU, pY / 5.0))
        vet = _fbm(ang / TAU * 4, Y / 22.0, oct=3, per=4, pie=np.maximum(pA * 4 / TAU, pY / 22.0))
        s3 = _rayas(TAU * Y / 6.0 + 17 * ang + 6.0 * vet, pY / 6.0 + 17 * pA / TAU)
        a = (0.45 if not atras else 0.32) * np.clip((s3 * 0.55 + n2 * 0.7 - 0.55) * 2.6, 0, 1)
        a *= _paso(1.0, 0.72, q + 0.2 * (n2 - 0.5)) * _paso(MURO_Y0 + 8, MURO_Y0 - 30, Y) * np.clip(t / 25.0, 0, 1)
        P, n = normal_lado(rx, rz, X, Y, Z)
        luz = luz_volumen(P, n, np.array([0.24, 0.24, 0.34], np.float32), 0.5)
        rgb = C_EMB_CLARO * (0.35 + 0.85 * n2)[:, None] * luz * (0.7 + 0.3 * np.clip(Y / 200.0, 0, 1))[:, None]
        rgb += vista_rim[None] * (0.6 * q ** 4 * n2)[:, None]
        rgb += (C_RAYO * 0.9 * flash)[None] * (q ** 3)[:, None]
        return a, tinte_fondo(rgb, t)

    capa = capa_embudo(cam, D, tt, prof, radio_env, lambda *a: color_envoltura(*a, atras=True), cara='atras')
    if capa:
        sobre(col, *capa[:3])

    def color_nucleo(X, Y, Z, phi, q, t, rx, rz, pY, pA):
        w = giro(Y)
        ang = phi + w * tt
        # estrias en helice (como un poste de barbero: al girar parecen subir)
        warp = _fbm(ang / TAU * 4, Y / 30.0, oct=3, per=4, pie=np.maximum(pA * 4 / TAU, pY / 30.0))
        grumos = _fbm(ang / TAU * 8 + 0.3, Y / 16.0, oct=5, per=8, pie=np.maximum(pA * 8 / TAU, pY / 16.0))
        s1 = _rayas(TAU * Y / 9.0 + 11 * ang + 5.0 * warp, pY / 9.0 + 11 * pA / TAU)
        s2 = _rayas(TAU * Y / 3.4 + 29 * ang + 7.0 * warp + 3.0 * grumos, pY / 3.4 + 29 * pA / TAU)
        # fibras finas de viento, para cuando la camara se mete
        fibras = _fbm((ang + Y / 40.0) / TAU * 64, Y / 1.3, oct=3, per=64,
                      pie=np.maximum((pA + pY / 40.0) * 64 / TAU, pY / 1.3))
        cuerda = 0.6 * s1 + 0.4 * s2
        v = np.clip((0.36 * cuerda + 0.6 * grumos + 0.34 * fibras - 0.56) * 2.6, 0, 1) ** 1.15
        a = 0.97 * _paso(1.0, 0.86, q + 0.12 * (grumos - 0.5) + 0.05 * (s1 - 0.5)) * _paso(MURO_Y0 + 8, MURO_Y0 - 40, Y)
        P, n = normal_lado(rx, rz, X, Y, Z)
        luz = luz_volumen(P, n, np.array([0.30, 0.29, 0.42], np.float32), 0.7)
        base = C_EMB_OSC + (C_EMB_MED - C_EMB_OSC) * v[:, None]
        polvo = _paso(80.0, 5.0, Y)[:, None]                  # abajo arrastra tierra
        base = base * (1 - polvo) + C_POLVO * (0.45 + 0.7 * v)[:, None] * polvo
        rgb = base * luz * (0.75 + 0.25 * np.clip(Y / 220.0, 0, 1))[:, None]
        rgb += vista_rim[None] * (0.55 * q ** 5 * (0.4 + v))[:, None]
        rgb += (C_RAYO * 0.8 * flash)[None] * (q ** 4 * (0.4 + v))[:, None]
        return a, tinte_fondo(rgb, t)

    capa = capa_embudo(cam, D, tt, prof, radio_nucleo, color_nucleo)
    if capa:
        sobre(col, *capa[:3])
    # el huevo de pascua: dos ojos cian dentro del tornado, tres fotogramas
    if 3.5 <= s < 3.5 + 3 / FPS:
        col = ojos_en_tornado(cam, col, tt)
    capa = capa_embudo(cam, D, tt, prof, radio_env, color_envoltura)
    if capa:
        sobre(col, *capa[:3])
    capa = capa_embudo(cam, D, tt, prof, radio_polvo, color_polvo)
    if capa:
        sobre(col, *capa[:3])
    pintar_escombros(col, trozos, detras=False, luces=luces, flash=flash)

    # --- a pantalla completa, con una curva que levanta los medios sin quemar los relampagos
    col = np.maximum(col, 0)
    col = col * 1.32 / (1 + 0.32 * col)
    full = np.zeros((H, W, 3), np.float32)
    full[HV0:HV1] = col
    img = Image.fromarray((np.clip(full, 0, 1) * 255).astype(np.uint8))
    # brillo de lo mas claro (relampagos, franja)
    luma = np.clip((full.max(axis=2) - 0.55) * 2.0, 0, 1)
    if luma.any():
        b = Image.fromarray((luma[..., None] * full * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(22 * ESCALA))
        img = Image.fromarray(np.clip(np.array(img).astype(np.int16) + (np.array(b) * 0.7).astype(np.int16), 0, 255).astype(np.uint8))
    img = img.convert('RGBA')
    rush = suave((s - 4.3) / 0.9)
    if rush > 0.02:
        # el tiron: desenfoque radial hacia fuera
        for e, al in ((1.012 + 0.02 * rush, int(70 * rush)), (1.03 + 0.035 * rush, int(40 * rush))):
            big = img.resize((int(W * e), int(H * e)), Image.BILINEAR)
            off = ((big.width - W) // 2, (big.height - H) // 2)
            cp = big.crop((off[0], off[1], off[0] + W, off[1] + H))
            cp.putalpha(al)
            img.alpha_composite(cp)
    lluvia(img, s, flash)
    return img


def dibujar_rayos(cam, col, rayos_vis):
    hv = col.shape[:2]
    nucleo = Image.new('L', (W, hv[0]), 0)
    halo = Image.new('L', (W, hv[0]), 0)
    dn, dh = ImageDraw.Draw(nucleo), ImageDraw.Draw(halo)
    for f, (tipo, p0, p1, sem) in rayos_vis:
        for trazo, peso in rayo_mundo(p0, p1, sem, ramas=4 if tipo == 'tierra' else 7):
            P = np.array(trazo)
            x, y, z = cam.proyectar(P)
            if (z < 1).any():
                continue
            pts = list(zip(x.tolist(), (y - HV0).tolist()))
            g = int(255 * min(1.0, f * 1.3) * (1.0 if peso == 1.0 else 0.7))
            dn.line(pts, fill=g, width=max(1, int((3.4 if peso == 1.0 else 1.8) * ESCALA)))
            dh.line(pts, fill=g, width=max(2, int(14 * ESCALA * peso)))
    n = np.array(nucleo).astype(np.float32) / 255
    h1 = np.array(halo.filter(ImageFilter.GaussianBlur(10 * ESCALA))).astype(np.float32) / 255
    h2 = np.array(halo.filter(ImageFilter.GaussianBlur(55 * ESCALA))).astype(np.float32) / 255
    col = col + n[..., None] * C_RAYO * 1.4 + h1[..., None] * C_RAYO_HALO * 0.9 + h2[..., None] * C_RAYO_HALO * 0.8
    return col


def ojos_en_tornado(cam, col, tt):
    y = 128.0
    ax, az = eje(np.float32(y), tt)
    R = float(radio_embudo(y))
    hacia = cam.ojo - np.array([float(ax), y, float(az)])
    hacia[1] = 0
    hacia /= np.linalg.norm(hacia)
    centro = np.array([float(ax), y, float(az)]) + hacia * R * 0.55
    lado = np.cross(hacia, [0, 1, 0])
    capa = Image.new('L', (W, col.shape[0]), 0)
    d = ImageDraw.Draw(capa)
    for sg in (-1, 1):
        x, yy, z = cam.proyectar(centro + lado * 5.5 * sg)
        rr = max(2.5 * ESCALA, 3.2 * cam.foco / max(float(z), 1.0))
        yy -= HV0
        d.ellipse((x - rr, yy - rr * 0.55, x + rr, yy + rr * 0.55), fill=255)
    n = np.array(capa).astype(np.float32) / 255
    g1 = np.array(capa.filter(ImageFilter.GaussianBlur(6 * ESCALA))).astype(np.float32) / 255
    g2 = np.array(capa.filter(ImageFilter.GaussianBlur(28 * ESCALA))).astype(np.float32) / 255
    ojo = np.array([0.6, 0.95, 1.0], np.float32)
    return col + n[..., None] * ojo + g1[..., None] * ojo * 1.6 + g2[..., None] * C_CIAN * 1.8


def escombros(cam, tt, s):
    """Bloques arrancados que giran alrededor del embudo y suben en espiral."""
    rng = np.random.default_rng(7)
    n = 190
    h0 = 210.0 * rng.random(n) ** 1.8
    sube = rng.uniform(3.0, 10.0, n)
    y = (h0 + sube * tt) % 230.0
    R = radio_embudo(y)
    rad = R * rng.uniform(1.25, 3.2, n) + np.where(y < 60, rng.uniform(0, 60, n), 0)
    w = 0.75 * 45.0 / rad
    ang = rng.uniform(0, TAU, n) - w * tt            # gira hacia el mismo lado que la nube
    lado = rng.uniform(0.5, 2.6, n) ** 1.3
    vuelta = rng.uniform(0, TAU, n) + tt * rng.uniform(-3, 3, n)
    ax, az = eje(y, tt)
    P = np.stack([ax + rad * np.cos(ang), y, az + rad * np.sin(ang)], 1)
    P0 = np.stack([ax + rad * np.cos(ang + w / FPS * 1.5), y - sube / FPS, az + rad * np.sin(ang + w / FPS * 1.5)], 1)
    x, yy, z = cam.proyectar(P)
    x0, y0, z0 = cam.proyectar(P0)
    # detras o delante del eje, visto desde la camara
    eje_p = np.stack([ax, y, az], 1)
    _, _, ze = cam.proyectar(eje_p)
    out = []
    for k in range(n):
        if z[k] < 2 or z0[k] < 2:
            continue
        tam = lado[k] * cam.foco / z[k]
        out.append((x[k], yy[k] - HV0, x0[k], y0[k] - HV0, tam, z[k] > ze[k], vuelta[k], P[k], float(z[k])))
    return out


def pintar_escombros(col, trozos, detras, luces, flash):
    hv = col.shape[:2]
    capa = Image.new('RGBA', (W, hv[0]), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for x, y, x0, y0, tam, atras, giro_, P, z in trozos:
        if atras != detras:
            continue
        if x < -200 or x > W + 200 or y < -200 or y > hv[0] + 200:
            continue
        niebla = 1 - math.exp(-z / 2600.0)
        lit = 0.0
        for f, pos, _ in luces:
            dist = float(np.linalg.norm(pos - P))
            lit += f / (1 + (dist / 900.0) ** 2)
        c = np.array([0.05, 0.048, 0.06]) * (1 + 6 * lit) + np.array([0.3, 0.32, 0.45]) * niebla * 0.55
        rgb = tuple(int(255 * min(1.0, v)) for v in c)
        al = int(255 * (0.55 if detras else 0.9) * (1 - 0.6 * niebla))
        if tam < 1.2:
            d.line([(x0, y0), (x, y)], fill=rgb + (int(al * max(0.35, tam / 1.2)),), width=1)
            continue
        if math.hypot(x - x0, y - y0) > tam * 0.8:
            d.line([(x0, y0), (x, y)], fill=rgb + (al // 3,), width=max(1, int(tam * 0.8)))
        pts = [(x + tam * 0.6 * math.cos(giro_ + k * TAU / 4), y + tam * 0.6 * math.sin(giro_ + k * TAU / 4)) for k in range(4)]
        d.polygon(pts, fill=rgb + (al,))
    a = np.array(capa).astype(np.float32) / 255
    k = a[..., 3:4]
    col[:] = col * (1 - k) + a[..., :3] * k


def lluvia(img, s, flash):
    """Lluvia y polvo que cruzan delante, empujados hacia el tornado."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(int(s * FPS) + 101)
    rush = suave((s - 4.3) / 0.9)
    for _ in range(int(320 * ESCALA + 200 * ESCALA * rush)):
        x, y = r.uniform(-0.1, 1.1) * W, r.uniform(0, 1) * H
        L = r.uniform(18, 70) * ESCALA * (1 + 2.5 * rush)
        ang = 1.25 - 0.9 * rush + r.uniform(-0.06, 0.06)
        a = int(r.uniform(14, 40) * (1 + 2.2 * min(1.0, flash)))
        d.line([(x, y), (x + math.cos(ang) * L * -1, y + math.sin(ang) * L)], fill=(190, 200, 235, min(255, a)),
               width=max(1, int(ESCALA * r.choice([1, 1, 1, 2]))))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(0.5 * ESCALA + 0.3)))


# ----------------------------------------------------------------------
#  Dentro de la pared: viento que gira y se precipita
# ----------------------------------------------------------------------
_RUIDO = np.random.default_rng(5).random((64, 256))


def vortice(t, zoom, luz, centro=(0.5, 0.46), oscuro_centro=0.9):
    """Un tunel de viento visto desde dentro: vetas en espiral que giran y se
    acercan. zoom > 0 hace que la pared se abra hacia la camara."""
    if 'malla' not in _CACHE:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _CACHE['malla'] = (xx, yy)
    xx, yy = _CACHE['malla']
    cx, cy = W * centro[0], H * centro[1]
    dx, dy = (xx - cx) / W, (yy - cy) / W
    r = np.sqrt(dx * dx + dy * dy) + 1e-4
    th = np.arctan2(dy, dx)
    prof = 1.0 / r                       # lo lejano, cerca del centro
    u = (th / math.tau * 256 + prof * 18 + t * 70) % 256
    v = (prof * 6.0 - t * (9.0 + zoom * 30.0)) % 64
    a = _RUIDO[v.astype(int) % 64, u.astype(int) % 256]
    b = _RUIDO[(v * 0.5 + 17).astype(int) % 64, (u * 0.5 + 40).astype(int) % 256]
    veta = np.clip((a * 0.6 + b * 0.6) - 0.35, 0, 1) ** 1.6
    borde = np.clip(r * 3.2, 0, 1) ** (1.0 + oscuro_centro)
    val = (0.08 + 0.95 * veta) * borde * luz
    col = val[..., None] * np.array([0.78, 0.84, 0.98])
    return np.clip(col, 0, 1)


def dentro(s, d):
    k = s / d
    f = destello(s, [(0.9, 0.35)])
    arr = vortice(6.2 + s, 0.6 + k, 0.9 + 1.2 * f, centro=(0.5 + 0.03 * math.sin(s * 3), 0.46))
    img = Image.fromarray((arr * 255).astype(np.uint8)).convert('RGBA')
    # desenfoque de movimiento hacia fuera: copias algo mas grandes encima
    for e, al in ((1.04, 90), (1.09, 60)):
        big = img.resize((int(W * e), int(H * e)), Image.BILINEAR)
        off = ((big.width - W) // 2, (big.height - H) // 2)
        capa = big.crop((off[0], off[1], off[0] + W, off[1] + H))
        capa.putalpha(al)
        img.alpha_composite(capa)
    r = random.Random(int(s * 1000))
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for _ in range(18):
        sp = Image.open(os.path.join(A, 'particle', f'aeralis_polvo_{r.randint(0, 2)}.png')).convert('RGBA')
        lado = int(r.choice([30, 60, 100]) * ESCALA)
        sp = sp.resize((lado, lado), Image.NEAREST)
        capa.alpha_composite(sp, (r.randint(0, W - lado), r.randint(BARRA, H - BARRA - lado)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(6 * ESCALA)))
    vs.estelas(img, 60, r.randint(0, 999), alfa=110)
    return img


# ----------------------------------------------------------------------
#  El ojo de la tormenta: su cara
# ----------------------------------------------------------------------
def mundo(M, pose, pieza, local=(0, 0, 0)):
    return (M @ np.array([*vj.punto(pose, pieza, local), 1.0]))[:3]


def ojo_tormenta(s, d):
    sp = 2.02 + max(0.0, s - 0.55) * 0.5
    pose = va.pose_en('DESPERTAR', sp)
    M = vr.entidad_a_mundo(0, 3.0, 0, 0, vj.ESCALA)
    cab = mundo(M, pose, 'cabeza')
    acerca = suave(s / d)
    ojo = cab + np.array([-0.7, 0.4, -5.6 + 0.9 * acerca])
    obj = cab + np.array([0.0, 0.1, 0.0])
    r = random.Random(int(s * 997) + 7)
    temblor = 1.0 if 0.7 < s < 2.2 else 0.0
    if temblor:
        ojo = ojo + np.array([r.uniform(-1, 1), r.uniform(-1, 1), 0]) * 0.08
        obj = obj + np.array([r.uniform(-1, 1), r.uniform(-1, 1), 0]) * 0.16
    cam = vr.Camara(ojo=tuple(ojo), objetivo=tuple(obj), fov=48, ancho=W, alto=H)
    f = destello(s, [(0.42, 1.0), (0.58, 0.55), (1.6, 0.6)])
    luces = [((0.2, 0.6, 1.0), (0.85, 0.88, 1.0), 0.3 + 3.0 * f, 'contra'),
             ((-0.6, 0.8, -0.6), (0.6, 0.7, 1.0), 0.1 + 1.6 * f, 'llave')]
    amb = np.array([0.02, 0.025, 0.04]) + np.array([0.3, 0.32, 0.4]) * f
    em = emis(0.0 if s < 0.5 else 1.4 * suave((s - 0.5) / 0.25))
    lz = vr.Lienzo(W, H)
    qs = vj.quads(pose, UV, ALTO, M)
    for Pq, UVq, _, mat in [q for q in qs if q[3] not in PLANOS]:
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UVq[k] for k in tri], TEX, luz, em, None, brillo=1.6)
    for Pq, UVq, _, mat in sorted([q for q in qs if q[3] in PLANOS], key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2]):
        luz = 0.03 + 0.9 * vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UVq[k] for k in tri], TEX, luz, None, None, translucido=1.0)
    fondo = vortice(8.1 + s, 0.0, 0.18 + 1.3 * f, centro=(0.5, 0.5), oscuro_centro=0.2)
    alfa = lz.alfa[..., None]
    arr = np.clip(lz.color, 0, 1) * alfa + fondo * (1 - alfa)
    arr = ne.bloom(arr, np.clip(lz.emis, 0, 1), radios=((4 * ESCALA, 0.8), (16 * ESCALA, 0.6), (50 * ESCALA, 0.45)))
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    vs.estelas(img, 26, r.randint(0, 999), alfa=70)
    if temblor:
        # el chillido empuja el aire: una onda que se abre desde su boca
        k = (s - 0.7) / 1.5
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(capa).ellipse((W / 2 - W * k, H * 0.62 - H * k * 0.6, W / 2 + W * k, H * 0.62 + H * k * 0.6),
                                     outline=(200, 235, 255, int(90 * (1 - k))), width=max(2, int(10 * ESCALA)))
        img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(8 * ESCALA)))
    return img


# ----------------------------------------------------------------------
#  Cierre: su nombre
# ----------------------------------------------------------------------
def fuente(n, t):
    return ImageFont.truetype('C:/Windows/Fonts/' + n, int(t * ESCALA))


def titulo(s):
    if 'fondo' not in _CACHE:
        _CACHE['fondo'] = vs.cielo(W, H, H * 0.75, 9, rayos=0.8)
        nombre = Image.open(os.path.join(A, 'gui/aeralis_barra_nombre.png')).convert('RGBA')
        nombre = nombre.crop(nombre.getbbox())
        k = max(1, int(W * 0.5 / nombre.width))
        _CACHE['nombre'] = nombre.resize((nombre.width * k, nombre.height * k), Image.NEAREST)
        nucleo = Image.open(os.path.join(A, 'gui/aeralis_barra_nucleo_1.png')).convert('RGBA')
        _CACHE['nucleo'] = nucleo.resize((int(128 * ESCALA), int(128 * ESCALA)), Image.NEAREST)
    entra = suave(s / 0.7)
    fondo = _CACHE['fondo'] * (0.2 + 0.5 * destello(s, [(0.05, 1.0)]) + 0.08 * entra)
    img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    n = _CACHE['nombre']
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    x, y = (W - n.width) // 2, int(H * 0.44) - n.height // 2
    capa.alpha_composite(n, (x, y + int((1 - entra) * 18 * ESCALA)))
    nu = _CACHE['nucleo'].rotate(-s * 40, resample=Image.NEAREST)
    capa.alpha_composite(nu, ((W - nu.width) // 2, y - nu.height - int(30 * ESCALA)))
    d = ImageDraw.Draw(capa)
    f2 = fuente('Montserrat-Bold.ttf', 26)
    t2 = 'P R Ó X I M A M E N T E'
    if s > 1.0:
        a2 = suave((s - 1.0) / 0.6)
        d.text(((W - d.textlength(t2, font=f2)) / 2, y + n.height + int(50 * ESCALA)), t2, font=f2,
               fill=(120, 214, 255, int(255 * a2)))
    capa.putalpha(capa.getchannel('A').point(lambda v: int(v * entra)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(18 * ESCALA)))
    img.alpha_composite(capa)
    salida = suave((3.0 - s) / 0.6)
    if salida < 1:
        img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, int(255 * (1 - salida)))))
    return img


def acabar(img, t):
    """Grado de color, grano, vineta y bandas de cine."""
    f = np.array(img.convert('RGB')).astype(float) / 255.0
    yy, xx = _CACHE['malla'] if 'malla' in _CACHE else np.mgrid[0:H, 0:W]
    vin = 1 - 0.55 * np.clip(np.hypot((xx - W / 2) / (W * 0.6), (yy - H / 2) / (H * 0.6)) - 0.35, 0, 1) ** 1.4
    f *= vin[..., None]
    f = f * np.array([0.95, 0.98, 1.06])
    f += np.random.default_rng(int(t * FPS)).normal(0, 0.008, (H, W, 1))
    f[:BARRA] = 0
    f[H - BARRA:] = 0
    return Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8))


FUNDIDO = (6.04, 6.25)     # la pared del tornado se convierte en el tunel de dentro


def fotograma(i):
    t = i / FPS
    nombre, s, d = plano_en(t)
    if FUNDIDO[0] <= t < FUNDIDO[1]:
        k = suave((t - FUNDIDO[0]) / (FUNDIDO[1] - FUNDIDO[0]))
        img = Image.blend(tornado(t - 1.0, 5.2), dentro(t - 6.2, 1.9), k)
        return acabar(img, t)
    if nombre.startswith('negro'):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        if nombre == 'negro':
            vs.estelas(img, 8, i, alfa=int(40 * min(1.0, t / 1.0)))
    elif nombre == 'titulo':
        img = titulo(s)
    else:
        img = {'tornado': tornado, 'dentro': dentro, 'ojo': ojo_tormenta}[nombre](s, d)
        # entrada desde negro; el paso de dentro al ojo es un corte seco
        k = min(1.0, s / 0.25) if nombre == 'tornado' else 1.0
        if nombre == 'ojo':
            k = min(1.0, (d - s) / 0.05)
        if k < 1:
            img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, int(255 * (1 - max(0.0, k))))))
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

    def poner(nombre, t, vol=1.0, dur=None, fundido=0.15, desde=0.0, entrada=0.0):
        x = cargar_ogg(nombre)[int(desde * SR):].copy()
        if dur:
            x = x[:int(dur * SR)].copy()
            f = min(len(x), int(fundido * SR))
            x[-f:] *= np.linspace(1, 0, f)
        if entrada:
            e = min(len(x), int(entrada * SR))
            x[:e] *= np.linspace(0, 1, e)
        i = int(t * SR)
        x = x[:max(0, n - i)]
        pista[i:i + len(x)] += x * vol

    # viento que crece hasta el rugido del tornado
    poner('ambiente1', 0.0, 0.5, dur=4.0, fundido=1.5, entrada=0.8)
    for k, t in enumerate((1.0, 3.6)):
        poner(f'tornado{k % 2 + 1}', t, 0.5 + 0.25 * k, dur=3.0, fundido=0.6, entrada=0.4)
    poner('juicio_ciclon', 2.2, 0.8, dur=4.0, fundido=0.2, entrada=1.5)
    poner('trueno2', 1.75, 0.8)
    poner('trueno1', 4.45, 0.75)
    poner('marca1', 4.5, 0.25, dur=0.8, fundido=0.3)
    # dentro: el rugido de lleno y el tiron
    poner('tornado_atrapa1', 6.15, 1.0)
    poner('juicio_ciclon', 6.2, 1.0, dur=1.9, fundido=0.05, desde=3.0)
    # el ojo: de golpe, casi nada; el trueno; el chillido
    poner('juicio_silencio', 8.1, 0.35, dur=0.6, fundido=0.4, desde=2.6)
    poner('trueno3', 8.5, 0.9)
    poner('chillido1', 8.8, 1.0)
    poner('juicio_golpe', 10.55, 0.85, dur=3.0, fundido=1.2, desde=0.5)
    poner('ambiente2', 11.2, 0.3, dur=3.0, fundido=1.5)
    pista /= max(1e-9, np.max(np.abs(pista))) / 0.9
    est = np.stack([pista, np.roll(pista, int(0.012 * SR)) * 0.96], axis=1)
    ruta = os.path.join(TRAB, 'teaser.wav')
    sf.write(ruta, est.astype(np.float32), SR)
    return ruta


def main():
    total = int(TOTAL * FPS)
    if MUESTRAS:
        tiempos = [float(x) for x in os.environ.get('TIEMPOS', '2.0,3.6,4.55,5.9,7.0,8.7,9.6,12.5').split(',')]
        ims = [fotograma(int(t * FPS)) for t in tiempos]
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

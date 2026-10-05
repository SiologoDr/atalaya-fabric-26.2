"""
Teaser de Rajang, el Jaguar de Jade: unos 15 segundos, sin voz y casi sin
ensenarlo hasta el final.

Negro: la tierra retumba muy hondo y algo late. La camara se desliza de noche
por la selva en bloques (bruma, luciernagas verdes, hojas que caen, la luna
que se cuela entre las copas) y sale al claro del templo escalonado, con sus
espirales de oro. Delante, tumbada como una esfinge, una estatua de jade
enorme, apagada, con polvo y musgo encima: es Rajang, dormido. Latido: el sol
de jade de su pecho se enciende y una grieta de luz verde corre por la piedra.
Otro, y otro, cada vez mas seguidos; la costra de piedra se raja y se le
cae... y abre los ojos. Se alza y ruge: la onda barre la plaza, revientan los
pinchos de roca escalonados, la maldicion le raja el jade de la fase I a la IV
y la cresta se vuelve oro. Se encabrita, el cielo se raja en verde y caen los
fragmentos de jade. Negro. Su nombre.

Rajang es la malla del juego (rajang_juego.py) con los atlas y las capas de
brillo de sus fases I y IV, en las poses de sus animaciones
(rajang_juego_anim.py). La selva, el templo, las columnas, los pinchos (como
RajangDibujo) y los fragmentos (como FragmentoJadeRenderer) se rasterizan por
software en un G-buffer (color, brillo, normal y profundidad) que despues se
ilumina por pixel: la luna con la sombra de las copas y la de Rajang, el sol
de su pecho, sus ojos, las grietas y la bruma. El suelo se pinta lanzando
rayos. Las particulas son las suyas (rajang_*). El sonido se monta solo con
sus .ogg (rajang_sonidos.py).

Uso: python rajang_teaser.py <raiz del proyecto> <carpeta de trabajo> <salida.mp4> [escala]
     python rajang_teaser.py <raiz> <trabajo> <hoja.png> [escala] --muestras    (TIEMPOS=1.0,2.5,... en segundos)
     Con PARTE=k/n solo pinta los fotogramas k, k+n, k+2n... (para repartirlos
     entre varios procesos); sin PARTE pinta los que falten, monta el sonido y
     codifica.
"""
import math, os, random, subprocess, sys, tempfile
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

RAIZ, TRAB, SALIDA = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
ESCALA = float(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else 1.0
MUESTRAS = '--muestras' in sys.argv
GEN = os.path.join(RAIZ, 'materiales/generadores')
sys.path.insert(0, GEN)
_argv = sys.argv
sys.argv = [_argv[0], RAIZ, tempfile.mkdtemp()]
_cwd = os.getcwd()
os.chdir(GEN)
import vigia_render as vr
import rajang_juego as rj
import rajang_juego_anim as ra
import tierra_modelo as tm
import tierra_piel as tp
import tierra_escenas as ts
os.chdir(_cwd)
sys.argv = _argv

FF = imageio_ffmpeg.get_ffmpeg_exe()
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
PART = os.path.join(A, 'particle')
ENT = os.path.join(A, 'entity/rajang')
SND = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/rajang')
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
FPS = 24
BARRA = int(H * 0.11)        # bandas negras de cine arriba y abajo
HV0, HV1 = BARRA, H - BARRA  # solo se pinta entre las bandas
HV = HV1 - HV0
os.makedirs(TRAB, exist_ok=True)
CUADROS = os.path.join(TRAB, 'cuadros')
os.makedirs(CUADROS, exist_ok=True)
TAU = math.tau
ZN = 0.08                    # el plano cercano de la camara
_CACHE = {}


def suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _paso(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1)
    return k * k * (3 - 2 * k)


def destello(t, picos, tau=0.07):
    """Picos (instante, fuerza) que se apagan en unos fotogramas."""
    v = 0.0
    for t0, k in picos:
        if t >= t0:
            v = max(v, k * math.exp(-(t - t0) / tau))
    return v


def catmull(claves, s):
    """Interpola posiciones (t, (x, y, z)) con Catmull-Rom."""
    ts_ = [k[0] for k in claves]
    ps = [np.array(k[1], float) for k in claves]
    if s <= ts_[0]:
        return ps[0]
    if s >= ts_[-1]:
        return ps[-1]
    i = max(j for j in range(len(ts_) - 1) if ts_[j] <= s)
    u = (s - ts_[i]) / (ts_[i + 1] - ts_[i])
    p0, p1, p2, p3 = ps[max(0, i - 1)], ps[i], ps[i + 1], ps[min(len(ps) - 1, i + 2)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


# ----------------------------------------------------------------------
#  Planos: (nombre, inicio, duracion)
# ----------------------------------------------------------------------
PLANOS_T = [('negro', 0.0, 1.0), ('selva', 1.0, 5.0), ('pecho', 6.0, 1.5), ('cara', 7.5, 1.5),
            ('rugido', 9.0, 1.7), ('cielo', 10.7, 1.1), ('negro2', 11.8, 0.4), ('titulo', 12.2, 3.0)]
TOTAL = 15.2
# Los latidos de la piedra (segundos del video): el sonido y el pulso del sol del pecho van juntos.
LATIDOS = [0.3, 1.9, 3.5, 5.0, 6.1, 6.75, 7.3, 7.75, 8.12]
T_OJOS = 8.35          # abre los ojos
T_RUGE = 9.75          # ruge (DESPERTAR 2,3 s)
T_IMPACTO = 11.6       # el fragmento que cae delante
# La costra de piedra se cae y las grietas corren desde el pecho: radio
# alcanzado tras cada latido del despertar (bloques)
RADIOS = [(6.1, 0.8), (6.75, 1.5), (7.3, 2.3), (7.75, 3.2), (8.12, 4.2)]


def plano_en(t):
    for nombre, t0, d in PLANOS_T:
        if t0 <= t < t0 + d:
            return nombre, t - t0, d
    return 'titulo', t - 12.2, 3.0


def latido_k(t):
    """El pulso del corazon de jade (con su segundo golpe) a t segundos del video."""
    k = 0.0
    for t0 in LATIDOS:
        dt = t - t0
        if dt >= 0:
            k = max(k, math.exp(-dt / 0.13) + 0.6 * math.exp(-max(0.0, dt - 0.24) / 0.12) * (dt > 0.24))
    return k


# ----------------------------------------------------------------------
#  Ruido (como en los teasers de Aeralis y Nerea)
# ----------------------------------------------------------------------
_TAB = np.random.default_rng(41).random((256, 256)).astype(np.float32)
_TAB1 = np.random.default_rng(42).random(1024).astype(np.float32)


def _ruido(u, v):
    iu, iv = np.floor(u), np.floor(v)
    fu, fv = (u - iu).astype(np.float32), (v - iv).astype(np.float32)
    fu = fu * fu * (3 - 2 * fu)
    fv = fv * fv * (3 - 2 * fv)
    i0 = iu.astype(np.int64) & 255
    i1 = (i0 + 1) & 255
    j0 = iv.astype(np.int64) & 255
    j1 = (j0 + 1) & 255
    a, b, c, d = _TAB[j0, i0], _TAB[j0, i1], _TAB[j1, i0], _TAB[j1, i1]
    return a + (b - a) * fu + (c - a) * fv + (a - b - c + d) * fu * fv


def _fbm(u, v, oct=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for k in range(oct):
        s = s + amp * _ruido(u + 19.0 * k, v + 7.3 * k)
        tot += amp
        amp *= 0.5
        u, v = u * 2, v * 2
    return s / tot


def _ruido1(x):
    i = np.floor(x)
    f = x - i
    f = f * f * (3 - 2 * f)
    i0 = i.astype(np.int64) & 1023
    return _TAB1[i0] * (1 - f) + _TAB1[(i0 + 1) & 1023] * f


def _hash3(ix, iy, iz, s=0):
    h = (ix.astype(np.int64) * 73856093) ^ (iy.astype(np.int64) * 19349663) ^ (iz.astype(np.int64) * 83492791) \
        ^ np.int64((s * 2654435761) % (1 << 31))
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return (h & 0xFFFFFF).astype(np.float32) / np.float32(16777216.0)


def _ruido3(P, escala, s=0):
    """Ruido de valor sobre el cuerpo (P: N x 3): dos planos cruzados del de
    2D, barato y sin costuras a la vista."""
    q = P / escala
    a = _ruido(q[:, 0] * 1.0 + q[:, 2] * 0.62 + 31.0 * s, q[:, 1] * 1.0 - q[:, 2] * 0.37)
    b = _ruido(q[:, 2] * 1.0 - q[:, 0] * 0.45 + 57.0 * s, q[:, 1] * 0.9 + q[:, 0] * 0.33 + 11.0)
    return (a + b) * 0.5


def _hex(s):
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


# ----------------------------------------------------------------------
#  Camara: como vr.Camara (con alabeo), y la direccion de cada pixel
# ----------------------------------------------------------------------
class CamT:
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
        self._D = None

    def proyectar(self, p):
        """Del mundo a la pantalla entera: (x, y, profundidad)."""
        d = np.asarray(p, float) - self.ojo
        x, y, z = d @ self.r, d @ self.u, d @ self.f
        zz = np.maximum(z, 1e-3)
        return W / 2 + self.foco * x / zz, H / 2 - self.foco * y / zz, z

    def rayos(self):
        """Direccion por pixel de la franja visible, con D.f = 1 (el parametro
        del rayo es la profundidad)."""
        if self._D is None:
            if 'rej' not in _CACHE:
                xs = np.arange(W, dtype=np.float32) + 0.5 - W / 2
                ys = np.arange(HV0, HV1, dtype=np.float32) + 0.5 - H / 2
                _CACHE['rej'] = (xs[None, :], ys[:, None])
            xs, ys = _CACHE['rej']
            a, b = xs / self.foco, ys / self.foco
            self._D = [(self.f[k] + a * self.r[k] - b * self.u[k]).astype(np.float32) for k in range(3)]
        return self._D


# ----------------------------------------------------------------------
#  El G-buffer: rasterizado por software que guarda, por pixel, el color de
#  la textura (dos: fase I y fase IV), el brillo (dos), la normal, la
#  profundidad y el grupo; la luz se pone despues (sombrear)
# ----------------------------------------------------------------------
# Grupos: lo de Rajang del 1 al 6, el mundo del 10 en adelante
G_CUERPO, G_ORO, G_SOL, G_OJO, G_CRISTAL, G_BOCA = 1, 2, 3, 4, 5, 6
G_SUELO, G_PIEDRA, G_GLIFO, G_MADERA, G_HOJAS, G_ROCA, G_JADE = 10, 11, 12, 13, 14, 15, 16
GRUPO_MAT = {'jade': G_CUERPO, 'jade_osc': G_CUERPO, 'vientre': G_CUERPO, 'obsidiana': G_CUERPO, 'colmillo': G_CUERPO,
             'oro': G_ORO, 'sol_img': G_SOL, 'ojo': G_OJO, 'cristal': G_CRISTAL, 'boca': G_BOCA}


def _recortar(cs, uv):
    """Sutherland-Hodgman contra el plano cercano (z >= ZN), en el espacio de la camara."""
    out_c, out_uv = [], []
    n = len(cs)
    for i in range(n):
        a, b = cs[i], cs[(i + 1) % n]
        ua, ub = uv[i], uv[(i + 1) % n]
        ina, inb = a[2] >= ZN, b[2] >= ZN
        if ina:
            out_c.append(a)
            out_uv.append(ua)
        if ina != inb:
            k = (ZN - a[2]) / (b[2] - a[2])
            out_c.append(a + (b - a) * k)
            out_uv.append(ua + (ub - ua) * k)
    return out_c, out_uv


class LienzoG:
    def __init__(self, cam):
        self.cam = cam
        self.z = np.full((HV, W), np.inf, np.float32)
        self.alb = np.zeros((HV, W, 3), np.float32)
        self.alb2 = np.zeros((HV, W, 3), np.float32)
        self.em = np.zeros((HV, W, 3), np.float32)
        self.em2 = np.zeros((HV, W, 3), np.float32)
        self.nrm = np.zeros((HV, W, 3), np.float32)
        self.grupo = np.zeros((HV, W), np.uint8)
        self.suma = np.zeros((HV, W, 3), np.float32)     # lo que solo brilla (llamas, estelas)

    def cara(self, P, UV, tex, grupo, n, envolver=False, aditivo=0.0, k_alb=1.0):
        """Un poligono convexo (P: k x 3 en el mundo, UV: k x 2). tex: la pila
        de texturas (h, w, 16): color I, color IV, brillo I, brillo IV."""
        cam = self.cam
        d = np.asarray(P, np.float64) - cam.ojo
        cs = np.stack([d @ cam.r, d @ cam.u, d @ cam.f], 1)
        if cs[:, 2].max() < ZN:
            return
        UV = np.asarray(UV, np.float64)
        if cs[:, 2].min() < ZN:
            cl, cu = _recortar(cs, UV)
            if len(cl) < 3:
                return
            cs, UV = np.array(cl), np.array(cu)
        sx = W / 2 + cam.foco * cs[:, 0] / cs[:, 2]
        sy = H / 2 - cam.foco * cs[:, 1] / cs[:, 2] - HV0
        if sx.max() < 0 or sx.min() > W or sy.max() < 0 or sy.min() > HV:
            return
        for k in range(1, len(cs) - 1):
            i = [0, k, k + 1]
            self._tri(sx[i], sy[i], cs[i, 2], UV[i], tex, grupo, n, envolver, aditivo, k_alb)

    def _tri(self, xs, ys, zs, uv, tex, grupo, n, envolver, aditivo, k_alb):
        x0, x1 = max(int(math.floor(xs.min())), 0), min(int(math.ceil(xs.max())), W - 1)
        y0, y1 = max(int(math.floor(ys.min())), 0), min(int(math.ceil(ys.max())), HV - 1)
        if x0 > x1 or y0 > y1:
            return
        ax, bx, cx = xs
        ay, by, cy = ys
        az, bz, cz = zs
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            return
        gx = (np.arange(x0, x1 + 1, dtype=np.float32) + 0.5 - cx)[None, :]
        gy = (np.arange(y0, y1 + 1, dtype=np.float32) + 0.5 - cy)[:, None]
        l1 = ((by - cy) * gx + (cx - bx) * gy) / den
        l2 = ((cy - ay) * gx + (ax - cx) * gy) / den
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-5) & (l2 >= -1e-5) & (l3 >= -1e-5)
        if not m.any():
            return
        w1, w2, w3 = l1[m] / az, l2[m] / bz, l3[m] / cz
        z = 1.0 / (w1 + w2 + w3)
        bw = x1 - x0 + 1
        idx = np.flatnonzero(m)
        filas, cols = idx // bw + y0, idx % bw + x0
        vis = z < self.z[filas, cols]
        if not vis.any():
            return
        z, w1, w2, w3, filas, cols = z[vis], w1[vis], w2[vis], w3[vis], filas[vis], cols[vis]
        u = (w1 * uv[0, 0] + w2 * uv[1, 0] + w3 * uv[2, 0]) * z
        v = (w1 * uv[0, 1] + w2 * uv[1, 1] + w3 * uv[2, 1]) * z
        th, tw = tex.shape[:2]
        if envolver:
            tu = np.floor(u * tw).astype(np.int64) % tw
            tv = np.floor(v * th).astype(np.int64) % th
        else:
            tu = np.clip((u * tw).astype(np.int64), 0, tw - 1)
            tv = np.clip((v * th).astype(np.int64), 0, th - 1)
        texel = tex[tv, tu]
        if aditivo:
            ok = texel[:, 3] > 2
            t_ = texel[ok].astype(np.float32) / 255.0
            self.suma[filas[ok], cols[ok]] += t_[:, 0:3] * t_[:, 3:4] * aditivo
            return
        ok = texel[:, 3] > 25
        if not ok.any():
            return
        f_, c_ = filas[ok], cols[ok]
        t_ = texel[ok].astype(np.float32) / 255.0
        self.z[f_, c_] = z[ok]
        self.alb[f_, c_] = t_[:, 0:3] * k_alb
        self.alb2[f_, c_] = t_[:, 4:7] * k_alb
        self.em[f_, c_] = t_[:, 8:11] * t_[:, 11:12]
        self.em2[f_, c_] = t_[:, 12:15] * t_[:, 15:16]
        self.nrm[f_, c_] = n
        self.grupo[f_, c_] = grupo


def pila(base, brillo=None, base2=None, brillo2=None):
    """Las cuatro texturas de una superficie, juntas para leerlas de una vez."""
    base = np.asarray(base, np.uint8)
    base2 = base if base2 is None else np.asarray(base2, np.uint8)
    brillo = np.zeros_like(base) if brillo is None else np.asarray(brillo, np.uint8)
    brillo2 = brillo if brillo2 is None else np.asarray(brillo2, np.uint8)
    return np.ascontiguousarray(np.concatenate([base, base2, brillo, brillo2], 2))


# ----------------------------------------------------------------------
#  La sombra de la luna (solo la proyecta Rajang): un mapa de profundidad
#  ortografico desde la luna
# ----------------------------------------------------------------------
class Sombra:
    def __init__(self, L, centro, radio, n=900):
        self.f = -np.asarray(L, float) / np.linalg.norm(L)
        r = np.cross(self.f, [0, 1, 0])
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)
        self.c = np.asarray(centro, float)
        self.n = n
        self.k = n / (2.0 * radio)
        self.z = np.full((n, n), np.inf, np.float32)

    def _a_mapa(self, P):
        d = np.asarray(P, np.float64) - self.c
        return self.n / 2 + (d @ self.r) * self.k, self.n / 2 - (d @ self.u) * self.k, d @ self.f

    def cara(self, P):
        xs, ys, zs = self._a_mapa(P)
        for k in range(1, len(P) - 1):
            i = [0, k, k + 1]
            self._tri(xs[i], ys[i], zs[i])

    def _tri(self, xs, ys, zs):
        n = self.n
        x0, x1 = max(int(math.floor(xs.min())), 0), min(int(math.ceil(xs.max())), n - 1)
        y0, y1 = max(int(math.floor(ys.min())), 0), min(int(math.ceil(ys.max())), n - 1)
        if x0 > x1 or y0 > y1:
            return
        ax, bx, cx = xs
        ay, by, cy = ys
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            return
        gx = (np.arange(x0, x1 + 1) + 0.5 - cx)[None, :]
        gy = (np.arange(y0, y1 + 1) + 0.5 - cy)[:, None]
        l1 = ((by - cy) * gx + (cx - bx) * gy) / den
        l2 = ((cy - ay) * gx + (ax - cx) * gy) / den
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
        if not m.any():
            return
        z = (l1 * zs[0] + l2 * zs[1] + l3 * zs[2]).astype(np.float32)
        sub = self.z[y0:y1 + 1, x0:x1 + 1]
        np.minimum(sub, np.where(m, z, np.inf), out=sub)

    def luz(self, P, sesgo=0.12):
        """Cuanto le llega de luna a cada punto (N x 3), con el borde suave."""
        xs, ys, zs = self._a_mapa(P)
        v = np.zeros(len(P), np.float32)
        n = self.n
        for ox, oy in ((-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)):
            ix = np.clip((xs + ox).astype(np.int64), 0, n - 1)
            iy = np.clip((ys + oy).astype(np.int64), 0, n - 1)
            fuera = (xs + ox < 0) | (xs + ox >= n) | (ys + oy < 0) | (ys + oy >= n)
            v += ((zs - sesgo <= self.z[iy, ix]) | fuera).astype(np.float32)
        return v / 4


# ----------------------------------------------------------------------
#  Texturas: las del mod (Rajang, sus piezas y las particulas) y las de la
#  selva y el templo, pintadas aqui a pixel
# ----------------------------------------------------------------------
UV_RJ, ALTO_RJ = rj.empaquetar()


def _tex(nombre):
    return np.array(Image.open(os.path.join(ENT, nombre + '.png')).convert('RGBA'))


TEX_RJ = pila(_tex('rajang_f1'), _tex('rajang_brillo_f1'), _tex('rajang_f4'), _tex('rajang_brillo_f4'))
TEX_ROCA = pila(_tex('roca'), _tex('roca_brillo'))
TEX_JADE = pila(_tex('fragmento'), _tex('fragmento_brillo'))


def _estela_llama():
    """La llama de la estela con el apagado de la cabeza a la cola (como el juego)."""
    t = _tex('llama').astype(float)
    v = np.linspace(0, 1, t.shape[0])[:, None]
    t[..., 3] *= 230 / 255 * (1 - v)
    return pila(t.astype(np.uint8))


TEX_ESTELA = _estela_llama()
TEX_LLAMA = pila(_tex('llama'))
_MAT = tm.materiales(1)


def _sin_brillo(m):
    return m[0] if isinstance(m, tuple) else m


TEX_TEMPLO = pila(_sin_brillo(_MAT['templo']))
TEX_MADERA = pila(ts.SELVA['madera'])
TEX_HOJAS = pila(ts.SELVA['hojas'])


def _tex_oro_espiral(n=32):
    """Una placa de oro de 2 x 2 bloques con la espiral cuadrada de los
    templos; por los surcos, el brillo verde de la maldicion."""
    r = random.Random(5)
    O = [_hex(c) for c in ('4a3410', '7a5818', 'a8802a', 'd4a63a', 'f2cf6e')]
    esp = tp.espiral_cuadrada(n - 6, n - 6, 4, 0)
    base = np.zeros((n, n, 4), np.uint8)
    brillo = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            canto = x in (0, n - 1) or y in (0, n - 1)
            surco = not canto and (x in (1, 2, n - 3, n - 2) or y in (1, 2, n - 3, n - 2))
            k = r.choice([2, 3, 3, 3, 4])
            if canto:
                k = 4
            elif surco:
                k = 1
            elif 3 <= x < n - 3 and 3 <= y < n - 3:
                if esp[y - 3, x - 3]:
                    k = r.choice([3, 4]) if not esp[max(0, y - 4), x - 3] else r.choice([2, 3, 3])
                else:
                    k = 0
                    brillo[y, x] = (110, 255, 140, 255)
            base[y, x, :3] = (O[k] * 255).astype(np.uint8)
            base[y, x, 3] = 255
    return pila(base, brillo)


TEX_ORO = _tex_oro_espiral()


def _tex_banda_oro(w=32, h=8):
    r = random.Random(6)
    O = [_hex(c) for c in ('4a3410', '7a5818', 'a8802a', 'd4a63a', 'f2cf6e')]
    t = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            g = tp._greca(np.array([x]), np.array([y - 1]), 6)[0] if 1 <= y < h - 1 else False
            k = 4 if y == 0 else (1 if y == h - 1 else (1 if g else r.choice([2, 3, 3])))
            t[y, x, :3] = (O[k] * 255).astype(np.uint8)
            t[y, x, 3] = 255
    return pila(t)


TEX_BANDA = _tex_banda_oro()


def _tex_puerta(n=16):
    """La boca del santuario: negro, con la luz verde que sale de dentro."""
    t = np.zeros((n, n, 4), np.uint8)
    t[..., 3] = 255
    t[..., :3] = (8, 14, 10)
    b = np.zeros((n, n, 4), np.uint8)
    yy, xx = np.mgrid[0:n, 0:n]
    k = np.clip(1 - np.hypot((xx - n / 2 + 0.5) / (n / 2), (yy - n + 0.5) / n) * 1.1, 0, 1)
    b[..., 0] = (40 * k).astype(np.uint8)
    b[..., 1] = (200 * k).astype(np.uint8)
    b[..., 2] = (90 * k).astype(np.uint8)
    b[..., 3] = 255
    return pila(t, b)


TEX_PUERTA = _tex_puerta()


def _tex_helecho(n=24, semilla=0):
    """Un helecho de la selva, en pixel, para plantar en cruz: frondas que
    salen del centro, se arquean y caen, con sus foliolos a los lados."""
    r = random.Random(semilla)
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    V = [(22, 50, 26), (32, 70, 34), (46, 92, 42), (62, 112, 50), (80, 130, 58)]
    for k in range(6):
        lado = -1 if k % 2 == 0 else 1
        alcance = r.uniform(0.15, 0.48) * n * lado
        alto = r.uniform(0.55, 0.95) * n
        pts = []
        for i in range(12):
            u = i / 11
            pts.append((n / 2 + alcance * u, n - 1 - alto * (1.9 * u - 1.15 * u * u)))
        for i in range(11):
            d.line([pts[i], pts[i + 1]], fill=(*V[min(4, 1 + i // 3)], 255), width=1)
        for i in range(2, 11, 2):
            u = i / 11
            x, y = pts[i]
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
            ln = math.hypot(dx, dy) + 1e-6
            nx_, ny_ = -dy / ln, dx / ln
            largo = 1.0 + 2.5 * (1 - u)
            for sg in (-1, 1):
                d.line([(x, y), (x + nx_ * largo * sg + dx / ln, y + ny_ * largo * sg + dy / ln)],
                       fill=(*V[r.randint(1, 4)], 255), width=1)
    return pila(np.array(im))


TEX_HELECHOS = [_tex_helecho(24, s) for s in range(3)]


def _tex_liana(w=4, h=64, semilla=0):
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    V = [(20, 46, 24), (30, 64, 30), (44, 84, 38)]
    x = 1
    for y in range(h):
        if r.random() < 0.2:
            x = max(0, min(w - 1, x + r.choice([-1, 1])))
        t[y, x] = (*V[r.randint(0, 2)], 255)
        if r.random() < 0.3:
            t[y, max(0, min(w - 1, x + r.choice([-1, 1])))] = (*V[r.randint(0, 2)], 255)
    return pila(t)


TEX_LIANAS = [_tex_liana(4, 64, s) for s in range(3)]


def _mips(tex, niveles=6):
    out = [tex.astype(np.float32) / 255.0]
    im = Image.fromarray(tex)
    for k in range(1, niveles):
        n = max(1, tex.shape[0] >> k)
        out.append(np.array(im.resize((n, n), Image.BOX)).astype(np.float32) / 255.0)
    return out


MIP_SELVA = _mips(np.asarray(ts.SELVA['selva'], np.uint8))
MIP_PLAZA = _mips(np.asarray(ts.SELVA['plaza'], np.uint8), 5)


def sprite(nombre, lado, giro=0):
    clave = (nombre, lado, giro)
    if clave not in _CACHE:
        im = Image.open(os.path.join(PART, nombre)).convert('RGBA')
        im = im.resize((max(1, lado), max(1, lado)), Image.NEAREST)
        if giro:
            im = im.rotate(giro, resample=Image.NEAREST, expand=True)
        _CACHE[clave] = im
    return _CACHE[clave]


# ----------------------------------------------------------------------
#  El mundo: la plaza del templo en el claro y la selva alrededor
# ----------------------------------------------------------------------
PCX, PCZ, R_PLAZA = 0.0, 7.0, 22.0       # la plaza de losas
TZ = 44.0                                # el centro del templo
CLARO = (0.0, 22.0, 30.0, 40.0)          # el claro de la selva (sin arboles): centro x, z y radios
LUZ_CLARO = (4.0, 22.0, 33.0, 43.0)      # donde la luna llega al suelo entera
H_COPAS = 24.0                           # la altura de las copas: los haces de luna no pasan de ahi
C_LUNA = np.array([0.6, 0.76, 0.95], np.float32)
# El camino por el que entra la camara, en diagonal desde delante a la izquierda
CAMINO = (np.array([-31.0, -66.0]), np.array([-9.0, -24.0]))


def _caja(L, x0, y0, z0, x1, y1, z1, tex, grupo, tam=1.0, k=1.0, sin_abajo=True):
    """Las caras de una caja del mundo, con su normal hacia fuera; la textura
    se repite cada 'tam' bloques."""
    def uvs(P, eje):
        if eje == 0:
            return [(p[2] / tam, -p[1] / tam) for p in P]
        if eje == 2:
            return [(p[0] / tam, -p[1] / tam) for p in P]
        return [(p[0] / tam, p[2] / tam) for p in P]
    caras = [
        ([(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], (1, 0, 0), 0),
        ([(x0, y0, z1), (x0, y0, z0), (x0, y1, z0), (x0, y1, z1)], (-1, 0, 0), 0),
        ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1), 2),
        ([(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)], (0, 0, -1), 2),
        ([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], (0, 1, 0), 1),
    ]
    if not sin_abajo:
        caras.append(([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0), 1))
    for P, n, eje in caras:
        L.append((np.array(P, np.float32), np.array(uvs(P, eje), np.float32), tex, grupo, np.array(n, np.float32), k, True))


def _plano(L, P, UV, tex, grupo, k=1.0):
    """Un plano de dos caras (helechos, lianas)."""
    P = np.array(P, np.float32)
    n = np.cross(P[1] - P[0], P[2] - P[0])
    L.append((P, np.array(UV, np.float32), tex, grupo, (n / np.linalg.norm(n)).astype(np.float32), k, False))


def _arbol(L, x, z, alto, semilla, ramas=True):
    """Un arbol de la selva en bloques: tronco grueso, contrafuertes, ramas
    con su mata de hojas, la copa arriba y las lianas que cuelgan."""
    r = random.Random(semilla)
    g = r.choice([1.0, 1.5, 2.0, 2.0])
    tono = r.uniform(0.75, 1.1)
    _caja(L, x - g / 2, 0, z - g / 2, x + g / 2, alto, z + g / 2, TEX_MADERA, G_MADERA, 1.0, tono)
    for k in range(4):                          # contrafuertes
        a = k * TAU / 4 + r.uniform(-0.3, 0.3)
        cx, cz = x + math.cos(a) * (g / 2 + 0.4), z + math.sin(a) * (g / 2 + 0.4)
        h = r.uniform(1.0, 2.6)
        _caja(L, cx - 0.4, 0, cz - 0.4, cx + 0.4, h, cz + 0.4, TEX_MADERA, G_MADERA, 1.0, tono * 0.9)
    for k in range(r.randint(3, 5)):            # la copa: matas apiladas, mas anchas abajo
        cx, cz = x + r.uniform(-3.5, 3.5), z + r.uniform(-3.5, 3.5)
        w_ = r.uniform(5, 9)
        y0 = alto - r.uniform(1.0, 3.5)
        tk = r.uniform(0.7, 1.0)
        _caja(L, cx - w_ / 2, y0, cz - w_ / 2, cx + w_ / 2, y0 + 2.0, cz + w_ / 2, TEX_HOJAS, G_HOJAS, 1.0, tk, sin_abajo=False)
        w2 = w_ * r.uniform(0.5, 0.7)
        _caja(L, cx - w2 / 2, y0 + 2.0, cz - w2 / 2, cx + w2 / 2, y0 + 3.5, cz + w2 / 2, TEX_HOJAS, G_HOJAS, 1.0, tk * 1.08,
              sin_abajo=False)
        for j in range(r.randint(1, 4)):        # lianas que cuelgan de la copa
            lx, lz = cx + r.uniform(-w_ / 2, w_ / 2), cz + r.choice([-1, 1]) * w_ / 2 * r.uniform(0.8, 1.0)
            largo_l = r.uniform(3.0, y0 - 1.5)
            a2 = r.uniform(0, math.pi)
            dx, dz = math.cos(a2) * 0.18, math.sin(a2) * 0.18
            _plano(L, [(lx - dx, y0, lz - dz), (lx + dx, y0, lz + dz), (lx + dx, y0 - largo_l, lz + dz), (lx - dx, y0 - largo_l, lz - dz)],
                   [(0, 0), (1, 0), (1, largo_l / 4), (0, largo_l / 4)], TEX_LIANAS[r.randint(0, 2)], G_HOJAS, 0.9)
    if ramas:
        for k in range(r.randint(1, 3)):        # ramas bajas con su mata
            a = r.uniform(0, TAU)
            y = alto * r.uniform(0.35, 0.7)
            largo = r.uniform(2.5, 5.0)
            ex, ez = x + math.cos(a) * largo, z + math.sin(a) * largo
            _caja(L, min(x, ex) - 0.3, y, min(z, ez) - 0.3, max(x, ex) + 0.3, y + 0.6, max(z, ez) + 0.3, TEX_MADERA, G_MADERA,
                  1.0, tono)
            w_ = r.uniform(2.0, 3.6)
            _caja(L, ex - w_ / 2, y - 0.4, ez - w_ / 2, ex + w_ / 2, y + w_ * 0.6, ez + w_ / 2, TEX_HOJAS, G_HOJAS, 1.0,
                  r.uniform(0.65, 1.0), sin_abajo=False)
            for j in range(r.randint(1, 3)):    # lianas
                lx, lz = ex + r.uniform(-w_ / 2, w_ / 2), ez + r.uniform(-w_ / 2, w_ / 2)
                largo_l = r.uniform(2.0, y - 0.8)
                a2 = r.uniform(0, math.pi)
                dx, dz = math.cos(a2) * 0.18, math.sin(a2) * 0.18
                _plano(L, [(lx - dx, y - 0.4, lz - dz), (lx + dx, y - 0.4, lz + dz), (lx + dx, y - 0.4 - largo_l, lz + dz),
                           (lx - dx, y - 0.4 - largo_l, lz - dz)],
                       [(0, 0), (1, 0), (1, largo_l / 4), (0, largo_l / 4)], TEX_LIANAS[r.randint(0, 2)], G_HOJAS, 0.9)


def _helecho(L, x, z, tam, semilla):
    r = random.Random(semilla)
    a = r.uniform(0, math.pi)
    tex = TEX_HELECHOS[r.randint(0, 2)]
    for k in range(2):
        b = a + k * math.pi / 2
        dx, dz = math.cos(b) * tam / 2, math.sin(b) * tam / 2
        _plano(L, [(x - dx, tam, z - dz), (x + dx, tam, z + dz), (x + dx, 0, z + dz), (x - dx, 0, z - dz)],
               [(0, 0), (1, 0), (1, 1), (0, 1)], tex, G_HOJAS, r.uniform(0.7, 1.0))


def _templo(L):
    """La piramide escalonada: siete gradas, la escalera por delante, las
    placas de oro con la espiral y el santuario arriba."""
    niveles, base, alto = 7, 40.0, 3.0
    for k in range(niveles):
        w_ = base - k * 5.0
        y0 = k * alto
        _caja(L, -w_ / 2, y0, TZ - w_ / 2, w_ / 2, y0 + alto, TZ + w_ / 2, TEX_TEMPLO, G_PIEDRA, 2.0, 0.95)
        # la banda de oro arriba de cada grada, por delante
        zf = TZ - w_ / 2 - 0.06
        _plano(L, [(w_ / 2, y0 + alto, zf), (-w_ / 2, y0 + alto, zf), (-w_ / 2, y0 + alto - 0.5, zf), (w_ / 2, y0 + alto - 0.5, zf)],
               [(0, 0), (w_ / 2, 0), (w_ / 2, 1), (0, 1)], TEX_BANDA, G_ORO, 0.85)
        # las placas con la espiral, a los lados de la escalera
        x = 6.0
        while x + 1.0 < w_ / 2 - 0.5:
            for sg in (-1, 1):
                cx = sg * x
                _plano(L, [(cx + 1, y0 + 2.3, zf), (cx - 1, y0 + 2.3, zf), (cx - 1, y0 + 0.3, zf), (cx + 1, y0 + 0.3, zf)],
                       [(0, 0), (1, 0), (1, 1), (0, 1)], TEX_ORO, G_GLIFO)
            x += 4.0
    # el santuario
    w_ = base - niveles * 5.0 + 1.0
    y0 = niveles * alto
    _caja(L, -w_ / 2, y0, TZ - w_ / 2, w_ / 2, y0 + 4.0, TZ + w_ / 2, TEX_TEMPLO, G_PIEDRA, 2.0, 0.95)
    _caja(L, -w_ / 2 - 0.6, y0 + 4.0, TZ - w_ / 2 - 0.6, w_ / 2 + 0.6, y0 + 4.8, TZ + w_ / 2 + 0.6, TEX_TEMPLO, G_PIEDRA, 2.0, 0.85)
    zf = TZ - w_ / 2 - 0.05
    _plano(L, [(1.3, y0 + 3.0, zf), (-1.3, y0 + 3.0, zf), (-1.3, y0, zf), (1.3, y0, zf)], [(0, 0), (1, 0), (1, 1), (0, 1)],
           TEX_PUERTA, G_GLIFO)
    for sg in (-1, 1):
        _plano(L, [(sg * 2.2 + 1, y0 + 3.6, zf), (sg * 2.2 - 1, y0 + 3.6, zf), (sg * 2.2 - 1, y0 + 1.6, zf), (sg * 2.2 + 1, y0 + 1.6, zf)],
               [(0, 0), (1, 0), (1, 1), (0, 1)], TEX_ORO, G_GLIFO)
    # la escalera: sube de uno en uno hasta el santuario
    z0 = TZ - base / 2 - 1.0
    for k in range(niveles * 3):
        _caja(L, -3.5, 0, z0 + k, 3.5, k + 1.0, z0 + k + 1.0, TEX_TEMPLO, G_PIEDRA, 2.0, 0.8 + 0.1 * (k % 2))
    for sg in (-1, 1):                          # las alfardas, con oro arriba
        for k in range(0, niveles * 3, 3):
            _caja(L, sg * 3.5 - 0.6, 0, z0 + k, sg * 3.5 + 0.6, k + 2.0, z0 + k + 3.0, TEX_TEMPLO, G_PIEDRA, 2.0, 0.7)


def _columnas(L):
    """Columnas viejas alrededor de la plaza: basa, fuste, el aro de oro y el
    capitel; algunas rotas."""
    r = random.Random(14)
    sitios = [(15.5, -3.5, 7.0, True), (17.5, 3.0, 5.0, True),
              (18.5, 16.0, 9.0, False), (-12.0, 25.0, 7.5, False), (12.5, 25.5, 6.0, True)]
    for x, z, alto, rota in sitios:
        _caja(L, x - 1.4, 0, z - 1.4, x + 1.4, 1.0, z + 1.4, TEX_TEMPLO, G_PIEDRA, 2.0, 0.8)
        _caja(L, x - 0.9, 1.0, z - 0.9, x + 0.9, alto, z + 0.9, TEX_TEMPLO, G_PIEDRA, 2.0, 0.92)
        yb = alto * 0.62
        _caja(L, x - 1.05, yb, z - 1.05, x + 1.05, yb + 0.6, z + 1.05, TEX_BANDA, G_ORO, 2.0, 0.9)
        if rota:
            _caja(L, x - 0.9, alto, z - 0.9, x + r.uniform(-0.2, 0.6), alto + r.uniform(0.6, 1.4), z + r.uniform(-0.3, 0.5),
                  TEX_TEMPLO, G_PIEDRA, 2.0, 0.85)
            bx, bz = x + r.uniform(1.6, 2.8) * r.choice([-1, 1]), z + r.uniform(-2.5, 2.5)
            _caja(L, bx - 0.9, 0, bz - 0.9, bx + 0.9, 1.6, bz + 0.9, TEX_TEMPLO, G_PIEDRA, 2.0, 0.8)
        else:
            _caja(L, x - 1.3, alto, z - 1.3, x + 1.3, alto + 0.9, z + 1.3, TEX_TEMPLO, G_PIEDRA, 2.0, 0.85)


def _selva(L):
    """Los arboles: cierran el claro y bordean el camino por el que entra la camara."""
    r = random.Random(23)
    puestos = []

    def libre(x, z, sep):
        return all(math.hypot(x - a, z - b) > sep for a, b in puestos)

    a, b = CAMINO
    eje = (b - a) / np.linalg.norm(b - a)
    perp = np.array([-eje[1], eje[0]])

    def al_camino(x, z):
        """Distancia al camino de la camara (y cuanto se ha avanzado por el)."""
        q = np.array([x, z]) - a
        s = q @ eje
        if s < -6 or s > np.linalg.norm(b - a) + 4:
            return 99.0
        return abs(q @ perp)

    def abierto(x, z):
        """Distancia a la linea por la que miran los planos abiertos (la camara del rugido y del cielo)."""
        p0, p1 = np.array([-24.0, -23.0]), np.array([0.0, 0.0])
        e = (p1 - p0) / np.linalg.norm(p1 - p0)
        q = np.array([x, z]) - p0
        s_ = min(max(q @ e, 0.0), np.linalg.norm(p1 - p0))
        return float(np.linalg.norm(q - e * s_))

    # los que pasan rozando la camara, a los dos lados del camino
    largo = np.linalg.norm(b - a)
    for k, (s, lado, alto) in enumerate(((2.0, 4.2, 22.0), (8.0, -5.0, 24.0), (15.0, 4.6, 20.0), (22.0, -4.4, 21.0),
                                         (29.0, 5.2, 23.0), (36.0, -5.6, 22.0), (41.0, -6.5, 24.0))):
        p = a + eje * min(s, largo) + perp * lado
        puestos.append((p[0], p[1]))
        _arbol(L, p[0], p[1], alto, 1000 + k)
    intentos = 0
    while len(puestos) < 140 and intentos < 9000:
        intentos += 1
        x, z = r.uniform(-75, 70), r.uniform(-80, 95)
        dc = math.hypot((x - CLARO[0]) / CLARO[2], (z - CLARO[1]) / CLARO[3])
        if dc < 1.0 or al_camino(x, z) < 4.0:
            continue
        cerca = dc < 1.6
        if not libre(x, z, 4.5 if cerca else 6.0) or abierto(x, z) < 7.0:
            continue
        puestos.append((x, z))
        _arbol(L, x, z, r.uniform(17, 28), 100 + len(puestos), ramas=dc < 1.8)
    for k in range(320):                         # helechos y matas por el suelo
        x, z = r.uniform(-45, 30), r.uniform(-70, 30)
        if math.hypot(x - PCX, z - PCZ) < R_PLAZA - 1 or al_camino(x, z) < 1.0 or abierto(x, z) < 2.5 \
                or math.hypot(x + 18.5, z + 18.0) < 11.0:
            continue
        if r.random() < 0.8:
            _helecho(L, x, z, r.uniform(0.9, 1.9), 500 + k)
        else:
            w_ = r.uniform(1.0, 2.2)
            _caja(L, x - w_ / 2, 0, z - w_ / 2, x + w_ / 2, w_ * r.uniform(0.6, 1.0), z + w_ / 2, TEX_HOJAS, G_HOJAS, 1.0,
                  r.uniform(0.55, 0.85))
    return puestos


def _mundo():
    L = []
    _templo(L)
    _columnas(L)
    _selva(L)
    # todo en arrays para cribar de golpe lo que no se ve
    P = np.stack([c[0] for c in L])                           # (N, 4, 3)
    nrm = np.stack([c[4] for c in L])
    cerrada = np.array([c[6] for c in L])
    return L, P, nrm, cerrada


MUNDO, MUNDO_P, MUNDO_N, MUNDO_CERRADA = _mundo()


def dibujar_mundo(lz, cam, lejos=140.0):
    """Las caras del mundo que caen en la camara, de cerca a lejos."""
    d = MUNDO_P - cam.ojo
    zc = d @ cam.f
    xc = d @ cam.r
    yc = d @ cam.u
    zmax = zc.max(1)
    zz = np.maximum(zc, ZN)
    sx = xc * cam.foco / zz
    sy = yc * cam.foco / zz
    fuera = (zmax < ZN) | (zc.min(1) > lejos) | ((sx.max(1) < -W / 2) & (zc.min(1) > ZN)) | \
            ((sx.min(1) > W / 2) & (zc.min(1) > ZN)) | ((sy.max(1) < -H / 2) & (zc.min(1) > ZN)) | \
            ((sy.min(1) > H / 2) & (zc.min(1) > ZN))
    centro = MUNDO_P.mean(1)
    de_cara = ((cam.ojo - centro) * MUNDO_N).sum(1) > 0
    sirve = ~fuera & (de_cara | ~MUNDO_CERRADA)
    orden = np.argsort(zc.min(1))
    for i in orden:
        if not sirve[i]:
            continue
        P, UV, tex, grupo, n, k, cerrada = MUNDO[i]
        if not cerrada and n @ (cam.ojo - centro[i]) < 0:
            n = -n
        lz.cara(P, UV, tex, grupo, n, envolver=True, k_alb=k)


def suelo(lz, cam):
    """El suelo de la selva y las losas de la plaza, lanzando un rayo por pixel."""
    Dx, Dy, Dz = cam.rayos()
    O = cam.ojo
    m = Dy < -1e-5
    t = np.where(m, -O[1] / np.where(m, Dy, -1.0), np.inf).astype(np.float32)
    m &= t < 400
    iy, ix = np.nonzero(m)
    t = t[iy, ix]
    X, Z = O[0] + t * Dx[iy, ix], O[2] + t * Dz[iy, ix]
    lon = np.sqrt(Dx[iy, ix] ** 2 + Dy[iy, ix] ** 2 + Dz[iy, ix] ** 2)
    # cuantos texeles (32 por bloque) caben en un pixel
    pie = 32.0 * t * lon / cam.foco / np.maximum(np.abs(Dy[iy, ix]) / lon, 0.06) * 0.55
    nivel = np.clip(np.log2(np.maximum(pie, 1.0)), 0, 4.99)
    rp = np.hypot(X - PCX, Z - PCZ)
    borde = R_PLAZA + 3.0 * (_ruido1(np.arctan2(Z - PCZ, X - PCX) * 4 + 30) - 0.5)
    es_plaza = rp < borde
    col = np.zeros((len(t), 3), np.float32)
    for mips, tam, sel in ((MIP_SELVA, 8.0, ~es_plaza), (MIP_PLAZA, 4.0, es_plaza)):
        if not sel.any():
            continue
        u, v, nv = X[sel] / tam, Z[sel] / tam, nivel[sel]
        n0 = np.floor(nv).astype(np.int64)
        fr = (nv - n0)[:, None]
        acc = np.zeros((sel.sum(), 3), np.float32)
        for lv in range(len(mips)):
            for dl, peso in ((0, 1 - fr), (1, fr)):
                q = (n0 + dl) == lv
                if not q.any():
                    continue
                tx = mips[lv]
                n = tx.shape[0]
                tu = np.floor(u[q.ravel()] * n).astype(np.int64) % n
                tv = np.floor(v[q.ravel()] * n).astype(np.int64) % n
                acc[q.ravel()] += tx[tv, tu, :3] * peso[q.ravel()]
        col[sel] = acc
    # el musgo se come el borde de la plaza
    orilla = np.clip((rp - borde + 2.5) / 2.5, 0, 1) * es_plaza
    col *= (1 - 0.35 * orilla)[:, None]
    lz.z[iy, ix] = t
    lz.alb[iy, ix] = col
    lz.alb2[iy, ix] = col
    lz.nrm[iy, ix] = (0, 1, 0)
    lz.grupo[iy, ix] = G_SUELO


# ----------------------------------------------------------------------
#  Rajang: la malla del juego, con la normal de cada cara hacia fuera
# ----------------------------------------------------------------------
RAJ_M = vr.entidad_a_mundo(0, 0, 0, 0)


def quads_rajang(pose, M=RAJ_M):
    Ms = rj.matrices(pose)
    out = []
    for nombre in rj.ORDEN:
        q, oculto = nombre, False
        while q:
            if pose.get(q, {}).get('oculto'):
                oculto = True
            q = rj.PARTES[q].padre
        if oculto:
            continue
        Mw = M @ Ms[nombre]
        for i, c in enumerate(rj.PARTES[nombre].cajas):
            u, v = UV_RJ[(nombre, i)]
            x0, y0, z0, w_, h_, d_ = c[:6]
            cen = (Mw @ np.array([x0 + w_ / 2, y0 + h_ / 2, z0 + d_ / 2, 1.0]))[:3]
            plano = min(w_, h_, d_) < 1e-6
            for pts, uvs in vr.caja_quads((u, v), c[:6], False, rj.ANCHO_ATLAS, ALTO_RJ):
                P = (np.c_[np.array(pts, float), np.ones(4)] @ Mw.T)[:, :3]
                out.append((P, np.array(uvs), nombre, c[6], cen, plano))
    return out


def dibujar_rajang(lz, cam, pose, sombra=None):
    for P, UV, nombre, mat, cen, plano in quads_rajang(pose):
        n = np.cross(P[1] - P[0], P[2] - P[0])
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        n = n / ln
        c = P.mean(0)
        if not plano and n @ (c - cen) < 0:
            n = -n
        hacia = n @ (cam.ojo - c)
        if plano:
            if mat == 'sol_img' and n @ np.array([0, 0, -1.0]) < 0:
                continue                      # el sol del pecho: solo la cara de delante
            if hacia < 0:
                n = -n
        elif hacia < 0:
            if sombra is not None and n @ sombra.f < 0:
                sombra.cara(P)
            continue
        if sombra is not None and (plano or n @ sombra.f < 0):
            sombra.cara(P)
        lz.cara(P, UV, TEX_RJ, GRUPO_MAT.get(mat, G_CUERPO), n.astype(np.float32))


def mezclar_poses(a, b, k):
    out = {}
    for pz in set(a) | set(b):
        da, db = a.get(pz, {}), b.get(pz, {})
        d = {}
        for tipo, nulo in (('rot', (0, 0, 0)), ('pos', (0, 0, 0)), ('esc', (1, 1, 1))):
            va, vb = np.array(da.get(tipo, nulo), float), np.array(db.get(tipo, nulo), float)
            d[tipo] = tuple(va + (vb - va) * k)
        out[pz] = d
    return out


def ojos_abiertos(t):
    """Los ojos: una rendija hasta que los abre de golpe (y se pasan un poco)."""
    ab = t - T_OJOS
    if ab < 0:
        return 0.1
    if ab < 0.06:
        return 0.1 + 1.25 * ab / 0.06
    return 1.35 - 0.35 * suave((ab - 0.06) / 0.15)


def crecer(t):
    """Los cristales crecen al rugir (como en la fase IV)."""
    return 1.0 + 0.55 * suave((t - T_RUGE - 0.05) / 0.5)


def pose_rajang(t):
    if t < 9.0:
        p = ra.pose_en('DORMIDO', t * 0.9)
        if t > T_OJOS:                          # alza la cabeza y levanta las orejas
            k = suave((t - T_OJOS) / 0.65)
            p = mezclar_poses(p, ra.pose_en('DESPERTAR', 0.6), k)
    elif t < 10.7:
        if t < T_RUGE:                          # se levanta (deprisa)
            k = (t - 9.0) / (T_RUGE - 9.0)
            s = 1.0 + 1.3 * (k * k * (3 - 2 * k) * 0.6 + 0.4 * k)
        else:
            s = min(2.3 + (t - T_RUGE), 3.05)
        p = ra.pose_en('DESPERTAR', s)
    else:
        u = t - 10.7
        s = 0.55 + u * 2.0 if u < 0.375 else 1.3 + (u - 0.375) * 1.2
        p = ra.pose_en('CATACLISMO', min(s, 2.25))
    a = ojos_abiertos(t)
    for o in ('ojo_izq', 'ojo_der'):
        d = p.setdefault(o, {})
        e = d.get('esc', (1, 1, 1))
        d['esc'] = (e[0], e[1] * a, e[2])
    k = crecer(t)
    if k > 1.001:
        for c in rj.CRISTALES:
            d = p.setdefault(c, {})
            e = d.get('esc', (1, 1, 1))
            d['esc'] = (e[0] * math.sqrt(k), e[1] * k, e[2] * math.sqrt(k))
    return p


def punto_rj(pose, pieza, local=(0, 0, 0)):
    return (RAJ_M @ np.array([*rj.punto(pose, pieza, local), 1.0]))[:3]


# ----------------------------------------------------------------------
#  Las piezas de los ataques, como RajangDibujo (pinchos de roca en bloques)
#  y FragmentoJadeRenderer (el terron de jade con su llama)
# ----------------------------------------------------------------------
def _xrot(q, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([q[0], q[1] * c + q[2] * s, q[2] * c - q[1] * s])


def _yrot(q, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([q[0] * c + q[2] * s, q[1], q[2] * c - q[0] * s])


def _zrot(q, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([q[0] * c + q[1] * s, q[1] * c - q[0] * s, q[2]])


CARAS_CAJA = ((0, 4, 6, 2), (5, 1, 3, 7), (1, 0, 2, 3), (4, 5, 7, 6), (2, 6, 7, 3), (0, 1, 5, 4))


def bloque(out, r, x, y, z, hx, hy, hz, mover, gx, gy, gz, densidad, tw, th):
    """Un bloque de medio lado (hx, hy, hz) con las esquinas algo movidas y
    girado (grados x, y, z); cada cara lleva el centro del bloque."""
    v = []
    for i in range(8):
        sx, sy, sz = (1 if i & 1 else -1), (1 if i & 2 else -1), (1 if i & 4 else -1)
        q = np.array([sx * hx * (1 + (r.random() - 0.5) * mover), sy * hy * (1 + (r.random() - 0.5) * mover),
                      sz * hz * (1 + (r.random() - 0.5) * mover)])
        q = _yrot(_xrot(_zrot(q, math.radians(gz)), math.radians(gx)), math.radians(gy))
        v.append(q + np.array([x, y, z]))
    cen = np.mean(v, axis=0)
    lados = ((hz, hy), (hz, hy), (hx, hy), (hx, hy), (hz, hx), (hx, hz))
    for k, c in enumerate(CARAS_CAJA):
        du = min(1.0, 2 * lados[k][0] * densidad / tw)
        dv = min(1.0, 2 * lados[k][1] * densidad / th)
        u0, v0 = r.random() * (1 - du), r.random() * (1 - dv)
        out.append((np.array([v[c[0]], v[c[1]], v[c[2]], v[c[3]]]), np.array([(u0, v0 + dv), (u0 + du, v0 + dv), (u0 + du, v0), (u0, v0)]),
                    cen))


def pincho(out, r, x, z, alto, ancho, inclina, ladea):
    """Un pincho de roca en bloques: tramos apilados que se estrechan hasta un
    taco en la punta, inclinado hacia delante (+Z) y hacia el lado (+X)."""
    e = _xrot(_zrot(np.array([0.0, 1.0, 0.0]), math.radians(ladea)), math.radians(-inclina))
    n = max(3, min(7, int(round(alto / max(0.45, ancho * 0.75)))))
    paso = alto / e[1] / n
    base = np.array([x, 0.0, z])
    s = -0.35
    for i in range(n):
        m = max(0.09, ancho * 0.5 * (1 - i / n) ** 0.8)
        h = paso * (0.95 + r.random() * 0.15)
        c = base + e * (s + h / 2)
        bloque(out, r, *c, m * (0.9 + r.random() * 0.15), h / 2 * 1.04, m * (0.85 + r.random() * 0.2), 0.1, -inclina,
               (r.random() - 0.5) * 18, ladea, 12, 32, 64)
        s += h * 0.9
    m = max(0.07, ancho * 0.08)
    c = base + e * (s + paso * 0.25)
    bloque(out, r, *c, m, paso * 0.3, m, 0.1, -inclina, (r.random() - 0.5) * 18, ladea, 12, 32, 64)


def pico_tierra(tam, semilla):
    """Un golpe de pinchos de la Garra (como PicoTierraRenderer), en local:
    el grande, los menores abiertos alrededor y los terrones."""
    r = random.Random(semilla)
    caras = []
    alto = 6.0 * tam
    ancho = 0.5 + 1.25 * tam
    pincho(caras, r, 0, 0, alto, ancho, 12 + r.random() * 10, (r.random() - 0.5) * 12)
    n = 2 + r.randrange(3)
    for i in range(n):
        a = (i + r.random() * 0.5) / n * TAU
        d = ancho * (0.55 + r.random() * 0.3)
        abre = 22 + r.random() * 18
        pincho(caras, r, math.cos(a) * d, math.sin(a) * d, alto * (0.3 + r.random() * 0.3), ancho * (0.45 + r.random() * 0.2),
               math.sin(a) * abre, math.cos(a) * abre)
    for i in range(6):
        a = r.random() * TAU
        d = ancho * (0.9 + r.random() * 0.7)
        t = ancho * (0.12 + r.random() * 0.1)
        bloque(caras, r, math.cos(a) * d, t * 0.4, math.sin(a) * d, t, t * 0.7, t, 0.2, (r.random() - 0.5) * 50,
               r.random() * 90, (r.random() - 0.5) * 50, 12, 32, 64)
    return caras, alto


def racimo(semilla):
    """El terron de jade del Cataclismo: dos bloques cruzados, sus puntas y la llama."""
    r = random.Random(semilla)
    jade, aura = [], []
    n = 0.75 + r.random() * 0.1
    bloque(jade, r, 0, 0, 0, n, n * (0.85 + r.random() * 0.2), n, 0.18, r.random() * 30, r.random() * 90, r.random() * 30, 16, 32, 32)
    bloque(jade, r, n * 0.3, n * 0.2, -n * 0.2, n * 0.8, n * 0.7, n * 0.8, 0.18, 30 + r.random() * 30, 45 + r.random() * 30,
           r.random() * 30, 16, 32, 32)
    for k in range(3 + r.randrange(2)):
        theta = math.acos(1 - 2 * (k + r.random() * 0.6) / 4)
        phi = r.random() * TAU
        largo = 0.5 + r.random() * 0.45
        grueso = 0.22 + r.random() * 0.1
        d = np.array([math.sin(theta) * math.sin(phi), math.cos(theta), math.sin(theta) * math.cos(phi)])
        bloque(jade, r, *(d * (n * 0.7 + largo / 2)), grueso, largo / 2, grueso, 0.1, -math.degrees(theta), math.degrees(phi), 0,
               16, 32, 32)
    a = n * 1.3
    bloque(aura, r, 0, 0, 0, a, a, a, 0.25, r.random() * 45, r.random() * 45, 0, 8, 16, 32)
    return jade, aura


def pintar_piezas(lz, cam, caras, M, tex, grupo, aditivo=0.0, sombra=None, k_alb=1.0):
    for P, UV, cen in caras:
        Pw = (np.c_[P, np.ones(4)] @ M.T)[:, :3]
        cw = (M @ np.array([*cen, 1.0]))[:3]
        n = np.cross(Pw[1] - Pw[0], Pw[2] - Pw[0])
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        n /= ln
        c = Pw.mean(0)
        if n @ (c - cw) < 0:
            n = -n
        if sombra is not None and n @ sombra.f < 0:
            sombra.cara(Pw)
        if aditivo:
            lz.cara(Pw, UV, tex, grupo, n.astype(np.float32), aditivo=aditivo)
        elif n @ (cam.ojo - c) > 0:
            lz.cara(Pw, UV, tex, grupo, n.astype(np.float32), k_alb=k_alb)


# Los pinchos que revientan al rugir: (x, z, tam, rumbo, semilla, instante)
A_CAMARA = math.atan2(-19.0, -17.0)        # hacia donde queda la camara de los planos abiertos


def _pinchos():
    r = random.Random(31)
    out = []
    # un anillo alrededor de el, que sale en ola desde sus zarpas
    for k in range(13):
        a = k / 13 * TAU + r.uniform(-0.12, 0.12)
        if abs(math.atan2(math.sin(a - A_CAMARA), math.cos(a - A_CAMARA))) < 0.75:
            continue                              # deja libre lo que ve la camara
        rad = r.uniform(9.0, 13.5)
        x, z = rad * math.cos(a), -1.5 + rad * math.sin(a)
        out.append((x, z, r.uniform(0.55, 0.95), r.uniform(0, 360), 200 + k, T_RUGE + 0.08 + 0.02 * rad + r.uniform(0, 0.05)))
    # una fila que corre por la plaza hacia la izquierda de la camara (la Garra)
    for k in range(5):
        x, z = 4.0 + k * 2.5, -9.0 - k * 0.9
        out.append((x, z, 0.4 + 0.12 * k, -40 + r.uniform(-20, 20), 300 + k, T_RUGE + 0.1 + 0.07 * k))
    return out


PINCHOS = _pinchos()
_PIEZAS = {}


def pinchos_de(semilla, tam):
    if semilla not in _PIEZAS:
        _PIEZAS[semilla] = pico_tierra(tam, semilla)
    return _PIEZAS[semilla]


def brote(t, t0):
    """Cuanto ha salido un pincho: revienta deprisa, se pasa un poco y asienta."""
    u = (t - t0) / 0.16
    if u <= 0:
        return 0.0
    if u < 1:
        return 1 - (1 - u) ** 3
    return 1.0 + 0.06 * math.exp(-(u - 1) * 3) * math.sin((u - 1) * 6)


def dibujar_pinchos(lz, cam, t, sombra=None):
    for x, z, tam, rumbo, sem, t0 in PINCHOS:
        g = brote(t, t0)
        if g <= 0:
            continue
        caras, alto = pinchos_de(sem, tam)
        M = vr.T(x, (g - 1.0) * alto * 1.05, z) @ vr.Ry(math.radians(-rumbo))
        pintar_piezas(lz, cam, caras, M, TEX_ROCA, G_ROCA, sombra=sombra, k_alb=0.62)


# ----------------------------------------------------------------------
#  La luz: G-buffer -> color, por pixel
# ----------------------------------------------------------------------
def copas(X, Z):
    """Cuanta luna pasa entre las copas, medido en el suelo (X, Z: el punto
    del suelo en la misma columna de luz): el claro entero y, en la selva,
    algun hueco."""
    dc = np.hypot((X - LUZ_CLARO[0]) / LUZ_CLARO[2], (Z - LUZ_CLARO[1]) / LUZ_CLARO[3])
    ang = np.arctan2(Z - LUZ_CLARO[1], X - LUZ_CLARO[0])
    claro = _paso(1.06, 0.84, dc + 0.12 * (_ruido1(ang * 5 + 3) - 0.5))
    huecos = np.clip((_fbm(X / 7.0 + 3, Z / 7.0 + 7, 2) - 0.6) * 5.0, 0, 1)
    return np.maximum(claro, huecos * 0.8)


def copas_en(P, L):
    k = P[:, 1] / L[1]
    return copas(P[:, 0] - k * L[0], P[:, 2] - k * L[2])


PALETA_MUSGO = np.array([_hex(c) for c in ('233a18', '2e4a1e', '3c5c26', '4c6e2e', '5e3e1a', '7a5422', '3a2a14')],
                        np.float32)


def efectos_rajang(P, n, alb, alb2, em, em2, g, E):
    """La estatua, la costra que se cae, las grietas que corren desde el pecho
    y la maldicion (fase I -> IV). Devuelve (color, brillo, mascara de piedra)."""
    d = np.linalg.norm(P - E['pecho'], axis=1)
    q = np.floor(P * 8.0)
    hq = _hash3(q[:, 0], q[:, 1], q[:, 2], 3)
    vn = _ruido3(P, 0.9, 5)
    de = d + 1.3 * (vn - 0.5) + 0.35 * (hq - 0.5)
    m = np.clip((E['R_m'] - de) / 0.9, 0, 1)
    gk = np.clip((E['R_g'] - de) / 0.5, 0, 1)
    c = np.clip((de - E['R_c']) / 0.35, 0, 1)
    alb_v = alb * (1 - m[:, None]) + alb2 * m[:, None]
    em_v = em * (1 - m[:, None]) + em2 * m[:, None]
    # la piedra de la estatua: el jade apagado y gris, con musgo y hojas encima
    lum = alb_v @ np.array([0.3, 0.59, 0.11], np.float32)
    piedra = (0.07 + 0.8 * lum)[:, None] * np.array([0.84, 0.94, 0.82], np.float32)
    arriba = np.clip((n[:, 1] - 0.3) / 0.45, 0, 1)
    q2 = np.floor(P * 6.0)
    h2 = _hash3(q2[:, 0], q2[:, 1], q2[:, 2], 9)
    vm = _ruido3(P, 0.7, 11)
    musgo = arriba * np.clip((vm - 0.3) * 4.0, 0, 1) + (1 - arriba) * np.clip((vm - 0.62) * 3.0, 0, 0.7)
    tono = PALETA_MUSGO[np.minimum((h2 * len(PALETA_MUSGO)).astype(np.int64), len(PALETA_MUSGO) - 1)]
    piedra = piedra * (1 - musgo[:, None]) + tono * musgo[:, None]
    piedra *= (0.82 + 0.3 * hq)[:, None]
    col = alb_v * (1 - c[:, None]) + piedra * c[:, None]
    # los ojos cerrados no brillan
    col[g == G_OJO] *= E['k_ojo_col']
    K = np.ones(len(P), np.float32)
    K[g == G_SOL] = E['k_sol']
    K[g == G_OJO] = E['k_ojo']
    K[g == G_CRISTAL] = E['k_cristal']
    K[g == G_BOCA] = E['k_boca']
    K[(g == G_CUERPO) | (g == G_ORO)] = E['k_cuerpo']
    brillo = em_v * K[:, None] * np.where(g == G_SOL, 1.0, 1 - c)[:, None]
    # las grietas que corren desde el pecho, verdes, con el pulso de cada latido
    cuerpo = ((g == G_CUERPO) | (g == G_ORO))
    if E['k_grieta'] > 0:
        pulso = np.zeros(len(P), np.float32)
        for tb, k_ in E['ondas']:
            rb = 9.0 * (E['t'] - tb)
            pulso += k_ * np.exp(-((de - rb) / 0.7) ** 2) * math.exp(-(E['t'] - tb) / 0.45)
        gr = em2 * (gk * (1 - m) * cuerpo)[:, None] * E['k_grieta'] * (1 + 1.6 * pulso)[:, None]
        brillo += gr * np.array([0.55, 1.0, 0.45], np.float32)
        # el frente de la costra: una raya de luz donde la piedra se abre
        frente = np.exp(-((de - E['R_c']) / 0.08) ** 2) * (E['R_c'] > 0.05) * cuerpo
        brillo += (frente * E['k_frente'])[:, None] * np.array([0.35, 1.0, 0.45], np.float32)
    return col, brillo, c


def sombrear(lz, cam, E):
    """La luz de la escena sobre el G-buffer: luna (con las copas y la sombra
    de Rajang), cielo, contraluz, luces de punto, brillo y bruma."""
    Dx, Dy, Dz = cam.rayos()
    hay = np.isfinite(lz.z)
    iy, ix = np.nonzero(hay)
    z = lz.z[iy, ix]
    dx_, dy_, dz_ = Dx[iy, ix], Dy[iy, ix], Dz[iy, ix]
    O = cam.ojo.astype(np.float32)
    P = np.stack([O[0] + z * dx_, O[1] + z * dy_, O[2] + z * dz_], 1).astype(np.float32)
    n = lz.nrm[iy, ix]
    g = lz.grupo[iy, ix]
    alb = lz.alb[iy, ix]
    em = lz.em[iy, ix] * E['k_grupo'][g][:, None]
    vista = O[None, :] - P
    dist = np.linalg.norm(vista, axis=1) + 1e-6
    vista /= dist[:, None]
    piedra = np.zeros(len(P), np.float32)
    es_rj = (g >= 1) & (g <= 6)
    if es_rj.any():
        k = np.nonzero(es_rj)[0]
        c_, b_, piedra_ = efectos_rajang(P[k], n[k], alb[k], lz.alb2[iy[k], ix[k]], lz.em[iy[k], ix[k]],
                                         lz.em2[iy[k], ix[k]], g[k], E)
        alb[k] = c_
        em[k] = b_
        piedra[k] = piedra_
    # cielo y suelo (luz que rebota)
    ny = n[:, 1:2]
    luz = E['amb_cielo'] * (0.5 + 0.5 * ny) + E['amb_suelo'] * (0.5 - 0.5 * ny)
    for L, color, k_, tipo in E['luces']:
        L = np.asarray(L, np.float32)
        L = L / np.linalg.norm(L)
        ndl = np.clip(n @ L, 0, None)
        if tipo == 'luna':
            vis = copas_en(P, L) if E.get('copas', True) else np.ones(len(P), np.float32)
            if E.get('sombra') is not None:
                vis = vis * E['sombra'].luz(P)
            luz = luz + (color * k_)[None, :] * (ndl * vis)[:, None]
        elif tipo == 'llave':
            luz = luz + (color * k_)[None, :] * ndl[:, None]
        else:          # contraluz: el borde que se aleja de la camara (en el suelo no)
            borde = (1 - np.abs((n * vista).sum(1))) ** 1.5
            luz = luz + (color * k_)[None, :] * (ndl * (0.3 + borde) * (g != G_SUELO))[:, None]
    for p, color, k_, radio in E['puntos']:
        if k_ <= 0:
            continue
        Lp = np.asarray(p, np.float32)[None, :] - P
        dd = np.linalg.norm(Lp, axis=1) + 1e-4
        ndl = np.clip(((n * Lp).sum(1) / dd + 0.25) / 1.25, 0, 1)
        luz = luz + (np.asarray(color, np.float32) * k_)[None, :] * (ndl / (1 + (dd / radio) ** 2))[:, None]
    rgb = alb * luz
    # el jade pulido brilla un poco a la luna
    if es_rj.any() and E['luces']:
        L = np.asarray(E['luces'][0][0], np.float32)
        L = L / np.linalg.norm(L)
        h_ = L[None, :] + vista
        h_ /= np.linalg.norm(h_, axis=1)[:, None]
        spec = np.clip((n * h_).sum(1), 0, 1) ** 24 * 0.35 * (1 - piedra) * es_rj
        rgb += spec[:, None] * E['luces'][0][1][None, :]
    rgb = rgb + em
    # la bruma: por distancia y, mas espesa, pegada al suelo
    hb = E['niebla_alto']
    y0, y1 = O[1], P[:, 1]
    dy = y1 - y0
    capa = np.where(np.abs(dy) > 1e-3, hb * (np.exp(-y0 / hb) - np.exp(-y1 / hb)) / np.where(np.abs(dy) > 1e-3, dy, 1.0),
                    math.exp(-y0 / hb))
    espesor = dist * (E['niebla'] + E['niebla_suelo'] * capa)
    f = (1 - np.exp(-espesor))[:, None]
    rgb = rgb * (1 - f) + E['c_niebla'][None, :] * f
    em = em * (1 - f)
    col = np.zeros((HV, W, 3), np.float32)
    brillo = np.zeros((HV, W, 3), np.float32)
    col[iy, ix] = rgb
    brillo[iy, ix] = em
    # el cielo donde no hay nada
    cielo = E['cielo'](cam, Dx, Dy, Dz)
    col[~hay] = cielo[~hay]
    col += lz.suma
    brillo += lz.suma
    return col, brillo


def cielo_noche(cam, Dx, Dy, Dz):
    """Cielo de noche sobre la selva: azul verdoso, mas claro y brumoso abajo."""
    lon = np.sqrt(Dx * Dx + Dy * Dy + Dz * Dz)
    elev = Dy / lon
    k = np.clip(elev / 0.5, 0, 1)[..., None] ** 0.7
    abajo = np.array([0.06, 0.11, 0.10], np.float32)
    arriba = np.array([0.012, 0.026, 0.034], np.float32)
    col = abajo + (arriba - abajo) * k
    # estrellas muy flojas
    az = np.arctan2(Dx, Dz)
    q1, q2 = np.floor(az * 260), np.floor(elev * 260)
    h_ = _hash3(q1, q2, q1 * 0 + 1, 7)
    col += (np.clip((h_ - 0.9965) * 300, 0, 1) * np.clip(elev * 4, 0, 1))[..., None] * 0.3
    return col


# ----------------------------------------------------------------------
#  El aire: haces de luna entre las copas, luciernagas y hojas
# ----------------------------------------------------------------------
def haces(lz, cam, L, k=1.0, pasos=16, lejos=70.0):
    """Luz de luna que se cuela entre las copas: se marcha por cada rayo (a un
    sexto de resolucion) y se suma la que cruza la bruma."""
    paso = 6
    Dx, Dy, Dz = (a[paso // 2::paso, paso // 2::paso] for a in cam.rayos())
    pr = lz.z[paso // 2::paso, paso // 2::paso]
    O = cam.ojo
    tfin = np.minimum(pr, lejos)
    L = np.asarray(L, float) / np.linalg.norm(L)
    acum = np.zeros(Dx.shape, np.float32)
    for i in range(pasos):
        t = tfin * (i + 0.5) / pasos
        Py = O[1] + t * Dy
        Px, Pz = O[0] + t * Dx, O[2] + t * Dz
        kk = Py / L[1]
        v = copas(Px - kk * L[0], Pz - kk * L[2])
        dens = 0.35 + np.exp(-np.maximum(Py, 0) / 3.0)
        acum += v * dens * np.exp(-t / 45.0) * (Py < H_COPAS) * (tfin / pasos)
    acum *= 0.012 * k * paso / 4
    im = Image.fromarray(np.clip(acum * 255, 0, 255).astype(np.uint8)).resize((W, HV), Image.BILINEAR)
    return np.array(im.filter(ImageFilter.GaussianBlur(2.5 * ESCALA))).astype(np.float32)[..., None] / 255.0


_LUCI = np.random.default_rng(17).random((420, 5)).astype(np.float32)


def luciernagas(capa, cam, lz, t, k=1.0, zona=((-42, 26), (0.4, 6.5), (-66, 26)), huida=0.0):
    """Luciernagas verdes que flotan y parpadean (puntos de luz con su halo)."""
    p = _LUCI
    X = zona[0][0] + (zona[0][1] - zona[0][0]) * p[:, 0] + 0.8 * np.sin(t * 0.7 + p[:, 3] * 30)
    Y = zona[1][0] + (zona[1][1] - zona[1][0]) * p[:, 1] + 0.4 * np.sin(t * 1.1 + p[:, 4] * 20)
    Z = zona[2][0] + (zona[2][1] - zona[2][0]) * p[:, 2] + 0.8 * np.cos(t * 0.6 + p[:, 3] * 17)
    if huida > 0:              # el rugido las espanta lejos
        dx, dz = X, Z + 2
        dd = np.hypot(dx, dz) + 1
        X = X + dx / dd * huida * 18
        Z = Z + dz / dd * huida * 18
        Y = Y + huida * 6 * p[:, 4]
    sx, sy, sz = cam.proyectar(np.stack([X, Y, Z], 1))
    d = ImageDraw.Draw(capa)
    for i in range(len(p)):
        if sz[i] < 0.5 or sz[i] > 70 or not (0 <= sx[i] < W and HV0 <= sy[i] < HV1):
            continue
        if abs(X[i]) < 7.5 and -13 < Z[i] < 13 and huida == 0:
            continue                   # ninguna delante de la estatua
        if sz[i] > lz.z[int(sy[i]) - HV0, int(sx[i])] + 0.2:
            continue
        parpadeo = max(0.0, math.sin(t * (1.5 + 2 * p[i, 3]) + p[i, 4] * 40)) ** 2
        b = k * parpadeo * math.exp(-sz[i] / 45.0)
        if b < 0.03:
            continue
        rr = min(4.5 * ESCALA, max(0.8 * ESCALA, 0.06 * cam.foco / sz[i]))
        c = (int(150 * b), int(255 * min(1.0, b * 1.2)), int(110 * b))
        d.ellipse((sx[i] - rr, sy[i] - HV0 - rr, sx[i] + rr, sy[i] - HV0 + rr), fill=c)


_HOJAS = np.random.default_rng(19).random((160, 6)).astype(np.float32)


def hojas_que_caen(img, cam, lz, t, zona=((-20, 20), (0, 14), (-58, 12)), soplo=None, n=160):
    """Hojas de la selva (rajang_hoja) que caen dando vueltas; con 'soplo'
    (centro, instante), el rugido las barre hacia fuera."""
    p = _HOJAS[:n]
    alto = zona[1][1] - zona[1][0]
    X = zona[0][0] + (zona[0][1] - zona[0][0]) * p[:, 0] + 1.2 * np.sin(t * 0.9 + p[:, 3] * 20)
    Y = zona[1][0] + (alto * p[:, 1] - t * (0.9 + 0.8 * p[:, 4])) % alto
    Z = zona[2][0] + (zona[2][1] - zona[2][0]) * p[:, 2] + 0.6 * np.cos(t * 0.8 + p[:, 5] * 13)
    if soplo is not None:
        (cx, cz), t0 = soplo
        u = max(0.0, t - t0)
        if u > 0:
            dx, dz = X - cx, Z - cz
            dd = np.hypot(dx, dz) + 0.5
            emp = 26.0 * u * np.exp(-dd / 30.0) / (1 + u * 0.8)
            X = X + dx / dd * emp
            Z = Z + dz / dd * emp
            Y = Y + 5.0 * u * np.exp(-dd / 25.0) * (0.5 + p[:, 4])
    sx, sy, sz = cam.proyectar(np.stack([X, Y, Z], 1))
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for i in np.argsort(-sz):
        if sz[i] < 0.4 or sz[i] > 60 or not (-50 < sx[i] < W + 50 and HV0 - 50 < sy[i] < HV1 + 50):
            continue
        iy_, ix_ = int(min(max(sy[i] - HV0, 0), HV - 1)), int(min(max(sx[i], 0), W - 1))
        if sz[i] > lz.z[iy_, ix_] + 0.3:
            continue
        lado = int(0.36 * cam.foco / sz[i])
        if lado < 2 or lado > H * 0.07:
            continue
        giro = int((t * 120 * (p[i, 3] - 0.5) + p[i, 4] * 360) // 15 * 15) % 360
        s = sprite(f'rajang_hoja_{int(p[i, 5] * 3) % 3}.png', lado, giro)
        oscuro = math.exp(-sz[i] / 30.0) * 0.55 + 0.2
        s2 = s.copy()
        a = np.array(s2).astype(np.float32)
        a[..., :3] *= oscuro
        s2 = Image.fromarray(a.astype(np.uint8))
        capa.alpha_composite(s2, (int(sx[i] - s2.width / 2), int(sy[i] - s2.height / 2)))
    img.alpha_composite(capa)


def sprites3d(img, cam, lz, lista, desenfoque=0.0):
    """[(P, lado en bloques, nombre, alfa, giro, oscuro)]: particulas propias en 3D,
    tapadas por lo que tengan delante."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for P, lado_b, nombre, alfa, giro, oscuro in lista:
        sx, sy, sz = cam.proyectar(np.asarray(P, float))
        if sz < 2.0 or not (-80 < sx < W + 80 and HV0 - 80 < sy < HV1 + 80):
            continue
        iy_, ix_ = int(min(max(sy - HV0, 0), HV - 1)), int(min(max(sx, 0), W - 1))
        if sz > lz.z[iy_, ix_] + 0.5:
            continue
        lado = int(lado_b * cam.foco / sz)
        if lado < 1 or lado > H * 0.07:
            continue
        s = sprite(nombre, max(2, lado), int(giro) // 15 * 15 % 360)
        if alfa < 0.99 or oscuro != 1.0:
            a = np.array(s).astype(np.float32)
            a[..., :3] *= oscuro
            a[..., 3] *= alfa
            s = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
    if desenfoque:
        img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(desenfoque)))
    img.alpha_composite(capa)


# ----------------------------------------------------------------------
#  Del G-buffer a la imagen: brillo (bloom), curva y la franja de cine
# ----------------------------------------------------------------------
def a_imagen(col, brillo, k_bloom=1.0, extra=None):
    """col y brillo en lineal (franja visible) -> imagen RGBA de pantalla entera."""
    e = np.clip(brillo * 0.5, 0, 1)
    e8 = Image.fromarray((e * 255).astype(np.uint8))
    peq = e8.resize((W // 4, HV // 4), Image.BILINEAR)
    out = col.copy()
    for r_, k_ in ((3 * ESCALA, 0.55), (12 * ESCALA, 0.5)):
        out += np.array(e8.filter(ImageFilter.GaussianBlur(r_))).astype(np.float32) / 255.0 * 2 * k_ * k_bloom
    for r_, k_ in ((10 * ESCALA, 0.45), (30 * ESCALA, 0.35)):
        b = peq.filter(ImageFilter.GaussianBlur(r_)).resize((W, HV), Image.BILINEAR)
        out += np.array(b).astype(np.float32) / 255.0 * 2 * k_ * k_bloom
    if extra is not None:
        out += extra
    out = np.maximum(out, 0)
    out = out * 1.25 / (1 + 0.25 * out)          # la curva: levanta los medios sin quemar lo que brilla
    full = np.zeros((H, W, 3), np.float32)
    full[HV0:HV1] = np.clip(out, 0, 1)
    return Image.fromarray((full * 255).astype(np.uint8)).convert('RGBA')


def suavizar_bordes(img, lz):
    """Un antialias barato: donde salta la profundidad, se mezcla con el
    vecindario (los cantos de los bloques no hacen dientes de sierra)."""
    z = np.where(np.isfinite(lz.z), lz.z, 1e4)
    dz = np.zeros_like(z)
    dz[:, 1:] = np.maximum(dz[:, 1:], np.abs(np.diff(z, axis=1)) / np.minimum(z[:, 1:], z[:, :-1]))
    dz[1:, :] = np.maximum(dz[1:, :], np.abs(np.diff(z, axis=0)) / np.minimum(z[1:, :], z[:-1, :]))
    borde = np.clip((dz - 0.02) * 25, 0, 1)
    borde = np.array(Image.fromarray((borde * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))).astype(np.float32) / 255
    a = np.array(img).astype(np.float32)
    franja = a[HV0:HV1, :, :3]
    bl = np.array(img.crop((0, HV0, W, HV1)).filter(ImageFilter.BoxBlur(1))).astype(np.float32)[..., :3]
    franja[:] = franja * (1 - 0.6 * borde[..., None]) + bl * 0.6 * borde[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ----------------------------------------------------------------------
#  El estado de la escena en cada instante
# ----------------------------------------------------------------------
def radio_costra(t):
    """Hasta donde se ha caido la costra de piedra (bloques desde el pecho)."""
    r = 0.0
    for t0, rad in RADIOS:
        if t >= t0:
            r = r + (rad - r) * suave((t - t0) / 0.28)
    if t >= T_OJOS:
        r = max(r, 4.2 + 30.0 * suave((t - T_OJOS) / 0.5) ** 1.5)
    return r


def k_grupos(t):
    """Lo que brilla del mundo: los glifos del templo despiertan con el."""
    k = np.ones(32, np.float32)
    glifo = 0.0
    if t > T_OJOS:
        glifo = 0.35 * suave((t - T_OJOS) / 0.4)
    if t > T_RUGE:
        glifo += 0.9 * suave((t - T_RUGE) / 0.3)
    k[G_GLIFO] = glifo + 0.02
    k[G_ROCA] = 0.9
    k[G_JADE] = 1.0
    return k


def estado(t):
    lat = latido_k(t)
    despierto = t >= 6.0
    rc = radio_costra(t)
    E = {
        't': t, 'pecho': None, 'R_c': rc, 'R_g': rc + (0.5 if despierto else 0.0),
        'R_m': 0.0 if t < T_RUGE else 26.0 * suave((t - T_RUGE - 0.05) / 0.55) ** 1.3,
        'k_sol': (0.12 + 0.55 * lat) if not despierto else (0.35 + 1.4 * lat),
        'k_ojo': 0.0 if t < T_OJOS else (3.0 * math.exp(-(t - T_OJOS) / 0.12) + 1.1 + 0.5 * (t > T_RUGE)),
        'k_ojo_col': 0.12 if t < T_OJOS else 1.0,
        'k_cristal': 0.0 if t < T_OJOS else 0.25 + 0.3 * suave((t - T_RUGE) / 0.4),
        'k_boca': 0.0 if t < 9.2 else 1.3 * suave((t - 9.3) / 0.4),
        'k_cuerpo': 0.0 if t < T_OJOS else 0.7 + 0.5 * (t > T_RUGE),
        'k_grieta': 0.0 if not despierto else (0.3 if t < T_RUGE else 1.0),
        'k_frente': 0.0 if not despierto or t > T_OJOS + 0.6 else 0.8,
        'ondas': [(tb, 1.0) for tb in LATIDOS if 6.0 <= tb <= t],
        'k_grupo': k_grupos(t),
    }
    return E


LUNA = np.array([-0.35, 0.8, -0.5])         # hacia la luna: alta, por delante y a la izquierda
L_SOMBRA = LUNA / np.linalg.norm(LUNA)


def escena_noche(t, pose, extra_puntos=()):
    """Las luces de la noche en la selva."""
    E = estado(t)
    pecho = punto_rj(pose, 'sol', (0, 3, -118.5))
    E['pecho'] = pecho
    lat = latido_k(t)
    E['luces'] = [(LUNA, C_LUNA, 1.7, 'luna'),
                  ((0.55, 0.45, 0.7), np.array([0.25, 0.55, 0.42], np.float32), 0.55, 'contra'),
                  ((-0.2, 0.3, -1.0), np.array([0.10, 0.16, 0.15], np.float32), 0.5, 'llave')]
    E['amb_cielo'] = np.array([0.075, 0.115, 0.12], np.float32)
    E['amb_suelo'] = np.array([0.03, 0.045, 0.035], np.float32)
    # el sol del pecho alumbra lo de alrededor al latir
    k_sol = E['k_sol']
    E['puntos'] = [(pecho + np.array([0, 0, -0.6]), (0.4, 1.0, 0.45), 0.9 * k_sol, 1.6)]
    if t >= T_OJOS:
        ko = E['k_ojo']
        for o in ('ojo_izq', 'ojo_der'):
            E['puntos'].append((punto_rj(pose, o, (0, 0, -3)), (0.75, 1.0, 0.5), 0.35 * ko, 0.9))
    E['puntos'] += list(extra_puntos)
    E['niebla'] = 0.007
    E['niebla_suelo'] = 0.028
    E['niebla_alto'] = 2.2
    E['c_niebla'] = np.array([0.035, 0.07, 0.065], np.float32)
    E['cielo'] = cielo_noche
    return E


# ----------------------------------------------------------------------
#  1. La selva: la camara se desliza hacia el claro y la estatua
# ----------------------------------------------------------------------
_CAM_OJO = [(0.0, (-27.0, 1.7, -58.5)), (1.7, (-21.5, 2.0, -47.5)), (3.4, (-15.5, 2.3, -35.5)), (5.0, (-10.0, 2.5, -24.5))]
_CAM_OBJ = [(0.0, (-14.0, 2.8, -32.0)), (1.7, (-5.0, 3.6, -12.0)), (3.4, (-1.0, 3.9, -3.0)), (5.0, (0.0, 3.8, -2.5))]


def cam_selva(s):
    ojo = catmull(_CAM_OJO, s)
    obj = catmull(_CAM_OBJ, s)
    ojo = ojo + np.array([0.0, 0.08 * math.sin(s * 1.3), 0.0])
    return CamT(ojo, obj, 50.0 - 4.0 * suave(s / 5.0), 0.012 * math.sin(s * 0.7))


def plano_selva(s, d):
    t = 1.0 + s
    cam = cam_selva(s)
    lz = LienzoG(cam)
    suelo(lz, cam)
    pose = pose_rajang(t)
    sombra = Sombra(L_SOMBRA, (0, 3, 2), 16.0)
    dibujar_rajang(lz, cam, pose, sombra)
    dibujar_mundo(lz, cam)
    E = escena_noche(t, pose)
    E['sombra'] = sombra
    col, brillo = sombrear(lz, cam, E)
    col += haces(lz, cam, LUNA, 1.0) * np.array([0.42, 0.6, 0.62], np.float32)
    capa = Image.new('RGB', (W, HV), (0, 0, 0))
    luciernagas(capa, cam, lz, t, 1.0)
    extra = np.array(capa).astype(np.float32) / 255.0
    extra = extra + np.array(capa.filter(ImageFilter.GaussianBlur(5 * ESCALA))).astype(np.float32) / 255.0 * 3.0
    img = a_imagen(col, brillo, 1.0, extra)
    img = suavizar_bordes(img, lz)
    hojas_que_caen(img, cam, lz, t, zona=((-34, 6), (0, 14), (-62, 8)), n=60)
    return img


# ----------------------------------------------------------------------
#  2. El despertar: el pecho late, la costra se raja; abre los ojos
# ----------------------------------------------------------------------
def polvo_que_cae(t, pose, desde, n=70, zona=4.0, semilla=3):
    """Polvo y chinas que se le caen de la costra con cada latido."""
    r = random.Random(semilla)
    pecho = punto_rj(pose, 'sol', (0, 3, -118.5))
    out = []
    for k in range(n):
        tb = r.choice([x for x in LATIDOS if x >= desde] or [desde])
        vida = t - tb - r.uniform(0, 0.15)
        if vida < 0 or vida > 1.6:
            continue
        p0 = pecho + np.array([r.uniform(-zona, zona), r.uniform(0.5, 3.5), r.uniform(-zona * 0.6, zona * 0.3)])
        p = p0 + np.array([r.uniform(-0.3, 0.3) * vida, -4.9 * vida * vida, r.uniform(-0.3, 0.3) * vida])
        if p[1] < 0.05:
            continue
        al = min(1.0, (1.6 - vida) / 0.4)
        if k % 3 == 0:
            out.append((p, r.choice([0.12, 0.16, 0.2]), f'rajang_roca_{r.randint(0, 2)}.png', al, r.uniform(0, 360), 0.45))
        else:
            out.append((p, r.choice([0.3, 0.45]), f'rajang_polvo_{r.randint(0, 2)}.png', al * 0.45, r.uniform(0, 360), 0.5))
    return out


def costra_estalla(t, pose, n=26, semilla=8):
    """Al abrir los ojos la costra de la cara revienta hacia fuera."""
    r = random.Random(semilla)
    cab = punto_rj(pose, 'cabeza', (0, -4, -40))
    out = []
    for k in range(n):
        vida = t - T_OJOS - r.uniform(0, 0.08)
        if vida < 0 or vida > 1.4:
            continue
        v = np.array([r.uniform(-3, 3), r.uniform(-0.5, 3.5), r.uniform(-6, -1.5)])
        p = cab + np.array([r.uniform(-1.2, 1.2), r.uniform(-0.8, 0.8), r.uniform(-0.6, 0.2)]) + v * vida + np.array([0, -4.9 * vida * vida, 0])
        al = min(1.0, (1.4 - vida) / 0.4)
        if k % 3:
            out.append((p, r.choice([0.1, 0.14, 0.18]), f'rajang_roca_{r.randint(0, 2)}.png', al, r.uniform(0, 360), 0.55))
        else:
            out.append((p, r.choice([0.3, 0.4]), f'rajang_polvo_{r.randint(0, 2)}.png', al * 0.3, r.uniform(0, 360), 0.6))
    return out


def ojos_brillan(img, cam, lz, pose, k, tam=1.0):
    """El fogonazo de los ojos que se ven: un halo verde y la raya de luz."""
    if k <= 0.02:
        return
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for o in ('ojo_izq', 'ojo_der'):
        sx, sy, sz = cam.proyectar(punto_rj(pose, o, (0, 0, -1.2)))
        if sz < 0.5 or not (0 <= sx < W and HV0 <= sy < HV1):
            continue
        if sz > lz.z[int(sy) - HV0, int(sx)] + 0.25:
            continue
        r_ = 34 * ESCALA * tam * min(k, 2.5) ** 0.5
        a = int(min(255, 150 * k))
        d.ellipse((sx - r_, sy - r_ * 0.8, sx + r_, sy + r_ * 0.8), fill=(150, 255, 120, a))
        largo = W * 0.16 * tam * min(k, 2.5) ** 0.6
        d.ellipse((sx - largo, sy - 2.5 * ESCALA, sx + largo, sy + 2.5 * ESCALA), fill=(210, 255, 190, a))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(14 * ESCALA * tam)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(3 * ESCALA)))


def temblor(t, k, semilla=0):
    r = random.Random(int(t * FPS) * 31 + semilla)
    return np.array([r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1)]) * k


def plano_cerca(s, d, t, cam):
    lz = LienzoG(cam)
    suelo(lz, cam)
    pose = pose_rajang(t)
    sombra = Sombra(L_SOMBRA, (0, 3, 2), 16.0)
    dibujar_rajang(lz, cam, pose, sombra)
    dibujar_mundo(lz, cam)
    E = escena_noche(t, pose)
    E['sombra'] = sombra
    col, brillo = sombrear(lz, cam, E)
    col += haces(lz, cam, LUNA, 0.8, pasos=16, lejos=40.0) * np.array([0.42, 0.6, 0.62], np.float32)
    img = a_imagen(col, brillo, 1.0)
    img = suavizar_bordes(img, lz)
    return img, lz, pose


# Las camaras de los planos cercanos: (ojo al empezar, ojo al acabar, a donde mira, campo de vision)
CAMS = {
    'pecho': ((-3.3, 1.2, -14.2), (-2.8, 1.3, -12.6), (-0.2, 2.75, -4.4), 30.0),
    'cara': ((-5.6, 5.9, -16.2), (-4.7, 5.8, -14.6), (-0.4, 5.05, -7.2), 27.0),
    'rugido': ((-17.5, 1.1, -19.5), (-16.3, 1.1, -18.3), (-1.0, 5.2, -2.0), 40.0),
    'cielo': ((-20.5, 1.0, -19.5), (-19.5, 1.0, -18.5), (-1.0, 9.0, 0.5), 52.0),
}


def cam_de(nombre, k):
    a, b, obj, fov = CAMS[nombre]
    return np.array(a) + (np.array(b) - np.array(a)) * k, np.array(obj, float), fov


def plano_pecho(s, d):
    t = 6.0 + s
    lat = latido_k(t)
    ojo, obj, fov = cam_de('pecho', s / d)
    cam = CamT(ojo + temblor(t, 0.02 * lat), obj + temblor(t, 0.03 * lat, 1), fov, -0.03)
    img, lz, pose = plano_cerca(s, d, t, cam)
    sprites3d(img, cam, lz, polvo_que_cae(t, pose, 6.0), 0.6 * ESCALA)
    hojas_que_caen(img, cam, lz, t, zona=((-8, 8), (0, 8), (-14, 0)), n=40)
    return img


def plano_cara(s, d):
    t = 7.5 + s
    lat = latido_k(t)
    acerca = suave(s / d)
    sac = 0.03 * lat + (0.05 * math.exp(-(t - T_OJOS) / 0.25) if t > T_OJOS else 0.0)
    ojo, obj, fov = cam_de('cara', acerca)
    cam = CamT(ojo + temblor(t, sac), obj + temblor(t, sac * 1.5, 2), fov, -0.02)
    img, lz, pose = plano_cerca(s, d, t, cam)
    sprites3d(img, cam, lz, polvo_que_cae(t, pose, 7.3, n=50, zona=3.0, semilla=5) + costra_estalla(t, pose), 0.6 * ESCALA)
    if t > T_OJOS:
        ojos_brillan(img, cam, lz, pose, 2.4 * math.exp(-(t - T_OJOS) / 0.14) + 0.55)
    if t > T_OJOS:                    # el fogonazo de los ojos
        f = destello(t, [(T_OJOS, 1.0)], 0.1)
        if f > 0.01:
            img.alpha_composite(Image.new('RGBA', img.size, (120, 255, 140, int(60 * f))))
    return img


# ----------------------------------------------------------------------
#  3. El rugido: se alza, ruge; la onda, los pinchos y la maldicion
# ----------------------------------------------------------------------
def onda_suelo(t):
    """El anillo de la onda de choque en el suelo: (radio, fuerza)."""
    u = t - T_RUGE - 0.03
    if u < 0 or u > 1.2:
        return None
    return 3.0 + 34.0 * (1 - (1 - min(u / 1.0, 1)) ** 2), math.exp(-u / 0.45)


def grietas_suelo(lz, cam, t, centro=(0.0, -2.0)):
    """Las grietas encendidas que corren por la plaza desde sus zarpas y el anillo de la onda."""
    u = t - T_RUGE
    if u < 0:
        return
    Dx, Dy, Dz = cam.rayos()
    m = lz.grupo == G_SUELO
    iy, ix = np.nonzero(m)
    z = lz.z[iy, ix]
    X = cam.ojo[0] + z * Dx[iy, ix]
    Z = cam.ojo[2] + z * Dz[iy, ix]
    Xq, Zq = np.floor(X * 8) / 8, np.floor(Z * 8) / 8
    rx, rz = Xq - centro[0], Zq - centro[1]
    r_ = np.hypot(rx, rz)
    th = np.arctan2(rz, rx)
    R = 2.5 + 22.0 * suave(u / 0.7)
    gl = np.zeros(len(z), np.float32)
    for k in range(11):
        a0 = k / 11 * TAU + 0.3
        thk = a0 + 0.22 * np.sin(r_ * 0.33 + k * 1.7) + 0.08 * np.sin(r_ * 1.4 + k)
        dang = np.angle(np.exp(1j * (th - thk)))
        dl = np.abs(dang) * r_
        ancho = 0.16 * np.clip(1.2 - r_ / 22, 0.2, 1)
        gl = np.maximum(gl, (dl < ancho) * (r_ < R) * (r_ > 2.5))
    gl *= np.clip(1.3 - r_ / 24, 0, 1)
    o = onda_suelo(t)
    anillo = np.zeros(len(z), np.float32)
    if o is not None:
        anillo = np.exp(-((r_ - o[0]) / 0.9) ** 2) * o[1]
    add = gl[:, None] * np.array([0.55, 1.0, 0.3], np.float32) * 1.6 + anillo[:, None] * np.array([0.6, 1.0, 0.7], np.float32) * 0.9
    lz.em[iy, ix] += add
    lz.alb[iy, ix] *= (1 - 0.7 * gl)[:, None]


def escombros_rugido(t, n=90, semilla=21):
    """Terrones, polvo y hojas que salen despedidos con la onda."""
    r = random.Random(semilla)
    out = []
    for k in range(n):
        t0 = T_RUGE + r.uniform(0.02, 0.3)
        vida = t - t0
        if vida < 0 or vida > 1.6:
            continue
        a = r.uniform(0, TAU)
        rad = r.uniform(3, 12)
        v = np.array([math.cos(a) * r.uniform(5, 14), r.uniform(3, 9), math.sin(a) * r.uniform(5, 14)])
        p = np.array([math.cos(a) * rad, 0.2, -2 + math.sin(a) * rad]) + v * vida + np.array([0, -9.8 * vida * vida * 0.5, 0])
        if p[1] < 0:
            continue
        al = min(1.0, (1.6 - vida) / 0.5)
        c = k % 4
        if c == 0:
            out.append((p, r.choice([0.6, 0.9, 1.2]), f'rajang_polvo_{r.randint(0, 2)}.png', al * 0.45, r.uniform(0, 360), 0.55))
        elif c == 1:
            out.append((p, r.choice([0.3, 0.45]), f'rajang_hoja_{r.randint(0, 2)}.png', al, r.uniform(0, 360) + vida * 400, 0.6))
        else:
            out.append((p, r.choice([0.22, 0.32, 0.45]), f'rajang_roca_{r.randint(0, 2)}.png', al, r.uniform(0, 360) + vida * 300, 0.7))
    return out


def plano_rugido(s, d):
    t = 9.0 + s
    u = t - T_RUGE
    sac = 0.04 + (0.22 * math.exp(-max(0.0, u) / 0.5) if u > 0 else 0.0)
    ojo, obj, fov = cam_de('rugido', s / d)
    cam = CamT(ojo + temblor(t, sac), obj + temblor(t, sac * 2.2, 3), fov,
               0.04 + (0.03 * math.sin(t * 40) * math.exp(-u / 0.4) if u > 0 else 0))
    lz = LienzoG(cam)
    suelo(lz, cam)
    pose = pose_rajang(t)
    sombra = Sombra(L_SOMBRA, (0, 4, 0), 20.0)
    dibujar_rajang(lz, cam, pose, sombra)
    dibujar_pinchos(lz, cam, t, sombra)
    dibujar_mundo(lz, cam)
    grietas_suelo(lz, cam, t)
    boca = punto_rj(pose, 'cabeza', (0, 6, -54))
    E = escena_noche(t, pose, [(boca, (0.55, 1.0, 0.4), 1.5 * suave((t - 9.3) / 0.4), 2.5)])
    E['sombra'] = sombra
    if u > 0:     # la maldicion lo enciende: luz verde desde dentro
        E['puntos'].append((E['pecho'] + np.array([0, 1.5, 0]), (0.6, 1.0, 0.35), 2.2 * suave(u / 0.4), 7.0))
    col, brillo = sombrear(lz, cam, E)
    col += haces(lz, cam, LUNA, 0.7, pasos=16, lejos=50.0) * np.array([0.42, 0.6, 0.62], np.float32)
    capa = Image.new('RGB', (W, HV), (0, 0, 0))
    luciernagas(capa, cam, lz, t, 0.8, huida=suave(u / 1.0) if u > 0 else 0.0)
    extra = np.array(capa).astype(np.float32) / 255.0 + np.array(capa.filter(ImageFilter.GaussianBlur(5 * ESCALA))).astype(np.float32) / 255.0 * 3
    f = destello(t, [(T_RUGE + 0.02, 0.5)], 0.12)
    extra += f * np.array([0.25, 0.45, 0.2], np.float32)
    img = a_imagen(col, brillo, 1.1, extra)
    img = suavizar_bordes(img, lz)
    sprites3d(img, cam, lz, escombros_rugido(t), 0.8 * ESCALA)
    ojos_brillan(img, cam, lz, pose, 0.35 + (0.9 * math.exp(-u / 0.3) if u > 0 else 0.0), 0.6)
    hojas_que_caen(img, cam, lz, t, zona=((-18, 18), (0, 12), (-22, 14)), soplo=((0.0, -2.0), T_RUGE + 0.03), n=120)
    # la onda empuja el aire: un anillo que se abre en la pantalla
    if 0 < u < 0.7:
        bx, by, _ = cam.proyectar(boca)
        k = u / 0.7
        ar = Image.new('RGBA', img.size, (0, 0, 0, 0))
        rad = W * 0.9 * k ** 0.7
        ImageDraw.Draw(ar).ellipse((bx - rad, by - rad * 0.6, bx + rad, by + rad * 0.6), outline=(190, 255, 170, int(90 * (1 - k))),
                                   width=max(2, int(14 * ESCALA * (1 - k * 0.6))))
        img.alpha_composite(ar.filter(ImageFilter.GaussianBlur(9 * ESCALA)))
    return img


# ----------------------------------------------------------------------
#  4. El cielo se raja: se encabrita y caen los fragmentos de jade
# ----------------------------------------------------------------------
GRIETA_CIELO = (0.62, 0.02)            # donde se abre, en la pantalla (fraccion de W y de H)


def grieta_cielo(k, semilla=7):
    """La raja del cielo, en bloques: tramos rectos y quiebros secos, con sus
    ramas; el nucleo casi blanco y el halo lima. k: cuanto se ha abierto."""
    r = random.Random(semilla)
    b = max(1, int(6 * ESCALA))
    w, h = W // b + 1, H // b + 1
    capa = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(capa)
    gx, gy = GRIETA_CIELO[0] * W / b, GRIETA_CIELO[1] * H / b + 30 * ESCALA / b

    def rama(x, y, a, largo, grueso, prof):
        for s_ in range(int(largo)):
            quiebro = r.choice([-1, 1]) * r.uniform(0.35, 0.8) if s_ % 2 else 0.0
            paso = r.uniform(40, 80) * ESCALA / b
            x1, y1 = x + math.cos(a + quiebro) * paso, y + math.sin(a + quiebro) * paso
            if s_ / max(1, largo) < k:
                g = max(1, int(round(grueso * (1 - s_ / (largo + 1)) ** 0.8)))
                d.line((x, y, x1, y1), fill=255, width=g)
                if prof < 1 and r.random() < 0.45:
                    rama(x1, y1, a + r.choice([-1, 1]) * r.uniform(0.7, 1.2), max(2, largo * 0.4), grueso * 0.5, prof + 1)
            x, y = x1, y1
    for a, largo in ((math.pi * 0.95, 9), (0.15, 5), (math.pi * 0.62, 4), (math.pi * 0.3, 3)):
        rama(gx, gy, a, largo, 3.6, 0)
    capa = capa.resize((w * b, h * b), Image.NEAREST).crop((0, 0, W, H))
    g = np.array(capa).astype(np.float32) / 255
    halo = np.array(capa.filter(ImageFilter.GaussianBlur(12 * ESCALA))).astype(np.float32) / 255
    lejos = np.array(capa.filter(ImageFilter.GaussianBlur(60 * ESCALA))).astype(np.float32) / 255
    return (g[..., None] * np.array([0.9, 1.0, 0.6]) + halo[..., None] * np.array([0.5, 0.95, 0.25]) * 0.8
            + lejos[..., None] * np.array([0.3, 0.62, 0.16]) * 0.7).astype(np.float32)[HV0:HV1]


# Los fragmentos que caen: (salida en el cielo, impacto en el suelo, instante del impacto, tam, semilla)
FRAGMENTOS = [((60.0, 95.0, 120.0), (-14.0, 0.0, 6.0), 11.95, 1.4, 3), ((80.0, 110.0, 140.0), (16.0, 0.0, 14.0), 11.7, 1.3, 5),
              ((40.0, 100.0, 130.0), (-4.0, 0.0, 26.0), 11.85, 1.5, 8), ((45.0, 85.0, 70.0), (-12.0, 0.0, -3.0), T_IMPACTO, 1.3, 11),
              ((90.0, 120.0, 160.0), (24.0, 0.0, 30.0), 12.1, 1.4, 13)]
T_CAIDA = 1.1


def fragmento(lz, cam, t, salida, impacto, t_imp, tam, sem):
    """Un fragmento de jade cayendo: el terron que da vueltas, la llama que lo
    envuelve y la estela de tres cintas."""
    u = 1 - (t_imp - t) / T_CAIDA
    if u < 0 or u > 1:
        return None
    a, b = np.array(salida), np.array(impacto)
    p = a + (b - a) * u
    dv = (b - a) / np.linalg.norm(b - a)
    jade, llama = racimo(sem)
    giro = (t * 5.0 + sem, t * 3.3, t * 4.1)
    M = vr.T(*p) @ vr.Ry(giro[1]) @ vr.Rx(giro[0]) @ vr.Rz(giro[2]) @ vr.S(tam)
    pintar_piezas(lz, cam, jade, M, TEX_JADE, G_JADE)
    pintar_piezas(lz, cam, llama, M, TEX_LLAMA, G_JADE, aditivo=0.35)
    cabeza, cola = p + dv * 0.4 * tam, p - dv * 14.0 * tam
    l0 = np.cross(dv, [1.0, 0.0, 0.0])
    l0 /= np.linalg.norm(l0)
    m0 = np.cross(dv, l0)
    for k in range(3):
        ang = math.pi * k / 3
        l = l0 * math.cos(ang) + m0 * math.sin(ang)
        pts = np.array([cabeza - l * 1.5 * tam, cabeza + l * 1.5 * tam, cola + l * 0.4 * tam, cola - l * 0.4 * tam])
        lz.cara(pts, [(0, 0), (1, 0), (1, 1), (0, 1)], TEX_ESTELA, G_JADE, np.array([0, 1, 0], np.float32), aditivo=1.0)
    return p


def plano_cielo(s, d):
    t = 10.7 + s
    f_imp = destello(t, [(T_IMPACTO, 1.0)], 0.07)
    ojo, obj, fov = cam_de('cielo', s / d)
    cam = CamT(ojo + temblor(t, 0.05 + 0.25 * f_imp), obj + temblor(t, 0.08 + 0.4 * f_imp, 4), fov, -0.05)
    lz = LienzoG(cam)
    suelo(lz, cam)
    pose = pose_rajang(t)
    sombra = Sombra(L_SOMBRA, (0, 5, 0), 20.0)
    dibujar_rajang(lz, cam, pose, sombra)
    dibujar_pinchos(lz, cam, t, sombra)
    dibujar_mundo(lz, cam, lejos=160.0)
    grietas_suelo(lz, cam, t)
    puntos = []
    for salida, impacto, t_imp, tam, sem in FRAGMENTOS:
        p = fragmento(lz, cam, t, salida, impacto, t_imp, tam, sem)
        if p is not None:
            puntos.append((p, (0.5, 1.0, 0.4), 3.0, 6.0))
    abre = suave(s / 0.45)
    E = escena_noche(t, pose, puntos)
    E['sombra'] = sombra
    E['puntos'].append((E['pecho'] + np.array([0, 1.5, 0]), (0.6, 1.0, 0.35), 2.2, 7.0))
    # la grieta del cielo lo recorta en lima por detras
    E['luces'].append(((0.45, 0.7, 0.55), np.array([0.6, 1.0, 0.35], np.float32), 2.6 * abre, 'contra'))
    E['luces'].append(((0.3, 0.8, 0.5), np.array([0.35, 0.6, 0.25], np.float32), 0.7 * abre, 'llave'))
    E['amb_cielo'] = E['amb_cielo'] + np.array([0.07, 0.14, 0.05], np.float32) * abre
    raja = grieta_cielo(abre)

    def cielo_rajado(cam_, Dx, Dy, Dz):
        c = cielo_noche(cam_, Dx, Dy, Dz)
        c = c * (1 - 0.4 * abre) + np.array([0.03, 0.08, 0.04], np.float32) * abre
        yy, xx = np.mgrid[0:HV, 0:W].astype(np.float32)
        dd = np.hypot((xx - GRIETA_CIELO[0] * W) / W, (yy + HV0 - GRIETA_CIELO[1] * H) / W)
        c += (np.exp(-(dd / 0.35) ** 2) * 0.25 * abre)[..., None] * np.array([0.35, 0.7, 0.2], np.float32)
        return c + raja
    E['cielo'] = cielo_rajado
    col, brillo = sombrear(lz, cam, E)
    brillo += raja * (~np.isfinite(lz.z))[..., None] * 0.6
    extra = f_imp * np.array([0.5, 0.8, 0.45], np.float32) * 0.7
    img = a_imagen(col, brillo, 1.15, extra)
    img = suavizar_bordes(img, lz)
    sprites3d(img, cam, lz, escombros_rugido(t, n=60, semilla=33), 0.8 * ESCALA)
    # chispas de la llama verde que dejan los fragmentos
    r = random.Random(int(t * FPS))
    lista = []
    for salida, impacto, t_imp, tam, sem in FRAGMENTOS:
        u = 1 - (t_imp - t) / T_CAIDA
        if not 0 < u < 1:
            continue
        a, b = np.array(salida), np.array(impacto)
        for k in range(8):
            q = a + (b - a) * max(0.0, u - r.uniform(0.01, 0.12)) + np.array([r.gauss(0, 0.8), r.gauss(0, 0.8), r.gauss(0, 0.8)])
            lista.append((q, r.choice([0.5, 0.7, 0.9]), f'rajang_llama_{r.randint(0, 2)}.png', 1.0, 0, 1.0))
    # el que cae delante revienta: esquirlas de jade y llama verde
    u = t - T_IMPACTO
    if u > 0:
        r = random.Random(77)
        b = np.array(FRAGMENTOS[3][1]) + np.array([0, 0.5, 0])
        lista = []
        for k in range(56):
            v = np.array([r.uniform(-1, 1), r.uniform(0.3, 1.2), r.uniform(-1, 1)]) * r.uniform(8, 18)
            q = b + v * u + np.array([0, -4.9 * u * u, 0])
            nombre = f'rajang_jade_{r.randint(0, 2)}.png' if k % 2 else f'rajang_llama_{r.randint(0, 2)}.png'
            lista.append((q, r.choice([0.9, 1.2, 1.6]), nombre, 1.0, r.uniform(0, 360), 1.0))
        sprites3d(img, cam, lz, lista, 1.0 * ESCALA)
    sprites3d(img, cam, lz, lista)
    if s > d - 0.1:
        img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, int(255 * suave((s - (d - 0.1)) / 0.08)))))
    return img


# ----------------------------------------------------------------------
#  Cierre: su nombre
# ----------------------------------------------------------------------
def fuente(n, t):
    return ImageFont.truetype('C:/Windows/Fonts/' + n, int(t * ESCALA))


T_LATIDOS_TITULO = (0.15, 0.55, 1.35, 1.75)


def titulo(s):
    if 'fondo_t' not in _CACHE:
        y = np.linspace(0, 1, H)[:, None, None]
        arriba, abajo = np.array([0.018, 0.06, 0.04]), np.array([0.003, 0.01, 0.006])
        f = arriba + (abajo - arriba) * y ** 0.7
        f = np.broadcast_to(f, (H, W, 3)).copy()
        capa = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(capa)
        r = random.Random(7)
        for _ in range(7):
            x = r.uniform(0.05, 0.95) * W
            ancho = r.uniform(0.02, 0.06) * W
            inc = r.uniform(-0.25, 0.1) * W
            d.polygon([(x, 0), (x + ancho, 0), (x + ancho + inc + ancho, H), (x + inc - ancho * 0.3, H)], fill=r.randint(30, 70))
        rayos = np.array(capa.filter(ImageFilter.GaussianBlur(W / 60))).astype(float) / 255.0
        f += rayos[..., None] * np.array([0.09, 0.3, 0.16]) * 0.6
        _CACHE['fondo_t'] = f
        g = os.path.join(A, 'gui')
        nombre = Image.open(os.path.join(g, 'rajang_barra_nombre.png')).convert('RGBA')
        nombre = nombre.crop(nombre.getbbox())
        k = max(1, int(W * 0.42 / nombre.width))
        _CACHE['nombre'] = nombre.resize((nombre.width * k, nombre.height * k), Image.NEAREST)
        _CACHE['soles'] = [Image.open(os.path.join(g, f'rajang_barra_sol_{i}.png')).convert('RGBA') for i in (1, 2, 3, 4)]
        _CACHE['runas'] = [Image.open(os.path.join(PART, f'rajang_runa_{i}.png')).convert('RGBA') for i in (0, 1, 2)]
    entra = suave(s / 0.7)
    fondo = _CACHE['fondo_t'] * (0.35 + 0.65 * entra)
    img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    n = _CACHE['nombre']
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    x, y = (W - n.width) // 2, int(H * 0.47) - n.height // 2
    capa.alpha_composite(n, (x, y + int((1 - entra) * 18 * ESCALA)))
    # el sol de jade, latiendo: con cada latido la maldicion avanza una fase
    lat, fase = 0.0, 0
    for i, t0 in enumerate(T_LATIDOS_TITULO):
        if s >= t0:
            lat = max(lat, math.exp(-(s - t0) / 0.12))
            fase = i
    lado = int(150 * ESCALA * (1 + 0.1 * lat))
    sol = _CACHE['soles'][fase].resize((lado, lado), Image.NEAREST)
    cy = y - int(175 * ESCALA)
    capa.alpha_composite(sol, ((W - lado) // 2, cy - lado // 2))
    # las runas de oro de la Piel de Jade, a cada lado
    for sg in (-1, 1):
        for j in range(3):
            ru = _CACHE['runas'][0]
            lr = int(56 * ESCALA)
            ru = ru.resize((lr, lr), Image.NEAREST)
            cx_ = W // 2 + sg * int(lado * 0.5 + 34 * ESCALA + (j + 0.5) * lr * 1.25)
            al = 1.0 - 0.3 * j
            r2 = ru.copy()
            r2.putalpha(r2.getchannel('A').point(lambda v, al=al: int(v * al)))
            capa.alpha_composite(r2, (cx_ - lr // 2, cy - lr // 2))
    d = ImageDraw.Draw(capa)
    f1 = fuente('Montserrat-SemiBoldItalic.ttf', 30)
    t1 = 'El Jaguar de Jade'
    if s > 0.6:
        a1 = suave((s - 0.6) / 0.6)
        d.text(((W - d.textlength(t1, font=f1)) / 2, y + n.height + int(26 * ESCALA)), t1, font=f1,
               fill=(214, 236, 214, int(255 * a1)))
    f2 = fuente('Montserrat-Bold.ttf', 26)
    t2 = 'P R Ó X I M A M E N T E'
    if s > 1.0:
        a2 = suave((s - 1.0) / 0.6)
        ty = y + n.height + int(92 * ESCALA)
        d.text(((W - d.textlength(t2, font=f2)) / 2, ty), t2, font=f2, fill=(118, 236, 158, int(255 * a2)))
        lw = int(70 * ESCALA * a2)
        d.rectangle((W // 2 - lw, ty + int(50 * ESCALA), W // 2 + lw, ty + int(54 * ESCALA)), fill=(248, 217, 124, int(255 * a2)))
    capa.putalpha(capa.getchannel('A').point(lambda v: int(v * entra)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(18 * ESCALA)))
    # el latido tine el aire alrededor del sol, del verde al oro
    if lat > 0.02:
        tono = [(70, 220, 110), (110, 240, 90), (190, 255, 70), (255, 220, 90)][fase]
        halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
        rr = int(170 * ESCALA)
        ImageDraw.Draw(halo).ellipse((W // 2 - rr, cy - rr, W // 2 + rr, cy + rr), fill=(*tono, int(70 * lat * entra)))
        img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(60 * ESCALA)))
    img.alpha_composite(capa)
    salida = suave((3.0 - s) / 0.6)
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
    f = f * np.array([0.97, 1.0, 0.98], np.float32)
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
        img = {'selva': plano_selva, 'pecho': plano_pecho, 'cara': plano_cara, 'rugido': plano_rugido,
               'cielo': plano_cielo}[nombre](s, d)
        if nombre == 'selva':
            k = suave(s / 0.8)
            if k < 1:
                img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, int(255 * (1 - k)))))
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


def grave(x, fc):
    """Paso bajo (en frecuencia, con el corte suave)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def tono(x, k):
    """Cambia el tono (y la duracion) por k: k < 1 lo hace mas grave y lento."""
    n = int(len(x) / k)
    return np.interp(np.arange(n) * k, np.arange(len(x)), x)


def latido_sonido(fuerza=1.0):
    """Un latido de piedra: el 'toc' hondo del reloj y la columna, mucho mas graves."""
    a = grave(tono(cargar_ogg('reloj'), 0.5), 260)
    b = grave(tono(cargar_ogg('pilar1')[:int(0.5 * SR)], 0.55), 180)
    b *= np.linspace(1, 0, len(b)) ** 2
    n = max(len(a), len(b))
    x = np.zeros(n)
    x[:len(a)] += a / max(1e-9, np.abs(a).max()) * 0.9
    x[:len(b)] += b / max(1e-9, np.abs(b).max()) * 0.7
    return x * fuerza


def mezcla():
    n = int(TOTAL * SR)
    pista = np.zeros(n)

    def poner(x, t, vol=1.0, dur=None, fundido=0.15, desde=0.0, entrada=0.0, corte=None):
        if isinstance(x, str):
            x = cargar_ogg(x)
        x = x[int(desde * SR):].copy()
        if corte:
            x = grave(x, corte)
        if dur:
            x = x[:int(dur * SR)].copy()
            f = min(len(x), int(fundido * SR))
            x[-f:] *= np.linspace(1, 0, f)
        if entrada:
            e = min(len(x), int(entrada * SR))
            x[:e] *= np.linspace(0, 1, e)
        i = int(t * SR)
        if i < 0:
            x, i = x[-i:], 0
        x = x[:max(0, n - i)]
        pista[i:i + len(x)] += x * vol

    lat = latido_sonido()
    # negro: la tierra retumba muy hondo; la selva: la estatua respira como piedra
    poner('columna', 0.0, 0.4, dur=6.4, fundido=1.2, entrada=1.0, corte=500)
    poner('dormido1', 0.6, 0.55, dur=5.7, fundido=1.0, entrada=0.5)
    # el corazon de jade: lento, y en el despertar cada vez mas seguido y fuerte
    for k, t in enumerate(LATIDOS):
        fuerza = 0.32 + 0.05 * k if t < 6 else 0.6 + 0.08 * (k - 4)
        poner(lat, t, fuerza)
        poner(lat, t + 0.24, fuerza * 0.55)
    # las grietas que corren y la costra que se raja y se cae
    poner('grieta1', 6.1, 0.55)
    poner('grieta2', 7.28, 0.55)
    poner('despertar', 6.0, 0.6, dur=2.45, fundido=0.3, desde=0.3)
    poner('piel_jade', 7.7, 0.35, dur=1.4, fundido=0.4, desde=1.0)
    # abre los ojos: el jade que canta y el grunido
    poner('marca1', T_OJOS - 0.02, 0.8)
    poner('inmune1', T_OJOS, 0.6)
    poner('grunido1', T_OJOS + 0.15, 0.95)
    # se alza y ruge: la onda, los pinchos y la tierra que tiembla
    poner('despertar', T_RUGE - 0.75, 0.9, desde=2.0, dur=3.0, fundido=0.4)
    poner('rugido1', T_RUGE - 0.02, 0.6, dur=2.0, fundido=0.5)
    poner('onda1', T_RUGE + 0.03, 0.9)
    poner('terremoto1', T_RUGE + 0.05, 0.55, dur=2.0, fundido=0.6)
    for k, (x, z, tam, rumbo, sem, t0) in enumerate(sorted(PINCHOS, key=lambda p: p[5])[:6]):
        poner(f'pico{k % 3 + 1}', t0 - 0.03, 0.55 if k else 0.8)
    poner('pilar1', T_RUGE + 0.12, 0.6)
    # el cielo se raja y caen los fragmentos
    poner('cataclismo', 10.7 - 0.6, 0.85, desde=0.6, dur=2.2, fundido=0.5)
    poner('cielo', 10.72, 0.9)
    poner('fragmento1', 10.7, 0.8, desde=T_CAIDA + 0.9 - (T_IMPACTO - 10.7), dur=T_IMPACTO - 10.7)
    poner('impacto1', T_IMPACTO, 1.0)
    # su nombre: el golpe y los cuatro latidos de las fases
    poner('impacto2', 12.2, 0.6, corte=900)
    for k, t0 in enumerate(T_LATIDOS_TITULO):
        poner(lat, 12.2 + t0, 0.55 + 0.08 * k)
    poner('ambiente2', 12.4, 0.3, dur=2.8, fundido=1.4, entrada=0.4, corte=1500)
    # un limitador suave y a -1 dB
    pista = np.tanh(pista / max(1e-9, np.percentile(np.abs(pista), 99.9)) * 1.2)
    pista /= max(1e-9, np.max(np.abs(pista))) / 0.89
    est = np.stack([pista, np.roll(pista, int(0.012 * SR)) * 0.96], axis=1)
    ruta = os.path.join(TRAB, 'teaser.wav')
    sf.write(ruta, est.astype(np.float32), SR)
    return ruta


def main():
    total = int(round(TOTAL * FPS))
    if MUESTRAS:
        tiempos = [float(x) for x in os.environ.get('TIEMPOS', '2.0,4.6,5.8,6.9,8.0,8.6,9.5,10.0,11.3,13.6').split(',')]
        ims = [fotograma(int(round(t * FPS))) for t in tiempos]
        w, h = ims[0].size
        hoja = Image.new('RGB', (w * 2, h * ((len(ims) + 1) // 2)), (0, 0, 0))
        for k, im in enumerate(ims):
            hoja.paste(im, ((k % 2) * w, (k // 2) * h))
        hoja.save(SALIDA)
        print('muestras', len(ims))
        return
    parte = os.environ.get('PARTE')
    k0, paso = (int(parte.split('/')[0]), int(parte.split('/')[1])) if parte else (0, 1)
    for i in range(k0, total, paso):
        ruta = os.path.join(CUADROS, f'{i:04d}.png')
        if os.path.exists(ruta):
            continue
        fotograma(i).save(ruta + '.tmp.png')
        os.replace(ruta + '.tmp.png', ruta)
        if i % 24 == k0 % 24:
            print('fotograma', i, '/', total, flush=True)
    if parte:
        return
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

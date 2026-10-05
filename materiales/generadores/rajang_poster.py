"""
Poster promocional de Rajang, el Jaguar de Jade, en la plaza de su templo,
en lo hondo de la selva, con el Cataclismo de Jade en marcha. Presenta al
jefe: el grande a la derecha, su nombre a la izquierda y nada mas (ni
jugadores ni lista de ataques).

Rajang en la fase IV (Corazon), de tres cuartos por delante, con la camara
baja y lejos para que se le vea entero: a cuatro patas, agazapado y a punto
de saltar, las manos plantadas, la cresta de cristales encendida en los
hombros, la cabeza baja y adelantada rugiendo con los sables de perfil y la
cola en alto. De la zarpa sale una fila de pinchos de roca escalonados que
se aleja por la plaza. Detras, el cielo se ha rajado
y de la grieta llueven fragmentos de jade con su estela de llama verde; uno
viene de frente hacia quien mira. A su alrededor giran los aros de runas de
oro de la Piel de Jade (por detras de el; por delante solo le pasan por las
patas). Arriba, su barra de jefe tal cual sale en el juego.

Todo lo que sale esta hecho para el mod: la malla del juego con su atlas y su
capa de brillo de la fase IV (rajang_juego.py), los pinchos y los fragmentos
con la forma y las texturas que usa el juego (RajangDibujo, PicoTierraRenderer,
FragmentoJadeRenderer), el suelo de la plaza y las grietas de la ficha
(tierra_escenas.py, tierra_ataques.py), la selva lejana en bloques, el cielo
rajado, los haces de luz, las
particulas propias y la barra. Las fuentes son las del sistema.

Uso: python rajang_poster.py <raiz del proyecto> <salida.png> [escala]
"""
import math, os, sys, random, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
ESCALA = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_argv = sys.argv
sys.argv = [_argv[0], RAIZ, tempfile.mkdtemp()]
import vigia_render as vr
import tierra_ataques as ta
import tierra_escenas as ts
import rajang_juego as rj
import rajang_juego_anim as ra
sys.argv = _argv

A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
P = os.path.join(A, 'particle')
GUI = os.path.join(A, 'gui')
ENT = os.path.join(A, 'entity/rajang')
FUENTES = 'C:/Windows/Fonts/'
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
SS = 2
FASE = 4
TAU = math.tau

JADE = (118, 236, 158, 255)
ORO = (0xF8, 0xD9, 0x7C, 255)
BLANCO = (244, 248, 236, 255)
GRIS = (182, 204, 188, 255)


def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, int(tam * ESCALA))


def px(n):
    return int(round(n * ESCALA))


# ----------------------------------------------------------------------
#  El lienzo: el de vigia_render, pero lo opaco que tapa algo le borra
#  tambien el brillo. Con las grietas de la fase IV encendidas por todo el
#  cuerpo, si no, el brillo de las caras de detras se veria a traves.
# ----------------------------------------------------------------------
class Lienzo(vr.Lienzo):
    def triangulo(self, cam, P_, UV, tex, luz_fn, emis_tex=None, niebla=None, aditivo=False, brillo=1.0, envolver=False,
                  translucido=0.0):
        if aditivo or translucido > 0:
            return super().triangulo(cam, P_, UV, tex, luz_fn, emis_tex, niebla, aditivo, brillo, envolver, translucido)
        s = [cam.proyectar(p) for p in P_]
        if min(q[2] for q in s) < 0.05:
            return
        xs = [q[0] for q in s]
        ys = [q[1] for q in s]
        x0, x1 = max(int(math.floor(min(xs))), 0), min(int(math.ceil(max(xs))), self.W - 1)
        y0, y1 = max(int(math.floor(min(ys))), 0), min(int(math.ceil(max(ys))), self.H - 1)
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
        z = 1 / (l1 / az + l2 / bz + l3 / cz)
        u = (l1 * UV[0][0] / az + l2 * UV[1][0] / bz + l3 * UV[2][0] / cz) * z
        v = (l1 * UV[0][1] / az + l2 * UV[1][1] / bz + l3 * UV[2][1] / cz) * z
        th, tw = tex.shape[:2]
        if envolver:
            tu, tv = np.floor(u * tw).astype(int) % tw, np.floor(v * th).astype(int) % th
        else:
            tu, tv = np.clip((u * tw).astype(int), 0, tw - 1), np.clip((v * th).astype(int), 0, th - 1)
        texel = tex[tv, tu]
        zb = self.z[y0:y1 + 1, x0:x1 + 1]
        m = dentro & (texel[..., 3] > 25) & (z < zb)
        if not m.any():
            return
        rgb = texel[..., :3] / 255.0 * luz_fn
        if niebla is not None:
            f = niebla(z)[..., None]
            rgb = rgb * (1 - f) + np.array(niebla.color) * f
        col = self.color[y0:y1 + 1, x0:x1 + 1]
        col[m] = rgb[m]
        self.alfa[y0:y1 + 1, x0:x1 + 1][m] = 1.0
        zb[m] = z[m]
        em = self.emis[y0:y1 + 1, x0:x1 + 1]
        em[m] = 0.0
        if emis_tex is not None:
            et = emis_tex[tv, tu]
            ea = et[..., 3] / 255.0
            me = m & (ea > 0.01)
            k = 1.0 if niebla is None else (1 - niebla(z))[..., None]
            em[me] = (et[..., :3] / 255.0 * ea[..., None] * brillo * k)[me]
            col[me] = np.maximum(col, et[..., :3] / 255.0 * k)[me]


# ----------------------------------------------------------------------
#  La pose: a cuatro patas, agazapado y a punto de saltar. Las manos bien
#  plantadas y abiertas, los hombros (con la cresta) en alto, la cabeza baja
#  y adelantada, algo girada hacia quien mira, rugiendo con los sables de
#  perfil; las patas de atras flexionadas y la cola en alto, en ese.
#  Las patas estan resueltas para que las cuatro zarpas apoyen en el suelo
#  (rj.a_bloques da 0,28 en las manos y 0,16 en los pies, como en reposo, y
#  nada queda por debajo del suelo). Fase IV: los cristales crecidos (como
#  RajangModel.crecer) y sin peto.
# ----------------------------------------------------------------------
def pose_poster():
    pose = ra.sumar(ra.cuerpo(x=-5, baja=14),
                    ra.mano(1, 14.0, -29.5, 20.5, 9), ra.mano(-1, 20.0, -28.9, 13.9, 9),
                    ra.pata(1, -33.4, 38.3, -10, 10.1, 5), ra.pata(-1, -30.1, 43.2, -10, 1.9, 5),
                    ra.cabeza(x=8, y=-14, boca=36, cuello=14, cuello_y=-12, orejas=-26),
                    ra.cola(sube=34, lado=-24, fase=1.4, onda=18))
    k = 1.55
    for c in rj.CRISTALES:
        d = pose.setdefault(c, {})
        e = d.get('esc', (1, 1, 1))
        d['esc'] = (e[0] * math.sqrt(k), e[1] * k, e[2] * math.sqrt(k))
    pose['peto'] = {'oculto': True}
    return pose


# ----------------------------------------------------------------------
#  Escena: camara baja (a la altura de los ojos de un jugador) y lejos, de
#  tres cuartos por delante, mirando un poco hacia arriba: se le ve entero,
#  de la cabeza a la cola.
# ----------------------------------------------------------------------
RAJANG_EN = (3.0, 0.0, 3.0)
GUINADA = float(os.environ.get('GUINADA', '-22'))
CAM = vr.Camara(ojo=(-7.982, 1.2, -21.666), objetivo=(-2.091, 3.248, -13.849), fov=32, ancho=W * SS, alto=H * SS)


def hacia(derecha, arriba, fondo):
    """Una direccion del mundo dada en la base de la camara (derecha, arriba y
    hacia el fondo de la imagen)."""
    d = CAM.r * derecha + np.array([0.0, 1.0, 0.0]) * arriba + np.array([CAM.f[0], 0.0, CAM.f[2]]) * fondo
    return tuple(d / np.linalg.norm(d))


LUCES = [
    (hacia(-0.6, 0.55, -0.6), (1.0, 0.9, 0.7), 0.95, 'llave'),     # luz calida por delante: la cara se lee
    (hacia(0.55, 0.75, 0.6), (0.78, 1.0, 0.42), 1.5, 'contra'),     # la grieta del cielo lo recorta en lima
    (hacia(-0.9, 0.25, 0.5), (0.4, 1.0, 0.62), 1.1, 'contra'),      # el jade de la selva, por la izquierda
]
AMBIENTE = (0.14, 0.2, 0.16)
LUCES_MUNDO = [
    (hacia(0.4, 0.8, 0.4), (0.62, 0.86, 0.5), 0.75, 'llave'),
    (hacia(-0.6, 0.5, -0.5), (0.9, 0.78, 0.55), 0.4, 'llave'),
]
AMB_MUNDO = (0.16, 0.22, 0.18)
# la roca de los pinchos y el jade de los fragmentos, con su color: menos lima
LUCES_PIEDRA = [
    (hacia(-0.6, 0.6, -0.5), (1.0, 0.86, 0.66), 0.95, 'llave'),
    (hacia(0.55, 0.75, 0.6), (0.72, 1.0, 0.45), 0.75, 'contra'),
]
AMB_PIEDRA = (0.2, 0.19, 0.16)
LUCES_JADE = [
    (hacia(-0.5, 0.6, -0.6), (0.85, 1.0, 0.85), 0.5, 'llave'),
    (hacia(0.5, 0.7, 0.6), (0.6, 1.0, 0.4), 0.8, 'contra'),
]
AMB_JADE = (0.14, 0.22, 0.16)


class Niebla:
    """La bruma verde de la selva de noche."""
    color = (0.1, 0.2, 0.15)

    def __init__(self, ini=16.0, largo=40.0, tope=0.9):
        self.ini, self.largo, self.tope = ini, largo, tope

    def __call__(self, z):
        return np.clip((z - self.ini) / self.largo, 0, self.tope)


def sumar(base, capa, k=1.0):
    f = np.array(base).astype(float)
    f[..., :3] = np.clip(f[..., :3] + np.array(capa).astype(float)[..., :3] * k, 0, 255)
    return Image.fromarray(f.astype(np.uint8))


def sprite(nombre, ancho, alto=None):
    return Image.open(os.path.join(P, nombre)).convert('RGBA').resize((max(1, ancho), max(1, alto or ancho)), Image.NEAREST)


def pantalla(p):
    """Del mundo al poster: (x, y) en pixeles de la imagen final y la profundidad."""
    sx, sy, z = CAM.proyectar(np.asarray(p, float))
    return sx / SS, sy / SS, z


def tam_px(bloques, prof):
    """Cuantos pixeles del poster mide algo de 'bloques' a 'prof' de la camara."""
    return max(2, int(bloques * CAM.foco / SS / max(prof, 0.5)))


def en_suelo(sx, sy):
    """El punto del suelo (y=0) que cae en (sx, sy) del poster (medido en 1920x1080)."""
    d = desproyectar(sx, sy, 1.0) - CAM.ojo
    return CAM.ojo + d * (-CAM.ojo[1] / d[1])


def desproyectar(sx, sy, prof):
    """El punto del mundo que cae en (sx, sy) del poster (medido en 1920x1080) a "prof" bloques de la camara."""
    x = (sx * ESCALA * SS - CAM.W / 2) * prof / CAM.foco
    y = (CAM.H / 2 - sy * ESCALA * SS) * prof / CAM.foco
    return CAM.ojo + CAM.f * prof + CAM.r * x + CAM.u * y


def a_imagen(arr):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return im.resize((W, H), Image.LANCZOS)


def flotante(im):
    return np.array(im).astype(float) / 255.0


def textura(nombre):
    return vr.cargar(os.path.join(ENT, nombre + '.png'))


TEX_ROCA, TEX_VETAS = textura('roca'), textura('roca_brillo')
TEX_JADE, TEX_JADE_BRILLO = textura('fragmento'), textura('fragmento_brillo')
TEX_LLAMA = textura('llama')


def _estela_llama():
    """La llama de la estela con el apagado de la cabeza a la cola que el juego
    pone en los vertices (alfa 230 en la cabeza, 0 en la cola)."""
    t = TEX_LLAMA.astype(float).copy()
    v = np.linspace(0, 1, t.shape[0])[:, None]
    t[..., 3] *= 230 / 255 * (1 - v)
    return t.astype(np.uint8)


TEX_ESTELA = _estela_llama()


def _vetas_jade():
    """Solo las vetas claras del brillo del fragmento: de cerca, el que viene
    de frente se ve como jade con las vetas encendidas, no como un bloque de luz."""
    t = TEX_JADE_BRILLO.copy()
    lum = t[..., :3].astype(float).mean(axis=2)
    t[..., 3] = np.where(lum > np.percentile(lum, 80), 255, 0)
    return t


TEX_JADE_VETAS = _vetas_jade()


# ----------------------------------------------------------------------
#  Geometria de las piezas, como RajangDibujo.java (bloques de roca torcidos
#  y pinchos escalonados) y FragmentoJadeRenderer (el terron de jade)
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
    girado (grados x, y, z); la textura a 'densidad' pixeles por bloque."""
    v = []
    for i in range(8):
        sx, sy, sz = (1 if i & 1 else -1), (1 if i & 2 else -1), (1 if i & 4 else -1)
        q = np.array([sx * hx * (1 + (r.random() - 0.5) * mover), sy * hy * (1 + (r.random() - 0.5) * mover),
                      sz * hz * (1 + (r.random() - 0.5) * mover)])
        q = _yrot(_xrot(_zrot(q, math.radians(gz)), math.radians(gx)), math.radians(gy))
        v.append(q + np.array([x, y, z]))
    lados = ((hz, hy), (hz, hy), (hx, hy), (hx, hy), (hz, hx), (hx, hz))
    for k, c in enumerate(CARAS_CAJA):
        du = min(1.0, 2 * lados[k][0] * densidad / tw)
        dv = min(1.0, 2 * lados[k][1] * densidad / th)
        u0, v0 = r.random() * (1 - du), r.random() * (1 - dv)
        out.append(([v[c[0]], v[c[1]], v[c[2]], v[c[3]]], [(u0, v0 + dv), (u0 + du, v0 + dv), (u0 + du, v0), (u0, v0)]))


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


def pico_tierra(x, z, tam, rumbo, semilla):
    """Un golpe de pinchos de la Garra como PicoTierraRenderer: el grande, los
    menores abiertos alrededor y los terrones del suelo roto (en el mundo)."""
    r = random.Random(semilla)
    caras = []
    alto = 6.0 * tam
    ancho = 0.5 + 1.25 * tam
    pincho(caras, r, 0, 0, alto, ancho, 16 + r.random() * 10, (r.random() - 0.5) * 12)
    if tam > 0.25:
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
    M = vr.T(x, 0, z) @ vr.Ry(math.radians(-rumbo))
    return [([(M @ np.array([*p, 1.0]))[:3] for p in pts], uvs) for pts, uvs in caras]


def racimo(semilla):
    """El terron de jade del Cataclismo (FragmentoJadeRenderer.racimo): el
    nucleo de dos bloques cruzados, sus puntas, la llama que lo envuelve y los
    terrones del crater. En unidades del fragmento (tam 1)."""
    r = random.Random(semilla)
    jade, aura, crater = [], [], []
    n = 0.75 + r.random() * 0.1
    bloque(jade, r, 0, 0, 0, n, n * (0.85 + r.random() * 0.2), n, 0.18, r.random() * 30, r.random() * 90, r.random() * 30, 16, 32, 32)
    bloque(jade, r, n * 0.3, n * 0.2, -n * 0.2, n * 0.8, n * 0.7, n * 0.8, 0.18, 30 + r.random() * 30, 45 + r.random() * 30,
           r.random() * 30, 16, 32, 32)
    puntas = 3 + r.randrange(2)
    for k in range(puntas):
        theta = math.acos(1 - 2 * (k + r.random() * 0.6) / puntas)
        phi = r.random() * TAU
        largo = 0.5 + r.random() * 0.45
        grueso = 0.22 + r.random() * 0.1
        d = np.array([math.sin(theta) * math.sin(phi), math.cos(theta), math.sin(theta) * math.cos(phi)])
        c = d * (n * 0.7 + largo / 2)
        bloque(jade, r, *c, grueso, largo / 2, grueso, 0.1, -math.degrees(theta), math.degrees(phi), 0, 16, 32, 32)
        t = d * (n * 0.7 + largo + 0.12)
        bloque(jade, r, *t, grueso * 0.5, 0.16, grueso * 0.5, 0.1, -math.degrees(theta), math.degrees(phi), 0, 16, 32, 32)
    a = n * 1.3
    bloque(aura, r, 0, 0, 0, a, a, a, 0.25, r.random() * 45, r.random() * 45, 0, 8, 16, 32)
    for k in range(8):
        ang = TAU * k / 8 + r.random() * 0.5
        d = 1.0 + r.random() * 0.9
        t = 0.22 + r.random() * 0.22
        bloque(crater, r, math.cos(ang) * d, t * 0.3, math.sin(ang) * d, t, t * 0.7, t * (0.8 + r.random() * 0.3), 0.2,
               15 + r.random() * 30, math.degrees(-ang), (r.random() - 0.5) * 30, 12, 32, 64)
    return jade, aura, crater


def mover(caras, M):
    return [([(M @ np.array([*p, 1.0]))[:3] for p in pts], uvs) for pts, uvs in caras]


def pintar(lz, caras, tex, emis, brillo=1.0, niebla=None, luces=None, amb=None, plano=False):
    """Caras opacas con su textura y su capa de brillo, iluminadas."""
    for pts, uvs in caras:
        luz = np.ones(3) if plano else vr.iluminar(vr.normal(pts), CAM, np.mean(pts, axis=0), luces or LUCES, amb or AMBIENTE)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [pts[i] for i in tri], [uvs[i] for i in tri], tex, luz, emis, niebla, brillo=brillo)


def sumar_caras(lz, caras, tex, brillo):
    """Caras que solo brillan (la llama): se suman a la capa de luz."""
    for pts, uvs in caras:
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [pts[i] for i in tri], [uvs[i] for i in tri], tex, np.ones(3), None, None, aditivo=True,
                         brillo=brillo)


# ----------------------------------------------------------------------
#  El Cataclismo: la grieta del cielo y los fragmentos que caen de ella. La
#  grieta esta en el punto de fuga de su caida: todas las estelas salen de
#  ella, y los fragmentos mas cercanos vienen hacia quien mira.
# ----------------------------------------------------------------------
GRIETA = (float(os.environ.get('GRIETA_X', '1560')), float(os.environ.get('GRIETA_Y', '-40')))


def caida():
    """La direccion en que caen los fragmentos (desde la grieta)."""
    d = desproyectar(*GRIETA, 1.0) - CAM.ojo
    return -d / np.linalg.norm(d)


# Los fragmentos que caen: (x, y del poster, profundidad, tam, semilla)
FRAGMENTOS = [
    (430, 170, 129.0, 1.5, 3), (760, 300, 93.0, 1.4, 5), (930, 110, 145.0, 1.3, 8), (1830, 470, 80.5, 1.5, 11),
    (250, 420, 113.0, 1.2, 13), (1340, 210, 121.0, 1.3, 17),
    (640, 60, 191.0, 1.2, 23), (300, 300, 181.0, 1.1, 29), (1010, 230, 201.0, 1.2, 31),
]
# El que viene hacia quien mira: (x, y del poster, profundidad, tam, semilla)
ESTRELLA = (float(os.environ.get('EST_X', '1720')), float(os.environ.get('EST_Y', '820')), 10.5, 0.55, 21)
LARGO_ESTRELLA = 16.0


def fragmento(lz, p, d, tam, semilla, giro, largo=12.0, brillo_estela=0.9, aura=0.22, cabeza=0.4, ancho=1.5, brillo=0.9,
              vetas=TEX_JADE_BRILLO):
    """Un fragmento cayendo como FragmentoJadeRenderer: el terron que da
    vueltas, la llama que lo envuelve y la estela de tres cintas en abanico
    (que empieza 'cabeza' por delante de el; si viene de frente, por detras,
    para que no lo tape)."""
    jade, llama, _ = racimo(semilla)
    M = vr.T(*p) @ vr.Ry(giro[1]) @ vr.Rx(giro[0]) @ vr.Rz(giro[2]) @ vr.S(tam)
    pintar(lz, mover(jade, M), TEX_JADE, vetas, brillo=brillo, luces=LUCES_JADE, amb=AMB_JADE)
    if aura:
        sumar_caras(lz, mover(llama, M), TEX_LLAMA, aura)
    cabeza = p + d * cabeza * tam
    cola = p - d * largo * tam
    l0 = np.cross(d, [1.0, 0.0, 0.0])
    l0 /= np.linalg.norm(l0)
    m0 = np.cross(d, l0)
    ancho = ancho * tam
    for k in range(3):
        ang = math.pi * k / 3 + giro[1]
        l = l0 * math.cos(ang) + m0 * math.sin(ang)
        pts = [cabeza - l * ancho, cabeza + l * ancho, cola + l * ancho * 0.25, cola - l * ancho * 0.25]
        sumar_caras(lz, [(pts, [(0, 0), (1, 0), (1, 1), (0, 1)])], TEX_ESTELA, brillo_estela)


# ----------------------------------------------------------------------
#  Los aros de runas de la Piel de Jade (RajangEntity: runas de oro que le
#  dan vueltas). Aqui algo inclinados: por delante bajan a las patas y por
#  detras suben por encima del lomo.
# ----------------------------------------------------------------------
# (radio, altura en el centro, inclinacion (grados), giro del eje (grados))
AROS = [(7.6, 4.0, 15.0, 30.0), (6.4, 7.4, 20.0, 75.0)]
FRENTE_MAX = 4.6


def aro(centro, radio, alto, inclina, giro, n=200):
    """Los puntos del aro, en el mundo."""
    R = vr.Ry(math.radians(giro)) @ vr.Rx(math.radians(inclina))
    return [np.array([centro[0], alto, centro[2]]) + (R @ np.array([math.cos(a) * radio, 0.0, math.sin(a) * radio, 1.0]))[:3]
            for a in np.linspace(0, TAU, n, endpoint=False)]


# ----------------------------------------------------------------------
#  Fondo: cielo de tormenta, la grieta, los haces que salen de ella y la
#  selva lejana
# ----------------------------------------------------------------------
def ruido(w, h, celdas, semilla):
    g = np.random.default_rng(semilla).random((celdas[1] + 1, celdas[0] + 1))
    return flotante(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC))


def cielo(horiz):
    yy, xx = np.mgrid[0:H, 0:W]
    t = np.clip(yy / max(horiz, 1), 0, 1)
    arriba, abajo = np.array([0.015, 0.04, 0.05]), np.array([0.12, 0.22, 0.19])
    col = arriba + (abajo - arriba) * t[..., None] ** 1.4
    gx, gy = GRIETA[0] * ESCALA, GRIETA[1] * ESCALA
    dx, dy = (xx - gx) / W, (yy - gy) / W * 1.3
    d = np.hypot(dx, dy) + 1e-6
    ang = np.arctan2(dy, dx)
    # las nubes de la tormenta giran alrededor de la grieta, encendidas por ella
    n1 = ruido(W, H, (14, 8), 4) * 0.6 + ruido(W, H, (40, 22), 5) * 0.4
    remolino = 0.5 + 0.5 * np.sin(ang * 3 + np.log(d) * 6.0 + n1 * 3)
    nubes = np.clip(remolino * 0.6 + n1 * 0.7 - 0.45, 0, 1) * np.exp(-((d - 0.32) / 0.34) ** 2)
    col += nubes[..., None] * np.array([0.12, 0.24, 0.13]) * 0.8
    col += np.exp(-(d / 0.2) ** 2)[..., None] * np.array([0.3, 0.46, 0.1]) * 0.32
    col += np.exp(-(d / 0.6) ** 2)[..., None] * np.array([0.03, 0.08, 0.04])
    return col


def grieta_cielo():
    """La grieta que se abre en el cielo: una raja quebrada en bloques (como
    todo en el mod), con tramos rectos y quiebros secos y sus ramas, el nucleo
    casi blanco y el halo lima."""
    r = random.Random(7)
    k = max(1, px(6))                      # el tamano del bloque de la raja
    w, h = W // k + 1, H // k + 1
    capa = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(capa)
    gx, gy = GRIETA[0] * ESCALA / k, GRIETA[1] * ESCALA / k

    def rama(x, y, a, largo, grueso, prof):
        for s_ in range(int(largo)):
            quiebro = r.choice([-1, 1]) * r.uniform(0.35, 0.8) if s_ % 2 else 0.0
            paso = r.uniform(40, 80) * ESCALA / k
            x1, y1 = x + math.cos(a + quiebro) * paso, y + math.sin(a + quiebro) * paso
            g = max(1, int(round(grueso * (1 - s_ / (largo + 1)) ** 0.8)))
            d.line((x, y, x1, y1), fill=255, width=g)
            if prof < 1 and r.random() < 0.45:
                rama(x1, y1, a + r.choice([-1, 1]) * r.uniform(0.7, 1.2), max(2, largo * 0.4), grueso * 0.5, prof + 1)
            x, y = x1, y1
    for a, largo in ((math.pi * 0.95, 8), (0.08, 5), (math.pi * 0.6, 3)):
        rama(gx, gy + 40 * ESCALA / k, a, largo, 3.4, 0)
    capa = capa.resize((w * k, h * k), Image.NEAREST).crop((0, 0, W, H))
    g = flotante(capa)
    halo = flotante(capa.filter(ImageFilter.GaussianBlur(px(12))))
    lejos = flotante(capa.filter(ImageFilter.GaussianBlur(px(50))))
    return (g[..., None] * np.array([0.86, 1.0, 0.5]) + halo[..., None] * np.array([0.5, 0.95, 0.25]) * 0.7
            + lejos[..., None] * np.array([0.3, 0.62, 0.16]) * 0.5)


def haces(n=16, semilla=3):
    """Haces de luz que bajan de la grieta abriendose en abanico."""
    r = random.Random(semilla)
    capa = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(capa)
    gx, gy = GRIETA[0] * ESCALA, GRIETA[1] * ESCALA
    for _ in range(n):
        a = r.uniform(math.pi * 0.5, math.pi * 0.97)
        abre = r.uniform(0.015, 0.045)
        L = W * 1.6
        d.polygon([(gx, gy), (gx + math.cos(a - abre) * L, gy + math.sin(a - abre) * L),
                   (gx + math.cos(a + abre) * L, gy + math.sin(a + abre) * L)], fill=r.randint(26, 70))
    capa = flotante(capa.filter(ImageFilter.GaussianBlur(px(24))))
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.hypot(xx - gx, yy - gy) / W
    return capa * np.exp(-dd * 1.0)


def selva_lejana(horiz, semilla=12):
    """Las copas de la selva en el horizonte, en bloques: tres capas que se
    oscurecen hacia delante. Devuelve [(mascara, tono)] de atras a delante."""
    r = random.Random(semilla)
    capas = []
    for k, (alto, bloque_, tono) in enumerate(((px(190), px(22), 0.95), (px(130), px(30), 0.75), (px(80), px(40), 0.55))):
        m = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(m)
        x = -px(40)
        while x < W:
            ancho = r.randint(4, 9) * bloque_
            cima = horiz - alto * r.uniform(0.4, 1.0)
            # la copa: bloques que se ensanchan hacia abajo, como un arbol de hojas en bloque
            for j in range(4):
                w_ = ancho * (0.45 + 0.18 * j) * r.uniform(0.85, 1.1)
                xx_ = x + (ancho - w_) / 2 + r.uniform(-1, 1) * bloque_ * 0.5
                yy_ = cima + j * bloque_ * 0.9
                d.rectangle((xx_, min(yy_, horiz), xx_ + w_, horiz + px(20)), fill=255)
            x += ancho * r.uniform(0.55, 0.95)
        capas.append((flotante(m.filter(ImageFilter.GaussianBlur(max(1, px(2))))), tono))
    return capas


# ----------------------------------------------------------------------
#  La barra de jefe
# ----------------------------------------------------------------------
def barra_jefe(escala, vida=0.2, rastro=0.235):
    """La barra de jefe de Rajang, compuesta igual que en RajangBarraHud: la
    energia de la tierra del color de la fase, el rastro claro del ultimo
    golpe, los tres colmillos (rotos en la fase IV), el sol de la fase y los
    rotulos."""
    def tex(n):
        return Image.open(os.path.join(GUI, n + '.png')).convert('RGBA')

    def tenir(im, rgb):
        a = np.array(im).astype(float)
        a[..., :3] *= np.array(rgb)[None, None] / 255.0
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    color = (0xE6, 0xFF, 0x4A)
    lienzo = Image.new('RGBA', (208, 26 + 7), (0, 0, 0, 0))
    y0 = 7
    lienzo.alpha_composite(tex('rajang_barra_marco'), (0, y0))
    lleno, hasta = round(172 * vida), round(172 * rastro)
    if hasta > lleno:
        ImageDraw.Draw(lienzo).rectangle((28 + lleno, y0 + 9, 28 + hasta - 1, y0 + 9 + 7), fill=(0xF0, 0xFF, 0xE0, 0xD8))
    relleno = tenir(tex('rajang_barra_relleno'), color)
    for x in range(0, lleno, 64):
        lienzo.alpha_composite(relleno.crop((0, 0, min(64, lleno - x), 8)), (28 + x, y0 + 9))
    for corte in (0.75, 0.5, 0.25):
        nombre = 'rajang_barra_muesca_rota' if vida < corte else 'rajang_barra_muesca'
        lienzo.alpha_composite(tex(nombre), (28 + round(172 * corte) - 3, y0 + 9 - 2))
    lienzo.alpha_composite(tex(f'rajang_barra_sol_{FASE}'), (13 - 8, y0 + 13 - 8))
    lienzo.alpha_composite(tex('rajang_barra_nombre'), (28, y0 + 7 - 10))
    lienzo.alpha_composite(tenir(tex(f'rajang_barra_fase_{FASE}'), color), (28 + 172 - 64 + 1, y0 + 7 - 10))
    return lienzo.resize((lienzo.width * escala, lienzo.height * escala), Image.NEAREST)


# ----------------------------------------------------------------------
#  Composicion (todo medido en el poster de 1920x1080)
# ----------------------------------------------------------------------
# La fila de pinchos de la Garra: sale de la zarpa adelantada y se aleja
# hacia la izquierda, cada uno mas grande. (x, y del pie en el poster, tam)
PINCHOS = [(1060, 1010, 0.36), (950, 990, 0.5), (845, 976, 0.66), (745, 966, 0.85)]
# Pinchos sueltos junto a sus patas y por detras de el
PINCHOS_DETRAS = [(1150, 1062, 0.26), (1480, 975, 0.7), (1760, 968, 0.6)]
# Crateres con su fragmento clavado: (x, y del poster, semilla)
CRATERES = [(560, 962, 31), (1500, 958, 33)]


def main():
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(28.0, 89.0, 0.93)
    r = random.Random(9)

    # el suelo: la plaza del templo y la selva alrededor
    ts.dibujar_mundo(lz, CAM, ts.plaza(26, 195, 70), niebla, 1, LUCES_MUNDO, AMB_MUNDO)
    # las grietas de la maldicion en el suelo, desde sus zarpas (lo oscuro)
    rx, rz = RAJANG_EN[0], RAJANG_EN[2]
    grietas = []
    for k in range(7):
        a = TAU * k / 7 + r.uniform(-0.25, 0.25)
        d1 = r.uniform(9, 16)
        grietas.append((rx + math.cos(a) * 2.5, rz + math.sin(a) * 2.5, rx + math.cos(a) * d1, rz + math.sin(a) * d1,
                        r.uniform(0.45, 0.75), 60 + k))
    zarpa = en_suelo(1180, 1030)
    fin = en_suelo(*PINCHOS[-1][:2])
    grietas.append((zarpa[0], zarpa[2], fin[0] - 1.0, fin[2], 0.9, 77))
    for g in grietas:
        ta.grieta(lz, CAM, *g[:5], semilla=g[5], parte='oscura', luz=np.array([0.5, 0.55, 0.5]))

    # Rajang: la malla del juego con su atlas y su capa de brillo de la fase IV
    uv, alto_atlas = rj.empaquetar()
    tex = textura(f'rajang_f{FASE}')
    brillo = textura(f'rajang_brillo_f{FASE}')
    pose = pose_poster()
    M = vr.entidad_a_mundo(*RAJANG_EN, GUINADA)
    cuerpo = rj.quads(pose, uv, alto_atlas, M)
    for Pq, UVq, _, mat in cuerpo:
        luz = vr.iluminar(vr.normal(Pq), CAM, np.mean(Pq, axis=0), LUCES, AMBIENTE)
        # los cristales, a media luz: si no, la cresta entera se quema en blanco
        k_brillo = 0.45 if mat == 'cristal' else 1.0
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, luz, brillo, None, brillo=k_brillo)

    def punto(pieza, local=(0, 0, 0)):
        return (M @ np.array([*rj.punto(pose, pieza, local), 1.0]))[:3]
    pecho = punto('sol', (0, 3, -118.5))
    boca = punto('cabeza', (0, 6, -54))
    ojos = [punto('ojo_izq'), punto('ojo_der')]
    centro = punto('cuerpo', (0, 0, -40))
    cara = pantalla(punto('cabeza', (0, -2, -40)))
    cresta = [punto(f'cresta{i}_a', (0, -30, 0)) for i in range(8)]

    # la silueta de Rajang: lo que pasa por detras se recorta con ella
    solo = Lienzo(W * SS, H * SS)
    for Pq, UVq, _, _ in cuerpo:
        for tri in ((0, 1, 2), (0, 2, 3)):
            solo.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, np.ones(3))
    figura = flotante(a_imagen(solo.alfa))

    # los pinchos de la Garra, que salen de la zarpa adelantada, y otros detras
    piedras = []
    for i, (sx, sy, tam) in enumerate(PINCHOS + PINCHOS_DETRAS):
        q = en_suelo(sx, sy)
        piedras += pico_tierra(q[0], q[2], tam, GUINADA + 30 + r.uniform(-30, 30), 100 + i)
    # los crateres de los fragmentos que ya cayeron, con el terron clavado
    clavados = []
    for sx, sy, sem in CRATERES:
        q = en_suelo(sx, sy)
        jade, _, crater = racimo(sem)
        piedras += mover(crater, vr.T(*q) @ vr.S(1.4))
        clavados += mover(jade, vr.T(q[0], 0.4, q[2]) @ vr.Ry(r.uniform(0, TAU)) @ vr.Rx(0.5) @ vr.S(1.4))
    pintar(lz, piedras, TEX_ROCA, TEX_VETAS, brillo=1.5, niebla=Niebla(40.0, 100.0, 0.6), luces=LUCES_PIEDRA, amb=AMB_PIEDRA)
    pintar(lz, clavados, TEX_JADE, TEX_JADE_BRILLO, brillo=1.0, niebla=niebla, luces=LUCES_JADE, amb=AMB_JADE)

    # los fragmentos que caen de la grieta y el que viene de frente
    d = caida()
    for sx, sy, prof, tam, sem in FRAGMENTOS:
        fragmento(lz, desproyectar(sx, sy, prof), d, tam, sem, (r.uniform(0, TAU), r.uniform(0, TAU), r.uniform(0, TAU)))
    ex, ey, eprof, etam, esem = ESTRELLA
    estrella = desproyectar(ex, ey, eprof)
    fragmento(lz, estrella, d, etam, esem, (0.6, 2.2, 0.3), largo=LARGO_ESTRELLA, brillo_estela=0.5, aura=0.0, cabeza=-0.9,
              ancho=0.6, brillo=1.0, vetas=TEX_JADE_VETAS)

    # lo que brilla en el suelo, encima de todo lo opaco
    for g in grietas:
        ta.grieta(lz, CAM, *g[:5], semilla=g[5], brillo=1.0, parte='brillo')
    for sx, sy, _ in CRATERES:
        q = en_suelo(sx, sy)
        ta.calco(lz, CAM, q[0], q[2], 3.6, ta.ONDA, 0.45)
        ta.cartel(lz, CAM, (q[0], 1.0, q[2]), 2.0, ta.HALO, 0.55)

    # --- a resolucion final ---
    color = flotante(a_imagen(lz.color))
    alfa = flotante(a_imagen(lz.alfa))[..., None]
    emis = a_imagen(lz.emis)

    lejos = np.array([CAM.ojo[0] + CAM.f[0] * 400, 0.0, CAM.ojo[2] + CAM.f[2] * 400])
    horiz = CAM.proyectar(lejos)[1] / SS
    fondo = cielo(horiz)
    fondo += grieta_cielo()
    fondo += haces()[..., None] * np.array([0.55, 0.85, 0.35]) * 0.9
    # la selva lejana, recortada contra el cielo
    for m, tono in selva_lejana(horiz):
        fondo = fondo * (1 - m[..., None]) + m[..., None] * np.array(Niebla.color) * tono
    yy, xx = np.mgrid[0:H, 0:W]
    # el sol del pecho tine el aire detras de el
    cx, cy, _ = pantalla(pecho)
    dd = np.hypot((xx - cx) / (W * 0.25), (yy - cy) / (H * 0.38))
    fondo += np.array([0.28, 0.4, 0.06])[None, None] * np.exp(-dd ** 2 * 1.4)[..., None] * 0.3
    # el contraluz: el aire brilla justo detras de su silueta
    halo = flotante(Image.fromarray((figura * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(px(46))))
    fondo += halo[..., None] * np.array([0.22, 0.4, 0.12]) * 0.55
    fondo_img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

    f = flotante(fondo_img)[..., :3]
    f = color * alfa + f * (1 - alfa)
    # bruma baja que corre por la plaza
    bruma = np.exp(-((yy - horiz + px(10)) / px(60)) ** 2) * (0.55 + 0.45 * ruido(W, H, (24, 6), 6))
    f += np.array([0.14, 0.24, 0.17])[None, None] * bruma[..., None] * 0.7 * (1 - figura[..., None])
    img = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

    e = emis.convert('RGB')
    for radio, k in ((px(5), 0.8), (px(18), 0.6), (px(60), 0.45)):
        img = sumar(img, e.filter(ImageFilter.GaussianBlur(radio)), k)
    img = sumar(img, e, 0.6).convert('RGBA')

    # contraluces: el borde que mira a la grieta, en lima; el de la izquierda, en jade
    f = np.array(img).astype(float)
    for (dx_, dy_), rgb, k in (((1, -1), (210, 255, 120), 0.8), ((-1, 0), (90, 230, 160), 0.5)):
        n_ = max(1, px(3))
        vecino = np.roll(figura, (-dy_ * n_, -dx_ * n_), axis=(0, 1))
        borde = np.clip(figura - vecino, 0, 1)
        borde = flotante(Image.fromarray((borde * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(1, px(1.5)))))
        f[..., :3] += borde[..., None] * np.array(rgb) * k
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))

    # --- particulas propias, en 2D ---
    _, cintura, _ = pantalla((RAJANG_EN[0], FRENTE_MAX, RAJANG_EN[2]))
    arriba = np.clip((cintura + px(40) - yy) / px(80), 0, 1)
    zbuf = np.array(Image.fromarray(np.minimum(solo.z, 1e4).astype(np.float32)).resize((W, H), Image.NEAREST))

    def detras(p, holgura=0.0):
        sx, sy, z = pantalla(p)
        ix, iy = int(min(W - 1, max(0, sx))), int(min(H - 1, max(0, sy)))
        return z > zbuf[iy, ix] + holgura

    # los ojos encendidos: un destello donde se ven
    luz_ojos = np.zeros((H, W))
    for o in ojos:
        if detras(o, 0.4):
            continue
        ox, oy, _ = pantalla(o)
        luz_ojos += np.exp(-((xx - ox) ** 2 + (yy - oy) ** 2) / (2 * px(9) ** 2))
    img = sumar(img, Image.fromarray((np.clip(luz_ojos[..., None] * np.array([255, 255, 200]), 0, 255)).astype(np.uint8)), 1.0)
    img = sumar(img, Image.fromarray((np.clip(luz_ojos[..., None] * np.array([200, 255, 90]), 0, 255)).astype(np.uint8))
                .filter(ImageFilter.GaussianBlur(px(14))), 1.2).convert('RGBA')

    # el fragmento que viene de frente: la llama verde que lo envuelve y la
    # estela, lenguas de fuego que se alejan hacia la grieta. Cada pixel de la
    # estela sabe a que profundidad esta: donde pasa por detras de Rajang, se
    # esconde.
    zfull = np.array(Image.fromarray(np.minimum(lz.z, 1e4).astype(np.float32)).resize((W, H), Image.NEAREST))
    gx_, gy_, gz_ = pantalla(estrella)
    rad = tam_px(1.1 * etam, gz_)
    s_ = np.linspace(0, 1, 40)
    traza = np.array([pantalla(estrella - d * etam * LARGO_ESTRELLA * k) for k in s_])
    u = traza[-1, :2] - traza[0, :2]
    largo = np.linalg.norm(u)
    u /= largo
    perp = np.array([-u[1], u[0]])
    c0 = np.array([gx_, gy_])
    m = Image.new('L', (W, H), 0)
    dm = ImageDraw.Draw(m)
    rf = random.Random(4)
    for k in range(11):
        giro_ = rf.uniform(-0.09, 0.09)
        dk = u * math.cos(giro_) + perp * math.sin(giro_)
        pk = np.array([-dk[1], dk[0]])
        ok = perp * rf.uniform(-0.45, 0.45) * rad
        wk = rad * rf.uniform(0.25, 0.55)
        dm.polygon([tuple(c0 + ok + pk * wk), tuple(c0 + ok + dk * largo * rf.uniform(0.4, 1.0)), tuple(c0 + ok - pk * wk)],
                   fill=rf.randint(90, 170))
    dm.ellipse((gx_ - rad * 1.25, gy_ - rad * 1.25, gx_ + rad * 1.25, gy_ + rad * 1.25), fill=120)
    dm.ellipse((gx_ - rad * 0.75, gy_ - rad * 0.75, gx_ + rad * 0.75, gy_ + rad * 0.75), fill=20)    # el terron se ve dentro
    llamarada = flotante(m.filter(ImageFilter.GaussianBlur(max(1, rad * 0.16))))
    t = np.clip(((xx - gx_) * u[0] + (yy - gy_) * u[1]) / largo, 0, 1)
    llamarada *= (1 - t) ** 1.2
    prof_estela = np.interp(t, np.linalg.norm(traza[:, :2] - c0, axis=1) / largo, traza[:, 2])
    llamarada *= np.clip((zfull - prof_estela) / 0.6, 0, 1)
    cerca = np.clip(1 - t * 3, 0, 1)[..., None]
    tono = np.array([70, 225, 90]) * (1 - cerca) + np.array([215, 255, 170]) * cerca
    img = sumar(img, Image.fromarray(np.clip(llamarada[..., None] * tono * 1.1, 0, 255).astype(np.uint8)), 1.0)
    img = sumar(img, Image.fromarray(np.clip(llamarada[..., None] * tono, 0, 255).astype(np.uint8))
                .filter(ImageFilter.GaussianBlur(px(30))), 0.8).convert('RGBA')

    tras = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    frente = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # los aros de runas: la estela de oro y las runas que la arrastran
    for k, (radio, alto_, inclina, giro) in enumerate(AROS):
        pts = aro(centro, radio, alto_, inclina, giro)
        n = len(pts)
        dl = (ImageDraw.Draw(tras), ImageDraw.Draw(frente))
        for i in range(n):
            p0, p1 = pts[i], pts[(i + 1) % n]
            (ax_, ay_, az_), (bx_, by_, bz_) = pantalla(p0), pantalla(p1)
            if min(az_, bz_) < 3.0 or min(ay_, by_) < px(150):
                continue
            fase_ = (i / n * 8 + k * 0.4) % 1.0           # tramos de estela que se apagan hacia atras
            al = int(240 * fase_ ** 1.6)
            if al < 8:
                continue
            delante = not detras(p0) and p0[1] <= FRENTE_MAX
            dl[1 if delante else 0].line([(ax_, ay_), (bx_, by_)], fill=(255, 216, 112, al), width=tam_px(0.15, az_))
        for j in range(8):
            p = pts[int((j + 0.97) * n / 8 + k * 0.4 * n / 8) % n]
            sx, sy, z = pantalla(p)
            if z < 3.0 or sy < px(170) or math.hypot(sx - cara[0], sy - cara[1]) < px(300):
                continue
            s = sprite(f'rajang_runa_{(j + k) % 3}.png', tam_px(0.6, z))
            delante = not detras(p) and p[1] <= FRENTE_MAX
            (frente if delante else tras).alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))

    # por detras se recortan con su silueta; por delante, nada le tapa la cara ni el pecho
    deja = 1 - figura * arriba
    tras.putalpha(Image.fromarray((np.array(tras.getchannel('A')).astype(float) * (1 - figura)).astype(np.uint8)))
    frente.putalpha(Image.fromarray((np.array(frente.getchannel('A')).astype(float) * deja).astype(np.uint8)))
    for capa_ in (tras, frente):
        img.alpha_composite(capa_.filter(ImageFilter.GaussianBlur(px(6))))
        img.alpha_composite(capa_)

    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    bx_, by_, bz_ = pantalla(boca)
    for _ in range(9):                            # el aliento verde que se le escapa entre los sables
        s = sprite(f'rajang_chispa_{r.randint(0, 2)}.png', tam_px(r.choice([0.14, 0.2, 0.26]), bz_))
        capa.alpha_composite(s, (int(bx_ + r.uniform(-px(90), px(70)) - s.width / 2), int(by_ + r.uniform(px(60), px(260)))))
    puestas = 0
    while puestas < 40:                           # chispas y oro que suben de la cresta y las grietas
        c = cresta[r.randrange(len(cresta))]
        p = c + np.array([r.uniform(-2.5, 2.5), r.uniform(0.5, 6.0), r.uniform(-2.5, 2.5)])
        sx, sy, z = pantalla(p)
        if not (0 <= sx < W and 0 <= sy < H) or (figura[int(sy), int(sx)] > 0.1 and sy > cintura - px(300)):
            continue
        nombre = f'rajang_oro_{r.randint(0, 2)}.png' if r.random() < 0.4 else f'rajang_chispa_{r.randint(0, 2)}.png'
        s = sprite(nombre, tam_px(r.choice([0.25, 0.32, 0.4]), z))
        capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
        puestas += 1
    # la estela de llama que deja el fragmento que viene de frente
    for k in range(12):
        t = r.uniform(0.2, 1.0)
        q = estrella - d * etam * 12.0 * t ** 1.5 + np.array([r.gauss(0, 0.45), r.gauss(0, 0.45), r.gauss(0, 0.45)]) * etam
        sx, sy, z = pantalla(q)
        if z < 2.0 or detras(q):
            continue
        nombre = f'rajang_llama_{r.randint(0, 2)}.png' if k % 3 else f'rajang_jade_{r.randint(0, 2)}.png'
        s = sprite(nombre, tam_px(r.choice([0.25, 0.35, 0.45]), z))
        capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
    # polvo y terrones que saltan al reventar los pinchos
    for sx0, sy0, tam in PINCHOS:
        q0 = en_suelo(sx0, sy0)
        _, _, z0 = pantalla(q0)
        for _ in range(3):
            q = q0 + np.array([r.uniform(-1.6, 1.6), r.uniform(0.1, 0.6), r.uniform(-1.6, 1.6)]) * (0.6 + tam)
            sx, sy, z = pantalla(q)
            s = sprite(f'rajang_polvo_{r.randint(0, 2)}.png', tam_px(r.choice([0.5, 0.65, 0.8]) * (0.6 + tam), z))
            s = s.filter(ImageFilter.GaussianBlur(max(1, s.width // 10)))
            s.putalpha(s.getchannel('A').point(lambda v: int(v * 0.4)))
            capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
        for _ in range(3):
            q = q0 + np.array([r.uniform(-1.4, 1.4), r.uniform(1.2, 6.0) * tam + 0.5, r.uniform(-1.4, 1.4)])
            sx, sy, z = pantalla(q)
            s = sprite(f'rajang_roca_{r.randint(0, 2)}.png', tam_px(r.choice([0.25, 0.32, 0.4]), z)).rotate(
                r.uniform(0, 360), expand=True)
            capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(px(5))))
    img.alpha_composite(capa)

    # hojas de la selva y esquirlas de jade en el aire, con profundidad: lejos
    # pequenas y nitidas, cerca grandes y desenfocadas
    for n_hojas, tams, desenfoque in ((34, (10, 13, 16), 0), (7, (34, 44, 54), 5)):
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        puestas = 0
        while puestas < n_hojas:
            hx, hy = int(r.uniform(px(820), W - px(30))), int(r.uniform(px(130), H - px(40)))
            if figura[min(H - 1, hy), min(W - 1, hx)] > 0.1:
                continue
            nombre = f'rajang_hoja_{r.randint(0, 2)}.png' if r.random() < 0.7 else f'rajang_jade_{r.randint(0, 2)}.png'
            s = sprite(nombre, px(r.choice(tams))).rotate(r.uniform(0, 360), expand=True)
            capa.alpha_composite(s, (hx - s.width // 2, hy - s.height // 2))
            puestas += 1
        if desenfoque:
            capa = capa.filter(ImageFilter.GaussianBlur(px(desenfoque)))
            capa.putalpha(capa.getchannel('A').point(lambda v: int(v * 0.75)))
        img.alpha_composite(capa)

    # el fragmento corta el aire: rayas que van de el hacia la grieta
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(capa)
    gx0, gy0 = GRIETA[0] * ESCALA, GRIETA[1] * ESCALA
    gx_, gy_, _ = pantalla(estrella)
    perp = np.array([-(gy_ - gy0), gx_ - gx0])
    perp /= np.linalg.norm(perp)
    for k in range(16):
        t = r.uniform(-1, 1)
        x0 = gx_ + perp[0] * t * px(150)
        y0 = gy_ + perp[1] * t * px(150)
        k1 = r.uniform(0.1, 0.3)
        dr.line([(x0, y0), (x0 + (gx0 - x0) * k1, y0 + (gy0 - y0) * k1)], fill=(200, 255, 170, r.randint(50, 120)),
                width=max(1, px(2)))
    capa.putalpha(Image.fromarray((np.array(capa.getchannel('A')).astype(float) * deja).astype(np.uint8)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(max(1, px(1)))))

    # --- grado y vineta ---
    f = np.array(img).astype(float) / 255.0
    vin = 1 - 0.6 * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.32, 0, 1) ** 1.4
    f[..., :3] *= vin[..., None]
    f[..., :3] = np.clip(f[..., :3] * np.array([0.98, 1.0, 0.97]) + np.random.default_rng(2).normal(0, 0.01, (H, W, 1)), 0, 1)
    img = Image.fromarray((f * 255).astype(np.uint8)).convert('RGBA')

    # --- el anuncio ---
    gr = np.zeros((H, W, 4), np.uint8)
    gr[..., :3] = (3, 12, 8)
    gr[..., 3] = (np.clip(1 - xx / (W * 0.5), 0, 1) ** 1.6 * 215).astype(np.uint8)
    img.alpha_composite(Image.fromarray(gr))
    d_ = ImageDraw.Draw(img)

    x0 = px(110)
    texto_espaciado(d_, (x0, px(300)), 'ATALAYA  ·  JEFE DE LA TIERRA', fuente('Montserrat-Bold.ttf', 22), JADE, px(5))
    brillo_texto(img, (x0 - px(6), px(320)), 'RAJANG', fuente('Oswald-Bold.ttf', 196), BLANCO, (60, 210, 110, 210), px(24))
    d_ = ImageDraw.Draw(img)
    d_.text((x0, px(562)), 'El Jaguar de Jade', font=fuente('Montserrat-SemiBoldItalic.ttf', 34), fill=(212, 232, 214, 255))
    d_.text((x0, px(608)), FRASE, font=fuente('Montserrat-Medium.ttf', 24), fill=GRIS)
    d_.rectangle((x0, px(656), x0 + px(90), px(661)), fill=ORO)

    # la barra de jefe, como en el juego, sobre el
    barra = barra_jefe(max(1, px(2)))
    img.alpha_composite(barra, (int(float(os.environ.get('BARRA_X', '1260')) * ESCALA) - barra.width // 2, px(36)))
    d_ = ImageDraw.Draw(img)

    fs = fuente('Oswald-Bold.ttf', 26)
    fp = fuente('Montserrat-Medium.ttf', 18)
    tw = d_.textlength('HARDCORE', font=fs)
    bx, by = W - px(110) - tw - px(36), px(60)
    d_.rectangle((bx, by, bx + tw + px(36), by + px(52)), outline=ORO, width=max(1, px(3)))
    d_.text((bx + px(18), by + px(6)), 'HARDCORE', font=fs, fill=ORO)
    d_.text((W - px(110) - d_.textlength('Minecraft 26.2 · Fabric', font=fp), H - px(70)),
            'Minecraft 26.2 · Fabric', font=fp, fill=(164, 190, 172, 255))
    img.convert('RGB').save(SALIDA)
    print('ok', W, H)


FRASE = 'Resiste el cataclismo. Arranca la raíz de su pecho.'


def texto_espaciado(d, xy, txt, f, color, sep):
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + sep
    return x


def brillo_texto(base, xy, txt, f, color, halo, radio):
    capa = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).text(xy, txt, font=f, fill=halo)
    capa = capa.filter(ImageFilter.GaussianBlur(radio))
    base.alpha_composite(capa)
    base.alpha_composite(capa)
    ImageDraw.Draw(base).text(xy, txt, font=f, fill=color)


main()

"""
Renders de la ficha de diseno del Caballero Solar (jefe del fuego): las tres
opciones, la escala junto a los jefes de antes, las fases y una escena por
ataque, en el Altar del Sol (una explanada de basalto con el sol de oro en el
suelo, braseros y su propio sol en el cielo).

Uso: python fuego_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import copy, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador de escala
import fuego_modelo as fm

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
FUENTE = 'C:/Windows/Fonts/'
SS = 2
TAU = math.tau

LUCES = [((-0.35, 1.0, -0.55), (1.0, 0.78, 0.5), 1.15, 'llave'),     # su sol, arriba y delante
         ((0.6, 0.35, 0.9), (1.0, 0.38, 0.14), 0.85, 'contra'),       # el horizonte que arde, detras
         ((-0.8, 0.1, 0.4), (0.9, 0.3, 0.1), 0.45, 'contra')]
AMB = (0.3, 0.17, 0.14)
LUZ_ESTUDIO = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (1.0, 0.65, 0.45), 0.5, 'contra')]
AMB_ESTUDIO = (0.36, 0.35, 0.35)
SOL = np.array([0.0, 46.0, 70.0])     # el Sol del Caballero, sobre el altar
V = 'N'                               # la variante de las escenas: Novilis (ronda 2)


def rgb(h):
    return tuple(c / 255 for c in nm._hex(h))


def color_fase(fase, cual=1):
    return nm._hex(fm.FASE[fase][cual])


# ----------------------------------------------------------------------
#  El lienzo: lo opaco que tapa algo le borra tambien el brillo (como en las
#  escenas de Rajang), para que el fuego de detras no se vea a traves
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
#  Materiales del altar
# ----------------------------------------------------------------------
def _loseta(semilla, rampa, pesos, juntas=False, vetas=None):
    r = random.Random(semilla)
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            b = r.choice(pesos)
            if vetas and vetas(x, y):
                b = min(4, b + 1)
            if juntas and (x == 0 or y == 0):
                b = max(0, b - 2)
            t[y, x] = (*rampa[b], 255)
    return t


def _magma(semilla, col=('ffd27a', 'ff7a1a', '8a2a0a')):
    """Como el bloque de magma: costra oscura y celdas encendidas (que brillan)."""
    r = random.Random(semilla)
    nuc, pri, hon = (nm._hex(c) for c in col)
    t = np.zeros((16, 16, 4), np.uint8)
    e = np.zeros((16, 16, 4), np.uint8)
    centros = [(r.uniform(0, 16), r.uniform(0, 16)) for _ in range(5)]
    for y in range(16):
        for x in range(16):
            d = sorted(min(abs(x - cx), 16 - abs(x - cx)) ** 2 + min(abs(y - cy), 16 - abs(y - cy)) ** 2 for cx, cy in centros)
            borde = math.sqrt(d[1]) - math.sqrt(d[0])
            if borde < 1.0:
                c = (40, 14, 10) if r.random() < 0.7 else (58, 20, 12)
                t[y, x] = (*c, 255)
            else:
                k = min(1.0, (borde - 1.0) / 3.0)
                c = fm._mezcla(hon, pri, k * 1.4) if k < 0.7 else fm._mezcla(pri, nuc, (k - 0.7) / 0.3)
                t[y, x] = (*c, 255)
                e[y, x] = (*c, int(140 + 115 * k))
    return t, e


BASALTO = nm._rampa('1e1a1c', '2a2427', '363033', '443d40', '554c4e')
NEGRA = nm._rampa('141012', '1c1719', '241e20', '2e2629', '3a3033')
TERRACOTA = nm._rampa('6a2c16', '7e361c', '904224', 'a24e2c', 'b45c36')
ARENA = nm._rampa('9a4a22', 'ac5628', 'bc622e', 'c87038', 'd48244')
MARMOL = nm._rampa('8c8070', 'a89c8a', 'c0b4a0', 'd4cab6', 'e6dece')
ORO_B = nm._rampa('8a5a14', 'b0761c', 'd09424', 'e8b23a', 'ffd86a')

fm.registrar('basalto', _loseta(31, BASALTO, (1, 2, 2, 2, 3), vetas=lambda x, y: x % 4 == 0))
fm.registrar('basalto_j', _loseta(32, BASALTO, (0, 1, 1, 2, 2), juntas=True))
fm.registrar('negra', _loseta(33, NEGRA, (0, 1, 2, 2, 3, 4)))
fm.registrar('terracota', _loseta(34, TERRACOTA, (1, 2, 2, 3, 3, 4)))
fm.registrar('arena_roja', _loseta(35, ARENA, (0, 1, 2, 2, 3, 4)))
fm.registrar('marmol', _loseta(36, MARMOL, (1, 2, 3, 3, 4)))
fm.registrar('marmol_osc', _loseta(37, MARMOL, (0, 1, 1, 2)))
fm.registrar('oro_bloque', _loseta(38, ORO_B, (2, 3, 3, 4), juntas=True))
_m, _me = _magma(39)
fm.registrar('magma', _m, _me)


def _sol_sup(fase, semilla=41):
    """La superficie de un sol: granulos claros y manchas mas hondas."""
    r = random.Random(semilla)
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            q = r.random()
            c = fm._mezcla(pri, nuc, 0.55) if q < 0.45 else pri if q < 0.85 else fm._mezcla(pri, hon, 0.6)
            t[y, x] = (*c, 255)
    return t


for _f in fm.FASE:
    _t, _e, _p = fm.materiales(_f)
    _t['sol_sup'] = _sol_sup(_f)
    _p.add('sol_sup')


# ----------------------------------------------------------------------
#  Texturas de los efectos (RGBA uint8)
# ----------------------------------------------------------------------
def _mez(a, b, t):
    return fm._mezcla(a, b, t)


def tex_disco(nuc, pri, n=128, duro=0.35, cola=2.2):
    """Un resplandor redondo: el nucleo casi blanco (con su tinte) y la corona que se apaga."""
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d = np.hypot(x - n / 2, y - n / 2) / (n / 2)
    t = np.zeros((n, n, 4), np.uint8)
    k = np.clip(1 - d, 0, 1)
    nucleo = d < duro
    for c in range(3):
        t[..., c] = np.where(nucleo, nuc[c], pri[c] * (0.6 + 0.4 * k) + (nuc[c] - pri[c]) * np.clip(1 - d / duro, 0, 1))
    t[..., 3] = np.clip(np.where(nucleo, 255, 255 * k ** cola * 1.3), 0, 255)
    return t


def tex_aro(color, n=256, grueso=0.05, relleno=0, marcas=0, color2=None):
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d = np.hypot(x - n / 2, y - n / 2) / (n / 2)
    a = np.arctan2(y - n / 2, x - n / 2)
    t = np.zeros((n, n, 4), np.uint8)
    if relleno:
        t[d < 1] = (*(color2 or color), relleno)
    t[(d > 1 - grueso) & (d < 1)] = (*color, 240)
    if marcas:
        m = (d > 0.86) & (d < 0.92) & (((a + math.pi) / TAU * marcas) % 1 < 0.45)
        t[m] = (*color, 210)
    return t


def tex_sello(color, n=256, rayos=12, relleno=60):
    """El sello del sol en el suelo (donde va a caer algo): aro doble, rayos y el disco."""
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d = np.hypot(x - n / 2, y - n / 2) / (n / 2)
    a = np.arctan2(y - n / 2, x - n / 2)
    claro = _mez(color, (255, 255, 255), 0.45)
    t = np.zeros((n, n, 4), np.uint8)
    t[d < 1] = (*color, relleno)
    t[(d > 0.93) & (d < 1)] = (*claro, 245)
    t[(d > 0.80) & (d < 0.84)] = (*color, 220)
    s = ((a + math.pi) / TAU * rayos) % 1
    rayo = (np.abs(s - 0.5) < 0.09 * (1 - d) + 0.02) & (d > 0.3) & (d < 0.78)
    t[rayo] = (*color, 200)
    t[(d > 0.2) & (d < 0.26)] = (*claro, 230)
    t[d < 0.16] = (*claro, 200)
    return t


def tex_llamas(nuc, pri, hon, w=64, h=64, semilla=1, densidad=1.0):
    """Una pared de llamas (vista de lado): lenguas que suben, el pie encendido."""
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    alturas = []
    for x in range(w):
        alturas.append(0.45 + 0.35 * abs(math.sin(x * 0.31 + r.random())) * densidad + r.uniform(-0.08, 0.08))
    for x in range(w):
        for y in range(h):
            v = 1 - y / (h - 1)                      # 0 abajo, 1 arriba
            alto = alturas[x]
            if v > alto:
                continue
            k = v / alto
            if k < 0.35:
                c = _mez(nuc, pri, k / 0.35)
            elif k < 0.75:
                c = _mez(pri, hon, (k - 0.35) / 0.4)
            else:
                c = _mez(hon, (60, 10, 6), (k - 0.75) / 0.25)
            a = int(255 * (1 - k ** 3))
            t[y, x] = (*c, a)
    return t


def tex_media_luna(nuc, pri, n=128):
    """El tajo de fuego que sale volando: una media luna con el filo encendido."""
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d1 = np.hypot(x - n / 2, y - n * 0.62) / (n * 0.46)
    d2 = np.hypot(x - n / 2, y - n * 0.82) / (n * 0.46)
    luna = (d1 < 1) & (d2 > 1)
    k = np.clip((d2 - 1) / 0.35, 0, 1)            # 0 en el filo de dentro, 1 en el lomo
    t = np.zeros((n, n, 4), np.uint8)
    for c in range(3):
        t[..., c] = np.where(luna, nuc[c] * (1 - k) + pri[c] * k, 0)
    t[..., 3] = np.where(luna, np.clip(255 * (1.15 - k * 0.6) * np.clip((1 - d1) / 0.12, 0, 1), 0, 255), 0)
    return t


def tex_haz(nuc, pri, w=32, h=8):
    """Un haz de luz (de lado a lado): el alma casi blanca y el color por fuera."""
    t = np.zeros((h, w, 4), np.uint8)
    for x in range(w):
        v = abs(x - (w - 1) / 2) / ((w - 1) / 2)
        if v < 0.3:
            c, a = nuc, 255
        else:
            k = (v - 0.3) / 0.7
            c, a = _mez(nuc, pri, k), int(240 * (1 - k ** 1.4))
        t[:, x] = (*c, a)
    return t


def tex_nota(color, n=32):
    """Una nota (corchea) de luz, para la melodia de las trompetas."""
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    claro = _mez(color, (255, 255, 255), 0.5)
    d.ellipse((4, 20, 15, 29), fill=(*claro, 255))
    d.rectangle((13, 4, 15, 24), fill=(*claro, 255))
    d.polygon([(15, 4), (26, 10), (26, 15), (15, 9)], fill=(*claro, 255))
    halo = im.filter(ImageFilter.GaussianBlur(2))
    a = np.array(halo).astype(float)
    a[..., :3] = color
    out = Image.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), im)
    return np.array(out)


def tex_plano(color, alfa=255):
    t = np.zeros((4, 4, 4), np.uint8)
    t[...] = (*color, alfa)
    return t


def tex_cupula(color, n=64):
    """La cupula de sol (no se le puede pegar): hexagonos de luz casi transparentes."""
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            q = (x / 8.0 + (y // 7) % 2 * 0.5) % 1.0
            borde = q < 0.12 or (y % 7) == 0
            t[y, x] = (*_mez(color, (255, 255, 255), 0.4 if borde else 0.0), 150 if borde else 40)
    return t


# ----------------------------------------------------------------------
#  Geometria de los efectos
# ----------------------------------------------------------------------
def billboard(p, tam, cam, giro=0.0, alto=None):
    p = np.array(p, float)
    c, s_ = math.cos(giro), math.sin(giro)
    rr, uu = cam.r * c + cam.u * s_, -cam.r * s_ + cam.u * c
    h = tam if alto is None else alto
    P = [p - rr * tam - uu * h, p + rr * tam - uu * h, p + rr * tam + uu * h, p - rr * tam + uu * h]
    return ([tuple(q) for q in P], [(0, 1), (1, 1), (1, 0), (0, 0)])


def suelo_cuad(cx, cz, R, y=0.06, giro=0.0):
    c, s_ = math.cos(giro) * R, math.sin(giro) * R
    P = [(cx - c + s_, y, cz - s_ - c), (cx + c + s_, y, cz + s_ - c), (cx + c - s_, y, cz + s_ + c),
         (cx - c - s_, y, cz - s_ + c)]
    return [(P, [(0, 0), (1, 0), (1, 1), (0, 1)])]


def cilindro(cx, cz, r, h0, h1, n=24, rep=3.0, r1=None, y0=0.0):
    out = []
    r1 = r if r1 is None else r1
    for i in range(n):
        a0, a1 = TAU * i / n, TAU * (i + 1) / n
        P = [(cx + math.cos(a0) * r, y0 + h0, cz + math.sin(a0) * r), (cx + math.cos(a1) * r, y0 + h0, cz + math.sin(a1) * r),
             (cx + math.cos(a1) * r1, y0 + h1, cz + math.sin(a1) * r1), (cx + math.cos(a0) * r1, y0 + h1, cz + math.sin(a0) * r1)]
        out.append((P, [(i / n * rep, 1), ((i + 1) / n * rep, 1), ((i + 1) / n * rep, 0), (i / n * rep, 0)]))
    return out


def cinta3d(pts, ancho, cam, u0=0.0, u1=1.0):
    """Una cinta que mira a la camara por una lista de puntos."""
    out = []
    n = len(pts) - 1
    for i in range(n):
        a, b = np.array(pts[i], float), np.array(pts[i + 1], float)
        v = cam.ojo - (a + b) / 2
        lado = np.cross(b - a, v)
        lado = lado / (np.linalg.norm(lado) + 1e-9)
        wa = ancho(i / n) if callable(ancho) else ancho
        wb = ancho((i + 1) / n) if callable(ancho) else ancho
        ua, ub = u0 + (u1 - u0) * i / n, u0 + (u1 - u0) * (i + 1) / n
        out.append(([a - lado * wa, b - lado * wb, b + lado * wb, a + lado * wa], [(ua, 1), (ub, 1), (ub, 0), (ua, 0)]))
    return out


def banda_horizontal(cx, cy, cz, r0, r1, a0, a1, n=28, inclina=0.0):
    """Una banda plana en forma de arco (la estela del barrido), con u a lo largo."""
    out = []
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        b0, b1 = a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1
        pts = []
        for (ang, r) in ((b0, r0), (b1, r0), (b1, r1), (b0, r1)):
            pts.append((cx + math.cos(ang) * r, cy + math.sin(inclina) * r * math.sin(ang), cz + math.sin(ang) * r))
        out.append((pts, [(t0, 1), (t1, 1), (t1, 0), (t0, 0)]))
    return out


def ordenar(cam, qs):
    return sorted(qs, key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2])


def aditivo(lz, cam, qs, tex, brillo=1.0):
    for P, UV in qs:
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True,
                         brillo=brillo)


def trans(lz, cam, qs, tex, k=0.85, niebla=None, glow=0.0, luz=1.05):
    for P, UV in ordenar(cam, qs):
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3) * luz, None, niebla, translucido=k)
            if glow:
                lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True,
                             brillo=glow)


def brillo_en(lz, cam, p, tam, color, k=1.0):
    """Un resplandor (aditivo) en p."""
    aditivo(lz, cam, [billboard(p, tam, cam)], tex_disco(_mez(color, (255, 255, 255), 0.6), color, 64), k)


# ----------------------------------------------------------------------
#  El altar
# ----------------------------------------------------------------------
class Niebla:
    color = (0.42, 0.16, 0.08)

    def __init__(self, ini=18.0, largo=60.0, tope=0.85):
        self.ini, self.largo, self.tope = ini, largo, tope

    def __call__(self, z):
        return np.clip((z - self.ini) / self.largo, 0, self.tope)


RADIO_ALTAR = 15


def material_suelo(gx, gz, r):
    d = math.hypot(gx + 0.5, gz + 0.5)
    a = math.atan2(gz + 0.5, gx + 0.5)
    if d < RADIO_ALTAR:
        if d > RADIO_ALTAR - 1.1:
            return 'oro_bloque'
        if d < 2.2:
            return 'magma'
        if 2.2 <= d < 3.2:
            return 'oro_bloque'
        s = ((a + math.pi) / TAU * 12) % 1
        arco = abs(s - 0.5) * TAU / 12 * d                 # distancia (en bloques) a la raya del rayo
        largo = 7.6 if int((a + math.pi) / TAU * 12) % 2 == 0 else 5.6
        if arco < 0.5 and 3.2 <= d < largo:
            return 'oro_bloque'
        if abs(d - 9.6) < 0.5:
            return 'oro_bloque' if (int((a + math.pi) / TAU * 48) % 3 == 0) else 'basalto_j'
        return 'basalto' if r.random() < 0.82 else 'negra'
    if d < RADIO_ALTAR + 1.2:
        return 'negra'
    q = r.random()
    if q < 0.05:
        return 'magma'
    if q < 0.25:
        return 'negra'
    return 'terracota' if q < 0.62 else 'arena_roja'


def suelo(lz, cam, niebla, fase=1, ext=34, desde=-30, prof=58, bloque_lejos=4):
    """El altar bloque a bloque cerca; lejos, losas de 4x4 (mas rapido)."""
    r = random.Random(7)
    qs = []
    for gx in range(-ext, ext):
        for gz in range(desde, prof):
            mat = material_suelo(gx, gz, r)
            if abs(gx) > 22 or gz > 28:
                if gx % bloque_lejos or gz % bloque_lejos:
                    continue
                b = bloque_lejos
                qs.append(([(gx, 0, gz), (gx + b, 0, gz), (gx + b, 0, gz + b), (gx, 0, gz + b)],
                           [(0, 0), (b, 0), (b, b), (0, b)], mat if mat != 'magma' else 'terracota'))
                continue
            h = 0.0
            if math.hypot(gx + 0.5, gz + 0.5) >= RADIO_ALTAR + 1.2:
                h = r.choice((0, 0, 0, 0, -0.0625))
            qs.append(([(gx, h, gz), (gx + 1, h, gz), (gx + 1, h, gz + 1), (gx, h, gz + 1)],
                       [(0, 0), (1, 0), (1, 1), (0, 1)], mat))
    fm.dibujar(lz, cam, qs, LUCES[:1], (0.3, 0.17, 0.13), niebla, brillo=1.0, fase=fase)


def caja_mundo(x, y, z, w, h, d, mat):
    """Una caja en bloques (x, y, z la esquina de abajo)."""
    raiz = nm.nodo('c', (0, 0, 0), (0, 0, 0), [((0, 0, 0, w * 16, h * 16, d * 16), mat)])
    M = vr.T(x, y, z) @ np.diag([1 / 16, 1 / 16, 1 / 16, 1])
    return nm.quads(raiz, {}, M)


def brasero(x, z, alto=6.0, llama=True):
    """Columna de basalto con anillos de oro y un brasero que arde arriba."""
    qs = caja_mundo(x - 1, 0, z - 1, 2, alto, 2, 'basalto_j')
    qs += caja_mundo(x - 1.2, 0, z - 1.2, 2.4, 0.5, 2.4, 'negra')
    for yy in (alto * 0.3, alto * 0.7):
        qs += caja_mundo(x - 1.08, yy, z - 1.08, 2.16, 0.25, 2.16, 'oro_bloque')
    qs += caja_mundo(x - 1.4, alto, z - 1.4, 2.8, 0.6, 2.8, 'oro_bloque')
    qs += caja_mundo(x - 1.1, alto + 0.6, z - 1.1, 2.2, 0.15, 2.2, 'magma')
    return qs


BRASEROS = [(math.cos(a) * (RADIO_ALTAR + 3.5), math.sin(a) * (RADIO_ALTAR + 3.5)) for a in
            [math.radians(22.5 + 45 * k) for k in range(8)]]


def braseros(lz, cam, niebla, fase=1, cuales=None, cerca=13.0):
    for k, (x, z) in enumerate(BRASEROS):
        if cuales is not None and k not in cuales:
            continue
        lejos = math.hypot(cam.ojo[0], cam.ojo[2])
        if math.hypot(x - cam.ojo[0], z - cam.ojo[2]) < max(cerca, 0.62 * lejos) or cam.proyectar((x, 3, z))[2] < 2:
            continue
        fm.dibujar(lz, cam, brasero(x, z), LUCES, AMB, niebla, brillo=1.1, fase=fase)
        llamas_en(lz, cam, (x, 6.7, z), 1.5, fase, n=5, semilla=k)


_TEX_LLAMA = {}


def tex_llama_sprite(fase, semilla=0):
    k = (fase, semilla % 4)
    if k not in _TEX_LLAMA:
        nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
        t = tex_llamas(nuc, pri, hon, 32, 48, semilla=semilla + 3, densidad=1.3)
        # que se apague por los lados: una lengua, no una pared
        x = np.abs(np.arange(32) - 15.5) / 15.5
        t[..., 3] = (t[..., 3] * np.clip(1.15 - x ** 2 * 1.2, 0, 1)[None, :]).astype(np.uint8)
        _TEX_LLAMA[k] = t
    return _TEX_LLAMA[k]


def llamas_en(lz, cam, p, tam, fase, n=4, semilla=0, brillo=1.0):
    """Unas lenguas de fuego (aditivas) que suben desde p."""
    r = random.Random(semilla)
    p = np.array(p, float)
    for i in range(n):
        q = p + np.array([r.uniform(-0.4, 0.4) * tam, tam * r.uniform(0.6, 1.0), r.uniform(-0.4, 0.4) * tam])
        aditivo(lz, cam, [billboard(q, tam * r.uniform(0.4, 0.6), cam, r.uniform(-0.2, 0.2), alto=tam * r.uniform(0.8, 1.1))],
                tex_llama_sprite(fase, i + semilla), brillo * 0.9)
    brillo_en(lz, cam, p + np.array([0, tam * 0.4, 0]), tam * 1.2, color_fase(fase), 0.35 * brillo)


# ----------------------------------------------------------------------
#  El cielo, su sol y el acabado
# ----------------------------------------------------------------------
def cielo(W, H, horizonte, fase=1):
    y = np.linspace(0, 1, H)[:, None]
    arriba = np.array([0.09, 0.03, 0.05])
    medio = np.array([0.38, 0.09, 0.06])
    abajo = np.array([0.95, 0.46, 0.17])
    if fase == 4:
        medio, abajo = np.array([0.32, 0.03, 0.05]), np.array([0.85, 0.16, 0.10])
    if fase == 'furia':
        medio, abajo = np.array([0.12, 0.08, 0.2]), np.array([0.45, 0.55, 0.85])
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.6, arriba + (medio - arriba) * (k / 0.6), medio + (abajo - medio) * ((k - 0.6) / 0.4))
    return np.broadcast_to(col[:, None, :], (H, W, 3)).copy().reshape(H, W, 3)


def tono(x, blanco=0.35):
    """Recorta a 1 sin quemar a blanco: lo que se pasa baja en proporcion (se queda
    con su color) y solo una parte se va hacia el blanco."""
    m = x.max(axis=-1, keepdims=True)
    exceso = np.clip(m - 1, 0, None)
    y = x / np.maximum(1, m)
    return np.clip(y + (1 - y) * np.clip(exceso * blanco, 0, 1), 0, 1)


def bloom(arr, emis, radios=((3, 0.8), (14, 0.6), (44, 0.45)), recorta=True):
    e = Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8))
    out = arr.copy()
    for r_, k in radios:
        out += np.array(e.filter(ImageFilter.GaussianBlur(r_))).astype(float) / 255.0 * k
    out = out + emis * 0.55
    return np.clip(out, 0, 1) if recorta else out


def vineta(arr, fuerza=0.55):
    H, W = arr.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - fuerza * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.3, 0, 1) ** 1.3
    return arr * v[..., None]


def brasas(img, n, semilla, color=(255, 170, 60), zona=None):
    """Brasas que suben por el aire."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x = r.uniform(*(zona[0] if zona else (0, W)))
        y = r.uniform(*(zona[1] if zona else (0, H)))
        rad = r.choice([1, 1, 1.5, 2, 2, 3]) * W / 1600
        largo = r.uniform(2, 7) * W / 1600
        c = (*color, r.randint(120, 230))
        d.line((x, y, x + r.uniform(-1, 1), y + largo), fill=c, width=max(1, int(rad)))
    glow = capa.filter(ImageFilter.GaussianBlur(2))
    out = Image.alpha_composite(img.convert('RGBA'), glow)
    return Image.alpha_composite(out, capa)


def sol_en_cielo(arr, cam, W, H, fase=1, pos=SOL, radio=5.0):
    """El Sol del Caballero: un disco que arde sobre el altar (2D, detras de todo)."""
    x, y, z = cam.proyectar(pos)
    if z <= 0:
        return arr
    x, y = x / SS, y / SS
    rp = cam.foco / SS * radio / z
    nuc, pri, hon = (np.array(nm._hex(c)) / 255 for c in fm.FASE[fase])
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot(xx - x, yy - y) / max(rp, 1)
    disco = np.clip(1.4 - d, 0, 1) ** 0.5
    corona = np.clip(1 - (d - 1) / 6, 0, 1) ** 2.5
    out = arr + corona[..., None] * pri * 0.55
    out = out * (1 - disco[..., None]) + disco[..., None] * (nuc * 0.7 + pri * 0.3)
    # rayos largos
    a = np.arctan2(yy - y, xx - x)
    rayo = (np.cos(a * 9 + 0.4) ** 24) * np.clip(1 - (d - 1) / 14, 0, 1) * (d > 1)
    out += rayo[..., None] * pri * 0.25
    return np.clip(out, 0, 1)


def componer(lz, cam, W, H, fase=1, sol=True, n_brasas=160, semilla=3, cielo_fase=None, fuerza_vineta=0.55):
    alfa = np.array(Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float)[..., None] / 255
    col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    emis = np.array(Image.fromarray((np.clip(tono(lz.emis), 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, fase if cielo_fase is None else cielo_fase)
    if sol:
        fondo = sol_en_cielo(fondo, cam, W, H, fase, pos=SOL)
    arr = col * alfa + fondo * (1 - alfa)
    arr = tono(bloom(arr, emis, recorta=False))
    arr = vineta(arr, fuerza_vineta)
    arr = np.clip(arr * np.array([1.04, 0.98, 0.94]), 0, 1)
    img = Image.fromarray((arr * 255).astype(np.uint8))
    color = (120, 220, 255) if fase == 'furia' else (255, 90, 70) if fase == 4 else (255, 170, 60)
    return brasas(img, int(n_brasas * W / 1600), semilla, color)


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    print('ok', nombre, flush=True)
    return img


# ----------------------------------------------------------------------
#  El caballero y los jugadores
# ----------------------------------------------------------------------
def caballero(lz, cam, x, z, guinada, pose, variante=V, fase=1, niebla=None, luces=None, amb=None, brillo=1.4,
              con_espada=True, y=0.0, escala=fm.ESCALA):
    M = vr.T(0, y, 0) @ fm.entidad_a_mundo(x, 0, z, guinada, escala)
    fm.dibujar(lz, cam, fm.quads(variante, pose, M, con_espada), luces or LUCES, amb or AMB, niebla, brillo, fase)
    return M


def punto(M, p):
    return fm.modelo_a_mundo(M, p)


def jugador(lz, cam, x, z, guinada, y=0.0, niebla=None, pose=None, M=None):
    M = (vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, guinada)) if M is None else M
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), pose or {}, M), LUCES, AMB, niebla)
    return M


def guinada_hacia(x, z, ox=0.0, oz=0.0):
    """La guinada que hace mirar a una entidad en (x, z) hacia (ox, oz) (el frente es -Z)."""
    return math.degrees(math.atan2(-(ox - x), -(oz - z))) % 360 - 0.0


def espada_clavada(lz, cam, M_ent, x, z, variante=V, fase=1, niebla=None, inclina=8.0, giro=0.0):
    """La espada clavada en el suelo junto a el (en px de modelo del caballero)."""
    # la punta un poco hundida: el origen de la espada (empunadura) arriba
    largo = fm.PUNTA_ESPADA
    Mp = M_ent @ vr.T(x, 24 + 6 - largo * math.cos(math.radians(inclina)), z) @ vr.Ry(math.radians(giro)) @ vr.Rx(math.radians(inclina))
    fm.dibujar(lz, cam, fm.quads_espada(variante, Mp), LUCES, AMB, niebla, 1.4, fase)
    return Mp


# ----------------------------------------------------------------------
#  Poses (los brazos se colocan buscando donde caen los punos)
# ----------------------------------------------------------------------
_POSES = {}

PIERNAS_FIRME = {'pierna_izq': {'rot': (-4, 0, -4)}, 'pierna_der': {'rot': (4, 0, 4)}}
PIERNAS_GUARDIA = {'pierna_izq': {'rot': (-20, 0, -8)}, 'espinilla_izq': {'rot': (22, 0, 0)}, 'pie_izq': {'rot': (-2, 0, 0)},
                   'pierna_der': {'rot': (18, 0, 10)}, 'espinilla_der': {'rot': (12, 0, 0)}, 'pie_der': {'rot': (-28, 0, 0)}}
RODILLA = {'pelvis': {'pos': (0, 33, 0)}, 'tabardo': {'rot': (-72, 0, 0)},
           'pierna_izq': {'rot': (-82, 0, -6)}, 'espinilla_izq': {'rot': (84, 0, 0)}, 'pie_izq': {'rot': (-2, 0, 0)},
           'pierna_der': {'rot': (6, 0, 6)}, 'espinilla_der': {'rot': (86, 0, 0)}, 'pie_der': {'rot': (-60, 0, 0)}}
CAPA_VIENTO = {'capa_1': {'rot': (22, 0, 0)}, 'capa_2': {'rot': (12, 0, 0)}, 'capa_3': {'rot': (14, 0, 0)}}


def _une(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = {**out.get(k, {}), **v}
    return out


def _calc(nombre):
    p = None
    if nombre == 'REPOSO':
        p = _une(PIERNAS_FIRME, {'capa_1': {'rot': (2, 0, 0)}})
        p, _ = fm.alcanzar(p, 'der', (-21, -34, -16))
        p, _ = fm.alcanzar(p, 'izq', (24, -26, -2))
        p = fm.apuntar_espada(p, (-0.12, 0.6, -0.8))
    elif nombre == 'HEROICA':
        p = _une(PIERNAS_GUARDIA, CAPA_VIENTO, {'torso': {'rot': (-4, 14, 0)}, 'cabeza': {'rot': (4, -16, 0)}})
        p, _ = fm.alcanzar(p, 'der', (-24, -116, -2))
        p, _ = fm.alcanzar(p, 'izq', (26, -62, -34))
        p = fm.apuntar_espada(p, (-0.55, -0.78, 0.3))
    elif nombre == 'BARRIDO':
        p = _une(PIERNAS_GUARDIA, CAPA_VIENTO, {'torso': {'rot': (6, -24, 0)}, 'cabeza': {'rot': (0, 18, 0)}})
        p, _ = fm.alcanzar(p, 'der', (6, -58, -36))
        p, _ = fm.alcanzar(p, 'izq', (30, -52, 14))
        p = fm.apuntar_espada(p, (0.85, 0.05, -0.52))
    elif nombre == 'CASTIGO_ALZA':
        p = _une(PIERNAS_FIRME, {'cabeza': {'rot': (-22, 0, 0)}, 'torso': {'rot': (-6, 0, 0)}}, CAPA_VIENTO)
        p, _ = fm.alcanzar(p, 'der', (0, -124, -8))
        p, _ = fm.alcanzar(p, 'izq', (1, -112, -8))
        p = fm.apuntar_espada(p, (0, -1, 0.02))
    elif nombre in ('CASTIGO_CLAVA', 'FUENTES'):
        p = _une(RODILLA, {'torso': {'rot': (12, 0, 0)}, 'cabeza': {'rot': (-28 if nombre == 'FUENTES' else 10, 0, 0)}},
                 {'capa_1': {'rot': (8, 0, 0)}, 'capa_2': {'rot': (22, 0, 0)}, 'capa_3': {'rot': (50, 0, 0)}})
        p, _ = fm.alcanzar(p, 'der', (0, -27, -30))
        p, _ = fm.alcanzar(p, 'izq', (0, -37, -30))
    elif nombre == 'SOL':
        p = _une(PIERNAS_GUARDIA, CAPA_VIENTO, {'cabeza': {'rot': (-24, 10, 0)}, 'torso': {'rot': (-6, -10, 0)}})
        p, _ = fm.alcanzar(p, 'izq', (36, -116, -12))
        p, _ = fm.alcanzar(p, 'der', (-24, -36, -14))
        p = fm.apuntar_espada(p, (-0.2, 0.55, -0.81))
    elif nombre == 'OFRENDA':
        p = _une(PIERNAS_FIRME, {'cabeza': {'rot': (-34, 0, 0)}, 'torso': {'rot': (-6, 0, 0)}}, CAPA_VIENTO)
        p, _ = fm.alcanzar(p, 'izq', (10.5, -112, -30))
        p, _ = fm.alcanzar(p, 'der', (-10.5, -112, -30))
    elif nombre == 'DIOS':
        p = _une(PIERNAS_GUARDIA, CAPA_VIENTO, {'cabeza': {'rot': (-16, 0, 0)}, 'torso': {'rot': (-8, 0, 0)}})
        p, _ = fm.alcanzar(p, 'izq', (44, -116, -10))
        p, _ = fm.alcanzar(p, 'der', (-44, -116, -10))
    elif nombre == 'GRITO':
        p = _une(PIERNAS_GUARDIA, CAPA_VIENTO, {'cabeza': {'rot': (-26, 0, 0)}, 'torso': {'rot': (-10, 0, 0)}})
        p, _ = fm.alcanzar(p, 'izq', (36, -44, -12))
        p, _ = fm.alcanzar(p, 'der', (-36, -44, -12))
        p = fm.apuntar_espada(p, (-0.5, 0.3, -0.8))
    return p


def pose(nombre):
    if nombre not in _POSES:
        _POSES[nombre] = _calc(nombre)
    return copy.deepcopy(_POSES[nombre])


POSES_SIN_ESPADA = {'CASTIGO_CLAVA', 'FUENTES', 'OFRENDA', 'DIOS'}


def prueba_poses(W=420, H=640):
    """Hoja de poses, en el estudio (para revisar)."""
    nombres = ['REPOSO', 'HEROICA', 'BARRIDO', 'CASTIGO_ALZA', 'CASTIGO_CLAVA', 'FUENTES', 'SOL', 'OFRENDA', 'DIOS', 'GRITO']
    ims = []
    for n in nombres:
        cam = vr.Camara(ojo=(-14, 7.0, -70), objetivo=(0, 6.8, 0), fov=13.5, ancho=W * SS, alto=H * SS)
        lz = Lienzo(W * SS, H * SS)
        M = caballero(lz, cam, 0, 0, -20, pose(n), V, 1, None, LUZ_ESTUDIO, AMB_ESTUDIO, 1.2, con_espada=n not in POSES_SIN_ESPADA)
        if n in ('CASTIGO_CLAVA', 'FUENTES'):
            espada_clavada(lz, cam, M, 0, -30, V, 1, None, inclina=0.0)
        if n in ('OFRENDA', 'DIOS'):
            espada_clavada(lz, cam, M, -36, -8, V, 1, None, inclina=10.0, giro=20)
        col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
        a = lz.alfa[..., None]
        arr = col * a + np.array([0.93, 0.94, 0.95]) * (1 - a)
        im = Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
        ImageDraw.Draw(im).text((10, 10), n, fill=(20, 20, 20), font=ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 22))
        ims.append(im)
    cols = 5
    img = Image.new('RGB', (W * cols, H * ((len(ims) + cols - 1) // cols)), (240, 240, 240))
    for i, im in enumerate(ims):
        img.paste(im, ((i % cols) * W, (i // cols) * H))
    guardar(img, 'prueba_poses')


# ----------------------------------------------------------------------
#  Ayudas de las escenas
# ----------------------------------------------------------------------
def sol_en_pantalla(cam, sx, sy, dist=90.0):
    """El punto del mundo que cae en (sx, sy) de la pantalla (0..1), a 'dist' bloques."""
    t = math.tan(math.radians(cam_fov(cam)) / 2)
    asp = cam.W / cam.H
    d = cam.f + cam.r * (2 * sx - 1) * t * asp + cam.u * (1 - 2 * sy) * t
    return cam.ojo + d / np.linalg.norm(d) * dist


def cam_fov(cam):
    return math.degrees(2 * math.atan((cam.H / 2) / cam.foco))


_ESQ = {}


def esq(variante):
    if variante not in _ESQ:
        _ESQ[variante] = fm.esqueleto(variante)
    return _ESQ[variante]


def mundo_de(M_ent, variante, pose_, nombre, local=(0, 0, 0)):
    Mn = fm.matrices(esq(variante), pose_)[nombre]
    return (M_ent @ Mn @ np.array([*local, 1.0]))[:3]


def fuego_cuerpo(lz, cam, M, variante, pose_, fase, espada=True, k=1.0):
    """Lenguas de fuego de verdad (sprites) sobre la corona o el halo, las hombreras y la hoja."""
    if variante in ('A', 'C'):
        llamas_en(lz, cam, mundo_de(M, variante, pose_, 'cabeza', (0, -24, -1)), 1.5 if variante == 'A' else 1.9, fase, 5, 11, k)
        for lado in ('izq', 'der'):
            llamas_en(lz, cam, mundo_de(M, variante, pose_, 'hombro_' + lado, (5 if lado == 'izq' else -5, -8, 0)), 0.9, fase, 3, 12, k)
    else:
        brillo_en(lz, cam, mundo_de(M, variante, pose_, 'halo'), 3.6, color_fase(fase), 0.35 * k)
    if variante == 'N':
        for lado in ('izq', 'der'):
            llamas_en(lz, cam, mundo_de(M, variante, pose_, 'hombro_' + lado, (6.5 if lado == 'izq' else -6.5, -13, 0)), 0.8, fase, 3, 12, k)
        brillo_en(lz, cam, mundo_de(M, variante, pose_, 'torso', (0, -34, -16)), 1.6, color_fase(fase), 0.5 * k)
    else:
        brillo_en(lz, cam, mundo_de(M, variante, pose_, 'torso', (0, -33, -12)), 1.4, color_fase(fase), 0.5 * k)
    if espada:
        for i in range(7):
            p = mundo_de(M, variante, pose_, 'espada', (0, 16 + i * 9, 0))
            llamas_en(lz, cam, p, 0.55, fase, 2, 40 + i, 0.8 * k)
        brillo_en(lz, cam, mundo_de(M, variante, pose_, 'espada', (0, 9, 0)), 0.9, color_fase(fase, 0), 0.6 * k)


def aura(lz, cam, M, variante, pose_, fase, n=160, semilla=5, tam=(0.5, 1.3), k=0.5, con_espada=True):
    """El cuerpo envuelto en llamas (Furia, Dios de la Guerra): sprites sobre la malla."""
    r = random.Random(semilla)
    qs = fm.quads(variante, pose_, M, con_espada)
    centro = punto(M, (0, -40, 0))
    for _ in range(n):
        P, _, _ = qs[r.randrange(len(qs))]
        c = np.mean(P, axis=0)
        fuera = c - centro
        fuera[1] *= 0.3
        c = c + fuera / (np.linalg.norm(fuera) + 1e-6) * 0.25
        t = r.uniform(*tam)
        aditivo(lz, cam, [billboard(c + np.array([0, t * 0.7, 0]), t * 0.45, cam, r.uniform(-0.25, 0.25), alto=t)],
                tex_llama_sprite(fase, r.randrange(8)), k)


def sello(lz, cam, x, z, R, fase, relleno=60, k=0.75, glow=0.5):
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    trans(lz, cam, suelo_cuad(x, z, R, 0.07), tex_sello(pri, relleno=relleno), k, None, glow)


def explosion(lz, cam, p, R, fase, semilla=1, lava=True, k=1.0):
    """Una explosion de fuego y lava: el estallido del color de la fase, lenguas de
    fuego que salen, gotas de lava y el charco que queda."""
    r = random.Random(semilla)
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    p = np.array(p, float)
    aditivo(lz, cam, [billboard(p + np.array([0, R * 0.5, 0]), R * 1.3, cam)], tex_disco(pri, hon, 128, 0.12, 1.8), 0.55 * k)
    aditivo(lz, cam, [billboard(p + np.array([0, R * 0.4, 0]), R * 0.55, cam)], tex_disco(nuc, pri, 64, 0.25, 1.4), 0.45 * k)
    for i in range(22):
        a = r.uniform(0, TAU)
        d = r.uniform(0.1, 0.95)
        q = p + np.array([math.cos(a) * R * d, R * r.uniform(0.05, 0.7) * (1.2 - d), math.sin(a) * R * d])
        t = R * r.uniform(0.25, 0.5)
        aditivo(lz, cam, [billboard(q + np.array([0, t * 0.6, 0]), t * 0.55, cam, r.uniform(-0.5, 0.5), alto=t)],
                tex_llama_sprite(fase, i), 0.75 * k)
    if lava:
        for i in range(7):                      # gotas de lava que salen volando
            a = r.uniform(0, TAU)
            d = r.uniform(0.6, 1.5) * R
            q = p + np.array([math.cos(a) * d, r.uniform(0.3, 1.3) * R, math.sin(a) * d])
            fm.dibujar(lz, cam, caja_mundo(*(q - 0.11), 0.22, 0.22, 0.22, 'lava'), LUCES, AMB, None, 0.8, fase)
        # el charco de lava que queda
        trans(lz, cam, suelo_cuad(p[0], p[2], R * 0.8, 0.08, r.uniform(0, 1)), tex_disco(pri, hon, 64, 0.5, 0.7), 0.9, None, 0.35)


def sol_mini(lz, cam, p, R, fase, semilla=3, k=1.0):
    """Un sol en miniatura: el nucleo de cubos, la corona y lenguas de fuego alrededor."""
    r = random.Random(semilla)
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    p = np.array(p, float)
    aditivo(lz, cam, [billboard(p, R * 2.4, cam)], tex_disco(pri, hon, 128, 0.1, 2.0), 0.5 * k)
    for (w, h, d) in ((0.78, 0.48, 0.48), (0.48, 0.78, 0.48), (0.48, 0.48, 0.78),
                      (0.68, 0.68, 0.48), (0.68, 0.48, 0.68), (0.48, 0.68, 0.68)):     # una bola de cubos
        fm.dibujar(lz, cam, caja_mundo(p[0] - R * w, p[1] - R * h, p[2] - R * d, 2 * R * w, 2 * R * h, 2 * R * d, 'sol_sup'),
                   LUCES, AMB, None, 0.7, fase)
    for i in range(14):
        a = TAU * i / 14 + r.uniform(-0.1, 0.1)
        dirv = cam.r * math.cos(a) + cam.u * math.sin(a)
        aditivo(lz, cam, [billboard(p + dirv * R * 1.05, R * 0.32, cam, a - math.pi / 2, alto=R * 0.55)],
                tex_llama_sprite(fase, i), 0.8 * k)


def estela(lz, cam, pts, ancho, fase, k=0.9):
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    tex = tex_haz(nuc, pri, 32, 8)
    tex = np.transpose(tex, (1, 0, 2)).copy()       # el alma a lo largo
    aditivo(lz, cam, cinta3d(pts, ancho, cam), tex, k)


def haz_vertical(lz, cam, x, z, r, y0, y1, fase, k=1.0):
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    aditivo(lz, cam, cilindro(x, z, r, y0, y1, 16, 1.0), tex_haz(nuc, pri, 32, 8), k)
    aditivo(lz, cam, cilindro(x, z, r * 0.45, y0, y1, 12, 1.0), tex_haz((255, 255, 245), nuc, 32, 8), k)


def jugador_pose(caido=False, brazos_arriba=False, salto=False, corre=False, golpe=False):
    p = {}
    if brazos_arriba:
        p.update({'bi': {'rot': (-160, 0, -25)}, 'bd': {'rot': (-150, 0, 30)}, 'pi': {'rot': (20, 0, -8)}, 'pd': {'rot': (-15, 0, 8)}})
    if salto:
        p.update({'pi': {'rot': (-40, 0, 0)}, 'pd': {'rot': (30, 0, 0)}, 'bi': {'rot': (-40, 0, -30)}, 'bd': {'rot': (40, 0, 30)}})
    if corre:
        p.update({'pi': {'rot': (-35, 0, 0)}, 'pd': {'rot': (35, 0, 0)}, 'bi': {'rot': (40, 0, 0)}, 'bd': {'rot': (-40, 0, 0)}})
    if golpe:
        p.update({'bd': {'rot': (-110, -20, 0)}, 'pi': {'rot': (-15, 0, 0)}, 'pd': {'rot': (15, 0, 0)}})
    if caido:
        p.update({'cuerpo': {'rot': (0, 0, 0)}})
    return p


def jugador_a(lz, cam, x, z, ox=0.0, oz=0.0, y=0.0, niebla=None, pose_=None, extra=0.0):
    return jugador(lz, cam, x, z, guinada_hacia(x, z, ox, oz) + extra, y=y, niebla=niebla, pose=pose_)


def jugador_volando(lz, cam, p, guinada, inclina, niebla=None, pose_=None):
    """Un jugador lanzado (inclinado hacia atras), con los pies en p."""
    M = vr.T(*p) @ vr.Ry(math.radians(guinada)) @ vr.Rx(math.radians(inclina)) @ vr.T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), pose_ or {}, M), LUCES, AMB, niebla)


def ruptura(lz, cam, x, z, n, fase, largo=8.0, semilla=2):
    """Grietas de lava que salen por el suelo desde (x, z)."""
    r = random.Random(semilla)
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    tex = tex_haz(nuc, pri, 32, 8)
    tex = np.transpose(tex, (1, 0, 2)).copy()
    for i in range(n):
        a = TAU * i / n + r.uniform(-0.2, 0.2)
        pts = [(x, 0.06, z)]
        px, pz = x, z
        for j in range(6):
            a += r.uniform(-0.35, 0.35)
            px += math.cos(a) * largo / 6
            pz += math.sin(a) * largo / 6
            pts.append((px, 0.06, pz))
        out = []
        for j in range(len(pts) - 1):
            a0, b0 = np.array(pts[j]), np.array(pts[j + 1])
            d = b0 - a0
            lado = np.array([-d[2], 0, d[0]]) / (np.linalg.norm(d) + 1e-9) * 0.14 * (1 - j / 6)
            out.append(([a0 - lado, b0 - lado, b0 + lado, a0 + lado], [(0, 1), (1, 1), (1, 0), (0, 0)]))
        aditivo(lz, cam, out, tex, 0.9)


def estatua(rota=False):
    """Un angel de piedra con su trompeta de oro (para las Trompetas del Apocalipsis).
    En px (16 = 1 bloque), y = 0 en el suelo, Y hacia abajo, frente -Z."""
    n = nm.nodo
    if rota:
        return n('estatua', (0, 0, 0), (0, 0, 0), [
            ((-12, -10, -12, 24, 10, 24), 'marmol_osc'), ((-12.5, -11, -12.5, 25, 1.5, 25), 'oro_bloque'),
            ((-7, -18, -5, 14, 8, 10), 'marmol'), ((-5, -24, -2, 7, 6, 6), 'marmol'),
            ((6, -3, -16, 6, 3, 5), 'marmol'), ((-16, -2, 4, 5, 2, 6), 'marmol'), ((12, -2, 8, 4, 2, 4), 'marmol_osc'),
            ((-14, -4, -14, 4, 4, 4), 'oro_bloque')])
    ala = lambda s: n('ala_' + ('i' if s > 0 else 'd'), (5 * s, -40, 5), (0, -40 * s, -30 * s), [
        ((-1, -10, 0, 2, 20, 7), 'marmol'), ((-1, -18, 6, 2, 30, 6), 'marmol'), ((-1, -24, 11, 2, 34, 6), 'marmol_osc'),
        ((-1, -20, 16, 2, 26, 5), 'marmol'), ((-1, -14, 20, 2, 16, 4), 'marmol_osc')])
    trompeta = n('trompeta', (0, -46, -6), (-58, 0, 0), [
        ((-1, -26, -1, 2, 26, 2), 'oro_bloque'), ((-2, -29, -2, 4, 3, 4), 'oro_bloque'),
        ((-3.4, -32, -3.4, 6.8, 3, 6.8), 'oro_bloque'), ((-5, -34, -5, 10, 2.4, 10), 'oro_bloque'),
        ((-4, -34.6, -4, 8, 1, 8), 'nucleo')])
    brazos = [n('brazo_' + nn, (5 * s, -40, -2), (-70, 0, -10 * s), [((-1.8, 0, -1.8, 3.6, 12, 3.6), 'marmol')])
              for s, nn in ((1, 'i'), (-1, 'd'))]
    return n('estatua', (0, 0, 0), (0, 0, 0), [
        ((-12, -10, -12, 24, 10, 24), 'marmol_osc'), ((-12.5, -11, -12.5, 25, 1.5, 25), 'oro_bloque'),
        ((-9, -22, -7, 18, 12, 14), 'marmol'),                  # el vuelo de la tunica
        ((-7, -42, -5, 14, 20, 10), 'marmol'),
        ((-7.5, -43, -5.5, 15, 2, 11), 'oro_bloque'),           # el cinto
        ((-4.5, -51, -4.5, 9, 9, 9), 'marmol'),                 # la cabeza
        ((-5.5, -54, -0.5, 11, 1.4, 1.4), 'oro_bloque'),        # el halo
    ], [ala(1), ala(-1), *brazos, trompeta])


def dibujar_estatua(lz, cam, x, z, guinada, niebla, rota=False, fase=2):
    M = vr.T(x, 0, z) @ vr.Ry(math.radians(guinada)) @ vr.S(2.2) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])
    fm.dibujar(lz, cam, nm.quads(estatua(rota), {}, M), LUCES, AMB, niebla, 1.2, fase)
    return M


def fuente_solar(rota=False):
    """Una fuente solar: obelisco de marmol y oro con vetas de fuego; el sol flota encima.
    En px (16 = 1 bloque), y = 0 en el suelo, Y hacia abajo."""
    n = nm.nodo
    if rota:
        return n('fuente', (0, 0, 0), (0, 0, 0), [
            ((-14, -6, -14, 28, 6, 28), 'oro_bloque'), ((-10, -30, -10, 20, 24, 20), 'marmol'),
            ((-7, -40, -8, 11, 10, 12), 'marmol'), ((-10.5, -24, -10.5, 21, 2, 21), 'oro_bloque'),
            ((12, -5, -6, 9, 5, 9), 'marmol'), ((-22, -4, 4, 8, 4, 7), 'marmol_osc'), ((-4, -42, -4, 4, 3, 4), 'magma')])
    vetas = [((-10.4, -64 + 12 * k, -10.4, 20.8, 1.2, 20.8), 'nucleo') for k in range(4)]
    return n('fuente', (0, 0, 0), (0, 0, 0), [
        ((-14, -6, -14, 28, 6, 28), 'oro_bloque'),
        ((-10, -70, -10, 20, 64, 20), 'marmol'),
        ((-7, -80, -7, 14, 10, 14), 'marmol'),
        ((-4, -86, -4, 8, 6, 8), 'oro_bloque'),
        *vetas,
        ((-11, -12, -11, 22, 2, 22), 'oro_bloque'), ((-11, -72, -11, 22, 2, 22), 'oro_bloque'),
    ])


def dibujar_fuente(lz, cam, x, z, niebla, rota=False, fase=3):
    M = vr.T(x, 0, z) @ vr.S(1.6) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])
    fm.dibujar(lz, cam, nm.quads(fuente_solar(rota), {}, M), LUCES, AMB, niebla, 1.3, fase)
    return (M @ np.array([0, -104, 0, 1.0]))[:3]


def cupula(c, R, n=18, m=8):
    """Media esfera (la cupula de sol que no deja pegarle)."""
    out = []
    for i in range(n):
        for j in range(m):
            a0, a1 = TAU * i / n, TAU * (i + 1) / n
            b0, b1 = (math.pi / 2) * j / m, (math.pi / 2) * (j + 1) / m
            P = [(c[0] + R * math.cos(b) * math.cos(a), c[1] + R * math.sin(b) * 1.15, c[2] + R * math.cos(b) * math.sin(a))
                 for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
            out.append((P, [(i / n * 4, j / m * 2), ((i + 1) / n * 4, j / m * 2), ((i + 1) / n * 4, (j + 1) / m * 2),
                            (i / n * 4, (j + 1) / m * 2)]))
    return out


def estudio(lz, W, H, emis=0.5, fondo=(0.93, 0.94, 0.95)):
    col = np.clip(lz.color + lz.emis * emis, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array(fondo) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)


def rotulo(img, texto, x, y, tam=30, color=(30, 18, 14), fuente='Oswald-Bold.ttf', centro=False):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FUENTE + fuente, tam)
    if centro:
        x -= d.textlength(texto, font=f) / 2
    d.text((x, y), texto, font=f, fill=color)


# ----------------------------------------------------------------------
#  1. El cuerpo: las tres opciones, vistas, escala y fases
# ----------------------------------------------------------------------
JUGADORES_HEROICA = ((-6.0, -1.5), (5.8, -2.6), (-2.6, -6.0), (8.5, 3.0), (-9.5, 4.5))


def heroica(variante=V, fase=1, W=1600, H=900, nombre=None):
    if variante == 'N':
        cam = vr.Camara(ojo=(-10.0, 2.4, -14.0), objetivo=(0.6, 8.0, 4.0), fov=56, ancho=W * SS, alto=H * SS)
    else:
        cam = vr.Camara(ojo=(-9.0, 1.7, -14.5), objetivo=(0.6, 6.4, 4.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(18, 70)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase)
    for (x, z) in JUGADORES_HEROICA:
        jugador_a(lz, cam, x, z, 0, 4, niebla=niebla)
    p = pose('HEROICA')
    M = caballero(lz, cam, 0, 4, 22, p, variante, fase, niebla)
    fuego_cuerpo(lz, cam, M, variante, p, fase)
    global SOL
    viejo = SOL
    SOL = sol_en_pantalla(cam, 0.8, 0.14, 120)
    img = componer(lz, cam, W, H, fase)
    SOL = viejo
    return guardar(img, nombre or f'heroica_{variante}')


def opciones(W=1800, H=860):
    """Las tres opciones lado a lado, en el estudio."""
    img = Image.new('RGB', (W, H), (237, 238, 240))
    w = W // 3
    for i, v in enumerate('ABC'):
        cam = vr.Camara(ojo=(-16, 7.0, -64), objetivo=(0, 6.4, 0), fov=12.0, ancho=w * SS, alto=(H - 70) * SS)
        lz = Lienzo(w * SS, (H - 70) * SS)
        M = caballero(lz, cam, 0, 0, -18, pose('REPOSO'), v, 1, None, LUZ_ESTUDIO, AMB_ESTUDIO, 1.25)
        im = estudio(lz, w, H - 70, fondo=(0.93, 0.935, 0.945))
        img.paste(im, (i * w, 0))
        rotulo(img, ('A · CORONA DE LLAMAS', 'B · HALO DE SOL', 'C · BRASA VIVA')[i], i * w + w / 2, H - 62, 34, centro=True)
    guardar(img, 'opciones')


def vistas(variante=V, W=1800, H=760):
    img = Image.new('RGB', (W, H), (237, 238, 240))
    w = W // 3
    for i, g in enumerate((0, -90, 180)):
        cam = vr.Camara(ojo=(0, 7.2, -70), objetivo=(0, 7.2, 0), fov=12.6, ancho=w * SS, alto=H * SS)
        lz = Lienzo(w * SS, H * SS)
        caballero(lz, cam, 0, 0, g, pose('REPOSO'), variante, 1, None, LUZ_ESTUDIO, AMB_ESTUDIO, 1.25)
        img.paste(estudio(lz, w, H, fondo=(0.93, 0.935, 0.945)), (i * w, 0))
    guardar(img, f'vistas_{variante}')


def fases(variante=V, W=1800, H=640):
    w = W // 5
    img = Image.new('RGB', (W, H))
    for i, f in enumerate((1, 2, 3, 4, 'furia')):
        cam = vr.Camara(ojo=(-14, 7.6, -66), objetivo=(0, 7.4, 0), fov=13.6, ancho=w * SS, alto=H * SS)
        lz = Lienzo(w * SS, H * SS)
        p = pose('GRITO' if f == 'furia' else 'REPOSO')
        M = caballero(lz, cam, 0, 0, -18, p, variante, f, None, LUCES, AMB, 1.4)
        if f in (4, 'furia'):
            aura(lz, cam, M, variante, p, f, 120, 9, (0.5, 1.2), 0.7)
        fuego_cuerpo(lz, cam, M, variante, p, f, k=0.8)
        col = np.array(nm._hex(fm.FASE[f][2])) / 255
        arr_l = np.clip(lz.color, 0, 1)
        a = lz.alfa[..., None]
        yy = np.linspace(0, 1, H * SS)[:, None, None]
        fondo = np.broadcast_to(0.06 + col * 0.35 * yy, (H * SS, w * SS, 3))
        arr = arr_l * a + fondo * (1 - a)
        arr = tono(bloom(arr, tono(lz.emis), ((4, 0.7), (20, 0.5)), recorta=False))
        im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).resize((w, H), Image.LANCZOS)
        img.paste(im, (i * w, 0))
        rotulo(img, ('I', 'II', 'III', 'IV', 'FURIA')[i], i * w + 18, H - 54, 34, color=tuple(nm._hex(fm.FASE[f][1])))
        rotulo(img, fm.NOMBRE_FASE[f], i * w + (58 if i < 4 else 120), H - 46, 22, color=(235, 225, 215), fuente='Montserrat-SemiBold.ttf')
    guardar(img, 'fases')


def escala(W=1800, H=820):
    """Un jugador, el Vigia, el Caballero y los jefes de antes, sobre la reticula de bloques."""
    import importlib
    cam = vr.Camara(ojo=(6.0, 9.2, -150), objetivo=(6.0, 9.2, 0), fov=9.4, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    amb = (0.36, 0.36, 0.38)
    xs = {'jugador': -14.0, 'vigia': -11.0, 'caballero': -4.5, 'rajang': 6.5, 'nerea': 20.0}
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(xs['jugador'], 0, -20)), LUZ_ESTUDIO, amb)
    vt = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia.png'))
    vb = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia_ojo.png'))
    vr.dibujar_quads(lz, cam, vr.quads_del_modelo({}, modelo_a_mundo=vr.entidad_a_mundo(xs['vigia'], 0, 0, -20)), vt, emis=vb,
                     luces=LUZ_ESTUDIO, ambiente=amb, brillo=1.2)
    caballero(lz, cam, xs['caballero'], 0, -20, pose('REPOSO'), V, 1, None, LUZ_ESTUDIO, amb, 1.25)
    altos = {'jugador': 1.8, 'vigia': 2.9, 'caballero': None}
    otros = []
    try:
        rme = importlib.import_module('rajang_mejoras_escenas')
        ra = importlib.import_module('rajang_juego_anim')
        qs = rme.rajang(lz, cam, xs['rajang'], 0, -20, ra.pose_en('REPOSO', 0.0), 1, LUZ_ESTUDIO, amb)
        altos['rajang'] = max(max(p[1] for p in q[0]) for q in qs)
        otros.append('rajang')
    except Exception as e:
        print('sin rajang:', e)
    try:
        nre = importlib.import_module('nerea_remake_escenas')
        nre.nerea(lz, cam, 'despues', xs['nerea'], 0, -20, luces=LUZ_ESTUDIO, amb=amb, brillo=1.2)
        altos['nerea'] = 15.0
        otros.append('nerea')
    except Exception as e:
        print('sin nerea:', e)
    # el alto del caballero, medido en su malla (hasta lo mas alto del yelmo)
    qk = fm.quads(V, pose('REPOSO'), fm.entidad_a_mundo(0, 0, 0, 0))
    altos['caballero'] = max(max(p[1] for p in q[0]) for q, mat in [(q, q[2]) for q in qk] if mat not in ('llama', 'llama_p'))
    img = estudio(lz, W, H).convert('RGBA')
    rej = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rej)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 18)
    for b in range(0, 19, 2):
        _, y, _ = cam.proyectar((0, b, 0)); y /= SS
        d.line((44, y, W - 14, y), fill=(70, 40, 30, 110 if b else 220), width=2 if b == 0 else 1)
        d.text((10, y - 11), f'{b}', font=f, fill=(70, 40, 30, 255))
    img = Image.alpha_composite(img, rej)
    d = ImageDraw.Draw(img)
    fn = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 26)
    fa = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 17)
    nombres = {'jugador': 'JUGADOR', 'vigia': 'VIGÍA', 'caballero': 'NOVILIS', 'rajang': 'RAJANG', 'nerea': 'NEREA'}
    for k in ['jugador', 'vigia', 'caballero'] + otros:
        alto = altos[k]
        px_, py, _ = cam.proyectar((xs[k], alto + 0.5, 0)); px_ /= SS; py /= SS
        cifra = f'{alto:.1f}'.replace('.', ',') + ' bloques'
        wn = d.textlength(nombres[k], font=fn); wa = d.textlength(cifra, font=fa)
        col = (150, 50, 20, 255) if k == 'caballero' else (60, 40, 34, 255)
        d.text((px_ - wn / 2, py - 60), nombres[k], font=fn, fill=col)
        d.text((px_ - wa / 2, py - 26), cifra, font=fa, fill=(90, 70, 60, 255))
    img.convert('RGB').save(os.path.join(OUT, 'escala.jpg'), quality=92)
    print('ok escala', altos, flush=True)


# ----------------------------------------------------------------------
#  2. Ataques
# ----------------------------------------------------------------------
def barrido(W=1600, H=900, fase=1):
    cam = vr.Camara(ojo=(-14.0, 9.5, -18.5), objetivo=(0.5, 3.8, 3.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(22, 60)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase)
    cz = 4.0
    # el de cerca, al que le acaba de pasar la hoja (cae de espaldas), y los de lejos
    jugador_volando(lz, cam, (-3.5, 0.6, cz - 6.8), 200, -35, niebla, jugador_pose(brazos_arriba=True))
    jugador_a(lz, cam, 3.4, cz - 7.6, 0, cz, niebla=niebla, pose_=jugador_pose(golpe=True))
    lejos = [(-12.0, cz - 9.0), (-4.0, cz - 15.5), (11.5, cz - 11.0)]
    for (x, z) in lejos:
        jugador_a(lz, cam, x, z, 0, cz, niebla=niebla, pose_=jugador_pose(corre=True), extra=180)
    p = pose('BARRIDO')
    M = caballero(lz, cam, 0, cz, 8, p, V, fase, niebla)
    fuego_cuerpo(lz, cam, M, V, p, fase)
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    # el alcance de la hoja (cerca: el golpe) en el suelo
    trans(lz, cam, suelo_cuad(0, cz, 8.6, 0.07), tex_aro(pri, 256, 0.025, 26, 36), 0.7, None, 0.4)
    # la estela de la hoja: una banda de fuego a la altura del tajo
    yb = mundo_de(M, V, p, 'espada', (0, 40, 0))[1]
    ab = banda_horizontal(0, yb, cz, 2.2, 8.4, math.radians(-200), math.radians(-60), 36)
    tex = tex_media_luna(nuc, pri, 128)
    estela_tex = np.zeros((16, 64, 4), np.uint8)
    for u in range(64):
        k = u / 63
        for v in range(16):
            q = v / 15
            a = (k ** 1.5) * (1 - abs(q - 0.65) / 0.65) if q < 1 else 0
            c = _mez(hon, nuc, q)
            estela_tex[v, u] = (*c, int(np.clip(a * 300, 0, 255)))
    aditivo(lz, cam, ab, estela_tex, 1.0)
    # los tajos de fuego que salen volando hacia los de lejos
    for i, (x, z) in enumerate(lejos):
        d = np.array([x, 0, z - cz])
        d /= np.linalg.norm(d)
        q = np.array([0, yb - 0.6, cz]) + d * (8.5 + 3.5 * (i % 2)) + np.array([0, -0.4 * i, 0])
        aditivo(lz, cam, [billboard(q, 2.6, cam, 0.0, alto=1.3)], tex, 1.0)
        aditivo(lz, cam, [billboard(q - d * 1.6, 1.8, cam, 0.0, alto=0.9)], tex, 0.45)
        llamas_en(lz, cam, q - np.array([0, 0.5, 0]), 0.7, fase, 3, 60 + i, 0.8)
    img = componer(lz, cam, W, H, fase, sol=False)
    guardar(img, 'barrido')


def castigo_rayos(W=1600, H=900, fase=2):
    cam = vr.Camara(ojo=(-19.0, 8.0, -24.0), objetivo=(0.0, 5.0, 3.0), fov=54, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(26, 60)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase)
    cz = 5.0
    marcas = [(-8.5, -3.0, True), (6.0, -4.5, False), (-2.0, -9.0, True), (10.0, 4.0, False)]
    for (x, z, cae) in marcas:
        sello(lz, cam, x, z, 1.9, fase, 70, 0.8, 0.5)
    # a uno le cae encima; el otro sale de su sello a tiempo; a los otros dos les va a caer
    jugador_a(lz, cam, -8.5 - 2.4, -3.0 - 1.0, 0, cz, niebla=niebla, pose_=jugador_pose(corre=True), extra=90)
    jugador_volando(lz, cam, (-2.0, 0.4, -9.0), 30, -25, niebla, jugador_pose(brazos_arriba=True))
    jugador_a(lz, cam, 6.0, -4.5, 0, cz, niebla=niebla)
    jugador_a(lz, cam, 10.0, 4.0, 0, cz, niebla=niebla, pose_=jugador_pose(corre=True), extra=-90)
    p = pose('CASTIGO_ALZA')
    M = caballero(lz, cam, 0, cz, 14, p, V, fase, niebla)
    fuego_cuerpo(lz, cam, M, V, p, fase, k=1.1)
    global SOL
    viejo = SOL
    SOL = sol_en_pantalla(cam, 0.36, 0.06, 140)
    punta = mundo_de(M, V, p, 'espada', (0, fm.PUNTA_ESPADA, 0))
    estela(lz, cam, [SOL + (punta - SOL) * t for t in np.linspace(0.7, 1.0, 10)], 0.22, fase, 0.7)
    brillo_en(lz, cam, punta, 1.6, color_fase(fase), 0.6)
    for (x, z, cae) in marcas:
        if cae:
            haz_vertical(lz, cam, x, z, 0.5, 0, 30, fase, 0.3)
            explosion(lz, cam, (x, 0.1, z), 1.7, fase, int(x * 7) % 11, lava=False, k=0.8)
    img = componer(lz, cam, W, H, fase)
    SOL = viejo
    guardar(img, 'castigo_rayos')


def castigo_onda(W=1600, H=900, fase=2):
    cam = vr.Camara(ojo=(-15.0, 6.0, -18.0), objetivo=(0.0, 2.6, 4.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(24, 60)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase)
    cz = 5.0
    R = 8.5
    p = pose('CASTIGO_CLAVA')
    M = caballero(lz, cam, 0, cz, 10, p, V, fase, niebla, con_espada=False)
    base = punto(M, (0, 24, -30))
    # los que saltan la onda (uno la salta, otro llega tarde)
    for ang, y, pose_ in ((215, 1.6, jugador_pose(salto=True)), (290, 1.4, jugador_pose(salto=True))):
        a = math.radians(ang)
        jugador_a(lz, cam, base[0] + math.cos(a) * R, base[2] + math.sin(a) * R, base[0], base[2], y=y, niebla=niebla, pose_=pose_)
    jugador_volando(lz, cam, (base[0] + 9.2, 0.5, base[2] + 3.0), -100, -30, niebla, jugador_pose(brazos_arriba=True))
    jugador_a(lz, cam, -11.0, cz - 10.0, 0, cz, niebla=niebla, pose_=jugador_pose(corre=True))
    espada_clavada(lz, cam, M, 0, -30, V, fase, niebla, inclina=0.0)
    fuego_cuerpo(lz, cam, M, V, p, fase, espada=False)
    ruptura(lz, cam, base[0], base[2], 9, fase, R * 0.95, 4)
    explosion(lz, cam, base, 1.3, fase, 3, lava=False, k=0.6)
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    pared = tex_llamas(nuc, pri, hon, 64, 48, 7, 1.4)
    trans(lz, cam, cilindro(base[0], base[2], R, 0, 1.9, 64, 16.0), pared, 0.8, None, 0.35)
    trans(lz, cam, suelo_cuad(base[0], base[2], R + 0.3, 0.08), tex_aro(pri, 256, 0.05, 0), 0.7, None, 0.3)
    r = random.Random(9)
    for i in range(46):                                   # lenguas sueltas por encima de la onda
        a = TAU * i / 46 + r.uniform(-0.05, 0.05)
        q = (base[0] + math.cos(a) * R, 1.0, base[2] + math.sin(a) * R)
        aditivo(lz, cam, [billboard(np.array(q) + np.array([0, 0.6, 0]), 0.5, cam, r.uniform(-0.2, 0.2), alto=1.0)],
                tex_llama_sprite(fase, i), 0.6)
    img = componer(lz, cam, W, H, fase, sol=False)
    guardar(img, 'castigo_onda')


def esc_sol(W=1600, H=900, fase=2):
    cam = vr.Camara(ojo=(-12.5, 3.2, -16.5), objetivo=(0.6, 7.0, 4.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(22, 60)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase)
    cz = 6.0
    marcas = [(-9.0, -2.0), (5.5, -6.5), (11.0, 6.0)]
    for (x, z) in marcas:
        sello(lz, cam, x, z, 3.2, fase, 80, 0.8, 0.6)
    jugador_a(lz, cam, -9.0 + 3.6, -2.0 - 1.6, 0, cz, niebla=niebla, pose_=jugador_pose(corre=True), extra=110)
    jugador_a(lz, cam, 6.4, -6.1, 0, cz, niebla=niebla)
    jugador_a(lz, cam, 1.6, -4.5, 0, cz, niebla=niebla, pose_=jugador_pose(golpe=True))
    p = pose('SOL')
    M = caballero(lz, cam, 0, cz, 16, p, V, fase, niebla)
    fuego_cuerpo(lz, cam, M, V, p, fase)
    mano = mundo_de(M, V, p, 'mano_izq', (0, 6, 0))
    centro = mano + np.array([0, 2.1, 0])
    sol_mini(lz, cam, centro, 1.25, fase, 4)
    # el primero ya ha caido: la explosion de fuego y lava
    explosion(lz, cam, (-9.0, 0.1, -2.0), 3.0, fase, 6)
    # el segundo va en el aire, con su estela
    destino = np.array([5.5, 0.0, -6.5])
    vuelo = centro + (destino - centro) * 0.55 + np.array([0, 2.5, 0])
    pts = [centro + (vuelo - centro) * t + np.array([0, 2.0 * math.sin(math.pi * t) * 0.6, 0]) for t in np.linspace(0.1, 1.0, 10)]
    estela(lz, cam, pts, lambda t: 0.15 + 0.55 * t, fase, 0.8)
    sol_mini(lz, cam, vuelo, 0.75, fase, 7)
    img = componer(lz, cam, W, H, fase, sol=False)
    guardar(img, 'sol')


def fuentes(W=1600, H=900, fase=3):
    cam = vr.Camara(ojo=(-18.0, 13.0, -22.0), objetivo=(0.0, 4.6, 3.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(26, 60)
    suelo(lz, cam, niebla, fase)
    cz = 4.0
    pos = [(math.cos(math.radians(a)) * 11.5, cz + math.sin(math.radians(a)) * 11.5) for a in (300, 190, 10)]
    rota = 1
    orbes = []
    for i, (x, z) in enumerate(pos):
        orbes.append(dibujar_fuente(lz, cam, x, z, niebla, rota=i == rota, fase=fase))
    # los que le pegan a una fuente
    fx, fz = pos[0]
    for dx, dz in ((2.4, -0.4), (-1.0, -2.4), (1.4, -2.0)):
        jugador_a(lz, cam, fx + dx, fz + dz, fx, fz, niebla=niebla, pose_=jugador_pose(golpe=True))
    jugador_a(lz, cam, pos[2][0] - 2.0, pos[2][1] - 2.2, *pos[2], niebla=niebla, pose_=jugador_pose(corre=True))
    p = pose('FUENTES')
    M = caballero(lz, cam, 0, cz, 6, p, V, fase, niebla, con_espada=False)
    espada_clavada(lz, cam, M, 0, -30, V, fase, niebla, inclina=0.0)
    fuego_cuerpo(lz, cam, M, V, p, fase, espada=False)
    pecho = mundo_de(M, V, p, 'torso', (0, -33, -12))
    brillo_en(lz, cam, pecho, 2.4, color_fase(fase), 0.6)
    # el sol que va creciendo encima de el
    cima = punto(M, (0, -96, 0)) + np.array([0, 5.0, 0])
    sol_mini(lz, cam, cima, 2.2, fase, 9, 1.0)
    estela(lz, cam, [pecho + (cima - pecho) * t for t in np.linspace(0, 1, 8)], 0.3, fase, 0.6)
    for i, o in enumerate(orbes):
        if i == rota:
            explosion(lz, cam, (pos[i][0], 3.4, pos[i][1]), 1.0, fase, 3, lava=False, k=0.45)
            continue
        sol_mini(lz, cam, o, 0.7, fase, 20 + i, 0.8)
        mid = (o + cima) / 2 + np.array([0, 2.5, 0])
        pts = [(1 - t) ** 2 * o + 2 * (1 - t) * t * mid + t ** 2 * cima for t in np.linspace(0, 1, 20)]
        estela(lz, cam, pts, 0.28, fase, 0.75)
    img = componer(lz, cam, W, H, fase, sol=False)
    guardar(img, 'fuentes')


def trompetas(W=1600, H=900, fase=2):
    cam = vr.Camara(ojo=(-18.0, 11.0, -22.0), objetivo=(0.0, 3.6, 3.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(26, 60)
    suelo(lz, cam, niebla, fase)
    cz = 3.0
    R = 11.5
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    nota = tex_nota(pri)
    p = pose('REPOSO')
    p['cabeza'] = {'rot': (-12, 0, 0)}
    M = caballero(lz, cam, 0, cz, 0, p, V, fase, niebla)
    fuego_cuerpo(lz, cam, M, V, p, fase)
    pecho = mundo_de(M, V, p, 'torso', (0, -40, -10))
    rota = 2
    for i, a in enumerate((225, 315, 45, 135)):
        x, z = math.cos(math.radians(a)) * R, cz + math.sin(math.radians(a)) * R
        g = guinada_hacia(x, z, 0, cz)
        Me = dibujar_estatua(lz, cam, x, z, g + 180, niebla, rota=i == rota, fase=fase)
        if i == rota:
            continue
        boca = (Me @ np.array([0, -64, -34, 1.0]))[:3]
        brillo_en(lz, cam, boca, 1.0, pri, 0.5)
        mid = (boca + pecho) / 2 + np.array([0, 4.5, 0])
        r = random.Random(i)
        for t in np.linspace(0.06, 0.94, 10):
            q = (1 - t) ** 2 * boca + 2 * (1 - t) * t * mid + t ** 2 * pecho
            q = q + np.array([0, math.sin(t * 9 + i) * 0.5, 0])
            aditivo(lz, cam, [billboard(q, 0.6 + 0.2 * r.random(), cam, r.uniform(-0.3, 0.3))], nota, 0.9)
    # los que rompen una estatua
    for ang, dd in ((225, ((2.4, 0.6), (0.6, 2.4))), (315, ((-2.3, 1.2),))):
        x, z = math.cos(math.radians(ang)) * R, cz + math.sin(math.radians(ang)) * R
        for dx, dz in dd:
            jugador_a(lz, cam, x + dx, z + dz, x, z, niebla=niebla, pose_=jugador_pose(golpe=True))
    jugador_a(lz, cam, -2.0, -4.0, 6.0, -6.0, niebla=niebla, pose_=jugador_pose(corre=True))
    img = componer(lz, cam, W, H, fase, sol=False)
    guardar(img, 'trompetas')


def ofrenda(W=1600, H=900, fase=3):
    cz = 5.0
    p = pose('OFRENDA')
    M = fm.entidad_a_mundo(0, 0, cz, 12)
    mi = mundo_de(M, V, p, 'mano_izq', (0, 6, 0))
    md = mundo_de(M, V, p, 'mano_der', (0, 6, 0))
    cintura = (mi + md) / 2 + np.array([0, 0.35, 0])
    cam = vr.Camara(ojo=(-15.0, 4.0, -7.0), objetivo=tuple(cintura * 0.5 + punto(M, (0, -40, 0)) * 0.5), fov=56,
                    ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(22, 60)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase)
    caballero(lz, cam, 0, cz, 12, p, V, fase, niebla, con_espada=False)
    espada_clavada(lz, cam, M, -40, -6, V, fase, niebla, inclina=10.0, giro=20)
    fuego_cuerpo(lz, cam, M, V, p, fase, espada=False)
    # el ofrecido, de espaldas a el y de cara al sol, pataleando
    g = 12
    Mj = vr.T(cintura[0], cintura[1] - 0.75, cintura[2]) @ vr.Ry(math.radians(g)) @ vr.T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {'bi': {'rot': (-150, 0, -30)}, 'bd': {'rot': (-30, 0, 40)},
                                                 'pi': {'rot': (30, 0, -10)}, 'pd': {'rot': (-25, 0, 10)}}, Mj), LUCES, AMB, niebla)
    for (x, z) in ((-5.5, -1.0), (4.5, -2.5), (1.2, -5.0)):
        jugador_a(lz, cam, x, z, 0, cz, niebla=niebla, pose_=jugador_pose(golpe=x > 0))
    global SOL
    viejo = SOL
    SOL = sol_en_pantalla(cam, 0.3, 0.05, 140)
    # el haz del sol sobre el que ofrece (mientras, no recibe dano: como en los ataques de los otros jefes)
    estela(lz, cam, [SOL + (cintura + np.array([0, 0.6, 0]) - SOL) * t for t in np.linspace(0.75, 1.0, 10)], 0.5, fase, 0.55)
    brillo_en(lz, cam, cintura + np.array([0, 0.6, 0]), 1.8, color_fase(fase), 0.45)
    img = componer(lz, cam, W, H, fase)
    SOL = viejo
    guardar(img, 'ofrenda')


def ofrenda_pov(W=854, H=480, fase=3):
    """La pantalla del que esta en sus manos: la camara se aleja un poco (como con F5)
    para que se vea que le tiene; delante, el sol."""
    cz = 5.0
    p = pose('OFRENDA')
    M = fm.entidad_a_mundo(0, 0, cz, 12)
    mi = mundo_de(M, V, p, 'mano_izq', (0, 6, 0))
    md = mundo_de(M, V, p, 'mano_der', (0, 6, 0))
    cintura = (mi + md) / 2 + np.array([0, 0.35, 0])
    fwd = punto(M, (0, 0, -100)) - punto(M, (0, 0, 0))
    fwd = fwd / np.linalg.norm(fwd)
    lado = np.cross(fwd, [0, 1.0, 0])
    ojo = cintura - fwd * 4.2 + np.array([0, 2.2, 0]) + lado * 1.2
    obj = cintura + fwd * 6 + np.array([0, 0.6, 0])
    cam = vr.Camara(ojo=tuple(ojo), objetivo=tuple(obj), fov=64, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(22, 60)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase, cerca=4)
    for (x, z) in ((-5.5, -1.0), (4.5, -2.5), (1.2, -5.0), (-1.0, -9.0)):
        jugador_a(lz, cam, x, z, 0, cz, niebla=niebla)
    caballero(lz, cam, 0, cz, 12, p, V, fase, niebla, con_espada=False)
    fuego_cuerpo(lz, cam, M, V, p, fase, espada=False, k=0.6)
    Mj = vr.T(cintura[0], cintura[1] - 0.75, cintura[2]) @ vr.Ry(math.radians(12)) @ vr.T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {'bi': {'rot': (-150, 0, -30)}, 'bd': {'rot': (-30, 0, 40)},
                                                 'pi': {'rot': (30, 0, -10)}, 'pd': {'rot': (-25, 0, 10)}}, Mj), LUCES, AMB, niebla)
    global SOL
    viejo = SOL
    SOL = sol_en_pantalla(cam, 0.62, 0.12, 140)
    img = componer(lz, cam, W, H, fase, n_brasas=90)
    SOL = viejo
    guardar(img, 'ofrenda_pov_base')


def dios(W=1600, H=900, fase=4):
    cam = vr.Camara(ojo=(-18.0, 9.0, -22.0), objetivo=(0.0, 4.4, 4.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(26, 60)
    niebla.color = (0.35, 0.06, 0.05)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase)
    cz = 6.0
    zonas = [(-9.0, -3.0), (7.5, -5.0), (10.0, 10.0)]
    for (x, z) in zonas:
        sello(lz, cam, x, z, 4.2, fase, 80, 0.8, 0.4)
    jugador_a(lz, cam, -9.0 - 5.0, -3.0 - 2.0, 0, cz, niebla=niebla, pose_=jugador_pose(corre=True), extra=120)
    jugador_volando(lz, cam, (-9.4, 0.8, -2.0), 40, -50, niebla, jugador_pose(brazos_arriba=True))
    jugador_a(lz, cam, 7.0, -4.2, 0, cz, niebla=niebla, pose_=jugador_pose(corre=True), extra=180)
    jugador_a(lz, cam, 2.5, -6.5, 0, cz, niebla=niebla, pose_=jugador_pose(golpe=True))
    p = pose('DIOS')
    M = caballero(lz, cam, 0, cz, 8, p, V, fase, niebla, con_espada=False)
    espada_clavada(lz, cam, M, 0, -26, V, fase, niebla, inclina=0.0)
    aura(lz, cam, M, V, p, fase, 170, 4, (0.6, 1.5), 0.42, con_espada=False)
    fuego_cuerpo(lz, cam, M, V, p, fase, espada=False, k=0.7)
    for lado in ('izq', 'der'):
        sol_mini(lz, cam, mundo_de(M, V, p, 'mano_' + lado, (0, 6, 0)) + np.array([0, 1.3, 0]), 0.75, fase, 31)
    # zona 1: la cadena de explosiones; zona 2: los soles que caen; zona 3: el aviso
    r = random.Random(5)
    x, z = zonas[0]
    for i in range(5):
        a = r.uniform(0, TAU)
        d = r.uniform(0, 2.6)
        explosion(lz, cam, (x + math.cos(a) * d, 0.1, z + math.sin(a) * d), r.uniform(1.4, 2.2), fase, 40 + i, lava=i < 2, k=0.7)
    x, z = zonas[1]
    for i in range(3):
        q = np.array([x + r.uniform(-2, 2), 5.0 + i * 3.2, z + r.uniform(-2, 2)])
        estela(lz, cam, [q + np.array([0, 3.0 * t, 0]) for t in np.linspace(0, 1, 6)], 0.3, fase, 0.5)
        sol_mini(lz, cam, q, 0.6, fase, 50 + i, 0.9)
    img = componer(lz, cam, W, H, fase)
    guardar(img, 'dios')


def furia(W=1600, H=900):
    fase = 'furia'
    cam = vr.Camara(ojo=(-9.0, 1.8, -14.5), objetivo=(0.6, 6.2, 4.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(18, 70)
    niebla.color = (0.16, 0.14, 0.26)
    suelo(lz, cam, niebla, fase)
    braseros(lz, cam, niebla, fase)
    for (x, z) in JUGADORES_HEROICA:
        jugador_a(lz, cam, x, z, 0, 4, niebla=niebla)
    p = pose('GRITO')
    M = caballero(lz, cam, 0, 4, 22, p, V, fase, niebla)
    aura(lz, cam, M, V, p, fase, 260, 8, (0.6, 1.7), 0.8)
    fuego_cuerpo(lz, cam, M, V, p, fase)
    global SOL
    viejo = SOL
    SOL = sol_en_pantalla(cam, 0.8, 0.14, 120)
    img = componer(lz, cam, W, H, fase)
    SOL = viejo
    guardar(img, 'furia')


def prueba_rodilla(W=500, H=600):
    ims = []
    for n, g in (('CASTIGO_CLAVA', -90), ('CASTIGO_CLAVA', -30), ('OFRENDA', -90), ('OFRENDA', -20), ('SOL', -30), ('BARRIDO', -30)):
        cam = vr.Camara(ojo=(0, 6.0, -62), objetivo=(0, 5.6, 0), fov=12.5, ancho=W * SS, alto=H * SS)
        lz = Lienzo(W * SS, H * SS)
        p = pose(n)
        M = caballero(lz, cam, 0, 0, g, p, V, 1, None, LUZ_ESTUDIO, AMB_ESTUDIO, 1.2, con_espada=n not in POSES_SIN_ESPADA)
        if n in ('CASTIGO_CLAVA', 'FUENTES'):
            espada_clavada(lz, cam, M, 0, -30, V, 1, None, inclina=0.0)
        if n == 'OFRENDA':
            espada_clavada(lz, cam, M, -40, -6, V, 1, None, inclina=10.0, giro=20)
        ims.append(estudio(lz, W, H))
    img = Image.new('RGB', (W * len(ims), H))
    for i, im in enumerate(ims):
        img.paste(im, (i * W, 0))
    guardar(img, 'prueba_rodilla')


def antes_despues(W=1800, H=900):
    """La A de la ronda 1 y Novilis, a la misma escala y con la misma luz."""
    img = Image.new('RGB', (W, H), (237, 238, 240))
    w = W // 2
    for i, v in enumerate(('A', 'N')):
        cam = vr.Camara(ojo=(-17, 7.4, -70), objetivo=(0, 7.0, 0), fov=12.6, ancho=w * SS, alto=(H - 70) * SS)
        lz = Lienzo(w * SS, (H - 70) * SS)
        caballero(lz, cam, 0, 0, -18, pose('REPOSO'), v, 1, None, LUZ_ESTUDIO, AMB_ESTUDIO, 1.25)
        img.paste(estudio(lz, w, H - 70, fondo=(0.93, 0.935, 0.945)), (i * w, 0))
        rotulo(img, ('ANTES · RONDA 1 (A)', 'NOVILIS · RONDA 2')[i], i * w + w / 2, H - 62, 34, centro=True)
    guardar(img, 'antes_despues')


ESCENAS = {
    'prueba_poses': prueba_poses, 'prueba_rodilla': prueba_rodilla,
    'heroica_A': lambda: heroica('A'), 'heroica_B': lambda: heroica('B'), 'heroica_C': lambda: heroica('C'), 'heroica_N': lambda: heroica('N'),
    'opciones': opciones, 'antes_despues': antes_despues, 'vistas': vistas, 'fases': fases, 'escala': escala,
    'barrido': barrido, 'castigo_rayos': castigo_rayos, 'castigo_onda': castigo_onda, 'sol': esc_sol,
    'fuentes': fuentes, 'trompetas': trompetas, 'ofrenda': ofrenda, 'ofrenda_pov': ofrenda_pov,
    'dios': dios, 'furia': furia,
}


if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else [k for k in ESCENAS if not k.startswith('prueba')]
    for k in pedidas:
        ESCENAS[k]()

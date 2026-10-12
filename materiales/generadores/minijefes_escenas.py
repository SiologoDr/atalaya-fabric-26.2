"""
Renders de los bocetos de los cuatro mini jefes (minijefes_modelo) para su ficha
de diseno: por cada uno, la escena heroica, las vistas (frente, perfil y
espalda) y sus tres ataques -normal, de area y especial- con sus efectos; y la
escala, los cuatro junto a un jugador.

Cada uno en su sitio:
  - Moctezuma: una plaza azteca al atardecer, con su piramide y braseros.
  - Yiatzo: una cumbre en plena tormenta, con rocas que flotan.
  - Atlahua: ruinas en el fondo del mar, con rayos de luz y nieve marina.
  - Xiuhquetzal: ruinas volcanicas de noche, con grietas de lava y ascuas.

En las escenas de ataque se pinta primero lo opaco (suelo, ruinas, mallas,
jugadores) y al final lo que brilla sumado (estelas, ondas, llamas, chispas),
para que el brillo no atraviese a nadie.

Uso: python minijefes_escenas.py <raiz del proyecto> <carpeta de salida> [nombre o escena,...]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne
import minijefes_modelo as mj

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
SS = 2
_hex = nm._hex
UV4 = [(0, 0), (1, 0), (1, 1), (0, 1)]


# ----------------------------------------------------------------------
#  Texturas de efectos (RGBA, la alfa es la fuerza)
# ----------------------------------------------------------------------
def _rgba(color, alfa):
    h, w = alfa.shape
    t = np.zeros((h, w, 4), np.uint8)
    t[..., :3] = color
    t[..., 3] = np.clip(alfa * 255, 0, 255).astype(np.uint8)
    return t


def tex_brillo(n=64, color=(255, 255, 255), k=2.2):
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2) / (n / 2)
    return _rgba(color, np.clip(1 - d, 0, 1) ** k)


def tex_aro(n=256, color=(255, 255, 255), radio=0.84, grosor=0.05, halo=0.16):
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2) / (n / 2)
    a = np.exp(-((d - radio) / grosor) ** 2) + 0.4 * np.exp(-((d - radio) / halo) ** 2) * (d < radio)
    return _rgba(color, np.clip(a, 0, 1) * (d < 1))


def tex_estela(w=256, h=48, c1=(255, 255, 255), c2=(120, 200, 255), cola=1.4):
    """Una estela: nace en u=0 y se apaga; caliente (c1) en el centro, c2 en los bordes."""
    v, u = np.mgrid[0:h, 0:w]
    u, v = u / (w - 1), v / (h - 1)
    centro = np.exp(-((v - 0.5) / 0.12) ** 2)
    borde = np.exp(-((v - 0.5) / 0.3) ** 2)
    a = (1 - u) ** cola * borde
    col = np.array(c2)[None, None, :] * (1 - centro[..., None]) + np.array(c1)[None, None, :] * centro[..., None]
    t = np.zeros((h, w, 4), np.uint8)
    t[..., :3] = np.clip(col, 0, 255)
    t[..., 3] = np.clip(a * 255, 0, 255)
    return t


def tex_viento(w=256, h=64, color=(200, 245, 255), semilla=1, n=14):
    """Rafagas: hilos finos de aire de distintos largos."""
    r = random.Random(semilla)
    capa = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(capa)
    for _ in range(n):
        y = r.uniform(0.1, 0.9) * h
        x0 = r.uniform(0, 0.5) * w
        x1 = x0 + r.uniform(0.3, 0.6) * w
        d.line((x0, y, x1, y), fill=r.randint(120, 255), width=r.choice([1, 1, 2]))
    a = np.array(capa.filter(ImageFilter.GaussianBlur(1.2))).astype(float) / 255
    u = np.linspace(0, 1, w)[None, :]
    a = a * np.sin(np.pi * u) ** 0.6
    return _rgba(color, a * 0.9)


def tex_media_luna(n=128, color=(220, 250, 255)):
    """Una cuchilla de aire: media luna con el filo brillante."""
    yy, xx = np.mgrid[0:n, 0:n]
    x, y = (xx - (n - 1) / 2) / (n / 2), (yy - (n - 1) / 2) / (n / 2)
    d1 = np.hypot(x, y)
    d2 = np.hypot(x + 0.3, y)
    a = np.clip((1 - d1) * 6, 0, 1) * np.clip((d2 - 0.78) * 6, 0, 1)
    return _rgba(color, a)


def tex_llama(w=48, h=96, cols=((255, 250, 210), (255, 190, 60), (255, 90, 20), (180, 20, 30)), semilla=1):
    """Una llama: la punta arriba; caliente y blanca dentro, roja en el borde."""
    r = np.random.default_rng(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    ruido = r.uniform(-1, 1, h)
    ruido = np.convolve(ruido, np.ones(9) / 9, 'same')
    for y in range(h):
        v = y / (h - 1)
        ancho = 0.48 * math.sin(math.pi * min(1.0, v * 1.05)) ** 0.7 * (0.55 + 0.45 * v)
        cx = 0.5 + ruido[y] * 0.12 * (1 - v)
        for x in range(w):
            u = x / (w - 1)
            d = abs(u - cx) / max(ancho, 1e-3)
            if d > 1:
                continue
            k = d * 0.8 + (1 - v) * 0.5
            idx = min(len(cols) - 1.001, k * (len(cols) - 1))
            i = int(idx)
            f = idx - i
            c = [cols[i][j] + (cols[i + 1][j] - cols[i][j]) * f for j in range(3)]
            t[y, x] = (*[int(q) for q in c], int(255 * (1 - d ** 2) * min(1.0, v * 3)))
    return t


def tex_grietas(n=256, color=(120, 255, 170), semilla=2, ramas=14):
    """Grietas que salen del centro, con el brillo de lo que hay debajo."""
    r = random.Random(semilla)
    capa = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(capa)
    c = n / 2
    for k in range(ramas):
        a = k / ramas * 2 * math.pi + r.uniform(-0.2, 0.2)
        x, y = c, c
        largo = r.uniform(0.6, 0.95) * c
        pasos = 9
        for i in range(pasos):
            a += r.uniform(-0.45, 0.45)
            nx, ny = x + math.cos(a) * largo / pasos, y + math.sin(a) * largo / pasos
            d.line((x, y, nx, ny), fill=255, width=max(1, int(5 * (1 - i / pasos))))
            x, y = nx, ny
            if r.random() < 0.25:
                b = a + r.choice([-1, 1]) * 0.8
                d.line((x, y, x + math.cos(b) * largo / 6, y + math.sin(b) * largo / 6), fill=200, width=1)
    nitida = np.array(capa).astype(float) / 255
    halo = np.array(capa.filter(ImageFilter.GaussianBlur(n / 60))).astype(float) / 255
    return _rgba(color, np.clip(nitida + halo * 1.5, 0, 1))


def tex_agua(n=128, semilla=3):
    """Agua translucida con el dibujo de la luz (causticas)."""
    yy, xx = np.mgrid[0:n, 0:n] / n * 2 * math.pi
    c = np.abs(np.sin(xx * 3 + np.sin(yy * 2) * 1.5) * np.sin(yy * 3 + np.sin(xx * 2) * 1.5))
    c = c ** 3
    t = np.zeros((n, n, 4), np.uint8)
    base = np.array([30, 120, 150])
    t[..., :3] = np.clip(base + c[..., None] * np.array([140, 140, 100]), 0, 255)
    t[..., 3] = 255
    return t


def tex_espuma(w=256, h=32, semilla=4):
    """La cresta de una ola: espuma blanca rota."""
    r = np.random.default_rng(semilla)
    v, u = np.mgrid[0:h, 0:w]
    v = v / (h - 1)
    ruido = np.convolve(r.uniform(0, 1, w), np.ones(7) / 7, 'same')[None, :]
    a = np.clip(1 - np.abs(v - 0.5) * 2.4 + (ruido - 0.5) * 0.8, 0, 1)
    return _rgba((235, 255, 255), a)


T_BRILLO = tex_brillo()
T_JADE = tex_brillo(color=(90, 255, 160))
T_VIOLETA = tex_brillo(color=(190, 90, 255))
T_CIAN = tex_brillo(color=(110, 230, 255))
T_FUEGO = tex_brillo(color=(255, 140, 40))
T_ROSA = tex_brillo(color=(255, 90, 200))
T_LISO_JADE = _rgba((90, 255, 160), np.ones((8, 8)))
T_ARO_JADE = tex_aro(color=(110, 255, 170))
T_ARO_CIAN = tex_aro(color=(150, 240, 255))
T_ARO_FUEGO = tex_aro(color=(255, 110, 40), grosor=0.07)
T_ARO_VIOLETA = tex_aro(color=(200, 100, 255), grosor=0.06)
T_ESTELA_OBSIDIANA = tex_estela(c1=(220, 170, 255), c2=(110, 40, 200))
T_ESTELA_JADE = tex_estela(c1=(220, 255, 230), c2=(60, 220, 130))
T_ESTELA_AGUA = tex_estela(c1=(230, 255, 255), c2=(60, 180, 255))
T_ESTELA_FUEGO = tex_estela(c1=(255, 240, 180), c2=(255, 80, 20), cola=1.0)
T_ESTELA_VIOLETA = tex_estela(c1=(255, 200, 255), c2=(160, 40, 255), cola=1.0)
T_VIENTO = [tex_viento(semilla=k) for k in range(4)]
T_LUNA = tex_media_luna()
T_LLAMAS = [tex_llama(semilla=k) for k in range(4)]
T_LLAMAS_V = [tex_llama(cols=((255, 230, 255), (240, 120, 255), (170, 40, 230), (80, 10, 140)), semilla=10 + k)
              for k in range(3)]
T_GRIETAS_JADE = tex_grietas()
T_GRIETAS_LAVA = tex_grietas(color=(255, 120, 30), semilla=5, ramas=18)
T_AGUA = tex_agua()
T_ESPUMA = tex_espuma()


# ----------------------------------------------------------------------
#  Primitivas de dibujo
# ----------------------------------------------------------------------
def quad(lz, cam, P, tex, aditivo=True, brillo=1.0, translucido=0.0, uv=UV4, luz=None, niebla=None):
    luz = np.ones(3) if luz is None else luz
    P = [np.asarray(p, float) for p in P]
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [uv[i] for i in tri], tex, luz, None, niebla, aditivo=aditivo,
                     brillo=brillo, translucido=translucido)


def billboard(lz, cam, c, w, h, tex, giro=0.0, **kw):
    c = np.asarray(c, float)
    cg, sg = math.cos(giro), math.sin(giro)
    r = cam.r * cg + cam.u * sg
    u = -cam.r * sg + cam.u * cg
    quad(lz, cam, [c - r * w / 2 + u * h / 2, c + r * w / 2 + u * h / 2, c + r * w / 2 - u * h / 2,
                   c - r * w / 2 - u * h / 2], tex, **kw)


def horizontal(lz, cam, c, rx, rz, tex, giro=0.0, **kw):
    c = np.asarray(c, float)
    cg, sg = math.cos(giro), math.sin(giro)
    ex, ez = np.array([cg, 0, sg]) * rx, np.array([-sg, 0, cg]) * rz
    quad(lz, cam, [c - ex - ez, c + ex - ez, c + ex + ez, c - ex + ez], tex, **kw)


def cinta3d(lz, cam, pts, anchos, tex, normal=None, **kw):
    """Una banda a lo largo de una linea 3D; mira a la camara salvo que se le de la normal del plano."""
    pts = [np.asarray(p, float) for p in pts]
    n = len(pts)
    lados = []
    for i in range(n):
        t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        t /= np.linalg.norm(t) + 1e-9
        ref = np.asarray(normal, float) if normal is not None else (cam.ojo - pts[i])
        lado = np.cross(t, ref)
        lado /= np.linalg.norm(lado) + 1e-9
        lados.append(lado)
    for i in range(n - 1):
        a0, a1 = anchos[i] / 2, anchos[i + 1] / 2
        u0, u1 = i / (n - 1), (i + 1) / (n - 1)
        P = [pts[i] - lados[i] * a0, pts[i + 1] - lados[i + 1] * a1, pts[i + 1] + lados[i + 1] * a1, pts[i] + lados[i] * a0]
        quad(lz, cam, P, tex, uv=[(u0, 0), (u1, 0), (u1, 1), (u0, 1)], **kw)


def arco(c, radio, a0, a1, n=24, y=0.0, inclina=0.0, eje='y'):
    """Puntos de un arco de circunferencia (en el plano horizontal, o inclinado)."""
    out = []
    for k in range(n):
        a = a0 + (a1 - a0) * k / (n - 1)
        p = np.array([math.cos(a) * radio, y + math.sin(a) * radio * math.sin(inclina), math.sin(a) * radio * math.cos(inclina)])
        out.append(np.asarray(c, float) + p)
    return out


def espiral(c, r0, r1, alto, vueltas, n=60, fase=0.0):
    out = []
    for k in range(n):
        t = k / (n - 1)
        a = fase + t * vueltas * 2 * math.pi
        rr = r0 + (r1 - r0) * t
        out.append(np.asarray(c, float) + np.array([math.cos(a) * rr, t * alto, math.sin(a) * rr]))
    return out


# ----------------------------------------------------------------------
#  El mundo: suelos, cajas y modelos
# ----------------------------------------------------------------------
def _losa(x, y, r):
    R = nm._rampa('4a463c', '5e584a', '726a58', '867c66', '9a8f76')
    if x % 8 == 0 or y % 8 == 0:
        return R[0]
    if r.random() < 0.07:
        return nm._hex('4a6a3a')
    return R[r.choice([1, 2, 2, 3, 3, 4])]


def _piedra_templo(x, y, r):
    R = nm._rampa('3e3a32', '544e42', '6a6252', '807662')
    if y % 8 == 0:
        return R[0]
    return R[r.choice([1, 2, 2, 3])]


def _roca(x, y, r):
    R = nm._rampa('2e3238', '3e444c', '50575f', '646c75', '7c858e')
    if x % 8 == 0 or y % 8 == 0:
        return R[1]
    if r.random() < 0.02:
        return nm._hex('dfe8ee')
    return R[2 + ((x // 3 + y // 3 * 2) % 3 == 0)] if r.random() < 0.85 else R[r.choice([1, 3])]


def _nieve(x, y, r):
    return nm._rampa('c8d2dc', 'dce4ec', 'eef3f8')[r.choice([0, 1, 2, 2])]


def _arena(x, y, r):
    R = nm._rampa('2a3a40', '34484e', '3e565a', '4a6466')
    return R[2] if r.random() < 0.7 else R[r.choice([1, 3])]


def _ruina_marina(x, y, r):
    R = nm._rampa('16242c', '1e323c', '284450', '325666')
    if x % 8 == 0 or y % 8 == 0:
        return R[0]
    return R[r.choice([1, 2, 2, 3])] if r.random() > 0.06 else nm._hex('3a7a50')


def _basalto(x, y, r):
    R = nm._rampa('120e10', '1c1618', '262022', '302a2a')
    return R[r.choice([0, 1, 1, 2, 3])]


def _basalto_lava():
    r = random.Random(77)
    t = np.zeros((16, 16, 4), np.uint8)
    e = np.zeros((16, 16, 4), np.uint8)
    R = nm._rampa('120e10', '1c1618', '262022', '302a2a')
    for y in range(16):
        for x in range(16):
            t[y, x] = (*R[r.choice([0, 1, 1, 2, 3])], 255)
    for _ in range(3):
        x, y = r.randint(0, 15), r.randint(0, 15)
        for k in range(10):
            t[y % 16, x % 16] = (255, 120, 30, 255)
            e[y % 16, x % 16] = (255, 140, 40, 255)
            x += r.choice([-1, 0, 1, 1])
            y += r.choice([-1, 0, 1])
    return t, e


ENV = {
    'losa': nm._loseta(601, _losa),
    'templo': nm._loseta(602, _piedra_templo),
    'roca': nm._loseta(603, _roca),
    'nieve': nm._loseta(604, _nieve),
    'arena': nm._loseta(605, _arena),
    'ruina': nm._loseta(606, _ruina_marina),
    'basalto': nm._loseta(607, _basalto),
    'basalto_lava': _basalto_lava(),
}


def camara(ojo, objetivo, fov, ancho, alto, k=1.36):
    """Como vr.Camara, pero apartada de su objetivo lo que han crecido los mini jefes (dos bloques mas: x1,36) y
    mirando un poco mas arriba, para que el encuadre siga igual."""
    o = np.array(objetivo, float)
    o[1] *= 1.28
    e = o + (np.array(ojo, float) - np.array(objetivo, float)) * k
    e[1] = max(e[1], 0.35)
    return vr.Camara(ojo=tuple(e), objetivo=tuple(o), fov=fov, ancho=ancho, alto=alto)


def caja(x, y, z, w, h, d, mat):
    """Una caja en bloques de mundo (y hacia arriba), como quads."""
    raiz = nm.nodo('c', (0, 0, 0), (0, 0, 0), [((0, -h * 16, 0, w * 16, h * 16, d * 16), mat)])
    return nm.quads(raiz, {}, vr.T(x, y, z) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1]))


def caja_girada(x, y, z, w, h, d, mat, rx=0.0, ry=0.0, rz=0.0):
    raiz = nm.nodo('c', (0, 0, 0), (rx, ry, rz), [((-w * 8, -h * 8, -d * 8, w * 16, h * 16, d * 16), mat)])
    return nm.quads(raiz, {}, vr.T(x, y, z) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1]))


def suelo(mat, x0, x1, z0, z1, k=1.0, y=0.0):
    qs = []
    for gx in range(x0, x1):
        for gz in range(z0, z1):
            qs.append(([(gx, y, gz), (gx + 1, y, gz), (gx + 1, y, gz + 1), (gx, y, gz + 1)],
                       [(gx / k, gz / k), ((gx + 1) / k, gz / k), ((gx + 1) / k, (gz + 1) / k), (gx / k, (gz + 1) / k)], mat))
    return qs


def dibujar_mundo(lz, cam, qs, luces, amb, niebla=None, brillo=1.3):
    for P, UV, mat in qs:
        tex = ENV.get(mat) if mat in ENV else (mj.MAT.get(mat) if mat in mj.MAT else nm.MAT[mat])
        emis = None
        if isinstance(tex, tuple):
            tex, emis = tex
        luz = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla, brillo=brillo, envolver=True)


def minijefe(lz, cam, nombre, x, z, guinada, pose=None, luces=None, amb=(0.3, 0.3, 0.34), niebla=None, y=0.0,
             brillo=1.4, escala=1.0):
    hacer, reposo, _ = mj.MINIJEFES[nombre]
    M = mj.entidad_a_mundo(x, y, z, guinada, escala * mj.ESCALA[nombre])
    mj.dibujar(lz, cam, mj.quads(hacer(), reposo if pose is None else pose, M), luces or LUCES_ESTUDIO, amb, niebla, brillo)


def hacia(desde, a):
    """La guinada para que un modelo en 'desde' (x, z) mire hacia 'a' (x, z)."""
    return math.degrees(math.atan2(-(a[0] - desde[0]), -(a[1] - desde[1])))


def punto(nombre, x, z, guinada, pose, mat, y=0.0):
    """Donde queda en el mundo una pieza del modelo (el centro de sus caras de ese material)."""
    hacer, _, _ = mj.MINIJEFES[nombre]
    M = mj.entidad_a_mundo(x, y, z, guinada, mj.ESCALA[nombre])
    pts = [np.mean(q[0], axis=0) for q in mj.quads(hacer(), pose, M) if q[2] == mat]
    return np.mean(pts, axis=0)


def tex_nube(n=64, color=(170, 185, 200), semilla=5):
    r = np.random.default_rng(semilla)
    base = r.uniform(0, 1, (n // 8, n // 8))
    img = Image.fromarray((base * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
    a = np.array(img).astype(float) / 255
    t = np.zeros((n, n, 4), np.uint8)
    t[..., :3] = np.clip(np.array(color)[None, None, :] * (0.6 + 0.5 * a[..., None]), 0, 255)
    t[..., 3] = 255
    return t


T_NUBE = tex_nube()


def embudo(lz, cam, c, r0, r1, alto, n=24, capas=8, translucido=0.22, giro=0.0):
    """El cuerpo de un torbellino: un cono de nube translucida, mas ancho arriba."""
    c = np.asarray(c, float)
    for j in range(capas):
        h0, h1 = j / capas, (j + 1) / capas
        ra, rb = r0 + (r1 - r0) * h0, r0 + (r1 - r0) * h1
        for k in range(n):
            a0 = giro + k / n * 2 * math.pi + h0 * 1.5
            a1 = giro + (k + 1) / n * 2 * math.pi + h0 * 1.5
            P = [c + [math.cos(a0) * ra, h0 * alto, math.sin(a0) * ra], c + [math.cos(a1) * ra, h0 * alto, math.sin(a1) * ra],
                 c + [math.cos(a1 + 0.2) * rb, h1 * alto, math.sin(a1 + 0.2) * rb], c + [math.cos(a0 + 0.2) * rb, h1 * alto, math.sin(a0 + 0.2) * rb]]
            quad(lz, cam, P, T_NUBE, aditivo=False, translucido=translucido,
                 uv=[(k / 4, h0 * 2), ((k + 1) / 4, h0 * 2), ((k + 1) / 4, h1 * 2), (k / 4, h1 * 2)])


def fantasma(lz, cam, nombre, x, z, guinada, pose, tex, y=0.0, brillo=0.5):
    """La silueta del mini jefe en luz (la estela de una embestida): sus caras sumadas con un solo color."""
    hacer, _, _ = mj.MINIJEFES[nombre]
    M = mj.entidad_a_mundo(x, y, z, guinada, mj.ESCALA[nombre])
    for q in mj.quads(hacer(), pose, M):
        quad(lz, cam, q[0], tex, aditivo=False, translucido=brillo, uv=UV4)


def jugador(lz, cam, x, z, guinada, y=0.0, luces=None, amb=(0.3, 0.3, 0.34), niebla=None, pose=None):
    M = vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, guinada)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), pose or {}, M), luces or LUCES_ESTUDIO, amb, niebla)


LUCES_ESTUDIO = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.8, 0.9, 1.0), 0.5, 'contra')]
JUGADOR_EMPUJADO = {'bi': {'rot': (-150, 0, -20)}, 'bd': {'rot': (-140, 0, 20)}, 'pi': {'rot': (30, 0, 0)},
                    'pd': {'rot': (-20, 0, 0)}, 'cuerpo': {'rot': (-20, 0, 0)}}


class Niebla:
    def __init__(self, color, ini=12.0, largo=40.0, tope=0.85):
        self.color, self.ini, self.largo, self.tope = color, ini, largo, tope

    def __call__(self, z):
        return np.clip((z - self.ini) / self.largo, 0, self.tope)


# ----------------------------------------------------------------------
#  Cielos y composicion
# ----------------------------------------------------------------------
def cielo(W, H, arriba, abajo, sol=None, nubes=0.0, semilla=1, color_nubes=(0.2, 0.22, 0.26)):
    y = np.linspace(0, 1, H)[:, None, None]
    col = np.array(arriba) + (np.array(abajo) - np.array(arriba)) * y ** 1.1
    col = np.broadcast_to(col, (H, W, 3)).copy()
    if sol:
        sx, sy, scol, sr = sol
        yy, xx = np.mgrid[0:H, 0:W]
        g = np.exp(-(((xx - W * sx) / (W * sr)) ** 2 + ((yy - H * sy) / (W * sr)) ** 2))
        col += g[..., None] * np.array(scol)
    if nubes:
        r = random.Random(semilla)
        capa = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(capa)
        for _ in range(60):
            cx, cy = r.uniform(-0.1, 1.1) * W, r.uniform(-0.1, 0.55) * H
            rr = r.uniform(0.04, 0.14) * W
            d.ellipse((cx - rr, cy - rr * 0.45, cx + rr, cy + rr * 0.45), fill=r.randint(90, 255))
        m = np.array(capa.filter(ImageFilter.GaussianBlur(W / 90))).astype(float)[..., None] / 255 * nubes
        col = col * (1 - m) + np.array(color_nubes) * m
    return np.clip(col, 0, 1)


def componer(lz, W, H, fondo, extra=None, vineta=0.5, bloom=((4, 0.75), (14, 0.55), (46, 0.4))):
    def baja(a):
        return np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    alfa = baja(lz.alfa)[..., None]
    col = baja(lz.color)
    emis = baja(lz.emis)
    arr = col * alfa + fondo * (1 - alfa)
    if extra is not None:
        arr = extra(arr)
    arr = ne.bloom(arr, emis, radios=bloom)
    arr = ne.vineta(arr, vineta)
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert('RGBA')


def particulas(img, n, zona, colores, semilla, tam=(1.5, 4.0), sube=0.0):
    """Motas y ascuas pintadas encima, con un halo suave."""
    r = random.Random(semilla)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    W = img.size[0]
    for _ in range(n):
        x, y = r.uniform(*zona[0]), r.uniform(*zona[1])
        rr = r.uniform(*tam) * W / 1600
        c = r.choice(colores)
        if sube:
            d.line((x, y, x + r.uniform(-2, 2), y + rr * sube), fill=(*c, r.randint(90, 200)), width=max(1, int(rr / 1.5)))
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(*c, r.randint(150, 255)))
    halo = capa.filter(ImageFilter.GaussianBlur(W / 400))
    img.alpha_composite(halo)
    img.alpha_composite(capa)


def nube_polvo(img, n, zona, semilla, color=(160, 140, 110), alfa=(40, 110)):
    r = random.Random(semilla)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for _ in range(n):
        x, y = r.uniform(*zona[0]), r.uniform(*zona[1])
        rr = r.uniform(20, 70) * img.size[0] / 1600
        d.ellipse((x - rr, y - rr * 0.6, x + rr, y + rr * 0.6), fill=(*color, r.randint(*alfa)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(img.size[0] / 160)))


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=91)
    print(nombre, flush=True)


# ======================================================================
#  MOCTEZUMA: la plaza azteca al atardecer
# ======================================================================
LUCES_PLAZA = [((-0.6, 0.7, -0.4), (1.0, 0.82, 0.55), 1.1, 'llave'), ((0.7, 0.35, 0.7), (0.4, 1.0, 0.6), 0.7, 'contra')]
AMB_PLAZA = (0.26, 0.26, 0.24)
NIEBLA_PLAZA = Niebla((0.82, 0.68, 0.48), 14, 46, 0.8)


def plaza():
    qs = suelo('losa', -26, 26, -12, 50)
    for k in range(7):                                   # la piramide del fondo
        w = 24 - k * 3.2
        qs += caja(-w / 2, k * 2.2, 34 - w / 2, w, 2.2, w, 'templo')
    qs += caja(-2.6, 0, 22.6, 5.2, 15.4, 3, 'templo')     # la escalinata
    for x in (-7, 7):                                     # los braseros
        qs += caja(x - 0.6, 0, 12 - 0.6, 1.2, 1.4, 1.2, 'templo')
        qs += caja(x - 0.9, 1.4, 12 - 0.9, 1.8, 0.4, 1.8, 'mj_oro')
    return qs


def fuegos_braseros(lz, cam, k=1.0):
    for x in (-7, 7):
        for i, t in enumerate(T_LLAMAS[:3]):
            billboard(lz, cam, (x + (i - 1) * 0.25, 2.5 + i * 0.1, 12), 1.0, 2.0, t, brillo=1.2 * k)
        billboard(lz, cam, (x, 2.3, 12), 3.0, 3.0, T_FUEGO, brillo=0.6 * k)


def fondo_plaza(W, H):
    return cielo(W, H, (0.32, 0.36, 0.42), (1.0, 0.72, 0.42), sol=(0.75, 0.55, (0.8, 0.5, 0.2), 0.2), nubes=0.35,
                 color_nubes=(0.55, 0.4, 0.36))


MOCTEZUMA_CORTE = {
    'pelvis': {'rot': (0, 30, 0)}, 'torso': {'rot': (6, -50, 0)}, 'cabeza': {'rot': (0, 30, 0)},
    'pierna_izq': {'rot': (-30, 0, -8)}, 'espinilla_izq': {'rot': (30, 0, 0)},
    'pierna_der': {'rot': (26, 0, 8)}, 'espinilla_der': {'rot': (14, 0, 0)}, 'pie_der': {'rot': (-24, 0, 0)},
    'hombro_der': {'rot': (-88, -60, 0)}, 'antebrazo_der': {'rot': (-8, 0, 0)}, 'macuahuitl': {'rot': (0, 0, 0)},
    'hombro_izq': {'rot': (-50, 30, -20)}, 'antebrazo_izq': {'rot': (-50, 0, 0)},
}
MOCTEZUMA_GOLPE = {
    'pelvis': {'pos': (0, 4, 0), 'rot': (14, 0, 0)}, 'torso': {'rot': (30, 0, 0)}, 'cabeza': {'rot': (-30, 0, 0)},
    'pierna_izq': {'rot': (-70, 0, -14)}, 'espinilla_izq': {'rot': (80, 0, 0)}, 'pie_izq': {'rot': (-24, 0, 0)},
    'pierna_der': {'rot': (-20, 0, 16)}, 'espinilla_der': {'rot': (90, 0, 0)}, 'pie_der': {'rot': (-60, 0, 0)},
    'hombro_izq': {'rot': (-60, 0, -10)}, 'antebrazo_izq': {'rot': (-10, 0, 0)},
    'hombro_der': {'rot': (-160, 20, 30)}, 'antebrazo_der': {'rot': (-30, 0, 0)}, 'macuahuitl': {'rot': (30, 0, 0)},
}
MOCTEZUMA_EMBESTIDA = {
    'pelvis': {'rot': (20, 0, 0)}, 'torso': {'rot': (20, 10, 0)}, 'cabeza': {'rot': (-30, 0, 0)},
    'pierna_izq': {'rot': (-70, 0, -4)}, 'espinilla_izq': {'rot': (70, 0, 0)},
    'pierna_der': {'rot': (40, 0, 4)}, 'espinilla_der': {'rot': (50, 0, 0)}, 'pie_der': {'rot': (-30, 0, 0)},
    'hombro_der': {'rot': (50, 0, 30)}, 'antebrazo_der': {'rot': (-20, 0, 0)}, 'macuahuitl': {'rot': (60, 0, 0)},
    'hombro_izq': {'rot': (-80, 0, -14)}, 'antebrazo_izq': {'rot': (-40, 0, 0)},
}


def moctezuma_heroica(W=1600, H=900):
    cam = camara(ojo=(-2.6, 0.7, -3.6), objetivo=(0.3, 2.3, 2.4), fov=50, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, plaza(), LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA)
    minijefe(lz, cam, 'moctezuma', 0.4, 2.4, 18, mj.MOCTEZUMA_HEROICA, LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA)
    fuegos_braseros(lz, cam)
    r = random.Random(3)
    for _ in range(40):                                  # la furia de jade le sube del suelo
        p = (0.4 + r.uniform(-1.4, 1.4), r.uniform(0.0, 3.6), 2.4 + r.uniform(-1.2, 1.2))
        billboard(lz, cam, p, 0.25, 0.25, T_JADE, brillo=0.9)
    horizontal(lz, cam, (0.4, 0.02, 2.4), 2.6, 2.6, T_GRIETAS_JADE, brillo=0.9)
    img = componer(lz, W, H, fondo_plaza(W, H))
    nube_polvo(img, 18, ((W * 0.2, W * 0.8), (H * 0.78, H * 0.95)), 2)
    particulas(img, 70, ((0, W), (0, H)), [(255, 200, 120), (140, 255, 180)], 4, (1.0, 2.6))
    guardar(img, 'moctezuma_heroica')


def moctezuma_normal(W=1600, H=900):
    """Corte de Obsidiana: tajos rapidos con el macuahuitl que dejan medias lunas de obsidiana y esquirlas."""
    cam = camara(ojo=(-5.0, 2.0, -4.6), objetivo=(0.6, 1.8, 2.2), fov=50, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, plaza(), LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA)
    minijefe(lz, cam, 'moctezuma', 0, 2, 30, MOCTEZUMA_CORTE, LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA)
    jugador(lz, cam, 2.2, 0.0, -150, y=0.35, luces=LUCES_PLAZA, amb=AMB_PLAZA, pose=JUGADOR_EMPUJADO)
    r = random.Random(5)
    for _ in range(26):                                  # las esquirlas de obsidiana
        p = (1.4 + r.uniform(-0.6, 1.8), r.uniform(1.0, 2.8), 0.6 + r.uniform(-1.2, 1.0))
        dibujar_mundo(lz, cam, caja_girada(*p, 0.12, 0.28, 0.06, 'mj_obsidiana', r.uniform(0, 180), r.uniform(0, 180),
                                            r.uniform(0, 180)), LUCES_PLAZA, AMB_PLAZA)
        billboard(lz, cam, p, 0.3, 0.3, T_VIOLETA, brillo=0.8)
    fuegos_braseros(lz, cam, 0.7)
    # Dos tajos: el horizontal que acaba de dar y el vertical que viene.
    cinta3d(lz, cam, arco((0, 1.9, 2), 2.3, math.radians(200), math.radians(330), 28), [1.1 * math.sin(math.pi * k / 27) + 0.05
            for k in range(28)], T_ESTELA_OBSIDIANA, brillo=1.6)
    cinta3d(lz, cam, arco((0, 1.9, 2), 2.25, math.radians(205), math.radians(325), 28), [0.35] * 28, T_ESTELA_JADE, brillo=1.0)
    cinta3d(lz, cam, [np.array([0.9 + 0.1 * k, 3.6 - 0.32 * k, 1.0 - 0.05 * k]) for k in range(10)],
            [0.6 * math.sin(math.pi * k / 9) + 0.05 for k in range(10)], T_ESTELA_OBSIDIANA, brillo=0.9)
    billboard(lz, cam, (1.8, 1.6, 0.4), 1.6, 1.6, T_VIOLETA, brillo=1.2)
    img = componer(lz, W, H, fondo_plaza(W, H))
    particulas(img, 60, ((W * 0.45, W * 0.95), (H * 0.25, H * 0.75)), [(200, 140, 255), (120, 255, 170)], 6, (1.0, 2.4))
    guardar(img, 'moctezuma_normal')


def moctezuma_area(W=1600, H=900):
    """Terremoto del Aguila: salta y estampa el escudo; el suelo se agrieta en jade, sale la onda y se levantan
    pilares de piedra en corro."""
    cam = camara(ojo=(-7.5, 4.6, -8.5), objetivo=(0, 0.8, 1.6), fov=50, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    c = np.array([0.0, 0.0, 2.0])
    r = random.Random(7)
    escena = plaza()
    for k in range(14):                                   # el corro de pilares que se levantan
        a = k / 14 * 2 * math.pi
        d = 3.6 + r.uniform(-0.3, 0.3)
        alto = r.uniform(0.8, 1.9)
        escena += caja_girada(c[0] + math.cos(a) * d, alto / 2, c[2] + math.sin(a) * d, 0.7, alto, 0.7, 'templo',
                              r.uniform(-25, 25), r.uniform(0, 90), r.uniform(-25, 25))
    for k in range(20):                                   # y otro, mas lejos, mas bajo
        a = k / 20 * 2 * math.pi + 0.1
        d = 6.0 + r.uniform(-0.4, 0.4)
        alto = r.uniform(0.3, 0.9)
        escena += caja_girada(c[0] + math.cos(a) * d, alto / 2, c[2] + math.sin(a) * d, 0.6, alto, 0.6, 'losa',
                              r.uniform(-30, 30), r.uniform(0, 90), r.uniform(-30, 30))
    dibujar_mundo(lz, cam, escena, LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA)
    minijefe(lz, cam, 'moctezuma', c[0], c[2], 0, MOCTEZUMA_GOLPE, LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA)
    for (x, z, g) in ((-4.0, -1.0, 40), (3.6, -1.6, -50)):
        jugador(lz, cam, x, z, g, y=0.8, luces=LUCES_PLAZA, amb=AMB_PLAZA, pose=JUGADOR_EMPUJADO)
    for _ in range(30):                                   # las piedras que saltan
        a = r.uniform(0, 2 * math.pi)
        d = r.uniform(1.5, 6.5)
        p = (c[0] + math.cos(a) * d, r.uniform(0.6, 3.2), c[2] + math.sin(a) * d)
        dibujar_mundo(lz, cam, caja_girada(*p, 0.25, 0.25, 0.25, 'templo', r.uniform(0, 90), r.uniform(0, 90), 0),
                      LUCES_PLAZA, AMB_PLAZA)
    horizontal(lz, cam, c + [0, 0.03, 0], 7.5, 7.5, T_GRIETAS_JADE, brillo=1.5)
    horizontal(lz, cam, c + [0, 0.05, 0], 4.2, 4.2, T_ARO_JADE, brillo=1.4)
    horizontal(lz, cam, c + [0, 0.05, 0], 7.0, 7.0, T_ARO_JADE, brillo=0.8)
    billboard(lz, cam, c + [0.8, 0.4, -0.6], 3.0, 1.6, T_JADE, brillo=1.4)
    for k in range(14):
        a = k / 14 * 2 * math.pi
        billboard(lz, cam, c + [math.cos(a) * 3.6, 0.3, math.sin(a) * 3.6], 1.2, 0.8, T_JADE, brillo=0.7)
    img = componer(lz, W, H, fondo_plaza(W, H))
    nube_polvo(img, 40, ((W * 0.1, W * 0.9), (H * 0.45, H * 0.85)), 8, alfa=(30, 90))
    particulas(img, 90, ((W * 0.15, W * 0.85), (H * 0.2, H * 0.8)), [(140, 255, 180), (255, 220, 150)], 9, (1.0, 2.8))
    guardar(img, 'moctezuma_area')


def moctezuma_especial(W=1600, H=900):
    """Tormenta de Obsidiana y Jade: se lanza como un rayo verde; deja su estela de siluetas y un reguero de
    esquirlas de obsidiana clavadas que revientan al final."""
    cam = camara(ojo=(-6.2, 1.8, -3.4), objetivo=(1.4, 1.6, 3.4), fov=54, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, plaza(), LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA)
    r = random.Random(11)
    camino = [np.array([-5.0 + k * 1.0, 0.0, 9.0 - k * 0.9]) for k in range(9)]
    for p in camino[:-1]:                                  # las esquirlas clavadas en el suelo
        for _ in range(3):
            q = p + [r.uniform(-0.6, 0.6), 0, r.uniform(-0.6, 0.6)]
            dibujar_mundo(lz, cam, caja_girada(q[0], 0.18, q[2], 0.16, 0.5, 0.08, 'mj_obsidiana', r.uniform(-30, 30),
                                                r.uniform(0, 180), r.uniform(-30, 30)), LUCES_PLAZA, AMB_PLAZA)
    minijefe(lz, cam, 'moctezuma', 3.4, 1.4, 228, MOCTEZUMA_EMBESTIDA, LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA)
    jugador(lz, cam, 5.0, -0.6, 60, y=0.0, luces=LUCES_PLAZA, amb=AMB_PLAZA)
    for k, (x, z) in enumerate(((-3.0, 7.2), (-1.0, 5.4), (1.0, 3.6))):   # las siluetas que deja atras
        fantasma(lz, cam, 'moctezuma', x, z, 228, MOCTEZUMA_EMBESTIDA, T_LISO_JADE, brillo=0.18 + 0.1 * k)
    for p in camino[:-1]:
        billboard(lz, cam, p + [0, 0.3, 0], 1.1, 0.7, T_VIOLETA, brillo=0.9)
    for k, p in enumerate(camino[:4]):                     # las primeras ya revientan
        billboard(lz, cam, p + [0, 0.6, 0], 2.4, 2.4, T_VIOLETA, brillo=1.4)
        billboard(lz, cam, p + [0, 0.6, 0], 1.4, 1.4, T_JADE, brillo=1.2)
        horizontal(lz, cam, p + [0, 0.04, 0], 1.6, 1.6, T_ARO_VIOLETA, brillo=1.2)
    cinta3d(lz, cam, [p + [0, 1.5, 0] for p in camino[:7]] + [np.array([3.4, 1.5, 1.4])], [0.2, 0.5, 0.8, 1.1, 1.3, 1.4,
            1.5, 1.6], T_ESTELA_JADE, brillo=1.1)
    img = componer(lz, W, H, fondo_plaza(W, H))
    particulas(img, 110, ((0, W), (H * 0.3, H * 0.9)), [(200, 140, 255), (120, 255, 170), (255, 255, 255)], 12, (1.0, 2.6))
    guardar(img, 'moctezuma_especial')


# ======================================================================
#  YIATZO: la cumbre en tormenta
# ======================================================================
LUCES_CUMBRE = [((-0.4, 0.9, -0.5), (0.8, 0.88, 1.0), 0.95, 'llave'), ((0.7, 0.3, 0.7), (0.5, 0.9, 1.0), 0.8, 'contra')]
AMB_CUMBRE = (0.24, 0.27, 0.32)
NIEBLA_CUMBRE = Niebla((0.42, 0.48, 0.56), 12, 40, 0.85)


def cumbre():
    r = random.Random(21)
    qs = suelo('roca', -26, 26, -12, 50)
    for _ in range(22):                                    # nieve a parches y piedras
        x, z = r.uniform(-14, 14), r.uniform(-4, 30)
        qs += caja(x, 0, z, r.uniform(0.6, 2.4), 0.12, r.uniform(0.6, 2.0), 'nieve')
    for _ in range(10):
        x, z = r.uniform(-14, 14), r.uniform(6, 34)
        w = r.uniform(0.6, 1.6)
        qs += caja(x, 0, z, w, r.uniform(0.4, 1.4), w, 'roca')
    for _ in range(8):                                     # rocas que flotan, lejos
        x, y, z = r.uniform(-18, 18), r.uniform(5, 12), r.uniform(18, 40)
        w = r.uniform(1.2, 3.0)
        qs += caja(x, y, z, w, w * 0.6, w, 'roca')
    return qs


def fondo_cumbre(W, H, oscuro=0.0):
    f = cielo(W, H, (0.16, 0.19, 0.25), (0.62, 0.68, 0.76), nubes=0.8, color_nubes=(0.22, 0.25, 0.31), semilla=4)
    if oscuro:
        f = f * (1 - oscuro) + np.array([0.06, 0.08, 0.12]) * oscuro
    return f


YIATZO_RAFAGA = {
    'cuerpo': {'rot': (6, -24, 0)}, 'capucha': {'rot': (0, 14, 0)},
    'hombro_der': {'rot': (-92, 14, 0)}, 'antebrazo_der': {'rot': (0, 0, 0)}, 'baston': {'rot': (180, 0, 0)},
    'hombro_izq': {'rot': (-40, 0, -40)}, 'antebrazo_izq': {'rot': (-50, 0, 0)},
}
YIATZO_TORMENTA = {
    'cuerpo': {'rot': (-4, 0, 0)}, 'capucha': {'rot': (-14, 0, 0)},
    'hombro_der': {'rot': (-172, 0, 12)}, 'antebrazo_der': {'rot': (0, 0, 0)}, 'baston': {'rot': (172, 0, 0)},
    'hombro_izq': {'rot': (-20, 0, -80)}, 'antebrazo_izq': {'rot': (-30, 0, 0)},
}
YIATZO_CICLON = {
    'cuerpo': {'rot': (-12, 0, 0)}, 'capucha': {'rot': (-20, 0, 0)},
    'hombro_der': {'rot': (-160, 0, 26)}, 'antebrazo_der': {'rot': (-10, 0, 0)}, 'baston': {'rot': (170, 0, 0)},
    'hombro_izq': {'rot': (-160, 0, -26)}, 'antebrazo_izq': {'rot': (-10, 0, 0)},
}


def remolino(lz, cam, c, r0, r1, alto, vueltas, hilos, brillo, semilla, ancho=0.4):
    r = random.Random(semilla)
    for k in range(hilos):
        pts = espiral(c, r0 * r.uniform(0.8, 1.2), r1 * r.uniform(0.85, 1.15), alto * r.uniform(0.8, 1.0),
                      vueltas, 70, fase=r.uniform(0, 2 * math.pi))
        cinta3d(lz, cam, pts, [ancho * r.uniform(0.6, 1.3)] * len(pts), T_VIENTO[k % 4], brillo=brillo)


def yiatzo_heroica(W=1600, H=900):
    cam = camara(ojo=(-3.0, 0.9, -4.8), objetivo=(0.2, 2.9, 2.4), fov=54, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, cumbre(), LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE)
    minijefe(lz, cam, 'yiatzo', 0.3, 2.4, 16, mj.YIATZO_HEROICA, LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE, y=0.45)
    remolino(lz, cam, (0.3, 0.1, 2.4), 1.2, 1.9, 3.4, 1.3, 7, 0.35, 3)
    billboard(lz, cam, punto('yiatzo', 0.3, 2.4, 16, mj.YIATZO_HEROICA, 'mj_orbe', y=0.45), 1.4, 1.4, T_CIAN, brillo=1.0)
    horizontal(lz, cam, (0.3, 0.03, 2.4), 2.4, 2.4, T_ARO_CIAN, brillo=0.9)
    img = componer(lz, W, H, fondo_cumbre(W, H))
    particulas(img, 80, ((0, W), (0, H)), [(220, 245, 255), (180, 230, 255)], 5, (0.8, 2.0), sube=6)
    guardar(img, 'yiatzo_heroica')


def yiatzo_normal(W=1600, H=900):
    """Rafaga de Viento: del orbe del baston sale un cono de viento con cuchillas de aire que empujan y cortan."""
    A, P = (0.8, 4.0), (-1.2, -1.4)
    g = hacia(A, P)
    cam = camara(ojo=(-5.8, 2.2, -0.6), objetivo=(0.0, 1.9, 1.8), fov=54, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, cumbre(), LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE)
    minijefe(lz, cam, 'yiatzo', A[0], A[1], g, YIATZO_RAFAGA, LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE, y=0.45)
    jugador(lz, cam, P[0], P[1], hacia(P, A), y=0.6, luces=LUCES_CUMBRE, amb=AMB_CUMBRE, pose=JUGADOR_EMPUJADO)
    origen = punto('yiatzo', A[0], A[1], g, YIATZO_RAFAGA, 'mj_orbe', y=0.45)
    destino = np.array([P[0], 1.4, P[1]]) + (np.array([P[0], 1.4, P[1]]) - origen) * 0.25
    r = random.Random(8)
    for k in range(14):                                    # el cono de viento
        fin = destino + [r.uniform(-1.2, 1.2), r.uniform(-0.8, 0.8), r.uniform(-1.2, 1.2)]
        pts = [origen + (fin - origen) * t + np.array([0, math.sin(t * 6 + k) * 0.12, 0]) for t in np.linspace(0, 1, 16)]
        cinta3d(lz, cam, pts, [0.12 + 0.8 * t for t in np.linspace(0, 1, 16)], T_VIENTO[k % 4], brillo=0.4)
    for k, t in enumerate((0.3, 0.55, 0.8)):              # las cuchillas de aire
        p = origen + (destino - origen) * t
        billboard(lz, cam, p, 0.9 + t * 1.4, 0.9 + t * 1.4, T_LUNA, giro=0.4 + k * 0.5, brillo=0.75)
    billboard(lz, cam, origen, 1.2, 1.2, T_CIAN, brillo=1.0)
    img = componer(lz, W, H, fondo_cumbre(W, H))
    particulas(img, 90, ((0, W * 0.8), (H * 0.2, H * 0.8)), [(220, 245, 255)], 9, (0.6, 1.6), sube=10)
    guardar(img, 'yiatzo_normal')


def yiatzo_area(W=1600, H=900):
    """Tormenta de Viento: levanta el baston y alrededor se forma un remolino que arranca piedras y empuja."""
    cam = camara(ojo=(-7.2, 3.6, -8.2), objetivo=(0, 1.8, 2.0), fov=50, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    c = np.array([0.0, 0.0, 2.0])
    r = random.Random(12)
    dibujar_mundo(lz, cam, cumbre(), LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE)
    minijefe(lz, cam, 'yiatzo', c[0], c[2], 0, YIATZO_TORMENTA, LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE, y=0.6)
    for (x, z, g, y) in ((-4.2, 0.6, 50, 1.2), (3.8, -0.6, -40, 0.7)):
        jugador(lz, cam, x, z, g, y=y, luces=LUCES_CUMBRE, amb=AMB_CUMBRE, pose=JUGADOR_EMPUJADO)
    for _ in range(36):                                    # piedras y bloques arrancados
        a = r.uniform(0, 2 * math.pi)
        d = r.uniform(2.4, 5.4)
        p = (c[0] + math.cos(a) * d, r.uniform(0.4, 4.6), c[2] + math.sin(a) * d)
        s = r.uniform(0.18, 0.5)
        dibujar_mundo(lz, cam, caja_girada(*p, s, s, s, r.choice(['roca', 'roca', 'nieve']), r.uniform(0, 90), r.uniform(0, 90),
                                            r.uniform(0, 90)), LUCES_CUMBRE, AMB_CUMBRE)
    embudo(lz, cam, c, 2.6, 5.4, 4.6, translucido=0.16)
    remolino(lz, cam, c, 2.4, 5.4, 4.8, 1.6, 16, 0.32, 4, 0.5)
    horizontal(lz, cam, c + [0, 0.03, 0], 5.6, 5.6, T_ARO_CIAN, brillo=1.1)
    horizontal(lz, cam, c + [0, 0.04, 0], 3.0, 3.0, T_ARO_CIAN, brillo=0.8, giro=0.6)
    billboard(lz, cam, c + [-0.6, 4.8, -0.2], 2.0, 2.0, T_CIAN, brillo=1.4)
    img = componer(lz, W, H, fondo_cumbre(W, H, 0.25))
    particulas(img, 120, ((W * 0.1, W * 0.9), (H * 0.1, H * 0.85)), [(220, 245, 255), (160, 220, 255)], 13, (0.6, 1.8), sube=8)
    guardar(img, 'yiatzo_area')


def yiatzo_especial(W=1600, H=900):
    """Ciclon Devastador: sube al cielo y debajo de el nace un ciclon enorme que se lo traga todo."""
    cam = camara(ojo=(-9.0, 1.6, -12.0), objetivo=(0, 5.0, 3.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    c = np.array([0.0, 0.0, 3.0])
    r = random.Random(14)
    dibujar_mundo(lz, cam, cumbre(), LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE)
    minijefe(lz, cam, 'yiatzo', c[0], c[2], 10, YIATZO_CICLON, LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE, y=8.2)
    for (x, z, g, y) in ((0.8, 2.0, 50, 3.6), (-1.2, 4.0, 160, 5.6), (1.6, 3.6, -80, 1.6)):
        jugador(lz, cam, x, z, g, y=y, luces=LUCES_CUMBRE, amb=AMB_CUMBRE, pose=JUGADOR_EMPUJADO)
    for _ in range(50):
        t = r.uniform(0, 1)
        a = r.uniform(0, 2 * math.pi)
        d = 0.8 + t * 4.2
        p = (c[0] + math.cos(a) * d, t * 8.5 + 0.2, c[2] + math.sin(a) * d)
        s = r.uniform(0.2, 0.6)
        dibujar_mundo(lz, cam, caja_girada(*p, s, s, s, r.choice(['roca', 'roca', 'nieve', 'losa']), r.uniform(0, 90),
                                            r.uniform(0, 90), r.uniform(0, 90)), LUCES_CUMBRE, AMB_CUMBRE)
    embudo(lz, cam, c, 0.6, 5.0, 8.4, capas=12, translucido=0.3)
    remolino(lz, cam, c, 0.7, 5.2, 8.6, 3.0, 22, 0.26, 6, 0.6)
    remolino(lz, cam, c, 0.4, 3.0, 8.0, 2.4, 10, 0.3, 7, 0.35)
    horizontal(lz, cam, c + [0, 0.03, 0], 3.6, 3.6, T_ARO_CIAN, brillo=1.2)
    billboard(lz, cam, c + [-0.6, 10.0, 0], 3.4, 3.4, T_CIAN, brillo=1.4)
    img = componer(lz, W, H, fondo_cumbre(W, H, 0.45))
    nube_polvo(img, 40, ((W * 0.25, W * 0.75), (H * 0.6, H * 0.95)), 15, color=(150, 160, 170), alfa=(30, 80))
    particulas(img, 140, ((W * 0.2, W * 0.8), (0, H)), [(220, 245, 255), (160, 220, 255)], 16, (0.6, 1.8), sube=12)
    guardar(img, 'yiatzo_especial')


# ======================================================================
#  ATLAHUA: ruinas en el fondo del mar
# ======================================================================
LUCES_ABISMO = [((-0.3, 1.0, -0.3), (0.55, 0.85, 1.0), 0.9, 'llave'), ((0.6, 0.3, 0.8), (0.3, 1.0, 0.9), 0.9, 'contra')]
AMB_ABISMO = (0.12, 0.2, 0.26)
NIEBLA_ABISMO = Niebla((0.04, 0.16, 0.22), 6, 30, 0.92)


def ruinas_mar():
    r = random.Random(31)
    qs = suelo('arena', -26, 26, -12, 50)
    for x, z, alto in ((-6, 10, 6.0), (6.5, 12, 4.0), (-9, 18, 7.5), (9, 20, 3.0), (-3, 24, 5.0), (4, 26, 6.5)):
        qs += caja(x - 0.8, 0, z - 0.8, 1.6, alto, 1.6, 'ruina')
        qs += caja(x - 1.1, alto, z - 1.1, 2.2, 0.5, 2.2, 'ruina')
    for _ in range(14):
        x, z = r.uniform(-12, 12), r.uniform(-2, 30)
        qs += caja_girada(x, 0.3, z, r.uniform(0.6, 1.4), 0.6, r.uniform(0.6, 1.4), 'ruina', r.uniform(-10, 10),
                          r.uniform(0, 90), r.uniform(-10, 10))
    for _ in range(16):                                    # coral
        x, z = r.uniform(-10, 10), r.uniform(0, 26)
        qs += caja(x, 0, z, 0.4, r.uniform(0.6, 1.6), 0.4, r.choice(['coral_r', 'coral_n', 'coral_p']))
    return qs


def fondo_abismo(W, H, k=1.0):
    f = cielo(W, H, (0.01, 0.05, 0.09), (0.06, 0.32, 0.4), sol=(0.4, -0.1, (0.1, 0.35, 0.4), 0.4))
    return f + ne.rayos(W, H, 3)[..., None] * np.array([0.25, 0.55, 0.6]) * k


ATLAHUA_ESTOCADA = {
    'pelvis': {'rot': (0, -20, 0)}, 'torso': {'rot': (16, 24, 0)}, 'cabeza': {'rot': (-14, -6, 0)}, 'mandibula': {'rot': (20, 0, 0)},
    'pierna_izq': {'rot': (-40, 0, -6)}, 'espinilla_izq': {'rot': (40, 0, 0)},
    'pierna_der': {'rot': (30, 0, 6)}, 'espinilla_der': {'rot': (10, 0, 0)}, 'pie_der': {'rot': (-30, 0, 0)},
    'hombro_der': {'rot': (-92, 6, 0)}, 'antebrazo_der': {'rot': (0, 0, 0)}, 'tridente': {'rot': (180, 0, 0)},
    'hombro_izq': {'rot': (-40, 0, -40)}, 'antebrazo_izq': {'rot': (-60, 0, 0)},
}
ATLAHUA_OLAS = {
    'pelvis': {'pos': (0, 2.5, 0), 'rot': (10, 0, 0)}, 'torso': {'rot': (26, 0, 0)}, 'cabeza': {'rot': (-24, 0, 0)},
    'mandibula': {'rot': (28, 0, 0)},
    'pierna_izq': {'rot': (-50, 0, -12)}, 'espinilla_izq': {'rot': (56, 0, 0)},
    'pierna_der': {'rot': (-10, 0, 14)}, 'espinilla_der': {'rot': (60, 0, 0)}, 'pie_der': {'rot': (-40, 0, 0)},
    'hombro_der': {'rot': (-62, 0, 6)}, 'antebrazo_der': {'rot': (0, 0, 0)}, 'tridente': {'rot': (180, 0, 0)},
    'hombro_izq': {'rot': (-30, 0, -50)}, 'antebrazo_izq': {'rot': (-40, 0, 0)},
}
ATLAHUA_TSUNAMI = {
    'torso': {'rot': (-10, 0, 0)}, 'cabeza': {'rot': (-30, 0, 0)}, 'mandibula': {'rot': (30, 0, 0)},
    'hombro_der': {'rot': (-170, 0, 14)}, 'antebrazo_der': {'rot': (0, 0, 0)}, 'tridente': {'rot': (170, 0, 0)},
    'hombro_izq': {'rot': (-150, 0, -30)}, 'antebrazo_izq': {'rot': (-10, 0, 0)},
    'pierna_izq': {'rot': (-10, 0, -10)}, 'pierna_der': {'rot': (10, 0, 10)}, 'cola_pez': {'rot': (40, 0, 0)},
}


def anillo_agua(lz, cam, c, radio, alto, brillo=1.0, n=60):
    """Una ola en corro: la pared de agua translucida y la espuma encima."""
    pts = [np.asarray(c, float) + [math.cos(2 * math.pi * k / (n - 1)) * radio, 0, math.sin(2 * math.pi * k / (n - 1)) * radio]
           for k in range(n)]
    for i in range(n - 1):
        a, b = pts[i], pts[i + 1]
        P = [a, b, b + [0, alto, 0], a + [0, alto, 0]]
        quad(lz, cam, P, T_AGUA, aditivo=False, translucido=0.45, uv=[(i / 8, 0), ((i + 1) / 8, 0), ((i + 1) / 8, 1), (i / 8, 1)])
    cinta3d(lz, cam, [p + [0, alto, 0] for p in pts], [0.35] * n, T_ESPUMA, brillo=brillo)


def atlahua_heroica(W=1600, H=900):
    cam = camara(ojo=(-2.6, 0.8, -3.6), objetivo=(0.3, 2.4, 2.4), fov=52, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, ruinas_mar(), LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO)
    minijefe(lz, cam, 'atlahua', 0.4, 2.4, 18, mj.ATLAHUA_HEROICA, LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO)
    horizontal(lz, cam, (0.4, 0.03, 2.4), 2.4, 2.4, T_ARO_CIAN, brillo=0.8)
    r = random.Random(4)
    for _ in range(30):
        p = (0.4 + r.uniform(-1.6, 1.6), r.uniform(0.2, 3.6), 2.4 + r.uniform(-1.2, 1.2))
        billboard(lz, cam, p, 0.18, 0.18, T_CIAN, brillo=0.9)
    img = componer(lz, W, H, fondo_abismo(W, H), vineta=0.6)
    ne.burbujas(img, 60, 6)
    guardar(img, 'atlahua_heroica')


def atlahua_normal(W=1600, H=900):
    """Estocada del Tridente: tres estocadas seguidas, cada una con su lanza de agua y su estela de burbujas."""
    A, P = (0.8, 3.6), (-1.0, -1.2)
    g = hacia(A, P)
    cam = camara(ojo=(-5.6, 2.0, -0.6), objetivo=(0.0, 1.7, 1.6), fov=54, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, ruinas_mar(), LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO)
    minijefe(lz, cam, 'atlahua', A[0], A[1], g, ATLAHUA_ESTOCADA, LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO)
    jugador(lz, cam, P[0], P[1], hacia(P, A), y=0.3, luces=LUCES_ABISMO, amb=AMB_ABISMO, pose=JUGADOR_EMPUJADO)
    punta = punto('atlahua', A[0], A[1], g, ATLAHUA_ESTOCADA, 'mj_punta_coral')
    blanco = np.array([P[0], 1.5, P[1]])
    for k, desvio in enumerate((-0.5, 0.0, 0.5)):
        fin = blanco + (blanco - punta) * 0.35 + np.array([desvio, desvio * 0.5, 0])
        pts = [punta + (fin - punta) * t for t in np.linspace(0, 1, 12)]
        cinta3d(lz, cam, pts, [0.6 - 0.45 * t for t in np.linspace(0, 1, 12)], T_ESTELA_AGUA, brillo=0.9 - 0.25 * abs(desvio))
    billboard(lz, cam, blanco, 1.8, 1.8, T_CIAN, brillo=0.8)
    horizontal(lz, cam, (P[0], 0.04, P[1]), 1.8, 1.8, T_ARO_CIAN, brillo=0.8)
    billboard(lz, cam, punta, 1.0, 1.0, T_CIAN, brillo=1.0)
    img = componer(lz, W, H, fondo_abismo(W, H), vineta=0.6)
    ne.burbujas(img, 90, 8, ((W * 0.1, W * 0.7), (H * 0.25, H * 0.75)))
    guardar(img, 'atlahua_normal')


def atlahua_area(W=1600, H=900):
    """Olas del Abismo: clava el tridente y salen olas en corro que empujan y van subiendo el agua del suelo."""
    cam = camara(ojo=(-7.4, 4.0, -8.4), objetivo=(0, 1.0, 1.8), fov=50, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    c = np.array([0.0, 0.0, 2.0])
    dibujar_mundo(lz, cam, ruinas_mar(), LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO)
    minijefe(lz, cam, 'atlahua', c[0], c[2], 0, ATLAHUA_OLAS, LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO)
    for (x, z, g) in ((-4.4, -0.4, 60), (4.0, -1.2, -50)):
        jugador(lz, cam, x, z, g, y=0.7, luces=LUCES_ABISMO, amb=AMB_ABISMO, pose=JUGADOR_EMPUJADO)
    horizontal(lz, cam, c + [0, 0.22, 0], 9, 9, T_AGUA, aditivo=False, translucido=0.35)   # el agua que sube
    for radio, alto in ((2.4, 0.9), (4.4, 0.6), (6.4, 0.4)):
        anillo_agua(lz, cam, c, radio, alto, 1.0)
    for radio in (2.4, 4.4, 6.4):
        horizontal(lz, cam, c + [0, 0.25, 0], radio * 1.1, radio * 1.1, T_ARO_CIAN, brillo=0.7)
    billboard(lz, cam, c + [0.4, 0.4, -0.8], 2.4, 1.4, T_CIAN, brillo=1.2)
    img = componer(lz, W, H, fondo_abismo(W, H), vineta=0.6)
    ne.burbujas(img, 120, 10, ((W * 0.15, W * 0.85), (H * 0.35, H * 0.85)))
    guardar(img, 'atlahua_area')


def atlahua_especial(W=1600, H=900):
    """Tsunami del Abismo: sube en una columna de agua y suelta una ola enorme que arrastra a todos y deja el
    suelo inundado."""
    cam = camara(ojo=(-6.8, 1.8, -8.2), objetivo=(0.0, 3.0, 2.6), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, ruinas_mar(), LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO)
    A = (0.0, 5.0)
    c = np.array([A[0], 0.0, A[1]])
    g = hacia(A, (-6.8, -8.2))
    minijefe(lz, cam, 'atlahua', A[0], A[1], g, ATLAHUA_TSUNAMI, LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO, y=3.6)
    for (x, z, gj, y) in ((-3.4, 0.6, 30, 1.6), (2.6, 0.2, -40, 2.3)):
        jugador(lz, cam, x, z, gj, y=y, luces=LUCES_ABISMO, amb=AMB_ABISMO, pose=JUGADOR_EMPUJADO)
    horizontal(lz, cam, (0, 0.3, 4), 14, 14, T_AGUA, aditivo=False, translucido=0.35)       # el suelo inundado
    for k in range(18):                                    # la columna de agua que lo sube
        a0, a1 = k / 18 * 2 * math.pi, (k + 1) / 18 * 2 * math.pi
        rr = 1.5
        Pq = [c + [math.cos(a0) * rr, 0, math.sin(a0) * rr], c + [math.cos(a1) * rr, 0, math.sin(a1) * rr],
              c + [math.cos(a1) * rr * 0.75, 3.6, math.sin(a1) * rr * 0.75], c + [math.cos(a0) * rr * 0.75, 3.6, math.sin(a0) * rr * 0.75]]
        quad(lz, cam, Pq, T_AGUA, aditivo=False, translucido=0.4, uv=[(k / 6, 0), ((k + 1) / 6, 0), ((k + 1) / 6, 1), (k / 6, 1)])
    horizontal(lz, cam, c + [0, 3.62, 0], 1.3, 1.3, T_ARO_CIAN, brillo=0.9)
    # La ola, delante, que viene hacia la camara: una pared curva de agua con la cresta rota en espuma.
    n = 30
    base = [np.array([-7.0 + 14.0 * t, 0.3, 0.6 - 1.4 * math.sin(math.pi * t)]) for t in np.linspace(0, 1, n)]

    def p(b, h):
        return b + [0, h * 4.2, -math.sin(h * math.pi * 0.85) * 1.8]
    for i in range(n - 1):
        for j in range(6):
            h0, h1 = j / 6, (j + 1) / 6
            Pq = [p(base[i], h0), p(base[i + 1], h0), p(base[i + 1], h1), p(base[i], h1)]
            quad(lz, cam, Pq, T_AGUA, aditivo=False, translucido=0.42, uv=[(i / 5, h0), ((i + 1) / 5, h0), ((i + 1) / 5, h1), (i / 5, h1)])
    cinta3d(lz, cam, [p(b, 1.0) for b in base], [0.6] * n, T_ESPUMA, brillo=0.5)
    cinta3d(lz, cam, [p(b, 0.08) for b in base], [0.4] * n, T_ESPUMA, brillo=0.3)
    billboard(lz, cam, c + [0, 4.4, 0], 2.2, 2.2, T_CIAN, brillo=0.8)
    img = componer(lz, W, H, fondo_abismo(W, H, 0.8), vineta=0.6)
    ne.burbujas(img, 160, 12)
    guardar(img, 'atlahua_especial')


# ======================================================================
#  XIUHQUETZAL: ruinas volcanicas de noche
# ======================================================================
LUCES_VOLCAN = [((-0.4, 0.6, -0.6), (1.0, 0.55, 0.3), 0.9, 'llave'), ((0.6, 0.3, 0.8), (0.8, 0.4, 1.0), 0.9, 'contra')]
AMB_VOLCAN = (0.2, 0.12, 0.16)
NIEBLA_VOLCAN = Niebla((0.16, 0.06, 0.1), 12, 40, 0.85)


def ruinas_volcan():
    r = random.Random(41)
    qs = suelo('basalto', -44, 44, -34, 62)
    for _ in range(26):
        x, z = r.uniform(-16, 16), r.uniform(-6, 34)
        qs += caja(x, 0.0, z, r.uniform(1, 3), 0.04, r.uniform(1, 3), 'basalto_lava')
    for x, z, alto in ((-7, 12, 5.0), (7.5, 14, 3.5), (-10, 20, 7.0), (10, 22, 2.5), (-4, 26, 4.0)):
        qs += caja(x - 0.8, 0, z - 0.8, 1.6, alto, 1.6, 'basalto')
    return qs


def fondo_volcan(W, H, k=1.0):
    return cielo(W, H, (0.04, 0.02, 0.06), (0.42, 0.1, 0.12), sol=(0.5, 0.95, (0.5 * k, 0.12 * k, 0.05), 0.35), nubes=0.6,
                 color_nubes=(0.12, 0.04, 0.08), semilla=9)


XIUHQUETZAL_PICADO = {
    'cuerpo': {'rot': (26, 0, 0)},
    'ala_izq': {'rot': (-62, -34, -34)}, 'mano_ala_izq': {'rot': (0, -14, -10)},
    'ala_der': {'rot': (-62, 34, 34)}, 'mano_ala_der': {'rot': (0, 14, 10)},
    'cuello': {'rot': (-10, 0, 0)}, 'cabeza': {'rot': (-6, 0, 0)}, 'pico_inf': {'rot': (30, 0, 0)},
    'pata_izq': {'rot': (-62, 0, 0)}, 'pata_der': {'rot': (-62, 0, 0)},
    'garras_izq': {'rot': (-30, 0, 0)}, 'garras_der': {'rot': (-30, 0, 0)},
    'cola': {'rot': (-24, 0, 0)},
}
XIUHQUETZAL_LLUVIA = {
    'cuerpo': {'rot': (-8, 0, 0)},
    'ala_izq': {'rot': (-72, -6, -22)}, 'mano_ala_izq': {'rot': (0, -2, -4)},
    'ala_der': {'rot': (-72, 6, 22)}, 'mano_ala_der': {'rot': (0, 2, 4)},
    'cuello': {'rot': (10, 0, 0)}, 'cabeza': {'rot': (-20, 0, 0)}, 'pico_inf': {'rot': (20, 0, 0)},
}
XIUHQUETZAL_LLAMARADA = {
    'cuerpo': {'rot': (-6, 0, 0)},
    'ala_izq': {'rot': (-66, 26, -26)}, 'mano_ala_izq': {'rot': (0, 14, -8)},
    'ala_der': {'rot': (-66, -26, 26)}, 'mano_ala_der': {'rot': (0, -14, 8)},
    'cuello': {'rot': (20, 0, 0)}, 'cabeza': {'rot': (-36, 0, 0)}, 'pico_inf': {'rot': (34, 0, 0)},
    'cola': {'rot': (-14, 0, 0)},
}


def aura_fuego(lz, cam, c, radio, alto, n, semilla, brillo=1.0, violeta=0.4):
    r = random.Random(semilla)
    for _ in range(n):
        p = np.asarray(c, float) + [r.uniform(-radio, radio), r.uniform(0, alto), r.uniform(-radio, radio)]
        t = r.choice(T_LLAMAS_V) if r.random() < violeta else r.choice(T_LLAMAS)
        s = r.uniform(0.5, 1.3)
        billboard(lz, cam, p, s * 0.6, s * 1.2, t, giro=r.uniform(-0.3, 0.3), brillo=brillo)


def xiuhquetzal_heroica(W=1600, H=900):
    cam = camara(ojo=(-1.9, 0.8, -2.6), objetivo=(0.4, 3.2, 2.6), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, ruinas_volcan(), LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN)
    minijefe(lz, cam, 'xiuhquetzal', 0.4, 2.6, 14, mj.XIUHQUETZAL_HEROICA, LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN, y=0.0)
    aura_fuego(lz, cam, (0.4, 0.3, 3.4), 1.6, 1.4, 16, 3, 0.45)
    billboard(lz, cam, (0.4, 1.8, 3.0), 4.6, 4.6, T_FUEGO, brillo=0.28)
    horizontal(lz, cam, (0.4, 0.03, 2.6), 3.0, 3.0, T_GRIETAS_LAVA, brillo=1.2)
    img = componer(lz, W, H, fondo_volcan(W, H))
    particulas(img, 160, ((0, W), (0, H)), [(255, 160, 60), (255, 220, 120), (220, 120, 255)], 7, (0.8, 2.2), sube=-7)
    guardar(img, 'xiuhquetzal_heroica')


def xiuhquetzal_normal(W=1600, H=900):
    """Picotazo de Llamas: se tira en picado con el pico y las garras por delante, dejando una cola de fuego."""
    A, P = (1.6, 3.2), (-1.4, -1.0)
    g = hacia(A, P)
    cam = camara(ojo=(-4.2, 1.4, -2.6), objetivo=(0.0, 2.6, 1.2), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, ruinas_volcan(), LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN)
    jugador(lz, cam, P[0], P[1], hacia(P, A), y=0.2, luces=LUCES_VOLCAN, amb=AMB_VOLCAN, pose=JUGADOR_EMPUJADO)
    minijefe(lz, cam, 'xiuhquetzal', A[0], A[1], g, XIUHQUETZAL_PICADO, LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN, y=0.0)
    pecho = punto('xiuhquetzal', A[0], A[1], g, XIUHQUETZAL_PICADO, 'mj_brasa', y=0.0)
    atras = np.array([A[0] - P[0], 0, A[1] - P[1]])
    atras = atras / np.linalg.norm(atras)
    cola = [pecho + atras * t * 6.0 + np.array([0, t * 4.0, 0]) for t in np.linspace(0, 1, 18)]
    cinta3d(lz, cam, cola, [2.2 * (1 - t) + 0.2 for t in np.linspace(0, 1, 18)], T_ESTELA_FUEGO, brillo=1.0)
    cinta3d(lz, cam, [p + [0, 0.5, 0] for p in cola], [1.1 * (1 - t) + 0.1 for t in np.linspace(0, 1, 18)], T_ESTELA_VIOLETA,
            brillo=0.7)
    aura_fuego(lz, cam, (P[0], 0.2, P[1] + 0.4), 0.8, 1.2, 10, 5, 0.8)
    billboard(lz, cam, (P[0] + 0.4, 1.2, P[1] + 0.6), 2.2, 2.2, T_FUEGO, brillo=0.8)
    img = componer(lz, W, H, fondo_volcan(W, H))
    particulas(img, 140, ((W * 0.2, W), (0, H * 0.9)), [(255, 160, 60), (255, 230, 140), (220, 120, 255)], 9, (0.8, 2.2), sube=-6)
    guardar(img, 'xiuhquetzal_normal')


def xiuhquetzal_area(W=1600, H=900):
    """Tormenta de Plumas Igneas: sube y llueven plumas ardiendo que revientan al tocar el suelo y lo dejan en llamas."""
    cam = camara(ojo=(-8.0, 2.0, -8.6), objetivo=(0, 3.4, 2.4), fov=56, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    c = np.array([0.0, 0.0, 2.6])
    r = random.Random(17)
    dibujar_mundo(lz, cam, ruinas_volcan(), LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN)
    minijefe(lz, cam, 'xiuhquetzal', c[0], c[2], 0, XIUHQUETZAL_LLUVIA, LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN, y=3.0)
    for (x, z, g) in ((-3.6, -0.6, 50), (3.4, -1.2, -40)):
        jugador(lz, cam, x, z, g, luces=LUCES_VOLCAN, amb=AMB_VOLCAN)
    pluma_tex = mj.MAT['mj_ala'][0]
    pluma_v = mj.MAT['mj_ala_v'][0]
    for _ in range(46):                                    # las plumas que caen
        p = c + [r.uniform(-6, 6), r.uniform(0.6, 6.0), r.uniform(-5, 5)]
        billboard(lz, cam, p, 0.32, 1.1, pluma_v if r.random() < 0.4 else pluma_tex, giro=r.uniform(-0.6, 0.6),
                  aditivo=False)
        cinta3d(lz, cam, [p + [0, 0.5, 0], p + [0, 1.9, 0]], [0.3, 0.05], T_ESTELA_FUEGO, brillo=0.8)
    for _ in range(12):                                    # las que ya han caido: revientan y dejan fuego
        p = c + [r.uniform(-5, 5), 0, r.uniform(-4, 4)]
        horizontal(lz, cam, p + [0, 0.04, 0], 1.2, 1.2, T_ARO_FUEGO, brillo=1.1)
        aura_fuego(lz, cam, p, 0.4, 0.5, 4, r.randint(0, 99), 1.1, 0.5)
        billboard(lz, cam, p + [0, 0.5, 0], 1.6, 1.6, T_FUEGO, brillo=0.9)
    aura_fuego(lz, cam, c + [0, 4.6, 0], 1.2, 2.4, 16, 21, 0.8)
    img = componer(lz, W, H, fondo_volcan(W, H, 1.3))
    particulas(img, 180, ((0, W), (0, H)), [(255, 160, 60), (255, 230, 140), (220, 120, 255)], 19, (0.8, 2.2), sube=-6)
    guardar(img, 'xiuhquetzal_area')


def xiuhquetzal_especial(W=1600, H=900):
    """Llamarada del Renacimiento: abre las alas y revienta en un anillo de fuego rojo y violeta que crece; detras
    salen plumas ardiendo que persiguen a los jugadores."""
    cam = camara(ojo=(-9.5, 3.6, -10.5), objetivo=(0, 2.2, 2.4), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    c = np.array([0.0, 0.0, 2.6])
    r = random.Random(23)
    dibujar_mundo(lz, cam, ruinas_volcan(), LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN)
    minijefe(lz, cam, 'xiuhquetzal', c[0], c[2], 0, XIUHQUETZAL_LLAMARADA, LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN, y=0.2)
    for (x, z, g) in ((-5.2, -1.0, 50), (5.0, -0.4, -60), (-1.0, -5.0, 10)):
        jugador(lz, cam, x, z, g, y=0.5, luces=LUCES_VOLCAN, amb=AMB_VOLCAN, pose=JUGADOR_EMPUJADO)
    horizontal(lz, cam, c + [0, 0.04, 0], 9.5, 9.5, T_GRIETAS_LAVA, brillo=1.4)
    for radio, t, b in ((3.2, T_ARO_FUEGO, 1.6), (5.4, T_ARO_VIOLETA, 1.3), (7.6, T_ARO_FUEGO, 0.9)):
        horizontal(lz, cam, c + [0, 0.06, 0], radio, radio, t, brillo=b)
    for k in range(40):                                    # la pared de llamas del anillo
        a = k / 40 * 2 * math.pi
        rr = 5.4 + r.uniform(-0.4, 0.4)
        p = c + [math.cos(a) * rr, 0.9, math.sin(a) * rr]
        t = T_LLAMAS_V[k % 3] if k % 2 else T_LLAMAS[k % 4]
        billboard(lz, cam, p, 1.0, 2.2, t, brillo=1.1)
    for k in range(5):                                     # las plumas que persiguen
        pts = espiral(c + [0, 2.0, 0], 1.0, 5.5, 2.0, 0.6, 20, fase=k * 1.25)
        cinta3d(lz, cam, pts, [0.05 + 0.4 * t for t in np.linspace(0, 1, 20)], T_ESTELA_VIOLETA if k % 2 else T_ESTELA_FUEGO,
                brillo=1.2)
    billboard(lz, cam, c + [0, 2.4, 0], 7.0, 7.0, T_FUEGO, brillo=0.8)
    billboard(lz, cam, c + [0, 2.4, 0], 4.0, 4.0, T_ROSA, brillo=0.6)
    img = componer(lz, W, H, fondo_volcan(W, H, 1.6))
    particulas(img, 220, ((0, W), (0, H)), [(255, 160, 60), (255, 230, 140), (220, 120, 255)], 25, (0.8, 2.4), sube=-7)
    guardar(img, 'xiuhquetzal_especial')


# ----------------------------------------------------------------------
#  Vistas y escala
# ----------------------------------------------------------------------
def vistas(nombre, W=1800, H=640):
    """Frente, perfil y espalda sobre fondo claro."""
    _, reposo, _ = mj.MINIJEFES[nombre]
    lienzos = []
    for g in (0, -90, 180):
        cam = vr.Camara(ojo=(0, 2.9, -40), objetivo=(0, 2.9, 0), fov=13 if nombre != 'xiuhquetzal' else 21,
                        ancho=600 * SS, alto=H * SS)
        lz = vr.Lienzo(600 * SS, H * SS)
        minijefe(lz, cam, nombre, 0, 0, g, reposo, amb=(0.36, 0.36, 0.38), brillo=1.2)
        lienzos.append(lz)
    img = Image.new('RGB', (W, H), (236, 238, 240))
    for k, lz in enumerate(lienzos):
        col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
        a = lz.alfa[..., None]
        arr = col * a + np.array([0.925, 0.93, 0.94]) * (1 - a)
        im = Image.fromarray((arr * 255).astype(np.uint8)).resize((600, H), Image.LANCZOS)
        img.paste(im, (k * 600, 0))
    img.save(os.path.join(OUT, f'{nombre}_vistas.jpg'), quality=92)
    print(nombre, 'vistas', flush=True)


def escala(W=2000, H=700):
    """Los cuatro, en fila, junto a un jugador (1,8 bloques)."""
    cam = vr.Camara(ojo=(0, 3.2, -34), objetivo=(0, 2.8, 0), fov=27, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, suelo('losa', -20, 20, -4, 6), LUCES_ESTUDIO, (0.36, 0.36, 0.38))
    jugador(lz, cam, -13.0, 0, 0, amb=(0.36, 0.36, 0.38))
    for (nombre, x, y) in (('moctezuma', -8.4, 0.0), ('yiatzo', -2.8, 0.45), ('atlahua', 2.6, 0.0), ('xiuhquetzal', 12.0, 0.0)):
        minijefe(lz, cam, nombre, x, 0, 0, None, amb=(0.36, 0.36, 0.38), y=y, brillo=1.2)
    fondo = cielo(W, H, (0.86, 0.88, 0.9), (0.95, 0.96, 0.97))
    img = componer(lz, W, H, fondo, vineta=0.15, bloom=((4, 0.4), (14, 0.25)))
    d = ImageDraw.Draw(img)
    for k in range(7):                                     # una regla de bloques a la izquierda
        y0 = cam.proyectar(np.array([-15.0, k, 0]))[1] / SS
        y1 = cam.proyectar(np.array([-15.0, k + 1, 0]))[1] / SS
        x = cam.proyectar(np.array([-15.0, 0, 0]))[0] / SS
        d.rectangle((x - 6, y1, x + 6, y0), fill=(60, 60, 70) if k % 2 else (150, 150, 160))
    guardar(img, 'escala')


# ----------------------------------------------------------------------
#  Retratos: de cerca y desde abajo, como las referencias
# ----------------------------------------------------------------------
def _retrato(nombre, mundo, luces, amb, niebla, fondo, pose, ojo, obj, fov, A, y=0.0, extra=None, post=None, W=1600, H=900):
    cam = camara(ojo=ojo, objetivo=obj, fov=fov, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    dibujar_mundo(lz, cam, mundo, luces, amb, niebla)
    minijefe(lz, cam, nombre, A[0], A[1], hacia(A, (ojo[0], ojo[2])), pose, luces, amb, niebla, y=y)
    if extra:
        extra(lz, cam)
    img = componer(lz, W, H, fondo(W, H))
    if post:
        post(img)
    guardar(img, nombre + '_retrato')


def moctezuma_retrato():
    def extra(lz, cam):
        fuegos_braseros(lz, cam, 0.8)
        horizontal(lz, cam, (0.3, 0.03, 2.4), 2.2, 2.2, T_GRIETAS_JADE, brillo=0.8)
    _retrato('moctezuma', plaza(), LUCES_PLAZA, AMB_PLAZA, NIEBLA_PLAZA, fondo_plaza, mj.MOCTEZUMA_HEROICA,
             (-1.3, 0.55, -0.5), (0.25, 2.5, 2.4), 54, (0.3, 2.4), extra=extra,
             post=lambda img: particulas(img, 60, ((0, img.size[0]), (0, img.size[1])), [(255, 200, 120), (140, 255, 180)], 4,
                                         (1.0, 2.6)))


def yiatzo_retrato():
    def extra(lz, cam):
        remolino(lz, cam, (0.3, 0.1, 2.4), 1.3, 2.0, 3.6, 1.4, 8, 0.3, 3)
        billboard(lz, cam, punto('yiatzo', 0.3, 2.4, hacia((0.3, 2.4), (-1.2, -0.6)), mj.YIATZO_REPOSO, 'mj_orbe', y=0.45),
                  1.2, 1.2, T_CIAN, brillo=0.9)
    _retrato('yiatzo', cumbre(), LUCES_CUMBRE, AMB_CUMBRE, NIEBLA_CUMBRE, fondo_cumbre, mj.YIATZO_REPOSO,
             (-1.2, 0.75, -0.6), (0.25, 2.7, 2.4), 56, (0.3, 2.4), y=0.45, extra=extra,
             post=lambda img: particulas(img, 80, ((0, img.size[0]), (0, img.size[1])), [(220, 245, 255)], 5, (0.8, 2.0), sube=6))


def atlahua_retrato():
    _retrato('atlahua', ruinas_mar(), LUCES_ABISMO, AMB_ABISMO, NIEBLA_ABISMO, fondo_abismo, mj.ATLAHUA_HEROICA,
             (-1.2, 0.6, -0.6), (0.25, 2.6, 2.4), 56, (0.3, 2.4),
             post=lambda img: ne.burbujas(img, 70, 6))


def xiuhquetzal_retrato():
    def extra(lz, cam):
        aura_fuego(lz, cam, (0.4, 0.3, 3.4), 1.6, 1.2, 12, 3, 0.4)
    _retrato('xiuhquetzal', ruinas_volcan(), LUCES_VOLCAN, AMB_VOLCAN, NIEBLA_VOLCAN, fondo_volcan, mj.XIUHQUETZAL_HEROICA,
             (-1.4, 0.4, -1.0), (0.3, 3.0, 2.6), 74, (0.4, 2.6), y=0.0, extra=extra,
             post=lambda img: particulas(img, 160, ((0, img.size[0]), (0, img.size[1])), [(255, 160, 60), (255, 220, 120),
                                                                                          (220, 120, 255)], 7, (0.8, 2.2), sube=-7))


ESCENAS = {
    'moctezuma': [moctezuma_retrato, moctezuma_heroica, moctezuma_normal, moctezuma_area, moctezuma_especial],
    'yiatzo': [yiatzo_retrato, yiatzo_heroica, yiatzo_normal, yiatzo_area, yiatzo_especial],
    'atlahua': [atlahua_retrato, atlahua_heroica, atlahua_normal, atlahua_area, atlahua_especial],
    'xiuhquetzal': [xiuhquetzal_retrato, xiuhquetzal_heroica, xiuhquetzal_normal, xiuhquetzal_area, xiuhquetzal_especial],
}


def main():
    solo = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    for nombre, fns in ESCENAS.items():
        for fn in [lambda n=nombre: vistas(n)] + fns:
            clave = getattr(fn, '__name__', 'vistas')
            if solo and not any(s in (nombre, clave, nombre + '_vistas' if clave == '<lambda>' else '') for s in solo):
                continue
            fn()
    if not solo or 'escala' in solo:
        escala()


if __name__ == '__main__':
    main()

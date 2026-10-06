"""
Renders de la ficha del remake de Nerea: el antes (la malla y la piel del
juego de hoy) y el despues (nerea_remake.py), con la misma camara y la misma
luz; y las escenas de los ataques rehechos y nuevos, en el fondo del mar de la
ficha original (nerea_escenas.py).

Uso: python nerea_remake_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nerea_remake as nr
import nerea_juego as nj
import nerea_juego_anim as nja
import nerea_modelo as nm
import nerea_escenas as ne
import vigia_render as vr

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
FUENTE = 'C:/Windows/Fonts/'
SS = 2
LUZ_ESTUDIO = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
AMB_ESTUDIO = (0.36, 0.38, 0.42)
LUCES = ne.LUCES_MAR
AMB = (0.2, 0.28, 0.34)

# El color de cada fase (el de los ojos): cian, violeta, magenta, rojo; y la Furia.
COLOR = {1: (63, 224, 255), 2: (154, 107, 255), 3: (212, 60, 255), 4: (255, 32, 80), 'libre': (255, 194, 58)}
AGUA = (90, 200, 230)
ESPUMA = (236, 252, 255)


# ----------------------------------------------------------------------
#  Poses
# ----------------------------------------------------------------------
def pose(nombre='REPOSO', s=0.0, fase=1, libre=False):
    """Una pose de las animaciones, con lo que el juego ensena en esa fase:
    el corazon de la fase, las cadenas que le quedan y las costillas."""
    p = nja.pose_en(nombre, s)
    for k in ('molino_izq', 'molino_der'):
        p[k] = {'oculto': True}
    for i in range(1, 5):
        p['corazon_%d' % i] = {**p.get('corazon_%d' % i, {}), 'oculto': libre or i != fase}
        p['cadena_%d' % i] = {**p.get('cadena_%d' % i, {}), 'oculto': i > 5 - fase}
    p['corazon_libre'] = {**p.get('corazon_libre', {}), 'oculto': not libre}
    if fase >= 4:
        p['costillas'] = {**p.get('costillas', {}), 'oculto': True}
    return p


# ----------------------------------------------------------------------
#  Dibujar una Nerea (antes o despues) con su atlas
# ----------------------------------------------------------------------
def nerea(lz, cam, cual, x, z, guinada, p=None, fase=1, niebla=None, luces=None, amb=None, brillo=1.4, y=0.0,
          aura=None):
    base, emis, uv, alto = nr.atlas(cual, fase)
    nr.usar(cual)
    p = pose(fase=fase if fase != 'libre' else 1, libre=fase == 'libre') if p is None else p
    luces = LUZ_ESTUDIO if luces is None else luces
    amb = AMB_ESTUDIO if amb is None else amb
    M = vr.T(0, y, 0) @ vr.entidad_a_mundo(x, 0, z, guinada, nr.ESCALA[cual])
    for Pq, UV, n in nj.quads(p, uv, alto, M):
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], base, luz, emis, niebla, brillo=brillo)
    if aura is not None:
        # El aura de la Furia: la misma malla un poco hinchada, con las bandas encima.
        Ma = vr.T(x, y, z) @ vr.S(1.05) @ vr.T(-x, -y, -z) @ M
        for Pq, UV, n in nj.quads(p, uv, alto, Ma):
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], aura, np.ones(3), None, None,
                             aditivo=True, brillo=0.3)


def jugador(lz, cam, x, z, guinada, y=0.0, niebla=None, luces=None):
    M = vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, guinada)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, M), luces or LUCES, AMB, niebla)


def estudio(lz, W, H, emis=0.45, fondo=(0.93, 0.95, 0.96)):
    col = np.clip(lz.color + lz.emis * emis, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array(fondo) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)


def rotulo(img, texto, x, y, tam=30, color=(16, 32, 58), fuente='Oswald-Bold.ttf'):
    d = ImageDraw.Draw(img)
    d.text((x, y), texto, font=ImageFont.truetype(FUENTE + fuente, tam), fill=color)


# ----------------------------------------------------------------------
#  El fondo del mar: arena, pilares-sello y la luz de arriba
# ----------------------------------------------------------------------
def suelo(lz, cam, ext=22, desde=-36, prof=40, niebla=None):
    """La arena y las losas de prismarina (el de nerea_escenas, hasta la camara)."""
    qs = []
    r = random.Random(5)
    for gx in range(-ext, ext):
        for gz in range(desde, prof):
            mat = 'arena' if r.random() < 0.75 else 'prisma_osc'
            h = 0.0 if abs(gx) < 8 and abs(gz) < 8 else r.choice([0, 0, 0, 0.0625])
            qs.append(([(gx, h, gz), (gx + 1, h, gz), (gx + 1, h, gz + 1), (gx, h, gz + 1)],
                       [(0, 0), (1, 0), (1, 1), (0, 1)], mat))
    nm.dibujar(lz, cam, qs, ne.LUCES_MAR[:1], (0.16, 0.24, 0.3), niebla)


def fondo(lz, cam, niebla, pilares=True, ext=22, prof=40):
    suelo(lz, cam, ext=ext, prof=prof, niebla=niebla)
    if pilares:
        pil = ne.pilar(-13, 14, 9) + ne.pilar(14, 13, 8) + ne.pilar(-20, 2, 6)
        nm.dibujar(lz, cam, pil, LUCES, AMB, niebla)


def acabar(lz, cam, W, H, nombre, semilla, rayos=1.0):
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS
    img = ne.componer(lz, W, H, horiz, semilla, rayos)
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    return img


# ----------------------------------------------------------------------
#  Texturas de los efectos (RGBA uint8)
# ----------------------------------------------------------------------
def mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def tex_ola(color, w=64, h=40, semilla=1):
    """Una ola vista de lado: el cuerpo de agua del color de la fase, mas claro
    hacia arriba, y la cresta de espuma blanca rota."""
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    for x in range(w):
        cresta = 0.16 + 0.06 * math.sin(x * 0.45) + r.uniform(-0.03, 0.03)
        for y in range(h):
            v = y / (h - 1)
            if v < cresta:
                if r.random() < 0.85 * (v / cresta) + 0.2:
                    t[y, x] = (*ESPUMA, 250)
            else:
                k = (v - cresta) / (1 - cresta)
                c = mezclar(mezclar(color, (255, 255, 255), 0.45), mezclar(color, (10, 30, 60), 0.5), k)
                a = int(225 - 120 * k)
                if (x + int(y * 1.7)) % 11 == 0 and r.random() < 0.7:
                    c, a = mezclar(c, (255, 255, 255), 0.5), a + 20
                t[y, x] = (*c, min(255, a))
    return t


def tex_espiral(color, n=160, brazos=3, relleno=70):
    """El remolino en el suelo: brazos de espuma que se aprietan hacia el centro."""
    t = np.zeros((n, n, 4), np.uint8)
    y, x = np.mgrid[0:n, 0:n] + 0.5
    dx, dy = (x - n / 2) / (n / 2), (y - n / 2) / (n / 2)
    d = np.hypot(dx, dy) + 1e-6
    a = np.arctan2(dy, dx)
    s = (a * brazos / (2 * math.pi) + np.log(d) * 1.6) % 1.0
    dentro = d < 1
    t[dentro] = (*mezclar(color, (10, 30, 60), 0.35), relleno)
    t[dentro & (s < 0.22)] = (*mezclar(color, (255, 255, 255), 0.35), 200)
    t[dentro & (s < 0.07)] = (*ESPUMA, 240)
    t[(d > 0.95) & (d < 1)] = (*ESPUMA, 245)
    t[d < 0.12] = (*mezclar(color, (0, 0, 0), 0.6), 230)
    return t


def tex_burbuja(color, n=64):
    """Una burbuja bomba: pompa casi transparente con el borde claro, el
    reflejo y el nucleo del color del corazon latiendo dentro."""
    t = np.zeros((n, n, 4), np.uint8)
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d = np.hypot(x - n / 2, y - n / 2) / (n / 2)
    t[d < 1] = (*mezclar(AGUA, (255, 255, 255), 0.4), 60)
    t[(d > 0.86) & (d < 1)] = (*ESPUMA, 220)
    nucleo = d < 0.36
    k = np.clip(1 - d / 0.36, 0, 1)
    for c in range(3):
        t[..., c] = np.where(nucleo, (color[c] * (0.6 + 0.4 * k) + 255 * k ** 3 * 0.6).clip(0, 255), t[..., c])
    t[nucleo, 3] = 235
    t[np.hypot(x - n * 0.33, y - n * 0.3) / n < 0.08] = (255, 255, 255, 255)
    return t


def tex_aro(color, n=128, grueso=0.06, marcas=24, relleno=0):
    t = np.zeros((n, n, 4), np.uint8)
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d = np.hypot(x - n / 2, y - n / 2) / (n / 2)
    a = np.arctan2(y - n / 2, x - n / 2)
    t[(d > 1 - grueso) & (d < 1)] = (*color, 235)
    m = (d > 0.84) & (d < 0.9) & (((a + math.pi) / (2 * math.pi) * marcas) % 1 < 0.45)
    t[m] = (*color, 200)
    if relleno:
        t[d < 0.84] = (*color, relleno)
    return t


def tex_haz(color, w=16, h=8):
    """Un haz (rayo de la Mirada, estelas): el alma blanca y el color por fuera."""
    t = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        v = abs(y - (h - 1) / 2) / ((h - 1) / 2)
        if v < 0.3:
            c, a = (255, 255, 255), 255
        else:
            k = (v - 0.3) / 0.7
            c, a = mezclar(color, (255, 255, 255), 0.25 * (1 - k)), int(230 * (1 - k ** 1.5))
        t[y, :] = (*c, a)
    return t


def tex_columna(color, w=32, h=64, semilla=3):
    """Agua que sube: vetas verticales claras sobre el color."""
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    for x in range(w):
        fase = r.random() * h
        for y in range(h):
            if (y + fase) % 16 < 3 and x % 5 < 3:
                t[y, x] = (*ESPUMA, 230)
            else:
                t[y, x] = (*mezclar(color, (255, 255, 255), 0.25), 120 + r.randint(0, 40))
    return t


def tex_plano(color, alfa=255):
    t = np.zeros((4, 4, 4), np.uint8)
    t[...] = (*color, alfa)
    return t


def tex_galon(color, w=32, h=32):
    """Un galon (flecha) para las lineas de aviso en el suelo."""
    t = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            u, v = x / (w - 1), y / (h - 1)
            cen = abs(u - 0.5)
            if abs(v - (0.25 + cen * 0.9)) < 0.11:
                t[y, x] = (*mezclar(color, (255, 255, 255), 0.4), 245)
            elif u < 0.06 or u > 0.94:
                t[y, x] = (*color, 200)
            else:
                t[y, x] = (*mezclar(color, (0, 0, 0), 0.5), 70)
    return t


def tex_grieta(color, n=48, semilla=5):
    """Grietas de luz sobre un ojo golpeado."""
    r = random.Random(semilla)
    t = np.zeros((n, n, 4), np.uint8)
    for _ in range(5):
        x, y = n / 2, n / 2
        a = r.uniform(0, 2 * math.pi)
        for _ in range(26):
            a += r.uniform(-0.6, 0.6)
            x += math.cos(a) * 0.9
            y += math.sin(a) * 0.9
            if 0 <= int(x) < n and 0 <= int(y) < n:
                t[int(y), int(x)] = (255, 255, 255, 255)
                if int(x) + 1 < n:
                    t[int(y), int(x) + 1] = (*color, 220)
    return t


def aura_atlas(base, k=0):
    """El aura de la Furia sobre el atlas: rayos en zigzag donde hay piel."""
    h, w = base.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    quiebro = np.where((yy // 6) % 2 == 0, 3.0, -3.0)
    s = (xx + yy + quiebro + 2.0 * np.sin(2 * np.pi * yy / 24.0) + k * 4) % 14.0
    out = np.zeros((h, w, 4), np.uint8)
    out[s < 6.0] = (20, 120, 150, 255)
    out[s < 4.0] = (80, 230, 255, 255)
    out[s < 1.6] = (230, 255, 255, 255)
    out[(s > 9.0) & (s < 11.0)] = (200, 40, 160, 255)
    out[base[..., 3] < 16] = 0
    return out


# ----------------------------------------------------------------------
#  Geometria de los efectos
# ----------------------------------------------------------------------
def dibujar_trans(lz, cam, qs, tex, k=0.85, niebla=None, glow=0.0):
    qs = sorted(qs, key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2])
    for P, UV in qs:
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3) * 1.05, None, niebla, translucido=k)
            if glow:
                lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True,
                             brillo=glow)


def suelo_cuad(cx, cz, R, y=0.06, giro=0.0):
    c, s_ = math.cos(giro) * R, math.sin(giro) * R
    P = [(cx - c + s_, y, cz - s_ - c), (cx + c + s_, y, cz + s_ - c), (cx + c - s_, y, cz + s_ + c),
         (cx - c - s_, y, cz - s_ + c)]
    return [(P, [(0, 0), (1, 0), (1, 1), (0, 1)])]


def billboard(p, tam, cam, giro=0.0):
    p = np.array(p, float)
    c, s_ = math.cos(giro), math.sin(giro)
    rr, uu = cam.r * c + cam.u * s_, -cam.r * s_ + cam.u * c
    P = [p - rr * tam - uu * tam, p + rr * tam - uu * tam, p + rr * tam + uu * tam, p - rr * tam + uu * tam]
    return ([tuple(q) for q in P], [(0, 1), (1, 1), (1, 0), (0, 0)])


def cinta3d(pts, ancho, cam):
    out = []
    for i in range(len(pts) - 1):
        a, b = np.array(pts[i], float), np.array(pts[i + 1], float)
        v = cam.ojo - (a + b) / 2
        lado = np.cross(b - a, v)
        lado = lado / (np.linalg.norm(lado) + 1e-9) * ancho
        u0, u1 = i / (len(pts) - 1), (i + 1) / (len(pts) - 1)
        out.append(([a - lado, b - lado, b + lado, a + lado], [(u0, 1), (u1, 1), (u1, 0), (u0, 0)]))
    return out


def ola(cx, cz, rumbo, abre, R, alto, n=14, curva=0.35):
    """Un arco de ola a R bloques del centro, centrado en el rumbo (grados) y
    de 'abre' grados: la pared sube y la cresta se vuelca hacia delante."""
    out = []
    for i in range(n):
        a0 = math.radians(rumbo - abre / 2 + abre * i / n)
        a1 = math.radians(rumbo - abre / 2 + abre * (i + 1) / n)
        u0, u1 = i / n * 3, (i + 1) / n * 3
        for (h0, h1, v0, v1, d0, d1) in ((0, alto * 0.7, 1.0, 0.45, 0, 0), (alto * 0.7, alto, 0.45, 0.0, 0, curva * alto)):
            P = [(cx + math.cos(a0) * (R + d0), h0, cz + math.sin(a0) * (R + d0)),
                 (cx + math.cos(a1) * (R + d0), h0, cz + math.sin(a1) * (R + d0)),
                 (cx + math.cos(a1) * (R + d1), h1, cz + math.sin(a1) * (R + d1)),
                 (cx + math.cos(a0) * (R + d1), h1, cz + math.sin(a0) * (R + d1))]
            out.append((P, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]))
    return out


def pared(x0, z0, x1, z1, alto, curva=0.4, n=24):
    """Una pared de agua recta (la Gran Marea); la cresta se vuelca hacia -Z."""
    out = []
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        ax, az = x0 + (x1 - x0) * t0, z0 + (z1 - z0) * t0
        bx, bz = x0 + (x1 - x0) * t1, z0 + (z1 - z0) * t1
        u0, u1 = t0 * 8, t1 * 8
        for (h0, h1, v0, v1, d0, d1) in ((0, alto * 0.72, 1.0, 0.45, 0, 0), (alto * 0.72, alto, 0.45, 0.0, 0, -curva * alto)):
            P = [(ax, h0, az + d0), (bx, h0, bz + d0), (bx, h1, bz + d1), (ax, h1, az + d1)]
            out.append((P, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]))
    return out


def cilindro(cx, cz, r, h0, h1, n=18, giro=0.0, rep=2.0, r1=None):
    out = []
    r1 = r if r1 is None else r1
    for i in range(n):
        a0 = giro + 2 * math.pi * i / n
        a1 = giro + 2 * math.pi * (i + 1) / n
        P = [(cx + math.cos(a0) * r, h0, cz + math.sin(a0) * r), (cx + math.cos(a1) * r, h0, cz + math.sin(a1) * r),
             (cx + math.cos(a1) * r1, h1, cz + math.sin(a1) * r1), (cx + math.cos(a0) * r1, h1, cz + math.sin(a0) * r1)]
        out.append((P, [(i / n * rep, 1), ((i + 1) / n * rep, 1), ((i + 1) / n * rep, 0), (i / n * rep, 0)]))
    return out


def linea_suelo(x0, z0, x1, z1, ancho, y=0.07, paso=2.0):
    d = np.array([x1 - x0, z1 - z0], float)
    L = np.linalg.norm(d)
    d /= L
    lado = np.array([-d[1], d[0]]) * ancho
    P = [(x0 - lado[0], y, z0 - lado[1]), (x0 + lado[0], y, z0 + lado[1]),
         (x1 + lado[0], y, z1 + lado[1]), (x1 - lado[0], y, z1 - lado[1])]
    return [(P, [(0, 0), (1, 0), (1, L / paso), (0, L / paso)])]


def ancla(p, rumbo=0.0, escala=1.0, inclina=0.0):
    """Un ancla de prismarina oxidada (la del Arpon y el Molino), en p."""
    k = escala
    cajas = [((-1.3 * k, 0, -1.3 * k, 2.6 * k, 19 * k, 2.6 * k), 'prisma_osc'),
             ((-2.6 * k, -2.5 * k, -0.9 * k, 5.2 * k, 3 * k, 1.8 * k), 'oxido'),
             ((-1.1 * k, 2.5 * k, -8 * k, 2.2 * k, 2.2 * k, 16 * k), 'oxido'),
             ((-2 * k, 18 * k, -2 * k, 4 * k, 3.5 * k, 4 * k), 'prisma_osc')]
    brazos = [nm.nodo('ancla_' + n, (0, 20 * k, 0), (0, 0, s * 128), [
        ((-1.2 * k, 0, -1.2 * k, 2.4 * k, 11 * k, 2.4 * k), 'prisma_osc'),
        ((-3.4 * k, 7 * k, -1.4 * k, 6.8 * k, 6 * k, 2.8 * k), 'prisma_osc')]) for s, n in ((1, 'i'), (-1, 'd'))]
    raiz = nm.nodo('ancla', (0, 0, 0), (inclina, rumbo, 0), cajas, brazos)
    M = vr.T(*p) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])
    return nm.quads(raiz, {}, M)


# ----------------------------------------------------------------------
#  1. El cuerpo: heroica, vistas, fases y escala
# ----------------------------------------------------------------------
def heroica(cual, W=1600, H=900, fase=1, nombre=None, aura=False):
    cam = vr.Camara(ojo=(-11.0, 2.4, -27.0), objetivo=(1.2, 8.0, 0), fov=50, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(16, 40)
    fondo(lz, cam, niebla)
    for (x, z, g) in ((-6.0, -9.0, 200), (4.0, -10.5, 170), (-1.5, -13.0, 185), (9.0, -6.0, 130), (-10.0, -5.0, 230)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    a = None
    if aura:
        base, _, _, _ = nr.atlas(cual, fase)
        a = aura_resplandor(base)
    p = pose('ROMPEOLAS', 0.18, fase=fase)
    nerea(lz, cam, cual, 0, 2, 22, p=p, fase=fase, niebla=niebla, luces=LUCES, amb=AMB, brillo=1.55, aura=a)
    if aura:
        # motas del abismo que le suben por el cuerpo y rayos de agua alrededor
        r = random.Random(9)
        tb = tex_burbuja((230, 60, 190))
        for _ in range(70):
            q = (r.uniform(-4.5, 4.5), r.uniform(0.5, 16.0), 2 + r.uniform(-3.0, 3.0))
            dibujar_trans(lz, cam, [billboard(q, r.uniform(0.12, 0.3), cam)], tb, 0.8, niebla, 0.7)
        th = tex_haz((60, 220, 240))
        for k in range(10):
            a0 = r.uniform(0, 2 * math.pi)
            pts = [(math.cos(a0 + t * 0.9) * (3.5 + t), 1 + t * 3.2, 2 + math.sin(a0 + t * 0.9) * (3.5 + t)) for t in
                   np.linspace(0, 1.4, 6)]
            dibujar_trans(lz, cam, cinta3d(pts, 0.1, cam), th, 0.7, niebla, 0.6)
    acabar(lz, cam, W, H, nombre or f'heroica_{cual}' + ('' if fase == 1 else f'_f{fase}'), 3)


def vistas(cual, W=1800, H=680):
    img = Image.new('RGB', (W, H), (237, 242, 245))
    w = W // 3
    for i, g in enumerate((0, -90, 180)):
        cam = vr.Camara(ojo=(0, 8.6, -90), objetivo=(0, 8.6, 0), fov=12.5, ancho=w * SS, alto=H * SS)
        lz = vr.Lienzo(w * SS, H * SS)
        nerea(lz, cam, cual, 0, 0, g, fase=1)
        img.paste(estudio(lz, w, H), (i * w, 0))
    img.save(os.path.join(OUT, f'vistas_{cual}.jpg'), quality=92)


def fases(cual, W=1800, H=620):
    img = Image.new('RGB', (W, H), (237, 242, 245))
    w = W // 4
    for i, f in enumerate((1, 2, 3, 4)):
        cam = vr.Camara(ojo=(-8, 8.6, -88), objetivo=(0, 8.6, 0), fov=12.5, ancho=w * SS, alto=H * SS)
        lz = vr.Lienzo(w * SS, H * SS)
        nerea(lz, cam, cual, 0, 0, -18, fase=f)
        img.paste(estudio(lz, w, H, emis=0.6), (i * w, 0))
        rotulo(img, ['FASE I', 'FASE II', 'FASE III', 'FASE IV'][i], i * w + 18, 12, 28, (20, 40, 56))
    img.save(os.path.join(OUT, f'fases_{cual}.jpg'), quality=92)


def escala(W=1600, H=820):
    cam = vr.Camara(ojo=(0.6, 9.6, -120), objetivo=(0.6, 9.6, 0), fov=10.0, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    jugador(lz, cam, 9.0, 0, -20, luces=LUZ_ESTUDIO)
    nerea(lz, cam, 'antes', 3.6, 0, -20)
    nerea(lz, cam, 'despues', -6.0, 0, -20)
    img = estudio(lz, W, H).convert('RGBA')
    rej = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rej)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 20)
    for b in range(0, 17, 2):
        _, y, _ = cam.proyectar((0.6, b, 0)); y /= SS
        d.line((70, y, W - 20, y), fill=(40, 70, 80, 110 if b else 220), width=2 if b == 0 else 1)
        d.text((20, y - 12), f'{b}', font=f, fill=(40, 70, 80, 255))
    img = Image.alpha_composite(img, rej)
    d = ImageDraw.Draw(img)
    fn = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 30)
    fa = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 19)
    for nombre, x, alto, techo in (('JUGADOR', 9.0, '1,8', 2.2), ('NEREA HOY', 3.6, 'unos 10', 11.4),
                                   ('NEREA NUEVA', -6.0, 'unos 15', 18.0)):
        px_, py, _ = cam.proyectar((x, techo, 0)); px_ /= SS; py /= SS
        cifra = alto + ' bloques'
        wn = d.textlength(nombre, font=fn); wa = d.textlength(cifra, font=fa)
        d.text((px_ - wn / 2, py - 66), nombre, font=fn, fill=(16, 52, 60, 255))
        d.text((px_ - wa / 2, py - 26), cifra, font=fa, fill=(60, 96, 104, 255))
    img.convert('RGB').save(os.path.join(OUT, 'escala.jpg'), quality=92)


# ----------------------------------------------------------------------
#  2. Ataques rehechos
# ----------------------------------------------------------------------
def rompeolas(W=1600, H=900, fase=2):
    """Tres olas en abanico, mas altas que un jugador, con la cresta de espuma
    y el color de la fase; entre ola y ola, un hueco por donde pasar."""
    cam = vr.Camara(ojo=(7.0, 4.5, -25.0), objetivo=(0.0, 5.0, -2.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(20, 46)
    fondo(lz, cam, niebla)
    cz = 6.0
    nerea(lz, cam, 'despues', 0, cz, 0, p=pose('ROMPEOLAS', 0.55, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    t_s = tex_galon(COLOR[fase])
    olas = []
    for rumbo, R in ((-90 - 30, 13.0), (-90, 16.0), (-90 + 30, 12.0)):
        olas += ola(0, cz, rumbo, 24, R, 4.6, n=18)
        a = math.radians(rumbo)
        dibujar_trans(lz, cam, linea_suelo(math.cos(a) * 5, cz + math.sin(a) * 5, math.cos(a) * (R - 1.5),
                                           cz + math.sin(a) * (R - 1.5), 1.3), t_s, 0.7, niebla, 0.3)
    # uno en el hueco entre dos olas (a salvo), dos que se la llevan, uno lejos
    for (x, z, g) in ((-4.6, -6.0, 10), (0.4, -11.5, -5), (7.4, -4.8, 20), (-10.0, -12.0, -20)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    dibujar_trans(lz, cam, olas, tex_ola(COLOR[fase]), 0.9, niebla, 0.4)
    acabar(lz, cam, W, H, 'rompeolas', 11)


def remolino(W=1600, H=900, fase=1):
    """El remolino: la espiral de espuma en el suelo (hasta donde tira), el agua
    que le sube alrededor y un jugador con antorcha, a salvo en su burbuja."""
    cam = vr.Camara(ojo=(7.0, 15.0, -27.0), objetivo=(0.0, 3.5, 0.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(20, 46)
    fondo(lz, cam, niebla)
    dibujar_trans(lz, cam, suelo_cuad(0, 0, 11.5, giro=0.3), tex_espiral(COLOR[fase]), 0.9, niebla, 0.25)
    nerea(lz, cam, 'despues', 0, 0, 0, p=pose('REMOLINO', 2.0, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    for (x, z, g) in ((6.5, -6.0, 40), (-7.0, -5.0, -30), (8.5, 3.0, 80)):
        jugador(lz, cam, x, z, g, niebla=niebla)
        pts = [(x * k, 0.9, z * k) for k in (1.4, 1.25, 1.1, 0.95)]
        dibujar_trans(lz, cam, cinta3d(pts, 0.14, cam), tex_haz(ESPUMA), 0.8, niebla, 0.3)
    dibujar_trans(lz, cam, cilindro(0, 0, 3.6, 0, 6.5, 22, 0.4, 3, r1=5.4), tex_columna(COLOR[fase]), 0.3, niebla, 0.1)
    jugador(lz, cam, -2.0, -10.0, 0, niebla=niebla)
    dibujar_trans(lz, cam, [billboard((-2.0, 1.0, -10.0), 1.5, cam)], tex_burbuja((255, 196, 90)), 0.55, niebla, 0.6)
    acabar(lz, cam, W, H, 'remolino', 21)


def burbujas(W=1600, H=900, fase=1):
    """Burbujas bomba: pompas con el corazon latiendo dentro y, bajo cada una,
    el aro de hasta donde revienta; una revienta de un flechazo, sin dano."""
    cam = vr.Camara(ojo=(11.0, 6.0, -27.0), objetivo=(0.0, 5.0, -3.0), fov=54, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(20, 46)
    fondo(lz, cam, niebla)
    nerea(lz, cam, 'despues', 0, 5, 0, p=pose('BURBUJAS', 0.5, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    corazon = (224, 20, 76)
    tb = tex_burbuja(corazon)
    ta = tex_aro(corazon, grueso=0.06, relleno=22)
    bur = [(-4.0, 4.5, -3.0, 1.1), (1.5, 6.5, -1.0, 1.25), (5.0, 3.5, -5.0, 1.0), (-1.0, 3.0, -8.0, 1.05),
           (-7.5, 6.0, -6.5, 0.95)]
    for (x, y, z, s) in bur:
        dibujar_trans(lz, cam, suelo_cuad(x, z, 3.0, giro=0.2), ta, 0.7, niebla, 0.3)
    for (x, z, g) in ((-3.0, -13.0, 0), (4.0, -12.0, 15), (-9.0, -11.0, -20)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    for (x, y, z, s) in bur:
        dibujar_trans(lz, cam, [billboard((x, y, z), s, cam)], tb, 0.75, niebla, 0.55)
    # la que revienta de un flechazo: espuma, sin dano
    tfo = tex_burbuja(ESPUMA)
    for k in range(10):
        a = k * 0.63
        dibujar_trans(lz, cam, [billboard((8.0 + math.cos(a) * 1.3, 6.0 + math.sin(a) * 1.3, -7.0), 0.32, cam)], tfo, 0.8,
                      niebla, 0.4)
    dibujar_trans(lz, cam, cinta3d([(4.0, 1.6, -12.0), (8.0, 6.0, -7.0)], 0.05, cam), tex_plano((240, 230, 210)), 1.0, niebla)
    acabar(lz, cam, W, H, 'burbujas', 31)


def molino(W=1600, H=900, fase=2):
    """El Molino: dos cadenas con un ancla en la punta barren un anillo de 14
    bloques, dejando una estela de agua; un jugador la salta."""
    cam = vr.Camara(ojo=(9.0, 21.0, -27.0), objetivo=(0.0, 2.0, 0.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(24, 50)
    fondo(lz, cam, niebla)
    nerea(lz, cam, 'despues', 0, 0, 0, p=pose('MOLINO', 1.2, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    R, alto = 14.0, 1.0
    dibujar_trans(lz, cam, suelo_cuad(0, 0, R + 0.6), tex_aro(COLOR[fase], grueso=0.025, marcas=48), 0.6, niebla, 0.3)
    for ang in (-60, 120):
        a = math.radians(ang)
        mano = (math.cos(a) * 3.0, 7.5, math.sin(a) * 3.0)
        punta = (math.cos(a) * R, alto, math.sin(a) * R)
        nm.dibujar(lz, cam, nm.cadena_mundo(mano, punta, 2.4), LUCES, AMB, niebla)
        nm.dibujar(lz, cam, ancla(punta, rumbo=-ang + 90, escala=1.7, inclina=70), LUCES, AMB, niebla)
        arco = [(math.cos(math.radians(ang + 8 + k * 6)) * R, alto + 0.4, math.sin(math.radians(ang + 8 + k * 6)) * R)
                for k in range(14)]
        dibujar_trans(lz, cam, cinta3d(arco, 0.6, cam), tex_ola(COLOR[fase], 32, 16), 0.75, niebla, 0.35)
    for (x, z, g, y) in ((5.5, -13.0, 10, 1.5), (-10.0, -9.5, -40, 0.0), (12.0, 6.0, 80, 0.0), (-3.0, -6.0, 0, 0.0)):
        jugador(lz, cam, x, z, g, y=y, niebla=niebla)
    acabar(lz, cam, W, H, 'molino', 41)


def arpon(W=1600, H=900, fase=2):
    """El Arpon: el ancla vuela hacia el mas lejano con la cadena y una estela de
    agua; bajo el, el aro de fijado."""
    cam = vr.Camara(ojo=(24.0, 8.0, -8.0), objetivo=(0.0, 5.0, -4.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(22, 50)
    fondo(lz, cam, niebla)
    nerea(lz, cam, 'despues', 0, 8, 0, p=pose('ARPON_LANZAR', 0.86, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    mano = np.array([-2.5, 9.0, 6.0])
    blanco = np.array([1.0, 0.0, -18.0])
    punta = np.array([0.8, 2.8, -13.0])
    pts = [tuple(mano + (punta - mano) * k + np.array([0, -1.5 * math.sin(math.pi * k), 0])) for k in np.linspace(0, 1, 8)]
    for i in range(len(pts) - 1):
        nm.dibujar(lz, cam, nm.cadena_mundo(pts[i], pts[i + 1], 2.0), LUCES, AMB, niebla)
    dibujar_trans(lz, cam, cinta3d([tuple(np.array(q) + np.array([0, 0.5, 0])) for q in pts], 0.55, cam),
                  tex_haz(AGUA), 0.5, niebla, 0.3)
    nm.dibujar(lz, cam, ancla(tuple(punta), rumbo=0, escala=1.6, inclina=-85), LUCES, AMB, niebla)
    dibujar_trans(lz, cam, suelo_cuad(blanco[0], blanco[2], 2.4, giro=0.4),
                  tex_aro(COLOR[fase], grueso=0.1, marcas=8, relleno=40), 0.85, niebla, 0.5)
    jugador(lz, cam, blanco[0], blanco[2], 0, niebla=niebla)
    jugador(lz, cam, -6.0, -11.0, -10, niebla=niebla)
    acabar(lz, cam, W, H, 'arpon', 51)


def mirada(W=1600, H=900, fase=3):
    """La Mirada: los ojos crecen y se rajan con cada flechazo (los dos que hay
    que romper); el rayo doble va hacia uno que se esconde tras un bloque."""
    cam = vr.Camara(ojo=(15.0, 7.0, -22.0), objetivo=(-1.0, 7.5, 0.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(20, 46)
    fondo(lz, cam, niebla)
    p = pose('MIRADA', 2.0, fase=fase)
    nerea(lz, cam, 'despues', 0, 6, 0, p=p, fase=fase, niebla=niebla, luces=LUCES, amb=AMB, brillo=1.5)
    nr.usar('despues')
    M = vr.entidad_a_mundo(0, 0, 6, 0, nr.ESCALA['despues'])
    Ms = nj.matrices(p)
    ojos = [(M @ Ms[n] @ np.array([0, 0, -0.6, 1.0]))[:3] for n in ('ojo_izq', 'ojo_der')]
    medio = (ojos[0] + ojos[1]) / 2
    blanco = np.array([-5.0, 1.2, -14.0])
    th = tex_haz(COLOR[fase])
    for o in ojos:
        dibujar_trans(lz, cam, cinta3d([o, medio + (blanco - medio) * 0.3, blanco], 0.35, cam), th, 0.9, niebla, 0.8)
    caja = nm.nodo('bloque', (0, 0, 0), (0, 0, 0), [((-8, -32, -8, 16, 32, 16), 'prisma_osc')])
    nm.dibujar(lz, cam, nm.quads(caja, {}, vr.T(-4.6, 0, -12.6) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])), LUCES, AMB, niebla)
    jugador(lz, cam, -5.0, -14.2, 0, niebla=niebla)
    for (x, z, g) in ((5.0, -12.0, 15), (8.0, -9.0, 30), (2.0, -15.0, 5)):
        jugador(lz, cam, x, z, g, niebla=niebla)
        o = ojos[1 if x > 4 else 0]
        q = np.array([x, 1.5, z])
        dibujar_trans(lz, cam, cinta3d([q, q + (o - q) * 0.75], 0.04, cam), tex_plano((240, 236, 220)), 1.0, niebla, 0.2)
    tg = tex_grieta(COLOR[fase])
    for i, o in enumerate(ojos):
        dibujar_trans(lz, cam, [billboard(o, 1.0, cam)], tex_aro(COLOR[fase], 48, 0.12, 6), 0.9, niebla, 0.8)
        dibujar_trans(lz, cam, [billboard(o, 0.8, cam, giro=i)], tg, 0.9, niebla, 0.6)
    acabar(lz, cam, W, H, 'mirada', 61)


def geiser(W=1600, H=900, fase=2):
    """Geiser del Abismo (nuevo): bajo cada jugador se abre un remolino oscuro
    (1,5 s de aviso) y revienta en una columna de agua que lo lanza al cielo."""
    cam = vr.Camara(ojo=(13.0, 7.0, -30.0), objetivo=(0.0, 6.5, -3.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(22, 50)
    fondo(lz, cam, niebla)
    nerea(lz, cam, 'despues', 0, 8, 0, p=pose('REMOLINO', 0.75, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    te = tex_espiral(COLOR[fase], brazos=2, relleno=120)
    for (x, z) in ((-6.0, -8.0), (-1.5, -14.0), (8.5, -10.0)):
        dibujar_trans(lz, cam, suelo_cuad(x, z, 1.8, giro=x), te, 0.9, niebla, 0.45)
        jugador(lz, cam, x, z, 0, niebla=niebla)
    gx, gz = 9.5, -3.0
    dibujar_trans(lz, cam, suelo_cuad(gx, gz, 2.3), te, 0.9, niebla, 0.45)
    dibujar_trans(lz, cam, cilindro(gx, gz, 1.7, 0, 13.0, 18, 0.2, 2, r1=1.2), tex_columna(AGUA, semilla=7), 0.75, niebla, 0.3)
    for k in range(12):
        a = k * 0.55
        dibujar_trans(lz, cam, [billboard((gx + math.cos(a) * 1.8, 13.0 + math.sin(k * 1.3) * 0.7, gz + math.sin(a) * 1.8),
                                          0.55, cam)], tex_burbuja(ESPUMA), 0.8, niebla, 0.4)
    jugador(lz, cam, gx, gz, 30, y=14.0, niebla=niebla)
    acabar(lz, cam, W, H, 'geiser', 71)


def marea(W=1600, H=900, fase=3):
    """La Gran Marea (nueva): alza el tridente y una ola de 7 bloques cruza la
    arena hacia los jugadores; hay un solo hueco, marcado en el suelo."""
    cam = vr.Camara(ojo=(2.0, 5.0, -24.0), objetivo=(0.0, 6.0, 4.0), fov=66, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(26, 54)
    fondo(lz, cam, niebla, ext=34)
    nerea(lz, cam, 'despues', 0, 16, 0, p=pose('REMOLINO', 0.75, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    zf = 5.0
    hueco = (-6.0, -1.5)
    qs = pared(-32, zf, hueco[0], zf, 9.0) + pared(hueco[1], zf, 32, zf, 9.0)
    medio = (hueco[0] + hueco[1]) / 2
    dibujar_trans(lz, cam, linea_suelo(medio, zf - 1, medio, -14, 2.0), tex_galon(ESPUMA), 0.8, niebla, 0.5)
    for (x, z, g) in ((-2.0, -2.0, 30), (6.0, -6.0, 60), (-12.0, -7.0, -40), (12.0, -2.0, 80), (-5.0, -10.0, 10)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    dibujar_trans(lz, cam, qs, tex_ola(COLOR[fase], semilla=4), 0.9, niebla, 0.3)
    acabar(lz, cam, W, H, 'marea', 81)


def furia(W=1600, H=900):
    heroica('despues', W, H, fase=4, nombre='furia', aura=True)


def aura_resplandor(base):
    """El aura de la Furia para los renders: un resplandor del abismo (de cian a
    magenta segun la fila del atlas) donde hay piel."""
    h, w = base.shape[:2]
    out = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    banda = ((xx + yy) // 5) % 3 == 0
    out[...] = (40, 200, 230, 255)
    out[banda] = (230, 60, 190, 255)
    out[base[..., 3] < 16] = 0
    return out


ESCENAS = {
    'heroica_antes': lambda: heroica('antes'), 'heroica_despues': lambda: heroica('despues'),
    'heroica_despues_f4': lambda: heroica('despues', fase=4),
    'vistas_antes': lambda: vistas('antes'), 'vistas_despues': lambda: vistas('despues'),
    'fases_antes': lambda: fases('antes'), 'fases_despues': lambda: fases('despues'),
    'escala': escala,
    'rompeolas': rompeolas, 'remolino': remolino, 'burbujas': burbujas, 'molino': molino, 'arpon': arpon,
    'mirada': mirada, 'geiser': geiser, 'marea': marea, 'furia': furia,
}

if __name__ == '__main__':
    solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in solo:
        ESCENAS[k]()
        print(k, flush=True)

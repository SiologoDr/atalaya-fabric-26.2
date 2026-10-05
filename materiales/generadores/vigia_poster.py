"""
Poster promocional del Vigia, con el mismo formato que los de Aeralis y Nerea:
el bicho grande a la derecha, su nombre a la izquierda y nada mas (ni
jugadores, ni lista de ataques, ni franja de datos).

El Vigia de noche, visto desde el suelo, alto como una torre: a media
zancada, una garra alzada contra una luna grande —que lo recorta y le saca
rayos de luz por entre los brazos—, la otra abierta, la capa al viento y el
farol de la cabeza encendido en rojo de caza.

Efectos:
  - La Mirada, el protagonista: el rayo sale del ojo y viene hacia quien mira,
    con el destello del ojo, las rayas de calor que se abren hacia la camara y
    chispas que saltan a su paso.
  - La maldicion, envolviendolo: tres espirales de humo maldito que suben a su
    alrededor abriendose como un embudo (por detras de el; por delante solo le
    pasan por las piernas), y en ellas los sellos de la maldicion, cerca y lejos.
  - Brasas, ceniza y humo a distintas profundidades; niebla baja.
En el horizonte, las colinas y la atalaya con su ventana encendida.

Todo lo que sale esta hecho para el mod: la malla y las texturas del Vigia
(via vigia_render.py), la malla de su rayo (la de RayoVigiaModel), sus
particulas, el humo de la maldicion (una textura en pixeles pintada aqui), el
cielo, la luna, el suelo y la atalaya. Las fuentes son las del sistema.

Uso: python vigia_poster.py <raiz del proyecto> <salida.png> [escala]
"""
import math, os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
ESCALA = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
P = os.path.join(A, 'particle')
FUENTES = 'C:/Windows/Fonts/'
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
SS = 2                                    # supermuestreo: se pinta al doble y se reduce

AMBAR = (255, 180, 58, 255)
ROJO = (255, 64, 40, 255)
BLANCO = (245, 242, 236, 255)
GRIS = (196, 190, 200, 255)

# ----------------------------------------------------------------------
#  La pose: dispara La Mirada. Se yergue a media zancada, alza una garra
#  —que se recorta contra la luna— y abre la otra hacia abajo, por debajo
#  del rayo; la capa vuela y el ojo, dilatado, apunta hacia quien mira.
# ----------------------------------------------------------------------
POSE = {
    'torso':        {'rot': (-16, 14, 3)},
    'cuello':       {'rot': (-4, 0, 0)},
    'cabeza':       {'rot': (8, -14, 8)},
    'ojo':          {'esc': 1.6},
    'capa':         {'rot': (34, 0, 7)},
    'brazo_izq':    {'rot': (18, -10, -50)},
    'antebrazo_izq': {'rot': (-60, 0, 0)},
    'garras_izq':   {'rot': (50, 0, 0)},
    'brazo_der':    {'rot': (10, 15, 100)},
    'antebrazo_der': {'rot': (-55, 0, 0)},
    'garras_der':   {'rot': (45, 0, 0)},
    'pierna_izq':   {'rot': (-24, 0, -7)},
    'espinilla_izq': {'rot': (28, 0, 0)},
    'pie_izq':      {'rot': (-6, 0, 0)},
    'pierna_der':   {'rot': (20, 0, 9)},
    'espinilla_der': {'rot': (12, 0, 0)},
}

# ----------------------------------------------------------------------
#  Escena: camara a ras de suelo, mirando hacia arriba. Apunta a la
#  izquierda del Vigia (la X de pantalla va al reves que la del mundo): asi
#  el queda en la mitad derecha y el texto respira a la izquierda.
# ----------------------------------------------------------------------
VIGIA_EN = (0.0, 0.0, 0.0)
GUINADA = float(os.environ.get('GUINADA', '35'))
CAM = vr.Camara(ojo=(0.8, 0.3, -5.8), objetivo=(1.3, 2.15, 0.0), fov=44, ancho=W * SS, alto=H * SS)

LUCES = [
    # (la X del mundo va al reves que la de pantalla: +X es la izquierda)
    ((0.2, 0.5, -0.8), (0.46, 0.54, 0.86), 0.5, 'llave'),     # el cielo de noche, de frente y flojo
    ((0.7, 0.6, 0.5), (0.62, 0.70, 1.0), 1.25, 'contra'),      # la luna, detras a la izquierda: borde frio
    ((-0.8, 0.15, 0.6), (1.0, 0.22, 0.12), 1.5, 'contra'),     # el resplandor rojo del horizonte, a la derecha
    ((-0.6, 0.3, -0.75), (1.0, 0.45, 0.16), 0.16, 'llave'),    # el rayo alumbra de frente por la derecha
    ((0.2, -1.0, -0.2), (0.35, 0.12, 0.08), 0.3, 'llave'),     # rebote calido del suelo
]
AMBIENTE = (0.09, 0.08, 0.13)

LUNA_C, LUNA_R = (1075, 235), 150          # en pixeles del poster a 1920x1080


class Niebla:
    color = (0.11, 0.05, 0.10)

    def __call__(self, z):
        return np.clip((z - 6.0) / 24.0, 0, 0.94)


def suelo_tex():
    """Losas de piedra musgosa oscura, 16x16, pintadas aqui."""
    r = random.Random(3)
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            base = r.choice([(46, 48, 56), (52, 54, 62), (40, 42, 50), (58, 60, 68)])
            if r.random() < 0.18:
                base = r.choice([(40, 58, 44), (48, 66, 50)])      # musgo
            if x == 0 or y == 0:
                base = (30, 30, 38)                                 # junta
            t[y, x] = (*base, 255)
    return t


# ----------------------------------------------------------------------
#  Utilidades de composicion
# ----------------------------------------------------------------------
def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, int(tam * ESCALA))


def px(n):
    return int(round(n * ESCALA))


def sumar(base, capa_rgb, k=1.0):
    f = np.array(base).astype(float)
    f[..., :3] = np.clip(f[..., :3] + np.array(capa_rgb).astype(float)[..., :3] * k, 0, 255)
    return Image.fromarray(f.astype(np.uint8))


def sprite(nombre, lado, alfa=1.0):
    im = Image.open(os.path.join(P, nombre)).convert('RGBA')
    im = im.resize((max(1, int(lado)), max(1, int(lado * im.height / im.width))), Image.NEAREST)
    if alfa < 1.0:
        im.putalpha(im.getchannel('A').point(lambda v: int(v * alfa)))
    return im


def pegar(capa, s, x, y):
    capa.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2)))


def pantalla(p):
    """Del mundo al poster: (x, y) en pixeles de la imagen final y la profundidad."""
    sx, sy, z = CAM.proyectar(np.asarray(p, float))
    return sx / SS, sy / SS, z


def delante_del_eje(p):
    """Si un punto queda entre la camara y el eje del Vigia (a su misma altura)."""
    eje = np.array([VIGIA_EN[0], p[1], VIGIA_EN[2]])
    return (np.asarray(p) - eje) @ CAM.f < 0


def a_imagen(arr):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return im.resize((W, H), Image.LANCZOS)


def mascara(arr):
    return np.array(a_imagen(arr)).astype(float) / 255.0


def desenfocar(arr, radio):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return np.array(im.filter(ImageFilter.GaussianBlur(radio))).astype(float) / 255.0


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


# ----------------------------------------------------------------------
#  La luna: un disco de pixeles con sus crateres, pintado aqui
# ----------------------------------------------------------------------
def luna_pixel(n=22):
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    c = (n - 1) / 2
    # crateres: (x, y, radio) en pixeles de la luna; el borde de abajo a la
    # derecha de cada uno, en sombra
    crateres = [(7, 6, 2.2), (14, 9, 1.6), (9, 14, 2.6), (15, 15, 1.3), (5, 11, 1.1), (12, 4, 1.0)]
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - c, y - c)
            if d > n / 2 - 0.3:
                continue
            # luz desde arriba a la izquierda, borde algo mas oscuro
            k = 0.9 + 0.08 * ((c - x) + (c - y)) / n - 0.1 * (d / (n / 2)) ** 4
            for cx, cy, cr in crateres:
                dc = math.hypot(x - cx, y - cy)
                if dc < cr:
                    k -= 0.1
                elif dc < cr + 1 and (x - cx) + (y - cy) > 0:
                    k -= 0.05
            k = max(0.6, min(1.0, round(k * 20) / 20))      # pocos tonos, como un pixel-art
            im.putpixel((x, y), (int(238 * k), int(232 * k), int(242 * k), 255))
    return im


# ----------------------------------------------------------------------
#  Cielo y horizonte: todo pintado aqui
# ----------------------------------------------------------------------
def cielo(horizonte_y, centro_brillo):
    """El cielo (sin la luna) en flotante, HxWx3."""
    y = np.linspace(0, 1, H)[:, None, None]
    arriba = np.array([8, 7, 20]) / 255.0
    medio = np.array([24, 12, 36]) / 255.0
    abajo = np.array([84, 18, 30]) / 255.0
    t = np.clip(y / (horizonte_y / H), 0, 1)
    col = np.where(t < 0.55, arriba + (medio - arriba) * (t / 0.55), medio + (abajo - medio) * ((t - 0.55) / 0.45))
    col = np.broadcast_to(col, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    # el resplandor rojo detras del Vigia, que sube desde el horizonte
    cx, cy = centro_brillo
    d = np.hypot((xx - cx) / (W * 0.30), (yy - cy) / (H * 0.55))
    col += np.array([0.70, 0.09, 0.06])[None, None] * np.exp(-d ** 2 * 1.5)[..., None] * 0.85
    # el halo frio de la luna
    lx, ly, lr = px(LUNA_C[0]), px(LUNA_C[1]), px(LUNA_R)
    dl = np.hypot(xx - lx, yy - ly) / lr
    col += np.array([0.30, 0.30, 0.48])[None, None] * (np.exp(-np.maximum(dl - 1, 0) * 1.6) * (dl > 0.9))[..., None] * 0.55
    return col


def estrellas(img, horizonte_y):
    d2 = ImageDraw.Draw(img)
    r = random.Random(7)
    lx, ly, lr = px(LUNA_C[0]), px(LUNA_C[1]), px(LUNA_R)
    for _ in range(int(300 * ESCALA)):
        sx, sy = r.randrange(W), r.randrange(max(1, int(horizonte_y * 0.8)))
        if math.hypot(sx - lx, sy - ly) < lr * 1.5:
            continue
        b = r.randint(110, 255)
        tam = max(1, px(1.5)) if r.random() < 0.85 else max(1, px(3))
        d2.rectangle((sx, sy, sx + tam, sy + tam), fill=(b, b, min(255, b + 20), 255))


def luna(img):
    lr = px(LUNA_R)
    im = luna_pixel().resize((lr * 2, lr * 2), Image.NEAREST)
    img.alpha_composite(im, (px(LUNA_C[0]) - lr, px(LUNA_C[1]) - lr))


def horizonte(img, y0, torre_x):
    """Dos filas de colinas de bloques (la de atras, en la niebla) y, en lo
    alto de una, la atalaya: el nombre del mod."""
    d = ImageDraw.Draw(img)
    r = random.Random(4)
    bloque = px(14)
    for col, alt, var in (((52, 18, 34), 105, 40), ((34, 14, 30), 70, 40), ((20, 10, 22), 40, 28)):
        x = 0
        h = alt
        while x < W:
            h = max(8, min(alt + var, h + r.choice([-14, 0, 0, 14])))
            d.rectangle((x, y0 - px(h), x + bloque, y0 + px(6)), fill=(*col, 255))
            x += bloque
    tx, base = torre_x, y0 - px(70)
    sil = (16, 9, 20, 255)
    d.rectangle((tx - px(56), base, tx + px(56), y0), fill=sil)
    d.rectangle((tx - px(15), base - px(124), tx + px(15), base), fill=sil)
    d.rectangle((tx - px(25), base - px(148), tx + px(25), base - px(124)), fill=sil)
    for k in range(-25, 26, 12):
        d.rectangle((tx + px(k) - px(4), base - px(160), tx + px(k) + px(4), base - px(148)), fill=sil)
    # su ventana encendida: la misma luz ambar que el ojo en calma
    ventana = (tx - px(4), base - px(141), tx + px(4), base - px(131))
    halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).rectangle(ventana, fill=(255, 170, 50, 200))
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(px(8))))
    d.rectangle(ventana, fill=(255, 190, 70, 255))


def niebla_horizonte(img, y0):
    """Una franja de niebla rojiza sobre el horizonte, y otra mas fina encima."""
    yy = np.arange(H)[:, None].astype(float)
    a = (np.exp(-((yy - (y0 - px(40))) / px(55)) ** 2) * 0.55 + np.exp(-((yy - (y0 - px(150))) / px(30)) ** 2) * 0.18)
    capa = np.zeros((H, W, 4), np.uint8)
    capa[..., :3] = (120, 40, 60)
    capa[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)[:, :1].repeat(W, axis=1)
    img.alpha_composite(Image.fromarray(capa))


def rayos_de_luz(luz, cx, cy, n=36, paso=0.016):
    """Rayos de luz desde (cx, cy): la luz se estira hacia fuera, y lo que la
    tapa (su silueta) deja sombras en los rayos."""
    im = Image.fromarray((np.clip(luz, 0, 1) * 255).astype(np.uint8))
    acc = np.zeros(luz.shape)
    peso = 0.0
    for k in range(n):
        s = 1 + k * paso
        w = (1 - k / n) ** 1.5
        t = im.transform(im.size, Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s), resample=Image.BILINEAR)
        acc += np.array(t).astype(float) / 255.0 * w
        peso += w
    return acc / peso


# ----------------------------------------------------------------------
#  El rayo, en 3D, con la geometria de RayoVigiaModel
# ----------------------------------------------------------------------
def rayo_quads(punta, direccion, largo, escala=1.3, giro_eje=20.0):
    """La malla del rayo con la punta en 'punta'. De ancho, la del juego (1,3
    veces la malla); de largo se estira para que la cola acabe a 'largo'
    bloques de la punta: en vuelo el rayo es un trazo, no un palo de 4 bloques."""
    z = np.array(direccion, float); z /= np.linalg.norm(z)
    x = np.cross([0, 1, 0], z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.eye(4); R[:3, 0] = x; R[:3, 1] = y; R[:3, 2] = z
    E = np.diag([escala / 16, escala / 16, largo / 48, 1.0])
    M = vr.T(*punta) @ R @ vr.Rz(giro_eje * vr.D2R) @ E
    cajas = [((0, 0), (-1, -1, -24, 2, 2, 28), 0), ((0, 30), (-2.5, -2.5, -20, 5, 5, 22), 0),
             ((0, 30), (-2.5, -2.5, -20, 5, 5, 22), 45), ((64, 0), (-2, -2, 0, 4, 4, 4), 0),
             ((60, 30), (-1.5, -1.5, -48, 3, 3, 30), 0)]
    out = []
    for tex, box, giro in cajas:
        Mg = M @ vr.Rz(giro * vr.D2R)
        for pts, uvs in vr.caja_quads(tex, box, False, 128, 64):
            out.append(([(Mg @ np.array([*q, 1.0]))[:3] for q in pts], uvs))
    return out


def calor(capa, camino, r):
    """Las rayas de calor de La Mirada: hebras que siguen el rayo y se abren
    hacia quien mira, mas vivas cuanto mas cerca."""
    lapiz = ImageDraw.Draw(capa)
    n = len(camino)
    for hebra in range(11):
        o = (hebra / 10 - 0.5) * 2
        fase = r.uniform(0, math.tau)
        for i in range(n - 1):
            (ta, ax, ay, az), (tb, bx, by, bz) = camino[i], camino[i + 1]
            t = i / (n - 1)
            tx, ty = bx - ax, by - ay
            lt = math.hypot(tx, ty) + 1e-6
            ancho = px(560) / az * (0.3 + 1.2 * t)
            ox, oy = -ty / lt * o * ancho, tx / lt * o * ancho
            al = int(190 * t ** 1.1 * (1 - abs(o) * 0.6) * max(0.0, math.sin(t * 19 + fase)) ** 0.5)
            if al <= 2:
                continue
            col = (255, 196, 110, al) if abs(o) < 0.5 else (255, 96, 44, al)
            lapiz.line([(ax + ox, ay + oy), (bx + ox, by + oy)], fill=col, width=max(1, int(px(7) / az)))


# ----------------------------------------------------------------------
#  La maldicion, hecha malla: espirales de humo maldito que suben a su
#  alrededor y se abren como un embudo. Bandas con la textura pintada aqui:
#  arriba la brasa (lo que brilla), debajo humo rojo oscuro que se deshace.
# ----------------------------------------------------------------------
def _tex_maldicion(semilla, w=64, h=12):
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        k = 1 - y / (h - 1)
        x = 0
        while x < w:
            largo = r.randint(3, 10)
            if y == 0:
                col, a = (255, 150, 90), r.randint(200, 245) if r.random() < 0.8 else 0
            elif y == 1:
                col, a = (240, 64, 40), r.randint(170, 220) if r.random() < 0.75 else 0
            elif r.random() < 0.35 + 0.45 * k:
                col, a = r.choice([(170, 30, 36), (130, 20, 42), (196, 52, 40)]), int(r.randint(120, 200) * (0.3 + 0.7 * k))
            else:
                col, a = (70, 12, 30), int(r.randint(60, 120) * (0.3 + 0.7 * k))
            for xx in range(x, min(w, x + largo)):
                t[y, xx] = (*col, a)
            x += largo + (0 if y <= 1 else r.randint(0, 5))
    return t


TEX_MALDICION = _tex_maldicion(5)
TEX_BRASA = TEX_MALDICION.copy()            # solo la brasa brilla
TEX_BRASA[2:, :, 3] = 0

CERCA = 2.8                                 # lo que este mas cerca de la camara no se pinta
CINTURA = 1.5                               # por encima, nada le pasa por delante
# (angulo de salida, vueltas, altura de salida y de llegada, radio abajo y
#  arriba, alto de la banda abajo y arriba)
ESPIRALES = [
    (0.4, 0.85, 0.1, 3.9, 1.25, 2.0, 0.45, 0.95),
    (2.6, 0.8, 0.4, 4.2, 1.35, 2.15, 0.4, 0.85),
    (4.5, 0.75, 0.0, 3.4, 1.15, 1.85, 0.4, 0.8),
]


def banda(filas, largo_tex=1.6):
    """filas: [(base, cresta, opacidad)] a lo largo de la banda -> quads (P, UV, k)."""
    qs, s = [], 0.0
    for (a0, a1, ka), (b0, b1, kb) in zip(filas, filas[1:]):
        ds = float(np.linalg.norm(b0 - a0))
        ua, ub = s / largo_tex, (s + ds) / largo_tex
        qs.append(([a0, b0, b1, a1], [(ua, 0.999), (ub, 0.999), (ub, 0.0), (ua, 0.0)], (ka + kb) / 2))
        s += ds
    return qs


def bandas_maldicion():
    cx, cz = VIGIA_EN[0], VIGIA_EN[2]
    qs, crestas = [], []
    for th0, vueltas, y0, y1, r0, r1, b0, b1 in ESPIRALES:
        filas = []
        for i in range(110):
            t = i / 109
            th = th0 + t * vueltas * math.tau
            rad = r0 + (r1 - r0) * t ** 1.3
            p = np.array([cx + math.cos(th) * rad, y0 + (y1 - y0) * t, cz + math.sin(th) * rad])
            # la brasa va arriba: la banda cuelga de ella como humo
            filas.append((p, p + np.array([0, b0 + (b1 - b0) * t, 0]), 0.9 * math.sin(math.pi * t) ** 0.7))
        qs += banda(filas)
        crestas += [f[1] for f in filas[4::9]]
    return qs, crestas


def dibujar_maldicion(lz, niebla):
    """Pinta el humo en su propio lienzo con la profundidad de la escena (asi
    queda detras de el cuando pasa por detras), de atras a delante."""
    humo = vr.Lienzo(lz.W, lz.H)
    humo.z = lz.z.copy()
    qs, crestas = bandas_maldicion()
    qs = [q for q in qs if min(CAM.proyectar(p)[2] for p in q[0]) > CERCA]
    qs.sort(key=lambda q: -CAM.proyectar(np.mean(q[0], axis=0))[2])
    for Pq, UVq, k in qs:
        # arriba se disuelve: la luna y el sello quedan limpios
        sx_ = np.mean([CAM.proyectar(p)[0] for p in Pq]) / SS / ESCALA
        alto_pantalla = min(CAM.proyectar(p)[1] for p in Pq) / SS / ESCALA
        k *= min(1.0, max(0.0, (alto_pantalla - 120) / 160))
        k *= min(1.0, max(0.0, (math.hypot(sx_ - LUNA_C[0], alto_pantalla - LUNA_C[1]) - LUNA_R * 1.5) / 60))
        if k < 0.02:
            continue
        for tri in ((0, 1, 2), (0, 2, 3)):
            humo.triangulo(CAM, [Pq[i] for i in tri], [UVq[i] for i in tri], TEX_MALDICION, np.ones(3), None, niebla,
                           envolver=True, translucido=k * 0.8)
            humo.triangulo(CAM, [Pq[i] for i in tri], [UVq[i] for i in tri], TEX_BRASA, np.ones(3), None, None,
                           aditivo=True, brillo=0.38 * k, envolver=True)
    return humo, crestas


def main():
    lz = vr.Lienzo(W * SS, H * SS)
    tex = vr.cargar(os.path.join(A, 'entity/vigia/vigia.png'))
    brillo = vr.cargar(os.path.join(A, 'entity/vigia/vigia_ojo_caza.png'))
    rayo_tex = vr.cargar(os.path.join(A, 'entity/vigia/rayo.png'))
    niebla = Niebla()

    # el suelo de losas, plano: a ras de suelo los escalones dejarian rendijas
    # por las que asoma el cielo rojo
    st = suelo_tex()
    quads = []
    for gx in range(-16, 18):
        for gz in range(-7, 44):
            P0 = [(gx, 0.0, gz), (gx + 1, 0.0, gz), (gx + 1, 0.0, gz + 1), (gx, 0.0, gz + 1)]
            quads.append((P0, [(0, 0), (1, 0), (1, 1), (0, 1)], 'suelo'))
    vr.dibujar_quads(lz, CAM, quads, st, luces=LUCES[:1], ambiente=(0.2, 0.18, 0.26), niebla=niebla)

    # el Vigia
    M = vr.entidad_a_mundo(*VIGIA_EN, GUINADA, 1.0)
    vigia = vr.quads_del_modelo(POSE, modelo_a_mundo=M)
    vr.dibujar_quads(lz, CAM, vigia, tex, emis=brillo, luces=LUCES, ambiente=AMBIENTE, brillo=1.4)
    # su silueta sola: recorta lo que pasa por detras y le pone el contraluz
    solo = vr.Lienzo(W * SS, H * SS)
    vr.dibujar_quads(solo, CAM, vigia, tex, luces=[], ambiente=(1, 1, 1))
    figura = mascara(solo.alfa)

    # el humo de la maldicion, despues de todo lo opaco
    humo, crestas = dibujar_maldicion(lz, niebla)

    # La Mirada: el rayo sale del ojo y viene hacia quien mira, pasandole por
    # la derecha y algo por debajo. La punta queda justo fuera de cuadro y la
    # cola acaba un palmo delante del ojo: el ojo se sigue leyendo.
    ojo = np.mean([np.mean(q[0], axis=0) for q in vigia if q[2] == 'ojo'], axis=0)
    blanco = CAM.ojo + CAM.r * 5.5 - CAM.u * 1.8
    dirr = blanco - ojo
    dirr /= np.linalg.norm(dirr)
    hueco = 0.45
    camino = []                                # el rayo en pantalla, del ojo al borde: (t, x, y, prof)
    for t in np.linspace(hueco, np.linalg.norm(blanco - ojo) - 0.3, 300):
        sx, sy, z = pantalla(ojo + dirr * t)
        if not (0 <= sx <= W and 0 <= sy <= H):
            break
        camino.append((t, sx, sy, z))
    t_punta = camino[-1][0] + 0.25
    punta = ojo + dirr * t_punta
    for Pq, UVq in rayo_quads(punta, dirr, t_punta - hueco):
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [Pq[i] for i in tri], [UVq[i] for i in tri], rayo_tex, None, aditivo=True, brillo=0.65)

    # --- a resolucion final ---
    color = a_imagen(lz.color)
    alfa = a_imagen(lz.alfa)
    emis = a_imagen(lz.emis)

    ex, ey, _ = pantalla(ojo)
    lejos = np.array([CAM.ojo[0] + CAM.f[0] * 400, 0.0, CAM.ojo[2] + CAM.f[2] * 400])
    horiz = CAM.proyectar(lejos)[1] / SS
    pie_x, pie_y, _ = pantalla(VIGIA_EN)
    _, cintura, _ = pantalla((VIGIA_EN[0], CINTURA, VIGIA_EN[2]))
    yy, xx = np.mgrid[0:H, 0:W]

    # el cielo; detras de el, el aire brilla: frio arriba, rojo abajo, y rojo
    # de caza alrededor del farol
    fondo = cielo(horiz, (pie_x, horiz - px(120)))
    halo = desenfocar(figura, px(45))
    arriba_abajo = np.clip((yy - px(200)) / px(700), 0, 1)[..., None]
    fondo += halo[..., None] * (np.array([0.22, 0.24, 0.42]) * (1 - arriba_abajo) + np.array([0.5, 0.08, 0.06]) * arriba_abajo) * 0.7
    dd = np.hypot((xx - ex) / (W * 0.12), (yy - ey) / (H * 0.2))
    fondo += np.array([0.5, 0.06, 0.04])[None, None] * np.exp(-dd ** 2 * 1.4)[..., None] * 0.45
    fondo_img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    estrellas(fondo_img, horiz)
    luna(fondo_img)
    horizonte(fondo_img, int(horiz), px(870))
    niebla_horizonte(fondo_img, int(horiz))

    escena = color.convert('RGBA')
    escena.putalpha(alfa)
    fondo_img.alpha_composite(escena)
    # la luz roja de las costillas y del ojo, encharcada en el suelo a sus pies
    charco = np.exp(-(((xx - pie_x) / px(330)) ** 2 + ((yy - (pie_y + px(10))) / px(34)) ** 2))
    charco *= (yy > horiz)
    fondo_img = sumar(fondo_img, Image.fromarray((charco[..., None] * np.array([150, 26, 18])).astype(np.uint8)), 0.9)

    # el humo maldito: ya viene recortado por detras de el; por delante solo
    # se deja pasar por sus piernas, no por el pecho ni la cara
    sobre = np.clip((cintura + px(30) - yy) / px(60), 0, 1)
    deja = 1 - figura * sobre
    a_humo = np.array(a_imagen(humo.alfa)).astype(float)[..., None] / 255 * deja[..., None]
    c_humo = np.array(a_imagen(humo.color)).astype(float) * deja[..., None]
    f = np.array(fondo_img).astype(float)
    f[..., :3] = f[..., :3] * (1 - a_humo) + c_humo
    fondo_img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    e_humo = np.array(a_imagen(humo.emis)).astype(float) * deja[..., None]
    emis = Image.fromarray(np.clip(np.array(emis).astype(float) + e_humo, 0, 255).astype(np.uint8))

    # --- particulas propias, a varias profundidades ---
    tras = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    frente = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lejos_capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))     # cerca de la camara: desenfocado
    r = random.Random(9)

    def libre(x, y):
        """Por delante no se tapa la cara ni el pecho."""
        xi, yi = min(W - 1, max(0, int(x))), min(H - 1, max(0, int(y)))
        return not (figura[yi, xi] > 0.1 and y < cintura)

    def lejos_del_rayo(x, y, margen):
        """Ni encima del ojo ni encima del rayo: son el foco."""
        if math.hypot(x - ex, y - ey) < px(170) + margen:
            return False
        for _, cx_, cy_, prof_ in camino[::6]:
            if math.hypot(x - cx_, y - cy_) < CAM.foco / SS * (2.5 * 1.3 / 16) / prof_ * 1.5 + margen:
                return False
        return True

    # los sellos de la maldicion, en las espirales: cerca y lejos
    lx, ly, lr = px(LUNA_C[0]), px(LUNA_C[1]), px(LUNA_R)
    elegidas = [p for i, p in enumerate(crestas) if i % 3 == 1]
    for p in elegidas:
        sx, sy, prof = pantalla(p)
        if prof < CERCA or sy < px(150) or sx < px(840) or math.hypot(sx - lx, sy - ly) < lr * 1.25:
            continue
        lado = int(px(330) / prof)
        if not lejos_del_rayo(sx, sy, lado / 2):
            continue
        s = sprite(f'vigia_maldicion_{r.randint(1, 2)}.png', lado, 0.95)
        if delante_del_eje(p):
            # los sellos de delante, nunca encima de el (ni de las piernas)
            sobre_el = figura[max(0, int(sy - lado / 2)):int(sy + lado / 2), max(0, int(sx - lado / 2)):int(sx + lado / 2)]
            if sobre_el.size and sobre_el.max() < 0.1:
                pegar(frente, s, sx, sy)
        else:
            pegar(tras, s, sx, sy)
    # marcas sueltas y brasas que se desprenden del humo
    for p in crestas:
        if r.random() > 0.6:
            continue
        sx, sy, prof = pantalla(p + np.array([r.uniform(-0.3, 0.3), r.uniform(0.0, 0.5), r.uniform(-0.3, 0.3)]))
        if prof < CERCA or sy < px(150) or sx < px(840) or math.hypot(sx - lx, sy - ly) < lr * 1.15:
            continue
        nombre = f'vigia_marca_{r.randint(0, 2)}.png' if r.random() < 0.4 else f'vigia_chispa_{r.randint(0, 2)}.png'
        s = sprite(nombre, int(px(110) / prof * r.uniform(0.7, 1.2)))
        if delante_del_eje(p):
            if libre(sx, sy):
                pegar(frente, s, sx, sy)
        else:
            pegar(tras, s, sx, sy)
    # brasas y ceniza en el aire, alrededor de el
    for _ in range(45):
        p = np.array([r.uniform(-3.5, 4.5), r.uniform(0.0, 5.5), r.uniform(-2.5, 5.0)])
        sx, sy, prof = pantalla(p)
        if prof < CERCA or not (px(820) < sx < W and px(130) < sy < H) or math.hypot(sx - lx, sy - ly) < lr * 1.1:
            continue
        nombre = f'vigia_chispa_{r.randint(1, 2)}.png' if r.random() < 0.6 else f'vigia_esquirla_{r.randint(0, 3)}.png'
        s = sprite(nombre, max(3, int(px(90) / prof * r.uniform(0.6, 1.1))), r.uniform(0.6, 1.0))
        if delante_del_eje(p):
            if libre(sx, sy):
                pegar(frente, s, sx, sy)
        else:
            pegar(tras, s, sx, sy)
    # unas pocas brasas muy cerca de la camara, grandes y fuera de foco
    for (bx, by, lado) in ((1830, 860, 64), (960, 1000, 52), (1700, 160, 40), (980, 760, 34)):
        s = sprite(f'vigia_chispa_{r.randint(0, 2)}.png', px(lado), 0.75)
        pegar(lejos_capa, s, px(bx), px(by))
    # chispas que convergen al ojo: La Mirada cargando
    for _ in range(9):
        a = r.uniform(0, math.tau); d = r.uniform(px(50), px(150))
        s = sprite(f'vigia_chispa_{r.randint(0, 2)}.png', px(r.choice([16, 20, 26])))
        x, y = ex + math.cos(a) * d, ey + math.sin(a) * d
        if libre(x, y) or figura[min(H - 1, max(0, int(y))), min(W - 1, max(0, int(x)))] < 0.1:
            pegar(frente, s, x, y)
    # chispas que salta el rayo a su paso, mas grandes cuanto mas cerca
    for _ in range(14):
        t, sx, sy, prof = camino[r.randint(len(camino) // 4, len(camino) - 1)]
        lado = max(4, int(px(120) / prof * r.uniform(0.5, 1.0)))
        s = sprite(f'vigia_chispa_{r.randint(0, 2)}.png', lado)
        o = r.choice([-1, 1]) * r.uniform(0.6, 1.4) * px(420) / prof      # saltan fuera del rayo
        pegar(frente, s, sx + r.uniform(-0.3, 0.3) * o, sy + o)

    hueco_fig = 1 - figura
    tras.putalpha(Image.fromarray((np.array(tras.getchannel('A')).astype(float) * hueco_fig).astype(np.uint8)))
    fondo_img.alpha_composite(tras.filter(ImageFilter.GaussianBlur(px(6))))
    fondo_img.alpha_composite(tras)

    # rayos de luz de la luna: su silueta los corta
    # (el borde de la luna, roto en rayos con un ruido por angulo)
    dl = np.hypot(xx - lx, yy - ly) / lr
    ang = (np.arctan2(yy - ly, xx - lx) / math.tau + 0.5) * 90
    rr = np.random.default_rng(4).uniform(0.15, 1.0, 92)
    ruido = rr[np.floor(ang).astype(int)] * (1 - ang % 1) + rr[np.floor(ang).astype(int) + 1] * (ang % 1)
    luz = ((dl < 1.0) * 0.7 + np.exp(-np.maximum(dl - 1, 0) * 3.0) * 0.5 * (dl >= 1.0)) * ruido
    luz *= (1 - figura)
    rayos = rayos_de_luz(luz, lx, ly, n=40, paso=0.02) * (dl > 1.02)
    fondo_img = sumar(fondo_img, Image.fromarray((np.clip(rayos[..., None] * np.array([0.6, 0.6, 0.9]), 0, 1) * 255)
                                                 .astype(np.uint8)), 0.55)

    # bloom: tres radios; el amplio tine el aire alrededor del ojo y del rayo
    e = emis.convert('RGB')
    for radio, k in ((px(5), 0.85), (px(18), 0.65), (px(60), 0.5)):
        fondo_img = sumar(fondo_img, e.filter(ImageFilter.GaussianBlur(radio)), k)
    img = sumar(fondo_img, e, 0.55).convert('RGBA')

    # contraluces: el borde de la silueta que mira a la luna, en blanco frio,
    # y el que mira al resplandor del horizonte, en rojo
    f = np.array(img).astype(float)
    for (dx, dy), rgb, k in (((-1, -1), (190, 205, 255), 0.7), ((1, 0), (255, 70, 40), 0.6)):
        n_ = max(1, px(3))
        vecino = np.roll(figura, (-dy * n_, -dx * n_), axis=(0, 1))
        borde = desenfocar(np.clip(figura - vecino, 0, 1), max(1, px(1.5)))
        f[..., :3] += borde[..., None] * np.array(rgb) * k
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).convert('RGBA')

    # el destello del ojo: un trazo horizontal y una cruz, en rojo de caza
    destello = Image.new('RGB', (W, H), (0, 0, 0))
    dd_ = ImageDraw.Draw(destello)
    dd_.ellipse((ex - px(140), ey - px(4), ex + px(140), ey + px(4)), fill=(255, 90, 50))
    dd_.ellipse((ex - px(4), ey - px(60), ex + px(4), ey + px(60)), fill=(200, 60, 40))
    img = sumar(img, destello.filter(ImageFilter.GaussianBlur(px(4))), 0.8)
    img = sumar(img, destello.filter(ImageFilter.GaussianBlur(px(14))), 0.6).convert('RGBA')

    # las rayas de calor del rayo y lo que pasa por delante de el
    capa_calor = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    calor(capa_calor, camino, r)
    img.alpha_composite(capa_calor.filter(ImageFilter.GaussianBlur(px(3))))
    img.alpha_composite(capa_calor)
    img.alpha_composite(frente.filter(ImageFilter.GaussianBlur(px(6))))
    img.alpha_composite(frente)

    # niebla baja de humo a los pies, por delante de las piernas
    humo2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for _ in range(28):
        s = sprite(f'vigia_humo_{r.randint(2, 4)}.png', px(r.choice([100, 130, 170])), 0.42)
        pegar(humo2, s, pie_x + r.uniform(-px(520), px(460)), pie_y - r.uniform(px(0), px(60)))
    img.alpha_composite(humo2.filter(ImageFilter.GaussianBlur(px(6))))
    img.alpha_composite(lejos_capa.filter(ImageFilter.GaussianBlur(px(7))))

    # --- grado de color y vineta ---
    f = np.array(img).astype(float) / 255.0
    vin = 1 - 0.58 * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.34, 0, 1) ** 1.4
    f[..., :3] *= vin[..., None]
    grano = np.random.default_rng(2).normal(0, 0.011, (H, W, 1))
    f[..., :3] = np.clip(f[..., :3] + grano, 0, 1)
    img = Image.fromarray((f * 255).astype(np.uint8)).convert('RGBA')

    # --- el anuncio ---
    gr = np.zeros((H, W, 4), np.uint8)
    gr[..., :3] = (8, 5, 12)
    gr[..., 3] = (np.clip(1 - xx / (W * 0.5), 0, 1) ** 1.6 * 215).astype(np.uint8)
    img.alpha_composite(Image.fromarray(gr))
    d = ImageDraw.Draw(img)

    x0 = px(110)
    texto_espaciado(d, (x0, px(300)), 'ATALAYA  ·  NUEVA AMENAZA', fuente('Montserrat-Bold.ttf', 22), AMBAR, px(5))
    brillo_texto(img, (x0 - px(6), px(320)), 'EL VIGÍA', fuente('Oswald-Bold.ttf', 196), BLANCO, (255, 40, 20, 200), px(24))
    d = ImageDraw.Draw(img)
    d.text((x0, px(562)), 'El Centinela de la Noche', font=fuente('Montserrat-SemiBoldItalic.ttf', 34), fill=(232, 222, 222, 255))
    d.text((x0, px(608)), 'Lo que mira, lo maldice.', font=fuente('Montserrat-Medium.ttf', 24), fill=GRIS)
    d.rectangle((x0, px(656), x0 + px(90), px(661)), fill=ROJO)

    # sello hardcore y version
    fs = fuente('Oswald-Bold.ttf', 26)
    fp = fuente('Montserrat-Medium.ttf', 18)
    tw = d.textlength('HARDCORE', font=fs)
    bx, by = W - px(110) - tw - px(36), px(60)
    d.rectangle((bx, by, bx + tw + px(36), by + px(52)), outline=ROJO, width=max(1, px(3)))
    d.text((bx + px(18), by + px(6)), 'HARDCORE', font=fs, fill=ROJO)
    d.text((W - px(110) - d.textlength('Minecraft 26.2 · Fabric', font=fp), H - px(70)),
           'Minecraft 26.2 · Fabric', font=fp, fill=(170, 160, 175, 255))

    img.convert('RGB').save(SALIDA)
    print('ok', W, H)


main()

"""
Todo lo pequeno de Aeralis, la Mariposa del Vendaval, que no es su cuerpo,
pintado aqui pixel a pixel (nada de vanilla):

  textures/entity/aeralis/   cuchilla de viento, banda del tornado, rafaga,
                             nucleo de viento (+ su brillo), mascara de disolverse
  textures/particle/         las particulas aeralis_*
  particles/                 sus definiciones
  textures/item/             escama_aeralis (la Escama del Vendaval)
  textures/mob_effect/       marca_vendaval, bendicion_vientos
  textures/gui/              miedo_aeralis (la vineta de tormenta)

Uso: python aeralis_extras.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image, ImageFilter
import math, os, sys, json, random

RAIZ = sys.argv[1]
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
ENT = os.path.join(A, 'textures/entity/aeralis')
PAR = os.path.join(A, 'textures/particle')
DEF = os.path.join(A, 'particles')
ITEM = os.path.join(A, 'textures/item')
EFE = os.path.join(A, 'textures/mob_effect')
GUI = os.path.join(A, 'textures/gui')
for d in (ENT, PAR, DEF, ITEM, EFE, GUI):
    os.makedirs(d, exist_ok=True)
rnd = random.Random(2027)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def lienzo(w, h=None):
    return Image.new('RGBA', (w, h or w), (0, 0, 0, 0))


def mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


CIELO = [hexc(c) for c in ('2a4a78', '4f8fc0', '8fd6ff', 'cfeeff', 'f4fbff')]
TORMENTA = [hexc(c) for c in ('2a1a50', '5a3a9a', '9070e0', 'c0a8ff', 'eee6ff')]
PIZARRA = [hexc(c) for c in ('141a26', '1f2738', '2b3550', '3c4a6c', '56688f')]
ORO = [hexc(c) for c in ('7a4a08', 'c07a10', 'ffc23a', 'ffe08a', 'fffbe0')]
GRIS = [hexc(c) for c in ('4a505c', '6d7482', '9aa2b0', 'c8ced8', 'eef1f5')]


def guardar(nombre, frames):
    nombres = []
    for i, im in enumerate(frames):
        n = f'{nombre}_{i}' if len(frames) > 1 else nombre
        im.save(os.path.join(PAR, n + '.png'))
        nombres.append(f'atalaya:{n}')
    with open(os.path.join(DEF, nombre + '.json'), 'w', encoding='utf-8') as f:
        json.dump({'textures': nombres}, f, indent=2)
    return frames


def espiral(n, brazos=2, k=2.6, c1=CIELO[4], c2=CIELO[2], fondo=None, grosor=1.0, giro=0.0):
    im = lienzo(n)
    p = im.load()
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2, y + 0.5 - n / 2
            d = math.hypot(dx, dy) / (n / 2)
            if d > 1:
                continue
            ang = math.atan2(dy, dx) + giro
            t = ((ang - k * math.log(max(d, 0.05))) * brazos / (2 * math.pi)) % 1.0
            if t < 0.32 * grosor:
                p[x, y] = mezclar(c1, c2, min(1.0, d)) if d < 0.95 else c2
            elif fondo:
                p[x, y] = fondo
    return im


# ======================================================================
#  ENTIDADES
# ======================================================================
# Cuchilla de viento (64x16): media luna; el centro blanco y los bordes cian
cu = lienzo(64, 16)
p = cu.load()
for y in range(16):
    for x in range(64):
        u, v = x / 63, abs(y - 7.5) / 7.5
        fin = math.sin(math.pi * u) ** 0.6
        a = (1 - v) ** 1.5 * fin
        if a > 0.04:
            c = mezclar(CIELO[4], CIELO[2], min(1.0, v * 1.6))
            if (x + y * 3) % 9 == 0:
                c = CIELO[4]
            p[x, y] = (c[0], c[1], c[2], int(255 * min(1.0, a * 1.4)))
cu.save(os.path.join(ENT, 'cuchilla.png'))

# Banda del tornado (32x64, en mosaico vertical): vetas que suben en diagonal
to = lienzo(32, 64)
p = to.load()
for y in range(64):
    for x in range(32):
        f = (x * 2 + y) % 16
        if f < 3:
            p[x, y] = mezclar(GRIS[4], CIELO[3], rnd.random() * 0.4)[:3] + (rnd.randint(170, 230),)
        elif f < 6:
            p[x, y] = GRIS[3][:3] + (rnd.randint(70, 120),)
        elif rnd.random() < 0.08:
            p[x, y] = GRIS[4][:3] + (rnd.randint(90, 160),)
to.save(os.path.join(ENT, 'tornado.png'))

# Rafaga (32x32): bola de viento en espiral, con su brillo
ra = espiral(32, 3, 2.8, CIELO[4], CIELO[2])
ra.save(os.path.join(ENT, 'rafaga.png'))

# Nucleo de viento (32x32): cristal de cielo para el modelo (cara de 8x8 en mosaico)
nu = lienzo(32, 32)
nu_br = lienzo(32, 32)
p, pb = nu.load(), nu_br.load()
for y in range(32):
    for x in range(32):
        i, j = x % 8, y % 8
        borde = min(i, j, 7 - i, 7 - j)
        if borde == 0:
            p[x, y] = CIELO[1]
        elif (i + j) % 5 == 0:
            p[x, y] = CIELO[4]
            pb[x, y] = CIELO[4]
        else:
            p[x, y] = CIELO[2 + (i * j) % 2]
            pb[x, y] = CIELO[2][:3] + (150,)
nu.save(os.path.join(ENT, 'nucleo.png'))
nu_br.save(os.path.join(ENT, 'nucleo_brillo.png'))

# Mascara de disolverse (512x256, las UV de su atlas): ruido suave
W, H = 512, 256
base = [[rnd.random() for _ in range(W // 8 + 2)] for _ in range(H // 8 + 2)]
ma = lienzo(W, H)
p = ma.load()
for y in range(H):
    for x in range(W):
        gx, gy = x / 8, y / 8
        x0, y0 = int(gx), int(gy)
        tx, ty = gx - x0, gy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        v = (base[y0][x0] * (1 - tx) + base[y0][x0 + 1] * tx) * (1 - ty) + \
            (base[y0 + 1][x0] * (1 - tx) + base[y0 + 1][x0 + 1] * tx) * ty
        v = 0.75 * v + 0.25 * rnd.random()
        p[x, y] = (255, 255, 255, int(8 + 240 * v))
ma.save(os.path.join(ENT, 'aeralis_disolver.png'))


# ======================================================================
#  PARTICULAS
# ======================================================================
def estela(n, largo, alfa):
    im = lienzo(n)
    p = im.load()
    y = n // 2
    for x in range(n):
        k = x / (n - 1)
        if abs(k - 0.5) * 2 <= largo:
            a = int(alfa * (1 - abs(k - 0.5) * 2 / largo) ** 0.7)
            p[x, y] = CIELO[4][:3] + (a,)
            if 0.35 < k < 0.65:
                p[x, y - 1] = CIELO[3][:3] + (a // 2,)
    return im


guardar('aeralis_viento', [estela(16, l, a) for l, a in ((1.0, 230), (0.8, 170), (0.5, 100))])


def escama(f):
    im = lienzo(8)
    p = im.load()
    c = [CIELO[4], CIELO[3], TORMENTA[3]][f]
    for (x, y) in ((3, 2), (4, 2), (2, 3), (3, 3), (4, 3), (5, 3), (3, 4), (4, 4), (3, 5)):
        p[x, y] = c
    if f == 0:
        p[3, 3] = (255, 255, 255, 255)
    return im


guardar('aeralis_escama', [escama(f) for f in range(3)])
guardar('aeralis_remolino', [espiral(16, 2, 2.4, CIELO[4], GRIS[3], giro=f * 2.1) for f in range(3)])


def rayo(f):
    im = lienzo(16)
    p = im.load()
    r = random.Random(30 + f)
    x, y = 8, 0
    while y < 16:
        for dx in (0, 1):
            if 0 <= x + dx < 16:
                p[x + dx, y] = (255, 250, 220, 255) if dx == 0 else TORMENTA[3]
        y += 1
        x += r.choice((-1, 0, 1))
        x = max(1, min(14, x))
    return im


guardar('aeralis_rayo', [rayo(f) for f in range(3)])


def marca(f):
    im = espiral(16, 1, 3.0, (220, 245, 255, 255), (90, 170, 255, 255), giro=f * 1.5)
    p = im.load()
    for i in range(16):                          # el aro de la diana
        a = i / 16 * 2 * math.pi
        x, y = int(8 + 7.2 * math.cos(a)), int(8 + 7.2 * math.sin(a))
        p[x, y] = (120, 190, 255, 255)
    return im


guardar('aeralis_marca', [marca(f) for f in range(2)])


def luz(f, rampa):
    im = lienzo(8)
    p = im.load()
    r = [2.0, 3.0, 3.6][f]
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - 3.5, y - 3.5) / r
            if d <= 1:
                p[x, y] = mezclar(rampa[4], rampa[2], d)[:3] + (int(255 * (1 - d) ** 0.6),)
    return im


guardar('aeralis_luz', [luz(f, CIELO) for f in range(3)])
guardar('aeralis_oro', [luz(f, ORO) for f in range(3)])


def onda(f):
    n = 64
    im = lienzo(n)
    p = im.load()
    for y in range(n):
        for x in range(n):
            d = math.hypot(x + 0.5 - n / 2, y + 0.5 - n / 2) / (n / 2)
            g = abs(d - 0.86) / 0.12
            if g < 1:
                a = int(220 * (1 - g) ** 1.5 * [1.0, 0.75, 0.45][f])
                p[x, y] = mezclar(CIELO[4], CIELO[2], g)[:3] + (a,)
    return im


guardar('aeralis_onda', [onda(f) for f in range(3)])


def circulo_juicio(f):
    """El circulo que se abre bajo todos en el Juicio del Ciclon."""
    n = 128
    im = lienzo(n)
    p = im.load()
    c, b = TORMENTA[4], TORMENTA[2]
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2, y + 0.5 - n / 2
            d = math.hypot(dx, dy) / (n / 2)
            ang = math.atan2(dy, dx) + f * 0.4
            if 0.94 < d < 0.99 or 0.77 < d < 0.8:
                p[x, y] = c[:3] + (230,)
            elif 0.8 < d < 0.94 and int((ang + math.pi) / (2 * math.pi) * 36) % 3 == 0:
                p[x, y] = b[:3] + (190,)
            elif d < 0.77 and (ang - 3.0 * math.log(max(d, 0.02))) % (math.pi / 2) < 0.2:
                p[x, y] = b[:3] + (int(150 * (1 - d) + 50),)
    return im


guardar('aeralis_circulo', [circulo_juicio(f) for f in range(2)])


def polvo(f):
    im = lienzo(8)
    p = im.load()
    r = [1.6, 2.6, 3.4][f]
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - 3.5, y - 3.5) / r
            if d <= 1 and rnd.random() > 0.15:
                p[x, y] = GRIS[2 + (x + y) % 2][:3] + (int(200 * (1 - d * 0.6)),)
    return im


guardar('aeralis_polvo', [polvo(f) for f in range(3)])


def jiron(f):
    """Un jiron de ala que se desprende: triangulo traslucido con su vena."""
    im = lienzo(8)
    p = im.load()
    r = random.Random(60 + f)
    for y in range(8):
        for x in range(8):
            if x + y < 7 + r.randint(-1, 1) and x > 0 and y > 0:
                p[x, y] = CIELO[3][:3] + (150,)
    for k in range(1, 6):
        p[k, k] = PIZARRA[3]
    return im


guardar('aeralis_jiron', [jiron(f) for f in range(3)])

# ======================================================================
#  OBJETO: la Escama del Vendaval (16x16)
# ======================================================================
es = lienzo(16)
p = es.load()
for y in range(16):
    for x in range(16):
        # escama en rombo alargado, con canto oscuro
        d = abs(x - 7.5) / 6.0 + abs(y - 8.0) / 7.5
        if d <= 1.0:
            if d > 0.86:
                p[x, y] = PIZARRA[2]
            else:
                t = (x - 2) / 12 + (y - 2) / 24
                p[x, y] = mezclar(CIELO[4], TORMENTA[2], max(0.0, min(1.0, t)))
sp = espiral(8, 2, 2.4, (255, 255, 255, 255), CIELO[2])
es.alpha_composite(sp, (4, 4))
for (x, y) in ((5, 3), (6, 3), (5, 4)):
    p[x, y] = (255, 255, 255, 255)
es.save(os.path.join(ITEM, 'escama_aeralis.png'))

# ======================================================================
#  EFECTOS (18x18)
# ======================================================================
mv = lienzo(18)
mv.alpha_composite(marca(0).resize((18, 18), Image.NEAREST))
mv.save(os.path.join(EFE, 'marca_vendaval.png'))

bv = lienzo(18)
p = bv.load()
for y in range(18):                              # una pluma de viento dorada
    for x in range(18):
        u = (x + y) / 2 - 3
        v = (x - y)
        if 0 <= u <= 11 and abs(v) <= 3.2 * math.sin(math.pi * u / 11):
            p[x, y] = ORO[3] if abs(v) < 0.8 else ORO[2] if abs(v) < 2 else ORO[1]
for k in range(4):
    a = k * 0.9
    p[int(4 + 3 * math.cos(a)), int(13 - 3 * math.sin(a))] = CIELO[4]
bv.save(os.path.join(EFE, 'bendicion_vientos.png'))

# ======================================================================
#  GUI: la vineta de tormenta (256x256)
# ======================================================================
mi = lienzo(256)
p = mi.load()
nubes = Image.new('L', (256, 256), 0)
from PIL import ImageDraw
d = ImageDraw.Draw(nubes)
for _ in range(90):
    a = rnd.uniform(0, 2 * math.pi)
    rr = rnd.uniform(0.82, 1.15) * 128
    cx, cy = 128 + math.cos(a) * rr, 128 + math.sin(a) * rr
    s = rnd.uniform(18, 46)
    d.ellipse((cx - s, cy - s * 0.6, cx + s, cy + s * 0.6), fill=rnd.randint(120, 255))
nubes = nubes.filter(ImageFilter.GaussianBlur(10))
for y in range(256):
    for x in range(256):
        rr = math.hypot(x - 127.5, y - 127.5) / 128
        a = max(0.0, min(1.0, (rr - 0.55) / 0.5)) ** 1.6
        a = max(a, nubes.getpixel((x, y)) / 255 * max(0.0, rr - 0.45) * 1.6)
        # estelas de viento que se cuelan hacia dentro
        ang = math.atan2(y - 127.5, x - 127.5)
        if (ang * 12 + rr * 9) % 2.2 < 0.12 and rr > 0.6:
            a = min(1.0, a + 0.25)
        p[x, y] = (12, 16, 30, int(255 * min(1.0, a)))
mi.save(os.path.join(GUI, 'miedo_aeralis.png'))

if len(sys.argv) > 2:
    nombres = sorted(f for f in os.listdir(PAR) if f.startswith('aeralis_'))
    prev = Image.new('RGBA', (len(nombres) * 40 + 20, 140), (40, 46, 60, 255))
    for i, f in enumerate(nombres):
        im = Image.open(os.path.join(PAR, f)).convert('RGBA')
        k = max(1, 32 // max(im.size))
        prev.alpha_composite(im.resize((im.width * k, im.height * k), Image.NEAREST), (10 + i * 40, 10))
    x = 10
    for f in (os.path.join(ITEM, 'escama_aeralis.png'), os.path.join(EFE, 'marca_vendaval.png'), os.path.join(EFE, 'bendicion_vientos.png'),
              os.path.join(ENT, 'cuchilla.png'), os.path.join(ENT, 'rafaga.png'), os.path.join(ENT, 'tornado.png')):
        im = Image.open(f).convert('RGBA')
        k = max(1, 48 // max(im.size))
        prev.alpha_composite(im.resize((im.width * k, im.height * k), Image.NEAREST), (x, 60))
        x += im.width * k + 12
    prev.save(sys.argv[2])
    print(len(nombres), 'texturas de particula')

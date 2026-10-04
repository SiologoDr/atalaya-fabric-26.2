"""
Todo lo pequeno de Nerea que no es su cuerpo, pintado aqui pixel a pixel:

  textures/entity/nerea/   burbuja (+ nucleo que brilla), gancho (y el oxido de
                           las cadenas), rayo de la mirada, mascara de disolverse
  textures/particle/       las diez particulas nerea_*
  particles/               sus definiciones
  textures/item/           lagrima_nerea
  textures/mob_effect/     bendicion_mareas

Las cuadriculas UV de la burbuja y el gancho son las de sus modelos Java
(BurbujaNereaRenderer.Modelo, GanchoNereaRenderer.Modelo).

Uso: python nerea_extras.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image
import math, os, sys, json, random

RAIZ = sys.argv[1]
ENT = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/nerea')
PAR = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/particle')
DEF = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/particles')
ITEM = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
EFE = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/mob_effect')
for d in (ENT, PAR, DEF, ITEM, EFE):
    os.makedirs(d, exist_ok=True)
rnd = random.Random(2026)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def lienzo(w, h=None):
    return Image.new('RGBA', (w, h or w), (0, 0, 0, 0))


def mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


PRISMA_OSC = [hexc(c) for c in ('0f2a2c', '173b3c', '22504d', '2f6660', '3f7f76')]
OXIDO = [hexc(c) for c in ('2a1a12', '4a2a18', '6e3c1e', '9a5726', 'c47a3a')]
HUESO = [hexc(c) for c in ('5c5545', '8a8068', 'b3a98c', 'd3c9aa', 'ece4c8')]
LATON = [hexc(c) for c in ('4a3410', '7a5a1c', 'b08a2e', 'dcb84a', 'fff0a0')]
CIAN = [hexc(c) for c in ('0b4f63', '1b8aa6', '3fe0ff', '9ff4ff', 'eaffff')]
MAGENTA = [hexc(c) for c in ('5a0a2c', 'a0144c', 'e0144c', 'ff6aa0', 'ffd0e0')]
ORO = [hexc(c) for c in ('7a4a08', 'c07a10', 'ffc23a', 'ffe08a', 'fffbe0')]
ESPUMA = [hexc(c) for c in ('7fb8c8', 'a8dbe4', 'cdeef2', 'eefcff', 'ffffff')]


def rellenar(im, x, y, w, h, fn):
    p = im.load()
    for j in range(h):
        for i in range(w):
            c = fn(i, j, w, h)
            if c is not None:
                p[x + i, y + j] = c


def grano(rampa, lo=1, hi=3):
    return lambda i, j, w, h: rampa[rnd.randint(lo, hi)]


# ======================================================================
#  BURBUJA BOMBA: pompa de agua con un nucleo de maldicion dentro
#  UV (64x32): burbuja texOffs(0,0) 12x12x12 ; nucleo (0,24) 4x4x4
# ======================================================================
bu = lienzo(64, 32)
bu_br = lienzo(64, 32)
p = bu.load()
for (x0, y0, w, h) in ((12, 0, 12, 12), (24, 0, 12, 12), (0, 12, 12, 12), (12, 12, 12, 12), (24, 12, 12, 12), (36, 12, 12, 12)):
    for j in range(h):
        for i in range(w):
            borde = min(i, j, w - 1 - i, h - 1 - j)
            if borde == 0:
                c = hexc('cdf6ff', 200)
            elif borde == 1:
                c = hexc('8fe0f0', 120)
            else:
                c = hexc('3fb4d0', 55 + rnd.randint(0, 20))
            # el reflejo de arriba a la izquierda
            if 2 <= i <= 4 and 2 <= j <= 3 or (i == 2 and j == 4):
                c = hexc('ffffff', 230)
            p[x0 + i, y0 + j] = c
rellenar(bu, 0, 24, 16, 8, lambda i, j, w, h: MAGENTA[2 + (i + j) % 2])
rellenar(bu_br, 0, 24, 16, 8, lambda i, j, w, h: MAGENTA[3 + (i * 3 + j) % 2])
bu.save(os.path.join(ENT, 'burbuja.png'))
bu_br.save(os.path.join(ENT, 'burbuja_brillo.png'))

# ======================================================================
#  GANCHO (32x32): oxido arriba (texOffs 0,0), hueso abajo (texOffs 0,8)
# ======================================================================
ga = lienzo(32, 32)
rellenar(ga, 0, 0, 32, 8, lambda i, j, w, h: OXIDO[0] if j in (0, 7) else OXIDO[rnd.randint(1, 4)])
rellenar(ga, 0, 8, 32, 14, lambda i, j, w, h: HUESO[1] if (i + 2 * j) % 11 == 0 else HUESO[rnd.randint(2, 4)])
ga.save(os.path.join(ENT, 'gancho.png'))

# ======================================================================
#  RAYO de la mirada (16x16): nucleo blanco, borde cian, vetas a lo largo
# ======================================================================
ra = lienzo(16, 16)
p = ra.load()
for y in range(16):
    for x in range(16):
        d = abs(x - 7.5) / 7.5
        a = max(0.0, 1 - d ** 1.6)
        veta = 0.75 + 0.25 * math.sin(y * 0.8 + x * 0.3) + (0.15 if rnd.random() < 0.15 else 0)
        c = mezclar(CIAN[4], CIAN[2], min(1.0, d * 1.4))
        p[x, y] = (c[0], c[1], c[2], int(255 * a * min(1.0, veta)))
ra.save(os.path.join(ENT, 'rayo.png'))

# ======================================================================
#  MASCARA DE DISOLVERSE (256x256, mismas UV que el atlas): ruido suave.
#  Donde la mascara es alta, la pieza desaparece antes.
# ======================================================================
N = 256
base = [[rnd.random() for _ in range(N // 8 + 2)] for _ in range(N // 8 + 2)]
ma = lienzo(N, N)
p = ma.load()
for y in range(N):
    for x in range(N):
        gx, gy = x / 8, y / 8
        x0, y0 = int(gx), int(gy)
        tx, ty = gx - x0, gy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        v = (base[y0][x0] * (1 - tx) + base[y0][x0 + 1] * tx) * (1 - ty) + \
            (base[y0 + 1][x0] * (1 - tx) + base[y0 + 1][x0 + 1] * tx) * ty
        v = 0.75 * v + 0.25 * rnd.random()
        p[x, y] = (255, 255, 255, int(8 + 240 * v))
ma.save(os.path.join(ENT, 'nerea_disolver.png'))


# ======================================================================
#  PARTICULAS
# ======================================================================
def guardar(nombre, frames):
    nombres = []
    for i, im in enumerate(frames):
        n = f'{nombre}_{i}' if len(frames) > 1 else nombre
        im.save(os.path.join(PAR, n + '.png'))
        nombres.append(f'atalaya:{n}')
    with open(os.path.join(DEF, nombre + '.json'), 'w', encoding='utf-8') as f:
        json.dump({'textures': nombres}, f, indent=2)


def circulo(n, cx, cy, r, fn):
    im = lienzo(n)
    p = im.load()
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - cx, y - cy) / r
            if d <= 1:
                c = fn(d, x, y)
                if c:
                    p[x, y] = c
    return im


# burbuja: aro con reflejo, y el ultimo fotograma es el estallido
def pompa(r):
    return circulo(8, 3.5, 3.5, r, lambda d, x, y: hexc('eaffff', 240) if d > 0.7 else
                   (hexc('ffffff', 255) if (x, y) in ((2, 2), (3, 2), (2, 3)) else hexc('7fd8ec', 70)))
estallido = lienzo(8)
for (x, y) in ((1, 1), (6, 1), (1, 6), (6, 6), (3, 0), (0, 4), (7, 3), (4, 7)):
    estallido.load()[x, y] = hexc('eaffff', 220)
guardar('nerea_burbuja', [pompa(3.6), pompa(2.8), estallido])


# espuma: nube blanca que crece y se deshace
def espuma(f):
    r = random.Random(f + 7)
    im = lienzo(8)
    p = im.load()
    rad = 1.8 + f * 0.6
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - 3.5 + r.uniform(-0.6, 0.6), y - 3.5 + r.uniform(-0.6, 0.6)) / rad
            if d <= 1 and (f < 3 or r.random() > 0.35):
                p[x, y] = ESPUMA[min(4, int((1 - d) * 4) + (1 if f < 2 else 0))][:3] + (230 - f * 40,)
    return im
guardar('nerea_espuma', [espuma(f) for f in range(4)])


# gota: lagrima de agua
def gota(alarg):
    im = lienzo(8)
    p = im.load()
    for y in range(8):
        for x in range(8):
            t = y / 7
            semi = 2.6 * math.sin(math.pi * min(1.0, t ** alarg * 1.05))
            if abs(x - 3.5) <= semi:
                p[x, y] = CIAN[4] if (x < 3.5 and 3 < y < 6) else CIAN[2] if abs(x - 3.5) < semi - 0.8 else CIAN[1]
    return im
guardar('nerea_gota', [gota(1.6), gota(1.0)])


# ola: la cresta que rompe, 4 fotogramas de 16x16
def ola(f):
    im = lienzo(16)
    p = im.load()
    alto = [6, 10, 12, 8][f]
    for x in range(16):
        h = alto * (0.55 + 0.45 * math.sin((x / 15) * math.pi * 0.9 + f * 0.4))
        for y in range(16):
            yy = 15 - y
            if yy < h:
                prof = yy / max(1, h)
                c = ESPUMA[4] if prof > 0.82 else ESPUMA[2] if prof > 0.6 else CIAN[2] if prof > 0.3 else CIAN[1]
                p[x, y] = c[:3] + (235 if f < 3 else 160,)
    # la cresta se curva hacia delante en los dos del medio
    if f in (1, 2):
        for k in range(5):
            x, y = 10 + k, 15 - alto + k // 2
            if 0 <= y < 16:
                p[min(15, x), y] = ESPUMA[4]
    return im
guardar('nerea_ola', [ola(f) for f in range(4)])


# remolino: espiral que gira (la rota el codigo)
def espiral(f):
    im = lienzo(16)
    p = im.load()
    for k in range(240):
        t = k / 239
        a = t * math.pi * 4 + f * 0.7
        r = 1 + t * 6.5
        x, y = 7.5 + r * math.cos(a), 7.5 + r * math.sin(a)
        if 0 <= x < 16 and 0 <= y < 16:
            c = ESPUMA[4] if t > 0.75 else CIAN[3] if t > 0.4 else CIAN[2]
            p[int(x), int(y)] = c[:3] + (int(120 + 130 * t),)
    return im
guardar('nerea_remolino', [espiral(f) for f in range(3)])


# chispa de la cadena arrastrada: naranja de oxido al rojo
def chispa(l):
    im = lienzo(8)
    p = im.load()
    for y in range(8):
        for x in range(8):
            dx, dy = abs(x - 3.5), abs(y - 3.5)
            if (dx <= 0.5 and dy <= l) or (dy <= 0.5 and dx <= l):
                d = (dx + dy) / (l + 0.01)
                p[x, y] = hexc('fff4c0') if d < 0.3 else hexc('ffb040') if d < 0.65 else hexc('e05a10')
    return im
guardar('nerea_chispa', [chispa(3.5), chispa(2.5), chispa(1.5)])


# ojo: destello cian que vuela a los ojos durante la mirada
def destello(l):
    im = lienzo(8)
    p = im.load()
    for y in range(8):
        for x in range(8):
            dx, dy = abs(x - 3.5), abs(y - 3.5)
            if (dx <= 0.5 and dy <= l) or (dy <= 0.5 and dx <= l) or dx + dy <= l * 0.5:
                d = (dx + dy) / (l + 0.01)
                p[x, y] = CIAN[4] if d < 0.3 else CIAN[3] if d < 0.6 else CIAN[2]
    return im
guardar('nerea_ojo', [destello(3.5), destello(2.5), destello(1.5)])


# sello: esquirlas de cristal y de laton
def esquirla(semilla, rampa):
    r = random.Random(semilla)
    im = lienzo(6)
    p = im.load()
    pts = [(r.uniform(0, 2), r.uniform(0, 2)), (r.uniform(4, 6), r.uniform(0, 3)), (r.uniform(2, 6), r.uniform(4, 6))]
    (x1, y1), (x2, y2), (x3, y3) = pts
    den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    for y in range(6):
        for x in range(6):
            a = ((y2 - y3) * (x + 0.5 - x3) + (x3 - x2) * (y + 0.5 - y3)) / den
            b = ((y3 - y1) * (x + 0.5 - x3) + (x1 - x3) * (y + 0.5 - y3)) / den
            if a >= 0 and b >= 0 and a + b <= 1:
                p[x, y] = rampa[min(len(rampa) - 1, (x + y) // 3 + 2)] if (x + y) % 4 else rampa[-1]
    return im
guardar('nerea_sello', [esquirla(1, CIAN), esquirla(2, CIAN), esquirla(3, LATON), esquirla(4, LATON)])


# corazon: latido magenta que se abre
def latido(f):
    r = 1.6 + f * 1.1
    return circulo(8, 3.5, 3.5, r, lambda d, x, y: MAGENTA[4] if d < 0.35 and f == 0 else
                   (MAGENTA[3] if d > 0.7 else (MAGENTA[2] if f < 2 else None)))
guardar('nerea_corazon', [latido(f) for f in range(3)])


# luz: mota dorada de la liberacion
def mota(f):
    l = [3.0, 2.2, 1.4][f]
    im = lienzo(8)
    p = im.load()
    for y in range(8):
        for x in range(8):
            dx, dy = abs(x - 3.5), abs(y - 3.5)
            if dx + dy <= l:
                d = (dx + dy) / (l + 0.01)
                p[x, y] = ORO[4] if d < 0.35 else ORO[3] if d < 0.7 else ORO[2]
    return im
guardar('nerea_luz', [mota(f) for f in range(3)])

# onda expansiva: anillo de espuma que adelgaza al abrirse (3 fotogramas de 32x32)
def onda(f):
    n = 32
    im = lienzo(n)
    p = im.load()
    grosor = [0.20, 0.13, 0.08][f]
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - 15.5, y - 15.5) / 15.5
            e = abs(d - (1 - grosor))
            if d <= 1 and e <= grosor:
                k = 1 - e / grosor
                c = ESPUMA[4] if k > 0.6 else CIAN[3] if k > 0.3 else CIAN[2]
                p[x, y] = c[:3] + (int(255 * k ** 0.7),)
            elif d < 1 - grosor and f == 0 and rnd.random() < 0.04:
                p[x, y] = ESPUMA[3][:3] + (120,)
    return im
guardar('nerea_onda', [onda(f) for f in range(3)])

# rocas: esquirlas de prismarina y de ladrillo oscuro
PRIS = [hexc(c) for c in ('1d4a46', '2a645d', '3b8075', '5aa596', '8fd0bd')]
OSC = [hexc(c) for c in ('0f2a2c', '173b3c', '22504d', '2f6660', '3f7f76')]
guardar('nerea_roca', [esquirla(11, PRIS), esquirla(12, PRIS), esquirla(13, OSC), esquirla(14, OSC)])

# polvo: nube de arena que se abre y se aclara
ARENA = [hexc(c) for c in ('8f8466', 'a89c79', 'bdb18c', 'cfc39d', 'ddd2b0')]
def polvo(f):
    r = random.Random(f + 31)
    im = lienzo(8)
    p = im.load()
    rad = 1.9 + f * 0.55
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - 3.5 + r.uniform(-0.7, 0.7), y - 3.5 + r.uniform(-0.7, 0.7)) / rad
            if d <= 1 and (f < 2 or r.random() > 0.3):
                p[x, y] = ARENA[min(4, int((1 - d) * 3) + 1)][:3] + (200 - f * 40,)
    return im
guardar('nerea_polvo', [polvo(f) for f in range(4)])

# ======================================================================
#  LAGRIMA DE NEREA (item 16x16): gota de cristal de mar con aro de oro
# ======================================================================
la = lienzo(16)
p = la.load()
for y in range(16):
    for x in range(16):
        t = (y - 1) / 14
        if t < 0 or t > 1:
            continue
        semi = 5.6 * math.sin(math.pi * min(1.0, (t ** 1.5) * 1.04))
        dx = abs(x - 7.5)
        if dx <= semi:
            borde = dx > semi - 1.1 or y >= 14
            if borde:
                p[x, y] = ORO[2] if x < 8 else ORO[1]
            else:
                k = (x - 4) / 8 + (y - 5) / 12
                p[x, y] = CIAN[4] if (x in (5, 6) and 7 <= y <= 10) else CIAN[3] if k < 0.5 else CIAN[2] if k < 0.9 else CIAN[1]
# la maldicion dentro, ya purificada: una chispa dorada en el centro
for (x, y) in ((8, 10), (8, 11), (9, 10)):
    p[x, y] = ORO[4]
la.save(os.path.join(ITEM, 'lagrima_nerea.png'))

# ======================================================================
#  BENDICION DE LAS MAREAS (icono de efecto 18x18): ola dorada y burbujas
# ======================================================================
be = lienzo(18)
p = be.load()
for x in range(18):
    h = 6 + 3 * math.sin(x / 17 * math.pi * 1.6 + 0.4)
    for y in range(18):
        yy = 17 - y
        if 2 <= yy < h:
            p[x, y] = ORO[3] if yy > h - 2 else CIAN[2] if yy > h - 4 else CIAN[1]
for (cx, cy, rr) in ((5, 4, 2.2), (11, 3, 1.6), (14, 7, 1.2)):
    for y in range(18):
        for x in range(18):
            d = math.hypot(x - cx, y - cy)
            if rr - 0.8 <= d <= rr:
                p[x, y] = CIAN[4]
be.save(os.path.join(EFE, 'bendicion_mareas.png'))

# ======================================================================
#  MIEDO (gui 256x256): la vineta de cuando Nerea ruge o te mira. El color va
#  en la textura (el HUD la pinta en blanco): azul abismo en los bordes, con
#  vetas de agua oscura que se cuelan hacia el centro.
# ======================================================================
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
mi = lienzo(256)
p = mi.load()
rv = random.Random(77)
vetas = [(rv.uniform(0, math.tau), rv.uniform(0.55, 0.8), rv.uniform(0.02, 0.05)) for _ in range(22)]
for y in range(256):
    for x in range(256):
        dx, dy = (x - 127.5) / 127.5, (y - 127.5) / 127.5
        d = math.hypot(dx * 1.0, dy * 1.12)
        a = max(0.0, min(1.0, (d - 0.55) / 0.5)) ** 1.6
        ang = math.atan2(dy, dx)
        for (ang0, alcance, ancho) in vetas:
            da = abs((ang - ang0 + math.pi) % math.tau - math.pi)
            if da < ancho * (1.2 - d) * 6 and d > alcance - 0.25 * math.sin(ang0 * 3):
                a = max(a, 0.55 * (1 - da / (ancho * 6)))
        ondula = 0.06 * math.sin(d * 40 + ang * 3)
        a = max(0.0, min(1.0, a + ondula * a))
        p[x, y] = (6, 18, 30, int(255 * a))
mi.save(os.path.join(GUI, 'miedo_nerea.png'))

# El huevo de Nerea (item) lo dibuja huevos_jefes.py.

if len(sys.argv) > 2:
    todas = sorted(f for f in os.listdir(PAR) if f.startswith('nerea_'))
    prev = Image.new('RGBA', (len(todas) * 20, 22), (40, 40, 44, 255))
    for i, f in enumerate(todas):
        im = Image.open(os.path.join(PAR, f)).convert('RGBA').resize((16, 16), Image.NEAREST)
        prev.alpha_composite(im, (i * 20 + 2, 3))
    prev = prev.resize((prev.width * 5, prev.height * 5), Image.NEAREST)
    extras = Image.new('RGBA', (prev.width, 230), (40, 40, 44, 255))
    x = 4
    for f in ('burbuja.png', 'gancho.png', 'rayo.png'):
        im = Image.open(os.path.join(ENT, f)).convert('RGBA')
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        extras.alpha_composite(im, (x, 4))
        x += im.width + 8
    for f, k in ((os.path.join(ITEM, 'lagrima_nerea.png'), 8), (os.path.join(EFE, 'bendicion_mareas.png'), 8)):
        im = Image.open(f).convert('RGBA')
        im = im.resize((im.width * k, im.height * k), Image.NEAREST)
        extras.alpha_composite(im, (x, 4))
        x += im.width + 8
    hoja = Image.new('RGBA', (prev.width, prev.height + extras.height))
    hoja.paste(prev, (0, 0))
    hoja.paste(extras, (0, prev.height))
    hoja.save(sys.argv[2])
    print(len(todas), 'texturas de particula')

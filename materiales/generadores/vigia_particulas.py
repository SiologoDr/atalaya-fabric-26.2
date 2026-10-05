"""
Particulas del Vigia. Cada una es un dibujo propio, pintado aqui pixel a pixel
con la misma paleta del bicho (ambar del farol, rojo de caza, hierro, humo).

Las que llevan "gris" se tinen en el codigo (setColor): el rayo cambia de ambar
a rojo segun la carga, y eso con una sola imagen solo se puede si es clara.
"""
from PIL import Image
import math, os, sys, json, random

RAIZ = sys.argv[1]
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/particle')
DEF = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/particles')
os.makedirs(TEX, exist_ok=True); os.makedirs(DEF, exist_ok=True)
rnd = random.Random(42)

def hexc(s, a=255):
    s = s.lstrip('#'); return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)

def lienzo(n):
    return Image.new('RGBA', (n, n), (0, 0, 0, 0))

def guardar(nombre, frames):
    nombres = []
    for i, im in enumerate(frames):
        n = f'{nombre}_{i}' if len(frames) > 1 else nombre
        im.save(os.path.join(TEX, n + '.png'))
        nombres.append(f'atalaya:{n}')
    with open(os.path.join(DEF, nombre + '.json'), 'w', encoding='utf-8') as f:
        json.dump({'textures': nombres}, f, indent=2)
    return frames

AMBAR = [hexc(c) for c in ('8a4a10', 'c8741a', 'ffb43a', 'ffd36a', 'fff0a8')]
ROJO = [hexc(c) for c in ('701008', 'b01e10', 'ff3a24', 'ff8a70', 'ffd2c0')]

def radial(n, cx, cy, rampa, radio, forma=lambda dx, dy: math.hypot(dx, dy)):
    im = lienzo(n); p = im.load()
    for y in range(n):
        for x in range(n):
            d = forma(x - cx, y - cy) / radio
            if d > 1: continue
            k = min(int((1 - d) * len(rampa)), len(rampa) - 1)
            p[x, y] = rampa[k]
    return im

# --- chispa: estrella de 4 puntas, 3 tamanos que se encogen con la edad ---
def estrella4(n, largo, rampa):
    im = lienzo(n); p = im.load(); c = (n - 1) / 2
    for y in range(n):
        for x in range(n):
            dx, dy = abs(x - c), abs(y - c)
            # rombo con brazos: grosor que cae a lo largo de cada eje
            if (dx <= 0.5 and dy <= largo) or (dy <= 0.5 and dx <= largo) or (dx + dy <= largo * 0.45):
                d = (dx + dy) / (largo + 0.01)
                p[x, y] = rampa[4] if d < 0.25 else rampa[3] if d < 0.5 else rampa[2] if d < 0.8 else rampa[1]
    return im
guardar('vigia_chispa', [estrella4(8, l, AMBAR) for l in (3.5, 2.5, 1.5)])

# --- rayo: orbe con anillo, en GRISES (lo tine el codigo) ---
GRIS = [(90, 90, 90, 140), (160, 160, 160, 200), (215, 215, 215, 240), (245, 245, 245, 255), (255, 255, 255, 255)]
guardar('vigia_rayo', [radial(8, 3.5, 3.5, GRIS, 3.6)])

# --- marca: un ojo pequeno, rojo, de 8x8 (lo que flota alrededor del marcado) ---
def ojito(n, rampa, abierto=1.0):
    im = lienzo(n); p = im.load(); c = (n - 1) / 2
    for y in range(n):
        for x in range(n):
            dx, dy = (x - c) / (n / 2), (y - c)
            semi = (n / 2 - 1.2) * abierto * math.cos(dx * math.pi / 2) if abs(dx) <= 1 else -1
            if abs(dy) > semi: continue
            borde = abs(dy) > semi - 0.9
            p[x, y] = rampa[1] if borde else rampa[3] if abs(x - c) < 1.1 else rampa[2]
    # pupila
    for y in range(n):
        if p[int(c), y][3] and abs(y - c) < 1.6:
            p[int(c), y] = hexc('2b0505'); p[int(c) + 1, y] = hexc('2b0505')
    return im
guardar('vigia_marca', [ojito(8, ROJO, a) for a in (1.0, 0.6, 0.25)])

# --- maldicion: runa-ojo de 16x16 que se abre (3 fotogramas) ---
def runa(apertura):
    n = 16; im = lienzo(n); p = im.load(); c = 7.5
    # aro exterior roto en cuatro trozos: un sello, no un circulo
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - c, y - c); ang = math.degrees(math.atan2(y - c, x - c)) % 90
            if 6.2 <= d <= 7.4 and 12 < ang < 78:
                p[x, y] = ROJO[2] if d < 6.8 else ROJO[1]
    o = ojito(10, ROJO, apertura)
    im.alpha_composite(o, (3, 3))
    # cuatro marcas en los huecos del aro
    for (x, y) in ((7, 0), (8, 0), (0, 7), (0, 8), (15, 7), (15, 8), (7, 15), (8, 15)):
        p[x, y] = ROJO[3]
    return im
guardar('vigia_maldicion', [runa(a) for a in (0.2, 0.6, 1.0)])

# --- zarpa: tres tajos paralelos en diagonal, afilados en las puntas ---
def zarpa(fase):
    n = 16; im = lienzo(n); p = im.load()
    # cuanto del tajo se ve (de arriba-derecha a abajo-izquierda) y lo grueso
    hasta, grosor, rampa = [(0.45, 1.3, AMBAR), (1.0, 1.5, AMBAR), (1.0, 1.0, AMBAR), (1.0, 0.6, AMBAR[:3])][fase]
    for k in (-4, 0, 4):
        for i in range(160):
            t = i / 159 * hasta
            x = 13 - 10 * t + k * 0.7
            y = 2 + 11 * t + k * 0.7 + 1.5 * math.sin(math.pi * t)
            g = grosor * math.sin(math.pi * t) + 0.25
            for yy in range(int(y - g) - 1, int(y + g) + 2):
                for xx in range(int(x - g) - 1, int(x + g) + 2):
                    d = math.hypot(xx + 0.5 - x, yy + 0.5 - y)
                    if 0 <= xx < n and 0 <= yy < n and d <= g:
                        p[xx, yy] = rampa[-1] if d < g * 0.5 else rampa[-3]
    return im
guardar('vigia_zarpa', [zarpa(f) for f in range(4)])

# --- esquirla: trozos de cristal ahumado y de hierro, 4 variantes al azar ---
CRISTAL = [hexc('3a2816'), hexc('7a5a3c'), hexc('e3a52c'), hexc('fff0a8')]
HIERRO = [hexc('231f1c'), hexc('554638'), hexc('a8683a')]
def esquirla(semilla, rampa):
    r = random.Random(semilla); im = lienzo(6); p = im.load()
    pts = [(r.uniform(0, 2), r.uniform(0, 2)), (r.uniform(4, 6), r.uniform(0, 3)), (r.uniform(2, 6), r.uniform(4, 6))]
    def dentro(x, y):
        (x1, y1), (x2, y2), (x3, y3) = pts
        d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / d
        b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / d
        return a >= 0 and b >= 0 and a + b <= 1
    for y in range(6):
        for x in range(6):
            if dentro(x + 0.5, y + 0.5):
                p[x, y] = rampa[min(len(rampa) - 1, (x + y) // 3 + 1)] if (x + y) % 4 else rampa[-1]
    return im
guardar('vigia_esquirla', [esquirla(1, CRISTAL), esquirla(2, CRISTAL), esquirla(3, HIERRO), esquirla(4, HIERRO)])

# --- humo: bocanada que crece y se aclara; los dos primeros llevan brasa ---
HUMO = [(28, 24, 26, 210), (52, 46, 48, 190), (84, 76, 76, 160), (120, 112, 110, 120)]
def humo(fase):
    n = 8; im = lienzo(n); p = im.load(); r = random.Random(fase)
    radio = 1.6 + fase * 0.55
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - 3.5 + r.uniform(-0.4, 0.4), y - 3.5 + r.uniform(-0.4, 0.4))
            if d <= radio:
                k = min(3, int(d / radio * 2) + fase // 2)
                p[x, y] = HUMO[k]
    if fase < 2:
        for (x, y) in ((3, 4), (4, 3)):
            p[x, y] = AMBAR[3 - fase]
    return im
guardar('vigia_humo', [humo(f) for f in range(5)])

# --- alma: llamita ambar con la punta arriba, 3 fotogramas de parpadeo ---
def alma(fase):
    n = 8; im = lienzo(n); p = im.load()
    for y in range(n):
        t = y / (n - 1)                       # 0 arriba (punta), 1 abajo (base)
        semi = 2.8 * (t ** 0.75) if t < 0.8 else 2.8 * (0.8 ** 0.75) * math.sqrt(max(0.0, 1 - ((t - 0.8) / 0.2) ** 2))
        cx = 3.5 + (fase - 1) * 0.7 * (1 - t)  # la punta oscila, la base no
        for x in range(n):
            if abs(x + 0.5 - (cx + 0.5)) <= semi + 0.2:
                d = abs(x - cx) / (semi + 0.2)
                p[x, y] = AMBAR[4] if (d < 0.4 and t > 0.5) else AMBAR[3] if d < 0.7 and t > 0.25 else AMBAR[2]
    return im
guardar('vigia_alma', [alma(f) for f in range(3)])

# hoja de previsualizacion
todas = sorted(f for f in os.listdir(TEX) if f.startswith('vigia_'))
prev = Image.new('RGBA', (len(todas) * 20, 22), (40, 40, 44, 255))
for i, f in enumerate(todas):
    im = Image.open(os.path.join(TEX, f)).convert('RGBA')
    im = im.resize((16, 16), Image.NEAREST)
    prev.alpha_composite(im, (i * 20 + 2, 3))
prev.resize((prev.width * 6, prev.height * 6), Image.NEAREST).save(sys.argv[2])
print(len(todas), 'texturas:', ' '.join(t[:-4] for t in todas))

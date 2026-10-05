"""
Todo lo pequeno de Rajang, el Jaguar de Jade, que no es su cuerpo, pintado
aqui pixel a pixel (nada de vanilla):

  textures/particle/   las particulas rajang_*
  particles/           sus definiciones (la lista de fotogramas)
  textures/item/       colmillo_jade (el Colmillo de Jade, su botin)
  textures/mob_effect/ peso_tierra (la lentitud del Terremoto) y
                       bendicion_tierra (la bendicion al liberarlo)
  textures/gui/        miedo_rajang (la vineta: selva oscura con raices y
                       grietas que entran desde los bordes)

Particulas (fotogramas, tamano):
  rajang_polvo   3  8x8    polvo pardo que se abre y se aclara
  rajang_roca    3  8x8    terrones de roca parda (grande, mediano, pequeno)
  rajang_jade    3  8x8    esquirla, lasca y destello de jade
  rajang_chispa  3  8x8    brasas verdes de la maldicion (de grande a pequena)
  rajang_hoja    3  8x8    hojas de selva: verde oscuro, verde, verde amarillo
  rajang_onda    3  64x64  anillo de tierra, fino, que se apaga (tumbado)
  rajang_grieta  3  32x32  estrella de grietas que brillan, de corta a larga (tumbada)
  rajang_aviso   2  32x32  hexagono de aviso con la estrella rota; el 1 es el destello
  rajang_marca   8  32x32  la marca del Cataclismo: el arco de dentro se cierra
                           del 0 (casi entero) al 7 (casi nada)
  rajang_sello   2  64x64  el circulo del Sello; el 1 es el encendido
  rajang_runa    3  8x8    runas de oro: espiral cuadrada, glifo T, piramide
  rajang_llama   3  8x8    llama verde de los fragmentos (de grande a pequena)
  rajang_lastre  2  32x32  aro ambar con tres flechas hacia dentro; en el 1 se cierran
  rajang_oro     3  8x8    destellos de oro de la liberacion (de grande a pequeno)

Uso: python rajang_extras.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image, ImageDraw, ImageFilter
import math, os, sys, json, random

RAIZ = sys.argv[1]
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
PAR = os.path.join(A, 'textures/particle')
DEF = os.path.join(A, 'particles')
ITEM = os.path.join(A, 'textures/item')
EFE = os.path.join(A, 'textures/mob_effect')
GUI = os.path.join(A, 'textures/gui')
for d in (PAR, DEF, ITEM, EFE, GUI):
    os.makedirs(d, exist_ok=True)
rnd = random.Random(3303)
TAU = 2 * math.pi


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def lienzo(w, h=None):
    return Image.new('RGBA', (w, h or w), (0, 0, 0, 0))


def mezclar(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


def alfa(c, a):
    return c[:3] + (max(0, min(255, int(a))),)


JADE = [hexc(c) for c in ('07160e', '0e2a1c', '143a27', '1c4e34', '266444', '387a56', '3aa866', '58c886', '86e2a8')]
ORO = [hexc(c) for c in ('3a2606', '5e400e', '8f6418', 'c28d28', 'e2b443', 'f8d97c', 'fffbe8')]
ROCA = [hexc(c) for c in ('21180f', '3a2b1d', '54402b', '70573b', '8c7050', 'a88c66', 'c4aa82')]
POLVO = [hexc(c) for c in ('5a5244', '73695a', '8d8370', 'a69c86', 'c0b69e', 'd6cdb6')]
HOJA = [hexc(c) for c in ('17361a', '24522a', '336e34', '4a8c3a', '6aa840', '94c44a', 'bcd85c')]
AMBAR = [hexc(c) for c in ('4a2606', '7a420c', 'b06a14', 'd8901f', 'eeb040', 'fbd57a', 'fff0c0')]
# la maldicion: verde (II), lima (III), amarillo lima (IV); y su nucleo casi blanco
VERDE = hexc('8cff5a')
LIMA = hexc('c8ff2a')
LIMA_CLARO = hexc('e6ff4a')
NUCLEO = hexc('f2ffe0')


def guardar(nombre, frames):
    nombres = []
    for i, im in enumerate(frames):
        n = f'{nombre}_{i}' if len(frames) > 1 else nombre
        im.save(os.path.join(PAR, n + '.png'))
        nombres.append(f'atalaya:{n}')
    with open(os.path.join(DEF, nombre + '.json'), 'w', encoding='utf-8') as f:
        json.dump({'textures': nombres}, f, indent=2)
    return frames


def pintar(im, dibujo, paleta, ox=0, oy=0):
    q = im.load()
    for y, fila in enumerate(dibujo):
        for x, c in enumerate(fila):
            if c != '.' and 0 <= ox + x < im.width and 0 <= oy + y < im.height:
                q[ox + x, oy + y] = paleta[c]
    return im


def contorno(im, color):
    """Pone un contorno de un pixel (4 vecinos) alrededor de lo pintado."""
    q = im.load()
    w, h = im.size
    llenos = {(x, y) for y in range(h) for x in range(w) if q[x, y][3] > 0}
    for (x, y) in llenos:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = x + dx, y + dy
            if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in llenos:
                q[xx, yy] = color
    return im


def cobertura(dentro, x, y, s=4):
    """Que parte del pixel (x, y) cubre la forma: se muestrea s x s veces.
    Asi las formas giradas salen con el canto limpio, sin dientes sueltos."""
    n = 0
    for j in range(s):
        for i in range(s):
            if dentro(x + (i + 0.5) / s, y + (j + 0.5) / s):
                n += 1
    return n / (s * s)


def dist_segmento(px, py, x0, y0, x1, y1):
    vx, vy = x1 - x0, y1 - y0
    l2 = vx * vx + vy * vy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - x0) * vx + (py - y0) * vy) / l2))
    return math.hypot(px - x0 - t * vx, py - y0 - t * vy)


# ======================================================================
#  PARTICULAS
# ======================================================================
# --- polvo: nube parda que crece, se aclara y se deshace
def polvo(f):
    im = lienzo(8)
    p = im.load()
    r = random.Random(400 + f)
    R = [2.3, 3.0, 3.7][f]
    bultos = [(4.0, 4.4, R), (4.0 - R * 0.45, 4.3, R * 0.66), (4.0 + R * 0.45, 3.8, R * 0.7), (4.0, 3.9 - R * 0.35, R * 0.62)]
    for y in range(8):
        for x in range(8):
            px, py = x + 0.5, y + 0.5
            d = min(math.hypot(px - bx, py - by) / br for bx, by, br in bultos)
            if d > 1:
                continue
            if f == 2 and d > 0.45 and r.random() < 0.32:
                continue                                    # se deshace
            luz = -((px - 4) + (py - 4)) / (2 * R)
            k = 2 + f // 2 + (1 if luz > 0.12 else 0) - (1 if luz < -0.25 else 0)
            if d < 0.45 and f < 2:
                k += 1
            a = [235, 200, 150][f] * (1 - max(0.0, d - 0.55) * 1.3)
            p[x, y] = alfa(POLVO[max(0, min(5, k))], a)
    return im


guardar('rajang_polvo', [polvo(f) for f in range(3)])

# --- roca: terrones de roca parda (como en las ilustraciones: casi cubicos)
ROCA_PAL = {'o': ROCA[0], '1': ROCA[1], '2': ROCA[2], '3': ROCA[3], '4': ROCA[4], '5': ROCA[5], '6': ROCA[6],
            'j': JADE[6], 'J': JADE[8]}
TERRONES = [
    [".oooooo.",
     "o666655o",
     "o655542o",
     "o443322o",
     "o44J321o",
     "o43j221o",
     "o332211o",
     ".ooooo.."],
    ["........",
     "..ooo...",
     ".o665o..",
     ".o5543o.",
     ".o44321o",
     ".o3321o.",
     "..oooo..",
     "........"],
    ["........",
     "........",
     "...ooo..",
     "..o654o.",
     "..o431o.",
     "...ooo..",
     "........",
     "........"],
]
guardar('rajang_roca', [pintar(lienzo(8), t, ROCA_PAL) for t in TERRONES])

# --- jade: esquirla larga, lasca, destello
JADE_PAL = {'o': JADE[1], '3': JADE[3], '4': JADE[4], '5': JADE[5], '6': JADE[6], '7': JADE[7], '8': JADE[8],
            'w': hexc('f0fff4')}
ESQUIRLAS = [
    ["......o.",
     ".....o8o",
     "....o87o",
     "...o876o",
     "..o865o.",
     ".o865o..",
     ".o54o...",
     "..oo...."],
    ["........",
     "...oo...",
     "..o8wo..",
     ".o8776o.",
     ".o7654o.",
     "..o54o..",
     "...oo...",
     "........"],
    ["........",
     "...w....",
     "...8....",
     ".w878w..",
     "...8....",
     "...w....",
     "........",
     "........"],
]
guardar('rajang_jade', [pintar(lienzo(8), e, JADE_PAL) for e in ESQUIRLAS])


# --- chispa: brasa verde de la maldicion, de grande a pequena
def brasa(f):
    im = lienzo(8)
    p = im.load()
    radio = [3.4, 2.4, 1.5][f]
    for y in range(8):
        for x in range(8):
            dx, dy = abs(x - 3.5), abs(y - 3.5)
            d = (dx + dy) / radio                     # rombo
            cruz = min(dx, dy) < 0.6 and max(dx, dy) < radio + 0.6
            if d <= 1 or cruz:
                t = min(1.0, (dx + dy) / (radio + 0.6))
                if t < 0.3:
                    c = NUCLEO
                elif t < 0.65:
                    c = mezclar(VERDE, LIMA, 0.25)
                else:
                    c = alfa(JADE[7], 200)
                p[x, y] = c
    return im


guardar('rajang_chispa', [brasa(f) for f in range(3)])


# --- hoja: hojas de selva con su nervio y su tallo; la luz de arriba a la izquierda
def hoja_base(rampa, ancho):
    """Una hoja tumbada en la diagonal: el tallo abajo a la izquierda, la punta arriba a la derecha."""
    im = lienzo(8)
    p = im.load()
    for y in range(8):
        for x in range(8):
            k = x + y - 7                              # 0 sobre el nervio
            t = (x - y + 7) / 14                       # 0 en el tallo, 1 en la punta
            w = ancho * math.sin(math.pi * min(1.0, t ** 0.85))
            if abs(k) <= round(w):
                if k == 0:
                    c = rampa[4] if 0.1 < t < 0.9 else rampa[2]
                elif k < 0:
                    c = rampa[3] if abs(k) < round(w) else rampa[2]
                else:
                    c = rampa[1] if abs(k) < round(w) else rampa[0]
                p[x, y] = c
    p[0, 7] = rampa[1]                                 # el tallo
    return im


guardar('rajang_hoja', [
    hoja_base(HOJA[0:5], 2.3),
    hoja_base(HOJA[1:6], 2.0).transpose(Image.FLIP_LEFT_RIGHT),
    hoja_base(HOJA[2:7], 2.6).transpose(Image.ROTATE_270),
])


# --- onda: anillo de tierra que se abre, fino, con terrones sueltos
def onda(f):
    n = 64
    im = lienzo(n)
    p = im.load()
    r = random.Random(600 + f)
    claro, medio, oscuro = hexc('e4f0cc'), hexc('b4cc94'), hexc('7a8c5c')
    fuerza = [1.0, 0.75, 0.45][f]
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2, y + 0.5 - n / 2
            d = math.hypot(dx, dy) / (n / 2)
            ang = math.atan2(dy, dx)
            # el anillo se desmigaja: el grosor y el alfa cambian con el angulo
            ondula = 0.5 + 0.5 * math.sin(ang * 7 + f) * math.sin(ang * 3 + 1.0)
            g = abs(d - 0.88) / (0.045 + 0.02 * ondula)
            if g < 1:
                c = claro if g < 0.35 else medio if g < 0.75 else oscuro
                a = 235 * fuerza * (0.75 + 0.25 * ondula)
                if g > 0.75:
                    a *= 0.6
                p[x, y] = alfa(c, a)
            elif 0.74 < d < 0.8 and r.random() < 0.10 * fuerza:
                p[x, y] = alfa(medio, 150 * fuerza)   # polvo que queda dentro
    # terrones que salen despedidos por fuera
    for _ in range(int(14 * fuerza)):
        a = r.uniform(0, TAU)
        rr = r.uniform(0.94, 0.99) * n / 2
        x, y = int(n / 2 + rr * math.cos(a)), int(n / 2 + rr * math.sin(a))
        if 0 <= x < n and 0 <= y < n:
            p[x, y] = alfa(oscuro, 220 * fuerza)
    return im


guardar('rajang_onda', [onda(f) for f in range(3)])


# --- grieta: estrella de grietas oscuras por las que se ve el brillo verde
def red_grietas(semilla, n, largo, ramas=6, sub=True):
    """Lista de segmentos (x0, y0, x1, y1, grosor) de una estrella de grietas."""
    r = random.Random(semilla)
    segs = []
    c = n / 2

    def rama(x, y, ang, resto, grosor, prof):
        while resto > 0:
            paso = r.uniform(1.6, 2.6)
            ang += r.uniform(-0.45, 0.45)
            nx, ny = x + paso * math.cos(ang), y + paso * math.sin(ang)
            segs.append((x, y, nx, ny, grosor))
            x, y = nx, ny
            resto -= paso
            grosor = max(1.0, grosor - 0.35)
            if sub and prof == 0 and resto > 3 and r.random() < 0.3:
                rama(x, y, ang + r.choice((-1, 1)) * r.uniform(0.6, 1.0), resto * 0.5, 1.0, 1)

    base = r.uniform(0, TAU)
    for i in range(ramas):
        a = base + i * TAU / ramas + r.uniform(-0.3, 0.3)
        rama(c, c, a, largo * r.uniform(0.75, 1.0), 2.2, 0)
    return segs


def grieta(f):
    """Una fisura en el suelo: dos brazos opuestos que serpentean con alguna
    ramita, oscura por fuera y con la luz verde por dentro; crece de corta a
    larga (no una estrella: asi parece tierra rota)."""
    n = 32
    largo = [8.0, 12.0, 15.5][f]
    segs = red_grietas(77, n, largo, ramas=2)
    # se dibuja en grande y se reduce a pixeles duros
    k = 8
    mask = Image.new('L', (n * k, n * k), 0)
    d = ImageDraw.Draw(mask)
    for (x0, y0, x1, y1, g) in segs:
        if math.hypot(x0 - n / 2, y0 - n / 2) > largo:
            continue
        d.line((x0 * k, y0 * k, x1 * k, y1 * k), fill=255, width=max(1, int(g * k * 0.75)))
    d.ellipse((n / 2 * k - 1.2 * k, n / 2 * k - 1.2 * k, n / 2 * k + 1.2 * k, n / 2 * k + 1.2 * k), fill=255)
    mask = mask.resize((n, n), Image.BOX)
    grieta_px = {(x, y) for y in range(n) for x in range(n) if mask.getpixel((x, y)) > 70}
    im = lienzo(n)
    p = im.load()
    # el halo verde alrededor
    for y in range(n):
        for x in range(n):
            dmin = 9
            for (gx, gy) in grieta_px:
                if abs(gx - x) <= 2 and abs(gy - y) <= 2:
                    dmin = min(dmin, max(abs(gx - x), abs(gy - y)))
            if dmin == 1:
                p[x, y] = alfa(JADE[6], 135)
            elif dmin == 2:
                p[x, y] = alfa(JADE[5], 60)
    # la grieta: canto oscuro y, por dentro, la luz
    for (x, y) in grieta_px:
        dentro = all((x + dx, y + dy) in grieta_px for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        dist = math.hypot(x + 0.5 - n / 2, y + 0.5 - n / 2) / max(1.0, largo)
        if dentro:
            p[x, y] = NUCLEO if dist < 0.18 else VERDE
        elif dist < 0.55 and mask.getpixel((x, y)) > 150:
            p[x, y] = mezclar(VERDE, JADE[6], 0.4)
        else:
            p[x, y] = hexc('120c06', 240)
    return im


guardar('rajang_grieta', [grieta(f) for f in range(3)])


# --- el zarpazo: tres garras en arco que cortan el aire (blanco por dentro,
#     jade por fuera), de recien salido a deshaciendose
def zarpazo(f):
    n = 64
    k = 4
    m = Image.new('L', (n * k, n * k), 0)
    b = Image.new('L', (n * k, n * k), 0)
    dm, db = ImageDraw.Draw(m), ImageDraw.Draw(b)
    largo = [0.55, 1.0, 1.0][f]
    grosor = [3.2, 3.6, 2.2][f]
    for i in range(3):
        off = (i - 1) * 9.0
        pts = []
        for j in range(25):
            t = j / 24
            if t > largo:
                break
            ang = math.radians(-58 + 116 * t)
            r = 27 - abs(i - 1) * 1.5
            x = 32 + off * 0.55 + math.sin(ang) * r * 0.95
            y = 46 + off - math.cos(ang) * r * 0.55 - 6
            pts.append((x * k, y * k, math.sin(math.pi * t)))
        for (x0, y0, w0), (x1, y1, w1) in zip(pts, pts[1:]):
            g = max(1.0, grosor * (0.25 + 0.75 * (w0 + w1) / 2))
            dm.line((x0, y0, x1, y1), fill=255, width=int(g * k * 1.9))
            db.line((x0, y0, x1, y1), fill=255, width=max(1, int(g * k * 0.7)))
    m = m.filter(ImageFilter.GaussianBlur(k * 0.8)).resize((n, n), Image.LANCZOS)
    b = b.resize((n, n), Image.LANCZOS)
    im = lienzo(n)
    q = im.load()
    desv = [1.0, 1.0, 0.55][f]
    for y in range(n):
        for x in range(n):
            a = m.getpixel((x, y)) / 255
            c = b.getpixel((x, y)) / 255
            if a < 0.04 and c < 0.04:
                continue
            col = mezclar(JADE[7], NUCLEO, min(1.0, c * 1.4))
            q[x, y] = alfa(col, 255 * min(1.0, max(a * 0.85, c)) * desv)
    return im


guardar('rajang_zarpazo', [zarpazo(f) for f in range(3)])


# --- aviso: hexagono de aviso con una estrella rota dentro
def hexagono(px, py, c, radio):
    dx, dy = abs(px - c), abs(py - c)
    return max(dx, dx * 0.5 + dy * 0.866) / radio       # hexagono con las puntas a los lados


def rayos_rotos(semilla, c, n_rayos, largo, hueco):
    """Rayos quebrados que salen del centro; cada uno con un hueco (la rotura)."""
    r = random.Random(semilla)
    rayos = []
    for i in range(n_rayos):
        ang = i * TAU / n_rayos + math.pi / n_rayos + r.uniform(-0.12, 0.12)
        pts = [(c, c)]
        x, y = c, c
        dist = 0.0
        while dist < largo:
            paso = r.uniform(1.6, 2.4)
            ang += r.uniform(-0.3, 0.3)
            x += paso * math.cos(ang)
            y += paso * math.sin(ang)
            dist += paso
            pts.append((x, y))
        segs = []
        acum = 0.0
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            l = math.hypot(x1 - x0, y1 - y0)
            segs.append((x0, y0, x1, y1, acum, acum + l))
            acum += l
        rayos.append(segs)
    return rayos


def aviso(f):
    n = 32
    c = n / 2
    im = lienzo(n)
    p = im.load()
    rayos = rayos_rotos(81, c, 6, 9.5, (4.2, 5.8))
    for y in range(n):
        for x in range(n):
            h = hexagono(x + 0.5, y + 0.5, c, n / 2)
            if 0.86 < h <= 0.94:
                p[x, y] = mezclar(VERDE, NUCLEO, 0.5) if f == 1 else VERDE
            elif 0.94 < h <= 1.0:
                p[x, y] = alfa(JADE[6], 230)
            elif 0.80 < h <= 0.86:
                p[x, y] = alfa(JADE[3], 150)
            elif 0.70 < h <= 0.74 and (x + y) % 3 == 0:
                p[x, y] = alfa(JADE[7], 210)          # el hilo de dentro, punteado
            elif f == 1 and h <= 0.80:
                p[x, y] = alfa(VERDE, 48)             # destello: el hexagono se llena

            # la estrella rota
            def en_rayo(px, py):
                for segs in rayos:
                    for (x0, y0, x1, y1, a0, a1) in segs:
                        dd = dist_segmento(px, py, x0, y0, x1, y1)
                        if dd < 1.25:
                            # posicion a lo largo del rayo
                            l = math.hypot(x1 - x0, y1 - y0) or 1
                            t = max(0.0, min(1.0, ((px - x0) * (x1 - x0) + (py - y0) * (y1 - y0)) / (l * l)))
                            s = a0 + t * (a1 - a0)
                            if 4.2 < s < 5.8:
                                continue                # la rotura
                            grosor = 1.05 - 0.45 * min(1.0, s / 9.5)
                            if dd < grosor:
                                return True
                return False

            if h < 0.78:
                cov = cobertura(en_rayo, x, y)
                if cov >= 0.4:
                    dc = math.hypot(x + 0.5 - c, y + 0.5 - c)
                    p[x, y] = NUCLEO if dc < 2.6 else VERDE if dc < 7.5 else alfa(JADE[7], 235)
    return im


guardar('rajang_aviso', [aviso(f) for f in range(2)])


# --- marca del Cataclismo: doble aro con dientes escalonados, rombo de jade
#     y la cuenta atras: un arco que se cierra fotograma a fotograma
def marca(f):
    n = 32
    c = n / 2
    im = lienzo(n)
    p = im.load()
    tramo = TAU * (0.94 - f * 0.125)                   # del 0 (casi entero) al 7 (casi nada)
    OSC = hexc('5a8a10')

    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - c, y + 0.5 - c
            d = math.hypot(dx, dy)
            desde_arriba = (math.atan2(dy, dx) + math.pi / 2) % TAU
            if 12.4 < d <= 13.6:
                p[x, y] = LIMA if d < 13.1 else alfa(OSC, 240)
            elif 10.0 < d <= 11.1:
                p[x, y] = alfa(hexc('a6e01c'), 235)
            elif 6.2 < d <= 8.6:
                if desde_arriba <= tramo:
                    p[x, y] = LIMA_CLARO if 6.9 < d <= 7.9 else alfa(LIMA, 225)
                    if desde_arriba > tramo - 0.22:
                        p[x, y] = NUCLEO              # la punta del arco, encendida
                else:
                    p[x, y] = alfa(hexc('2e4a0c'), 110)   # el carril que ya se ha cerrado
    # los dientes escalonados: cuatro grandes en los ejes y cuatro pequenos en las diagonales
    norte = [(x, 1, LIMA) for x in range(13, 19)] + [(15, 0, LIMA), (16, 0, LIMA)] + [(12, 1, alfa(OSC, 240)), (19, 1, alfa(OSC, 240))]
    diag = [(25, 5, LIMA), (26, 5, LIMA), (26, 6, LIMA), (25, 4, alfa(OSC, 240)), (27, 6, alfa(OSC, 240)), (27, 4, LIMA)]
    for (x, y, col) in norte:
        for (xx, yy) in ((x, y), (31 - y, x), (31 - x, 31 - y), (y, 31 - x)):
            p[xx, yy] = col
    for (x, y, col) in diag:
        for (xx, yy) in ((x, y), (31 - y, x), (31 - x, 31 - y), (y, 31 - x)):
            p[xx, yy] = col
    # el rombo de jade del centro, con su contorno y su brillo
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - c, y + 0.5 - c
            r = abs(dx) + abs(dy)
            if r <= 5.0:
                if r > 4.0:
                    p[x, y] = JADE[1]
                else:
                    luz = -(dx + dy) / 6
                    p[x, y] = JADE[8] if luz > 0.35 else JADE[7] if luz > 0.05 else JADE[6] if luz > -0.3 else JADE[5]
    p[int(c) - 1, int(c) - 2] = hexc('f0fff4')
    p[int(c), int(c)] = LIMA_CLARO
    return im


guardar('rajang_marca', [marca(f) for f in range(8)])

# --- sello: el circulo del Sello de la Tierra
#   '#' trazo, '+' relleno, 'e' ojos encendidos, 'k' puntos de los bigotes
MASCARA = [
    "##.................##",
    "#+#...............#+#",
    "#++#.............#++#",
    "#+++#############+++#",
    "#+++++++++++++++++++#",
    "#++######+++######++#",
    "#+#eeeee#+++#eeeee#+#",
    "#++#eee#+++++#eee#++#",
    "#+++###+++#+++###+++#",
    ".#+++++++###+++++++#.",
    ".#+k+k++#####++k+k+#.",
    ".#++++++++#++++++++#.",
    "..#+#############+#..",
    "..#+#f#+++++++#f#+#..",
    "...#+#f#+++++#f#+#...",
    "....#+f#+++++#f+#....",
    ".....#f#######f#.....",
    "......f.......f......",
]


def sello(f):
    n = 64
    c = n / 2
    im = lienzo(n)
    p = im.load()
    luz = 1.0 if f == 1 else 0.85
    claro = mezclar(VERDE, NUCLEO, 0.4) if f == 1 else VERDE

    def piramide(px, py):
        """La greca: piramides escalonadas que miran hacia fuera, sobre una base."""
        dx, dy = px - c, py - c
        d = math.hypot(dx, dy)
        if not (25.2 < d <= 30.2):
            return False
        if d <= 26.3:
            return True                               # la base
        u = ((math.atan2(dy, dx) + math.pi) / TAU * 16) % 1.0
        m = abs(u - 0.5)
        if d <= 27.6:
            return m < 0.36
        if d <= 28.9:
            return m < 0.24
        return m < 0.11

    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - c, y + 0.5 - c
            d = math.hypot(dx, dy)
            if 30.6 < d <= 31.7:
                p[x, y] = alfa(claro, 245 * luz)
            elif 31.7 < d <= 32.0:
                p[x, y] = alfa(JADE[5], 150 * luz)
            elif 25.2 < d <= 30.6:
                cov = cobertura(piramide, x, y)
                if cov >= 0.5:
                    p[x, y] = alfa(claro if cov > 0.85 else JADE[6], 225 * luz)
                elif cov > 0.15:
                    p[x, y] = alfa(JADE[5], 140 * luz)
                else:
                    p[x, y] = alfa(JADE[3], 60 * luz)
            elif 23.9 < d <= 25.2:
                p[x, y] = alfa(claro, 250 * luz)
            elif d <= 23.9:
                p[x, y] = alfa(JADE[4], 36 * luz)    # el fondo del circulo, apenas
    # los cuatro nodos en las diagonales, unidos al centro
    nodos = [(c + 20.2 * math.cos(a), c + 20.2 * math.sin(a)) for a in (math.pi / 4 + i * math.pi / 2 for i in range(4))]
    for (nx, ny) in nodos:
        def enlace(px, py, nx=nx, ny=ny):
            if math.hypot(px - c, py - c) < 10.5:
                return False
            return dist_segmento(px, py, c, c, nx, ny) < 0.95
        for y in range(n):
            for x in range(n):
                if cobertura(enlace, x, y) >= 0.45:
                    p[x, y] = alfa(claro, 220 * luz)
        for y in range(n):
            for x in range(n):
                dd = math.hypot(x + 0.5 - nx, y + 0.5 - ny)
                if dd <= 3.7:
                    if dd > 2.6:
                        p[x, y] = alfa(claro, 250 * luz)
                    elif dd > 1.5:
                        p[x, y] = JADE[2]
                    else:
                        p[x, y] = NUCLEO if f == 1 else LIMA
    # la mascara del jaguar en el centro, con los sables colgando
    pal = {'#': alfa(claro, 255 * luz), '+': alfa(JADE[5], 165 * luz), 'k': JADE[1],
           'e': NUCLEO if f == 1 else LIMA_CLARO, 'f': NUCLEO if f == 1 else mezclar(VERDE, NUCLEO, 0.6)}
    pintar(im, MASCARA, pal, int(c) - 10, int(c) - 9)
    return im


guardar('rajang_sello', [sello(f) for f in range(2)])

# --- runas de oro: espiral cuadrada, glifo T, piramide escalonada
RUNAS = [
    ["yyyyyyy.",
     "Y.....Y.",
     "Y.yyY.Y.",
     "Y.Y.Y.Y.",
     "Y.Y...Y.",
     "Y.GGGGG.",
     "Y.......",
     "........"],
    [".yyyyyy.",
     ".Y....Y.",
     ".Y.yY.Y.",
     "...YG...",
     "...YG...",
     ".yYGGGG.",
     "........",
     "........"],
    ["...yY...",
     "..yYYG..",
     "..Y..G..",
     ".yY..GG.",
     ".Y.yG.G.",
     "yYYYGGGG",
     "........",
     "........"],
]


def runa(f):
    im = lienzo(8)
    pal = {'y': ORO[5], 'Y': ORO[4], 'G': ORO[3]}
    pintar(im, RUNAS[f], pal)
    # sombra de oro oscuro abajo a la derecha, para que se lea sobre cualquier fondo
    q = im.load()
    llenos = [(x, y) for y in range(8) for x in range(8) if q[x, y][3]]
    for (x, y) in llenos:
        if x + 1 < 8 and y + 1 < 8 and q[x + 1, y + 1][3] == 0:
            q[x + 1, y + 1] = alfa(ORO[1], 200)
    return im


guardar('rajang_runa', [runa(f) for f in range(3)])

# --- llama verde: la estela de los fragmentos del Cataclismo
LLAMAS = [
    ["...a....",
     "...ba...",
     "..abb...",
     "..bccb..",
     ".bcddcb.",
     ".bcdwdb.",
     ".bcddcb.",
     "..bccb.."],
    ["........",
     "....a...",
     "...ab...",
     "..abcb..",
     "..bcdc..",
     "..bcwc..",
     "...bcb..",
     "........"],
    ["........",
     "........",
     "....a...",
     "...bb...",
     "...cdb..",
     "...bcb..",
     "........",
     "........"],
]
LLAMA_PAL = {'a': alfa(JADE[6], 150), 'b': alfa(JADE[7], 230), 'c': VERDE, 'd': mezclar(VERDE, NUCLEO, 0.6),
             'w': NUCLEO}
guardar('rajang_llama', [pintar(lienzo(8), l, LLAMA_PAL) for l in LLAMAS])


# --- lastre: aro ambar con tres flechas hacia dentro (la lentitud bajo los pies)
def lastre(f):
    n = 32
    c = n / 2
    im = lienzo(n)
    p = im.load()
    for y in range(n):
        for x in range(n):
            d = math.hypot(x + 0.5 - c, y + 0.5 - c)
            if 13.5 < d <= 15.0:
                p[x, y] = (AMBAR[6] if f == 1 else AMBAR[5]) if d < 14.3 else AMBAR[3]
            elif 15.0 < d <= 15.9:
                p[x, y] = alfa(AMBAR[1], 210)
            elif 12.6 < d <= 13.5:
                p[x, y] = alfa(AMBAR[2], 150)
            elif (d <= 12.6 and f == 1):
                p[x, y] = alfa(AMBAR[3], 26)
    # las tres flechas, en su capa, con su contorno oscuro
    capa = lienzo(n)
    q = capa.load()
    meter = 1.6 if f == 1 else 0.0
    for i in range(3):
        a = -math.pi / 2 + i * TAU / 3
        ux, uy = math.cos(a), math.sin(a)              # hacia fuera
        vx, vy = -uy, ux

        def v_flecha(px, py, ux=ux, uy=uy, vx=vx, vy=vy):
            dx, dy = px - c, py - c
            s = dx * ux + dy * uy
            t = dx * vx + dy * vy
            # punta de flecha con muesca: el frente en V y la espalda mas abierta
            s0 = 4.8 - meter
            return s >= s0 + abs(t) * 1.1 and s <= s0 + 3.4 + abs(t) * 0.35

        for y in range(n):
            for x in range(n):
                cov = cobertura(v_flecha, x, y)
                if cov >= 0.45:
                    dx, dy = x + 0.5 - c, y + 0.5 - c
                    s = dx * ux + dy * uy
                    t = dx * vx + dy * vy
                    b = s - (4.8 - meter) - abs(t) * 1.1
                    q[x, y] = AMBAR[6] if b < 1.0 else AMBAR[5] if b < 1.9 else AMBAR[4]
    contorno(capa, alfa(AMBAR[0], 220))
    im.alpha_composite(capa)
    return im


guardar('rajang_lastre', [lastre(f) for f in range(2)])

# --- oro: destellos de la liberacion
ORO_PAL = {'w': ORO[6], 'y': ORO[5], 'Y': ORO[4], 'G': alfa(ORO[3], 200), 'g': alfa(ORO[2], 140)}
DESTELLOS = [
    ["...g....",
     "...G....",
     "...Y....",
     "gGYwYGg.",
     "...Y....",
     "...G....",
     "...g....",
     "........"],
    ["........",
     "...G....",
     "..gYg...",
     ".GYwYG..",
     "..gYg...",
     "...G....",
     "........",
     "........"],
    ["........",
     "........",
     "...g....",
     "..gyg...",
     "...g....",
     "........",
     "........",
     "........"],
]
guardar('rajang_oro', [pintar(lienzo(8), dd, ORO_PAL) for dd in DESTELLOS])

# ======================================================================
#  OBJETO: el Colmillo de Jade (16x16): un sable curvo de jade con su
#  casquillo de oro escalonado en la raiz
# ======================================================================
P0, P1, P2 = (13.2, 2.4), (3.6, 3.4), (2.0, 14.9)     # raiz, control, punta


def curva(t):
    a, b, cc = (1 - t) ** 2, 2 * (1 - t) * t, t * t
    return (a * P0[0] + b * P1[0] + cc * P2[0], a * P0[1] + b * P1[1] + cc * P2[1])


def tangente(t):
    return (2 * (1 - t) * (P1[0] - P0[0]) + 2 * t * (P2[0] - P1[0]),
            2 * (1 - t) * (P1[1] - P0[1]) + 2 * t * (P2[1] - P1[1]))


MUESTRAS = [(i / 400, curva(i / 400)) for i in range(401)]


def ancho_colmillo(t):
    return 2.55 * (1 - t) ** 0.8 + 0.3


def cercano(px, py):
    mejor = None
    for t, (x, y) in MUESTRAS:
        dd = math.hypot(px - x, py - y)
        if mejor is None or dd < mejor[0]:
            mejor = (dd, t, x, y)
    return mejor


def en_colmillo(px, py):
    dd, t, _, _ = cercano(px, py)
    return dd < ancho_colmillo(t) and t >= 0.0


co = lienzo(16)
p = co.load()
for y in range(16):
    for x in range(16):
        if cobertura(en_colmillo, x, y, 3) < 0.5:
            continue
        dd, t, cx, cy = cercano(x + 0.5, y + 0.5)
        tx, ty = tangente(t)
        l = math.hypot(tx, ty) or 1
        lado = (tx * (y + 0.5 - cy) - ty * (x + 0.5 - cx)) / l    # > 0 por el lomo (arriba a la izquierda)
        s = lado / ancho_colmillo(t)
        if t < 0.07:
            p[x, y] = ORO[2] if s > -0.2 else ORO[1]                  # el canto de la raiz
        elif t < 0.22:
            # el casquillo de oro con su escalon grabado
            escalon = 0.15 if s > 0.1 else 0.18 if s > -0.4 else 0.21
            if abs(t - escalon) < 0.018:
                p[x, y] = ORO[2]
            else:
                p[x, y] = ORO[5] if s > 0.35 else ORO[4] if s > -0.25 else ORO[3]
        else:
            k = 8 if s > 0.5 else 7 if s > 0.05 else 6 if s > -0.45 else 5
            if t > 0.8:
                k -= 1
            p[x, y] = JADE[k]
contorno(co, JADE[0])
p[6, 6] = hexc('f4fff8')                                           # el brillo
co.save(os.path.join(ITEM, 'colmillo_jade.png'))

# ======================================================================
#  EFECTOS (18x18)
# ======================================================================
# Peso de la Tierra: una pesa de piedra parda con su asa y una banda ambar
PESA = [
    "..................",
    "......oooooo......",
    ".....o566665o.....",
    ".....o5o..o3o.....",
    ".....o5o..o3o.....",
    "....oooooooooo....",
    "....o66666554o....",
    "...o5666665543o...",
    "...o5666655443o...",
    "..oyAAAAAAAAAAao..",
    "..o5aaaaaaaaaa2o..",
    "..o555544433221o..",
    ".o55544443332211o.",
    ".o55444433322211o.",
    "o5544443333222110o",
    "o4444333322221100o",
    "oooooooooooooooooo",
    "..................",
]
PAL_PESA = {'o': ROCA[0], '0': ROCA[0], '1': ROCA[1], '2': ROCA[2], '3': ROCA[3], '4': ROCA[4], '5': ROCA[5],
            '6': ROCA[6], 'A': AMBAR[4], 'a': AMBAR[2], 'y': AMBAR[6]}
pe = pintar(lienzo(18), PESA, PAL_PESA)
pe.save(os.path.join(EFE, 'peso_tierra.png'))

# Bendicion de la tierra: un sol de oro y, delante, una hoja de jade con el nervio de oro
bt = lienzo(18)
p = bt.load()
SC = (12.6, 5.4)


def rayo_sol(px, py):
    dx, dy = px - SC[0], py - SC[1]
    d = math.hypot(dx, dy)
    if not (4.0 < d <= 5.9):
        return False
    ang = math.atan2(dy, dx)
    off = abs(((ang / (TAU / 8)) + 0.5) % 1.0 - 0.5) * (TAU / 8)
    return off * d < 0.75 * (5.9 - d) / 1.9 + 0.35


for y in range(18):
    for x in range(18):
        dx, dy = x + 0.5 - SC[0], y + 0.5 - SC[1]
        d = math.hypot(dx, dy)
        if d <= 3.5:
            p[x, y] = ORO[0] if d > 2.8 else ORO[6] if dx + dy < -1.8 else ORO[5] if dx + dy < 0.6 else ORO[4]
        elif cobertura(rayo_sol, x, y) >= 0.45:
            p[x, y] = ORO[4] if dx + dy < 0 else ORO[3]
hoja_capa = lienzo(18)
q = hoja_capa.load()
S0, S1 = (1.6, 16.4), (10.4, 7.6)                      # el tallo y la punta de la hoja
L = math.hypot(S1[0] - S0[0], S1[1] - S0[1])
ux, uy = (S1[0] - S0[0]) / L, (S1[1] - S0[1]) / L
vx, vy = -uy, ux                                      # hacia abajo a la derecha


def en_hoja(px, py):
    a = ((px - S0[0]) * ux + (py - S0[1]) * uy) / L
    b = (px - S0[0]) * vx + (py - S0[1]) * vy
    if not (0.0 <= a <= 1.0):
        return False
    return abs(b) <= 3.7 * math.sin(math.pi * a ** 0.8) ** 0.9


for y in range(18):
    for x in range(18):
        if cobertura(en_hoja, x, y) < 0.5:
            continue
        px, py = x + 0.5, y + 0.5
        a = ((px - S0[0]) * ux + (py - S0[1]) * uy) / L
        b = (px - S0[0]) * vx + (py - S0[1]) * vy
        w = 3.7 * math.sin(math.pi * a ** 0.8) ** 0.9
        if abs(b) < 0.6 and a < 0.88:
            q[x, y] = ORO[5] if a < 0.5 else ORO[4]                # el nervio de oro
        elif b < 0:
            q[x, y] = JADE[8] if abs(b) < 1.6 else JADE[7]
        else:
            q[x, y] = JADE[6] if abs(b) < 1.6 else JADE[5]
        # las venas: diagonales que salen del nervio
        if 0.6 < abs(b) < w - 0.8 and int((a * L + abs(b) * 0.9) * 0.62) % 2 == 0 and int(a * L + abs(b)) % 3 == 0:
            q[x, y] = JADE[7] if b > 0 else JADE[6]
contorno(hoja_capa, JADE[1])
for (x, y) in ((0, 17), (1, 16)):                      # el tallo
    q[x, y] = ORO[3]
bt.alpha_composite(hoja_capa)
bt.save(os.path.join(EFE, 'bendicion_tierra.png'))

# ======================================================================
#  GUI: la vineta del miedo (256x256): selva oscura, raices y grietas
#  El color va en la textura (el HUD la pinta en blanco).
# ======================================================================
N = 256
K = 2                                                # se dibuja al doble y se reduce
masa = Image.new('L', (N * K, N * K), 0)
d = ImageDraw.Draw(masa)
for _ in range(110):                                 # follaje: hojas grandes en los bordes
    a = rnd.uniform(0, TAU)
    rr = rnd.uniform(0.86, 1.2) * N / 2 * K
    cx, cy = N / 2 * K + math.cos(a) * rr, N / 2 * K + math.sin(a) * rr
    largo = rnd.uniform(30, 70) * K
    ancho = largo * rnd.uniform(0.28, 0.4)
    giro = a + math.pi + rnd.uniform(-0.6, 0.6)      # apuntan hacia dentro
    pts = []
    for i in range(14):
        t = i / 13
        pts.append((t * largo, ancho * math.sin(math.pi * t) * 0.5))
    for i in range(13, -1, -1):
        t = i / 13
        pts.append((t * largo, -ancho * math.sin(math.pi * t) * 0.5))
    poly = [(cx + px * math.cos(giro) - py * math.sin(giro), cy + px * math.sin(giro) + py * math.cos(giro)) for px, py in pts]
    d.polygon(poly, fill=rnd.randint(150, 255))
masa = masa.filter(ImageFilter.GaussianBlur(3 * K)).resize((N, N), Image.LANCZOS)

raices = Image.new('L', (N * K, N * K), 0)
brillo = Image.new('L', (N * K, N * K), 0)
dr = ImageDraw.Draw(raices)
db = ImageDraw.Draw(brillo)


def raiz(x, y, ang, largo, grosor, prof, encendida):
    while largo > 0 and grosor > 0.6:
        paso = rnd.uniform(5, 9) * K
        ang += rnd.uniform(-0.35, 0.35)
        nx, ny = x + paso * math.cos(ang), y + paso * math.sin(ang)
        dr.line((x, y, nx, ny), fill=255, width=max(1, int(grosor * K)))
        if encendida and grosor < 3.2:
            db.line((x, y, nx, ny), fill=255, width=max(1, int(grosor * K * 0.45)))
        x, y = nx, ny
        largo -= paso
        grosor *= 0.93
        if prof < 3 and rnd.random() < 0.18:
            raiz(x, y, ang + rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.9), largo * 0.6, grosor * 0.7, prof + 1, encendida)


for i in range(16):
    a = i / 16 * TAU + rnd.uniform(-0.1, 0.1)
    # nacen fuera del borde y entran hacia el centro, sin llegar a taparlo
    rr = 0.98 * N / 2 * K * math.sqrt(2)
    x0 = max(-4, min(N * K + 4, N / 2 * K + math.cos(a) * rr))
    y0 = max(-4, min(N * K + 4, N / 2 * K + math.sin(a) * rr))
    hacia = math.atan2(N / 2 * K - y0, N / 2 * K - x0) + rnd.uniform(-0.35, 0.35)
    borde = math.hypot(x0 - N / 2 * K, y0 - N / 2 * K) / K
    raiz(x0, y0, hacia, (borde - rnd.uniform(104, 118)) * K, rnd.uniform(3.5, 5.0), 0, i % 4 == 0)
raices = raices.resize((N, N), Image.LANCZOS)
brillo = brillo.filter(ImageFilter.GaussianBlur(1.0 * K)).resize((N, N), Image.LANCZOS)
halo = brillo.filter(ImageFilter.GaussianBlur(4))

mi = lienzo(N)
p = mi.load()
OSCURO = (4, 14, 8)
for y in range(N):
    for x in range(N):
        rr = math.hypot(x - 127.5, y - 127.5) / 128
        a = max(0.0, min(1.0, (rr - 0.62) / 0.5)) ** 1.8
        a = max(a, masa.getpixel((x, y)) / 255 * max(0.0, rr - 0.6) * 1.9)
        a = max(a, raices.getpixel((x, y)) / 255 * 0.8 * min(1.0, max(0.0, rr - 0.5) * 3))
        b = brillo.getpixel((x, y)) / 255
        h = halo.getpixel((x, y)) / 255
        col = OSCURO
        if b > 0.05 or h > 0.05:
            # la grieta encendida: verde maldito por dentro de la raiz
            t = min(1.0, b * 1.3)
            col = tuple(int(OSCURO[i] + (VERDE[i] * 0.75 - OSCURO[i]) * t) for i in range(3))
            if h > 0.05 and b < 0.05:
                col = tuple(int(OSCURO[i] + (JADE[5][i] - OSCURO[i]) * min(1.0, h * 1.5)) for i in range(3))
                a = max(a, min(0.7, h * 0.9))
            else:
                a = max(a, t)
        p[x, y] = col + (int(255 * min(1.0, a)),)
mi.save(os.path.join(GUI, 'miedo_rajang.png'))

# ======================================================================
#  VISTA PREVIA
# ======================================================================
if len(sys.argv) > 2:
    grupos = ['rajang_polvo', 'rajang_roca', 'rajang_jade', 'rajang_chispa', 'rajang_hoja', 'rajang_runa',
              'rajang_llama', 'rajang_oro', 'rajang_grieta', 'rajang_aviso', 'rajang_lastre', 'rajang_onda',
              'rajang_sello', 'rajang_marca']
    filas = []
    for g in grupos:
        lista = json.load(open(os.path.join(DEF, g + '.json')))['textures']
        filas.append([Image.open(os.path.join(PAR, t.split(':')[1] + '.png')).convert('RGBA') for t in lista])
    ancho = 1600
    prev = Image.new('RGBA', (ancho, 3000), (46, 52, 44, 255))
    y = 10
    x = 10
    alto_fila = 0
    for g, fr in zip(grupos, filas):
        k = 12 if fr[0].width <= 8 else 6 if fr[0].width <= 32 else 3
        alto = fr[0].height * k
        bloque = len(fr) * (fr[0].width * k + 6) + 20
        if x + bloque > ancho:
            x = 10
            y += alto_fila + 12
            alto_fila = 0
        for im in fr:
            # medio fondo oscuro, medio de tierra, para juzgar el contraste
            fondo = Image.new('RGBA', (im.width * k, alto), (46, 52, 44, 255))
            ImageDraw.Draw(fondo).rectangle((0, alto // 2, im.width * k, alto), fill=(120, 104, 80, 255))
            fondo.alpha_composite(im.resize((im.width * k, alto), Image.NEAREST))
            if x + im.width * k > ancho:
                x = 10
                y += alto_fila + 12
                alto_fila = 0
            prev.alpha_composite(fondo, (x, y))
            x += im.width * k + 6
            alto_fila = max(alto_fila, alto)
        x += 20
    y += alto_fila + 16
    x = 10
    for f in (os.path.join(ITEM, 'colmillo_jade.png'), os.path.join(EFE, 'peso_tierra.png'),
              os.path.join(EFE, 'bendicion_tierra.png')):
        im = Image.open(f).convert('RGBA')
        k = 12
        fondo = Image.new('RGBA', (im.width * k, im.height * k), (139, 139, 139, 255))
        fondo.alpha_composite(im.resize((im.width * k, im.height * k), Image.NEAREST))
        prev.alpha_composite(fondo, (x, y))
        prev.alpha_composite(im, (x, y + im.height * k + 6))
        prev.alpha_composite(im.resize((im.width * 2, im.height * 2), Image.NEAREST), (x + 24, y + im.height * k + 6))
        x += im.width * k + 12
    fondo = Image.new('RGBA', (256, 256), (150, 170, 130, 255))
    fondo.alpha_composite(Image.open(os.path.join(GUI, 'miedo_rajang.png')))
    prev.alpha_composite(fondo, (x, y))
    y += 270
    prev = prev.crop((0, 0, ancho, y))
    prev.save(sys.argv[2])
    print(sum(len(f) for f in filas), 'texturas de particula')

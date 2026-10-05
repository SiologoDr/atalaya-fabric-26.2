"""
La barra de jefe de Nerea, pintada aqui pixel a pixel (nada de la de vanilla):

  nerea_barra_marco.png       el marco: prismarina vieja con coral y el hueco
                              redondo del emblema a la izquierda (208x26)
  nerea_barra_agua.png        el relleno: agua con crestas, en grises para
                              tenirlo con el color de cada fase (64x8, en bucle)
  nerea_barra_corazon_N.png   el emblema: el corazon de cada fase, cada vez mas
                              rajado y apagado, y el liberado (16x16)
  nerea_barra_eslabon_*.png   las muescas de fase: un eslabon entero o partido
  nerea_barra_nombre.png      "NEREA" en letras de pixel (nada de la fuente de Minecraft)
  nerea_barra_fase_N.png      "FASE I".."FASE IV" y nerea_barra_libre.png, en grises
                              para tenirlos con el color de la fase
  mob_effect/corriente_abismal.png   el icono del efecto Corriente Abismal

Uso: python nerea_hud.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image
import math, os, sys, random

RAIZ = sys.argv[1]
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')
os.makedirs(GUI, exist_ok=True)
rnd = random.Random(8)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


PRIS = [hexc(c) for c in ('0b1f21', '173b3c', '22504d', '2f6660', '3f7f76', '5aa596', '8fd0bd')]
HUESO = [hexc(c) for c in ('5c5545', '8a8068', 'b3a98c', 'd3c9aa', 'ece4c8')]
CORAL = [hexc(c) for c in ('7a1636', 'a8204a', 'd8336a', 'f2618f')]
OXIDO = [hexc(c) for c in ('2a1a12', '4a2a18', '6e3c1e', '9a5726', 'c47a3a')]

# --------------------------------------------------------------- marco
# Compacto, para no tapar la vista: 208x26 con el emblema redondo a la izquierda.
W, H = 208, 26
BX0, BX1, BY0, BY1 = 28, 199, 9, 16           # hueco de la barra (lo que se rellena), 172x8
EC, ER = 13.0, 12.6                           # emblema: centro (en el borde entre pixeles) y radio
m = Image.new('RGBA', (W, H), (0, 0, 0, 0))
p = m.load()
for y in range(H):
    for x in range(W):
        dentro_barra = BX0 - 3 <= x <= BX1 + 3 and BY0 - 3 <= y <= BY1 + 3
        d = math.hypot(x + 0.5 - EC, y + 0.5 - EC)
        if dentro_barra or d <= ER:
            borde = (x in (BX0 - 3, BX1 + 3) or y in (BY0 - 3, BY1 + 3)) and dentro_barra and d > ER - 1
            if d <= ER and d > ER - 1.2:
                p[x, y] = PRIS[0]
            elif d <= ER - 1.2 and d > ER - 3.0:
                k = 5 if (y + 0.5 < EC - 3) else 3 if y + 0.5 < EC + 3 else 2
                p[x, y] = PRIS[k] if rnd.random() > 0.15 else PRIS[k - 1]
            elif d <= ER - 3.0:
                p[x, y] = hexc('061214')
            elif borde:
                p[x, y] = PRIS[0]
            elif BX0 <= x <= BX1 and BY0 <= y <= BY1:
                p[x, y] = hexc('050e12')                       # el fondo del hueco
            else:
                k = 5 if y < BY0 - 1 else 2 if y > BY1 + 1 else 3
                p[x, y] = PRIS[k] if rnd.random() > 0.18 else PRIS[k - 1]
# remaches de hueso a lo largo del borde
for x in range(BX0 + 10, BX1 - 4, 22):
    for dx in (0, 1):
        p[x + dx, BY0 - 2] = HUESO[3] if dx == 0 else HUESO[1]
        p[x + dx, BY1 + 2] = HUESO[2] if dx == 0 else HUESO[0]
# coral creciendo sobre el marco: dos matas arriba (la derecha queda libre
# para el rotulo de la fase); abajo nada, que ahi va el nombre
for cx, alto_, sube in ((96, 5, True), (118, 4, True)):
    y0 = BY0 - 3 if sube else BY1 + 3
    for k in range(alto_):
        yy = y0 - k if sube else y0 + k
        for (dx, rama) in ((0, 0), (-1 - k // 3, 1), (1 + k // 2, 2)):
            if rama and k < 2:
                continue
            xx = cx + dx
            if 0 <= yy < H:
                p[xx, yy] = CORAL[min(3, 1 + k * 3 // alto_)]
# la punta derecha: un garfio de hueso, como el gancho del arpon
for k in range(7):
    p[BX1 + 4 + k // 2, BY0 - 3 + k] = HUESO[3]
    p[BX1 + 4 + k // 2, BY1 + 3 - k] = HUESO[2]
m.save(os.path.join(GUI, 'nerea_barra_marco.png'))

# --------------------------------------------------------------- agua (relleno)
aw, ah = 64, 8
a = Image.new('RGBA', (aw, ah), (0, 0, 0, 0))
p = a.load()
for y in range(ah):
    for x in range(aw):
        cresta = 1.6 + 0.9 * math.sin(x / aw * math.tau * 2) + 0.4 * math.sin(x / aw * math.tau * 5 + 1)
        t = y / (ah - 1)
        v = 235 - 120 * t
        if abs(y - cresta) < 0.7:
            v = 255                                           # la cresta de la ola
        elif y < cresta:
            v = 200                                           # espuma por encima
        if (x * 7 + y * 13) % 29 == 0 and y > 3:
            v = min(255, v + 40)                              # burbujitas
        p[x, y] = (int(v), int(v), int(v), 255)
a.save(os.path.join(GUI, 'nerea_barra_agua.png'))

# --------------------------------------------------------------- corazones del emblema
# 16x16, simetrico y centrado: la curva del corazon muestreada en el centro de
# cada pixel, asi que el dibujo queda en medio del circulo sin descuadrarse.
S = 16
COLORES = {1: ('ffd0e0', 'e0144c'), 2: ('eaa6c6', 'b0124a'), 3: ('bb7aa0', '7a0e44'), 4: ('7c4a6a', '3e0828'),
           'libre': ('f0fffa', '35e0b0')}
GRIETAS = {1: 0, 2: 2, 3: 4, 4: 7, 'libre': 0}
ESCALA = 6.1                                   # pixeles por unidad: ~14 de ancho
forma = set()
for j in range(S):
    for i in range(S):
        x = (i + 0.5 - S / 2) / ESCALA
        y = -(j + 0.5 - S / 2) / ESCALA + 0.12
        if (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0:
            forma.add((i, j))
borde_c = {(i, j) for (i, j) in forma
           if any((i + di, j + dj) not in forma for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
for clave, (c1, c2) in COLORES.items():
    r = random.Random(str(clave))
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    q = im.load()
    a1, b1 = hexc(c1), hexc(c2)
    for (i, j) in forma:
        if (i, j) in borde_c:
            q[i, j] = (30, 6, 18, 255)
        else:
            d = min(1.0, math.hypot(i - 5, j - 4.5) / 8)
            q[i, j] = tuple(int(a1[k] + (b1[k] - a1[k]) * d) for k in range(3)) + (255,)
    for (i, j) in ((4, 4), (5, 4), (4, 5)):          # el brillo del lobulo izquierdo
        if (i, j) in forma and (i, j) not in borde_c:
            q[i, j] = tuple(min(255, int(v * 0.5 + 255 * 0.5)) for v in q[i, j][:3]) + (255,)
    for _ in range(GRIETAS[clave]):
        x, y = r.randrange(4, 12), r.randrange(4, 11)
        for _ in range(r.randint(2, 4)):
            if (x, y) in forma and (x, y) not in borde_c:
                q[x, y] = (24, 4, 12, 255)
            x += r.choice((-1, 0, 1))
            y += r.choice((-1, 1))
    im.save(os.path.join(GUI, f'nerea_barra_corazon_{clave}.png'))


# --------------------------------------------------------------- eslabones de las muescas
def eslabon(roto):
    im = Image.new('RGBA', (6, 12), (0, 0, 0, 0))
    q = im.load()
    for y in range(12):
        for x in range(6):
            d = math.hypot((x + 0.5 - 3) / 3, (y + 0.5 - 6) / 6)
            if 0.5 <= d <= 1.0:
                if roto and 4 <= y <= 7:
                    continue                                   # partido por la mitad
                q[x, y] = OXIDO[4] if x < 2 and y < 5 else OXIDO[3] if d < 0.78 else OXIDO[1]
    return im


eslabon(False).save(os.path.join(GUI, 'nerea_barra_eslabon.png'))
eslabon(True).save(os.path.join(GUI, 'nerea_barra_eslabon_roto.png'))

# --------------------------------------------------------------- letras en pixel
# Nada de la fuente de Minecraft: el nombre y la fase van dibujados a mano,
# letras gruesas de 6x7 con borde oscuro y sombra, como talladas en hueso.
GLIFOS = {
    'N': ["##..##", "###.##", "######", "##.###", "##..##", "##..##", "##..##"],
    'E': ["######", "##....", "##....", "#####.", "##....", "##....", "######"],
    'R': ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    'A': [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    'F': ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    'S': [".#####", "##....", "##....", ".####.", "....##", "....##", "#####."],
    'I': ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    'V': ["##..##", "##..##", "##..##", "##..##", ".####.", ".####.", "..##.."],
    'L': ["##....", "##....", "##....", "##....", "##....", "##....", "######"],
    'B': ["#####.", "##..##", "##..##", "#####.", "##..##", "##..##", "#####."],
    ' ': ["..", "..", "..", "..", "..", "..", ".."],
}


def palabra(texto, relleno, borde, sombra, ancho=None, derecha=False):
    """La palabra con borde de 1 px alrededor y sombra 1 px abajo. 'relleno(fila)'
    da el color de cada fila (degradado). Si se da 'ancho', el lienzo es fijo y
    el texto va pegado a la izquierda o a la derecha."""
    puntos = set()
    x = 0
    for ch in texto:
        g = GLIFOS[ch]
        for fy, fila in enumerate(g):
            for fx, c in enumerate(fila):
                if c == '#':
                    puntos.add((x + fx, fy))
        x += len(g[0]) + 1
    w_txt = x - 1 + 2
    w = ancho or w_txt
    h = 7 + 3
    ox = (w - w_txt if derecha else 0) + 1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    q = im.load()
    for (px, py) in puntos:                                  # sombra
        for dx, dy in ((0, 2), (1, 2), (-1, 2)):
            xx, yy = px + ox + dx, py + 1 + dy
            if 0 <= xx < w and 0 <= yy < h:
                q[xx, yy] = sombra
    for (px, py) in puntos:                                  # borde
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = px + ox + dx, py + 1 + dy
                if 0 <= xx < w and 0 <= yy < h and (px + dx, py + dy) not in puntos:
                    q[xx, yy] = borde
    for (px, py) in puntos:                                  # relleno
        q[px + ox, py + 1] = relleno(py)
    return im


def nacar(fila):
    """Nacar a espuma de arriba abajo: el nombre de Nerea."""
    rampa = ['f4fbf6', 'e6f6ef', 'd2efe6', 'bfe6dc', 'a6d9cf', '8ccabf', '74b8ad']
    return hexc(rampa[fila])


def gris(fila):
    """En grises, para tenirlo con el color de la fase desde el HUD."""
    v = [255, 246, 236, 224, 210, 196, 182][fila]
    return (v, v, v, 255)


BORDE = hexc('061214')
SOMBRA = (0, 0, 0, 110)
palabra('NEREA', nacar, BORDE, SOMBRA).save(os.path.join(GUI, 'nerea_barra_nombre.png'))
ANCHO_FASE = 64
for n, romano in ((1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV')):
    palabra('FASE ' + romano, gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, f'nerea_barra_fase_{n}.png'))
palabra('LIBRE', gris, BORDE, SOMBRA, ANCHO_FASE, True).save(os.path.join(GUI, 'nerea_barra_libre.png'))
print('nombre', Image.open(os.path.join(GUI, 'nerea_barra_nombre.png')).size, 'fase', (ANCHO_FASE, 10))

# --------------------------------------------------------------- icono de la Corriente Abismal (efecto, 18x18)
# Un remolino de agua oscura que tira hacia abajo, con su cresta de espuma y
# las burbujas que suben: la corriente de fondo que te frena.
EFE = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/mob_effect')
os.makedirs(EFE, exist_ok=True)
ABISMO = [hexc(c) for c in ('081a2e', '0f2f4f', '1b4f7a', '2f78a6', '5aa8cf', 'a6e0f0', 'f0fbff')]
ic = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
q = ic.load()
for y in range(18):
    for x in range(18):
        dx, dy = x + 0.5 - 9, y + 0.5 - 9.5
        r = math.hypot(dx, dy)
        if r > 8.2:
            continue
        ang = math.atan2(dy, dx)
        # espiral logaritmica de dos brazos que se cierra hacia el centro
        brazo = (ang - 1.9 * math.log(max(r, 0.6))) % math.pi
        if r < 1.6:
            q[x, y] = ABISMO[0]
        elif brazo < 0.95:
            k = min(6, 2 + int((8.2 - r) / 2.2) + (1 if brazo < 0.35 else 0))
            q[x, y] = ABISMO[k]
        elif r > 7.2:
            q[x, y] = ABISMO[1]
        else:
            q[x, y] = ABISMO[1] if brazo < 1.6 else ABISMO[0]
for (bx, by) in ((14, 3), (15, 1), (3, 2)):                 # burbujas
    q[bx, by] = ABISMO[6]
ic.save(os.path.join(EFE, 'corriente_abismal.png'))

if len(sys.argv) > 2:
    prev = Image.new('RGBA', (208 * 4, 26 * 4 + 90), (30, 40, 46, 255))
    marco = Image.open(os.path.join(GUI, 'nerea_barra_marco.png'))
    prev.alpha_composite(marco.resize((832, 104), Image.NEAREST), (0, 0))
    x = 4
    for clave in (1, 2, 3, 4, 'libre'):
        im = Image.open(os.path.join(GUI, f'nerea_barra_corazon_{clave}.png')).resize((64, 64), Image.NEAREST)
        prev.alpha_composite(im, (x, 112))
        x += 80
    agua = Image.open(os.path.join(GUI, 'nerea_barra_agua.png')).resize((192, 24), Image.NEAREST)
    prev.alpha_composite(agua, (x + 10, 130))
    prev.save(sys.argv[2])
    print('ok')

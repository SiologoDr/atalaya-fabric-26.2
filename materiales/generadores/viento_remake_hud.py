"""
La barra de Aeralis del remake (propuesta), pixel a pixel, junto a la de hoy
montada igual que la monta AeralisBarraHud. Solo vista previa: no escribe nada
en el repo.

  - El emblema: el ojo de la tormenta con la corona de puas del remake y su aro.
  - Dos alas que salen del emblema por encima del marco, con su filo encendido.
  - El marco de nube de tormenta, mas alto, y el relleno con el color dentro de
    la imagen (de la tormenta oscura al filo claro) y un frente que brilla.
  - Las muescas de fase son ojos de tormenta: enteros, o apagados al pasarlos.
  - Durante el Juicio del Ciclon, cuatro cristales bajo la barra: los nucleos
    que quedan en pie.

Uso: python viento_remake_hud.py <raiz del proyecto> <salida.png>
"""
import math, os, sys
from PIL import Image

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
GUI = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui')


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


COLOR_FASE = ['5fd2ff', '7f8cff', 'b07cff', 'ff4fd8']
ORO = 'ffc23a'


def cargar(n, vieja=False):
    """Una pieza de la barra; las de la antigua (vieja), del commit de antes del remake."""
    ruta = os.path.join(GUI, n)
    if not vieja and os.path.exists(ruta):
        return Image.open(ruta).convert('RGBA')
    import io, subprocess
    datos = subprocess.run(['git', '-C', RAIZ, 'show', '132056c:src/main/resources/assets/atalaya/textures/gui/' + n],
                           capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(datos)).convert('RGBA')


def tenir(im, color):
    r, g, b, _ = hexc(color)
    out = im.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            a, bb, c, al = px[x, y]
            px[x, y] = (a * r // 255, bb * g // 255, c * b // 255, al)
    return out


# ----------------------------------------------------------------------
#  La de hoy, como la monta AeralisBarraHud
# ----------------------------------------------------------------------
def antes(fase, vida, libre=False):
    W, H = 208, 26
    im = Image.new('RGBA', (W, H + 12), (0, 0, 0, 0))
    oy = 12
    im.alpha_composite(cargar('aeralis_barra_marco.png', True), (0, oy))
    color = ORO if libre else COLOR_FASE[fase - 1]
    viento = tenir(cargar('aeralis_barra_viento.png', True), color)
    lleno = round(172 * vida)
    x = 0
    while x < lleno:
        w = min(64, lleno - x)
        im.alpha_composite(viento.crop((0, 0, w, 8)), (28 + x, oy + 9))
        x += w
    for corte in (0.75, 0.5, 0.25):
        pl = cargar('aeralis_barra_pluma_rota.png' if vida < corte else 'aeralis_barra_pluma.png', True)
        im.alpha_composite(pl, (28 + round(172 * corte) - 3, oy + 7))
    nuc = cargar('aeralis_barra_nucleo_libre.png' if libre else f'aeralis_barra_nucleo_{fase}.png', True)
    im.alpha_composite(nuc, (13 - 8, oy + 13 - 8))
    im.alpha_composite(cargar('aeralis_barra_nombre.png', True), (28, oy + 7 - 10))
    rot = tenir(cargar('aeralis_barra_libre.png' if libre else f'aeralis_barra_fase_{fase}.png', True), color)
    im.alpha_composite(rot, (28 + 172 - 64 + 1, oy + 7 - 10))
    return im


# ----------------------------------------------------------------------
#  La nueva
# ----------------------------------------------------------------------
NW, NH = 240, 44
HX0, HX1, HY0, HY1 = 40, 230, 22, 31          # el hueco del relleno
EC = (19, 26)                                  # el centro del emblema
ER = 15.5


def rampa_fase(fase, libre=False):
    if libre:
        return [hexc(c) for c in ('5a3a10', '9a6a1a', 'd6a032', 'ffc23a', 'ffe9a8', 'fffbe0')]
    return [hexc(c) for c in (
        ('10283c', '1d4f74', '2f86b8', '5fd2ff', 'a8ecff', 'f2ffff'),
        ('141838', '242c70', '3e4cb0', '7f8cff', 'bcc4ff', 'eef0ff'),
        ('1c1238', '3a2470', '6c48b8', 'b07cff', 'dcc0ff', 'fff7d6'),
        ('2a0a26', '5c1452', 'a42c8c', 'ff4fd8', 'ffb0ee', 'ffffff'),
    )[fase - 1]]


NUBE = [hexc(c) for c in ('0e121c', '1c2232', '323c52', '56627c', '8592ac', 'c8d2e2')]


def nueva(fase, vida, juicio=None, libre=False):
    R = rampa_fase(fase, libre)
    im = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
    px = im.load()

    def pon(x, y, c):
        if 0 <= x < NW and 0 <= y < NH:
            px[x, y] = c

    # --- las alas, detras de todo: una grande sobre el marco y otra pequena tras el emblema
    def dentro(poly, x, y):
        c = False
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1:
                c = not c
        return c

    def ala(poly, ocelo, raiz):
        pts = {(x, y) for y in range(NH) for x in range(NW) if dentro(poly, x + 0.5, y + 0.5)}
        largo = max(math.hypot(x - raiz[0], y - raiz[1]) for x, y in pts)
        for (x, y) in pts:
            vec = sum((x + dx, y + dy) in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            arriba = (x, y - 1) not in pts
            d = math.hypot(x - raiz[0], y - raiz[1]) / largo
            if arriba:
                pon(x, y, NUBE[0])                     # la costa
            elif vec < 4:
                pon(x, y, R[4])                        # el filo encendido
            else:
                c = NUBE[1] if d < 0.3 else R[1] if d < 0.55 else R[2] if d < 0.8 else R[3]
                if (x * 2 + y * 3) % 9 == 0 and d > 0.4:
                    c = R[4]                           # vetas de viento
                pon(x, y, (*c[:3], 240))
        ox, oy, orad = ocelo
        for dy in range(-orad, orad + 1):
            for dx in range(-orad, orad + 1):
                dd = math.hypot(dx, dy)
                if dd <= orad + 0.4 and (ox + dx, oy + dy) in pts:
                    pon(ox + dx, oy + dy, R[5] if dd < orad * 0.4 else R[3] if dd < orad * 0.75 else NUBE[0])

    ala([(30, 21), (38, 13), (52, 6), (70, 2), (88, 1), (92, 4), (88, 10), (80, 15), (66, 19), (48, 22)], (70, 9, 3), (30, 21))
    ala([(10, 16), (6, 10), (1, 6), (0, 9), (2, 15), (6, 19)], (4, 11, 1), (10, 16))

    # --- el marco: nube de tormenta, el canto de arriba claro
    for y in range(HY0 - 3, HY1 + 3):
        for x in range(HX0 - 8, HX1 + 3):
            if HX0 <= x < HX1 and HY0 <= y < HY1:
                continue
            borde = y in (HY0 - 3, HY1 + 2) or x in (HX0 - 8, HX1 + 2)
            if borde:
                pon(x, y, NUBE[0])
            elif y == HY0 - 2:
                pon(x, y, NUBE[4])
            elif y == HY1 + 1:
                pon(x, y, NUBE[1])
            else:
                pon(x, y, NUBE[2] if (x + y) % 5 else NUBE[3])
    # el hueco vacio
    for y in range(HY0, HY1):
        for x in range(HX0, HX1):
            pon(x, y, (*NUBE[0][:3], 255))
    # --- el relleno: la tormenta oscura abajo, el color, el filo claro arriba; vetas de viento y el frente
    lleno = round((HX1 - HX0) * vida)
    for x in range(lleno):
        for y in range(HY0, HY1):
            fila = y - HY0
            c = R[[4, 3, 3, 2, 2, 2, 1, 1, 0][min(8, fila)]]
            if (x * 3 + fila * 7) % 23 < 4 and 1 <= fila <= 6:
                c = R[4]
            if x >= lleno - 2:
                c = R[5]
            pon(HX0 + x, y, c)
    # --- las muescas: ojos de tormenta, apagados al pasarlos
    for corte in (0.75, 0.5, 0.25):
        ex = HX0 + round((HX1 - HX0) * corte)
        pasado = vida < corte
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if abs(dx) + abs(dy) <= 3:
                    d = abs(dx) + abs(dy)
                    if pasado:
                        c = NUBE[1] if d < 3 else NUBE[0]
                    else:
                        c = R[5] if d == 0 else R[3] if d == 1 else NUBE[3] if d == 2 else NUBE[0]
                    pon(ex + dx, HY1 + 1 + dy, c)
    # --- el emblema: aro, ojo de tormenta en espiral y la corona de puas
    for k in range(5):
        ang = math.radians(-90 + (k - 2) * 28)
        for q in range(4):
            x = round(EC[0] + math.cos(ang) * (ER + q))
            y = round(EC[1] + math.sin(ang) * (ER + q))
            pon(x, y, R[4] if q == 3 else NUBE[1])
            pon(x + 1, y, NUBE[0] if q < 3 else R[3])
    for y in range(NH):
        for x in range(40):
            d = math.hypot(x + 0.5 - EC[0], y + 0.5 - EC[1])
            if d <= ER:
                if d > ER - 1.2:
                    pon(x, y, NUBE[0])
                elif d > ER - 2.6:
                    pon(x, y, R[4])
                elif d > ER - 3.6:
                    pon(x, y, NUBE[1])
                else:
                    a = math.atan2(y + 0.5 - EC[1], x + 0.5 - EC[0])
                    brazo = (a - 2.6 * math.log(max(d, 0.5) / (ER - 3.6))) % (2 * math.pi / 3) < 0.95
                    c = R[5] if d < 2.2 else (R[3] if d < 6 else R[2]) if brazo else NUBE[0]
                    pon(x, y, c)
    # --- el Juicio: cuatro cristales bajo la barra
    if juicio is not None:
        for i in range(4):
            cx, cy = HX0 + 70 + i * 16, HY1 + 8
            roto = i >= juicio
            for dy in range(-4, 5):
                semi = 2 - abs(dy) // 2
                for dx in range(-semi, semi + 1):
                    borde = abs(dx) == semi or abs(dy) == 4
                    c = (NUBE[2] if not borde else NUBE[0]) if roto else (R[5] if dx == 0 and dy < 0 else R[3] if not borde else R[1])
                    pon(cx + dx, cy + dy, c)
    # --- los rotulos (las letras de hoy), arriba a la derecha
    im.alpha_composite(cargar('aeralis_barra_nombre.png'), (100, 9))
    rot = tenir(cargar('aeralis_barra_libre.png' if libre else f'aeralis_barra_fase_{fase}.png'), ORO if libre else COLOR_FASE[fase - 1])
    im.alpha_composite(rot, (HX1 - 64 + 1, 8))
    return im


# ----------------------------------------------------------------------
#  La hoja: hoy arriba, el remake abajo, a x3 sobre un cielo de tormenta
# ----------------------------------------------------------------------
K = 3
filas = [('HOY', [antes(f, v) for f, v in ((1, 0.92), (2, 0.66), (3, 0.41), (4, 0.18))] + [antes(4, 0.0, libre=True)]),
         ('REMAKE', [nueva(f, v) for f, v in ((1, 0.92), (2, 0.66), (3, 0.41), (4, 0.18))] + [nueva(4, 0.0, libre=True)]),
         ('REMAKE · JUICIO DEL CICLON (QUEDAN 2 NUCLEOS)', [nueva(3, 0.41, juicio=2), nueva(4, 0.12, juicio=3)])]
ancho = max(sum(b.width * K + 30 for b in bs) for _, bs in filas) + 30
alto = sum(max(b.height for b in bs) * K + 60 for _, bs in filas) + 20
hoja = Image.new('RGBA', (ancho, alto), (0, 0, 0, 255))
pxh = hoja.load()
for y in range(alto):
    t = y / alto
    c = (int(18 + 40 * t), int(26 + 50 * t), int(44 + 70 * t), 255)
    for x in range(ancho):
        pxh[x, y] = c
from PIL import ImageDraw, ImageFont
d = ImageDraw.Draw(hoja)
f = ImageFont.truetype('C:/Windows/Fonts/Oswald-Bold.ttf', 22)
y = 16
for titulo, bs in filas:
    d.text((30, y), titulo, font=f, fill=(220, 232, 250))
    y += 34
    x = 30
    for b in bs:
        g = b.resize((b.width * K, b.height * K), Image.NEAREST)
        hoja.alpha_composite(g, (x, y))
        x += g.width + 30
    y += max(b.height for b in bs) * K + 26
hoja.convert('RGB').save(SALIDA, quality=95)
print('ok', hoja.size)

"""
Las texturas de los minijuegos de Novilis (octubre de 2026): El Caballero
Manda, la Forja del Juramento, Piedra, Papel o Tijera y Frio o Caliente.
Segunda version (Juan: "mejora los disenos, sorprendeme"): mismas mecanicas,
dibujos nuevos. Con la paleta de la barra y la Egida de Novilis (acero quemado
casi negro, oro en cinco pasos y fuego) y las reglas de DISENO.md: la silueta
como datos (mascaras de formas), contorno calculado (vecindad-4), sombreado por
distancia al borde (punto 18) con luz de arriba a la izquierda, rampas de
cinco tonos con el borde tenido y alguna mota suelta.

  entity/novilis/yunque.png        el yunque (128 x 64): costado de basalto con banda de oro y runas, cara de
                                   acero templado (los colores del temple), cintura, peana con el sol en relieve,
                                   cuerno, la hoja al rojo y la forjada, empunadura, guarda y los tachones
  entity/novilis/forja_suelo.png   las brasas y el hollin del suelo alrededor del yunque (64 x 64)
  entity/novilis/aro_forja.png     el aro de luz: un sol con doce rayos hacia dentro (64 x 64)
  entity/novilis/aro_hoja.png      la mira quieta del tamano de la hoja (32 x 32)
  entity/novilis/destello.png      el destello del golpe: una estrella de ocho puntas (32 x 32)
  entity/novilis/brasa_grieta.png  la grieta de la brasa: un charco de magma y grietas que se ramifican (48 x 48)
  particle/novilis_piedra.png      basalto con vetas de lava (32 x 32)
  particle/novilis_papel.png       pergamino con su sello de cera
  particle/novilis_tijera.png      tijeras forjadas: hojas de acero, pernio de oro y mangos carmesi
  gui/novilis_rps.png              los tres, para la pantalla (96 x 32)
  gui/novilis_rps_casilla.png      la casilla de cada mano (80 x 40): basalto y oro; elegida, con llamas
  gui/novilis_manda.png            el estandarte (240 x 72): vara con remates de sol, damasco carmesi con
                                   pliegues, cenefa de oro, medallon, cartucho para la orden y puntas con borlas
  gui/novilis_manda_cinta.png      la cinta de oro de "¡Por el Sol...!" (112 x 13)
  gui/novilis_ordenes.png          las cuatro ordenes (128 x 32): un caballero de rodillas, uno que salta, el
                                   sol y un ojo que lo mira, y un guantelete en alto
  gui/novilis_termometro.png       el termometro es su espada (128 x 128): el fondo del cristal, el fuego que lo
                                   llena (de frio a ardiendo, de abajo arriba), el frente (filos, guarda, empunadura,
                                   pomo de sol, marcas) y el relleno del pomo (en gris, se tine)

Uso: python novilis_minijuegos.py <raiz del proyecto> [hoja.png]
"""
import math
import os
import random
import sys
from collections import deque

from PIL import Image, ImageDraw

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
ASSETS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')

# --- La paleta de Novilis (la de la barra y la Egida) ---
NEGRO = ((10, 6, 6), (20, 12, 10), (43, 29, 28), (61, 42, 37), (84, 56, 45), (110, 74, 56))
ORO = ((99, 60, 17), (192, 124, 34), (232, 168, 58), (255, 215, 122), (255, 240, 208))
ORO_HONDO = (138, 84, 24)
BRASA = ((92, 22, 6), (184, 74, 12), (255, 138, 30), (255, 192, 112), (255, 240, 208))
CARMESI = ((58, 10, 10), (96, 18, 16), (128, 28, 22), (162, 44, 30), (196, 74, 48))
BASALTO = ((40, 33, 34), (66, 57, 58), (96, 86, 86), (132, 120, 116), (176, 164, 156))
ACERO = ((52, 56, 66), (92, 98, 112), (140, 146, 160), (190, 196, 208), (236, 240, 248))
PERGAMINO = ((112, 70, 34), (176, 128, 72), (222, 184, 124), (242, 216, 166), (255, 244, 214))
CREMA = ((132, 80, 34), (196, 140, 70), (234, 196, 132), (250, 226, 180), (255, 248, 228))
TINTA = (86, 44, 20)
HIELO = ((24, 52, 112), (44, 96, 180), (82, 156, 232), (150, 210, 255), (226, 246, 255))

LUZ = (-1, -1)


# ----------------------------------------------------------------------
#  Herramientas: mascaras, distancia al borde y sombreado
# ----------------------------------------------------------------------

def lienzo(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def pon(im, x, y, c, a=255):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), tuple(c[:3]) + (a,))


def mascara(w, h):
    m = Image.new('L', (w, h), 0)
    return m, ImageDraw.Draw(m)


def solido(m):
    w, h = m.size
    px = m.load()
    return {(x, y) for y in range(h) for x in range(w) if px[x, y] > 0}


def distancias(sol):
    """Pasos hasta el aire mas cercano (vecindad-4): 0 en el borde (DISENO.md, punto 18)."""
    d = {}
    cola = deque()
    for (x, y) in sol:
        if any((x + a, y + b) not in sol for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            d[(x, y)] = 0
            cola.append((x, y))
    while cola:
        x, y = cola.popleft()
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + a, y + b)
            if q in sol and q not in d:
                d[q] = d[(x, y)] + 1
                cola.append(q)
    return d


def sombrear(im, sol, rampa, x0=0, y0=0, luz=LUZ, marcas=None, contorno=True, nucleo=None, alcance=4.0):
    """
    Pinta una silueta: el borde con el tono 0 (tenido), dentro por distancia al
    borde (o a 'nucleo', si se da) y, en el canto que mira a la luz, un paso mas
    claro; en el de sombra, uno mas oscuro.
    """
    marcas = marcas or {}
    d = distancias(sol)
    lx, ly = luz
    for (x, y) in sol:
        if (x, y) in marcas:
            pon(im, x0 + x, y0 + y, marcas[(x, y)])
            continue
        dd = d[(x, y)]
        if dd == 0 and contorno:
            t = 0
        else:
            if nucleo is not None:
                r = math.hypot(x - nucleo[0], y - nucleo[1])
                t = 4 if r < alcance * 0.35 else 3 if r < alcance * 0.7 else 2 if r < alcance * 1.1 else 1
            else:
                t = 1 + min(3, int(dd * 3 / alcance + 0.5))
            if (x + lx, y + ly) not in sol or (x + 2 * lx, y + 2 * ly) not in sol:
                t = min(4, t + 1)
            elif (x - lx, y - ly) not in sol:
                t = max(1, t - 1)
        pon(im, x0 + x, y0 + y, rampa[t])


def motas(im, lista, x0=0, y0=0):
    for (x, y, c) in lista:
        pon(im, x0 + x, y0 + y, c)


def guardar(im, ruta):
    ruta = os.path.join(ASSETS, ruta)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    im.save(ruta)
    print('  ', os.path.relpath(ruta, ASSETS), im.size)
    return im


# ----------------------------------------------------------------------
#  Piedra, papel y tijera (32 x 32)
# ----------------------------------------------------------------------

def piedra(im=None, x0=0, y0=0):
    im = im or lienzo(32, 32)
    m, dib = mascara(32, 32)
    r = random.Random(5)
    vertices = []
    for i in range(14):
        a = 2 * math.pi * i / 14 - math.pi / 2
        rad = 12.5 + r.uniform(-1.6, 1.0)
        if math.sin(a) > 0.55:
            rad *= 0.86          # la base, algo aplastada
        vertices.append((16 + math.cos(a) * rad * 1.05, 17 + math.sin(a) * rad * 0.92))
    dib.polygon(vertices, fill=255)
    sol = solido(m)
    # Las vetas de lava: tres grietas que serpentean, y unos poros encendidos.
    vetas = {}
    for inicio, rumbo in (((9, 11), 0.55), ((22, 9), 2.2), ((13, 24), -0.35)):
        x, y = inicio
        a = rumbo
        for k in range(11):
            a += r.uniform(-0.45, 0.45)
            x += math.cos(a) * 1.1
            y += math.sin(a) * 1.1
            p = (int(round(x)), int(round(y)))
            if p in sol:
                vetas[p] = BRASA[3] if k % 4 == 1 else BRASA[2]
    for p in ((15, 15), (19, 19), (11, 18)):
        if p in sol:
            vetas[p] = BRASA[4]
    # El borde no lleva lava (que no se coma el contorno).
    d = distancias(sol)
    vetas = {p: c for p, c in vetas.items() if d.get(p, 0) > 0}
    sombrear(im, sol, BASALTO, x0, y0, marcas=vetas, alcance=5.0)
    motas(im, [(29, 9, BASALTO[2]), (3, 26, BASALTO[1]), (27, 28, BRASA[2])], x0, y0)
    return im


def papel(im=None, x0=0, y0=0):
    im = im or lienzo(32, 32)
    m, dib = mascara(32, 32)
    dib.rectangle((8, 6, 23, 25), fill=255)
    dib.rounded_rectangle((5, 2, 26, 8), radius=3, fill=255)
    dib.rounded_rectangle((5, 23, 26, 29), radius=3, fill=255)
    sol = solido(m)
    marcas = {}
    # Los rollos, como cilindros: bandas de arriba abajo.
    for y, t in ((3, 4), (4, 3), (5, 2), (6, 1), (7, 1)):
        for x in range(6, 26):
            if (x, y) in sol:
                marcas[(x, y)] = PERGAMINO[t]
    for y, t in ((24, 3), (25, 3), (26, 2), (27, 1), (28, 1)):
        for x in range(6, 26):
            if (x, y) in sol:
                marcas[(x, y)] = PERGAMINO[t]
    # Lo escrito, con tinta sepia, a renglones con huecos.
    for y in (11, 14, 17, 20):
        for x in range(10, 22):
            if (x * 5 + y * 3) % 11 not in (0, 1) and not (y == 20 and x > 15):
                marcas[(x, y)] = TINTA
    # El sello de cera carmesi con el sol de oro.
    for y in range(17, 25):
        for x in range(17, 25):
            dd = math.hypot(x - 20.5, y - 21.5)
            if dd < 3.6:
                marcas[(x, y)] = CARMESI[0] if dd > 2.9 else CARMESI[3] if (x + y) % 3 == 0 else CARMESI[2]
    marcas[(20, 21)] = ORO[3]
    marcas[(21, 22)] = ORO[2]
    marcas[(20, 22)] = ORO[2]
    marcas[(21, 21)] = ORO[4]
    sombrear(im, sol, PERGAMINO, x0, y0, marcas=marcas, alcance=5.0)
    # El sello asoma por fuera del papel: su canto, oscuro.
    for (x, y) in ((24, 20), (24, 21), (24, 22), (24, 23)):
        pon(im, x0 + x, y0 + y, CARMESI[0])
    motas(im, [(28, 12, PERGAMINO[2]), (2, 17, PERGAMINO[1])], x0, y0)
    return im


def tijera(im=None, x0=0, y0=0):
    im = im or lienzo(32, 32)
    # Las hojas: dos cunas de acero que se cruzan en el pernio.
    m, dib = mascara(32, 32)
    dib.polygon([(5, 2), (8, 1), (18, 15), (15, 17)], fill=255)
    dib.polygon([(27, 2), (24, 1), (14, 15), (17, 17)], fill=255)
    hojas = solido(m)
    # Los mangos: dos aros carmesi.
    m2, dib2 = mascara(32, 32)
    for cx in (10, 22):
        dib2.ellipse((cx - 6, 18, cx + 6, 30), fill=255)
        dib2.ellipse((cx - 3, 21, cx + 3, 27), fill=0)
    dib2.polygon([(13, 16), (19, 16), (20, 20), (12, 20)], fill=255)
    mangos = solido(m2) - hojas
    sombrear(im, hojas, ACERO, x0, y0, alcance=2.0)
    sombrear(im, mangos, CARMESI, x0, y0, alcance=2.5)
    # El filo de cada hoja, encendido; y el pernio de oro.
    for k in range(10):
        pon(im, x0 + 7 + k, y0 + 2 + int(k * 1.3), ACERO[4])
        pon(im, x0 + 25 - k, y0 + 2 + int(k * 1.3), ACERO[3])
    for (x, y, c) in ((15, 16, ORO[0]), (16, 16, ORO[0]), (17, 16, ORO[0]), (15, 15, ORO[2]), (16, 15, ORO[4]), (17, 15, ORO[2]),
                      (15, 17, ORO[1]), (16, 17, ORO[3]), (17, 17, ORO[1]), (16, 14, ORO[0])):
        pon(im, x0 + x, y0 + y, c)
    # Un remache de oro en cada aro.
    for cx in (10, 22):
        pon(im, x0 + cx, y0 + 19, ORO[3])
    motas(im, [(2, 8, ACERO[2]), (29, 11, ACERO[1]), (27, 30, CARMESI[2])], x0, y0)
    return im


def casillas():
    """La casilla de cada mano: placa de basalto con filo de oro; la elegida, encendida y con llamas."""
    im = lienzo(80, 40)
    for k, elegida in enumerate((False, True)):
        x0 = k * 40
        m, dib = mascara(40, 40)
        dib.rounded_rectangle((1, 3, 38, 39), radius=4, fill=255)
        sol = solido(m)
        d = distancias(sol)
        for (x, y) in sol:
            dd = d[(x, y)]
            if dd == 0:
                c = ORO[0]
            elif dd == 1:
                c = (ORO[3] if elegida else ORO[2]) if (x + y < 40) else (ORO[2] if elegida else ORO[1])
            elif dd == 2:
                c = ORO_HONDO if not elegida else ORO[1]
            elif dd == 3:
                c = NEGRO[0]
            else:
                # El fondo: basalto quemado, mas claro arriba; la elegida, con un calor rojizo en medio.
                c = NEGRO[2] if y < 14 else NEGRO[1]
                if elegida:
                    r = math.hypot(x - 19.5, y - 22)
                    c = (84, 34, 18) if r < 9 else (61, 26, 18) if r < 14 else c
            pon(im, x0 + x, y, c)
        # Remaches de oro en las esquinas.
        for (x, y) in ((5, 7), (34, 7), (5, 35), (34, 35)):
            pon(im, x0 + x, y, ORO[4] if elegida else ORO[3])
        if elegida:
            # Lenguas de fuego que salen del canto de arriba.
            r = random.Random(9)
            for x in range(4, 37):
                alto = int(2 + 2.5 * (0.5 + 0.5 * math.sin(x * 0.9)) + r.random() * 1.5)
                for k2 in range(alto):
                    y = 3 - k2
                    c = BRASA[4] if k2 == 0 else BRASA[3] if k2 == 1 else BRASA[2]
                    if y >= 0 and (k2 < alto - 1 or x % 2 == 0):
                        pon(im, x0 + x, y, c)
    return im


# ----------------------------------------------------------------------
#  El Caballero Manda: el estandarte, la cinta y las ordenes
# ----------------------------------------------------------------------

ESTANDARTE_W, ESTANDARTE_H = 240, 72
MEDALLON = (40, 35, 18)          # centro x, y y radio
CARTUCHO = (66, 13, 222, 56)     # x0, y0, x1, y1


def estandarte():
    w, h = ESTANDARTE_W, ESTANDARTE_H
    im = lienzo(w, h)
    r = random.Random(3)
    # --- El pano: con las puntas cortadas abajo ---
    m, dib = mascara(w, h)
    dib.rectangle((10, 6, 229, 58), fill=255)
    puntas = 7
    ancho = (229 - 10 + 1) / puntas
    for i in range(puntas):
        a = 10 + i * ancho
        dib.polygon([(a, 58), (a + ancho - 1, 58), (a + ancho / 2, 67)], fill=255)
    pano = solido(m)
    d = distancias(pano)
    for (x, y) in pano:
        dd = d[(x, y)]
        # Los pliegues: bandas que suben y bajan de luz a lo ancho.
        pliegue = math.sin((x - 10) / 34.0 * 2 * math.pi)
        base = 2 if pliegue > 0.35 else 1 if pliegue > -0.45 else 0
        # El damasco: una red de rombos con un punto en cada nudo.
        u, v = (x + y) % 12, (x - y) % 12
        if u == 0 or v == 0:
            base = min(3, base + 1)
        if (x + y) % 12 == 6 and (x - y) % 12 == 6:
            base = 3
        c = CARMESI[base + 1] if base < 4 else CARMESI[4]
        if dd == 0:
            c = ORO[0]
        elif dd in (1, 2, 3) and y < 59:
            # La cenefa de oro: filo, cordon con puntos de sol y filo.
            c = ORO[1] if dd == 1 else (ORO[4] if (x + y) % 4 == 0 else ORO[2]) if dd == 2 else ORO[0]
        elif dd in (1, 2) and y >= 59:
            c = ORO[2] if dd == 1 else CARMESI[1]
        elif dd == 4:
            c = CARMESI[0]
        if r.random() < 0.02 and dd > 4:
            c = CARMESI[4]
        pon(im, x, y, c)
    # --- Las borlas de oro en la punta de cada pico ---
    for i in range(puntas):
        cx = int(10 + i * ancho + ancho / 2)
        for (x, y, c) in ((0, 67, ORO[0]), (-1, 68, ORO[1]), (0, 68, ORO[3]), (1, 68, ORO[1]),
                          (-1, 69, ORO[2]), (0, 69, ORO[2]), (1, 69, ORO[1]), (-1, 70, ORO[1]), (1, 70, ORO[0]), (0, 71, ORO[1])):
            pon(im, cx + x, y, c)
    # --- La vara de oro, con anillas que sujetan el pano y un sol en cada remate ---
    for x in range(6, 234):
        for y, c in ((2, ORO[0]), (3, ORO[3]), (4, ORO[2]), (5, ORO[1]), (6, ORO[0])):
            pon(im, x, y, c)
        if x % 4 == 0:
            pon(im, x, 3, ORO[4])
    for x in range(14, 228, 24):
        for y in (6, 7):
            pon(im, x, y, ORO[1])
            pon(im, x + 1, y, ORO[2])
    for cx in (4, 235):
        for y in range(0, 10):
            for x in range(cx - 5, cx + 6):
                dd = math.hypot(x - cx, y - 4)
                a = math.atan2(y - 4, x - cx)
                if dd < 2.4:
                    pon(im, x, y, ORO[4] if dd < 1.2 else ORO[3])
                elif dd < 3.3:
                    pon(im, x, y, ORO[1])
                elif dd < 5.2 and abs(math.sin(a * 4)) < 0.28:
                    pon(im, x, y, ORO[2])
    # --- El medallon: aro de oro y, dentro, acero quemado con rayos grabados ---
    mx, my, mr = MEDALLON
    for y in range(my - mr - 1, my + mr + 2):
        for x in range(mx - mr - 1, mx + mr + 2):
            dd = math.hypot(x - mx, y - my)
            if dd > mr + 0.5:
                continue
            luz = (x - mx) + (y - my) < 0
            if dd > mr - 0.7:
                c = ORO[0]
            elif dd > mr - 1.8:
                c = ORO[3] if luz else ORO[1]
            elif dd > mr - 2.9:
                c = ORO[2] if luz else ORO_HONDO
            elif dd > mr - 3.6:
                c = NEGRO[0]
            else:
                a = math.atan2(y - my, x - mx)
                c = NEGRO[1] if dd > mr * 0.55 else NEGRO[2]
                if abs(math.sin(a * 6)) < 0.12 and dd > 5:
                    c = NEGRO[3]
            pon(im, x, y, c)
    # --- El cartucho: placa oscura con marco de oro y las esquinas cortadas ---
    x0, y0, x1, y1 = CARTUCHO
    m, dib = mascara(w, h)
    dib.polygon([(x0 + 3, y0), (x1 - 3, y0), (x1, y0 + 3), (x1, y1 - 3), (x1 - 3, y1), (x0 + 3, y1), (x0, y1 - 3), (x0, y0 + 3)],
                fill=255)
    cart = solido(m)
    d = distancias(cart)
    for (x, y) in cart:
        dd = d[(x, y)]
        if dd == 0:
            c = ORO[0]
        elif dd == 1:
            c = ORO[3] if y < (y0 + y1) / 2 else ORO[1]
        elif dd == 2:
            c = ORO_HONDO
        elif dd == 3:
            c = NEGRO[0]
        else:
            k = (y - y0) / (y1 - y0)
            c = NEGRO[2] if k < 0.18 else NEGRO[1] if k < 0.85 else NEGRO[0]
        pon(im, x, y, c)
    # Un rombo de oro en medio de cada lado del cartucho.
    for cx, cy in ((x0, (y0 + y1) // 2), (x1, (y0 + y1) // 2)):
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if abs(dx) + abs(dy) <= 3:
                    pon(im, cx + dx, cy + dy, ORO[0] if abs(dx) + abs(dy) == 3 else ORO[3] if dx + dy < 0 else ORO[2])
    return im


def cinta():
    """La cinta de oro de "¡Por el Sol...!": banda con los cabos doblados en cola de golondrina."""
    w, h = 112, 13
    im = lienzo(w, h)
    m, dib = mascara(w, h)
    dib.rectangle((9, 0, w - 10, 10), fill=255)
    banda = solido(m)
    m2, dib2 = mascara(w, h)
    dib2.polygon([(0, 2), (12, 2), (12, 12), (0, 12), (4, 7)], fill=255)
    dib2.polygon([(w - 1, 2), (w - 13, 2), (w - 13, 12), (w - 1, 12), (w - 5, 7)], fill=255)
    cabos = solido(m2) - banda
    for (x, y) in cabos:
        borde = any((x + a, y + b) not in cabos and (x + a, y + b) not in banda for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        pon(im, x, y, ORO[0] if borde else ORO_HONDO if y > 7 else ORO[1])
    for (x, y) in banda:
        borde = any((x + a, y + b) not in banda for a, b in ((0, 1), (0, -1)))
        c = ORO[0] if borde else (ORO[4], ORO[3], ORO[3], ORO[2], ORO[2], ORO[2], ORO[2], ORO[1], ORO[1], ORO[1], ORO[0])[y]
        if x in (9, w - 10):
            c = ORO[0]
        pon(im, x, y, c)
    return im


def caballero_rodillas():
    m, dib = mascara(32, 32)
    dib.ellipse((10, 2, 18, 10), fill=255)                     # el yelmo
    dib.rectangle((10, 6, 18, 9), fill=255)
    dib.polygon([(9, 10), (19, 10), (20, 19), (10, 20)], fill=255)          # el torso
    dib.polygon([(17, 18), (23, 18), (24, 21), (18, 21)], fill=255)          # el muslo de delante
    dib.polygon([(21, 20), (24, 20), (24, 28), (21, 28)], fill=255)          # la espinilla
    dib.polygon([(20, 27), (26, 27), (26, 29), (20, 29)], fill=255)          # el pie
    dib.polygon([(10, 19), (15, 19), (14, 28), (10, 28)], fill=255)          # la rodilla en el suelo
    dib.polygon([(4, 27), (14, 27), (14, 29), (4, 29)], fill=255)
    dib.line([(17, 12), (26, 11)], fill=255, width=3)                       # el brazo, a la espada
    dib.rectangle((27, 6, 28, 29), fill=255)                                # la espada clavada
    dib.rectangle((24, 9, 31, 10), fill=255)
    dib.rectangle((26, 4, 29, 6), fill=255)
    sol = solido(m)
    marcas = {}
    for x in range(11, 18):
        marcas[(x, 6)] = NEGRO[1]                                          # la rendija del yelmo
    marcas[(14, 7)] = NEGRO[1]
    marcas[(14, 8)] = NEGRO[1]
    for y in range(11, 29):
        marcas[(27, y)] = ACERO[3]
        marcas[(28, y)] = ACERO[2]
    m2, dib2 = mascara(32, 32)
    dib2.polygon([(10, 10), (12, 11), (9, 24), (2, 28), (4, 21)], fill=255)  # la capa, que cae detras
    capa = solido(m2) - sol
    return sol, marcas, capa


def caballero_salta():
    m2, dib2 = mascara(32, 32)
    dib2.polygon([(12, 9), (20, 9), (25, 16), (22, 21), (16, 18), (10, 21), (7, 16)], fill=255)   # la capa, al vuelo
    m, dib = mascara(32, 32)
    dib.ellipse((12, 1, 20, 9), fill=255)
    dib.rectangle((12, 5, 20, 8), fill=255)
    dib.polygon([(11, 9), (21, 9), (20, 18), (12, 18)], fill=255)
    dib.line([(12, 10), (6, 3)], fill=255, width=3)
    dib.line([(20, 10), (26, 3)], fill=255, width=3)
    dib.line([(13, 17), (9, 21), (12, 24)], fill=255, width=3)
    dib.line([(19, 17), (23, 21), (20, 24)], fill=255, width=3)
    sol = solido(m)
    marcas = {}
    for x in range(13, 20):
        marcas[(x, 5)] = NEGRO[1]
    marcas[(16, 6)] = NEGRO[1]
    marcas[(16, 7)] = NEGRO[1]
    return sol, marcas, solido(m2) - sol


def sol_ojo():
    m, dib = mascara(32, 32)
    cx, cy = 16, 11
    dib.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=255)
    for i in range(8):
        a = i * math.pi / 4
        p = (cx + math.cos(a) * 11, cy + math.sin(a) * 11)
        q1 = (cx + math.cos(a + 0.28) * 6.5, cy + math.sin(a + 0.28) * 6.5)
        q2 = (cx + math.cos(a - 0.28) * 6.5, cy + math.sin(a - 0.28) * 6.5)
        dib.polygon([p, q1, q2], fill=255)
    sol = solido(m)
    m2, dib2 = mascara(32, 32)
    dib2.polygon([(7, 27), (11, 24), (16, 23), (21, 24), (25, 27), (21, 30), (16, 31), (11, 30)], fill=255)
    ojo = solido(m2) - sol
    return sol, ojo


def guantelete():
    m, dib = mascara(32, 32)
    dib.rounded_rectangle((10, 13, 22, 24), radius=2, fill=255)            # la palma
    for i, alto in enumerate((5, 3, 4, 6)):
        x = 10 + i * 3
        dib.rounded_rectangle((x, alto, x + 2, 14), radius=1, fill=255)    # los dedos
    dib.polygon([(10, 15), (6, 11), (4, 13), (9, 20)], fill=255)            # el pulgar
    dib.rectangle((9, 24, 23, 30), fill=255)                               # el punyo
    sol = solido(m)
    marcas = {}
    for i in range(4):
        x = 10 + i * 3
        for y in (9, 12):
            marcas[(x, y)] = CREMA[1]
            marcas[(x + 1, y)] = CREMA[1]
    for x in range(10, 23):
        marcas[(x, 25)] = ORO[2]
        marcas[(x, 26)] = ORO[1]
    return sol, marcas


def ordenes():
    im = lienzo(128, 32)
    sol, marcas, capa = caballero_rodillas()
    sombrear(im, capa, CARMESI, 0, 0, alcance=2.0)
    sombrear(im, sol, CREMA, 0, 0, marcas=marcas, alcance=2.5)
    motas(im, [(2, 30, CREMA[1]), (17, 30, CREMA[1])], 0, 0)
    sol, marcas, capa = caballero_salta()
    sombrear(im, capa, CARMESI, 32, 0, alcance=2.0)
    sombrear(im, sol, CREMA, 32, 0, marcas=marcas, alcance=2.5)
    # Debajo, la sombra en el suelo y unas rayas de impulso.
    for x in range(11, 22):
        pon(im, 32 + x, 30, NEGRO[4])
    for (x, y) in ((9, 27), (10, 27), (21, 27), (22, 27), (15, 28), (16, 28), (17, 28)):
        pon(im, 32 + x, y, CREMA[2])
    sol, ojo = sol_ojo()
    sombrear(im, sol, BRASA, 64, 0, nucleo=(16, 11), alcance=8.0)
    # El ojo: blanco con el canto pardo, y el iris arriba, mirando al sol.
    d = distancias(ojo)
    for (x, y) in ojo:
        pon(im, 64 + x, y, NEGRO[2] if d[(x, y)] == 0 else CREMA[4] if y < 28 else CREMA[3])
    for y in range(24, 29):
        for x in range(13, 20):
            dd = math.hypot(x - 16, y - 25.5)
            if dd < 2.9 and (x, y) in ojo and d[(x, y)] > 0:
                pon(im, 64 + x, y, NEGRO[1] if dd < 1.2 else HIELO[1] if dd < 2.2 else HIELO[0])
    pon(im, 64 + 15, 24, HIELO[4])
    # La mirada: tres motas de oro del ojo al sol.
    for (x, y) in ((16, 21), (16, 19)):
        pon(im, 64 + x, y, ORO[3])
    sol, marcas = guantelete()
    sombrear(im, sol, CREMA, 96, 0, marcas=marcas, alcance=3.0)
    motas(im, [(26, 6, CREMA[2]), (28, 9, CREMA[1]), (3, 6, CREMA[1])], 96, 0)
    return im


# ----------------------------------------------------------------------
#  Frio o Caliente: el termometro es su espada
# ----------------------------------------------------------------------

# La hoja: del pico (y 2) a la guarda (y 92); dentro, el cristal (x 13 a 18) se llena de abajo (y 90) arriba (y 8).
TUBO_X0, TUBO_X1 = 13, 18
TUBO_ABAJO, TUBO_ARRIBA = 90, 8


def termometro():
    w, h = 32, 128
    im = lienzo(128, 128)
    # La hoja: el pico y el cuerpo.
    semis = {2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 4}
    hoja = set()
    for y in range(2, 92):
        s = semis.get(y, 4)
        for x in range(16 - s, 16 + s):
            hoja.add((x, y))
    cristal = {(x, y) for (x, y) in hoja if TUBO_X0 <= x <= TUBO_X1 and TUBO_ARRIBA <= y <= TUBO_ABAJO}
    # El fondo del cristal (region 0): oscuro y opaco, para que se lea sobre el cielo.
    for (x, y) in hoja:
        pon(im, x, y, NEGRO[1] if (x, y) in cristal else NEGRO[0])
    # La guarda, la empunadura y el pomo (macizos en el fondo tambien).
    m, dib = mascara(w, h)
    dib.rounded_rectangle((3, 92, 28, 98), radius=2, fill=255)
    dib.rectangle((2, 88, 4, 93), fill=255)
    dib.rectangle((27, 88, 29, 93), fill=255)
    guarda = solido(m)
    m, dib = mascara(w, h)
    dib.rectangle((13, 99, 18, 111), fill=255)
    puno = solido(m)
    m, dib = mascara(w, h)
    dib.ellipse((8, 111, 24, 127), fill=255)
    pomo = solido(m)
    bulbo = {(x, y) for (x, y) in pomo if math.hypot(x - 16, y - 119) < 5.2}
    for (x, y) in pomo:
        pon(im, x, y, NEGRO[1] if (x, y) in bulbo else NEGRO[0])

    # El fuego que lo llena (region 1): de abajo arriba, del hielo al blanco del fuego, como un cilindro.
    zonas = [(0.0, HIELO), (0.533, ORO), (0.733, BRASA), (0.9, ((160, 20, 10), (220, 40, 20), (255, 90, 40), (255, 190, 120),
                                                                  (255, 250, 230)))]
    for y in range(TUBO_ARRIBA, TUBO_ABAJO + 1):
        nivel = (TUBO_ABAJO - y) / (TUBO_ABAJO - TUBO_ARRIBA)
        rampa = zonas[0][1]
        for desde, rr in zonas:
            if nivel >= desde:
                rampa = rr
        for x in range(TUBO_X0, TUBO_X1 + 1):
            t = {13: 1, 14: 3, 15: 4, 16: 3, 17: 2, 18: 1}[x]
            if (x + y) % 7 == 0 and t > 1:
                t -= 1
            pon(im, 32 + x, y, rampa[t])
    # El frente (region 2): los filos de la hoja, la guarda, la empunadura, el pomo de sol y las marcas.
    fx = 64
    d = distancias(hoja)
    for (x, y) in hoja:
        if (x, y) in cristal:
            continue
        luz = x < 16
        c = ACERO[3] if luz else ACERO[1]
        if d[(x, y)] == 0:
            c = ACERO[0]
        if y < 9 and luz:
            c = ACERO[4]
        pon(im, fx + x, y, c)
    # El brillo del cristal: una raya clara a la izquierda (transparente: deja ver el fuego).
    for y in range(TUBO_ARRIBA + 2, TUBO_ABAJO - 1):
        if y % 9 not in (0, 1):
            pon(im, fx + 14, y, (255, 255, 255), 70)
    # Las marcas de cada grado: muescas de oro en los dos filos (frio | templado | caliente | ardiendo).
    for nivel in (0.533, 0.733, 0.9):
        y = int(round(TUBO_ABAJO - nivel * (TUBO_ABAJO - TUBO_ARRIBA)))
        for x, c in ((10, ORO[1]), (11, ORO[3]), (20, ORO[3]), (21, ORO[1])):
            pon(im, fx + x, y, c)
        pon(im, fx + 12, y, ORO[2])
        pon(im, fx + 19, y, ORO[2])
    sombrear(im, guarda, ORO, fx, 0, alcance=2.0)
    for (x, y, c) in ((15, 94, BRASA[1]), (16, 94, BRASA[2]), (15, 95, BRASA[3]), (16, 95, BRASA[4]), (17, 95, BRASA[2]),
                      (15, 96, BRASA[1]), (16, 96, BRASA[2]), (14, 95, BRASA[1]), (17, 94, BRASA[1])):
        pon(im, fx + x, y, c)
    for (x, y) in puno:
        c = CARMESI[3] if (x + y) % 4 in (0, 1) else CARMESI[1]
        if (x - y) % 6 == 0:
            c = ORO[2]
        if x in (13, 18):
            c = CARMESI[0]
        pon(im, fx + x, y, c)
    # El pomo: un sol de oro alrededor del cristal, con ocho rayos.
    for y in range(108, 128):
        for x in range(4, 28):
            dd = math.hypot(x - 16, y - 119)
            a = math.atan2(y - 119, x - 16)
            if 5.2 <= dd < 6.4:
                pon(im, fx + x, y, ORO[0])
            elif 6.4 <= dd < 8.0:
                pon(im, fx + x, y, ORO[3] if (x - 16) + (y - 119) < 0 else ORO[1])
            elif 8.0 <= dd < 10.5 and abs(math.sin(a * 4)) < 0.22 and y < 128:
                pon(im, fx + x, y, ORO[2] if dd < 9.3 else ORO[1])
    pon(im, fx + 14, 116, (255, 255, 255), 140)
    pon(im, fx + 13, 117, (255, 255, 255), 90)
    # Los dos extremos: un cristal de hielo abajo a la izquierda y una llama arriba.
    for (x, y, c) in ((5, 82, HIELO[3]), (5, 84, HIELO[3]), (4, 83, HIELO[3]), (6, 83, HIELO[3]), (5, 83, HIELO[4]),
                      (3, 81, HIELO[2]), (7, 81, HIELO[2]), (3, 85, HIELO[2]), (7, 85, HIELO[2]), (5, 80, HIELO[1]), (5, 86, HIELO[1]),
                      (2, 83, HIELO[1]), (8, 83, HIELO[1])):
        pon(im, fx + x, y, c)
    for (x, y, c) in ((5, 8, BRASA[1]), (4, 9, BRASA[1]), (5, 9, BRASA[2]), (6, 9, BRASA[1]), (4, 10, BRASA[2]), (5, 10, BRASA[3]),
                      (6, 10, BRASA[2]), (4, 11, BRASA[2]), (5, 11, BRASA[4]), (6, 11, BRASA[2]), (5, 12, BRASA[3]), (6, 7, BRASA[0]),
                      (4, 12, BRASA[1]), (6, 12, BRASA[1])):
        pon(im, fx + x, y, c)
    # El relleno del pomo (region 3): una esfera en grises que el codigo tine del color del grado.
    for (x, y) in bulbo:
        dd = math.hypot(x - 14.8, y - 117.8)
        g = 255 if dd < 1.6 else 225 if dd < 3.0 else 190 if dd < 4.6 else 150
        pon(im, 96 + x, y, (g, g, g))
    return im


# ----------------------------------------------------------------------
#  La Forja: el yunque, el suelo, el aro, la mira y el destello
# ----------------------------------------------------------------------

def yunque():
    W, H = 128, 64
    im = lienzo(W, H)
    r = random.Random(11)

    def bloques(x0, y0, w, h, fila=5, largo=12):
        # Sillares de basalto: juntas oscuras, canto de arriba a la izquierda claro.
        for y in range(h):
            for x in range(w):
                f = y // fila
                xx = x + (largo // 2 if f % 2 else 0)
                junta = y % fila == fila - 1 or xx % largo == largo - 1
                if junta:
                    c = BASALTO[0]
                elif y % fila == 0 or xx % largo == 0:
                    c = BASALTO[3]
                else:
                    c = BASALTO[r.choice((1, 2, 2, 2))]
                pon(im, x0 + x, y0 + y, c)

    # A. El costado del cuerpo (48 x 16): banda de oro con soles, sillares y una veta de lava abajo.
    bloques(0, 3, 48, 13, fila=5, largo=12)
    for x in range(48):
        for y, c in ((0, ORO[0]), (1, ORO[3]), (2, ORO[1])):
            pon(im, x, y, c)
        if x % 8 == 4:
            pon(im, x, 1, ORO[4])
            pon(im, x - 1, 1, ORO[2])
            pon(im, x + 1, 1, ORO[2])
    for x in range(48):
        alto = 1 + (1 if math.sin(x * 0.7) > 0.3 else 0) + (1 if x % 11 == 3 else 0)
        for k in range(alto):
            pon(im, x, 15 - k, BRASA[2] if k == 0 else BRASA[1])
    for (x, y) in ((3, 8), (44, 8), (23, 9)):
        pon(im, x, y, ORO[3])
        pon(im, x + 1, y, ORO[1])
    # B. La cara de golpear (48 x 16): acero pulido con los colores del temple en el centro.
    temple = ((214, 186, 118), (190, 132, 70), (142, 78, 120), (74, 82, 156), (92, 98, 112))
    for y in range(16):
        for x in range(48):
            k = math.hypot((x - 23.5) / 24.0, (y - 7.5) / 8.0)
            c = temple[0] if k < 0.18 else temple[1] if k < 0.32 else temple[2] if k < 0.45 else temple[3] if k < 0.58 else ACERO[1]
            if k >= 0.58 and (x * 3 + y * 7) % 13 == 0:
                c = ACERO[2]
            if (x - 2 * y) % 17 == 0 and 0.2 < k < 0.9:
                c = ACERO[3]                                  # rayas del martillo
            if min(x, y, 47 - x, 15 - y) == 0:
                c = ORO[1]
            pon(im, 48 + x, y, c)
    # C. La cintura (16 x 16): basalto con una veta de lava que sube.
    for y in range(16):
        for x in range(16):
            c = BASALTO[1] if (x + y) % 5 else BASALTO[2]
            if x in (0, 15):
                c = BASALTO[0]
            if abs(x - 7.5 - math.sin(y * 0.8) * 1.5) < 0.8:
                c = BRASA[2] if y % 3 else BRASA[3]
            pon(im, 96 + x, y, c)
    # D. El costado de la peana (48 x 12): filos de oro y el sol en relieve en medio.
    bloques(0, 17, 48, 10, fila=5, largo=8)
    for x in range(48):
        pon(im, x, 16, ORO[0])
        pon(im, x, 17, ORO[2])
        pon(im, x, 27, ORO[0])
    for y in range(18, 27):
        for x in range(16, 32):
            dd = math.hypot(x - 23.5, y - 22)
            a = math.atan2(y - 22, x - 23.5)
            if dd < 2.2:
                pon(im, x, y, ORO[4] if dd < 1 else ORO[3])
            elif dd < 3.0:
                pon(im, x, y, ORO[1])
            elif dd < 4.6 and abs(math.sin(a * 4)) < 0.3:
                pon(im, x, y, ORO[2])
    # E. Lo de arriba de la peana (48 x 12): basalto tosco.
    for y in range(16, 28):
        for x in range(48, 96):
            pon(im, x, y, BASALTO[r.choice((1, 1, 2))] if min(x - 48, y - 16, 95 - x, 27 - y) else BASALTO[0])
    # F. El cuerno (32 x 8): acero que se oscurece hacia la punta.
    for y in range(16, 24):
        for x in range(96, 128):
            t = 3 if y in (17, 18) else 2 if y < 21 else 1
            if x > 118:
                t = max(1, t - 1)
            pon(im, x, y, ACERO[t] if y not in (16, 23) else ACERO[0])
    # G. La hoja al rojo (64 x 8): los filos casi blancos, el vaceo oscuro en medio, motas de cascarilla.
    filas = (4, 3, 2, 1, 1, 2, 3, 4)
    for y in range(8):
        for x in range(64):
            c = BRASA[filas[y]]
            if y in (3, 4) and x % 9 == 4:
                c = BRASA[0]
            if (x * 7 + y * 13) % 23 == 0 and 1 < y < 6:
                c = BRASA[0]
            pon(im, x, 32 + y, c)
    # H. La hoja forjada (64 x 8): oro con el filo blanco y soles grabados en el vaceo.
    for y in range(8):
        for x in range(64):
            c = ORO[filas[y]]
            if y in (3, 4) and x % 8 in (3, 4):
                c = ORO[4]
            pon(im, x, 40 + y, c)
    # I. La empunadura (16 x 8): cuero carmesi enrollado con hilo de oro.
    for y in range(8):
        for x in range(16):
            c = CARMESI[3] if (x + y) % 4 < 2 else CARMESI[1]
            if (x + y) % 8 == 0:
                c = ORO[2]
            pon(im, 64 + x, 32 + y, c)
    # J. La guarda (16 x 8): oro con una gema de fuego.
    for y in range(8):
        for x in range(16):
            c = (ORO[0], ORO[3], ORO[2], ORO[2], ORO[1], ORO[1], ORO[1], ORO[0])[y]
            if 6 <= x <= 9 and 2 <= y <= 5:
                c = BRASA[4] if (x, y) in ((7, 3), (8, 3)) else BRASA[2]
            pon(im, 80 + x, 32 + y, c)
    # K y L. Los tachones (8 x 8): apagado (hierro) y encendido (un sol).
    for y in range(8):
        for x in range(8):
            dd = math.hypot(x - 3.5, y - 3.5)
            pon(im, 96 + x, 32 + y, NEGRO[3] if dd < 2.2 else NEGRO[2] if dd < 3.5 else NEGRO[1])
            pon(im, 104 + x, 32 + y, ORO[4] if dd < 1.5 else ORO[3] if dd < 2.5 else ORO[2] if dd < 3.5 else ORO[1])
    return im


def forja_suelo():
    """El suelo alrededor del yunque: hollin que se aclara hacia fuera y brasas sueltas."""
    im = lienzo(64, 64)
    r = random.Random(17)
    for y in range(64):
        for x in range(64):
            dd = math.hypot(x - 31.5, y - 31.5) / 31.5
            if dd < 1.0:
                a = int(150 * (1.0 - dd) ** 1.5)
                if (x * 5 + y * 3) % 7 == 0:
                    a = int(a * 0.7)
                pon(im, x, y, NEGRO[0], a)
    for _ in range(46):
        a = r.random() * math.pi * 2
        d = 6 + r.random() * 24
        x = int(31.5 + math.cos(a) * d)
        y = int(31.5 + math.sin(a) * d)
        c = BRASA[r.choice((2, 2, 3, 4))]
        pon(im, x, y, c)
        if r.random() < 0.4:
            pon(im, x + 1, y, BRASA[1])
    return im


def aro():
    """El aro de luz: un sol con doce rayos que apuntan a la hoja."""
    im = lienzo(64, 64)
    for y in range(64):
        for x in range(64):
            dd = math.hypot(x - 31.5, y - 31.5)
            a = math.atan2(y - 31.5, x - 31.5)
            if 29.0 <= dd < 31.4:
                alma = 29.7 <= dd < 30.7
                pon(im, x, y, ORO[4] if alma else ORO[3], 255 if alma else 230)
            elif 26.6 <= dd < 27.6:
                pon(im, x, y, ORO[2], 150)
            else:
                # Los rayos: triangulos de 27 a 21 que apuntan hacia dentro.
                u = (a / (2 * math.pi / 12)) % 1.0
                ancho = (dd - 20.5) / 6.5 * 0.16
                if 20.5 <= dd < 27.0 and abs(u - 0.5) < ancho:
                    pon(im, x, y, ORO[3] if abs(u - 0.5) < ancho * 0.45 else ORO[2], 220)
                elif 27.6 <= dd < 29.0 and abs(u) < 0.03:
                    pon(im, x, y, ORO[4], 200)
    return im


def aro_hoja():
    """La mira quieta del tamano de la hoja: aro discontinuo y cuatro muescas."""
    im = lienzo(32, 32)
    for y in range(32):
        for x in range(32):
            dd = math.hypot(x - 15.5, y - 15.5)
            a = math.atan2(y - 15.5, x - 15.5)
            u = (a / (math.pi / 8)) % 2.0
            if 13.4 <= dd < 15.2 and u < 1.35:
                pon(im, x, y, (255, 255, 255), 255 if dd < 14.4 else 170)
            dx, dy = abs(x - 15.5), abs(y - 15.5)
            if (dx < 1.0 and 9.5 <= dy < 13.0 - dx * 2) or (dy < 1.0 and 9.5 <= dx < 13.0 - dy * 2):
                pon(im, x, y, (255, 255, 255), 230)
    return im


def destello():
    """El destello del golpe: estrella de ocho puntas, larga en cruz y corta en aspa."""
    im = lienzo(32, 32)
    for y in range(32):
        for x in range(32):
            dx, dy = x - 15.5, y - 15.5
            dd = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            u = (a / (math.pi / 4)) % 2.0
            k = 1.0 - abs(u - round(u))         # 1 en las puntas
            largo = 15.0 if round(u) % 2 == 0 else 9.0
            radio = 3.0 + (largo - 3.0) * (k ** 6)
            if dd < radio:
                c = (255, 255, 255) if dd < 2.5 else (255, 250, 230) if dd < radio * 0.5 else (255, 230, 170)
                pon(im, x, y, c, 255 if dd < radio * 0.7 else 190)
    return im


def grieta():
    """La grieta de la brasa: un charco de magma con costra y grietas encendidas que se ramifican."""
    im = lienzo(48, 48)
    r = random.Random(7)
    c0 = (23.5, 23.5)

    def rama(x, y, a, largo, nivel):
        for k in range(largo):
            a += r.uniform(-0.5, 0.5)
            x += math.cos(a)
            y += math.sin(a)
            xi, yi = int(round(x)), int(round(y))
            calor = 1.0 - k / max(1, largo)
            c = BRASA[4] if calor > 0.8 else BRASA[3] if calor > 0.5 else BRASA[2] if calor > 0.25 else BRASA[1]
            pon(im, xi, yi, c, 255 if calor > 0.3 else 200)
            # El hollin a los lados de la grieta.
            for (ox, oy) in ((1, 0), (0, 1)):
                q = (xi + ox, yi + oy)
                if 0 <= q[0] < 48 and 0 <= q[1] < 48 and im.getpixel(q)[3] == 0:
                    pon(im, q[0], q[1], NEGRO[1], 140)
            if nivel < 2 and r.random() < 0.12 and k > 2:
                rama(x, y, a + r.choice((-1, 1)) * r.uniform(0.6, 1.1), int(largo * 0.5), nivel + 1)

    for i in range(8):
        a = 2 * math.pi * i / 8 + r.uniform(-0.3, 0.3)
        rama(c0[0] + math.cos(a) * 4, c0[1] + math.sin(a) * 4, a, r.randrange(11, 19), 0)
    # El charco de magma, irregular, con placas de costra.
    for y in range(48):
        for x in range(48):
            a = math.atan2(y - c0[1], x - c0[0])
            borde = 5.4 + 0.9 * math.sin(a * 3 + 1) + 0.5 * math.sin(a * 5)
            dd = math.hypot(x - c0[0], y - c0[1])
            if dd < borde:
                if dd > borde - 1.0:
                    c = BRASA[1]
                elif (x * 3 + y * 5) % 11 == 0 and dd > 2:
                    c = BRASA[0]                # costra
                else:
                    c = BRASA[4] if dd < 1.8 else BRASA[3] if dd < 3.4 else BRASA[2]
                pon(im, x, y, c)
    return im


# ----------------------------------------------------------------------

def rps():
    im = lienzo(96, 32)
    piedra(im, 0, 0)
    papel(im, 32, 0)
    tijera(im, 64, 0)
    return im


def main():
    hechas = [
        guardar(yunque(), 'textures/entity/novilis/yunque.png'),
        guardar(forja_suelo(), 'textures/entity/novilis/forja_suelo.png'),
        guardar(aro(), 'textures/entity/novilis/aro_forja.png'),
        guardar(aro_hoja(), 'textures/entity/novilis/aro_hoja.png'),
        guardar(destello(), 'textures/entity/novilis/destello.png'),
        guardar(grieta(), 'textures/entity/novilis/brasa_grieta.png'),
        guardar(piedra(), 'textures/particle/novilis_piedra.png'),
        guardar(papel(), 'textures/particle/novilis_papel.png'),
        guardar(tijera(), 'textures/particle/novilis_tijera.png'),
        guardar(rps(), 'textures/gui/novilis_rps.png'),
        guardar(casillas(), 'textures/gui/novilis_rps_casilla.png'),
        guardar(estandarte(), 'textures/gui/novilis_manda.png'),
        guardar(cinta(), 'textures/gui/novilis_manda_cinta.png'),
        guardar(ordenes(), 'textures/gui/novilis_ordenes.png'),
        guardar(termometro(), 'textures/gui/novilis_termometro.png'),
    ]
    for nombre in ('novilis_piedra', 'novilis_papel', 'novilis_tijera'):
        with open(os.path.join(ASSETS, 'particles', nombre + '.json'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('{\n  "textures": [\n    "atalaya:' + nombre + '"\n  ]\n}\n')
    if len(sys.argv) > 2:
        escala = 5
        grandes = [h.resize((h.width * escala, h.height * escala), Image.NEAREST) for h in hechas]
        ancho = 1700
        x = y = alto = 0
        pos = []
        for g in grandes:
            if x + g.width > ancho:
                x, y, alto = 0, y + alto + 10, 0
            pos.append((x, y))
            x += g.width + 10
            alto = max(alto, g.height)
        hoja = Image.new('RGBA', (ancho, y + alto), (40, 34, 36, 255))
        for g, p in zip(grandes, pos):
            hoja.paste(g, p, g)
        hoja.save(sys.argv[2])


if __name__ == '__main__':
    main()

"""
Las texturas de los minijuegos de Aeralis (octubre de 2026): Ocelos, Veletas
del Vendaval, Pararrayos y La Chispa. Segunda version (10-10-2026, Juan:
"mejora el diseno de los ataques"): con la paleta de sus alas (pizarra de
tormenta con el canto electrico cian y los ocelos en espiral), la de su barra
(cian, anil, violeta y magenta de las fases) y las reglas de DISENO.md:
silueta como datos, contorno calculado, rampas de cinco tonos con el borde
tenido y alguna mota suelta. Lo redondo, de pixeles.

  entity/aeralis/aeralis_ocelos.png        sobre el atlas de Aeralis (512 x 1024): los ocelos hechos ojos abiertos
                                           (parpado de luz, iris rojo con estrias, pupila en rendija, brillo y un
                                           halo); fuera, transparente
  entity/aeralis/aeralis_ocelos_aviso.png  lo mismo con los ojos entornados, de ambar: van a abrirse
  entity/aeralis/veleta.png                la veleta (128 x 64): poste de la piedra de la cima con la espiral del
                                           viento tallada (y su luz aparte), tapa, cristal de tormenta (apagado y
                                           encendido), bronce, letras de los vientos, flecha (apagada y de luz) y
                                           la cola de polilla (apagada y de luz)
  entity/aeralis/rosa_vientos.png          la rosa de los vientos a los pies de cada veleta (64 x 64)
  entity/aeralis/veleta_cuna.png           la cuna de luz que marca en el suelo hacia donde apunta (32 x 32)
  entity/aeralis/circulo_rayo.png          el sello de tormenta donde va a caer un rayo (128 x 128)
  entity/aeralis/circulo_rayo_aro.png      el aro que se va cerrando hasta que cae (64 x 64)
  entity/aeralis/circulo_rayo_quemado.png  el suelo quemado con grietas de luz tras el rayo (64 x 64)
  entity/aeralis/rayo_columna.png          el rayo que cae del cielo (32 x 128: dos cuadros de 16 de ancho)
  entity/aeralis/chispa.png                la chispa (128 x 64): cuatro cuadros de una bola de rayos; abajo, de oro
  entity/aeralis/chispa_cuenta.png         la cuenta atras sobre la chispa (72 x 24): 3, 2 y 1
  entity/aeralis/chispa_aro.png            el aro que chisporrotea en el suelo alrededor de quien la lleva (64 x 64)
  entity/aeralis/remolino.png              el remolino de La Chispa jugando solo (128 x 64: cuatro cuadros de 32 x 64)
  item/pararrayos_tormenta.png             el pararrayos (16 x 16) y item/pararrayos_tormenta_cargado.png, cargado
  gui/aeralis_minijuegos.png               la pantalla (256 x 128): la placa de polilla con su medallon, los
                                           iconos del medallon y los ocelos de las alas (las cuentas)

Uso: python aeralis_minijuegos.py <raiz del proyecto> [hoja.png]
"""
import math
import os
import random
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
ASSETS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
ENT = os.path.join(ASSETS, 'textures/entity/aeralis')

NOCHE = ((6, 8, 22), (14, 16, 44), (24, 28, 70), (40, 46, 104), (62, 70, 140))
PLATA = ((70, 78, 110), (130, 140, 176), (184, 194, 222), (214, 222, 240), (244, 247, 255))
CIAN = ((20, 70, 120), (40, 130, 200), (95, 210, 255), (160, 232, 255), (226, 248, 255))
VIOLETA = ((52, 24, 98), (100, 56, 180), (176, 124, 255), (214, 180, 255), (246, 236, 255))
MAGENTA = ((90, 14, 70), (170, 40, 140), (255, 79, 216), (255, 160, 236), (255, 232, 250))
ROJO = ((80, 8, 20), (170, 24, 40), (255, 70, 90), (255, 150, 140), (255, 230, 210))
AMBAR = ((92, 46, 8), (176, 98, 18), (240, 168, 48), (255, 214, 118), (255, 244, 204))
ORO = ((96, 60, 10), (176, 120, 30), (240, 190, 70), (255, 226, 140), (255, 248, 214))
BRONCE = ((70, 40, 18), (130, 82, 34), (186, 128, 58), (226, 176, 98), (250, 222, 160))
VERDIN = ((40, 92, 86), (70, 140, 126))
COBRE = ((90, 40, 24), (150, 74, 44), (206, 112, 70), (238, 160, 118), (255, 214, 180))
PIEDRA = ((44, 48, 68), (70, 76, 100), (100, 108, 134), (136, 144, 170), (176, 184, 206))
# La pizarra de sus alas (de lo hondo a la franja clara del canto).
ALA = ((12, 16, 34), (26, 32, 60), (42, 52, 90), (64, 78, 122), (104, 120, 164))


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


def sombrear(im, sol, rampa, x0=0, y0=0, alcance=3.0):
    d = distancias(sol)
    for (x, y) in sol:
        dd = d[(x, y)]
        if dd == 0:
            t = 0
        else:
            t = 1 + min(3, int(dd * 3 / alcance + 0.5))
            if (x - 1, y - 1) not in sol or (x - 2, y - 2) not in sol:
                t = min(4, t + 1)
            elif (x + 1, y + 1) not in sol:
                t = max(1, t - 1)
        pon(im, x0 + x, y0 + y, rampa[t])


def halo(im, sol, color, alfa, x0=0, y0=0):
    """Un pixel de luz alrededor de la silueta (por fuera, sin pisarla ni pisar lo ya pintado)."""
    for (x, y) in sol:
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + a, y + b)
            px, py = x0 + q[0], y0 + q[1]
            if q in sol or not (0 <= px < im.width and 0 <= py < im.height):
                continue
            if im.getpixel((px, py))[3] == 0:
                pon(im, px, py, color, alfa)


def disco(cx, cy, r):
    return {(x, y) for y in range(int(cy - r - 1), int(cy + r + 2)) for x in range(int(cx - r - 1), int(cx + r + 2))
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}


def guardar(im, ruta):
    ruta = os.path.join(ASSETS, ruta)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    im.save(ruta)
    print('  ', os.path.relpath(ruta, ASSETS), im.size)
    return im


# ----------------------------------------------------------------------
#  Ocelos: los ojos sobre el atlas de Aeralis
# ----------------------------------------------------------------------

def buscar_ocelos():
    """Los aros blancos de los ocelos en el atlas: (cx, cy, radio)."""
    base = np.array(Image.open(os.path.join(ENT, 'aeralis_f1.png')).convert('RGBA')).astype(int)
    blanco = (base[..., 0] > 215) & (base[..., 1] > 215) & (base[..., 2] > 215) & (base[..., 3] > 200)
    lab, n = ndimage.label(blanco)
    ojos = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 40:
            continue
        cy, cx = ys.mean(), xs.mean()
        rad = np.hypot(ys - cy, xs - cx)
        # Un aro: sin pixeles en el centro y redondo; los ocelos miden de 5 a 21 de radio.
        if rad.min() < 3.0 or not (5.0 <= rad.max() <= 22.0) or cy > 440:
            continue
        ojos.append((cx, cy, rad.max()))
    return base.shape[1], base.shape[0], ojos


def ojo(im, cx, cy, R, abierto):
    """
    Un ocelo hecho ojo. Abierto: parpado de luz violeta, el blanco del ojo en
    noche, el iris rojo con estrias que se aclara hacia la pupila (en rendija,
    con el canto magenta), un brillo y un halo por fuera. Entornado (el aviso):
    el parpado cae y deja una almendra estrecha con el iris de ambar.
    """
    grande = R > 10
    iris = ROJO if abierto else AMBAR
    ri = R * 0.68
    for y in range(int(cy - R - 3), int(cy + R + 4)):
        for x in range(int(cx - R - 3), int(cx + R + 4)):
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy)
            if d > R + 1.6:
                continue
            if d > R + 0.6:
                pon(im, x, y, MAGENTA[2] if abierto else AMBAR[2], 110)              # el halo
                continue
            if not abierto:
                # La almendra que deja el parpado entornado.
                media = R * 0.36 * math.sqrt(max(0.0, 1 - (dx / R) ** 2))
                if abs(dy + R * 0.08) > media:
                    borde = abs(dy + R * 0.08) - media < 1.2
                    c = AMBAR[3] if borde and dy > 0 else VIOLETA[2] if borde else (VIOLETA[0] if d > R - 1.6 else NOCHE[1])
                    if not borde and dy < 0 and (x + y) % 5 == 0:
                        c = VIOLETA[1]                                                 # el veteado del parpado
                    pon(im, x, y, c)
                    continue
            if d > R - 1.6:
                c = VIOLETA[4] if dx + dy < 0 else MAGENTA[2] if abierto else AMBAR[2]   # el parpado, encendido
            elif d > ri:
                c = NOCHE[0] if d > R * 0.84 else NOCHE[1]                              # el blanco del ojo, oscuro
            else:
                k = d / ri
                a = math.atan2(dy, dx)
                estria = int((a / (2 * math.pi)) * (14 if grande else 9) + 100) % 2 == 0
                if k < 0.22:
                    c = iris[4]
                elif k < 0.45:
                    c = iris[3]
                elif k < 0.8:
                    c = iris[2] if estria else iris[3]
                else:
                    c = iris[1] if estria else iris[2]
                rendija = ri * (0.17 if grande else 0.26) * math.sqrt(max(0.0, 1 - (dy / ri) ** 2))
                if abs(dx) < rendija + 0.35:
                    c = NOCHE[0]
                elif abs(dx) < rendija + 1.25 and grande:
                    c = MAGENTA[1] if abierto else AMBAR[1]                             # el canto de la pupila
            pon(im, x, y, c)
    # El brillo, arriba a la izquierda (en el entornado, mas abajo: dentro de la almendra).
    bx, by = int(round(cx - R * 0.3)), int(round(cy - (R * 0.36 if abierto else R * 0.05)))
    pon(im, bx, by, (255, 255, 255))
    if grande:
        pon(im, bx + 1, by, (255, 255, 255))
        pon(im, bx, by + 1, (255, 240, 250))
        pon(im, bx + 3, by + 2, (255, 220, 240))


def ocelos(abierto):
    w, h, ojos = buscar_ocelos()
    im = lienzo(w, h)
    for cx, cy, R in ojos:
        ojo(im, cx, cy, R, abierto)
    print('   ocelos encontrados:', len(ojos))
    return im


# ----------------------------------------------------------------------
#  La veleta, su rosa de los vientos y la cuna
# ----------------------------------------------------------------------

LETRAS = {
    'N': ['#...#', '##..#', '#.#.#', '#..##', '#...#'],
    'E': ['#####', '#....', '####.', '#....', '#####'],
    'S': ['.####', '#....', '.###.', '....#', '####.'],
    'O': ['.###.', '#...#', '#...#', '#...#', '.###.'],
}


def espiral(x, y):
    """Si (x, y) de la cara del poste cae en la espiral tallada (y en los dos anillos)."""
    return (x + y * 0.75) % 16 < 2.0 or y in (3, 4, 43, 44)


def veleta():
    im = lienzo(128, 64)
    r = random.Random(4)
    # A. El costado del poste (16 x 48): sillares de la cima con la espiral del viento tallada.
    #    B, al lado: solo la luz de la espiral (lo demas transparente), para cuando apunta.
    for y in range(48):
        for x in range(16):
            c = PIEDRA[r.choice((1, 2, 2, 3))]
            if y % 12 == 11 or (x + (4 if (y // 12) % 2 else 0)) % 8 == 7:
                c = PIEDRA[0]                                                      # las juntas
            if x in (0, 15):
                c = PIEDRA[0]
            elif x == 1:
                c = PIEDRA[3] if c != PIEDRA[0] else c                             # el canto que da la luz
            if espiral(x, y) and 0 < x < 15:
                c = CIAN[0] if (x + y) % 3 else NOCHE[3]
                pon(im, 16 + x, y, CIAN[3] if (x + y) % 4 else CIAN[4])
            pon(im, x, y, c)
    # C. La tapa del poste (16 x 16): octogono con la runa del viento.
    for y in range(16):
        for x in range(16):
            dx, dy = abs(x - 7.5), abs(y - 7.5)
            d = max(dx, dy, (dx + dy) / 1.4)
            c = PIEDRA[0] if d > 6.6 else PIEDRA[1] if d > 5.6 else PIEDRA[3] if d < 2.2 else PIEDRA[2]
            pon(im, 32 + x, y, c)
    for (x, y) in ((7, 4), (8, 4), (9, 5), (10, 6), (10, 7), (9, 8), (8, 8), (7, 7), (7, 9), (6, 10), (5, 10)):
        pon(im, 32 + x, y, CIAN[1])                                                # la runa: una espiral
    # D. El bronce de la cruz (16 x 8) y E. el bronce oscuro (16 x 8).
    for y in range(8):
        for x in range(16):
            pon(im, 48 + x, y, BRONCE[(0, 3, 4, 3, 2, 2, 1, 0)[y]] if (x * 5 + y) % 13 else VERDIN[1])
            pon(im, 48 + x, 8 + y, BRONCE[(0, 2, 2, 1, 1, 1, 0, 0)[y]])
    # F. Las letras de los vientos (8 x 8 cada una, bronce claro sobre oscuro con el canto de luz).
    for k, l in enumerate('NESO'):
        ox, oy = 64 + (k % 2) * 8, (k // 2) * 8
        for y in range(8):
            for x in range(8):
                pon(im, ox + x, oy + y, BRONCE[0] if min(x, y, 7 - x, 7 - y) == 0 else BRONCE[1])
        for y, fila in enumerate(LETRAS[l]):
            for x, ch in enumerate(fila):
                if ch == '#':
                    pon(im, ox + 1 + x, oy + 1 + y, BRONCE[4] if y < 2 else BRONCE[3])
    # G. El cristal de tormenta (16 x 16) apagado y H. encendido: tallado en rombos.
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            faceta = (abs(dx) + abs(dy)) / 8.5
            luz = (dx < 0) + (dy < 0)
            if min(x, y, 15 - x, 15 - y) == 0:
                pon(im, 32 + x, 16 + y, CIAN[0])
                pon(im, 48 + x, 16 + y, CIAN[2])
                continue
            pon(im, 32 + x, 16 + y, (NOCHE[2], NOCHE[3], CIAN[0], CIAN[1])[min(3, luz + (faceta < 0.5))])
            pon(im, 48 + x, 16 + y, (CIAN[2], CIAN[3], CIAN[4], (255, 255, 255))[min(3, luz + (faceta < 0.5))])
    for (x, y) in ((5, 4), (4, 5), (10, 3)):
        pon(im, 32 + x, 16 + y, CIAN[2])
        pon(im, 48 + x, 16 + y, (255, 255, 255))
    # I. La flecha apagada (64 x 8) y J. la encendida: por filas, como una barra redonda, con grabados.
    for y in range(8):
        for x in range(64):
            t = (0, 2, 3, 4, 3, 2, 1, 0)[y]
            c = BRONCE[t]
            if x % 8 == 0 and 1 < y < 6:
                c = BRONCE[1]                                                      # los anillos grabados
            elif (x * 3 + y * 7) % 23 == 0 and 0 < y < 7:
                c = VERDIN[0] if t < 3 else VERDIN[1]                              # el verdin del bronce viejo
            pon(im, x, 48 + y, c)
            cl = CIAN[(1, 2, 3, 4, 4, 3, 2, 1)[y]]
            if y in (3, 4) and x % 6 == 0:
                cl = (255, 255, 255)
            pon(im, x, 56 + y, cl)
    # K. La cola de polilla (32 x 32), apagada y L. de luz: el ala de delante, la de detras y un ocelo.
    m, dib = mascara(32, 32)
    dib.polygon([(0, 12), (4, 6), (12, 2), (22, 0), (31, 0), (31, 6), (27, 12), (18, 15), (6, 15)], fill=255)  # delantera
    dib.polygon([(0, 17), (10, 16), (20, 17), (28, 21), (30, 27), (24, 31), (12, 30), (4, 24)], fill=255)      # trasera
    dib.rectangle([0, 12, 5, 19], fill=255)                                                                    # el engarce
    sol = solido(m)
    d = distancias(sol)
    for (x, y) in sol:
        dd = d[(x, y)]
        oc = math.hypot(x - 21, y - 7)
        oc2 = math.hypot(x - 19, y - 24)
        if dd == 0:
            apag, luz = BRONCE[0], CIAN[2]
        elif oc < 3.8 or oc2 < 2.8:
            k = oc / 3.8 if oc < 3.8 else oc2 / 2.8
            apag = VERDIN[1] if k < 0.4 else BRONCE[4] if k < 0.7 else BRONCE[1]
            luz = (255, 255, 255) if k < 0.4 else CIAN[2] if k < 0.7 else CIAN[4]
        elif dd == 1:
            apag, luz = BRONCE[3] if x + y < 30 else BRONCE[1], CIAN[4]
        else:
            # Las venas del ala, desde el engarce.
            vena = any(abs((y - 16) - s * x) < 0.6 for s in (-0.6, -0.25, 0.3, 0.6))
            apag = BRONCE[1] if vena else BRONCE[2] if (x * 7 + y * 3) % 11 else BRONCE[3]
            luz = CIAN[2] if vena else CIAN[3]
        pon(im, 64 + x, 16 + y, apag)
        pon(im, 96 + x, 16 + y, luz)
    return im


def rosa_vientos():
    """La rosa de los vientos: estrella de ocho puntas de piedra y bronce, con la N, E, S y O."""
    im = lienzo(64, 64)
    c = 31.5
    puntas = []
    for k in range(8):
        a = -math.pi / 2 + k * math.pi / 4
        largo = 21 if k % 2 == 0 else 13
        puntas.append((a, largo))
    m, dib = mascara(64, 64)
    for a, largo in puntas:
        ancho = 4.5 if largo > 20 else 3.0
        p = (c + math.cos(a) * largo, c + math.sin(a) * largo)
        i = (c + math.cos(a + math.pi / 2) * ancho, c + math.sin(a + math.pi / 2) * ancho)
        d = (c + math.cos(a - math.pi / 2) * ancho, c + math.sin(a - math.pi / 2) * ancho)
        dib.polygon([p, i, (c, c), d], fill=255)
    estrella = solido(m)
    # El aro de piedra, con sus muescas cada 45 grados.
    for y in range(64):
        for x in range(64):
            dd = math.hypot(x + 0.5 - 32, y + 0.5 - 32)
            a = math.degrees(math.atan2(y + 0.5 - 32, x + 0.5 - 32)) % 45
            if 29.0 <= dd < 31.5:
                pon(im, x, y, PIEDRA[0] if dd > 30.8 or dd < 29.6 else PIEDRA[2] if a > 3 and a < 42 else CIAN[2], 235)
            elif 15.0 <= dd < 16.0:
                pon(im, x, y, PIEDRA[1], 190)
    # La estrella: cada punta con su lado de luz y su lado de sombra (de bronce las grandes).
    for (x, y) in estrella:
        dx, dy = x + 0.5 - c - 0.5, y + 0.5 - c - 0.5
        a = math.atan2(dy, dx)
        mejor = min(puntas, key=lambda q: abs(math.atan2(math.sin(a - q[0]), math.cos(a - q[0]))))
        lado = math.sin(a - mejor[0]) > 0
        rampa = BRONCE if mejor[1] > 20 else PIEDRA
        borde = any((x + u, y + v) not in estrella for u, v in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        col = rampa[0] if borde else rampa[3] if lado else rampa[1]
        pon(im, x, y, col)
    for (x, y) in disco(32, 32, 2.6):
        pon(im, x, y, CIAN[2] if math.hypot(x + 0.5 - 32, y + 0.5 - 32) < 1.6 else BRONCE[0])
    # Las letras, en los huecos entre las puntas grandes y las pequenas, con su sombra.
    for l, (ox, oy) in (('N', (30, 4)), ('E', (55, 30)), ('S', (30, 55)), ('O', (4, 30))):
        letra = {(ox + x, oy + y) for y, fila in enumerate(LETRAS[l]) for x, ch in enumerate(fila) if ch == '#'}
        for (x, y) in {(x + 1, y + 1) for (x, y) in letra} - letra:
            pon(im, x, y, BRONCE[0])
        for (x, y) in letra:
            pon(im, x, y, BRONCE[4])
    return im


def veleta_cuna():
    """La cuna de luz (apunta hacia arriba de la textura): una punta de flecha de viento con su estela."""
    im = lienzo(32, 32)
    m, dib = mascara(32, 32)
    dib.polygon([(16, 0), (25, 12), (19, 11), (19, 22), (13, 22), (13, 11), (7, 12)], fill=255)
    sol = solido(m)
    sombrear(im, sol, CIAN, alcance=2.0)
    for k, y in enumerate(range(24, 32, 2)):
        for x in range(14 + k // 2, 18 - k // 2):
            pon(im, x, y, CIAN[2], 200 - k * 40)                                    # la estela
    return im


# ----------------------------------------------------------------------
#  El circulo del rayo: el sello, el aro que se cierra, el quemado y el rayo
# ----------------------------------------------------------------------

def circulo_rayo():
    """El sello de tormenta (128 x 128): doble aro con runas, ocho ocelos, aro de muescas y el rayo en medio."""
    im = lienzo(128, 128)
    c = 64.0
    for y in range(128):
        for x in range(128):
            dx, dy = x + 0.5 - c, y + 0.5 - c
            d = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            ang = (math.degrees(a) + 360) % 360
            if 59.0 <= d < 63.0:
                col = VIOLETA[4] if 60.4 <= d < 61.6 else VIOLETA[2] if d < 62.4 else VIOLETA[1]
                pon(im, x, y, col)
            elif 55.0 <= d < 59.0 and (ang % 15) < 1.6:
                pon(im, x, y, VIOLETA[3], 230)                                       # las runas del aro
            elif 40.0 <= d < 42.4:
                corte = (ang % 22.5) < 15.0
                pon(im, x, y, VIOLETA[3] if corte else VIOLETA[1], 240 if corte else 150)
            elif d < 59.0:
                pon(im, x, y, VIOLETA[1], int(64 * (1 - d / 59.0)) + 26)            # el velo de dentro
    # Los ocho ocelos de tormenta, entre los dos aros (redondos: se leen igual a cualquier giro).
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        ox, oy = c + math.cos(a) * 49.5, c + math.sin(a) * 49.5
        for (x, y) in disco(ox, oy, 4.6):
            dd = math.hypot(x + 0.5 - ox, y + 0.5 - oy)
            pon(im, x, y, VIOLETA[0] if dd > 3.8 else (255, 255, 255) if dd > 2.9 else CIAN[2] if dd > 1.4 else CIAN[4])
    # El rayo en medio, grande, con el corazon blanco.
    m, dib = mascara(128, 128)
    dib.polygon([(70, 22), (46, 66), (62, 66), (52, 106), (84, 56), (67, 56), (78, 22)], fill=255)
    sol = solido(m)
    sombrear(im, sol, VIOLETA, alcance=3.0)
    d = distancias(sol)
    for (x, y), dd in d.items():
        if dd >= 4:
            pon(im, x, y, (255, 255, 255))
    halo(im, sol, MAGENTA[2], 170)
    return im


def circulo_aro():
    """El aro que se cierra (64 x 64): un anillo de luz de canto quebrado, claro para teñirlo."""
    im = lienzo(64, 64)
    r = random.Random(9)
    quiebro = [r.uniform(-0.9, 0.9) for _ in range(48)]
    for y in range(64):
        for x in range(64):
            dx, dy = x + 0.5 - 32, y + 0.5 - 32
            d = math.hypot(dx, dy)
            a = (math.atan2(dy, dx) + math.pi) / (2 * math.pi) * 48
            q = quiebro[int(a) % 48] * (1 - a % 1) + quiebro[(int(a) + 1) % 48] * (a % 1)
            e = d - (29.5 + q)
            if abs(e) < 0.8:
                pon(im, x, y, (255, 255, 255))
            elif abs(e) < 1.7:
                pon(im, x, y, VIOLETA[4], 230)
            elif abs(e) < 2.7:
                pon(im, x, y, VIOLETA[3], 110)
    return im


def circulo_quemado():
    """El suelo quemado (64 x 64): mancha de ceniza con grietas que aun brillan."""
    im = lienzo(64, 64)
    r = random.Random(13)
    for y in range(64):
        for x in range(64):
            d = math.hypot(x + 0.5 - 32, y + 0.5 - 32)
            borde = 25 + 4 * math.sin(math.atan2(y - 32, x - 32) * 5 + 1.3)
            if d < borde:
                k = d / borde
                c = (16, 14, 22) if k < 0.4 else (28, 24, 34) if k < 0.75 else (44, 40, 52)
                if r.random() < 0.08:
                    c = (52, 46, 62)
                pon(im, x, y, c, int(235 - 120 * k * k))
    # Las grietas: caminos quebrados desde el centro.
    for k in range(7):
        a = k * 2 * math.pi / 7 + r.uniform(-0.3, 0.3)
        x, y = 32.0, 32.0
        for paso in range(26):
            a += r.uniform(-0.5, 0.5)
            x += math.cos(a)
            y += math.sin(a)
            c = (255, 255, 255) if paso < 5 else VIOLETA[3] if paso < 14 else VIOLETA[2]
            pon(im, int(x), int(y), c, 255 if paso < 18 else 160)
    return im


def rayo_columna():
    """El rayo que cae (32 x 128): dos cuadros de 16 de ancho; corazon blanco, canto violeta y ramas."""
    im = lienzo(32, 128)
    for k in range(2):
        r = random.Random(30 + k)
        x = 8.0
        camino = []
        for y in range(128):
            if y % 6 == 0:
                x = min(12.0, max(4.0, x + r.uniform(-2.6, 2.6)))
            camino.append(x)
        for y in range(128):
            cx = camino[y]
            for dx in range(-4, 5):
                xx = int(round(cx)) + dx
                a = abs(dx)
                c = (255, 255, 255) if a == 0 else VIOLETA[4] if a == 1 else VIOLETA[2] if a == 2 else VIOLETA[1]
                alfa = 255 if a <= 1 else 200 if a == 2 else 90 if a == 3 else 40
                pon(im, k * 16 + xx, y, c, alfa)
        # Las ramas.
        for _ in range(4):
            y0 = r.randint(10, 110)
            x = camino[y0]
            s = r.choice((-1, 1))
            for paso in range(9):
                x += s * r.uniform(0.4, 1.0)
                yy = y0 + paso
                if 0 <= x < 16:
                    pon(im, k * 16 + int(x), yy, VIOLETA[3], 220 - paso * 18)
    return im


# ----------------------------------------------------------------------
#  La chispa, su cuenta, su aro y el remolino
# ----------------------------------------------------------------------

def chispa():
    """Cuatro cuadros de una bola de rayos (32 x 32 cada uno); la fila de abajo, de oro (cargada)."""
    im = lienzo(128, 64)
    for fila, (rampa, arco) in enumerate(((VIOLETA, CIAN), (ORO, AMBAR))):
        for k in range(4):
            r = random.Random(50 + k)
            ox, oy = k * 32, fila * 32
            # El nucleo redondo, de pixeles, con el anillo.
            for (x, y) in disco(15.5, 15.5, 7.2):
                d = math.hypot(x + 0.5 - 15.5, y + 0.5 - 15.5)
                c = (255, 255, 255) if d < 2.6 else rampa[4] if d < 4.2 else rampa[3] if d < 5.8 else rampa[2]
                pon(im, ox + x, oy + y, c)
            for (x, y) in disco(15.5, 15.5, 8.6) - disco(15.5, 15.5, 7.2):
                pon(im, ox + x, oy + y, rampa[1], 200)
            # Los arcos: cuatro que saltan, quebrados, distintos en cada cuadro.
            for j in range(4):
                a = j * math.pi / 2 + k * 0.55 + r.uniform(-0.3, 0.3)
                x, y = 15.5 + math.cos(a) * 8, 15.5 + math.sin(a) * 8
                for paso in range(7):
                    a2 = a + r.uniform(-0.9, 0.9)
                    x += math.cos(a2) * 1.1
                    y += math.sin(a2) * 1.1
                    pon(im, ox + int(x), oy + int(y), arco[4] if paso < 3 else arco[3], 255 if paso < 5 else 170)
            # Motas sueltas.
            for _ in range(3):
                a = r.uniform(0, 2 * math.pi)
                rr = r.uniform(11, 14)
                pon(im, ox + int(15.5 + math.cos(a) * rr), oy + int(15.5 + math.sin(a) * rr), arco[2], 200)
    return im


CIFRAS = {
    '3': ['.####.', '#....#', '.....#', '..###.', '.....#', '#....#', '.####.'],
    '2': ['.####.', '#....#', '.....#', '....#.', '..##..', '.#....', '######'],
    '1': ['..##..', '.###..', '#.##..', '..##..', '..##..', '..##..', '######'],
}


def cuenta():
    """3, 2 y 1 (24 x 24 cada una): cifras gruesas de pixel, de blanco a oro, con canto de noche y su sombra."""
    im = lienzo(72, 24)
    for k, cif in enumerate('321'):
        sol = set()
        for y, fila in enumerate(CIFRAS[cif]):
            for x, ch in enumerate(fila):
                if ch == '#':
                    for a in range(3):
                        for b in range(3):
                            sol.add((k * 24 + 3 + x * 3 + a, 1 + y * 3 + b))
        for (x, y) in sol:
            pon(im, x + 1, y + 1, NOCHE[0])                                          # la sombra
        for (x, y) in sol:
            for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + a, y + b) not in sol:
                    pon(im, x + a, y + b, NOCHE[0])
        for (x, y) in sol:
            yy = y - 1
            pon(im, x, y, ORO[4] if yy < 6 else ORO[3] if yy < 13 else ORO[2])
    return im


def chispa_aro():
    """El aro que chisporrotea en el suelo (64 x 64): claro, para teñirlo (violeta y, al final, rojo)."""
    im = lienzo(64, 64)
    r = random.Random(17)
    for y in range(64):
        for x in range(64):
            dx, dy = x + 0.5 - 32, y + 0.5 - 32
            d = math.hypot(dx, dy)
            ang = (math.degrees(math.atan2(dy, dx)) + 360) % 360
            if 29.0 <= d < 31.0 and (ang % 20) < 13:
                pon(im, x, y, (255, 255, 255) if d < 30.0 else (220, 220, 240))
            elif 27.0 <= d < 29.0 and (ang % 20) < 13:
                pon(im, x, y, (200, 200, 230), 130)
            elif d < 27.0:
                pon(im, x, y, (190, 190, 220), int(22 * (d / 27.0) ** 2))
    # Chispas que saltan del aro hacia dentro.
    for k in range(10):
        a = k * 2 * math.pi / 10 + r.uniform(-0.2, 0.2)
        x, y = 32 + math.cos(a) * 28, 32 + math.sin(a) * 28
        for paso in range(4):
            x -= math.cos(a) * 1.2 + r.uniform(-0.6, 0.6)
            y -= math.sin(a) * 1.2 + r.uniform(-0.6, 0.6)
            pon(im, int(x), int(y), (255, 255, 255), 230 - paso * 45)
    return im


def remolino():
    """El remolino (cuatro cuadros de 32 x 64): un torbellino estrecho abajo y ancho arriba, de rachas claras."""
    im = lienzo(128, 64)
    for k in range(4):
        r = random.Random(70)
        for y in range(64):
            t = 1 - y / 63
            ancho = 3 + 12 * t ** 1.2
            for x in range(32):
                dx = (x + 0.5 - 16) / ancho
                if abs(dx) > 1:
                    continue
                # Rachas que suben girando: bandas en diagonal que se mueven con el cuadro.
                fase = (y * 0.55 + dx * 5.5 - k * 2.2) % 4.0
                borde = abs(dx) > 0.82
                if borde:
                    pon(im, k * 32 + x, y, CIAN[3], 150)
                elif fase < 1.1:
                    pon(im, k * 32 + x, y, (255, 255, 255) if abs(dx) < 0.5 else CIAN[4], 220)
                elif fase < 1.9:
                    pon(im, k * 32 + x, y, CIAN[3], 120)
                else:
                    pon(im, k * 32 + x, y, CIAN[2], 40)
        # El polvo que levanta abajo.
        for _ in range(8):
            x = 16 + r.uniform(-8, 8)
            y = 60 + r.uniform(-3, 3)
            pon(im, k * 32 + int(x + (k - 1.5) * 1.2), int(y), PLATA[2], 160)
    return im


# ----------------------------------------------------------------------
#  El pararrayos
# ----------------------------------------------------------------------

def pararrayos(cargado):
    """
    El pararrayos (16 x 16): asta de plata en diagonal con su pomo, la bobina de
    cobre de tres vueltas, la corona de tres puntas y el cristal de tormenta.
    Cargado: el cristal y la bobina dan luz y le saltan chispas.
    """
    im = lienzo(16, 16)
    # El asta, de abajo a la izquierda arriba a la derecha.
    for k in range(10):
        x, y = 3 + k, 12 - k
        pon(im, x, y, PLATA[3])
        pon(im, x + 1, y, PLATA[1])
        pon(im, x, y + 1, PLATA[0])
    # El pomo.
    for (x, y, c) in ((1, 14, PLATA[2]), (2, 14, PLATA[1]), (1, 13, PLATA[3]), (2, 13, PLATA[2]), (3, 13, PLATA[0]),
                      (2, 15, PLATA[0]), (0, 14, PLATA[0]), (1, 15, PLATA[0]), (0, 13, PLATA[0])):
        pon(im, x, y, c)
    # La bobina: tres vueltas de cobre.
    for j, k in enumerate((4, 6, 8)):
        x, y = 3 + k, 12 - k
        luz = cargado
        claro = CIAN[4] if luz else COBRE[3]
        medio = CIAN[2] if luz else COBRE[2]
        oscuro = CIAN[1] if luz else COBRE[0]
        for (a, b, c) in ((-1, -1, claro), (0, -1, claro), (-1, 0, medio), (1, 0, medio), (0, 1, oscuro), (1, 1, oscuro)):
            pon(im, x + a, y + b, c)
    # La corona: tres puntas de plata alrededor del cristal.
    for (x, y, c) in ((12, 0, PLATA[4]), (12, 1, PLATA[2]), (15, 3, PLATA[4]), (14, 3, PLATA[2]), (15, 0, PLATA[3]),
                      (11, 2, PLATA[1]), (13, 4, PLATA[1])):
        pon(im, x, y, c)
    # El cristal.
    cr = ((13, 1), (14, 1), (13, 2), (14, 2), (12, 3), (13, 3))
    for i, (x, y) in enumerate(cr):
        if cargado:
            pon(im, x, y, (255, 255, 255) if i in (0, 1) else CIAN[4] if i in (2, 3) else CIAN[3])
        else:
            pon(im, x, y, VIOLETA[4] if i == 0 else VIOLETA[3] if i in (1, 2) else VIOLETA[2] if i == 3 else VIOLETA[1])
    if cargado:
        for (x, y, c) in ((10, 0, CIAN[3]), (15, 5, CIAN[3]), (9, 1, CIAN[2]), (6, 3, CIAN[3]), (11, 7, CIAN[2]),
                          (5, 9, CIAN[4]), (8, 11, CIAN[2])):
            pon(im, x, y, c)
    else:
        pon(im, 10, 0, VIOLETA[2])
        pon(im, 15, 5, CIAN[2])
    return im


# ----------------------------------------------------------------------
#  La pantalla: la placa de polilla, los iconos del medallon y las cuentas
# ----------------------------------------------------------------------

PLACA = (176, 48)
MEDALLON = (88.0, 24.0, 21.5)
# Los huecos de las cuentas en las alas (centro, de la izquierda; la derecha es su espejo).
# Mismo orden que AeralisMinijuegosHud.HUECOS.
HUECOS_IZQ = [(52, 18), (36, 13), (18, 11), (60, 40)]


def placa():
    """La placa: dos pares de alas de su pizarra con el canto electrico, y el medallon de plata en medio."""
    im = lienzo(*PLACA)
    m, dib = mascara(*PLACA)
    izq_sup = [(86, 18), (70, 14), (56, 10), (40, 4), (22, 0), (8, 0), (1, 4), (0, 12), (4, 20), (10, 26), (20, 30),
               (34, 30), (48, 27), (62, 25), (86, 24)]
    izq_inf = [(86, 28), (72, 30), (60, 33), (50, 38), (46, 43), (50, 47), (60, 47), (72, 43), (82, 37), (88, 31)]
    for pol in (izq_sup, izq_inf):
        dib.polygon(pol, fill=255)
        dib.polygon([(PLACA[0] - 1 - x, y) for x, y in pol], fill=255)
    alas = solido(m)
    d = distancias(alas)
    r = random.Random(3)
    raiz = (88, 24)
    for (x, y) in alas:
        dd = d[(x, y)]
        xi = x if x < 88 else PLACA[0] - 1 - x
        vena = False
        for s in (-0.55, -0.22, 0.08, 0.42, 0.85):
            if abs((y - raiz[1]) - s * (raiz[0] - xi)) < 0.55 and dd >= 2:
                vena = True
        if dd == 0:
            c = CIAN[4] if (x * 7 + y * 3) % 9 == 0 else CIAN[2]                   # el canto electrico
        elif dd == 1:
            c = ALA[1]
        elif dd == 2:
            c = ALA[4]                                                               # la franja clara del canto
        elif dd == 3:
            c = ALA[3]
        elif dd in (5, 6) and (x + 2 * y) % 5 < 2:
            c = ALA[3]                                                               # las manchas de la orla
        elif vena:
            c = ALA[1]
        else:
            c = ALA[2]
        pon(im, x, y, c)
    halo(im, alas, CIAN[1], 140)
    # El medallon: aro de plata con doce marcas y el fondo de noche.
    cx, cy, R = MEDALLON
    for (x, y) in disco(cx, cy, R):
        dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
        ang = (math.degrees(math.atan2(y + 0.5 - cy, x + 0.5 - cx)) + 360) % 360
        if dd > R - 0.9:
            c = PLATA[0]
        elif dd > R - 2.0:
            c = PLATA[4] if (x + y) < cx + cy - 6 else PLATA[2]
        elif dd > R - 3.2:
            c = CIAN[3] if (ang % 30) < 6 else PLATA[1]
        elif dd > R - 4.0:
            c = NOCHE[0]
        else:
            k = dd / (R - 4.0)
            c = NOCHE[3] if k < 0.35 else NOCHE[2] if k < 0.7 else NOCHE[1]
        pon(im, x, y, c)
    return im


def icono_ojo(im, ox, oy, estado):
    """El ojo del medallon (32 x 32): 0 abierto (rojo), 1 entornado (ambar), 2 cerrado (cian)."""
    if estado == 2:
        for x in range(3, 30):
            y = int(round(15 + 5 * math.sin((x - 3) / 26 * math.pi)))
            pon(im, ox + x, oy + y, CIAN[4])
            pon(im, ox + x, oy + y - 1, CIAN[2])
            pon(im, ox + x, oy + y + 1, CIAN[1])
        for x in (7, 12, 16, 20, 25):
            y = int(round(15 + 5 * math.sin((x - 3) / 26 * math.pi)))
            pon(im, ox + x + (1 if x > 16 else -1 if x < 16 else 0), oy + y + 3, CIAN[3])
            pon(im, ox + x + (2 if x > 16 else -2 if x < 16 else 0), oy + y + 5, CIAN[2])
        return
    alto = 9.5 if estado == 0 else 4.5
    iris = ROJO if estado == 0 else AMBAR
    sol = set()
    for y in range(32):
        for x in range(32):
            dx, dy = x + 0.5 - 16, y + 0.5 - 16
            if abs(dx) < 15 and abs(dy) < alto * (1 - (dx / 15) ** 2) ** 0.8:
                sol.add((x, y))
    d = distancias(sol)
    for (x, y) in sol:
        dx, dy = x + 0.5 - 16, y + 0.5 - 16
        rr = math.hypot(dx, dy)
        if d[(x, y)] == 0:
            c = VIOLETA[4] if dy < 0 else (MAGENTA[2] if estado == 0 else AMBAR[2])
        elif rr < 8.0:
            k = rr / 8.0
            estria = int((math.atan2(dy, dx) / (2 * math.pi)) * 12 + 100) % 2 == 0
            c = iris[4] if k < 0.25 else iris[3] if k < 0.5 else (iris[2] if estria else iris[3]) if k < 0.8 else iris[1]
            if abs(dx) < 1.5 * math.sqrt(max(0, 1 - (dy / 8.0) ** 2)) + 0.2:
                c = NOCHE[0]
        else:
            c = NOCHE[1]
        pon(im, ox + x, oy + y, c)
    if estado == 1:
        # El parpado que cae, pesado, por encima.
        for x in range(2, 30):
            dx = x + 0.5 - 16
            ytop = 16 - 4.5 * (1 - (dx / 15) ** 2) ** 0.8
            for y in range(int(16 - 10 * (1 - (dx / 15) ** 2) ** 0.8), int(ytop)):
                pon(im, ox + x, oy + y, VIOLETA[0] if (x + y) % 4 else VIOLETA[1])
    pon(im, ox + 12, oy + 12 + (3 if estado == 1 else 0), (255, 255, 255))
    pon(im, ox + 13, oy + 12 + (3 if estado == 1 else 0), (255, 255, 255))
    if estado == 0:
        for (x, y) in ((16, 2), (16, 3), (9, 4), (23, 4), (4, 8), (28, 8)):
            pon(im, ox + x, oy + y, VIOLETA[3])                                     # las pestanas de luz


def icono_chispa(im, ox, oy, oro):
    rampa, arco = (ORO, AMBAR) if oro else (VIOLETA, CIAN)
    for (x, y) in disco(16, 16, 8.0):
        dd = math.hypot(x + 0.5 - 16, y + 0.5 - 16)
        pon(im, ox + x, oy + y, (255, 255, 255) if dd < 3 else rampa[4] if dd < 4.8 else rampa[3] if dd < 6.5 else rampa[2])
    for (x, y) in disco(16, 16, 9.4) - disco(16, 16, 8.0):
        pon(im, ox + x, oy + y, rampa[1])
    r = random.Random(5)
    for j in range(6):
        a = j * math.pi / 3 + 0.3
        x, y = 16 + math.cos(a) * 9, 16 + math.sin(a) * 9
        for paso in range(5):
            a2 = a + r.uniform(-0.8, 0.8)
            x += math.cos(a2) * 1.2
            y += math.sin(a2) * 1.2
            pon(im, ox + int(x), oy + int(y), arco[4] if paso < 2 else arco[3])


def icono_rayo(im, ox, oy):
    m, dib = mascara(32, 32)
    dib.polygon([(19, 1), (8, 17), (15, 17), (10, 31), (24, 12), (17, 12), (22, 1)], fill=255)
    sol = solido(m)
    sombrear(im, sol, VIOLETA, ox, oy, alcance=2.0)
    for (x, y), dd in distancias(sol).items():
        if dd >= 2:
            pon(im, ox + x, oy + y, (255, 255, 255))
    for (x, y) in sol:
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + a, y + b) not in sol:
                pon(im, ox + x + a, oy + y + b, CIAN[2], 160)


def cuenta_hueco(im, ox, oy, tipo):
    """
    Un ocelo de las alas (11 x 11): 0 apagado, 1 encendido (la espiral cian de
    sus alas), 2 ojo abierto (rojo), 3 ojo cerrado, 4 de oro, 5 entornado (ambar).
    """
    c = 5.0
    for y in range(11):
        for x in range(11):
            dx, dy = x - c, y - c
            d = math.hypot(dx, dy)
            if d > 5.4:
                continue
            borde = d > 4.3
            if tipo == 0:
                col = ALA[3] if borde else ALA[0] if d > 1.6 else ALA[2]
            elif tipo == 1:
                ang = math.atan2(dy, dx)
                espira = (ang / (2 * math.pi) * 1.0 + d / 3.2) % 1.0 < 0.45
                col = (255, 255, 255) if borde else CIAN[4] if d < 1.3 else CIAN[2] if espira else NOCHE[1]
            elif tipo == 4:
                col = ORO[4] if borde else ORO[3] if d < 2.2 else ORO[2]
            elif tipo == 3:
                col = ALA[3] if borde else (CIAN[3] if abs(dy - 0.5 * math.sin(dx / 4)) < 0.7 else ALA[0])
            else:
                iris = ROJO if tipo == 2 else AMBAR
                abre = 1.0 if tipo == 2 else 0.45
                if borde:
                    col = VIOLETA[3] if dy < 0 else iris[2]
                elif abs(dy) > 4.3 * abre:
                    col = VIOLETA[0]
                else:
                    col = NOCHE[0] if abs(dx) < 0.8 else iris[3] if d < 2.2 else iris[2]
            pon(im, ox + x, oy + y, col)


def pantalla():
    im = lienzo(256, 128)
    p = placa()
    im.paste(p, (0, 0), p)
    # Los iconos del medallon (32 x 32), en la fila de y = 48.
    icono_ojo(im, 0, 48, 0)
    icono_ojo(im, 32, 48, 1)
    icono_ojo(im, 64, 48, 2)
    icono_chispa(im, 96, 48, False)
    icono_chispa(im, 128, 48, True)
    icono_rayo(im, 160, 48)
    # Las cuentas (11 x 11), en la fila de y = 88, cada 12.
    for k in range(6):
        cuenta_hueco(im, k * 12, 88, k)
    return im


def main():
    hechas = [
        guardar(ocelos(True), 'textures/entity/aeralis/aeralis_ocelos.png'),
        guardar(ocelos(False), 'textures/entity/aeralis/aeralis_ocelos_aviso.png'),
        guardar(veleta(), 'textures/entity/aeralis/veleta.png'),
        guardar(rosa_vientos(), 'textures/entity/aeralis/rosa_vientos.png'),
        guardar(veleta_cuna(), 'textures/entity/aeralis/veleta_cuna.png'),
        guardar(circulo_rayo(), 'textures/entity/aeralis/circulo_rayo.png'),
        guardar(circulo_aro(), 'textures/entity/aeralis/circulo_rayo_aro.png'),
        guardar(circulo_quemado(), 'textures/entity/aeralis/circulo_rayo_quemado.png'),
        guardar(rayo_columna(), 'textures/entity/aeralis/rayo_columna.png'),
        guardar(chispa(), 'textures/entity/aeralis/chispa.png'),
        guardar(cuenta(), 'textures/entity/aeralis/chispa_cuenta.png'),
        guardar(chispa_aro(), 'textures/entity/aeralis/chispa_aro.png'),
        guardar(remolino(), 'textures/entity/aeralis/remolino.png'),
        guardar(pararrayos(False), 'textures/item/pararrayos_tormenta.png'),
        guardar(pararrayos(True), 'textures/item/pararrayos_tormenta_cargado.png'),
        guardar(pantalla(), 'textures/gui/aeralis_minijuegos.png'),
    ]
    if len(sys.argv) > 2:
        # La hoja para mirarlas: ampliadas, sobre gris oscuro (los ocelos, recortados a las alas).
        grandes = []
        for h in hechas:
            if h.size == (512, 1024):
                h = h.crop((0, 0, 512, 440))
                k = 2
            else:
                k = max(1, min(8, 420 // max(h.size)))
            grandes.append(h.resize((h.width * k, h.height * k), Image.NEAREST))
        ancho = 2200
        x = y = alto = 0
        pos = []
        for g in grandes:
            if x + g.width > ancho:
                x, y, alto = 0, y + alto + 10, 0
            pos.append((x, y))
            x += g.width + 10
            alto = max(alto, g.height)
        hoja = Image.new('RGBA', (ancho, y + alto), (40, 34, 52, 255))
        for g, q in zip(grandes, pos):
            hoja.paste(g, q, g)
        hoja.save(sys.argv[2])


if __name__ == '__main__':
    main()

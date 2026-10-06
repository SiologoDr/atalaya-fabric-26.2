"""
Las texturas del remake de Aeralis (octubre de 2026), pixel a pixel. Solo
escribe ficheros nuevos (y el icono de la Marca, que cambia de dibujo): volver
a pasar aeralis_extras.py reescribiria todo lo de antes.

  textures/entity/aeralis/
    polilla.png        la rafaga de la Caceria: una polilla de viento, en
                       grises para tenirla del color de la fase (32x32)
    picado_galon.png   un galon de la linea del Picado (se repite a lo largo)
    picado_punta.png   el final de la linea, donde se posa
    aro.png            el aro del suelo de los tornados y las corrientes (64x64)
    rayo.png           una veta de rayo para las ataduras del Juicio (8x32)
    aeralis_furia_N.png  el aura de la Furia del Vendaval, doce cuadros sobre
                       el atlas de Aeralis (respeta el recorte de las alas):
                       rayos en zigzag violetas que corren, como la de Rajang
    embudo.png         el embudo de los tornados: un velo de aire con vetas
                       que se enroscan, en grises para tenirlo (32x64; el
                       tornado.png de antes queda para las columnas de luz)
  textures/mob_effect/
    marca_vendaval.png la Marca del Vendaval: una polilla de viento, la misma
                       de la Caceria (18x18, el metodo de DISENO.md)
    paralisis.png      la Paralisis de las Escamas de Tormenta: un rayo en el
                       violeta de la Tempestad, con chispas (18x18)

Uso: python aeralis_mejoras_extras.py <raiz del proyecto>
"""
import math, os, sys
from PIL import Image

RAIZ = sys.argv[1]
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
ENT = os.path.join(A, 'entity/aeralis')
EFE = os.path.join(A, 'mob_effect')


def lienzo(w, h=None):
    return Image.new('RGBA', (w, h or w), (0, 0, 0, 0))


def gris(v, a=255):
    return (v, v, v, a)


# ----------------------------------------------------------------------
#  La polilla de viento: cuatro alas con el filo claro, el cuerpo blanco y
#  un ocelo en cada ala de arriba. En grises: el juego la tine.
# ----------------------------------------------------------------------
def polilla():
    n = 32
    im = lienzo(n)
    px = im.load()
    c = (n - 1) / 2
    dentro = set()
    for y in range(n):
        for x in range(n):
            dx, dy = (x - c) / c, (y - c) / c
            ea = ((abs(dx) - 0.46) / 0.46) ** 2 + ((dy + 0.22) / 0.40) ** 2
            eb = ((abs(dx) - 0.30) / 0.30) ** 2 + ((dy - 0.38) / 0.32) ** 2
            if ea < 1 or eb < 1:
                dentro.add((x, y))
    for (x, y) in dentro:
        borde = any((x + dx, y + dy) not in dentro for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        dxn = abs(x - c) / c
        # el canto oscuro (se tine de la fase en oscuro) para que se lea contra el cielo,
        # un filo claro por dentro y el ala clara
        filo = any((x + dx, y + dy) not in dentro for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)))
        px[x, y] = gris(60, 255) if borde else gris(255, 245) if filo else gris(int(170 + 70 * dxn), 215)
    for s in (-1, 1):
        ox, oy = c + s * 0.48 * c, c - 0.22 * c
        for y in range(n):
            for x in range(n):
                d = math.hypot(x - ox, y - oy)
                if d < 3.2 and (x, y) in dentro:
                    px[x, y] = gris(255) if d < 1.2 else gris(110, 230) if d < 2.2 else gris(240)
    for y in range(4, n - 4):
        for x in (int(c), int(c) + 1):
            px[x, y] = gris(255)
    for s in (-1, 1):
        for k in range(5):
            px[int(c + s * (1 + k * 0.7)), 3 - k // 2 if k < 4 else 1] = gris(235)
    return im


# ----------------------------------------------------------------------
#  La linea del Picado: galones de viento (v crece hacia donde se lanza)
# ----------------------------------------------------------------------
def galon():
    w = h = 32
    im = lienzo(w, h)
    px = im.load()
    for y in range(h):
        for x in range(w):
            u, v = x / (w - 1), y / (h - 1)
            cen = abs(u - 0.5)
            d = abs(v - (0.62 - cen * 0.9))
            if d < 0.07:
                px[x, y] = gris(255, 250)
            elif d < 0.13:
                px[x, y] = gris(200, 200)
            elif u < 0.05 or u > 0.95:
                px[x, y] = gris(230, 210)
            else:
                px[x, y] = gris(120, 60)
    return im


def punta():
    w = h = 32
    im = lienzo(w, h)
    px = im.load()
    for y in range(h):
        for x in range(w):
            dx, dy = x - (w - 1) / 2, y - (h - 1) / 2
            d = math.hypot(dx, dy) / (w / 2)
            if 0.82 < d < 0.98:
                px[x, y] = gris(255, 245)
            elif 0.5 < d < 0.6:
                px[x, y] = gris(220, 210)
            elif d < 0.82 and (math.atan2(dy, dx) * 4 / math.pi) % 1 < 0.18:
                px[x, y] = gris(200, 150)
            elif d < 0.82:
                px[x, y] = gris(120, 50)
    return im


# ----------------------------------------------------------------------
#  El aro del suelo: un anillo con muescas, en grises
# ----------------------------------------------------------------------
def aro():
    n = 64
    im = lienzo(n)
    px = im.load()
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2, y + 0.5 - n / 2
            d = math.hypot(dx, dy) / (n / 2)
            a = math.atan2(dy, dx)
            if 0.93 < d < 1.0:
                px[x, y] = gris(255, 240)
            elif 0.82 < d < 0.88 and ((a + math.pi) / (2 * math.pi) * 24) % 1 < 0.45:
                px[x, y] = gris(220, 200)
            elif d < 0.82:
                px[x, y] = gris(160, int(40 * d))
    return im


# ----------------------------------------------------------------------
#  Una veta de rayo: el centro blanco, los filos que se apagan
# ----------------------------------------------------------------------
def rayo():
    w, h = 8, 32
    im = lienzo(w, h)
    px = im.load()
    for y in range(h):
        for x in range(w):
            d = abs(x - (w - 1) / 2) / ((w - 1) / 2)
            if d < 0.3:
                px[x, y] = gris(255)
            elif d < 0.75:
                px[x, y] = gris(230, int(220 * (1 - d)))
    return im


# ----------------------------------------------------------------------
#  El embudo: un velo de aire (para que tenga cuerpo y no parezca una red),
#  bandas mas densas y vetas claras en diagonal que se enroscan. Se repite en
#  los dos sentidos.
# ----------------------------------------------------------------------
def embudo():
    w, h = 32, 64
    im = lienzo(w, h)
    px = im.load()
    for y in range(h):
        for x in range(w):
            u, v = x / w, y / h
            banda = 0.5 + 0.5 * math.sin(2 * math.pi * (2 * u + 1 * v) + 1.3 * math.sin(2 * math.pi * 3 * v))
            veta = math.sin(2 * math.pi * (4 * u + 2 * v)) > 0.82
            fina = math.sin(2 * math.pi * (7 * u + 3 * v) + 2.0) > 0.93
            if veta:
                px[x, y] = gris(255, 235)
            elif fina:
                px[x, y] = gris(240, 170)
            else:
                ruido = ((x * 7 + y * 13) % 11) / 11.0
                px[x, y] = gris(int(170 + 60 * banda), int(70 + 80 * banda + 18 * ruido))
    return im


# ----------------------------------------------------------------------
#  El aura de la Furia: sobre el mismo atlas de Aeralis (solo donde hay
#  piel, asi respeta el recorte de las alas), bandas en diagonal que se
#  quiebran en zigzag como rayos, del blanco violeta al violeta oscuro, y un
#  brillo tenue debajo. Doce cuadros con las bandas corridas 2 px cada uno (el
#  ultimo empalma con el primero): el juego funde cada cuadro con el siguiente
#  y las bandas corren seguidas, sin saltos (con cuatro cuadros de 6 px se veia
#  a tirones). Fuera de las bandas, transparente.
# ----------------------------------------------------------------------
CUADROS_FURIA = 12


def aura_furia(cuadro):
    import numpy as np
    base = np.array(Image.open(os.path.join(ENT, 'aeralis_f1.png')).convert('RGBA'))
    h, w = base.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    # Rayos gruesos: el atlas va a media resolucion y las alas son enormes, asi
    # que con bandas finas no se veian.
    quiebro = np.where((yy // 10) % 2 == 0, 5.0, -5.0)
    s = (xx + yy + quiebro + 3.0 * np.sin(2 * np.pi * yy / 48.0) + cuadro * 24.0 / CUADROS_FURIA) % 24.0
    out = np.zeros((h, w, 4), np.uint8)
    # Algo mas finas y mas transparentes que al principio: se ve el cuerpo debajo.
    out[s < 9.0] = (110, 50, 200, 85)
    out[s < 6.0] = (175, 105, 255, 175)
    out[s < 2.5] = (246, 232, 255, 245)
    out[base[..., 3] < 16] = 0
    return Image.fromarray(out)


# ----------------------------------------------------------------------
#  El icono de la Marca: la polilla de 18x18 (ver viento_remake_iconos.py)
# ----------------------------------------------------------------------
CANTO, MEDIO, CLARO, NUCLEO = (90, 170, 255), (120, 190, 255), (162, 211, 255), (222, 242, 255)
EJE = 8
FILAS = {3: [0, 3, 4, 5], 4: [0, 1, 2, 3, 4, 5, 6], 5: [0, 1, 2, 3, 4, 5, 6, 7], 6: [0, 1, 2, 3, 4, 5, 6, 7],
         7: [0, 1, 2, 3, 4, 5, 6], 8: [0, 1, 2, 3, 4], 9: [0, 1, 2, 3, 4, 5], 10: [0, 1, 2, 3, 4, 5],
         11: [0, 1, 2, 3, 4], 12: [0, 2, 3], 13: [0, 3], 14: [3]}
ANTENAS = [(EJE - 1, 2), (EJE - 2, 1), (EJE + 1, 2), (EJE + 2, 1)]
OCELOS = [(EJE - 4, 5.5), (EJE + 4, 5.5), (EJE - 3, 9.5), (EJE + 3, 9.5)]
MOTAS = [(1, 14, MEDIO), (16, 3, CLARO), (15, 12, MEDIO)]


def icono_marca():
    solido = set(ANTENAS)
    for y, dxs in FILAS.items():
        for dx in dxs:
            solido.add((EJE - dx, y))
            solido.add((EJE + dx, y))
    im = lienzo(18)
    px = im.load()
    for (x, y) in solido:
        if x == EJE:
            c = NUCLEO if y in (4, 5, 6) else CLARO
        elif any((x + dx, y + dy) not in solido for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c = CANTO
        else:
            d = min(math.hypot(x - ox, y - oy) for ox, oy in OCELOS)
            c = NUCLEO if d < 0.8 else CLARO if d < 1.7 else MEDIO
        px[x, y] = (*c, 255)
    for (x, y) in ANTENAS:
        px[x, y] = (*CLARO, 255)
    for x, y, c in MOTAS:
        if (x, y) not in solido:
            px[x, y] = (*c, 255)
    return im


# ----------------------------------------------------------------------
#  El icono de la Paralisis: un rayo en zigzag, como datos (fila: de x a x),
#  con el canto apagado, el alma clara y chispas sueltas
# ----------------------------------------------------------------------
P_CANTO, P_MEDIO, P_CLARO, P_NUCLEO = (124, 84, 214), (164, 124, 255), (206, 178, 255), (246, 238, 255)
RAYO_FILAS = {2: (9, 12), 3: (8, 11), 4: (7, 10), 5: (6, 9), 6: (5, 8), 7: (4, 12), 8: (5, 12), 9: (8, 11),
              10: (7, 10), 11: (7, 9), 12: (6, 8), 13: (6, 7), 14: (5, 6), 15: (5, 5)}
P_MOTAS = [(3, 4, P_CLARO), (14, 4, P_MEDIO), (13, 13, P_CLARO), (2, 11, P_MEDIO)]


def icono_paralisis():
    solido = {(x, y) for y, (x0, x1) in RAYO_FILAS.items() for x in range(x0, x1 + 1)}
    im = lienzo(18)
    px = im.load()
    for (x, y) in solido:
        x0, x1 = RAYO_FILAS[y]
        alma = (x0 + x1) / 2
        if y in (7, 8) and 6 <= x <= 9:
            c = P_NUCLEO
        elif any((x + dx, y + dy) not in solido for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c = P_CANTO if abs(x - alma) > 0.6 or x1 - x0 < 2 else P_CLARO
        else:
            c = P_CLARO if abs(x - alma) <= 0.6 else P_MEDIO
        px[x, y] = (*c, 255)
    for x, y, c in P_MOTAS:
        if (x, y) not in solido:
            px[x, y] = (*c, 255)
    return im


polilla().save(os.path.join(ENT, 'polilla.png'))
galon().save(os.path.join(ENT, 'picado_galon.png'))
punta().save(os.path.join(ENT, 'picado_punta.png'))
aro().save(os.path.join(ENT, 'aro.png'))
rayo().save(os.path.join(ENT, 'rayo.png'))
embudo().save(os.path.join(ENT, 'embudo.png'))
for k in range(CUADROS_FURIA):
    aura_furia(k).save(os.path.join(ENT, f'aeralis_furia_{k}.png'))
if os.path.exists(os.path.join(ENT, 'aeralis_furia.png')):
    os.remove(os.path.join(ENT, 'aeralis_furia.png'))
icono_marca().save(os.path.join(EFE, 'marca_vendaval.png'))
icono_paralisis().save(os.path.join(EFE, 'paralisis.png'))
print('ok')

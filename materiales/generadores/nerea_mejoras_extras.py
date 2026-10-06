"""
Las texturas del remake de Nerea (octubre de 2026), pixel a pixel. Todo es
mar: agua, espuma, burbujas, remolinos y la luz que se cuela bajo el agua;
nada de rayos ni de galones (cada jefe tiene lo suyo). La paleta del agua es
la de sus particulas de siempre (nerea_extras.py: 1b8aa6, 3fe0ff, 9ff4ff,
cdeef2, eaffff) con dos tonos hondos debajo.

  textures/entity/nerea/
    ola.png            la pared de agua del Rompeolas y de la Gran Marea: la
                       cresta de espuma arriba y el agua cada vez mas honda
                       hacia abajo, con vetas que bajan (32x64, se repite a lo
                       ancho)
    ola_flujo.png      lo que sube por la cara de la ola: encajes de espuma
                       rotos y burbujas sobre transparente (32x32, se repite en
                       los dos sentidos; el juego lo hace subir deprisa)
    estela.png         el rastro de espuma que dejan las olas en el suelo, con
                       los dos bordes y las burbujas (32x32, se repite a lo largo)
    remolino.png       el remolino del suelo: brazos de espuma que se enroscan
                       hacia la sima del centro (128x128). Lo usan el Remolino
                       y el aviso del Geiser
    columna.png        la columna del Geiser: chorros de agua que suben con
                       borbotones de espuma (32x64, se repite hacia arriba)
    espuma_aro.png     un aro de espuma, irregular, para marcar en el suelo lo
                       que alcanza un golpe: las burbujas, el molino y el ancla
                       (128x128)
    burbuja_aire.png   la burbuja de aire dorada que protege del Remolino a
                       quien lleva una antorcha (32x32)
    rayo_agua.png      el chorro de la Mirada del Abismo: agua que corre con el
                       nucleo claro, en grises para tenirlo de la fase (16x32)
    aro_ojo.png        el aro de agua que gira alrededor de cada ojo mientras
                       mira, en grises (32x32)
    grieta_ojo_N.png   las grietas de los ojos con los impactos (1-4, 16x16)
    sendero.png        el paso que deja la Gran Marea: luz que se cuela bajo el
                       agua, con los dos bordes (32x32, se repite a lo largo)
    corazon_burbuja.png  el corazon maldito dentro de la burbuja bomba (16x16)
    nerea_furia_N.png  el aura de la Furia de las Mareas, dieciseis cuadros
                       sobre el atlas de Nerea: la red de luz que hace el sol
                       bajo el agua (causticas) en verde abismo, que ondula (cada
                       nudo de la red da una vuelta pequena; el juego funde un
                       cuadro con el siguiente)
  textures/particle/
    nerea_chispa_N.png   las salpicaduras (antes chispas de oxido): gotas
                         blancas con su destello
    nerea_polvo_N.png    la rociada (antes polvo de arena): bruma de agua

Volver a pasar nerea_extras.py devolveria las chispas y el polvo de antes.

Uso: python nerea_mejoras_extras.py <raiz del proyecto> [hoja.png]
"""
import math, os, sys, random
import numpy as np
from PIL import Image

RAIZ = sys.argv[1]
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
ENT = os.path.join(A, 'entity/nerea')
PAR = os.path.join(A, 'particle')


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def lienzo(w, h=None):
    return Image.new('RGBA', (w, h or w), (0, 0, 0, 0))


def mezclar(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def con_alfa(c, a):
    return (c[0], c[1], c[2], int(max(0, min(255, a))))


# El agua de Nerea, de lo hondo a la espuma (los cinco de sus particulas y dos mas hondos)
HONDO = hexc('062a36')
OSCURO = hexc('0e4e60')
MEDIO = hexc('1b8aa6')
CLARO = hexc('3fe0ff')
CIELO = hexc('9ff4ff')
NIEBLA = hexc('cdeef2')
ESPUMA = hexc('eaffff')
BLANCO = hexc('ffffff')
ABISMO = hexc('020b12')
ORO = [hexc(c) for c in ('7a4a08', 'b8780e', 'ffc23a', 'ffe08a', 'fffbe0')]


def ruido(w, h, celda, semilla, envolver=True):
    """Ruido suave (bilineal) en [0, 1], que se repite si 'envolver'."""
    r = np.random.default_rng(semilla)
    gw, gh = w // celda, h // celda
    g = r.random((gh + 1, gw + 1))
    if envolver:
        g[-1, :] = g[0, :]
        g[:, -1] = g[:, 0]
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    fx, fy = xx / celda, yy / celda
    x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - x0, fy - y0
    tx = tx * tx * (3 - 2 * tx)
    ty = ty * ty * (3 - 2 * ty)
    a = g[y0, x0] * (1 - tx) + g[y0, x0 + 1] * tx
    b = g[y0 + 1, x0] * (1 - tx) + g[y0 + 1, x0 + 1] * tx
    return a * (1 - ty) + b * ty


# ----------------------------------------------------------------------
#  La pared de agua: la cresta de espuma (que se riza hacia delante: eso lo
#  pone la malla), el labio claro, el cuerpo que se hace hondo hacia abajo con
#  manchas suaves y dos encajes de espuma que la cruzan. Se repite a lo ancho
#  (32 px de lado a lado).
# ----------------------------------------------------------------------
def ola():
    w, h = 32, 64
    im = lienzo(w, h)
    px = im.load()
    n = ruido(w, h, 8, 3)
    fino = ruido(w, h, 4, 9)
    # La cresta: una linea suave que sube y baja una vez por tile (se repite a lo ancho).
    cresta = [4 + 1.6 * math.sin(x / w * math.tau) for x in range(w)]
    for x in range(w):
        for y in range(h):
            c0 = cresta[x]
            if y < c0 - 2.5:
                continue
            if y < c0:
                # la espuma de arriba, seguida, con el borde de arriba algo roto
                if fino[y, x] > 0.25 or y > c0 - 1.7:
                    px[x, y] = con_alfa(BLANCO if fino[y, x] > 0.55 else ESPUMA, 255)
                continue
            t = (y - c0) / (h - c0)                     # 0 en la cresta, 1 abajo
            if t < 0.05:
                c = ESPUMA
            elif t < 0.11:
                c = CIELO
            elif t < 0.30:
                c = mezclar(CLARO, MEDIO, (t - 0.11) / 0.19)
            elif t < 0.62:
                c = mezclar(MEDIO, OSCURO, (t - 0.30) / 0.32)
            else:
                c = mezclar(OSCURO, HONDO, (t - 0.62) / 0.38)
            # El agua no es lisa: manchas suaves mas claras y mas oscuras (nada de vetas:
            # en una pared de 80 bloques se veian como persianas).
            k = (n[y, x] - 0.5) * 0.18
            c = mezclar(c, CIELO if k > 0 else HONDO, abs(k))
            # Encajes de espuma que cruzan la cara de lado a lado, rotos.
            for alto_encaje, grosor in ((0.16, 0.9), (0.33, 0.7)):
                ye = c0 + alto_encaje * (h - c0) + 1.2 * math.sin(x / w * math.tau * 2 + alto_encaje * 9)
                if abs(y - ye) < grosor and fino[y, x] > 0.42:
                    c = mezclar(c, ESPUMA, 0.75 - alto_encaje)
            a = 235 - 70 * t
            px[x, y] = con_alfa(c, a)
    rnd = random.Random(5)
    for _ in range(18):
        x = rnd.randrange(w)
        y = int(cresta[x]) + rnd.randrange(3, 34)
        if y < h:
            px[x, y] = con_alfa(ESPUMA if y < 20 else CIELO, 210)
    return im


# ----------------------------------------------------------------------
#  El flujo de la ola: encajes de espuma rotos que cruzan de lado a lado y
#  burbujas, sobre transparente. El juego lo pinta encima de la ola y lo hace
#  subir por la cara: es lo que da la sensacion de agua que se levanta.
# ----------------------------------------------------------------------
def ola_flujo():
    w = h = 32
    im = lienzo(w, h)
    px = im.load()
    fino = ruido(w, h, 4, 13)
    for y in range(h):
        for x in range(w):
            for k in range(3):
                ye = (k * h / 3 + 2.2 * math.sin(x / w * math.tau * 2 + k * 2.1)) % h
                d = min(abs(y - ye), h - abs(y - ye))
                if d < 0.75 and fino[y, x] > 0.4:
                    px[x, y] = con_alfa(ESPUMA if fino[y, x] > 0.6 else CIELO, 200)
    rnd = random.Random(17)
    for _ in range(12):
        x, y = rnd.randrange(w), rnd.randrange(h)
        px[x, y] = con_alfa(BLANCO, 220)
    return im


# ----------------------------------------------------------------------
#  La estela: los dos bordes de espuma de la ola que paso y burbujas que
#  revientan en medio. Se repite a lo largo (v).
# ----------------------------------------------------------------------
def estela():
    w = h = 32
    im = lienzo(w, h)
    px = im.load()
    n = ruido(w, h, 8, 11)
    for y in range(h):
        for x in range(w):
            borde = min(x, w - 1 - x)
            onda = 1.5 * math.sin(y / h * math.tau * 2 + (0 if x < w / 2 else 2))
            if borde < 3 + onda + 2 * n[y, x]:
                px[x, y] = con_alfa(ESPUMA if n[y, x] > 0.5 else NIEBLA, 215)
            elif n[y, x] > 0.72:
                px[x, y] = con_alfa(CIELO, 120)
            else:
                px[x, y] = con_alfa(CLARO, 34)
    rnd = random.Random(2)
    for _ in range(14):
        x, y = rnd.randrange(6, 26), rnd.randrange(h)
        px[x, y] = con_alfa(BLANCO, 200)
    return im


# ----------------------------------------------------------------------
#  El remolino: cuatro brazos de espuma en espiral logaritmica que se
#  cierran hacia la sima del centro; el agua se hace honda hacia dentro y
#  se apaga hacia fuera.
# ----------------------------------------------------------------------
def remolino():
    s = 128
    im = lienzo(s)
    px = im.load()
    n = ruido(s, s, 16, 7, envolver=False)
    c0 = s / 2
    for y in range(s):
        for x in range(s):
            dx, dy = x + 0.5 - c0, y + 0.5 - c0
            r = math.hypot(dx, dy) / c0                 # 0 en el centro, 1 en el borde
            if r > 1.0:
                continue
            ang = math.atan2(dy, dx)
            brazo = ((ang + 2.6 * math.log(max(r, 0.02)) + 0.6 * n[y, x]) * 4 / math.tau) % 1.0
            fuera = max(0.0, (r - 0.72) / 0.28)         # se apaga hacia el borde
            if r < 0.11:
                c, a = ABISMO, 245
            elif r < 0.2:
                c, a = mezclar(ABISMO, HONDO, (r - 0.11) / 0.09), 240
            elif brazo < 0.16:
                c = ESPUMA if brazo < 0.07 else CIELO
                a = 230
            elif brazo < 0.26:
                c, a = CLARO, 200
            else:
                c = mezclar(HONDO, MEDIO, min(1.0, r * 1.2))
                a = 175
            px[x, y] = con_alfa(c, a * (1.0 - fuera ** 1.5))
    return im


# ----------------------------------------------------------------------
#  La columna del Geiser: chorros verticales (claros en medio de cada uno),
#  agua honda entre ellos y borbotones de espuma. Se repite hacia arriba.
# ----------------------------------------------------------------------
def columna():
    w, h = 32, 64
    im = lienzo(w, h)
    px = im.load()
    n = ruido(w, h, 8, 21)
    for y in range(h):
        for x in range(w):
            chorro = 0.5 + 0.5 * math.sin((x + 2.5 * n[y, x]) / w * math.tau * 3)
            if chorro > 0.86:
                c, a = ESPUMA, 245
            elif chorro > 0.66:
                c, a = CIELO, 225
            elif chorro > 0.4:
                c, a = CLARO, 205
            else:
                c, a = MEDIO, 190
            if n[y, x] > 0.74:
                c, a = BLANCO, 250                      # borbotones
            px[x, y] = con_alfa(c, a)
    return im


# ----------------------------------------------------------------------
#  El aro de espuma: irregular (el ruido lo engorda y lo adelgaza), blanco
#  con el canto cian, y un velo de agua muy tenue por dentro.
# ----------------------------------------------------------------------
def espuma_aro():
    s = 128
    im = lienzo(s)
    px = im.load()
    n = ruido(s, s, 8, 31, envolver=False)
    c0 = s / 2
    for y in range(s):
        for x in range(s):
            r = math.hypot(x + 0.5 - c0, y + 0.5 - c0)
            grueso = 3.0 + 2.2 * n[y, x]
            d = abs(r - (c0 - 6))
            if d < grueso * 0.45:
                px[x, y] = con_alfa(BLANCO if n[y, x] > 0.55 else ESPUMA, 240)
            elif d < grueso:
                px[x, y] = con_alfa(CIELO, 200)
            elif d < grueso + 1.2:
                px[x, y] = con_alfa(CLARO, 130)
            elif r < c0 - 6:
                px[x, y] = con_alfa(CLARO, 22 + int(30 * max(0.0, (r - (c0 - 22)) / 16)))
    return im


# ----------------------------------------------------------------------
#  La burbuja de aire dorada: el canto de oro, el aire calido y translucido
#  dentro, el brillo arriba a la izquierda y dos burbujitas.
# ----------------------------------------------------------------------
def burbuja_aire():
    s = 32
    im = lienzo(s)
    px = im.load()
    c0 = s / 2
    for y in range(s):
        for x in range(s):
            dx, dy = x + 0.5 - c0, y + 0.5 - c0
            r = math.hypot(dx, dy)
            if r > 15.0:
                continue
            luz = -(dx + dy) / 30
            if r > 13.6:
                c, a = ORO[2] if luz > 0 else ORO[1], 235
            elif r > 12.2:
                c, a = ORO[3] if luz > -0.1 else ORO[2], 170
            else:
                c, a = ORO[4], int(28 + 40 * (r / 12.2) ** 2)
            px[x, y] = con_alfa(c, a)
    for (x, y) in ((8, 9), (9, 8), (9, 9), (10, 8), (8, 10), (11, 7), (7, 11)):
        px[x, y] = con_alfa(ORO[4], 250)
    for (x, y, k) in ((20, 19, 2), (22, 23, 1)):
        for ox in range(-k, k + 1):
            for oy in range(-k, k + 1):
                if abs(math.hypot(ox, oy) - k) < 0.7:
                    px[x + ox, y + oy] = con_alfa(ORO[3], 200)
    return im


# ----------------------------------------------------------------------
#  El chorro de la Mirada: el nucleo claro en medio, el canto que se apaga
#  hacia los lados y ondas de agua que corren (v). En grises para tenirlo.
# ----------------------------------------------------------------------
def rayo_agua():
    w, h = 16, 32
    im = lienzo(w, h)
    px = im.load()
    for y in range(h):
        for x in range(w):
            u = (x + 0.5) / w - 0.5
            onda = 0.08 * math.sin(y / h * math.tau * 2)
            d = abs(u - onda)
            if d < 0.1:
                v, a = 255, 255
            elif d < 0.22:
                v, a = 225, 230
            elif d < 0.36:
                v, a = 175, 150
            elif d < 0.5:
                v, a = 140, 60
            else:
                continue
            if (y * 3 + x * 5) % 13 == 0 and d > 0.1:
                v = 245                                 # gotas que corren por el borde
            px[x, y] = (v, v, v, a)
    return im


# ----------------------------------------------------------------------
#  El aro de agua alrededor de cada ojo: un anillo con tres gotas que
#  giran (la malla lo hace girar). En grises.
# ----------------------------------------------------------------------
def aro_ojo():
    s = 32
    im = lienzo(s)
    px = im.load()
    c0 = s / 2
    for y in range(s):
        for x in range(s):
            dx, dy = x + 0.5 - c0, y + 0.5 - c0
            r = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            grueso = 1.1 + 0.6 * math.sin(ang * 3)
            if abs(r - 12.5) < grueso:
                v = 255 if abs(r - 12.5) < grueso * 0.5 else 200
                px[x, y] = (v, v, v, 235)
    for k in range(3):
        a = k * math.tau / 3
        gx, gy = c0 + math.cos(a) * 12.5, c0 + math.sin(a) * 12.5
        for y in range(s):
            for x in range(s):
                if math.hypot(x + 0.5 - gx, y + 0.5 - gy) < 2.2:
                    px[x, y] = (255, 255, 255, 255)
    return im


# ----------------------------------------------------------------------
#  Las grietas del ojo: cuatro etapas, cada una suma ramas a la anterior,
#  oscuras con el canto un poco mas claro para que se lean sobre el brillo.
# ----------------------------------------------------------------------
RAMAS = [
    [(8, 8), (10, 6), (12, 5), (14, 3)],
    [(8, 8), (6, 10), (5, 12), (3, 13)],
    [(8, 8), (5, 7), (3, 6), (1, 7)],
    [(8, 8), (10, 11), (12, 12), (13, 15)],
]


def grieta_ojo(n):
    s = 16
    im = lienzo(s)
    px = im.load()
    puntos = set()
    for rama in RAMAS[:n]:
        for (x0, y0), (x1, y1) in zip(rama, rama[1:]):
            pasos = max(abs(x1 - x0), abs(y1 - y0))
            for k in range(pasos + 1):
                puntos.add((round(x0 + (x1 - x0) * k / pasos), round(y0 + (y1 - y0) * k / pasos)))
    for (x, y) in puntos:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in puntos and 0 <= q[0] < s and 0 <= q[1] < s:
                px[q] = con_alfa(OSCURO, 150)
    for (x, y) in puntos:
        px[x, y] = con_alfa(ABISMO, 245)
    return im


# ----------------------------------------------------------------------
#  El sendero de la Gran Marea: causticas (la red de luz que hace el sol bajo
#  el agua) en aguamarina clara, y los dos bordes bien marcados.
# ----------------------------------------------------------------------
def causticas(w, h, semilla, celda, desplaza=(0.0, 0.0), giro=None, onda=0.0):
    """Distancia al borde mas cercano de una red de Voronoi que se repite:
    pequena cerca de las lineas de luz. Devuelve un array en [0, 1]. Con
    "giro" (radianes), cada nudo se aparta "onda" pixeles por su propio
    circulo: una vuelta entera vuelve a la red del principio."""
    r = np.random.default_rng(semilla)
    nx, ny = w // celda, h // celda
    pts = []
    for j in range(ny):
        for i in range(nx):
            # en el medio de su celda: dos nudos casi juntos dejaban una mancha llena de luz
            px_, py_ = (i + 0.25 + 0.5 * r.random()) * celda, (j + 0.25 + 0.5 * r.random()) * celda
            pts.append((px_, py_))
    pts = np.array(pts)
    if giro is not None:
        fases = r.random(len(pts)) * 2 * np.pi
        sentido = np.where(r.random(len(pts)) < 0.5, -1.0, 1.0)
        pts = pts + onda * np.stack([np.cos(fases + sentido * giro), np.sin(fases + sentido * giro)], axis=1)
    pts = pts + np.array(desplaza)
    yy, xx = np.mgrid[0:h, 0:w].astype(float) + 0.5
    d1 = np.full((h, w), 1e9)
    d2 = np.full((h, w), 1e9)
    for (px_, py_) in pts:
        for ox in (-w, 0, w):
            for oy in (-h, 0, h):
                d = np.hypot(xx - (px_ + ox), yy - (py_ + oy))
                menor = d < d1
                d2 = np.where(menor, d1, np.minimum(d2, d))
                d1 = np.where(menor, d, d1)
    return np.clip((d2 - d1) / celda, 0, 1)


def sendero():
    w = h = 32
    im = lienzo(w, h)
    px = im.load()
    k = causticas(w, h, 41, 8)
    for y in range(h):
        for x in range(w):
            borde = min(x, w - 1 - x)
            if borde < 2:
                px[x, y] = con_alfa(ESPUMA if borde == 0 else CIELO, 235)
            elif k[y, x] < 0.09:
                px[x, y] = con_alfa(ESPUMA, 210)
            elif k[y, x] < 0.2:
                px[x, y] = con_alfa(CIELO, 140)
            else:
                px[x, y] = con_alfa(CLARO, 46)
    return im


# ----------------------------------------------------------------------
#  El corazon dentro de la burbuja: magenta, con el lobulo claro y una
#  grieta; el contorno calculado.
# ----------------------------------------------------------------------
def corazon_burbuja():
    s = 16
    im = lienzo(s)
    px = im.load()
    forma = set()
    for j in range(s):
        for i in range(s):
            x = (i + 0.5 - 8) / 5.6
            y = -(j + 0.5 - 8) / 5.6 + 0.2
            if (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0:
                forma.add((i, j))
    rampa = [hexc(c) for c in ('5a0a2a', 'a0124a', 'e0144c', 'ff5a8a', 'ffd0e0')]
    for (i, j) in forma:
        borde = any((i + a, j + b) not in forma for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        d = math.hypot(i - 5.5, j - 5.5)
        c = rampa[0] if borde else rampa[4] if d < 1.5 else rampa[3] if d < 3.2 else rampa[2] if d < 5.5 else rampa[1]
        px[i, j] = c
    for (i, j) in ((9, 6), (9, 7), (10, 8), (9, 9), (10, 10)):
        if (i, j) in forma:
            px[i, j] = rampa[0]
    return im


# ----------------------------------------------------------------------
#  El aura de la Furia: sobre el mismo atlas de Nerea (solo donde hay piel),
#  la red de causticas en verde abismo, con las lineas casi blancas; dieciseis
#  cuadros en los que cada nudo de la red da una vuelta pequena (ondula como la
#  luz bajo el agua y el ultimo empalma con el primero). Fuera, transparente.
# ----------------------------------------------------------------------
CUADROS_FURIA = 16


def aura_furia(cuadro):
    base = np.array(Image.open(os.path.join(ENT, 'nerea_f1.png')).convert('RGBA'))
    h, w = base.shape[:2]
    # La red se calcula en un lienzo de 128x256 y se amplia: lineas finas que
    # dejan ver el cuerpo debajo (con las gruesas se veia todo verde).
    k = causticas(128, 256, 77, 16, giro=2 * math.pi * cuadro / CUADROS_FURIA, onda=2.5)
    k = np.array(Image.fromarray((k * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)).astype(float) / 255
    out = np.zeros((h, w, 4), np.uint8)
    out[k < 0.1] = (8, 120, 92, 70)
    out[k < 0.055] = (32, 240, 176, 170)
    out[k < 0.022] = (214, 255, 240, 240)
    out[base[..., 3] < 16] = 0
    return Image.fromarray(out)


# ----------------------------------------------------------------------
#  Particulas: las salpicaduras (en lugar de las chispas) y la rociada (en
#  lugar del polvo). Mismos tamanos y cuadros que las de antes.
# ----------------------------------------------------------------------
def salpicadura(l):
    """Una gota con su destello en cruz, de mas a menos (8x8)."""
    im = lienzo(8)
    px = im.load()
    for y in range(8):
        for x in range(8):
            d = abs(x - 3.5) + abs(y - 3.5)
            cruz = (abs(x - 3.5) < 0.6 or abs(y - 3.5) < 0.6) and d < l + 0.6
            if d < l * 0.55:
                px[x, y] = BLANCO
            elif d < l * 0.85:
                px[x, y] = ESPUMA
            elif cruz:
                px[x, y] = CIELO
    return im


def rociada(f):
    """Una nube de agua pulverizada que se abre y se aclara (8x8)."""
    im = lienzo(8)
    px = im.load()
    rnd = random.Random(50 + f)
    r = 1.8 + f * 0.6
    for y in range(8):
        for x in range(8):
            d = math.hypot(x + 0.5 - 4, y + 0.5 - 4) + rnd.random() * 0.9
            if d < r:
                c = ESPUMA if d < r * 0.45 else NIEBLA if d < r * 0.8 else CIELO
                px[x, y] = con_alfa(c, 210 - f * 35)
    return im


IMGS = {
    'ola': ola(), 'ola_flujo': ola_flujo(), 'estela': estela(), 'remolino': remolino(), 'columna': columna(),
    'espuma_aro': espuma_aro(), 'burbuja_aire': burbuja_aire(), 'rayo_agua': rayo_agua(), 'aro_ojo': aro_ojo(),
    'sendero': sendero(), 'corazon_burbuja': corazon_burbuja(),
}
for n in range(1, 5):
    IMGS[f'grieta_ojo_{n}'] = grieta_ojo(n)
for nombre, im in IMGS.items():
    im.save(os.path.join(ENT, nombre + '.png'))
for k in range(CUADROS_FURIA):
    aura_furia(k).save(os.path.join(ENT, f'nerea_furia_{k}.png'))
for i, l in enumerate((3.5, 2.5, 1.5)):
    salpicadura(l).save(os.path.join(PAR, f'nerea_chispa_{i}.png'))
for f in range(4):
    rociada(f).save(os.path.join(PAR, f'nerea_polvo_{f}.png'))

# ----------------------------------------------------------------------
#  Hoja de control: todo ampliado sobre fondo oscuro y sobre piedra
# ----------------------------------------------------------------------
if len(sys.argv) > 2:
    from PIL import ImageDraw
    piezas = list(IMGS.items()) + [(f'chispa_{i}', Image.open(os.path.join(PAR, f'nerea_chispa_{i}.png'))) for i in range(3)] \
        + [(f'polvo_{f}', Image.open(os.path.join(PAR, f'nerea_polvo_{f}.png'))) for f in range(4)]
    K = 4
    filas = []
    x = y = 10
    alto_fila = 0
    hoja = Image.new('RGBA', (1500, 1100), (34, 44, 52, 255))
    d = ImageDraw.Draw(hoja)
    for nombre, im in piezas:
        k = K if im.width >= 32 else 8
        g = im.resize((im.width * k, im.height * k), Image.NEAREST)
        if x + g.width > 1490:
            x = 10
            y += alto_fila + 22
            alto_fila = 0
        fondo = Image.new('RGBA', g.size, (34, 44, 52, 255))
        # medio fondo de piedra para ver la transparencia sobre algo claro
        fp = Image.new('RGBA', (g.width, g.height // 2), (125, 125, 125, 255))
        fondo.paste(fp, (0, g.height // 2))
        fondo.alpha_composite(g)
        hoja.alpha_composite(fondo, (x, y))
        d.text((x, y + g.height + 4), nombre, fill=(255, 255, 255, 255))
        x += g.width + 14
        alto_fila = max(alto_fila, g.height)
    furia = Image.open(os.path.join(ENT, 'nerea_furia_0.png'))
    base = Image.open(os.path.join(ENT, 'nerea_f1.png')).convert('RGBA')
    mezcla = base.copy()
    mezcla.alpha_composite(furia)
    y += alto_fila + 30
    hoja.alpha_composite(mezcla.resize((256, 512), Image.NEAREST).crop((0, 0, 256, 1100 - y - 10 if 1100 - y - 10 < 512 else 512)), (10, y))
    hoja.save(sys.argv[2])
print('ok')

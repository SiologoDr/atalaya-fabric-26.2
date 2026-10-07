"""
Las texturas de las mejoras de Rajang de octubre de 2026, pixel a pixel y con
la rampa de jade de sus otras marcas de suelo (rajang_extras.py): nada se
difumina, cada linea es de pixeles enteros.

  textures/entity/rajang/
                       tumba_borde.png   el borde de la Tumba de Raices: el aro, las
                       tumba_borde_aviso.png  muescas y cuatro flechas hacia fuera (por
                                         donde hay que salir); el _aviso es el
                                         parpadeo del ultimo segundo
                       tumba_borde_anillo.png  el borde de la Tumba en anillo: el mismo,
                       tumba_borde_anillo_aviso.png  con las flechas hacia DENTRO (hacia el)
                       tumba_seguro.png  el circulo dorado de la Tumba en anillo: donde
                                         se salva (testers, 07-10-2026)
                       tumba_raiz.png    lo llenado: raices que salen del centro y
                                         el frente encendido (crece en el juego)
                                         Los tres los pinta RajangRenderer tumbados
                                         (no son particulas: una de 72 bloques
                                         desaparecia al salir su centro de la vista)
                       flecha.png        un galon de la flecha de la Embestida con los
                                         dos filetes (se repite a lo largo; v crece
                                         hacia donde va a cargar)
                       flecha_punta.png  la punta
                       rombo.png         un rombo de las filas de los pinchos
                       rajang_furia.png  las bandas del aura de la Furia (se suman
                                         encima del cuerpo, como la carga del creeper)
  textures/gui/        rajang_barra_furia.png  "FURIA" en letras de pixel, en grises
                                         para tenirlo (como "FASE I")

Uso: python rajang_mejoras_extras.py <raiz del proyecto> [vista_previa.png]
"""
import math, os, random, sys
from PIL import Image

RAIZ = sys.argv[1]
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
ENT = os.path.join(A, 'textures/entity/rajang')
GUI = os.path.join(A, 'textures/gui')
TAU = 2 * math.pi
rnd = random.Random(2610)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def alfa(c, a):
    return c[:3] + (a,)


# La rampa de jade de las marcas de suelo de Rajang (la del aviso y el Sello)
J1, J2, J3, J4, J5 = (hexc(c) for c in ('143a27', '1c4e34', '266444', '387a56', '3aa866'))
JADE = hexc('58c886')
VERDE = hexc('8cff5a')
LIMA = hexc('c8ff2a')
LIMA_CLARO = hexc('e6ff4a')
NUCLEO = hexc('f2ffe0')


def lienzo(w, h=None):
    return Image.new('RGBA', (w, h or w), (0, 0, 0, 0))


# ----------------------------------------------------------------------
#  El borde de la Tumba: el aro de dos pixeles, el filete de dentro a trozos,
#  dieciseis muescas hacia dentro y, en los cuatro puntos, una flecha que
#  apunta hacia fuera. En el parpadeo, todo un tono mas claro y el aro mas grueso.
# ----------------------------------------------------------------------
def borde_tumba(encendido, hacia_dentro=False):
    n = 64
    im = lienzo(n)
    q = im.load()
    c = (n - 1) / 2
    aro_fuera, aro_dentro = (LIMA, VERDE) if encendido else (VERDE, J5)
    for y in range(n):
        for x in range(n):
            r = math.hypot(x - c, y - c)
            a = math.atan2(y - c, x - c)
            if 30.0 <= r < 31.6:
                q[x, y] = aro_fuera
            elif 28.8 <= r < 30.0 or (encendido and 28.0 <= r < 28.8):
                q[x, y] = aro_dentro
            elif 26.2 <= r < 27.2 and int((a + math.pi) / TAU * 48) % 2 == 0:
                q[x, y] = alfa(JADE, 220)
            # las muescas: dientes cortos hacia dentro, cada 22,5 grados
            elif 25.0 <= r < 28.8 and abs(((a / TAU * 16) % 1.0) - 0.5) < 0.09:
                q[x, y] = J5 if not encendido else JADE
    # cuatro flechas hacia fuera, entre el filete y el aro: la punta (fila 0) es
    # lo de mas fuera y cada fila hacia dentro es un pixel mas ancha. En la Tumba
    # en anillo, al reves: la punta hacia dentro (hay que ir hacia el)
    for k in range(4):
        ang = k * math.pi / 2 + math.pi / 4
        ux, uy = math.cos(ang), math.sin(ang)
        px, py = -uy, ux
        for fila in range(5):
            d = 20.0 + fila if hacia_dentro else 24.0 - fila
            for s in range(-fila, fila + 1):
                x = round(c + ux * d + px * s * 0.9)
                y = round(c + uy * d + py * s * 0.9)
                if 0 <= x < n and 0 <= y < n:
                    q[x, y] = (LIMA_CLARO if encendido else LIMA) if abs(s) == fila else (VERDE if encendido else JADE)
    return im


borde_tumba(False).save(os.path.join(ENT, 'tumba_borde.png'))
borde_tumba(True).save(os.path.join(ENT, 'tumba_borde_aviso.png'))
borde_tumba(False, True).save(os.path.join(ENT, 'tumba_borde_anillo.png'))
borde_tumba(True, True).save(os.path.join(ENT, 'tumba_borde_anillo_aviso.png'))


# ----------------------------------------------------------------------
#  El circulo seguro de la Tumba en anillo: en oro (el de su mascara), para
#  que no se confunda con el jade de lo que mata. El aro de dos tonos, el
#  filete a trozos y dentro un velo dorado flojo: ahi no llegan las raices.
# ----------------------------------------------------------------------
O1, O2, O3, O4, O5 = (hexc(c) for c in ('5a3a0c', '8a5a12', 'c08a1c', 'ffc23a', 'fff0a8'))


def seguro_tumba():
    n = 64
    im = lienzo(n)
    q = im.load()
    c = (n - 1) / 2
    for y in range(n):
        for x in range(n):
            r = math.hypot(x - c, y - c)
            a = math.atan2(y - c, x - c)
            if 30.0 <= r < 31.6:
                q[x, y] = O4
            elif 28.8 <= r < 30.0:
                q[x, y] = O3
            elif 26.2 <= r < 27.2 and int((a + math.pi) / TAU * 40) % 2 == 0:
                q[x, y] = alfa(O5, 230)
            elif r < 28.8:
                q[x, y] = alfa(O2, 40 + int(30 * r / 28.8))
    return im


seguro_tumba().save(os.path.join(ENT, 'tumba_seguro.png'))


# ----------------------------------------------------------------------
#  Lo llenado: el disco en verde oscuro translucido, la red de raices que
#  sale del centro (lineas de pixel, mas claras cuanto mas lejos) y el frente
#  encendido en el borde, que es lo que avanza al crecer.
# ----------------------------------------------------------------------
def raiz():
    n = 64
    im = lienzo(n)
    q = im.load()
    c = (n - 1) / 2
    for y in range(n):
        for x in range(n):
            r = math.hypot(x - c, y - c)
            if r < 29.5:
                q[x, y] = alfa(J2, 70 + int(40 * r / 29.5))
            elif r < 31.6:
                q[x, y] = VERDE if r >= 30.4 else LIMA
    # las raices: doce brazos quebrados desde el centro, con alguna rama
    puntos = []
    for k in range(12):
        a = TAU * k / 12 + rnd.uniform(-0.12, 0.12)
        x, y = c, c
        r = 0.0
        while r < 28.5:
            a += rnd.uniform(-0.35, 0.35)
            paso = rnd.uniform(2.5, 4.5)
            nx, ny = x + math.cos(a) * paso, y + math.sin(a) * paso
            for s in range(8):
                px, py = round(x + (nx - x) * s / 8), round(y + (ny - y) * s / 8)
                puntos.append((px, py, r))
            if rnd.random() < 0.25:
                b = a + rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.0)
                for s in range(1, 5):
                    puntos.append((round(nx + math.cos(b) * s), round(ny + math.sin(b) * s), r + s))
            x, y = nx, ny
            r = math.hypot(x - c, y - c)
    for px, py, r in puntos:
        if 0 <= px < n and 0 <= py < n and math.hypot(px - c, py - c) < 29.5:
            q[px, py] = J5 if r < 10 else JADE if r < 20 else VERDE
    q[round(c), round(c)] = NUCLEO
    return im


raiz().save(os.path.join(ENT, 'tumba_raiz.png'))


# ----------------------------------------------------------------------
#  La flecha de la Embestida (se pinta tumbada; v crece hacia donde carga)
# ----------------------------------------------------------------------
def galon():
    """Un tramo: los dos filetes de los lados, el fondo verde oscuro
    translucido y un galon (una V que apunta hacia delante)."""
    w, h = 32, 32
    im = lienzo(w, h)
    q = im.load()
    for y in range(h):
        for x in range(w):
            q[x, y] = alfa(J2, 90)
            if x in (0, 31):
                q[x, y] = J5
            elif x in (1, 30):
                q[x, y] = VERDE
    # la V: de las esquinas de arriba al centro de abajo, tres pixeles de grueso
    for y in range(4, 26):
        k = (y - 4) / 21
        for lado in (-1, 1):
            xc = 15.5 + lado * (12.5 * (1 - k))
            for d in (-1, 0, 1):
                x = round(xc + d)
                if 2 <= x < 30:
                    q[x, y] = VERDE if d == 0 else JADE
    for y in range(24, 27):
        for x in range(14, 18):
            q[x, y] = LIMA if y == 25 else VERDE
    return im


def punta():
    """La punta: un triangulo que apunta hacia delante, con el filete claro."""
    w, h = 32, 32
    im = lienzo(w, h)
    q = im.load()
    for y in range(2, 31):
        k = (y - 2) / 28
        mitad = 15.0 * (1 - k)
        for x in range(w):
            d = abs(x - 15.5)
            if d <= mitad:
                borde = mitad - d < 1.6 or y < 4
                q[x, y] = VERDE if borde else (JADE if d > mitad * 0.45 else LIMA if d < 1.0 else JADE)
    return im


def rombo():
    """Un rombo de la fila de los pinchos: canto oscuro, nucleo claro."""
    w, h = 16, 32
    im = lienzo(w, h)
    q = im.load()
    for y in range(h):
        for x in range(w):
            d = abs(x - 7.5) / 6.5 + abs(y - 15.5) / 10.5
            if d <= 1.0:
                q[x, y] = J5 if d > 0.82 else JADE if d > 0.55 else VERDE if d > 0.25 else LIMA
    return im


galon().save(os.path.join(ENT, 'flecha.png'))
punta().save(os.path.join(ENT, 'flecha_punta.png'))
rombo().save(os.path.join(ENT, 'rombo.png'))


# ----------------------------------------------------------------------
#  El aura de la Furia: bandas onduladas en diagonal, verde vivo sobre negro
#  (se SUMAN encima del cuerpo: el negro no anade nada). El atlas del cuerpo
#  es de 1024: con 256 aqui, una banda cada ~8 pixeles de malla, dos o tres
#  por cara de bloque.
# ----------------------------------------------------------------------
def aura():
    n = 256
    im = Image.new('RGBA', (n, n), (0, 0, 0, 255))
    q = im.load()
    for y in range(n):
        for x in range(n):
            s = (x + y + 2.0 * math.sin(TAU * y / 32.0)) % 8.0
            if s < 1.0:
                q[x, y] = (150, 255, 110, 255)
            elif s < 2.5:
                q[x, y] = (70, 190, 70, 255)
            elif s < 3.5:
                q[x, y] = (24, 80, 34, 255)
    return im


aura().save(os.path.join(ENT, 'rajang_furia.png'))


# ----------------------------------------------------------------------
#  "FURIA" para la barra, con las letras de rajang_hud.py (mas la U)
# ----------------------------------------------------------------------
GLIFOS = {
    'A': [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    'F': ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    'I': ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    'R': ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    'U': ["##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
}


def palabra(texto, relleno, borde, sombra, ancho=None, derecha=False):
    """La misma que rajang_hud.py: relleno, contorno de un pixel y sombra."""
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
    h = 10
    ox = (w - w_txt if derecha else 0) + 1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    q = im.load()
    for (px, py) in puntos:
        for dx in (0, 1, -1):
            xx, yy = px + ox + dx, py + 3
            if 0 <= xx < w and 0 <= yy < h:
                q[xx, yy] = sombra
    for (px, py) in puntos:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = px + ox + dx, py + 1 + dy
                if 0 <= xx < w and 0 <= yy < h and (px + dx, py + dy) not in puntos:
                    q[xx, yy] = borde
    for (px, py) in puntos:
        q[px + ox, py + 1] = relleno(px, py)
    return im


def gris(fx, fila):
    v = [255, 246, 236, 224, 210, 196, 182][fila]
    return (v, v, v, 255)


palabra('FURIA', gris, hexc('04100a'), (0, 0, 0, 110), 64, True).save(os.path.join(GUI, 'rajang_barra_furia.png'))

# ----------------------------------------------------------------------
#  Vista previa: todo ampliado, sobre fondo oscuro y sobre tierra
# ----------------------------------------------------------------------
if len(sys.argv) > 2:
    piezas = [Image.open(os.path.join(ENT, n + '.png')) for n in ('tumba_borde', 'tumba_borde_aviso', 'tumba_raiz')]
    piezas += [Image.open(os.path.join(ENT, n + '.png')) for n in ('flecha', 'flecha_punta', 'rombo')]
    piezas += [Image.open(os.path.join(GUI, 'rajang_barra_furia.png'))]
    k = 5
    W = sum(p.width * k + 16 for p in piezas) + 16
    H = max(p.height * k for p in piezas) * 2 + 40
    prev = Image.new('RGBA', (W, H + 280), (40, 44, 38, 255))
    x = 16
    for p in piezas:
        g = p.convert('RGBA').resize((p.width * k, p.height * k), Image.NEAREST)
        prev.alpha_composite(g, (x, 16))
        tierra = Image.new('RGBA', g.size, (112, 98, 74, 255))
        tierra.alpha_composite(g)
        prev.alpha_composite(tierra, (x, 24 + g.height))
        x += g.width + 16
    # la flecha montada: tres galones y la punta, como en el juego
    f = Image.open(os.path.join(ENT, 'flecha.png'))
    pu = Image.open(os.path.join(ENT, 'flecha_punta.png'))
    tira = Image.new('RGBA', (32, 32 * 3 + 32), (0, 0, 0, 0))
    for i in range(3):
        tira.alpha_composite(f, (0, 32 * i))
    tira.alpha_composite(pu, (0, 96))
    tira = tira.rotate(90, expand=True).resize((128 * 2, 32 * 2), Image.NEAREST)
    prev.alpha_composite(tira, (16, H + 20))
    au = Image.open(os.path.join(ENT, 'rajang_furia.png')).crop((0, 0, 64, 64)).resize((256, 256), Image.NEAREST)
    prev.alpha_composite(au, (300, H + 10))
    prev.save(sys.argv[2])
print('ok')

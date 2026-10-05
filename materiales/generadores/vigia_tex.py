"""
Textura del Vigia: 128x64, cuadricula UV identica a VigiaModel.java.

Una caja (w,h,d) en texOffs (u,v) se despliega asi:
    arriba   (u+d,     v)     w x d
    abajo    (u+d+w,   v)     w x d
    lado A   (u,       v+d)   d x h
    frente   (u+d,     v+d)   w x h      <- cara -Z, la que mira el bicho
    lado B   (u+d+w,   v+d)   d x h
    espalda  (u+2d+w,  v+d)   w x h
"""
from PIL import Image
import random, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 128, 64
rnd = random.Random(7)

def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)

# --- Rampas (borde -> nucleo), 4-5 pasos como pide DISENO.md ---
TELA   = [hexc(c) for c in ('1d1a22', '2a2631', '38333f', '48424f', '5a5363')]
HUESO  = [hexc(c) for c in ('4f4839', '7a705b', 'a39880', 'c7bda3', 'e2d9c0')]
HIERRO = [hexc(c) for c in ('231f1c', '3a332d', '554638', '7a5a3c', 'a8683a')]  # el ultimo es oxido
ASTA   = [hexc(c) for c in ('3d3226', '5c4b37', '7f6a4d', 'a48c67', 'c9b48d')]
CAVIDAD = hexc('120e10')
CRISTAL = [hexc(c) for c in ('2a1d12', '3a2816', '4a321a')]
TRANSP = (0, 0, 0, 0)

img = Image.new('RGBA', (W, H), TRANSP)
px = img.load()

def rect(x, y, w, h, fn):
    for j in range(h):
        for i in range(w):
            c = fn(i, j, w, h)
            if c is not None:
                px[x + i, y + j] = c

def grano(rampa, lo=1, hi=3):
    """Ruido de pocos tonos: rampa escalonada, no degradado continuo."""
    return lambda i, j, w, h: rampa[rnd.randint(lo, hi)]

def caja(u, v, w, h, d, caras):
    """caras: dict con 'arriba','abajo','a','frente','b','espalda' -> fn."""
    pos = {
        'arriba':  (u + d, v, w, d),
        'abajo':   (u + d + w, v, w, d),
        'a':       (u, v + d, d, h),
        'frente':  (u + d, v + d, w, h),
        'b':       (u + d + w, v + d, d, h),
        'espalda': (u + 2 * d + w, v + d, w, h),
    }
    for k, fn in caras.items():
        if k == '*':
            continue
    for k, (x, y, ww, hh) in pos.items():
        fn = caras.get(k, caras.get('*'))
        if fn and ww > 0 and hh > 0:
            rect(x, y, ww, hh, fn)

# ------------------------------------------------------------------
# Cabeza: farol de hierro oxidado con cristal ahumado
# ------------------------------------------------------------------
def farol_lado(i, j, w, h):
    if i == 0 or j == 0 or i == w - 1 or j == h - 1:
        # marco: hierro con alguna mancha de oxido
        return HIERRO[4] if rnd.random() < 0.18 else HIERRO[2 if (i + j) % 3 else 3]
    if i == w // 2 or i == w // 2 - 1:
        if j == h // 2:
            return HIERRO[3]
    # cristal ahumado, mas oscuro abajo (hollin)
    return CRISTAL[2 if j < h // 2 else (1 if rnd.random() < .7 else 0)]

def farol_tapa(i, j, w, h):
    if i == 0 or j == 0 or i == w - 1 or j == h - 1:
        return HIERRO[2]
    return HIERRO[1] if (i + j) % 2 else HIERRO[2] if rnd.random() < .5 else HIERRO[4]

caja(0, 0, 8, 8, 8, {'*': farol_lado, 'arriba': farol_tapa, 'abajo': farol_tapa})

# Cuello: vertebras
def vertebra(i, j, w, h):
    return HUESO[3] if j % 2 == 0 else HUESO[1]
caja(32, 0, 3, 5, 3, {'*': vertebra})

# Ojo: la cara frontal es lo que se ve; iris claro, pupila en ranura
def ojo_frente(i, j, w, h):
    if i in (1, 2) and j in (1, 2):
        return hexc('2b0d05')  # pupila: punto de 2x2, no ranura, o se lee como dos ojos
    return hexc('e3a52c') if j in (1, 2) else hexc('b8741d')
caja(32, 8, 4, 4, 1, {'*': lambda i, j, w, h: hexc('b8741d'), 'frente': ojo_frente})

# Astas
caja(44, 0, 1, 7, 1, {'*': lambda i, j, w, h: ASTA[4] if j < 2 else ASTA[3] if j < 5 else ASTA[2]})
caja(48, 0, 1, 3, 1, {'*': lambda i, j, w, h: ASTA[4] if j == 0 else ASTA[3]})

# ------------------------------------------------------------------
# Torso: costillar abierto por delante, envuelto en tela por detras
# ------------------------------------------------------------------
def costillar(i, j, w, h):
    eje = w // 2
    if i in (eje - 1, eje):                 # esternon
        return HUESO[3] if j % 3 else HUESO[2]
    if j < 2:                               # clavicula
        return HUESO[2] if i in (0, w - 1) else HUESO[3]
    if j >= h - 3:                          # faja de tela a la cintura
        return TELA[2] if (i + j) % 3 else TELA[1]
    if j % 3 == 0:                          # costilla
        return HUESO[4] if 2 < i < w - 3 else HUESO[2]
    if j % 3 == 1 and i in (1, w - 2):
        return HUESO[1]
    return CAVIDAD                          # hueco: el rescoldo lo pone la capa de brillo

def tela(i, j, w, h):
    pliegue = (i % 3 == 0)
    base = 1 if pliegue else 2
    if rnd.random() < 0.15:
        base += 1
    return TELA[min(base, 4)]

caja(0, 16, 10, 16, 6, {'*': tela, 'frente': costillar})

# Brazo: hueso con vendas
def brazo_superior(i, j, w, h):
    if j % 5 in (0, 1):
        return TELA[3] if j % 5 == 0 else TELA[2]
    return HUESO[2] if i == 0 else HUESO[3]
caja(32, 16, 3, 14, 3, {'*': brazo_superior})

def antebrazo(i, j, w, h):
    if j < 3:
        return TELA[3]
    return HUESO[3] if (i + j) % 4 else HUESO[2]
caja(44, 16, 2, 14, 2, {'*': antebrazo})

# Garras: oscurecen hacia la punta
caja(52, 16, 1, 6, 1, {'*': lambda i, j, w, h: HUESO[4] if j < 2 else HUESO[2] if j < 4 else hexc('3a3128')})

# Hombreras: harapos gruesos
caja(88, 0, 4, 3, 5, {'*': tela, 'arriba': lambda i, j, w, h: TELA[3] if (i + j) % 2 else TELA[4]})

# ------------------------------------------------------------------
# Piernas: zancos de hueso, pies como pezunas
# ------------------------------------------------------------------
def muslo(i, j, w, h):
    if j < 4:
        return TELA[2] if (i + j) % 2 else TELA[3]
    return HUESO[3] if i % 3 else HUESO[2]
caja(0, 40, 3, 11, 3, {'*': muslo})
caja(12, 40, 2, 11, 2, {'*': lambda i, j, w, h: HUESO[3] if (j // 2) % 3 else HUESO[2]})
caja(20, 40, 3, 2, 5, {'*': lambda i, j, w, h: hexc('2b2520') if j else hexc('3d352d')})

# ------------------------------------------------------------------
# Capa: plano de grosor cero, bajo deshilachado
# ------------------------------------------------------------------
def capa(i, j, w, h):
    # jirones: cada columna acaba a una altura distinta
    largo = [18, 16, 17, 14, 18, 15, 17, 13, 16, 18][i]
    if j >= largo:
        return None
    if j >= largo - 1 and rnd.random() < 0.5:
        return TELA[0]
    pliegue = (i % 3 == 1)
    return TELA[1 if pliegue else 2] if j > 3 else TELA[3]
rect(64, 0, 10, 18, capa)
# la cara de atras es la misma tela, reflejada para que los jirones casen
for j in range(18):
    for i in range(10):
        px[74 + i, j] = px[64 + 9 - i, j]

img.save(os.path.join(OUT, 'vigia.png'))

# ------------------------------------------------------------------
# Capas de brillo: solo los pixeles que alumbran. Dos colores: calma y caza.
# ------------------------------------------------------------------
def brillo(nombre, iris, nucleo, rescoldo, farol):
    g = Image.new('RGBA', (W, H), TRANSP)
    q = g.load()
    # ojo, cara frontal en (33,9) 4x4
    for j in range(4):
        for i in range(4):
            if i in (1, 2) and j in (1, 2):
                continue  # la pupila no alumbra
            q[33 + i, 9 + j] = nucleo if (i in (1, 2) or j in (1, 2)) else iris
    # el cristal del farol deja escapar un poco de luz por los cuatro lados
    for (fx, fy) in ((0, 8), (8, 8), (16, 8), (24, 8)):
        for j in range(1, 7):
            for i in range(1, 7):
                if j >= 4 and rnd.random() < 0.55:
                    q[fx + i, fy + j] = farol
    # rescoldo entre las costillas
    for j in range(2, 13):
        for i in range(1, 9):
            x, y = 6 + i, 22 + j
            if px[x, y] == CAVIDAD:
                centro = abs(i - 4.5) < 2.2 and 4 < j < 11
                if centro or rnd.random() < 0.25:
                    q[x, y] = rescoldo if centro else farol
    g.save(os.path.join(OUT, nombre))

brillo('vigia_ojo.png', hexc('ffb43a'), hexc('fff0a8'), hexc('c86a14'), hexc('6a3a0c'))
brillo('vigia_ojo_caza.png', hexc('ff3a24'), hexc('ffd2c0'), hexc('d01e10'), hexc('701008'))
print('ok')

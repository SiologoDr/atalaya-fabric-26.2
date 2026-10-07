"""
Todo lo pequeno de Novilis, el Caballero Solar, que no es su cuerpo, pintado
aqui pixel a pixel (nada de vanilla). Las rampas del fuego son las de su barra
(fuego_hud_propuesta.py): ambar (I), oro (II), carmesi (IV) y el azul de la
Furia; el acero quemado y el oro de la armadura, los de fuego_modelo.py.

  textures/particle/   las particulas novilis_*
  particles/           sus definiciones (la lista de fotogramas)
  textures/entity/novilis/
    sello.png          el sello solar del suelo, visto desde arriba: aro doble,
                       doce rayos, aro de dentro y disco. En grises: el codigo lo
                       tine (fase, naranja del Sol, carmesi del Dios) (128x128)
    haz.png            el haz de luz que cae: el alma clara en medio y los lados
                       que se apagan, con vetas; en grises (16x64, se repite en v)
    llamas_n.png       una pared de llamas vista de lado: el pie encendido y las
    llamas_c.png       lenguas hacia arriba (64x32, se repite a lo ancho). n en
    llamas_a.png       naranja y oro, c en carmesi, a en azul
    media_luna.png     el tajo de fuego que sale volando: la panza hacia arriba
                       (v = 0), el filo encendido en el lado de dentro (64x32)
    sol.png            el resplandor y la corona de un sol pequeno (64x64)
    sol_superficie.png la superficie del sol, granulos de fuego (16x16, se repite)
    charco.png         un charco de lava visto desde arriba: costra y vetas
                       encendidas (64x64)
    estela.png         la estela de fuego: la cabeza en v = 0 y la cola que se
                       apaga hacia v = 1; en grises (16x64)
    chispas_suelo.png  la quemadura del suelo: hollin y grietas que brillan (64x64)
    novilis_disolver.png  la mascara de disolverse (256x256, ruido suave)
  textures/item/       nucleo_solar (el Nucleo Solar, su botin)
  textures/mob_effect/ bendicion_sol (la bendicion al liberarlo)
  textures/gui/        miedo_novilis (la vineta: el borde se quema y se cierra,
                       con brasas y el aire que tiembla de calor)

Particulas (fotogramas, tamano):
  novilis_brasa    3  8x8    brasa naranja que sube (de grande a pequena)
  novilis_chispa   3  8x8    chispa en cruz, casi blanca (de grande a pequena)
  novilis_ceniza   3  8x8    copos de ceniza gris (uno con el canto encendido)
  novilis_llama    4  16x16  bocanada de fuego: prende, crece, se suelta, se apaga
  novilis_humo     4  16x16  humo oscuro que se abre y se deshace
  novilis_onda     3  64x64  anillo de fuego que se abre por el suelo (tumbado)
  novilis_roca     3  8x8    trozos de basalto con una veta de lava
  novilis_nota     3  16x16  notas de oro: corchea, dos corcheas, negra
  novilis_luz      3  8x8    mota de oro de la liberacion (de pequena a grande)
  novilis_azul     4  16x16  lengua de fuego azul (la Furia)
  novilis_carmesi  4  16x16  lengua de fuego carmesi (el Dios de la Guerra)

El huevo de Novilis lo dibuja huevos_jefes.py.

Uso: python novilis_extras.py <raiz del proyecto> [vista_previa.png]
"""
from PIL import Image, ImageDraw
import math, os, sys, json, random
import numpy as np

RAIZ = sys.argv[1]
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
PAR = os.path.join(A, 'textures/particle')
DEF = os.path.join(A, 'particles')
ENT = os.path.join(A, 'textures/entity/novilis')
ITEM = os.path.join(A, 'textures/item')
EFE = os.path.join(A, 'textures/mob_effect')
GUI = os.path.join(A, 'textures/gui')
for d in (PAR, DEF, ENT, ITEM, EFE, GUI):
    os.makedirs(d, exist_ok=True)
TAU = 2 * math.pi


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def lienzo(w, h=None):
    return Image.new('RGBA', (w, h or w), (0, 0, 0, 0))


def mezclar(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def alfa(c, a):
    return c[:3] + (max(0, min(255, int(a))),)


def gris(v, a=255):
    v = max(0, min(255, int(v)))
    return (v, v, v, max(0, min(255, int(a))))


def rampa(*cs):
    return [hexc(c) for c in cs]


# El fuego, de la brasa honda al nucleo (el [3] es el color de la fase). El
# nucleo nunca es blanco puro: tira al color.
AMBAR = rampa('2a0c04', '6a1e06', 'b84a0c', 'ff8a1e', 'ffc070', 'fff0d0')
ORO_F = rampa('2e1404', '7a3a08', 'c87810', 'ffc23a', 'ffe48a', 'fffae0')
CARMESI = rampa('2c0408', '6e0a16', 'b8142a', 'ff2a3a', 'ff9a84', 'ffe4d8')
AZUL = rampa('041828', '0a3c62', '1a78b8', '5ad8ff', 'b4f2ff', 'f0fdff')
# El fuego "de siempre" de Novilis, del canto rojo al alma: naranja que se hace oro
FUEGO = rampa('8a2a08', 'c84a0c', 'ff7a1a', 'ff9e2a', 'ffc23a', 'ffe07a', 'fff4c4', 'fffbe8')
# Acero quemado y oro de la armadura; basalto del altar; ceniza y humo
ACERO = rampa('1c1416', '2b1d1c', '3d2a25', '54382d', '6e4a38')
ORO = rampa('5a3410', '8a5418', 'c07c22', 'e8a83a', 'ffd77a')
BASALTO = rampa('141012', '2a2427', '363033', '443d40', '554c4e', '6a6062')
CENIZA = rampa('4a4442', '6a6360', '8c8580', 'ada6a0', 'cfc8c0')
HUMO = rampa('171313', '221c1b', '2e2725', '3b3330', '4a413d', '5c524d')
CHAR = hexc('1a0d08')          # el negro de lo quemado: lleva el tinte del fuego


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


VECINOS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def capas(solido):
    """Pasos hasta el aire mas cercano (vecindad 4): el canto vale 0, sus
    vecinos de dentro 1, y asi hacia dentro (DISENO 18)."""
    d = {}
    frente = [p for p in solido if any((p[0] + dx, p[1] + dy) not in solido for dx, dy in VECINOS4)]
    for p in frente:
        d[p] = 0
    paso = 0
    while frente:
        paso += 1
        nuevo = []
        for (x, y) in frente:
            for dx, dy in VECINOS4:
                q = (x + dx, y + dy)
                if q in solido and q not in d:
                    d[q] = paso
                    nuevo.append(q)
        frente = nuevo
    return d


def sueltos(solido, maximo, envolver=None):
    """Los pixeles de los trozos pequenos (menos de 'maximo', vecindad 4). Son
    todo canto, asi que se les suben dos tonos: si no, un trozo de llama suelto
    sale como una mancha oscura en vez de como una chispa. Con 'envolver' (el
    ancho), las x dan la vuelta."""
    fuera = set()
    vistos = set()
    for p0 in solido:
        if p0 in vistos:
            continue
        grupo, pila = [], [p0]
        vistos.add(p0)
        while pila:
            (x, y) = pila.pop()
            grupo.append((x, y))
            for dx, dy in VECINOS4:
                q2 = ((x + dx) % envolver if envolver else x + dx, y + dy)
                if q2 in solido and q2 not in vistos:
                    vistos.add(q2)
                    pila.append(q2)
        if len(grupo) < maximo:
            fuera.update(grupo)
    return fuera


def dentro_poly(poly, x, y):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def ruido(w, h, celda, semilla, envolver=True):
    """Ruido suave (bilineal) en [0, 1], que se repite si 'envolver'."""
    r = np.random.default_rng(semilla)
    gw, gh = max(1, w // celda), max(1, h // celda)
    g = r.random((gh + 1, gw + 1))
    if envolver:
        g[-1, :] = g[0, :]
        g[:, -1] = g[:, 0]
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    fx, fy = xx / celda, yy / celda
    x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
    x0, y0 = np.minimum(x0, gw - 1), np.minimum(y0, gh - 1)
    tx, ty = fx - x0, fy - y0
    tx = tx * tx * (3 - 2 * tx)
    ty = ty * ty * (3 - 2 * ty)
    a = g[y0, x0] * (1 - tx) + g[y0, x0 + 1] * tx
    b = g[y0 + 1, x0] * (1 - tx) + g[y0 + 1, x0 + 1] * tx
    return a * (1 - ty) + b * ty


def cobertura(fn, w, h, s=4):
    """Que parte de cada pixel cubre la forma fn(x, y) (arrays): se muestrea
    s x s veces por pixel. Asi los aros y los rayos salen con el canto limpio."""
    yy, xx = np.mgrid[0:h * s, 0:w * s].astype(float)
    m = fn((xx + 0.5) / s, (yy + 0.5) / s).astype(float)
    return m.reshape(h, s, w, s).mean(axis=(1, 3))


def de_array(a):
    # copy(): la imagen de fromarray comparte memoria con el array y no se deja pintar
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA').copy()


# ======================================================================
#  PARTICULAS
# ======================================================================
# --- brasa: un punto encendido con su halo, de grande a pequeno (el codigo la
#     hace parpadear y la enrojece al apagarse)
def brasa(f):
    im = lienzo(8)
    p = im.load()
    r = [2.6, 1.8, 1.0][f]
    for y in range(8):
        for x in range(8):
            d = abs(x - 3.5) + abs(y - 3.5)
            if d <= r * 0.42 + 0.5:
                p[x, y] = AMBAR[5]
            elif d <= r * 0.75 + 0.5:
                p[x, y] = AMBAR[4]
            elif d <= r + 0.5:
                p[x, y] = AMBAR[3]
            elif d <= r + 1.5 and f < 2:
                p[x, y] = alfa(AMBAR[2], 120)
    return im


guardar('novilis_brasa', [brasa(f) for f in range(3)])


# --- chispa: una cruz casi blanca con las puntas de oro (y un destello en
#     diagonal en la grande)
def chispa(f):
    im = lienzo(8)
    p = im.load()
    l = [3.5, 2.5, 1.5][f]
    for y in range(8):
        for x in range(8):
            dx, dy = abs(x - 3.5), abs(y - 3.5)
            cruz = (dx < 0.6 and dy <= l) or (dy < 0.6 and dx <= l)
            if cruz:
                t = (dx + dy) / (l + 0.01)
                p[x, y] = ORO_F[5] if t < 0.3 else ORO_F[4] if t < 0.62 else ORO_F[3] if t < 0.9 else AMBAR[3]
            elif f == 0 and abs(dx - dy) < 0.1 and dx < 1.6:
                p[x, y] = alfa(ORO_F[3], 170)
    return im


guardar('novilis_chispa', [chispa(f) for f in range(3)])

# --- ceniza: copos grises, la luz arriba a la izquierda; al tercero le queda
#     el canto encendido
CENIZA_PAL = {'a': CENIZA[4], 'b': CENIZA[3], 'c': CENIZA[2], 'd': CENIZA[1], 'o': CENIZA[0],
              'e': AMBAR[3], 'E': AMBAR[4]}
COPOS = [
    ["........",
     "...ab...",
     "..abbc..",
     ".abbccd.",
     "..bccdo.",
     "...cdo..",
     "....o...",
     "........"],
    ["........",
     "........",
     ".ab.....",
     "..bbc...",
     "...ccdd.",
     ".....do.",
     "........",
     "........"],
    ["........",
     "........",
     "...Ea...",
     "..ebbc..",
     "..bccd..",
     "...ddo..",
     "........",
     "........"],
]
guardar('novilis_ceniza', [pintar(lienzo(8), c, CENIZA_PAL) for c in COPOS])


# --- las lenguas de fuego: un poligono por lengua, y el color por pasos hasta
#     el aire (canto rojo, alma casi blanca)
def lengua(cx, base, semi, alto, lean=0.0, curva=0.0, n=28):
    """Una lengua de fuego: panza redonda abajo y la punta arriba, que se va
    hacia un lado (lean, en anchos por alto) y se ondula (curva, en pixeles)."""
    izq, der = [], []
    for i in range(n + 1):
        t = i / n
        w = semi * math.sin(math.pi * (0.35 + 0.65 * t))
        x = cx + lean * alto * t ** 1.4 + curva * math.sin(math.pi * t * 1.6)
        y = base - alto * t
        izq.append((x - w, y))
        der.append((x + w, y))
    fondo = []
    w0 = semi * math.sin(math.pi * 0.35)
    for i in range(1, 12):
        a = math.pi * i / 12
        fondo.append((cx + w0 * math.cos(a), base + semi * 0.55 * math.sin(a)))
    return izq + der[::-1] + fondo


def gota(cx, cy, r):
    """Un trozo de llama suelto: una gota que apunta hacia arriba."""
    return lengua(cx, cy + r * 0.5, r, r * 2.2, 0.0)


def llama(n, lenguas, rmp, calor=1, a_canto=230, sesgo_abajo=True):
    """Rellena las lenguas en un lienzo de n x n y lo colorea por pasos:
    el canto con rmp[0], hacia dentro cada paso un tono mas; abajo, donde la
    llama es ancha, un tono mas caliente (DISENO 6)."""
    im = lienzo(n)
    q = im.load()
    solido = set()
    for poly in lenguas:
        for y in range(n):
            for x in range(n):
                if dentro_poly(poly, x + 0.5, y + 0.5):
                    solido.add((x, y))
    if not solido:
        return im
    d = capas(solido)
    abajo = max(y for _, y in solido)
    arriba = min(y for _, y in solido)
    alto = max(1, abajo - arriba)
    suelto = sueltos(solido, 10)
    for (x, y), k in d.items():
        if sesgo_abajo:
            k += int(calor * max(0.0, (y - arriba) / alto - 0.35) * 2.6)
        if (x, y) in suelto:
            k += 2
        k = max(0, min(len(rmp) - 1, k))
        q[x, y] = alfa(rmp[k], a_canto) if k == 0 else rmp[k]
    return im


# --- llama: una bocanada que prende, crece, se suelta del suelo y se apaga
F_LLAMA = FUEGO[1:]
LLAMA_FOTOS = [
    [lengua(8, 12.5, 4.2, 8.5, 0.05), lengua(5.2, 13, 2.0, 4.0, -0.3), lengua(10.8, 13, 2.0, 4.5, 0.3)],
    [lengua(8, 13.5, 5.0, 12.5, 0.06, 0.8), lengua(4.6, 14, 2.4, 7.0, -0.28), lengua(11.6, 14, 2.4, 8.0, 0.3)],
    [lengua(8.5, 12.5, 4.2, 10.0, -0.08, -0.8), lengua(5.2, 13, 1.8, 5.0, -0.35), gota(10.5, 3.2, 1.6)],
    [lengua(7.8, 12.5, 3.0, 6.5, 0.1, -0.5), gota(9.0, 4.2, 1.5)],
]
LLAMA_CALOR = [2, 2, 1, 1]
llamas = [llama(16, l, F_LLAMA if i < 3 else FUEGO[1:6], LLAMA_CALOR[i]) for i, l in enumerate(LLAMA_FOTOS)]
guardar('novilis_llama', llamas)

# --- lenguas azules (Furia) y carmesi (Dios de la Guerra): una sola lengua
#     fina que se ondula, se tuerce al otro lado, suelta la punta y se apaga
WISP_FOTOS = [
    [lengua(8, 14, 3.0, 13.0, 0.08, 1.2)],
    [lengua(8, 14, 3.2, 12.0, -0.1, -1.4)],
    [lengua(7.5, 14, 2.8, 8.5, 0.12, 0.8), gota(9.2, 3.0, 1.3)],
    [lengua(8, 14, 2.0, 6.0, -0.15, -0.6)],
]


def rampa_lengua(base):
    """De la rampa de seis de la fase: el canto en el tono hondo, el alma casi blanca."""
    return [base[1], base[2], base[3], base[4], base[5]]


guardar('novilis_azul', [llama(16, l, rampa_lengua(AZUL), 1 if i < 3 else 0) for i, l in enumerate(WISP_FOTOS)])
guardar('novilis_carmesi', [llama(16, l, rampa_lengua(CARMESI), 1 if i < 3 else 0) for i, l in enumerate(WISP_FOTOS)])


# --- humo: bocanadas oscuras que se abren y se deshacen (la luz arriba a la izquierda)
HUECOS_HUMO = ruido(16, 16, 4, 905)


def humo(f):
    im = lienzo(16)
    p = im.load()
    R = [3.6, 4.6, 5.6, 6.4][f]
    bultos = [(8.0, 9.0, R), (8.0 - R * 0.5, 9.4, R * 0.62), (8.0 + R * 0.5, 8.6, R * 0.7), (7.8, 8.6 - R * 0.45, R * 0.66)]
    for y in range(16):
        for x in range(16):
            px, py = x + 0.5, y + 0.5
            d = min(math.hypot(px - bx, py - by) / br for bx, by, br in bultos)
            if d > 1:
                continue
            if f >= 2 and d > 0.45 and HUECOS_HUMO[y, x] < 0.22 * f - 0.1:
                continue                                    # se deshace a jirones
            luz = -((px - 8) + (py - 8)) / (2 * R)
            k = 2 + (1 if luz > 0.15 else 0) + (1 if luz > 0.45 else 0) - (1 if luz < -0.3 else 0)
            k += (f + 1) // 2
            a = [235, 215, 175, 125][f] * (1 - max(0.0, d - 0.6) * 1.6)
            p[x, y] = alfa(HUMO[max(0, min(5, k))], a)
    return im


guardar('novilis_humo', [humo(f) for f in range(4)])


# --- onda: un anillo de fuego tumbado que se abre: el filo de dentro casi
#     blanco, el cuerpo naranja, lenguas hacia fuera y brasas sueltas
def onda(f):
    n = 64
    im = lienzo(n)
    p = im.load()
    r = random.Random(700 + f)
    fuerza = [1.0, 0.78, 0.5][f]
    grueso = [0.11, 0.085, 0.06][f]
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2, y + 0.5 - n / 2
            d = math.hypot(dx, dy) / (n / 2)
            ang = math.atan2(dy, dx)
            # las lenguas que salen hacia fuera: el canto de fuera sube y baja con el angulo
            lenguas = max(0.0, math.sin(ang * 18 + f * 1.3)) ** 3 * 0.6 + max(0.0, math.sin(ang * 11 + 2.0)) ** 4 * 0.4
            r0 = 0.80
            r1 = r0 + grueso + 0.07 * lenguas * fuerza
            if r0 <= d <= r1:
                t = (d - r0) / (r1 - r0)                  # 0 en el filo de dentro, 1 en la punta de fuera
                c = FUEGO[7] if t < 0.12 else FUEGO[6] if t < 0.25 else FUEGO[4] if t < 0.45 else \
                    FUEGO[3] if t < 0.68 else FUEGO[1]
                a = 255 * fuerza if t < 0.68 else 200 * fuerza
                if f == 2 and math.sin(ang * 7 + 0.5) > 0.55:
                    a *= 0.35                             # se rompe al final
                p[x, y] = alfa(c, a)
            elif r0 - 0.035 <= d < r0:
                p[x, y] = alfa(FUEGO[5], 150 * fuerza)    # el resplandor de dentro
            elif 0.6 < d < r0 - 0.035 and r.random() < 0.025 * fuerza:
                p[x, y] = alfa(CHAR, 150 * fuerza)        # hollin que deja al pasar
    for _ in range(int(16 * fuerza)):                     # brasas que salen despedidas
        a = r.uniform(0, TAU)
        rr = r.uniform(0.93, 0.99) * n / 2
        x, y = int(n / 2 + rr * math.cos(a)), int(n / 2 + rr * math.sin(a))
        if 0 <= x < n and 0 <= y < n:
            p[x, y] = alfa(FUEGO[5] if r.random() < 0.5 else FUEGO[3], 235 * fuerza)
    return im


guardar('novilis_onda', [onda(f) for f in range(3)])

# --- roca: trozos de basalto con una veta de lava
ROCA_PAL = {'o': BASALTO[0], '1': BASALTO[1], '2': BASALTO[2], '3': BASALTO[3], '4': BASALTO[4], '5': BASALTO[5],
            'L': AMBAR[4], 'l': AMBAR[3], 'k': AMBAR[2]}
TROZOS = [
    [".oooooo.",
     "o554433o",
     "o54k321o",
     "o4lL211o",
     "o3kl211o",
     "o32k211o",
     "o221111o",
     ".oooooo."],
    ["........",
     "..oooo..",
     ".o5543o.",
     ".o4lk2o.",
     ".o3L21o.",
     ".o3211o.",
     "..oooo..",
     "........"],
    ["........",
     "........",
     "...ooo..",
     "..o54o..",
     "..o3lo..",
     "...ooo..",
     "........",
     "........"],
]
guardar('novilis_roca', [pintar(lienzo(8), t, ROCA_PAL) for t in TROZOS])

# --- notas de oro: corchea, dos corcheas unidas y negra, con su halo
NOTAS = [
    ["................",
     "........##......",
     "........###.....",
     "........####....",
     "........##.##...",
     "........##..##..",
     "........##...#..",
     "........##...#..",
     "........##..#...",
     "........##......",
     "....######......",
     "...#######......",
     "...######.......",
     "....####........",
     "................",
     "................"],
    ["................",
     "....##########..",
     "....##########..",
     "....##......##..",
     "....##......##..",
     "....##......##..",
     "....##......##..",
     "....##......##..",
     "....##......##..",
     ".#####...#####..",
     "######..######..",
     "#####...#####...",
     ".###.....###....",
     "................",
     "................",
     "................"],
    ["................",
     "................",
     ".........##.....",
     ".........##.....",
     ".........##.....",
     ".........##.....",
     ".........##.....",
     ".........##.....",
     ".........##.....",
     ".........##.....",
     ".....######.....",
     "....#######.....",
     "....######......",
     ".....####.......",
     "................",
     "................"],
]


def nota(dibujo):
    n = 16
    im = lienzo(n)
    q = im.load()
    solido = {(x, y) for y, fila in enumerate(dibujo) for x, c in enumerate(fila) if c == '#'}
    # el halo: un paso fuera de la nota (en cruz mas fuerte, en diagonal tenue)
    for y in range(n):
        for x in range(n):
            if (x, y) in solido:
                continue
            if any((x + dx, y + dy) in solido for dx, dy in VECINOS4):
                q[x, y] = alfa(ORO_F[3], 80)
            elif any((x + dx, y + dy) in solido for dx in (-1, 1) for dy in (-1, 1)):
                q[x, y] = alfa(ORO_F[3], 34)
    cabeza_y = max(y for _, y in solido)
    for (x, y) in solido:
        borde = any((x + dx, y + dy) not in solido for dx, dy in VECINOS4)
        sombra = (x + 1, y) not in solido or (x, y + 1) not in solido     # abajo a la derecha
        q[x, y] = ORO_F[2] if borde and sombra else ORO_F[3] if borde else ORO_F[4]
    # el brillo de la cabeza, arriba a la izquierda
    for (x, y) in solido:
        if y >= cabeza_y - 2 and (x - 1, y) not in solido and (x, y - 1) in solido and (x + 1, y) in solido:
            q[x + 1, y] = ORO_F[5]
    return im


guardar('novilis_nota', [nota(d) for d in NOTAS])


# --- luz: la mota de oro de la liberacion, suave, de pequena a grande
def luz(f):
    im = lienzo(8)
    p = im.load()
    r = [2.0, 2.8, 3.6][f]
    for y in range(8):
        for x in range(8):
            d = math.hypot(x + 0.5 - 4, y + 0.5 - 4) / r
            # un nucleo macizo y el halo de oro que se apaga (si todo es
            # translucido, sobre lo oscuro sale beis en vez de oro)
            if d <= 0.4:
                p[x, y] = ORO_F[5]
            elif d <= 0.7:
                p[x, y] = alfa(ORO_F[4], 245)
            elif d <= 1:
                p[x, y] = alfa(ORO_F[3], 90 + 120 * (1 - d) / 0.3)
    return im


guardar('novilis_luz', [luz(f) for f in range(3)])


# ======================================================================
#  TEXTURAS DE LOS RENDERERS (textures/entity/novilis/)
# ======================================================================
def por_niveles(cov, alfa_lleno):
    """La cobertura a dos escalones: lleno o medio canto. Nada se difumina mas
    de un pixel."""
    return np.where(cov >= 0.55, alfa_lleno, np.where(cov >= 0.2, alfa_lleno * 0.45, 0.0))


# ----------------------------------------------------------------------
#  El sello solar (128x128, en grises): aro doble fuera, doce rayos
#  facetados (una mitad clara y la otra un tono mas honda, como una talla),
#  el aro de dentro y el disco con su filete. Un velo tenue lo llena.
# ----------------------------------------------------------------------
def sello():
    n = 128
    c = n / 2
    out = np.zeros((n, n, 4), float)

    def capa(fn, v, a):
        cov = cobertura(fn, n, n)
        al = por_niveles(cov, a)
        m = al > 0
        out[m, 0:3] = v
        out[m, 3] = al[m]

    def radio(x, y):
        return np.hypot(x - c, y - c)

    capa(lambda x, y: radio(x, y) < 57.0, 255, 38)                                  # el velo
    capa(lambda x, y: (radio(x, y) >= 60.4) & (radio(x, y) < 63.2), 255, 250)       # aro de fuera
    capa(lambda x, y: (radio(x, y) >= 55.0) & (radio(x, y) < 57.0), 225, 240)       # su pareja
    # los rayos: triangulos de la base (r = 30) a la punta (r = 53); cada uno en dos mitades
    for mitad, v in ((0, 255), (1, 196)):
        def rayo(x, y, mitad=mitad):
            r = radio(x, y)
            a = np.arctan2(y - c, x - c) + math.pi / 2              # el primero, arriba
            s = (a / (TAU / 12)) % 1.0 - 0.5                         # -0.5..0.5 dentro del sector
            ancho = 4.6 * np.clip((53.0 - r) / 23.0, 0, 1) + 0.35  # media anchura, en pixeles
            dentro = (r >= 29.0) & (r < 53.0) & (np.abs(s) * r * TAU / 12 < ancho)
            return dentro & ((s < 0) if mitad == 0 else (s >= 0))
        capa(rayo, v, 235)
    capa(lambda x, y: (radio(x, y) >= 25.0) & (radio(x, y) < 28.2), 255, 245)       # aro de dentro
    capa(lambda x, y: radio(x, y) < 17.5, 240, 235)                                  # el disco
    capa(lambda x, y: (radio(x, y) >= 11.2) & (radio(x, y) < 12.6), 180, 240)       # su filete
    capa(lambda x, y: radio(x, y) < 5.2, 255, 250)                                   # y el centro
    return de_array(out)


# ----------------------------------------------------------------------
#  El haz que cae (16x64, en grises; se repite en v): el alma clara, los
#  lados que se apagan y vetas que suben y bajan de brillo a lo largo.
# ----------------------------------------------------------------------
def haz():
    w, h = 16, 64
    out = np.zeros((h, w, 4), float)
    rv = random.Random(31)
    fases = [rv.uniform(0, TAU) for _ in range(w)]
    for y in range(h):
        for x in range(w):
            d = abs(x + 0.5 - w / 2) / (w / 2)                     # 0 en medio, 1 en el canto
            if d < 0.22:
                v, a = 255, 255
            elif d < 0.42:
                v, a = 238, 225
            elif d < 0.62:
                v, a = 210, 150
            elif d < 0.82:
                v, a = 185, 78
            else:
                v, a = 165, 26
            # vetas: cada columna late a lo largo (dos y tres veces por vuelta: se repite)
            veta = 0.5 * math.sin(TAU * 2 * y / h + fases[x]) + 0.5 * math.sin(TAU * 3 * y / h + fases[x] * 1.7)
            if d >= 0.22:
                v += 16 * veta
                a *= 1.0 + 0.3 * veta
            out[y, x] = (v, v, v, a)
    return de_array(out)


# ----------------------------------------------------------------------
#  La pared de llamas (64x32, se repite a lo ancho): lenguas que se envuelven
#  de un lado al otro, el pie encendido y el color por pasos hasta el aire.
# ----------------------------------------------------------------------
LENGUAS_PARED = None


def lenguas_pared():
    r = random.Random(64)
    ls = []
    x = 0.0
    while x < 64:
        ls.append((x + r.uniform(-1.0, 1.0), r.uniform(13, 29), r.uniform(3.2, 5.6), r.uniform(-0.18, 0.18)))
        x += r.uniform(5.5, 8.0)
    return ls


def pared_llamas(rmp):
    w, h = 64, 32
    ls = lenguas_pared()
    solido = set()
    for y in range(h):
        v = h - 1 - y + 0.5                                       # altura desde abajo
        for x in range(w):
            pie = 6.0 + 1.5 * math.sin(TAU * 3 * x / w) + 1.0 * math.sin(TAU * 5 * x / w + 1.0)
            dentro = v < pie
            for (cx, alto, semi, lean) in ls:
                if v >= alto:
                    continue
                t = v / alto
                centro = cx + lean * v
                dx = (x + 0.5 - centro + w / 2) % w - w / 2          # envuelve: casa al repetirse
                if abs(dx) <= semi * (1 - t) ** 0.85 * (1.0 + 0.35 * math.sin(math.pi * t)):
                    dentro = True
                    break
            if dentro:
                solido.add((x, y))
    # trozos sueltos encima de algunas lenguas
    for (cx, alto, semi, lean) in ls[::3]:
        gx, gy = round(cx + lean * alto + 1) % w, round(h - 1 - alto - 2.5)
        for (ox, oy) in ((0, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
            if 0 <= gy + oy < h:
                solido.add(((gx + ox) % w, gy + oy))
    # los pasos hasta el aire, envolviendo a lo ancho (tres copias y la del medio)
    triple = {(x + k * w, y) for (x, y) in solido for k in (-1, 0, 1)}
    d = capas(triple)
    suelto = sueltos(solido, 10, w)
    im = lienzo(w, h)
    q = im.load()
    for (x, y) in solido:
        k = d[(x, y)]
        v = h - 1 - y
        k += 3 if v < 3 else 2 if v < 6 else 1 if v < 10 else 0     # el pie, encendido
        if (x, y) in suelto:
            k += 2
        k = max(0, min(len(rmp) - 1, k))
        q[x, y] = alfa(rmp[k], 215) if k == 0 else rmp[k]
    return im


PARED_N = FUEGO[1:]
PARED_C = rampa('6e0a16', 'b8142a', 'e01c30', 'ff2a3a', 'ff6a6a', 'ff9a84', 'ffc8b8', 'ffe4d8')
PARED_A = rampa('0a3c62', '1a78b8', '2fa6e6', '5ad8ff', '8ae6ff', 'b4f2ff', 'dcf8ff', 'f0fdff')


# ----------------------------------------------------------------------
#  La media luna (64x32): la panza arriba (v = 0), las puntas abajo. El filo
#  de dentro, el concavo, casi blanco; hacia el lomo se hace naranja, y por
#  fuera se deshace en lenguas pequenas.
# ----------------------------------------------------------------------
def media_luna():
    w, h = 64, 32
    cx, cy, ro, grueso, tope = 32.0, 35.5, 32.0, 13.5, math.radians(70)
    cos_t = math.cos(tope)
    im = lienzo(w, h)
    q = im.load()
    for y in range(h):
        for x in range(w):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            th = math.atan2(dx, -dy)                              # 0 arriba
            if abs(th) > tope:
                continue
            # el grueso de una luna de verdad: lleno en medio, las puntas afiladas
            perfil = max(0.0, (math.cos(th) - cos_t) / (1 - cos_t))
            ri = ro - grueso * perfil ** 0.8
            # el lomo no es liso: ondula y suelta lenguas hacia atras
            lomo = ro - 1.5 + 0.8 * math.sin(th * 11 + 0.4) * perfil
            flecos = 2.4 * max(0.0, math.sin(th * 8 + 2.2)) ** 3 * perfil ** 0.5 + 1.1 * max(0.0, math.sin(th * 19)) ** 4
            if perfil < 0.08:
                flecos = 0.0
            if ri <= r < lomo:
                s = (lomo - r) / max(0.5, lomo - ri)             # 0 en el lomo, 1 en el filo de dentro
                s += 0.11 * math.sin(th * 21 + r * 1.1) * (1 - s)    # vetas que barren, no bandas
                c = FUEGO[7] if s > 0.86 else FUEGO[6] if s > 0.7 else FUEGO[5] if s > 0.52 else \
                    FUEGO[4] if s > 0.34 else FUEGO[3] if s > 0.17 else FUEGO[2]
                q[x, y] = c if perfil > 0.12 else alfa(c, 210)
            elif lomo <= r < lomo + flecos:
                q[x, y] = alfa(FUEGO[1] if r > lomo + 1.5 else FUEGO[2], 215)
    # En gris: el renderer la tine con el color de la fase (naranja por naranja
    # saldria pardo).
    a = np.array(im).astype(float)
    luz = a[..., :3] @ np.array([0.299, 0.587, 0.114])
    a[..., :3] = (110 + 145 * luz / 255.0)[..., None]
    return Image.fromarray(a.round().astype(np.uint8), 'RGBA')


# ----------------------------------------------------------------------
#  El resplandor del sol pequeno (64x64): el nucleo blanco, el cuerpo y una
#  corona de lenguas que se apaga hacia fuera. Suave: es luz. En gris (se tine).
# ----------------------------------------------------------------------
def sol():
    n = 64
    out = np.zeros((n, n, 4), float)
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    d = np.hypot(xx - n / 2, yy - n / 2) / (n / 2)
    a = np.arctan2(yy - n / 2, xx - n / 2)
    g = (0.5 + 0.5 * np.sin(a * 9 + 0.3)) * 0.5 + (0.5 + 0.5 * np.sin(a * 14 + 2.1)) * 0.3 + (0.5 + 0.5 * np.sin(a * 5 + 4.0)) * 0.2
    rc = 0.66 + 0.28 * g ** 1.6                                    # hasta donde llegan las lenguas

    def tono(c):
        return np.array(c[:3], float)

    col = np.zeros((n, n, 3))
    al = np.zeros((n, n))
    t1 = np.clip(d / 0.34, 0, 1)
    nucleo = d < 0.34
    col[nucleo] = (tono(FUEGO[7]) * (1 - t1[..., None]) + tono(FUEGO[6]) * t1[..., None])[nucleo]
    al[nucleo] = 255
    cuerpo = (d >= 0.34) & (d < 0.6)
    t2 = np.clip((d - 0.34) / 0.26, 0, 1)
    col[cuerpo] = (tono(FUEGO[6]) * (1 - t2[..., None]) + tono(FUEGO[4]) * t2[..., None])[cuerpo]
    al[cuerpo] = 255 - 30 * t2[cuerpo]
    corona = (d >= 0.6) & (d < rc)
    t3 = np.clip((d - 0.6) / np.maximum(0.05, rc - 0.6), 0, 1)
    col[corona] = (tono(FUEGO[3]) * (1 - t3[..., None]) + tono(FUEGO[1]) * t3[..., None])[corona]
    al[corona] = (225 * (1 - t3 ** 1.3))[corona]
    halo = d >= rc
    col[halo] = tono(FUEGO[2])
    al[halo] = np.clip(60 * (1 - (d[halo] - 0.6) / 0.4), 0, 60)
    # Todo blanco, la forma solo en el alfa: el renderer lo tine con el color de
    # la fase en tres capas (si llevara color, o gris oscuro en el halo, sobre el
    # cielo salia pardo, como humo: se vio en el juego el 06-10-2026).
    out[..., :3] = 255
    out[..., 3] = al
    return de_array(out)


# ----------------------------------------------------------------------
#  La superficie del sol (16x16, se repite): granulos de fuego, claros en
#  medio y con las juntas mas hondas, y alguna mancha oscura.
# ----------------------------------------------------------------------
def sol_superficie():
    n = 16
    r = random.Random(17)
    centros = [(r.uniform(0, n), r.uniform(0, n)) for _ in range(8)]
    im = lienzo(n)
    q = im.load()
    for y in range(n):
        for x in range(n):
            ds = []
            for (gx, gy) in centros:
                ddx = min(abs(x + 0.5 - gx), n - abs(x + 0.5 - gx))
                ddy = min(abs(y + 0.5 - gy), n - abs(y + 0.5 - gy))
                ds.append(math.hypot(ddx, ddy))
            ds.sort()
            junta = ds[1] - ds[0]
            if junta < 0.7:
                c = FUEGO[3]
            elif junta < 1.5:
                c = FUEGO[4]
            elif ds[0] < 1.2:
                c = FUEGO[7]
            elif ds[0] < 2.2:
                c = FUEGO[6]
            else:
                c = FUEGO[5]
            q[x, y] = c
    for (x, y) in ((3, 11), (4, 11), (12, 4)):
        q[x, y] = FUEGO[2]                                         # manchas
    return im


# ----------------------------------------------------------------------
#  El charco de lava (64x64): una mancha irregular con gotas sueltas; la
#  costra en placas oscuras y las vetas encendidas entre ellas (mas lava y
#  menos costra hacia el centro); el canto de costra fria.
# ----------------------------------------------------------------------
def charco():
    n = 64
    c = n / 2
    r = random.Random(23)
    fases = [r.uniform(0, TAU) for _ in range(4)]

    def forma(px, py):
        dx, dy = px - c, py - c
        a = math.atan2(dy, dx)
        rr = 23.0 + 2.8 * math.sin(3 * a + fases[0]) + 2.0 * math.sin(5 * a + fases[1]) + 1.2 * math.sin(8 * a + fases[2])
        return math.hypot(dx, dy) / rr

    gotas = [(c + 27 * math.cos(a), c + 27 * math.sin(a), rr) for a, rr in ((0.6, 2.2), (2.4, 1.6), (4.1, 2.6), (5.3, 1.4))]
    placas = [(r.uniform(4, 60), r.uniform(4, 60)) for _ in range(30)]
    solido = set()
    for y in range(n):
        for x in range(n):
            if forma(x + 0.5, y + 0.5) <= 1.0 or any(math.hypot(x + 0.5 - gx, y + 0.5 - gy) <= gr for gx, gy, gr in gotas):
                solido.add((x, y))
    d = capas(solido)
    nr = ruido(n, n, 4, 24, envolver=False)
    im = lienzo(n)
    q = im.load()
    COSTRA = rampa('1e0f0a', '2c160e', '3c1e12', '4e2816')
    for (x, y) in solido:
        k = d[(x, y)]
        rc = math.hypot(x + 0.5 - c, y + 0.5 - c) / 24.0
        ds = sorted(math.hypot(x + 0.5 - px, y + 0.5 - py) for px, py in placas)
        junta = ds[1] - ds[0]
        ancho = 0.7 + 1.8 * max(0.0, 0.55 - rc)                   # las vetas engordan hacia el centro
        if k == 0:
            col = alfa(COSTRA[0], 235)                            # el canto frio
        elif k == 1:
            col = COSTRA[2] if nr[y, x] > 0.45 else COSTRA[3]
        elif k == 2:
            col = FUEGO[1]                                        # el borde de la lava, al rojo
        elif junta < ancho * 0.45:
            col = FUEGO[6] if rc < 0.35 else FUEGO[5]
        elif junta < ancho:
            col = FUEGO[3]
        elif junta < ancho + 0.7:
            col = FUEGO[1]
        elif rc < 0.22:
            col = FUEGO[2]                                        # en medio, la costra aun al rojo
        else:
            col = COSTRA[2] if nr[y, x] > 0.68 else COSTRA[1] if nr[y, x] > 0.3 else COSTRA[0]
        q[x, y] = col
    return im


# ----------------------------------------------------------------------
#  La estela (16x64, en grises): la cabeza arriba (v = 0), clara y llena; la
#  cola se estrecha y se apaga hacia abajo; tres hebras finas que tiemblan a
#  lo largo, cada una a su ritmo (si se cruzan a compas parece una cadena).
# ----------------------------------------------------------------------
HEBRAS = ((-0.42, 1.0, 0.3, 0.16), (0.05, 2.0, 1.9, 0.10), (0.46, 1.5, 4.0, 0.14))


def estela():
    w, h = 16, 64
    out = np.zeros((h, w, 4), float)
    for y in range(h):
        largo = 1.0 - y / (h - 1)                                 # 1 en la cabeza, 0 en la cola
        for x in range(w):
            u = (x + 0.5) / w - 0.5
            ancho = 0.2 + 0.28 * largo
            dd = abs(u) / ancho
            if dd >= 1.0:
                continue
            v = 236 - 64 * dd
            a = 255 * (1 - dd ** 2) * largo ** 0.9
            for (sitio, ritmo, fase, tiembla) in HEBRAS:
                centro = (sitio + tiembla * math.sin(TAU * ritmo * y / h + fase)) * ancho
                if abs(u - centro) < 0.045:
                    v, a = 255, max(a, 235 * largo ** 0.7)
            out[y, x] = (v, v, v, a)
    return de_array(out)


# ----------------------------------------------------------------------
#  La quemadura del suelo (64x64): hollin irregular, grietas que brillan desde
#  el centro y brasas sueltas.
# ----------------------------------------------------------------------
def chispas_suelo():
    n = 64
    c = n / 2
    r = random.Random(47)
    fases = [r.uniform(0, TAU) for _ in range(3)]
    nr = ruido(n, n, 8, 48, envolver=False)
    im = lienzo(n)
    q = im.load()
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - c, y + 0.5 - c
            a = math.atan2(dy, dx)
            rr = 25.0 + 3.0 * math.sin(4 * a + fases[0]) + 2.0 * math.sin(7 * a + fases[1])
            t = math.hypot(dx, dy) / rr + (nr[y, x] - 0.5) * 0.35
            if t < 1.0:
                al = 235 if t < 0.55 else 190 if t < 0.75 else 120 if t < 0.9 else 60
                col = CHAR if nr[y, x] > 0.42 else hexc('2c1810')
                q[x, y] = alfa(col, al)
    # las grietas: brazos quebrados desde el centro, con alguna rama
    puntos = {}
    for i in range(7):
        ang = i * TAU / 7 + r.uniform(-0.25, 0.25)
        x, y, recorrido = c, c, 0.0
        largo = r.uniform(15, 23)
        while recorrido < largo:
            ang += r.uniform(-0.4, 0.4)
            paso = r.uniform(1.6, 2.6)
            nx, ny = x + paso * math.cos(ang), y + paso * math.sin(ang)
            for s in range(6):
                px, py = int(x + (nx - x) * s / 6), int(y + (ny - y) * s / 6)
                puntos[(px, py)] = min(puntos.get((px, py), 99), recorrido / largo)
            if r.random() < 0.22:
                b = ang + r.choice((-1, 1)) * r.uniform(0.7, 1.1)
                for s in range(1, 4):
                    p2 = (int(nx + math.cos(b) * s), int(ny + math.sin(b) * s))
                    puntos[p2] = min(puntos.get(p2, 99), 0.8)
            x, y = nx, ny
            recorrido += paso
    for (x, y), t in puntos.items():
        for dx, dy in VECINOS4:
            p2 = (x + dx, y + dy)
            if p2 not in puntos and 0 <= p2[0] < n and 0 <= p2[1] < n:
                q[p2] = alfa(FUEGO[1], 150)                     # el canto de la grieta, al rojo
    for (x, y), t in puntos.items():
        if 0 <= x < n and 0 <= y < n:
            q[x, y] = FUEGO[6] if t < 0.25 else FUEGO[4] if t < 0.6 else FUEGO[3]
    for _ in range(18):                                          # brasas
        a = r.uniform(0, TAU)
        rr = r.uniform(4, 22)
        x, y = int(c + rr * math.cos(a)), int(c + rr * math.sin(a))
        if (x, y) not in puntos:
            q[x, y] = FUEGO[5] if r.random() < 0.4 else FUEGO[3]
    return im


# ----------------------------------------------------------------------
#  La mascara de disolverse (256x256; como la de Nerea: blanco con el ruido en
#  la transparencia). Donde es alta, la pieza se va antes: dos tamanos de
#  manchas y un grano fino, como un papel que se quema a trozos.
# ----------------------------------------------------------------------
def disolver():
    n = 256
    v = 0.55 * ruido(n, n, 16, 61) + 0.3 * ruido(n, n, 6, 62) + 0.15 * np.random.default_rng(63).random((n, n))
    v = (v - v.min()) / (v.max() - v.min())
    out = np.zeros((n, n, 4), float)
    out[..., 0:3] = 255
    out[..., 3] = 8 + 240 * v
    return de_array(out)


# ----------------------------------------------------------------------
#  La llama suelta (8 cuadros de 32x64 en fila: 256x64), en grises: la tine el
#  codigo (azul en la Furia, carmesi en el Dios de la Guerra). Una lengua con
#  el alma clara abajo, que se mece y se afila, y dos lamidas sueltas que suben
#  por encima. Se pinta con suma de luz (energySwirl): lo oscuro no se ve.
# ----------------------------------------------------------------------
def llama_sprite():
    W, H, N = 32, 64, 8
    out = np.zeros((H, W * N, 4), float)
    yy, xx = np.mgrid[0:H, 0:W].astype(float) + 0.5
    v = 1.0 - yy / H                       # 0 abajo, 1 arriba
    u = (xx - W / 2) / (W / 2)             # -1..1
    for k in range(N):
        p = k / N
        # el centro se mece mas cuanto mas arriba, como una lengua de fuego
        c = 0.16 * v ** 1.4 * np.sin(TAU * (p + v * 0.9)) + 0.05 * v * np.sin(TAU * (2 * p + v * 2.3))
        # el ancho: lleno abajo, afilado arriba, con lamidas que suben
        # una gota: la base redonda, lo mas ancho a un cuarto y la punta afilada
        vb = np.clip(v - 0.04, 0, 1)
        abajo = 0.86 * np.sqrt(np.clip(1 - ((0.24 - vb) / 0.24) ** 2, 0, 1))
        arriba = 0.86 * np.clip((1 - vb) / 0.76, 0, 1) ** 1.25
        ancho = np.where(vb < 0.24, abajo, arriba)
        ancho = ancho * (1 + 0.12 * v * np.sin(TAU * (v * 3.1 - p * 2)) + 0.07 * v * np.sin(TAU * (v * 6.3 - p * 3)))
        d = np.abs(u - c) / np.maximum(ancho, 1e-3)
        dentro = d < 1.0
        i = np.clip(1 - d, 0, 1) ** 0.75 * (1.0 - 0.45 * v)
        # dos lamidas sueltas que suben y se apagan
        for j, (x0, r0) in enumerate(((0.14, 0.22), (-0.2, 0.17))):
            fase = (p + j * 0.5) % 1.0
            cy = 0.66 + 0.3 * fase
            cx = x0 + 0.1 * np.sin(TAU * (fase + j * 0.3))
            r = r0 * (1 - fase) + 0.02
            dd = np.hypot((u - cx) / r, (v - cy) / (r * 0.75))
            m = dd < 1.0
            i = np.where(m, np.maximum(i, (1 - dd) * 0.75 * (1 - fase)), i)
            dentro = dentro | m
        # en escalones, como el resto del pixel art del jefe
        niv = np.clip(np.floor(i * 5) / 4, 0, 1)
        gris = np.where(niv >= 0.75, 255, np.where(niv >= 0.5, 220, np.where(niv >= 0.25, 170, 120)))
        a = np.where(dentro & (i > 0.02), 255, 0)
        bloque = out[:, k * W:(k + 1) * W]
        bloque[..., 0] = gris
        bloque[..., 1] = gris
        bloque[..., 2] = gris
        bloque[..., 3] = a
    return de_array(out)


# ----------------------------------------------------------------------
#  La estela del tajo (32x64, grises: la tine el codigo). De lado a lado (u),
#  de la base de la hoja (nada) a la punta (el filo encendido, casi blanco);
#  a lo largo (v), del ahora (arriba) a lo de hace un momento (se apaga).
# ----------------------------------------------------------------------
def tajo_estela():
    W, H = 32, 64
    yy, xx = np.mgrid[0:H, 0:W].astype(float) + 0.5
    u = xx / W
    v = yy / H
    filo = np.exp(-((u - 0.86) / 0.07) ** 2)
    cuerpo = np.clip(u / 0.86, 0, 1) ** 1.8
    luz = np.clip(0.55 * cuerpo + 0.6 * filo, 0, 1)
    apaga = (1 - v) ** 0.9
    a = np.clip(luz * apaga * 1.15, 0, 1)
    a[u > 0.97] = 0
    niv = np.floor(np.clip(luz, 0, 1) * 4.999) / 4
    gris = 150 + 105 * niv
    out = np.zeros((H, W, 4))
    out[..., 0] = gris
    out[..., 1] = gris
    out[..., 2] = gris
    out[..., 3] = np.floor(a * 6) / 6 * 255
    return de_array(out)


# ----------------------------------------------------------------------
#  El estrado de los angeles de las Trompetas: marmol con filo de oro.
#  estrado_cima (64x64, la losa de arriba entera: el borde de oro, el marmol
#  vetado y un sol de oro en medio) y estrado_lado (32x32, se repite cada dos
#  bloques: sillares de marmol, la moldura de oro arriba y una costura de
#  fuego abajo, que avisa de que de ahi sale el pulso).
# ----------------------------------------------------------------------
MARMOL = rampa('6e675a', '9a917e', 'c9c1ae', 'e2dccd', 'f2eee3')
ORO_E = rampa('5a3c12', '8e6420', 'c8902a', 'f0bd52', 'ffe39a')


def _vetas(n, semilla):
    v = 0.6 * ruido(n, n, 8, semilla) + 0.4 * ruido(n, n, 3, semilla + 1)
    return (v - v.min()) / (v.max() - v.min())


def estrado_cima():
    n = 64
    out = np.zeros((n, n, 4))
    v = _vetas(n, 801)
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    for y in range(n):
        for x in range(n):
            k = 2 + (1 if v[y, x] > 0.62 else 0) - (1 if v[y, x] < 0.25 else 0)
            out[y, x, :3] = MARMOL[k][:3]
            out[y, x, 3] = 255
    # el filo de oro (dos pixeles) con su sombra por dentro
    borde = (xx < 3) | (yy < 3) | (xx > n - 3) | (yy > n - 3)
    sombra = ((xx < 4) | (yy < 4) | (xx > n - 4) | (yy > n - 4)) & ~borde
    out[borde, :3] = ORO_E[3][:3]
    out[(xx < 1.5) | (yy < 1.5), :3] = ORO_E[4][:3]
    out[(xx > n - 1.5) | (yy > n - 1.5), :3] = ORO_E[2][:3]
    out[sombra, :3] = MARMOL[1][:3]
    # el sol de oro en medio: disco con rayos
    d = np.hypot(xx - n / 2, yy - n / 2)
    a = np.arctan2(yy - n / 2, xx - n / 2)
    rayo = (d < 22) & (d > 9) & (np.abs(((a / TAU * 12) % 1.0) - 0.5) < 0.12 + 0.06 * (1 - (d - 9) / 13))
    out[rayo, :3] = ORO_E[2][:3]
    out[(d < 9.5), :3] = ORO_E[3][:3]
    out[(d < 7), :3] = ORO_E[4][:3]
    out[(d < 9.5) & (d > 8.5), :3] = ORO_E[1][:3]
    return de_array(out)


def estrado_lado():
    n = 32
    out = np.zeros((n, n, 4))
    v = _vetas(n, 811)
    for y in range(n):
        for x in range(n):
            k = 2 + (1 if v[y, x] > 0.6 else 0) - (1 if v[y, x] < 0.25 else 0)
            out[y, x, :3] = MARMOL[k][:3]
            out[y, x, 3] = 255
    # sillares: juntas horizontales y verticales al tresbolillo
    for y in (10, 21):
        out[y, :, :3] = MARMOL[0][:3]
        out[y - 1, :, :3] = MARMOL[1][:3]
    for fila, (y0, y1) in enumerate(((3, 10), (11, 21), (22, 29))):
        for x in ((8, 24) if fila % 2 == 0 else (0, 16)):
            out[y0:y1, x, :3] = MARMOL[0][:3]
    # la moldura de oro arriba y la costura de fuego abajo
    out[0:3, :, :3] = ORO_E[3][:3]
    out[0, :, :3] = ORO_E[4][:3]
    out[2, :, :3] = ORO_E[1][:3]
    out[29:32, :, :3] = MARMOL[0][:3]
    out[30, :, :3] = (255, 150, 50)
    out[30, ::5, :3] = (255, 220, 120)
    return de_array(out)


ENTIDAD = {
    'sello': sello(), 'haz': haz(), 'llamas_n': pared_llamas(PARED_N), 'llamas_c': pared_llamas(PARED_C),
    'llamas_a': pared_llamas(PARED_A), 'media_luna': media_luna(), 'sol': sol(), 'sol_superficie': sol_superficie(),
    'charco': charco(), 'estela': estela(), 'chispas_suelo': chispas_suelo(), 'novilis_disolver': disolver(),
    'llama_sprite': llama_sprite(), 'tajo_estela': tajo_estela(),
    'estrado_cima': estrado_cima(), 'estrado_lado': estrado_lado(),
}
for nombre, im in ENTIDAD.items():
    im.save(os.path.join(ENT, nombre + '.png'))


# ======================================================================
#  OBJETO: el Nucleo Solar (16x16), el sol del pecho de Novilis: una gema de
#  fuego en un bisel de acero quemado, el aro de oro y ocho rayos (cuatro
#  largos hasta el canto, de dos de ancho, y cuatro cortos en diagonal). Cada
#  rayo en dos caras, la que mira a la luz (arriba a la izquierda) mas clara.
# ======================================================================
GEMA = [AMBAR[2], AMBAR[3], ORO_F[3], ORO_F[4], ORO_F[5]]
ORO_CLARO = hexc('fff2c0')


def nucleo_solar():
    n, c = 16, 7.5
    im = lienzo(n)
    q = im.load()
    oro, bisel, gema = set(), set(), set()
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - c, y - c)
            if d <= 3.5:
                gema.add((x, y))
            elif d <= 4.5:
                bisel.add((x, y))
            elif d <= 5.6:
                oro.add((x, y))
    largos = set()
    for t in range(4):
        for a in (7, 8):
            largos |= {(a, t), (a, 15 - t), (t, a), (15 - t, a)}
    cortos = set()
    for k in range(2):
        cortos |= {(2 + k, 2 + k), (13 - k, 2 + k), (2 + k, 13 - k), (13 - k, 13 - k)}
    oro = (oro | largos | cortos) - gema - bisel
    for (x, y) in oro:
        luz = (c - x) + (c - y)
        if (x, y) in largos and math.hypot(x - c, y - c) > 5.6:
            vertical = x in (7, 8)
            lado = x if vertical else y                         # 7: la cara de la luz, 8: la otra
            antes = (y < c) if vertical else (x < c)            # el rayo de arriba o de la izquierda
            q[x, y] = ORO[4] if lado == 7 and antes else ORO[3] if lado == 7 or antes else ORO[2]
        elif (x, y) in cortos and math.hypot(x - c, y - c) > 5.6:
            q[x, y] = ORO[4] if x < c and y < c else ORO[2] if x > c and y > c else ORO[3]
        else:
            borde = any((x + dx, y + dy) not in oro and (x + dx, y + dy) not in bisel for dx, dy in VECINOS4)
            q[x, y] = ORO[1] if borde and luz < -2.5 else ORO[4] if luz > 2.5 else ORO[3] if luz > -2.5 else ORO[2]
    for (x, y) in bisel:
        luz = (c - x) + (c - y)
        q[x, y] = ACERO[3] if luz > 2 else ACERO[2] if luz > -2 else ACERO[1]
    for (x, y) in gema:
        d = math.hypot(x - (c - 1.0), y - (c - 1.0))            # la luz, arriba a la izquierda
        borde = any((x + dx, y + dy) not in gema for dx, dy in VECINOS4)
        if borde:
            q[x, y] = GEMA[2] if d < 2.5 else GEMA[1] if d < 3.9 else GEMA[0]
        else:
            q[x, y] = GEMA[4] if d < 0.8 else GEMA[3] if d < 2.0 else GEMA[2]
    for (x, y) in ((7, 0), (0, 7)):
        q[x, y] = ORO_CLARO                                     # el destello de las puntas
    return im


nucleo_solar().save(os.path.join(ITEM, 'nucleo_solar.png'))

# ======================================================================
#  EFECTO: la Bendicion del Sol (18x18). La espada del caballero, de punta
#  arriba, en oro claro, con la gloria de rayos detras. Distinta de la
#  insolacion (un disco) y de la quemadura (una llama) por la forma, y toda
#  la rampa en la franja clara (DISENO 4-bis: nada por debajo de ~170).
# ======================================================================
B_CANTO, B_MEDIO, B_CLARO, B_NUCLEO, B_PUNO = hexc('f0a830'), ORO_F[3], ORO_F[4], ORO_F[5], hexc('ff9a2e')
ESPADA = [
    "..................",
    "........n.........",
    ".......cnm........",
    ".......cnm........",
    ".......cnm........",
    ".......cnm........",
    ".......cnm........",
    ".......cnm........",
    ".......cnm........",
    ".......cnm........",
    "...c...cnm...m....",
    "...cccccccmmmm....",
    "........a.........",
    "........a.........",
    "........a.........",
    ".......cnm........",
    "........m.........",
    "..................",
]
B_PAL = {'c': B_CLARO, 'n': B_NUCLEO, 'm': B_MEDIO, 'a': B_PUNO, 'k': B_CANTO}
# la gloria: seis rayos cortos alrededor de (8, 6), y tres motas sueltas
GLORIA = [(5, 6, 'm'), (4, 6, 'c'), (3, 6, 'm'), (11, 6, 'm'), (12, 6, 'c'), (13, 6, 'm'),
          (5, 3, 'm'), (4, 2, 'c'), (11, 3, 'm'), (12, 2, 'c'),
          (5, 9, 'm'), (4, 10, 'k'), (11, 9, 'm'), (12, 10, 'k')]
B_MOTAS = [(1, 14, 'm'), (15, 15, 'c'), (16, 9, 'm')]


def bendicion_sol():
    im = lienzo(18)
    q = im.load()
    for (x, y, c) in GLORIA + B_MOTAS:
        q[x, y] = B_PAL[c]
    pintar(im, ESPADA, B_PAL)
    return im


bendicion_sol().save(os.path.join(EFE, 'bendicion_sol.png'))

# ======================================================================
#  GUI: la vineta del miedo (256x256). El color va en la textura (el HUD la
#  pinta en blanco). El borde de la pantalla se quema como un papel: carbon
#  por fuera, el frente encendido que se mete hacia dentro (mas por abajo,
#  donde lamen las llamas), el resplandor naranja, el aire que tiembla de
#  calor en la mitad de abajo y brasas que suben.
# ======================================================================
def miedo():
    n = 256
    r = random.Random(1717)
    yy, xx = np.mgrid[0:n, 0:n].astype(float) + 0.5
    dx, dy = (xx - n / 2) / (n / 2), (yy - n / 2) / (n / 2)
    # rectangulo redondeado (no un circulo): el borde que se quema sigue los
    # bordes de la pantalla, y no dibuja una elipse en medio
    d = (np.abs(dx) ** 5 + np.abs(dy) ** 5) ** 0.2
    th = np.arctan2(dy, dx)
    fs = [r.uniform(0, TAU) for _ in range(5)]
    ondas = (0.5 * np.sin(5 * th + fs[0]) + 0.3 * np.sin(9 * th + fs[1]) + 0.2 * np.sin(14 * th + fs[2])
             + 0.12 * np.sin(23 * th + fs[3]))
    abajo = np.clip(np.sin(th), 0, 1)                           # 1 abajo (la y crece hacia abajo)
    # lenguas de distinto tamano (todas iguales parecian dientes)
    lenguas = (np.clip(np.sin(th * 29 + fs[4]), 0, 1) ** 4 * 0.55 + np.clip(np.sin(th * 13 + fs[3] + 1.0), 0, 1) ** 3 * 0.45
               + np.clip(np.sin(th * 47 + fs[2]), 0, 1) ** 6 * 0.25) * 0.08 * abajo
    # El frente pegado al borde: estirada a lo ancho de la pantalla, mas adentro
    # se veia como una elipse flotando en medio (06-10-2026, en el juego).
    frente = 0.9 + 0.04 * ondas - 0.07 * abajo - lenguas
    e = d - frente                                               # > 0 quemado, < 0 aun limpio
    col = np.zeros((n, n, 3))
    al = np.zeros((n, n))

    def encima(mask, c, a):
        """Pinta c con alfa a (array o numero) encima de lo que hay."""
        a = np.where(mask, a, 0.0)
        c = np.array(c, float)
        nuevo = a + al * (1 - a)
        col[:] = np.where(nuevo[..., None] > 0,
                          (c * a[..., None] + col * (al * (1 - a))[..., None]) / np.maximum(nuevo, 1e-6)[..., None], col)
        al[:] = nuevo

    # el calor de dentro: se oscurece hacia rojo antes del frente
    t = np.clip((d - 0.62) / np.maximum(0.05, frente - 0.62), 0, 1)
    encima(e < 0, (110, 26, 6), 0.22 * t ** 2)
    # el aire que tiembla: hebras finas que suben haciendo eses, en la mitad de abajo
    s = (xx * 0.085 + 1.6 * np.sin(yy * 0.07 + xx * 0.021)) % 1.0
    temblor = (s < 0.1) & (yy > 120) & (e < -0.05)
    encima(temblor, (255, 150, 60), 0.15 * np.clip((yy - 120) / 136, 0, 1) * np.clip((d - 0.35) / 0.35, 0, 1))
    # el resplandor del frente, hacia dentro
    g = np.clip(1 - (-e - 0.012) / 0.085, 0, 1)
    encima((e < -0.012) & (e > -0.1), (255, 118, 28), 0.55 * g ** 1.6)
    # la linea encendida y el canto al rojo
    encima((e >= -0.012) & (e < 0), (255, 214, 120), 0.7)
    encima((e >= 0) & (e < 0.016), (255, 112, 24), 1.0)
    # el carbon: rojo de brasa al lado del frente y casi negro hacia fuera
    k = np.clip((e - 0.016) / 0.12, 0, 1)
    carbon = np.stack([70 - 54 * k, 16 - 10 * k, 6 - 2 * k], axis=-1)
    a_carbon = 0.8 + 0.2 * k
    m = e >= 0.016
    a_m = np.where(m, a_carbon, 0.0)
    nuevo = a_m + al * (1 - a_m)
    col[:] = np.where(m[..., None], (carbon * a_m[..., None] + col * (al * (1 - a_m))[..., None]) /
                      np.maximum(nuevo, 1e-6)[..., None], col)
    al[:] = nuevo
    # vetas encendidas en el carbon, cerca del frente
    vetas = ruido(n, n, 6, 1718, envolver=False)
    encima((e >= 0.016) & (e < 0.09) & (vetas > 0.72), (200, 60, 12), 0.9)
    out = np.zeros((n, n, 4))
    out[..., :3] = col
    out[..., 3] = al * 255
    im = de_array(out)
    q = im.load()
    # brasas que suben, cerca del frente: un punto y, debajo, la cola que se apaga
    for _ in range(90):
        while True:
            a = r.uniform(0, TAU)
            if r.random() < 0.55:
                a = r.uniform(0.15 * math.pi, 0.85 * math.pi)      # la mayoria, abajo
            rr = r.uniform(0.55, 1.0)
            x, y = int(n / 2 + rr * math.cos(a) * n / 2), int(n / 2 + rr * math.sin(a) * n / 2)
            if 0 <= x < n and 1 <= y < n - 3 and -0.16 < e[y, x] < -0.02:
                break
        c = r.choice(((255, 236, 170), (255, 180, 70), (255, 132, 40)))
        q[x, y] = c + (235,)
        if r.random() < 0.6:
            q[x, y + 1] = (255, 120, 30, 150)
            if r.random() < 0.5:
                q[x, y + 2] = (200, 70, 16, 80)
    return im


miedo().save(os.path.join(GUI, 'miedo_novilis.png'))

# ======================================================================
#  VISTA PREVIA
# ======================================================================
if len(sys.argv) > 2:
    grupos = ['novilis_brasa', 'novilis_chispa', 'novilis_ceniza', 'novilis_roca', 'novilis_luz', 'novilis_llama',
              'novilis_azul', 'novilis_carmesi', 'novilis_humo', 'novilis_nota', 'novilis_onda']
    filas = []
    for g in grupos:
        lista = json.load(open(os.path.join(DEF, g + '.json')))['textures']
        filas.append([Image.open(os.path.join(PAR, t.split(':')[1] + '.png')).convert('RGBA') for t in lista])
    ancho = 1600
    prev = Image.new('RGBA', (ancho, 4000), (40, 34, 32, 255))
    y = x = 10
    alto_fila = 0

    def poner(im, k, fondo_claro=(120, 104, 90, 255)):
        global x, y, alto_fila
        g = im.resize((im.width * k, im.height * k), Image.NEAREST)
        if x + g.width > ancho:
            x = 10
            y += alto_fila + 12
            alto_fila = 0
        fondo = Image.new('RGBA', g.size, (40, 34, 32, 255))
        ImageDraw.Draw(fondo).rectangle((0, g.height // 2, g.width, g.height), fill=fondo_claro)
        fondo.alpha_composite(g)
        prev.alpha_composite(fondo, (x, y))
        x += g.width + 6
        alto_fila = max(alto_fila, g.height)

    for fr in filas:
        for im in fr:
            poner(im, 12 if im.width <= 8 else 6 if im.width <= 16 else 3)
        x += 20
    x = 10
    y += alto_fila + 20
    alto_fila = 0
    for nombre in ENTIDAD:
        if nombre != 'novilis_disolver':
            im = Image.open(os.path.join(ENT, nombre + '.png')).convert('RGBA')
            poner(im, 4 if im.width <= 64 else 2)
    x = 10
    y += alto_fila + 20
    alto_fila = 0
    for f in (os.path.join(ITEM, 'nucleo_solar.png'), os.path.join(EFE, 'bendicion_sol.png')):
        poner(Image.open(f).convert('RGBA'), 12, (139, 139, 139, 255))
    fondo = Image.new('RGBA', (256, 256), (150, 170, 130, 255))
    fondo.alpha_composite(Image.open(os.path.join(GUI, 'miedo_novilis.png')))
    prev.alpha_composite(fondo, (x, y))
    y += max(alto_fila, 256) + 10
    prev.crop((0, 0, ancho, y)).save(sys.argv[2])
    print(sum(len(f) for f in filas), 'texturas de particula')
print('ok')

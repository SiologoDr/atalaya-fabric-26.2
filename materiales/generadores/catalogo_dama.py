"""
Catalogo de piezas para las jefas (13-10-2026). Juan, tras Vulpina y la Gorgona: «la cara sigue siendo
el problema, y veo que la rodilla esta rara, los brazos igual; puedes hacerlo mejor: si haces varias
pruebas o formas de cara, de brazos igual y de piernas igual, lo mismo con los pechos, varios disenos, y
yo te digo cuales se quedan o faltan mejorar». Mando de referencia un modelo de Minecraft de chica
gotica (cara pintada con ojos grandes, pelo en mechones gruesos que se abren, corse en bandas).

Una figura base, con la misma luz y el mismo fondo, y en cada foto cambia SOLO una pieza:

    caras    C1..C8   (la cabeza de cerca)
    brazos   B1..B6   (el busto con los brazos: el derecho doblado para que se vea el codo)
    piernas  L1..L6   (de la cintura abajo: la derecha da un paso para que se vea la rodilla)
    pechos   P1..P6   (el torso de tres cuartos)
    F0                (la figura entera con las piezas base)

Todo de cajas, como un modelo de Blockbench. Las unidades son pixeles de la piel de Minecraft (la
cabeza mide 8 x 8 x 8) con 2 pixeles de textura por unidad. Codos y rodillas giran sobre el canto de
fuera (la espalda del codo, el frente de la rodilla): asi las dos cajas se tocan siempre por ese canto
y la union se ve limpia, como un carton doblado, sin huecos ni bolas.

Uso: python catalogo_dama.py <carpeta de salida> <todas | C1,B2,...>   (RAPIDO=1: a media resolucion)
"""
import math, os, random, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import eclipse_modelo as em
import quimeras_modelo as qm
import quimeras_escenas as qe
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel

D = vr.D2R
_r = bm._r
PPB = 2                                         # pixeles de textura por unidad
bm.PPB = PPB
I4 = np.eye(4)

PIEL = _r('8a6a68', 'bc9c96', 'dcc0b6', 'eedad0', 'fcefe8')
PELO = _r('0c0a0f', '17141c', '232029', '36313d', '544e5e')
TELA = _r('0a090d', '131116', '1c1a22', '29252f', '3b3644')
VINO = _r('1a070c', '2c0c15', '43121f', '5c1a2b', '7a2639')
BLANCO = _r('7c7884', 'a8a4b0', 'd0ccd6', 'e9e5ed', 'fbf9fd')
ORO = _r('5a3a08', '8a6014', 'b88a24', 'e0b440', 'fff0a0')
ACERO = _r('22222a', '3a3a44', '5a5a66', '8a8a98', 'c4c4d0')
CUERO = _r('180c0e', '2c1518', '421f23', '5a2b30', '7a3e44')
PELAJE = _r('120e14', '201a24', '302834', '453a4a', '615266')
ESCAMA = _r('120a18', '20122a', '331c42', '4c285e', '6c3a84')
GARRA = _r('0a0808', '171313', '272020', '3c3131', '574848')
ROJO = _r('3a0610', '680c1c', '9e1428', 'cc2438', 'f85868')
HUESO = _r('6a6056', '9a8e80', 'c6baa8', 'e2d8c8', 'faf3e6')

# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
P = {}


def reg(nombre, fn, pleno=False):
    fn.__name__ = 'cat2_' + nombre
    if pleno:
        bm.PLENOS.add(fn)
    P[nombre] = fn
    return fn


def liso(rampa, base=2, luz=1, sombra=1):
    def f(tw, th, cara, s):
        return _imagen(_bisel(np.full((th, tw), base), luz, sombra), rampa), None
    return f


reg('piel', liso(PIEL, 2, 0, 1))
reg('tela', liso(TELA, 2, 1, 1))
reg('vino', liso(VINO, 2, 1, 1))
reg('blanco', liso(BLANCO, 2, 1, 1))
reg('oro', liso(ORO, 2, 2, 1))
reg('acero', liso(ACERO, 2, 1, 1))
reg('cuero', liso(CUERO, 2, 1, 1))
reg('rojo', liso(ROJO, 2, 1, 1))
reg('hueso', liso(HUESO, 3, 1, 1))
reg('garra', liso(GARRA, 2, 2, 1))


def _hebras(tw, th, s, rampa, base=1, brillo=3):
    """Pelo: hebras a lo largo del lado mas largo, con algun brillo suelto."""
    largo_x = tw >= th
    n_l, n_t = (tw, th) if largo_x else (th, tw)
    rng = random.Random(s)
    idx = np.full((n_t, n_l), base)
    for t in range(n_t):
        if (t + s) % 3 == 0:
            idx[t, :] = base + 1
    for _ in range(max(1, n_l * n_t // 14)):
        t, a = rng.randrange(n_t), rng.randrange(n_l)
        idx[t, a:a + rng.randint(2, 4)] = brillo
    idx[:, 0] = np.minimum(idx[:, 0], base + 1)
    if not largo_x:
        idx = idx.T
    return _imagen(_bisel(idx, 1, 1), rampa)


reg('pelo', lambda tw, th, c, s: (_hebras(tw, th, s, PELO), None))
reg('pelaje', lambda tw, th, c, s: (_hebras(tw, th, s, PELAJE, 2, 4), None))


def mechon(tw, th, cara, s):
    """Los mechones largos: el centro oscuro y los cantos largos claros (como en la referencia)."""
    largo_x = tw >= th
    n_l, n_t = (tw, th) if largo_x else (th, tw)
    idx = np.full((n_t, n_l), 1)
    if n_t >= 3:
        idx[0, :] = 3
        idx[-1, :] = 2
    rng = random.Random(s)
    for _ in range(max(1, n_l // 5)):
        a = rng.randrange(n_l)
        idx[n_t // 2, a:a + 2] = 2
    if not largo_x:
        idx = idx.T
    return _imagen(idx, PELO), None


reg('mechon', mechon)


def encaje(tw, th, cara, s):
    """Una cinta de encaje blanco: la fila de agujeros y el borde de abajo en ondas (recortado)."""
    t = _imagen(_bisel(np.full((th, tw), 3), 1, 1), BLANCO)
    if cara in ('arriba', 'abajo') or th < 3:
        return t, None
    xs = np.arange(tw)
    t[th // 2, (xs % 3) == 1] = (*BLANCO[0], 255)
    t[-1, (xs % 3) == 2] = (0, 0, 0, 0)
    return t, None


reg('encaje', encaje)


def bandas(tw, th, cara, s):
    """El corse de la referencia: bandas anchas claras con su sombra, separadas por tiras negras."""
    if cara in ('arriba', 'abajo'):
        return _imagen(np.full((th, tw), 1), TELA), None
    t = np.zeros((th, tw, 4), np.uint8)
    for y in range(th):
        k = y % 5
        if k == 0:
            c = (*TELA[0], 255)
        elif k == 1:
            c = (*BLANCO[4], 255)
        elif k in (2, 3):
            c = (*BLANCO[2 if k == 2 else 1], 255)
        else:
            c = (*TELA[1], 255)
        t[y, :] = c
    t[:, 0] = (*TELA[0], 255)
    t[:, -1] = (*TELA[0], 255)
    return t, None


reg('bandas', bandas)


def medias(tw, th, cara, s):
    idx = np.full((th, tw), 1)
    idx[:, ::3] = 2
    return _imagen(_bisel(idx, 1, 1), TELA), None


reg('medias', medias)


def escama(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.full((th, tw), 2)
    idx[((xs + (ys // 2) % 2 * 2) % 4 == 0)] = 1
    idx[(ys % 2 == 0) & ((xs + (ys // 2) % 2 * 2) % 4 == 2)] = 3
    return _imagen(_bisel(idx, 1, 1), ESCAMA), None


reg('escama', escama)


def tachas(tw, th, cara, s):
    """El cinturon de la referencia: negro con cuadros blancos."""
    t = _imagen(_bisel(np.full((th, tw), 1), 1, 1), TELA)
    if cara in ('arriba', 'abajo') or th < 3:
        return t, None
    for x in range(1, tw - 1, 4):
        t[1:th - 1, x:x + 2] = (*BLANCO[3], 255)
        t[1, x:x + 2] = (*BLANCO[4], 255)
    return t, None


reg('tachas', tachas)


def calavera(tw, th, cara, s):
    """El adorno de calavera de la referencia (en la cara de delante; lo demas, hueso)."""
    if cara != 'frente':
        return _imagen(np.full((th, tw), 2), HUESO), None
    dib = ["..wwww..",
           ".wwwwww.",
           "wwwwwwww",
           "wkkwwkkw",
           "wkkwwkkw",
           "wwwkkwww",
           ".wwwwww.",
           "..wkwk.."]
    col = {'w': (*HUESO[3], 255), 'k': (*TELA[0], 255), '.': (0, 0, 0, 0)}
    t = np.array([[col[ch] for ch in f] for f in dib], np.uint8)
    t = np.array(Image.fromarray(t).resize((tw, th), Image.NEAREST))
    return t, None


reg('calavera', calavera)


def _hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def emisivo(c1, c2, nombre):
    def f(tw, th, cara, s):
        return qm._emisivo(c1, c2, max(2, tw), max(2, th)), None
    return reg(nombre, f, pleno=True)


emisivo('ffe0e4', 'ff2a44', 'gema')


def porcelana(tw, th, cara, s):
    """La porcelana del antifaz: blanca con su canto y, por delante, una filigrana de oro en zigzag."""
    t = _imagen(_bisel(np.full((th, tw), 3), 1, 1), HUESO)
    if cara == 'frente' and tw >= 6 and th >= 4:
        ys, xs = np.mgrid[0:th, 0:tw]
        onda = (xs // 2) % 4
        fila = np.where(onda < 2, onda, 4 - onda)
        m = (ys - 1 == fila % max(1, th - 2)) & (xs > 0) & (xs < tw - 1)
        t[m] = (*ORO[3], 255)
        t[(ys == th - 2) & (xs % 4 == 1)] = (*ROJO[3], 255)
    return t, None


reg('porcelana', porcelana)


def porcelana_rota(tw, th, cara, s):
    """La media mascara: porcelana lisa (sin canto, para que las piezas se lean como una sola) y, por
    delante, grietas quebradas con un pixel rojo encendido a su lado (la luz de dentro). Las grietas se
    dibujan en coordenadas de la cara entera, asi siguen de una pieza a otra."""
    t = _imagen(np.full((th, tw), 3), HUESO)
    if cara != 'frente':
        return t, None
    m = MASCARA_GRIETAS.get((tw, th, (s - tw * 7 - th) // 131))
    if m is None:
        return t, None
    if m.shape != (th, tw):
        m = np.array(Image.fromarray(m.astype(np.uint8) * 255).resize((tw, th), Image.NEAREST)) > 0
    t[m] = (34, 6, 12, 255)
    luz = np.zeros_like(m)
    luz[:, 1:] |= m[:, :-1]
    luz &= ~m
    t[luz] = (255, 64, 84, 255)
    return t, _emis(t, luz, 210)


MASCARA_GRIETAS = {}


def _grietas(W, H, semilla=3):
    """Las grietas de toda la mascara (W x H pixeles): tres que bajan quebradas y alguna rama."""
    rng = random.Random(semilla)
    m = np.zeros((H, W), bool)
    for x0 in (int(W * 0.18), int(W * 0.55), int(W * 0.82)):
        x, y = x0, 0
        while y < H:
            if 0 <= x < W:
                m[y, x] = True
            if rng.random() < 0.5:
                x += rng.choice((-1, 1))
                if 0 <= x < W:
                    m[y, x] = True
            if rng.random() < 0.06:
                bx, by = x, y
                for _ in range(rng.randint(3, 6)):
                    bx += rng.choice((-1, 1))
                    by += 1
                    if 0 <= bx < W and by < H:
                        m[by, bx] = True
            y += 1
    return m


reg('porcelana_rota', porcelana_rota)


# ----------------------------------------------------------------------
#  Las caras pintadas: la mitad izquierda de cada una, que se copia en espejo
# ----------------------------------------------------------------------
COLORES = {
    'h': (*PELO[0], 255), 'H': (*PELO[1], 255),
    's': (*PIEL[2], 255), 'S': (*PIEL[1], 255), 'q': (*PIEL[3], 255), 'x': (200, 168, 160, 255),
    'k': (18, 10, 18, 255), 'K': (74, 48, 60, 255),
    'w': (244, 240, 242, 255), 'W': (200, 194, 208, 255),
    'r': (214, 36, 56, 255), 'R': (122, 12, 30, 255), 'n': (255, 112, 120, 255), 'z': (255, 255, 255, 255),
    'b': (232, 150, 160, 255), 'B': (240, 182, 188, 255),
    'm': (178, 38, 60, 255), 'M': (108, 16, 34, 255), 'l': (222, 96, 112, 255),
    'c': (46, 32, 42, 255),
    'g': (150, 160, 180, 255), 'G': (78, 86, 108, 255), 'e': (206, 214, 228, 255),
    'o': (92, 64, 92, 255), 'O': (150, 112, 140, 255),
    'v': (128, 28, 60, 255),
    'Y': (255, 58, 74, 255), 'y': (255, 226, 228, 255), 'u': (150, 10, 28, 255),
}
BRILLAN = set('Yyu')


def espejo(izq, cambios=None, derecha=None):
    """La cara entera a partir de su mitad izquierda; 'cambios' pone pixeles sueltos {(fila, col): letra}
    y 'derecha' recolorea la mitad derecha {letra: letra} (para un ojo de cada color)."""
    filas = []
    for f in izq:
        d = f[::-1]
        if derecha:
            d = ''.join(derecha.get(ch, ch) for ch in d)
        filas.append(list(f + d))
    for (y, x), ch in (cambios or {}).items():
        filas[y][x] = ch
    return [''.join(f) for f in filas]


def pinta(filas):
    alto, ancho = len(filas), len(filas[0])
    t = np.zeros((alto, ancho, 4), np.uint8)
    m = np.zeros((alto, ancho), bool)
    for y, f in enumerate(filas):
        assert len(f) == ancho, (y, f)
        for x, ch in enumerate(f):
            t[y, x] = COLORES[ch]
            m[y, x] = ch in BRILLAN
    return t, m


CARAS = {}

# C1 · Clasica: la de Minecraft de siempre, 8 x 8
CARAS['C1'] = dict(forma='cubo', flequillo=6.0, filas=espejo([
    "hhhh",
    "hhhh",
    "Hsss",
    "Hkks",
    "Hwrs",
    "sbss",
    "sssm",
    "ssss"]))

# C2 · Chibi: como la referencia: la cabeza mas ancha que alta y los ojos grandes y bajos (18 x 16)
CARAS['C2'] = dict(forma='ancha', flequillo=5.0, filas=espejo([
    "hhhhhhhhh",
    "hhhhhhhhh",
    "hhhhhhhhh",
    "hhhhhhhhh",
    "hhhhhhhhh",
    "Hhhhhhhhh",
    "Hssssssss",
    "Hsskkkkss",
    "HskzRRRss",
    "HssrrRrss",
    "Hssnrrnss",
    "sBbssssss",
    "sssssssss",
    "sssssssKs",
    "ssssssssK",
    "sssssssss"]))

# C3 · Anime: ojos de 4 x 3 con la pestana y su rabillo, el blanco por fuera y dos brillos (16 x 16)
CARAS['C3'] = dict(forma='cubo', flequillo=5.0, filas=espejo([
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "Hhhhhhhh",
    "Hscccsss",
    "Hsssssss",
    "Hkkkkkss",
    "HswRRRss",
    "Hswzrrss",
    "HsWrnrss",
    "ssbbssss",
    "ssssssss",
    "sssssssm",
    "ssssssss"], {(12, 8): 'S'}))

# C4 · Reina: almendrados con la raya y el rabillo, la sombra, la pupila rasgada, la ceja en arco y los
# labios llenos; la mandibula en V (24 x 24, la barbilla mas estrecha)
CARAS['C4'] = dict(forma='v', flequillo=6.2, filas=espejo([
    "hhhhhhhhhhhh",
    "hhhhhhhhhhhh",
    "hhhhhhhhhhhh",
    "hhhhhhhhhhhh",
    "hhhhhhhhhhhh",
    "hhhhhhhhhhhh",
    "Hhhhhhhhhhhh",
    "Hsssssssssss",
    "Hsssccccssss",
    "Hsccsssscccs",
    "Hsssssssssss",
    "Hksskkkkksss",
    "HskkwzRRwkss",
    "HsskWrkrWKss",
    "HsssKKnKKsss",
    "HssssSSSssss",
    "SssBBsssssss",
    "Sssssssssssq",
    "SsssssssssSs",
    "Sssssssssmms",
    "ssssssssmmmm",
    "ssssssssMMMM",
    "sssssssssllS",
    "ssssssssssSS"]))

# C5 · Relieve suave: los ojos pintados y la ceja, la nariz, la pestana y los labios de bloque (16 x 16)
CARAS['C5'] = dict(forma='cubo', flequillo=5.0, relieve=True, filas=espejo([
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "Hhhhhhhh",
    "Hsssssss",
    "Hsssssss",
    "HsKKKKss",
    "HswRRRss",
    "Hswzrrss",
    "HsWrnrss",
    "ssbbssss",
    "ssssssss",
    "ssssssss",
    "ssssssss"]))

# C6 · Monstruo: el blanco del ojo negro, el iris encendido y rasgado, la ceja de enfado, las marcas que
# bajan de los ojos, los labios oscuros y dos colmillos de bloque (16 x 16)
CARAS['C6'] = dict(forma='cubo', flequillo=5.2, colmillos=True, filas=espejo([
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "Hhhhhhhh",
    "Hccsssss",
    "Hsscccss",
    "Hkkkkkcs",
    "HskYkYks",
    "HskykYks",
    "Hsskkkss",
    "Hssvssss",
    "Hssvssss",
    "HsssvMMM",
    "sssssssm"]))

# C7 · Muneca gotica: un ojo rojo y otro gris (como la referencia), la sombra oscura, una lagrima negra,
# una costura en la mejilla y los labios oscuros (16 x 16)
CARAS['C7'] = dict(forma='cubo', flequillo=5.0, filas=espejo([
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "hhhhhhhh",
    "Hhhhhhhh",
    "Hsssssss",
    "HoOOOOss",
    "Hkkkkkss",
    "HowRRRss",
    "Hswzrrss",
    "HsKrrKss",
    "ssoooSss",
    "ssssssss",
    "ssssssMM",
    "sssssssm"],
    {(12, 3): 'k', (13, 3): 'k', (14, 3): 'k', (12, 11): 'K', (12, 13): 'K', (13, 12): 'K', (14, 11): 'K', (14, 13): 'K'},
    derecha={'r': 'g', 'R': 'G', 'n': 'e'}))

# C8 · Media mascara: porcelana rota que tapa media cara, con el ojo encendido en su agujero y luz roja en
# las grietas; la otra mitad, pintada como C3, y los labios oscuros (16 x 16)
_C3_DER = [f[::-1] for f in ("Hscccsss", "Hsssssss", "Hkkkkkss", "HswRRRss", "Hswzrrss", "HsWrnrss", "ssbbssss")]
CARAS['C8'] = dict(forma='cubo', flequillo=5.0, mascara=True, filas=[
    "hhhhhhhh" + "hhhhhhhh",
    "hhhhhhhh" + "hhhhhhhh",
    "hhhhhhhh" + "hhhhhhhh",
    "hhhhhhhh" + "hhhhhhhh",
    "hhhhhhhh" + "hhhhhhhh",
    "Hhhhhhhh" + "hhhhhhhH",
    "Hsssssss" + _C3_DER[0],
    "Hsssssss" + _C3_DER[1],
    "Hsuuuuss" + _C3_DER[2],
    "HsuyYuss" + _C3_DER[3],
    "HsuYyuss" + _C3_DER[4],
    "Hsuuuuss" + _C3_DER[5],
    "ssssssss" + _C3_DER[6],
    "ssssssss" + "ssssssss",
    "sssssMMM" + "MMMsssss",
    "ssssssml" + "lmssssss"])

NOMBRES = {
    'C1': 'Clásica (8×8)', 'C2': 'Chibi, como la referencia', 'C3': 'Anime', 'C4': 'Reina (mandíbula en V)',
    'C5': 'Relieve suave', 'C6': 'Monstruo', 'C7': 'Muñeca gótica', 'C8': 'Media máscara rota',
}


# ----------------------------------------------------------------------
#  La cabeza: la forma, la cara recortada en cada caja y el pelo
# ----------------------------------------------------------------------
FORMAS = {
    # cajas (x0, x1, y0, y1, z0, z1) con el origen en la barbilla; la cara mira a +z
    'cubo': [(-4, 4, 0, 8, -4, 4)],
    'ancha': [(-4.5, 4.5, 0, 8, -4, 4)],
    'v': [(-4, 4, 7 / 3, 8, -4, 4), (-11 / 3, 11 / 3, 4 / 3, 7 / 3, -3.8, 3.95), (-3, 3, 1 / 3, 4 / 3, -3.4, 3.9),
          (-7 / 3, 7 / 3, 0, 1 / 3, -2.8, 3.85)],
}


def _recorte(nombre, img, emis, c0, c1, f0, f1):
    sub = np.ascontiguousarray(img[f0:f1, c0:c1])
    sube = np.ascontiguousarray(emis[f0:f1, c0:c1])

    def f(tw, th, cara, s):
        t = np.array(Image.fromarray(sub).resize((tw, th), Image.NEAREST))
        if not sube.any():
            return t, None
        m = np.array(Image.fromarray(sube.astype(np.uint8) * 255).resize((tw, th), Image.NEAREST)) > 0
        return t, _emis(t, m, 240)
    return reg(nombre, f)


def cabeza(out, Mh, cid, suelto=True):
    c = CARAS[cid]
    img, m = pinta(c['filas'])
    alto, ancho = img.shape[:2]
    cajas = FORMAS[c['forma']]
    W = cajas[0][1] - cajas[0][0]
    ppu = ancho / W                                   # pixeles de cara por unidad
    bm.PPB = ppu
    try:
        for i, (x0, x1, y0, y1, z0, z1) in enumerate(cajas):
            c0, c1 = int(round((x0 + W / 2) * ppu)), int(round((x1 + W / 2) * ppu))
            f0, f1 = int(round((8 - y1) * ppu)), int(round((8 - y0) * ppu))
            pin = _recorte('cara_%s_%d' % (cid, i), img, m, c0, c1, f0, f1)
            bm.cubo(out, Mh, x0, y0, z0, x1 - x0, y1 - y0, z1 - z0, P['piel'], caras={'frente': pin}, semilla=20 + i)
    finally:
        bm.PPB = PPB
    if c.get('relieve'):
        relieve(out, Mh)
    if c.get('colmillos'):
        for s in (1, -1):
            bm.cubo(out, Mh, s * 0.75 - 0.25, 0.55, 3.9, 0.5, 0.75, 0.3, P['hueso'], semilla=26)
            bm.cubo(out, Mh, s * 0.75 - 0.15, 0.3, 3.95, 0.3, 0.3, 0.22, P['hueso'], semilla=27)
    if c.get('mascara'):
        mascara(out, Mh)
    pelo(out, Mh, W, c['flequillo'], suelto)


reg('pestana', liso(_r('080508', '120a10', '1c1018', '2a1a24', '3c2a36'), 2, 1, 0))
reg('labio_arriba', liso(_r('4a0a18', '7a1426', 'a8243a', 'c83c52', 'e86a7c'), 2, 0, 1))
reg('labio_abajo', liso(_r('5a0e1c', '8c1a30', 'c03a52', 'dc6276', 'f4a0ac'), 2, 1, 0))


def relieve(out, Mh):
    """C5: la ceja, la pestana, la nariz y los labios en bloques que salen poco (medio pixel)."""
    for s in (1, -1):
        M = Mh @ vr.T(s * 1.95, 5.05, 4.0) @ vr.Rz(s * 8 * D)
        bm.cubo(out, M, -1.0, 0.0, 0.0, 2.0, 0.42, 0.32, P['pelo'], semilla=30)                         # la ceja
        M = Mh @ vr.T(s * 2.0, 3.55, 4.0)
        bm.cubo(out, M, -1.15, 0.0, 0.0, 2.3, 0.45, 0.42, P['pestana'], semilla=31)                     # la pestana
        Mr = M @ vr.T(s * 1.15, 0.12, 0) @ vr.Rz(s * 25 * D)
        bm.cubo(out, Mr, 0.0 if s > 0 else -0.55, 0.0, 0.0, 0.55, 0.32, 0.38, P['pestana'], semilla=32)  # el rabillo
    bm.cubo(out, Mh, -0.35, 1.95, 4.0, 0.7, 1.3, 0.35, P['piel'], semilla=33)                          # la nariz
    bm.cubo(out, Mh, -0.5, 1.8, 4.0, 1.0, 0.5, 0.55, P['piel'], semilla=34)
    bm.cubo(out, Mh, -0.9, 0.98, 4.0, 1.8, 0.32, 0.2, P['labio_arriba'], semilla=35)                    # los labios
    bm.cubo(out, Mh, -0.7, 0.7, 4.0, 1.4, 0.3, 0.24, P['labio_abajo'], semilla=36)


def mascara(out, Mh):
    """C8: una media mascara de porcelana rota sobre la mitad de la cara que mira a la camara: el agujero
    del ojo (el ojo encendido detras), las grietas con luz roja, el canto de oro por el medio de la cara y
    una gema en la sien. Por debajo deja la boca a la vista."""
    z0, z1 = 4.0, 4.4
    bm.PPB = 6
    try:
        piezas = [(-4.45, 0.35, 3.6, 5.6), (-4.45, -3.0, 2.45, 3.6), (-1.0, 0.35, 2.45, 3.6), (-4.45, 0.35, 1.9, 2.45),
                  (-4.45, -1.3, 1.2, 1.9)]
        X0, X1, Y0, Y1 = -4.45, 0.35, 1.2, 5.6
        G = _grietas(int(round((X1 - X0) * 6)), int(round((Y1 - Y0) * 6)))
        for i, (x0, x1, y0, y1) in enumerate(piezas):
            c0, c1 = int(round((x0 - X0) * 6)), int(round((x1 - X0) * 6))
            f0, f1 = int(round((Y1 - y1) * 6)), int(round((Y1 - y0) * 6))
            MASCARA_GRIETAS[(c1 - c0, f1 - f0, (40 + i + 1) % 7)] = G[f0:f1, c0:c1]
            bm.cubo(out, Mh, x0, y0, z0, x1 - x0, y1 - y0, z1 - z0, P['porcelana_rota'], semilla=40 + i)
        bm.cubo(out, Mh, 0.2, 1.9, z0, 0.32, 3.7, z1 - z0 + 0.1, P['oro'], semilla=47)                    # el canto de oro
        bm.cubo(out, Mh, -1.3, 1.25, z0, 0.3, 0.65, z1 - z0 + 0.06, P['oro'], semilla=48)
        bm.cubo(out, Mh, -3.15, 3.55, z1 - 0.04, 2.3, 0.18, 0.1, P['oro'], semilla=49)                    # el filo del ojo
        bm.cubo(out, Mh, -3.95, 4.2, z1 - 0.05, 0.6, 0.6, 0.2, P['gema'], semilla=50)                     # la gema de la sien
    finally:
        bm.PPB = PPB


def vr_pt(M, p):
    return (M @ np.array([p[0], p[1], p[2], 1.0]))[:3]


def _caja_dir(out, p0, p1, ancho, pintor, semilla=0, extra=0.0, alto=None):
    """Una caja de p0 a p1 de seccion ancho x alto (el alto, hacia arriba del mundo)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    if L < 1e-4:
        return
    d = (p1 - p0) / L
    up = (0.0, 1.0, 0.0) if abs(d[1]) < 0.9 else (0.0, 0.0, 1.0)
    M = em.marco(p0, p1 - p0, up=up)
    a = ancho if alto is None else alto
    bm.cubo(out, M, -ancho / 2, -a / 2, -extra, ancho, a, L + 2 * extra, pintor, semilla=semilla)


def pelo(out, Mh, W, flequillo, suelto=True):
    """El pelo comun: el casco (la capa de encima de la cabeza), el flequillo en mechones que acaban en
    escalon, los dos mechones que enmarcan la cara y, como la referencia, ocho mechones gruesos y quebrados
    que salen hacia los lados y otros tres que caen por la espalda."""
    a = W / 2 + 0.5
    bm.cubo(out, Mh, -a, 7.0, -4.55, 2 * a, 1.6, 9.15, P['pelo'], semilla=60)                            # el casco
    bm.cubo(out, Mh, -a, -0.5, -4.6, 2 * a, 7.6, 1.0, P['pelo'], semilla=61)                             # la nuca
    for s in (1, -1):
        bm.cubo(out, Mh, (W / 2 - 0.05) if s > 0 else -a, 1.6, -4.4, a - W / 2 + 0.05, 5.6, 6.9, P['pelo'], semilla=62)
    # el flequillo: siete mechones con la punta en escalon (los del medio, mas cortos)
    xs = np.linspace(-W / 2 - 0.2, W / 2 + 0.2, 8)
    caida = [0.6, 0.15, 0.5, -0.3, -0.3, 0.5, 0.15, 0.6]
    for j in range(7):
        x0, x1 = xs[j], xs[j + 1]
        yb = flequillo - (caida[j] + caida[j + 1]) / 2
        M = Mh @ vr.T((x0 + x1) / 2, 7.2, 4.0) @ vr.Rz((j - 3) * 2.5 * D)
        w = x1 - x0 + 0.08
        bm.cubo(out, M, -w / 2, yb - 7.2 + 0.45, 0.0, w, 7.2 - yb - 0.45 + 0.4, 0.55, P['pelo'], semilla=63 + j % 3)
        bm.cubo(out, M, -w / 4, yb - 7.2, 0.05, w / 2, 0.5, 0.45, P['pelo'], semilla=66)
    # los mechones de la cara
    for s in (1, -1):
        M = Mh @ vr.T(s * (W / 2 + 0.05), 7.2, 3.6) @ vr.Rz(s * 4 * D)
        bm.cubo(out, M, -0.9, -8.6, -0.8, 1.6, 8.8, 1.45, P['pelo'], semilla=67)
        bm.cubo(out, M, -0.6, -9.6, -0.6, 1.0, 1.2, 1.05, P['pelo'], semilla=68)
    if not suelto:
        TRAZAS = []
    else:
        TRAZAS = None
    # los mechones gruesos que se abren: cada uno sale de la cabeza, se quiebra y cae
    TRAZAS = TRAZAS if TRAZAS is not None else [  # (base, tramos), en el marco de la cabeza, para el lado +x
        ((W / 2 + 0.3, 6.4, -0.6), [(2.8, 1.6, -0.6), (2.6, -3.0, -0.4), (0.9, -5.6, 0.3), (0.2, -3.2, 0.2)]),
        ((W / 2 + 0.2, 4.6, -2.2), [(3.0, 0.2, -1.6), (1.6, -4.6, -0.8), (0.6, -6.8, 0.2), (0.1, -3.4, 0.2)]),
        ((W / 2 - 0.6, 3.0, -3.6), [(1.6, -1.2, -2.2), (0.8, -6.0, -0.6), (0.3, -6.2, 0.4), (0.0, -3.0, 0.2)]),
    ]
    for s in (1, -1):
        for i, (base, tramos) in enumerate(TRAZAS):
            p = np.array((s * base[0], base[1], base[2]))
            pts = [p]
            for t in tramos:
                p = p + np.array((s * t[0], t[1], t[2]))
                pts.append(p)
            pts = [vr_pt(Mh, q) for q in pts]
            g = 1.95 - 0.12 * i
            for k in range(len(pts) - 1):
                gk = g * (1.0, 0.88, 0.74, 0.55)[k]
                _caja_dir(out, pts[k], pts[k + 1], gk, P['mechon'], semilla=70 + i + k, extra=gk * 0.32)
    for j, x in enumerate((-2.4, 0.0, 2.4)):                                                            # por la espalda
        p0 = vr_pt(Mh, (x, 5.0, -4.3))
        p1 = vr_pt(Mh, (x * 1.25, -4.0, -5.4))
        p2 = vr_pt(Mh, (x * 1.4, -12.0, -4.6 - 0.4 * abs(x)))
        _caja_dir(out, p0, p1, 2.6, P['mechon'], semilla=80 + j, extra=0.6)
        _caja_dir(out, p1, p2, 2.2, P['mechon'], semilla=83 + j, extra=0.5)


# ----------------------------------------------------------------------
#  El torso y los pechos
# ----------------------------------------------------------------------
def torso(out, pid='P2'):
    """El torso en cajas escalonadas (cadera ancha, cintura estrecha, costillas, hombros) con el
    cuello y la gargantilla, y el pecho de cada opcion."""
    ropa = P['bandas'] if pid == 'P3' else P['vino']
    escalones = [  # (y0, y1, medio ancho, medio fondo, pintor)
        (11.0, 12.6, 3.7, 2.1, P['vino']), (12.6, 13.8, 3.45, 2.0, P['vino']), (13.8, 15.0, 3.15, 1.9, ropa),
        (15.0, 17.4, 2.9, 1.75, ropa), (17.4, 18.4, 3.2, 1.85, ropa), (18.4, 21.2, 3.5, 1.9, ropa)]
    for i, (y0, y1, hx, hz, pin) in enumerate(escalones):
        bm.cubo(out, I4, -hx, y0, -hz, 2 * hx, y1 - y0, 2 * hz, pin, semilla=100 + i)
    bm.cubo(out, I4, -3.2, 11.3, -2.6, 6.4, 2.4, 0.6, P['vino'], semilla=107)                              # la grupa
    alto_tela = pid in ('P1', 'P6')
    bm.cubo(out, I4, -3.6, 21.2, -1.85, 7.2, 1.2, 3.7, P['vino'] if alto_tela else P['piel'], semilla=108)  # el pecho alto
    bm.cubo(out, I4, -3.9, 22.4, -1.8, 7.8, 1.6, 3.6, P['vino'] if pid == 'P6' else P['piel'], semilla=109)  # los hombros
    bm.cubo(out, I4, -1.1, 23.6, -1.0, 2.2, 1.8, 2.1, P['piel'], semilla=110)                              # el cuello
    if pid not in ('P5', 'P6'):
        bm.cubo(out, I4, -1.25, 24.0, -1.15, 2.5, 0.45, 2.4, P['tela'], semilla=111)                       # la gargantilla
    pecho(out, pid)


def copa(out, s, y0=18.6, y1=21.3, z0=1.85, sale=1.55, pin=None, borde=None):
    """Un pecho en dos cajas (la de delante algo menor, para que se lea redondo)."""
    pin = pin or P['vino']
    x0, x1 = s * 0.12, s * 3.1
    xa, xb = min(x0, x1), max(x0, x1)
    bm.cubo(out, I4, xa, y0, z0, xb - xa, y1 - y0, sale, pin, semilla=120)
    bm.cubo(out, I4, xa + 0.35, y0 + 0.3, z0 + sale, xb - xa - 0.7, y1 - y0 - 0.65, 0.45, pin, semilla=121)
    if borde is not None:
        bm.cubo(out, I4, xa - 0.05, y1 - 0.4, z0 - 0.05, xb - xa + 0.1, 0.45, sale + 0.1, borde, semilla=122)


def pecho(out, pid):
    if pid == 'P1':                                                    # Minecraft: una caja de un pixel
        bm.cubo(out, I4, -3.0, 19.0, 1.85, 6.0, 2.4, 1.0, P['vino'], semilla=130)
        bm.cubo(out, I4, -3.3, 21.1, 1.75, 6.6, 0.4, 0.4, P['blanco'], semilla=131)
    elif pid == 'P2':                                                  # dos bloques
        for s in (1, -1):
            copa(out, s)
    elif pid == 'P3':                                                  # el corse de la referencia
        for s in (1, -1):
            copa(out, s, pin=P['bandas'])
            M = vr.T(s * 3.05, 23.0, 1.55)
            bm.cubo(out, M, -1.0, -1.0, 0.0, 2.0, 2.0, 0.55, P['calavera'], semilla=132)                   # calaveras en los hombros
        bm.cubo(out, I4, -1.6, 21.2, 1.9, 3.2, 0.5, 0.35, P['encaje'], semilla=133)                         # el volante
        bm.cubo(out, I4, -0.8, 22.2, 1.85, 1.6, 1.6, 0.5, P['calavera'], semilla=134)                       # la calavera del escote
        bm.cubo(out, I4, -0.25, 13.8, 1.95, 0.5, 4.6, 0.12, P['blanco'], semilla=135)                      # el cordon
        for y in np.arange(14.2, 18.2, 0.8):
            bm.cubo(out, I4, -0.55, y, 1.98, 1.1, 0.18, 0.12, P['blanco'], semilla=136)
        bm.cubo(out, I4, -3.55, 12.6, -2.05, 7.1, 1.0, 4.1, P['tachas'], semilla=137)                    # el cinturon de tachas
    elif pid == 'P4':                                                  # escote de corazon
        for s in (1, -1):
            copa(out, s, y1=21.0)
            bm.cubo(out, I4, min(s * 0.12, s * 1.6), 20.75, 3.15, 1.48, 0.42, 0.25, P['encaje'], semilla=140)
            bm.cubo(out, I4, min(s * 1.6, s * 3.1), 20.95, 3.15, 1.5, 0.42, 0.25, P['encaje'], semilla=141)
            bm.cubo(out, I4, min(s * 0.12, s * 3.15), 20.6, 1.85, 3.03, 0.45, 1.75, P['encaje'], semilla=142)
        bm.cubo(out, I4, -0.3, 23.85, 1.15, 0.6, 0.6, 0.2, P['gema'], semilla=143)                         # la gema del cuello
        for s in (1, -1):                                                                                  # los tirantes
            bm.cubo(out, I4, s * 2.3 - 0.3, 21.0, 1.7, 0.6, 3.0, 0.3, P['vino'], semilla=144)
    elif pid == 'P5':                                                  # la coraza
        bm.cubo(out, I4, -3.6, 17.4, 1.8, 7.2, 3.9, 0.55, P['acero'], semilla=150)                         # el peto
        for s in (1, -1):
            x0 = min(s * 0.15, s * 3.25)
            bm.cubo(out, I4, x0, 18.4, 2.3, 3.1, 2.8, 0.95, P['acero'], semilla=151)                      # las copas en escalon
            bm.cubo(out, I4, x0 + 0.4, 18.7, 3.25, 2.3, 2.2, 0.4, P['acero'], semilla=152)
            bm.cubo(out, I4, x0 - 0.05, 21.0, 2.2, 3.2, 0.32, 1.12, P['oro'], semilla=154)               # el filo del escote
        bm.cubo(out, I4, -0.2, 17.4, 2.3, 0.4, 3.75, 0.75, P['oro'], semilla=155)                          # la cresta del medio
        bm.cubo(out, I4, -0.42, 17.75, 2.95, 0.84, 0.84, 0.3, P['gema'], semilla=156)
        for j, (y, w) in enumerate(((16.2, 3.05), (15.0, 3.2), (13.8, 3.4))):                         # el vientre en lamas
            bm.cubo(out, I4, -w, y, 1.75 + 0.1 * j, 2 * w, 1.3, 0.35, P['acero'], semilla=157 + j)
            bm.cubo(out, I4, -w - 0.03, y, 2.05 + 0.1 * j, 2 * w + 0.06, 0.25, 0.1, P['oro'], semilla=160)
        bm.cubo(out, I4, -1.3, 24.0, -1.2, 2.6, 0.8, 2.5, P['acero'], semilla=161)                         # la gargantilla de acero
        bm.cubo(out, I4, -1.38, 24.65, -1.28, 2.76, 0.22, 2.66, P['oro'], semilla=162)
    elif pid == 'P6':                                                  # vestido cerrado con lazo
        for s in (1, -1):
            copa(out, s, sale=1.3)
        bm.cubo(out, I4, -1.35, 23.5, -1.25, 2.7, 1.3, 2.6, P['blanco'], semilla=170)                      # el cuello alto
        bm.cubo(out, I4, -1.5, 24.6, -1.35, 3.0, 0.4, 2.8, P['encaje'], semilla=171)
        for s in (1, -1):                                                                                  # el lazo
            M = vr.T(s * 0.62, 22.9, 1.95) @ vr.Rz(-s * 10 * D)
            bm.cubo(out, M, -0.62, -0.42, 0.0, 1.24, 0.84, 0.45, P['rojo'], semilla=172)
            M = vr.T(s * 0.35, 22.6, 2.05) @ vr.Rz(s * 18 * D)
            bm.cubo(out, M, -0.2, -2.0, 0.0, 0.42, 2.0, 0.2, P['rojo'], semilla=173)
        bm.cubo(out, I4, -0.3, 22.6, 1.95, 0.6, 0.6, 0.55, P['rojo'], semilla=174)
        for y in (17.6, 16.4, 15.2, 14.0):
            bm.cubo(out, I4, -0.2, y, 1.7, 0.4, 0.4, 0.2, P['oro'], semilla=175)
        bm.cubo(out, I4, -3.95, 22.2, -1.85, 7.9, 0.5, 3.7, P['blanco'], semilla=176)                     # el canesu


# ----------------------------------------------------------------------
#  Brazos y manos
# ----------------------------------------------------------------------
HOMBRO = np.array((5.4, 22.6, 0.0))


def caja(out, M, x0, x1, y0, y1, z0, z1, pin, semilla=0):
    bm.cubo(out, M, x0, y0, z0, x1 - x0, y1 - y0, z1 - z0, pin, semilla=semilla)


def mano(out, M, s, estilo, pin, una=None, k=1.0):
    """La mano en el marco de la muneca (los dedos hacia -y, la palma mirando al cuerpo, el pulgar
    delante). 'bloque': la palma, los dedos juntos y el pulgar; 'dedos': cuatro dedos de dos falanges
    algo doblados; 'garra': mas grande, con unas largas."""
    pal = -s                                                       # hacia donde mira la palma (x local)
    caja(out, M, -0.65 * k, 0.65 * k, -2.0 * k, 0.2, -1.15 * k, 1.15 * k, pin, semilla=200)       # la palma
    if estilo == 'bloque':
        Mf = M @ vr.T(pal * 0.45 * k, -2.0 * k, 0) @ vr.Rz(-pal * 18 * D)
        caja(out, Mf, -1.05 * k if pal > 0 else -0.05, 0.05 if pal > 0 else 1.05 * k, -1.5 * k, 0.05, -1.1 * k, 1.1 * k, pin, semilla=201)
    else:
        largo = 1.0 if estilo == 'dedos' else 1.3
        for j in range(4):
            zc = (-0.83 + 0.555 * j) * k
            Mf = M @ vr.T(pal * 0.3 * k, -1.95 * k, zc) @ vr.Rz(-pal * 14 * D)
            caja(out, Mf, -0.42 * k, 0.42 * k, -largo * k, 0.05, -0.25 * k, 0.25 * k, pin, semilla=202)
            Mg = Mf @ vr.T(0, -largo * k, 0) @ vr.Rz(-pal * 22 * D)
            l2 = (0.8 - 0.08 * abs(j - 1.5)) * k
            caja(out, Mg, -0.36 * k, 0.36 * k, -l2, 0.05, -0.22 * k, 0.22 * k, pin, semilla=203)
            if una is not None:
                Mu = Mg @ vr.T(0, -l2, 0) @ vr.Rz(-pal * 25 * D)
                lu = (0.55 if estilo == 'dedos' else 1.1) * k
                caja(out, Mu, -0.28 * k, 0.28 * k, -lu, 0.05, -0.2 * k, 0.2 * k, una, semilla=204)
                caja(out, Mu @ vr.T(0, -lu, 0), -0.14 * k, 0.14 * k, -lu * 0.6, 0.02, -0.1 * k, 0.1 * k, una, semilla=205)
    Mp = M @ vr.T(pal * 0.35 * k, -0.6 * k, 0.95 * k) @ vr.Rx(-35 * D) @ vr.Rz(-pal * 20 * D)          # el pulgar
    caja(out, Mp, -0.32 * k, 0.32 * k, -1.35 * k, 0.1, -0.32 * k, 0.32 * k, pin, semilla=206)
    if una is not None and estilo == 'garra':
        caja(out, Mp @ vr.T(0, -1.35 * k, 0), -0.2 * k, 0.2 * k, -0.8 * k, 0.02, -0.18 * k, 0.18 * k, una, semilla=207)


POSE_BRAZO = {1: dict(abd=7, flex=4, codo=14, mun=0), -1: dict(abd=10, flex=8, codo=78, mun=10, giro=38)}


def marcos_brazo(s, pose, grueso=1.5, grueso2=1.4, L1=5.6, L2=5.0):
    Mh = (vr.T(s * HOMBRO[0], HOMBRO[1], HOMBRO[2]) @ vr.Rz(s * pose['abd'] * D) @ vr.Rx(-pose['flex'] * D)
          @ vr.Ry(-s * pose.get('giro', 0) * D))
    Mc = Mh @ vr.T(0, -L1, -grueso) @ vr.Rx(-pose['codo'] * D) @ vr.T(0, 0, grueso2)       # el codo gira por la espalda
    Mm = Mc @ vr.T(0, -L2, 0) @ vr.Rx(-pose['mun'] * D)
    return Mh, Mc, Mm


def brazo(out, s, bid='B0', pose=None):
    pose = pose or POSE_BRAZO[s]
    if bid == 'B1':                                                    # Minecraft: una caja de 3 x 12
        Mh = vr.T(s * HOMBRO[0], HOMBRO[1], HOMBRO[2]) @ vr.Rz(s * pose['abd'] * D) @ vr.Rx(-min(pose['codo'], 40) * D)
        caja(out, Mh, -1.5, 1.5, -10.6, 1.4, -1.5, 1.5, P['piel'], semilla=210)
        caja(out, Mh, -1.75, 1.75, -3.4, 1.65, -1.75, 1.75, P['vino'], semilla=211)
        return
    if bid in ('B0', 'B2'):                                            # dos cajas con el codo limpio y la mano de bloque
        Mh, Mc, Mm = marcos_brazo(s, pose)
        caja(out, Mh, -1.5, 1.5, -5.6, 1.4, -1.5, 1.5, P['piel'], semilla=212)
        caja(out, Mc, -1.4, 1.4, -5.0, 0.0, -1.4, 1.4, P['piel'], semilla=213)
        if bid == 'B2':
            caja(out, Mh, -1.75, 1.75, -2.6, 1.65, -1.75, 1.75, P['vino'], semilla=214)                    # la manga corta
            caja(out, Mc, -1.62, 1.62, -5.0, -4.1, -1.62, 1.62, P['encaje'], semilla=215)                 # el puno
        mano(out, Mm, s, 'bloque', P['piel'])
    elif bid == 'B3':                                                  # fino, con guante largo
        Mh, Mc, Mm = marcos_brazo(s, pose, 1.3, 1.25)
        caja(out, Mh, -1.3, 1.3, -2.2, 1.4, -1.3, 1.3, P['piel'], semilla=216)
        caja(out, Mh, -1.35, 1.35, -5.6, -2.2, -1.3, 1.35, P['tela'], semilla=217)
        caja(out, Mh, -1.5, 1.5, -2.6, -1.9, -1.5, 1.5, P['encaje'], semilla=218)
        caja(out, Mc, -1.25, 1.25, -5.0, 0.0, -1.25, 1.25, P['tela'], semilla=219)
        mano(out, Mm, s, 'dedos', P['tela'], k=0.92)
    elif bid == 'B4':                                                  # manga abullonada
        Mh, Mc, Mm = marcos_brazo(s, pose, 1.3, 1.25)
        caja(out, Mh, -1.3, 1.3, -5.6, 0.0, -1.3, 1.3, P['piel'], semilla=220)
        for w, y0, y1 in ((2.3, -2.6, 1.6), (2.0, -3.0, 1.9), (1.7, -3.2, 2.1)):
            caja(out, Mh, -w, w, y0, y1, -w * (2.0 / 2.3), w * (2.0 / 2.3), P['vino'], semilla=221)
        caja(out, Mh, -1.85, 1.85, -3.4, -2.8, -1.6, 1.6, P['encaje'], semilla=222)
        caja(out, Mc, -1.25, 1.25, -5.0, 0.0, -1.25, 1.25, P['piel'], semilla=223)
        caja(out, Mc, -1.5, 1.5, -5.0, -4.2, -1.5, 1.5, P['encaje'], semilla=224)
        caja(out, Mc, -0.3, 0.3, -4.9, -4.3, 1.5, 1.85, P['rojo'], semilla=225)
        mano(out, Mm, s, 'dedos', P['piel'], k=0.92)
    elif bid == 'B5':                                                  # armadura: hombrera, codera y guantelete
        Mh, Mc, Mm = marcos_brazo(s, pose)
        caja(out, Mh, -1.5, 1.5, -5.6, 1.4, -1.5, 1.5, P['vino'], semilla=226)
        for j in range(3):                                                                             # la hombrera en tres placas
            Mj = Mh @ vr.T(s * (0.25 + 0.15 * j), 1.9 - 1.15 * j, 0) @ vr.Rz(s * (12 + 10 * j) * D)
            w = 2.15 - 0.12 * j
            caja(out, Mj, -w, w, -1.25, 0.0, -2.05 + 0.1 * j, 2.05 - 0.1 * j, P['acero'], semilla=227 + j)
            caja(out, Mj, -w - 0.08, w + 0.08, -1.25, -0.95, -2.13 + 0.1 * j, 2.13 - 0.1 * j, P['oro'], semilla=230)
        caja(out, Mh, -1.75, 1.75, -6.3, -4.5, -2.05, -0.2, P['acero'], semilla=231)                     # la codera
        caja(out, Mh, -0.5, 0.5, -6.1, -4.9, -2.35, -1.9, P['oro'], semilla=232)
        caja(out, Mc, -1.7, 1.7, -4.9, -0.3, -1.7, 1.7, P['acero'], semilla=233)                         # el brazal
        for y0 in (-4.9, -0.9):
            caja(out, Mc, -1.82, 1.82, y0, y0 + 0.55, -1.82, 1.82, P['oro'], semilla=234)
        mano(out, Mm, s, 'dedos', P['acero'], k=1.08)
    elif bid == 'B6':                                                  # garra de monstruo
        Mh, Mc, Mm = marcos_brazo(s, pose)
        caja(out, Mh, -1.5, 1.5, -5.6, 1.4, -1.5, 1.5, P['piel'], semilla=235)
        caja(out, Mc, -1.6, 1.6, -5.0, 0.0, -1.6, 1.6, P['escama'], semilla=236)
        caja(out, Mc, -1.85, 1.85, -1.4, 0.35, -1.85, 1.85, P['pelaje'], semilla=237)                    # la gorguera de pelo
        for j in range(3):                                                                             # las puas del antebrazo
            Mj = Mc @ vr.T(0.0, -1.6 - 1.25 * j, -1.6) @ vr.Rx(40 * D)
            caja(out, Mj, -0.35, 0.35, 0.0, 1.1 - 0.15 * j, -0.35, 0.35, P['garra'], semilla=238)
        mano(out, Mm, s, 'garra', P['escama'], una=P['garra'], k=1.25)


# ----------------------------------------------------------------------
#  Piernas y pies
# ----------------------------------------------------------------------
CADERA = np.array((1.75, 13.5, 0.0))
DY = 1.5                                        # lo que sube el cuerpo sobre las piernas largas
POSE_PIERNA = {1: dict(abd=2, flex=0, rodilla=4, pie=0), -1: dict(abd=3, flex=30, rodilla=42, pie=-8)}


def marcos_pierna(s, pose, g1=1.65, g2=1.5, L1=7.0, L2=6.0):
    Mt = vr.T(s * CADERA[0], CADERA[1], CADERA[2]) @ vr.Rz(s * pose['abd'] * D) @ vr.Rx(-pose['flex'] * D)
    Mr = Mt @ vr.T(0, -L1, g1) @ vr.Rx(pose['rodilla'] * D) @ vr.T(0, 0, -g2)                 # la rodilla gira por delante
    Mp = Mr @ vr.T(0, -L2, 0) @ vr.Rx((pose['flex'] - pose['rodilla'] - pose['pie']) * D)      # el pie vuelve a la horizontal
    return Mt, Mr, Mp


def pie(out, M, estilo, pin, s):
    if estilo == 'zapato':                                             # zapato de tira (mary jane)
        caja(out, M, -1.55, 1.55, -0.55, 0.35, -1.6, 3.0, pin, semilla=250)
        caja(out, M, -1.6, 1.6, -0.6, -0.35, -1.65, 3.05, P['cuero'], semilla=251)
        caja(out, M, -1.62, 1.62, 0.0, 0.3, 0.2, 0.75, pin, semilla=252)
    elif estilo == 'tacon':
        Mi = M @ vr.Rx(18 * D)
        caja(out, Mi, -1.45, 1.45, -0.5, 0.35, -1.5, 3.1, pin, semilla=253)
        caja(out, M, -0.45, 0.45, -1.55, -0.3, -1.45, -0.6, pin, semilla=254)
    elif estilo == 'bota':
        caja(out, M, -1.75, 1.75, -0.6, 0.6, -1.8, 3.2, pin, semilla=255)
        caja(out, M, -1.8, 1.8, -0.65, -0.35, -1.85, 3.25, P['cuero'], semilla=256)
        caja(out, M, -0.6, 0.6, -0.65, 0.0, -1.85, -1.0, pin, semilla=257)


def pierna(out, s, lid='L0', pose=None):
    pose = pose or POSE_PIERNA[s]
    g1, g2, L1, L2 = 1.65, 1.5, 7.0, 6.0
    if lid == 'L1':                                                    # Minecraft: una caja de 3,3 x 13,5
        Mt = vr.T(s * CADERA[0], CADERA[1], CADERA[2]) @ vr.Rz(s * pose['abd'] * D) @ vr.Rx(-pose['flex'] * 0.6 * D)
        caja(out, Mt, -g1, g1, -13.5, 0.6, -g1, g1, P['piel'], semilla=260)
        caja(out, Mt, -g1 - 0.1, g1 + 0.1, -13.5, -12.2, -g1 - 0.1, g1 + 0.25, P['tela'], semilla=261)
        caja(out, Mt, -g1 - 0.12, g1 + 0.12, -12.6, -12.3, -g1 - 0.12, g1 + 0.27, P['cuero'], semilla=262)
        return
    if lid in ('L0', 'L2'):                                            # dos cajas con la rodilla limpia
        Mt, Mr, Mp = marcos_pierna(s, pose)
        caja(out, Mt, -g1, g1, -L1, 0.6, -g1, g1, P['piel'], semilla=263)
        caja(out, Mr, -g2, g2, -L2, 0.0, -g2, g2, P['piel'], semilla=264)
        if lid == 'L2':
            caja(out, Mr, -g2 - 0.1, g2 + 0.1, -L2, -3.3, -g2 - 0.1, g2 + 0.1, P['medias'], semilla=265)  # el calcetin
            caja(out, Mr, -g2 - 0.18, g2 + 0.18, -3.55, -3.1, -g2 - 0.18, g2 + 0.18, P['encaje'], semilla=266)
        pie(out, Mp, 'zapato', P['tela'], s)
    elif lid == 'L3':                                                  # botas altas con la vuelta sobre la rodilla
        Mt, Mr, Mp = marcos_pierna(s, pose, g1, 1.55)
        caja(out, Mt, -g1, g1, -L1, 0.6, -g1, g1, P['piel'], semilla=267)
        caja(out, Mr, -1.55, 1.55, -L2, 0.0, -1.55, 1.55, P['cuero'], semilla=268)
        caja(out, Mr, -1.75, 1.75, -0.9, 0.9, -1.75, 1.75, P['cuero'], semilla=269)                     # la vuelta
        caja(out, Mr, -1.8, 1.8, 0.62, 0.92, -1.8, 1.8, P['oro'], semilla=270)
        for y in (-2.4, -3.7, -5.0):
            caja(out, Mr, -0.6, 0.6, y, y + 0.4, 1.5, 1.72, P['oro'], semilla=271)
        pie(out, Mp, 'bota', P['cuero'], s)
    elif lid == 'L4':                                                  # medias hasta el muslo con liga
        Mt, Mr, Mp = marcos_pierna(s, pose)
        caja(out, Mt, -g1, g1, -4.4, 0.6, -g1, g1, P['piel'], semilla=272)
        caja(out, Mt, -g1 + 0.03, g1 - 0.03, -L1, -4.4, -g1 + 0.03, g1 - 0.03, P['medias'], semilla=273)
        caja(out, Mt, -g1 - 0.12, g1 + 0.12, -4.9, -4.2, -g1 - 0.12, g1 + 0.12, P['encaje'], semilla=274)
        caja(out, Mt, -0.2, 0.2, -4.4, 0.4, g1 - 0.05, g1 + 0.12, P['tela'], semilla=275)                 # la liga
        caja(out, Mr, -g2, g2, -L2, 0.0, -g2, g2, P['medias'], semilla=276)
        pie(out, Mp, 'tacon', P['tela'], s)
    elif lid == 'L5':                                                  # estilizada: seccion de ocho lados que se afina
        Mt, Mr, Mp = marcos_pierna(s, pose, 1.45, 1.4)
        for kx, kz in ((1.0, 0.7), (0.7, 1.0)):
            caja(out, Mt, -1.75 * kx, 1.75 * kx, -3.6, 0.6, -1.75 * kz, 1.75 * kz, P['piel'], semilla=277)
            caja(out, Mt, -1.45 * kx, 1.45 * kx, -L1, -3.4, -1.45 * kz, 1.45 * kz, P['piel'], semilla=278)
            caja(out, Mr, -1.4 * kx, 1.4 * kx, -1.0, 0.0, -1.4 * kz, 1.4 * kz, P['medias'], semilla=279)
            caja(out, Mr, -1.5 * kx, 1.5 * kx, -3.4, -0.9, -1.75 * kz, 1.4 * kz, P['medias'], semilla=280)
            caja(out, Mr, -1.0 * kx, 1.0 * kx, -L2, -3.3, -1.0 * kz, 1.0 * kz, P['medias'], semilla=281)
        caja(out, Mt, -1.55, 1.55, -L1 + 0.15, -L1 + 0.75, -1.55, 1.55, P['encaje'], semilla=282)
        pie(out, Mp, 'tacon', P['tela'], s)
    elif lid == 'L6':                                                  # de bestia: el talon en alto
        a1, a2, a3 = (22 + (8 if s < 0 else 0)), 62, 54
        Mt = vr.T(s * CADERA[0], CADERA[1], CADERA[2]) @ vr.Rz(s * pose['abd'] * D) @ vr.Rx(-a1 * D)
        caja(out, Mt, -1.85, 1.85, -5.6, 0.6, -1.85, 1.85, P['pelaje'], semilla=283)
        Mr = Mt @ vr.T(0, -5.6, 1.85) @ vr.Rx(a2 * D) @ vr.T(0, 0, -1.45)                          # la rodilla, por delante
        caja(out, Mr, -1.45, 1.45, -5.0, 0.0, -1.45, 1.45, P['escama'], semilla=284)
        Mk = Mr @ vr.T(0, -5.0, -1.45) @ vr.Rx(-a3 * D) @ vr.T(0, 0, 1.2)                          # el corvejon, por detras
        caja(out, Mk, -1.2, 1.2, -3.8, 0.0, -1.2, 1.2, P['escama'], semilla=285)
        Mp = Mk @ vr.T(0, -3.8, 0) @ vr.Rx((a1 - a2 + a3) * D)
        caja(out, Mp, -1.45, 1.45, -0.75, 0.25, -1.3, 2.0, P['escama'], semilla=286)
        for j in range(3):
            Mu = Mp @ vr.T((j - 1) * 0.95, -0.35, 2.0) @ vr.Rx(25 * D)
            caja(out, Mu, -0.3, 0.3, -0.3, 0.3, -0.1, 0.9, P['garra'], semilla=287)
            caja(out, Mu @ vr.T(0, 0, 0.9) @ vr.Rx(30 * D), -0.18, 0.18, -0.2, 0.18, -0.05, 0.55, P['garra'], semilla=288)
        caja(out, Mt, -2.05, 2.05, -1.8, 0.8, -2.05, 2.05, P['pelaje'], semilla=289)                     # el mechon de la cadera
        caja(out, Mr, -1.65, 1.65, -1.2, 0.3, -1.65, 1.65, P['pelaje'], semilla=290)                     # el de la rodilla


def falda(out):
    """La falda corta de la figura base: dos escalones que se abren y el bajo de encaje."""
    bm.cubo(out, I4, -3.85, 11.3, -2.35, 7.7, 2.4, 4.7, P['vino'], semilla=290)
    bm.cubo(out, I4, -4.3, 9.6, -2.8, 8.6, 1.9, 5.6, P['vino'], semilla=291)
    bm.cubo(out, I4, -4.35, 9.2, -2.85, 8.7, 0.6, 5.7, P['encaje'], semilla=292)


# ----------------------------------------------------------------------
#  La figura y las fotos
# ----------------------------------------------------------------------
REPOSO_BRAZO = {1: dict(abd=9, flex=-4, codo=12, mun=4), -1: dict(abd=7, flex=6, codo=18, mun=4)}
REPOSO_PIERNA = {1: dict(abd=3, flex=-4, rodilla=5, pie=0), -1: dict(abd=2, flex=10, rodilla=16, pie=0)}


def figura(cid='C3', bid='B0', lid='L0', pid='P2', poses=True, suelto=True):
    """La figura: el cuerpo de arriba se monta con la cadera a 12 y se sube DY sobre las piernas."""
    arriba = []
    torso(arriba, pid)
    for s in (1, -1):
        brazo(arriba, s, bid, None if poses else REPOSO_BRAZO[s])
    falda(arriba)
    Mh = vr.T(0, 25.0, 0.15) @ vr.Rx(4 * D)
    cabeza(arriba, Mh, cid, suelto)
    out = qm.transformar(arriba, vr.T(0, DY, 0))
    for s in (1, -1):
        pierna(out, s, lid, None if poses else REPOSO_PIERNA[s])
    return out


RAPIDO = os.environ.get('RAPIDO') == '1'
K = 0.5 if RAPIDO else 1.0
SS = 1 if RAPIDO else 2


def perfilar(lz, mascara, grosor, color=(1.0, 0.97, 1.0)):
    zc = np.where(mascara, lz.z, np.inf)
    for _ in range(grosor):
        e = zc.copy()
        e[1:] = np.minimum(e[1:], zc[:-1])
        e[:-1] = np.minimum(e[:-1], zc[1:])
        e[:, 1:] = np.minimum(e[:, 1:], zc[:, :-1])
        e[:, :-1] = np.minimum(e[:, :-1], zc[:, 1:])
        zc = np.where(mascara, zc, e)
    borde = ~mascara & np.isfinite(zc) & (lz.z > zc)
    lz.color[borde] = color
    lz.alfa[borde] = 1.0
    lz.emis[borde] = np.array(color) * 0.12


def foto(qs, ojo, obj, fov, nombre, out_dir, ancho=900, alto=900):
    W, H = int(ancho * K), int(alto * K)
    lz = qe.Lienzo(W * SS, H * SS)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    luces = [((-0.55, 0.7, 0.75), (1.0, 0.96, 0.94), 0.95, 'llave'), ((0.6, 0.35, -1.0), (0.8, 0.62, 1.0), 0.85, 'contra'),
             ((0.7, -0.1, 0.7), (0.5, 0.46, 0.6), 0.32, 'llave')]
    qm.dibujar(lz, cam, qs, luces, (0.36, 0.34, 0.4), None, 1.35)
    perfilar(lz, lz.alfa > 0, max(1, int(round(3 * SS * K))))

    def baja(a):
        return np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    alfa = baja(lz.alfa)[..., None]
    col = baja(lz.color)
    emis = baja(qe.tono(lz.emis))
    y = np.linspace(0, 1, H)[:, None, None]
    fondo = np.array((0.08, 0.07, 0.12)) * (1 - y) + np.array((0.23, 0.19, 0.29)) * y
    fondo = np.broadcast_to(fondo, (H, W, 3))
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis, radios=((2 * K, 0.5), (8 * K, 0.35), (22 * K, 0.25))))
    arr = qe.vineta(arr, 0.3)
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out_dir, nombre + '.jpg'), quality=92)
    print('ok', nombre, flush=True)


def escena(clave, out_dir):
    if clave == 'F0':
        foto(figura(poses=False), (-20.0, 23.0, 44.0), (0.0, 18.2, 0.0), 44, clave, out_dir, 900, 1100)
    elif clave.startswith('C'):
        foto(figura(cid=clave, poses=False), (-10.0, 33.0, 29.0), (0.0, 29.6, 2.0), 34, clave, out_dir)
    elif clave.startswith('B'):
        foto(figura(bid=clave, suelto=False), (-25.0, 25.0, 22.0), (0.0, 20.0, 0.5), 42, clave, out_dir)
    elif clave.startswith('L'):
        foto(figura(lid=clave, suelto=False), (-17.0, 10.0, 27.0), (0.0, 7.6, 1.0), 42, clave, out_dir)
    elif clave.startswith('P'):
        foto(figura(pid=clave, poses=False, suelto=False), (-12.5, 25.0, 23.0), (0.0, 21.0, 0.6), 38, clave, out_dir)


TODAS = (['F0'] + ['C%d' % i for i in range(1, 9)] + ['B%d' % i for i in range(1, 7)] + ['L%d' % i for i in range(1, 7)]
         + ['P%d' % i for i in range(1, 7)])

if __name__ == '__main__':
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    pedidas = TODAS if sys.argv[2] == 'todas' else sys.argv[2].split(',')
    for k in pedidas:
        escena(k, out_dir)

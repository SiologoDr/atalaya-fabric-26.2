"""
Los iconos de las armaduras y las espadas de los tres jefes (octubre de 2026),
pixel a pixel. Sustituyen a los de armaduras_jefes.py (la netherite
recoloreada): cada pieza tiene aqui su silueta y sus detalles, y las espadas
estan dibujadas nuevas y animadas.

  mareas    Nerea, el guardian del abismo: metal azul abisal, prismarina que
            brilla, nacar, coral y algas.
  jade      Rajang, el jaguar de jade del templo: metal verde casi negro, jade
            que brilla, oro de templo y marfil (colmillos y garras).
  vendaval  Aeralis, la reina polilla de la tormenta: metal anil, cielo y rayo,
            violeta de tormenta y pluma blanca.

Escribe, para cada tema, en textures/item/:
  <tema>_helmet|chestplate|leggings|boots.png   las piezas (16x16)
  <tema>_sword.png + .mcmeta                    la espada en el inventario
                                                (16x16, tira animada)
  <tema>_sword_in_hand.png + .mcmeta            la espada en la mano (32x32,
                                                tira animada, mas detalle)

Como se dibuja (ver DISENO.md en la raiz):
  - Cada icono es un mapa de texto: cada caracter es un material y un tono de
    su rampa. '0'-'6' el metal (7 pasos); 'a'-'e', 'f'-'j', 'k'-'o' y 'p'-'t'
    los otros materiales del tema (5 pasos, de oscuro a claro). '.' es aire.
  - El contorno se calcula: todo pixel que toca el aire por uno de sus cuatro
    lados pasa al tono mas oscuro de su material (que lleva el tinte, nunca es
    negro). En mayuscula, el mismo tono sin contorno (para lo fino: un cuerno
    de coral de un pixel se pintaria entero de oscuro).
  - Luz de arriba a la izquierda, como los items de vanilla.

Uso: python armaduras_iconos.py <raiz> [hoja.png]
"""
import json, math, os, sys
from PIL import Image

RAIZ = sys.argv[1]
ITEM = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def rampa(*cs):
    return [hexc(c) for c in cs]


def mezclar(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


# ----------------------------------------------------------------------
#  Las paletas. Cada rampa va del contorno (oscuro, con el tinte) al nucleo
#  (claro, tirando al color). M es el metal (7 pasos); A B C D los demas;
#  H la hoja de la espada (6 pasos).
# ----------------------------------------------------------------------
TEMAS = {
    'mareas': {
        'M': rampa('0b161d', '13262f', '1c3843', '284c58', '386470', '527f8a', '7fa9b0'),
        'A': rampa('0e4e60', '1b8aa6', '3fe0ff', '9ff4ff', 'eaffff'),     # prismarina
        'B': rampa('5c3a54', 'a87a94', 'd6aac0', 'f0d4e2', 'fff4fa'),     # nacar
        'C': rampa('5e1029', '9e1a42', 'd8336a', 'f2618f', 'ffb3c8'),     # coral
        'D': rampa('0b2a24', '15493c', '226a52', '3a8f6a', '72c08e'),     # alga
        'H': rampa('0a3346', '0f5f7a', '1b8aa6', '3fe0ff', '9ff4ff', 'eaffff'),  # hoja: agua
    },
    'jade': {
        'M': rampa('0c140f', '142019', '1c2d22', '273c2e', '35503d', '4b6a53', '6f8f76'),
        'A': rampa('0c3a1e', '1d6b3a', '35a85a', '6fe08a', 'c8ffd0'),     # jade
        'B': rampa('5e4410', '9a7420', 'd4a83a', 'f8d97c', 'fff2c0'),     # oro
        'C': rampa('4a3a22', '8a7650', 'c8b488', 'ecdcb0', 'fff8e2'),     # marfil
        'D': rampa('0c3a1e', '1d6b3a', '35a85a', '6fe08a', 'c8ffd0'),
        'H': rampa('0a2e18', '145a30', '238a48', '3fbf68', '7fe89a', 'd0ffd8'),  # hoja: jade tallado
    },
    'vendaval': {
        'M': rampa('11111f', '191a2e', '232542', '2f3256', '40446e', '595f8c', '858cb4'),
        'A': rampa('1b3f6e', '2f6fb0', '5fb6ff', 'a8dcff', 'eaf6ff'),     # cielo y rayo
        'B': rampa('2a1a58', '6a44b8', '9a7cff', 'c9b4ff', 'f0e8ff'),     # violeta
        'C': rampa('3c4068', '8a90b0', 'b8bdd8', 'd8dcf0', 'eef0fa'),     # pluma
        'D': rampa('2a1a58', '6a44b8', '9a7cff', 'c9b4ff', 'f0e8ff'),
        'H': rampa('1a1c3a', '3a4a86', '6a7cc0', '9fb2e8', 'cfe0ff', 'f2f8ff'),  # hoja: acero de cielo
    },
}

# El caracter -> (material, tono)
LEYENDA = {}
for _i in range(7):
    LEYENDA[str(_i)] = ('M', _i)
for _m, _letras in (('A', 'abcde'), ('B', 'fghij'), ('C', 'klmno'), ('D', 'pqrst'), ('H', 'uvwxyz')):
    for _i, _ch in enumerate(_letras):
        LEYENDA[_ch] = (_m, _i)


def limpia(fila):
    """Las filas se escriben en dos mitades de 8 separadas por '|' (para contar)."""
    return fila.replace('|', '')


def leer(filas):
    """El mapa de texto -> {(x, y): (material, tono, libre)}; libre = sin contorno."""
    out = {}
    for y, fila in enumerate(filas):
        for x, ch in enumerate(limpia(fila)):
            if ch in '. ':
                continue
            libre = ch.isupper()
            m, t = LEYENDA[ch.lower()] if libre else LEYENDA[ch]
            out[(x, y)] = (m, t, libre)
    return out


def contorno(celdas, w, h):
    """Todo lo que toca el aire por uno de sus cuatro lados pasa al tono 0."""
    out = dict(celdas)
    for (x, y), (m, t, libre) in celdas.items():
        if libre:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in celdas:
                out[(x, y)] = (m, 0, libre)
                break
    return out


def pintar(filas, tema, w=None, h=None, dx=0, dy=0):
    w = w or len(limpia(filas[0]))
    h = h or len(filas)
    T = TEMAS[tema]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for (x, y), (m, t, _) in contorno(leer(filas), w, h).items():
        if 0 <= x + dx < w and 0 <= y + dy < h:
            px[x + dx, y + dy] = T[m][t]
    return im


def comprobar(nombre, filas, ancho):
    """Que cada fila mida lo que debe y no lleve caracteres sin leyenda."""
    malas = []
    if len(filas) != ancho:
        malas.append(f'{nombre}: {len(filas)} filas, no {ancho}')
    for i, f in enumerate(filas):
        f = limpia(f)
        if len(f) != ancho:
            malas.append(f'{nombre}: la fila {i} mide {len(f)}: "{f}"')
        for ch in f:
            if ch not in '. ' and ch.lower() not in LEYENDA:
                malas.append(f'{nombre}: caracter raro "{ch}" en la fila {i}')
    return malas


# ----------------------------------------------------------------------
#  Las piezas (16x16). Cada fila en dos mitades de 8 (x 0-7 | x 8-15).
# ----------------------------------------------------------------------
PIEZAS = {}

# MAREAS -- 0-6 metal abisal; a-e prismarina; f-j nacar; k-o coral; p-t alga
PIEZAS['mareas_helmet'] = [
    "........|........",
    "...i.ij.|.ji.i...",
    "..hjfjjf|fjjfjh..",
    ".ijfijhf|fhjifji.",
    ".hjfhh01|10hhfjh.",
    "..hg0156|5510gh..",
    "O..45665|55443..O",
    "M.45655j|i44332.M",
    ".L45544i|h43332L.",
    "..454443|433322..",
    "..41bcd3|3dcb12..",
    "..432111|111222..",
    "..432...|...222..",
    "..32....|....22..",
    "........|........",
    "........|........",
]
PIEZAS['mareas_chestplate'] = [
    "........|..O.O...",
    "........|.NM.MN..",
    ".fjjih..|..LML0..",
    "fjgggi..|.0lmml0.",
    "fjgjjh4.|.4lml543",
    "figggh54|44554432",
    ".hiihg45|44444332",
    ".4554454|4443322.",
    "...455hj|jh443...",
    "...344ie|di332...",
    "...554hd|ch443...",
    "...3444g|g4332...",
    "...55544|44433...",
    "...R3333|3322R...",
    "...SQ.R.|..R.QS..",
    "....T..S|...T....",
]
PIEZAS['mareas_leggings'] = [
    "........|........",
    "........|........",
    "...44444|44444...",
    "...4cdcd|dcdc4...",
    "..hh5554|4443hh..",
    ".hjih554|443hijh.",
    "hjgjgh5.|.3hgjgjh",
    "hjgjgj4.|.3jgjgjh",
    "f1f1f54.|.43f1f1f",
    "...5434.|.4323...",
    ".B.5444.|.4333.B.",
    ".CB4ih4.|.3ih3BC.",
    ".DCB434.|.432BCD.",
    "...5444.|.4333...",
    "...4444.|.3333...",
    "........|........",
]
PIEZAS['mareas_boots'] = [
    "........|........",
    "........|........",
    "........|........",
    "B..4554.|.4554..B",
    "CB.5543.|.3455.BC",
    ".DB5443.|.3445BD.",
    "BCD4543.|.3454DCB",
    ".CB5443.|.3445BC.",
    "..D4543.|.3454D..",
    "..j5443.|.3445j..",
    ".jgi543.|.345igj.",
    ".hjgh43.|.34hgjh.",
    ".fffff0.|.0fffff.",
    "........|........",
    "........|........",
    "........|........",
]

# JADE -- 0-6 metal verde; a-e jade; f-j oro; k-o marfil
PIEZAS['jade_helmet'] = [
    "........|........",
    "..00...E|C...00..",
    ".0h50..E|C..05h0.",
    ".0h550.D|C.044h0.",
    ".055655d|b444330.",
    ".0565256|5424430.",
    ".05cde56|54edc30.",
    ".054bd45|43db330.",
    ".0444551|1433320.",
    "..hiiiij|iiiihh..",
    "..04O111|111O30..",
    "..03N111|111N20..",
    "..030...|...020..",
    "........|........",
    "........|........",
    "........|........",
]
PIEZAS['jade_chestplate'] = [
    "......E.|.D......",
    ".....Ed.|.cB.....",
    "iiiiiiC.|.Biiiiii",
    "ijjjji5.|.3ijjjji",
    "igggji54|43ijgggi",
    "ijigji45|43ijgiji",
    "ijjjji54|43ijjjji",
    "iiiiii45|43iiiiii",
    "...4544i|h4443...",
    "...544ij|ih443...",
    "...44iie|dhh43...",
    "...54hid|chg33...",
    "...444hh|hg432...",
    "...4444h|g4332...",
    "....ihih|ihih....",
    ".....444|333.....",
]
PIEZAS['jade_leggings'] = [
    "........|........",
    "........|........",
    "...hhhhh|hhhhh...",
    "...hihid|eihih...",
    "..iiiii4|4iiiii..",
    "..ijjji5|4ijjji..",
    "..iggji.|.ijggi..",
    "..ijjji.|.ijjji..",
    "..iiiii.|.iiiii..",
    "...5454.|.4543...",
    "...5dc4.|.4cd3...",
    "...4cb5.|.5bc3...",
    "...5454.|.4543...",
    "...hihi.|.ihih...",
    "...4444.|.4444...",
    "........|........",
]
PIEZAS['jade_boots'] = [
    "........|........",
    "........|........",
    "........|........",
    "...4554.|.4554...",
    "...5243.|.4523...",
    "...4543.|.4243...",
    "..hiiih.|.hiiih..",
    "..ghdhg.|.ghdhg..",
    "...5523.|.4553...",
    "..55443.|.32455..",
    ".555443.|.344555.",
    "O524433.|.334425O",
    "N000000.|.000000N",
    ".O......|......O.",
    "........|........",
    "........|........",
]

# VENDAVAL -- 0-6 metal anil; a-e cielo; f-j violeta; k-o pluma
PIEZAS['vendaval_helmet'] = [
    "........|........",
    "o..I....|....I..o",
    "no.GI...|...IG.on",
    "mno.G...|...G.onm",
    "omno.G00|00G.onmo",
    ".omno565|543onmo.",
    "..omn55h|h43nmo..",
    "...455he|dh433...",
    "...4544h|g4332...",
    "...41bcd|dcb12...",
    "...43111|11122...",
    "...43...|...22...",
    "...32...|...22...",
    "........|........",
    "........|........",
    "........|........",
]
PIEZAS['vendaval_chestplate'] = [
    "........|........",
    "........|........",
    ".kkkk...|...kkkk.",
    "koonnk..|..knnook",
    "nononm5.|.4mnonon",
    "mnmnmn55|44nmnmnm",
    "m.m45554|44433m.m",
    ".gh4544h|h4433hg.",
    "gDh454he|dh433hDg",
    "ggh544hd|ch432hgg",
    "gg.4544h|g4332.gg",
    "g..45444|44332..g",
    "....4544|4332....",
    ".....444|333.....",
    "........|........",
    "........|........",
]
PIEZAS['vendaval_leggings'] = [
    "........|........",
    "........|........",
    "...hhhhh|hhhhh...",
    "...gihie|dihig...",
    ".knk5454|4545knk.",
    "knonk545|545knonk",
    "nomon54.|.45nomon",
    "nomon45.|.54nomon",
    ".nmn545.|.545nmn.",
    ".m.m4c4.|.4c4m.m.",
    "...4c54.|.45c3...",
    "...5c44.|.44c3...",
    "...45c4.|.4c43...",
    "...4c54.|.45c3...",
    "...4444.|.4444...",
    "........|........",
]
PIEZAS['vendaval_boots'] = [
    "........|........",
    "........|........",
    "........|.......O",
    "O..4554.|.4554.ON",
    "NO.5543.|.3455OMN",
    "MNO4543.|.3454NML",
    "LMN5443.|.3445ML.",
    ".LM4543.|.3454L..",
    "..L5443.|.3445...",
    "...4543.|.3454...",
    "..54443.|.34445..",
    ".5c5c43.|.34c5c5.",
    "0000000.|.0000000",
    "........|........",
    "........|........",
    "........|........",
]




# ----------------------------------------------------------------------
#  Las espadas. En la mano (32x32) la hoja se calcula: una curva de Bezier
#  del arranque a la punta y su semianchura a cada lado, escritas como datos;
#  la guarda, el puno y el pomo van en mapas de texto. En el inventario
#  (16x16) la espada entera va a mano. La animacion se pinta encima de cada
#  cuadro, solo por dentro del contorno (y alguna chispa suelta fuera).
# ----------------------------------------------------------------------
CUADROS = 12


def bezier(puntos, n=240):
    out = []
    for i in range(n + 1):
        t = i / n
        pts = list(puntos)
        while len(pts) > 1:
            pts = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(pts, pts[1:])]
        out.append(pts[0])
    return out


def perfil(tabla, u):
    """Interpolacion lineal en una tabla [(u, valor), ...]."""
    if u <= tabla[0][0]:
        return tabla[0][1]
    for (u0, v0), (u1, v1) in zip(tabla, tabla[1:]):
        if u <= u1:
            return v0 + (v1 - v0) * (u - u0) / max(1e-9, u1 - u0)
    return tabla[-1][1]


def proyectar(curva, pixeles):
    """{(x, y): (u, d, fuera)} de cada pixel sobre la curva: u de 0 (arranque)
    a 1 (punta) a lo largo de ella; d la distancia con signo (+ hacia el lomo,
    arriba a la izquierda); fuera, si cae por detras del arranque o mas alla
    de la punta."""
    import numpy as np
    P = np.array(curva, dtype=float)
    A, V = P[:-1], P[1:] - P[:-1]
    L2 = (V ** 2).sum(1)
    Ls = np.sqrt(L2)
    acum = np.concatenate([[0.0], np.cumsum(Ls)])
    total = acum[-1]
    out = {}
    for (x, y) in pixeles:
        p = np.array([x + 0.5, y + 0.5])
        t = ((p - A) * V).sum(1) / L2
        antes, despues = bool(t[0] < -0.05), bool(t[-1] > 1.05)
        t = np.clip(t, 0.0, 1.0)
        Q = A + t[:, None] * V
        dist = np.sqrt(((p - Q) ** 2).sum(1))
        i = int(np.argmin(dist))
        nx, ny = V[i, 1] / Ls[i], -V[i, 0] / Ls[i]
        d = (p[0] - Q[i, 0]) * nx + (p[1] - Q[i, 1]) * ny
        fuera = (antes and i == 0) or (despues and i == len(Ls) - 1)
        out[(x, y)] = (float((acum[i] + t[i] * Ls[i]) / total), float(d), fuera)
    return out


def hoja(curva, lomo, filo, w=32):
    """{(x, y): (u, s, d)} de los pixeles de la hoja: los que caen dentro de
    la semianchura de su lado (lomo(u) o filo(u)). s es d partido por esa
    semianchura: de -1 en el filo a +1 en el lomo."""
    out = {}
    todos = [(x, y) for y in range(w) for x in range(w)]
    for p, (u, d, fuera) in proyectar(curva, todos).items():
        if fuera:
            continue
        semi = perfil(lomo, u) if d >= 0 else perfil(filo, u)
        if abs(d) <= semi:
            out[p] = (u, d / max(0.01, semi), d)
    return out


def que_toca_aire(celdas):
    """Los pixeles que tocan el aire por alguno de sus cuatro lados."""
    return {p for p in celdas if any((p[0] + dx, p[1] + dy) not in celdas
                                     for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def a_imagen(celdas, tema, w, h):
    T = TEMAS[tema]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for (x, y), (m, t, _) in celdas.items():
        if 0 <= x < w and 0 <= y < h:
            px[x, y] = T[m][max(0, min(len(T[m]) - 1, t))]
    return im


def tira(cuadros):
    """Los cuadros de una animacion, uno debajo de otro (lo que lee el .mcmeta)."""
    w, h = cuadros[0].size
    out = Image.new('RGBA', (w, h * len(cuadros)), (0, 0, 0, 0))
    for k, c in enumerate(cuadros):
        out.paste(c, (0, h * k))
    return out


def seg(p, a, b):
    """(t, d, largo) de un punto respecto del segmento a-b: t de 0 a 1 a lo
    largo; d con signo (+ a la izquierda yendo de a a b: en algo que sube a la
    derecha, arriba a la izquierda)."""
    vx, vy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(vx, vy)
    t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / (L * L)
    d = ((p[0] - a[0]) * vy - (p[1] - a[1]) * vx) / L
    return t, d, L


def contornear(celdas):
    """El contorno calculado (lo que toca el aire, salvo lo libre, al tono 0).
    Devuelve los pixeles de contorno, que la animacion no toca."""
    borde = {p for p in que_toca_aire(celdas) if not celdas[p][2]}
    for p in borde:
        m, t, l = celdas[p]
        celdas[p] = (m, 0, l)
    return borde


def barra(celdas, a, b, ancho, tono, w=32, encima=False):
    """Lo que queda a menos de 'ancho' del segmento a-b (un puno, una barra de
    guarda). tono(t, d, largo) -> (material, tono)."""
    for y in range(w):
        for x in range(w):
            if (x, y) in celdas and not encima:
                continue
            t, d, L = seg((x + 0.5, y + 0.5), a, b)
            if -0.04 <= t <= 1.04 and abs(d) <= ancho:
                celdas[(x, y)] = tono(t, d, L) + (False,)


def bola(celdas, c, r, tono, w=32):
    """Un disco de radio r; tono(dx, dy, r) -> (material, tono)."""
    for y in range(w):
        for x in range(w):
            dx, dy = x + 0.5 - c[0], y + 0.5 - c[1]
            if math.hypot(dx, dy) <= r:
                celdas[(x, y)] = tono(dx, dy, math.hypot(dx, dy)) + (False,)


def calcar(celdas, filas, ox, oy):
    """Un mapa de texto encima, desde (ox, oy)."""
    for (x, y), v in leer(filas).items():
        celdas[(x + ox, y + oy)] = v


def destello(celdas, p, e, interior, m='H', alto=5, brazos=1, libres=False):
    """Un brillo que dura tres cuadros: punto, estrella, punto apagado."""
    if p is None:
        return
    x, y = p
    if e == 0:
        celdas[p] = (m, alto, celdas.get(p, (m, 0, False))[2])
    elif e == 1:
        celdas[p] = (m, alto, celdas.get(p, (m, 0, False))[2])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for i in range(1, brazos + 1):
                q = (x + dx * i, y + dy * i)
                if q in interior:
                    celdas[q] = (m, max(celdas[q][1], alto - i), False)
                elif libres and i == brazos and q not in celdas:
                    celdas[q] = (m, alto - 1, True)
    elif e == 2:
        celdas[p] = (m, alto - 1, celdas.get(p, (m, 0, False))[2])


def cerca(info, u_obj, s_min, s_max, interior):
    """El pixel de la hoja mas cerca de u_obj con s entre s_min y s_max."""
    c = [p for p, v in info.items() if s_min <= v[1] <= s_max and p in interior]
    return min(c, key=lambda p: abs(info[p][0] - u_obj)) if c else None


_CACHE = {}


def hoja_de(clave, curva, lomo, filo, w=32):
    if clave not in _CACHE:
        _CACHE[clave] = hoja(curva, lomo, filo, w)
    return _CACHE[clave]


# ---------------------------- Las Mareas -------------------------------
#  Una hoja curva como una ola que rompe: espuma en el lomo (arriba), agua
#  honda hacia el filo; crestas y senos que corren hacia la punta y destellos
#  de espuma. Guarda de venera de nacar (cinco costillas en lineas limpias de
#  pixel, a 0, 45 y 90 grados), puno envuelto en alga y una perla por pomo.
MAREAS_CURVA = bezier([(10, 22), (13, 12), (21, 3), (30.5, 1.5)])
MAREAS_LOMO = [(0, 2.2), (0.25, 3.2), (0.55, 3.8), (0.8, 3.0), (0.93, 2.0), (1.0, 0.4)]
MAREAS_FILO = [(0, 2.2), (0.3, 2.4), (0.6, 2.2), (0.85, 1.6), (0.95, 1.0), (1.0, 0.3)]
# Los destellos de espuma: (cuadro en que nace, por donde va de la hoja)
MAREAS_ESPUMA = [(0, 0.30), (4, 0.78), (8, 0.52)]


def agua(u, s, fase, olas=4.0):
    """El tono del agua: por bandas de lomo a filo, con la ola que corre."""
    t = 4 if s > 0.62 else 3 if s > 0.1 else 2 if s > -0.45 else 1
    w = (u * olas - fase - 0.3 * s) % 1.0
    if t in (2, 3) and 0.5 <= w < 0.64:
        t -= 1                      # el seno de la ola
    elif w < 0.12:
        t = min(5, t + 1)           # la cresta
    return t


def venera(celdas, H, R=6.0, bulto=0.35):
    """La venera de la guarda, abierta hacia la hoja desde el gozne H."""
    rayos = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]
    for y in range(32):
        for x in range(32):
            dx, dy = x - H[0], y - H[1]
            if dx - dy < 0:
                continue                         # del lado del puno no hay concha
            r = math.hypot(dx, dy)
            k = (math.atan2(-dy, dx) + math.pi / 4) / (math.pi / 4)
            if k < -0.05 or k > 4.05:
                continue
            frac = abs(k - round(k))             # 0 sobre una costilla, 0.5 en un surco
            if r > R + bulto * (1 - 2 * frac) + 0.3:
                continue
            costilla = any((dx, dy) == (a * i, b * i) for a, b in rayos for i in range(1, 9))
            t = 2 if r < 1.2 else 4 if costilla else 1 if frac > 0.3 else 3
            celdas[(x, y)] = ('B', t, False)
    celdas[H] = ('B', 2, False)


def mareas_mano(k):
    fase = k / CUADROS
    info = hoja_de('mareas', MAREAS_CURVA, MAREAS_LOMO, MAREAS_FILO)
    celdas = {p: ('H', agua(u, s, fase), False) for p, (u, s, d) in info.items()}
    venera(celdas, (8, 24), R=5.4)
    barra(celdas, (7.4, 25.6), (3.4, 29.0), 1.75,
          lambda t, d, L: ('D', 3 if (t * L / 1.5 + d * 0.6) % 2.0 < 0.9 else 2 if d > 0 else 1))
    bola(celdas, (2.6, 29.4), 2.35,
         lambda dx, dy, r: ('B', 4 if math.hypot(dx + 0.7, dy + 0.7) < 1.0 else 3 if math.hypot(dx + 0.7, dy + 0.7) < 1.9 else 2))
    borde = contornear(celdas)
    interior = {p for p in info if p not in borde and celdas[p][0] == 'H'}
    for nace, u in MAREAS_ESPUMA:
        e = (k - nace) % CUADROS
        if e < 3:
            destello(celdas, cerca(info, u, 0.45, 1.0, interior), e, interior)
    return a_imagen(celdas, 'mareas', 32, 32)


# ------------------------------ El Jade --------------------------------
#  Un montante de jade tallado: ancho, con la arista en medio (la cara de
#  arriba con luz, la de abajo en sombra), tres cortes de faceta y vetas que
#  laten con un pulso que sube hacia la punta. Un destello salta de faceta en
#  faceta. Guarda de oro con las dos puntas en espiral cuadrada y una gema;
#  puno de metal con anillas de oro; una cabeza de jaguar por pomo.
JADE_CURVA = bezier([(10, 22), (30.6, 1.4)])
JADE_ANCHO = [(0, 3.4), (0.72, 3.8), (1.0, 0.4)]
JADE_CORTES = (0.30, 0.55, 0.78)
JADE_FACETAS = [(0.30, 0.3), (0.55, -0.35), (0.78, 0.3), (0.93, 0.0)]   # por donde salta el destello
ESPIRAL = ["ffffff",
           "fjjjjf",
           "fgggjf",
           "fjigjf",
           "fjjjjf",
           "ffffff"]
JAGUAR = [".f...f.",
          "fhf.fhf",
          "fiiiiif",
          "fiDiDif",
          ".fhghf.",
          "..fNf..",
          ]


def vena(u, s):
    """Las vetas del jade: dos lineas que serpentean por las dos caras."""
    return (abs(s - 0.42 * math.sin(u * 10.0 + 0.7)) < 0.13 or
            (0.12 < u < 0.72 and abs(s + 0.55 - 0.22 * math.sin(u * 15.0)) < 0.11))


def jade_tono(u, s):
    t = 4 if s > 0.62 else 3 if s > 0.0 else 2 if s > -0.62 else 1
    if abs(s) < 0.14 and u < 0.97:
        t = 4                                    # la arista
    for c in JADE_CORTES:
        if abs(u - c - 0.06 * abs(s)) < 0.016:
            t = max(1, t - 2)                    # el corte entre dos facetas
    return t


def jade_mano(k):
    fase = k / CUADROS
    info = hoja_de('jade', JADE_CURVA, JADE_ANCHO, JADE_ANCHO)
    celdas = {p: ('H', jade_tono(u, s), False) for p, (u, s, d) in info.items()}
    # La guarda: una barra de oro de punta a punta y las dos espirales.
    calcar(celdas, ESPIRAL, 3, 14)
    calcar(celdas, [f[::-1] for f in ESPIRAL[::-1]], 13, 24)
    barra(celdas, (7.6, 18.6), (13.4, 24.4), 1.9,
          lambda t, d, L: ('B', 4 if d > 0.7 else 3 if d > -0.5 else 2), encima=True)
    calcar(celdas, ["ed", "dc"], 10, 21)
    # El puno y el pomo.
    barra(celdas, (8.8, 24.2), (5.0, 28.0), 1.5,
          lambda t, d, L: ('B', 3) if (t * L) % 2.4 < 0.9 else ('M', 4 if d > 0.3 else 3 if d > -0.6 else 2))
    calcar(celdas, JAGUAR, 0, 26)
    borde = contornear(celdas)
    interior = {p for p in info if p not in borde and celdas[p][0] == 'H'}
    # Las vetas: un poco mas claras siempre; el pulso las enciende al pasar.
    for p in interior:
        u, s, d = info[p]
        if not vena(u, s):
            continue
        brillo = 1
        for j in (0.0, 0.5):
            du = (u - (fase + j)) % 1.0
            if du < 0.10 or du > 0.97:
                brillo = 2
        m, t, l = celdas[p]
        celdas[p] = ('H', min(5, max(t, 3) + brillo), l)
    # El destello que salta de faceta en faceta (tres cuadros en cada una).
    u, s = JADE_FACETAS[(k // 3) % len(JADE_FACETAS)]
    p = min(interior, key=lambda q: (info[q][0] - u) ** 2 * 900 + (info[q][1] - s) ** 2 * 9)
    destello(celdas, p, k % 3, interior, brazos=2, libres=True)
    return a_imagen(celdas, 'jade', 32, 32)


# ---------------------------- El Vendaval ------------------------------
#  Una hoja larga y fina, de acero con tinte de cielo, por la que sube un
#  rayo en zigzag que parpadea y suelta chispas. Guarda de dos alas de pluma
#  blanca (con su ojo de polilla), puno violeta y el ojo de la tormenta por
#  pomo.
VENDAVAL_CURVA = bezier([(11, 21), (31.3, 0.7)])
VENDAVAL_ANCHO = [(0, 2.1), (0.85, 1.75), (1.0, 0.4)]


def zigzag(u, dientes=9.0, amplitud=0.62):
    """Por donde va el rayo a lo ancho de la hoja (s), a cada altura u."""
    f = (u * dientes) % 1.0
    return amplitud * (4 * abs(f - 0.5) - 1)


def ala(celdas, raiz, direccion, largo=8.4, vuelo=3.0):
    """Un ala de pluma desde la guarda: su eje sale en 'direccion' y se curva
    hacia la punta de la espada ('vuelo'). Barbas por bandas y un ojo."""
    dx, dy = direccion
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    fx, fy = 1 / math.sqrt(2), -1 / math.sqrt(2)          # hacia la punta
    eje = [(raiz[0] + dx * largo * t + fx * vuelo * t * t,
            raiz[1] + dy * largo * t + fy * vuelo * t * t) for t in [i / 40 for i in range(41)]]
    lomo = [(0, 1.2), (0.35, 2.4), (0.75, 2.0), (1.0, 0.4)]
    filo = [(0, 1.2), (0.35, 2.0), (0.75, 1.6), (1.0, 0.4)]
    for p, (u, s, d) in hoja(eje, lomo, filo).items():
        if p in celdas and celdas[p][0] != 'H':
            continue
        lado_punta = (p[0] + 0.5 - raiz[0]) * fx + (p[1] + 0.5 - raiz[1]) * fy
        t = 4 if lado_punta > 1.2 else 3 if s > -0.2 else 2
        if (u * 5.0 + 0.4 * s) % 1.0 < 0.2 and u > 0.25:
            t = 2                                # la separacion de las plumas
        if abs(u - 0.58) < 0.09 and abs(s) < 0.35:
            celdas[p] = ('A', 3, False) if abs(u - 0.58) < 0.04 else ('B', 1, False)
            continue
        celdas[p] = ('C', t, False)


def vendaval_mano(k):
    info = hoja_de('vendaval', VENDAVAL_CURVA, VENDAVAL_ANCHO, VENDAVAL_ANCHO)
    celdas = {}
    for p, (u, s, d) in info.items():
        celdas[p] = ('H', 4 if s > 0.35 else 3 if s > -0.3 else 2, False)
    raiz = (10.6, 21.4)
    ala(celdas, raiz, (-1, -1))
    ala(celdas, raiz, (1, 1))
    calcar(celdas, ["gh", "hg"], 10, 21)
    barra(celdas, (9.2, 22.8), (5.0, 27.0), 1.45,
          lambda t, d, L: ('B', 3 if (t * L + d * 0.7) % 2.0 < 0.9 else 2 if d > 0 else 1))
    bola(celdas, (3.3, 28.7), 2.45,
         lambda dx, dy, r: ('A', 4) if r < 0.9 else ('A', 2) if r < 1.5 else ('B', 3 if dx + dy < 0 else 2))
    borde = contornear(celdas)
    interior = {p for p in info if p not in borde and celdas[p][0] == 'H'}
    # El rayo: la cabeza sube de la guarda a la punta en los doce cuadros y
    # deja una estela que se apaga; cada pocos cuadros parpadea.
    cabeza = -0.15 + 1.35 * (k + 1) / CUADROS
    parpadeo = k in (3, 7, 10)
    for p in interior:
        u, s, d = info[p]
        if abs(s - zigzag(u)) > 0.42:
            continue
        atras = cabeza - u
        if 0 <= atras < 0.42:
            t = 4 if atras < 0.08 else 3 if atras < 0.22 else 2
            if parpadeo:
                t -= 1
            celdas[p] = ('A', t, False)
    # Chispas que saltan junto a la cabeza del rayo.
    if 0.05 < cabeza < 1.0 and not parpadeo:
        for lado in (1, -1):
            u = min(0.97, cabeza - (0.03 if lado > 0 else 0.1))
            c = min(info, key=lambda q: (info[q][0] - u) ** 2)
            x, y = c
            q = (x - 2, y - 2) if lado > 0 else (x + 2, y + 2)
            if q not in celdas and 0 <= q[0] < 32 and 0 <= q[1] < 32:
                celdas[q] = ('A', 3 if (k + lado) % 2 else 4, True)
    return a_imagen(celdas, 'vendaval', 32, 32)


MANO = {'mareas': mareas_mano, 'jade': jade_mano, 'vendaval': vendaval_mano}


# ----------------------------------------------------------------------
#  Las espadas del inventario (16x16), a mano. La misma idea que en la mano
#  con menos pixeles; la animacion sale de proyectar la hoja sobre la curva
#  de la espada a media escala (u a lo largo, s a lo ancho).
#  Leyenda: u-z la hoja (de contorno a nucleo); en mayuscula, sin contorno.
# ----------------------------------------------------------------------
ICONOS_ESPADA = {
    # La ola de prismarina, la venera de nacar, el alga y la perla.
    'mareas': [
        "........|...uuuu.",
        "........|.uuyzzyu",
        "........|uyyxwvuu",
        ".......u|yxxwvu..",
        "......uy|yxwvu...",
        "......uy|xwvu....",
        ".....uyx|wvu.....",
        "..f.f.yx|wu......",
        ".gjgjgyx|vu......",
        ".hjijhxw|u.......",
        "..gjijhv|u.......",
        "...fhjih|........",
        "..qrfhf.|........",
        ".jqrf...|........",
        "jjif....|........",
        ".if.....|........",
    ],
    # El jade tallado (arista clara en medio), la guarda de oro con las
    # puntas vueltas, el puno oscuro y la cabeza de jaguar.
    'jade': [
        "........|......uu",
        "........|....uuzu",
        "........|...uyzxu",
        "........|..uyzxwu",
        "........|.uyzxwvu",
        "........|uyzxwvu.",
        ".......u|yzxwvu..",
        "..fff.uy|zxwvu...",
        "..fjf.yz|xwvu....",
        "..ffiiyz|wvu.....",
        "....ijji|vu......",
        ".....iij|i.......",
        "....2.ji|iff.....",
        ".f.f2...|fjf.....",
        ".fhf....|fff.....",
        ".fDf....|........",
    ],
    # La hoja fina con el filo claro (sin contorno por arriba), las dos alas
    # de pluma, el puno violeta y el ojo de la tormenta.
    'vendaval': [
        "........|.......Z",
        "........|......Yu",
        "........|.....Yxu",
        "........|....Yxu.",
        "........|...Yxu..",
        "........|..Yxu...",
        "...O....|.Yxu....",
        "...NO...|Yxu.....",
        "...LMN.Y|xu......",
        "....LMYx|u.......",
        "......gh|MNO.....",
        ".....ghg|LMN.....",
        "....ghg.|.L......",
        "...ghg..|........",
        "..aEa...|........",
        "..aa....|........",
    ],
}
ICONO_CURVA = {
    'mareas': bezier([(5, 11), (6.5, 6), (10.5, 1.5), (15.25, 0.75)]),
    'jade': bezier([(5, 11), (15.3, 0.7)]),
    'vendaval': bezier([(5.5, 10.5), (15.6, 0.4)]),
}
ICONO_SEMI = {'mareas': 2.2, 'jade': 2.4, 'vendaval': 1.3}


def icono_espada(tema, k):
    fase = k / CUADROS
    celdas = leer(ICONOS_ESPADA[tema])
    borde = contornear(celdas)
    dentro = {p for p, v in celdas.items() if v[0] == 'H' and p not in borde}
    info = {p: (u, d / ICONO_SEMI[tema], d)
            for p, (u, d, _) in proyectar(ICONO_CURVA[tema], dentro).items()}
    if tema == 'mareas':
        # La ola que corre hacia la punta y los destellos de espuma.
        for p, (u, s, d) in info.items():
            m, t, l = celdas[p]
            w = (u * 2.5 - fase - 0.3 * s) % 1.0
            if w < 0.16:
                t = min(5, t + 1)
            elif 0.5 <= w < 0.64:
                t = max(1, t - 1)
            celdas[p] = (m, t, l)
        for nace, u in MAREAS_ESPUMA:
            e = (k - nace) % CUADROS
            if e < 3:
                destello(celdas, cerca(info, u, 0.0, 1.0, dentro), e, dentro)
    elif tema == 'jade':
        # La arista descansa un tono por debajo; el pulso la enciende al subir.
        for p, (u, s, d) in info.items():
            m, t, l = celdas[p]
            if t == 5:
                t = 4
            for j in (0.0, 0.5):
                du = (u - (fase + j)) % 1.0
                if du < 0.14 or du > 0.95:
                    t = min(5, t + 1)
            celdas[p] = (m, t, l)
        u, s = JADE_FACETAS[(k // 3) % len(JADE_FACETAS)]
        p = min(info, key=lambda q: (info[q][0] - u) ** 2 * 400 + (info[q][1] - s) ** 2)
        destello(celdas, p, k % 3, dentro, libres=True)
    else:
        # El rayo: un tramo claro que sube por la hoja y parpadea.
        cabeza = -0.15 + 1.35 * (k + 1) / CUADROS
        parpadeo = k in (3, 7, 10)
        for p, (u, s, d) in info.items():
            atras = cabeza - u
            if 0 <= atras < 0.4:
                t = 4 if atras < 0.1 else 3 if atras < 0.25 else 2
                if (p[0] + p[1] + k) % 2 and t > 2:
                    t -= 1                       # el chisporroteo
                if parpadeo:
                    t -= 1
                celdas[p] = ('A', t, celdas[p][2])
        if 0.05 < cabeza < 1.0 and not parpadeo:
            c = min(info, key=lambda q: (info[q][0] - cabeza) ** 2)
            q = (c[0] - 1, c[1] - 1) if k % 2 else (c[0] + 1, c[1] + 1)
            if q not in celdas and 0 <= q[0] < 16 and 0 <= q[1] < 16:
                celdas[q] = ('A', 4, True)
    return a_imagen(celdas, tema, 16, 16)


ICONO = {t: (lambda k, t=t: icono_espada(t, k)) for t in ICONOS_ESPADA}


# === PRINCIPAL ===
# (los bancos de pruebas cortan el fichero aqui para no escribir nada)
PIEZAS_ORDEN = ('helmet', 'chestplate', 'leggings', 'boots')
malas = []
for _n, _f in list(PIEZAS.items()) + list(ICONOS_ESPADA.items()):
    malas += comprobar(_n, _f, 16)
if malas:
    raise SystemExit('\n'.join(malas))

os.makedirs(ITEM, exist_ok=True)
MCMETA = json.dumps({'animation': {'frametime': 2}}, indent=2) + '\n'
SALIDAS = {}
for tema in TEMAS:
    for pieza in PIEZAS_ORDEN:
        im = pintar(PIEZAS[f'{tema}_{pieza}'], tema)
        im.save(os.path.join(ITEM, f'{tema}_{pieza}.png'))
        SALIDAS[f'{tema}_{pieza}'] = im
    icono = [icono_espada(tema, k) for k in range(CUADROS)]
    mano = [MANO[tema](k) for k in range(CUADROS)]
    tira(icono).save(os.path.join(ITEM, f'{tema}_sword.png'))
    tira(mano).save(os.path.join(ITEM, f'{tema}_sword_in_hand.png'))
    for nombre in (f'{tema}_sword.png.mcmeta', f'{tema}_sword_in_hand.png.mcmeta'):
        with open(os.path.join(ITEM, nombre), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(MCMETA)
    SALIDAS[f'{tema}_sword'] = icono
    SALIDAS[f'{tema}_sword_in_hand'] = mano
print('ok:', len(TEMAS) * 4, 'piezas,', len(TEMAS), 'espadas de', CUADROS, 'cuadros (16x16 y 32x32)')

# ----------------------------------------------------------------------
#  Hoja de control: por tema, las cinco piezas a 8x sobre el gris del
#  inventario y sobre oscuro; a tamano real (x1, x2 y x3) y en una barra de
#  inventario como la del juego; los doce cuadros de la espada del
#  inventario (x4) y de la espada en la mano (x3).
# ----------------------------------------------------------------------
if len(sys.argv) > 2:
    from PIL import ImageDraw
    GRIS, OSCURO, FONDO = (139, 139, 139, 255), (30, 32, 40, 255), (48, 50, 58, 255)
    TEXTO = (235, 235, 240, 255)

    def ranura(d, x, y, e):
        """Una ranura del inventario de vanilla (18x18 a escala e)."""
        d.rectangle((x, y, x + 18 * e - 1, y + 18 * e - 1), fill=(139, 139, 139, 255))
        d.rectangle((x, y, x + 17 * e - 1, y + e - 1), fill=(55, 55, 55, 255))
        d.rectangle((x, y, x + e - 1, y + 17 * e - 1), fill=(55, 55, 55, 255))
        d.rectangle((x + e, y + 17 * e, x + 18 * e - 1, y + 18 * e - 1), fill=(255, 255, 255, 255))
        d.rectangle((x + 17 * e, y + e, x + 18 * e - 1, y + 18 * e - 1), fill=(255, 255, 255, 255))

    def grande(im, e):
        return im.resize((im.width * e, im.height * e), Image.NEAREST)

    ANCHO = 1300
    ALTO_TEMA = 20 + 2 * 136 + 70 + 2 * 72 + 2 * 104 + 30
    hoja = Image.new('RGBA', (ANCHO, 10 + len(TEMAS) * ALTO_TEMA), FONDO)
    d = ImageDraw.Draw(hoja)
    for i, tema in enumerate(TEMAS):
        y0 = 10 + i * ALTO_TEMA
        d.text((12, y0), tema.upper(), fill=TEXTO)
        y = y0 + 20
        cosas = [SALIDAS[f'{tema}_{p}'] for p in PIEZAS_ORDEN] + [SALIDAS[f'{tema}_sword'][0]]
        # A 8x, sobre gris y sobre oscuro.
        for fila, fondo in enumerate((GRIS, OSCURO)):
            for j, im in enumerate(cosas):
                x = 12 + j * 136
                d.rectangle((x, y + fila * 136, x + 131, y + fila * 136 + 131), fill=fondo)
                hoja.alpha_composite(grande(im, 8), (x + 2, y + fila * 136 + 2))
        # A la derecha: la espada en la mano, grande.
        for fila, fondo in enumerate((GRIS, OSCURO)):
            x = 12 + 5 * 136 + 10
            d.rectangle((x, y + fila * 136, x + 131, y + fila * 136 + 131), fill=fondo)
            hoja.alpha_composite(grande(SALIDAS[f'{tema}_sword_in_hand'][0], 4), (x + 2, y + fila * 136 + 2))
        # A tamano real: x1, x2 y x3 sobre los dos fondos, y la barra del inventario.
        xr = 12 + 6 * 136 + 30
        for fila, fondo in enumerate((GRIS, OSCURO)):
            yy = y + fila * 136
            d.rectangle((xr, yy, ANCHO - 12, yy + 131), fill=fondo)
            for j, im in enumerate(cosas):
                hoja.alpha_composite(im, (xr + 6 + j * 20, yy + 6))
                hoja.alpha_composite(grande(im, 2), (xr + 6 + j * 36, yy + 30))
                hoja.alpha_composite(grande(im, 3), (xr + 6 + j * 52, yy + 72))
        y += 2 * 136 + 6
        for j, im in enumerate(cosas):
            ranura(d, 12 + j * 18 * 3, y, 3)
            hoja.alpha_composite(grande(im, 3), (12 + j * 18 * 3 + 3, y + 3))
        for j, im in enumerate(cosas):
            ranura(d, 300 + j * 18 * 2, y + 8, 2)
            hoja.alpha_composite(grande(im, 2), (300 + j * 18 * 2 + 2, y + 10))
        d.text((500, y + 20), 'en una ranura del inventario, a escala 3 y 2', fill=TEXTO)
        y += 64
        # Los cuadros de la espada del inventario (x4) y de la mano (x3).
        for fila, fondo in enumerate((GRIS, OSCURO)):
            for k, im in enumerate(SALIDAS[f'{tema}_sword']):
                x = 12 + k * 72
                d.rectangle((x, y + fila * 72, x + 67, y + fila * 72 + 67), fill=fondo)
                hoja.alpha_composite(grande(im, 4), (x + 2, y + fila * 72 + 2))
        y += 2 * 72
        for fila, fondo in enumerate((GRIS, OSCURO)):
            for k, im in enumerate(SALIDAS[f'{tema}_sword_in_hand']):
                x = 12 + k * 104
                d.rectangle((x, y + fila * 104, x + 99, y + fila * 104 + 99), fill=fondo)
                hoja.alpha_composite(grande(im, 3), (x + 2, y + fila * 104 + 2))
    os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])), exist_ok=True)
    hoja.save(sys.argv[2])
    print('hoja', sys.argv[2])

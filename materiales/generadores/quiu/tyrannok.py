"""
Tyrannok (DEDsafío 4, la Dungeon de Qumara y el recinto de huesos): el tiranosaurio del evento, rehecho pieza a pieza
sobre los fotogramas del juego (Juan, 21-10-2026: la versión anterior estaba «como un chiste»). El libro lo describe:
«destruye todo a su paso, aplicando Lentitud».

Un terópodo de cajas, como el del juego:
  - el tronco, un cajón hondo inclinado (los hombros más altos que la cadera), con la cadera aparte detrás;
  - el cuello corto y grueso, de dos cajas escalonadas, que sube del pecho;
  - la cabeza enorme y cuadrada (15 x 14 x 25 texels del juego): el hocico, 2 texels más alto que el cráneo (el
    escalón sobre el ojo), la ceja que baja en diagonal hacia delante, el ojo de 1 x 3 (el brillo blanco detrás) y en la
    cara de delante la banda oscura en V, las dos narinas con su marco claro y el labio;
  - la boca abierta: el paladar y el suelo granate, la lengua rosa en relieve, los dientes de arriba como teclas de
    piano (6 delante: los 2 de las esquinas grandes) y los de abajo, más pequeños, de pie en el canto de la mandíbula
    crema;
  - los brazos largos de tres piezas (el brazo que cuelga del pecho con 3 bandas, el antebrazo hacia delante y la mano
    de 3 dedos con las garras en bloque gris oscuro);
  - las patas en zigzag (el muslo gordo con bandas, la espinilla hacia atrás y el metatarso largo hacia delante), con
    3 dedos dorados y garras en bloque;
  - la cola en dos tramos, la punta cortada en cuadrado.
La piel, oro ocre apagado con un moteado suave; rayas de tigre pardas por el lomo, el cuello, la cadera y la cola, que
bajan media altura del costado; manchas sueltas debajo; la garganta, el pecho, el vientre, el bajo de la cola y la
mandíbula, crema caqui. La cabeza, sin rayas.

Las medidas van en texels del juego (13 por bloque) y TAM las lleva a 16 por bloque; el píxel de la textura sigue a 16
por bloque (y a 32 en lo fino: el ojo, la cara, los dientes).
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import T
from bestiario_hormigas import _azar1
from bestiario_reptiles import caja_en

ID = 'tyrannok'
TAM = 1.25

HUEVO = (
    ('e2b452', 'c69434', '8a6420'),
    ('6c481a', '4e320e'),
    [
        ((5, 4), '6c481a'), ((6, 4), '6c481a'), ((7, 5), '6c481a'),
        ((9, 6), 'f2f2ee'), ((10, 6), '141008'), ((11, 6), '141008'),
        ((5, 8), '6c481a'), ((6, 8), '6c481a'), ((7, 9), '6c481a'),
        ((8, 9), 'ece6da'), ((9, 9), 'ece6da'), ((10, 9), 'ece6da'),
        ((6, 11), 'd4b67c'), ((7, 11), 'd4b67c'), ((8, 11), 'd4b67c'),
        ((9, 11), 'd4b67c'),
    ],
)

# ======================================================================================================================
#  Colores (paleta.json de la ficha: medidos en el juego, sin tinte de daño)
# ======================================================================================================================
def _r(*c):
    return L.rampa(*c)


ORO_TYRANNOK = _r('8a6420', 'b8862e', 'c69434', 'd4a23e', 'e2b452')       # 3: el oro; 2 y 4, el moteado
RAYA_TYRANNOK = _r('4e320e', '5e3e14', '6c481a', '7a5020', '8c5e28')      # 3: la raya
CREMA_TYRANNOK = _r('a08a5c', 'b49a68', 'c6a872', 'd4b67c', 'e4cc96')     # 3: la crema; 4, el canto claro
BOCA_TYRANNOK = _r('1e060c', '2e0c16', '4a1824', '5a1e2c', '74303e')      # el granate de dentro
LENGUA_TYRANNOK = _r('5a1a34', '8a2e50', 'a83c62', 'b8466e', 'd06a8a')
DIENTE_TYRANNOK = _r('8c8474', 'bcb2a0', 'd8d0c2', 'ece6da', 'faf8f2')
GARRA_TYRANNOK = _r('1c1a16', '2c2822', '3c372e', '4a4438', '6a6252')
PUPILA_TYRANNOK = B.H('141008')
BRILLO_TYRANNOK = B.H('f2f2ee')
# La cara de delante del hocico: el oro y sus tonos, medidos en 5:29:43.67 y 43.82 (proporciones de brillo frente al
# oro de esa misma cara: claro 1,18, marco 1,33, oscuro 0,85, banda 0,7, narina 0,59).
CARA_TYRANNOK = {'g': B.H('d4a23e'), 'L': B.H('e8b84e'), 'f': B.H('f4cc62'), 'o': B.H('b88a34'),
                 'b': B.H('94702a'), 'n': B.H('6e5022')}
# Las 14 filas de la cara (15 columnas), de arriba abajo, como en el juego.
MAPA_CARA_TYRANNOK = [
    'googgLLLLLLggog',
    'ooogggLLLLgggog',
    'ooooggggggggggg',
    'ooooggggggggogg',
    'goooggggggggoog',
    'gooooggggggooog',
    'gobbbooooobbbog',
    'ooobbbooobbbooo',
    'gffffgooogffffg',
    'fnnnnfooofnnnnf',
    'LnnnnfgogfnnnnL',
    'gggbbLgggLbbggg',
    'ooooboooooboooo',
    'goggogggggoggog',
]


# La postura de reposo: los ángulos de cada articulación, en grados. Los giros del tronco, el cuello y la cabeza son
# respecto al suelo (negativo: el morro hacia arriba); los de la cola, también (negativo: la punta hacia ABAJO, porque
# la cola apunta hacia atrás); los de las patas y los brazos, desde la vertical (positivo: hacia delante). La cadera se
# pone a la altura que deja los dedos en el suelo. Es la postura del icono del libro (el juego lo pinta con el modelo
# en reposo), buscada con util/postura.py: iou 0.851 con el icono.
POSTURA_TYRANNOK = dict(
    inc=-21.5,          # el tronco: los hombros, más altos que la cadera
    cuello=-16.0,       # el cuello sube del pecho
    cabeza=2.0,         # la cabeza, casi recta
    abre=5.0,           # la boca, entreabierta: se ven los dientes (el icono)
    cola1=1.0,          # la cola, casi horizontal (en la cola, positivo sube la punta)
    cola2=0.5,
    muslo=14.0,         # el muslo, algo hacia delante
    espinilla=-34.0,    # la espinilla, hacia atrás
    metatarso=45.0,     # el metatarso, hacia delante hasta los dedos
    brazo=38.0,         # el brazo baja del pecho echado hacia delante (el icono)
    antebrazo=90.0,     # el antebrazo, hacia delante, horizontal
    mano=67.0,          # los dedos, hacia abajo: las manos, a la altura de las rodillas
    dedos=0.0,          # los dedos del pie, planos en el suelo (positivo: las puntas hacia abajo)
)


# ======================================================================================================================
#  Utilidades de pintura
# ======================================================================================================================
def _malla(tw, th):
    return L._malla(tw, th)


def _limpiar(mk):
    """Quita los píxeles sueltos de una máscara (los que no tienen ningún vecino igual): nada de ruido de un píxel."""
    v = np.zeros(mk.shape, int)
    v[1:, :] += mk[:-1, :]
    v[:-1, :] += mk[1:, :]
    v[:, 1:] += mk[:, :-1]
    v[:, :-1] += mk[:, 1:]
    return mk & (v > 0)


def _moteado(xs, ys, s, claro=0.68, oscuro=0.31):
    """El moteado suave de la piel: manchas de 2 a 5 píxeles, claras y oscuras, limpias (sin píxeles sueltos), de
    rejillas desplazadas que se suman para que no se vea la cuadrícula. Devuelve +1, 0 o -1."""
    n = (0.45 * _azar1((xs + 2) // 4, (ys + 1) // 4, s + 5) + 0.35 * _azar1((xs + 1) // 3, (ys + 2) // 3, s + 7)
         + 0.2 * _azar1(xs // 2, ys // 2, s + 9))
    cl = _limpiar(n > claro)
    os_ = _limpiar(n < oscuro)
    return cl.astype(int) - os_.astype(int)


def _z_delante(cara, xs, ys, tw, th):
    """La distancia (en píxeles) al canto de delante de la caja, en las caras que corren a lo largo de ella."""
    if cara == 'izq':
        return tw - 1 - xs
    if cara == 'der':
        return xs
    if cara == 'arriba':
        return th - 1 - ys
    if cara == 'abajo':
        return ys
    return None


def _rayas_tyrannok(L_, s, paso=(6, 7), ancho=(3, 3), largo=(0.42, 0.62), roto=0.45, desde=1):
    """Las rayas de tigre a lo largo de una pieza de L_ píxeles (desde delante): (z, ancho, largo, rotura, ladeo,
    mancha debajo). Como en 5:29:49.10: unas 3 px de ancho cada 6-7, casi tan anchas como el oro de entre medias."""
    rng = np.random.default_rng(int(s) * 131 + L_ * 7 + 3)
    out = []
    z = desde + int(rng.integers(0, 3))
    while z < L_ - 1:
        w = int(rng.choice(range(ancho[0], ancho[1] + 1), p=None))
        lf = float(rng.uniform(*largo))
        rot = float(rng.uniform(0.45, 0.62)) if rng.uniform() < roto else None
        lad = int(rng.choice([-1, 1]))
        debajo = rng.uniform() < 0.6
        out.append((z, w, lf, rot, lad, debajo))
        z += int(rng.integers(paso[0], paso[1] + 1))
    return out


def _mascara_rayas_lado(zf, ys, th, rayas):
    """Las rayas en una cara de lado, como en el juego (5:29:49.10): cada una, dos o tres trozos rectos apilados desde
    el lomo, el de abajo corrido un píxel y algo más estrecho (a veces con un píxel de hueco entre los dos), y debajo,
    a veces, una mancha suelta de 2-3 × 2-3."""
    raya = np.zeros(zf.shape, bool)
    mancha = np.zeros(zf.shape, bool)
    for (z, w, lf, rot, lad, debajo) in rayas:
        fin = max(3, int(round(lf * th)))
        corte = int(round(fin * 0.55))                    # donde empieza el trozo de abajo
        arriba_ = (zf >= z) & (zf < z + w) & (ys < corte)
        w2 = max(2, w - 1)
        z2 = z + (lad if lad > 0 else 0)
        abajo_ = (zf >= z2) & (zf < z2 + w2) & (ys >= corte + (1 if rot is not None else 0)) & (ys < fin)
        raya |= arriba_ | abajo_
        if debajo:
            y0 = fin + 2
            h = 2 + (w > 2)
            zc = z + lad
            mancha |= (zf >= zc) & (zf < zc + 2 + (w > 2)) & (ys >= y0) & (ys < y0 + h)
    return raya, mancha


def piel_tyrannok(nombre, rayas=None, manchas=0.0, crema=0.0, crema_caras=('abajo',), bandas=None, base=3.0,
                  arriba_claro=0.25, sin_rayas_arriba=False, semilla=0):
    """La piel del Tyrannok, al píxel (16 por bloque):
      - el oro con el moteado suave (claro y oscuro, de 2 a 4 píxeles);
      - rayas: las de tigre (dict para _rayas_tyrannok): bajan del lomo por los costados y cruzan por encima;
      - manchas: las manchas sueltas de la mitad de abajo del costado (cuántas, de 0 a 1);
      - crema: la parte de abajo de los costados que es crema (el vientre), con el borde en escalones; las caras de
        'crema_caras', crema enteras;
      - bandas: las bandas a lo ancho de las patas y los brazos (paso, ancho): trazos oscuros que no llegan a los
        cantos, algunos partidos en dos."""
    def fn(tw, th, c, s):
        s = s + semilla
        xs, ys = _malla(tw, th)
        v = np.full((th, tw), base) + _moteado(xs, ys, s) * 0.85
        if c == 'arriba':
            v = v + arriba_claro
        raya = np.zeros((th, tw), bool)
        mancha = np.zeros((th, tw), bool)
        zf = _z_delante(c, xs, ys, tw, th)
        lado = c in ('izq', 'der')
        lista = None
        if rayas is not None and zf is not None and c != 'abajo':
            lista = _rayas_tyrannok(tw if lado else th, s, **rayas)
            if lado:
                raya, mancha = _mascara_rayas_lado(zf, ys, th, lista)
            elif not sin_rayas_arriba:
                for (z, w, lf, rot, lad, debajo) in lista:
                    raya |= (zf >= z) & (zf < z + w)
        if manchas > 0 and lado:
            rng = np.random.default_rng(int(s) * 17 + tw * 5 + th)
            y0, y1 = int(th * 0.45), int(th * (1.0 - crema) - 1)
            n = int(round(manchas * tw * max(0, y1 - y0) / 30.0))
            for _ in range(n):
                w_, h_ = int(rng.integers(2, 4)), int(rng.integers(2, 5))
                x_ = int(rng.integers(0, max(1, tw - w_)))
                y_ = int(rng.integers(y0, max(y0 + 1, y1 - h_ + 1)))
                mancha[y_:y_ + h_, x_:x_ + w_] = True
        mancha &= ~raya
        if bandas is not None and c in ('izq', 'der', 'frente', 'atras'):
            paso, an = bandas.get('paso', 4), bandas.get('ancho', 1)
            desde = bandas.get('desde', 1)
            # Como en el juego (5:29:49.10, 5:29:44.22): filas de manchas pardas de 2 de alto, cada fila hecha de
            # trozos de 2 a 5 de largo con huecos de 1-2, y cada trozo a su altura (±1).
            rng = np.random.default_rng(int(s) * 23 + th * 3 + tw + len(c))
            for k, y0 in enumerate(range(desde, th - 1, paso)):
                if k >= bandas.get('cuantas', 99):
                    break
                x = int(rng.integers(0, 2))
                while x < tw - 1:
                    largo_ = int(rng.integers(3, 7))
                    dy = int(rng.choice([-1, 0, 0, 1]))
                    raya |= (ys >= y0 + dy) & (ys < y0 + dy + an) & (xs >= x) & (xs < x + largo_)
                    x += largo_ + int(rng.integers(1, 3))
        crema_mk = np.zeros((th, tw), bool)
        if c in crema_caras:
            crema_mk[...] = True
        elif crema > 0 and c in ('izq', 'der', 'frente', 'atras'):
            rng = np.random.default_rng(int(s) * 29 + tw)
            corte = np.zeros(tw, int)
            x = 0
            h0 = int(round(th * (1.0 - crema)))
            while x < tw:
                paso_ = int(rng.integers(3, 6))
                corte[x:x + paso_] = h0 + int(rng.choice([-1, 0, 0, 1]))
                x += paso_
            crema_mk = ys >= corte[None, :]
        rgb = L.color_continuo(ORO_TYRANNOK, v)
        rv = 3.0 + _moteado(xs, ys, s + 77, 0.8, 0.2) * 0.45 - 0.2 * (c != 'arriba')
        rgb = np.where(raya[..., None], L.color_continuo(RAYA_TYRANNOK, rv), rgb)
        rgb = np.where(mancha[..., None], L.color_continuo(RAYA_TYRANNOK, rv + 0.25), rgb)
        cv = 3.0 + _moteado(xs, ys, s + 91, 0.78, 0.22) * 0.55 - 0.2 * (c == 'abajo')
        rgb = np.where(crema_mk[..., None], L.color_continuo(CREMA_TYRANNOK, cv), rgb)
        return L._rgba(rgb), None
    return B.Pintor(nombre, fn)


def crema_tyrannok(nombre, base=3.0, canto=None):
    """La crema (la mandíbula, la garganta): caqui con un moteado muy suave. 'canto': en esas caras, la fila de arriba
    es el canto claro."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        v = base + _moteado(xs, ys, s + 3, 0.76, 0.24) * 0.55 - 0.25 * (c == 'abajo')
        if canto and c in canto:
            v = np.where(ys == 0, 4.2, v)
        return L._rgba(L.color_continuo(CREMA_TYRANNOK, v)), None
    return B.Pintor(nombre, fn)


def liso_tyrannok(nombre, R, base=3.0, mot=0.4):
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        v = base + _moteado(xs, ys, s + 11, 0.75, 0.25) * mot
        return L._rgba(L.color_continuo(R, v)), None
    return B.Pintor(nombre, fn)


def garra_tyrannok(nombre):
    """La garra en bloque: gris oscuro algo pardo, el canto de arriba más claro."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        v = np.full((th, tw), 2.6)
        if c == 'arriba':
            v[...] = 3.6
        elif c == 'abajo':
            v[...] = 1.4
        else:
            v = v + (ys == 0) * 1.0 - (ys == th - 1) * 0.6
        return L._rgba(L.color_continuo(GARRA_TYRANNOK, v)), None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def _fino_sobre(piel, tw, th, c, s):
    """La piel al píxel de 16 por bloque, doblada para pintar encima a 32 por bloque."""
    base = piel.fn(max(1, (tw + 1) // 2), max(1, (th + 1) // 2), c, s)[0][..., :3].astype(float)
    return np.repeat(np.repeat(base, 2, 0), 2, 1)[:th, :tw]


def _mapa_lado_tyrannok():
    """El lado de la cabeza (los dos lados, iguales), 25 texels de largo (columna 0, la nuca) por 14 de alto (fila 0,
    el techo del hocico; el cráneo, 1,5 más alto, sube por encima de la fila 0). '.': la piel de siempre.
      - el ojo en la fila 7: el brillo blanco detrás (columna 10) y los 2 negros delante (11-12), justo detrás del
        escalón entre el cráneo y el hocico (5:29:49.10, 5:29:38.05, 4:36:23.72);
      - la ceja: un reborde oscuro con su canto claro encima, que empieza 3,5 texels por encima del brillo y baja en
        diagonal hacia delante hasta la altura del ojo, 6 texels más adelante (medido en la principal, 5:29:42.67);
      - la mejilla: una banda más oscura por debajo del ojo, a lo largo del hocico, con el canto de arriba oscuro
        (5:29:42.67, 5:29:49.10, 4:36:23.72); por encima de la ceja, el lado del hocico queda más claro;
      - el labio: la fila de abajo del hocico, dorada y algo más clara."""
    W, H_ = 25, 14
    g = [['.'] * W for _ in range(H_)]

    def pon(c, r, ch):
        if 0 <= c < W and 0 <= r < H_:
            g[r][c] = ch
    # El lado del hocico por encima de la ceja, algo más claro.
    for c in range(13, 25):
        for r in range(0, 5):
            pon(c, r, 'L')
    # La ceja (canto claro 'f' encima, reborde oscuro 'b' debajo), de atrás adelante.
    for c, r in ((9, 2), (10, 3), (11, 3), (12, 4), (13, 4), (14, 5), (15, 5), (16, 6), (17, 6)):
        for rr in range(0, r):
            if c >= 13:
                pon(c, rr, 'L')
        pon(c, r, 'f')
        pon(c, r + 1, 'b')
    # El ojo.
    pon(10, 7, 'w')
    pon(11, 7, 'k')
    pon(12, 7, 'k')
    # La mejilla: el canto oscuro desde el ojo hacia delante y la banda más oscura debajo.
    for c in range(13, 23):
        pon(c, 8, 'b')
    for c in range(13, 24):
        for r in (9, 10):
            pon(c, r, 'o')
    for c in range(14, 23):
        pon(c, 11, 'o')
    # El labio.
    for c in range(13, 25):
        pon(c, 13, 'L')
    return [''.join(f) for f in g]


MAPA_LADO_TYRANNOK = _mapa_lado_tyrannok()


def _pinta_mapa(rgb, mapa, colores, ii, jj):
    for j in range(len(mapa)):
        fila = mapa[j]
        for i, ch in enumerate(fila):
            if ch in colores:
                rgb[(ii == i) & (jj == j)] = colores[ch]


def cabeza_tyrannok(nombre, piel, col0, largo_t, alto_t, cara=False, paladar=True):
    """La piel de una caja de la cabeza, a 32 por bloque, con el mapa del lado encima ('col0': la columna del mapa
    donde empieza la caja, desde la nuca; 'largo_t' x 'alto_t': lo que mide la caja en texels del juego; el mapa se
    alinea por abajo), 'cara': el mapa de la cara de delante; 'paladar': la cara de abajo, granate."""
    colores = dict(CARA_TYRANNOK)
    colores.update({'w': BRILLO_TYRANNOK, 'k': PUPILA_TYRANNOK})

    def fn(tw, th, c, s):
        if c == 'abajo' and paladar:
            xs, ys = _malla(tw, th)
            v = 2.6 + _moteado(xs, ys, s + 1, 0.8, 0.2) * 0.4
            return L._rgba(L.color_continuo(BOCA_TYRANNOK, v)), None
        rgb = _fino_sobre(piel, tw, th, c, s)
        xs, ys = _malla(tw, th)
        if c in ('izq', 'der'):
            zt = (xs + 0.5) / tw * largo_t                  # desde atrás
            if c == 'der':
                zt = largo_t - zt
            ii = np.floor(col0 + zt).astype(int)
            jj = np.floor(14.0 - alto_t + (ys + 0.5) / th * alto_t).astype(int)
            _pinta_mapa(rgb, MAPA_LADO_TYRANNOK, colores, ii, jj)
        if c == 'frente' and cara:
            mp = MAPA_CARA_TYRANNOK
            H_, W_ = len(mp), len(mp[0])
            ii = np.minimum(((xs + 0.5) / tw * W_).astype(int), W_ - 1)
            jj = np.minimum(((ys + 0.5) / th * H_).astype(int), H_ - 1)
            _pinta_mapa(rgb, mp, colores, ii, jj)
        return L._rgba(rgb), None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def suelo_boca_tyrannok(nombre, canto_t, ancho_t, largo_t):
    """La cara de arriba de la mandíbula: el suelo granate con el canto claro de 1 texel alrededor (delante y a los
    lados); los lados y el fondo, crema."""
    crema = crema_tyrannok(nombre + '_c')

    def fn(tw, th, c, s):
        if c != 'arriba':
            return crema.fn(tw, th, c, s)
        xs, ys = _malla(tw, th)
        xt = (xs + 0.5) / tw * ancho_t
        zt = (th - (ys + 0.5)) / th * largo_t        # desde atrás (la fila de abajo es delante)
        borde = (xt < canto_t) | (xt > ancho_t - canto_t) | (zt > largo_t - canto_t)
        v = 2.9 + _moteado(xs, ys, s + 4, 0.8, 0.2) * 0.35
        rgb = L.color_continuo(BOCA_TYRANNOK, v)
        rgb = np.where(borde[..., None], L.color_continuo(CREMA_TYRANNOK, np.full((th, tw), 4.1)), rgb)
        return L._rgba(rgb), None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def lengua_tyrannok(nombre):
    """La lengua rosa en relieve, con la línea del medio más clara."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        if c == 'arriba':
            v = np.where(np.abs((xs + 0.5) - tw / 2) <= 0.75, 3.9, 3.0)
        else:
            v = np.full((th, tw), 2.0)
        return L._rgba(L.color_continuo(LENGUA_TYRANNOK, v)), None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def dientes_arriba_tyrannok(nombre, ancho_t, largo_t, alto_t, banda_t, lado_desde_t):
    """Los dientes de arriba en una 2.ª capa (la caja algo mayor que el borde de la cabeza): en la cara de delante 6
    (los 2 de las esquinas grandes, de 2 x 3 texels, y 4 pequeños de 1 x 2), en los lados una fila de dientes de 1 x 2,5
    con un hueco de 1 texel, como teclas de piano, desde delante hasta la comisura. Lo demás, vacío. 'banda_t': lo que
    la capa sube por encima del labio (vacío)."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c in ('arriba', 'abajo', 'atras'):
            return tex, None
        yt = (ys + 0.5) / th * alto_t - banda_t           # texels bajo el labio (negativo: encima)
        if c == 'frente':
            xt = (xs + 0.5) / tw * ancho_t
            mk = np.zeros((th, tw), bool)
            sombra = np.zeros((th, tw), bool)
            # Medidos en 5:29:43.82: los de las esquinas, de 2 de ancho y 3 de largo; los 4 del medio, de 1.
            for (x0, w, l) in ((0.0, 2.1, 3.0), (ancho_t - 2.1, 2.1, 3.0), (3.6, 1.0, 2.0), (5.8, 1.0, 1.6),
                               (ancho_t - 6.8, 1.0, 1.6), (ancho_t - 4.6, 1.0, 2.0)):
                d = (xt >= x0) & (xt < x0 + w) & (yt >= 0) & (yt < l)
                mk |= d
                sombra |= d & (xt >= x0 + w * 0.55)
        else:
            zt = (xs + 0.5) / tw * largo_t
            if c == 'izq':
                zt = largo_t - zt                         # desde delante
            mk = np.zeros((th, tw), bool)
            sombra = np.zeros((th, tw), bool)
            z = 2.1
            k = 0
            while z < largo_t - lado_desde_t:
                l = 2.2 if k % 3 != 1 else 1.8
                d = (zt >= z) & (zt < z + 1.0) & (yt >= 0) & (yt < l)
                mk |= d
                sombra |= d & (zt >= z + 0.55)
                z += 2.0
                k += 1
            # el diente grande de la esquina, de lado
            d = (zt < 2.0) & (yt >= 0) & (yt < 3.0)
            mk |= d
        punta = yt > 1.4
        v = np.where(sombra, 3.0, 3.5) + punta * 0.5
        tex[..., :3] = np.round(L.color_continuo(DIENTE_TYRANNOK, v)).astype(np.uint8)
        tex[..., 3] = np.where(mk, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def dientes_abajo_tyrannok(nombre, ancho_t, largo_t, alto_t, lado_hasta_t):
    """Los dientes de abajo en una 2.ª capa: de pie en el canto de dentro de la mandíbula, pequeños (1 x 1,5-2) y algo
    más grises; 4 delante y una fila a cada lado."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c in ('arriba', 'abajo', 'atras'):
            return tex, None
        yt = (th - (ys + 0.5)) / th * alto_t              # texels desde el canto, hacia arriba
        mk = np.zeros((th, tw), bool)
        sombra = np.zeros((th, tw), bool)
        if c == 'frente':
            xt = (xs + 0.5) / tw * ancho_t
            n = 4
            for k in range(n):
                x0 = (k + 0.5) / n * ancho_t - 0.5
                l = 1.8 if k in (0, n - 1) else 1.5
                d = (xt >= x0) & (xt < x0 + 1.0) & (yt < l)
                mk |= d
                sombra |= d & (xt >= x0 + 0.55)
        else:
            zt = (xs + 0.5) / tw * largo_t
            if c == 'izq':
                zt = largo_t - zt
            z = 1.4
            k = 0
            while z < largo_t - lado_hasta_t:
                l = 1.8 if k % 2 == 0 else 1.5
                d = (zt >= z) & (zt < z + 1.0) & (yt < l)
                mk |= d
                sombra |= d & (zt >= z + 0.55)
                z += 2.0
                k += 1
        v = np.where(sombra, 2.4, 3.1) + (yt > 1.1) * 0.5
        tex[..., :3] = np.round(L.color_continuo(DIENTE_TYRANNOK, v)).astype(np.uint8)
        tex[..., 3] = np.where(mk, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), 0.5)


# ======================================================================================================================
#  Geometría
# ======================================================================================================================
def _rx(a):
    return B.girar((a, 0, 0))


def _pt(M, p):
    return (M @ np.array((p[0], p[1], p[2], 1.0)))[:3]


def _colgar(m, parte, M, tam, pint, arriba=0.0, caras=None):
    """Una caja que cuelga del origen del marco M a lo largo de su -Y (sube 'arriba' por encima del origen)."""
    w, h, d = tam
    caja_en(m, parte, M, (0.0, arriba - h / 2.0, 0.0), (w, h, d), pint, caras)


def construir():
    m = B.Modelo('tyrannok', K=2, ancho=256)
    m.escala = 1.0

    # ---------------- Los pintores ----------------
    piel = piel_tyrannok('piel_tyrannok')
    tronco = piel_tyrannok('tronco_tyrannok', rayas=dict(paso=(6, 7), ancho=(3, 3), largo=(0.42, 0.6)),
                           manchas=0.5, crema=0.22, crema_caras=('abajo', 'frente'))
    cadera = piel_tyrannok('cadera_tyrannok', rayas=dict(paso=(6, 7), ancho=(3, 3), largo=(0.42, 0.6)),
                           manchas=0.45, crema=0.2, crema_caras=('abajo',), semilla=7)
    cuello = piel_tyrannok('cuello_tyrannok', rayas=dict(paso=(6, 7), ancho=(3, 3), largo=(0.3, 0.42)),
                           crema=0.45, crema_caras=('abajo',), semilla=3)
    cola = piel_tyrannok('cola_tyrannok', rayas=dict(paso=(5, 7), ancho=(3, 3), largo=(0.5, 0.7)),
                         crema=0.2, crema_caras=('abajo',), semilla=5)
    muslo = piel_tyrannok('muslo_tyrannok', bandas=dict(paso=6, ancho=2, desde=6, cuantas=4), semilla=2)
    espinilla = piel_tyrannok('espinilla_tyrannok', bandas=dict(paso=6, ancho=2, desde=4, cuantas=3),
                              semilla=4)
    brazo_p = piel_tyrannok('brazo_tyrannok', bandas=dict(paso=5, ancho=2, desde=4, cuantas=3), semilla=6)
    dedo = piel_tyrannok('dedo_tyrannok', semilla=8)
    garra = garra_tyrannok('garra_tyrannok')
    crema = crema_tyrannok('crema_tyrannok')

    P = POSTURA_TYRANNOK
    # ---------------- Las patas: dónde queda la cadera para que los dedos pisen el suelo ----------------
    def _dir(a):
        """La dirección de un hueso que baja desde su articulación, girado 'a' grados hacia delante."""
        return np.array((0.0, -math.cos(math.radians(a)), math.sin(math.radians(a))))
    LM, LE, LT = 17.75, 16.2, 8.5               # muslo (cadera-rodilla), espinilla (rodilla-tobillo), metatarso
    def _p(k, ld):
        """El ángulo 'k' del lado 'ld' (los dos lados, iguales salvo que la postura diga otra cosa)."""
        return P.get(f'{k}_{ld}', P[k])
    caida = max(-(LM * _dir(_p('muslo', ld)) + LE * _dir(_p('espinilla', ld)) + LT * _dir(_p('metatarso', ld)))[1]
                for ld in ('i', 'd'))
    H0 = np.array((0.0, 2.6 + caida, -1.5))     # la articulación de la cadera (y el pivote del cuerpo)

    # ---------------- El cuerpo (la raíz): el tronco y la cadera, inclinados ----------------
    INC = P['inc']                              # el tronco, con los hombros más altos que la cadera
    m.parte('cuerpo', None, tuple(H0))
    Mt = T(*H0) @ _rx(INC)
    caja_en(m, 'cuerpo', Mt, (0, -3.5, 19.5), (19, 22, 32), tronco)
    caja_en(m, 'cuerpo', Mt, (0, -4.5, -4.5), (16, 19, 20), cadera)

    # ---------------- El cuello: dos cajas escalonadas que suben del pecho ----------------
    N0 = _pt(Mt, (0, 2.5, 31.5))
    m.parte('cuello', 'cuerpo', tuple(N0))
    Mn = T(*N0) @ _rx(P['cuello'])
    caja_en(m, 'cuello', Mn, (0, -0.5, 2.5), (13, 15, 9), cuello)
    caja_en(m, 'cuello', Mn, (0, 1.5, 6.25), (12, 12, 6.5), cuello)

    # ---------------- La cabeza ----------------
    # El origen de la cabeza: el centro de abajo de su cara de atrás (la línea del labio). Largo 25, ancho 15; el
    # cráneo (los 13 de atrás) mide 15,5 de alto y el hocico (los 12 de delante) 14: el escalón de 1,5 texels sobre los
    # ojos de la ficha (el icono, 5:29:38.05, 5:29:42.67). Probado contra las tres referencias con la cabeza y el
    # cuello libres: el cráneo de 15,5 da 0.872 / 0.850 / 0.816; el de 12 (el hocico más alto), 0.872 / 0.823 / 0.796.
    C0 = _pt(Mn, (0, -4.5, 9.5))
    m.parte('cabeza', 'cuello', tuple(C0))
    Mc = T(*C0) @ _rx(P['cabeza'])
    lado_cr = cabeza_tyrannok('craneo_tyrannok', piel, 0.0, 13.0, 15.5)
    lado_ho = cabeza_tyrannok('hocico_tyrannok', piel, 13.0, 12.0, 14.0, cara=True)
    caja_en(m, 'cabeza', Mc, (0, 7.75, 6.5), (15, 15.5, 13), lado_cr)
    caja_en(m, 'cabeza', Mc, (0, 7.0, 19.0), (15, 14, 12), lado_ho)
    # Los dientes de arriba (2.ª capa): desde justo detrás del ojo hasta delante (5:29:42.67: 8 por lado con el de la
    # esquina, como teclas de piano).
    caja_en(m, 'cabeza', Mc, (0, -1.35, 17.08), (15.4, 3.7, 16.15),
            dientes_arriba_tyrannok('dientes_arriba_tyrannok', 15.4, 16.15, 3.7, 0.5, 0.6))

    # ---------------- La mandíbula: abierta desde la comisura (el 90 % del largo) ----------------
    G = _pt(Mc, (0, 0.0, 2.5))
    m.parte('mandibula', 'cabeza', tuple(G))
    Mj = T(*G) @ _rx(P['cabeza'] + P['abre'])
    caja_en(m, 'mandibula', Mj, (0, -2.5, 11.25), (12, 5, 22.5),
            suelo_boca_tyrannok('mandibula_tyrannok', 1.0, 12.0, 22.5))
    caja_en(m, 'mandibula', Mj, (0, 0.5, 10.0), (5.0, 1.0, 15.0), lengua_tyrannok('lengua_tyrannok'))
    caja_en(m, 'mandibula', Mj, (0, 1.0, 12.4), (10.4, 2.0, 19.6),
            dientes_abajo_tyrannok('dientes_abajo_tyrannok', 10.4, 19.6, 2.0, 1.0))

    # ---------------- La cola, en dos tramos; la punta cortada en cuadrado ----------------
    # El segundo tramo mide 0,6 del alto del primero (VOD 3:12:08.75 y 09.10: 28/52 y 35/53) y, en la principal,
    # 0,14 del alto de la figura (con 10,5 de alto salía 0,22). Los dos, casi horizontales. Probado a bajar el primero
    # 5 texels (como parecía en esos perfiles): empeora las tres referencias, era la perspectiva.
    C1 = _pt(Mt, (0, -1.0, -13.5))
    m.parte('cola', 'cuerpo', tuple(C1))
    Mk = T(*C1) @ _rx(P['cola1'])
    caja_en(m, 'cola', Mk, (0, 0.0, -8.5), (11.5, 13, 18), cola)
    C2 = _pt(Mk, (0, -1.0, -16.5))
    m.parte('cola2', 'cola', tuple(C2))
    Mk2 = T(*C2) @ _rx(P['cola2'])
    caja_en(m, 'cola2', Mk2, (0, 0.0, -11.0), (7.5, 8, 23), cola)

    # ---------------- Las patas, en zigzag ----------------
    for lado, ld in ((1, 'i'), (-1, 'd')):
        x = lado * 7.4
        cad = np.array((x, H0[1], H0[2]))
        rod = cad + LM * _dir(_p('muslo', ld))
        tob = rod + LE * _dir(_p('espinilla', ld))
        bol = tob + LT * _dir(_p('metatarso', ld))
        n = m.parte(f'pierna_{ld}', 'cuerpo', tuple(cad))
        _colgar(m, n, T(*cad) @ _rx(-_p('muslo', ld)), (11, 22, 12.5), muslo, arriba=4.5)
        n2 = m.parte(f'cana_{ld}', n, tuple(rod))
        _colgar(m, n2, T(*rod) @ _rx(-_p('espinilla', ld)), (8, 17.5, 8), espinilla, arriba=2.6)
        n3 = m.parte(f'pie_{ld}', n2, tuple(tob))
        _colgar(m, n3, T(*tob) @ _rx(-_p('metatarso', ld)), (7, 11, 7), piel, arriba=1.6)
        # Los tres dedos (dorados, algo abiertos) y sus garras en bloque, en su parte (gira en la bola del pie: así se
        # quedan planos en el suelo aunque el tobillo cambie de ángulo, y caen un poco al levantar el pie).
        n4 = m.parte(f'dedos_{ld}', n3, (x, 2.6, bol[2]))
        for k, giro in ((-1, -16.0), (0, 0.0), (1, 16.0)):
            Md = T(x + k * 2.2, 1.0, bol[2] - 1.0) @ B.girar((0, giro, 0))
            caja_en(m, n4, Md, (0, 0, 3.0), (2.0, 2.0, 6.5), dedo)
            caja_en(m, n4, Md @ T(0, -0.1, 7.2) @ _rx(14.0), (0, 0, 0), (2.0, 2.2, 3.0), garra)

    # ---------------- Los brazos: el brazo cuelga del bajo del pecho, el antebrazo va hacia delante ----------------
    for lado, ld in ((1, 'i'), (-1, 'd')):
        hom = _pt(Mt, (lado * 10.6, -12.5, 29.0))
        n = m.parte(f'brazo_{ld}', 'cuerpo', tuple(hom))
        _colgar(m, n, T(*hom) @ _rx(-_p('brazo', ld)), (5, 15, 5), brazo_p, arriba=1.5)
        codo = hom + 12.63 * _dir(_p('brazo', ld))
        n2 = m.parte(f'antebrazo_{ld}', n, tuple(codo))
        _colgar(m, n2, T(*codo) @ _rx(-_p('antebrazo', ld)), (5, 14, 5), piel, arriba=1.8)
        mun = codo + 11.5 * _dir(_p('antebrazo', ld))
        n3 = m.parte(f'mano_{ld}', n2, tuple(mun))
        # La mano: 3 dedos dorados que siguen al antebrazo, algo más hacia abajo, y en la punta de cada uno su garra
        # en bloque, gris oscuro, que cuelga hacia el suelo.
        for k in (-1, 0, 1):
            # Los dedos, algo abiertos en abanico y con hueco entre las garras (5:29:43.80: 3 bloques oscuros sueltos).
            Md = T(mun[0] + k * 2.3, mun[1], mun[2]) @ B.girar((0, 0, -k * 6.0)) @ _rx(-_p('mano', ld))
            _colgar(m, n3, Md, (1.6, 5.0, 2.0), dedo, arriba=0.6)
            caja_en(m, n3, Md @ T(0, -4.6, 0.0) @ _rx(35.0), (0, -1.4, 0.3), (1.8, 3.2, 2.2), garra)

    m.mirar(('cabeza', 0.6), ('cuello', 0.3))
    anims_tyrannok(m)
    return m


# ======================================================================================================================
#  Animaciones: cada clave es una postura del cuerpo entero (los ángulos de POSTURA_TYRANNOK que cambian; los de las
#  patas y los brazos pueden ir por lado: 'muslo_i', 'brazo_d'...). De la postura se saca lo que gira cada parte y lo
#  que sube o baja el cuerpo para que el pie que apoya siga en el suelo.
# ======================================================================================================================
LM_TYRANNOK, LE_TYRANNOK, LT_TYRANNOK = 17.75, 16.2, 8.5
PARTES_POSE_TYRANNOK = ('cuerpo', 'cuello', 'cabeza', 'mandibula', 'cola', 'cola2',
                        'pierna_i', 'cana_i', 'pie_i', 'dedos_i', 'pierna_d', 'cana_d', 'pie_d', 'dedos_d',
                        'brazo_i', 'antebrazo_i', 'mano_i', 'brazo_d', 'antebrazo_d', 'mano_d')


def _pierna_tyrannok(a1, a2, a3):
    """Lo que baja la pierna desde la cadera hasta la bola del pie (y), y lo que se adelanta (z)."""
    r = math.radians
    y = LM_TYRANNOK * math.cos(r(a1)) + LE_TYRANNOK * math.cos(r(a2)) + LT_TYRANNOK * math.cos(r(a3))
    z = LM_TYRANNOK * math.sin(r(a1)) + LE_TYRANNOK * math.sin(r(a2)) + LT_TYRANNOK * math.sin(r(a3))
    return y, z


def pose_tyrannok(destino, fijar_z=False):
    """Los giros (X del boceto, grados) de cada parte y el movimiento del cuerpo (y, z en texels) que llevan de la
    postura de reposo a 'destino'. Con 'fijar_z', el cuerpo se corre para que el pie que apoya no resbale."""
    R = POSTURA_TYRANNOK

    def v(k, ld=None):
        if ld and f'{k}_{ld}' in destino:
            return destino[f'{k}_{ld}']
        return destino.get(k, R[k])
    rot = {}
    dc = v('inc') - R['inc']
    rot['cuerpo'] = dc
    rot['cuello'] = v('cuello') - R['cuello'] - dc
    rot['cabeza'] = (v('cabeza') - R['cabeza']) - (v('cuello') - R['cuello'])
    rot['mandibula'] = v('abre') - R['abre']
    rot['cola'] = v('cola1') - R['cola1'] - dc
    rot['cola2'] = (v('cola2') - R['cola2']) - (v('cola1') - R['cola1'])
    patas = []
    for ld in ('i', 'd'):
        dp = R['muslo'] - v('muslo', ld) - dc
        dk = R['espinilla'] - v('espinilla', ld) - dc - dp
        df = R['metatarso'] - v('metatarso', ld) - dc - dp - dk
        rot[f'pierna_{ld}'], rot[f'cana_{ld}'], rot[f'pie_{ld}'] = dp, dk, df
        rot[f'dedos_{ld}'] = v('metatarso', ld) - R['metatarso'] + v('dedos', ld) - R['dedos']
        db = R['brazo'] - v('brazo', ld) - dc
        da = R['antebrazo'] - v('antebrazo', ld) - dc - db
        dm = R['mano'] - v('mano', ld) - dc - db - da
        rot[f'brazo_{ld}'], rot[f'antebrazo_{ld}'], rot[f'mano_{ld}'] = db, da, dm
        patas.append(_pierna_tyrannok(v('muslo', ld), v('espinilla', ld), v('metatarso', ld)))
    y0, z0 = _pierna_tyrannok(R['muslo'], R['espinilla'], R['metatarso'])
    yy, zz = max(patas)                                # apoya la pata que más baja
    dz = (z0 - zz) if fijar_z else 0.0
    return rot, (0.0, yy - y0, dz)


def lo_mas_bajo_tyrannok(m, a, t):
    """Lo más bajo de todas las cajas (y del boceto) con la animación 'a' en el instante t."""
    Ainv = np.linalg.inv(B.A)
    mund = m.mundos(a, t)
    lo = 1e9
    for n, p in m.partes.items():
        for caja in p.cajas:
            Bm, (x0, y0, z0, w, h, d) = m.caja_mc(p, caja)
            (bx, by, bz), (ax, ay, az) = m.pose(Bm)
            M = Ainv @ mund[n] @ T(bx, by, bz) @ B.Rz(az) @ B.Ry(ay) @ B.Rx(ax)
            for dx in (0, w):
                for dy in (0, h):
                    for dz in (0, d):
                        lo = min(lo, float((M @ np.array((x0 + dx, y0 + dy, z0 + dz, 1.0)))[1]))
    return lo


def al_suelo_tyrannok(m, a, n):
    """Sube o baja el cuerpo en cada instante para que lo más bajo quede donde en reposo: ni se hunde en el suelo ni
    flota (para la muerte, que gira el cuerpo entero)."""
    ref = lo_mas_bajo_tyrannok(m, None, 0.0)
    claves = []
    for k in range(n + 1):
        t = a.largo * k / n
        claves.append((t, 0.0, round(ref - lo_mas_bajo_tyrannok(m, a, t), 3), 0.0))
    a.mov('cuerpo', claves)


def _mezcla_tyrannok(d0, d1, f):
    """La postura a medio camino entre d0 y d1 (f de 0 a 1)."""
    R = POSTURA_TYRANNOK
    out = {}
    for k in set(d0) | set(d1):
        base = R.get(k.rsplit('_', 1)[0], 0.0) if k not in R else R[k]
        v0 = d0.get(k, d0.get(k.rsplit('_', 1)[0], base))
        v1 = d1.get(k, d1.get(k.rsplit('_', 1)[0], base))
        out[k] = v0 + (v1 - v0) * f
    return out


def claves_pose_tyrannok(a, claves, fijar_z=False, sub=0):
    """Las claves de una animación a partir de posturas: claves = [(t, destino), ...] (o (t, destino, suave)). Con
    'sub', entre cada dos posturas se meten 'sub' posturas intermedias (mezcladas con suavidad), cada una con su altura
    del cuerpo: así los pies no se hunden ni flotan a medio camino."""
    if sub:
        mas = []
        for (c0, c1) in zip(claves[:-1], claves[1:]):
            mas.append(c0)
            for i in range(1, sub + 1):
                u = i / (sub + 1)
                f = 0.5 - 0.5 * math.cos(math.pi * u)
                mas.append((c0[0] + (c1[0] - c0[0]) * u, _mezcla_tyrannok(c0[1], c1[1], f)))
        mas.append(claves[-1])
        claves = mas
    canales = {p: [] for p in PARTES_POSE_TYRANNOK}
    mov = []
    for c in claves:
        t, destino = c[0], c[1]
        suave = c[2] if len(c) > 2 else 1
        rot, (dx, dy, dz) = pose_tyrannok(destino, fijar_z)
        for p in PARTES_POSE_TYRANNOK:
            canales[p].append((t, round(rot[p], 2), 0.0, 0.0, suave))
        mov.append((t, dx, round(dy, 3), round(dz, 3), suave))
    for p, ks in canales.items():
        if any(abs(k[1]) > 0.05 for k in ks):
            a.rot(p, ks)
    if any(abs(k[2]) > 0.01 or abs(k[3]) > 0.01 for k in mov):
        a.mov('cuerpo', mov)


def _paso_pose_tyrannok(p, amp, rodilla, base):
    """Una pata en la fase p (0: delante del todo, posándose; 0,5: atrás): apoya de 0 a 0,62 (el muslo va hacia atrás)
    y en el vuelo dobla la rodilla, levanta el pie y lo lleva hacia delante."""
    p = p % 1.0
    if p < 0.62:
        f = p / 0.62
        a1 = base['muslo'] + amp * math.cos(math.pi * f)
        vuelo = 0.0
    else:
        f = (p - 0.62) / 0.38
        a1 = base['muslo'] - amp * math.cos(math.pi * f)
        vuelo = math.sin(math.pi * f)
    a2 = base['espinilla'] - rodilla * vuelo - 0.35 * (a1 - base['muslo'])
    a3 = base['metatarso'] + rodilla * 0.55 * vuelo + 0.2 * (base['muslo'] - a1)
    return a1, a2, a3


def vuelo_tyrannok(p):
    """Cuánto está en el aire una pata en la fase p (0 apoyada, 1 en lo alto del vuelo)."""
    p = p % 1.0
    return 0.0 if p < 0.62 else math.sin(math.pi * (p - 0.62) / 0.38)


def ciclo_tyrannok(a, largo, n, base, amp, rodilla, cuerpo=None):
    """Un ciclo de marcha: n posturas seguidas, las dos patas a media vuelta. 'cuerpo(fase)' da lo demás de cada
    postura (tronco, cuello, cola, brazos...)."""
    claves = []
    for k in range(n + 1):
        ph = k / n
        d = dict(base)
        for ld, f0 in (('i', 0.0), ('d', 0.5)):
            a1, a2, a3 = _paso_pose_tyrannok(ph + f0, amp, rodilla, base)
            d[f'muslo_{ld}'], d[f'espinilla_{ld}'], d[f'metatarso_{ld}'] = a1, a2, a3
            d[f'dedos_{ld}'] = 30.0 * max(0.0, vuelo_tyrannok(ph + f0) - 0.4) / 0.6
        if cuerpo:
            d.update(cuerpo(ph))
        claves.append((largo * ph, d))
    claves_pose_tyrannok(a, claves)


def _onda(largo, n, amp, fase=0.0, base=0.0, eje=1, ciclos=1.0):
    """Claves de una oscilación (para los giros de lado y de balanceo)."""
    out = []
    for k in range(n + 1):
        t = largo * k / n
        v = base + amp * math.sin(2 * math.pi * (ciclos * k / n + fase))
        xyz = [0.0, 0.0, 0.0]
        xyz[eje] = round(v, 2)
        out.append((t, *xyz))
    return out


# La postura del rugido (el clip de Lenniay, 0:11.6-0:11.7, y el de cracksterss, 0:17.7-0:18.6): erguido (el tronco a
# 52°) enseñando la tripa crema, el cuello echado hacia delante para que la cabeza quede delante del pecho y la
# mandíbula cuelgue por delante (si no, se mete en el pecho), la cabeza mirando abajo, hacia quien tiene delante, y la
# boca abierta del todo: se ven el paladar, la lengua y el suelo de la boca, justo bajo los dientes de arriba. Los brazos, como en el clip: el brazo sale hacia fuera y algo hacia abajo, el
# antebrazo viene hacia delante (hacia quien mira) y la mano levanta las garras. Las direcciones (brazo
# (0,8, -0,5, 0,3), antebrazo (0,3, -0,15, 0,94) y mano (0,3, 0,6, 0,75), del lado izquierdo) dan los giros con
# util/brazo_solver.py: los X van en la postura y los Y y Z, aparte (BRAZO_RUGIDO_TYRANNOK).
RUGIDO_TYRANNOK = dict(inc=-52.0, cuello=-22.0, cabeza=18.0, abre=54.0, cola1=-10.0, cola2=-2.0, muslo=14.0,
                       espinilla=-22.0, metatarso=40.0, brazo=31.4, antebrazo=81.5, mano=98.2)
# Los giros Y y Z de los brazos en el rugido (del lado izquierdo; el derecho, al revés).
BRAZO_RUGIDO_TYRANNOK = {'brazo': (0.0, 53.9), 'antebrazo': (-19.1, -4.0), 'mano': (38.5, 20.3)}


def anims_tyrannok(m):
    """Las animaciones (los nombres que entiende el juego):
      siempre   respira: la mandíbula y el cuello, un poco;
      reposo    la cola se mece despacio, el cuerpo respira y la cabeza mira a un lado y a otro;
      andar     zancadas: la rodilla se dobla al llevar la pata delante, el pie que apoya no se mueve del suelo, el
                cuerpo sube y baja con el paso, la cola se mece al contrapaso y los brazos se balancean;
      correr    lo mismo, más largo y rápido: el tronco más empinado, el cuello alto, la boca abierta, los brazos
                delante y la cola siguiendo la línea del tronco (5:29:42-49);
      ataque    el mordisco: se echa atrás abriendo la boca, se agacha de golpe con la boca abierta del todo y las manos
                hacia el suelo (5:29:42.67) y la cierra;
      especial  el rugido del clip (0:11.6-0:11.7): se yergue hasta poner el tronco casi vertical, enseña la tripa
                crema, la cabeza arriba con la boca abierta del todo y los brazos abiertos a los lados con las garras
                hacia arriba; tiembla rugiendo y vuelve;
      muerte    se derrumba de lado;
      aparece   sale agachado y se levanta con un rugido corto."""
    # ---- siempre ----
    s_ = m.anim('siempre', 2.4, bucle=True)
    s_.rot('mandibula', _onda(2.4, 8, 2.0, eje=0))
    s_.rot('cuello', _onda(2.4, 8, 0.8, fase=0.25, eje=0))

    # ---- reposo ----
    r = m.anim('reposo', 4.0, bucle=True)
    r.mov('cuerpo', [(t / 2.0, 0, round(0.35 * math.sin(math.pi * t / 2.0), 3), 0) for t in range(9)])
    r.rot('cola', _onda(4.0, 8, 5.0))
    r.rot('cola2', _onda(4.0, 8, 7.0, fase=-0.12))
    r.rot('cabeza', [(0, 0, 0, 0), (0.5, 2, 14, 0), (1.6, 2, 14, 0), (2.1, 0, 0, 0), (2.5, 2, -12, 0),
                     (3.5, 2, -12, 0), (4.0, 0, 0, 0)])
    r.rot('cuello', [(0, 0, 0, 0), (0.5, 0, 5, 0), (1.6, 0, 5, 0), (2.1, 0, 0, 0), (2.5, 0, -4, 0),
                     (3.5, 0, -4, 0), (4.0, 0, 0, 0)])

    # ---- andar ----
    a = m.anim('andar', 1.4, bucle=True)
    base = dict(POSTURA_TYRANNOK)

    def cuerpo_andar(ph):
        return {'inc': base['inc'] + 1.5 * math.sin(4 * math.pi * ph),
                'cuello': base['cuello'] - 2.0 * math.sin(4 * math.pi * ph + 1.0),
                'cabeza': base['cabeza'] + 2.0 * math.sin(4 * math.pi * ph + 1.6),
                'brazo_i': base['brazo'] + 7 * math.sin(2 * math.pi * ph + math.pi),
                'brazo_d': base['brazo'] + 7 * math.sin(2 * math.pi * ph),
                'antebrazo_i': base['antebrazo'] + 5 * math.sin(2 * math.pi * ph + math.pi + 0.6),
                'antebrazo_d': base['antebrazo'] + 5 * math.sin(2 * math.pi * ph + 0.6)}
    ciclo_tyrannok(a, 1.4, 16, base, 15.0, 30.0, cuerpo_andar)
    a.rot('cola', _onda(1.4, 16, 7.0, fase=0.25))
    a.rot('cola2', _onda(1.4, 16, 10.0, fase=0.12))
    a.rot('cuerpo', _onda(1.4, 16, 2.5, fase=0.25, eje=2))

    # ---- correr ----
    # Como en 5:29:49.10 (corriendo de perfil): agachado, con zancadas largas (el muslo llega casi a la horizontal al
    # adelantar la pata), el tronco algo inclinado, el cuello alto, la cabeza recta con la boca abierta, la cola
    # siguiendo la línea del tronco hacia atrás y abajo, los brazos colgando con los antebrazos hacia delante. Probado
    # contra ese fotograma en 8 instantes del ciclo: 0.62-0.73 (con la carrera erguida de antes, 0.53-0.60).
    c = m.anim('correr', 0.72, bucle=True)
    base_c = dict(POSTURA_TYRANNOK, inc=-16.0, cuello=-40.0, cabeza=0.0, abre=24.0, cola1=-13.5, cola2=-8.8,
                  muslo=56.0, espinilla=-54.0, metatarso=44.0, brazo=2.0, antebrazo=88.0, mano=72.0)

    def cuerpo_correr(ph):
        return {'inc': base_c['inc'] + 2.5 * math.sin(4 * math.pi * ph),
                'cuello': base_c['cuello'] - 3.0 * math.sin(4 * math.pi * ph + 1.0),
                'cabeza': base_c['cabeza'] + 3.0 * math.sin(4 * math.pi * ph + 1.6),
                'abre': base_c['abre'] + 5.0 * math.sin(4 * math.pi * ph),
                'cola1': base_c['cola1'] - 3.0 * math.sin(4 * math.pi * ph + 0.8),
                'brazo_i': base_c['brazo'] + 12 * math.sin(2 * math.pi * ph + math.pi),
                'brazo_d': base_c['brazo'] + 12 * math.sin(2 * math.pi * ph)}
    ciclo_tyrannok(c, 0.72, 16, base_c, 26.0, 32.0, cuerpo_correr)
    c.rot('cola', _onda(0.72, 16, 6.0, fase=0.25))
    c.rot('cola2', _onda(0.72, 16, 9.0, fase=0.12))
    c.rot('cuerpo', _onda(0.72, 16, 3.0, fase=0.25, eje=2))

    # ---- ataque: el mordisco ----
    at = m.anim('ataque', 0.85)
    prep = dict(inc=-27.0, cuello=-26.0, cabeza=-8.0, abre=26.0, cola1=-12.0, cola2=-4.0, muslo=34.0,
                espinilla=-40.0, metatarso=46.0, brazo=26.0, antebrazo=86.0, mano=60.0)
    # La postura de 5:29:42.67 (la referencia principal), buscada con util/postura.py, cada lado por su cuenta (iou
    # 0.87 con fov 55): agachado, la cabeza baja con la boca abierta, la mano derecha (la de cerca en la foto) en el
    # suelo y el brazo izquierdo recogido hacia atrás. La boca, a 30° (la búsqueda daba 20°, pero al lado de la foto se
    # ve más abierta).
    pico = dict(inc=-26.4, cuello=10.6, cabeza=16.7, abre=30.0, cola1=-4.8, cola2=-4.8, muslo=60.2, espinilla=-70.0,
                metatarso=45.1, brazo=-11.2, antebrazo=51.0, mano=51.8,
                brazo_i=-39.2, antebrazo_i=99.0, mano_i=86.5, brazo_d=-10.2, antebrazo_d=51.0, mano_d=51.8,
                muslo_d=68.1, metatarso_d=40.1, metatarso_i=46.8)
    cierre = dict(pico, abre=2.0, cabeza=22.0, cuello=10.0)
    claves_pose_tyrannok(at, [(0.0, {}), (0.18, prep), (0.34, pico), (0.46, cierre), (0.6, dict(cierre, abre=6.0)),
                              (0.85, {})], fijar_z=True, sub=2)

    # ---- especial: el rugido ----
    e = m.anim('especial', 2.6)
    arriba = RUGIDO_TYRANNOK
    claves_pose_tyrannok(e, [(0.0, {}), (0.22, dict(inc=-30.0, cuello=-28.0, cabeza=-4.0, abre=14.0, muslo=24.0,
                                                    espinilla=-30.0, metatarso=44.0)),
                             (0.55, arriba), (1.95, arriba), (2.6, {})], fijar_z=True, sub=2)
    temblor = [(0.0, 0, 0, 0), (0.55, 0, 0, 0)]
    t, k = 0.55, 0
    while t < 1.8:
        t = round(t + 0.1, 3)
        temblor.append((t, (2.5 if k % 2 == 0 else -2.5), (3.0 if k % 2 == 0 else -3.0), 0))
        k += 1
    temblor += [(1.95, 0, 0, 0), (2.6, 0, 0, 0)]
    e.rot('cabeza', temblor)
    for lado, ld in ((1, 'i'), (-1, 'd')):
        for parte, (gy, gz) in BRAZO_RUGIDO_TYRANNOK.items():
            e.rot(f'{parte}_{ld}', [(0.0, 0, 0, 0), (0.22, 0, lado * gy * 0.35, lado * gz * 0.35),
                                    (0.55, 0, lado * gy, lado * gz), (1.95, 0, lado * gy, lado * gz), (2.6, 0, 0, 0)])
        e.rot(f'pierna_{ld}', [(0.0, 0, 0, 0), (0.55, 0, 0, lado * 9), (1.95, 0, 0, lado * 9), (2.6, 0, 0, 0)])
        e.rot(f'cana_{ld}', [(0.0, 0, 0, 0), (0.55, 0, 0, -lado * 9), (1.95, 0, 0, -lado * 9), (2.6, 0, 0, 0)])

    # ---- muerte: se tambalea echándose atrás, se le doblan las patas y cae de lado (sobre la derecha) ----
    d = m.anim('muerte', 1.5)
    tambalea = dict(inc=-32.0, cuello=-34.0, cabeza=-10.0, abre=34.0, muslo=34.0, espinilla=-46.0, metatarso=46.0,
                    brazo=28.0, antebrazo=84.0)
    caida = dict(inc=-10.0, cuello=6.0, cabeza=14.0, abre=28.0, cola1=-6.0, cola2=-2.0, muslo=66.0, espinilla=-30.0,
                 metatarso=70.0, brazo=44.0, antebrazo=96.0, mano=110.0)
    claves_pose_tyrannok(d, [(0.0, {}), (0.35, tambalea), (1.05, caida), (1.5, caida)], sub=1)
    d.rot('cuerpo', [(0.0, 0, 0, 0), (0.35, 0, 0, -5), (0.8, 0, 0, 40), (1.05, 0, 0, 90), (1.2, 0, 0, 84),
                     (1.5, 0, 0, 87)])
    d.rot('cola', [(0.0, 0, 0, 0), (0.6, 0, -10, 0), (1.05, 0, 12, 0), (1.5, 0, 10, 0)])
    al_suelo_tyrannok(m, d, 15)

    # ---- aparece: sale agachado y se levanta rugiendo ----
    ap = m.anim('aparece', 1.8)
    agachado = dict(inc=-8.0, cuello=10.0, cabeza=14.0, abre=4.0, muslo=60.0, espinilla=-66.0, metatarso=34.0,
                    brazo=34.0, antebrazo=88.0, mano=104.0)
    ruge = dict(inc=-34.0, cuello=-40.0, cabeza=-16.0, abre=40.0, muslo=20.0, espinilla=-28.0)
    claves_pose_tyrannok(ap, [(0.0, agachado), (0.5, agachado), (1.0, ruge), (1.4, ruge), (1.8, {})], fijar_z=True,
                         sub=2)

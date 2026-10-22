"""La Zarinosa Espigüeya (DEDsafío Minecraft 4, cuevas del Centro de Quiu): el lagarto verde que va en manada, se te
sube a la cabeza, te ciega y te drena la vida (solo te la quita otro jugador).

Copia fiel del juego (directo de elded del 26-09, Dungeon de Qumara, 4:36:40.32 y 4:47:24.10, y el icono del libro):
  - un cuadrúpedo LARGO y BAJO de cajas rectas: el tronco, una caja de 24 x 10 x 10 con las aristas vivas, sobre cuatro
    patas cortas de dos tramos, acodadas y abiertas: el de arriba, largo y grueso, sale del costado y baja casi tumbado
    hacia delante y hacia fuera; el de abajo, corto, baja al pie, una placa crema de 3 dedos gruesos apoyada plana;
  - la cabeza, una caja larga y lisa (12 de largo) verde lima, más clara que el cuerpo, que sale de la cara delantera
    del tronco 1,5 px por debajo del lomo, sin cuello; la mandíbula en los 2 px de abajo (se abre mucho para morder, roja
    por dentro), los dientecitos verdes que cuelgan del borde de abajo, el ojo de 2 x 1 (rojo oscuro delante, negro
    detrás), la «Y» de color carbón en la punta del hocico y la corona de 5 placas de hueso en la nuca;
  - el lomo con su dibujo propio: la raya central verde oscuro y los chevrones amarillos en espejo; los costados, con
    rayos amarillos en zigzag (limón y dorado) que bajan hacia atrás; la panza lisa, verde medio-oscuro;
  - 8 púas cortas de gris cálido en forma de bota, al tresbolillo en tres filas, y 1 en la nuca;
  - la cola en «espiga»: un tramo grueso que sale recto hacia atrás por abajo de la grupa, un tramo anillado que se dobla
    hacia arriba y un tallo fino con dos pares de barbas planas de hueso en forma de rayo (el de arriba, la horquilla en V).

Animaciones: reposo (respira y mira a tirones, como el diablo espinoso), andar y correr (las diagonales a la vez:
cada pata se levanta mientras avanza; el tronco ondula y la cola le sigue), ataque (echa la cabeza atrás y muerde con
la boca muy abierta), especial (se alza sobre las patas de atrás con la panza a la vista y salta a la cabeza), estado1
(agarrada a la cabeza de un jugador, como en el clip de Cracksterss: el origen, encima de su cabeza; tumbada de través
sobre el casco, la cabeza levantada y la cola enroscada en anillo; supone que el juego le da la orientación del
jugador), muerte (se vuelca panza arriba y patalea) y aparece (sale de una grieta del suelo).

Tamaño: 1 bloque hasta el lomo, ~1,4 hasta la punta de la espiga y ~2,9 del hocico al final del tramo grueso de la cola
(medido con el casco de diamante del clip y con la textura del lomo). Todas las cajas miden múltiplos de medio píxel
(si no, la textura queda a medio píxel y por las juntas asoma lo de dentro).
"""
import math

import numpy as np

import bestiario as B
from bestiario import T
from bestiario_fantasmas_v2 import a_tam

ID = 'zarinosa'
TAM = 1.0
FINO_ZARINOSA = 0.5
# El huevo: los tres verdes de la piel, el amarillo del contorno y sus señas (dos púas, un rayo amarillo, el ojo rojo
# y negro y los pies crema), como los de bestiario_reptiles.EN_JUEGO (se pasan a R._puntos).
HUEVO = (('7ccc49', '66b232', '4d7f30'), ('f8e838', 'b79c06'),
         [((6, 3), 'adae94'), ((9, 3), 'adae94'), ((5, 6), 'f8e838'), ((6, 7), 'e2be12'), ((7, 6), 'f8e838'),
          ((8, 7), 'e2be12'), ((9, 6), 'f8e838'), ((10, 7), 'e2be12'), ((9, 9), '140f0a'), ((10, 9), '6d1117'),
          ((6, 12), 'd0c085'), ((9, 12), 'd0c085')])


def _hx_zarinosa(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ======================================================================================================================
#  La paleta (paleta.json): los colores de las caras que miran arriba, los de la textura de verdad. Las púas, las barbas
#  y la «Y» solo se midieron en caras de lado (con la sombra del juego, x0,7-0,75): su textura es más clara.
# ======================================================================================================================
COLORES_ZARINOSA = {
    # El lomo y los costados
    'L': '7ccc49',   # verde claro (bordes)
    'G': '66b232',   # verde medio (base)
    'g': '4d7f30',   # verde oscuro (raya central, manchas)
    'Y': 'f8e838',   # amarillo limón
    'O': 'e2be12',   # dorado
    'o': 'b79c06',   # dorado oscuro
    'P': '4a7a2c',   # la panza
    # La cabeza
    'C': '6ac539',   # lima
    'c': '83e151',   # lima claro
    'k': '65ad46',   # lima oscuro
    'E': '6d1117',   # el ojo, rojo oscuro
    'N': '140f0a',   # el ojo, negro
    'R': '4f0612',   # la boca por dentro
    # La «Y» del hocico (carbón)
    'H': '48423c', 'h': '5e5a4a', 'x': '332f2b',
    # Las púas (gris cálido claro)
    'S': 'd6d7c0', 's': 'e6e7d4', 'z': 'aeb19c',
    # Las barbas de la cola y la corona de la nuca (hueso caqui)
    'B': 'cfc39e', 'b': 'ddd3b4', 'q': 'b3a683',
    # La corona de la nuca: el mismo hueso, algo más pardo (en el juego sale casi siempre en sombra, #585332)
    'K': '8f8160', 'j': 'a29472', 'J': '74684a',
    # Los pies
    'F': 'd0c085', 'f': 'ebd6a0', 'v': 'b9a358',
    # El tallo de la cola
    'T': '548f2d', 'A': 'c8a405',
}


def pintor_mapa_zarinosa(nombre, mapas, fino=False, espejo_der=True):
    """Un pintor que pinta cada cara con su mapa de letras (los colores de COLORES_ZARINOSA; '.' o una letra que no
    está, vacío). mapas: {cara: lista de cadenas, o fn(tw, th, cara, semilla) -> lista}; con la clave '*', el de las
    caras que no se nombran. En los costados, la columna 0 es la de atrás; con espejo_der, la cara de la derecha va en
    espejo (lo de delante sigue delante en los dos lados)."""
    cols = {k: np.array(_hx_zarinosa(v), np.uint8) for k, v in COLORES_ZARINOSA.items()}

    def fn(tw, th, c, s):
        mp = mapas.get(c, mapas.get('*'))
        tex = np.zeros((th, tw, 4), np.uint8)
        if mp is None:
            return tex, None
        if callable(mp):
            mp = mp(tw, th, c, s)
        a = a_tam(mp, th, tw)
        if c == 'der' and espejo_der:
            a = a[:, ::-1]
        for letra, col in cols.items():
            sel = a == letra
            if sel.any():
                tex[sel, :3] = col
                tex[sel, 3] = 255
        return tex, None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO_ZARINOSA) if fino else p


def liso_zarinosa(letra):
    return lambda tw, th, c, s: [letra * tw] * th


def _azar_zarinosa(x, y, s):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(s) * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


# ======================================================================================================================
#  Las texturas de la piel
# ======================================================================================================================
# El lomo, píxel a píxel (ficha, sección 5; 4:47:25.77): 10 de ancho; la fila 0, la de delante. Cada chevrón amarillo
# apunta a la raya central verde oscuro; se repite cada 8 filas (tres veces en los 24 del lomo). Mirado desde la cabeza
# (4:36:41.75), lo primero es verde liso y luego asoman las barras doradas y los corchetes.
MOTIVO_LOMO_ZARINOSA = [
    'GGGGGGGGGG',   # 7
    'OggGGGGggO',   # 8
    'OOOGLLGOOO',   # 1
    'YGOOGGOOGY',   # 2
    'LGGYGGYGGL',   # 3
    'LGGYggYGGL',   # 4
    'LLYYggYYLL',   # 5
    'GOOGGGGOOG',   # 6
]
MOTIVO_LOMO_B_ZARINOSA = [
    'GGGGLLGGGG',   # 7 (con la luz del centro)
    'OggGGGGggO',   # 8
    'YYGGLLGGYY',   # 9
    'GYOOGGOOYG',   # 10
    'LGGYGGYGGL',
    'LGGYggYGGL',
    'LLYYggYYLL',
    'GOOGGGGOOG',
]
LOMO_ZARINOSA = MOTIVO_LOMO_ZARINOSA + MOTIVO_LOMO_B_ZARINOSA + MOTIVO_LOMO_ZARINOSA


def lomo_zarinosa(tw, th, c, s):
    return LOMO_ZARINOSA


# Los rayos de los costados (4:36:37.15 de muy cerca y 4:36:40.32): cada rayo es una banda continua de 1 px que baja
# en escalera hacia atrás (tramos de 3 que bajan una fila cada 2 px, con algún quiebro hacia delante: el zigzag del
# rayo), de un solo color (dorado o limón, alternos de un rayo al siguiente), con su sombra verde oscuro debajo; uno
# cada ~7 px a lo largo. Entre medias, verde medio, alguna celda clara arriba y alguna mancha oscura abajo.
def rayos_zarinosa(tw, th, c, s, paso=7, tramo=2, avance=2, quiebro=4, desde=0, semilla=0):
    """Los rayos a tw x th. En la cara, la columna 0 es la de atrás y la fila 0, la de arriba: se dibujan de delante
    (columna 0 del dibujo) hacia atrás y se dan la vuelta."""
    g = [['G'] * tw for _ in range(th)]
    for y in range(min(3, th)):
        for x in range(tw):
            if _azar_zarinosa(x, y, semilla + 1) > 0.9:
                g[y][x] = 'L'
    for y in range(th // 2, th):
        for x in range(0, tw - 1, 2):
            if _azar_zarinosa(x, y, semilla + 2) < 0.12:
                g[y][x] = g[y][x + 1] = 'g'
    n = 0
    for x0 in range(desde - th * avance - paso, tw + paso, paso):
        col = 'O' if (n + semilla) % 2 == 0 else 'Y'
        x = x0
        for y in range(th):
            for k in range(tramo):
                if 0 <= x + k < tw:
                    g[y][x + k] = col
            if y + 1 < th:
                for k in range(avance):
                    if 0 <= x + k < tw and g[y + 1][x + k] not in 'YO':
                        g[y + 1][x + k] = 'g'
            x += -1 if (y + n) % quiebro == quiebro - 1 else avance
        n += 1
    return [''.join(f[::-1]) for f in g]


def rayos_pata_zarinosa(tw, th, c, s):
    """Las patas (4:36:40.32): los mismos rayos, más cortos y separados (tramos de 2), sobre el verde; las caras de
    arriba y de abajo, verdes con manchas oscuras."""
    if c in ('arriba', 'abajo'):
        return [''.join('g' if _azar_zarinosa(x // 2, y, s + 3) < 0.25 else 'G' for x in range(tw)) for y in range(th)]
    return rayos_zarinosa(tw, th, c, s, paso=6, tramo=2, avance=1, quiebro=3, desde=s % 4, semilla=s % 2)


def bandas_cola_zarinosa(tw, th, c, s):
    """El tramo grueso de la cola: los verdes con bandas amarillas que lo cruzan cada ~4 px, en zigzag (como las del
    tronco, pero de través)."""
    if c in ('frente', 'atras'):
        return rayos_zarinosa(tw, th, c, s, paso=5, tramo=2, avance=1, quiebro=3)
    if c == 'arriba':
        # Por encima (4:47:27.77, desde atrás), los corchetes amarillos del lomo en estrecho: a cada lado, una barra
        # que se cierra hacia el centro, con el centro verde claro; cada 5 filas.
        motivo = ['YGGY', 'YLLY', 'OYYO', 'GGGG', 'GggG']
        return [motivo[(y + 1) % 5] if tw == 4 else ('G' * tw) for y in range(th)]
    g = [['G'] * tw for _ in range(th)]
    for y in range(th):
        for x in range(0, tw - 1, 2):
            if _azar_zarinosa(x, y, s + 5) < 0.22:
                g[y][x] = g[y][x + 1] = 'g'
    # bandas de través: cada 4 a lo largo, un escalón de 1 a media altura
    largo = tw if c in ('izq', 'der') else th
    ancho = th if c in ('izq', 'der') else tw
    for k0 in range(1, largo, 4):
        col = 'Y' if (k0 // 4) % 2 == 0 else 'O'
        for j in range(ancho):
            kk = k0 + (1 if j >= ancho // 2 else 0)
            for dk in (0, 1):
                q = kk + dk
                if 0 <= q < largo:
                    if c in ('izq', 'der'):
                        g[j][q] = col
                    else:
                        g[q][j] = col
    return [''.join(f) for f in g]


def anillos_zarinosa(tw, th, c, s):
    """El tramo anillado y el tallo: anillos de 1-2 px, verde y amarillo oliva."""
    return [('A' if y % 3 == 1 else 'T') * tw for y in range(th)]


def tallo_zarinosa(tw, th, c, s):
    """El tallo fino: verde, con algún anillo amarillo abajo."""
    return [('A' if (y % 4 == 3 and y > th // 2) else 'T') * tw for y in range(th)]


def mosaico_cabeza_zarinosa(tw, th, c, s, claro=0.22, oscuro=0.2):
    """La cabeza (4:47:24.10, congelado): lima liso con celdas sueltas, en parejas a lo largo. Arriba, los dos cantos
    más claros y en medio alguna pareja más oscura; en los lados, la fila de arriba más clara y las de abajo con alguna
    pareja oscura. 'claro' y 'oscuro', cuántas (la mandíbula, más oscura)."""
    g = [['C'] * tw for _ in range(th)]
    for y in range(th):
        for x in range(tw):
            a = _azar_zarinosa(x // 2 + (y % 2), y, s * 5 + 3)
            if c == 'arriba':
                canto = x in (0, tw - 1)
                if canto:
                    g[y][x] = 'c' if a > 0.2 else 'C'
                elif a < oscuro:
                    g[y][x] = 'k'
                elif a > 1 - claro * 0.6:
                    g[y][x] = 'c'
            else:
                arriba_ = y == 0 and c != 'abajo'
                if arriba_:
                    g[y][x] = 'c' if a > 0.45 else 'C'
                elif a < oscuro:
                    g[y][x] = 'k'
                elif a > 1 - claro * 0.5:
                    g[y][x] = 'c'
    return [''.join(f) for f in g]


def cabeza_zarinosa(ojo_desde_atras, ojo_fila):
    """El pintor de la mandíbula de arriba: el mosaico lima y, en los dos costados, el ojo de 2 x 1 (rojo delante,
    negro detrás) a 'ojo_desde_atras' px de la cara de atrás y en la fila 'ojo_fila' (desde arriba); por debajo, la
    boca por dentro (rojo oscuro)."""
    def lado(tw, th, c, s):
        g = [list(f) for f in mosaico_cabeza_zarinosa(tw, th, c, s)]
        x = ojo_desde_atras
        for xx, letra in ((x, 'N'), (x + 1, 'E')):
            g[ojo_fila][xx] = letra
        for xx in (x - 1, x + 2):                      # sin marco: que no le toque una celda clara
            if 0 <= xx < tw and g[ojo_fila][xx] == 'c':
                g[ojo_fila][xx] = 'C'
        return [''.join(f) for f in g]
    # (la cara de abajo, verde oscuro: con la boca cerrada no debe asomar rojo por la junta)
    return pintor_mapa_zarinosa('cabeza_zarinosa', {'izq': lado, 'der': lado, 'abajo': liso_zarinosa('k'),
                                                    '*': mosaico_cabeza_zarinosa})


def mandibula_zarinosa():
    def arriba(tw, th, c, s):
        # la boca por dentro, con la comisura negra al fondo (la última fila, la de atrás)
        return ['R' * tw] * (th - 1) + ['N' * tw]

    def lado(tw, th, c, s):
        return mosaico_cabeza_zarinosa(tw, th, c, s, claro=0.12, oscuro=0.32)
    return pintor_mapa_zarinosa('mandibula_zarinosa', {'arriba': arriba, '*': lado})


def flecos_zarinosa(tw, th, c, s):
    """La 2.ª capa del borde de abajo de la cabeza (a 32 por bloque): los dientecitos verdes de 1 px de ancho y de 1 a
    2 de largo que cuelgan del canto, separados 1-2 px, irregulares (4:47:24.10); delante, los dos dientes verde claro
    que asoman bajo el tallo de la «Y» (4:36:40.25-40.38). Lo demás, vacío; la fila de arriba es el canto."""
    g = [['.'] * tw for _ in range(th)]
    if c == 'frente':
        for x0 in (tw // 2 - 3, tw // 2 + 1):
            for y in range(min(th, 4)):
                for dx in (0, 1):
                    g[y][x0 + dx] = 'c' if y < 3 else 'C'
        return [''.join(f) for f in g]
    x = 1
    k = 0
    largos = (2, 4, 3, 2, 4, 2, 3, 4, 2)
    huecos = (2, 2, 3, 2, 2, 4, 2)
    while x < tw - 1:
        largo = min(th, largos[(k + s) % len(largos)])
        for y in range(largo):
            for dx in (0, 1):
                if x + dx < tw:
                    g[y][x + dx] = 'C' if y < largo - 1 or dx == 0 else 'k'
        x += 2 + huecos[(k + s) % len(huecos)]
        k += 1
    return [''.join(f) for f in g]


# Las púas del lomo (4:47:27.02 y 4:47:24.10, nítidos): una «L» fina de gris cálido claro, de 2,5 x 3 px: el asta de
# 1 px delante, que sube recta, y abajo el pie de 1 px que se alarga hacia atrás. A 32 por bloque (5 x 6); la columna
# 0, detrás (la lámina mira a -X); la fila de abajo, la raíz.
PUA_ZARINOSA = [
    '...ss',
    '...sS',
    '...sS',
    '...sz',
    'ssSSz',
    'zzSzz',
]
# La de la nuca (4:47:24.10, la de la boca abierta): más alta (4 px), en rayo: el asta con un quiebro a media altura.
PUA_NUCA_ZARINOSA = [
    '..ss.',
    '..sS.',
    '..sz.',
    '.sSz.',
    'sSz..',
    'sSz..',
    'ssSSz',
    'zzSzz',
]

# Las barbas de la cola (al píxel fino, cada escalón de 2 x 2): rayos de hueso de 2-3 escalones, de la raíz (abajo, en
# el tallo) a la punta (arriba); la columna 0, delante. Se echan hacia delante o hacia atrás con su giro.
BARBAS_ZARINOSA = {
    # La de la horquilla: 3 x 5 px.
    'v': [
        '...bb',
        '..bBq',
        '..bB.',
        '.bBq.',
        'bBBq.',
        '.bBB.',
        '..bBq',
        '.bBq.',
        '.bB..',
        'bBq..',
    ],
    # La grande de en medio: 4 x 5 px.
    'm': [
        '.....bb.',
        '....bBBq',
        '...bBBq.',
        '..bBBq..',
        '.bBBBBq.',
        '...bBBq.',
        '..bBBq..',
        '.bBBq...',
        '.bBq....',
        'bBq.....',
    ],
    # La pequeña de en medio: 2 x 3 px.
    'p': [
        '..bb',
        '.bBq',
        'bBq.',
        '.bBq',
        '.bBq',
        'bBq.',
    ],
}


# ======================================================================================================================
#  Las piezas
# ======================================================================================================================
def caja_zarinosa(m, parte, x0, x1, y0, y1, z0, z1, pint, caras=None):
    """Una caja recta de esquina a esquina (en el boceto)."""
    m.caja(parte, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), pint, caras=caras)


def viga_zarinosa(m, parte, a, b, grueso, pint, extra=0.0):
    """Una viga de a a b (como Modelo.viga), con el largo redondeado hacia arriba a medio píxel: con medidas que no
    son múltiplos de 0,5 px, la textura (a 2 píxeles por píxel del boceto) queda a medio píxel y el canto de la cara
    coge el margen vacío o la cara de al lado (y por la rendija asoma lo de dentro)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    largo = float(np.linalg.norm(b - a)) + extra
    extra += math.ceil(largo * 2 - 1e-6) / 2 - largo
    m.viga(parte, a, b, grueso, pint, extra=extra)


def lamina_zarinosa(m, parte, M, ancho, alto, pint, x0=None):
    """Una lámina de una sola cara en el plano XY del marco M, que sube desde su origen."""
    xa = -ancho / 2 if x0 is None else x0
    m._caja(parte, M, xa, 0.0, 0.0, ancho, alto, 0.0, None, {c: (pint if c == 'frente' else None) for c in B.CARAS})


def sagital_zarinosa(x, y, z, inclina=0.0):
    """El marco de una lámina de perfil (en el plano YZ) en (x, y, z), con la cara hacia -X (la que el juego alumbra
    mejor en este render) y echada 'inclina' grados hacia atrás (la punta hacia -Z). La columna 0 de su mapa queda
    detrás."""
    return T(x, y, z) @ B.girar((0, -90, 0)) @ B.girar((0, 0, inclina))


def pata_zarinosa(m, lado, ld, delante, piel, pie, dedo):
    """Una pata de dos tramos, acodada y abierta (4:36:40.32): el de arriba, largo y grueso, sale del costado y baja
    casi tumbado hacia delante y hacia fuera; el de abajo, corto, baja casi vertical al pie, una placa crema con 3 dedos
    gruesos que apunta adelante."""
    # Medidas en el crudo de 4:36:40.32 con el tronco de regla (12,2 px por celda): el tramo de arriba, corto (~6 px)
    # y a ~35-40° de la vertical, hacia delante y hacia fuera; el de abajo, casi vertical (15-25°). El pie de delante
    # queda bajo el frente del tronco (z ~10) y el de atrás bajo su mitad (z ~ -1).
    if delante:
        nom, grueso, g2 = ('brazo', 'antebrazo'), 4.5, 3.5
        hombro, raiz, codo, tobillo = (5.0, 9.6, 6.5), (6.2, 10.0, 5.8), (7.6, 6.0, 9.6), (7.9, 1.0, 10.4)
    else:
        nom, grueso, g2 = ('muslo', 'pierna'), 5.0, 4.0
        hombro, raiz, codo, tobillo = (5.0, 9.8, -7.5), (6.4, 10.2, -8.2), (7.8, 5.0, -3.4), (8.0, 1.0, -1.6)
    hombro, raiz, codo, tobillo = (np.array((lado * p[0], p[1], p[2])) for p in (hombro, raiz, codo, tobillo))
    p1 = m.parte(f'{nom[0]}_{ld}', 'cuerpo', tuple(hombro))
    viga_zarinosa(m, p1, raiz, codo, grueso, piel, extra=1.6)
    p2 = m.parte(f'{nom[1]}_{ld}', p1, tuple(codo))
    viga_zarinosa(m, p2, codo + np.array((0, 0.8, -0.2)), tobillo, g2, piel, extra=0.4)
    # El pie: la palma y los tres dedos, apoyados planos, apuntando adelante.
    px, pz = tobillo[0], tobillo[2]
    caja_zarinosa(m, p2, px - 2.0, px + 2.0, 0.0, 1.0, pz - 1.6, pz + 1.4, pie)
    for dx, largo in ((-1.5, 2.5), (0.0, 3.0), (1.5, 2.5)):
        caja_zarinosa(m, p2, px + dx - 0.5, px + dx + 0.5, 0.0, 1.0, pz + 1.4, pz + 1.4 + largo, dedo)
    return p1, p2


def construir():
    m = B.Modelo(ID, K=2, ancho=128)
    m.escala = 1.0

    # Los pintores
    piel_cuerpo = pintor_mapa_zarinosa('cuerpo_zarinosa', {
        'arriba': lomo_zarinosa, 'izq': rayos_zarinosa, 'der': rayos_zarinosa,
        'frente': lambda tw, th, c, s: rayos_zarinosa(tw, th, c, s, paso=6, desde=2, semilla=1),
        'atras': lambda tw, th, c, s: rayos_zarinosa(tw, th, c, s, paso=6, desde=1, semilla=2),
        'abajo': liso_zarinosa('P')})
    piel_pata = pintor_mapa_zarinosa('pata_zarinosa', {'*': rayos_pata_zarinosa})
    piel_cola = pintor_mapa_zarinosa('cola_zarinosa', {'*': bandas_cola_zarinosa, 'abajo': liso_zarinosa('P')})
    anillos = pintor_mapa_zarinosa('anillos_zarinosa', {'*': anillos_zarinosa})
    tallo = pintor_mapa_zarinosa('tallo_zarinosa', {'*': tallo_zarinosa})
    pie = pintor_mapa_zarinosa('pie_zarinosa', {'*': liso_zarinosa('F'), 'arriba': liso_zarinosa('f'),
                                                'abajo': liso_zarinosa('v')})
    dedo = pintor_mapa_zarinosa('dedo_zarinosa', {
        '*': lambda tw, th, c, s: ['v' * (tw - 1) + 'f'] * th,
        'frente': liso_zarinosa('f'),
        'arriba': lambda tw, th, c, s: ['f' * tw] * 1 + ['F' * tw] * (th - 1)})
    cabeza_p = cabeza_zarinosa(ojo_desde_atras=2, ojo_fila=2)
    mand_p = mandibula_zarinosa()
    flecos = pintor_mapa_zarinosa('flecos_zarinosa', {'izq': flecos_zarinosa, 'der': flecos_zarinosa,
                                                      'frente': flecos_zarinosa}, fino=True)
    carbon = pintor_mapa_zarinosa('horquilla_zarinosa', {
        '*': liso_zarinosa('H'), 'frente': lambda tw, th, c, s: ['h' + 'H' * (tw - 1)] * th,
        'arriba': liso_zarinosa('h'), 'abajo': liso_zarinosa('x')})
    hueso = pintor_mapa_zarinosa('corona_zarinosa', {'*': liso_zarinosa('K'), 'arriba': liso_zarinosa('j'),
                                                     'abajo': liso_zarinosa('J')})
    pua = pintor_mapa_zarinosa('pua_zarinosa', {'frente': PUA_ZARINOSA}, fino=True)
    pua_nuca = pintor_mapa_zarinosa('pua_nuca_zarinosa', {'frente': PUA_NUCA_ZARINOSA}, fino=True)
    barbas = {k: pintor_mapa_zarinosa('barba_zarinosa_' + k, {'frente': v}, fino=True)
              for k, v in BARBAS_ZARINOSA.items()}
    # (en el dibujo, la columna 0 queda detrás: las barbas que se echan hacia atrás van en espejo)
    barbas['w'] = pintor_mapa_zarinosa('barba_zarinosa_w', {'frente': [f[::-1] for f in BARBAS_ZARINOSA['v']]},
                                       fino=True)
    barbas['q'] = pintor_mapa_zarinosa('barba_zarinosa_q', {'frente': [f[::-1] for f in BARBAS_ZARINOSA['p']]},
                                       fino=True)

    # El tronco: la caja de 24 x 10 x 10, de aristas vivas (la panza a 5,5 px del suelo).
    m.parte('cuerpo', None, (0, 10.5, 0))
    caja_zarinosa(m, 'cuerpo', -5, 5, 5.5, 15.5, -12, 12, piel_cuerpo)
    # Las púas: tres filas al tresbolillo (3, 2 y 3) y la de la nuca.
    # (la fila de la derecha, 1 px más adelante que la de la izquierda, y la del centro más baja: de lado no se ven
    # alineadas como una valla, como en 4:36:40.32)
    for x, zs, alto in ((-3.5, (8.2, 1.0, -6.2), 3.0), (0.0, (3.6, -3.6), 2.5), (3.5, (7.2, 0.0, -7.2), 3.0)):
        for z in zs:
            lamina_zarinosa(m, 'cuerpo', sagital_zarinosa(x, 15.5, z, inclina=6), 2.5, alto, pua)
    lamina_zarinosa(m, 'cuerpo', sagital_zarinosa(0.0, 15.5, 11.0, inclina=8), 2.5, 3.0, pua_nuca)

    # La cabeza: una caja larga y lisa, sin escalón de hocico, 1,5 px por debajo del lomo; la mandíbula, los 2 px de
    # abajo, y los dientecitos colgando de su borde.
    # (4:47:24.10, congelado: 3 filas de mandíbula de arriba con el ojo en la de abajo, 1 de mandíbula y debajo los
    # dientecitos, irregulares, de 1-2 px)
    m.parte('cabeza', 'cuerpo', (0, 10.5, 12.0))
    caja_zarinosa(m, 'cabeza', -4, 4, 10.5, 13.5, 11.5, 24, cabeza_p)
    m.parte('mandibula', 'cabeza', (0, 10.5, 13.0))
    caja_zarinosa(m, 'mandibula', -4, 4, 9.5, 10.5, 12, 24, mand_p)
    caja_zarinosa(m, 'mandibula', -4.25, 4.25, 7.5, 9.5, 12.25, 24.25, flecos,
                  caras={c: (flecos if c in ('izq', 'der', 'frente') else None) for c in B.CARAS})
    # La «Y» del hocico (4:36:40.25-40.38 y 4:47:24.10, medida con rejilla): dos puntas de 1,5 px que suben ~2,5 px
    # sobre el hocico, separadas 1 px, que se juntan y bajan en un tallo por delante de la cara hasta la boca (5,5 px
    # en total); de cajas finas de 1 px, mirando al frente y echada ~12° hacia atrás (las puntas hacia la cabeza).
    My = T(0, 13.5, 24.4) @ B.girar((-12, 0, 0))
    for x0, x1, y0, y1 in ((-2.0, -0.5, 0.5, 3.0), (0.5, 2.0, 0.5, 3.0), (-2.0, 2.0, -0.75, 0.75),
                           (-0.75, 0.75, -2.5, -0.5)):
        m._caja('cabeza', My, x0, y0, -0.5, x1 - x0, y1 - y0, 1.0, carbon)
    # La corona de la nuca: 5 placas pequeñas de hueso pardo de 1 x 1,5, echadas hacia atrás 45°, en fila sobre el
    # borde de atrás de la cabeza (de frente, 4:36:41.60, una fila de 5 dientecitos a 1,25 px; de lado y desde arriba,
    # cuadraditos pardos).
    for x in (-2.5, -1.25, 0.0, 1.25, 2.5):
        Mc = T(x, 13.2, 13.9) @ B.girar((-45, 0, 0))
        m._caja('cabeza', Mc, -0.5, 0.0, -0.5, 1.0, 1.5, 1.0, hueso)

    # Las patas.
    for delante in (True, False):
        for lado, ld in ((1, 'i'), (-1, 'd')):
            pata_zarinosa(m, lado, ld, delante, piel_pata, pie, dedo)

    # La cola: el tramo grueso, recto hacia atrás por la mitad de abajo de la grupa.
    m.parte('cola', 'cuerpo', (0, 8.5, -12.0))
    caja_zarinosa(m, 'cola', -2, 2, 6.5, 10.5, -22.5, -11.5, piel_cola)
    # El tramo anillado, que se dobla y sube casi vertical (algo echado hacia atrás): de y ~10 a ~15 (4:36:40.32, en
    # crudo: 13,75 px de pantalla por celda en la cola).
    m.parte('cola_alta', 'cola', (0, 9.6, -21.5))
    viga_zarinosa(m, 'cola_alta', (0, 9.4, -21.4), (0, 14.6, -22.6), 2.0, anillos, extra=0.6)
    # El tallo fino con las barbas: el par de en medio (y ~14-17; la de delante, grande) y, en lo alto, la horquilla en
    # V, pequeña (el cruce a y ~19,7 y las puntas a ~22).
    m.parte('espiga', 'cola_alta', (0, 14.4, -22.5))
    viga_zarinosa(m, 'espiga', (0, 14.2, -22.5), (0, 20.0, -23.9), 1.0, tallo, extra=0.3)
    lamina_zarinosa(m, 'espiga', sagital_zarinosa(0, 14.6, -22.6, inclina=-62), 4.0, 5.0, barbas['m'])
    lamina_zarinosa(m, 'espiga', sagital_zarinosa(0, 15.8, -22.9, inclina=48), 2.0, 3.0, barbas['q'])
    lamina_zarinosa(m, 'espiga', sagital_zarinosa(0, 19.5, -23.7, inclina=-34), 2.5, 3.5, barbas['v'])
    lamina_zarinosa(m, 'espiga', sagital_zarinosa(0, 19.7, -23.9, inclina=38), 2.5, 3.5, barbas['w'])

    m.mirar(('cabeza', 0.7))
    anims_zarinosa(m)
    return m


# ======================================================================================================================
#  Las animaciones (los giros, en grados en los ejes del boceto: X, la cabeza arriba (-) o abajo (+); Y, hacia su
#  izquierda (+); Z, el lado izquierdo arriba (+). Los movimientos, en píxeles)
# ======================================================================================================================
PATAS_ZARINOSA = (('brazo_i', 'antebrazo_i', 1, 0.0), ('muslo_d', 'pierna_d', -1, 0.0),
                  ('brazo_d', 'antebrazo_d', -1, 0.5), ('muslo_i', 'pierna_i', 1, 0.5))


def anims_zarinosa(m):
    reposo_zarinosa(m)
    a = m.anim('andar', 0.9, bucle=True)
    paso_zarinosa(a, 0.9, barrido=22, alza=12, codo=14, cuerpo=4.0)
    c = m.anim('correr', 0.5, bucle=True)
    paso_zarinosa(c, 0.5, barrido=30, alza=16, codo=18, cuerpo=6.0)
    c.rot('cabeza', [(0, -6, 0, 0), (0.5, -6, 0, 0)])
    ataque_zarinosa(m)
    especial_zarinosa(m)
    estado1_zarinosa(m)
    muerte_zarinosa(m)
    aparece_zarinosa(m)


def reposo_zarinosa(m):
    """Quieta como el diablo espinoso: respira, se mece adelante y atrás y mira a tirones (gira la cabeza y se queda
    así; la levanta y la gira hacia un lado, como en 4:36:40.32), y la espiga se cimbrea."""
    r = m.anim('reposo', 3.6, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.25, periodo=1.8)
    r.mov('cuerpo', [(0, 0, 0, 0), (1.6, 0, 0, 0), (1.9, 0, 0, 0.6), (2.3, 0, 0, -0.3), (2.6, 0, 0, 0), (3.6, 0, 0, 0)])
    r.rot('cabeza', [(0, 0, 0, 0), (0.25, -12, 16, 0, 0), (1.2, -12, 16, 0, 0), (1.45, 0, 0, 0, 0),
                     (2.2, 0, 0, 0, 0), (2.4, 4, -18, 0, 0), (3.2, 4, -18, 0, 0), (3.4, 0, 0, 0, 0),
                     (3.6, 0, 0, 0, 0)])
    r.rot('mandibula', [(0, 0, 0, 0), (2.5, 0, 0, 0), (2.65, 8, 0, 0), (2.8, 0, 0, 0), (3.6, 0, 0, 0)])
    r.onda('cola_alta', 'r', 0, 3, periodo=3.6)
    r.onda('espiga', 'r', 2, 5, periodo=1.8, fase=0.25)


def paso_zarinosa(a, largo, barrido=22, alza=12, codo=14, cuerpo=4.0):
    """El paso de lagarto: las diagonales a la vez (brazo izquierdo con muslo derecho). Cada pata barre alrededor del
    hombro (hacia delante, girando en Y) y, mientras va hacia delante, se levanta (el codo sube, girando en Z) y el
    tramo de abajo se adelanta; el tronco ondula de lado, y la cola le sigue."""
    for arriba, abajo, lado, fase in PATAS_ZARINOSA:
        a.onda(arriba, 'r', 1, -barrido * lado, periodo=largo, fase=fase)
        a.onda(arriba, 'r', 2, alza * lado, periodo=largo, fase=fase + 0.25, forma=lambda v: max(0.0, v))
        a.onda(abajo, 'r', 0, -codo, periodo=largo, fase=fase + 0.25, forma=lambda v: max(0.0, v))
    a.onda('cuerpo', 'r', 1, cuerpo, periodo=largo)
    a.onda('cuerpo', 'm', 1, 0.35, periodo=largo / 2)
    a.onda('cabeza', 'r', 1, -cuerpo * 0.8, periodo=largo, fase=0.05)
    a.onda('cola', 'r', 1, -cuerpo * 1.5, periodo=largo, fase=0.1)
    a.onda('cola_alta', 'r', 2, cuerpo, periodo=largo, fase=0.2)
    a.onda('espiga', 'r', 2, cuerpo * 1.2, periodo=largo, fase=0.3)


def ataque_zarinosa(m):
    """El mordisco (4:47:24.10, la de la izquierda): echa la cabeza atrás, la lanza abriendo mucho la boca (~32°) y la
    cierra de golpe; el tronco acompaña."""
    at = m.anim('ataque', 0.6)
    at.rot('cabeza', [(0, 0, 0, 0), (0.16, -16, 0, 0), (0.3, 6, 0, 0), (0.42, 4, 0, 0), (0.6, 0, 0, 0)])
    at.mov('cabeza', [(0, 0, 0, 0), (0.16, 0, 0.4, -0.8), (0.3, 0, 0, 2.2), (0.42, 0, 0, 1.6), (0.6, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.16, 34, 0, 0), (0.28, 34, 0, 0), (0.34, 0, 0, 0), (0.6, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.16, -4, 0, 0), (0.3, 3, 0, 0), (0.6, 0, 0, 0)])
    at.mov('cuerpo', [(0, 0, 0, 0), (0.16, 0, 0, -0.8), (0.3, 0, 0, 1.2), (0.6, 0, 0, 0)])
    at.rot('espiga', [(0, 0, 0, 0), (0.2, -10, 0, 0), (0.4, 6, 0, 0), (0.6, 0, 0, 0)])


# El salto a la cabeza (4:36:36.82; james_aap 4:38:33.60-34.05): se alza casi de pie sobre las patas de atrás, con la
# panza a la vista, las de delante abiertas a los lados y la cabeza estirada hacia arriba, y salta.
ALZA_ZARINOSA = -62.0


def _alzada_zarinosa(a):
    """(giro del tronco, subida, adelanto) para que, alzada 'a' grados, la cadera (y 9,8, z -9) siga en su sitio: el
    tronco gira en su centro (0, 10,5, 0)."""
    r = math.radians(a)
    y, z = 9.8 - 10.5, -9.0
    y2 = y * math.cos(r) - z * math.sin(r)
    z2 = y * math.sin(r) + z * math.cos(r)
    return a, (y - y2), (z - z2)


def especial_zarinosa(m):
    e = m.anim('especial', 1.3)
    giro, sube, adelanta = _alzada_zarinosa(ALZA_ZARINOSA)
    e.rot('cuerpo', [(0, 0, 0, 0), (0.45, giro, 0, 0), (0.85, giro, 0, 0), (1.0, giro * 0.4, 0, 0), (1.3, 0, 0, 0)])
    e.mov('cuerpo', [(0, 0, 0, 0), (0.45, 0, sube, adelanta), (0.85, 0, sube, adelanta), (1.0, 0, sube + 9, 14),
                     (1.15, 0, 4, 18), (1.3, 0, 0, 0)])
    for p in ('muslo_i', 'muslo_d'):
        e.rot(p, [(0, 0, 0, 0), (0.45, -giro, 0, 0), (0.85, -giro, 0, 0), (1.0, -giro * 0.2, 0, 0), (1.3, 0, 0, 0)])
    for p, k in (('brazo_i', 1), ('brazo_d', -1)):
        e.rot(p, [(0, 0, 0, 0), (0.45, 10, -30 * k, 50 * k), (0.85, 10, -30 * k, 50 * k), (1.0, -30, 0, 20 * k),
                  (1.3, 0, 0, 0)])
    for p in ('antebrazo_i', 'antebrazo_d'):
        e.rot(p, [(0, 0, 0, 0), (0.45, -30, 0, 0), (0.85, -30, 0, 0), (1.3, 0, 0, 0)])
    e.rot('cabeza', [(0, 0, 0, 0), (0.45, 24, 0, 0), (0.85, 20, 0, 0), (1.0, 34, 0, 0), (1.3, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.5, 20, 0, 0), (0.85, 24, 0, 0), (1.0, 0, 0, 0), (1.3, 0, 0, 0)])
    e.rot('cola', [(0, 0, 0, 0), (0.45, -giro * 0.9, 0, 0), (0.85, -giro * 0.9, 0, 0), (1.3, 0, 0, 0)])


def estado1_zarinosa(m):
    """Agarrada a la cabeza de un jugador, como en el clip de Cracksterss (0:01.73-0:02.03): el origen va encima de la
    cabeza del jugador (la cabeza, de 8 x 8 x 8, de y -8 a 0) y la Zarinosa mira hacia donde mira el jugador, así que
    la pose la gira 90°: queda tumbada de través sobre el casco, con la panza encima, la cabeza levantada hacia la
    izquierda del jugador y la cola hacia la derecha, enroscada en un anillo vertical (baja, sube y el tallo se dobla
    hacia delante, con las barbas arriba). Las cuatro patas abrazan la cabeza por las cuatro esquinas (las de la
    derecha, delante de la cara). Respira y aprieta (le drena la vida)."""
    e = m.anim('estado1', 1.2, bucle=True)
    # (de través y con el morro algo levantado, ~18°, como en el clip; la panza, justo encima del casco)
    e.rot('cuerpo', [(0, -18, 90, 0), (0.6, -16, 90, -3), (1.2, -18, 90, 0)])
    e.mov('cuerpo', [(0, 0, -4.3, 0), (0.6, 0, -3.8, 0), (1.2, 0, -4.3, 0)])
    e.rot('cabeza', [(0, -26, 0, 0), (0.6, -32, 6, 0), (1.2, -26, 0, 0)])
    e.rot('mandibula', [(0, 10, 0, 0), (0.3, 22, 0, 0), (0.6, 10, 0, 0), (1.2, 10, 0, 0)])
    for p, k in (('brazo_i', 1), ('brazo_d', -1)):
        e.rot(p, [(0, 40, 0, -20 * k), (0.6, 36, 0, -24 * k), (1.2, 40, 0, -20 * k)])
    for p in ('antebrazo_i', 'antebrazo_d'):
        e.rot(p, [(0, 10, 0, 0), (1.2, 10, 0, 0)])
    for p, k in (('muslo_i', 1), ('muslo_d', -1)):
        e.rot(p, [(0, 15, 0, -20 * k), (0.6, 12, 0, -24 * k), (1.2, 15, 0, -20 * k)])
    # (el anillo: el tramo grueso sale hacia atrás y abajo, el anillado sube por detrás y el tallo se dobla hacia
    # delante, por encima de la grupa)
    e.rot('cola', [(0, 4, 0, 0), (0.6, 8, 0, 0), (1.2, 4, 0, 0)])
    e.rot('cola_alta', [(0, -22, 0, 0), (0.6, -18, 0, 0), (1.2, -22, 0, 0)])
    e.rot('espiga', [(0, 78, 0, 0), (0.6, 72, 0, 0), (1.2, 78, 0, 0)])


def muerte_zarinosa(m):
    """Se encoge, se vuelca panza arriba y patalea antes de quedarse quieta."""
    d = m.anim('muerte', 1.4)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.2, -8, 0, -12), (0.6, 0, 0, 180), (1.4, 0, 0, 180)])
    d.mov('cuerpo', [(0, 0, 0, 0), (0.2, 0, 1.5, 0), (0.6, 0, -1.0, 0), (1.4, 0, -1.5, 0)])
    for p, k in (('brazo_i', 1), ('brazo_d', -1), ('muslo_i', 1), ('muslo_d', -1)):
        d.rot(p, [(0, 0, 0, 0), (0.6, 0, 0, -20 * k), (0.75, 20, 0, -30 * k), (0.9, -15, 0, -20 * k),
                  (1.05, 15, 0, -28 * k), (1.4, 0, 0, -24 * k)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.6, -10, 0, 0), (1.4, 12, 10, 0)])
    d.rot('mandibula', [(0, 0, 0, 0), (0.6, 22, 0, 0), (1.4, 18, 0, 0)])
    d.rot('cola_alta', [(0, 0, 0, 0), (0.6, 30, 0, 0), (1.4, 50, 0, 0)])


def aparece_zarinosa(m):
    """Sale de una grieta del suelo de la cueva: aplastada y medio enterrada, asoma la cabeza y trepa fuera."""
    ap = m.anim('aparece', 1.1)
    ap.mov('cuerpo', [(0, 0, -12, 0), (0.35, 0, -8, 0), (0.8, 0, -1.5, 0), (1.1, 0, 0, 0)])
    ap.rot('cuerpo', [(0, -35, 0, 0), (0.35, -30, 0, 0), (0.8, -6, 0, 0), (1.1, 0, 0, 0)])
    ap.rot('cabeza', [(0, 20, 0, 0), (0.35, 0, 14, 0), (0.6, 0, -12, 0), (0.85, -8, 0, 0), (1.1, 0, 0, 0)])
    for p, k in (('brazo_i', 1), ('brazo_d', -1)):
        ap.rot(p, [(0, 30, 0, 30 * k), (0.35, -20, 0, 30 * k), (0.6, 10, 0, 10 * k), (0.85, -10, 0, 0),
                   (1.1, 0, 0, 0)])
    for p in ('muslo_i', 'muslo_d'):
        ap.rot(p, [(0, 35, 0, 0), (0.6, 30, 0, 0), (0.9, 0, 0, 0), (1.1, 0, 0, 0)])
    ap.rot('cola', [(0, 40, 0, 0), (0.6, 20, 0, 0), (1.1, 0, 0, 0)])

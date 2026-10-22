"""El Narval (DEDsafío 4, familia de Quiu), rehecho pieza a pieza sobre el cartel oficial del día 3 y los directos
(ficha: quiu_ref2/narval/ficha.md). Un monstruo marino azul marino, macizo y por tramos que bajan hacia la cola:

  cabeza      una caja casi tan ancha como el cuerpo, con boca de mosasaurio abierta (dientes cuadrados de bloque, boca
              ciruela con la lengua rosa en «T»), un marco lavanda en cada costado y el ojo pequeño abajo y atrás
  cuernos     tres barras gris claro de sección cuadrada en abanico en la línea del medio: el colmillo largo hacia
              delante y un poco abajo, el medio casi recto (12°) y el corto empinado (65°), con galones grises
  tramos      el delantero, alto, con cuatro cuadros, un arco y tres puntos lavanda en cada costado; el trasero, más bajo
              y estrecho; un tallo y la aleta de la cola en dos lóbulos horizontales en V
  aletas      cuatro palas planas con la punta en escalones y una línea lavanda en zigzag, que salen a los lados
              echadas atrás (35° en reposo; al nadar reman de ~15° a ~55°)
  ganchos     tres láminas gruesas en espiral cuadrada sobre el lomo; la 1.ª, la más grande, detrás de la cabeza

construir() da el Narval solo; construir_montado(), el mismo con la silla, la cincha y la hebilla que lleva cuando lo
monta un Reptisaurio Arquero (id 'narval_jinete'; el jinete va aparte, sentado en la silla).

Al píxel de Minecraft (16 por bloque): TAM 1, las piezas ya van a su tamaño. Los dientes, a 32 por bloque (2.ª capa).
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import T

ID = 'narval'
TAM = 1.0

# ======================================================================================================================
#  Colores (quiu_ref2/narval/paleta.json: los de la textura, ya corregidos de la luz del agua)
# ======================================================================================================================
PIEL_NARVAL = np.array([B.H('0b1a38'), B.H('122257'), B.H('24367b'), B.H('344894'), B.H('123168')])   # muy osc., osc., media,
PESOS_PIEL_NARVAL = (0.07, 0.23, 0.40, 0.19, 0.11)       # clara, verdosa (medido en el primer plano, 1:11.45)
LINEA_NARVAL = B.H('a69bd4')
GANCHO_BORDE_NARVAL = B.H('8c87b6')
GANCHO_RELLENO_NARVAL = B.H('0c1838')
GANCHO_RELLENO2_NARVAL = B.H('1d2a5c')
CUERNO_NARVAL = (B.H('dcdde0'), B.H('a3a9b1'), B.H('6b717b'))                 # claro, medio, galón
ALETA_NARVAL = np.array([B.H('162654'), B.H('2f3b7d'), B.H('515d93'), B.H('24367b'), B.H('122257')])
ALETA_LINEA_NARVAL = (B.H('a399d1'), B.H('707bb6'))
BOCA_NARVAL = {'fondo': B.H('1e0c22'), 'encia': B.H('5a2458'), 'lengua': B.H('6e2a62'), 'lengua2': B.H('8a3a78')}
DIENTE_NARVAL = (B.H('dcdad2'), B.H('a8a6a0'))
OJO_NARVAL = (B.H('e6ecf2'), B.H('0a0b12'))
# La silla (quiu_ref2/narval_jinete/paleta.json): el cuero, la cincha y la hebilla.
CUERO_NARVAL = np.array([B.H('2a1e12'), B.H('36271a'), B.H('413021'), B.H('4e3a2a'), B.H('5b4534')])
CANTO_CUERO_NARVAL = B.H('6d5947')
CINCHA_NARVAL = np.array([B.H('1b150f'), B.H('271e15'), B.H('33281d')])
HEBILLA_NARVAL = np.array([B.H('4e4c50'), B.H('6f6c72'), B.H('88817e')])

# ======================================================================================================================
#  Medidas (px de Minecraft). El boceto: Y arriba, el frente en +Z, +X la izquierda del mob.
#  z = 0 es la junta de la cabeza con el tramo delantero; la panza del tramo delantero, a Y0_NARVAL.
# ======================================================================================================================
Y0_NARVAL = 6.0
CRANEO_NARVAL = (14, 9, 12)            # ancho, alto, largo
BAJA_CRANEO_NARVAL = 3                 # el techo de la cabeza, por debajo del techo del tramo delantero
MANDIBULA_NARVAL = (13, 3, 12)
GOZNE_Z_NARVAL = 0.5                   # la bisagra de la mandíbula (z; 0 = la cara de atrás del cráneo)
ABRE_BOCA_NARVAL = 24                  # grados, en reposo (el cartel)
DELANTERO_NARVAL = (15, 14, 28)
TRASERO_NARVAL = (12, 11, 18)
TRASERO_BAJA_NARVAL = 3                # su techo, por debajo del del delantero
TALLO_NARVAL = (6, 4, 5)
ALTURA_COLA_NARVAL = 0.65            # a qué altura del tramo trasero salen el tallo y la cola (0 abajo, 1 arriba)
LOBULO_NARVAL = dict(largo=22, raiz=6, punta=2, grueso=1, abre=20, cae=0, recto=0.35)
ALETA_DEL_NARVAL = dict(largo=16, raiz=8, punta=4, grueso=1, z=-9.0, atras=35, cae=4, y=0.0, gira=-16, recto=0.6)
ALETA_TRAS_NARVAL = dict(largo=11, raiz=6, punta=3, grueso=1, z=-37.0, atras=35, cae=4, y=0.0, gira=-16, recto=0.6)
COLMILLO_NARVAL = dict(largo=19, grueso=4, baja=3.5, angulo=-4)
CUERNO_MEDIO_NARVAL = dict(largo=10, grueso=4, z=10.5, angulo=12)
CUERNO_CORTO_NARVAL = dict(largo=6, grueso=4, z=7.0, angulo=65)
GANCHOS_NARVAL = ((0.0, 1), (-24.0, 2), (-40.0, 2))        # (z del poste de delante, tamaño 1 grande / 2 pequeño)
# La silla del Narval montado (ficha del jinete, 5.2): entre los ganchos 1 y 2, con el centro a ~1/3 del largo.
SILLA_NARVAL = dict(z=-15.0, largo=10, alto=1.5, faldon=6, cincha=3.5, hebilla=(5, 4.5), bajo_faldon=2.5)

# ======================================================================================================================
#  Los pintores, al píxel
# ======================================================================================================================


def _azar_narval(*claves):
    """Un generador fijo para cada combinación de claves (la textura no cambia de una vez a otra)."""
    h = 2166136261
    for c in claves:
        for ch in str(c):
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return np.random.default_rng(h)


def mosaico_narval(tw, th, semilla, colores=PIEL_NARVAL, pesos=PESOS_PIEL_NARVAL):
    """La piel del Narval: un mosaico limpio de manchas planas de 1 x 1 a 2 x 3 en cuatro azules y un azul verdoso
    (sin ruido dentro de cada mancha), como en los primeros planos del clip (1:11.45). Devuelve rgb (th, tw, 3)."""
    rng = _azar_narval('mosaico', tw, th, semilla)
    idx = -np.ones((th, tw), int)
    p = np.array(pesos, float) / sum(pesos)
    for y in range(th):
        for x in range(tw):
            if idx[y, x] >= 0:
                continue
            w = int(rng.choice((1, 2), p=(0.4, 0.6)))
            h = int(rng.choice((1, 2, 3), p=(0.35, 0.45, 0.2)))
            c = int(rng.choice(len(p), p=p))
            vecinos = {idx[y, x - 1] if x > 0 else -1, idx[y - 1, x] if y > 0 else -1}
            if c in vecinos:
                c = int(rng.choice(len(p), p=p))
            zona = idx[y:y + h, x:x + w]
            zona[zona < 0] = c
    return colores[idx].astype(float)


def _rgba_narval(rgb, alfa=None):
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = np.clip(np.round(rgb), 0, 255)
    out[..., 3] = 255 if alfa is None else alfa
    return out


def _pintor_narval(nombre, fn, fino=False):
    p = B.Pintor(nombre, lambda tw, th, c, s: (fn(c, tw, th, s), None))
    return B.fino(p, 0.5) if fino else p


def _marcar_lado_narval(rgb, celdas, color, cara):
    """Pinta las celdas (columna desde delante, fila desde arriba) en una cara de lado: en 'izq' (-X) el frente queda a
    la derecha de la textura; en 'der' (+X), a la izquierda."""
    th, tw = rgb.shape[:2]
    for c, r in celdas:
        x = (tw - 1 - c) if cara == 'izq' else c
        if 0 <= x < tw and 0 <= r < th:
            rgb[r, x] = color


# El dibujo de cada costado del tramo delantero (columna desde delante, fila desde arriba), medido en el clip (1:11.92)
# y en 1:19:45.67: cuatro cuadros de 2 x 2 cada 3 px (el 1.º, una fila más bajo) y uno de 1 x 1; debajo, el arco
# (la pata de delante bajo el 2.º cuadro, la barra hacia atrás, tres escalones y la línea a media altura hasta el borde
# de atrás) y, delante de la pata, la columna de tres puntos.
def dibujo_costado_narval(largo):
    celdas = []
    for c0, r0 in ((3, 3), (6, 2), (9, 2), (12, 2)):
        celdas += [(c0 + i, r0 + j) for i in (0, 1) for j in (0, 1)]
    celdas.append((15, 3))
    celdas += [(c, 5) for c in range(7, 17)]                 # la barra (la esquina de delante, redondeada)
    celdas += [(6, r) for r in range(6, 13)]                 # la pata
    celdas += [(17, 6), (18, 6), (19, 7)]                    # los escalones
    celdas += [(c, 8) for c in range(20, largo)]             # la línea hasta el borde de atrás
    celdas += [(3, 6), (4, 8), (3, 10)]                      # la columna de puntos (el 2.º, 1 px más atrás)
    return celdas


def costado_narval(nombre, largo):
    celdas = dibujo_costado_narval(largo)

    def fn(c, tw, th, s):
        rgb = mosaico_narval(tw, th, (nombre, c))
        if c in ('izq', 'der'):
            _marcar_lado_narval(rgb, celdas, LINEA_NARVAL, c)
        return _rgba_narval(rgb)
    return _pintor_narval(nombre, fn)


def piel_narval(nombre):
    return _pintor_narval(nombre, lambda c, tw, th, s: _rgba_narval(mosaico_narval(tw, th, (nombre, c))))


# La cabeza: el marco lavanda de cada costado (un rectángulo de 8 x 5 con las esquinas en escalón, a 1 px del techo y
# 2 px de delante) y el ojo debajo de su esquina de atrás (la pupila delante, el blanco detrás); arriba, una fila de
# cuadraditos junto al borde de atrás y una línea en escalera metida junto a cada lado; abajo, el paladar.
def cabeza_narval(nombre):
    marco = ([(c, 1) for c in range(3, 9)] + [(c, 5) for c in range(3, 9)] + [(2, r) for r in range(2, 5)] +
             [(9, r) for r in range(2, 5)])
    ojo_negro = [(8, 6)]
    ojo_blanco = [(9, 6), (10, 6)]

    def fn(c, tw, th, s):
        if c == 'abajo':
            rgb = np.zeros((th, tw, 3)) + BOCA_NARVAL['fondo']
            return _rgba_narval(rgb)
        rgb = mosaico_narval(tw, th, (nombre, c))
        if c in ('izq', 'der'):
            _marcar_lado_narval(rgb, marco, LINEA_NARVAL, c)
            _marcar_lado_narval(rgb, ojo_negro, OJO_NARVAL[1], c)
            _marcar_lado_narval(rgb, ojo_blanco, OJO_NARVAL[0], c)
        elif c == 'frente':
            # Dos manchas de 2 x 2 del azul más oscuro a los lados de la raíz del colmillo (de frente, 1:22:58.33, son azul
            # muy oscuro y no negras; en 1:22:43.95, en sombra, parecían casi negras).
            for x0 in (1, tw - 3):
                rgb[5:7, x0:x0 + 2] = PIEL_NARVAL[0]
        elif c == 'arriba':
            # fila 0: el borde de atrás; las columnas crecen hacia +X (la izquierda del mob)
            puntos = [(2, 1), (4, 1), (9, 1), (11, 1), (6, 1), (7, 1), (6, 2), (7, 2)]
            for lado in (0, 1):
                linea = [(1, 3), (1, 4), (1, 5), (2, 6), (2, 7), (3, 8), (3, 9), (4, 9)]
                for x, r in linea:
                    puntos.append((x if lado == 0 else tw - 1 - x, r))
            for x, r in puntos:
                if 0 <= x < tw and 0 <= r < th:
                    rgb[r, x] = LINEA_NARVAL
        return _rgba_narval(rgb)
    return _pintor_narval(nombre, fn)


def mandibula_narval(nombre):
    """La mandíbula: por fuera, piel; arriba, el suelo de la boca ciruela con el borde magenta y la lengua rosa en «T»
    (4 px de ancho atrás y 2 hacia delante); en los costados, la fila de arriba magenta (el labio)."""
    def fn(c, tw, th, s):
        rgb = mosaico_narval(tw, th, (nombre, c))
        if c == 'arriba':
            rgb[...] = BOCA_NARVAL['fondo']
            rgb[0, :] = rgb[-1, :] = rgb[:, 0] = rgb[:, -1] = BOCA_NARVAL['encia']
            # La lengua en «T» en medio del suelo de la boca (fila 0, la de atrás), como se ve de frente con la boca
            # abierta (1:22:58.33): desde la bisagra, 3 filas de 4 px de ancho y luego un tallo de 2 px hasta la fila 8,
            # con la luz en el centro.
            cx = tw // 2
            for r in range(1, 4):
                rgb[r, cx - 2:cx + 2] = BOCA_NARVAL['lengua']
            for r in range(4, 9):
                rgb[r, cx - 1:cx + 1] = BOCA_NARVAL['lengua']
            rgb[2:4, cx - 1:cx + 1] = BOCA_NARVAL['lengua2']
            rgb[4:7, cx - 1] = BOCA_NARVAL['lengua2']
        elif c in ('izq', 'der', 'frente'):
            rgb[0, :] = BOCA_NARVAL['encia']
        return _rgba_narval(rgb)
    return _pintor_narval(nombre, fn)


def dientes_narval(nombre, arriba, frente, lado, alto_capa, encia=1):
    """Los dientes en una 2.ª capa (la caja algo mayor que el labio), a 32 por bloque: dientes cuadrados de bloque,
    blancos hueso con la cara de abajo en sombra. 'frente' y 'lado': las columnas (en px de Minecraft, desde la
    izquierda de la textura) y el ancho y el alto de cada diente; 'arriba': cuelgan (si no, se levantan). Las filas
    que montan sobre la pieza ('encia'), vacías."""
    def fn(c, tw, th, s):
        tex = np.zeros((th, tw, 4), np.uint8)
        if c not in ('frente', 'izq', 'der'):
            return tex
        dientes = frente if c == 'frente' else lado
        k = 2                                               # píxeles finos por píxel de Minecraft
        for x0, w, h in dientes:
            xs = range(int(round(x0 * k)), int(round((x0 + w) * k)))
            if c == 'der':
                xs = range(tw - int(round((x0 + w) * k)), tw - int(round(x0 * k)))
            for y in range(int(h * k)):
                fila = (encia * k + y) if arriba else (th - 1 - encia * k - y)
                if not (0 <= fila < th):
                    continue
                punta = y >= h * k - 1
                for x in xs:
                    if 0 <= x < tw:
                        col = DIENTE_NARVAL[1] if (punta and arriba) or (y == 0 and not arriba) else DIENTE_NARVAL[0]
                        tex[fila, x, :3] = col
                        tex[fila, x, 3] = 255
        return tex
    return _pintor_narval(nombre, fn, fino=True)


def cuerno_narval(nombre):
    """Un cuerno: gris claro casi blanco con galones (escalones oscuros de 2 x 1 en diagonal con 1 px de gris medio al
    lado, cada 4 px, que se juntan en cada arista en una V hacia la punta); la cara de la punta, con un cuadrado de
    línea oscura."""
    claro, medio, oscuro = CUERNO_NARVAL

    def fn(c, tw, th, s):
        rgb = np.zeros((th, tw, 3)) + claro
        if c in ('arriba', 'abajo'):
            if c == 'arriba' and tw >= 3 and th >= 3:
                rgb[0, :] = rgb[-1, :] = rgb[:, 0] = rgb[:, -1] = oscuro
            return _rgba_narval(rgb)
        xs, ys = L._malla(tw, th)
        # La V: en cada cara la diagonal baja hacia el canto de la derecha (o de la izquierda en las caras alternas),
        # así en cada arista se encuentran dos diagonales. La fila 0 es la punta.
        u = xs if c in ('frente', 'atras') else (tw - 1 - xs)
        k = (ys - u // 2) % 4
        rgb[k == 0] = oscuro
        rgb[k == 1] = medio
        return _rgba_narval(rgb)
    return _pintor_narval(nombre, fn)


# El gancho: una lámina azul marino muy oscura con una línea lavanda de 1 px en espiral cuadrada: sube por el poste
# de delante, cruza por arriba hacia atrás, baja por detrás y se enrosca hacia dentro; abierta abajo y atrás, con un
# hueco por el que se ve a través (ficha, 5.8; el cartel y 1:22:46.88 la enseñan oscura con la línea clara; en el clip,
# 1:11.92, un tercio de la cara es lavanda). Columna 0 = delante. L lavanda, D oscuro, . vacío.
GANCHO_GRANDE_NARVAL = [
    '.DDDDDDD.',
    'DLLLLLLLD',
    'DLDDDDDLD',
    'DLDLLLDLD',
    'DLDDDLDLD',
    'DLD.DLLLD',
    'DLD.DDDDD',
    'DLD......',
    'DLD......',
    'DDD......',
]
GANCHO_CHICO_NARVAL = [
    '.DDDD.',
    'DLLLLD',
    'DLDDLD',
    'DLDLLD',
    'DLD.DD',
    'DDD...',
]


def gancho_narval(nombre, mapa):
    """La lámina gruesa del gancho: en las dos caras de lado, el dibujo (lo de fuera, vacío); en los cantos de arriba,
    de delante y de detrás, el relleno oscuro donde hay lámina, como en el clip (1:11.92) y en el cartel."""
    alto, largo = len(mapa), len(mapa[0])

    def color(ch):
        return GANCHO_BORDE_NARVAL if ch == 'L' else GANCHO_RELLENO_NARVAL

    def fn(c, tw, th, s):
        tex = np.zeros((th, tw, 4), np.uint8)
        canto = GANCHO_RELLENO2_NARVAL
        if c in ('izq', 'der'):
            for r in range(min(th, alto)):
                for col in range(min(tw, largo)):
                    ch = mapa[r][col]
                    if ch == '.':
                        continue
                    x = (tw - 1 - col) if c == 'izq' else col
                    tex[r, x, :3] = color(ch)
                    tex[r, x, 3] = 255
        elif c == 'arriba':                    # filas: de atrás (0) a delante
            for r in range(th):
                col = largo - 1 - r
                if 0 <= col < largo and mapa[0][col] != '.':
                    tex[r, :, :3] = canto
                    tex[r, :, 3] = 255
        # La de abajo, vacía: va pegada al lomo (en el mismo plano saldría con ruido) y nunca se ve.
        elif c in ('frente', 'atras'):
            col = 0 if c == 'frente' else largo - 1
            for r in range(min(th, alto)):
                if mapa[r][col] != '.':
                    tex[r, :, :3] = canto
                    tex[r, :, 3] = 255
        return tex
    return _pintor_narval(nombre, fn)


def _forma_aleta_narval(largo, raiz, punta, recto=0.5):
    """La silueta de una aleta o de un lóbulo (largo x cuerda), una pala: la raíz recta y la cuerda entera hasta
    'recto' del largo; luego el borde de atrás sube en escalones hasta una punta de 'punta' px, y el de delante, casi
    recto, cae 1 px en las dos últimas columnas (de canto, como en el cartel, se lee afilada; desde arriba, como en el
    juego, ancha). Devuelve dentro[r, c]: r = 0 el borde de atrás, c = 0 la raíz."""
    dentro = np.zeros((raiz, largo), bool)
    for c in range(largo):
        t = c / max(1, largo - 1)
        if t <= recto:
            cuerda = raiz
        else:
            u = (t - recto) / (1.0 - recto)
            cuerda = int(round(raiz - (raiz - punta) * u))
        arriba = raiz - (1 if c >= largo - 2 else 0)        # el borde de delante, que cae en la punta
        abajo = max(0, arriba - cuerda)
        dentro[abajo:arriba, c] = True
    return dentro


def dibujo_aleta_narval(largo, raiz, lobulo=False):
    """El dibujo de arriba de una aleta (c desde la raíz, r desde el borde de atrás): el marco de la raíz, la línea lavanda
    a lo largo que sube y baja en escalones, con una muesca hacia el borde de atrás cada 4 px, y cuadraditos sueltos junto
    al borde de delante (como en 1:22:53.40 y 1:11.87). Devuelve {(c, r): 1 línea | 2 segundo tono}."""
    d = {}
    mid = raiz // 2
    c0 = 0
    if not lobulo:
        for c in range(0, 4):                      # el marco de la raíz
            d[(c, 1)] = d[(c, raiz - 2)] = 1
        for r in range(1, raiz - 1):
            d[(0, r)] = d[(3, r)] = 1
        c0 = 4
    ola = (0, 0, 1, 1, 0, 0, -1, -1)
    for c in range(c0, largo - 1):
        r = mid + ola[(c - c0) % len(ola)]
        d[(c, r)] = 1
        if (c - c0) % 4 == 2 and r - 2 >= 0:      # la muesca hacia atrás
            d[(c, r - 1)] = 2
            d[(c, r - 2)] = 2
        if (c - c0) % 5 == 4 and raiz - 2 > r:    # un cuadradito junto al borde de delante
            d[(c, raiz - 2)] = 1
    return d


def aleta_narval(nombre, largo, raiz, punta, espejo=False, semilla=0, lobulo=False, recto=0.5):
    """Una aleta (o un lóbulo de la cola) en losa: arriba, la base azul algo más clara que la piel con el dibujo lavanda
    (dibujo_aleta_narval); abajo, el borde claro y una fila de cuadraditos junto al borde de delante (como dientes de
    peine, en las vistas desde abajo de noche); los cantos, azul oscuro: el de delante y el de la raíz, macizos; el de
    atrás y la punta, que van en escalones, vacíos. 'espejo': la de la derecha (la raíz a la derecha de la textura)."""
    dentro = _forma_aleta_narval(largo, raiz, punta, recto)
    dibujo = dibujo_aleta_narval(largo, raiz, lobulo)
    linea, linea2 = ALETA_LINEA_NARVAL

    def fn(c, tw, th, s):
        if c in ('arriba', 'abajo'):
            rgb = mosaico_narval(tw, th, (nombre, c, semilla), colores=ALETA_NARVAL, pesos=(0.12, 0.50, 0.18, 0.15, 0.05))
            mk = np.zeros((th, tw), bool)
            for r in range(th):
                for x in range(tw):
                    cc = (tw - 1 - x) if espejo else x
                    rr = r if c == 'arriba' else (th - 1 - r)
                    if 0 <= rr < dentro.shape[0] and 0 <= cc < dentro.shape[1]:
                        mk[r, x] = dentro[rr, cc]
            if c == 'arriba':
                for (cc, rr), v in dibujo.items():
                    x = (tw - 1 - cc) if espejo else cc
                    if 0 <= x < tw and 0 <= rr < th and mk[rr, x]:
                        rgb[rr, x] = linea if v == 1 else linea2
            else:
                vec = np.zeros_like(mk)
                vec[1:, :] |= ~mk[:-1, :]
                vec[:-1, :] |= ~mk[1:, :]
                vec[:, 1:] |= ~mk[:, :-1]
                vec[:, :-1] |= ~mk[:, 1:]
                vec[0, :] = vec[-1, :] = True
                vec[:, 0] = vec[:, -1] = True
                borde = mk & vec
                rgb[borde] = linea2
                for x in range(tw):
                    cc = (tw - 1 - x) if espejo else x
                    rr = th - 1 - (raiz - 2)
                    if cc % 2 == 1 and cc < largo - 2 and 0 <= rr < th and mk[rr, x]:
                        rgb[rr, x] = linea
            return _rgba_narval(rgb, np.where(mk, 255, 0).astype(np.uint8))
        rgb = np.zeros((th, tw, 3)) + ALETA_NARVAL[0]
        alfa = np.zeros((th, tw), np.uint8)
        if c == 'frente':
            alfa[...] = 255                                       # el borde de delante, recto
            if tw >= 3:
                cols = range(tw - 2, tw) if not espejo else range(0, 2)
                for x in cols:
                    alfa[:, x] = 0                                # la punta, cortada en escalón
        elif c in ('izq', 'der'):
            raiz_aqui = (c == 'izq') != espejo
            if raiz_aqui:
                alfa[...] = 255
        return _rgba_narval(rgb, alfa)
    return _pintor_narval(nombre, fn)


# ======================================================================================================================
#  El modelo
# ======================================================================================================================
def _aleta_en_narval(m, parte, raiz, lado, d, pint):
    """Una aleta en losa desde 'raiz' (el punto del borde de abajo del costado), hacia fuera ('lado' +1 izquierda,
    -1 derecha), echada atrás d['atras'] grados y caída d['cae']; centrada a lo largo en la raíz."""
    gira = B.girar((-d.get('gira', 0.0), 0, 0))          # sobre su eje largo ('gira' < 0: el borde de delante, abajo)
    if lado > 0:
        M = T(*raiz) @ B.girar((0, d['atras'], 0)) @ B.girar((0, 0, -d['cae'])) @ gira
        x0 = 0.0
    else:
        M = T(*raiz) @ B.girar((0, -d['atras'], 0)) @ B.girar((0, 0, d['cae'])) @ gira
        x0 = -d['largo']
    m._caja(parte, M, x0, -d['grueso'] / 2, -d['raiz'] / 2, d['largo'], d['grueso'], d['raiz'], pint)


def _cuerpo_narval(m):
    """Las piezas del Narval (las mismas en el solo y en el montado). Devuelve las medidas que usa la silla."""
    cw, ch, cl = CRANEO_NARVAL
    dw, dh, dl = DELANTERO_NARVAL
    tw_, th_, tl = TRASERO_NARVAL
    techo = Y0_NARVAL + dh
    piel = piel_narval('piel_narval')
    # El tramo delantero (la raíz del modelo).
    m.parte('cuerpo', None, (0, Y0_NARVAL + dh / 2, -dl / 2))
    m.caja('cuerpo', (0, Y0_NARVAL + dh / 2, -dl / 2), (dw, dh, dl), costado_narval('costado_narval', dl))
    # La cabeza: el cráneo (su techo, 2 px más bajo), los dientes en su 2.ª capa y los tres cuernos.
    techo_c = techo - BAJA_CRANEO_NARVAL
    suelo_c = techo_c - ch
    m.parte('cabeza', 'cuerpo', (0, suelo_c + ch / 2, 0))
    m.caja('cabeza', (0, suelo_c + ch / 2, cl / 2), (cw, ch, cl), cabeza_narval('cabeza_narval'))
    # Los dientes de arriba: cuatro anchos delante y cuatro a cada lado, cuadrados.
    frente_d = [(1.75, 2, 1), (4.75, 2, 1), (7.75, 2, 1), (10.75, 2, 1)]     # de frente, tablitas de 2 x 1
    lado_d = [(1.5, 2, 2), (4.5, 2, 2), (7.5, 2, 2), (10.0, 1, 2)]
    capa = (cw + 0.5, 3.0, cl + 0.25 - 0.5)
    m.caja('cabeza', (0, suelo_c + 1 - capa[1] / 2, 0.5 + capa[2] / 2), capa,
           dientes_narval('dientes_arriba_narval', True, frente_d, lado_d, capa[1], encia=1))
    # Los cuernos: el colmillo del centro de arriba de la cara; el medio, del borde de delante del techo; el corto,
    # 3-4 px detrás.
    g = COLMILLO_NARVAL
    yc = techo_c - g['baja'] - g['grueso'] / 2
    a = math.radians(g['angulo'])
    p0 = np.array((0.0, yc, cl - 1.0))
    p1 = p0 + (g['largo'] + 1.0) * np.array((0.0, math.sin(a), math.cos(a)))
    m.viga('cabeza', p0, p1, g['grueso'], cuerno_narval('colmillo_narval'))
    for nombre, d in (('cuerno_medio_narval', CUERNO_MEDIO_NARVAL), ('cuerno_corto_narval', CUERNO_CORTO_NARVAL)):
        a = math.radians(d['angulo'])
        eje = np.array((0.0, math.sin(a), math.cos(a)))
        p0 = np.array((0.0, techo_c - 1.0, d['z']))
        m.viga('cabeza', p0, p0 + eje * (d['largo'] + 1.0), d['grueso'], cuerno_narval(nombre))
    # La mandíbula, abierta en reposo (sus cajas, ya giradas desde el gozne).
    mw, mh, ml = MANDIBULA_NARVAL
    gozne = (0.0, suelo_c, GOZNE_Z_NARVAL)
    m.parte('mandibula', 'cabeza', gozne)
    Mj = T(*gozne) @ B.girar((ABRE_BOCA_NARVAL, 0, 0))
    _caja_en_narval(m, 'mandibula', Mj, (0, -mh / 2, ml / 2), (mw, mh, ml), mandibula_narval('mandibula_narval'))
    frente_b = [(1.75, 2, 1.5), (4.75, 2, 1.5), (7.75, 2, 1.5), (10.75, 2, 1.5)]
    lado_b = [(1.5, 2, 1.5), (4.5, 2, 1.5), (7.5, 2, 1.5), (10.5, 1, 1.5)]
    capa_b = (mw + 0.5, 2.5, ml + 0.25)
    _caja_en_narval(m, 'mandibula', Mj, (0, capa_b[1] / 2 - 1.0, capa_b[2] / 2 - 0.0), capa_b,
                    dientes_narval('dientes_abajo_narval', False, frente_b, lado_b, capa_b[1], encia=1))
    # El tramo trasero, el tallo y la aleta de la cola.
    yt0 = techo - TRASERO_BAJA_NARVAL - th_
    m.parte('grupa', 'cuerpo', (0, yt0 + th_ / 2, -dl))
    m.caja('grupa', (0, yt0 + th_ / 2, -dl - tl / 2), (tw_, th_, tl), piel)
    lw, lh, ll = TALLO_NARVAL
    yt = yt0 + th_ * ALTURA_COLA_NARVAL
    m.parte('tallo', 'grupa', (0, yt, -dl - tl))
    m.caja('tallo', (0, yt, -dl - tl - ll / 2), (lw, lh, ll), piel)
    zc = -dl - tl - ll
    m.parte('cola', 'tallo', (0, yt, zc))
    d = LOBULO_NARVAL
    for lado in (1, -1):
        pint = aleta_narval('lobulo_i_narval' if lado > 0 else 'lobulo_d_narval', d['largo'], d['raiz'], d['punta'],
                            espejo=lado < 0, semilla=3, lobulo=True, recto=d['recto'])
        _lobulo_narval(m, 'cola', lado, (lado * 1.0, yt, zc + 1.5), d, pint)
    # Las aletas: las de delante del borde de abajo del costado del tramo delantero; las de atrás, del trasero.
    for lado, ld in ((1, 'i'), (-1, 'd')):
        for nombre, dd, x, y, padre in (('del', ALETA_DEL_NARVAL, dw / 2, Y0_NARVAL + ALETA_DEL_NARVAL['y'], 'cuerpo'),
                                        ('tras', ALETA_TRAS_NARVAL, tw_ / 2, yt0 + ALETA_TRAS_NARVAL['y'], 'grupa')):
            pint = aleta_narval(f'aleta_{nombre}_{ld}_narval', dd['largo'], dd['raiz'], dd['punta'], espejo=lado < 0,
                                recto=dd['recto'])
            raiz = (lado * (x - 0.5), y, dd['z'])
            n = m.parte(f'aleta_{nombre}_{ld}', padre, raiz)
            _aleta_en_narval(m, n, raiz, lado, dd, pint)
    # Los ganchos del lomo, de pie en la línea del medio.
    for k, (z, tam) in enumerate(GANCHOS_NARVAL):
        mapa = GANCHO_GRANDE_NARVAL if tam == 1 else GANCHO_CHICO_NARVAL
        alto, largo = len(mapa), len(mapa[0])
        sobre = techo if z > -dl else techo - TRASERO_BAJA_NARVAL
        padre = 'cuerpo' if z > -dl else 'grupa'
        pint = gancho_narval(f'gancho{tam}_narval', mapa)
        m.caja(padre, (0, sobre + alto / 2, z - largo / 2), (2, alto, largo), pint)
    return dict(techo=techo, ancho=dw, largo=dl)


def _caja_en_narval(m, parte, M, centro, tam, pint):
    w, h, d = tam
    m._caja(parte, M @ T(*centro), -w / 2, -h / 2, -d / 2, w, h, d, pint)


def _lobulo_narval(m, parte, lado, raiz, d, pint):
    """Un lóbulo de la cola: una losa horizontal que sale del final del tallo hacia atrás y abierta d['abre'] grados
    hacia su lado; su largo, a lo largo de la X local (la raíz en x = 0)."""
    # Izquierda: la X local hacia atrás y afuera (la raíz en x = 0); derecha: la X local hacia delante y adentro (la raíz
    # en x = 0 y la punta en -largo), así la Z local (el canto de delante) mira afuera en las dos.
    if lado > 0:
        M = T(*raiz) @ B.girar((0, 90 - d['abre'], 0)) @ B.girar((0, 0, -d['cae']))
        x0 = 0.0
    else:
        M = T(*raiz) @ B.girar((0, d['abre'] - 90, 0)) @ B.girar((0, 0, d['cae']))
        x0 = -d['largo']
    m._caja(parte, M, x0, -d['grueso'] / 2, -d['raiz'] / 2, d['largo'], d['grueso'], d['raiz'], pint)


def anims_narval(m, partes_aletas):
    """reposo: flota casi quieto, la cola ondula despacio de arriba abajo y las aletas reman un poco; andar (nadar): la
    cola de arriba abajo (la aleta de la cola es horizontal), cada tramo un poco después del anterior, y las aletas
    reman; correr: la embestida en carrera, el cuerpo rígido, las aletas pegadas atrás y la cola rápida; ataque: el
    mordisco, la mandíbula casi en vertical; especial: la embestida con el colmillo (se echa atrás, se lanza con la boca
    cerrada y muerde al llegar); especial2: el salto fuera del agua; siempre: la boca respira; muerte: se pone de
    costado y se hunde; aparece: sube desde abajo dando coletazos."""
    r = m.anim('reposo', 3.0, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.5, periodo=3.0)
    r.onda('cuerpo', 'r', 0, 1.2, periodo=3.0, fase=0.25)
    # La onda va de la cabeza a la cola: cada tramo, un poco más tarde que el de delante.
    r.onda('grupa', 'r', 0, 3.0, periodo=3.0, fase=-0.1)
    r.onda('tallo', 'r', 0, 6.0, periodo=3.0, fase=-0.2)
    r.onda('cola', 'r', 0, 10.0, periodo=3.0, fase=-0.3)
    for n, lado in partes_aletas:
        r.onda(n, 'r', 1, 8.0 * lado, periodo=3.0, fase=0.0)
        r.onda(n, 'r', 2, 6.0 * lado, periodo=3.0, fase=0.25)
    for nombre, largo, amp in (('andar', 1.2, 1.0), ('correr', 0.7, 1.4)):
        a = m.anim(nombre, largo, bucle=True)
        a.onda('cuerpo', 'r', 0, 2.0 * amp, periodo=largo, fase=0.0)
        a.onda('cuerpo', 'm', 1, 0.6 * amp, periodo=largo, fase=0.25)
        a.onda('cabeza', 'r', 0, -1.5 * amp, periodo=largo, fase=0.0)
        a.onda('grupa', 'r', 0, 6.0 * amp, periodo=largo, fase=-0.12)
        a.onda('tallo', 'r', 0, 12.0 * amp, periodo=largo, fase=-0.24)
        a.onda('cola', 'r', 0, 20.0 * amp, periodo=largo, fase=-0.36)
        for n, lado in partes_aletas:
            if nombre == 'andar':
                # El remo: de casi perpendiculares (las vistas de arriba del juego) a echadas atrás (el cartel), y
                # suben al volver hacia delante.
                a.onda(n, 'r', 1, 20.0 * lado, periodo=largo, fase=0.0)
                a.onda(n, 'r', 2, 10.0 * lado, periodo=largo, fase=0.25)
            else:
                a.rot(n, [(0, 0, 30 * lado, -6 * lado), (largo, 0, 30 * lado, -6 * lado)])
    at = m.anim('ataque', 0.6)
    # La boca baja casi en vertical (~75°, 1:22:58.33) y las aletas se abren hacia delante, a los lados, para frenar.
    at.rot('mandibula', [(0, 0, 0, 0), (0.18, 75 - ABRE_BOCA_NARVAL, 0, 0), (0.32, -ABRE_BOCA_NARVAL, 0, 0), (0.6, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.18, -10, 0, 0), (0.32, 6, 0, 0), (0.6, 0, 0, 0)])
    at.mov('cuerpo', [(0, 0, 0, 0), (0.18, 0, 0, -1.5), (0.32, 0, 0, 3.0), (0.6, 0, 0, 0)])
    for n, lado in partes_aletas:
        abre = -ALETA_DEL_NARVAL['atras'] if 'del' in n else -ALETA_TRAS_NARVAL['atras'] * 0.6
        at.rot(n, [(0, 0, 0, 0), (0.18, 0, abre * lado, 4 * lado), (0.4, 0, abre * lado * 0.6, 0), (0.6, 0, 0, 0)])
    e = m.anim('especial', 1.4)
    e.mov('cuerpo', [(0, 0, 0, 0), (0.35, 0, 0, -3.0), (0.75, 0, 0, 8.0), (1.0, 0, 0, 8.0), (1.4, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.3, -ABRE_BOCA_NARVAL, 0, 0), (0.85, -ABRE_BOCA_NARVAL, 0, 0), (1.0, 75 - ABRE_BOCA_NARVAL, 0, 0),
                        (1.15, 75 - ABRE_BOCA_NARVAL, 0, 0), (1.4, 0, 0, 0)])
    e.rot('cabeza', [(0, 0, 0, 0), (0.35, -6, 0, 0), (0.75, 2, 0, 0), (1.4, 0, 0, 0)])
    for n, lado in partes_aletas:
        e.rot(n, [(0, 0, 0, 0), (0.3, 0, 35 * lado, -8 * lado), (1.0, 0, 35 * lado, -8 * lado), (1.4, 0, 0, 0)])
    for parte, amp in (('grupa', 8), ('tallo', 14), ('cola', 24)):
        e.rot(parte, [(0, 0, 0, 0), (0.2, amp, 0, 0), (0.4, -amp, 0, 0), (0.55, amp, 0, 0), (0.7, -amp, 0, 0),
                      (0.85, 0, 0, 0), (1.4, 0, 0, 0)])
    # especial2: el salto fuera del agua (1:22:42 y 1:22:46.88, con jinete): se encoge, sale con los cuernos por
    # delante y el cuerpo arqueado, las aletas de delante colgando, y entra de cabeza.
    j = m.anim('especial2', 1.6)
    j.mov('cuerpo', [(0, 0, 0, 0), (0.25, 0, -2, -1), (0.6, 0, 9, 5), (0.95, 0, 12, 9), (1.3, 0, 4, 12),
                     (1.6, 0, 0, 0)])
    j.rot('cuerpo', [(0, 0, 0, 0), (0.25, 8, 0, 0), (0.6, -28, 0, 0), (0.95, -4, 0, 0), (1.3, 26, 0, 0),
                     (1.6, 0, 0, 0)])
    j.rot('cabeza', [(0, 0, 0, 0), (0.6, 6, 0, 0), (0.95, 10, 0, 0), (1.3, 4, 0, 0), (1.6, 0, 0, 0)])
    j.rot('mandibula', [(0, 0, 0, 0), (0.6, -ABRE_BOCA_NARVAL * 0.6, 0, 0), (1.1, -ABRE_BOCA_NARVAL * 0.6, 0, 0), (1.6, 0, 0, 0)])
    for parte, a1, a2 in (('grupa', 6, -5), ('tallo', 11, -8), ('cola', 16, -10)):
        j.rot(parte, [(0, 0, 0, 0), (0.25, a1, 0, 0), (0.6, -a1 * 0.7, 0, 0), (0.95, a2, 0, 0), (1.3, a2 * 0.5, 0, 0),
                      (1.6, 0, 0, 0)])
    for n, lado in partes_aletas:
        cuelga = 70 if 'del' in n else 35
        j.rot(n, [(0, 0, 0, 0), (0.3, 0, 10 * lado, -20 * lado), (0.6, 0, 15 * lado, -cuelga * lado),
                  (1.1, 0, 15 * lado, -cuelga * lado), (1.4, 0, 30 * lado, -10 * lado), (1.6, 0, 0, 0)])
    s = m.anim('siempre', 2.6, bucle=True)
    s.onda('mandibula', 'r', 0, 2.5, periodo=2.6)
    d = m.anim('muerte', 1.4)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, 4, 0, 0), (1.4, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.4, 0, -4, 0)])
    d.rot('mandibula', [(0, 0, 0, 0), (0.5, 30, 0, 0), (1.4, 22, 0, 0)])
    d.rot('cola', [(0, 0, 0, 0), (0.4, 18, 0, 0), (1.4, -6, 0, 0)])
    for n, lado in partes_aletas:
        d.rot(n, [(0, 0, 0, 0), (1.4, 0, 0, 20 * lado)])
    ap = m.anim('aparece', 1.2)
    ap.mov('cuerpo', [(0, 0, -10, -4), (0.8, 0, -1, 0), (1.2, 0, 0, 0)])
    ap.rot('cuerpo', [(0, -25, 0, 0), (0.8, 4, 0, 0), (1.2, 0, 0, 0)])
    for parte, amp in (('tallo', 16), ('cola', 26)):
        ap.rot(parte, [(0, 0, 0, 0), (0.2, amp, 0, 0), (0.4, -amp, 0, 0), (0.6, amp, 0, 0), (0.8, -amp, 0, 0),
                       (1.2, 0, 0, 0)])


def _silla_narval(m, medidas):
    """La silla, la cincha y la hebilla del Narval montado (ficha del jinete, 5.2), en el tramo delantero: una losa
    fina de cuero sobre el lomo, del ancho del lomo, que cae por los dos costados como un faldón; de su borde de abajo
    baja la cincha recta por el costado y da la vuelta por la tripa; a 3 px del faldón, la hebilla, un marco gris claro
    de 1 px con la cincha oscura dentro. Sin perilla ni respaldo (no salen en ninguna vista). Devuelve el asiento."""
    d = SILLA_NARVAL
    techo, ancho = medidas['techo'], medidas['ancho']
    z, L = d['z'], d['largo']
    w = ancho + 1.0                                   # vuela 0,5 px por cada lado, sobre el costado
    m.parte('silla', 'cuerpo', (0, techo, z))
    m.caja('silla', (0, techo + d['alto'] / 2, z), (w, d['alto'], L), cuero_narval('silla_narval', 'tapa'))
    for lado in (1, -1):
        # El faldón: de debajo de la losa (el lomo) hasta 'faldon' px más abajo; no sube dentro de la losa, para que
        # su cara no comparta plano con el canto de la losa.
        y0 = techo - d['faldon']                            # su borde de abajo
        alto_f = techo - y0
        m.caja('silla', (lado * (ancho / 2 + 0.25), y0 + alto_f / 2, z), (0.5, alto_f, L),
               cuero_narval('faldon_narval', 'faldon'))
        # La cincha: del borde de abajo del faldón a la tripa (sin meterse bajo el faldón: no pisa su cara).
        alto_c = y0 - (Y0_NARVAL - 0.25)
        m.caja('silla', (lado * (ancho / 2 + 0.375), (y0 + Y0_NARVAL - 0.25) / 2, z), (0.25, alto_c, d['cincha']),
               cincha_narval('cincha_narval'))
        hw, hh = d['hebilla']
        yh = y0 - d['bajo_faldon'] - hh / 2
        m.caja('silla', (lado * (ancho / 2 + 0.6), yh, z), (0.5, hh, hw), hebilla_narval('hebilla_narval'))
    # Por debajo de la tripa.
    m.caja('silla', (0, Y0_NARVAL - 0.125, z), (ancho + 1.0, 0.25, d['cincha']), cincha_narval('cincha_tripa_narval'))
    return (0.0, techo + d['alto'], z)


def cuero_narval(nombre, cual):
    """El cuero de la silla: liso, con el canto de 1 px un tono más claro; el faldón, con una franja más oscura en
    medio (ficha del jinete, 7)."""
    R_ = CUERO_NARVAL

    def fn(c, tw, th, s):
        rgb = np.zeros((th, tw, 3)) + R_[4 if c == 'arriba' else 3]
        if cual == 'tapa':
            if c == 'arriba':
                rgb[0, :] = rgb[-1, :] = CANTO_CUERO_NARVAL
                rgb[:, 0] = rgb[:, -1] = CANTO_CUERO_NARVAL
            elif c in ('izq', 'der', 'frente', 'atras'):
                rgb[...] = R_[4]
        else:
            if c in ('izq', 'der'):
                rgb[-1, :] = CANTO_CUERO_NARVAL                 # el borde de abajo
                rgb[:, 0] = rgb[:, -1] = R_[3]
                f0 = max(1, th // 2 - 1)
                rgb[f0:f0 + 2, 1:-1] = R_[2]                    # la franja oscura de en medio
            elif c in ('frente', 'atras', 'abajo'):
                rgb[...] = R_[1]
        return _rgba_narval(rgb)
    return _pintor_narval(nombre, fn)


def cincha_narval(nombre):
    def fn(c, tw, th, s):
        rgb = np.zeros((th, tw, 3)) + CINCHA_NARVAL[1]
        if c in ('izq', 'der', 'abajo') and tw >= 3:
            rgb[:, 0] = rgb[:, -1] = CINCHA_NARVAL[0]           # los bordes, un tono más oscuros
        return _rgba_narval(rgb)
    return _pintor_narval(nombre, fn)


def hebilla_narval(nombre):
    """La hebilla: un marco cuadrado gris claro de 1 px, con la cincha oscura dentro; la cara de arriba, más clara."""
    def fn(c, tw, th, s):
        rgb = np.zeros((th, tw, 3)) + HEBILLA_NARVAL[1]
        if c in ('izq', 'der'):
            rgb[1:-1, 1:-1] = CINCHA_NARVAL[1]
            rgb[0, :] = HEBILLA_NARVAL[2]
        elif c == 'arriba':
            rgb[...] = HEBILLA_NARVAL[2]
        elif c == 'abajo':
            rgb[...] = HEBILLA_NARVAL[0]
        return _rgba_narval(rgb)
    return _pintor_narval(nombre, fn)


ALETAS_NARVAL = (('aleta_del_i', 1), ('aleta_del_d', -1), ('aleta_tras_i', 1), ('aleta_tras_d', -1))


def construir(con_silla=False):
    """El Narval solo (o con la pieza 'silla' lista para cuando lleve jinete en el juego)."""
    m = B.Modelo(ID, K=2, ancho=128)
    m.escala = 1.0
    medidas = _cuerpo_narval(m)
    if con_silla:
        m.asiento = _silla_narval(m, medidas)
    m.mirar(('cabeza', 0.5))
    anims_narval(m, ALETAS_NARVAL)
    return m


# Dónde va sentado el jinete en el Narval montado: el centro de la tapa de la silla, en px del boceto (Y arriba, el
# frente en +Z), a TAM 1. En el juego (ModelPart: Y hacia abajo desde 24, el frente en -Z) es (0, 2,5, 15).
ASIENTO_NARVAL = (0.0, Y0_NARVAL + DELANTERO_NARVAL[1] + SILLA_NARVAL['alto'], SILLA_NARVAL['z'])


def construir_montado():
    """El Narval con la silla, la cincha y la hebilla que lleva cuando lo monta un Reptisaurio Arquero (id
    'narval_jinete', mismo TAM). El jinete va aparte, sentado en ASIENTO_NARVAL."""
    m = B.Modelo('narval_jinete', K=2, ancho=128)
    m.escala = 1.0
    medidas = _cuerpo_narval(m)
    m.asiento = _silla_narval(m, medidas)
    m.mirar(('cabeza', 0.5))
    anims_narval(m, ALETAS_NARVAL)
    return m


# El huevo: azul marino con el contorno lavanda; las señas, la fila de cuadros y el arco del costado y la punta del
# colmillo.
HUEVO = (('344894', '24367b', '122257'), ('a69bd4', '2f3b7d'),
         [((5, 6), 'a69bd4'), ((7, 6), 'a69bd4'), ((9, 6), 'a69bd4'), ((11, 7), 'a69bd4'),
          ((6, 9), 'a69bd4'), ((7, 9), 'a69bd4'), ((8, 9), 'a69bd4'), ((9, 9), 'a69bd4'), ((10, 10), 'a69bd4'),
          ((6, 10), 'a69bd4'), ((6, 11), 'a69bd4'), ((7, 3), 'dcdde0'), ((8, 3), 'a3a9b1')])

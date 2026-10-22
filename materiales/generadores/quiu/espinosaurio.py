"""El Espinosaurio (DEDsafío 4, Centro de Quiu): «rompe todo a su paso y da Veneno».

Copia fiel del icono del libro del juego (la pila de 144 fotogramas del directo de conterstine, 28-09): un monstruo bajo
y largo de dos patas, cocodrilo verde petróleo con escamas en mosaico; la cola enorme y gruesa en dos tramos, cortada en
recto, con la red amarilla sobre manchas verdes en el tramo grueso, paneles mostaza en el de la punta, la franja crema
por debajo y 8 discos en fila por encima; la vela en arco de 12 discos mostaza (7 por fuera y 5 por dentro) sobre un
núcleo gris casi negro; la cabeza grande e inclinada sobre un cuello corto, con la boca muy abierta (magenta por dentro,
con la lengua rosa), 4 colmillos blancos en la punta del hocico, la mandíbula crema con la punta en gancho, un cuerno
alto casi negro detrás del ojo verde y una cresta de discos sobre el hocico; la garganta y el pecho, una placa blanca con
rayas grises; las patas cortas (muslo verde, canilla amarilla con rayas y pie con 3 garras) y los brazos amarillos con
rayas que cuelgan rectos bajo el pecho, con las manos casi negras.

Se construye ya a su tamaño (TAM = 1): ~7,8 bloques de largo y ~3,4 de alto con la vela (la ficha). Las medidas, en
píxeles de Minecraft (16 por bloque); el eje de las patas en Z = 0, el frente hacia +Z, los pies en Y = 0.
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import T
from bestiario_hormigas import _azar1
from bestiario_reptiles import _con_cara, caja_en, lamina, P


def sagital(x, y, z, alto=0.0):
    return T(x, y, z) @ B.girar((alto, 90, 0))


def ojo_en(nombre, piel, cara, patron, fx, fy, colores):
    W, H_ = int(round(cara[0] * 2)), int(round(cara[1] * 2))
    filas = [['.'] * W for _ in range(H_)]
    x0, y0 = int(round(fx * W)), int(round(fy * H_))
    for j, fila in enumerate(patron):
        for i, ch in enumerate(fila):
            if ch != '.' and 0 <= y0 + j < H_ and 0 <= x0 + i < W:
                filas[y0 + j][x0 + i] = ch
    mapa = [''.join(f) for f in filas]
    return _con_cara(nombre, piel, {'izq': mapa, 'der': mapa}, colores, fino=True)


def quijada(m, padre, gozne, abre):
    m.parte('mandibula', padre, tuple(gozne))
    return T(*gozne) @ B.girar((abre, 0, 0))

ID = 'espinosaurio'
TAM = 1.0
FINO_ESPINOSAURIO = 0.5
# El huevo: la piel verde petróleo, el contorno mostaza y sus señas: la vela de discos con el núcleo oscuro, el cuerno,
# el ojo verde, la boca magenta con un colmillo, la garganta crema y las manchas mostaza de la cola.
HUEVO = (('458072', '2a705b', '143f35'), ('c1b249', '6a610b'),
         [((6, 4), 'bcb05e'), ((7, 3), '9a8c32'), ((8, 3), 'bcb05e'), ((9, 4), '9a8c32'), ((7, 4), '40423f'),
          ((8, 4), '40423f'), ((10, 5), '3b3537'), ((10, 7), '8fc76c'), ((11, 7), '26541c'), ((11, 9), '8c1e4a'),
          ((10, 9), 'f4f0ea'), ((9, 10), 'e3dfb9'), ((9, 11), 'e3dfb9'), ((4, 11), 'c1b249'), ((5, 12), 'c1b249'),
          ((6, 12), 'daca62')])


def _rampa_espinosaurio(*c):
    return np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in c], float)


# Las rampas (de oscuro a claro): las de la paleta de la ficha, corregidas comparando zona a zona el render (con la luz
# del juego y la cámara del libro) con la pila del icono (colores.py): casi todas quedan a ±10 % del icono.
PIEL_ESPINOSAURIO = _rampa_espinosaurio('104537', '1e5e4c', '2a705b', '378d75', '49a390')
MUSLO_ESPINOSAURIO = _rampa_espinosaurio('213a33', '344f44', '455d51', '546f62', '648172')
AMARILLO_ESPINOSAURIO = _rampa_espinosaurio('6a610b', '978a28', 'c1b249', 'daca62', 'efe99e')
MANCHA_ESPINOSAURIO = _rampa_espinosaurio('17351c', '26472d', '365a3e', '436b4d', '547b5b')
CREMA_ESPINOSAURIO = _rampa_espinosaurio('989471', 'aca986', 'd2cdad', 'e8e3c7', 'fbf7e3')
DISCO_ESPINOSAURIO = _rampa_espinosaurio('352b05', '594b08', '8e811e', 'ada238', 'c5bc4f')
DISCO_COLA_ESPINOSAURIO = _rampa_espinosaurio('322904', '645005', '968725', 'b1a73b', 'c2bc4f')
NUCLEO_ESPINOSAURIO = _rampa_espinosaurio('22261e', '30332d', '40423f', '4e4f49', '5a5b55')
GARGANTA_ESPINOSAURIO = _rampa_espinosaurio('8c8b73', 'a9a68b', 'c5c2a1', 'd3cfbf', 'e0ddd0')
BOCA_ESPINOSAURIO = _rampa_espinosaurio('3a0718', '5e0f2c', '8c1e4a', 'b04a72', 'd98aa6')
DIENTE_ESPINOSAURIO = _rampa_espinosaurio('b4aca4', 'd8d2cc', 'f0ece6', 'f8f6f0', 'ffffff')
TAPA_ESPINOSAURIO = _rampa_espinosaurio('2a705b', '378d75', '4d9a8a', '5aa596', '6ab0a2')
HOCICO_ESPINOSAURIO = _rampa_espinosaurio('14302a', '1f4239', '2c5249', '3a6458', '4a7568')
MANDIBULA_ESPINOSAURIO = _rampa_espinosaurio('5e5748', '857f6b', 'bdb69e', 'd4ccb6', 'e2dccb')
OSCURO_ESPINOSAURIO = _rampa_espinosaurio('181415', '251e20', '2f292b', '3a3333', '463e3e')
CRESTA_ESPINOSAURIO = _rampa_espinosaurio('2f2911', '534a22', '786f3e', '908752', 'a29a6c')
CANILLA_ESPINOSAURIO = _rampa_espinosaurio('341900', '7b7014', 'cab74d', 'e4db80', 'f2eaa8')
BRAZO_ESPINOSAURIO = _rampa_espinosaurio('2e1600', '6c6012', 'a99446', 'c5b668', 'd2c68d')
MANO_ESPINOSAURIO = _rampa_espinosaurio('211b1a', '2d2623', '3e3737', '504747', '5e5555')
GARRA_ESPINOSAURIO = _rampa_espinosaurio('211a19', '342a27', '4e3c3e', '5e4e50', '6e6062')


# ======================================================================================================================
#  Los pintores (todos limpios: 4 o 5 tonos, un dibujo y nada de ruido)
# ======================================================================================================================
def _malla_espinosaurio(tw, th):
    ys, xs = np.mgrid[0:th, 0:tw]
    return xs, ys


def _img_espinosaurio(R, v, dentro=None):
    tex = L._rgba(L.color_continuo(R, np.clip(np.round(v), 0, len(R) - 1)))
    if dentro is not None:
        tex[..., 3] = np.where(dentro, 255, 0)
    return tex


def _luz_espinosaurio(tw, th, cara, base, luz=0.6):
    """El tono de fondo: en los lados, algo más claro arriba; arriba, más claro; abajo, más oscuro."""
    xs, ys = _malla_espinosaurio(tw, th)
    if cara == 'arriba':
        v = np.full((th, tw), base + luz)
    elif cara == 'abajo':
        v = np.full((th, tw), base - luz)
    else:
        v = base + luz * (0.45 - (ys + 0.5) / max(1, th) * 0.9)
    return xs, ys, v


def _hacia_atras_espinosaurio(xs, ys, tw, th, cara):
    """Cuánto de atrás (0, delante; 1, atrás) está cada píxel de la cara (las caras de lado van como se ven de fuera:
    en 'izq' el frente queda a la derecha; en 'der', a la izquierda; arriba, el frente abajo)."""
    if cara == 'izq':
        return 1.0 - (xs + 0.5) / tw
    if cara == 'der':
        return (xs + 0.5) / tw
    if cara in ('arriba', 'abajo'):
        return 1.0 - (ys + 0.5) / th
    return np.full(xs.shape, 0.0 if cara == 'frente' else 1.0)


def _voronoi_espinosaurio(tw, th, paso, semilla, alargar=1.0, desvio=0.55):
    """Celdas de un mosaico: semillas en una rejilla al tresbolillo con su desvío fijo; devuelve, por píxel, la distancia
    a la semilla más cercana, la distancia a la segunda y el número de la celda."""
    xs, ys = _malla_espinosaurio(tw, th)
    px, py = paso * alargar, paso
    d1 = np.full((th, tw), 1e9)
    d2 = np.full((th, tw), 1e9)
    cel = np.zeros((th, tw), int)
    for gy in range(-1, int(th / py) + 2):
        for gx in range(-1, int(tw / px) + 2):
            cx = gx * px + (gy % 2) * px * 0.5 + (_azar1(gx, gy, semilla) - 0.5) * px * desvio
            cy = gy * py + (_azar1(gx, gy, semilla + 3) - 0.5) * py * desvio
            d = np.hypot((xs + 0.5 - cx) / alargar, ys + 0.5 - cy)
            mk = d < d1
            d2 = np.where(mk, d1, np.minimum(d2, d))
            cel = np.where(mk, (gx + 50) * 1000 + gy + 50, cel)
            d1 = np.where(mk, d, d1)
    return xs, ys, d1, d2, cel


def _borde_celdas_espinosaurio(cel):
    """Los píxeles del borde de cada celda (los que tocan, a la derecha o abajo, otra celda): rayas de 1 px seguidas."""
    b = np.zeros(cel.shape, bool)
    b[:, :-1] |= cel[:, :-1] != cel[:, 1:]
    b[:-1, :] |= cel[:-1, :] != cel[1:, :]
    return b


def celdas_espinosaurio(nombre, R, base=2.0, luz=0.6, paso=3.0, claro=0.3, oscuro=0.9, semilla=0, R_bajo=None,
                        corte=0.55):
    """La piel en mosaico del icono: escamas como adoquines redondeados de 2-3 px (celdas de Voronoi al píxel), con la
    raya de 1 px más oscura entre ellas y algunas escamas un tono más claras; sin motas sueltas. Con 'R_bajo', las
    escamas de la parte de abajo de los costados (por debajo de 'corte' del alto, celda a celda) van de esa rampa: el
    tronco, verde petróleo arriba y gris verdoso abajo, como en la pila del icono."""
    def fn(tw, th, cara, s):
        xs, ys, v = _luz_espinosaurio(tw, th, cara, base, luz)
        cel = _voronoi_espinosaurio(tw, th, paso, s * 3 + semilla)[-1]
        raya = _borde_celdas_espinosaurio(cel)
        v = v + (_azar1(cel, cel // 3, s + semilla + 11) < claro) * 0.8
        v = np.where(raya, v - oscuro, v)
        tex = _img_espinosaurio(R, v)
        if R_bajo is not None and cara in ('izq', 'der', 'frente', 'atras'):
            # La fila media de cada celda decide de qué lado del corte queda (para que el borde siga las escamas).
            fila_media = np.zeros((th, tw))
            for c in np.unique(cel):
                sel = cel == c
                fila_media[sel] = ys[sel].mean()
            bajo = fila_media >= th * corte
            tb = _img_espinosaurio(R_bajo, v)
            tex[bajo] = tb[bajo]
        return tex, None
    return B.Pintor(nombre, fn)


def red_cola_espinosaurio(nombre, R_net, R_mancha, semilla=0, paso=4.4):
    """El tramo grueso de la cola: manchas verde azuladas redondeadas de 4-5 px dentro de una red amarilla de 1 px, como
    una jirafa; junto al tronco, verde liso (la red empieza celda a celda); hacia la punta, alguna mancha se queda
    amarilla; el canto de arriba, claro."""
    def fn(tw, th, cara, s):
        xs, ys, v = _luz_espinosaurio(tw, th, cara, 2.0, 0.6)
        if cara == 'abajo':
            return _img_espinosaurio(R_net, v), None
        atras = _hacia_atras_espinosaurio(xs, ys, tw, th, cara)
        cel = _voronoi_espinosaurio(tw, th, paso, s * 5 + semilla, alargar=1.2, desvio=0.3)[-1]
        # Junto al tronco (el 30 % de delante, con 5 px metidos en el tronco) la cola es verde liso, como el tronco.
        red = _borde_celdas_espinosaurio(cel) & (atras > 0.3 + 0.1 * _azar1(cel, cel // 3, s + 13))
        llena = _azar1(cel, cel // 7, s + semilla + 5) < np.clip(atras - 0.85, 0, 1) * 2.5
        verde = ~red & ~llena
        tex = _img_espinosaurio(R_net, v + 0.3)
        tm = _img_espinosaurio(R_mancha, v + 0.5 + (_azar1(cel, cel // 5, s + 9) < 0.3) * 0.7)
        tex[verde] = tm[verde]
        if cara in ('izq', 'der'):
            borde = ys == 0
            tex[borde] = _img_espinosaurio(R_net, np.full((th, tw), 4.0))[borde]
        return tex, None
    return B.Pintor(nombre, fn)


def paneles_cola_espinosaurio(nombre, R, R_mancha, ancho=8, cuadros=True):
    """El tramo de la punta: mostaza en paneles de ~8 px separados por rayas verticales de 1 px más oscuras, con el
    canto claro arriba y en la punta; y, hacia la punta y abajo, ventanas verde azuladas de 3 x 3 a 4 x 4 dentro de
    los paneles (como en el icono)."""
    def fn(tw, th, cara, s):
        xs, ys, v = _luz_espinosaurio(tw, th, cara, 2.0, 0.6)
        if cara in ('izq', 'der'):
            atras = _hacia_atras_espinosaurio(xs, ys, tw, th, cara)
            pos = np.floor(atras * tw).astype(int)               # desde delante, en píxeles
            desde_punta = tw - 1 - pos
            raya = (desde_punta % ancho) == ancho - 1
            v = np.where(raya, v - 0.9, v)
            v = np.where((ys == 0) | (desde_punta == 0), 4.0, v)   # el canto claro de arriba y el de la punta
            tex = _img_espinosaurio(R, v)
            if cuadros:
                verde = np.zeros((th, tw), bool)
                # (desde la punta, desde arriba, largo, alto): las ventanas del icono, en los dos paneles de la punta
                # (dos una encima de otra en el primero y una arriba en el segundo) y una pequeña en el tercero.
                for p0, y0, lw, lh in ((1, 2, 5, 4), (1, 7, 5, 3), (9, 2, 4, 4), (17, 7, 3, 2)):
                    verde |= ((desde_punta >= p0) & (desde_punta < p0 + lw) & (ys >= y0) & (ys < y0 + lh))
                tm = _img_espinosaurio(R_mancha, v)
                tex[verde] = tm[verde]
            return tex, None
        if cara == 'arriba':
            v = np.where((xs == 0) | (xs == tw - 1), 4.0, v + 0.3)
        return _img_espinosaurio(R, v), None
    return B.Pintor(nombre, fn)


def placas_espinosaurio(nombre, R, ancho=7, base=2.0):
    """La franja crema de la tripa: placas de 6-7 px separadas por rayas de 1 px más oscuras."""
    def fn(tw, th, cara, s):
        xs, ys, v = _luz_espinosaurio(tw, th, cara, base, 0.5)
        if cara in ('izq', 'der', 'abajo', 'arriba'):
            atras = _hacia_atras_espinosaurio(xs, ys, tw, th, cara)
            if cara in ('abajo', 'arriba'):
                pos = ys
            else:
                pos = np.round(atras * tw).astype(int)
            v = np.where((pos % ancho) == 0, v - 1.0, v)
        return _img_espinosaurio(R, v), None
    return B.Pintor(nombre, fn)


def rayas_h_espinosaurio(nombre, R, paso=3, base=2.0, luz=0.5, fase=0, oscuro=1.2, solo=None):
    """Rayas horizontales de 1 px cada 'paso' (la garganta, las canillas, los brazos); 'solo': las caras que las llevan."""
    def fn(tw, th, cara, s):
        xs, ys, v = _luz_espinosaurio(tw, th, cara, base, luz)
        if cara not in ('arriba', 'abajo') and (solo is None or cara in solo):
            v = np.where(((ys + fase) % paso) == paso - 1, v - oscuro, v)
        return _img_espinosaurio(R, v), None
    return B.Pintor(nombre, fn)


def liso_espinosaurio(nombre, R, base=2.0, luz=0.5, fino=False):
    def fn(tw, th, cara, s):
        xs, ys, v = _luz_espinosaurio(tw, th, cara, base, luz)
        return _img_espinosaurio(R, v), None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO_ESPINOSAURIO) if fino else p


def disco_espinosaurio(nombre, R, nivel, de, luz=0.45):
    """Un disco de la vela, de la cola o de la cresta, en píxeles: 'de' cajas apiladas desde la base (la 0, la más ancha
    y la más baja; cada una 2 px más estrecha y 1 más alta), que dan la punta redonda. Este pintor es el de la caja
    'nivel'. En las caras de lado, redondo con la luz de arriba (4 tonos: el brillo arriba y atrás, el tono, y la
    sombra abajo y delante) y el contorno oscuro de 1 px a los lados y en la base; la tapa de cada escalón, clara."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_espinosaurio(tw, th)
        if cara not in ('izq', 'der'):
            # La tapa de cada escalón, al sol (que el disco se lea redondo y no con un tejadillo oscuro); el canto de
            # delante, a media luz; el de detrás y el de abajo, en sombra.
            tono = {'arriba': 3.2, 'frente': 2.0}.get(cara, 1.2)
            return _img_espinosaurio(R, np.full((th, tw), tono)), None
        sobra = de - 1 - nivel                       # filas del disco por encima de esta caja
        alto = th + sobra
        ancho = tw + 2 * nivel
        y = ys + sobra
        x = xs + nivel
        if cara == 'izq':                            # el frente a la derecha: la luz, arriba y atrás (a la izquierda)
            u = (x + 0.5) / ancho
        else:
            u = 1.0 - (x + 0.5) / ancho
        w = (y + 0.5) / alto
        # Redondo y con la luz de arriba (como en el icono): la parte de arriba clara, con el brillo hacia atrás; la
        # de en medio, de su tono; la de abajo, en sombra; en 4 tonos limpios.
        d = np.hypot((u - 0.35) * 0.9, (w - luz * 0.3) * 1.3)
        v = np.full((th, tw), 2.5)
        v = np.where(d < 0.42, 2.9, v)
        v = np.where(d < 0.2, 3.4, v)
        v = np.where((w > 0.74) | (u > 0.86), 1.8, v)
        contorno = (xs == 0) | (xs == tw - 1)
        if nivel == 0:
            contorno |= ys == th - 1
        v = np.where(contorno, 0.4, v)
        return _img_espinosaurio(R, v), None
    return B.Pintor(nombre, fn)


def pintores_disco_espinosaurio(nombre, R, de=3, luz=0.45):
    return [disco_espinosaurio(f'{nombre}_{k}de{de}', R, k, de, luz) for k in range(de)]


def ojo_mapa_espinosaurio():
    """El ojo, a 32 por bloque (2 x 3 px de Minecraft): una rendija verde de pie con el borde casi negro, y encima el
    párpado amarillo pardo (como en los directos de aquino y elded)."""
    return ['pppp',
            'kggk',
            'kggk',
            'kggk',
            'kggk',
            '.kk.']


def lengua_espinosaurio(nombre, R):
    """La cara de arriba de la mandíbula de abajo: magenta oscuro, con la lengua (una raya de 1 px rosa apagado) por el
    medio de la mitad de delante."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_espinosaurio(tw, th)
        v = np.full((th, tw), 1.3)
        if cara == 'arriba':
            c = (tw - 1) / 2.0
            delante = ys >= th * 0.4                     # (arriba: el frente de la caja queda abajo de la cara)
            v = np.where((np.abs(xs - c) <= 0.6) & delante, 2.9, v)
        return _img_espinosaurio(R, v), None
    return B.fino(B.Pintor(nombre, fn), FINO_ESPINOSAURIO)


def colmillos_espinosaurio(nombre, R, largos, encia=1):
    """La 2.ª capa de los dientes de arriba: la caja algo mayor que el hocico, vacía salvo los dientes que cuelgan de su
    canto de abajo (a 32 por bloque); las 'encia' filas de arriba, las que montan sobre el hocico, vacías. 'largos':
    (posición desde la punta, largo, medio ancho), en px de Minecraft, de cada diente; en la cara de delante, los de
    las esquinas."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_espinosaurio(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara in ('arriba', 'abajo', 'atras'):
            return tex, None
        x = xs + 0.5
        r = ys + 0.5 - encia * 2                     # filas desde el canto del hocico (las de la encía, sobre él, vacías)
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        if cara == 'frente':
            lista = [(1.0, largos[0][1], 1.0), (tw / 2.0 - 1.0, largos[0][1] * 0.8, 1.0)]
            pos_x = lambda p: p * 2.0
        else:
            lista = largos
            pos_x = (lambda p: tw - p * 2.0) if cara == 'izq' else (lambda p: p * 2.0)
        for p, l, w in lista:
            cx = pos_x(p)
            ancho = w * 1.0 * np.clip(1.0 - r / (l * 2.0), 0, 1) + 0.15
            mk = (r >= 0) & (r < l * 2.0) & (np.abs(x - cx) < ancho)
            v = np.where(mk, 3.0 + (x < cx) * 0.8 - (x > cx + 0.3) * 0.7 + (r > l * 2.0 - 2) * 0.6, v)
            dentro |= mk
            if cara == 'frente':
                mk2 = (r >= 0) & (r < l * 2.0) & (np.abs(x - (tw - cx)) < ancho)
                v = np.where(mk2, 3.0 + (x < tw - cx) * 0.8 - (x > tw - cx + 0.3) * 0.7, v)
                dentro |= mk2
        tex = _img_espinosaurio(R, v, dentro)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO_ESPINOSAURIO)


def dientes_abajo_espinosaurio(nombre, R, posiciones, largo=1.5):
    """La 2.ª capa de los dientes de abajo: pequeños, de pie desde el canto de arriba de la mandíbula (a 32 por bloque);
    'posiciones' en px de Minecraft desde la punta."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_espinosaurio(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara in ('arriba', 'abajo', 'atras'):
            return tex, None
        x = xs + 0.5
        r = (2 * largo) - (ys + 0.5)                     # desde la punta del diente hacia abajo (0, la punta)
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        if cara == 'frente':
            cxs = [tw / 2.0 - 1.4, tw / 2.0 + 1.4]
        else:
            cxs = [(tw - p * 2.0) if cara == 'izq' else p * 2.0 for p in posiciones]
        for cx in cxs:
            ancho = 1.0 * np.clip(r / (2 * largo), 0, 1) + 0.2
            mk = (r >= 0) & (r < 2 * largo) & (np.abs(x - cx) < ancho)
            v = np.where(mk, 3.0 + (x < cx) * 0.7 - (x > cx + 0.3) * 0.6, v)
            dentro |= mk
        return _img_espinosaurio(R, v, dentro), None
    return B.fino(B.Pintor(nombre, fn), FINO_ESPINOSAURIO)


def boca_lamina_espinosaurio(nombre, R, puntos):
    """La pared de dentro de la boca abierta (una lámina en el plano del espinazo): el triángulo entre las dos mandíbulas,
    magenta oscuro, algo más oscuro hacia la garganta. puntos: los tres vértices, en fracciones del ancho y del alto
    de la lámina (y hacia arriba)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_espinosaurio(tw, th)
        x, y = (xs + 0.5) / tw, 1.0 - (ys + 0.5) / th
        (ax, ay), (bx, by), (cx, cy) = puntos

        def lado(px, py, qx, qy):
            return (qx - px) * (y - py) - (qy - py) * (x - px)
        d1, d2, d3 = lado(ax, ay, bx, by), lado(bx, by, cx, cy), lado(cx, cy, ax, ay)
        dentro = ((d1 <= 0) & (d2 <= 0) & (d3 <= 0)) | ((d1 >= 0) & (d2 >= 0) & (d3 >= 0))
        v = np.full((th, tw), 1.6) - (x > 0.8) * 0.6
        return _img_espinosaurio(R, v, dentro), None
    return B.fino(B.Pintor(nombre, fn), FINO_ESPINOSAURIO)


def garras_espinosaurio(nombre, R, n=3):
    """Garras dibujadas (lámina): 'n' garras que salen de arriba y se curvan hacia delante (la derecha) y abajo, claras
    a un lado y en sombra al otro."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_espinosaurio(tw, th)
        x, y = xs + 0.5, ys + 0.5
        t = y / th
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        for k in range(n):
            c0 = (k + 0.5) / n * tw
            cc = c0 + 0.9 * (t ** 2) * tw / n
            w = tw / n * 0.42 * np.clip(1.0 - t, 0, 1) ** 0.7 + 0.35
            mk = (np.abs(x - cc) < w) & (t < 0.98)
            v = np.where(mk, 2.4 + ((x - cc) < 0) * 0.8 - ((x - cc) > w * 0.4) * 0.6 + (t > 0.7) * 0.6, v)
            dentro |= mk
        return _img_espinosaurio(R, v, dentro), None
    return B.fino(B.Pintor(nombre, fn), FINO_ESPINOSAURIO)


def cresta_placa_espinosaurio(nombre, R_placa, R_borde):
    """La placa de la cresta del hocico: oscura, con el borde amarillo de 1 px arriba y a los lados."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_espinosaurio(tw, th)
        if cara not in ('izq', 'der'):
            return _img_espinosaurio(R_placa, np.full((th, tw), 1.6)), None
        tex = _img_espinosaurio(R_placa, np.full((th, tw), 2.0) + (ys < th / 2) * 0.4)
        borde = (ys == 0) | (xs == 0) | (xs == tw - 1)
        tb = _img_espinosaurio(R_borde, np.full((th, tw), 2.6))
        tex[borde] = tb[borde]
        return tex, None
    return B.Pintor(nombre, fn)


# ======================================================================================================================
#  Las piezas
# ======================================================================================================================
def disco_en_espinosaurio(m, parte, M, largo, alto, grueso, pints):
    """Un disco de píxeles en el plano del espinazo, que sale de la base (el origen del marco M) hacia su +Y: 'largo' a
    lo largo (Z del marco), 'alto' (Y) y 'grueso' (X); tantas cajas apiladas como pintores (cada una 2 más estrecha, 1
    más alta y algo más fina, para que sus caras no se pisen)."""
    de = len(pints)
    for k, p in enumerate(pints):
        w = largo - 2 * k
        h = alto - (de - 1 - k)
        if w < 1:
            break
        caja_en(m, parte, M, (0, h / 2.0, 0), (grueso - 0.25 * k, h, w), p)


def construir():
    """El Espinosaurio a su tamaño: el modelo, sus pintores y sus animaciones. Las medidas salen del icono del libro
    vuelto al modelo con su cámara (az -42, el 13, ortográfica; proy.py): el eje de las canillas en Z = 0."""
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0
    m.paso = 3.0

    # Los pintores.
    piel = celdas_espinosaurio('piel_espinosaurio', PIEL_ESPINOSAURIO, base=2.0, luz=0.6)
    piel_tronco = celdas_espinosaurio('piel_tronco_espinosaurio', PIEL_ESPINOSAURIO, base=2.0, luz=0.6, semilla=2,
                                      R_bajo=MUSLO_ESPINOSAURIO, corte=0.5)
    piel_cuello = celdas_espinosaurio('piel_cuello_espinosaurio', PIEL_ESPINOSAURIO, base=2.0, luz=0.6, semilla=5)
    vientre = placas_espinosaurio('vientre_espinosaurio', CREMA_ESPINOSAURIO)
    garganta = rayas_h_espinosaurio('garganta_espinosaurio', GARGANTA_ESPINOSAURIO, paso=3, base=2.3, luz=0.4,
                                    oscuro=1.1, solo=('frente',))
    cola1 = red_cola_espinosaurio('cola1_espinosaurio', AMARILLO_ESPINOSAURIO, MANCHA_ESPINOSAURIO, paso=5.0)
    cola2 = paneles_cola_espinosaurio('cola2_espinosaurio', AMARILLO_ESPINOSAURIO, MANCHA_ESPINOSAURIO)
    muslo = celdas_espinosaurio('muslo_espinosaurio', MUSLO_ESPINOSAURIO, base=2.0, luz=0.5, semilla=9, claro=0.2)
    canilla = rayas_h_espinosaurio('canilla_espinosaurio', CANILLA_ESPINOSAURIO, paso=3, base=2.1, luz=0.5, oscuro=1.4)
    pie = liso_espinosaurio('pie_espinosaurio', CANILLA_ESPINOSAURIO, base=1.4, luz=0.5)
    # La tapa del cráneo y del hocico, más clara (en el icono le da la luz de lleno: #549288), con su mosaico; y los
    # lados del hocico, un poco más apagados (en sombra).
    tapa = celdas_espinosaurio('tapa_espinosaurio', TAPA_ESPINOSAURIO, base=3.0, luz=0.4, claro=0.2, oscuro=0.7,
                               semilla=3)
    piel_hocico = celdas_espinosaurio('piel_hocico_espinosaurio', HOCICO_ESPINOSAURIO, base=2.4, luz=0.5, semilla=7)
    brazo = rayas_h_espinosaurio('brazo_espinosaurio', BRAZO_ESPINOSAURIO, paso=3, base=2.1, luz=0.5, oscuro=1.4)
    mano = liso_espinosaurio('mano_espinosaurio', MANO_ESPINOSAURIO, base=2.0, luz=0.5)
    garra = garras_espinosaurio('garra_espinosaurio', GARRA_ESPINOSAURIO, n=3)
    nucleo = liso_espinosaurio('nucleo_espinosaurio', NUCLEO_ESPINOSAURIO, base=2.0, luz=0.3)
    cuerno = liso_espinosaurio('cuerno_espinosaurio', OSCURO_ESPINOSAURIO, base=2.0, luz=0.4)
    disco_v = pintores_disco_espinosaurio('disco_espinosaurio', DISCO_ESPINOSAURIO, de=2)
    disco_c = pintores_disco_espinosaurio('discoc_espinosaurio', DISCO_COLA_ESPINOSAURIO, de=3, luz=0.5)
    disco_r = pintores_disco_espinosaurio('crestad_espinosaurio', CRESTA_ESPINOSAURIO, de=2)
    placa = cresta_placa_espinosaurio('cresta_placa_espinosaurio', OSCURO_ESPINOSAURIO, CRESTA_ESPINOSAURIO)
    mandibula = liso_espinosaurio('mandibula_espinosaurio', MANDIBULA_ESPINOSAURIO, base=2.0, luz=0.5)
    paladar = liso_espinosaurio('paladar_espinosaurio', BOCA_ESPINOSAURIO, base=1.6, luz=0.3)
    lengua = lengua_espinosaurio('lengua_espinosaurio', BOCA_ESPINOSAURIO)

    # ------------------------------------------------------------------------------------------------------------------
    #  El tronco: corto y hondo, echado 14° con el pecho arriba (en el icono, con la cámara a 13°, el lomo se ve casi
    #  plano): el lomo, en la línea del espinazo, de Y 30 (Z -8,7) a 34,6 (Z 9,9); la tripa, a Y 15 en Z 12,6. Es
    #  corto: su canto de atrás (en el icono, x 95,5 de la pila) cae justo encima de las patas, como en un cocodrilo;
    #  detrás ya es la cola.
    # ------------------------------------------------------------------------------------------------------------------
    m.parte('cuerpo', None, (0, 14, 0))
    Mt = T(0, 23.26, 5.25) @ B.girar((-14, 0, 0))
    caja_en(m, 'cuerpo', Mt, (0, 0, 0), (16, 19.5, 19.5), piel_tronco, caras={'abajo': vientre})
    # El pecho y el cuello: un bloque que sube del frente del tronco hasta la cabeza, con la placa blanca delante.
    ZF = 23.3                           # la cara de delante del cuello (la placa blanca, de 11 de ancho)
    m.caja('cuerpo', (0, 29.5, ZF - 5.0), (11, 21, 10), piel_cuello, caras={'frente': garganta})

    # ------------------------------------------------------------------------------------------------------------------
    #  La cola: dos tramos de caja que bajan hacia la punta (la punta toca el suelo) y casi no se afilan; cortada en
    #  recto. La franja crema de la tripa por debajo, que acaba antes de la punta.
    # ------------------------------------------------------------------------------------------------------------------
    # Medidas del icono: el tramo 1, arriba de Y 24,9 (Z -8) a 18,6 (Z -40) y abajo de 9,6 a 5,8; el tramo 2, arriba de
    # 17,3 a 10,8 (la punta, Z -77) y abajo de 6,5 a 0,9 (la punta toca el suelo).
    m.parte('cola', 'cuerpo', (0, 17.25, -9.0))
    Mc1 = T(0, 17.25, -9.0) @ B.girar((-9.3, 0, 0))
    caja_en(m, 'cola', Mc1, (0, 0, -12.0), (10, 14.2, 34), cola1, caras={'abajo': vientre})
    caja_en(m, 'cola', Mc1, (0, -6.3, -12.0), (10.4, 2.6, 34.2), vientre, caras={'arriba': None})
    j = P(Mc1, (0, 0, -28.4))
    m.parte('cola2', 'cola', tuple(j))
    Mc2 = T(*j) @ B.girar((-8.3, 0, 0))
    caja_en(m, 'cola2', Mc2, (0, -0.85, -20.0), (8.5, 12.2, 40.6), cola2, caras={'abajo': vientre})
    caja_en(m, 'cola2', Mc2, (0, -6.75, -14.0), (8.9, 2.2, 28.2), vientre, caras={'arriba': None})
    # Los 8 discos de la cola, de canto: huevos anchos que casi se tocan abajo, echados 12° hacia delante, que crecen
    # hacia el cuerpo; la base, metida en la cola. (marco, a lo largo del tramo, largo, alto a la vista sobre la cola):
    # las cimas, del perfil de la silueta del icono, uno cada ~8 desde Z -73 hasta Z -17,5.
    discos_cola = ((Mc2, -36.6, 7, 4.4), (Mc2, -29.3, 8, 5.4), (Mc2, -20.8, 8, 6.1), (Mc2, -13.0, 8, 6.1),
                   (Mc2, -5.7, 8, 7.7), (Mc1, -25.8, 8, 8.8), (Mc1, -16.9, 8, 9.3), (Mc1, -8.6, 8, 10.8))
    for k, (M, z, largo, alto) in enumerate(discos_cola):
        parte, tope = ('cola2', 5.25) if k < 5 else ('cola', 7.1)
        disco_en_espinosaurio(m, parte, M @ T(0, tope - 2.5, z + 0.2) @ B.girar((12, 0, 0)), largo,
                              int(round(alto + 1.3)), 1.5 + 0.05 * (k % 2), disco_c)

    # ------------------------------------------------------------------------------------------------------------------
    #  La vela: el núcleo casi negro y 12 discos en arco (7 por fuera y 5 por dentro), puestos en radio.
    # ------------------------------------------------------------------------------------------------------------------
    DV = 1.2                            # (todo, 1,2 hacia delante: la silueta del icono)
    m.parte('vela', 'cuerpo', (0, 31, 3 + DV))
    m.caja('vela', (0, 38.0, 4.0 + DV), (0.8, 13, 14), nucleo)
    # Los 12 discos, en su sitio medido en el icono: (Z y Y de su centro, ángulo desde arriba (hacia delante +), largo,
    # alto). Por fuera: el de abajo atrás (de pie, sobre el lomo), el de atrás, el de arriba atrás, el de arriba, el de
    # arriba delante, el de delante y el de abajo delante (medio tapado por el cuello). Por dentro, cinco más pequeños.
    fuera = ((-6.1, 34.4, 0, 6, 9), (-6.9, 41.7, -25, 6, 8), (-5.1, 49.0, -40, 6, 8), (1.1, 52.6, -10, 7, 8),
             (7.3, 52.6, 20, 7, 8), (10.9, 47.5, 45, 6, 8), (13.0, 41.8, 65, 6, 8))
    dentro = ((-1.5, 44.4, -25, 6, 8), (5.2, 45.8, 15, 6, 8), (8.3, 42.5, 45, 5, 8), (-4.6, 38.5, -50, 5, 7),
              (-3.0, 34.1, 0, 5, 7))
    # Cada disco con su grueso (0,06 más que el anterior): los que se solapan no tienen caras en el mismo plano (si
    # no, se pisan y salen con ruido, también en el juego). Los de fuera, 1 hacia dentro de su centro medido: así el
    # borde de la vela cae en el del icono.
    for k, ((z, y, ang, lz, ly), grueso) in enumerate([(d, 1.1) for d in dentro] + [(d, 1.5) for d in fuera]):
        dirr = np.array((0.0, math.cos(math.radians(ang)), math.sin(math.radians(ang))))
        base = np.array((0.0, y, z + DV)) - dirr * (ly / 2.0 + (1.0 if k >= len(dentro) else 0.0))
        disco_en_espinosaurio(m, 'vela', T(*base) @ B.girar((ang, 0, 0)), lz, ly, grueso + 0.06 * k, disco_v)

    # ------------------------------------------------------------------------------------------------------------------
    #  La cabeza: el cráneo sobre el frente del cuello, el ojo arriba y delante, el cuerno encima, el hocico que baja
    #  un poco con la cresta, y la boca muy abierta.
    # ------------------------------------------------------------------------------------------------------------------
    m.parte('cabeza', 'cuerpo', (0, 38, ZF - 2))
    colores_ojo = {'g': np.array((143, 199, 108), float), 'k': np.array((24, 40, 22), float),
                   'p': np.array((126, 101, 60), float)}
    # El cráneo, de Z 22 a 33 y de Y 42,2 a 48,3, con la tapa clara; debajo de su parte de atrás, la quijada (hasta
    # Y 37,3, donde empieza la garganta); la boca se abre desde la comisura (Z ~27).
    zc0, zc1, yc0, yc1 = 22.0, 33.0, 42.2, 48.3
    cara = ojo_en('cara_espinosaurio', piel, (zc1 - zc0, yc1 - yc0), ojo_mapa_espinosaurio(), 0.82, 0.10, colores_ojo)
    m.caja('cabeza', (0, (yc0 + yc1) / 2, (zc0 + zc1) / 2), (8, yc1 - yc0, zc1 - zc0), piel,
           caras={'izq': cara, 'der': cara, 'abajo': paladar, 'arriba': tapa})
    m.caja('cabeza', (0, 39.8, 24.3), (7.6, 5.0, 4.6), piel)
    # El hocico: 6 de ancho y 4,7 de alto, del frente del cráneo a la punta (Z 45,6); su canto de abajo, de Y 40,6 en
    # Z 33 a Y 39,1 en la punta: baja 7°. Los 4 colmillos de la punta, en su 2.ª capa (el 2.º y el 3.º, los más largos).
    Mh = T(0, 42.95, zc1 - 0.5) @ B.girar((7, 0, 0))
    caja_en(m, 'cabeza', Mh, (0, 0, 6.5), (6, 4.7, 13), piel_hocico, caras={'abajo': paladar, 'arriba': tapa})
    colm = colmillos_espinosaurio('colmillos_espinosaurio', DIENTE_ESPINOSAURIO,
                                  ((0.8, 3.0, 0.95), (2.6, 3.8, 0.95), (4.4, 3.6, 0.95), (6.3, 2.4, 0.9)))
    caja_en(m, 'cabeza', Mh, (0, -2.35 - 2.0 + 0.5, 6.55), (6.3, 4.0 + 1.0, 13.1), colm)
    # La cresta: la placa oscura con el borde mostaza y dos discos mostaza, de delante del ojo a la punta. Medidas del
    # icono: la placa, de Z 34 a 39 y hasta Y 48,7; el lóbulo pequeño, en alto (Z 42, Y 47-51); el grande, en la punta
    # (Z 43-49, Y 43-49), que sobresale ~3 por delante del hocico.
    m.caja('cabeza', (0, 45.9, 36.7), (1.0, 5.6, 5.2), placa)
    disco_en_espinosaurio(m, 'cabeza', T(0, 44.0, 42.3), 3, 7, 1.2, disco_r)      # (nace del hocico, Y 44)
    disco_en_espinosaurio(m, 'cabeza', T(0, 42.9, 46.0) @ B.girar((8, 0, 0)), 6, 7, 1.4, disco_r)
    # El cuerno: una placa alta casi negra sobre el frente del cráneo, encima del ojo, echada hacia atrás; baja por
    # delante del cráneo hasta el hocico (en el icono, su mancha oscura llega a la altura del ojo).
    m.caja('cabeza', (0, yc1 + 0.8, zc1 - 1.0), (2.0, 10.4, 4.4), cuerno, rot=(-12, 0, 0))
    # La boca: la mandíbula de abajo, del gozne bajo la nuca a la punta, que baja 27°; crema grisácea por fuera y
    # magenta por dentro con la lengua, la punta en gancho y los dientes pequeños en su 2.ª capa. Medidas del icono:
    # el canto de abajo, de (Z 22,5, Y 37,9) a (Z 43, Y 26,6); el de arriba, de la comisura (Z ~29) a (Z 47, Y 31,5).
    gozne = (0, 41.9, 24.5)
    Mj = quijada(m, 'cabeza', gozne, 27)
    # Se afila hacia la punta como la de un cocodrilo: 6 de ancho atrás y 4 delante (en el icono, la punta no pasa del
    # canto de lejos del hocico).
    caja_en(m, 'mandibula', Mj, (0, -3.1, 6.5), (6.0, 4.4, 13), mandibula, caras={'arriba': lengua})
    caja_en(m, 'mandibula', Mj, (0, -3.4, 18.0), (4.0, 5.0, 12), mandibula, caras={'arriba': lengua})
    caja_en(m, 'mandibula', Mj @ T(0, -0.9, 23.2) @ B.girar((-35, 0, 0)), (0, 0.9, 0.0), (3.6, 2.0, 2.0), mandibula)
    dab = dientes_abajo_espinosaurio('dientes_abajo_espinosaurio', DIENTE_ESPINOSAURIO,
                                     (0.8, 2.6, 5.0, 7.5, 10.0), largo=1.4)
    caja_en(m, 'mandibula', Mj, (0, -0.2, 18.05), (4.3, 1.4, 12.1), dab)
    # (Como la ficha: 2 en la punta y 4-5 pequeños por el canto de dentro; aquí, 3 delante y 2 atrás.)
    dab2 = dientes_abajo_espinosaurio('dientes_abajo2_espinosaurio', DIENTE_ESPINOSAURIO, (3.5, 8.5), largo=1.2)
    caja_en(m, 'mandibula', Mj, (0, -0.2, 6.55), (6.3, 1.4, 13.1), dab2)
    # La pared de dentro de la boca (lámina en el plano del espinazo), magenta: el triángulo de la comisura (Z 29,
    # Y 39,8) a la punta del hocico (Z 45,6, Y 38,5) y a la de la mandíbula (Z 46,5, Y 31,2).
    # (La lámina de sagital() va centrada en su punto y su ancho corre hacia -Z: x = 0 es su punta de delante.)
    pared = boca_lamina_espinosaurio('boca_espinosaurio', BOCA_ESPINOSAURIO, ((0.99, 0.97), (0.04, 0.76), (0.0, 0.0)))
    lamina(m, 'cabeza', sagital(0, 31.0, 27.0 + 9.75), 19.5, 10.0, pared)

    # ------------------------------------------------------------------------------------------------------------------
    #  Las patas: el muslo gris verdoso, una caja que asoma 1 px del costado del tronco (en la pila sin IA se ve como una
    #  mancha gris verdosa de x 97 a 110 y de y 100 a 116, más apagada que el tronco; la versión con IA la borra), la
    #  canilla amarilla con 3 rayas (de Y 1,6 a 9,6: en el icono empieza 3 px más abajo de lo que pedía la ficha) y el pie
    #  con 3 garras.
    # ------------------------------------------------------------------------------------------------------------------
    for lado, ld in ((1, 'i'), (-1, 'd')):
        x = lado * 6.0
        xc = lado * 5.5
        m.parte(f'pierna_{ld}', 'cuerpo', (x, 22, 1.0))
        m.caja(f'pierna_{ld}', (x, 17.15, 1.2), (6, 14.7, 6), muslo)
        m.parte(f'cana_{ld}', f'pierna_{ld}', (xc, 9.6, 0))
        m.caja(f'cana_{ld}', (xc, 5.6, 0.0), (4, 8, 4), canilla)
        m.caja(f'cana_{ld}', (xc, 0.8, 0.6), (4.6, 1.6, 4.6), pie)
        lamina(m, f'cana_{ld}', T(xc, 2.6, 2.9) @ B.girar((0, -90, 0)), 3.0, 2.6, garra, abajo=True, x0=-0.4)
        lamina(m, f'cana_{ld}', T(xc, 2.6, 2.9), 5.0, 2.6, garra, abajo=True)

    # ------------------------------------------------------------------------------------------------------------------
    #  Los brazos: amarillos con rayas, cuelgan rectos bajo el pecho; las manos casi negras con 3 garras.
    # ------------------------------------------------------------------------------------------------------------------
    for lado, ld in ((1, 'i'), (-1, 'd')):
        x = lado * 7.0
        za = 19.5
        m.parte(f'brazo_{ld}', 'cuerpo', (x, 21, za))
        m.caja(f'brazo_{ld}', (x, 17.0, za), (4, 8, 4), brazo)
        m.caja(f'brazo_{ld}', (x, 10.6, za + 0.3), (4.4, 5.6, 4.4), mano)
        lamina(m, f'brazo_{ld}', T(x, 7.8, za + 2.1) @ B.girar((0, -90, 0)), 3.0, 2.2, garra, abajo=True, x0=-0.6)
        lamina(m, f'brazo_{ld}', T(x, 7.8, za + 2.1), 4.0, 2.2, garra, abajo=True)

    m.mirar(('cabeza', 0.6))
    anims_espinosaurio(m)
    return m


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
def anims_espinosaurio(m):
    """Las animaciones (en los ejes del boceto: giro positivo en X = la punta hacia abajo; en Y = hacia su izquierda).

    reposo    respira (el tronco sube y baja), la cola se mece despacio en sus dos tramos, la cabeza mira a un lado y
              a otro y la boca se abre y se cierra un poco
    andar     paso corto de terópodo de patas cortas: el muslo adelanta y atrasa, la rodilla solo se dobla al levantar
              el pie; el tronco se balancea y sube y baja; la cola ondula a contrapaso; los brazos se mecen
    correr    lo mismo, más deprisa y más largo, echado hacia delante y con la cabeza baja
    ataque    el mordisco con Veneno: echa la cabeza atrás abriendo más la boca y la lanza cerrándola de golpe
    especial  el rugido: la cabeza arriba, la boca abierta del todo, el pecho arriba, la vela que tiembla, los brazos
              abiertos y la cola levantada
    especial2 el golpe de mandíbula de lado («rompe todo a su paso»): gira la cabeza a un lado con la boca abierta y la
              barre al otro cerrándola de golpe, con el tronco y la cola a contragolpe
    aparece   se levanta de agachado, sacude la vela y abre la boca
    muerte    se desploma de lado, con la cabeza y la cola caídas"""
    lados = ((1, 'i'), (-1, 'd'))
    r = m.anim('reposo', 4.0, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.35, periodo=4.0)
    r.onda('cuerpo', 'r', 0, -0.8, periodo=4.0)
    for lado, ld in lados:
        r.onda(f'pierna_{ld}', 'r', 0, 0.8, periodo=4.0)
        r.onda(f'brazo_{ld}', 'r', 0, 3.0, periodo=4.0, fase=0.2)
    r.onda('cola', 'r', 1, 4.0, periodo=4.0)
    r.onda('cola2', 'r', 1, 6.0, periodo=4.0, fase=0.15)
    r.onda('vela', 'r', 2, 0.8, periodo=4.0, fase=0.3)
    r.rot('cabeza', [(0, 0, 0, 0), (0.8, -2, 12, 0), (1.6, 0, 12, 0), (2.0, 0, 0, 0), (2.8, -2, -12, 0),
                     (3.6, 0, -12, 0), (4.0, 0, 0, 0)])
    r.onda('mandibula', 'r', 0, 3.0, periodo=2.0, base=-1.0)

    for nombre, largo, amp, inclina in (('andar', 1.2, 1.0, 0.0), ('correr', 0.75, 1.4, 6.0)):
        a = m.anim(nombre, largo, bucle=True)
        for k, (lado, ld) in enumerate(lados):
            f = 0.5 * k
            a.onda(f'pierna_{ld}', 'r', 0, 22 * amp, periodo=largo, fase=f, base=-inclina)
            # La rodilla solo se dobla al adelantar la pata (el pie, en el aire); apoyada, recta.
            a.onda(f'cana_{ld}', 'r', 0, 24 * amp, periodo=largo, fase=f - 0.25, forma=lambda v: max(0.0, v))
            a.onda(f'brazo_{ld}', 'r', 0, 9 * amp, periodo=largo, fase=f + 0.5, base=-inclina * 0.5)
        a.onda('cuerpo', 'r', 2, 2.5 * amp, periodo=largo)
        a.onda('cuerpo', 'r', 1, 2.0 * amp, periodo=largo, fase=0.25)
        a.onda('cuerpo', 'r', 0, 1.5 * amp, periodo=largo / 2, base=inclina)
        a.onda('cuerpo', 'm', 1, 0.6 * amp, periodo=largo / 2)
        a.onda('cola', 'r', 1, 7 * amp, periodo=largo, fase=0.5)
        a.onda('cola2', 'r', 1, 10 * amp, periodo=largo, fase=0.62)
        a.onda('cabeza', 'r', 0, 3 * amp, periodo=largo / 2, fase=0.25, base=inclina * 0.8)
        a.onda('vela', 'r', 2, 1.0 * amp, periodo=largo, fase=0.1)

    at = m.anim('ataque', 0.7)
    at.rot('cabeza', [(0, 0, 0, 0), (0.22, -18, 0, 0), (0.36, 12, 0, 0), (0.5, 8, 0, 0), (0.7, 0, 0, 0)])
    at.mov('cabeza', [(0, 0, 0, 0), (0.22, 0, 1, -1.5), (0.36, 0, -1, 3), (0.7, 0, 0, 0)])
    # La boca, más abierta al echarse atrás y cerrada de golpe (hasta el canto del hocico) al morder.
    at.rot('mandibula', [(0, 0, 0, 0), (0.22, 14, 0, 0), (0.34, -20, 0, 0), (0.5, -20, 0, 0), (0.7, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.22, -4, 0, 0), (0.36, 5, 0, 0), (0.7, 0, 0, 0)])
    for lado, ld in lados:
        at.rot(f'pierna_{ld}', [(0, 0, 0, 0), (0.22, 4, 0, 0), (0.36, -5, 0, 0), (0.7, 0, 0, 0)])
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.22, 10, 0, 0), (0.36, -25, 0, 0), (0.7, 0, 0, 0)])
    at.rot('cola', [(0, 0, 0, 0), (0.22, 0, 6, 0), (0.36, 0, -8, 0), (0.7, 0, 0, 0)])

    e = m.anim('especial', 1.6)
    e.rot('cuerpo', [(0, 0, 0, 0), (0.35, -9, 0, 0), (1.15, -9, 0, 0), (1.6, 0, 0, 0)])
    for lado, ld in lados:
        # Las patas, al revés que el tronco: los pies no se mueven del suelo.
        e.rot(f'pierna_{ld}', [(0, 0, 0, 0), (0.35, 9, 0, 0), (1.15, 9, 0, 0), (1.6, 0, 0, 0)])
        e.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.35, -30, 0, lado * 22), (1.15, -30, 0, lado * 22), (1.6, 0, 0, 0)])
    e.rot('cabeza', [(0, 0, 0, 0), (0.35, -26, 0, 0), (0.55, -26, 5, 0), (0.75, -26, -5, 0), (0.95, -26, 5, 0),
                     (1.15, -26, 0, 0), (1.6, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.35, 20, 0, 0), (1.15, 20, 0, 0), (1.6, 0, 0, 0)])
    e.onda('vela', 'r', 2, 1.8, periodo=0.16)
    # La cola, al revés que el tronco y algo más (la punta ya toca el suelo): queda un poco levantada y se mece.
    e.rot('cola', [(0, 0, 0, 0), (0.35, 12, 4, 0), (0.75, 12, -4, 0), (1.15, 12, 0, 0), (1.6, 0, 0, 0)])
    e.rot('cola2', [(0, 0, 0, 0), (0.35, 3, 6, 0), (0.75, 3, -6, 0), (1.15, 3, 0, 0), (1.6, 0, 0, 0)])

    e2 = m.anim('especial2', 0.9)
    e2.rot('cabeza', [(0, 0, 0, 0), (0.25, 6, 28, 0), (0.45, 10, -32, -6), (0.6, 8, -32, -6), (0.9, 0, 0, 0)])
    e2.rot('mandibula', [(0, 0, 0, 0), (0.25, 14, 0, 0), (0.42, -20, 0, 0), (0.6, -20, 0, 0), (0.9, 0, 0, 0)])
    e2.rot('cuerpo', [(0, 0, 0, 0), (0.25, 0, 8, 0), (0.45, 2, -10, 0), (0.9, 0, 0, 0)])
    e2.rot('cola', [(0, 0, 0, 0), (0.25, 0, -8, 0), (0.45, 0, 10, 0), (0.9, 0, 0, 0)])
    e2.rot('cola2', [(0, 0, 0, 0), (0.3, 0, -10, 0), (0.5, 0, 12, 0), (0.9, 0, 0, 0)])
    for lado, ld in lados:
        e2.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.45, -15, 0, 0), (0.9, 0, 0, 0)])

    ap = m.anim('aparece', 1.2)
    ap.mov('cuerpo', [(0, 0, -6, 0), (0.6, 0, -1, 0), (0.8, 0, 0, 0), (1.2, 0, 0, 0)])
    ap.rot('cuerpo', [(0, 10, 0, 0), (0.6, 2, 0, 0), (0.8, -3, 0, 0), (1.2, 0, 0, 0)])
    for lado, ld in lados:
        ap.rot(f'pierna_{ld}', [(0, -40, 0, 0), (0.6, -10, 0, 0), (0.8, 3, 0, 0), (1.2, 0, 0, 0)])
        ap.rot(f'cana_{ld}', [(0, 60, 0, 0), (0.6, 15, 0, 0), (0.8, 0, 0, 0), (1.2, 0, 0, 0)])
    ap.rot('cabeza', [(0, 15, 0, 0), (0.6, 0, 0, 0), (0.8, -12, 0, 0), (1.2, 0, 0, 0)])
    ap.rot('mandibula', [(0, -20, 0, 0), (0.6, 0, 0, 0), (0.8, 12, 0, 0), (1.2, 0, 0, 0)])
    ap.onda('vela', 'r', 2, 1.5, periodo=0.2)

    d = m.anim('muerte', 1.2)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.35, 6, 0, 0), (1.2, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (0.35, 0, -1, 0), (1.2, 0, -6, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.5, -15, 0, 0), (1.2, 14, 0, 0)])
    d.rot('mandibula', [(0, 0, 0, 0), (0.5, 20, 0, 0), (1.2, 6, 0, 0)])
    d.rot('cola', [(0, 0, 0, 0), (1.2, 4, 10, 0)])
    d.rot('cola2', [(0, 0, 0, 0), (1.2, 4, 12, 0)])
    for lado, ld in lados:
        d.rot(f'pierna_{ld}', [(0, 0, 0, 0), (1.2, -15, 0, 0)])
        d.rot(f'brazo_{ld}', [(0, 0, 0, 0), (1.2, -30, 0, 0)])

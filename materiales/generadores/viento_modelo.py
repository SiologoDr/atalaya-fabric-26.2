"""
Boceto 3D de la Mariposa del Vendaval (jefe elemental del aire).

Una polilla gigante de tormenta que flota erguida, de cara a los jugadores:
cuerpo de quitina azul pizarra con collar de pelaje, ojos compuestos de hielo
encendido bajo un ceno oscuro, colmillos curvos, antenas plumosas y el "ojo
de la tormenta" girando en el pecho. Cuatro alas de viento, translucidas, con
ocelos en forma de ciclon y vetas que fluyen hacia fuera; las de abajo acaban
en colas largas, como la mariposa luna. Del abdomen cuelgan dos cintas de
viento.

Malla de cajas al estilo Minecraft, en pixeles de modelo (16 = 1 bloque, Y
hacia abajo, el frente mira a -Z), con materiales en mosaico para el cuerpo e
imagenes estiradas para las alas, el nucleo y las cintas (con la forma en el
alfa). Es un boceto para decidir forma, tamano y color; la textura final del
juego se hace despues.

Medidas: unos 26 bloques de envergadura y 16 de alto con las alas en alto;
flota con el torax a unos 9 bloques del suelo.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm

_hex = nm._hex
_loseta = nm._loseta


def _rampa(*hs):
    return [_hex(h) for h in hs]


# ----------------------------------------------------------------------
#  Paletas por fase: la tormenta se oscurece y las alas se rasgan
# ----------------------------------------------------------------------
FASES = {
    1: dict(nombre='Brisa',
            quitina=_rampa('141a26', '1f2738', '2b3550', '3c4a6c', '56688f'),
            pelaje=_rampa('7d8aa6', '9aa7c0', 'b8c3d7', 'd5dde9', 'eef3f8'),
            membrana=(214, 234, 252), alfa=118, vena=(70, 96, 140), costa=(24, 34, 58),
            brillo_c='f2ffff', brillo_b='5fd2ff', rayos=0.0, rasgado=0.0),
    2: dict(nombre='Rafaga',
            quitina=_rampa('12162a', '1c2140', '272e58', '363f78', '4d58a0'),
            pelaje=_rampa('6f78a2', '8b94bc', 'a8b0d4', 'c6cce6', 'e4e8f6'),
            membrana=(188, 202, 246), alfa=132, vena=(60, 66, 136), costa=(22, 24, 62),
            brillo_c='eef0ff', brillo_b='7f8cff', rayos=0.0, rasgado=0.06),
    3: dict(nombre='Tempestad',
            quitina=_rampa('100f22', '191734', '25204a', '342c66', '4a3e8a'),
            pelaje=_rampa('5f5a86', '78729e', '948eb8', 'b2acd2', 'd4d0ea'),
            membrana=(160, 154, 220), alfa=146, vena=(52, 40, 110), costa=(20, 14, 48),
            brillo_c='fff7d6', brillo_b='b07cff', rayos=0.55, rasgado=0.16),
    4: dict(nombre='Ojo de la tormenta',
            quitina=_rampa('0b0a14', '13111f', '1d1930', '2a2446', '3d3462'),
            pelaje=_rampa('4a4660', '5e5978', '757092', '908aac', 'b0aac8'),
            membrana=(112, 104, 160), alfa=166, vena=(30, 24, 66), costa=(10, 8, 26),
            brillo_c='ffffff', brillo_b='ff4fd8', rayos=1.0, rasgado=0.32),
}

# ----------------------------------------------------------------------
#  Imagenes con forma (alas, nucleo, cintas)
# ----------------------------------------------------------------------
ALA_W, ALA_H = 72, 48         # ala de arriba, en texels
COLA_W, COLA_H = 56, 72       # ala de abajo, con su cola


def _dentro(poly, x, y):
    c = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            c = not c
    return c


def _dist_seg(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-12)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _linea(im, x0, y0, x1, y1, col, gl=None):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    H, W = im.shape[:2]
    for i in range(n + 1):
        t = i / n
        x, y = int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t)
        if 0 <= x < W and 0 <= y < H and im[y, x, 3] > 0:
            im[y, x] = col
            if gl is not None:
                gl[y, x] = col


def _espiral(im, gl, cx, cy, R, P, aro=True):
    """El ocelo y el nucleo: un ciclon con su ojo, que brilla."""
    H, W = im.shape[:2]
    for y in range(H):
        for x in range(W):
            dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if dd > R or im[y, x, 3] == 0:
                continue
            if aro and dd > R * 0.82:
                im[y, x] = (*P['costa'], 240)
            elif aro and dd > R * 0.64:
                im[y, x] = (238, 246, 255, 235)
                gl[y, x] = (150, 190, 220, 255)
            else:
                ang = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
                brazo = (ang - 2.4 * math.log(max(dd, 0.4) / R)) % math.pi
                if brazo < 1.05 or dd < R * 0.16:
                    c = _hex(P['brillo_b']) if dd > R * 0.24 else _hex(P['brillo_c'])
                    im[y, x] = (*c, 255)
                    gl[y, x] = (*c, 255)
                else:
                    im[y, x] = (*P['costa'], 235)


def _ala(W, H, poly, venas, ocelo, fase, semilla):
    """Un ala: membrana translucida que se aclara hacia fuera, con vetas de
    viento que fluyen del cuerpo al borde; venas, costa oscura, margen de
    festones que brillan, el ocelo en forma de ciclon y, en las fases altas,
    rayos y desgarros. Devuelve (imagen, brillo)."""
    P = FASES[fase]
    r = random.Random(semilla)
    im = np.zeros((H, W, 4), np.uint8)
    gl = np.zeros((H, W, 4), np.uint8)
    poly = [(u * W, v * H) for u, v in poly]
    mem = np.array(P['membrana'], float)
    blanco = np.array((246, 251, 255), float)
    for y in range(H):
        for x in range(W):
            if not _dentro(poly, x + 0.5, y + 0.5):
                continue
            d = min(_dist_seg(x + 0.5, y + 0.5, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
            hacia_fuera = x / W
            col = mem * (0.84 + 0.12 * r.random()) * (1 - 0.25 * hacia_fuera) + blanco * 0.25 * hacia_fuera
            a = P['alfa'] + r.randint(-8, 8)
            if d < 1.6:
                col, a = np.array(P['costa'], float), 236
            elif d < 4.0:
                col = mem * 0.6
                a = P['alfa'] + 45
                if (x + y * 2) % 11 in (0, 1):
                    col, a = blanco, 225
                    gl[y, x] = (150, 200, 235, 255)
            im[y, x] = (*np.clip(col, 0, 255).astype(int), int(np.clip(a, 0, 255)))
    # vetas de viento: trazos largos y claros que fluyen del cuerpo al borde
    ru, rv = venas[0][0][0] * W, venas[0][0][1] * H
    for _ in range(22):
        x, y = r.uniform(0.15, 0.7) * W, r.uniform(0.1, 0.9) * H
        if not _dentro(poly, x, y):
            continue
        dx, dy = x - ru, y - rv
        n = math.hypot(dx, dy) + 1e-6
        largo = r.uniform(5, 11)
        _linea(im, x, y, x + dx / n * largo, y + dy / n * largo + r.uniform(-1, 1), (236, 246, 255, P['alfa'] + 70))
    for (u0, v0), (u1, v1) in venas:
        _linea(im, u0 * W, v0 * H, u1 * W, v1 * H, (*P['vena'], 230))
    cu, cv, rad = ocelo
    _espiral(im, gl, cu * W, cv * H, rad * W, P)
    if P['rayos'] > 0:
        for _ in range(int(2 + 5 * P['rayos'])):
            x, y = r.uniform(0.08, 0.45) * W, r.uniform(0.25, 0.75) * H
            for _ in range(r.randint(8, 16)):
                nx, ny = x + r.uniform(1.5, 4.0), y + r.uniform(-2.5, 2.5)
                _linea(im, x, y, nx, ny, (*_hex(P['brillo_c']), 255), gl)
                x, y = nx, ny
    if P['rasgado'] > 0:
        for _ in range(int(42 * P['rasgado'])):
            x, y = r.uniform(0.45, 1.0) * W, r.uniform(0.0, 1.0) * H
            rr = r.uniform(1.0, 3.6)
            for yy in range(int(y - rr), int(y + rr) + 1):
                for xx in range(int(x - rr), int(x + rr) + 1):
                    if 0 <= xx < W and 0 <= yy < H and math.hypot(xx - x, yy - y) <= rr:
                        im[yy, xx, 3] = 0
                        gl[yy, xx, 3] = 0
    for _ in range(30):                     # el borde se deshace en estelas
        y = r.randint(0, H - 1)
        fila = np.nonzero(im[y, :, 3])[0]
        if len(fila) == 0:
            continue
        x0 = fila[-1] + 1
        for k in range(r.randint(2, 8)):
            if x0 + k < W:
                im[y, x0 + k] = (232, 244, 255, max(0, 130 - k * 16))
    return im, gl


POLY_SUP = [(0.0, 0.42), (0.18, 0.2), (0.55, 0.04), (0.93, 0.0), (1.0, 0.08), (0.94, 0.3),
            (0.82, 0.6), (0.62, 0.86), (0.34, 0.98), (0.12, 0.92), (0.0, 0.78)]
VENAS_SUP = [((0.0, 0.6), (0.95, 0.06)), ((0.0, 0.6), (0.9, 0.36)), ((0.0, 0.6), (0.72, 0.74)),
             ((0.0, 0.6), (0.46, 0.92)), ((0.0, 0.6), (0.22, 0.95)), ((0.32, 0.35), (0.62, 0.62))]
OCELO_SUP = (0.56, 0.44, 0.14)
POLY_INF = [(0.0, 0.0), (0.38, 0.02), (0.72, 0.1), (0.9, 0.24), (0.86, 0.42), (0.68, 0.54),
            (0.6, 0.62), (0.66, 0.78), (0.78, 0.92), (0.86, 1.0), (0.7, 0.98), (0.5, 0.82),
            (0.4, 0.66), (0.24, 0.6), (0.06, 0.46), (0.0, 0.3)]
VENAS_INF = [((0.0, 0.15), (0.84, 0.3)), ((0.0, 0.15), (0.62, 0.5)), ((0.0, 0.15), (0.3, 0.56)),
             ((0.5, 0.56), (0.8, 0.96))]
OCELO_INF = (0.46, 0.27, 0.15)


def _nucleo(fase):
    """El ojo de la tormenta del pecho: un ciclon en un rombo de quitina."""
    P = FASES[fase]
    n = 24
    im = np.zeros((n, n, 4), np.uint8)
    gl = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            if abs(x + 0.5 - n / 2) + abs(y + 0.5 - n / 2) <= n / 2:
                im[y, x] = (*P['quitina'][0], 255)
    _espiral(im, gl, n / 2, n / 2, n * 0.42, P, aro=False)
    return im, gl


def _cinta(fase, semilla):
    """Cinta de viento que cuelga del abdomen: se estrecha y se deshace."""
    P = FASES[fase]
    r = random.Random(semilla)
    W, H = 10, 64
    im = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        t = y / H
        c = W / 2 + math.sin(t * 9 + semilla) * 2.2 * t
        ancho = (1 - t) * 3.6 + 0.6
        for x in range(W):
            if abs(x + 0.5 - c) <= ancho:
                a = int(200 * (1 - t) + 30)
                col = np.array(P['membrana']) * (0.8 + 0.2 * r.random()) * (1 - 0.3 * t) + 60 * t
                im[y, x] = (*np.clip(col, 0, 255).astype(int), a)
    return im, np.zeros_like(im)


_IMAGENES = {}


def imagenes(fase=1):
    """Las imagenes de las piezas planas (y su brillo); las de la derecha, en espejo."""
    if fase not in _IMAGENES:
        sup, gsup = _ala(ALA_W, ALA_H, POLY_SUP, VENAS_SUP, OCELO_SUP, fase, 7)
        inf, ginf = _ala(COLA_W, COLA_H, POLY_INF, VENAS_INF, OCELO_INF, fase, 8)
        nuc, gnuc = _nucleo(fase)
        c1, g1 = _cinta(fase, 1)
        c2, g2 = _cinta(fase, 2)
        _IMAGENES[fase] = {
            'ala_sup_izq': (sup, gsup), 'ala_sup_der': (sup[:, ::-1].copy(), gsup[:, ::-1].copy()),
            'ala_inf_izq': (inf, ginf), 'ala_inf_der': (inf[:, ::-1].copy(), ginf[:, ::-1].copy()),
            'nucleo_img': (nuc, gnuc),
            'cinta_izq': (c1, g1), 'cinta_der': (c2, g2),
        }
    return _IMAGENES[fase]


TRANSLUCIDOS = {'ala_sup_izq', 'ala_sup_der', 'ala_inf_izq', 'ala_inf_der', 'cinta_izq', 'cinta_der'}
PLANOS = TRANSLUCIDOS | {'nucleo_img'}


def materiales(fase=1):
    """Losetas de 16x16 para el cuerpo, en la paleta de la fase."""
    P = FASES[fase]
    Q, F = P['quitina'], P['pelaje']
    bc, bb = _hex(P['brillo_c']), _hex(P['brillo_b'])

    def quitina(x, y, r):
        if x % 5 == 0 or y % 6 == 0:
            return Q[0]
        if (x % 5 == 1) or (y % 6 == 1):
            return Q[3]
        return Q[r.choice([1, 2, 2, 2])]

    def quitina_osc(x, y, r):
        return Q[r.choice([0, 0, 1, 1, 2])]

    def pelaje(x, y, r):
        b = r.choice([1, 2, 2, 3, 3])
        if (x * 3 + y) % 7 == 0:
            b = 4
        if (x + y * 2) % 11 == 0:
            b = 0
        return F[b]

    def anillos(x, y, r):
        # el abdomen: placas oscuras y una franja de pelo cada tres
        if y % 8 == 6:
            return F[r.choice([0, 1])]
        return Q[r.choice([1, 2, 2]) if x % 4 else 0]

    def ojo_compuesto(x, y, r):
        # facetas: celdas brillantes con su junta, mas oscuras hacia el borde
        borde = max(abs(x - 7.5), abs(y - 7.5)) / 7.5
        if x % 3 == 0 or y % 3 == 0:
            return tuple(int(bb[i] * 0.3) for i in range(3))
        k = max(0.0, 1 - 1.3 * borde)
        base = tuple(bb[i] * 0.62 for i in range(3))
        return tuple(int(base[i] + (bc[i] - base[i]) * k * 0.8) for i in range(3))

    return {
        'quitina': _loseta(101, quitina),
        'quitina_osc': _loseta(102, quitina_osc),
        'pelaje': _loseta(103, pelaje),
        'anillos': _loseta(104, anillos),
        'ojo': _loseta(110, ojo_compuesto),
        'brillo': _loseta(111, nm.emisivo(P['brillo_c'], P['brillo_b'])),
    }


EMISIVOS = {'ojo', 'brillo', 'nucleo_img'}

# ----------------------------------------------------------------------
#  El esqueleto
# ----------------------------------------------------------------------
nodo = nm.nodo

TAM_SUP = (200, 132)    # px de modelo: largo y alto del ala de arriba
TAM_INF = (128, 146)


def _plano(nombre, x0, y0, w, h, z=0.0):
    return ((x0, y0, z, w, h, 0.0), nombre)


def _ala_nodo(lado, cual, off, rot):
    s = lado
    nombre = f'ala_{cual}_{"izq" if s > 0 else "der"}'
    W, H = TAM_SUP if cual == 'sup' else TAM_INF
    v0 = -H * (0.42 if cual == 'sup' else 0.08)
    return nodo(nombre, off, rot, [_plano(nombre, 0.0 if s > 0 else -W, v0, W, H)])


def _antena(lado):
    s = lado
    lado_ = 'izq' if s > 0 else 'der'
    barbas = []
    for i in range(13):
        L = 10 - abs(i - 5) * 0.9
        y = -8 - i * 4.4
        barbas.append(((0.8, y, -0.6, L, 1.4, 1.2), 'pelaje'))
        barbas.append(((-0.8 - L, y, -0.6, L, 1.4, 1.2), 'pelaje'))
    return nodo('antena_' + lado_, (8 * s, -24, -6), (-30, 0, 24 * s), [
        ((-1.4, -64, -1.4, 2.8, 64, 2.8), 'quitina_osc'), *barbas,
    ], [
        nodo('antena_punta_' + lado_, (0, -64, 0), (-46, 0, -12 * s), [
            ((-1, -14, -1, 2, 14, 2), 'quitina_osc'), ((-1.5, -17, -1.5, 3, 3, 3), 'brillo')]),
    ])


def _pata(lado, i):
    s = lado
    nom = f'pata{i}_{"izq" if s > 0 else "der"}'
    # las de delante en alto, como un insecto de presa; las demas recogidas
    rot = [(-38, 0, 34 * s), (-6, 0, 52 * s), (30, 0, 52 * s)][i]
    return nodo(nom, (17 * s, -8 + i * 13, -8 + i * 4), rot, [((-2, 0, -2, 4, 28, 4), 'quitina')], [
        nodo(nom + '_tibia', (0, 28, 0), ((-70, 0, 0) if i == 0 else (50, 0, 0)), [
            ((-1.5, 0, -1.5, 3, 30, 3), 'quitina_osc'),
            *([((-2.5, 6, -2, 1, 16, 1), 'pelaje')] if i == 0 else []),
        ], [
            nodo(nom + '_garra', (0, 30, 0), (34, 0, 0), [((-2, 0, -0.75, 4, 8, 1.5), 'quitina')]),
        ]),
    ])


def _colmillo(lado):
    s = lado
    lado_ = 'izq' if s > 0 else 'der'
    return nodo('colmillo_' + lado_, (5 * s, -3, -14), (-12, 0, -16 * s), [((-1.6, 0, -1.6, 3.2, 10, 3.2), 'quitina_osc')], [
        nodo('colmillo_punta_' + lado_, (0, 10, 0), (-30, 0, 34 * s), [((-1.1, 0, -1.1, 2.2, 8, 2.2), 'pelaje')]),
    ])


def esqueleto(altura=9.0):
    """altura: bloques del suelo al centro del torax."""
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        nodo('cuerpo', (0, 24 - altura * 16, 0), (0, 0, 0), [], [
            nodo('torax', (0, 0, 0), (-8, 0, 0), [
                ((-21, -24, -16, 42, 48, 32), 'quitina'),
                ((-24, -29, -19, 48, 17, 38), 'pelaje'),             # el collar de pelaje
                ((-28, -26, -8, 8, 14, 24), 'pelaje'),               # mechones de los hombros
                ((20, -26, -8, 8, 14, 24), 'pelaje'),
                ((-15, -9, -17.2, 30, 30, 2), 'quitina_osc'),        # peto
                _plano('nucleo_img', -11, -5, 22, 22, -17.4),         # el ojo de la tormenta
                ((-19, 22, -15, 38, 4, 30), 'pelaje'),               # pelo de la cintura
            ], [
                nodo('cabeza', (0, -27, -5), (12, 0, 0), [
                    ((-16, -26, -14, 32, 26, 27), 'quitina'),
                    ((-18, -31, -7, 36, 9, 22), 'pelaje'),            # cresta
                    ((-5, -7, -15, 10, 7, 2), 'quitina_osc'),         # la boca
                ], [
                    # ojos compuestos, rasgados hacia el centro: mirada de presa
                    nodo('ojo_izq', (12, -14, -12), (0, 0, -18), [((-5, -8, -4, 10, 15, 13), 'ojo')]),
                    nodo('ojo_der', (-12, -14, -12), (0, 0, 18), [((-5, -8, -4, 10, 15, 13), 'ojo')]),
                    # el ceno: dos placas oscuras inclinadas sobre los ojos
                    nodo('ceno_izq', (8, -21, -16.5), (0, 0, -20), [((-7, -2.5, -1, 15, 4, 5), 'quitina_osc')]),
                    nodo('ceno_der', (-8, -21, -16.5), (0, 0, 20), [((-8, -2.5, -1, 15, 4, 5), 'quitina_osc')]),
                    _colmillo(1), _colmillo(-1),
                    _antena(1), _antena(-1),
                ]),
                _ala_nodo(1, 'sup', (19, -14, 12), (0, -18, -14)),
                _ala_nodo(-1, 'sup', (-19, -14, 12), (0, 18, 14)),
                _ala_nodo(1, 'inf', (18, 10, 13), (0, -26, 10)),
                _ala_nodo(-1, 'inf', (-18, 10, 13), (0, 26, -10)),
                *[_pata(s, i) for s in (1, -1) for i in range(3)],
                nodo('abdomen', (0, 24, 4), (10, 0, 0), [((-17, 0, -14, 34, 20, 28), 'anillos')], [
                    nodo('abdomen2', (0, 20, 0), (8, 0, 0), [((-14, 0, -11, 28, 18, 22), 'anillos')], [
                        nodo('abdomen3', (0, 18, 0), (8, 0, 0), [((-10.5, 0, -8.5, 21, 17, 17), 'anillos')], [
                            nodo('abdomen4', (0, 17, 0), (10, 0, 0), [((-7, 0, -6, 14, 14, 12), 'anillos')], [
                                nodo('punta', (0, 14, 0), (10, 0, 0), [
                                    ((-3.5, 0, -3, 7, 9, 6), 'quitina'), ((-2, 8, -2, 4, 4, 4), 'brillo'),
                                ], [
                                    nodo('cinta_izq', (1.5, 10, 0), (0, 0, -8), [_plano('cinta_izq', -7, 0, 14, 96)]),
                                    nodo('cinta_der', (-1.5, 10, 0), (0, 70, 10), [_plano('cinta_der', -7, 0, 14, 84)]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ])


# ----------------------------------------------------------------------
#  Dibujo: opaco, piezas translucidas de atras adelante, y su brillo
# ----------------------------------------------------------------------
def quads(raiz, pose, M, planos=None):
    """Como nerea_modelo.quads, pero las piezas planas llevan su imagen entera
    estirada, y de cada una se queda solo la cara de delante (las dos caen en
    el mismo sitio, la de atras en espejo: con una se pinta por los dos lados).
    planos: nombres de las piezas planas (por defecto, las de este diseno)."""
    planos = PLANOS if planos is None else planos
    viejo = set(nm.ESTIRADOS)
    nm.ESTIRADOS.update(planos)
    try:
        todos = nm.quads(raiz, pose, M)
    finally:
        nm.ESTIRADOS.clear()
        nm.ESTIRADOS.update(viejo)
    out, vistas = [], {}
    for P, UV, mat in todos:
        if mat in planos:
            # cada pieza plana sale dos veces seguidas (delante y detras): una basta
            if vistas.get(mat) == len(out):
                continue
            vistas[mat] = len(out) + 1
        out.append((P, UV, mat))
    return out


def dibujar(lienzo, cam, qs, luces, ambiente, fase=1, niebla=None, brillo=1.4, extra=None,
            mats=None, imgs=None, translucidos_=None, emisivos=None):
    """extra: materiales de fuera del bicho (suelo, jugadores...) por nombre.
    mats / imgs / translucidos_ / emisivos: los de otro diseno (B, C); por
    defecto, los de este. Un material puede ser (textura, brillo): se ilumina
    normal y ademas brilla donde la segunda imagen tenga color (vetas de rayo)."""
    mats = materiales(fase) if mats is None else mats
    img = imagenes(fase) if imgs is None else imgs
    trans = TRANSLUCIDOS if translucidos_ is None else translucidos_
    emi = EMISIVOS if emisivos is None else emisivos
    opacos, translucidos = [], []
    for q in qs:
        (translucidos if q[2] in trans else opacos).append(q)
    for P, UV, mat in opacos:
        if mat in img:
            tex, emis = img[mat]
            luz = np.ones(3)
            envolver = False
        else:
            tex = mats[mat] if mat in mats else (extra or nm.MAT)[mat]
            envolver = True
            if isinstance(tex, tuple):
                tex, emis = tex
                luz = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, ambiente)
            elif mat in emi:
                luz, emis = np.ones(3), tex
            else:
                luz, emis = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, ambiente), None
        for tri in ((0, 1, 2), (0, 2, 3)):
            lienzo.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla,
                             brillo=brillo, envolver=envolver)
    translucidos.sort(key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2])
    for P, UV, mat in translucidos:
        tex, gl = img[mat]
        luz = 0.6 + 0.6 * vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, ambiente)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lienzo.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, None, niebla, translucido=1.0)
            lienzo.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], gl, np.ones(3), None, None,
                             aditivo=True, brillo=1.1)


def entidad_a_mundo(x, y, z, guinada, escala=1.0):
    return vr.entidad_a_mundo(x, y, z, guinada, escala)

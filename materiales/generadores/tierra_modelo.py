"""
Boceto 3D de Rajang, el Jaguar de Jade (jefe elemental de la tierra).

Un felino colosal con la anatomia de un dientes de sable de verdad, tallado en
jade por un pueblo antiguo para guardar su templo en lo mas hondo de la
selva: pecho hondo y la joroba de los omoplatos, la cintura recogida, el lomo
que baja hacia la grupa, brazos gruesos y patas traseras en zigzag, la cabeza
baja y adelantada, el hocico largo y dos sables de dos bloques. La piel es
jade con las rosetas del jaguar (el vientre, mas claro).

Encima, los accesorios: la mascara y las hombreras de oro con grecas, una
cresta de cristales de jade por el lomo, el sol de jade en el pecho (por
donde le entro la Maldicion de la Raiz), brazaletes y anillos de oro, y los
ojos y la boca encendidos.

Con cada fase la maldicion le raja el jade (las grietas brillan), el oro se
mancha, los cristales crecen y, en la ultima, el peto revienta.

Malla de cajas al estilo Minecraft, en pixeles de modelo (16 = 1 bloque, Y
hacia abajo, el frente mira a -Z). La piel no se repite: cada cara lleva su
propia textura pintada segun su sitio en el cuerpo (tierra_piel.py), a un
texel por pixel, como el atlas del juego.

Medidas: unos 8 bloques a la cruz, 17 de largo sin la cola y 25 con ella.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm

_hex = nm._hex


def _rampa(*hs):
    return [_hex(h) for h in hs]


def _loseta(semilla, fn, n=32):
    r = random.Random(semilla)
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            t[y, x] = (*fn(x, y, r), 255)
    return t


# ----------------------------------------------------------------------
#  Paletas por fase: la maldicion raja el jade y apaga el oro
# ----------------------------------------------------------------------
FASES = {
    1: dict(nombre='Selva',
            jade=_rampa('0e2a1c', '143a27', '1c4e34', '266444', '387a56'),
            vientre=_rampa('3c6e50', '4a8060', '5a9472', '6ca783', '82ba96'),
            oro=_rampa('5e400e', '8f6418', 'c28d28', 'e2b443', 'f8d97c'),
            grieta=None, ojo=('f0fff4', '42e884'), cristal=('c8ffd8', '2ec870'), boca=('7ee8a4', '0e4a24'),
            sol=('fff3c0', '3ee07a')),
    2: dict(nombre='Grieta',
            jade=_rampa('113222', '18432c', '20573a', '2a6a48', '3c805a'),
            vientre=_rampa('376449', '447558', '528868', '639a78', '78ad8b'),
            oro=_rampa('543a10', '835c18', 'b08024', 'cfa23a', 'eac868'),
            grieta=('eaffc8', '8cff5a'), ojo=('f2ffe0', '7cff5a'), cristal=('d8ffb4', '58e840'), boca=('d8ffb8', '3aa83a'),
            sol=('f4ffc8', '7cff4a')),
    3: dict(nombre='Raiz',
            jade=_rampa('0b241a', '112f22', '183e2d', '214f39', '316649'),
            vientre=_rampa('2a5040', '35604d', '41705a', '508068', '62927a'),
            oro=_rampa('3a2a10', '584018', '765822', '927034', 'aa8a4c'),
            grieta=('f8ffb0', 'c8ff2a'), ojo=('fbffd0', 'd0ff2a'), cristal=('f2ff9a', 'b8f028'), boca=('f4ffb0', '8ad82a'),
            sol=('fcffd8', 'd0ff3a')),
    4: dict(nombre='Corazon',
            jade=_rampa('061a12', '0b231a', '113024', '183e2f', '255541'),
            vientre=_rampa('1e3c30', '284a3c', '335a48', '3f6a56', '4e7c66'),
            oro=_rampa('281e0e', '3a2c12', '4e3c18', '624c22', '765c30'),
            grieta=('ffffe0', 'e6ff4a'), ojo=('ffffe8', 'f0ff6a'), cristal=('fffbd0', 'ffd83a'), boca=('ffffd0', 'c8f040'),
            sol=('ffffff', 'f0ff5a')),
    5: dict(nombre='Coloso',
            # el espiritu de la tierra que se alza durante el Sello: Rajang hecho de
            # tierra y roca, con la maldicion verde en las grietas
            jade=_rampa('2a1e12', '3a2a1a', '4c3824', '604a30', '76603e'),
            vientre=_rampa('3a2c1c', '4a3a26', '5c4a32', '6e5a3e', '826c4c'),
            oro=_rampa('2a2a24', '3a3a32', '4c4c40', '5e5e50', '727262'),
            grieta=('eaffd0', '7cff5a'), ojo=('f0fff0', '5cff7a'), cristal=('d8ffd0', '4ce070'), boca=('e0ffd0', '4cd060'),
            sol=('f0ffd8', '7cff5a')),
}


def _rosetas(semilla, n=32, cuantas=4):
    """Rosetas de jaguar repartidas por la loseta: anillos rotos de manchas
    alrededor de un centro algo mas oscuro, cada una distinta."""
    r = random.Random(semilla)
    anillo, centro = set(), set()
    for _ in range(cuantas):
        cx, cy = r.uniform(0, n), r.uniform(0, n)
        rad = r.uniform(3.2, 5.2)
        manchas = r.randint(4, 6)
        for k in range(manchas):
            a = k / manchas * math.tau + r.uniform(-0.3, 0.3)
            mx, my = cx + math.cos(a) * rad, cy + math.sin(a) * rad * 0.85
            tam = r.uniform(1.0, 1.9)
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if dx * dx + dy * dy <= tam * tam:
                        anillo.add((int(mx + dx) % n, int(my + dy) % n))
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= (rad - 1.6) ** 2:
                    centro.add((int(cx + dx) % n, int(cy + dy) % n))
    return anillo, centro


def materiales(fase=1):
    """Losetas de 32x32 en la paleta de la fase. Las que pueden brillar (jade
    con grietas, cristal) van como (textura, brillo)."""
    P = FASES[fase]
    J, V, O = P['jade'], P['vientre'], P['oro']
    r_g = random.Random(fase * 11)
    grietas = set()
    if P['grieta']:
        for _ in range({2: 1, 3: 1, 4: 2, 5: 2}[fase]):
            x, y = r_g.randint(0, 31), 0
            while y < 32:
                grietas.add((x % 32, y))
                x += r_g.choice([-1, 0, 0, 1])
                y += 1
    gb = _hex(P['grieta'][1]) if P['grieta'] else None
    anillo, centro = _rosetas(5)
    anillo_v, centro_v = _rosetas(9, cuantas=2)

    def jade(x, y, r):
        if (x, y) in grietas:
            return J[0]
        if (x, y) in anillo:
            return tuple(int(c * 0.45) for c in J[0])
        if (x, y) in centro:
            return J[r.choice([1, 2])]
        return J[r.choice([2, 3, 3, 3, 4])] if (x * 7 + y * 3) % 23 else J[4]

    def jade_brillo(x, y, r):
        return tuple(int(c * 0.6) for c in gb) if (x, y) in grietas else (0, 0, 0)

    def vientre(x, y, r):
        if (x, y) in anillo_v:
            return V[0]
        return V[r.choice([1, 2, 3, 3, 4])]

    def jade_osc(x, y, r):
        if (x, y) in grietas:
            return J[0]
        if (x, y) in anillo:
            return tuple(int(c * 0.4) for c in J[0])
        return J[r.choice([0, 1, 1, 2])]

    def oro(x, y, r):
        # greca escalonada de templo, a dos texeles por pixel
        gx, gy = x // 2, y // 2
        g = ((gx // 2 + gy // 2) % 4 == 0) or (gy % 8 in (0, 7))
        if g:
            return O[1]
        return O[r.choice([2, 3, 3, 4])] if r.random() > 0.05 * fase else O[0]

    def obsidiana(x, y, r):
        if (x + y) % 9 == 0:
            return _hex('5a4a7a')
        return _hex(r.choice(['0c0a14', '15121f', '1d1a2c', '262238']))

    def cristal(x, y, r):
        a, b = _hex(P['cristal'][0]), _hex(P['cristal'][1])
        k = 0.5 + 0.5 * math.sin((x * 0.45 + y * 0.3))
        return tuple(int(b[i] + (a[i] - b[i]) * k * 0.6) for i in range(3))

    def cristal_brillo(x, y, r):
        a = _hex(P['cristal'][1])
        return tuple(int(c * (0.42 + 0.04 * fase)) for c in a) if (x * 3 + y) % 7 else tuple(int(c * 0.8) for c in _hex(P['cristal'][0]))

    def colmillo(x, y, r):
        # los sables: hueso de jade claro, con la veta a lo largo
        base = _rampa('a8d8b8', 'c4ead0', 'e0f6e6')
        return base[r.choice([0, 1, 1, 2])] if x % 6 else base[0]

    def piedra_templo(x, y, r):
        R = _rampa('3a3a2e', '4a4a3a', '5c5c48', '6e6e58', '84846a')
        if x % 16 == 0 or y % 16 == 0:
            return R[0]
        if r.random() < 0.16:
            return _hex(r.choice(['3c5a2a', '4a6a30']))
        return R[r.choice([1, 2, 2, 3, 4])]

    def musgo(x, y, r):
        return _hex(r.choice(['2e4a22', '3c5a2a', '4a6a30', '5c7e3a']))

    return {
        'jade': (_loseta(301, jade), _loseta(301, jade_brillo)) if P['grieta'] else _loseta(301, jade),
        'vientre': _loseta(302, vientre),
        'jade_osc': _loseta(303, jade_osc),
        'oro': _loseta(304, oro),
        'obsidiana': _loseta(305, obsidiana),
        'cristal': (_loseta(306, cristal), _loseta(307, cristal_brillo)),
        'colmillo': _loseta(308, colmillo),
        'ojo': nm._loseta(310, nm.emisivo(*P['ojo'])),
        'boca': nm._loseta(311, nm.emisivo(*P['boca'])),
        'brillo': nm._loseta(312, nm.emisivo(*P['cristal'])),
        'templo': _loseta(320, piedra_templo),
        'musgo': _loseta(321, musgo),
    }


EMISIVOS = {'ojo', 'boca', 'brillo'}


def _sol(fase, n=64):
    """El sol de jade del pecho: un disco de piedra con rayos tallados y el
    ojo de la maldicion en el centro, que brilla mas en cada fase."""
    P = FASES[fase]
    c, b = _hex(P['sol'][0]), _hex(P['sol'][1])
    J = P['jade']
    t = np.zeros((n, n, 4), np.uint8)
    gl = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2, y + 0.5 - n / 2
            d = math.hypot(dx, dy) / (n / 2)
            ang = math.atan2(dy, dx)
            if d > 1.0:
                continue
            if d > 0.86:
                t[y, x] = (*_hex('c28d28'), 255)
            elif d > 0.55:
                rayo = (int((ang + math.pi) / (2 * math.pi) * 16) % 2 == 0)
                t[y, x] = (*(J[3] if rayo else J[1]), 255)
                if rayo and fase >= 2 and 0.6 < d < 0.8:
                    gl[y, x] = (*b, int(120 + 30 * min(fase, 4)))
            elif d > 0.3:
                t[y, x] = (*J[1], 255)
                if abs(d - 0.42) < 0.05:
                    t[y, x] = (*b, 255)
                    gl[y, x] = (*b, 200)
            else:
                k = 1 - d / 0.3
                col = tuple(int(b[i] + (c[i] - b[i]) * k) for i in range(3))
                t[y, x] = (*col, 255)
                gl[y, x] = (*col, int(180 + 15 * min(fase, 4)))
    return t, gl


_IMAGENES = {}


def imagenes(fase=1):
    if fase not in _IMAGENES:
        _IMAGENES[fase] = {'sol_img': _sol(fase)}
    return _IMAGENES[fase]


PLANOS = {'sol_img'}

# ----------------------------------------------------------------------
#  El esqueleto: anatomia de dientes de sable
# ----------------------------------------------------------------------
nodo = nm.nodo


def _plano(nombre, x0, y0, w, h, z=0.0):
    return ((x0, y0, z, w, h, 0.0), nombre)


def _garras(ancho, z0, y0=5):
    """Cuatro dedos con su garra de obsidiana asomando por delante."""
    out = []
    paso = ancho / 4
    for k in range(4):
        x = -ancho / 2 + paso * (k + 0.5)
        out.append(((x - paso * 0.42, y0 - 3, z0 - 3, paso * 0.84, 6, 6), 'jade_osc'))
        out.append(((x - 1.2, y0, z0 - 8, 2.4, 3, 6), 'obsidiana'))
    return out


def _pata_delantera(lado):
    """Brazo en angulo hacia atras (el codo a media altura), antebrazo recto y
    grueso y la zarpa ancha."""
    s = lado
    n = 'izq' if s > 0 else 'der'
    return nodo(f'brazo_{n}', (22 * s, 6, -92), (20, 0, 0), [
        ((-12, -10, -16, 24, 46, 32), 'jade'),                   # hombro y brazo
        ((-13 + 5 * s, -14, -12, 9, 26, 26), 'jade'),            # el musculo del hombro
    ], [
        nodo(f'antebrazo_{n}', (0, 34, -1), (-20, 0, 0), [
            ((-10, 0, -10, 20, 46, 20), 'jade'),
            ((-11, 28, -11, 22, 6, 22), 'oro'),                  # brazalete
            ((-9, 4, 8, 18, 30, 3), 'vientre'),                  # la parte de atras, mas clara
            ((10 if s > 0 else -12.5, 7, -8, 2.5, 16, 16), 'oro'),   # placa de la espiral
        ], [
            nodo(f'mano_{n}', (0, 46, -2), (0, 0, 0), [
                ((-13, 0, -16, 26, 10, 26), 'jade_osc'),
                *_garras(26, -16, 5),
            ]),
        ]),
    ])


def _pata_trasera(lado):
    """El anca potente, la rodilla adelante, el corvejon atras y el tarso casi
    recto: la pata en zigzag de un felino."""
    s = lado
    n = 'izq' if s > 0 else 'der'
    return nodo(f'muslo_{n}', (22 * s, 2, 46), (-30, 0, 0), [
        ((-14, -14, -18, 28, 52, 36), 'jade'),                   # el anca
        ((14 if s > 0 else -17, -6, -12, 3, 24, 24), 'oro'),     # placa de la espiral
    ], [
        nodo(f'tibia_{n}', (0, 36, 2), (65, 0, 0), [((-9, 0, -10, 18, 34, 20), 'jade')], [
            nodo(f'tarso_{n}', (0, 32, 0), (-45, 0, 0), [((-7, 0, -8, 14, 28, 16), 'jade'),
                                                         ((-8, 8, -9, 16, 5, 18), 'oro')], [
                nodo(f'pie_{n}', (0, 26, 0), (10, 0, 0), [((-12, 0, -18, 24, 9, 26), 'jade_osc'),
                                                          *_garras(24, -18, 4)]),
            ]),
        ]),
    ])


def _cristal(nombre, x, y, z, alto, ancho, inclina, gira=0.0, ladea=0.0):
    return nodo(nombre, (x, y, z), (inclina, gira, ladea), [
        ((-ancho / 2, -alto, -ancho / 2, ancho, alto, ancho), 'cristal'),
        ((-ancho / 2 - 1.5, -5, -ancho / 2 - 1.5, ancho + 3, 5, ancho + 3), 'jade_osc'),
    ])


def _cumulo(nombre, x, y, z, k, semilla, inclina=-40.0, ladea=0.0):
    """Un cumulo de cristales de jade: uno grande y dos o tres menores
    alrededor, cada uno con su inclinacion, sobre su base de jade."""
    r = random.Random(semilla)
    alto = 30 * k
    hijos = [_cristal(f'{nombre}_a', 0, 0, 0, alto, 10, 0, 0, 0)]
    for j in range(r.choice([2, 3])):
        lado = (-1) ** j
        hijos.append(_cristal(f'{nombre}_{j}', lado * r.uniform(5, 7), 1, r.uniform(-5, 5), alto * r.uniform(0.45, 0.7),
                              r.choice([6, 7, 8]), r.uniform(-14, 14), r.uniform(-20, 20), lado * r.uniform(12, 26)))
    return nodo(nombre, (x, y, z), (inclina, 0, ladea), [((-9, -3, -9, 18, 6, 18), 'jade_osc')], hijos)


def _relieve(semilla, evitar):
    """Bloques sueltos que asoman de la piel (el aire de tallado en bloques de
    las ilustraciones): en el lomo y en los costados del pecho, las costillas y
    el anca. 'evitar': rectangulos (y0, y1, z0, z1) de los costados donde van
    placas de oro."""
    r = random.Random(semilla)
    out = []
    techos = [(-36, -18, 18, -106, -72), (-28, -22, 22, -50, -16), (-24, -18, 18, -12, 18), (-30, -20, 20, 24, 58)]
    for y, x0, x1, z0, z1 in techos:
        for _ in range(6):
            w, d, h = r.choice([4, 6, 8]), r.choice([4, 6, 8]), r.uniform(1.5, 3.5)
            out.append(((r.uniform(x0, x1 - w), y - h, r.uniform(z0, z1 - d), w, h + 2, d), 'jade'))
    costados = [(32, -24, 26, -112, -56), (28, -20, 22, -50, -16), (22, -18, 10, -12, 18), (26, -20, 16, 20, 60)]
    for x, y0, y1, z0, z1 in costados:
        for lado in (1, -1):
            for _ in range(6):
                hh, d, sale = r.choice([4, 6, 8]), r.choice([4, 6, 8]), r.uniform(1.5, 3.0)
                yy, zz = r.uniform(y0, y1 - hh), r.uniform(z0, z1 - d)
                if any(a0 - 2 < yy + hh and yy < a1 + 2 and b0 - 2 < zz + d and zz < b1 + 2 for a0, a1, b0, b1 in evitar):
                    continue
                xx = x - 2 if lado > 0 else -x - sale
                out.append(((xx, yy, zz, sale + 2, hh, d), 'jade'))
    return out


def _cola(fase):
    grosor = [14, 13, 12, 11, 10, 9, 8]
    maza = [nodo('punta_cola', (0, 0, 22), (0, 0, 0), [
        ((-6, -6, 0, 12, 12, 12), 'jade_osc'),
        ((-3.5, -13, 2, 7, 9, 7), 'cristal'), ((-2.5, -17, 7, 5, 7, 5), 'cristal'),
    ])]
    actual = maza
    rots = [-6, 14, 12, 8, 2, -10, -16]
    for i in reversed(range(7)):
        g = grosor[i]
        cajas = [((-g / 2, -g / 2, 0, g, g, 23), 'jade')]
        if i in (1, 4):
            cajas.append(((-g / 2 - 1.5, -g / 2 - 1.5, 8, g + 3, g + 3, 5), 'oro'))
        actual = [nodo(f'cola{i}', (0, 0, 0 if i == 0 else 22), (rots[i], 0, 0), cajas, actual)]
    return actual[0]


def _cabeza(fase):
    """Cabeza de dientes de sable: craneo ancho y bajo, pomulos marcados, hocico
    largo con los belfos colgando sobre los sables, orejas pequenas y la boca
    abierta, encendida por dentro."""
    corona = [_cristal('corona_i', 10, -30, -18, 18, 7, -48, 0, -16), _cristal('corona_d', -10, -30, -18, 18, 7, -48, 0, 16),
              _cumulo('corona_c', 0, -34, -10, 0.85, 7, -56)]
    return nodo('cabeza', (0, 2, -38), (-18, 0, 0), [
        ((-22, -22, -36, 44, 32, 36), 'jade'),                    # craneo
        ((-20, -27, -34, 40, 8, 28), 'jade'),                     # frente, sobre los ojos
        ((-27, -10, -28, 54, 18, 20), 'jade'),                    # pomulos
        ((-13, -14, -60, 26, 20, 28), 'jade'),                    # hocico largo
        ((-14, 4, -58, 28, 6, 24), 'jade_osc'),                   # belfos sobre los sables
        ((-7, -16, -62, 14, 7, 5), 'obsidiana'),                  # nariz
        # la mascara de oro: la placa de la espiral en la frente, las bandas, el
        # puente de la nariz y las carrilleras con su espiral
        ((-12, -34, -39.5, 24, 16, 3), 'oro'),
        ((-23, -30, -37, 11, 6, 9), 'oro'), ((12, -30, -37, 11, 6, 9), 'oro'),
        ((-5, -18, -56, 10, 4, 22), 'oro'),
        ((-30, -12, -28, 3, 16, 16), 'oro'), ((27, -12, -28, 3, 16, 16), 'oro'),
        ((-9, -38, -31, 18, 8, 14), 'oro'),                       # cresta escalonada
        ((-11, 10, -54, 22, 0.8, 30), 'boca'),                    # el paladar, encendido
        # los incisivos de arriba
        *[((x, 9.5, -58.5, 2.6, 3.5, 2.6), 'colmillo') for x in (-6.5, -3, 0.4, 3.9)],
    ], [
        nodo('ojo_izq', (13, -12, -36.6), (0, 0, -16), [((-6, -2, -1, 12, 4, 2), 'ojo')]),
        nodo('ojo_der', (-13, -12, -36.6), (0, 0, 16), [((-6, -2, -1, 12, 4, 2), 'ojo')]),
        nodo('ceno', (0, -17, -37), (0, 0, 0), [((-20, -2, -2, 40, 4, 4), 'jade_osc')]),
        nodo('oreja_izq', (16, -22, -6), (-30, 0, -10), [((-5, -8, -3, 10, 8, 5), 'jade'), ((-6, -3, -4, 12, 2, 7), 'oro')]),
        nodo('oreja_der', (-16, -22, -6), (-30, 0, 10), [((-5, -8, -3, 10, 8, 5), 'jade'), ((-6, -3, -4, 12, 2, 7), 'oro')]),
        nodo('sable_izq', (8, 6, -50), (-8, 0, 3), [((-2.5, 0, -3.5, 5, 28, 6), 'colmillo')], [
            nodo('sable_punta_izq', (0, 28, 0), (18, 0, 0), [((-1.8, 0, -2.5, 3.6, 11, 4), 'colmillo')])]),
        nodo('sable_der', (-8, 6, -50), (-8, 0, -3), [((-2.5, 0, -3.5, 5, 28, 6), 'colmillo')], [
            nodo('sable_punta_der', (0, 28, 0), (18, 0, 0), [((-1.8, 0, -2.5, 3.6, 11, 4), 'colmillo')])]),
        nodo('mandibula', (0, 8, -6), (24, 0, 0), [
            ((-14, 0, -48, 28, 10, 48), 'jade_osc'),
            ((-11, -2, -44, 22, 2, 38), 'boca'),                  # la boca, encendida por dentro
            # los colmillos de abajo y la fila de dientes
            ((-11.5, -9, -46.5, 4, 9, 4), 'colmillo'), ((7.5, -9, -46.5, 4, 9, 4), 'colmillo'),
            *[((x, -3.5, z, 2.4, 3.5, 2.4), 'colmillo') for x in (-11.5, 9.1) for z in (-39, -33, -27, -21)],
            ((-15, 3, -40, 30, 4, 4), 'oro'),                     # la banda de oro de la barbilla
        ]),
        *corona,
    ])


def esqueleto(fase=1):
    """El dientes de sable de pie, mirando a -Z. 'cuerpo' queda a 6 bloques del
    suelo; la cruz, a 8."""
    k = {1: 1.0, 2: 1.12, 3: 1.3, 4: 1.55, 5: 1.4}[fase]
    peto = [] if fase >= 4 else [((-14, -10, -117.5, 28, 26, 3), 'oro')]
    lado_sol = 20 if fase < 4 else 28
    cresta = [_cumulo(f'cresta{i}', 0, y, z, kk * k, 20 + i, inc) for i, (y, z, kk, inc) in enumerate(
        [(-36, -102, 0.75, -36), (-37, -88, 1.05, -40), (-36, -74, 1.0, -44), (-29, -58, 0.85, -48),
         (-28, -42, 0.72, -52), (-25, -26, 0.6, -56), (-25, -8, 0.5, -60), (-31, 12, 0.45, -64)])]
    hombros = [_cumulo(f'hombro_{n}', 26 * s, -24, -98, 0.6 * k, 40 + (s > 0), -30, -30 * s) for s, n in ((1, 'izq'), (-1, 'der'))]
    placas = [(-28, 6, -114, -80), (-18, 10, -44, -16)]
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        nodo('cuerpo', (0, -72, 0), (0, 0, 0), [
            ((-32, -30, -115, 64, 64, 64), 'jade'),               # pecho hondo
            ((-36, -22, -104, 8, 36, 40), 'jade'), ((28, -22, -104, 8, 36, 40), 'jade'),   # los hombros, anchos
            ((-23, -36, -108, 46, 12, 38), 'jade'),               # la joroba de los omoplatos
            ((-28, -28, -52, 56, 56, 38), 'jade'),                # costillas
            ((-22, -24, -14, 44, 38, 34), 'jade'),                # la cintura recogida
            ((-26, -26, 18, 52, 48, 44), 'jade'),                 # cadera y anca
            ((-22, -30, 22, 44, 6, 36), 'jade'),                  # la grupa
            ((-25, 32, -110, 50, 4, 56), 'vientre'),              # pecho y vientre, mas claros
            ((-20, 26, -50, 40, 4, 34), 'vientre'),
            # el oro: las hombreras y las placas del costado con su espiral, la silla del lomo
            ((-40, -28, -114, 4, 34, 34), 'oro'), ((36, -28, -114, 4, 34, 34), 'oro'),
            ((-31, -18, -44, 3, 28, 28), 'oro'), ((28, -18, -44, 3, 28, 28), 'oro'),
            ((-18, -31, -40, 36, 4, 34), 'oro'),
            *_relieve(9, placas),
            *peto,
            _plano('sol_img', -lado_sol / 2, -7, lado_sol, lado_sol, -118.5),
        ], [
            *cresta, *hombros,
            nodo('cuello', (0, -16, -112), (24, 0, 0), [
                ((-20, -22, -42, 40, 42, 44), 'jade'),
                ((-21, 12, -40, 42, 8, 38), 'vientre'),
                ((-22, -24, -12, 44, 5, 9), 'oro'),               # collar
                ((-22, -24, -30, 44, 5, 7), 'oro'),
            ], [_cabeza(fase), _cumulo('cresta_cuello', 0, -22, -24, 0.55 * k, 30, -30)]),
            _pata_delantera(1), _pata_delantera(-1),
            _pata_trasera(1), _pata_trasera(-1),
            nodo('cola_base', (0, -20, 62), (-14, 0, 0), [], [_cola(fase)]),
        ]),
    ])


# ----------------------------------------------------------------------
#  Poses
# ----------------------------------------------------------------------
ACECHO = {
    # al acecho: la cabeza baja, una mano adelantada, el lomo tenso
    'cuello': {'rot': (10, 0, 0)}, 'cabeza': {'rot': (4, 0, 0)}, 'mandibula': {'rot': (-12, 0, 0)},
    'brazo_izq': {'rot': (-16, 0, 0)}, 'antebrazo_izq': {'rot': (12, 0, 0)},
    'brazo_der': {'rot': (12, 0, 0)}, 'antebrazo_der': {'rot': (-6, 0, 0)},
    'muslo_izq': {'rot': (10, 0, 0)}, 'muslo_der': {'rot': (-8, 0, 0)},
    'cola0': {'rot': (14, 0, 0)}, 'cola3': {'rot': (0, 0, 10)}, 'cola5': {'rot': (-10, 0, 0)},
}
RUGIDO = {
    # ruge: la cabeza baja y adelantada, girada hacia la presa, la boca abierta del todo
    'cuerpo': {'rot': (2, 0, 0), 'pos': (0, 4, 0)},
    'cuello': {'rot': (2, -12, 0)}, 'cabeza': {'rot': (-12, -8, 0)}, 'mandibula': {'rot': (22, 0, 0)},
    'oreja_izq': {'rot': (-20, 0, 0)}, 'oreja_der': {'rot': (-20, 0, 0)},
    'brazo_izq': {'rot': (-10, 0, -6)}, 'brazo_der': {'rot': (6, 0, 6)},
    'cola0': {'rot': (-6, 0, 0)}, 'cola2': {'rot': (0, 0, 12)}, 'cola4': {'rot': (-14, 0, 10)},
}
GARRA = {
    # alza la garra para clavarla: el peso atras, la mano en alto
    'cuerpo': {'rot': (-12, 0, 0), 'pos': (0, -4, 6)},
    'brazo_der': {'rot': (-80, 0, 8)}, 'antebrazo_der': {'rot': (40, 0, 0)}, 'mano_der': {'rot': (-30, 0, 0)},
    'cuello': {'rot': (4, 0, 0)}, 'cabeza': {'rot': (0, 0, 0)}, 'mandibula': {'rot': (6, 0, 0)},
    'muslo_izq': {'rot': (14, 0, 0)}, 'muslo_der': {'rot': (14, 0, 0)},
    'cola0': {'rot': (-8, 0, 0)},
}
ALZADO = {
    # el Cataclismo: se alza sobre las patas traseras y ruge al cielo
    'cuerpo': {'rot': (-42, 0, 0), 'pos': (0, -26, 30)},
    'brazo_izq': {'rot': (-40, 0, -10)}, 'brazo_der': {'rot': (-30, 0, 10)},
    'antebrazo_izq': {'rot': (50, 0, 0)}, 'antebrazo_der': {'rot': (40, 0, 0)},
    'muslo_izq': {'rot': (40, 0, 0)}, 'muslo_der': {'rot': (36, 0, 0)},
    'cuello': {'rot': (-4, 0, 0)}, 'cabeza': {'rot': (-24, 0, 0)}, 'mandibula': {'rot': (16, 0, 0)},
    'cola0': {'rot': (40, 0, 0)}, 'cola2': {'rot': (14, 0, 0)},
}
AGAZAPADO = {
    # pegado al suelo antes del Terremoto
    'cuerpo': {'pos': (0, 10, 0), 'rot': (4, 0, 0)},
    'brazo_izq': {'rot': (20, 0, 0)}, 'brazo_der': {'rot': (20, 0, 0)},
    'antebrazo_izq': {'rot': (-30, 0, 0)}, 'antebrazo_der': {'rot': (-30, 0, 0)},
    'muslo_izq': {'rot': (-14, 0, 0)}, 'muslo_der': {'rot': (-14, 0, 0)},
    'cuello': {'rot': (14, 0, 0)}, 'cabeza': {'rot': (-12, 0, 0)}, 'mandibula': {'rot': (-4, 0, 0)},
    'cola0': {'rot': (-12, 0, 0)}, 'cola2': {'rot': (0, 0, 14)}, 'cola4': {'rot': (6, 0, -10)},
}
ANDAR = {
    # el paso: en diagonal, como un felino de verdad
    'brazo_izq': {'rot': (-22, 0, 0)}, 'antebrazo_izq': {'rot': (10, 0, 0)},
    'brazo_der': {'rot': (18, 0, 0)}, 'antebrazo_der': {'rot': (-4, 0, 0)}, 'mano_der': {'rot': (30, 0, 0)},
    'muslo_izq': {'rot': (12, 0, 0)}, 'tibia_izq': {'rot': (10, 0, 0)},
    'muslo_der': {'rot': (-14, 0, 0)}, 'tibia_der': {'rot': (-6, 0, 0)},
    'cuello': {'rot': (6, 0, 0)}, 'mandibula': {'rot': (-16, 0, 0)},
    'cola0': {'rot': (8, 0, 0)}, 'cola4': {'rot': (0, 0, 12)},
}

ZARPAZO = {
    # la Garra Terrestre: clava la zarpa delante, el peso encima, y ruge
    'cuerpo': {'rot': (8, 0, 0), 'pos': (0, 8, -6)},
    'brazo_der': {'rot': (-44, 0, 6)}, 'antebrazo_der': {'rot': (-6, 0, 0)}, 'mano_der': {'rot': (40, 0, 0)},
    'brazo_izq': {'rot': (14, 0, -4)}, 'antebrazo_izq': {'rot': (-16, 0, 0)},
    'muslo_izq': {'rot': (-6, 0, 0)}, 'muslo_der': {'rot': (-10, 0, 0)},
    'cuello': {'rot': (6, -10, 0)}, 'cabeza': {'rot': (-14, -6, 0)}, 'mandibula': {'rot': (20, 0, 0)},
    'cola0': {'rot': (-10, 0, 0)}, 'cola2': {'rot': (0, 0, -14)}, 'cola4': {'rot': (-12, 0, 8)},
}


def quads(raiz, pose, M):
    """Cuadrilateros con la clave de su cara, para la piel pintada."""
    import tierra_piel as tp
    return tp.quads(raiz, pose, M, planos=PLANOS)


def dibujar(lienzo, cam, qs, luces, ambiente, fase=1, niebla=None, brillo=1.4, extra=None):
    """La piel pintada cara por cara (tierra_piel); los ojos, la boca y el
    brillo, con su loseta emisiva; el sol del pecho, con su imagen."""
    import tierra_piel as tp
    mats = materiales(fase)
    pintada = tp.texturas(esqueleto(fase), fase, FASES[fase], PLANOS)
    imgs = imagenes(fase)
    for q in qs:
        P, UV, mat = q[:3]
        clave = q[3] if len(q) > 3 else None
        envolver = True
        if mat in imgs:
            (tex, emis), luz, envolver = imgs[mat], np.ones(3), False
        elif mat in tp.PINTADOS and clave in pintada:
            tex, emis = pintada[clave]
            luz, envolver = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, ambiente), False
        else:
            tex = mats[mat] if mat in mats else (extra or nm.MAT)[mat]
            if isinstance(tex, tuple):
                tex, emis = tex
                luz = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, ambiente)
            elif mat in EMISIVOS:
                luz, emis = np.ones(3), tex
            else:
                luz, emis = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, ambiente), None
        for tri in ((0, 1, 2), (0, 2, 3)):
            lienzo.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla,
                             brillo=brillo, envolver=envolver)


def entidad_a_mundo(x, y, z, guinada, escala=1.0):
    return vr.entidad_a_mundo(x, y, z, guinada, escala)

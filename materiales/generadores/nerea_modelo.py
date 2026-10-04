"""
Boceto 3D de Nerea, Guardian de los Mares (jefe elemental del agua).

Malla de cajas al estilo Minecraft, en pixeles de modelo (16 = 1 bloque, Y
hacia abajo, el frente mira a -Z), pero con MATERIALES en mosaico en vez de un
atlas UV: es un boceto para decidir forma y tamano, no la textura final.

Alto total: ~90 px = 5,6 bloques (el Vigia mide 2,9; un jugador, 1,8).
"""
import math, random
import numpy as np
import vigia_render as vr

# ----------------------------------------------------------------------
#  Materiales: losetas 16x16 pintadas aqui
# ----------------------------------------------------------------------
def _loseta(semilla, fn):
    r = random.Random(semilla)
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            t[y, x] = (*fn(x, y, r), 255)
    return t

def _hex(s):
    s = s.lstrip('#'); return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

def _rampa(*hs):
    return [_hex(h) for h in hs]

PRISMA = _rampa('1d4a46', '2a645d', '3b8075', '5aa596', '8fd0bd')
PRISMA_OSC = _rampa('0f2a2c', '173b3c', '22504d', '2f6660', '3f7f76')
HUESO = _rampa('5c5545', '8a8068', 'b3a98c', 'd3c9aa', 'ece4c8')
ABISMO = _rampa('05070d', '0a0f1a', '120f22', '1a1430', '241a3e')
CORAL_R = _rampa('7a1636', 'a8204a', 'd8336a', 'f2618f', 'ffa3c0')
CORAL_N = _rampa('8a3b10', 'c25a18', 'ea7f26', 'f8a74a', 'ffd08a')
CORAL_P = _rampa('5a1a72', '7e2a9c', 'a243c4', 'c46fe0', 'e3a6f5')
OXIDO = _rampa('2a1a12', '4a2a18', '6e3c1e', '9a5726', 'c47a3a')
ALGA = _rampa('183a14', '245a1c', '347a26', '4c9a34', '6dba4a')
ARENA = _rampa('8f8466', 'a89c79', 'bdb18c', 'cfc39d', 'ddd2b0')

def piedra(rampa, vetas=0.18):
    def f(x, y, r):
        b = r.choice([1, 2, 2, 2, 3])
        if x % 8 == 0 or y % 8 == 0:
            b = 0                      # juntas de bloque
        elif r.random() < vetas:
            b = 4                      # vetas claras
        return rampa[b]
    return f

def hueso(x, y, r):
    b = r.choice([2, 3, 3, 3, 4])
    if r.random() < 0.08 or (x + 2 * y) % 13 == 0:
        b = 1                          # grietas
    return HUESO[b]

def coral(rampa):
    def f(x, y, r):
        if (x * 7 + y * 3) % 5 == 0:
            return rampa[0]            # poros
        return rampa[r.choice([2, 3, 3, 4])]
    return f

def cadena(x, y, r):
    if x in (0, 15) or y in (0, 15):
        return OXIDO[0]
    return OXIDO[r.choice([1, 2, 2, 3, 3, 4])]

def abismo(x, y, r):
    return ABISMO[r.choice([0, 0, 1, 1, 2, 3])] if r.random() > 0.06 else ABISMO[4]

def alga(x, y, r):
    return ALGA[r.choice([1, 2, 3, 3, 4])] if x % 4 else ALGA[0]

def emisivo(c1, c2):
    a, b = _hex(c1), _hex(c2)
    def f(x, y, r):
        d = max(abs(x - 7.5), abs(y - 7.5)) / 7.5
        return tuple(int(a[i] + (b[i] - a[i]) * d) for i in range(3))
    return f

MAT = {
    'prisma': _loseta(1, piedra(PRISMA)),
    'prisma_osc': _loseta(2, piedra(PRISMA_OSC, 0.1)),
    'hueso': _loseta(3, hueso),
    'abismo': _loseta(4, abismo),
    'coral_r': _loseta(5, coral(CORAL_R)),
    'coral_n': _loseta(6, coral(CORAL_N)),
    'coral_p': _loseta(7, coral(CORAL_P)),
    'oxido': _loseta(8, cadena),
    'alga': _loseta(9, alga),
    'arena': _loseta(10, piedra(ARENA, 0.08)),
    'percebe': _loseta(11, lambda x, y, r: HUESO[4] if r.random() < 0.3 else PRISMA_OSC[1]),
    # emisivos: brillan en la oscuridad
    'ojo': _loseta(20, emisivo('eaffff', '3fe0ff')),
    'corazon': _loseta(21, emisivo('ffd0e0', 'e0144c')),
    'punta': _loseta(22, emisivo('d8ffff', '2ec8e8')),
    'sello': _loseta(23, emisivo('fff2b0', '35d0ff')),
    # variantes del final: liberado
    'ojo_libre': _loseta(24, emisivo('fffbe0', 'ffc23a')),
    'corazon_libre': _loseta(25, emisivo('e8fff8', '35e0b0')),
}
EMISIVOS = {'ojo', 'corazon', 'punta', 'sello', 'ojo_libre', 'corazon_libre'}
ESTIRADOS = set()   # materiales que se estiran en vez de repetirse

# ----------------------------------------------------------------------
#  Ayudas de construccion
# ----------------------------------------------------------------------
def nodo(nombre, off, rot, cajas, hijos=()):
    return [nombre, off, rot, list(cajas), list(hijos)]

def cadena_nodo(nombre, inicio, fin, grosor=1.0, mat='oxido'):
    """Cadena de eslabones de inicio a fin (en el espacio del padre)."""
    d = np.array(fin, float) - np.array(inicio, float)
    L = float(np.linalg.norm(d)); d /= L
    a = math.degrees(math.acos(max(-1.0, min(1.0, d[1]))))
    b = math.degrees(math.atan2(d[0], d[2]))
    cajas = []
    paso = 3.2 * grosor
    y = 0.0; k = 0
    while y < L - 1:
        g = grosor
        if k % 2 == 0:
            cajas.append(((-1.5 * g, y, -0.5 * g, 3 * g, 4 * g, 1 * g), mat))
        else:
            cajas.append(((-0.5 * g, y, -1.5 * g, 1 * g, 4 * g, 3 * g), mat))
        y += paso; k += 1
    # Rz*Ry*Rx: con c=0, +Y local apunta a d
    return nodo(nombre, tuple(inicio), (a, b, 0.0), cajas)

def coral_rama(nombre, off, rot, mat, alto=7):
    return nodo(nombre, off, rot, [((-1, -alto, -1, 2, alto, 2), mat)], [
        nodo(nombre + '_a', (0, -alto * 0.55, 0), (0, 0, 38), [((-0.75, -alto * 0.5, -0.75, 1.5, alto * 0.5, 1.5), mat)]),
        nodo(nombre + '_b', (0, -alto * 0.75, 0), (0, 0, -34), [((-0.75, -alto * 0.4, -0.75, 1.5, alto * 0.4, 1.5), mat)]),
    ])

# ----------------------------------------------------------------------
#  El esqueleto
# ----------------------------------------------------------------------
def _brazo(lado, nombre, mano_hijos):
    s = lado
    return nodo('hombro_' + nombre, (15 * s, -25, 0), (0, 0, 0), [
        ((-6.5, -5, -6.5, 13, 9, 13), 'prisma'),            # hombrera
        ((-5.5, -6, -5.5, 11, 1, 11), 'prisma_osc'),
        ((3 * s - 1, -7, 2, 2, 2, 2), 'percebe'),
    ], [
        coral_rama('coral_h1_' + nombre, (2 * s, -6, -2), (8, 0, 10 * s), 'coral_r', 9),
        coral_rama('coral_h2_' + nombre, (-3 * s, -6, 3), (-10, 0, -14 * s), 'coral_n', 6),
        coral_rama('coral_h3_' + nombre, (4 * s, -6, 4), (-6, 0, 22 * s), 'coral_p', 7),
        nodo('brazo_' + nombre, (0, 2, 0), (0, 0, 0), [
            ((-3.5, 0, -3.5, 7, 16, 7), 'hueso'),
            ((-4, 4, -4, 8, 4, 8), 'prisma_osc'),           # brazal
        ], [
            nodo('antebrazo_' + nombre, (0, 16, 0), (0, 0, 0), [
                ((-3, 0, -3, 6, 15, 6), 'hueso'),
                ((-3.6, 6, -3.6, 7.2, 8, 7.2), 'prisma'),
            ], [
                nodo('mano_' + nombre, (0, 15, 0), (0, 0, 0), [((-3.5, 0, -3.5, 7, 6, 7), 'hueso')], mano_hijos),
            ]),
        ]),
    ])

def _pierna(lado, nombre):
    s = lado
    return nodo('pierna_' + nombre, (6 * s, 2, 0), (-6, 0, 0), [
        ((-4.5, 0, -4.5, 9, 16, 9), 'prisma'),
    ], [
        nodo('espinilla_' + nombre, (0, 16, 0), (10, 0, 0), [
            ((-3.5, 0, -3.5, 7, 15, 7), 'hueso'),
            ((-4, 1, -4.6, 8, 9, 2), 'prisma_osc'),          # greba
        ], [
            nodo('pie_' + nombre, (0, 15, 0), (-4, 0, 0), [((-4.5, 0, -7, 9, 3, 11), 'prisma_osc')]),
        ]),
    ])

def tridente():
    return nodo('tridente', (0, 4, 0), (0, 0, 0), [
        ((-1, -26, -1, 2, 84, 2), 'prisma_osc'),             # asta
        ((-1.5, 52, -1.5, 3, 3, 3), 'punta'),
        ((-8, 55, -1.5, 16, 2.5, 3), 'prisma'),               # cruz
        ((-1.25, 57, -1.25, 2.5, 13, 2.5), 'punta'),          # punta central
        ((-7.5, 57, -1, 2, 9, 2), 'punta'),
        ((5.5, 57, -1, 2, 9, 2), 'punta'),
        ((-3, 64, -0.75, 1.5, 3, 1.5), 'punta'),              # lenguetas
        ((1.5, 64, -0.75, 1.5, 3, 1.5), 'punta'),
    ])

def esqueleto(libre=False):
    ojo = 'ojo_libre' if libre else 'ojo'
    corazon = 'corazon_libre' if libre else 'corazon'
    cadenas_pecho = [] if libre else [
        cadena_nodo('cadena_x1', (-11, -27, -9.6), (11, -6, -9.6), 1.1),
        cadena_nodo('cadena_x2', (11, -27, -9.6), (-11, -6, -9.6), 1.1),
        cadena_nodo('cadena_cin', (-12.5, -4, -7.4), (12.5, -4, -7.4), 1.0),
    ]
    costillas = [((-9, -24.5 + 4.2 * i, -8.6, 18, 1.4, 1.6), 'hueso') for i in range(4)]
    algas = [((-10 + 4 * i, 3, -6.3 + (i % 2) * 12.6, 3, 14 + (i * 7) % 9, 0), 'alga') for i in range(6)]
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        nodo('pelvis', (0, -12, 0), (0, 0, 0), [
            ((-10, -4, -6, 20, 8, 12), 'prisma_osc'),
            ((-11, 2, -6.5, 22, 4, 13), 'prisma'),            # faldon
            *algas,
        ], [
            _pierna(1, 'izq'), _pierna(-1, 'der'),
            nodo('torso', (0, -4, 0), (14, 0, 0), [
                ((-12, -28, -6, 24, 28, 13), 'abismo'),       # la cavidad
                ((-12.5, -28.5, 0, 25, 29, 7.5), 'prisma'),   # espalda acorazada
                ((-12.5, -9, -7, 25, 9, 7), 'prisma'),        # vientre
                *costillas,
                ((-5, -23, -8.2, 10, 11, 6), corazon),        # EL CORAZON MALDITO, a la vista
                ((-3, -25, -7.6, 6, 2, 4), corazon),          # aorta
                ((-1.5, -27, -8.9, 3, 18, 1.4), 'hueso'),     # esternon, por delante
                ((-9, -27, 7, 3, 3, 2), 'percebe'), ((5, -12, 7, 3, 3, 2), 'percebe'),
            ], [
                *cadenas_pecho,
                nodo('cuello', (0, -28, -2), (-12, 0, 0), [((-3, -5, -3, 6, 5, 6), 'hueso')], [
                    nodo('cabeza', (0, -5, 0), (-4, 0, 0), [
                        ((-7, -13, -7, 14, 13, 14), 'hueso'),
                        ((-7.5, -14, -7.5, 15, 3, 15), 'prisma'),     # aro de la corona
                        ((-5.5, -7.5, -7.3, 3.5, 3, 0.6), 'abismo'),  # cuencas
                        ((2, -7.5, -7.3, 3.5, 3, 0.6), 'abismo'),
                        ((-1, -4.5, -7.2, 2, 2, 0.4), 'abismo'),      # nariz
                    ], [
                        nodo('ojo_izq', (3.75, -6, -7.6), (0, 0, 0), [((-1.25, -1, -0.4, 2.5, 2, 0.8), ojo)]),
                        nodo('ojo_der', (-3.75, -6, -7.6), (0, 0, 0), [((-1.25, -1, -0.4, 2.5, 2, 0.8), ojo)]),
                        nodo('mandibula', (0, 0, 3), (0, 0, 0), [
                            ((-6, 0, -11, 12, 4, 11), 'hueso'),
                            *[((-5 + 2.2 * i, -1.3, -10.8, 1.2, 1.5, 1.2), 'hueso') for i in range(5)],
                        ]),
                        *[nodo(f'puas_{i}', (x, -14, z), (rx, 0, rz), [((-1, -6 - (i % 3) * 2, -1, 2, 6 + (i % 3) * 2, 2), 'prisma')])
                          for i, (x, z, rx, rz) in enumerate([(-6, -6, -10, -12), (0, -7, -14, 0), (6, -6, -10, 12),
                                                               (-6.5, 0, 0, -16), (6.5, 0, 0, 16), (0, 6, 12, 0)])],
                        coral_rama('corona_c1', (-4, -14, -3), (-6, 0, -18), 'coral_r', 10),
                        coral_rama('corona_c2', (3, -14, 2), (8, 0, 22), 'coral_n', 8),
                        coral_rama('corona_c3', (5, -14, -4), (-12, 0, 30), 'coral_p', 7),
                        coral_rama('corona_c4', (-2, -14, 5), (16, 0, -8), 'coral_r', 6),
                    ]),
                ]),
                _brazo(1, 'izq', [cadena_nodo('cadena_mano', (0, 5, 0), (0, 30, 4), 1.3)]),
                _brazo(-1, 'der', [tridente()]),
            ]),
        ]),
    ])

# ----------------------------------------------------------------------
#  Cajas -> cuadrilateros con UV en mosaico (1 loseta = 16 px de modelo)
# ----------------------------------------------------------------------
def caja_mosaico(box):
    x0, y0, z0, w, h, d = box
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    V = {0: (x0, y0, z0), 1: (x1, y0, z0), 2: (x1, y1, z0), 3: (x0, y1, z0),
         4: (x0, y0, z1), 5: (x1, y0, z1), 6: (x1, y1, z1), 7: (x0, y1, z1)}
    caras = [((5, 4, 0, 1), w, d), ((2, 3, 7, 6), w, d), ((0, 4, 7, 3), d, h),
             ((1, 0, 3, 2), w, h), ((5, 1, 2, 6), d, h), ((4, 5, 6, 7), w, h)]
    out = []
    for idx, a, b in caras:
        if a <= 0 or b <= 0:
            continue
        uv = [(a / 16, 0), (0, 0), (0, b / 16), (a / 16, b / 16)]
        out.append(([V[i] for i in idx], uv))
    return out

def quads(raiz, pose, modelo_a_mundo):
    out = []

    def visitar(n, M):
        nombre, off, rot, cajas, hijos = n
        ex = pose.get(nombre, {})
        r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        p = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        L = vr.T(*p) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R) @ vr.S(ex.get('esc', 1.0))
        Mn = M @ L
        if ex.get('oculto'):
            return
        for box, mat in cajas:
            for pts, uv in caja_mosaico(box):
                if mat in ESTIRADOS:   # una sola imagen estirada sobre la cara (aletas)
                    uv = [(1, 0), (0, 0), (0, 1), (1, 1)]
                w = [(modelo_a_mundo @ Mn @ np.array([*q, 1.0]))[:3] for q in pts]
                out.append((w, uv, mat))
        for h in hijos:
            visitar(h, Mn)

    visitar(raiz, np.eye(4))
    return out

def cadena_mundo(p0, p1, grosor=1.6):
    """Cadena en coordenadas de mundo (bloques), para las que van a los pilares."""
    raiz = cadena_nodo('c', (0, 0, 0), tuple((np.array(p1) - np.array(p0)) * 16), grosor)
    M = vr.T(*p0) @ vr.S(1 / 16)
    return quads(raiz, {}, M)

def dibujar(lienzo, cam, qs, luces, ambiente, niebla=None, brillo=1.4, materiales=MAT):
    for P, UV, mat in qs:
        tex = materiales[mat]
        if mat in EMISIVOS:
            luz, emis = np.ones(3), tex
        else:
            n = vr.normal(P)
            luz, emis = vr.iluminar(n, cam, np.mean(P, axis=0), luces, ambiente), None
        for tri in ((0, 1, 2), (0, 2, 3)):
            lienzo.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla,
                             brillo=brillo, envolver=True)

def entidad_a_mundo(x, y, z, guinada, escala=1.0):
    return vr.entidad_a_mundo(x, y, z, guinada, escala)

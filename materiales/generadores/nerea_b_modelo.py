"""
Nerea, opcion B: "La Marea Encadenada". Propuesta propia.

La maldicion le disolvio el cuerpo: solo queda su vieja armadura de buzo, de
bronce, llena de mar vivo. Cada ataque sale de una pieza del cuerpo:

  - sin piernas: flota sobre un REMOLINO, y de ahi salen los remolinos
  - cadenas que atan el agua del pecho y acaban en ANCLAS: molino y arpon
  - tanques de aire a la espalda: las BURBUJAS BOMBA salen por sus valvulas
  - los ojos son las MIRILLAS de cristal del casco: se rompen a flechazos
  - el CORAZON maldito flota a la vista dentro del agua del pecho

Alto: ~160 px = 10 bloques. Mismo formato de huesos que nerea_modelo.
"""
import math
import numpy as np
import vigia_render as vr
import nerea_modelo as nm

nodo, cadena_nodo, coral_rama = nm.nodo, nm.cadena_nodo, nm.coral_rama

# ----------------------------------------------------------------------
#  Materiales propios de esta version
# ----------------------------------------------------------------------
BRONCE = nm._rampa('23463c', '3a6f5c', '4f8f78', '7ab79c', 'a8d8bf')
BRONCE_V = nm._rampa('5a3a1c', '7a5226', '9a6a32', 'b8864a', 'd6a866')
BRONCE_OSC = nm._rampa('141e1a', '1f2e28', '2a3d34', '3a4f44', '4e6457')
AGUA = nm._rampa('0b2f57', '12477a', '1d64a0', '3a8cc8', '7fd0f2')
HIERRO = nm._rampa('1c1f22', '2e3236', '42474c', '5a6066', '7a8086')

def bronce(x, y, r):
    if x % 8 == 0 or y % 8 == 0:
        return BRONCE_OSC[2]                  # juntas de las placas
    if r.random() < 0.22:
        return BRONCE_V[r.choice([2, 3, 4])]  # bronce que asoma bajo la patina
    return BRONCE[r.choice([1, 2, 2, 3, 3, 4])]

def bronce_osc(x, y, r):
    if (x, y) in ((3, 3), (12, 3), (3, 12), (12, 12)):
        return BRONCE_V[3]                    # remaches
    return BRONCE_OSC[r.choice([1, 2, 2, 3, 4])]

def agua(x, y, r):
    if (x + y * 2) % 11 == 0:
        return AGUA[4]                        # vetas de luz
    return AGUA[r.choice([0, 1, 1, 2, 2, 3])]

def espuma(x, y, r):
    return (225, 246, 255) if r.random() < 0.6 else (180, 226, 242)

def hierro(x, y, r):
    if r.random() < 0.12:
        return nm.OXIDO[r.choice([3, 4])]
    return HIERRO[r.choice([1, 2, 2, 3, 4])]

nm.MAT.update({
    'bronce': nm._loseta(30, bronce),
    'bronce_osc': nm._loseta(31, bronce_osc),
    'agua': nm._loseta(32, agua),
    'espuma': nm._loseta(33, espuma),
    'hierro': nm._loseta(34, hierro),
    'cristal': nm._loseta(35, nm.emisivo('eaffff', '1fb4f0')),
    'cristal_libre': nm._loseta(36, nm.emisivo('fffbe0', 'ffbf2e')),
    'agua_libre': nm._loseta(37, lambda x, y, r: (60, 170, 210) if r.random() < 0.7 else (140, 220, 240)),
})
nm.EMISIVOS.update({'cristal', 'cristal_libre'})
TRANSLUCIDOS = {'agua': 0.5, 'agua_libre': 0.38, 'espuma': 0.8}

# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def ancla(nombre, off):
    return nodo(nombre, off, (0, 0, 0), [
        ((-3, -4, -1, 6, 4, 2), 'hierro'),            # argolla
        ((-1.5, 0, -1.5, 3, 30, 3), 'hierro'),        # cana
        ((-9, 4, -1.5, 18, 3, 3), 'hierro'),          # cepo
        ((-15, 26, -2, 30, 4, 4), 'hierro'),          # cruz
        ((-17, 18, -2, 4, 10, 4), 'hierro'),          # brazos
        ((13, 18, -2, 4, 10, 4), 'hierro'),
        ((-19, 14, -2.5, 5, 5, 5), 'hierro'),         # unas
        ((14, 14, -2.5, 5, 5, 5), 'hierro'),
    ])

def remolino(giro=0.0, libre=False):
    """Ocho anillos de agua que se ensanchan hacia arriba, cada uno girado."""
    mat = 'agua_libre' if libre else 'agua'
    anillos = []
    for k in range(8):
        y = 24 - 6 * k - 3
        r = 5 + k * 2.7
        n = 10
        segs = []
        for i in range(n):
            a = 2 * math.pi * i / n
            ancho = 2 * math.pi * r / n * 1.15
            m = 'espuma' if (i + k) % 4 == 0 else mat
            segs.append(nodo(f'rem_{k}_{i}', (r * math.cos(a), y, r * math.sin(a)), (0, -math.degrees(a) + 90, 0),
                             [((-ancho / 2, -3, -1.5, ancho, 6, 3), m)]))
        anillos.append(nodo(f'anillo_{k}', (0, 0, 0), (0, giro + k * 17, 0), [], segs))
    # la espuma del pie, a ras de suelo
    pie = [nodo(f'pie_{i}', (9 * math.cos(2 * math.pi * i / 12), 23, 9 * math.sin(2 * math.pi * i / 12)),
                (0, -30 * i, 0), [((-3, -1, -3, 6, 2, 6), 'espuma')]) for i in range(12)]
    return nodo('remolino', (0, 0, 0), (0, 0, 0), [], anillos + pie)

def hombro(lado, nombre):
    s = lado
    return nodo('hombro_' + nombre, (32 * s, -50, 0), (0, 0, 0), [
        ((-12, -8, -14, 24, 16, 28), 'bronce'),
        ((-13, 6, -15, 26, 3, 30), 'bronce_osc'),
        ((-8, -12, -10, 16, 4, 20), 'bronce'),
        ((6 * s - 2, -10, 8, 4, 4, 4), 'percebe'), ((-4 * s - 2, -10, -9, 3, 3, 3), 'percebe'),
        *[((-1.5 + (6 * s * (j - 1)), -18 - (j % 2) * 4, -1.5 + (j - 1) * 6, 3, 10 + (j % 2) * 4, 3), 'bronce_osc') for j in range(3)],
    ], [
        coral_rama('hc1_' + nombre, (5 * s, -12, 6), (6, 0, 18 * s), 'coral_r', 14),
        coral_rama('hc2_' + nombre, (-4 * s, -12, 2), (-10, 0, -12 * s), 'coral_p', 10),
        coral_rama('hc3_' + nombre, (8 * s, -12, -6), (-8, 0, 26 * s), 'coral_n', 9),
        nodo('brazo_' + nombre, (0, 6, 0), (0, 0, 0), [
            ((-6, 0, -6, 12, 24, 12), 'agua'),
            ((-7, 6, -7, 14, 3, 14), 'bronce_osc'), ((-7, 16, -7, 14, 3, 14), 'bronce_osc'),
        ], [
            nodo('antebrazo_' + nombre, (0, 24, 0), (0, 0, 0), [
                ((-8, 0, -8, 16, 22, 16), 'bronce'),
                ((-8.6, 2, -8.6, 17.2, 3, 17.2), 'bronce_osc'),
                ((-8.6, 16, -8.6, 17.2, 3, 17.2), 'bronce_osc'),
            ], [
                nodo('mano_' + nombre, (0, 22, 0), (0, 0, 0), [((-9, 0, -9, 18, 10, 18), 'bronce_osc')], [
                    nodo('cadena_ancla_' + nombre, (0, 0, 0), (0, 0, 0), [], [
                        cadena_nodo('cad_' + nombre, (0, 8, 0), (0, 28, 0), 1.6, 'hierro'),
                        ancla('ancla_' + nombre, (0, 32, 0)),
                    ]),
                ]),
            ]),
        ]),
    ])

def casco(libre=False):
    ojo = 'cristal_libre' if libre else 'cristal'
    puas = [(0, -8, 14), (8, -6, 10), (-8, -6, 10), (11, 1, 9), (-11, 1, 9), (6, 8, 8), (-6, 8, 8)]
    return nodo('casco', (0, -58, -1), (0, 0, 0), [
        ((-17, -30, -17, 34, 30, 34), 'bronce'),
        ((-13, -36, -13, 26, 6, 26), 'bronce'),
        ((-6, -40, -6, 12, 4, 12), 'bronce_osc'),
        # mirillas: marco
        ((-15, -25, -18.6, 13, 13, 2), 'bronce_osc'), ((2, -25, -18.6, 13, 13, 2), 'bronce_osc'),
        ((-1, -27, -18.2, 2, 18, 1.4), 'bronce_osc'),                  # nervio central
        # rejilla de la boca
        ((-10, -9, -17.7, 20, 8, 0.6), 'abismo'),
        *[((-9 + 4 * i, -9, -18.6, 2, 8, 1.2), 'bronce_osc') for i in range(5)],
        # valvulas a los lados
        ((-20, -19, -4, 3, 9, 9), 'bronce_osc'), ((17, -19, -4, 3, 9, 9), 'bronce_osc'),
        *[((x, y, -18.3, 1.6, 1.6, 0.8), 'bronce_osc') for x in (-16, 14.4) for y in (-28, -6)],
    ], [
        nodo('ojo_izq', (8.5, -18.5, -19.4), (0, 0, 0), [((-4.5, -4.5, -0.5, 9, 9, 1), ojo)]),
        # cejas de bronce en V: le dan el ceno
        nodo('ceja_izq', (8.5, -26.5, -19.6), (0, 0, -14), [((-8.5, -2, -1.8, 17, 3.5, 3.6), 'bronce_osc')]),
        nodo('ceja_der', (-8.5, -26.5, -19.6), (0, 0, 14), [((-8.5, -2, -1.8, 17, 3.5, 3.6), 'bronce_osc')]),
        # barba de algas que cuelga de la rejilla
        nodo('barba', (0, -1, -18.2), (8, 0, 0), [((-9 + 3.4 * i, 0, 0, 2.6, 10 + (i * 5) % 9, 0), 'alga') for i in range(6)]),
        nodo('ojo_der', (-8.5, -18.5, -19.4), (0, 0, 0), [((-4.5, -4.5, -0.5, 9, 9, 1), ojo)]),
        *[nodo(f'pua_{i}', (x, -36, z), (z * 0.9, 0, -x * 1.6), [((-1.5, -h, -1.5, 3, h, 3), 'bronce_osc')])
          for i, (x, z, h) in enumerate(puas)],
        coral_rama('cc1', (-9, -36, -4), (-6, 0, -20), 'coral_r', 16),
        coral_rama('cc2', (8, -36, 3), (10, 0, 24), 'coral_p', 13),
        coral_rama('cc3', (2, -36, 9), (20, 0, 4), 'coral_n', 11),
    ])

def esqueleto(libre=False, giro_remolino=0.0):
    corazon = 'corazon_libre' if libre else 'corazon'
    agua_mat = 'agua_libre' if libre else 'agua'
    cadenas = [] if libre else [
        cadena_nodo('cx1', (-19, -50, -14.6), (19, -14, -14.6), 1.5, 'hierro'),
        cadena_nodo('cx2', (19, -50, -14.6), (-19, -14, -14.6), 1.5, 'hierro'),
        cadena_nodo('cin', (-21, -28, -14.4), (21, -28, -14.4), 1.4, 'hierro'),
    ]
    aros = []
    for y in (-10, -32):
        aros += [((-25, y, -15.5, 50, 4, 2), 'bronce'), ((-25, y, 13.5, 50, 4, 2), 'bronce'),
                 ((-25.5, y, -15, 2, 4, 30), 'bronce'), ((23.5, y, -15, 2, 4, 30), 'bronce')]
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        remolino(giro_remolino, libre),
        nodo('torso', (0, -24, 0), (6, 0, 0), [
            ((-24, -52, -14, 48, 52, 28), agua_mat),             # el mar que lo llena
            ((-8, -38, -6, 16, 16, 12), corazon),                # el corazon, flotando dentro
            ((-3, -42, -2, 6, 4, 4), corazon),
            *aros,
            ((-25, -52, -16.5, 17, 16, 3), 'bronce'),            # peto izquierdo
            ((8, -52, -16.5, 17, 16, 3), 'bronce'),              # peto derecho
            ((-26, -58, -17, 52, 7, 34), 'bronce_osc'),          # gorguera
            ((-25, -52, 13, 50, 22, 3), 'bronce'),               # espaldar
            ((-16, -54, 16, 12, 36, 12), 'bronce'),              # tanques de aire
            ((4, -54, 16, 12, 36, 12), 'bronce'),
            ((-13, -58, 19, 6, 4, 6), 'bronce_osc'), ((7, -58, 19, 6, 4, 6), 'bronce_osc'),
            ((-12, -66, 20.5, 3, 9, 3), 'bronce_osc'), ((9, -66, 20.5, 3, 9, 3), 'bronce_osc'),
            ((-12, -24, 28, 3, 3, 2), 'percebe'), ((6, -40, 28, 3, 3, 2), 'percebe'),
        ], [
            *cadenas,
            hombro(1, 'izq'), hombro(-1, 'der'),
            casco(libre),
        ]),
    ])

# ----------------------------------------------------------------------
#  Dibujo: opaco primero, luego el agua de atras a delante
# ----------------------------------------------------------------------
def dibujar(lienzo, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    opacos = [q for q in qs if q[2] not in TRANSLUCIDOS]
    claros = [q for q in qs if q[2] in TRANSLUCIDOS]
    nm.dibujar(lienzo, cam, opacos, luces, ambiente, niebla, brillo)
    claros.sort(key=lambda q: -np.linalg.norm(np.mean(q[0], axis=0) - cam.ojo))
    for P, UV, mat in claros:
        tex = nm.MAT[mat]
        n = vr.normal(P)
        luz = vr.iluminar(n, cam, np.mean(P, axis=0), luces, ambiente) + 0.15
        for tri in ((0, 1, 2), (0, 2, 3)):
            lienzo.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, None, niebla,
                             envolver=True, translucido=TRANSLUCIDOS[mat])

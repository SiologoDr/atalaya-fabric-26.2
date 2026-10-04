"""
Nerea, opcion C: "La Leyenda de las Mareas". Propuesta propia, mistica.

Una deidad abisal, no un monstruo de Minecraft: torso humanoide de piel
abisal con runas que brillan, y en vez de piernas una cola de serpiente
marina enroscada que lo alza 10 bloques. Tres ojos, corona de espinas de
nacar, halo de agua flotando tras la cabeza, aletas en abanico por orejas y
hombros, barba de tentaculos.

  - la cola enroscada gira y levanta el REMOLINO
  - sopla la CARACOLA gigante de la mano izquierda: BURBUJAS BOMBA
  - las CADENAS de la maldicion: molino y arpon
  - los TRES OJOS: la Mirada del Abismo, y sus puntos debiles
  - el corazon es una PERLA NEGRA incrustada en el pecho

Alto: ~10 bloques. Mismo formato de huesos que nerea_modelo.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm

nodo, cadena_nodo = nm.nodo, nm.cadena_nodo

# ----------------------------------------------------------------------
#  Materiales propios (ninguno sale de una textura de Minecraft)
# ----------------------------------------------------------------------
def _escamas_serpiente():
    """Escamas en rombo, de serpiente marina: juntas en diagonal de un pixel y
    cada escama clara en la punta y violacea abajo. A 16 px por bloque, unos
    arcos redondos salen gruesos y se leen como ladrillos; los rombos no."""
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            a, b = (x + y) % 8, (x - y) % 8
            if a == 0 or b == 0:
                c = (8, 30, 40)
            else:
                s = (a + (8 - b)) / 16.0
                c = np.array([44, 140, 128]) * (1 - s) + np.array([56, 52, 126]) * s
                if a in (1, 2) and b in (6, 7):
                    c = np.array([200, 214, 150])        # brillo dorado en la punta
                c = tuple(int(v) for v in c)
            t[y, x] = (*c, 255)
    return t

def piel(x, y, r):
    base = [(170, 196, 204), (184, 208, 214), (198, 220, 224), (156, 184, 196)]
    if (x * 5 + y * 3) % 17 == 0:
        return (130, 160, 190)          # motas, como de pez abisal
    return base[r.choice([0, 1, 1, 2, 3])]

def _aleta(ancho, alto, invertida=False, color_base=(60, 90, 200), color_punta=(240, 80, 170), rayos=7):
    """Abanico: radios que salen de la base y borde festoneado entre radio y radio."""
    t = np.zeros((alto, ancho, 4), np.uint8)
    for y in range(alto):
        for x in range(ancho):
            yy = (alto - 1 - y) if not invertida else y        # 0 en la base
            v = yy / (alto - 1)
            u = (x + 0.5) / ancho
            fase = (u * rayos) % 1.0
            borde = 1.0 - 0.13 * math.sin(math.pi * fase) ** 0.6   # festones entre radios
            borde *= 1.0 - 0.25 * (2 * u - 1) ** 4                 # se redondea por los lados
            if v > borde:
                continue
            col = np.array(color_base) * (1 - v) + np.array(color_punta) * v
            if fase < 0.12 or fase > 0.92:
                col = col * 0.55 + np.array([230, 200, 250]) * 0.25   # radio
            a = int(255 * (0.75 + 0.25 * (1 - v)))
            t[y, x] = (*np.clip(col, 0, 255).astype(int), a)
    return t

def nacar(x, y, r):
    t = (x * 3 + y * 5) % 16 / 16
    return (int(214 + 34 * t), int(200 + 24 * (1 - t)), int(226 + 22 * t)) if r.random() > 0.1 else (186, 170, 200)

def caracola(x, y, r):
    banda = (y + x // 4) % 5
    return [(238, 210, 178), (222, 176, 140), (196, 132, 104), (246, 228, 204), (210, 156, 120)][banda]

def tentaculo(x, y, r):
    if y % 4 == 0 and x % 2:
        return (150, 110, 200)          # ventosas
    return [(34, 66, 82), (44, 84, 98), (58, 104, 116)][r.choice([0, 1, 1, 2])]

def garra(x, y, r):
    return [(26, 28, 40), (40, 42, 58), (58, 60, 80)][r.choice([0, 1, 2])]

def cadena_maldita(x, y, r):
    if x in (0, 15) or y in (0, 15):
        return (22, 14, 30)
    if r.random() < 0.08:
        return (170, 60, 200)
    return [(48, 36, 62), (64, 48, 80), (82, 62, 98)][r.choice([0, 1, 1, 2])]

nm.MAT.update({
    'escamas': _escamas_serpiente(),
    'piel_c': nm._loseta(61, piel),
    'aleta': _aleta(32, 32),
    'aleta_inv': _aleta(32, 32, invertida=True),
    'cresta': _aleta(32, 16, color_base=(50, 80, 180), color_punta=(220, 90, 190), rayos=9),
    'nacar': nm._loseta(63, nacar),
    'caracola': nm._loseta(64, caracola),
    'tentaculo': nm._loseta(65, tentaculo),
    'garra': nm._loseta(66, garra),
    'cadena_maldita': nm._loseta(67, cadena_maldita),
    'runa': nm._loseta(68, nm.emisivo('d8fbff', '35c8ff')),
    'ojo_c': nm._loseta(69, nm.emisivo('ffffff', '5ce8ff')),
    'perla': nm._loseta(70, nm.emisivo('f6b0ff', '4a0c66')),
    'halo': nm._loseta(71, lambda x, y, r: (120, 210, 240) if r.random() < 0.7 else (200, 245, 255)),
    'gota': nm._loseta(72, nm.emisivo('ffffff', '8ae6ff')),
    'runa_libre': nm._loseta(73, nm.emisivo('fff6d0', 'ffc23a')),
    'ojo_c_libre': nm._loseta(74, nm.emisivo('fffbe0', 'ffbf2e')),
    'perla_libre': nm._loseta(75, nm.emisivo('ffffff', 'b8f4ff')),
    'colmillo': nm._loseta(76, lambda x, y, r: (236, 232, 214)),
})
nm.EMISIVOS.update({'runa', 'ojo_c', 'perla', 'gota', 'runa_libre', 'ojo_c_libre', 'perla_libre'})
nm.ESTIRADOS.update({'aleta', 'aleta_inv', 'cresta'})
TRANSLUCIDOS = {'aleta': 0.8, 'aleta_inv': 0.8, 'cresta': 0.85, 'halo': 0.55}

# lo que lleva siempre, sea cual sea la pose
POSE_BASE = {'cabeza': {'esc': 1.25}}

def pose(extra):
    p = {k: dict(v) for k, v in POSE_BASE.items()}
    for k, v in extra.items():
        p.setdefault(k, {}).update(v)
    return p

def plano(x0, y0, z0, w, h, d=0):
    return (x0, y0, z0, w, h, d)

# ----------------------------------------------------------------------
#  Cola: baja de la cadera, toca el suelo y se enrosca por delante
# ----------------------------------------------------------------------
COLA = [  # (largo, ancho, rx, rz)
    (22, 22, 4, 0), (22, 21, 14, 0), (18, 20, 30, 0), (16, 19, 42, 0),
    (17, 18, 0, -30), (17, 17, 0, -32), (16, 16, 0, -34), (16, 14, 0, -36),
    (15, 12, 0, -36), (14, 10, -4, -34), (13, 8, -8, -30), (12, 6, -10, -24),
]

def cola():
    hijo = nodo('aleta_cola', (0, 12, 0), (0, 0, 0), [
        (plano(0, 0, -12, 0, 22, 24), 'aleta_inv'), (plano(-12, 0, 0, 24, 18, 0), 'aleta_inv'),
    ])
    for i in range(len(COLA) - 1, -1, -1):
        L, w, rx, rz = COLA[i]
        cajas = [((-w / 2, 0, -w / 2 * 0.85, w, L + 1, w * 0.85), 'escamas')]
        if i < 9:
            cajas.append((plano(0, 1, w / 2 * 0.85 - 0.5, 0, L - 1, 8), 'cresta'))
        hijo = nodo(f'cola_{i}', (0, COLA[i - 1][0] if i else 0, 0), (rx, 0, rz), cajas, [hijo])
    return hijo

# ----------------------------------------------------------------------
#  Brazos, caracola
# ----------------------------------------------------------------------
def caracola_gigante():
    """Caracola de trompeta: espiral conica que se estrecha hasta la boquilla."""
    piezas = []
    n = 12
    for k in range(n):
        t = k / (n - 1)
        r = 7.5 - 6.0 * t
        piezas.append(nodo(f'car_{k}', (0, -k * 2.6, 0), (0, k * 38, 0), [
            ((-r, -2.8, -r, 2 * r, 3.0, 2 * r), 'caracola'),
        ]))
    boca = nodo('boca_car', (0, 2, 0), (0, 0, 0), [((-8.5, -1, -8.5, 17, 4, 17), 'nacar'), ((-6, 2.5, -6, 12, 1, 12), 'perla')])
    return nodo('caracola', (0, 10, 0), (70, 0, 0), [], piezas + [boca])

def brazo(lado, nombre, en_mano, libre=False):
    s = lado
    runa = 'runa_libre' if libre else 'runa'
    return nodo('hombro_' + nombre, (18 * s, -20, 0), (0, 0, 0), [
        ((-7.5, -6, -7.5, 15, 12, 15), 'escamas'),
    ], [
        # gola de aletas en abanico que sale del hombro
        nodo('gola_' + nombre, (5 * s, -5, 3), (-25, 20 * s, 34 * s), [(plano(-14, -30, 0, 28, 30, 0), 'aleta')]),
        nodo('brazo_' + nombre, (0, 4, 0), (0, 0, 0), [
            ((-4.5, 0, -4.5, 9, 24, 9), 'piel_c'),
            ((-4.8, 8, -4.9, 9.6, 1.2, 0.6), runa), ((-4.8, 15, -4.9, 9.6, 1.2, 0.6), runa),
        ], [
            nodo('antebrazo_' + nombre, (0, 24, 0), (0, 0, 0), [
                ((-4, 0, -4, 8, 22, 8), 'escamas'),
            ], [
                nodo('cuchilla_' + nombre, (4 * s, 2, 2), (0, 0, 0), [(plano(0, 0, -2, 0, 22, 14), 'cresta')]),
                nodo('mano_' + nombre, (0, 22, 0), (0, 0, 0), [
                    ((-5, 0, -5, 10, 7, 10), 'piel_c'),
                    *[((-4.5 + 3 * k, 7, -4.5, 1.6, 8, 1.6), 'garra') for k in range(4)],
                ], en_mano),
            ]),
        ]),
    ])

# ----------------------------------------------------------------------
#  Cabeza
# ----------------------------------------------------------------------
def cabeza(libre=False):
    ojo = 'ojo_c_libre' if libre else 'ojo_c'
    runa = 'runa_libre' if libre else 'runa'
    espinas = [(0, -6, 18, -22), (-4.5, -4, 15, -28), (4.5, -4, 15, -28), (-8, 0, 12, -36), (8, 0, 12, -36), (-5, 4, 9, -46), (5, 4, 9, -46)]
    halo = [nodo(f'halo_{k}', (17 * math.cos(2 * math.pi * k / 20), 17 * math.sin(2 * math.pi * k / 20), 0),
                 (0, 0, math.degrees(2 * math.pi * k / 20)), [((-1.5, -3, -1.5, 3, 6, 3), 'halo')]) for k in range(20)]
    gotas = [nodo(f'gota_{k}', (17 * math.cos(2 * math.pi * k / 7 + 0.3), 17 * math.sin(2 * math.pi * k / 7 + 0.3), 0), (0, 0, 0),
                  [((-1.2, -1.2, -1.2, 2.4, 2.4, 2.4), 'gota')]) for k in range(7)]
    barba = [nodo(f'barba_{k}', (-5.5 + 2.75 * k, 4, -6 + abs(k - 2) * 1.2), (10 - abs(k - 2) * 5, 0, (k - 2) * 7), [
        ((-1.2, 0, -1.2, 2.4, 12 + (k * 7) % 6, 2.4), 'tentaculo')], [
        nodo(f'barba_p_{k}', (0, 12 + (k * 7) % 6, 0), (24, 0, (k - 2) * -4), [((-0.9, 0, -0.9, 1.8, 11, 1.8), 'tentaculo')], [
            nodo(f'barba_q_{k}', (0, 11, 0), (28, 0, 0), [((-0.6, 0, -0.6, 1.2, 7, 1.2), 'tentaculo')])])]) for k in range(5)]
    melena = [nodo(f'melena_{k}', (-6 + 3 * k, -15, 7), (22, 0, (k - 2) * 6), [((-1.4, 0, -0.6, 2.8, 22, 1.2), 'tentaculo')], [
        nodo(f'melena_p_{k}', (0, 22, 0), (16, 0, 0), [((-1.1, 0, -0.5, 2.2, 20 - abs(k - 2) * 3, 1), 'tentaculo')])]) for k in range(5)]
    return nodo('cabeza', (0, -8, -1), (0, 0, 0), [  # se dibuja a x1,25 (POSE_BASE)
        ((-6.5, -19, -7, 13, 19, 14), 'piel_c'),                       # craneo alargado
        ((-7, -19.5, -0.5, 14, 11, 8), 'escamas'),                     # escamas de la nuca
        ((-5.5, -1, -8.5, 11, 6, 8), 'piel_c'),                        # hocico
        ((-4.5, 4.5, -8, 9, 2, 6), 'piel_c'),                          # mandibula
        *[((-4 + 2.2 * k, 3.5, -8.7, 1, 2.6, 1), 'colmillo') for k in range(5)],
        ((-6.8, -11, -7.6, 13.6, 1.6, 1.2), 'escamas'),               # ceja de escamas
        ((-0.6, -18, -7.4, 1.2, 4, 0.6), runa), ((-4.5, -3, -7.4, 1, 3, 0.4), runa), ((3.5, -3, -7.4, 1, 3, 0.4), runa),
    ], [
        nodo('ojo_izq', (3.4, -8, -7.4), (0, 0, -12), [((-2.2, -0.9, -0.4, 4.4, 1.8, 0.8), ojo)]),
        nodo('ojo_der', (-3.4, -8, -7.4), (0, 0, 12), [((-2.2, -0.9, -0.4, 4.4, 1.8, 0.8), ojo)]),
        nodo('ojo_tercero', (0, -14, -7.5), (0, 0, 0), [((-1.1, -2.2, -0.4, 2.2, 4.4, 0.8), ojo)]),
        # aletas por orejas, en abanico hacia atras
        nodo('oreja_izq', (6.5, -9, -1), (0, -62, -34), [(plano(0, -24, 0, 0, 24, 22), 'aleta')]),
        nodo('oreja_der', (-6.5, -9, -1), (0, 62, 34), [(plano(0, -24, 0, 0, 24, 22), 'aleta')]),
        *[nodo(f'espina_{i}', (x, -19, z), (rx, 0, -x * 2.2), [((-1.3, -h, -1.3, 2.6, h, 2.6), 'nacar')], [
            nodo(f'espina_p_{i}', (0, -h, 0), (rx * 0.5, 0, 0), [((-0.7, -h * 0.55, -0.7, 1.4, h * 0.55, 1.4), 'nacar')])])
          for i, (x, z, h, rx) in enumerate(espinas)],
        nodo('halo', (0, -16, 10), (-12, 0, 0), [], halo + gotas),
        *barba, *melena,
    ])

# ----------------------------------------------------------------------
#  El cuerpo entero
# ----------------------------------------------------------------------
def esqueleto(libre=False):
    runa = 'runa_libre' if libre else 'runa'
    perla = 'perla_libre' if libre else 'perla'
    cadenas = [] if libre else [
        cadena_nodo('cx1', (-14, -22, -10), (12, -2, -8.5), 1.4, 'cadena_maldita'),
        cadena_nodo('cx2', (14, -22, -10), (-12, -2, -8.5), 1.4, 'cadena_maldita'),
        cadena_nodo('cin', (-12, -2, -8.6), (12, -2, -8.6), 1.3, 'cadena_maldita'),
    ]
    runas_pecho = [((-11, -20, -9.4, 1.2, 9, 0.6), runa), ((9.8, -20, -9.4, 1.2, 9, 0.6), runa),
                   ((-8, -23, -9.4, 16, 1.2, 0.6), runa), ((-3, -4, -9.3, 6, 1.2, 0.6), runa),
                   ((-13, -12, -9.4, 4, 1, 0.6), runa), ((9, -12, -9.4, 4, 1, 0.6), runa)]
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        nodo('cadera', (0, -40, 0), (0, 0, 0), [((-11.5, -4, -8.5, 23, 8, 17), 'escamas')], [
            cola(),
            nodo('abdomen', (0, -2, 0), (8, 0, -9), [
                ((-11, -16, -7, 22, 16, 14), 'piel_c'),
                ((-11.4, -16, -1, 22.8, 16, 8.4), 'escamas'),
                (plano(0, -16, 7.4, 0, 16, 9), 'cresta'),
            ], [
                nodo('pecho', (0, -16, 0), (10, 0, 14), [
                    ((-15, -24, -9, 30, 24, 18), 'piel_c'),
                    ((-15.4, -24, 0, 30.8, 24, 9.4), 'escamas'),
                    ((-6, -18, -11.5, 12, 12, 4.5), perla),           # LA PERLA NEGRA
                    *runas_pecho,
                    (plano(0, -24, 9.4, 0, 24, 13), 'cresta'),
                ], [
                    *cadenas,
                    nodo('cuello', (0, -24, -1), (-20, 0, -8), [((-5, -8, -5, 10, 8, 10), 'piel_c')], [cabeza(libre)]),
                    brazo(1, 'izq', [caracola_gigante()], libre),
                    brazo(-1, 'der', [] if libre else [cadena_nodo('latigo', (0, 8, 0), (0, 40, 6), 1.6, 'cadena_maldita')], libre),
                ]),
            ]),
        ]),
    ])

def dibujar(lienzo, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    opacos = [q for q in qs if q[2] not in TRANSLUCIDOS]
    claros = [q for q in qs if q[2] in TRANSLUCIDOS]
    nm.dibujar(lienzo, cam, opacos, luces, ambiente, niebla, brillo)
    claros.sort(key=lambda q: -np.linalg.norm(np.mean(q[0], axis=0) - cam.ojo))
    for P, UV, mat in claros:
        tex = nm.MAT[mat]
        n = vr.normal(P)
        luz = vr.iluminar(n, cam, np.mean(P, axis=0), luces, ambiente) + 0.12
        for tri in ((0, 1, 2), (0, 2, 3)):
            lienzo.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, None, niebla,
                             envolver=mat not in nm.ESTIRADOS, translucido=TRANSLUCIDOS[mat])

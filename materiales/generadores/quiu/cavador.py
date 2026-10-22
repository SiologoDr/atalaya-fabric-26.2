"""
El Reptisaurio Cavador / Molusco Rocoso (DEDsafío 4, libro del juego:
«Pequeño (un bloque) y lento, de arena, sobre cuatro pilares y con un manojo de prismas en el lomo:
ataca a quien se le acerque. Si te alejas demasiado, se entierra (solo asoman las puntas de sus prismas),
te sigue bajo tierra hasta encontrarte y sale debajo de ti de un mordisco. Suelta un hongo marrón y,
a veces, un fragmento de netherita»).

Rediseño completo con textura rocosa/arenisca hiperdetallada, rostro feroz de depredador subterráneo
y animaciones de acecho y excavación:
  - Rostro tallado en arenisca con ojos brillantes de ámbar/topacio en cuencas de piedra profunda,
    cejas pétreas y colmillos de mineral afilados en 3D.
  - Caparazón estratificado de piedra sedimentaria con vetas de obsidiana y manojo de prismas de amatista/geoda.
  - Cuatro pilares de roca firme con estrías geológicas.
  - Animaciones: marcha de acecho subterráneo, temblor y excavación frenética al enterrarse, deslizamiento
    de espinas como aleta bajo tierra, y erupción explosiva al emerger mordiendo.
"""
import math
import numpy as np

import bestiario as B
import bestiario_creepers as bc
import bestiario_fantasmas_v2 as bf2
import bestiario_hormigas as bh
import bestiario_limpio as L
from bestiario import T
from bestiario_hormigas import _azar1
from bestiario_limpio import rampa
from bestiario_reptiles import FINO, H, _con_cara

ID = 'molusco_rocoso'
TAM = 0.54

# ======================================================================================================================
#  Paleta de colores
# ======================================================================================================================
ARENA_ROCOSA = rampa('3a2418', '5c3a28', '84563e', 'aa7456', 'cc9272')
TERRACOTA_PILARES = rampa('26120c', '3e2016', '5a3022', '7a4434', '9e5c46')
COLMILLO_MINERAL = rampa('4e3a2c', '7c6652', 'aa947e', 'd2c0ac', 'f4e8d8')
CRISTAL_GEODA = rampa('34123c', '5a1e64', '883094', 'b84ac4', 'e470ee')
OJO_TOPACIO = rampa('4c2c04', '8a520a', 'd48a14', 'ffb824', 'fff070')
OSCURO_FOSA = H('100806')

LADOS = ((1, 'd'), (-1, 'i'))

# ======================================================================================================================
#  Pintores y texturas
# ======================================================================================================================
def textura_arenisca(nombre, R_=ARENA_ROCOSA, base=2.6, luz=0.7):
    """Arenisca estratificada con vetas minerales y desgaste geológico."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c in ('arriba', 'abajo'):
            v = np.full((th, tw), base + (0.6 if c == 'arriba' else -0.5))
            d = np.hypot(xs - tw / 2, ys - th / 2)
            v = v + (np.sin(d * 1.5) > 0.3) * 0.4
        else:
            # Estratos horizontales geológicos
            estrato = np.sin((ys + s) * 0.8) * 0.6
            v = base + estrato + luz * (0.3 - (ys + 0.5) / th * 0.6)
        a = _azar1(xs // 2, ys // 2, s * 7 + 13)
        v = v + np.where(a < 0.2, -0.6, np.where(a > 0.8, 0.5, 0.0))
        idx = np.clip(np.round(v), 0, len(R_) - 1)
        return L._rgba(L.color_continuo(R_, idx)), None
    return B.Pintor(nombre, fn)


def textura_pilar(nombre, R_=TERRACOTA_PILARES):
    """Pilar de piedra chiseled con vetas verticales y anillos de compresión."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        if c in ('arriba', 'abajo'):
            d = np.maximum(np.abs(xs - (tw - 1) / 2), np.abs(ys - (th - 1) / 2))
            v = np.full((th, tw), 3.2 if c == 'arriba' else 1.2) - (np.round(d) % 2 == 1) * 0.5
        else:
            col = _azar1(xs, np.zeros_like(xs), s + 9)
            veta = (col < 0.25) & (_azar1(xs, ys // 5, s + 5) > 0.2)
            anillo_horiz = (ys % 6 == 0) * 0.5
            v = 2.4 + (col - 0.5) * 0.8 - veta * 0.7 - anillo_horiz + (a > 0.92) * 0.4
        idx = np.clip(np.round(v), 0, len(R_) - 1)
        return L._rgba(L.color_continuo(R_, idx)), None
    return B.Pintor(nombre, fn)


def prisma_cristal(nombre, R_=CRISTAL_GEODA):
    """Prisma de cristal amatista con núcleo translúcido brillante y facetas chiseled."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        # Facetas brillantes de cuarzo/amatista
        v = 2.8 + 1.2 * (1.0 - (ys + 0.5) / th)
        arista = (xs == 0) | (xs == tw - 1) | (ys == 0)
        v = v + arista * 0.8
        a = _azar1(xs, ys, s + 3)
        v = v + (a > 0.85) * 0.5 - (a < 0.1) * 0.5
        idx = np.clip(np.round(v), 0, len(R_) - 1)
        return L._rgba(L.color_continuo(R_, idx)), None
    return B.Pintor(nombre, fn)


# Rostro de depredador subterráneo (14 x 10 a 32 por bloque)
# Ojos de topacio brillante con pupila hendida y colmillos minerales
CARA_CAVADOR_HD = [
    "..............",
    "..kk......kk..",
    ".koook..koook.",
    ".koyok..koyok.",
    ".koqok..koqok.",
    "..kkk....kkk..",
    "..............",
    ".ww........ww.",
    ".ww........ww.",
    "..w........w..",
]

# Versión compacta a escala reducida (8 x 6)
CARA_CAVADOR_CHICO_HD = [
    "........",
    ".kk..kk.",
    "koykkoo.",
    "koqkkoo.",
    "........",
    "ww....ww",
]


def colmillos_hd(nombre, R_=COLMILLO_MINERAL):
    """Colmillos de mineral en segunda capa: dos colmillos largos frontales y laterales afilados."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara == 'frente':
            dientes = [(0.25, 0.95), (0.75, 0.95)]
        elif cara == 'izq':
            dientes = [(0.75, 0.50)]
        elif cara == 'der':
            dientes = [(0.25, 0.50)]
        else:
            return tex, None

        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        for fx, fl in dientes:
            lk = max(2.0, fl * th)
            t = np.clip(y / lk, 0, 1)
            cx = fx * tw
            w = np.where(t < 0.7, 1.15, 0.5)
            mk = (y >= 0) & (y < lk) & (np.abs(x - cx) < w)
            v = np.where(mk, 3.2 - (x > cx) * 0.8 + (t > 0.6) * 0.6, v)
            dentro |= mk

        rgb = L.color_continuo(R_, np.clip(np.round(v), 0, 4))
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


# ======================================================================================================================
#  Construcción del modelo
# ======================================================================================================================
def construir():
    """Construye el Reptisaurio Cavador / Molusco Rocoso."""
    m = B.Modelo(ID, K=2, ancho=128)
    m.escala = 1.0

    arena = textura_arenisca('arena_cavador', ARENA_ROCOSA)
    pr = textura_pilar('prisma_cavador', TERRACOTA_PILARES)
    cristal = prisma_cristal('cristal_cavador', CRISTAL_GEODA)

    m.parte('cuerpo', None, (0, 9, 0))
    # Caparazón central de roca arenisca
    m.caja('cuerpo', (0, 9.0, 0.0), (12, 4.4, 12), arena)

    # Cabeza con rostro esculpido
    m.parte('cabeza', 'cuerpo', (0, 9.0, 6.0))
    mapa = CARA_CAVADOR_HD if TAM >= 0.75 else CARA_CAVADOR_CHICO_HD
    colores_cara = {
        'k': H('140a06'),
        'o': H('d48a14'),
        'y': H('fff070'),
        'q': H('0a0402'),
        'w': H('f0e4d0'),
    }
    cara = _con_cara('cara_cavador', arena, {'frente': mapa}, colores_cara, fino=True)
    m.caja('cabeza', (0, 8.2, 7.6), (7.2, 5.2, 3.8), arena, caras={'frente': cara})
    m.caja('cabeza', (0, 3.8, 7.6), (6.8, 4.8, 4.0), colmillos_hd('colmillos_cavador', COLMILLO_MINERAL))

    # Pilares de roca cuadrúpedos
    pata = textura_arenisca('pata_arena_cavador', ARENA_ROCOSA, base=2.4)
    for lado, ld in LADOS:
        for z, nombre in ((8.6, 'del'), (-8.6, 'tra')):
            n = m.parte(f'pata_{nombre}_{ld}', 'cuerpo', (lado * 5.0, 9.4, z * 0.5))
            pilar = np.array((lado * 10.6, 0.0, z))
            m.caja(n, (pilar[0], 5.6, z), (4.4, 11.2, 4.4), pr)
            m.viga(n, (lado * 5.0, 9.4, z * 0.5), (lado * 8.6, 9.4, z * 0.95), 2.2, pata, ancho=2.2, extra=1.0)

    # Manojo de prismas de cristal geoda dorsal
    m.parte('prismas', 'cuerpo', (0, 11.0, -1.0))
    anillos = [(0.0, 0, 1, 20.0), (3.6, 6, 6, 15.5), (5.8, 13, 8, 10.0)]
    for radio, abre, cuantos, alto in anillos:
        for k in range(cuantos):
            ang = 2 * math.pi * k / cuantos + (0.4 if cuantos == 8 else 0.0)
            ox, oz = radio * math.cos(ang), radio * math.sin(ang) - 1.4
            al = alto + ((k * 7) % 3 - 1) * 1.2
            giro_x = abre * math.sin(ang)
            giro_z = -abre * math.cos(ang)
            M = T(ox, 10.6, oz) @ B.girar((giro_x - 4, 0, giro_z))
            # Mezcla de pilares de roca y espinas de cristal
            pintor_prisma = cristal if k % 2 == 0 or radio == 0.0 else pr
            m._caja('prismas', M, -2.0, 0.0, -2.0, 4.0, al, 4.0, pintor_prisma)

    m.mirar(('cabeza', 0.6))
    anims_cavador(m)
    return m


# ======================================================================================================================
#  Animaciones de depredador subterráneo
# ======================================================================================================================
def anims_cavador(m):
    """Animaciones del Cavador:
    reposo: acecho en cuclillas bajas; respiración pesada con estremecimiento de prismas; cabeza que otea el suelo olfateando.
    andar: marcha cuadrúpeda en compás cruzado con zancada pesada de pilares.
    ataque: salto de emboscada frontal mordiendo ferozmente con los colmillos.
    especial: temblor frenético de perforación, escarbando la tierra hasta sumergirse.
    estado1: navegando bajo tierra con solo las espinas superiores cortando la superficie.
    aparece: erupción vertical rompiendo la tierra y cayendo sobre sus 4 pilares.
    muerte: vuelco hacia atrás con patas extendidas en rigidez.
    """
    # Reposo
    r = m.anim('reposo', 3.2, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.35, periodo=1.6)
    r.onda('prismas', 'r', 2, 3.5, periodo=3.2)
    r.onda('prismas', 'r', 0, 2.5, periodo=1.6, fase=0.3)
    r.rot('cabeza', [
        (0.0, 0, 0, 0),
        (0.5, 4, 16, 0),
        (1.2, -2, 16, 0),
        (1.6, 0, 0, 0),
        (2.1, 4, -16, 0),
        (2.8, -2, -16, 0),
        (3.2, 0, 0, 0)
    ])

    # Andar
    a = m.anim('andar', 0.70, bucle=True)
    for k, (lado, ld) in enumerate(LADOS):
        for nombre, f in (('del', 0.5 * k), ('tra', 0.5 * (1 - k))):
            a.onda(f'pata_{nombre}_{ld}', 'm', 1, 2.8, periodo=0.70, fase=f, forma=lambda v: max(0.0, v))
            a.onda(f'pata_{nombre}_{ld}', 'm', 2, 2.0, periodo=0.70, fase=f + 0.25)
    a.onda('cuerpo', 'm', 1, 0.6, periodo=0.35)
    a.onda('cuerpo', 'r', 2, 4.0, periodo=0.70)
    a.onda('prismas', 'r', 2, 4.5, periodo=0.35, fase=0.2)

    # Ataque mordisco
    at = m.anim('ataque', 0.45)
    at.mov('cuerpo', [(0, 0, 0, 0), (0.15, 0, 0.6, -2.0), (0.28, 0, -0.4, 4.2), (0.45, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.15, -12, 0, 0), (0.28, 14, 0, 0), (0.45, 0, 0, 0)])
    at.mov('cabeza', [(0, 0, 0, 0), (0.15, 0, 0.5, -2.0), (0.28, 0, -0.2, 3.5), (0.45, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.15, -16, 0, 0), (0.28, 18, 0, 0), (0.45, 0, 0, 0)])

    # Especial: excavación y sumersión
    en = m.anim('especial', 0.65)
    en.mov('cuerpo', [(0, 0, 0, 0), (0.12, 0, 1.2, 0), (0.65, 0, -21.5, 0)])
    en.rot('cuerpo', [
        (0.0, 0, 0, 0),
        (0.10, 0, 0, 14),
        (0.20, 0, 0, -14),
        (0.30, 0, 0, 12),
        (0.40, 0, 0, -12),
        (0.50, 0, 0, 8),
        (0.60, 0, 0, -6),
        (0.65, 0, 0, 0)
    ])

    # Estado 1: acecho bajo tierra
    e = m.anim('estado1', 1.0, bucle=True)
    e.mov('cuerpo', [(0, 0, -21.5, 0), (0.5, 0, -20.6, 0), (1.0, 0, -21.5, 0)])
    e.rot('cuerpo', [(0, 0, 0, -4), (0.5, 0, 0, 4), (1.0, 0, 0, -4)])
    e.onda('prismas', 'r', 2, 3.0, periodo=1.0)

    # Aparece: erupción explosiva de emboscada
    ap = m.anim('aparece', 0.55)
    ap.mov('cuerpo', [(0, 0, -21.5, 0), (0.22, 0, 4.5, 0), (0.38, 0, -1.0, 0), (0.55, 0, 0, 0)])
    ap.rot('cuerpo', [(0, 0, 0, 0), (0.22, 14, 0, 0), (0.38, -6, 0, 0), (0.55, 0, 0, 0)])

    # Muerte
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (1.0, 0, 0, 180)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, 8, 0)])

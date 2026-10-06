"""
Nerea A para el juego: la malla del boceto pasada a piezas animables, con su
atlas de textura y el codigo Java que la construye.

Es la UNICA fuente de la geometria. De aqui salen:
  - src/client/.../NereaMalla.java      las piezas, cajas y texOffs
  - textures/entity/nerea/nerea.png      el atlas (cada caja pintada con su material)
  - textures/entity/nerea/nerea_brillo*.png  lo que brilla (ojos, corazon, puntas)
y nerea_juego_anim.py importa este modulo para animar y para sacar los puntos
que usa el servidor (ojos, corazon, mano, punta del tridente).

Unidades: pixeles de modelo, Y hacia abajo, el frente mira a -Z, pies en y=24.
El renderer escala x2,4: un pixel de modelo son 0,15 bloques en el mundo.

Desde el remake de octubre de 2026 (_remake, al final de construir) mide unos
15 bloques en vez de 10 y lleva la venera de nacar detras de la cabeza, la
corona y los corales mas largos, la barba y la capa de algas, las espinas del
lomo, la caracola del hombro, el ancla en la cadena, el tridente largo con su
espiral de espuma y los brazos, piernas y ojos mas gruesos. La malla de antes
esta en nerea_juego_v1.py (la usa la ficha para el antes).
"""
import math, random, os, sys
import numpy as np
from PIL import Image
import nerea_modelo as nm

ESCALA = 2.4

# ----------------------------------------------------------------------
#  Materiales: los del boceto, mas los que el juego necesita aparte
# ----------------------------------------------------------------------
MAT = dict(nm.MAT)
# El corazon tiene cuatro estados (uno por fase: cada vez mas rajado y mas
# apagado) y el de liberado, limpio. Cada uno es una pieza con su material.
CORAZONES = ['corazon1', 'corazon2', 'corazon3', 'corazon4', 'corazon_libre']
for _c in CORAZONES:
    MAT[_c] = nm.MAT['corazon']
EMISIVOS = {'ojo', 'corazon', 'punta', *CORAZONES}
# lo que brilla en la capa "eyes": color normal y color liberado
BRILLO = {'ojo': ('eaffff', '3fe0ff'), 'corazon': ('ffd0e0', 'e0144c'), 'punta': ('d8ffff', '2ec8e8'),
          'corazon1': ('ffd0e0', 'e0144c'), 'corazon2': ('eaa6c6', 'b0124a'), 'corazon3': ('bb7aa0', '7a0e44'),
          'corazon4': ('7c4a6a', '3e0828'), 'corazon_libre': ('f0fffa', '35e0b0')}
BRILLO_LIBRE = {'ojo': ('fffbe0', 'ffc23a'), 'corazon': ('f0fffa', '35e0b0'), 'punta': ('fff6d0', 'ffcf5a'),
                **{c: ('f0fffa', '35e0b0') for c in CORAZONES}}
# grietas por estado del corazon (cuantas por cara)
GRIETAS = {'corazon2': 2, 'corazon3': 5, 'corazon4': 9}

# Lo que cambia con cada fase: la maldicion se extiende por el cuerpo.
#   ojos y puntas    cian -> violeta -> magenta -> rojo
#   venas            magenta, cada vez mas por hueso y prismarina
#   coral y algas    se mueren: pierden el color hasta quedar grises
OJOS_FASE = {1: ('eaffff', '3fe0ff'), 2: ('f0e4ff', '9a6bff'), 3: ('ffd8f8', 'd43cff'), 4: ('ffe0e6', 'ff2050')}
PUNTAS_FASE = {1: ('d8ffff', '2ec8e8'), 2: ('ece0ff', '8a6bff'), 3: ('ffd0f4', 'c040f0'), 4: ('ffd6dc', 'e8204a')}
VENAS_FASE = {1: 0.0, 2: 0.0025, 3: 0.006, 4: 0.012}
CORAL_MUERTO = {1: 0.0, 2: 0.2, 3: 0.5, 4: 0.85}
CORALES = {'coral_r', 'coral_n', 'coral_p', 'alga'}
CON_VENAS = {'prisma', 'prisma_osc', 'hueso', 'abismo'}

# --- Los materiales del remake (losetas 16x16, como nerea_modelo.py) ---
NACAR = nm._rampa('6a4862', 'a0788e', 'd0a6bc', 'f0d2e2', 'fff4fa')
ALGA_OSC = nm._rampa('0c200e', '143214', '1e4a1a', '2a6222', '3a7a2e')


def _nacar(x, y, r):
    # bandas de nacar con un reflejo iridiscente (rosa y turquesa)
    b = [1, 2, 3, 3, 2][(y // 3) % 5]
    if r.random() < 0.12:
        b = 4
    c = NACAR[b]
    if (x + y * 2) % 11 == 0:
        c = (c[0] - 20, c[1] + 18, c[2] + 22)
    elif (x * 3 + y) % 13 == 0:
        c = (c[0] + 24, c[1] - 6, c[2] + 4)
    return tuple(max(0, min(255, v)) for v in c)


def _nacar_osc(x, y, r):
    # el surco entre lomos de la venera: el mismo nacar, mas apagado y rosado
    c = _nacar(x, y, r)
    return tuple(max(0, min(255, int(v))) for v in (c[0] * 0.78 + 12, c[1] * 0.66, c[2] * 0.74))


def _alga_osc(x, y, r):
    b = r.choice([1, 2, 2, 3])
    if x in (0, 15):
        b = 0
    elif x == 8 and r.random() < 0.7:
        b = 4                       # el nervio de la hoja
    return ALGA_OSC[b]


MAT.update({
    'concha': nm._loseta(30, _nacar),
    'concha_osc': nm._loseta(35, _nacar_osc),
    'alga_osc': nm._loseta(31, _alga_osc),
    'perla': nm._loseta(33, nm.emisivo('ffffff', '9fe8ff')),
    'espuma': nm._loseta(34, nm.emisivo('f0ffff', '3fe0ff')),
    'nacar_luz': nm._loseta(36, nm.emisivo('fff4fa', 'ff9ac8')),
})
EMISIVOS |= {'perla', 'espuma', 'nacar_luz'}
BRILLO.update({'perla': ('ffffff', '9fe8ff'), 'espuma': ('f0ffff', '3fe0ff'), 'nacar_luz': ('fff4fa', 'ff9ac8')})
BRILLO_LIBRE.update({'perla': ('fffbe0', 'ffd86a'), 'espuma': ('fff6d0', 'ffcf5a'), 'nacar_luz': ('fffbe0', 'ffd86a')})
# la maldicion tambien le sube por la concha
CON_VENAS |= {'concha', 'concha_osc'}


class Parte:
    def __init__(self, nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
        self.nombre, self.padre = nombre, padre
        self.pivote = tuple(float(v) for v in pivote)
        self.rot = tuple(float(v) for v in rot)
        self.cajas = [tuple(c) for c in cajas]      # (x0, y0, z0, w, h, d, mat)
        self.hijos = []


PARTES = {}
ORDEN = []


def parte(nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
    assert nombre not in PARTES, nombre
    p = Parte(nombre, padre, pivote, rot, cajas)
    PARTES[nombre] = p
    ORDEN.append(nombre)
    if padre:
        PARTES[padre].hijos.append(p)
    return p


def eslabones(largo, grosor, mat='oxido'):
    """Eslabones alternos a lo largo de +Y local, de 0 a largo."""
    cajas = []
    paso = 3.2 * grosor
    y, k = 0.0, 0
    while y < largo - 1:
        g = grosor
        if k % 2 == 0:
            cajas.append((-1.5 * g, y, -0.5 * g, 3 * g, 4 * g, 1 * g, mat))
        else:
            cajas.append((-0.5 * g, y, -1.5 * g, 1 * g, 4 * g, 3 * g, mat))
        y += paso
        k += 1
    return cajas


def rot_hacia(d):
    """Angulos (x, y) en grados que llevan +Y local a la direccion d (Rz*Ry*Rx, z=0)."""
    d = np.array(d, float)
    d /= np.linalg.norm(d)
    a = math.degrees(math.acos(max(-1.0, min(1.0, d[1]))))
    b = math.degrees(math.atan2(d[0], d[2]))
    return a, b


def cadena(nombre, padre, inicio, fin, grosor=1.0, mat='oxido'):
    d = np.array(fin, float) - np.array(inicio, float)
    a, b = rot_hacia(d)
    return parte(nombre, padre, inicio, (a, b, 0.0), eslabones(float(np.linalg.norm(d)), grosor, mat))


def coral(nombre, padre, off, rot, mat, alto=7):
    parte(nombre, padre, off, rot, [(-1, -alto, -1, 2, alto, 2, mat)])
    parte(nombre + '_a', nombre, (0, -alto * 0.55, 0), (0, 0, 38), [(-0.75, -alto * 0.5, -0.75, 1.5, alto * 0.5, 1.5, mat)])
    parte(nombre + '_b', nombre, (0, -alto * 0.75, 0), (0, 0, -34), [(-0.75, -alto * 0.4, -0.75, 1.5, alto * 0.4, 1.5, mat)])


# ----------------------------------------------------------------------
#  El esqueleto (el del boceto, con piezas sueltas donde hace falta animar)
# ----------------------------------------------------------------------
def construir():
    PARTES.clear()
    ORDEN.clear()
    parte('pelvis', None, (0, -12, 0), cajas=[
        (-10, -4, -6, 20, 8, 12, 'prisma_osc'),
        (-11, 2, -6.5, 22, 4, 13, 'prisma'),               # faldon
    ])
    # algas del faldon: delante y detras, sueltas para que ondeen
    parte('algas_del', 'pelvis', (0, 5, -6.3), cajas=[
        (-10 + 8 * i, -2, 0, 3, 14 + (i * 7) % 9, 0, 'alga') for i in range(3)])
    parte('algas_tras', 'pelvis', (0, 5, 6.3), cajas=[
        (-6 + 8 * i, -2, 0, 3, 13 + (i * 5) % 8, 0, 'alga') for i in range(3)])

    for s, n in ((1, 'izq'), (-1, 'der')):
        parte('pierna_' + n, 'pelvis', (6 * s, 2, 0), (-6, 0, 0), [(-4.5, 0, -4.5, 9, 16, 9, 'prisma')])
        parte('espinilla_' + n, 'pierna_' + n, (0, 16, 0), (10, 0, 0), [
            (-3.5, 0, -3.5, 7, 15, 7, 'hueso'),
            (-4, 1, -4.6, 8, 9, 2, 'prisma_osc')])         # greba
        parte('pie_' + n, 'espinilla_' + n, (0, 15, 0), (-4, 0, 0), [(-4.5, 0, -7, 9, 3, 11, 'prisma_osc')])

    parte('torso', 'pelvis', (0, -4, 0), (14, 0, 0), [
        (-12, -28, -6, 24, 28, 13, 'abismo'),              # la cavidad
        (-12.5, -28.5, 0, 25, 29, 7.5, 'prisma'),          # espalda acorazada
        (-12.5, -9, -7, 25, 9, 7, 'prisma'),               # vientre
        (-9, -27, 7, 3, 3, 2, 'percebe'), (5, -12, 7, 3, 3, 2, 'percebe'),
    ])
    # las costillas van aparte: en la fase IV se abren y el corazon queda al aire
    parte('costillas', 'torso', (0, 0, 0), cajas=[
        *[(-9, -24.5 + 4.2 * i, -8.6, 18, 1.4, 1.6, 'hueso') for i in range(4)],
        (-1.5, -27, -8.9, 3, 18, 1.4, 'hueso')])           # esternon
    # el corazon, con el pivote en su centro para que lata sin moverse de sitio;
    # dentro, sus cinco estados (el modelo ensena solo el que toca)
    parte('corazon', 'torso', (0, -17.5, -5.2))
    for c in CORAZONES:
        parte('corazon_' + c.replace('corazon', '').strip('_') if c != 'corazon_libre' else 'corazon_libre',
              'corazon', (0, 0, 0), cajas=[
                  (-5, -5.5, -3, 10, 11, 6, c),
                  (-3, -7.5, -2.4, 6, 2, 4, c)])            # aorta

    # las cuatro cadenas del pecho: una por sello, se parten cuando cae su pilar
    cadena('cadena_1', 'torso', (-11, -27, -9.6), (11, -6, -9.6), 1.1)
    cadena('cadena_2', 'torso', (11, -27, -9.6), (-11, -6, -9.6), 1.1)
    cadena('cadena_3', 'torso', (-12.5, -4, -7.6), (12.5, -4, -7.6), 1.0)
    cadena('cadena_4', 'torso', (-12, -26.4, -9.9), (12, -26.4, -9.9), 1.0)

    parte('cuello', 'torso', (0, -28, -2), (-12, 0, 0), [(-3, -5, -3, 6, 5, 6, 'hueso')])
    parte('cabeza', 'cuello', (0, -5, 0), (-4, 0, 0), [
        (-7, -13, -7, 14, 13, 14, 'hueso'),
        (-7.5, -14, -7.5, 15, 3, 15, 'prisma'),            # aro de la corona
        (-5.5, -7.5, -7.3, 3.5, 3, 0.6, 'abismo'),         # cuencas
        (2, -7.5, -7.3, 3.5, 3, 0.6, 'abismo'),
        (-1, -4.5, -7.2, 2, 2, 0.4, 'abismo'),             # nariz
    ])
    parte('ojo_izq', 'cabeza', (3.75, -6, -7.6), cajas=[(-1.25, -1, -0.4, 2.5, 2, 0.8, 'ojo')])
    parte('ojo_der', 'cabeza', (-3.75, -6, -7.6), cajas=[(-1.25, -1, -0.4, 2.5, 2, 0.8, 'ojo')])
    parte('mandibula', 'cabeza', (0, 0, 3), cajas=[
        (-6, 0, -11, 12, 4, 11, 'hueso'),
        *[(-5 + 2.2 * i, -1.3, -10.8, 1.2, 1.5, 1.2, 'hueso') for i in range(5)]])
    for i, (x, z, rx, rz) in enumerate([(-6, -6, -10, -12), (0, -7, -14, 0), (6, -6, -10, 12),
                                        (-6.5, 0, 0, -16), (6.5, 0, 0, 16), (0, 6, 12, 0)]):
        parte(f'puas_{i}', 'cabeza', (x, -14, z), (rx, 0, rz),
              [(-1, -6 - (i % 3) * 2, -1, 2, 6 + (i % 3) * 2, 2, 'prisma')])
    coral('corona_c1', 'cabeza', (-4, -14, -3), (-6, 0, -18), 'coral_r', 10)
    coral('corona_c2', 'cabeza', (3, -14, 2), (8, 0, 22), 'coral_n', 8)
    coral('corona_c3', 'cabeza', (5, -14, -4), (-12, 0, 30), 'coral_p', 7)
    coral('corona_c4', 'cabeza', (-2, -14, 5), (16, 0, -8), 'coral_r', 6)

    for s, n in ((1, 'izq'), (-1, 'der')):
        parte('hombro_' + n, 'torso', (15 * s, -25, 0), cajas=[
            (-6.5, -5, -6.5, 13, 9, 13, 'prisma'),          # hombrera
            (-5.5, -6, -5.5, 11, 1, 11, 'prisma_osc'),
            (3 * s - 1, -7, 2, 2, 2, 2, 'percebe')])
        coral('coral_h1_' + n, 'hombro_' + n, (2 * s, -6, -2), (8, 0, 10 * s), 'coral_r', 9)
        coral('coral_h2_' + n, 'hombro_' + n, (-3 * s, -6, 3), (-10, 0, -14 * s), 'coral_n', 6)
        coral('coral_h3_' + n, 'hombro_' + n, (4 * s, -6, 4), (-6, 0, 22 * s), 'coral_p', 7)
        # Reposo de los brazos: el derecho sujeta el tridente como un baston,
        # con el antebrazo adelantado; el izquierdo cuelga con el codo suelto.
        rot_brazo = (-24, 0, 6) if n == 'der' else (-6, 0, -4)
        rot_antebrazo = (-62, 0, 0) if n == 'der' else (-16, 0, 0)
        parte('brazo_' + n, 'hombro_' + n, (0, 2, 0), rot_brazo, cajas=[
            (-3.5, 0, -3.5, 7, 16, 7, 'hueso'),
            (-4, 4, -4, 8, 4, 8, 'prisma_osc')])            # brazal
        parte('antebrazo_' + n, 'brazo_' + n, (0, 16, 0), rot_antebrazo, cajas=[
            (-3, 0, -3, 6, 15, 6, 'hueso'),
            (-3.6, 6, -3.6, 7.2, 8, 7.2, 'prisma')])
        parte('mano_' + n, 'antebrazo_' + n, (0, 15, 0), cajas=[(-3.5, 0, -3.5, 7, 6, 7, 'hueso')])

    # la cadena-latigo de la mano izquierda, con el ancla del Arpon al final
    cadena('cadena_mano', 'mano_izq', (0, 5, 0), (0, 20, 5), 1.3)
    largo = float(np.linalg.norm([0, 15, 5]))
    ancla('gancho_mano', 'cadena_mano', (0, largo, 0))

    # el tridente: en reposo, vertical y con las puntas arriba (el giro exacto
    # sale de la postura del brazo, al final de construir)
    parte('tridente', 'mano_der', (0, 4, 0), (180, 0, 0), [
        (-1, -26, -1, 2, 84, 2, 'prisma_osc'),              # asta
        (-1.5, 52, -1.5, 3, 3, 3, 'punta'),
        (-8, 55, -1.5, 16, 2.5, 3, 'prisma'),               # cruz
        (-1.25, 57, -1.25, 2.5, 13, 2.5, 'punta'),          # punta central
        (-7.5, 57, -1, 2, 9, 2, 'punta'),
        (5.5, 57, -1, 2, 9, 2, 'punta'),
        (-3, 64, -0.75, 1.5, 3, 1.5, 'punta'),              # lenguetas
        (1.5, 64, -0.75, 1.5, 3, 1.5, 'punta'),
    ])

    # las cadenas largas del Molino: cuelgan de la pelvis (que es la que gira)
    # desde donde quedan las manos en la pose del molino hasta el suelo a 10
    # bloques. Solo se ven durante el ataque.
    for n, (ini, fin) in MOLINO_CADENAS.items():
        cadena('molino_' + n, 'pelvis', ini, fin, 1.6)
        # y en la punta, un ancla que barre el suelo
        ancla('ancla_molino_' + n, 'molino_' + n, (0, float(np.linalg.norm(np.array(fin) - np.array(ini))), 0))

    _remake()

    # El tridente, a plomo en el puno: su eje +Y ha de apuntar arriba en el mundo.
    Rm = matrices()['mano_der'][:3, :3]
    t = Rm.T @ np.array([0, -1.0, 0])
    PARTES['tridente'].rot = (math.degrees(math.asin(t[2])), 0.0, math.degrees(math.atan2(-t[0], t[1])))


def giro_empunar():
    """Offset del tridente para que las puntas vayan donde apunta el antebrazo
    (empunado para golpear). Se busca la equivalencia mas cercana al reposo,
    para que el giro de muneca sea corto y no una voltereta."""
    rx, _, rz = PARTES['tridente'].rot
    return (-180.0 - rx, 0.0, 180.0 - rz)


# El ancla (desde el remake, en lugar del gancho de hueso): la argolla, la cana
# de prismarina con percebes, el cepo de oxido y la cruz; los dos brazos con sus
# unas van aparte (ancla()). El eje va en +Y local: la argolla en 0, la cruz al
# fondo. Las mismas cajas pinta GanchoNereaRenderer para el Arpon.
ANCLA = [
    (-2.6, -2.5, -0.9, 5.2, 3, 1.8, 'oxido'),           # la argolla
    (-1.3, 0, -1.3, 2.6, 13, 2.6, 'prisma_osc'),        # la cana
    (-1.1, 2.5, -8, 2.2, 2.2, 16, 'oxido'),             # el cepo, de fondo
    (-2, 12, -2, 4, 3.5, 4, 'prisma_osc'),              # la cruz
    (-1, 5, 1.2, 2, 2, 2, 'percebe'), (0.6, 9, -2.2, 2, 2, 1.5, 'percebe')]
ANCLA_BRAZO = [(-1.2, 0, -1.2, 2.4, 11, 2.4, 'prisma_osc'),
               (-3.4, 7, -1.4, 6.8, 6, 2.8, 'prisma_osc')]   # la una


def ancla(nombre, padre, pivote, rot=(0, 0, 0)):
    """Un ancla entera: la cana y, desde la cruz, los dos brazos hacia atras."""
    parte(nombre, padre, pivote, rot, ANCLA)
    for s, lado in ((1, 'a'), (-1, 'b')):
        parte(f'{nombre}_{lado}', nombre, (0, 14, 0), (0, 0, s * 128), ANCLA_BRAZO)


def _escalar_y(nombre, k):
    """Alarga una pieza (y sus hijos) a lo largo de su Y local: cajas y pivotes."""
    p = PARTES[nombre]
    p.cajas = [(c[0], c[1] * k, c[2], c[3], c[4] * k, c[5], c[6]) for c in p.cajas]
    for h in p.hijos:
        h.pivote = (h.pivote[0], h.pivote[1] * k, h.pivote[2])
        _escalar_y(h.nombre, k)


def _escalar(nombre, k):
    """Agranda las cajas de una pieza alrededor de su pivote."""
    p = PARTES[nombre]
    p.cajas = [tuple(v * k for v in c[:6]) + (c[6],) for c in p.cajas]


def _engordar(nombre, k):
    """Engorda una pieza (x y z de sus cajas) sin alargarla: las piernas siguen
    midiendo lo mismo para la cinematica inversa de nerea_fisica.py."""
    p = PARTES[nombre]
    p.cajas = [(c[0] * k, c[1], c[2] * k, c[3] * k, c[4], c[5] * k, c[6]) for c in p.cajas]


def _remake():
    """El remake de octubre de 2026, sobre la malla de siempre."""
    # --- La corona: puas y cuernos de coral mucho mas largos
    for i in range(6):
        _escalar_y(f'puas_{i}', 1.9)
    for n in ('corona_c1', 'corona_c2', 'corona_c3', 'corona_c4'):
        _escalar_y(n, 1.7)
    for n in [k for k in ORDEN if k.startswith('coral_h')]:     # (las ramas, dos veces: como en la ficha)
        _escalar_y(n, 1.5)

    # --- La venera: costillas anchas que se solapan (lomos y surcos alternos),
    # con el filo encendido, y una perla que brilla en el centro
    parte('concha', 'cabeza', (0, -8, 10), (10, 0, 0), [(-4, -4, -1.2, 8, 8, 2.4, 'concha_osc')])
    for i in range(15):
        a = -70 + i * 10
        lomo = i % 2 == 0
        largo = 30 if lomo else 28
        ancho = 5.6
        parte(f'concha_r{i}', 'concha', (0, 0, 0.0 if lomo else 0.6), (0, 0, a), [
            (-ancho / 2, -largo, -0.7 if lomo else -0.5, ancho, largo, 1.4 if lomo else 1.0,
             'concha' if lomo else 'concha_osc'),
            (-ancho / 2 - 0.2, -largo - 1.4, -0.8, ancho + 0.4, 1.6, 1.6, 'nacar_luz')])
    parte('perla', 'concha', (0, 0, -1.8), cajas=[(-2.4, -2.4, -1.4, 4.8, 4.8, 2.8, 'perla')])

    # --- La barba: algas de la mandibula, como tentaculos
    for i, x in enumerate((-4.5, -2.5, -0.5, 1.5, 3.5)):
        largo = (20, 27, 32, 26, 19)[i]
        parte(f'barba_{i}', 'mandibula', (x + 0.5, 3.6, -11.2), (14, 0, (i - 2) * 5),
              [(-1.2, 0, 0, 2.6, largo, 0, 'alga')])

    # --- La capa de algas: de los hombros al suelo, por la espalda
    for i, x in enumerate((-11, -5.5, 0, 5.5, 11)):
        largo = (52, 60, 64, 60, 52)[i]
        parte(f'capa_{i}', 'torso', (x, -27, 8.2), (24, 0, (i - 2) * -3), [(-3, 0, 0, 6, largo, 0, 'alga_osc')])

    # --- Espinas de hueso por el lomo, entre las algas de la capa
    for i, y in enumerate((-26, -20, -14)):
        parte(f'espina_{i}', 'torso', (0, y, 8), (-55, 0, 0), [(-1.1, -12 + i * 2, -1.1, 2.2, 12 - i * 2, 2.2, 'hueso')])

    # --- Hombreras mas grandes y la caracola del hombro izquierdo
    for n in ('hombro_izq', 'hombro_der'):
        _escalar(n, 1.3)
    parte('caracola', 'hombro_izq', (1, -7, 0), (0, 0, 18), [
        (-7, -5, -7, 14, 5, 14, 'concha'),
        (-5.5, -9.5, -5.5, 11, 4.5, 11, 'concha'),
        (-4, -13, -4, 8, 3.5, 8, 'concha'),
        (-2.6, -16, -2.6, 5.2, 3, 5.2, 'concha'),
        (-1.3, -19.5, -1.3, 2.6, 3.5, 2.6, 'concha'),
        (6.5, -4, -1, 5, 2, 2, 'concha'), (-1, -8, 5, 2, 2, 5, 'concha'),
        (-9.5, -7, -1, 4, 2, 2, 'concha'), (-1, -3, -10, 2, 2, 4, 'concha')])

    # --- El tridente: mas largo, puntas mas grandes y la espiral de espuma
    PARTES['tridente'].cajas = [
        (-1.3, -30, -1.3, 2.6, 96, 2.6, 'prisma_osc'),
        (-2, 64, -2, 4, 4, 4, 'punta'),
        (-11, 67, -2, 22, 3.5, 4, 'prisma'),
        (-1.8, 70, -1.8, 3.6, 20, 3.6, 'punta'),
        (-10.5, 70, -1.5, 3, 14, 3, 'punta'),
        (7.5, 70, -1.5, 3, 14, 3, 'punta'),
        (-4.5, 81, -1, 2.5, 4, 2, 'punta'),
        (2, 81, -1, 2.5, 4, 2, 'punta'),
        (-11.5, 81, -1, 2, 4, 2, 'punta'), (9.5, 81, -1, 2, 4, 2, 'punta')]
    espiral = []
    for k in range(26):
        a = k * 0.62
        y = -22 + k * 3.3
        espiral.append((math.cos(a) * 3.2 - 0.8, y, math.sin(a) * 3.2 - 0.8, 1.6, 1.6, 1.6, 'espuma'))
    parte('espiral', 'tridente', (0, 0, 0), cajas=espiral)

    # --- Brazos y piernas mas gruesos (iban flacos bajo las hombreras nuevas),
    # ojos mas grandes y algas del faldon mas largas
    for n in ('brazo', 'antebrazo', 'mano', 'pierna', 'espinilla', 'pie'):
        for lado in ('izq', 'der'):
            _engordar(f'{n}_{lado}', 1.22)
    for n in ('ojo_izq', 'ojo_der'):
        _escalar(n, 1.35)
    for n in ('algas_del', 'algas_tras'):
        _escalar_y(n, 1.35)

# Se rellenan en nerea_juego_anim.py con la cinematica de la pose del molino
# (inicio en la mano, fin en el suelo), en el espacio de la pelvis.
MOLINO_CADENAS = {}

# ----------------------------------------------------------------------
#  Cinematica directa
# ----------------------------------------------------------------------
T, Rx, Ry, Rz, S = nm.vr.T, nm.vr.Rx, nm.vr.Ry, nm.vr.Rz, nm.vr.S
D2R = math.pi / 180


def matrices(pose=None):
    """Matriz de cada pieza (espacio del modelo) para una pose.

    pose: {pieza: {'rot': (grados que se suman), 'pos': (px que se suman, Y abajo),
                   'esc': (sx, sy, sz) multiplicadores, 'oculto': bool}}
    """
    pose = pose or {}
    out = {}

    def visitar(p, M):
        ex = pose.get(p.nombre, {})
        r = [p.rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        q = [p.pivote[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        e = ex.get('esc', (1, 1, 1))
        L = T(*q) @ Rz(r[2] * D2R) @ Ry(r[1] * D2R) @ Rx(r[0] * D2R) @ np.diag([e[0], e[1], e[2], 1.0])
        Mn = M @ L
        out[p.nombre] = Mn
        for h in p.hijos:
            visitar(h, Mn)

    for n in ORDEN:
        if PARTES[n].padre is None:
            visitar(PARTES[n], np.eye(4))
    return out


def punto(pose, pieza, local=(0, 0, 0)):
    """Punto de una pieza en el espacio del modelo (px)."""
    M = matrices(pose)[pieza]
    return (M @ np.array([*local, 1.0]))[:3]


def a_bloques(p):
    """Del modelo (px, Y abajo, frente -Z) al espacio de la entidad en bloques:
    (izquierda, alto, frente), con el factor de escala del renderer."""
    k = ESCALA / 16
    return (p[0] * k, (24.016 - p[1]) * k, -p[2] * k)


# ----------------------------------------------------------------------
#  Atlas UV: cada caja distinta (medidas + material) recibe su hueco
# ----------------------------------------------------------------------
ANCHO_ATLAS = 256


def tam_uv(c):
    x0, y0, z0, w, h, d, mat = c
    return int(math.ceil(2 * (d + w))) + 1, int(math.ceil(d + h)) + 1


def empaquetar():
    claves = {}
    for n in ORDEN:
        for c in PARTES[n].cajas:
            k = (round(c[3], 3), round(c[4], 3), round(c[5], 3), c[6])
            claves.setdefault(k, c)
    orden = sorted(claves, key=lambda k: (-tam_uv(claves[k])[1], -tam_uv(claves[k])[0]))
    uv = {}
    x = y = fila = 0
    for k in orden:
        w, h = tam_uv(claves[k])
        if x + w > ANCHO_ATLAS:
            x, y, fila = 0, y + fila, 0
        uv[k] = (x, y)
        x += w
        fila = max(fila, h)
    alto = y + fila
    alto_atlas = 1 << (alto - 1).bit_length()
    return uv, alto_atlas


def clave(c):
    return (round(c[3], 3), round(c[4], 3), round(c[5], 3), c[6])


def caras_uv(u, v, w, h, d):
    """Rectangulos (x, y, ancho, alto) de las seis caras, como ModelPart.Cube."""
    return {
        'arriba': (u + d, v, w, d),
        'abajo': (u + d + w, v, w, d),
        'oeste': (u, v + d, d, h),
        'frente': (u + d, v + d, w, h),
        'este': (u + d + w, v + d, d, h),
        'espalda': (u + 2 * d + w, v + d, w, h),
    }


def _hex(s):
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def pintar_atlas(uv, alto, fase=1):
    base = np.zeros((alto, ANCHO_ATLAS, 4), np.uint8)
    brillo = np.zeros_like(base)
    libre = np.zeros_like(base)
    rnd = random.Random(11)
    venas = random.Random(100 + fase)
    tabla_fase = dict(BRILLO)
    tabla_fase['ojo'] = OJOS_FASE[fase]
    tabla_fase['punta'] = PUNTAS_FASE[fase]
    tabla_fase['espuma'] = PUNTAS_FASE[fase]      # la espiral del tridente, del color de la fase
    hechas = set()
    for n in ORDEN:
        for c in PARTES[n].cajas:
            k = clave(c)
            if k in hechas:
                continue
            hechas.add(k)
            u, v = uv[k]
            w, h, d, mat = k
            loseta = MAT[mat]
            ox, oy = rnd.randrange(16), rnd.randrange(16)
            for cara, (fx, fy, fw, fh) in caras_uv(u, v, w, h, d).items():
                x0, y0 = int(math.floor(fx)), int(math.floor(fy))
                x1, y1 = int(math.ceil(fx + fw)), int(math.ceil(fy + fh))
                if x1 <= x0 or y1 <= y0:
                    continue
                for yy in range(y0, y1):
                    for xx in range(x0, x1):
                        col = loseta[(yy - y0 + oy) % 16, (xx - x0 + ox) % 16].astype(float)
                        if mat in CORALES and CORAL_MUERTO[fase] > 0:
                            # el coral se muere: hacia el gris y mas oscuro
                            gris = col[:3].mean()
                            k = CORAL_MUERTO[fase]
                            col[:3] = (col[:3] * (1 - k) + gris * k * np.array([0.95, 0.93, 1.0])) * (1 - 0.3 * k)
                        j = (yy - y0) / max(1, (y1 - y0 - 1))
                        if cara == 'abajo':
                            col[:3] *= 0.72
                        elif cara != 'arriba' and mat not in EMISIVOS:
                            # sombra de contacto abajo y canto claro arriba
                            if yy == y1 - 1 and y1 - y0 > 2:
                                col[:3] *= 0.78
                            elif yy == y0 and y1 - y0 > 2:
                                col[:3] = np.minimum(255, col[:3] * 1.12)
                            col[:3] *= 1.0 - 0.10 * j
                        base[yy, xx] = np.clip(col, 0, 255)
                        if mat in EMISIVOS:
                            dd = max(abs(xx - (x0 + x1 - 1) / 2) / max(1, (x1 - x0) / 2),
                                     abs(yy - (y0 + y1 - 1) / 2) / max(1, (y1 - y0) / 2))
                            for destino, tabla in ((brillo, tabla_fase), (libre, BRILLO_LIBRE)):
                                a, b = _hex(tabla[mat][0]), _hex(tabla[mat][1])
                                t = min(1.0, dd)
                                destino[yy, xx] = (*[int(a[i] + (b[i] - a[i]) * t) for i in range(3)], 255)
                            # la piel del corazon es su color normal, no el de liberado
                            base[yy, xx] = (*[int(x) for x in brillo[yy, xx][:3]], 255)
                        elif mat == 'abismo' and rnd.random() < 0.05:
                            # la maldicion asoma por la cavidad: motas magenta
                            brillo[yy, xx] = (180, 20, 90, 255)
                # Venas de la maldicion: lineas magenta que brillan en la oscuridad.
                if mat in CON_VENAS and VENAS_FASE[fase] > 0:
                    for _ in range(int((x1 - x0) * (y1 - y0) * VENAS_FASE[fase] + venas.random())):
                        gx = venas.randrange(x0, x1)
                        gy = venas.randrange(y0, y1)
                        for _ in range(venas.randint(3, 6)):
                            if x0 <= gx < x1 and y0 <= gy < y1:
                                base[gy, gx] = (120, 18, 70, 255)
                                brillo[gy, gx] = (230, 40, 140, 200)
                            gx += venas.choice((-1, 0, 1))
                            gy += venas.choice((-1, 0, 1))
                # Grietas del corazon: lineas oscuras que no brillan.
                for _ in range(GRIETAS.get(mat, 0)):
                    gx = rnd.randrange(x0, x1)
                    gy = rnd.randrange(y0, y1)
                    for _ in range(rnd.randint(3, 7)):
                        if x0 <= gx < x1 and y0 <= gy < y1:
                            base[gy, gx] = (34, 4, 16, 255)
                            brillo[gy, gx] = (0, 0, 0, 0)
                        gx += rnd.choice((-1, 0, 1))
                        gy += rnd.choice((-1, 1))
    return base, brillo, libre


# ----------------------------------------------------------------------
#  Exportar a Java
# ----------------------------------------------------------------------
def f(x):
    s = ('%.4f' % x).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s + 'F'


def var(n):
    return 'p_' + n


def java_malla(uv, alto):
    L = []
    L.append('package com.atalaya.client;')
    L.append('')
    L.append('import net.minecraft.client.model.geom.PartPose;')
    L.append('import net.minecraft.client.model.geom.builders.CubeDeformation;')
    L.append('import net.minecraft.client.model.geom.builders.CubeListBuilder;')
    L.append('import net.minecraft.client.model.geom.builders.LayerDefinition;')
    L.append('import net.minecraft.client.model.geom.builders.MeshDefinition;')
    L.append('import net.minecraft.client.model.geom.builders.PartDefinition;')
    L.append('')
    L.append('/**')
    L.append(' * La malla de Nerea. GENERADO por materiales/generadores/nerea_juego.py: no se')
    L.append(' * edita a mano. Cambiar una caja aqui sin cambiar el script descuadra la')
    L.append(' * textura, que se pinta con la misma cuadricula.')
    L.append(' */')
    L.append('public final class NereaMalla {')
    L.append('')
    L.append('    private NereaMalla() {')
    L.append('    }')
    L.append('')
    L.append('    public static LayerDefinition crear() {')
    L.append('        return crear(CubeDeformation.NONE);')
    L.append('    }')
    L.append('')
    L.append('    /** La misma malla hinchada: la capa del aura de la Furia (como las de Rajang y Aeralis). */')
    L.append('    public static LayerDefinition crearAura() {')
    L.append('        return crear(new CubeDeformation(1.2F));')
    L.append('    }')
    L.append('')
    L.append('    private static LayerDefinition crear(CubeDeformation infla) {')
    L.append('        MeshDefinition malla = new MeshDefinition();')
    L.append('        PartDefinition p_root = malla.getRoot();')
    for n in ORDEN:
        p = PARTES[n]
        padre = var(p.padre) if p.padre else 'p_root'
        cub = 'CubeListBuilder.create()'
        for c in p.cajas:
            u, v = uv[clave(c)]
            cub += f'\n                .texOffs({u}, {v}).addBox({f(c[0])}, {f(c[1])}, {f(c[2])}, {f(c[3])}, {f(c[4])}, {f(c[5])}, infla)'
        rx, ry, rz = [r * D2R for r in p.rot]
        pose = f'PartPose.offsetAndRotation({f(p.pivote[0])}, {f(p.pivote[1])}, {f(p.pivote[2])}, {f(rx)}, {f(ry)}, {f(rz)})'
        decl = f'PartDefinition {var(n)} = ' if p.hijos else ''
        L.append(f'        {decl}{padre}.addOrReplaceChild("{n}", {cub},\n                {pose});')
    L.append(f'        return LayerDefinition.create(malla, {ANCHO_ATLAS}, {alto});')
    L.append('    }')
    # El ancla del Arpon suelta (GanchoNereaRenderer): las mismas cajas y el
    # mismo atlas que la de la mano, girada para que su eje +Y vaya a +Z (el
    # sentido de vuelo) y centrada: la cruz y las unas delante, la argolla detras.
    ancla = PARTES['gancho_mano']

    def cubos(p):
        cub = 'CubeListBuilder.create()'
        for c in p.cajas:
            u, v = uv[clave(c)]
            cub += f'\n                .texOffs({u}, {v}).addBox({f(c[0])}, {f(c[1])}, {f(c[2])}, {f(c[3])}, {f(c[4])}, {f(c[5])}, infla)'
        return cub
    L.append('')
    L.append('    /** El ancla del Arpon cuando vuela: la de la mano, con la cruz por delante (+Z). */')
    L.append('    public static LayerDefinition crearAncla() {')
    L.append('        CubeDeformation infla = CubeDeformation.NONE;')
    L.append('        MeshDefinition malla = new MeshDefinition();')
    L.append('        PartDefinition p_root = malla.getRoot();')
    L.append(f'        PartDefinition p_ancla = p_root.addOrReplaceChild("ancla", {cubos(ancla)},\n'
             f'                PartPose.offsetAndRotation(0F, 0F, -6.5F, {f(math.pi / 2)}, 0F, 0F));')
    for h in ancla.hijos:
        rx, ry, rz = [r * D2R for r in h.rot]
        L.append(f'        p_ancla.addOrReplaceChild("{h.nombre}", {cubos(h)},\n'
                 f'                PartPose.offsetAndRotation({f(h.pivote[0])}, {f(h.pivote[1])}, {f(h.pivote[2])}, {f(rx)}, {f(ry)}, {f(rz)}));')
    L.append(f'        return LayerDefinition.create(malla, {ANCHO_ATLAS}, {alto});')
    L.append('    }')
    L.append('}')
    return '\n'.join(L) + '\n'


# ----------------------------------------------------------------------
#  Cuadrilateros con el UV real del atlas (para comprobar en los renders)
# ----------------------------------------------------------------------
def quads(pose, uv, alto, modelo_a_mundo):
    Ms = matrices(pose)
    out = []
    for n in ORDEN:
        if pose.get(n, {}).get('oculto'):
            continue
        # una pieza oculta oculta tambien a sus hijos
        q = PARTES[n].padre
        oculto = False
        while q:
            if pose.get(q, {}).get('oculto'):
                oculto = True
            q = PARTES[q].padre
        if oculto:
            continue
        M = modelo_a_mundo @ Ms[n]
        for c in PARTES[n].cajas:
            u, v = uv[clave(c)]
            for pts, uvs in nm.vr.caja_quads((u, v), c[:6], False, ANCHO_ATLAS, alto):
                w = [(M @ np.array([*q_, 1.0]))[:3] for q_ in pts]
                out.append((w, uvs, n))
    return out


if __name__ == '__main__':
    import nerea_juego_anim  # noqa: F401  (rellena MOLINO_CADENAS y exporta todo)

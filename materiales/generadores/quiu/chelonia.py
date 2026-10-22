"""Chelonia (DEDsafío 4, Aguas del Centro de Quiu): «la tortuga con plantas: semiacuática y acorazada; ataca de cerca y
lanza proyectiles; se esconde en el caparazón y solo le dañan los golpes cuerpo a cuerpo».

Copiada de los fotogramas 1080p del directo de elded del 29-09 (0:28:51-0:29:01; la principal, con la cámara del juego
resuelta a partir de las esquinas de la bandeja) y del icono del libro. Es una tortuga grande y de pie, sobre cuatro
patas de dos tramos abiertas en aspa (brazo con la sombra de la bandeja en el arranque y aleta más clara, acabada en
escalón con una uña parda). Lleva una caja de hojas de lados rectos y tapa plana metida en una bandeja blanca, y encima
una corona de once bloques blancos con las esquinas rosadas, abierta como una flor (los del borde, tumbados hacia fuera;
dos rectos y más altos en medio, cada uno con su anillo verde amarillento en la base). Del frente le sale un cuello
largo y grueso con cuatro racimos de cristales azules de punta blanca en 2 x 2, y al final una cabeza cuadrada: el
cráneo mostaza con el ojo amarillo y negro y la fosa nasal, una placa blanca en la nuca y una «L» blanca en cada mejilla
que tapa la mandíbula; entre el cráneo y la mandíbula, la boca morada con dientes en almena. Por detrás, una cola corta
con un racimo de pie y otro largo tumbado hacia atrás y hacia fuera.

Al morder se encabrita y levanta el cráneo (con las L y la placa) hasta ponerlo de pie; la mandíbula queda horizontal.
Escondida (estado1), mete el cuello y la cabeza en la caja de hojas, pliega las patas bajo la bandeja y apoya la panza.

Al píxel de Minecraft (16 por bloque), a su tamaño de juego: TAM = 1.
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
import bestiario_reptiles as R
from bestiario import T
from bestiario_hormigas import _azar1
from bestiario_limpio import rampa

ID = 'chelonia'
TAM = 1.0

# ======================================================================================================================
#  Los colores (paleta.json de la ficha, muestreada en los fotogramas; de oscuro a claro)
# ======================================================================================================================
TAPA_CHELONIA = rampa('1c3e18', '2a4c1e', '3b5721', '4d6429', '5f722c', '758435')
LADO_HOJAS_CHELONIA = rampa('183819', '23451c', '344f1f', '436126', '5a732a', '738a32')
AMARILLO_TAPA_CHELONIA = rampa('58701e', '6a8226', '7c922e', '90a236', 'a4b440')
BANDEJA_CHELONIA = rampa('8e8784', 'a8a29e', 'c4bfbb', 'd9d6d3', 'e8e6e4')
ROSA_BANDEJA_CHELONIA = rampa('968a84', 'aea19b', 'c4b7b0', 'd4c9c3', 'e0d7d2')
BLOQUE_CHELONIA = rampa('8e8884', 'afa7a2', 'c2bbb6', 'd1ccc8', 'dcdad7')
ESQUINA_CHELONIA = rampa('a2907d', 'b49c8c', 'c2ab9e', 'd2bcb0', 'd8c8c1')
HUESO_CHELONIA = rampa('8d807a', 'a79890', 'baada5', 'c9c0ba', 'd7cfcb')
CRANEO_CHELONIA = rampa('4e4528', '5e5436', '786839', '907e3a', 'a99333', 'c4a946')
CARA_CHELONIA = rampa('544525', '6a5a2c', '847236', '9c8a40', 'b8a24c')
MANDIBULA_CHELONIA = rampa('4c4020', '6a5a28', '8c7a30', 'ab9636', 'c8b044')
CUELLO_CHELONIA = rampa('4e4426', '625630', '766a38', '8a7c40', 'a0904a')
CUERPO_CHELONIA = rampa('34301e', '423a26', '4e452c', '5c5234', '6a5e3c')
PATA_CHELONIA = rampa('433310', '5f552e', '786836', '897937', 'a28a2c', 'b29a37')
BOCA_CHELONIA = rampa('230c1d', '331b2a', '45263e', '562e57', '6b4564')
DIENTE_CHELONIA = rampa('9a8e8a', 'b1a6a0', 'c9bcb6', 'dac3c8', 'ece0e0')
CRISTAL_CHELONIA = rampa('3c88d6', '4a98e2', '5ea8ea', '86c0f0', 'c4e2f8', 'f0f8fe')
OJO_CHELONIA = (L.H('d4c044'), L.H('2a1e06'))
UNA_CHELONIA = rampa('1e140a', '30200e', '463014', '5e4420', '76582c')
FOSA_CHELONIA = L.H('221e14')

# El huevo: la piel verde de la caja de hojas, el contorno blanco de la bandeja y oliva, y sus señas: los bloques
# blancos de la corona, el borde blanco, un racimo azul de punta blanca, las patas mostaza y la cabeza.
HUEVO = (('517433', '315823', '1c3e18'), ('dad6d3', '786836'),
         [((6, 3), 'e0dfde'), ((8, 2), 'e0dfde'), ((10, 3), 'e0dfde'), ((5, 7), 'dddfdd'), ((6, 7), 'dddfdd'),
          ((7, 7), 'dddfdd'), ((8, 7), 'dddfdd'), ((9, 7), 'dddfdd'), ((10, 7), 'dddfdd'), ((11, 6), '3179af'),
          ((11, 5), 'd8e4f0'), ((4, 10), 'a28a2c'), ((10, 11), 'a28a2c'), ((12, 9), '907e3a'), ((12, 10), 'e3dddb')])

# ======================================================================================================================
#  Las medidas (px de Minecraft, el boceto: Y arriba, el frente en +Z, +X la izquierda del mob)
# ======================================================================================================================
Y_PANZA_CHELONIA = 4.5            # el hueco bajo la panza
Y_BANDEJA_CHELONIA = 8.5          # el cuerpo oliva va de la panza hasta aquí
ALTO_BANDEJA_CHELONIA = 3.5
Y_TAPA_CHELONIA = 20.0            # la tapa de la caja de hojas (8 px por encima de la bandeja)
BANDEJA_XZ_CHELONIA = (22.0, 30.0)
HOJAS_XZ_CHELONIA = (18.5, 26.5)  # metida 1,75 px por dentro del borde
CUERPO_XZ_CHELONIA = (19.0, 27.0)
LADO_BLOQUE_CHELONIA = 4.0
# La corona de bloques blancos: (largo 0-26 desde atrás, ancho 0-18 desde el lado que se ve en la principal, hacia
# dónde se tumba en x y en z, cuánto se tumba, alto). La disposición de la ficha (53s70: las 4 esquinas tumbadas en
# diagonal, 2 en el lado cercano y 3 en el lejano tumbados hacia fuera, sin bloque en medio del lado cercano, y 2 rectos
# y más altos en el centro), ajustada sitio a sitio con la cámara del juego sobre la principal (ajustar_corona.py).
CORONA_CHELONIA = [
    (0.0, 0.5, -1, -1, 12, 4.0), (2.0, 18.0, 1, -1, 52, 4.0), (26.0, 4.0, -1, 1, 16, 4.0), (24.5, 11.0, 1, 1, 66, 4.0),
    (8.5, 2.0, -1, 0, 40, 4.0), (21.0, 1.0, -1, 0, 40, 4.0),
    (7.5, 17.5, 1, 0, 41, 4.0), (12.5, 15.5, 1, 0, 38, 4.0), (20.5, 15.5, 1, 0, 16, 4.0),
    (7.0, 9.0, 0, 0, 0, 6.5), (16.0, 9.0, 0, 0, 0, 6.5),
]
# El cuello y la cabeza
CUELLO_Y_CHELONIA = (6.0, 13.0)
CUELLO_Z_CHELONIA = (12.0, 26.5)
CUELLO_X_CHELONIA = 8.0
CABEZA_Z_CHELONIA = (26.0, 39.0)
CABEZA_X_CHELONIA = 9.0
CRANEO_Y_CHELONIA = (12.0, 16.0)
MANDIBULA_Y_CHELONIA = (8.0, 11.0)
GOZNE_CHELONIA = (0.0, 11.5, 27.0)
# La placa blanca de la nuca: (ancho, grueso, largo, dónde cae su centro a lo largo desde la nuca)
PLACA_CHELONIA = (5.0, 2.0, 6.0, 1.5)
# El cuerpo gira sobre las patas de atrás (al encabritarse no hunde la cola)
PIVOTE_CUERPO_CHELONIA = (0.0, 4.0, -10.0)
# La cola: la altura de su centro
COLA_Y_CHELONIA = 7.0
# Las patas: dónde nacen (bajo el borde blanco, a media altura del cuerpo) y cómo van: (nombre, lado, delante, abierta
# desde el costado vista desde arriba, lo que baja el brazo, lo que baja la aleta), en grados
X_HOMBRO_CHELONIA, Y_HOMBRO_CHELONIA = 9.0, 7.5
# (delante: dónde nace a lo largo, abierta, lo que baja el brazo, lo que baja la aleta), y lo mismo detrás
PATA_DEL_CHELONIA = (7.0, 12.0, 42.0, -8.0)
PATA_TRA_CHELONIA = (-7.0, 32.0, 25.0, 15.0)


def geometria_patas_chelonia():
    out = []
    for nombre, lado, delante in (('pata_del_i', 1, 1), ('pata_del_d', -1, 1), ('pata_tra_i', 1, -1),
                                  ('pata_tra_d', -1, -1)):
        z, abre, baja1, baja2 = PATA_DEL_CHELONIA if delante > 0 else PATA_TRA_CHELONIA
        out.append((nombre, lado, delante, z, abre, baja1, baja2))
    return out
# Las patas: (largo, alto, ancho) del brazo y de la aleta
BRAZO_CHELONIA = (10.0, 3.0, 7.0)
ALETA_CHELONIA = (7.0, 2.0, 8.0)


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def _tex_chelonia(Rm, v, dentro=None):
    """Cada píxel, un tono de la rampa (sin mezclas)."""
    tex = L._rgba(L.color_continuo(Rm, np.clip(np.round(v), 0, len(Rm) - 1)))
    if dentro is not None:
        tex[..., 3] = np.where(dentro, 255, 0)
    return tex


def _parches_chelonia(tw, th, s, P=10, oscuro=1.4, claro=3.0, brillo=4.4, canto=0.4):
    """Las hojas de la caja: rombos de P en diagonal; dentro, bandas de 2 px en diagonal (en un sentido o en el otro
    según la hoja); el canto entre hojas, oscuro, y alguna hoja con la banda clara amarillenta."""
    xs, ys = L._malla(tw, th)
    a, b = xs + ys, xs - ys + 32 * P
    ca, cb = a // P, b // P
    ua, ub = a % P, b % P
    sentido = _azar1(ca, cb, s) > 0.5
    t = np.where(sentido, ua, ub)
    banda = (t // 2) % 2
    v = np.where(banda == 1, claro, oscuro)
    borde = (ua == 0) | (ub == 0)
    v = np.where(borde, canto, v)
    clara = _azar1(ca, cb, s + 5) > 0.75
    return np.where(clara & (banda == 1) & ~borde, brillo, v)


def hojas_chelonia(nombre, bloques=()):
    """La caja de hojas: la tapa con su dibujo y un cuadro verde amarillento alrededor del pie de cada bloque blanco
    ('bloques': (columna, fila, lado) en la cara de arriba); los lados, el mismo dibujo más oscuro."""
    def fn(tw, th, c, s):
        if c == 'arriba':
            v = _parches_chelonia(tw, th, s, oscuro=1.0, claro=2.2, brillo=3.2, canto=0.3)
            tex = _tex_chelonia(TAPA_CHELONIA, v)
            xs, ys = L._malla(tw, th)
            for (cx, cy, lado) in bloques:
                r = lado / 2.0
                dx, dy = np.abs(xs + 0.5 - cx), np.abs(ys + 0.5 - cy)
                cuadro = (dx <= r) & (dy <= r) & ((dx > r - 1.0) | (dy > r - 1.0))
                if cuadro.any():
                    va = 2.0 + (v[cuadro] > 2.5) * 1.0 - (v[cuadro] < 1.0) * 1.0
                    tex[cuadro, :3] = np.round(L.color_continuo(AMARILLO_TAPA_CHELONIA, np.clip(va, 0, 4)))
            return tex, None
        if c == 'abajo':
            return _tex_chelonia(LADO_HOJAS_CHELONIA, np.full((th, tw), 0.6)), None
        xs, ys = L._malla(tw, th)
        v = _parches_chelonia(tw, th, s + 11, oscuro=2.3, claro=3.4, brillo=4.0, canto=1.2)
        v = v + (ys == 0) * 0.8
        return _tex_chelonia(LADO_HOJAS_CHELONIA, v), None
    return B.Pintor(nombre, fn)


def bandeja_chelonia(nombre):
    """La bandeja blanca: blanco hueso con manchas rosadas de 1-2 px; el canto de arriba, claro."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), 3.6)
        elif c == 'abajo':
            v = np.full((th, tw), 1.4)
        else:
            v = 2.9 + (ys == 0) * 0.7 - (ys == th - 1) * 0.8
        mancha = _azar1(xs // 2, ys, s + 3) < 0.2
        tex = _tex_chelonia(BANDEJA_CHELONIA, v)
        rosa = _tex_chelonia(ROSA_BANDEJA_CHELONIA, v - 0.2)
        tex[mancha] = rosa[mancha]
        return tex, None
    return B.Pintor(nombre, fn)


def bloque_chelonia(nombre):
    """Un bloque blanco liso con un píxel rosado en cada esquina de cada cara."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), 3.6)
        elif c == 'abajo':
            v = np.full((th, tw), 1.6)
        else:
            v = 2.6 + (ys == 0) * 0.4 - (ys == th - 1) * 0.6
        tex = _tex_chelonia(BLOQUE_CHELONIA, v)
        esq = ((xs == 0) | (xs == tw - 1)) & ((ys == 0) | (ys == th - 1))
        tex[esq, :3] = np.round(L.color_continuo(ESQUINA_CHELONIA, np.full(int(esq.sum()), 3.0)))
        return tex, None
    return B.Pintor(nombre, fn)


def hueso_chelonia(nombre):
    """El hueso de las L y de la placa de la nuca: blanco rosado con manchas rosadas."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), 3.5)
        elif c == 'abajo':
            v = np.full((th, tw), 1.5)
        else:
            v = 2.9 + (ys == 0) * 0.6 - (ys == th - 1) * 0.6
        tex = _tex_chelonia(HUESO_CHELONIA, v)
        mancha = _azar1(xs // 2, ys // 2, s + 7) < 0.25
        tex[mancha] = _tex_chelonia(HUESO_CHELONIA, v - 1.0)[mancha]
        return tex, None
    return B.Pintor(nombre, fn)


def vetas_chelonia(nombre, Rm, base=2.0):
    """Piel oliva con vetas verticales de 1-2 px de largos distintos (el cuerpo bajo la bandeja, el cuello, la cola)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), base + 0.8)
        elif c == 'abajo':
            v = np.full((th, tw), base - 0.8)
        else:
            v = base + (ys == 0) * 0.6 - (ys == th - 1) * 0.5
        col = _azar1(xs, np.zeros_like(xs), s + 13)
        largo = _azar1(xs, ys // 3, s + 17)
        v = v - ((col < 0.3) & (largo > 0.25)) * 1.0 + ((col > 0.82) & (largo > 0.4)) * 0.8
        return _tex_chelonia(Rm, v), None
    return B.Pintor(nombre, fn)


def panza_chelonia(nombre):
    """La panza: el oliva de las patas en tablas de 2 px a lo largo, con la junta oscura."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = 2.0 - ((xs % 3) == 2) * 1.0 + (_azar1(xs, ys // 4, s) > 0.85) * 0.6
        return _tex_chelonia(PATA_CHELONIA, v), None
    return B.Pintor(nombre, fn)


def pata_chelonia(nombre, base=2.2, claro=0.0, sombra=0.0):
    """Las patas (su largo, a lo ancho de la textura en las caras de arriba, abajo, frente y atrás): oliva mostaza con
    rayas oscuras de 1 px a lo largo y manchas amarillas claras de 2 x 2."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), base + claro)
        if c == 'abajo':
            v = v - 0.6
        if c in ('arriba', 'abajo', 'frente', 'atras'):
            raya = ((ys % 3) == 1 if th >= 4 else (ys == th - 1)) & (_azar1(xs // 3, ys, s + 9) > 0.25)
            v = v - raya * 0.9
            mancha = (_azar1(xs // 2, ys // 2, s + 3) > 0.68) & ~raya
            v = v + mancha * 1.5
        else:
            v = v + (_azar1(xs // 2, ys // 2, s + 5) > 0.7) * 1.2
        if sombra and c in ('arriba', 'frente', 'atras', 'abajo'):
            # la sombra de la bandeja en el arranque (el lado de la textura que va pegado al cuerpo)
            u = (xs + 0.5) / tw if c in ('arriba', 'frente', 'abajo') else 1 - (xs + 0.5) / tw
            v = v - sombra * np.clip(1.0 - u / 0.4, 0, 1)
        elif sombra and c == 'izq':
            v = v - sombra
        return _tex_chelonia(PATA_CHELONIA, v), None
    return B.Pintor(nombre, fn)


def una_chelonia(nombre):
    """La uña de la punta de la aleta (lámina, al píxel fino): un triángulo pardo oscuro, ancho en la raíz (abajo en la
    textura) y en punta arriba, con el canto de la izquierda un tono más claro."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        t = (ys + 0.5) / th                              # 0 en la punta, 1 en la raíz
        x = (xs + 0.5) / tw
        dentro = np.abs(x - 0.5) < 0.5 * t + 0.06
        v = 1.4 + (x < 0.5) * 0.8 + (1 - t) * 0.6
        return _tex_chelonia(UNA_CHELONIA, v, dentro), None
    return B.fino(B.Pintor(nombre, fn), R.FINO)


# El marco de la uña: su alto (la Y de la lámina) a lo largo de la aleta, su ancho a lo ancho y la cara hacia arriba.
TUMBADA_CHELONIA = np.array(((0, 1, 0, 0), (0, 0, 1, 0), (1, 0, 0, 0), (0, 0, 0, 1)), float)


def craneo_chelonia(nombre, largo, alto, ojo_z, fosa_z, ojo_fila, fosa_fila):
    """El cráneo: la tapa mostaza, oscura en la nuca y clara hacia el hocico, con manchas; los lados más oscuros, con el
    ojo (1 px amarillo detrás y 1 px negro delante, el negro hacia el hocico) y la fosa nasal. 'ojo_z' y 'fosa_z':
    la columna (desde atrás) del píxel amarillo y de la fosa."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            t = (ys + 0.5) / th                                     # 0 en la nuca, 1 en el hocico
            v = 1.4 + 3.2 * t
            mancha = _azar1(xs // 2, ys // 2, s + 5) < 0.22
            v = v - mancha * 1.2
            return _tex_chelonia(CRANEO_CHELONIA, v), None
        if c == 'abajo':
            return _tex_chelonia(BOCA_CHELONIA, np.full((th, tw), 2.0)), None
        v = 2.0 + (ys == 0) * 0.8
        mancha = _azar1(xs // 2, ys // 2, s + 9) < 0.25
        v = v - mancha * 0.8
        tex = _tex_chelonia(CARA_CHELONIA, v)
        if c in ('izq', 'der'):
            def col(z):
                return z if c == 'izq' else tw - 1 - z
            for z, color in ((ojo_z, OJO_CHELONIA[0]), (ojo_z + 1, OJO_CHELONIA[1])):
                if 0 <= ojo_fila < th:
                    tex[ojo_fila, col(z), :3] = np.round(color)
            if 0 <= fosa_fila < th:
                tex[fosa_fila, col(fosa_z), :3] = np.round(FOSA_CHELONIA)
        return tex, None
    return B.Pintor(nombre, fn)


def mandibula_chelonia(nombre):
    """La mandíbula: amarillo oliva con manchas; la tapa, morada (la lengua)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = 2.0 + (_azar1(xs, ys, s) > 0.8) * 1.0
            return _tex_chelonia(BOCA_CHELONIA, v), None
        if c == 'abajo':
            return _tex_chelonia(MANDIBULA_CHELONIA, np.full((th, tw), 1.2)), None
        v = 2.4 + (ys == 0) * 0.6 - (ys == th - 1) * 0.6
        mancha = _azar1(xs // 2, ys // 2, s + 9) < 0.3
        v = v - mancha * 1.0
        return _tex_chelonia(MANDIBULA_CHELONIA, v), None
    return B.Pintor(nombre, fn)


def boca_chelonia(nombre):
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = 2.0 + (_azar1(xs, ys, s) > 0.8) * 1.0 - (_azar1(xs, ys, s + 1) < 0.15) * 1.0
        return _tex_chelonia(BOCA_CHELONIA, v), None
    return B.Pintor(nombre, fn)


def almenas_chelonia(nombre, arriba=True, fase=0):
    """Los dientes en una 2.ª capa: 1 px de ancho y todo el alto de la capa, con huecos de 1 px, como almenas; en los
    lados y en el frente (arriba, abajo y atrás, nada). La raíz, un tono más oscura."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c not in ('izq', 'der', 'frente'):
            return tex, None
        diente = ((xs + fase) % 2) == 0
        raiz = (ys == 0) if arriba else (ys == th - 1)
        v = 3.2 - raiz * 0.8
        tex = _tex_chelonia(DIENTE_CHELONIA, v)
        tex[..., 3] = np.where(diente, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


# Los racimos de cristales, al píxel (copiados de los fotogramas 137 y 145 a 60 fps): un abeto de escalones, la
# mitad de arriba y el borde de la izquierda blancos, abajo azul intenso. w blanco, l azul muy claro, m azul claro,
# b azul, d azul oscuro.
RACIMO_ALTO_CHELONIA = [
    '...w...',
    '..wl...',
    '..lmm..',
    '.lmbmb.',
    '.mbbbbm',
    'mbbdbbb',
    'bbddbdb',
]
RACIMO_BAJO_CHELONIA = [
    '..w..w.',
    '.wlm.lm',
    'lmbmlmb',
    'mbbbmbb',
    'bbdbbdb',
]
RACIMO_COLA_CHELONIA = [
    '..w...',
    '.wwl.w',
    '.wlmwl',
    'wlmbml',
    'lmbbbm',
    'mbbdbb',
]
RACIMO_COLA_LARGO_CHELONIA = [
    '...w..',
    '..wl..',
    '.wlmw.',
    '.lmbl.',
    'wmbbmw',
    'lbbdbl',
    'mbddbm',
]
TONO_RACIMO_CHELONIA = {'w': 5, 'l': 4, 'm': 3, 'b': 2, 'd': 1}


def racimo_chelonia(nombre, Rm, mapa):
    """Un racimo de cristales (lámina): el mapa de píxeles, estirado a la cara; lo de alrededor, vacío."""
    filas = len(mapa)
    cols = len(mapa[0])

    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        fx = np.minimum((xs * cols) // max(1, tw), cols - 1)
        fy = np.minimum((ys * filas) // max(1, th), filas - 1)
        letras = np.array([list(f) for f in mapa])[fy, fx]
        dentro = letras != '.'
        v = np.zeros((th, tw))
        for k, tono in TONO_RACIMO_CHELONIA.items():
            v[letras == k] = tono
        return _tex_chelonia(Rm, v, dentro), None
    return B.Pintor(nombre, fn)


# ======================================================================================================================
#  Las piezas
# ======================================================================================================================
def cruz_chelonia(m, parte, M, ancho, alto, pint, fuera=-1, laminas=(45.0, -45.0)):
    """Un racimo en láminas cruzadas (por defecto, dos en X a 45°, como el racimo de amatista; con 'laminas', las que
    se pidan). La luz de Minecraft ilumina cada cara por su normal (la de la lámina es el eje +Z de su marco), así que
    cada lámina se pone en el sentido cuya cara mira más hacia arriba y hacia fuera del cuerpo ('fuera': -1 si el
    racimo va en el lado -X, 1 en el +X)."""
    hacia = np.array((0.6 * fuera, 1.0, 0.0))
    for g in laminas:
        giro = max((g, g + 180.0), key=lambda a_: float((M @ B.girar((0, a_, 0)))[:3, 2] @ hacia))
        R.lamina(m, parte, M @ B.girar((0, giro, 0)), ancho, alto, pint)


ESTRELLA_CHELONIA = (90.0, 30.0, -30.0)     # tres láminas a 60°: el racimo se ve lleno desde cualquier lado


def _rodrigues_chelonia(dx, dz, ang):
    """La matriz que tumba el +Y 'ang' grados hacia la dirección horizontal (dx, dz)."""
    n = math.hypot(dx, dz)
    M = np.eye(4)
    if n < 1e-9 or abs(ang) < 1e-9:
        return M
    k = np.array((dz / n, 0.0, -dx / n))
    th = math.radians(ang)
    K = np.array(((0, -k[2], k[1]), (k[2], 0, -k[0]), (-k[1], k[0], 0)))
    M[:3, :3] = np.eye(3) * math.cos(th) + math.sin(th) * K + (1 - math.cos(th)) * np.outer(k, k)
    return M


def _marco_pata_chelonia(origen, lado, delante, abre, baja):
    """El marco de un tramo de pata: X a lo largo del tramo (hacia fuera y abajo), Y la cara ancha (hacia arriba) y Z
    a lo ancho. 'abre': cuánto se abre hacia delante (o hacia atrás) desde el costado, vista desde arriba; 'baja':
    cuánto baja desde la horizontal."""
    a, b = math.radians(abre), math.radians(baja)
    e1 = np.array((lado * math.cos(a) * math.cos(b), -math.sin(b), delante * math.sin(a) * math.cos(b)))
    e3 = np.array((-delante * math.sin(a), 0.0, lado * math.cos(a)))
    e3 = e3 / np.linalg.norm(e3)
    e2 = np.cross(e3, e1)
    if e2[1] < 0:
        e3, e2 = -e3, -e2
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = e1, e2, e3, origen
    return M


def construir():
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0

    # --- los pintores
    blanco = bandeja_chelonia('bandeja_chelonia')
    bloque = bloque_chelonia('bloque_chelonia')
    hueso = hueso_chelonia('hueso_chelonia')
    cuerpo = vetas_chelonia('cuerpo_chelonia', CUERPO_CHELONIA, base=2.2)
    cuello = vetas_chelonia('cuello_chelonia', CUELLO_CHELONIA, base=2.4)
    panza = panza_chelonia('panza_chelonia')
    pata = pata_chelonia('pata_chelonia', base=2.0, sombra=1.6)
    aleta = pata_chelonia('aleta_chelonia', base=2.6, claro=0.6)
    boca = boca_chelonia('boca_chelonia')
    mand = mandibula_chelonia('mandibula_chelonia')
    una = una_chelonia('una_chelonia')

    # --- el cuerpo, la bandeja y la caja de hojas
    m.parte('cuerpo', None, PIVOTE_CUERPO_CHELONIA)
    cx, cz = CUERPO_XZ_CHELONIA
    ycu = Y_BANDEJA_CHELONIA + 0.5
    m.caja('cuerpo', (0, (Y_PANZA_CHELONIA + ycu) / 2, 0), (cx, ycu - Y_PANZA_CHELONIA, cz), cuerpo,
           caras={'abajo': panza})
    bx, bz = BANDEJA_XZ_CHELONIA
    m.caja('cuerpo', (0, Y_BANDEJA_CHELONIA + ALTO_BANDEJA_CHELONIA / 2, 0), (bx, ALTO_BANDEJA_CHELONIA, bz), blanco)

    # La corona (CORONA_CHELONIA): (largo 0-26 desde atrás, ancho 0-18 desde el lado que se ve en la principal, -X).
    hx, hz = HOJAS_XZ_CHELONIA
    LB = LADO_BLOQUE_CHELONIA
    bloques_tapa = []
    for fx, fz, dx, dz, inc, alto in CORONA_CHELONIA:
        z = -hz / 2 + fx * hz / 26.0
        x = -hx / 2 + fz * hx / 18.0
        hundido = (LB / 2) * math.sin(math.radians(inc)) + (1.5 if inc == 0 else 0.4)
        M = T(x, Y_TAPA_CHELONIA - hundido, z) @ _rodrigues_chelonia(dx, dz, inc)
        m._caja('cuerpo', M, -LB / 2, 0.0, -LB / 2, LB, alto, LB, bloque)
        bloques_tapa.append((x + hx / 2, z + hz / 2, LB + 2))
    hojas = hojas_chelonia('hojas_chelonia', bloques_tapa)
    m.caja('cuerpo', (0, (ycu + Y_TAPA_CHELONIA) / 2, 0), (hx, Y_TAPA_CHELONIA - ycu, hz), hojas)

    # --- la cola: un muñón corto (sale 5 px por detrás de la bandeja) con dos racimos de cristales: uno de pie y otro
    # tumbado hacia atrás, largo, que asoma por detrás de la bandeja a la altura de su canto
    yc = COLA_Y_CHELONIA
    m.parte('cola', 'cuerpo', (0, yc, -bz / 2 + 2))
    m.caja('cola', (0, yc, -bz / 2 - 1.0), (5, 4, 8), cuerpo)
    cc = racimo_chelonia('cristal_cola_chelonia', CRISTAL_CHELONIA, RACIMO_COLA_CHELONIA)
    cl = racimo_chelonia('cristal_cola_largo_chelonia', CRISTAL_CHELONIA, RACIMO_COLA_LARGO_CHELONIA)
    cruz_chelonia(m, 'cola', T(-0.5, yc + 1.6, -bz / 2 - 1.5), 6.0, 6.0, cc, fuera=-1)
    # el tumbado: hacia atrás (62° desde la vertical) y 30° hacia fuera, al lado que se ve en la principal (-X)
    cruz_chelonia(m, 'cola', T(-0.8, yc + 1.2, -bz / 2 - 4.0) @ B.girar((0, 30, 0)) @ B.girar((-62, 0, 0)), 6.0, 7.0,
                  cl, fuera=-1)

    # --- el cuello, con los cuatro racimos de cristales en 2 x 2
    y_c0, y_c1 = CUELLO_Y_CHELONIA
    z_c0, z_c1 = CUELLO_Z_CHELONIA
    m.parte('cuello', 'cuerpo', (0, (y_c0 + y_c1) / 2, z_c0 + 2))
    m.caja('cuello', (0, (y_c0 + y_c1) / 2, (z_c0 + z_c1) / 2), (CUELLO_X_CHELONIA, y_c1 - y_c0, z_c1 - z_c0), cuello)
    alto_r = racimo_chelonia('cristal_alto_chelonia', CRISTAL_CHELONIA, RACIMO_ALTO_CHELONIA)
    bajo_r = racimo_chelonia('cristal_bajo_chelonia', CRISTAL_CHELONIA, RACIMO_BAJO_CHELONIA)
    # 2 x 2: el par de atrás, más alto, junto a la bandeja; el de delante, a media altura del cuello
    for z, alto, pint, sep in ((bz / 2 + 2.5, 7.0, alto_r, 2.3), (bz / 2 + 7.0, 5.0, bajo_r, 2.0)):
        for x in (-sep, sep):
            cruz_chelonia(m, 'cuello', T(x, y_c1 - 0.4, z) @ B.girar((0, 0, -x * 3)), 6.0, alto, pint,
                          fuera=1 if x > 0 else -1, laminas=ESTRELLA_CHELONIA)

    # --- la cabeza: cráneo (con las L, la placa y los dientes de arriba) y mandíbula (con la lengua y los de abajo)
    za, zb = CABEZA_Z_CHELONIA
    W = CABEZA_X_CHELONIA
    m.parte('cabeza', 'cuello', (0, 11.0, za))
    m.parte('craneo', 'cabeza', GOZNE_CHELONIA)
    ya, yb = CRANEO_Y_CHELONIA
    largo = int(zb - za)
    craneo = craneo_chelonia('craneo_chelonia', largo, int(yb - ya), ojo_z=5, fosa_z=largo - 2, ojo_fila=1,
                             fosa_fila=1)
    m.caja('craneo', (0, (ya + yb) / 2, (za + zb) / 2), (W, yb - ya, zb - za), craneo)
    # la placa de la nuca, que sobresale hacia atrás por encima del cuello
    px_, py_, pz_, pzc = PLACA_CHELONIA
    m.caja('craneo', (0, yb + py_ / 2, za + pzc), (px_, py_, pz_), hueso)
    # las L de las mejillas: el brazo de pie detrás del ojo y el tumbado, que tapa la mandíbula
    ma, mb = MANDIBULA_Y_CHELONIA
    for lado in (1, -1):
        x = lado * (W / 2 + 1.0)
        m.caja('craneo', (x, (ma + mb) / 2, za + 2 + (zb - za - 2) / 2), (2.0, mb - ma, zb - za - 2), hueso)
        m.caja('craneo', (x, (mb + ya + 2.5) / 2, za + 3.0), (2.0, ya + 2.5 - mb, 2.0), hueso)
    # los dientes de arriba, que cuelgan del cráneo (2.ª capa, algo más ancha que la cabeza)
    m.caja('craneo', (0, ya - 1.0, (za + 1 + zb) / 2 + 0.03), (W + 0.12, 2.0, zb - za - 1 + 0.06),
           almenas_chelonia('dientes_arriba_chelonia', arriba=True))
    m.parte('mandibula', 'cabeza', (0, mb, za + 1.0))
    m.caja('mandibula', (0, (ma + mb) / 2, (za + 1 + zb) / 2), (W - 0.2, mb - ma, zb - za - 1), mand)
    # la lengua: lo morado que se ve por la rendija de la boca
    m.caja('mandibula', (0, mb + 0.5, (za + 1 + zb) / 2), (W - 1.0, 1.0, zb - za - 2), boca)
    # los dientes de abajo, de pie en el canto de la mandíbula (por dentro del cráneo: solo se ven al abrir)
    m.caja('mandibula', (0, mb + 1.0, (za + 1 + zb) / 2), (W - 0.6, 2.0, zb - za - 1.4),
           almenas_chelonia('dientes_abajo_chelonia', arriba=False, fase=0))

    # --- las patas: dos tramos (el brazo y la aleta), abiertas en aspa
    l1, t1, w1 = BRAZO_CHELONIA
    l2, t2, w2 = ALETA_CHELONIA
    for nombre, lado, delante, z, abre, baja1, baja2 in geometria_patas_chelonia():
        nom, ld = nombre.split('_')[1], nombre.split('_')[2]
        if True:
            hombro = np.array((lado * X_HOMBRO_CHELONIA, Y_HOMBRO_CHELONIA, z))
            M1 = _marco_pata_chelonia(hombro, lado, delante, abre, baja1)
            n1 = m.parte(f'pata_{nom}_{ld}', 'cuerpo', tuple(hombro))
            R.caja_en(m, n1, M1, (l1 / 2, 0, 0), (l1, t1, w1), pata)
            codo = R.P(M1, (l1 - 0.5, 0, 0))
            M2 = _marco_pata_chelonia(codo, lado, delante, abre, baja2)
            n2 = m.parte(f'aleta_{nom}_{ld}', n1, tuple(codo))
            R.caja_en(m, n2, M2, (l2 / 2, -0.4, 0), (l2, t2, w2), aleta)
            # la punta, en escalón: 2 px más, 2 px más estrecha, corrida hacia el borde de delante de la aleta
            ade = -delante * lado                       # hacia dónde cae el borde de delante en el eje Z de la aleta
            R.caja_en(m, n2, M2, (l2 + 1.0, -0.6, ade * 1.0), (2.0, t2 - 0.4, w2 - 2.0), aleta)
            # la uña, tumbada sobre la punta y mirando hacia arriba
            R.lamina(m, n2, M2 @ T(l2 + 1.4, -0.6 + (t2 - 0.4) / 2 + 0.02, ade * 2.2) @ TUMBADA_CHELONIA, 1.6, 2.4,
                     una)

    m.mirar(('cabeza', 0.7), ('cuello', 0.3))
    anims_chelonia(m)
    return m


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
PATAS_CHELONIA = (  # (pata, lado, fase): en diagonal (la ficha), la de delante de un lado con la de atrás del otro
    ('pata_del_i', 1, 0.0), ('pata_tra_d', -1, 0.0), ('pata_del_d', -1, 0.5), ('pata_tra_i', 1, 0.5))


def _paso_chelonia(p, apoyo=0.65, adelante=20.0, alza=16.0):
    """Una pata en un paso (p de 0 a 1): apoyada, barre de delante (+adelante) hacia atrás; luego se levanta y vuelve
    por el aire. Devuelve (hacia delante, alzada) en grados."""
    if p < apoyo:
        return adelante * math.cos(math.pi * p / apoyo), 0.0
    u = (p - apoyo) / (1.0 - apoyo)
    return -adelante * math.cos(math.pi * u), alza * math.sin(math.pi * u)


def _ciclo_chelonia(a, parte, fn, largo, n=16):
    """Claves en bucle: fn(p) -> (rx, ry, rz) en n puntos del ciclo, cerrado en 0 y en el largo."""
    ks = []
    for i in range(n + 1):
        p = (i % n) / n
        ks.append((largo * i / n, *fn(p)))
    a.rot(parte, ks)


def anims_chelonia(m):
    # --- reposo: respira, mira a un lado y a otro y menea la cola
    r = m.anim('reposo', 4.0, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.25, periodo=4.0)
    r.rot('cabeza', [(0, 0, 0, 0), (1.0, -3, 12, 0), (2.0, 0, 0, 0), (3.0, -3, -12, 0), (4.0, 0, 0, 0)])
    r.rot('cuello', [(0, 0, 0, 0), (1.0, -4, 4, 0), (2.0, 0, 0, 0), (3.0, -4, -4, 0), (4.0, 0, 0, 0)])
    r.onda('cola', 'r', 1, 6, periodo=4.0)
    # --- andar: las patas en diagonal, con el apoyo largo; el cuello va algo levantado y cabecea con el paso
    T_ = 1.6
    a = m.anim('andar', T_, bucle=True)
    for nombre, lado, fase in PATAS_CHELONIA:
        def fn(p, lado=lado, fase=fase):
            adelante, alza = _paso_chelonia((p + fase) % 1.0)
            return 0.0, -lado * adelante, lado * alza
        _ciclo_chelonia(a, nombre, fn, T_)
        aleta = 'aleta' + nombre[4:]

        def fn2(p, lado=lado, fase=fase):
            _, alza = _paso_chelonia((p + fase) % 1.0)
            return 0.0, 0.0, lado * alza * 0.6
        _ciclo_chelonia(a, aleta, fn2, T_)
    a.onda('cuerpo', 'm', 1, 0.3, periodo=T_ / 2)
    a.onda('cuerpo', 'r', 2, 1.5, periodo=T_)
    a.onda('cuello', 'r', 0, 3.0, periodo=T_ / 2, base=-12.0)
    a.onda('cabeza', 'r', 0, 2.0, periodo=T_ / 2, fase=0.25, base=4.0)
    a.onda('cola', 'r', 1, 8, periodo=T_, fase=0.5)
    # --- ataque (el mordisco): se encabrita, estira el cuello y levanta el cráneo hasta ponerlo de pie; la mandíbula
    # queda horizontal
    at = m.anim('ataque', 0.5)
    at.rot('cuerpo', [(0, 0, 0, 0), (0.1, -16, 0, 0), (0.28, -16, 0, 0), (0.45, 0, 0, 0)])
    at.rot('cuello', [(0, 0, 0, 0), (0.1, -18, 0, 0), (0.28, -18, 0, 0), (0.45, 0, 0, 0)])
    at.mov('cuello', [(0, 0, 0, 0), (0.1, 0, 0, 1.5), (0.28, 0, 0, 1.5), (0.45, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.1, 34, 0, 0), (0.28, 34, 0, 0), (0.45, 0, 0, 0)])
    at.rot('craneo', [(0, 0, 0, 0), (0.1, -88, 0, 0), (0.24, -88, 0, 0), (0.34, 0, 0, 0)])
    for nombre, lado, fase in PATAS_CHELONIA:
        if '_del_' in nombre:
            at.rot(nombre, [(0, 0, 0, 0), (0.1, 0, 0, -lado * 10), (0.28, 0, 0, -lado * 10), (0.45, 0, 0, 0)])
    # --- especial (lanza un proyectil): echa la cabeza atrás y la estira de golpe con la boca abierta
    es = m.anim('especial', 0.8)
    es.mov('cuello', [(0, 0, 0, 0), (0.3, 0, 0.5, -3.0), (0.42, 0, 0, 2.5), (0.8, 0, 0, 0)])
    es.rot('cuello', [(0, 0, 0, 0), (0.3, -10, 0, 0), (0.42, 4, 0, 0), (0.8, 0, 0, 0)])
    es.rot('craneo', [(0, 0, 0, 0), (0.3, 0, 0, 0), (0.42, -40, 0, 0), (0.6, -40, 0, 0), (0.8, 0, 0, 0)])
    es.rot('cuerpo', [(0, 0, 0, 0), (0.3, -3, 0, 0), (0.42, 2, 0, 0), (0.8, 0, 0, 0)])
    # --- muerte: cae de lado, con las patas flojas
    d = m.anim('muerte', 1.2)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, -6, 0, 0), (1.0, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, 6.0, 0)])
    d.rot('cuello', [(0, 0, 0, 0), (1.0, 20, 0, 0)])
    for nombre, lado, fase in PATAS_CHELONIA:
        d.rot(nombre, [(0, 0, 0, 0), (1.0, 0, 0, lado * 20)])
    # --- estado1: escondida en el caparazón. El cuello se mete recto hacia atrás y la cabeza con él; las patas se
    # pliegan bajo el borde, la cola se recoge y el cuerpo baja hasta apoyar la panza
    e = m.anim('estado1', 1.0, bucle=True)
    escondida_chelonia(e, 0.0, 1.0)
    # --- aparece: sale del caparazón (lo contrario de esconderse)
    ap = m.anim('aparece', 1.2)
    escondida_chelonia(ap, 0.0, 0.0, hasta=1.2)


def escondida_chelonia(a, t0, t1, hasta=None):
    """La postura de escondida, quieta de t0 a t1; con 'hasta', desde ahí vuelve a la de siempre (el 'aparece').
    El cuello se mete recto hacia atrás con la cabeza (todo dentro de la caja de hojas y encogido para que no asome),
    la cola se recoge, el cuerpo baja hasta apoyar la panza y cada pata se pone horizontal, de lado, y se mete bajo la
    bandeja; la aleta se pliega contra el codo (se encoge hacia él: dentro del caparazón no se ve)."""
    poses = {
        ('cuello', 'm'): (0, -1.0, -14.0), ('cabeza', 'm'): (0, 0, -14.0), ('cola', 'm'): (0, 0, 11.0),
        ('cuello', 'e'): (0.02, 0.02, 0.02), ('cabeza', 'e'): (0.02, 0.02, 0.02), ('cola', 'e'): (0.05, 0.05, 0.05),
        ('cuerpo', 'm'): (0, -4.0, 0),
    }
    for nombre, lado, delante, z, abre, baja1, baja2 in geometria_patas_chelonia():
        # primero gira para que apunte de lado (sin ir hacia delante ni hacia atrás), luego sube hasta la horizontal
        poses[(nombre, 'r')] = (0, lado * delante * abre, lado * baja1)
        poses[(nombre, 'm')] = (-lado * 11.0, 1.0, 0)
        poses[('aleta' + nombre[4:], 'e')] = (0.05, 0.05, 0.05)
    for (parte, tipo), v in poses.items():
        normal = (1.0, 1.0, 1.0) if tipo == 'e' else (0, 0, 0)
        ks = [(t0, *v), (t1, *v)] if hasta is None else [(t0, *v), (hasta * 0.35, *v), (hasta, *normal)]
        {'m': a.mov, 'r': a.rot, 'e': a.esc}[tipo](parte, ks)

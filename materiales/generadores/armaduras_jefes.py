"""
Las armaduras de los tres jefes (octubre de 2026), en 3D y con capas. No son
la netherite recoloreada: cada pieza tiene su forma y sus piezas propias por
encima del cuerpo (crestas, venera, cuernos de coral, aletas, capa de algas,
caracola, cristales de jade, hombreras de oro en espiral, alas de polilla,
plumas, antenas, garras...), que se mueven: la capa y las aletas ondean, las
alas aletean, las esquirlas de jade flotan. Se pintan en tres capas:

  base       lo opaco (metal, escamas, nacar, oro, hueso, plumas)
  membrana   lo translucido (las aletas de las Mareas, los cristales de Jade, las
             alas del Vendaval)
  brillo     lo que brilla sin luz (costuras de prismarina, gemas, ojos, vetas
             de jade, rayos), en 8 cuadros que el juego alterna: la luz corre

Las tres:
  mareas    Nerea, agua. Metal abisal con escamas, costuras de prismarina,
            nacar, coral, algas y la venera con su perla.
  jade      Rajang, tierra. Metal verde negro, oro de templo en espiral
            cuadrada, cristales de jade, colmillos y garras de jaguar.
  vendaval  Aeralis, viento. Metal anil, rayos celestes, violeta de tormenta,
            plumas blancas y alas de polilla con su ocelo.

Escribe (todo generado, no se edita a mano):
  textures/entity/armadura/<tema>.png, <tema>_membrana.png, <tema>_brillo_N.png
  textures/entity/equipment/humanoid(_leggings)/<tema>.png   la capa plana (de
                         respaldo, por si algo la pinta sin el modelo 3D)
  textures/particle/<tema>_tajo_N.png                        el tajo de la espada
  src/client/java/com/atalaya/client/ArmaduraJefeMalla.java  las mallas y las
                         animaciones de cada pieza

Los iconos de las piezas y de las espadas los pinta armaduras_iconos.py.

Uso: python armaduras_jefes.py <raiz> [hoja.png]
"""
import json, math, os, random, sys, zlib
from PIL import Image

RAIZ = sys.argv[1]
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
JAVA = os.path.join(RAIZ, 'src/client/java/com/atalaya/client/ArmaduraJefeMalla.java')
CUADROS_BRILLO = 8


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def rampa(*cs):
    return [hexc(c) for c in cs]


def mezclar(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (a[3] if len(a) > 3 else 255,)


# ----------------------------------------------------------------------
#  Las paletas de cada tema
#    metal  7 pasos, de la junta al filo
#    luz    lo que brilla (costuras, gemas, rayos)
#    deco   nacar / oro / violeta
#    extra  coral / jade claro / pluma
#    hueso, alga (mareas), cristal (jade), membrana
# ----------------------------------------------------------------------
TEMAS = {
    'mareas': {
        'metal': rampa('0a141a', '11222b', '1a333d', '254753', '345e6a', '4c7984', '75a3ab'),
        'luz': rampa('0e4e60', '1b8aa6', '3fe0ff', '9ff4ff', 'eaffff'),
        'deco': rampa('5e3e55', '9a6f88', 'cfa2b8', 'efd2e0', 'fff4fa'),
        'extra': rampa('5e1029', '9e1a42', 'd8336a', 'f2618f', 'ffb3c8'),
        'hueso': rampa('5c5545', '8a8068', 'b3a98c', 'd3c9aa', 'ece4c8'),
        'alga': rampa('0c200e', '143214', '1e4a1a', '2a6222', '3a7a2e'),
        'membrana': rampa('0e4e60', '1b8aa6', '3fe0ff', '9ff4ff', 'eaffff'),
    },
    'jade': {
        'metal': rampa('0b130e', '131f17', '1b2c21', '263b2c', '34503b', '4a6a51', '6e8f74'),
        'luz': rampa('0c3a1e', '1d6b3a', '35a85a', '6fe08a', 'd2ffd8'),
        'deco': rampa('4e380c', '8a661c', 'c99c32', 'f2d06e', 'fff2c0'),
        'extra': rampa('1d6b3a', '35a85a', '58c886', '8cff5a', 'e6ffb0'),
        'hueso': rampa('6a5a3c', '9a8a62', 'c8b88c', 'e6dab4', 'fff6dc'),
        'alga': rampa('0c200e', '143214', '1e4a1a', '2a6222', '3a7a2e'),
        'membrana': rampa('0e4a26', '1d7a40', '35b064', '7ee69a', 'd8ffe0'),
    },
    'vendaval': {
        'metal': rampa('0f0f1c', '181a2c', '22243f', '2e3152', '3f4469', '585e88', '838ab0'),
        'luz': rampa('1b3f6e', '2f6fb0', '5fb6ff', 'a8dcff', 'eef8ff'),
        'deco': rampa('34206a', '6040b0', '9078f8', 'c4b0ff', 'f0e8ff'),
        'extra': rampa('868cae', 'b6bbd6', 'd6daee', 'eceff9', 'ffffff'),
        'hueso': rampa('868cae', 'b6bbd6', 'd6daee', 'eceff9', 'ffffff'),
        'alga': rampa('34206a', '6040b0', '9078f8', 'c4b0ff', 'f0e8ff'),
        'membrana': rampa('2a1f5e', '4a3aa0', '7f78e8', 'b8c8ff', 'eef4ff'),
    },
}

# ----------------------------------------------------------------------
#  Los materiales: (capa, color, brillo) de cada pixel de una cara.
#    capa: 'base' (opaco), 'mem' (translucido) o None (no se pinta)
#  i, j: el pixel dentro de la cara; w, h: lo que mide la cara.
# ----------------------------------------------------------------------
def material(letra, T, i, j, w, h, rnd):
    M, L, D, X = T['metal'], T['luz'], T['deco'], T['extra']
    borde = i == 0 or j == 0 or i == w - 1 or j == h - 1
    if letra == '.':
        return None, None, None
    if letra in 'Mm':
        # Placa con bisel: el canto de arriba y la izquierda claros, abajo y a la derecha hondos.
        k = 3 if letra == 'M' else 2
        if j == 0 or i == 0:
            k += 1
        if j == h - 1 or i == w - 1:
            k -= 1
        if rnd.random() < 0.12:
            k += rnd.choice((-1, 1))
        if w >= 4 and h >= 4 and (i, j) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
            k = 5                                   # remaches en las esquinas
        return 'base', M[max(0, min(6, k))], None
    if letra == 'S':
        # Escamas: medias lunas en filas alternas, con su sombra.
        fila = j // 2
        x = (i + (fila % 2) * 2) % 4
        if j % 2 == 0:
            k = 5 if x in (1, 2) else 3
        else:
            k = 2 if x in (0, 3) else 4
        return 'base', M[k], None
    if letra == 'P':
        # Costura que brilla.
        return 'base', L[1], L[3]
    if letra == 'E':
        # Gema: el centro claro.
        return 'base', L[2], L[4]
    if letra == 'e':
        return 'base', L[1], L[2]
    if letra in 'N':
        # Deco: nacar con bandas / oro con su brillo / violeta.
        k = [1, 2, 3, 3, 2][(j + i // 3) % 5]
        if rnd.random() < 0.1:
            k = 4
        return 'base', D[k], None
    if letra == 'n':
        return 'base', D[1], None
    if letra == 'O':
        # Oro con bisel (en las tres sale de la deco).
        k = 3 if (i + j) % 5 else 4
        if j == h - 1:
            k = 1
        return 'base', D[k], None
    if letra == 'R':
        # Coral / jade claro / pluma: moteado.
        k = rnd.choice((1, 2, 2, 3, 3, 4))
        return 'base', X[k], None
    if letra == 'B':
        k = 3 if (i + j) % 4 else 2
        if borde:
            k = 1
        return 'base', T['hueso'][k], None
    if letra == 'T':
        # Colmillo: marfil que se oscurece hacia la punta.
        k = 4 - min(3, j * 4 // max(1, h))
        return 'base', T['hueso'][k], None
    if letra == 'K':
        # Alga: el nervio en el medio y las hojas mas oscuras al canto.
        A = T['alga']
        if i == w // 2:
            k = 4
        elif borde:
            k = 0
        else:
            k = 2 + (j + i) % 2
        return 'base', A[k], None
    if letra == 'W':
        # Pluma: el canon en el medio, las barbas en diagonal, el filo gris.
        P = T['extra']
        if i == w // 2:
            return 'base', P[4], None
        if borde and j > 0:
            return 'base', P[1], None
        k = 3 if (i + j) % 3 else 2
        return 'base', P[k], None
    if letra == 'F':
        # Membrana (aleta): radios que la atraviesan y el filo claro; translucida.
        Mb = T['membrana']
        a = 150
        if borde:
            return 'mem', Mb[4][:3] + (220,), Mb[3]
        if i % 2 == 0:
            return 'mem', Mb[2][:3] + (190,), None
        return 'mem', Mb[1][:3] + (a,), None
    if letra == 'J':
        # Cristal de jade, translucido, con facetas y vetas que brillan.
        C = T['membrana']
        faceta = (i * 2 + j) % 7
        if faceta == 0:
            return 'mem', C[4][:3] + (235,), C[3]
        k = 2 + (faceta % 2)
        if borde:
            k = 1
        return 'mem', C[k][:3] + (215,), (C[3] if (i + j * 3) % 9 == 0 else None)
    if letra == 'A':
        # Ala de polilla: membrana con el ocelo (el ojo) en el centro y el filo de pluma.
        Mb, P = T['membrana'], T['extra']
        u, v = (i + 0.5) / w, (j + 0.5) / h
        d = math.hypot(u - 0.55, (v - 0.42) * h / max(1, w))
        if borde:
            return 'base', P[2 if (i + j) % 2 else 3], None
        if d < 0.1:
            return 'base', T['luz'][4], T['luz'][3]
        if d < 0.17:
            return 'base', T['deco'][1], None
        if d < 0.24:
            return 'mem', T['deco'][3][:3] + (220,), T['deco'][2]
        if (i + j) % 5 == 0:
            return 'mem', Mb[1][:3] + (170,), None
        return 'mem', Mb[2][:3] + (140,), None
    raise ValueError(letra)


# ----------------------------------------------------------------------
#  Las piezas. Una caja: (x, y, z, w, h, d, material o caras, inflado).
#  "caras" es un dict cara -> letra por defecto o lista de filas (calco):
#  up (w x d), down (w x d), north (w x h, delante), south (w x h, detras),
#  west (d x h, lado -X), east (d x h, lado +X).
#  Una parte: (nombre, padre, pivote, giro en grados, cajas, pieza).
# ----------------------------------------------------------------------
PARTES = {t: [] for t in TEMAS}
ANIMS = {t: {} for t in TEMAS}
BASES = ('head', 'body', 'right_arm', 'left_arm', 'right_leg', 'left_leg')
PIVOTE_BASE = {'head': (0, 0, 0), 'body': (0, 0, 0), 'right_arm': (-5, 2, 0), 'left_arm': (5, 2, 0),
               'right_leg': (-1.9, 12, 0), 'left_leg': (1.9, 12, 0)}


def caja(x, y, z, w, h, d, caras, infla=0.0):
    return (x, y, z, w, h, d, caras, infla)


def parte(tema, pieza, nombre, padre, pivote=(0, 0, 0), giro=(0, 0, 0), cajas=()):
    PARTES[tema].append({'nombre': nombre, 'padre': padre, 'pivote': pivote, 'giro': giro,
                         'cajas': list(cajas), 'pieza': pieza})


def anim(tema, pieza, nombre, eje, amplitud, frecuencia, fase=0.0, andar=0.0):
    """eje: 0 xRot, 1 yRot, 2 zRot, 3 y (flota), 4 giro continuo en Y, 5 xRot que sube al andar."""
    ANIMS[tema].setdefault(pieza, []).append((nombre, eje, amplitud, frecuencia, fase, andar))


def lados(caras_lado, abajo='.', arriba=None):
    """Caras de una caja de armadura: los cuatro lados con lo mismo, abajo abierto."""
    c = {'north': caras_lado, 'south': caras_lado, 'west': caras_lado, 'east': caras_lado, 'down': abajo}
    if arriba is not None:
        c['up'] = arriba
    return c


def con_banda(filas_base, alto, ancho, bandas):
    """Un calco de 'ancho x alto' relleno de una letra con filas cambiadas: bandas = {fila: letra}."""
    filas = []
    for j in range(alto):
        filas.append((bandas.get(j, filas_base)) * ancho if len(bandas.get(j, filas_base)) == 1
                     else bandas.get(j, filas_base))
    return filas


# ======================================================================
#  MAREAS: el guardian de los mares
# ======================================================================
T = 'mareas'
parte(T, 'casco', 'casco_mareas', 'head', cajas=[caja(-4, -8, -4, 8, 8, 8, {
    'north': ["SSSPPSSS",
              "SPPEEPPS",
              "M......M",
              "M......M",
              "MM....MM",
              "MP.MM.PM",
              "MP....PM",
              "MMM..MMM"],
    'south': con_banda('S', 8, 8, {1: 'P', 7: 'M'}),
    'west': con_banda('S', 8, 8, {1: 'P', 7: 'M'}),
    'east': con_banda('S', 8, 8, {1: 'P', 7: 'M'}),
    'up': con_banda('S', 8, 8, {3: 'SSSNNSSS', 4: 'SSSNNSSS'}),
    'down': '.'}, 1.0)])
# La venera: un abanico de nacar detras de la cabeza, con la perla en el centro.
parte(T, 'casco', 'venera', 'head', (0, -7, 4.2), (-28, 0, 0), [caja(-1.5, -1.5, -0.5, 3, 3, 1, 'E')])
for k in range(7):
    a = -60 + k * 20
    largo = 8 if k in (0, 6) else 10 if k in (1, 5) else 11
    parte(T, 'casco', f'venera_{k}', 'venera', (0, 0, 0), (0, 0, a), [
        caja(-1, -largo, -0.4, 2, largo, 1, {'north': con_banda('N', largo, 2, {0: 'P'}),
                                             'south': con_banda('N', largo, 2, {0: 'P'}), 'up': 'P'})])
# Cuernos de coral en las sienes, y las branquias que ondean.
for lado, s in (('izq', 1), ('der', -1)):
    parte(T, 'casco', f'coral_{lado}', 'head', (s * 4.5, -6.5, -1), (0, 0, s * 25), [
        caja(-0.5, -4, -0.5, 1, 4, 1, 'R'), caja(-0.5 + s * 1, -6, -0.5, 1, 2, 1, 'R'),
        caja(-0.5 - s * 1, -5, -0.5, 1, 1, 1, 'R')])
    parte(T, 'casco', f'branquia_{lado}', 'head', (s * 5.0, -3.5, 0.5), (0, s * 35, 0), [
        caja(0, -3, -0.5, 0, 6, 5, 'F')])
    anim(T, 'casco', f'branquia_{lado}', 1, s * 0.22, 0.22, 0.0 if s > 0 else 1.6, 0.6)

# La coraza: escamas, la venera chica con la perla, la caracola y el coral en los hombros, la capa de algas.
parte(T, 'pechera', 'pechera_mareas', 'body', cajas=[caja(-4, 0, -2, 8, 12, 4, {
    'north': ["MMNNNNMM",
              "MSNnnNSM",
              "SSNEENSS",
              "SSnNNnSS",
              "SSSnnSSS",
              "PSSSSSSP",
              "SSSSSSSS",
              "SPSSSSPS",
              "SSSSSSSS",
              "MMMPPMMM",
              "MSSSSSSM",
              "MMMMMMMM"],
    'south': ["MMMMMMMM",
              "MSSBBSSM",
              "SSSBBSSS",
              "SSSBBSSS",
              "SSSBBSSS",
              "PSSBBSSP",
              "SSSBBSSS",
              "SSSBBSSS",
              "SSSBBSSS",
              "MMMPPMMM",
              "MSSSSSSM",
              "MMMMMMMM"],
    'west': con_banda('S', 12, 4, {0: 'M', 5: 'P', 9: 'P', 11: 'M'}),
    'east': con_banda('S', 12, 4, {0: 'M', 5: 'P', 9: 'P', 11: 'M'}),
    'up': 'M', 'down': '.'}, 1.0)])
for brazo, x0 in (('right_arm', -3), ('left_arm', -1)):
    parte(T, 'pechera', f'manga_{brazo}', brazo, cajas=[caja(x0, -2, -2, 4, 12, 4,
          lados(con_banda('S', 12, 4, {0: 'M', 8: 'P', 9: 'M', 11: 'M'}), arriba='M'), 1.0)])
# La caracola del hombro izquierdo: una espiral de nacar que se estrecha.
parte(T, 'pechera', 'caracola', 'left_arm', (1.5, -3.2, 0), (0, 0, -18), [
    caja(-3, -2, -3, 6, 2, 6, {'up': 'N', 'north': con_banda('N', 2, 6, {1: 'R'}), 'south': 'N',
                               'west': 'N', 'east': con_banda('N', 2, 6, {1: 'R'}), 'down': 'n'}),
    caja(-2, -4, -2, 4, 2, 4, 'N'), caja(-1.5, -6, -1.5, 3, 2, 3, {'up': 'N', 'north': con_banda('N', 2, 3, {0: 'R'}),
                                                                   'south': 'N', 'west': 'N', 'east': 'N', 'down': 'n'}),
    caja(-1, -8, -1, 2, 2, 2, 'N'), caja(-0.5, -9, -0.5, 1, 1, 1, 'E'),
    caja(2.5, -1.5, -1, 2, 1, 2, 'N'), caja(-1, -1.5, 2.5, 2, 1, 2, 'N')])
# El coral del hombro derecho.
parte(T, 'pechera', 'coral_hombro', 'right_arm', (-1.5, -3.0, 0), (0, 0, 15), [
    caja(-3, -1, -3, 6, 1, 6, 'M'),
    caja(-2, -5, -1, 1, 4, 1, 'R'), caja(-3, -6, -1, 1, 2, 1, 'R'),
    caja(0, -4, 1, 1, 3, 1, 'R'), caja(1, -5, 1, 1, 1, 1, 'R'),
    caja(1, -3, -2, 1, 2, 1, 'R'), caja(-1, -7, -1, 1, 2, 1, 'R')])
# La capa de algas: tres tiras desde los hombros, que ondean y se levantan al correr.
for k, x in enumerate((-3, 0, 3)):
    largo = (15, 17, 15)[k]
    parte(T, 'pechera', f'capa_{k}', 'body', (x, 0.5, 2.9), (8, 0, (k - 1) * -4), [
        caja(-1.5, 0, 0, 3, largo, 0, 'K')])
    anim(T, 'pechera', f'capa_{k}', 0, 0.07, 0.11, k * 0.9, 1.0)
    anim(T, 'pechera', f'capa_{k}', 5, 0.9, 0.0, 0.0, 1.0)
# Espinas de hueso por el lomo.
for k, y in enumerate((2, 5, 8)):
    parte(T, 'pechera', f'espina_{k}', 'body', (0, y, 3.0), (-50, 0, 0), [caja(-0.5, -3 + k * 0.5, -0.5, 1, 3, 1, 'B')])

# Las grebas: el cinturon con su hebilla de nacar y las conchas que cuelgan; aletas en las rodillas.
parte(T, 'grebas', 'cintura_mareas', 'body', cajas=[caja(-4, 7, -2, 8, 5, 4, {
    'north': ["nNNNNNNn", "NNNEENNN", "SSSSSSSS", "SSSSSSSS", "SPSSSSPS"],
    'south': ["nNNNNNNn", "NNNNNNNN", "SSSSSSSS", "SSSSSSSS", "SPSSSSPS"],
    'west': con_banda('S', 5, 4, {0: 'n', 1: 'N'}), 'east': con_banda('S', 5, 4, {0: 'n', 1: 'N'}),
    'up': '.', 'down': '.'}, 0.55)])
for pierna in ('right_leg', 'left_leg'):
    parte(T, 'grebas', f'pernera_{pierna}', pierna, cajas=[caja(-2, 0, -2, 4, 9, 4,
          lados(con_banda('S', 9, 4, {5: 'P', 6: 'M'}), arriba='.'), 0.5)])
parte(T, 'grebas', 'conchas_delante', 'body', (0, 11.5, -2.7), (8, 0, 0), [
    caja(-3.5, 0, -0.5, 3, 3, 1, {'north': ["NNN", "NnN", ".N."], 'south': 'n', 'up': 'N', 'down': 'n',
                                  'west': 'N', 'east': 'N'}),
    caja(0.5, 0, -0.5, 3, 3, 1, {'north': ["NNN", "NnN", ".N."], 'south': 'n', 'up': 'N', 'down': 'n',
                                 'west': 'N', 'east': 'N'})])
for lado, pierna, s in (('izq', 'left_leg', 1), ('der', 'right_leg', -1)):
    parte(T, 'grebas', f'aleta_rodilla_{lado}', pierna, (s * 2.6, 5, -1), (0, s * 25, 0), [
        caja(0, -3, -0.5, 0, 4, 4, 'F')])
    anim(T, 'grebas', f'aleta_rodilla_{lado}', 1, s * 0.12, 0.25, 0.7 * s, 0.8)

# Las botas: puntera de concha y aletas en los tobillos.
for lado, pierna, s in (('izq', 'left_leg', 1), ('der', 'right_leg', -1)):
    parte(T, 'botas', f'bota_{pierna}', pierna, cajas=[caja(-2, 6, -2, 4, 6, 4, {
        'north': ["NNNN", "SSSS", "SPPS", "NNNN", "NnnN", "mmmm"],
        'south': con_banda('S', 6, 4, {0: 'N', 5: 'm'}), 'west': con_banda('S', 6, 4, {0: 'N', 5: 'm'}),
        'east': con_banda('S', 6, 4, {0: 'N', 5: 'm'}), 'up': '.', 'down': 'm'}, 1.0)])
    parte(T, 'botas', f'aleta_tobillo_{lado}', pierna, (s * 3.1, 8.5, 1.2), (0, s * 30, 0), [
        caja(0, -3, 0, 0, 4, 4, 'F')])
    anim(T, 'botas', f'aleta_tobillo_{lado}', 1, s * 0.18, 0.3, 0.4 * s, 1.2)

# ======================================================================
#  JADE: el jaguar de jade
# ======================================================================
T = 'jade'
parte(T, 'casco', 'casco_jade', 'head', cajas=[caja(-4, -8, -4, 8, 8, 8, {
    'north': ["MOOOOOOM",
              "MEMOOMEM",
              "MMMOOMMM",
              "M......M",
              "M......M",
              "MT....TM",
              "M.T..T.M",
              "MM....MM"],
    'south': con_banda('M', 8, 8, {1: 'O', 5: 'e', 7: 'O'}),
    'west': con_banda('M', 8, 8, {1: 'O', 7: 'O'}),
    'east': con_banda('M', 8, 8, {1: 'O', 7: 'O'}),
    'up': ["OOOOOOOM",
           "MMMMMMOM",
           "MOOOOMOM",
           "MOMMOMOM",
           "MOMEEMOM",
           "MOMMMMOM",
           "MOOOOOOM",
           "MMMMMMMM"],
    'down': '.'}, 1.0)])
# El hocico del jaguar sobre la frente, con los colmillos de arriba.
parte(T, 'casco', 'hocico', 'head', (0, -6.5, -5.3), (12, 0, 0), [
    caja(-3, -1, -1.5, 6, 2, 2, {'north': ["MOOOOM", "MMeeMM"], 'up': 'M', 'down': 'm', 'south': 'M',
                                 'west': 'M', 'east': 'M'}),
    caja(-1, -0.5, -2.5, 2, 1, 1, 'm'),
    caja(-2.8, 1, -1.2, 1, 2, 1, 'T'), caja(1.8, 1, -1.2, 1, 2, 1, 'T')])
for lado, s in (('izq', 1), ('der', -1)):
    parte(T, 'casco', f'oreja_{lado}', 'head', (s * 3.2, -8.6, 0.5), (0, 0, s * 18), [
        caja(-1, -2, -1, 2, 2, 1, {'north': ["OO", "MM"], 'south': 'M', 'up': 'O', 'down': 'M', 'west': 'M', 'east': 'M'})])
# La cresta de cristales de jade.
for k, (x, z, gx, gz, alto) in enumerate(((0, 0.5, -10, 0, 6), (-2.2, 1.6, -18, 18, 4), (2.2, 1.6, -18, -18, 4))):
    parte(T, 'casco', f'cristal_casco_{k}', 'head', (x, -8.6, z), (gx, 0, gz), [
        caja(-1, -alto, -1, 2, alto, 2, 'J'), caja(-0.5, -alto - 1, -0.5, 1, 1, 1, 'J')])

parte(T, 'pechera', 'pechera_jade', 'body', cajas=[caja(-4, 0, -2, 8, 12, 4, {
    'north': ["OOOOOOOO",
              "MOMMMMOM",
              "MMOOOOMM",
              "MOOJJOOM",
              "MOJEEJOM",
              "MOOJJOOM",
              "MMOOOOMM",
              "MMMOOMMM",
              "MMMMMMMM",
              "OOOOOOOO",
              "MOMOMOMO",
              "MMMMMMMM"],
    'south': ["OOOOOOOO",
              "MMMMMMMM",
              "MMMeeMMM",
              "MMMMMMMM",
              "MMMeeMMM",
              "MMMMMMMM",
              "MMMeeMMM",
              "MMMMMMMM",
              "MMMMMMMM",
              "OOOOOOOO",
              "MOMOMOMO",
              "MMMMMMMM"],
    'west': con_banda('M', 12, 4, {0: 'O', 9: 'O'}), 'east': con_banda('M', 12, 4, {0: 'O', 9: 'O'}),
    'up': 'O', 'down': '.'}, 1.0)])
for brazo, x0 in (('right_arm', -3), ('left_arm', -1)):
    parte(T, 'pechera', f'manga_{brazo}', brazo, cajas=[caja(x0, -2, -2, 4, 12, 4,
          lados(con_banda('M', 12, 4, {0: 'O', 7: 'O', 8: 'e', 9: 'O'}), arriba='O'), 1.0)])
ESPIRAL7 = ["OOOOOOO", "MMMMMMO", "MOOOOMO", "MOMEMMO", "MOMOOOO", "MOMMMMM", "MOOOOOO"]
for lado, brazo, s in (('izq', 'left_arm', 1), ('der', 'right_arm', -1)):
    parte(T, 'pechera', f'hombrera_{lado}', brazo, (s * 1.2, -2.9, 0), (0, 0, s * -12), [
        caja(-3.5, -1, -3.5, 7, 2, 7, {'up': ESPIRAL7 if s > 0 else [f[::-1] for f in ESPIRAL7],
                                      'north': ["OOOOOOO", "MeMMMeM"], 'south': ["OOOOOOO", "MeMMMeM"],
                                      'west': ["OOOOOOO", "MMeMeMM"], 'east': ["OOOOOOO", "MMeMeMM"], 'down': 'm'}),
        caja(-3, 1, -3, 6, 1, 6, 'O'),
        caja(s * 2.2 - 1, -2.5, -1, 2, 2, 2, 'J')])
    # Una esquirla de jade que flota sobre el hombro y gira.
    parte(T, 'pechera', f'esquirla_{lado}', brazo, (s * 3.5, -7.5, 0), (0, 0, 0), [
        caja(-0.5, -1.5, -0.5, 1, 3, 1, 'J'), caja(-1, -0.5, -0.5, 2, 1, 1, 'J')])
    anim(T, 'pechera', f'esquirla_{lado}', 3, 0.8, 0.12, 0.0 if s > 0 else 2.0, 0.0)
    anim(T, 'pechera', f'esquirla_{lado}', 4, 0.06, 0.0, 0.0, 0.0)
# Cristales de jade por la espalda.
for k, (x, y, gz, alto) in enumerate(((0, 2.5, 0, 6), (-2.5, 4.5, 22, 5), (2.5, 4.5, -22, 5), (0, 7.5, 0, 4))):
    parte(T, 'pechera', f'cristal_espalda_{k}', 'body', (x, y, 2.8), (-38, 0, gz), [
        caja(-1, -alto, -1, 2, alto, 2, 'J'), caja(-0.5, -alto - 1, -0.5, 1, 1, 1, 'J')])

parte(T, 'grebas', 'cintura_jade', 'body', cajas=[caja(-4, 7, -2, 8, 5, 4, {
    'north': ["OOOOOOOO", "OOOEEOOO", "MMMMMMMM", "MOMMMMOM", "MMMMMMMM"],
    'south': ["OOOOOOOO", "OOOOOOOO", "MMMMMMMM", "MOMMMMOM", "MMMMMMMM"],
    'west': con_banda('M', 5, 4, {0: 'O', 1: 'O'}), 'east': con_banda('M', 5, 4, {0: 'O', 1: 'O'}),
    'up': '.', 'down': '.'}, 0.55)])
for pierna in ('right_leg', 'left_leg'):
    parte(T, 'grebas', f'pernera_{pierna}', pierna, cajas=[caja(-2, 0, -2, 4, 9, 4, {
        'north': ["MMMM", "OOOO", "OMMO", "OMeO", "OOOO", "MJJM", "MMMM", "MOOM", "MMMM"],
        'south': con_banda('M', 9, 4, {1: 'O', 7: 'O'}), 'west': con_banda('M', 9, 4, {1: 'O', 7: 'O'}),
        'east': con_banda('M', 9, 4, {1: 'O', 7: 'O'}), 'up': '.', 'down': '.'}, 0.5)])
parte(T, 'grebas', 'faldon_delante', 'body', (0, 11.6, -2.7), (6, 0, 0), [
    caja(-3, 0, -0.5, 6, 4, 1, {'north': ["OOOOOO", "OMMMMO", "OMeeMO", "OOOOOO"], 'south': 'M', 'up': 'O',
                                'down': 'O', 'west': 'O', 'east': 'O'})])
parte(T, 'grebas', 'faldon_detras', 'body', (0, 11.6, 2.7), (-6, 0, 0), [
    caja(-3, 0, -0.5, 6, 4, 1, {'south': ["OOOOOO", "OMMMMO", "OMMMMO", "OOOOOO"], 'north': 'M', 'up': 'O',
                                'down': 'O', 'west': 'O', 'east': 'O'})])

for lado, pierna, s in (('izq', 'left_leg', 1), ('der', 'right_leg', -1)):
    parte(T, 'botas', f'bota_{pierna}', pierna, cajas=[caja(-2, 6, -2, 4, 6, 4, {
        'north': ["OOOO", "MeeM", "MMMM", "MMMM", "OOOO", "mmmm"],
        'south': con_banda('M', 6, 4, {0: 'O', 4: 'O', 5: 'm'}), 'west': con_banda('M', 6, 4, {0: 'O', 4: 'O', 5: 'm'}),
        'east': con_banda('M', 6, 4, {0: 'O', 4: 'O', 5: 'm'}), 'up': '.', 'down': 'm'}, 1.0)])
    # Tres garras de jaguar en la puntera.
    for k, x in enumerate((-1.6, 0, 1.6)):
        parte(T, 'botas', f'garra_{lado}_{k}', pierna, (x, 11.6, -3.0), (-25, 0, 0), [
            caja(-0.5, -0.5, -2, 1, 1, 2, 'T')])

# ======================================================================
#  VENDAVAL: la reina polilla de la tormenta
# ======================================================================
T = 'vendaval'
parte(T, 'casco', 'casco_vendaval', 'head', cajas=[caja(-4, -8, -4, 8, 8, 8, {
    'north': ["MMNNNNMM",
              "MNNEENNM",
              "M......M",
              "MP....PM",
              "M......M",
              "MPM..MPM",
              "M.M..M.M",
              "MM....MM"],
    'south': ["MMMMMMMM", "MPMMMMPM", "MMPMMPMM", "MMMPPMMM", "MMMMMMMM", "MNNNNNNM", "MMMMMMMM", "MMMMMMMM"],
    'west': con_banda('M', 8, 8, {1: 'N', 4: 'MPMMPMMP'}), 'east': con_banda('M', 8, 8, {1: 'N', 4: 'PMMPMMPM'}),
    'up': con_banda('M', 8, 8, {3: 'MMMNNMMM', 4: 'MMMNNMMM'}), 'down': '.'}, 1.0)])
# Alas de pluma a los lados, que aletean.
for lado, s in (('izq', 1), ('der', -1)):
    parte(T, 'casco', f'ala_casco_{lado}', 'head', (s * 4.6, -5.5, 1.5), (0, s * -20, 0), [])
    for k, g in enumerate((-10, -32, -54)):
        largo = (8, 7, 5)[k]
        parte(T, 'casco', f'pluma_casco_{lado}_{k}', f'ala_casco_{lado}', (0, 0, 0), (g, 0, 0), [
            caja(0, -largo, 0, 0, largo, 3, 'W')])
    anim(T, 'casco', f'ala_casco_{lado}', 1, s * 0.25, 0.32, 0.0, 0.8)
    # Antenas de polilla.
    parte(T, 'casco', f'antena_{lado}', 'head', (s * 1.6, -8.6, -2.0), (-22, 0, s * 16), [
        caja(-0.5, -6, -0.5, 1, 6, 1, 'N'), caja(-0.5, -7, -0.5, 1, 1, 1, 'E'),
        caja(0, -6, -2, 0, 4, 2, 'W')])
    anim(T, 'casco', f'antena_{lado}', 2, s * 0.08, 0.17, 0.0 if s > 0 else 1.0, 0.5)

parte(T, 'pechera', 'pechera_vendaval', 'body', cajas=[caja(-4, 0, -2, 8, 12, 4, {
    'north': ["MMNNNNMM",
              "MNPPPPNM",
              "MPNNNNPM",
              "MPNEENPM",
              "MPNEPNPM",
              "MPPNNPPM",
              "MMNPPNMM",
              "MMMNNMMM",
              "MPMMMMPM",
              "MMPMMPMM",
              "MMMPPMMM",
              "MMMMMMMM"],
    'south': ["MMMMMMMM", "MNMMMMNM", "MMNMMNMM", "MMMNNMMM", "MMMMMMMM", "MMMMMMMM",
              "MMMMMMMM", "MMMMMMMM", "MPMMMMPM", "MMPMMPMM", "MMMPPMMM", "MMMMMMMM"],
    'west': con_banda('M', 12, 4, {0: 'N', 5: 'PMMP', 9: 'N'}), 'east': con_banda('M', 12, 4, {0: 'N', 5: 'PMMP', 9: 'N'}),
    'up': 'N', 'down': '.'}, 1.0)])
for brazo, x0 in (('right_arm', -3), ('left_arm', -1)):
    parte(T, 'pechera', f'manga_{brazo}', brazo, cajas=[caja(x0, -2, -2, 4, 12, 4,
          lados(con_banda('M', 12, 4, {0: 'N', 4: 'PMMP', 5: 'MPPM', 9: 'N'}), arriba='N'), 1.0)])
# Hombreras de pluma.
for lado, brazo, s in (('izq', 'left_arm', 1), ('der', 'right_arm', -1)):
    parte(T, 'pechera', f'hombrera_{lado}', brazo, (s * 1.2, -2.9, 0), (0, 0, s * -10), [
        caja(-3, -1, -3, 6, 2, 6, {'up': 'N', 'north': ["NNNNNN", "MPMMPM"], 'south': ["NNNNNN", "MPMMPM"],
                                  'west': ["NNNNNN", "MMPPMM"], 'east': ["NNNNNN", "MMPPMM"], 'down': 'm'})])
    for k, g in enumerate((25, 50, 75)):
        parte(T, 'pechera', f'pluma_hombro_{lado}_{k}', f'hombrera_{lado}', (s * 2.8, -0.5, 0), (0, 0, s * -g), [
            caja(0, -6 + k, -1.5, 0, 6 - k, 3, 'W')])
    anim(T, 'pechera', f'hombrera_{lado}', 2, s * 0.03, 0.4, 0.0, 0.5)
# Alas de polilla en la espalda: la de arriba y la de abajo de cada lado, que aletean.
for lado, s in (('izq', 1), ('der', -1)):
    parte(T, 'pechera', f'ala_{lado}', 'body', (s * 1.0, 3.0, 2.9), (0, s * -38, s * -6), [])
    parte(T, 'pechera', f'ala_alta_{lado}', f'ala_{lado}', (0, 0, 0), (0, 0, s * -14), [
        caja(0 if s > 0 else -15, -12, 0, 15, 13, 0, 'A')])
    parte(T, 'pechera', f'ala_baja_{lado}', f'ala_{lado}', (0, 1.5, 0), (0, 0, s * 24), [
        caja(0 if s > 0 else -11, 0, 0, 11, 10, 0, 'A')])
    anim(T, 'pechera', f'ala_{lado}', 1, s * 0.32, 0.22, 0.0, 1.5)

parte(T, 'grebas', 'cintura_vendaval', 'body', cajas=[caja(-4, 7, -2, 8, 5, 4, {
    'north': ["NNNNNNNN", "NNNEENNN", "MMPMMPMM", "MMMPPMMM", "MMMMMMMM"],
    'south': ["NNNNNNNN", "NNNNNNNN", "MMMMMMMM", "MPMMMMPM", "MMMMMMMM"],
    'west': con_banda('M', 5, 4, {0: 'N', 1: 'N'}), 'east': con_banda('M', 5, 4, {0: 'N', 1: 'N'}),
    'up': '.', 'down': '.'}, 0.55)])
for pierna in ('right_leg', 'left_leg'):
    parte(T, 'grebas', f'pernera_{pierna}', pierna, cajas=[caja(-2, 0, -2, 4, 9, 4, {
        'north': ["MMMM", "MPMM", "MMPM", "MMMP", "MMPM", "MPMM", "NNNN", "MMMM", "MMMM"],
        'south': con_banda('M', 9, 4, {6: 'N'}), 'west': con_banda('M', 9, 4, {2: 'P', 6: 'N'}),
        'east': con_banda('M', 9, 4, {2: 'P', 6: 'N'}), 'up': '.', 'down': '.'}, 0.5)])
for lado, x, g in (('izq', 2.4, -12), ('der', -2.4, 12)):
    parte(T, 'grebas', f'pluma_cadera_{lado}', 'body', (x, 11.0, -2.6), (8, 0, g), [
        caja(-1.5, 0, 0, 3, 5, 0, 'W')])

for lado, pierna, s in (('izq', 'left_leg', 1), ('der', 'right_leg', -1)):
    parte(T, 'botas', f'bota_{pierna}', pierna, cajas=[caja(-2, 6, -2, 4, 6, 4, {
        'north': ["NNNN", "MPPM", "MMMM", "MMMM", "NNNN", "mmmm"],
        'south': con_banda('M', 6, 4, {0: 'N', 4: 'N', 5: 'm'}), 'west': con_banda('M', 6, 4, {0: 'N', 4: 'N', 5: 'm'}),
        'east': con_banda('M', 6, 4, {0: 'N', 4: 'N', 5: 'm'}), 'up': '.', 'down': 'm'}, 1.0)])
    # Alas en los talones.
    parte(T, 'botas', f'ala_talon_{lado}', pierna, (s * 3.2, 8.5, 1.0), (0, s * -30, 0), [])
    for k, g in enumerate((-15, -45)):
        parte(T, 'botas', f'pluma_talon_{lado}_{k}', f'ala_talon_{lado}', (0, 0, 0), (g, 0, 0), [
            caja(0, -4 + k, 0, 0, 4 - k, 3, 'W')])
    anim(T, 'botas', f'ala_talon_{lado}', 1, s * 0.3, 0.4, 0.0, 1.2)
    parte(T, 'botas', f'puntera_{lado}', pierna, (0, 11.5, -3.0), (0, 0, 0), [caja(-1, -0.5, -1.5, 2, 1, 2, 'N')])


# ----------------------------------------------------------------------
#  Las caras de una caja y donde caen en el atlas (el UV de caja de vanilla)
# ----------------------------------------------------------------------
def regiones(u, v, w, h, d):
    """cara -> (u0, v0, ancho, alto) en la textura, como ModelPart.Cube."""
    return {
        'up': (u + d, v, w, d),
        'down': (u + d + w, v, w, d),
        'west': (u, v + d, d, h),
        'north': (u + d, v + d, w, h),
        'east': (u + d + w, v + d, d, h),
        'south': (u + d + w + d, v + d, w, h),
    }


def calco_cara(caras, cara, w, h):
    """Las filas de letras de una cara (el calco o la letra por defecto, repetida)."""
    if isinstance(caras, str):
        c = caras
    elif cara in caras:
        c = caras[cara]
    else:
        # Sin calco para esa cara: la letra que mas sale en la de delante.
        frente = caras.get('north', 'M')
        if isinstance(frente, str):
            c = frente
        else:
            letras = ''.join(frente).replace('.', '') or 'M'
            c = max(set(letras), key=letras.count)
    if isinstance(c, str):
        return [c * w for _ in range(h)]
    filas = list(c)
    if len(filas) != h or any(len(f) != w for f in filas):
        raise ValueError(f'calco de {cara}: {len(filas)}x{len(filas[0]) if filas else 0}, se esperaba {h}x{w}')
    return filas


def pintar_caja(capas, tema, u, v, x, y, z, w, h, d, caras, semilla):
    """Pinta las seis caras de una caja en las capas (base, mem, brillo)."""
    T = TEMAS[tema]
    rnd = random.Random(semilla)
    base, mem, brillo = capas
    for cara, (u0, v0, cw, ch) in regiones(u, v, int(w), int(h), int(d)).items():
        if cw == 0 or ch == 0:
            continue
        filas = calco_cara(caras, cara, cw, ch)
        for j in range(ch):
            for i in range(cw):
                capa, color, luz = material(filas[j][i], T, i, j, cw, ch, rnd)
                if capa is None:
                    continue
                destino = base if capa == 'base' else mem
                destino.putpixel((u0 + i, v0 + j), color[:3] + (color[3] if len(color) > 3 else 255,))
                if luz is not None:
                    brillo.putpixel((u0 + i, v0 + j), luz[:3] + (255,))


# ----------------------------------------------------------------------
#  El empaquetado del atlas de cada tema: estantes de 128 de ancho
# ----------------------------------------------------------------------
ANCHO = 128


def empaquetar(tema):
    cajas = []
    for p in PARTES[tema]:
        for k, c in enumerate(p['cajas']):
            x, y, z, w, h, d = c[:6]
            cajas.append(((p['nombre'], k), int(2 * (d + w)), int(d + h)))
    cajas.sort(key=lambda c: (-c[2], -c[1]))
    uv = {}
    x = y = alto_fila = 0
    for clave, cw, ch in cajas:
        if x + cw > ANCHO:
            x = 0
            y += alto_fila
            alto_fila = 0
        uv[clave] = (x, y)
        x += cw
        alto_fila = max(alto_fila, ch)
    alto = y + alto_fila
    alto = 64 if alto <= 64 else 128 if alto <= 128 else 256
    return uv, alto


def generar(tema):
    uv, alto = empaquetar(tema)
    base = Image.new('RGBA', (ANCHO, alto), (0, 0, 0, 0))
    mem = Image.new('RGBA', (ANCHO, alto), (0, 0, 0, 0))
    luz = Image.new('RGBA', (ANCHO, alto), (0, 0, 0, 0))
    for p in PARTES[tema]:
        for k, c in enumerate(p['cajas']):
            x, y, z, w, h, d, caras, infla = c
            u, v = uv[(p['nombre'], k)]
            pintar_caja((base, mem, luz), tema, u, v, x, y, z, w, h, d, caras, zlib.crc32(f"{tema}/{p['nombre']}/{k}".encode()))
    return uv, alto, base, mem, luz


def cuadros_brillo(luz):
    """Los 8 cuadros del brillo: una onda de luz que corre en diagonal por el atlas."""
    out = []
    px = luz.load()
    for k in range(CUADROS_BRILLO):
        im = Image.new('RGBA', luz.size, (0, 0, 0, 0))
        q = im.load()
        for y in range(luz.height):
            for x in range(luz.width):
                c = px[x, y]
                if c[3] == 0:
                    continue
                fase = (x + y * 0.6) / 9.0
                k_luz = 0.5 + 0.5 * math.sin(2 * math.pi * k / CUADROS_BRILLO - fase)
                f = 0.45 + 0.55 * k_luz
                q[x, y] = (int(c[0] * f), int(c[1] * f), int(c[2] * f), 255)
        out.append(im)
    return out


# ----------------------------------------------------------------------
#  La capa plana de respaldo (el UV de la armadura de vanilla, 64x32): las
#  mismas cajas de base con sus calcos, por si algo la pinta sin el modelo
# ----------------------------------------------------------------------
def capa_plana(tema, piernas):
    im = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
    mem = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
    luz = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
    sitio = {'head': (0, 0, 8, 8, 8), 'body': (16, 16, 8, 12, 4), 'right_arm': (40, 16, 4, 12, 4),
             'right_leg': (0, 16, 4, 12, 4)}
    for p in PARTES[tema]:
        if p['padre'] not in BASES or (p['pieza'] == 'grebas') != piernas or not p['cajas']:
            continue
        x, y, z, w, h, d, caras, infla = p['cajas'][0]
        if p['padre'] not in sitio or (w, h, d) not in ((8, 8, 8), (8, 12, 4), (4, 12, 4), (4, 6, 4), (8, 5, 4), (4, 9, 4)):
            continue
        u, v, sw, sh, sd = sitio[p['padre']]
        if (w, h, d) == (sw, sh, sd):
            pintar_caja((im, mem, luz), tema, u, v, x, y, z, w, h, d, caras, 7)
    im.alpha_composite(luz)
    return im


# ----------------------------------------------------------------------
#  El tajo de la espada al golpear: una media luna que se abre (4 cuadros)
# ----------------------------------------------------------------------
def tajo(tema, k):
    T = TEMAS[tema]
    R = T['luz'] if tema != 'vendaval' else T['extra']
    acento = T['deco']
    s = 32
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    px = im.load()
    abre = 0.35 + 0.25 * k
    grosor = 3.4 - 0.6 * k
    alfa = [255, 235, 190, 120][k]
    c0 = (s / 2, s / 2 + 4)
    radio = 11.5
    for y in range(s):
        for x in range(s):
            dx, dy = x + 0.5 - c0[0], y + 0.5 - c0[1]
            r = math.hypot(dx, dy)
            u = (math.atan2(dy, dx) + math.pi) / math.pi
            if dy > 0.5 or u < 0.5 - abre or u > 0.5 + abre:
                continue
            g = grosor * min(1.0, min(u - (0.5 - abre), (0.5 + abre) - u) / max(0.01, abre) * 3.0)
            dd = r - radio
            if abs(dd) > g:
                continue
            t = 1.0 - abs(dd) / max(0.01, g)
            c = R[4] if t > 0.75 else R[3] if t > 0.45 else R[2] if t > 0.2 else acento[2]
            px[x, y] = c[:3] + (int(alfa * min(1.0, 0.4 + t)),)
    rnd = random.Random(tema + str(k))
    for _ in range(3 + k * 2):
        a = -math.pi * rnd.random()
        r = radio + 3 + rnd.random() * 4 + k
        x, y = int(c0[0] + math.cos(a) * r), int(c0[1] + math.sin(a) * r)
        if 0 <= x < s and 0 <= y < s:
            px[x, y] = acento[3][:3] + (alfa,)
    return im


# ----------------------------------------------------------------------
#  El Java: una malla por tema y pieza, y sus animaciones
# ----------------------------------------------------------------------
def f(v):
    s = f'{float(v):.4f}'.rstrip('0').rstrip('.')
    return (s if s not in ('-0', '') else '0') + 'F'


def java(datos):
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.model.geom.PartPose;',
         'import net.minecraft.client.model.geom.builders.CubeDeformation;',
         'import net.minecraft.client.model.geom.builders.CubeListBuilder;',
         'import net.minecraft.client.model.geom.builders.LayerDefinition;',
         'import net.minecraft.client.model.geom.builders.MeshDefinition;',
         'import net.minecraft.client.model.geom.builders.PartDefinition;', '',
         '/**',
         ' * Las mallas 3D de las armaduras de los jefes. GENERADO por',
         ' * materiales/generadores/armaduras_jefes.py: no se edita a mano (las cajas',
         ' * van con la textura, que se pinta con el mismo empaquetado).',
         ' */',
         'public final class ArmaduraJefeMalla {', '',
         '    /** Lo que se mueve de cada pieza: parte, eje (0 x, 1 y, 2 z, 3 flota, 4 gira, 5 sube al andar),',
         '     *  amplitud, frecuencia, fase y cuanto crece al andar. */',
         '    public record Anim(String parte, int eje, float amplitud, float frecuencia, float fase, float andar) {',
         '    }', '',
         '    private ArmaduraJefeMalla() {', '    }', '',
         '    private static PartDefinition bases(PartDefinition raiz) {',
         '        return raiz;', '    }', '']
    piezas = ('casco', 'pechera', 'grebas', 'botas')
    # crear(tema, pieza)
    L.append('    public static LayerDefinition crear(String tema, String pieza) {')
    L.append('        return switch (tema + "/" + pieza) {')
    for tema in TEMAS:
        for pieza in piezas:
            L.append(f'            case "{tema}/{pieza}" -> {tema}_{pieza}();')
    L.append('            default -> throw new IllegalArgumentException(tema + "/" + pieza);')
    L.append('        };')
    L.append('    }')
    L.append('')
    L.append('    public static Anim[] anims(String tema, String pieza) {')
    L.append('        return switch (tema + "/" + pieza) {')
    for tema in TEMAS:
        for pieza in piezas:
            lista = ANIMS[tema].get(pieza, [])
            if not lista:
                continue
            items = ', '.join(f'new Anim("{n}", {e}, {f(a)}, {f(fr)}, {f(fa)}, {f(an)})' for n, e, a, fr, fa, an in lista)
            L.append(f'            case "{tema}/{pieza}" -> new Anim[]{{{items}}};')
    L.append('            default -> new Anim[0];')
    L.append('        };')
    L.append('    }')
    L.append('')
    L.append('    /** Si la pieza lleva algo translucido (la capa de membrana). */')
    L.append('    public static boolean conMembrana(String tema, String pieza) {')
    L.append('        return switch (tema + "/" + pieza) {')
    con = []
    for tema in TEMAS:
        for pieza in piezas:
            for p in PARTES[tema]:
                if p['pieza'] != pieza:
                    continue
                letras = ''.join(str(c[6]) for c in p['cajas'])
                if any(ch in letras for ch in 'FJA'):
                    con.append(f'"{tema}/{pieza}"')
                    break
    if con:
        L.append(f'            case {", ".join(con)} -> true;')
    L.append('            default -> false;')
    L.append('        };')
    L.append('    }')
    for tema in TEMAS:
        uv, alto = datos[tema]
        for pieza in piezas:
            L.append('')
            L.append(f'    private static LayerDefinition {tema}_{pieza}() {{')
            L.append('        MeshDefinition malla = new MeshDefinition();')
            L.append('        PartDefinition raiz = malla.getRoot();')
            for b in BASES:
                px, py, pz = PIVOTE_BASE[b]
                L.append(f'        PartDefinition p_{b} = raiz.addOrReplaceChild("{b}", CubeListBuilder.create(), '
                         f'PartPose.offset({f(px)}, {f(py)}, {f(pz)}));')
            for p in PARTES[tema]:
                if p['pieza'] != pieza:
                    continue
                cub = 'CubeListBuilder.create()'
                for k, c in enumerate(p['cajas']):
                    x, y, z, w, h, d, caras, infla = c
                    u, v = uv[(p['nombre'], k)]
                    defo = 'CubeDeformation.NONE' if infla == 0 else f'new CubeDeformation({f(infla)})'
                    cub += (f'\n                .texOffs({u}, {v}).addBox({f(x)}, {f(y)}, {f(z)}, {f(w)}, {f(h)}, {f(d)}, '
                            f'{defo})')
                rx, ry, rz = [math.radians(g) for g in p['giro']]
                px, py, pz = p['pivote']
                padre = f'p_{p["padre"]}'
                L.append(f'        PartDefinition p_{p["nombre"]} = {padre}.addOrReplaceChild("{p["nombre"]}", {cub},')
                L.append(f'                PartPose.offsetAndRotation({f(px)}, {f(py)}, {f(pz)}, {f(rx)}, {f(ry)}, {f(rz)}));')
            L.append(f'        return LayerDefinition.create(malla, {ANCHO}, {alto});')
            L.append('    }')
    L.append('}')
    return '\n'.join(L) + '\n'


# ----------------------------------------------------------------------
DATOS = {}
SALIDAS = {}
dir_arm = os.path.join(TEX, 'entity/armadura')
os.makedirs(dir_arm, exist_ok=True)
for d in ('entity/equipment/humanoid', 'entity/equipment/humanoid_leggings', 'particle'):
    os.makedirs(os.path.join(TEX, d), exist_ok=True)
for tema in TEMAS:
    uv, alto, base, mem, luz = generar(tema)
    DATOS[tema] = (uv, alto)
    base.save(os.path.join(dir_arm, f'{tema}.png'))
    mem.save(os.path.join(dir_arm, f'{tema}_membrana.png'))
    for k, im in enumerate(cuadros_brillo(luz)):
        im.save(os.path.join(dir_arm, f'{tema}_brillo_{k}.png'))
    capa_plana(tema, False).save(os.path.join(TEX, f'entity/equipment/humanoid/{tema}.png'))
    capa_plana(tema, True).save(os.path.join(TEX, f'entity/equipment/humanoid_leggings/{tema}.png'))
    for k in range(4):
        tajo(tema, k).save(os.path.join(TEX, f'particle/{tema}_tajo_{k}.png'))
    SALIDAS[tema] = (base, mem, luz)
    print(tema, 'atlas', ANCHO, 'x', alto, '|', len(PARTES[tema]), 'partes')
with open(JAVA, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(java(DATOS))
print('java', JAVA)

if len(sys.argv) > 2:
    hoja = Image.new('RGBA', (ANCHO * 4 * 3 + 40, 256 * 4 + 20), (34, 40, 50, 255))
    for i, tema in enumerate(TEMAS):
        base, mem, luz = SALIDAS[tema]
        im = Image.new('RGBA', base.size, (0, 0, 0, 0))
        im.alpha_composite(base)
        im.alpha_composite(mem)
        im.alpha_composite(luz)
        hoja.alpha_composite(im.resize((im.width * 4, im.height * 4), Image.NEAREST), (10 + i * (ANCHO * 4 + 10), 10))
    hoja.save(sys.argv[2])
    print('hoja', sys.argv[2])

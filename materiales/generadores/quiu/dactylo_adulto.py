"""
El Dáctylo Adulto (DEDsafío 4, Centro de Quiu): el pterosaurio grande que «te agarra, te sube y te suelta». Copia fiel
del icono del cartel 4K (la pose del libro), del tráiler oficial y de los directos (ficha en SP/quiu_ref2/dactylo_adulto).

  vuela siempre   una banda de alas enorme, larga y estrecha, con un cuerpo pequeño en medio; planea con las alas
                  abiertas en «ala de gaviota» (el brazo sube, la mano cae)
  cuerpo          azul marino por arriba, turquesa por debajo (cuello, pecho y vientre); 6 púas en gancho por el lomo
  cabeza          el cráneo rojo con la cara de arriba oscura y el ojo de dos puntos amarillos; el pico en caja, el de
                  arriba naranja con el canto amarillo y el de abajo rojo; la boca abierta, con los dientes blancos en
                  cremallera
  cresta          un abanico de fuego de 14 rayos (rojo en el centro, amarillos y naranjas alternos, el borde amarillo en
                  escalera) de la nuca a la punta del pico, y el cuerno azul marino que sale de la nuca por detrás
  alas            dos tramos (brazo y mano) que se doblan por la muñeca; por arriba azul marino con 5 anillos de fuego, por
                  debajo de fuego con vetas y muescas granate; la barra del borde de ataque acaba en una garra negra
  patas           muslos pálidos, cañas casi negras y pies en gancho para agarrar
  cola            recta, con 2 pares de llamas planas y una placa de anillos abierta por detrás en dos ganchos amarillos

Se construye ya a su tamaño de juego (TAM 1): unos 8 bloques de envergadura y 4 de largo. El píxel, a 16 por bloque; la
cabeza, la cresta, los dientes, las llamas, la placa y las garras, a 32 (B.fino).
"""
import math

import numpy as np

import bestiario as B
import bestiario_reptiles as R
from bestiario import T

ID = 'dactylo_adulto'
TAM = 1.0


# ======================================================================================================================
#  Colores (paleta.json de la ficha: el cartel 4K para los colores de día)
# ======================================================================================================================
def _rampa_dactylo_adulto(*hx):
    return np.array([B.H(h) for h in hx], float)


MARINO_DACTYLO_ADULTO = _rampa_dactylo_adulto('041838', '062b64', '0d3a80', '1a50a4', '3268c0')
TURQUESA_DACTYLO_ADULTO = _rampa_dactylo_adulto('0b3f52', '0d4e63', '196680', '3489a3', '7fb0c4')
MUSLO_DACTYLO_ADULTO = _rampa_dactylo_adulto('3a4e62', '4f6a82', '6e859d', '93aabc', 'bccfdb')
PATA_DACTYLO_ADULTO = _rampa_dactylo_adulto('07090c', '121418', '221a1f', '3a262c', '503238')
PUA_DACTYLO_ADULTO = _rampa_dactylo_adulto('140e10', '2a1a1a', '46282a', '64382f', '7a4836')
GARRA_DACTYLO_ADULTO = _rampa_dactylo_adulto('0e0a0c', '1e1418', '33222a', '4c3a40', '64525a')
CUERNO_DACTYLO_ADULTO = _rampa_dactylo_adulto('051a42', '0a286a', '12408a', '2a5cb0', '4878c8')
CRESTA_DACTYLO_ADULTO = _rampa_dactylo_adulto('a8100e', 'e01a1c', 'f0641a', 'f89a18', 'f8c214', 'fce04a')
CRANEO_DACTYLO_ADULTO = _rampa_dactylo_adulto('7a1210', 'b81e16', 'e02a1c', 'f2543a')
PIZARRA_DACTYLO_ADULTO = _rampa_dactylo_adulto('141630', '202240', '2e3258')
OJO_DACTYLO_ADULTO = B.H('fdd832')
PICO_DACTYLO_ADULTO = _rampa_dactylo_adulto('b04a0c', 'e8701a', 'f69a22', 'f9bd2a', 'fcd458')
QUIJADA_DACTYLO_ADULTO = _rampa_dactylo_adulto('7e1a12', 'b8301e', 'e44426', 'f0643a')
DIENTE_DACTYLO_ADULTO = _rampa_dactylo_adulto('bdb4aa', 'e6e0d6', 'f6f2ea')
BOCA_DACTYLO_ADULTO = _rampa_dactylo_adulto('1a0606', '380c0e', '561418')
FUEGO_DACTYLO_ADULTO = _rampa_dactylo_adulto('5c201c', 'c44d39', 'f0642a', 'fa8c15', 'ffb70e', 'ffd84a')
MUESCA_DACTYLO_ADULTO = _rampa_dactylo_adulto('3e1612', '612621', '7a3428')
ANILLO_DACTYLO_ADULTO = _rampa_dactylo_adulto('c8261a', 'f0641a', 'f8c012')
LLAMA_DACTYLO_ADULTO = _rampa_dactylo_adulto('2b2939', '544a5d', 'c34e40', 'ee622c', 'f48916', 'f9b513')
PLACA_DACTYLO_ADULTO = _rampa_dactylo_adulto('2b2939', '3a3448', '544a5d', 'c42a20', 'e0582c', 'f48916')
GANCHO_DACTYLO_ADULTO = _rampa_dactylo_adulto('c89a14', 'e6c220', 'f9dc3a')

# El huevo: azul marino con el canto de fuego; arriba, el abanico de la cresta (centro rojo, rayos naranja y
# amarillos) con el ojo amarillo debajo; y dos anillos de fuego huecos, como los del ala.
HUEVO = (('1a50a4', '062b64', '041838'), ('fa8c15', 'c44d39'),
         [((7, 3), 'f0641a'), ((8, 3), 'f8c214'), ((9, 3), 'f0641a'), ((6, 4), 'f8c214'), ((7, 4), 'e01a1c'),
          ((8, 4), 'f0641a'), ((9, 4), 'e01a1c'), ((10, 4), 'f8c214'), ((8, 5), 'e01a1c'), ((9, 6), 'fdd832'),
          ((4, 9), 'c8261a'), ((5, 9), 'f0641a'), ((6, 9), 'f8c012'), ((4, 10), 'c8261a'), ((6, 10), 'f8c012'),
          ((4, 11), 'f0641a'), ((5, 11), 'f8c012'), ((6, 11), 'f8c012'),
          ((9, 11), 'c8261a'), ((10, 11), 'f0641a'), ((11, 11), 'f8c012'), ((9, 12), 'f0641a'),
          ((11, 12), 'f8c012'), ((9, 13), 'f0641a'), ((10, 13), 'f8c012'), ((11, 13), 'f8c012')])


# ======================================================================================================================
#  Ayudantes de pintura
# ======================================================================================================================
def _malla_dactylo_adulto(tw, th):
    ys, xs = np.mgrid[0:th, 0:tw]
    return xs, ys


def _tono_dactylo_adulto(R_, idx):
    """El tono de la rampa (sin mezclas: cada píxel, uno de sus tonos)."""
    return R_[np.clip(np.round(idx), 0, len(R_) - 1).astype(int)]


def _tex_dactylo_adulto(rgb, dentro=None):
    th, tw = rgb.shape[:2]
    out = np.zeros((th, tw, 4), np.uint8)
    out[..., :3] = np.clip(np.round(rgb), 0, 255)
    out[..., 3] = 255 if dentro is None else np.where(dentro, 255, 0)
    return out


def _pintor_dactylo_adulto(nombre, fn, fino=False, pleno=False):
    p = B.Pintor(nombre, fn, pleno=pleno)
    return B.fino(p, 0.5) if fino else p


def _brilla_dactylo_adulto(tex, mascara):
    """Lo que brilla (el fuego: en los directos de noche la cresta, la cara de abajo de las alas, las llamas y la placa
    siguen encendidas mientras el cuerpo, el cráneo y el pico se apagan)."""
    emis = np.zeros_like(tex)
    mk = mascara & (tex[..., 3] > 0)
    emis[mk] = tex[mk]
    return emis if mk.any() else None


def _trazo_dactylo_adulto(tw, th, puntos, grosor):
    """Un trazo por 'puntos' (en píxeles del pintor, x hacia la derecha e y hacia abajo), de 'grosor' (raíz, punta):
    devuelve lo que pinta y lo que lleva andado cada píxel (0 en la raíz, 1 en la punta)."""
    xs, ys = _malla_dactylo_adulto(tw, th)
    x, y = xs + 0.5, ys + 0.5
    seg = []
    for (x0, y0), (x1, y1) in zip(puntos[:-1], puntos[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) * 4))
        for t in np.linspace(0, 1, n, endpoint=False):
            seg.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    seg.append(puntos[-1])
    mejor = np.full((th, tw), np.inf)
    avance = np.zeros((th, tw))
    for i, (sx, sy) in enumerate(seg):
        t = i / max(1, len(seg) - 1)
        d = np.hypot(x - sx, y - sy) - (grosor[0] + (grosor[1] - grosor[0]) * t)
        mk = d < mejor
        mejor = np.where(mk, d, mejor)
        avance = np.where(mk, t, avance)
    return mejor < 0, avance


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def piel_dactylo_adulto(nombre, marino_filas, panza=True):
    """El cuerpo y el cuello: azul marino arriba (la cara de arriba y las 'marino_filas' de arriba de las caras de los
    lados, con el canto un tono más claro) y turquesa debajo, el canto de abajo un tono más oscuro; la panza, en
    cuadros grandes de dos tonos (los «cuadros azul pizarra» del vientre)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        if cara == 'arriba':
            idx = np.where((xs == 0) | (xs == tw - 1), 2, 1)
            rgb = _tono_dactylo_adulto(MARINO_DACTYLO_ADULTO, idx)
        elif cara == 'abajo':
            idx = 1 + ((xs // 3 + ys // 3) % 2) if panza else np.full((th, tw), 2)
            rgb = _tono_dactylo_adulto(TURQUESA_DACTYLO_ADULTO, idx)
        else:
            marino = (ys + 0.5) < marino_filas
            im = np.where(ys == 0, 2, 1)
            it = np.where(ys == th - 1, 1, 2)
            rgb = np.where(marino[..., None], _tono_dactylo_adulto(MARINO_DACTYLO_ADULTO, im),
                           _tono_dactylo_adulto(TURQUESA_DACTYLO_ADULTO, it))
        return _tex_dactylo_adulto(rgb), None
    return _pintor_dactylo_adulto(nombre, fn)


def liso_dactylo_adulto(nombre, R_, base=1, arriba=None, abajo=None, fino=False):
    """Un color limpio: la cara de arriba un tono más clara y la de abajo más oscura; en los lados, el canto de arriba
    claro."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        if cara == 'arriba':
            idx = np.full((th, tw), base + 1 if arriba is None else arriba)
        elif cara == 'abajo':
            idx = np.full((th, tw), base - 1 if abajo is None else abajo)
        else:
            idx = np.where((ys == 0) & (th > 2), base + 1, base)
        return _tex_dactylo_adulto(_tono_dactylo_adulto(R_, idx)), None
    return _pintor_dactylo_adulto(nombre, fn, fino)


def craneo_dactylo_adulto(nombre):
    """El cráneo (a 32 por bloque): los lados rojos con la franja oscura de arriba y el ojo de dos texels amarillos
    separados por uno oscuro, justo debajo de la franja, en la mitad de delante; la cara de arriba, pizarra oscura."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        if cara in ('izq', 'der'):
            u = xs if cara == 'izq' else (tw - 1 - xs)          # de atrás (0) hacia delante
            idx = np.where(ys >= th - 1, 1, 2)
            rgb = _tono_dactylo_adulto(CRANEO_DACTYLO_ADULTO, idx)
            rgb[ys < 2] = PIZARRA_DACTYLO_ADULTO[1]
            e0 = int(round(tw * 0.5))
            ojo = (ys == 2) & ((u == e0) | (u == e0 + 2))
            hueco = (ys == 2) & (u == e0 + 1)
            rgb[ojo] = OJO_DACTYLO_ADULTO
            rgb[hueco] = PIZARRA_DACTYLO_ADULTO[0]
        elif cara == 'arriba':
            rgb = _tono_dactylo_adulto(PIZARRA_DACTYLO_ADULTO, np.where((xs == 0) | (xs == tw - 1), 2, 1))
        elif cara == 'abajo':
            rgb = _tono_dactylo_adulto(CRANEO_DACTYLO_ADULTO, np.zeros((th, tw)))
        else:
            rgb = _tono_dactylo_adulto(CRANEO_DACTYLO_ADULTO, np.where(ys >= th - 1, 1, 2))
            rgb[ys < 2] = PIZARRA_DACTYLO_ADULTO[1]
        return _tex_dactylo_adulto(rgb), None
    return _pintor_dactylo_adulto(nombre, fn, fino=True)


def pico_dactylo_adulto(nombre):
    """El pico de arriba (a 32 por bloque): los costados naranja con el canto de arriba amarillo; la cara de arriba y la
    punta, amarillas; por debajo, el techo de la boca, granate oscuro."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        if cara in ('izq', 'der'):
            idx = np.where(ys == 0, 3, np.where(ys >= th - 1, 0, 1))
            rgb = _tono_dactylo_adulto(PICO_DACTYLO_ADULTO, idx)
        elif cara == 'arriba':
            rgb = _tono_dactylo_adulto(PICO_DACTYLO_ADULTO, np.where((xs == 0) | (xs == tw - 1), 2, 3))
        elif cara == 'frente':
            rgb = _tono_dactylo_adulto(PICO_DACTYLO_ADULTO, np.where(ys >= th - 1, 2, 3))
        elif cara == 'abajo':
            rgb = _tono_dactylo_adulto(BOCA_DACTYLO_ADULTO, np.ones((th, tw)))
        else:
            rgb = _tono_dactylo_adulto(PICO_DACTYLO_ADULTO, np.ones((th, tw)))
        return _tex_dactylo_adulto(rgb), None
    return _pintor_dactylo_adulto(nombre, fn, fino=True)


def quijada_dactylo_adulto(nombre):
    """El pico de abajo (a 32 por bloque): rojo-naranja, más oscuro que el de arriba; por encima, el suelo de la boca."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        if cara in ('izq', 'der', 'frente'):
            idx = np.where(ys == 0, 2, np.where(ys >= th - 1, 0, 1))
            rgb = _tono_dactylo_adulto(QUIJADA_DACTYLO_ADULTO, idx)
        elif cara == 'arriba':
            rgb = _tono_dactylo_adulto(BOCA_DACTYLO_ADULTO, np.ones((th, tw)))
        else:
            rgb = _tono_dactylo_adulto(QUIJADA_DACTYLO_ADULTO, np.zeros((th, tw)))
        return _tex_dactylo_adulto(rgb), None
    return _pintor_dactylo_adulto(nombre, fn, fino=True)


def dientes_dactylo_adulto(nombre, arriba, desfase=0, frente=0):
    """Los dientes en su 2.ª capa (a 32 por bloque): una fila en cada costado, de 1 texel de ancho y 2-3 de largo con 1
    de hueco (los de arriba cuelgan; los de abajo, de pie y desfasados uno: la cremallera); en la cara de delante,
    'frente' dientes verticales más. Lo demás, vacío."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara in ('izq', 'der'):
            u = xs if cara == 'izq' else (tw - 1 - xs)          # de atrás hacia delante
            r = ys if arriba else (th - 1 - ys)                  # desde la encía hacia la punta
            col = (u + desfase) % 2 == 0
            largo = np.where(((u + desfase) // 2) % 2 == 0, th, th - 1)
            dentro = col & (r < largo)
        elif cara == 'frente' and frente:
            r = ys if arriba else (th - 1 - ys)
            paso = max(2, tw // (frente + 1))
            dentro = ((xs % paso) == paso // 2) & (xs > 0) & (xs < tw - 1) & (r < th)
        else:
            return tex, None
        idx = np.where(r == 0, 1, 2)
        tex[..., :3] = _tono_dactylo_adulto(DIENTE_DACTYLO_ADULTO, idx)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return _pintor_dactylo_adulto(nombre, fn, fino=True)


def boca_dactylo_adulto(nombre, cuna):
    """El fondo de la boca (lámina de perfil, a 32 por bloque): granate muy oscuro, más negro hacia la garganta;
    'cuna(u, v)' dice qué parte de la lámina es boca (u de delante hacia atrás, v de arriba abajo, de 0 a 1)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        u, v = (xs + 0.5) / tw, (ys + 0.5) / th
        dentro = cuna(u, v)
        rgb = _tono_dactylo_adulto(BOCA_DACTYLO_ADULTO, np.where(u > 0.75, 0, 1))
        return _tex_dactylo_adulto(rgb, dentro), None
    return _pintor_dactylo_adulto(nombre, fn, fino=True)


def cresta_dactylo_adulto(nombre, largo, alto, centro_u, delante, detras, nuca_u, cuerno_ang, rayos=14):
    """La cresta (lámina de perfil, a 32 por bloque): un abanico que sale de un punto justo encima del ojo ('centro_u',
    medido desde la punta del pico hacia atrás) y se abre de la punta del pico a lo largo del cuerno: por debajo la
    limita la línea de la cabeza y por detrás el cuerno (sube desde la nuca, 'nuca_u', con 'cuerno_ang' grados); por
    fuera, un óvalo de radio 'delante' hacia el pico, 'alto' hacia arriba y 'detras' hacia atrás. 'rayos' cuñas iguales
    en ángulo, alternas: amarillas (naranja junto al centro, amarillo claro en el borde) y rojas (rojo oscuro dentro,
    rojo-naranja hacia fuera); el centro rojo y el borde en escalera de un texel, amarillo claro. Medidas en píxeles del
    modelo."""
    t_c = math.tan(math.radians(cuerno_ang))

    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        k = tw / largo                                            # texels por píxel del modelo
        u = (xs + 0.5) / k                                        # de delante hacia atrás
        v = (th - ys - 0.5) / k                                   # alto sobre la línea de la cabeza
        du = centro_u - u                                         # > 0 hacia el pico
        a = np.where(du > 0, delante, detras)
        rr = np.hypot(du / a, v / alto)                           # 1 en el borde
        cuerno = (u > nuca_u) & (v < (u - nuca_u) * t_c)          # por debajo del cuerno
        dentro = (v >= 0) & (rr < 1.0) & ~cuerno
        ang = np.degrees(np.arctan2(v, du))                       # 0 hacia el pico, 180 hacia atrás
        a_max = 180.0 - cuerno_ang * 0.6
        sector = np.clip((ang / a_max * rayos).astype(int), 0, rayos - 1)
        amarillo = sector % 2 == 0
        idx = np.where(amarillo, np.where(rr < 0.42, 3, 4), np.where(rr < 0.84, 1, 2)).astype(float)
        idx = np.where(rr < 0.2, 1, idx)                          # el centro, rojo
        radio = np.hypot(du, v) / np.maximum(1e-3, rr)            # el radio del borde en esa dirección
        borde = dentro & (rr > 1.0 - 1.2 / (k * np.maximum(1.0, radio)))
        idx = np.where(borde, np.where(amarillo, 5, 4), idx)
        rgb = _tono_dactylo_adulto(CRESTA_DACTYLO_ADULTO, idx)
        return _tex_dactylo_adulto(rgb, dentro), None
    return _pintor_dactylo_adulto(nombre, fn, fino=True, pleno=True)


def ala_dactylo_adulto(nombre, lado, s0, largo, cuerda, s_garra, s_punta, anillos):
    """La membrana de un tramo del ala (losa de 1 de grueso), pintada en las coordenadas del ala: s, del costado hacia
    la punta; c, del borde de ataque hacia atrás. Por arriba, azul marino con los anillos de fuego; por debajo, fuego
    (base naranja, vetas amarillas que salen del borde de ataque hacia atrás y afuera, rojo hacia el borde de salida);
    el borde de salida, con muescas granate cada 3. La punta, cortada en oblicuo de la garra ('s_garra', c = 0) a la
    esquina de atrás ('s_punta', c = cuerda). 'lado' 1: el ala izquierda (+X); -1: la derecha, cuya losa va girada media
    vuelta sobre el eje de delante (su cara de arriba es la de abajo del mundo)."""
    def coords(tw, th, cara):
        xs, ys = _malla_dactylo_adulto(tw, th)
        x, y = xs + 0.5, ys + 0.5
        if cara == 'arriba':
            return s0 + x, cuerda - y
        if cara == 'abajo':
            return s0 + x, y
        if cara == 'atras':
            return s0 + largo - x, np.full_like(x, cuerda)
        if cara == 'izq':
            return np.full_like(x, s0), cuerda - x
        if cara == 'der':
            return np.full_like(x, s0 + largo), x
        return s0 + x, np.zeros_like(x)

    def dentro_de(S, C):
        # Cuerda constante (en el juego la banda es casi igual de ancha hasta la punta; recortarla con transparencia
        # borraría el canto naranja del borde de salida, que se ve en el icono).
        return (S <= s_garra) | (C >= (S - s_garra) / max(0.1, s_punta - s_garra) * cuerda)

    def arriba_(S, C):
        # Azul marino, con vetas suaves algo más claras que salen del borde de ataque hacia atrás y afuera (las fibras
        # que se ven en el tráiler y de cerca en el juego), de 2 tonos y sin motas.
        u = S - C * 0.7
        veta = (np.floor(u / 2.0) % 4 == 0) & (C > 2.0) & (C < cuerda - 2.0)
        idx = np.where(C < 2.0, 2, np.where(veta, 2, 1)).astype(float)
        idx = np.where(C > cuerda - 1.0, 0, idx)
        rgb = _tono_dactylo_adulto(MARINO_DACTYLO_ADULTO, idx)
        # Los anillos: octógonos de píxel (D píxeles enteros de lado, las esquinas cortadas en escalón), con trazo de 1
        # (2 en los grandes); el color gira del rojo al naranja y al amarillo alrededor del anillo.
        for (s_ini, D) in anillos:
            c_ini = int(round((cuerda - D) / 2.0))
            i = np.floor(S - s_ini).astype(int)
            j = np.floor(C - c_ini).astype(int)
            dentro_caja = (i >= 0) & (i < D) & (j >= 0) & (j < D)

            def octo(i, j, n, corte):
                return ((i >= 0) & (j >= 0) & (i < n) & (j < n) & (i + j >= corte) & ((n - 1 - i) + j >= corte)
                        & (i + (n - 1 - j) >= corte) & ((n - 1 - i) + (n - 1 - j) >= corte))
            g = 2 if D >= 8 else 1
            corte = max(1, int(round(D / 3.4)))
            trazo = dentro_caja & octo(i, j, D, corte) & ~octo(i - g, j - g, D - 2 * g, max(0, corte - g))
            dx, dy = i - (D - 1) / 2.0, j - (D - 1) / 2.0
            t = (1 + np.cos(np.arctan2(dy, dx) - math.radians(-50))) / 2   # rojo a un lado, amarillo al otro
            col = _tono_dactylo_adulto(ANILLO_DACTYLO_ADULTO, np.round(t * 2))
            rgb = np.where(trazo[..., None], col, rgb)
        # Las muescas del borde de salida, vistas desde arriba: la sierra.
        muesca = (C > cuerda - 1.0) & (np.floor(S) % 3 == 0)
        rgb = np.where(muesca[..., None], MUESCA_DACTYLO_ADULTO[1], rgb)
        return rgb

    def abajo_(S, C):
        # Bandas anchas de fuego (amarillo, naranja, rojo-naranja) que salen del borde de ataque hacia atrás y afuera,
        # algo onduladas como llamas, más rojas hacia el borde de salida.
        n = C - 0.75 * S + 1.1 * np.sin(S * 0.33 + C * 0.21)
        ciclo = np.array([4, 3, 2, 3, 4, 3, 2, 1], float)
        idx = ciclo[(np.floor(n / 2.6) % len(ciclo)).astype(int)]
        idx = np.where(C > cuerda * 0.62, np.maximum(1, idx - 1), idx)
        idx = np.where(C < 1.2, 3, idx)
        rgb = _tono_dactylo_adulto(FUEGO_DACTYLO_ADULTO, idx)
        k = np.floor(S) % 3
        muesca = ((C > cuerda - 1.0) & (k != 2)) | ((C > cuerda - 2.0) & (k == 0))
        rgb = np.where(muesca[..., None], MUESCA_DACTYLO_ADULTO[1], rgb)
        return rgb

    def canto_(S, C):
        idx = np.full(S.shape, 3.0)
        rgb = _tono_dactylo_adulto(FUEGO_DACTYLO_ADULTO, idx)
        muesca = np.floor(S) % 3 == 0
        return np.where(muesca[..., None], MUESCA_DACTYLO_ADULTO[1], rgb)

    def fn(tw, th, cara, s):
        S, C = coords(tw, th, cara)
        dentro = dentro_de(S, C)
        mundo = cara
        if lado < 0 and cara in ('arriba', 'abajo'):
            mundo = 'abajo' if cara == 'arriba' else 'arriba'
        if mundo == 'arriba':
            return _tex_dactylo_adulto(arriba_(S, C), dentro), None
        if cara in ('izq', 'der'):
            # Los extremos de cada tramo (la muñeca): del azul de arriba, para que el pliegue no deje una raya.
            return _tex_dactylo_adulto(_tono_dactylo_adulto(MARINO_DACTYLO_ADULTO, np.ones(S.shape)), dentro), None
        rgb = abajo_(S, C) if mundo == 'abajo' else canto_(S, C)
        tex = _tex_dactylo_adulto(rgb, dentro)
        return tex, _brilla_dactylo_adulto(tex, np.ones(dentro.shape, bool))
    return _pintor_dactylo_adulto(nombre, fn)


def barra_dactylo_adulto(nombre, lado):
    """La barra del borde de ataque: azul marino, la cara de arriba más clara y la de abajo casi negra (en el ala
    derecha la losa va girada: su 'arriba' es la de abajo)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        mundo = cara
        if lado < 0 and cara in ('arriba', 'abajo'):
            mundo = 'abajo' if cara == 'arriba' else 'arriba'
        if mundo == 'arriba':
            idx = np.full((th, tw), 3.0)
        elif mundo == 'abajo':
            idx = np.full((th, tw), 0.0)
        else:
            fila = ys if lado > 0 else (th - 1 - ys)
            idx = np.where(fila == 0, 2, 1)
        return _tex_dactylo_adulto(_tono_dactylo_adulto(MARINO_DACTYLO_ADULTO, idx)), None
    return _pintor_dactylo_adulto(nombre, fn)


def gancho_dactylo_adulto(nombre, R_, puntos, grosor, claro=True):
    """Un gancho dibujado (lámina): la garra de la punta del ala, los pies en J, las púas en «r». Oscuro en la raíz y
    un tono más claro hacia la punta, con el canto de un lado claro."""
    def fn(tw, th, cara, s):
        dentro, t = _trazo_dactylo_adulto(tw, th, [(px * tw, py * th) for px, py in puntos],
                                          (grosor[0] * tw, grosor[1] * tw))
        idx = 1.0 + 1.6 * t + (0.6 if claro else 0.0) * 0
        return _tex_dactylo_adulto(_tono_dactylo_adulto(R_, idx), dentro), None
    return _pintor_dactylo_adulto(nombre, fn, fino=True)


def llama_dactylo_adulto(nombre, barra, largo_u, ancho_w):
    """Un par de llamas de la cola (lámina plana y horizontal, cara hacia arriba, a 32 por bloque): a cada lado de la
    barra ('barra', su ancho), una hoja barrida hacia atrás (la parte de delante junto a la barra y la punta hacia fuera
    y atrás); el núcleo junto a la barra amarillo-naranja, el cuerpo rojo-naranja, la parte de delante roja y el borde
    gris morado, dentado. La textura: columnas de -X a +X; fila 0 detrás."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        k = tw / (barra + 2 * largo_u)
        x = (xs + 0.5) / k - (barra / 2 + largo_u)                  # 0 en el eje de la cola
        w = (th - ys - 0.5) / k                                     # de delante (0) hacia atrás (ancho_w)
        u = np.abs(x) - barra / 2                                   # hacia fuera desde la barra
        f = np.clip(u / largo_u, 0, 1.2)
        w_punta = ancho_w * 0.5                                     # la punta, a media hoja y algo hacia atrás
        frente = w_punta * f ** 2.6                                 # el canto de delante: casi recto y al final atrás
        detras = ancho_w - (ancho_w - w_punta) * f ** 2.0           # el de atrás: ancha hasta cerca de la punta
        dentro = (u > -0.4) & (f < 1.0) & (w >= frente) & (w <= detras)
        # El borde gris morado, dentado: lo que queda a menos de 1,6 texels del contorno, a dientes de 2.
        hueco = (np.minimum(w - frente, detras - w) * k)
        fuera = (1.0 - f) * largo_u * k
        dist = np.minimum(hueco, fuera)
        diente = ((np.floor((w + u) * k / 2) % 2) == 0)
        borde = dentro & (u > 0.2) & (dist < np.where(diente, 2.2, 1.2))
        idx = np.where(f < 0.28, 5, np.where(f < 0.5, 4, 3)).astype(float)
        idx = np.where((w - frente) * k < 3.0 + 4.0 * (1 - f), np.where(f > 0.35, 2, idx), idx)  # la parte de delante, roja
        idx = np.where(borde, np.where(diente, 0, 1), idx)
        tex = _tex_dactylo_adulto(_tono_dactylo_adulto(LLAMA_DACTYLO_ADULTO, idx), dentro)
        return tex, _brilla_dactylo_adulto(tex, idx >= 2)
    return _pintor_dactylo_adulto(nombre, fn, fino=True)


def placa_dactylo_adulto(nombre, ancho, largo_ovalo, largo_total):
    """La placa de la cola (lámina plana y horizontal, cara hacia arriba, a 32 por bloque): un óvalo de anillos
    concéntricos (rojo-naranja, gris morado, naranja, gris morado oscuro y el centro rojo con un cuadrito oscuro); el
    anillo de fuera se abre por detrás y sus dos extremos siguen en dos ganchos amarillos que se curvan hacia dentro sin
    tocarse. La textura: columnas de -X a +X; fila 0 detrás (los ganchos)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla_dactylo_adulto(tw, th)
        k = tw / ancho
        x = (xs + 0.5) / k - ancho / 2                              # 0 en el eje
        w = (th - ys - 0.5) / k                                     # de delante (0) hacia atrás
        a, b = ancho / 2, largo_ovalo / 2
        r = np.hypot(x / a, (w - b) / b)
        ang = np.degrees(np.arctan2(np.abs(x), w - b))              # 0 hacia atrás, 180 hacia delante
        ovalo = r < 1.0
        abierto = (ang < 36) & (r > 0.74)
        dentro = ovalo & ~abierto
        idx = np.full(r.shape, 4.0)                                 # rojo-naranja
        idx = np.where(r < 0.76, 2, idx)                            # gris morado
        idx = np.where(r < 0.62, 5, idx)                            # naranja
        idx = np.where(r < 0.44, 1, idx)                            # gris morado oscuro
        idx = np.where(r < 0.34, 3, idx)                            # el centro rojo
        cx, cw = np.abs(x), np.abs(w - b)                           # el cuadrito: marco gris morado, rojo dentro
        cuad = (np.maximum(cx / 0.62, cw / 0.8) < 1.0) & (np.maximum(cx / 0.62, cw / 0.8) > 0.45)
        idx = np.where(cuad, 1, idx)
        rgb = _tono_dactylo_adulto(PLACA_DACTYLO_ADULTO, idx)
        calido = idx >= 3
        # Los dos ganchos (largos, como en el tráiler visto desde abajo y en 0m05s33): el anillo de fuera sigue por cada
        # lado, hacia atrás, y se cierra un poco hacia dentro, cada vez más fino, sin tocarse las puntas (a un tercio
        # del ancho una de otra).
        ext = largo_total - largo_ovalo
        for lado in (-1, 1):
            p0 = (a * 0.88 * math.sin(math.radians(42)), b + b * 0.88 * math.cos(math.radians(42)))
            pts = [(lado * p0[0], p0[1]), (lado * a * 0.56, largo_ovalo + 0.3 * ext),
                   (lado * a * 0.44, largo_ovalo + 0.7 * ext), (lado * a * 0.27, largo_total - 0.3)]
            pts_px = [((px + ancho / 2) * k, th - py * k) for px, py in pts]
            g, t = _trazo_dactylo_adulto(tw, th, pts_px, (0.85 * k, 0.2 * k))
            g = g & ~(ovalo & ~abierto & (r < 0.86))
            rgb = np.where(g[..., None], _tono_dactylo_adulto(GANCHO_DACTYLO_ADULTO, 0.4 + 1.8 * t), rgb)
            dentro = dentro | g
            calido = calido | g
        tex = _tex_dactylo_adulto(rgb, dentro)
        return tex, _brilla_dactylo_adulto(tex, calido)
    return _pintor_dactylo_adulto(nombre, fn, fino=True)


# ======================================================================================================================
#  Las piezas
# ======================================================================================================================
E_DACTYLO_ADULTO = 0.04


def bloque_dactylo_adulto(m, parte, M, centro, tam, nombre, marino_por_arriba, panza=True):
    """Una pieza de cantos achaflanados (tres cajas cruzadas, como 'redondo') en el marco M, pintada con el azul marino
    hasta 'marino_por_arriba' píxeles por debajo de su cara de arriba (en cada caja, lo mismo de alto: la línea queda
    recta) y turquesa debajo."""
    w, h, d = tam
    cajas = ((w, h - 2, d - 2), (w - 2 - E_DACTYLO_ADULTO, h, d - 2 - E_DACTYLO_ADULTO),
             (w - 2 - 2 * E_DACTYLO_ADULTO, h - 2 - E_DACTYLO_ADULTO, d))
    for k, (cw, ch, cd) in enumerate(cajas):
        filas = marino_por_arriba - (h - ch) / 2
        p = piel_dactylo_adulto(f'{nombre}_{k}', max(0.0, filas), panza)
        R.caja_en(m, parte, M, centro, (cw, ch, cd), p)


def construir():
    """El modelo a su tamaño de juego, planeando con las alas abiertas."""
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0
    Gx = B.girar

    # ------------------------------------------------------------------ el tronco
    # Una caja de sección casi cuadrada, algo más larga que la cabeza, un poco levantada por delante (el pecho más alto
    # que la cadera).
    m.parte('cuerpo', None, (0, 12, 0))
    Mtr = T(0, 12, 0) @ Gx((-6, 0, 0))

    def en_tronco(p):
        return (Mtr @ np.array((*p, 1.0)))[:3]
    bloque_dactylo_adulto(m, 'cuerpo', Mtr, (0, 0, 0), (6.6, 6.6, 15), 'tronco_dactylo_adulto', 3.0)
    # Las púas del lomo: postes de 1 con la punta doblada hacia atrás («r»), del arranque del cuello a media espalda, y
    # 2 más pequeñas al principio de la cola.
    pua = liso_dactylo_adulto('pua_dactylo_adulto', PUA_DACTYLO_ADULTO, base=1, arriba=2, abajo=0, fino=True)
    # Como en el tráiler (1m23.54s): postes finos (1 texel a 32 por bloque), unas 4 veces más altos que anchos y
    # separados otro tanto, con el gancho de arriba doblado hacia atrás.
    for k, z in enumerate((6.6, 4.7, 2.8, 0.9, -1.0, -2.9)):
        h = 2.4 if 0 < k < 5 else 2.0
        R.caja_en(m, 'cuerpo', Mtr, (0, 3.3 + h / 2 - 0.1, z), (0.5, h, 0.5), pua)
        R.caja_en(m, 'cuerpo', Mtr, (0, 3.3 + h - 0.35, z - 0.55), (0.5, 0.5, 0.6), pua)

    # ------------------------------------------------------------------ el cuello
    # Sale del pecho hacia delante y arriba (25°), en 3 cajas que adelgazan hacia la cabeza: marino arriba, turquesa
    # por los lados y por debajo.
    sube = 25.0
    N0 = en_tronco((0, 1.0, 6.6))
    u_cuello = np.array((0.0, math.sin(math.radians(sube)), math.cos(math.radians(sube))))
    m.parte('cuello', 'cuerpo', tuple(N0))
    Mc = T(*N0) @ Gx((-sube, 0, 0))
    bloque_dactylo_adulto(m, 'cuello', Mc, (0, 0, 2.2), (4.4, 4.4, 5), 'cuello1_dactylo_adulto', 1.4, panza=False)
    R.caja_en(m, 'cuello', Mc, (0, 0, 5.8), (3.6, 3.6, 4), piel_dactylo_adulto('cuello2_dactylo_adulto', 1.2, False))
    R.caja_en(m, 'cuello', Mc, (0, 0, 8.9), (3.1, 3.1, 3.4), piel_dactylo_adulto('cuello3_dactylo_adulto', 1.0, False))
    NE = N0 + u_cuello * 10.2

    # ------------------------------------------------------------------ la cabeza
    # El marco de la cabeza: el origen en la nuca (atrás del cráneo, en medio), Z por la línea del pico, mirando hacia
    # delante y algo abajo.
    baja = 14.0
    H0 = NE - u_cuello * 0.6
    m.parte('cabeza', 'cuello', tuple(H0))
    Mh = T(*H0) @ Gx((baja, 0, 0))
    # El cráneo: 6 de largo, 3,4 de alto y 4 de ancho (la cabeza, más o menos tan larga como el tronco).
    R.caja_en(m, 'cabeza', Mh, (0, 0, 3.0), (4, 3.4, 6), craneo_dactylo_adulto('craneo_dactylo_adulto'))
    # El pico de arriba: una caja larga y recta (12 x 1,8 x 3,4), arriba, a ras del cráneo.
    R.caja_en(m, 'cabeza', Mh, (0, 0.8, 12), (3.4, 1.8, 12), pico_dactylo_adulto('pico_dactylo_adulto'))
    # Los dientes: 10 por fila (la ficha: 9-10), de 1 texel con 1 de hueco, del medio del pico a la punta.
    R.caja_en(m, 'cabeza', Mh, (0, -0.73, 13.1), (3.6, 1.55, 10.0),
              dientes_dactylo_adulto('dientes_arriba_dactylo_adulto', True, 0, frente=2))
    # La cresta: lámina de perfil, un abanico desde encima del ojo (z = 4) que va de la punta del pico (z = 18) a lo
    # largo del cuerno, en el que apoya su borde de atrás.
    c_u, c_del, c_det, alto_c = 14.0, 14.0, 8.8, 8.4
    largo_c = c_u + c_det
    Mcr = Mh @ T(0, 1.7, 18 - largo_c / 2) @ Gx((0, 90, 0))
    R.lamina(m, 'cabeza', Mcr, largo_c, alto_c,
             cresta_dactylo_adulto('cresta_dactylo_adulto', largo_c, alto_c, centro_u=c_u, delante=c_del,
                                   detras=c_det, nuca_u=18.0 - 1.1, cuerno_ang=28.0))
    # El cuerno: barra azul marino que sale de la nuca hacia atrás y algo arriba, por el borde de atrás de la cresta.
    ang_c = 28.0
    largo_cu = 9.0
    dir_c = np.array((0.0, math.sin(math.radians(ang_c)), -math.cos(math.radians(ang_c))))
    p_c = np.array((0.0, 1.55, 1.1)) + dir_c * (largo_cu / 2)
    R.caja_en(m, 'cabeza', Mh @ T(*p_c) @ Gx((ang_c, 0, 0)), (0, 0, 0), (1.7, 1.7, largo_cu),
              liso_dactylo_adulto('cuerno_dactylo_adulto', CUERNO_DACTYLO_ADULTO, base=1, arriba=2, abajo=0))

    # ------------------------------------------------------------------ la mandíbula (boca abierta)
    abre = 22.0
    gozne = np.array((0.0, -0.1, 4.8))
    m.parte('mandibula', 'cabeza', tuple((Mh @ np.array((*gozne, 1.0)))[:3]))
    Mj = Mh @ T(*gozne) @ Gx((abre, 0, 0))
    R.caja_en(m, 'mandibula', Mj, (0, -0.85, 5.6), (2.9, 1.7, 15.2), quijada_dactylo_adulto('quijada_dactylo_adulto'))
    R.caja_en(m, 'mandibula', Mj, (0, 0.575, 8.1), (3.1, 1.35, 10.0),
              dientes_dactylo_adulto('dientes_abajo_dactylo_adulto', False, 1, frente=1))
    # El fondo de la boca: una lámina de perfil entre los dos picos (en la mandíbula: al cerrarla se esconde en el pico).
    t_ab = math.tan(math.radians(abre))

    def cuna(u, v):
        z = 12.8 - u * 12.4                                        # de delante (12,8) hacia el gozne (0,4)
        alto_hueco = z * t_ab + 1.1
        return (v * 4.2) < alto_hueco
    R.lamina(m, 'mandibula', Mj @ T(0, 0.02, 6.6) @ Gx((0, 90, 0)), 12.4, 4.2,
             boca_dactylo_adulto('boca_dactylo_adulto', lambda u, v: cuna(u, 1 - v)))

    # ------------------------------------------------------------------ las alas
    cuerda = 15.0
    s_brazo, s_mano = 15.0, 27.0
    s_garra = 37.0
    s_punta = s_brazo + s_mano
    diedro_b, diedro_m, flecha = 10.0, -9.0, 6.0
    anillos = ((2, 8), (12, 7), (21, 6), (29, 5), (35, 4))     # (dónde empieza, diámetro), en píxeles enteros
    hombro = en_tronco((3.0, 2.3, 6.6))
    for lado, ld in R.LADOS:
        O = hombro * np.array((lado, 1, 1))
        if lado > 0:
            Mb = T(*O) @ Gx((0, flecha, diedro_b))
        else:
            Mb = T(*O) @ B.Rz(math.radians(-diedro_b)) @ B.Ry(math.radians(-flecha)) @ B.Rz(math.pi)
        m.parte(f'ala_{ld}', 'cuerpo', tuple(O))
        R.caja_en(m, f'ala_{ld}', Mb, (s_brazo / 2, 0, -cuerda / 2), (s_brazo, 1, cuerda),
                  ala_dactylo_adulto(f'ala1_{ld}_dactylo_adulto', lado, 0.0, s_brazo, cuerda, s_garra, s_punta,
                                     anillos))
        R.caja_en(m, f'ala_{ld}', Mb, ((s_brazo - 1.2) / 2, 0, 0), (s_brazo + 1.2, 2, 2),
                  barra_dactylo_adulto(f'barra1_{ld}_dactylo_adulto', lado))
        W = (Mb @ np.array((s_brazo, 0, 0, 1.0)))[:3]
        if lado > 0:
            Mm = T(*W) @ Gx((0, flecha, diedro_m))
        else:
            Mm = T(*W) @ B.Rz(math.radians(-diedro_m)) @ B.Ry(math.radians(-flecha)) @ B.Rz(math.pi)
        m.parte(f'mano_{ld}', f'ala_{ld}', tuple(W))
        R.caja_en(m, f'mano_{ld}', Mm, (s_mano / 2, 0, -cuerda / 2), (s_mano, 1, cuerda),
                  ala_dactylo_adulto(f'ala2_{ld}_dactylo_adulto', lado, s_brazo, s_mano, cuerda, s_garra, s_punta,
                                     anillos))
        lb = s_garra - s_brazo
        R.caja_en(m, f'mano_{ld}', Mm, (lb / 2 - 0.5, 0, 0), (lb + 1, 2, 2),
                  barra_dactylo_adulto(f'barra2_{ld}_dactylo_adulto', lado))
        # La garra: un nudo negro algo más gordo que la barra y un gancho que se curva hacia delante y abajo.
        Pg = (Mm @ np.array((lb + 0.3, 0, 0, 1.0)))[:3]
        R.caja_en(m, f'mano_{ld}', Mm, (lb + 0.3, 0, 0.1), (2.2, 2.5, 2.6),
                  liso_dactylo_adulto(f'garra_{ld}_dactylo_adulto', GARRA_DACTYLO_ADULTO, base=1, arriba=2, abajo=0))
        R.lamina(m, f'mano_{ld}', T(*(Pg + np.array((0, -0.6, 1.0)))) @ Gx((0, 90, 0)), 3.0, 3.0,
                 gancho_dactylo_adulto('garra_gancho_dactylo_adulto', GARRA_DACTYLO_ADULTO,
                                       [(0.85, 0.15), (0.55, 0.3), (0.3, 0.55), (0.18, 0.92)], (0.2, 0.08)),
                 abajo=True)

    # ------------------------------------------------------------------ las patas
    # Muslo pálido (una cuña, ancha arriba y estrecha abajo, algo echada hacia atrás), caña fina casi negra y el pie
    # en gancho («J»: las garras se curvan hacia delante, como un garfio).
    muslo = liso_dactylo_adulto('muslo_dactylo_adulto', MUSLO_DACTYLO_ADULTO, base=2, arriba=3, abajo=1)
    cana = liso_dactylo_adulto('cana_dactylo_adulto', PATA_DACTYLO_ADULTO, base=1, arriba=2, abajo=0)
    pie = gancho_dactylo_adulto('pie_dactylo_adulto', PATA_DACTYLO_ADULTO,
                                [(0.78, 0.0), (0.78, 0.55), (0.62, 0.86), (0.36, 0.92), (0.16, 0.72), (0.14, 0.5)],
                                (0.2, 0.11))
    for lado, ld in R.LADOS:
        x = lado * 2.95                                            # a los lados de la cadera (asoman, 1m23.54s)
        cad = en_tronco((x, -2.6, -3.6))
        m.parte(f'pata_{ld}', 'cuerpo', tuple(cad))
        m.caja(f'pata_{ld}', (x, cad[1] - 0.5, cad[2] - 0.3), (2.3, 2.0, 3.0), muslo, rot=(18, 0, 0))
        m.caja(f'pata_{ld}', (x, cad[1] - 2.1, cad[2] - 1.0), (1.7, 1.8, 2.0), muslo, rot=(18, 0, 0))
        m.caja(f'pata_{ld}', (x, cad[1] - 4.1, cad[2] - 1.4), (1.2, 3.0, 1.2), cana)
        R.lamina(m, f'pata_{ld}', T(x, cad[1] - 5.4, cad[2] - 0.56) @ Gx((0, 90, 0)), 3.0, 3.0, pie, abajo=True)

    # ------------------------------------------------------------------ la cola
    # Recta, hacia atrás y abajo (25°): la barra azul marino, 2 púas pequeñas al principio, 2 pares de llamas planas y
    # la placa de anillos al final. En dos tramos para que ondule.
    cae = 25.0
    T0 = en_tronco((0.0, 0.3, -7.0))
    m.parte('cola', 'cuerpo', tuple(T0))
    Mt = T(*T0) @ Gx((-cae, 0, 0))
    barra_c = liso_dactylo_adulto('cola_dactylo_adulto', MARINO_DACTYLO_ADULTO, base=1, arriba=2, abajo=0)
    # Las medidas, de la ficha (con la cabeza de 18): barra de 1,8 (0,1 cabezas); llamas de 6 y 4,4 anchos de barra de
    # lado a lado; óvalo de la placa de 8,2 × 11 (0,45 cabezas de ancho, 1,35 veces más largo) y los ganchos hasta 16.
    gb = 1.8
    R.caja_en(m, 'cola', Mt, (0, 0, -3.4), (gb, gb, 7.6), barra_c)
    for z in (-1.2, -3.0):                                         # las 2 pequeñas del principio de la cola
        R.caja_en(m, 'cola', Mt, (0, gb / 2 + 0.6, z), (0.5, 1.4, 0.5), pua)
        R.caja_en(m, 'cola', Mt, (0, gb / 2 + 1.05, z - 0.5), (0.5, 0.5, 0.5), pua)
    R.lamina(m, 'cola', Mt @ T(0, 0, -1.2) @ Gx((-90, 0, 0)), gb + 9.0, 5.8,
             llama_dactylo_adulto('llama1_dactylo_adulto', gb, 4.5, 5.8))
    P1 = (Mt @ np.array((0, 0, -6.8, 1.0)))[:3]
    m.parte('cola2', 'cola', tuple(P1))
    R.caja_en(m, 'cola2', Mt, (0, 0, -10.0), (gb, gb, 6.6), barra_c)
    R.lamina(m, 'cola2', Mt @ T(0, 0, -7.0) @ Gx((-90, 0, 0)), gb + 6.1, 4.6,
             llama_dactylo_adulto('llama2_dactylo_adulto', gb, 3.05, 4.6))
    R.lamina(m, 'cola2', Mt @ T(0, 0.02, -12.6) @ Gx((-90, 0, 0)), 8.2, 16.0,
             placa_dactylo_adulto('placa_dactylo_adulto', 8.2, 11.0, 16.0))

    m.mirar(('cabeza', 0.6), ('cuello', 0.3))
    anims_dactylo_adulto(m)
    return m


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
def anims_dactylo_adulto(m):
    """reposo: planea (las alas se mecen un poco, el cuerpo sube y baja, la cola ondula, las patas cuelgan);
    andar: vuela batiendo (el brazo sube y baja desde el hombro y la mano se dobla por la muñeca, a destiempo);
    ataque: el picotazo (la cabeza se lanza, la boca se abre y se cierra); especial: agarra con las patas (el frenazo
    del icono: morro arriba, alas adelantadas, cola colgando, patas delante; aletazo y aprieta); especial2: el picado;
    estado1: lleva a la presa (patas delante apretando, batiendo fuerte); muerte: pliega las alas y cae de lado;
    aparece: abre las alas."""
    lados = R.LADOS
    # reposo: planeo.
    r = m.anim('reposo', 3.2, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.6, periodo=3.2)
    r.onda('cuerpo', 'r', 0, 1.5, periodo=3.2, fase=0.25)
    for lado, ld in lados:
        r.onda(f'ala_{ld}', 'r', 2, lado * 3.0, periodo=3.2, fase=0.5)
        r.onda(f'mano_{ld}', 'r', 2, lado * 4.0, periodo=3.2, fase=0.62)
        r.onda(f'pata_{ld}', 'r', 0, 4.0, periodo=3.2, fase=0.1 if lado > 0 else 0.35)
    r.onda('cola', 'r', 1, 3.0, periodo=3.2)
    r.onda('cola2', 'r', 1, 5.0, periodo=3.2, fase=0.15)
    r.onda('cuello', 'r', 0, 2.0, periodo=3.2, fase=0.6)
    # andar: vuelo batiendo.
    a = m.anim('andar', 1.0, bucle=True)
    for lado, ld in lados:
        a.onda(f'ala_{ld}', 'r', 2, lado * 32.0, periodo=1.0, base=lado * 4.0)
        a.onda(f'mano_{ld}', 'r', 2, lado * 22.0, periodo=1.0, fase=-0.18, base=-lado * 6.0)
        a.onda(f'pata_{ld}', 'r', 0, 6.0, periodo=1.0, fase=0.3)
    a.onda('cuerpo', 'm', 1, 1.2, periodo=1.0, fase=0.5)
    a.onda('cuerpo', 'r', 0, 2.5, periodo=1.0, fase=0.75)
    a.onda('cola', 'r', 0, 5.0, periodo=1.0, fase=0.6)
    a.onda('cola2', 'r', 0, 7.0, periodo=1.0, fase=0.75)
    a.onda('cuello', 'r', 0, 3.0, periodo=1.0, fase=0.25)
    a.onda('cabeza', 'r', 0, -3.0, periodo=1.0, fase=0.25)
    # ataque: picotazo.
    at = m.anim('ataque', 0.7)
    at.rot('cuello', [(0, 0, 0, 0), (0.22, -14, 0, 0), (0.38, 16, 0, 0), (0.7, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.22, -10, 0, 0), (0.38, 14, 0, 0), (0.7, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.22, 14, 0, 0), (0.36, -12, 0, 0), (0.5, -12, 0, 0), (0.7, 0, 0, 0)])
    at.mov('cuerpo', [(0, 0, 0, 0), (0.22, 0, 0.6, -1.2), (0.38, 0, -0.4, 2.4), (0.7, 0, 0, 0)])
    for lado, ld in lados:
        at.rot(f'ala_{ld}', [(0, 0, 0, 0), (0.22, 0, 0, lado * 18), (0.4, 0, 0, -lado * 10), (0.7, 0, 0, 0)])
        at.rot(f'mano_{ld}', [(0, 0, 0, 0), (0.22, 0, 0, -lado * 10), (0.4, 0, 0, lado * 6), (0.7, 0, 0, 0)])
    # especial: agarra a la presa con las patas. Es la pose del icono: frena con el morro arriba, las alas adelantadas
    # y caídas, la cola colgando y las patas delante; da un aletazo, aprieta los pies y vuelve a planear.
    # Las claves de 0,3 son la pose del icono hecha simétrica (ajuste en SP/quiu_obra/dactylo_adulto/trabajo): el
    # cuerpo 29° morro arriba, las alas 17° caídas y 10° adelantadas, las manos rectas, la cola algo caída.
    e = m.anim('especial', 1.3)
    e.rot('cuerpo', [(0, 0, 0, 0), (0.3, -29, 0, 0), (0.55, -27, 0, 0), (0.8, -22, 0, 0), (1.05, -8, 0, 0),
                     (1.3, 0, 0, 0)])
    e.mov('cuerpo', [(0, 0, 0, 0), (0.3, 0, 1.2, -1.0), (0.8, 0, 0.6, -0.4), (1.3, 0, 0, 0)])
    for lado, ld in lados:
        e.rot(f'pata_{ld}', [(0, 0, 0, 0), (0.3, -20, 0, 0), (0.55, -58, 0, 0), (0.75, -32, 0, 0), (1.0, -26, 0, 0),
                             (1.3, 0, 0, 0)])
        e.rot(f'ala_{ld}', [(0, 0, 0, 0), (0.3, 0, -lado * 10, -lado * 17), (0.55, 0, -lado * 12, lado * 12),
                            (0.8, 0, -lado * 8, -lado * 22), (1.05, 0, -lado * 3, lado * 6), (1.3, 0, 0, 0)])
        e.rot(f'mano_{ld}', [(0, 0, 0, 0), (0.3, 0, 0, 0), (0.55, 0, 0, -lado * 14), (0.8, 0, 0, lado * 4),
                             (1.05, 0, 0, -lado * 4), (1.3, 0, 0, 0)])
    e.rot('cola', [(0, 0, 0, 0), (0.3, -6, 0, 0), (0.8, -8, 0, 0), (1.3, 0, 0, 0)])
    e.rot('cola2', [(0, 0, 0, 0), (0.35, -4, 0, 0), (0.85, -6, 0, 0), (1.3, 0, 0, 0)])
    e.rot('cuello', [(0, 0, 0, 0), (0.3, 13, 0, 0), (0.8, 16, 0, 0), (1.3, 0, 0, 0)])
    e.rot('cabeza', [(0, 0, 0, 0), (0.3, 2, 0, 0), (0.8, 6, 0, 0), (1.3, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.3, 6, 0, 0), (0.6, -6, 0, 0), (1.3, 0, 0, 0)])
    # especial2: el picado (baja a por la presa): las alas medio plegadas hacia atrás y el morro abajo.
    p2 = m.anim('especial2', 1.0)
    p2.rot('cuerpo', [(0, 0, 0, 0), (0.3, 30, 0, 0), (0.7, 34, 0, 0), (1.0, 0, 0, 0)])
    for lado, ld in lados:
        p2.rot(f'ala_{ld}', [(0, 0, 0, 0), (0.3, 0, lado * 32, lado * 10), (0.7, 0, lado * 36, lado * 8),
                             (1.0, 0, 0, 0)])
        p2.rot(f'mano_{ld}', [(0, 0, 0, 0), (0.3, 0, lado * 30, -lado * 12), (0.7, 0, lado * 34, -lado * 14),
                              (1.0, 0, 0, 0)])
        p2.rot(f'pata_{ld}', [(0, 0, 0, 0), (0.3, 30, 0, 0), (0.7, 34, 0, 0), (1.0, 0, 0, 0)])
    p2.rot('cuello', [(0, 0, 0, 0), (0.3, -16, 0, 0), (0.7, -18, 0, 0), (1.0, 0, 0, 0)])
    p2.rot('cola', [(0, 0, 0, 0), (0.3, 18, 0, 0), (0.7, 20, 0, 0), (1.0, 0, 0, 0)])
    # estado1: lleva a la presa (se mantiene): los pies delante, apretando, y bate fuerte con el morro algo arriba.
    c = m.anim('estado1', 0.8, bucle=True)
    c.onda('cuerpo', 'r', 0, 2.0, periodo=0.8, fase=0.75, base=-10.0)
    c.onda('cuerpo', 'm', 1, 1.0, periodo=0.8, fase=0.5)
    for lado, ld in lados:
        c.onda(f'ala_{ld}', 'r', 2, lado * 36.0, periodo=0.8, base=lado * 6.0)
        c.onda(f'mano_{ld}', 'r', 2, lado * 24.0, periodo=0.8, fase=-0.18, base=-lado * 6.0)
        c.onda(f'pata_{ld}', 'r', 0, 3.0, periodo=0.8, fase=0.3, base=-40.0)
    c.onda('cola', 'r', 0, 5.0, periodo=0.8, fase=0.6, base=-8.0)
    c.onda('cola2', 'r', 0, 6.0, periodo=0.8, fase=0.75)
    c.onda('cuello', 'r', 0, 3.0, periodo=0.8, fase=0.25, base=10.0)
    # muerte: deja de batir, pliega las alas, la cabeza cae y se va de lado.
    d = m.anim('muerte', 1.6)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.4, 10, 0, 20), (1.6, 40, 0, 110)])
    d.mov('cuerpo', [(0, 0, 0, 0), (0.4, 0, 1.0, 0), (1.6, 0, -10, 0)])
    for lado, ld in lados:
        d.rot(f'ala_{ld}', [(0, 0, 0, 0), (0.4, 0, lado * 10, lado * 30), (1.6, 0, lado * 20, lado * 70)])
        d.rot(f'mano_{ld}', [(0, 0, 0, 0), (0.6, 0, 0, -lado * 40), (1.6, 0, 0, -lado * 110)])
        d.rot(f'pata_{ld}', [(0, 0, 0, 0), (1.6, 30, 0, lado * 10)])
    d.rot('cuello', [(0, 0, 0, 0), (1.6, 30, 0, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (1.6, 20, 0, 0)])
    d.rot('cola', [(0, 0, 0, 0), (1.6, -18, 0, 0)])
    d.rot('mandibula', [(0, 0, 0, 0), (0.5, 12, 0, 0), (1.6, 6, 0, 0)])
    # aparece: abre las alas desde plegadas.
    ap = m.anim('aparece', 1.0)
    for lado, ld in lados:
        ap.rot(f'ala_{ld}', [(0, 0, 0, lado * 70), (0.6, 0, 0, -lado * 20), (1.0, 0, 0, 0)])
        ap.rot(f'mano_{ld}', [(0, 0, 0, -lado * 120), (0.5, 0, 0, -lado * 30), (1.0, 0, 0, 0)])
    ap.mov('cuerpo', [(0, 0, 4, 0), (0.6, 0, -1, 0), (1.0, 0, 0, 0)])

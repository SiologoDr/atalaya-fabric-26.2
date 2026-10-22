"""
El Reptisaurio Arquero (DEDsafío Minecraft 4, cartel del día 2; el libro del juego: «Atacante a distancia: utiliza su
arco para alejar a los intrusos»), rehecho al pie de la letra de sus imágenes (SP/quiu_ref2/reptisaurio_arquero/ficha.md
y, montado, SP/quiu_ref2/narval_jinete/ficha.md).

Es el reptisaurio verde esmeralda de la familia (el cuerpo de gorila encorvado de reptisaurio() y los brazos en arco con
las manos hacia dentro) que lleva por casco la calavera enorme de una bestia:
  - el cráneo, ancho, encajado en la cabeza de las cejas para arriba, con la cuenca tumbada en cada lado;
  - el hocico, largo, que vuela por delante de la cara, con las dos narices en L al revés en el frente;
  - la losa del techo, más ancha y más clara, con la hilera de plumas turquesa por el medio;
  - los dientes de hueso en bloque, irregulares, colgando de todo el borde de abajo;
  - dos cuernos gris casi negro, anillados, en las esquinas de atrás.
Debajo asoman los ojos amarillos de raya negra, el morro y la boca entreabierta, granate oscuro, con sus cuatro dientes.
Una piel negra le cubre la nuca, los hombros y lo alto de la espalda, con el borde deshilachado y un hueso en L encima de
cada hombro; la cresta sigue por la espalda en una melena de plumas turquesa hasta la cintura. Lleva brazales de cuatro
anillos de hueso crema en los antebrazos, un faldón turquesa delante y, en la mano derecha, el arco largo de hueso gris,
colgando (clip de Cracksterss del 27-09).

Montado en el Narval (estado1; elded, 28-09, 1:22:42-1:22:48): sentado a horcajadas, echado hacia delante y agarrado con
las dos manos a la cabeza del Narval. El arco no se ve.
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import T
from bestiario_fantasmas_v2 import picos_capa
from bestiario_hormigas import _azar1
from bestiario_limpio import rampa
from bestiario_reptiles import (FINO, LADOS, P, anims_reptisaurio, brazo_reptisaurio, caja_en, lamina, reptisaurio,
                                _con_cara, H)

ID = 'reptisaurio_arquero'
TAM = 1.2

# ======================================================================================================================
#  Las rampas (paleta.json de la ficha: lo medido en el cartel, el libro y el juego)
# ======================================================================================================================
PIEL_ARQUERO = rampa('062a12', '0b4a1f', '13702f', '1f9442', '3cbc5e')
HUESO_ARQUERO = rampa('5e5a50', '8e887c', 'b2ac9e', 'd0cabc', 'ece8dc')
HUECO_ARQUERO = rampa('141310', '22201b', '2e2c26', '403e36', '55524a')
CUERNO_ARQUERO = rampa('141412', '24231f', '363430', '4a4842', '62605a')
MANTO_ARQUERO = rampa('08090a', '101213', '191b1d', '24262a', '323539')
CRESTA_ARQUERO = rampa('0a4a44', '0f6a60', '17887b', '27a595', '46c4b4')
FALDON_ARQUERO = rampa('074034', '0b5e4e', '10806c', '18a08a', '3cc2aa')
BRAZAL_ARQUERO = rampa('4a4230', '6a6446', '8e8862', 'b4ae88', 'd2ccaa')
BOCA_ARQUERO = rampa('100001', '1e0204', '320308', '4c080c', '681014')
ARCO_ARQUERO = rampa('2a2b22', '4d4f42', '76796a', 'a0a392', 'c4c6b4')

# El huevo, como los de bestiario_reptiles.EN_JUEGO: la piel verde (claro, medio, oscuro), el contorno turquesa de la
# cresta y sus señas: la calavera arriba con las dos cuencas, la cresta, los ojos amarillos debajo y los brazales.
HUEVO = (('1f9442', '13702f', '0b4a1f'), ('17887b', '0a4c45'),
         [((7, 3), '27a595'), ((8, 3), '46c4b4'),
          ((5, 4), 'd0cabc'), ((6, 4), 'd0cabc'), ((7, 4), 'ece8dc'), ((8, 4), 'd0cabc'), ((9, 4), 'd0cabc'),
          ((10, 4), 'b2ac9e'),
          ((4, 5), 'b2ac9e'), ((5, 5), 'd0cabc'), ((6, 5), '22201b'), ((7, 5), 'd0cabc'), ((8, 5), 'b2ac9e'),
          ((9, 5), '22201b'), ((10, 5), 'b2ac9e'), ((11, 5), '8e887c'),
          ((5, 6), 'b2ac9e'), ((6, 6), 'd0cabc'), ((7, 6), '8e887c'), ((8, 6), 'b2ac9e'), ((9, 6), 'd0cabc'),
          ((10, 6), '8e887c'),
          ((5, 7), '0a0804'), ((6, 7), 'e6d21c'), ((9, 7), 'e6d21c'), ((10, 7), '0a0804'),
          ((3, 10), 'd2ccaa'), ((3, 11), 'b4ae88'), ((12, 10), 'd2ccaa'), ((12, 11), 'b4ae88')])


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def piel_arquero(nombre, R_, base=2.3, luz=0.55, anillos=0, bandas=0, semilla=0):
    """La piel esmeralda, limpia: más clara arriba y más oscura abajo, con manchas grandes de 2 y 3 píxeles en tonos muy
    cercanos (sin píxeles sueltos ni cuadrícula). 'anillos': una banda de 1 px más oscura cada tantas filas a lo largo
    (los brazos y las piernas); 'bandas': las bandas horizontales del pecho y la tripa, en la cara de delante."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), base + luz * 0.7)
        elif c == 'abajo':
            v = np.full((th, tw), base - luz * 1.1)
        else:
            v = base + luz * (0.5 - (ys + 0.5) / th) + (ys == 0) * 0.3
        sx = (ys // 3) % 2
        n1 = _azar1((xs + sx) // 3, ys // 3, s * 3 + 11 + semilla)
        n2 = _azar1((xs + 1) // 2, (ys + 1) // 2, s * 3 + 17 + semilla)
        v = v - (n1 < 0.28) * 0.75 + (n1 > 0.82) * 0.5 - ((n2 < 0.14) & (n1 >= 0.28)) * 0.45
        if anillos and c not in ('arriba', 'abajo'):
            v = v - ((ys % anillos) == anillos - 1) * 0.7
        if bandas and c == 'frente':
            v = v - ((ys % bandas) == bandas - 1) * 0.6
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1))), None
    return B.Pintor(nombre, fn)


def hueso_arquero(nombre, R_, base=2.2, luz=0.6, manchas=0.26, marco=False, semilla=0):
    """Hueso blanco roto, algo gris: la cara de arriba más clara y la de abajo en sombra, el canto de arriba de los lados
    claro y manchas grises suaves de 2 a 3 píxeles; con 'marco', la cara de arriba lleva el recuadro claro de 1 px por el
    borde y el centro un tono más oscuro (la losa)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), base + 0.75)
            if marco:
                borde = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)
                v = np.where(borde, v + 0.25, v - 0.4)
        elif c == 'abajo':
            v = np.full((th, tw), base - 1.0)
        else:
            v = base + luz * (0.45 - (ys + 0.5) / th * 0.9) + (ys == 0) * 0.35
        n1 = _azar1((xs + (ys // 3) % 2) // 3, (ys + 1) // 3, s * 5 + 7 + semilla)
        n2 = _azar1((xs + 2) // 2, ys // 2, s * 5 + 13 + semilla)
        v = v - (n1 < manchas) * 0.85 + (n1 > 0.86) * 0.35 - ((n2 < 0.1) & (n1 >= manchas)) * 0.5
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1))), None
    return B.Pintor(nombre, fn)


def _pon_arquero(tex, mk, R_, v):
    if mk.any():
        tex[mk, :3] = np.round(L.color_continuo(R_, np.full(int(mk.sum()), float(v))))


def craneo_arquero(nombre, R_, RH, base=2.2):
    """El cráneo de la calavera: el hueso y, en cada lado, delante y arriba (justo bajo la losa), la cuenca del ojo, un
    hueco rectangular tumbado gris casi negro con el borde de arriba y el de atrás un tono más claros."""
    hueso = hueso_arquero(nombre + '_h', R_, base=base, semilla=5)

    def fn(tw, th, c, s):
        tex, _ = hueso.fn(tw, th, c, s)
        if c in ('izq', 'der'):
            xs, ys = L._malla(tw, th)
            largo, alto = max(3, int(round(tw * 0.56))), max(2, int(round(th * 0.3)))
            y0 = 1
            if c == 'izq':                                   # el frente, a la derecha de la cara de la izquierda
                x1 = tw - 1
                x0 = x1 - largo
                atras = xs == x0
            else:
                x0 = 1
                x1 = x0 + largo
                atras = xs == x1 - 1
            hueco = (xs >= x0) & (xs < x1) & (ys >= y0) & (ys < y0 + alto)
            _pon_arquero(tex, hueco, RH, 1.0)
            _pon_arquero(tex, hueco & ((ys == y0) | atras), RH, 3.2)
        return tex, None
    return B.Pintor(nombre, fn)


def hocico_arquero(nombre, R_, RH, base=2.3):
    """El hocico de la calavera: el hueso, con más manchas, y en el frente las dos narices, cada una una L al revés: una
    raya de 1 px arriba, del canto de fuera hacia dentro (que dobla la esquina hacia el lado), y el hueco vertical, gris
    casi negro, que baja por el lado de dentro hasta la mitad del frente."""
    hueso = hueso_arquero(nombre + '_h', R_, base=base, manchas=0.3, semilla=3)

    def fn(tw, th, c, s):
        tex, _ = hueso.fn(tw, th, c, s)
        xs, ys = L._malla(tw, th)
        barra = max(1, int(round(th * 0.13)))
        if c == 'frente':
            for x0, x1, h0, h1 in ((0, 0.34, 0.1, 0.34), (0.66, 1.0, 0.66, 0.9)):
                a, b_ = int(round(x0 * tw)), int(round(x1 * tw))
                c0, c1 = int(round(h0 * tw)), int(round(h1 * tw))
                _pon_arquero(tex, (ys < barra) & (xs >= a) & (xs < b_), RH, 2.6)
                _pon_arquero(tex, (ys >= barra) & (ys < int(round(th * 0.7))) & (xs >= c0) & (xs < c1), RH, 1.0)
        elif c in ('izq', 'der'):
            canto = (xs >= tw - 1) if c == 'izq' else (xs <= 0)
            _pon_arquero(tex, (ys < barra) & canto, RH, 2.6)
        return tex, None
    return B.Pintor(nombre, fn)


def dientes_calavera_arquero(nombre, R_, encima=0.12, frente=True, lados=True, semilla=0):
    """Los dientes de hueso de la calavera en una 2.ª capa (una caja algo mayor que el borde de abajo del hueso,
    transparente salvo los dientes), a 32 por bloque: dientes en bloque, rectangulares e irregulares, de 1 a 2 px de
    ancho y de 2 a 3 de largo, con huecos de 1 px, que cuelgan del borde; en el frente, 4 (los de las esquinas, más
    anchos). Claros a un lado, la fila de abajo un tono más oscura. 'encima': la parte de arriba de la capa, la que monta
    sobre el hueso (vacía)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c in ('arriba', 'abajo', 'atras') or (c == 'frente' and not frente) or (c in ('izq', 'der') and not lados):
            return tex, None
        f0 = int(round(th * encima))
        lmax = th - f0
        rng = np.random.default_rng(int(s) * 13 + tw * 5 + th + semilla + (7 if c == 'der' else 0))
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        dientes = []
        if c == 'frente':
            w_e, w_m = max(3, int(round(tw * 0.17))), max(2, int(round(tw * 0.1)))
            for x0, w, fl in ((0, w_e, 1.0), (int(round(tw * 0.33)), w_m, 0.8), (int(round(tw * 0.58)), w_m, 0.7),
                              (tw - w_e, w_e, 1.0)):
                dientes.append((x0, w, max(3, int(round(lmax * fl)))))
        else:
            x = int(rng.integers(1, 4))
            while x < tw - 2:
                w = int(rng.integers(3, 6))
                largo = int(rng.integers(max(3, int(lmax * 0.6)), lmax + 1))
                dientes.append((x, min(w, tw - x), largo))
                x += w + int(rng.integers(2, 6))
        for x0, w, largo in dientes:
            mk = (xs >= x0) & (xs < x0 + w) & (ys >= f0) & (ys < f0 + largo)
            tono = 2.6 + (xs == x0) * 0.5 - (xs == x0 + w - 1) * 0.6 - (ys >= f0 + largo - 2) * 0.6
            v = np.where(mk, tono, v)
            dentro |= mk
        tex = L._rgba(L.color_continuo(R_, np.clip(v, 0, len(R_) - 1)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def dientes_boca_arquero(nombre, R_, encia=2):
    """Los cuatro dientes de la boca (2.ª capa delante de la mandíbula de arriba, a 32 por bloque), como en 1:22:43.98:
    en las comisuras, dos colmillos de 2 px de ancho y unos 2,5 de largo (el de la derecha, con una muesca abajo, como
    un gancho); en medio, dos pequeños de 1 × 1. Claros a la izquierda y en sombra a la derecha, la punta un tono más
    oscura. Las filas de arriba (la encía) quedan vacías: ahí sigue la piel."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara != 'frente':
            return tex, None
        r = ys - encia
        alto = th - encia
        largo_c, largo_m = max(3, int(round(alto * 0.62))), max(2, int(round(alto * 0.26)))
        w_c, w_m = max(3, int(round(tw * 0.17))), 2
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        for x0, w, largo, muesca in ((1, w_c, largo_c, False), (int(round(tw * 0.36)), w_m, largo_m, False),
                                     (int(round(tw * 0.58)), w_m, largo_m, False), (tw - 1 - w_c, w_c, largo_c, True)):
            mk = (xs >= x0) & (xs < x0 + w) & (r >= 0) & (r < largo)
            if muesca:
                mk &= ~((xs == x0) & (r >= largo - 2))
            tono = 3.4 - (xs >= x0 + w - 1) * 0.9 - (r >= largo - 1) * 0.5
            v = np.where(mk, tono, v)
            dentro |= mk
        tex = L._rgba(L.color_continuo(R_, np.clip(v, 0, len(R_) - 1)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def boca_arquero(nombre, R_):
    """La boca por dentro (1:22:43.98): granate muy oscuro y liso, la fila de arriba (bajo el labio) casi negra; sin
    manchas."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), 1.6) - (ys == 0) * 0.9
        if c == 'abajo':
            v = np.full((th, tw), 1.2)
        return L._rgba(L.color_continuo(R_, np.clip(v, 0, len(R_) - 1))), None
    return B.Pintor(nombre, fn)


def cuerno_arquero(nombre, R_, paso=3, base=1.6):
    """Un cuerno gris casi negro, recto y en bloque, con anillos claros de 1 px cada 'paso' a lo largo; la punta (la cara
    de arriba de la viga) más clara y la raíz en sombra."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), base + 1.8)
        elif c == 'abajo':
            v = np.full((th, tw), base - 0.9)
        else:
            v = base + 0.4 * (0.5 - (xs + 0.5) / tw) + ((ys % paso) == 1) * 1.7 - ((ys % paso) == 2) * 0.3
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1))), None
    return B.Pintor(nombre, fn)


def manto_arquero(nombre, R_, base=1.9):
    """La piel negra del manto: mechones verticales de 1 px en dos tonos (cada columna con su tono, cortada de tarde en
    tarde), la cara de arriba un tono más clara; sin brillos."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), base + 0.7)
            xs, ys = ys, xs
        elif c == 'abajo':
            v = np.full((th, tw), base - 1.0)
        else:
            v = base + 0.6 * (0.5 - (ys + 0.5) / th)
        col = _azar1(xs, np.zeros_like(xs), s + 3)
        corte = _azar1(xs, ys // 4, s + 5)
        v = v + (col > 0.62) * 0.7 - (col < 0.25) * 0.55 - (corte < 0.14) * 0.5
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1))), None
    return B.Pintor(nombre, fn)


def pluma_arquero(nombre, R_, RQ, forma=0, base=3.1):
    """Una pluma plana de la cresta o de la melena (lámina, a 32 por bloque): ancha hasta arriba y luego en punta, con el
    borde en escalones de 1 px y la punta con muesca; el cuerpo turquesa vivo, la base y la raya del medio más oscuras
    y 1 px claro en el canto. forma 0: recta; 1: la punta echada a un lado; 2: con dos puntas. Lo de alrededor, vacío."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c != 'frente':
            return tex, None
        h = (th - ys - 0.5) / th                                   # 0 en la base, 1 en la punta
        hq = np.floor(h * th / 2.0) * 2.0 / th                     # en escalones de 2 píxeles finos (1 px)
        cx = tw / 2.0 + (forma == 1) * (tw * 0.24) * hq ** 1.5
        medio = (tw / 2.0) * (1.0 - hq ** 2.6) + 0.6
        x = xs + 0.5
        dentro = np.abs(x - cx) < medio
        if forma == 2:
            dentro &= ~((np.abs(x - cx) < 1.1) & (h > 0.66))       # dos puntas
        else:
            dentro &= ~((np.abs(x - cx) < 0.7) & (h > 0.88))       # la muesca de la punta
        canto = dentro & (np.abs(x - cx) > medio - 1.2)
        raya = dentro & (np.abs(x - cx) < 0.7) & (h < 0.75) & (h > 0.1)
        v = base + 0.8 * h - (h < 0.12) * 1.0 - raya * 0.8
        tex = L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1)))
        claro = canto & (x < cx)
        tex[claro, :3] = np.round(L.color_continuo(R_, np.full(int(claro.sum()), 4.0)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


# Las plumas de la cresta, al píxel (como en el juego: columnas de 1 px de alturas distintas, con escalones): el alto de
# cada columna, de atrás adelante, en partes del alto de la pluma.
PERFILES_PLUMA_ARQUERO = ((0.6, 1.0, 0.8), (1.0, 0.82, 0.55), (0.5, 0.86, 1.0, 0.7), (0.75, 1.0, 0.62))


def pluma_cresta_arquero(nombre, R_, forma=0, base=3.0):
    """Una pluma de la cresta (lámina, al píxel de Minecraft): columnas de 1 px de alturas distintas, en escalones; las
    columnas alternan dos turquesas (claro y algo más oscuro), la fila de abajo y la columna de delante en sombra y la
    punta de cada columna un tono más clara. Lo de alrededor, vacío."""
    perfil = np.array(PERFILES_PLUMA_ARQUERO[forma % len(PERFILES_PLUMA_ARQUERO)])

    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c != 'frente':
            return tex, None
        n = len(perfil)
        col = np.minimum((xs * n) // max(1, tw), n - 1)
        h = (th - ys - 0.5) / th
        alto = perfil[col]
        dentro = h < alto
        punta = dentro & (h > alto - 1.0 / th)
        v = base + 0.5 * ((col % 2) == 0) - 0.8 * (ys == th - 1) + 0.5 * punta - 0.4 * (col == n - 1)
        tex = L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def canon_arquero(nombre, R_):
    """El cañón blanco fino de la cresta (lámina): una raya de hueso de 1 px de ancho, clara arriba."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c != 'frente':
            return tex, None
        dentro = np.abs(xs + 0.5 - tw / 2.0) < max(1.0, tw * 0.3)
        v = 3.4 - (ys / th) * 1.2
        tex = L._rgba(L.color_continuo(R_, np.clip(v, 0, 4)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def brazal_arquero(nombre, R_, grieta=False):
    """Un anillo del brazal de hueso crema: 2 px claros (el de arriba con luz) y el surco oscuro de 1 px; con 'grieta',
    una grieta oscura de 1 px en diagonal en dos caras."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c in ('arriba', 'abajo'):
            v = np.full((th, tw), 2.4 if c == 'arriba' else 1.6)
        else:
            v = 3.0 + 0.5 * (ys == 0) - 1.7 * (ys == th - 1) + 0.3 * (0.5 - (xs + 0.5) / tw)
            if grieta and c in ('frente', 'izq'):
                v = v - (((xs + ys) == tw // 2) & (ys < th - 1)) * 1.6
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1))), None
    return B.Pintor(nombre, fn)


def faldon_arquero(nombre, R_):
    """El faldón turquesa: tela algo más verde y clara que la cresta, con la franja de arriba (la cintura) más clara y
    pliegues verticales suaves."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = 2.3 + 0.5 * (0.5 - (ys + 0.5) / th) - ((xs % 3) == 2) * 0.6 + (ys < 2) * 1.0 - (ys == 2) * 0.4
        if c == 'abajo':
            v = np.full((th, tw), 1.4)
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1))), None
    return B.Pintor(nombre, fn)


def arco_arquero(nombre, R_, atadura=False):
    """La vara del arco: hueso gris verdoso, con bandas oscuras de 1 px cada 3 (como lo enseña el clip de día); con
    'atadura', la empuñadura envuelta en tiras oscuras."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if atadura:
            v = 1.2 + ((ys % 2) == 0) * 0.8
        else:
            v = 2.9 + 0.5 * (xs == 0) - ((ys % 3) == 2) * 1.6
        if c == 'abajo':
            v = v - 0.8
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1))), None
    return B.Pintor(nombre, fn)


def cara_mapa_arquero(k):
    """La cara de delante (a 32 por bloque, del tamaño de la de la familia agrandada k veces): los ojos amarillos arriba,
    justo bajo la ceja y el borde de la calavera, de pie, cada uno con su raya negra en el lado de fuera y separados por
    unos 3 px de verde; debajo, los dos agujeros de la nariz, juntos."""
    W, Hh = int(round(18 * k)), int(round(12 * k))
    g = [['.'] * W for _ in range(Hh)]
    ojo, raya, m0 = int(round(3.4 * k)), max(1, int(round(1.4 * k))), max(1, int(round(1.6 * k)))
    f0, filas = int(round((4.6 - CEJAS_ARQUERO) / 6.0 * Hh)), int(round(4 * k))
    for f in range(f0, min(Hh, f0 + filas)):
        for c in range(m0, m0 + raya):
            g[f][c] = g[f][W - 1 - c] = 'k'
        for c in range(m0 + raya, m0 + raya + ojo):
            g[f][c] = g[f][W - 1 - c] = 'y'
    n0 = W // 2 - 2
    for f in (f0 + filas, f0 + filas + 1):
        if f < Hh:
            g[f][n0] = g[f][W - 1 - n0] = 'n'
    return [''.join(f) for f in g]


# ======================================================================================================================
#  Las piezas
# ======================================================================================================================
def _marco_hacia_arquero(M, pos, sube, cara):
    """El marco de una lámina en 'pos' del marco M que crece hacia 'sube' con la cara mirando hacia 'cara' (vectores del
    marco M; la cara se endereza para que quede en ángulo recto con 'sube')."""
    y = B._u(np.asarray(sube, float))
    z = np.asarray(cara, float)
    z = B._u(z - y * float(np.dot(z, y)))
    x = np.cross(y, z)
    R_ = np.eye(4)
    R_[:3, 0], R_[:3, 1], R_[:3, 2] = x, y, z
    return M @ T(*pos) @ R_


def _plano_arquero(M, pos, sube, gira=0.0, abre=0.0):
    """El marco de una lámina de perfil (en el plano del medio, el YZ) en 'pos' del marco M, que crece hacia 'sube' (un
    vector del plano YZ de M), se abre 'abre' grados hacia un lado (girando alrededor del eje de delante atrás) y luego
    se gira 'gira' grados alrededor de la vertical."""
    a = math.degrees(math.atan2(sube[2], sube[1]))
    return M @ T(*pos) @ B.girar((0, gira, 0)) @ B.girar((0, 0, abre)) @ B.girar((a, 0, 0)) @ B.girar((0, 90, 0))


# Las medidas de la calavera (en píxeles de Minecraft, a tamaño base): el largo y el ancho, del icono con el brazal de
# regla; los altos, de las vistas del juego (de frente, el hocico mide 0,75 de alto por ancho en 42.35 y 46.95; de lado,
# 44.97, el hocico es ~0,8 del alto del cráneo). Ver la bitácora. Cráneo y hocico (ancho, alto, largo), losa (ancho,
# alto) y el largo de los dientes.
CRANEO_ARQUERO = (11.5, 8.8, 9.6)
HOCICO_ARQUERO = (9.2, 7.0, 9.8)
ESCALON_ARQUERO = 1.0          # lo que el hocico queda más bajo que el cráneo por arriba
CEJAS_ARQUERO = 1.6            # la altura (en la cabeza) del borde de abajo del cráneo: justo sobre los ojos
CUELLO_ARQUERO = 16.4          # la altura del cuello en el tronco (1 más que el Salvaje: la boca, justo bajo los dientes)
GRUESO_ARQUERO = 1.2           # brazos y piernas algo más gruesos que el Salvaje (el icono es macizo), como el Guerrero
CABEZA_GIRO_ARQUERO = 8        # la calavera, algo echada hacia abajo (el icono, 44.97 y 47.02: la losa baja ~10° hacia delante)
ANCHO_CAPUCHA_ARQUERO = 20.0   # el ancho de la capucha detrás de la calavera
BAJO_LOSA_ARQUERO = 2.4        # lo que la capucha queda por debajo de lo alto de la losa
ABRE_ARCO_ANDAR_ARQUERO = 12.0         # lo que se abre el arco hacia fuera al andar (grados)
ABRE_ARCO_CORRER_ARQUERO = 22.0        # y al correr
LOSA_ARQUERO = (13.0, 1.3)
DIENTES_ARQUERO = 2.3


def calavera_arquero(m, Mh, y0, cd, canon):
    """La calavera-casco, en la parte 'cabeza' (marco Mh de la cabeza: la cara en z = cd, lo alto de la cabeza en
    y = 4,6): el cráneo encajado de las cejas (y0) para arriba, el hocico delante, la losa encima, los dientes de hueso
    colgando, los dos cuernos y la hilera de plumas de la cresta. Devuelve la altura de lo alto de la losa y la z de la
    cara de atrás del cráneo."""
    craneo = craneo_arquero('craneo_arquero', HUESO_ARQUERO, HUECO_ARQUERO)
    hocico = hocico_arquero('hocico_arquero', HUESO_ARQUERO, HUECO_ARQUERO)
    losa = hueso_arquero('losa_arquero', HUESO_ARQUERO, base=2.25, manchas=0.16, marco=True, semilla=9)
    cuerno = cuerno_arquero('cuerno_arquero', CUERNO_ARQUERO)
    # El cráneo: tapa la cabeza de las cejas para arriba, de 0,3 detrás de la nuca a 0,3 delante de la cara.
    ancho_c, alto_c, largo_c = CRANEO_ARQUERO
    z1_c = cd + 0.3
    z0_c = z1_c - largo_c
    caja_en(m, 'cabeza', Mh, (0, y0 + alto_c / 2, (z0_c + z1_c) / 2), (ancho_c, alto_c, largo_c), craneo)
    # El hocico: más estrecho que el cráneo y más bajo por arriba (el escalón bajo la losa); vuela por delante de la cara.
    ancho_h, alto_h, largo_h = HOCICO_ARQUERO
    y0_h = y0 + alto_c - ESCALON_ARQUERO - alto_h
    y1_h, z1_h = y0_h + alto_h, z1_c + largo_h
    caja_en(m, 'cabeza', Mh, (0, (y0_h + y1_h) / 2, (z1_c + z1_h) / 2), (ancho_h, alto_h, largo_h), hocico)
    # La losa: 1 de ala por lado, de 1 por detrás del cráneo a un tercio del hocico.
    ancho_l, alto_l = LOSA_ARQUERO
    y_losa, z0_l, z1_l = y0 + alto_c, z0_c - 1.0, z1_c + largo_h / 3
    caja_en(m, 'cabeza', Mh, (0, y_losa + alto_l / 2, (z0_l + z1_l) / 2), (ancho_l, alto_l, z1_l - z0_l), losa)
    # Los dientes: una capa en el borde de abajo del hocico (los 4 del frente y los de los lados) y otra en el del
    # cráneo (solo los lados).
    largo = DIENTES_ARQUERO
    caja_en(m, 'cabeza', Mh, (0, y0_h + 0.3 - (largo + 0.3) / 2, (z1_c - 0.2 + z1_h + 0.2) / 2),
            (ancho_h + 0.4, largo + 0.3, largo_h + 0.4),
            dientes_calavera_arquero('dientes_hocico_arquero', HUESO_ARQUERO))
    caja_en(m, 'cabeza', Mh, (0, y0 + 0.3 - (largo + 0.3) / 2, (z0_c - 0.2 + z1_c + 0.2) / 2),
            (ancho_c + 0.4, largo + 0.3, largo_c + 0.4),
            dientes_calavera_arquero('dientes_craneo_arquero', HUESO_ARQUERO, frente=False, semilla=5))
    # Los cuernos: de las esquinas de atrás del cráneo, bajo la losa, hacia arriba, atrás y fuera; la punta, unos 5 px
    # por encima de la losa.
    for lado in (1, -1):
        raiz = np.array((lado * (ancho_c / 2 - 1.6), y0 + alto_c - 1.2, z0_c + 1.6))
        punta = raiz + B._u(np.array((lado * 0.38, 0.62, -0.68))) * 5.6
        m.viga('cabeza', P(Mh, raiz), P(Mh, punta), 4.0, cuerno)
    # La cresta: una hilera de plumas planas por el medio de la losa, en sus dos tercios de atrás; la más alta en medio
    # y las de delante más bajas, echadas hacia atrás y abiertas a un lado y a otro; un cañón blanco entre ellas.
    y_top = y_losa + alto_l
    zs = np.linspace(z0_c + 0.6, z0_c + 0.6 + (z1_l - z0_l) * 0.62, 5)
    for i, (z, alto, ancho) in enumerate(zip(zs, (3.4, 4.8, 5.6, 4.4, 3.0), (2.6, 3.0, 3.4, 3.0, 2.6))):
        M_ = _plano_arquero(Mh, (0, y_top - 0.4, z), (0, 1.0, -0.3), gira=(8 if i % 2 else -8),
                            abre=(11 if i % 2 else -11) * (0.5 if i == 2 else 1.0))
        pint = pluma_cresta_arquero(f'pluma_cresta_arquero_{i}', CRESTA_ARQUERO, forma=i, base=2.9 + 0.2 * (i % 2))
        lamina(m, 'cabeza', M_, ancho, alto, pint)
    for z, alto in ((zs[1] + 1.4, 3.2), (zs[3] + 1.2, 2.6)):
        lamina(m, 'cabeza', _plano_arquero(Mh, (0, y_top - 0.3, z), (0, 1.0, -0.2)), 0.9, alto, canon)
    return y_top, z0_c


def manto_y_melena_arquero(m, Mt, Mh, z0_c, alto_capucha, plumas):
    """La piel negra (la capucha bajo la calavera, en la cabeza; el manto de los hombros, en el tronco) con su borde
    deshilachado, y la melena de púas turquesa que sigue la cresta por la nuca y el lomo hasta la cintura y asoma por
    los costados."""
    manto = manto_arquero('manto_arquero', MANTO_ARQUERO)
    flecos = picos_capa('flecos_arquero', MANTO_ARQUERO, colgando=True, banda=2, largo=6, paso=5, v0=1.6)
    # La capucha: nace bajo la parte de atrás de la calavera y le tapa la nuca; casi tan alta como el cráneo (en el
    # icono sube detrás de la calavera hasta cerca de la losa). De frente (42.35, 46.95) asoma a los dos lados de la
    # calavera como un cuello alto, ~±10 px.
    # Por detrás (46.55, 46.63, 46.75) es un bloque estrecho detrás de la calavera, no más: la espalda se ve verde, con
    # la melena. Así que va en tres piezas: el bloque de en medio, hondo, y dos alas delante, poco hondas, que de frente
    # hacen el cuello ancho.
    abajo = -1.5
    medio = 13.0
    caja_en(m, 'cabeza', Mh, (0, (alto_capucha + abajo) / 2, z0_c - 3.0), (medio, alto_capucha - abajo, 6.4), manto)
    caja_en(m, 'cabeza', Mh, (0, abajo - 1.3, z0_c - 3.0), (medio + 0.4, 2.6, 6.8), flecos)
    ala = (ANCHO_CAPUCHA_ARQUERO - medio) / 2
    for lado in (1, -1):
        x = lado * (medio / 2 + ala / 2)
        caja_en(m, 'cabeza', Mh, (x, (alto_capucha - 1.0 + abajo) / 2, z0_c - 1.2), (ala, alto_capucha - 1.0 - abajo, 2.8),
                manto)
        caja_en(m, 'cabeza', Mh, (x, abajo - 1.3, z0_c - 1.2), (ala + 0.2, 2.6, 3.2), flecos)
    # Por debajo de la mitad de atrás del cráneo, alrededor del cuello (en el icono no se ve cuello: todo es manto).
    caja_en(m, 'cabeza', Mh, (0, CEJAS_ARQUERO - 2.6, z0_c + 2.6), (12.6, 5.2, 5.6), manto)
    # El manto: sobre los dos hombros, por arriba, por fuera y por delante, con el brazo de arriba hasta cerca del codo
    # (el icono, 46.95, 42.35); por detrás no baja por la espalda: desde atrás solo se ve la capucha detrás de la
    # calavera, y la espalda es verde con la melena (46.63, 46.75).
    for lado in (1, -1):
        caja_en(m, 'tronco', Mt, (lado * 8.2, 14.0, 2.2), (6.8, 7.4, 4.0), manto)
        caja_en(m, 'tronco', Mt, (lado * 8.2, 10.3 - 1.3, 2.2), (7.2, 2.6, 4.4), flecos)
    # La melena: una hilera de púas turquesa al píxel (como las de la cresta) por el espinazo, de la nuca a la
    # cintura, que salen de la espalda hacia atrás; y a sus lados, otras dos hileras, alternadas, que se abren hacia
    # fuera (de cara hacia atrás: así llenan la espalda vista por detrás, como en 46.63 y 46.75).
    k = 0
    for i, y in enumerate((16.2, 13.6, 11.0, 8.4, 5.8, 3.2)):
        z = -3.0 if y > 7 else -2.7
        pint = pluma_cresta_arquero(f'pua_melena_arquero_{i % 4}', CRESTA_ARQUERO, forma=i % 4, base=2.9)
        lamina(m, 'tronco', _marco_hacia_arquero(Mt, (0, y, z), (0, 0.3, -1.0), (1, 0, 0)), 3.0,
               5.6 - 0.4 * (i % 2), pint)
        if y < 15:
            for lado in (1, -1):
                pint = pluma_cresta_arquero(f'pua_melena_arquero_{(i + 1) % 4}', CRESTA_ARQUERO, forma=(i + 1) % 4,
                                            base=2.9)
                M_ = _marco_hacia_arquero(Mt, (lado * 2.8, y + 1.3, z + 0.1), (lado * 0.8, 0.15, -1.0),
                                          (lado * 0.35, 0.3, -1.0))
                lamina(m, 'tronco', M_, 3.2, 5.2, pint)
        k += 1
    # Por los costados del tronco, bajo el manto: mechones que cuelgan hacia abajo y atrás, abiertos hacia fuera.
    for lado in (1, -1):
        for y, z in ((10.0, -2.4), (8.4, 0.2), (6.8, -2.0), (5.2, 0.8), (3.8, -1.2)):
            M_ = _marco_hacia_arquero(Mt, (lado * 5.0, y, z), (lado * 0.75, -1.0, -0.15), (lado * 1.0, 0.2, 0.35))
            lamina(m, 'tronco', M_, 3.0, 6.0 + (k % 2) * 1.6, plumas[k % len(plumas)])
            k += 1
    # Por la nuca, sobre la capucha, detrás de la calavera.
    for y in (alto_capucha - 1.0, alto_capucha - 3.6):
        lamina(m, 'cabeza', _plano_arquero(Mh, (0, y, z0_c - 6.0), (0, 0.3, -1.0)), 2.6, 4.6, plumas[k % len(plumas)])
        k += 1


def faja_arquero(m, Mt):
    """La franja turquesa de la cintura, delante, y el faldón que cuelga de ella entre los muslos (con la franja de
    arriba más clara)."""
    faldon = faldon_arquero('faldon_arquero', FALDON_ARQUERO)
    caja_en(m, 'tronco', Mt, (0, 6.2, 3.0), (7.4, 2.0, 0.8), faldon)
    cintura = P(Mt, (0, 5.4, 3.2))
    m.caja('tronco', cintura + np.array((0, -2.9, 0.7)), (4.6, 6.0, 0.8), faldon)


def huesos_l_arquero(m, Mh, z0_c, alto_capucha):
    """Los dos huesos blancos doblados en L, uno a cada lado, en las esquinas de arriba del final de la capucha, detrás
    de la calavera: un tramo corto que sube hasta cerca de la altura de la losa y otro más largo que se echa hacia
    atrás, algo hacia fuera y hacia abajo, acabado en cuña. Es lo que enseñan de lado y por detrás 47.02, 46.55, 46.63 y
    46.75 (una cuña larga arriba y detrás, apuntando hacia atrás y abajo), lo que dice la ficha del jinete y, en el
    icono, el hueso de arriba a la izquierda. De frente (46.95) no se ven: los tapan la calavera y la capucha. (Se
    probaron también sobre los hombros, apuntando hacia fuera como los del Salvaje: de frente salían como dos orejas
    blancas que no están en 46.95, y de lado se veían de punta.) Van en la cabeza, con la capucha."""
    hueso_l = hueso_arquero('hueso_l_arquero', HUESO_ARQUERO, base=2.6, manchas=0.15, semilla=4)
    for lado in (1, -1):
        a = P(Mh, (lado * 6.4, alto_capucha - 1.8, z0_c - 5.0))
        b = P(Mh, (lado * 6.7, alto_capucha + 1.8, z0_c - 5.4))
        c = P(Mh, (lado * 7.8, alto_capucha + 0.0, z0_c - 9.2))
        m.viga('cabeza', a, b, 3.0, hueso_l, extra=1.6)
        m.viga('cabeza', b, c, 2.6, hueso_l, ancho=3.0, extra=1.0)


def brazales_arquero(m, n, codo, mano, lado):
    """El brazal del antebrazo: cuatro anillos de hueso crema, 0,7 px más gruesos que el antebrazo por cada lado (44.02),
    algo desalineados como vértebras apiladas, del codo a un poco antes de la muñeca."""
    eje = B._u(mano - codo)
    lado_v = B._u(np.cross(eje, np.array((0.0, 0.0, 1.0))))
    grueso = 3.2 * GRUESO_ARQUERO + 1.4
    for i in range(4):
        c = codo + eje * (1.8 + i * 2.55) + lado_v * (0.22 if i % 2 else -0.12)
        pint = brazal_arquero(f'brazal_arquero_{"g" if i == 1 else "n"}', BRAZAL_ARQUERO, grieta=(i == 1))
        m.viga(n, c - eje * 1.32, c + eje * 1.32, grueso, pint, rodar=lado * (2.0 if i % 2 else -1.5))


def arco_en_mano_arquero(m, padre, puno):
    """El arco largo de hueso gris, colgando de la mano derecha (clip de Cracksterss: casi toca el suelo): la vara en
    una C escalonada, en el plano de delante atrás (de frente se ve como una vara fina), la cuerda detrás y la
    empuñadura envuelta en el puño."""
    m.parte('arco', padre, tuple(puno))
    vara = arco_arquero('arco_vara_arquero', ARCO_ARQUERO)
    atadura = arco_arquero('arco_atadura_arquero', ARCO_ARQUERO, atadura=True)
    cuerda = B.fino(arco_arquero('arco_cuerda_arquero', ARCO_ARQUERO), FINO)
    # Cuelga de la empuñadura, en diagonal, con la punta de abajo echada hacia fuera (~28°, como en el clip, 0:01.93 a
    # 0:02.43) y casi en el suelo; de frente se ve de canto (una vara fina) y de lado, la C.
    Ma = T(*puno) @ B.girar((-6, 0, -28))
    medio, curva = 14.0, 3.0
    us = (-medio, -medio * 0.66, -medio * 0.33, 0.0, medio * 0.33, medio * 0.66, medio)
    pts = [P(Ma, (0, u, curva * (1 - (u / medio) ** 2) - curva)) for u in us]
    # la vara, con las puntas algo vueltas hacia delante
    for a, b in zip(pts[:-1], pts[1:]):
        m.viga('arco', a, b, 1.4, vara, extra=0.5)
    m.viga('arco', pts[0], P(Ma, (0, -medio - 1.4, 0.8 - curva)), 1.2, vara, extra=0.2)
    m.viga('arco', pts[-1], P(Ma, (0, medio + 1.4, 0.8 - curva)), 1.2, vara, extra=0.2)
    m.viga('arco', P(Ma, (0, -1.6, 0)), P(Ma, (0, 1.6, 0)), 1.9, atadura)
    m.viga('arco', P(Ma, (0, -medio, -curva - 0.1)), P(Ma, (0, medio, -curva - 0.1)), 0.4, cuerda)


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
def _giro_hacia_arquero(desde, hacia):
    """La matriz del giro más corto que lleva la dirección 'desde' a 'hacia'."""
    a, b = B._u(np.asarray(desde, float)), B._u(np.asarray(hacia, float))
    eje = np.cross(a, b)
    s, c = float(np.linalg.norm(eje)), float(np.dot(a, b))
    if s < 1e-9:
        return np.eye(3)
    k = eje / s
    K = np.array(((0, -k[2], k[1]), (k[2], 0, -k[0]), (-k[1], k[0], 0)))
    return np.eye(3) + K * s + K @ K * (1 - c)


def _euler_arquero(R3):
    """Los grados (x, y, z) de una matriz de giro, en el orden de las animaciones (Z·Y·X)."""
    x, y, z = B.euler_zyx(R3)
    return math.degrees(x), math.degrees(y), math.degrees(z)


def _tramos_brazo_arquero(lado):
    """Los dos tramos de reposo del brazo (del hombro al codo y del codo a la muñeca), como los pone
    brazo_reptisaurio con el grueso del Arquero."""
    from bestiario_reptiles import BRAZO_REPTISAURIO
    (cx, cy, cz), (mx, my, mz) = BRAZO_REPTISAURIO
    k = 0.85 + 0.15 * GRUESO_ARQUERO
    return np.array((lado * cx * k, cy * k, cz)), np.array((lado * mx * k, my * k, mz))


def _brazo_hacia_arquero(lado, R_padre, dir_brazo, dir_ante):
    """Los giros (en grados) del brazo y del antebrazo para que el brazo apunte a 'dir_brazo' y el antebrazo a
    'dir_ante' (direcciones del boceto), con el tronco girado R_padre (3 x 3)."""
    d1, d2 = _tramos_brazo_arquero(lado)
    Rb = _giro_hacia_arquero(d1, R_padre.T @ np.asarray(dir_brazo, float))
    Ra = _giro_hacia_arquero(d2, (R_padre @ Rb).T @ np.asarray(dir_ante, float))
    return _euler_arquero(Rb), _euler_arquero(Ra)


def _ik_brazo_arquero(hombro, palma, a, b, polo):
    """Dos huesos: el codo para que, desde el hombro, el brazo (a) y el antebrazo hasta el centro de la palma (b)
    lleguen a 'palma', doblado hacia 'polo'. Devuelve las direcciones del brazo y del antebrazo (si no llega, estirado
    hacia la palma)."""
    v = np.asarray(palma, float) - hombro
    d = float(np.linalg.norm(v))
    u = v / d
    d = min(d, (a + b) * 0.999)
    cos_a = float(np.clip((a * a + d * d - b * b) / (2 * a * d), -1.0, 1.0))
    w = np.asarray(polo, float) - u * float(np.dot(polo, u))
    w = w / np.linalg.norm(w)
    codo = hombro + a * (cos_a * u + math.sqrt(1.0 - cos_a * cos_a) * w)
    return codo - hombro, hombro + u * d - codo


def _pose_arquero(lado, tronco_x, brazo, ante):
    """Los giros (grados) del brazo y del antebrazo de un lado para que apunten a 'brazo' y 'ante' (direcciones del
    boceto, con +X hacia fuera de ese lado), con el tronco girado tronco_x grados; y la matriz de toda la cadena."""
    Rt = B.girar((tronco_x, 0, 0))[:3, :3]
    db, da = (lado * brazo[0], brazo[1], brazo[2]), (lado * ante[0], ante[1], ante[2])
    gb, ga = _brazo_hacia_arquero(lado, Rt, db, da)
    cadena = Rt @ B.girar(gb)[:3, :3] @ B.girar(ga)[:3, :3]
    return gb, ga, cadena


# El disparo (ataque), a tamaño base: el tronco se endereza, la calavera se queda a nivel, el brazo derecho lleva el
# arco al frente, por el lado derecho del hocico, y la mano izquierda tensa la cuerda hasta la mejilla derecha.
# Cada fase: (tiempo, giro del tronco, giro de la cabeza, (brazo, antebrazo) derecho, (brazo, antebrazo) izquierdo),
# las direcciones con +X hacia fuera del lado de cada brazo.
DISPARO_ARQUERO = (
    (0.0, (-12.0, 10.0, ((0.18, -0.18, 0.96), (0.06, -0.08, 0.99)), ((-0.35, -0.35, 0.87), (-0.30, -0.20, 0.93)))),
    (0.18, (-18.0, 15.0, ((0.12, 0.04, 0.99), (0.03, 0.04, 1.0)), ((-0.50, 0.02, 0.86), (-0.55, 0.02, 0.83)))),
    (0.42, (-22.0, 19.0, ((0.14, 0.02, 0.99), (0.02, 0.02, 1.0)), ((-0.28, 0.08, 0.96), (-0.94, -0.04, 0.34)))),
    (0.50, (-22.0, 19.0, ((0.14, 0.02, 0.99), (0.02, 0.02, 1.0)), ((-0.28, 0.08, 0.96), (-0.94, -0.04, 0.34)))),
    (0.58, (-24.0, 17.0, ((0.15, 0.06, 0.99), (0.02, 0.08, 1.0)), ((0.18, 0.20, 0.96), (-0.65, 0.25, -0.15)))),
    (0.88, (-12.0, 10.0, ((0.18, -0.18, 0.96), (0.06, -0.08, 0.99)), ((-0.35, -0.35, 0.87), (-0.30, -0.20, 0.93)))),
)


def anim_alerta_arquero(m):
    """alerta: al detectar a un jugador, mantiene el arco levantado al frente en posición de guardia."""
    al = m.anim('alerta', 2.0, bucle=True)
    tx, cx, (bd, ad), (bi, ai) = DISPARO_ARQUERO[0][1]
    gb_d, ga_d, cadena = _pose_arquero(-1, tx, bd, ad)
    gb_i, ga_i, _ = _pose_arquero(1, tx, bi, ai)
    garco = _euler_arquero(cadena.T)
    _quieta_arquero(al, 'brazo_d', 'r', gb_d)
    _quieta_arquero(al, 'antebrazo_d', 'r', ga_d)
    if 'arco' in m.partes:
        _quieta_arquero(al, 'arco', 'r', garco)
    _quieta_arquero(al, 'brazo_i', 'r', gb_i)
    _quieta_arquero(al, 'antebrazo_i', 'r', ga_i)


def anim_disparo_arquero(m):
    """ataque: dispara con el arco. Se endereza, sube el arco de pie delante con la mano derecha (por el lado del
    hocico, para que no choque con la calavera), lleva la mano izquierda a la cuerda y la tensa hasta la mejilla;
    aguanta, suelta (la mano se va hacia atrás y el tronco da un respingo) y vuelve a su postura de guardia."""
    at = m.anim('ataque', DISPARO_ARQUERO[-1][0])
    canales = {n: [] for n in ('tronco', 'cabeza', 'brazo_d', 'antebrazo_d', 'brazo_i', 'antebrazo_i', 'arco')}
    for t, fase in DISPARO_ARQUERO:
        if fase is None:
            for n in canales:
                canales[n].append((t, 0, 0, 0))
            continue
        tx, cx, (bd, ad), (bi, ai) = fase
        canales['tronco'].append((t, tx, 0, 0))
        canales['cabeza'].append((t, cx, 0, 0))
        gb, ga, cadena = _pose_arquero(-1, tx, bd, ad)
        canales['brazo_d'].append((t, *gb))
        canales['antebrazo_d'].append((t, *ga))
        canales['arco'].append((t, *_euler_arquero(cadena.T)))
        gb, ga, _ = _pose_arquero(1, tx, bi, ai)
        canales['brazo_i'].append((t, *gb))
        canales['antebrazo_i'].append((t, *ga))
    for n, claves in canales.items():
        if n in m.partes:
            at.rot(n, claves)
    at.rot('mandibula', [(0, 0, 0, 0), (0.42, -6, 0, 0), (0.58, 10, 0, 0), (0.88, 0, 0, 0)])


def anim_zarpazo_arquero(m):
    """especial2: el zarpazo de la familia, cuerpo a cuerpo, si se le acercan («para alejar a los intrusos»): levanta
    los dos brazos y los descarga, con el tronco y la cabeza."""
    at = m.anim('especial2', 0.6)
    for lado, ld in LADOS:
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.18, -65, 0, lado * 18), (0.32, -2, 0, -lado * 10), (0.6, 0, 0, 0)])
        at.rot(f'antebrazo_{ld}', [(0, 0, 0, 0), (0.18, -35, 0, 0), (0.32, 8, 0, 0), (0.6, 0, 0, 0)])
    at.rot('tronco', [(0, 0, 0, 0), (0.18, -9, 0, 0), (0.32, 12, 0, 0), (0.6, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.18, -12, 0, 0), (0.32, 10, 0, 0), (0.6, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.2, 16, 0, 0), (0.6, 0, 0, 0)])


def anim_aparece_arquero(m):
    """aparece: se levanta del suelo encogido (las rodillas dobladas y el tronco echado), se yergue, sacude la calavera
    y abre los brazos, y se queda en su postura."""
    a = m.anim('aparece', 1.4)
    a.mov('cuerpo', [(0, 0, -7, 0), (0.45, 0, -2.5, 0), (0.7, 0, 0.6, 0), (0.9, 0, 0, 0), (1.4, 0, 0, 0)])
    a.rot('tronco', [(0, 22, 0, 0), (0.45, 10, 0, 0), (0.7, -8, 0, 0), (0.95, -4, 0, 0), (1.4, 0, 0, 0)])
    a.rot('cabeza', [(0, 18, 0, 0), (0.5, 4, 0, 0), (0.75, -8, 14, 0), (0.92, -8, -14, 0), (1.08, -4, 8, 0),
                     (1.4, 0, 0, 0)])
    a.rot('mandibula', [(0, 0, 0, 0), (0.7, 18, 0, 0), (1.1, 18, 0, 0), (1.4, 0, 0, 0)])
    for lado, ld in LADOS:
        a.rot(f'pierna_{ld}', [(0, -55, 0, 0), (0.45, -25, 0, 0), (0.8, 0, 0, 0), (1.4, 0, 0, 0)])
        a.rot(f'espinilla_{ld}', [(0, 60, 0, 0), (0.45, 28, 0, 0), (0.8, 0, 0, 0), (1.4, 0, 0, 0)])
        a.rot(f'brazo_{ld}', [(0, 20, 0, 0), (0.45, 10, 0, 0), (0.8, -18, 0, lado * 28), (1.1, -18, 0, lado * 28),
                              (1.4, 0, 0, 0)])
        a.rot(f'antebrazo_{ld}', [(0, 10, 0, 0), (0.8, -15, 0, lado * 12), (1.1, -15, 0, lado * 12),
                                  (1.4, 0, 0, 0)])


def _quieta_arquero(a, parte, tipo, xyz):
    """Un canal que se queda quieto en 'xyz' toda la animación."""
    claves = [(0.0, *xyz), (a.largo, *xyz)]
    a.rot(parte, claves) if tipo == 'r' else (a.mov(parte, claves) if tipo == 'm' else a.esc(parte, claves))


# El montado (estado1, el Narval con jinete). El origen del modelo va en el asiento del Narval montado (el centro de la
# tapa de la silla, ASIENTO_NARVAL de quiu_obra/narval.py). Desde ahí, en px del juego, el Narval tiene: la cabeza de
# z 15 a 27, con el techo en y -4,5 y los costados en x ±7; las raíces de los cuernos, de z 22 a 27; el gancho 1, de
# z 6 a 15 y hasta y 8,5; el costado del tramo delantero, en x ±7,5, por debajo de y -1,5.
MONTADO_ARQUERO = {
    'baja': 16.5,             # px (tamaño base): lo que baja el cuerpo; la cara de abajo de los muslos queda en y = 0
    'atras': 2.5,             # px (tamaño base): lo que se sienta hacia atrás en la silla (el pecho, detrás del gancho 1)
    'tronco': -2.0,           # grados: de los 32° de reposo a ~30° de la vertical: echado sobre el Narval
    'calavera': 12.0,         # grados: la calavera, algo hacia abajo, en la línea del Narval
    'cuello': (0.0, -2.5, -2.5),     # px: la cabeza, hundida entre los hombros (agarrado y encogido: en 46.88 los
                                     # dientes de la calavera quedan a ~0,6 calaveras del asiento)
    'palma': (8.9, -4.6, 16.8),      # px del juego: el centro de cada palma, en lo alto del costado de la cabeza del
                                     # Narval, detrás de la raíz de los cuernos (x hacia fuera); los dedos y las garras
                                     # bajan pegados al costado
    'polo_codo': (1.0, 0.5, -0.3),   # hacia dónde sale el codo (fuera, arriba y algo atrás): el brazo en arco
    'muslo': (0.40, -0.06, 0.915),   # dirección del muslo (x hacia fuera): tendido hacia delante y abierto en V
    'espinilla': (0.04, -1.0, -0.10),  # dirección de la espinilla: colgando, pegada al costado del Narval
}


def anims_arquero(m):
    """Las de la familia (reposo, siempre, andar, correr, especial, muerte) y las suyas:
      ataque     dispara con el arco: se endereza, levanta el brazo derecho con el arco de pie delante y tira de la
                 cuerda con la mano izquierda hasta la cara; suelta y vuelve;
      especial2  el zarpazo de la familia, cuerpo a cuerpo;
      estado1    montado en el Narval: sentado a horcajadas en la silla (los muslos hacia delante y abiertos, las
                 espinillas colgando pegadas al costado), echado hacia delante, con la cabeza hundida entre los hombros
                 y la calavera algo hacia abajo, y agarrado con las dos manos a lo alto de los costados de la cabeza del
                 Narval (MONTADO_ARQUERO); el arco no se ve;
      aparece    se levanta del suelo, encogido, sacude la cabeza y abre los brazos;
    y el arco, que en reposo, al andar y en la muerte va en la mano derecha (al andar y al correr, algo más abierto,
    para que la punta no toque el suelo)."""
    anims_reptisaurio(m)
    # El arco, al andar y al correr, se lleva algo más abierto hacia fuera, para que la punta de abajo no toque el
    # suelo cuando la mano baja en el paso.
    if 'arco' in m.partes:
        for nombre, abre in (('reposo', 6.0), ('andar', ABRE_ARCO_ANDAR_ARQUERO)):
            _quieta_arquero(m.anims[nombre], 'arco', 'r', (0, 0, -abre))
    anim_alerta_arquero(m)
    anim_disparo_arquero(m)
    anim_zarpazo_arquero(m)
    anim_aparece_arquero(m)
    # --- montado -------------------------------------------------------------------------------------------------
    M = MONTADO_ARQUERO
    e = m.anim('estado1', 2.0, bucle=True)
    desplaza = np.array((0.0, -M['baja'], -M['atras']))
    # Un vaivén muy leve con el nado (el cuerpo sube y baja un poco); las manos no se sueltan.
    e.mov('cuerpo', [(0.0, *desplaza), (1.0, desplaza[0], desplaza[1] + 0.25, desplaza[2]), (2.0, *desplaza)])
    dt = M['tronco']
    e.rot('tronco', [(0.0, dt, 0, 0), (1.0, dt - 1.0, 0, 0), (2.0, dt, 0, 0)])
    dc = M['calavera'] - CABEZA_GIRO_ARQUERO - dt
    e.rot('cabeza', [(0.0, dc, 0, 0), (1.0, dc + 1.0, 0, 0), (2.0, dc, 0, 0)])
    _quieta_arquero(e, 'cabeza', 'm', M['cuello'])
    Rt = B.girar((dt, 0, 0))[:3, :3]
    piv = np.array((0.0, 19.0, 0.0))                        # el pivote del tronco (y_cadera de reptisaurio())
    Mt0 = T(*piv) @ B.girar((32, 0, 0))                     # el tronco en reposo (encorvado 32°)
    for lado, ld in LADOS:
        # Las piernas: el muslo tendido hacia delante y abierto, la espinilla colgando por el costado.
        d_muslo = np.array((lado * 0.6, 19.0 * 0.56 - 19.0, 4.6))       # de la cadera a la rodilla (reptisaurio())
        d_espinilla = np.array((0.0, 3.0 - 19.0 * 0.56, -5.4))          # de la rodilla al tobillo
        mu, es = np.array(M['muslo']), np.array(M['espinilla'])
        Rp = _giro_hacia_arquero(d_muslo, (lado * mu[0], mu[1], mu[2]))
        Rs = _giro_hacia_arquero(d_espinilla, Rp.T @ np.array((lado * es[0], es[1], es[2])))
        _quieta_arquero(e, f'pierna_{ld}', 'r', _euler_arquero(Rp))
        _quieta_arquero(e, f'espinilla_{ld}', 'r', _euler_arquero(Rs))
        # Los brazos: del hombro (ya echado con el tronco) a la palma sobre la cabeza del Narval.
        hombro = P(Mt0, (lado * 6.2, 13.0, 0.6))
        hombro = piv + Rt @ (hombro - piv) + desplaza
        t1, t2 = _tramos_brazo_arquero(lado)
        a, b = float(np.linalg.norm(t1)), float(np.linalg.norm(t2)) + 1.8
        px, py, pz = M['palma']
        palma = np.array((lado * px, py, pz)) / TAM
        polo = np.array((lado * M['polo_codo'][0], M['polo_codo'][1], M['polo_codo'][2]))
        db, da = _ik_brazo_arquero(hombro, palma, a, b, polo)
        gb, ga = _brazo_hacia_arquero(lado, Rt, db, da)
        _quieta_arquero(e, f'brazo_{ld}', 'r', gb)
        _quieta_arquero(e, f'antebrazo_{ld}', 'r', ga)
    if 'arco' in m.partes:
        _quieta_arquero(e, 'arco', 'e', (0.001, 0.001, 0.001))
    return m


# ======================================================================================================================
#  El modelo
# ======================================================================================================================
def construir():
    """El Reptisaurio Arquero a su tamaño base (TAM lo agranda en el juego)."""
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0
    m.parte('cuerpo', None, (0, 19, 0))
    k = TAM
    piel = piel_arquero('piel_arquero', PIEL_ARQUERO, base=1.95)
    anillos = piel_arquero('anillos_arquero', PIEL_ARQUERO, base=1.95, anillos=5, semilla=3)
    vientre = piel_arquero('vientre_arquero', PIEL_ARQUERO, base=2.05, bandas=3, semilla=5)
    cw, ch, cd = 9, 6, 9.0
    Mt, Mh, hombros, h, garras = reptisaurio(m, piel, anillos, PIEL_ARQUERO, HUESO_ARQUERO, 32, cabeza=(cw, ch, cd),
                                             cuello_y=CUELLO_ARQUERO, cuello_z=2.2, vientre=vientre, abre_boca=22,
                                             cabeza_giro=CABEZA_GIRO_ARQUERO,
                                             grueso=GRUESO_ARQUERO, cara=cara_mapa_arquero(k), k=k, ojos_lado=False)
    # La cara, un tono más oscura que el cuerpo (la tapa la calavera): la piel de la cabeza y de la mandíbula.
    cara_osc = piel_arquero('cara_arquero', PIEL_ARQUERO, base=1.6, luz=0.4, semilla=7)
    colores = {'y': H('e6d21c'), 'k': H('0a0804'), 'n': H('0a0804')}
    cara_p = _con_cara('cara_frente_arquero', cara_osc, {'frente': cara_mapa_arquero(k)}, colores, fino=True)
    cab = m.partes['cabeza'].cajas[0][7]
    for c in B.CARAS:
        cab[c] = cara_p if c == 'frente' else cara_osc
    m.partes['cabeza'].cajas[1][7].update({c: cara_osc for c in B.CARAS})          # la ceja
    # La boca por dentro, casi negra con el borde granate (43.98), y sus cuatro dientes a medida.
    boca = boca_arquero('boca_arquero', BOCA_ARQUERO)
    m.partes['cabeza'].cajas[2][7].update({c: boca for c in B.CARAS})              # el paladar
    m.partes['cabeza'].cajas[3][7].update({c: dientes_boca_arquero('dientes_boca_arquero', HUESO_ARQUERO)
                                           for c in B.CARAS})
    mand = m.partes['mandibula'].cajas[0][7]
    for c in B.CARAS:
        mand[c] = boca if c == 'arriba' else cara_osc
    # Las plumas turquesa (la cresta y la melena), en tres formas.
    plumas = [pluma_arquero(f'pluma_arquero_{i}', CRESTA_ARQUERO, HUESO_ARQUERO, forma=i) for i in range(3)]
    canon = canon_arquero('canon_arquero', HUESO_ARQUERO)
    y_top, z0_c = calavera_arquero(m, Mh, CEJAS_ARQUERO, cd, canon)
    manto_y_melena_arquero(m, Mt, Mh, z0_c, y_top - BAJO_LOSA_ARQUERO, plumas)
    huesos_l_arquero(m, Mh, z0_c, y_top - BAJO_LOSA_ARQUERO)
    faja_arquero(m, Mt)
    # Los brazos de todos los reptisaurios, con los brazales en los antebrazos; el arco, en la mano derecha.
    for lado, ld, hombro in hombros:
        b_, n, codo, mano = brazo_reptisaurio(m, lado, ld, hombro, anillos, piel, garras, grueso=GRUESO_ARQUERO)
        brazales_arquero(m, n, codo, mano, lado)
        if ld == 'd':
            puno = mano + B._u(mano - codo) * 1.8
            arco_en_mano_arquero(m, n, puno)
    m.mirar(('cabeza', 0.8))
    anims_arquero(m)
    return m

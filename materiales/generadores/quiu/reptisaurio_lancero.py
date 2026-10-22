"""
El Reptisaurio con Lanza (reptisaurio_lancero; DEDsafío Minecraft 4, cartel del día 2; el libro del juego: «Combatiente
con lanza», da Veneno Primitivo y vive en los Asentamientos Reptisaurios), rehecho al pie de la letra de sus imágenes
(SP/quiu_ref2/reptisaurio_lancero/ficha.md: el directo de elded del 28-09 a 1080p60, el icono del libro y del cartel 4K
y los clips de la dungeon de Qumara).

Es el reptisaurio dorado: un bípedo con cuerpo de gorila y cabeza de reptil, sin cola.
  - La cabeza, enorme y baja, metida entre las hombreras y sin cuello, es un tótem de bloques apilados: la frente con
    una franja verde por el medio; los ojos amarillo mostaza de ranura negra, cada uno en su caja de esquina que sale
    hacia delante y dobla la esquina; el hocico, que sale por delante de los ojos, con las dos fosas negras; la boca
    poco abierta, granate casi negro, con cuatro dientes cuadrados (dos cortos en medio y dos largos en los extremos);
    y la mandíbula corta y gruesa, con el mentón saliente.
  - La cresta es una fila de hojas lima por la línea del medio del cráneo, que sigue por la nuca y la espalda como una
    crin de hojas más largas, oliva en la raíz y lima en la punta.
  - Dos hombreras de hueso crema con forma de cabeza de fémur, de pie a los lados de la cabeza; dos correas caqui que
    se cruzan en el pecho justo debajo de la barbilla, con una borla azul cielo delante de cada hombro; y un fémur
    largo a la espalda, del hombro izquierdo a la cadera derecha, cuyo nudo de abajo asoma junto al taparrabos.
  - Los brazos, larguísimos (la mano libre le llega al tobillo), en arco suave con las manos hacia dentro, con un
    brazalete de hueso a rayas (crema, gris y crema) en cada muñeca y tres garras gruesas de hueso en gancho.
  - El taparrabos: el cinturón oscuro y dos faldones de hojas, delante y detrás, hasta medio muslo.
  - Las piernas, gruesas y casi rectas, doradas enteras; los pies planos con tres garras finas.
  - En la mano derecha, siempre, la lanza: el asta de madera rojiza, la venda blanca y la punta de hueso en hoja,
    dentada como una espiga.

Se construye ya a su tamaño (TAM = 1): 42 px de la planta a la coronilla (2,6 bloques) y unos 3 con la cresta, como
el resto de la familia (Juan, 20-10-2026: «los Reptisaurios, un poco más grandes»); en el juego del DEDsafío mide 2,2.
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import T
from bestiario_hormigas import _azar1
from bestiario_limpio import rampa
from bestiario_reptiles import FINO, H, P, _con_cara, caja_en, lamina

ID = 'reptisaurio_lancero'
TAM = 1.0

# ======================================================================================================================
#  Las rampas (paleta.json de la ficha, columna «textura», de oscuro a claro)
# ======================================================================================================================
DORADO_LANCERO = rampa('4e3104', '6c4404', '8a5806', 'a46c0a', 'c08614')
CRESTA_LANCERO = rampa('343a08', '4e5806', '687408', '869412', 'a8b42a')
OJO_LANCERO = rampa('8a7c1e', 'a69628', 'c0ae30', 'd4c440', 'e8da5c')
BOCA_LANCERO = rampa('1e0006', '30020a', '440410', '5a0a18', '701422')
HUESO_LANCERO = rampa('6a6458', '8a8474', 'aaa392', 'c8c1ac', 'e2dcc6')
TAPARRABOS_LANCERO = rampa('0a2010', '123420', '1a462a', '245a36', '347a4a')
CORREA_LANCERO = rampa('3c3626', '564e38', '726850', '8e846a', 'aaa086')
BORLA_LANCERO = rampa('244a62', '336a88', '4a8cac', '62aac8', '84c8e0')
PALO_LANCERO = rampa('3a2214', '54321e', '6c4228', '885434', 'a06a46')
NEGRO_LANCERO = H('050403')
BANDA_LANCERO = H('5e5b54')
DIENTE_CENTRO_LANCERO = H('d8d0c2')
DIENTE_EXTREMO_LANCERO = H('a8a298')

HUEVO = (('a46c0a', '8a5806', '4e3104'), ('869412', '343a08'),
         [((5, 6), 'd4c440'), ((6, 6), '050403'), ((9, 6), 'd4c440'), ((10, 6), '050403'),
          ((7, 2), 'a8b42a'), ((8, 3), '869412'), ((6, 9), '440410'), ((9, 9), '440410'),
          ((4, 4), 'e2dcc6'), ((11, 4), 'e2dcc6'), ((7, 11), '4a8cac')])

# ======================================================================================================================
#  Las medidas (en píxeles de Minecraft, ya a su tamaño; Y arriba, el frente en +Z, +X la izquierda del mob)
# ======================================================================================================================
LADOS_LANCERO = ((1, 'i'), (-1, 'd'))
Y_CADERA_LANCERO = 21.0          # las articulaciones de la cadera
ENCORVADO_LANCERO = 12.0         # lo que se echa hacia delante el tronco, de pie (10-15° en 1:18:27.30)
CABEZA_Y_LANCERO = 27.8          # la barbilla (de pie, la cabeza va de 27,8 a 42,3)
CABEZA_Z_LANCERO = 10.6          # el plano de delante del cráneo
CABEZA_GIRO_LANCERO = 0.0
ABRE_BOCA_LANCERO = 10.0         # la boca, poco abierta (10° en reposo)


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def _tono_lancero(tw, th, c, base, luz):
    xs, ys = L._malla(tw, th)
    if c == 'arriba':
        v = np.full((th, tw), base + luz * 0.9)
    elif c == 'abajo':
        v = np.full((th, tw), base - luz * 0.8)
    else:
        v = base + luz * (0.3 - (ys + 0.5) / th * 0.6)
    return xs, ys, v


def piel_lancero(nombre, R_, base=2.0, luz=0.7, bandas=0, semilla=0):
    """La piel dorada al píxel (ficha, §7): un mosaico suave de dos o tres tonos en cuadros de 1-2 px, con algún parche
    de 2 x 3 más oscuro y poco contraste; las caras de arriba, más claras; sin motas sueltas de un píxel. 'bandas': una
    banda muy suave de 1 px cada tantos (los brazos y las piernas)."""
    def fn(tw, th, c, s):
        xs, ys, v = _tono_lancero(tw, th, c, base, luz)
        a = _azar1((xs + (ys // 2) % 2) // 2, ys // 2, s * 7 + semilla)
        v = v + np.where(a < 0.22, -0.55, np.where(a > 0.8, 0.5, 0.0))
        b = _azar1(xs // 2, ys // 3, s * 11 + semilla + 5)
        v = v - (b < 0.08) * 0.6
        if bandas and c not in ('arriba', 'abajo'):
            v = v - ((ys % bandas) == bandas - 1) * 0.35
        idx = np.clip(np.round(v), 0, len(R_) - 1)
        return L._rgba(L.color_continuo(R_, idx)), None
    return B.Pintor(nombre, fn)


def _sobre_piel_lancero(nombre, piel, dibujo, fino=True):
    """Un pintor que pinta la piel (al píxel de siempre) y encima un dibujo: dibujo(tex, xs, ys, tw, th, c) cambia
    'tex' (rgba) donde toque. Con 'fino', el dibujo va a 32 por bloque."""
    def fn(tw, th, c, s):
        if fino:
            t2 = piel.fn(max(1, (tw + 1) // 2), max(1, (th + 1) // 2), c, s)[0]
            tex = np.repeat(np.repeat(t2, 2, 0), 2, 1)[:th, :tw].copy()
        else:
            tex = piel.fn(tw, th, c, s)[0].copy()
        xs, ys = L._malla(tw, th)
        dibujo(tex, xs, ys, tw, th, c)
        return tex, None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO) if fino else p


def _pon(tex, mk, col):
    tex[mk, :3] = np.asarray(col, float)
    tex[mk, 3] = 255


def craneo_lancero(nombre, piel):
    """El cráneo: la piel, con la franja verde de la cresta que baja por el medio de la frente hasta el hocico y corre
    por el medio del techo de delante atrás (dos píxeles: oliva oscuro a la izquierda y oliva claro a la derecha)."""
    oscuro = CRESTA_LANCERO[1] * 0.75 + DORADO_LANCERO[1] * 0.25
    claro = CRESTA_LANCERO[2] * 0.7 + DORADO_LANCERO[2] * 0.3

    def dib(tex, xs, ys, tw, th, c):
        if c in ('frente', 'arriba', 'atras'):
            cx = tw / 2.0
            izq = (xs >= cx - 2) & (xs < cx)
            der = (xs >= cx) & (xs < cx + 2)
            _pon(tex, izq, oscuro)
            _pon(tex, der, claro)
    return _sobre_piel_lancero(nombre, piel, dib, fino=True)


def ojo_caja_lancero(nombre, piel, brow=2):
    """La caja de un ojo (a 32 por bloque): en la cara de delante, la fila de arriba dorada (la ceja) y debajo el ojo
    amarillo mostaza, que llena la caja: tres tercios iguales, amarillo, la ranura negra y amarillo (1:18:26.60), con
    la fila de arriba un tono más clara. En las dos caras de los lados el ojo dobla la esquina (1 px)."""
    claro, medio = OJO_LANCERO[3], OJO_LANCERO[2]

    def ojo(tex, xs, ys, tw, th, c0, c1):
        dentro = (ys >= brow) & (xs >= c0) & (xs < c1)
        arriba = dentro & (ys < brow + 2)
        _pon(tex, dentro, medio)
        _pon(tex, arriba, claro)
        return dentro

    def dib(tex, xs, ys, tw, th, c):
        if c == 'frente':
            ojo(tex, xs, ys, tw, th, 0, tw)
            r = max(2, int(round(tw / 3.0)))
            r0 = (tw - r) // 2
            _pon(tex, (ys >= brow) & (xs >= r0) & (xs < r0 + r), NEGRO_LANCERO)
        elif c in ('izq', 'der'):
            # Las caras de los lados: el frente queda a la derecha en 'izq' y a la izquierda en 'der'.
            c0, c1 = (tw - 2, tw) if c == 'izq' else (0, 2)
            ojo(tex, xs, ys, tw, th, c0, c1)
    return _sobre_piel_lancero(nombre, piel, dib, fino=True)


def hocico_lancero(nombre, piel, separa=2):
    """El hocico: la piel, con las dos fosas negras de 1 x 1 px en la fila de arriba de la cara de delante, separadas
    'separa' px."""
    def dib(tex, xs, ys, tw, th, c):
        if c == 'frente':
            cx = tw / 2.0
            for lado in (-1, 1):
                x0 = cx + lado * separa if lado > 0 else cx - separa - 2
                _pon(tex, (xs >= x0) & (xs < x0 + 2) & (ys >= 1) & (ys < 3), NEGRO_LANCERO)
    return _sobre_piel_lancero(nombre, piel, dib, fino=True)


def boca_lancero(nombre, R_=BOCA_LANCERO, base=1.2):
    """Dentro de la boca: granate casi negro, liso, con el fondo un tono más oscuro."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), base) - (ys >= th - 1) * 0.6 + (ys == 0) * 0.3
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, 4))), None
    return B.Pintor(nombre, fn)


def dientes_lancero(nombre, largo=5, corto=2):
    """Los cuatro dientes de los reptisaurios en una 2.ª capa (a 32 por bloque): cuelgan del borde de arriba en la
    cara de delante; cuadrados, no agujas: los de los extremos, de 1,5 px de ancho y 'largo' filas finas, gris claro;
    los dos del centro, de 1,5 px y 'corto' filas, blancos. Claros a la izquierda y en sombra a la derecha."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c != 'frente':
            return tex, None
        for fx, lk, col in ((0.16, largo, DIENTE_EXTREMO_LANCERO), (0.39, corto, DIENTE_CENTRO_LANCERO),
                            (0.61, corto, DIENTE_CENTRO_LANCERO), (0.84, largo, DIENTE_EXTREMO_LANCERO)):
            x0 = int(round(fx * tw - 1.5))
            mk = (xs >= x0) & (xs < x0 + 3) & (ys < lk)
            sombra = mk & (xs == x0 + 2)
            luz = mk & (xs == x0)
            _pon(tex, mk, col)
            _pon(tex, sombra, np.asarray(col) * 0.82)
            _pon(tex, luz, np.minimum(np.asarray(col) * 1.06, 255))
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def mandibula_lancero(nombre, piel, boca):
    """La mandíbula: la piel por fuera y, encima (el suelo de la boca), el granate de dentro."""
    def fn(tw, th, c, s):
        if c == 'arriba':
            return boca.fn(tw, th, c, s)
        return piel.fn(tw, th, c, s)
    return B.Pintor(nombre, fn)


def hueso_lancero(nombre, R_=HUESO_LANCERO, base=3.0, banda=None, rayas=None, fino=False):
    """Hueso crema (nunca blanco puro), con 1 px de sombra gris en los bordes de las caras de los lados; con 'banda'
    (fracción del alto desde arriba), una banda gris de 1 px de lado a lado; con 'rayas' (una lista de filas: 'c' crema,
    'g' gris), rayas a lo largo (el brazalete, la venda de la lanza)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), base, float)
        if c == 'arriba':
            v = v + 0.6
        elif c == 'abajo':
            v = v - 0.8
        else:
            borde = (xs == 0) | (xs == tw - 1) | (ys == th - 1)
            v = v - borde * 0.8 + (ys == 0) * 0.4
        tex = L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, 4)))
        if c not in ('arriba', 'abajo'):
            if banda is not None:
                f = int(round(banda * th))
                _pon(tex, ys == min(th - 1, f), BANDA_LANCERO)
            if rayas:
                n = len(rayas)
                fila = np.minimum((ys * n) // max(1, th), n - 1)
                for k, r in enumerate(rayas):
                    if r == 'g':
                        _pon(tex, fila == k, BANDA_LANCERO)
        return tex, None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO) if fino else p


def hoja_lancero(nombre, R_=CRESTA_LANCERO, ancho=3, muesca=0.45, lado=1, base=0.8, punta=1.0):
    """Una hoja de la cresta o de la crin, en una lámina, al píxel (ficha: «cada hoja es una lámina fina, nunca una
    caja; oliva en la base y lima en la punta, que acaba en pico»): crece de la raíz (abajo, en medio) a la punta
    (arriba), se estrecha en escalones de un píxel, con una muesca a un lado ('muesca': a qué altura; 'lado': de qué
    lado), y acaba en pico. El canto de la izquierda, un tono más claro. Lo de fuera, vacío."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        t = 1.0 - (ys + 0.5) / th                      # 0 en la raíz, 1 en la punta
        cx = (tw - 1) / 2.0
        w = np.where(t < muesca, ancho, np.where(t < 0.82, ancho - 1, 1))
        izq = np.floor(cx - (w - 1) / 2.0 + 0.01)
        der = izq + w - 1
        # La muesca: por encima de ella la hoja se corre un píxel hacia el lado contrario.
        corre = (t >= muesca) & (t < 0.82)
        izq = izq + corre * (lado > 0)
        der = der + corre * (lado > 0)
        dentro = (xs >= izq) & (xs <= der)
        v = base + 3.0 * t ** punta + (xs == izq) * 0.6 - (xs == der) * 0.3
        tex = L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, 4)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def faldon_lancero(nombre, R_=TAPARRABOS_LANCERO, semilla=0):
    """Un faldón de hojas del taparrabos (lámina, al píxel): verde hoja oscuro con siluetas de hoja de 2-3 px un tono
    más claras, la fila de arriba (bajo el cinturón) más oscura y el borde de abajo dentado, con puntas de hoja de
    1-2 px."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), 1.6)
        hoja = _azar1((xs + (ys // 3) % 2) // 2, ys // 3, semilla + 3) > 0.62
        v = v + hoja * 1.2 + (hoja & ((xs % 2) == 0)) * 0.4
        v = v - (ys == 0) * 0.8
        corte = th - np.where((xs % 3) == 1, 0, np.where((xs % 3) == 0, 1, 2))
        dentro = ys < corte
        tex = L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, 4)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def liso_lancero(nombre, R_, base=2.0, luz=0.6, veta=False):
    """Un material liso (el cinturón, las correas, el asta): el tono base, el canto de arriba más claro y abajo en
    sombra; con 'veta', una veta de 1 px un tono más oscura a lo largo (la madera)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), base + luz)
        elif c == 'abajo':
            v = np.full((th, tw), base - luz)
        else:
            v = base + (xs == 0) * luz * 0.7 - (xs == tw - 1) * luz * 0.5
            if veta:
                v = v - ((_azar1(xs, ys // 4, s + 3) < 0.18) & (tw > 1)) * 0.6
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, 4))), None
    return B.Pintor(nombre, fn)


def borla_lancero(nombre, R_=BORLA_LANCERO):
    """Una borla azul cielo (un lazo de 2 x 2 px): el centro claro, las esquinas en sombra."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), 2.4) + ((xs + ys) % 2 == 0) * 0.6 - (ys == th - 1) * 0.6
        if c == 'arriba':
            v = v + 0.5
        return L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, 4))), None
    return B.Pintor(nombre, fn)


def garra_lancero(nombre, R_=HUESO_LANCERO, gancho=1, ancho=2):
    """Una garra gruesa de hueso en gancho (lámina, a 32 por bloque): baja de la raíz (arriba) con 'ancho' px finos de
    grueso y al final se dobla hacia un lado ('gancho' 1: a la derecha de la lámina; -1: a la izquierda) y acaba en
    punta. Crema, con el canto de abajo en sombra gris."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        cx = tw // 2 - ancho // 2 if gancho > 0 else tw // 2 - ancho // 2
        baja = (xs >= cx) & (xs < cx + ancho) & (ys < th - ancho)
        if gancho > 0:
            pie = (ys >= th - ancho) & (xs >= cx) & (xs < tw - ((ys - (th - ancho)) > 0))
        else:
            pie = (ys >= th - ancho) & (xs < cx + ancho) & (xs >= ((ys - (th - ancho)) > 0) * 1)
        dentro = baja | pie
        v = np.full((th, tw), 3.0) + (xs == cx) * 0.6 - (ys >= th - 1) * 1.2 - (ys < 2) * 0.6
        t2 = L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, 4)))
        tex[dentro] = t2[dentro]
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def punta_lancero(nombre, R_=HUESO_LANCERO, dientes=4):
    """La hoja de hueso de la lanza (lámina, a 32 por bloque): una hoja en punta con 'dientes' dientes a cada lado
    echados hacia la punta, como una espiga o una hoja de helecho (1:18:30.72); crema, con el nervio del medio claro
    y la sombra gris en el canto de abajo de cada diente. La raíz abajo, la punta arriba."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x = xs + 0.5 - tw / 2.0
        t = 1.0 - (ys + 0.5) / th                      # 0 en la raíz, 1 en la punta
        semi = tw / 2.0
        # El perfil: dientes de sierra que se abren hacia atrás desde cada escalón, y la hoja que se afila.
        f = (t * dientes) % 1.0
        ancho = semi * (1.0 - t) ** 0.55 * (0.45 + 0.55 * f)
        dentro = (np.abs(x) <= np.maximum(ancho, 0.6)) & (t < 0.995)
        v = 3.0 + (np.abs(x) < 0.8) * 0.8 - (f < 0.22) * (np.abs(x) > 0.8) * 1.2 + t * 0.4
        tex = L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, 4)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


# ======================================================================================================================
#  Los ayudantes de geometría
# ======================================================================================================================
def _u_lancero(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def marco_lancero(p, largo, ancho):
    """El marco de una lámina en p: su alto (Y) hacia 'largo' y su ancho (X) hacia 'ancho' (vectores del boceto); la
    cara (Z) mira hacia X × Y."""
    y = _u_lancero(largo)
    a = np.asarray(ancho, float)
    x = _u_lancero(a - np.dot(a, y) * y)
    z = np.cross(x, y)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p
    return M


def hoja_en_lancero(m, parte, p, largo_dir, ancho_dir, ancho, alto, pint):
    """Una lámina de 'ancho' x 'alto' que sale de p hacia 'largo_dir' (centrada a lo ancho)."""
    lamina(m, parte, marco_lancero(np.asarray(p, float), largo_dir, ancho_dir), ancho, alto, pint)


def dir_lancero(atras, abre):
    """Una dirección: 'atras' grados echada hacia atrás desde la vertical y luego girada 'abre' grados alrededor de la
    vertical hacia el lado (+X, la izquierda del mob): con 'atras' 90 y 'abre' 90 sale de lado, en horizontal."""
    a, b = math.radians(atras), math.radians(abre)
    return _u_lancero((math.sin(a) * math.sin(b), math.cos(a), -math.sin(a) * math.cos(b)))


# ======================================================================================================================
#  El cuerpo
# ======================================================================================================================
def piernas_lancero(m, piel, piel_pierna, garra_pie):
    """Las piernas, gruesas y casi rectas, doradas enteras: el muslo (5,6 de grueso), la espinilla (4,6) y el pie plano
    (5 x 3 x 8) con tres garras finas delante."""
    for lado, ld in LADOS_LANCERO:
        cad = np.array((lado * 3.6, Y_CADERA_LANCERO, -0.4))
        rod = np.array((lado * 3.8, 11.2, 0.9))
        tob = np.array((lado * 3.8, 3.4, -0.2))
        n = m.parte(f'pierna_{ld}', 'cuerpo', tuple(cad))
        m.viga(n, rod, cad, 5.6, piel_pierna, extra=2.0)
        r_ = m.parte(f'espinilla_{ld}', n, tuple(rod))
        m.viga(r_, tob, rod, 4.6, piel_pierna, extra=1.6)
        m.caja(r_, (lado * 3.8, 1.5, 1.8), (5.0, 3.0, 8.0), piel)
        for k in (-1, 0, 1):
            p = np.array((lado * 3.8 + k * 1.5, 1.6, 5.6))
            hoja_en_lancero(m, r_, p, (0, 0, 1), (0, 1, 0), 3.0, 3.6, garra_pie)


def tronco_lancero(m, piel):
    """El tronco, ancho y de cajas rectas, echado hacia delante: la barriga (12 x 7 x 9), el pecho (14 x 10 x 9,5) y la
    giba de los hombros detrás de la cabeza. Devuelve su marco y los hombros."""
    m.parte('tronco', 'cuerpo', (0, Y_CADERA_LANCERO, -0.4))
    Mt = T(0, Y_CADERA_LANCERO, -0.4) @ B.girar((ENCORVADO_LANCERO, 0, 0))
    caja_en(m, 'tronco', Mt, (0, 3.5, 0.0), (13, 7, 9), piel)
    caja_en(m, 'tronco', Mt, (0, 12.0, 0.3), (15, 10, 10), piel)
    # Los hombros, anchos como los de un gorila (las hombreras quedan a unos 20 px una de otra, 1,5 veces la cabeza:
    # 1:28:03.37), y la giba de detrás de la cabeza, que sube hasta los ojos.
    for lado in (1, -1):
        caja_en(m, 'tronco', Mt, (lado * 8.6, 16.4, 0.0), (5.6, 5.2, 7.4), piel)
    caja_en(m, 'tronco', Mt, (0, 17.6, -1.8), (13, 3.6, 7.0), piel)
    hombros = [(lado, ld, P(Mt, (lado * 9.6, 17.0, 0.3))) for lado, ld in LADOS_LANCERO]
    return Mt, hombros


def cabeza_lancero(m, Mt, piel):
    """La cabeza: un tótem de bloques apilados, de abajo arriba la mandíbula, la boca, el hocico, los ojos en sus cajas
    de esquina y la frente; 13 de ancho y 14,5 de alto. Su marco: el origen en el plano de delante del cráneo, a la
    altura de la barbilla."""
    Mh = T(0, CABEZA_Y_LANCERO, CABEZA_Z_LANCERO) @ B.girar((CABEZA_GIRO_LANCERO, 0, 0))
    m.parte('cabeza', 'tronco', tuple(P(Mh, (0, 5.0, -9.0))))
    craneo = craneo_lancero('craneo_lancero', piel)
    # De abajo arriba (1:18:27.30 y 28.58): la mandíbula 2,2; la boca 2,5; el hocico 3; la mejilla 1; los ojos 2,5;
    # la ceja 1 y la frente 2,5 (14,7 en total).
    # El cráneo (13 x 7 x 11), de la mejilla a la coronilla.
    caja_en(m, 'cabeza', Mh, (0, 11.2, -5.5), (13, 7.0, 11), piel,
            caras={'frente': craneo, 'arriba': craneo, 'atras': craneo})
    # Lo de debajo del cráneo, detrás del hocico (la garganta).
    caja_en(m, 'cabeza', Mh, (0, 5.0, -7.0), (12, 5.0, 8.0), piel)
    # Las cajas de los ojos, en las esquinas: salen 1,2 px hacia delante y 0,6 hacia fuera; su techo hace de ceja.
    for lado, ld in LADOS_LANCERO:
        ojo = ojo_caja_lancero(f'ojo_{ld}_lancero', piel)
        caja_en(m, 'cabeza', Mh, (lado * 4.85, 10.45, -0.05), (4.5, 3.5, 2.5), ojo)
    # El hocico (12 x 3 x 6), que sale 2,4 px por delante de los ojos, con las dos fosas.
    caja_en(m, 'cabeza', Mh, (0, 6.2, 0.6), (12, 3.0, 6.0), hocico_lancero('hocico_lancero', piel))
    # Dentro de la boca (el fondo, 1,2 px por detrás del hocico) y los cuatro dientes, que cuelgan del hocico.
    boca = boca_lancero('boca_lancero')
    caja_en(m, 'cabeza', Mh, (0, 3.45, 0.9), (11, 2.5, 3.0), boca)
    caja_en(m, 'cabeza', Mh, (0, 3.45, 3.15), (11.4, 2.5, 0.6), dientes_lancero('dientes_lancero'))
    # La mandíbula: corta y gruesa, el mentón 0,3 px por delante del hocico; poco abierta en reposo (sus cajas, ya
    # giradas: el borde de delante queda a 2,2 de alto y el de abajo, en la barbilla).
    gozne = P(Mh, (0, 4.37, -8.0))
    m.parte('mandibula', 'cabeza', tuple(gozne))
    Mj = T(*gozne) @ B.girar((CABEZA_GIRO_LANCERO + ABRE_BOCA_LANCERO, 0, 0))
    suelo = boca_lancero('suelo_boca_lancero', base=0.7)
    caja_en(m, 'mandibula', Mj, (0, -1.115, 6.24), (12, 2.23, 12.48), mandibula_lancero('mandibula_lancero', piel,
                                                                                        suelo))
    return Mh


def cresta_lancero(m, Mh, Mt):
    """La cresta: una fila de hojas por la línea del medio del cráneo, de la frente a la nuca (la del medio, la más
    alta), echadas hacia atrás; y la crin, que sigue por la nuca y la espalda hasta media espalda con unas diez hojas
    más largas que salen hacia atrás y algo hacia los lados."""
    hojas = [hoja_lancero(f'hoja_lancero_{k}', ancho=a, muesca=mu, lado=ld, base=b)
             for k, (a, mu, ld, b) in enumerate(((2, 0.4, 1, 0.6), (3, 0.5, -1, 0.9), (2, 0.55, -1, 1.1),
                                                 (3, 0.35, 1, 0.5)))]
    techo = 14.7
    # (z en el techo, x, alto, echada atrás, giro, hoja)
    for k, (z, x, alto, atras, giro) in enumerate(((-0.8, -0.5, 3.4, 18, -24), (-2.4, 0.4, 6.8, 14, 20),
                                                    (-4.0, -0.3, 5.6, 22, -14), (-5.8, 0.5, 5.0, 28, 18),
                                                    (-7.6, -0.4, 4.6, 34, -20), (-9.4, 0.3, 4.2, 42, 16))):
        p = P(Mh, (x, techo - 0.2, z))
        g = math.radians(giro)
        hoja_en_lancero(m, 'cabeza', p, dir_lancero(atras, 0), (math.sin(g), 0, math.cos(g)),
                        2.6 if k % 2 else 2.0, alto, hojas[k % len(hojas)])
    # La crin: por la nuca y la espalda, hacia atrás y abiertas a los lados. Cada hoja, de canto hacia arriba: su cara
    # mira a los lados (las que van hacia atrás) o hacia atrás (las que se abren a los lados), como en 1:17:25.27.
    for k, (y, x, alto, atras, abre) in enumerate(((19.4, 0.0, 8.0, 40, 0), (18.8, 1.0, 8.5, 55, 50),
                                                    (18.8, -1.0, 8.5, 55, -50), (16.8, 1.5, 8.0, 75, 78),
                                                    (16.8, -1.5, 8.0, 75, -78), (15.8, 0.5, 9.0, 70, 15),
                                                    (14.2, 2.0, 8.0, 85, 62), (14.2, -2.0, 8.0, 85, -62),
                                                    (12.6, -0.5, 8.0, 80, -15), (11.0, 2.0, 7.0, 95, 72),
                                                    (11.0, -2.0, 7.0, 95, -72), (10.0, 0.0, 6.0, 90, 0))):
        p = P(Mt, (x, y, -5.0))
        d = dir_lancero(atras, abre)
        arriba = np.array((0.0, 1.0, 0.0)) - d[1] * d
        if np.linalg.norm(arriba) < 0.2:
            arriba = np.array((0.0, 0.0, 1.0))
        hoja_en_lancero(m, 'tronco', p, d, arriba, 3.0, alto, hojas[(k + 1) % len(hojas)])


def equipo_lancero(m, Mt):
    """Las correas en X, las borlas azules, el fémur de la espalda y el taparrabos."""
    correa = liso_lancero('correa_lancero', CORREA_LANCERO, base=2.0, luz=0.6)
    # Las correas por delante: de cada hombro (por fuera, junto a la hombrera) a la cadera del otro lado, cruzándose
    # justo debajo de la barbilla; en dos tramos, el del pecho y el de la barriga.
    for lado in (1, -1):
        a = np.array((lado * 6.8, 17.6, 5.45))
        b = np.array((-lado * 2.6, 3.0, 4.65))
        t7 = (17.6 - 7.0) / (17.6 - 3.0)
        mid = a + (b - a) * t7
        m.viga('tronco', P(Mt, (mid[0], 7.0, 5.45)), P(Mt, a), 0.5, correa, ancho=1.5, extra=0.6)
        m.viga('tronco', P(Mt, b), P(Mt, (mid[0], 7.0, 4.65)), 0.5, correa, ancho=1.5, extra=0.6)
        # Por encima del hombro y por la espalda (sujetan el fémur).
        m.viga('tronco', P(Mt, (lado * 6.8, 19.25, -3.9)), P(Mt, (lado * 6.8, 19.25, 3.9)), 0.5, correa, ancho=1.5)
        m.viga('tronco', P(Mt, (lado * 6.8, 17.6, 5.45)), P(Mt, (lado * 6.8, 19.25, 3.9)), 0.5, correa, ancho=1.5,
               extra=0.5)
        m.viga('tronco', P(Mt, (-lado * 2.6, 3.0, -4.65)), P(Mt, (lado * 6.8, 17.6, -5.45)), 0.5, correa, ancho=1.5,
               extra=0.6)
    # Las borlas azul cielo, sobre cada correa delante del hombro.
    borla = borla_lancero('borla_lancero')
    for lado in (1, -1):
        caja_en(m, 'tronco', Mt, (lado * 5.0, 14.8, 5.75), (2.4, 2.4, 1.2), borla)
    # El fémur de la espalda, del hombro izquierdo a la cadera derecha; el nudo de abajo asoma junto al taparrabos.
    hueso = hueso_lancero('hueso_espalda_lancero', base=3.0)
    nudo = hueso_lancero('nudo_lancero', base=3.0)
    arriba = np.array((6.5, 21.5, -5.8))
    abajo = np.array((-7.0, 2.6, -3.4))
    m.viga('tronco', P(Mt, abajo), P(Mt, arriba), 3.4, hueso)
    for p, k in ((arriba, 1), (abajo, -1)):
        eje = _u_lancero(arriba - abajo)
        q = p + eje * k * 0.6
        Mn = T(*P(Mt, q)) @ B.girar((ENCORVADO_LANCERO, 0, 0))
        caja_en(m, 'tronco', Mn, (0, 0, 0), (5.0, 3.4, 4.2), nudo)
    # Los hilos azules que cuelgan del fémur.
    hilo = liso_lancero('hilo_lancero', BORLA_LANCERO, base=2.5, luz=0.5)
    for t, dx in ((0.62, 0.0), (0.7, 1.0)):
        p = abajo + (arriba - abajo) * t + np.array((dx, 0, -1.9))
        hoja_en_lancero(m, 'tronco', P(Mt, p), (0, -1, 0), (1, 0, 0), 0.8, 3.5, hilo)
    # El cinturón oscuro y los dos faldones de hojas (delante y detrás), hasta medio muslo.
    cinto = liso_lancero('cinto_lancero', TAPARRABOS_LANCERO, base=0.8, luz=0.5)
    caja_en(m, 'tronco', Mt, (0, 1.4, 0.0), (12.6, 1.8, 9.6), cinto)
    for z, nombre in ((5.0, 'del'), (-5.0, 'tras')):
        n = m.parte(f'faldon_{nombre}', 'tronco', tuple(P(Mt, (0, 0.8, z))))
        Mf = T(*P(Mt, (0, 1.0, z))) @ B.girar((ENCORVADO_LANCERO * 0.3, 0 if z > 0 else 180, 0))
        lamina(m, n, Mf, 8.0, 8.0, faldon_lancero(f'faldon_{nombre}_lancero', semilla=7 if z > 0 else 11),
               abajo=True)


def hombrera_lancero(m, parte, hombro, lado, hueso_b, hueso):
    """Una hombrera de hueso crema con forma de cabeza de fémur, de pie sobre el hombro y un poco hacia fuera: el nudo
    de abajo (5 x 3,6 x 5) con su banda gris y otro más pequeño encima."""
    base = hombro + np.array((lado * 0.4, 2.0, -0.4))
    Mh = T(*base) @ B.girar((0, 0, -lado * 8))
    caja_en(m, parte, Mh, (0, 1.8, 0), (5.0, 3.6, 5.0), hueso_b)
    caja_en(m, parte, Mh, (lado * 0.2, 4.4, 0), (3.8, 1.8, 3.8), hueso)


def brazo_lancero(m, lado, ld, hombro, codo_d, mano_d, piel_brazo, piel, brazalete, garra):
    """Un brazo larguísimo y grueso: el brazo hasta el codo, el antebrazo hasta la muñeca, el brazalete de hueso a
    rayas en la muñeca, el puño dorado y tres garras gruesas de hueso en gancho, hacia abajo y hacia dentro."""
    n = m.parte(f'brazo_{ld}', 'tronco', tuple(hombro))
    codo = hombro + np.asarray(codo_d, float)
    muneca = codo + np.asarray(mano_d, float)
    m.viga(n, codo, hombro, 5.2, piel_brazo, extra=2.6)
    a = m.parte(f'antebrazo_{ld}', n, tuple(codo))
    m.viga(a, muneca, codo, 4.8, piel_brazo, extra=1.0)
    eje = _u_lancero(muneca - codo)
    m.viga(a, muneca + eje * 0.2, muneca - eje * 3.0, 5.6, brazalete)
    puno = muneca + eje * 2.4
    m.viga(a, muneca + eje * 4.6, muneca + eje * 0.2, 5.0, piel, ancho=5.0)
    # Las garras: salen de debajo del puño, por delante y del lado de dentro; cada una, dos láminas cruzadas.
    for k in (-1, 0, 1):
        raiz = muneca + eje * 4.4 + np.array((-lado * 1.2, 0, k * 1.5 + 0.6))
        hoja_en_lancero(m, a, raiz, -eje, (0, 0, 1), 2.4, 4.6, garra[0])
        hoja_en_lancero(m, a, raiz, -eje, (-lado, 0, 0), 2.4, 4.6, garra[1])
    return n, a, codo, muneca, puno


def lanza_lancero(m, padre, puno, eje_lanza, atras=3.0, largo=19.0):
    """La lanza en el puño, cogida cerca del extremo de atrás: el asta recta de madera rojiza (1,5 de grueso), la
    venda clara de dos vueltas en la base de la punta y la punta de hueso en hoja, dentada como una espiga (dos
    láminas cruzadas)."""
    eje = _u_lancero(eje_lanza)
    n = m.parte('lanza', padre, tuple(puno))
    culo = puno - eje * atras
    boca = culo + eje * largo
    m.viga(n, culo, boca, 1.5, liso_lancero('asta_lancero', PALO_LANCERO, base=2.0, luz=0.7, veta=True))
    venda = hueso_lancero('venda_lancero', base=3.2, rayas='cgcgc', fino=True)
    m.viga(n, boca - eje * 0.6, boca + eje * 3.0, 2.8, venda)
    punta = punta_lancero('punta_lancero')
    raiz = boca + eje * 2.8
    ref = np.array((0, 1.0, 0)) if abs(eje[1]) < 0.9 else np.array((1.0, 0, 0))
    lado_a = _u_lancero(np.cross(eje, ref))
    lado_b = _u_lancero(np.cross(eje, lado_a))
    hoja_en_lancero(m, n, raiz, eje, lado_a, 4.6, 9.0, punta)
    hoja_en_lancero(m, n, raiz, eje, lado_b, 4.6, 9.0, punta)
    return n


# ======================================================================================================================
#  El modelo
# ======================================================================================================================
def construir():
    """El Reptisaurio con Lanza a su tamaño (TAM = 1)."""
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0
    m.parte('cuerpo', None, (0, Y_CADERA_LANCERO, 0))
    piel = piel_lancero('piel_lancero', DORADO_LANCERO, base=2.0, luz=0.7)
    piel_miembro = piel_lancero('piel_miembro_lancero', DORADO_LANCERO, base=2.0, luz=0.7, bandas=4, semilla=3)
    garra_pie = garra_lancero('garra_pie_lancero', gancho=1, ancho=2)
    piernas_lancero(m, piel, piel_miembro, garra_pie)
    Mt, hombros = tronco_lancero(m, piel)
    Mh = cabeza_lancero(m, Mt, piel)
    cresta_lancero(m, Mh, Mt)
    equipo_lancero(m, Mt)
    hueso = hueso_lancero('hombrera_lancero', base=3.0)
    hueso_b = hueso_lancero('hombrera_banda_lancero', base=3.0, banda=0.7)
    brazalete = hueso_lancero('brazalete_lancero', base=3.0, rayas='ccggcc', fino=True)
    garras = (garra_lancero('garra_mano_lancero', gancho=1, ancho=3), garra_lancero('garra_mano_b_lancero', gancho=-1,
                                                                                    ancho=3))
    for lado, ld, hombro in hombros:
        if lado > 0:
            # El brazo libre (el izquierdo): cuelga en arco suave, el codo 1,8 px hacia fuera, y la mano le llega al
            # tobillo.
            n, a, codo, muneca, puno = brazo_lancero(m, lado, ld, hombro, (2.0, -14.0, 0.6), (-1.5, -13.6, 0.8),
                                                     piel_miembro, piel, brazalete, garras)
        else:
            # El de la lanza (el derecho), en guardia como en 1:18:27.30 y 28.58: hacia fuera, hacia abajo y algo
            # hacia delante, con la lanza tendida hacia fuera, hacia arriba y hacia delante.
            d1 = _u_lancero((-0.62, -0.74, 0.26)) * 13.6
            d2 = _u_lancero((-0.45, -0.62, 0.64)) * 12.6
            n, a, codo, muneca, puno = brazo_lancero(m, lado, ld, hombro, d1, d2, piel_miembro, piel, brazalete,
                                                     garras)
            lanza_lancero(m, a, puno, (-0.62, 0.42, 0.66))
        hombrera_lancero(m, n, hombro, lado, hueso_b, hueso)
    m.mirar(('cabeza', 0.8))
    anims_lancero(m)
    return m


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
def anims_lancero(m):
    """reposo: respira y mira; siempre: la boca y las hojas; andar y correr: las piernas con la rodilla que se dobla,
    el brazo libre que se balancea colgando, el tronco y la cabeza; ataque: alza la lanza por encima de la cabeza y la
    clava de arriba abajo; especial: el zarpazo con la mano libre; especial2: la arremetida con la lanza en ristre;
    muerte: se desploma; aparece: se levanta encogido."""
    r = m.anim('reposo', 4.0, bucle=True)
    r.onda('tronco', 'r', 0, 1.5, periodo=4.0)
    r.rot('cabeza', [(0, 0, 0, 0), (0.8, 0, 12, 0), (1.6, 2, 12, 0), (2.0, 0, 0, 0), (2.8, 0, -12, 0),
                     (3.6, 2, -12, 0), (4.0, 0, 0, 0)])
    r.onda('brazo_i', 'r', 2, 2.5, periodo=4.0)
    r.onda('antebrazo_i', 'r', 0, 3.0, periodo=4.0, fase=0.25)
    r.onda('brazo_d', 'r', 0, 2.0, periodo=4.0, fase=0.5)
    s_ = m.anim('siempre', 2.5, bucle=True)
    s_.onda('mandibula', 'r', 0, 2.5, periodo=2.5)
    for nombre, largo, amp, inclina in (('andar', 1.3, 1.0, 0.0), ('correr', 0.75, 1.4, 14.0)):
        a = m.anim(nombre, largo, bucle=True)
        for k, (lado, ld) in enumerate(LADOS_LANCERO):
            f = 0.5 * k
            a.onda(f'pierna_{ld}', 'r', 0, 22 * amp, periodo=largo, fase=f)
            a.onda(f'espinilla_{ld}', 'r', 0, 24 * amp, periodo=largo, fase=f - 0.25, forma=lambda v: max(0.0, v))
        a.onda('brazo_i', 'r', 0, 18 * amp, periodo=largo, fase=0.0)
        a.onda('antebrazo_i', 'r', 0, 10 * amp, periodo=largo, fase=0.25, base=-6 * amp)
        a.onda('brazo_d', 'r', 0, 6 * amp, periodo=largo, fase=0.5, base=inclina * 0.5)
        a.onda('faldon_del', 'r', 0, 8 * amp, periodo=largo / 2, fase=0.25, base=-4 * amp)
        a.onda('faldon_tras', 'r', 0, 6 * amp, periodo=largo / 2, fase=0.75, base=4 * amp)
        a.onda('tronco', 'r', 2, 3.0 * amp, periodo=largo)
        a.onda('tronco', 'r', 1, 4.0 * amp, periodo=largo, fase=0.25)
        a.onda('tronco', 'r', 0, 1.5 * amp, periodo=largo / 2, base=inclina)
        a.onda('tronco', 'm', 1, 0.45 * amp, periodo=largo / 2)
        a.onda('cabeza', 'r', 0, 3.0 * amp, periodo=largo / 2, fase=0.25, base=-inclina * 0.6)
    at = m.anim('ataque', 0.9)
    at.rot('brazo_d', [(0, 0, 0, 0), (0.3, -150, 10, 25), (0.42, -150, 10, 25), (0.58, -30, 0, 0), (0.9, 0, 0, 0)])
    at.rot('antebrazo_d', [(0, 0, 0, 0), (0.3, -30, 0, 0), (0.42, -30, 0, 0), (0.58, 10, 0, 0), (0.9, 0, 0, 0)])
    at.rot('tronco', [(0, 0, 0, 0), (0.3, -10, 8, 0), (0.42, -10, 8, 0), (0.58, 16, -6, 0), (0.9, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.3, -10, 0, 0), (0.58, 8, 0, 0), (0.9, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.3, 14, 0, 0), (0.58, 4, 0, 0), (0.9, 0, 0, 0)])
    e = m.anim('especial', 0.7)
    e.rot('brazo_i', [(0, 0, 0, 0), (0.25, -110, 0, 20), (0.4, -20, 0, -10), (0.7, 0, 0, 0)])
    e.rot('antebrazo_i', [(0, 0, 0, 0), (0.25, -30, 0, 0), (0.4, 10, 0, 0), (0.7, 0, 0, 0)])
    e.rot('tronco', [(0, 0, 0, 0), (0.25, -6, -12, 0), (0.4, 10, 10, 0), (0.7, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.25, 18, 0, 0), (0.7, 0, 0, 0)])
    e2 = m.anim('especial2', 1.0)
    e2.rot('tronco', [(0, 0, 0, 0), (0.3, 24, 0, 0), (0.75, 24, 0, 0), (1.0, 0, 0, 0)])
    e2.rot('brazo_d', [(0, 0, 0, 0), (0.3, -40, -20, 0), (0.5, -60, -20, 0), (0.75, -40, -20, 0), (1.0, 0, 0, 0)])
    e2.mov('cuerpo', [(0, 0, 0, 0), (0.3, 0, -1, 0), (0.5, 0, -1, 4), (0.75, 0, -1, 2), (1.0, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, 6, 0, 0), (1.0, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -10, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.4, -15, 0, 0), (1.0, 10, 0, 0)])
    ap = m.anim('aparece', 1.2)
    ap.mov('cuerpo', [(0, 0, -8, 0), (0.6, 0, -2, 0), (1.2, 0, 0, 0)])
    ap.rot('tronco', [(0, 30, 0, 0), (0.6, 20, 0, 0), (1.2, 0, 0, 0)])
    ap.rot('cabeza', [(0, 20, 0, 0), (0.8, -12, 0, 0), (1.2, 0, 0, 0)])

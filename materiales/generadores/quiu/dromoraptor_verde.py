"""
El Dromoraptor Verde (DEDsafío 4, Centro de Quiu; desde el día 7 también en los cerezos): el raptor verde de la manada,
con abanicos de membrana magenta en el lomo, una aleta grande colgando de cada brazo, el bloque amarillo translúcido
sobre el hocico y dos crestas verdes detrás. Copia fiel de sus imágenes del juego (los iconos del libro y los directos
de Samulx y elded; ficha en SP/quiu_ref2/dromoraptor_verde/).

El cuerpo es el de los raptores que Juan ya aprobó (bestiario_reptiles.dromoraptor(), el del Rojo y el Azul) y no se
toca su forma: este módulo lo construye tal cual y luego le cambia lo que distingue al Verde:
  la piel      verde vivo tirando a azulado (2a8526) con manchas verdes y oliva y motas claras; la mitad de abajo del
               tronco, el gaznate, la mandíbula y el bajo de los muslos, oliva pardo, con el paso manchado
  las patas    de la rodilla abajo casi negras con rayas claras de 1 px; los antebrazos, gris casi negro; las garras,
               negras con el canto gris
  la cara      el ojo amarillo de 4 x 2 con la pupila negra (amarillo, negro, amarillo, amarillo, de atrás adelante), sin
               ceja; la mancha oliva del ojo hacia delante y la nariz; los dientes blanco crema de 1 px separados 1 px, el
               paladar y la encía rojos
  el bloque    una caja amarilla translúcida (como la capa del slime) sobre la mitad de delante de la cabeza
  las crestas  dos palos planos de 2 px, verdes, algo echados atrás y con la punta en banderita
  los abanicos tres en la línea del medio (el de la cola, el pequeño de la cadera y el de los hombros): radios verdes de
               1 px en escalera y la membrana morada en la raíz y magenta hacia el borde, que llena entre los radios
               hasta un borde en escalera; los de la cola, echados hacia atrás, y el de los hombros, derecho
  las aletas   la de cada brazo, la más grande: cuelga del antebrazo, con seis radios casi paralelos que asoman por
               abajo en picos
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
import bestiario_reptiles as R
from bestiario import T
from bestiario_hormigas import _azar1

ID = 'dromoraptor_verde'
TAM = 1.28

HUEVO = (
    ('74b42e', '386a16', '14280a'),
    ('d23cae', '5c0a4c'),
    [
        ((9, 6), 'f0d020'), ((10, 6), '120a06'),
        ((5, 4), 'ae1c8c'), ((6, 3), 'd23cae'), ((7, 4), 'ae1c8c'),
        ((10, 3), 'c8c418'), ((11, 3), 'f0e040'),
    ],
)

# ======================================================================================================================
#  Los colores (paleta.json de la ficha: los de textura, de oscuro a claro)
# ======================================================================================================================
PIEL_DROMORAPTOR_VERDE = B.rampa('1c4a14', '25661c', '2a8526', '3a9a32', '52ad44')
OLIVA_DROMORAPTOR_VERDE = B.rampa('243410', '2b3d13', '3f5f1a', '4a6422', '58702c')
VIENTRE_DROMORAPTOR_VERDE = B.rampa('24261a', '2e3018', '3e4222', '50562c', '5c6436')
PATAS_DROMORAPTOR_VERDE = B.rampa('0e0f0b', '141510', '22241a', '34362a', '4e5440')
ANTEBRAZO_DROMORAPTOR_VERDE = B.rampa('141410', '1c1c18', '2a2b24', '3c3e34', '4a4c40')
GARRA_DROMORAPTOR_VERDE = B.rampa('060708', '0a0c0e', '1c2024', '30363a', '485058')
MEMBRANA_DROMORAPTOR_VERDE = B.rampa('3a1236', '5a1850', '741f63', '94257c', 'c8107a')
RADIO_DROMORAPTOR_VERDE = B.rampa('174c14', '1d5e18', '2a8125', '3ca83a', '52b84a')
AMARILLO_DROMORAPTOR_VERDE = B.rampa('5a6010', '807a12', 'a89814', 'c0b02a', 'd4c440')
DIENTE_DROMORAPTOR_VERDE = B.rampa('8c826e', 'b8ac94', 'd2c8ae', 'e8e0c8', 'f2ecd8')
BOCA_DROMORAPTOR_VERDE = B.rampa('2e0a0c', '44100f', '5a1418', '741820', '8e1c24')
OJO_DROMORAPTOR_VERDE = {'a': B.H('d8c418'), 's': B.H('a89810'), 'k': B.H('141410'), 'n': B.H('101208'),
                         'm': B.H('3f5f1a'), 'M': B.H('2b3d13')}


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def _tex_dromoraptor_verde(Rr, v, dentro=None):
    """Al píxel: cada píxel, uno de los tonos de la rampa (sin mezclas)."""
    tex = L._rgba(L.color_continuo(Rr, np.clip(np.round(v), 0, len(Rr) - 1)))
    if dentro is not None:
        tex[..., 3] = np.where(dentro, 255, 0)
    return tex


def _manchas_dromoraptor_verde(xs, ys, s):
    """Un ruido de manchas de 2 a 4 píxeles (tres rejillas desplazadas que se suman), de 0 a 1."""
    n1 = _azar1((xs + 1) // 3, (ys + 2) // 3, s + 31)
    n2 = _azar1(xs // 2, (ys + 1) // 2, s + 37)
    n3 = _azar1((xs + 3) // 4, (ys + 1) // 4, s + 43)
    return n1 * 0.45 + n2 * 0.2 + n3 * 0.35


def _piel_rgb_dromoraptor_verde(tw, th, s, t, cara):
    """La piel al píxel: verde (manchas de verde medio y oscuro, alguna mancha oliva y motas claras) donde t es bajo y
    oliva pardo donde es alto (t, por píxel: 0 verde, 1 oliva), con el paso entre los dos manchado."""
    xs, ys = L._malla(tw, th)
    b = _manchas_dromoraptor_verde(xs, ys, s)
    b2 = _manchas_dromoraptor_verde(xs + 17, ys + 5, s + 101)
    a = _azar1(xs, ys, s * 7 + 5)
    oliva = (t + (b2 - 0.5) * 0.8) > 0.5
    v = 2.0 + (b > 0.62) * 1.0 - (b < 0.36) * 1.0 + ((a > 0.955) & (b > 0.45)) * 1.0
    if cara == 'abajo':
        v = v - 0.6
    verde = L.color_continuo(PIEL_DROMORAPTOR_VERDE, np.clip(np.round(v), 0, 4))
    # Manchas oliva sueltas sobre el verde, más hacia abajo.
    mo = (_manchas_dromoraptor_verde(xs + 7, ys + 3, s + 211) < 0.2 + 0.25 * np.clip(t * 2, 0, 1)) & ~oliva
    vo = 1.6 + (b > 0.55) * 1.0
    verde = np.where(mo[..., None], L.color_continuo(OLIVA_DROMORAPTOR_VERDE, np.clip(np.round(vo), 0, 4)), verde)
    vv = 2.0 + (b > 0.6) * 1.0 - (b < 0.34) * 1.0 - (cara == 'abajo') * 0.8
    pardo = L.color_continuo(VIENTRE_DROMORAPTOR_VERDE, np.clip(np.round(vv), 0, 4))
    return np.where(oliva[..., None], pardo, verde)


def piel_dromoraptor_verde(nombre, modo='filas', verde=0.45, oliva=0.75, y0=None, y1=None, corte=None):
    """El pintor de la piel de una caja. modo: 'filas' (el verde arriba y el oliva abajo, por las filas de las caras de
    los lados: con y0 y y1, la altura de arriba y de abajo de la caja, y corte, la altura a la que pasa a oliva, el paso
    es el mismo en todas las cajas del tronco), 'cuello' (de la nuca verde al gaznate oliva, por las columnas), 'verde'
    o 'oliva' (todo). verde, oliva: dónde empieza y acaba el paso (de 0, arriba, a 1, abajo)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        f = (ys + 0.5) / th
        if modo == 'verde':
            t = np.zeros((th, tw))
        elif modo == 'oliva':
            t = np.ones((th, tw))
        elif modo == 'cuello':
            g = (xs + 0.5) / tw
            if c == 'der':
                g = 1.0 - g
            if c in ('izq', 'der'):
                t = np.clip((g - 0.42) / 0.3, 0, 1)
            elif c == 'frente':
                t = np.ones((th, tw))
            else:
                t = np.zeros((th, tw))
        else:
            if c == 'arriba':
                t = np.zeros((th, tw))
            elif c == 'abajo':
                t = np.ones((th, tw))
            elif y0 is not None:
                y = y0 - f * (y0 - y1)
                t = np.clip((corte + 2.0 - y) / 4.0, 0, 1)
            else:
                t = np.clip((f - verde) / max(0.05, oliva - verde), 0, 1)
        return L._rgba(_piel_rgb_dromoraptor_verde(tw, th, s, t, c)), None
    return B.Pintor(nombre, fn)


def patas_dromoraptor_verde(nombre, paso=4, fase=1, rayas=True):
    """De la rodilla abajo: casi negras (oliva muy oscuro), con una raya clara de 1 px cada 'paso' filas."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s * 3 + 1)
        v = 1.4 + (a > 0.85) * 0.6 - (a < 0.1) * 0.5
        if c == 'arriba':
            v = v + 0.4
        elif c == 'abajo':
            v = v - 0.6
        elif rayas:
            v = np.where((ys + fase) % paso == 0, 3.4, v)
        return _tex_dromoraptor_verde(PATAS_DROMORAPTOR_VERDE, v), None
    return B.Pintor(nombre, fn)


def antebrazo_dromoraptor_verde(nombre):
    """El antebrazo: gris casi negro, con alguna veta a lo largo."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys // 3, s * 5 + 2)
        v = 1.6 + (a > 0.8) * 0.8 - (a < 0.15) * 0.6 + (c == 'arriba') * 0.5 - (c == 'abajo') * 0.6
        return _tex_dromoraptor_verde(ANTEBRAZO_DROMORAPTOR_VERDE, v), None
    return B.Pintor(nombre, fn)


def boca_dromoraptor_verde(nombre, base=1.6):
    """El paladar y la lengua: rojo oscuro."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s * 11 + 3)
        v = base + (a > 0.8) * 1.0 - (a < 0.12) * 0.8
        return _tex_dromoraptor_verde(BOCA_DROMORAPTOR_VERDE, v), None
    return B.Pintor(nombre, fn)


def cabeza_dromoraptor_verde(nombre):
    """La cabeza: la piel verde y, en los lados, el ojo de 4 x 2 (de atrás adelante: amarillo, pupila negra,
    amarillo, amarillo; sin ceja) a 4 px de la nuca y 2 del techo, la mancha oliva del ojo hacia delante (6 x 3) y la
    nariz, un punto oscuro arriba y delante. Debajo, el paladar rojo. Pintado al píxel de Minecraft, sin estirar."""
    def fn(tw, th, c, s):
        if c == 'abajo':
            return boca_dromoraptor_verde(nombre + '_b').fn(tw, th, c, s)
        rgb = _piel_rgb_dromoraptor_verde(tw, th, s, np.zeros((th, tw)), c)
        tex = L._rgba(rgb)
        if c in ('izq', 'der'):
            def pon(col, fila, letra):
                # col contada desde la nuca (en 'izq' la columna 0 es la nuca; en 'der', el hocico).
                cc = col if c == 'izq' else tw - 1 - col
                if 0 <= cc < tw and 0 <= fila < th:
                    tex[fila, cc, :3] = np.round(OJO_DROMORAPTOR_VERDE[letra])
            for k in range(6):
                for f in range(1, 4):
                    pon(8 + k, f, 'm' if (k + f) % 3 else 'M')
            for k, letra in enumerate('akaa'):
                pon(4 + k, 2, letra)
                pon(4 + k, 3, 's' if letra == 'a' else 'k')
            pon(tw - 3, 1, 'n')
        return tex, None
    return B.Pintor(nombre, fn)


def dientes_dromoraptor_verde(nombre, arriba=True, encia=1, largos=(3, 2), paso=2):
    """Los dientes en su 2.ª capa, al píxel de Minecraft: de 1 px de ancho, separados 1 px, blanco crema con la raíz
    algo más oscura. Arriba cuelgan (las 'encia' filas de arriba montan sobre la cabeza y quedan vacías); abajo se
    levantan sobre la mandíbula, con la encía roja entre ellos."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c in ('arriba', 'abajo', 'atras'):
            return tex, None
        rng = np.random.default_rng(int(s) * 13 + tw * 5 + th)
        n = tw
        lk = rng.choice(largos, n)
        col = xs if c != 'der' else tw - 1 - xs
        diente = (col % paso) == 0
        if arriba:
            r = ys - encia
            dentro = diente & (r >= 0) & (r < lk[col])
            v = 3.0 - (r == 0) * 1.4 + (r >= 2) * 0.6
            tex = _tex_dromoraptor_verde(DIENTE_DROMORAPTOR_VERDE, v, dentro)
        else:
            r = (th - 1 - encia) - ys
            dentro = diente & (ys <= th - 1 - encia) & (r < lk[col])
            v = 3.0 + (ys == 0) * 0.6
            tex = _tex_dromoraptor_verde(DIENTE_DROMORAPTOR_VERDE, v, dentro)
            gum = ~diente & (ys == th - 1 - encia)
            tex[gum, :3] = np.round(BOCA_DROMORAPTOR_VERDE[4])
            tex[gum, 3] = 255
        return tex, None
    return B.Pintor(nombre, fn)


def mandibula_dromoraptor_verde(nombre):
    """La mandíbula: por fuera oliva oscuro; arriba, la lengua roja."""
    piel = piel_dromoraptor_verde(nombre + '_p', modo='oliva')
    boca = boca_dromoraptor_verde(nombre + '_b', base=2.6)

    def fn(tw, th, c, s):
        if c == 'arriba':
            return boca.fn(tw, th, c, s)
        tex, _ = piel.fn(tw, th, c, s)
        return tex, None
    return B.Pintor(nombre, fn)


def bloque_dromoraptor_verde(nombre):
    """El bloque amarillo, con el aire translúcido de la capa del slime pintado (opaco, como la vela de los raptores
    aprobados, para que se vea igual en el juego y en las vistas): el canto claro de 1 px arriba y a un lado, las caras
    amarillas con algún píxel más oscuro y verdoso (lo de dentro, que se ve a través) y el canto del otro lado y el de
    abajo, en sombra."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s * 3 + 9)
        v = 2.0 + (a > 0.88) * 1.0 - ((a < 0.14) & (ys > 1)) * 1.0
        if c == 'arriba':
            v = np.where((xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1), 4.0, 3.0 - (a < 0.12) * 1.0)
        else:
            v = np.where(xs == tw - 1, 1.0, v)
            v = np.where(ys == th - 1, 1.0, v)
            v = np.where(xs == 0, 3.0, v)
            v = np.where(ys == 0, 4.0, v)
        return _tex_dromoraptor_verde(AMARILLO_DROMORAPTOR_VERDE, v), None
    return B.Pintor(nombre, fn)


def cresta_dromoraptor_verde(nombre, ancho=2):
    """Una cresta: un palo plano de 'ancho' px, verde de la piel (el canto de delante más claro), con la punta cortada en
    recto y un pellizco de 1 px hacia atrás arriba (la banderita). La columna 0, detrás."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        palo = xs >= tw - ancho
        bandera = (xs == tw - ancho - 1) & (ys < 2)
        dentro = palo | bandera
        a = _azar1(xs, ys, s * 5 + 7)
        v = 2.2 + (xs == tw - 1) * 0.8 - (ys > th * 0.7) * 0.6 + (a > 0.85) * 0.5
        return _tex_dromoraptor_verde(PIEL_DROMORAPTOR_VERDE, v, dentro), None
    return B.Pintor(nombre, fn)


def _linea_dromoraptor_verde(p, q):
    """Los píxeles de una raya de 1 px de p a q (en píxeles, x a lo ancho e y a lo alto): uno por fila si es más alta
    que ancha (o uno por columna si no), así que inclinada sale en escalera. Devuelve [(i, j, t)], t de 0 en p a 1."""
    (x0, y0), (x1, y1) = p, q
    out = []
    if abs(y1 - y0) >= abs(x1 - x0):
        j0, j1 = int(math.floor(min(y0, y1))), int(math.floor(max(y0, y1)))
        for j in range(j0, j1 + 1):
            yc = min(max(j + 0.5, min(y0, y1)), max(y0, y1))
            t = (yc - y0) / (y1 - y0) if y1 != y0 else 0.0
            out.append((int(math.floor(x0 + (x1 - x0) * t)), j, t))
    else:
        i0, i1 = int(math.floor(min(x0, x1))), int(math.floor(max(x0, x1)))
        for i in range(i0, i1 + 1):
            xc = min(max(i + 0.5, min(x0, x1)), max(x0, x1))
            t = (xc - x0) / (x1 - x0)
            out.append((i, int(math.floor(y0 + (y1 - y0) * t)), t))
    return out


def _poligono_dromoraptor_verde(px, py, pts):
    """Si los puntos (px, py) están dentro del polígono (par-impar)."""
    dentro = np.zeros(px.shape, bool)
    n = len(pts)
    for k in range(n):
        (xa, ya), (xb, yb) = pts[k], pts[(k + 1) % n]
        cruza = ((ya > py) != (yb > py))
        xi = xa + (py - ya) * (xb - xa) / np.where(yb == ya, 1e-9, yb - ya)
        dentro ^= cruza & (px < xi)
    return dentro


def vela_dromoraptor_verde(nombre, rayos, asoma, colgando=False, fucsia=0.3):
    """Un abanico (o la aleta de un brazo) en una lámina, al píxel de Minecraft: los radios verdes de 1 px en escalera
    y, entre cada dos, la membrana, que llena desde la raíz hasta un borde en escalera que va de cerca de la punta de un
    radio a unos píxeles por debajo de la del siguiente (cada gajo acaba en pico y los radios asoman). La membrana,
    morada oscura en la raíz y magenta hacia el borde, con manchas fucsia cerca del borde.
    rayos: [((u, v) de la raíz, (u, v) de la punta)], en fracciones de la lámina: u de atrás (0) adelante (1) y v de la
    raíz (0) a lo más lejos (1) (hacia arriba; con 'colgando', hacia abajo). asoma: por gajo (entre el radio k y el
    k + 1), lo que asoman (en píxeles) el radio k y el k + 1 por encima del borde de la membrana."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c != 'frente':
            return tex, None
        # u, v en píxeles (centros): u de atrás adelante y v desde la raíz.
        U = xs + 0.5
        V = (ys + 0.5) if colgando else (th - 1 - ys) + 0.5
        P = [((ub * (tw - 1) + 0.5, vb * (th - 1) + 0.5), (ut * (tw - 1) + 0.5, vt * (th - 1) + 0.5))
             for (ub, vb), (ut, vt) in rayos]
        memb = np.zeros((th, tw), bool)
        hasta = np.ones((th, tw))
        for k in range(len(P) - 1):
            (a0, a1), (b0, b1) = P[k], P[k + 1]
            la, lb = math.dist(a0, a1), math.dist(b0, b1)
            pa, pb = asoma[k]
            fa, fb = max(0.0, 1 - pa / la), max(0.0, 1 - pb / lb)
            qa = (a0[0] + (a1[0] - a0[0]) * fa, a0[1] + (a1[1] - a0[1]) * fa)
            qb = (b0[0] + (b1[0] - b0[0]) * fb, b0[1] + (b1[1] - b0[1]) * fb)
            mk = _poligono_dromoraptor_verde(U, V, [a0, qa, qb, b0])
            memb |= mk
            # Lo que le falta a cada píxel para llegar al borde (para el magenta y el fucsia de fuera).
            borde_v = qa[1] + (qb[1] - qa[1]) * np.clip((U - qa[0]) / ((qb[0] - qa[0]) or 1e-9), 0, 1)
            hasta = np.where(mk, np.clip(V / np.maximum(borde_v, 1.0), 0, 1), hasta)
        a = _azar1(xs, ys, s * 7 + 3)
        bl = _manchas_dromoraptor_verde(xs, ys, s + 59)
        vm = 2.0 + 1.7 * hasta + (a > 0.86) * 0.6 - (a < 0.12) * 0.6
        fu = (hasta > 0.72) & (bl > 1.0 - fucsia)
        vm = np.where(fu, 4.0, vm)
        tex = _tex_dromoraptor_verde(MEMBRANA_DROMORAPTOR_VERDE, vm, memb)
        # Los radios, encima.
        for (p0, p1) in P:
            for (i, j, t) in _linea_dromoraptor_verde(p0, p1):
                col = i
                fila = j if colgando else th - 1 - j
                if 0 <= col < tw and 0 <= fila < th:
                    vr = 2.0 + 2.0 * t + (_azar1(col, fila, s + 3) > 0.8) * 0.5
                    tex[fila, col, :3] = np.round(L.color_continuo(RADIO_DROMORAPTOR_VERDE,
                                                                   np.array([float(np.clip(round(vr), 0, 4))]))[0])
                    tex[fila, col, 3] = 255
        return tex, None
    return B.Pintor(nombre, fn)


def garras_dromoraptor_verde(nombre, curva, n=1):
    """Las garras, con el dibujo de las aprobadas (garras_lamina) y negras con el canto gris."""
    return R.garras_lamina(nombre, GARRA_DROMORAPTOR_VERDE, n=n, curva=curva, adelante=True)


# ======================================================================================================================
#  Las piezas del Verde, sobre el cuerpo aprobado
# ======================================================================================================================
def _lamina_dromoraptor_verde(m, parte, M, ancho, alto, pint, y0=0.0):
    """Una lámina de una sola cara en el plano XY del marco M, de 'ancho' x 'alto', centrada en X, desde y0."""
    m._caja(parte, M, -ancho / 2, y0, 0.0, ancho, alto, 0.0, None, {c: (pint if c == 'frente' else None) for c in B.CARAS})


def _sagital_dromoraptor_verde(z, y, inclina=0.0):
    """El marco de una lámina de perfil (en la línea del medio), con la raíz en (0, y, z): su cara mira hacia -X y la
    columna 0 de su textura queda detrás (-Z); 'inclina' la echa hacia delante (+) o hacia atrás (-), en grados,
    alrededor de la raíz. (En el juego da igual hacia qué lado mire: la luz de las caras de los lados es la misma; en
    las vistas, la cara que mira a -X se ve con la luz de los costados del tronco, como en las imágenes.)"""
    return T(0, y, z) @ B.girar((inclina, 0, 0)) @ B.girar((0, -90, 0))


def _reemplazar_dromoraptor_verde(m, parte, idx, pint, caras=None):
    """Cambia el pintor de la caja idx de la parte (sin tocar su forma): 'pint' en todas sus caras pintadas, o 'caras'."""
    c = list(m.partes[parte].cajas[idx])
    c[7] = {k: ((caras or {}).get(k, pint) if v is not None else None) for k, v in c[7].items()}
    m.partes[parte].cajas[idx] = tuple(c)


def _franja_dromoraptor_verde(m, parte, idx):
    """La altura (en el boceto) de arriba y de abajo de la caja idx."""
    M, x0, y0, z0, w, h, d = m.partes[parte].cajas[idx][:7]
    ys = [(M @ np.array((x0 + dx, y0 + dy, z0 + dz, 1.0)))[1] for dx in (0, w) for dy in (0, h) for dz in (0, d)]
    return max(ys), min(ys)


def retexturar_dromoraptor_verde(m):
    """Las texturas del Verde en las cajas del cuerpo aprobado (cuántas hay en cada parte se comprueba, para que un
    cambio del cuerpo no pase sin verse)."""
    n = {p: len(m.partes[p].cajas) for p in m.partes}
    assert n['cuerpo'] == 9 and n['cabeza'] == 5 and n['mandibula'] == 2, n
    assert n['cola'] == 2 and n['cola2'] == 2 and n['plumas'] == 3, n
    for ld in ('i', 'd'):
        assert n[f'pierna_{ld}'] == 1 and n[f'cana_{ld}'] == 7 and n[f'brazo_{ld}'] == 5, n
    # El tronco: el paso del verde al oliva, a la misma altura en todas sus cajas (y 16,5 del boceto).
    for k in range(8):
        y0, y1 = _franja_dromoraptor_verde(m, 'cuerpo', k)
        _reemplazar_dromoraptor_verde(m, 'cuerpo', k, piel_dromoraptor_verde(f'piel_tronco_{ID}_{k}', y0=y0, y1=y1,
                                                                              corte=16.5))
    _reemplazar_dromoraptor_verde(m, 'cuerpo', 8, piel_dromoraptor_verde(f'piel_cuello_{ID}', modo='cuello'))
    # La cabeza (el ojo, la mancha y la nariz; el paladar rojo), los dientes y la mandíbula.
    _reemplazar_dromoraptor_verde(m, 'cabeza', 0, cabeza_dromoraptor_verde(f'cabeza_{ID}'))
    _reemplazar_dromoraptor_verde(m, 'cabeza', 1, dientes_dromoraptor_verde(f'dientes_arriba_{ID}', arriba=True))
    _reemplazar_dromoraptor_verde(m, 'mandibula', 0, mandibula_dromoraptor_verde(f'mandibula_{ID}'))
    _reemplazar_dromoraptor_verde(m, 'mandibula', 1, dientes_dromoraptor_verde(f'dientes_abajo_{ID}', arriba=False,
                                                                             encia=1, largos=(1, 2)))
    # La cola: verde arriba, oliva por los lados abajo.
    for parte in ('cola', 'cola2'):
        for k in range(2):
            _reemplazar_dromoraptor_verde(m, parte, k, piel_dromoraptor_verde(f'piel_{parte}_{ID}_{k}', verde=0.4,
                                                                              oliva=0.8))
    garra_pie = garras_dromoraptor_verde(f'garra_pie_{ID}', 0.9)
    hoz = garras_dromoraptor_verde(f'hoz_{ID}', 1.4)
    gancho = garras_dromoraptor_verde(f'gancho_{ID}', 1.7)
    for ld in ('i', 'd'):
        # El muslo, verde arriba y oliva pardo abajo; de la rodilla abajo, casi negro con rayas.
        _reemplazar_dromoraptor_verde(m, f'pierna_{ld}', 0, piel_dromoraptor_verde(f'muslo_{ID}', verde=0.35,
                                                                                   oliva=0.7))
        _reemplazar_dromoraptor_verde(m, f'cana_{ld}', 0, patas_dromoraptor_verde(f'espinilla_{ID}', paso=4, fase=2))
        _reemplazar_dromoraptor_verde(m, f'cana_{ld}', 1, patas_dromoraptor_verde(f'cana_{ID}', paso=4, fase=1))
        _reemplazar_dromoraptor_verde(m, f'cana_{ld}', 2, patas_dromoraptor_verde(f'pie_{ID}', rayas=False))
        for k in (3, 4, 5):
            _reemplazar_dromoraptor_verde(m, f'cana_{ld}', k, garra_pie)
        _reemplazar_dromoraptor_verde(m, f'cana_{ld}', 6, hoz)
        # El brazo de arriba, verde; el antebrazo, casi negro; las garras, negras.
        _reemplazar_dromoraptor_verde(m, f'brazo_{ld}', 0, piel_dromoraptor_verde(f'brazo_{ID}', modo='verde'))
        _reemplazar_dromoraptor_verde(m, f'brazo_{ld}', 1, antebrazo_dromoraptor_verde(f'antebrazo_{ID}'))
        for k in (2, 3):
            _reemplazar_dromoraptor_verde(m, f'brazo_{ld}', k, gancho)


def quitar_dromoraptor_verde(m):
    """Quita del cuerpo aprobado lo que se rehace en el Verde: las crestas y la vela amarilla de la cabeza, las aletas
    de los brazos y los abanicos (con su parte, 'plumas')."""
    m.partes['cabeza'].cajas = m.partes['cabeza'].cajas[:2]
    for ld in ('i', 'd'):
        m.partes[f'brazo_{ld}'].cajas = m.partes[f'brazo_{ld}'].cajas[:4]
    assert not any(p.padre == 'plumas' for p in m.partes.values())
    del m.partes['plumas']


# Las medidas del cuerpo aprobado que se usan (en el boceto, sin agrandar).
CABEZA_DROMORAPTOR_VERDE = dict(techo=30.0, frente=22.1, nuca=9.1, ancho=8.0)


def bloque_y_crestas_dromoraptor_verde(m):
    """El bloque amarillo (una caja translúcida sobre la mitad de delante de la cabeza, con su frente 1 px por detrás
    del hocico) y las dos crestas (palos de 2 px, 1 px detrás del bloque y 1 px entre ellas, algo echadas atrás)."""
    px = 1.0 / TAM
    c = CABEZA_DROMORAPTOR_VERDE
    largo, ancho, alto = 6.0, 6.0, 7.0
    z1 = c['frente'] - px
    z0 = z1 - largo
    m.caja('cabeza', (0, c['techo'] + alto / 2, (z0 + z1) / 2), (ancho, alto, largo),
           bloque_dromoraptor_verde(f'bloque_{ID}'), caras={'abajo': None})
    cresta = cresta_dromoraptor_verde(f'cresta_{ID}')
    w = 3 * px
    zc = z0 - px - 2 * px
    for k, sobre in enumerate((alto + px, alto * 0.62)):
        # La lámina: 3 px de ancho (el palo de 2 delante y la banderita detrás), desde 1 px dentro de la cabeza.
        z = zc - k * 3 * px + px / 2
        M = _sagital_dromoraptor_verde(z, c['techo'] - px, inclina=-12)
        _lamina_dromoraptor_verde(m, 'cabeza', M, w, sobre + px, cresta)


# Los abanicos del lomo: (parte, padre, z de detrás y de delante de la lámina, y de la raíz, alto, rayos, asoma).
ABANICOS_DROMORAPTOR_VERDE = (
    # El de la cola: cuatro radios echados hacia atrás, el de detrás corto y el de delante el más alto.
    ('abanico_cola', 'cola2', -33.0, -18.0, 22.2, 15.2,
     [((0.20, 0.0), (0.0, 0.34)), ((0.48, 0.0), (0.24, 0.74)), ((0.72, 0.0), (0.47, 0.92)), ((1.0, 0.0), (0.70, 1.0))],
     [(0.6, 3.5), (1.0, 3.0), (1.0, 2.5)]),
    # El pequeño, en la raíz de la cola: tres radios echados hacia atrás.
    ('abanico_cadera', 'cola', -17.0, -9.0, 22.8, 8.6,
     [((0.25, 0.0), (0.0, 0.45)), ((0.62, 0.0), (0.36, 1.0)), ((1.0, 0.0), (0.80, 0.82))],
     [(0.6, 3.0), (3.0, 1.0)]),
    # El de los hombros: cinco radios en abanico, el del medio derecho y el más alto.
    ('abanico_lomo', 'cuerpo', -7.0, 7.0, 23.4, 14.2,
     [((0.30, 0.0), (0.0, 0.50)), ((0.40, 0.0), (0.20, 0.86)), ((0.50, 0.0), (0.50, 1.0)), ((0.60, 0.0), (0.80, 0.86)),
      ((0.70, 0.0), (1.0, 0.50))],
     [(0.6, 3.0), (0.8, 3.0), (3.0, 0.8), (3.0, 0.6)]),
)


def abanicos_dromoraptor_verde(m):
    """Los tres abanicos del lomo y de la cola, láminas en la línea del medio, cada uno en la parte en la que va (el de
    la cola se mueve con la punta de la cola)."""
    for nombre, padre, z0, z1, y, alto, rayos, asoma in ABANICOS_DROMORAPTOR_VERDE:
        m.parte(nombre, padre, (0, y, (z0 + z1) / 2))
        vela = vela_dromoraptor_verde(f'{nombre}_{ID}', rayos, asoma)
        _lamina_dromoraptor_verde(m, nombre, _sagital_dromoraptor_verde((z0 + z1) / 2, y), z1 - z0, alto, vela)


def aletas_brazos_dromoraptor_verde(m):
    """La aleta de cada brazo: cuelga del canto de abajo del antebrazo, de la muñeca al codo, hasta casi el suelo, con
    seis radios casi paralelos echados hacia atrás que se abren un poco hacia abajo y asoman en picos."""
    rayos = [((0.02, 0.0), (0.0, 0.92)), ((0.21, 0.0), (0.15, 1.0)), ((0.40, 0.0), (0.33, 0.95)),
             ((0.59, 0.0), (0.53, 1.0)), ((0.78, 0.0), (0.74, 0.94)), ((0.97, 0.0), (0.96, 0.98))]
    asoma = [(1.0, 3.0)] * 5
    aleta = vela_dromoraptor_verde(f'aleta_brazo_{ID}', rayos, asoma, colgando=True, fucsia=0.25)
    for lado, ld in R.LADOS:
        z0, z1 = 3.6, 17.2
        arriba, abajo = 8.6, 0.4
        M = T(lado * 5.6, abajo, (z0 + z1) / 2) @ B.girar((0, -90, 0))
        _lamina_dromoraptor_verde(m, f'brazo_{ld}', M, z1 - z0, arriba - abajo, aleta)


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
# La boca, siempre abierta como en todas sus imágenes (unos 25° quieto): la mandíbula aprobada está cerrada en la malla,
# así que se abre con la animación 'siempre' (si se quiere cerrada, basta con poner este ángulo a 0).
BOCA_ABIERTA_DROMORAPTOR_VERDE = 20.0


def anims_dromoraptor_verde(m):
    """siempre: la boca abierta, que jadea un poco, y los abanicos que respiran; reposo: la cabeza a tirones de pájaro
    (mira a un lado, se queda, mira al otro), el cuerpo que respira, la cola que se mece y las aletas de los brazos que
    se balancean; andar y correr: la pierna en zigzag (el muslo adelante y atrás y la rodilla que se dobla al levantar
    el pie), el cuerpo que sube y baja, la cola que ondula a contrapaso y la cabeza firme (al correr, echado hacia
    delante y con los brazos recogidos); ataque: echa la cabeza atrás y lanza el mordisco con la boca abierta del todo y
    las garras por delante; especial: la llamada a la manada (la cabeza arriba, la boca abierta y los abanicos que se
    abren); especial2: el salto sobre la presa, como en las imágenes (se agacha, salta con los muslos adelante y las
    patas recogidas, los brazos por delante y la boca abierta, y cae); aparece: se sacude y se yergue; muerte: cae de
    lado."""
    LADOS = R.LADOS
    s_ = m.anim('siempre', 3.2, bucle=True)
    s_.onda('mandibula', 'r', 0, 4.0, periodo=1.6, base=BOCA_ABIERTA_DROMORAPTOR_VERDE)
    for nombre in ('abanico_cola', 'abanico_cadera', 'abanico_lomo'):
        s_.onda(nombre, 'e', 1, 0.03, periodo=1.6, base=1.0)
    r = m.anim('reposo', 3.2, bucle=True)
    r.rot('cabeza', [(0, 0, 0, 0), (0.12, 4, 22, 0), (1.0, 4, 22, 0), (1.12, -6, 0, 0), (1.6, -6, 0, 0),
                     (1.72, 2, -20, 0), (2.7, 2, -20, 0), (2.85, 0, 0, 0), (3.2, 0, 0, 0)])
    r.onda('cola', 'r', 1, 6, periodo=3.2)
    r.onda('cola2', 'r', 1, 9, periodo=3.2, fase=0.15)
    r.onda('cuerpo', 'm', 1, 0.3, periodo=1.6)
    for k, (lado, ld) in enumerate(LADOS):
        r.onda(f'brazo_{ld}', 'r', 0, 3, periodo=3.2, fase=0.5 * k)
    for nombre, largo, amp, inclina in (('andar', 0.8, 1.0, 0.0), ('correr', 0.5, 1.4, 7.0)):
        a = m.anim(nombre, largo, bucle=True)
        for k, (lado, ld) in enumerate(LADOS):
            f = 0.5 * k
            a.onda(f'pierna_{ld}', 'r', 0, 28 * amp, periodo=largo, fase=f)
            a.onda(f'cana_{ld}', 'r', 0, 22 * amp, periodo=largo, fase=f + 0.25, base=-10 * amp)
            a.onda(f'brazo_{ld}', 'r', 0, 6 * amp, periodo=largo, fase=f + 0.5, base=-inclina * 1.5)
        a.onda('cuerpo', 'm', 1, 0.7 * amp, periodo=largo / 2, base=0.5 * amp)
        a.onda('cuerpo', 'r', 0, 1.5 * amp, periodo=largo / 2, base=inclina)
        a.onda('cola', 'r', 1, 7 * amp, periodo=largo, fase=0.5)
        a.onda('cola2', 'r', 1, 10 * amp, periodo=largo, fase=0.65)
        a.onda('cola', 'r', 0, 2 * amp, periodo=largo / 2, base=-inclina * 0.8)
        a.onda('cabeza', 'r', 0, 2 * amp, periodo=largo / 2, fase=0.5, base=-inclina * 0.5)
        a.onda('abanico_lomo', 'r', 0, 2.5 * amp, periodo=largo / 2)
        a.onda('abanico_cola', 'r', 0, 3 * amp, periodo=largo / 2, fase=0.25)
    at = m.anim('ataque', 0.5)
    at.rot('cabeza', [(0, 0, 0, 0), (0.15, -18, 0, 0), (0.28, 22, 0, 0), (0.5, 0, 0, 0)])
    at.mov('cabeza', [(0, 0, 0, 0), (0.15, 0, 0.5, -1.0), (0.28, 0, -0.5, 3.0), (0.5, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.15, 30, 0, 0), (0.28, -14, 0, 0), (0.5, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.15, -4, 0, 0), (0.28, 5, 0, 0), (0.5, 0, 0, 0)])
    for lado, ld in LADOS:
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.15, -35, 0, 0), (0.28, 25, 0, 0), (0.5, 0, 0, 0)])
    e = m.anim('especial', 1.2)
    e.rot('cabeza', [(0, 0, 0, 0), (0.25, -32, 0, 0), (0.9, -32, 0, 0), (1.2, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.25, 26, 0, 0), (0.45, 12, 0, 0), (0.6, 26, 0, 0), (0.9, 20, 0, 0),
                        (1.2, 0, 0, 0)])
    for nombre in ('abanico_cola', 'abanico_cadera', 'abanico_lomo'):
        e.esc(nombre, [(0, 1, 1, 1), (0.25, 1.0, 1.15, 1.06), (0.9, 1.0, 1.15, 1.06), (1.2, 1, 1, 1)])
    e.rot('cola', [(0, 0, 0, 0), (0.25, -8, 0, 0), (0.9, -8, 0, 0), (1.2, 0, 0, 0)])
    for lado, ld in LADOS:
        e.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.25, -20, 0, lado * 12), (0.9, -20, 0, lado * 12), (1.2, 0, 0, 0)])
    # El salto (como en la imagen principal, en pleno vuelo hacia t = 0,45).
    j = m.anim('especial2', 1.0)
    j.mov('cuerpo', [(0, 0, 0, 0), (0.15, 0, -2.0, -0.5), (0.45, 0, 7.0, 5.0), (0.62, 0, 6.0, 8.0),
                     (0.85, 0, -1.0, 9.0), (1.0, 0, 0, 0)])
    j.rot('cuerpo', [(0, 0, 0, 0), (0.15, 6, 0, 0), (0.45, -6, 0, 0), (0.62, -2, 0, 0), (0.85, 5, 0, 0),
                     (1.0, 0, 0, 0)])
    j.rot('cabeza', [(0, 0, 0, 0), (0.15, 6, 0, 0), (0.45, -8, 0, 0), (0.7, 4, 0, 0), (1.0, 0, 0, 0)])
    j.rot('mandibula', [(0, 0, 0, 0), (0.15, 4, 0, 0), (0.45, 10, 0, 0), (0.7, 18, 0, 0), (1.0, 0, 0, 0)])
    for lado, ld in LADOS:
        j.rot(f'pierna_{ld}', [(0, 0, 0, 0), (0.15, 18, 0, 0), (0.45, -48, 0, 0), (0.62, -40, 0, 0),
                                (0.85, 4, 0, 0), (1.0, 0, 0, 0)])
        j.rot(f'cana_{ld}', [(0, 0, 0, 0), (0.15, -26, 0, 0), (0.45, 72, 0, 0), (0.62, 60, 0, 0), (0.85, -6, 0, 0),
                              (1.0, 0, 0, 0)])
        j.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.15, 10, 0, 0), (0.45, -26, 0, 0), (0.7, -30, 0, 0),
                               (1.0, 0, 0, 0)])
    j.rot('cola', [(0, 0, 0, 0), (0.15, -4, 0, 0), (0.45, 6, 0, 0), (0.85, -6, 0, 0), (1.0, 0, 0, 0)])
    ap = m.anim('aparece', 0.8)
    ap.rot('cuerpo', [(0, 0, 0, 0), (0.1, 0, 0, 6), (0.2, 0, 0, -6), (0.3, 0, 0, 4), (0.4, 0, 0, -2), (0.5, 0, 0, 0)])
    ap.rot('cabeza', [(0, 0, 0, 0), (0.2, -20, 0, 0), (0.55, -20, 0, 0), (0.8, 0, 0, 0)])
    ap.rot('mandibula', [(0, 0, 0, 0), (0.2, 20, 0, 0), (0.55, 20, 0, 0), (0.8, 0, 0, 0)])
    ap.onda('cola', 'r', 1, 12, periodo=0.4)
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, 5, 0, 0), (1.0, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -9, 0)])
    d.rot('cola', [(0, 0, 0, 0), (1.0, 0, 15, 0)])
    d.rot('mandibula', [(0, 0, 0, 0), (0.4, 14, 0, 0), (1.0, 6, 0, 0)])
    for lado, ld in LADOS:
        d.rot(f'pierna_{ld}', [(0, 0, 0, 0), (1.0, -20, 0, 0)])
        d.rot(f'cana_{ld}', [(0, 0, 0, 0), (1.0, 30, 0, 0)])


def construir():
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0
    # El cuerpo aprobado, tal cual (los pintores de aquí se cambian después caja a caja).
    R.dromoraptor(m, piel_dromoraptor_verde(f'piel_{ID}'), patas_dromoraptor_verde(f'patas_{ID}'),
                  PIEL_DROMORAPTOR_VERDE, (MEMBRANA_DROMORAPTOR_VERDE, RADIO_DROMORAPTOR_VERDE),
                  (cresta_dromoraptor_verde(f'cresta0_{ID}'), bloque_dromoraptor_verde(f'bloque0_{ID}')),
                  DIENTE_DROMORAPTOR_VERDE)
    retexturar_dromoraptor_verde(m)
    quitar_dromoraptor_verde(m)
    bloque_y_crestas_dromoraptor_verde(m)
    abanicos_dromoraptor_verde(m)
    aletas_brazos_dromoraptor_verde(m)
    m.anims.clear()
    anims_dromoraptor_verde(m)
    return m

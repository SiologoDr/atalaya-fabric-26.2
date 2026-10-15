"""
El Slime rediseñado (15-10-2026). Juan: «ahora sí me gustó, guárdalo en mobs; ahora sigamos con el slime», después del
Blaze. Lo que valió con el Blaze: que siga siendo el mob (su silueta y sus señas) pero que imponga, con una cara de
monstruo y piezas nuevas grandes, y texturas de pixel detallado a un texel por pixel.

Del Slime se queda lo que lo hace un Slime: el cubo de gelatina translucida, el nucleo de dentro y la cara que se ve a
traves de la gelatina, y el charco que deja. Lo nuevo: es de tres bloques, la cara es de monstruo (el ceño en uve, los
ojos rasgados que brillan y los dientes) y cada tipo cambia una cosa grande:

    A  el Tragón     verde de siempre: el cubo se abre en dos como unas fauces, con los dientes de gelatina, las babas
                     entre la quijada y la boca y la garganta que brilla; dentro se ven los huesos y el yelmo de lo que se
                     ha tragado
    B  el Erizo      verde de cienaga, azulado: lleva clavadas las armas de los que no pudieron con el (espadas, flechas,
                     una lanza, un hacha y un escudo hundido de canto); la boca es una sonrisa de dientes
    C  el Fundido    de gelatina negra con acido que brilla: se derrite, con chorretones que bajan por los lados y un
                     charco de acido que brilla debajo; burbujas que suben por dentro, el nucleo encendido y los ojos que
                     lloran acido

Se modela como un mob: en pixeles del modelo con un texel por pixel, y luego se agranda. La gelatina va aparte, para
pintarla translucida despues de lo opaco.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _emis
from sierpe_modelo import lamina
from jefa_modelo import pt

TAU = math.tau
D = vr.D2R
PPB = 1


def _h(*cs):
    return [nm._hex(c) for c in cs]


VARIANTES = {
    'A': dict(clave='SLA', nombre='el Tragón', corto='tragon', escala=1.6,
              gel=_h('1a4416', '2a6420', '3e8a2c', '5eb244', '8cd866', 'c8f8a0'),
              nucleo=_h('0e2a0c', '163e12', '20541a', '2c6a22'),
              brillo=_h('7cff5a', 'd8ffb0'), diente=_h('9ed886', 'd2f4bc', 'f0ffe4'),
              transl=0.5, luz='8cff5a'),
    'B': dict(clave='SLB', nombre='el Erizo', corto='erizo', escala=1.6,
              gel=_h('0c3434', '125250', '1c7470', '30988e', '5ec4b4', 'b4f4e6'),
              nucleo=_h('08201e', '0e302e', '164442', '205a56'),
              brillo=_h('ffb43a', 'ffe6a0'), diente=_h('8ec8bc', 'c8eee6', 'eefffa'),
              transl=0.5, luz='ffb43a'),
    'C': dict(clave='SLC', nombre='el Fundido', corto='fundido', escala=1.6,
              gel=_h('0c120a', '16200e', '223016', '34461e', '4c642a', '74903a'),
              nucleo=_h('101a06', '1c2c0a', '2c4210', '6a9a18'),
              brillo=_h('b4ff2a', 'eeffa0'), diente=_h('6a7a3a', '9cb04e', 'd4ec7a'),
              transl=0.62, luz='b4ff2a'),
}

HIERRO = _h('1e2228', '30363e', '4a525c', '6e7882', 'a4aeb8', 'dce4ea')
MADERA = _h('2a180c', '3e2612', '58381c', '744a26', '8e6032')
HUESO = _h('6a6450', '9a9276', 'c4bc9c', 'e2dcc0', 'f6f2e2')
PLUMA = _h('8a8a8a', 'c4c4c4', 'eeeeee')


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _pinta(idx, rampa, alfa=None):
    """La textura desde un indice de la rampa (con -1, transparente)."""
    th, tw = idx.shape
    t = np.zeros((th, tw, 4), np.uint8)
    for k, c in enumerate(rampa):
        t[idx == k] = (*c, 255)
    if alfa is not None:
        t[~alfa] = 0
    t[idx < 0] = 0
    return t


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    gel, nuc, bri, die = V['gel'], V['nucleo'], V['brillo'], V['diente']
    tipo = V['corto']

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'sl%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def p_gel(tw, th, cara_, s):
        """La gelatina: lisa, con el canto un tono mas claro (asi se lee el borde del cubo), un brillo en ele arriba a
        la izquierda y dos o tres burbujas limpias."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        if cara_ == 'abajo':
            return _pinta(np.full((th, tw), 2), gel), None
        borde = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)
        idx[borde] = 4
        if tw >= 8 and th >= 8:
            idx[2, 2:min(tw - 2, 7)] = 5                                         # el brillo, en ele
            idx[3:min(th - 2, 5), 2] = 5
            rng = random.Random(s)
            for _ in range(3):                                                   # las burbujas
                x, y = rng.randrange(4, tw - 3), rng.randrange(th // 2, th - 3)
                idx[y, x] = 4
                if rng.random() < 0.5 and x + 1 < tw - 1:
                    idx[y, x + 1] = 4
        if cara_ == 'arriba':
            idx[idx == 3] = 4 if tipo != 'fundido' else 3
        t = _pinta(idx, gel)
        if tipo == 'fundido':
            return t, _emis(t, idx >= 4, 40)
        return t, None
    reg('gel', p_gel)

    def p_nucleo(tw, th, cara_, s):
        """El nucleo: la gelatina espesa, mas oscura, en manchas de dos pixeles y con el canto oscuro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = 2 - (((xs // 2) * 7 + (ys // 2) * 5 + s) % 5 == 0).astype(int) + (((xs // 2) * 3 + (ys // 2) * 11 + s) % 7 == 0)
        idx[(xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)] = 0
        t = _pinta(np.clip(idx, 0, 3), nuc)
        return t, None
    reg('nucleo', p_nucleo)

    def ojo(lado):
        def f(tw, th, cara_, s):
            """El ojo: la cuenca oscura cortada en diagonal por arriba (baja hacia la nariz: el ceño) y dentro la
            pupila rasgada que brilla, con el centro claro."""
            ys, xs = np.mgrid[0:th, 0:tw]
            idx = np.zeros((th, tw), int)
            if cara_ != 'frente':
                return _pinta(idx, nuc), None
            dentro = xs if lado > 0 else (tw - 1 - xs)                           # 0 en el lado de la nariz
            corte = ys < (th * 0.6) * (1 - dentro / max(tw - 1, 1))               # la diagonal del ceño
            pup = (ys >= th // 2 - 1) & (ys <= th // 2) & (dentro >= 1) & (dentro <= tw - 2)
            centro = pup & (dentro >= tw // 2 - 1) & (dentro <= tw // 2)
            t = np.zeros((th, tw, 4), np.uint8)
            t[...] = (*nuc[0], 255)
            t[pup] = (*bri[0], 255)
            t[centro] = (*bri[1], 255)
            t[corte] = 0
            return t, _emis(t, pup, 255)
        return f
    reg('ojo_izq', ojo(-1))
    reg('ojo_der', ojo(1))

    def p_ceno(tw, th, cara_, s):
        return _pinta(np.zeros((th, tw), int), nuc), None
    reg('ceno', p_ceno)

    def p_diente(tw, th, cara_, s):
        """El diente de gelatina dura, en hoja: la base arriba y la punta abajo, claro a un lado y oscuro al otro."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            w = tw * (th - y) / th
            a, b = (tw - w) / 2, (tw + w) / 2
            for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                t[y, x] = (*(die[2] if x < tw / 2 else die[1]), 255)
        return t, None
    reg('diente', p_diente)

    def p_boca(tw, th, cara_, s):
        """La boca: oscura, con la garganta que brilla al fondo (en el Tragón) y los dientes dibujados en hoja arriba y
        abajo, en sierra (en el Erizo y el Fundido)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*nuc[0], 255)
        luz = np.zeros((th, tw), bool)
        if tipo == 'tragon':
            luz = ((xs + ys * 2 + s) % 9 == 0) | ((ys >= th - 3) & ((xs + s) % 5 == 0))
            t[luz] = (*bri[0], 255)
            return t, _emis(t, luz, 150)
        if cara_ != 'frente':
            return t, None
        paso = 3
        diente_arr = ys < (1 - np.abs((xs % paso) - 1)) + 1                     # la fila de arriba, en sierra
        diente_aba = (th - 1 - ys) < (1 - np.abs(((xs + 1) % paso) - 1)) + 1
        hueco = ~(diente_arr | diente_aba)
        if tipo == 'fundido':
            luz = hueco & (np.abs(ys - th // 2) <= 0)
            t[hueco] = (*nuc[1], 255)
            t[luz] = (*bri[0], 255)
        t[diente_arr | diente_aba] = (*die[1], 255)
        t[(diente_arr | diente_aba) & (xs % paso == 0)] = (*die[2], 255)
        esquina = np.minimum(xs, tw - 1 - xs)
        t[ys > esquina + (th - 3)] = 0                                          # la mueca: las esquinas de abajo
        return t, (_emis(t, luz, 255) if tipo == 'fundido' else None)
    reg('boca', p_boca)

    def p_garganta(tw, th, cara_, s):
        """El fondo de la boca del Tragón: oscura, con el brillo verde que sale de dentro, mas fuerte abajo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys >= th * 0.55, 1, 0)
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*nuc[0], 255)
        t[idx == 1] = (*nuc[2], 255)
        luz = (ys >= th * 0.55) & (((xs // 2) + (ys // 2) + s) % 3 == 0)
        t[luz] = (*bri[0], 255)
        return t, _emis(t, luz | (idx == 1), 120)
    reg('garganta', p_garganta)

    def p_charco_gel(tw, th, cara_, s):
        """El charco de gelatina: mas oscuro que el cubo, liso, con el borde un tono mas claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx[(xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)] = 3
        return _pinta(idx, gel), None
    reg('charco_gel', p_charco_gel)

    def p_baba(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        return _pinta(np.where(xs == 0, 5, 4), gel), None
    reg('baba', p_baba)

    def p_acido(tw, th, cara_, s):
        """El acido del Fundido: verde limon que brilla, con vetas claras."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*bri[0], 255)
        t[((xs + ys * 2 + s) % 7) == 0] = (*bri[1], 255)
        return t, _emis(t, np.ones((th, tw), bool), 230)
    reg('acido', p_acido, pleno=True)

    def p_charco(tw, th, cara_, s):
        """El charco de acido: liso, que brilla poco, con alguna onda larga y limpia que brilla mas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*nuc[2], 255)
        rng = random.Random(s)
        onda = np.zeros((th, tw), bool)
        for _ in range(max(1, tw * th // 160)):
            x, y = rng.randrange(tw), rng.randrange(th)
            onda[y, x:x + rng.choice((3, 4, 5))] = True
        t[onda] = (*bri[0], 255)
        return t, _emis(t, np.ones((th, tw), bool), 90)
    reg('charco', p_charco)

    def p_hierro(tw, th, cara_, s):
        """El hierro de las hojas: el filo claro a un lado, el vaceo oscuro en medio a lo largo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        if tw >= 3:
            idx[:, 0] = 5
            idx[:, tw - 1] = 2
            idx[:, tw // 2] = 4
        elif tw == 2:
            idx[:, 0] = 5
        return _pinta(idx, HIERRO), None
    reg('hierro', p_hierro)

    def p_hierro_o(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs + ys) % 5 == 0, 3, 2)
        idx[(xs == 0) | (ys == 0)] = 4
        return _pinta(idx, HIERRO), None
    reg('hierro_o', p_hierro_o)

    def p_madera(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs + s) % 3 == 0, 1, 2)
        idx[(ys + s) % 5 == 0] = 3
        return _pinta(idx, MADERA), None
    reg('madera', p_madera)

    def p_escudo(tw, th, cara_, s):
        """El escudo: tablas de madera con el canto de hierro y el umbo en medio."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = _pinta(np.where(xs % 4 == 0, 1, np.where(xs % 4 == 1, 3, 2)), MADERA)
        canto = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)
        t[canto] = (*HIERRO[3], 255)
        cx, cy = tw // 2, th // 2
        umbo = (np.abs(xs - cx + 0.5) <= 1) & (np.abs(ys - cy + 0.5) <= 1)
        t[umbo] = (*HIERRO[4], 255)
        return t, None
    reg('escudo', p_escudo)

    def p_pluma(tw, th, cara_, s):
        """Las plumas de la flecha, en hoja a los dos lados del asta: blancas con el canto gris, cortadas en diagonal
        por arriba."""
        ys, xs = np.mgrid[0:th, 0:tw]
        m = (tw - 1) / 2
        t = _pinta(np.where((xs == 0) | (xs == tw - 1), 1, 2), PLUMA)
        t[ys < np.abs(xs - m) - 0.5] = 0
        return t, None
    reg('pluma', p_pluma)

    def p_hueso(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        idx[:, 0] = 4
        idx[:, -1] = 1
        if tipo == 'fundido':                                                    # comidos por el acido
            idx[(xs + ys * 3 + s) % 7 == 0] = 0
        return _pinta(idx, HUESO), None
    reg('hueso', p_hueso)
    return P


# ----------------------------------------------------------------------
#  Las piezas
# ----------------------------------------------------------------------
def marco_y(p, d, frente=(0.0, 0.0, 1.0)):
    """Un marco en p con el eje y hacia d."""
    y = _u(d)
    f = np.asarray(frente, float)
    if abs(f @ y) > 0.95:
        f = np.array((1.0, 0.0, 0.0))
    x = _u(np.cross(y, f))
    z = np.cross(x, y)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p
    return M


def hoja(out, P4, pintor, ancho, alto, semilla=0):
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def diente(out, P, M, x, z, largo, ancho, hacia=-1.0, semilla=0):
    """Un diente en dos hojas cruzadas, desde (x, 0, z) del marco M hacia abajo (hacia=-1) o hacia arriba (+1)."""
    base = pt(M, (x, 0.0, z))
    eje = M[:3, :3] @ np.array((0.0, hacia, 0.0))
    for ll in (M[:3, :3] @ np.array((1.0, 0.0, 0.0)), M[:3, :3] @ np.array((0.0, 0.0, 1.0))):
        a, b = base - ll * ancho / 2, base + ll * ancho / 2
        punta = base + eje * largo
        hoja(out, (punta - ll * 0.05, punta + ll * 0.05, b, a), P['diente'], ancho, largo, semilla)   # la base, arriba en la textura


def cara(out, P, M, y, z, ancho_ojo=6.0, alto_ojo=4.0, sep=6.6, boca=None):
    """La cara de monstruo dentro de la gelatina (en el marco M, mirando a +z): los dos ojos rasgados con el ceño en uve
    encima y, si se pide, la boca (x0, y0, ancho, alto)."""
    for lado, nombre in ((-1, 'ojo_izq'), (1, 'ojo_der')):
        cx = lado * sep
        bm.cubo(out, M, cx - ancho_ojo / 2, y, z - 1.0, ancho_ojo, alto_ojo, 1.0, P[nombre], semilla=2)
        Mc = M @ vr.T(cx + lado * 0.4, y + alto_ojo + 0.9, z - 0.9) @ vr.Rz(lado * 0.36)  # el ceño, en uve
        bm.cubo(out, Mc, -ancho_ojo * 0.62, -0.8, 0.0, ancho_ojo * 1.24, 1.6, 1.0, P['ceno'], semilla=3)
    if boca is not None:
        x0, y0, w, h = boca
        bm.cubo(out, M, x0, y0, z - 1.0, w, h, 1.0, P['boca'], semilla=4)


def gelatina(gel, P, M, x0, y0, z0, w, h, d, caras=None, semilla=0):
    bm.cubo(gel, M, x0, y0, z0, w, h, d, P['gel'], caras=caras, semilla=semilla)


def hueso(out, P, a, b, grosor=1.0, semilla=0):
    """Un hueso de a a b: la cana y los dos nudillos de las puntas."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    M = marco_y(a, b - a)
    L = float(np.linalg.norm(b - a))
    bm.cubo(out, M, -grosor / 2, 0.0, -grosor / 2, grosor, L, grosor, P['hueso'], semilla=semilla)
    for yy in (0.0, L):
        bm.cubo(out, M, -grosor, yy - grosor * 0.7, -grosor * 0.7, grosor * 2, grosor * 1.4, grosor * 1.4, P['hueso'],
                semilla=semilla + 1)


def yelmo(out, P, M):
    """Un yelmo de hierro: el casco, el borde y la visera con su raja."""
    bm.cubo(out, M, -3.0, 0.0, -3.0, 6.0, 4.0, 6.0, P['hierro_o'], semilla=1)
    bm.cubo(out, M, -3.4, 0.0, -3.4, 6.8, 1.0, 6.8, P['hierro_o'], semilla=2)
    bm.cubo(out, M, -2.0, 1.4, 2.8, 4.0, 0.6, 0.6, P['ceno'], semilla=3)


def espada(out, P, punta, mango, ancho=2.2, semilla=0):
    """Una espada de la punta (clavada) a la empunadura: la hoja, la guarda, el puno y el pomo."""
    punta, mango = np.asarray(punta, float), np.asarray(mango, float)
    d = mango - punta
    L = float(np.linalg.norm(d))
    M = marco_y(punta, d)
    hoja_l = L - 5.0
    bm.cubo(out, M, -ancho / 2, 0.0, -0.4, ancho, hoja_l, 0.8, P['hierro'], semilla=semilla)
    bm.cubo(out, M, -3.2, hoja_l, -0.8, 6.4, 1.2, 1.6, P['hierro_o'], semilla=semilla + 1)
    bm.cubo(out, M, -0.7, hoja_l + 1.2, -0.7, 1.4, 3.4, 1.4, P['madera'], semilla=semilla + 2)
    bm.cubo(out, M, -1.1, hoja_l + 4.6, -1.1, 2.2, 1.8, 2.2, P['hierro_o'], semilla=semilla + 3)


def flecha(out, P, punta, cola, semilla=0):
    """Una flecha clavada: el asta y las plumas en cruz en la cola (la punta queda dentro)."""
    punta, cola = np.asarray(punta, float), np.asarray(cola, float)
    d = cola - punta
    L = float(np.linalg.norm(d))
    M = marco_y(punta, d)
    bm.cubo(out, M, -0.45, 0.0, -0.45, 0.9, L, 0.9, P['madera'], semilla=semilla)
    bm.cubo(out, M, -0.9, 0.0, -0.9, 1.8, 1.6, 1.8, P['hierro_o'], semilla=semilla)
    for g in (0.0, math.pi / 2):
        ll = M[:3, :3] @ np.array((math.cos(g), 0.0, math.sin(g)))
        eje = M[:3, :3] @ np.array((0.0, 1.0, 0.0))
        b = pt(M, (0.0, L - 4.0, 0.0))
        hoja(out, (b - ll * 1.8, b + ll * 1.8, b + ll * 1.8 + eje * 3.8, b - ll * 1.8 + eje * 3.8), P['pluma'], 3.6, 3.8,
             semilla)


def hacha(out, P, cabeza, cola, semilla=0):
    """Un hacha clavada de filo: el mango y la cabeza de hierro."""
    cabeza, cola = np.asarray(cabeza, float), np.asarray(cola, float)
    M = marco_y(cabeza, cola - cabeza)
    L = float(np.linalg.norm(cola - cabeza))
    bm.cubo(out, M, -0.5, -1.0, -0.5, 1.0, L + 1.0, 1.0, P['madera'], semilla=semilla)
    bm.cubo(out, M, -0.6, -1.4, -4.2, 1.2, 3.6, 3.6, P['hierro_o'], semilla=semilla + 1)
    bm.cubo(out, M, -0.4, -2.2, -5.6, 0.8, 5.2, 1.6, P['hierro'], semilla=semilla + 2)


def lanza(out, P, punta, cola, semilla=0):
    punta, cola = np.asarray(punta, float), np.asarray(cola, float)
    M = marco_y(punta, cola - punta)
    L = float(np.linalg.norm(cola - punta))
    bm.cubo(out, M, -0.45, 0.0, -0.45, 0.9, L, 0.9, P['madera'], semilla=semilla)
    bm.cubo(out, M, -0.7, L - 1.0, -0.7, 1.4, 1.0, 1.4, P['hierro_o'], semilla=semilla)


def escudo(out, P, centro, giro, inclina, semilla=0):
    M = vr.T(*centro) @ vr.Ry(giro) @ vr.Rx(inclina)
    bm.cubo(out, M, -4.5, -5.5, -0.5, 9.0, 11.0, 1.0, P['madera'], caras={'frente': P['escudo'], 'atras': P['escudo']},
            semilla=semilla)


# ----------------------------------------------------------------------
#  Los tres
# ----------------------------------------------------------------------
W_, H_, D_ = 30.0, 26.0, 30.0          # el cubo de gelatina, en pixeles


def charco(gel, P, semilla=0, pintor=None):
    """El charco que deja: tres losas finas de gelatina, unas sobre otras, para que el borde no sea un cuadrado."""
    for (x0, z0, w, d) in ((-17.0, -16.0, 34.0, 33.0), (-6.0, 15.0, 14.0, 4.0), (9.0, 13.0, 5.0, 3.0),
                           (-19.0, -4.0, 3.0, 10.0), (16.0, -9.0, 3.0, 7.0)):
        bm.cubo(gel, vr.T(0, 0, 0), x0, 0.02, z0, w, 0.3, d, pintor or P['charco_gel'], caras={'abajo': None},
                semilla=semilla)


def tragon(out, gel, P, V):
    """El Tragón: el cubo se abre en dos como unas fauces (la parte de arriba se levanta por delante, con la bisagra
    detras), con los dientes de gelatina dura, las babas, la garganta que brilla y, dentro, lo que se ha tragado."""
    hy = 9.0
    gelatina(gel, P, vr.T(0, 0, 0), -W_ / 2, 0.0, -D_ / 2, W_, hy, D_, semilla=1)          # la quijada
    Mu = vr.T(0.0, hy, -D_ / 2) @ vr.Rx(-16 * D) @ vr.T(0.0, -hy, D_ / 2)               # la de arriba, levantada
    gelatina(gel, P, Mu, -W_ / 2, hy, -D_ / 2, W_, H_ - hy, D_, semilla=2)
    gelatina(gel, P, vr.T(0, 0, 0), -W_ / 2 + 0.5, hy - 0.5, -D_ / 2 + 0.5, W_ - 1.0, 4.0, 7.0,  # la bisagra
             caras={'abajo': None}, semilla=3)
    bm.cubo(out, vr.T(0, 0, 0), -13.0, hy - 0.4, -13.0, 26.0, 6.0, 18.0, P['garganta'], semilla=4)  # la garganta
    for x in (-12.0, -8.4, -4.8, -1.2, 2.4, 6.0, 9.6, 12.6):                             # los dientes de arriba
        diente(out, P, Mu @ vr.T(0.0, hy, 0.0), x, D_ / 2 - 1.2, 4.6 if abs(x) > 9 else 3.6, 2.2, -1.0, semilla=5)
    for x in (-10.4, -6.6, -3.0, 0.6, 4.2, 7.8, 11.2):                                   # los de abajo
        diente(out, P, vr.T(0.0, hy, 0.0), x, D_ / 2 - 1.2, 3.4 if abs(x) > 9 else 2.6, 2.0, 1.0, semilla=6)
    for x, alto in ((-9.0, 7.0), (3.5, 7.8), (10.5, 6.6)):                               # las babas
        bm.cubo(gel, vr.T(0, 0, 0), x, hy, D_ / 2 - 3.0, 1.0, alto, 1.0, P['baba'], semilla=7)
    cara(out, P, Mu, 17.0, D_ / 2 - 1.0, ancho_ojo=6.4, alto_ojo=4.2, sep=7.0)            # la cara, arriba
    bm.cubo(out, Mu, -11.0, 12.5, -8.0, 22.0, 11.5, 14.0, P['nucleo'], semilla=8)        # el nucleo, detras de la cara
    hueso(out, P, (-11.0, 2.5, -6.0), (-3.0, 4.5, 4.0), 1.2, semilla=9)                    # lo que se ha tragado
    hueso(out, P, (4.0, 2.0, -9.0), (11.0, 3.0, 2.0), 1.0, semilla=10)
    yelmo(out, P, vr.T(8.0, 12.5, -8.0) @ vr.Rz(0.5) @ vr.Ry(0.6))
    hueso(out, P, pt(Mu, (-12.0, 16.0, -10.0)), pt(Mu, (-9.0, 23.0, -4.0)), 1.0, semilla=11)
    return pt(Mu, (0.0, 19.0, D_ / 2)), np.array((0.0, hy + 2.0, 6.0))


def erizo(out, gel, P, V):
    """El Erizo: el cubo cerrado, con la sonrisa de dientes, y clavadas por todas partes las armas de los que no
    pudieron con el."""
    gelatina(gel, P, vr.T(0, 0, 0), -W_ / 2, 0.0, -D_ / 2, W_, H_, D_, semilla=1)
    cara(out, P, vr.T(0, 0, 0), 15.0, D_ / 2 - 1.0, ancho_ojo=6.4, alto_ojo=4.2, sep=7.0,
         boca=(-9.0, 5.0, 18.0, 6.0))
    bm.cubo(out, vr.T(0, 0, 0), -11.0, 4.0, -9.0, 22.0, 18.0, 14.0, P['nucleo'], semilla=8)
    # las espadas: arriba, de canto a un lado y detras
    espada(out, P, (-6.0, 18.0, -2.0), (-10.0, 37.0, -7.0), semilla=10)
    espada(out, P, (9.0, 16.0, 6.0), (20.0, 31.0, 10.0), semilla=12)
    espada(out, P, (2.0, 14.0, -10.0), (6.0, 30.0, -24.0), semilla=14)
    # las flechas
    for punta, cola in (((13.0, 18.0, 8.0), (24.0, 21.0, 13.0)), ((12.0, 9.0, -4.0), (24.0, 11.0, -5.0)),
                        ((-12.0, 20.0, 4.0), (-24.0, 25.0, 8.0)), ((3.0, 22.0, 2.0), (6.0, 34.0, 7.0)),
                        ((-8.0, 12.0, 12.0), (-14.0, 15.0, 23.0))):
        flecha(out, P, punta, cola, semilla=20)
    lanza(out, P, (-4.0, 12.0, -8.0), (-22.0, 30.0, -20.0), semilla=30)                   # una lanza, detras
    hacha(out, P, (7.0, 24.0, -3.0), (9.0, 33.0, -8.0), semilla=40)                      # un hacha en lo alto
    escudo(out, P, (-15.0, 8.0, 3.0), 1.2, 0.25, semilla=50)                              # el escudo, hundido de canto
    return np.array((0.0, 17.0, D_ / 2)), np.array((0.0, 14.0, -3.0))


def fundido(out, gel, P, V):
    """El Fundido: la gelatina negra que se derrite (chorretones que bajan por los lados desde arriba y gotas que
    cuelgan), el charco de acido que brilla, las burbujas que suben, el nucleo encendido y los ojos que lloran acido."""
    rng = random.Random(7)
    gelatina(gel, P, vr.T(0, 0, 0), -W_ / 2, 0.0, -D_ / 2, W_, H_, D_, semilla=1)
    # los goterones: cortos, desde el labio de arriba, tres por lado
    for lado in (0, 1, 3):                                                                # (detras no: se veria a traves)
        M = vr.Ry(lado * math.pi / 2)
        for x, largo in rng.sample(((-11.0, 3.0), (-5.0, 5.0), (1.0, 2.0), (6.0, 4.0), (10.0, 3.0)), 3):
            bm.cubo(gel, M, x, H_ - 2.0 - largo, D_ / 2, 3.0, largo, 1.0, P['gel'], caras={'atras': None}, semilla=lado + 2)
    # el labio de arriba, que se escurre por el borde
    bm.cubo(gel, vr.T(0, 0, 0), -W_ / 2 - 0.6, H_ - 2.0, -D_ / 2 - 0.6, W_ + 1.2, 2.0, D_ + 1.2, P['gel'], semilla=9)
    # el charco de acido, en losas
    for (x0, z0, w, d) in ((-18.0, -17.0, 36.0, 35.0), (-21.0, -8.0, 42.0, 16.0), (-10.0, 15.0, 22.0, 6.0),
                           (8.0, 14.0, 9.0, 8.0), (-22.0, 6.0, 6.0, 7.0)):
        bm.cubo(out, vr.T(0, 0, 0), x0, 0.0, z0, w, 0.3, d, P['charco'], caras={'abajo': None}, semilla=10)
    cara(out, P, vr.T(0, 0, 0), 15.0, D_ / 2 - 1.0, ancho_ojo=6.4, alto_ojo=4.2, sep=7.0,
         boca=(-7.5, 5.5, 15.0, 5.0))
    for lado in (-1, 1):                                                                  # las lagrimas de acido
        bm.cubo(out, vr.T(0, 0, 0), lado * 7.0 + lado * 1.4, 12.4, D_ / 2 - 1.6, 0.8, 2.6, 0.6, P['acido'], semilla=11)
    bm.cubo(out, vr.T(0, 0, 0), -10.0, 4.0, -9.0, 20.0, 17.0, 14.0, P['nucleo'], semilla=8)  # el nucleo, que arde poco
    for k in range(10):                                                                   # las burbujas que suben
        x, z = rng.uniform(-11, 11), rng.uniform(-11, 9)
        y = rng.uniform(2, 23)
        if abs(x) < 12.5 and z > -10:
            continue
        g = rng.choice((1.0, 1.0, 1.6, 2.2))
        bm.cubo(out, vr.T(x, y, z), -g / 2, -g / 2, -g / 2, g, g, g, P['acido'], semilla=12)
    hueso(out, P, (-17.0, 0.4, 10.0), (-9.0, 1.2, 18.0), 1.2, semilla=13)                # huesos comidos en el charco
    hueso(out, P, (12.0, 0.4, 14.0), (19.0, 0.8, 8.0), 1.0, semilla=14)
    return np.array((0.0, 17.0, D_ / 2)), np.array((0.0, 14.0, -3.0))


DISENOS = {'A': tragon, 'B': erizo, 'C': fundido}


def slime(tipo='A'):
    """El slime: (lo opaco, la gelatina, info). La gelatina se pinta translucida despues de lo opaco."""
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out, gel = [], []
    try:
        cara_p, nuc = DISENOS[tipo](out, gel, P, V)
        if tipo != 'C':
            charco(gel, P, semilla=20)
    finally:
        bm.PPB = ppb
    k = V['escala'] / 16.0
    E = np.diag([k, k, k, 1.0])
    out, gel = qm.transformar(out, E), qm.transformar(gel, E)
    return out, gel, {'cabeza': pt(E, cara_p), 'nucleo': pt(E, nuc), 'luces': [pt(E, nuc)], 'luz': V['luz'],
                      'transl': V['transl'], 'brilla': tipo == 'C'}


# ----------------------------------------------------------------------
#  El Slime de vanilla, dibujado aqui con su paleta, para la foto de escala
# ----------------------------------------------------------------------
def vanilla_a_escala():
    """El Slime grande de vanilla (tamano 4, 2 bloques): el cubo de 8 x 8 x 8 translucido, el nucleo de 6 x 6 x 6, los
    ojos de 2 x 2 y la boca de 1 x 1, con la paleta verde de vanilla."""
    VERDE = _h('4a8a3a', '5aa648', '74c05c', '8cd472', 'a8e48a')
    OSC = _h('1e3a16', '2c4c22')

    def gel_v(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs + ys * 3 + s) % 5 == 0, 3, 2)
        idx[(xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)] = 4
        return _pinta(idx, VERDE), None

    def nuc_v(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        return _pinta(np.where((xs + ys + s) % 4 == 0, 0, 1), VERDE), None

    def osc_v(tw, th, cara_, s):
        return _pinta(np.zeros((th, tw), int), OSC), None
    gel_v.__name__, nuc_v.__name__, osc_v.__name__ = 'slV_gel', 'slV_nuc', 'slV_osc'
    ppb = bm.PPB
    bm.PPB = PPB
    out, gel = [], []
    try:
        bm.cubo(gel, vr.T(0, 0, 0), -4.0, 0.0, -4.0, 8.0, 8.0, 8.0, gel_v, semilla=1)
        bm.cubo(out, vr.T(0, 0, 0), -3.0, 1.0, -3.0, 6.0, 6.0, 6.0, nuc_v, semilla=2)
        for sx in (-1, 1):
            bm.cubo(out, vr.T(0, 0, 0), sx * 2.3 - 1.0, 4.0, 2.5, 2.0, 2.0, 1.0, osc_v, semilla=3)
        bm.cubo(out, vr.T(0, 0, 0), -1.5, 2.0, 2.5, 1.0, 1.0, 1.0, osc_v, semilla=4)
    finally:
        bm.PPB = ppb
    E = np.diag([0.25, 0.25, 0.25, 1.0])
    return qm.transformar(out, E), qm.transformar(gel, E)


# ----------------------------------------------------------------------
#  El dibujo: lo opaco y despues la gelatina, de atras a delante
# ----------------------------------------------------------------------
_MASCARA = np.full((1, 1, 4), 255, np.uint8)
qm._reg('sl_mascara', _MASCARA)


def dibujar(lz, cam, qs, gel, luces, ambiente, niebla=None, brillo=1.4, transl=0.5, brilla=False):
    """Lo opaco como siempre; la gelatina, translucida y de atras a delante. Al final la gelatina se apunta en la
    profundidad, para que el contorno blanco la abrace."""
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)
    lejos = sorted(gel, key=lambda q: -float(np.linalg.norm(np.mean(q[0], axis=0) - cam.ojo)))
    for P, UV, mat in lejos:
        tex = qm.MAT[mat]
        luz = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, ambiente) * 1.15
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, None, niebla, brillo=brillo,
                         translucido=transl)
        if brilla and mat in qm.EMIS:
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], qm.EMIS[mat], np.ones(3), None, niebla,
                             aditivo=True, brillo=0.35)
    # la profundidad de la gelatina, para el contorno
    tmp = vr.Lienzo(lz.W, lz.H)
    tmp.z = lz.z.copy()
    for P, UV, mat in gel:
        for tri in ((0, 1, 2), (0, 2, 3)):
            tmp.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], _MASCARA, np.ones(3))
    lz.z = np.minimum(lz.z, tmp.z)

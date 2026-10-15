"""
El Trasgo (15-10-2026): el mob que se te aferra al cuerpo. Juan, del Izador: «se ve raro y su cara no me gusto; la
mecanica es buena, pero se siente falso»; y «sigamos con los mobs que hacen algo al jugador». De su lista quedaban el
que te traga y el que se te aferra al cuerpo.

El trasgo de las leyendas de Asturias y Cantabria, pero nuestro: un duendecillo flaco y encorvado, de cabeza grande, con
el gorro rojo, las orejas largas en punta, la nariz ganchuda, los ojos rasgados que brillan y una sonrisa de dientes; los
brazos muy largos con garras para agarrarse; y, como en la leyenda, un agujero en la palma de la mano izquierda. Te salta
encima y no te suelta:

    A  el Colgon    gris verdoso, con la cola larga de gancho y la cresta de puas en la nuca: se te cuelga de la espalda,
                    abrazado al cuello; pesa (no corres ni saltas) y te muerde
    B  el Jinete    palido, de cueva, con dos cuernecillos y los dedos muy largos: se te sube a los hombros, te tapa los
                    ojos con las manos y te lleva caminando hacia la lava o el barranco
    C  el Ladron    rojizo, de orejas enormes, con el saco del botin a la espalda: se te cuelga del brazo, te arranca lo
                    que llevas en la mano y huye con ello

Se modela como un mob, en pixeles del jugador (16 por bloque), con un texel por pixel. Esta articulado: la postura
dice donde van la pelvis, el giro del cuerpo y de la cabeza, y los codos, las manos, las rodillas y los pies.
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
    'A': dict(clave='TRA', nombre='el Colgón', corto='colgon',
              piel=_h('141c14', '1e2a1e', '2c3c2a', '3e5238', '566c48'),
              gorro=_h('3a0a0a', '5c1210', '82201a', 'a83024', 'c84a34'),
              ojo=_h('ffb43a', 'fff0b0'), boca=_h('ff8a2a', 'ffd890'), una=_h('140e0a', '2a2018', '4a3a2a', '8a7458')),
    'B': dict(clave='TRB', nombre='el Jinete', corto='jinete',
              piel=_h('22262c', '383e46', '525a62', '6e7880', '8c989e'),
              gorro=_h('3a0a10', '5c1218', '822028', 'a83038', 'c84a4a'),
              ojo=_h('6ae8ff', 'e0faff'), boca=_h('3ac8ff', 'c8f4ff'), una=_h('1a1612', '2e2822', '4e463a', '9a8e76')),
    'C': dict(clave='TRC', nombre='el Ladrón', corto='ladron',
              piel=_h('2a120c', '42201a', '5c3024', '7a4430', '985a3e'),
              gorro=_h('0e0c0c', '1a1616', '2a2222', '3a3030', '4e4240'),
              ojo=_h('a4ff4a', 'eaffc0'), boca=_h('8aff3a', 'd8ffa0'), una=_h('140e0a', '2a2018', '4a3a2a', '8a7458')),
}
DIENTE = _h('8a8068', 'c8bea0', 'f0ead6')
SACO = _h('2a1e10', '3e2e1a', '584226', '725834', '8c7044')
ORO = _h('8a5a0a', 'c88a14', 'f0c030', 'fff07a')


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _pinta(idx, rampa):
    th, tw = idx.shape
    t = np.zeros((th, tw, 4), np.uint8)
    for k, c in enumerate(rampa):
        t[idx == k] = (*c, 255)
    t[idx < 0] = 0
    return t


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    piel, gorro, ojo, boca, una = V['piel'], V['gorro'], V['ojo'], V['boca'], V['una']

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'tr%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def p_piel(tw, th, cara_, s):
        """La piel: lisa, con la fila de arriba un tono mas clara y la de abajo mas oscura, y una arruga cada cinco
        filas (en los brazos y el cuerpo se leen como tendones y costillas)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        if cara_ not in ('arriba', 'abajo'):
            idx[(ys % 5) == 3] = 1
            idx[0, :] = 3
            idx[th - 1, :] = 1
        elif cara_ == 'arriba':
            idx[...] = 3
        else:
            idx[...] = 1
        return _pinta(idx, piel), None
    reg('piel', p_piel)

    def p_palma(tw, th, cara_, s):
        """La palma de la mano izquierda, con el agujero de la leyenda."""
        idx = np.full((th, tw), 2)
        idx[th // 2 - 1:th // 2 + 1, tw // 2 - 1:tw // 2 + 1] = 0
        return _pinta(idx, piel), None
    reg('palma', p_palma)

    def p_gorro(tw, th, cara_, s):
        """El gorro rojo de lana: los pliegues en rayas oscuras cada tres pixeles y el borde de abajo vuelto, mas
        claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs % 3) == 0, 1, 2)
        idx[ys == 0] = 3
        if cara_ in ('arriba', 'abajo'):
            idx = np.full((th, tw), 2)
        return _pinta(idx, gorro), None
    reg('gorro', p_gorro)

    def p_borde(tw, th, cara_, s):
        """El borde vuelto del gorro: mas claro, con la costura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs % 2) == 0, 3, 4)
        return _pinta(idx, gorro), None
    reg('borde', p_borde)

    def p_ojo(tw, th, cara_, s):
        """El ojo rasgado: la cuenca oscura cortada en diagonal arriba (el ceño), el iris que brilla y la pupila de raja
        en medio."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*piel[0], 255)
        if cara_ != 'frente':
            return t, None
        iris = (ys >= 1) & (ys <= th - 1) & (xs >= 0) & (xs <= tw - 1)
        t[iris] = (*ojo[0], 255)
        t[(ys == th // 2) & (xs > 0) & (xs < tw - 1)] = (*ojo[1], 255)
        t[(xs == tw // 2)] = (*piel[0], 255)                                      # la pupila de raja
        return t, _emis(t, iris & (xs != tw // 2), 255)
    reg('ojo', p_ojo)

    def p_boca(tw, th, cara_, s):
        """La boca por dentro: oscura (las encias), con el brillo del neon solo en una raja al fondo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (30, 8, 10, 255)
        raja = (ys == th // 2) & (xs > tw // 6) & (xs < tw - 1 - tw // 6)
        t[raja] = (*boca[0], 255)
        return t, _emis(t, raja, 140)
    reg('boca', p_boca)

    def p_diente(tw, th, cara_, s):
        """El diente en hoja: la base arriba y la punta abajo, claro a un lado y oscuro al otro."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            w = tw * (th - y) / th
            a, b = (tw - w) / 2, (tw + w) / 2
            for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                t[y, x] = (*(DIENTE[2] if x < tw / 2 else DIENTE[1]), 255)
        return t, None
    reg('diente', p_diente)

    def p_una(tw, th, cara_, s):
        """La garra: cuerno oscuro, con la punta (abajo) mas clara."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys >= th - max(1, th // 3), 3, np.where(xs == 0, 2, 1))
        return _pinta(idx, una), None
    reg('una', p_una)

    def p_oreja(tw, th, cara_, s):
        """La oreja en hoja, en punta (la punta a la derecha de la textura): la piel por fuera y por dentro mas oscura,
        con el borde claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        alto = (th / 2) * (1 - xs / max(tw, 1)) ** 0.9
        dentro = np.abs(ys - (th - 1) / 2) <= alto
        borde = dentro & (np.abs(ys - (th - 1) / 2) > alto - 1)
        t[dentro] = (*piel[1], 255)
        t[borde] = (*piel[3], 255)
        return t, None
    reg('oreja', p_oreja)

    def p_trapo(tw, th, cara_, s):
        """El taparrabos: tela vieja oscura, en rayas, con el borde de abajo deshilachado."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = _pinta(np.where((xs % 3) == 0, 0, 1), SACO)
        t[(ys == th - 1) & ((xs % 2) == 0)] = 0
        return t, None
    reg('trapo', p_trapo)

    def p_saco(tw, th, cara_, s):
        """El saco del botin: arpillera con la trama en cuadros y los remiendos cosidos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs % 2) + (ys % 2)) == 1, 2, 3)
        idx[(ys % 5) == 0] = 1
        return _pinta(idx, SACO), None
    reg('saco', p_saco)

    def p_oro(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs + ys) % 3 == 0, 3, 2)
        t = _pinta(idx, ORO)
        return t, _emis(t, idx == 3, 120)
    reg('oro', p_oro)
    return P


# ----------------------------------------------------------------------
#  Las piezas
# ----------------------------------------------------------------------
def hoja(out, P4, pintor, ancho, alto, semilla=0):
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def hueso(out, a, b, grosor, pintor, caras=None, semilla=0):
    """Un tramo de miembro de a a b (una caja de seccion cuadrada, que se solapa un poco en las juntas)."""
    bm.viga(out, a, b, grosor, grosor, pintor, extra=grosor * 0.3, caras=caras, semilla=semilla)


def garra(out, P, base, eje, lateral, largo, semilla=0):
    """Una garra curva: tres tramos que se doblan hacia la palma."""
    eje, lateral = _u(eje), _u(lateral)
    palma = _u(np.cross(lateral, eje))
    pts = [np.asarray(base, float)]
    d = eje
    for k in range(3):
        pts.append(pts[-1] + d * largo / 3)
        d = _u(d + palma * 0.55)
    for a, b in zip(pts[:-1], pts[1:]):
        bm.viga(out, a, b, 0.7, 0.7, P['una'], extra=0.2, semilla=semilla)


def mano(out, P, codo, muneca, lado, abierta=1.0, izquierda=False, largos=(4.0, 4.6, 4.0), semilla=0):
    """La mano: la palma (con el agujero en la izquierda) y tres dedos largos con garra, abiertos en abanico."""
    eje = _u(np.asarray(muneca, float) - np.asarray(codo, float))
    lat = _u(np.cross(eje, np.array((0.0, 1.0, 0.0))) if abs(eje[1]) < 0.9 else np.array((1.0, 0.0, 0.0)))
    M = bm.em.marco(np.asarray(muneca, float), eje, up=np.cross(lat, eje))
    bm.cubo(out, M, -1.8, -0.9, 0.0, 3.6, 1.8, 3.0, P['piel'],
            caras={'abajo': P['palma']} if izquierda else None, semilla=semilla)
    for k, dx in enumerate((-1.3, 0.0, 1.3)):
        b = pt(M, (dx, 0.0, 2.8))
        ej = M[:3, :3] @ _u((dx * 0.18 * abierta, 0.0, 1.0))
        L = largos[k]
        p1 = b + ej * L * 0.55
        bm.viga(out, b, p1, 0.9, 0.9, P['piel'], extra=0.2, semilla=semilla + 1)
        garra(out, P, p1, ej, M[:3, 0], L * 0.7, semilla=semilla + 2)


def cabeza(out, P, V, M, abre=0.35):
    """La cabeza grande: el craneo, el ceño, los pomulos, la nariz ganchuda, los ojos rasgados que brillan, la boca de
    oreja a oreja con los dientes en hoja y la quijada un poco abierta, las orejas largas en punta y el gorro rojo
    caido hacia atras. Mira a +z."""
    tipo = V['corto']
    bm.cubo(out, M, -5.5, 2.0, -4.5, 11.0, 7.5, 9.0, P['piel'], semilla=1)                       # el craneo
    bm.cubo(out, M, -5.0, 0.4, -3.0, 10.0, 2.0, 7.4, P['piel'], caras={'frente': P['boca']}, semilla=2)  # la boca
    bm.cubo(out, M, -6.0, 6.0, 3.6, 12.0, 1.6, 1.6, P['piel'], semilla=3)                        # el ceño
    for lado in (-1, 1):                                                                         # los pomulos
        bm.cubo(out, M, lado * 4.6 - 1.2, 2.6, 3.2, 2.4, 2.0, 1.6, P['piel'], semilla=4)
    Mn = M @ vr.T(0.0, 6.0, 4.6) @ vr.Rx(0.5)                                                     # la nariz ganchuda
    bm.cubo(out, Mn, -1.0, -3.6, 0.0, 2.0, 3.6, 2.0, P['piel'], semilla=5)
    bm.cubo(out, Mn @ vr.T(0.0, -3.6, 0.0) @ vr.Rx(-0.9), -0.9, -1.8, 0.0, 1.8, 1.8, 1.6, P['piel'], semilla=6)
    for lado in (-1, 1):                                                                         # los ojos, rasgados
        bm.cubo(out, M @ vr.T(lado * 2.9, 4.6, 4.5) @ vr.Rz(lado * 0.32), -1.8, -0.9, 0.0, 3.6, 1.8, 0.6, P['ojo'],
                semilla=7)
    Mq = M @ vr.T(0.0, 1.0, -2.6) @ vr.Rx(abre)                                                   # la quijada
    bm.cubo(out, Mq, -4.6, -2.0, 0.0, 9.2, 2.0, 7.4, P['piel'], caras={'arriba': P['boca']}, semilla=8)
    for x in (-3.6, -2.0, -0.4, 1.2, 2.8):                                                        # los dientes de arriba
        base = pt(M, (x + 0.4, 0.5, 4.3))
        ll = M[:3, 0] * 0.6
        punta = base - M[:3, 1] * (2.2 if abs(x + 0.4) > 3 else 1.6)
        hoja(out, (punta - ll * 0.1, punta + ll * 0.1, base + ll, base - ll), P['diente'], 1.2, 2.0, semilla=9)
    for x in (-2.8, -1.2, 0.4, 2.0, 3.6):                                                         # y los de abajo
        base = pt(Mq, (x - 0.4, 0.0, 7.1))
        ll = Mq[:3, 0] * 0.6
        punta = base + Mq[:3, 1] * 1.6
        hoja(out, (punta - ll * 0.1, punta + ll * 0.1, base + ll, base - ll), P['diente'], 1.2, 1.6, semilla=10)
    largo_oreja = 11.0 if tipo == 'ladron' else 8.0
    for lado in (-1, 1):                                                                         # las orejas, en punta
        b = pt(M, (lado * 5.4, 5.6, -0.5))
        fuera = M[:3, :3] @ _u((lado * 1.0, 0.35, -0.45))
        arriba = M[:3, :3] @ np.array((0.0, 1.0, 0.0))
        a1, a2 = b - arriba * 2.0, b + arriba * 2.0
        p = b + fuera * largo_oreja
        hoja(out, (a1, p - arriba * 0.2, p + arriba * 0.2, a2) if lado > 0 else (p - arriba * 0.2, a1, a2, p + arriba * 0.2),
             P['oreja'], largo_oreja, 4.0, semilla=11)
    # el gorro rojo: el borde vuelto, la copa y la punta que cae hacia atras
    bm.cubo(out, M, -5.9, 8.6, -4.9, 11.8, 1.6, 9.8, P['borde'], semilla=12)
    bm.cubo(out, M @ vr.T(0.0, 10.2, -0.6) @ vr.Rx(-0.35), -4.6, 0.0, -3.6, 9.2, 3.2, 7.2, P['gorro'], semilla=13)
    bm.cubo(out, M @ vr.T(0.0, 12.6, -2.4) @ vr.Rx(-0.95), -3.0, 0.0, -2.4, 6.0, 3.6, 4.8, P['gorro'], semilla=14)
    bm.cubo(out, M @ vr.T(0.0, 13.2, -6.0) @ vr.Rx(-1.9), -1.8, 0.0, -1.6, 3.6, 3.6, 3.2, P['gorro'], semilla=15)
    bm.cubo(out, M @ vr.T(0.0, 11.4, -9.0) @ vr.Rx(-2.6), -1.0, 0.0, -1.0, 2.0, 2.6, 2.0, P['gorro'], semilla=16)
    if tipo == 'colgon':                                                                         # la cresta de puas en la nuca
        for k in range(4):
            b = pt(M, (0.0, 7.0 - k * 1.8, -4.5))
            atras = M[:3, :3] @ _u((0.0, 0.4, -1.0))
            ll = M[:3, 0] * 0.8
            hoja(out, (b - ll, b + ll, b + atras * 3.0 + ll * 0.1, b + atras * 3.0 - ll * 0.1), P['una'], 1.6, 3.0, 17)
    elif tipo == 'jinete':                                                                       # los cuernecillos
        for lado in (-1, 1):
            pts = [pt(M, (lado * 3.0, 9.4, 1.0))]
            for d in ((lado * 0.6, 1.4, 0.4), (lado * 0.5, 1.2, -0.2), (lado * 0.2, 1.0, -0.6)):
                pts.append(pts[-1] + M[:3, :3] @ np.array(d))
            for a, b in zip(pts[:-1], pts[1:]):
                bm.viga(out, a, b, 1.2, 1.2, P['una'], extra=0.2, semilla=18)


# ----------------------------------------------------------------------
#  Las posturas
# ----------------------------------------------------------------------
# Cada postura: la pelvis (pixeles), el cuerpo (inclinacion hacia delante y giro), la cabeza (cabeceo, giro y lo que
# abre la boca) y los puntos, en coordenadas del modelo, de los codos, las manos, las rodillas y los pies (izquierda,
# derecha). El hombro y la cadera salen del cuerpo.
POSTURAS = {
    # agazapado para saltar: el cuerpo echado adelante, una mano en el suelo y la otra en alto con las garras abiertas
    'acecho': dict(pelvis=(0.0, 6.5, -3.0), inclina=1.0, gira=0.0, cab=(-0.25, 0.0, 0.45),
                   codo=((8.0, 7.0, 6.0), (-9.5, 12.5, 8.0)), mano=((6.5, 0.5, 12.0), (-8.5, 18.5, 14.0)),
                   rodilla=((6.5, 10.5, 1.0), (-6.5, 10.5, 1.0)), pie=((5.0, 0.0, -1.0), (-5.0, 0.0, -1.0))),
}


def postura_espalda():
    """El Colgon, colgado de la espalda de un jugador (que mira a +z y tiene el pecho en z=+2 y la espalda en z=-2):
    el cuerpo pegado a su espalda, la cabeza asomando sobre su hombro derecho (x<0) y mordiendo hacia el cuello, los
    brazos rodeandole el pecho y las piernas la cintura."""
    return dict(pelvis=(0.0, 12.0, -5.2), inclina=-0.1, gira=0.0, cab=(0.15, -0.55, 0.5), cabeza_en=(-4.4, 25.0, -2.6),
                codo=((7.0, 19.0, -1.0), (-7.0, 19.0, -1.0)), mano=((2.0, 18.5, 3.6), (-2.0, 19.5, 3.6)),
                rodilla=((6.0, 12.0, -1.0), (-6.0, 12.0, -1.0)), pie=((3.0, 9.0, 3.2), (-3.0, 9.5, 3.2)))


def postura_hombros():
    """El Jinete, sentado en los hombros de un jugador: la pelvis detras de su cabeza, el cuerpo echado sobre ella, la
    cabeza asomando por encima, sonriendo, y las manos tapandole los ojos; las piernas por delante del pecho."""
    return dict(pelvis=(0.0, 24.5, -4.0), inclina=0.55, gira=0.0, cab=(-0.2, 0.0, 0.5),
                codo=((7.0, 30.0, 2.0), (-7.0, 30.0, 2.0)), mano=((2.4, 28.0, 4.8), (-2.4, 28.0, 4.8)),
                rodilla=((4.5, 26.0, 2.0), (-4.5, 26.0, 2.0)), pie=((3.6, 17.0, 3.0), (-3.6, 17.0, 3.0)))


def postura_brazo(mano_jugador):
    """El Ladron, colgado del brazo derecho del jugador (estirado hacia delante): las manos agarradas a su mano, el
    cuerpo colgando debajo, la cabeza echada atras mordiendo, las piernas pataleando."""
    hx, hy, hz = mano_jugador
    return dict(pelvis=(hx, hy - 19.0, hz + 1.0), inclina=-0.15, gira=-1.3, cab=(0.45, 0.2, 0.6),
                cabeza_en=(hx + 0.5, hy - 8.0, hz + 3.0),
                codo=((hx + 4.5, hy - 5.0, hz + 2.5), (hx - 4.0, hy - 4.0, hz + 2.0)),
                mano=((hx + 1.2, hy + 0.5, hz + 0.5), (hx - 1.2, hy + 0.8, hz - 0.5)),
                rodilla=((hx + 4.0, hy - 23.0, hz + 4.0), (hx - 3.5, hy - 21.0, hz - 1.0)),
                pie=((hx + 3.0, hy - 28.0, hz + 1.0), (hx - 4.5, hy - 26.0, hz - 4.0)))


# ----------------------------------------------------------------------
#  El Trasgo
# ----------------------------------------------------------------------
def trasgo(tipo='A', postura='acecho', escala=1.0 / 16):
    """El Trasgo en una postura: (los quads, info). La postura puede ser el nombre de una de POSTURAS o un dict."""
    V = VARIANTES[tipo]
    P = pintores(V)
    Q = POSTURAS[postura] if isinstance(postura, str) else postura
    corto = V['corto']
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        pel = np.array(Q['pelvis'], float)
        Mt = vr.T(*pel) @ vr.Ry(Q['gira']) @ vr.Rx(Q['inclina'])                                 # el cuerpo
        bm.cubo(out, Mt, -3.4, 0.0, -2.4, 6.8, 5.0, 4.8, P['piel'], semilla=20)                    # el vientre
        bm.cubo(out, Mt, -4.0, 4.6, -2.8, 8.0, 5.4, 5.4, P['piel'], semilla=21)                    # el pecho
        bm.cubo(out, Mt, -3.6, -1.2, -2.6, 7.2, 2.4, 5.2, P['trapo'], semilla=22)                  # el taparrabos
        bm.cubo(out, Mt, -1.6, 9.6, -1.4, 3.2, 2.0, 3.0, P['piel'], semilla=23)                    # el cuello
        hombro = [pt(Mt, (4.6, 8.8, 0.0)), pt(Mt, (-4.6, 8.8, 0.0))]
        cadera = [pt(Mt, (2.2, 0.4, 0.0)), pt(Mt, (-2.2, 0.4, 0.0))]
        cuello = pt(Mt, (0.0, 11.0, 0.4))
        # la cabeza
        cp, cg, abre = Q['cab']
        if 'cabeza_en' in Q:
            cen = np.array(Q['cabeza_en'], float)
            Mh = vr.T(*cen) @ vr.Ry(Q['gira'] + cg) @ vr.Rx(cp) @ vr.T(0.0, -4.0, 0.0)
            hueso(out, cuello, pt(Mh, (0.0, 2.0, -1.0)), 2.6, P['piel'], semilla=24)
        else:
            Mh = Mt @ vr.T(0.0, 10.6, 1.2) @ vr.Rx(-Q['inclina'] + cp) @ vr.Ry(cg) @ vr.T(0.0, -1.0, 1.6)
        cabeza(out, P, V, Mh, abre)
        # los brazos y las piernas
        for i, lado in enumerate((1, -1)):
            codo, mano_p = np.array(Q['codo'][i], float), np.array(Q['mano'][i], float)
            bm.cubo(out, vr.T(*hombro[i]), -1.6, -1.6, -1.6, 3.2, 3.2, 3.2, P['piel'], semilla=25)
            hueso(out, hombro[i], codo, 2.4, P['piel'], semilla=26)
            hueso(out, codo, mano_p, 2.0, P['piel'], semilla=27)
            largos = (5.0, 6.0, 5.0) if corto == 'jinete' else (4.0, 4.6, 4.0)
            mano(out, P, codo, mano_p, lado, izquierda=(lado > 0), largos=largos, semilla=28)
            rod, pie = np.array(Q['rodilla'][i], float), np.array(Q['pie'][i], float)
            hueso(out, cadera[i], rod, 2.6, P['piel'], semilla=29)
            hueso(out, rod, pie, 2.0, P['piel'], semilla=30)
            eje = _u(pie - rod)
            Mp = bm.em.marco(pie, eje)
            for dx in (-0.9, 0.9):                                                               # los dedos del pie
                b = pt(Mp, (dx, 0.0, 0.0))
                garra(out, P, b, _u(eje * 0.3 + np.array((0.0, 0.0, 1.0)) * (1 if Q is POSTURAS.get('acecho') else 0.6)),
                      Mp[:3, 0], 3.0, semilla=31)
        # lo de cada tipo
        if corto == 'colgon':                                                                    # la cola de gancho
            pts = [pt(Mt, (0.0, 0.5, -2.6))]
            d = _u(Mt[:3, :3] @ np.array((0.0, -0.4, -1.0)))
            for k in range(7):
                pts.append(pts[-1] + d * 3.2)
                d = _u(d + np.array((0.0, -0.25 + k * 0.12, 0.0)) + Mt[:3, :3] @ np.array((0.15, 0.0, 0.0)))
            for k, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
                hueso(out, a, b, 1.8 - k * 0.15, P['piel'], semilla=32)
            garra(out, P, pts[-1], d, np.array((1.0, 0.0, 0.0)), 3.5, semilla=33)
        elif corto == 'ladron':                                                                  # el saco del botin
            Ms = Mt @ vr.T(0.0, 6.0, -3.0) @ vr.Rx(0.2)
            bm.cubo(out, Ms, -3.6, -4.0, -6.0, 7.2, 8.0, 6.0, P['saco'], semilla=34)
            bm.cubo(out, Ms, -2.6, 4.0, -5.0, 5.2, 1.6, 4.0, P['saco'], semilla=35)
            for k, (x, z) in enumerate(((-1.4, -3.4), (1.2, -2.6), (0.0, -4.4))):              # el oro que asoma
                bm.cubo(out, Ms, x - 0.8, 5.4, z - 0.8, 1.6, 1.4, 1.6, P['oro'], semilla=36 + k)
            for lado in (-1, 1):                                                                 # las correas
                hueso(out, pt(Mt, (lado * 3.0, 9.4, 2.9)), pt(Mt, (lado * 3.0, 1.0, 2.9)), 0.8, P['trapo'], semilla=37)
    finally:
        bm.PPB = ppb
    E = np.diag([escala, escala, escala, 1.0])
    out = qm.transformar(out, E)
    return out, {'cabeza': pt(E, pt(Mh, (0.0, 4.0, 5.0))), 'ojos': pt(E, pt(Mh, (0.0, 4.6, 5.0))),
                 'luz': {'colgon': 'ffb43a', 'jinete': '6ae8ff', 'ladron': 'a4ff4a'}[corto]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

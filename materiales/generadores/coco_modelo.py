"""
El Coco (16-10-2026): el mob que te mete en la panza. Juan: «hagamos un mob que meta al jugador dentro de su panza, como
atrapado, y le quite vida lentamente; no tanto daño, pero si no hay una persona cerca esa cosa puede ser mortal; la
unica forma de salvar a un jugador es matando al mob».

El de la nana («duermete niño, duermete ya, que viene el Coco y te comera»), pero nuestro. La leyenda no le da forma; lo
que cuenta es que el coco (el fruto) se llama asi por el: los marineros vieron en sus tres agujeros la cara del
monstruo. Nuestro Coco lleva por cabeza una cascara dura con los tres agujeros (los dos ojos, hondos, con una brasa al
fondo, y el de la nariz) y las tres aristas del coco, que se juntan en el ceño; al abrirse se parte de lado a lado como
un coco roto, y el canto de la carne blanca son los dientes. El cuerpo es pesado y encorvado, con la giba, las piernas
cortas y arqueadas, los brazos larguisimos y las manos enormes de cuatro dedos para agarrarte; y la panza: grande,
colgante, donde te mete. Si tiene a alguien dentro, encima del Coco sale un aviso: el icono de alerta, el nombre del
jugador y «¡ha sido atrapado!» (Juan: «no quiero panza translucida»).

    A  el Gloton       cascara parda con la cresta de estopa (la fibra del coco) de punta; cuerpo de carbon y la panza
                       de brasa: te agarra, te traga y se queda quieto haciendo la digestion, defendiendose
    B  el del Saco     cascara de hueso palido bajo la capucha de arpillera, que cae atras en punta y va atada con una
                       cuerda; la panza cosida como un saco, de azufre: te traga y huye de los demas para comerte solo
    C  el de la Nana   cascara negra y pulida con hileras de agujeros que brillan (por ahi silba la nana) y la barba de
                       fibra; la panza lila: su nana adormece a los que la oyen y entonces te traga

Se modela como un mob, en pixeles del jugador (16 por bloque), con un texel por pixel.
"""
import math
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _emis
from sierpe_modelo import lamina
from jefa_modelo import pt

TAU = math.tau
PPB = 1
JUEGO = False            # para la malla del juego: sin los carrillos (una caja no se estira al abrir la boca)


def PARTE(nombre, padre, marco):
    """Donde empieza una parte que se mueve. coco_juego.py la cambia para repartir las cajas en las piezas de la malla
    del juego; en los bocetos no hace nada."""


def EN(nombre):
    """Vuelve a una parte ya empezada (lo mismo: solo para coco_juego.py)."""


def _h(*cs):
    return [nm._hex(c) for c in cs]


VARIANTES = {
    'A': dict(clave='COA', nombre='el Glotón', corto='gloton',
              cascara=_h('1c110a', '2c1b10', '402816', '583820', '744c2c'),
              fibra=_h('3a2414', '583a20', '7a542e', 'a07444', 'c49a62'),
              piel=_h('171312', '231e1c', '312a27', '403732', '52463f'),
              panza=_h('3e2e26', '54402f', '6a5240', '806450', '987a62'),
              ojo=_h('ff6a2a', 'ffe0c0'), luz='ff6a2a'),
    'B': dict(clave='COB', nombre='el del Saco', corto='saco',
              cascara=_h('3a342c', '5a5246', '7e7464', 'a49a88', 'c8bfae'),
              fibra=_h('22160c', '34230f', '4a3418', '644822', '80602e'),
              piel=_h('130d09', '1e150f', '2b1f16', '3a2b1f', '4c3a2a'),
              panza=_h('3a3020', '50432c', '665838', '7c6c46', '948456'),
              ojo=_h('ffd23a', 'fff6d0'), luz='ffd23a'),
    'C': dict(clave='COC', nombre='el de la Nana', corto='nana',
              cascara=_h('0a0706', '140e0b', '201611', '2e2018', '3e2c20'),
              fibra=_h('4a3e2a', '6a5a3e', '8e7c56', 'b2a074', 'd4c69c'),
              piel=_h('0d1110', '151b18', '1e2722', '29342e', '36443c'),
              panza=_h('283230', '36423e', '46544e', '586860', '6c7e74'),
              ojo=_h('b48aff', 'f2e6ff'), luz='b48aff'),
}
CARNE = _h('4a2c14', 'b4ab98', 'e2dccc', 'faf6ec')       # la piel parda de la semilla y la carne blanca del coco
UNA = _h('2a2218', '5a4c38', '8e7e62', 'bcae8c', 'e2d8bc')
CUERDA = _h('2e200e', '4a3618', '6a5024', '8c6c34')
HILO = _h('120c08', '22180e')


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
    cascara, fibra, piel, panza, ojo = V['cascara'], V['fibra'], V['piel'], V['panza'], V['ojo']

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'co%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def _vetas(tw, th, s):
        """La cascara del coco: las vetas de la fibra a lo largo (una oscura cada cuatro, alguna clara) y el canto de
        abajo a la sombra."""
        idx = np.full((th, tw), 2)
        x, j = s % 3, 0
        while x < tw:
            largo = th if j % 3 else max(2, (th * 2) // 3)
            y0 = (j * 5 + s) % max(1, th - largo + 1)
            idx[y0:y0 + largo, x] = 1
            if j % 4 == 1 and x + 1 < tw:
                idx[y0:y0 + max(1, largo // 2), x + 1] = 3
            x += (3, 5, 2, 4, 6, 3)[(j + s) % 6]
            j += 1
        return idx

    def p_cascara(tw, th, cara_, s):
        idx = _vetas(tw, th, s)
        if cara_ == 'arriba':
            idx[idx == 2] = 3
            idx[idx == 1] = 2
        if cara_ not in ('arriba', 'abajo'):
            idx[th - 1, :] = np.minimum(idx[th - 1, :], 1)
        if cara_ == 'abajo':
            idx[...] = 1
        return _pinta(idx, cascara), None
    reg('cascara', p_cascara)

    def p_borde(tw, th, cara_, s):
        """El canto de la cascara de arriba: abajo, la raya parda de la semilla y la carne blanca (donde se parte)."""
        t = p_cascara(tw, th, cara_, s)[0]
        if cara_ not in ('arriba', 'abajo') and th >= 3:
            t[th - 1, :] = (*CARNE[3], 255)
            t[th - 2, :] = (*CARNE[0], 255)
        return t, None
    reg('borde', p_borde)

    def p_borde_q(tw, th, cara_, s):
        """El canto de la quijada: arriba, la carne blanca y la raya parda."""
        t = p_cascara(tw, th, cara_, s)[0]
        if cara_ not in ('arriba', 'abajo') and th >= 3:
            t[0, :] = (*CARNE[3], 255)
            t[1, :] = (*CARNE[0], 255)
        return t, None
    reg('borde_q', p_borde_q)

    def p_arista(tw, th, cara_, s):
        """Las aristas del coco: mas claras, con el filo de arriba encendido de luz."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        if cara_ == 'arriba':
            idx[...] = 4
        else:
            idx[th - 1, :] = 2
        return _pinta(idx, cascara), None
    reg('arista', p_arista)

    def p_fibra(tw, th, cara_, s):
        """La estopa: hebras a lo largo (de la raiz arriba a la punta abajo), mas claras hacia la punta, y la punta
        deshilachada (con huecos)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = ys / max(th - 1, 1)
        idx = np.where((xs + s) % 3 == 0, 1, 2)
        idx = idx + (f > 0.55).astype(int) + (f > 0.85).astype(int)
        idx[(xs + s) % 3 == 0] = np.minimum(idx[(xs + s) % 3 == 0], 2)
        t = _pinta(np.clip(idx, 0, 4), fibra)
        corto = ((xs * 7 + s) % 5) < 2
        t[(f > 0.8) & corto] = 0
        return t, None
    reg('fibra', p_fibra)

    def p_piel(tw, th, cara_, s):
        """La piel del cuerpo: oscura, en pliegues a lo ancho (la raya del pliegue y el canto claro debajo), limpia."""
        ys, xs = np.mgrid[0:th, 0:tw]
        if cara_ in ('arriba', 'abajo'):
            idx = np.full((th, tw), 2)
            idx[(xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)] = 3 if cara_ == 'arriba' else 1
            if cara_ == 'abajo':
                idx[...] = 1
            return _pinta(idx, piel), None
        idx = np.full((th, tw), 2)
        idx[0, :] = 3
        idx[th - 1, :] = 1
        return _pinta(idx, piel), None
    reg('piel', p_piel)

    def p_panza(tw, th, cara_, s):
        """La barriga, en bandas a lo ancho (cada piso de la panza es una): el canto de arriba claro, el medio y el
        de abajo a la sombra. Limpia, sin motas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        if cara_ in ('arriba', 'abajo'):
            return _pinta(np.full((th, tw), 3 if cara_ == 'arriba' else 1), panza), None
        if cara_ != 'frente' or tw < 8 or th < 8:
            idx = np.full((th, tw), 2)
            idx[0, :] = 3
            idx[th - 1, :] = 1
            return _pinta(idx, panza), None
        u = (xs - (tw - 1) / 2) / (tw / 2)
        v = (ys - (th - 1) * 0.42) / (th / 2)
        r = u * u + v * v
        idx = np.where(r < 0.3, 4, np.where(r < 0.62, 3, np.where(r < 1.0, 2, 1)))
        ox, oy = int(round((tw - 1) / 2)), int(round(th * 0.62))                           # el ombligo
        idx[oy, ox] = 0
        idx[oy - 1, ox] = 1
        for k in range(1, 3):                                                             # los pliegues de arriba
            fila = int(round(th * (0.08 + 0.07 * k)))
            ancho = np.abs(u[0]) < 0.75 - 0.15 * k
            idx[fila][ancho] = np.minimum(idx[fila][ancho], 1)
            idx[fila + 1][ancho] = np.maximum(idx[fila + 1][ancho], 3)
        return _pinta(idx, panza), None
    reg('panza', p_panza)

    def p_paladar(tw, th, cara_, s):
        """El paladar (la cara de abajo de la cascara; la fila de arriba de la textura es la de delante): oscuro, con
        los pliegues de la carne a lo ancho, y al fondo las rayas de luz que suben de la garganta."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (34, 10, 10, 255)
        t[(ys % 3) == 1] = (56, 18, 16, 255)
        f = ys / max(th - 1, 1)
        luz = (f > 0.72) & ((ys % 2) == 0)
        t[luz] = (*ojo[0], 255)
        return t, _emis(t, luz, 170)
    reg('paladar', p_paladar)

    def p_lengua(tw, th, cara_, s):
        """El suelo de la boca (la cara de arriba de la quijada; la fila de arriba es la del fondo)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (44, 12, 12, 255)
        t[np.abs(xs - (tw - 1) / 2) < 0.6] = (30, 8, 8, 255)
        f = ys / max(th - 1, 1)
        luz = (f < 0.22) & ((ys % 2) == 0)
        t[luz] = (*ojo[0], 255)
        return t, _emis(t, luz, 150)
    reg('lengua', p_lengua)

    def p_carrillo(tw, th, cara_, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (30, 9, 9, 255)
        return t, None
    reg('carrillo', p_carrillo)

    def p_garganta(tw, th, cara_, s):
        """El fondo de la garganta: el neon con el centro casi blanco."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*ojo[0], 255)
        cen = (np.abs(xs - (tw - 1) / 2) <= tw / 5) & (np.abs(ys - (th - 1) / 2) <= th / 4)
        t[cen] = (*ojo[1], 255)
        return t, _emis(t, np.ones((th, tw), bool), 230)
    reg('garganta', p_garganta, pleno=True)

    def p_cuenca(tw, th, cara_, s):
        """El ojo: un agujero hondo en la cascara (el canto oscuro y el fondo negro) con la brasa al fondo: un punto
        casi blanco y su cruz de neon."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (6, 4, 3, 255)
        canto = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)
        t[canto] = (*cascara[0], 255)
        cx, cy = (tw - 1) // 2, (th - 1) // 2
        cruz = ((np.abs(xs - cx) + np.abs(ys - cy)) == 1) & ~canto
        t[cruz] = (*ojo[0], 255)
        t[cy, cx] = (*ojo[1], 255)
        luz = cruz.copy()
        luz[cy, cx] = True
        return t, _emis(t, luz, 255)
    reg('cuenca', p_cuenca)

    def p_hueco(tw, th, cara_, s):
        """El agujero de la nariz: hondo y negro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (5, 3, 2, 255)
        t[(xs == 0) | (ys == 0) | (xs == tw - 1)] = (*cascara[0], 255)
        return t, None
    reg('hueco', p_hueco)

    def p_diente(tw, th, cara_, s):
        """Un diente de carne de coco, en hoja: la base arriba (con la raya parda de la semilla) y la punta abajo, un
        poco torcida, como un trozo partido."""
        t = np.zeros((th, tw, 4), np.uint8)
        sesgo = ((s % 3) - 1) * 0.18
        for y in range(th):
            k = (th - y) / th
            w = tw * k
            c = (tw - w) / 2 + sesgo * tw * (1 - k)
            for x in range(int(math.floor(c)), min(tw, int(math.ceil(c + w)))):
                if x < 0:
                    continue
                t[y, x] = (*(CARNE[3] if x < c + w / 2 else CARNE[2]), 255)
        t[0, :][t[0, :, 3] > 0] = (*CARNE[0], 255)
        return t, None
    reg('diente', p_diente)

    def p_una(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs == 0, 3, 2)
        if cara_ == 'arriba':
            idx[...] = 3
        return _pinta(idx, UNA), None
    reg('una', p_una)

    def p_arpillera(tw, th, cara_, s):
        """La capucha del Saco: arpillera de estopa, tejida a cuadros de dos (hebras de pie y hebras tumbadas)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        celda = ((xs // 2) + (ys // 2)) % 2
        idx = np.where(celda == 0, np.where(xs % 2 == 0, 2, 3), np.where(ys % 2 == 0, 2, 1))
        if cara_ not in ('arriba', 'abajo'):
            idx[th - 1, :] = 1
        return _pinta(idx, fibra), None
    reg('arpillera', p_arpillera)

    def p_cuerda(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs + ys) % 3) == 0, 1, 2)
        idx[((xs + ys) % 3) == 1] = 3
        return _pinta(idx, CUERDA), None
    reg('cuerda', p_cuerda)

    def p_hilo(tw, th, cara_, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*HILO[1], 255)
        return t, None
    reg('hilo', p_hilo)

    def p_agujero(tw, th, cara_, s):
        """Un agujero de la Nana, que brilla: neon y el centro casi blanco."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*ojo[0], 255)
        return t, _emis(t, np.ones((th, tw), bool), 190)
    reg('agujero', p_agujero, pleno=True)

    def p_negro(tw, th, cara_, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (5, 3, 2, 255)
        return t, None
    reg('negro', p_negro)
    return P


# ----------------------------------------------------------------------
#  Las piezas
# ----------------------------------------------------------------------
def hoja(out, P4, pintor, ancho, alto, semilla=0):
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def hueso(out, a, b, grosor, pintor, alto=None, semilla=0):
    """Un tramo de miembro de a a b (una caja que se solapa un poco en las juntas)."""
    bm.viga(out, a, b, grosor, alto or grosor, pintor, extra=grosor * 0.3, semilla=semilla)


def caja_r(out, M, x0, y0, z0, w, h, d, pintor, b=2.0, caras=None, semilla=0):
    """Una caja con los cantos comidos (tres cajas: cada una entera en un eje y metida 'b' en los otros dos): se lee
    redonda sin cortarla en rodajas."""
    bm.cubo(out, M, x0, y0 + b, z0 + b, w, h - 2 * b, d - 2 * b, pintor, caras=caras, semilla=semilla)
    bm.cubo(out, M, x0 + b, y0, z0 + b, w - 2 * b, h, d - 2 * b, pintor, caras=caras, semilla=semilla + 1)
    bm.cubo(out, M, x0 + b, y0 + b, z0, w - 2 * b, h - 2 * b, d, pintor, caras=caras, semilla=semilla + 2)


def garra(out, P, M, largo, grosor=1.5, semilla=0):
    """Una garra en tres escalones que se curvan hacia la palma (-y del marco), a lo largo de +z."""
    Mi = M
    for k in range(3):
        g = grosor * (1.0 - k * 0.3)
        bm.cubo(out, Mi, -g / 2, -g / 2, -0.15, g, g, largo / 3 + 0.3, P['una'], semilla=semilla)
        Mi = Mi @ vr.T(0.0, 0.0, largo / 3) @ vr.Rx(0.4)


def mano(out, P, muneca, hacia, dorso, cierra=0.5, abierta=1.0, nombre=None, semilla=0):
    """La mano enorme: la palma y cuatro dedos largos de dos falanges con su garra, abiertos en abanico. 'hacia' es
    adonde apuntan los dedos; 'dorso', hacia donde mira el dorso (los dedos se doblan hacia la palma)."""
    Mm = bm.em.marco(np.asarray(muneca, float), _u(hacia), up=_u(dorso))
    if nombre:
        EN(nombre)
    bm.cubo(out, Mm, -3.6, -1.5, -0.6, 7.2, 3.0, 6.4, P['piel'], caras={'abajo': P['panza']}, semilla=semilla)
    bm.cubo(out, Mm, -3.0, 1.2, 0.6, 6.0, 0.8, 4.6, P['piel'], semilla=semilla + 1)               # los nudillos
    for k, x in enumerate((-2.7, -0.9, 0.9, 2.7)):
        largo = (4.4, 5.2, 5.0, 4.0)[k]
        Mf = Mm @ vr.T(x, 0.0, 5.4) @ vr.Ry(x * 0.07 * abierta) @ vr.Rx(cierra * 0.6)
        if nombre:
            PARTE(f'{nombre}_dedo{k}', nombre, Mf)
        bm.cubo(out, Mf, -1.0, -1.0, -0.3, 2.0, 2.0, largo + 0.3, P['piel'], caras={'abajo': P['panza']},
                semilla=semilla + 2)
        Mf = Mf @ vr.T(0.0, 0.0, largo) @ vr.Rx(cierra * 0.8)
        if nombre:
            PARTE(f'{nombre}_dedo{k}b', f'{nombre}_dedo{k}', Mf)
        bm.cubo(out, Mf, -0.85, -0.85, -0.3, 1.7, 1.7, largo * 0.75 + 0.3, P['piel'], caras={'abajo': P['panza']},
                semilla=semilla + 3)
        garra(out, P, Mf @ vr.T(0.0, -0.1, largo * 0.75) @ vr.Rx(cierra * 0.5), 3.6, 1.5, semilla + 4)


def pie(out, P, tobillo, giro, semilla=0):
    """El pie: ancho y plano, con tres dedos cortos y sus garras clavadas en el suelo."""
    Mp = vr.T(*tobillo) @ vr.Ry(giro)
    y0 = -float(tobillo[1])
    bm.cubo(out, Mp, -3.4, y0, -3.6, 6.8, 3.4, 7.6, P['piel'], semilla=semilla)
    for x in (-2.2, 0.0, 2.2):
        bm.cubo(out, Mp, x - 1.0, y0, 3.8, 2.0, 1.8, 2.2, P['piel'], semilla=semilla + 1)
        garra(out, P, Mp @ vr.T(x, y0 + 1.0, 5.8) @ vr.Rx(0.25), 2.6, 1.3, semilla + 2)


def fibras(out, P, M, raiz, hacia, largo, ancho=2.4, caida=0.5, semilla=0):
    """Un mechon de estopa: dos tramos de hojas cruzadas (para que se vea de todos lados) que se doblan hacia abajo."""
    a = pt(M, raiz)
    d = _u(M[:3, :3] @ np.asarray(hacia, float))
    pts = [a, a + d * largo * 0.55]
    d2 = _u(d + np.array((0.0, -caida, 0.0)))
    pts.append(pts[-1] + d2 * largo * 0.45)
    for i, (p0, p1) in enumerate(zip(pts[:-1], pts[1:])):
        eje = _u(p1 - p0)
        l1 = _u(np.cross(eje, np.array((0.0, 1.0, 0.0))) if abs(eje[1]) < 0.95 else np.array((1.0, 0.0, 0.0)))
        l2 = _u(np.cross(eje, l1))
        w = ancho * (1.0 - 0.25 * i) / 2
        for ll in (l1, l2):
            hoja(out, (p1 - ll * w * 0.7, p1 + ll * w * 0.7, p0 + ll * w, p0 - ll * w), P['fibra'], ancho,
                 float(np.linalg.norm(p1 - p0)), semilla + i)


def dientes(out, P, M, desde, hasta, n, hacia, largos, semilla=0):
    """Una fila de dientes de carne de coco entre dos puntos del canto (del marco M), hacia abajo (-1) o arriba (+1),
    con largos que cambian (es un coco partido, no una sierra)."""
    a, b = np.asarray(desde, float), np.asarray(hasta, float)
    lado = _u(M[:3, :3] @ _u(b - a))
    eje = M[:3, :3] @ np.array((0.0, float(hacia), 0.0))
    fuera = _u(np.cross(lado, eje)) * (-1.0 if hacia < 0 else 1.0)
    for i in range(n):
        base = pt(M, a + (b - a) * ((i + 0.5) / n))
        L = largos[i % len(largos)]
        w = float(np.linalg.norm(b - a)) / n * 0.62
        punta = base + eje * L + fuera * 0.25
        for ll in (lado, _u(lado + fuera * 0.9)):
            hoja(out, (punta - ll * 0.12, punta + ll * 0.12, base + ll * w, base - ll * w), P['diente'], 2.0, L,
                 semilla + i)


# ----------------------------------------------------------------------
#  La cabeza
# ----------------------------------------------------------------------
def cabeza(out, P, V, M, abre=0.5):
    """La cascara: el craneo redondeado, la cara (los dos ojos hondos con su brasa y el agujero de la nariz), las tres
    aristas que bajan al ceño, el canto de carne blanca donde se parte y la quijada que se abre con sus dientes. Mira a
    +z; el canto de la parte esta en y = -2."""
    tipo = V['corto']
    c = P['cascara']
    bm.cubo(out, M, -8.0, -2.0, -7.0, 16.0, 7.5, 14.6, P['borde'], caras={'abajo': P['paladar'], 'arriba': c}, semilla=1)
    bm.cubo(out, M, -7.4, 5.5, -6.6, 14.8, 3.1, 14.0, c, semilla=2)                             # la boveda
    bm.cubo(out, M, -5.8, 8.6, -5.2, 11.6, 1.8, 10.8, c, semilla=3)
    bm.cubo(out, M, -3.4, 10.4, -3.4, 6.8, 0.9, 7.0, c, semilla=3)
    bm.cubo(out, M, -7.0, -1.0, -8.4, 14.0, 7.6, 1.4, c, semilla=4)                             # la nuca
    bm.cubo(out, M, -5.0, 0.0, -9.4, 10.0, 6.0, 1.0, c, semilla=4)
    for lado in (-1, 1):                                                                       # los lados, abombados
        bm.cubo(out, M, (8.0 if lado > 0 else -9.0), -1.2, -5.0, 1.0, 5.8, 10.6, c, semilla=5)
        bm.cubo(out, M, (7.4 if lado > 0 else -8.4), 5.5, -4.6, 1.0, 2.2, 9.8, c, semilla=5)
    bm.cubo(out, M, -6.6, -1.4, 7.6, 13.2, 7.4, 1.2, P['borde'], semilla=6)                     # la cara
    bm.cubo(out, M, -5.4, -1.4, 7.6, 10.8, 8.8, 1.2, P['borde'], semilla=6)
    for lado in (-1, 1):                                                                       # los pomulos
        bm.cubo(out, M, (4.4 if lado > 0 else -7.2), -0.8, 8.4, 2.8, 2.2, 1.2, c, semilla=6)
    # los ojos (hondos, con la brasa al fondo) y el agujero de la nariz: los tres agujeros del coco
    for lado in (-1, 1):
        bm.cubo(out, M, lado * 3.7 - 2.5, 1.9, 8.55, 5.0, 5.0, 0.3, P['cuenca'], semilla=7)
    bm.cubo(out, M, -1.4, -0.9, 8.55, 2.8, 2.2, 0.3, P['hueco'], semilla=8)
    # las aristas: la de en medio por encima de la boveda, que baja al ceño, y las dos de los lados que bajan en uve
    bm.cubo(out, M, -1.0, 9.4, -5.6, 2.0, 1.0, 11.6, P['arista'], semilla=9)
    bm.cubo(out, M @ vr.T(0.0, 9.6, 6.0) @ vr.Rx(0.7), -1.0, -1.0, -0.4, 2.0, 1.4, 3.6, P['arista'], semilla=10)
    for lado in (-1, 1):
        Mc = M @ vr.T(lado * 3.6, 7.6, 8.4) @ vr.Rz(lado * 0.36)
        bm.cubo(out, Mc, -3.6, -0.9, -1.4, 7.2, 1.9, 2.0, P['arista'], semilla=11)
        bm.cubo(out, M @ vr.T(lado * 6.6, 6.2, 1.0) @ vr.Ry(lado * 0.1), -0.8, 0.0, -6.0, 1.6, 1.0, 12.0, P['arista'],
                semilla=12)
    # el fondo de la garganta y los dientes de carne de coco de arriba, partidos
    bm.cubo(out, M, -5.0, -6.0, -6.2, 10.0, 4.2, 1.0, P['garganta'], semilla=16)
    dientes(out, P, M, (-6.6, -1.6, 8.4), (6.6, -1.6, 8.4), 7, -1, (3.4, 2.4, 4.2, 2.8, 3.8, 2.2, 3.6), semilla=18)
    for lado in (-1, 1):
        dientes(out, P, M, (lado * 7.8, -1.6, 6.6), (lado * 7.8, -1.6, -2.4), 4, -1, (3.0, 2.2, 2.6, 1.8), semilla=19)
    # la quijada: la otra mitad de la cascara, de bisagra atras, con sus dientes hacia arriba
    Mq = M @ vr.T(0.0, -2.0, -6.4) @ vr.Rx(abre)
    PARTE('quijada', 'cabeza', Mq)
    bm.cubo(out, Mq, -7.4, -4.6, 0.0, 14.8, 4.6, 14.6, P['borde_q'], caras={'arriba': P['lengua']}, semilla=13)
    bm.cubo(out, Mq, -5.8, -5.8, 1.2, 11.6, 1.3, 12.6, c, semilla=14)                           # la barbilla
    bm.cubo(out, Mq, -6.0, -4.0, 14.5, 12.0, 4.0, 0.8, P['borde_q'], semilla=15)
    dientes(out, P, Mq, (-6.4, 0.0, 14.0), (6.4, 0.0, 14.0), 6, 1, (2.6, 3.6, 2.0, 3.2, 2.4, 3.4), semilla=20)
    for lado in (-1, 1):
        dientes(out, P, Mq, (lado * 7.2, 0.0, 12.4), (lado * 7.2, 0.0, 4.0), 3, 1, (2.4, 1.8, 2.0), semilla=21)
    if tipo == 'nana':                                                                         # la barba de estopa
        for k, (x, z, largo) in enumerate(((-4.6, 12.6, 9.0), (-2.4, 13.6, 12.0), (0.0, 14.0, 14.0), (2.4, 13.6, 12.0),
                                           (4.6, 12.6, 9.0), (-6.4, 9.0, 8.0), (6.4, 9.0, 8.0))):
            fibras(out, P, Mq, (x, -5.6, z), (x * 0.03, -1.0, 0.35), largo, ancho=2.8, caida=0.1, semilla=67 + k)
    EN('cabeza')
    # los carrillos, por dentro (de la quijada al craneo): en el juego no, que una caja no se estira
    if not JUEGO:
        for lado in (-1, 1):
            x = lado * 7.2
            a_, b_ = pt(M, (x, -2.0, -6.0)), pt(M, (x, -2.0, 7.0))
            q = pt(Mq, (x, 0.0, 12.0))
            hoja(out, (a_, q, b_, a_), P['carrillo'], 12.0, 6.0, semilla=17)
    # lo de cada tipo
    if tipo == 'gloton':                                                                       # la cresta de estopa
        PARTE('cresta', 'cabeza', M @ vr.T(0.0, 9.4, 0.0))
        for k, (x, z, alto, atras) in enumerate(((0.0, 4.0, 11.0, 0.5), (-1.6, 2.0, 10.0, 0.7), (1.6, 2.0, 10.0, 0.7),
                                                 (-0.8, -0.5, 12.0, 0.9), (0.8, -0.5, 12.0, 0.9), (-2.6, -2.5, 9.0, 1.1),
                                                 (2.6, -2.5, 9.0, 1.1), (0.0, -3.5, 11.0, 1.2), (-1.6, -5.0, 8.0, 1.4),
                                                 (1.6, -5.0, 8.0, 1.4))):
            fibras(out, P, M, (x, 9.4, z), (x * 0.12, 1.0, -atras), alto, ancho=2.6, caida=0.6, semilla=30 + k)
        for lado in (-1, 1):                                                                   # y los mechones de las sienes
            for k, z in enumerate((-1.0, -4.0)):
                fibras(out, P, M, (lado * 8.6, 4.0, z), (lado * 0.6, 0.2, -1.0), 8.0 - k, ancho=2.4, caida=0.9,
                       semilla=40 + k)
    elif tipo == 'saco':                                                                       # la capucha de arpillera
        a = P['arpillera']
        bm.cubo(out, M, -9.4, 2.4, -9.8, 18.8, 8.8, 14.8, a, semilla=50)
        bm.cubo(out, M, -8.0, 11.2, -8.6, 16.0, 1.8, 12.6, a, semilla=51)
        bm.cubo(out, M, -5.2, 13.0, -7.2, 10.4, 1.4, 8.6, a, semilla=51)
        for lado in (-1, 1):                                                                   # el canto que enmarca la cara
            bm.cubo(out, M, (8.6 if lado > 0 else -10.8), -2.6, 2.6, 2.2, 15.0, 3.6, a, semilla=52)
        bm.cubo(out, M, -10.8, 10.2, 2.6, 21.6, 3.2, 3.6, a, semilla=53)
        bm.cubo(out, M, -8.4, 13.2, 2.4, 16.8, 1.2, 3.0, a, semilla=53)
        pts = [pt(M, (0.0, 12.4, -4.0))]                                                        # el pico, atras y arriba
        for d in ((0.0, 3.4, -2.6), (0.0, 2.0, -3.4), (0.0, 0.2, -3.2)):
            pts.append(pts[-1] + M[:3, :3] @ np.array(d))
        for k, (p0, p1) in enumerate(zip(pts[:-1], pts[1:])):
            g = 9.0 - k * 2.6
            hueso(out, p0, p1, g, a, alto=g * 0.85, semilla=54 + k)
        nudo = pts[-2] + (pts[-1] - pts[-2]) * 0.55                                               # la cuerda que lo ata
        eje = _u(pts[-1] - pts[-2])
        hueso(out, nudo - eje * 0.7, nudo + eje * 0.7, 4.6, P['cuerda'], alto=4.2, semilla=58)
        for k, dx in enumerate((-0.9, 0.0, 0.9)):                                               # el remate deshilachado
            fibras(out, P, np.eye(4), pts[-1] + np.array((dx, 0.0, 0.0)), eje + np.array((dx * 0.25, 0.3, 0.0)),
                   4.0, ancho=1.8, caida=0.9, semilla=59 + k)
    else:                                                                                      # la Nana: los agujeros que silban
        bm.cubo(out, M, -6.8, 10.4, -5.6, 13.6, 4.4, 11.6, c, semilla=60)                       # la cascara alta
        bm.cubo(out, M, -5.0, 14.8, -4.4, 10.0, 3.2, 8.8, c, semilla=61)
        bm.cubo(out, M, -3.0, 18.0, -2.8, 6.0, 1.6, 5.6, c, semilla=62)
        bm.cubo(out, M, -1.0, 10.4, 5.4, 2.0, 7.6, 0.9, P['arista'], semilla=63)                 # la arista, de frente
        for x, y in ((-3.2, 11.8), (3.2, 11.8), (-3.2, 13.8), (3.2, 13.8), (-2.4, 16.2), (2.4, 16.2)):
            z = 6.0 if y < 14.8 else 4.4
            bm.cubo(out, M, x - 0.8, y - 0.8, z, 1.6, 1.6, 0.25, P['agujero'], semilla=64)
        for lado in (-1, 1):
            for z in (-3.0, 0.0, 3.0):
                bm.cubo(out, M, (6.8 if lado > 0 else -7.05), 11.8, z - 0.8, 0.25, 1.6, 1.6, P['agujero'], semilla=65)
            for z in (-1.5, 1.5):
                bm.cubo(out, M, (5.0 if lado > 0 else -5.25), 15.6, z - 0.8, 0.25, 1.6, 1.6, P['agujero'], semilla=66)


# ----------------------------------------------------------------------
#  Las posturas
# ----------------------------------------------------------------------
# Cada postura: lo que abre la boca, el cabeceo y el giro de la cabeza, y por cada brazo (izquierdo x>0, derecho x<0)
# el codo, la muñeca, adonde apuntan los dedos, el dorso de la mano y lo que se cierran.
POSTURAS = {
    # al acecho: encorvado, una mano apoyada en el suelo con las garras clavadas y la otra alzada hacia ti, abierta
    'acecho': dict(abre=0.5, cab=(0.12, 0.0),
                   codo=((23.5, 26.0, 6.0), (-21.5, 21.0, -1.0)), muneca=((19.5, 31.0, 18.0), (-20.5, 6.6, 6.0)),
                   hacia=((-0.2, 1.0, 0.55), (-0.1, -0.35, 1.0)), dorso=((-0.15, 0.35, -1.0), (0.0, 1.0, 0.25)),
                   cierra=(0.55, 0.9), abierta=(1.0, 0.7)),
    # lleno: con alguien en la barriga; la boca casi cerrada, las dos manos en el suelo
    'lleno': dict(abre=0.12, cab=(0.2, 0.0),
                  codo=((21.5, 21.0, -1.0), (-21.5, 21.0, -1.0)), muneca=((20.5, 6.6, 6.0), (-20.5, 6.6, 6.0)),
                  hacia=((0.1, -0.35, 1.0), (-0.1, -0.35, 1.0)), dorso=((0.0, 1.0, 0.25), (0.0, 1.0, 0.25)),
                  cierra=(0.9, 0.9), abierta=(0.7, 0.7)),
    # el reposo de la malla del juego: como 'lleno', pero con la boca cerrada; las animaciones salen de aqui
    'reposo': dict(abre=0.04, cab=(0.12, 0.0),
                   codo=((21.5, 21.0, -1.0), (-21.5, 21.0, -1.0)), muneca=((20.5, 6.6, 6.0), (-20.5, 6.6, 6.0)),
                   hacia=((0.1, -0.35, 1.0), (-0.1, -0.35, 1.0)), dorso=((0.0, 1.0, 0.25), (0.0, 1.0, 0.25)),
                   cierra=(0.9, 0.9), abierta=(0.7, 0.7)),
    # agarra: las dos manos delante, apretando a un jugador a la altura del pecho, y las fauces abiertas del todo
    'agarra': dict(abre=0.85, cab=(-0.05, 0.0),
                   codo=((21.0, 26.0, 10.0), (-21.0, 26.0, 10.0)), muneca=((10.5, 30.0, 25.0), (-10.5, 30.0, 25.0)),
                   hacia=((-1.0, 0.25, 0.35), (1.0, 0.25, 0.35)), dorso=((0.3, 0.2, 1.0), (-0.3, 0.2, 1.0)),
                   cierra=(1.1, 1.1), abierta=(0.6, 0.6)),
}
PANZA = dict(centro=(0.0, 15.6, 4.0), rx=12.4, ry=(10.6, 12.0), rz=(8.0, 11.0))


# ----------------------------------------------------------------------
#  El Coco
# ----------------------------------------------------------------------
def coco(tipo='A', postura='acecho', lleno=False, escala=1.0 / 16):
    """El Coco mirando a +z: (los quads, info). 'lleno', con alguien dentro: la barriga mas hinchada."""
    V = VARIANTES[tipo]
    P = pintores(V)
    Q = POSTURAS[postura] if isinstance(postura, str) else postura
    corto = V['corto']
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        I = np.eye(4)
        pl = P['piel']
        PARTE('cuerpo', None, vr.T(0.0, 13.0, -4.0))
        # el cuerpo: la cadera detras de la barriga y el tronco, echado adelante, con la giba (cajas de cantos comidos,
        # no en rodajas)
        Mt = vr.T(0.0, 20.0, -6.0) @ vr.Rx(0.38) @ vr.T(0.0, -20.0, 6.0)
        caja_r(out, I, -10.5, 8.0, -12.0, 21.0, 15.0, 11.0, pl, b=2.5, semilla=1)                 # la cadera
        PARTE('tronco', 'cuerpo', Mt @ vr.T(0.0, 20.0, -6.0))
        caja_r(out, Mt, -13.0, 20.0, -11.0, 26.0, 16.0, 16.0, pl, b=3.0, semilla=2)               # el tronco
        caja_r(out, Mt, -9.6, 35.0, -11.6, 19.2, 7.0, 10.0, pl, b=2.2, semilla=3)                 # la giba
        for lado in (-1, 1):                                                                   # los hombros
            caja_r(out, Mt, lado * 14.8 - 4.6, 29.0, -7.6, 9.2, 9.2, 9.2, pl, b=2.0, semilla=4)
        if corto == 'saco':                                                                    # la capa de arpillera
            ap = P['arpillera']
            caja_r(out, Mt, -16.6, 36.0, -13.0, 33.2, 4.0, 14.4, ap, b=1.4, semilla=30)
            caja_r(out, Mt, -13.4, 19.0, -14.6, 26.8, 19.0, 4.0, ap, b=1.2, semilla=31)
            for j, x in enumerate(np.arange(-12.4, 12.5, 2.2)):                               # el bajo, deshilachado
                largo = (2.6, 4.2, 1.8, 3.4, 5.0, 2.2, 3.8)[j % 7]
                bm.cubo(out, Mt, x - 1.0, 19.0 - largo, -14.4, 2.0, largo + 0.4, 3.0, ap, semilla=32)
        # la barriga: grande y colgante, que sale por delante del tronco; llena (con alguien dentro), mas hinchada
        k = 1.0 if not lleno else 1.1
        bw, bh, bd = 23.0 * k, 22.0 * k, 16.0 * k
        PARTE('barriga', 'cuerpo', vr.T(0.0, 3.6 + bh / 2, 1.0))
        caja_r(out, I, -bw / 2, 3.6, -3.0, bw, bh, bd, P['panza'], b=2.6, semilla=9)
        zf = -3.0 + bd
        caja_r(out, I, -bw / 2 + 3.0, 6.6, zf - 1.0, bw - 6.0, bh - 6.0, 4.2 * k, P['panza'], b=1.6, semilla=10)
        zf = zf + 3.2 * k
        cy = 3.6 + bh / 2
        if corto == 'saco':                                                                    # la barriga cosida como un saco
            for y in np.arange(cy - 7.0, cy + 7.5, 2.0):
                for s_ in (-1, 1):
                    bm.cubo(out, vr.T(0.0, y, zf + 0.2) @ vr.Rz(s_ * 0.8), -1.6, -0.3, -0.3, 3.2, 0.6, 0.6, P['hilo'],
                            semilla=11)
            Mr = vr.T(-8.6, cy + 2.0, zf - 2.2) @ vr.Ry(-0.45)
            bm.cubo(out, Mr, -2.8, -2.8, 0.0, 5.6, 5.6, 0.8, P['arpillera'], semilla=12)        # el remiendo
            for j in range(4):
                bm.cubo(out, Mr @ vr.T(-2.8 + j * 1.85, 2.8, 0.8), -0.25, -0.6, 0.0, 0.5, 1.2, 0.3, P['hilo'], semilla=13)
        # las piernas: cortas, gordas y arqueadas
        for lado in (-1, 1):
            cad = np.array((lado * 8.6, 13.0, -7.0))
            rod = np.array((lado * 14.6, 8.6, -2.6))
            tob = np.array((lado * 13.0, 3.2, -1.6))
            ld = 'i' if lado > 0 else 'd'
            PARTE('pierna_' + ld, 'cuerpo', vr.T(*cad))
            hueso(out, cad, rod, 8.0, pl, semilla=14)
            PARTE('canilla_' + ld, 'pierna_' + ld, vr.T(*rod))
            hueso(out, rod, tob, 6.2, pl, semilla=15)
            PARTE('pie_' + ld, 'canilla_' + ld, vr.T(*tob))
            pie(out, P, tob, lado * 0.3, semilla=16)
        # la cabeza: baja y adelantada, colgando de la giba por un cuello corto
        cp, cg = Q['cab']
        Mh = vr.T(0.0, 38.4, 16.0) @ vr.Ry(cg) @ vr.Rx(cp)
        EN('tronco')
        hueso(out, pt(Mt, (0.0, 34.0, 0.0)), pt(Mh, (0.0, 1.0, -4.0)), 10.0, pl, alto=8.0, semilla=17)
        PARTE('cabeza', 'cuerpo', vr.T(0.0, 38.4, 16.0))
        cabeza(out, P, V, Mh, Q['abre'])
        EN('tronco')
        if corto == 'gloton':                                                                  # la estopa de la giba
            for k, (z, alto) in enumerate(((-3.0, 7.0), (-6.0, 8.0), (-9.0, 6.5))):
                fibras(out, P, Mt, (0.0, 41.8, z), (0.0, 1.0, -0.8), alto, ancho=2.6, caida=0.5, semilla=70 + k)
        # los brazos larguisimos y las manos
        for i, lado in enumerate((1, -1)):
            hom = pt(Mt, (lado * 14.8, 33.6, -3.0))
            codo, mun = np.array(Q['codo'][i], float), np.array(Q['muneca'][i], float)
            ld = 'i' if lado > 0 else 'd'
            PARTE('brazo_' + ld, 'tronco', vr.T(*hom))
            hueso(out, hom, codo, 5.8, pl, semilla=19)
            PARTE('antebrazo_' + ld, 'brazo_' + ld, vr.T(*codo))
            hueso(out, codo, mun, 5.4, pl, semilla=20)
            PARTE('mano_' + ld, 'antebrazo_' + ld, vr.T(*mun))
            mano(out, P, mun, Q['hacia'][i], Q['dorso'][i], Q['cierra'][i], Q['abierta'][i], nombre='mano_' + ld,
                 semilla=21)
    finally:
        bm.PPB = ppb
    E = np.diag([escala, escala, escala, 1.0])
    out = qm.transformar(out, E)
    return out, {'cabeza': pt(E, pt(Mh, (0.0, 2.0, 4.0))), 'ojos': pt(E, pt(Mh, (0.0, 4.0, 9.0))),
                      'boca': pt(E, pt(Mh, (0.0, -3.0, 4.0))), 'panza': pt(E, np.array(PANZA['centro'])),
                      'luz': V['luz']}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

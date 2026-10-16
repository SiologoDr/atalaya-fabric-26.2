"""
El Tragaldabas (15-10-2026): el mob que te traga. Juan, al guardar el Trasgo: «guárdalos en mobs, sube todo y haz otro
mob». De su lista quedaba «la rana gigante que te come y te atrapa» (el Sapo de Dedsafio 3); este es nuestro: un bicho
creible, rechoncho, que es casi todo boca.

La cabezota ancha y plana con las fauces de oreja a oreja y las filas de dientes de aguja, la garganta que brilla, los
ojos saltones encima de la cabeza, las patas de delante cortas y palmeadas y las de detras grandes, plegadas para el
salto; y el buche: una barriga translucida que brilla, donde se ve lo que se ha tragado.

    A  de Lengua     pardo de cienaga, con la lengua larga y pegajosa: te atrapa con ella desde lejos y te arrastra a
                     la boca
    B  de Cebo       azul pizarra, de cueva, con la antena y el cebo que brilla como un mineral: se entierra y solo
                     asoma el cebo; si te acercas, el suelo se abre en fauces bajo tus pies
    C  Escupidor     granate, con los carrillos hinchados y la cresta de puas: te traga, te ves dentro de su buche, y
                     luego te escupe lejos

Se modela como un mob, en pixeles del jugador (16 por bloque), con un texel por pixel. La barriga va aparte, para
pintarla translucida (como la gelatina del Slime).
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
    'A': dict(clave='TGA', nombre='el Tragaldabas de Lengua', corto='lengua',
              piel=_h('16180c', '242a14', '363e1e', '4c562a', '667238'),
              vientre=_h('3a3418', '5a5226', '7c7238', '9e944e', 'c0b668'),
              buche=_h('3a4a10', '5a7018', '82a02a', 'aed040', 'd8f480', 'f4ffc0'),
              ojo=_h('ffb43a', 'fff0b0'), boca=_h('ff7a2a', 'ffd08a'), luz='ffb43a'),
    'B': dict(clave='TGB', nombre='el Tragaldabas de Cebo', corto='cebo',
              piel=_h('0e1218', '182030', '243046', '344460', '4a5e80'),
              vientre=_h('2a3040', '3e4658', '565e72', '70788c', '8c94a6'),
              buche=_h('0e3a4a', '145a70', '1e8098', '3ab0c8', '7adcec', 'd0f8ff'),
              ojo=_h('6ae8ff', 'e0faff'), boca=_h('3ad0ff', 'c8f4ff'), luz='6ae8ff'),
    'C': dict(clave='TGC', nombre='el Tragaldabas Escupidor', corto='escupidor',
              piel=_h('1a0a0e', '2c1218', '441c24', '5e2832', '7c3842'),
              vientre=_h('4a2a24', '6a3c32', '8c5244', 'ae6c58', 'cc8a72'),
              buche=_h('4a0e3a', '701658', '9a2278', 'c43a9c', 'e87ac4', 'ffc4ec'),
              ojo=_h('d8ff4a', 'f6ffc8'), boca=_h('ff4aa8', 'ffc0e4'), luz='ff6ac0'),
}
DIENTE = _h('8a8068', 'c8bea0', 'f0ead6')
LENGUA = _h('5a1420', '86202e', 'b03444', 'd65264', 'f08494')


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
    piel, vientre, buche, ojo, boca = V['piel'], V['vientre'], V['buche'], V['ojo'], V['boca']

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'tg%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def p_piel(tw, th, cara_, s):
        """La piel del lomo: lisa, con las verrugas en rejilla (cada una de 2 x 2, con la luz arriba) y el canto de abajo
        mas oscuro. Limpia, sin motas sueltas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        fila = ys // 5
        verruga = (((xs + (fila % 2) * 3) % 6) < 2) & ((ys % 5) < 2)
        idx[verruga] = 3
        idx[verruga & ((ys % 5) == 0)] = 4
        if cara_ not in ('arriba', 'abajo'):
            idx[th - 1, :] = 1
        if cara_ == 'abajo':
            idx[...] = 1
        return _pinta(idx, piel), None
    reg('piel', p_piel)

    def p_vientre(tw, th, cara_, s):
        """El vientre y la garganta por fuera: claro, en pliegues (bandas) a lo ancho."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys % 3) == 0, 2, 3)
        return _pinta(idx, vientre), None
    reg('vientre', p_vientre)

    def p_buche(tw, th, cara_, s):
        """El buche translucido: el canto un tono mas claro, unas venas que brillan (pocas, largas) y el brillo en ele."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        borde = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)
        idx[borde] = 4
        vena = ((xs + ys // 2 + s) % 9 == 0) & (ys > 0) & (ys < th - 1)
        idx[vena] = 5
        if tw >= 8 and th >= 6:
            idx[1, 1:5] = 5
            idx[1:3, 1] = 5
        t = _pinta(idx, buche)
        return t, _emis(t, idx >= 5, 70)
    reg('buche', p_buche)

    def p_boca(tw, th, cara_, s):
        """La boca por dentro: carne oscura, con la luz de la garganta que sube del fondo en bandas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (40, 10, 14, 255)
        f = ys / max(th - 1, 1)
        luz = np.zeros((th, tw), bool)
        if cara_ in ('arriba', 'abajo'):                                          # el paladar y la lengua: bandas de luz al fondo
            luz = (f < 0.3) & ((ys % 2) == 0)
            t[(ys % 3) == 1] = (70, 18, 24, 255)
        t[luz] = (*boca[0], 255)
        return t, _emis(t, luz, 160)
    reg('boca', p_boca)

    def p_garganta(tw, th, cara_, s):
        """El fondo de la garganta: el neon con el centro casi blanco."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*boca[0], 255)
        cen = (np.abs(xs - (tw - 1) / 2) <= tw / 4) & (np.abs(ys - (th - 1) / 2) <= th / 4)
        t[cen] = (*boca[1], 255)
        return t, _emis(t, np.ones((th, tw), bool), 230)
    reg('garganta', p_garganta, pleno=True)

    def p_diente(tw, th, cara_, s):
        """El diente de aguja, en hoja: la base arriba y la punta abajo."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            w = tw * (th - y) / th
            a, b = (tw - w) / 2, (tw + w) / 2
            for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                t[y, x] = (*(DIENTE[2] if x < tw / 2 else DIENTE[1]), 255)
        return t, None
    reg('diente', p_diente)

    def p_ojo(tw, th, cara_, s):
        """El ojo saltón: el iris que brilla con la pupila de raja en vertical y el parpado oscuro arriba."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*ojo[0], 255)
        t[(np.abs(xs - (tw - 1) / 2) < 0.6)] = (20, 10, 6, 255)
        t[ys == 0] = (*piel[1], 255)
        t[(ys == th // 2) & (np.abs(xs - (tw - 1) / 2) >= 1.5)] = (*ojo[1], 255)
        luz = (ys > 0) & (np.abs(xs - (tw - 1) / 2) >= 0.6)
        return t, _emis(t, luz, 230)
    reg('ojo', p_ojo)

    def p_lengua(tw, th, cara_, s):
        """La lengua: rosa, humeda, con el surco claro en medio."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(np.abs(xs - (tw - 1) / 2) < 0.6, 4, np.where((ys % 4) == 0, 2, 3))
        return _pinta(idx, LENGUA), None
    reg('lengua', p_lengua)

    def p_cebo(tw, th, cara_, s):
        """El cebo: brilla como una gema de cueva, facetado (los filos claros) con el centro casi blanco."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*buche[3], 255)
        t[(xs == 0) | (ys == 0)] = (*buche[5], 255)
        t[(xs == tw - 1) | (ys == th - 1)] = (*buche[2], 255)
        return t, _emis(t, np.ones((th, tw), bool), 255)
    reg('cebo', p_cebo, pleno=True)

    def p_una(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys >= th - max(1, th // 3), 3, 2)
        return _pinta(idx, DIENTE), None
    reg('una', p_una)
    return P


# ----------------------------------------------------------------------
#  Las piezas
# ----------------------------------------------------------------------
def hoja(out, P4, pintor, ancho, alto, semilla=0):
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def tramo(out, a, b, grosor, pintor, semilla=0, alto=None):
    bm.viga(out, a, b, grosor, alto or grosor, pintor, extra=grosor * 0.3, semilla=semilla)


def diente(out, P, M, x, z, largo, hacia, semilla=0):
    """Un diente de aguja en dos hojas cruzadas, desde (x, 0, z) del marco M hacia abajo (-1) o hacia arriba (+1)."""
    base = pt(M, (x, 0.0, z))
    eje = M[:3, :3] @ np.array((0.0, hacia, 0.0))
    for ll in (M[:3, 0], M[:3, 2]):
        ll = _u(ll) * 0.75
        punta = base + eje * largo
        hoja(out, (punta - ll * 0.08, punta + ll * 0.08, base + ll, base - ll), P['diente'], 1.5, largo, semilla)


def redondo(out, M, cx, cy, cz, rx, ry, rz, pintor, pisos=None, caras=None, semilla=0):
    """Un cuerpo redondo de pixel: pisos de tres cajas cruzadas (la planta casi redonda) del ancho de la elipse."""
    n = pisos or max(3, int(round(ry)))
    h = 2 * ry / n
    for j in range(n):
        y0 = -ry + j * h
        ym = y0 + h / 2
        f = math.sqrt(max(0.0, 1 - (ym / ry) ** 2))
        w, d = rx * f, rz * f
        if w < 0.6 or d < 0.6:
            continue
        for (a, b) in ((1.0, 0.62), (0.62, 1.0), (0.86, 0.86)):
            bm.cubo(out, M @ vr.T(cx, cy, cz), -w * a, y0, -d * b, 2 * w * a, h, 2 * d * b, pintor, caras=caras,
                    semilla=semilla + j)


def pata_delante(out, P, hombro, codo, mano, semilla=0):
    """La pata de delante: corta y gruesa, con la mano palmeada de tres dedos y garras."""
    tramo(out, hombro, codo, 6.5, P['piel'], semilla)
    tramo(out, codo, mano, 5.0, P['piel'], semilla + 1)
    for k, ang in enumerate((-0.7, 0.0, 0.7)):
        d = np.array((math.sin(ang), 0.0, math.cos(ang)))
        p1 = np.asarray(mano, float) + d * 4.5 + np.array((0.0, -0.4, 0.0))
        tramo(out, mano, p1, 1.6, P['piel'], semilla + 2, alto=1.0)
        tramo(out, p1, p1 + d * 1.6 + np.array((0.0, -0.6, 0.0)), 0.8, P['una'], semilla + 3)
    hoja(out, (np.asarray(mano) + np.array((-3.0, -0.6, 3.0)), np.asarray(mano) + np.array((3.0, -0.6, 3.0)),
               np.asarray(mano) + np.array((2.0, -0.4, 0.5)), np.asarray(mano) + np.array((-2.0, -0.4, 0.5))),
         P['piel'], 6.0, 3.0, semilla)                                                          # la membrana


def pata_detras(out, P, cadera, rodilla, tobillo, pie, semilla=0):
    """La pata de detras, grande y plegada para el salto: el muslo grueso, la espinilla, el tobillo y el pie largo."""
    tramo(out, cadera, rodilla, 8.0, P['piel'], semilla)
    tramo(out, rodilla, tobillo, 5.0, P['piel'], semilla + 1)
    tramo(out, tobillo, pie, 3.6, P['piel'], semilla + 2)
    for k, ang in enumerate((-0.5, 0.0, 0.5)):
        d = np.array((math.sin(ang), 0.0, math.cos(ang)))
        p1 = np.asarray(pie, float) + d * 5.0
        tramo(out, pie, p1, 1.6, P['piel'], semilla + 3, alto=1.0)
        tramo(out, p1, p1 + d * 1.6 + np.array((0.0, -0.5, 0.0)), 0.8, P['una'], semilla + 4)


# ----------------------------------------------------------------------
#  El Tragaldabas
# ----------------------------------------------------------------------
def tragaldabas(tipo='A', abre=0.5, lengua=None, enterrado=False, lleno=False, escala=1.0 / 16):
    """El Tragaldabas sentado y mirando a +z: (lo opaco, el buche translucido, info). 'abre' abre la boca (radianes);
    'lengua' es el punto (pixeles) adonde llega la lengua, si la saca; 'enterrado' lo deja con la cabeza a ras de suelo
    y las fauces hacia arriba (el de Cebo, cuando se abre bajo tus pies); 'lleno', con el buche hinchado (cuando se ha
    tragado a alguien: cabe un jugador sentado)."""
    V = VARIANTES[tipo]
    P = pintores(V)
    corto = V['corto']
    ppb = bm.PPB
    bm.PPB = PPB
    out, gel = [], []
    try:
        M0 = vr.T(0.0, -21.0, 23.0) @ vr.Rx(-1.35) if enterrado else np.eye(4)        # la boca a ras de suelo, hacia arriba
        # el lomo: redondo, echado un poco hacia atras, y la grupa
        redondo(out, M0, 0.0, 22.0, -10.0, 17.0, 12.0, 16.0, P['piel'], pisos=8, semilla=1)
        redondo(out, M0, 0.0, 16.0, -20.0, 14.0, 10.0, 10.0, P['piel'], pisos=6, semilla=2)
        # el buche, translucido: la barriga apoyada en el suelo, entre las patas
        if lleno:
            Mb = M0 @ vr.T(0.0, 13.6, 0.0)
            redondo(gel, Mb, 0.0, 0.0, 0.0, 15.5, 13.6, 15.0, P['buche'], pisos=9, semilla=3)
        else:
            Mb = M0 @ vr.T(0.0, 9.5, -3.0)
            redondo(gel, Mb, 0.0, 0.0, 0.0, 12.0, 9.5, 11.0, P['buche'], pisos=7, semilla=3)
            bm.cubo(out, Mb, -1.6, -2.0, -1.6, 3.2, 3.2, 3.2, P['garganta'], semilla=4)              # la luz de dentro
        # la cabezota: la mandibula de arriba (el labio, la cupula redondeada, los orificios y el ceño) y la de abajo
        Mh = M0 @ vr.T(0.0, 27.0, 2.0)
        bm.cubo(out, Mh, -17.0, 0.0, -6.0, 34.0, 3.0, 23.0, P['piel'], caras={'abajo': P['boca']}, semilla=5)
        bm.cubo(out, Mh, -16.5, -1.0, 13.0, 33.0, 1.6, 4.4, P['vientre'], caras={'abajo': P['boca']}, semilla=6)  # el labio
        redondo(out, Mh, 0.0, 3.0, 4.0, 17.0, 5.5, 12.5, P['piel'], pisos=4, semilla=15)                # la cupula
        for lado in (-1, 1):
            bm.cubo(out, Mh, lado * 3.0 - 1.0, 4.4, 14.6, 2.0, 1.0, 1.2, P['boca'], semilla=16)          # los orificios
        Mq = Mh @ vr.T(0.0, -0.5, -5.0) @ vr.Rx(abre)
        bm.cubo(out, Mq, -16.0, -3.0, 0.0, 32.0, 3.0, 22.0, P['vientre'], caras={'arriba': P['boca']}, semilla=7)
        redondo(out, Mq, 0.0, -3.8, 11.0, 15.0, 2.8, 10.5, P['vientre'], pisos=3, semilla=17)           # la barbilla
        bm.cubo(out, Mh, -12.0, -6.0, -5.0, 24.0, 6.0, 2.0, P['garganta'], semilla=8)                 # el fondo
        for x in np.arange(-15.0, 15.5, 2.6):                                                    # los dientes de aguja
            largo = 4.6 if abs(x) > 11 else 3.2 + (abs(int(x * 10)) % 3) * 0.5
            diente(out, P, Mh @ vr.T(0.0, -1.2, 0.0), x, 17.0, largo, -1.0, semilla=9)
            diente(out, P, Mq, x + 1.3, 22.0, largo * 0.8, 1.0, semilla=10)
        for z in np.arange(-2.0, 16.0, 3.4):                                                     # y por los lados
            for lado in (-1, 1):
                diente(out, P, Mh @ vr.T(0.0, -1.2, 0.0), lado * 16.4, z, 2.6, -1.0, semilla=11)
        # los ojos saltones, encima de la cabeza
        for lado in (-1, 1):
            Mo = Mh @ vr.T(lado * 10.0, 8.0, 7.0)
            redondo(out, Mo, 0.0, 3.0, -1.0, 5.0, 4.0, 5.0, P['piel'], pisos=3, semilla=12)
            bm.cubo(out, Mo, -3.6, 1.0, 3.6, 7.2, 4.8, 1.0, P['ojo'], semilla=14)                       # el ojo saltón
            bm.cubo(out, Mo @ vr.Rz(lado * 0.3), -4.8, 5.8, -3.0, 9.6, 1.8, 6.0, P['piel'], semilla=13)  # el ceño
        # las patas
        for lado in (-1, 1):
            pata_delante(out, P, pt(M0, (lado * 13.0, 18.0, 6.0)), pt(M0, (lado * 17.0, 9.0, 10.0)),
                         pt(M0, (lado * 16.0, 1.2, 14.0)), semilla=20)
            pata_detras(out, P, pt(M0, (lado * 12.0, 14.0, -20.0)), pt(M0, (lado * 21.0, 18.0, -6.0)),
                        pt(M0, (lado * 19.0, 4.0, -20.0)), pt(M0, (lado * 18.0, 1.2, -8.0)), semilla=30)
        # lo de cada tipo
        if corto == 'lengua' or lengua is not None:
            base = pt(Mq, (0.0, 0.2, 10.0))
            fin = np.asarray(lengua, float) if lengua is not None else pt(Mq, (0.0, -1.0, 30.0)) + np.array((0.0, -6.0, 0.0))
            n = 8
            pts = [base + (fin - base) * (k / n) + np.array((0.0, -math.sin(math.pi * k / n) * 2.0, 0.0)) for k in range(n + 1)]
            for a, b in zip(pts[:-1], pts[1:]):
                tramo(out, a, b, 4.0, P['lengua'], semilla=40, alto=1.8)
            redondo(out, np.eye(4), *fin, 3.4, 2.6, 3.4, P['lengua'], pisos=3, semilla=41)       # la punta pegajosa
        if corto == 'cebo':                                                                      # la antena y el cebo
            pts = [pt(Mh, (0.0, 9.0, 8.0))]
            for d in ((0.0, 5.0, 2.0), (0.0, 4.0, 4.0), (0.0, 2.0, 5.0), (0.0, -1.0, 4.0)):
                pts.append(pts[-1] + Mh[:3, :3] @ np.array(d))
            for a, b in zip(pts[:-1], pts[1:]):
                tramo(out, a, b, 1.4, P['piel'], semilla=42)
            Mc = vr.T(*(pts[-1] + Mh[:3, :3] @ np.array((0.0, -2.5, 0.0))))
            for g in (0.0, math.pi / 4):
                bm.cubo(out, Mc @ vr.Ry(g), -1.8, -2.5, -1.8, 3.6, 5.0, 3.6, P['cebo'], semilla=43)
        if corto == 'escupidor':                                                                 # los carrillos y la cresta
            for lado in (-1, 1):
                redondo(gel, Mh, lado * 18.5, 0.0, 6.0, 4.0, 4.5, 6.5, P['buche'], pisos=4, semilla=44)
            for k in range(6):
                b = pt(M0, (0.0, 34.0 - k * 1.0, -2.0 - k * 4.5))
                arriba = _u(np.array((0.0, 1.0, -0.35)))
                ll = np.array((0.9, 0.0, 0.0))
                largo = 6.0 - abs(k - 2) * 0.8
                hoja(out, (b - ll, b + ll, b + arriba * largo + ll * 0.1, b + arriba * largo - ll * 0.1), P['una'], 1.8,
                     largo, semilla=45)
    finally:
        bm.PPB = ppb
    E = np.diag([escala, escala, escala, 1.0])
    out, gel = qm.transformar(out, E), qm.transformar(gel, E)
    return out, gel, {'cabeza': pt(E, pt(Mh, (0.0, 4.0, 18.0))), 'buche': pt(E, pt(Mb, (0.0, 0.0, 0.0))),
                      'luz': V['luz'], 'boca': pt(E, pt(Mh, (0.0, -2.0, 10.0)))}


def dibujar(lz, cam, qs, gel, luces, ambiente, niebla=None, brillo=1.4, transl=0.28):
    """Lo opaco y despues el buche translucido (como la gelatina del Slime). Cada piso del buche son tres cajas
    cruzadas, asi que delante de lo que hay dentro se juntan varias capas: cada una, poco opaca."""
    import slime_modelo as sl
    sl.dibujar(lz, cam, qs, gel, luces, ambiente, niebla, brillo, transl=transl, brilla=False)

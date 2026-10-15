"""
El Izador (15-10-2026): el primer mob «que hace algo». Juan: «ahora vamos a crear mobs que hagan algo; puedes
investigar Dedsafio 3 y 4 sobre sus mobs, como el creeper pastel, el flashbang, la rana gigante que te come y te
atrapa, un mob que te agarra y te lleva al aire, un mob que se te aferra al cuerpo...; haz uno con sus 3 tipos».

El Izador te agarra y te lleva al aire, y ademas te atrapa (como el sapo de Dedsafio 3): es un globo aerostatico vivo.
Arriba, el saco de gas que brilla por dentro; colgando de unas cuerdas de tendon, la jaula de costillas, que es su
barquilla; delante asoma la cabeza con las fauces encendidas, y dos brazos largos con garfios te enganchan y te meten
en la jaula. Dentro cuelga su corazon, un farol: es el punto debil.

    A  de Fuego      un saco grande y redondo, en gajos, que arde por dentro como un globo: te sube muy alto y abre la
                     jaula
    B  de Tormenta   tres sacos de nube oscura con venas de rayo y la jaula de cobre: te sube a la tormenta y los
                     rayos caen en la jaula
    C  de Cienaga    un saco largo, como un dirigible, de gas verde, con musgo y lianas: te lleva lejos, a su nido, y
                     te separa de los tuyos

Se modela como un mob: en pixeles del modelo con un texel por pixel, y luego se agranda.
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
    'A': dict(clave='IZA', nombre='el Izador de Fuego', corto='fuego', escala=0.9,
              hueso=_h('3a2e24', '5a4836', '806a50', 'a89070', 'cdb894'),
              piel=_h('140e0c', '1e1612', '2a201a', '382a22', '4a382c'),
              saco=_h('3a140a', '6a2410', 'a83c14', 'e0661e', 'ffa040', 'ffd890'),
              neon=_h('ff7a1a', 'ffd27a', 'fff4d8'), luz='ff8a2a'),
    'B': dict(clave='IZB', nombre='el Izador de Tormenta', corto='tormenta', escala=0.9,
              hueso=_h('1e3a34', '2e5a4c', '3e7a64', '62a084', '9cc8a8'),
              piel=_h('0e1018', '161a26', '202636', '2c3448', '3c465c'),
              saco=_h('0e121c', '181e2c', '242c3e', '343e56', '4c5a78', '7a8aac'),
              neon=_h('5ad8ff', 'b8f0ff', 'f0fcff'), luz='6ad8ff'),
    'C': dict(clave='IZC', nombre='el Izador de Ciénaga', corto='cienaga', escala=0.9,
              hueso=_h('2a2414', '423a20', '5e5430', '7e7444', 'a49a62'),
              piel=_h('0e140a', '162010', '202c16', '2c3a1e', '3a4a28'),
              saco=_h('10200c', '1c3814', '2c5420', '42782e', '62a040', '9cd474'),
              neon=_h('a4ff4a', 'd8ff9a', 'f6ffe0'), luz='a4ff4a'),
}


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


NIVELES = 8          # los pisos del saco, de abajo arriba (para que brille mas abajo, donde esta el fuego)


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    hue, piel, saco, neon = V['hueso'], V['piel'], V['saco'], V['neon']
    tipo = V['corto']

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'iz%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def p_hueso(tw, th, cara_, s):
        """El hueso (las costillas, el espinazo, los garfios): el canto claro a un lado y oscuro al otro, y un anillo
        mas oscuro cada cuatro pixeles a lo largo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        if tw >= 2:
            idx[:, 0] = 3
            idx[:, -1] = 1
        idx[(ys % 5) == 4] = 1
        if cara_ in ('arriba', 'abajo'):
            idx = np.full((th, tw), 3)
        return _pinta(idx, hue), None
    reg('hueso', p_hueso)

    def p_piel(tw, th, cara_, s):
        """La piel de la cabeza y los brazos: oscura, en placas de bandas (una raya clara cada cuatro filas) y el canto
        de abajo mas oscuro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx[(ys % 4) == 0] = 3
        idx[ys == th - 1] = 1
        if tw >= 3:
            idx[:, -1] = np.minimum(idx[:, -1], 1)
        return _pinta(idx, piel), None
    reg('piel', p_piel)

    def p_cuerda(tw, th, cara_, s):
        """Las cuerdas de tendon de las que cuelga la jaula: trenzadas, en rayas en diagonal."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs + ys) % 3) == 0, 1, 2)
        return _pinta(idx, hue), None
    reg('cuerda', p_cuerda)

    def saco_nivel(nivel):
        f0 = nivel / max(NIVELES - 1, 1)                                         # 0 abajo, 1 arriba

        def f(tw, th, cara_, s):
            """El saco de gas, en gajos como un globo: cada cara es un gajo, con la costura oscura en las aristas (asi
            casan de un piso a otro) y el centro mas claro; segun el tipo, la luz de dentro: el fuego (mas fuerte abajo),
            el rayo que corre por las costuras o el gas verde."""
            ys, xs = np.mgrid[0:th, 0:tw]
            c = np.abs(xs - (tw - 1) / 2) / max((tw - 1) / 2, 0.5)                # 0 en medio, 1 en la arista
            if tw < 5:
                c = np.full((th, tw), 0.5)                                         # las caras estrechas, de un tono
            idx = np.where(c > 0.8, 1, np.where(c < 0.35, 4, 3))
            costura = c > 0.8
            if tipo == 'fuego':
                idx = idx + (1 if f0 < 0.3 else 0) - (1 if f0 > 0.8 else 0)
                idx[costura] = 1
                luz = ~costura
                alfa = int(190 - 110 * f0)
            elif tipo == 'tormenta':
                idx = np.where(c < 0.35, 3, 2)
                idx[costura] = 5
                luz = costura
                alfa = 230
            else:
                idx[costura] = 1
                luz = idx >= 4
                alfa = 110
            if cara_ in ('arriba', 'abajo'):
                idx = np.full((th, tw), 3 if cara_ == 'arriba' else (4 if tipo == 'fuego' else 2))
                luz = np.full((th, tw), tipo == 'fuego' and cara_ == 'abajo')
            idx = np.clip(idx, 0, len(saco) - 1)
            t = _pinta(idx, saco)
            return t, _emis(t, luz, alfa)
        return f
    for n in range(NIVELES):
        reg('saco%d' % n, saco_nivel(n))

    def p_nucleo(tw, th, cara_, s):
        """El corazon que cuelga en la jaula, un farol: el neon con el centro casi blanco y el canto oscuro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neon[0], 255)
        cen = (np.abs(xs - (tw - 1) / 2) <= tw / 4) & (np.abs(ys - (th - 1) / 2) <= th / 4)
        t[cen] = (*neon[2], 255)
        borde = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)
        t[borde] = (*neon[1], 255)
        return t, _emis(t, np.ones((th, tw), bool), 255)
    reg('nucleo', p_nucleo, pleno=True)

    def p_boca(tw, th, cara_, s):
        """El paladar, en escalones de luz: casi blanco al fondo, el neon y la sombra hacia fuera."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*piel[0], 255)
        f = ys / max(th - 1, 1)
        t[f < 0.66] = (*neon[0], 255)
        t[f < 0.33] = (*neon[2], 255)
        luz = f < 0.66
        if cara_ in ('der', 'izq'):
            t[...] = (*piel[0], 255)
            luz = np.zeros((th, tw), bool)
        return t, _emis(t, luz, 220)
    reg('boca', p_boca)

    def p_diente(tw, th, cara_, s):
        """El diente, en hoja: la base arriba y la punta abajo."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            w = tw * (th - y) / th
            a, b = (tw - w) / 2, (tw + w) / 2
            for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                t[y, x] = (*(hue[4] if x < tw / 2 else hue[3]), 255)
        return t, None
    reg('diente', p_diente)

    def p_ojo(tw, th, cara_, s):
        """El ojo: la cuenca oscura y la pupila rasgada que brilla."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*piel[0], 255)
        pup = (ys == th // 2) & (xs >= 1) & (xs <= tw - 2) if th >= 3 else (xs >= 0)
        t[pup] = (*neon[1], 255)
        return t, _emis(t, pup, 255)
    reg('ojo', p_ojo)

    def p_membrana(tw, th, cara_, s):
        """La membrana de la cresta: oscura, en bandas a lo largo, con el borde libre (arriba) encendido."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs % 3) == 0, 1, 2)
        t = _pinta(idx, piel)
        borde = ys == 0
        t[borde] = (*neon[0], 255)
        return t, _emis(t, borde, 200)
    reg('membrana', p_membrana)

    def p_musgo(tw, th, cara_, s):
        """El musgo y las lianas que cuelgan (el de Cienaga): verde oscuro en rayas, la punta clara."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys + xs) % 4 == 0, 1, 2)
        idx[ys >= th - 1] = 3
        return _pinta(idx, _h('101c0a', '1a2c10', '284218', '3c5c22')), None
    reg('musgo', p_musgo)
    return P


# ----------------------------------------------------------------------
#  Las piezas
# ----------------------------------------------------------------------
def hoja(out, P4, pintor, ancho, alto, semilla=0):
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def viga(out, p0, p1, ancho, pintor, semilla=0):
    bm.viga(out, p0, p1, ancho, ancho, pintor, semilla=semilla)


def curva(out, puntos, ancho, pintor, semilla=0):
    """Un hueso o una cuerda que sigue una curva de puntos, por tramos (que se solapan un poco en las juntas)."""
    for a, b in zip(puntos[:-1], puntos[1:]):
        bm.viga(out, a, b, ancho, ancho, pintor, extra=ancho * 0.35, semilla=semilla)


def globo(out, P, centro, rx, ry, rz, pisos=None, semilla=0, eje='y'):
    """Un saco redondo de pixel: rodajas de dos pixeles, cada una con tres cajas cruzadas (la planta casi redonda), del
    ancho de la elipse en esa rodaja. Con eje='y' las rodajas son pisos (un globo); con eje='z', rodajas a lo largo (un
    dirigible). Cada rodaja lleva su pintor (de abajo arriba, o de atras adelante), para la luz."""
    cx, cy, cz = centro
    largo = ry if eje == 'y' else rz
    n = pisos or max(4, int(round(largo)))
    h = 2 * largo / n
    M0 = vr.T(cx, cy, cz) if eje == 'y' else vr.T(cx, cy, cz) @ vr.Rx(math.pi / 2)
    a1, a2 = (rx, rz) if eje == 'y' else (rx, ry)
    for j in range(n):
        y0 = -largo + j * h
        ym = y0 + h / 2
        f = math.sqrt(max(0.0, 1 - (ym / largo) ** 2))
        w, d = a1 * f, a2 * f
        if w < 0.6 or d < 0.6:
            continue
        nivel = min(NIVELES - 1, int(j / n * NIVELES)) if eje == 'y' else 4
        pin = P['saco%d' % nivel]
        for (a, b) in ((1.0, 0.62), (0.62, 1.0), (0.86, 0.86)):
            bm.cubo(out, M0, -w * a, y0, -d * b, 2 * w * a, h, 2 * d * b, pin, semilla=semilla + j)


def jaula(out, P, base_y, alto, ancho, fondo, abierta=0.0, semilla=0):
    """La jaula de costillas: el espinazo grueso detras, cinco pares de costillas curvas que bajan hacia delante (del
    espinazo a la puerta, que queda abierta en medio), el collar de arriba (de donde cuelga) y la pelvis abajo, que es
    el suelo de la jaula. 'abierta' gira las costillas hacia fuera."""
    zb = -fondo / 2
    vert = [np.array((0.0, base_y - 2.0 + y, zb)) for y in np.linspace(0, alto + 2.0, 8)]
    curva(out, vert, 3.0, P['hueso'], semilla)
    for y in np.linspace(base_y, base_y + alto, 8)[:-1]:                                       # las vertebras
        bm.cubo(out, vr.T(0.0, y, zb), -2.4, 0.6, -2.4, 4.8, 2.2, 3.4, P['hueso'], semilla=semilla + 1)
    for i, y in enumerate(np.linspace(base_y + alto - 3.0, base_y + 6.0, 5)):
        cae = -6.0                                                                             # bajan hacia delante
        for lado in (-1, 1):
            pts = []
            for t in np.linspace(0, 1, 7):
                a = (math.pi - 0.42) * t                                                       # dejan la puerta abierta
                x = lado * (ancho / 2) * math.sin(a)
                z = -math.cos(a) * fondo / 2
                x += lado * abierta * t * t * 6
                z += abierta * t * t * 2
                pts.append(np.array((x, y + cae * t * t, z)))
            curva(out, pts, 2.2, P['hueso'], semilla + 2)
    pts = [np.array((math.sin(a) * (ancho / 2 + 0.5), base_y + alto, -math.cos(a) * (fondo / 2 + 0.5)))
           for a in np.linspace(0.0, TAU, 13)]
    curva(out, pts, 2.0, P['hueso'], semilla + 3)                                              # el collar
    bm.cubo(out, vr.T(0.0, base_y - 1.5, zb + fondo * 0.45), -ancho * 0.36, 0.0, -fondo * 0.45, ancho * 0.72, 2.0,
            fondo * 0.8, P['hueso'], semilla=semilla + 4)                                       # la pelvis, el suelo


def garfio(out, P, base, eje, lado, largo=6.0, semilla=0):
    """Un garfio: tres tramos que se curvan hacia dentro, como un anzuelo."""
    eje = _u(eje)
    pts = [np.asarray(base, float)]
    d = eje.copy()
    giro = np.array((-lado * 0.0, 0.0, 1.0))
    for k in range(4):
        p = pts[-1] + d * (largo / 4)
        pts.append(p)
        d = _u(d + giro * 0.55)
    curva(out, pts, 1.0, P['hueso'], semilla)


def brazo(out, P, hombro, codo, muneca, lado, semilla=0):
    """El brazo largo: el hombro, el brazo y el antebrazo de piel, y la mano de tres garfios."""
    hombro, codo, muneca = (np.asarray(p, float) for p in (hombro, codo, muneca))
    bm.cubo(out, vr.T(*hombro), -2.4, -2.4, -2.4, 4.8, 4.8, 4.8, P['piel'], semilla=semilla)
    viga(out, hombro, codo, 2.6, P['piel'], semilla + 1)
    viga(out, codo, muneca, 2.2, P['piel'], semilla + 2)
    bm.cubo(out, vr.T(*muneca), -1.8, -1.8, -1.8, 3.6, 3.6, 3.6, P['piel'], semilla=semilla + 3)
    eje = _u(muneca - codo)
    for k, dx in enumerate((-1.4, 0.0, 1.4)):
        b = muneca + np.array((dx, 0.0, 0.6 * (k == 1)))
        garfio(out, P, b, eje + np.array((dx * 0.12, 0.0, 0.0)), lado, 6.5 if k == 1 else 5.5, semilla + 4)


def cabeza(out, P, V, M):
    """La cabeza, colgando delante de la jaula y mirando abajo, hacia ti: el craneo largo, la quijada abierta con los
    dientes en hoja, el paladar que brilla, los ojos rasgados y, segun el tipo, lo que la enmarca."""
    tipo = V['corto']
    bm.cubo(out, M, -5.0, 1.0, -6.0, 10.0, 6.5, 11.0, P['piel'], caras={'abajo': P['boca']}, semilla=1)   # el craneo
    bm.cubo(out, M, -4.0, 4.6, -7.5, 8.0, 3.4, 4.0, P['piel'], semilla=1)                             # la nuca
    bm.cubo(out, M, -5.6, 5.4, 3.0, 11.2, 2.2, 3.4, P['piel'], semilla=2)                             # el ceño, que sale
    bm.cubo(out, M, -3.6, 1.0, 5.0, 7.2, 3.0, 4.6, P['piel'], caras={'abajo': P['boca']}, semilla=2)    # el hocico, bajo
    Mq = M @ vr.T(0.0, 1.0, -5.0) @ vr.Rx(0.78)                                                         # la quijada
    bm.cubo(out, Mq, -4.4, -2.6, 0.0, 8.8, 2.6, 14.0, P['piel'], caras={'arriba': P['boca']}, semilla=3)
    for x in (-3.0, -1.5, 0.0, 1.5, 3.0):                                                            # los dientes
        for (Mx, zz, yy, hacia, largo) in ((M, 9.2, 1.0, -1.0, 3.0 if abs(x) > 2 else 2.2),
                                           (Mq, 13.4, 0.0, 1.0, 2.6 if abs(x) > 2 else 1.8)):
            base = pt(Mx, (x, yy, zz))
            eje = Mx[:3, :3] @ np.array((0.0, hacia, 0.0))
            for ll in (Mx[:3, :3] @ np.array((1.0, 0.0, 0.0)), Mx[:3, :3] @ np.array((0.0, 0.0, 1.0))):
                ll = _u(ll) * 0.7
                a, b = base - ll, base + ll
                punta = base + eje * largo
                hoja(out, (punta - ll * 0.07, punta + ll * 0.07, b, a), P['diente'], 1.4, largo, semilla=4)
    for lado in (-1, 1):                                                                            # los ojos, bajo el ceño
        bm.cubo(out, M @ vr.T(lado * 2.9, 4.4, 5.0) @ vr.Rz(lado * 0.28), -1.7, -0.7, 0.0, 3.4, 1.5, 0.5,
                P['ojo'], semilla=5)
    if tipo == 'fuego':                                                                              # la cresta de membrana
        for k, (x, alto, inc) in enumerate(((-3.4, 6.0, -0.5), (-1.2, 8.0, -0.2), (1.2, 8.0, 0.2), (3.4, 6.0, 0.5))):
            b = pt(M, (x, 7.4, -3.0))
            arriba = M[:3, :3] @ _u((inc, 1.0, -0.6))
            atras = M[:3, :3] @ np.array((0.0, 0.0, -1.0))
            hoja(out, (b, b + atras * 4.0, b + atras * 5.5 + arriba * alto, b + arriba * alto * 0.9), P['membrana'],
                 5.0, alto, semilla=6 + k)
    elif tipo == 'tormenta':                                                                        # los pararrayos
        for lado in (-1, 1):
            pts = [pt(M, (lado * 3.6, 7.0, -3.0))]
            for d in ((lado * 1.4, 3.0, -1.6), (lado * 0.8, 3.4, -1.0), (lado * 0.2, 3.2, -0.4), (0.0, 2.6, 0.0)):
                pts.append(pts[-1] + M[:3, :3] @ np.array(d))
            curva(out, pts, 1.4, P['hueso'], semilla=7)
            bm.cubo(out, vr.T(*pts[-1]), -0.8, 0.0, -0.8, 1.6, 1.6, 1.6, P['nucleo'], semilla=8)
    else:                                                                                            # la barba de musgo
        for k, x in enumerate((-4.0, -2.0, 0.0, 2.0, 4.0)):
            b = pt(Mq, (x, -3.0, 6.0 + (k % 2) * 4.0))
            largo = 5.0 + (k % 3) * 2.5
            hoja(out, (b + np.array((-0.8, -largo, 0.0)), b + np.array((0.8, -largo, 0.0)), b + np.array((0.8, 0, 0)),
                       b + np.array((-0.8, 0, 0))), P['musgo'], 1.6, largo, semilla=9 + k)


# ----------------------------------------------------------------------
#  El Izador
# ----------------------------------------------------------------------
BASE, ALTO, ANCHO, FONDO = 12.0, 34.0, 20.0, 18.0          # la jaula (pixeles): cabe un jugador de pie


def izador(tipo='A', abierta=0.0):
    """El Izador: (los quads, info). 'abierta' abre la jaula (para la foto de cuando suelta)."""
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    corto = V['corto']
    try:
        top = BASE + ALTO
        G = top + 18.0                                                                       # donde empieza el saco
        # el saco (o los sacos) y de donde salen las cuerdas
        if corto == 'fuego':
            globo(out, P, (0.0, G + 25.0, -2.0), 24.0, 26.0, 24.0, pisos=13, semilla=10)
            anclas = [(-9.0, G + 2.0, -11.0), (9.0, G + 2.0, -11.0), (-9.0, G + 2.0, 7.0), (9.0, G + 2.0, 7.0)]
            bm.cubo(out, vr.T(0.0, G - 2.0, -2.0), -3.0, 0.0, -3.0, 6.0, 3.0, 6.0, P['nucleo'], semilla=11)  # la boca de fuego
        elif corto == 'tormenta':
            for k, (c, r) in enumerate((((-12.0, G + 13.0, 0.0), 14.0), ((12.0, G + 13.0, -2.0), 14.0),
                                        ((0.0, G + 25.0, -6.0), 15.0), ((0.0, G + 9.0, 9.0), 10.0))):
                globo(out, P, c, r, r * 0.9, r, pisos=int(r * 0.9), semilla=10 + k)
            anclas = [(-12.0, G + 1.5, -2.0), (12.0, G + 1.5, -4.0), (-4.0, G + 2.0, -8.0), (4.0, G + 1.0, 8.0)]
        else:
            globo(out, P, (0.0, G + 13.0, -4.0), 15.0, 13.0, 38.0, pisos=24, semilla=10, eje='z')
            anclas = [(-9.0, G + 1.5, -16.0), (9.0, G + 1.5, -16.0), (-9.0, G + 1.0, 8.0), (9.0, G + 1.0, 8.0)]
            for k in range(9):                                                                   # las lianas del saco
                x = -12.0 + (k % 5) * 6.0
                z = -30.0 + k * 7.0
                largo = 8.0 + (k % 3) * 5.0
                b = np.array((x * 0.9, G + 2.0, z * 0.8))
                hoja(out, (b + np.array((-0.8, -largo, 0)), b + np.array((0.8, -largo, 0)), b + np.array((0.8, 0, 0)),
                           b + np.array((-0.8, 0, 0))), P['musgo'], 1.6, largo, semilla=20 + k)
        # las cuerdas de tendon, del saco a las esquinas de arriba de la jaula
        esquinas = [(-ANCHO / 2 + 1, top, -FONDO / 2 + 2), (ANCHO / 2 - 1, top, -FONDO / 2 + 2),
                    (-ANCHO / 2 + 1, top, FONDO / 2 - 3), (ANCHO / 2 - 1, top, FONDO / 2 - 3)]
        for a, b in zip(anclas, esquinas):
            a, b = np.array(a), np.array(b)
            m = (a + b) / 2 + np.array((0.0, -1.5, 0.0))
            curva(out, [a, m, b], 1.2, P['cuerda'], semilla=30)
        jaula(out, P, BASE, ALTO, ANCHO, FONDO, abierta=abierta, semilla=40)
        # el corazon, colgando dentro de la jaula
        curva(out, [np.array((0.0, top, -2.0)), np.array((0.0, top - 6.0, -2.0))], 0.8, P['cuerda'], semilla=41)
        bm.cubo(out, vr.T(0.0, top - 10.5, -2.0), -2.2, 0.0, -2.2, 4.4, 4.5, 4.4, P['nucleo'], semilla=42)
        # la cabeza, colgando delante de la jaula, mirando al frente y un poco abajo
        Mc = vr.T(0.0, top - 9.0, FONDO / 2 + 7.0) @ vr.Rx(0.3) @ np.diag([1.35, 1.35, 1.35, 1.0])
        curva(out, [np.array((0.0, top + 1.0, FONDO / 2 - 3.0)), np.array((0.0, top - 1.0, FONDO / 2 + 2.0)),
                    pt(Mc, (0.0, 3.5, -5.0))], 4.0, P['piel'], 50)                                   # el cuello
        cabeza(out, P, V, Mc)
        # los brazos, de los lados de arriba de la jaula, abiertos para agarrar
        for lado in (-1, 1):
            h = np.array((lado * (ANCHO / 2 + 1.5), top - 5.0, 1.0))
            c = h + np.array((lado * 9.0, -9.0, 7.0))
            m = c + np.array((-lado * 2.0, -12.0, 6.0))
            brazo(out, P, h, c, m, lado, semilla=60)
        # las raices que cuelgan debajo de la jaula
        for k, (x, z, largo) in enumerate(((-5.0, -4.0, 10.0), (4.0, -5.0, 13.0), (0.0, 4.0, 8.0), (-7.0, 3.0, 6.0),
                                          (7.0, 2.0, 9.0))):
            pts = [np.array((x, BASE, z))]
            for j in range(3):
                pts.append(pts[-1] + np.array((math.sin(k + j) * 1.2, -largo / 3, math.cos(k * 2 + j) * 1.0)))
            curva(out, pts, 1.0, P['cuerda'], semilla=70 + k)
    finally:
        bm.PPB = ppb
    k = V['escala'] / 16.0
    E = np.diag([k, k, k, 1.0])
    out = qm.transformar(out, E)
    cab = pt(E, pt(Mc, (0.0, 3.0, 8.0)))
    return out, {'cabeza': cab, 'nucleo': pt(E, (0.0, BASE + ALTO - 8.0, -2.0)), 'luz': V['luz'],
                 'jaula': pt(E, (0.0, BASE, 0.0)), 'escala': k,
                 'luces': [pt(E, (0.0, BASE + ALTO - 8.0, -2.0)), cab]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

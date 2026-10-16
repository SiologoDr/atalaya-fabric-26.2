"""
El Fogonazo (16-10-2026): el mob que, si se te acerca, estalla y te deja la pantalla en blanco. Juan: «hagamos un mob
que, si se te acerca a cierta distancia, explote y te aparezca la pantalla en blanco; primero hagamos el diseno». Al
ver la primera ficha: «cambia la cara por una mas tipo luciernaga; que estalle a 3 bloques; el blanco, 4 segundos; que
el estallido sea como la explosion de un creeper: te va a empujar, cegar y hacer dano».

Un bicho-luciernaga de la noche que lleva la luz dentro. Anda agazapado sobre cuatro patas, las de atras con las
rodillas altas; el pecho va acorazado de placas y detras, levantado sobre el lomo como el abdomen de una luciernaga,
lleva el farol: la luz sale por las juntas de sus bandas y por debajo de sus placas. La cabeza es de luciernaga: metida
bajo el escudo (el pronoto, con el borde de color y la mancha oscura), con dos ojos compuestos grandes, las mandibulas
en hoz, la boca pequena encendida por dentro y dos antenas en sierra larguisimas echadas hacia atras. Cuando te tiene
cerca se abre: levanta las placas, se le encienden los ojos y estalla.

    A  el Destello   pizarra oscura y luz blanca: el de siempre
    B  el Argos      palido como los bichos de las cuevas, con el farol hecho de ojos cerrados; luz blanca y fria
    C  el Racimo     pardo rojizo y luz de ambar, con un racimo de vainas de luz en lugar del farol

No se parece a un creeper (el Fulminante ya lo es), aunque estalle como uno: lo suyo es la luz.

Se modela como un mob, en pixeles de la piel (16 por bloque), con un texel por pixel.
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


def _h(*cs):
    return [nm._hex(c) for c in cs]


VARIANTES = {
    'A': dict(clave='FGA', nombre='el Destello', corto='destello',
              piel=_h('0e1014', '181c22', '242a32', '343e48', '4a5664'),
              luz=_h('7a5420', 'd8a046', 'ffd894', 'fff0cc', 'fffaf0'), luz_hex='ffeccc', marca=_h('6e2a20', 'c4563a')),
    'B': dict(clave='FGB', nombre='el Argos', corto='argos',
              piel=_h('4a4440', '6e665e', '948a7e', 'b6ad9e', 'd8d0c0'),
              luz=_h('1a4a7a', '3a9ad8', '8adcff', 'd6f2ff', 'f6fcff'), luz_hex='c4eeff', marca=_h('5e7280', '9fb4c2')),
    'C': dict(clave='FGC', nombre='el Racimo', corto='racimo',
              piel=_h('160a06', '26120c', '381c12', '4e2a1a', '683c24'),
              luz=_h('7a2a06', 'd8661a', 'ffae3a', 'ffdf8a', 'fff6d8'), luz_hex='ffcf72', marca=_h('8a3a14', 'd07a34')),
}
DIENTE = _h('7a7262', 'bcb29a', 'eee8d8')
UNA = _h('0c0a08', '1c1814', '322c24', '5a5040', '8a7e66')


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
#  Los pintores (cinco tonos por material, sin ruido)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    piel, luz = V['piel'], V['luz']

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'fg%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def p_piel(tw, th, cara_, s):
        """La piel: lisa, la fila de arriba un tono mas clara y la de abajo mas oscura, y una junta cada cuatro pixeles a
        lo largo (en las patas y las antenas se leen como los segmentos)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        if cara_ in ('arriba', 'abajo'):
            idx[...] = 3 if cara_ == 'arriba' else 1
            idx[(ys % 8) == 7] = 2 if cara_ == 'arriba' else 0
        else:
            idx[(xs % 8) == 7] = 1
            idx[0, :] = 3
            idx[th - 1, :] = 1
        return _pinta(idx, piel), None
    reg('piel', p_piel)

    def p_placa(tw, th, cara_, s):
        """Las placas del lomo, como un caparazon en bandas: el canto de atras claro (el bisel), estrias a lo ancho cada
        tres pixeles y, en el canto de delante, la raja por donde se escapa la luz."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        if cara_ == 'arriba':                              # la cara de fuera: las filas van de atras (0) a delante
            idx = np.full((th, tw), 2)
            idx[(xs % 3) == 1] = 1
            idx[0, :] = 4
            idx[1, :] = 3
            t = _pinta(idx, piel)
            raja = ys == th - 1
            t[raja] = (*luz[2], 255)
            return t, _emis(t, raja, 150)
        idx = np.full((th, tw), 1)
        idx[0, :] = 3
        return _pinta(idx, piel), None
    reg('placa', p_placa)

    def p_banda(tw, th, cara_, s):
        """Las bandas de la panza: oscuras, con el canto un tono mas claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 1)
        idx[(xs == 0) | (xs == tw - 1)] = 2
        return _pinta(idx, piel), None
    reg('banda', p_banda)

    def p_luz(tw, th, cara_, s):
        """La luz de dentro: escalones del borde (neon) al centro (casi blanco), sin degradado suave."""
        ys, xs = np.mgrid[0:th, 0:tw]
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        idx = np.clip(1 + d, 1, 4)
        return _pinta(idx, luz), None
    reg('luz', p_luz, pleno=True)

    def p_paladar(tw, th, cara_, s):
        """El paladar y la lengua: blanco al fondo de la garganta, luego el neon y la sombra hacia los dientes, con los
        pliegues del paladar cada tres filas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = ys / max(th - 1, 1)
        if cara_ == 'abajo':                               # en 'abajo' la fila 0 es la de delante
            f = 1 - f
        idx = np.where(f < 0.3, 4, np.where(f < 0.55, 3, np.where(f < 0.8, 2, 1)))
        idx[((ys % 3) == 2) & (idx > 1)] -= 1
        t = _pinta(idx, luz)
        return t, _emis(t, idx >= 2, 200)
    reg('paladar', p_paladar)

    def p_garganta(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        return _pinta(np.clip(3 + d, 3, 4), luz), None
    reg('garganta', p_garganta, pleno=True)

    def p_ojo(tw, th, cara_, s):
        """El ojo cerrado: el parpado de arriba abombado, con su canto claro, el de abajo mas oscuro y, entre los dos, la
        raja por la que se escapa la luz."""
        ys, xs = np.mgrid[0:th, 0:tw]
        if cara_ not in ('frente', 'arriba'):
            return _pinta(np.full((th, tw), 1), piel), None
        idx = np.where(ys < th // 2, 3, 2)
        idx[(ys == 0) | (ys == th - 1) | (xs == 0) | (xs == tw - 1)] = 0                 # la cuenca
        t = _pinta(idx, piel)
        raja = (ys == th // 2) & (xs > 0) & (xs < tw - 1)
        t[raja] = (*luz[3], 255)
        t[(ys == th // 2) & ((xs == 1) | (xs == tw - 2))] = (*luz[2], 255)
        return t, _emis(t, raja, 170)
    reg('ojo', p_ojo)

    def p_ojo_abierto(tw, th, cara_, s):
        """El ojo abierto al estallar: todo luz."""
        ys, xs = np.mgrid[0:th, 0:tw]
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        return _pinta(np.clip(2 + d, 2, 4), luz), None
    reg('ojo_abierto', p_ojo_abierto, pleno=True)

    def p_diente(tw, th, cara_, s):
        """El diente en aguja: la base arriba, la punta abajo, claro a un lado y oscuro al otro."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            w = tw * (th - y) / th
            a, b = (tw - w) / 2, (tw + w) / 2
            for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                t[y, x] = (*(DIENTE[2] if x < tw / 2 else DIENTE[1]), 255)
        return t, None
    reg('diente', p_diente)

    def p_una(tw, th, cara_, s):
        """Las unas y los garfios: cuerno oscuro, la punta mas clara."""
        ys, xs = np.mgrid[0:th, 0:tw]
        if cara_ in ('arriba', 'abajo'):
            idx = np.where(ys >= th - max(1, th // 3), 3, 1)
        else:
            idx = np.where(xs >= tw - max(1, tw // 3), 3, np.where(ys == 0, 2, 1))
        return _pinta(idx, UNA), None
    reg('una', p_una)

    def p_antena(tw, th, cara_, s):
        """La antena: segmentos oscuros con un anillo claro cada tres pixeles."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a = ys if cara_ in ('arriba', 'abajo') else xs
        idx = np.where((a % 3) == 0, 3, 1)
        return _pinta(idx, piel), None
    reg('antena', p_antena)

    def p_compuesto(tw, th, cara_, s):
        """El ojo compuesto de luciernaga: negro y liso como un cristal, con el canto de abajo encendido por la luz del
        farol (la mitad de arriba queda a oscuras bajo el escudo, como un ceño) y un brillo pequeno."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = _pinta(np.full((th, tw), 0), piel)
        canto = ((xs == 0) | (xs == tw - 1) | (ys == th - 1)) & (ys >= th // 2)
        t[canto] = (*luz[1], 255)
        brillo = (ys == 1) & (xs == 1) if min(tw, th) >= 4 else np.zeros_like(canto)
        t[brillo] = (*luz[4], 255)
        return t, _emis(t, canto | brillo, 150)
    reg('compuesto', p_compuesto)

    def p_compuesto_abierto(tw, th, cara_, s):
        """El ojo compuesto al estallar: todas las facetas encendidas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs % 2) == 0) | ((ys % 2) == 0), 2, 4)
        return _pinta(idx, luz), None
    reg('compuesto_abierto', p_compuesto_abierto, pleno=True)

    marca = V['marca']

    def p_escudo(tw, th, cara_, s):
        """El escudo de la cabeza (el pronoto de la luciernaga): por fuera, el borde de color, la placa y, en el centro,
        la mancha oscura; por los cantos, el borde de color."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = _pinta(np.full((th, tw), 2), piel)
        if cara_ == 'arriba':
            d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
            t[d == 1] = (*marca[0], 255)
            t[d == 0] = (*marca[1], 255)
            cx, cy = (tw - 1) / 2, th * 0.42
            mancha = ((xs - cx) / max(tw * 0.2, 1)) ** 2 + ((ys - cy) / max(th * 0.3, 1)) ** 2 <= 1
            t[mancha & (d >= 2)] = (*piel[0], 255)
        elif cara_ != 'abajo':
            t[...] = (*marca[0], 255)
            t[0, :] = (*marca[1], 255)
        else:
            t[...] = (*piel[0], 255)
        return t, None
    reg('escudo', p_escudo)

    def p_sierra(tw, th, cara_, s):
        """Un diente de la antena en sierra: un triangulo oscuro."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            w = tw * (th - y) / th
            for x in range(int(math.ceil(w))):
                t[y, min(tw - 1, x)] = (*piel[3 if x == 0 else 1], 255)
        return t, None
    reg('sierra', p_sierra)

    def p_cuerno(tw, th, cara_, s):
        """Las mandibulas: cuerno claro con la punta oscura y el filo de dentro mas claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys == 0, 4, 3)
        if cara_ not in ('arriba', 'abajo'):
            idx = np.where(xs >= tw - max(1, tw // 4), 1, np.where(ys == 0, 4, 3))
        return _pinta(idx, UNA), None
    reg('cuerno', p_cuerno)

    def p_hueco(tw, th, cara_, s):
        return _pinta(np.full((th, tw), 0), piel), None
    reg('hueco', p_hueco)

    def p_vaina(tw, th, cara_, s):
        """Una vaina de luz del Racimo: encendida, en gajos (las costuras oscuras a lo largo) y mas clara en el
        centro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        idx = np.clip(1 + d, 1, 3)
        idx[(xs % 3) == 2] = 1
        t = _pinta(idx, luz)
        t[(xs % 3) == 2] = (*piel[1], 255)
        return t, None
    reg('vaina', p_vaina, pleno=True)
    return P


# ----------------------------------------------------------------------
#  Las piezas
# ----------------------------------------------------------------------
def hoja(out, P4, pintor, ancho, alto, semilla=0):
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def hueso(out, a, b, grosor, pintor, semilla=0):
    bm.viga(out, a, b, grosor, grosor, pintor, extra=grosor * 0.3, semilla=semilla)


def ovalo(out, M, rx, ry, rz, pintor, semilla=0):
    """Un ovalo de pixel: tres cajas cruzadas (de medidas distintas, para que no haya dos caras en el mismo plano)."""
    for a, b, c in ((1.0, 0.7, 0.84), (0.7, 1.0, 0.9), (0.74, 0.74, 1.0)):
        bm.cubo(out, M, -rx * a, -ry * b, -rz * c, 2 * rx * a, 2 * ry * b, 2 * rz * c, pintor, semilla=semilla)


def garra(out, P, base, eje, lateral, largo, semilla=0):
    """Una una curva: tres tramos que se doblan hacia abajo."""
    eje, lateral = _u(eje), _u(lateral)
    abajo = _u(np.cross(eje, lateral))
    if abajo[1] > 0:
        abajo = -abajo
    pts = [np.asarray(base, float)]
    d = eje
    for k in range(3):
        pts.append(pts[-1] + d * largo / 3)
        d = _u(d + abajo * 0.6)
    for k, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        bm.viga(out, a, b, 0.9 - k * 0.15, 0.9 - k * 0.15, P['una'], extra=0.15, semilla=semilla)


def pata(out, P, raiz, rodilla, pie, gruesa, fina, semilla=0):
    """Una pata: el muslo (grueso, de dos tramos para que se afine), la canilla fina y tres unas que se clavan."""
    raiz, rodilla, pie = (np.asarray(p, float) for p in (raiz, rodilla, pie))
    medio = raiz + (rodilla - raiz) * 0.55
    hueso(out, raiz, medio, gruesa, P['piel'], semilla)
    hueso(out, medio, rodilla, gruesa * 0.72, P['piel'], semilla + 1)
    hueso(out, rodilla, pie + np.array((0.0, 0.8, 0.0)), fina, P['piel'], semilla + 2)
    delante = _u(np.array((pie[0] - raiz[0], 0.0, 0.0)) * 0.3 + np.array((0.0, 0.0, 1.0)))
    lat = _u(np.cross(np.array((0.0, 1.0, 0.0)), delante))
    for k, a in enumerate((-0.55, 0.0, 0.55)):
        d = _u(delante * math.cos(a) + lat * math.sin(a) + np.array((0.0, 0.25, 0.0)))
        garra(out, P, pie + np.array((0.0, 0.8, 0.0)), d, _u(np.cross(np.array((0.0, 1.0, 0.0)), d)), 2.6, semilla + 3)


def arco(t, ry=6.8, rz=9.0):
    """El arco del lomo (en el marco del cuerpo): el punto, la tangente (hacia delante) y la normal (hacia fuera)."""
    p = np.array((0.0, ry * math.cos(t), rz * math.sin(t)))
    tg = _u((0.0, -ry * math.sin(t), rz * math.cos(t)))
    n = _u((0.0, math.cos(t) / ry, math.sin(t) / rz))
    return p, tg, n


def marco_arco(Mt, t, ry=6.8, rz=9.0):
    p, tg, n = arco(t, ry, rz)
    M = np.eye(4)
    M[:3, 0] = np.cross(n, tg)
    M[:3, 1] = n
    M[:3, 2] = tg
    M[:3, 3] = p
    return Mt @ M


def placas(out, P, M, tetas, ry, rz, ancho, largo, abierto, faldon=3.0, ojos=False, semilla=0):
    """Placas en arco sobre un cuerpo (en el marco M, sobre su +y), cada una con sus dos faldones que caen por los
    costados; al estallar se levantan y se separan, y entre ellas sale la luz. En el Argos, cada placa lleva dos ojos
    cerrados."""
    for i, t in enumerate(tetas):
        Mi = marco_arco(M, t, ry, rz) @ vr.T(0.0, abierto * 2.2, 0.0) @ vr.Rx(-abierto * 0.35)
        bm.cubo(out, Mi, -ancho / 2, 0.0, -largo / 2, ancho, 1.8, largo, P['placa'], semilla=semilla + i)
        for lado in (-1, 1):
            Mf = Mi @ vr.T(lado * (ancho / 2 - 0.3), 1.2, 0.0) @ vr.Rz(lado * (0.32 + abierto * 0.7))
            bm.cubo(out, Mf, -0.7, -faldon, -largo / 2, 1.4, faldon + 0.4, largo, P['placa'], semilla=semilla + 10 + i)
        if ojos:
            for lado in (-1, 1):
                bm.cubo(out, Mi @ vr.T(lado * ancho * 0.24, 1.8, 0.1), -1.5, 0.0, -1.3, 3.0, 1.1, 2.6,
                        P['ojo_abierto'] if abierto > 0.5 else P['ojo'], semilla=semilla + 20 + i)


def ojos_farol(out, P, M, rx, ry, rz, abierto, semilla=0):
    """El farol del Argos: la piel palida tapada de ojos cerrados, y la luz solo sale por las rajas de los parpados;
    al estallar se abren todos."""
    ovalo(out, M, rx * 0.92, ry * 0.92, rz * 0.95, P['piel'], semilla=semilla)
    for z, angulos in ((-4.4, (-80, 0, 80)), (-1.5, (-125, -42, 42, 125)), (1.5, (-80, 0, 80)), (4.3, (-40, 40))):
        for a in angulos:
            f = math.radians(a)
            d = np.array((math.sin(f), -math.cos(f), 0.0))                             # alrededor del eje, 0 = delante
            c = np.array((d[0] * rx * 0.95, d[1] * ry * 0.95, z))
            Mo = M @ bm.em.marco(c, _u(d + np.array((0.0, 0.0, z / rz * 0.35))), up=(0.0, 0.0, 1.0))
            bm.cubo(out, Mo, -2.0, -1.5, -0.4, 4.0, 3.0, 1.0, P['ojo_abierto'] if abierto > 0.5 else P['ojo'],
                    semilla=semilla + 1)


def racimo(out, P, M, abierto, semilla=0):
    """El Racimo: en vez del farol, un racimo de vainas de luz apretadas (cada una con su caliz oscuro hacia dentro),
    sobre un corazon oscuro."""
    ovalo(out, M, 3.8, 3.6, 5.2, P['piel'], semilla=semilla)
    for k, (x, y, z, r) in enumerate(((0.0, 0.4, -5.6, 2.6), (3.3, 1.2, -2.8, 2.5), (-3.3, 1.0, -2.6, 2.4),
                                      (0.0, 4.0, -1.6, 2.6), (3.6, -1.6, 0.4, 2.3), (-3.5, -1.8, 0.6, 2.4),
                                      (0.2, -3.6, 0.2, 2.3), (2.8, 3.0, 2.2, 2.2), (-2.8, 3.0, 2.4, 2.2),
                                      (0.0, 0.6, 4.4, 2.2))):
        c = np.array((x, y, z)) * (1.0 + abierto * 0.25)
        fuera = _u(c)
        Mv = M @ vr.T(*c) @ bm.em.marco(np.zeros(3), fuera)
        ovalo(out, Mv, r * 0.9, r * 0.9, r, P['vaina'], semilla=semilla + k)
        bm.cubo(out, Mv, -r * 0.55, -r * 0.55, -r - 1.0, r * 1.1, r * 1.1, 1.6, P['placa'], semilla=semilla + 10 + k)


def cabeza(out, P, V, M, abre=0.4, ojos=0.0):
    """La cabeza de luciernaga (Juan: «cambia la cara por una mas tipo luciernaga»): pequena y metida bajo el escudo,
    una placa ancha y redondeada que la tapa desde arriba, con el borde de color y la mancha oscura en el centro, como
    el pronoto de las luciernagas; a los lados, dos ojos compuestos grandes, de facetas; delante, dos mandibulas en hoz
    que se cruzan, y entre ellas la boca pequena, encendida por dentro, con dientes en aguja; y los palpos cortos.
    Al estallar, los ojos se encienden enteros, el escudo se levanta y las mandibulas se abren. Mira a +z."""
    ojo = P['compuesto_abierto'] if ojos > 0.5 else P['compuesto']
    bm.cubo(out, M, -3.2, 0.4, -2.8, 6.4, 4.6, 6.6, P['piel'], semilla=1)                       # la capsula
    bm.cubo(out, M, -2.4, 0.8, 3.6, 4.8, 3.0, 1.4, P['piel'], semilla=2)                        # la frente
    for lado in (-1, 1):                                                                         # los ojos compuestos
        ovalo(out, M @ vr.T(lado * 3.2, 3.0, 2.0), 2.3, 2.5, 2.5, ojo, semilla=3)
    Me = M @ vr.T(0.0, 5.0, -1.6) @ vr.Rx(0.22 - ojos * 0.35)                                   # el escudo
    bm.cubo(out, Me, -6.2, 0.0, -5.6, 12.4, 1.4, 9.6, P['escudo'], semilla=4)
    bm.cubo(out, Me, -3.8, 1.3, -4.6, 7.6, 1.0, 7.4, P['escudo'], semilla=5)                    # el abombado
    bm.cubo(out, Me, -5.4, -0.1, 4.0, 10.8, 1.3, 1.4, P['escudo'], semilla=6)                   # lo redondo
    bm.cubo(out, Me, -4.2, -0.2, 5.4, 8.4, 1.2, 1.2, P['escudo'], semilla=6)
    bm.cubo(out, Me, -2.6, -0.3, 6.6, 5.2, 1.1, 0.9, P['escudo'], semilla=6)
    for lado in (-1, 1):                                                                         # sus faldones
        bm.cubo(out, Me @ vr.T(lado * 6.0, 0.6, -0.8) @ vr.Rz(lado * 0.55), -0.6, -2.6, -4.6, 1.2, 3.0, 8.4,
                P['escudo'], semilla=7)
    # la boca: pequena, encendida por dentro, con su labio de abajo y los dientes en aguja alrededor
    bm.cubo(out, M, -2.0, -0.8, 2.4, 4.0, 1.6, 2.6, P['piel'], caras={'frente': P['garganta']}, semilla=8)
    Mq = M @ vr.T(0.0, -0.8, 2.2) @ vr.Rx(abre * 0.6)
    bm.cubo(out, Mq, -2.2, -1.2, 0.0, 4.4, 1.2, 3.4, P['piel'], caras={'arriba': P['paladar']}, semilla=9)

    def diente(base, hacia, largo, ancho, eje):
        ll = eje * ancho / 2
        punta = base + hacia * largo
        hoja(out, (punta - ll * 0.12, punta + ll * 0.12, base + ll, base - ll), P['diente'], 1, 3, semilla=10)

    for x in (-1.5, -0.5, 0.5, 1.5):                                                             # los de arriba
        diente(pt(M, (x, 0.8, 5.1)), -M[:3, 1], 1.6 if abs(x) < 1 else 2.0, 0.8, M[:3, 0])
    for x in (-1.0, 0.0, 1.0):                                                                   # los de abajo
        diente(pt(Mq, (x, 0.0, 3.3)), Mq[:3, 1], 1.4, 0.8, Mq[:3, 0])
    for lado in (-1, 1):                                                                         # las mandibulas en hoz
        p = pt(M, (lado * 2.4, 0.4, 4.4))
        d = M[:3, :3] @ _u((lado * (0.45 + ojos * 0.9), -0.35, 1.0))
        for k in range(3):
            q = p + d * 1.7
            g = 1.1 - 0.25 * k
            bm.viga(out, p, q, g, g, P['cuerno'], extra=0.15, semilla=11)
            p = q
            d = _u(d + M[:3, :3] @ np.array((-lado * (0.42 + 0.12 * k), 0.08, -0.12)))
        q = pt(M, (lado * 1.5, -0.4, 4.6))                                                       # los palpos
        r = q + M[:3, :3] @ np.array((lado * 0.5, -1.4, 0.9))
        bm.viga(out, q, r, 0.6, 0.6, P['piel'], extra=0.1, semilla=12)
        bm.viga(out, r, r + M[:3, :3] @ np.array((lado * 0.2, -1.0, 0.9)), 0.5, 0.5, P['piel'], extra=0.1, semilla=12)


def antena(out, P, M, lado, abierto, segmentos=11, semilla=0):
    """Una antena de luciernaga, en sierra: sale de la frente, por debajo del escudo, sube por delante de el y se echa
    hacia atras sobre el lomo, afinandose; cada segmento lleva un diente hacia fuera. Al estallar se levanta."""
    p = pt(M, (lado * 1.0, 3.8, 4.8))
    d = M[:3, :3] @ _u((lado * 0.45, 0.7 + abierto * 0.3, 0.55))
    fuera = M[:3, 0] * lado
    for k in range(segmentos):
        q = p + d * (2.4 if k < 2 else 3.0)
        g = 0.95 - 0.45 * k / segmentos
        bm.viga(out, p, q, g, g, P['antena'], extra=0.1, semilla=semilla)
        if 1 <= k < segmentos - 2:                                                          # el diente de la sierra
            b = p + (q - p) * 0.2
            c = p + (q - p) * 0.75
            n = _u(fuera - d * float(fuera @ d))
            t = b + (q - p) * 0.15 + n * (1.1 - 0.5 * k / segmentos)
            hoja(out, (t, t, c, b), P['sierra'], 1, 2, semilla=semilla)
        p = q
        d = _u(d + M[:3, :3] @ np.array((-lado * 0.03, -0.05 - 0.012 * k + abierto * 0.05, -0.34)))
    return p


# ----------------------------------------------------------------------
#  Las posturas
# ----------------------------------------------------------------------
# alza: cuanto levanta la parte de delante; cab: cabeceo de la cabeza (negativo, arriba); abre: la quijada; ojos y
# abierto: 0 cerrado, 1 al estallar; luz: lo que se hincha el farol; y los codos, las rodillas y los pies (en el marco del
# modelo).
POSTURAS = {
    'acecho': dict(alza=0.05, cab=0.18, abre=0.42, ojos=0.0, abierto=0.0, luz=1.0,
                   codo=(7.0, 7.0, 8.5), pie_d=(6.5, 0.0, 12.5), rodilla=(8.5, 15.5, -3.0), pie_t=(8.5, 0.0, -1.0)),
    'estalla': dict(alza=-0.25, cab=-0.3, abre=0.95, ojos=1.0, abierto=1.0, luz=1.35,
                    codo=(7.0, 10.5, 9.5), pie_d=(6.5, 0.0, 12.0), rodilla=(9.0, 15.5, -3.5), pie_t=(9.0, 0.0, -1.5)),
}


def fogonazo(tipo='A', postura='acecho', escala=1.0 / 16):
    """El Fogonazo en una postura: (los quads, info)."""
    V = VARIANTES[tipo]
    P = pintores(V)
    Q = POSTURAS[postura] if isinstance(postura, str) else postura
    corto = V['corto']
    argos = corto == 'argos'
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        Mt = vr.T(0.0, 9.0, 3.0) @ vr.Rx(Q['alza'])                                     # el pecho
        ovalo(out, Mt, 4.6, 3.6, 5.0, P['piel'], semilla=1)
        placas(out, P, Mt, (-0.75, -0.05, 0.65), 4.4, 5.6, 11.0, 4.6, Q['abierto'] * 0.25, 2.6, semilla=2)
        # el farol: detras, levantado sobre el lomo (como el abdomen de una luciernaga)
        Ma = (Mt @ vr.T(0.0, 1.8, -4.2) @ vr.Rx(1.1 + 0.15 * Q['abierto']) @ vr.T(0.0, 0.0, -6.4)
              @ vr.Rz(math.pi))                                                         # las placas, detras
        k = Q['luz']
        rx, ry, rz = 5.6 * k ** 0.4, 5.4 * k ** 0.4, 7.0
        if corto == 'racimo':
            racimo(out, P, Ma, Q['abierto'], semilla=30)
        elif argos:
            ojos_farol(out, P, Ma, rx, ry, rz, Q['abierto'], semilla=60)
            placas(out, P, Ma, (-0.95, -0.32, 0.3, 0.9), ry + 0.8, rz + 0.8, 2 * rx + 2.4, 4.9, Q['abierto'], 3.0,
                   semilla=10)
        else:
            ovalo(out, Ma, rx, ry, rz, P['luz'], semilla=3)
            for i, z in enumerate((-3.6, 0.0, 3.6)):                                    # las bandas
                for a, b in ((1.0, 0.72), (0.74, 1.0)):
                    bm.cubo(out, Ma, -(rx + 0.5) * a, -(ry + 0.5) * b, z - 0.7, 2 * (rx + 0.5) * a,
                            2 * (ry + 0.5) * b, 1.4, P['banda'], semilla=4 + i)
            placas(out, P, Ma, (-0.95, -0.32, 0.3, 0.9), ry + 0.8, rz + 0.8, 2 * rx + 2.4, 4.9, Q['abierto'], 3.0,
                   semilla=10)
        Mc = Ma @ vr.T(0.0, 0.0, -rz + 0.5)                                             # la punta
        bm.cubo(out, Mc, -2.2, -2.2, -2.6, 4.4, 4.4, 2.6, P['piel'], semilla=6)
        bm.cubo(out, Mc, -1.2, -1.2, -4.4, 2.4, 2.4, 2.0, P['piel'], semilla=7)
        hueso(out, pt(Mt, (0.0, 1.0, -3.6)), pt(Ma, (0.0, -0.5, rz - 1.0)), 3.6, P['piel'], semilla=8)   # el talle
        Mh = Mt @ vr.T(0.0, -1.8, 5.4) @ vr.Rx(-Q['alza'] + Q['cab'])                    # la cabeza
        cabeza(out, P, V, Mh, Q['abre'], Q['ojos'])
        puntas = [antena(out, P, Mh, lado, Q['abierto'], 9 if argos else 11, semilla=40) for lado in (-1, 1)]
        for lado in (-1, 1):                                                           # las patas
            s = np.array((lado, 1.0, 1.0))
            pata(out, P, pt(Mt, (lado * 3.8, -2.0, 2.6)), np.array(Q['codo']) * s, np.array(Q['pie_d']) * s, 2.2, 1.4,
                 semilla=50)
            pata(out, P, pt(Mt, (lado * 4.0, -1.4, -2.6)), np.array(Q['rodilla']) * s, np.array(Q['pie_t']) * s, 3.2,
                 1.5, semilla=56)
    finally:
        bm.PPB = ppb
    E = np.diag([escala, escala, escala, 1.0])
    out = qm.transformar(out, E)
    return out, {'nucleo': pt(E, pt(Ma, (0.0, 0.0, 0.0))), 'cabeza': pt(E, pt(Mh, (0.0, 3.0, 5.0))),
                 'boca': pt(E, pt(Mh, (0.0, 0.0, 6.0))), 'luz': V['luz_hex'], 'puntas': [pt(E, p) for p in puntas]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

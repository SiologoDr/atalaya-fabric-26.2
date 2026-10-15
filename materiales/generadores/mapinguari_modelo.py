"""
El Mapinguari y sus tipos (15-10-2026). Juan, tras Bravara: «no es lo que busco yo personalmente»; y luego «tu eliges».
Mirando los jefes del mod (Nerea, Aeralis, Rajang, Novilis), lo que tienen en comun es que son seres malditos, con el
punto debil en el pecho («Rompe sus cadenas. Libera su corazon»; «Arranca la raiz de su pecho»). El Mapinguari encaja en
eso: en la Amazonia es un chaman maldito, convertido en una bestia gigante que guarda la selva; anda erguido, apesta,
tiene garras enormes, los pies vueltos hacia atras y una boca en el vientre.

Lo nuestro: la boca del vientre son sus costillas, que se abren en el pecho como unas fauces de hueso y dejan ver el
corazon encendido (lo que hay que arrancarle para liberarlo). La cabeza va baja y adelantada, con el morro corto, los
ojos hundidos que brillan bajo una ceja de hueso y dos colmillos de abajo. El cuerpo, en pera y peludo, con mechones que
cuelgan de los hombros y de los brazos; los brazos, larguisimos, con tres garras de perezoso gigante en cada mano; los
pies, al reves.

Los tres tipos tienen la misma pose y cambian el pelo, la cabeza, lo que lleva encima y el color:

    A  el Guardian       pelo rojizo con musgo en los hombros; luz verde
    B  el Chaman Maldito pelo negro con pinturas blancas en zigzag, un solo ojo y un tocado de huesos; luz roja
    C  el Viejo del Rio  pelo gris plata, con lianas y helechos que le crecen encima y cuernos de raiz; luz ambar
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _manchas, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.62
CABEZA = 1.6

VARIANTES = {
    'A': dict(
        clave='MA', nombre='el Guardian', corto='guardian', cabeza='dos_ojos', encima='musgo',
        pelo=_r('220806', '420e0a', '661810', '8c2418', 'b03a26'),
        cara=_r('1e1412', '30221e', '44322c', '5a443c', '725a50'),
        neon=('eaffd8', '5aff3a', '0e5a04'),
        pinta=None,
    ),
    'B': dict(
        clave='MB', nombre='el Chaman Maldito', corto='chaman', cabeza='un_ojo', encima='huesos',
        pelo=_r('08080a', '121216', '1c1c22', '28282e', '36363e'),
        cara=_r('0c0606', '180c0c', '261414', '361e1e', '4a2a2a'),
        neon=('ffe6e0', 'ff3a2a', '6a0a04'),
        pinta=_r('a89c90', 'cac0b4', 'e6ded2', 'f4eee6', 'fffaf4'),
    ),
    'C': dict(
        clave='MC', nombre='el Viejo del Rio', corto='viejo', cabeza='raices', encima='lianas',
        pelo=_r('3a3e44', '585e66', '7a8088', '9ca2aa', 'c2c8ce'),
        cara=_r('121416', '1e2124', '2c3034', '3c4146', '50565c'),
        neon=('fff4d0', 'ffb21a', '6a4004'),
        pinta=None,
    ),
}


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


# ----------------------------------------------------------------------
#  Los pintores, todos propios
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    neo = [nm._hex(c) for c in V['neon']]
    MUSGO = _r('122410', '1c3818', '2a5222', '3c6e2c', '548c3a')
    HUESO = _r('6a5e4c', '988a72', 'c4b698', 'e0d4b8', 'f4ecd8')
    GARRA = _r('0c0a08', '1a1612', '2a241e', '3e362c', '564c40')
    LIANA = _r('0e1a0a', '182a10', '243e18', '345622', '48722e')

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'map%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def pelo(tw, th, cara, s):
        """El pelaje: hebras largas a lo largo, en franjas oscuras y claras, con brillos sueltos; en el Chaman, las
        pinturas blancas en zigzag por encima."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo, de_traves = (ys, xs) if cara in ('arriba', 'abajo') else (xs, ys)
        corrida = (a_lo_largo // 6 + de_traves * 7) % 3
        idx = np.where((de_traves + corrida) % 3 == 0, 1, 2)
        idx = np.where(((de_traves * 5 + a_lo_largo // 3) % 13 == 0), 3, idx)
        if cara == 'arriba':
            idx = np.clip(idx + 1, 0, 4)
        img = _imagen(_bisel(idx, 1, 1), V['pelo'])
        if V['pinta'] is not None:
            zig = (abs(((xs % 8) - 4)) == (ys % 10) // 2) & ((ys // 10) % 2 == 0)
            img = np.where(zig[..., None], _imagen(np.full((th, tw), 3), V['pinta']), img)
        return img, None
    reg('pelo', pelo)

    def mechon(tw, th, cara, s):
        """Un mechon que cuelga: en punta hacia abajo, con sus hebras."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t_ = ys / max(th - 1, 1)
        dentro = abs(xs - (tw - 1) / 2) <= (tw / 2) * (1.0 - 0.85 * t_) + 0.3
        idx = np.where(xs % 2 == 0, 2, 1)
        idx = np.where(xs % 5 == 0, 3, idx)
        img = _imagen(idx, V['pelo'])
        img[..., 3] = np.where(dentro, 255, 0)
        return img, None
    reg('mechon', mechon)

    def cara(tw, th, cara_, s):
        """La cara: piel oscura y curtida, casi sin pelo, con arrugas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys % 4 == 0, 1, 2)
        return _imagen(_bisel(idx, 1, 1), V['cara']), None
    reg('cara', cara)

    def ojo(tw, th, cara_, s):
        """El ojo hundido: negro, con un iris que brilla y la pupila rasgada."""
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        d = np.hypot((xs - cx) / max(cx, 1), (ys - cy) / max(cy, 1))
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (10, 6, 6, 255)
        iris = d < 0.8
        t[iris] = (*neo[1], 255)
        t[d < 0.4] = (*neo[0], 255)
        pupila = (abs(xs - cx) < max(0.6, tw * 0.1)) & (abs(ys - cy) < th * 0.36)
        t[pupila] = (10, 6, 6, 255)
        return t, _emis(t, iris & ~pupila, 255)
    reg('ojo', ojo)

    def hueso(tw, th, cara_, s):
        """El hueso de las costillas y de la ceja: liso, con su canto, y una veta de la luz del corazon en la cara de dentro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo = ys if cara_ in ('arriba', 'abajo') else xs
        idx = np.where(a_lo_largo % 6 == 0, 2, 3)
        return _imagen(_bisel(idx, 1, 1), HUESO), None
    reg('hueso', hueso)

    def craneo(tw, th, cara_, s):
        """La cara de hueso por delante: las cuencas hondas y oscuras y, dentro, los ojos que brillan (o el ojo solo del
        Chaman, grande, en medio); unas grietas finas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        idx = np.where((xs * 3 + ys * 5) % 23 == 0, 2, idx)
        img = _imagen(_bisel(idx, 1, 1), HUESO)
        centros = [(0.5, 0.42, 0.28, 0.26)] if V['cabeza'] == 'un_ojo' else [(0.26, 0.42, 0.2, 0.21), (0.74, 0.42, 0.2, 0.21)]
        brilla = np.zeros((th, tw), bool)
        for cx, cy, rx, ry in centros:
            d = np.hypot((xs + 0.5 - cx * tw) / (rx * tw), (ys + 0.5 - cy * th) / (ry * th))
            haz = 1 if cx < 0.5 else -1 if cx > 0.5 else 0                  # hacia donde baja el ceno
            if haz == 0:                                                      # el ojo solo: el ceno en V, que baja al medio
                ceno = (ys + 0.5 - cy * th) < -ry * th * 0.6 + abs(xs + 0.5 - cx * tw) * 0.55
            else:
                ceno = (ys + 0.5 - cy * th) < -ry * th * 0.15 + haz * (xs + 0.5 - cx * tw) * 0.55
            d = np.where(ceno, 9.0, d)
            img[d < 1.0] = (16, 8, 8, 255)
            dd = np.hypot((xs + 0.5 - cx * tw) / (rx * tw * 0.5), (ys + 0.5 - (cy + ry * 0.2) * th) / (ry * th * 0.5))
            iris = (dd < 1.0) & (d < 1.0)
            img[iris] = (*neo[1], 255)
            img[(dd < 0.5) & (d < 1.0)] = (*neo[0], 255)
            brilla |= iris
        return img, _emis(img, brilla, 255)
    reg('craneo', craneo)

    def morro(tw, th, cara_, s):
        """El morro de hueso por delante: el hueco de la nariz, oscuro y en punta hacia arriba."""
        ys, xs = np.mgrid[0:th, 0:tw]
        img = _imagen(_bisel(np.full((th, tw), 3), 1, 1), HUESO)
        cx = (tw - 1) / 2
        hueco = (ys > th * 0.1) & (ys < th * 0.55) & (abs(xs - cx) < (ys - th * 0.1) * 0.8 + 0.6)
        img[hueco] = (16, 8, 8, 255)
        return img, None
    reg('morro', morro)

    def dientes(tw, th, cara_, s):
        """Los dientes de la calavera: de bloque, apretados, en punta."""
        t = np.zeros((th, tw, 4), np.uint8)
        paso = 3
        for x0 in range(0, tw - 1, paso):
            for y in range(th):
                w = paso * (1 - 0.6 * y / max(th, 1))
                for x in range(x0, min(tw, x0 + int(round(w)))):
                    c = HUESO[4] if x == x0 else HUESO[2]
                    t[y, x] = (*c, 255)
        return t, None
    reg('dientes', dientes)

    def garra(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs < tw / 2, 3, 2)
        return _imagen(_bisel(idx, 1, 1), GARRA), None
    reg('garra', garra)

    def corazon(tw, th, cara_, s):
        """El corazon: rojo oscuro con venas de luz que salen del centro, y el centro blanco."""
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        d = np.hypot((xs - cx) / max(cx, 1), (ys - cy) / max(cy, 1))
        ang = np.arctan2(ys - cy, xs - cx)
        vena = (abs(((ang * 3 / math.pi) % 1) - 0.5) < 0.12) | (d < 0.4)
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[2], 255)
        t[vena] = (*neo[1], 255)
        t[d < 0.25] = (*neo[0], 255)
        return t, None
    reg('corazon', corazon, pleno=True)

    def hueco(tw, th, cara_, s):
        """El hueco del pecho: carne oscura que se enciende hacia el corazon."""
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        d = np.hypot((xs - cx) / max(cx, 1), (ys - cy) / max(cy, 1))
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (24, 8, 8, 255)
        t[d < 0.75] = (*neo[2], 255)
        t[(d < 0.75) & ((xs + ys) % 4 == 0)] = (*neo[1], 255)
        return t, _emis(t, d < 0.75, 200)
    reg('hueco', hueco)

    def musgo(tw, th, cara_, s):
        idx = _manchas(tw, th, s, celda=4.0, umbral=0.5, alto=0.8)
        return _imagen(_bisel(np.array([1, 2, 3, 3, 4])[idx], 1, 1), MUSGO), None
    reg('musgo', musgo)

    def liana(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo = ys if cara_ in ('arriba', 'abajo') else xs
        idx = np.where(a_lo_largo % 4 == 0, 1, 2)
        return _imagen(idx, LIANA), None
    reg('liana', liana)

    def hoja(tw, th, cara_, s):
        """La hoja de helecho: un nervio en el medio y foliolos a los lados, recortada en punta."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t_ = ys / max(th - 1, 1)
        dentro = abs(xs - (tw - 1) / 2) <= (tw / 2) * (0.25 + 0.65 * np.sin(math.pi * (1 - t_))) + 0.2
        idx = np.where(abs(xs - (tw - 1) / 2) < 0.6, 1, np.where((ys + abs(xs - tw // 2)) % 3 == 0, 2, 3))
        img = _imagen(idx, MUSGO)
        img[..., 3] = np.where(dentro, 255, 0)
        return img, None
    reg('hoja', hoja)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def tubo_caras(out, pts, radios, pintor, caras=None, achata=1.0, semilla=0, arriba=(0.0, 1.0, 0.0)):
    """Un tubo de bloques: dos cajas cruzadas por tramo (seccion de ocho lados)."""
    for j in range(len(pts) - 1):
        p0, p1 = np.asarray(pts[j], float), np.asarray(pts[j + 1], float)
        d = p1 - p0
        L = float(np.linalg.norm(d))
        if L < 1e-4:
            continue
        up = arriba if abs(_u(d) @ _u(arriba)) < 0.95 else (0.0, 0.0, 1.0)
        M = em.marco(p0, d, up=up)
        r = (radios[j] + radios[j + 1]) / 2
        for kx, ky in ((1.0, 0.74), (0.74, 1.0)):
            bm.cubo(out, M, -r * kx, -r * ky * achata, -r * 0.3, 2 * r * kx, 2 * r * ky * achata, L + r * 0.6, pintor,
                    caras=caras, semilla=semilla + j % 3)


def mechones(out, P, base, abajo, lado, n, largo, ancho, semilla=0, abre=0.35):
    """Unos mechones que cuelgan en fila desde 'base' a lo largo de 'lado', hacia 'abajo', un poco abiertos."""
    rng = random.Random(semilla)
    base, abajo, lado = np.asarray(base, float), _u(abajo), np.asarray(lado, float)
    for i in range(n):
        t = (i / max(n - 1, 1)) - 0.5
        b = base + lado * t
        L = largo * rng.uniform(0.75, 1.15)
        d = _u(abajo + _u(lado) * t * abre)
        l = _u(lado) * ancho / 2
        lamina(out, (b - l + d * L, b + l + d * L, b + l, b - l), P['mechon'], ancho, L, semilla=semilla + i % 4)


def garras(out, P, muneca, adelante, s, semilla=0):
    """La mano: una pala ancha y tres garras de perezoso gigante, largas y curvas hacia abajo."""
    muneca, f = np.asarray(muneca, float), _u(adelante)
    e = _u(np.cross((0.0, 1.0, 0.0), f))
    caja(out, vr.T(*muneca), -2.4, 2.4, -2.0, 2.0, -2.4, 2.4, P['pelo'], semilla=semilla)
    for k, g in enumerate((-1, 0, 1)):
        a = muneca + e * g * 1.5 + f * 1.4
        b = a + f * 2.6 + np.array((0.0, -1.2, 0.0))
        c = b + f * 2.4 + np.array((0.0, -3.4, 0.0))
        d = c + f * 0.4 + np.array((0.0, -2.6, 0.0)) - f * 1.4
        tubo_caras(out, [a, b, c, d], [0.95, 0.8, 0.5, 0.08], P['garra'], semilla=semilla + 1)


def cabeza(out, Mh, P, V, semilla=0):
    """La cabeza, mirando a +z: la cara es de hueso, como el craneo de una bestia (la del chaman muerto), con las cuencas
    hondas donde brillan los ojos (o el ojo solo del Chaman), el hueco de la nariz y los dientes a la vista; la quijada,
    un poco abierta, con dos colmillos que suben; y alrededor, la melena roja que la enmarca."""
    pe, hu = P['pelo'], P['hueso']
    bm.cubo(out, Mh, -4.6, 0.0, -5.6, 9.2, 7.0, 5.4, pe, semilla=semilla)                                   # la mata de pelo, atras
    bm.cubo(out, Mh, -3.8, -2.6, -5.0, 7.6, 9.4, 4.8, pe, semilla=semilla + 1)
    bm.cubo(out, Mh, -3.2, -2.4, -0.6, 6.4, 6.0, 3.6, hu, caras={'frente': P['craneo']}, semilla=semilla + 2)  # el craneo
    bm.cubo(out, Mh, -3.5, 2.6, -0.4, 7.0, 1.2, 3.8, hu, semilla=semilla + 2)                               # la ceja
    bm.cubo(out, Mh, -2.2, -2.6, 3.0, 4.4, 2.6, 2.2, hu, caras={'frente': P['morro']}, semilla=semilla + 3)    # el morro, corto y bajo
    bm.cubo(out, Mh, -1.7, -2.4, 5.0, 3.4, 2.0, 1.0, hu, caras={'frente': P['morro']}, semilla=semilla + 3)
    hilera_dientes(out, Mh, [(-1.6, 6.0), (1.6, 6.0)], -2.4, -1.0, P['dientes'], semilla=semilla + 4)
    for s in (1, -1):
        hilera_dientes(out, Mh, [(s * 2.1, 3.2), (s * 1.7, 5.8)], -2.6, -1.0, P['dientes'], semilla=semilla + 4)
    Mj = Mh @ vr.T(0.0, -2.6, 0.6) @ vr.Rx(18 * D)                                       # la quijada, entreabierta
    bm.cubo(out, Mj, -2.4, -1.8, 0.0, 4.8, 1.8, 6.0, hu, caras={'arriba': P['hueco']}, semilla=semilla + 5)
    hilera_dientes(out, Mj, [(-1.9, 1.0), (-1.9, 5.8), (1.9, 5.8), (1.9, 1.0)], 0.0, 1.0, P['dientes'], semilla=semilla + 6,
                   sube=True)
    for s in (1, -1):                                                                     # los colmillos que suben
        caja(out, Mj @ vr.T(s * 1.5, 0.0, 5.0) @ vr.Rz(-s * 10 * D), -0.45, 0.45, 0.0, 3.0, -0.45, 0.45, hu,
             semilla=semilla + 7)
    # la melena: mechones que caen de arriba y de los lados, alrededor de la cara
    rng = random.Random(semilla)
    for i, a in enumerate(np.linspace(-1.75, 1.75, 13)):
        b = pt(Mh, (math.sin(a) * 4.8, 3.4 + math.cos(a) * 3.4, -0.4 - abs(math.sin(a)) * 1.0))
        d = Mh[:3, :3] @ _u(np.array((math.sin(a) * 0.7, -1.0, 0.25)))
        l = Mh[:3, :3] @ _u(np.array((math.cos(a), -math.sin(a) * 0.3, 0.0))) * 1.3
        L = rng.uniform(6.0, 9.5) if abs(a) > 0.6 else rng.uniform(2.6, 3.6)
        lamina(out, (b - l + d * L, b + l + d * L, b + l, b - l), P['mechon'], 2.6, L, semilla=semilla + 9 + i % 3)
    if V['cabeza'] == 'raices':                                                           # los cuernos de raiz
        for s in (1, -1):
            a = pt(Mh, (s * 3.0, 5.6, -1.6))
            ps = [a, a + np.array((s * 3.6, 5.0, -1.8)), a + np.array((s * 4.6, 10.0, -3.0)), a + np.array((s * 3.0, 14.0, -5.0))]
            tubo_caras(out, ps, [1.2, 0.95, 0.65, 0.12], P['liana'], semilla=semilla + 12)
            for t, (dx, dy) in ((1, (3.4, 1.6)), (2, (3.0, 2.6)), (2, (-1.6, 3.4))):
                tubo_caras(out, [ps[t], ps[t] + np.array((s * dx, dy, 0.4))], [0.55, 0.1], P['liana'], semilla=semilla + 13)
    if V['cabeza'] == 'un_ojo':                                                           # el tocado de huesos
        for i, g in enumerate(np.linspace(-70.0, 70.0, 7)):
            a = g * D
            b = pt(Mh, (math.sin(a) * 3.4, 6.0, -1.6 - abs(math.sin(a)) * 1.0))
            d = Mh[:3, :3] @ _u(np.array((math.sin(a) * 0.8, 1.0, -0.4)))
            L = 8.5 - abs(g) / 70.0 * 3.0
            tubo_caras(out, [b, b + d * L], [0.4, 0.25], hu, semilla=semilla + 14)
            caja(out, vr.T(*(b + d * L)), -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, hu, semilla=semilla + 15)


def hilera_dientes(out, M, puntos, y, alto, pintor, semilla=0, sube=False):
    """Una fila de dientes por los puntos (x, z) a la altura y, que baja o, con 'sube', sube."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado = float(np.linalg.norm(B - A))
        if sube:
            lamina(out, (A, B, B2, A2), pintor, lado, abs(alto), semilla + j)
        else:
            lamina(out, (A2, B2, B, A), pintor, lado, abs(alto), semilla + j)


def pecho(out, P, V, semilla=0):
    """Las fauces del pecho: el pelo se abre, dentro arde el hueco y el corazon, y las costillas salen de los dos lados,
    se abren hacia fuera y se cierran delante en punta, curvas, como dientes de hueso. Devuelve el corazon."""
    c = np.array((0.0, 25.0, 8.8))
    bm.cubo(out, vr.T(*c), -4.0, -6.4, -1.2, 8.0, 12.8, 0.8, P['hueco'], semilla=semilla)                 # el hueco
    for w, h, d in ((2.0, 2.4, 1.2), (1.5, 2.9, 1.0), (2.4, 1.8, 1.0)):                    # el corazon
        caja(out, vr.T(*(c + np.array((0.0, 0.6, 0.6)))), -w, w, -h, h, -d * 0.6, d, P['corazon'], semilla=semilla + 1)
    for s in (1, -1):
        for j, y in enumerate(np.linspace(5.2, -5.2, 6)):
            k = 1.0 - abs(y) / 9.0
            r0 = c + np.array((s * 4.4, y + 0.6, -1.6))
            r1 = c + np.array((s * 6.4 * k, y + 0.6, 0.6))
            r2 = c + np.array((s * 5.0 * k, y, 3.2))
            r3 = c + np.array((s * 1.8, y - 0.9, 4.4))
            tubo_caras(out, [r0, r1, r2, r3], [0.9, 0.8, 0.55, 0.12], P['hueso'], semilla=semilla + 2)
    for s in (1, -1):                                                                     # el pelo que enmarca el hueco
        mechones(out, P, c + np.array((s * 6.2, 7.2, -0.6)), (s * 0.12, -1.0, 0.3), np.array((0.0, 0.0, 2.6)), 3, 14.0, 2.0,
                 semilla=semilla + 5)
    return c + np.array((0.0, 0.6, 2.2))


# ======================================================================
#  EL MAPINGUARI
# ======================================================================
def mapinguari(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    pe = P['pelo']
    try:
        # las patas: cortas y gruesas, con los pies al reves (la punta y las garras hacia atras)
        for s in (1, -1):
            cadera = np.array((s * 5.0, 15.0, -1.0))
            rodilla = np.array((s * 6.6, 8.0, 2.4))
            tobillo = np.array((s * 6.4, 2.0, 0.0))
            tubo_caras(out, [cadera, (cadera + rodilla) / 2 + np.array((s * 0.6, 0.0, 0.0)), rodilla], [5.4, 5.0, 3.6], pe, semilla=10)
            tubo_caras(out, [rodilla, tobillo], [3.6, 2.8], pe, semilla=11)
            bm.cubo(out, vr.T(*tobillo), -3.0, -2.0, -6.6, 6.0, 2.8, 8.4, pe, semilla=12)            # el pie, vuelto atras
            for x in (-1.8, 0.0, 1.8):
                tubo_caras(out, [tobillo + np.array((x, -1.2, -6.4)), tobillo + np.array((x, -1.8, -8.6))], [0.6, 0.1],
                           P['garra'], semilla=13)
            mechones(out, P, rodilla + np.array((s * 3.0, 3.0, 0.0)), (s * 0.2, -1.0, 0.0), np.array((0.0, 0.0, 5.0)), 4, 6.0, 1.6,
                     semilla=14)
        # el tronco, en pera: la panza ancha abajo, el pecho y los hombros echados adelante
        tronco = [np.array((0.0, 11.0, -1.0)), np.array((0.0, 16.0, 0.0)), np.array((0.0, 21.5, 1.0)), np.array((0.0, 27.0, 1.8)),
                  np.array((0.0, 32.0, 2.4)), np.array((0.0, 35.0, 3.4))]
        tubo_caras(out, tronco, [7.6, 9.0, 9.4, 8.6, 7.6, 5.6], pe, achata=0.78, arriba=(0.0, 0.0, 1.0), semilla=20)
        tubo_caras(out, [np.array((0.0, 30.0, -2.0)), np.array((0.0, 35.0, -0.6)), np.array((0.0, 37.0, 1.6))], [6.0, 6.4, 4.4],
                   pe, semilla=21)                                                        # la joroba de los hombros
        for s in (1, -1):
            mechones(out, P, np.array((s * 8.8, 32.0, 0.4)), (s * 0.35, -1.0, 0.0), np.array((0.0, 0.0, 7.0)), 5, 9.0, 2.0,
                     semilla=22)                                                          # los flecos de los hombros
            mechones(out, P, np.array((s * 9.6, 20.0, 0.0)), (s * 0.25, -1.0, 0.0), np.array((0.0, 0.0, 8.0)), 5, 8.0, 2.0,
                     semilla=23)                                                          # y de los costados
        for i, (y, z) in enumerate(((36.0, -2.6), (32.0, -5.0), (27.0, -6.6), (21.0, -7.6), (15.0, -7.6))):   # la cresta del lomo
            mechones(out, P, np.array((0.0, y, z)), (0.0, -0.4, -1.0), np.array((7.0, 0.0, 0.0)), 5, 7.0, 2.2, semilla=24 + i, abre=0.9)
        for s in (1, -1):                                                                 # los flecos de los muslos y la panza
            mechones(out, P, np.array((s * 8.6, 13.0, 1.0)), (s * 0.3, -1.0, 0.1), np.array((0.0, 0.0, 9.0)), 5, 6.5, 2.0,
                     semilla=27)
        mechones(out, P, np.array((0.0, 13.0, 7.4)), (0.0, -1.0, 0.25), np.array((10.0, 0.0, 0.0)), 6, 5.0, 2.0, semilla=28)
        corazon = pecho(out, P, V, semilla=30)
        # los brazos, larguisimos, colgando hacia delante, con las garras casi en el suelo
        for s in (1, -1):
            hombro = np.array((s * 9.0, 32.0, 1.6))
            codo = np.array((s * 13.4, 22.0, 4.6))
            muneca = np.array((s * 12.4, 11.0, 10.4))
            tubo_caras(out, [hombro, (hombro + codo) / 2 + np.array((s * 0.8, 0.0, 0.0)), codo], [4.2, 4.4, 3.2], pe, semilla=40)
            tubo_caras(out, [codo, (codo + muneca) / 2, muneca], [3.2, 3.0, 2.6], pe, semilla=41)
            caja(out, vr.T(*hombro), -4.4, 4.4, -4.0, 4.4, -4.4, 4.4, pe, semilla=42)
            mechones(out, P, (codo + muneca) / 2 + np.array((s * 2.8, 0.0, -1.0)), (s * 0.6, -1.0, -0.4), (muneca - codo) * 0.8, 5,
                     5.0, 1.6, semilla=43)                                                # el fleco del antebrazo
            garras(out, P, muneca, (s * 0.15, -0.35, 1.0), s, semilla=44)
        # la cabeza, baja y adelantada
        tubo_caras(out, [np.array((0.0, 34.0, 3.0)), np.array((0.0, 38.4, 4.0))], [4.4, 4.0], pe, semilla=59)   # el cuello
        Mh = vr.T(0.0, 39.4, 4.6) @ vr.Rx(30 * D) @ np.diag([CABEZA] * 3 + [1.0])
        cabeza(out, Mh, P, V, semilla=60)
        # lo de encima de cada tipo
        rng = random.Random(9)
        if V['encima'] == 'musgo':
            for i in range(12):
                p = np.array((rng.uniform(-9, 9), rng.uniform(33.5, 37.0), rng.uniform(-4, 2)))
                caja(out, vr.T(*p) @ vr.Ry(rng.uniform(0, 3)), -2.0, 2.0, -0.6, 1.0, -1.8, 1.8, P['musgo'], semilla=70 + i % 3)
            for i in range(9):                                                            # los helechos que le crecen encima
                p = np.array((rng.uniform(-9, 9), 36.0, rng.uniform(-4, 1)))
                for j in range(5):
                    g = TAU * j / 5 + rng.uniform(0, 1)
                    d = np.array((math.cos(g) * 0.8, 1.0, math.sin(g) * 0.8))
                    l = np.array((-math.sin(g), 0.0, math.cos(g))) * 0.9
                    lamina(out, (p - l + d * 5.0, p + l + d * 5.0, p + l, p - l), P['hoja'], 1.8, 5.0, semilla=72 + j)
        elif V['encima'] == 'lianas':
            for i in range(6):
                x = rng.uniform(-8, 8)
                a = np.array((x, 34.5, rng.uniform(-3, 1)))
                ps = [a, a + np.array((rng.uniform(-1, 1), -6, 1.0)), a + np.array((rng.uniform(-2, 2), -13, 0.5)),
                      a + np.array((rng.uniform(-2, 2), -19, -0.5))]
                tubo_caras(out, ps, [0.45, 0.4, 0.35, 0.2], P['liana'], semilla=70)
                for t in (0.35, 0.7):
                    q = ps[0] + (ps[-1] - ps[0]) * t
                    l = np.array((1.2, 0.0, 0.0))
                    lamina(out, (q - l + np.array((0, -2.4, 0.6)), q + l + np.array((0, -2.4, 0.6)), q + l, q - l), P['hoja'], 2.4, 2.6,
                           semilla=71)
            for i in range(7):
                p = np.array((rng.uniform(-7, 7), 35.0, rng.uniform(-3, 2)))
                for j in range(4):
                    g = TAU * j / 4 + rng.uniform(0, 1)
                    d = np.array((math.cos(g) * 0.9, 0.8, math.sin(g) * 0.9))
                    l = np.array((-math.sin(g), 0.0, math.cos(g))) * 0.8
                    lamina(out, (p - l + d * 3.6, p + l + d * 3.6, p + l, p - l), P['hoja'], 1.6, 3.6, semilla=72 + j)
        elif V['encima'] == 'huesos':                                                      # collar de huesos y semillas
            for i, a in enumerate(np.linspace(-1.2, 1.2, 9)):
                p = np.array((math.sin(a) * 7.0, 31.6 - abs(math.sin(a)) * 1.2, 4.4 + math.cos(a) * 2.6))
                caja(out, vr.T(*p) @ vr.Ry(a), -0.5, 0.5, -2.6 if i % 2 == 0 else -1.6, 0.0, -0.5, 0.5, P['hueso'], semilla=73)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    corazon = pt(E, corazon)
    ojo = pt(E @ Mh, (0.0, 2.0, 4.6))
    return out, {'corazon': corazon, 'ojo': ojo, 'luces': [corazon, ojo]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

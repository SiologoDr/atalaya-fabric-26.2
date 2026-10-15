"""
El Lobison y sus tipos (15-10-2026), el primer mob normal. Juan, al guardar el Oni: «ahora ya no vamos a hacer bosses,
ahora vamos a hacer mobs normales; crea un mob con sus 3 tipos».

El Lobison sale de la leyenda guarani (y de todo el sur de America): el septimo hijo varon que, las noches de luna
llena, se convierte en una bestia. Como mob es un hombre lobo del tamano de los de Minecraft (2,6 bloques encorvado):
la cabeza de lobo con el hocico y la quijada abierta que arde por dentro y los ojos encendidos, el lomo encorvado, los
brazos largos con las garras, las patas de lobo (la rodilla delante y el corvejon atras) y la cola.

Se modela como un mob de vanilla: en pixeles de la piel (16 por bloque) y con un texel por pixel, en cajas. Las
texturas, limpias, de cinco tonos, con el pelo en hebras.

Los tres tipos son de tres sitios, como las variantes de los mobs de vanilla, y tienen la misma pose (encorvado, los
brazos adelante para el zarpazo, gruñendo):

    A  del Monte    pardo oscuro, la crin larga por el lomo y una oreja rota; ojos de ambar
    B  de la Nieve  blanco plata, la gorguera de pelo espeso al cuello y la cola muy poblada; ojos de hielo
    C  del Paramo   ocre con rayas oscuras, las orejas enormes y una fila de puas de hueso por el espinazo; ojos rojos
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, lamina
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 1                      # un texel por pixel, como un mob de vanilla
ESCALA = 1.0 / 16.0          # de pixeles a bloques

VARIANTES = {
    'A': dict(
        clave='LA', nombre='del Monte', corto='monte', marca='crin',
        pelo=_r('1a140f', '2c231b', '3e3227', '52443a', '6a5a4c'),
        claro=_r('4a3e32', '665646', '84725c', 'a08c72', 'bca88a'),
        neon=('fff2c8', 'ffb21a', '6a3a04'),
        rayas=False,
    ),
    'B': dict(
        clave='LB', nombre='de la Nieve', corto='nieve', marca='gorguera',
        pelo=_r('7a8088', 'a2a8b0', 'c6ccd2', 'e2e6ea', 'f6f8fa'),
        claro=_r('a8aeb6', 'c8ced4', 'e0e4e8', 'f0f2f4', 'fcfdfe'),
        neon=('e8ffff', '6ae0ff', '0a4a6a'),
        rayas=False,
    ),
    'C': dict(
        clave='LC', nombre='del Paramo', corto='paramo', marca='puas',
        pelo=_r('4a2a12', '6e4019', '925a24', 'b47836', 'd09a52'),
        claro=_r('8a6a40', 'ae8a56', 'cca870', 'e0c08a', 'f0d8a8'),
        neon=('ffe6e0', 'ff3a2a', '6a0a04'),
        rayas=True,
    ),
}

NEGRO = _r('0a0808', '141010', '1e1818', '2a2222', '362c2c')
GARRA = _r('5a5448', '847c6c', 'aca290', 'd0c8b4', 'eee8d8')
CARNE = _r('2a0a0c', '42121a', '5e1c24', '7a2a30', '963a3e')
HUESO = _r('6a6452', 'a09a7e', 'cac4a6', 'e6e0c4', 'fbf8e6')


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


# ----------------------------------------------------------------------
#  Los pintores: a un texel por pixel, como una piel de vanilla
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    neo = [nm._hex(c) for c in V['neon']]

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'lob%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def hebras(tw, th, s, rampa, cara, largo_y=True):
        """El pelo en hebras: el tono de fondo con mechones de tres o cuatro texeles (uno claro, uno oscuro) puestos en
        filas, sin motas sueltas; mas claro arriba y mas oscuro abajo. En el Paramo, las rayas oscuras de traves."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a, t = (ys, xs) if largo_y else (xs, ys)
        n = th if largo_y else tw
        idx = np.full((th, tw), 2)
        claro = ((a + t * 3 + s) % 7 < 3) & (t % 2 == 0)
        oscuro = ((a + t * 5 + s + 4) % 9 < 3) & (t % 2 == 1)
        idx = np.where(claro, 3, np.where(oscuro, 1, idx))
        if cara == 'arriba':
            idx = np.clip(idx + 1, 0, 4)
        elif cara == 'abajo':
            idx = np.clip(idx - 1, 0, 4)
        img = _imagen(idx, rampa)
        if V['rayas'] and cara != 'abajo':
            raya = ((t + (a // 3) % 2) % 6 < 2) if not largo_y else (((a + (t // 3) % 2) % 6) < 2)
            img = np.where(raya[..., None], _imagen(np.clip(idx - 2, 0, 4), V['pelo']), img)
        return img

    def pelo(tw, th, cara, s):
        return hebras(tw, th, s, V['pelo'], cara, largo_y=cara not in ('arriba', 'abajo')), None
    reg('pelo', pelo)

    def pelo_largo(tw, th, cara, s):
        """El pelo de las piezas largas (brazos, patas, cola): las hebras a lo largo de la pieza."""
        return hebras(tw, th, s, V['pelo'], cara, largo_y=cara in ('arriba', 'abajo')), None
    reg('pelo_largo', pelo_largo)

    def pecho(tw, th, cara, s):
        return hebras(tw, th, s + 2, V['claro'], cara), None
    reg('pecho', pecho)

    def cara(tw, th, cara_, s):
        """La cara por delante (8 de ancho): la frente con el ceno, los ojos rasgados que arden y el entrecejo oscuro."""
        img = hebras(tw, th, s, V['pelo'], 'frente')
        ojo = np.zeros((th, tw), bool)
        y = int(th * 0.4)
        for x0, paso in ((1, 1), (tw - 3, -1)):
            for dx in range(2):
                ojo[y, x0 + dx] = True
            ojo[y - 1, x0 + (1 if paso > 0 else 0)] = True                 # el rabillo, que sube hacia fuera
        img[ojo] = (*neo[1], 255)
        img[y, 2] = (*neo[0], 255)
        img[y, tw - 3] = (*neo[0], 255)
        for x in range(0, tw):                                              # el ceno: la frente oscura sobre los ojos
            if x in (1, 2, tw - 3, tw - 2):
                img[y - 2, x] = (*V['pelo'][0], 255)
        img[y - 1, tw // 2 - 1:tw // 2 + 1] = (*V['pelo'][0], 255)
        return img, _emis(img, ojo, 255)
    reg('cara', cara)

    def hocico(tw, th, cara_, s):
        """El hocico por delante: la trufa negra arriba y el labio oscuro abajo."""
        img = hebras(tw, th, s, V['claro'], 'frente')
        img[0:2, 1:tw - 1] = (*NEGRO[2], 255)
        img[0, 1:tw - 1] = (*NEGRO[3], 255)
        img[th - 1, :] = (*NEGRO[1], 255)
        return img, None
    reg('hocico', hocico)

    def boca(tw, th, cara_, s):
        """Dentro de la boca (el cielo y el suelo): la carne con los surcos, encendida hacia el fondo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = ys / max(th - 1, 1)                                             # hacia el fondo
        t = _imagen(np.where(xs % 2 == 0, 1, 2), CARNE)
        luz = f > 0.55
        t[luz] = (*neo[1], 255)
        t[f > 0.85] = (*neo[0], 255)
        return t, _emis(t, luz, 220)
    reg('boca', boca)

    def dientes(tw, th, cara_, s):
        """Los dientes, en hoja: colmillos en las esquinas y dientes pequenos entre ellos."""
        t = np.zeros((th, tw, 4), np.uint8)
        for x in range(tw):
            largo = th if x in (0, tw - 1) else (th - 1 if x % 2 == 0 else 0)
            for y in range(largo):
                t[y, x] = (*(HUESO[3] if y < largo - 1 else HUESO[2]), 255)
        return t, None
    reg('dientes', dientes)

    def oreja(tw, th, cara_, s):
        """La oreja por delante: el pelo con el hueco de dentro, oscuro y rosado."""
        img = hebras(tw, th, s, V['pelo'], 'frente')
        if tw >= 3 and th >= 3:
            img[1:th, 1:tw - 1] = (*CARNE[1], 255)
            img[th - 1, 1:tw - 1] = (*CARNE[2], 255)
        return img, None
    reg('oreja', oreja)

    def garra(tw, th, cara_, s):
        return _imagen(_bisel(np.full((th, tw), 3), 1, 1), GARRA), None
    reg('garra', garra)

    def hueso(tw, th, cara_, s):
        return _imagen(_bisel(np.full((th, tw), 3), 1, 1), HUESO), None
    reg('hueso', hueso)

    def almohadilla(tw, th, cara_, s):
        return _imagen(np.full((th, tw), 2), NEGRO), None
    reg('almohadilla', almohadilla)
    return P


# ----------------------------------------------------------------------
#  Cajas
# ----------------------------------------------------------------------
def pieza(out, p0, p1, ancho, alto, pin, arriba=(0.0, 1.0, 0.0), extra=0.0, caras=None, semilla=0):
    """Una caja de p0 a p1 (de seccion ancho x alto), como una pieza de un modelo de vanilla girada."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    up = np.asarray(arriba, float)
    if abs(_u(d) @ _u(up)) > 0.95:
        up = np.array((0.0, 0.0, 1.0)) if abs(_u(d)[2]) < 0.95 else np.array((1.0, 0.0, 0.0))
    M = em.marco(p0, d, up=up)
    bm.cubo(out, M, -ancho / 2, -alto / 2, -extra, ancho, alto, float(np.linalg.norm(d)) + 2 * extra, pin, caras=caras,
            semilla=semilla)
    return M


# ======================================================================
#  EL LOBISON
# ======================================================================
def lobison(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    pe, pl = P['pelo'], P['pelo_largo']
    try:
        # ---- las patas de lobo: el muslo, la canilla hacia atras, el pie largo y los dedos con garras
        for s in (-1, 1):
            cad = np.array((s * 3.6, 21.0, -3.0))
            rod = np.array((s * 4.4, 14.0, 1.6))
            cor = np.array((s * 4.6, 7.0, -3.4))
            pie = np.array((s * 4.6, 1.6, 0.6))
            pieza(out, cad, rod, 5.0, 5.0, pl, extra=1.0, semilla=1)
            pieza(out, rod, cor, 3.6, 3.6, pl, extra=0.8, semilla=2)
            pieza(out, cor, pie, 3.0, 3.0, pl, extra=0.6, semilla=3)
            bm.cubo(out, vr.T(*pie), -2.0, -1.6, -1.0, 4.0, 2.4, 4.2, pe, caras={'abajo': P['almohadilla']}, semilla=4)
            for x in (-1.3, 0.0, 1.3):                                      # las garras de los pies
                pieza(out, pie + np.array((x, -0.9, 3.0)), pie + np.array((x, -1.5, 4.6)), 0.7, 0.7, P['garra'], semilla=5)
        # ---- el tronco, encorvado: las caderas, el vientre y el pecho
        cadera, pecho_c = np.array((0.0, 21.0, -3.0)), np.array((0.0, 29.0, 6.0))
        Mt = pieza(out, cadera, pecho_c, 9.0, 7.0, pe, extra=1.5, caras={'abajo': P['pecho']}, semilla=10)
        pieza(out, pecho_c + np.array((0.0, -1.0, -1.0)), pecho_c + np.array((0.0, 3.0, 3.0)), 11.0, 9.0, pe, extra=1.0,
              caras={'abajo': P['pecho'], 'frente': P['pecho']}, semilla=11)                         # el pecho, ancho
        pieza(out, (0.0, 24.0, 4.0), (0.0, 29.0, 9.0), 8.0, 5.0, P['pecho'], semilla=12)              # el pecho claro
        # ---- los brazos: largos, adelante, con las manos abiertas y las garras
        for s in (-1, 1):
            hombro = np.array((s * 6.4, 31.0, 6.0))
            codo = np.array((s * 9.6, 24.0, 11.0))
            muneca = np.array((s * 8.4, 18.0, 16.6))
            pieza(out, hombro, codo, 4.0, 4.0, pl, extra=1.0, semilla=20)
            pieza(out, codo, muneca, 3.4, 3.4, pl, extra=0.8, semilla=21)
            Mm = em.marco(muneca, _u(muneca - codo), up=(0.0, 0.0, 1.0))
            bm.cubo(out, Mm, -2.0, -1.4, 0.0, 4.0, 2.8, 3.0, pe, semilla=22)                       # la mano
            d = _u(muneca - codo)
            lado = _u(np.cross(d, (0.0, 0.0, 1.0)))
            for j in (-1, 0, 1):                                             # los dedos y las garras
                a = muneca + d * 2.8 + lado * j * 1.3
                b = a + d * 2.0 + np.array((0.0, 0.0, 0.6))
                pieza(out, a, b, 1.0, 1.0, pe, semilla=23)
                pieza(out, b, b + d * 1.6 + np.array((0.0, -1.0, 0.8)), 0.8, 0.8, P['garra'], semilla=24)
        # ---- la cabeza, adelantada y baja, gruñendo
        Mh = vr.T(0.0, 31.6, 11.0) @ vr.Rx(-4 * D)
        bm.cubo(out, Mh, -4.5, -1.5, -3.5, 9.0, 8.0, 7.5, pe, caras={'frente': P['cara']}, semilla=30)      # el craneo
        bm.cubo(out, Mh, -2.2, -0.6, 4.0, 4.4, 3.0, 6.0, pe, caras={'frente': P['hocico'], 'abajo': P['boca']}, semilla=31)
        bm.cubo(out, Mh, -1.6, 2.4, 3.8, 3.2, 1.2, 5.0, pe, semilla=32)                                       # el lomo del hocico
        Mj = Mh @ vr.T(0.0, -0.6, 4.0) @ vr.Rx(0.62)                                                          # la quijada
        bm.cubo(out, Mj, -2.0, -1.4, 0.0, 4.0, 1.4, 5.6, P['pecho'], caras={'arriba': P['boca']}, semilla=33)
        a, b = pt(Mh, (-2.2, -0.6, 10.0)), pt(Mh, (2.2, -0.6, 10.0))
        lamina(out, (pt(Mh, (-2.2, -2.0, 10.0)), pt(Mh, (2.2, -2.0, 10.0)), b, a), P['dientes'], 4.4, 1.4)      # los de arriba
        lamina(out, (pt(Mh, (2.2, -2.0, 10.0)), pt(Mh, (-2.2, -2.0, 10.0)), a, b), P['dientes'], 4.4, 1.4)
        a, b = pt(Mj, (-2.0, 0.0, 5.6)), pt(Mj, (2.0, 0.0, 5.6))
        lamina(out, (a, b, pt(Mj, (2.0, 1.3, 5.6)), pt(Mj, (-2.0, 1.3, 5.6))), P['dientes'], 4.0, 1.3)          # los de abajo
        lamina(out, (b, a, pt(Mj, (-2.0, 1.3, 5.6)), pt(Mj, (2.0, 1.3, 5.6))), P['dientes'], 4.0, 1.3)
        bm.cubo(out, Mh, -4.0, -3.0, -2.6, 8.0, 1.6, 5.4, P['pecho'], semilla=34)                              # la papada
        orejas(out, Mh, P, V)
        marca(out, Mh, P, V, cadera, pecho_c)
        # ---- la cola
        cola = [cadera + np.array((0.0, 1.0, -3.0)), cadera + np.array((0.0, -2.0, -8.0)), cadera + np.array((0.0, -3.0, -13.0)),
                cadera + np.array((0.0, -1.0, -17.0))]
        anchos = (4.0, 4.6, 4.0, 2.4) if V['marca'] != 'puas' else (2.6, 2.4, 2.0, 1.4)
        if V['marca'] == 'gorguera':
            anchos = (5.0, 6.2, 5.6, 3.4)
        for j in range(3):
            pieza(out, cola[j], cola[j + 1], anchos[j], anchos[j], pl, extra=0.6, semilla=40 + j)
        if V['marca'] == 'puas':                                             # el penacho de la punta
            pieza(out, cola[3], cola[3] + np.array((0.0, 1.0, -3.0)), 3.4, 3.4, P['pelo'], semilla=43)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    return out, {'boca': pt(E @ Mh, (0.0, -0.6, 9.0)), 'ojos': pt(E @ Mh, (0.0, 3.4, 4.2)),
                 'luces': [pt(E @ Mh, (0.0, -0.8, 7.0))]}


def orejas(out, Mh, P, V):
    """Las orejas: altas y en punta (dos escalones); en el Monte, la izquierda rota; en el Paramo, enormes."""
    grande = V['marca'] == 'puas'
    for s in (-1, 1):
        Mo = Mh @ vr.T(s * 2.9, 6.5, -0.6) @ vr.Rz(-s * (0.3 if grande else 0.18)) @ vr.Rx(-0.15)
        h = 5.0 if grande else 3.4
        w = 3.2 if grande else 2.6
        rota = V['marca'] == 'crin' and s < 0
        bm.cubo(out, Mo, -w / 2, 0.0, -0.6, w, h * (0.6 if rota else 1.0), 1.4, P['pelo'], caras={'frente': P['oreja']},
                semilla=50)
        if not rota:
            bm.cubo(out, Mo, -w / 4, h, -0.4, w / 2, h * 0.5, 1.0, P['pelo'], semilla=51)


def marca(out, Mh, P, V, cadera, pecho_c):
    """Lo de cada tipo: la crin larga por el lomo (Monte), la gorguera de pelo al cuello (Nieve) o las puas de hueso
    por el espinazo (Paramo)."""
    if V['marca'] == 'crin':
        for j, t in enumerate(np.linspace(0.0, 1.0, 6)):
            p = pt(Mh, (0.0, 6.0, -2.0)) * (1 - t) + (cadera + np.array((0.0, 3.0, -1.0))) * t
            h = 4.0 - 2.4 * t
            bm.cubo(out, vr.T(*p) @ vr.Rx(-0.5), -1.6, 0.0, -2.0, 3.2, h, 3.0, P['pelo'], semilla=60 + j)
    elif V['marca'] == 'gorguera':
        c = pecho_c + np.array((0.0, 3.4, 3.0))
        for j, (w, h, d, dy) in enumerate(((14.0, 6.0, 10.0, 0.0), (12.0, 4.0, 12.0, -2.4), (10.0, 3.0, 9.0, 3.0))):
            bm.cubo(out, vr.T(*(c + np.array((0.0, dy, 0.0)))) @ vr.Rx(-0.35), -w / 2, -h / 2, -d / 2, w, h, d, P['pelo'],
                    caras={'frente': P['pecho']}, semilla=61 + j)
        for s in (-1, 1):                                                    # los puños de pelo
            p = np.array((s * 9.0, 21.0, 10.8))
            bm.cubo(out, vr.T(*p), -2.6, -2.0, -2.6, 5.2, 4.0, 5.2, P['pelo'], semilla=64)
    else:
        for j, t in enumerate(np.linspace(0.05, 0.95, 7)):
            p = pt(Mh, (0.0, 5.4, -2.6)) * (1 - t) + (cadera + np.array((0.0, 3.6, -1.6))) * t
            h = 3.2 - 1.6 * abs(t - 0.4)
            pieza(out, p, p + np.array((0.0, h, -h * 0.5)), 1.2, 1.2, P['hueso'], semilla=65)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

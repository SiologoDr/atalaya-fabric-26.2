"""
Kalara y sus tipos (15-10-2026). Juan, al dejar la ilustracion: «mejor sigamos haciendolo como estabamos antes de
pedirte la ilustracion; hagamos otros boss y sus 3 tipos». Kalara sale de la leyenda del Kala (el Kirtimukha de la
India, la «Cara de Gloria»): un monstruo con tanta hambre que, cuando no le quedo nada que comer, se comio su propio
cuerpo, y solo le quedaron la cara y las manos. Por eso su cara esta sobre las puertas de los templos.

Una forma que no tenemos: no tiene cuerpo. Es una cara colosal que flota a ras del suelo y asoma las dos manos
garrudas para arrastrarse hacia ti. Del Kala le quedan rastros: los ojos saltones bajo las cejas en ceno, la nariz
ancha, los colmillos que cuelgan de la comisura y, sobre todo, que no tiene quijada de abajo: la boca es un arco
abierto que arde por dentro (el paladar en escalones y la garganta encendida al fondo). Detras le cuelga la melena
hasta el suelo, donde estaba el cuerpo.

Hecha desde cero (sin piezas de otros jefes): formas de ocho lados, texturas limpias de cinco tonos con vetas como
curvas de nivel, el oro de los adornos y los dientes en hoja.

Los tres tipos tienen la misma pose y cambian lo que enmarca la cara y el color:

    A  la Melena    una corona de mechones de llama alrededor de la cara, con la punta encendida, y dos cuernos
                    cortos; granate y oro, luz ambar
    B  los Cuernos  dos cuernos de carnero enormes que se enroscan a los lados, y las orejas con discos de bronce;
                    jade y bronce, luz de jade
    C  la Corona    una corona alta de cinco puntas de oro y dos colmillos de jabali que suben de la boca, y las
                    orejas; negra, luz roja
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _limpiar, _degradado, lamina
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.55

VARIANTES = {
    'A': dict(
        clave='KA', nombre='la Melena', corto='melena', marco='melena',
        piel=_r('1a0806', '2e100c', '461a12', '5e281a', '7a3824'),
        pelo=_r('140404', '280a06', '42140a', '5e2210', '7e3418'),
        cuerno=_r('5a4a36', '8a7656', 'b8a27c', 'dccaa2', 'f6eacc'),
        neon=('fff0c8', 'ffb21a', '6a3a04'),
    ),
    'B': dict(
        clave='KB', nombre='los Cuernos', corto='cuernos', marco='cuernos',
        piel=_r('061410', '0c221a', '143426', '1e4a36', '2c644a'),
        pelo=_r('040c0a', '081812', '0e241c', '163428', '204636'),
        cuerno=_r('3a2410', '6a4420', '9a6a30', 'c69446', 'eac06a'),
        neon=('e8fff6', '3affc8', '045a40'),
    ),
    'C': dict(
        clave='KC', nombre='la Corona', corto='corona', marco='corona',
        piel=_r('0a080e', '141018', '201a26', '2e2636', '40364a'),
        pelo=_r('050408', '0a080e', '120e16', '1a1620', '24202c'),
        cuerno=_r('6a6452', 'a09a7e', 'cac4a6', 'e6e0c4', 'fbf8e6'),
        neon=('ffe6e0', 'ff2a2a', '6a0404'),
    ),
}

ORO = _r('5a3a08', '8a5c10', 'c08a1e', 'e8b83a', 'fae27a')
DIENTE = _r('6a6452', 'a09a7e', 'cac4a6', 'e6e0c4', 'fbf8e6')
GARRA = _r('0c0a08', '1a1612', '2a241e', '3e362c', '564c40')
CARNE = _r('140406', '24080a', '360e10', '4a1618', '5e2022')


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
    OSCURO = (8, 4, 4, 255)

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'kal%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def piel(tw, th, cara, s):
        """La piel: lisa, con vetas finas como curvas de nivel, mas clara arriba y mas oscura abajo."""
        v = bm._ruido(tw, th, s, 18.0)
        idx = np.where(((v * 5.0) % 1.0) < 0.09, 1, 2)
        idx = _limpiar(idx)
        if cara == 'arriba':
            idx = idx + 1
        elif cara == 'abajo':
            idx = idx - 1
        return _imagen(_bisel(np.clip(idx, 0, 4), 1, 1), V['piel']), None
    reg('piel', piel)

    def oro(tw, th, cara, s):
        """El oro de los adornos: liso, con muescas grabadas en la fila del medio y el bisel."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        if th >= 5:
            idx = np.where((abs(ys - th / 2 + 0.5) < 0.6) & (xs % 4 != 0), 2, idx)
        return _imagen(_bisel(idx, 1, 1), ORO), None
    reg('oro', oro)

    def nariz(tw, th, cara, s):
        """La nariz por delante: ancha, con las dos ventanas oscuras y la sombra de las aletas."""
        img, _ = piel(tw, th, cara, s)
        ys, xs = np.mgrid[0:th, 0:tw]
        for cx in (0.3, 0.7):
            d = np.hypot((xs + 0.5 - cx * tw) / (0.14 * tw), (ys + 0.5 - 0.68 * th) / (0.16 * th))
            img[d < 1.0] = OSCURO
        return img, None
    reg('nariz', nariz)

    def carne(tw, th, cara, s):
        """Dentro de la boca, los lados: carne oscura con pliegues que bajan, un poco encendida hacia el fondo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs % 4 == 0, 1, 2)
        img = _imagen(idx, CARNE)
        return img, None
    reg('carne', carne)

    def paladar(tw, th, cara, s):
        """El cielo de la boca (la cara de abajo de la boca de arriba): escalones de luz del borde (oscuro) al fondo
        (blanco), con las estrias oscuras entre uno y otro."""
        t = _degradado(th, tw, True, V['neon'][0], V['neon'][1], V['neon'][2])
        luz = t[..., :3].sum(axis=2) > 200
        return t, _emis(t, luz, 220)
    reg('paladar', paladar)

    def garganta(tw, th, cara, s):
        """El fondo de la garganta: un remolino de luz, blanco en el centro, con brazos de neon y de sombra."""
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        dx, dy = (xs - cx) / max(cx, 1), (ys - cy) / max(cy, 1)
        r = np.hypot(dx, dy)
        a = np.arctan2(dy, dx)
        brazo = ((a + r * 4.0) % (TAU / 3)) < (TAU / 6)
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[2], 255)
        t[brazo] = (*neo[1], 255)
        t[r < 0.3] = (*neo[0], 255)
        return t, None
    reg('garganta', garganta, pleno=True)

    def dientes(tw, th, cara, s):
        """Los dientes de arriba, dibujados en hoja: anchos y romos, de canto redondeado, con un hueco entre uno y otro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        paso = 6
        x = xs % paso
        diente = (x < paso - 1) & ~((ys == th - 1) & ((x == 0) | (x == paso - 2)))
        t[diente] = (*DIENTE[3], 255)
        t[diente & (x >= paso // 2)] = (*DIENTE[2], 255)
        t[diente & (ys == 0)] = (*DIENTE[1], 255)
        return t, None
    reg('dientes', dientes)

    def colmillo(tw, th, cara, s):
        """El colmillo, dibujado en hoja: la base arriba y la punta abajo, con la cara de la luz mas clara."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            w = tw * (1 - y / th) ** 0.8
            a, b = (tw - w) / 2, (tw + w) / 2
            for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                c = DIENTE[4] if x < tw / 2 else DIENTE[2]
                if x == int(math.floor(a)) or x == int(math.ceil(b)) - 1:
                    c = DIENTE[1]
                t[y, x] = (*c, 255)
        return t, None
    reg('colmillo', colmillo)

    def ojo(tw, th, cara, s):
        """El ojo, en hoja: almendrado, con el parpado de arriba en ceno (la esquina de dentro mas baja), el blanco
        amarillento, el iris que arde y la pupila rasgada."""
        ys, xs = np.mgrid[0:th, 0:tw]
        u = (xs + 0.5) / tw * 2 - 1
        v = (ys + 0.5) / th * 2 - 1
        almendra = (abs(v) < 0.95 * (1 - u * u) ** 0.6)
        lado = 1 if s % 2 == 0 else -1                                  # hacia donde esta la nariz
        ceno = v < -0.15 + lado * u * 0.5
        dentro = almendra & ~ceno
        t = np.zeros((th, tw, 4), np.uint8)
        t[almendra] = (*V['piel'][0], 255)
        t[dentro] = (226, 214, 176, 255)
        iris = dentro & (np.hypot(u * 1.1, v - 0.1) < 0.62)
        t[iris] = (*neo[1], 255)
        t[iris & (np.hypot(u * 1.1, v - 0.1) < 0.3)] = (*neo[0], 255)
        pupila = dentro & (abs(u) < 0.1) & (abs(v - 0.1) < 0.5)
        t[pupila] = OSCURO
        return t, _emis(t, iris & ~pupila, 255)
    reg('ojo_d', ojo)

    def ojo_i(tw, th, cara, s):
        return ojo(tw, th, cara, s + 1)
    reg('ojo_i', ojo_i)

    def llama(tw, th, cara, s):
        """El mechon de la melena, en hoja: una llama que se estrecha hacia la punta, oscura, con la veta del medio y la
        punta encendida."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = 1 - (ys + 0.5) / th                                           # 0 en la raiz (abajo), 1 en la punta
        ancho = 0.5 * (1 - f ** 1.6) + 0.05
        onda = 0.08 * np.sin(f * 9.0)
        dentro = abs((xs + 0.5) / tw - 0.5 - onda) < ancho
        idx = np.where(abs((xs + 0.5) / tw - 0.5 - onda) < 0.1, 3, 2)
        img = _imagen(idx, V['pelo'])
        canto = dentro & ~(abs((xs + 0.5) / tw - 0.5 - onda) < ancho - 0.1)
        punta = (dentro & (f > 0.86)) | (canto & (f > 0.55))
        img[punta] = (*neo[1], 255)
        img[dentro & (f > 0.94)] = (*neo[0], 255)
        img[..., 3] = np.where(dentro, 255, 0)
        return img, _emis(img, punta, 230)
    reg('llama', llama)

    def mechon(tw, th, cara, s):
        """Los mechones que le cuelgan por detras hasta el suelo: oscuros, con hebras a lo largo, en punta abajo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = (ys + 0.5) / th                                               # 0 arriba, 1 en la punta (abajo)
        dentro = abs((xs + 0.5) / tw - 0.5) < 0.5 * (1 - f ** 3)
        idx = np.where(xs % 3 == 0, 1, 2)
        img = _imagen(idx, V['pelo'])
        img[..., 3] = np.where(dentro, 255, 0)
        return img, None
    reg('mechon', mechon)

    def cuerno(tw, th, cara, s):
        """El cuerno: anillado, con el bisel."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a = xs if cara in ('der', 'izq') else ys
        idx = np.where(a % 4 == 0, 2, 3)
        return _imagen(_bisel(idx, 1, 1), V['cuerno']), None
    reg('cuerno', cuerno)

    def garra(tw, th, cara, s):
        return _imagen(_bisel(np.full((th, tw), 2), 1, 1), GARRA), None
    reg('garra', garra)

    def gema(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        d = np.maximum(abs(xs - (tw - 1) / 2) / max(tw / 2, 1), abs(ys - (th - 1) / 2) / max(th / 2, 1))
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[2], 255)
        t[d < 0.75] = (*neo[1], 255)
        t[d < 0.35] = (*neo[0], 255)
        return t, None
    reg('gema', gema, pleno=True)

    def punta_oro(tw, th, cara, s):
        """Una punta de la corona, en hoja: oro en forma de llama con una gema en medio."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = 1 - (ys + 0.5) / th
        dentro = abs((xs + 0.5) / tw - 0.5) < 0.5 * (1 - f ** 1.4) + 0.03
        borde = dentro & ~(abs((xs + 0.5) / tw - 0.5) < 0.5 * (1 - f ** 1.4) - 0.12)
        img = _imagen(np.where(borde, 4, 3), ORO)
        g = np.hypot((xs + 0.5) / tw - 0.5, (f - 0.3) * th / tw) < 0.16
        img[g & dentro] = (*neo[1], 255)
        img[..., 3] = np.where(dentro, 255, 0)
        return img, _emis(img, g & dentro, 255)
    reg('punta_oro', punta_oro)
    return P


# ----------------------------------------------------------------------
#  Formas
# ----------------------------------------------------------------------
def losa(out, M, y0, y1, rx, rz, pin, caras=None, k=0.74, semilla=0):
    """Una losa de ocho lados en planta (dos cajas cruzadas)."""
    bm.cubo(out, M, -rx, y0, -rz * k, 2 * rx, y1 - y0, 2 * rz * k, pin, caras=caras, semilla=semilla)
    bm.cubo(out, M, -rx * k, y0, -rz, 2 * rx * k, y1 - y0, 2 * rz, pin, caras=caras, semilla=semilla + 1)


def tubo(out, pts, radios, pin, caras=None, semilla=0, arriba=(0.0, 1.0, 0.0)):
    """Un tubo de ocho lados por los puntos."""
    for j in range(len(pts) - 1):
        p0, p1 = np.asarray(pts[j], float), np.asarray(pts[j + 1], float)
        d = p1 - p0
        L = float(np.linalg.norm(d))
        if L < 1e-4:
            continue
        up = np.asarray(arriba, float)
        if abs(_u(d) @ _u(up)) > 0.95:
            up = np.array((0.0, 0.0, 1.0)) if abs(_u(d)[2]) < 0.95 else np.array((1.0, 0.0, 0.0))
        M = em.marco(p0, d, up=up)
        r = (radios[j] + radios[j + 1]) / 2
        for kx, ky in ((1.0, 0.72), (0.72, 1.0)):
            bm.cubo(out, M, -r * kx, -r * ky, -r * 0.3, 2 * r * kx, 2 * r * ky, L + r * 0.6, pin, caras=caras,
                    semilla=semilla + j % 3)


def hoja(out, P4, pintor, ancho, alto, semilla=0):
    """Una lamina que se ve por las dos caras (p0 abajo-izq, p1 abajo-der, p2 arriba-der, p3 arriba-izq)."""
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def mechon(out, pintor, raiz, dirl, lado, largo, ancho, semilla=0):
    """Un mechon en hoja desde la raiz hacia 'dirl', de lado a lado segun 'lado'."""
    raiz, d, l = np.asarray(raiz, float), _u(dirl), _u(lado) * ancho / 2
    hoja(out, (raiz - l, raiz + l, raiz + l + d * largo, raiz - l + d * largo), pintor, ancho, largo, semilla)


# ======================================================================
#  KALARA
# ======================================================================
def cara(out, Mh, P, V):
    """La cara, mirando a +z, con la comisura de la boca en y=0: la frente y el craneo, los pomulos y las mejillas
    que bajan a los lados de la boca, la boca de arriba con los dientes y los colmillos, la nariz, las cejas en ceno
    sobre los ojos, la gema de la frente y la garganta al fondo del arco de la boca (sin quijada de abajo)."""
    pi = P['piel']
    pal = {'abajo': P['paladar']}
    losa(out, Mh @ vr.T(0.0, 0.0, -3.0), 5.0, 15.0, 15.6, 10.0, pi, semilla=10)                     # el craneo, que se
    losa(out, Mh @ vr.T(0.0, 0.0, -3.2), 15.0, 19.0, 13.6, 9.0, pi, semilla=11)                     # estrecha arriba
    losa(out, Mh @ vr.T(0.0, 0.0, -3.6), 19.0, 21.6, 10.4, 7.0, pi, semilla=11)
    losa(out, Mh @ vr.T(0.0, 0.0, -4.0), 21.6, 23.0, 6.8, 5.0, pi, semilla=11)
    for s in (-1, 1):                                                                          # las mejillas y su papada
        Ms = Mh @ vr.T(s * 12.8, 0.0, 0.0)
        dentro = {'izq' if s > 0 else 'der': P['carne']}
        losa(out, Ms, -9.0, 9.0, 5.4, 7.4, pi, caras=dentro, semilla=12)
        losa(out, Ms @ vr.T(s * 1.2, 0.0, 1.6), -10.4, -4.6, 4.8, 6.0, pi, caras=dentro, semilla=13)
        losa(out, Ms @ vr.T(s * 2.0, 0.0, 2.8), 3.0, 8.4, 4.4, 4.8, pi, semilla=14)              # el pomulo
    bm.cubo(out, Mh, -8.6, 0.0, -6.0, 17.2, 5.4, 8.0, pi, caras=pal, semilla=15)               # el cielo de la boca, atras
    bm.cubo(out, Mh, -9.4, 0.0, 2.0, 18.8, 4.6, 7.4, pi, caras=pal, semilla=16)                # la boca de arriba
    bm.cubo(out, Mh, -8.0, 0.4, 9.4, 16.0, 3.4, 1.0, pi, caras=pal, semilla=17)                # el labio
    bm.cubo(out, Mh, -7.8, -10.6, -7.4, 15.6, 11.2, 1.0, P['carne'], caras={'frente': P['garganta']}, semilla=18)
    bm.cubo(out, Mh, -8.2, -11.0, -8.6, 16.4, 11.6, 1.2, P['carne'], semilla=18)
    bm.cubo(out, Mh, -4.6, 4.4, 5.2, 9.2, 4.6, 5.6, pi, caras={'frente': P['nariz']}, semilla=19)   # la nariz
    bm.cubo(out, Mh, -2.6, 8.6, 4.4, 5.2, 4.6, 4.4, pi, semilla=20)
    # los dientes de arriba, por el canto de la boca, y los colmillos de la comisura
    filo = [(-9.0, 2.6), (-9.0, 8.4), (-7.6, 10.3), (7.6, 10.3), (9.0, 8.4), (9.0, 2.6)]
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(filo, filo[1:])):
        A, B = pt(Mh, (x0, 0.2, z0)), pt(Mh, (x1, 0.2, z1))
        hoja(out, (pt(Mh, (x0, -2.6, z0)), pt(Mh, (x1, -2.6, z1)), B, A), P['dientes'], float(np.linalg.norm(B - A)), 2.8,
             semilla=21 + j)
    for s in (-1, 1):
        b = pt(Mh, (s * 7.0, 0.4, 9.6))
        abajo = Mh[:3, :3] @ _u(np.array((s * 0.12, -1.0, 0.15)))
        for lado in (Mh[:3, 0], Mh[:3, 2]):
            l = _u(lado - abajo * (lado @ abajo)) * 0.9
            hoja(out, (b + abajo * 8.0 - l * 0.1, b + abajo * 8.0 + l * 0.1, b + l, b - l), P['colmillo'], 1.8, 8.0,
                 semilla=27)
    # los ojos: el globo saltón, el ojo en hoja delante y la ceja en ceno encima
    for s in (-1, 1):
        Mo = Mh @ vr.T(s * 6.6, 11.6, 5.4)
        losa(out, Mo @ vr.Rx(math.pi / 2), -0.4, 2.4, 4.2, 3.0, pi, semilla=28)
        a, b, c, d = (pt(Mo, (-3.8, -2.6, 2.6)), pt(Mo, (3.8, -2.6, 2.6)), pt(Mo, (3.8, 2.6, 2.6)), pt(Mo, (-3.8, 2.6, 2.6)))
        lamina(out, (a, b, c, d), P['ojo_d' if s > 0 else 'ojo_i'], 7.6, 5.2, semilla=29)
        Mc = Mh @ vr.T(s * 6.8, 15.0, 6.6) @ vr.Rz(s * 0.32)
        bm.cubo(out, Mc, -5.4, -1.0, -2.6, 10.8, 2.6, 4.4, pi, semilla=30)                    # la ceja
        bm.cubo(out, Mc, (2.8 if s > 0 else -6.6), -0.4, -2.2, 3.8, 2.0, 3.6, pi, semilla=31)   # su rizo de fuera
    losa(out, Mh @ vr.T(0.0, 18.4, 7.0) @ vr.Rx(math.pi / 2), -0.6, 0.6, 1.8, 2.2, P['oro'], semilla=32)   # la gema
    losa(out, Mh @ vr.T(0.0, 18.4, 7.6) @ vr.Rx(math.pi / 2), -0.2, 0.4, 1.1, 1.4, P['gema'], semilla=33)


def marco(out, Mh, P, V):
    """Lo que enmarca la cara de cada tipo, y las orejas (en los Cuernos y en la Corona)."""
    if V['marco'] == 'melena':
        rng = random.Random(5)
        for i, a in enumerate(np.linspace(-125.0, 125.0, 19)):
            g = a * D
            raiz = pt(Mh, (math.sin(g) * 15.6, 6.0 + math.cos(g) * 14.0, -4.0))
            sale = Mh[:3, :3] @ _u(np.array((math.sin(g), math.cos(g), -0.25)))
            lado = Mh[:3, :3] @ np.array((math.cos(g), -math.sin(g), 0.0))
            largo = (16.0 if i % 2 == 0 else 12.0) * rng.uniform(0.9, 1.1)
            mechon(out, P['llama'], raiz, sale, lado, largo, 6.6, semilla=40 + i % 4)
        for s in (-1, 1):                                                                      # dos cuernos cortos
            b = pt(Mh, (s * 7.0, 21.0, 0.0))
            tubo(out, [b, b + np.array((s * 1.6, 3.6, -0.6)), b + np.array((s * 2.6, 6.4, -2.0))], [1.3, 0.9, 0.2],
                 P['cuerno'], semilla=44)
        return
    for s in (-1, 1):                                                                          # las orejas, con su disco
        Mo = Mh @ vr.T(s * 17.0, 11.0, -3.0) @ vr.Rz(-s * 0.25)
        bm.cubo(out, Mo, -1.0, -3.0, -3.0, 2.0, 9.0, 5.2, P['piel'], semilla=45)
        bm.cubo(out, Mo, -1.2, -8.0, -2.0, 2.4, 5.2, 3.4, P['piel'], semilla=46)
        losa(out, Mo @ vr.T(s * 1.4, -9.0, -0.4) @ vr.Rz(math.pi / 2), -0.6, 0.6, 3.2, 3.2, P['oro'], semilla=47)
    if V['marco'] == 'cuernos':
        for s in (-1, 1):                                                                      # los cuernos de carnero
            c = np.array((s * 18.4, 17.0, -3.0))
            pts, rs = [], []
            n = 22
            for j in range(n + 1):
                t = j / n
                phi = math.pi - t * 1.75 * math.pi
                R = 7.6 * (1 - 0.5 * t)
                pts.append(pt(Mh, c + np.array((s * R * math.cos(phi), R * math.sin(phi), 4.0 * t))))
                rs.append(2.8 * (1 - 0.72 * t))
            tubo(out, pts, rs, P['cuerno'], semilla=48)
        return
    # la Corona: la diadema, las cinco puntas y los colmillos de jabali
    losa(out, Mh @ vr.T(0.0, 0.0, -3.0), 19.0, 21.6, 10.6, 8.2, P['oro'], semilla=50)
    for i, a in enumerate(np.linspace(-56.0, 56.0, 5)):
        g = a * D
        raiz = pt(Mh, (math.sin(g) * 10.0, 20.6, -3.0 + math.cos(g) * 8.0))
        sube = Mh[:3, :3] @ _u(np.array((math.sin(g) * 0.3, 1.0, math.cos(g) * 0.12)))
        lado = Mh[:3, :3] @ np.array((math.cos(g), 0.0, -math.sin(g)))
        alto = 14.0 - abs(a) / 56.0 * 5.0
        mechon(out, P['punta_oro'], raiz, sube, lado, alto, 6.4, semilla=51 + i % 3)
    for s in (-1, 1):
        ps = [pt(Mh, p) for p in ((s * 8.6, -1.0, 7.0), (s * 10.0, -5.0, 9.0), (s * 12.6, -6.0, 10.4),
                                   (s * 14.6, -3.0, 11.0), (s * 15.0, 1.4, 10.4))]
        tubo(out, ps, [1.4, 1.3, 1.1, 0.8, 0.2], P['cuerno'], semilla=55)


def kalara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        Mh = vr.T(0.0, 25.0, 0.0) @ vr.Rx(12 * D)
        cara(out, Mh, P, V)
        marco(out, Mh, P, V)
        # la melena de detras, que cuelga hasta el suelo donde estaba el cuerpo
        rng = random.Random(9)
        for i, a in enumerate(np.linspace(-120.0, 120.0, 11)):
            g = a * D
            raiz = pt(Mh, (math.sin(g) * 13.0, 10.0 + math.cos(g) * 7.0, -11.0))
            d = np.array((math.sin(g) * 0.35, -1.0, -0.55))
            lado = _u(np.cross(d, (0.0, 0.0, 1.0)))
            mechon(out, P['mechon'], raiz, d, lado, rng.uniform(13.0, 19.0), rng.uniform(4.0, 5.4), semilla=60 + i % 4)
        # los brazos: salen de debajo de las mejillas y apoyan las manos delante, en el suelo
        for s in (-1, 1):
            hombro = pt(Mh, (s * 12.6, -8.0, -1.0))
            codo = np.array((s * 21.0, 10.0, 7.0))
            muneca = np.array((s * 17.0, 2.6, 18.0))
            tubo(out, [hombro, (hombro + codo) / 2 + np.array((s * 1.0, 0.0, 0.0)), codo], [3.4, 3.2, 2.8], P['piel'],
                 semilla=70)
            tubo(out, [codo, muneca], [2.8, 2.4], P['piel'], semilla=71)
            for t, r in ((0.85, 2.9), (0.75, 2.8)):                                           # las ajorcas de oro
                q = codo + (muneca - codo) * t
                tubo(out, [q, q + _u(muneca - codo) * 0.9], [r, r], P['oro'], semilla=72)
            tubo(out, [hombro + (codo - hombro) * 0.4, hombro + (codo - hombro) * 0.48], [3.7, 3.7], P['oro'], semilla=72)
            Mm = vr.T(*muneca)
            losa(out, Mm, -2.4, 1.2, 3.4, 3.2, P['piel'], semilla=73)                         # la mano
            for j, g in enumerate((-40.0, -14.0, 12.0, 38.0)):                               # los dedos y las garras
                d = np.array((math.sin(g * D + s * 0.15), 0.0, math.cos(g * D + s * 0.15)))
                a = muneca + d * 2.4 + np.array((0.0, -0.4, 0.0))
                b = a + d * 3.4 + np.array((0.0, 0.6, 0.0))
                c = b + d * 2.8 + np.array((0.0, -1.6, 0.0))
                tubo(out, [a, b, c], [0.9, 0.8, 0.7], P['piel'], semilla=74)
                tubo(out, [c, c + d * 1.6 + np.array((0.0, -0.6, 0.0)), c + d * 2.0 + np.array((0.0, -2.6, 0.0))],
                     [0.65, 0.45, 0.06], P['garra'], semilla=75)
            pul = muneca + np.array((-s * 2.6, -0.6, 1.4))                                    # el pulgar
            tubo(out, [pul, pul + np.array((-s * 2.0, 0.0, 2.2)), pul + np.array((-s * 2.6, -1.6, 3.6))], [0.85, 0.7, 0.1],
                 P['piel'], semilla=76)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E @ Mh, (0.0, -3.0, 4.0))
    return out, {'boca': boca, 'ojos': pt(E @ Mh, (0.0, 11.6, 9.0)),
                 'luces': [pt(E @ Mh, (0.0, -4.0, -2.0)), boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

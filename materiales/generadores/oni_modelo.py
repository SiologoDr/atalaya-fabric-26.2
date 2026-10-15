"""
El Oni y sus tipos (15-10-2026). Juan, al rechazar a Kalara: «no me gusto, se ve raro, no es intimidante, haz otro
boss». El Oni es el demonio de Japon: un gigante con cuernos, la boca de oreja a oreja con los colmillos de abajo hacia
arriba, la melena salvaje, el taparrabos de piel de tigre y el kanabo, el garrote de hierro con pinchos. Lo que manda
es que intimide: plantado con las piernas abiertas y las rodillas dobladas, echado hacia delante, el kanabo cruzado
por encima del hombro para aplastarte, la otra mano tendida hacia ti con las garras abiertas, y la cara rugiendo con
la boca encendida.

No es el Minotauro: la cabeza es una cara de demonio (no la de un toro), no tiene giba y la postura es de ataque.

Hecho desde cero: formas de ocho lados (losas y tubos), texturas limpias de cinco tonos, los dientes y la melena en
hoja.

Los tres tipos tienen la misma pose y cambian los cuernos, los ojos, la melena y el color:

    A  el Rojo (Aka-oni)    dos cuernos que se curvan hacia atras y la melena blanca; luz de oro
    B  el Azul (Ao-oni)     un solo cuerno enorme, un tercer ojo en la frente y la melena negra; luz cian
    C  el Negro (Kuro-oni)  una corona de cuatro cuernos y la melena roja; luz carmesi
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
ESCALA = 0.56
CABEZA = 1.5

VARIANTES = {
    'A': dict(
        clave='OA', nombre='el Rojo', corto='rojo', cuernos='dos', tercer_ojo=False,
        piel=_r('2a0806', '4a100c', '701c14', '962c1e', 'bc4430'),
        pelo=_r('8a8480', 'b4aea8', 'd6d0ca', 'eeeae4', 'fcfaf6'),
        cuerno=_r('3a3024', '6a5a44', '9c8a6a', 'c8b892', 'eee2c4'),
        neon=('fff8d8', 'ffcc1a', '6a4a04'),
    ),
    'B': dict(
        clave='OB', nombre='el Azul', corto='azul', cuernos='uno', tercer_ojo=True,
        piel=_r('060c22', '0c1a3c', '16285a', '22407e', '345ca4'),
        pelo=_r('050508', '0c0c12', '16161e', '22222c', '32323e'),
        cuerno=_r('3a3024', '6a5a44', '9c8a6a', 'c8b892', 'eee2c4'),
        neon=('e8ffff', '3ae8ff', '04466a'),
    ),
    'C': dict(
        clave='OC', nombre='el Negro', corto='negro', cuernos='cuatro', tercer_ojo=False,
        piel=_r('08080a', '121216', '1c1c22', '282830', '363642'),
        pelo=_r('3a0606', '640c0c', '941616', 'c02222', 'e84438'),
        cuerno=_r('1a1612', '2e2820', '463c30', '625444', '82725c'),
        neon=('ffe6ea', 'ff2a46', '6a0414'),
    ),
}

HIERRO = _r('0c0e10', '181c20', '262c32', '384048', '505a64')
TIGRE = _r('5a2a06', '8a440c', 'b86414', 'e08a24', 'f6b04a')
NEGRO = (14, 10, 8, 255)
CUERDA = _r('3a2c18', '5a462a', '7e663e', 'a48a58', 'c8b07a')
PAPEL = _r('a8a49a', 'cac6bc', 'e4e0d6', 'f4f0e8', 'fffcf6')
MADERA = _r('1a0e08', '2e1a0e', '462816', '603820', '7c4c2c')
DIENTE = _r('6a6452', 'a09a7e', 'cac4a6', 'e6e0c4', 'fbf8e6')
GARRA = _r('0a0808', '161212', '241e1c', '36302a', '4c443c')
ORO = _r('5a3a08', '8a5c10', 'c08a1e', 'e8b83a', 'fae27a')


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
    OSCURO = (10, 4, 4, 255)

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'oni%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def piel(tw, th, cara, s):
        """La piel: lisa, con vetas finas y largas como curvas de nivel, mas clara arriba y mas oscura abajo."""
        v = bm._ruido(tw, th, s, 20.0)
        idx = np.where(((v * 4.0) % 1.0) < 0.08, 1, 2)
        idx = _limpiar(idx)
        if cara == 'arriba':
            idx = idx + 1
        elif cara == 'abajo':
            idx = idx - 1
        return _imagen(_bisel(np.clip(idx, 0, 4), 1, 1), V['piel']), None
    reg('piel', piel)

    def musculo(tw, th, cara, s):
        """El pecho y el vientre por delante: la piel con la raya del medio y las bandas del vientre marcadas."""
        img, _ = piel(tw, th, cara, s)
        ys, xs = np.mgrid[0:th, 0:tw]
        raya = abs(xs + 0.5 - tw / 2) < 0.6
        banda = (ys % 7 == 6) & (abs(xs + 0.5 - tw / 2) < tw * 0.3)
        som = _imagen(np.full((th, tw), 1), V['piel'])
        return np.where((raya | banda)[..., None], som, img), None
    reg('musculo', musculo)

    def tigre(tw, th, cara, s):
        """La piel de tigre del taparrabos: ocre con las rayas negras, onduladas y limpias."""
        ys, xs = np.mgrid[0:th, 0:tw]
        onda = np.sin(xs / max(tw, 1) * TAU * 1.5 + s) * 1.5
        raya = ((ys + onda) % 7) < 1.6
        img = _imagen(_bisel(np.full((th, tw), 3), 1, 1), TIGRE)
        img[raya] = NEGRO
        return img, None
    reg('tigre', tigre)

    def taparrabo(tw, th, cara, s):
        """El faldon de piel de tigre, en hoja: con las rayas y el canto de abajo en picos."""
        img, _ = tigre(tw, th, cara, s)
        ys, xs = np.mgrid[0:th, 0:tw]
        pico = th - 1 - (abs((xs % 6) - 3) * 1.4)
        img[..., 3] = np.where(ys < pico, 255, 0)
        return img, None
    reg('taparrabo', taparrabo)

    def cuerda(tw, th, cara, s):
        """La cuerda sagrada (shimenawa): torcida, en bandas en diagonal con su sombra."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a, t = (xs, ys) if tw >= th else (ys, xs)
        f = (a + t) % 6
        idx = np.where(f == 0, 1, np.where(f < 3, 3, 2))
        return _imagen(idx, CUERDA), None
    reg('cuerda', cuerda)

    def shide(tw, th, cara, s):
        """El papel en zigzag que cuelga de la cuerda (shide), en hoja."""
        ys, xs = np.mgrid[0:th, 0:tw]
        tramo = th // 4 if th >= 8 else 2
        paso = (ys // max(tramo, 1)) % 2
        izq = np.where(paso == 0, 0, tw // 3)
        dentro = (xs >= izq) & (xs < izq + tw * 2 // 3)
        img = _imagen(np.where(xs == izq, 4, 3), PAPEL)
        img[..., 3] = np.where(dentro, 255, 0)
        return img, None
    reg('shide', shide)

    def hierro(tw, th, cara, s):
        """El hierro del kanabo y de los brazales: oscuro, con el bisel y una banda clara."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        return _imagen(_bisel(idx, 1, 1), HIERRO), None
    reg('hierro', hierro)

    def madera(tw, th, cara, s):
        """El puno del kanabo: madera envuelta en tiras de cuero en diagonal."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a, t = (xs, ys) if tw >= th else (ys, xs)
        idx = np.where((a + t) % 5 == 0, 1, 2)
        return _imagen(idx, MADERA), None
    reg('madera', madera)

    def cuenta(tw, th, cara, s):
        return _imagen(_bisel(np.full((th, tw), 2), 1, 1), MADERA), None
    reg('cuenta', cuenta)

    def oro(tw, th, cara, s):
        return _imagen(_bisel(np.full((th, tw), 3), 1, 1), ORO), None
    reg('oro', oro)

    def mechon(tw, th, cara, s):
        """Un mechon de la melena, en hoja: ancho en la raiz y en punta, con las hebras y una veta de brillo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = 1 - (ys + 0.5) / th                                           # 0 en la raiz (abajo), 1 en la punta
        dentro = abs((xs + 0.5) / tw - 0.5) < 0.5 * (1 - f ** 1.8) + 0.04
        idx = np.where(xs % 3 == 0, 1, 2)
        idx = np.where(abs((xs + 0.5) / tw - 0.36) < 0.08, 3, idx)
        img = _imagen(idx, V['pelo'])
        img[..., 3] = np.where(dentro, 255, 0)
        return img, None
    reg('mechon', mechon)

    def pelo(tw, th, cara, s):
        """El pelo de los mechones en tubo: hebras a lo largo, con una veta de brillo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a, t = (xs, ys) if cara in ('der', 'izq') else (ys, xs)
        idx = np.where(t % 3 == 0, 1, 2)
        idx = np.where((t % 7 == 2) & (a % 9 > 2), 3, idx)
        if cara == 'arriba':
            idx = idx + 1
        return _imagen(_bisel(np.clip(idx, 0, 4), 1, 1), V['pelo']), None
    reg('pelo', pelo)

    def cuerno(tw, th, cara, s):
        """El cuerno: anillado, oscuro en la raiz y claro hacia la punta (los tubos van de la raiz a la punta)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a = xs if cara in ('der', 'izq') else ys
        idx = np.where(a % 4 == 0, 2, 3)
        return _imagen(_bisel(idx, 1, 1), V['cuerno']), None
    reg('cuerno', cuerno)

    def garra(tw, th, cara, s):
        return _imagen(_bisel(np.full((th, tw), 2), 1, 1), GARRA), None
    reg('garra', garra)

    def colmillo(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        a = xs if cara in ('der', 'izq') else ys
        idx = np.where(a % 5 == 0, 2, 3)
        return _imagen(_bisel(idx, 1, 1), DIENTE), None
    reg('colmillo', colmillo)

    def dientes(base_arriba):
        def f(tw, th, cara, s):
            """Los dientes, en hoja: anchos, en punta roma, apretados, con la cara de la luz mas clara."""
            ys, xs = np.mgrid[0:th, 0:tw]
            t = np.zeros((th, tw, 4), np.uint8)
            paso = 5
            x = xs % paso
            fila = ys if base_arriba else th - 1 - ys
            punta = (fila > th * 0.6) & ((x == 0) | (x == paso - 2))
            diente = (x < paso - 1) & ~punta
            t[diente] = (*DIENTE[3], 255)
            t[diente & (x >= 2)] = (*DIENTE[2], 255)
            t[diente & (fila == 0)] = (*DIENTE[1], 255)
            return t, None
        return f
    reg('dientes_arriba', dientes(True))
    reg('dientes_abajo', dientes(False))

    def paladar(tw, th, cara, s):
        """El cielo y el suelo de la boca: escalones de luz, del borde (oscuro) al fondo (blanco)."""
        t = _degradado(th, tw, True, V['neon'][0], V['neon'][1], V['neon'][2])
        luz = t[..., :3].sum(axis=2) > 200
        return t, _emis(t, luz, 220)
    reg('paladar', paladar)

    def boca_suelo(tw, th, cara, s):
        """El suelo de la boca (la cara de arriba de la quijada): oscuro delante y encendido hacia la garganta."""
        t = _degradado(th, tw, False, V['neon'][0], V['neon'][1], V['neon'][2])
        luz = t[..., :3].sum(axis=2) > 200
        return t, _emis(t, luz, 220)
    reg('boca_suelo', boca_suelo)

    def garganta(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        d = np.hypot((xs - (tw - 1) / 2) / max(tw / 2, 1), (ys - (th - 1) / 2) / max(th / 2, 1))
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[2], 255)
        t[d < 0.8] = (*neo[1], 255)
        t[d < 0.4] = (*neo[0], 255)
        return t, None
    reg('garganta', garganta, pleno=True)

    def ojo(lado):
        def f(tw, th, cara, s):
            """El ojo, en hoja: rasgado, con el parpado en ceno (la esquina de dentro mas baja), todo encendido, y la
            pupila rasgada."""
            ys, xs = np.mgrid[0:th, 0:tw]
            u = (xs + 0.5) / tw * 2 - 1
            v = (ys + 0.5) / th * 2 - 1
            almendra = abs(v) < 0.95 * np.clip(1 - u * u, 0, 1) ** 0.5
            ceno = v < -0.2 + lado * u * 0.7
            dentro = almendra & ~ceno
            t = np.zeros((th, tw, 4), np.uint8)
            t[almendra] = OSCURO
            t[dentro] = (*neo[1], 255)
            t[dentro & (np.hypot(u, v - 0.15) < 0.4)] = (*neo[0], 255)
            pupila = dentro & (abs(u) < 0.09) & (abs(v - 0.15) < 0.55)
            t[pupila] = OSCURO
            return t, _emis(t, dentro & ~pupila, 255)
        return f
    reg('ojo_d', ojo(-1))
    reg('ojo_i', ojo(1))
    reg('ojo_m', ojo(0))

    def nariz(tw, th, cara, s):
        img, _ = piel(tw, th, cara, s)
        ys, xs = np.mgrid[0:th, 0:tw]
        for cx in (0.3, 0.7):
            u, v = (xs + 0.5 - cx * tw) / (0.13 * tw), (ys + 0.5 - 0.8 * th) / (0.1 * th)
            img[np.maximum(abs(u), abs(v)) * 0.4 + np.hypot(u, v) * 0.6 < 1.0] = OSCURO
        return img, None
    reg('nariz', nariz)
    return P


# ----------------------------------------------------------------------
#  Formas
# ----------------------------------------------------------------------
def losa(out, M, y0, y1, rx, rz, pin, caras=None, k=0.72, semilla=0):
    """Una losa de ocho lados en planta (dos cajas cruzadas)."""
    bm.cubo(out, M, -rx, y0, -rz * k, 2 * rx, y1 - y0, 2 * rz * k, pin, caras=caras, semilla=semilla)
    bm.cubo(out, M, -rx * k, y0, -rz, 2 * rx * k, y1 - y0, 2 * rz, pin, caras=caras, semilla=semilla + 1)


def tubo(out, pts, radios, pin, caras=None, semilla=0, arriba=(0.0, 1.0, 0.0), achata=1.0):
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
            bm.cubo(out, M, -r * kx, -r * ky * achata, -r * 0.3, 2 * r * kx, 2 * r * ky * achata, L + r * 0.6, pin,
                    caras=caras, semilla=semilla + j % 3)


def hoja(out, P4, pintor, ancho, alto, semilla=0):
    """Una lamina que se ve por las dos caras (p0 abajo-izq, p1 abajo-der, p2 arriba-der, p3 arriba-izq)."""
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def mechon(out, pintor, raiz, dirl, lado, largo, ancho, semilla=0, curva=None):
    """Un mechon en hoja desde la raiz hacia 'dirl'; con 'curva', en dos tramos que se doblan hacia alli."""
    raiz, d, l = np.asarray(raiz, float), _u(dirl), _u(lado) * ancho / 2
    if curva is None:
        hoja(out, (raiz - l, raiz + l, raiz + l + d * largo, raiz - l + d * largo), pintor, ancho, largo, semilla)
        return
    m = raiz + d * largo * 0.55
    d2 = _u(d + _u(curva) * 0.8)
    f = m + d2 * largo * 0.5
    hoja(out, (raiz - l, raiz + l, m + l * 0.75, m - l * 0.75), pintor, ancho, largo * 0.55, semilla)
    hoja(out, (m - l * 0.75, m + l * 0.75, f + l * 0.05, f - l * 0.05), pintor, ancho * 0.75, largo * 0.5, semilla + 1)


def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    """Una fila de dientes por los puntos (x, z) a la altura y: baja si alto < 0 y sube si alto > 0."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado = float(np.linalg.norm(B - A))
        if alto < 0:
            hoja(out, (A2, B2, B, A), pintor, lado, abs(alto), semilla + j)
        else:
            hoja(out, (A, B, B2, A2), pintor, lado, abs(alto), semilla + j)


# ======================================================================
#  LA CABEZA
# ======================================================================
def cabeza(out, Mh, P, V):
    """La cara del Oni, mirando a +z, con la comisura en y=0: el craneo ancho, la ceja de hueso en ceno sobre los ojos
    rasgados que arden, los pomulos, la nariz ancha y chata, la boca de oreja a oreja abierta (la quijada cae) con los
    dientes de arriba y de abajo, los dos colmillos de abajo que suben por fuera, el paladar y el suelo de la boca
    encendidos y la garganta al fondo; las orejas en punta con su aro de oro."""
    pi = P['piel']
    losa(out, Mh @ vr.T(0.0, 0.0, -1.0), 2.0, 11.0, 7.6, 7.0, pi, caras={'abajo': P['paladar']}, semilla=10)   # el craneo
    losa(out, Mh @ vr.T(0.0, 0.0, -1.6), 11.0, 13.6, 6.2, 5.8, pi, semilla=11)
    losa(out, Mh @ vr.T(0.0, 0.0, -2.0), 13.6, 14.8, 4.2, 4.0, pi, semilla=12)
    bm.cubo(out, Mh, -6.6, 0.0, -3.0, 13.2, 2.4, 9.6, pi, caras={'abajo': P['paladar']}, semilla=13)          # la boca de arriba
    bm.cubo(out, Mh, -2.4, 2.4, 5.4, 4.8, 3.2, 3.0, pi, caras={'frente': P['nariz']}, semilla=14)               # la nariz
    bm.cubo(out, Mh, -1.3, 5.2, 5.2, 2.6, 3.4, 2.4, pi, semilla=15)                                            # el puente
    for s in (-1, 1):
        bm.cubo(out, Mh, (3.8 if s > 0 else -6.8), 3.4, 3.4, 3.0, 2.6, 3.0, pi, semilla=16)                     # los pomulos
        Mc = Mh @ vr.T(s * 3.6, 8.6, 6.6) @ vr.Rz(s * 0.36)                                                      # la ceja
        bm.cubo(out, Mc, -3.8, -0.8, -2.0, 7.6, 2.2, 3.2, pi, semilla=17)
        Mo = Mh @ vr.T(s * 3.5, 6.5, 7.5)                                                                          # el ojo
        a, b, c, d = pt(Mo, (-2.7, -1.5, 0.0)), pt(Mo, (2.7, -1.5, 0.0)), pt(Mo, (2.7, 1.5, 0.0)), pt(Mo, (-2.7, 1.5, 0.0))
        lamina(out, (a, b, c, d), P['ojo_d' if s > 0 else 'ojo_i'], 5.4, 3.0, semilla=18)
        bm.cubo(out, Mh, (1.1 if s > 0 else -6.1), 4.6, 4.0, 5.0, 4.0, 3.4, pi, semilla=18)                     # la cuenca
        Mr = Mh @ vr.T(s * 7.6, 6.4, -1.0) @ vr.Rz(-s * 0.35)                                                     # la oreja
        bm.cubo(out, Mr, -0.6, -2.4, -1.6, 1.2, 6.6, 3.2, pi, semilla=19)
        bm.cubo(out, Mr, -0.5, 4.0, -1.2, 1.0, 2.4, 1.8, pi, semilla=19)
        losa(out, Mr @ vr.T(s * 0.4, -3.6, 0.0) @ vr.Rz(math.pi / 2), -0.4, 0.4, 1.6, 1.6, P['oro'], semilla=20)
    if V['tercer_ojo']:
        Mo = Mh @ vr.T(0.0, 11.0, 6.6)
        a, b, c, d = pt(Mo, (-1.0, -1.8, 0.0)), pt(Mo, (1.0, -1.8, 0.0)), pt(Mo, (1.0, 1.8, 0.0)), pt(Mo, (-1.0, 1.8, 0.0))
        lamina(out, (a, b, c, d), P['ojo_m'], 2.0, 3.6, semilla=21)
    hilera(out, Mh, [(-6.0, 1.0), (-6.0, 5.0), (-4.4, 6.5), (4.4, 6.5), (6.0, 5.0), (6.0, 1.0)], 0.1, -1.8, P['dientes_arriba'],
           semilla=22)
    bm.cubo(out, Mh, -5.4, -7.0, -3.4, 10.8, 7.4, 0.8, P['piel'], caras={'frente': P['garganta']}, semilla=23)
    Mj = Mh @ vr.T(0.0, 0.6, -3.0) @ vr.Rx(0.42)                                                                  # la quijada
    bm.cubo(out, Mj, -6.4, -3.4, 0.0, 12.8, 3.4, 9.6, pi, caras={'arriba': P['boca_suelo']}, semilla=24)
    bm.cubo(out, Mj, -5.0, -4.4, 2.0, 10.0, 1.4, 7.4, pi, semilla=25)                                            # la barbilla
    hilera(out, Mj, [(-5.8, 2.0), (-5.8, 7.6), (-4.2, 9.4), (4.2, 9.4), (5.8, 7.6), (5.8, 2.0)], 0.0, 1.6, P['dientes_abajo'],
           semilla=26)
    for s in (-1, 1):                                                                                             # los colmillos
        b = pt(Mj, (s * 4.8, 0.2, 8.6))
        tubo(out, [b, b + Mh[:3, :3] @ np.array((s * 0.7, 3.8, 0.8)), b + Mh[:3, :3] @ np.array((s * 1.8, 7.4, -0.2))],
             [1.3, 1.0, 0.16], P['colmillo'], semilla=27)


def cuernos(out, Mh, P, V):
    """Los cuernos de cada tipo: dos que se curvan hacia atras, uno enorme en medio, o una corona de cuatro."""
    if V['cuernos'] == 'dos':
        for s in (-1, 1):
            b = pt(Mh, (s * 4.2, 12.6, 2.6))
            ps = [b, pt(Mh, (s * 6.0, 16.4, 2.0)), pt(Mh, (s * 7.4, 19.6, -0.6)), pt(Mh, (s * 7.8, 21.6, -4.2)),
                  pt(Mh, (s * 7.2, 21.8, -7.4))]
            tubo(out, ps, [1.5, 1.25, 0.95, 0.6, 0.12], P['cuerno'], semilla=30)
    elif V['cuernos'] == 'uno':
        b = pt(Mh, (0.0, 13.2, 3.2))
        ps = [b, pt(Mh, (0.0, 17.0, 4.0)), pt(Mh, (0.0, 21.0, 3.0)), pt(Mh, (0.0, 24.0, 0.6)), pt(Mh, (0.0, 25.4, -2.6))]
        tubo(out, ps, [2.2, 1.8, 1.3, 0.7, 0.14], P['cuerno'], semilla=30)
    else:
        for s in (-1, 1):
            b = pt(Mh, (s * 3.0, 13.4, 2.8))
            ps = [b, pt(Mh, (s * 3.6, 17.6, 3.4)), pt(Mh, (s * 3.4, 21.0, 2.2)), pt(Mh, (s * 2.2, 22.6, 0.4))]
            tubo(out, ps, [1.4, 1.1, 0.7, 0.12], P['cuerno'], semilla=30)
            b = pt(Mh, (s * 6.0, 11.4, 1.6))
            ps = [b, pt(Mh, (s * 9.0, 14.2, 1.6)), pt(Mh, (s * 11.0, 17.6, 0.6)), pt(Mh, (s * 11.4, 20.0, -1.0))]
            tubo(out, ps, [1.2, 0.95, 0.6, 0.1], P['cuerno'], semilla=31)


def melena(out, Mh, P, V):
    """La melena salvaje: mechones gruesos que salen de la coronilla y de la nuca y se echan hacia atras y hacia
    arriba, como por el viento, doblandose en la punta; y los que caen por los lados de la cara."""
    rng = random.Random(4)
    R = Mh[:3, :3] / CABEZA
    for i, a in enumerate(np.linspace(-140.0, 140.0, 15)):
        g = a * D
        p = pt(Mh, (math.sin(g) * 6.0, 11.4 + math.cos(g) * 2.0, -1.4 - abs(math.cos(g)) * 1.4))
        d = R @ _u(np.array((math.sin(g) * 0.8, 0.75 + math.cos(g) * 0.2, -0.85)))
        L = rng.uniform(20.0, 28.0)
        pts, rs = [p], [rng.uniform(2.0, 2.6)]
        for k in range(3):
            d = _u(d + R @ np.array((math.sin(g) * 0.2, -0.38, -0.3)))
            p = p + d * L * (0.4, 0.34, 0.26)[k]
            pts.append(p)
            rs.append(rs[0] * (0.82, 0.55, 0.12)[k])
        tubo(out, pts, rs, P['pelo'], semilla=40 + i % 3)
    for s in (-1, 1):
        for j, z in enumerate((-3.6, -0.6)):
            p = pt(Mh, (s * 7.0, 10.0, z))
            pts = [p, p + R @ np.array((s * 2.6, -6.0, -1.0)), p + R @ np.array((s * 4.4, -13.0, -2.6)),
                   p + R @ np.array((s * 5.0, -18.0, -5.0))]
            tubo(out, pts, [2.0, 1.7, 1.1, 0.2], P['pelo'], semilla=44 + j)


# ======================================================================
#  EL ONI
# ======================================================================
TRONCO = [  # (y0, y1, rx, rz): la cadera, la cintura, el vientre, el pecho y el cuello de toro
    (22.0, 26.0, 8.6, 6.4), (26.0, 30.0, 8.2, 6.0), (30.0, 34.0, 9.4, 6.6), (34.0, 39.0, 11.4, 7.6),
    (39.0, 43.0, 12.4, 8.0), (43.0, 46.0, 10.6, 7.0), (46.0, 49.0, 6.0, 5.2)]


def oni(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    pi = P['piel']
    try:
        # ---- las piernas: abiertas, las rodillas dobladas hacia fuera
        for s, dz in ((-1, -1.0), (1, 1.6)):
            cad = np.array((s * 5.6, 23.0, 0.0))
            rod = np.array((s * 11.6, 13.0, dz + 4.0))
            tob = np.array((s * 12.6, 3.4, dz))
            tubo(out, [cad, (cad + rod) / 2 + np.array((s * 0.8, 0.6, 0.0)), rod], [5.2, 5.0, 3.8], pi, semilla=1)
            tubo(out, [rod, (rod + tob) / 2 + np.array((0.0, 0.0, -0.8)), tob], [3.8, 3.6, 2.6], pi, semilla=2)
            losa(out, vr.T(*tob) @ vr.Rx(math.pi), -0.8, 0.8, 3.2, 3.2, P['hierro'], semilla=3)          # el grillete del tobillo
            Mp = vr.T(tob[0], 0.0, tob[2]) @ vr.Ry(s * 0.25)                                            # el pie
            losa(out, Mp, 0.0, 3.6, 3.4, 4.0, pi, semilla=4)
            losa(out, Mp @ vr.T(0.0, 0.0, 3.6), 0.0, 2.4, 3.6, 2.6, pi, semilla=5)
            for x in (-2.4, 0.0, 2.4):
                tubo(out, [pt(Mp, (x, 1.2, 5.4)), pt(Mp, (x, 0.8, 7.0)), pt(Mp, (x, 0.0, 7.8))], [0.8, 0.5, 0.1], P['garra'],
                     semilla=6)
        # ---- el tronco, echado hacia delante
        Mt = vr.T(0.0, 22.0, 0.0) @ vr.Rx(14 * D) @ vr.T(0.0, -22.0, 0.0)
        for i, (y0, y1, rx, rz) in enumerate(TRONCO):
            losa(out, Mt, y0, y1, rx, rz, pi, semilla=10 + i)
        for s in (-1, 1):                                                                       # los pectorales
            bm.cubo(out, Mt @ vr.T(s * 5.6, 39.6, 7.4) @ vr.Ry(s * 0.2), -5.4, -4.0, 0.0, 10.8, 7.6, 1.4, pi,
                    caras={'frente': P['musculo']}, semilla=17)
        bm.cubo(out, Mt, -5.4, 27.0, 6.0, 10.8, 8.0, 0.9, pi, caras={'frente': P['musculo']}, semilla=18)   # el vientre
        for s in (-1, 1):                                                                       # los hombros
            losa(out, Mt @ vr.T(s * 12.6, 0.0, 0.6), 40.0, 47.4, 5.2, 5.6, pi, semilla=19)
        # ---- el taparrabos de tigre, la cuerda sagrada y sus papeles
        losa(out, Mt, 20.0, 26.0, 9.0, 6.8, P['tigre'], semilla=20)
        for z, sg in ((7.2, 1), (-7.2, -1)):
            a0, a1 = pt(Mt, (-6.0, 22.0, z)), pt(Mt, (6.0, 22.0, z))
            b0, b1 = a0 + np.array((0.0, -10.0, sg * 2.4)), a1 + np.array((0.0, -10.0, sg * 2.4))
            hoja(out, (b0, b1, a1, a0), P['taparrabo'], 12.0, 10.0, semilla=21)
        losa(out, Mt, 25.4, 27.6, 9.6, 7.2, P['cuerda'], semilla=22)
        for i, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
            a = pt(Mt, (x, 25.6, 7.4))
            hoja(out, (a + np.array((-1.0, -6.0, 0.6)), a + np.array((1.0, -6.0, 0.6)), a + np.array((1.0, 0.0, 0.0)),
                       a + np.array((-1.0, 0.0, 0.0))), P['shide'], 2.0, 6.0, semilla=23 + i)
        # ---- el collar de cuentas
        for i, g in enumerate(np.linspace(-70.0, 70.0, 11)):
            a = g * D
            c = pt(Mt, (math.sin(a) * 8.2, 44.0 - math.cos(a) * 5.0, 5.4 + math.cos(a) * 2.6))
            losa(out, vr.T(*c), -1.2, 1.2, 1.3, 1.3, P['cuenta'], semilla=24)
        # ---- los brazos: el derecho (-x) cruza el kanabo por encima del hombro; el izquierdo se tiende hacia ti
        brazos = ((pt(Mt, (-13.2, 44.6, 0.6)), np.array((-23.0, 50.0, 1.0)), np.array((-21.0, 59.0, 4.0))),
                  (pt(Mt, (13.2, 44.6, 0.6)), np.array((21.0, 37.0, 9.0)), np.array((20.0, 35.0, 19.0))))
        for k, (ho, co, mu) in enumerate(brazos):
            tubo(out, [ho, (ho + co) / 2 + _u(co - ho) * 0.0 + np.array((0.0, 0.8, 0.0)), co], [4.4, 4.6, 3.6], pi, semilla=30)
            tubo(out, [co, (co + mu) / 2, mu], [3.6, 3.4, 2.8], pi, semilla=31)
            d = _u(mu - co)
            L = float(np.linalg.norm(mu - co))
            tubo(out, [co + d * L * 0.55, mu - d * 0.3], [3.6, 3.2], P['hierro'], semilla=32)        # el brazal
        mano_cerrada(out, P, brazos[0][2], _u(brazos[0][2] - brazos[0][1]))
        mano_abierta(out, P, brazos[1][2], _u(brazos[1][2] - brazos[1][1]))
        kanabo(out, P, brazos[0][2] + _u(brazos[0][2] - brazos[0][1]) * 2.6, _u(np.array((-0.3, 0.92, -0.22))))
        # ---- la cabeza
        Mh = Mt @ vr.T(0.0, 47.0, 4.6) @ vr.Rx(-8 * D) @ np.diag([CABEZA] * 3 + [1.0])
        bm.PPB = PPB / CABEZA
        cabeza(out, Mh, P, V)
        cuernos(out, Mh, P, V)
        melena(out, Mh, P, V)
        bm.PPB = PPB
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E @ Mh, (0.0, -1.0, 3.0))
    return out, {'boca': boca, 'ojos': pt(E @ Mh, (0.0, 6.4, 7.0)),
                 'luces': [pt(E @ Mh, (0.0, -1.0, 1.0)), pt(E @ Mh, (0.0, 6.4, 10.0))]}


def mano_cerrada(out, P, muneca, d):
    """La mano que agarra el puno del kanabo."""
    losa(out, em.marco(muneca, d, up=(0.0, 0.0, 1.0)) @ vr.Rx(math.pi / 2), 0.0, 4.2, 2.8, 2.4, P['piel'], semilla=40)


def mano_abierta(out, P, muneca, d):
    """La mano tendida hacia ti: la palma y cinco dedos abiertos en abanico, con las garras."""
    lado = _u(np.cross((0.0, 1.0, 0.0), d))
    arriba = np.cross(d, lado)
    losa(out, em.marco(muneca, d, up=arriba) @ vr.Rx(math.pi / 2), 0.0, 4.6, 3.0, 1.6, P['piel'], semilla=41)
    base = muneca + d * 4.2
    for j, g in enumerate((-46.0, -18.0, 4.0, 26.0)):
        dd = _u(d * math.cos(g * D) + lado * math.sin(g * D) + arriba * 0.15)
        a = base + lado * (j - 1.5) * 1.3
        b = a + dd * 3.6 + arriba * 0.4
        c = b + dd * 2.8 - arriba * 0.6
        tubo(out, [a, b, c], [0.95, 0.85, 0.75], P['piel'], semilla=42)
        tubo(out, [c, c + dd * 1.6 - arriba * 0.6, c + dd * 2.2 - arriba * 2.0], [0.7, 0.5, 0.08], P['garra'], semilla=43)
    pul = muneca + d * 2.0 - lado * 2.4
    tubo(out, [pul, pul - lado * 2.4 + d * 1.6, pul - lado * 3.4 + d * 3.6], [0.95, 0.8, 0.7], P['piel'], semilla=44)
    c = pul - lado * 3.4 + d * 3.6
    tubo(out, [c, c + d * 1.4 - arriba * 1.2], [0.6, 0.08], P['garra'], semilla=45)


def kanabo(out, P, mano, d):
    """El kanabo: el garrote de hierro, cruzado por encima del hombro hacia atras, que engorda hacia la punta, con las
    bandas y los pinchos en filas; el puno, envuelto en cuero, y el pomo."""
    lado = _u(np.cross(d, (0.0, 0.0, 1.0)))
    tubo(out, [mano - d * 5.0, mano + d * 4.0], [1.3, 1.3], P['madera'], semilla=50, arriba=(0.0, 0.0, 1.0))
    losa(out, em.marco(mano - d * 6.4, d, up=(0.0, 0.0, 1.0)) @ vr.Rx(math.pi / 2), 0.0, 1.6, 2.0, 2.0, P['hierro'], semilla=51)
    L = 30.0
    pts = [mano + d * (4.0 + L * t) for t in (0.0, 0.3, 0.65, 1.0)]
    tubo(out, pts, [1.6, 2.6, 3.4, 3.6], P['hierro'], semilla=52)
    for t in (0.0, 0.32, 0.66, 0.98):                                                    # las bandas
        q = mano + d * (4.0 + L * t)
        tubo(out, [q - d * 0.5, q + d * 0.5], [2.0 + 2.0 * t, 2.0 + 2.0 * t], P['hierro'], semilla=53)
    for i in range(6):                                                                     # los pinchos, en filas
        t = 0.38 + i * 0.11
        q = mano + d * (4.0 + L * t)
        r = 2.8 + 0.9 * min(1.0, t)
        for j in range(6):
            g = TAU * j / 6 + (i % 2) * TAU / 12
            n = _u(lado * math.cos(g) + np.cross(lado, d) * math.sin(g))
            tubo(out, [q + n * (r - 0.4), q + n * (r + 1.6)], [0.75, 0.08], P['hierro'], semilla=54)
    punta = mano + d * (4.0 + L)
    losa(out, em.marco(punta, d, up=(0.0, 0.0, 1.0)) @ vr.Rx(math.pi / 2), 0.0, 1.4, 3.0, 3.0, P['hierro'], semilla=55)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

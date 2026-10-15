"""
El Ciclope y sus tipos (15-10-2026). Juan, tras Bravara: «me gusto el diseno, los colores, pero no es lo que busco yo
personalmente... seguimos con otros boss y sus tipos»; y al preguntarle por cual tirar: «tu eliges». Se vuelve al
bestiario griego (la Gorgona, el Minotauro y Cerbero gustaron) con lo aprendido de Sedara y Bravara: cabeza propia,
color propio y escena propia, nada del formato de antes.

El Ciclope: un gigante de un solo ojo, de pie, que alza una roca enorme con los dos brazos por encima de la cabeza para
lanzarla, como Polifemo contra el barco de Ulises. Lo que manda es la cabeza: el ojo enorme, encendido como una fragua,
bajo una ceja de hueso que le da el ceno; sin nariz de hombre (dos ranuras), la boca abierta de oreja a oreja con dientes
gordos y dos colmillos que suben; la barba y la melena, salvajes, le enmarcan la cara, y los brazos alzados con la roca,
la cabeza entera. No es el Minotauro: ni cabeza de toro ni giba, sino erguido, con los brazos arriba.

Los tres tipos tienen la misma pose (la roca en alto) y cambian la cabeza, lo que lleva encima y el color:

    A  Polifemo, el Pastor     melena y barba negras y rizadas, piel de oveja en los hombros; ojo de ambar
    B  Brontes, el del Trueno  calvo, con un cuerno en la frente y la barba en trenzas con anillos de hierro, mandil de
                               cuero y brazales; ojo de hierro fundido
    C  Arges, el del Rayo      el pelo y la barba blancos y de punta, la piel gris surcada de cicatrices de rayo que
                               brillan; ojo blanco azulado
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
        clave='CA', nombre='Polifemo, el Pastor', corto='polifemo', pelo='rizos', encima='vellon',
        piel=_r('3a2216', '5e3a26', '845838', 'a8784e', 'c89a6a'),
        pelo_c=_r('08060a', '141018', '201a24', '2e2632', '403644'),
        ropa=_r('8a8270', 'b2aa96', 'd6cfba', 'ece6d4', 'faf6ea'),
        neon=('fff0c4', 'ffa81a', '6a3404'),
        cicatriz=None,
    ),
    'B': dict(
        clave='CB', nombre='Brontes, el del Trueno', corto='brontes', pelo='trenzas', encima='mandil',
        piel=_r('2a1a12', '48301e', '6a4628', '8e6236', 'b0804a'),
        pelo_c=_r('1a0e08', '30180c', '4a2412', '64321a', '824424'),
        ropa=_r('1a120c', '2c1e14', '42301e', '5a422a', '74583a'),
        neon=('fff0d8', 'ff5a1a', '6a1404'),
        cicatriz=None,
    ),
    'C': dict(
        clave='CC', nombre='Arges, el del Rayo', corto='arges', pelo='punta', encima='nada',
        piel=_r('1e2228', '30363e', '464e58', '5e6874', '7a8692'),
        pelo_c=_r('8a92a0', 'b2bac6', 'd4dae2', 'eaeef4', 'fafcff'),
        ropa=_r('121418', '1e2228', '2c3038', '3c424c', '505864'),
        neon=('f0faff', '6ad8ff', '0a3a6a'),
        cicatriz=True,
    ),
}


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


# ----------------------------------------------------------------------
#  Los pintores, todos propios
# ----------------------------------------------------------------------
def _rayos(tw, th, s):
    """Cicatrices de rayo (figuras de Lichtenberg): ramas que se abren desde arriba, de un pixel."""
    rng = random.Random(s)
    m = np.zeros((th, tw), bool)

    def rama(x, y, dx, n):
        for _ in range(n):
            if not (0 <= x < tw and 0 <= y < th):
                return
            m[int(y), int(x)] = True
            y += 1
            x += dx + rng.choice((-1, 0, 0, 1))
            if rng.random() < 0.12 and n > 4:
                rama(x, y, -dx if dx else rng.choice((-1, 1)), n // 2)
    for _ in range(max(1, tw // 10)):
        rama(rng.randrange(tw), 0, rng.choice((-1, 0, 1)), th)
    return m


def pintores(V):
    k = V['clave']
    P = {}
    neo = [nm._hex(c) for c in V['neon']]

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'cic%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def piel(tw, th, cara, s):
        """La piel curtida: el tono del gigante con manchas grandes y limpias un poco mas oscuras y, en Arges, las
        cicatrices de rayo que brillan."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx = np.where((ys // 3 + xs // 5) % 7 == 0, 1, idx)
        if cara == 'arriba':
            idx = idx + 1
        elif cara == 'abajo':
            idx = idx - 1
        img = _imagen(_bisel(idx, 1, 1), V['piel'])
        if V['cicatriz']:
            m = _rayos(tw, th, s)
            img[m] = (*neo[1], 255)
            return img, _emis(img, m, 200)
        return img, None
    reg('piel', piel)

    def pecho(tw, th, cara, s):
        """El pecho y la panza: la piel con el vello en el medio (en Polifemo y Brontes) y la linea de la panza."""
        img, em_ = piel(tw, th, cara, s)
        if V['pelo'] == 'punta':
            return img, em_
        ys, xs = np.mgrid[0:th, 0:tw]
        vello = (abs(xs - tw / 2) < tw * (0.12 + 0.18 * (1 - abs(ys / max(th, 1) - 0.35)))) & ((xs + ys) % 3 != 0)
        img = np.where(vello[..., None], _imagen(np.full((th, tw), 1), V['pelo_c']), img)
        return img, em_
    reg('pecho', pecho)

    def pelo(tw, th, cara, s):
        """El pelo y la barba: rizos (Polifemo), trenzas con su hebra (Brontes) o pelo de punta (Arges)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        if V['pelo'] == 'rizos':
            idx = np.where(((xs // 2 + ys // 2) % 3 == 0) | ((xs + ys) % 5 == 0), 3, 1)
            idx = np.where((xs // 3 + ys // 3) % 4 == 0, 2, idx)
        elif V['pelo'] == 'trenzas':
            idx = np.where((ys + (xs // 3) % 2 * 2) % 4 < 2, 3, 2)
            idx = np.where(xs % 3 == 2, 1, idx)
        else:
            idx = np.where(xs % 2 == 0, 3, 2)
            idx = np.where((xs + ys) % 6 == 0, 4, idx)
        return _imagen(_bisel(idx, 1, 1), V['pelo_c']), None
    reg('pelo', pelo)

    def ropa(tw, th, cara, s):
        """Lo de encima: el vellon de oveja (rizos de lana en bolitas), el cuero del mandil (con costuras) o la tela."""
        ys, xs = np.mgrid[0:th, 0:tw]
        if V['encima'] == 'vellon':
            idx = np.where(((xs // 2) + (ys // 2)) % 2 == 0, 3, 2)
            idx = np.where((xs % 2 == 0) & (ys % 2 == 0), 4, idx)
        else:
            idx = np.full((th, tw), 2)
            idx = np.where(ys % 6 == 0, 1, idx)
            idx = np.where((xs % 4 == 0) & (ys % 6 == 3), 3, idx)
        return _imagen(_bisel(idx, 1, 1), V['ropa']), None
    reg('ropa', ropa)

    HIERRO = _r('14161a', '24272e', '383c46', '50566a', '72788c')

    def hierro(tw, th, cara, s):
        """El hierro de los brazales y los anillos: liso, con remaches."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx = np.where((xs % 4 == 1) & (ys % 4 == 1), 4, idx)
        return _imagen(_bisel(idx, 1, 1), HIERRO), None
    reg('hierro', hierro)

    CUERNO = _r('3a2e22', '5e4a36', '86704e', 'ac946a', 'd0b88a')

    def cuerno(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo = ys if cara in ('arriba', 'abajo') else xs
        idx = np.where(a_lo_largo % 3 == 0, 1, 3)
        return _imagen(_bisel(idx, 1, 0), CUERNO), None
    reg('cuerno', cuerno)

    def ojo(tw, th, cara, s):
        """El ojo: el blanco amarillento con venas, el iris grande que brilla como una fragua y la pupila oscura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        d = np.hypot((xs - cx) / max(cx, 1), (ys - cy) / max(cy, 1))
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (232, 220, 196, 255)
        rng = random.Random(s)
        for _ in range(4):                                              # las venas
            a = rng.uniform(0, TAU)
            for r_ in np.linspace(0.95, 0.62, 6):
                x, y = int(cx + math.cos(a) * r_ * cx), int(cy + math.sin(a) * r_ * cy)
                if 0 <= x < tw and 0 <= y < th:
                    t[y, x] = (176, 40, 34, 255)
                a += rng.uniform(-0.25, 0.25)
        iris = d < 0.6
        t[iris] = (*neo[1], 255)
        t[(d < 0.6) & (d > 0.48)] = (*neo[2], 255)
        t[d < 0.34] = (*neo[0], 255)
        pupila = d < 0.2
        t[pupila] = (16, 8, 6, 255)
        t[(abs(xs - cx + tw * 0.18) < 1) & (abs(ys - cy + th * 0.18) < 1)] = (255, 255, 255, 255)
        t[d >= 0.97] = (40, 22, 16, 255)
        return t, _emis(t, iris & ~pupila, 255)
    reg('ojo', ojo)

    def boca(tw, th, cara, s):
        """Dentro de la boca: carne oscura con la luz que sube del fondo (el mismo fuego del ojo)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t_ = ys / max(th - 1, 1)
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (40, 10, 10, 255)
        t[t_ > 0.55] = (*neo[2], 255)
        t[t_ > 0.8] = (*neo[1], 255)
        return t, _emis(t, t_ > 0.55, 220)
    reg('boca', boca)

    DIENTE = _r('6a5a40', '9a8a68', 'c8b896', 'e4d8bc', 'f6eedc')

    def dientes(tw, th, cara, s):
        """Los dientes del gigante: gordos, de bloque, desiguales y amarillentos, con su canto."""
        t = np.zeros((th, tw, 4), np.uint8)
        rng = random.Random(s)
        x = 0
        while x < tw:
            w = rng.choice((3, 4, 4, 5))
            h = th if rng.random() < 0.7 else int(th * 0.7)
            for xx in range(x, min(tw, x + w - 1)):
                for y in range(h):
                    c = DIENTE[3] if xx < x + w // 2 else DIENTE[2]
                    if y == h - 1 or xx == x:
                        c = DIENTE[1]
                    t[y, xx] = (*c, 255)
            x += w
        return t, None
    reg('dientes', dientes)

    def colmillo(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs < tw / 2, 3, 2)
        return _imagen(_bisel(idx, 1, 1), DIENTE), None
    reg('colmillo', colmillo)

    ROCA = _r('22201e', '36332e', '4c4840', '645e54', '7e786a')
    LIQUEN = _r('2a3018', '3e4622', '58622e', '74803e', '96a052')

    def roca(tw, th, cara, s):
        """La roca que alza: piedra gris con grietas y manchas de liquen."""
        idx = _manchas(tw, th, s, celda=6.0, umbral=0.6, alto=0.85)
        img = _imagen(_bisel(np.array([1, 2, 2, 3, 3])[idx], 1, 1), ROCA)
        m = _manchas(tw, th, s + 9, celda=5.0, umbral=0.72, alto=0.9) >= 3
        if cara == 'arriba':
            img = np.where(m[..., None], _imagen(np.full((th, tw), 2), LIQUEN), img)
        return img, None
    reg('roca', roca)
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
        M = em.marco(p0, d, up=arriba) if abs(_u(d) @ _u(arriba)) < 0.95 else em.marco(p0, d, up=(0.0, 0.0, 1.0))
        r = (radios[j] + radios[j + 1]) / 2
        for kx, ky in ((1.0, 0.74), (0.74, 1.0)):
            bm.cubo(out, M, -r * kx, -r * ky * achata, -r * 0.3, 2 * r * kx, 2 * r * ky * achata, L + r * 0.6, pintor,
                    caras=caras, semilla=semilla + j % 3)


def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    """Una fila de dientes a lo largo del canto de la boca (puntos x-z a la altura y), que baja (alto < 0) o sube."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado = float(np.linalg.norm(B - A))
        if alto < 0:
            lamina(out, (A2, B2, B, A), pintor, lado, abs(alto), semilla + j)
        else:
            lamina(out, (A, B, B2, A2), pintor, lado, abs(alto), semilla + j)


def cabeza(out, Mh, P, V, abre=26.0, semilla=0):
    """La cabeza, mirando a +z, con la comisura en y=0: el craneo ancho, la ceja de hueso en V sobre el ojo enorme, dos
    ranuras por nariz, la boca de oreja a oreja (la quijada cae abierta) con dientes gordos y dos colmillos que suben,
    y la luz en el fondo. Devuelve el fondo de la boca."""
    pi, pe = P['piel'], P['pelo']
    bm.cubo(out, Mh, -4.4, 0.0, -4.0, 8.8, 8.4, 7.6, pi, caras={'abajo': P['boca']}, semilla=semilla)            # el craneo
    bm.cubo(out, Mh, -3.8, -0.4, -3.6, 7.6, 9.4, 7.0, pi, caras={'abajo': P['boca']}, semilla=semilla + 1)
    bm.cubo(out, Mh, -4.0, 0.0, 3.4, 8.0, 2.4, 0.9, pi, semilla=semilla + 2)                                     # el morro
    for s in (1, -1):                                                                     # los pomulos
        bm.cubo(out, Mh, (2.4 if s > 0 else -4.6), 1.6, 2.2, 2.2, 2.2, 1.8, pi, semilla=semilla + 3)
    # el ojo, enorme, un poco salido, con sus parpados
    bm.cubo(out, Mh, -2.2, 3.0, 3.5, 4.4, 4.0, 0.5, pi, caras={'frente': P['ojo']}, semilla=semilla + 4)
    bm.cubo(out, Mh, -2.5, 6.8, 3.2, 5.0, 0.6, 1.0, pi, semilla=semilla + 5)
    bm.cubo(out, Mh, -2.4, 2.6, 3.3, 4.8, 0.5, 0.9, pi, semilla=semilla + 5)
    # la ceja de hueso, en V: baja hacia el centro
    for s in (1, -1):
        Mc = Mh @ vr.T(s * 2.0, 7.7, 3.9) @ vr.Rz(s * 16 * D)
        caja(out, Mc, -2.8, 2.6, -0.6, 0.7, -1.0, 0.8, pi, semilla=semilla + 6)
    for s in (1, -1):                                                                     # las ranuras de la nariz
        bm.cubo(out, Mh, s * 0.7 - 0.25, 2.4, 4.25, 0.5, 0.3, 0.1, P['boca'], semilla=semilla + 7)
    hilera(out, Mh, [(-3.6, 0.6), (-3.6, 3.4), (3.6, 3.4), (3.6, 0.6)], 0.05, -1.4, P['dientes'], semilla=semilla + 8)
    bm.cubo(out, Mh, -3.4, -3.6, -2.4, 6.8, 3.6, 0.4, P['boca'], semilla=semilla + 9)                            # el fondo
    Mj = Mh @ vr.T(0.0, -0.2, -2.2) @ vr.Rx(abre * D)                                       # la quijada
    bm.cubo(out, Mj, -4.0, -3.4, -1.6, 8.0, 3.4, 7.2, pi, caras={'arriba': P['boca']}, semilla=semilla + 10)
    bm.cubo(out, Mj, -3.6, -2.8, 5.4, 7.2, 3.4, 0.9, pi, semilla=semilla + 11)
    hilera(out, Mj, [(-3.4, 0.0), (-3.4, 5.4), (3.4, 5.4), (3.4, 0.0)], 0.1, 1.3, P['dientes'], semilla=semilla + 12)
    for s in (1, -1):                                                                     # los colmillos que suben
        b = (s * 2.5, 0.2, 5.0)
        for lado in ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)):
            l = Mj[:3, :3] @ np.array(lado) * 0.55
            arr = Mj[:3, :3] @ np.array((0.0, 1.0, -0.15)) * 3.0
            q = pt(Mj, b)
            lamina(out, (q - l, q + l, q + l * 0.25 + arr, q - l * 0.25 + arr), P['colmillo'], 1.1, 3.0, semilla=semilla + 13)
    return pt(Mh, (0.0, -1.6, -1.6)), Mj


def pelambre(out, Mh, Mj, P, V, semilla=0):
    """La melena y la barba de cada tipo: rizos y barba ancha (Polifemo), calvo con un cuerno y la barba en tres
    trenzas con anillos de hierro (Brontes), o el pelo y la barba de punta, blancos (Arges)."""
    pe = P['pelo']
    if V['pelo'] != 'trenzas':
        bm.cubo(out, Mh, -4.8, 6.2, -4.6, 9.6, 3.2, 7.4, pe, semilla=semilla)                                 # el casco de pelo
        bm.cubo(out, Mh, -5.0, 0.4, -5.0, 10.0, 7.6, 2.8, pe, semilla=semilla + 1)                            # la nuca
    if V['pelo'] == 'rizos':
        rng = random.Random(3)
        for i in range(14):                                                               # los rizos sueltos de la melena
            a = -1.3 + 2.6 * i / 13
            b = pt(Mh, (math.sin(a) * 4.8, 8.6 + rng.uniform(-0.6, 0.6), -1.2 - abs(math.cos(a)) * 2.4))
            M = vr.T(*b) @ vr.Ry(a)
            caja(out, M, -1.0, 1.0, -0.9, 1.1, -1.0, 1.0, pe, semilla=semilla + 2 + i % 3)
        for x in np.linspace(-3.4, 3.4, 6):                                               # la barba, ancha, que cuelga
            L = 6.5 - abs(x) * 0.5
            a = pt(Mj, (x, -3.0, 4.6))
            ps = [a, a + np.array((x * 0.1, -L * 0.5, 0.8)), a + np.array((x * 0.15, -L, 0.6))]
            tubo_caras(out, ps, [1.3, 1.1, 0.5], pe, semilla=semilla + 5)
        for s in (1, -1):                                                                 # las patillas
            caja(out, Mh, s * 4.4 - 0.7, s * 4.4 + 0.7, -3.2, 3.4, -2.6, 2.4, pe, semilla=semilla + 7)
    elif V['pelo'] == 'trenzas':
        tubo_caras(out, [pt(Mh, (0.0, 8.0, 1.8)), pt(Mh, (0.0, 10.4, 2.6)), pt(Mh, (0.0, 12.2, 3.6))], [1.0, 0.7, 0.12],
                   P['cuerno'], semilla=semilla)                                            # el cuerno de la frente
        for s in (1, -1):
            caja(out, Mh, s * 4.4 - 0.6, s * 4.4 + 0.6, 1.0, 5.6, -3.6, 1.8, pe, semilla=semilla + 1)
        for x in (-2.4, 0.0, 2.4):                                                        # las trenzas de la barba
            a = pt(Mj, (x, -3.0, 4.2))
            ps = [a, a + np.array((x * 0.15, -3.0, 0.6)), a + np.array((x * 0.25, -6.0, 0.4)), a + np.array((x * 0.3, -8.4, -0.2))]
            tubo_caras(out, ps, [1.2, 1.0, 0.85, 0.5], pe, semilla=semilla + 2)
            for t in (0.35, 0.75):
                q = ps[0] + (ps[-1] - ps[0]) * t
                caja(out, vr.T(*q), -1.05, 1.05, -0.4, 0.4, -1.05, 1.05, P['hierro'], semilla=semilla + 3)
    else:
        rng = random.Random(5)
        for i in range(16):                                                               # el pelo de punta, como erizado
            a = -1.4 + 2.8 * i / 15
            b = pt(Mh, (math.sin(a) * 4.2, 8.8, -1.0 - abs(math.cos(a)) * 1.8))
            d = Mh[:3, :3] @ _u(np.array((math.sin(a) * 0.8, 1.0, -0.5)))
            L = rng.uniform(3.0, 5.0)
            tubo_caras(out, [b, b + d * L * 0.6, b + d * L], [0.7, 0.45, 0.08], pe, semilla=semilla + i % 3)
        for i, x in enumerate(np.linspace(-3.0, 3.0, 7)):                                 # la barba, de punta hacia abajo
            a = pt(Mj, (x, -3.0, 3.6))
            d = Mj[:3, :3] @ _u(np.array((x * 0.12, -1.0, 0.25)))
            L = 5.5 - abs(x) * 0.5
            tubo_caras(out, [a, a + d * L * 0.6, a + d * L], [0.8, 0.5, 0.08], pe, semilla=semilla + i % 3)


# ======================================================================
#  EL CICLOPE
# ======================================================================
def ciclope(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    pi = P['piel']
    try:
        # las piernas, abiertas y plantadas (la izquierda adelantada), gruesas y cortas
        for s, adelante in ((1, -2.0), (-1, 2.4)):
            cadera = np.array((s * 4.6, 19.0, 0.0))
            rodilla = np.array((s * 6.6, 10.6, adelante + 1.8))
            tobillo = np.array((s * 7.0, 2.4, adelante))
            tubo_caras(out, [cadera, (cadera + rodilla) / 2 + np.array((s * 0.6, 0.0, 0.4)), rodilla], [4.8, 4.6, 3.4], pi, semilla=10)
            tubo_caras(out, [rodilla, (rodilla + tobillo) / 2 + np.array((0.0, 0.0, -0.6)), tobillo], [3.4, 3.2, 2.4], pi, semilla=11)
            bm.cubo(out, vr.T(*tobillo), -3.0, -2.4, -3.0, 6.0, 3.2, 8.6, pi, semilla=12)        # el pie, ancho
            for x in (-2.0, 0.0, 2.0):
                bm.cubo(out, vr.T(*tobillo), x - 0.8, -2.4, 5.4, 1.6, 1.4, 1.2, P['colmillo'], semilla=13)
        # el tronco, redondo: la cadera, la panza que sale, el pecho ancho y los hombros
        tronco = [np.array((0.0, 15.0, 0.0)), np.array((0.0, 19.0, 0.8)), np.array((0.0, 23.5, 1.6)), np.array((0.0, 28.0, 1.0)),
                  np.array((0.0, 32.0, 0.0)), np.array((0.0, 34.0, -0.4))]
        tubo_caras(out, tronco, [6.2, 7.2, 7.8, 8.6, 8.4, 6.0], pi, caras={'frente': P['pecho']}, achata=0.62,
                   arriba=(0.0, 0.0, 1.0), semilla=20)
        for s in (1, -1):                                                                 # los hombros, como bolas
            caja(out, vr.T(s * 9.4, 31.4, 0.0), -3.8, 3.8, -3.4, 3.6, -3.8, 3.8, pi, semilla=21)
        tubo_caras(out, [np.array((0.0, 32.0, 0.0)), np.array((0.0, 36.0, 0.8))], [3.8, 3.4], pi, semilla=22)   # el cuello
        # lo de encima de cada tipo
        if V['encima'] == 'vellon':
            bm.cubo(out, np.eye(4), -11.6, 32.4, -6.0, 23.2, 3.6, 7.0, P['ropa'], semilla=30)               # la piel de oveja,
            bm.cubo(out, np.eye(4), -11.0, 20.0, -6.4, 22.0, 13.0, 2.6, P['ropa'], semilla=30)              # a la espalda
            bm.cubo(out, np.eye(4), -7.6, 12.6, -5.2, 15.2, 5.4, 10.6, P['ropa'], semilla=31)               # y el faldon
        elif V['encima'] == 'mandil':
            bm.cubo(out, np.eye(4), -5.6, 9.0, 5.8, 11.2, 17.0, 0.8, P['ropa'], semilla=30)                 # el mandil de cuero
            bm.cubo(out, np.eye(4), -7.6, 14.6, -5.4, 15.2, 2.2, 11.0, P['hierro'], semilla=31)             # el cinturon de hierro
            for s in (1, -1):
                tubo_caras(out, [np.array((s * 4.0, 25.0, 6.4)), np.array((s * 7.0, 31.4, 3.0))], [0.7, 0.7], P['ropa'], semilla=32)
        else:
            bm.cubo(out, np.eye(4), -7.6, 12.8, -5.2, 15.2, 5.0, 10.6, P['ropa'], semilla=31)               # el taparrabos
        # los brazos, alzados: la roca va encima y detras de la cabeza
        roca_c = np.array((0.0, 60.0, -3.0))
        for s in (1, -1):
            hombro = np.array((s * 9.6, 31.6, 0.0))
            codo = np.array((s * 14.4, 41.0, 0.4))
            muneca = np.array((s * 10.6, 51.5, -1.6))
            tubo_caras(out, [hombro, (hombro + codo) / 2 + np.array((s * 0.8, 0.0, 0.4)), codo], [4.2, 4.4, 3.2], pi, semilla=40)
            tubo_caras(out, [codo, (codo + muneca) / 2 + np.array((s * 0.4, 0.0, 0.3)), muneca], [3.2, 3.4, 2.6], pi, semilla=41)
            if V['encima'] == 'mandil':
                tubo_caras(out, [codo + (muneca - codo) * 0.5, muneca], [3.5, 3.0], P['hierro'], semilla=44)   # los brazales
            Mm = vr.T(*muneca) @ vr.Rz(s * 20 * D)
            caja(out, Mm, -2.8, 2.8, 0.0, 4.6, -2.8, 2.8, pi, semilla=45)                               # la mano
            for z in (-1.9, 0.0, 1.9):
                caja(out, Mm, (-3.8 if s > 0 else 1.9), (-1.9 if s > 0 else 3.8), 2.6, 6.4, z - 0.8, z + 0.8, pi, semilla=46)
        rng = random.Random(7)                                                            # la roca, de bloques torcidos
        for i, (w, h, d) in enumerate(((15.0, 9.0, 11.0), (12.0, 11.0, 9.0), (10.0, 7.0, 13.0), (8.0, 12.0, 8.0))):
            M = vr.T(*(roca_c + np.array((rng.uniform(-1.5, 1.5), rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0))))) \
                @ vr.Ry(rng.uniform(0, 1.5)) @ vr.Rz(rng.uniform(-0.3, 0.3)) @ vr.Rx(rng.uniform(-0.3, 0.3))
            bm.cubo(out, M, -w / 2, -h / 2, -d / 2, w, h, d, P['roca'], semilla=50 + i)
        # la cabeza, grande, adelantada y mirando abajo, al que tiene delante
        Mh = vr.T(0.0, 36.2, 2.6) @ vr.Rx(12 * D) @ np.diag([CABEZA] * 3 + [1.0])
        fondo, Mj = cabeza(out, Mh, P, V, semilla=60)
        pelambre(out, Mh, Mj, P, V, semilla=80)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    fondo = pt(E, fondo)
    ojo = pt(E @ Mh, (0.0, 5.0, 5.4))
    return out, {'boca': fondo, 'ojo': ojo, 'luces': [fondo, ojo]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

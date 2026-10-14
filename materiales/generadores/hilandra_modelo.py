"""
Hilandra, la Reina de las Telas (13-10-2026). Juan, tras Melenara: «en el siguiente boss podrias
hacer algo femenino, una boss mujer, anatomia de mujer».

Una reina arana: del cuerpo de una arana gigante de ocho patas sale el torso de una mujer (las
caderas, la cintura estrecha, el corpino de quitina, los hombros y los brazos largos con garras), y
encima, su cabeza: una cara de mujer con los ojos rasgados y encendidos, una tiara de seis ojillos de
arana en la frente, la melena larga que le cae por la espalda y la boca abierta en un grito, encendida
por dentro, con dos queliceros como colmillos a los lados. Las patas, gruesas y con sus rodillas
altas, la rodean como una corona; detras, el abdomen con su marca encendida.

Hecha como guia (no como ejemplo) de lo que funciono: la cabeza manda y se hace sin escala, pocas
piezas gordas (troncos que se afinan), texturas limpias, la boca encendida de un solo color, fotos sin
letras y con el borde blanco. Nada de piezas de Lumara ni de Melenara.

Los tres tipos cambian de FORMA:

    A  Tejedora    los brazos alzados sostienen una tela redonda que se abre detras de ella como un
                   halo, con el rocio encendido; nacar y coral
    B  Viuda       un velo negro que le cae de la cabeza a la espalda, el abdomen enorme con el reloj
                   de arena encendido y las patas de delante alzadas; azabache y carmin
    C  Cazadora    cuatro brazos con garras, agazapada, las patas de delante alzadas para saltar y el
                   cuerpo con mechones de vello; cobre y turquesa
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
import sierpe_modelo as sm
from bestias_modelo import cubo, viga, pua, punto, _imagen, _emis
from sierpe_modelo import _bisel, lamina, bola
from riscara_modelo import bloque
from lumara_modelo import _dir
from melenara_modelo import _tronco, _planta, _tapa, _hilera

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 8

DIENTE = _r('5e5a56', '8e8a84', 'bdb8b0', 'dedad2', 'f6f4ee')
VARIANTES = {
    'A': dict(
        clave='A', nombre='Tejedora', color='Nacar',
        quitina=_r('1c1410', '2c201a', '42322a', '5e4a3e', '80685a'),
        piel=_r('8a7e74', 'b0a598', 'd2c8ba', 'eae2d4', 'fbf6ec'),
        cabello=_r('120c0a', '1e1612', '2c221c', '3e3028', '544238'),
        seda=_r('9a9086', 'c0b6aa', 'ddd4c8', 'eee8de', 'fffaf2'),
        neon=('fff0ea', 'ff7a5a', '7a2414'),
    ),
    'B': dict(
        clave='B', nombre='Viuda', color='Azabache',
        quitina=_r('08080a', '121214', '1e1e22', '2e2e34', '46464e'),
        piel=_r('6a6870', '8e8c94', 'b2b0b8', 'd2d0d6', 'eeecf0'),
        cabello=_r('060608', '0e0e12', '18181e', '24242c', '34343e'),
        seda=_r('08080a', '101014', '1a1a20', '26262e', '363640'),
        neon=('ffe2e2', 'ff2a3a', '6a0610'),
    ),
    'C': dict(
        clave='C', nombre='Cazadora', color='Cobre',
        quitina=_r('1e100a', '341c10', '502c18', '704020', '965a2e'),
        piel=_r('6e4a34', '966648', 'ba8662', 'd6a682', 'eccaa8'),
        cabello=_r('1a0e08', '2a1810', '3e2418', '563422', '74482e'),
        seda=_r('1a0e08', '2a1810', '3e2418', '563422', '74482e'),
        neon=('e8fffa', '2ee8c8', '06584c'),
    ),
}


def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'hil%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']
    c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)

    def quitina(tw, th, cara, s):
        """La quitina de la arana: lisa y lustrosa, con un brillo largo a un lado y el canto claro."""
        idx = np.full((th, tw), 1)
        largo_x = tw >= th
        if largo_x and th >= 4:
            idx[1, :] = 3
            idx[2, :] = 2
        elif tw >= 4:
            idx[:, 1] = 3
            idx[:, 2] = 2
        return _imagen(_bisel(idx), V['quitina']), None
    reg('quitina', quitina)

    def pata(tw, th, cara, s):
        """Las patas: la quitina con un anillo claro cerca de cada punta (las rodillas)."""
        idx = np.full((th, tw), 1)
        largo_x = tw >= th
        n = tw if largo_x else th
        a = np.arange(n)
        anillo = (a < max(1, n * 0.1)) | (a >= n - max(1, n * 0.1))
        if largo_x:
            idx[:, anillo] = 3
            if th >= 4:
                idx[1, ~anillo] = 2
        else:
            idx[anillo, :] = 3
            if tw >= 4:
                idx[~anillo, 1] = 2
        return _imagen(_bisel(idx), V['quitina']), None
    reg('pata', pata)

    def caparazon(tw, th, cara, s):
        """El caparazon de encima del cuerpo: surcos que salen del centro, oscuros, sobre la quitina."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        ang = np.arctan2(ys - cy, xs - cx)
        r = np.hypot((xs - cx) / max(cx, 1), (ys - cy) / max(cy, 1))
        idx = np.where(r < 0.25, 3, 2)
        surco = (np.abs(((ang / (TAU / 8)) % 1) - 0.5) > 0.44) & (r > 0.3)
        idx = np.where(surco, 0, idx)
        return _imagen(_bisel(idx), V['quitina']), None
    reg('caparazon', caparazon)

    def piel(tw, th, cara, s):
        """La piel de la reina: lisa, con su canto."""
        idx = np.full((th, tw), 2)
        return _imagen(_bisel(idx), V['piel']), None
    reg('piel', piel)

    def corpino(tw, th, cara, s):
        """El corpino de quitina: placas a lo largo con la costura clara en medio y los cantos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs % 4) == 0, 0, 2)
        idx = np.where((xs % 4) == 1, 3, idx)
        if tw >= 6:
            idx[:, tw // 2 - 1:tw // 2 + 1] = 4
        if th >= 6:
            idx[(ys % 6) == 5] = np.minimum(idx[(ys % 6) == 5], 1)
        return _imagen(_bisel(idx), V['quitina']), None
    reg('corpino', corpino)

    def cabello(tw, th, cara, s):
        """La melena: mechones a lo largo, de dos tonos, con alguna hebra clara; limpia."""
        largo_x = tw >= th
        n_l, n_t = (tw, th) if largo_x else (th, tw)
        fase = random.Random(s).randrange(5)
        b = (np.arange(n_t)[:, None] + fase) % 5
        a = np.arange(n_l)[None, :]
        idx = np.where(b < 2, 2, 1) + 0 * a
        idx = np.where((b == 0) & (((a + 3 * fase) % 13) < 9), 3, idx)
        if not largo_x:
            idx = idx.T
        return _imagen(idx, V['cabello']), None
    reg('cabello', cabello)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)

    def cara(tw, th, cara_, s):
        """La cara de la reina, pintada a pixel como la de un modelo de Minecraft (la frente arriba, la
        nariz abajo; la boca va aparte): la piel con la sombra a los lados, la tiara de seis ojillos de
        arana encendidos, las cejas finas que bajan hacia dentro, los ojos almendrados con la raya
        oscura de las pestanas, el rabillo que sube y el iris encendido, y la nariz con su sombra."""
        t = np.zeros((th, tw, 4), np.uint8)
        pi = [(*c, 255) for c in V['piel']]
        os_ = [(*c, 255) for c in V['cabello']]
        t[:, :] = pi[2]
        t[:, :max(1, tw // 10)] = pi[1]
        t[:, tw - max(1, tw // 10):] = pi[1]
        t[th - max(1, th // 8):, :] = pi[1]
        for y in range(th):                                        # la sombra en V de los carrillos
            f = (y / max(th - 1, 1) - 0.55) / 0.45
            if f > 0:
                w = int(round(f * tw * 0.22))
                t[y, :w] = pi[1]
                t[y, tw - w:] = pi[1]
        X = lambda f: int(round(f * (tw - 1)))
        Y = lambda f: int(round(f * (th - 1)))

        def px(x, y, col):
            if 0 <= x < tw and 0 <= y < th:
                t[y, x] = col
        brillo = np.zeros((th, tw), bool)

        def luz(x, y, col):
            if 0 <= x < tw and 0 <= y < th:
                t[y, x] = col
                brillo[y, x] = True
        c_ojo, c_nuc = (*c_m, 255), (*c_n, 255)
        for j, (fx, fy) in enumerate(((0.16, 0.2), (0.29, 0.14), (0.43, 0.11), (0.57, 0.11), (0.71, 0.14), (0.84, 0.2))):
            x, y = X(fx), Y(fy)                                   # la tiara de ojillos
            luz(x, y, c_ojo)
            if j in (2, 3):
                luz(x, y + 1, c_ojo)
                luz(x + (1 if j == 3 else -1), y, c_nuc)
        # cada ojo, dibujado a mano (para el lado izquierdo; el derecho, en espejo). Filas desde la
        # ceja: 'c' ceja, 'l' pestana, 'g' neon, 'n' iris, 's' sombra de piel, 'p' parpado de abajo
        OJO = (".....ccc.",
               "...cc....",
               ".........",
               "........l",
               ".lllllll.",
               "sggnnggg.",
               ".ggnnggp.",
               "..ppppp..")
        ye0 = Y(0.3)
        for lado in (1, -1):
            xc = X(0.5 + lado * 0.235)
            for fy, fila in enumerate(OJO):
                for fx, ch in enumerate(fila):
                    if ch == '.':
                        continue
                    dx = fx - 4
                    x = xc + (dx if lado > 0 else -dx)
                    y = ye0 + fy
                    if ch == 'c':
                        px(x, y, os_[1])
                    elif ch == 'l':
                        px(x, y, os_[0])
                    elif ch == 'g':
                        luz(x, y, c_ojo)
                    elif ch == 'n':
                        luz(x, y, c_nuc)
                    elif ch == 's':
                        px(x, y, pi[1])
                    elif ch == 'p':
                        px(x, y, pi[1])
        xn = X(0.5)
        for y in range(Y(0.58), Y(0.78)):                          # la nariz
            px(xn + 1, y, pi[1])
        px(xn - 1, Y(0.79), pi[0])
        px(xn + 2, Y(0.79), pi[0])
        for lado in (1, -1):                                       # el colorete, apenas
            px(X(0.5 + lado * 0.26), Y(0.7), (*qm._mezcla(V['piel'][2], c_m, 0.18), 255))
        return t, _emis(t, brillo, 245)
    reg('cara', cara)

    def punta(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('punta', punta, pleno=True)

    def sombra(tw, th, cara, s):
        """Lo oscuro: las cuencas de los ojos, los labios y las garras."""
        idx = np.full((th, tw), 0)
        if th >= 3:
            idx[0, :] = 1
        return _imagen(idx, V['cabello']), None
    reg('sombra', sombra)

    def garra(tw, th, cara, s):
        idx = np.full((th, tw), 1)
        if tw >= th and th >= 2:
            idx[0, :] = 3
        elif tw >= 2:
            idx[:, 0] = 3
        return _imagen(idx, V['cabello']), None
    reg('garra', garra)

    def _hojas_de_dientes(tw, th, colgando):
        """Dientes finos y puntiagudos, dibujados en una hoja: de tres pixeles, juntos, en sierra."""
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTE]
        n = max(1, (tw + 1) // 4)
        x0 = (tw - (n * 4 - 1)) // 2
        for i in range(n):
            x = x0 + i * 4
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.75)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)
                pix = ((x + 1, c[4]),) if f > 0.6 else ((x, c[2]), (x + 1, c[4]), (x + 2, c[1]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
        return t, None

    def colmillos(tw, th, cara, s):
        return _hojas_de_dientes(tw, th, True)
    reg('colmillos', colmillos)

    def dientes(tw, th, cara, s):
        return _hojas_de_dientes(tw, th, False)
    reg('dientes', dientes)

    def encia(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = qm._mezcla(c_h, (6, 4, 6), 0.55)
        t[..., 3] = 255
        return t, None
    reg('encia', encia)

    def fauces(tw, th, cara, s):
        """Por dentro de la boca: hondo junto a los dientes y cada vez mas claro hacia la garganta."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            f = y / max(th - 1, 1)
            c = c_n if f > 0.84 else (qm._mezcla(c_m, c_n, 0.45) if f > 0.62 else (c_m if f > 0.38 else
                                                                                 (qm._mezcla(c_h, c_m, 0.5) if f > 0.18 else c_h)))
            t[y, :] = (*c, 255)
            if y % 3 == 2 and f < 0.84:
                t[y, :] = (*qm._mezcla(c_h, (0, 0, 0), 0.3), 255)
        return t, _emis(t, np.ones((th, tw), bool), 225)
    reg('fauces', fauces)

    def garganta(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot((xs - cx) / max(tw / 2, 1), (ys - cy) / max(th / 2, 1))
        col = np.where((r < 0.3)[..., None], np.array(c_n),
                       np.where((r < 0.55)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)),
                                np.where((r < 0.8)[..., None], np.array(c_m), np.array(c_h))))
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 0.8, 240)
    reg('garganta', garganta)

    def quelicero(tw, th, cara, s):
        """Los queliceros: quitina negra y lustrosa con la punta encendida (el veneno)."""
        idx = np.full((th, tw), 1)
        largo_x = tw >= th
        if largo_x and th >= 3:
            idx[1, :] = 3
        elif tw >= 3:
            idx[:, 1] = 3
        tex = _imagen(idx, V['cabello'])
        return tex, None
    reg('quelicero', quelicero)

    def abdomen(tw, th, cara, s):
        """El abdomen: la quitina lisa y lustrosa, con bandas finas de traves."""
        idx = np.full((th, tw), 1)
        largo_x = tw >= th
        if largo_x and th >= 4:
            idx[1, :] = 3
        elif tw >= 4:
            idx[:, 1] = 3
        return _imagen(_bisel(idx), V['quitina']), None
    reg('abdomen', abdomen)

    def marca(tw, th, cara, s):
        """La marca encendida del lomo del abdomen (arriba de la textura, hacia delante): cheurones
        en la Tejedora, el reloj de arena en la Viuda y una fila de rombos en la Cazadora."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        u = (xs + 0.5) / tw - 0.5
        v = (ys + 0.5) / th
        if k == 'A':
            fase = (v * 4.0) % 1
            m = (np.abs(fase - (0.25 + np.abs(u) * 1.1)) < 0.09) & (np.abs(u) < 0.38) & (v > 0.06) & (v < 0.94)
        elif k == 'B':
            w = 0.05 + 0.42 * np.abs(v - 0.5) / 0.5
            m = (np.abs(u) < w) & (np.abs(v - 0.5) < 0.42)
        else:
            fase = (v * 5.0) % 1 - 0.5
            m = ((np.abs(u) * 2.2 + np.abs(fase)) < 0.32) & (v > 0.05) & (v < 0.95)
        if not m.any():
            return t, None
        t[m] = (*c_m, 255)
        borde = sm._borde_de(m) & ~m
        t[borde] = (*c_h, 255)
        nucleo = m & ~sm._borde_de(~m)
        t[nucleo & (((xs + ys) % 2) == 0)] = (*qm._mezcla(c_m, c_n, 0.5), 255)
        return t, _emis(t, m, 230)
    reg('marca', marca)
    def tela(tw, th, cara, s):
        """Un sector de la tela redonda: los dos radios de los bordes y uno en medio, de un pixel, y la
        espiral en tramos rectos de radio a radio (filas de la textura, arriba el borde de fuera), con
        gotas de rocio encendidas; entre los hilos, nada."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        v = 1 - (ys + 0.5) / th                                   # 0 en el centro, 1 en el borde
        radio = (xs == 0) | (xs == tw - 1) | (xs == tw // 2)
        paso = max(4, th // 11)
        espiral = ((ys % paso) == 1) & (v > 0.14)
        lineas = (radio | espiral) & (v < 0.995)
        t[lineas] = (*V['seda'][3], 255)
        t[radio & lineas] = (*V['seda'][4], 255)
        gota = espiral & (((xs * 5 + ys * 3) % 17) == 0) & (v > 0.3)
        t[gota] = (*c_n, 255)
        return t, _emis(t, gota, 230)
    reg('tela', tela)

    def velo(tw, th, cara, s):
        """El velo de la Viuda: seda negra en bandas finas que caen, con un encaje claro en el borde de
        abajo, roto en picos, y el canto encendido."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs % 3) == 0, 0, 2)
        img = _imagen(idx, V['seda'])
        A = max(2.0, th * 0.06)
        fase = (xs % 7 + 0.5) / 7
        borde = th - 1 - A * np.abs(fase * 2 - 1)                  # el borde de abajo, en picos
        fuera = ys > borde
        canto = (~fuera) & (ys > borde - 1.2)
        img[canto] = (*c_m, 255)
        t[~fuera] = img[~fuera]
        return t, _emis(t, canto, 160)
    reg('velo', velo)

    def vello(tw, th, cara, s):
        """Los mechones de vello de la Cazadora: hebras cortas, claras en la punta."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs + (ys // 3)) % 3) == 0, 1, 2)
        idx = np.where(ys < max(1, th * 0.3), 3, idx)
        return _imagen(idx, V['cabello']), None
    reg('vello', vello)
    return P


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def _seg(out, p0, p1, r0, r1, pintor, semilla=0, achata=1.0):
    """Un tramo que se afina, de p0 (medio lado r0) a p1 (r1); 'achata' estrecha la seccion de
    canto (para brazos y cuello)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    if L < 1e-4:
        return
    M = em.marco(p0, p1 - p0)
    todo = {'arriba': pintor, 'abajo': pintor, 'lados': pintor, 'frente': pintor, 'atras': pintor}
    _tronco(out, M, -r0 * 0.3, L + r1 * 0.3, (-r0, r0, -r0 * achata, r0 * achata), (-r1, r1, -r1 * achata, r1 * achata), todo,
            semilla=semilla)


def _ovoide(out, M, rx, ry, rz, pintor, semilla=0, caras=None):
    """Un huevo de pixeles: cinco cajas cruzadas a escalones, para que el canto se lea redondo desde
    cualquier lado."""
    for a, b, c in ((1.0, 0.55, 0.82), (0.92, 0.76, 0.9), (0.76, 0.92, 0.95), (0.52, 1.0, 0.78), (0.66, 0.66, 1.0)):
        cubo(out, M, -rx * a, -ry * b, -rz * c, 2 * rx * a, 2 * ry * b, 2 * rz * c, pintor, caras=caras, semilla=semilla)


def _huevo(out, M, rx, ry, rz, pintor, semilla=0):
    """Un huevo de troncos a lo largo de z (en el marco M): secciones que crecen y menguan, dos
    veces (una derecha y otra girada 45 grados y algo menor), para que se lea redondo desde todos
    los lados y no como una caja. Devuelve el perfil de arriba (z, alto) para poner la marca."""
    perfil = ((-1.0, 0.36), (-0.66, 0.84), (-0.16, 1.0), (0.38, 0.92), (0.78, 0.64), (1.0, 0.28))
    todo = {'arriba': pintor, 'abajo': pintor, 'lados': pintor, 'frente': pintor, 'atras': pintor}
    for giro, k_ in ((0.0, 1.0), (45.0, 0.78)):
        Mg = M @ vr.Rz(giro * D)
        for j, ((z0, f0), (z1, f1)) in enumerate(zip(perfil, perfil[1:])):
            _tronco(out, Mg, z0 * rz, z1 * rz, (-rx * f0 * k_, rx * f0 * k_, -ry * f0 * k_, ry * f0 * k_),
                    (-rx * f1 * k_, rx * f1 * k_, -ry * f1 * k_, ry * f1 * k_), todo, semilla=semilla + j)
    return [(z * rz, ry * f) for z, f in perfil]


def _mano(out, muneca, d, arriba, P, semilla=0, abre=1.0, largo=1.0):
    """Una mano de dedos largos, abierta: la palma y cuatro dedos de dos tramos que acaban en garra
    oscura, y el pulgar."""
    M = em.marco(np.asarray(muneca, float), d, up=arriba)
    _seg(out, punto(M, (0, 0, -0.1)), punto(M, (0, 0, 0.9 * largo)), 0.42, 0.5, P['piel'], semilla=semilla, achata=0.45)
    for j in range(4):
        f = (j - 1.5) / 1.5
        b = punto(M, (f * 0.36, 0.0, 0.85 * largo))
        d1 = _dir(M, (f * 0.35 * abre, 0.05, 1.0))
        d1 = d1 / np.linalg.norm(d1)
        m = b + d1 * (0.75 + 0.1 * (1 - abs(f))) * largo
        d2 = _dir(M, (f * 0.3 * abre, -0.45, 1.0))
        d2 = d2 / np.linalg.norm(d2)
        q = m + d2 * 0.6 * largo
        _seg(out, b, m, 0.13, 0.11, P['piel'], semilla=semilla + 1)
        _seg(out, m, q, 0.11, 0.05, P['garra'], semilla=semilla + 2)
    b = punto(M, (0.0, 0.0, 0.2))
    pulgar = _dir(M, (-0.9, 0.0, 0.6))
    _seg(out, b + _dir(M, (-0.35, 0, 0)), b + _dir(M, (-0.35, 0, 0)) + pulgar / np.linalg.norm(pulgar) * 0.75, 0.13, 0.06,
         P['garra'], semilla=semilla + 3)


def _brazo(out, hombro, codo, muneca, d_mano, arriba_mano, P, semilla=0, abre=1.0):
    """Un brazo largo y fino: el hombro con su placa, el brazo de piel, el antebrazo de quitina y la
    mano de garras."""
    _seg(out, hombro, codo, 0.5, 0.4, P['piel'], semilla=semilla, achata=0.9)
    bola(out, vr.T(*codo), 0.42, P['piel'], semilla=semilla + 1)
    _seg(out, codo, muneca, 0.46, 0.34, P['quitina'], semilla=semilla + 2, achata=0.85)
    _mano(out, muneca, d_mano, arriba_mano, P, semilla=semilla + 4, abre=abre)


# ----------------------------------------------------------------------
#  La cabeza (se hace sin escala; hilandra() la pone agrandada)
# ----------------------------------------------------------------------
def cabeza(out, Mh, V, P):
    """La cabeza de la reina, de mujer y estrecha: el craneo alto que se estrecha hacia la nuca, la
    frente con la tiara de seis ojillos de arana, los ojos rasgados y encendidos con su sombra, las
    cejas finas, los pomulos altos y la nariz fina; la boca abierta en un grito, encendida por dentro,
    con dientes finos en hoja y los labios oscuros, y la barbilla en punta; a los lados de la boca,
    los dos queliceros que bajan como colmillos."""
    piel = {'arriba': P['piel'], 'abajo': P['piel'], 'lados': P['piel'], 'frente': P['piel'], 'atras': P['piel']}
    sin_cara = {'arriba': P['piel'], 'abajo': P['piel'], 'lados': P['piel'], 'atras': P['piel']}
    _tronco(out, Mh, -2.0, 1.0, (-1.12, 1.12, 0.95, 3.25), (-1.28, 1.28, 0.75, 3.45), sin_cara, semilla=1)  # el craneo
    ppb = bm.PPB
    bm.PPB = ppb * 2                                       # la cara, a doble pixel (como la cabeza de un jugador)
    try:
        lamina(out, (punto(Mh, (-1.28, 0.75, 1.0)), punto(Mh, (1.28, 0.75, 1.0)), punto(Mh, (1.28, 3.45, 1.0)),
                     punto(Mh, (-1.28, 3.45, 1.0))), P['cara'], 2.56, 2.7, semilla=2)
    finally:
        bm.PPB = ppb
    for s in (1, -1):
        bloque(out, Mh @ vr.T(s * 0.86, 1.32, 0.86) @ vr.Rz(s * 8 * D), 0.46, 0.36, 0.42, P['piel'], semilla=3)   # el pomulo
    _tronco(out, Mh @ vr.T(0, 1.62, 1.0), 0.0, 0.22, (-0.1, 0.1, -0.5, 0.0), (-0.11, 0.11, -0.56, -0.36),
            {'frente': P['piel'], 'lados': P['piel'], 'abajo': P['piel']}, semilla=7)                    # la nariz
    # la de arriba: el labio oscuro y los dientes finos; el paladar encendido
    Mu = Mh @ vr.T(0, 0.75, -0.45)
    Z0, ZD = 0.35, 1.48
    _tronco(out, Mu, -0.3, ZD, (-1.0, 1.0, 0.0, 0.62), (-0.7, 0.7, 0.0, 0.5),
            {'lados': P['piel'], 'frente': P['piel'], 'abajo': P['encia']}, semilla=8)
    cubo(out, Mu, -0.5, -0.02, ZD - 0.04, 1.0, 0.12, 0.08, P['sombra'], semilla=9)                      # el labio
    _tapa(out, Mu, -0.04, 1.7, 1.15, Z0, ZD - 0.1, P['fauces'], semilla=10)
    _hilera(out, Mu, _planta(0.82, 0.55, Z0, ZD - 0.08, 0.25), -0.04, -0.3, P['colmillos'], semilla=11)
    # la de abajo, caida en el grito, con la barbilla en punta
    Ml = Mh @ vr.T(0, 0.7, -0.45) @ vr.Rx(26 * D)
    _tronco(out, Ml, -0.3, 1.4, (-0.95, 0.95, -0.55, 0.0), (-0.3, 0.3, -0.42, 0.0),
            {'lados': P['piel'], 'frente': P['piel'], 'abajo': P['piel'], 'arriba': P['encia']}, semilla=12)
    _tapa(out, Ml, 0.04, 1.6, 0.6, Z0, 1.38, P['fauces'], semilla=13)
    _hilera(out, Ml, _planta(0.78, 0.3, Z0, 1.36, 0.2), 0.04, 0.26, P['dientes'], semilla=14)
    cubo(out, Ml, -0.3, 0.0, 1.3, 0.6, 0.1, 0.1, P['sombra'], semilla=15)                               # el labio de abajo
    q0, q1 = punto(Ml, (-0.72, 0.04, Z0)), punto(Ml, (0.72, 0.04, Z0))
    q2, q3 = punto(Mu, (0.82, -0.04, Z0)), punto(Mu, (-0.82, -0.04, Z0))
    lamina(out, (q0, q1, q2, q3), P['garganta'], 1.64, float(np.linalg.norm(q3 - q0)), semilla=16)         # la garganta
    for s in (1, -1):                                                                                   # las comisuras
        a, b = punto(Mu, (s * 0.86, -0.02, Z0 - 0.1)), punto(Mu, (s * 0.76, -0.02, 0.95))
        c, d = punto(Ml, (s * 0.62, 0.0, 0.9)), punto(Ml, (s * 0.8, 0.0, Z0 - 0.1))
        lamina(out, (d, c, b, a), P['encia'], float(np.linalg.norm(b - a)), float(np.linalg.norm(c - b)), semilla=17)
    # los queliceros: salen de debajo de los pomulos y bajan junto a la boca, curvados hacia dentro
    for s in (1, -1):
        p = punto(Mh, (s * 1.05, 0.95, 0.7))
        tramos = (((s * 0.3, -1.0, 0.45), 0.34, 0.95), ((-s * 0.2, -1.0, 0.35), 0.27, 0.85), ((-s * 0.65, -0.6, 0.2), 0.17, 0.6))
        for j, (dd, g, l) in enumerate(tramos):
            dd = _dir(Mh, dd)
            dd = dd / np.linalg.norm(dd)
            q = p + dd * l
            _seg(out, p, q, g, g * 0.75, P['quelicero'] if j < 2 else P['punta'], semilla=20 + j)
            p = q


def melena(out, Mh, P, larga=1.0):
    """La melena larga, echada hacia atras para dejar la cara al aire: el volumen de arriba con la
    raya en medio, la nuca, dos mechones finos que caen por delante de los hombros y los mechones
    largos que caen por la espalda, cada uno con su onda."""
    _ovoide(out, Mh @ vr.T(0, 3.35, -0.8), 1.45, 0.58, 1.66, P['cabello'], semilla=30)                  # arriba
    _ovoide(out, Mh @ vr.T(0, 2.1, -1.8), 1.5, 1.6, 0.75, P['cabello'], semilla=31)                     # la nuca
    for s in (1, -1):                                                                                   # las sienes
        _ovoide(out, Mh @ vr.T(s * 1.3, 2.5, -0.55), 0.28, 0.95, 1.3, P['cabello'], semilla=32)
    for s in (1, -1):                                                                                   # por delante
        a = punto(Mh, (s * 1.22, 2.4, 1.06))
        b = punto(Mh, (s * 1.12, 0.6, 1.1))
        c = punto(Mh, (s * 1.5, -1.6, 0.9))
        e = punto(Mh, (s * 1.8, -3.6 * larga, 0.6))
        _seg(out, a, b, 0.2, 0.26, P['cabello'], semilla=33, achata=0.9)
        _seg(out, b, c, 0.26, 0.24, P['cabello'], semilla=34, achata=0.9)
        _seg(out, c, e, 0.24, 0.08, P['cabello'], semilla=34, achata=0.9)
    for j, x in enumerate((-1.25, -0.62, 0.0, 0.62, 1.25)):                                             # por la espalda
        a = punto(Mh, (x, 2.8, -2.0))
        b = punto(Mh, (x * 1.15, 0.0, -2.45))
        c = punto(Mh, (x * 1.3 + 0.25 * (j % 2 - 0.5), -2.6 * larga, -2.6))
        e = punto(Mh, (x * 1.45, -5.0 * larga, -2.4))
        _seg(out, a, b, 0.46, 0.46, P['cabello'], semilla=35 + j % 3, achata=0.55)
        _seg(out, b, c, 0.46, 0.36, P['cabello'], semilla=38 + j % 3, achata=0.55)
        _seg(out, c, e, 0.36, 0.1, P['cabello'], semilla=41 + j % 3, achata=0.55)


def corona(out, Mh, P):
    """La corona de la reina: dos pares de patas de arana que salen de lo alto de la cabeza, suben
    como cuernos y se doblan hacia fuera y atras, negras, con su rodilla y la punta encendida."""
    for s in (1, -1):
        for j, (x, alto, abre, g) in enumerate(((0.55, 2.3, 0.35, 0.24), (1.05, 1.7, 0.75, 0.2))):
            base = punto(Mh, (s * x, 3.5 - 0.15 * j, -0.4 - 0.2 * j))
            d1 = _dir(Mh, (s * abre, 1.0, 0.05))
            d1 = d1 / np.linalg.norm(d1)
            m = base + d1 * alto
            d2 = _dir(Mh, (s * (0.9 + abre), 0.15, -0.55))
            d2 = d2 / np.linalg.norm(d2)
            q = m + d2 * alto * 0.65
            _seg(out, base, m, g, g * 0.8, P['quelicero'], semilla=45 + j)
            bola(out, vr.T(*m), g * 1.05, P['quelicero'], semilla=48)
            _seg(out, m, q, g * 0.75, g * 0.35, P['quelicero'], semilla=49)
            cubo(out, vr.T(*q), -g * 0.55, -g * 0.55, -g * 0.55, g * 1.1, g * 1.1, g * 1.1, P['punta'], semilla=50)


# ----------------------------------------------------------------------
#  El torso de mujer
# ----------------------------------------------------------------------
def torso(out, P):
    """Las caderas de quitina que salen del cuerpo de la arana, la cintura estrecha, el corpino de
    quitina en placas con el busto, el escote y los hombros de piel, y el cuello largo."""
    q = {'arriba': P['quitina'], 'abajo': P['quitina'], 'lados': P['quitina'], 'frente': P['quitina'], 'atras': P['quitina']}
    c = {'lados': P['corpino'], 'arriba': P['corpino'], 'abajo': P['corpino']}
    pl = {'lados': P['piel'], 'arriba': P['piel'], 'abajo': P['piel'], 'frente': P['piel']}
    Mv = vr.T(0, 0, 2.6) @ vr.Rx(-90 * D)                  # sube: z local es arriba; y local es hacia atras
    _tronco(out, Mv, 6.2, 8.2, (-2.1, 2.1, -1.7, 1.7), (-1.3, 1.3, -1.0, 1.0), q, semilla=40)          # las caderas
    _tronco(out, Mv, 8.1, 9.6, (-1.28, 1.28, -0.98, 0.98), (-1.45, 1.45, -1.05, 1.05), c, semilla=41)  # la cintura
    _tronco(out, Mv, 9.5, 11.9, (-1.45, 1.45, -1.05, 1.05), (-1.8, 1.8, -1.15, 1.15), c, semilla=42)   # el corpino
    _tronco(out, Mv, 11.8, 12.9, (-1.8, 1.8, -1.1, 1.1), (-2.05, 2.05, -0.95, 0.95), pl, semilla=43)   # el escote
    for s in (1, -1):
        _ovoide(out, vr.T(s * 0.7, 11.05, 3.55), 0.72, 0.66, 0.55, P['corpino'], semilla=44)            # el busto
        bloque(out, vr.T(s * 2.05, 12.6, 2.6) @ vr.Rz(-s * 14 * D), 1.15, 0.85, 1.5, P['piel'], semilla=45)   # el hombro
    _seg(out, (0.0, 12.7, 2.6), (0.0, 13.8, 2.8), 0.4, 0.36, P['piel'], semilla=46)                      # el cuello


# ----------------------------------------------------------------------
#  El cuerpo de la arana
# ----------------------------------------------------------------------
C0 = np.array((0.0, 5.0, 0.6))
ANGULOS = (44.0, 76.0, 110.0, 144.0)


def cuerpo_arana(out, P, abdomen=1.0):
    """El cefalotorax redondo con su caparazon, la cintura y el abdomen grande en huevo, con su marca
    encendida en el lomo y las hileras detras."""
    c0 = C0
    _huevo(out, vr.T(*c0), 3.1, 1.7, 3.4, P['quitina'], semilla=50)
    cubo(out, vr.T(*(c0 + (0, 1.55, -0.3))), -2.1, 0.0, -2.2, 4.2, 0.3, 4.4, P['quitina'], caras={'arriba': P['caparazon']}, semilla=51)
    _seg(out, c0 + (0, 0.5, -2.9), c0 + (0, 1.4, -4.3), 0.8, 0.8, P['quitina'], semilla=52)                 # la cintura
    Ma = vr.T(*(c0 + np.array((0.0, 2.7 + 0.8 * (abdomen - 1), -8.0 - 1.8 * (abdomen - 1))))) @ vr.Rx(16 * D) @ vr.Ry(180 * D)
    perfil = _huevo(out, Ma, 4.4 * abdomen, 4.0 * abdomen, 5.6 * abdomen, P['abdomen'], semilla=53)
    for (z0, y0), (z1, y1) in zip(perfil[1:4], perfil[2:5]):                                            # la marca, encima
        w0, w1 = 4.4 * abdomen * y0 / (4.0 * abdomen) * 0.55, 4.4 * abdomen * y1 / (4.0 * abdomen) * 0.55
        lamina(out, (punto(Ma, (-w0, y0 + 0.04, z0)), punto(Ma, (w0, y0 + 0.04, z0)), punto(Ma, (w1, y1 + 0.04, z1)),
                     punto(Ma, (-w1, y1 + 0.04, z1))), P['marca'], 2 * max(w0, w1), float(np.hypot(z1 - z0, y1 - y0)), semilla=56)
    for j, x in enumerate((-0.6, 0.0, 0.6)):                                                            # las hileras
        p = punto(Ma, (x, -0.4, 5.6 * abdomen - 0.3))
        pua(out, em.marco(p, _dir(Ma, (x * 0.2, -0.3, 1.0))) @ vr.Rx(90 * D), 0.35, 1.0, P['quitina'], semilla=54 + j)
    return c0, Ma


def pata(out, P, s, k, c0, rodilla=None, tobillo=None, punta=None, semilla=0):
    """Una pata de arana, gruesa: la coxa, el femur que sube hasta la rodilla alta (a la altura de
    los hombros de la reina), la tibia que baja y el metatarso hasta la punta, cada tramo mas fino,
    con su anillo claro, las rodillas redondas y dos pinchos en el femur."""
    a = ANGULOS[k] * D
    d = np.array((s * math.sin(a), 0.0, math.cos(a)))
    base = c0 + d * 2.4 + np.array((0.0, 0.2, 0.0))
    coxa = c0 + d * 3.3 + np.array((0.0, 0.9, 0.0))
    alto = (13.6, 13.0, 12.2, 11.2)[k]
    rod = c0 + d * 6.2 + np.array((0.0, alto - c0[1], 0.0)) if rodilla is None else np.asarray(rodilla, float)
    tob = c0 + d * 9.2 + np.array((0.0, 5.0 - c0[1], 0.0)) if tobillo is None else np.asarray(tobillo, float)
    fin = c0 + d * 10.6 + np.array((0.0, -c0[1], 0.0)) if punta is None else np.asarray(punta, float)
    g = (1.0, 0.96, 0.92, 0.88)[k]
    _seg(out, base, coxa, 0.85 * g, 0.8 * g, P['quitina'], semilla=semilla)
    _seg(out, coxa, rod, 0.8 * g, 0.68 * g, P['pata'], semilla=semilla + 1)
    bola(out, vr.T(*rod), 0.76 * g, P['quitina'], semilla=semilla + 2)
    _seg(out, rod, tob, 0.64 * g, 0.52 * g, P['pata'], semilla=semilla + 3)
    bola(out, vr.T(*tob), 0.56 * g, P['quitina'], semilla=semilla + 4)
    _seg(out, tob, fin, 0.5 * g, 0.18 * g, P['pata'], semilla=semilla + 5)
    for t in (0.35, 0.65):                                                                               # dos pinchos en el femur
        p = coxa + (rod - coxa) * t
        pua(out, em.marco(p, d + np.array((0.0, 0.7, 0.0))) @ vr.Rx(90 * D), 0.16, 0.8, P['quitina'], semilla=semilla + 6)
    return rod, tob, fin


# ----------------------------------------------------------------------
#  Lo de cada tipo
# ----------------------------------------------------------------------
def tela_halo(out, P, centro, radio, n=10, semilla=0):
    """A: la tela redonda detras de ella, en sectores: cada uno con sus hilos y su espiral."""
    centro = np.asarray(centro, float)
    pts = []
    for j in range(n + 1):
        th = j * TAU / n + math.pi / 2
        pts.append(centro + np.array((math.cos(th) * radio, math.sin(th) * radio, -0.15 * math.sin(th))))
    for j in range(n):
        a, b = pts[j], pts[j + 1]
        lamina(out, (centro, centro, b, a), P['tela'], float(np.linalg.norm(b - a)), radio, semilla=semilla + j % 3)
    return pts


def velo(out, Mh, P, largo=7.5):
    """B: el velo negro, como una capucha: cubre lo alto de la cabeza, cae por los lados de la cara
    (por fuera del pelo) hasta mas abajo de los hombros y por la espalda; el borde de abajo, roto en
    picos y con el canto encendido."""
    bloque(out, Mh @ vr.T(0, 3.55, -0.45), 3.3, 1.0, 3.6, P['quitina'], semilla=63)                     # la toca
    for s in (1, -1):
        a, b = punto(Mh, (s * 1.62, 3.9, 1.15)), punto(Mh, (s * 1.62, 3.9, -2.3))
        c, d = punto(Mh, (s * 2.6, -largo, -3.4)), punto(Mh, (s * 2.5, -largo, 1.6))
        lamina(out, (d, c, b, a), P['velo'], float(np.linalg.norm(b - a)) * 1.3, largo + 3.9, semilla=60 + (s > 0))
    a, b = punto(Mh, (-1.62, 3.9, -2.3)), punto(Mh, (1.62, 3.9, -2.3))
    c, d = punto(Mh, (2.6, -largo, -3.4)), punto(Mh, (-2.6, -largo, -3.4))
    lamina(out, (d, c, b, a), P['velo'], 5.2, largo + 3.9, semilla=62)


def mechones(out, P, puntos, semilla=0):
    """C: mechones de vello en las patas y en el lomo."""
    for j, (p, d) in enumerate(puntos):
        p, d = np.asarray(p, float), np.asarray(d, float)
        d = d / np.linalg.norm(d)
        _seg(out, p, p + d * 0.9, 0.3, 0.08, P['vello'], semilla=semilla + j % 4)


# ======================================================================
#  HILANDRA
# ======================================================================
ESC_CABEZA = 1.75
ESC_CUERPO = 1.25
ESC_MUJER = 1.3                        # la reina, mas grande que la arana (se agranda desde las caderas)
ANCLA = np.array((0.0, 6.2, 2.6))
CABEZA = np.array((0.0, 14.45, 3.45))
MIRA = (0.0, -0.32, 1.0)


def hilandra(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    out = []
    q = []
    ppb = bm.PPB
    bm.PPB = ppb / ESC_CUERPO
    try:
        c0, Ma = cuerpo_arana(q, P, abdomen=1.25 if tipo == 'B' else 1.0)
        rodillas = {}
        for s in (1, -1):
            for k in range(4):
                if k == 0 and tipo in ('B', 'C'):                                                      # las de delante, alzadas
                    a = ANGULOS[0] * D
                    d = np.array((s * math.sin(a), 0.0, math.cos(a)))
                    rod = c0 + d * 5.8 + np.array((0.0, 15.6 - c0[1], 0.0))
                    tob = c0 + d * 8.2 + np.array((0.0, 19.0 - c0[1], 0.0)) + np.array((0.0, 0.0, 1.8))
                    fin = tob + np.array((s * 0.4, -1.8, 2.4))
                    rodillas[(s, k)] = pata(q, P, s, k, c0, rod, tob, fin, semilla=70 + 8 * k)[0]
                else:
                    rodillas[(s, k)] = pata(q, P, s, k, c0, semilla=70 + 8 * k)[0]
        q_arana = q
        q = []
        torso(q, P)
        hombro = {s: np.array((s * 2.2, 12.5, 2.6)) for s in (1, -1)}
        if tipo == 'A':                                                                                  # los brazos alzados
            for s in (1, -1):
                codo, mun = hombro[s] + (s * 1.8, 1.9, 0.5), hombro[s] + (s * 3.2, 4.5, 0.2)
                _brazo(q, hombro[s], codo, mun, (s * 0.45, 1.0, 0.05), (0.0, 0.0, 1.0), P, semilla=80)
        elif tipo == 'B':                                                                                # los brazos hacia ti
            for s in (1, -1):
                codo, mun = hombro[s] + (s * 0.9, -2.0, 1.4), hombro[s] + (s * 0.6, -2.4, 4.0)
                _brazo(q, hombro[s], codo, mun, (s * 0.25, 0.1, 1.0), (0.0, 1.0, 0.0), P, semilla=80)
        else:                                                                                            # cuatro brazos
            for s in (1, -1):
                codo, mun = hombro[s] + (s * 1.9, 1.4, 1.4), hombro[s] + (s * 2.2, 3.4, 3.4)
                _brazo(q, hombro[s], codo, mun, (s * 0.3, 0.6, 1.0), (0.0, 1.0, 0.0), P, semilla=80)
                h2 = np.array((s * 1.6, 10.4, 2.7))
                codo2, mun2 = h2 + (s * 1.4, -1.0, 1.4), h2 + (s * 1.2, -0.4, 3.8)
                _brazo(q, h2, codo2, mun2, (s * 0.2, 0.1, 1.0), (0.0, 1.0, 0.0), P, semilla=90, abre=0.7)
            pts = []
            for s in (1, -1):
                for k in range(4):
                    r = rodillas[(s, k)]
                    pts += [(r + (0, 0.5, 0), (s * 0.4, 1.0, -0.2)), (r + (s * 0.4, 0.2, 0.3), (s * 1.0, 0.6, 0.2))]
            for j in range(9):
                pts.append((punto(Ma, (-2.4 + 0.6 * j, 3.9, -1.0 + 0.3 * (j % 3))), (0.0, 1.0, -0.4)))
            mechones(q_arana, P, pts, semilla=100)
        if tipo == 'A':
            tela_halo(q, P, np.array((0.0, 16.4, 0.6)), 8.2, n=12, semilla=110)
    finally:
        bm.PPB = ppb
    Mmujer = vr.T(*ANCLA) @ np.diag([ESC_MUJER, ESC_MUJER, ESC_MUJER, 1.0]) @ vr.T(*(-ANCLA))
    out += qm.transformar(q_arana, np.diag([ESC_CUERPO, ESC_CUERPO, ESC_CUERPO, 1.0]))
    out += qm.transformar(q, np.diag([ESC_CUERPO, ESC_CUERPO, ESC_CUERPO, 1.0]) @ Mmujer)
    Hc = punto(Mmujer, CABEZA) * ESC_CUERPO
    cab = []
    Mh0 = em.marco(np.zeros(3), MIRA)
    ppb = bm.PPB
    bm.PPB = ppb / ESC_CABEZA
    try:
        cabeza(cab, Mh0, V, P)
        melena(cab, Mh0, P, larga=0.8 if tipo == 'C' else 1.0)
        if tipo == 'B':
            velo(cab, Mh0, P)
        else:
            corona(cab, Mh0, P)
    finally:
        bm.PPB = ppb
    Mpon = vr.T(*Hc) @ np.diag([ESC_CABEZA, ESC_CABEZA, ESC_CABEZA, 1.0])
    out += qm.transformar(cab, Mpon)
    Mh = Mpon @ Mh0
    return out, {'cabeza': Mh, 'boca': punto(Mh, (0.0, 0.2, 1.6))}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

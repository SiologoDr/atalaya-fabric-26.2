"""
Estudio de Ofidia (12-10-2026). Juan: «recrea igual a Ofidia, o hazle sub variantes; pon la
original y sus variantes para no copiarla como tal». Tras la primera version: «no son
iguales en modelo a Ofidia, que tiene boca de monstruo, cola... fijate bien como es». Y tras la
segunda: «no son manos o brazos, son alas lo que tiene; su boca es como triangular, revisa
bien su portada».

  Ofidia es la sirena-sierpe de la tercera dungeon de Dedsafio 4 (diseno de Eufonia Studio).
  Estudiada en el cartel, en el retrato de su barra y en la presentacion del directo del
  10-10-2026 (los fotogramas estan en el scratchpad, ded/intro6). Su forma de monstruo:

    - la cola: una sierpe de tambores de marmol azul con cinturones granates con remaches,
      que se enrosca en el suelo y se alza;
    - la cintura: un cinturon con remaches;
    - el torso: un costillar abierto que brilla rosa por dentro, con costillas blancas y la
      columna oscura de vertebras grises por delante;
    - dos alas: el hueso grueso de marmol sale del hombro, sube hasta el codo y se abre hasta la
      muneca, donde lleva un cubo rosa encendido; de el cuelga la membrana lisa azul noche, en
      hojas que acaban en pico (en vuelo, las alas son hojas largas echadas hacia atras);
    - la cabeza: una capucha puntiaguda de azul noche, una visera lila con una gema blanca
      que brilla, dos cuernos lila, una media luna lila, una espina rosa, un gancho negro con
      remaches turquesa y un tallo negro con muescas en la coronilla;
    - la boca, triangular: arriba la mandibula ancha con una cortina de colmillos planos rosas y
      blancos, con la punta en escalon; abajo una artesa en V de dos losas gruesas, abierta, con
      el interior encendido y los dientes rojos en escalon por los cantos: de frente, la boca es
      un triangulo; de lado, la losa oscura con los dientes rojos debajo del rosa;
    - tres cebos: el de arriba sale del tallo negro, sube y se dobla hacia atras, y los de los
      lados salen de la capucha y se doblan hacia atras y abajo; acaban en cubos rosas.

  Las variantes usan ese mismo cuerpo (cola, costillar, alas y boca) y cambian la forma de lo
  que la enmarca, el material y el neon:

    O  la original      solo para estudiarla (no va al mod)
    A  de la Capucha    la capucha se abre en una capucha de cobra con dos ojos falsos;
                        sin cebos; marmol de luna y hierro; azul hielo
    B  de los Faroles   los cebos se hacen faroles con almas: una corona en la cabeza, uno
                        a cada lado y otro colgando de cada ala; marmol pizarra y laton;
                        verde de almas
    C  Encadenada       cuernos de carnero, bozal de hierro roto, grilletes en las alas con
                        la cadena rota, cadenas en vez de cebos, barrotes en el pecho y
                        cadenas por la cola; marmol negro con vetas rojas; carmesi

Mismo oficio que Simara: cajas con las caras pintadas a 8 px por bloque, sin ruido.
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
from sierpe_modelo import _borde_de, _limpiar, _manchas, _bisel, _remaches, _degradado, lamina, bola, cadena

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 8

VARIANTES = {
    'O': dict(
        clave='O', nombre='la original',
        marmol=_r('1e1c5e', '2e2c8e', '4644bc', '6e6adc', 'a49cf2'),
        capucha=_r('080a20', '0e1234', '161c4a', '222a62', '323c80'),
        cinto=_r('240c20', '441836', '642850', '84386a', 'aa5c8a'),
        hueso=_r('5e4e94', '8e7ec6', 'b8acea', 'd8d0f8', 'f2eeff'),
        costilla=_r('a07890', 'd0a8c0', 'f0d8e6', 'fbeef4', 'ffffff'),
        colmillo=_r('a0285e', 'd8467e', 'ff78ac', 'ffb4d2', 'fff0f6'),
        diente_bajo=_r('520816', '84102a', 'b81a3c', 'dc3a5a', 'f46c88'),
        gancho=_r('06060c', '0e0e18', '181824', '242434', '343446'),
        remache='3ad6d0',
        trapo=_r('060818', '0c1028', '141a3a', '1e2650', '2a3468'),
        neon=('fff0f8', 'ff5ab4', '7a0a4a'),
    ),
    'A': dict(
        clave='A', nombre='de la Capucha',
        marmol=_r('3a4460', '5a6684', '8290ae', 'aebad2', 'dce4f2'),
        capucha=_r('060c18', '0c162a', '142240', '1e3058', '2c4274'),
        cinto=_r('0c0e16', '181c26', '282e3a', '3c4452', '566070'),
        hueso=_r('4a6680', '7894b0', 'a8c2d8', 'd0e2ee', 'f2f8fc'),
        costilla=_r('7890a8', 'a8c0d4', 'd4e4f0', 'ecf4fa', 'ffffff'),
        colmillo=_r('1e5486', '3a7ab0', '6ab0e0', 'aad8f6', 'f0faff'),
        diente_bajo=_r('16346a', '204a8c', '3668b2', '5688d2', '86b0ec'),
        gancho=_r('06080c', '0e1218', '181e26', '242c36', '343e4a'),
        remache='6ad8ff',
        trapo=_r('060c18', '0c1628', '14223a', '1e3050', '2a4268'),
        neon=('f2fbff', '6ad8ff', '0a4a7c'),
    ),
    'B': dict(
        clave='B', nombre='de los Faroles',
        marmol=_r('101a18', '1a2a28', '2a3e3a', '3e5850', '5a786e'),
        capucha=_r('060c0a', '0c1614', '142220', '1e302c', '2a423c'),
        cinto=_r('281a08', '4c3612', '78581e', 'a6802e', 'd4ac4c'),
        hueso=_r('4c5a4e', '74887a', '9eb4a2', 'c6d8c8', 'eaf4ea'),
        costilla=_r('7a9a84', 'a8c8b0', 'd2ecd8', 'ecf8ee', 'ffffff'),
        colmillo=_r('146a3a', '1e9452', '4ac87c', '96ecb4', 'f0fff4'),
        diente_bajo=_r('083818', '105828', '1c8842', '38b664', '68e68e'),
        gancho=_r('060a08', '0e1410', '18201a', '242e26', '343e36'),
        remache='6affa0',
        trapo=_r('060c0a', '0c1612', '14221c', '1e3028', '2a4236'),
        hierro=_r('0a0c0c', '141818', '1e2424', '2c3434', '3e4848'),
        neon=('f0fff4', '6affa0', '0a6a2a'),
    ),
    'C': dict(
        clave='C', nombre='Encadenada',
        marmol=_r('0a0608', '140c10', '201418', '2e1e24', '402a32'),
        capucha=_r('060406', '0e080c', '180e14', '24161e', '34202a'),
        cinto=_r('1c0c06', '381a0e', '582c16', '7c4224', 'a25e38'),
        hueso=_r('5a4a3a', '8a7660', 'b4a088', 'd8c8b0', 'f4ecdc'),
        costilla=_r('8a7a66', 'b8a68c', 'dccab0', 'f0e4d0', 'fffaf0'),
        colmillo=_r('8a1420', 'b81e2c', 'e84a54', 'ff8e90', 'fff0ec'),
        diente_bajo=_r('480a10', '781018', 'ae1a28', 'd63a46', 'f26a72'),
        gancho=_r('0e0c0c', '1c1818', '2c2626', '403838', '5a5050'),
        remache='ff3a4a',
        trapo=_r('180608', '2a0c10', '40141a', '581e26', '762a34'),
        hierro=_r('0e0c0c', '1c1818', '2c2626', '403838', '5a5050'),
        neon=('fff0ec', 'ff3a4a', '7a0a14'),
    ),
}


def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'ofi%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def marmol(tw, th, cara, s):
        """El marmol de la cola y los brazos: manchas grandes y claras de borde limpio (en la C,
        negro con vetas rojas que brillan, como curvas de nivel)."""
        idx = _manchas(tw, th, s, celda=6.5, umbral=0.56, alto=0.8)
        tex = _imagen(_bisel(idx), V['marmol'])
        if k == 'C':
            v = bm._ruido(tw, th, s + 11, 9.0)
            veta = _limpiar((np.abs(v - 0.5) < 0.03).astype(int), 1).astype(bool)
            if veta.any():
                c1, c2 = nm._hex(nuc), nm._hex(neo)
                tex[_borde_de(veta)] = (*qm._mezcla(V['marmol'][1], c2, 0.35), 255)
                tex[veta] = (*c2, 255)
                tex[veta & (np.abs(v - 0.5) < 0.01)] = (*c1, 255)
                return tex, _emis(tex, veta, 200)
        return tex, None
    reg('marmol', marmol)

    def capucha(tw, th, cara, s):
        """La capucha: azul noche con manchas suaves y el canto un poco mas claro."""
        idx = _manchas(tw, th, s + 5, celda=7.0, umbral=0.6, alto=0.86)
        idx = np.array([1, 2, 2, 3, 3])[idx]
        return _imagen(_bisel(idx), V['capucha']), None
    reg('capucha', capucha)

    def cinto(tw, th, cara, s):
        """Los cinturones: el canto claro, la sombra y una fila de remaches de 2 x 2."""
        idx = np.full((th, tw), 2)
        if cara in ('der', 'izq'):
            idx[:, 0] = 3
            idx[:, -1] = 1
        else:
            idx[0, :] = 3
            idx[-1, :] = 1
        return _imagen(_remaches(idx, cara), V['cinto']), None
    reg('cinto', cinto)

    def hueso(tw, th, cara, s):
        """El hueso lila de la visera, los cuernos y la media luna: liso, con su canto y una
        veta mas clara."""
        idx = np.full((th, tw), 2)
        if tw >= 4 and cara in ('der', 'izq', 'frente', 'atras'):
            idx[:, 1] = 3
        if th >= 4 and cara in ('arriba', 'abajo'):
            idx[1, :] = 3
        return _imagen(_bisel(idx), V['hueso']), None
    reg('hueso', hueso)

    def gema(tw, th, cara, s):
        return qm._emisivo('ffffff', nuc, max(2, tw), max(2, th)), None
    reg('gema', gema, pleno=True)

    def colmillo(tw, th, cara, s):
        """Los colmillos largos de arriba: el neon con una raya blanca a lo largo y la punta
        clara; brillan un poco, como en Ofidia."""
        idx = np.full((th, tw), 2)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 1
        if th >= 4:
            idx[-2:, :] = np.maximum(idx[-2:, :], 3)
        tex = _imagen(idx, V['colmillo'])
        return tex, _emis(tex, idx >= 2, 150)
    reg('colmillo', colmillo)

    def diente_bajo(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if tw >= 2:
            idx[:, 0] = 3
            idx[:, -1] = 1
        if th >= 3:
            idx[0, :] = 4
        return _imagen(idx, V['diente_bajo']), None
    reg('diente_bajo', diente_bajo)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def nucleo(tw, th, cara, s):
        """El fondo de la garganta: un resplandor redondo, blanco en el centro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        dentro = r < 1.0
        col = np.where((r < 0.45)[..., None], np.array(c_n),
                       np.where((r < 0.75)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m)))
        col = np.where(((r > 0.9) & dentro)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = np.where(dentro, 255, 0)
        return t, _emis(t, dentro & (r < 0.9), 240)
    reg('nucleo', nucleo)

    def boca(tw, th, cara, s):
        """El interior de la mandibula de abajo, en triangulo: bandas en V del neon, hondas en los
        bordes y casi blancas en el centro, como el corazon rosa que se ve de frente."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        u = (xs + 0.5) / tw
        dd = np.minimum(u, 1 - u) * 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((dd < 0.2)[..., None], np.array(c_h),
                       np.where((dd < 0.46)[..., None], np.array(qm._mezcla(c_h, c_m, 0.6)),
                                np.where((dd < 0.76)[..., None], np.array(c_m), np.array(qm._mezcla(c_m, c_n, 0.65)))))
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        if th >= 6:
            t[:2, :, :3] = np.array(c_h)
        return t, _emis(t, dd >= 0.2, 235)
    reg('boca', boca)

    def pecho(tw, th, cara, s):
        """Lo de dentro del costillar: el neon en escalones, mas claro en el centro y hondo en
        los bordes, con lineas horizontales suaves."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        u = np.abs(xs - (tw - 1) / 2) / max((tw - 1) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        t = np.zeros((th, tw, 4), np.uint8)
        col = np.where((u < 0.35)[..., None], np.array(qm._mezcla(c_m, c_n, 0.45)),
                       np.where((u < 0.75)[..., None], np.array(c_m), np.array(qm._mezcla(c_h, c_m, 0.5))))
        col = np.where(((ys % 4) == 3)[..., None], np.array(qm._mezcla(c_h, c_m, 0.55)), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, np.ones((th, tw), bool), 170)
    reg('pecho', pecho)

    def costilla(tw, th, cara, s):
        idx = np.full((th, tw), 3)
        if th >= 3:
            idx[0, :] = 4
            idx[-1, :] = 1
        if tw >= 3 and cara in ('der', 'izq'):
            idx[:, -1] = 2
        tex = _imagen(idx, V['costilla'])
        return tex, _emis(tex, idx >= 3, 70)
    reg('costilla', costilla)

    def columna(tw, th, cara, s):
        """La columna del pecho: oscura, con las vertebras como cuadrados grises."""
        idx = np.full((th, tw), 1)
        ys, xs = np.mgrid[0:th, 0:tw]
        if tw >= 4:
            vert = ((ys % 6) >= 1) & ((ys % 6) <= 2) & (np.abs(xs - (tw - 1) / 2) < 1.2)
            idx = np.where(vert, 3, idx)
        return _imagen(_bisel(idx), V['gancho']), None
    reg('columna', columna)

    def cebo(tw, th, cara, s):
        return qm._emisivo('fff4fa' if k == 'O' else nuc, neo, max(2, tw), max(2, th)), None
    reg('cebo', cebo, pleno=True)

    def banda(tw, th, cara, s):
        t = qm._emisivo(nuc, neo, max(2, tw), max(2, th))
        return t, None
    reg('banda', banda, pleno=True)

    def vara(tw, th, cara, s):
        """Las varillas de los cebos: azul con manchas lila que se aclaran hasta el blanco,
        y brillan un poco."""
        idx = _manchas(tw, th, s + 21, celda=3.0, umbral=0.5, alto=0.72)
        idx = np.array([2, 2, 2, 3, 4])[idx]
        tex = _imagen(_bisel(idx, luz=0, sombra=1), V['marmol'])
        return tex, _emis(tex, idx >= 4, 110)
    reg('vara', vara)

    def gancho(tw, th, cara, s):
        """El gancho negro: liso, con remaches de 2 x 2 del color de su neon."""
        idx = np.full((th, tw), 2)
        tex = _imagen(_bisel(idx), V['gancho'])
        ys, xs = np.mgrid[0:th, 0:tw]
        m = ((ys % 5) < 2) & ((xs % 5) < 2) & (ys > 0) & (xs > 0) & (ys < th - 1) & (xs < tw - 1)
        if m.any():
            tex[m] = (*nm._hex(V['remache']), 255)
            return tex, _emis(tex, m, 160)
        return tex, None
    reg('gancho', gancho)

    def trapo(tw, th, cara, s):
        """Los jirones de las mangas y la falda: pliegues de tres pixeles con la cresta mas
        clara y el borde de abajo deshecho en tiras."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs // 3) % 2) == 0, 2, 1)
        idx = np.where((xs % 6) == 0, 3, idx)
        rng = random.Random(s)
        cortes = np.array([rng.randint(0, max(1, th // 3)) for _ in range((tw + 1) // 2)])
        cortes = np.repeat(cortes, 2)[:tw]
        fin = th - 1 - cortes[None, :]
        idx = np.where(ys > fin - 2, 0, idx)
        img = _imagen(idx, V['trapo'])
        dentro = ys <= fin
        t[dentro] = img[dentro]
        return t, None
    reg('trapo', trapo)

    def ala(tw, th, cara, s):
        """La membrana del ala: lisa, azul noche con manchas de marmol mas claras; el canto que va
        pegado al hueso, claro, y hacia la punta cada vez mas oscura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        m = _manchas(tw, th, s + 31, celda=6.5, umbral=0.58, alto=0.8)
        idx = np.array([0, 1, 1, 2, 3])[m]
        v = ys / max(th - 1, 1)                           # 0 en el hueso, 1 en la punta
        idx = np.where(v > 0.55, np.maximum(idx - 1, 0), idx)
        if th >= 4:
            idx[0, :] = 4
            idx[1, :] = np.maximum(idx[1, :], 3)
        tex = _imagen(idx, V['trapo'])
        tex[..., 3] = 255
        return tex, None
    reg('ala', ala)

    if k == 'O':
        def espina(tw, th, cara, s):
            idx = np.full((th, tw), 3)
            if tw >= 3:
                idx[:, 0] = 4
                idx[:, -1] = 1
            tex = _imagen(idx, V['colmillo'])
            return tex, _emis(tex, idx >= 3, 140)
        reg('espina', espina)

    if k == 'A':
        def cobra(tw, th, cara, s):
            """La capucha de cobra: un ovalo de membrana en bandas, con el canto encendido y dos
            ojos falsos arriba (anillo claro, hueco oscuro y la pupila de luz)."""
            t = np.zeros((th, tw, 4), np.uint8)
            ys, xs = np.mgrid[0:th, 0:tw].astype(float)
            cx, cy = (tw - 1) / 2, th * 0.56
            r = np.hypot((xs - cx) / (tw * 0.5), (ys - cy) / (th * 0.56))
            dentro = r < 1.0
            idx = np.where(r > 0.8, 3, np.where(r > 0.55, 2, 1))
            img = _imagen(idx, V['capucha'])
            filo = dentro & (r > 0.93)
            img[filo] = (*nm._hex(neo), 255)
            brillo = filo.copy()
            if cara == 'frente':
                for sx in (-1, 1):
                    ex, ey = cx + sx * tw * 0.31, th * 0.27
                    e = np.hypot((xs - ex) / (tw * 0.11), (ys - ey) / (th * 0.1))
                    img[e < 1.0] = (*V['hueso'][4], 255)
                    img[e < 0.72] = (*V['capucha'][0], 255)
                    anillo = (e >= 0.38) & (e < 0.5)
                    img[anillo] = (*nm._hex(neo), 255)
                    img[e < 0.38] = (*nm._hex(nuc), 255)
                    brillo |= (e < 0.5)
            t[dentro] = img[dentro]
            return t, _emis(t, brillo & dentro, 220)
        reg('cobra', cobra)

    if k in ('B', 'C'):
        def hierro(tw, th, cara, s):
            return _imagen(_bisel(np.full((th, tw), 2)), V['hierro']), None
        reg('hierro', hierro)

    if k == 'C':
        def oxido(tw, th, cara, s):
            idx = np.full((th, tw), 3)
            if tw >= 3:
                idx[:, 0] = 4
                idx[:, -1] = 1
            return _imagen(idx, V['cinto']), None
        reg('oxido', oxido)
    return P


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def _dir(M, d):
    """Un vector del marco M pasado al mundo."""
    return punto(M, d) - punto(M, (0, 0, 0))


def _ruta(out, p, tramos, M, grueso, pintor, semilla=0, afina=0.1):
    """Una varilla de tramos rectos (dados en el marco M) que empieza en p; devuelve la punta."""
    p = np.asarray(p, float)
    for j, d in enumerate(tramos):
        q = p + _dir(M, d)
        g = grueso * (1 - afina * j)
        viga(out, p, q, g, g, pintor, extra=g / 2, semilla=semilla + j)
        p = q
    return p


def _cubo_diamante(out, p, lado, pintor, semilla=0, giro=0.0):
    """Un cubo girado para que se vea de pico (como los cebos de Ofidia)."""
    M = vr.T(*p) @ vr.Ry((45 + giro) * D) @ vr.Rx(35 * D) @ vr.Rz(45 * D)
    cubo(out, M, -lado / 2, -lado / 2, -lado / 2, lado, lado, lado, pintor, semilla=semilla)


def _jirones(out, a, b, largo, P, semilla=0, vuelo=(0.0, 0.0, 0.0)):
    """Un jiron que cuelga de la linea a-b, con su borde de abajo deshecho."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    abajo = np.array((vuelo[0], -largo, vuelo[2]))
    lamina(out, (a + abajo, b + abajo * 0.9, b, a), P['trapo'], float(np.linalg.norm(b - a)), largo, semilla)


# ----------------------------------------------------------------------
#  La cola: tambores de marmol con su cinturon, enroscada en el suelo y alzandose
# ----------------------------------------------------------------------
COLA = [(8.6, 0.55, -7.8), (5.2, 0.9, -10.2), (0.4, 1.25, -10.4), (-3.8, 1.55, -7.6), (-4.8, 1.8, -3.4),
        (-2.8, 2.1, 0.0), (-0.6, 4.0, 0.9), (0.1, 7.2, 0.6), (0.0, 10.2, 0.0)]


def cola(out, V, P):
    pts = sm._por_longitud(COLA, 2.3)
    marcos = sm._marcos(pts, (0, 1, 0))
    n = len(marcos)
    for i, M in enumerate(marcos):
        t = i / max(n - 1, 1)
        r = 0.5 + 1.75 * t ** 0.6
        L = float(np.linalg.norm(pts[i + 1] - pts[i]))
        cubo(out, M, -r, -r, -0.15, 2 * r, 2 * r, L + 0.3, P['marmol'], semilla=i)
        if i > 0:
            rb = r * 1.16
            cubo(out, M @ vr.T(0, 0, -0.28), -rb, -rb, 0, 2 * rb, 2 * rb, 0.56, P['cinto'], semilla=i)
        if V['clave'] == 'C' and i % 2 == 1 and 0.25 < t < 0.95:          # cadenas que cruzan el tambor
            for s in (1, -1):
                cadena(out, punto(M, (-s * r * 1.08, r * 1.08, 0.3)), punto(M, (s * r * 1.08, r * 1.08, L - 0.3)), 0.9,
                       P['oxido'], semilla=i)
    pua(out, marcos[0] @ vr.Rx(-90 * D), 0.42, 1.8, P['marmol'], semilla=99)        # la punta de la cola
    return pts


# ======================================================================
#  OFIDIA
# ======================================================================
def ofidia(variante='O'):
    V = VARIANTES[variante]
    P = pintores(V)
    k = V['clave']
    out = []
    cola(out, V, P)
    cubo(out, vr.T(0, 10.3, 0.0), -2.6, -0.4, -2.6, 5.2, 0.8, 5.2, P['cinto'], semilla=1)         # el cinturon de la cintura

    # el torso: el costillar abierto, que brilla por dentro
    Mt = vr.T(0, 12.9, 0.2) @ vr.Rx(6 * D) @ np.diag([1.1, 1.05, 1.1, 1.0])
    cubo(out, Mt, -2.2, -2.3, -1.1, 4.4, 4.6, 2.3, None, caras={'frente': P['pecho'], 'der': P['pecho'], 'izq': P['pecho'],
                                                                'arriba': P['pecho'], 'abajo': P['pecho']}, semilla=2)
    cubo(out, Mt, -2.45, -2.4, -1.75, 4.9, 4.8, 0.85, P['marmol'], semilla=3)                     # la espalda
    cubo(out, Mt, -0.4, -2.45, 1.0, 0.8, 4.9, 0.5, P['columna'], semilla=4)                       # la columna
    for j, y in enumerate((1.55, 0.6, -0.35, -1.3)):
        for s in (1, -1):
            p0 = punto(Mt, (s * 0.35, y, 1.25))
            p1 = punto(Mt, (s * 2.35, y - 0.3, 1.25))
            p2 = punto(Mt, (s * 2.35, y - 0.85, -1.2))
            viga(out, p0, p1, 0.36, 0.36, P['costilla'], extra=0.12, semilla=5 + j)
            viga(out, p1, p2, 0.36, 0.36, P['costilla'], extra=0.12, semilla=9 + j)
    cubo(out, Mt, -2.55, 2.2, -1.75, 5.1, 0.55, 3.3, P['cinto'], semilla=13)                      # el cuello del costillar
    if k == 'C':                                                                                  # barrotes: el pecho es una celda
        for x in (-1.6, -0.95, 0.95, 1.6):
            viga(out, punto(Mt, (x, 2.2, 1.55)), punto(Mt, (x, -2.4, 1.55)), 0.24, 0.24, P['oxido'], semilla=14)
        for y in (1.1, -1.0):
            viga(out, punto(Mt, (-2.3, y, 1.6)), punto(Mt, (2.3, y, 1.6)), 0.22, 0.22, P['oxido'], semilla=15)

    # las dos alas, abiertas a los lados
    for s in (1, -1):
        ala(out, s, V, P)

    # el cuello y la cabeza
    viga(out, np.array((0, 15.2, 0.3)), np.array((0, 18.0, 1.6)), 2.0, 2.0, P['marmol'], extra=0.3, semilla=40)
    cubo(out, em.marco(np.array((0, 16.4, 0.85)), (0, 2.8, 1.3)), -1.2, -1.2, -0.3, 2.4, 2.4, 0.6, P['cinto'], semilla=41)
    Mh = em.marco(np.array((0.0, 20.0, 3.3)), (0.0, -0.58, 1.0)) @ np.diag([1.3, 1.3, 1.3, 1.0])
    cabeza(out, Mh, V, P)
    if k == 'O':
        _corona_original(out, Mh, P)
    elif k == 'A':
        _corona_capucha(out, Mh, P)
    elif k == 'B':
        _corona_faroles(out, Mh, P)
    else:
        _corona_encadenada(out, Mh, P)
    return out, {'cabeza': Mh}


def ala(out, s, V, P):
    """Un ala, como en el cartel y en el vuelo: el hueso grueso de marmol sale del hombro, sube
    hasta el codo y se abre hasta la muneca, donde lleva un cubo encendido; de el cuelga la
    membrana lisa, en hojas que acaban en pico (el borde de abajo, roto en picos)."""
    k = V['clave']
    raiz = np.array((s * 2.7, 16.0, -0.7))
    codo = np.array((s * 7.4, 18.4, -1.9))
    muneca = np.array((s * 12.8, 17.4, -3.2))
    cubo(out, vr.T(*raiz), -1.0, -0.9, -1.1, 2.0, 1.8, 2.2, P['gancho'], semilla=20)               # el hombro, con remaches
    viga(out, raiz, codo, 1.55, 1.45, P['marmol'], extra=0.35, semilla=21)
    viga(out, codo, muneca, 1.2, 1.1, P['marmol'], extra=0.3, semilla=22)
    bola(out, vr.T(*codo), 0.95, P['marmol'], semilla=23)
    d = (muneca - codo) / np.linalg.norm(muneca - codo)
    if k == 'B':                                                                                  # en la punta, un farol
        _cubo_diamante(out, muneca + d * 0.4, 1.0, P['cebo'], semilla=24)
        cadena(out, muneca + np.array((0, -0.5, 0)), muneca + np.array((0, -2.2, 0)), 0.45, P['hierro'], semilla=31)
        farol(out, muneca + np.array((0, -2.35, 0)), P, semilla=32, g=0.6)
    else:
        _cubo_diamante(out, muneca + d * 0.55, 1.4, P['cebo'], semilla=24, giro=s * 15)
    # la membrana: una sola tela que cuelga del hueso; el borde de abajo va en dientes de sierra
    # (puntas largas y muescas), como la de Ofidia
    huesos = []
    for t in np.linspace(0, 1, 11):
        if t <= 0.5:
            p = raiz + (codo - raiz) * (t / 0.5)
        else:
            p = codo + (muneca - codo) * ((t - 0.5) / 0.5)
        huesos.append(p + np.array((0, -0.55, 0.0)))
    huesos.append(muneca + d * 1.2)
    borde = []
    for i, h in enumerate(huesos):
        t = i / (len(huesos) - 1)
        caida = 7.4 - 5.6 * t                          # junto al cuerpo cuelga mucho; en la punta, poco
        if i % 2 == 1:
            caida *= 0.62                              # las muescas
        borde.append(h + np.array((s * 0.25 * t, -caida, -1.2 - 1.4 * t)))
    for i in range(len(huesos) - 1):
        a, b = huesos[i], huesos[i + 1]
        ea, eb = borde[i], borde[i + 1]
        lamina(out, (ea, eb, b, a), P['ala'], float(np.linalg.norm(b - a)), float(np.linalg.norm(ea - a)), 25 + i + 20 * (s > 0))
    if k == 'C':                                                                                  # grilletes en el hueso, con la cadena rota
        for p, dd in (((raiz + codo) / 2, codo - raiz), (codo * 0.45 + muneca * 0.55, muneca - codo)):
            M = em.marco(p, dd)
            cubo(out, M, -1.05, -1.0, -0.35, 2.1, 2.0, 0.7, P['oxido'], semilla=33)
            cadena(out, p + np.array((0, -0.95, 0)), p + np.array((s * 0.3, -4.4, 0.4)), 0.75, P['oxido'], semilla=34)


def colmillo(out, M, ancho, largo, grueso, pintor, semilla=0):
    """Un colmillo plano de dos escalones que cuelga a lo largo de -y local: la hoja y la punta,
    como los de Ofidia (rectangulares, con la punta en escalon)."""
    cubo(out, M, -ancho / 2, -largo * 0.66, -grueso / 2, ancho, largo * 0.66, grueso, pintor, semilla=semilla)
    cubo(out, M, -ancho * 0.36, -largo, -grueso * 0.4, ancho * 0.56, largo * 0.36, grueso * 0.8, pintor, semilla=semilla + 1)


def cabeza(out, Mh, V, P):
    """La cabeza: la capucha puntiaguda, la visera lila con su gema, la mandibula de arriba con
    la cortina de colmillos y la de abajo en cuña, en V, de modo que la boca abierta es un
    triangulo encendido por dentro."""
    k = V['clave']
    # la capucha, que acaba en pico hacia atras
    cubo(out, Mh, -2.05, -0.5, -3.0, 4.1, 2.7, 3.8, P['capucha'], semilla=1)
    if k != 'A':
        for j, (w, y, z, ang) in enumerate(((3.9, 2.1, -1.3, -16), (3.0, 3.0, -1.8, -22), (2.0, 3.85, -2.3, -30),
                                            (1.1, 4.6, -2.9, -38), (0.5, 5.2, -3.5, -46))):
            cubo(out, Mh @ vr.T(0, y, z) @ vr.Rx(ang * D), -w / 2, -0.1, -w * 0.5, w, 1.0, w, P['capucha'], semilla=2 + j)
    for s in (1, -1):                                                                              # los faldones de la capucha
        x0 = 2.0 if s > 0 else -2.4
        cubo(out, Mh, x0, -1.9, -3.0, 0.4, 3.9, 3.4, P['capucha'], semilla=6)
    # la visera: el bloque de delante, lila, con la gema en medio; por debajo, el paladar encendido
    cubo(out, Mh, -2.15, -0.55, 0.2, 4.3, 2.35, 2.7, P['hueso'], caras={'abajo': P['fauces'], 'arriba': P['marmol']}, semilla=7)
    cubo(out, Mh, -2.18, -0.55, 2.84, 4.36, 0.42, 0.1, P['capucha'], semilla=8)                    # la banda oscura de abajo
    cubo(out, Mh, -0.32, 1.8, -1.8, 0.64, 0.42, 2.7, P['hueso'], semilla=11)                       # la cresta
    cubo(out, Mh @ vr.T(0, 0.95, 2.91) @ vr.Rz(45 * D), -0.4, -0.4, 0, 0.8, 0.8, 0.08, P['gema'], semilla=9)
    for j in range(8):                                                                             # los colmillos de delante
        x = -1.75 + j * 0.5
        colmillo(out, Mh @ vr.T(x, -0.5, 2.72), 0.42, 0.8 + 0.28 * (j % 2), 0.16, P['colmillo'], semilla=12 + j)
    for s in (1, -1):                                                                              # los de los lados
        for j in range(3):
            M = Mh @ vr.T(s * 1.98, -0.5, 0.75 + j * 0.7) @ vr.Ry(90 * D)
            colmillo(out, M, 0.5, 0.75 + 0.25 * ((j + 1) % 2), 0.16, P['colmillo'], semilla=20 + j)
    # la mandibula de abajo: cuelga casi vertical y se estrecha en escalones hasta la barbilla, asi
    # que de frente la boca es un triangulo rosa; los dientes rojos van en escalon por los bordes
    Mj = Mh @ vr.T(0, -0.5, 1.95) @ vr.Rx(62 * D)
    z = 0.0
    for j, (mitad, largo) in enumerate(((2.0, 0.95), (1.6, 0.9), (1.15, 0.85), (0.74, 0.8), (0.37, 0.6))):
        cubo(out, Mj, -mitad, -0.9, z, 2 * mitad, 0.9, largo, P['marmol'], caras={'arriba': P['fauces']}, semilla=33 + j)
        for lado in (1, -1):                                                                         # dos dientes por escalon
            for q in range(2):
                M = Mj @ vr.T(lado * (mitad - 0.14), 0, z + 0.2 + q * (largo - 0.42))
                alto = 0.3 + 0.1 * ((j + q) % 2)
                cubo(out, M, -0.11, 0, -0.15, 0.22, alto, 0.3, P['diente_bajo'], semilla=40 + j)
                cubo(out, M, -0.08, alto, -0.15, 0.16, 0.16, 0.17, P['diente_bajo'], semilla=46 + j)
        z += largo
    cubo(out, Mj, -0.34, -0.9, z, 0.68, 0.65, 0.3, P['marmol'], semilla=52)                      # la punta de la barbilla
    ti, td, pu = punto(Mj, (-2.0, 0.06, 0.0)), punto(Mj, (2.0, 0.06, 0.0)), punto(Mj, (0.0, 0.06, z + 0.1))
    e = _dir(Mj, (0.2, 0, 0))
    lamina(out, (pu - e, pu + e, td, ti), P['boca'], 4.0, z, 53)                                   # el triangulo rosa de dentro
    # al fondo de la boca, la garganta que brilla
    Mv = em.marco(punto(Mh, (0.0, -0.95, 0.55)), _dir(Mh, (0.0, 0.1, 1.0)))
    cubo(out, Mv, -1.15, -1.15, 0, 2.3, 2.3, 0.05, None, caras={'frente': P['nucleo']}, semilla=49)
    if k == 'C':
        return
    # los dos cuernos lila de la visera
    for s in (1, -1):
        p = punto(Mh, (s * 1.55, 1.75, 0.9))
        pua(out, em.marco(p, _dir(Mh, (s * 0.5, 1.0, -0.25))) @ vr.Rx(90 * D), 0.26, 3.2, P['hueso'], semilla=50)


def _media_luna(out, Mh, P, x=1.15):
    """La media luna lila de la coronilla: una hoja curva que sube hacia atras y se dobla
    hacia delante."""
    p = punto(Mh, (x, 2.3, -1.9))
    for j, (d, w) in enumerate((((0, 1.0, -0.45), 0.75), ((0, 1.0, 0.15), 0.62), ((0, 0.45, 0.9), 0.48),
                                 ((0, -0.2, 1.0), 0.32))):
        q = p + _dir(Mh, d) * 0.95
        viga(out, p, q, w, 0.22, P['hueso'], arriba=_dir(Mh, (1, 0, 0)), extra=0.08, semilla=51 + j)
        p = q


def _gancho_negro(out, Mh, P, s=1):
    """El gancho negro con remaches: sale de un lado de la cabeza, sube y se dobla."""
    p = punto(Mh, (s * 2.2, 1.3, -1.3))
    _ruta(out, p, ((s * 1.3, 0.0, 0.0), (0.0, 2.2, -0.2), (-s * 0.1, 0.0, 0.9)), Mh, 0.72, P['gancho'], semilla=55, afina=0.05)


def _tallo_negro(out, Mh, P):
    """El tallo negro de la coronilla, con sus muescas: de su punta sale el cebo de arriba."""
    base = punto(Mh, (-0.1, 2.5, -1.3))
    tope = _ruta(out, base, ((0.0, 2.3, -0.1),), Mh, 0.95, P['gancho'], semilla=60)
    for j in range(3):
        p = base + _dir(Mh, (0.0, 0.55 + j * 0.62, -0.05))
        viga(out, p - _dir(Mh, (0.78, 0, 0)), p + _dir(Mh, (0.78, 0, 0)), 0.32, 0.32, P['gancho'], semilla=61)
    return tope


def _cebos(out, Mh, P, tope, final=None):
    """Los tres cebos: el de arriba sale del tallo negro, sube y se dobla hacia atras; los de los
    lados salen de la capucha, se abren y se doblan hacia atras y abajo. Cada uno acaba en un
    cubo encendido (o en lo que diga 'final')."""
    puntas = [_ruta(out, tope, ((0.0, 1.5, -0.2), (-2.4, 0.5, -1.4), (-0.2, -1.0, -0.2)), Mh, 0.42, P['vara'], semilla=62,
                    afina=0.06)]
    for s in (1, -1):
        base = punto(Mh, (s * 2.1, 1.1, -1.4))
        puntas.append(_ruta(out, base, ((s * 1.3, 0.5, -0.2), (s * 0.5, 0.1, -2.4), (s * 0.2, -1.8, -0.4)), Mh, 0.36, P['vara'],
                            semilla=66 + (s > 0) * 3, afina=0.06))
    for j, p in enumerate(puntas):
        lado = 1.45 if j == 0 else 1.25
        if final:
            final(p, j)
        else:
            _cubo_diamante(out, p + _dir(Mh, (0, -lado * 0.45, 0)), lado, P['cebo'], semilla=72 + j, giro=j * 20)


def _corona_original(out, Mh, P):
    _media_luna(out, Mh, P)
    _gancho_negro(out, Mh, P, 1)
    _cebos(out, Mh, P, _tallo_negro(out, Mh, P))
    p = punto(Mh, (0.9, 2.4, -0.6))                                                # la espina rosa
    pua(out, em.marco(p, _dir(Mh, (0.4, 1.0, -0.1))) @ vr.Rx(90 * D), 0.3, 2.4, P['espina'], semilla=75)


def _corona_capucha(out, Mh, P):
    # la capucha de cobra: un ovalo de membrana detras de la cabeza, con sus varillas detras
    Mc = Mh @ vr.T(0, 2.0, -3.1) @ vr.Rx(-12 * D)
    cubo(out, Mc, -5.6, -4.4, 0, 11.2, 9.8, 0.08, None, caras={'frente': P['cobra'], 'atras': P['cobra']}, semilla=80)
    raiz = punto(Mc, (0, -3.9, -0.15))
    for j in range(9):
        phi = math.radians(-84 + j * 21)
        fin = punto(Mc, (math.sin(phi) * 5.2, 1.1 + math.cos(phi) * 4.9, -0.15))
        viga(out, raiz, fin, 0.24, 0.24, P['gancho'], semilla=81)
    for s in (1, -1):                                                              # dos ganchos cortos
        _ruta(out, punto(Mh, (s * 2.2, 1.0, -0.8)), ((s * 0.9, 0.3, 0.0), (0.0, 1.2, 0.3)), Mh, 0.5, P['gancho'], semilla=82)


def farol(out, p, P, semilla=0, g=0.5):
    """Un farol de hierro con un alma encendida dentro."""
    Mf = vr.T(*p)
    cubo(out, Mf, -g, -2.4 * g, -g, 2 * g, 0.16, 2 * g, P['hierro'], semilla=semilla)
    cubo(out, Mf, -g, -0.16, -g, 2 * g, 0.16, 2 * g, P['hierro'], semilla=semilla)
    for (x, z) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        cubo(out, Mf, x * g * 0.86 - 0.07, -2.4 * g, z * g * 0.86 - 0.07, 0.14, 2.4 * g, 0.14, P['hierro'], semilla=semilla + 1)
    cubo(out, Mf, -g * 0.62, -2.0 * g, -g * 0.62, 1.24 * g, 1.5 * g, 1.24 * g, P['cebo'], semilla=semilla + 2)
    cubo(out, Mf, -0.12, 0, -0.12, 0.24, 0.3, 0.24, P['hierro'], semilla=semilla + 3)


def _corona_faroles(out, Mh, P):
    # seis varillas que salen de la capucha, se abren y se doblan; de cada punta cuelga un farol
    puntas = []
    for j in range(6):
        phi = math.radians(-75 + j * 30)
        sx, cy = math.sin(phi), math.cos(phi)
        base = punto(Mh, (sx * 1.4, 2.6, -1.4 - 0.3 * cy))
        tramos = ((sx * 1.4, 1.4 + 1.1 * cy, -0.3), (sx * 2.4, 0.3 * cy, 0.3), (sx * 0.2, -0.9, 0.1))
        p = _ruta(out, base, tramos, Mh, 0.3, P['vara'], semilla=90 + j, afina=0.06)
        puntas.append(p)
        farol(out, p + np.array((0, -0.25, 0)), P, semilla=96, g=0.55)
    for a, b in zip(puntas, puntas[1:]):
        cadena(out, a + np.array((0, -0.1, 0)), b + np.array((0, -0.1, 0)), 0.42, P['hierro'], semilla=97)
    _media_luna(out, Mh, P, x=0.0)
    # los cebos de los lados tambien son faroles
    for s in (1, -1):
        base = punto(Mh, (s * 2.1, 1.1, -1.4))
        p = _ruta(out, base, ((s * 1.3, 0.5, -0.2), (s * 0.5, 0.1, -2.4), (s * 0.2, -1.4, -0.4)), Mh, 0.36, P['vara'],
                  semilla=98, afina=0.06)
        farol(out, p + np.array((0, -0.2, 0)), P, semilla=99, g=0.6)


def _corona_encadenada(out, Mh, P):
    # cuernos de carnero: una espiral a cada lado que sale de la capucha, va atras, baja y vuelve
    for s in (1, -1):
        p = punto(Mh, (s * 1.7, 2.0, -0.6))
        for j in range(10):
            a = j * 0.6
            d = (s * 0.5, 0.95 * math.cos(a), -0.95 * math.sin(a))
            q = p + _dir(Mh, d) * (1.1 - j * 0.05)
            g = 1.0 - j * 0.075
            viga(out, p, q, g, g, P['hueso'], extra=0.12, semilla=100 + j)
            p = q
        a = punto(Mh, (s * 2.9, 0.6, -2.0))                                       # un jiron que cuelga del cuerno
        _jirones(out, a, a + _dir(Mh, (0, 0, -1.4)), 4.0, P, semilla=112 + (s > 0))
        # en vez de cebos, una cadena rota que cuelga de la capucha, con su grillete
        base = punto(Mh, (s * 2.3, -0.6, -2.2))
        fin = base + np.array((s * 1.4, -5.6, 0.4))
        cadena(out, base, fin, 0.8, P['oxido'], semilla=118)
        cubo(out, vr.T(*fin) @ vr.Ry(s * 20 * D), -0.6, -0.9, -0.6, 1.2, 0.9, 1.2, P['oxido'], semilla=119)
    # el bozal de hierro, roto: tres aros sobre el hocico (el de delante, partido) y dos barras
    for j, z in enumerate((0.7, 1.7, 2.7)):
        y0, y1 = -0.7, 2.0
        for s in (1, -1):
            if j == 2 and s < 0:
                continue
            viga(out, punto(Mh, (s * 2.32, y0, z)), punto(Mh, (s * 2.32, y1, z)), 0.34, 0.34, P['oxido'], semilla=114)
        viga(out, punto(Mh, (-2.32 if j < 2 else 0.4, y1, z)), punto(Mh, (2.32, y1, z)), 0.34, 0.34, P['oxido'], semilla=115)
    for s in (1, -1):
        viga(out, punto(Mh, (s * 0.9, 2.05, 0.3)), punto(Mh, (s * 0.9, 2.05, 3.0)), 0.3, 0.3, P['oxido'], semilla=116)
    p0 = punto(Mh, (-2.32, -0.6, 2.7))                                             # una cadena rota que cuelga del bozal
    cadena(out, p0, p0 + np.array((-0.4, -4.2, 0.4)), 0.8, P['oxido'], semilla=117)
    _gancho_negro(out, Mh, P, 1)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

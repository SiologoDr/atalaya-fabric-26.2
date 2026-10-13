"""
Estudio de Ofidia (12-10-2026). Juan: «recrea igual a Ofidia, o hazle sub variantes; pon la
original y sus variantes para no copiarla como tal». Tras la primera version: «no son
iguales en modelo a Ofidia, que tiene boca de monstruo, cola... fijate bien como es». Y tras la
segunda: «no son manos o brazos, son alas lo que tiene; su boca es como triangular, revisa
bien su portada».

  Ofidia es la sirena-sierpe de la tercera dungeon de Dedsafio 4 (diseno de Eufonia Studio).
  Estudiada en el cartel, en el retrato de su barra y en la presentacion del directo del
  10-10-2026 (los fotogramas estan en el scratchpad, ded/intro6). Su forma de monstruo:

    - flota erguida, como una sirena: la cola es una sierpe de tambores de marmol azul con
      cinturones granates con remaches, que cuelga del cinturon de la cintura, hace una ese
      suave y acaba en una aleta roja de hojas en abanico;
    - la cintura: un cinturon con remaches;
    - la pose, la del directo (el fotograma que marco Juan): el torso se echa un poco hacia
      delante y la cabeza va delante del pecho, a la altura del costillar, mirando al frente,
      con la mandibula de abajo colgando por delante; las alas, abiertas a los lados; debajo de
      la cintura, el cuerpo baja, se abomba hacia delante por debajo de la cabeza y se curva
      hacia atras hasta la aleta roja;
    - de arriba abajo, por la ese: el costillar, que es solo costillas (seis pares de huesos
      curvos que brillan: salen de la columna, rodean el pecho bajando un poco y vuelven por
      delante hasta el esternon; las del medio, las mas anchas; las dos de abajo, sueltas); la
      cintura, pequena; y
      debajo, tambores de marmol con su cinturon que van de menor a mayor y de mayor a menor
      hasta la cola (lo mas gordo, a la mitad, el doble que la cintura, sin llegar a ancho);
    - dos alas de murcielago: el brazo (codo hacia atras, muneca hacia delante) y cuatro dedos
      largos en abanico, con la membrana azul noche tendida solo entre ellos y el borde libre en
      arcos (nada en las axilas). Sin cubos de luz; los huesos, de marmol oscuro, llevan una
      veta del neon que brilla un poco;
    - la cabeza, GRANDE Y MACIZA como en el cartel (se hace sin escala y se pone 1,4 veces mas
      grande, con el pixel del mismo tamano que el del cuerpo): una capucha alta de azul noche,
      en capas, con el pico en escalones hacia atras, melenas oscuras que se rizan detras como
      algas y una fila de pinchos; una visera lila con una gema blanca que brilla, dos cuernos
      lila, una media luna lila, una espina rosa, un gancho negro y un tallo negro con muescas
      en la coronilla;
    - la boca: las dos mandibulas son medio rectangulo y medio triangulo (la planta acaba en
      punta), con la bisagra atras. La de arriba, larga y recta, lila por encima y en la proa,
      con la gema en la arista, los colmillos rosas y blancos por todo el borde y el gancho
      negro, que sale de un lado de la punta y sube; la de abajo, una bandeja rosa por dentro
      con el borde de marmol y los dientes rojos en escalon, cuelga muy abierta, en diagonal.
      De frente es el escudo rosa que acaba en punta debajo de la visera (asi en la portada y
      en el directo);
    - tres cebos de varillas gruesas: el de arriba sale del tallo negro, sube y se dobla hacia
      atras, y los de los lados salen de la capucha y se doblan hacia atras y abajo; acaban en
      cubos rosas.

  Las variantes usan ese mismo cuerpo (cola, costillar, alas y boca) y cambian la forma de lo
  que la enmarca, el material y el neon:

    O  la original      solo para estudiarla (no va al mod)
    A  de la Capucha    la capucha se abre en una capucha de cobra con dos ojos falsos;
                        sin cebos; marmol de luna y hierro; azul hielo
    B  de los Faroles   los cebos se hacen faroles con almas: una corona en la cabeza y uno
                        a cada lado; marmol pizarra y laton; verde de almas
    C  Encadenada       cuernos de carnero, bozal de hierro roto, grilletes en las alas
                        con la cadena rota, cadenas en vez de cebos, barrotes en el pecho y
                        cadenas por el cuerpo; marmol negro con vetas rojas; carmesi

Mismo oficio que Simara: cajas con las caras pintadas a 8 px por bloque, sin ruido. El marmol
esta dibujado a mano (TESELA): manchas grandes de centro claro, puestas una a una.
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


# ----------------------------------------------------------------------
#  El marmol, dibujado a mano como en el cartel: una tesela de 32 x 32 con manchas de formas y
#  tamanos distintos, puestas a mano. 3 es el cuerpo lila de la mancha, 4 su centro claro, 1 la
#  sombra de abajo a la derecha, las motas oscuras del fondo y las grietas; 2 el fondo.
# ----------------------------------------------------------------------
_MANCHAS = {
    'S1': ("....33333....",
           "..333444433..",
           ".33444444443.",
           "3344444444433",
           "3344444444331",
           ".33344443331.",
           "...3333311...",
           ".....111....."),
    'S2': ("..3333...",
           ".334443..",
           "33444443.",
           "334444431",
           ".3344431.",
           "..33331..",
           "...11...."),
    'S3': (".333..",
           "33443.",
           "344431",
           "344431",
           "334431",
           ".3331.",
           "..11.."),
    'S4': ("..333333..",
           ".33444443.",
           "3344444431",
           ".333333311",
           "...1111..."),
    'S5': (".333.",
           "34443",
           "33431",
           ".311."),
    'S6': (".3.",
           "341",
           ".1."),
    'M1': (".11..",
           "1111.",
           ".11.."),
    'K1': ("1....",
           ".1...",
           ".11..",
           "...1.",
           "....1"),
    'K2': ("..1",
           ".1.",
           "1.."),
}
# donde va cada una (fila, columna); las motas del fondo, antes que las manchas
_SITIOS = (('M1', 8, 4), ('M1', 15, 18), ('M1', 29, 12), ('M1', 24, 29), ('M1', 6, 27),
           ('S1', 0, 1), ('S2', 1, 18), ('S5', 3, 28), ('S4', 10, 9), ('S3', 9, 22), ('S6', 11, 2),
           ('S2', 17, 1), ('S1', 18, 14), ('S5', 26, 4), ('S4', 27, 22), ('S6', 16, 28),
           ('K1', 12, 26), ('K2', 24, 10))


def _hacer_tesela():
    t = np.full((32, 32), 2)
    for nombre, f0, c0 in _SITIOS:
        for i, fila in enumerate(_MANCHAS[nombre]):
            for j, ch in enumerate(fila):
                if ch != '.':
                    t[(f0 + i) % 32, (c0 + j) % 32] = int(ch)
    return t


TESELA = _hacer_tesela()


def _tesela(tw, th, s):
    """Un trozo de la tesela del tamano de la cara; la semilla dice por donde empieza."""
    rng = random.Random(s)
    f0, c0 = rng.randrange(32), rng.randrange(32)
    return TESELA[(np.arange(th)[:, None] + f0) % 32, (np.arange(tw)[None, :] + c0) % 32]


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
        """El marmol del cuerpo, dibujado a mano: manchas grandes y claras con su sombra (en la C,
        negro con vetas rojas que brillan, como curvas de nivel)."""
        idx = _tesela(tw, th, s)
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
        """La capucha: azul noche, con las manchas del marmol apagadas."""
        idx = np.array([0, 1, 2, 3, 3])[_tesela(tw, th, s + 5)]
        return _imagen(_bisel(idx), V['capucha']), None
    reg('capucha', capucha)

    def ala_hueso(tw, th, cara, s):
        """Los huesos de las alas: el marmol, mas oscuro que el del cuerpo, con una veta del neon
        a lo largo que brilla un poco (Juan: «quiero que tenga ese toque de iluminado un poco»)."""
        idx = np.array([0, 1, 1, 2, 3])[_tesela(tw, th, s + 9)]
        tex = _imagen(_bisel(idx), V['marmol'])
        veta = np.zeros((th, tw), bool)
        if tw >= th and th >= 3:
            veta[th // 2, 1:-1] = True
        elif tw >= 3:
            veta[1:-1, tw // 2] = True
        if not veta.any():
            return tex, None
        tex[veta] = (*nm._hex(V['neon'][1]), 255)
        return tex, _emis(tex, veta, 110)
    reg('ala_hueso', ala_hueso)

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

    def _hojas_de_dientes(tw, th, rampa, colgando, brillo=None):
        """Una fila de dientes dibujada en una hoja, como en el cartel (no hecha de cubos): cada
        diente, de cuatro pixeles de ancho, con la raya clara por el medio, el borde oscuro y la
        punta en escalon; uno largo y uno corto; entre uno y otro, hueco. Si cuelgan, la raiz va
        arriba de la textura; si estan de pie, abajo."""
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in rampa]
        n = max(1, (tw + 1) // 5)
        x0 = (tw - (n * 5 - 1)) // 2
        for i in range(n):
            x = x0 + i * 5
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.68)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)                     # 0 en la raiz, 1 en la punta
                if f > 0.85:
                    pix = ((x + 1, c[4]),)
                elif f > 0.6:
                    pix = ((x + 1, c[4]), (x + 2, c[3]))
                else:
                    pix = ((x, c[2]), (x + 1, c[4]), (x + 2, c[3]), (x + 3, c[1]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
            y = 0 if colgando else th - 1                      # la raiz, mas oscura
            for xx in range(max(x, 0), min(x + 4, tw)):
                t[y, xx] = c[1]
        return t, (_emis(t, t[..., 3] > 0, brillo) if brillo else None)

    def colmillos(tw, th, cara, s):
        """Los colmillos de arriba: una hoja que cuelga del borde del paladar, con los dientes
        rosas y blancos dibujados; brillan un poco."""
        return _hojas_de_dientes(tw, th, V['colmillo'], True, 150)
    reg('colmillos', colmillos)

    def dientes(tw, th, cara, s):
        """Los dientes rojos de abajo: una hoja de pie sobre el borde de la bandeja rosa."""
        return _hojas_de_dientes(tw, th, V['diente_bajo'], False)
    reg('dientes', dientes)

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

    def aleta(tw, th, cara, s):
        """Las hojas de la aleta de la cola: rojas, con la raiz oscura, una veta clara por el medio y
        la punta clara."""
        ys, xs = np.mgrid[0:th, 0:tw]
        v = ys / max(th - 1, 1)                        # 0 en la punta (arriba de la textura), 1 en la raiz
        idx = np.where(v > 0.7, 1, np.where(v > 0.25, 2, 3))
        if tw >= 4:
            idx = np.where(np.abs(xs - (tw - 1) / 2) < 0.6, np.minimum(idx + 1, 4), idx)
        if th >= 4:
            idx[0, :] = 4
        return _imagen(idx, V['diente_bajo']), None
    reg('aleta', aleta)

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
        """Una costilla: una barra del neon con el canto de arriba casi blanco y la sombra abajo;
        brilla entera."""
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = c_m
        t[..., 3] = 255
        if th >= 3:
            t[0, :, :3] = qm._mezcla(c_m, c_n, 0.75)
            t[1, :, :3] = qm._mezcla(c_m, c_n, 0.4)
            t[-1, :, :3] = qm._mezcla(c_h, c_m, 0.5)
        if tw >= 4:
            t[:, ::4, :3] = qm._mezcla(c_m, c_n, 0.25)
        return t, _emis(t, np.ones((th, tw), bool), 215)
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
        """Las varillas de los cebos: gruesas, del marmol un poco mas oscuro, como en el cartel."""
        idx = np.array([0, 1, 1, 2, 3])[_tesela(tw, th, s + 21)]
        return _imagen(_bisel(idx), V['marmol']), None
    reg('vara', vara)

    def gancho(tw, th, cara, s):
        """El gancho negro: liso, con remaches de 2 x 2 del color de su neon (en la original, apagados)."""
        idx = np.full((th, tw), 2)
        tex = _imagen(_bisel(idx), V['gancho'])
        ys, xs = np.mgrid[0:th, 0:tw]
        m = ((ys % 5) < 2) & ((xs % 5) < 2) & (ys > 0) & (xs > 0) & (ys < th - 1) & (xs < tw - 1)
        if k == 'O':                                       # en el cartel, el negro no lleva remaches que brillen
            tex[m] = (*V['gancho'][4], 255)
            return tex, None
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

    def _membrana(tw, th, s, libre):
        """La membrana del ala de murcielago: azul noche con manchas de marmol, mas oscura junto a
        la raiz; si el borde es libre, va recortado en arco (cada tramo entre dos dedos se hunde)
        y con un canto un poco mas claro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        u = (xs + 0.5) / tw
        m = _manchas(tw, th, s + 31, celda=6.5, umbral=0.58, alto=0.8)
        idx = np.array([0, 1, 1, 2, 3])[m]
        v = 1 - (ys + 0.5) / th                        # 0 en la raiz (abajo), 1 en el borde (arriba)
        idx = np.where(v < 0.3, np.maximum(idx - 1, 0), idx)
        img = _imagen(idx, V['trapo'])
        borde = (th - 1) * (0.03 + 0.2 * np.sin(np.pi * u)) if libre else np.zeros_like(u)
        fuera = ys < borde
        if libre:
            canto = (~fuera) & (ys < borde + 1.6)
            img[canto] = (*V['trapo'][4], 255)
        t[~fuera] = img[~fuera]
        return t, None

    def membrana(tw, th, cara, s):
        return _membrana(tw, th, s, True)
    reg('membrana', membrana)

    def membrana_lisa(tw, th, cara, s):
        return _membrana(tw, th, s, False)
    reg('membrana_lisa', membrana_lisa)

    def hombro(tw, th, cara, s):
        """El hombro de las alas: el negro del gancho con remaches que no brillan."""
        idx = np.full((th, tw), 2)
        tex = _imagen(_bisel(idx), V['gancho'])
        ys, xs = np.mgrid[0:th, 0:tw]
        m = ((ys % 5) < 2) & ((xs % 5) < 2) & (ys > 0) & (xs > 0) & (ys < th - 1) & (xs < tw - 1)
        tex[m] = (*V['gancho'][4], 255)
        return tex, None
    reg('hombro', hombro)

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
#  El cuerpo en ese: tambores de marmol con su cinturon, de menor a mayor y de mayor a menor
# ----------------------------------------------------------------------
CINTURA = 0.65                    # la cintura, lo mas fino del cuerpo
# el grueso del cuerpo por la ese (fraccion del largo, radio): la cintura, pequena; el primer
# tambor; crece hasta lo mas gordo, a la mitad (el doble que la cintura, sin llegar a ancho), y
# de ahi mengua hasta la cola. Juan lo quiso menos ancho «en general»: el cuerpo es de cajas
# cuadradas y, visto en diagonal, parece aun mas ancho
PERFIL = ((0.0, CINTURA), (0.09, CINTURA), (0.0901, 0.95), (0.25, 1.15), (0.45, 1.42), (0.6, 1.4), (0.75, 1.12),
          (0.88, 0.85), (1.0, 0.5))
INCLINA = 24.0                    # el torso se echa hacia delante (grados)
ESC_CABEZA = 1.4                  # la cabeza, grande y maciza como en el cartel
ANCLA = np.array((0.0, 23.0, 0.0))  # la base del costillar: de aqui cuelga el cuerpo en ese

# el cuerpo, de perfil, desde la base del costillar hasta la aleta, medido en el fotograma del
# directo que marco Juan (a unos 18 pixeles por bloque): baja, se abomba hacia delante por debajo
# de la cabeza y se curva hacia atras hasta la aleta
ESE = [(0.0, 23.0, 0.0), (0.0, 20.8, 0.0), (0.0, 19.0, 0.9), (0.0, 16.8, 2.2), (0.0, 14.3, 3.4), (0.0, 11.8, 4.0),
       (0.0, 9.3, 3.8), (0.0, 7.1, 2.9), (0.0, 5.4, 1.4), (0.0, 4.4, -0.4), (0.0, 4.0, -1.9)]


def _radio(f):
    """El radio del cuerpo a la fraccion f del largo de la ese (0 en la cintura, 1 en la aleta)."""
    xs, rs = zip(*PERFIL)
    return float(np.interp(f, xs, rs))


def _marco_sin_giro(p, d):
    """Un marco con +Z hacia d que no gira alrededor de la ese: como la ese va de perfil (en el
    plano y-z), su eje x es siempre el x del mundo."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    return em.marco(p, d, up=(0.0, -d[2], d[1]) if abs(d[0]) < 0.9 else (0.0, 1.0, 0.0))


def cuerpo_ese(out, V, P):
    """De la base del costillar a la aleta, por la ese, en tambores de marmol rectos y de una
    pieza, como en el cartel (no en rodajas), con un cinturon grueso en cada junta que tapa el
    codo: la cintura, pequena, y debajo los tambores, que van de menor a mayor (lo mas gordo, a
    la mitad) y de mayor a menor hasta la cola. No se tuercen: siguen la ese sin girar. Al
    final, la aleta roja que apunta hacia atras."""
    curva, _ = em.catmull(ESE, 800)
    curva = [np.asarray(p, float) for p in curva]
    L = [0.0]
    for a, b in zip(curva, curva[1:]):
        L.append(L[-1] + float(np.linalg.norm(b - a)))
    total = L[-1]

    def en(m):
        i = min(max(int(np.searchsorted(L, m)), 1), len(curva) - 1)
        f = (m - L[i - 1]) / max(L[i] - L[i - 1], 1e-9)
        return curva[i - 1] + (curva[i] - curva[i - 1]) * min(max(f, 0.0), 1.0)

    cortes = [0.0, PERFIL[1][0] * total]                                          # las juntas
    while True:
        largo = max(2.0, 2.5 * _radio((cortes[-1] + 1.2) / total))                # cada tambor, algo mas largo que grueso
        if cortes[-1] + largo > total - 1.0:
            break
        cortes.append(cortes[-1] + largo)
    cortes.append(total)
    pts = [en(m) for m in cortes]
    for j in range(len(pts) - 1):                                                 # los tambores
        d = pts[j + 1] - pts[j]
        r = _radio((cortes[j] + cortes[j + 1]) / 2 / total)
        cubo(out, _marco_sin_giro(pts[j], d), -r, -r, -0.35, 2 * r, 2 * r, float(np.linalg.norm(d)) + 0.7, P['marmol'],
             semilla=j)
    for j in range(len(pts) - 1):                                                 # los cinturones, en cada junta
        d = pts[j + 1] - pts[max(j - 1, 0)]
        r = max(_radio(max(cortes[j] - 0.1, 0.0) / total), _radio((cortes[j] + 0.1) / total))
        rb = r * 1.15
        cubo(out, _marco_sin_giro(pts[j], d), -rb, -rb, -0.45, 2 * rb, 2 * rb, 0.9, P['cinto'], semilla=60 + j)
        if V['clave'] == 'C' and j >= 1 and j % 2 == 1:                           # cadenas que cruzan el tambor
            dd = pts[j + 1] - pts[j]
            Mm = _marco_sin_giro(pts[j], dd)
            Lj = float(np.linalg.norm(dd))
            r = _radio((cortes[j] + cortes[j + 1]) / 2 / total) * 1.02
            for sx in (1, -1):
                cadena(out, punto(Mm, (-sx * r, r, 0.5)), punto(Mm, (sx * r, r, Lj - 0.5)), 0.7, P['oxido'], semilla=j)
    fin = pts[-1]
    t = pts[-1] - pts[-2]
    aleta(out, fin, t / np.linalg.norm(t), P)
    return pts


def cuello(out, ctrl, P, r=1.2):
    """El cuello: dos tambores de marmol, un poco abombados, con su cinturon, que suben de lo
    alto del pecho a la cabeza; devuelve la punta de arriba."""
    curva, _ = em.catmull(ctrl, 300)
    curva = [np.asarray(p, float) for p in curva]
    L = [0.0]
    for a, b in zip(curva, curva[1:]):
        L.append(L[-1] + float(np.linalg.norm(b - a)))
    total = L[-1]
    n = max(4, 2 * int(math.ceil(total / 1.6)))
    pts = [curva[min(int(np.searchsorted(L, total * i / n)), len(curva) - 1)] for i in range(n + 1)]
    marcos = sm._marcos(pts, (0, 0, 1))
    for i, M in enumerate(marcos):
        Ls = float(np.linalg.norm(pts[i + 1] - pts[i]))
        u = ((i + 0.5) / n * 2) % 1.0
        rr = r * (0.9 + 0.1 * math.sin(math.pi * u))
        cubo(out, M, -rr, -rr, -0.3, 2 * rr, 2 * rr, Ls + 0.6, P['marmol'], semilla=80 + i)
    rb = r * 1.08
    for i in (0, n // 2):
        cubo(out, marcos[i] @ vr.T(0, 0, -0.38), -rb, -rb, 0, 2 * rb, 2 * rb, 0.76, P['cinto'], semilla=90 + i)
    return pts[-1]


def aleta(out, p, t, P):
    """La aleta roja del final de la cola: un abanico de hojas planas en el plano de perfil y unas
    pocas fuera de el, para que tenga bulto."""
    cubo(out, vr.T(*p), -0.55, -0.55, -0.55, 1.1, 1.1, 1.1, P['cinto'], semilla=95)
    for j, (phi, largo, x) in enumerate(((0, 4.4, 0.0), (20, 4.0, 0.0), (-20, 4.0, 0.0), (40, 3.4, 0.0), (-40, 3.4, 0.0),
                                         (60, 2.7, 0.0), (-60, 2.7, 0.0), (10, 3.6, 0.7), (-10, 3.6, -0.7), (30, 3.0, -0.65),
                                         (-30, 3.0, 0.65), (50, 2.4, 0.5), (-50, 2.4, -0.5))):
        c, s_ = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        d = np.array((x * 0.6, t[1] * c - t[2] * s_, t[1] * s_ + t[2] * c))
        d = d / np.linalg.norm(d)
        Mb = em.marco(p, d, up=(1, 0, 0))
        w = 0.78 - 0.06 * abs(phi) / 20
        largo *= 1.2
        cubo(out, Mb, -w / 2, -0.09, 0, w, 0.18, largo * 0.72, P['aleta'], semilla=96 + j)
        cubo(out, Mb, -w * 0.3, -0.07, largo * 0.72, w * 0.6, 0.14, largo * 0.28, P['aleta'], semilla=97 + j)


# ======================================================================
#  OFIDIA
# ======================================================================
def ofidia(variante='O'):
    V = VARIANTES[variante]
    P = pintores(V)
    k = V['clave']
    out = []
    # el torso (costillar y hombros) se hace derecho y luego se echa hacia delante sobre la base
    torso = []
    Mt = vr.T(0, 21.75, 0.0) @ np.diag([1.0, 1.12, 1.0, 1.0])
    cubo(torso, Mt, -0.55, -2.6, -1.85, 1.1, 5.3, 0.95, P['columna'], semilla=4)                  # la columna
    cubo(torso, Mt, -0.4, -1.5, 1.5, 0.8, 4.0, 0.5, P['columna'], semilla=5)                      # el esternon
    cubo(torso, Mt, -2.0, -2.4, -1.45, 4.0, 4.8, 2.95, P['capucha'], semilla=6)                   # lo de dentro, oscuro
    # las costillas (Juan: «no parecen costillas sino barras»): seis pares de huesos curvos que
    # salen de la columna, rodean el pecho bajando un poco y vuelven por delante hasta el
    # esternon; las del medio son las mas anchas (el pecho, como un barril) y las dos de abajo
    # quedan sueltas, sin llegar al esternon. Brillan, con huecos oscuros entre ellas
    for j, (y, a, suelta) in enumerate(((2.15, 1.9, False), (1.35, 2.35, False), (0.55, 2.6, False),
                                        (-0.25, 2.6, False), (-1.05, 2.4, True), (-1.85, 2.0, True))):
        for sx in (1, -1):
            ctrl = [(sx * 0.45, y + 0.2, -1.5), (sx * a * 0.85, y, -1.0), (sx * a, y - 0.3, 0.1),
                    (sx * a * 0.8, y - 0.6, 1.1), (sx * (0.95 if suelta else 0.45), y - 0.85, 1.3 if suelta else 1.7)]
            pts, _ = em.catmull([punto(Mt, c) for c in ctrl], 9)
            for q in range(len(pts) - 1):
                viga(torso, pts[q], pts[q + 1], 0.5, 0.42, P['costilla'], extra=0.12, semilla=7 + (j + q) % 5)
    cubo(torso, Mt, -2.9, 2.45, -1.7, 5.8, 0.6, 3.5, P['cinto'], semilla=13)                      # los hombros
    cubo(torso, Mt, -2.3, -2.95, -1.75, 4.6, 0.55, 3.4, P['cinto'], semilla=14)                   # el cinturon de abajo
    if k == 'C':                                                                                  # barrotes: el pecho es una celda
        for x in (-1.6, -0.85, 0.85, 1.6):
            viga(torso, punto(Mt, (x, 2.4, 2.25)), punto(Mt, (x, -2.6, 2.25)), 0.24, 0.24, P['oxido'], semilla=14)
        for y in (1.1, -1.2):
            viga(torso, punto(Mt, (-2.4, y, 2.3)), punto(Mt, (2.4, y, 2.3)), 0.22, 0.22, P['oxido'], semilla=15)
    G = vr.T(*ANCLA) @ vr.Rx(INCLINA * D) @ vr.T(0, -18.8, 0)
    out += qm.transformar(torso, G)

    # las alas, abiertas del todo a los lados, casi horizontales y con las puntas un poco hacia arriba
    # (a nivel: no se inclinan con el torso)
    hombros = np.array((0.0, 24.4, -0.8))
    alas_q = []                                                                                   # van al final (las escenas las separan)
    for s in (1, -1):
        alas = []
        ala(alas, s, V, P, dy=8.4)
        Mal = vr.T(*punto(G, hombros)) @ vr.Ry(s * 8 * D) @ vr.Rz(-s * 10 * D) @ vr.T(*(-hombros))
        alas_q += qm.transformar(alas, Mal)

    # el cuerpo en ese, de la base del costillar a la aleta
    cuerpo_ese(out, V, P)

    # el cuello sube de lo alto del pecho y se adelanta; encima va la cabeza, y debajo de ella se
    # ve el costillar (Juan: «nos falta el cuello y las costillas que se vean mas abajo»)
    b = punto(G, (0.0, 24.6, 0.3))
    tope = cuello(out, [b, b + np.array((0.0, 1.8, 0.3)), b + np.array((0.0, 3.6, 1.1)), b + np.array((0.0, 5.0, 2.0))], P)
    Hc = tope + np.array((0.0, 0.3, 2.9))
    # la cabeza se hace en su sitio, sin escala, y se pone agrandada; mientras se pinta, el pixel se
    # hace mas pequeno para que, ya agrandado, mida lo mismo que el del cuerpo
    cab = []
    Mh0 = em.marco(np.zeros(3), (0.0, -0.2, 1.0))
    ppb = bm.PPB
    bm.PPB = ppb / ESC_CABEZA
    try:
        cabeza(cab, Mh0, V, P)
        {'O': _corona_original, 'A': _corona_capucha, 'B': _corona_faroles, 'C': _corona_encadenada}[k](cab, Mh0, P)
    finally:
        bm.PPB = ppb
    Mpon = vr.T(*Hc) @ np.diag([ESC_CABEZA, ESC_CABEZA, ESC_CABEZA, 1.0])
    out += qm.transformar(cab, Mpon)
    Mh = Mpon @ Mh0
    out += alas_q
    return out, {'cabeza': Mh, 'boca': punto(Mh, (0.0, -1.4, 2.4)), 'n_alas': len(alas_q)}


def _pano(out, raiz, a, b, pintor, semilla=0):
    """Un pano de membrana de la raiz al tramo a-b, que es su borde (libre o no)."""
    raiz, a, b = np.asarray(raiz, float), np.asarray(a, float), np.asarray(b, float)
    lamina(out, (raiz, raiz, b, a), pintor, float(np.linalg.norm(b - a)), float(np.linalg.norm((a + b) / 2 - raiz)), semilla)


def ala(out, s, V, P, dy=0.0):
    """Un ala de murcielago: el brazo (hombro, codo hacia atras y muneca hacia delante) y cuatro
    dedos largos que se abren en abanico desde la muneca; la membrana va tendida solo entre los
    dedos y del antebrazo al ultimo dedo, con el borde libre en arcos; en las axilas no hay
    membrana. No lleva luz (Juan: «en sus alas no tiene luz»)."""
    k = V['clave']
    sube = np.array((0.0, dy, 0.0))
    hombro = np.array((s * 2.7, 16.0, -0.8)) + sube
    codo = np.array((s * 6.6, 17.2, -2.6)) + sube
    muneca = np.array((s * 10.6, 19.6, -1.4)) + sube
    dedos = [np.array((s * 19.8, 22.4, -3.0)) + sube, np.array((s * 21.0, 17.6, -4.4)) + sube,
             np.array((s * 18.2, 12.4, -4.8)) + sube, np.array((s * 13.4, 9.6, -4.0)) + sube]
    cubo(out, vr.T(*hombro), -1.1, -1.0, -1.2, 2.2, 2.0, 2.4, P['hombro'], semilla=20)            # el hombro, con remaches
    viga(out, hombro, codo, 1.7, 1.6, P['ala_hueso'], extra=0.35, semilla=21)
    viga(out, codo, muneca, 1.4, 1.3, P['ala_hueso'], extra=0.3, semilla=22)
    bola(out, vr.T(*codo), 1.0, P['ala_hueso'], semilla=23)
    bola(out, vr.T(*muneca), 0.9, P['ala_hueso'], semilla=24)
    for j, t in enumerate(dedos):                                                                # los dedos
        g = 0.62 - 0.05 * j
        viga(out, muneca, t, g, g, P['ala_hueso'], extra=0.12, semilla=25 + j)
    # la membrana: solo entre los dedos (con el borde en arcos) y del antebrazo al ultimo dedo;
    # nada en las axilas ni hasta el costado
    for j in range(3):
        _pano(out, muneca, dedos[j], dedos[j + 1], P['membrana'], semilla=30 + j + 10 * (s > 0))
    _pano(out, codo, muneca, dedos[3], P['membrana'], semilla=34 + 10 * (s > 0))
    if k == 'C':                                                                                  # grilletes en el brazo, con la cadena rota
        for p, dd in (((hombro + codo) / 2, codo - hombro), ((codo + muneca) / 2, muneca - codo)):
            M = em.marco(p, dd)
            cubo(out, M, -0.95, -0.9, -0.35, 1.9, 1.8, 0.7, P['oxido'], semilla=40)
            cadena(out, p + np.array((0, -0.9, 0)), p + np.array((s * 0.3, -4.2, 0.4)), 0.75, P['oxido'], semilla=41)


def prisma5(out, M, ancho, y0, y1, recto, largo, pintores, semilla=0):
    """Un prisma cuya planta es medio rectangulo y medio triangulo: de z=0 a z=recto, el
    rectangulo de 'ancho'; de ahi a z=largo, el triangulo que acaba en punta. Va de y0 a y1.
    pintores dice el de cada cara: 'arriba', 'abajo', 'atras', 'lados' (los dos lados rectos)
    y 'proa' (las dos caras de la punta); la que no tiene pintor no se dibuja."""
    a = ancho / 2
    planta = [(-a, 0.0), (a, 0.0), (a, recto), (0.0, largo), (-a, recto)]
    pa = lambda x, z: punto(M, (x, y1, z))
    pb = lambda x, z: punto(M, (x, y0, z))
    alto = abs(y1 - y0)
    caras = []
    if pintores.get('atras'):
        caras.append(((pb(a, 0), pb(-a, 0), pa(-a, 0), pa(a, 0)), pintores['atras']))
    if pintores.get('lados'):
        caras.append(((pb(-a, 0), pb(-a, recto), pa(-a, recto), pa(-a, 0)), pintores['lados']))
        caras.append(((pb(a, recto), pb(a, 0), pa(a, 0), pa(a, recto)), pintores['lados']))
    if pintores.get('proa'):
        caras.append(((pb(-a, recto), pb(0, largo), pa(0, largo), pa(-a, recto)), pintores['proa']))
        caras.append(((pb(0, largo), pb(a, recto), pa(a, recto), pa(0, largo)), pintores['proa']))
    for k, (P4, pin) in enumerate(caras):
        p0, p1, p2, p3 = P4
        lamina(out, P4, pin, float(max(np.linalg.norm(p1 - p0), 0.05)), float(max(alto, 0.05)), semilla + k)
    for clave, f in (('arriba', pa), ('abajo', pb)):
        pin = pintores.get(clave)
        if not pin:
            continue
        rect = (f(-a, 0), f(a, 0), f(a, recto), f(-a, recto))
        tri = (f(-a, recto), f(a, recto), f(0, largo), f(0, largo))
        if clave == 'abajo':
            rect, tri = rect[::-1], tri[::-1]
        lamina(out, rect, pin, ancho, recto, semilla + 10)
        lamina(out, tri, pin, ancho, largo - recto, semilla + 11)
    return planta


def borde5(ancho, recto, largo, paso):
    """Puntos a lo largo del borde de la planta de prisma5 (los dos lados y la punta), con la
    direccion del borde en cada uno, para poner dientes."""
    a = ancho / 2
    tramos = [((-a, 0.0), (-a, recto)), ((-a, recto), (0.0, largo)), ((0.0, largo), (a, recto)), ((a, recto), (a, 0.0))]
    puntos = []
    for (x0, z0), (x1, z1) in tramos:
        L = math.hypot(x1 - x0, z1 - z0)
        n = max(1, int(L / paso))
        for i in range(n):
            t = (i + 0.5) / n
            puntos.append((x0 + (x1 - x0) * t, z0 + (z1 - z0) * t, math.atan2(x1 - x0, z1 - z0)))
    return puntos


def _hilera(out, M, ancho, recto, largo, y, alto, pintor, semilla=0, mete=0.2):
    """Los dientes de una mandibula como hojas (no cubos), una por cada lado de la planta de
    prisma5, metidas un poco hacia dentro del borde: de y a y + alto en el marco M (con alto
    negativo, cuelgan; con alto positivo, estan de pie)."""
    a = ancho / 2 - mete
    planta = [(-a, mete), (-a, recto), (0.0, largo - mete * 1.6), (a, recto), (a, mete)]
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(planta, planta[1:])):
        A, B = punto(M, (x0, y, z0)), punto(M, (x1, y, z1))
        A2, B2 = punto(M, (x0, y + alto, z0)), punto(M, (x1, y + alto, z1))
        lado, h = float(np.linalg.norm(B - A)), float(np.linalg.norm(A2 - A))
        if alto < 0:                                   # arriba de la textura, la raiz
            lamina(out, (A2, B2, B, A), pintor, lado, h, semilla + j)
        else:                                          # arriba de la textura, las puntas
            lamina(out, (A, B, B2, A2), pintor, lado, h, semilla + j)


def colmillo(out, M, ancho, largo, grueso, pintor, semilla=0):
    """Un colmillo plano de dos escalones que cuelga a lo largo de -y local: la hoja y la punta,
    como los de Ofidia (rectangulares, con la punta en escalon)."""
    cubo(out, M, -ancho / 2, -largo * 0.66, -grueso / 2, ancho, largo * 0.66, grueso, pintor, semilla=semilla)
    cubo(out, M, -ancho * 0.36, -largo, -grueso * 0.4, ancho * 0.56, largo * 0.36, grueso * 0.8, pintor, semilla=semilla + 1)


def cabeza(out, Mh, V, P):
    """La cabeza, grande y maciza como en el cartel (se hace sin escala; ofidia() la agranda):
    la capucha alta, en capas, con el pico en escalones hacia atras, las melenas oscuras que se
    rizan detras como algas y una fila de pinchos en el borde de atras; los faldones a los lados;
    y la boca de dos mandibulas, medio rectangulo y medio triangulo cada una: la de arriba, lila,
    con la gema en la arista y una fila de colmillos largos; la de abajo, una bandeja rosa con
    los dientes rojos por el borde, que de frente es el escudo rosa que acaba en punta."""
    k = V['clave']
    # la capucha: un bloque grande, otro encima un poco mas estrecho y el pico en escalones
    cubo(out, Mh, -2.3, -0.6, -3.4, 4.6, 3.0, 4.3, P['capucha'], semilla=1)
    cubo(out, Mh, -1.95, 2.4, -3.0, 3.9, 0.6, 3.6, P['capucha'], semilla=2)
    if k != 'A':
        for j, (w, y, z, ang) in enumerate(((3.7, 2.6, -1.5, -14), (2.9, 3.4, -2.0, -20), (2.1, 4.2, -2.6, -27),
                                            (1.4, 4.9, -3.2, -34), (0.8, 5.5, -3.8, -41), (0.4, 6.0, -4.4, -48))):
            cubo(out, Mh @ vr.T(0, y, z) @ vr.Rx(ang * D), -w / 2, -0.1, -w * 0.5, w, 1.0, w, P['capucha'], semilla=3 + j)
        # las melenas: tiras oscuras que salen de atras de la capucha y se rizan hacia arriba
        for j, x in enumerate((-1.3, 0.0, 1.3)):
            p = punto(Mh, (x, 2.6, -3.3))
            for q in range(6):
                a = -0.4 + 0.25 * j + q * 0.42
                d = _dir(Mh, (0.15 * x, math.sin(a) * 0.9 + 0.35, -math.cos(a) * 0.9))
                g = 0.5 - 0.06 * q
                viga(out, p, p + d, g, g * 0.6, P['capucha'], extra=0.1, semilla=10 + q)
                p = p + d
    for j, x in enumerate((-1.7, -0.85, 0.0, 0.85, 1.7)):                                         # los pinchos de atras
        p = punto(Mh, (x, 0.3, -3.35))
        pua(out, em.marco(p, _dir(Mh, (0.25 * x, -0.35, -1.0))) @ vr.Rx(90 * D), 0.2, 1.1 + 0.25 * (j % 2), P['capucha'],
            semilla=20 + j % 3)
    for s in (1, -1):                                                                              # los faldones
        x0 = 2.25 if s > 0 else -2.7
        cubo(out, Mh, x0, -2.2, -3.4, 0.45, 4.4, 4.0, P['capucha'], semilla=6)
    # la de arriba: lila por encima y en la proa, con la gema en la arista y los colmillos largos
    # colgando por todo el borde del paladar
    Mu = _mandibula_arriba(Mh)
    W, R, L = 4.5, 3.0, 5.6
    prisma5(out, Mu, W, 0.0, 2.0, R, L, {'arriba': P['hueso'], 'proa': P['hueso'], 'lados': P['capucha'], 'atras': P['capucha'],
                                         'abajo': P['boca']}, semilla=7)
    n = _dir(Mu, (0.0, 0.0, 1.0))
    Mg = em.marco(punto(Mu, (0.0, 1.0, L)) + n * 0.05, n)
    cubo(out, Mg @ vr.Rz(45 * D), -0.4, -0.4, 0, 0.8, 0.8, 0.06, None, caras={'frente': P['gema']}, semilla=9)
    _hilera(out, Mu, W, R, L, 0.02, -1.6, P['colmillos'], semilla=12)                             # los colmillos, en hoja
    # la de abajo: la bandeja rosa con el borde de marmol y los dientes rojos en escalon
    Ml = Mh @ vr.T(0, -0.3, -0.2) @ vr.Rx(46 * D)
    prisma5(out, Ml, 4.3, -1.5, 0.0, 3.2, 6.0, {'arriba': P['boca'], 'abajo': P['marmol'], 'lados': P['marmol'],
                                                 'proa': P['marmol'], 'atras': P['capucha']}, semilla=33)
    _hilera(out, Ml, 4.3, 3.2, 6.0, 0.0, 0.85, P['dientes'], semilla=40, mete=0.25)              # los dientes rojos, en hoja
    # al fondo de la boca, la garganta que brilla
    Mv = em.marco(punto(Mh, (0.0, -0.2, 0.05)), _dir(Mh, (0.0, 0.05, 1.0)))
    cubo(out, Mv, -1.5, -1.5, 0, 3.0, 3.0, 0.05, None, caras={'frente': P['nucleo']}, semilla=49)
    if k == 'C':
        return
    for s in (1, -1):                                                                              # los dos cuernos lila
        p = punto(Mu, (s * 1.55, 1.9, 0.9))
        pua(out, em.marco(p, _dir(Mh, (s * 0.5, 1.0, -0.25))) @ vr.Rx(90 * D), 0.3, 3.4, P['hueso'], semilla=50)


def _mandibula_arriba(Mh):
    """El marco de la mandibula de arriba: bisagra atras y un poco levantada."""
    return Mh @ vr.T(0, -0.3, -0.2) @ vr.Rx(-14 * D)


def _media_luna(out, Mh, P, x=1.3):
    """La media luna lila de la coronilla: una hoja curva que sube hacia atras y se dobla
    hacia delante."""
    p = punto(Mh, (x, 2.9, -1.3))
    for j, (d, w) in enumerate((((0, 1.0, -0.45), 0.9), ((0, 1.0, 0.15), 0.75), ((0, 0.45, 0.9), 0.58),
                                 ((0, -0.2, 1.0), 0.38))):
        q = p + _dir(Mh, d) * 1.1
        viga(out, p, q, w, 0.26, P['hueso'], arriba=_dir(Mh, (1, 0, 0)), extra=0.08, semilla=51 + j)
        p = q


def _gancho_negro(out, Mh, P, s=1):
    """El gancho negro con remaches, como en el cartel: sale de un lado de la punta de la
    mandibula de arriba, va hacia fuera, sube y se dobla hacia dentro."""
    Mu = _mandibula_arriba(Mh)
    p = punto(Mu, (s * 2.0, 1.0, 2.6))
    _ruta(out, p, ((s * 1.7, 0.0, 0.4), (0.0, 1.5, 0.05), (-s * 0.6, 0.0, 0.0)), Mu, 0.85, P['gancho'], semilla=55, afina=0.05)


def _tallo_negro(out, Mh, P):
    """El tallo negro de la coronilla, con sus muescas: de su punta sale el cebo de arriba."""
    base = punto(Mh, (-0.1, 2.9, -0.9))
    tope = _ruta(out, base, ((0.0, 2.6, -0.1),), Mh, 1.1, P['gancho'], semilla=60)
    for j in range(3):
        p = base + _dir(Mh, (0.0, 0.6 + j * 0.7, -0.05))
        viga(out, p - _dir(Mh, (0.85, 0, 0)), p + _dir(Mh, (0.85, 0, 0)), 0.4, 0.4, P['gancho'], semilla=61)
    return tope


def _cebos(out, Mh, P, tope, final=None):
    """Los tres cebos, de varillas gruesas: el de arriba sale del tallo negro, sube y se dobla
    hacia atras; los de los lados salen de la capucha, se abren y se doblan hacia atras y abajo.
    Cada uno acaba en un cubo encendido (o en lo que diga 'final')."""
    puntas = [_ruta(out, tope, ((0.0, 1.5, -0.2), (-2.4, 0.5, -1.4), (-0.2, -1.0, -0.2)), Mh, 0.6, P['vara'], semilla=62,
                    afina=0.08)]
    for s in (1, -1):
        base = punto(Mh, (s * 2.3, 1.1, -1.4))
        puntas.append(_ruta(out, base, ((s * 1.5, 0.5, -0.2), (s * 0.7, 0.1, -1.6), (s * 0.15, -2.2, 0.4)), Mh, 0.5, P['vara'],
                            semilla=66 + (s > 0) * 3, afina=0.08))
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
    p = punto(Mh, (1.0, 2.9, -0.4))                                                # la espina rosa
    pua(out, em.marco(p, _dir(Mh, (0.4, 1.0, -0.1))) @ vr.Rx(90 * D), 0.32, 2.8, P['espina'], semilla=75)


def _corona_capucha(out, Mh, P):
    # la capucha de cobra: un ovalo de membrana detras de la cabeza, con sus varillas detras
    Mc = Mh @ vr.T(0, 2.0, -3.5) @ vr.Rx(-12 * D)
    cubo(out, Mc, -4.8, -3.8, 0, 9.6, 8.4, 0.08, None, caras={'frente': P['cobra'], 'atras': P['cobra']}, semilla=80)
    raiz = punto(Mc, (0, -3.4, -0.15))
    for j in range(9):
        phi = math.radians(-84 + j * 21)
        fin = punto(Mc, (math.sin(phi) * 4.5, 0.9 + math.cos(phi) * 4.2, -0.15))
        viga(out, raiz, fin, 0.24, 0.24, P['gancho'], semilla=81)
    for s in (1, -1):                                                              # dos ganchos cortos
        _ruta(out, punto(Mh, (s * 2.4, 1.0, -0.8)), ((s * 0.9, 0.3, 0.0), (0.0, 1.2, 0.3)), Mh, 0.5, P['gancho'], semilla=82)


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
        base = punto(Mh, (sx * 1.4, 3.0, -1.4 - 0.3 * cy))
        tramos = ((sx * 1.4, 1.4 + 1.1 * cy, -0.3), (sx * 2.4, 0.3 * cy, 0.3), (sx * 0.2, -0.9, 0.1))
        p = _ruta(out, base, tramos, Mh, 0.4, P['vara'], semilla=90 + j, afina=0.06)
        puntas.append(p)
        farol(out, p + np.array((0, -0.25, 0)), P, semilla=96, g=0.5)
    for a, b in zip(puntas, puntas[1:]):
        cadena(out, a + np.array((0, -0.1, 0)), b + np.array((0, -0.1, 0)), 0.42, P['hierro'], semilla=97)
    _media_luna(out, Mh, P, x=0.0)
    # los cebos de los lados tambien son faroles
    for s in (1, -1):
        base = punto(Mh, (s * 2.3, 1.1, -1.4))
        p = _ruta(out, base, ((s * 1.5, 0.5, -0.2), (s * 0.7, 0.1, -1.6), (s * 0.15, -1.8, 0.4)), Mh, 0.5, P['vara'],
                  semilla=98, afina=0.06)
        farol(out, p + np.array((0, -0.2, 0)), P, semilla=99, g=0.55)


def _corona_encadenada(out, Mh, P):
    # cuernos de carnero: una espiral a cada lado que sale de la capucha, va atras, baja y vuelve
    for s in (1, -1):
        p = punto(Mh, (s * 1.9, 2.2, -0.6))
        for j in range(10):
            a = j * 0.6
            d = (s * 0.5, 0.95 * math.cos(a), -0.95 * math.sin(a))
            q = p + _dir(Mh, d) * (1.1 - j * 0.05)
            g = 1.0 - j * 0.075
            viga(out, p, q, g, g, P['hueso'], extra=0.12, semilla=100 + j)
            p = q
        a = punto(Mh, (s * 3.0, 0.6, -2.0))                                       # un jiron que cuelga del cuerno
        _jirones(out, a, a + _dir(Mh, (0, 0, -1.4)), 3.0, P, semilla=112 + (s > 0))
        # en vez de cebos, una cadena rota que cuelga de la capucha, con su grillete
        base = punto(Mh, (s * 2.5, -0.6, -2.2))
        fin = base + np.array((s * 1.0, -4.0, 0.3))
        cadena(out, base, fin, 0.8, P['oxido'], semilla=118)
        cubo(out, vr.T(*fin) @ vr.Ry(s * 20 * D), -0.6, -0.9, -0.6, 1.2, 0.9, 1.2, P['oxido'], semilla=119)
    # el bozal de hierro, roto: tres aros sobre el hocico (el de delante, partido) y dos barras
    Mu = _mandibula_arriba(Mh)
    for j, z in enumerate((0.6, 1.5, 2.4)):
        y0, y1 = -0.15, 2.2
        for s in (1, -1):
            if j == 2 and s < 0:
                continue
            viga(out, punto(Mu, (s * 2.4, y0, z)), punto(Mu, (s * 2.4, y1, z)), 0.34, 0.34, P['oxido'], semilla=114)
        viga(out, punto(Mu, (-2.4 if j < 2 else 0.4, y1, z)), punto(Mu, (2.4, y1, z)), 0.34, 0.34, P['oxido'], semilla=115)
    for s in (1, -1):
        viga(out, punto(Mu, (s * 0.9, 2.22, 0.3)), punto(Mu, (s * 0.9, 2.22, 3.4)), 0.3, 0.3, P['oxido'], semilla=116)
    p0 = punto(Mu, (-2.4, -0.1, 2.4))                                             # una cadena rota que cuelga del bozal
    cadena(out, p0, p0 + np.array((-0.3, -3.0, 0.3)), 0.8, P['oxido'], semilla=117)
    _gancho_negro(out, Mh, P, 1)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

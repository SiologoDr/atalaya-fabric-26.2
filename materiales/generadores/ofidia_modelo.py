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
    - el torso: un costillar abierto que brilla rosa por dentro, con costillas blancas y la
      columna oscura de vertebras grises por delante;
    - dos alas de murcielago: el brazo (codo hacia atras, muneca hacia delante con un cubo rosa
      encendido por pulgar) y cuatro dedos largos en abanico, con la membrana azul noche tendida
      entre ellos y el borde libre en arcos;
    - la cabeza: una capucha puntiaguda de azul noche, una visera lila con una gema blanca
      que brilla, dos cuernos lila, una media luna lila, una espina rosa, un gancho negro con
      remaches turquesa y un tallo negro con muescas en la coronilla;
    - la boca: las dos mandibulas son medio rectangulo y medio triangulo (la planta acaba en
      punta), con la bisagra atras. La de arriba, lila por encima y en la proa, con la gema en
      la arista y los colmillos rosas y blancos por todo el borde; la de abajo, una bandeja rosa
      por dentro con el borde de marmol y los dientes rojos en escalon. De lado se ve la caja
      con los dientes rojos por el borde de arriba; de frente, el escudo rosa que acaba en
      punta debajo de la visera (asi en la portada y en el directo);
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
COLA = [(0.0, 12.0, 0.0), (0.0, 9.4, 0.7), (0.0, 6.6, 0.6), (0.0, 4.6, -0.4), (0.0, 3.3, -1.7)]


def cola(out, V, P):
    """La cola: tambores de marmol con su cinturon que cuelgan del cinturon de la cintura,
    hacen una ese suave y acaban en la aleta roja."""
    pts = sm._por_longitud(COLA, 1.9)
    marcos = sm._marcos(pts, (0, 0, 1))
    n = len(marcos)
    for i, M in enumerate(marcos):
        t = i / max(n - 1, 1)
        r = 2.0 - 1.2 * t
        L = float(np.linalg.norm(pts[i + 1] - pts[i]))
        cubo(out, M, -r, -r, -0.15, 2 * r, 2 * r, L + 0.3, P['marmol'], semilla=i)
        rb = r * 1.16
        cubo(out, M @ vr.T(0, 0, -0.28), -rb, -rb, 0, 2 * rb, 2 * rb, 0.56, P['cinto'], semilla=i)
        if V['clave'] == 'C' and i % 2 == 1:                                    # cadenas que cruzan el tambor
            for s in (1, -1):
                cadena(out, punto(M, (-s * r * 1.08, r * 1.08, 0.3)), punto(M, (s * r * 1.08, r * 1.08, L - 0.3)), 0.8,
                       P['oxido'], semilla=i)
    fin = pts[-1]
    t = pts[-1] - pts[-2]
    aleta(out, fin, t / np.linalg.norm(t), P)
    return pts


def aleta(out, p, t, P):
    """La aleta roja del final de la cola: un abanico de hojas planas en el plano de perfil y unas
    pocas fuera de el, para que tenga bulto."""
    cubo(out, vr.T(*p), -0.55, -0.55, -0.55, 1.1, 1.1, 1.1, P['cinto'], semilla=95)
    for j, (phi, largo, x) in enumerate(((0, 4.4, 0.0), (20, 4.0, 0.0), (-20, 4.0, 0.0), (40, 3.4, 0.0), (-40, 3.4, 0.0),
                                         (60, 2.7, 0.0), (-60, 2.7, 0.0), (10, 3.6, 0.7), (-10, 3.6, -0.7), (30, 3.0, -0.65),
                                         (-30, 3.0, 0.65), (50, 2.4, 0.5), (-50, 2.4, -0.5))):
        c, s_ = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        d = np.array((x, t[1] * c - t[2] * s_, t[1] * s_ + t[2] * c))
        d = d / np.linalg.norm(d)
        Mb = em.marco(p, d, up=(1, 0, 0))
        w = 0.78 - 0.06 * abs(phi) / 20
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
    Mh = em.marco(np.array((0.0, 20.0, 3.0)), (0.0, -0.3, 1.0)) @ np.diag([1.25, 1.25, 1.25, 1.0])
    cabeza(out, Mh, V, P)
    if k == 'O':
        _corona_original(out, Mh, P)
    elif k == 'A':
        _corona_capucha(out, Mh, P)
    elif k == 'B':
        _corona_faroles(out, Mh, P)
    else:
        _corona_encadenada(out, Mh, P)
    # flota: todo lo de arriba sube y la cola cuelga hasta la aleta, sin tocar el suelo
    sube = vr.T(0, 2.0, 0)
    out = qm.transformar(out, sube)
    cola(out, V, P)
    return out, {'cabeza': sube @ Mh}


def _pano(out, raiz, a, b, pintor, semilla=0):
    """Un pano de membrana de la raiz al tramo a-b, que es su borde (libre o no)."""
    raiz, a, b = np.asarray(raiz, float), np.asarray(a, float), np.asarray(b, float)
    lamina(out, (raiz, raiz, b, a), pintor, float(np.linalg.norm(b - a)), float(np.linalg.norm((a + b) / 2 - raiz)), semilla)


def ala(out, s, V, P):
    """Un ala de murcielago: el brazo (hombro, codo hacia atras y muneca hacia delante, con el
    cubo encendido por pulgar) y cuatro dedos largos que se abren en abanico desde la muneca; la
    membrana va tendida entre los dedos, con el borde libre en arcos, y del ultimo dedo baja
    hasta el costado."""
    k = V['clave']
    hombro = np.array((s * 2.7, 16.0, -0.8))
    codo = np.array((s * 6.4, 17.0, -3.2))
    muneca = np.array((s * 10.0, 20.4, -1.2))
    dedos = [np.array((s * 16.0, 23.0, -3.6)), np.array((s * 18.6, 18.0, -5.2)), np.array((s * 16.8, 12.6, -5.8)),
             np.array((s * 12.2, 9.4, -5.0))]
    costado = np.array((s * 3.0, 10.4, -1.8))
    cubo(out, vr.T(*hombro), -1.0, -0.9, -1.1, 2.0, 1.8, 2.2, P['gancho'], semilla=20)            # el hombro, con remaches
    viga(out, hombro, codo, 1.35, 1.3, P['marmol'], extra=0.3, semilla=21)
    viga(out, codo, muneca, 1.1, 1.05, P['marmol'], extra=0.28, semilla=22)
    bola(out, vr.T(*codo), 0.8, P['marmol'], semilla=23)
    bola(out, vr.T(*muneca), 0.7, P['marmol'], semilla=24)
    for j, t in enumerate(dedos):                                                                # los dedos
        g = 0.44 - 0.04 * j
        viga(out, muneca, t, g, g, P['marmol'], extra=0.1, semilla=25 + j)
    # la membrana: entre los dedos, con el borde en arcos; del ultimo dedo al costado; y por dentro
    for j in range(3):
        _pano(out, muneca, dedos[j], dedos[j + 1], P['membrana'], semilla=30 + j + 10 * (s > 0))
    _pano(out, codo, dedos[3], costado, P['membrana'], semilla=33 + 10 * (s > 0))
    _pano(out, codo, muneca, dedos[3], P['membrana_lisa'], semilla=34)
    _pano(out, hombro, codo, costado, P['membrana_lisa'], semilla=35)
    _pano(out, codo, hombro, muneca, P['membrana_lisa'], semilla=36)
    # el pulgar: el cubo encendido de la muneca (en los Faroles, un farol colgando)
    if k == 'B':
        _cubo_diamante(out, muneca + np.array((0, 0.6, 0.3)), 0.95, P['cebo'], semilla=37)
        cadena(out, muneca + np.array((0, -0.5, 0)), muneca + np.array((0, -2.2, 0)), 0.45, P['hierro'], semilla=38)
        farol(out, muneca + np.array((0, -2.35, 0)), P, semilla=39, g=0.6)
    else:
        _cubo_diamante(out, muneca + np.array((0, 0.75, 0.35)), 1.3, P['cebo'], semilla=37, giro=s * 15)
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


def colmillo(out, M, ancho, largo, grueso, pintor, semilla=0):
    """Un colmillo plano de dos escalones que cuelga a lo largo de -y local: la hoja y la punta,
    como los de Ofidia (rectangulares, con la punta en escalon)."""
    cubo(out, M, -ancho / 2, -largo * 0.66, -grueso / 2, ancho, largo * 0.66, grueso, pintor, semilla=semilla)
    cubo(out, M, -ancho * 0.36, -largo, -grueso * 0.4, ancho * 0.56, largo * 0.36, grueso * 0.8, pintor, semilla=semilla + 1)


def cabeza(out, Mh, V, P):
    """La cabeza: la capucha puntiaguda y la boca de dos mandibulas, medio rectangulo y medio
    triangulo cada una: la de arriba, lila, con la gema en la arista y los colmillos por el
    borde; la de abajo, una bandeja rosa con los dientes rojos por el borde, que de frente es
    el escudo rosa que acaba en punta."""
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
    # la boca: las dos mandibulas son medio rectangulo y medio triangulo (la planta acaba en
    # punta), con la bisagra atras. La de arriba: lila por encima y en la proa, con la gema en
    # la arista, y los colmillos colgando por todo el borde del paladar. La de abajo: una bandeja
    # rosa por dentro, con el borde de marmol y los dientes rojos en escalon; abierta, de frente
    # es el escudo rosa que acaba en punta debajo de la visera.
    Mu = _mandibula_arriba(Mh)
    W, R, L = 4.1, 2.6, 4.5
    prisma5(out, Mu, W, 0.0, 1.6, R, L, {'arriba': P['hueso'], 'proa': P['hueso'], 'lados': P['capucha'], 'atras': P['capucha'],
                                         'abajo': P['boca']}, semilla=7)
    n = _dir(Mu, (0.0, 0.0, 1.0))
    Mg = em.marco(punto(Mu, (0.0, 0.85, L)) + n * 0.05, n)
    cubo(out, Mg @ vr.Rz(45 * D), -0.36, -0.36, 0, 0.72, 0.72, 0.06, None, caras={'frente': P['gema']}, semilla=9)
    cubo(out, Mh, -0.32, 2.0, -1.8, 0.64, 0.42, 1.9, P['hueso'], semilla=11)                       # la cresta
    for j, (x, z, ang) in enumerate(borde5(W - 0.45, R, L - 0.35, 0.5)):                           # los colmillos, por el borde
        M = Mu @ vr.T(x, 0.05, z) @ vr.Ry(ang + math.pi / 2)
        colmillo(out, M, 0.44, 0.95 + 0.35 * (j % 2), 0.16, P['colmillo'], semilla=12 + j % 9)
    # la de abajo
    Ml = Mh @ vr.T(0, -0.3, -0.2) @ vr.Rx(40 * D)
    prisma5(out, Ml, 3.9, -1.3, 0.0, 2.3, 4.3, {'arriba': P['boca'], 'abajo': P['marmol'], 'lados': P['marmol'],
                                                 'proa': P['marmol'], 'atras': P['capucha']}, semilla=33)
    for j, (x, z, ang) in enumerate(borde5(3.9 - 0.4, 2.3, 4.3 - 0.35, 0.52)):                     # los dientes rojos, en escalon
        M = Ml @ vr.T(x, 0, z) @ vr.Ry(ang)
        alto = 0.42 + 0.14 * (j % 2)
        cubo(out, M, -0.12, 0, -0.13, 0.24, alto, 0.26, P['diente_bajo'], semilla=40 + j % 7)
        cubo(out, M, -0.09, alto, -0.1, 0.18, 0.18, 0.18, P['diente_bajo'], semilla=47 + j % 7)
    # al fondo de la boca, la garganta que brilla
    Mv = em.marco(punto(Mh, (0.0, -0.2, 0.05)), _dir(Mh, (0.0, 0.05, 1.0)))
    cubo(out, Mv, -1.3, -1.3, 0, 2.6, 2.6, 0.05, None, caras={'frente': P['nucleo']}, semilla=49)
    if k == 'C':
        return
    # los dos cuernos lila de la visera
    for s in (1, -1):
        Mu = _mandibula_arriba(Mh)
        p = punto(Mu, (s * 1.45, 1.5, 0.9))
        pua(out, em.marco(p, _dir(Mh, (s * 0.5, 1.0, -0.25))) @ vr.Rx(90 * D), 0.26, 3.2, P['hueso'], semilla=50)


def _mandibula_arriba(Mh):
    """El marco de la mandibula de arriba: bisagra atras y un poco levantada."""
    return Mh @ vr.T(0, -0.3, -0.2) @ vr.Rx(-14 * D)


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
    Mu = _mandibula_arriba(Mh)
    for j, z in enumerate((0.6, 1.5, 2.4)):
        y0, y1 = -0.15, 1.8
        for s in (1, -1):
            if j == 2 and s < 0:
                continue
            viga(out, punto(Mu, (s * 2.3, y0, z)), punto(Mu, (s * 2.3, y1, z)), 0.34, 0.34, P['oxido'], semilla=114)
        viga(out, punto(Mu, (-2.3 if j < 2 else 0.4, y1, z)), punto(Mu, (2.3, y1, z)), 0.34, 0.34, P['oxido'], semilla=115)
    for s in (1, -1):
        viga(out, punto(Mu, (s * 0.9, 1.82, 0.3)), punto(Mu, (s * 0.9, 1.82, 3.2)), 0.3, 0.3, P['oxido'], semilla=116)
    p0 = punto(Mu, (-2.3, -0.1, 2.4))                                             # una cadena rota que cuelga del bozal
    cadena(out, p0, p0 + np.array((-0.4, -4.2, 0.4)), 0.8, P['oxido'], semilla=117)
    _gancho_negro(out, Mh, P, 1)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

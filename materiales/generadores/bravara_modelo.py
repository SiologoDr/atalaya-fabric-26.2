"""
Bravara y sus tipos (15-10-2026). Juan, al rechazar a Sedara: «estamos haciendo el mismo formato de bosses en vez de
hacer variedad y calidad; estamos haciendo cantidad copiando de disenos anteriores». Desde Cerbero, casi todos los jefes
llevaban la misma cabeza (una caja oscura con la quijada caida y el paladar en columna de luz), el cuerpo negro de un
solo neon y la misma noche. Bravara rompe con todo eso a la vez y se hace entero aqui, sin piezas de otros jefes:

  - la forma: un pez luchador colosal que flota sobre su estanque en plena exhibicion, con las agallas abiertas y
    todas las aletas desplegadas detras de la cabeza, como un abanico de estandartes;
  - la cabeza: corta, roma y alta, con la frente abombada, los ojos grandes bajo una ceja de hueso y la boca hacia
    arriba (la quijada de abajo, enorme, sale mas que la de arriba), con agujas por dientes; la luz no esta en el
    paladar sino al fondo de la garganta, en anillos, y en las branquias;
  - lo que la enmarca: las agallas abiertas, redondas, y la barba oscura que asoma por su canto;
  - el color: el cuerpo de su color (rojo, azul o blanco de carpa) y las aletas en dos bandas, como las de las
    «mariposa»; no un cuerpo negro;
  - la escena: un estanque de lotos al atardecer, no la noche.

Los tres tipos tienen la misma pose y cambian la cola, las aletas, lo que lleva en la frente y el color:

    A  la Media Luna   cola en media luna de canto liso; dos cuernos echados atras; roja, aletas de canto rosa palido
    B  la Corona       la tela llega a media aleta y los radios siguen en puas; corona de puas en la frente; azul y
                       mostaza
    C  la Doble Cola   la cola partida en dos y la aleta del lomo muy alta; dos barbillones; blanca con manchas de carpa
"""
import math
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _escamas, _escamas_cara, _manchas, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.55
ALTURA = 1.2            # lo que flota sobre el agua (en bloques)
CABEZA = 1.3            # la cabeza (con las agallas y lo de la frente), mas grande que la de un pez de verdad

VARIANTES = {
    'A': dict(
        clave='BA', nombre='la Media Luna', corto='media_luna', cola='media_luna', frente='cuernos',
        cuerpo=_r('2a060a', '560a12', '8a121c', 'b41c26', 'd8343a'),
        brillo=_r('3a0a12', '6a1420', '9a2430', 'd04a52', 'f4868a'),
        aleta=_r('2a050a', '58091a', '8a1224', 'b81e2e', 'dc3a40'),
        aleta2=_r('a86070', 'd0909c', 'ecc0c6', 'f8e0e2', 'fff6f6'),
        canto=_r('100204', '1e0408', '30080c', '480e14', '641a1e'),
        rayo=_r('2a0408', '4a0a10', '6e1218', '942028', 'b83236'),
        barba=_r('0c0204', '1a0408', '2a080c', '421016', '5e1a20'),
        antifaz=_r('120206', '22040a', '360810', '4e0e18', '6a1822'),
        vientre=_r('8a4a50', 'b87278', 'dc9ea2', 'f2c8ca', 'fce6e6'),
        cuerno=_r('6a4a0a', 'a8781a', 'd8a830', 'f0cc5a', 'fff0a0'),
        neon=('fff2c8', 'ffb21a', '6a3a04'),
        manchas=None,
    ),
    'B': dict(
        clave='BB', nombre='la Corona', corto='corona', cola='corona', frente='corona',
        cuerpo=_r('060a16', '0e1a2e', '182c48', '244064', '345a84'),
        brillo=_r('0e2a3a', '164a5e', '1e7086', '34a0ae', '6ad2d2'),
        aleta=_r('080e1c', '122036', '1c3454', '284a72', '386694'),
        aleta2=_r('6a5408', 'a8860e', 'd4ae1e', 'f0d03e', 'fff08a'),
        canto=_r('2a2406', '4a400a', '6e5e10', '98821a', 'c2a82a'),
        rayo=_r('0a1220', '16243a', '243a56', '345474', '4a7096'),
        barba=_r('04060c', '080c18', '101828', '1a263c', '283a56'),
        antifaz=_r('02040a', '060a14', '0c1420', '141e30', '1e2c44'),
        vientre=_r('3a4a5a', '5a6e82', '8496aa', 'b0c0d0', 'dce6ee'),
        cuerno=_r('5a4608', '8e7010', 'c09a1a', 'e6c234', 'fae27a'),
        neon=('ffe6f8', 'ff3ab8', '6a0448'),
        manchas=None,
    ),
    'C': dict(
        clave='BC', nombre='la Doble Cola', corto='doble_cola', cola='doble', frente='barbillones',
        cuerpo=_r('9a96a0', 'c4c0c8', 'e2dee4', 'f2eff4', 'fdfcfe'),
        brillo=_r('a8b0c4', 'ccd4e4', 'e6ecf6', 'f4f8fc', 'ffffff'),
        aleta=_r('a8a4b0', 'c8c4d0', 'e0dde6', 'efedf3', 'faf9fc'),
        aleta2=_r('8a84b4', 'aaa4d0', 'c8c4e6', 'e2e0f4', 'f6f4fe'),
        canto=_r('3a3460', '524a84', '6a62a6', '8a84c4', 'aaa6dc'),
        rayo=_r('8e8a98', 'aca8b6', 'c8c4d0', 'dedbe4', 'f0eef4'),
        barba=_r('140608', '260a0e', '3c1014', '58181c', '762428'),
        antifaz=_r('5a0606', '960c0c', 'c81a16', 'e4362a', 'f6624a'),
        vientre=_r('a49ca8', 'cac4ce', 'e6e2ea', 'f6f4f8', 'ffffff'),
        cuerno=_r('5a0606', '960c0c', 'c81a16', 'e4362a', 'f6624a'),
        neon=('fff0ea', 'ff4a3a', '6a0a04'),
        manchas=None,
    ),
}


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


# la agalla, vista de lado, en el plano y-z de su marco: recta delante (la bisagra, z = 0) y redonda atras
AG_Z0, AG_Z1, AG_Y0, AG_Y1 = -6.6, 0.0, -5.0, 4.0
AG_C = (-0.5, -0.6)          # el centro de la curva (y, z) y sus radios
AG_R = (4.5, 6.0)


def _dentro_agalla(y, z):
    """Si un punto (y, z) de la placa queda dentro de la agalla: delante es recta y atras es media elipse."""
    dy, dz = (y - AG_C[0]) / AG_R[0], (z - AG_C[1]) / AG_R[1]
    return (z >= AG_C[1]) | (dy * dy + dz * dz <= 1.0)


# ----------------------------------------------------------------------
#  Los pintores, todos propios
# ----------------------------------------------------------------------
def pintores(V):
    """Las texturas de Bravara: las escamas con su brillo, la cabeza de escama menuda, el labio, las aletas en dos
    bandas con sus radios, las agallas recortadas en redondo, las branquias y la garganta encendidas, la barba, los
    ojos, los cuernos y las agujas de los dientes."""
    k = V['clave']
    P = {}
    neo = [nm._hex(c) for c in V['neon']]

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'bra%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def colorear(idx, s, tw, th, brillo=True):
        """El color de cada pixel: la escama en el color del pez y su brillo (el centro) un poco mas vivo; en la Doble
        Cola, manchas grandes de naranja y de negro, como una carpa."""
        img = _imagen(idx, V['cuerpo'])
        if brillo:
            img = np.where((idx >= 4)[..., None], _imagen(idx, V['brillo']), img)
        if V['manchas'] is not None:
            naranja, negro = V['manchas']
            m1 = _manchas(tw, th, s, celda=16.0, umbral=0.6, alto=0.92) >= 3
            m2 = _manchas(tw, th, s + 17, celda=12.0, umbral=0.78, alto=0.97) >= 3
            img = np.where(m1[..., None], _imagen(idx, naranja), img)
            img = np.where((m2 & ~m1)[..., None], _imagen(idx, negro), img)
        return img

    def escamas(tw, th, cara, s):
        """El costado: escamas grandes en U, con el canto oscuro y el centro que brilla."""
        idx = _escamas_cara(tw, th, cara)
        if cara == 'arriba':
            idx = np.clip(idx - 1, 0, 4)
        elif cara == 'abajo':
            idx = np.clip(idx + 1, 0, 4)
        return colorear(_bisel(idx, 1, 1), s, tw, th), None
    reg('escamas', escamas)

    def cabeza(tw, th, cara, s):
        """La piel de la cabeza: escama menuda, con su canto."""
        idx = _escamas(tw, th, sw=4, sh=3)
        idx = np.where(idx >= 3, 3, idx)
        if cara == 'arriba':
            idx = np.clip(idx - 1, 0, 4)
        return colorear(_bisel(idx, 1, 1), s + 5, tw, th, brillo=False), None
    reg('cabeza', cabeza)

    def antifaz(tw, th, cara, s):
        """El antifaz: la cara de arriba, mas oscura, de escama menuda (en la Doble Cola, la piel de carpa)."""
        if V['antifaz'] is None:
            return cabeza(tw, th, cara, s)
        idx = _escamas(tw, th, sw=4, sh=3)
        idx = np.where(idx >= 3, 3, idx)
        return _imagen(_bisel(idx, 1, 1), V['antifaz']), None
    reg('antifaz', antifaz)

    def barbilla(tw, th, cara, s):
        """La barbilla y la garganta: claras y lisas, con pliegues de traves, como la panza de un pez."""
        ys, xs = np.mgrid[0:th, 0:tw]
        de_traves = xs if cara in ('arriba', 'abajo') else ys
        idx = np.where(de_traves % 4 == 0, 2, 3)
        return _imagen(_bisel(idx, 1, 1), V['vientre']), None
    reg('barbilla', barbilla)

    def labio(tw, th, cara, s):
        """El labio: grueso y liso, del color del pez, con una veta clara."""
        idx = np.full((th, tw), 3)
        idx[th // 2:, :] = 2
        if th >= 4:
            idx[1, :] = 4
        return _imagen(_bisel(idx, 0, 1), V['cuerpo']), None
    reg('labio', labio)

    def paladar(tw, th, cara, s):
        """El cielo de la boca: carne oscura con pliegues de traves."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys % 3 == 0, 3, 2)
        return _imagen(idx, V['barba']), None
    reg('paladar', paladar)

    def suelo_boca(tw, th, cara, s):
        """El suelo de la boca: carne oscura con un surco por el medio."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(abs(xs - tw / 2 + 0.5) < 1, 1, 3)
        return _imagen(idx, V['barba']), None
    reg('suelo_boca', suelo_boca)

    def garganta(tw, th, cara, s):
        """El fondo de la garganta: anillos de luz uno dentro de otro (los arcos de las branquias) y el nucleo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        d = np.maximum(abs(xs - cx) / max(cx, 1), abs(ys - cy) / max(cy, 1))
        anillo = np.minimum((d * 6).astype(int), 5)
        oscuro = tuple(V['barba'][1])
        cols = [neo[0], neo[0], neo[1], oscuro, neo[1], oscuro]
        t = np.zeros((th, tw, 4), np.uint8)
        for i, c in enumerate(cols):
            t[anillo == i] = (*c, 255)
        return t, None
    reg('garganta', garganta, pleno=True)

    def branquia(tw, th, cara, s):
        """Las branquias bajo las agallas: cuatro arcos de laminillas, curvos como los de un pez, encendidos en el canto
        y oscuros en la raiz, sobre la carne oscura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = (xs + 0.5) / tw if cara == 'der' else 1 - (xs + 0.5) / tw     # 0 delante (la bisagra), 1 atras
        y = (ys + 0.5) / th
        d = np.hypot(f * 1.15, (y - 0.5) * 1.3)                          # arcos alrededor de la bisagra
        banda = (d * 9).astype(int)
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*V['barba'][1], 255)
        arco = (banda % 2 == 1) & (banda < 9)
        fila = (ys % 2 == 0)
        t[arco] = (*neo[2], 255)
        t[arco & fila] = (*neo[1], 255)
        luz = arco & fila & ((d * 9) % 1 > 0.5)
        t[luz] = (*neo[0], 255)
        return t, _emis(t, arco & fila, 255)
    reg('branquia', branquia)

    def mascara_agalla(tw, th, cara):
        """La forma de la agalla en la textura de su cara grande: recortada en redondo por detras."""
        ys, xs = np.mgrid[0:th, 0:tw]
        y = AG_Y1 - (ys + 0.5) / th * (AG_Y1 - AG_Y0)
        f = (xs + 0.5) / tw
        z = AG_Z1 - f * (AG_Z1 - AG_Z0) if cara == 'der' else AG_Z0 + f * (AG_Z1 - AG_Z0)
        return _dentro_agalla(y, z), y, z

    def operculo(tw, th, cara, s):
        """La agalla por fuera: una placa lisa de anillos de crecimiento alrededor de la bisagra, el canto de atras mas
        claro y la forma redonda."""
        m, y, z = mascara_agalla(tw, th, cara)
        d = np.hypot((y - AG_C[0]) / AG_R[0], (z - 0.6) / (AG_R[1] + 0.6))
        idx = np.where(np.isin((d * 7).astype(int), (3, 5)), 2, 3)
        dy, dz = (y - AG_C[0]) / AG_R[0], (z - AG_C[1]) / AG_R[1]
        canto = (z < AG_C[1]) & (dy * dy + dz * dz > 0.78)
        idx = np.where(canto, 4, idx)
        img = colorear(idx, s + 9, tw, th, brillo=True)
        img[..., 3] = np.where(m, 255, 0)
        return img, None
    reg('operculo', operculo)

    def forro(tw, th, cara, s):
        """La agalla por dentro: rojo oscuro de branquia, con la misma forma."""
        m, y, z = mascara_agalla(tw, th, 'izq' if cara == 'der' else 'der')
        idx = np.full((th, tw), 1)
        idx[::3, :] = 2
        img = _imagen(idx, V['barba'])
        img[..., 3] = np.where(m, 255, 0)
        return img, None
    reg('forro', forro)

    def tela(parte):
        def f(tw, th, cara, s):
            """La tela de la aleta, entre dos radios: en la raiz, el color del pez cada vez mas vivo; en la punta, la
            banda clara de las «mariposa» y el canto fino y oscuro; los radios en los bordes."""
            ys, xs = np.mgrid[0:th, 0:tw]
            t_ = 1.0 - ys / max(th - 1, 1)                   # 0 en el canto (fila 0), 1 en la raiz
            if parte == 'raiz':
                idx = np.where(t_ > 0.6, 1, np.where(t_ > 0.25, 2, 3))
                img = _imagen(idx, V['aleta'])
            else:
                idx = np.where(t_ > 0.62, 3, np.where(t_ > 0.18, 2, 3))
                img = np.where((t_ > 0.62)[..., None], _imagen(np.full((th, tw), 4), V['aleta']),
                               _imagen(idx, V['aleta2']))
                canto = ys < max(1, th // 16)
                img = np.where(canto[..., None], _imagen(np.full((th, tw), 2), V['canto']), img)
            if V['manchas'] is not None:
                naranja, _ = V['manchas']
                m = _manchas(tw, th, s + 3, celda=12.0, umbral=0.66, alto=0.92) >= 3
                img = np.where(m[..., None], _imagen(np.full((th, tw), 3), naranja), img)
            return img, None
        return f
    reg('aleta_raiz', tela('raiz'))
    reg('aleta_punta', tela('punta'))

    def cinta(clara):
        def f(tw, th, cara, s):
            """Las ventrales: una cinta del color de la aleta, con el borde mas oscuro; la punta, de la banda clara."""
            ys, xs = np.mgrid[0:th, 0:tw]
            idx = np.where((xs == 0) | (xs == tw - 1), 2, 3)
            return _imagen(idx, V['aleta2'] if clara else V['aleta']), None
        return f
    reg('cinta', cinta(False))
    reg('cinta_punta', cinta(True))

    def anillo(tw, th, cara, s):
        """Los anillos de la garganta: hueso que brilla con la luz del fondo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[1], 255)
        t[(ys + xs) % 4 == 0] = (*neo[0], 255)
        return t, None
    reg('anillo', anillo, pleno=True)

    def rayo(tw, th, cara, s):
        """El radio de la aleta: hueso del color de la aleta, con nudos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo = ys if cara in ('arriba', 'abajo') else xs
        idx = np.where(a_lo_largo % 5 == 0, 1, 3)
        return _imagen(idx, V['rayo']), None
    reg('rayo', rayo)

    def pua(tw, th, cara, s):
        """Las puas de la Corona: el radio que sigue fuera de la tela, del color de la banda clara."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo = ys if cara in ('arriba', 'abajo') else xs
        idx = np.where(a_lo_largo % 6 == 0, 2, 3)
        return _imagen(idx, V['aleta2']), None
    reg('pua', pua)

    def barba(tw, th, cara, s):
        """La barba: tela oscura con pliegues que bajan hasta el canto, un poco mas claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 2) % 2 == 0, 2, 1)
        idx = np.where(ys < max(1, th // 8), 4, idx)
        return _imagen(idx, V['barba']), None
    reg('barba', barba)

    def ojo(tw, th, cara, s):
        """El ojo: grande y oscuro, con un anillo de luz, la pupila rasgada y un brillo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        d = np.hypot((xs - cx) / max(cx, 1), (ys - cy) / max(cy, 1))
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*V['barba'][0], 255)
        anillo = (d < 0.92) & (d > 0.45)
        t[anillo] = (*neo[1], 255)
        t[(d <= 0.45)] = (*neo[0], 255)
        pupila = (abs(xs - cx) < max(0.6, tw * 0.1)) & (abs(ys - cy) < th * 0.4)
        t[pupila] = (*V['barba'][0], 255)
        return t, _emis(t, (d < 0.92) & ~pupila, 255)
    reg('ojo', ojo)

    def cuerno(tw, th, cara, s):
        """El cuerno: hueso en anillos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo = ys if cara in ('arriba', 'abajo') else xs
        idx = np.where(a_lo_largo % 4 == 0, 1, np.where(a_lo_largo % 4 == 1, 3, 2))
        return _imagen(_bisel(idx, 1, 0), V['cuerno']), None
    reg('cuerno', cuerno)

    def barbillon(tw, th, cara, s):
        """El barbillon de carpa: liso, del naranja de las manchas, mas claro en la punta."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t_ = ys / max(th - 1, 1)
        idx = np.where(t_ < 0.7, 2, 3)
        return _imagen(idx, V['cuerno']), None
    reg('barbillon', barbillon)

    DIENTE = _r('8a8070', 'b8ae9c', 'ddd4c2', 'f2ecdf', 'fffcf4')

    def agujas(base_arriba):
        def f(tw, th, cara, s):
            """Las agujas: dientes largos y finos, uno largo y uno corto, con la cara de la luz mas clara."""
            t = np.zeros((th, tw, 4), np.uint8)
            paso = 4
            for i, x0 in enumerate(range(0, tw - 2, paso)):
                largo = th if i % 2 == 0 else int(th * 0.6)
                for y in range(largo):
                    w = 3.0 * (1 - y / max(largo, 1))
                    if w < 0.5:
                        continue
                    yy = y if base_arriba else th - 1 - y
                    for x in range(x0, min(tw, x0 + int(math.ceil(w)))):
                        c = DIENTE[3] if x - x0 < w / 2 else DIENTE[1]
                        t[yy, x] = (*c, 255)
            return t, None
        return f
    reg('dientes_arriba', agujas(True))
    reg('dientes_abajo', agujas(False))

    def sierra(base_arriba):
        def f(tw, th, cara, s):
            """Los dientes de sierra, de pirana: triangulos anchos y apretados, con la cara de la luz mas clara y el
            canto oscuro."""
            t = np.zeros((th, tw, 4), np.uint8)
            paso = 5
            for x0 in range(0, tw - 1, paso):
                for y in range(th):
                    w = paso * (1 - y / max(th, 1))
                    if w < 0.6:
                        continue
                    yy = y if base_arriba else th - 1 - y
                    a, b = x0 + (paso - w) / 2, x0 + (paso + w) / 2
                    for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                        c = DIENTE[3] if x < x0 + paso / 2 else DIENTE[1]
                        if x == int(math.floor(a)) or x == int(math.ceil(b)) - 1:
                            c = DIENTE[0]
                        t[yy, x] = (*c, 255)
            return t, None
        return f
    reg('sierra_arriba', sierra(True))

    def colmillo(tw, th, cara, s):
        """El colmillo: un diente largo en punta (la punta arriba), con la cara de la luz mas clara y el canto oscuro."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            w = tw * (y + 1) / th
            a, b = (tw - w) / 2, (tw + w) / 2
            for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                c = DIENTE[4] if x < tw / 2 else DIENTE[2]
                if x == int(math.floor(a)) or x == int(math.ceil(b)) - 1:
                    c = DIENTE[0]
                t[y, x] = (*c, 255)
        return t, None
    reg('colmillo', colmillo)
    reg('sierra_abajo', sierra(False))

    def brasa(tw, th, cara, s):
        """La luz de dentro de la boca, que se ve entre los dientes."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[1], 255)
        t[(xs + 2 * ys) % 5 == 0] = (*neo[0], 255)
        return t, None
    reg('brasa', brasa, pleno=True)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def tronco(out, P, pts, rs, achata, semilla=0):
    """El cuerpo, alto y estrecho, en tramos de dos cajas cruzadas (seccion de ocho lados)."""
    for j in range(len(pts) - 1):
        p0, p1 = np.asarray(pts[j], float), np.asarray(pts[j + 1], float)
        d = p1 - p0
        L = float(np.linalg.norm(d))
        M = em.marco(p0, d, up=(0.0, 1.0, 0.0))
        r = (rs[j] + rs[j + 1]) / 2
        for kx, ky in ((1.0, 0.8), (0.72, 1.0)):
            bm.cubo(out, M, -r * kx, -r * ky * achata, -r * 0.3, 2 * r * kx, 2 * r * ky * achata, L + r * 0.6,
                    P['escamas'], semilla=semilla + j % 4)


def membrana(out, P, raices, medias, puntas, semilla=0, rayos=True, grosor=0.13, solo_raiz=False):
    """Una aleta de tela de radios curvos: entre cada dos radios, una lamina de la raiz a la mitad y otra de la mitad a la
    punta; y los radios de hueso."""
    filas = [(raices, medias, P['aleta_raiz'])] + ([] if solo_raiz else [(medias, puntas, P['aleta_punta'])])
    for ini, fin, pintor in filas:
        for i in range(len(ini) - 1):
            a, b = np.asarray(ini[i], float), np.asarray(ini[i + 1], float)
            c, d = np.asarray(fin[i + 1], float), np.asarray(fin[i], float)
            ancho = max(float(np.linalg.norm(c - d)), float(np.linalg.norm(b - a)), 0.4)
            alto = max((float(np.linalg.norm(d - a)) + float(np.linalg.norm(c - b))) / 2, 0.4)
            lamina(out, (a, b, c, d), pintor, ancho, alto, semilla=semilla + i % 5)
    if rayos:
        for a, m, d in list(zip(raices, medias, puntas))[::2]:
            jm.tubo(out, [np.asarray(a, float), np.asarray(m, float), np.asarray(d, float)], [grosor * 1.6, grosor, grosor * 0.5],
                    [P['rayo'], P['rayo']], semilla=semilla + 2)


def radios(raices, normales, largos, atras, curva=1.0):
    """Los radios curvos: salen por su normal y se van echando atras hacia la punta."""
    medias, puntas = [], []
    for r, n, L in zip(raices, normales, largos):
        r, n = np.asarray(r, float), _u(n)
        m = r + _u(n + atras * 0.35 * curva) * L * 0.5
        medias.append(m)
        puntas.append(m + _u(n * 0.7 + atras * 1.1 * curva) * L * 0.55)
    return medias, puntas


def tira(out, pintor, ctrl, ancho, semilla=0, n=8, fin=0.25, punta=None):
    """Una aleta en cinta (las ventrales y los barbillones): una tira que se afina hacia la punta, de canto."""
    pts, _, ts = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], n, ((0.0, 1.0), (1.0, 1.0)))
    filas = []
    for k, p in enumerate(pts):
        t_ = _u(pts[min(k + 1, n)] - pts[max(k - 1, 0)])
        lado = _u(np.cross(t_, (1.0, 0.0, 0.0)))
        w = ancho / 2 * (1.0 - (1.0 - fin) * ts[k])
        filas.append((p - lado * w, p + lado * w))
    L_total = sum(float(np.linalg.norm(pts[k + 1] - pts[k])) for k in range(n))
    for k in range(n):
        (a0, b0), (a1, b1) = filas[k], filas[k + 1]
        pin = punta if punta is not None and k >= n * 0.6 else pintor
        lamina(out, (a1, b1, b0, a0), pin, max(float(np.linalg.norm(b0 - a0)), 0.4), max(L_total / n, 0.4),
               semilla=semilla + k % 3)


def hilera(out, M, puntos, y, alto, pintor, semilla=0, arriba=False):
    """Una fila de agujas a lo largo del borde de la quijada (puntos en x-z, a la altura y): una lamina por tramo, que
    baja (alto < 0) o sube."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado, h = float(np.linalg.norm(B - A)), abs(alto)
        if arriba:
            lamina(out, (A, B, B2, A2), pintor, lado, h, semilla + j)
        else:
            lamina(out, (A2, B2, B, A), pintor, lado, h, semilla + j)


def cabeza(out, Mh, P, V, abre=28.0, semilla=0):
    """La cabeza de pez, con el hocico hacia +z: estrecha y alta, en cuna, que se afila hacia el hocico, con la frente
    abombada y el antifaz oscuro. La boca va en diagonal hacia arriba: la quijada de abajo es una hoja larga que sube
    hasta la punta y sale mas que la de arriba, con dos colmillos grandes que suben de la barbilla; abierta, hace una V
    con agujas en los dos labios y, al fondo, la garganta encendida. Los ojos, saltones, van a los lados bajo una ceja de
    hueso. Devuelve el fondo de la boca y la boca."""
    pc, af, pal, lab, bb = P['cabeza'], P['antifaz'], P['paladar'], P['labio'], P['barbilla']
    # el craneo y el hocico: cajas cada vez mas estrechas y mas bajas hacia delante
    pal_f = {'frente': pal}
    bm.cubo(out, Mh, -2.7, -4.6, -4.2, 5.4, 10.2, 3.4, af, caras=pal_f, semilla=semilla)
    bm.cubo(out, Mh, -2.5, -0.2, -1.0, 5.0, 5.6, 2.6, af, caras={'abajo': pal}, semilla=semilla + 1)
    bm.cubo(out, Mh, -2.2, -0.1, 1.4, 4.4, 4.5, 2.2, af, caras={'abajo': pal}, semilla=semilla + 2)
    bm.cubo(out, Mh, -1.9, 0.0, 3.4, 3.8, 3.2, 1.8, af, caras={'abajo': pal}, semilla=semilla + 3)
    bm.cubo(out, Mh, -1.5, 0.1, 5.0, 3.0, 2.0, 1.6, af, caras={'abajo': pal}, semilla=semilla + 4)
    bm.cubo(out, Mh, -2.1, 5.4, -3.6, 4.2, 1.2, 4.0, af, semilla=semilla + 5)                       # la frente
    for s in (1, -1):                                                                     # el labio de arriba, por el canto
        bm.cubo(out, Mh, (1.5 if s > 0 else -2.1), -0.3, 1.2, 0.6, 0.8, 5.4, lab, caras={'abajo': pal}, semilla=semilla + 6)
    bm.cubo(out, Mh, -1.5, -0.3, 6.4, 3.0, 0.9, 0.6, lab, caras={'abajo': pal}, semilla=semilla + 6)
    hilera(out, Mh, [(-1.9, 1.0), (-1.8, 4.0), (-1.4, 6.6), (1.4, 6.6), (1.8, 4.0), (1.9, 1.0)], -0.25, -1.1,
           P['dientes_arriba'], semilla=semilla + 7)
    # la garganta, al fondo
    bm.cubo(out, Mh, -1.9, -3.8, 0.4, 3.8, 3.6, 0.4, pal, caras={'frente': P['garganta']}, semilla=semilla + 8)
    # la quijada de abajo: una hoja larga que sube hasta la barbilla
    Mj = Mh @ vr.T(0.0, -0.5, 0.2) @ vr.Rx(abre * D)
    sb = {'arriba': P['suelo_boca'], 'abajo': bb}
    bm.cubo(out, Mj, -2.5, -4.0, -4.0, 5.0, 4.0, 6.0, pc, caras=sb, semilla=semilla + 9)
    bm.cubo(out, Mj, -2.2, -3.0, 2.0, 4.4, 3.4, 2.8, pc, caras=sb, semilla=semilla + 10)
    bm.cubo(out, Mj, -1.8, -2.0, 4.8, 3.6, 2.8, 2.2, pc, caras=sb, semilla=semilla + 11)
    bm.cubo(out, Mj, -1.4, -1.0, 7.0, 2.8, 2.6, 1.4, pc, caras=dict(sb, atras=P['suelo_boca']), semilla=semilla + 12)
    for s in (1, -1):                                                                     # el labio de abajo
        bm.cubo(out, Mj, (1.6 if s > 0 else -2.2), 0.0, 0.0, 0.6, 0.8, 7.2, lab, semilla=semilla + 13)
    bm.cubo(out, Mj, -1.5, 1.2, 7.2, 3.0, 0.7, 1.2, lab, semilla=semilla + 13)
    hilera(out, Mj, [(-2.0, 0.2), (-1.9, 4.6), (-1.4, 7.4), (1.4, 7.4), (1.9, 4.6), (2.0, 0.2)], 0.6, 1.2,
           P['dientes_abajo'], semilla=semilla + 14, arriba=True)
    for s in (1, -1):                                                                     # los dos colmillos de la barbilla
        colmillo(out, Mj, (s * 1.0, 1.4, 7.9), 3.2, 1.3, P, semilla=semilla + 15)
    # los arcos de las branquias, encendidos: en U, uno detras de otro, dentro de la boca
    for n, z in enumerate((1.2, -0.2)):
        Ma = Mj @ vr.T(0.0, -0.2, z)
        for x0, x1, y0, y1 in ((-1.8, 1.8, -0.4, 0.0), (-2.0, -1.6, -0.4, 2.0 - n * 0.5), (1.6, 2.0, -0.4, 2.0 - n * 0.5)):
            caja(out, Ma, x0, x1, y0, y1, -0.2, 0.2, P['anillo'], semilla=semilla + 16)
    # los ojos, saltones, y su ceja
    for s in (1, -1):
        Mo = Mh @ vr.T(s * 2.5, 2.6, 0.0)
        for w, h in ((1.4, 0.95), (1.15, 1.15), (0.95, 1.4)):
            bm.cubo(out, Mo, -0.45, -h, -w, 0.9, 2 * h, 2 * w, af, caras={'der' if s > 0 else 'izq': P['ojo']},
                    semilla=semilla + 17)
        Mc = Mh @ vr.T(s * 2.4, 4.4, 0.2) @ vr.Rx(-14 * D) @ vr.Rz(s * 20 * D)
        caja(out, Mc, -0.7, 0.7, -0.45, 0.45, -2.2, 2.1, af, semilla=semilla + 18)
    return pt(Mh, (0.0, -1.6, 0.8)), pt(Mh, (0.0, -0.4, 4.6))


def colmillo(out, M, base, largo, ancho, P, semilla=0):
    """Un colmillo grande que sube de la barbilla y se curva un poco atras: dos laminas cruzadas, en punta."""
    b = pt(M, base)
    arriba = _u(M[:3, :3] @ np.array((0.0, 1.0, -0.25)))
    for lado in (M[:3, 0], M[:3, 2]):
        l = _u(lado - arriba * (lado @ arriba))
        p0, p1 = b - l * ancho / 2, b + l * ancho / 2
        q0, q1 = p0 + arriba * largo, p1 + arriba * largo
        lamina(out, (p0, p1, q1, q0), P['colmillo'], ancho, largo, semilla)


def agallas(out, Mh, P, V, abre=62.0, semilla=0):
    """Las agallas abiertas a los lados de la cabeza, como dos escudos redondos, con las branquias encendidas debajo y
    la barba oscura que asoma por todo su canto."""
    for s in (1, -1):
        x0 = 2.3 if s > 0 else -2.9
        bm.cubo(out, Mh, x0, -4.8, -8.4, 0.6, 8.6, 6.8, P['forro'], caras={'der' if s > 0 else 'izq': P['branquia']},
                semilla=semilla)
        Mo = Mh @ vr.T(s * 2.75, -0.6, -1.6) @ vr.Ry(-s * abre * D) @ vr.Rx(-4 * D)
        fuera, dentro = ('der', 'izq') if s > 0 else ('izq', 'der')
        x_ = (0.0, 0.45) if s > 0 else (-0.45, 0.0)
        bm.cubo(out, Mo, x_[0], AG_Y0, AG_Z0, 0.45, AG_Y1 - AG_Y0, AG_Z1 - AG_Z0, P['operculo'],
                caras={dentro: P['forro'], 'arriba': None, 'abajo': None, 'atras': None, 'frente': None}, semilla=semilla + 1)
        raices, medias, puntas = [], [], []
        for i, g in enumerate(np.linspace(-90.0, 72.0, 15)):
            a = g * D
            y = AG_C[0] + AG_R[0] * math.sin(a)
            z = AG_C[1] - AG_R[1] * math.cos(a)
            radial = np.array((0.0, math.sin(a), -math.cos(a)))
            L = 3.4 if i % 2 == 0 else 2.4
            base = np.array((x_[0] + x_[1], y, z)) * np.array((0.5, 1.0, 1.0))
            raices.append(pt(Mo, base - radial * 0.4))
            medias.append(pt(Mo, base + radial * L * 0.5 + np.array((s * 0.5, 0.0, 0.0))))
            puntas.append(pt(Mo, base + radial * L + np.array((s * 1.1, -0.3, 0.0))))
        membrana(out, dict(P, aleta_raiz=P['barba'], aleta_punta=P['barba']), raices, medias, puntas,
                 semilla=semilla + 3, rayos=False)


def frente(out, Mh, P, V, semilla=0):
    """Lo que lleva en la frente cada tipo: dos cuernos de oro echados atras que suben en la punta, una corona de puas o
    dos barbillones de carpa que cuelgan de la boca."""
    if V['frente'] == 'cuernos':
        for s in (1, -1):
            pts = [pt(Mh, (s * 1.5, 5.8, -1.0)), pt(Mh, (s * 2.6, 8.6, -1.8)), pt(Mh, (s * 3.6, 11.0, -3.6)),
                   pt(Mh, (s * 4.0, 12.8, -6.4)), pt(Mh, (s * 3.4, 13.4, -9.2))]
            jm.tubo(out, pts, [1.4, 1.2, 0.95, 0.6, 0.14], [P['cuerno']] * 4, semilla=semilla)
    elif V['frente'] == 'corona':
        for i, g in enumerate(np.linspace(-64.0, 64.0, 7)):
            a = g * D
            base = pt(Mh, (math.sin(a) * 1.8, 6.5 - abs(math.sin(a)) * 1.0, -1.6 - abs(math.sin(a)) * 1.4))
            dirl = Mh[:3, :3] @ _u(np.array((math.sin(a) * 0.7, 1.0, -0.6)))
            L = 5.2 - 1.8 * abs(g) / 64.0
            jm.tubo(out, [base, base + dirl * L * CABEZA * 0.5, base + dirl * L * CABEZA], [0.7, 0.45, 0.08], [P['cuerno']] * 2,
                    semilla=semilla)
    else:
        for s in (1, -1):
            a = pt(Mh, (s * 1.6, 0.3, 6.2))
            tira(out, P['barbillon'], [a, pt(Mh, (s * 3.4, -0.6, 7.8)), pt(Mh, (s * 4.6, -4.0, 8.2)),
                                       pt(Mh, (s * 5.0, -8.6, 6.4))], 0.8, semilla=semilla, fin=0.4)


def cola(out, P, V, base, adelante, arriba, semilla=0):
    """La cola de cada tipo, en abanico desde el pedunculo: media luna (de arriba abajo, canto liso), corona (la tela
    llega a media aleta y los radios siguen en puas, de dos en dos) o doble (dos lobulos con una muesca en medio)."""
    base, f, up = np.asarray(base, float), _u(adelante), _u(arriba)
    atras = -f
    tipo = V['cola']
    if tipo == 'doble':
        angulos = list(np.linspace(92.0, 12.0, 8)) + list(np.linspace(-12.0, -92.0, 8))
    else:
        angulos = list(np.linspace(92.0, -92.0, 17))
    raices, medias, puntas = [], [], []
    for g in angulos:
        a = g * D
        d = _u(atras * math.cos(a) + up * math.sin(a))
        L = 15.0
        if tipo == 'doble':
            L = 16.0 - 6.0 * (1 - abs(g) / 92.0) ** 1.4
        r = base + up * math.sin(a) * 1.2
        raices.append(r)
        medias.append(r + d * L * 0.5)
        puntas.append(r + d * L)
    if tipo == 'doble':
        for lob in (slice(0, 8), slice(8, 16)):
            membrana(out, P, raices[lob], medias[lob], puntas[lob], semilla=semilla)
    elif tipo == 'corona':
        corta = [r + (p - r) * 0.62 for r, p in zip(raices, puntas)]
        membrana(out, P, raices, medias, corta, semilla=semilla, rayos=False)
        puas(out, P, raices, puntas, semilla=semilla)
    else:
        membrana(out, P, raices, medias, puntas, semilla=semilla)


def puas(out, P, raices, puntas, semilla=0):
    """Los radios de la Corona: salen de la tela y se parten en dos puas que se abren un poco."""
    for i, (r, p) in enumerate(zip(raices, puntas)):
        r, p = np.asarray(r, float), np.asarray(p, float)
        m = r + (p - r) * 0.6
        jm.tubo(out, [r, m], [0.3, 0.22], [P['rayo']], semilla=semilla + 2)
        lado = _u(np.cross(p - r, (1.0, 0.0, 0.0)))
        for v in (1, -1):
            q = p + lado * v * 0.9
            jm.tubo(out, [m, m + (q - m) * 0.6, q], [0.22, 0.14, 0.04], [P['pua'], P['pua']], semilla=semilla + 3)


def aleta_larga(out, P, V, raices, normales, largos, atras, semilla=0):
    """Una aleta larga a lo largo del cuerpo (la del lomo o la del vientre), de radios curvos echados atras."""
    medias, puntas = radios(raices, normales, largos, atras)
    if V['cola'] == 'corona':
        corta = [np.asarray(m, float) + (np.asarray(p, float) - np.asarray(m, float)) * 0.3 for m, p in zip(medias, puntas)]
        membrana(out, P, raices, medias, corta, semilla=semilla, rayos=False)
        puas(out, P, raices, puntas, semilla=semilla)
    else:
        membrana(out, P, raices, medias, puntas, semilla=semilla)


# ======================================================================
#  BRAVARA
# ======================================================================
def bravara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        ACH = 1.85
        ctrl = [np.array((0.0, 14.2, -15.0)), np.array((0.0, 15.4, -7.5)), np.array((0.0, 16.8, 0.0)),
                np.array((0.0, 18.0, 5.2))]
        ps, rs, ts = jm.a_lo_largo(ctrl, 10, ((0.0, 0.9), (0.35, 2.0), (0.7, 2.5), (1.0, 2.6)))
        tronco(out, P, ps, rs, ACH, semilla=10)
        eje = _u(ps[-1] - ps[-2])
        atras = -_u(ps[-1] - ps[0])
        # la cabeza, alzada un poco
        Mh = vr.T(*(ps[-1] + np.array((0.0, -0.4, -1.0)))) @ em.marco((0.0, 0.0, 0.0), _u(eje + np.array((0.0, 0.12, 0.0))),
                                                                    up=(0.0, 1.0, 0.0)) @ np.diag([CABEZA] * 3 + [1.0])
        fondo, boca = cabeza(out, Mh, P, V, semilla=20)
        agallas(out, Mh, P, V, semilla=40)
        frente(out, Mh, P, V, semilla=50)

        def sobre(t, lado):
            i = t * (len(ps) - 1)
            j = min(int(i), len(ps) - 2)
            w = i - j
            q = ps[j] * (1 - w) + ps[j + 1] * w
            r = rs[j] * (1 - w) + rs[j + 1] * w
            return q + np.array((0.0, lado * r * ACH * 0.9, 0.0))
        # la aleta del lomo y la del vientre, grandes
        alto_lomo = 1.45 if V['cola'] == 'doble' else 1.0
        n = 10
        tl = np.linspace(0.1, 0.62, n)
        aleta_larga(out, P, V, [sobre(t, 1) for t in tl], [(0.0, 1.0, 0.0)] * n,
                    [alto_lomo * (7.0 + 6.0 * math.sin(math.pi * (0.2 + 0.8 * (1 - k / (n - 1))))) for k in range(n)], atras,
                    semilla=60)
        n = 12
        tv = np.linspace(0.03, 0.74, n)
        aleta_larga(out, P, V, [sobre(t, -1) for t in tv], [(0.0, -1.0, 0.0)] * n,
                    [8.0 + 6.5 * math.sin(math.pi * (0.15 + 0.85 * (1 - k / (n - 1)))) for k in range(n)], atras,
                    semilla=70)
        # la cola
        cola(out, P, V, ps[0] + atras * 0.3, -atras, (0.0, 1.0, 0.0), semilla=80)
        # las pectorales, pequenas, detras de las agallas
        for s in (1, -1):
            b = sobre(0.8, 0) + np.array((s * 2.0, -1.6, -0.6))
            raices = [b + np.array((0.0, dy, 0.0)) for dy in (1.0, 0.35, -0.35, -1.0)]
            medias, puntas = radios(raices, [(s * 1.0, dy * 0.5, -0.4) for dy in (1.0, 0.35, -0.35, -1.0)], [4.4] * 4, atras)
            membrana(out, P, raices, medias, puntas, semilla=90)
        # las ventrales, dos cintas largas que cuelgan bajo la cabeza y se van atras
        for s in (1, -1):
            a = sobre(0.7, -1) + np.array((s * 1.1, 0.6, 0.0))
            tira(out, P['cinta'], [a, a + np.array((s * 1.4, -3.2, -1.2)), a + np.array((s * 2.0, -6.8, -3.6)),
                                   a + np.array((s * 1.8, -10.0, -6.8))], 2.2, semilla=95, punta=P['cinta_punta'])
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = vr.T(0.0, ALTURA, 0.0) @ np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    fondo, boca = pt(E, fondo), pt(E, boca)
    return out, {'boca': boca, 'luces': [fondo, boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

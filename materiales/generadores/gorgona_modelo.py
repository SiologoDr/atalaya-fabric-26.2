"""
La Gorgona y sus hermanas (13-10-2026), tercera version. Juan eligio del muestrario de jefas la cara C3,
los brazos B2, B3, B5 y B6, las piernas L2, L3, L4 y L5 y el pecho P1, y pidio «haz los cambios para
Vulpina y la Gorgona»; y sobre el muestrario: «la anatomia que me mostraste es como una nina; debe verse
como una mujer adulta».

Ahora esta hecha con el cuerpo de jefa_modelo (todo de cajas, a lo Blockbench, con cuerpo de mujer
adulta; codos y rodillas que doblan por el canto) y la cara C3 con los ojos de serpiente del color de cada
hermana. Lo suyo de gorgona, tambien de bloques: la cabellera de serpientes vivas (tubos de bloques con
la cabeza, los ojos encendidos, la boca abierta y los colmillos), la diadema de oro con su gema y los
pendientes; y el quiton griego de un solo hombro, con la tira de grecas por el hombro, el cinturon de
grecas bajo el pecho y el de oro en la cintura.

Las tres hermanas cambian de FORMA (y de brazos y piernas del muestrario):

    A  Medusa     el quiton largo hasta los tobillos, abierto por delante para que asome la pierna; la
                  mano en alto, abierta, la que petrifica; la cabellera mas grande; brazos de bloque con
                  brazaletes (B2) y piernas estilizadas con sandalias (L5); esmeralda y oro
    B  Esteno     la arquera: armadura de bronce en los brazos (B5), grebas de bronce (L3), la falda corta
                  con el faldon de tiras de cuero y el arco recurvado en la mano; cobre, carmin y bronce
    C  Euriale    las alas de plumas negras con el borde carmin y el raquis de oro, abiertas; las garras
                  (B6) y las piernas de rodilla limpia con sandalias (L2); la falda corta; negra, oro y
                  carmin
"""
import math, random
import numpy as np
import vigia_render as vr
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen
from sierpe_modelo import _bisel
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
ORO = _r('5a3a08', '8a6014', 'b88a24', 'e0b440', 'fff0a0')
BRONCE = _r('3a2410', '6a4420', '9a6a34', 'c8964c', 'f0c878')
NEGRO = _r('0a090d', '131116', '1c1a22', '29252f', '3b3644')

VARIANTES = {
    'A': dict(
        clave='A', nombre='Medusa',
        piel=_r('8c8486', 'b2a8aa', 'd4cacb', 'e8e0e0', 'f8f2f2'),
        pelo=_r('0a140c', '122016', '1c2e20', '2a422c', '3e5a3e'),
        serpiente=_r('0c2a12', '16461e', '22662c', '3a8a3e', '6ab65a'),
        vientre=_r('5a5a20', '8a8a34', 'b8b44a', 'dcd66c', 'f4f0a0'),
        tela=_r('062a1e', '0c3e2c', '14563c', '1e7050', '2e9068'),
        oro=ORO, metal=BRONCE, cuero=_r('2a1a0e', '4a2e18', '6e4626', '946236', 'b8824a'),
        garra=_r('0a120a', '142014', '203020', '304430', '486048'),
        pelaje=_r('0c2a12', '16461e', '22662c', '3a8a3e', '6ab65a'), medias=NEGRO,
        escama=_r('0c2a12', '16461e', '22662c', '3a8a3e', '6ab65a'),
        neon=('f8ffe0', 'a8ff3a', '2e6a0a'), ojos=('8aee3a', '2a6a0a', 'd4ffa0'), labios='7a4a52', marca='22662c',
        brazos='B2', piernas='L5', falda='larga',
    ),
    'B': dict(
        clave='B', nombre='Esteno',
        piel=_r('7a5a40', 'a07a58', 'c49c76', 'dcbc96', 'f0dcbc'),
        pelo=_r('1e0a06', '34120a', '4c1c0e', '682814', '8a381c'),
        serpiente=_r('3a0a06', '62140c', '8a2a14', 'b04a22', 'd8783a'),
        vientre=_r('6a4a2a', '9a7448', 'c8a070', 'e6c896', 'fae8c0'),
        tela=_r('3a0808', '641010', '8e1c18', 'b42e24', 'd8503a'),
        oro=ORO, metal=BRONCE, cuero=_r('2a0e08', '4a1a10', '6e2a1a', '944028', 'b85a3a'),
        garra=_r('140806', '24100c', '361a14', '4c2a20', '683e30'),
        pelaje=_r('2a0e08', '4a1a10', '6e2a1a', '944028', 'b85a3a'), medias=NEGRO,
        escama=_r('3a0a06', '62140c', '8a2a14', 'b04a22', 'd8783a'),
        neon=('fff4e0', 'ffaa2e', '7a3204'), ojos=('ffaa2e', '8a4a08', 'ffe0a0'), labios='8a3a2a', marca='8a2a14',
        brazos='B5', piernas='L3', falda='corta',
    ),
    'C': dict(
        clave='C', nombre='Euriale',
        piel=_r('4a3428', '6a4a38', '8c644c', 'ac8264', 'cca486'),
        pelo=_r('08080a', '121216', '1c1c22', '2a2a32', '3c3c46'),
        serpiente=_r('08080a', '141418', '222228', '34343e', '4c4c58'),
        vientre=_r('3a3a40', '5a5a64', '7c7c88', 'a0a0ac', 'c8c8d2'),
        tela=_r('0c0a0c', '1a161a', '2a242a', '3c343c', '544a54'),
        oro=ORO, metal=BRONCE, cuero=_r('140e0c', '261c18', '3a2c26', '524036', '6e5848'),
        garra=_r('0a0808', '161212', '241e1e', '362c2c', '4c3e3e'),
        pelaje=BRONCE, medias=NEGRO, pluma=_r('0a0608', '1a0c10', '2c1218', '4a1a22', '8a2a30'),
        escama=_r('1a0608', '2e0a0e', '4a1016', '6e1a1e', '9a2a2a'),
        neon=('ffe8e0', 'ff2a3a', '6a0610'), ojos=('ff3a3a', '8a0a10', 'ff9a8a'), labios='6a1a20', marca='a01a24',
        brazos='B6', piernas='L2', falda='corta',
    ),
}
for _v in VARIANTES.values():
    _v.setdefault('ribete', _v['oro'])
    _v.setdefault('guante', _v['tela'])


def pintores(V):
    """Los pintores del cuerpo (jefa_modelo) y los de la gorgona: las escamas de serpiente, el vientre,
    la cenefa de grecas, el cuero de las tiras, los ojos encendidos de las serpientes y la pluma de bronce."""
    P = jm.pintores(V, 'gor3%s' % V['clave'])
    reg = P['_reg']
    nuc, neo, hon = V['neon']

    def serpiente(tw, th, cara_, s):
        """Las escamas: en filas al tresbolillo, con el canto claro de cada una."""
        ys, xs = np.mgrid[0:th, 0:tw]
        fila = ys // 3
        x = (xs + (fila % 2) * 2) % 4
        idx = np.full((th, tw), 2)
        idx = np.where((ys % 3) == 2, 1, idx)
        idx = np.where(((ys % 3) == 0) & (x == 1), 3, idx)
        idx = np.where(x == 3, np.minimum(idx, 1), idx)
        return _imagen(idx, V['serpiente']), None
    reg('serpiente', serpiente)
    reg('vientre', jm.liso(V['vientre'], 3, 1, 1))

    def greca(tw, th, cara_, s):
        """La cenefa de grecas (el meandro griego) en oro sobre la tela oscura."""
        t = _imagen(np.full((th, tw), 1), V['tela'])
        motivo = ("#####.",
                  "#...#.",
                  "#.#.#.",
                  "#.###.",
                  "#.....",
                  "######")
        largo_x = tw >= th
        for y in range(th):
            for x in range(tw):
                u, v = (x, y) if largo_x else (y, x)
                if motivo[v % 6][u % 6] == '#':
                    t[y, x] = (*V['oro'][3], 255)
        return t, None
    reg('greca', greca)

    def tiras(tw, th, cara_, s):
        """El cuero de las tiras del faldon: liso con un pespunte claro a los lados."""
        idx = np.full((th, tw), 2)
        if th >= tw and tw >= 4:
            idx[:, 1] = 3
            idx[:, -2] = 3
        return _imagen(_bisel(idx, 1, 1), V['cuero']), None
    reg('tiras', tiras)

    def ojo_serpiente(tw, th, cara_, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo_serpiente', ojo_serpiente, pleno=True)
    reg('boca', jm.liso(_r('2a0608', '4a0a10', '6e1218', '8a1c22', 'a82a30'), 1, 0, 0))
    reg('diente', jm.liso(_r('8a8478', 'b8b2a6', 'dcd6ca', 'f2eee4', 'ffffff'), 3, 1, 0))

    def pluma(tw, th, cara_, s):
        """Una pluma de bronce: en las caras grandes, el raquis claro por el medio a lo largo, las barbas en
        bandas y el borde oscuro; en los cantos, lisa."""
        rampa = V.get('pluma', V['metal'])
        idx = np.full((th, tw), 2)
        if th >= tw and tw >= 3:
            ys = np.arange(th)[:, None] + np.zeros((1, tw), int)
            idx[(ys // 2) % 2 == 0] = 1
            idx[:, 0] = 4
            idx[:, -1] = 3
            t = _imagen(idx, rampa)
            t[:, tw // 2] = (*V['oro'][3], 255)
            return t, None
        return _imagen(idx, rampa), None
    reg('pluma', pluma)
    reg('pluma_oscura', jm.liso(V.get('pluma', _r('24160a', '3a2412', '5a3a1e', '7e562c', 'a07040')), 1, 1, 1))
    return P


# ----------------------------------------------------------------------
#  La cabellera de serpientes, la diadema y los pendientes
# ----------------------------------------------------------------------
PERFIL_SERPIENTE = ((0.0, 0.95), (0.4, 1.05), (0.8, 0.85), (1.0, 0.75))


def serpiente(out, P, ctrl, grosor=1.0, semilla=0, abre=28.0):
    """Una serpiente de la cabellera: el cuerpo de bloques que se afina y, al final, la cabeza: el craneo,
    el hocico, los ojos encendidos a los lados, la mandibula abierta con la boca oscura y dos colmillos."""
    pts, rs, ts = jm.a_lo_largo(ctrl, 7, PERFIL_SERPIENTE)
    rs = [r * grosor for r in rs]
    jm.tubo(out, pts, rs, [P['serpiente']] * (len(pts) - 1), semilla=semilla)
    d = pts[-1] - pts[-2]
    M = em.marco(pts[-1], d, up=(0.0, 1.0, 0.0))
    g = grosor
    caja(out, M, -1.15 * g, 1.15 * g, -0.35 * g, 0.75 * g, -0.4 * g, 1.9 * g, P['serpiente'], semilla=semilla + 5)    # el craneo
    caja(out, M, -0.8 * g, 0.8 * g, -0.25 * g, 0.5 * g, 1.8 * g, 2.75 * g, P['serpiente'], semilla=semilla + 6)       # el hocico
    for s in (1, -1):                                                                                                # los ojos
        caja(out, M, s * 1.12 * g - 0.22 * g, s * 1.12 * g + 0.22 * g, 0.15 * g, 0.55 * g, 0.9 * g, 1.45 * g, P['ojo_serpiente'],
             semilla=semilla + 7)
    Mj = M @ vr.T(0, -0.35 * g, -0.2 * g) @ vr.Rx(abre * D)                                                          # la mandibula
    caja(out, Mj, -0.85 * g, 0.85 * g, -0.42 * g, 0.0, 0.0, 2.55 * g, P['serpiente'], semilla=semilla + 8)
    caja(out, Mj, -0.6 * g, 0.6 * g, -0.02, 0.06 * g, 0.6 * g, 2.3 * g, P['boca'], semilla=semilla + 9)
    caja(out, M, -0.62 * g, 0.62 * g, -0.36 * g, -0.26 * g, 0.8 * g, 2.6 * g, P['boca'], semilla=semilla + 10)
    for s in (1, -1):                                                                                                # los colmillos
        caja(out, M, s * 0.48 * g - 0.12 * g, s * 0.48 * g + 0.12 * g, -0.95 * g, -0.3 * g, 2.3 * g, 2.55 * g, P['diente'],
             semilla=semilla + 11)


def cabellera(out, Mh, P, grande=1.0):
    """Las serpientes: cinco que salen de arriba, suben, se arquean y miran hacia delante; cuatro por los
    lados, que se abren y vuelven hacia delante; y cuatro que caen por la espalda y se rizan."""
    def mundo(ctrl):
        return [pt(Mh, c) for c in ctrl]
    n = 0
    for j in range(5):
        f = (j - 2) / 2
        b = np.array((f * 2.6, 8.3, -1.2 - 0.6 * abs(f)))
        k = grande
        ctrl = [b, b + np.array((f * 1.4, 2.4, -0.8)) * k, b + np.array((f * 3.4, 5.0, -0.4)) * k, b + np.array((f * 4.6, 6.4, 1.8)) * k,
                b + np.array((f * 4.9, 5.8, 4.0)) * k]
        serpiente(out, P, mundo(ctrl), grosor=1.0, semilla=40 + n % 5)
        n += 1
    for s in (1, -1):
        for j, (y, z) in enumerate(((6.2, -0.4), (3.8, -1.8))):
            b = np.array((s * 4.5, y, z))
            k = grande
            ctrl = [b, b + np.array((s * 2.4, 0.8, -0.6)) * k, b + np.array((s * 4.8, 0.4, 0.4)) * k,
                    b + np.array((s * 5.8, -0.6 + 0.8 * j, 2.6)) * k, b + np.array((s * 5.2, -0.4 + 0.8 * j, 4.6)) * k]
            serpiente(out, P, mundo(ctrl), grosor=0.95, semilla=40 + n % 5)
            n += 1
    for j in range(4):
        f = (j - 1.5) / 1.5
        b = np.array((f * 2.6, 5.0, -4.6))
        ctrl = [b, b + np.array((f * 0.8, -4.0, -1.0)), b + np.array((f * 2.0, -8.6, -1.4)), b + np.array((f * 3.6, -12.0, 0.4)),
                b + np.array((f * 3.8, -11.4, 2.6))]
        serpiente(out, P, mundo(ctrl), grosor=1.05, semilla=40 + n % 5)
        n += 1


def joyas(out, Mh, P):
    """La diadema de oro sobre el flequillo con su gema encendida, y los pendientes de tres cuentas con la
    gota encendida."""
    caja(out, Mh, -4.65, 4.65, 6.9, 7.55, 3.95, 4.85, P['oro'], semilla=240)
    caja(out, Mh, -0.55, 0.55, 6.75, 7.85, 4.75, 5.05, P['gema'], semilla=241)
    for s in (1, -1):
        for j in range(3):
            y = 2.2 - 0.75 * j
            caja(out, Mh, s * 4.35 - 0.3, s * 4.35 + 0.3, y - 0.3, y + 0.3, 0.2, 0.8, P['oro'], semilla=242)
        caja(out, Mh, s * 4.35 - 0.35, s * 4.35 + 0.35, -1.0, -0.1, 0.15, 0.85, P['ojo_serpiente'], semilla=243)


# ----------------------------------------------------------------------
#  El quiton y las faldas
# ----------------------------------------------------------------------
def quiton(out, P, falda):
    """El quiton de un hombro: el torso de tela con el pecho P1 y su ribete de oro; la tira de grecas que
    sube por el hombro derecho y baja por la espalda (el izquierdo, al aire); el cinturon de grecas bajo el
    pecho y el de oro en la cintura; y la falda: larga y abierta por delante (Medusa) o corta (Esteno y
    Euriale)."""
    tl = P['tela_lisa']
    jm.torso(out, P, {'cadera': tl, 'cintura': tl, 'pecho': tl, 'busto': P['tela'], 'ribete': P['oro']})
    caja(out, jm.I4, -3.5, -1.5, 37.8, 41.75, 1.95, 2.4, P['greca'], semilla=50)                      # la tira del hombro
    caja(out, jm.I4, -3.5, -1.5, 41.5, 41.95, -2.35, 2.4, P['greca'], semilla=51)
    caja(out, jm.I4, -3.5, -1.5, 36.5, 41.75, -2.4, -1.95, P['greca'], semilla=52)
    caja(out, jm.I4, -3.6, 3.6, 34.0, 34.9, -2.2, 2.2, P['greca'], semilla=53)                        # bajo el pecho
    caja(out, jm.I4, -3.3, 3.3, 30.6, 31.4, -2.1, 2.1, P['oro'], semilla=54)                          # en la cintura
    if falda == 'larga':
        escalones = [(22.0, 28.4, 4.85, 2.85), (15.0, 22.1, 5.3, 3.2), (8.5, 15.1, 5.9, 3.7), (1.8, 8.6, 6.6, 4.3)]
        for i, (y0, y1, hx_, hz) in enumerate(escalones):
            if y1 <= 22.1:                                       # abierta por delante, del lado izquierdo
                caja(out, jm.I4, -hx_, hx_, y0, y1, -hz, 0.0, P['tela'], semilla=55 + i)
                caja(out, jm.I4, -hx_, 0.4, y0, y1, 0.0, hz, P['tela'], semilla=59 + i)
                caja(out, jm.I4, hx_ - 1.1, hx_, y0, y1, 0.0, hz * 0.55, P['tela'], semilla=63 + i)
            else:
                caja(out, jm.I4, -hx_, hx_, y0, y1, -hz, hz, P['tela'], semilla=55 + i)
        caja(out, jm.I4, -6.65, 0.5, 1.4, 2.4, 0.0, 4.35, P['greca'], semilla=67)                     # el bajo de grecas
        caja(out, jm.I4, -6.65, 6.65, 1.4, 2.4, -4.35, 0.0, P['greca'], semilla=68)
    else:
        caja(out, jm.I4, -4.85, 4.85, 23.6, 28.4, -2.85, 2.85, P['tela'], semilla=55)
        caja(out, jm.I4, -5.3, 5.3, 20.4, 23.7, -3.3, 3.3, P['tela'], semilla=56)
        caja(out, jm.I4, -5.35, 5.35, 19.7, 20.6, -3.35, 3.35, P['greca'], semilla=57)


def faldon(out, P):
    """B: el faldon de tiras de cuero (pteruges) que cuelga del cinturon alrededor de la cadera, cada tira
    con su punta de bronce."""
    n = 14
    for j in range(n):
        a = j * TAU / n
        p = np.array((math.sin(a) * 5.0, 29.0, math.cos(a) * 3.05))
        M = vr.T(*p) @ vr.Ry(a) @ vr.Rx(-8 * D)
        caja(out, M, -0.62, 0.62, -9.0, 0.0, -0.18, 0.18, P['tiras'], semilla=70 + j % 3)
        caja(out, M, -0.7, 0.7, -9.6, -8.6, -0.24, 0.24, P['metal'], semilla=73)


def sandalia(out, P, Mr):
    """Las tiras de oro de la sandalia, cruzadas en la pantorrilla."""
    for j, y in enumerate((-11.0, -9.4, -7.8, -6.2)):
        caja(out, Mr, -1.35 + 0.05 * j, 1.35 - 0.05 * j, y, y + 0.45, -1.4 - 0.08 * j, 1.75, P['oro'], semilla=80)


# ----------------------------------------------------------------------
#  El arco (Esteno) y las alas (Euriale)
# ----------------------------------------------------------------------
def arco(out, P, G, alto=10.0, semilla=0):
    """B: el arco recurvado de bronce en la mano: las dos palas que se curvan hacia atras y vuelven en
    las puntas, la empunadura de grecas y la cuerda."""
    G = np.asarray(G, float)
    puntas = []
    for k, sgn in enumerate((1, -1)):
        ctrl = [G, G + np.array((0.0, sgn * alto * 0.32, 0.6)), G + np.array((0.0, sgn * alto * 0.7, -0.6)),
                G + np.array((0.0, sgn * alto * 0.92, -2.0)), G + np.array((0.0, sgn * alto * 1.02, -1.4))]
        pts, rs, ts = jm.a_lo_largo(ctrl, 6, ((0.0, 0.62), (0.7, 0.42), (1.0, 0.3)))
        jm.tubo(out, pts, rs, [P['metal']] * (len(pts) - 1), semilla=semilla + k, arriba=(1.0, 0.0, 0.0))
        puntas.append(pts[-2])
    a, b = puntas
    jm.tubo(out, [a, b], [0.1, 0.1], [P['diente']], semilla=semilla + 3, arriba=(1.0, 0.0, 0.0))     # la cuerda
    caja(out, vr.T(*G), -0.75, 0.75, -1.3, 1.3, -0.75, 0.75, P['greca'], semilla=semilla + 4)        # la empunadura


def alas(out, P):
    """C: las alas de plumas negras abiertas detras de los hombros: el hueso de bronce en tres tramos y,
    colgando de el, las plumas grandes en abanico (de la mas larga en la punta a las cortas junto al
    cuerpo) con una fila de plumas cortas y oscuras encima."""
    for s in (1, -1):
        R = np.array((s * 1.9, 38.6, -2.6))
        C = R + np.array((s * 7.0, 6.0, -3.0))
        Mm = C + np.array((s * 8.0, 7.0, 0.5))
        T = Mm + np.array((s * 6.5, 3.0, 1.0))
        hueso = [R, C, Mm, T]
        jm.tubo(out, hueso, [1.1, 0.95, 0.75, 0.5], [P['metal']] * 3, semilla=90, arriba=(0.0, 0.0, 1.0))

        def en_hueso(f):
            i = min(int(f * 3), 2)
            return hueso[i] + (hueso[i + 1] - hueso[i]) * (f * 3 - i)
        for j in range(18):                                                  # las remeras
            f = j / 17
            q = en_hueso(f)
            L = 7.0 + 15.0 * f ** 1.3
            d = np.array((s * (0.2 + 0.8 * f), -1.0 + 1.15 * f, -0.25))
            M = em.marco(q, d, up=(0.0, 0.0, 1.0))
            caja(out, M, -1.7, 1.7, -0.22, 0.22, -0.4, L, P['pluma'], semilla=92 + j % 4)
        for fila, (k, largo, z) in enumerate(((0.55, 0.5, 0.3), (0.3, 0.28, 0.55))):  # las coberteras
            for j in range(12):
                f = j / 11
                q = en_hueso(f)
                L = (7.0 + 15.0 * f ** 1.3) * largo
                d = np.array((s * (0.2 + 0.8 * f), -1.0 + 1.15 * f, -0.25))
                M = em.marco(q + np.array((0.0, 0.0, z)), d, up=(0.0, 0.0, 1.0))
                caja(out, M, -1.5, 1.5, -0.2, 0.2, -0.6, L, P['pluma_oscura'] if fila else P['pluma'], semilla=96 + fila)


# ======================================================================
#  LA GORGONA
# ======================================================================
POSES = {
    'A': dict(brazos={1: dict(abd=70, flex=38, codo=58, giro=-80, mun=-30, cierra=0.25),
                      -1: dict(abd=20, flex=8, codo=22, giro=0, mun=0, cierra=0.6)},
              piernas={1: dict(abd=4, flex=16, rodilla=24, pie=0), -1: dict(abd=3, flex=-3, rodilla=4)},
              cabeza=(10, 4)),
    'B': dict(brazos={1: dict(abd=140, flex=12, codo=30, giro=-70, mun=-10, cierra=1.0),
                      -1: dict(abd=68, flex=22, codo=12, giro=0, mun=0, cierra=1.0)},
              piernas={1: dict(abd=8, flex=-6, rodilla=6), -1: dict(abd=8, flex=14, rodilla=20)},
              cabeza=(8, -6)),
    'C': dict(brazos={1: dict(abd=48, flex=30, codo=52, giro=-40, mun=-15, cierra=0.25),
                      -1: dict(abd=48, flex=30, codo=52, giro=-40, mun=-15, cierra=0.25)},
              piernas={1: dict(abd=5, flex=-4, rodilla=5), -1: dict(abd=5, flex=12, rodilla=18)},
              cabeza=(11, 3)),
}


def gorgona(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    pose = POSES[tipo]
    ppb = bm.PPB
    bm.PPB = jm.PPB
    out = []
    try:
        quiton(out, P, V['falda'])
        if tipo == 'B':
            faldon(out, P)
        manos = {}
        for s in (1, -1):
            if V['brazos'] == 'B2':
                c = {'manga': P['tela'], 'puno': P['oro']}
            elif V['brazos'] == 'B5':
                c = {'metal': P['metal'], 'borde': P['oro'], 'manga': P['tela']}
            else:
                c = {'escama': P['escama'], 'pelaje': P['pluma'], 'una': P['garra']}
            manos[s] = jm.brazo(out, P, s, V['brazos'], pose['brazos'][s], c)
            if V['piernas'] == 'L5':
                Mt, Mr, Mp = jm.pierna(out, P, s, 'L5', pose['piernas'][s],
                                       {'media': P['piel'], 'borde': P['oro'], 'pie': 'sandalia', 'zapato': P['oro']})
                sandalia(out, P, Mr)
            elif V['piernas'] == 'L3':
                jm.pierna(out, P, s, 'L3', pose['piernas'][s], {'bota': P['metal'], 'oro': P['oro']})
            else:
                Mt, Mr, Mp = jm.pierna(out, P, s, 'L2', pose['piernas'][s],
                                       {'calcetin': None, 'pie': 'sandalia', 'zapato': P['oro']})
                sandalia(out, P, Mr)
        if tipo == 'B':
            arco(out, P, pt(manos[-1], (0, 1.6, 0)), alto=11.0, semilla=120)
        if tipo == 'C':
            alas(out, P)
        tx, tz = pose['cabeza']
        Mh = vr.T(0.0, jm.CUELLO_Y, 0.2) @ vr.Rx(tx * D) @ vr.Rz(tz * D)
        jm.cabeza(out, Mh, P, V)
        caja(out, Mh, -4.55, 4.55, -6.0, 7.0, -4.95, -3.6, P['pelo'], semilla=59)                      # la melena corta de detras
        cabellera(out, Mh, P, grande=1.2 if tipo == 'A' else 1.0)
        joyas(out, Mh, P)
    finally:
        bm.PPB = ppb
    out = jm.a_escena(out)
    E = np.diag([jm.ESCALA] * 3 + [1.0])
    Mh_e = E @ Mh
    cara = pt(Mh_e, (0.0, 4.0, 4.2))
    return out, {'cabeza': Mh_e, 'cara': cara, 'boca': pt(Mh_e, (0.0, 1.3, 4.2)), 'luces': [],
                 'alza': 0.0}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

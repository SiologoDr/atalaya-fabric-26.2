"""
Vulpina, la Dama de las Nueve Colas (13-10-2026), tercera version. Juan eligio del muestrario de jefas
la cara C3, los brazos B2, B3, B5 y B6, las piernas L2, L3, L4 y L5 y el pecho P1, y pidio «haz los
cambios para Vulpina y la Gorgona»; y sobre el muestrario: «la anatomia que me mostraste es como una
nina; debe verse como una mujer adulta».

Ahora esta hecha con el cuerpo de jefa_modelo (todo de cajas, a lo Blockbench, con cuerpo de mujer
adulta: seis cabezas y media, cintura, caderas y piernas largas; codos y rodillas que doblan por el canto)
y la cara C3 con los ojos del color de cada tipo. Lo suyo de zorra, tambien de bloques: las orejas grandes
en escalones con la punta de color, la melena larga, la mascara de zorro de laca a un lado de la cabeza y
las horquillas de oro al otro; el corpino de kimono con el cuello rojo cruzado en V, el obi con su lazo
detras, el cordon con su gema, la soga sagrada en la cadera con sus papeles en zigzag y la falda corta con
el bajo rasgado; y las nueve colas, tubos de bloques de seccion de ocho lados, con el fuego en la punta.

Los tres tipos cambian de FORMA (y de brazos y piernas del muestrario):

    A  del Abanico   las nueve colas abiertas detras en abanico; los brazos en alto, cada mano con su
                     fuego; guantes largos (B3) y medias con liga (L4); blanca, roja y oro
    B  de la Llama   las colas alzadas como una llama; una garra en alto con un fuego grande y la otra
                     abajo, abierta; garras (B6) y botas altas (L3); negra y carmin
    C  del Manto     dos colas le rodean los hombros como una estola y siete se arrastran detras; una
                     mano en la cadera y en la otra un fuego, y un anillo de fuegos alrededor; armadura de
                     samurai en los brazos (B5) y piernas estilizadas (L5); plata y rosa
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
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
NEGRO = _r('0a090d', '131116', '1c1a22', '29252f', '3b3644')

VARIANTES = {
    'A': dict(
        clave='A', nombre='del Abanico', color='Blanca',
        piel=_r('a07e6e', 'c8a090', 'e6c4b0', 'f4dccb', 'fff0e4'),
        pelo=_r('8a8a96', 'b0b0bc', 'd2d2dc', 'ebebf2', 'ffffff'),
        pelaje=_r('a8a098', 'cac2b8', 'e6dfd4', 'f6f1ea', 'ffffff'),
        punta=_r('7a2a14', 'a8401c', 'd8662a', 'f0904a', 'ffc890'),
        tela=_r('9e968a', 'c4bcae', 'e0d9cc', 'f0ebe2', 'fbf8f2'),
        adorno=_r('3a0808', '6a1010', '9a1a18', 'c42a22', 'e8483a'),
        oro=ORO, metal=_r('5a5a64', '8a8a94', 'b8b8c2', 'dcdce4', 'ffffff'),
        cuero=_r('2a0e08', '4a1a10', '6e2a1a', '944028', 'b85a3a'),
        garra=_r('0c0808', '1a1212', '2a1e1e', '3e2e2e', '5a4444'),
        medias=NEGRO, escama=_r('100608', '200a0e', '3a1016', '5a1a20', '7a2a2a'),
        neon=('fff4e0', 'ffaa3c', '7a3204'), ojos=('ffaa30', '9a4a08', 'ffe090'), labios='b8283a', marca='c42a22',
        brazos='B3', piernas='L4',
    ),
    'B': dict(
        clave='B', nombre='de la Llama', color='Negra',
        piel=_r('8a6a5e', 'b08a7a', 'd0aa98', 'e6c6b4', 'f6e0d0'),
        pelo=_r('08080c', '121218', '1e1e26', '2c2c38', '40404e'),
        pelaje=_r('0a0a0e', '16161c', '24242c', '34343e', '4a4a56'),
        punta=_r('4a0806', '7a1008', 'b0200e', 'e04418', 'ff8a40'),
        tela=_r('0c0a0e', '18141c', '26202c', '362e3e', '4a4054'),
        adorno=_r('3a0606', '6e0e0a', 'a01a10', 'd0301a', 'f05a2e'),
        oro=ORO, metal=_r('5a5a64', '8a8a94', 'b8b8c2', 'dcdce4', 'ffffff'),
        cuero=_r('0c0a0e', '16121a', '221c28', '30283a', '40364c'),
        garra=_r('060406', '100a0c', '1c1418', '2c2024', '403036'),
        medias=NEGRO, escama=_r('140406', '2a080c', '4a0e14', '70181e', 'a02a26'),
        neon=('fff0e0', 'ff4a1e', '6a0a02'), ojos=('ff3a2a', '8a0c0a', 'ff9a7a'), labios='8a1420', marca='d0301a',
        brazos='B6', piernas='L3',
    ),
    'C': dict(
        clave='C', nombre='del Manto', color='Plateada',
        piel=_r('9a8484', 'bea6a4', 'dcc6c2', 'eedcd8', 'fbefec'),
        pelo=_r('6a6c74', '9294a0', 'b8bac6', 'd8dae4', 'f2f4fa'),
        pelaje=_r('6a6c74', '9294a0', 'b8bac6', 'd8dae4', 'f2f4fa'),
        punta=_r('6a1a36', '9a2a52', 'd04a7a', 'f07aa2', 'ffc0d4'),
        tela=_r('3a3c44', '5a5c66', '7c7e8a', 'a2a4b0', 'cacdd6'),
        adorno=_r('5a1030', '8a1a48', 'c02a66', 'e84a88', 'ff8ab4'),
        oro=_r('5a5a64', '8a8a94', 'b8b8c2', 'dcdce4', 'ffffff'), metal=_r('2a2c34', '464852', '6c6e7a', '989aa6', 'd4d6e0'),
        cuero=_r('1a1820', '2a2830', '3a3842', '4e4c58', '68666f'),
        garra=_r('0c0a0e', '18141a', '262028', '383040', '4e4458'),
        medias=_r('1e1c24', '2c2a34', '3c3a46', '504e5a', '6a6874'), escama=_r('120a18', '20122a', '331c42', '4c285e', '6c3a84'),
        neon=('fff0f6', 'ff6e9e', '6a0a2e'), ojos=('ff5aa0', '8a1448', 'ffb8d8'), labios='a8305a', marca='e84a88',
        brazos='B5', piernas='L5',
    ),
}
for _v in VARIANTES.values():
    _v.setdefault('ribete', _v['adorno'])
    _v.setdefault('guante', _v['adorno'])


def pintores(V):
    """Los pintores del cuerpo (jefa_modelo) y los de Vulpina: la punta de las colas, el dentro de la
    oreja, el adorno con su hilo de oro, el obi, la soga, los papeles, el bajo rasgado, la mascara y el
    fuego."""
    P = jm.pintores(V, 'vul3%s' % V['clave'])
    reg = P['_reg']
    nuc, neo, hon = V['neon']
    reg('punta', lambda tw, th, c, s: (jm.hebras(tw, th, s, V['punta'], 2, 4), None))

    def mullido(rampa):
        def f(tw, th, cara_, s):
            """El pelaje de la cola: hebras a lo largo, sin canto en los extremos del tramo, y las tapas
            lisas."""
            if cara_ in ('frente', 'atras'):
                return _imagen(np.full((th, tw), 2), rampa), None
            largo_x = tw >= th
            n_l, n_t = (tw, th) if largo_x else (th, tw)
            rng = random.Random(s)
            idx = np.full((n_t, n_l), 2)
            for t in range(n_t):
                if (t + s) % 3 == 0:
                    idx[t, :] = 3
            for _ in range(max(1, n_l * n_t // 16)):
                t, a = rng.randrange(n_t), rng.randrange(n_l)
                idx[t, a:a + rng.randint(2, 5)] = 4 if rng.random() < 0.5 else 1
            idx[0, :] = np.maximum(idx[0, :] - 1, 0)
            idx[-1, :] = np.maximum(idx[-1, :] - 1, 0)
            if not largo_x:
                idx = idx.T
            return _imagen(idx, rampa), None
        return f
    reg('cola', mullido(V['pelaje']))
    reg('cola_punta', mullido(V['punta']))

    def oreja(tw, th, cara_, s):
        """Por dentro de la oreja: oscuro con un mechon claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 1)
        idx[(xs % 3) == 1] = 2
        return _imagen(idx, V['punta']), None
    reg('oreja', oreja)

    def adorno(tw, th, cara_, s):
        """El adorno (el cuello del kimono, el lazo): liso con un hilo de oro."""
        tex = _imagen(_bisel(np.full((th, tw), 2)), V['adorno'])
        if tw >= th and th >= 4:
            tex[1, :] = (*V['oro'][3], 255)
        elif tw >= 4:
            tex[:, 1] = (*V['oro'][3], 255)
        return tex, None
    reg('adorno', adorno)
    reg('adorno_liso', jm.liso(V['adorno'], 2, 1, 1))

    def obi(tw, th, cara_, s):
        """El obi: la faja ancha con dos hilos de oro y un rombo en medio."""
        ys, xs = np.mgrid[0:th, 0:tw]
        tex = _imagen(np.full((th, tw), 2), V['adorno'])
        if cara_ in ('arriba', 'abajo'):
            return tex, None
        for y in (max(1, th // 5), th - 1 - max(1, th // 5)):
            tex[y, :] = (*V['oro'][3], 255)
        cx, cy = tw // 2, th // 2
        rombo = (np.abs(xs - cx) + np.abs(ys - cy)) <= max(1, th // 4)
        tex[rombo] = (*V['oro'][4], 255)
        return tex, None
    reg('obi', obi)

    def cuerda(tw, th, cara_, s):
        """La soga sagrada: trenzada en diagonal, clara, con la sombra de cada vuelta."""
        ys, xs = np.mgrid[0:th, 0:tw]
        largo_x = tw >= th
        a, b = (xs, ys) if largo_x else (ys, xs)
        idx = np.where(((a + b) % 4) < 2, 3, 2)
        idx = np.where(((a + b) % 4) == 3, 1, idx)
        return _imagen(idx, _r('5a4a30', '8a7650', 'c0aa7a', 'e2d2a6', 'fbf2d6')), None
    reg('cuerda', cuerda)
    reg('papel', jm.liso(_r('a8a498', 'c8c4b8', 'e8e4d8', 'f6f4ec', 'ffffff'), 3, 1, 1))

    def jirones(tw, th, cara_, s):
        """El bajo rasgado de la falda: la tela, una cenefa del color del adorno que sube en picos (como
        llamas) y el borde de abajo roto en tiras de distinto largo (recortado)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = _imagen(np.full((th, tw), 2), V['tela'])
        t[ys == 0] = (*V['tela'][3], 255)
        pico = th // 2 - np.abs((xs % 6) - 3) // 2
        t[ys >= pico] = (*V['adorno'][2], 255)
        t[(ys == pico)] = (*V['adorno'][3], 255)
        rng = random.Random(s)
        corte = np.array([th - rng.randint(0, max(1, th // 3)) for _ in range(tw // 2 + 2)])
        t[ys >= corte[xs // 2]] = 0
        return t, None
    reg('jirones', jirones)

    def mascara(tw, th, cara_, s):
        """La mascara de zorro: laca blanca con las marcas rojas (dos rayas en cada mejilla y la frente)."""
        t = _imagen(_bisel(np.full((th, tw), 3)), _r('8a8478', 'b8b2a6', 'dcd6ca', 'f2eee4', 'ffffff'))
        if cara_ == 'frente' and tw >= 8 and th >= 8:
            rojo = (*nm._hex(V['labios']), 255)
            for y in (th // 2, th // 2 + 2):
                t[y, 1:3] = rojo
                t[y, tw - 3:tw - 1] = rojo
            t[1:3, tw // 2 - 1:tw // 2 + 1] = rojo
            t[th // 2 - 2:th // 2, 3:5] = (20, 12, 16, 255)                              # los ojos
            t[th // 2 - 2:th // 2, tw - 5:tw - 3] = (20, 12, 16, 255)
        return t, None
    reg('mascara', mascara)

    def fuego(tw, th, cara_, s):
        """El fuego fatuo: blanco en el centro y de su color hacia fuera."""
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('fuego', fuego, pleno=True)
    return P


# ----------------------------------------------------------------------
#  La cabeza: las orejas, la melena, la mascara y las horquillas
# ----------------------------------------------------------------------
def orejas(out, Mh, P):
    """Las orejas de zorra, grandes, en escalones que se afinan, con la punta del color de la cola y el
    dentro oscuro; se abren un poco hacia fuera."""
    for s in (1, -1):
        M = Mh @ vr.T(s * 2.55, 8.2, -0.7) @ vr.Rz(-s * 14 * D) @ vr.Rx(-8 * D)
        caja(out, M, -1.75, 1.75, 0.0, 2.1, -0.8, 0.8, P['pelaje'], semilla=30)
        caja(out, M, -1.25, 1.25, 2.0, 3.9, -0.65, 0.65, P['pelaje'], semilla=31)
        caja(out, M, -0.75, 0.75, 3.8, 5.3, -0.5, 0.5, P['punta'], semilla=32)
        caja(out, M, -0.32, 0.32, 5.2, 6.2, -0.32, 0.32, P['punta'], semilla=33)
        caja(out, M, -1.15, 1.15, 0.3, 3.4, 0.8, 0.98, P['oreja'], semilla=34)                    # el dentro
        caja(out, M, -0.6, 0.6, 3.3, 4.7, 0.6, 0.78, P['oreja'], semilla=35)


def melena(out, Mh, P, abierta=1.0):
    """La melena larga hasta la cintura: el panel de la espalda con su volumen detras, y abajo cinco
    mechones con la punta en escalon que se abren un poco."""
    pelo = P['pelo']
    caja(out, Mh, -4.55, 4.55, -12.5, 6.8, -4.95, -3.65, pelo, semilla=40)
    caja(out, Mh, -3.9, 3.9, -10.5, 5.6, -5.6, -4.85, pelo, semilla=41)
    for j in range(5):
        f = (j - 2) / 2
        M = Mh @ vr.T(f * 3.4, -12.3, -4.3) @ vr.Rz(f * 9 * abierta * D)
        largo = 3.6 + 1.6 * (1 - abs(f)) + 0.8 * (j % 2)
        caja(out, M, -0.95, 0.95, -largo, 0.4, -0.65, 0.65, pelo, semilla=42 + j % 3)
        caja(out, M, -0.5, 0.5, -largo - 1.2, -largo + 0.1, -0.45, 0.45, pelo, semilla=45)
    for s in (1, -1):                                                                            # por detras de los hombros
        M = Mh @ vr.T(s * 4.3, 5.0, -2.2) @ vr.Rz(s * 6 * abierta * D)
        caja(out, M, -0.9, 0.9, -15.0, 0.6, -1.2, 1.2, pelo, semilla=46)
        caja(out, M, -0.5, 0.5, -16.4, -14.8, -0.7, 0.7, pelo, semilla=47)


def joyas_de_cabeza(out, Mh, P):
    """La mascara de zorro de laca, puesta a un lado de la cabeza (el que mira a la camara), y al otro las
    tres horquillas de oro con sus colgantes."""
    bm.PPB = 4
    try:
        M = Mh @ vr.T(-4.7, 4.2, 0.9) @ vr.Ry(-78 * D) @ vr.Rz(8 * D)
        caja(out, M, -1.6, 1.6, -1.7, 1.7, -0.25, 0.55, P['mascara'], semilla=50)                  # la cara
        caja(out, M, -0.7, 0.7, -1.4, -0.1, 0.5, 1.75, P['mascara'], semilla=51)                   # el hocico
        caja(out, M, -0.35, 0.35, -1.25, -0.75, 1.7, 2.0, P['adorno_liso'], semilla=52)            # la nariz
        for s in (1, -1):                                                                        # las orejas
            Mo = M @ vr.T(s * 1.0, 1.6, 0.1) @ vr.Rz(-s * 12 * D)
            caja(out, Mo, -0.45, 0.45, 0.0, 1.2, -0.2, 0.2, P['mascara'], semilla=53)
            caja(out, Mo, -0.22, 0.22, 1.1, 1.6, -0.15, 0.15, P['adorno_liso'], semilla=54)
    finally:
        bm.PPB = jm.PPB
    for j in range(3):                                                                           # las horquillas
        p = pt(Mh, (3.4 - 0.4 * j, 6.6 - 0.6 * j, -1.8 - 0.9 * j))
        q = pt(Mh, (6.2 - 0.3 * j, 9.6 - 0.3 * j, -3.2 - 1.2 * j))
        jm.tubo(out, [p, q], [0.22, 0.18], [P['oro']], semilla=55)
        caja(out, vr.T(*q), -0.38, 0.38, -0.38, 0.38, -0.38, 0.38, P['oro'], semilla=56)
        for k in range(2):
            e = q + np.array((0.0, -0.9 - 0.75 * k, 0.0))
            caja(out, vr.T(*e), -0.24, 0.24, -0.4, 0.3, -0.24, 0.24, P['adorno_liso'] if k else P['oro'], semilla=57)


# ----------------------------------------------------------------------
#  El kimono: el corpino, el cuello en V, el obi, la soga y la falda
# ----------------------------------------------------------------------
def kimono(out, P):
    """El corpino de kimono (los hombros al aire) con el pecho P1 y su ribete rojo; el cuello rojo
    cruzado en V sobre el pecho; el obi ancho con su cordon de oro, la gema y el lazo grande detras; la
    soga sagrada en la cadera con cuatro papeles en zigzag; y la falda corta en dos escalones con el bajo
    rasgado."""
    tl = P['tela_lisa']
    jm.torso(out, P, {'cadera': tl, 'cintura': tl, 'pecho': tl, 'busto': P['tela'], 'ribete': P['adorno_liso']})
    for s in (1, -1):                                                                            # el cuello en V
        a, b = np.array((s * 3.55, 38.2)), np.array((s * 0.15, 35.1))
        m = (a + b) / 2
        L = float(np.linalg.norm(a - b))
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        M = vr.T(m[0], m[1], 0.0) @ vr.Rz(ang)
        caja(out, M, -L / 2 - 0.3, L / 2 + 0.3, -0.55, 0.55, 2.0, 3.42, P['adorno'], semilla=60)
    caja(out, jm.I4, -3.5, 3.5, 29.2, 33.5, -2.3, 2.3, P['obi'], semilla=61)                     # el obi
    caja(out, jm.I4, -3.58, 3.58, 31.1, 31.6, -2.38, 2.38, P['oro'], semilla=62)                 # el cordon
    caja(out, jm.I4, -0.55, 0.55, 30.8, 31.9, 2.3, 2.75, P['gema'], semilla=63)
    caja(out, jm.I4, -1.1, 1.1, 29.9, 32.8, -3.4, -2.2, P['adorno_liso'], semilla=64)            # el nudo del lazo
    for s in (1, -1):                                                                            # las alas del lazo
        M = vr.T(s * 2.6, 31.4, -3.0) @ vr.Rz(s * 16 * D)
        caja(out, M, -2.0, 2.0, -1.5, 1.6, -0.6, 0.6, P['adorno'], semilla=65)
        M = vr.T(s * 1.0, 29.6, -3.0) @ vr.Rz(s * 12 * D)
        caja(out, M, -0.7, 0.7, -5.0, 0.0, -0.45, 0.45, P['adorno'], semilla=66)
    for (x0, x1, z0, z1) in ((-5.0, 5.0, 2.55, 3.25), (-5.0, 5.0, -3.25, -2.55), (4.35, 5.05, -3.25, 3.25), (-5.05, -4.35, -3.25, 3.25)):
        caja(out, jm.I4, x0, x1, 25.4, 26.5, z0, z1, P['cuerda'], semilla=67)                   # la soga
    for j, x in enumerate((-2.6, 2.6)):                                                          # los papeles en zigzag
        M = vr.T(x, 25.5, 3.45) @ vr.Rz((6 if x > 0 else -6) * D)
        for k in range(4):
            dx = 0.42 if k % 2 else -0.42
            caja(out, M, dx - 0.55, dx + 0.55, -1.2 * (k + 1), -1.2 * k + 0.05, -0.08, 0.12, P['papel'], semilla=68)
    caja(out, jm.I4, -4.85, 4.85, 23.0, 26.2, -2.85, 2.85, P['tela'], semilla=70)               # la falda
    caja(out, jm.I4, -5.3, 5.3, 20.2, 23.1, -3.25, 3.25, P['tela'], semilla=71)
    bm.cubo(out, jm.I4, -5.35, 18.4, -3.3, 10.7, 1.9, 6.6, P['jirones'], caras={'arriba': None, 'abajo': None}, semilla=72)


# ----------------------------------------------------------------------
#  Las colas y el fuego
# ----------------------------------------------------------------------
PERFIL_COLA = ((0.0, 1.4), (0.15, 2.6), (0.35, 3.5), (0.55, 3.7), (0.72, 3.3), (0.86, 2.4), (1.0, 1.0))
BASE_COLAS = np.array((0.0, 27.5, -3.3))


def cola(out, P, ctrl, grosor=1.0, semilla=0, fuego=True):
    """Una cola de zorra, mullida: un tubo de bloques que crece hasta la mitad y mengua hacia la punta (la
    ultima parte, del color de la punta), con su fuego al final."""
    pts, rs, ts = jm.a_lo_largo(ctrl, 11, PERFIL_COLA)
    rs = [r * grosor for r in rs]
    pinta = [P['cola_punta'] if (t0 + t1) / 2 > 0.76 else P['cola'] for t0, t1 in zip(ts, ts[1:])]
    jm.tubo(out, pts, rs, pinta, semilla=semilla)
    if fuego:
        d = pts[-1] - pts[-2]
        jm.llama(out, P['fuego'], pts[-1] + d / np.linalg.norm(d) * 1.4, 1.5 * grosor, semilla=semilla + 9)


def colas_abanico(out, P):
    """A: las nueve colas abiertas detras de ella en abanico, de abajo a un lado hasta abajo al otro."""
    B0 = BASE_COLAS
    for j in range(9):
        th = (-18.0 + j * 216.0 / 8) * D
        c, s_ = math.cos(th), math.sin(th)
        L = 30.0 - 4.0 * abs(j - 4) / 4
        ctrl = [B0, B0 + np.array((c * 5.0, s_ * 5.0 + 1.2, -2.7)), B0 + np.array((c * L * 0.55, s_ * L * 0.55 + 2.0, -6.2)),
                B0 + np.array((c * L * 0.85, s_ * L * 0.85 + 3.1, -7.4)), B0 + np.array((c * L - s_ * 2.3, s_ * L + c * 2.3 + 4.3, -7.0))]
        cola(out, P, ctrl, grosor=1.0 - 0.06 * abs(j - 4) / 4, semilla=70 + j)


def colas_llama(out, P):
    """B: las colas alzadas detras como una llama: suben juntas y se rizan hacia fuera en la punta."""
    B0 = BASE_COLAS
    for j in range(9):
        f = (j - 4) / 4
        L = 34.0 - 8.8 * abs(f)
        ctrl = [B0, B0 + np.array((f * 2.3, 5.1, -3.1)), B0 + np.array((f * 6.2, L * 0.5, -5.5 - 0.8 * abs(f))),
                B0 + np.array((f * 9.8, L * 0.82, -6.2)), B0 + np.array((f * 14.0 + (3.1 if f >= 0 else -3.1), L, -5.1))]
        cola(out, P, ctrl, grosor=1.0 - 0.1 * abs(f), semilla=70 + j)


def colas_manto(out, P):
    """C: dos colas suben por la espalda y le rodean el cuello sobre los hombros como una estola de piel;
    las otras siete se arrastran por el suelo detras, abiertas como la cola de un manto."""
    B0 = BASE_COLAS
    for j, s in enumerate((1, -1)):
        ctrl = [B0, np.array((s * 2.0, 34.0, -5.8)), np.array((s * 3.6, 42.0, -4.0)), np.array((s * 4.1, 43.8, -0.6)),
                np.array((s * 2.8, 42.2, 3.0)), np.array((s * 1.4, 39.6, 3.8))]
        cola(out, P, ctrl, grosor=0.5, semilla=70 + j, fuego=False)
    for j in range(7):
        f = (j - 3) / 3
        ctrl = [B0, B0 + np.array((f * 3.9, -4.7, -2.7)), np.array((f * 9.0, 8.4, -9.8)), np.array((f * 14.5, 4.2, -17.6)),
                np.array((f * 18.0, 4.0, -25.4 + abs(f) * 4.5))]
        cola(out, P, ctrl, grosor=0.9 - 0.08 * abs(f), semilla=80 + j)


# ======================================================================
#  VULPINA
# ======================================================================
POSES = {
    'A': dict(brazos={1: dict(abd=62, flex=12, codo=82, giro=-90, mun=-8, cierra=0.5),
                      -1: dict(abd=62, flex=12, codo=82, giro=-90, mun=-8, cierra=0.5)},
              piernas={1: dict(abd=4, flex=-3, rodilla=4), -1: dict(abd=3, flex=14, rodilla=20)},
              cabeza=(10, -5)),
    'B': dict(brazos={1: dict(abd=138, flex=14, codo=38, giro=-70, mun=-10, cierra=0.6),
                      -1: dict(abd=18, flex=24, codo=52, giro=8, mun=-10, cierra=0.2)},
              piernas={1: dict(abd=9, flex=-6, rodilla=6), -1: dict(abd=9, flex=16, rodilla=22)},
              cabeza=(8, 5)),
    'C': dict(brazos={1: dict(abd=35, flex=-5, codo=88, giro=90, mun=0, cierra=1.0),
                      -1: dict(abd=20, flex=42, codo=38, giro=0, mun=-20, cierra=0.3)},
              piernas={1: dict(abd=3, flex=0, rodilla=4), -1: dict(abd=2, flex=9, rodilla=13)},
              cabeza=(11, 3)),
}


def vulpina(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    pose = POSES[tipo]
    ppb = bm.PPB
    bm.PPB = jm.PPB
    out = []
    try:
        kimono(out, P)
        manos = {}
        for s in (1, -1):
            c = {'guante': P['adorno_liso'], 'borde': P['oro']} if V['brazos'] == 'B3' else \
                {'metal': P['metal'], 'borde': P['adorno_liso'], 'manga': P['tela']} if V['brazos'] == 'B5' else {}
            manos[s] = jm.brazo(out, P, s, V['brazos'], pose['brazos'][s], c)
            cp = {'borde': P['adorno_liso'], 'oro': P['oro']}
            jm.pierna(out, P, s, V['piernas'], pose['piernas'][s], cp)
        {'A': colas_abanico, 'B': colas_llama, 'C': colas_manto}[tipo](out, P)
        fuegos = []
        if tipo == 'A':                                              # un fuego sobre cada mano
            for s in (1, -1):
                fuegos.append((pt(manos[s], (0, 0, 0)) + np.array((s * 0.6, 4.2, 0.6)), 2.0))
        elif tipo == 'B':                                            # el fuego grande sobre la garra en alto
            fuegos.append((pt(manos[1], (0, 0, 0)) + np.array((0.4, 4.6, 0.6)), 3.0))
        else:                                                        # el fuego que ofrece y el anillo de fuegos
            fuegos.append((pt(manos[-1], (0, 0, 0)) + np.array((0.0, 3.6, 0.8)), 2.0))
            for j in range(9):
                a = j * TAU / 9 + 0.3
                fuegos.append((np.array((math.cos(a) * 17.0, 28.5 + 2.3 * math.sin(3 * a), math.sin(a) * 17.0)), 1.6))
        for p, r in fuegos:
            jm.llama(out, P['fuego'], p, r, semilla=130)
        tx, tz = pose['cabeza']
        Mh = vr.T(0.0, jm.CUELLO_Y, 0.2) @ vr.Rx(tx * D) @ vr.Rz(tz * D)
        jm.cabeza(out, Mh, P, V)
        orejas(out, Mh, P)
        melena(out, Mh, P, abierta=1.4 if tipo == 'B' else 1.0)
        joyas_de_cabeza(out, Mh, P)
    finally:
        bm.PPB = ppb
    out = jm.a_escena(out)
    E = np.diag([jm.ESCALA] * 3 + [1.0])
    Mh_e = E @ Mh
    luces = [jm.ESCALA * p for p, _ in fuegos]
    if tipo == 'C':
        luces = [luces[0], luces[5]]
    return out, {'cabeza': Mh_e, 'cara': pt(Mh_e, (0.0, 4.0, 4.2)), 'boca': pt(Mh_e, (0.0, 1.3, 4.2)),
                 'fuegos': [jm.ESCALA * p for p, _ in fuegos], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

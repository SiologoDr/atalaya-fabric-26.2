"""
Equidna y sus formas (14-10-2026). Juan, al rechazar a Tifon: «sigamos con otro boss y sus tipos». Gusto Escila (la jefa
con los perros de fauces encendidas en la cintura), asi que la siguiente sigue esa formula con otro monstruo del mito:
Equidna, la Madre de los Monstruos (madre de Cerbero, de la Hidra, de la Quimera y de Escila).

Una jefa con el cuerpo de jefa_modelo (el de la Gorgona y Escila: mujer adulta de cajas y la cara C3 con mirada de
jefa), con las garras de escamas, el corpino de escamas, la melena larga y una corona de cuernos de hueso. De la
cintura para abajo es una serpiente enorme que se enrosca en el suelo; la punta de la cola se alza por detras de ella y
acaba en una cabeza de dragon con las fauces encendidas (el paladar en escalones, los dientes dibujados en hojas, los
colmillos y el nucleo al fondo).

Las tres formas cambian lo que la rodea, y con ello la silueta:

    A  la Madre       de sus anillos asoman sus hijos: un perro, un dragon y una morena, con las fauces encendidas; ambar
    B  la Reina       la cola sube en espiral detras de ella, como un trono, y la cabeza de la cola la mira desde arriba;
                      dos hijos grandes a los lados; carmesi
    C  la del Nido    se enrosca alrededor de cinco huevos que arden; de uno roto asoma una cria con la boca abierta;
                      esmeralda
"""
import math
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
import sierpe_modelo as sm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt
import escila_modelo as es
import tifon_modelo as ti
from escila_modelo import _u

TAU = math.tau
D = vr.D2R
_r = bm._r
GRANDE = 1.25
CADERA_Y = 22.0
NACAR = es.NACAR

VARIANTES = {
    'A': dict(
        clave='A', nombre='la Madre', corto='madre',
        piel=_r('7e6e5e', 'a49482', 'c6b6a2', 'dfd0bc', 'f4eadc'),
        pelo=_r('0c0804', '181008', '26180c', '362212', '4c3018'),
        tela=_r('1c1408', '2c200e', '402e14', '58401c', '745628'),
        escama=_r('1c1408', '2c200e', '402e14', '58401c', '745628'),
        mar=_r('0e0a06', '18120a', '241a10', '322416', '42301e'),
        vientre=_r('3a2e1c', '54442a', '70603c', '8e7c52', 'ae9c6c'),
        aleta=_r('0e0a06', '18120a', '1e160c', '281e12', '342818'),
        hueso=_r('4a4234', '6e6450', '948870', 'b8ac92', 'd8ceb6'),
        cuerno=_r('1a140c', '2e2416', '463822', '5e4e32', '7a6646'),
        coral=NACAR, oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('0a0806', '14100c', '1e1812', '2a2218', '382e22'),
        pelaje=_r('0e0a06', '18120a', '241a10', '322416', '42301e'), medias=NACAR,
        neon=('fff2d6', 'ffb02a', '6a3a04'), ojos=('ffb02a', '8a5208', 'ffe0a0'), labios='6a4a3a', marca='7a4a14',
    ),
    'B': dict(
        clave='B', nombre='la Reina', corto='reina',
        piel=_r('7c6a6a', 'a28e8e', 'c6b2b0', 'e0cecc', 'f6eceb'),
        pelo=_r('0e0406', '1a080a', '2a0e12', '3e161a', '562026'),
        tela=_r('12060a', '200a10', '301018', '441822', '5c222e'),
        escama=_r('12060a', '200a10', '301018', '441822', '5c222e'),
        mar=_r('0c0606', '160c0c', '201212', '2c1a1a', '3a2424'),
        vientre=_r('3a2420', '54342e', '704840', '8e6056', 'ae7c70'),
        aleta=_r('0c0606', '160c0c', '1c0e0e', '261414', '321c1c'),
        hueso=_r('4e4038', '74625a', '9a887c', 'bcac9e', 'dccec0'),
        cuerno=_r('180a0a', '2a1212', '421c1c', '5a2828', '763636'),
        coral=NACAR, oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('0a0606', '140c0c', '1e1414', '2a1e1e', '3a2a2a'),
        pelaje=_r('0c0606', '160c0c', '201212', '2c1a1a', '3a2424'), medias=NACAR,
        neon=('ffe2e6', 'ff2a46', '6a0410'), ojos=('ff2a46', '8a0a14', 'ffa0aa'), labios='6a2a30', marca='8a1a24',
    ),
    'C': dict(
        clave='C', nombre='la del Nido', corto='nido',
        piel=_r('6e7a70', '94a296', 'b8c6ba', 'd2dcd2', 'eef4ee'),
        pelo=_r('040a06', '08140c', '0e2014', '162e1e', '22402a'),
        tela=_r('061a10', '0c2a1a', '143e26', '1e5434', '2c6e46'),
        escama=_r('061a10', '0c2a1a', '143e26', '1e5434', '2c6e46'),
        mar=_r('060c08', '0c1610', '122016', '1a2c1e', '243a28'),
        vientre=_r('24342a', '364a3c', '4c6452', '668070', '829e8c'),
        aleta=_r('060c08', '0c1610', '10180e', '182416', '20301e'),
        hueso=_r('424a40', '626e60', '869282', 'aab4a6', 'ccd4c8'),
        cuerno=_r('0c140e', '162418', '223826', '304c34', '446448'),
        coral=NACAR, oro=NACAR, metal=NACAR, cuero=NACAR, garra=_r('060a08', '0e1410', '161e18', '202a22', '2c382e'),
        pelaje=_r('060c08', '0c1610', '122016', '1a2c1e', '243a28'), medias=NACAR,
        neon=('eefff2', '3aff8a', '045a24'), ojos=('3aff8a', '0a6a2a', 'b0ffcc'), labios='4a5a4c', marca='1e5434',
    ),
}
for _v in VARIANTES.values():
    _v.setdefault('ribete', NACAR)
    _v.setdefault('guante', _v['tela'])


def pintores(V):
    """Los de Escila (cuerpo de jefa y monstruo) mas los que piden las cabezas de dragon de Tifon, y el huevo."""
    P = es.pintores(V)
    reg = P['_reg']
    nuc, neo, hon = V['neon']
    reg('hueso', jm.liso(V['hueso'], 3, 1, 1))

    def cuerno(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        v = ys if th >= tw else xs
        idx = np.where(v % 4 == 0, 1, np.where(v % 4 == 1, 3, 2))
        return _imagen(idx, V['cuerno']), None
    reg('cuerno', cuerno)

    def huevo(tw, th, cara, s):
        """El huevo: la cascara clara y lisa, con la luz de dentro que se ve en manchas grandes y en las grietas."""
        idx = sm._manchas(tw, th, s, celda=9.0, umbral=0.6, alto=0.82)
        t = _imagen(np.clip(idx, 1, 4), V['vientre'])
        c_m = np.array(nm._hex(neo))
        luz = idx >= 3
        t[..., :3] = np.where(luz[..., None], (t[..., :3] * 0.4 + c_m * 0.6).astype(np.uint8), t[..., :3])
        return t, _emis(t, luz, 180)
    reg('huevo', huevo)
    P['ojo'] = P['ojo_perro']
    P['vientre'] = P['vientre_mar']
    P['escama_jefa'] = P['escama']
    return P


def _dragon(out, P, Mc):
    """Una cabeza de dragon de Tifon con la piel de serpiente de Equidna."""
    Q = dict(P)
    Q['escama'] = P['mar']
    return ti.cabeza_dragon(out, Mc, Q, abre=38.0, cuernos=0.5)


def cabeza_en_cuello(out, P, ctrl, r0, r1, mira, escala, tipo='dragon', semilla=0):
    """Un cuello de serpiente por la curva y, al final, una cabeza (de dragon, de perro o de morena) a la escala dada,
    que mira hacia 'mira'. Devuelve el centro de la boca."""
    ps, rs, _ = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], 10, ((0.0, r0), (0.7, r1), (1.0, r1 * 1.1)))
    jm.tubo(out, ps, rs, [P['mar']] * (len(ps) - 1), semilla=semilla)
    mira = _u(mira)
    Mc = em.marco(ps[-1], mira, up=(0.0, 1.0, 0.0)) @ vr.T(0, -2.2 * escala, -1.8 * escala) @ np.diag([escala] * 3 + [1.0])
    ppb = bm.PPB
    bm.PPB = jm.PPB / escala
    if tipo == 'perro':
        boca = es.perro(out, Mc, P, abre=34.0, semilla=semilla + 20)
    elif tipo == 'morena':
        boca = es.morena(out, Mc, P, semilla=semilla + 20)
    else:
        boca = _dragon(out, P, Mc)
    bm.PPB = ppb
    return boca


def cola(out, P, ctrl, perfil, semilla=0):
    """El cuerpo de serpiente por la curva, con los escudos del vientre por debajo."""
    ps, rs, _ = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], max(12, len(ctrl) * 4), perfil)
    jm.tubo(out, ps, rs, [P['mar']] * (len(ps) - 1), semilla=semilla)
    for k in range(1, len(ps) - 1, 2):
        d = ps[k + 1] - ps[k - 1]
        lado = _u(np.cross(d, (0.0, 1.0, 0.0)) + np.array((1e-3, 0.0, 0.0)))
        abajo = _u(np.cross(d, lado))
        if abajo[1] > 0:
            abajo = -abajo
        M = em.marco(ps[k] + abajo * rs[k] * 0.86, d, up=-abajo)
        caja(out, M, -rs[k] * 0.62, rs[k] * 0.62, -0.25, 0.25, -0.9, 0.9, P['vientre'], semilla=semilla + 1)
    return ps, rs


def jefa(out, P, V, pose, semilla=0):
    """La mujer: el torso con el corpino de escamas, los brazos de garra, la cabeza C3, la melena larga y la corona de
    cuernos de hueso. Devuelve la cara."""
    sup = []
    esc = P['escama_jefa']
    bm.PPB = jm.PPB * GRANDE
    jm.torso(sup, P, {'cadera': esc, 'cintura': esc, 'pecho': esc, 'busto': esc, 'ribete': P['nacar']})
    for s in (1, -1):
        jm.brazo(sup, P, s, 'B6', pose[s], {'escama': esc, 'pelaje': P['mar'], 'una': P['garra']})
    Mh = vr.T(0.0, jm.CUELLO_Y, 0.2) @ vr.Rx(8 * D)
    jm.cabeza(sup, Mh, P, V)
    caja(sup, Mh, -4.55, 4.55, -4.0, 7.0, -4.95, -3.6, P['pelo'], semilla=59)
    for k, x in enumerate((-3.4, -1.7, 0.0, 1.7, 3.4)):                                                # la melena larga
        b = pt(Mh, (x, 0.0, -4.4))
        ctrl = [b, b + np.array((x * 0.1, -6.0, -1.4)), b + np.array((x * 0.25, -13.0, -2.0)), b + np.array((x * 0.3, -18.0 + abs(x), -1.2))]
        ps, rs, _ = jm.a_lo_largo(ctrl, 6, ((0.0, 1.0), (1.0, 0.5)))
        jm.tubo(sup, ps, rs, [P['pelo']] * (len(ps) - 1), semilla=60 + k)
    for k, (x, a, L) in enumerate(((-2.8, 30, 4.0), (-1.4, 14, 5.0), (0.0, 0, 6.0), (1.4, -14, 5.0), (2.8, -30, 4.0))):  # la corona de cuernos
        b = pt(Mh, (x, 7.6, -0.6))
        d = Mh[:3, :3] @ np.array((math.sin(-a * D), 1.0, -0.35))
        ctrl = [b, b + _u(d) * L * 0.55, b + _u(d) * L + np.array((0.0, 0.0, -L * 0.25))]
        jm.tubo(sup, ctrl, [0.55, 0.38, 0.12], [P['cuerno']] * 2, semilla=70)
    caja(sup, Mh, -0.6, 0.6, 7.4, 8.6, 3.9, 4.6, P['luz'], semilla=72)                               # la gema de la corona
    bm.PPB = jm.PPB
    Ms = vr.T(0.0, CADERA_Y, 0.0) @ np.diag([GRANDE] * 3 + [1.0]) @ vr.T(0.0, -24.0, 0.0)
    out += qm.transformar(sup, Ms)
    return pt(Ms @ Mh, (0.0, 4.0, 4.2))


POSES = {
    'A': {1: dict(abd=58, flex=40, codo=48, giro=-40, mun=-10, cierra=0.25), -1: dict(abd=40, flex=46, codo=64, giro=-30, mun=-10, cierra=0.25)},
    'B': {1: dict(abd=110, flex=20, codo=30, giro=-60, mun=-10, cierra=0.2), -1: dict(abd=34, flex=26, codo=40, giro=-20, mun=0, cierra=0.5)},
    'C': {1: dict(abd=36, flex=58, codo=50, giro=-20, mun=-20, cierra=0.3), -1: dict(abd=36, flex=58, codo=50, giro=-20, mun=-20, cierra=0.3)},
}
PERFIL_COLA = ((0.0, 5.6), (0.25, 6.2), (0.6, 4.8), (0.85, 3.4), (1.0, 2.8))


# ======================================================================
#  EQUIDNA
# ======================================================================
def equidna(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = jm.PPB
    out = []
    luces = []
    try:
        cara = jefa(out, P, V, POSES[tipo], semilla=80)
        Y = CADERA_Y
        if tipo == 'A':
            # la cola: baja por delante, se enrosca una vez y media en el suelo y se alza detras, a su izquierda
            ctrl = [(0.0, Y + 1.0, 0.0), (0.0, Y - 8.0, 3.0), (3.0, 5.0, 9.0), (13.0, 4.0, 6.0), (17.0, 4.0, -5.0), (8.0, 4.0, -14.0),
                    (-8.0, 4.0, -13.0), (-16.0, 4.5, -3.0), (-15.0, 6.0, 8.0), (-19.0, 14.0, 4.0), (-17.0, 26.0, -2.0),
                    (-12.0, 36.0, -1.0)]
            ps, rs = cola(out, P, ctrl, PERFIL_COLA, semilla=100)
            luces.append(cabeza_en_cuello(out, P, [ps[-1], ps[-1] + np.array((2.0, 4.0, 2.0)), ps[-1] + np.array((4.0, 6.0, 6.0))], 2.8, 2.6,
                                          np.array((0.25, -0.2, 1.0)), 1.15, 'dragon', semilla=120))
            for j, (b, d, tipo_h, esc_) in enumerate((((12.0, 6.0, 8.0), (0.8, 1.8, 1.0), 'perro', 1.35),
                                                       ((-4.0, 6.0, 11.0), (-0.7, 1.9, 0.8), 'dragon', 1.05),
                                                       ((15.0, 6.0, -6.0), (1.0, 2.0, 0.6), 'morena', 1.3))):
                b = np.array(b)
                d = _u(np.array(d))
                ctrl_h = [b, b + d * 6.0, b + d * 11.0 + np.array((0.0, 2.0, 3.0))]
                luces.append(cabeza_en_cuello(out, P, ctrl_h, 2.4, 2.0, np.array((d[0] * 0.6, -0.1, 1.0)), esc_, tipo_h, semilla=130 + j * 10))
            luces[0], luces[1] = luces[1], luces[0]                                    # la foto de la cabeza mira al perro
        elif tipo == 'B':
            # la cola: se enrosca en el suelo y sube en espiral detras de ella, como un trono
            ctrl = [(0.0, Y + 1.0, 0.0), (0.0, Y - 8.0, 3.0), (4.0, 5.0, 7.0), (12.0, 4.0, 2.0), (10.0, 4.5, -9.0), (-2.0, 5.0, -13.0)]
            for k in range(13):                                                        # la espiral, a su izquierda
                a = k * 0.62 * math.pi
                ctrl.append((-14.0 + math.sin(a) * 6.5, 8.0 + k * 4.6, -6.0 + math.cos(a) * 6.5))
            ctrl += [(-10.0, 70.0, -2.0), (-4.0, 74.0, 2.0)]
            ps, rs = cola(out, P, ctrl, ((0.0, 5.6), (0.2, 6.0), (0.5, 4.4), (0.85, 3.2), (1.0, 2.8)), semilla=100)
            luces.append(cabeza_en_cuello(out, P, [ps[-1], ps[-1] + np.array((2.0, 2.0, 3.0)), ps[-1] + np.array((4.0, 1.0, 7.0))], 2.8, 2.6,
                                          np.array((0.35, -0.6, 1.0)), 1.45, 'dragon', semilla=120))
            for j, s in enumerate((1, -1)):
                b = np.array((s * 10.0, 6.0, 4.0))
                d = _u(np.array((s * 0.6, 1.4, 0.5)))
                ctrl_h = [b, b + d * 7.0, b + d * 12.0 + np.array((0.0, 2.0, 3.0))]
                luces.append(cabeza_en_cuello(out, P, ctrl_h, 2.8, 2.3, np.array((s * 0.45, -0.1, 1.0)), 1.25, 'perro' if s > 0 else 'dragon',
                                              semilla=130 + j * 10))
        else:
            # la cola: enroscada alrededor del nido, con la punta alzada detras
            ctrl = [(0.0, Y + 1.0, 0.0), (0.0, Y - 9.0, -3.0), (8.0, 3.0, -8.0), (20.0, 2.6, -2.0), (22.0, 2.4, 12.0), (12.0, 2.4, 25.0),
                    (0.0, 2.4, 29.0), (-12.0, 2.4, 25.0), (-21.0, 3.0, 14.0), (-23.0, 8.0, 6.0), (-21.0, 16.0, 5.0)]
            ps, rs = cola(out, P, ctrl, ((0.0, 5.6), (0.15, 4.0), (0.5, 2.9), (0.85, 2.9), (1.0, 2.8)), semilla=100)
            luces.append(cabeza_en_cuello(out, P, [ps[-1], ps[-1] + np.array((1.5, 3.0, 2.0)), ps[-1] + np.array((3.0, 4.0, 5.5))], 2.8, 2.6,
                                          np.array((0.5, -0.3, 1.0)), 1.2, 'dragon', semilla=120))
            for k, (x, z, r) in enumerate(((-8.0, 15.0, 4.8), (0.0, 18.0, 5.2), (8.5, 15.5, 4.6), (-12.5, 6.0, 4.2), (13.0, 6.5, 4.3))):   # el nido
                c = np.array((x, r * 1.1, z))
                for kx, ky in ((1.0, 1.3), (0.78, 1.45), (1.12, 1.0)):
                    caja(out, vr.T(*c), -r * kx, r * kx, -r * ky, r * ky, -r * kx, r * kx, P['huevo'], semilla=150 + k)
                luces.append(c + np.array((0.0, 0.0, r + 1.0)))
            c = np.array((0.0, 11.5, 18.0))                                                            # la cria que asoma
            luces.insert(1, cabeza_en_cuello(out, P, [c, c + np.array((0.0, 3.0, 1.5)), c + np.array((0.0, 4.5, 3.5))], 1.4, 1.2,
                                             np.array((0.0, 0.1, 1.0)), 0.75, 'dragon', semilla=170))
            for k in range(6):                                                                         # la cascara rota
                a = TAU * k / 6
                M = vr.T(c[0] + math.sin(a) * 4.0, c[1] + 0.6, c[2] + math.cos(a) * 4.0) @ vr.Ry(a) @ vr.Rx(-25 * D)
                caja(out, M, -1.4, 1.4, 0.0, 2.2 + (k % 2), -0.4, 0.4, P['huevo'], semilla=180)
        # la union de la cintura con la serpiente
        caja(out, jm.I4, -5.4, 5.4, Y - 3.0, Y + 2.5, -3.6, 3.6, P['mar'], semilla=190)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([jm.ESCALA] * 3 + [1.0]) @ vr.T(0.0, -min(y0, 0.0), 0.0)
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    return out, {'boca': luces[0], 'luces': luces, 'cara': pt(E, cara)}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

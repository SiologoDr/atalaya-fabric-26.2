"""
Florara y sus formas (14-10-2026). Juan, al descartar a Anubis: «cambiemos de tematica a plantas, naturaleza,
etc.; creamos un boss asi y se mas creativo».

Un monstruo planta, inventado: una flor colosal que camina. Las piernas son haces de raices trenzadas que acaban
en garras de raiz hundidas en el suelo; el cuerpo, un tallo grueso envuelto en hojas de vaina, con hojas por
hombreras; los brazos, lianas trenzadas con una hoja-cuchilla y dedos de espina; y el cuello se dobla hacia
delante, como el de un girasol, para que la flor mire hacia abajo, a quien tiene delante. No tiene boca: la flor es
la cara, y lo que arde con su neon es la flor misma. Todo de cajas, con texturas limpias (las fibras del tallo, el
nervio de las hojas, las semillas).

Las tres formas cambian de flor, y con ella la silueta:

    A  la Girasola   un disco de girasol enorme con las semillas en espirales que arden (la espiral de las
                     semillas, como un remolino) y una corona de petalos secos; oro de girasol
    B  la Vilana     un diente de leon en semilla: una bola de vilanos con las puntas encendidas, y semillas que
                     se sueltan y flotan alrededor; blanco de luna
    C  la Cardona    un cardo: un cuenco de bracteas con espinas y encima un penacho de filamentos encendidos; el
                     cuerpo entero erizado de espinas; magenta
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.6
AUREO = math.pi * (3.0 - math.sqrt(5.0))                 # el angulo de oro: el de las semillas del girasol

VARIANTES = {
    'A': dict(
        clave='A', nombre='la Girasola', corto='girasola',
        tallo=_r('0a120a', '122014', '1a2e1c', '244026', '325634'),
        hoja=_r('081008', '10200f', '183018', '224424', '2e5a30'),
        raiz=_r('140e0a', '221810', '32241a', '443222', '5a442e'),
        petalo=_r('2a1806', '4a2c0a', '704412', '9a621c', 'c8882a'),
        semilla=_r('0e0806', '1a100a', '281a10', '382416', '4c321e'),
        espina=_r('3a3424', '5e5640', '847a5c', 'aa9e7c', 'd0c4a0'),
        neon=('fff8d6', 'ffc21e', '6a3e02'),
    ),
    'B': dict(
        clave='B', nombre='la Vilana', corto='vilana',
        tallo=_r('0a100e', '121c18', '1a2a24', '243a32', '304e44'),
        hoja=_r('081010', '0e1c1a', '162a28', '1e3a36', '2a4e48'),
        raiz=_r('121010', '1e1a18', '2c2622', '3c342e', '50463e'),
        petalo=_r('5a6066', '7e858c', 'a6acb2', 'ccd2d8', 'eef2f6'),
        semilla=_r('1a1612', '2a241e', '3c342c', '50463c', '685c50'),
        espina=_r('4a4e52', '6e7276', '94989c', 'babec2', 'e0e4e8'),
        neon=('ffffff', 'bfeeff', '2a4a6a'),
    ),
    'C': dict(
        clave='C', nombre='la Cardona', corto='cardona',
        tallo=_r('0c100c', '141c16', '1e2a20', '2a3a2c', '384e3a'),
        hoja=_r('0a0e0c', '121a16', '1c2822', '28382e', '364c3e'),
        raiz=_r('140e10', '22181a', '322428', '443238', '5a444c'),
        petalo=_r('2a0a26', '4a1240', '6e1c60', '962a84', 'c040aa'),
        semilla=_r('101410', '1a221a', '263226', '344434', '465a46'),
        espina=_r('3a4030', '5e664a', '848e68', 'aab488', 'd0d8ae'),
        neon=('ffe6fa', 'ff3ad0', '6a0858'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'flo%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def tallo(tw, th, cara, s):
        """El tallo y las lianas: fibras a lo largo, claras y oscuras, con un nudo de trecho en trecho."""
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        idx = np.full((n_a, n_l), 2)
        idx[np.arange(n_a) % 3 == 0, :] = 1
        idx[np.arange(n_a) % 3 == 1, :] = 3
        idx[:, np.arange(n_l) % 14 == 0] = 1
        if not largo_x:
            idx = idx.T
        return _imagen(_bisel(idx, 1, 1), V['tallo']), None
    reg('tallo', tallo)

    def raiz(tw, th, cara, s):
        """Las raices: corteza en vetas largas, oscura, con el canto claro."""
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        ys, xs = np.mgrid[0:n_a, 0:n_l]
        idx = np.where(((ys + xs // 6) % 4) == 0, 1, np.where(((ys + xs // 6) % 4) == 2, 3, 2))
        if not largo_x:
            idx = idx.T
        return _imagen(_bisel(idx, 1, 1), V['raiz']), None
    reg('raiz', raiz)

    def hoja(tw, th, cara, s):
        """La hoja: el nervio claro por el medio a lo largo y los nervios de los lados en uve, sobre el verde
        oscuro; en los cantos, lisa."""
        if min(tw, th) < 4:
            return _imagen(np.full((th, tw), 2), V['hoja']), None
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        ys, xs = np.mgrid[0:n_a, 0:n_l]
        c = n_a // 2
        idx = np.full((n_a, n_l), 2)
        idx = np.where(((xs - abs(ys - c)) % 5) == 0, 3, idx)                                       # los nervios en uve
        idx[c, :] = 4
        idx[0, :] = 1
        idx[-1, :] = 1
        if not largo_x:
            idx = idx.T
        return _imagen(idx, V['hoja']), None
    reg('hoja', hoja)

    def petalo(tw, th, cara, s):
        """El petalo: estrias a lo largo, el centro mas oscuro y el canto claro."""
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        idx = np.full((n_a, n_l), 2)
        idx[np.arange(n_a) % 2 == 0, :] = 3
        if n_a >= 4:
            idx[0, :] = 4
            idx[-1, :] = 4
        if not largo_x:
            idx = idx.T
        return _imagen(idx, V['petalo']), None
    reg('petalo', petalo)
    reg('semilla', jm.liso(V['semilla'], 2, 1, 1))
    reg('espina', jm.liso(V['espina'], 3, 1, 1))

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def _u(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def pua(out, p, d, r, h, pintor, semilla=0):
    """Una pua (o espina) en tres escalones que sale de p hacia d."""
    M = em.marco(np.asarray(p, float), np.asarray(d, float))
    caja(out, M, -r, r, -r, r, -0.4, h * 0.45, pintor, semilla=semilla)
    caja(out, M, -r * 0.64, r * 0.64, -r * 0.64, r * 0.64, h * 0.4, h * 0.76, pintor, semilla=semilla + 1)
    caja(out, M, -r * 0.32, r * 0.32, -r * 0.32, r * 0.32, h * 0.72, h, pintor, semilla=semilla + 2)


def hoja(out, P, base, d, n, largo, ancho, pintor=None, curva=0.0, semilla=0):
    """Una hoja (o un petalo): fina, de cara a n, que sale de base hacia d, ancha por el medio y en punta, en cuatro
    tramos; curva la dobla hacia atras (grados por tramo)."""
    pin = pintor or P['hoja']
    M = em.marco(np.asarray(base, float), _u(d), up=_u(n))
    perfil = ((0.0, 0.25, 0.55), (0.25, 0.55, 1.0), (0.55, 0.8, 0.82), (0.8, 1.0, 0.36))
    for j, (t0, t1, w) in enumerate(perfil):
        L = (t1 - t0) * largo
        caja(out, M, -ancho * w / 2, ancho * w / 2, -0.16, 0.16, -0.15, L + 0.15, pin, semilla=semilla + j % 2)
        M = M @ vr.T(0, 0, L) @ vr.Rx(curva * D)


def haz(out, P, ctrl, r, pintor, hebras=3, giro=1.6, afina=0.6, semilla=0):
    """Un haz de raices (o de lianas) trenzadas: varias hebras que se enroscan alrededor de la linea ctrl."""
    pts, rs, ts = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], 12, ((0.0, 1.0), (1.0, afina)))
    for h in range(hebras):
        fase = h * TAU / hebras
        cam = []
        for j, p in enumerate(pts):
            d = pts[min(j + 1, len(pts) - 1)] - pts[max(j - 1, 0)]
            M = em.marco(p, d)
            a = fase + ts[j] * giro * TAU
            cam.append(pt(M, (math.cos(a) * r * 0.55 * rs[j], math.sin(a) * r * 0.55 * rs[j], 0.0)))
        jm.tubo(out, cam, [r * 0.62 * x for x in rs], [pintor] * (len(cam) - 1), semilla=semilla + h)
    return pts


def base_de_raices(out, P, cima, n=11, alcance=17.0, semilla=0):
    """El pie de raices: el tronco que se ensancha hacia abajo, como el pie de un arbol, y las raices que salen de
    el y se extienden por el suelo, gruesas junto al tronco, bajas y torcidas, con la punta hundida; y algunas
    raicillas que asoman."""
    cima = np.asarray(cima, float)
    pts = [np.array((0.0, 0.0, 0.0)), np.array((0.0, cima[1] * 0.45, 0.0)), cima]
    pts, rs, ts = jm.a_lo_largo(pts, 6, ((0.0, 6.4), (0.35, 4.6), (1.0, 4.2)))
    jm.tubo(out, pts, rs, [P['raiz']] * (len(pts) - 1), semilla=semilla)
    rng = random.Random(semilla)
    for k in range(n):
        a = (k + rng.uniform(-0.25, 0.25)) * TAU / n
        u = np.array((math.sin(a), 0.0, math.cos(a)))
        lado = np.array((u[2], 0.0, -u[0]))
        L = alcance * rng.uniform(0.75, 1.1)
        tuerce = rng.uniform(-0.25, 0.25)
        ctrl = [u * 3.0 + np.array((0.0, rng.uniform(4.0, 6.5), 0.0)), u * 6.5 + np.array((0.0, 2.2, 0.0)),
                (u + lado * tuerce) * L * 0.62 + np.array((0.0, 0.9, 0.0)), (u + lado * tuerce * 1.6) * L + np.array((0.0, -0.4, 0.0))]
        p_, r_, t_ = jm.a_lo_largo(ctrl, 7, ((0.0, 2.4), (0.4, 1.5), (1.0, 0.45)))
        jm.tubo(out, p_, r_, [P['raiz']] * (len(p_) - 1), semilla=semilla + 1 + k % 3)
        if k % 3 == 0:                                                                              # una raicilla
            q0 = p_[3]
            jm.tubo(out, [q0, q0 + lado * 1.5 + np.array((0.0, 1.8, 0.0)), q0 + lado * 2.2 + np.array((0.0, 1.2, 0.0)) + u * 1.0],
                    [0.5, 0.35, 0.2], [P['raiz']] * 2, semilla=semilla + 4)


def brazo(out, P, hombro, codo, mano, espinas=False, semilla=0):
    """Un brazo de liana: dos hebras trenzadas que van del hombro a la mano haciendo una ese, con dos hojas que le
    brotan y una hoja-cuchilla larga en el antebrazo; acaba en tres garras de espina oscuras y curvas, no en una
    mano."""
    hombro, codo, mano = (np.asarray(p, float) for p in (hombro, codo, mano))
    d1, d2 = _u(codo - hombro), _u(mano - codo)
    ola = _u(np.cross(d1, (0.0, 0.0, 1.0)) + np.array((1e-3, 0.0, 0.0)))
    ctrl = [hombro, hombro + (codo - hombro) * 0.5 + ola * 1.4, codo, codo + (mano - codo) * 0.5 - ola * 1.2, mano]
    pts = haz(out, P, ctrl, 2.5, P['tallo'], hebras=2, giro=1.4, afina=0.7, semilla=semilla)
    fuera = _u(np.cross(d2, (0.0, 0.0, 1.0)) + np.array((1e-3, 0.0, 0.0)))
    if fuera @ (hombro - np.array((0.0, hombro[1], 0.0))) < 0:
        fuera = -fuera
    hoja(out, P, codo + fuera * 1.0, d2 * 0.85 + fuera * 0.35, np.cross(d2, fuera), 14.0, 4.2, semilla=semilla + 5)   # la cuchilla
    for t, lado in ((0.3, 1.0), (0.55, -1.0)):                                                     # las hojas que brotan
        q = pts[int(t * (len(pts) - 1))]
        hoja(out, P, q, fuera * lado + np.array((0.0, 0.9, 0.0)), np.array((0.0, 0.3, 1.0)), 6.0, 2.6, curva=8.0,
             semilla=semilla + 6)
    for j, a in enumerate((-30, 0, 30)):                                                            # las garras de espina
        Md = em.marco(mano, d2) @ vr.Ry(a * D)
        caja(out, Md, -0.75, 0.75, -0.75, 0.75, -0.4, 3.2, P['raiz'], semilla=semilla + 7)
        Mg = Md @ vr.T(0, 0, 3.0) @ vr.Rx(32 * D)
        caja(out, Mg, -0.55, 0.55, -0.55, 0.55, -0.2, 2.8, P['raiz'], semilla=semilla + 7)
        Mg = Mg @ vr.T(0, 0, 2.6) @ vr.Rx(32 * D)
        caja(out, Mg, -0.32, 0.32, -0.32, 0.32, -0.1, 2.2, P['espina'], semilla=semilla + 8)
    if espinas:
        for q in pts[2:-2:2]:
            pua(out, q + fuera * 1.3, fuera + np.array((0.0, 0.3, 0.0)), 0.45, 2.6, P['espina'], semilla=semilla + 9)


def tronco(out, P, cadera, pecho, espinas=False, semilla=0):
    """El cuerpo: el tallo grueso de la cadera al pecho, con el nudo de raices de la cadera, las hojas de vaina que
    lo envuelven subiendo y las dos hojas grandes de cada hombro."""
    cadera, pecho = np.asarray(cadera, float), np.asarray(pecho, float)
    pts, rs, ts = jm.a_lo_largo([cadera, (cadera + pecho) / 2 + np.array((0.0, 0.0, 0.8)), pecho], 8,
                                ((0.0, 4.2), (0.4, 3.1), (0.8, 3.5), (1.0, 2.9)))
    jm.tubo(out, pts, rs, [P['tallo']] * (len(pts) - 1), semilla=semilla)
    caja(out, vr.T(*cadera), -4.8, 4.8, -2.6, 2.4, -3.8, 3.8, P['raiz'], semilla=semilla + 1)         # el nudo de la cadera
    for fila, (t, n, L) in enumerate(((0.12, 6, 9.0), (0.5, 6, 8.0))):                              # las hojas de vaina
        c = cadera + (pecho - cadera) * t
        for k in range(n):
            a = (k + 0.5 * fila) * TAU / n
            u = np.array((math.sin(a), 0.0, math.cos(a)))
            hoja(out, P, c + u * 3.4, u * 0.35 + np.array((0.0, 1.0, 0.0)), u, L, 4.2, curva=-6.0, semilla=semilla + 2 + k % 2)
    for s in (1, -1):                                                                               # las hombreras
        for j, (ang, L) in enumerate(((42, 13.0), (72, 11.0))):
            base = pecho + np.array((s * 2.6, 0.4 - j * 1.2, -0.8))
            d = np.array((s * math.cos(ang * D), math.sin(ang * D), -0.3))
            hoja(out, P, base, d, np.array((0.0, 0.3, 1.0)), L, 3.6, curva=-7.0, semilla=semilla + 4)
    if espinas:
        for j in range(1, len(pts) - 1):
            for k in range(4):
                a = k * TAU / 4 + j * 0.7
                u = np.array((math.sin(a), 0.15, math.cos(a)))
                pua(out, pts[j] + u * rs[j], u, 0.5, 2.8, P['espina'], semilla=semilla + 6)


# ----------------------------------------------------------------------
#  Las flores
# ----------------------------------------------------------------------
def girasol(out, P, Mf):
    """A: el disco del girasol, mirando hacia +z: el disco de semillas, que se ordenan con el angulo de oro, y las
    espirales de las que arden; la corona de petalos secos alrededor, en dos vueltas; y el caliz verde de
    bracteas por detras. Devuelve el centro del disco."""
    R = 9.5
    for w, h in ((R, R * 0.42), (R * 0.42, R), (R * 0.72, R * 0.72)):                               # el disco
        caja(out, Mf, -w, w, -h, h, -1.2, 1.0, P['semilla'], semilla=1)
    for w, h in ((R * 0.8, R * 0.34), (R * 0.34, R * 0.8), (R * 0.58, R * 0.58)):                   # su lomo, abombado
        caja(out, Mf, -w, w, -h, h, 0.9, 1.5, P['semilla'], semilla=1)
    for k in range(1, 240):                                                                         # las semillas
        r = 0.6 * math.sqrt(k)
        if r > R * 0.92:
            break
        a = k * AUREO
        x, y = r * math.cos(a), r * math.sin(a)
        z = 1.5 + 0.35 * (1.0 - r / R)
        arde = r < 3.2 or (k % 8 == 0 and r < 8.6)
        g = 0.32 + 0.12 * (r / R)
        caja(out, Mf, x - g, x + g, y - g, y + g, z - 0.1, z + 0.35, P['luz'] if arde else P['semilla'], semilla=2)
    for vuelta, (n, L, w, z, fase) in enumerate(((21, 8.5, 2.8, 0.2, 0.0), (21, 7.0, 2.6, -0.6, 0.5))):   # los petalos
        for j in range(n):
            a = (j + fase) * TAU / n
            u = np.array((math.cos(a), math.sin(a), 0.0))
            base = pt(Mf, u * (R - 0.6) + np.array((0.0, 0.0, z)))
            d = Mf[:3, :3] @ (u + np.array((0.0, 0.0, -0.18 - 0.2 * vuelta)))
            hoja(out, P, base, d, Mf[:3, :3] @ np.array((0.0, 0.0, 1.0)), L, w, pintor=P['petalo'], curva=-5.0 - 4 * vuelta,
                 semilla=3 + j % 2)
    for j in range(13):                                                                             # el caliz
        a = j * TAU / 13
        u = np.array((math.cos(a), math.sin(a), 0.0))
        base = pt(Mf, u * (R * 0.55) + np.array((0.0, 0.0, -1.3)))
        d = Mf[:3, :3] @ (u * 0.8 + np.array((0.0, 0.0, -0.6)))
        hoja(out, P, base, d, Mf[:3, :3] @ -u, 4.5, 2.6, semilla=5)
    return pt(Mf, (0.0, 0.0, 3.0))


def vilano(out, P, Mf, rng):
    """B: el diente de leon en semilla: un corazon pequeno y, alrededor, una bola de semillas, cada una con su
    filamento y el vilano en la punta, encendido. Devuelve el centro."""
    caja(out, Mf, -2.2, 2.2, -2.2, 2.2, -2.2, 2.2, P['semilla'], semilla=1)
    caja(out, Mf, -1.6, 1.6, -2.8, 2.8, -1.6, 1.6, P['semilla'], semilla=1)
    n = 130
    R = 10.5
    for k in range(n):                                                                              # la bola de vilanos
        y = 1.0 - 2.0 * (k + 0.5) / n
        rr = math.sqrt(max(1.0 - y * y, 0.0))
        a = k * AUREO
        u = np.array((math.cos(a) * rr, y, math.sin(a) * rr))
        if u[1] < -0.85:                                                                            # por abajo, el tallo
            continue
        pie = pt(Mf, u * 2.0)
        punta = pt(Mf, u * R)
        M = em.marco(pie, punta - pie)
        L = float(np.linalg.norm(punta - pie))
        caja(out, M, -0.12, 0.12, -0.12, 0.12, 0.0, L, P['petalo'], semilla=2)
        Mt = em.marco(punta, punta - pie)
        for j in range(3):                                                                          # el vilano
            caja(out, Mt @ vr.Rz(j * 60 * D), -1.1, 1.1, -0.1, 0.1, -0.1, 0.1, P['luz'], semilla=3)
        caja(out, Mt, -0.3, 0.3, -0.3, 0.3, -0.2, 0.3, P['luz'], semilla=3)
    return pt(Mf, (0.0, 0.0, 0.0))


def semilla_suelta(out, P, p, d):
    """B: una semilla que se ha soltado y flota: el grano, el filamento y el vilano encendido."""
    p, d = np.asarray(p, float), _u(d)
    M = em.marco(p, d)
    caja(out, M, -0.25, 0.25, -0.25, 0.25, -1.4, 0.0, P['semilla'], semilla=4)
    caja(out, M, -0.1, 0.1, -0.1, 0.1, 0.0, 3.0, P['petalo'], semilla=4)
    Mt = M @ vr.T(0, 0, 3.0)
    for j in range(3):
        caja(out, Mt @ vr.Rz(j * 60 * D), -1.0, 1.0, -0.1, 0.1, -0.1, 0.1, P['luz'], semilla=5)


def cardo(out, P, Mf):
    """C: la flor del cardo, mirando hacia +z (y algo hacia arriba): el cuenco de bracteas en escalones, erizado de
    espinas en filas, y encima el penacho denso de filamentos con las puntas encendidas. Devuelve el centro del
    penacho."""
    for j, (r, z0, z1) in enumerate(((3.0, -4.0, -2.4), (4.6, -2.6, 0.2), (5.2, 0.0, 2.6), (4.4, 2.4, 4.0))):   # el cuenco
        for w, h in ((r, r * 0.42), (r * 0.42, r), (r * 0.72, r * 0.72)):
            caja(out, Mf, -w, w, -h, h, z0, z1, P['tallo'], semilla=1 + j)
    for fila, (z, r, n) in enumerate(((-3.0, 3.2, 8), (-0.8, 4.8, 11), (1.4, 5.3, 13), (3.2, 4.4, 11))):     # las espinas
        for k in range(n):
            a = (k + 0.5 * fila) * TAU / n
            u = np.array((math.cos(a), math.sin(a), 0.0))
            base = pt(Mf, u * r + np.array((0.0, 0.0, z)))
            d = Mf[:3, :3] @ (u + np.array((0.0, 0.0, 0.55)))
            pua(out, base, d, 0.42, 3.0 + 0.6 * fila, P['espina'], semilla=6)
    n = 90
    for k in range(n):                                                                              # el penacho
        r = 3.8 * math.sqrt((k + 0.5) / n)
        a = k * AUREO
        x, y = r * math.cos(a), r * math.sin(a)
        base = pt(Mf, (x, y, 3.8))
        d = Mf[:3, :3] @ np.array((x * 0.18, y * 0.18, 1.0))
        L = 6.5 - 1.2 * (r / 3.8)
        M = em.marco(base, d)
        caja(out, M, -0.2, 0.2, -0.2, 0.2, 0.0, L, P['petalo'], semilla=7)
        caja(out, M, -0.24, 0.24, -0.24, 0.24, L, L + 0.9, P['luz'], semilla=8)
    return pt(Mf, (0.0, 0.0, 8.0))


# ======================================================================
#  FLORARA
# ======================================================================
def florara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    rng = random.Random(11)
    try:
        espinas = (tipo == 'C')
        encorva = {'A': 4.0, 'B': 14.0, 'C': 10.0}[tipo]
        cadera = np.array((0.0, 12.0, 0.0))
        pecho = np.array((0.0, 31.0, 1.0 + encorva * 0.2))
        base_de_raices(out, P, cadera, semilla=120)
        tronco(out, P, cadera, pecho, espinas=espinas, semilla=100)
        brazos = {
            'A': {1: ((11.5, 22.0, 3.0), (14.5, 12.0, 8.0)), -1: ((11.0, 21.0, 2.0), (13.5, 10.5, 6.5))},
            'B': {1: ((12.5, 24.0, 6.0), (16.5, 18.0, 14.0)), -1: ((12.0, 23.0, 5.0), (16.0, 16.0, 13.0))},
            'C': {1: ((13.0, 27.0, 4.0), (18.5, 33.0, 10.0)), -1: ((12.0, 21.0, 4.0), (15.0, 11.0, 9.0))},
        }[tipo]
        for s in (1, -1):
            codo, mano = brazos[s]
            brazo(out, P, pecho + np.array((s * 4.6, -0.6, -0.4)), (s * codo[0], codo[1], codo[2]), (s * mano[0], mano[1], mano[2]),
                  espinas=espinas, semilla=140)
        # el cuello se dobla hacia delante y la flor mira abajo, a quien tiene delante
        if tipo == 'B':
            ctrl = [pecho, pecho + np.array((0.0, 8.0, -1.0)), pecho + np.array((0.0, 15.0, 3.0)), pecho + np.array((0.0, 15.5, 9.0))]
            centro, mira = pecho + np.array((0.0, 15.0, 14.0)), 10.0
        elif tipo == 'C':
            ctrl = [pecho, pecho + np.array((0.0, 6.0, 0.0)), pecho + np.array((0.0, 10.0, 2.5)), pecho + np.array((0.0, 11.5, 5.5))]
            centro, mira = pecho + np.array((0.0, 12.5, 7.0)), -25.0
        else:
            ctrl = [pecho, pecho + np.array((0.0, 7.0, -0.5)), pecho + np.array((0.0, 13.0, 2.0)), pecho + np.array((0.0, 14.0, 6.5))]
            centro, mira = pecho + np.array((0.0, 12.5, 9.0)), 30.0
        pts, rs, ts = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], 8, ((0.0, 3.0), (1.0, 2.2)))
        jm.tubo(out, pts, rs, [P['tallo']] * (len(pts) - 1), semilla=160)
        for j in (2, 5):                                                                            # dos hojas en el cuello
            d = pts[j + 1] - pts[j - 1]
            for s in (1, -1):
                u = _u(np.cross(d, (0.0, 0.0, 1.0)) * s + np.array((0.0, 0.0, 1e-3)))
                hoja(out, P, pts[j] + u * rs[j], u + np.array((0.0, 0.5, -0.3)), np.array((0.0, 1.0, 0.0)), 7.0, 3.2, curva=6.0,
                     semilla=162)
        Mf = vr.T(*centro) @ vr.Rx(mira * D)
        if tipo == 'A':
            luz = girasol(out, P, Mf)
        elif tipo == 'B':
            luz = vilano(out, P, Mf, rng)
            for k in range(9):                                                                      # las que se sueltan
                a = rng.uniform(0, TAU)
                p = centro + np.array((math.cos(a) * rng.uniform(13, 22), rng.uniform(-14, 8), math.sin(a) * rng.uniform(6, 16)))
                semilla_suelta(out, P, p, (rng.uniform(-0.4, 0.4), 1.0, rng.uniform(-0.4, 0.4)))
        else:
            luz = cardo(out, P, Mf)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    luz = pt(E, luz)
    return out, {'boca': luz, 'luces': [luz]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

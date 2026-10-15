"""
Zancara y sus formas (14-10-2026). Juan, al ver Tanara: «no todo tiene que ver con una boca con dientes grande...
algo asi raro; no poner a todo bocas y dientes; cambia el diseno y crea otro monstruo».

Un monstruo inventado y raro, sin boca: la Vigia de los Zancos, una atalaya viva. Un cuerpo pequeno, una jaula
de costillas con membrana oscura, alzado sobre zancos larguisimos de hueso, y un cuello largo de vertebras que
acaba en un solo ojo enorme. Lo que manda es el ojo: entrecerrado bajo un parpado de hueso en uve (como un ceno),
con el blanco oscuro y venoso, el iris encendido de un solo neon en anillos y la pupila negra en raja; lo enmarca
una corona de puas. Vigila desde arriba, como el farol de una torre. Todo de cajas, con texturas limpias.

Las tres formas cambian la silueta:

    A  la Vigia        sobre cuatro zancos, con el cuello alzado y el ojo en lo alto, mirando abajo; naranja de
                       faro
    B  la Errante      de pie sobre dos zancos, con el cuerpo derecho, el cuello corto y dos brazos larguisimos
                       que arrastran unas manos como rastrillos; verde acido
    C  la Pendula      sobre cuatro zancos mas altos, con el cuello colgando por debajo del cuerpo y el ojo cerca
                       del suelo, como un pendulo que barre; rosa
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
OJO = 1.2

VARIANTES = {
    'A': dict(
        clave='A', nombre='la Vigia', corto='vigia',
        membrana=_r('0e0a08', '1a120e', '281c16', '382820', '4c382c'),
        craneo=_r('16120e', '241e18', '362e24', '4c4032', '665846'),
        hueso=_r('5a4e3a', '8a7c62', 'b8a888', 'dccca8', 'f4eacc'),
        globo=_r('5a3a2a', '9a8068', 'c8b498', 'e2d4bc', 'f6eedc'),
        neon=('fff2e0', 'ff8a1e', '6a2a02'),
    ),
    'B': dict(
        clave='B', nombre='la Errante', corto='errante',
        membrana=_r('0a0c08', '12160e', '1c2216', '28301e', '384228'),
        craneo=_r('12140e', '1e2218', '2c3224', '3e4632', '545e44'),
        hueso=_r('545a44', '828a6c', 'aeb692', 'd2d8b2', 'eef2d6'),
        globo=_r('3e4a2a', '7e8a64', 'b4bc98', 'd8dcbe', 'f2f4e2'),
        neon=('f4ffe0', 'b6ff2a', '2e5a04'),
    ),
    'C': dict(
        clave='C', nombre='la Pendula', corto='pendula',
        membrana=_r('0e080c', '1a0e16', '281620', '381e2e', '4c2a3e'),
        craneo=_r('161014', '241a20', '362830', '4c3844', '664c5c'),
        hueso=_r('5a4c52', '8a7a82', 'b8a8ae', 'dccdd2', 'f6ecf0'),
        globo=_r('5a2a3e', '9a7684', 'c8acb6', 'e2d0d6', 'f6ecf0'),
        neon=('ffe6f4', 'ff3aa8', '6a0838'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'zan%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def membrana(tw, th, cara, s):
        """La membrana del cuerpo: oscura, en bandas de traves con su canto claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys % 5) == 0, 1, np.where((ys % 5) == 1, 3, 2))
        return _imagen(idx, V['membrana']), None
    reg('membrana', membrana)

    def craneo(tw, th, cara, s):
        """El hueso oscuro de los zancos, el cuello y las costillas, en placas con su sutura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx = np.where((ys % 7) == 0, 1, idx)
        idx = np.where(((xs + (ys // 7) * 3) % 8) == 0, 1, idx)
        return _imagen(_bisel(idx, 1, 1), V['craneo']), None
    reg('craneo', craneo)

    def hueso(tw, th, cara, s):
        """El hueso claro de los anillos, los parpados y las puas, con suturas de traves."""
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        idx = np.full((n_a, n_l), 3)
        idx[:, np.arange(n_l) % 6 == 0] = 1
        idx[:, np.arange(n_l) % 6 == 1] = 2
        if not largo_x:
            idx = idx.T
        return _imagen(_bisel(idx, 1, 1), V['hueso']), None
    reg('hueso', hueso)

    def globo(tw, th, cara, s):
        """El blanco del ojo, claro: con venas oscuras en lineas quebradas que salen del centro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        cx, cy = tw // 2, th // 2
        for k in range(6):
            a = k * TAU / 6 + (s % 5) * 0.3
            for t in range(max(tw, th)):
                x = int(cx + math.cos(a) * t)
                y = int(cy + math.sin(a) * t)
                if 0 <= x < tw and 0 <= y < th and t > 1:
                    idx[y, x] = 1
        return _imagen(_bisel(idx, 1, 1), V['globo']), None
    reg('globo', globo)

    def iris(tw, th, cara, s):
        """El iris encendido: anillos del neon, claro por dentro y oscuro en el canto."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((r < 0.4)[..., None], np.array(c_n), np.where((r < 0.62)[..., None], np.array(qm._mezcla(c_m, c_n, 0.5)),
                       np.where((r < 0.86)[..., None], np.array(c_m), np.array(c_h))))
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 0.9, 240)
    reg('iris', iris)
    reg('pupila', jm.liso(_r('020202', '060606', '0a0a0a', '0e0e0e', '141414'), 1, 0, 0))
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def _u(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def pua(out, p, d, r, h, pintor, semilla=0):
    """Una pua en tres escalones que sale de p hacia d."""
    M = em.marco(np.asarray(p, float), np.asarray(d, float))
    caja(out, M, -r, r, -r, r, -0.4, h * 0.45, pintor, semilla=semilla)
    caja(out, M, -r * 0.64, r * 0.64, -r * 0.64, r * 0.64, h * 0.4, h * 0.76, pintor, semilla=semilla + 1)
    caja(out, M, -r * 0.32, r * 0.32, -r * 0.32, r * 0.32, h * 0.72, h, pintor, semilla=semilla + 2)


def ojo(out, P, Mh):
    """El ojo-cabeza, mirando hacia +z: el globo redondo, en rodajas de ocho lados; el iris encendido en anillos y
    la pupila en raja, a ras del globo; los parpados finos y curvos que lo abrazan (el de arriba en dos mitades en
    uve, como un ceno, y el de abajo), con el canto claro; el caliz de seis sepalos oscuros que lo sujetan por
    detras; y la corona de puas que sale hacia atras. Devuelve el centro del iris."""
    R = 5.0
    zi = R * 0.7                                                                                    # el iris, al frente
    ri = math.sqrt(R * R - zi * zi) + 0.3
    zs = np.linspace(-R, zi, 8)
    for z0, z1 in zip(zs, zs[1:]):                                                                  # el globo, detras
        zm = (z0 + z1) / 2
        r = math.sqrt(max(R * R - zm * zm, 0.0)) + 0.25
        for w, h in ((r, r * 0.42), (r * 0.42, r), (r * 0.72, r * 0.72)):
            caja(out, Mh, -w, w, -h, h, z0, z1, P['globo'], semilla=1)
    for w, h in ((ri, ri * 0.42), (ri * 0.42, ri), (ri * 0.72, ri * 0.72)):                        # el iris
        caja(out, Mh, -w, w, -h, h, zi - 0.2, zi + 0.3, P['iris'], semilla=2)
    caja(out, Mh, -0.42, 0.42, -ri * 0.85, ri * 0.85, zi + 0.25, zi + 0.45, P['pupila'], semilla=3)  # la pupila
    caja(out, Mh, -0.8, 0.8, -0.8, 0.8, zi + 0.25, zi + 0.45, P['pupila'], semilla=3)

    def teja(M, ang, x0, x1, pin, sem):
        """Una teja del parpado: una placa fina tangente al globo, girada ang grados sobre el eje x."""
        Mt = M @ vr.Rx(ang * D) @ vr.T(0.0, R + 0.15, 0.0)
        caja(out, Mt, x0, x1, 0.0, 1.0, -1.9, 1.9, pin, semilla=sem)

    for s_ in (1, -1):                                                                              # el de arriba, en uve
        M = Mh @ vr.Rz(s_ * 13 * D)
        for ang in (0.0, 20.0, 38.0):
            teja(M, ang, *sorted((s_ * 0.1, s_ * 5.4)), P['craneo'], 4)
    for ang in (180.0, 160.0):                                                                      # el de abajo
        teja(Mh, ang, -4.6, 4.6, P['craneo'], 4)
    for k in range(6):                                                                              # el caliz
        a = (k + 0.5) * TAU / 6
        Ms = Mh @ vr.Rz(a) @ vr.T(0.0, R * 0.55, -R * 0.55) @ vr.Rx(-38 * D)
        caja(out, Ms, -2.6, 2.6, 0.0, 0.9, -1.5, 5.6, P['membrana'], semilla=6)
        caja(out, Ms, -1.6, 1.6, 0.0, 0.8, 5.4, 7.2, P['membrana'], semilla=6)
    for j in range(7):                                                                              # la corona
        a = (j - 3) / 3 * 70 * D
        u = np.array((math.sin(a), math.cos(a), 0.0))
        base = pt(Mh, (u[0] * 3.6, u[1] * 3.6, -3.0))
        d = Mh[:3, :3] @ (u + np.array((0.0, 0.0, -1.0)))
        pua(out, base, d, 0.85, (10.0 - 1.8 * abs(j - 3)) * OJO, P['hueso'], semilla=7)
    return pt(Mh, (0.0, 0.0, R + 0.5))


def cuello(out, P, ctrl, r0=2.4, r1=1.8, semilla=0):
    """El cuello: un tubo de hueso oscuro con un disco claro en cada vertebra y una pua por arriba."""
    pts, rs, ts = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], 10, ((0.0, r0), (1.0, r1)))
    jm.tubo(out, pts, rs, [P['craneo']] * (len(pts) - 1), semilla=semilla)
    for j in range(1, len(pts) - 1):
        d = pts[j + 1] - pts[j - 1]
        M = em.marco(pts[j], d, up=(0.0, 1.0, 0.0))
        g = rs[j] * 1.4
        caja(out, M, -g, g, -g * 0.75, g * 0.75, -0.3, 0.3, P['hueso'], semilla=semilla + 1)
        pua(out, pts[j] + M[:3, 1] * rs[j] * 0.9, M[:3, 1] - M[:3, 2] * 0.5, 0.45, 2.2, P['hueso'], semilla=semilla + 2)
    return pts


def cuerpo(out, P, M, largo=13.0, r=6.6, semilla=0):
    """El cuerpo: un barril de membrana oscura (la jaula), con seis costillas de hueso que lo abrazan y el espinazo
    con sus puas por arriba. M: marco del cuerpo, con +z hacia delante."""
    pts = [pt(M, (0.0, 0.0, z)) for z in np.linspace(-largo / 2, largo / 2, 7)]
    rs = [r * (0.62 + 0.38 * math.sin(math.pi * (k / 6))) for k in range(7)]
    jm.tubo(out, pts, rs, [P['membrana']] * 6, semilla=semilla, achata=1.15)
    for k in range(1, 6):                                                                           # las costillas
        z = -largo / 2 + largo * k / 6
        rr = rs[k] * 1.08
        aro = [pt(M, (math.cos(a) * rr, math.sin(a) * rr * 1.15, z)) for a in np.linspace(-0.15 * math.pi, 1.15 * math.pi, 9)]
        jm.tubo(out, aro, [0.55] * 9, [P['hueso']] * 8, semilla=semilla + 1)
    for k in range(6):                                                                              # el espinazo
        z = -largo / 2 + largo * (k + 0.5) / 6
        pua(out, pt(M, (0.0, rs[min(k, 6)] * 1.15, z)), M[:3, :3] @ np.array((0.0, 1.0, -0.35)), 0.6, 2.6, P['hueso'], semilla=semilla + 2)


def zanco(out, P, cadera, rodilla, pie, semilla=0):
    """Un zanco: el muslo y la caña larguisima de hueso oscuro, con la rodilla de hueso claro y anillos claros a
    trechos, acabado en una punta clavada en el suelo."""
    cadera, rodilla, pie = (np.asarray(p, float) for p in (cadera, rodilla, pie))
    jm.tubo(out, [cadera, rodilla], [2.5, 2.0], [P['craneo']], semilla=semilla)
    caja(out, vr.T(*rodilla), -2.4, 2.4, -2.4, 2.4, -2.4, 2.4, P['hueso'], semilla=semilla + 1)
    fin = pie + np.array((0.0, 2.6, 0.0))
    jm.tubo(out, [rodilla, (rodilla + fin) / 2, fin], [1.9, 1.4, 1.0], [P['craneo']] * 2, semilla=semilla + 2)
    L = float(np.linalg.norm(fin - rodilla))
    for t in np.arange(0.2, 1.0, 0.22):                                                             # los anillos
        p = rodilla + (fin - rodilla) * t
        M = em.marco(p, fin - rodilla)
        g = (1.5 - 0.7 * t) * 1.3
        caja(out, M, -g, g, -g, g, -0.25, 0.25, P['hueso'], semilla=semilla + 3)
    pua(out, fin, (0.0, -1.0, 0.0), 0.9, 3.0, P['hueso'], semilla=semilla + 4)                    # la punta


def brazo(out, P, hombro, codo, mano_, semilla=0):
    """Un brazo larguisimo de hueso que cuelga hasta el suelo: el hombro de hueso claro, el brazo y el antebrazo
    con anillos, y la mano de cuatro dedos largos como un rastrillo, con las unas negras."""
    hombro, codo, mano_ = (np.asarray(p, float) for p in (hombro, codo, mano_))
    caja(out, vr.T(*hombro), -2.2, 2.2, -2.2, 2.2, -2.2, 2.2, P['hueso'], semilla=semilla)
    jm.tubo(out, [hombro, codo, mano_], [1.6, 1.3, 1.0], [P['craneo']] * 2, semilla=semilla + 1)
    caja(out, vr.T(*codo), -1.7, 1.7, -1.7, 1.7, -1.7, 1.7, P['hueso'], semilla=semilla + 2)
    Mm = em.marco(mano_, mano_ - codo)
    caja(out, Mm, -1.4, 1.4, -0.5, 0.5, -0.3, 2.0, P['hueso'], semilla=semilla + 3)
    for j in range(4):
        x = (j - 1.5) * 0.9
        Mf = Mm @ vr.T(x, 0.0, 1.9) @ vr.Ry(x * 12 * D) @ vr.Rx(12 * D)
        for k, L in enumerate((2.6, 2.2, 1.8)):
            g = 0.32 - 0.05 * k
            caja(out, Mf, -g, g, -g, g, 0.0, L, P['hueso'], semilla=semilla + 4)
            Mf = Mf @ vr.T(0, 0, L) @ vr.Rx(12 * D)


def cola(out, P, ctrl, semilla=0):
    """La cola: vertebras que se afinan y acaban en un garfio."""
    pts, rs, ts = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], 10, ((0.0, 1.8), (1.0, 0.5)))
    jm.tubo(out, pts, rs, [P['craneo']] * (len(pts) - 1), semilla=semilla)
    for j in range(1, len(pts) - 1, 2):
        M = em.marco(pts[j], pts[j + 1] - pts[j - 1])
        g = rs[j] * 1.4
        caja(out, M, -g, g, -g, g, -0.25, 0.25, P['hueso'], semilla=semilla + 1)
    pua(out, pts[-1], _u(pts[-1] - pts[-2]) + np.array((0.0, 0.6, 0.0)), 0.5, 2.6, P['hueso'], semilla=semilla + 2)


# ======================================================================
#  ZANCARA
# ======================================================================
def zancara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        if tipo == 'A':
            Y = 36.0
            Mb = vr.T(0.0, Y, 0.0) @ vr.Rx(-6 * D)
            cuerpo(out, P, Mb, semilla=100)
            caderas = [(s, z) for s in (1, -1) for z in (4.5, -4.5)]
            for s, z in caderas:
                cad = pt(Mb, (s * 4.6, -2.5, z))
                zanco(out, P, cad, cad + np.array((s * 1.6, -7.0, z * 0.25)), np.array((s * 8.0, 0.0, z * 1.7)), semilla=120)
            cuello(out, P, [pt(Mb, (0.0, 3.0, 6.0)), (0.0, Y + 12.0, 9.0), (0.0, Y + 20.0, 13.0), (0.0, Y + 20.5, 19.0),
                            (0.0, Y + 17.0, 22.5)], semilla=140)
            Mh = vr.T(0.0, Y + 14.5, 25.0) @ vr.Rx(24 * D) @ np.diag([OJO * 1.25] * 3 + [1.0])
            cola(out, P, [pt(Mb, (0.0, 0.0, -6.5)), (0.0, Y - 5.0, -11.0), (0.0, Y - 13.0, -12.0), (0.0, Y - 18.0, -8.0)], semilla=160)
        elif tipo == 'B':
            Y = 30.0
            Mb = vr.T(0.0, Y + 6.5, 0.0) @ vr.Rx(-78 * D)                  # el cuerpo, de pie
            cuerpo(out, P, Mb, largo=15.0, r=6.6, semilla=100)
            for s in (1, -1):
                cad = np.array((s * 3.6, Y - 1.0, 0.0))
                zanco(out, P, cad, cad + np.array((s * 1.0, -12.0, 2.5)), np.array((s * 5.0, 0.0, -1.0)), semilla=120)
                hombro = np.array((s * 7.0, Y + 12.0, 1.0))                # los brazos, que arrastran
                codo = np.array((s * 11.0, Y - 2.0, 3.5))
                mano_ = np.array((s * 12.5, 4.0, 6.0))
                brazo(out, P, hombro, codo, mano_, semilla=150)
            cuello(out, P, [(0.0, Y + 13.5, 1.0), (0.0, Y + 19.0, 2.5), (0.0, Y + 22.0, 6.0), (0.0, Y + 21.0, 10.0)],
                   r0=2.6, r1=2.0, semilla=140)
            Mh = vr.T(0.0, Y + 18.5, 13.5) @ vr.Rx(22 * D) @ np.diag([OJO * 1.25] * 3 + [1.0])
        else:
            Y = 44.0
            Mb = vr.T(0.0, Y, 0.0)
            cuerpo(out, P, Mb, largo=11.0, r=5.8, semilla=100)
            for s, z in [(s, z) for s in (1, -1) for z in (4.0, -4.0)]:
                cad = pt(Mb, (s * 4.8, -2.0, z))
                zanco(out, P, cad, cad + np.array((s * 1.8, -8.0, z * 0.3)), np.array((s * 9.0, 0.0, z * 2.0)), semilla=120)
            cuello(out, P, [pt(Mb, (0.0, -5.5, 2.0)), (0.0, Y - 12.0, 4.0), (0.0, Y - 20.0, 6.5), (0.0, Y - 26.0, 9.0)],
                   r0=2.6, r1=1.9, semilla=140)
            Mh = vr.T(0.0, Y - 31.0, 11.0) @ vr.Rx(10 * D) @ np.diag([OJO * 1.25] * 3 + [1.0])
            for j in range(5):                                                                      # su corona, en el lomo
                a = (j - 2) / 2 * 50 * D
                pua(out, pt(Mb, (math.sin(a) * 3.0, 6.0, -1.0 + j * 0.3)), (math.sin(a), 1.0, -0.4), 1.0, 8.0 - 1.5 * abs(j - 2),
                    P['hueso'], semilla=170)
            cola(out, P, [pt(Mb, (0.0, 0.0, -6.0)), (0.0, Y - 3.0, -12.0), (0.0, Y - 10.0, -14.0), (0.0, Y - 15.0, -10.0)], semilla=160)
        bm.PPB = PPB / (OJO * 1.25)
        luz = ojo(out, P, Mh)
        bm.PPB = PPB
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    luz = pt(E, luz)
    return out, {'boca': luz, 'luces': [luz]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

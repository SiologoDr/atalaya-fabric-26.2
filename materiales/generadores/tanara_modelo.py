"""
Tanara y sus formas (14-10-2026). Juan, al descartar la Estinfalida: «nos estamos alejando de lo principal
como Espinara, Lumara, que no son animales como tal sino creaciones de monstruos... sorprendeme».

Version 2, el mismo dia. La primera llevaba colgando una cabeza de fauces enormes, y Juan: «ojo, no todo tiene
que ver con una boca con dientes grande... pudiste haber hecho en Tanara como una momia, algo asi raro; no poner a
todo bocas y dientes». Ahora el badajo de la campana es una momia.

Un monstruo inventado, no un animal: una cupula viva de costillas de hueso con membrana oscura entre ellas (como
una medusa), que flota, y debajo, colgada del centro como el badajo de una campana, una momia envuelta en
vendas. No tiene boca: lo que manda son los ojos, que arden por una rendija entre las vendas de la cara, y la luz
que se escapa por las grietas de las vendas del pecho. La membrana es oscura y va en bandas; su borde libre va
encendido. Del borde cuelgan tiras de venda que ondean. Todo de cajas y laminas, con texturas limpias.

Las tres formas cambian la silueta:

    A  la Campana       la cupula honda echada atras como una capucha; la momia cuelga con los brazos cruzados
                        sobre el pecho y las piernas atadas; oro de ambar
    B  la Desplegada    la cupula abierta y muy ancha, con garfios largos; la momia abre los brazos, de los que
                        cuelgan vendas largas como alas rotas; rojo sangre
    C  la Encapuchada   la cupula pequena como una capucha sobre la cabeza de la momia, que tiende hacia delante
                        cuatro brazos vendados con manos de hueso y arrastra una cola de vendas; blanco hueso
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
ESCALA = 0.62

GARRA = _r('08080a', '121214', '1c1c20', '28282e', '38383e')
VARIANTES = {
    'A': dict(
        clave='A', nombre='la Campana', corto='campana',
        membrana=_r('120806', '1e0e08', '2c180c', '3e2412', '56341a'),
        hueso=_r('5a4e3a', '8a7c62', 'b8a888', 'dccca8', 'f4eacc'),
        craneo=_r('140f0a', '221a12', '33281c', '4a3b2a', '665240'),
        venda=_r('241a10', '3e2e1c', '5c4a30', '7e6a48', 'a48e66'),
        garra=GARRA, neon=('fff6d8', 'ffb21e', '6a3a02'),
    ),
    'B': dict(
        clave='B', nombre='la Desplegada', corto='desplegada',
        membrana=_r('10050a', '1c0910', '2a0e18', '3c1622', '541f2e'),
        hueso=_r('4e463e', '7a6e62', 'a89a8a', 'd0c4b2', 'eee6d8'),
        craneo=_r('140c0e', '221618', '342226', '4a3236', '66484c'),
        venda=_r('261616', '402626', '5e3a36', '7e5248', 'a0705e'),
        garra=GARRA, neon=('ffe4e6', 'ff2b38', '6a0410'),
    ),
    'C': dict(
        clave='C', nombre='la Encapuchada', corto='encapuchada',
        membrana=_r('0c0c0e', '161618', '222226', '303036', '424248'),
        hueso=_r('5a5248', '8a8070', 'b8ac98', 'dcd2be', 'f8f2e4'),
        craneo=_r('121214', '1e1e22', '2e2e34', '44444c', '5e5e68'),
        venda=_r('1c1c1e', '2e2e30', '46444a', '625e64', '827c80'),
        garra=GARRA, neon=('ffffff', 'f2deb0', '6a5432'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'tan2%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def membrana(tw, th, cara, s):
        """La membrana de la cupula: oscura, en bandas de traves con su canto claro, y una vena clara a cada
        lado, junto a las costillas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys % 5) == 0, 1, np.where((ys % 5) == 1, 3, 2))
        if tw >= 6:
            idx = np.where((xs == 1) | (xs == tw - 2), 3, idx)
        return _imagen(idx, V['membrana']), None
    reg('membrana', membrana)

    def hueso(tw, th, cara, s):
        """El hueso: claro, con suturas oscuras de traves cada pocos pixeles y el canto en bisel."""
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        idx = np.full((n_a, n_l), 3)
        idx[:, np.arange(n_l) % 6 == 0] = 1
        idx[:, np.arange(n_l) % 6 == 1] = 2
        if not largo_x:
            idx = idx.T
        return _imagen(_bisel(idx, 1, 1), V['hueso']), None
    reg('hueso', hueso)

    def craneo(tw, th, cara, s):
        """El hueso viejo y oscuro de las costillas, en placas con su sutura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx = np.where((ys % 7) == 0, 1, idx)
        idx = np.where(((xs + (ys // 7) * 3) % 8) == 0, 1, idx)
        return _imagen(_bisel(idx, 1, 1), V['craneo']), None
    reg('craneo', craneo)
    reg('garra', jm.liso(V['garra'], 2, 2, 1))

    def _vendas(tw, th, base):
        """Las vendas: tiras que dan la vuelta un poco en diagonal, cada una con su canto claro y la junta oscura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        k = ys * 2 + xs // 3
        return np.where((k % 6) == 0, 1, np.where((k % 6) == 1, base + 1, base))

    reg('venda', lambda tw, th, c, s: (_imagen(_vendas(tw, th, 2), V['venda']), None))
    reg('venda_clara', lambda tw, th, c, s: (_imagen(_vendas(tw, th, 3), V['venda']), None))
    reg('hueco', jm.liso(_r('040404', '08080a', '0c0c0e', '121214', '18181a'), 1, 0, 0))

    def borde(tw, th, cara, s):
        """El borde libre de la membrana y las grietas de las vendas, encendidos: el neon con el centro claro."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        v = (ys + 0.5) / th
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((v < 0.35)[..., None], np.array(c_m), np.where((v < 0.7)[..., None], np.array(qm._mezcla(c_m, c_n, 0.5)),
                                                                     np.array(c_m)))
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, np.ones((th, tw), bool), 220)
    reg('borde', borde)

    def grieta(tw, th, cara, s):
        return borde(tw, th, cara, s)
    reg('grieta', grieta)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)
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


def _perfil(t, R, H, forma):
    """El perfil de la cupula: radio y bajada a la altura t (0 en la cima, 1 en el borde)."""
    if forma == 'campana':
        return R * (1 - (1 - t) ** 2.2) * (1 + 0.12 * t ** 6), -H * t ** 1.5
    if forma == 'sombrilla':
        return R * t ** 0.85, -H * t ** 1.3
    return R * (1 - (1 - t) ** 1.8), -H * t ** 1.25                       # la capucha


def cima_eje(M):
    """El eje de la cupula a media altura (para echar hacia fuera los festones)."""
    return pt(M, (0.0, -4.0, 0.0))


def cupula(out, P, cima, R, H, n, forma, inclina=0.0, garfio=2.5, semilla=0):
    """La cupula: n costillas de hueso que bajan de la cima al borde y acaban en garfio, y entre ellas la
    membrana en bandas, por las dos caras; el ultimo tramo cuelga en festones y su borde libre va encendido.
    Devuelve el marco de la cupula y las puntas de las costillas."""
    M = vr.T(*cima) @ vr.Rx(inclina * D)
    m = 7
    costillas = []
    for i in range(n):
        a = (i + 0.5) * TAU / n
        u = np.array((math.sin(a), 0.0, math.cos(a)))
        pts = []
        for j in range(m + 1):
            r, y = _perfil(j / m, R, H, forma)
            pts.append(pt(M, (u[0] * r, y, u[2] * r)))
        costillas.append((a, pts))
        jm.tubo(out, pts, [0.8] + [1.3] * (m - 1) + [1.0], [P['craneo']] * m, semilla=semilla)
        d = _u(pts[-1] - pts[-2])                                                                  # el garfio
        abajo = _u(d + np.array((0.0, -1.2, 0.0)))
        pua(out, pts[-1], abajo, 0.85, garfio, P['hueso'], semilla=semilla + 1)

    def lienzo(A, B, C, Dd, pintor, sem):
        ancho = float(np.linalg.norm(B - A) + np.linalg.norm(C - Dd)) / 2
        alto = float(np.linalg.norm(Dd - A) + np.linalg.norm(C - B)) / 2
        if ancho < 0.05:
            return
        lamina(out, (Dd, C, B, A), pintor, max(ancho, 0.3), max(alto, 0.3), semilla=sem)       # por fuera
        lamina(out, (A, B, C, Dd), pintor, max(ancho, 0.3), max(alto, 0.3), semilla=sem)       # y por dentro

    abajo = np.array((0.0, -0.9, 0.0))
    for i in range(n):                                                                             # la membrana
        a0, p0 = costillas[i]
        a1, p1 = costillas[(i + 1) % n]
        for j in range(m - 1):
            lienzo(p0[j], p1[j], p1[j + 1], p0[j + 1], P['membrana'], semilla + 2 + j % 2)
        arriba = (p0[m - 1] + p1[m - 1]) / 2
        bajo = (p0[m] + p1[m]) / 2 + np.array((0.0, -0.22 * H - 0.8, 0.0)) + _u((p0[m] + p1[m]) / 2 - cima_eje(M)) * 0.6
        lienzo(p0[m - 1], arriba, bajo, p0[m], P['membrana'], semilla + 3)
        lienzo(arriba, p1[m - 1], p1[m], bajo, P['membrana'], semilla + 3)
        for A, B in ((p0[m], bajo), (bajo, p1[m])):
            lienzo(A + abajo, B + abajo, B, A, P['borde'], semilla + 4)
    cima_w = pt(M, (0.0, 0.0, 0.0))
    caja(out, vr.T(*cima_w), -2.4, 2.4, -0.6, 1.6, -2.4, 2.4, P['craneo'], semilla=semilla + 5)      # el nudo de la cima
    for k in range(5):                                                                             # su corona de puas
        a = k * TAU / 5
        u = np.array((math.sin(a) * 0.5, 1.0, math.cos(a) * 0.5))
        pua(out, cima_w + np.array((math.sin(a) * 1.4, 1.0, math.cos(a) * 1.4)), M[:3, :3] @ u, 0.7, 3.4, P['hueso'], semilla=semilla + 6)
    return M, [(a, pts[-1]) for a, pts in costillas]


def cinta(out, P, a, largo, direccion=(0.0, -1.0, 0.0), ancho=1.4, ola=1.4, fase=0.0, pintor=None, semilla=0):
    """Una tira de venda que cuelga de a y ondea: tramos planos que siguen una ese suave, y la punta deshilachada
    en dos hilos."""
    pin = pintor or P['venda']
    a = np.asarray(a, float)
    d = _u(direccion)
    lado = _u(np.cross(d, (0.0, 0.0, 1.0)) + np.array((1e-3, 0.0, 0.0)))
    n = max(4, int(largo / 2.2))
    pts = [a + d * largo * (k / n) + lado * ola * math.sin(fase + k / n * math.pi * 1.6) * (k / n) for k in range(n + 1)]
    for k in range(n):
        p0, p1 = pts[k], pts[k + 1]
        M = em.marco(p0, p1 - p0, up=np.cross(lado, p1 - p0) + np.array((0.0, 0.0, 1e-3)))
        L = float(np.linalg.norm(p1 - p0))
        w = ancho * (1.0 - 0.35 * k / n)
        caja(out, M, -w / 2, w / 2, -0.13, 0.13, -0.1, L + 0.1, pin, semilla=semilla + k % 2)
    M = em.marco(pts[-1], pts[-1] - pts[-2])
    for s in (1, -1):                                                                              # los hilos
        caja(out, M @ vr.Ry(s * 12 * D), s * 0.2 - 0.12, s * 0.2 + 0.12, -0.1, 0.1, 0.0, 1.8, pin, semilla=semilla + 2)


def mano(out, P, muneca, d, abre=0.0, semilla=0):
    """Una mano de hueso que asoma de las vendas: la palma y cuatro dedos largos de tres falanges con las unas
    negras, abiertos."""
    Mm = em.marco(np.asarray(muneca, float), _u(d))
    caja(out, Mm, -1.3, 1.3, -0.5, 0.5, -0.3, 2.0, P['hueso'], semilla=semilla)
    for j in range(4):
        x = (j - 1.5) * 0.85
        Mf = Mm @ vr.T(x, 0.0, 1.9) @ vr.Ry(x * (14 + abre) * D) @ vr.Rx(16 * D)
        for k, L in enumerate((2.0, 1.7, 1.4)):
            g = 0.3 - 0.05 * k
            caja(out, Mf, -g, g, -g, g, 0.0, L, P['hueso'], semilla=semilla + 1)
            Mf = Mf @ vr.T(0, 0, L) @ vr.Rx(14 * D)
        caja(out, Mf, -0.18, 0.18, -0.18, 0.18, 0.0, 0.9, P['garra'], semilla=semilla + 2)


def brazo(out, P, hombro, codo, muneca, abre=0.0, cintas=0, semilla=0):
    """Un brazo vendado: el brazo y el antebrazo como tubos de vendas, la mano de hueso, y unas tiras sueltas que
    cuelgan del antebrazo."""
    hombro, codo, muneca = (np.asarray(p, float) for p in (hombro, codo, muneca))
    jm.tubo(out, [hombro, codo, muneca], [1.5, 1.3, 1.1], [P['venda']] * 2, semilla=semilla)
    mano(out, P, muneca, muneca - codo, abre=abre, semilla=semilla + 3)
    for k in range(cintas):
        t = (k + 1) / (cintas + 1)
        a = codo + (muneca - codo) * t + np.array((0.0, -1.0, 0.0))
        cinta(out, P, a, 9.0 + 5.0 * (k % 2), ancho=1.6, ola=1.2, fase=k, semilla=semilla + 6)


def momia(out, P, Mm, pose='cruzados', piernas=True):
    """La momia-badajo, con el origen en la coronilla (hacia abajo, -y; la cara, hacia +z): la cabeza envuelta,
    con las vendas cruzadas por la cara y una rendija negra por la que arden los ojos; el cuello; el pecho y los
    hombros, con la luz que se escapa por las grietas de las vendas; la cintura; los brazos segun la pose
    (cruzados sobre el pecho, abiertos o cuatro tendidos hacia delante); y las piernas atadas en un solo haz que se
    afina hasta los pies. Devuelve los puntos de luz (los ojos y el pecho)."""
    V, VC = P['venda'], P['venda_clara']
    caja(out, Mm, -2.7, 2.7, -5.8, 0.0, -2.6, 2.5, V, semilla=1)                                       # la cabeza
    caja(out, Mm, -2.2, 2.2, -6.7, -5.2, -2.0, 2.1, V, semilla=2)
    for s in (1, -1):                                                                               # la rendija, en uve
        Me = Mm @ vr.T(s * 1.1, -2.15, 0.0) @ vr.Rz(s * 13 * D)
        caja(out, Me, -1.25, 1.25, -0.7, 0.6, 2.4, 2.62, P['hueco'], semilla=3)
        caja(out, Me, -0.75, 0.6, -0.42, 0.32, 2.55, 2.75, P['ojo'], semilla=4)                    # los ojos
    for k, (y, ang) in enumerate(((-0.9, 14), (-3.7, -17), (-5.0, 9))):                             # vendas cruzadas
        caja(out, Mm @ vr.T(0.0, y, 2.5) @ vr.Rz(ang * D), -2.95, 2.95, -0.36, 0.36, 0.0, 0.32, VC, semilla=5)
    caja(out, Mm, -1.5, 1.5, -7.8, -6.2, -1.5, 1.5, V, semilla=6)                                    # el cuello
    caja(out, Mm, -3.9, 3.9, -15.5, -7.4, -2.3, 2.3, V, semilla=7)                                   # el pecho
    caja(out, Mm, -4.7, 4.7, -9.8, -7.2, -2.0, 2.0, VC, semilla=8)                                   # los hombros
    caja(out, Mm, -3.1, 3.1, -20.5, -15.2, -1.9, 1.9, V, semilla=9)                                  # la cintura
    for k, (x, y, ang, l) in enumerate(((0.4, -10.0, 12, 2.4), (-0.3, -12.2, -10, 3.0), (0.2, -14.2, 8, 2.2))):
        caja(out, Mm @ vr.T(x, y, 2.3) @ vr.Rz(ang * D), -l, l, -0.24, 0.24, 0.0, 0.2, P['grieta'], semilla=10)
    caja(out, Mm @ vr.T(0.0, -18.0, 1.9) @ vr.Rz(-6 * D), -1.6, 1.6, -0.2, 0.2, 0.0, 0.18, P['grieta'], semilla=10)
    if piernas:                                                                                     # atadas
        for y0, y1, g in ((-26.5, -20.2, 3.0), (-32.0, -26.0, 2.6), (-36.5, -31.6, 2.1)):
            caja(out, Mm, -g, g, y0, y1, -g * 0.7, g * 0.7, V, semilla=11)
        for s in (1, -1):
            caja(out, Mm, s * 1.0 - 0.9, s * 1.0 + 0.9, -37.6, -36.2, -1.3, 2.4, VC, semilla=12)
        for k, (x, y) in enumerate(((2.6, -24.0), (-2.4, -29.0), (1.8, -33.0))):                  # tiras sueltas
            cinta(out, P, pt(Mm, (x, y, 1.0)), 7.0 + 2.0 * k, ancho=1.3, ola=1.0, fase=k * 1.3, semilla=13)

    def hombro(s, y=-8.5):
        return pt(Mm, (s * 4.3, y, 0.0))
    if pose == 'cruzados':
        for s in (1, -1):
            codo = pt(Mm, (s * 4.9, -14.3, 1.2))
            mun = pt(Mm, (-s * 1.9, -10.6 + (0.6 if s > 0 else -0.6), 3.2 + (0.7 if s > 0 else 0.0)))
            brazo(out, P, hombro(s), codo, mun, abre=-4.0, semilla=20)
    elif pose == 'abiertos':
        for s in (1, -1):
            codo = pt(Mm, (s * 10.0, -11.0, 0.6))
            mun = pt(Mm, (s * 15.5, -14.5, 1.8))
            brazo(out, P, hombro(s), codo, mun, abre=10.0, cintas=3, semilla=20)
    else:                                                                                           # cuatro, hacia delante
        for s in (1, -1):
            brazo(out, P, hombro(s), pt(Mm, (s * 7.5, -9.5, 4.5)), pt(Mm, (s * 9.5, -10.5, 11.0)), abre=10.0, cintas=1, semilla=20)
            brazo(out, P, hombro(s, -15.5), pt(Mm, (s * 6.8, -17.5, 4.0)), pt(Mm, (s * 8.5, -20.0, 10.0)), abre=6.0, cintas=1,
                  semilla=25)
    return [pt(Mm, (0.0, -2.1, 4.5)), pt(Mm, (0.0, -12.0, 5.0))]


# ======================================================================
#  TANARA
# ======================================================================
def tanara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        if tipo == 'A':
            cima, R, H, n, forma, inclina, garfio = (0.0, 66.0, -6.0), 16.0, 15.0, 10, 'campana', -30.0, 2.6
            coronilla, cabeceo, pose = np.array((0.0, 59.0, 4.0)), 14.0, 'cruzados'
        elif tipo == 'B':
            cima, R, H, n, forma, inclina, garfio = (0.0, 62.0, -4.0), 24.0, 7.0, 12, 'sombrilla', -24.0, 6.5
            coronilla, cabeceo, pose = np.array((0.0, 57.5, 3.0)), 12.0, 'abiertos'
        else:
            cima, R, H, n, forma, inclina, garfio = (0.0, 56.0, -3.0), 10.5, 13.0, 9, 'capucha', -48.0, 2.2
            coronilla, cabeceo, pose = np.array((0.0, 50.0, 5.5)), 18.0, 'cuatro'
        Mc, puntas = cupula(out, P, cima, R, H, n, forma, inclina=inclina, garfio=garfio, semilla=100)
        # la momia cuelga dentro de la cupula, como el badajo: la cabeza metida en ella y sujeta por tiras de venda
        Mm = vr.T(*coronilla) @ vr.Rx(cabeceo * D)
        for s, x, y in ((1, 3.0, -2.0), (-1, 3.0, -2.0), (1, 5.5, -4.5), (-1, 5.5, -4.5)):
            arriba = pt(Mc, (s * x, y, -2.0))
            abajo = pt(Mm, (s * (2.6 if x < 4 else 4.4), -1.0 if x < 4 else -7.6, -1.2))
            jm.tubo(out, [arriba, (arriba + abajo) / 2 + np.array((0.0, -0.6, 0.0)), abajo], [0.7, 0.6, 0.55], [P['venda_clara']] * 2,
                    semilla=121)
        luces = momia(out, P, Mm, pose=pose, piernas=(tipo != 'C'))
        if tipo == 'C':                                                                             # la cola de vendas
            base = pt(Mm, (0.0, -19.5, -1.0))
            ctrl = [base, base + np.array((0.0, -10.0, -4.0)), base + np.array((1.5, -18.0, -12.0)), np.array((3.0, 1.5, base[2] - 24.0))]
            pts, rs, ts = jm.a_lo_largo(ctrl, 9, ((0.0, 2.8), (1.0, 0.8)))
            jm.tubo(out, pts, rs, [P['venda']] * (len(pts) - 1), semilla=130)
        # tiras de venda que cuelgan del borde de la cupula (no por delante)
        rng = random.Random(7)
        for i, (a, p) in enumerate(puntas):
            if math.cos(a) > (0.55 if tipo != 'C' else -0.2) or (tipo == 'B' and i % 2):
                continue
            largo = rng.uniform(14.0, 24.0) if tipo != 'B' else rng.uniform(18.0, 28.0)
            cinta(out, P, p + np.array((0.0, -1.5, 0.0)), largo, ancho=1.5, ola=1.6, fase=a * 3, semilla=140)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0 + 5.0, 0)                     # flota sobre el suelo
    out = qm.transformar(out, E)
    luces = [pt(E, l) for l in luces]
    return out, {'boca': luces[0], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

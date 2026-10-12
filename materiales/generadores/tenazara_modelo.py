"""
Boceto de un jefe en tres tipos (12-10-2026). Juan, tras Riscara: «me gusto tambien ese
monstruo y sus variables; ahora sigue haciendo mas, ya no de ese monstruo sino otro y
sus variables».

  Tenazara, la de las Tenazas Hambrientas: una alacrana colosal, baja y ancha, con las
  tenazas en alto y la cola arqueada sobre el lomo. Lo nuevo: sus tenazas son fauces;
  se abren como dos bocas con dientes en peine, encendidas por dentro y con el nucleo al
  fondo, y el aguijon es un bulbo de su veneno que brilla. La misma alacrana en tres tipos:

    A  del Desierto   quitina negra en bandas y anillos de oro con remaches; neon ambar
    B  de la Geoda    quitina violeta en manchas y drusas de amatista; neon violeta
    C  del Arrecife   quitina verdeazul con lunares, corales y percebes; neon rosa coral

Mismo oficio que Simara y Riscara: cajas con las caras pintadas a 8 px por bloque y
texturas dibujadas, sin ruido ni motas sueltas.
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
from sierpe_modelo import _borde_de, _limpiar, _manchas, _bisel, _escudos, _remaches, _degradado, lamina, bola
from riscara_modelo import bloque

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 8

TIPOS = {
    'A': dict(
        clave='A', nombre='del Desierto',
        piel=_r('0c0907', '18120d', '261c14', '38291c', '503b28'),
        junta=_r('080605', '120e0a', '1e1710', '2c2218', '3e3022'),
        oro=_r('3a2406', '6e4a0e', 'a87818', 'dcae38', 'fae08a'),
        diente=_r('6a5a44', 'a8967a', 'd6c6aa', 'eee2cc', 'fbf6ea'),
        neon=('fff2c8', 'ffae2a', '7a3c06'),
    ),
    'B': dict(
        clave='B', nombre='de la Geoda',
        piel=_r('0a0612', '160c22', '241434', '34204a', '4a2e66'),
        junta=_r('07040c', '100a18', '1a1026', '261836', '36224a'),
        cristal=_r('3a1466', '6a2aa8', '9a52e0', 'c890fa', 'ecd6ff'),
        diente=_r('6a5a80', 'a898c0', 'd2c6e6', 'ece4f6', 'faf6ff'),
        neon=('f8ecff', 'b46aff', '4a1a8a'),
    ),
    'C': dict(
        clave='C', nombre='del Arrecife',
        piel=_r('041614', '082a26', '0e3e38', '16564e', '247268'),
        junta=_r('03100e', '061c1a', '0c2c28', '123c36', '1c5048'),
        claro=_r('2a5c50', '4a8a78', '7ab8a2', 'aedcc8', 'e0f6ec'),
        coral=_r('6a1426', 'a42a40', 'e0566a', 'ff8c96', 'ffc8c6'),
        percebe=_r('3e3e36', '6a6a5c', '9a9a88', 'c4c4b2', 'e8e8da'),
        diente=_r('5a6a66', '98aaa4', 'cad8d2', 'e6f0ec', 'f8fffc'),
        neon=('fff0f4', 'ff6a8a', '7a0a2a'),
    ),
}


def pintores(T):
    k = T['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'ten%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = T['neon']

    # ---------------- el caparazon ----------------
    if k == 'A':
        def caparazon(tw, th, cara, s):
            """Quitina en bandas: cada banda con su canto claro arriba y su sombra abajo, y la
            raya del lomo por el medio."""
            ys, xs = np.mgrid[0:th, 0:tw]
            v = ys % 5
            idx = np.where(v == 0, 3, np.where(v == 4, 1, 2))
            if tw >= 8 and cara in ('arriba', 'frente', 'atras'):
                idx = np.where((np.abs(xs - (tw - 1) / 2) < 1.0) & (v != 0), 4, idx)
            return _imagen(_bisel(idx), T['piel']), None
    elif k == 'B':
        def caparazon(tw, th, cara, s):
            """Manchas grandes y limpias, como el marmol de Ofidia."""
            idx = _manchas(tw, th, s, celda=6.0, umbral=0.6, alto=0.82)
            idx = np.array([1, 1, 2, 3, 4])[idx]
            return _imagen(_bisel(idx), T['piel']), None
    else:
        def caparazon(tw, th, cara, s):
            """Verdeazul con lunares claros de borde oscuro, en una rejilla movida."""
            idx = np.full((th, tw), 2)
            rng = random.Random(s * 7 + tw * 3 + th)
            ys, xs = np.mgrid[0:th, 0:tw]
            luna = np.zeros((th, tw), bool)
            for gy in range(3, th + 3, 9):
                for gx in range(2 + (gy // 9) % 2 * 4, tw + 3, 9):
                    if rng.random() < 0.3:
                        continue
                    cx, cy = gx + rng.uniform(-1.2, 1.2), gy + rng.uniform(-1.2, 1.2)
                    luna |= np.hypot(xs - cx, ys - cy) < rng.uniform(1.5, 2.2)
            idx = _bisel(idx)
            tex = _imagen(idx, T['piel'])
            claro = T['claro']
            orilla = _borde_de(luna)
            tex[orilla] = (*T['piel'][0], 255)
            tex[luna] = (*claro[1], 255)
            brillo = luna & ~np.roll(luna, 1, axis=0)
            tex[brillo] = (*claro[2], 255)
            return tex, None
    reg('caparazon', caparazon)

    def junta(tw, th, cara, s):
        return _imagen(_escudos(tw, th), T['junta']), None
    reg('junta', junta)

    def pata(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if tw >= 4:
            idx[:, 1] = 3
        return _imagen(_bisel(idx), T['piel']), None
    reg('pata', pata)

    def diente(tw, th, cara, s):
        idx = np.full((th, tw), 3)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 2
        if th >= 3:
            idx[-1, :] = 2
        return _imagen(idx, T['diente']), None
    reg('diente', diente)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def nucleo(tw, th, cara, s):
        """El fondo de cada tenaza: anillos limpios del neon, blanco en el centro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        dentro = r < 1.0
        anillo = (np.floor(r * 5) % 2) == 0
        col = np.where(anillo[..., None], np.array(c_m), np.array(qm._mezcla(c_h, c_m, 0.4)))
        col = np.where((r < 0.3)[..., None], np.array(c_n), col)
        col = np.where(((r > 0.88) & dentro)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = np.where(dentro, 255, 0)
        return t, _emis(t, dentro & (r < 0.88), 240)
    reg('nucleo', nucleo)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)

    def veneno(tw, th, cara, s):
        """El bulbo del aguijon: quitina con gajos de veneno encendido entre las costillas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        costilla = (xs % 4) == 0
        idx = np.where(costilla, 2, 1)
        tex = _imagen(_bisel(idx), T['junta'])
        gajo = ~costilla & (ys > 0) & (ys < th - 1)
        k_ = np.abs(ys - (th - 1) / 2) / max((th - 1) / 2, 1)
        col = np.where((k_ < 0.35)[..., None], np.array(nm._hex(nuc)), np.array(nm._hex(neo)))
        col = np.where(((xs % 4) == 1)[..., None], np.array(qm._mezcla(nm._hex(hon), nm._hex(neo), 0.5)), col)
        tex[gajo, :3] = col[gajo]
        return tex, _emis(tex, gajo, 230)
    reg('veneno', veneno)

    def aguijon(tw, th, cara, s):
        idx = np.full((th, tw), 1)
        if tw >= 3:
            idx[:, 0] = 2
        if th >= 4:
            idx[0, :] = 3
        return _imagen(idx, T['junta']), None
    reg('aguijon', aguijon)

    # ---------------- lo propio de cada tipo ----------------
    if k == 'A':
        def oro(tw, th, cara, s):
            """Los anillos de oro: un cinturon con su canto claro, su sombra y remaches."""
            idx = np.full((th, tw), 2)
            if cara in ('der', 'izq'):
                idx[:, 0] = 3
                idx[:, -1] = 1
            else:
                idx[0, :] = 3
                idx[-1, :] = 1
            return _imagen(_remaches(idx, cara), T['oro']), None
        reg('oro', oro)
    if k == 'B':
        def cristal(tw, th, cara, s):
            """Amatista: dos tonos partidos en diagonal y un filo de luz; el filo brilla un poco."""
            ys, xs = np.mgrid[0:th, 0:tw]
            diag = xs * th - ys * tw
            idx = np.where(diag > 0, 3, 2)
            idx = np.where(np.abs(diag) < max(tw, th) * 0.7, 4, idx)
            if tw >= 3:
                idx[:, -1] = 1
            if th >= 3:
                idx[-1, :] = 1
            tex = _imagen(idx, T['cristal'])
            return tex, _emis(tex, idx >= 4, 140)
        reg('cristal', cristal)
    if k == 'C':
        def coral(tw, th, cara, s):
            """Coral: la piel en anillos de dos tonos y la punta clara, que brilla un poco."""
            ys, xs = np.mgrid[0:th, 0:tw]
            idx = np.where((ys % 3) == 0, 3, 2)
            if th >= 4 and cara not in ('arriba', 'abajo'):
                idx[:2, :] = 4
            if cara == 'arriba':
                idx[:] = 4
            if tw >= 3:
                idx[:, -1] = 1
            tex = _imagen(idx, T['coral'])
            return tex, _emis(tex, idx >= 4, 110)
        reg('coral', coral)

        def percebe(tw, th, cara, s):
            idx = np.full((th, tw), 2)
            if cara == 'arriba':
                idx[:] = 1
                if tw >= 3 and th >= 3:
                    idx[1:-1, 1:-1] = 0
                return _imagen(idx, T['percebe']), None
            if th >= 3:
                idx[0, :] = 4
                idx[1, :] = 3
            return _imagen(_bisel(idx), T['percebe']), None
        reg('percebe', percebe)
    return P


# ----------------------------------------------------------------------
#  Lo que le crece encima segun el tipo
# ----------------------------------------------------------------------
def drusa(out, M, P, n=4, alto=1.4, semilla=0):
    """Un racimo de cristales de amatista que nacen de un punto."""
    r = random.Random(semilla)
    for j in range(n):
        Mi = M @ vr.T(r.uniform(-0.3, 0.3), 0, r.uniform(-0.3, 0.3)) @ vr.Rz(r.uniform(-30, 30) * D) @ vr.Rx(r.uniform(-30, 30) * D)
        g = r.uniform(0.2, 0.32)
        bm.cristal(out, Mi, g, alto * (1.0 if j == 0 else r.uniform(0.5, 0.85)), P['cristal'], semilla=semilla + j)


def rama_coral(out, M, P, alto=1.4, nivel=0, semilla=0):
    """Un coral de cuernos: un tronco cuadrado que se abre en dos, y cada rama otra vez."""
    r = random.Random(semilla)
    g = 0.2 - nivel * 0.045
    cubo(out, M, -g, 0, -g, 2 * g, alto, 2 * g, P['coral'], semilla=semilla)
    if nivel < 2:
        for j, lado in enumerate((-1, 1)):
            Mi = M @ vr.T(0, alto * r.uniform(0.6, 0.9), 0) @ vr.Ry(r.uniform(0, 1.2) + j * 1.6) @ vr.Rz(lado * r.uniform(28, 42) * D)
            rama_coral(out, Mi, P, alto * 0.62, nivel + 1, semilla + 7 * (j + 1))


def percebes(out, M, P, n=5, radio=0.8, semilla=0):
    """Unos percebes: cada uno un cono de dos escalones con la boca oscura arriba."""
    r = random.Random(semilla)
    for j in range(n):
        x, z = r.uniform(-radio, radio), r.uniform(-radio, radio)
        Mi = M @ vr.T(x, -0.05, z)
        g = r.uniform(0.14, 0.24)
        cubo(out, Mi, -g, 0, -g, 2 * g, g * 1.3, 2 * g, P['percebe'], semilla=semilla + j)
        cubo(out, Mi, -g * 0.6, g * 1.3, -g * 0.6, g * 1.2, g * 0.6, g * 1.2, P['percebe'], semilla=semilla + j + 9)


def adorno(out, M, P, k, semilla=0, alto=1.3):
    """En el lomo: puas (A), drusas de amatista (B) o coral y percebes (C)."""
    if k == 'A':
        pua(out, M @ vr.Rx(-25 * D), 0.18, alto * 0.75, P['aguijon'], semilla=semilla)
    elif k == 'B':
        drusa(out, M, P, n=3 + semilla % 2, alto=alto, semilla=semilla)
    else:
        if semilla % 3 != 1:
            rama_coral(out, M @ vr.Rz(((semilla % 3) - 1) * 12 * D), P, alto=alto, semilla=semilla)
            percebes(out, M, P, n=3, radio=0.5, semilla=semilla + 3)
        else:
            percebes(out, M, P, n=6, radio=0.7, semilla=semilla)


# ======================================================================
#  TENAZARA
# ======================================================================
def tenazara(tipo='A', abre=50.0, semilla=1):
    T = TIPOS[tipo]
    P = pintores(T)
    k = T['clave']
    out = []
    anillo = P['oro'] if k == 'A' else P['junta']

    # el prosoma: la coraza de delante, con el escudo, los ojos y la boca
    Mp = vr.T(0, 3.4, 2.1) @ vr.Rx(-5 * D)
    bloque(out, Mp, 6.4, 2.6, 5.4, P['caparazon'], caras={'abajo': P['junta']}, semilla=1)
    cubo(out, Mp, -3.4, 1.2, -2.85, 6.8, 0.45, 5.7, P['caparazon'], semilla=2)                    # el escudo
    cubo(out, Mp, -1.8, 1.65, -2.5, 3.6, 0.24, 4.1, P['caparazon'], semilla=3)                    # el lomo del escudo
    for s in (1, -1):                                                                           # los ojos
        cubo(out, Mp, s * 0.55 - 0.28, 1.89, 1.0, 0.56, 0.4, 0.56, P['ojo'], semilla=4)
        for (x, y, z) in ((2.7, 1.2, 2.45), (3.05, 1.05, 2.05), (2.3, 1.28, 2.7)):
            cubo(out, Mp, s * x - 0.15, y, z, 0.3, 0.3, 0.22, P['ojo'], semilla=5)
    for s in (1, -1):                                                                           # los queliceros
        Mq = Mp @ vr.T(s * 0.72, -0.5, 2.6) @ vr.Ry(s * 12 * D)
        cubo(out, Mq, -0.48, -0.48, 0, 0.96, 0.96, 1.3, P['caparazon'], semilla=6)
        pua(out, Mq @ vr.T(-s * 0.25, -0.48, 1.1) @ vr.Rx(170 * D), 0.11, 0.7, P['diente'], semilla=7)
    cubo(out, Mp, -0.85, -1.2, 2.72, 1.7, 1.15, 0.05, None, caras={'frente': P['nucleo']}, semilla=8)  # la boca
    if k == 'A':
        cubo(out, Mp, -3.45, 1.15, 2.45, 6.9, 0.55, 0.45, P['oro'], semilla=9)                    # el filo de oro del escudo
    else:
        adorno(out, Mp @ vr.T(-1.9, 1.65, -1.2), P, k, semilla=9, alto=1.7)
        adorno(out, Mp @ vr.T(1.8, 1.65, -0.3), P, k, semilla=10, alto=1.3)

    # el mesosoma: seis anillos (el mas ancho en medio) con su placa encima y su junta detras
    for j, (w, h) in enumerate(((6.2, 2.5), (6.5, 2.55), (6.4, 2.5), (6.0, 2.4), (5.4, 2.25), (4.6, 2.1))):
        z = -1.35 - j * 1.5
        y = 3.35 - j * 0.05
        M = vr.T(0, y, z)
        bloque(out, M, w, h, 1.42, P['caparazon'], caras={'abajo': P['junta']}, semilla=11 + j)
        cubo(out, M, -w / 2 - 0.15, h / 2 - 0.1, -0.7, w + 0.3, 0.4, 1.4, P['caparazon'], semilla=17 + j)
        cubo(out, M, -w / 2 + 0.22, -h / 2 + 0.12, -0.82, w - 0.44, h - 0.24, 0.14, P['junta'], semilla=23 + j)
        if k == 'A':
            pua(out, M @ vr.T(0, h / 2 + 0.3, -0.2) @ vr.Rx(-30 * D), 0.18, 0.8, P['aguijon'], semilla=29 + j)
        elif j in (0, 2, 3, 5):
            adorno(out, M @ vr.T((1.3 if j % 2 else -1.3), h / 2 + 0.3, 0), P, k, semilla=30 + j, alto=1.4 - 0.1 * j)

    # las patas: cuatro pares, bajas y fuertes
    for s in (1, -1):
        for j, za in enumerate((3.4, 1.8, 0.2, -1.4)):
            cad = np.array((s * 2.9, 2.6, za))
            rod = np.array((s * (5.0 + 0.3 * j), 4.6 - 0.2 * j, za + 0.8 - 0.75 * j))
            tob = np.array((s * (6.6 + 0.45 * j), 1.5, za + 1.4 - 1.3 * j))
            pie = tob + np.array((s * 0.35, -1.5, 0.2 - 0.25 * j))
            viga(out, cad, rod, 0.85, 0.85, P['caparazon'], extra=0.15, semilla=40 + j)
            bola(out, vr.T(*rod), 0.5, anillo, semilla=44)
            viga(out, rod, tob, 0.66, 0.66, P['pata'], extra=0.1, semilla=45 + j)
            viga(out, tob, pie, 0.46, 0.46, P['aguijon'], semilla=49)

    # los brazos y las tenazas, que son fauces
    for s in (1, -1):
        hom = np.array((s * 2.8, 3.4, 4.4))
        codo = np.array((s * 5.9, 4.3, 5.3))
        mun = np.array((s * 6.1, 4.9, 8.1))
        viga(out, hom, codo, 1.25, 1.2, P['caparazon'], extra=0.3, semilla=50)
        viga(out, codo, mun, 1.2, 1.15, P['caparazon'], extra=0.3, semilla=51)
        bola(out, vr.T(*codo), 0.8, anillo, semilla=52)
        bola(out, vr.T(*mun), 0.72, anillo, semilla=53)
        tenaza(out, em.marco(mun, (-s * 0.18, 0.1, 1.0)) @ np.diag([1.08, 1.08, 1.08, 1.0]), P, abre, k, s)

    # la cola: tramos con su anillo, arqueada por encima del lomo hasta la cabeza
    ctrl = [(0, 3.3, -9.4), (-0.2, 6.6, -11.7), (-0.9, 11.0, -11.6), (-1.7, 14.9, -8.8), (-1.9, 17.0, -5.0), (-1.4, 16.6, -1.4)]
    pts, _ = em.catmull(ctrl, 8)
    pts = [np.asarray(p, float) for p in pts]
    marcos = sm._marcos(pts, (0, 0, -1))
    for i, M in enumerate(marcos):
        t = i / max(len(marcos) - 1, 1)
        r = 1.5 - 0.5 * t
        L = float(np.linalg.norm(pts[i + 1] - pts[i]))
        cubo(out, M, -r, -r, -0.1, 2 * r, 2 * r, L + 0.2, P['caparazon'], caras={'abajo': P['junta']}, semilla=60 + i)
        cubo(out, M, -r * 0.6, r - 0.05, 0.2, r * 1.2, 0.3, L - 0.2, P['caparazon'], semilla=67 + i)       # la quilla
        rb = r * 1.12
        cubo(out, M @ vr.T(0, 0, -0.25), -rb, -rb, 0, 2 * rb, 2 * rb, 0.5, anillo, semilla=74 + i)
        if k == 'A':
            pua(out, M @ vr.T(0, r + 0.25, L * 0.55) @ vr.Rx(-40 * D), 0.17, 0.9, P['aguijon'], semilla=81 + i)
        elif i in (1, 3, 5):
            adorno(out, M @ vr.T(0, r + 0.25, L * 0.5), P, k, semilla=82 + i, alto=1.2)
    Mfin = marcos[-1] @ vr.T(0, 0, float(np.linalg.norm(pts[-1] - pts[-2])))
    cubo(out, Mfin @ vr.T(0, 0, -0.1), -0.85, -0.85, 0, 1.7, 1.7, 0.55, anillo, semilla=88)
    # el bulbo del veneno y el aguijon, que se curva hacia delante y abajo
    Mb = Mfin @ vr.T(0, -0.2, 1.6)
    bola(out, Mb, 1.4, P['veneno'], semilla=89)
    p0 = punto(Mb, (0, -0.55, 1.1))
    ruta = [p0]
    for d in ((0, -0.8, 1.2), (0, -1.3, 0.55), (0, -1.0, -0.35)):
        ruta.append(ruta[-1] + (punto(Mb, d) - punto(Mb, (0, 0, 0))))
    for j, (a, b) in enumerate(zip(ruta, ruta[1:])):
        g = 0.56 - j * 0.16
        viga(out, a, b, g, g, P['aguijon'], extra=0.05, semilla=90 + j)
    return out, {'bulbo': punto(Mb, (0, 0, 0))}


def dedo(out, M0, P, lado, semilla=0):
    """Un dedo de la tenaza: tres tramos que se estrechan y se curvan hacia la boca, con la
    cara de dentro encendida, los dientes en peine por los dos bordes y un gancho en la
    punta. lado=1 es el de arriba (los dientes miran abajo) y -1 el de abajo."""
    M = M0
    dentro = 'abajo' if lado > 0 else 'arriba'
    fuera = 'arriba' if lado > 0 else 'abajo'
    tramos = ((2.3, 0.95, 1.75, 0), (1.85, 0.82, 1.55, 15), (1.35, 0.7, 1.35, 17))
    for j, (w, h, l, curva) in enumerate(tramos):
        if j:
            M = M @ vr.T(0, 0, tramos[j - 1][2] - 0.08) @ vr.Rx(lado * curva * D)
        y0 = 0 if lado > 0 else -h
        cubo(out, M, -w / 2, y0, 0, w, h, l, P['caparazon'], caras={dentro: P['fauces'], fuera: P['caparazon']}, semilla=semilla + j)
        n = 3 if j < 2 else 2
        for x in (-1, 1):
            for q in range(n):
                largo = (0.62 - 0.1 * j) + 0.16 * ((q + j + (lado < 0)) % 2)
                Md = M @ vr.T(x * (w / 2 - 0.2), 0, 0.3 + q * (l - 0.45) / max(n - 1, 1))
                pua(out, Md @ vr.Rx(180 * D) if lado > 0 else Md, 0.09, largo, P['diente'], semilla=semilla + 10 + q)
    w, h, l, _ = tramos[-1]
    Mg = M @ vr.T(0, (h * 0.35) * lado, l - 0.15) @ vr.Rx((125 if lado > 0 else 55) * D)
    pua(out, Mg, 0.26, 1.2, P['aguijon'], semilla=semilla + 20)
    for x in (-0.3, 0.3):                                  # los dos colmillos de la punta
        Md = M @ vr.T(x, 0, l - 0.3)
        pua(out, Md @ vr.Rx(180 * D) if lado > 0 else Md, 0.1, 0.75, P['diente'], semilla=semilla + 21)


def tenaza(out, Mc, P, abre, k, s):
    """La tenaza en su marco (+Z hacia delante): la palma abultada y dos dedos que se abren
    como mandibulas, encendidos por dentro, con el nucleo al fondo."""
    bloque(out, Mc @ vr.T(0, 0, 1.5), 3.0, 2.7, 3.4, P['caparazon'], caras={'abajo': P['junta']}, semilla=1)
    dedo(out, Mc @ vr.T(0, 0.45, 3.0) @ vr.Rx(-abre * 0.45 * D), P, 1, semilla=2)
    dedo(out, Mc @ vr.T(0, -0.45, 3.0) @ vr.Rx(abre * 0.55 * D), P, -1, semilla=30)
    # al fondo, el nucleo que brilla
    cubo(out, Mc @ vr.T(0, 0, 3.22), -0.9, -0.9, 0, 1.8, 1.8, 0.05, None, caras={'frente': P['nucleo']}, semilla=60)
    # lo de cada tipo sobre la palma
    if k == 'A':
        cubo(out, Mc, -1.6, -1.52, 0.35, 3.2, 3.04, 0.6, P['oro'], semilla=61)
        cubo(out, Mc, -1.6, -1.52, 2.35, 3.2, 3.04, 0.45, P['oro'], semilla=62)
        for j in range(3):
            pua(out, Mc @ vr.T(0, 1.45, 0.5 + j * 0.8) @ vr.Rx(-35 * D), 0.16, 0.8 - j * 0.12, P['aguijon'], semilla=63 + j)
    else:
        adorno(out, Mc @ vr.T(-s * 0.35, 1.45, 1.2), P, k, semilla=30 + (s > 0), alto=1.3)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

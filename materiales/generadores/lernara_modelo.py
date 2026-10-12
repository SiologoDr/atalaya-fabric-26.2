"""
Boceto de un jefe en tres variantes (12-10-2026). Juan, tras Tenazara: «haz el siguiente
con sus variantes; recuerda que deben ser variados los tipos de variantes, no lo mismo;
y esta vez es un escorpion literalmente, no es un monstruo como los anteriores».

  Lernara, la Hidra de la Cienaga: un monstruo, no un animal. Un cuerpo de dragon sin alas,
  pesado y bajo, del que salen varios cuellos, cada uno con su cabeza y sus fauces
  encendidas (dientes en peine y el nucleo al fondo de la garganta). Las tres variantes
  cambian de FORMA, no solo de color:

    A  de Tres Cabezas    tres cuellos en abanico; cabezas con cuernos hacia atras;
                          escamas verde negro; neon verde
    B  de Cinco Cabezas   cinco cuellos unidos por una membrana que se abre como una
                          capucha; cabezas con aletas; piel lisa con manchas; neon magenta
    C  de Dos Cabezas     dos cuellos trenzados como una soga que se abren arriba en dos;
                          cabezas con capucha; placas con anillos de bronce; neon cian

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
from sierpe_modelo import _borde_de, _limpiar, _manchas, _bisel, _escamas_cara, _escudos, _remaches, _degradado, lamina, bola
from riscara_modelo import bloque

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 8

VARIANTES = {
    'A': dict(
        clave='A', nombre='de Tres Cabezas', cabezas=3,
        piel=_r('060c08', '0e1a10', '18281a', '263c28', '3a5638'),
        vientre=_r('1e2414', '323a20', '4a5430', '687444', '8e9a5e'),
        hueso=_r('2a2418', '4a4028', '6e6040', '948664', 'bcb088'),
        diente=_r('6a6650', 'a6a28a', 'd2cfb8', 'ecead8', 'fbfaf0'),
        bronce=_r('1a1408', '3a2c12', '5e4820', '8a6c34', 'b8945a'),
        ala=_r('060a06', '0c140c', '141e12', '1e2a1a', '2a3a24'),
        neon=('f4ffd0', '96ff2a', '2a6a06'),
    ),
    'B': dict(
        clave='B', nombre='de Cinco Cabezas', cabezas=5,
        piel=_r('0c0610', '1a0c20', '2a1434', '3e2050', '58306e'),
        vientre=_r('241424', '3c2238', '583452', '7a4c70', 'a26e94'),
        hueso=_r('2a1c28', '4a3046', '6e4a66', '94708c', 'bc9cb4'),
        diente=_r('6a5a68', 'a898a8', 'd6c8d4', 'eee4ec', 'fdf8fc'),
        bronce=_r('1a1408', '3a2c12', '5e4820', '8a6c34', 'b8945a'),
        ala=_r('0e0814', '1c0e26', '2c163c', '3e2254', '58326e'),
        neon=('fff0fc', 'ff4ad8', '6a0a52'),
    ),
    'C': dict(
        clave='C', nombre='de Dos Cabezas', cabezas=2,
        piel=_r('060a10', '0e1620', '182434', '26364a', '3a5068'),
        vientre=_r('1a222a', '2c3a46', '445666', '62788a', '8aa2b4'),
        hueso=_r('1c2028', '323844', '4c5462', '6c7686', '949eae'),
        diente=_r('5a6670', '98a8b2', 'cad8de', 'e6f0f2', 'f8ffff'),
        bronce=_r('1e1408', '44300e', '6e5018', '9c762a', 'd2a44a'),
        ala=_r('0a1420', '142232', '1e3248', '2a4660', '3c6080'),
        neon=('f2ffff', '52e2ff', '0a5a7c'),
    ),
}


def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'ler%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    # ---------------- la piel: cada variante con la suya ----------------
    if k == 'A':
        def cuerpo(tw, th, cara, s):
            """Escamas en U, como Simara y Riscara."""
            return _imagen(_escamas_cara(tw, th, cara), V['piel']), None
    elif k == 'B':
        def cuerpo(tw, th, cara, s):
            """Piel lisa de anguila con manchas grandes de borde limpio."""
            idx = _manchas(tw, th, s, celda=6.5, umbral=0.62, alto=0.82)
            idx = np.array([1, 1, 2, 3, 4])[idx]
            return _imagen(_bisel(idx), V['piel']), None
    else:
        def cuerpo(tw, th, cara, s):
            """Placas en bandas que se solapan: cada banda con su canto claro arriba y su sombra
            abajo, y una costura por el medio."""
            ys, xs = np.mgrid[0:th, 0:tw]
            v = ys % 5
            idx = np.where(v == 0, 3, np.where(v == 4, 1, 2))
            if tw >= 8:
                idx = np.where((np.abs(xs - (tw - 1) / 2) < 0.6) & (v != 0), 1, idx)
            return _imagen(_bisel(idx), V['piel']), None
    reg('cuerpo', cuerpo)

    def vientre(tw, th, cara, s):
        return _imagen(_escudos(tw, th), V['vientre']), None
    reg('vientre', vientre)

    def hueso(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if cara in ('der', 'izq', 'frente', 'atras') and tw >= 4:
            idx[:, 1] = 3
        return _imagen(_bisel(idx), V['hueso']), None
    reg('hueso', hueso)

    def diente(tw, th, cara, s):
        idx = np.full((th, tw), 3)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 2
        if th >= 3:
            idx[-1, :] = 2
        return _imagen(idx, V['diente']), None
    reg('diente', diente)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def nucleo(tw, th, cara, s):
        """El fondo de la garganta: anillos limpios del neon, blanco en el centro."""
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
        t = qm._emisivo(nuc, neo, max(2, tw), max(2, th))
        th2, tw2 = t.shape[:2]
        if tw2 >= 3:
            t[:, tw2 // 2] = (*nm._hex(hon), 255)
        return t, None
    reg('ojo', ojo, pleno=True)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

    def fosa(tw, th, cara, s):
        return _imagen(np.zeros((th, tw), int), V['piel']), None
    reg('fosa', fosa)

    def bronce(tw, th, cara, s):
        """Los collares de bronce: un cinturon con su canto claro, su sombra y remaches."""
        idx = np.full((th, tw), 2)
        if cara in ('der', 'izq'):
            idx[:, 0] = 3
            idx[:, -1] = 1
        else:
            idx[0, :] = 3
            idx[-1, :] = 1
        return _imagen(_remaches(idx, cara), V['bronce']), None
    reg('bronce', bronce)

    def _membrana(tw, th, s, libre):
        """Membrana oscura en tres bandas (la raiz abajo); si el borde es libre, va en festones
        y encendido con el neon."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        u = (xs + 0.5) / tw
        v = 1 - (ys + 0.5) / th
        idx = np.where(v < 0.35, 1, np.where(v < 0.75, 2, 3))
        img = _imagen(idx, V['ala'])
        borde = (th - 1) * (0.04 + 0.16 * np.abs(np.sin(np.pi * u * 2))) if libre else np.zeros_like(u)
        fuera = ys < borde
        brillo = np.zeros((th, tw), bool)
        if libre:
            filo = (~fuera) & (ys < borde + 2.0)
            img[filo] = (*nm._hex(neo), 255)
            brillo |= filo
        t[~fuera] = img[~fuera]
        return t, _emis(t, brillo & ~fuera, 215)

    def membrana(tw, th, cara, s):
        return _membrana(tw, th, s, True)
    reg('membrana', membrana)

    def membrana_lisa(tw, th, cara, s):
        return _membrana(tw, th, s, False)
    reg('membrana_lisa', membrana_lisa)
    return P


# ----------------------------------------------------------------------
#  Ayudas de forma
# ----------------------------------------------------------------------
def cuello(out, ctrl, radios, P, n=9, semilla=0, collar=None, bandas=False):
    """Un cuello de tramos cuadrados por una curva (el lomo atras y arriba), con la franja de
    escudos por delante. Devuelve los puntos y los marcos."""
    pts, _ = em.catmull(ctrl, n + 1)
    pts = [np.asarray(p, float) for p in pts]
    marcos = sm._marcos(pts, (0, 0, -1))
    for i, M in enumerate(marcos):
        t = i / max(len(marcos) - 1, 1)
        r = radios[0] + (radios[1] - radios[0]) * t
        L = float(np.linalg.norm(pts[i + 1] - pts[i]))
        cubo(out, M, -r, -r, -0.1, 2 * r, 2 * r, L + 0.2, P['cuerpo'], semilla=semilla + i)
        cubo(out, M, -r * 0.55, -r - 0.12, -0.1, r * 1.1, 0.26, L + 0.2, P['vientre'], semilla=semilla + i)
        if bandas and i % 2 == 1:
            rb = r * 1.12
            cubo(out, M @ vr.T(0, 0, -0.22), -rb, -rb, 0, 2 * rb, 2 * rb, 0.44, P['bronce'], semilla=semilla + i)
    if collar:                                             # el collar de bronce bajo la cabeza
        M = marcos[-1]
        L = float(np.linalg.norm(pts[-1] - pts[-2]))
        rb = radios[1] * 1.18
        cubo(out, M @ vr.T(0, 0, L * 0.3), -rb, -rb, 0, 2 * rb, 2 * rb, 0.55, P['bronce'], semilla=semilla + 50)
    return pts, marcos


def cabeza(out, Mh, V, P, abre, corona):
    """Una cabeza de la hidra (en su marco, +Z hacia delante): craneo, hocico, fauces abiertas
    con los dientes en peine, cuatro ojos y la corona de su variante."""
    cubo(out, Mh, -1.5, -0.8, -1.8, 3.0, 2.2, 3.2, P['cuerpo'], caras={'abajo': P['vientre']}, semilla=1)
    cubo(out, Mh @ vr.T(0, 1.05, -0.4) @ vr.Rx(8 * D), -1.62, 0, 0, 3.24, 0.5, 2.2, P['hueso'], semilla=2)      # la ceja
    cubo(out, Mh, -1.2, -0.7, 1.3, 2.4, 1.6, 1.9, P['cuerpo'], caras={'abajo': P['fauces']}, semilla=3)
    Ms2 = Mh @ vr.T(0, 0, 3.1) @ vr.Rx(5 * D)
    cubo(out, Ms2, -0.9, -0.65, 0, 1.8, 1.3, 1.9, P['cuerpo'], caras={'abajo': P['fauces']}, semilla=4)
    cubo(out, Ms2, -0.3, 0.6, 0.2, 0.6, 0.3, 1.5, P['hueso'], semilla=5)                                       # la cresta del hocico
    for s in (1, -1):
        cubo(out, Ms2, s * 0.45 - 0.15, 0.4, 1.85, 0.3, 0.18, 0.08, P['fosa'], semilla=6)
        x0 = 1.5 if s > 0 else -1.56
        for j, (y, z) in enumerate(((0.55, 0.75), (0.2, 1.25))):                                           # dos ojos por lado
            cubo(out, Mh, x0, y, z, 0.06, 0.3, 0.45, P['ojo'], semilla=7)
    # los dientes de arriba, en peine, y los colmillos
    for s in (1, -1):
        for j in range(5):
            pua(out, Mh @ vr.T(s * 1.05, -0.7, 1.5 + j * 0.36) @ vr.Rx(180 * D), 0.09, 0.85 + 0.25 * (j % 2), P['diente'], semilla=8 + j)
        for j in range(5):
            pua(out, Ms2 @ vr.T(s * 0.75, -0.65, 0.2 + j * 0.36) @ vr.Rx(180 * D), 0.09, 0.8 + 0.2 * (j % 2), P['diente'], semilla=13 + j)
    for j in range(5):
        x = -0.6 + j * 0.3
        largo = 1.6 if j in (0, 4) else 0.9
        pua(out, Ms2 @ vr.T(x, -0.65, 1.75) @ vr.Rx(180 * D), 0.12 if j in (0, 4) else 0.09, largo, P['diente'], semilla=18 + j)
    # la mandibula, abierta
    Mj = Mh @ vr.T(0, -0.8, -1.3) @ vr.Rx(abre * D)
    cubo(out, Mj, -1.3, -0.85, 0, 2.6, 0.85, 3.4, P['cuerpo'], caras={'arriba': P['fauces'], 'abajo': P['vientre']}, semilla=23)
    Mj2 = Mj @ vr.T(0, 0, 3.35) @ vr.Rx(-8 * D)
    cubo(out, Mj2, -0.95, -0.75, 0, 1.9, 0.75, 2.6, P['cuerpo'], caras={'arriba': P['fauces'], 'abajo': P['vientre']}, semilla=24)
    for s in (1, -1):
        for j in range(7):
            pua(out, Mj @ vr.T(s * 1.15, 0, 0.55 + j * 0.4), 0.09, 0.75 + 0.2 * (j % 2), P['diente'], semilla=25 + j)
        for j in range(5):
            pua(out, Mj2 @ vr.T(s * 0.8, 0, 0.3 + j * 0.42), 0.09, 0.7 + 0.18 * (j % 2), P['diente'], semilla=32 + j)
    for j in range(4):
        x = -0.55 + j * 0.37
        pua(out, Mj2 @ vr.T(x, 0, 2.45), 0.12 if j in (0, 3) else 0.09, 1.3 if j in (0, 3) else 0.8, P['diente'], semilla=37 + j)
    # al fondo de la garganta, el nucleo
    Mv = Mh @ vr.T(0, -1.25, 0.8) @ vr.Rx(abre * 0.5 * D)
    cubo(out, Mv, -0.95, -0.95, 0, 1.9, 1.9, 0.05, None, caras={'frente': P['nucleo']}, semilla=41)

    if corona == 'cuernos':
        for s in (1, -1):                                # dos cuernos que se van hacia atras y hacia fuera
            p = punto(Mh, (s * 1.05, 1.35, -0.4))
            for j, (d, g) in enumerate((((s * 0.35, 0.75, -0.9), 0.5), ((s * 0.35, 0.35, -1.0), 0.38),
                                        ((s * 0.2, 0.05, -1.0), 0.28), ((s * 0.05, -0.2, -0.9), 0.2))):
                q = p + (punto(Mh, d) - punto(Mh, (0, 0, 0))) * 1.25
                viga(out, p, q, g, g, P['hueso'], extra=0.06, semilla=42 + j)
                p = q
        for j in range(3):                               # puas por la frente
            pua(out, Mh @ vr.T(0, 1.5, 1.0 - j * 0.85) @ vr.Rx(-40 * D), 0.15, 0.8 - j * 0.1, P['hueso'], semilla=46)
    elif corona == 'cresta':
        raiz = punto(Mh, (0, 1.3, -1.6))                 # la cresta, de la frente a la nuca
        puntas = [raiz + (punto(Mh, d) - punto(Mh, (0, 0, 0))) for d in ((0, 1.6, 1.2), (0, 2.2, 0.0), (0, 1.6, -1.2))]
        for q in puntas:
            viga(out, raiz, q, 0.14, 0.14, P['hueso'], semilla=49)
        for a, b in zip(puntas, puntas[1:]):
            lamina(out, (raiz, raiz, b, a), P['membrana'], float(np.linalg.norm(b - a)), float(np.linalg.norm(a - raiz)), 50)
    elif corona == 'capucha':
        nuca = punto(Mh, (0, 0.2, -1.7))                 # la capucha: seis varillas abiertas en ovalo detras de la cabeza
        puntas = []
        for j in range(7):
            phi = math.radians(-95 + j * 31.7)
            d = punto(Mh, (math.sin(phi) * 3.1, math.cos(phi) * 2.3 + 0.4, -0.4)) - punto(Mh, (0, 0, 0))
            fin = nuca + d
            viga(out, nuca, fin, 0.16, 0.16, P['hueso'], semilla=51)
            puntas.append(fin)
        for a, b in zip(puntas, puntas[1:]):
            lamina(out, (nuca, nuca, b, a), P['membrana'], float(np.linalg.norm(b - a)), float(np.linalg.norm(a - nuca)), 52)


# ======================================================================
#  El cuerpo, que es el mismo en las tres
# ======================================================================
def cuerpo(out, V, P):
    k = V['clave']
    # el pecho alzado, el vientre y las caderas
    Mpe = vr.T(0, 5.5, 1.4) @ vr.Rx(-16 * D)
    bloque(out, Mpe, 6.0, 4.4, 4.4, P['cuerpo'], caras={'abajo': P['vientre']}, semilla=1)
    cubo(out, Mpe, -1.6, -2.3, -1.6, 3.2, 0.32, 3.4, P['vientre'], semilla=2)
    Mvi = vr.T(0, 5.1, -2.4) @ vr.Rx(-4 * D)
    bloque(out, Mvi, 5.6, 4.0, 4.2, P['cuerpo'], caras={'abajo': P['vientre']}, semilla=3)
    cubo(out, Mvi, -1.5, -2.1, -2.0, 3.0, 0.3, 4.0, P['vientre'], semilla=4)
    Mca = vr.T(0, 5.0, -6.0) @ vr.Rx(8 * D)
    bloque(out, Mca, 4.8, 3.6, 3.6, P['cuerpo'], caras={'abajo': P['vientre']}, semilla=5)
    # las espinas del lomo
    for j, (y, z) in enumerate(((8.1, 0.2), (7.6, -1.6), (7.3, -3.3), (7.1, -5.0), (6.8, -6.6))):
        Mt = vr.T(0, y - 0.3, z) @ vr.Rx(-30 * D)
        pua(out, Mt, 0.26, 1.2 - j * 0.12, P['hueso'], semilla=10 + j)
        for s in (1, -1):
            pua(out, vr.T(s * 1.3, y - 0.6, z - 0.4) @ vr.Rz(-s * 25 * D) @ vr.Rx(-30 * D), 0.16, 0.7 - j * 0.06, P['hueso'], semilla=15 + j)
    # las patas: brazo, antebrazo y una mano de tres garras; detras, muslo, pierna y pie
    for s in (1, -1):
        hom, codo, mano = np.array((s * 2.9, 6.0, 1.8)), np.array((s * 3.9, 3.4, 2.4)), np.array((s * 3.7, 1.0, 3.2))
        viga(out, hom, codo, 1.7, 1.8, P['cuerpo'], extra=0.3, semilla=20)
        viga(out, codo, mano, 1.3, 1.3, P['cuerpo'], extra=0.25, semilla=21)
        cubo(out, vr.T(*mano), -0.9, -1.0, -0.8, 1.8, 0.9, 1.9, P['cuerpo'], caras={'abajo': P['vientre']}, semilla=22)
        for j, dx in enumerate((-0.6, 0.0, 0.6)):
            p0 = mano + np.array((dx, -0.6, 1.0))
            bm.garra(out, p0, (dx * 0.3, 0.1, 1.0), (0, -1.0, 0.4), 0.7, 0.55, 0.3, P['hueso'], semilla=23 + j)
        cad, rod, tob = np.array((s * 2.5, 5.2, -6.0)), np.array((s * 3.5, 3.0, -4.2)), np.array((s * 3.3, 1.4, -6.6))
        viga(out, cad, rod, 1.8, 1.9, P['cuerpo'], extra=0.3, semilla=26)
        viga(out, rod, tob, 1.2, 1.2, P['cuerpo'], extra=0.2, semilla=27)
        viga(out, tob, tob + np.array((0, -1.1, 0.5)), 1.0, 1.0, P['cuerpo'], semilla=28)
        pie = tob + np.array((0, -1.2, 0.7))
        cubo(out, vr.T(*pie), -0.85, -0.25, -0.6, 1.7, 0.7, 1.8, P['cuerpo'], caras={'abajo': P['vientre']}, semilla=29)
        for j, dx in enumerate((-0.55, 0.0, 0.55)):
            bm.garra(out, pie + np.array((dx, 0.1, 1.1)), (dx * 0.3, 0.1, 1.0), (0, -1.0, 0.4), 0.55, 0.45, 0.26, P['hueso'], semilla=30 + j)
    # la cola, que se curva a un lado y acaba en puas
    ctrl = [(0, 5.2, -7.6), (0.3, 4.2, -10.4), (1.6, 3.0, -13.0), (4.0, 2.0, -14.8), (7.0, 2.0, -15.4), (9.6, 2.8, -14.6)]
    pts, marcos = cuello(out, ctrl, (1.5, 0.4), P, n=12, semilla=40, bandas=(k == 'C'))
    for i, M in enumerate(marcos[::2]):
        t = 2 * i / max(len(marcos) - 1, 1)
        pua(out, M @ vr.T(0, (1.5 + (0.4 - 1.5) * t) - 0.1, 0.3) @ vr.Rx(-35 * D), 0.18, 0.9 - 0.4 * t, P['hueso'], semilla=60 + i)
    Mfin = marcos[-1] @ vr.T(0, 0, float(np.linalg.norm(pts[-1] - pts[-2])))
    for j in range(3):
        pua(out, Mfin @ vr.Rz((j * 120) * D) @ vr.Rx(-55 * D), 0.18, 1.4, P['hueso'], semilla=70 + j)


# ======================================================================
#  LERNARA
# ======================================================================
def _cabeza_en(pts, yaw, escala):
    """El marco de la cabeza al final de un cuello: un poco por delante, mirando al frente
    y girada yaw grados hacia fuera."""
    d = np.array((math.sin(math.radians(yaw)), -0.2, math.cos(math.radians(yaw))))
    d /= np.linalg.norm(d)
    return em.marco(pts[-1] + d * 1.15 * escala, d) @ np.diag([escala, escala, escala, 1.0])


def lernara(variante='A', abre=40.0, semilla=1):
    V = VARIANTES[variante]
    P = pintores(V)
    k = V['clave']
    out = []
    cuerpo(out, V, P)
    cabezas = []
    if k == 'A':
        # tres cuellos en abanico: el del centro mas alto y mas gordo
        ctrl = [(0, 7.0, 3.0), (0, 9.4, 3.9), (0, 12.0, 4.0), (0, 14.4, 4.8), (0, 15.6, 6.4)]
        pts, _ = cuello(out, ctrl, (1.75, 1.2), P, n=9, semilla=100, collar=True)
        cabezas.append(_cabeza_en(pts, 0, 1.35))
        for s in (1, -1):
            ctrl = [(s * 2.0, 6.6, 2.8), (s * 3.4, 8.4, 3.5), (s * 5.1, 10.1, 3.6), (s * 6.4, 11.4, 4.4), (s * 7.0, 11.9, 5.8)]
            pts, _ = cuello(out, ctrl, (1.45, 1.0), P, n=8, semilla=120, collar=True)
            cabezas.append(_cabeza_en(pts, s * 18, 1.05))
        corona = 'cuernos'
    elif k == 'B':
        # cinco cuellos en abanico, unidos por la membrana: se abren como una capucha
        filas = []
        for i, phi in enumerate((-62, -31, 0, 31, 62)):
            f = math.radians(phi)
            bx, by = math.sin(f) * 1.9, 6.9 + math.cos(f) * 0.4
            tx, ty = math.sin(f) * 8.8, 6.0 + math.cos(f) * (9.2 if i == 2 else 8.4)
            ctrl = [(bx, by, 2.9), (bx + 0.36 * (tx - bx), by + 0.36 * (ty - by), 3.5), (bx + 0.72 * (tx - bx), by + 0.72 * (ty - by), 3.9),
                    (tx, ty, 4.5), (tx * 1.02, ty + 0.2, 5.8)]
            centro = i == 2
            pts, _ = cuello(out, ctrl, (1.45, 1.0) if centro else (1.2, 0.85), P, n=9, semilla=100 + 10 * i, collar=True)
            filas.append(pts)
            cabezas.append(_cabeza_en(pts, phi * 0.35, 1.2 if centro else (0.92 if abs(phi) < 40 else 0.8)))
        for a, b in zip(filas, filas[1:]):              # la membrana entre cada dos cuellos, hasta las tres cuartas partes
            n = int(len(a) * 0.68)
            for j in range(n - 1):
                libre = j == n - 2
                lamina(out, (a[j], b[j], b[j + 1], a[j + 1]), P['membrana' if libre else 'membrana_lisa'],
                       float(np.linalg.norm(b[j + 1] - a[j + 1])), float(np.linalg.norm(a[j + 1] - a[j])), 140 + j)
        corona = 'cresta'
    else:
        # dos cuellos trenzados como una soga, que arriba se abren en dos
        filas = []
        for s in (1, -1):
            ctrl = []
            for j in range(7):
                t = j / 6
                th = TAU * 1.25 * t + (0 if s > 0 else math.pi)
                ax = np.array((0, 6.8 + 6.4 * t, 2.9 + 1.4 * t))
                ctrl.append(tuple(ax + np.array((math.cos(th) * 1.2, 0, math.sin(th) * 1.2))))
            ctrl += [(s * 2.4, 14.6, 4.9), (s * 3.9, 15.6, 6.0)]
            pts, _ = cuello(out, ctrl, (1.15, 0.95), P, n=14, semilla=100 + (s > 0) * 20, collar=True, bandas=True)
            filas.append(pts)
            cabezas.append(_cabeza_en(pts, s * 24, 1.25))
        corona = 'capucha'
    for Mh in cabezas:
        cabeza(out, Mh, V, P, abre, corona)
    return out, {'cabezas': cabezas}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

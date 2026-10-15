"""
La Tarasca y sus formas (14-10-2026). Juan, tras el Minotauro: «corrige esto y haz otro monstruo».
Version 2, el mismo dia: «no me gusta su diseno, siento que es muy robusto»; ahora es esbelta.

La Tarasca de la leyenda (la de las procesiones del Corpus): cabeza de leon, caparazon con puas, seis patas y
una cola de escorpion. Con la receta de la guia: la cabeza manda, grande, mirando a camara y enmarcada por la
melena (mechones finos echados hacia atras), con las fauces abiertas que arden por dentro con un solo neon en
escalones (los dientes dibujados en hojas, cuatro colmillos arriba y dos abajo, el nucleo al fondo de la
garganta). El cuerpo es oscuro y esbelto: un tronco estrecho con cintura, el caparazon en siete placas que se
montan unas sobre otras (antes era una cupula de 18 bloques de ancho; ahora 11), seis patas largas de felino,
de puntillas, el cuello en S y la cola de escorpion larga y fina, en anillos. Todo de cajas, con texturas
limpias (escamas en U, el caparazon en bandas, puas de hueso en escalones).

Las tres formas cambian la silueta:

    A  del Rodano   la clasica: al acecho sobre sus seis patas, con el cuello alzado y la cola de escorpion
                    arqueada detras; neon lima
    B  Alzada       de pie sobre las dos patas de atras, con las otras cuatro en alto y las garras abiertas y
                    la cola de puntal; se le ve el peto en bandas; neon brasa
    C  Erizada      agazapada, con las placas erizadas de puas largas como un erizo y el aguijon arqueado
                    por encima de la cabeza; la melena de puas; neon violeta
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _manchas, _degradado, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.72
CABEZA = 1.55

VARIANTES = {
    'A': dict(
        clave='A', nombre='la Tarasca del Ródano', corto='rodano',
        piel=_r('0e120c', '182016', '222c1e', '2e3a28', '3e4c36'),
        caparazon=_r('120c08', '1e150e', '2a1e14', '3a2a1c', '4e3a28'),
        vientre=_r('3a2e1a', '5a4828', '7a6436', '9a8248', 'c0a660'),
        pua=_r('5a5040', '8a7e66', 'b8aa8c', 'dcd0b2', 'f6eedc'),
        melena=_r('1e0e08', '341a0e', '4e2614', '6c3a1e', '8e5028'),
        garra=_r('0a0808', '161212', '241e1c', '342c28', '4a3e38'),
        dientes=_r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2'),
        neon=('f4ffd8', 'b4ff2a', '3a6a04'),
    ),
    'B': dict(
        clave='B', nombre='la Tarasca Alzada', corto='alzada',
        piel=_r('140c0a', '221412', '301c18', '422620', '5a342a'),
        caparazon=_r('0c0a0a', '161212', '201a1a', '2c2424', '3c3232'),
        vientre=_r('3a1a0c', '5a2a12', '7a3a18', 'a05020', 'c86a2a'),
        pua=_r('4a3e34', '6e6052', '94846e', 'b8a88e', 'd8ccb2'),
        melena=_r('2a0a04', '4a1206', '6e1e08', '9a300c', 'c84a14'),
        garra=_r('0a0808', '161212', '241e1c', '342c28', '4a3e38'),
        dientes=_r('8a7a6e', 'b8a898', 'dcccba', 'f2e6d8', 'fffaf2'),
        neon=('fff0d8', 'ff6a1a', '6a1a02'),
    ),
    'C': dict(
        clave='C', nombre='la Tarasca Erizada', corto='erizada',
        piel=_r('0e0a12', '18121e', '221a2a', '2e2238', '3e2e4a'),
        caparazon=_r('0c0a10', '16121c', '201a28', '2c2236', '3a2e46'),
        vientre=_r('2a1e34', '3e2c4c', '564066', '70548a', '9070b0'),
        pua=_r('4a4250', '74687e', 'a094aa', 'c8bcd2', 'eee6f6'),
        melena=_r('100a16', '1c1226', '2a1a38', '3a244e', '4e3068'),
        garra=_r('0a080c', '161218', '221c26', '322a36', '463a4c'),
        dientes=_r('8a8090', 'b8aebe', 'dcd4e2', 'f2ecf6', 'fffcff'),
        neon=('f8e0ff', 'c44aff', '4a0a6a'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'tar%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def piel(tw, th, cara, s):
        """La piel: escamas en U al tresbolillo, con el canto claro de cada una."""
        ys, xs = np.mgrid[0:th, 0:tw]
        fila = ys // 3
        x = (xs + (fila % 2) * 2) % 4
        idx = np.full((th, tw), 2)
        idx = np.where((ys % 3) == 2, 1, idx)
        idx = np.where(((ys % 3) == 0) & (x == 1), 3, idx)
        idx = np.where(x == 3, np.minimum(idx, 1), idx)
        return _imagen(_bisel(idx, 1, 1), V['piel']), None
    reg('piel', piel)

    def caparazon(tw, th, cara, s):
        """El caparazon: bandas anchas con el canto de abajo oscuro y el de arriba claro, y manchas grandes
        de borde limpio un tono mas claras."""
        idx = _manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
        idx = np.array([1, 2, 2, 3, 3])[idx]
        if cara not in ('arriba', 'abajo'):
            ys = np.arange(th)[:, None] + np.zeros((1, tw), int)
            idx = np.where((ys % 6) == 5, 1, np.where((ys % 6) == 0, np.maximum(idx, 3), idx))
        return _imagen(_bisel(idx, 1, 1), V['caparazon']), None
    reg('caparazon', caparazon)

    def vientre(tw, th, cara, s):
        """El vientre (el peto de la tortuga): placas en bandas de traves con su sombra."""
        largo_x = tw >= th
        n = th if largo_x else tw
        a = np.arange(n)
        fila = np.where((a % 5) == 0, 1, np.where((a % 5) == 1, 3, 2))
        idx = np.tile(fila[:, None], (1, tw)) if largo_x else np.tile(fila[None, :], (th, 1))
        return _imagen(_bisel(idx, 1, 1), V['vientre']), None
    reg('vientre', vientre)

    def pua(tw, th, cara, s):
        """Las puas: hueso con una raya clara a lo largo."""
        idx = np.full((th, tw), 2)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 1
        return _imagen(idx, V['pua']), None
    reg('pua', pua)
    reg('melena', lambda tw, th, c, s: (jm.hebras(tw, th, s, V['melena'], 2, 4), None))
    reg('garra', jm.liso(V['garra'], 2, 2, 1))
    reg('nariz', jm.liso(V['garra'], 1, 1, 1))

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def boca(tw, th, cara, s):
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
        return t, _emis(t, dd >= 0.2, 230)
    reg('boca', boca)

    def nucleo(tw, th, cara, s):
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

    def _hojas_de_dientes(tw, th, rampa, colgando):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in rampa]
        n = max(1, (tw + 1) // 5)
        x0 = (tw - (n * 5 - 1)) // 2
        for i in range(n):
            x = x0 + i * 5
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.68)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)
                if f > 0.85:
                    pix = ((x + 1, c[4]),)
                elif f > 0.6:
                    pix = ((x + 1, c[4]), (x + 2, c[3]))
                else:
                    pix = ((x, c[2]), (x + 1, c[4]), (x + 2, c[3]), (x + 3, c[1]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
            y = 0 if colgando else th - 1
            for xx in range(max(x, 0), min(x + 4, tw)):
                t[y, xx] = c[1]
        return t, None
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, V['dientes'], True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, V['dientes'], False))

    def colmillo(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 1
        return _imagen(idx, V['dientes']), None
    reg('colmillo', colmillo)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    """Una fila de dientes en hojas a lo largo de una linea quebrada en el plano de la mandibula."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado, h = float(np.linalg.norm(B - A)), float(np.linalg.norm(A2 - A))
        if alto < 0:
            lamina(out, (A2, B2, B, A), pintor, lado, h, semilla + j)
        else:
            lamina(out, (A, B, B2, A2), pintor, lado, h, semilla + j)


def pua(out, p, d, r, h, pintor, semilla=0):
    """Una pua en tres escalones que sale de p hacia d."""
    M = em.marco(np.asarray(p, float), np.asarray(d, float))
    caja(out, M, -r, r, -r, r, -0.4, h * 0.45, pintor, semilla=semilla)
    caja(out, M, -r * 0.64, r * 0.64, -r * 0.64, r * 0.64, h * 0.4, h * 0.76, pintor, semilla=semilla + 1)
    caja(out, M, -r * 0.32, r * 0.32, -r * 0.32, r * 0.32, h * 0.72, h, pintor, semilla=semilla + 2)


def cabeza(out, Mh, P, abre=34.0, puas=False):
    """La cabeza de leon, con el morro hacia +z: el craneo ancho, el ceno en angulo y los ojos encendidos
    bajo el; el morro ancho y corto con la nariz; las fauces abiertas (el paladar encendido, los dientes en
    hojas, cuatro colmillos arriba y dos abajo, el suelo de la boca encendido y el nucleo al fondo); las
    orejas; y la melena que la enmarca en dos coronas de mechones (en la Erizada, de puas de hueso)."""
    piel = P['piel']
    caja(out, Mh, -4.6, 4.6, 0.0, 6.4, -3.6, 3.0, piel, semilla=1)                                     # el craneo
    caja(out, Mh, -4.8, 4.8, 4.0, 5.4, 2.4, 4.0, piel, semilla=2)                                     # el ceno
    for s in (1, -1):
        x0, x1 = sorted((s * 1.4, s * 3.9))
        caja(out, Mh, x0, x1, 2.7, 3.8, 2.9, 3.25, P['ojo'], semilla=3)                                # los ojos
        Mc = Mh @ vr.T(s * 2.6, 4.0, 3.35) @ vr.Rz(s * 15 * D)
        caja(out, Mc, -2.0, 2.0, -0.25, 0.7, -0.5, 0.8, piel, semilla=4)
        Mo = Mh @ vr.T(s * 3.6, 6.0, -0.8) @ vr.Rz(-s * 18 * D)                                        # las orejas
        caja(out, Mo, -1.0, 1.0, 0.0, 1.8, -0.6, 0.6, P['melena'], semilla=5)
    bm.cubo(out, Mh, -3.6, 0.8, 2.9, 7.2, 3.2, 4.9, piel, caras={'abajo': P['fauces']}, semilla=6)     # el morro
    caja(out, Mh, -1.8, 1.8, 3.8, 4.6, 3.2, 7.4, piel, semilla=7)
    caja(out, Mh, -2.2, 2.2, 2.6, 4.1, 7.6, 8.4, P['nariz'], semilla=8)
    hilera(out, Mh, [(-3.35, 3.2), (-3.35, 7.55), (3.35, 7.55), (3.35, 3.2)], 0.85, -1.1, P['dientes_arriba'], semilla=9)
    for x, z, l in ((2.7, 6.8, 2.9), (-2.7, 6.8, 2.9), (1.0, 7.3, 1.8), (-1.0, 7.3, 1.8)):                # los colmillos
        M = Mh @ vr.T(x, 0.85, z)
        caja(out, M, -0.42, 0.42, -l * 0.7, 0.0, -0.36, 0.36, P['colmillo'], semilla=10)
        caja(out, M, -0.25, 0.25, -l, -l * 0.65, -0.22, 0.22, P['colmillo'], semilla=11)
    caja(out, Mh, -2.4, 2.4, -1.8, 0.85, 2.55, 2.9, P['nucleo'], semilla=12)                          # el nucleo
    Mj = Mh @ vr.T(0, 0.8, 1.0) @ vr.Rx(abre * D)                                                     # la mandibula
    bm.cubo(out, Mj, -3.3, -2.0, 0.0, 6.6, 2.0, 7.0, piel, caras={'arriba': P['boca']}, semilla=13)
    hilera(out, Mj, [(-3.05, 1.0), (-3.05, 6.75), (3.05, 6.75), (3.05, 1.0)], 0.0, 1.0, P['dientes_abajo'], semilla=14)
    for s in (1, -1):
        M = Mj @ vr.T(s * 2.6, 0.0, 6.0) @ vr.Rz(-s * 8 * D)
        caja(out, M, -0.45, 0.45, 0.0, 2.6, -0.4, 0.4, P['colmillo'], semilla=15)
        caja(out, M, -0.28, 0.28, 2.5, 3.4, -0.25, 0.25, P['colmillo'], semilla=16)
    # la melena: dos coronas de mechones que salen del contorno de la cara hacia fuera (y algo hacia atras)
    centro = np.array((0.0, 3.0, -0.6))
    for corona, (n, largo, ancho, z, fase) in enumerate(((16, 4.4, 2.1, -0.4, 0.0), (14, 6.4, 2.4, -1.8, 0.5))):
        for j in range(n):
            a = (j + fase) * TAU / n
            d = np.array((math.cos(a), math.sin(a) * 0.95, -0.6 - 0.25 * corona))
            base = centro + np.array((math.cos(a) * 4.4, math.sin(a) * 3.9, z))
            if puas:
                pua(out, pt(Mh, base), pt(Mh, base + d) - pt(Mh, base), ancho * 0.32 * CABEZA, largo * 1.25 * CABEZA,
                    P['pua'], semilla=20 + j % 3)
            else:
                M = em.marco(pt(Mh, base), pt(Mh, base + d) - pt(Mh, base))
                g = ancho * CABEZA * 0.5
                caja(out, M, -g, g, -g * 0.7, g * 0.7, -0.5, largo * CABEZA * 0.7, P['melena'], semilla=20 + j % 3)
                caja(out, M, -g * 0.6, g * 0.6, -g * 0.45, g * 0.45, largo * CABEZA * 0.68, largo * CABEZA, P['melena'], semilla=23)
    return pt(Mh, (0.0, 0.4, 5.0))


def pata(out, P, cad, pie, codo, gruesa=1.0, alzada=False, semilla=0):
    """Una pata larga y fina, de felino: el muslo hasta el codo (o la rodilla), la pierna hasta el tobillo,
    que va alto, el metatarso hasta la pata, una placa del caparazon en el codo y la pata estrecha con cuatro
    garras. codo es hacia donde sale la articulacion de en medio (atras en las de delante, adelante en las de
    atras); el tobillo sale al reves. Alzada, la pata no pisa: las garras apuntan a donde va la pata."""
    cad, pie, codo = (np.asarray(v, float) for v in (cad, pie, codo))
    codo = codo / np.linalg.norm(codo)
    L = float(np.linalg.norm(pie - cad))
    plano = np.array((codo[0], 0.0, codo[2]))
    rod = cad + (pie - cad) * 0.42 + codo * L * 0.2
    if alzada:
        tob = cad + (pie - cad) * 0.8 - codo * L * 0.06
    else:
        tob = pie + np.array((0.0, min(4.4, L * 0.27), 0.0)) - plano * L * 0.1
    fin = pie + np.array((0.0, 0.0 if alzada else 0.8, 0.0))
    caja(out, vr.T(*cad), -2.5 * gruesa, 2.5 * gruesa, -2.4 * gruesa, 2.4 * gruesa, -2.5 * gruesa, 2.5 * gruesa,
         P['piel'], semilla=semilla)                                                                    # el hombro
    for a, b, g in ((cad, rod, 2.3 * gruesa), (rod, tob, 1.65 * gruesa), (tob, fin, 1.3 * gruesa)):
        M = em.marco(a, b - a)
        Lg = float(np.linalg.norm(b - a))
        caja(out, M, -g, g, -g, g, -0.5, Lg + 0.5, P['piel'], semilla=semilla + 1)
    M = em.marco(rod, tob - rod)
    caja(out, M, -2.15 * gruesa, 2.15 * gruesa, -2.15 * gruesa, 2.15 * gruesa, -1.1, 1.3, P['caparazon'], semilla=semilla + 2)
    if alzada:
        Mp = em.marco(pie, pie - tob, up=(0.0, 1.0, 0.0))
    else:
        adelante = np.array((plano[0] * 0.25, 0.0, 1.0))
        Mp = em.marco(pie, adelante, up=(0.0, 1.0, 0.0))
    caja(out, Mp, -1.8, 1.8, -0.8, 1.0, -1.6, 2.3, P['piel'], semilla=semilla + 3)                   # la pata
    for j in range(4):
        x = (j - 1.5) * 1.05
        Mu = Mp @ vr.T(x, -0.3, 1.9) @ vr.Ry(x * 9 * D) @ vr.Rx(28 * D)
        caja(out, Mu, -0.3, 0.3, -0.36, 0.28, 0.0, 1.4, P['garra'], semilla=semilla + 4)
        caja(out, Mu @ vr.T(0, 0, 1.3) @ vr.Rx(32 * D), -0.2, 0.2, -0.26, 0.18, 0.0, 1.0, P['garra'], semilla=semilla + 5)


def _eje(Y):
    """El eje del tronco: de las caderas (atras) al pecho (delante), con la cintura un poco hundida."""
    return [np.array(c, float) for c in ((0.0, Y + 0.8, -19.0), (0.0, Y, -9.0), (0.0, Y + 0.3, 1.0), (0.0, Y + 1.6, 10.5))]


PERFIL_TRONCO = ((0.0, 4.2), (0.22, 4.6), (0.5, 3.7), (0.8, 4.9), (1.0, 4.2))


def _en_eje(Y, z):
    """La altura del eje y el radio del tronco a la altura z."""
    zs = [-19.0, -9.0, 1.0, 10.5]
    ys = [Y + 0.8, Y, Y + 0.3, Y + 1.6]
    t = (z + 19.0) / 29.5
    return float(np.interp(z, zs, ys)), float(np.interp(t, [a for a, _ in PERFIL_TRONCO], [b for _, b in PERFIL_TRONCO]))


def tronco(out, P, Y, largas=False, semilla=0):
    """El cuerpo esbelto: el tronco de escamas que se estrecha en la cintura, el peto en bandas por debajo y,
    encima, el caparazon en siete placas que se montan unas sobre otras (cada una con el canto de atras
    levantado, como escamas), con una fila de puas en la cresta y otra a cada lado. En la Erizada las puas
    son largas y hay una fila mas a cada lado, como un erizo."""
    pts, rs, ts = jm.a_lo_largo(_eje(Y), 10, PERFIL_TRONCO)
    jm.tubo(out, pts, rs, [P['piel']] * (len(pts) - 1), semilla=semilla)
    for j in range(1, len(pts) - 2):                                                                 # el peto
        a, b = pts[j], pts[j + 1]
        r = (rs[j] + rs[j + 1]) / 2
        M = em.marco(a, b - a)
        caja(out, M, -r * 0.6, r * 0.6, -r - 0.3, -r + 1.3, -0.3, float(np.linalg.norm(b - a)) + 0.3, P['vientre'], semilla=semilla + 1)
    cap = P['caparazon']
    for k in range(7):
        z = -17.0 + k * 4.0
        yc, r = _en_eje(Y, z)
        M = vr.T(0.0, yc, z) @ vr.Rx(7 * D)
        caja(out, M, -(r + 2.0), r + 2.0, r * 0.1, r + 0.9, -2.7, 2.7, cap, semilla=semilla + 2 + k % 3)
        caja(out, M, -(r * 0.75 + 1.0), r * 0.75 + 1.0, r + 0.9, r + 1.9, -2.4, 2.4, cap, semilla=semilla + 5)
        caja(out, M, -1.5, 1.5, r + 1.9, r + 2.6, -2.0, 2.0, cap, semilla=semilla + 6)
        h = 8.0 if largas else 3.0
        pua(out, pt(M, (0.0, r + 2.3, -0.4)), (M[:3, :3] @ np.array((0.0, 1.0, -0.4))), 0.85, h * (0.8 + 0.4 * math.sin(k / 6 * math.pi)),
            P['pua'], semilla=semilla + 10 + k % 3)
        for s in (1, -1):
            pua(out, pt(M, (s * (r + 1.6), r * 0.5, 0.0)), (M[:3, :3] @ np.array((s * 1.0, 0.45, -0.3))), 0.6,
                (6.0 if largas else 2.0), P['pua'], semilla=semilla + 13)
            if largas:
                pua(out, pt(M, (s * (r * 0.7 + 0.2), r + 1.6, 0.0)), (M[:3, :3] @ np.array((s * 0.7, 1.0, -0.35))), 0.75,
                    7.0 * (0.8 + 0.3 * math.sin(k / 6 * math.pi)), P['pua'], semilla=semilla + 14)


def cola(out, P, ctrl, semilla=0):
    """La cola de escorpion, larga y fina: segmentos de escamas que se afinan, con una cresta de puas
    pequenas, el bulbo y el aguijon curvo que acaba encendido."""
    pts, rs, ts = jm.a_lo_largo(ctrl, 14, ((0.0, 2.6), (0.4, 1.9), (0.8, 1.3), (1.0, 1.1)))
    jm.tubo(out, pts, rs, [P['caparazon'] if j % 2 else P['piel'] for j in range(len(pts) - 1)], semilla=semilla)   # en anillos
    for j in range(1, len(pts) - 1, 2):                                                               # la cresta
        d = pts[j + 1] - pts[j - 1]
        lado = np.cross(d, (1.0, 0.0, 0.0))
        arriba = lado / max(np.linalg.norm(lado), 1e-6)
        if arriba[1] < 0:
            arriba = -arriba
        pua(out, pts[j] + arriba * rs[j] * 0.8, arriba, 0.5, 1.5, P['pua'], semilla=semilla + 5)
    d = pts[-1] - pts[-2]
    d = d / np.linalg.norm(d)
    M = em.marco(pts[-1], d)
    caja(out, M, -2.4, 2.4, -2.4, 2.4, -0.5, 3.8, P['caparazon'], semilla=semilla + 6)                # el bulbo
    caja(out, M, -1.7, 1.7, -1.7, 1.7, 3.6, 4.6, P['piel'], semilla=semilla + 8)
    lado = np.cross(d, (1.0, 0.0, 0.0))
    if np.linalg.norm(lado) < 1e-3:
        lado = np.array((0.0, 1.0, 0.0))
    lado = lado / np.linalg.norm(lado)
    if lado[1] > 0:                                                    # el aguijon se curva hacia abajo
        lado = -lado
    curva = [pts[-1] + d * 5.2, pts[-1] + d * 8.0 + lado * 1.3, pts[-1] + d * 9.6 + lado * 3.9, pts[-1] + d * 9.8 + lado * 5.6]
    jm.tubo(out, [pts[-1] + d * 4.4] + curva, [1.25, 0.95, 0.7, 0.45, 0.25], [P['garra'], P['garra'], P['ojo'], P['ojo']], semilla=semilla + 7)
    return curva[-1]


# ======================================================================
#  LA TARASCA
# ======================================================================
# las patas: (fila, z de la cadera, hacia donde sale el codo, grosor); fila 1 delante, 0 en medio, -1 detras
PATAS = [(1, 6.5, (0.35, 0.0, -1.0), 1.0), (0, -3.5, (0.6, 0.0, -0.6), 0.92), (-1, -14.0, (0.35, 0.0, 1.0), 1.15)]


def tarasca(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    Y = {'A': 16.0, 'B': 16.0, 'C': 11.5}[tipo]
    cuerpo, patas = [], []
    try:
        tronco(cuerpo, P, Y, largas=(tipo == 'C'), semilla=100)
        # el cuello en S, que sale del pecho; la cabeza se engancha por la nuca baja
        if tipo == 'C':                                                  # bajo y hacia delante
            ctrl_cuello = [(0.0, Y + 1.5, 8.0), (0.0, Y + 3.0, 13.0), (0.0, Y + 4.2, 17.0), (0.0, Y + 5.0, 20.0)]
            inclina = 4
        elif tipo == 'B':                                                # hacia delante del cuerpo, que se alza
            ctrl_cuello = [(0.0, Y + 1.5, 8.0), (0.0, Y + 4.5, 13.0), (0.0, Y + 5.0, 18.0), (0.0, Y + 3.0, 21.5)]
            inclina = 66
        else:                                                            # alzado
            ctrl_cuello = [(0.0, Y + 1.5, 8.0), (0.0, Y + 6.0, 13.5), (0.0, Y + 11.0, 14.5), (0.0, Y + 14.5, 17.5)]
            inclina = 10
        ctrl_cuello = [np.array(c, float) for c in ctrl_cuello]
        pts, rs, ts = jm.a_lo_largo(ctrl_cuello, 8, ((0.0, 3.8), (0.5, 3.0), (1.0, 2.9)))
        jm.tubo(cuerpo, pts, rs, [P['piel']] * (len(pts) - 1), semilla=120)
        Mh = vr.T(*ctrl_cuello[-1]) @ vr.Rx(inclina * D) @ np.diag([CABEZA] * 3 + [1.0]) @ vr.T(0.0, -2.2, 3.0)
        bm.PPB = PPB / CABEZA
        boca = cabeza(cuerpo, Mh, P, abre=34.0 if tipo != 'B' else 40.0, puas=(tipo == 'C'))
        bm.PPB = PPB
        # el cuerpo entero, segun la forma
        if tipo == 'B':                                                  # alzada sobre las patas de atras
            Mc = vr.T(0.0, Y, -14.0) @ vr.Rx(-58 * D) @ vr.T(0.0, -Y, 14.0)
        else:
            Mc = np.eye(4)
        # la cola de escorpion
        if tipo == 'C':                                                  # arqueada por encima de la cabeza
            ctrl_cola = [(0.0, Y + 0.8, -19.0), (0.0, Y + 6.0, -27.0), (0.0, Y + 19.0, -29.0), (0.0, Y + 29.0, -20.0),
                         (0.0, Y + 31.0, -6.0), (0.0, Y + 28.0, 5.0)]
        elif tipo == 'B':                                                # apoyada en el suelo, de puntal
            base = pt(Mc, (0.0, Y + 0.8, -19.0))
            ctrl_cola = [tuple(base), tuple(base + np.array((0.0, -6.0, -4.0))), (2.0, 2.6, -28.0), (5.0, 2.4, -35.0),
                         (8.0, 3.4, -40.0), (10.0, 8.0, -42.0)]
        else:                                                            # arqueada detras, el aguijon sobre el lomo
            ctrl_cola = [(0.0, Y + 0.8, -19.0), (0.0, Y + 3.0, -27.0), (0.0, Y + 10.0, -33.0), (0.0, Y + 19.0, -33.0),
                         (0.0, Y + 25.0, -27.0), (0.0, Y + 26.0, -19.0)]
        cola_qs = []
        cola(cola_qs, P, [np.array(c, float) for c in ctrl_cola], semilla=140)
        out = qm.transformar(cuerpo, Mc) + (cola_qs if tipo == 'B' else qm.transformar(cola_qs, Mc))
        boca = pt(Mc, boca)
        # las seis patas, del costado del tronco al suelo
        for fila, z, codo, gruesa in PATAS:
            yc, r = _en_eje(Y, z)
            for s in (1, -1):
                cad = pt(Mc, (s * r * 0.75, yc - r * 0.35, z))
                cd = np.array((s * codo[0], codo[1], codo[2]))
                alzada = False
                if tipo == 'B' and fila == 1:                             # las de delante, en alto con las garras abiertas
                    pie = cad + np.array((s * 5.0, 7.0, 9.0))
                    cd, alzada = np.array((s * 0.6, -1.0, 0.0)), True
                elif tipo == 'B' and fila == 0:                           # las de en medio, a media altura
                    pie = cad + np.array((s * 8.0, -1.0, 8.0))
                    cd, alzada = np.array((s * 0.5, -1.0, -0.2)), True
                elif tipo == 'C':                                         # agazapada: las patas abiertas
                    pie = np.array((cad[0] + s * 8.5, 0.8, cad[2] + fila * 3.0))
                    cd = cd + np.array((s * 0.5, 0.3, 0.0))
                else:
                    pie = np.array((cad[0] + s * 3.5, 0.8, cad[2] + fila * 2.0 + (1.0 if tipo == 'A' else 0.0)))
                pata(patas, P, cad, pie, cd, gruesa=gruesa, alzada=alzada, semilla=160 + (fila + 1) * 6)
        out += patas
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

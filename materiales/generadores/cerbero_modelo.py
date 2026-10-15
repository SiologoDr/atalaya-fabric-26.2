"""
Cerbero y sus formas (14-10-2026). Juan, al guardar el Minotauro y pedir que se rehiciera la Tarasca:
«creame otro boss».

Del mismo bestiario griego que la Gorgona y el Minotauro: el perro del Hades que guarda la puerta, una forma
de cuerpo que no estaba en las fichas (un perro de presa, de cuatro patas largas). No es un perro agrandado:
tiene varias cabezas, la crin de serpientes y la cola que es una serpiente con su propia boca. Con la receta
de la guia (materiales/fichas/COMO_HACEMOS_LOS_MONSTRUOS.md): las cabezas mandan, grandes y mirando a camara,
con las fauces abiertas que arden por dentro con un solo neon en escalones (los dientes dibujados en hojas,
los colmillos y el nucleo al fondo de la garganta) y los ojos encendidos bajo un ceno en angulo; las
enmarcan las orejas en punta, la gola de pelo y el collar de pinchos. El cuerpo es oscuro y enjuto: el pecho
hondo, la cintura recogida y las patas largas, de puntillas. Todo de cajas, con texturas limpias (manchas
grandes de borde limpio, escamas en U, remaches de 2 x 2), en pixeles de piel y escalado a la escena.

Las tres formas cambian la silueta:

    A  Cerbero, el Guardian   tres cabezas abiertas en abanico, plantado sobre las cuatro patas; la crin de
                              serpientes por el lomo; la cola-serpiente en alto; collares de bronce; azufre
    B  Ortro, el de Gerion    el hermano de dos cabezas: mas largo y flaco, agazapado para saltar (el pecho
                              bajo, la grupa alta), con las orejas largas y la cresta de pelo; fucsia
    C  Cerbero Encadenado     el que saco Heracles del Hades: sentado sobre los cuartos traseros, muy alto,
                              con las cadenas rotas colgando de los collares y la cola enroscada; azul de alma
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _manchas, _remaches, _degradado, lamina, cadena
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.72
CABEZA = 1.4                                     # las cabezas mandan: se hacen sin escala y se agrandan

DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')
VARIANTES = {
    'A': dict(
        clave='A', nombre='Cerbero, el Guardian', corto='guardian',
        piel=_r('0a0807', '141010', '1e1816', '2a221e', '3a302a'),
        pelaje=_r('0c0806', '181009', '24180e', '342214', '4a301c'),
        serpiente=_r('10100a', '1e1e12', '30301c', '464428', '5e5c36'),
        metal=_r('3a2410', '6a4420', '9a6a34', 'c8964c', 'f0c878'),
        garra=_r('0a0808', '141010', '1e1818', '2a2222', '3a3030'),
        dientes=DIENTES, neon=('fffbe0', 'ffd21a', '6a4c02'),
    ),
    'B': dict(
        clave='B', nombre='Ortro, el Perro de Gerion', corto='ortro',
        piel=_r('100606', '1c0c0c', '2a1414', '3a1c1c', '4e2828'),
        pelaje=_r('120606', '200c0a', '30140f', '441e16', '5c2a20'),
        serpiente=_r('140810', '24101e', '361a2c', '4c263e', '663454'),
        metal=_r('16161a', '262630', '3a3a46', '56566a', '7e7e94'),
        garra=_r('0a0606', '140c0c', '1e1414', '2a1c1c', '3a2828'),
        dientes=DIENTES, neon=('ffe2f2', 'ff2a9a', '6a0236'),
    ),
    'C': dict(
        clave='C', nombre='Cerbero Encadenado', corto='encadenado',
        piel=_r('0a0c10', '12161c', '1c2028', '282e38', '384050'),
        pelaje=_r('0a0c10', '141820', '1e242e', '2c3440', '3e4858'),
        serpiente=_r('0e1214', '1a2024', '283034', '384448', '4c5a5e'),
        metal=_r('1a1c20', '2c3036', '444a52', '646c76', '9aa4ae'),
        garra=_r('08090c', '101216', '181c22', '22282e', '30363e'),
        dientes=DIENTES, neon=('e2f6ff', '3ab8ff', '043a6a'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'cer%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def piel(tw, th, cara, s):
        """El pelo corto del cuerpo: oscuro, con manchas grandes de borde limpio un tono mas claras."""
        idx = _manchas(tw, th, s, celda=7.0, umbral=0.6, alto=0.8)
        idx = np.array([1, 2, 2, 3, 3])[idx]
        return _imagen(_bisel(idx, 1, 1), V['piel']), None
    reg('piel', piel)
    reg('pelaje', lambda tw, th, c, s: (jm.hebras(tw, th, s, V['pelaje'], 2, 4), None))

    def serpiente(tw, th, cara, s):
        """Las escamas de las serpientes: en U al tresbolillo, con el canto claro de cada una."""
        ys, xs = np.mgrid[0:th, 0:tw]
        fila = ys // 3
        x = (xs + (fila % 2) * 2) % 4
        idx = np.full((th, tw), 2)
        idx = np.where((ys % 3) == 2, 1, idx)
        idx = np.where(((ys % 3) == 0) & (x == 1), 3, idx)
        idx = np.where(x == 3, np.minimum(idx, 1), idx)
        return _imagen(_bisel(idx, 1, 1), V['serpiente']), None
    reg('serpiente', serpiente)

    def metal(tw, th, cara, s):
        """El collar: placa con su canto claro y una fila de remaches de 2 x 2."""
        idx = _remaches(np.full((th, tw), 2), cara, paso=5) if min(tw, th) >= 4 else np.full((th, tw), 2)
        return _imagen(_bisel(idx, 2, 1), V['metal']), None
    reg('metal', metal)
    reg('metal_liso', jm.liso(V['metal'], 3, 1, 1))

    def pincho(tw, th, cara, s):
        """Los pinchos del collar: el metal con una raya clara a lo largo."""
        idx = np.full((th, tw), 2)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 1
        return _imagen(idx, V['metal']), None
    reg('pincho', pincho)
    reg('garra', jm.liso(V['garra'], 2, 2, 1))
    reg('nariz', jm.liso(V['garra'], 1, 1, 1))
    reg('boca_serpiente', jm.liso(_r('1a0406', '2e080c', '480e14', '641820', '82242c'), 1, 0, 0))

    def fauces(tw, th, cara, s):
        """El paladar: escalones de luz (blanco al fondo, el neon, la sombra) con sus estrias."""
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


def cabeza(out, Mh, P, abre=36.0, orejas=1.0):
    """La cabeza de perro de presa, con el hocico hacia +z: el craneo con la coronilla en escalon, el ceno en
    angulo y los ojos encendidos bajo el; las orejas en punta, en tres escalones; la gola de pelo en las
    mejillas; el hocico largo con el caballete y la trufa; las fauces abiertas (el paladar encendido, los
    dientes en hojas, dos colmillos arriba y dos abajo, el suelo de la boca encendido y el nucleo al fondo); y
    la barba de pelo bajo la mandibula."""
    piel, pelo = P['piel'], P['pelaje']
    caja(out, Mh, -3.6, 3.6, 0.0, 5.6, -3.6, 2.4, piel, semilla=1)                                    # el craneo
    caja(out, Mh, -2.9, 2.9, 5.4, 6.3, -3.0, 1.4, piel, semilla=2)
    for s in (1, -1):
        x0, x1 = sorted((s * 1.75, s * 3.35))
        caja(out, Mh, x0, x1, 3.75, 4.45, 2.35, 2.62, P['ojo'], semilla=3)                            # los ojos
        Mc = Mh @ vr.T(s * 2.45, 4.75, 2.6) @ vr.Rz(s * 17 * D)                                       # el ceno
        caja(out, Mc, -1.75, 1.75, -0.3, 0.6, -0.6, 0.7, piel, semilla=4)
        Mo = Mh @ vr.T(s * 2.35, 5.6, -1.4) @ vr.Rz(-s * 16 * D) @ vr.Rx(-24 * D)                     # las orejas
        k = orejas
        caja(out, Mo, -1.35, 1.35, 0.0, 1.9 * k, -0.75, 0.75, piel, semilla=5)
        caja(out, Mo, -0.9, 0.9, 1.8 * k, 3.5 * k, -0.52, 0.52, piel, semilla=5)
        caja(out, Mo, -0.45, 0.45, 3.4 * k, 4.9 * k, -0.3, 0.3, piel, semilla=5)
        Mg = Mh @ vr.T(s * 3.45, 1.0, -0.8) @ vr.Rz(s * 22 * D)                                       # la gola
        caja(out, Mg, -0.9, 0.9, -1.8, 1.8, -2.6, 1.4, pelo, semilla=6)
        caja(out, Mg @ vr.T(s * 0.9, -0.6, -0.6), -0.7, 0.7, -1.6, 1.2, -2.2, 0.8, pelo, semilla=7)
    bm.cubo(out, Mh, -2.6, 0.8, 2.3, 5.2, 2.8, 8.0, piel, caras={'abajo': P['fauces']}, semilla=8)     # el hocico
    caja(out, Mh, -1.6, 1.6, 3.5, 4.3, 2.3, 9.4, piel, semilla=9)
    caja(out, Mh, -1.5, 1.5, 2.4, 3.9, 10.2, 11.0, P['nariz'], semilla=10)
    hilera(out, Mh, [(-2.35, 2.6), (-2.35, 10.05), (2.35, 10.05), (2.35, 2.6)], 0.85, -1.0, P['dientes_arriba'], semilla=11)
    for s in (1, -1):                                                                                 # los colmillos
        M = Mh @ vr.T(s * 1.85, 0.85, 9.2)
        caja(out, M, -0.42, 0.42, -2.0, 0.0, -0.38, 0.38, P['colmillo'], semilla=12)
        caja(out, M, -0.24, 0.24, -3.0, -1.9, -0.22, 0.22, P['colmillo'], semilla=13)
    caja(out, Mh, -1.9, 1.9, -1.6, 0.85, 2.0, 2.3, P['nucleo'], semilla=14)                          # el nucleo
    Mj = Mh @ vr.T(0, 0.8, 1.4) @ vr.Rx(abre * D)                                                     # la mandibula
    bm.cubo(out, Mj, -2.4, -1.7, 0.0, 4.8, 1.7, 8.6, piel, caras={'arriba': P['boca']}, semilla=15)
    hilera(out, Mj, [(-2.15, 1.2), (-2.15, 8.35), (2.15, 8.35), (2.15, 1.2)], 0.0, 0.9, P['dientes_abajo'], semilla=16)
    for s in (1, -1):
        M = Mj @ vr.T(s * 1.7, 0.0, 7.6)
        caja(out, M, -0.38, 0.38, 0.0, 1.8, -0.34, 0.34, P['colmillo'], semilla=17)
        caja(out, M, -0.22, 0.22, 1.7, 2.5, -0.2, 0.2, P['colmillo'], semilla=18)
    caja(out, Mj, -1.7, 1.7, -2.7, -1.5, 0.6, 4.4, pelo, semilla=19)                                 # la barba
    return pt(Mh, (0.0, 0.4, 5.5))


def serpiente(out, P, ctrl, grosor=1.0, encendida=False, abre=32.0, semilla=0):
    """Una serpiente (de la crin o la cola): el cuerpo de bloques que se afina y, al final, la cabeza: el
    craneo, el hocico, los ojos encendidos a los lados, la mandibula abierta y dos colmillos. La de la cola
    lleva la boca encendida del neon, como las cabezas."""
    pts, rs, ts = jm.a_lo_largo(ctrl, 8, ((0.0, 1.0), (0.45, 1.05), (0.85, 0.8), (1.0, 0.72)))
    rs = [r * grosor for r in rs]
    jm.tubo(out, pts, rs, [P['serpiente']] * (len(pts) - 1), semilla=semilla)
    d = pts[-1] - pts[-2]
    M = em.marco(pts[-1], d, up=(0.0, 1.0, 0.0))
    g = grosor
    caja(out, M, -1.2 * g, 1.2 * g, -0.35 * g, 0.8 * g, -0.4 * g, 2.0 * g, P['serpiente'], semilla=semilla + 5)
    caja(out, M, -0.85 * g, 0.85 * g, -0.25 * g, 0.55 * g, 1.9 * g, 2.9 * g, P['serpiente'], semilla=semilla + 6)
    for s in (1, -1):
        caja(out, M, s * 1.17 * g - 0.22 * g, s * 1.17 * g + 0.22 * g, 0.15 * g, 0.6 * g, 0.9 * g, 1.5 * g, P['ojo'],
             semilla=semilla + 7)
    boca_ = P['fauces'] if encendida else P['boca_serpiente']
    suelo = P['boca'] if encendida else P['boca_serpiente']
    Mj = M @ vr.T(0, -0.35 * g, -0.2 * g) @ vr.Rx(abre * D)
    caja(out, Mj, -0.9 * g, 0.9 * g, -0.45 * g, 0.0, 0.0, 2.7 * g, P['serpiente'], semilla=semilla + 8)
    caja(out, Mj, -0.65 * g, 0.65 * g, -0.02, 0.06 * g, 0.5 * g, 2.45 * g, suelo, semilla=semilla + 9)
    caja(out, M, -0.66 * g, 0.66 * g, -0.37 * g, -0.27 * g, 0.7 * g, 2.75 * g, boca_, semilla=semilla + 10)
    for s in (1, -1):
        caja(out, M, s * 0.5 * g - 0.13 * g, s * 0.5 * g + 0.13 * g, -1.0 * g, -0.3 * g, 2.4 * g, 2.68 * g, P['colmillo'],
             semilla=semilla + 11)
    return pt(M, (0.0, -0.3 * g, 1.6 * g))


def collar(out, P, p, d, r, pinchos=8, semilla=0):
    """El collar: un aro ancho de metal con remaches alrededor del cuello y los pinchos hacia fuera."""
    M = em.marco(np.asarray(p, float), np.asarray(d, float))
    R = r + 0.7
    caja(out, M, -R, R, -R * 0.72, R * 0.72, -0.8, 0.8, P['metal'], semilla=semilla)
    caja(out, M, -R * 0.72, R * 0.72, -R, R, -0.8, 0.8, P['metal'], semilla=semilla + 1)
    for k in range(pinchos):
        a = (k + 0.5) * TAU / pinchos
        u = np.array((math.cos(a), math.sin(a), 0.0))
        pua(out, pt(M, u * R * 0.95), M[:3, :3] @ u, 0.45, 2.0, P['pincho'], semilla=semilla + 2)
    return M


def cuello(out, P, ctrl, r0=3.4, r1=2.9, semilla=0):
    """El cuello de una cabeza: un tubo de pelo corto con la crin de mechones por arriba y el collar de
    pinchos cerca de la cabeza. Devuelve el marco del collar."""
    pts, rs, ts = jm.a_lo_largo(ctrl, 7, ((0.0, r0), (1.0, r1)))
    jm.tubo(out, pts, rs, [P['piel']] * (len(pts) - 1), semilla=semilla)
    for j in range(1, len(pts) - 2):                                                                # la crin
        d = pts[j + 1] - pts[j]
        M = em.marco(pts[j], d, up=(0.0, 1.0, 0.0))
        Mt = M @ vr.T(0.0, rs[j] * 0.85, 0.0) @ vr.Rx(-62 * D)
        caja(out, Mt, -1.1, 1.1, -0.45, 0.45, 0.0, 3.0, P['pelaje'], semilla=semilla + 3)
    j = len(pts) - 2
    return collar(out, P, pts[j], pts[j + 1] - pts[j], rs[j], semilla=semilla + 5)


def pata(out, P, cad, pie, codo, gruesa=1.0, alzada=False, rod=None, tob=None, semilla=0):
    """Una pata larga de perro, de puntillas: el muslo hasta el codo (o la rodilla), la pierna hasta el
    tobillo, que va alto, el metatarso hasta la pata y la pata con cuatro dedos y sus unas. codo es hacia
    donde sale la articulacion de en medio (atras en las de delante, adelante en las de atras); el tobillo
    sale al reves. rod y tob fuerzan las articulaciones (sentado)."""
    cad, pie, codo = (np.asarray(v, float) for v in (cad, pie, codo))
    codo = codo / np.linalg.norm(codo)
    L = float(np.linalg.norm(pie - cad))
    plano = np.array((codo[0], 0.0, codo[2]))
    rod = cad + (pie - cad) * 0.42 + codo * L * 0.2 if rod is None else np.asarray(rod, float)
    if tob is None:
        tob = pie + np.array((0.0, min(4.0, L * 0.26), 0.0)) - plano * L * 0.1
    tob = np.asarray(tob, float)
    fin = pie + np.array((0.0, 0.8, 0.0))
    caja(out, vr.T(*cad), -2.6 * gruesa, 2.6 * gruesa, -2.6 * gruesa, 2.6 * gruesa, -2.6 * gruesa, 2.6 * gruesa,
         P['piel'], semilla=semilla)
    for a, b, g in ((cad, rod, 2.3 * gruesa), (rod, tob, 1.6 * gruesa), (tob, fin, 1.25 * gruesa)):
        M = em.marco(a, b - a)
        Lg = float(np.linalg.norm(b - a))
        caja(out, M, -g, g, -g, g, -0.5, Lg + 0.5, P['piel'], semilla=semilla + 1)
    adelante = np.array((plano[0] * 0.2, 0.0, 1.0))
    Mp = em.marco(pie, adelante, up=(0.0, 1.0, 0.0))
    caja(out, Mp, -1.9, 1.9, -0.8, 1.0, -1.6, 1.8, P['piel'], semilla=semilla + 3)                   # la pata
    for j in range(4):                                                                              # los dedos
        x = (j - 1.5) * 1.05
        caja(out, Mp, x - 0.48, x + 0.48, -0.8, 0.55, 1.6, 2.8 - 0.3 * abs(j - 1.5), P['piel'], semilla=semilla + 4)
        Mu = Mp @ vr.T(x, -0.2, 2.7 - 0.3 * abs(j - 1.5)) @ vr.Rx(30 * D)
        caja(out, Mu, -0.26, 0.26, -0.32, 0.26, 0.0, 1.2, P['garra'], semilla=semilla + 5)


def _eje(Y, largo):
    """El eje del tronco: de la grupa (atras) al pecho (delante), con la cintura recogida."""
    zt = -16.0 - (largo - 1.0) * 6.0
    return [np.array(c, float) for c in ((0.0, Y + 0.6, zt), (0.0, Y - 0.3, -7.0), (0.0, Y, 1.0), (0.0, Y + 1.0, 9.0))]


PERFIL_TRONCO = ((0.0, 4.3), (0.2, 4.5), (0.45, 3.4), (0.75, 5.3), (0.9, 5.5), (1.0, 4.7))
ACHATA = 1.2                                     # el tronco es mas alto que ancho: pecho hondo


def _en_eje(Y, z, largo=1.0):
    zt = -16.0 - (largo - 1.0) * 6.0
    zs = [zt, -7.0, 1.0, 9.0]
    ys = [Y + 0.6, Y - 0.3, Y, Y + 1.0]
    t = (z - zt) / (9.0 - zt)
    return float(np.interp(z, zs, ys)), float(np.interp(t, [a for a, _ in PERFIL_TRONCO], [b for _, b in PERFIL_TRONCO]))


def tronco(out, P, Y, largo=1.0, cresta=1.0, semilla=0):
    """El cuerpo de perro de presa: el tronco que se recoge en la cintura, el pecho hondo con la quilla, la
    pechera de pelo, los hombros y la grupa de musculo, y la cresta de mechones por el lomo."""
    pts, rs, ts = jm.a_lo_largo(_eje(Y, largo), 10, PERFIL_TRONCO)
    jm.tubo(out, pts, rs, [P['piel']] * (len(pts) - 1), semilla=semilla, achata=ACHATA)
    yc, r = _en_eje(Y, 5.0, largo)
    caja(out, jm.I4, -3.6, 3.6, yc - r * ACHATA - 1.6, yc - 2.0, 0.5, 8.4, P['piel'], semilla=semilla + 1)     # la quilla
    caja(out, jm.I4, -4.0, 4.0, yc - r * ACHATA - 0.6, yc + 2.4, 7.6, 10.4, P['pelaje'], semilla=semilla + 2)  # la pechera
    for s in (1, -1):
        x0, x1 = sorted((s * 3.0, s * 6.0))
        caja(out, jm.I4, x0, x1, yc - 4.2, yc + 2.6, 2.6, 9.4, P['piel'], semilla=semilla + 3)             # los hombros
        yg, rg = _en_eje(Y, -13.0 * largo, largo)
        x0, x1 = sorted((s * 2.6, s * 5.4))
        caja(out, jm.I4, x0, x1, yg - 3.6, yg + 2.4, -13.0 * largo - 4.0, -13.0 * largo + 3.4, P['piel'], semilla=semilla + 4)
    for j in range(1, len(pts) - 1):                                                                  # la cresta
        d = pts[j + 1] - pts[j - 1]
        M = em.marco(pts[j], d, up=(0.0, 1.0, 0.0))
        Mt = M @ vr.T(0.0, rs[j] * ACHATA * 0.9, 0.0) @ vr.Rx(-58 * D)
        caja(out, Mt, -1.2, 1.2, -0.5, 0.5, 0.0, 2.4 * cresta, P['pelaje'], semilla=semilla + 5 + j % 2)


# ======================================================================
#  CERBERO
# ======================================================================
def cerbero(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    largo = 1.25 if tipo == 'B' else 1.0
    Y = {'A': 19.0, 'B': 16.0, 'C': 17.0}[tipo]
    cuerpo, resto = [], []
    try:
        tronco(cuerpo, P, Y, largo=largo, cresta=(1.9 if tipo == 'B' else 1.0), semilla=100)
        # la pose del cuerpo
        zg = -13.0 * largo                                                 # la grupa
        if tipo == 'B':                                                    # agazapado: el pecho baja, la grupa queda alta
            Mc = vr.T(0.0, Y, zg) @ vr.Rx(11 * D) @ vr.T(0.0, -Y, -zg)
        elif tipo == 'C':                                                  # sentado sobre los cuartos traseros
            Mc = vr.T(0.0, 7.5 - Y, 0.0) @ vr.T(0.0, Y, zg) @ vr.Rx(-46 * D) @ vr.T(0.0, -Y, -zg)
        else:
            Mc = np.eye(4)
        out = qm.transformar(cuerpo, Mc)
        # las cabezas: (base del cuello en el cuerpo, punta del cuello en el mundo respecto a la base, giro, cabeceo)
        if tipo == 'A':
            cabezas = [((0.0, Y + 2.4, 8.4), (0.0, 10.4, 7.0), 0, 8),
                       ((-3.4, Y + 1.6, 7.6), (-10.6, 6.6, 4.8), -26, 6),
                       ((3.4, Y + 1.6, 7.6), (10.6, 6.6, 4.8), 26, 6)]
        elif tipo == 'B':
            cabezas = [((-2.4, Y + 1.8, 8.4), (-5.6, 3.8, 9.4), -14, 4),
                       ((2.4, Y + 1.8, 8.4), (5.6, 3.8, 9.4), 14, 4)]
        else:
            cabezas = [((0.0, Y + 2.4, 8.4), (0.0, 11.0, 6.4), 0, 16),
                       ((-3.4, Y + 1.6, 7.6), (-10.6, 6.8, 4.6), -22, 14),
                       ((3.4, Y + 1.6, 7.6), (10.6, 6.8, 4.6), 22, 14)]
        bocas, collares = [], []
        for base_b, punta, giro, cabeceo in cabezas:
            base = pt(Mc, base_b)
            fin = base + np.array(punta)
            medio = base + (fin - base) * 0.5 + np.array((0.0, 1.6, -0.6))
            Mcol = cuello(resto, P, [base, medio, fin], semilla=120)
            collares.append(Mcol)
            Mh = vr.T(*fin) @ vr.Ry(giro * D) @ vr.Rx(cabeceo * D) @ np.diag([CABEZA] * 3 + [1.0]) @ vr.T(0.0, -1.8, 3.2)
            bm.PPB = PPB / CABEZA
            bocas.append(cabeza(resto, Mh, P, abre=38.0, orejas=(1.35 if tipo == 'B' else 1.0)))
            bm.PPB = PPB
        # la crin de serpientes por el lomo (el Guardian)
        if tipo == 'A':
            for j, z in enumerate((4.0, 0.0, -4.0, -8.0, -12.0)):
                yc, r = _en_eje(Y, z)
                fx = 1.0 if j % 2 else -1.0
                b = np.array((fx * 1.0, yc + r * ACHATA * 0.85, z))
                alto = 11.5 - 0.9 * j                                   # se abren a los lados: asoman junto a las cabezas
                ctrl = [b, b + np.array((fx * 2.0, alto * 0.4, -1.0)), b + np.array((fx * 5.0, alto * 0.8, -0.5)),
                        b + np.array((fx * 7.0, alto, 1.5)), b + np.array((fx * 7.4, alto * 0.94, 3.6))]
                serpiente(resto, P, ctrl, grosor=1.3, semilla=150 + j % 3)
        # la cola, que es una serpiente con la boca encendida
        if tipo == 'A':
            ctrl_cola = [(0.0, Y + 1.0, -15.5), (3.0, Y + 3.0, -21.0), (8.0, Y + 9.0, -24.0), (11.0, Y + 15.0, -21.0),
                         (12.0, Y + 18.0, -16.0), (12.0, Y + 18.6, -12.0)]
            ctrl_cola = [pt(Mc, c) for c in ctrl_cola]
        elif tipo == 'B':
            ctrl_cola = [(0.0, Y + 1.0, zg - 3.0), (2.0, Y + 2.0, zg - 9.0), (7.0, Y + 5.0, zg - 13.0), (11.0, Y + 10.0, zg - 11.0),
                         (12.0, Y + 13.0, zg - 6.0), (11.5, Y + 13.6, zg - 2.0)]
            ctrl_cola = [pt(Mc, c) for c in ctrl_cola]
        else:                                                              # enroscada en el suelo, la cabeza alzada delante
            base = pt(Mc, (0.0, Y + 0.6, zg - 2.5))
            ctrl_cola = [base, base + np.array((3.0, -3.0, -3.0)), np.array((9.0, 2.0, base[2] - 2.0)),
                         np.array((12.5, 2.2, base[2] + 6.0)), np.array((13.0, 3.6, base[2] + 13.0)),
                         np.array((12.4, 6.8, base[2] + 16.0))]
        pts, rs, ts = jm.a_lo_largo([np.asarray(c, float) for c in ctrl_cola], 12, ((0.0, 2.4), (0.6, 1.8), (1.0, 1.5)))
        jm.tubo(resto, pts, rs, [P['serpiente']] * (len(pts) - 1), semilla=170)
        d = pts[-1] - pts[-2]
        cola_boca = serpiente(resto, P, [pts[-2], pts[-1], pts[-1] + d / np.linalg.norm(d) * 1.5], grosor=2.1, encendida=True,
                              abre=34.0, semilla=175)
        # las cadenas rotas (el Encadenado): de cada collar al suelo, y entre los collares
        if tipo == 'C':
            eslabon = 1.7
            bajos = [pt(M, (0.0, -3.6, 0.0)) for M in collares]
            for j, p0 in enumerate(bajos):
                s = (0.0, -1.0, 1.0)[j]
                p1 = np.array((p0[0] + s * 1.5, 2.2, p0[2] + 3.0))
                cadena(resto, p0, p1, eslabon, P['metal_liso'], semilla=180)
                cadena(resto, p1, p1 + np.array((s * 2.5 + 1.0, 0.0, 4.0)), eslabon, P['metal_liso'], semilla=181)
            for j in (1, 2):
                a, b = bajos[0], bajos[j]
                m = (a + b) / 2 + np.array((0.0, -4.5, 1.5))
                cadena(resto, a, m, eslabon, P['metal_liso'], semilla=182)
                cadena(resto, m, b, eslabon, P['metal_liso'], semilla=183)
        # las cuatro patas, del cuerpo al suelo
        for fila, z, codo, gruesa in ((1, 6.0, (0.2, 0.0, -1.0), 1.05), (-1, zg, (0.2, 0.0, 1.0), 1.15)):
            yc, r = _en_eje(Y, z, largo)
            for s in (1, -1):
                cad = pt(Mc, (s * 4.6, yc - 3.4, z))
                cd = np.array((s * codo[0], codo[1], codo[2]))
                rod = tob = None
                if tipo == 'B' and fila == 1:                               # agazapado: las de delante abiertas y dobladas
                    pie = np.array((cad[0] + s * 3.4, 0.0, cad[2] + 6.5))
                    cd = np.array((s * 0.6, 0.2, -1.0))
                elif tipo == 'B':                                           # las de atras, estiradas
                    pie = np.array((cad[0] + s * 1.2, 0.0, cad[2] - 4.0))
                elif tipo == 'C' and fila == 1:                             # sentado: las de delante rectas
                    pie = np.array((cad[0] + s * 0.8, 0.0, cad[2] + 2.5))
                    cd = np.array((s * 0.1, 0.0, -1.0))
                elif tipo == 'C':                                           # sentado: la de atras doblada en el suelo
                    pie = np.array((cad[0] + s * 3.2, 0.0, cad[2] + 9.0))
                    rod = cad + np.array((s * 3.4, 2.6, 6.0))
                    tob = np.array((cad[0] + s * 3.0, 1.6, cad[2] - 1.0))
                else:
                    pie = np.array((cad[0] + s * 0.8, 0.0, cad[2] + fila * 2.0))
                pie = pie + np.array((0.0, 0.8, 0.0))
                pata(resto, P, cad, pie, cd, gruesa=gruesa, rod=rod, tob=tob, semilla=200 + (fila + 1) * 6)
        out += resto
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    bocas = [pt(E, b) for b in bocas]
    centro = bocas[0] if len(bocas) == 3 else (bocas[0] + bocas[1]) / 2   # la de en medio, o entre las dos de Ortro
    return out, {'boca': centro, 'bocas': bocas, 'luces': bocas + [pt(E, cola_boca)]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

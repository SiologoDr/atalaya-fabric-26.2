"""
Anubis y sus formas (14-10-2026). Juan, al descartar Tanara y Zancara: «revisa nuevamente cada ficha de boss y
mobs para que hagas el siguiente boss y sus tipos; en el siguiente hagamos algo con tematica egipcia».

Lo aprobado en las fichas son monstruos de mito hechos grandes y que imponen (la sierpe, la dragona, la hidra, la
sirena, la Gorgona, el Minotauro, Cerbero). El de Egipto es Anubis, el dios con cabeza de chacal que guarda a los
muertos y pesa sus corazones: un coloso como el Minotauro, no un animal. Se lee egipcio de un vistazo por las
orejas altas en punta, el nemes de rayas de oro y lapislazuli, el collar ancho de cuentas, el faldellin de lino
plisado y los brazaletes de oro. No va por la boca: lo que manda son los ojos encendidos, perfilados de oro como el
ojo egipcio, y lo que lleva en cada forma. Todo de cajas, con texturas limpias (rayas, cuentas, pliegues).

Las tres formas cambian la silueta:

    A  el Pesador de Almas   de pie, erguido, con la balanza del juicio en alto (el corazon encendido contra la
                             pluma de Maat) y el cetro uas; lapislazuli
    B  el Chacal de la Duat  la bestia: encorvado para saltar, con las fauces abiertas que arden, la crin negra y
                             una espada jopesh en cada mano; cornalina
    C  Anubis Embalsamado    la momia: envuelto en vendas, con los brazos cruzados sobre el pecho y el cayado y el
                             mayal, el anj encendido en el vientre, las piernas atadas, flotando; turquesa
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _degradado, lamina, cadena
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.58
CABEZA = 1.5

ORO = _r('5a3a0a', '8a6014', 'b88a24', 'e0b440', 'fde68a')
LAPIS = _r('0a1640', '12245e', '1c3a8a', '2c58b8', '4a80e0')
TURQUESA = _r('0a3a34', '12584e', '1e7e6e', '34a890', '5ad0b4')
CORNALINA = _r('5a1a0a', '8a2a12', 'b84020', 'e0602e', 'ff8a50')
LINO = _r('8a8270', 'b0a890', 'd0c8b0', 'e8e0cc', 'faf6ea')
DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')
VARIANTES = {
    'A': dict(
        clave='A', nombre='el Pesador de Almas', corto='pesador',
        piel=_r('08080c', '101016', '18181f', '22222b', '2e2e3a'),
        pelaje=_r('060608', '0e0e12', '16161c', '202028', '2c2c36'),
        bronce=_r('3a2410', '6a4420', '9a6a34', 'c8964c', 'f0c878'),
        venda=LINO, neon=('e0ecff', '2f6bff', '0a1c5a'),
    ),
    'B': dict(
        clave='B', nombre='el Chacal de la Duat', corto='chacal',
        piel=_r('0c0808', '161010', '201818', '2c2020', '3a2c2a'),
        pelaje=_r('0a0606', '120c0c', '1c1414', '281c1c', '362626'),
        bronce=_r('3a2410', '6a4420', '9a6a34', 'c8964c', 'f0c878'),
        venda=LINO, neon=('ffe8e0', 'ff4b26', '6a1404'),
    ),
    'C': dict(
        clave='C', nombre='Anubis Embalsamado', corto='embalsamado',
        piel=_r('08090a', '101214', '181b1e', '222629', '2e3337'),
        pelaje=_r('060708', '0e1012', '16181b', '202326', '2c3034'),
        bronce=_r('3a2410', '6a4420', '9a6a34', 'c8964c', 'f0c878'),
        venda=_r('3a3426', '5e5640', '847a5e', 'a89e80', 'ccc2a4'),
        neon=('e0fff6', '36e0b0', '045a44'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def _bandas(tw, th, colores, ancho=3, a_lo_largo=False):
    """Bandas de colores (cada una con su canto claro y su junta oscura): las rayas del nemes, del collar, del
    cetro. colores: lista de rampas de 5 tonos que se repiten."""
    ys, xs = np.mgrid[0:th, 0:tw]
    k = (xs if a_lo_largo else ys)
    banda = (k // ancho) % len(colores)
    fila = k % ancho
    t = np.zeros((th, tw, 4), np.uint8)
    for i, rampa in enumerate(colores):
        idx = np.where(fila == 0, 3, np.where(fila == ancho - 1, 1, 2))
        img = _imagen(idx, rampa)
        m = banda == i
        t[m] = img[m]
    return t


def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'anu%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']
    reg('piel', jm.liso(V['piel'], 2, 1, 1))
    reg('pelaje', lambda tw, th, c, s: (jm.hebras(tw, th, s, V['pelaje'], 2, 4), None))
    reg('nariz', jm.liso(_r('020202', '060606', '0c0c0c', '141414', '1c1c1c'), 1, 1, 0))
    reg('hueco', jm.liso(_r('020202', '040404', '080808', '0c0c0c', '101010'), 1, 0, 0))
    reg('oro', jm.liso(ORO, 3, 1, 1))
    reg('lapis', jm.liso(LAPIS, 2, 1, 1))
    reg('bronce', jm.liso(V['bronce'], 3, 1, 1))

    def nemes(tw, th, cara, s):
        """El nemes: rayas de oro y de lapislazuli, de traves."""
        return _bandas(tw, th, (ORO, LAPIS), ancho=3), None
    reg('nemes', nemes)

    def nemes_largo(tw, th, cara, s):
        """Las rayas a lo largo (para los cetros y el delantal)."""
        return _bandas(tw, th, (ORO, LAPIS), ancho=3, a_lo_largo=True), None
    reg('nemes_largo', nemes_largo)

    def collar(tw, th, cara, s):
        """El collar ancho de cuentas: bandas de oro, lapislazuli, turquesa y cornalina, con las cuentas claras."""
        t = _bandas(tw, th, (ORO, LAPIS, TURQUESA, CORNALINA), ancho=3)
        ys, xs = np.mgrid[0:th, 0:tw]
        cuenta = ((ys % 3) == 1) & ((xs % 2) == 0)
        t[cuenta, :3] = np.minimum(t[cuenta, :3].astype(int) + 40, 255).astype(np.uint8)
        return t, None
    reg('collar', collar)

    def lino(tw, th, cara, s):
        """El lino plisado del faldellin: pliegues verticales claros con su sombra."""
        largo_x = tw >= th
        ys, xs = np.mgrid[0:th, 0:tw]
        k_ = ys if largo_x and False else xs
        idx = np.where((k_ % 3) == 0, 4, np.where((k_ % 3) == 1, 3, 2))
        return _imagen(idx, LINO), None
    reg('lino', lino)

    def venda(tw, th, cara, s):
        """Las vendas: tiras un poco en diagonal, con el canto claro y la junta oscura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        k_ = ys * 2 + xs // 3
        return _imagen(np.where((k_ % 6) == 0, 1, np.where((k_ % 6) == 1, 3, 2)), V['venda']), None
    reg('venda', venda)

    def pluma(tw, th, cara, s):
        """La pluma de Maat: blanca, con el raquis claro por el medio y las barbas en bandas."""
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        idx = np.full((n_a, n_l), 3)
        idx[:, np.arange(n_l) % 3 == 0] = 2
        idx[n_a // 2, :] = 4
        if not largo_x:
            idx = idx.T
        return _imagen(idx, LINO), None
    reg('pluma', pluma)

    def filo(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if tw >= 3:
            idx[:, -1] = 4
            idx[:, -2] = 3
        return _imagen(_bisel(idx, 1, 1), V['bronce']), None
    reg('filo', filo)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)
    reg('luz', ojo, pleno=True)

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
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, DIENTES, True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, DIENTES, False))
    reg('colmillo', jm.liso(DIENTES, 3, 1, 1))
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def _u(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


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


def cabeza(out, Mh, P, abierta=False, vendada=False):
    """La cabeza de chacal, con el hocico hacia +z: el craneo estrecho y redondeado; los ojos encendidos,
    perfilados de oro como el ojo egipcio, con la raya que se alarga hacia la sien y la ceja de oro; el hocico
    largo y fino, en tres tramos que se afinan, con la trufa negra; la boca cerrada (o abierta y encendida, en la
    bestia); las orejas altas en punta, negras, con una tira de oro dentro; y el nemes de rayas, con la banda de la
    frente, las alas a los lados y las caidas por delante de los hombros. Devuelve el punto de luz."""
    piel = P['piel']
    caja(out, Mh, -3.0, 3.0, 0.0, 5.4, -3.4, 2.0, piel, semilla=1)                                   # el craneo
    caja(out, Mh, -2.4, 2.4, 5.2, 5.9, -2.8, 1.4, piel, semilla=1)
    caja(out, Mh, -3.3, 3.3, 0.8, 4.4, -2.8, 1.4, piel, semilla=1)                                   # las mejillas
    for s in (1, -1):
        x0, x1 = sorted((s * 0.95, s * 2.5))
        caja(out, Mh, x0, x1, 3.5, 4.25, 1.9, 2.22, P['ojo'], semilla=2)                              # los ojos
        x0, x1 = sorted((s * 2.45, s * 3.1))                                                         # el perfil de oro
        caja(out, Mh, x0, x1, 3.65, 3.98, -0.6, 2.1, P['oro'], semilla=3)
        x0, x1 = sorted((s * 2.85, s * 3.15))
        caja(out, Mh, x0, x1, 2.8, 3.75, -0.6, -0.1, P['oro'], semilla=3)
        Mc = Mh @ vr.T(s * 1.75, 4.6, 2.05) @ vr.Rz(s * 10 * D)                                       # la ceja
        caja(out, Mc, -1.15, 1.15, -0.14, 0.14, -0.1, 0.12, P['oro'], semilla=3)
        Mo = Mh @ vr.T(s * 1.85, 5.3, -1.3) @ vr.Rz(-s * 8 * D) @ vr.Rx(-12 * D)                     # las orejas
        for k, (w, y0, y1, d) in enumerate(((1.3, 0.0, 2.9, 0.7), (0.9, 2.7, 5.6, 0.5), (0.5, 5.4, 7.8, 0.34))):
            caja(out, Mo, -w, w, y0, y1, -d, d, piel, semilla=4)
            if k < 2:
                caja(out, Mo, -w * 0.35, w * 0.35, y0 + 0.3, y1 - 0.2, d - 0.05, d + 0.1, P['oro'], semilla=5)
    hoc = P['venda'] if vendada else piel
    if not abierta:
        caja(out, Mh, -1.7, 1.7, 1.3, 3.3, 1.8, 5.8, hoc, semilla=6)                                 # el hocico
        caja(out, Mh, -1.35, 1.35, 1.3, 3.0, 5.6, 9.4, hoc, semilla=6)
        caja(out, Mh, -1.0, 1.0, 1.4, 2.8, 9.2, 11.0, hoc, semilla=6)
        caja(out, Mh, -0.8, 0.8, 2.1, 2.95, 10.8, 11.5, P['nariz'], semilla=7)                        # la trufa
        caja(out, Mh, -1.4, 1.4, 0.35, 1.4, 1.6, 10.4, hoc, semilla=8)                               # la boca cerrada
        caja(out, Mh, -1.42, 1.42, 1.32, 1.46, 3.0, 10.3, P['hueco'], semilla=9)
        luz = pt(Mh, (0.0, 3.9, 4.0))
    else:                                                                                              # la bestia: abierta
        bm.cubo(out, Mh, -1.7, 1.3, 1.8, 3.4, 2.0, 4.0, piel, caras={'abajo': P['fauces']}, semilla=10)
        bm.cubo(out, Mh, -1.35, 1.3, 5.6, 2.7, 1.7, 3.8, piel, caras={'abajo': P['fauces']}, semilla=10)
        caja(out, Mh, -1.0, 1.0, 1.4, 2.8, 9.2, 11.0, piel, semilla=6)
        caja(out, Mh, -0.8, 0.8, 2.1, 2.95, 10.8, 11.5, P['nariz'], semilla=7)
        hilera(out, Mh, [(-1.5, 2.2), (-1.2, 9.2), (1.2, 9.2), (1.5, 2.2)], 1.3, -1.0, P['dientes_arriba'], semilla=11)
        for s in (1, -1):
            M = Mh @ vr.T(s * 1.0, 1.3, 8.6)
            caja(out, M, -0.3, 0.3, -1.8, 0.0, -0.28, 0.28, P['colmillo'], semilla=12)
        Mj = Mh @ vr.T(0, 1.3, 1.8) @ vr.Rx(36 * D)
        bm.cubo(out, Mj, -1.4, -1.1, 0.0, 2.8, 1.1, 8.0, piel, caras={'arriba': P['boca']}, semilla=13)
        hilera(out, Mj, [(-1.2, 0.6), (-1.0, 7.7), (1.0, 7.7), (1.2, 0.6)], 0.0, 0.8, P['dientes_abajo'], semilla=14)
        luz = pt(Mh, (0.0, 0.6, 5.5))
    # el nemes: la banda de la frente, el casquete, las alas y las caidas por delante
    caja(out, Mh, -3.35, 3.35, 4.9, 5.45, -3.7, 2.15, P['oro'], semilla=15)
    caja(out, Mh, -3.3, 3.3, 3.6, 5.0, -3.9, 1.7, P['nemes'], semilla=16)
    for s in (1, -1):
        x0, x1 = sorted((s * 3.0, s * 4.15))
        caja(out, Mh, x0, x1, -2.6, 4.9, -3.7, 1.0, P['nemes'], semilla=17)                          # las alas
        x0, x1 = sorted((s * 2.9, s * 4.25))
        caja(out, Mh, x0, x1, -9.5, -2.4, -0.4, 1.6, P['nemes'], semilla=18)                         # las caidas
        caja(out, Mh, x0, x1, -10.0, -9.4, -0.5, 1.7, P['oro'], semilla=19)
    caja(out, Mh, -2.3, 2.3, -6.0, 1.0, -4.6, -3.5, P['nemes'], semilla=20)                          # la cola del nemes
    return luz


def torso(out, P, cuerpo='piel'):
    """El torso de dios: la cadera, la cintura mas estrecha, el pecho ancho con los pectorales y los abdominales,
    los hombros anchos y el cuello."""
    piel = P[cuerpo]
    caja(out, jm.I4, -5.4, 5.4, 22.0, 27.6, -3.6, 3.6, piel, semilla=100)                            # la cadera
    caja(out, jm.I4, -4.7, 4.7, 27.4, 32.8, -3.2, 3.2, piel, semilla=101)                            # la cintura
    if cuerpo == 'piel':
        for j, y in enumerate((28.0, 29.7, 31.4)):
            for s in (1, -1):
                x0, x1 = sorted((s * 0.3, s * 2.6))
                caja(out, jm.I4, x0, x1, y, y + 1.3, 3.05, 3.6, piel, semilla=102)
    caja(out, jm.I4, -7.4, 7.4, 32.6, 41.4, -4.2, 4.2, piel, semilla=103)                            # el pecho
    if cuerpo == 'piel':
        for s in (1, -1):
            x0, x1 = sorted((s * 0.3, s * 6.6))
            caja(out, jm.I4, x0, x1, 35.6, 40.6, 4.1, 5.1, piel, semilla=104)
    caja(out, jm.I4, -9.0, 9.0, 38.8, 42.6, -3.8, 3.8, piel, semilla=105)                            # los hombros
    caja(out, jm.I4, -2.7, 2.7, 41.6, 46.0, -2.5, 2.5, P['piel'], semilla=106)                       # el cuello


def collar(out, P):
    """El collar ancho de cuentas: cuatro escalones de bandas sobre los hombros y el pecho."""
    for j, (w, y0, y1, z0, z1) in enumerate(((9.4, 40.8, 42.9, -4.1, 4.6), (8.2, 38.8, 41.0, 3.9, 5.2),
                                             (6.6, 36.8, 39.0, 4.7, 5.8), (4.4, 35.2, 37.0, 5.3, 6.2))):
        caja(out, jm.I4, -w, w, y0, y1, z0, z1, P['collar'], semilla=110 + j)
    caja(out, jm.I4, -9.5, 9.5, 41.0, 42.8, -4.3, -3.8, P['collar'], semilla=114)


def faldellin(out, P):
    """El faldellin de lino plisado, abierto en trapecio, con el cinturon de rayas y el delantal de oro y
    lapislazuli por delante."""
    caja(out, jm.I4, -5.7, 5.7, 25.0, 27.4, -3.9, 3.9, P['nemes'], semilla=120)                      # el cinturon
    caja(out, jm.I4, -6.0, 6.0, 19.4, 25.2, -4.1, 4.1, P['lino'], semilla=121)
    caja(out, jm.I4, -6.7, 6.7, 15.0, 19.6, -4.6, 4.6, P['lino'], semilla=122)
    caja(out, jm.I4, -1.7, 1.7, 14.4, 25.0, 4.5, 5.0, P['nemes_largo'], semilla=123)                 # el delantal
    caja(out, jm.I4, -2.0, 2.0, 14.0, 14.8, 4.4, 5.1, P['oro'], semilla=124)


HOMBRO = np.array((10.6, 40.0, 0.0))
L_BRAZO, L_ANTEBRAZO = 10.0, 9.0


def brazo(out, P, s, pose, cuerpo='piel'):
    """Un brazo de dios: el hombro, el brazo y el antebrazo, que dobla por la espalda del codo, con el brazalete
    de oro arriba y la ajorca en la muneca, y la mano. Devuelve el marco de la mano."""
    piel = P[cuerpo]
    Mh = (vr.T(s * HOMBRO[0], HOMBRO[1], HOMBRO[2]) @ vr.Rz(s * pose.get('abd', 10) * D) @ vr.Rx(-pose.get('flex', 0) * D)
          @ vr.Ry(-s * pose.get('giro', 0) * D))
    Mc = Mh @ vr.T(0, -L_BRAZO, -2.8) @ vr.Rx(-pose.get('codo', 10) * D) @ vr.T(0, 0, 3.0)
    Mm = Mc @ vr.T(0, -L_ANTEBRAZO, 0) @ vr.Rx(-pose.get('mun', 0) * D)
    caja(out, Mh, -2.9, 2.9, -L_BRAZO, 1.6, -2.9, 2.9, piel, semilla=130)
    caja(out, Mh, -3.5, 3.5, -3.4, 2.8, -3.5, 3.5, piel, semilla=131)                                # el deltoide
    caja(out, Mc, -2.6, 2.6, -L_ANTEBRAZO, 0.0, -2.6, 2.6, piel, semilla=132)
    if cuerpo == 'piel':
        caja(out, Mh, -3.15, 3.15, -6.4, -4.6, -3.15, 3.15, P['oro'], semilla=133)                   # el brazalete
        caja(out, Mc, -2.95, 2.95, -L_ANTEBRAZO + 0.3, -L_ANTEBRAZO + 2.6, -2.95, 2.95, P['collar'], semilla=134)
    mano = jm.mano(out, Mm, s, 'bloque', P['piel'] if cuerpo == 'piel' else P['venda'], k=2.4, cierra=pose.get('cierra', 1.0))
    return mano, Mm


CADERA = np.array((3.5, 23.5, 0.0))
L_MUSLO, L_PIERNA = 11.5, 11.0


def pierna(out, P, s, pose, cuerpo='piel'):
    """Una pierna larga: el muslo, la rodilla que dobla por delante, la pierna y el pie con la sandalia de oro."""
    piel = P[cuerpo]
    Mt = vr.T(s * CADERA[0], CADERA[1], CADERA[2]) @ vr.Rz(s * pose.get('abd', 4) * D) @ vr.Rx(-pose.get('flex', 0) * D)
    Mr = Mt @ vr.T(0, -L_MUSLO, 2.8) @ vr.Rx(pose.get('rodilla', 5) * D) @ vr.T(0, 0, -2.5)
    Mp = (Mr @ vr.T(0, -L_PIERNA, 0) @ vr.Rx((pose.get('flex', 0) - pose.get('rodilla', 5)) * D) @ vr.Rz(-s * pose.get('abd', 4) * D))
    caja(out, Mt, -3.2, 3.2, -L_MUSLO, 1.2, -3.4, 3.0, piel, semilla=140)
    caja(out, Mr, -2.6, 2.6, -4.6, 0.0, -3.0, 2.6, piel, semilla=141)
    caja(out, Mr, -2.2, 2.2, -L_PIERNA, -4.5, -2.4, 2.4, piel, semilla=142)
    caja(out, Mp, -2.1, 2.1, -1.6, 0.4, -2.4, 4.6, P['piel'] if cuerpo == 'piel' else P['venda'], semilla=143)   # el pie
    caja(out, Mp, -2.2, 2.2, -1.8, -1.3, -2.5, 4.8, P['oro'], semilla=144)                           # la sandalia
    caja(out, Mp, -2.25, 2.25, -0.6, -0.1, 1.0, 1.6, P['oro'], semilla=145)
    return Mp


# ----------------------------------------------------------------------
#  Lo de cada forma
# ----------------------------------------------------------------------
def balanza(out, P, puno):
    """A: la balanza del juicio, colgando del puno: el astil de rayas, la cruz con sus remates, las cadenas y los
    dos platillos: en uno, el corazon encendido; en el otro, la pluma de Maat. Devuelve el punto del corazon."""
    p = np.asarray(puno, float)
    caja(out, vr.T(*p), -0.45, 0.45, -1.0, 9.0, -0.45, 0.45, P['nemes_largo'], semilla=150)        # el astil
    cruz = p + np.array((0.0, 9.0, 0.0))
    caja(out, vr.T(*cruz), -7.0, 7.0, -0.4, 0.4, -0.4, 0.4, P['oro'], semilla=151)
    caja(out, vr.T(*cruz), -1.0, 1.0, -0.8, 1.6, -0.8, 0.8, P['oro'], semilla=152)
    corazon = None
    for s in (1, -1):
        cabo = cruz + np.array((s * 6.6, 0.0, 0.0))
        caja(out, vr.T(*cabo), -0.6, 0.6, -0.6, 0.6, -0.6, 0.6, P['oro'], semilla=153)
        plato = cabo + np.array((0.0, -9.0, 0.0))
        for dx in (-1.6, 1.6):                                                                       # las cadenas
            cadena(out, cabo, plato + np.array((dx, 0.4, 0.0)), 0.9, P['oro'], semilla=154)
        caja(out, vr.T(*plato), -2.4, 2.4, -0.5, 0.2, -2.4, 2.4, P['oro'], semilla=155)            # el platillo
        caja(out, vr.T(*plato), -1.8, 1.8, -0.9, -0.4, -1.8, 1.8, P['oro'], semilla=155)
        if s < 0:                                                                                    # el corazon
            M = vr.T(*(plato + np.array((0.0, 1.4, 0.0))))
            caja(out, M, -1.2, 1.2, -1.0, 1.0, -0.9, 0.9, P['luz'], semilla=156)
            caja(out, M, -0.7, 0.7, 0.9, 1.6, -0.6, 0.6, P['luz'], semilla=156)
            corazon = pt(M, (0.0, 0.0, 0.0))
        else:                                                                                        # la pluma de Maat
            M = vr.T(*(plato + np.array((0.0, 0.2, 0.0)))) @ vr.Rz(-8 * D)
            caja(out, M, -0.9, 0.9, 0.0, 5.0, -0.25, 0.25, P['pluma'], semilla=157)
            caja(out, M, -0.6, 0.6, 5.0, 6.2, -0.22, 0.22, P['pluma'], semilla=157)
            caja(out, M @ vr.T(0.4, 6.0, 0.0) @ vr.Rz(-40 * D), -0.4, 0.4, 0.0, 1.2, -0.2, 0.2, P['pluma'], semilla=157)
    return corazon


def cetro_uas(out, P, puno, alto=40.0):
    """A: el cetro uas, derecho por el puno: el asta de rayas, la horquilla de abajo y la cabeza de la bestia de
    Set arriba, de oro."""
    M = vr.T(*np.asarray(puno, float))
    caja(out, M, -0.5, 0.5, -16.0, alto - 16.0, -0.5, 0.5, P['nemes_largo'], semilla=160)
    for s in (1, -1):                                                                                # la horquilla
        x0, x1 = sorted((s * 0.2, s * 1.4))
        caja(out, M, x0, x1, -18.5, -15.8, -0.45, 0.45, P['oro'], semilla=161)
    Mt = M @ vr.T(0, alto - 16.0, 0)
    caja(out, Mt, -0.7, 0.7, 0.0, 1.6, -0.7, 0.7, P['oro'], semilla=162)
    caja(out, Mt @ vr.Rx(-60 * D), -0.6, 0.6, 0.0, 3.6, -0.6, 0.6, P['oro'], semilla=163)          # la cabeza de Set
    caja(out, Mt @ vr.T(0, 1.4, 1.8) @ vr.Rx(10 * D), -0.45, 0.45, 0.0, 1.6, -0.35, 0.35, P['oro'], semilla=164)


def jopesh(out, P, Mm, s):
    """B: la espada jopesh, que sigue al brazo desde el puno: la empunadura de oro, el tramo recto de bronce y la
    hoz que se curva hacia fuera, con el filo claro."""
    p = pt(Mm, (0, -2.4, 0))
    d = _u(-Mm[:3, 1])
    M = em.marco(p, d, up=Mm[:3, 2])
    caja(out, M, -0.45, 0.45, -0.45, 0.45, -1.0, 2.6, P['oro'], semilla=170)                        # la empunadura
    caja(out, M, -0.6, 0.6, -0.6, 0.6, 2.4, 3.0, P['oro'], semilla=170)
    caja(out, M, -0.32, 0.32, -1.2, 0.7, 3.0, 9.0, P['bronce'], semilla=171)                       # el tramo recto
    Mk = M @ vr.T(0, 0, 9.0)
    for j in range(4):                                                                              # la hoz
        Mk = Mk @ vr.Rx(-30 * D)
        caja(out, Mk, -0.3, 0.3, -2.0, 0.5, -0.1, 2.5, P['filo'], semilla=172 + j % 2)
        Mk = Mk @ vr.T(0, 0, 2.4)


def cayado_y_mayal(out, P, centro):
    """C: el cayado y el mayal cruzados sobre el pecho, con rayas de oro y lapislazuli: el cayado con su gancho y
    el mayal con sus tres ramales."""
    c = np.asarray(centro, float)
    for s, cosa in ((1, 'cayado'), (-1, 'mayal')):
        M = vr.T(*c) @ vr.Rz(s * 38 * D)
        caja(out, M, -0.45, 0.45, -7.0, 7.0, -0.45, 0.45, P['nemes_largo'], semilla=180)
        Mt = M @ vr.T(0, 7.0, 0)
        if cosa == 'cayado':
            caja(out, Mt, -0.45, 0.45, 0.0, 2.2, -0.45, 0.45, P['oro'], semilla=181)
            caja(out, Mt @ vr.T(0, 2.2, 0), -2.6, 0.45, -0.45, 0.45, -0.45, 0.45, P['oro'], semilla=181)
            caja(out, Mt @ vr.T(-2.4, 2.2, 0), -0.45, 0.45, -1.8, 0.0, -0.45, 0.45, P['oro'], semilla=181)
        else:
            for k in range(3):
                Mr = Mt @ vr.T(0, 0.5, 0) @ vr.Rz((-20 + 20 * k) * D)
                for j in range(4):
                    caja(out, Mr, -0.35, 0.35, j * 1.3, j * 1.3 + 1.1, -0.35, 0.35, P['collar'], semilla=182)


def anj(out, P, centro):
    """C: el anj encendido sobre el vientre."""
    M = vr.T(*np.asarray(centro, float))
    caja(out, M, -0.5, 0.5, -4.0, 0.6, -0.3, 0.3, P['luz'], semilla=190)
    caja(out, M, -2.0, 2.0, 0.0, 0.8, -0.3, 0.3, P['luz'], semilla=190)
    for (x0, x1, y0, y1) in ((-1.4, -0.7, 0.8, 3.0), (0.7, 1.4, 0.8, 3.0), (-1.0, 1.0, 2.8, 3.4)):
        caja(out, M, x0, x1, y0, y1, -0.3, 0.3, P['luz'], semilla=190)


# ======================================================================
#  ANUBIS
# ======================================================================
POSES = {
    'A': dict(brazos={-1: dict(abd=48, flex=34, codo=50, giro=-10, cierra=1.0),
                      1: dict(abd=16, flex=18, codo=72, giro=10, cierra=1.0)},
              piernas={1: dict(abd=6, flex=-6, rodilla=6), -1: dict(abd=6, flex=10, rodilla=12)},
              cabeza=(8, 0), encorva=2.0),
    'B': dict(brazos={-1: dict(abd=34, flex=40, codo=34, giro=-20, cierra=1.0),
                      1: dict(abd=40, flex=24, codo=48, giro=20, cierra=1.0)},
              piernas={1: dict(abd=10, flex=-28, rodilla=20), -1: dict(abd=9, flex=40, rodilla=64)},
              cabeza=(-6, 0), encorva=30.0),
    'C': dict(brazos={-1: dict(abd=8, flex=62, codo=100, giro=-58, cierra=1.0),
                      1: dict(abd=8, flex=62, codo=100, giro=58, cierra=1.0)},
              cabeza=(10, 0), encorva=0.0),
}


def anubis(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    pose = POSES[tipo]
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    luces = []
    try:
        cuerpo = 'venda' if tipo == 'C' else 'piel'
        arriba = []
        torso(arriba, P, cuerpo=cuerpo)
        collar(arriba, P)
        manos = {}
        for s in (1, -1):
            manos[s] = brazo(arriba, P, s, pose['brazos'][s], cuerpo=cuerpo)
        if tipo == 'B':                                                 # la crin negra de la bestia
            caja(arriba, jm.I4, -4.6, 4.6, 40.0, 47.0, -4.8, -1.2, P['pelaje'], semilla=200)
            caja(arriba, jm.I4, -3.4, 3.4, 33.0, 41.0, -5.2, -4.0, P['pelaje'], semilla=201)
            for s in (1, -1):
                jopesh(arriba, P, manos[s][1], s)
        tx, tz = pose['cabeza']
        Mh = vr.T(0.0, 45.4, 1.6) @ vr.Rx(tx * D) @ vr.Rz(tz * D) @ np.diag([CABEZA] * 3 + [1.0])
        bm.PPB = PPB / CABEZA
        luz = cabeza(arriba, Mh, P, abierta=(tipo == 'B'), vendada=(tipo == 'C'))
        bm.PPB = PPB
        luces.append(luz)
        if tipo == 'A':
            corazon = balanza(arriba, P, pt(manos[-1][1], (0, -2.6, 0)))
            luces.append(corazon)
            cetro_uas(arriba, P, pt(manos[1][1], (0, -2.6, 0)))
        if tipo == 'C':
            cayado_y_mayal(arriba, P, (0.0, 37.0, 9.0))
            anj(arriba, P, (0.0, 30.0, 3.7))
            luces.append(np.array((0.0, 30.0, 6.0)))
        enc = pose.get('encorva', 0.0)
        Mt = vr.T(0, 24.0, 0) @ vr.Rx(enc * D) @ vr.T(0, -24.0, 0)
        out += qm.transformar(arriba, Mt)
        luces = [pt(Mt, l) for l in luces]
        if tipo == 'C':                                                 # la momia: las piernas atadas, flotando
            for y0, y1, g in ((14.0, 23.0, 5.0), (7.0, 14.4, 4.2), (1.0, 7.4, 3.4)):
                caja(out, jm.I4, -g, g, y0, y1, -g * 0.75, g * 0.75, P['venda'], semilla=210)
            caja(out, jm.I4, -2.6, 2.6, -0.4, 1.2, -1.8, 3.2, P['venda'], semilla=211)
            import tanara_modelo as tm
            for k, (x, y) in enumerate(((4.4, 19.0), (-4.0, 12.0), (3.0, 6.0), (-5.6, 30.0), (5.8, 34.0))):
                tm.cinta(out, P, (x, y, 1.0), 8.0 + 2.0 * (k % 3), ancho=1.4, ola=1.0, fase=k * 1.3, semilla=212)
        else:
            faldellin(out, P)
            for s in (1, -1):
                pierna(out, P, s, pose['piernas'][s])
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    sube = 5.0 if tipo == 'C' else 0.0                                  # la momia flota
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0 + sube, 0)
    out = qm.transformar(out, E)
    luces = [pt(E, l) for l in luces]
    return out, {'boca': luces[0], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

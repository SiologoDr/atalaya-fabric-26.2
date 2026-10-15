"""
Mantara y sus formas (14-10-2026). Juan: «sigamos con lo que estabamos haciendo antes: hacer un boss y sus 3 tipos
sin un objetivo o algo en concreto». Elegido con libertad.

Una quimera inventada: la Dragona Mantis. El cuerpo de una mantis (el torax alzado como un torso, cuatro patas de
andar en hoja con las rodillas por encima del lomo y el abdomen largo en segmentos), alas que le salen de los
hombros y la cabeza de mantis a su proporcion (Juan, 14-10: «la cara es muy grotesca, muy grande; si es una mantis
tiene que tener rasgos»): en triangulo, con los ojos compuestos abombados en las esquinas, que arden en facetas con
su seudopupila, los tres ocelos encendidos, los palpos, las mandibulas pequenas y las antenas. Lleva dos guadanas
enormes, con su fila de pinchos claros. Se ve de frente: las guadanas y las alas enmarcan la cabeza.
Todo de cajas y laminas, con texturas limpias (bandas de quitina, venas en las alas, petalos en bandas).

Las tres formas cambian la silueta:

    A  la Segadora     las guadanas alzadas a los lados de la cabeza, como dos hoces; las alas plegadas, colgando
                       de los hombros como un manto con el canto encendido; naranja
    B  la Desplegada   la amenaza: las alas abiertas en dos abanicos enormes detras de la cabeza, con un ocelo y el
                       borde encendidos; las guadanas alzadas y abiertas a los lados, como dos hojas; rojo
    C  la Orquidea     el disfraz de flor: cinco petalos enormes detras de la cabeza, el manto y los lobulos de las
                       patas de petalo, las guadanas plegadas delante del pecho y el abdomen enroscado; rosa
"""
import math
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _degradado, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.6
CABEZA = 1.25

DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')
VARIANTES = {
    'A': dict(
        clave='A', nombre='la Segadora', corto='segadora',
        quitina=_r('0a0c06', '12160c', '1c2212', '28301a', '364024'),
        placa=_r('0c0e08', '161a0e', '222816', '30381e', '424c2a'),
        membrana=_r('0a0c06', '12160c', '1a2010', '262e18', '343e22'),
        espina=_r('5a5a3a', '86865a', 'b0b080', 'd6d6aa', 'f2f2d0'),
        petalo=_r('0c0e08', '161a0e', '222816', '30381e', '424c2a'),
        neon=('fff2dc', 'ff8a1e', '6a2a02'),
    ),
    'B': dict(
        clave='B', nombre='la Desplegada', corto='desplegada',
        quitina=_r('100806', '1c0e0a', '2a1410', '3a1c16', '50281e'),
        placa=_r('140a08', '22120e', '321c16', '44261e', '5c3428'),
        membrana=_r('0e0808', '1a0e0e', '281616', '382020', '4c2c2c'),
        espina=_r('5e5040', '8a7a62', 'b4a488', 'd8caae', 'f4ead2'),
        petalo=_r('140a08', '22120e', '321c16', '44261e', '5c3428'),
        neon=('ffe4e0', 'ff3a2a', '6a0a04'),
    ),
    'C': dict(
        clave='C', nombre='la Orquidea', corto='orquidea',
        quitina=_r('120a10', '1e1018', '2c1824', '3c2232', '502e44'),
        placa=_r('160c14', '24121e', '341c2c', '46263c', '5c3450'),
        membrana=_r('120a10', '1e1018', '2c1824', '3c2232', '502e44'),
        espina=_r('8a6a7e', 'b490a8', 'd6b4ca', 'eed2e2', 'fceef6'),
        petalo=_r('8a2a64', 'b8488e', 'd878b2', 'f0aad2', 'fde0f0'),
        neon=('fff0fa', 'ff4ac0', '6a0a4a'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'man%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def quitina(tw, th, cara, s):
        """La quitina: placas lisas con el canto en bisel y una veta clara a lo largo."""
        largo_x = tw >= th
        n_l, n_a = (tw, th) if largo_x else (th, tw)
        idx = np.full((n_a, n_l), 2)
        if n_a >= 4:
            idx[n_a // 2, :] = 3
        if not largo_x:
            idx = idx.T
        return _imagen(_bisel(idx, 1, 1), V['quitina']), None
    reg('quitina', quitina)

    def placa(tw, th, cara, s):
        """Los segmentos: bandas de traves con la junta oscura y el canto claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys % 5) == 0, 1, np.where((ys % 5) == 1, 3, 2))
        return _imagen(idx, V['placa']), None
    reg('placa', placa)

    def membrana(tw, th, cara, s):
        """El ala: oscura, en bandas a lo largo, con las venas claras de traves cada tanto."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 3) % 2 == 0, 2, 1)
        idx = np.where((xs % 6) == 0, 3, idx)
        idx = np.where((ys % 11) == 0, 3, idx)
        return _imagen(idx, V['membrana']), None
    reg('membrana', membrana)
    reg('espina', jm.liso(V['espina'], 3, 1, 1))
    reg('pupila', jm.liso(_r('060608', '0a0a0e', '101014', '16161c', '1e1e26'), 2, 1, 1))

    def facetas(tw, th, cara, s):
        """El ojo compuesto: facetas de 2 pixeles del neon, con la junta mas oscura y las filas corridas, como un
        panal; mas claro hacia el centro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        borde = ((xs + (ys // 2) % 2) % 2 == 0) & (ys % 2 == 0)
        cy, cx = (th - 1) / 2, (tw - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        medio = np.array(qm._mezcla(c_h, c_m, 0.72))
        col = np.where(borde[..., None], medio, np.array(c_m))
        col = np.where(((r < 0.4) & ~borde)[..., None], np.array(qm._mezcla(c_m, c_n, 0.25)), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, np.ones((th, tw), bool), 120)
    reg('ojo', facetas)

    def petalo(tw, th, cara, s):
        """Los petalos (pintados de traves sobre la lamina): claros en el centro y mas oscuros hacia los cantos,
        en bandas limpias, con estrias finas a lo largo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        u = np.abs((xs + 0.5) / tw - 0.5) * 2
        idx = np.where(u < 0.3, 4, np.where(u < 0.6, 3, np.where(u < 0.85, 2, 1)))
        idx = np.where(((xs % 4) == 0) & (u >= 0.3), idx - 1, idx)
        return _imagen(np.clip(idx, 0, 4), V['petalo']), None
    reg('petalo', petalo)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def nucleo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((r < 0.45)[..., None], np.array(c_n),
                       np.where((r < 0.8)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m)))
        col = np.where((r > 1.0)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 1.0, 240)
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
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, DIENTES, True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, DIENTES, False))
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def _u(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    """Una hilera de dientes dibujados en hojas, por las caras de un poligono (en el plano y del marco M)."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado, h = float(np.linalg.norm(B - A)), float(np.linalg.norm(A2 - A))
        if alto < 0:
            lamina(out, (A2, B2, B, A), pintor, lado, h, semilla + j)
        else:
            lamina(out, (A, B, B2, A2), pintor, lado, h, semilla + j)


def pua(out, p, d, r, h, pintor, semilla=0):
    M = em.marco(np.asarray(p, float), np.asarray(d, float))
    caja(out, M, -r, r, -r, r, -0.4, h * 0.45, pintor, semilla=semilla)
    caja(out, M, -r * 0.64, r * 0.64, -r * 0.64, r * 0.64, h * 0.4, h * 0.76, pintor, semilla=semilla + 1)
    caja(out, M, -r * 0.32, r * 0.32, -r * 0.32, r * 0.32, h * 0.72, h, pintor, semilla=semilla + 2)


def petalo(out, P, base, d, n, largo, ancho, curva=0.0, semilla=0):
    """Un petalo (o un lobulo): una hoja fina de cara a n, estrecha en la base, ancha por el medio y con la punta
    redonda; se curva hacia n como una cuchara (curva, en bloques en la punta), con el nervio en medio."""
    base, d, n = np.asarray(base, float), _u(d), _u(n)
    n = _u(n - d * (n @ d))
    x = np.cross(n, d)
    perfil = ((0.0, 0.18), (0.25, 0.8), (0.55, 1.0), (0.8, 0.85), (0.93, 0.55), (1.0, 0.12))
    m = 8
    filas = []
    for k in range(m + 1):
        t = k / m
        w = float(np.interp(t, [a for a, _ in perfil], [b for _, b in perfil])) * ancho / 2
        c = base + d * (t * largo) + n * (curva * t * t)
        filas.append((c - x * w, c, c + x * w))
    for k in range(m):
        (a0, _, b0), (a1, _, b1) = filas[k], filas[k + 1]
        L = float(np.linalg.norm(filas[k + 1][1] - filas[k][1]))
        W_ = max(float(np.linalg.norm(b0 - a0)), float(np.linalg.norm(b1 - a1)), 0.5)
        lamina(out, (a0, b0, b1, a1), P['petalo'], W_, L, semilla=semilla)
        lamina(out, (a1, b1, b0, a0), P['petalo'], W_, L, semilla=semilla)
    jm.tubo(out, [f[1] for f in filas[:-1]], [0.35] * m, [P['espina']] * (m - 1), semilla=semilla + 1)   # el nervio


def cabeza(out, Mh, P, tipo):
    """La cabeza de mantis, de cara a +z, en triangulo y a su proporcion: arriba, en las esquinas, los dos ojos
    compuestos, grandes y abombados, en lagrima hacia arriba y afuera, que arden en facetas con su seudopupila
    oscura; entre ellos, la frente con los tres ocelos encendidos; abajo, el escudo de la cara (frente y clipeo) y
    las mejillas que bajan en V hasta la boca, pequena, en la punta: el labro, las dos mandibulas que se cruzan y la
    luz entre ellas; y a los lados de la boca, los palpos articulados que cuelgan. Devuelve la boca y los ojos."""
    q = P['quitina']
    caja(out, Mh, -4.4, 4.4, 1.4, 3.4, -2.6, 0.8, q, semilla=1)                                        # el vertice
    caja(out, Mh, -1.2, 1.2, 3.2, 3.9, -2.2, 0.2, P['placa'], semilla=2)
    ojos = []
    for s in (1, -1):                                                                                  # los ojos compuestos
        Mo = Mh @ vr.T(s * 5.0, 2.2, -0.7) @ vr.Rz(-s * 20 * D)
        caja(out, Mo, -1.9, 1.9, -2.0, 2.0, -1.6, 1.6, P['ojo'], semilla=3)
        caja(out, Mo, -1.5, 1.5, -2.6, 2.6, -1.3, 1.3, P['ojo'], semilla=3)
        caja(out, Mo, -1.4, 1.4, -1.6, 1.6, -2.0, 2.0, P['ojo'], semilla=3)
        caja(out, Mo, -0.9, 0.9, 2.4, 3.5, -0.9, 0.9, P['ojo'], semilla=3)                             # la punta de la lagrima
        caja(out, Mo, -s * 0.05 - 0.25, -s * 0.05 + 0.25, -0.1, 0.5, 1.95, 2.08, P['pupila'], semilla=4)  # la seudopupila
        ojos.append(pt(Mo, (0.0, 0.0, 2.4)))
    for k, (x, y) in enumerate(((0.0, 2.7), (-0.75, 2.0), (0.75, 2.0))):                               # los tres ocelos
        r = 0.32 if k else 0.38
        caja(out, Mh, x - r, x + r, y - r, y + r, 0.6, 0.95, P['luz'], semilla=5)
    caja(out, Mh, -2.6, 2.6, -0.4, 1.6, -2.0, 1.0, q, semilla=6)                                       # la frente
    caja(out, Mh, -1.9, 1.9, -1.9, -0.3, -1.8, 1.2, P['placa'], semilla=6)                             # el clipeo
    for s in (1, -1):                                                                                  # las mejillas, en V
        Mc = Mh @ vr.T(s * 2.9, -0.5, -0.8) @ vr.Rz(-s * 36 * D)
        caja(out, Mc, -0.9, 0.9, -2.3, 2.2, -1.4, 1.0, q, semilla=7)
    caja(out, Mh, -1.3, 1.3, -2.9, -1.8, -1.2, 1.3, q, semilla=8)                                      # el labro
    caja(out, Mh, -0.8, 0.8, -3.7, -2.8, -0.9, 0.7, P['luz'], semilla=9)                               # la luz de la boca
    for s in (1, -1):                                                                                  # las mandibulas
        Mm = Mh @ vr.T(s * 1.0, -2.8, 0.4) @ vr.Rz(s * 28 * D)
        caja(out, Mm, -0.45, 0.45, -1.4, 0.0, -0.5, 0.5, q, semilla=10)
        caja(out, Mm @ vr.T(0, -1.3, 0) @ vr.Rz(s * 38 * D), -0.3, 0.3, -1.0, 0.0, -0.35, 0.35, q, semilla=10)
    for s in (1, -1):                                                                                  # los palpos
        p0 = pt(Mh, (s * 1.7, -2.6, 0.6))
        d = Mh[:3, :3] @ np.array((s * 0.35, -1.0, 0.45))
        for k, (L, r) in enumerate(((1.4, 0.32), (1.2, 0.28), (1.0, 0.25))):
            M = em.marco(p0, d)
            caja(out, M, -r, r, -r, r, -0.1, L, P['placa'] if k % 2 else q, semilla=11)
            p0 = pt(M, (0.0, 0.0, L))
            d = M[:3, :3] @ np.array((-s * 0.2, 0.0, 1.0)) + Mh[:3, :3] @ np.array((0.0, -0.5, 0.0))
    return pt(Mh, (0.0, -3.3, 1.0)), ojos


def antenas(out, P, Mh, largo=17.0):
    """Las antenas: dos hilos largos que salen de entre los ojos, suben y se curvan hacia atras."""
    for s in (1, -1):
        base = pt(Mh, (s * 0.7, 2.6, 0.7))
        sube = Mh[:3, :3] @ np.array((s * 0.4, 1.0, 0.2))
        sube = _u(sube)
        ctrl = [base, base + sube * 3.0, base + np.array((s * 4.0, largo * 0.55, -2.0)), base + np.array((s * 8.0, largo * 0.8, -9.0))]
        pts, rs, ts = jm.a_lo_largo([np.asarray(c, float) for c in ctrl], 10, ((0.0, 0.5), (1.0, 0.2)))
        jm.tubo(out, pts, rs, [P['quitina']] * (len(pts) - 1), semilla=11)


def guadana(out, P, hombro, codo, rodilla, adentro, abre, lobulos=False, semilla=0):
    """Una pata de rapina: la coxa (del hombro al codo); el femur, una hoja ancha del codo a la rodilla con una
    fila de pinchos claros por el lado de 'adentro'; la tibia, que sale de la rodilla y se pliega contra los
    pinchos (abre: los grados que se separa del femur; 180 es plegada del todo), con su fila de pinchos; y la
    garra curva de la punta."""
    hombro, codo, rodilla = (np.asarray(p, float) for p in (hombro, codo, rodilla))
    jm.tubo(out, [hombro, codo], [2.0, 1.8], [P['quitina']], semilla=semilla)                         # la coxa
    caja(out, vr.T(*codo), -2.0, 2.0, -2.0, 2.0, -2.0, 2.0, P['quitina'], semilla=semilla + 1)
    d = _u(rodilla - codo)
    L = float(np.linalg.norm(rodilla - codo))
    M = em.marco(codo, d, up=-_u(adentro))                                                             # +y: el lomo del femur
    caja(out, M, -1.0, 1.0, -1.4, 1.6, -0.4, L + 0.6, P['quitina'], semilla=semilla + 2)              # el femur, hoja
    caja(out, M, -0.7, 0.7, 1.4, 2.6, 0.8, L - 0.8, P['placa'], semilla=semilla + 3)                   # su lomo
    for j in range(7):                                                                                 # sus pinchos
        t = 0.12 + 0.12 * j
        pua(out, pt(M, (0.0, -1.3, L * t)), M[:3, :3] @ np.array((0.0, -1.0, 0.3)), 0.38, 2.4 + (j % 2) * 1.2,
            P['espina'], semilla=semilla + 4)
    if lobulos:                                                                                        # el lobulo de petalo
        petalo(out, P, pt(M, (0.0, 2.2, L * 0.15)), M[:3, :3] @ np.array((0.0, 0.45, 1.0)), M[:3, :3] @ np.array((1.0, 0.0, 0.0)),
               L * 0.8, 5.0, curva=-2.0, semilla=semilla + 5)
    caja(out, M, -1.3, 1.3, -1.6, 1.8, L - 0.6, L + 1.4, P['quitina'], semilla=semilla + 6)            # la rodilla
    Mt = M @ vr.T(0, -1.6, L + 0.4) @ vr.Rx(abre * D)                                                  # la tibia
    Lt = L * 0.72
    caja(out, Mt, -0.8, 0.8, -0.9, 1.1, -0.3, Lt, P['quitina'], semilla=semilla + 7)
    for j in range(5):
        pua(out, pt(Mt, (0.0, 1.0, Lt * (0.15 + 0.17 * j))), Mt[:3, :3] @ np.array((0.0, 1.0, 0.3)), 0.3, 1.8, P['espina'],
            semilla=semilla + 8)
    Mg = Mt @ vr.T(0, 0, Lt) @ vr.Rx(-38 * D)                                                          # la garra
    caja(out, Mg, -0.55, 0.55, -0.55, 0.55, -0.2, 2.4, P['espina'], semilla=semilla + 9)
    caja(out, Mg @ vr.T(0, 0, 2.2) @ vr.Rx(-40 * D), -0.35, 0.35, -0.35, 0.35, -0.1, 1.8, P['espina'], semilla=semilla + 9)


def pata(out, P, cadera, rodilla, pie, lobulos=False, semilla=0):
    """Una pata de andar en hoja: el femur, una hoja alta y plana que sube hasta la rodilla, por encima del lomo,
    con su cresta y una fila de pinchos por debajo; la tibia, otra hoja mas fina que baja al suelo; y el tarso de
    tres artejos que acaba en una una."""
    cadera, rodilla, pie = (np.asarray(p, float) for p in (cadera, rodilla, pie))
    fuera = _u(np.array((rodilla[0], 0.0, 0.0)))
    d = rodilla - cadera
    L = float(np.linalg.norm(d))
    M = em.marco(cadera, d, up=(0.0, 1.0, 0.0))
    caja(out, M, -1.1, 1.1, -2.0, 2.2, -0.6, L + 0.6, P['quitina'], semilla=semilla)                  # el femur
    caja(out, M, -0.7, 0.7, 2.0, 3.0, 1.0, L - 1.2, P['placa'], semilla=semilla + 1)                   # su cresta
    for t in (0.35, 0.55, 0.75):
        pua(out, pt(M, (0.0, -1.9, L * t)), M[:3, :3] @ np.array((0.0, -1.0, -0.4)), 0.32, 1.8, P['espina'], semilla=semilla + 2)
    caja(out, vr.T(*rodilla), -1.8, 1.8, -1.8, 1.8, -1.8, 1.8, P['quitina'], semilla=semilla + 3)      # la rodilla
    fin = pie + np.array((0.0, 1.8, 0.0))
    d2 = fin - rodilla
    L2 = float(np.linalg.norm(d2))
    M2 = em.marco(rodilla, d2, up=fuera)
    caja(out, M2, -1.1, 1.1, -1.7, 1.7, 0.0, L2, P['quitina'], semilla=semilla + 4)                    # la tibia
    caja(out, M2, -0.6, 0.6, 1.4, 2.2, 1.0, L2 - 1.5, P['placa'], semilla=semilla + 5)
    for t in (0.3, 0.55):
        pua(out, pt(M2, (0.0, 1.6, L2 * t)), M2[:3, :3] @ np.array((0.0, 1.0, 0.5)), 0.3, 1.8, P['espina'], semilla=semilla + 6)
    adelante = _u(np.array((fin[0] - cadera[0], 0.0, fin[2] - cadera[2])))
    Mt = em.marco(fin, adelante + np.array((0.0, -1.6, 0.0)))
    for j, Lt in enumerate((1.6, 1.4, 1.2)):
        caja(out, Mt, -0.7, 0.7, -0.7, 0.7, 0.0, Lt, P['quitina'], semilla=semilla + 7)
        Mt = Mt @ vr.T(0, 0, Lt) @ vr.Rx(12 * D)
    caja(out, Mt, -0.45, 0.45, -0.45, 0.45, 0.0, 1.2, P['quitina'], semilla=semilla + 8)
    if lobulos:                                                                                        # el lobulo de petalo
        petalo(out, P, pt(M, (0.0, 2.4, L * 0.3)), _u(d) * 0.5 + fuera * 0.7 + np.array((0.0, 0.3, 0.0)),
               np.array((0.0, 1.0, 0.6)), L * 1.1, 9.0, curva=-2.0, semilla=semilla + 9)


def manto(out, P, raiz, s, largo, ancho, pintor, borde=True, semilla=0):
    """Un ala plegada que cuelga del hombro como la mitad de un manto: baja por detras hasta el suelo, el canto
    de dentro junto al lomo y el de fuera abierto hacia el lado y un poco hacia delante, de modo que de frente
    se ve detras del torso; las venas a lo largo y, si borde, el canto libre encendido."""
    raiz = np.asarray(raiz, float)
    perfil = ((0.0, 0.3), (0.25, 0.8), (0.6, 1.0), (0.9, 0.9), (1.0, 0.55))
    n = 9
    filas = []
    for k in range(n + 1):
        t = k / n
        w = float(np.interp(t, [a for a, _ in perfil], [b for _, b in perfil])) * ancho
        c = raiz + np.array((s * (0.6 + 2.0 * t), -t * largo * 0.86, -1.5 - t * largo * 0.42 - t * t * 4.0))
        fuera = c + np.array((s * w * 0.88, -w * 0.12, w * 0.28))
        filas.append((c, fuera))
    for k in range(n):
        (a0, b0), (a1, b1) = filas[k], filas[k + 1]
        L = float(np.linalg.norm(a1 - a0))
        Wd = float(np.linalg.norm(b0 - a0)) + 0.5
        lamina(out, (a0, b0, b1, a1), pintor, Wd, L, semilla=semilla)
        lamina(out, (a1, b1, b0, a0), pintor, Wd, L, semilla=semilla)
    for f in (0.35, 0.7):                                                                              # las venas
        jm.tubo(out, [a + (b - a) * f for a, b in filas], [0.3] * (n + 1), [P['quitina']] * n, semilla=semilla + 1)
    jm.tubo(out, [f[0] for f in filas], [0.6] * (n + 1), [P['quitina']] * n, semilla=semilla + 1)       # el canto de dentro
    jm.tubo(out, [f[1] for f in filas], [0.45] * (n + 1), [P['luz'] if borde else P['quitina']] * n, semilla=semilla + 2)
    jm.tubo(out, [filas[-1][0], filas[-1][1]], [0.45, 0.45], [P['luz'] if borde else P['quitina']], semilla=semilla + 2)


def ala_abierta(out, P, raiz, s, largos, ocelos=True, semilla=0):
    """El ala de la amenaza: un abanico de venas que sale de la raiz, la membrana en bandas entre cada dos, el
    borde libre encendido y, en medio, un ocelo (un ojo falso en anillos que arde). Devuelve el centro del ocelo."""
    raiz = np.asarray(raiz, float)
    angs = np.linspace(4 * D, 125 * D, len(largos))
    dirs = [np.array((s * math.sin(a), math.cos(a), -0.28)) for a in angs]
    puntas = [raiz + _u(d) * L for d, L in zip(dirs, largos)]
    for p in puntas:
        jm.tubo(out, [raiz, p], [0.6, 0.3], [P['quitina']], semilla=semilla)
    for i in range(len(puntas) - 1):
        a0, a1 = raiz + _u(dirs[i]) * 1.2, raiz + _u(dirs[i + 1]) * 1.2
        b0, b1 = puntas[i], puntas[i + 1]
        ancho = max(float(np.linalg.norm(b1 - b0)), 0.5)
        alto = max(float(np.linalg.norm(b0 - a0)), 0.5)
        lamina(out, (a0, a1, b1, b0), P['membrana'], ancho, alto, semilla=semilla + 1)
        lamina(out, (b0, b1, a1, a0), P['membrana'], ancho, alto, semilla=semilla + 1)
    jm.tubo(out, puntas, [0.4] * len(puntas), [P['luz']] * (len(puntas) - 1), semilla=semilla + 2)  # el borde encendido
    k = len(puntas) // 2
    c = raiz + (puntas[k] - raiz) * 0.6
    n_v = np.array((0.0, 0.0, 1.0))
    if ocelos:
        M = em.marco(c + n_v * 0.3, n_v)
        for r, pin in ((3.6, P['quitina']), (2.7, P['luz']), (1.6, P['quitina']), (0.8, P['luz'])):
            for w, h in ((r, r * 0.42), (r * 0.42, r), (r * 0.72, r * 0.72)):
                caja(out, M, -w, w, -h, h, 0.0, 0.2 + (3.6 - r) * 0.1, pin, semilla=semilla + 3)
    return c


# ======================================================================
#  MANTARA
# ======================================================================
def mantara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    luces = []
    try:
        lob = (tipo == 'C')
        W = np.array((0.0, 9.0, -1.0))                                   # el torax de las patas
        # el abdomen: largo, en segmentos y ancho; en la Orquidea se enrosca hacia arriba
        if tipo == 'C':
            ctrl = [W + np.array((0.0, 0.0, -2.0)), W + np.array((0.0, -2.0, -11.0)), W + np.array((0.0, -1.0, -20.0)),
                    W + np.array((0.0, 6.0, -26.0)), W + np.array((0.0, 13.0, -24.0))]
        else:
            ctrl = [W + np.array((0.0, 0.0, -2.0)), W + np.array((0.0, -2.0, -11.0)), W + np.array((0.0, -4.0, -20.0)),
                    W + np.array((0.0, -6.0, -27.0)), W + np.array((0.0, -5.0, -32.0))]
        pts, rs, ts = jm.a_lo_largo(ctrl, 11, ((0.0, 4.0), (0.3, 5.6), (0.6, 5.0), (0.85, 3.2), (1.0, 1.4)))
        jm.tubo(out, pts, rs, [P['placa']] * (len(pts) - 1), semilla=100, achata=0.8)
        for j in range(1, len(pts) - 1):                                                               # los anillos
            M = em.marco(pts[j], pts[j + 1] - pts[j - 1], up=(0.0, 1.0, 0.0))
            g = rs[j] * 1.06
            caja(out, M, -g, g, -g * 0.82, g * 0.82, -0.3, 0.3, P['quitina'], semilla=101)
        for s in (1, -1):                                                                              # los cercos
            pua(out, pts[-1], _u(pts[-1] - pts[-2]) + np.array((s * 0.5, 0.2, 0.0)), 0.5, 3.6, P['espina'], semilla=102)
        jm.tubo(out, [W + np.array((0.0, 0.0, -3.0)), W + np.array((0.0, 0.8, 4.0))], [4.2, 3.6], [P['quitina']] * 1, semilla=103)
        # el protorax, alzado como un torso, con su cresta de pinchos por detras
        cuello0 = W + np.array((0.0, 1.0, 3.5))
        cuello1 = cuello0 + {'A': np.array((0.0, 25.0, 6.0)), 'B': np.array((0.0, 26.0, 3.0)), 'C': np.array((0.0, 24.0, 6.5))}[tipo]
        p_pts, p_rs, _ = jm.a_lo_largo([cuello0, (cuello0 + cuello1) / 2 + np.array((0.0, 0.0, -0.8)), cuello1], 7,
                                       ((0.0, 4.2), (0.35, 3.4), (0.75, 3.6), (1.0, 3.8)))
        jm.tubo(out, p_pts, p_rs, [P['quitina']] * (len(p_pts) - 1), semilla=104)
        for j in range(1, len(p_pts) - 1):
            pua(out, p_pts[j] + np.array((0.0, 0.0, -p_rs[j] * 0.85)), (0.0, 0.5, -1.0), 0.4, 2.2, P['espina'], semilla=105)
        Mp = em.marco(p_pts[-2], p_pts[-1] - p_pts[-2], up=(0.0, 0.0, 1.0))                            # el escudo del pecho
        caja(out, Mp, -4.4, 4.4, -1.0, 2.6, -1.0, 3.2, P['placa'], semilla=106)
        # la cabeza
        Mh = vr.T(*(cuello1 + np.array((0.0, 3.4, 3.2)))) @ vr.Rx(12 * D) @ np.diag([CABEZA] * 3 + [1.0])
        jm.tubo(out, [cuello1 - np.array((0.0, 0.5, 0.5)), pt(Mh, (0.0, 0.6, -2.2))], [2.2, 1.6], [P['quitina']], semilla=108)
        bm.PPB = PPB / CABEZA
        boca, ojos = cabeza(out, Mh, P, tipo)
        bm.PPB = PPB
        antenas(out, P, Mh)
        luces += [boca] + ojos
        if lob:                                                                                        # los petalos de orquidea
            for (x, y, dx, dy, L, A_) in ((0.0, 3.2, 0.0, 1.0, 15.0, 9.0), (3.6, 2.0, 1.0, 0.3, 14.0, 8.5),
                                          (-3.6, 2.0, -1.0, 0.3, 14.0, 8.5), (2.6, -0.6, 0.8, -0.8, 11.0, 7.0),
                                          (-2.6, -0.6, -0.8, -0.8, 11.0, 7.0)):
                base = pt(Mh, (x, y, -2.8))
                petalo(out, P, base, Mh[:3, :3] @ np.array((dx, dy, -0.22)), Mh[:3, :3] @ np.array((0.0, 0.0, 1.0)),
                       L, A_, curva=-3.0, semilla=107)
        # las guadanas
        hombro = p_pts[-3] + np.array((0.0, 0.0, 1.6))
        for s in (1, -1):
            if tipo == 'B':                                       # abiertas y alzadas a los lados
                codo = hombro + np.array((s * 6.5, -2.0, 4.0))
                rod = codo + np.array((s * 9.0, 13.0, 3.0))
                adentro = np.array((-s * 0.7, 0.0, 1.0))
                abre = 40.0
            elif tipo == 'C':                                     # plegadas bajas, delante del pecho
                codo = hombro + np.array((s * 4.0, -6.0, 5.5))
                rod = codo + np.array((s * 1.0, 7.5, 6.0))
                adentro = np.array((-s * 0.4, -0.3, 1.0))
                abre = 165.0
            else:                                                 # alzadas a los lados de la cabeza, como dos hoces
                codo = hombro + np.array((s * 6.0, -3.0, 3.0))
                rod = codo + np.array((s * 6.5, 14.0, -1.0))
                adentro = np.array((-s * 0.25, 0.0, 1.0))
                abre = 145.0
            guadana(out, P, hombro + np.array((s * 2.2, 0.0, 0.0)), codo, rod, adentro, abre, lobulos=lob, semilla=110 + (s > 0))
        # las cuatro patas de andar, con la rodilla por encima del lomo
        for s in (1, -1):
            for zc, (rz, pz) in ((1.5, (5.0, 12.0)), (-3.0, (-7.0, -14.0))):
                cad = W + np.array((s * 3.4, -1.0, zc))
                rod = np.array((s * 9.0, W[1] + 6.0, rz))
                pie = np.array((s * 11.5, 0.0, pz))
                pata(out, P, cad, rod, pie, lobulos=lob, semilla=120)
        # las alas
        raiz = p_pts[-3] + np.array((0.0, 1.0, -3.0))
        if tipo == 'B':                                           # abiertas en abanico detras de la cabeza
            for s in (1, -1):
                ala_abierta(out, P, raiz + np.array((s * 2.0, 0.0, 0.0)), s, [26, 32, 35, 36, 35, 32, 27, 20], semilla=130)
        else:                                                     # plegadas, colgando de los hombros como un manto
            for s in (1, -1):
                manto(out, P, raiz + np.array((s * 1.0, 0.0, 0.0)), s, raiz[1] + 2.0, 12.0 if tipo == 'A' else 13.0,
                      P['membrana'] if tipo == 'A' else P['petalo'], borde=(tipo == 'A'), semilla=130)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    return out, {'boca': luces[0], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

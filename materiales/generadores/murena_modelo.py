"""
Murena y sus formas (14-10-2026). Juan: «crea tus monstruos; si debes usar animales, usalos… pero que no sea igual,
tenemos que poner nuestro toque»; y como pista: «sus morenas [las de Escila], puedes hacer un boss tipo morena».

Murena, la Morena del Arrecife: una morena cinta colosal que sale de su guarida, una roca con coral y percebes, y se
alza en una ese muy alta hacia quien se acerca. Manda la cabeza: alta y larga, con las fauces abiertas que arden por
dentro (el paladar en escalones, los dientes dibujados en hojas, los colmillos del centro del paladar y el nucleo al fondo
de la garganta), los ojos encendidos y las narices abiertas como hojas en la punta del hocico. La aleta del lomo le corre
de la nuca a la cueva, alta y con el canto encendido. Azul noche y limon.

Juan eligio esta (14-10-2026: «me gusta la opcion B») entre la Dragona, la Cinta y la Gigante; luego, entre la Cinta, la
Trenza y la del Velo: «solo deja la opcion 1 y quita la mini serpiente de su boca». La segunda mandibula que salia de la
garganta queda como opcion de la cabeza (segunda=True), apagada.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
import sierpe_modelo as sm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _degradado, lamina
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.6
DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')
ROCA = _r('0c0c0e', '161618', '201f22', '2c2a2e', '3a383c')

VARIANTES = {
    'A': dict(
        clave='A', nombre='la Cinta', corto='cinta', patron='liso',
        piel=_r('04060e', '080c1a', '0e1428', '161e38', '22304e'),
        dibujo=_r('5a5a10', '8a8a1a', 'b8b828', 'dcdc44', 'f6f66e'),
        aleta=_r('1a1a04', '2c2c08', '42420e', '5a5a16', '767620'),
        neon=('fffff0', 'f0ff3a', '5a6a04'),
        forma='ese', aleta_alta=4.6, aleta_baja=0.0, narices='hoja',
        cuerpo=dict(r=2.9, ctrl=[(0.0, 8.0, 3.0), (0.0, 14.0, 11.0), (6.0, 24.0, 8.0), (0.0, 34.0, 2.0), (-5.0, 43.0, 6.0),
                                 (-1.0, 50.0, 12.0), (0.0, 52.0, 16.0)], cabeza=1.3, mira=(0.0, -0.25, 1.0), abre=44.0),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'mur%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def piel(tw, th, cara, s):
        """La piel de morena: lisa, sin escamas, con el dibujo de cada forma (manchas claras redondas, lisa con una veta,
        o el panal: las celdas oscuras con la red clara entre ellas)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        base = _imagen(_bisel(np.full((th, tw), 2), 1, 1), V['piel'])
        if V['patron'] == 'manchas':
            idx = sm._manchas(tw, th, s, celda=9.0, umbral=0.72, alto=0.86)
            m = idx >= 3
            dib = _imagen(np.where(idx >= 4, 3, 2), V['dibujo'])
        elif V['patron'] == 'panal':
            idx = sm._manchas(tw, th, s, celda=5.0, umbral=0.42, alto=0.95)
            m = idx < 3                                                                 # la red clara entre las manchas
            dib = _imagen(np.full((th, tw), 2), V['dibujo'])
        else:
            m = np.zeros((th, tw), bool)
            if th >= 6:
                m[th // 2, :] = True
            dib = _imagen(np.full((th, tw), 2), V['dibujo'])
        t = np.where(m[..., None], dib, base).astype(np.uint8)
        return t, None
    reg('piel', piel)

    def aleta(tw, th, cara, s):
        """La aleta del lomo: en bandas, con los radios claros."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 2) % 2 == 0, 2, 1)
        idx = np.where((xs % 6) == 0, 4, idx)
        return _imagen(idx, V['aleta']), None
    reg('aleta', aleta)
    reg('hueso', jm.liso(V['dibujo'], 3, 1, 1))
    reg('oscuro', jm.liso(_r('040404', '080808', '0e0e10', '161618', '202024'), 2, 1, 1))

    def roca(tw, th, cara, s):
        idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
        idx = np.array([1, 2, 2, 3, 3])[idx]
        return _imagen(_bisel(idx), ROCA), None
    reg('roca', roca)
    reg('percebe', jm.liso(_r('5a5650', '7e7a72', 'a29e94', 'c2beb4', 'e0dcd2'), 3, 1, 1))
    reg('coral', jm.liso(_r('3a0a0e', '5e1418', '8a2226', 'b43a36', 'dc6a58'), 3, 1, 1))

    def ojo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = nm._hex(neo)
        t[..., 3] = 255
        if tw >= 3:
            t[:, tw // 2, :3] = (10, 8, 6)
        return t, _emis(t, np.ones((th, tw), bool), 230)
    reg('ojo', ojo)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

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
                                np.where((dd < 0.76)[..., None], np.array(c_m), np.array(qm._mezcla(c_m, c_n, 0.6)))))
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
        col = np.where((r < 0.45)[..., None], np.array(c_n),
                       np.where((r < 0.8)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m)))
        col = np.where((r > 1.0)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 1.0, 240)
    reg('nucleo', nucleo)

    def _hojas_de_dientes(tw, th, colgando, paso=5):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTES]
        n = max(1, (tw + 1) // paso)
        x0 = (tw - (n * paso - 1)) // 2
        for i in range(n):
            x = x0 + i * paso
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.7)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)
                if paso < 5:
                    pix = ((x + 1, c[4]),) if f > 0.5 else ((x, c[3]), (x + 1, c[4]))
                elif f > 0.85:
                    pix = ((x + 1, c[4]),)
                elif f > 0.6:
                    pix = ((x + 1, c[4]), (x + 2, c[3]))
                else:
                    pix = ((x, c[2]), (x + 1, c[4]), (x + 2, c[3]), (x + 3, c[1]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
        return t, None
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, False))
    reg('agujas_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, True, 3))
    reg('agujas_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, False, 3))

    def colmillo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [np.array((*cc, 255)) for cc in DIENTES]
        for y in range(th):
            f = y / max(th - 1, 1)
            w = (1.0 - f) ** 0.8 * tw / 2
            cx = (tw - 1) / 2
            for x in range(tw):
                d = x - cx
                if abs(d) <= w:
                    t[y, x] = c[4] if d < -w * 0.2 else (c[3] if d < w * 0.4 else c[1])
        return t, None
    reg('colmillo', colmillo)

    def hoja(tw, th, cara, s):
        """Las narices en hoja de la Cinta: del color del dibujo, con el nervio y el borde."""
        ys, xs = np.mgrid[0:th, 0:tw]
        u = np.abs((xs + 0.5) / tw - 0.5) * 2
        idx = np.where(u < 0.15, 4, np.where(u < 0.8, 3, 1))
        t = _imagen(idx, V['dibujo'])
        return t, _emis(t, u < 0.15, 160)
    reg('hoja', hoja)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def _u(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado, h = float(np.linalg.norm(B - A)), float(np.linalg.norm(A2 - A))
        if alto < 0:
            lamina(out, (A2, B2, B, A), pintor, lado, h, semilla + j)
            lamina(out, (B2, A2, A, B), pintor, lado, h, semilla + j)
        else:
            lamina(out, (A, B, B2, A2), pintor, lado, h, semilla + j)
            lamina(out, (B, A, A2, B2), pintor, lado, h, semilla + j)


def colmillo(out, M, base, largo, ancho, abajo, P, semilla=0):
    b = pt(M, base)
    d = _u(M[:3, :3] @ np.asarray(abajo, float))
    for lado in (M[:3, 0], M[:3, 2]):
        l = _u(lado - d * (lado @ d))
        p0, p1 = b - l * ancho / 2, b + l * ancho / 2
        q0, q1 = p0 + d * largo, p1 + d * largo
        lamina(out, (q0, q1, p1, p0), P['colmillo'], ancho, largo, semilla)
        lamina(out, (q1, q0, p0, p1), P['colmillo'], ancho, largo, semilla)


def tubo_nariz(out, P, M, base, d, largo, r, semilla=0):
    """Una nariz en tubo (un cuerno corto que se afina y se dobla), con la punta oscura."""
    p0 = pt(M, base)
    d = _u(M[:3, :3] @ np.asarray(d, float))
    p1 = p0 + d * largo * 0.6
    p2 = p1 + _u(d + M[:3, :3] @ np.array((0.0, 0.0, 0.5))) * largo * 0.4
    jm.tubo(out, [p0, p1, p2], [r, r * 0.8, r * 0.65], [P['piel'], P['hueso']], semilla=semilla)
    caja(out, vr.T(*p2), -r * 0.7, r * 0.7, -r * 0.7, r * 0.7, -r * 0.7, r * 0.7, P['oscuro'], semilla=semilla + 1)


def nariz_hoja(out, P, M, base, d, n, largo, ancho, semilla=0):
    """Una nariz abierta como una hoja (la Cinta): una lamina en abanico con el nervio que brilla un poco."""
    b = pt(M, base)
    d = _u(M[:3, :3] @ np.asarray(d, float))
    n = _u(M[:3, :3] @ np.asarray(n, float))
    x = _u(np.cross(n, d))
    filas = []
    for t, w in ((0.0, 0.2), (0.35, 1.0), (0.75, 0.85), (1.0, 0.15)):
        c = b + d * largo * t
        filas.append((c - x * w * ancho / 2, c + x * w * ancho / 2))
    for (a0, b0), (a1, b1) in zip(filas, filas[1:]):
        L = float(np.linalg.norm((a1 + b1) / 2 - (a0 + b0) / 2))
        W_ = max(float(np.linalg.norm(b0 - a0)), float(np.linalg.norm(b1 - a1)), 0.3)
        lamina(out, (a0, b0, b1, a1), P['hoja'], W_, L, semilla=semilla)
        lamina(out, (a1, b1, b0, a0), P['hoja'], W_, L, semilla=semilla)


def mandibula_de_dentro(out, P, M, sale, abre=26.0, semilla=0):
    """La segunda mandibula de la garganta: dos piezas pequenas, la de arriba y la de abajo, con sus dientes en hojas y el
    paladar encendido, que salen hacia delante (sale: cuanto asoman); detras, en el fondo, el nucleo."""
    Mi = M @ vr.T(0.0, -0.9, -3.0 + sale)
    bm.cubo(out, Mi, -1.3, 0.0, 0.0, 2.6, 1.0, 3.6, P['piel'], caras={'abajo': P['fauces']}, semilla=semilla)
    hilera(out, Mi, [(-1.15, 0.4), (-1.15, 3.4), (1.15, 3.4), (1.15, 0.4)], 0.0, -0.8, P['agujas_arriba'], semilla=semilla + 1)
    Mj = Mi @ vr.T(0.0, 0.0, 0.2) @ vr.Rx(abre * D)
    bm.cubo(out, Mj, -1.2, -0.9, 0.0, 2.4, 0.9, 3.4, P['piel'], caras={'arriba': P['boca']}, semilla=semilla + 2)
    hilera(out, Mj, [(-1.05, 0.4), (-1.05, 3.2), (1.05, 3.2), (1.05, 0.4)], 0.0, 0.7, P['agujas_abajo'], semilla=semilla + 3)
    jm.tubo(out, [pt(M, (0.0, -0.6, -4.5)), pt(Mi, (0.0, -0.2, 0.2))], [1.0, 0.9], [P['fauces']], semilla=semilla + 4)   # el cuello de dentro
    caja(out, M, -1.6, 1.6, -2.4, 0.4, -4.4, -4.1, P['nucleo'], semilla=semilla + 5)
    return pt(Mi, (0.0, -0.4, 2.0))


def cabeza(out, Mh, P, forma, abre, semilla=0):
    """La cabeza de morena, con el hocico hacia +z: alta y larga, con la nuca en joroba, los ojos pequenos y encendidos
    arriba, cerca del hocico; el agujero de la agalla; las fauces abiertas: el paladar encendido, los dientes en hojas por
    los bordes, los colmillos del centro del paladar y, en la Dragona, las mandibulas curvas que no cierran; las narices
    de cada forma; y la segunda mandibula que sale de la garganta. Devuelve la boca."""
    p = P['piel']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -2.7, 0.0, -5.0, 5.4, 6.0, 6.0, p, caras=F, semilla=semilla)                    # la nuca alta
    bm.cubo(out, Mh, -2.4, 0.0, 1.0, 4.8, 4.6, 4.0, p, caras=F, semilla=semilla + 1)
    bm.cubo(out, Mh, -2.0, 0.2, 5.0, 4.0, 3.4, 3.4, p, caras=F, semilla=semilla + 2)                 # el hocico
    bm.cubo(out, Mh, -1.5, 0.4, 8.4, 3.0, 2.4, 2.0, p, caras=F, semilla=semilla + 3)
    if forma.get('gancho'):                                                                            # el gancho de arriba
        Mg = Mh @ vr.T(0.0, 0.6, 10.2) @ vr.Rx(30 * D)
        bm.cubo(out, Mg, -1.2, 0.0, 0.0, 2.4, 1.8, 2.2, p, caras=F, semilla=semilla + 4)
    for s in (1, -1):
        x0 = 1.95 if s > 0 else -2.25
        bm.cubo(out, Mh, x0, 3.4, 5.4, 0.3, 1.1, 1.4, P['ojo'], semilla=semilla + 5)                  # los ojos
        bm.cubo(out, Mh, x0 - 0.15 * s, 4.3, 5.0, 0.6, 0.6, 2.2, p, semilla=semilla + 6)
        x1 = 2.6 if s > 0 else -2.9
        bm.cubo(out, Mh, x1, 1.0, -3.6, 0.3, 1.6, 1.0, P['oscuro'], semilla=semilla + 7)              # la agalla
    pts = [(-2.3, -4.0), (-2.2, 4.6), (-1.8, 8.0), (-1.3, 10.2), (1.3, 10.2), (1.8, 8.0), (2.2, 4.6), (2.3, -4.0)]
    hilera(out, Mh, pts, 0.0, -1.3, P['dientes_arriba'], semilla=semilla + 8)
    for z in (6.5, 8.8):                                                                               # los colmillos del paladar
        colmillo(out, Mh, (0.0, 0.2, z), 2.6, 0.9, (0, -1, 0.1), P, semilla=semilla + 9)
    Mj = Mh @ vr.T(0.0, 0.2, -4.6) @ vr.Rx(abre * D)                                                   # la mandibula de abajo
    J = {'arriba': P['boca']}
    bm.cubo(out, Mj, -2.4, -2.2, 0.0, 4.8, 2.2, 8.0, p, caras=J, semilla=semilla + 10)
    bm.cubo(out, Mj, -1.9, -2.0, 8.0, 3.8, 2.0, 3.4, p, caras=J, semilla=semilla + 11)
    if forma.get('gancho'):                                                                            # curva, no cierra
        Mj2 = Mj @ vr.T(0.0, 0.0, 11.2) @ vr.Rx(-34 * D)
        bm.cubo(out, Mj2, -1.5, -1.8, 0.0, 3.0, 1.8, 3.4, p, caras=J, semilla=semilla + 12)
        hilera(out, Mj2, [(-1.3, 0.3), (-1.3, 3.0), (1.3, 3.0), (1.3, 0.3)], 0.0, 1.2, P['dientes_abajo'], semilla=semilla + 13)
        colmillo(out, Mj2, (0.0, 0.0, 2.6), 2.4, 0.9, (0, 1, 0.2), P, semilla=semilla + 14)
    hilera(out, Mj, [(-2.15, 0.6), (-2.15, 7.8), (-1.7, 11.0), (1.7, 11.0), (2.15, 7.8), (2.15, 0.6)], 0.0, 1.2, P['dientes_abajo'],
           semilla=semilla + 15)
    for x in (-1.3, 1.3):
        colmillo(out, Mj, (x, 0.0, 10.4), 2.2, 0.8, (0, 1, 0.1), P, semilla=semilla + 16)
    if forma.get('quijadas'):                                                                          # las quijadas gruesas
        for s in (1, -1):
            x0 = 2.2 if s > 0 else -3.6
            bm.cubo(out, Mj, x0, -2.6, 0.5, 1.4, 2.6, 6.0, p, semilla=semilla + 17)
    # las narices de cada forma
    narices = forma.get('narices', 'corta')
    if narices == 'tubo':
        for s in (1, -1):
            tubo_nariz(out, P, Mh, (s * 0.9, 2.6, 9.8), (s * 0.3, 1.0, 0.7), 2.8, 0.42, semilla=semilla + 18)
            tubo_nariz(out, P, Mh, (s * 1.3, 4.6, 4.6), (s * 0.35, 1.0, -0.2), 3.6, 0.5, semilla=semilla + 19)
    elif narices in ('hoja', 'corona'):
        for s in (1, -1):
            nariz_hoja(out, P, Mh, (s * 0.9, 2.6, 9.6), (s * 0.6, 0.9, 0.7), (s * 1.0, 0.0, -0.4), 3.4, 2.6, semilla=semilla + 18)
            if narices == 'corona':                                                                    # y dos mas, grandes, sobre los ojos
                nariz_hoja(out, P, Mh, (s * 1.4, 4.8, 5.4), (s * 0.55, 1.0, -0.35), (s * 1.0, 0.0, 0.3), 5.0, 3.6,
                           semilla=semilla + 19)
    else:
        for s in (1, -1):
            tubo_nariz(out, P, Mh, (s * 0.9, 2.6, 9.6), (s * 0.2, 1.0, 0.5), 1.2, 0.35, semilla=semilla + 18)
    # la segunda mandibula, que sale de la garganta
    Mg = Mh @ vr.Rx(abre * 0.45 * D)
    if forma.get('segunda'):
        return mandibula_de_dentro(out, P, Mg, sale=forma.get('sale', 5.5), semilla=semilla + 30)
    caja(out, Mg, -1.8, 1.8, -2.6, 0.2, -4.4, -4.1, P['nucleo'], semilla=semilla + 30)                  # el nucleo, al fondo
    return pt(Mg, (0.0, -1.0, 2.0))


def guarida(out, P, semilla=0):
    """La guarida: una roca grande con la boca de la cueva por delante (de donde sale), con coral y percebes."""
    rng = random.Random(semilla)
    for i in range(16):
        a = rng.uniform(-2.2, 2.2) + math.pi
        r = rng.uniform(4.0, 11.0)
        y = rng.uniform(0.0, 10.0)
        w = rng.uniform(4.0, 7.5)
        M = vr.T(math.sin(a) * r, y, math.cos(a) * r - 4.0) @ vr.Ry(rng.uniform(0, 3)) @ vr.Rz(rng.uniform(-0.3, 0.3))
        caja(out, M, -w, w, -2.0, w * 0.8, -w * 0.8, w * 0.8, P['roca'], semilla=semilla + i % 5)
    for s in (1, -1):                                                                                  # los lados de la boca
        M = vr.T(s * 7.0, 0.0, 2.0) @ vr.Ry(s * 0.3)
        caja(out, M, -3.2, 3.2, 0.0, 13.0, -3.0, 3.0, P['roca'], semilla=semilla + 6)
    caja(out, jm.I4, -9.0, 9.0, 12.0, 17.0, -4.0, 3.5, P['roca'], semilla=semilla + 7)                 # el dintel
    caja(out, jm.I4, -4.2, 4.2, 0.5, 12.0, -1.0, 1.0, P['oscuro'], semilla=semilla + 8)                # el hueco
    for k in range(9):                                                                                 # los percebes
        a = rng.uniform(0, TAU)
        p = np.array((rng.uniform(-9, 9), rng.uniform(2, 16), rng.uniform(-1, 4.5)))
        caja(out, vr.T(*p), -0.7, 0.7, -0.6, 0.9, -0.7, 0.7, P['percebe'], semilla=semilla + 9)
    for k in range(5):                                                                                 # el coral
        b = np.array((rng.uniform(-10, 10), 15.0 + rng.uniform(0, 2.5), rng.uniform(-3, 3)))
        for j in range(3):
            d = _u(np.array((rng.uniform(-0.5, 0.5), 1.0, rng.uniform(-0.5, 0.5))))
            jm.tubo(out, [b, b + d * 2.5, b + d * 4.2 + np.array((rng.uniform(-1, 1), 0.0, 0.0))], [0.45, 0.32, 0.18],
                    [P['coral']] * 2, semilla=semilla + 10)


def cuerpo(out, P, C, aleta_alta, aleta_baja=0.0, semilla=0):
    """El cuerpo de morena por la curva: alto y aplastado de lado, con la aleta del lomo de la nuca a la cueva (canto
    encendido). Devuelve los puntos y los radios."""
    ctrl = [np.array(c, float) for c in C['ctrl']]
    r = C['r']
    ps, rs, _ = jm.a_lo_largo(ctrl, max(14, len(ctrl) * 4), ((0.0, r * 0.95), (0.5, r * 1.05), (1.0, r * 0.95)))
    jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=semilla, achata=1.25)
    base, tops = [], []
    for k in range(1, len(ps) - 1):
        d = ps[k + 1] - ps[k - 1]
        arriba = _u(np.cross(d, (1.0, 0.0, 0.0)))                                    # el lomo, del lado de fuera de la curva
        h = (aleta_alta if k < len(ps) - 3 else aleta_alta * 0.5)
        base.append(ps[k] + arriba * rs[k] * 1.1)
        tops.append(ps[k] + arriba * (rs[k] * 1.1 + h))
    for k in range(len(base) - 1):
        a0, a1, b0, b1 = base[k], base[k + 1], tops[k], tops[k + 1]
        L = max(float(np.linalg.norm(a1 - a0)), 0.4)
        H = max(float(np.linalg.norm(b0 - a0)), 0.4)
        lamina(out, (a0, a1, b1, b0), P['aleta'], L, H, semilla=semilla + 1)
        lamina(out, (a1, a0, b0, b1), P['aleta'], L, H, semilla=semilla + 1)
    jm.tubo(out, tops, [0.32] * len(tops), [P['luz']] * (len(tops) - 1), semilla=semilla + 2)
    if aleta_baja > 0:                                                               # la aleta de abajo, de velo
        base2, tops2 = [], []
        for k in range(2, len(ps) - 3):
            d = ps[k + 1] - ps[k - 1]
            abajo = -_u(np.cross(d, (1.0, 0.0, 0.0)))
            h = aleta_baja * math.sin(math.pi * (k - 2) / max(len(ps) - 6, 1)) + 0.4
            base2.append(ps[k] + abajo * rs[k] * 1.05)
            tops2.append(ps[k] + abajo * (rs[k] * 1.05 + h))
        for k in range(len(base2) - 1):
            a0, a1, b0, b1 = base2[k], base2[k + 1], tops2[k], tops2[k + 1]
            L = max(float(np.linalg.norm(a1 - a0)), 0.4)
            H = max(float(np.linalg.norm(b0 - a0)), 0.4)
            lamina(out, (a0, a1, b1, b0), P['aleta'], L, H, semilla=semilla + 3)
            lamina(out, (a1, a0, b0, b1), P['aleta'], L, H, semilla=semilla + 3)
        jm.tubo(out, tops2, [0.3] * len(tops2), [P['luz']] * (len(tops2) - 1), semilla=semilla + 4)
    return ps, rs


# ======================================================================
#  MURENA
# ======================================================================
def _cabeza_al_final(out, P, ps, mira, C, V, semilla=0):
    mira = _u(np.asarray(mira, float))
    esc = C['cabeza']
    Mh = em.marco(ps[-1], mira, up=(0.0, 1.0, 0.0)) @ vr.T(0.0, -2.8 * esc, -1.5 * esc) @ np.diag([esc] * 3 + [1.0])
    bm.PPB = PPB / esc
    boca = cabeza(out, Mh, P, dict(narices=V['narices'], segunda=False), C['abre'], semilla=semilla)
    bm.PPB = PPB
    return boca, pt(Mh, (0.0, -0.5, 4.0))


def murena(tipo='A'):
    V = VARIANTES[tipo]
    C = V['cuerpo']
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        guarida(out, P, semilla=200)
        ps, rs = cuerpo(out, P, C, V['aleta_alta'], aleta_baja=V['aleta_baja'], semilla=100)
        luces = list(_cabeza_al_final(out, P, ps, C['mira'], C, V, semilla=120))
    finally:
        bm.PPB = ppb
    E = np.diag([ESCALA] * 3 + [1.0])
    out = qm.transformar(out, E)
    luces = [pt(E, p) for p in luces]
    return out, {'boca': luces[0], 'luces': luces}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)
